# Geometry Mode

> Geometry and BSP editing

| 属性 | 值 |
|---|---|
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（Slate 样式资源、图标） |
| 模块 | `GeometryMode` (Editor), `BspMode` (Editor), `TextureAlignMode` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2019-10-28 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/GeometryMode) | |

## 用途

GeometryMode 是 UE5 中用于直接编辑 BSP（Binary Space Partitioning）Brush 几何体的编辑器插件。它提供了三个紧密关联的编辑器模式模块：

1. **GeometryMode** — 核心模块，允许关卡设计师在视口中直接选择和编辑 Brush 的顶点（Vertex）、边（Edge）和多边形（Poly），并提供了十余种几何修改器（Modifier）用于执行挤出、裁剪、旋转成型等操作。
2. **BspMode** — 在放置面板（Placement Mode）中注册 BSP 基础几何体（Box、Cone、Cylinder、各类楼梯、Sphere），支持拖拽放置到场景中。
3. **TextureAlignMode** — 提供纹理对齐模式，允许通过 Gizmo 直接在视口中平移、旋转和缩放 BSP 表面的纹理坐标。

这个插件的存在意义在于为 BSP 关卡设计工作流提供完整的编辑能力。虽然 UE5 的主流关卡设计已转向 Static Mesh 和 Modeling Tools（编辑器内建模），但 BSP 仍然在原型设计、阻挡体积（Blocking Volume）和简单关卡搭建中有其用途。GeometryMode 是 BSP 工作流的核心编辑入口。

## 使用场景

- 你正在用 BSP 快速搭建关卡原型，需要调整 Brush 的形状 → 进入 Geometry Mode，选择顶点/边/面进行编辑
- 你需要沿法线方向挤出一个多边面来创建墙壁延伸 → 选择面，使用 Extrude 修改器
- 你需要沿着一条线裁剪 Brush → 使用 Clip 修改器，在正交视口中放置裁剪点
- 你需要从零开始绘制自定义形状的 Brush → 使用 Pen 修改器，在正交视口中逐点绘制
- 你需要将 Brush Shape 旋转成型为圆柱/花瓶等旋转体 → 使用 Lathe 修改器
- 你需要精确调整 BSP 表面上的纹理位置和旋转 → 进入 Texture Alignment 模式
- 你需要快速放置标准几何体 Brush（立方体、圆柱、楼梯等）→ 使用 BspMode 的放置面板

## 模块架构

### GeometryMode 模块

核心模块，注册了 `EM_Geometry` 编辑器模式。进入该模式后，选中的 Brush 会被解析为可编辑的几何元素（顶点/边/多边形），用户可以通过视口中的 Hit Proxy 直接点击选择，并使用各种修改器进行操作。

**关键类：**

| 类 | 说明 |
|---|---|
| `FEdModeGeometry` | 编辑器模式主类，管理几何对象集合、选择状态、渲染 |
| `FModeTool_GeometryModify` | 模式工具类，管理所有几何修改器，处理输入事件 |
| `FGeometryModeToolkit` | 模式 Toolkit，提供编辑器面板 UI（修改器按钮、属性面板） |
| `FGeomObject` | 一个 Brush 的几何表示，包含顶点池、边池、多边形池 |
| `FGeomVertex` | 顶点，继承自 `FVector3f`，追踪所属多边形 |
| `FGeomEdge` | 边，由两个顶点索引定义，追踪所属多边形 |
| `FGeomPoly` | 多边形，索引到 Brush 的实际 `FPoly` |
| `FGeomBase` | 所有几何元素的基类，提供选择状态、中点、法线等 |
| `UGeomModifier` | 所有几何修改器的基类（UObject），提供事务管理、状态缓存 |
| `UBrushEditingSubsystemImpl` | 编辑器子系统，处理 Brush 几何体的点击选择逻辑 |

### BspMode 模块

向 Placement Mode 面板注册 BSP 基础几何体类别。支持以下 Brush Builder：

| Builder | 形状 |
|---|---|
| `UCubeBuilder` | 立方体 |
| `UConeBuilder` | 圆锥 |
| `UCylinderBuilder` | 圆柱 |
| `UCurvedStairBuilder` | 弧形楼梯 |
| `ULinearStairBuilder` | 直线楼梯 |
| `USpiralStairBuilder` | 螺旋楼梯 |
| `UTetrahedronBuilder` | 球体 |

### TextureAlignMode 模块

注册 `EM_TextureAlign` 编辑器模式。进入后，坐标系自动切换为 Local，Gizmo 对齐到选中表面的纹理坐标系（TextureU/TextureV/Normal）。支持：
- **平移**：沿纹理 U/V 方向移动纹理
- **旋转**：绕表面法线旋转纹理
- **缩放**：沿纹理 U/V 方向缩放纹理

## 几何修改器一览

GeometryMode 提供了 12 种几何修改器（`UGeomModifier` 子类），分为两类：

### 模式修改器（Radio Button，持续生效）

| 修改器 | 类 | 说明 |
|---|---|---|
| Edit | `UGeomModifier_Edit` | 默认选择模式，可选择顶点/边/面并用 Gizmo 平移、旋转、缩放 |
| Extrude | `UGeomModifier_Extrude` | 沿法线方向挤出选中的面，创建新的几何体。支持 Length 和 Segments 参数 |
| Lathe | `UGeomModifier_Lathe` | 将 Brush Shape 围绕枢轴点旋转成型。需要在正交视口中操作，支持 TotalSegments、Segments、AlignToSide 参数 |
| Pen | `UGeomModifier_Pen` | 在正交视口中逐点绘制多边形。Space 放置顶点，Enter 闭合。支持自动挤出（bAutoExtrude）、凸多边形优化（bCreateConvexPolygons）、BrushShape 模式 |
| Clip | `UGeomModifier_Clip` | 沿平面裁剪 Brush。在正交视口中放置裁剪标记点，支持 bSplit（分割）和 bFlipNormal（翻转法线）选项 |

### 操作修改器（Button，一次性执行）

| 修改器 | 类 | 说明 |
|---|---|---|
| Delete | `UGeomModifier_Delete` | 删除选中的几何元素（顶点、边或多边形） |
| Create | `UGeomModifier_Create` | 从选中的顶点创建新的多边形（需按顺时针顺序选择以确保法线朝外） |
| Flip | `UGeomModifier_Flip` | 翻转选中多边形的法线方向 |
| Split | `UGeomModifier_Split` | 分离选中的多边形 |
| Triangulate | `UGeomModifier_Triangulate` | 将选中的多边形分解为三角形 |
| Optimize | `UGeomModifier_Optimize` | 优化选中的几何体，将可合并的三角形合并为凸多边形（先 Triangulate 再合并） |
| Turn | `UGeomModifier_Turn` | 翻转选中边的连接方向（适用于相邻两个三角形共享的边） |
| Weld | `UGeomModifier_Weld` | 将所有选中的顶点合并到第一个选中的顶点 |

## 编辑器交互

### 选择方式

- **点击选择**：在视口中直接点击顶点、边或多边形
- **Ctrl+点击**：追加/取消选择
- **框选**：支持矩形框选和锥形框选
- **正交视口联动**：在正交视口中选择边或顶点时，自动选择投影位置相同的所有元素

### 特殊操作

- **顶点吸附**：右键点击顶点可将其吸附到最近的网格点，同时移动所有已选顶点
- **枢轴点设置**：Alt+MMB 点击可设置枢轴点位置
- **Shift+拖拽**：旋转顶点（非 Shift 拖拽只平移）
- **Shift+Ctrl+拖拽**：在编辑几何体的同时移动摄像机

## 蓝图用法

此插件为纯编辑器插件，不暴露 `BlueprintCallable` 函数。所有交互通过编辑器 UI 完成。

## C++ 用法

### 头文件引入

```cpp
#include "GeometryModeModule.h"     // FGeometryEditingModes 编辑器模式 ID
#include "GeometryEdMode.h"         // FEdModeGeometry, FModeTool_GeometryModify
#include "EditorGeometry.h"         // FGeomObject, FGeomVertex, FGeomEdge, FGeomPoly
#include "GeomModifier.h"           // UGeomModifier 基类
```

### 检查 Geometry Mode 是否激活

```cpp
// 来源: BrushEditingSubsystemImpl.cpp
#include "EditorModeManager.h"
#include "GeometryModeModule.h"

bool bIsActive = GLevelEditorModeTools().IsModeActive(FGeometryEditingModes::EM_Geometry);
```

### 获取当前编辑模式实例

```cpp
// 来源: GeometryModifiers.cpp
FEdModeGeometry* GeomMode = static_cast<FEdModeGeometry*>(
    GLevelEditorModeTools().GetActiveMode(FGeometryEditingModes::EM_Geometry)
);

if (GeomMode)
{
    // 遍历所有几何对象
    for (FEdModeGeometry::TGeomObjectIterator It = GeomMode->GeomObjectItor(); It; ++It)
    {
        FGeomObjectPtr GeomObject = *It;
        ABrush* Brush = GeomObject->GetActualBrush();
        
        // 访问顶点池
        for (int32 i = 0; i < GeomObject->VertexPool.Num(); ++i)
        {
            FGeomVertex& Vertex = GeomObject->VertexPool[i];
            if (Vertex.IsSelected())
            {
                FVector Position = (FVector)Vertex;
                // ...
            }
        }
    }
}
```

### 自定义几何修改器

```cpp
// 继承 UGeomModifier 或 UGeomModifier_Edit 来创建自定义修改器
UCLASS()
class UGeomModifier_Custom : public UGeomModifier_Edit
{
    GENERATED_UCLASS_BODY()
    
    virtual bool SupportsCurrentSelection() override;
    
protected:
    virtual bool OnApply() override;
};

// 构造函数中设置属性
UGeomModifier_Custom::UGeomModifier_Custom(const FObjectInitializer& ObjectInitializer)
    : Super(ObjectInitializer)
{
    Description = NSLOCTEXT("MyModule", "Custom", "Custom");
    Tooltip = NSLOCTEXT("MyModule", "CustomTooltip", "My custom geometry modifier.");
    bPushButton = true;  // true = 按钮（一次性操作），false = 单选按钮（持续模式）
    bAppearsInToolbar = true;
    ToolbarIconName = TEXT("MyModule.CustomTool");
}

bool UGeomModifier_Custom::SupportsCurrentSelection()
{
    FEdModeGeometry* Mode = static_cast<FEdModeGeometry*>(
        GLevelEditorModeTools().GetActiveMode(FGeometryEditingModes::EM_Geometry));
    return Mode != nullptr && Mode->HavePolygonsSelected();
}

bool UGeomModifier_Custom::OnApply()
{
    FEdModeGeometry* Mode = static_cast<FEdModeGeometry*>(
        GLevelEditorModeTools().GetActiveMode(FGeometryEditingModes::EM_Geometry));
    
    // 获取选中的多边形
    TArray<FGeomPoly*> SelectedPolys;
    Mode->GetSelectedPolygons(SelectedPolys);
    
    for (FGeomPoly* Poly : SelectedPolys)
    {
        FPoly* ActualPoly = Poly->GetActualPoly();
        // 对实际多边形进行操作...
    }
    
    // 重建 BSP
    GEditor->RebuildAlteredBSP();
    return true;
}
```

### 通过 UBrushEditingSubsystem 交互

```cpp
// 来源: BrushEditingSubsystemImpl.h
#include "Subsystems/BrushEditingSubsystem.h"

UBrushEditingSubsystem* Subsystem = GEditor->GetEditorSubsystem<UBrushEditingSubsystem>();
if (Subsystem)
{
    // 检查是否在 Geometry Mode
    bool bActive = Subsystem->IsGeometryEditorModeActive();
    
    // 更新选中 Brush 的几何数据
    Subsystem->UpdateGeometryFromSelectedBrushes();
    
    // 更新单个 Brush 的几何数据
    Subsystem->UpdateGeometryFromBrush(MyBrush);
    
    // 取消所有几何选择
    Subsystem->DeselectAllEditingGeometry();
}
```

## 模块依赖

### GeometryMode 模块

| 模块 | 用途 |
|---|---|
| `BSPUtils` | BSP 操作工具（构建、裁剪、优化） |
| `Core` | 核心引擎功能 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心（Brush、Model 等） |
| `InputCore` | 输入系统 |
| `Slate` | UI 框架 |
| `SlateCore` | Slate 核心 |
| `EditorFramework` | 编辑器框架 |
| `UnrealEd` | 编辑器核心（EdMode、编辑器操作） |
| `RenderCore` | 渲染核心 |
| `LevelEditor` | 关卡编辑器 |
| `NavigationSystem` | 导航系统（NavMesh Bounds Volume 支持） |
| `EditorSubsystem` | 编辑器子系统 |
| `Projects` | 项目信息 |

### BspMode 模块

| 模块 | 用途 |
|---|---|
| `Core` | 核心引擎功能 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `InputCore` | 输入系统 |
| `Slate` | UI 框架 |
| `SlateCore` | Slate 核心 |
| `UnrealEd` | 编辑器核心 |

### TextureAlignMode 模块

| 模块 | 用途 |
|---|---|
| `Core` | 核心引擎功能 |
| `CoreUObject` | UObject 系统 |
| `EditorFramework` | 编辑器框架 |
| `Engine` | 引擎核心 |
| `GeometryMode` | 几何模式核心（共享编辑器模式 ID） |
| `SlateCore` | Slate 核心 |
| `UnrealEd` | 编辑器核心 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-08-04 | `21d73b2` | [Viewport Selection] Generalize Viewport Selection functions so they work with FEditorViewportClient instead of just FLevelEditorViewportClient | 将视口选择函数泛化为支持 `FEditorViewportClient`，提高代码复用性。属于编辑器框架重构的一部分 |
| 2025-06-25 | `84880cb` | Updated dll storage on code using UnrealCodeFixup with LyraEditor win64 as target | 自动代码修复工具的编译更新，无功能变更 |
| 2025-03-14 | `7ce30a0` | Fix simple cases of unreachable code for loops that terminate after one iteration | 静态分析修复，移除不可达代码。无功能变更 |

### 维护评价

**维护不活跃**。

- **创建时间**：2019 年 10 月（从 UE4 时代的旧 Geometry Mode 迁移重构而来，实际历史可追溯到 UE1/UE2 时代）
- **最近更新**：最近 3 次提交均为框架级重构或编译修复，没有功能性更新
- **功能状态**：功能完整且稳定，但 BSP 工作流本身已不再是 UE5 的推荐关卡设计方式
- **已知限制**：
  - BSP 编辑是纯编辑器功能，不支持运行时使用
  - 不暴露 BlueprintCallable API，无法通过蓝图扩展
  - 不支持自动化测试（未找到相关测试用例）
  - Lathe 修改器要求 Brush Shape 类型的 Actor，且必须在正交视口中操作
  - Extrude 修改器要求 Local 坐标系
- **推荐程度**：如果你的工作流依赖 BSP 关卡设计，这个插件是必需的。但 Epic Games 的发展方向是 Static Mesh + Modeling Tools（编辑器内建模），新项目建议优先使用 Modeling Tools 而非 BSP

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/GeometryMode)
- 官方文档：无（.uplugin 中 DocsURL 为空）
