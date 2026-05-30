# Motion Design Scene State

> Motion Design Scene State plugin for managing scene states and data links.

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计场景状态 |
| 分类 | VirtualProduction |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、图表节点） |
| 模块 | `SceneState` (Runtime), `SceneStateBinding` (Runtime), `SceneStateBlueprint` (Runtime), `SceneStateBlueprintEditor` (Runtime), `SceneStateEditor` (Runtime), `SceneStateEvent` (Runtime), `SceneStateEventEditor` (Runtime), `SceneStateEventGraph` (Runtime), `SceneStateGameplay` (Runtime), `SceneStateGameplayEditor` (Runtime), `SceneStateMachineEditor` (Runtime), `SceneStateMachineGraph` (Runtime), `SceneStateTasks` (Runtime), `SceneStateTransitionGraph` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/SceneState) | |

## 用途

**Motion Design Scene State** 插件为 Unreal Engine 的**虚拟制片**和**动态设计**工作流提供了一套完整的**场景状态管理**与**数据绑定**系统。它解决了在复杂场景中（如广播级实时图形、虚拟演播室）如何高效、可视化地控制场景对象状态转换和数据同步的核心问题。其存在价值在于将传统蓝图状态机与专门的“数据链接”概念相结合，为设计师和开发者提供了一种更直观、更可控的场景逻辑构建方式。

**核心概念**：
1.  **场景状态机**：类似于蓝图中的状态机，但专为场景对象的状态管理而设计，支持事件驱动和数据驱动的状态转换。
2.  **数据链接**：定义了不同场景对象属性或组件之间的数据流，确保状态变化能正确、高效地传递和同步。
3.  **事件系统**：提供了一套完整的事件广播、推送、查找和检查机制，是状态机驱动的主要方式。

## 使用场景

*   **虚拟演播室图形控制**：你需要为体育转播或新闻节目创建动态的、可交互的实时图形。使用 `SceneState` 插件可以将图形的出现、动画、数据更新等逻辑封装在清晰的状态机中，并通过事件控制其切换。
*   **复杂场景交互流程**：在虚拟制片场景中，你需要让多个道具或角色按特定剧本（如展览流程、互动装置）进入不同状态。利用该插件的状态机和数据绑定，可以精确编排整个流程。
*   **数据驱动的视觉呈现**：你需要将来自外部系统（如数据库、传感器）的数据实时反映到场景中。通过数据链接和事件，可以构建从数据源到视觉表现的自动化管线。

## 蓝图用法

此插件通过自定义蓝图节点（`UK2Node`）扩展了蓝图编辑器的功能，主要围绕**场景状态事件**的发送与接收。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Broadcast Scene State Event` | **广播事件**。向指定的 `EventStream` 发送一个场景状态事件，任何监听该流的处理器都会收到。 | `UK2Node_SceneStateBroadcastEvent` |
| `Push Scene State Event` | **推送事件**。将事件直接推送到特定的目标处理器，而非广播。 | `UK2Node_SceneStatePushEvent` |
| `Find Scene State Event` | **查找事件**。从指定的 `EventStream` 中查找并返回一个具有特定 Schema 的事件对象（如果存在）。 | `UK2Node_SceneStateFindEvent` |
| `Has Scene State Event` | **检查事件**。检查指定的 `EventStream` 中是否存在具有特定 Schema 的事件，返回布尔值。 | `UK2Node_SceneStateHasEvent` |

### 使用示例（蓝图描述）

1.  **触发状态转换**：
    *   在某个 Actor 的事件图表中，添加一个 `Broadcast Scene State Event` 节点。
    *   为其 `Event Stream` 引脚连接一个代表场景事件流的对象（通常通过上下文获取）。
    *   设置 `Event Schema` 为你事先定义好的、代表“场景重置”、“切换模式”等逻辑的事件结构体。
    *   （可选）如果事件携带数据，通过节点自动生成的 `Event Data` 输入引脚填入具体数据。
    *   当该节点执行时，事件被广播，所有订阅了该事件 Schema 的状态机或处理器将被触发，从而执行相应的状态转换或逻辑。

2.  **监听并响应事件**：
    *   在状态机的一个状态内，可以使用 `Find Scene State Event` 或 `Has Scene State Event` 节点进行条件检查。
    *   例如，在状态机的“更新”逻辑中，使用 `Has Scene State Event` 节点检查是否收到了“用户输入”事件。如果是，则连接执行流到状态转换引脚。

## C++ 用法

此插件的 `SceneStateEventGraph` 模块主要提供**蓝图节点**的底层实现。扩展或自定义新的场景状态事件节点需要深入理解其基类 `UK2Node_SceneStateEventBase`。

### 头文件引入

```cpp
#include "SceneStateEventGraph/Nodes/K2Node_SceneStateEventBase.h"
```

### 基本用法（继承与创建自定义事件节点）

以下代码演示了如何创建一个新的蓝图节点，用于发送一个自定义的“特效触发”场景状态事件。此示例基于对 `UK2Node_SceneStateBroadcastEvent` 的简化理解。

**MyK2Node_TriggerEffect.h**
```cpp
#pragma once
#include "SceneStateEventGraph/Nodes/K2Node_SceneStateEventBase.h"
#include "MyK2Node_TriggerEffect.generated.h"

UCLASS()
class UMyK2Node_TriggerEffect : public UK2Node_SceneStateEventBase
{
	GENERATED_BODY()

public:
	UMyK2Node_TriggerEffect();

protected:
	//~ Begin UEdGraphNode
	virtual void AllocateDefaultPins() override;
	virtual FText GetNodeTitle(ENodeTitleType::Type InTitleType) const override;
	//~ End UEdGraphNode

	//~ Begin UK2Node
	virtual void ExpandNode(FKismetCompilerContext& InCompilerContext, UEdGraph* InSourceGraph) override;
	//~ End UK2Node
};
```

**MyK2Node_TriggerEffect.cpp**
```cpp
#include "MyK2Node_TriggerEffect.h"
// ... 其他必要的头文件，如 K2Node_CallFunction

UMyK2Node_TriggerEffect::UMyK2Node_TriggerEffect()
{
	// 设置此节点将使用的事件 Schema
	// FSceneStateEventSchemaHandle MySchemaHandle = ... // 获取或创建一个特定的事件 Schema
	// EventSchemaHandle = MySchemaHandle;
}

void UMyK2Node_TriggerEffect::AllocateDefaultPins()
{
	// 调用基类分配标准引脚（EventStream， WorldContextObject）
	Super::AllocateDefaultPins();
	// 根据 EventSchemaHandle 创建事件数据输入引脚（如果需要）
	CreateEventDataPins(/* InPinsToSearch */ {});
	// 添加任何自定义的输入引脚，例如特效资源
	CreatePin(EGPD_Input, UEdGraphSchema_K2::PC_Object, UParticleSystem::StaticClass(), FName("EffectAsset"));
}

FText UMyK2Node_TriggerEffect::GetNodeTitle(ENodeTitleType::Type InTitleType) const
{
	return FText::FromString(TEXT("Trigger Effect Event"));
}

void UMyK2Node_TriggerEffect::ExpandNode(FKismetCompilerContext& InCompilerContext, UEdGraph* InSourceGraph)
{
	Super::ExpandNode(InCompilerContext, InSourceGraph);
	// 在此实现节点的编译逻辑：
	// 1. 创建中间调用节点（例如调用一个 BroadcastSceneEvent 的底层函数）
	// 2. 将自定义引脚（如 EffectAsset）连接到中间节点
	// 3. 使用 ChainNode 和 FinishChain 管理执行流
	// 详细逻辑需参考 UK2Node_SceneStateBroadcastEvent 的实现
}
```

### 进阶用法（理解节点扩展上下文）

`UK2Node_SceneStateEventBase` 内部定义了一个 `FNodeExpansionContext` 结构体，它在 `ExpandNode` 函数中用于管理节点到中间节点的链接过程。自定义复杂事件节点时，需要操作此上下文。

```cpp
// 在 ExpandNode 内部示例
FNodeExpansionContext Context;
Context.CompilerContext = InCompilerContext;
Context.SourceGraph = InSourceGraph;
Context.EventDataPin = /* 获取事件数据输出引脚 */;

// 添加第一个中间节点（如参数准备节点）
UK2Node* PrepNode = CreateTempNode<UK2Node>();
// ... 配置 PrepNode
ChainNode(Context, PrepNode); // 将 PrepNode 链接到当前节点的执行流

// 添加第二个中间节点（如实际调用函数的节点）
UK2Node_CallFunction* FuncNode = CreateTempNode<UK2Node_CallFunction>();
// ... 设置函数、连接参数
ChainNode(Context, FuncNode);

// 完成链条，将“Then”执行引脚移动到最后一个节点
FinishChain(Context);
```

## Demo 示例

一个最小的自定义场景状态事件蓝图节点，当在蓝图中调用时，会记录一条消息。

**MyK2Node_LogSceneEvent.h**
```cpp
#pragma once
#include "SceneStateEventGraph/Nodes/K2Node_SceneStateEventBase.h"
#include "MyK2Node_LogSceneEvent.generated.h"

UCLASS()
class UMyK2Node_LogSceneEvent : public UK2Node_SceneStateEventBase
{
	GENERATED_BODY()

public:
	UMyK2Node_LogSceneEvent();

protected:
	virtual void AllocateDefaultPins() override;
	virtual FText GetNodeTitle(ENodeTitleType::Type InTitleType) const override;
	virtual void ExpandNode(FKismetCompilerContext& InCompilerContext, UEdGraph* InSourceGraph) override;
};
```

**MyK2Node_LogSceneEvent.cpp**
```cpp
#include "MyK2Node_LogSceneEvent.h"
#include "EdGraphSchema_K2.h"
#include "K2Node_CallFunction.h"
#include "KismetCompiler.h"

UMyK2Node_LogSceneEvent::UMyK2Node_LogSceneEvent()
{
	// 此示例不处理事件数据，因此可以设置一个最小的或虚拟的 Schema
	bHasEventData = false;
}

void UMyK2Node_LogSceneEvent::AllocateDefaultPins()
{
	Super::AllocateDefaultPins(); // 创建 EventStream, WorldContextObject
	// 添加一个自定义的文本输入引脚
	CreatePin(EGPD_Input, UEdGraphSchema_K2::PC_Text, FName("LogMessage"));
}

FText UMyK2Node_LogSceneEvent::GetNodeTitle(ENodeTitleType::Type InTitleType) const
{
	return FText::FromString(TEXT("Log Scene State"));
}

void UMyK2Node_LogSceneEvent::ExpandNode(FKismetCompilerContext& InCompilerContext, UEdGraph* InSourceGraph)
{
	Super::ExpandNode(InCompilerContext, InSourceGraph);

	// 1. 创建调用 PrintString 函数的节点
	UK2Node_CallFunction* PrintFuncNode = InCompilerContext.SpawnIntermediateNode<UK2Node_CallFunction>(this, InSourceGraph);
	static const FName PrintFuncName = GET_FUNCTION_NAME_CHECKED(UKismetSystemLibrary, PrintString);
	PrintFuncNode->FunctionReference.SetExternalMember(PrintFuncName, UKismetSystemLibrary::StaticClass());
	PrintFuncNode->AllocateDefaultPins();

	// 2. 获取相关引脚
	UEdGraphPin* ExecPin = GetExecPin();
	UEdGraphPin* ThenPin = FindPin(UEdGraphSchema_K2::PN_Then);
	UEdGraphPin* MsgPin = FindPin(FName("LogMessage"));
	UEdGraphPin* PrintExecPin = PrintFuncNode->GetExecPin();
	UEdGraphPin* PrintMsgPin = PrintFuncNode->FindPin(FName("InString"));
	UEdGraphPin* PrintWorldPin = PrintFuncNode->FindPin(FName("WorldContextObject"));

	// 3. 连接执行流
	InCompilerContext.MovePinLinksToIntermediate(*ExecPin, *PrintExecPin);
	InCompilerContext.MovePinLinksToIntermediate(*ThenPin, *PrintFuncNode->GetThenPin());

	// 4. 连接数据
	InCompilerContext.MovePinLinksToIntermediate(*MsgPin, *PrintMsgPin);
	// 将节点自带的 WorldContextObject 引脚连接到 PrintString 函数
	UEdGraphPin* MyWorldPin = FindPin(PN_WorldContextObject);
	if (MyWorldPin && PrintWorldPin)
	{
		InCompilerContext.MovePinLinksToIntermediate(*MyWorldPin, *PrintWorldPin);
	}

	// 5. 处理事件流和上下文（使用基类方法）
	FNodeExpansionContext Context;
	Context.CompilerContext = InCompilerContext;
	Context.SourceGraph = InSourceGraph;
	Context.EventDataPin = nullptr; // 无事件数据
	// 由于没有其他中间节点需要链接，这里通常不需要显式调用 ChainNode/FinishChain
	// 因为执行流已经通过 MovePinLinksToIntermediate 处理了。
}
```

## 模块依赖

基于 `SceneStateEventGraph` 模块的推断依赖。实际使用整个插件时，依赖关系会更复杂。

| 模块 | 用途 |
|---|---|
| `SceneState` | 场景状态管理的运行时核心模块，提供基础类型和接口 |
| `KismetCompiler` | 蓝图编译器，用于自定义节点的编译扩展 |
| `BlueprintGraph` | 蓝图图表基础框架 |

*(注：完整的 `Build.cs` 文件内容未在提供信息中给出，上述依赖基于模块功能和头文件引用推断。实际开发时，请以模块 `Build.cs` 文件为准。)*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构视口相关代码，通过通知客户端关联/解耦状态来减少重复代码 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回退之前的提交（CL53913857） |
| 2026-04-17 | `6e111b5d` | Motion Design Scene State: fixed issues with bindings not checking for null event payload struct (op | 修复数据绑定逻辑中未检查事件载荷结构体是否为空的问题 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将传统的 UE_LOG 日志调用迁移到 UE_LOGF 宏 |

### 维护评价

*   **创建时间**：2025年8月创建，属于较新的插件。
*   **更新频率**：在创建后不到一年的时间内（截至2026年5月），仍有持续的功能性更新和Bug修复，表明处于**活跃开发**阶段。
*   **维护状态**：**活跃维护中**。最近的提交涉及代码重构、功能修复和代码质量改进（日志宏迁移）。
*   **已知问题/限制**：插件处于 **Beta** 状态 (`IsBetaVersion: true`)，意味着其API和功能可能尚未完全稳定，可能存在未发现的Bug，且未来版本可能有破坏性变更。
*   **推荐使用**：**推荐在实验性项目或非关键路径的虚拟制片/动态设计工作流中使用**。对于追求稳定性的正式项目，建议密切关注其版本变化并评估Beta状态带来的风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/SceneState)
- [官方文档]() (暂无)
- [测试用例]() (在提供的信息中未明确路径，通常可在插件目录内或 `Engine/Tests` 下查找)