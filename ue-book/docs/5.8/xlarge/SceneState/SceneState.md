# Motion Design Scene State

> 

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计场景状态 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容） |
| 模块 | `SceneState` (Runtime), `SceneStateBinding` (Runtime), `SceneStateBlueprint` (Runtime), `SceneStateBlueprintEditor` (Runtime), `SceneStateEditor` (Runtime), `SceneStateEvent` (Runtime), `SceneStateEventEditor` (Runtime), `SceneStateEventGraph` (Runtime), `SceneStateGameplay` (Runtime), `SceneStateGameplayEditor` (Runtime), `SceneStateMachineEditor` (Runtime), `SceneStateMachineGraph` (Runtime), `SceneStateTasks` (Runtime), `SceneStateTransitionGraph` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/SceneState) | |

## 用途

`SceneState` 插件提供了一个**专为虚拟制作（Virtual Production）和动态设计（Motion Design）工作流构建的、基于状态机的运行时框架**。它并非一个通用的状态机库，而是旨在解决特定领域内的复杂控制与同步问题。

通过分析其核心类（如 `USceneStateObject`、`FSceneStateMachine`、`FSceneStateTask`）可以推断，它允许用户通过蓝图或C++定义一系列的状态、任务（Tasks）和转换（Transitions），这些定义被编译成高效、可运行的数据（`USceneStateTemplateData`）。其核心价值在于：
1.  **抽象复杂流程**：将复杂的序列化动画、灯光变化、特效触发、摄像机控制等逻辑，从零散的蓝图或C++代码中抽离，提升可维护性。
2.  **数据驱动**：状态和任务的定义与具体逻辑分离，使得内容创作人员可以更直观地编排场景流程。
3.  **高性能运行**：通过模板数据（`USceneStateTemplateData`）和执行上下文（`FSceneStateExecutionContext`）的分离，实现了实例数据的高效管理和执行，避免了运行时频繁的分配和拷贝。
4.  **与属性系统深度集成**：通过 `SceneStateBinding` 等模块，支持将状态、任务的数据属性与场景中的其他对象（如Actor组件、Material参数）进行双向绑定，实现自动化控制。

## 使用场景

-   你正在构建一个虚拟制片场景，需要精确控制一组灯光、烟雾和音效按时间线顺序或特定条件触发 → 用 `SceneState` 定义一个状态机，每个状态代表一个场景阶段，任务用于控制各个子系统。
-   你需要在动态设计节目中，让多个3D对象的动画和特效严格同步，并基于用户交互或事件切换到不同模式 → 使用 `SceneState` 的事件处理器（Event Handlers）和转换条件。
-   你希望为复杂的交互式装置（如主题公园设施）创建控制逻辑，逻辑涉及多步骤、等待和并行操作 → 利用 `SceneState` 的任务前提条件（Prerequisites）和状态嵌套（Nested State Machines）来构建清晰的逻辑树。
-   你需要在蓝图中实现复杂的、基于状态的行为，但希望避免蓝图图表过于庞大和难以调试 → 将逻辑拆分为多个 `USceneStateBlueprintableTask`，并在 `SceneState` 中组织它们。

## 蓝图用法

`SceneState` 提供了蓝图友好的类和接口，特别是通过 `USceneStateBlueprintableTask` 和 `USceneStateObject`。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Context Object` | 获取驱动此场景状态的外部对象（如拥有此组件的Actor） | `USceneStateObject` |
| `Get Event Stream` | 获取此场景状态对象的事件流，用于发送和接收自定义事件 | `USceneStateObject` |
| `Is Active` | 判断此场景状态对象是否有正在运行的根状态机 | `USceneStateObject` |
| `Finish Task` | 在蓝图任务中调用，标记当前任务已完成，允许状态机继续前进 | `USceneStateBlueprintableTask` |
| `Get Root State` | 在蓝图任务中，获取拥有此任务的场景状态对象实例 | `USceneStateBlueprintableTask` |
| `Receive Start` | **蓝图可实现事件**：当任务首次开始时被调用 | `USceneStateBlueprintableTask` |
| `Receive Tick` | **蓝图可实现事件**：当任务处于活动状态且可勾选时，每帧被调用 | `USceneStateBlueprintableTask` |
| `Receive Stop` | **蓝图可实现事件**：当任务结束（完成或被强制停止）时被调用 | `USceneStateBlueprintableTask` |

### 使用示例（蓝图描述）

1.  **创建蓝图任务**：创建一个继承自 `USceneStateBlueprintableTask` 的蓝图类。在事件图表中实现 `ReceiveStart`, `ReceiveTick` 和 `ReceiveStop` 事件。在 `ReceiveStart` 中可以开始播放一个时间轴或触发一个特效，在 `ReceiveTick` 中可以检测完成条件并调用 `FinishTask`。
2.  **在场景状态蓝图中使用**：在 `SceneState` 蓝图编辑器中，将上面创建的任务蓝图作为节点拖入状态内。通过可视化连线设置任务之间的前提条件。
3.  **添加转换与事件**：为状态添加“退出转换”，并连接到另一个状态。在转换线的节点上，可以设置条件，例如“等待所有任务完成”或“监听某个特定的事件被触发”。
4.  **触发场景状态**：在一个 Actor 的蓝图中，添加一个 `USceneStatePlayer` 组件。设置其 `SceneStateClass` 为你创建的场景状态蓝图类。然后，通过调用该玩家组件的 `Setup`, `Begin`, `Tick` 和 `End` 函数来控制整个场景状态的生命周期。

## C++ 用法

核心 API 集中在管理执行上下文（`FSceneStateExecutionContext`）、状态（`FSceneState`）和任务（`FSceneStateTask`）。

### 头文件引入

```cpp
#include "SceneState/SceneStateObject.h"
#include "SceneState/SceneStateExecutionContext.h"
#include "SceneState/Tasks/SceneStateTask.h"
#include "SceneState/SceneStateInstance.h"
```

### 基本用法

以下示例展示了如何在 C++ 中设置和查询一个 `FSceneStateExecutionContext`。

```cpp
// 假设已经有一个有效的 USceneStateObject* 指针: MySceneStateObject
FSceneStateExecutionContext Context;

// 设置执行上下文，关联到根场景状态对象
Context.Setup(MySceneStateObject);

// 查询当前上下文中的根对象
USceneStateObject* Root = Context.GetRootObject();

// 遍历指定状态中的所有任务
const FSceneState* SomeState = Context.GetState(0); // 通过索引获取状态
if (SomeState)
{
    Context.ForEachTask(*SomeState, [](const FSceneStateTask& Task, uint16 RelativeIndex)
    {
        UE_LOG(LogTemp, Log, TEXT("Task %d in state"), RelativeIndex);
        return UE::SceneState::EIterationResult::Continue;
    });
}

// 查找一个状态实例（如果状态正在运行）
FSceneStateInstance* StateInstance = Context.FindStateInstance(*SomeState);
if (StateInstance)
{
    UE::SceneState::EExecutionStatus Status = StateInstance->GetStatus();
    // ... 做一些逻辑判断
}

// 清理上下文
Context.Reset();
```

### 进阶用法

创建一个自定义的 C++ 任务。

```cpp
// MyCustomTask.h
#include "SceneState/Tasks/SceneStateTask.h"
#include "SceneState/Tasks/SceneStateTaskInstance.h"

USTRUCT(DisplayName="My Custom Task", Category="Custom")
struct FMyCustomTask : public FSceneStateTask
{
    GENERATED_BODY()

    using FInstanceDataType = FMyCustomTaskInstance;

protected:
    virtual void OnStart(const FSceneStateExecutionContext& InContext, FStructView InTaskInstance) const override;
    virtual void OnTick(const FSceneStateExecutionContext& InContext, FStructView InTaskInstance, float InDeltaSeconds) const override;
    virtual void OnStop(const FSceneStateExecutionContext& InContext, FStructView InTaskInstance, ESceneStateTaskStopReason InStopReason) const override;
};

// MyCustomTask.cpp
void FMyCustomTask::OnStart(const FSceneStateExecutionContext& InContext, FStructView InTaskInstance) const
{
    // 获取此任务的实例数据
    FMyCustomTaskInstance& MyInstance = InTaskInstance.Get<FMyCustomTaskInstance>();
    MyInstance.ElapsedTime = 0.f;
    UE_LOG(LogTemp, Log, TEXT("Custom task started!"));
}

void FMyCustomTask::OnTick(const FSceneStateExecutionContext& InContext, FStructView InTaskInstance, float InDeltaSeconds) const
{
    FMyCustomTaskInstance& MyInstance = InTaskInstance.Get<FMyCustomTaskInstance>();
    MyInstance.ElapsedTime += InDeltaSeconds;

    if (MyInstance.ElapsedTime >= 5.0f)
    {
        // 通知任务已完成
        Finish(InContext, InTaskInstance);
    }
}

void FMyCustomTask::OnStop(const FSceneStateExecutionContext& InContext, FStructView InTaskInstance, ESceneStateTaskStopReason InStopReason) const
{
    UE_LOG(LogTemp, Log, TEXT("Custom task stopped. Reason: %s"),
        InStopReason == ESceneStateTaskStopReason::Finished ? TEXT("Finished") : TEXT("Stopped by state"));
}
```

## Demo 示例

一个最小的、可编译的示例，展示如何创建一个简单的 C++ 任务并将其集成到场景状态中。

```cpp
// MyMinimalTask.h
#pragma once

#include "CoreMinimal.h"
#include "SceneState/Tasks/SceneStateTask.h"
#include "SceneState/Tasks/SceneStateTaskInstance.h"
#include "MyMinimalTask.generated.h"

USTRUCT(BlueprintType)
struct FMyMinimalTaskInstance : public FSceneStateTaskInstance
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadWrite, Category="Test")
    float Counter = 0.f;
};

USTRUCT(DisplayName="Minimal Counting Task", Category="Demo")
struct FMyMinimalTask : public FSceneStateTask
{
    GENERATED_BODY()

    using FInstanceDataType = FMyMinimalTaskInstance;

protected:
    virtual void OnStart(const FSceneStateExecutionContext& InContext, FStructView InTaskInstance) const override;
    virtual void OnTick(const FSceneStateExecutionContext& InContext, FStructView InTaskInstance, float InDeltaSeconds) const override;
};
```

```cpp
// MyMinimalTask.cpp
#include "MyMinimalTask.h"

void FMyMinimalTask::OnStart(const FSceneStateExecutionContext& InContext, FStructView InTaskInstance) const
{
    FMyMinimalTaskInstance& Instance = InTaskInstance.Get<FMyMinimalTaskInstance>();
    Instance.Counter = 0.f;
}

void FMyMinimalTask::OnTick(const FSceneStateExecutionContext& InContext, FStructView InTaskInstance, float InDeltaSeconds) const
{
    FMyMinimalTaskInstance& Instance = InTaskInstance.Get<FMyMinimalTaskInstance>();
    Instance.Counter += InDeltaSeconds;
    if (Instance.Counter > 2.0f)
    {
        Finish(InContext, InTaskInstance);
    }
}
```

## 模块依赖

此插件结构复杂，模块众多。对于核心 `SceneState` 模块的使用者，其依赖集中于引擎的数据和属性绑定系统。

| 模块 | 用途 |
|---|---|
| `StateTreeModule` | 状态机核心框架，`SceneState` 很可能基于或集成了它 |
| `PropertyBindingModule` | 属性绑定系统，用于任务、状态之间的数据通信 |
| `PropertyAccess` | 属性访问框架 |
| `GameplayTags` | 游戏玩法标签，常用于状态或事件的标识 |
| `CommonUI` | 用于编辑器中自定义UI |
| `UMG` | 用户界面框架 |

**注意**：由于该插件包含大量编辑器模块（如 `*Editor`, `*Graph`），在打包或作为运行时插件使用时，这些编辑器模块不会被包含。实际的运行时依赖会较少。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `6e111b5d` | Motion Design Scene State: fixed issues with bindings not checking for null event payload struct (op | 修复了绑定系统未检查事件载荷结构体是否为空的问题，提高了稳定性 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 `UE_LOG` 迁移至 `UE_LOGF`，遵循引擎新的日志规范 |
| 2025-08-27 | `94f96138` | Motion Design: Moved scene state and data link plugins out of experimental into virtualproduction | 插件从 `Experimental` 目录正式迁移到 `VirtualProduction` 目录，标志着其成为VP工作流的一部分 |

### 维护评价

`SceneState` 是一个**活跃维护中**的实验性插件。

-   **创建时间**：约1年前（2025年8月），相对较新。
-   **维护活跃度**：最近3个月仍有实质性的bug修复和代码维护，说明开发团队仍在积极使用和改进它。
-   **当前状态**：`.uplugin` 中 `IsBetaVersion=true`，表明它仍处于测试阶段，API和功能可能发生变化。源码中存在 `UE_DEPRECATED(5.8, ...)` 标记，说明其API正在从旧版本演进。
-   **已知限制**：作为实验性功能，其文档和社区支持可能有限。内部API（标记为 `UE_INTERNAL`）不保证稳定性。
-   **推荐使用**：**仅推荐**给深度参与虚拟制作或动态设计项目、且有能力应对实验性API变化的团队。对于通用游戏状态机需求，建议使用更成熟、稳定的 `StateTree` 或 `GAS` 等方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/SceneState)
- 官方文档：无
- 测试用例：无（源码中未发现独立的测试文件目录）