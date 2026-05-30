# Motion Design Scene State

> （Description from .uplugin）

| 属性 | 值 |
|---|---|
| 中文名 | 场景状态 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、编辑器工具） |
| 模块 | `SceneState` (Runtime), `SceneStateBinding` (Runtime), `SceneStateBlueprint` (Runtime), `SceneStateBlueprintEditor` (Runtime), `SceneStateEditor` (Runtime), `SceneStateEvent` (Runtime), `SceneStateEventEditor` (Runtime), `SceneStateEventGraph` (Runtime), `SceneStateGameplay` (Runtime), `SceneStateGameplayEditor` (Runtime), `SceneStateMachineEditor` (Runtime), `SceneStateMachineGraph` (Runtime), `SceneStateTasks` (Runtime), `SceneStateTransitionGraph` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/SceneState) | |

## 用途

**Scene State** 插件为 **Motion Design（运动设计）** 或 **Virtual Production（虚拟制片）** 工作流提供了一个强大的、基于蓝图的**状态机系统**。它旨在解决以下问题：
- **复杂场景逻辑的可视化管理**：允许美工、灯光师、特效师通过直观的蓝图节点图来编排复杂的场景状态、过渡和事件，而无需编写 C++ 代码。
- **动态数据绑定**：提供了一套灵活的属性绑定（Binding）和事件（Event）系统，让场景状态机的逻辑可以方便地与场景中的各种参数（如材质参数、Actor 变换、蓝图变量等）进行双向驱动。
- **编辑器集成与调试**：提供了完整的编辑器模块，用于创建、编辑和调试这些场景状态蓝图，并集成了蓝图编译器、属性细节自定义和专用的调试视图。

该插件的核心是一个**状态机（State Machine）**，每个状态可以包含一系列**任务（Tasks）**，状态之间通过**过渡（Transitions）** 进行切换，整个流程通过蓝图进行可视化编程。

## 使用场景

- 你需要为虚拟制片中的一个**灯光秀**或**动态场景效果**编程复杂的播放顺序和触发逻辑。
- 你在构建一个**建筑可视化**项目，需要根据用户交互动态切换场景的昼夜、季节或展示模式。
- 你需要在**虚拟拍摄（Virtual Production）** 现场快速调整场景元素的状态（如切换背景、控制道具动画），并希望通过直观的节点图来管理。
- 你希望将场景中的多个属性（如灯光强度、后期处理参数）组织成一个有逻辑的状态流程。

## 蓝图用法

该插件主要提供的是**编辑器端**的蓝图资产创建和编辑功能。其运行时节点（如 `SceneStateObject` 的蓝图接口）通常用于在游戏逻辑中触发或查询状态。核心的编辑体验在 **Scene State Blueprint Editor** 中。

### 核心节点（编辑器与运行时概念）

| 节点/概念 | 说明 | 所在模块/类 |
|---|---|---|
| **State Machine** | 状态机图，是整个逻辑的容器。 | `SceneStateBlueprint`, `USceneStateMachineGraph` |
| **State** | 状态机中的一个状态，包含要执行的任务。 | `USceneStateNode` (图节点) |
| **Task** | 在状态中执行的具体动作或子逻辑。 | `FSceneStateTask`, `USceneStateTaskNode` |
| **Transition** | 状态之间的转换条件和逻辑。 | `USceneStateTransitionNode`, `USceneStateTransitionGraph` |
| **Event** | 用于触发状态机内部逻辑的事件。 | `FSceneStateEventTemplate` |
| **Binding** | 连接任务参数与场景中数据的桥梁。 | `FSceneStateBinding` |

### 使用示例（蓝图描述）

1.  **创建资产**：在内容浏览器中右键，选择 “Animation > Scene State Blueprint”。
2.  **编辑状态机**：双击打开蓝图，会看到一个类似动画蓝图的状态机编辑器。
3.  **添加状态**：在图表中右键添加 “State” 节点。
4.  **编辑状态细节**：选中状态节点，在细节面板中添加 “Tasks”（例如 “PlayLevelSequence” 任务）。
5.  **配置绑定**：选中任务，在细节面板的属性上点击 “绑定” 按钮，可以从场景上下文中选择要驱动的变量。
6.  **创建过渡**：从一个状态拖拽到另一个状态创建过渡，并双击过渡线编辑其条件图表。
7.  **调试**：使用编辑器提供的专用调试视图和控制面板来实时观察和控制状态机的运行。

## C++ 用法

该插件的 C++ 用法主要集中在**扩展编辑器**和**自定义任务**。从 `SceneStateBlueprintEditor` 模块的头文件可以看出其架构。

### 头文件引入

```cpp
#include "ISceneStateBlueprintEditorModule.h"
#include "ISceneStateContextEditor.h"
```

### 基本用法（获取编辑器模块）

```cpp
// 获取 SceneStateBlueprintEditor 模块实例
if (UE::SceneState::Editor::IBlueprintEditorModule::IsLoaded())
{
    UE::SceneState::Editor::IBlueprintEditorModule& EditorModule = UE::SceneState::Editor::IBlueprintEditorModule::Get();
    // 可以使用 EditorModule 进行操作，例如注册上下文编辑器
}
```

### 进阶用法（注册上下文编辑器）

为你的自定义 `UObject` 定义编辑器逻辑。

```cpp
// 假设你有一个自定义的上下文对象类
UCLASS()
class UMyCustomContextObject : public UObject
{
    // ...
};

// 实现 IContextEditor 接口
class FMyCustomContextEditor : public UE::SceneState::Editor::IContextEditor
{
public:
    virtual void GetContextClasses(TArray<TSubclassOf<UObject>>& OutContextClasses) const override
    {
        OutContextClasses.Add(UMyCustomContextObject::StaticClass());
    }

    virtual TSharedPtr<SWidget> CreateViewWidget(const FContextParams& InContextParams) const override
    {
        // 创建并返回用于调试视图的自定义控件
        return SNew(STextBlock).Text(FText::FromString(TEXT("My Custom View")));
    }
};

// 在模块启动时注册
void FMyGameModule::StartupModule()
{
    if (UE::SceneState::Editor::IBlueprintEditorModule::IsLoaded())
    {
        auto ContextEditor = MakeShared<FMyCustomContextEditor>();
        UE::SceneState::Editor::IBlueprintEditorModule::Get().RegisterContextEditor(ContextEditor);
    }
}
```

## Demo 示例

一个最小的 C++ 示例，演示如何在自己的模块中检查并获取 Scene State 编辑器模块。

**MyGameModule.h**
```cpp
#pragma once

#include "Modules/ModuleManager.h"

class FMyGameModule : public IModuleInterface
{
public:
    /** IModuleInterface implementation */
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

**MyGameModule.cpp**
```cpp
#include "MyGameModule.h"
#include "ISceneStateBlueprintEditorModule.h"

#define LOCTEXT_NAMESPACE "FMyGameModule"

void FMyGameModule::StartupModule()
{
    // 此处可以放置模块启动时的初始化代码
    UE_LOG(LogTemp, Log, TEXT("MyGameModule Started."));

    // 检查 Scene State 编辑器模块是否已加载
    if (UE::SceneState::Editor::IBlueprintEditorModule::IsLoaded())
    {
        UE_LOG(LogTemp, Log, TEXT("SceneStateBlueprintEditor module is loaded and available."));
        // 你可以在此处与它交互，例如注册自定义内容
    }
}

void FMyGameModule::ShutdownModule()
{
    // 此处可以放置模块关闭时的清理代码
    UE_LOG(LogTemp, Log, TEXT("MyGameModule Shutdown."));
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyGameModule, MyGame)
```

## 模块依赖

要使用此插件，你的模块需要依赖以下模块（基于插件的模块结构推断）：

| 模块 | 用途 |
|---|---|
| `SceneState` | 核心运行时状态机、任务和绑定逻辑 |
| `SceneStateBlueprint` | 蓝图资产相关的运行时类 |
| `SceneStateBinding` | 属性绑定系统 |
| `SceneStateEvent` | 事件系统 |
| `SceneStateBlueprintEditor` | 蓝图编辑器核心（仅编辑器使用） |

**注意**：该插件包含大量 `Editor` 后缀的模块（如 `SceneStateEditor`, `SceneStateEventEditor` 等），这些通常只在编辑器环境下使用，不需要在运行时模块中依赖。依赖关系应遵循 UE5 标准实践，通过 `Build.cs` 文件声明。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构视口相关代码，改进客户端关联/断开通知机制。 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回滚了一个变更。 |
| 2026-05-14 | `9ede83f2` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | （与第一条相同的改动，可能是不同分支的合并） |
| 2026-04-17 | `6e111b5d` | Motion Design Scene State: fixed issues with bindings not checking for null event payload struct (op | 修复了绑定系统在检查事件负载结构体时未处理空值的问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将部分日志宏从 UE_LOG 迁移到 UE_LOGF。 |

### 维护评价

- **状态**：**实验性，但活跃维护中**。
- **分析**：
    - 插件创建时间较短（约1年），且标记为 `IsBetaVersion: true`，属于实验性功能。
    - **最近更新非常活跃**（最后一次提交在2026年5月），包括功能重构、Bug修复和代码改进。
    - 这是一个由 Epic Games 官方维护的虚拟制片流程核心工具，前景明确。
- **限制**：作为实验性功能，其API和功能可能会在未来的引擎版本中发生变化。
- **推荐**：**推荐在虚拟制片和运动设计项目中试用**。它提供了强大的可视化编程能力，但需注意其“实验性”状态，生产环境使用前应充分测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/SceneState)
- [官方文档]() (暂无)
- [测试用例]() (根据信息暂未定位到公开测试文件路径)