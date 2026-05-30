# Motion Design Scene State

> Motion Design Scene State

| 属性 | 值 |
|---|---|
| 中文名 | 运动设计场景状态 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资源） |
| 模块 | `SceneState` (Runtime), `SceneStateBinding` (Runtime), `SceneStateBlueprint` (Runtime), `SceneStateBlueprintEditor` (Runtime), `SceneStateEditor` (Runtime), `SceneStateEvent` (Runtime), `SceneStateEventEditor` (Runtime), `SceneStateEventGraph` (Runtime), `SceneStateGameplay` (Runtime), `SceneStateGameplayEditor` (Runtime), `SceneStateMachineEditor` (Runtime), `SceneStateMachineGraph` (Runtime), `SceneStateTasks` (Runtime), `SceneStateTransitionGraph` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/SceneState) | |

## 用途

SceneState 插件是一个专为 Motion Design（运动设计）工作流设计的场景状态管理和逻辑执行框架。它并非简单的状态记录，而是一套完整的、基于状态机（State Machine）的交互式场景控制系统。

该插件解决的核心问题是：在虚拟制片（Virtual Production）的 Motion Design 环境下，如何让美术、动画师和设计师能够通过可视化、数据驱动的方式，而非编写大量 C++ 代码，来编排和控制复杂场景中对象的动画序列、交互逻辑和事件响应。它抽象了场景状态（如动画播放、材质变化、物体可见性）与触发逻辑（如时间、用户输入、外部事件）之间的关系，并通过蓝图和数据资产（Data Asset）进行配置。

## 使用场景

- 你在为一场虚拟演唱会或电影拍摄预览（Previz）设计复杂的视觉效果序列，需要根据音乐节拍或导演指令，精确控制场景中灯光、粒子和动画的触发与切换。
- 你需要为一个产品展示动画创建交互式原型，用户通过按钮或传感器（如 Leap Motion）控制展示流程，不同交互对应不同的动画状态和过渡。
- 你在开发一个基于虚拟制片的实时图形引擎（如电视新闻虚拟演播室），需要快速编排主持人、虚拟场景元素和实时数据之间的联动关系。

## 蓝图用法

此插件提供了一套基于数据资产和状态机的蓝图可配置系统。其核心在于通过编辑器模块创建和编辑状态机蓝图资产，并在运行时由 `SceneState` 运行时模块驱动。以下是从提供的编辑器模块头文件中提取的、与蓝图资产创建相关的核心概念。

### 核心概念

| 概念 | 说明 | 所在类/接口 |
|---|---|---|
| 任务描述 (Task Description) | 描述一个可在状态机节点中执行的任务（如播放动画、发送事件）的编辑器元数据，包括显示名称、工具提示、双击跳转目标等。 | `FSceneStateTaskDesc` |
| 任务描述注册表 (Task Desc Registry) | 全局单例，负责收集并缓存所有可用的任务描述（`FSceneStateTaskDesc`），供编辑器查询和展示。 | `FSceneStateTaskDescRegistry` |

### 使用示例（蓝图/数据资产配置流程）

1.  **创建任务 (Task)**：首先，开发者需要继承 `FSceneStateTask`（运行时任务基类）创建一个具体的任务（如 `FMyPlayAnimationTask`），并用 `USTRUCT` 宏标记。
2.  **创建任务描述 (Task Description)**：继承 `FSceneStateTaskDesc`，为上述任务创建对应的编辑器描述类（如 `FMyPlayAnimationTaskDesc`），并重写 `OnGetDisplayName`、`OnGetTooltip` 等虚函数来自定义其在状态机编辑器中的显示。
3.  **在状态机编辑器中使用**：在 Motion Design 的状态机编辑器界面中，设计师可以从任务列表（由 `FSceneStateTaskDescRegistry` 提供）中拖拽“播放动画”节点，并通过属性面板配置其参数。
4.  **运行时驱动**：在游戏或预览运行时，`SceneState` 运行时模块会解析状态机资产，实例化并执行对应的 `FSceneStateTask`，驱动场景对象执行相应操作。

## C++ 用法

此插件的 C++ API 主要用于扩展其任务系统。通过创建自定义的 Task 和 TaskDesc，你可以向状态机中添加新的可执行逻辑。

### 头文件引入

```cpp
// 引入任务描述基类
#include "Tasks/SceneStateTaskDesc.h"
```

### 基本用法：定义自定义任务描述

以下代码展示了如何为一个自定义的场景状态任务创建编辑器描述，使其能在状态机编辑器中正确显示和交互。

```cpp
// 假设你已经定义了运行时任务 FMyCustomTask (继承自 FSceneStateTask)
// MyCustomTaskDesc.h
#pragma once

#include "Tasks/SceneStateTaskDesc.h"
#include "MyCustomTaskDesc.generated.h"

USTRUCT()
struct FMyCustomTaskDesc : public FSceneStateTaskDesc
{
    GENERATED_BODY()

    // 构造函数中指定此描述所支持的任务类型
    FMyCustomTaskDesc()
    {
        // 将编辑器描述与运行时任务类型绑定
        SetSupportedTask<FMyCustomTask>();
    }

    // 重写虚函数以提供自定义的显示名称
    virtual bool OnGetDisplayName(const FSceneStateTaskDescContext& InContext, FText& OutDisplayName) const override
    {
        // 可以根据任务实例数据 (InContext.TaskData) 动态生成名称
        OutDisplayName = NSLOCTEXT("MyTask", "DisplayName", "My Custom Task");
        return true;
    }

    // 重写以提供工具提示
    virtual bool OnGetTooltip(const FSceneStateTaskDescContext& InContext, FText& OutTooltip) const override
    {
        OutTooltip = NSLOCTEXT("MyTask", "Tooltip", "Executes my custom logic on the target actor.");
        return true;
    }
};
```

### 进阶用法：监听任务数据变化

任务描述可以监听其关联任务实例数据的结构变化（例如，当任务数据中某个 `FStructId` 对应的结构体类型发生改变时），以便更新编辑器 UI 或数据。

```cpp
// 在你的自定义 TaskDesc 类中重写此方法
virtual void OnStructIdsChanged(const FSceneStateTaskDescMutableContext& InContext, const UE::SceneState::FStructIdChange& InChange) const override
{
    // InContext 提供了可修改的任务实例数据上下文
    // InChange 描述了哪个结构体 ID (StructId) 发生了变化
    Super::OnStructIdsChanged(InContext, InChange);

    // 例如，当某个被引用的资产类型改变后，你可能需要清理或更新其他依赖数据
    // const auto& NewStructType = InChange.GetNewStruct();
    // ... 更新逻辑
}
```

## Demo 示例

下面是一个自定义任务及其描述的最小示例头文件。请注意，运行时任务 (`FMyScaleTask`) 的实现未在此展示，但编辑器描述 (`FMyScaleTaskDesc`) 展示了如何将其集成到 SceneState 系统中。

```cpp
// MyScaleTask.h (Runtime Task - 仅展示结构)
#pragma once
#include "Tasks/SceneStateTask.h"
#include "MyScaleTask.generated.h"

USTRUCT()
struct FMyScaleTask : public FSceneStateTask
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere)
    FVector TargetScale = FVector(1.0f);
    // ... 其他属性和 Execute() 实现
};
```

```cpp
// MyScaleTaskDesc.h (Editor Description)
#pragma once

#include "Tasks/SceneStateTaskDesc.h"
#include "MyScaleTaskDesc.generated.h"

USTRUCT()
struct FMyScaleTaskDesc : public FSceneStateTaskDesc
{
    GENERATED_BODY()

    FMyScaleTaskDesc()
    {
        // 绑定到运行时任务类型
        SetSupportedTask<FMyScaleTask>();
    }

    // 提供编辑器显示名称
    virtual bool OnGetDisplayName(const FSceneStateTaskDescContext& InContext, FText& OutDisplayName) const override
    {
        OutDisplayName = NSLOCTEXT("ScaleTask", "Name", "Scale To");
        return true;
    }

    // 提供工具提示
    virtual bool OnGetTooltip(const FSceneStateTaskDescContext& InContext, FText& OutTooltip) const override
    {
        OutTooltip = NSLOCTEXT("ScaleTask", "Tooltip", "Scales the bound object to the target scale.");
        return true;
    }
};
```

## 模块依赖

由于未直接提供各模块的 `Build.cs` 文件，以下依赖基于模块名称和常见实践推断。使用此插件时，你的项目或模块很可能需要依赖：

| 模块 | 用途 |
|---|---|
| `SceneState` | 核心运行时模块，提供状态机执行引擎和任务系统基础 |
| `SceneStateBinding` | 提供场景对象与状态机数据绑定的运行时支持 |
| `SceneStateEvent` | 定义和管理系统事件的触发与分发 |
| `SceneStateGameplay` | 集成游戏框架（如 Gameplay Ability System）的特定逻辑 |
| `MovieScene` (推测) | 与 Sequencer 电影系统深度集成，用于时间轴驱动的状态转换 |

（注：实际依赖关系需以各模块 `Build.cs` 文件中 `PublicDependencyModuleNames` 和 `PrivateDependencyModuleNames` 为准。此插件包含大量编辑器相关模块，若仅在运行时使用，可只依赖 `SceneState`、`SceneStateBinding`、`SceneStateEvent` 等 Runtime 模块。）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit... | 视口重构：通过客户端关联/解关联通知来减少重复代码。 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回退了某个先前的更改 (CL53913857)。 |
| 2026-05-14 | `9ede83f2` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit... | 视口重构（同一主题的另一提交）。 |
| 2026-04-17 | `6e111b5d` | Motion Design Scene State: fixed issues with bindings not checking for null event payload struct (op... | 修复了事件负载结构体为空时，绑定未检查导致的崩溃问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志输出从 UE_LOG 迁移到 UE_LOGF 宏。 |

### 维护评价

- **状态**: **活跃维护中**。该插件于 2025 年 8 月创建，并于 2026 年 5 月仍在进行实质性功能更新（如视口重构）和 Bug 修复。
- **活跃度**: 近期提交频率较高，内容涉及功能重构和问题修复，表明项目正在积极开发和完善。
- **风险提示**: 虽然插件已从 `Experimental` 目录移出，但 `.uplugin` 文件中 `IsBetaVersion` 仍为 `true`，且 `Category` 为 `Experimental`，**表明它仍处于测试阶段**，API 和功能可能在未来的版本中发生变化。
- **推荐度**: 对于在虚拟制片和 Motion Design 领域有明确需求的项目，此插件是官方提供的一个前沿解决方案，值得在沙盒环境中进行原型验证。但由于其 Beta 状态，**不建议在追求稳定性的生产项目中直接依赖**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/SceneState)
- [官方文档]()（暂无）
- [测试用例]()（插件目录内未提供标准测试文件）