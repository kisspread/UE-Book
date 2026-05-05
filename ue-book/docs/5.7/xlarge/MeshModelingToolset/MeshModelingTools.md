# Mesh Modeling Toolset

> A set of modules implementing 3D mesh creation and editing based on the Interactive Tools Framework（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `MeshModelingTools` (Runtime), `MeshModelingToolsEditorOnly` (Runtime), `ModelingComponents` (Runtime), `ModelingComponentsEditorOnly` (Runtime), `ModelingOperators` (Runtime), `ModelingOperatorsEditorOnly` (Runtime), `SkeletalMeshModifiers` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-10-01 |
| 年龄标签 | 🆕（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MeshModelingToolset) | |

## 用途

Mesh Modeling Toolset 是 UE5 内置的**程序化网格建模与编辑工具集**，基于 Interactive Tools Framework 构建。它解决的核心问题是：**在引擎内直接进行 3D 网格的创建、编辑和雕刻，而无需导出到外部 DCC 工具（如 Blender、Maya）**。

该插件是 UE5 **Modeling Mode（建模模式）** 的底层实现，提供了从基础布尔运算到高级多边形编辑的完整工具链。与传统的静态网格编辑不同，它基于 `FDynamicMesh3` 动态网格系统，支持实时交互式操作和非破坏性工作流。

**为什么存在**：UE5 需要一个原生的、高性能的网格编辑能力，用于关卡设计中的快速原型制作、资产修正、UV 重排等场景，避免在引擎和外部工具之间频繁切换。

## 使用场景

- 你需要在引擎内快速合并多个网格体 → 用 **Combine Meshes** 工具
- 你需要对网格进行布尔运算（并集、差集、交集） → 用 **CSG Meshes** 工具
- 你需要雕刻网格表面细节 → 用 **Sculpting** 系列画笔（移动、膨胀、捏合、平面等）
- 你需要重新拓扑或优化网格三角形分布 → 用 **Remesh Mesh** 工具
- 你需要重新计算或布局 UV → 用 **Recompute UVs** / **UV Layout** 工具
- 你需要移除被遮挡的三角形（用于 LOD 优化） → 用 **Remove Occluded Triangles** 工具
- 你需要用一个网格切割另一个网格 → 用 **Cut Mesh With Mesh** 工具
- 你需要对多边形面进行内缩/外扩、切割、插入边循环等精细编辑 → 用 **PolyEdit** 系列活动
- 你需要平滑或偏移网格表面 → 用 **Smooth Mesh** / **Offset Mesh** 工具
- 你需要焊接网格边界边 → 用 **Weld Mesh Edges** 工具
- 你需要将一个网格投影到另一个网格上 → 用 **Project To Target** 工具
- 你需要通过绘制轮廓并旋转生成旋转体 → 用 **Draw And Revolve** 工具
- 你需要变形多边形组（线性或拉普拉斯变形） → 用 **Deform Mesh Polygons** 工具

## 模块架构

该插件由 7 个模块组成，按职责分层：

```
┌─────────────────────────────────────────────────┐
│              MeshModelingTools                   │  ← 具体工具实现（画笔、布尔、UV 等）
│              MeshModelingToolsEditorOnly         │  ← 编辑器专用工具
├─────────────────────────────────────────────────┤
│              ModelingComponents                  │  ← 通用组件（预览网格、机制等）
│              ModelingComponentsEditorOnly        │  ← 编辑器专用组件
├─────────────────────────────────────────────────┤
│              ModelingOperators                   │  ← 底层几何运算算子
│              ModelingOperatorsEditorOnly         │  ← 编辑器专用算子
├─────────────────────────────────────────────────┤
│              SkeletalMeshModifiers               │  ← 骨骼网格修改器
└─────────────────────────────────────────────────┘
```

## 子模块文档

由于本插件规模为 **xlarge**（850+ 源文件），按功能域拆分为以下子模块文档：

| 子模块 | 说明 | 文档链接 |
|---|---|---|
| **Sculpting** | 雕刻画笔系统（移动、膨胀、捏合、平面、组绘制等） | [Sculpting.md](Sculpting.md) |
| **PolyEdit Activities** | 多边形编辑活动（切割、内缩/外扩、插入边、UV 投影等） | [PolyEdit.md](PolyEdit.md) |
| **Mesh Operations** | 网格操作工具（布尔、合并、切割、重网格化、投影等） | [MeshOperations.md](MeshOperations.md) |
| **UV Tools** | UV 工具（重计算 UV、UV 布局） | [UVTools.md](UVTools.md) |
| **Mesh Processing** | 网格处理工具（平滑、偏移、焊接、移除遮挡三角形等） | [MeshProcessing.md](MeshProcessing.md) |
| **Deformation** | 变形工具（多边形变形、旋转体生成） | [Deformation.md](Deformation.md) |
| **Properties & Commands** | 通用属性集和选择编辑命令 | [PropertiesAndCommands.md](PropertiesAndCommands.md) |

## 维护状态

### 近期更新

```
- e7543c6742ad ModelingTools: Fix spacing mode in sculpt tools, which behaved poorly when moving across ridges.
- 06d857d4bede ModelingTools: Fix potential crash in sculpt tool from changing the TriangleROIArray out from under an asynchronous octree update.
- cdb09167637a Modeling Mode: add slight delay to appearance of working material during displace tool computations #JIRA UE-184461
```

### 维护评价

**活跃维护**。该插件是 UE5 Modeling Mode 的核心实现，由 Epic Games 持续维护。从近期 commit 可以看出，团队仍在积极修复雕刻工具的 bug（间距模式、异步八叉树崩溃）并优化用户体验。作为 UE5 编辑器建模功能的基础设施，该插件在每个引擎版本中都会收到更新。

**注意事项**：
- `.uplugin` 中标记为 `IsBetaVersion: true`，表明 API 可能在未来版本中发生变化
- `Hidden: true` 表示该插件不在插件浏览器中直接显示，而是通过 Modeling Mode 间接使用
- `EnabledByDefault: false`（`Installed: false`），需要通过启用 Modeling Mode 来激活

**推荐使用**：✅ 推荐。这是 UE5 官方建模工具的底层实现，稳定性和性能都有保障。但注意其 Beta 状态意味着 API 不保证向后兼容。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MeshModelingToolset)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/modeling-tools-in-unreal-engine/)（UE5 建模工具文档）

---

# Sculpting 子模块

> 雕刻画笔系统，提供基于 FDynamicMesh3 的交互式网格雕刻能力。

## 概述

Sculpting 子模块实现了完整的网格雕刻画笔框架，包括基础画笔操作类、多种画笔操作实现（移动、膨胀、捏合、平面、组绘制、雕刻层擦除等）、以及衰减函数库。所有画笔操作都基于 `FMeshSculptBrushOp` 基类，通过 `FSculptBrushStamp` 结构传递画笔状态。

## 核心类

### 画笔操作基类

| 类 | 说明 |
|---|---|
| `FMeshSculptBrushOp` | 所有雕刻画笔操作的基类，定义 `ApplyStamp` 接口 |
| `UMeshSculptBrushOpProps` | 画笔属性基类（强度、衰减、深度等） |
| `UDynamicMeshBrushTool` | 动态网格画笔工具基类，继承自 `UBaseBrushTool` |

### 画笔操作实现

| 画笔 | 属性类 | 操作类 | 说明 |
|---|---|---|---|
| **Move** | `UMoveBrushOpProps` | `FMoveBrushOp` | 沿画笔移动方向移动顶点，支持轴约束过滤 |
| **Inflate** | `UInflateBrushOpProps` | `FInflateBrushOp` | 沿顶点法线方向膨胀/收缩 |
| **Pinch** | `UPinchBrushOpProps` | `FPinchBrushOp` | 向画笔中心捏合顶点，支持垂直阻尼 |
| **Plane** | `UPlaneBrushOpProps` | `FPlaneBrushOp` | 将顶点推平到画笔平面 |
| **ViewAlignedPlane** | `UViewAlignedPlaneBrushOpProps` | — | 将顶点推平到视图对齐的平面 |
| **FixedPlane** | `UFixedPlaneBrushOpProps` | — | 将顶点推平到固定平面 |
| **Group Paint** | `UGroupEraseBrushOpProps` | `FGroupEraseBrushOp` | 擦除多边形组 |
| **Erase Sculpt Layer** | `UEraseSculptLayerBrushOpProps` | `FEraseSculptLayerBrushOp` | 擦除雕刻层偏移 |

### 衰减函数库

`UE::SculptFalloffs` 命名空间提供多种预定义衰减函数：

| 函数 | 说明 |
|---|---|
| `MakeStandardSmoothFalloff()` | 标准平滑衰减（三次方） |
| `MakeLinearFalloff()` | 线性衰减 |
| `MakeInverseFalloff()` | 反向衰减（三次方） |
| `MakeRoundFalloff()` | 圆形衰减 |
| `MakeSmoothBoxFalloff()` | 平滑盒形衰减 |

### 工具类

| 类 | 说明 |
|---|---|
| `UDynamicMeshBrushTool` | 动态网格画笔工具基类，管理 `UPreviewMesh`、命中测试、烘焙变换 |
| `UMeshSculptLayerProperties` | 雕刻层属性管理（活动层、层权重、添加/删除/移动层） |

## C++ 用法

### 头文件引入

```cpp
#include "Sculpting/MeshBrushOpBase.h"
#include "Sculpting/MeshInflateBrushOps.h"
#include "Sculpting/MeshMoveBrushOps.h"
#include "Sculpting/MeshSculptUtil.h"
```

### 自定义画笔操作

```cpp
// 来源: MeshModelingTools/Public/Sculpting/MeshInflateBrushOps.h
// 创建自定义画笔操作：沿法线方向移动顶点

class FMyCustomBrushOp : public FMeshSculptBrushOp
{
public:
    virtual ESculptBrushOpTargetType GetBrushTargetType() const override
    {
        return ESculptBrushOpTargetType::SculptMesh; // 操作实时雕刻网格
    }

    virtual void ApplyStamp(const FDynamicMesh3* Mesh, 
                            const FSculptBrushStamp& Stamp, 
                            const TArray<int32>& Vertices, 
                            TArray<FVector3d>& NewPositionsOut) override
    {
        double UsePower = Stamp.Direction * Stamp.Power * Stamp.Radius * Stamp.DeltaTime;

        ParallelFor(Vertices.Num(), [&](int32 k)
        {
            int32 VertIdx = Vertices[k];
            FVector3d OrigPos = Mesh->GetVertex(VertIdx);
            FVector3d Normal = UE::Geometry::FMeshNormals::ComputeVertexNormal(*Mesh, VertIdx);
            
            double Falloff = GetFalloff().Evaluate(Stamp, OrigPos);
            FVector3d NewPos = OrigPos + Falloff * UsePower * Normal;
            NewPositionsOut[k] = NewPos;
        });
    }
};
```

### 使用雕刻层

```cpp
// 来源: MeshModelingTools/Public/Properties/MeshSculptLayerProperties.h
// 管理雕刻层的权重和活动层

UMeshSculptLayerProperties* LayerProps = NewObject<UMeshSculptLayerProperties>();
LayerProps->Init(ToolAPI, 0); // 初始化，0 个锁定基础层

// 添加新层
LayerProps->AddLayer();

// 设置活动层
LayerProps->SetActiveLayer(1);

// 设置层权重
LayerProps->SetLayerWeight(0, 0.5, 0); // 层索引, 权重, 变更类型
```

### 法线重计算

```cpp
// 来源: MeshModelingTools/Public/Sculpting/MeshSculptUtil.h
// 高效地只重计算受影响区域的法线

using namespace UE::SculptUtil;

TSet<int32> ModifiedTris;
// ... 收集被修改的三角形 ID ...

TSet<int32> ElementSetBuffer;
TArray<int32> NormalsBuffer;

// 重计算 overlay 法线（仅受影响区域）
RecalculateNormals_Overlay(Mesh, ModifiedTris, ElementSetBuffer, NormalsBuffer);

// 或者重计算顶点法线
RecalculateNormals_PerVertex(Mesh, ModifiedTris, ElementSetBuffer, NormalsBuffer);
```

---

# PolyEdit Activities 子模块

> 多边形编辑活动系统，提供基于 GroupTopology 的高级网格编辑操作。

## 概述

PolyEdit Activities 实现了多边形编辑模式下的各种交互式活动（Activity），包括切割面、内缩/外扩、插入边/边循环、平面投影 UV 等。这些活动基于 `UInteractiveToolActivity` 接口，通过 `UPolyEditActivityContext` 共享上下文数据。

## 核心类

### 活动上下文

| 类 | 说明 |
|---|---|
| `UPolyEditActivityContext` | 活动共享上下文，包含当前网格、拓扑、空间索引、选择机制等 |
| `UPolyEditPreviewMesh` | 编辑预览网格 |
| `UPolyEditCommonProperties` | 通用编辑属性 |

### 活动实现

| 活动 | 属性类 | 说明 |
|---|---|---|
| **Cut Faces** | `UPolyEditCutProperties` | 沿路径切割面，支持法线方向/视图方向、吸附顶点 |
| **Inset/Outset** | `UPolyEditInsetOutsetProperties` | 面的内缩/外扩，支持柔度、边界模式、重投影 |
| **Insert Edge** | `UGroupEdgeInsertionProperties` | 插入组边，支持重三角化/平面切割模式、连续插入 |
| **Insert Edge Loop** | `UEdgeLoopInsertionProperties` | 插入边循环，支持均匀/比例/距离定位模式 |
| **Planar Projection UV** | `UPolyEditSetUVProperties` | 平面投影 UV |

### 选择编辑命令

| 命令 | 说明 |
|---|---|
| `UDeleteGeometrySelectionCommand` | 删除选中的几何元素 |
| `UDisconnectGeometrySelectionCommand` | 断开选中的几何元素 |
| `URetriangulateGeometrySelectionCommand` | 重新三角化选中区域 |
| `UModifyGeometrySelectionCommand` | 修改选择（全选、扩展、收缩、反转等） |
| `UModifyGeometrySelectionCommand_Invert` | 反转选择 |
| `UModifyGeometrySelectionCommand_ExpandToConnected` | 扩展到所有连接的几何体 |
| `UModifyGeometrySelectionCommand_Expand` | 单环扩展 |
| `UModifyGeometrySelectionCommand_Contract` | 单环收缩 |

## C++ 用法

### 头文件引入

```cpp
#include "ToolActivities/PolyEditActivityContext.h"
#include "ToolActivities/PolyEditCutFacesActivity.h"
#include "ToolActivities/PolyEditInsetOutsetActivity.h"
#include "ToolActivities/PolyEditInsertEdgeActivity.h"
#include "ToolActivities/PolyEditInsertEdgeLoopActivity.h"
#include "ToolActivities/PolyEditPlanarProjectionUVActivity.h"
```

### 活动上下文使用

```cpp
// 来源: MeshModelingTools/Public/ToolActivities/PolyEditActivityContext.h
// 活动通过上下文访问共享数据

UPolyEditActivityContext* Context = ...;

// 访问当前网格
TSharedPtr<FDynamicMesh3> CurrentMesh = Context->CurrentMesh;

// 访问拓扑
TSharedPtr<FGroupTopology> Topology = Context->CurrentTopology;

// 发出网格变更（带撤销支持）
Context->EmitCurrentMeshChangeAndUpdate(
    FText::FromString("Cut Faces"),
    MoveTemp(MeshChange),
    OutputSelection
);

// 监听撤销/重做事件
Context->OnUndoRedo.AddLambda([](bool bGroupTopologyChanged) {
    // 处理拓扑变化
});
```

### 创建编辑预览

```cpp
// 来源: MeshModelingTools/Public/ToolActivities/PolyEditActivityUtil.h
// 创建和更新多边形编辑预览

using namespace UE::Geometry::PolyEditActivityUtil;

UPolyEditPreviewMesh* Preview = CreatePolyEditPreviewMesh(Tool, ActivityContext);

// 更新预览材质
UpdatePolyEditPreviewMaterials(Tool, ActivityContext, *Preview, 
    EPreviewMaterialType::PreviewMaterial);
```

---

# Mesh Operations 子模块

> 网格操作工具，提供布尔运算、合并、切割、重网格化、投影等核心网格操作。

## 概述

Mesh Operations 子模块实现了各种网格操作工具，这些工具通常选择一个或多个网格作为输入，执行几何操作后生成新的网格输出。它们基于 `UBaseCreateFromSelectedTool`、`UMultiSelectionMeshEditingTool` 或 `USingleSelectionMeshEditingTool` 基类。

## 核心工具

| 工具 | Builder 类 | 工具类 | 说明 |
|---|---|---|---|
| **CSG Meshes** | `UCSGMeshesToolBuilder` | `UCSGMeshesTool` | CSG 布尔运算（并集、差集、交集、修剪） |
| **Combine Meshes** | `UCombineMeshesToolBuilder` | `UCombineMeshesTool` | 合并多个网格为一个，支持复制模式 |
| **Cut Mesh With Mesh** | — | `UCutMeshWithMeshTool` | 用一个网格切割另一个（同时执行减法和交集） |
| **Remesh Mesh** | `URemeshMeshToolBuilder` | `URemeshMeshTool` | 重新网格化，优化三角形分布 |
| **Project To Target** | `UProjectToTargetToolBuilder` | `UProjectToTargetTool` | 将网格投影到目标表面（带重网格化） |

## C++ 用法

### 头文件引入

```cpp
#include "CSGMeshesTool.h"
#include "CombineMeshesTool.h"
#include "CutMeshWithMeshTool.h"
#include "RemeshMeshTool.h"
#include "ProjectToTargetTool.h"
```

### CSG 布尔运算属性

```cpp
// 来源: MeshModelingTools/Public/CSGMeshesTool.h
// 配置 CSG 布尔运算参数

UCSGMeshesToolProperties* CSGProps = NewObject<UCSGMeshesToolProperties>();
CSGProps->Operation = ECSGOperation::DifferenceAB;  // A 减 B
CSGProps->bTryFixHoles = true;                       // 尝试修复孔洞
CSGProps->bTryCollapseEdges = true;                  // 尝试折叠多余边
CSGProps->WindingThreshold = 0.5;                    // 内外判定阈值
CSGProps->bShowNewBoundaries = true;                 // 显示新边界
CSGProps->bUseFirstMeshMaterials = false;            // 保留所有材质
```

### 重网格化配置

```cpp
// 来源: MeshModelingTools/Public/RemeshMeshTool.h
// 配置重网格化参数

URemeshMeshToolProperties* RemeshProps = NewObject<URemeshMeshToolProperties>();
RemeshProps->TargetTriangleCount = 1000;             // 目标三角形数
RemeshProps->SmoothingType = ERemeshSmoothingType::MeanValue; // 平滑类型
RemeshProps->bDiscardAttributes = false;             // 保留 UV 和法线
RemeshProps->bPreserveSharpEdges = true;             // 保留锐边
RemeshProps->RemeshType = ERemeshType::FullPass;     // 完整遍历模式
RemeshProps->RemeshIterations = 10;                  // 迭代次数
```

### 投影到目标

```cpp
// 来源: MeshModelingTools/Public/ProjectToTargetTool.h
// 将一个网格投影到另一个网格表面

UProjectToTargetToolProperties* ProjProps = NewObject<UProjectToTargetToolProperties>();
ProjProps->bWorldSpace = true;                       // 世界空间投影
ProjProps->bParallel = true;                         // 并行处理
ProjProps->SurfaceProjectionSpeed = 0.2f;            // 表面投影速度
ProjProps->NormalAlignmentSpeed = 0.2f;              // 法线对齐速度
ProjProps->bSmoothInFillAreas = true;                // 填充区域平滑
```

---

# UV Tools 子模块

> UV 工具，提供 UV 重计算和 UV 布局功能。

## 概述

UV Tools 子模块实现了两个 UV 相关工具：**Recompute UVs**（基于现有网格分段重新计算 UV）和 **UV Layout**（重新排列 UV 布局）。两者都支持 UV 通道选择、材质预览和 UV 布局可视化。

## 核心类

| 工具 | Builder 类 | 工具类 | 说明 |
|---|---|---|---|
| **Recompute UVs** | `URecomputeUVsToolBuilder` | `URecomputeUVsTool` | 基于多边形组重新计算 UV |
| **UV Layout** | `UUVLayoutToolBuilder` | `UUVLayoutTool` | 重新排列 UV 布局（支持多选） |

### 通用属性

| 属性类 | 说明 |
|---|---|
| `UMeshUVChannelProperties` | UV 通道选择（支持 MeshDescription 和 FDynamicMesh3 初始化） |
| `UExistingMeshMaterialProperties` | 现有网格材质预览（原始/棋盘格/覆盖材质） |
| `URecomputeUVsToolProperties` | UV 重计算参数 |
| `UUVLayoutProperties` | UV 布局参数 |

## C++ 用法

### 头文件引入

```cpp
#include "RecomputeUVsTool.h"
#include "UVLayoutTool.h"
#include "Properties/MeshUVChannelProperties.h"
```

### UV 通道管理

```cpp
// 来源: MeshModelingTools/Public/Properties/MeshUVChannelProperties.h
// 管理 UV 通道选择

UMeshUVChannelProperties* UVProps = NewObject<UMeshUVChannelProperties>();

// 从 FDynamicMesh3 初始化
UVProps->Initialize(DynamicMesh, true);

// 或从 MeshDescription 初始化
UVProps->Initialize(MeshDescription, true);

// 验证选择
if (UVProps->ValidateSelection(true))
{
    int32 ChannelIndex = UVProps->GetSelectedChannelIndex();
    // 使用 ChannelIndex...
}
```

---

# Mesh Processing 子模块

> 网格处理工具，提供平滑、偏移、焊接、移除遮挡三角形等网格后处理功能。

## 概述

Mesh Processing 子模块实现了各种网格后处理工具，用于改善网格质量、修复拓扑问题或优化网格结构。

## 核心工具

| 工具 | Builder 类 | 工具类 | 说明 |
|---|---|---|---|
| **Smooth Mesh** | — | `USmoothMeshTool` | 网格平滑（迭代/隐式/扩散三种模式） |
| **Offset Mesh** | — | `UOffsetMeshTool` | 网格偏移（迭代/隐式两种模式，支持创建壳体） |
| **Weld Mesh Edges** | `UWeldMeshEdgesToolBuilder` | `UWeldMeshEdgesTool` | 焊接网格边界边（支持 T 型接头修复、属性焊接） |
| **Remove Occluded Triangles** | `URemoveOccludedTrianglesToolBuilder` | `URemoveOccludedTrianglesTool` | 移除被遮挡的三角形（绕数/光线投射两种检测方式） |

## C++ 用法

### 头文件引入

```cpp
#include "SmoothMeshTool.h"
#include "OffsetMeshTool.h"
#include "WeldMeshEdgesTool.h"
#include "RemoveOccludedTrianglesTool.h"
```

### 平滑配置

```cpp
// 来源: MeshModelingTools/Public/SmoothMeshTool.h
// 配置网格平滑参数

USmoothMeshToolProperties* SmoothProps = NewObject<USmoothMeshToolProperties>();
SmoothProps->SmoothingType = ESmoothMeshToolSmoothType::Iterative;

// 迭代平滑参数
UIterativeSmoothProperties* IterProps = NewObject<UIterativeSmoothProperties>();
IterProps->SmoothingPerStep = 0.8f;  // 每步平滑量
IterProps->Steps = 10;               // 迭代次数
IterProps->bSmoothBoundary = true;   // 平滑边界
```

### 偏移配置

```cpp
// 来源: MeshModelingTools/Public/OffsetMeshTool.h
// 配置网格偏移参数

UOffsetMeshToolProperties* OffsetProps = NewObject<UOffsetMeshToolProperties>();
OffsetProps->OffsetType = EOffsetMeshToolOffsetType::Iterative;
OffsetProps->Distance = 1.0f;        // 偏移距离（世界单位）
OffsetProps->bCreateShell = false;   // 是否创建厚壳

// 迭代偏移参数
UIterativeOffsetProperties* IterOffsetProps = NewObject<UIterativeOffsetProperties>();
IterOffsetProps->Steps = 10;              // 迭代次数
IterOffsetProps->bOffsetBoundaries = true; // 偏移边界
IterOffsetProps->SmoothingPerStep = 0.0f;  // 每步平滑量
```

### 焊接配置

```cpp
// 来源: MeshModelingTools/Public/WeldMeshEdgesTool.h
// 配置网格边焊接参数

UWeldMeshEdgesToolProperties* WeldProps = NewObject<UWeldMeshEdgesToolProperties>();
WeldProps->Tolerance = FMathf::ZeroTolerance;  // 匹配容差
WeldProps->bOnlyUnique = false;                // 允许非唯一匹配
WeldProps->bResolveTJunctions = false;         // 是否修复 T 型接头
WeldProps->bSplitBowties = true;               // 是否分割蝴蝶结顶点
WeldProps->AttrWeldingMode = EWeldMeshEdgesAttributeUIMode::OnWeldedMeshEdgesOnly;
```

---

# Deformation 子模块

> 变形工具，提供多边形变形和旋转体生成功能。

## 概述

Deformation 子模块实现了两种变形工具：**Deform Mesh Polygons**（基于 GroupTopology 的交互式多边形变形）和 **Draw And Revolve**（绘制轮廓并旋转生成旋转体）。

## 核心工具

| 工具 | Builder 类 | 工具类 | 说明 |
|---|---|---|---|
| **Deform Mesh Polygons** | `UDeformMeshPolygonsToolBuilder` | `UDeformMeshPolygonsTool` | 交互式多边形组变形（线性/拉普拉斯） |
| **Draw And Revolve** | `UDrawAndRevolveToolBuilder` | `UDrawAndRevolveTool` | 绘制轮廓并旋转生成旋转体 |

## C++ 用法

### 头文件引入

```cpp
#include "DeformMeshPolygonsTool.h"
#include "DrawAndRevolveTool.h"
```

### 多边形变形配置

```cpp
// 来源: MeshModelingTools/Public/DeformMeshPolygonsTool.h
// 配置多边形变形策略

UDeformMeshPolygonsTransformProperties* DeformProps = 
    NewObject<UDeformMeshPolygonsTransformProperties>();

// 线性变形（快速，适合刚性变形）
DeformProps->DeformationStrategy = EGroupTopologyDeformationStrategy::Linear;

// 或拉普拉斯变形（平滑，适合有机变形）
DeformProps->DeformationStrategy = EGroupTopologyDeformationStrategy::Laplacian;

// 快速变换器模式
DeformProps->QuickTransformerMode = EQuickTransformerMode::AxisTranslation; // 平移
// 或
DeformProps->QuickTransformerMode = EQuickTransformerMode::AxisRotation;    // 旋转
```

### 旋转体生成配置

```cpp
// 来源: MeshModelingTools/Public/DrawAndRevolveTool.h
// 配置旋转体生成参数

URevolveToolProperties* RevolveProps = NewObject<URevolveToolProperties>();
RevolveProps->CapFillMode = ERevolvePropertiesCapFillMode::Delaunay; // 端盖填充模式
RevolveProps->bClosePathToAxis = true;    // 开放路径连接到轴
RevolveProps->DrawPlaneOrigin = FVector(0, 0, 0);     // 绘制平面原点
RevolveProps->DrawPlaneOrientation = FRotator(90, 0, 0); // 绘制平面方向
RevolveProps->bEnableSnapping = true;     // 启用吸附
```

---

# Properties And Commands 子模块

> 通用属性集和选择编辑命令，被多个工具共享使用。

## 概述

该子模块包含被多个工具共享的通用属性集（材质、统计、约束等）和几何选择编辑命令。

## 通用属性集

| 属性类 | 说明 |
|---|---|
| `UNewMeshMaterialProperties` | 新网格材质属性（材质、UV 缩放、世界空间缩放、线框显示） |
| `UExistingMeshMaterialProperties` | 现有网格材质预览（原始/棋盘格/覆盖材质、UV 通道） |
| `UMeshStatisticsProperties` | 网格统计信息（顶点数、三角形数、UV、属性） |
| `UMeshUVChannelProperties` | UV 通道选择管理 |
| `UMeshConstraintProperties` | 网格约束属性（边界约束、组约束、材质约束） |
| `URemeshProperties` | 重网格化属性（平滑、翻转、分裂、折叠） |
| `UMeshSculptLayerProperties` | 雕刻层管理（活动层、层权重、添加/删除/移动层） |

## C++ 用法

### 材质属性

```cpp
// 来源: MeshModelingTools/Public/Properties/MeshMaterialProperties.h
// 新网格材质配置

UNewMeshMaterialProperties* MatProps = NewObject<UNewMeshMaterialProperties>();
MatProps->Material = SomeMaterial;       // 材质
MatProps->UVScale = 1.0f;               // UV 缩放
MatProps->bWorldSpaceUVScale = false;    // 是否世界空间缩放
MatProps->bShowWireframe = false;        // 是否显示线框

// 现有网格材质预览
UExistingMeshMaterialProperties* ExistMatProps = NewObject<UExistingMeshMaterialProperties>();
ExistMatProps->MaterialMode = ESetMeshMaterialMode::Checkerboard; // 棋盘格模式
ExistMatProps->CheckerDensity = 20.0f;   // 棋盘格密度
```

### 网格统计

```cpp
// 来源: MeshModelingTools/Public/Properties/MeshStatisticsProperties.h
// 获取网格统计信息

UMeshStatisticsProperties* StatsProps = NewObject<UMeshStatisticsProperties>();
StatsProps->Update(*DynamicMesh);

// StatsProps->Mesh 包含顶点/三角形/边的统计字符串
// StatsProps->UV 包含 UV 通道信息
// StatsProps->Attributes 包含属性层信息
```

### 重网格化约束

```cpp
// 来源: MeshModelingTools/Public/Properties/RemeshProperties.h
// 配置重网格化约束

UMeshConstraintProperties* ConstraintProps = NewObject<UMeshConstraintProperties>();
ConstraintProps->bPreserveSharpEdges = true;
ConstraintProps->MeshBoundaryConstraint = EMeshBoundaryConstraint::Fixed;
ConstraintProps->GroupBoundaryConstraint = EGroupBoundaryConstraint::Refine;
ConstraintProps->MaterialBoundaryConstraint = EMaterialBoundaryConstraint::Free;
ConstraintProps->bPreventNormalFlips = true;
ConstraintProps->bPreventTinyTriangles = true;
```

## 模块依赖

从各模块的 Build.cs 提取的独特依赖（省略 Core/CoreUObject/Engine/Slate 等常见依赖）：

| 模块 | 用途 |
|---|---|
| `GeometryFramework` | 动态网格组件（UDynamicMeshComponent） |
| `GeometryCore` | 几何核心（FDynamicMesh3、空间索引等） |
| `GeometryAlgorithms` | 几何算法（重网格化、布尔运算、UV 等） |
| `ModelingOperators` | 建模算子基类 |
| `ModelingComponents` | 建模组件（预览网格、机制等） |
| `InteractiveToolsFramework` | 交互工具框架 |
| `MeshConversion` | MeshDescription 与 FDynamicMesh3 互转 |
| `MeshDescription` | 网格描述数据结构 |
| `MeshModelingTools` | 建模工具实现 |
| `SkeletalMeshModifiers` | 骨骼网格修改器 |