# Motion Design

> Compositing, designer and broadcasting tool. Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 运动设计 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（设计工具和示例） |
| 模块 | `Avalanche` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), `AvalancheComponentVisualizers` (Runtime), ...（共 43 个模块） |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Motion Design 是一个集成在虚幻引擎中的综合性运动图形与虚拟制片工具集。它旨在提供一套完整的解决方案，用于创建、编辑和管理复杂的动态视觉内容，例如电视节目包装、虚拟制片中的实时图形、以及现场广播中的动态元素。

与传统的静态资产和蓝图相比，Motion Design 专注于提供高效、可交互的编辑流程。它通过专用的编辑器面板、视口叠加和交互式可视化器，允许设计师直接在场景视口中拖拽、旋转、缩放组件，并实时预览参数变化，从而大大缩短了从设计到实时渲染的迭代周期。它解决的核心问题是将复杂的动态图形设计工作流集成到虚幻引擎的实时渲染管线中。

## 使用场景

*   你在为电视节目或大型活动制作实时动态图形（Lower Thirds, Bumpers） → 用 Motion Design 的 Text3D、形状、材质设计师和场景树来构建和管理这些元素。
*   你需要为虚拟制片项目（如VP舞台）设计和控制复杂的现场图形和动画 → 用 Motion Design 的场景装备（Scene Rig）、序列器和远程控制功能。
*   你在开发一个需要大量动态视觉效果的交互式应用或广播软件 → 用 Motion Design 的克隆器/效果器（ClonerEffector）和属性动画器（PropertyAnimator）来创建程序化动画。

## 蓝图用法

**注意**：`AvalancheComponentVisualizers` 模块主要为编辑器扩展和组件可视化器提供基础设施，其核心类（如 `FAvaVisualizerBase`）并非为蓝图直接调用设计。蓝图用户通常通过 `Motion Design` 的其他模块（如 `AvalancheBlueprint`）暴露的节点进行交互。以下介绍该模块提供的核心 C++ 接口。

## C++ 用法

该模块的核心是 `FAvaVisualizerBase` 类，它为在视口中交互式编辑 Motion Design 组件属性提供了框架。

### 头文件引入

```cpp
#include "AvaVisBase.h"
```

### 基本用法

创建一个自定义的组件可视化器。你需要继承 `FAvaVisualizerBase` 并重写关键方法。

```cpp
// 来源于引擎源码：Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheComponentVisualizers/Public/AvaVisBase.h
class FMyCustomVisualizer : public FAvaVisualizerBase
{
public:
    // 实现纯虚函数，定义要编辑的属性
    virtual TMap<UObject*, TArray<FProperty*>> GatherEditableProperties(UObject* InObject) const override
    {
        TMap<UObject*, TArray<FProperty*>> EditableProperties;
        if (UMyComponent* MyComp = Cast<UMyComponent>(InObject))
        {
            EditableProperties.Add(MyComp, {FMyComponent::StaticClass()->FindPropertyByName(GET_MEMBER_NAME_CHECKED(UMyComponent, MyProperty))});
        }
        return EditableProperties;
    }

    // 实现绘制逻辑，根据组件状态绘制不同的图形
    virtual void DrawVisualizationEditing(const UActorComponent* InComponent, const FSceneView* InView,
        FPrimitiveDrawInterface* InPDI, int32& InOutIconIndex) override
    {
        const UMyComponent* MyComp = Cast<UMyComponent>(InComponent);
        if (!MyComp) return;

        // 绘制一个简单的线框立方体
        FTransform CompTransform = GetComponentTransform(InComponent);
        FBox Bounds = GetComponentBounds(InComponent);
        InPDI->DrawLine(CompTransform.TransformPosition(Bounds.Min), CompTransform.TransformPosition(Bounds.Max), GetIconColor(true), SDPG_Foreground);
    }

    // 实现拖拽输入处理
    virtual bool HandleInputDeltaInternal(FEditorViewportClient* InViewportClient, FViewport* InViewport, const FVector& InAccumulatedTranslation,
        const FRotator& InAccumulatedRotation, const FVector& InAccumulatedScale) override
    {
        // 修改组件属性
        UMyComponent* MyComp = Cast<UMyComponent>(GetEditedComponent());
        if (MyComp)
        {
            // 使用 ModifyProperty 包裹属性修改，以便正确创建撤销事务
            ModifyProperty(MyComp, GET_MEMBER_NAME_CHECKED(UMyComponent, MyVectorProperty), EPropertyChangeType::ValueSet, [&]()
            {
                MyComp->MyVectorProperty += InAccumulatedTranslation;
            });
            return true;
        }
        return false;
    }
};
```

### 进阶用法：注册可视化器

使用模块提供的模板函数注册你的可视化器。

```cpp
// 来源于引擎源码：Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheComponentVisualizers/Public/IAvalancheComponentVisualizersModule.h
void RegisterMyVisualizer()
{
    // 注册可视化器，将 UMyComponent 与 FMyCustomVisualizer 关联
    IAvalancheComponentVisualizersModule::RegisterComponentVisualizer<UMyComponent, FMyCustomVisualizer>();
}
```

## Demo 示例

一个最小化的自定义组件可视化器实现。

**MyComponentVisualizer.h**
```cpp
#pragma once
#include "AvaVisBase.h"

class UMyComponent;

class FMyComponentVisualizer : public FAvaVisualizerBase
{
public:
    virtual TMap<UObject*, TArray<FProperty*>> GatherEditableProperties(UObject* InObject) const override;
    virtual void DrawVisualizationNotEditing(const UActorComponent* InComponent, const FSceneView* InView,
        FPrimitiveDrawInterface* InPDI, int32& InOutIconIndex) override;
    virtual void DrawVisualizationEditing(const UActorComponent* InComponent, const FSceneView* InView,
        FPrimitiveDrawInterface* InPDI, int32& InOutIconIndex) override;
    virtual bool HandleInputDeltaInternal(FEditorViewportClient* InViewportClient, FViewport* InViewport, const FVector& InAccumulatedTranslation,
        const FRotator& InAccumulatedRotation, const FVector& InAccumulatedScale) override;
};
```

**MyComponentVisualizer.cpp**
```cpp
#include "MyComponentVisualizer.h"
#include "MyComponent.h"

TMap<UObject*, TArray<FProperty*>> FMyComponentVisualizer::GatherEditableProperties(UObject* InObject) const
{
    TMap<UObject*, TArray<FProperty*>> Props;
    if (UMyComponent* Comp = Cast<UMyComponent>(InObject))
    {
        FProperty* RadiusProp = UMyComponent::StaticClass()->FindPropertyByName(GET_MEMBER_NAME_CHECKED(UMyComponent, Radius));
        Props.Add(Comp, {RadiusProp});
    }
    return Props;
}

void FMyComponentVisualizer::DrawVisualizationNotEditing(const UActorComponent* InComponent, const FSceneView* InView,
    FPrimitiveDrawInterface* InPDI, int32& InOutIconIndex)
{
    // 非编辑状态下绘制一个图标
    const UMyComponent* Comp = Cast<UMyComponent>(InComponent);
    if (!Comp) return;
    FVector WorldPos = Comp->GetComponentLocation();
    DrawDashedLine(InPDI, WorldPos, WorldPos + FVector(0, 0, 100.f), GetIconColor(false), 5.f, SDPG_Foreground);
}

void FMyComponentVisualizer::DrawVisualizationEditing(const UActorComponent* InComponent, const FSceneView* InView,
    FPrimitiveDrawInterface* InPDI, int32& InOutIconIndex)
{
    // 编辑状态下绘制可交互的圆环
    const UMyComponent* Comp = Cast<UMyComponent>(InComponent);
    if (!Comp) return;
    FTransform T = GetComponentTransform(InComponent);
    DrawCircle(InPDI, T.GetLocation(), T.GetUnitAxis(EAxis::X), T.GetUnitAxis(EAxis::Y),
        GetIconColor(true), Comp->Radius, 32, SDPG_Foreground);
}

bool FMyComponentVisualizer::HandleInputDeltaInternal(FEditorViewportClient* InViewportClient, FViewport* InViewport,
    const FVector& InAccumulatedTranslation, const FRotator& InAccumulatedRotation, const FVector& InAccumulatedScale)
{
    UMyComponent* Comp = Cast<UMyComponent>(GetEditedComponent());
    if (!Comp) return false;
    ModifyProperty(Comp, GET_MEMBER_NAME_CHECKED(UMyComponent, Radius), EPropertyChangeType::ValueSet, [&]()
    {
        // 根据拖拽缩放调整半径
        Comp->Radius += InAccumulatedScale.X * 10.f;
        Comp->Radius = FMath::Max(0.f, Comp->Radius);
    });
    return true;
}
```

## 模块依赖

从 `AvalancheComponentVisualizers.Build.cs` 分析，该模块依赖于 Motion Design 核心模块。

| 模块 | 用途 |
|---|---|
| `AvalancheCore` | Motion Design 核心类型、工具和通用功能 |

（注：其他依赖如 `Slate`, `Engine` 等为标准引擎模块，已省略。）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将Motion Design的面板（场景设置、大纲）移动到独立的分组中。 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 为使用 Rundown 页面设置时添加了 MRQ 分析功能。 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 在显示控制工具栏中添加了页面加载选项（全部、下一个、选定），并添加了相关功能。 |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 添加了项目设置，用于强制禁用 Text3D 和形状的碰撞。 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构：当客户端关联或断开关联时通知它，以整合必需的模板代码。 |

### 维护评价

**活跃维护**。Motion Design（Avalanche）插件是一个新创建（2025年）的大型功能集，从 `Experimental` 目录迁移至 `VirtualProduction` 标志着其成熟度和重要性。从提交历史看，开发团队在持续进行功能迭代和体验优化（如UI重组、添加分析、完善项目设置）。该插件是 Epic 虚拟制片战略的关键部分，预计会长期维护和更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheFunctionalTest) (可能位于 `AvalancheFunctionalTest` 模块)