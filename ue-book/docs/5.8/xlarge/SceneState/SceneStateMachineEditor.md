# Motion Design Scene State

> （照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 运动设计场景状态 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、测试资源） |
| 模块 | `SceneState` (Runtime), `SceneStateBinding` (Runtime), `SceneStateBlueprint` (Runtime), `SceneStateBlueprintEditor` (Runtime), `SceneStateEditor` (Runtime), `SceneStateEvent` (Runtime), `SceneStateEventEditor` (Runtime), `SceneStateEventGraph` (Runtime), `SceneStateGameplay` (Runtime), `SceneStateGameplayEditor` (Runtime), `SceneStateMachineEditor` (Runtime), `SceneStateMachineGraph` (Runtime), `SceneStateTasks` (Runtime), `SceneStateTransitionGraph` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-27 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/SceneState) | |

## 用途

基于源码分析，SceneState 是一个用于**虚拟制作（Virtual Production）** 领域，特别是**运动设计（Motion Design）** 的**状态机系统**。它提供了一套完整的框架，用于在编辑器中以图形化方式设计和管理复杂场景对象的状态逻辑，并在运行时高效执行。

核心解决的问题是：如何为电影、广告或现场活动中的复杂视觉特效序列（例如，舞台灯光秀、相机切换、粒子特效触发）创建可预测、可复用且易于迭代的**状态驱动（State-Driven）** 脚本。它超越了基础的动画蓝图，专注于处理离散的场景状态（如“入场”、“高潮”、“退场”）及其之间的转换条件，非常适合编排需要精确时序和逻辑控制的虚拟制片流程。

## 使用场景

- 你在策划一个虚拟舞台灯光秀，需要定义“观众入场”、“演出开始”、“歌曲间奏”、“谢幕”等状态，并在不同状态间根据音乐时间码或操作员输入自动切换灯光模式和相机视角。
- 你在制作一个产品发布会视频，需要让多个虚拟摄像机、虚拟角色和动态背景根据不同发布会环节（如“开场白”、“产品展示”、“问答环节”）自动执行预设动作。
- 你需要为一个大型虚拟制片项目创建模块化、可复用的状态逻辑单元（例如，“单个聚光灯控制”、“一组特效播放”），并将它们组合成复杂的时间线。

## 蓝图用法

当前文档聚焦的 `SceneStateMachineEditor` 模块主要提供**编辑器端**的图形化编译和用户界面支持，不直接暴露运行时蓝图节点。整个插件的蓝图使用主要通过 `SceneStateBlueprint`、`SceneStateGameplay` 等模块提供。核心的蓝图交互模式是：在编辑器中使用**状态机图（Scene State Machine Graph）** 来设计状态、转换和任务，这些图会编译成可在游戏或虚拟制片运行时执行的数据。

### 核心节点（概念）

由于本模块是编辑器编译后端，其“节点”对应编辑器中的图表元素：

| 编辑器元素 | 说明 | 对应编译器类 |
|---|---|---|
| **状态节点 (State Node)** | 代表场景中的一个离散状态（如“灯光模式A”）。 | `USceneStateMachineStateNode` |
| **转换节点 (Transition Node)** | 定义从一个状态到另一个状态的转换条件和逻辑。 | `USceneStateMachineTransitionNode` |
| **通道节点 (Conduit Node)** | 用于组织和路由转换，本身不包含状态逻辑，类似于图表的连接器。 | `USceneStateMachineConduitNode` |
| **任务节点 (Task Node)** | 附加在状态上，代表该状态下需要执行的具体动作（如“播放粒子特效”、“调用函数”）。 | `USceneStateMachineTaskNode` |

### 使用示例（蓝图描述）

1.  在编辑器中，通过 `Content Browser` 创建一个 `Scene State Machine` 资产。
2.  双击打开资产，进入状态机图编辑器。
3.  从工具栏拖拽 **State Node** 到图表中，命名为 `“舞台空闲”`。
4.  从 `“舞台空闲”` 状态节点的输出引脚拖拽出连线，并连接到另一个新的 **State Node** `“灯光秀进行中”`。这条连线会自动创建一个 **Transition Node**。
5.  选中这个 **Transition Node**，在细节面板中编写转换条件，例如 `“接收到‘开始表演’事件”` 或 `“时间大于 10 秒”`。
6.  选中 `“灯光秀进行中”` 状态节点，从任务列表添加 **Task Node**，例如 `“播放预设动画序列”` 或 `“激活粒子发射器”`。
7.  编译并运行，在运行时根据设计的逻辑和条件驱动场景对象的状态变化。

## C++ 用法

`SceneStateMachineEditor` 模块的核心功能是**将编辑器中的状态机图表编译成可在运行时执行的轻量级数据结构**。以下用法主要面向需要扩展或自定义编译流程的开发者。

### 头文件引入

```cpp
// 主编译器
#include "SceneStateMachineCompiler.h"

// 子编译器
#include "SceneStateMachineTransitionCompiler.h"
#include "SceneStateMachineTaskCompiler.h"
#include "SceneStateMachineConduitCompiler.h"

// 编译器上下文接口
#include "ISceneStateMachineCompilerContext.h"
```

### 基本用法：编译一个状态机图

从测试用例和核心类设计中可以提取出最基本的编译流程。你需要提供一个 `IStateMachineCompilerContext` 的实现，它负责管理编译期间的模板数据并处理转换图的编译请求。

```cpp
// 假设你已经有了一个 USceneStateMachineGraph* Graph 和一个 UBlueprint* Blueprint
// 1. 准备编译器上下文 (通常由插件内部提供或子类化)
class FMyStateMachineCompilerContext : public UE::SceneState::Editor::IStateMachineCompilerContext
{
public:
    FMyStateMachineCompilerContext(USceneStateTemplateData* InTemplateData) : TemplateData(InTemplateData) {}
    virtual ~FMyStateMachineCompilerContext() override {}

    //~ Begin IStateMachineCompilerContext
    virtual USceneStateTemplateData* GetTemplateData() override { return TemplateData; }
    virtual FTransitionGraphCompileResult CompileTransitionGraph(USceneStateTransitionGraph* InTransitionGraph) override
    {
        // 这里需要实现对转换图（条件逻辑）的编译，通常由插件的其他模块处理
        // 返回一个成功的结果
        return { ETransitionGraphCompileReturnCode::Success, FName(), FName() };
    }
    //~ End IStateMachineCompilerContext

private:
    TObjectPtr<USceneStateTemplateData> TemplateData;
};

// 2. 执行编译
USceneStateTemplateData* MyTemplateData = ...; // 分配的模板数据对象
FMyStateMachineCompilerContext CompilerContext(MyTemplateData);

UE::SceneState::Editor::FStateMachineCompiler Compiler(Graph, CompilerContext);
FSceneStateMachine RuntimeStateMachine = Compiler.Compile();
// RuntimeStateMachine 现在包含了可用于运行时的状态、转换、任务等数据
```

**来源**：基于 `Public/SceneStateMachineCompiler.h` 和 `Public/ISceneStateMachineCompilerContext.h` 的类接口分析。

### 进阶用法：自定义节点工厂

`SceneStateMachineEditor` 模块通过工厂模式创建不同的图表节点控件（`SGraphNode`）。你可以继承或注册自定义的工厂来修改或扩展节点的外观和行为。

```cpp
// 获取编辑器模块
FSceneStateMachineEditorModule& EditorModule = FModuleManager::LoadModuleChecked<FSceneStateMachineEditorModule>("SceneStateMachineEditor");

// 模块内部已经注册了默认工厂 (FStateMachineEdGraphNodeFactory, FStateMachineEdGraphPinFactory 等)
// 如果你需要添加全新的节点类型并定制其Slate控件，可以创建自己的工厂
struct FMyCustomNodeFactory : public UE::SceneState::Editor::FStateMachineEdGraphNodeFactory
{
    virtual TSharedPtr<SGraphNode> CreateNode(UEdGraphNode* InNode) const override
    {
        // 检查是否是你的自定义节点类
        if (UMyCustomStateNode* MyNode = Cast<UMyCustomStateNode>(InNode))
        {
            return SNew(SMyCustomStateNodeWidget, MyNode); // 返回你的自定义Slate控件
        }
        // 否则，调用父类默认创建
        return FStateMachineEdGraphNodeFactory::CreateNode(InNode);
    }
};

// 在合适的时机注册这个工厂 (例如，在你的自定义模块的StartupModule中)
```

**来源**：基于 `Private/SceneStateMachineEdGraphFactory.h` 的工厂注册模式。

## Demo 示例

由于 `SceneStateMachineEditor` 是一个**编辑器模块**，其主要功能是在编辑器环境中编译和渲染状态机图。以下示例展示了如何在C++中**模拟**其编译器的最基本使用逻辑，但这不是独立运行的完整项目，而是插件内部工作原理的演示。

```cpp
// MyStateMachineUsage.h
#pragma once
#include "CoreMinimal.h"
// 假设包含路径正确
#include "SceneStateMachineCompiler.h"
#include "ISceneStateMachineCompilerContext.h"
#include "SceneStateTemplateData.h" // 假设此类型存在

class FMinimalStateMachineCompilerContext : public UE::SceneState::Editor::IStateMachineCompilerContext
{
public:
    FMinimalStateMachineCompilerContext(USceneStateTemplateData* InData) : Data(InData) {}

    virtual USceneStateTemplateData* GetTemplateData() override { return Data; }
    virtual FTransitionGraphCompileResult CompileTransitionGraph(USceneStateTransitionGraph* InGraph) override
    {
        // 简化实现：总是返回成功，无事件名
        return { UE::SceneState::Editor::ETransitionGraphCompileReturnCode::Success, FName(), FName() };
    }

private:
    TObjectPtr<USceneStateTemplateData> Data;
};

// MyStateMachineUsage.cpp
#include "MyStateMachineUsage.h"
// 其他必要的包含

void CompileExampleStateMachine(USceneStateMachineGraph* Graph, USceneStateTemplateData* TemplateData)
{
    if (!Graph || !TemplateData)
    {
        return;
    }

    FMinimalStateMachineCompilerContext Context(TemplateData);
    UE::SceneState::Editor::FStateMachineCompiler Compiler(Graph, Context);

    // 执行编译
    FSceneStateMachine CompiledMachine = Compiler.Compile();

    UE_LOG(LogTemp, Log, TEXT("Compiled State Machine with %d states."), CompiledMachine.States.Num());
    // CompiledMachine 现在可用于驱动运行时逻辑
}
```

## 模块依赖

从 `Build.cs` 和模块职责推断，`SceneStateMachineEditor` 模块主要依赖于状态机图模型和编译基础设施，没有对不常见外部库的特殊依赖。

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 对视口相关代码进行了重构优化。 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回退了之前的某次提交。 |
| 2026-05-14 | `9ede83f2` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 与`cfb610df`为同一次重构的提交。 |
| 2026-04-17 | `6e111b5d` | Motion Design Scene State: fixed issues with bindings not checking for null event payload struct (op | 修复了运动设计场景状态中绑定未检查空事件有效负载结构体的问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式的 `UE_LOG` 迁移为新的 `UE_LOGF` 日志宏。 |

### 维护评价

**综合评价：积极维护中的实验性功能。**

- **创建时间**：插件整体于 2025 年 8 月创建，非常年轻。
- **维护频率**：近期有活跃的提交，包括功能修复（`6e111b5d`）和代码现代化（`35e60df1`，日志宏迁移），表明开发团队正在积极迭代和维护。
- **内容**：提交内容涉及功能修复、代码重构和标准化，是健康的开发迹象。
- **实验性状态**：`.uplugin` 中 `Category` 为 “Experimental”，且 `IsBetaVersion: true`。这明确表明该功能尚未稳定，API 和功能在未来版本中可能发生重大变化。
- **已知问题/限制**：作为实验性功能，其稳定性、文档和外围工具支持可能不足。源码中未见明显废弃标记。
- **推荐使用**：**谨慎推荐**。适合对虚拟制片/运动设计有前沿探索需求的团队，可以用于原型设计和概念验证。但由于其**实验性（Beta）** 标签，**不建议**用于需要长期稳定维护的生产项目核心功能中。应密切关注后续版本的更新日志和破坏性变更通知。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/SceneState)
- [官方文档]()（无，.uplugin 中未提供）
- [测试用例]()（插件自身目录下未发现明显测试文件，相关测试可能位于 `Engine/Tests/` 或其他位置）