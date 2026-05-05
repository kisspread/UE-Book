# Motion Design Scene State

> （Description 为空）

| 属性 | 值 |
|---|---|
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、状态机图表、任务定义等） |
| 模块 | `SceneState` (Runtime), `SceneStateBinding` (Runtime), `SceneStateBlueprint` (Runtime), `SceneStateBlueprintEditor` (Runtime), `SceneStateEditor` (Runtime), `SceneStateEvent` (Runtime), `SceneStateEventEditor` (Runtime), `SceneStateEventGraph` (Runtime), `SceneStateGameplay` (Runtime), `SceneStateGameplayEditor` (Runtime), `SceneStateMachineEditor` (Runtime), `SceneStateMachineGraph` (Runtime), `SceneStateTasks` (Runtime), `SceneStateTransitionGraph` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/SceneState) | |

## 用途

Motion Design Scene State 插件提供了一个**可视化、数据驱动的状态机系统**，专为虚拟制作（Virtual Production）和动态设计（Motion Design）场景打造。它允许设计师和开发者在编辑器中通过节点图直观地定义场景中各种元素（如灯光、摄像机、特效、动画）的状态、状态之间的转换条件以及每个状态下需要执行的任务。

其核心解决的问题是：在复杂的虚拟制作流程中，如何高效、可靠地管理和驱动场景中多个对象的协同状态变化。传统的蓝图或C++状态机实现可能分散且难以维护，而此插件将状态逻辑集中到一个专门的图表资产中，实现了逻辑与表现的分离，并提供了编译优化、事件驱动、任务系统等高级功能。

## 使用场景

- **虚拟制片（Virtual Production）**：在LED墙拍摄中，根据拍摄脚本或导演指令，自动切换场景的灯光氛围、背景内容、摄像机预设等。
- **动态设计（Motion Design）**：制作交互式装置艺术或展览，根据用户输入（如触摸、传感器）或时间线，驱动一系列视觉元素的动画和状态变化。
- **复杂场景编排**：管理游戏或应用中过场动画、环境事件、NPC行为等需要精确时序和条件触发的逻辑。
- **原型快速迭代**：设计师无需编写代码，即可通过拖拽节点快速搭建和测试交互逻辑原型。

## 蓝图用法

由于插件规模庞大（xlarge），蓝图API分散在多个模块中。以下是从核心模块推断出的关键蓝图节点类别：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Start State Machine` | 启动一个场景状态机实例 | `USceneStateComponent` (推测) |
| `Stop State Machine` | 停止一个场景状态机实例 | `USceneStateComponent` (推测) |
| `Send Event` | 向状态机发送一个自定义事件，触发状态转换 | `USceneStateComponent` (推测) |
| `Get Current State` | 获取状态机当前所处的状态名称 | `USceneStateComponent` (推测) |

### 使用示例（蓝图描述）

1.  **创建状态机资产**：在内容浏览器中右键，选择 `Miscellaneous` -> `Scene State Machine` 创建一个新的状态机资产。
2.  **编辑状态机**：双击打开资产，进入专用的状态机图表编辑器。从右键菜单添加“状态节点”、“转换节点”、“任务节点”等。
3.  **连接组件**：在场景中放置一个 `SceneStateComponent`（或类似组件），在其细节面板中指定要使用的状态机资产。
4.  **蓝图控制**：在关卡蓝图或角色蓝图中，获取该组件的引用，调用 `Start State Machine` 节点来启动逻辑。通过 `Send Event` 节点发送事件来驱动状态跳转。

## C++ 用法

### 头文件引入

```cpp
#include “SceneStateMachineCompiler.h”
#include “ISceneStateMachineCompilerContext.h”
```

### 基本用法

此插件的核心C++接口主要用于**扩展编译器**或**创建自定义任务**。以下示例展示了如何实现一个编译器上下文接口，这是与状态机编译器交互的关键。

```cpp
// 来源：基于 ISceneStateMachineCompilerContext.h 推断的用法
#include “ISceneStateMachineCompilerContext.h”
#include “SceneStateTemplateData.h”

class FMyStateMachineCompilerContext : public UE::SceneState::Editor::IStateMachineCompilerContext
{
public:
    virtual USceneStateTemplateData* GetTemplateData() override
    {
        // 返回用于存储编译后数据的模板对象
        return MyTemplateData;
    }

    virtual UE::SceneState::Editor::FTransitionGraphCompileResult CompileTransitionGraph(USceneStateTransitionGraph* InTransitionGraph) override
    {
        // 实现转换图的编译逻辑
        UE::SceneState::Editor::FTransitionGraphCompileResult Result;
        Result.ReturnCode = UE::SceneState::Editor::ETransitionGraphCompileReturnCode::Success;
        // ... 编译逻辑 ...
        return Result;
    }

private:
    USceneStateTemplateData* MyTemplateData;
};
```

### 进阶用法

结合 `FStateMachineCompiler` 和自定义的编译器上下文，可以程序化地编译一个状态机图。

```cpp
// 来源：基于 SceneStateMachineCompiler.h 推断的用法
#include “SceneStateMachineCompiler.h”
#include “SceneStateMachineGraph.h”

void CompileMyStateMachineGraph(USceneStateMachineGraph* InGraph)
{
    // 1. 创建自定义的编译器上下文
    FMyStateMachineCompilerContext CompilerContext;

    // 2. 实例化状态机编译器
    UE::SceneState::Editor::FStateMachineCompiler Compiler(InGraph, CompilerContext);

    // 3. 执行编译，获得运行时状态机数据
    FSceneStateMachine RuntimeStateMachine = Compiler.Compile();

    // 4. 将 RuntimeStateMachine 用于运行时执行或保存
    // ...
}
```

## Demo 示例

一个最小化的编译器上下文实现示例。

**MyStateMachineContext.h**
```cpp
#pragma once

#include “ISceneStateMachineCompilerContext.h”
#include “UObject/ObjectMacros.h”

class USceneStateTemplateData;
class UMyStateMachineContext : public UObject, public UE::SceneState::Editor::IStateMachineCompilerContext
{
    GENERATED_BODY()

public:
    UMyStateMachineContext();

    // IStateMachineCompilerContext 接口
    virtual USceneStateTemplateData* GetTemplateData() override;
    virtual UE::SceneState::Editor::FTransitionGraphCompileResult CompileTransitionGraph(USceneStateTransitionGraph* InTransitionGraph) override;

private:
    UPROPERTY()
    TObjectPtr<USceneStateTemplateData> TemplateData;
};
```

**MyStateMachineContext.cpp**
```cpp
#include “MyStateMachineContext.h”
#include “SceneStateTemplateData.h”
#include “SceneStateTransitionGraph.h”

UMyStateMachineContext::UMyStateMachineContext()
{
    TemplateData = CreateDefaultSubobject<USceneStateTemplateData>(TEXT(“TemplateData”));
}

USceneStateTemplateData* UMyStateMachineContext::GetTemplateData()
{
    return TemplateData;
}

UE::SceneState::Editor::FTransitionGraphCompileResult UMyStateMachineContext::CompileTransitionGraph(USceneStateTransitionGraph* InTransitionGraph)
{
    UE::SceneState::Editor::FTransitionGraphCompileResult Result;
    // 简单示例：假设所有转换图都编译成功
    Result.ReturnCode = UE::SceneState::Editor::ETransitionGraphCompileReturnCode::Success;
    // 在实际实现中，这里需要解析 InTransitionGraph 的节点和引脚，生成编译后的事件和属性名
    return Result;
}
```

## 模块依赖

从模块名称和功能推断，使用此插件（特别是其编辑器功能）可能需要依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `SceneState` | 核心运行时数据结构和执行逻辑 |
| `SceneStateBinding` | 处理状态机与场景对象之间的数据绑定 |
| `SceneStateBlueprint` | 集成蓝图系统，支持蓝图定义的任务和事件 |
| `SceneStateEvent` | 定义和处理状态机事件 |
| `SceneStateGameplay` | 与 GameplayAbilitySystem 或类似游戏逻辑框架集成 |
| `SceneStateMachineGraph` | 状态机图表的编辑器数据结构和资产类型 |
| `SceneStateTasks` | 内置任务库（如播放动画、设置材质参数等） |

## 维护状态

### 近期更新

```
- 2025-10-03 26c5be73ff3d Motion Design Scene State: fixed issue where uobjects instanced to the generated class and saved in the shared struct were getting marked as unreachable and garbage collected. This was done by changing the template data from being a struct (was being used as a shared struct) to a uobject. This uobject approach has the benefit that task uobjects can now be outered to the template data uobject directly rather than the owning class.
- 2025-10-03 82b738139aa2 Motion Design Scene State: removed unused interface function. Blueprint (if any) is automatically gotten from the graph.
- 2025-10-03 b660852deaec Motion Design Scene State: moved the generated class scene state data to its own struct to decouple compilers and executors from the generated class. This is done to allow to build unit tests without needing to deal with the generated class, and only use this template data struct.
```

### 维护评价

- **活跃维护**：插件创建于2025年4月，最近一次更新在2025年10月，且更新内容涉及核心架构优化（修复UObject垃圾回收问题、解耦编译器与生成类），表明项目处于**积极开发和优化阶段**。
- **实验性状态**：`.uplugin` 中 `IsBetaVersion=true`，且分类为 `Experimental`，说明API和功能可能在未来版本中发生变化，不建议在需要长期稳定性的生产项目中直接使用。
- **推荐使用**：对于虚拟制作、动态设计等前沿领域的**原型开发、内部工具或技术预研**，此插件提供了强大且直观的状态管理方案，值得尝试和关注。但需注意其“实验性”标签，做好应对API变更的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/SceneState)
- [官方文档]() (暂无)
- [测试用例]() (路径待确认，可能在 `Engine/Tests/` 下)