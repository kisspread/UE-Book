# Motion Design Scene State

> （无描述）

| 属性 | 值 |
|---|---|
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、状态定义） |
| 模块 | `SceneState` (Runtime), `SceneStateBinding` (Runtime), `SceneStateBlueprint` (Runtime), `SceneStateBlueprintEditor` (Runtime), `SceneStateEditor` (Runtime), `SceneStateEvent` (Runtime), `SceneStateEventEditor` (Runtime), `SceneStateEventGraph` (Runtime), `SceneStateGameplay` (Runtime), `SceneStateGameplayEditor` (Runtime), `SceneStateMachineEditor` (Runtime), `SceneStateMachineGraph` (Runtime), `SceneStateTasks` (Runtime), `SceneStateTransitionGraph` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/SceneState) | |

## 用途

SceneState 插件为 Unreal Engine 提供了一套完整的、用于管理和驱动场景状态的系统。它并非简单的状态机，而是一个面向虚拟制作（Virtual Production）和 Motion Design 的复杂状态管理框架。其核心目标是解决在实时渲染、LED 墙内容控制、复杂场景流程编排等场景下，如何高效、可视化地定义、触发和同步场景中的各种状态、事件和任务。

该插件通过模块化设计，将状态定义、状态机逻辑、事件系统、任务执行、蓝图集成和编辑器工具分离，旨在提供一个可扩展、可定制的场景流程控制解决方案。

## 使用场景

- **虚拟制作 (Virtual Production)**：在 LED 墙拍摄中，管理不同拍摄阶段（如场景切换、灯光预设、摄像机运动）的状态和触发逻辑。
- **Motion Design**：用于控制复杂的动态图形序列，例如根据时间、用户输入或外部信号切换不同的动画状态和视觉效果。
- **实时渲染与交互式体验**：在建筑可视化、主题公园游乐设施或交互式装置中，管理场景的交互流程和视觉反馈。
- **自动化场景测试**：定义场景状态和转换条件，用于自动化测试场景的完整性和逻辑正确性。

## 蓝图用法

由于插件处于实验阶段且主要面向编辑器扩展，直接暴露给蓝图的运行时节点相对有限。其核心价值在于通过编辑器工具（如状态机图表、事件图表）来配置状态逻辑，这些逻辑在运行时由引擎内部驱动。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetStructTooltip` | 获取指定 UStruct 的元数据 Tooltip（仅当显式设置时返回文本） | `UE::SceneState::Editor` (Editor Utils) |

### 使用示例（蓝图描述）

在蓝图中，你通常不会直接调用 SceneState 的底层函数。更常见的用法是：
1.  在编辑器中使用 SceneState 提供的专用图表（状态机图、事件图）来设计状态逻辑。
2.  将设计好的状态资产（如 `USceneStateBlueprint`）关联到场景中的 Actor 或组件。
3.  在蓝图中，通过其他系统（如 Enhanced Input、Gameplay Ability System）或自定义事件来触发状态转换或发送事件，从而间接驱动 SceneState 系统。

## C++ 用法

SceneState 的 C++ 接口主要面向插件开发者和需要深度定制状态行为的高级用户。其核心是定义和注册自定义的“任务描述”（Task Desc），以控制任务在编辑器中的显示和行为。

### 头文件引入

```cpp
#include "SceneStateEditorUtils.h"
#include "Tasks/SceneStateTaskDesc.h"
#include "Tasks/SceneStateTaskDescRegistry.h"
```

### 基本用法

创建一个自定义的任务描述，用于在编辑器中为特定的任务类型提供显示名称和工具提示。

```cpp
// MyCustomTaskDesc.h
#pragma once
#include "Tasks/SceneStateTaskDesc.h"
#include "MyCustomTaskDesc.generated.h"

USTRUCT()
struct FMyCustomTaskDesc : public FSceneStateTaskDesc
{
    GENERATED_BODY()

    FMyCustomTaskDesc()
    {
        // 指定此描述支持的任务类型
        SetSupportedTask<FMyCustomTask>();
    }

protected:
    // 重写以提供自定义显示名称
    virtual bool OnGetDisplayName(const FSceneStateTaskDescContext& InContext, FText& OutDisplayName) const override
    {
        OutDisplayName = NSLOCTEXT("MyTasks", "CustomTaskName", "我的自定义任务");
        return true;
    }

    // 重写以提供自定义工具提示
    virtual bool OnGetTooltip(const FSceneStateTaskDescContext& InContext, FText& OutDescription) const override
    {
        OutDescription = NSLOCTEXT("MyTasks", "CustomTaskTooltip", "这是一个自定义任务，用于执行特定操作。");
        return true;
    }
};
```

### 进阶用法

在模块启动时，将自定义的任务描述注册到全局注册表中，以便编辑器能够识别和使用它。

```cpp
// MyModule.cpp
#include "Tasks/SceneStateTaskDescRegistry.h"
#include "MyCustomTaskDesc.h"

void FMyModule::StartupModule()
{
    // 获取全局任务描述注册表
    FSceneStateTaskDescRegistry& Registry = const_cast<FSceneStateTaskDescRegistry&>(FSceneStateTaskDescRegistry::Get());

    // 创建并注册自定义任务描述
    TInstancedStruct<FSceneStateTaskDesc> TaskDesc;
    TaskDesc.InitializeAs<FMyCustomTaskDesc>();
    Registry.RegisterTaskDesc(FMyCustomTask::StaticStruct(), MoveTemp(TaskDesc));
}
```

## Demo 示例

以下示例展示如何创建一个简单的自定义任务及其对应的编辑器描述。

**MySimpleTask.h**
```cpp
#pragma once
#include "SceneStateTask.h"
#include "MySimpleTask.generated.h"

USTRUCT()
struct FMySimpleTask : public FSceneStateTask
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, Category = "Config")
    float Duration = 1.0f;

    // 任务执行逻辑（运行时）
    virtual void Execute(const FSceneStateExecutionContext& Context) const override;
};
```

**MySimpleTaskDesc.h**
```cpp
#pragma once
#include "Tasks/SceneStateTaskDesc.h"
#include "MySimpleTaskDesc.generated.h"

USTRUCT()
struct FMySimpleTaskDesc : public FSceneStateTaskDesc
{
    GENERATED_BODY()

    FMySimpleTaskDesc()
    {
        SetSupportedTask<FMySimpleTask>();
    }

protected:
    virtual bool OnGetDisplayName(const FSceneStateTaskDescContext& InContext, FText& OutDisplayName) const override
    {
        OutDisplayName = FText::FromString(TEXT("Simple Delay Task"));
        return true;
    }
};
```

## 模块依赖

该插件由多个模块组成，模块间存在依赖关系。对于最终用户（使用插件功能），通常不需要直接依赖这些模块。对于插件开发者或需要扩展该插件的开发者，可能需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `StructUtils` | 提供 `TInstancedStruct`, `TStructView` 等高级结构体工具，是插件数据驱动设计的基础。 |
| `SceneState` | 核心运行时模块，包含状态、任务、执行上下文等基础类型。 |
| `SceneStateEditor` | 编辑器工具模块，提供任务描述注册表、编辑器工具函数等。 |

## 维护状态

### 近期更新

```
- 94f961385e8e 2025-04-22 Motion Design: Moved scene state and data link plugins out of experimental into virtualproduction
```

### 维护评价

- **创建时间**：插件非常新，于 2025 年 4 月创建。
- **最近更新**：仅有一次记录，是将插件从 `Experimental` 分类移至 `VirtualProduction` 分类，这表明插件刚刚完成初步整合，进入虚拟制作工作流。
- **活跃度**：处于**早期开发阶段**。目前只有一次结构性迁移提交，尚无功能迭代或 bug 修复的记录。
- **已知问题/限制**：作为实验性（`IsBetaVersion=true`）插件，其 API 和功能可能不稳定，随时可能发生重大变更。文档和示例可能缺失。
- **推荐使用**：**不推荐在生产环境中使用**。适合对虚拟制作前沿技术感兴趣的开发者进行研究、原型开发和功能探索。使用前请做好应对 API 变更的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/SceneState)
- [官方文档]() （暂无）
- [测试用例]() （暂未发现公开测试用例）