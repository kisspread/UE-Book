# Mass Signals

> Implementation of large-scale agent simulation based on MassEntity

| 属性 | 值 |
|---|---|
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MassSignals` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MassGameplay/Source/MassSignals) | |

## 用途

MassSignals 模块为 MassEntity 框架提供了一套轻量级的信号（Signal）系统。它解决了在大规模实体（Mass Entity）模拟中，如何高效、解耦地进行实体间通信和事件通知的问题。不同于传统的委托或事件系统，MassSignals 通过名称和位掩码管理信号，专为处理成千上万个实体的通信而优化，支持即时、延迟和异步信号发送。

## 使用场景

- 你正在开发一个拥有大量单位（如 RTS 游戏、模拟城市）的游戏，需要向特定单位或单位群体发送指令（如“攻击”、“移动到某点”）。
- 你需要实现群体 AI 行为，当某个实体（如领头羊）发出信号时，附近的其他实体需要做出响应。
- 你需要一个解耦的系统，让不同的处理器（Processor）能够响应游戏世界中发生的事件，而无需直接引用彼此。

## 蓝图用法

MassSignals 主要通过 `UMassSignalSubsystem` 子系统暴露蓝图接口。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Signal Entity` | 向单个实体发送一个即时信号 | `UMassSignalSubsystem` |
| `Signal Entities` | 向一组实体发送一个即时信号 | `UMassSignalSubsystem` |
| `Delay Signal Entity` | 向单个实体发送一个延迟信号 | `UMassSignalSubsystem` |
| `Delay Signal Entities` | 向一组实体发送一个延迟信号 | `UMassSignalSubsystem` |
| `Signal Entity Deferred` | 通过命令缓冲区异步向单个实体发送信号 | `UMassSignalSubsystem` |
| `Signal Entities Deferred` | 通过命令缓冲区异步向一组实体发送信号 | `UMassSignalSubsystem` |
| `Delay Signal Entity Deferred` | 通过命令缓冲区异步向单个实体发送延迟信号 | `UMassSignalSubsystem` |
| `Delay Signal Entities Deferred` | 通过命令缓冲区异步向一组实体发送延迟信号 | `UMassSignalSubsystem` |

### 使用示例（蓝图描述）

1.  **获取子系统**：在任何需要发送信号的地方，使用 `Get Game Instance Subsystem` 节点获取 `UMassSignalSubsystem` 的实例。
2.  **发送信号**：将目标实体句柄（`FMassEntityHandle`）和一个信号名称（`FName`，例如 `“Attack”`）连接到 `Signal Entity` 节点的输入引脚。
3.  **接收信号**：创建一个继承自 `UMassSignalProcessorBase` 的蓝图类。在类中重写 `SignalEntities` 事件。在该事件中，你可以遍历接收到的实体，并根据信号名称执行逻辑。在处理器的初始化逻辑中，需要调用 `SubscribeToSignal` 函数来订阅你关心的信号名称。

## C++ 用法

### 头文件引入

```cpp
#include "MassSignalSubsystem.h"
#include "MassSignalProcessorBase.h"
#include "MassSignalTypes.h"
```

### 基本用法

**1. 发送信号**
```cpp
// 获取信号子系统
UMassSignalSubsystem* SignalSubsystem = GetWorld()->GetSubsystem<UMassSignalSubsystem>();
if (SignalSubsystem)
{
    // 向单个实体发送即时信号
    FMassEntityHandle TargetEntity = ...; // 获取目标实体句柄
    SignalSubsystem->SignalEntity(FName(“MySignal”), TargetEntity);

    // 向一组实体发送延迟信号（2秒后）
    TArray<FMassEntityHandle> TargetEntities = ...;
    SignalSubsystem->DelaySignalEntities(FName(“DelayedAlert”), TargetEntities, 2.0f);
}
```

**2. 创建信号处理器**
```cpp
// MySignalProcessor.h
#pragma once
#include “MassSignalProcessorBase.h”
#include “MySignalProcessor.generated.h”

UCLASS()
class UMySignalProcessor : public UMassSignalProcessorBase
{
    GENERATED_BODY()
public:
    UMySignalProcessor();

protected:
    virtual void ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager) override;
    virtual void SignalEntities(FMassEntityManager& EntityManager, FMassExecutionContext& Context, FMassSignalNameLookup& EntitySignals) override;
};

// MySignalProcessor.cpp
#include “MySignalProcessor.h”
#include “MassSignalSubsystem.h”

UMySignalProcessor::UMySignalProcessor()
{
    // 设置处理器执行顺序等
    ExecutionOrder.ExecuteInGroup = FName(“MyProcessingGroup”);
    ProcessingPhase = EMassProcessingPhase::PrePhysics;
}

void UMySignalProcessor::ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager)
{
    // 配置查询，定义此处理器关心哪些实体片段（Fragment）
    EntityQuery.AddRequirement<FMassRepresentationFragment>(EMassFragmentAccess::ReadWrite);
    // ... 其他需求
}

void UMySignalProcessor::SignalEntities(FMassEntityManager& EntityManager, FMassExecutionContext& Context, FMassSignalNameLookup& EntitySignals)
{
    // 遍历所有匹配查询的实体
    EntityQuery.ForEachEntityChunk(EntityManager, Context, [this, &EntitySignals](FMassExecutionContext& Context)
    {
        // 获取当前块中的实体句柄数组
        TConstArrayView<FMassEntityHandle> Entities = Context.GetEntities();
        for (const FMassEntityHandle& Entity : Entities)
        {
            // 获取该实体本帧接收到的信号
            TArray<FName> Signals;
            EntitySignals.GetSignalsForEntity(Entity, Signals);

            // 检查是否收到了我们关心的信号
            if (Signals.Contains(FName(“MySignal”)))
            {
                // 执行响应逻辑，例如修改实体片段
                // FMassRepresentationFragment& RepFragment = Context.GetMutableFragmentView<FMassRepresentationFragment>()[Entity];
                // RepFragment.SomeProperty = NewValue;
            }
        }
    });
}
```

**3. 订阅信号**
```cpp
// 通常在处理器的初始化或开始游戏时调用
void UMySignalProcessor::Initialize(UObject& Owner)
{
    Super::Initialize(Owner);

    UWorld* World = Owner.GetWorld();
    if (UMassSignalSubsystem* SignalSubsystem = World->GetSubsystem<UMassSignalSubsystem>())
    {
        // 订阅名为 “MySignal” 的信号
        SubscribeToSignal(*SignalSubsystem, FName(“MySignal”));
    }
}
```

### 进阶用法

**异步信号与命令缓冲区**
在处理器的 `Execute` 方法中，你可能需要发送信号，但直接调用 `SignalEntity` 可能不安全。此时应使用 `Deferred` 版本。
```cpp
void UMyAdvancedProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    // ... 处理逻辑

    // 在处理器执行期间，安全地发送异步信号
    if (UMassSignalSubsystem* SignalSubsystem = Context.GetWorld()->GetSubsystem<UMassSignalSubsystem>())
    {
        FMassEntityHandle SomeEntity = ...;
        SignalSubsystem->SignalEntityDeferred(Context, FName(“FollowUpSignal”), SomeEntity);
    }
}
```

## Demo 示例

**MySignalDemoProcessor.h**
```cpp
#pragma once
#include “MassSignalProcessorBase.h”
#include “MySignalDemoProcessor.generated.h”

UCLASS()
class UMySignalDemoProcessor : public UMassSignalProcessorBase
{
    GENERATED_BODY()
public:
    UMySignalDemoProcessor();

protected:
    virtual void ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager) override;
    virtual void SignalEntities(FMassEntityManager& EntityManager, FMassExecutionContext& Context, FMassSignalNameLookup& EntitySignals) override;
};
```

**MySignalDemoProcessor.cpp**
```cpp
#include “MySignalDemoProcessor.h”
#include “MassCommonFragments.h” // 假设使用基础片段
#include “MassSignalSubsystem.h”

UMySignalDemoProcessor::UMySignalDemoProcessor()
{
    ExecutionOrder.ExecuteInGroup = FName(“Demo”);
    ProcessingPhase = EMassProcessingPhase::PrePhysics;
    bAutoRegisterWithProcessingPhases = true; // 自动注册
}

void UMySignalDemoProcessor::ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager)
{
    // 要求实体拥有 Transform 片段
    EntityQuery.AddRequirement<FTransformFragment>(EMassFragmentAccess::ReadOnly);
}

void UMySignalDemoProcessor::SignalEntities(FMassEntityManager& EntityManager, FMassExecutionContext& Context, FMassSignalNameLookup& EntitySignals)
{
    EntityQuery.ForEachEntityChunk(EntityManager, Context, [&EntitySignals](FMassExecutionContext& Context)
    {
        TConstArrayView<FMassEntityHandle> Entities = Context.GetEntities();
        for (const FMassEntityHandle& Entity : Entities)
        {
            TArray<FName> Signals;
            EntitySignals.GetSignalsForEntity(Entity, Signals);

            if (Signals.Contains(FName(“Ping”)))
            {
                // 收到 “Ping” 信号，记录日志（实际项目中可执行移动、动画等）
                UE_LOG(LogTemp, Log, TEXT(“Entity %s received Ping signal.”), *Entity.DebugGetDescription());
            }
        }
    });
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

- 2024-10-26 ec9009980d52 为包含对应 .gen.cpp 文件的源文件添加了 UE_INLINE_GENERATED_CPP_BY_NAME。
- 2024-10-25 b1980471196e [Mass] 对 MassEntityManager 进行了小规模清理，包括移除一些头文件包含。
- 2024-10-25 a60b2b5c1723 为合并的模块修复了 API 宏，PURE_VIRTUAL 不再需要 API 导出。

### 维护评价

MassSignals 模块创建于 2021 年，是 MassEntity 框架的核心通信组件之一。从近期提交记录看，它仍在被 Epic Games 积极维护，但更新主要集中在代码清理、编译修复和 API 规范化上，而非新功能开发。作为 `IsExperimentalVersion: true` 的插件的一部分，它仍处于实验阶段，API 可能在未来版本中发生变化。考虑到其基础性和稳定性，它适合在实验性项目或需要大规模实体模拟的场景中谨慎使用，但不建议用于追求长期稳定性的生产项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MassGameplay/Source/MassSignals)
- [官方文档]()（暂无）
- [测试用例]()（暂未在模块目录内发现）