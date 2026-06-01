# State Tree

> General purpose hierarchical state machine

| 属性 | 值 |
|---|---|
| 中文名 | 状态树 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（资产） |
| 模块 | `StateTreeDeveloper` (Runtime), `StateTreeEditorModule` (Runtime), `StateTreeModule` (Runtime), `StateTreeTestSuite` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-09-28 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/StateTree) | |

## 用途

StateTree 是 Unreal Engine 中一个通用、数据驱动的分层状态机（Hierarchical State Machine, HSM）框架。它旨在解决复杂游戏逻辑和 AI 行为管理的难题，是传统状态树和行为树的现代化替代方案。

与蓝图状态机相比，StateTree 提供了更清晰的层次结构、更丰富的数据绑定机制，并支持在编辑器中可视化地设计和调试。它不仅仅是一个状态管理器，还集成了任务（Tasks）、条件（Conditions）和评估器（Evaluators），使其能够表达复杂的行为逻辑和游戏规则。

**为什么存在？**
1.  **统一行为系统**：为 AI 行为、游戏任务、动画状态、玩家交互等多种场景提供一个通用的、可复用的逻辑框架。
2.  **数据驱动**：状态、任务和条件的逻辑可以通过资产（UStateTreeAsset）在编辑器中配置，而非完全依赖硬编码，提高了策划和设计师的迭代效率。
3.  **强大的数据绑定**：支持属性绑定、外部数据集成和输出绑定，便于在状态、任务和游戏系统之间传递数据。
4.  **可扩展性**：通过自定义任务、条件和评估器，可以轻松扩展其功能以适应项目特定需求。

## 使用场景

-   **复杂的 AI 行为管理**：你需要一个清晰的、可调试的 AI 系统来控制 NPC 的巡逻、搜索、战斗、交互等多种行为。StateTree 的层次结构允许将高级目标（如“战斗”）分解为子状态（如“寻找掩体”、“开火”、“治疗”）。
-   **游戏任务与剧情系统**：管理复杂的、多阶段的游戏任务流程，包括条件检查、分支剧情、计时器和与游戏系统的交互。
-   **动画状态机的增强**：驱动复杂的角色动画逻辑，特别是当动画状态需要与游戏玩法数据（如速度、方向、武器状态）深度绑定时。
-   **自定义游戏机制**：实现解谜、驾驶载具、建造系统等任何需要“状态”管理的玩法机制。

## 蓝图用法

StateTree 的主要交互通常通过其资产和组件进行，但暴露的 API 允许在蓝图中进行更深层的控制。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `StartLogic` / `RestartLogic` | 启动或重启状态树逻辑 | `UStateTreeComponent` |
| `StopLogic` | 停止状态树逻辑 | `UStateTreeComponent` |
| `SendStateTreeEvent` | 向运行中的状态树发送一个事件，触发状态转换 | `UStateTreeComponent` |
| `SetExternalData` | 设置状态树执行上下文需要的外部数据（如角色、控制器引用） | `UStateTreeComponent` |
| `GetActiveStateNames` | 获取当前激活的状态路径名称（用于调试） | `UStateTreeComponent` |
| `GetStateTreeRunStatus` | 获取状态树当前的运行状态（Running, Succeeded, Failed） | `UStateTreeComponent` |

### 使用示例（蓝图描述）

1.  **挂载与启动**：在你的 AI 蓝图角色上，添加 `UStateTreeComponent`。在 BeginPlay 或其他事件中，调用 `StartLogic`。
2.  **提供外部数据**：状态树中的任务（如移动到目标）需要访问角色的导航信息。通过 `SetExternalData` 节点，将 `ACharacter`、`UAIPerceptionComponent` 等对象传递给状态树，供其内部任务使用。
3.  **驱动状态转换**：当游戏世界中发生特定事件（如玩家被发现、物品被拾取）时，调用 `SendStateTreeEvent` 节点，将一个 `FGameplayTag` 事件发送给状态树，以触发向“警戒”、“拾取物品”等状态的转换。
4.  **监控状态**：使用 `GetActiveStateNames` 在 HUD 或调试器上显示 AI 当前所处的状态层次，便于调试。

## C++ 用法

### 头文件引入

```cpp
#include "StateTreeModule.h"
#include "StateTreeExecutionContext.h"
#include "StateTreeTaskBase.h"
#include "StateTreeEvaluatorBase.h"
#include "StateTreeConditionCommonBase.h"
```

### 基本用法（从测试用例提取）

以下是创建一个最简单的自定义任务（Task）的模式，它会在进入状态时记录日志。这展示了 StateTree 任务的核心结构。
（来源文件：`Private/StateTreeTestTypes.h` 中的 `FTestTask_B`）

```cpp
// 1. 定义任务的实例数据结构，包含任务运行时需要的参数
USTRUCT()
struct FMyTaskInstanceData
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, Category = "Input")
    float Speed = 100.0f;
};

// 2. 定义任务本身，继承自 FStateTreeTaskBase
USTRUCT()
struct FMyTask_MoveForward : public FStateTreeTaskBase
{
    GENERATED_BODY()

    // 声明实例数据类型
    using FInstanceDataType = FMyTaskInstanceData;

    // 必须重写此函数，返回实例数据类型的 UStruct 指针
    virtual const UStruct* GetInstanceDataType() const override { return FInstanceDataType::StaticStruct(); }

    // 当状态进入时调用
    virtual EStateTreeRunStatus EnterState(FStateTreeExecutionContext& Context, const FStateTreeTransitionResult& Transition) const override
    {
        // 从上下文获取当前任务的实例数据
        const FInstanceDataType& InstanceData = Context.GetInstanceData(*this);

        // 这里可以添加开始向前移动的逻辑，例如调用角色移动组件
        // Context.GetOwner() 可以获取拥有此状态树的对象（如角色）
        UE_LOG(LogStateTree, Log, TEXT("开始向前移动，速度: %.1f"), InstanceData.Speed);

        // 返回运行状态，表示任务正在执行
        return EStateTreeRunStatus::Running;
    }

    // 每帧或定期调用，用于更新任务
    virtual EStateTreeRunStatus Tick(FStateTreeExecutionContext& Context, const float DeltaTime) const override
    {
        // 执行移动逻辑...
        // 可以在此处检查移动是否完成，并返回 Succeeded 或 Failed
        return EStateTreeRunStatus::Running;
    }

    // 当状态退出时调用（无论是正常结束还是被中断）
    virtual void ExitState(FStateTreeExecutionContext& Context, const FStateTreeTransitionResult& Transition) const override
    {
        // 停止移动，清理资源
    }
};
```

### 进阶用法（使用外部数据和自定义评估器）

评估器（Evaluator）可以持续评估条件并输出数据，供其他状态节点使用。以下是自定义评估器的基本结构。
（来源文件：`Private/StateTreeTestTypes.h` 中的 `FTestEval_A` 和 `FTestEval_Custom`）

```cpp
// 评估器的实例数据
USTRUCT()
struct FMyEvaluatorInstanceData
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, Category = "Parameter")
    float CheckInterval = 0.5f;
};

USTRUCT()
struct FMyEvaluator_ProximityCheck : public FStateTreeEvaluatorBase
{
    GENERATED_BODY()

    using FInstanceDataType = FMyEvaluatorInstanceData;

    virtual const UStruct* GetInstanceDataType() const override { return FInstanceDataType::StaticStruct(); }

    // 链接阶段：声明需要链接的外部数据（如角色引用）
    virtual bool Link(FStateTreeLinker& Linker) override
    {
        // 假设我们有一个外部数据句柄用于访问角色
        // Linker.LinkExternalData(CharacterHandle);
        return true;
    }

    // 当状态树（或所在子树）开始时调用
    virtual void TreeStart(FStateTreeExecutionContext& Context) const override
    {
        // 初始化逻辑，例如启动定时器
    }

    // 定期调用，用于评估条件并更新输出
    virtual void Tick(FStateTreeExecutionContext& Context, const float DeltaTime) const override
    {
        // 在这里执行距离检测、动画状态检查等逻辑
        // 可以通过 Context.GetExternalData(...) 获取链接的数据
        // 结果可以写入到实例数据或绑定到输出属性中，供条件（Condition）或任务（Task）使用
    }

    // 当状态树（或所在子树）停止时调用
    virtual void TreeStop(FStateTreeExecutionContext& Context) const override
    {
        // 清理逻辑
    }
};
```

**在 `UStateTreeComponent` 中使用**：
```cpp
// 在角色类中
void AMyCharacter::BeginPlay()
{
    Super::BeginPlay();

    if (StateTreeComponent)
    {
        // 设置外部数据，例如将自身角色传递给状态树
        FStateTreeExternalDataDesc CharacterDesc(ACharacter::StaticClass());
        StateTreeComponent->SetContextData(CharacterDesc, this);

        // 启动逻辑
        StateTreeComponent->StartLogic();
    }
}
```

## Demo 示例

一个完整的、可编译的最小自定义任务示例。

**MyStateTreeTask.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "StateTreeTaskBase.h"
#include "MyStateTreeTask.generated.h"

USTRUCT()
struct FMyLogTaskInstanceData
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, Category = "Input")
    FName LogLabel = "Default";

    UPROPERTY(EditAnywhere, Category = "Input")
    FString LogMessage = "Hello from StateTree!";
};

USTRUCT()
struct FMyLogTask : public FStateTreeTaskBase
{
    GENERATED_BODY()

    using FInstanceDataType = FMyLogTaskInstanceData;

    virtual const UStruct* GetInstanceDataType() const override { return FInstanceDataType::StaticStruct(); }

    virtual EStateTreeRunStatus EnterState(FStateTreeExecutionContext& Context, const FStateTreeTransitionResult& Transition) const override
    {
        const FInstanceDataType& Data = Context.GetInstanceData(*this);
        UE_LOG(LogTemp, Warning, TEXT("[%s] %s"), *Data.LogLabel.ToString(), *Data.LogMessage);
        // 此任务立即完成
        return EStateTreeRunStatus::Succeeded;
    }
};
```

**MyStateTreeTask.cpp**
```cpp
// 此文件可能为空，因为所有逻辑都在头文件中。根据模块设置，你可能需要在此处包含头文件。
#include "MyStateTreeTask.h"
```

**如何使用**：
1.  将上述头文件和源文件添加到你的项目模块中。
2.  在 StateTree 编辑器中，创建一个新的状态树资产。
3.  在状态节点的“任务”部分，搜索并添加 `FMyLogTask`。
4.  在任务细节面板中，设置 `LogLabel` 和 `LogMessage`。
5.  运行游戏，当状态进入该节点时，控制台将打印出你的日志。

## 模块依赖

要使用 StateTree 的核心功能，你的模块通常需要依赖 `StateTreeModule`。

| 模块 | 用途 |
|---|---|
| `StateTreeModule` | StateTree 运行时核心，包含执行上下文、基础任务、条件等。这是使用者主要需要依赖的模块。 |
| `AIModule` | 如果你的 StateTree 用于 AI 行为，可能需要依赖此模块以使用 AI 相关的功能（如 `UAIPerceptionComponent`）。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `2c528ff3` | [StateTree] Fix invalid memory access. | 修复无效内存访问问题。 |
| 2026-05-14 | `fbc95955` | [StateTree] Fix bas memory access in unittest | 修复单元测试中的内存访问错误。 |
| 2026-05-14 | `4efd5cdb` | [StateTree] Compile pending StateTree assets in the editor before linking. This prevents link failure | 在链接前预编译待处理的StateTree资产，防止链接失败。 |
| 2026-05-13 | `541c19e0` | Extend property binding compatibility to support task completion bindings | 扩展属性绑定兼容性，支持任务完成绑定。 |
| 2026-05-12 | `ea25bb3b` | [StateTree] Copy-paste transition also copies the bindings. Fix the UI that displays the list of states | 复制粘贴转换时同时复制绑定关系，修复显示状态列表的UI。 |

### 维护评价

StateTree 插件自 2021 年创建以来，经历了从实验性到正式功能的演变。从近期的 git 历史来看（截至 2026 年 5 月），该插件**仍在被积极维护**。

**优点**：
1.  **活跃开发**：近期提交集中在 bug 修复（如内存访问问题）、功能增强（如扩展绑定支持）和工作流改进（如资产预编译），表明 Epic Games 团队仍在持续投入。
2.  **核心功能稳定**：作为“Gameplay”分类下的通用系统，其设计目标明确，API 已趋于成熟。
3.  **完善的测试套件**：拥有独立的 `StateTreeTestSuite` 模块，保证了代码质量和回归测试。

**潜在考虑**：
-   **默认禁用**：插件默认未启用 (`EnabledByDefault=false`)，需要开发者手动在项目设置中启用，表明它可能被视为一个“可选”但强大的高级功能。
-   **学习曲线**：作为一个完整的 HSM 框架，其概念（状态、任务、条件、评估器、数据绑定）和工具链有一定学习成本。

**推荐使用**：如果你正在开发中等或以上复杂度的游戏逻辑（尤其是 AI），并且需要比蓝图状态机更强大、更可维护的解决方案，**强烈推荐学习和使用 StateTree**。它代表了 UE 在游戏逻辑系统方面的现代化方向。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/StateTree)
-   [官方文档](https://docs.unrealengine.com/5.0/en-US/state-tree-in-unreal-engine/) (无 .uplugin DocsURL，此为引擎文档站相关页面)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/StateTree/Source/StateTreeTestSuite)