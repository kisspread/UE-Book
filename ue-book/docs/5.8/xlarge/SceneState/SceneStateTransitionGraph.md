# Motion Design Scene State

> 

| 属性 | 值 |
|---|---|
| 中文名 | 运动设计场景状态 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（资产） |
| 模块 | `SceneState` (Runtime), `SceneStateBinding` (Runtime), `SceneStateBlueprint` (Runtime), `SceneStateBlueprintEditor` (Runtime), `SceneStateEditor` (Runtime), `SceneStateEvent` (Runtime), `SceneStateEventEditor` (Runtime), `SceneStateEventGraph` (Runtime), `SceneStateGameplay` (Runtime), `SceneStateGameplayEditor` (Runtime), `SceneStateMachineEditor` (Runtime), `SceneStateMachineGraph` (Runtime), `SceneStateTasks` (Runtime), `SceneStateTransitionGraph` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/SceneState) | |

## 用途

**Motion Design Scene State** 是一个面向虚拟制作（Virtual Production）的场景状态管理系统。它提供了一套完整的状态机框架和可视化编辑工具，用于管理场景中复杂对象或系统的状态转换逻辑。该插件解决的核心问题是：在虚拟演播室、实时光效控制或动态场景编排中，需要根据时间、用户交互或事件信号，精确控制场景元素（如灯光、动画、特效、摄像机行为等）的激活、切换和结束。通过图形化的状态机编辑器，设计师和开发者可以直观地定义状态、转换条件和事件响应，从而构建出可预测、可维护的动态场景行为逻辑。

## 使用场景

- **虚拟演播室控制**：你需要根据导演的实时指令（如通过触控板或自动化序列）切换虚拟场景的灯光氛围、背景动画或AR元素，使用此插件来预定义和触发这些状态。
- **交互式装置艺术**：你正在开发一个互动艺术装置，需要根据观众的接近或触摸触发一系列视觉和音效变化，使用状态机管理这些交互序列。
- **电影预演与动态分镜**：在Previs中，你需要快速编排镜头切换、角色走位和特效触发，用可视化的状态机来串联这些事件。
- **游戏内过场动画编排**：虽然名为“Motion Design”，但其状态机逻辑也适用于游戏内需要精确控制的过场动画或环境事件。

## 蓝图用法

此插件（特指 `SceneStateTransitionGraph` 模块）主要提供编辑器扩展和图形化编辑功能，不直接暴露运行时蓝图节点。状态机的创建、编辑和调试主要在UE编辑器的专用图表编辑器中完成。

### 核心编辑器功能

| 功能 | 说明 | 相关类 |
|---|---|---|
| 状态转换图表 | 可视化编辑状态之间转换条件的图表 | `USceneStateTransitionGraph` |
| 导管图表 | 用于组织复杂转换逻辑的中间图表 | `USceneStateConduitGraph` |
| 转换结果节点 | 图表中代表转换最终结果的节点 | `USceneStateTransitionResultNode` |

**使用示例（编辑器操作描述）**：
1. 在内容浏览器中右键创建一个新的“Scene State Transition Graph”资产。
2. 双击打开该资产，进入自定义的状态转换图表编辑器。
3. 从节点面板拖入所需的条件判断、变量读取等节点，连线至“Transition Result”节点以定义转换逻辑。
4. 将定义好的图表资产关联到具体的场景状态机中，作为某个状态之间的转换条件。

## C++ 用法

### 头文件引入

使用本模块提供的图表和节点类时，需要包含对应的头文件：

```cpp
#include "SceneStateTransitionGraph.h"
#include "SceneStateConduitGraph.h"
#include "Nodes/SceneStateTransitionResultNode.h"
#include "ISceneStateTransitionGraphProvider.h"
```

### 基本用法

以下代码示例展示了如何以编程方式创建和检查一个场景状态转换图表（通常在编辑器工具或自定义编辑器扩展中使用）。

```cpp
// 示例：创建一个新的状态转换图（来源：推测自类结构）
USceneStateTransitionGraph* TransitionGraph = NewObject<USceneStateTransitionGraph>(GetTransientPackage(), TEXT("MyTransitionGraph"));
if (TransitionGraph)
{
    // 创建并关联一个结果节点
    TransitionGraph->ResultNode = NewObject<USceneStateTransitionResultNode>(TransitionGraph);
    // 设置结果属性...
    TransitionGraph->ResultNode->Result.bIsEnabled = true;
}
```

### 进阶用法：实现图表提供者接口

要让你自己的 `UEdGraphNode` 子类能提供并管理一个“Scene State Transition Graph”，需要实现 `ISceneStateTransitionGraphProvider` 接口。

```cpp
#include "ISceneStateTransitionGraphProvider.h"

UCLASS()
class UMyCustomStateNode : public UEdGraphNode, public ISceneStateTransitionGraphProvider
{
    GENERATED_BODY()

    // ISceneStateTransitionGraphProvider 接口实现
    virtual FText GetTitle() const override
    {
        return NSLOCTEXT("MyNode", "Title", "My Custom State");
    }

    virtual bool IsBoundToGraphLifetime(UEdGraph& InGraph) const override
    {
        // 检查传入的图是否是本节点负责管理的转换图
        return (InGraph == MyManagedTransitionGraph);
    }

    virtual UEdGraphNode* AsNode() override
    {
        return this;
    }

private:
    UPROPERTY()
    TObjectPtr<USceneStateTransitionGraph> MyManagedTransitionGraph;
};
```

## Demo 示例

以下是一个最小化的 C++ 示例，演示如何创建一个继承自 `UEdGraph` 的自定义图，并集成场景状态转换图的模式（Schema）。

**MyDemoStateTransitionGraph.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "SceneStateTransitionGraph.h"
#include "MyDemoStateTransitionGraph.generated.h"

UCLASS()
class UMyDemoStateTransitionGraph : public USceneStateTransitionGraph
{
    GENERATED_BODY()

public:
    // 可以在这里添加自定义图表的属性和方法
    UPROPERTY()
    FString GraphDescription;
};
```

**MyDemoStateTransitionGraph.cpp**
```cpp
#include "MyDemoStateTransitionGraph.h"

// 此类已继承自 USceneStateTransitionGraph，
// 因此自动获得了 USceneStateTransitionGraphSchema 作为其图表模式，
// 在编辑器中双击打开时会使用场景状态转换图表的专用编辑器界面。
```

## 模块依赖

由于未提供具体的 `Build.cs` 文件内容，以下是根据模块名称和常见实践的推测。要使用 `SceneStateTransitionGraph` 模块，你的项目模块可能需要依赖以下内容（**请务必检查实际的 `Build.cs` 文件**）：

| 模块 | 用途 |
|---|---|
| `SceneState` | 场景状态核心运行时模块，提供基础状态和数据结构 |
| `SceneStateMachineGraph` | 状态机图表模块，提供基础图表节点和结构 |
| `UnrealEd` | 编辑器核心框架，用于创建自定义图表编辑器 |
| `Kismet` | 蓝图/图表编辑器基础设施 |
| `GraphEditor` | 图表编辑器UI和交互框架 |
| `PropertyEditor` | 用于在细节面板中编辑节点属性 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit... | 视口功能重构，与客户端关联/解除关联时进行通知。 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回滚了之前的提交 CL53913857。 |
| 2026-05-14 | `9ede83f2` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit... | 视口功能重构，与客户端关联/解除关联时进行通知。（与cfb610df可能为同一提交的不同阶段） |
| 2026-04-17 | `6e111b5d` | Motion Design Scene State: fixed issues with bindings not checking for null event payload struct (op... | 修复了场景状态绑定中未检查事件负载结构体是否为 null 的问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF。 |

### 维护评价

- **活跃度**：插件近期（2026年4月、5月）仍有持续的维护活动，包括bug修复和代码重构（日志宏迁移、空指针检查修复）。
- **状态**：该插件于 **2025年8月** 从实验区（Experimental）迁移到虚拟制作（VirtualProduction）类别，表明其正在逐步走向成熟。当前状态为 **Beta** (`IsBetaVersion: true`)，属于积极开发阶段。
- **建议**：可以用于项目原型和实验性功能开发。由于仍为Beta版本，在生产环境中使用时需要密切关注更新日志和已知问题，不建议用于需要长期稳定性的核心功能。
- **风险**：作为Beta软件，API和功能可能会有变动。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/SceneState)
- 官方文档：暂无
- 测试用例：未在提供的路径中发现公开的测试文件。