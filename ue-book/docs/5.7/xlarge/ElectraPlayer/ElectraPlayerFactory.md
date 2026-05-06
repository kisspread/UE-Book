# Electra Player

> Cross platform media player for local files and internet streaming.  
> Also provides optimized local mp4 file only player (Protron) for desktop machines.

| 属性 | 值 |
|---|---|
| 中文名 | 电子播放器 |
| 分类 | Media Players |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ElectraPlayerFactory` (Runtime), `ElectraPlayerPlugin` (Runtime), `ElectraPlayerPluginHandler` (Runtime), `ElectraPlayerRuntime` (Runtime), `ElectraProtron` (Runtime), `ElectraProtronFactory` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-09-11 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/ElectraPlayer) | |

---

## 用途

Electra Player 是虚幻引擎内置的高性能跨平台媒体播放器，支持本地文件播放和流媒体（如 HLS、DASH、RTMP 等）在线播放。它同时提供 **Protron** 优化播放器，专为桌面平台的本地 MP4 文件播放做了极致优化，减少资源占用并提升播放稳定性。

该插件作为 Media Framework 的核心实现之一，自动被引擎媒体资产（`UMediaPlayer`）使用，无需手动管理播放器实例。

## 使用场景

- **游戏内过场动画**：播放压缩后的 MP4 或流视频资源，替代实时渲染节省性能。
- **直播与流媒体**：集成 HLS/DASH 直播流，用于游戏内赛事直播、消息推送。
- **自定义媒体播放器**：在 C++ 中直接控制播放逻辑，实现特殊播放策略（如循环播放、自适应码率）。
- **高性能桌面播放**：使用 Protron 模式播放本地 MP4 文件，获得更低延迟和更平滑的体验。

## 蓝图用法

Electra 播放器已深度集成到蓝图 **Media Framework** 中，无需额外蓝图节点即可使用。推荐以下工作流：

1. 在内容浏览器创建 **Media Player** 资产和 **Media Source** 资产。
2. 将 Media Source 的 URL 设置为文件路径或流媒体地址。
3. 在关卡蓝图或控件蓝图中，使用 `MediaPlayer.Open Source` 节点打开媒体源，然后连接 `Play`、`Pause` 等控制节点。
4. 使用 `File Media Source` 或 `Stream Media Source` 资产指定具体内容。

Electra 作为默认播放器，会自动处理所有兼容的媒体格式。

### 核心节点（通用 Media Framework）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Open Source` | 打开 Media Source 资产 | `UMediaPlayer` |
| `Play` | 开始播放 | `UMediaPlayer` |
| `Pause` | 暂停播放 | `UMediaPlayer` |
| `Seek` | 跳转到指定时间 | `UMediaPlayer` |
| `OnMediaOpened` | 媒体打开成功事件 | `UMediaPlayer` |
| `OnMediaFailed` | 媒体打开失败事件 | `UMediaPlayer` |

## C++ 用法

### 头文件引入

```cpp
#include "MediaPlayer.h"
#include "MediaSource.h"
#include "FileMediaSource.h"
// 如果直接使用工厂创建播放器
#include "ElectraPlayerFactory.h"
#include "IMediaPlayerFactory.h"
```

### 基本用法

通过 Media Framework 创建并播放本地文件（推荐方式，由引擎自动选择 Electra 实现）：

```cpp
// 创建媒体播放器 UObject
UMediaPlayer* MediaPlayer = NewObject<UMediaPlayer>();
UFileMediaSource* MediaSource = NewObject<UFileMediaSource>();
MediaSource->FilePath = TEXT("/Game/Movies/Intro.mp4");

// 打开媒体源
MediaPlayer->OpenSource(MediaSource);
MediaPlayer->Play();
```

**来源**: 通用 Media Framework 用法（对应引擎 `Engine/Source/Runtime/MediaAssets/Private/MediaPlayer.cpp`）

### 进阶用法

直接通过 Electra 工厂创建底层播放器，以传递自定义选项：

```cpp
// 加载 ElectraPlayerFactory 模块
IElectraPlayerFactory* Factory = FModuleManager::LoadModuleChecked<IElectraPlayerFactory>("ElectraPlayerFactory");

// 创建播放器实例
TSharedPtr<IMediaPlayer> Player = Factory->CreatePlayer();

// 设置选项（例如设置自定义 HTTP 头）
FMediaPlayerOptions Options;
Options.BufferSize = 5 * 1024 * 1024; // 5MB 缓冲
Options.BandwidthLimit = 5000000; // 5 Mbps

// 打开 URL
Player->Open(TEXT("https://example.com/stream.m3u8"), Options);
```

**来源**: 基于 `ElectraPlayerFactory.h`（`IMediaPlayerFactory` 子类）和 `ElectraPlayerRuntime` 内部实现推断，具体接口请参考插件头文件。

## Demo 示例

以下展示一个最小可编译的控制台命令，用于播放本地 MP4 文件：

### AElectraPlayerDemo.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MediaPlayer.h"
#include "ElectraPlayerDemo.generated.h"

UCLASS()
class AElectraPlayerDemo : public AActor
{
	GENERATED_BODY()

public:
	virtual void BeginPlay() override;

	UPROPERTY(EditAnywhere)
	FString FilePath = TEXT("/Game/Movies/Demo.mp4");

	UPROPERTY()
	TObjectPtr<UMediaPlayer> MediaPlayer;
};
```

### AElectraPlayerDemo.cpp

```cpp
#include "ElectraPlayerDemo.h"
#include "FileMediaSource.h"

void AElectraPlayerDemo::BeginPlay()
{
	Super::BeginPlay();

	if (FilePath.IsEmpty()) return;

	MediaPlayer = NewObject<UMediaPlayer>(this);
	UFileMediaSource* MediaSource = NewObject<UFileMediaSource>();
	MediaSource->FilePath = FilePath;
	MediaPlayer->OpenSource(MediaSource);
	MediaPlayer->Play();
}
```

**注意**：此示例依赖 `MediaAssets` 模块（`UMediaPlayer` 位于其中），实际使用时需在项目 Build.cs 中添加 `"MediaAssets"` 依赖。

## 模块依赖

使用 Electra Player 最常用的方式是通过 Media Framework（`MediaAssets` 模块），无需直接依赖插件的内部模块。若需直接在 C++ 中使用底层 API，则需添加以下依赖：

| 模块 | 用途 |
|---|---|
| `ElectraPlayerFactory` | 创建和管理媒体播放器实例 |
| `ElectraBase` | 基础数据结构和工具函数 |
| `MediaAssets` | 蓝图可用的媒体资产和播放器类（推荐） |

**内部依赖说明**（使用者通常不需要直接引用）：
- `ElectraPlayerRuntime` 提供核心播放引擎，依赖 `Engine`、`DirectX`。
- `ElectraProtron` 提供桌面 MP4 优化，依赖 `D3D12RHI`，仅在 Windows 平台起作用。

## 维护状态

插件由 Epic Games 维护，基于 5.7 分支的近期日志显示活跃开发。

### 近期更新

- 2025-10-01 `31d4710d` 改进对回放事件的支持；增加将 HLS VoD 流转为重复播放的能力
- 2025-09-29 `d34a730c` 仅在缩短时长检查被跳过时发出媒体分段时长不匹配警告
- 2025-09-29 `49fa2b76` 当媒体分段时长较大时调整最大 Live 边缘延迟
- 2025-09-23 `0dc995dc` 使用 VoD 资源进行同步事件时，允许通过 DASH 媒体表现描述循环播放
- 2025-09-11 `d9f531d6` 合并多行原始字符串为单行

### 维护评价

- **创建时间**：2025-09-11（全新插件）
- **活跃度**：极活跃，几乎每周都有功能性更新和优化。
- **质量**：源自 Epic 内部成熟的媒体栈，在 5.7 版本作为全新模块重写，API 现代且无已知严重问题。
- **推荐**：✅ **强烈推荐**。作为 UE 默认媒体播放器，性能优异且持续迭代，适合所有需要视频播放的项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/ElectraPlayer)
- [官方文档](https://docs.unrealengine.com/en-US/Engine/MediaFramework/Overview)
- [Media Framework 教程](https://docs.unrealengine.com/en-US/WorkingWithMedia/BasicMediaPlayback)