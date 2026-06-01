# Motion Design - Shapes Editor 模块

> Compositing, designer and broadcasting tool.
>
> Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 动态形状编辑器 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AvalancheShapesEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheShapesEditor) | |

## 用途

AvalancheShapesEditor 是 Motion Design 插件的形状编辑器子模块，为 Motion Design 中的各种参数化形状（2D 和 3D）提供**视口可视化器**（Visualizer）和**交互式创建工具**。

这个模块解决的核心问题是：Motion Design 系统中的形状 Actor（如矩形、星形、圆环、圆锥等）拥有大量参数化属性（倒角大小、边数、内径比例、倾斜角度等），直接在 Details 面板中调节这些数值既不直观也难以精确控制。本模块通过以下机制解决这一问题：

1. **组件可视化器（Component Visualizer）**：在编辑器视口中为每种形状绘制可交互的控制手柄（Handle），用户可以直接拖拽手柄来调整形状参数
2. **交互式创建工具（Interactive Tools）**：通过视口绘制的方式创建形状，支持拖拽定义尺寸、逐点绘制不规则多边形等
3. **Sequencer 轨道编辑器**：为矩形圆角设置提供 Sequencer 动画轨道支持

**注意**：本模块是整个 Motion Design（Avalanche）插件的一个子模块。Motion Design 插件本身是一个完整的合成、设计和广播工具，包含 40+ 个子模块，涵盖材质设计、特效器、场景管理、媒体合成等功能。Shapes Editor 仅负责形状部分的编辑器侧支持。

## 使用场景

- 你需要创建广播级动态图形（Motion Graphics）中的参数化几何形状（矩形、星形、圆环等）并需要在视口中直观编辑它们的参数
- 你需要直接在 Unreal 编辑器视口中通过拖拽来调整形状的倒角、边数、内径等属性，而不是在 Details 面板中输入数字
- 你需要绘制不规则多边形（逐点绘制，支持添加/打断顶点、调整各顶点倒角）
- 你需要在 Sequencer 中对矩形的圆角设置进行关键帧动画

## 蓝图用法

本模块主要是**编辑器工具和可视化器**，几乎没有暴露给蓝图的公开 API。所有功能通过编辑器 UI 交互完成：

- 视口工具栏中的形状创建按钮
- 视口中形状组件上的交互式控制手柄
- Sequencer 中的矩形圆角轨道

本模块不包含 `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)` 接口。

## C++ 用法

本模块的核心价值在于其**组件可视化器**（Component Visualizer）和**交互式工具**（Interactive Tool）架构。以下展示如何理解其内部设计。

### 头文件引入

```cpp
#include "AvalancheShapesEditorModule.h"
```

### 组件可视化器体系

模块为每种形状类型注册了对应的组件可视化器，提供视口内交互式编辑能力：

```
FAvaVisualizerBase（基础可视化器，来自 AvalancheComponentVisualizers 模块）
  └─ FAvaShapeDynamicMeshVisualizer（所有形状动态网格的基础可视化器）
       ├─ FAvaShape2DDynamicMeshVisualizer（2D 形状基础）
       │    ├─ FAvaShapeRoundedPolygonDynamicMeshVisualizer（圆角多边形）
       │    │    ├─ FAvaShapeNGonDynamicMeshVisualizer（N 边形）
       │    │    ├─ FAvaShapeStarDynamicMeshVisualizer（星形）
       │    │    └─ FAvaShapeLineDynamicMeshVisualizer（线段）
       │    ├─ FAvaShapeRectangleDynamicMeshVisualizer（矩形）
       │    ├─ FAvaShapeEllipseDynamicMeshVisualizer（椭圆）
       │    ├─ FAvaShapeRingDynamicMeshVisualizer（圆环）
       │    └─ FAvaShapeIrregularPolygonDynamicMeshVisualizer（不规则多边形）
       └─ FAvaShape3DDynamicMeshVisualizer（3D 形状基础）
            ├─ FAvaShapeCubeDynamicMeshVisualizer（立方体）
            ├─ FAvaShapeSphereDynamicMeshVisualizer（球体）
            ├─ FAvaShapeConeDynamicMeshVisualizer（圆锥）
            └─ FAvaShapeTorusDynamicMeshVisualizer（圆环体）
```

### 交互式工具体系

模块为每种形状类型注册了对应的创建工具，通过视口拖拽方式创建形状：

```
UAvaInteractiveToolsActorToolBase（来自 AvalancheInteractiveTools 模块）
  └─ UAvaShapesEditorShapeToolBase（形状工具基类）
       ├─ UAvaShapesEditorShapeAreaToolBase（面积型工具，拖拽定义矩形区域）
       │    ├─ UAvaShapesEditorShapeToolRectangle（矩形）
       │    ├─ UAvaShapesEditorShapeToolEllipse（椭圆）
       │    ├─ UAvaShapesEditorShapeToolRing（圆环）
       │    ├─ UAvaShapesEditorShapeToolNGon（N 边形）
       │    ├─ UAvaShapesEditorShapeToolStar（星形）
       │    ├─ UAvaShapesEditorShapeTool2DArrow（2D 箭头）
       │    ├─ UAvaShapesEditorShapeToolChevron（V 形）
       │    ├─ UAvaShapesEditorShapeToolSphere（球体）
       │    ├─ UAvaShapesEditorShapeToolTorus（圆环体）
       │    ├─ UAvaShapesEditorShapeToolCone（圆锥）
       │    └─ UAvaShapesEditorShapeToolCube（立方体）
       ├─ UAvaShapesEditorShapeToolLine（线段，两点绘制）
       └─ UAvaShapesEditorShapeToolIrregularPoly（不规则多边形，逐点绘制）
```

### Hit Proxy 体系

可视化器通过 Hit Proxy 实现视口中的精确交互。每种可交互元素有对应的 Hit Proxy 类型：

| Hit Proxy | 用途 |
|---|---|
| `HAvaShapeSizeHitProxy` | 拖拽调整形状整体尺寸 |
| `HAvaShapeUVHitProxy` | 调整 UV 贴图参数 |
| `HAvaShapeNumSidesHitProxy` | 调整边数 |
| `HAvaShapeNumPointsHitProxy` | 调整角点数 |
| `HAvaShapeInnerSizeHitProxy` | 调整内径比例 |
| `HAvaShapeCornersHitProxy` | 调整圆角 |
| `HAvaShapeAngleDegreeHitProxy` | 调整角度 |
| `HAvaShapeRectangleCornerHitProxy` | 矩形圆角设置 |
| `HAvaShapeRectangleSlantHitProxy` | 矩形倾斜设置 |
| `HAvaShapeIrregularPolygonPointHitProxy` | 不规则多边形顶点 |
| `HAvaShapeIrregularPolygonBevelHitProxy` | 不规则多边形倒角 |
| `HAvaShapeIrregularPolygonBreakHitProxy` | 不规则多边形打断 |
| `HAvaShapeLineEndHitProxy` | 线段端点 |

### 模块初始化

```cpp
// 来自 Private/AvalancheShapesEditorModule.h
class FAvalancheShapesEditorModule : public IModuleInterface
{
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

    TArray<TSharedPtr<FComponentVisualizer>> Visualizers;
    void RegisterVisualizers();
    FDelegateHandle TrackEditorHandle;
};
```

模块在 `StartupModule()` 中完成以下初始化：
1. 注册所有形状类型的组件可视化器（`RegisterVisualizers()`）
2. 注册 Sequencer 轨道编辑器（矩形圆角设置）
3. 注册形状创建工具（通过 `IAvalancheInteractiveToolsModule` 接口）

### 形状工厂（Shape Factory）

```cpp
// 来自 Private/AvaShapeFactory.h
UCLASS()
class UAvaShapeFactory : public UActorFactory
{
    void SetMeshClass(TSubclassOf<UAvaShapeDynamicMeshBase> InMeshClass);
    void SetMeshSize(const FVector& InMeshSize);
    void SetMeshFunction(TFunction<void(UAvaShapeDynamicMeshBase*)> InFunction);
    void SetMeshNameOverride(const TOptional<FString>& InMeshNameOverride);
};
```

`UAvaShapeFactory` 是自定义的 Actor 工厂，用于在创建形状时设置网格类型、初始大小、后处理函数和名称覆盖。

### 可视化器核心接口

所有形状可视化器都实现了以下关键接口：

```cpp
// 来自 Private/Visualizers/AvaShapeDynMeshVis.h
class FAvaShapeDynamicMeshVisualizer : public FAvaVisualizerBase
{
    // 获取被编辑的组件
    virtual UActorComponent* GetEditedComponent() const override;
    
    // 收集可编辑属性（返回 Object -> Property 列表的映射）
    virtual TMap<UObject*, TArray<FProperty*>> GatherEditableProperties(UObject* InObject) const override;
    
    // 处理视口点击（通过 Hit Proxy 识别被点击的控制元素）
    virtual bool VisProxyHandleClick(...) override;
    
    // 获取 Widget 模式（平移/旋转/缩放）
    virtual bool GetWidgetMode(...) const override;
    
    // 获取 Widget 位置（控制手柄的世界坐标位置）
    virtual bool GetWidgetLocation(...) const override;
    
    // 处理输入增量（拖拽时的实时更新）
    virtual bool HandleInputDeltaInternal(...) override;
    
    // 重置值（双击恢复默认）
    virtual bool ResetValue(...) override;
};
```

### 2D vs 3D 形状可视化器的差异

| 特性 | 2D 形状可视化器 | 3D 形状可视化器 |
|---|---|---|
| 基类 | `FAvaShape2DDynamicMeshVisualizer` | `FAvaShape3DDynamicMeshVisualizer` |
| 尺寸类型 | `FVector2D` | `FVector` |
| 对齐方式 | 4 个角（TopLeft/TopRight/BottomLeft/BottomRight） | 8 个角（前后各 4 个角） |
| UV 编辑 | ✅ 支持 UV Section、UV Anchor | ❌ 不支持 |
| 吸附 | `SnapLocation2D()` | `SnapLocation3D()` |
| 特殊属性 | 矩形有 Slant、IrregularPolygon 有顶点/倒角/打断 | Torus 有 NumSlices/InnerSize/Angle、Cone 有 TopRadius 等 |

### 形状工具基类

```cpp
// 来自 Private/Tools/AvaShapesEditorShapeToolBase.h
UCLASS(Abstract)
class UAvaShapesEditorShapeToolBase : public UAvaInteractiveToolsActorToolBase
{
    struct FShapeFactoryParameters
    {
        FVector Size = FVector(100);
        TFunction<void(UAvaShapeDynamicMeshBase*)> Functor = [](UAvaShapeDynamicMeshBase*){};
        TOptional<FString> NameOverride;
    };
    
    // 创建形状工厂（模板方法，指定网格类型）
    template<typename InMeshClass>
    static UAvaShapeFactory* CreateFactory(const FShapeFactoryParameters& InParameters = DefaultParameters);
};
```

面积型工具（Area Tool）在此基础上增加了视口区域拖拽支持：

```cpp
// 来自 Private/Tools/AvaShapesEditorShapeAreaToolBase.h
UCLASS(Abstract)
class UAvaShapesEditorShapeAreaToolBase : public UAvaShapesEditorShapeToolBase
{
    virtual void OnViewportPlannerUpdate() override;   // 拖拽过程中实时更新形状尺寸
    virtual void OnViewportPlannerComplete() override;  // 拖拽完成
    void UpdateShapeSize(AAvaShapeActor* InShapeActor) const;
};
```

## Demo 示例

由于本模块主要是编辑器可视化器和工具，没有直接可用的运行时 API。以下是理解可视化器工作原理的最小示例：

```cpp
// MyShapeVisualizer.h
#pragma once

#include "Visualizers/AvaShape2DDynMeshVis.h"

// 自定义形状的可视化器示例（继承 2D 形状可视化器）
class FMyCustomShapeVisualizer : public FAvaShape2DDynamicMeshVisualizer
{
public:
    using Super = FAvaShape2DDynamicMeshVisualizer;

    FMyCustomShapeVisualizer();

    // 收集可编辑属性
    virtual TMap<UObject*, TArray<FProperty*>> GatherEditableProperties(UObject* InObject) const override;

    // 处理视口点击
    virtual bool VisProxyHandleClick(
        FEditorViewportClient* InViewportClient,
        HComponentVisProxy* InVisProxy,
        const FViewportClick& InClick) override;

protected:
    // 绘制非编辑状态的可视化
    virtual void DrawVisualizationNotEditing(
        const UActorComponent* InComponent,
        const FSceneView* InView,
        FPrimitiveDrawInterface* InPDI,
        int32& InOutIconIndex) override;

    // 绘制编辑状态的可视化（显示额外控制手柄）
    virtual void DrawVisualizationEditing(
        const UActorComponent* InComponent,
        const FSceneView* InView,
        FPrimitiveDrawInterface* InPDI,
        int32& InOutIconIndex) override;

    // 处理拖拽输入
    virtual bool HandleInputDeltaInternal(
        FEditorViewportClient* InViewportClient,
        FViewport* InViewport,
        const FVector& InAccumulatedTranslation,
        const FRotator& InAccumulatedRotation,
        const FVector& InAccumulatedScale) override;

    // 存储初始值（拖拽开始时）
    virtual void StoreInitialValues() override;
};
```

```cpp
// MyShapeVisualizer.cpp
#include "MyShapeVisualizer.h"

FMyCustomShapeVisualizer::FMyCustomShapeVisualizer()
{
    // 初始化
}

TMap<UObject*, TArray<FProperty*>> FMyCustomShapeVisualizer::GatherEditableProperties(UObject* InObject) const
{
    TMap<UObject*, TArray<FProperty*>> Properties;
    // 收集需要在视口中可编辑的属性
    // Properties.Add(InObject, { SizeProperty, SomeOtherProperty });
    return Properties;
}

bool FMyCustomShapeVisualizer::VisProxyHandleClick(
    FEditorViewportClient* InViewportClient,
    HComponentVisProxy* InVisProxy,
    const FViewportClick& InClick)
{
    // 根据 Hit Proxy 类型判断点击了哪个控制元素
    // if (InVisProxy->IsA(HAvaShapeSizeHitProxy::StaticGetType()))
    // {
    //     const HAvaShapeSizeHitProxy* SizeProxy = static_cast<HAvaShapeSizeHitProxy*>(InVisProxy);
    //     // 开始编辑尺寸...
    //     return true;
    // }
    return Super::VisProxyHandleClick(InViewportClient, InVisProxy, InClick);
}

void FMyCustomShapeVisualizer::DrawVisualizationNotEditing(
    const UActorComponent* InComponent,
    const FSceneView* InView,
    FPrimitiveDrawInterface* InPDI,
    int32& InOutIconIndex)
{
    // 非编辑状态：绘制基本控制手柄图标
    // Super::DrawSizeButtons(GetDynamicMeshAs<FMeshType>(), InView, InPDI);
}

void FMyCustomShapeVisualizer::DrawVisualizationEditing(
    const UActorComponent* InComponent,
    const FSceneView* InView,
    FPrimitiveDrawInterface* InPDI,
    int32& InOutIconIndex)
{
    // 编辑状态：绘制所有控制手柄（尺寸、UV 等）
    Super::DrawVisualizationEditing(InComponent, InView, InPDI, InOutIconIndex);
}

bool FMyCustomShapeVisualizer::HandleInputDeltaInternal(
    FEditorViewportClient* InViewportClient,
    FViewport* InViewport,
    const FVector& InAccumulatedTranslation,
    const FRotator& InAccumulatedRotation,
    const FVector& InAccumulatedScale)
{
    // 将输入增量转换为形状参数的变化
    // 例如：拖拽 Scale -> 更新 SizeProperty
    return Super::HandleInputDeltaInternal(InViewportClient, InViewport,
        InAccumulatedTranslation, InAccumulatedRotation, InAccumulatedScale);
}

void FMyCustomShapeVisualizer::StoreInitialValues()
{
    Super::StoreInitialValues();
    // 存储拖拽开始时的初始值
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AvalancheCore` | Motion Design 核心框架 |
| `AvalancheShapes` | 形状运行时组件（UAvaShapeDynamicMeshBase、AAvaShapeActor 等） |
| `AvalancheInteractiveToolsRuntime` | 交互式工具运行时基类 |
| `AvalancheComponentVisualizers` | 组件可视化器基础架构（FAvaVisualizerBase） |
| `AvalancheSequencer` | Sequencer 集成 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将 Motion Design 面板从关卡编辑器分离到独立分组 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 添加 MRQ 分析功能，追踪节目单页面设置使用情况 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 添加节目控制工具栏的页面加载选项（全部/下一个/已选） |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 添加项目设置以强制禁用 Text3D 和形状的碰撞 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构视口客户端关联/解除关联通知机制 |

### 维护评价

- **创建时间**：2025 年 5 月从 Experimental 迁移到 Virtual Production，是较新的模块
- **最近更新频率**：非常活跃，最近一周有多次提交，涉及功能增强和 UI 改进
- **维护状态**：**活跃维护中**，由 Epic Games 持续开发
- **已知限制**：
  - 标记为 Runtime 模块，但实际上包含大量编辑器专用代码（Visualizer、TrackEditor、Tools），模块类型标记可能不准确
  - 作为 Motion Design 的子模块，依赖整个 Motion Design 插件生态
- **推荐使用**：如果你在使用 Motion Design（Avalanche）插件进行虚拟制作或广播级动态图形创作，此模块是形状编辑功能的核心组件，会随 Motion Design 插件自动加载。不建议独立使用此模块。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheShapesEditor)
- [插件根目录](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [形状运行时模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheShapes)
- [组件可视化器基础模块](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheComponentVisualizers)
- [交互式工具模块](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheInteractiveTools)