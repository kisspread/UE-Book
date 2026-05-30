# Motion Design

> Compositing, designer and broadcasting tool. Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（模块化源码） |
| 模块 | `Avalanche` (Runtime), `AvalancheAttribute` (Runtime), `AvalancheAttributeEditor` (Runtime), `AvalancheCamera` (Runtime), `AvalancheComponentVisualizers` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), `AvalancheEditorCore` (Runtime), `AvalancheEffectors` (Runtime), `AvalancheEffectorsEditor` (Runtime), `AvalancheFunctionalTest` (Runtime), `AvalancheInteractiveTools` (Runtime), `AvalancheInteractiveToolsRuntime` (Runtime), `AvalancheLevelViewport` (Runtime), `AvalancheMRQ` (Runtime), `AvalancheMRQEditor` (Runtime), `AvalancheMask` (Runtime), `AvalancheMaskEditor` (Runtime), `AvalancheMaterial` (Runtime), `AvalancheMedia` (Runtime), `AvalancheMediaEditor` (Runtime), `AvalancheModifiers` (Runtime), `AvalancheModifiersEditor` (Runtime), `AvalancheOutliner` (Runtime), `AvalanchePropertyAnimator` (Runtime), `AvalanchePropertyAnimatorEditor` (Runtime), `AvalancheRemoteControl` (Runtime), `AvalancheRemoteControlEditor` (Runtime), `AvalancheSVGEditor` (Runtime), `AvalancheSceneRig` (Runtime), `AvalancheSceneRigEditor` (Runtime), `AvalancheSceneTree` (Runtime), `AvalancheSequence` (Runtime), `AvalancheSequencer` (Runtime), `AvalancheShapes` (Runtime), `AvalancheShapesEditor` (Runtime), `AvalancheTag` (Runtime), `AvalancheTagEditor` (Runtime), `AvalancheText` (Runtime), `AvalancheTextEditor` (Runtime), `AvalancheTransition` (Runtime), `AvalancheTransitionEditor` (Runtime), `AvalancheViewport` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Avalanche (Motion Design) 插件为 Unreal Editor 的 Level Editor 提供了一个专业的“动态设计”（Motion Design）工作区。它不是独立的编辑器模式，而是一套深度集成的编辑器扩展框架，专门服务于虚拟制作中的实时图形（broadcast graphics）、动态材质、文本、形状和过渡效果的设计与管理。

它解决的核心问题是：如何在 Unreal Editor 的标准 3D 视口中，为虚拟制作现场提供一个能够快速创建、编辑、组织和播放复杂动态图形序列的集成化工具集。它将图形元素作为场景中的 Actor 进行管理，并与 Sequencer、远程控制、材质设计器等子系统深度集成，实现从设计到播出的完整流程。

## 使用场景

*   **实时虚拟制作图形**：你在为虚拟演播室或现场直播设计动态图形（Lower Thirds、片头、数据可视化等）。使用 Motion Design 在 3D 世界中直接放置和动画化这些图形元素，并与摄像机跟踪数据同步。
*   **编辑器工作流定制**：你的团队需要一个高度定制的 Level Editor 界面来管理场景中的图形元素层次结构、属性和过渡。Avalanche 提供了一个可扩展的编辑器框架，可以添加自定义面板、工具栏和交互工具。
*   **Sequencer 驱动动画**：你希望将复杂的图形动画序列（如多个元素的协同运动）保存在 Sequencer 中，以便进行精确的时间线编辑和回放控制。Avalanche 的序列化模块与此紧密集成。
*   **远程控制与现场调整**：在直播或虚拟制作现场，你需要通过远程控制界面（如 Remote Control 面板或外部控制器）实时调整图形的颜色、位置、文字内容等参数。

## 蓝图用法

Avalanche 主要通过编辑器子系统和 C++ API 进行扩展，其公开的 `BlueprintCallable` 函数相对较少，主要集中在后台服务和状态查询上。大部分核心功能通过编辑器扩展和子系统在 C++ 层面使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetSelectedActors` | 获取当前选中的 Actor 列表 | `UAvaSelectionProviderSubsystem` |
| `GetActorOrientedBounds` | 获取 Actor 的定向包围盒（考虑旋转） | `UAvaBoundsProviderSubsystem` |
| `GetSelectionTransform` | 获取当前选择的变换（中心位置、第一个 Actor 的旋转） | `UAvaSelectionProviderSubsystem` |
| `GetActiveEditor` | 获取当前活动的 Motion Design 编辑器实例 | `UAvaEditorSubsystem` |

### 使用示例（蓝图描述）

1.  **获取选择信息**：在蓝图中，首先获取 `UAvaSelectionProviderSubsystem` 子系统。然后调用 `GetSelectedActors` 节点，这将返回一个 `TArray<AActor*>` 数组，包含了当前在编辑器中选中的所有 Actor。
2.  **计算选择边界**：获取 `UAvaBoundsProviderSubsystem` 子系统。对于选中的某个 Actor，调用 `CacheActorOrientedBounds` 缓存其边界，然后调用 `GetActorOrientedBounds` 来获取其精确的定向包围盒数据（`FOrientedBox`），用于布局计算。

## C++ 用法

Avalanche 的核心功能通过子系统（Subsystem）和接口暴露，便于其他模块集成和扩展。

### 头文件引入

```cpp
#include "AvalancheEditorCore.h" // 核心编辑器子系统
#include "Bounds/AvaBoundsProviderSubsystem.h"
#include "Selection/AvaSelectionProviderSubsystem.h"
#include "IAvaEditorSubsystem.h" // 编辑器子系统接口
```

### 基本用法

从代码结构推断，获取选择信息并计算边界是常见操作。
*来源文件：`Public/Selection/AvaSelectionProviderSubsystem.h`, `Public/Bounds/AvaBoundsProviderSubsystem.h`*

```cpp
// 1. 获取世界子系统（假设在具有有效世界的上下文中，如编辑器工具或另一个子系统）
UAvaSelectionProviderSubsystem* SelectionSubsystem = World->GetSubsystem<UAvaSelectionProviderSubsystem>();
UAvaBoundsProviderSubsystem* BoundsSubsystem = World->GetSubsystem<UAvaBoundsProviderSubsystem>();

if (SelectionSubsystem && BoundsSubsystem)
{
    // 2. 获取当前选中的 Actor
    TConstArrayView<TWeakObjectPtr<AActor>> SelectedActors = SelectionSubsystem->GetSelectedActors();

    if (!SelectedActors.IsEmpty())
    {
        // 3. 取第一个 Actor（示例）
        AActor* FirstSelectedActor = SelectedActors[0].Get();

        if (FirstSelectedActor)
        {
            // 4. 缓存该 Actor 的定向边界（世界空间）
            BoundsSubsystem->CacheActorOrientedBounds(FirstSelectedActor);

            // 5. 获取边界数据
            FOrientedBox OrientedBounds;
            if (BoundsSubsystem->GetActorOrientedBounds(FirstSelectedActor, OrientedBounds))
            {
                // 使用 OrientedBounds 进行布局计算...
                FVector Center = OrientedBounds.Center;
            }
        }
    }
}
```

### 进阶用法：使用编辑器子系统

要访问正在运行的 Motion Design 编辑器实例及其扩展，需使用 `UAvaEditorSubsystem`。
*来源文件：`Public/AvaEditorSubsystem.h`, `Public/IAvaEditor.h`*

```cpp
// 获取编辑器子系统
UAvaEditorSubsystem* EditorSubsystem = World->GetSubsystem<UAvaEditorSubsystem>();

if (EditorSubsystem)
{
    // 获取活动的编辑器实例
    TSharedPtr<IAvaEditor> ActiveEditor = EditorSubsystem->GetActiveEditor();

    if (ActiveEditor.IsValid())
    {
        // 通过模板函数查找特定的编辑器扩展
        // 假设你有一个自定义的扩展类型 UMyCustomExtension : public IAvaEditorExtension
        TSharedPtr<IAvaEditorExtension> FoundExtension = ActiveEditor->FindExtension<UMyCustomExtension>();

        if (FoundExtension.IsValid())
        {
            // 与你的自定义扩展交互...
            UMyCustomExtension* MyExt = StaticCast<UMyCustomExtension*>(FoundExtension.Get());
            // MyExt->DoSomething();
        }

        // 获取编辑器的命令列表，用于绑定快捷键
        TSharedPtr<FUICommandList> CommandList = ActiveEditor->GetCommandList();
        if (CommandList.IsValid())
        {
            // 可以在此绑定更多命令...
        }
    }
}
```

## Demo 示例

一个最小的示例，展示如何在编辑器工具中集成并查询 Motion Design 的选择状态。

**MyMotionDesignTool.h**
```cpp
// MyMotionDesignTool.h
#pragma once

#include "CoreMinimal.h"
#include "AvalancheEditorCore.h" // 引入 Avalanche 编辑器核心

class FMyMotionDesignTool
{
public:
    void LogSelectionInfo(UWorld* InWorld);

private:
    // 缓存获取到的子系统指针
    TWeakObjectPtr<UAvaSelectionProviderSubsystem> CachedSelectionSubsystem;
};
```

**MyMotionDesignTool.cpp**
```cpp
// MyMotionDesignTool.cpp
#include "MyMotionDesignTool.h"
#include "Selection/AvaSelectionProviderSubsystem.h"

void FMyMotionDesignTool::LogSelectionInfo(UWorld* InWorld)
{
    if (!InWorld) return;

    // 获取或缓存子系统
    if (!CachedSelectionSubsystem.IsValid())
    {
        CachedSelectionSubsystem = InWorld->GetSubsystem<UAvaSelectionProviderSubsystem>();
    }

    if (CachedSelectionSubsystem.IsValid())
    {
        // 获取选中的 Actor
        const auto& SelectedActors = CachedSelectionSubsystem->GetSelectedActors();
        UE_LOG(LogTemp, Log, TEXT("Motion Design - Selected Actors Count: %d"), SelectedActors.Num());

        for (const TWeakObjectPtr<AActor>& ActorPtr : SelectedActors)
        {
            if (AActor* Actor = ActorPtr.Get())
            {
                UE_LOG(LogTemp, Log, TEXT("  - %s"), *Actor->GetName());
            }
        }

        // 获取选择变换
        FTransform SelectionTransform = CachedSelectionSubsystem->GetSelectionTransform();
        UE_LOG(LogTemp, Log, TEXT("Selection Transform Location: %s"), *SelectionTransform.GetLocation().ToString());
    }
}
```

## 模块依赖

Avalanche 是一个模块化的插件，其自身模块众多。使用者（即依赖 Avalancce 功能的项目模块）主要依赖其核心接口模块。由于它集成了大量 Epic 官方功能插件，其内部依赖链复杂。

| 模块 | 用途 |
|---|---|
| `AvalancheCore` | 核心数据类型、接口和子系统基类 |
| `AvalancheEditorCore` | 提供核心的编辑器扩展框架、子系统和 UI 组件（如 `IAvaEditor`, `IAvaEditorExtension`, `UAvaEditorSubsystem`, `SAvaUserInputDialog`） |
| `Sequencer` | 用于集成和控制动画序列，是 `AvalanchePropertyAnimator` 等模块的依赖 |
| `RemoteControl` | 用于远程控制功能集成 |

*注意：该插件依赖大量其他功能插件（如 Text3D, Media Compositing 等），这些依赖关系会在 .uplugin 中自动处理。上表仅列出用于扩展开发时最可能需要直接引用的、非通用的内部模块。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将“场景设置”和“大纲”面板移动到独立的工作区组，优化编辑器布局。 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 使用“节目单页面”设置时，为 Movie Render Queue 添加了分析功能。 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 在节目控制工具栏中增加了页面加载选项（全部、下一个、已选），并进行了其他优化。 |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 添加了项目设置，可以强制禁用 Text3D 和形状的碰撞。 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构了视口代码，当客户端关联或解除关联时发送通知。 |

### 维护评价

**活跃维护**。Avalanche（Motion Design）是一个仍在积极开发中的插件。
- **近期更新频繁**：最近几次提交集中在 2026 年 5 月，且都是功能性增强和优化，表明插件正在快速迭代。
- **开发状态**：从首次提交（2025年5月）和近期更新来看，该插件处于**活跃开发期**，且已从实验性路径 (`/Experimental`) 正式迁移到虚拟制作 (`/VirtualProduction`) 路径，表明其已进入生产就绪阶段。
- **推荐程度**：强烈推荐。它是 Unreal 虚拟制作工作流的核心工具之一，官方维护，功能强大且持续进化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/animation-tools-and-settings-in-unreal-engine/) （应参考“动画”或“虚拟制作”相关章节，但未找到直接链接）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheFunctionalTest) （功能测试模块）