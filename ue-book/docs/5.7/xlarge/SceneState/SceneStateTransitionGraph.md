# Motion Design Scene State

> （Description 字段为空）

| 属性 | 值 |
|---|---|
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、图表资产） |
| 模块 | `SceneState` (Runtime), `SceneStateBinding` (Runtime), `SceneStateBlueprint` (Runtime), `SceneStateBlueprintEditor` (Runtime), `SceneStateEditor` (Runtime), `SceneStateEvent` (Runtime), `SceneStateEventEditor` (Runtime), `SceneStateEventGraph` (Runtime), `SceneStateGameplay` (Runtime), `SceneStateGameplayEditor` (Runtime), `SceneStateMachineEditor` (Runtime), `SceneStateMachineGraph` (Runtime), `SceneStateTasks` (Runtime), `SceneStateTransitionGraph` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/SceneState) | |

## 用途

**SceneState** 是一个为 **Motion Design（动态设计）** 工作流构建的复杂场景状态管理系统。它并非一个通用的状态机插件，而是深度集成于虚拟制作管线，旨在为艺术家和设计师提供一种直观、可视化的方式来定义和驱动场景中元素的状态、行为和交互。

该插件的核心目标是解决虚拟制作中场景元素（如灯光、摄像机、几何体、材质参数等）在不同“状态”（如“开场”、“高潮”、“转场”）间切换和响应事件的问题。它通过提供一套完整的编辑器工具链（状态机图、事件图、过渡图、数据绑定）和运行时框架，将复杂的场景逻辑从蓝图或C++代码中剥离出来，转化为可视化的、可维护的资产。

## 使用场景

-   **虚拟制作/广播图形**：你需要为一场虚拟演唱会或体育转播设计复杂的场景流程，包括灯光场景切换、摄像机预设激活、图形元素的显示/隐藏和动画触发。
-   **Motion Design 项目**：你在制作一个动态图形短片，需要精确控制多个3D元素在不同时间点的状态变化和过渡效果。
-   **交互式装置**：你正在开发一个博物馆互动装置，需要根据用户输入（如按钮、传感器）或时间线事件，切换场景的视觉呈现和交互模式。
-   **需要可视化逻辑的复杂场景**：当场景逻辑过于复杂，使用纯蓝图节点图难以维护时，可以使用 SceneState 的状态机和事件图来结构化地管理逻辑。

## 蓝图用法

由于 SceneState 是一个以编辑器图资产为核心的系统，其主要的“蓝图用法”体现在创建和编辑这些资产上，而非直接调用蓝图节点。运行时逻辑主要由状态机驱动。

### 核心资产类型

| 资产类型 | 说明 | 所在模块 |
|---|---|---|
| `USceneStateTransitionGraph` | 定义状态之间转换条件的图表。 | `SceneStateTransitionGraph` |
| `USceneStateConduitGraph` | 一种特殊的转换图，用于定义“导管”逻辑，可能用于复杂条件聚合。 | `SceneStateTransitionGraph` |
| `USceneStateTransitionResultNode` | 转换图中的结果节点，定义了转换的最终结果（如是否允许转换）。 | `SceneStateTransitionGraph` |

### 使用示例（蓝图描述）

1.  **创建状态机**：在内容浏览器中右键，创建 `Scene State Machine` 资产。双击打开状态机编辑器。
2.  **添加状态**：在状态机图中添加状态节点，每个状态可以关联一个 `Scene State` 资产（定义该状态下的具体场景配置）。
3.  **定义转换**：从一个状态节点拖拽到另一个状态节点，创建一条转换线。双击这条线，会打开一个 `SceneStateTransitionGraph`。
4.  **编写转换逻辑**：在打开的转换图中，使用蓝图节点（如比较节点、事件节点）连接到 `USceneStateTransitionResultNode` 的输入引脚，以定义何时允许此转换发生。
5.  **触发与运行**：在游戏逻辑或关卡蓝图中，通过 SceneState 提供的运行时接口触发状态机的启动、事件发送等操作。

## C++ 用法

SceneState 的 C++ 用法主要集中在扩展其编辑器图表系统和定义自定义的图表提供者。

### 头文件引入

```cpp
#include "SceneStateTransitionGraph.h"
#include "SceneStateTransitionResultNode.h"
#include "ISceneStateTransitionGraphProvider.h"
```

### 基本用法

创建一个自定义的图表提供者，使其能够拥有并管理一个转换图。

```cpp
// 来源: Engine/Plugins/VirtualProduction/SceneState/Source/SceneStateTransitionGraph/Public/ISceneStateTransitionGraphProvider.h
// 假设我们有一个自定义的 EdNode，它需要提供一个转换图
class UMyCustomTransitionNode : public UEdGraphNode, public ISceneStateTransitionGraphProvider
{
    GENERATED_BODY()

public:
    // ISceneStateTransitionGraphProvider 接口实现
    virtual FText GetTitle() const override
    {
        return NSLOCTEXT("MyNode", "Title", "My Custom Transition");
    }

    virtual bool IsBoundToGraphLifetime(UEdGraph& InGraph) const override
    {
        // 假设我们的节点与一个特定的转换图绑定
        return (TransitionGraph == &InGraph);
    }

    virtual UEdGraphNode* AsNode() override
    {
        return this;
    }

    // 拥有一个转换图
    UPROPERTY()
    TObjectPtr<USceneStateTransitionGraph> TransitionGraph;
};
```

### 进阶用法

在转换图中创建自定义节点，并与结果节点交互。

```cpp
// 来源: Engine/Plugins/VirtualProduction/SceneState/Source/SceneStateTransitionGraph/Public/Nodes/SceneStateTransitionResultNode.h
// 在自定义的转换图 Schema 中，可以控制结果节点的创建和行为
void UMyCustomTransitionGraphSchema::CreateDefaultNodesForGraph(UEdGraph& InGraph) const
{
    // 创建默认的结果节点
    FGraphNodeCreator<USceneStateTransitionResultNode> NodeCreator(InGraph);
    USceneStateTransitionResultNode* ResultNode = NodeCreator.CreateNode();
    NodeCreator.Finalize();
    SetNodeMetaData(ResultNode, FBlueprintMetadata::DefaultMessageNode);

    // 可以在这里设置结果节点的默认属性
    ResultNode->Result.bCanTransition = true; // 假设默认允许转换
}
```

## Demo 示例

以下示例展示如何创建一个简单的自定义转换图提供者节点。

**MyTransitionProviderNode.h**
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.
#pragma once

#include "EdGraph/EdGraphNode.h"
#include "ISceneStateTransitionGraphProvider.h"
#include "MyTransitionProviderNode.generated.h"

UCLASS()
class UMyTransitionProviderNode : public UEdGraphNode, public ISceneStateTransitionGraphProvider
{
    GENERATED_BODY()

public:
    //~ Begin ISceneStateTransitionGraphProvider Interface
    virtual FText GetTitle() const override;
    virtual bool IsBoundToGraphLifetime(UEdGraph& InGraph) const override;
    virtual UEdGraphNode* AsNode() override;
    //~ End ISceneStateTransitionGraphProvider Interface

    //~ Begin UEdGraphNode Interface
    virtual void AllocateDefaultPins() override;
    virtual FText GetNodeTitle(ENodeTitleType::Type TitleType) const override;
    //~ End UEdGraphNode Interface

    UPROPERTY()
    TObjectPtr<UEdGraph> BoundGraph;
};
```

**MyTransitionProviderNode.cpp**
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.
#include "MyTransitionProviderNode.h"

FText UMyTransitionProviderNode::GetTitle() const
{
    return NSLOCTEXT("MyTransition", "ProviderTitle", "My Transition");
}

bool UMyTransitionProviderNode::IsBoundToGraphLifetime(UEdGraph& InGraph) const
{
    return (BoundGraph == &InGraph);
}

UEdGraphNode* UMyTransitionProviderNode::AsNode()
{
    return this;
}

void UMyTransitionProviderNode::AllocateDefaultPins()
{
    // 创建一个执行引脚，用于连接其他节点
    CreatePin(EGPD_Input, UEdGraphSchema_K2::PC_Exec, TEXT("In"));
    CreatePin(EGPD_Output, UEdGraphSchema_K2::PC_Exec, TEXT("Out"));
}

FText UMyTransitionProviderNode::GetNodeTitle(ENodeTitleType::Type TitleType) const
{
    return GetTitle();
}
```

## 模块依赖

由于未提供具体的 Build.cs 文件，以下依赖基于模块名称和常见模式推断。SceneState 系统模块间存在复杂的相互依赖。

| 模块 | 用途 |
|---|---|
| `SceneState` | 核心运行时状态管理框架 |
| `SceneStateBinding` | 处理场景状态与场景对象之间的数据绑定 |
| `SceneStateEvent` | 定义和管理场景状态事件系统 |
| `SceneStateTasks` | 提供状态任务（如延迟、播放动画等）的实现 |
| `SceneStateMachineGraph` | 状态机图表的编辑器表示和逻辑 |
| `SceneStateTransitionGraph` | 状态转换图表的编辑器表示和逻辑 |
| `SceneStateEventGraph` | 事件图表的编辑器表示和逻辑 |
| `SceneStateBlueprint` | 与蓝图系统的集成 |
| `SceneStateGameplay` | 与游戏玩法框架的集成 |
| `*Editor` 模块 | 各个对应运行时模块的编辑器工具、自定义资产编辑器、图表编辑器等 |

## 维护状态

### 近期更新

```
- 2025-04-22 94f961385e8e Motion Design: Moved scene state and data link plugins out of experimental into virtualproduction
```

### 维护评价

-   **创建时间**：插件非常新（约 0 年），于 2025 年 4 月首次提交。
-   **最近更新**：仅有一次提交记录，内容是将插件从 `Experimental` 目录移动到 `VirtualProduction` 目录。这表明插件正在从实验阶段向正式支持的虚拟制作工具过渡。
-   **活跃度**：基于单次提交，无法判断长期维护频率。但作为 Epic 官方虚拟制作工具链的一部分，预计会得到持续支持。
-   **已知问题/限制**：作为 Beta 版本（`IsBetaVersion: true`），API 和功能可能不稳定，存在破坏性更改的风险。文档和示例可能不完善。
-   **推荐使用**：**谨慎推荐**。如果你正在开发基于 UE5 的虚拟制作或 Motion Design 项目，并且愿意承担 Beta 软件的风险，可以尝试使用。对于生产环境，建议密切关注其版本更新和稳定性报告。对于普通游戏开发，此插件可能过于专用且复杂。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/SceneState)
- [官方文档]() （暂无）
- [测试用例]() （暂未发现公开测试用例）

---
# SceneStateTransitionGraph 模块

> 该模块提供了场景状态转换图的编辑器图表表示、Schema 和核心节点。

| 属性 | 值 |
|---|---|
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SceneStateTransitionGraph` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/SceneState/Source/SceneStateTransitionGraph) | |

## 用途

`SceneStateTransitionGraph` 模块是 SceneState 状态机系统的核心编辑器组件之一。它定义了用于描述状态之间“转换条件”的图表资产和相关节点。当用户在状态机编辑器中连接两个状态并编辑其转换逻辑时，实际操作的就是由该模块提供的 `USceneStateTransitionGraph` 图表。该模块还包含一个特殊的“导管图”（Conduit Graph），可能用于实现更复杂的、可复用的转换逻辑聚合。

## 使用场景

-   **定义状态转换条件**：在 SceneState 状态机中，为两个状态之间的连线编写具体的判断逻辑（例如：“当玩家按下空格键”、“当计时器大于5秒”、“当某个变量为真”）。
-   **创建可复用的转换逻辑**：使用 `USceneStateConduitGraph` 封装一组复杂的条件判断，然后在多个状态转换中引用这个“导管”，避免重复编写相同的逻辑。
-   **扩展转换系统**：通过实现 `ISceneStateTransitionGraphProvider` 接口，创建自定义的图表提供者节点，将转换图与自定义的编辑器节点关联起来。

## 蓝图用法

本模块主要提供编辑器图表资产，不直接暴露运行时蓝图节点。其“蓝图用法”体现在图表编辑器中的节点连接。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Transition Result` | 转换图的输出节点，其布尔输入引脚的值决定了转换是否被允许。 | `USceneStateTransitionResultNode` |

### 使用示例（蓝图描述）

1.  在状态机编辑器中，双击一条状态转换线，打开 `USceneStateTransitionGraph`。
2.  图表中会自动创建一个 `USceneStateTransitionResultNode`。
3.  从其他蓝图节点（如 `Branch`、`Equal`、自定义函数节点）的输出布尔引脚，拖拽连线到 `Transition Result` 节点的输入引脚。
4.  当该输入为 `true` 时，状态机将执行此转换。

## C++ 用法

### 头文件引入

```cpp
#include "SceneStateTransitionGraph.h"
#include "SceneStateTransitionGraphSchema.h"
#include "SceneStateConduitGraph.h"
#include "ISceneStateTransitionGraphProvider.h"
#include "Nodes/SceneStateTransitionResultNode.h"
```

### 基本用法

创建一个转换图并获取其结果节点。

```cpp
// 来源: Engine/Plugins/VirtualProduction/SceneState/Source/SceneStateTransitionGraph/Public/SceneStateTransitionGraph.h
// 创建一个新的转换图对象
USceneStateTransitionGraph* TransitionGraph = NewObject<USceneStateTransitionGraph>();

// 结果节点通常在图创建时由 Schema 自动创建
USceneStateTransitionResultNode* ResultNode = TransitionGraph->ResultNode;
if (ResultNode)
{
    // 可以访问或修改结果节点的属性
    UE_LOG(LogTemp, Log, TEXT("Transition Graph has a result node."));
}
```

### 进阶用法

实现 `ISceneStateTransitionGraphProvider` 接口，将一个自定义的 EdNode 与转换图的生命周期绑定。

```cpp
// 来源: Engine/Plugins/VirtualProduction/SceneState/Source/SceneStateTransitionGraph/Public/ISceneStateTransitionGraphProvider.h
// 在自定义节点类中实现接口
class UMyStateNode : public UEdGraphNode, public ISceneStateTransitionGraphProvider
{
    // ... 其他代码 ...

    virtual bool IsBoundToGraphLifetime(UEdGraph& InGraph) const override
    {
        // 假设我们的节点管理着一个名为 MyTransitionGraph 的图表
        return (MyTransitionGraph == &InGraph);
    }

    UPROPERTY()
    TObjectPtr<USceneStateTransitionGraph> MyTransitionGraph;
};
```

## Demo 示例

演示如何通过 Schema 控制转换图的默认行为。

**MyTransitionGraphSchema.h**
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.
#pragma once

#include "SceneStateTransitionGraphSchema.h"
#include "MyTransitionGraphSchema.generated.h"

UCLASS()
class UMyTransitionGraphSchema : public USceneStateTransitionGraphSchema
{
    GENERATED_BODY()

public:
    // 重写以提供自定义的图表显示信息
    virtual void GetGraphDisplayInformation(const UEdGraph& InGraph, FGraphDisplayInfo& OutDisplayInfo) const override;
};
```

**MyTransitionGraphSchema.cpp**
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.
#include "MyTransitionGraphSchema.h"

void UMyTransitionGraphSchema::GetGraphDisplayInformation(const UEdGraph& InGraph, FGraphDisplayInfo& OutDisplayInfo) const
{
    // 调用父类实现获取基本信息
    Super::GetGraphDisplayInformation(InGraph, OutDisplayInfo);

    // 添加自定义信息
    OutDisplayInfo.AddCategory(TEXT("My Custom Category"));
    OutDisplayInfo.Tooltip = NSLOCTEXT("MySchema", "Tooltip", "This is a custom transition graph.");
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `SceneState` | 核心状态数据结构和运行时逻辑 |
| `SceneStateEvent` | 可能用于在转换条件中引用事件 |
| `Kismet` | 提供 `UK2Node` 基类和蓝图图表基础设施 |
| `BlueprintGraph` | 蓝图图表编辑相关功能 |

## 维护状态

### 近期更新

```
- 2025-04-22 94f961385e8e Motion Design: Moved scene state and data link plugins out of experimental into virtualproduction
```

### 维护评价

该模块与父插件 SceneState 同龄，非常新。作为 SceneState 状态机编辑器的核心部分，其稳定性直接关系到整个状态机编辑器的可用性。目前仅有一次初始提交，表明它正处于积极开发的早期阶段。由于是 Beta 版本的一部分，其 API 和内部结构可能会频繁变动。建议仅在开发或研究目的下使用，并做好应对 breaking changes 的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/SceneState/Source/SceneStateTransitionGraph)
- [官方文档]() （暂无）
- [测试用例]() （暂未发现公开测试用例）