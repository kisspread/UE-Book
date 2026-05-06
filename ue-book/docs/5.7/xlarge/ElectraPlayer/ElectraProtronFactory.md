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

## 用途

Electra Player 是 UE5 内置的高性能跨平台媒体播放器，支持本地文件和网络流媒体（HLS、DASH、MP4 等）。插件内部由多个模块组成，其中 **ElectraProtronFactory** 模块负责控制编辑器/游戏过程中是否自动优先选用 Protron（专为桌面平台优化的本地 MP4 播放器）而非默认的 Electra 播放器。此模块提供全局配置设置，允许开发者在不影响 Electra 完整功能的前提下，为简单本地 MP4 播放获得更好的性能。

## 使用场景

- 你在游戏中需要播放本地 MP4 文件（如过场动画、教学视频） → 通过 Protron 获得更高性能
- 你在编辑器中预览媒体资产时希望使用更轻量的播放器提升编辑体验 → 配置 `bPreferProtronInEditor = true`
- 你的项目依赖自动播放器选择机制（媒体源未明确指定播放器） → 通过此工厂设置调整默认偏好

## 蓝图用法

ElectraProtronFactory 模块本身不暴露蓝图可调用函数或属性（其设置类 `UElectraProtronFactorySettings` 属于配置对象，通过项目设置面板访问）。整个 Electra Player 插件的蓝图用法主要集中在其媒体源和媒体播放器组件上，例如使用 `MediaPlayer` 和 `FileMediaSource` 资产。具体蓝图节点请参考官方文档。

### 项目设置面板

| 设置项 | 类型 | 说明 |
|---|---|---|
| `Prefer Protron In Editor` | bool | 编辑器下当媒体源未指定播放器时，优先使用 Protron |
| `Prefer Protron In Game` | bool | 运行时当媒体源未指定播放器时，优先使用 Protron |

这些设置在 **项目设置 → Media → ElectraProtronFactory** 中可视化配置。

## C++ 用法

### 头文件引入

```cpp
#include "ElectraProtronFactorySettings.h"
```

### 基本用法

配置对象是全局单例，可通过默认对象直接访问设置：

```cpp
UElectraProtronFactorySettings* Settings = GetMutableDefault<UElectraProtronFactorySettings>();
if (Settings)
{
    Settings->bPreferProtronInEditor = true;  // 编辑器下优先使用 Protron
    Settings->bPreferProtronInGame = false;   // 游戏运行时默认使用 Electra
    Settings->SaveConfig();                   // 保存到配置文件中
}
```

### 进阶用法

配合播放器选择逻辑，在运行时查询当前设置并决定使用哪个播放器：

```cpp
#include "ElectraProtronFactorySettings.h"

bool ShouldUseProtron(bool bIsEditor)
{
    const UElectraProtronFactorySettings* Settings = GetDefault<UElectraProtronFactorySettings>();
    return bIsEditor ? Settings->bPreferProtronInEditor : Settings->bPreferProtronInGame;
}
```

## Demo 示例

以下是一个最小 C++ 示例，展示如何在游戏加载时根据设置切换播放器。

```cpp
// MyMediaPlayerManager.h
#pragma once
#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "MyMediaPlayerManager.generated.h"

UCLASS()
class UMyMediaPlayerManager : public UObject
{
    GENERATED_BODY()
public:
    void Initialize();
};

// MyMediaPlayerManager.cpp
#include "MyMediaPlayerManager.h"
#include "ElectraProtronFactorySettings.h"
#include "MediaPlayer.h"
#include "FileMediaSource.h"

void UMyMediaPlayerManager::Initialize()
{
    // 获取设置
    const UElectraProtronFactorySettings* Settings = GetDefault<UElectraProtronFactorySettings>();
    const bool bUseProtron = Settings->bPreferProtronInGame;

    // 创建媒体播放器（示例中通过 UImfMediaSource 或 UFileMediaSource 加载）
    UMediaPlayer* MediaPlayer = NewObject<UMediaPlayer>();
    UFileMediaSource* MediaSource = NewObject<UFileMediaSource>();
    MediaSource->SetFilePath(TEXT("/Game/Movies/Intro.mp4"));

    // 根据设置选择播放（实际播放器选择由 Media Framework 自动处理，此处仅为演示）
    if (bUseProtron)
    {
        UE_LOG(LogTemp, Log, TEXT("Using Protron player (optimized for local MP4)."));
    }
    else
    {
        UE_LOG(LogTemp, Log, TEXT("Using Electra player (full streaming support)."));
    }

    MediaPlayer->OpenSource(MediaSource);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ElectraBase` | 提供基础类型和日志工具（`LogElectraProtronFactory`） |

其他依赖均属于标准 Unreal Engine 核心模块，未列出。

## 维护状态

### 近期更新

- 2025-10-01 `31d4710d` ElectraPlayer: Improved support for replay events; added ability to turn a HLS VoD stream into a rep
- 2025-09-29 `d34a730c` ElectraPlayer: Emit warning about mismatched media segment duration only when the duration check was
- 2025-09-29 `49fa2b76` ElectraPlayer: Adjusting the maximum Live edge latency in case the media segments have a larger dura
- 2025-09-23 `0dc995dc` ElectraPlayer: Using a VoD asset for a synchronized event now allows it to loop when provided via DA
- 2025-09-11 `d9f531d6` Electra: combined multiline raw string into a single line

### 维护评价

Electra Player 是 UE5 内置的核心媒体插件，由 Epic Games 持续维护。最近一个月内有多次功能性更新和 bug 修复，社区活跃。ElectraProtronFactory 子模块虽然提供简单的配置，但其依赖的 Protron 播放器持续得到优化。综合来看：

- **创建时间**：2025 年 9 月（全新模块）
- **更新频率**：高（每周都有提交）
- **维护状态**：活跃维护
- **推荐程度**：强烈推荐——作为官方媒体播放器方案，功能完整且性能优秀。Protron 工厂设置让开发者能灵活优化桌面 MP4 播放体验。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/ElectraPlayer)
- [官方文档](https://docs.unrealengine.com/en-US/Engine/MediaFramework/Overview)
- [ElectraPlayerRuntime 测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Source/Programs/AutomationTool/Scripts/Tests/ElectraPlayer)