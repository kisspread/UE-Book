# Stage Monitor

> Plugin enabling monitoring in the context of a virtual production stage where multiple machines are in operation

| 属性 | 值 |
|---|---|
| 中文名 | 舞台监控 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `StageMonitor` (UncookedOnly), `StageMonitorEditor` (Editor), `StageDataProvider` (Runtime), `StageMonitorCommon` (Runtime) |
| 实验性 | ⚦ 是 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StageMonitoring) | |

## 用途

StageMonitoring 插件为虚拟制作（Virtual Production）环境提供了一套集中式监控解决方案。在由多台机器（例如摄像机控制、渲染节点、合成工作站）协同工作的虚拟拍摄现场，此插件解决的核心问题是：如何从单一界面监控整个制作流水线的健康状态、性能指标和运行日志，以便快速定位瓶颈或故障。

## 使用场景

- **多机虚拟拍摄监控**：你正在管理一个由多台 Unreal Engine 实例驱动的虚拟摄影棚，需要集中查看所有机器的 CPU/GPU 负载、内存占用、帧率、网络延迟以及关键事件日志。
- **性能调优与问题排查**：在调试复杂的虚拟制作流水线时，你需要关联不同机器上的性能数据和日志，以追踪问题的根源，例如某台渲染机器的延迟是否影响了最终合成画面。
- **远程状态检查**：导演或技术总监在另一个房间需要通过网络查看各工作站的实时状态，确保拍摄顺利进行。

## 蓝图用法

本插件主要通过蓝图子系统与数据提供者模式运作，核心交互围绕数据收集与界面展示。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetStageMonitoringSubsystem` | 获取舞台监控子系统，用于管理数据提供者和发送监控请求。 | `UStageMonitoringSubsystem` |
| `RegisterDataProvider` | 向监控子系统注册一个数据提供者，以开始提供特定类型的性能或状态数据。 | `UStageDataProvider` |
| `GetPerformanceReport` | 请求获取当前或历史的性能报告数据。 | `UStageMonitoringSubsystem` |
| `BroadcastMonitoringEvent` | 向监控中心广播一个自定义事件（例如“镜头开始拍摄”）。 | `UStageMonitoringSubsystem` |
| `SetMonitoringEnabled` | 启用或禁用全局监控数据采集。 | `UStageMonitoringSubsystem` |

### 使用示例（蓝图描述）

1.  在你的游戏模式或蓝图初始化事件中，使用 `GetStageMonitoringSubsystem` 节点获取子系统引用。
2.  创建一个 `StageDataProvider` 的子类蓝图，重写其 `CollectData` 函数，在其中收集你需要的性能数据（如帧时间、显存使用）。
3.  在初始化时，调用 `RegisterDataProvider` 节点将上一步创建的数据提供者注册到子系统中。
4.  在监控界面蓝图中，可以调用 `GetPerformanceReport` 来获取并显示数据。
5.  使用 `BroadcastMonitoringEvent` 在重要节点（如关卡加载完成、特定Gameplay事件发生时）发送事件，以便在监控日志中记录。

## C++ 用法

核心用法围绕实现自定义数据提供者（Data Provider）和使用子系统。

### 头文件引入

```cpp
#include “StageDataProvider.h”
#include “StageMonitoringSubsystem.h”
// 来自 StageMonitorCommon 模块
#include “StageMonitorCommon.h”
```

### 基本用法

```cpp
// 来源于 Source/StageMonitorCommon 的示例模式
// 创建一个自定义数据提供者
UCLASS()
class UMyPerformanceDataProvider : public UStageDataProvider
{
    GENERATED_BODY()
public:
    virtual void CollectData(FStageMonitoringData& Data) override
    {
        // 收集并填充数据
        Data.AddMetric(TEXT(“MyFrameTime”), GetWorld()->GetDeltaSeconds());
        Data.AddMetric(TEXT(“ActorCount”), GetWorld()->GetCurrentLevel()->Actors.Num());
    }
};
```

```cpp
// 在某个初始化阶段注册数据提供者
if (UStageMonitoringSubsystem* MonitoringSubsystem = GetWorld()->GetSubsystem<UStageMonitoringSubsystem>())
{
    UMyPerformanceDataProvider* MyProvider = NewObject<UMyPerformanceDataProvider>(this);
    MonitoringSubsystem->RegisterDataProvider(MyProvider);
}
```

### 进阶用法

实现一个基于事件的数据提供者，并在特定 Gameplay 事件中广播信息。

```cpp
// 自定义事件数据提供者
UCLASS()
class UGameplayEventDataProvider : public UStageDataProvider
{
    GENERATED_BODY()
public:
    // 由外部 Gameplay 逻辑调用
    void ReportGameplayEvent(const FString& EventName, const FString& Details)
    {
        FStageMonitoringEvent Event;
        Event.Name = EventName;
        Event.Details = Details;
        // 假设有一个缓冲区存储事件，等待下次 CollectData 调用
        PendingEvents.Add(Event);
    }

    virtual void CollectData(FStageMonitoringData& Data) override
    {
        for (const FStageMonitoringEvent& Event : PendingEvents)
        {
            Data.AddEvent(Event);
        }
        PendingEvents.Empty();
    }
private:
    TArray<FStageMonitoringEvent> PendingEvents;
};

// 在 Gameplay 代码中使用
void AMyGameMode::OnShotStarted()
{
    if (UGameplayEventDataProvider* EventProvider = FindEventProvider())
    {
        EventProvider->ReportGameplayEvent(TEXT(“ShotStarted”), TEXT(“Take: 5, Shot: 12”));
    }
    // 同时，也可以直接通过子系统广播
    if (UStageMonitoringSubsystem* Sub = GetWorld()->GetSubsystem<UStageMonitoringSubsystem>())
    {
        Sub->BroadcastMonitoringEvent(FName(“ShotStarted”));
    }
}
```

## Demo 示例

一个最小化的数据提供者示例，持续报告当前世界的 Actor 数量。

**MyActorCountProvider.h**
```cpp
#pragma once
#include "StageDataProvider.h"
#include "MyActorCountProvider.generated.h"

UCLASS()
class MYPROJECT_API UMyActorCountProvider : public UStageDataProvider
{
    GENERATED_BODY()
public:
    virtual void CollectData(FStageMonitoringData& Data) override;
};
```

**MyActorCountProvider.cpp**
```cpp
#include "MyActorCountProvider.h"
#include "Engine/World.h"

void UMyActorCountProvider::CollectData(FStageMonitoringData& Data)
{
    if (UWorld* World = GetWorld())
    {
        // 假设 FStageMonitoringData 提供了 AddMetric 方法
        Data.AddMetric(“TotalActors”, World->GetCurrentLevel()->Actors.Num());
        // 也可以添加文本信息
        Data.AddText(“WorldName”, World->GetName());
    }
}
```

注册和使用：
```cpp
// 在 GameMode 或 Actor 的 BeginPlay 中
void AMyGameMode::BeginPlay()
{
    Super::BeginPlay();
    if (UStageMonitoringSubsystem* Sub = GetWorld()->GetSubsystem<UStageMonitoringSubsystem>())
    {
        UMyActorCountProvider* Provider = NewObject<UMyActorCountProvider>(this);
        Sub->RegisterDataProvider(Provider);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Takes` | 用于集成虚拟制作拍摄流程和 Take 信息。 |
| `VirtualProductionUtilities` | 提供虚拟制作相关的通用工具函数。 |
| `SlateCore`, `UMG` | 用于构建监控器编辑器界面和UI控件。 |
| `Json` | 用于序列化监控数据为JSON格式，便于传输和存储。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构JSON对象以同时支持FString和UE::FSharedString，优化内存使用 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧的UE_LOG宏迁移到新的UE_LOGF格式 |
| 2026-03-02 | `9758fa58` | FORT-984709 - Remove string duplication in FJsonObject to free memory | 移除FJsonObject中的字符串重复以释放内存 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-rereplace. | 修复了上一次错误查找替换后的第二次尝试 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退了某个变更 |

### 维护评价

- **状态**：**活跃维护**。尽管插件标记为实验性（IsBetaVersion=true），但从近期的提交历史来看，开发团队在持续对其进行优化和重构，特别是针对JSON处理、内存管理和日志系统这些底层功能。
- **建议**：该插件是 Epic 为虚拟制作工作流提供的官方工具，功能具有明确的针对性。对于正在构建或使用多机虚拟制作流水线的项目，推荐在实验性环境下评估和使用，但需关注其可能随版本迭代发生API变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StageMonitoring)
- [官方文档]() （无）