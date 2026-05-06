# Electra Player

> Cross platform media player for local files and internet streaming.  
> Also provides optimized local mp4 file only player (Protron) for desktop machines.

| 属性 | 值 |
|---|---|
| 中文名 | 电磁播放器 |
| 分类 | Media Players |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ElectraPlayerFactory` (Runtime), `ElectraPlayerPlugin` (Runtime), `ElectraPlayerPluginHandler` (Runtime), `ElectraPlayerRuntime` (Runtime), `ElectraProtron` (Runtime), `ElectraProtronFactory` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-09-11 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/ElectraPlayer) | |

## 用途

Electra Player 是 Epic Games 开发的跨平台媒体播放器插件，支持：

- **本地文件播放**：MP4、TS 等常见容器格式。
- **互联网流媒体**：HLS、DASH、SmoothStreaming 等自适应码率协议。
- **Protron 模式**：在桌面端提供针对本地 MP4 文件的极致性能优化播放器，适合高质量视频回放。

该插件解决了传统媒体播放插件在平台兼容性、流媒体协议支持及性能方面的不足，是虚幻引擎 5 中官方推荐的媒体播放方案之一。

## 使用场景

- **游戏内过场动画**：使用 HLS 或 DASH 播放高质量视频，支持自适应码率以适应不同网络条件。
- **直播或流媒体集成**：在 UI 中嵌入直播画面。
- **本地 MP4 播放**：利用 Protron 模式实现高帧率、低延迟的本地视频播放。
- **同步事件播放**：支持根据时间轴触发媒体事件（如 Replay 事件、循环播放 VoD 资产）。

## 蓝图用法

> **说明**：Electra Player 的核心蓝图能力通过 `Media Player` 资产和 `Media Texture` 资源暴露。具体节点位于 `MediaPlayer` 蓝图库，插件本身不直接提供新的蓝图函数，而是复用虚幻引擎的媒体框架。以下为常用操作。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Open Source` | 从 Media Source 资产打开媒体流 | `UMediaPlayer` |
| `Play` | 开始播放 | `UMediaPlayer` |
| `Pause` | 暂停播放 | `UMediaPlayer` |
| `Close` | 关闭当前媒体 | `UMediaPlayer` |
| `Is Playing` | 检查是否正在播放 | `UMediaPlayer` |
| `Get Time` | 获取当前播放位置 | `UMediaPlayer` |
| `Set Time` | 跳转到指定时间 | `UMediaPlayer` |
| `On Media Opened` | 媒体打开完成时触发 | `UMediaPlayer` |
| `On Media Closed` | 媒体关闭时触发 | `UMediaPlayer` |
| `On End Reached` | 播放结束时触发 | `UMediaPlayer` |

### 使用示例（蓝图描述）

1. **播放本地 MP4 文件**  
   - 创建 `Media Player` 资产（如 `MP4Player`）。  
   - 创建 `Media Source` 资产并指向本地 MP4 文件路径（使用绝对路径或打包内路径）。  
   - 在关卡蓝图中调用 `Open Source` 节点，设置 `Media Source` 为创建的资产，`Media Player` 为 `MP4Player`。  
   - 成功后连接 `Play` 节点开始播放。  
   - 使用 `Create Media Texture` 节点将媒体纹理呈现到 UI 或 3D 资产上。

2. **流媒体直播（HLS/DASH）**  
   - 创建一个 `URL Media Source` 资产，填入流媒体 URL（如 `https://example.com/live.m3u8`）。  
   - 使用 `Open Source` 节点打开该 URL 媒体源。  
   - 同样使用 `Play` 开始播放，`On Media Opened` 事件可用于更新 UI。

3. **事件驱动循环播放**  
   - 利用 `On End Reached` 事件重新调用 `Open Source` 并设置 `Looping` 为 true 实现循环。  
   - 或在 `On Media Opened` 中根据需求设置回放选项（如 `Set Loop`）。

## C++ 用法

Electra Player 的 C++ 接口主要位于 `ElectraPlayerRuntime` 和 `ElectraPlayerPlugin` 模块。

### 头文件引入

```cpp
#include "MediaPlayer.h"
#include "MediaTexture.h"
#include "IMediaPlayer.h"          // 用于底层媒体播放器接口
#include "ElectraPlayerRuntime.h" // 可选，用于直接控制 Electra 播放器
```

### 基本用法

```cpp
// 获取 MediaPlayer 对象（从 UObject 或资产）
UMediaPlayer* MediaPlayer = NewObject<UMediaPlayer>();
MediaPlayer->AddToRoot(); // 确保不被 GC

// 打开本地文件（需要 UFileMediaSource）
UFileMediaSource* FileSource = NewObject<UFileMediaSource>();
FileSource->SetFilePath(TEXT("C:/Videos/movie.mp4"));

// 打开流媒体（使用 UMediaSource 或自定义 URL）
UMediaSource* StreamSource = UMediaSource::CreateFromURL(TEXT("https://example.com/stream.m3u8"));

// 打开媒体
MediaPlayer->OpenSource(FileSource);

// 播放
MediaPlayer->Play();

// 获取播放状态
bool bPlaying = MediaPlayer->IsPlaying();
FTimespan CurrentTime = MediaPlayer->GetTime();

// 关闭媒体
MediaPlayer->Close();
```

### 进阶用法

结合 Protron 模式与自定义事件：

```cpp
// 开启 Protron 模式（桌面端专用）
// 需要通过 ElectraProtron 模块的 API 设置，例如：
#include "ElectraProtron/Public/ElectraProtronPlayerManager.h"

// 假设存在一个全局 Manager 用于管理 Protron 实例
FElectraProtronPlayerManager::Get().Initialize();

// 创建 Protron 播放器
ProtronHandle Handle = FElectraProtronPlayerManager::Get().CreatePlayer();
Handle->PlayLocalFile(TEXT("C:/Videos/high_quality.mp4"));

// 设置同步事件（来自 HLS VoD 的 Replay 支持）
// 在 ElectraPlayerPlugin 的事件系统中处理
MyMediaPlayer.OnMediaOpened.BindLambda([](FString MediaUrl) {
    UE_LOG(LogTemp, Log, TEXT("Media opened: %s"), *MediaUrl);
});
MyMediaPlayer.OnEndReached.BindLambda([]() {
    // 重新打开实现循环
    MyMediaPlayer.OpenSource(MyMediaSource);
});
```

## Demo 示例

以下是一个最小 C++ 类，演示如何使用 Electra Player 在 UI 上播放视频。

**ElectraPlayerDemo.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MediaPlayer.h"
#include "MediaTexture.h"
#include "MediaSource.h"
#include "ElectraPlayerDemo.generated.h"

UCLASS()
class AElectraPlayerDemo : public AActor
{
    GENERATED_BODY()

public:
    AElectraPlayerDemo();

    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    UPROPERTY()
    UMediaPlayer* MediaPlayer;

    UPROPERTY()
    UMediaTexture* MediaTexture;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Media", meta = (AllowPrivateAccess = "true"))
    UMediaSource* MediaSource;
};
```

**ElectraPlayerDemo.cpp**

```cpp
#include "ElectraPlayerDemo.h"

AElectraPlayerDemo::AElectraPlayerDemo()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AElectraPlayerDemo::BeginPlay()
{
    Super::BeginPlay();

    if (!MediaSource)
    {
        UE_LOG(LogTemp, Error, TEXT("MediaSource not set!"));
        return;
    }

    MediaPlayer = NewObject<UMediaPlayer>(this, UMediaPlayer::StaticClass());
    MediaPlayer->SetLooping(false);
    MediaPlayer->SetBlockOnTime(true);

    MediaTexture = NewObject<UMediaTexture>(this, UMediaTexture::StaticClass());
    MediaTexture->SetMediaPlayer(MediaPlayer);

    if (MediaPlayer->OpenSource(MediaSource))
    {
        MediaPlayer->Play();
    }
}

void AElectraPlayerDemo::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (MediaPlayer)
    {
        MediaPlayer->Close();
    }
    Super::EndPlay(EndPlayReason);
}
```

> **注意**：实际使用时，需要将 `MediaTexture` 应用到材质实例，并显示在 UI 或 3D 表面。

## 模块依赖

从各构建模块提取的独特依赖：

| 模块 | 用途 |
|---|---|
| `DirectX` | 底层 D3D 资源管理，用于解码后的视频帧渲染（ElectraPlayerRuntime） |
| `D3D12RHI` | 桌面端 Protron 模式下的硬件加速渲染（ElectraProtron） |
| `MediaAssets` | 媒体资产框架（MediaPlayer、MediaTexture 等），已包含在 Engine 依赖中 |

> 其他依赖如 `Engine`、`Core` 为常见依赖，省略列出。

## 维护状态

### 近期更新

```
- 2025-10-01 31d4710d ElectraPlayer: Improved support for replay events; added ability to turn a HLS VoD stream into a rep …
- 2025-09-29 d34a730c ElectraPlayer: Emit warning about mismatched media segment duration only when the duration check was …
- 2025-09-29 49fa2b76 ElectraPlayer: Adjusting the maximum Live edge latency in case the media segments have a larger dura …
- 2025-09-23 0dc995dc ElectraPlayer: Using a VoD asset for a synchronized event now allows it to loop when provided via DA …
- 2025-09-11 d9f531d6 Electra: combined multiline raw string into a single line
```

### 维护评价

- **创建时间**：2025‑09‑11，距今不到半年。
- **近期更新**：持续有功能性更新（Replay 事件支持、HLS 段持续时间警告调整、Live 边缘延迟优化、VoD 循环事件）。
- **活跃度**：非常活跃，几乎每周都有提交，且多数为实质性功能增强与 bug 修复。
- **推荐使用**：推荐。该插件是目前虚幻引擎 5 中最为先进的跨平台媒体播放方案，官方持续投入维护。对于需要自适应流媒体或高性能本地播放的项目，是非常可靠的选择。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/ElectraPlayer)
- [官方文档](https://docs.unrealengine.com/en-US/Engine/MediaFramework/Overview)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/ElectraPlayer/Source/ElectraPlayerRuntime/Private/Tests)