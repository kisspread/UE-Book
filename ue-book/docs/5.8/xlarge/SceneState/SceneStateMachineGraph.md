# Motion Design Scene State

> （无描述）

| 属性 | 值 |
|---|---|
| 中文名 | 场景状态机图 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（状态机图编辑器资产） |
| 模块 | `SceneState` (Runtime), `SceneStateBinding` (Runtime), `SceneStateBlueprint` (Runtime), `SceneStateBlueprintEditor` (Runtime), `SceneStateEditor` (Runtime), `SceneStateEvent` (Runtime), `SceneStateEventEditor` (Runtime), `SceneStateEventGraph` (Runtime), `SceneStateGameplay` (Runtime), `SceneStateGameplayEditor` (Runtime), `SceneStateMachineEditor` (Runtime), `SceneStateMachineGraph` (Runtime), `SceneStateTasks` (Runtime), `SceneStateTransitionGraph` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/SceneState) | |

## 用途

Motion Design Scene State 插件是一个实验性的、标记为 Beta 的状态机编辑系统，专为虚拟制作（Virtual Production）和运动设计（Motion Design）场景构建。它提供了一套完整的**状态机图编辑器框架**，允许开发者通过可视化的节点图来设计和管理场景中物体的状态、行为和交互逻辑。其核心是 `SceneStateMachineGraph` 模块，它定义了状态机图的数据结构、节点类型（状态、任务、转场、导管等）、连接规则以及对应的蓝图图编辑器 Schema。这个插件旨在将复杂的状态逻辑与视觉呈现分离，为实现可配置、可交互的虚拟场景（如展览、演出、预演）提供底层支持。

## 使用场景

-   **虚拟制作（VP）**：你需要在 Unreal 的虚拟场景中控制灯光、道具、摄像机或其他 Actor 按照预设的剧本（Script）或条件进行状态切换和交互。
-   **运动设计（Motion Design）**：你在制作动态的视觉内容或交互式体验，需要一个系统来管理动画、效果和用户输入的响应流程。
-   **创建可配置的交互逻辑**：你需要为美术师或设计师提供一个非代码的方式，在编辑器中拖拽连接节点来定义复杂的状态流转逻辑，而无需编写 C++ 或蓝图。
-   **扩展蓝图编辑器功能**：你正在开发一个需要自定义节点图编辑器的插件或功能，可以基于此模块提供的架构进行扩展。

## 蓝图用法

此插件的核心功能主要体现在编辑器中的节点图操作，直接通过蓝图暴露的、用于运行时的节点较少。以下是从源码中提取的主要蓝图可用 API：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetEntryNode` | 获取状态机图的入口节点。 | `USceneStateMachineGraph` |
| `GetStateNode` | 从入口节点获取第一个连接的状态节点。 | `USceneStateMachineEntryNode` |
| `GatherTransitions` | 收集当前状态节点的所有转场节点，并可按优先级排序。 | `USceneStateMachineNode` |
| `GetSourceNode` / `GetTargetNode` | 获取转场节点的源状态和目标状态。 | `USceneStateMachineTransitionNode` |
| `CreateConnectionWithTransition` | 在图 Schema 中，通过参数创建一个新的转场连接。 | `USceneStateMachineGraphSchema` |
| `FindConnectedStateNode` | 静态函数，尝试找到连接到指定任务节点的状态节点。 | `USceneStateMachineGraphSchema` |
| `OnParametersChanged` | 当转场节点或状态节点的参数发生变化时触发的广播委托。 | `USceneStateMachineTransitionNode`, `USceneStateMachineStateNode` |

### 使用示例（蓝图描述）

在蓝图中，你可能通过获取当前正在编辑的 `USceneStateMachineGraph` 对象，然后调用 `GetEntryNode` 和 `GetStateNode` 来定位起始状态。若要创建新的节点连接，通常需要通过 `USceneStateMachineGraphSchema` 的上下文菜单或拖拽操作，而不是直接在运行时蓝图中调用。对于运行时，主要关注状态机实例的驱动和事件处理，这属于 `SceneStateGameplay` 等模块的范畴。

## C++ 用法

### 头文件引入

```cpp
#include "SceneStateMachineGraph.h"
#include "SceneStateMachineGraphSchema.h"
#include "Nodes/SceneStateMachineNode.h"
#include "Nodes/SceneStateMachineStateNode.h"
#include "Nodes/SceneStateMachineTransitionNode.h"
```

### 基本用法

定义自定义状态机节点类型（继承自 `USceneStateMachineNode`）。

**来源：** `Source/SceneStateMachineGraph/Public/Nodes/SceneStateMachineNode.h`

```cpp
// MyCustomStateNode.h
#pragma once
#include "Nodes/SceneStateMachineNode.h"
#include "MyCustomStateNode.generated.h"

UCLASS(MinimalAPI)
class UMyCustomStateNode : public USceneStateMachineNode
{
    GENERATED_BODY()
public:
    UMyCustomStateNode();

    // 重写以创建自定义的绑定图（例如，用于定义状态内的行为）
    virtual UEdGraph* CreateBoundGraphInternal() override;

    // 重写以分配自定义的引脚
    virtual void AllocateDefaultPins() override;

    // 可以添加自定义属性，这些属性可以在节点细节面板中编辑
    UPROPERTY(EditAnywhere, Category = "Custom")
    FText CustomStateDescription;
};
```

### 进阶用法

扩展状态机图 Schema 以支持新的连接类型或操作。

**来源：** `Source/SceneStateMachineGraph/Public/SceneStateMachineGraphSchema.h`

```cpp
// MyStateMachineGraphSchema.h
#pragma once
#include "SceneStateMachineGraphSchema.h"
#include "MyStateMachineGraphSchema.generated.h"

UCLASS(MinimalAPI)
class UMyStateMachineGraphSchema : public USceneStateMachineGraphSchema
{
    GENERATED_BODY()
public:
    // 重写以添加自定义的右键上下文菜单项
    virtual void GetContextMenuActions(UToolMenu* InMenu, UGraphNodeContextMenuContext* InContext) const override;

    // 重写以定义自定义的节点连接规则
    virtual const FPinConnectionResponse CanCreateConnection(const UEdGraphPin* InSourcePin, const UEdGraphPin* InTargetPin) const override;
};
```

## Demo 示例

一个最小的自定义状态机节点定义示例。

**MyMinimalStateNode.h**
```cpp
#pragma once
#include "Nodes/SceneStateMachineNode.h"
#include "MyMinimalStateNode.generated.h"

UCLASS(MinimalAPI)
class UMyMinimalStateNode : public USceneStateMachineNode
{
    GENERATED_BODY()

public:
    UMyMinimalStateNode();

    virtual void AllocateDefaultPins() override
    {
        // 创建输入和输出引脚（基类通常已处理，这里用于演示）
        CreatePin(EGPD_Input, PN_In, TEXT("In"));
        CreatePin(EGPD_Output, PN_Out, TEXT("Out"));
    }

    virtual FText GetNodeTitle(ENodeTitleType::Type InTitleType) const override
    {
        return NSLOCTEXT("MyMinimalStateNode", "NodeTitle", "Minimal Custom State");
    }
};
```
**注意**：要将此节点集成到编辑器图中，还需要在对应的 `UEdGraphSchema`（如 `USceneStateMachineGraphSchema`）的 `GetGraphContextActions` 中注册相应的 `FEdGraphSchemaAction`（例如 `FStateMachineAction_NewNode`），以便用户能在右键菜单中找到并创建它。

## 模块依赖

从模块命名和代码结构分析，`SceneStateMachineGraph` 模块主要用于编辑器扩展，其核心依赖是状态机的数据和蓝图模块。

| 模块 | 用途 |
|---|---|
| `SceneState` | 核心状态机运行时数据结构和逻辑。 |
| `SceneStateBlueprint` | 与蓝图资产集成，支持蓝图可定义的任务等。 |
| `BlueprintGraph`, `KismetCompiler` | UE 蓝图图编辑器和编译器框架，用于构建节点图编辑器。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口相关重构，优化客户端关联/解除关联通知。 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回滚了某个提交。 |
| 2026-05-14 | `9ede83f2` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 与 `cfb610df` 相同，是视口重构的一部分。 |
| 2026-04-17 | `6e111b5d` | Motion Design Scene State: fixed issues with bindings not checking for null event payload struct (op | 修复了事件绑定中未检查空有效载荷结构体的问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF。 |

### 维护评价

-   **创建时间**：创建于 2025 年 8 月，非常新的插件。
-   **更新频率**：最近的更新集中在 2026 年 4-5 月，间隔不到一个月，显示处于**活跃开发阶段**。
-   **更新内容**：近期提交以修复错误（如空指针检查）和内部重构（日志宏、视口通知）为主，属于持续维护和优化。
-   **状态**：标记为**实验性（Beta）**，这意味着 API 可能不稳定，功能可能不完整，但正在积极迭代。
-   **推荐度**：由于其专注于虚拟制作/运动设计这一细分领域，且处于实验阶段，**推荐相关领域的开发者关注和试用**，但不建议将其用于需要高度稳定性的生产核心项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/SceneState)
- [官方文档]() (无)
- [测试用例]() (未在提供的路径下发现标准测试文件，可能位于其他位置或为内部测试)