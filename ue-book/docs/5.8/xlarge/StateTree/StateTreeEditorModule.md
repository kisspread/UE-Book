# StateTree

> General purpose hierarchical state machine

| 属性 | 值 |
|---|---|
| 中文名 | 状态树 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `StateTreeModule` (Runtime), `StateTreeDeveloper` (Runtime), `StateTreeEditorModule` (Runtime), `StateTreeTestSuite` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-09-28 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/StateTree) | |

## 用途

StateTree 插件提供了一个通用、灵活的分层状态机（Hierarchical State Machine，HSM）框架，旨在解决复杂游戏逻辑（如 AI 行为、玩家交互、UI 流程）的状态管理问题。它超越了简单的有限状态机，允许状态拥有子状态，并支持复杂的条件、任务、评估器以及状态间的属性绑定。

该插件的核心价值在于：
1.  **结构化逻辑**：将复杂的行为分解为清晰、可管理的状态和转换。
2.  **数据驱动**：状态、任务和条件通过蓝图或 C++ 定义，易于配置和扩展。
3.  **强大的编辑器集成**：提供可视化的状态树编辑器，支持拖拽、编译、调试。
4.  **属性绑定**：允许在状态、任务和评估器之间轻松地传递和同步数据。
5.  **内置调试**：集成 Rewind Debugger，支持实时跟踪状态机的执行流程。

## 使用场景

*   **AI 角色行为**：为 NPC 创建复杂的行为树，包含巡逻、搜索、攻击、逃跑等多种状态，并根据感知、血量等条件进行切换。
*   **游戏内 UI 流程**：管理菜单系统的导航流程，如主菜单、设置、子菜单之间的状态转换和动画。
*   **玩家角色状态**：管理玩家角色的不同状态，如正常、冲刺、攀爬、受伤，并处理不同状态下的输入和动画。
*   **任务/任务系统**：定义任务的步骤、目标和完成条件，每个步骤可以视为一个状态。
*   **技能/能力系统**：管理技能的施放流程，包括蓄力、释放、冷却等阶段。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create State Tree` | 创建一个空的状态树资产实例。 | `UBlueprintFunctionLibrary` |
| `Compile State Tree` | 手动编译一个状态树资产，使其可以运行。 | `UBlueprintFunctionLibrary` |
| `Set State` | 在运行时强制设置状态树当前应进入的状态（通常用于调试或特定事件）。 | `UStateTreeComponent` |
| `Set Enabled` | 启用或禁用一个状态树组件，控制其是否处理逻辑。 | `UStateTreeComponent` |
| `Get State Tree Instance` | 获取一个状态树组件的实例数据，用于查询当前状态等信息。 | `UStateTreeComponent` |

### 使用示例

1.  **在角色蓝图中添加状态机**：
    *   向角色蓝图添加一个 `UStateTreeComponent`。
    *   在组件的 `State Tree` 属性中，选择或创建一个 `UStateTree` 资产。
    *   使用 `Event Graph` 中的节点（如 `Set Enabled`）控制状态机的激活。
2.  **创建和配置状态树资产**：
    *   在内容浏览器中右键，选择 `Gameplay > State Tree` 创建资产。
    *   打开资产，进入可视化编辑器。
    *   添加状态（State）、任务（Task）和条件（Condition）。
    *   使用拖拽创建状态间的转换（Transition），并设置触发条件。
3.  **使用属性绑定传递数据**：
    *   在状态树编辑器中，选择一个任务节点（如“播放动画”任务）。
    *   在详细面板中，将任务的属性（如“动画序列”）与另一个节点（如上下文节点）的属性绑定。
    *   运行时，数据将自动同步。

## C++ 用法

### 头文件引入

```cpp
#include "StateTreeModule.h"
#include "StateTreeComponent.h"
#include "StateTreeAsset.h"
```

### 基本用法

从状态树组件的运行和状态查询开始。

```cpp
// 假设在角色类中拥有一个 UStateTreeComponent 指针
UStateTreeComponent* StateTreeComp = FindComponentByClass<UStateTreeComponent>();
if (StateTreeComp)
{
    // 启用状态树
    StateTreeComp->SetEnabled(true);

    // 获取状态树实例，查询信息
    if (const FStateTreeInstanceData* InstanceData = StateTreeComp->GetStateTreeInstanceData())
    {
        // 可以在这里查询当前活跃状态等信息
        // 具体查询方法取决于你的状态树结构
    }
}
```

### 进阶用法

自定义一个简单的任务节点。

```cpp
// MyCustomTask.h
#include "StateTreeTaskBase.h"
#include "MyCustomTask.generated.h"

USTRUCT()
struct FMyCustomTaskInstanceData
{
    GENERATED_BODY()

    // 任务的实例数据，可以被属性绑定访问
    UPROPERTY(EditAnywhere, Category = "Input")
    float SomeValue = 1.0f;
};

USTRUCT(meta=(DisplayName="My Custom Task", Category="Custom"))
struct FMyCustomTask : public FStateTreeTaskBase
{
    GENERATED_BODY()

    using FInstanceDataType = FMyCustomTaskInstanceData;

    virtual EStateTreeRunStatus EnterState(FStateTreeExecutionContext& Context, const FStateTreeTransitionResult& Transition) const override;
    virtual void ExitState(FStateTreeExecutionContext& Context, const FStateTreeTransitionResult& Transition) const override;
};

// MyCustomTask.cpp
EStateTreeRunStatus FMyCustomTask::EnterState(FStateTreeExecutionContext& Context, const FStateTreeTransitionResult& Transition) const
{
    // 从上下文中获取实例数据
    FMyCustomTaskInstanceData& InstanceData = Context.GetInstanceData(*this);
    
    UE_LOG(LogTemp, Log, TEXT("MyCustomTask Entered! SomeValue: %f"), InstanceData.SomeValue);

    // 任务应该立即完成，还是持续运行
    return EStateTreeRunStatus::Running; // 或者 EStateTreeRunStatus::Succeeded
}

void FMyCustomTask::ExitState(FStateTreeExecutionContext& Context, const FStateTreeTransitionResult& Transition) const
{
    UE_LOG(LogTemp, Log, TEXT("MyCustomTask Exited."));
}
```

## Demo 示例

一个最小的自定义任务节点示例。

```cpp
// SimpleLogTask.h
#pragma once

#include "CoreMinimal.h"
#include "StateTreeTaskBase.h"
#include "SimpleLogTask.generated.h"

USTRUCT()
struct FSimpleLogTaskInstanceData
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, Category = "Parameter")
    FText LogMessage;
};

USTRUCT(meta=(DisplayName="Simple Log Task", Category="Debug"))
struct FSimpleLogTask : public FStateTreeTaskBase
{
    GENERATED_BODY()

    using FInstanceDataType = FSimpleLogTaskInstanceData;

    virtual EStateTreeRunStatus EnterState(FStateTreeExecutionContext& Context, const FStateTreeTransitionResult& Transition) const override
    {
        const FSimpleLogTaskInstanceData& Data = Context.GetInstanceData(*this);
        UE_LOG(LogTemp, Log, TEXT("StateTree Log: %s"), *Data.LogMessage.ToString());
        return EStateTreeRunStatus::Succeeded;
    }

    virtual void ExitState(FStateTreeExecutionContext& Context, const FStateTreeTransitionResult& Transition) const override
    {
        UE_LOG(LogTemp, Log, TEXT("SimpleLogTask finished."));
    }
};
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `2c528ff3` | [StateTree] Fix invalid memory access. | 修复无效内存访问的错误。 |
| 2026-05-14 | `fbc95955` | [StateTree] Fix bas memory access in unittest | 修复单元测试中的内存访问错误。 |
| 2026-05-14 | `4efd5cdb` | [StateTree] Compile pending StateTree assets in the editor before linking. This prevents link failur | 在编辑器中链接前编译待处理的状态树资产，防止链接失败。 |
| 2026-05-13 | `541c19e0` | Extend property binding compatibility to support task completion bindings | 扩展属性绑定兼容性以支持任务完成绑定。 |
| 2026-05-12 | `ea25bb3b` | [StateTree] Copy-paste transition also copies the bindings. Fix the UI that displays the list of sta | 复制粘贴转换时同时复制绑定。修复显示状态列表的UI。 |

### 维护评价

*   **活跃维护**：最近一次提交在2026年5月，近期有频繁的 bug 修复和功能增强（如任务完成绑定支持）。
*   **成熟度高**：作为 UE5 的核心游戏框架组件，经过了多年的迭代和打磨，API 稳定，功能完整。
*   **社区广泛**：是 UE5 中管理复杂游戏逻辑的主流方案之一，有大量文档、教程和社区讨论。
*   **推荐使用**：对于中等及以上复杂度的游戏逻辑（特别是AI和交互系统），StateTree 是一个强大且推荐的选择。尽管默认未启用，但其稳定性和功能使其成为项目的可靠基础。

## 相关链接

*   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/StateTree)
*   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/StateTree/Source/StateTreeTestSuite)