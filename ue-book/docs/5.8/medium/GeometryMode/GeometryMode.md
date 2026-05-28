# Geometry Mode

> Geometry and BSP editing

| 属性 | 值 |
|---|---|
| 中文名 | 几何编辑模式 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（编辑器图标资源） |
| 模块 | `GeometryMode` (Editor), `BspMode` (Editor), `TextureAlignMode` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2019-10-28 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/GeometryMode) | |

## 用途

GeometryMode 插件提供了对 BSP 画刷（Brush）进行底层几何编辑的能力。它是 UE 编辑器中"几何模式"的核心实现，允许关卡设计师直接操作画刷的**顶点、边和多边形**，而不仅仅是整体移动/旋转/缩放画刷。

这个插件存在是因为 UE 的 BSP 系统需要一种方式来进行精细的几何编辑——比如切割、挤压、删除面片、焊接顶点等操作。没有这个插件，设计师只能对整个画刷做变换，无法进行局部几何修改。

## 使用场景

- 你在使用 BSP 画刷搭建关卡灰盒（Blockout）→ 需要对画刷进行顶点/边/面编辑
- 你需要用平面切割一个画刷将其一分为二 → 使用 Clip 工具
- 你需要将多边形沿轴旋转生成圆形结构 → 使用 Lathe（车削）工具
- 你需要将画刷的某个面向外拉伸创建新体积 → 使用 Extrude（挤压）工具
- 你需要在场景中手绘创建新画刷 → 使用 Pen（画笔）工具
- 你需要优化画刷的多边形划分 → 使用 Optimize/Triangulate 工具

## 蓝图用法

此插件主要作为编辑器模式工具，不提供 `BlueprintCallable` API。所有交互通过编辑器 UI 完成。

### 编辑器模式

插件注册了三个编辑器模式：

| 模式 ID | 说明 | 所在模块 |
|---|---|---|
| `EM_Geometry` | 几何编辑模式（顶点/边/面编辑） | GeometryMode |
| `EM_Bsp` | BSP 画刷编辑模式 | BspMode |
| `EM_TextureAlign` | 纹理对齐模式 | TextureAlignMode |

### 几何修改器（Modifiers）

进入几何模式后，工具栏会显示以下修改器：

| 修改器 | 说明 | 支持的选择类型 |
|---|---|---|
| `Edit` | 默认编辑（移动选中的几何元素） | 顶点/边/面 |
| `Extrude` | 沿法线方向挤压选中的面 | 多边形 |
| `Clip` | 用平面裁切画刷 | 多边形 |
| `Lathe` | 绕轴旋转生成新画刷 | 多边形 |
| `Delete` | 删除选中的几何元素 | 顶点/边/面 |
| `Create` | 创建新面片 | 顶点 |
| `Split` | 分割选中的边 | 边 |
| `Weld` | 焊接顶点 | 顶点 |
| `Flip` | 翻转面法线 | 多边形 |
| `Turn` | 反转面绕序 | 多边形 |
| `Triangulate` | 三角化选中的多边形 | 多边形 |
| `Optimize` | 优化多边形划分（合并共面三角形） | 多边形 |
| `Pen` | 手绘创建新画刷形状 | 无（全新创建） |

## C++ 用法

此插件的 C++ API 主要面向编辑器扩展，用于程序化操作几何模式数据。

### 头文件引入

```cpp
#include "EditorGeometry.h"
#include "GeometryEdMode.h"
#include "GeometryModeModule.h"
```

### 基本用法

获取几何编辑模式实例并查询选择状态：

```cpp
#include "EditorGeometry.h"
#include "GeometryEdMode.h"

// 获取几何模式实例
FEdModeGeometry* GeomMode = static_cast<FEdModeGeometry*>(
    GLevelEditorModeTools().FindMode(FGeometryEditingModes::EM_Geometry)
);

if (GeomMode)
{
    // 查询选择状态
    int32 SelectionState = GeomMode->GetSelectionState();
    
    // 获取选中的多边形数量
    int32 PolyCount = GeomMode->CountSelectedPolygons();
    
    // 获取选中的边数量
    int32 EdgeCount = GeomMode->CountSelectedEdges();
    
    // 获取选中的顶点数量
    int32 VertCount = GeomMode->CountSelectedVertices();
    
    // 获取所有选中的多边形
    TArray<FGeomPoly*> SelectedPolys;
    GeomMode->GetSelectedPolygons(SelectedPolys);
    
    // 遍历几何对象
    for (FEdModeGeometry::TGeomObjectIterator It = GeomMode->GeomObjectItor(); It; ++It)
    {
        FGeomObjectPtr GeomObject = *It;
        ABrush* Brush = GeomObject->GetActualBrush();
        
        // 获取画刷的顶点/边/面池
        const TArray<FGeomVertex>& Verts = GeomObject->VertexPool;
        const TArray<FGeomEdge>& Edges = GeomObject->EdgePool;
        const TArray<FGeomPoly>& Polys = GeomObject->PolyPool;
    }
}
```

### 进阶用法

操作几何对象的选择系统：

```cpp
#include "EditorGeometry.h"

// FGeomObject 是几何模式的核心数据结构
// 每个选中的 ABrush 对应一个 FGeomObject
void ExploreGeometryObject(FGeomObjectPtr GeomObject)
{
    // 确保内部数据已编译
    GeomObject->ComputeData();
    
    // 获取画刷引用
    ABrush* Brush = GeomObject->GetActualBrush();
    
    // 获取多边形的实际数据
    for (FGeomPoly& Poly : GeomObject->PolyPool)
    {
        // 获取实际的 FPoly 数据
        FPoly* ActualPoly = Poly.GetActualPoly();
        int32 PolyIndex = Poly.ActualPolyIndex;
        
        // 获取该多边形的边索引
        const TArray<int>& EdgeIndices = Poly.EdgeIndices;
        
        // 检查选择状态
        bool bSelected = Poly.IsSelected();
        FVector MidPoint = Poly.GetMidPoint();
    }
    
    // 获取唯一边列表
    TArray<FGeomEdge> UniqueEdges;
    GeomObject->CompileUniqueEdgeArray(&UniqueEdges);
    
    // 将修改后的数据写回源画刷
    GeomObject->SendToSource();
    GeomObject->FinalizeSourceData();
}
```

使用 Hit Proxy 进行几何拾取：

```cpp
#include "EditorGeometry.h"

// Hit Proxy 用于在视口中拾取几何元素
// HGeomPolyProxy  - 多边形拾取代理
// HGeomEdgeProxy  - 边拾取代理
// HGeomVertexProxy - 顶点拾取代理

// 处理点击事件（在子系统中）
void ProcessHitProxy(HHitProxy* HitProxy)
{
    if (HGeomPolyProxy* PolyProxy = HitCast<HGeomPolyProxy>(HitProxy))
    {
        FGeomObject* GeomObj = PolyProxy->GetGeomObject();
        int32 PolyIndex = PolyProxy->PolyIndex;
        // 处理多边形点击...
    }
    else if (HGeomEdgeProxy* EdgeProxy = HitCast<HGeomEdgeProxy>(HitProxy))
    {
        FGeomObject* GeomObj = EdgeProxy->GetGeomObject();
        int32 EdgeIndex = EdgeProxy->EdgeIndex;
        // 处理边点击...
    }
    else if (HGeomVertexProxy* VertProxy = HitCast<HGeomVertexProxy>(HitProxy))
    {
        FGeomObject* GeomObj = VertProxy->GetGeomObject();
        int32 VertexIndex = VertProxy->VertexIndex;
        // 处理顶点点击...
    }
}
```

## Demo 示例

自定义几何修改器的最小示例：

```cpp
// MyGeomModifier.h
#pragma once

#include "GeomModifier.h"
#include "MyGeomModifier.generated.h"

UCLASS()
class UMyGeomModifier : public UGeomModifier_Edit
{
    GENERATED_UCLASS_BODY()

    UPROPERTY(EditAnywhere, Category=Settings)
    float ScaleFactor;

    virtual bool SupportsCurrentSelection() override;
    virtual void Initialize() override;

protected:
    virtual bool OnApply() override;
};
```

```cpp
// MyGeomModifier.cpp
#include "MyGeomModifier.h"
#include "EditorGeometry.h"
#include "GeometryEdMode.h"

UMyGeomModifier::UMyGeomModifier()
{
    Description = NSLOCTEXT("MyModifier", "MyModifier", "My Scale");
    Tooltip = NSLOCTEXT("MyModifier", "MyModifierTip", "Scale selected vertices by a factor");
    ScaleFactor = 1.0f;
}

bool UMyGeomModifier::SupportsCurrentSelection()
{
    // 仅在有顶点选中时启用
    FEdModeGeometry* GeomMode = static_cast<FEdModeGeometry*>(
        GLevelEditorModeTools().FindMode(FGeometryEditingModes::EM_Geometry)
    );
    return GeomMode && GeomMode->HaveVerticesSelected();
}

void UMyGeomModifier::Initialize()
{
    ScaleFactor = 1.0f;
}

bool UMyGeomModifier::OnApply()
{
    // 获取所有选中的顶点
    TArray<FGeomVertex*> SelectedVerts;
    FEdModeGeometry* GeomMode = static_cast<FEdModeGeometry*>(
        GLevelEditorModeTools().FindMode(FGeometryEditingModes::EM_Geometry)
    );
    GeomMode->GetSelectedVertices(SelectedVerts);

    for (FGeomVertex* Vert : SelectedVerts)
    {
        // 缩放顶点位置
        FVector Pos = *static_cast<FVector3f*>(Vert);
        *Vert = FVector3f(Pos * ScaleFactor);
    }

    return SelectedVerts.Num() > 0;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine/Slate 等） | |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `fbd199ea` | [Backout] - CL53903539 | 回退某次提交变更 |
| 2026-05-14 | `5c94be5d` | Global snapping toggle in toolbar, and (red) indicator when one or more snapping options are enabled | 工具栏添加全局吸附开关，吸附启用时显示红色指示器 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移到 UE_LOGF 格式 |
| 2026-02-25 | `12a309dc` | Remove as many PVS suppressions as possible that are no longer needed | 清理不再需要的 PVS 静态分析抑制项 |
| 2026-02-03 | `61433296` | Rename FViewMatrices members to follow the <Source>To<Target> pattern for transforms, to reduce ambi | 重命名视图矩阵成员以遵循 SourceToTarget 命名模式 |

### 维护评价

**活跃维护中**。该插件最近 6 个月内有多次更新，包含功能增强（全局吸附开关）和代码质量改进。作为 UE BSP 系统的核心编辑工具，它是编辑器基础设施的一部分，由 Epic 团队持续维护。

主要特点：
- 自 2019 年从引擎内部迁移到插件形式
- 持续获得功能更新和代码维护
- 作为 BSP 编辑的唯一途径，短期内不会被废弃
- 现代 UE5 项目更多使用 Static Mesh 而非 BSP，但灰盒搭建阶段仍常用

**推荐使用**：如果你的工作流涉及 BSP 画刷编辑，这是必须使用的插件。对于纯 Static Mesh 项目，可以安全禁用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/GeometryMode)