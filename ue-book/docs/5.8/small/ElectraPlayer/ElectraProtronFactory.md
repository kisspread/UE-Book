# Electra Player

> Cross platform media player for local files and internet streaming. Also provides optimized local mp4 file only player (Protron) for desktop machines.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | Electra播放器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ElectraPlayerFactory` (Runtime), `ElectraPlayerPlugin` (Runtime), `ElectraPlayerPluginHandler` (Runtime), `ElectraPlayerRuntime` (Runtime), `ElectraProtron` (Runtime), `ElectraProtronFactory` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-01-06 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraPlayer) | |

## 用途
`ElectraPlayer` 插件是 Unreal Engine 的一个**跨平台、模块化媒体播放框架**。其核心价值在于提供统一的媒体播放能力，支持本地文件（如 MP4）和互联网流媒体（如 HLS, DASH）。
它并非一个单一的播放器，而是一个播放器框架：
1.  **ElectraPlayer**：通用的、功能完整的跨平台播放器引擎，负责解复用、解码、同步等核心功能。
2.  **ElectraProtron**：一个**高度优化的本地 MP4 播放器**，专为桌面平台（Windows）设计，旨在提供更低的延迟和更高的性能。它通过 `ElectraProtronFactory` 模块进行工厂化管理和配置。
3.  **ElectraPlayerFactory** / `ElectraProtronFactory`：工厂模块，负责根据配置或用户选择，实例化具体的播放器实现（Electra 或 Protron）。

当前文档聚焦于 `ElectraProtronFactory` 模块，它主要管理 `Protron` 播放器的**配置和工厂逻辑**。

## 使用场景
-   你需要在桌面平台（Windows）上播放本地 MP4 文件，且对**性能和播放起播速度有极高要求**（例如：游戏内的过场动画、UI 动态视频元素），此时应优先考虑使用 `Protron` 播放器。
-   你需要在自动选择播放器时，通过配置控制在游戏运行时或编辑器内是使用通用的 `Electra` 还是优化的 `Protron`。
-   你的应用需要处理流媒体协议，但希望在底层利用 `ElectraPlayerRuntime` 提供的统一解复用和网络处理能力。

## 蓝图用法

### 核心节点
`ElectraProtronFactory` 模块本身不暴露蓝图可调用函数，其核心价值是提供**项目设置**，影响播放器自动选择行为。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `bPreferProtronInEditor` | 在编辑器中，当媒体源未指定播放器时，是否优先使用 Protron 而非 Electra。 | `UElectraProtronFactorySettings` |
| `bPreferProtronInGame` | 在游戏中（打包后），当媒体源未指定播放器时，是否优先使用 Protron 而非 Electra。 | `UElectraProtronFactorySettings` |

### 使用示例（蓝图描述）
这些设置不在蓝图图表中连接，而是通过 **项目设置 (Project Settings)** 面板进行配置：
1.  打开编辑器，进入 `编辑 (Edit)` -> `项目设置 (Project Settings)`。
2.  在左侧导航树中找到 `插件 (Plugins)` -> `Electra Protron Factory`。
3.  在右侧详情面板中，你会看到 `General` 分类下的两个复选框：`Prefer Protron In Editor` 和 `Prefer Protron In Game`。根据你的需求勾选即可。
4.  配置生效后，所有使用 `UMediaPlayer` 且未显式指定播放器名称的媒体源，在对应环境下将自动尝试使用 `Protron` 播放器。

## C++ 用法

### 头文件引入
```cpp
#include “ElectraProtronFactorySettings.h”
```

### 基本用法
在 C++ 中访问或修改 `Protron` 播放器的工厂设置。
*(来源：基于 `Private/ElectraProtronFactorySettings.h` 的分析)*
```cpp
// 获取默认的 Protron 工厂设置对象（单例）
const UElectraProtronFactorySettings* Settings = GetDefault<UElectraProtronFactorySettings>();

if (Settings)
{
    // 读取配置：是否在游戏中优先使用 Protron
    bool bShouldUseProtronInGame = Settings->bPreferProtronInGame;
    
    UE_LOG(LogTemp, Log, TEXT(“Protron preferred in game: %s“), bShouldUseProtronInGame ? TEXT(“Yes”) : TEXT(“No”));
}
```

### 进阶用法
这些设置通常是持久化在 `DefaultEngine.ini` 中的。你可以在代码中动态修改运行时配置（注意：修改默认对象可能不会影响已缓存的设置副本，最佳实践是修改配置文件或使用配置系统API）。
```cpp
// 动态修改配置（通常用于工具或调试）
UElectraProtronFactorySettings* MutableSettings = GetMutableDefault<UElectraProtronFactorySettings>();
if (MutableSettings)
{
    MutableSettings->bPreferProtronInGame = true;
    // 注意：此更改可能需要保存到配置文件才能持久化
    MutableSettings->SaveConfig();
}
```

## Demo 示例
一个展示如何在运行时检查 Protron 工厂配置的 Actor。

**MyMediaActor.h**
```cpp
#pragma once
#include “CoreMinimal.h”
#include “GameFramework/Actor.h”
#include “MyMediaActor.generated.h”

UCLASS()
class AMyMediaActor : public AActor
{
    GENERATED_BODY()
public:
    AMyMediaActor();

protected:
    virtual void BeginPlay() override;
    
    UFUNCTION(BlueprintCallable, Category = “Media”)
    void PrintProtronConfig() const;
};
```

**MyMediaActor.cpp**
```cpp
#include “MyMediaActor.h”
#include “ElectraProtronFactorySettings.h”

AMyMediaActor::AMyMediaActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyMediaActor::BeginPlay()
{
    Super::BeginPlay();
    PrintProtronConfig();
}

void AMyMediaActor::PrintProtronConfig() const
{
    const UElectraProtronFactorySettings* ProtronSettings = GetDefault<UElectraProtronFactorySettings>();
    if (ProtronSettings)
    {
        UE_LOG(LogTemp, Warning, TEXT(“Electra Protron Factory Config:”));
        UE_LOG(LogTemp, Warning, TEXT(“  Prefer in Editor: %s“), ProtronSettings->bPreferProtronInEditor ? TEXT(“true”) : TEXT(“false”));
        UE_LOG(LogTemp, Warning, TEXT(“  Prefer in Game: %s“), ProtronSettings->bPreferProtronInGame ? TEXT(“true”) : TEXT(“false”));
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT(“Could not retrieve Electra Protron Factory Settings.”));
    }
}
```

## 模块依赖
当前模块 `ElectraProtronFactory` 的构建依赖。要使用此模块，你的模块需要在 `.Build.cs` 中添加以下依赖。

| 模块 | 用途 |
|---|---|
| `ElectraBase` | Electra 播放器的基础库，提供通用的接口、类型和工具。 |

## 维护状态

### 近期更新
| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-21 | `ff9996e8` | Media Profile: Fixed issue where ElectraProtron issue would not play a new video after it had alread... | 修复了 Protron 播放器播放完一个视频后无法播放新视频的问题。 |
| 2026-05-14 | `d15b78b3` | ElectraPlayer: Fixed streamed album metadata | 修复了流媒体播放时专辑元数据显示不正确的问题。 |
| 2026-05-13 | `4340cfa6` | ElectraPlayer: Added configuration and cvars to control if decoders need to be suspended during play | 添加了配置和控制台变量，用于控制播放期间是否挂起解码器。 |
| 2026-05-12 | `a6372743` | ElectraPlayer: changed an assertion to an if() condition to handle cases where .ts internal timestam... | 将断言改为条件判断，以处理 `.ts` 文件内部时间戳异常的情况，提高了稳定性。 |
| 2026-05-12 | `e3746831` | ElectraPlayer: Checking for sequence index when prefetching subtitle media segments to reduce unnece... | 在预取字幕媒体段时检查序列索引，减少不必要的网络请求。 |

### 维护评价
`ElectraPlayer` 插件（包括 `ElectraProtronFactory`）**处于积极维护状态**。
-   **创建时间**：约 4 年前（2021年），属于较新的核心系统级插件。
-   **近期活跃度**：最近（2026年5月）有多次功能性更新和 Bug 修复，涉及播放稳定性、元数据、解码器控制等核心功能，表明 Epic 团队仍在持续投入。
-   **状态**：**活跃维护中**。无废弃迹象，反而在不断增强功能和修复问题。
-   **推荐度**：**强烈推荐**。对于需要高性能本地 MP4 播放（尤其是桌面平台）或跨平台流媒体播放的项目，应优先评估和使用此插件。其模块化设计允许灵活选择播放器实现。

## 相关链接
-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraPlayer)
-   [官方文档](https://docs.unrealengine.com/en-US/Engine/MediaFramework/Overview)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraPlayer/Tests)