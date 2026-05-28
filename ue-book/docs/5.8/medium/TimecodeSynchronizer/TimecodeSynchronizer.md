# Timecode Synchronizer (Deprecated)

> This plugin has been deprecated and will be removed in a future engine version. Please update your project to use the features of the TimedDataMonitor plugin instead.
> An asset that will become the TimecodeProvider once all the inputs get synchronized to a timecode.

| 属性 | 值 |
|---|---|
| 中文名 | 时间码同步器 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `TimecodeSynchronizer` (Runtime), `TimecodeSynchronizerEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-05-14 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/TimecodeSynchronizer) | |

## 用途

**重要：该插件已在 UE 5.0 中被废弃，计划在未来引擎版本中移除。所有新项目应使用 `TimedDataMonitor` 插件。**

该插件是一个虚拟制片工具，旨在解决多个输入源（如摄像机、音频、渲染节点）之间的时间码同步问题。它充当一个**协调者**，管理一组 `UTimeSynchronizationSource` 输入源，监控这些源的可用帧缓冲区，等待所有源都有可以对齐的帧，然后确定一个统一的、同步后的时间码，并将其提供给引擎。这可以确保所有输入源产生的数据是帧对齐的，对于 nDisplay 等多视图渲染或多引擎同步场景至关重要。

## 使用场景

- **已废弃**：此插件已废弃，**不建议在新项目中使用**。
- **历史场景（供参考）**：
    - 使用 nDisplay 将一个场景渲染到多个显示器或渲染节点时，需要所有节点的渲染帧和输入数据严格同步。
    - 在虚拟制片中，从多个摄像机、音频设备或跟踪系统接收输入，并需要将所有数据与一个统一的主时间码对齐。
    - **迁移方案**：如果您正在维护一个使用了此插件的老项目，应计划将其功能迁移到官方推荐的 `TimedDataMonitor` 插件。

## 蓝图用法

**警告：以下 API 均已标记为 `UE_DEPRECATED`，在未来的引擎版本中将被移除。仅适用于维护遗留项目。**

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `StartSynchronization` | 启动同步过程。如果已同步或正在同步，则不执行任何操作。返回是否成功启动。 | `UTimecodeSynchronizer` |
| `StopSynchronization` | 停止同步过程。如果未同步或未尝试同步，则不执行任何操作。 | `UTimecodeSynchronizer` |
| `GetSynchronizationState` | 获取同步提供者的当前同步状态（例如：已同步、正在同步、未同步、错误）。 | `UTimecodeSynchronizer` (继承自 `UTimecodeProvider`) |
| `GetSynchronizedSources` | 返回用于执行同步的源列表。 | `UTimecodeSynchronizer` |
| `GetNonSynchronizedSources` | 返回未被积极用于同步的源列表。 | `UTimecodeSynchronizer` |
| `OnSynchronizationEvent` | 一个委托事件，在同步过程状态改变（开始、成功、失败、停止）时广播。 | `UTimecodeSynchronizer` |

### 使用示例（蓝图描述）

1.  在您的游戏模式或管理类中，通过 `UTimecodeSynchronizerProjectSettings` 获取或创建一个 `UTimecodeSynchronizer` 实例。
2.  配置该实例的属性（如 `TimeSynchronizationInputSources` 数组，添加需要同步的输入源资产）。
3.  调用 `StartSynchronization` 节点来启动同步流程。
4.  绑定 `OnSynchronizationEvent` 委托，根据事件（如 `SynchronizationSucceeded`）来执行后续操作，例如开始录制或传输数据。
5.  在需要时调用 `StopSynchronization` 来结束同步。

## C++ 用法

**警告：以下 API 均已标记为 `UE_DEPRECATED`，在未来的引擎版本中将被移除。仅适用于维护遗留项目。**

### 头文件引入

```cpp
#include "TimecodeSynchronizer.h"
```

### 基本用法

创建并配置一个时间码同步器实例，并启动同步。

```cpp
// 获取项目设置中默认的同步器（如果配置了的话）
UTimecodeSynchronizerProjectSettings* Settings = GetMutableDefault<UTimecodeSynchronizerProjectSettings>();
if (UTimecodeSynchronizer* Synchronizer = Settings->DefaultTimecodeSynchronizer.Get())
{
    // 启动同步
    bool bStarted = Synchronizer->StartSynchronization();

    // 绑定同步事件回调
    Synchronizer->OnSynchronizationEvent().AddLambda([](ETimecodeSynchronizationEvent Event)
    {
        switch (Event)
        {
        case ETimecodeSynchronizationEvent::SynchronizationSucceeded:
            UE_LOG(LogTemp, Log, TEXT("Timecode Synchronization succeeded!"));
            break;
        case ETimecodeSynchronizerEvent::SynchronizationFailed:
            UE_LOG(LogTemp, Error, TEXT("Timecode Synchronization failed!"));
            break;
        default:
            break;
        }
    });
}
```

*(示例逻辑基于 `UTimecodeSynchronizer` 公共接口推断)*

### 进阶用法

在同步开始后，动态添加运行时源。

```cpp
// 假设已经有一个同步器实例 `Synchronizer`
// 在 `StartSynchronization` 成功后，通过 `OnSynchronizationEvent` 回调中添加
Synchronizer->OnSynchronizationEvent().AddLambda([Synchronizer](ETimecodeSynchronizationEvent Event)
{
    if (Event == ETimecodeSynchronizationEvent::SynchronizationStarted)
    {
        // 创建一个临时的、用于运行时的数据源
        UTimeSynchronizationSource* DynamicSource = CreateDynamicSourceSomehow();
        Synchronizer->AddRuntimeTimeSynchronizationSource(DynamicSource);
    }
});
```

## Demo 示例

**注意：此插件已废弃。以下代码仅为遗留系统维护参考，不建议在新项目中使用。**

`TimecodeSynchronizerDemo.h`
```cpp
// TimecodeSynchronizerDemo.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "TimecodeSynchronizerDemo.generated.h"

UCLASS()
class ATimecodeSynchronizerDemo : public AActor
{
    GENERATED_BODY()

public:
    ATimecodeSynchronizerDemo();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    UPROPERTY(VisibleAnywhere, Category = "TimecodeSynchronizer")
    class UTimecodeSynchronizer* MySynchronizer;

private:
    UFUNCTION()
    void OnSynchronizationEvent(ETimecodeSynchronizationEvent Event);
};
```

`TimecodeSynchronizerDemo.cpp`
```cpp
// TimecodeSynchronizerDemo.cpp
#include "TimecodeSynchronizerDemo.h"
#include "TimecodeSynchronizer.h" // 已废弃

ATimecodeSynchronizerDemo::ATimecodeSynchronizerDemo()
{
    PrimaryActorTick.bCanEverTick = false;
    // 在构造函数中创建同步器实例（实际项目中通常从设置或资产获取）
    MySynchronizer = CreateDefaultSubobject<UTimecodeSynchronizer>(TEXT("TimecodeSync"));
}

void ATimecodeSynchronizerDemo::BeginPlay()
{
    Super::BeginPlay();

    if (MySynchronizer)
    {
        // 绑定事件
        MySynchronizer->OnSynchronizationEvent().AddUObject(this, &ATimecodeSynchronizerDemo::OnSynchronizationEvent);

        // (可选) 配置输入源列表 MySynchronizer->TimeSynchronizationInputSources
        // ...

        // 启动同步
        if (MySynchronizer->StartSynchronization())
        {
            UE_LOG(LogTemp, Log, TEXT("TimecodeSynchronizer: Synchronization initiated."));
        }
    }
}

void ATimecodeSynchronizerDemo::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (MySynchronizer)
    {
        MySynchronizer->StopSynchronization();
    }
    Super::EndPlay(EndPlayReason);
}

void ATimecodeSynchronizerDemo::OnSynchronizationEvent(ETimecodeSynchronizationEvent Event)
{
    if (Event == ETimecodeSynchronizationEvent::SynchronizationSucceeded)
    {
        UE_LOG(LogTemp, Log, TEXT("TimecodeSynchronizer: All sources are now synchronized!"));
        // 在这里可以获取同步后的时间码
        FQualifiedFrameTime SyncedTime = MySynchronizer->GetQualifiedFrameTime();
    }
}
```

## 模块依赖

从 `TimecodeSynchronizer.Build.cs` 和模块用途推断，该插件依赖于媒体框架和时间管理模块。

| 模块 | 用途 |
|---|---|
| `MediaFramework` | 底层媒体框架支持 |
| `Media` | 媒体播放器和源的核心功能 |
| `MediaAssets` | 媒体相关的资产类型 |
| `TimeManagement` | 引擎的时间管理、时间码和帧率处理 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 `UE_LOG` 迁移为 `UE_LOGF`（格式化日志）。 |
| 2025-10-07 | `96352708` | - Renaming Base<Plugin>.ini to Default<Plugin>.ini | 将配置文件 `Base<Plugin>.ini` 重命名为 `Default<Plugin>.ini`。 |
| 2025-06-13 | `b3edcb21` | Replace some usages of FORCEINLINE with inline in MovieScene modules. | 在 MovieScene 模块中，将部分 `FORCEINLINE` 替换为 `inline`。 |
| 2023-11-29 | `c98c8912` | Fix C4702 warnings | 修复编译器警告 C4702（不可达代码）。 |
| 2023-02-18 | `e599d19e` | Removing redundant Private includes. | 移除了多余的 `Private` 目录下的头文件包含。 |

### 维护评价

- **状态：可能废弃**
- **创建时间**：2018年5月，已有约8年历史。
- **近期更新**：最近几次提交均为代码维护性更新（重命名、警告修复、格式调整），**没有功能性更新**。最后的功能性改动需要追溯到更早。
- **官方状态**：`.uplugin` 的 `Description` 明确指出该插件**已废弃**，所有核心类均标记为 `UE_DEPRECATED(5.0)`，并推荐使用 `TimedDataMonitor` 插件替代。`IsBetaVersion=true` 也表明其长期处于实验状态。
- **推荐**：**强烈不推荐在新项目中使用此插件**。对于维护遗留项目，应制定计划向 `TimedDataMonitor` 迁移。不应对该插件进行新功能开发或期待其获得官方支持。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/TimecodeSynchronizer)
- [官方文档（无专用页面）](https://docs.unrealengine.com) - 请查阅 `TimedDataMonitor` 的相关文档。
- 测试用例：未在插件目录内发现明确的测试文件。