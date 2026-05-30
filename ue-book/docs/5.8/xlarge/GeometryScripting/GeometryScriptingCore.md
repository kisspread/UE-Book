# Geometry Script

> Geometry Script provides a library of functions for creating and editing Meshes in Blueprints and Python

| 属性 | 值 |
|---|---|
| 中文名 | 几何脚本 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、测试资源） |
| 模块 | `GeometryScriptingCore` (Runtime), `GeometryScriptingEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2024-02-01 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GeometryScripting) | |

## 用途

Geometry Script 是 UE 内置的 **程序化网格编辑工具库**，让你在蓝图和 Python 中完整操控 `UDynamicMesh` 对象。它解决的核心问题是：**在运行时/编辑器中不依赖编辑器工具，纯靠脚本完成网格的创建、变形、修复、UV 操作、碰撞生成、烘焙等全套几何处理流水线**。

与 MeshModelingToolset 提供的交互式工具不同，Geometry Script 的所有函数都是蓝图可调用的静态函数库，适合自动化管线、数据驱动的资产生成、以及 DynamicMeshComponent 的运行时操作。

**EnabledByDefault=false**，需要在项目设置中手动启用。

## 子模块概览

本插件包含 100+ 个源文件，按功能领域分为以下子模块：

| 子模块 | 核心文件 | 功能概述 |
|---|---|---|
| [碰撞](docs/large/GeometryScripting/Collision.md) | CollisionFunctions.h | 简单碰撞生成、设置、合并、简化 |
| [烘焙](docs/large/GeometryScripting/Bake.md) | MeshBakeFunctions.h | 纹理烘焙、顶点烘焙、渲染捕获 |
| [网格编辑](docs/large/GeometryScripting/MeshBasicEdit.md) | MeshBasicEditFunctions.h | 顶点/三角形增删改、网格拼接 |
| [骨骼权重](docs/large/GeometryScripting/BoneWeights.md) | MeshBoneWeightFunctions.h | 蒙皮权重操作、骨骼信息查询 |
| [布尔运算](docs/large/GeometryScripting/Booleans.md) | MeshBooleanFunctions.h | 并集/交集/差集、平面切割、镜像 |
| [分解](docs/large/GeometryScripting/Decomposition.md) | MeshDecompositionFunctions.h | 连接岛分割、材质/PolyGroup 分割 |
| [变形](docs/large/GeometryScripting/Deform.md) | MeshDeformFunctions.h | 弯曲/扭曲/Perlin噪声/纹理置换 |
| [材质](docs/large/GeometryScripting/Materials.md) | MeshMaterialFunctions.h | MaterialID 管理、重映射 |
| [建模](docs/large/GeometryScripting/Modeling.md) | MeshModelingFunctions.h | 挤出/倒角/内缩/偏移面 |
| [法线](docs/large/GeometryScripting/Normals.md) | MeshNormalsFunctions.h | 法线翻转/重计算、切线操作 |
| [PolyGroup](docs/large/GeometryScripting/PolyGroups.md) | MeshPolygroupFunctions.h | PolyGroup 创建/查询/转换 |
| [基础体](docs/large/GeometryScripting/Primitives.md) | MeshPrimitiveFunctions.h | Box/Sphere/Cylinder/Rectangle/Extrude |
| [查询](docs/large/GeometryScripting/Query.md) | MeshQueryFunctions.h | 网格信息、顶点/三角形/UV 查询 |
| [重网格化](docs/large/GeometryScripting/Remesh.md) | MeshRemeshFunctions.h | 均匀/自适应重网格化 |
| [修复](docs/large/GeometryScripting/Repair.md) | MeshRepairFunctions.h | 焊接/填充孔/去隐藏三角形/修复退化 |
| [采样](docs/large/GeometryScripting/Sampling.md) | MeshSamplingFunctions.h | 泊松盘采样、非均匀采样 |
| [选择](docs/large/GeometryScripting/Selection.md) | MeshSelectionFunctions.h | 网格选择创建/转换/合并 |
| [简化](docs/large/GeometryScripting/Simplify.md) | MeshSimplifyFunctions.h | QEM/集群/平面简化 |
| [UV](docs/large/GeometryScripting/UVs.md) | MeshUVFunctions.h | UV 重计算/布局/打包/转换 |
| [顶点颜色](docs/large/GeometryScripting/VertexColors.md) | MeshVertexColorFunctions.h | 顶点颜色设置/模糊/传输 |
| [Asset 互操作](docs/large/GeometryScripting/AssetFunctions.md) | MeshAssetFunctions.h | StaticMesh/SkeletalMesh 读写 |
| [类型](docs/large/GeometryScripting/Types.md) | GeometryScriptTypes.h | 核心数据类型定义 |
| [列表工具](docs/large/GeometryScripting/ListUtils.md) | ListUtilityFunctions.h | IndexList/ScalarList/VectorList 操作 |
| [其他](docs/large/GeometryScripting/Misc.md) | Shape/Polygon/PolyPath/PointSet/Spatial/Voxel/Transform/Subdivide/Comparison/WeightMap/SculptLayers/Geodesic/Scene | 基础数学/多边形/空间查询/体素/细分等 |

---

## 蓝图用法

Geometry Script 的所有函数分布在多个静态函数库类中，按 Category 分组。以下按功能域列出核心节点。

### 网格基础操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AppendBox` | 追加一个盒体到网格 | `UGeometryScriptLibrary_MeshPrimitiveFunctions` |
| `AppendSphereLatLong` | 追加经纬球体 | 同上 |
| `AppendCylinder` | 追加圆柱体 | 同上 |
| `AppendRectangleXY` | 追加矩形 | 同上 |
| `AppendTriangle` | 追加单个三角形 | 同上 |
| `CopyMeshFromStaticMesh` | 从 StaticMesh 读取网格 | `UGeometryScriptLibrary_StaticMeshFunctions` |
| `CopyMeshToStaticMesh` | 写回网格到 StaticMesh | 同上 |
| `CopyMeshFromComponent` | 从场景组件拷贝网格 | `UGeometryScriptLibrary_SceneUtilityFunctions` |

### 网格查询

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetMeshInfoString` | 获取网格描述信息 | `UGeometryScriptLibrary_MeshQueryFunctions` |
| `GetMeshBoundingBox` | 获取网格包围盒 | 同上 |
| `GetTriangleCount` | 三角形数量 | 同上 |
| `GetVertexPosition` | 获取顶点位置 | 同上 |
| `GetTrianglePositions` | 获取三角形三个顶点位置 | 同上 |
| `GetIsClosedMesh` | 是否封闭网格 | 同上 |
| `GetNumConnectedComponents` | 连通分量数量 | 同上 |

### 网格编辑

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddVertexToMesh` | 添加顶点 | `UGeometryScriptLibrary_MeshBasicEditFunctions` |
| `AddTriangleToMesh` | 添加三角形 | 同上 |
| `DeleteTriangleFromMesh` | 删除三角形 | 同上 |
| `SetVertexPosition` | 设置顶点位置 | 同上 |
| `AppendMesh` | 拼接另一个网格 | 同上 |
| `MergeMeshVertexPair` | 合并两个顶点 | 同上 |

### 变形

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ApplyBendWarpToMesh` | 弯曲变形 | `UGeometryScriptLibrary_MeshDeformFunctions` |
| `ApplyTwistWarpToMesh` | 扭曲变形 | 同上 |
| `ApplyFlareWarpToMesh` | 膨胀变形 | 同上 |
| `ApplyPerlinNoiseToMesh` | Perlin 噪声位移 | 同上 |
| `ApplyIterativeSmoothingToMesh` | 迭代平滑 | 同上 |
| `ApplyDisplaceFromTextureMap` | 纹理位移 | 同上 |

### 布尔运算

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ApplyMeshBoolean` | 网格布尔运算（并/交/差） | `UGeometryScriptLibrary_MeshBooleanFunctions` |
| `ApplyMeshPlaneCut` | 平面切割 | 同上 |
| `ApplyMeshPlaneSlice` | 平面切片 | 同上 |
| `ApplyMeshMirror` | 镜像 | 同上 |

### 简化与重网格化

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ApplySimplifyToTriangleCount` | 简化到目标三角形数 | `UGeometryScriptLibrary_SimplifyFunctions` |
| `ApplySimplifyToTolerance` | 简化到误差阈值 | 同上 |
| `ApplySimplifyToPlanar` | 平面简化 | 同上 |
| `ApplyUniformRemesh` | 均匀重网格化 | `UGeometryScriptLibrary_RemeshingFunctions` |

### 碰撞

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetStaticMeshCollisionFromMesh` | 从网格生成 StaticMesh 碰撞 | `UGeometryScriptLibrary_CollisionFunctions` |
| `SetDynamicMeshCollisionFromMesh` | 从网格生成 DynamicMesh 碰撞 | 同上 |
| `GenerateCollisionFromMesh` | 生成简单碰撞形状 | 同上 |
| `MergeSimpleCollisionShapes` | 合并碰撞形状 | 同上 |

### UV 操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RecomputeMeshUVs` | 重计算 UV | `UGeometryScriptLibrary_MeshUVFunctions` |
| `LayoutMeshUVs` | UV 布局（打包/堆叠/归一化） | 同上 |
| `RepackMeshUVs` | 重打包 UV | 同上 |
| `CopyMeshUVChannelToMesh` | 导出 UV 为独立网格 | 同上 |

### 选择

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateSelectAllMeshSelection` | 全选 | `UGeometryScriptLibrary_MeshSelectionFunctions` |
| `SelectMeshElementsInBox` | 框选 | 同上 |
| `ConvertMeshSelection` | 转换选择类型 | 同上 |
| `InvertMeshSelection` | 反选 | 同上 |

### 使用示例（蓝图描述）

**场景：从 StaticMesh 读取网格 → 简化 → 写回**

1. 使用 `Copy Mesh From Static Mesh` 节点，连接你的 StaticMesh 资产到 `FromStaticMeshAsset`，创建一个新的 `UDynamicMesh` 对象作为输出。
2. 将输出的 DynamicMesh 连接到 `Apply Simplify To Triangle Count`，设置 `TriangleCount` 为 1000。
3. 将简化后的 DynamicMesh 连接到 `Copy Mesh To Static Mesh`，目标 StaticMesh 设为 `FromStaticMeshAsset`（同名覆盖），设置 `TargetLOD` 为 `SourceModel LOD 0`。
4. 确保 `Outcome` 引脚连接到分支节点，检查是否成功。

**场景：程序化生成基础体并设置碰撞**

1. 创建一个 `UDynamicMesh` 对象（用 `Create Dynamic Mesh Pool` 池化复用）。
2. 连续调用 `Append Box`、`Append Sphere Lat Long`、`Append Cylinder` 等节点追加基础体。
3. 使用 `Set Dynamic Mesh Collision From Mesh` 为 DynamicMeshComponent 生成凸包碰撞。
4. 将 DynamicMesh 赋值给 `UDynamicMeshComponent` 显示。

---

## C++ 用法

### 头文件引入

```cpp
// 核心类型
#include "GeometryScript/GeometryScriptTypes.h"

// 按需引入具体功能模块
#include "GeometryScript/MeshPrimitiveFunctions.h"
#include "GeometryScript/MeshQueryFunctions.h"
#include "GeometryScript/MeshBasicEditFunctions.h"
#include "GeometryScript/CollisionFunctions.h"
#include "GeometryScript/MeshAssetFunctions.h"
```

### 基本用法

从官方测试用例和文档注释提取的标准用法：

```cpp
// 创建一个 DynamicMesh 并追加基础体
UDynamicMesh* Mesh = NewObject<UDynamicMesh>();
FGeometryScriptPrimitiveOptions PrimOptions;
PrimOptions.PolygroupMode = EGeometryScriptPrimitivePolygroupMode::PerFace;
PrimOptions.bFlipOrientation = false;
PrimOptions.UVMode = EGeometryScriptPrimitiveUVMode::Uniform;

// 追加一个盒体到网格
UGeometryScriptLibrary_MeshPrimitiveFunctions::AppendBox(
    Mesh, PrimOptions, FTransform::Identity,
    100.0f, 100.0f, 100.0f,  // DimensionX/Y/Z
    0, 0, 0,                   // StepsX/Y/Z
    EGeometryScriptPrimitiveOriginMode::Base
);

// 查询网格信息
FString Info = UGeometryScriptLibrary_MeshQueryFunctions::GetMeshInfoString(Mesh);
int32 TriCount = UGeometryScriptLibrary_MeshQueryFunctions::GetTriangleCount(Mesh);
FBox Bounds = UGeometryScriptLibrary_MeshQueryFunctions::GetMeshBoundingBox(Mesh);
```

### 进阶用法

从多个功能组合的典型工作流：

```cpp
// 从 StaticMesh 读取 → 简化 → UV 重打包 → 写回
UDynamicMesh* Mesh = NewObject<UDynamicMesh>();
UGeometryScriptDebug* Debug = nullptr;

// 1. 读取
FGeometryScriptCopyMeshFromAssetOptions ReadOptions;
FGeometryScriptMeshReadLOD ReadLOD;
ReadLOD.LODType = EGeometryScriptLODType::SourceModel;
ReadLOD.LODIndex = 0;

EGeometryScriptOutcomePins ReadOutcome;
UGeometryScriptLibrary_StaticMeshFunctions::CopyMeshFromStaticMesh(
    MyStaticMesh, Mesh, ReadOptions, ReadLOD, ReadOutcome, Debug
);

// 2. 简化
FGeometryScriptSimplifyMeshOptions SimplifyOptions;
SimplifyOptions.Method = EGeometryScriptRemoveMeshSimplificationType::AttributeAware;
SimplifyOptions.bAllowSeamCollapse = true;
UGeometryScriptLibrary_SimplifyFunctions::ApplySimplifyToTriangleCount(
    Mesh, 1000, SimplifyOptions, Debug
);

// 3. UV 重打包
FGeometryScriptLayoutUVsOptions UVOptions;
UVOptions.LayoutType = EGeometryScriptUVLayoutType::Repack;
UVOptions.TextureResolution = 1024;
UVOptions.Scale = 1.0f;
UGeometryScriptLibrary_MeshUVFunctions::LayoutMeshUVs(
    Mesh, 0, UVOptions, Debug
);

// 4. 写回
FGeometryScriptCopyMeshToAssetOptions WriteOptions;
FGeometryScriptMeshWriteLOD WriteLOD;
WriteLOD.bWriteHiResSource = false;
WriteLOD.LODIndex = 0;

EGeometryScriptOutcomePins WriteOutcome;
UGeometryScriptLibrary_StaticMeshFunctions::CopyMeshToStaticMesh(
    Mesh, MyStaticMesh, WriteOptions, WriteLOD, WriteOutcome, true, Debug
);
```

---

## 模块依赖

GeometryScriptingCore 的 Build.cs 依赖以下模块：

| 模块 | 用途 |
|---|---|
| `GeometryProcessing` | 底层几何处理算法（网格布尔、简化、修复等） |
| `MeshModelingToolset` | 网格建模工具集（倒角、挤出等操作的后端实现） |
| `GeometryCore` | 几何核心数据结构（FDynamicMesh3、空间索引等） |
| `DynamicMesh` | UDynamicMesh 运行时对象 |
| `ModelingComponents` | 建模组件（DynamicMeshComponent 等） |

使用此插件时，你的 Build.cs 需要依赖：

```cpp
PublicDependencyModuleNames.AddRange(new string[] {
    "GeometryScriptingCore",
    "DynamicMesh",
    "GeometryCore"
});
```

---

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `5925f0e4` | GeometryScript: Add validation for DynamicMesh overlay triangle storage coverage to BakeTexture. | 烘焙纹理时增加网格 Overlay 三角形覆盖的验证检查 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断到 float 的警告 |
| 2026-05-12 | `6a996b5e` | [Geometry] Fixed auto generated poly group sometimes does not generate subd compatible groups | 修复自动生成的 PolyGroup 有时不兼容细分的问题 |
| 2026-04-23 | `9f503464` | Optional rebalance geometry/attribute weight in simplifier | 简化器新增可选的几何/属性权重重新平衡功能 |
| 2026-04-15 | `8b93226f` | Add editor-only dynamic mesh processor class, so dataflow geometry script users can access the editor | 新增编辑器专用 DynamicMesh 处理器，支持数据流几何脚本用户访问编辑器功能 |

### 维护评价

**活跃维护** ✅

- 创建于 2024 年初（从实验阶段迁移到 Runtime），约 2 年历史
- 最近的提交（2026年5月）表明该插件仍在**持续活跃开发**
- 更新内容涵盖：bug 修复、功能增强（简化器权重平衡）、新功能（编辑器集成）
- 作为 Epic 官方的核心几何处理工具链，持续投入资源
- **强烈推荐使用**：这是 UE5 中进行程序化网格操作的官方标准方案，API 覆盖面极广，蓝图和 Python 均可使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GeometryScripting)
- 官方文档：无（.uplugin 中 DocsURL 为空）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GeometryScripting/Tests)（如有）