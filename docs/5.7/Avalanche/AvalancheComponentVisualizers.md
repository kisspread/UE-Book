# Motion Design

> Compositing, designer and broadcasting tool.
>
> Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `Avalanche` (Runtime), `AvalancheAttribute` (Runtime), `AvalancheAttributeEditor` (Runtime), `AvalancheCamera` (Runtime), `AvalancheComponentVisualizers` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), `AvalancheEditorCore` (Runtime), `AvalancheEffectors` (Runtime), `AvalancheEffectorsEditor` (Runtime), `AvalancheInteractiveTools` (Runtime), `AvalancheInteractiveToolsRuntime` (Runtime), `AvalancheLevelViewport` (Runtime), `AvalancheMask` (Runtime), `AvalancheMaskEditor` (Runtime), `AvalancheMedia` (Runtime), `AvalancheMediaEditor` (Runtime), `AvalancheModifiers` (Runtime), `AvalancheModifiersEditor` (Runtime), `AvalancheMRQ` (Runtime), `AvalancheMRQEditor` (Runtime), `AvalancheOutliner` (Runtime), `AvalanchePropertyAnimator` (Runtime), `AvalanchePropertyAnimatorEditor` (Runtime), `AvalancheRemoteControl` (Runtime), `AvalancheRemoteControlEditor` (Runtime), `AvalancheSceneRig` (Runtime), `AvalancheSceneRigEditor` (Runtime), `AvalancheSceneTree` (Runtime), `AvalancheSequence` (Runtime), `AvalancheSequencer` (Runtime), `AvalancheShapes` (Runtime), `AvalancheShapesEditor` (Runtime), `AvalancheSVGEditor` (Runtime), `AvalancheTag` (Runtime), `AvalancheTagEditor` (Runtime), `AvalancheText` (Runtime), `AvalancheTextEditor` (Runtime), `AvalancheTransition` (Runtime), `AvalancheTransitionEditor` (Runtime), `AvalancheViewport` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-01-30 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Avalanche) | |

---

## 用途

Motion Design（原名 Avalanche）是 Epic 为虚拟制片打造的**运动图形设计工具**，定位类似 After Effects + C4D 的实时版本。它解决了以下核心问题：

- **实时运动图形合成**：在 UE 内直接创建、编辑和预览 2D/3D 运动图形，无需导出到外部工具
- **广播级输出**：支持 Media IO Framework 进行实时视频输出，适用于电视直播、虚拟演播室等场景
- **程序化动画**：通过 Effectors（克隆器/效果器）、Modifiers、PropertyAnimator 等系统实现程序化动画驱动
- **场景组织**：SceneTree、SceneRig 提供类似合成软件的层级管理，而非传统 Actor 列表
- **远程控制**：集成 Remote Control，支持外部设备实时操控参数

该插件包含 40+ 个模块，覆盖从核心运行时、编辑器 UI、形状/文本/遮罩/过渡等资产类型，到 Sequencer 集成、MRQ 渲染输出等完整工作流。

## 使用场景

- 你在做虚拟演播室直播 → 用 Motion Design 创建实时图形叠加、Lower Third、Logo 动画
- 你需要制作产品展示动画 → 用 Shapes + Effectors 创建程序化阵列动画
- 你要做广播级图文包装 → 用 Text3D + Transitions + Sequencer 编排复杂动画序列
- 你需要通过 NDI/SDI 输出实时合成画面 → 用 AvalancheMedia + Media IO Framework
- 你想在 UE 内完成运动图形设计全流程 → 用 Motion Design 替代传统 AE/C4D 工作流

---

## 本文档范围

本文档聚焦 **AvalancheComponentVisualizers** 模块——Motion Design 插件的组件可视化系统。该模块为 Motion Design 的各种组件（Shapes、Text、Effects 等）提供编辑器内的可视化操控手柄（gizmo/handle），是设计工作流的核心交互层。

---

## 蓝图用法

AvalancheComponentVisualizers 是一个纯 C++ 运行时模块，不暴露蓝图节点。其功能通过编辑器视口交互自动生效，无需蓝图调用。

---

## C++ 用法

### 头文件引入

```cpp
#include "IAvalancheComponentVisualizersModule.h"
#include "AvaVisBase.h"
```

### 基本用法：注册自定义组件可视化器

Motion Design 的组件可视化器通过模块接口注册。以下展示了标准注册模式：

```cpp
// 来源: IAvalancheComponentVisualizersModule.h 中的模板函数

// 1. 声明存储数组（通常作为模块成员变量）
TArray<TSharedPtr<FComponentVisualizer>> VisualizerStorage;

// 2. 注册可视化器
// InComponentClass: 要可视化的组件类
// InVisualizerClass: 可视化器类
// Storage: 可选，用于持有可视化器的共享引用防止被销毁
IAvalancheComponentVisualizersModule::RegisterComponentVisualizer<UMyComponent, FMyComponentVisualizer>(&VisualizerStorage);
```

### 基本用法：访问模块设置

```cpp
// 来源: IAvalancheComponentVisualizersModule.h, IAvaComponentVisualizersSettings.h

// 获取模块实例
IAvalancheComponentVisualizersModule& Module = IAvalancheComponentVisualizersModule::Get();

// 获取设置接口
IAvaComponentVisualizersSettings* Settings = Module.GetSettings();
if (Settings)
{
    // 调整可视化器精灵图大小
    float SpriteSize = Settings->GetSpriteSize();
    Settings->SetSpriteSize(2.0f);
    
    // 获取/设置特定可视化器的精灵图
    UTexture2D* Sprite = Settings->GetVisualizerSprite(FName("MyVisualizer"));
    Settings->SetVisualizerSprite(FName("MyVisualizer"), MyTexture);
    
    // 设置默认精灵图（不覆盖已有值）
    Settings->SetDefaultVisualizerSprite(FName("MyVisualizer"), DefaultTexture);
    
    // 持久化设置
    Settings->SaveSettings();
}
```

### 进阶用法：实现自定义可视化器

以下展示如何继承 `FAvaVisualizerBase` 实现自定义组件可视化器：

```cpp
// 来源: AvaVisBase.h

class FMyShapeVisualizer : public FAvaVisualizerBase
{
public:
    // 声明哪些属性可编辑
    virtual TMap<UObject*, TArray<FProperty*>> GatherEditableProperties(UObject* InObject) const override
    {
        TMap<UObject*, TArray<FProperty*>> Result;
        if (UMyComponent* Comp = Cast<UMyComponent>(InObject))
        {
            Result.Add(Comp, {
                FMyComponent::StaticStruct()->FindPropertyByName(GET_MEMBER_NAME_CHECKED(UMyComponent, Size)),
                FMyComponent::StaticStruct()->FindPropertyByName(GET_MEMBER_NAME_CHECKED(UMyComponent, Color))
            });
        }
        return Result;
    }

    // 绘制可视化形状（在视口中显示的线框/图形）
    // 基类 FAvaVisualizerBase::DrawVisualization 已提供默认实现
    // virtual void DrawVisualization(const UActorComponent* InComponent, 
    //     const FSceneView* InView, FPrimitiveDrawInterface* InPDI) override;

    // 处理拖拽输入
    // 基类已实现完整的 tracking 生命周期：
    //   HandleInputDelta → StartTracking → HandleInputDeltaInternal → TrackingStopped
    // virtual bool HandleInputDelta(FEditorViewportClient* InViewportClient, 
    //     FViewport* InViewport, FVector& InDeltaTranslate,
    //     FRotator& InDeltaRotate, FVector& InDeltaScale) override;

    // 可选：自定义 Widget 模式（平移/旋转/缩放）
    virtual bool GetWidgetMode(const FEditorViewportClient* InViewportClient, 
        UE::Widget::EWidgetMode& OutMode) const override
    {
        OutMode = UE::Widget::WM_Translate;
        return true;
    }

    // 可选：自定义坐标系
    // virtual bool GetCustomInputCoordinateSystem(const FEditorViewportClient* InViewportClient, 
    //     FMatrix& OutMatrix) const override;
};
```

### 进阶用法：视口覆盖层

```cpp
// 来源: IAvaComponentVisualizersViewportOverlay.h

// 获取视口覆盖层接口
IAvalancheComponentVisualizersModule& Module = IAvalancheComponentVisualizersModule::Get();
IAvaComponentVisualizersViewportOverlay& Overlay = Module.GetViewportOverlay();

// 添加覆盖层控件到指定视口
TArray<TSharedPtr<IAvaViewportClient>> ViewportClients = /* 获取视口客户端 */;
TArray<UObject*> SelectedObjects = /* 获取选中对象 */;
Overlay.AddWidget(ViewportClients, SelectedObjects);

// 检查控件是否激活
if (Overlay.IsWidgetActive())
{
    // 移除控件
    Overlay.RemoveWidget(ViewportClients);
}
```

---

## Demo 示例

以下是一个完整的自定义组件可视化器实现：

### MyShapeVisualizer.h

```cpp
#pragma once

#include "AvaVisBase.h"

class UMyMotionDesignComponent;

class FMyShapeVisualizer : public FAvaVisualizerBase
{
public:
    FMyShapeVisualizer();

    //~ Begin FAvaVisualizerBase
    virtual TMap<UObject*, TArray<FProperty*>> GatherEditableProperties(UObject* InObject) const override;
    virtual void DrawVisualization(const UActorComponent* InComponent, 
        const FSceneView* InView, FPrimitiveDrawInterface* InPDI) override;
    virtual bool HandleInputDelta(FEditorViewportClient* InViewportClient, 
        FViewport* InViewport, FVector& InDeltaTranslate,
        FRotator& InDeltaRotate, FVector& InDeltaScale) override;
    virtual bool GetWidgetMode(const FEditorViewportClient* InViewportClient, 
        UE::Widget::EWidgetMode& OutMode) const override;
    //~ End FAvaVisualizerBase

private:
    const UMyMotionDesignComponent* GetEditedMyComponent() const;
};
```

### MyShapeVisualizer.cpp

```cpp
#include "MyShapeVisualizer.h"
#include "MyMotionDesignComponent.h"

FMyShapeVisualizer::FMyShapeVisualizer()
{
}

TMap<UObject*, TArray<FProperty*>> FMyShapeVisualizer::GatherEditableProperties(UObject* InObject) const
{
    TMap<UObject*, TArray<FProperty*>> Result;
    if (UMyMotionDesignComponent* Comp = Cast<UMyMotionDesignComponent>(InObject))
    {
        static FProperty* SizeProp = UMyMotionDesignComponent::StaticStruct()
            ->FindPropertyByName(GET_MEMBER_NAME_CHECKED(UMyMotionDesignComponent, ShapeSize));
        static FProperty* ExtentProp = UMyMotionDesignComponent::StaticStruct()
            ->FindPropertyByName(GET_MEMBER_NAME_CHECKED(UMyMotionDesignComponent, Extent));
        
        Result.Add(Comp, {SizeProp, ExtentProp});
    }
    return Result;
}

void FMyShapeVisualizer::DrawVisualization(const UActorComponent* InComponent,
    const FSceneView* InView, FPrimitiveDrawInterface* InPDI)
{
    // 调用基类绘制（处理选中高亮等）
    FAvaVisualizerBase::DrawVisualization(InComponent, InView, InPDI);

    const UMyMotionDesignComponent* Comp = Cast<UMyMotionDesignComponent>(InComponent);
    if (!Comp)
    {
        return;
    }

    const FTransform& Transform = Comp->GetComponentTransform();
    const FVector Center = Transform.GetLocation();
    const float HalfSize = Comp->ShapeSize * 0.5f;

    // 使用 HAvaHitProxy 使形状可点击选中
    InPDI->SetHitProxy(new HAvaHitProxy(InComponent));

    // 绘制矩形线框
    const FColor DrawColor = Comp->IsSelectedInEditor() ? FColor::Green : FColor::White;
    InPDI->DrawLine(
        Center + FVector(-HalfSize, -HalfSize, 0),
        Center + FVector( HalfSize, -HalfSize, 0),
        DrawColor, SDPG_Foreground);
    InPDI->DrawLine(
        Center + FVector( HalfSize, -HalfSize, 0),
        Center + FVector( HalfSize,  HalfSize, 0),
        DrawColor, SDPG_Foreground);
    InPDI->DrawLine(
        Center + FVector( HalfSize,  HalfSize, 0),
        Center + FVector(-HalfSize,  HalfSize, 0),
        DrawColor, SDPG_Foreground);
    InPDI->DrawLine(
        Center + FVector(-HalfSize,  HalfSize, 0),
        Center + FVector(-HalfSize, -HalfSize, 0),
        DrawColor, SDPG_Foreground);

    InPDI->SetHitProxy(nullptr);
}

bool FMyShapeVisualizer::HandleInputDelta(FEditorViewportClient* InViewportClient,
    FViewport* InViewport, FVector& InDeltaTranslate,
    FRotator& InDeltaRotate, FVector& InDeltaScale)
{
    // 基类处理 tracking 生命周期（StartTracking/EndTracking/事务管理）
    if (!FAvaVisualizerBase::HandleInputDelta(InViewportClient, InViewport, 
        InDeltaTranslate, InDeltaRotate, InDeltaScale))
    {
        return false;
    }

    // 应用缩放到组件属性
    UMyMotionDesignComponent* Comp = const_cast<UMyMotionDesignComponent*>(GetEditedMyComponent());
    if (Comp && !InDeltaScale.IsNearlyZero())
    {
        Comp->ShapeSize *= (1.0f + InDeltaScale.X);
    }

    return true;
}

bool FMyShapeVisualizer::GetWidgetMode(const FEditorViewportClient* InViewportClient,
    UE::Widget::EWidgetMode& OutMode) const
{
    OutMode = UE::Widget::WM_Scale;
    return true;
}

const UMyMotionDesignComponent* FMyShapeVisualizer::GetEditedMyComponent() const
{
    return Cast<UMyMotionDesignComponent>(GetEditedComponent());
}
```

### 注册（在模块 StartupModule 中）

```cpp
void FMyModule::StartupModule()
{
    // 注册可视化器，Storage 持有引用防止被释放
    IAvalancheComponentVisualizersModule::RegisterComponentVisualizer<
        UMyMotionDesignComponent, FMyShapeVisualizer>(&VisualizerStorage);
}
```

---

## 模块依赖

AvalancheComponentVisualizers 的 Build.cs 依赖：

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine/Slate 等） | |

该模块作为 Motion Design 插件的内部模块，被其他 Avalanche 模块（如 AvalancheShapes、AvalancheText 等）依赖，用于为其组件提供编辑器可视化支持。

---

## 维护状态

### 近期更新

```
- 31e56d449c9c MotionDesign : Shapes - Fixed visualizer handles not showing when hovering actor
- d53ec51b85c0 Motion Design: moved the following plugins from /Plugins/Experimental to /Plugins/VirtualProduction: ActorModifier, ActorModifierCore, Motion Design, ClonerEffector, CustomDetailsView, Material Designer, GeometryMask, OperatorStack, PropertyAnimator, PropertyAnimatorCore, StormSync, StormSync Motion Design Bridge
```

### 维护评价

- **创建时间**：2024-01-30，约 1 年历史
- **近期活动**：有实质性 bug 修复（可视化器手柄显示问题），且刚从 Experimental 迁移到 VirtualProduction，表明 Epic 认为其已达到生产可用状态
- **活跃度**：活跃维护中，作为 Virtual Production 工作流的核心组件持续迭代
- **已知限制**：依赖大量其他插件（Advanced Renamer、Remote Control、SVG Importer 等），集成复杂度高
- **推荐程度**：✅ 推荐用于虚拟制片/广播场景。该插件是 Epic 官方维护的运动图形解决方案，已从实验阶段毕业，适合生产环境使用。但需注意其庞大的依赖链和模块数量（40+），学习曲线较陡。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Avalanche)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/motion-design-in-unreal-engine/)