# Motion Design

> Compositing, designer and broadcasting tool.
Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（工具、资产、蓝图逻辑） |
| 模块 | `Avalanche` (Runtime), `AvalancheAttribute` (Runtime), `AvalancheAttributeEditor` (Runtime), `AvalancheCamera` (Runtime), `AvalancheComponentVisualizers` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), `AvalancheEditorCore` (Runtime), `AvalancheEffectors` (Runtime), `AvalancheEffectorsEditor` (Runtime), `AvalancheFunctionalTest` (Runtime), `AvalancheInteractiveTools` (Runtime), `AvalancheInteractiveToolsRuntime` (Runtime), `AvalancheLevelViewport` (Runtime), `AvalancheMRQ` (Runtime), `AvalancheMRQEditor` (Runtime), `AvalancheMask` (Runtime), `AvalancheMaskEditor` (Runtime), `AvalancheMaterial` (Runtime), `AvalancheMedia` (Runtime), `AvalancheMediaEditor` (Runtime), `AvalancheModifiers` (Runtime), `AvalancheModifiersEditor` (Runtime), `AvalancheOutliner` (Runtime), `AvalanchePropertyAnimator` (Runtime), `AvalanchePropertyAnimatorEditor` (Runtime), `AvalancheRemoteControl` (Runtime), `AvalancheRemoteControlEditor` (Runtime), `AvalancheSVGEditor` (Runtime), `AvalancheSceneRig` (Runtime), `AvalancheSceneRigEditor` (Runtime), `AvalancheSceneTree` (Runtime), `AvalancheSequence` (Runtime), `AvalancheSequencer` (Runtime), `AvalancheShapes` (Runtime), `AvalancheShapesEditor` (Runtime), `AvalancheTag` (Runtime), `AvalancheTagEditor` (Runtime), `AvalancheText` (Runtime), `AvalancheTextEditor` (Runtime), `AvalancheTransition` (Runtime), `AvalancheTransitionEditor` (Runtime), `AvalancheViewport` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Avalanche 是 UE5 中面向**虚拟制作（Virtual Production）** 和 **动态广播图形（Motion Graphics）** 的综合性工具套件。它并非单一功能插件，而是一个包含数十个模块的庞大生态系统，旨在提供一套完整的“动态设计”工作流。

其核心目标是解决在实时广播、虚拟制片等场景下，需要**程序化、数据驱动地创建、合成和播放复杂动态图形**的需求。它整合了：
- **场景合成与管理**：通过 `SceneTree`, `SceneRig`, `Transition` 等模块管理场景层级和切换。
- **程序化内容创建**：通过 `Shapes`, `Text`, `SVG`, `Modifiers`, `Effectors`, `Mask` 等模块生成和操控几何体、文本、材质等。
- **动画与控制**：通过 `PropertyAnimator`, `Sequencer` 模块进行属性动画，并通过 `RemoteControl` 实现远程参数控制。
- **媒体与输出**：通过 `Media`, `MRQ` 模块集成媒体输入/输出和电影渲染队列。
- **编辑器集成**：通过 `Editor`, `Outliner`, `Viewport`, `InteractiveTools` 等模块提供自定义编辑器界面和工具。

简而言之，Motion Design 是 Epic 为广播、现场活动和虚拟制片中的动态图形设计师提供的一个**一体化解决方案**，使其能够在 UE5 中以类似 After Effects 或 Cinema 4D 的方式高效工作。

## 使用场景

- 你正在为**电视广播、网络直播或现场活动**设计实时播放的动态图形（Lower Thirds、Logo 动画、数据可视化等）。
- 你在进行**虚拟制片**，需要实时生成和操控复杂的背景、灯光或特效元素。
- 你需要基于**外部数据（如股票、体育比分）** 驱动场景中元素的变化。
- 你需要一个高度**可扩展、数据驱动**的工作流来创建和管理大量相似的动画或场景变体。
- 你需要通过**Sequencer或远程控制器**精确编排和播放复杂的动画序列。

## 蓝图用法

本文档聚焦于 `AvalancheTransition` 子模块，它负责管理场景（Level）之间的过渡逻辑。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetTransitionContext` | 从上下文对象获取当前的过渡上下文信息（包含过渡场景、类型、层级）。 | `UAvaTransitionLibrary` |
| `IsTransitionActiveInLayers` | 检查指定的过渡层级中是否有活跃的过渡。可过滤过渡类型（进/出）和比较特定层级。 | `UAvaTransitionLibrary` |
| `GetTransitionType` | 获取当前正在进行的过渡类型（`In` 或 `Out`）。 | `UAvaTransitionLibrary` |
| `AreScenesTransitioning` | 检查指定层级中是否有场景正在过渡（忽略即将被丢弃的场景）。 | `UAvaTransitionLibrary` |
| `GetTransitionBehavior` | 获取与当前上下文关联的过渡行为接口（`IAvaTransitionBehavior`）。 | `UAvaTransitionLibrary` |
| `GetTransitionTree` | 获取与当前上下文关联的过渡树资产。 | `UAvaTransitionLibrary` |
| `GetTransitionLayer` | 获取此过渡行为所使用的过渡层级标签。 | `IAvaTransitionBehavior` |
| `GetInstancingMode` | 获取此过渡行为的实例化模式（创建新实例或重用旧实例）。 | `IAvaTransitionBehavior` |

### 使用示例（蓝图描述）

1.  **创建过渡行为**：在需要参与过渡的 Level 中放置 `AAvaTransitionBehaviorActor` 或创建一个实现 `IAvaTransitionBehavior` 接口的自定义 Actor。为其分配一个 `UAvaTransitionTree` 资产和一个代表其所属层的标签（`FAvaTagHandle`）。
2.  **编写过渡逻辑**：在 `UAvaTransitionTree` 资产的 State Tree 编辑器中，使用 Motion Design 提供的条件（`AvaTransitionCondition`）和任务（`AvaTransitionTask`）来编写逻辑。例如：
    - **条件**：“当我的过渡类型是‘进’时”、“当同一层中另一个场景正在过渡时”。
    - **任务**：“延迟 2 秒”、“等待本层其他场景完成过渡”、“丢弃自身场景”。
3.  **在蓝图中查询状态**：在其他蓝图（如游戏逻辑或 UI 控制器）中，使用 `Get Transition Context` 节点获取当前过渡信息，然后用 `Is Transition Active In Layers` 节点检查特定状态，以驱动其他逻辑（如显示加载界面）。
4.  **触发过渡**：系统通过 `Avalanche` 的场景管理层或蓝图逻辑触发层级间的场景切换时，会自动为相关 Level 中的过渡行为创建 `FAvaTransitionBehaviorInstance` 并由 `FAvaTransitionExecutor` 执行状态树。

## C++ 用法

### 头文件引入

```cpp
#include "AvalancheTransition/Public/AvaTransitionLibrary.h"
#include "AvalancheTransition/Public/AvaTransitionSubsystem.h"
#include "AvalancheTransition/Public/Behavior/IAvaTransitionBehavior.h"
#include "AvalancheTransition/Public/Execution/AvaTransitionExecutorBuilder.h"
#include "AvalancheTransition/Public/Tasks/AvaTransitionDelayTask.h"
```

### 基本用法

查询当前过渡上下文和状态。
```cpp
// 在一个 UObject* ContextObject（通常为 StateTree 节点或 Actor）的蓝图函数中
void UMyLibrary::CheckTransitionStatus(UObject* ContextObject)
{
    if (const FAvaTransitionContext* Context = UAvaTransitionLibrary::GetTransitionContext(ContextObject))
    {
        // 获取过渡类型
        EAvaTransitionType Type = Context->GetTransitionType();
        // 获取过渡层
        FAvaTagHandle Layer = Context->GetTransitionLayer();

        // 使用子系统查询活跃实例
        if (UWorld* World = ContextObject->GetWorld())
        {
            if (UAvaTransitionSubsystem* Subsystem = World->GetSubsystem<UAvaTransitionSubsystem>())
            {
                if (IAvaTransitionBehavior* Behavior = Subsystem->GetTransitionBehavior())
                {
                    // 使用行为接口
                }
            }
        }
    }
}
```
*来源: `Public/AvaTransitionLibrary.h`, `Public/AvaTransitionSubsystem.h`*

### 进阶用法

使用构建器（Builder）模式手动创建和启动一个过渡执行器。
```cpp
void StartCustomTransition(UWorld* InWorld)
{
    UAvaTransitionSubsystem* Subsystem = InWorld->GetSubsystem<UAvaTransitionSubsystem>();
    if (!Subsystem) return;

    // 1. 准备进入和退出的行为实例 (FAvaTransitionBehaviorInstance)
    FAvaTransitionBehaviorInstance EnterInstance;
    EnterInstance.SetBehavior(/* 某个 IAvaTransitionBehavior 实现 */)
                 .CreateScene<FAvaTransitionPreviewScene>(...); // 为场景创建数据

    FAvaTransitionBehaviorInstance ExitInstance;
    ExitInstance.SetBehavior(/* 另一个 IAvaTransitionBehavior */)
                .CreateScene<FAvaTransitionPreviewScene>(...);

    // 2. 使用构建器组装
    FAvaTransitionExecutorBuilder Builder;
    Builder.SetContextName(TEXT("MyCustomTransition"))
           .AddEnterInstance(EnterInstance)
           .AddExitInstance(ExitInstance)
           .SetOnFinished(FSimpleDelegate::CreateLambda([](){
                UE_LOG(LogTemp, Log, TEXT("Transition Finished!"));
           }));

    // 3. 构建并启动执行器
    TSharedRef<IAvaTransitionExecutor> Executor = Builder.Build(*Subsystem);
    Executor->Start();
}
```
*来源: `Public/Execution/AvaTransitionExecutorBuilder.h`, `Public/Behavior/AvaTransitionBehaviorInstance.h`*

## Demo 示例

一个自定义过渡任务（Task）的简单实现，它在进入状态时记录日志。

**MyTransitionTask.h**
```cpp
#pragma once
#include "AvalancheTransition/Public/Tasks/AvaTransitionTask.h"

USTRUCT(DisplayName = "Log My Transition", Category="Transition Logic")
struct FMyTransitionTask : public FAvaTransitionTask
{
    GENERATED_BODY()

    virtual EStateTreeRunStatus EnterState(FStateTreeExecutionContext& InContext, const FStateTreeTransitionResult& InTransition) const override;
};
```

**MyTransitionTask.cpp**
```cpp
#include "MyTransitionTask.h"

EStateTreeRunStatus FMyTransitionTask::EnterState(FStateTreeExecutionContext& InContext, const FStateTreeTransitionResult& InTransition) const
{
    UE_LOG(LogTemp, Warning, TEXT("My Custom Transition Task Entered!"));
    // 任务立即完成
    return EStateTreeRunStatus::Succeeded;
}
```

然后你可以在 `UAvaTransitionTree` 的 State Tree 中使用这个 `FMyTransitionTask` 节点。

## 模块依赖

使用 `AvalancheTransition` 模块本身没有特殊依赖，它是 `Avalanche` 插件的一部分，依赖于插件提供的其他核心模块（如 `AvalancheTag` 用于标签系统）。在你的项目模块 `.Build.cs` 中，你需要添加对它的依赖。

```csharp
// YourModule.Build.cs
PublicDependencyModuleNames.Add("AvalancheTransition");
```

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将场景设置、大纲等标签页移至独立分组 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 使用节目单页面设置时添加 MRQ 分析 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 在演出控制工具栏添加页面加载选项（全部、下一个、已选） |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 添加项目设置以强制禁用 Text3D 和形状的碰撞 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口：通过通知客户端其关联或取消关联来重构必要的代码复制 |

### 维护评价

**AvalancheTransition** 模块是 **Motion Design** 插件的一部分。该插件在 2025 年 5 月从实验性分类迁移至虚拟制作分类，标志着其功能的成熟和重要性提升。

- **年龄与状态**：插件本身约 1 年历史，但很多底层模块和功能源自更早的实验性开发阶段，技术上相对成熟。
- **活跃度**：从近期提交看，Motion Design 插件整体仍在**积极开发**中，但提交主要集中在编辑器 UI、设置、分析等外围功能。`AvalancheTransition` 模块的核心架构（基于 State Tree）在近几个月没有大的改动，表明其逻辑层已趋于稳定。
- **推荐度**：**推荐使用**。作为 Epic 官方维护的虚拟制作核心工具链，其代码质量和与引擎的集成度很高。`AvalancheTransition` 提供的基于 State Tree 的场景过渡系统，是构建复杂、数据驱动广播图形工作流的关键组件。尽管可能需要一些学习成本来理解 State Tree 和其特定的任务/条件体系，但它提供了一套强大且可扩展的解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/motion-design-in-unreal-engine/)（链接为示例，Motion Design 文档通常在虚拟制作或广播相关内容下）