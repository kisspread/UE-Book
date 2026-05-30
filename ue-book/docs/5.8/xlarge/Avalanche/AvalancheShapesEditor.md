# Avalanche Shapes Editor

> Compositing, designer and broadcasting tool.
>
> Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 形状编辑器 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器工具、组件可视化器、序列化轨道编辑器） |
| 模块 | `AvalancheShapesEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

AvalancheShapesEditor 是 Motion Design（Avalanche）插件的形状编辑器模块，专门为虚拟制片和广播设计场景提供直观的形状创建与编辑能力。该模块解决的核心问题是：在 Motion Design 工作流中，用户需要快速在视口中创建和调整各种 2D/3D 基础几何形状（如矩形、椭圆、星形、圆环、立方体、球体、圆锥、圆环体等），并支持对形状的角点倒角、UV 映射、不规则多边形顶点等细节进行交互式操控。

该模块为每种形状类型都实现了完整的视口可视化编辑器（Visualizer），允许用户通过拖拽控制手柄直接在视口中调整形状参数，同时集成了 Sequencer 轨道编辑器，支持形状属性的动画关键帧录制。

## 使用场景

- 你在制作虚拟制片的广播图形（lower thirds、标题卡、Logo 动画） → 使用 Motion Design 的形状工具快速创建矩形、椭圆等 2D 形状
- 你需要在实时渲染的广播画面中添加动态几何元素（星形徽标、箭头指示器、环形进度条） → 用形状工具创建并配合 PropertyAnimator 做动画
- 你正在搭建 XR 虚拟场景的 UI 面板或装饰元素 → 使用 3D 形状工具（立方体、球体、圆锥）创建空间物体
- 你需要对不规则多边形的每个顶点位置和倒角进行精确控制 → 使用 Irregular Polygon 工具的多点编辑功能
- 你需要为形状属性录制 Sequencer 关键帧动画 → 使用内置的 Shape Rect Corner Track Editor

## 蓝图用法

该模块主要是编辑器侧的交互工具和可视化器，不暴露运行时蓝图 API。形状创建通过编辑器工具栏的形状工具完成，形状本身（`AAvaShapeActor` 及其 `UAvaShapeDynamicMeshBase` 组件）的运行时属性由父模块 `AvalancheShapes` 暴露。

### 核心形状类型

模块注册了以下形状创建工具（通过编辑器工具栏访问）：

| 形状类型 | 分类 | 说明 |
|---|---|---|
| Arrow (2D箭头) | 2D | 可调大小的箭头形状 |
| Chevron | 2D | V 形/人字形标记 |
| Ellipse | 2D | 椭圆/圆形，可调边数 |
| Line | 2D | 线段，支持起点终点编辑 |
| NGon | 2D | 正多边形，可调边数 |
| Rectangle / Square | 2D | 矩形/正方形，支持圆角和斜切 |
| Ring | 2D | 环形，可调内径和边数 |
| Star | 2D | 星形，可调角点数和内径 |
| Irregular Polygon | 2D | 不规则多边形，逐点编辑 |
| Cone | 3D | 圆锥体 |
| Cube | 3D | 立方体，支持倒角 |
| Cylinder | 3D | 圆柱体 |
| Sphere | 3D | 球体 |
| Torus | 3D | 圆环体 |

### 使用示例（编辑器操作）

1. 在 Motion Design 模式下，打开形状工具栏
2. 选择目标形状（如 Rectangle）
3. 在视口中按住鼠标拖拽，创建形状并定义初始大小
4. 创建完成后，选中形状 Actor，在视口中通过拖拽控制手柄调整：
   - **尺寸手柄**（Size handles）：拖拽角点调整整体大小
   - **圆角手柄**（Bevel buttons）：拖拽调整各角的倒角大小
   - **斜切手柄**（Slant buttons）：拖拽调整矩形的斜切角度
   - **UV 手柄**（UV buttons）：调整纹理坐标偏移、缩放、旋转

## C++ 用法

### 头文件引入

```cpp
// 形状编辑器工具基类
#include "Tools/AvaShapesEditorShapeToolBase.h"

// 形状工厂（用于程序化创建形状）
#include "AvaShapeFactory.h"

// 形状可视化器（用于自定义视口编辑行为）
#include "Visualizers/AvaShapeDynMeshVis.h"
#include "Visualizers/AvaShape2DDynMeshVis.h"
#include "Visualizers/AvaShape3DDynMeshVis.h"
```

### 基本用法

创建一个自定义形状工具，继承自 `UAvaShapesEditorShapeToolAreaToolBase`（用于拖拽区域类形状）：

```cpp
// 来源: Private/Tools/AvaShapesEditorShapeToolRectangle.h
UCLASS()
class UMyCustomShapeTool : public UAvaShapesEditorShapeAreaToolBase
{
    GENERATED_BODY()

public:
    UMyCustomShapeTool();

protected:
    virtual void OnRegisterTool(IAvalancheInteractiveToolsModule* InAITModule) override;
};
```

实现中通过模板函数创建工厂：

```cpp
// 来源: Private/Tools/AvaShapesEditorShapeToolBase.h - CreateFactory 模板
UMyCustomShapeTool::UMyCustomShapeTool()
{
    // 使用基类的 CreateFactory 模板方法指定形状网格类
    // UAvaShapesEditorShapeToolBase::CreateFactory<UMyShapeDynamicMeshClass>();
}

void UMyCustomShapeTool::OnRegisterTool(IAvalancheInteractiveToolsModule* InAITModule)
{
    // 注册工具到交互工具系统
}
```

### 进阶用法

使用 `UAvaShapeFactory` 程序化创建形状 Actor：

```cpp
// 来源: Private/AvaShapeFactory.h
#include "AvaShapeFactory.h"
#include "Shapes/AvaShapeRectangleDynamicMesh.h"

// 创建矩形工厂
UAvaShapeFactory* Factory = NewObject<UAvaShapeFactory>();

// 配置工厂参数
Factory->SetMeshClass(UAvaShapeRectangleDynamicMesh::StaticClass());
Factory->SetMeshSize(FVector(200.0f, 150.0f, 1.0f));
Factory->SetMeshFunction([](UAvaShapeDynamicMeshBase* InMesh)
{
    // 在形状生成后执行自定义配置
    if (auto* Rect = Cast<UAvaShapeRectangleDynamicMesh>(InMesh))
    {
        // 设置圆角等属性
    }
});
Factory->SetMeshNameOverride(TEXT("MyCustomRect"));

// 使用工厂生成 Actor（在编辑器上下文中）
AActor* NewActor = Factory->SpawnActor(/* ... */);
```

## Demo 示例

一个最小的自定义形状工具实现：

```cpp
// MyShapeTool.h
#pragma once

#include "CoreMinimal.h"
#include "Tools/AvaShapesEditorShapeAreaToolBase.h"
#include "MyShapeTool.generated.h"

UCLASS()
class UMyShapeTool : public UAvaShapesEditorShapeAreaToolBase
{
    GENERATED_BODY()

public:
    UMyShapeTool();

protected:
    virtual void OnRegisterTool(IAvalancheInteractiveToolsModule* InAITModule) override;
};
```

```cpp
// MyShapeTool.cpp
#include "MyShapeTool.h"
#include "AvalancheInteractiveToolsModule.h"

UMyShapeTool::UMyShapeTool()
{
    // 通过基类 CreateFactory 设置要生成的形状类型和默认尺寸
    // 形状类由父类 UAvaShapesEditorShapeToolBase 的 ShapeClass 控制
}

void UMyShapeTool::OnRegisterTool(IAvalancheInteractiveToolsModule* InAITModule)
{
    Super::OnRegisterTool(InAITModule);
    // 工具注册到 Motion Design 的交互工具系统
    // 拖拽区域类工具自动处理视口中的拖拽创建逻辑
    // 创建完成后由 UAvaShapesEditorShapeAreaToolBase::OnViewportPlannerComplete 完成
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AvalancheShapes` | 形状 Actor 和动态网格组件的运行时实现 |
| `AvalancheInteractiveTools` | 编辑器交互工具框架（视口拖拽创建、工具注册） |
| `AvalancheInteractiveToolsRuntime` | 交互工具运行时支持 |
| `AvalancheCore` | Motion Design 核心框架 |
| `AvalancheEditorCore` | 编辑器核心功能 |
| `AvalancheViewport` | 视口扩展和视口状态管理 |
| `LevelEditor` | 关卡编辑器集成 |
| `Sequencer` | 序列器轨道编辑器支持 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将 Motion Design 的场景设置和大纲视图标签页移至独立分组 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 新增使用 Rundown 页面时的 MRQ 分析统计 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 在演出控制工具栏新增页面加载选项（全部/下一个/选中） |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 新增项目设置，可强制禁用 Text3D 和形状的碰撞 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构视口关联/解除关联时的客户端通知机制 |

### 维护评价

AvalancheShapesEditor 模块作为 Motion Design 插件的组成部分，属于 **活跃维护** 状态：

- **创建时间**：2025 年 5 月从 Experimental 迁移到 VirtualProduction，是较新的模块
- **更新频率**：近一个月内有 5 次相关更新，频率较高
- **维护质量**：更新内容涵盖功能增强（新页面加载选项、碰撞控制）、UI 布局优化、分析统计集成等，属于实质性维护
- **注意事项**：该模块作为大型插件（44 个模块、2060 个源文件）的子模块，其生命周期取决于整个 Motion Design 插件的维护计划
- **推荐使用**：✅ 推荐。作为 Epic 官方虚拟制片工具链的一部分，该模块稳定且持续更新，适合虚拟制片和广播设计项目使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [官方文档](https://docs.unrealengine.com/en-US/animation-and-automation/motion-design-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheFunctionalTest)