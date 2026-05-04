# Geometry Scripting Core

> Geometry Script provides a library of functions for creating and editing Meshes in Blueprints and Python

| 属性 | 值 |
|---|---|
| 分类 | Geometry |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `GeometryScriptingCore` (Runtime), `GeometryScriptingEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2021-09-12 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GeometryScripting) | |

## 用途

Geometry Scripting Core 是 UE5 的程序化网格操作模块，提供完整的蓝图函数库用于创建、查询、编辑和处理 DynamicMesh。它将 GeometryCore/DynamicMesh 底层算法暴露给蓝图和 Python，使非程序员也能进行复杂的程序化几何操作。

核心价值：
- **运行时可用**：打包后仍可使用，适合游戏内程序化生成
- **蓝图友好**：所有操作都是 `BlueprintCallable`/`BlueprintPure`，链式调用
- **基于 UDynamicMesh**：轻量级运行时网格，无需 StaticMesh 资产
- **功能全面**：从基础查询到布尔运算、UV 展开、网格修复等高级操作

## 使用场景

- 你在做一个程序化地形生成器 → 用 MeshPrimitiveFunctions 生成基础形状 + MeshDeformFunctions 变形
- 你需要在运行时合并多个网格 → 用 MeshBasicEditFunctions 的 AppendMesh / CombineMeshes
- 你需要对网格做布尔运算（并集/交集/差集） → 用 MeshBooleanFunctions
- 你需要自动修复导入的破面模型 → 用 MeshRepairFunctions
- 你需要在蓝图中查询网格信息（包围盒、体积、连通性） → 用 MeshQueryFunctions
- 你需要动态生成碰撞体 → 用 CollisionFunctions
- 你需要程序化 UV 展开和打包 → 用 MeshUVFunctions
- 你需要网格简化 → 用 MeshSimplifyFunctions

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AppendMesh` | 将源网格追加到目标网格 | `UGeometryScriptLibrary_MeshBasicEditFunctions` |
| `CombineMeshes` | 合并多个网格 | `UGeometryScriptLibrary_MeshBasicEditFunctions` |
| `ApplyMeshBoolean` | 布尔运算（并集/交集/差集） | `UGeometryScriptLibrary_MeshBooleanFunctions` |
| `ApplyMeshPlaneCut` | 平面切割网格 | `UGeometryScriptLibrary_MeshBooleanFunctions` |
| `ApplyMeshMirror` | 镜像网格 | `UGeometryScriptLibrary_MeshBooleanFunctions` |
| `GetMeshInfoString` | 获取网格信息字符串 | `UGeometryScriptLibrary_MeshQueryFunctions` |
| `GetMeshBoundingBox` | 获取网格包围盒 | `UGeometryScriptLibrary_MeshQueryFunctions` |
| `GetMeshVolumeArea` | 获取网格体积和面积 | `UGeometryScriptLibrary_MeshQueryFunctions` |
| `GetIsClosedMesh` | 检查网格是否封闭 | `UGeometryScriptLibrary_MeshQueryFunctions` |
| `GetNumConnectedComponents` | 获取连通分量数量 | `UGeometryScriptLibrary_MeshQueryFunctions` |
| `TransformMesh` | 变换网格顶点 | `UGeometryScriptLibrary_MeshTransformFunctions` |
| `TranslateMesh` | 平移网格 | `UGeometryScriptLibrary_MeshTransformFunctions` |
| `RotateMesh` | 旋转网格 | `UGeometryScriptLibrary_MeshTransformFunctions` |
| `ScaleMesh` | 缩放网格 | `UGeometryScriptLibrary_MeshTransformFunctions` |
| `FlipNormals` | 翻转法线 | `UGeometryScriptLibrary_MeshNormalsFunctions` |
| `RepairMeshNormals` | 修复法线 | `UGeometryScriptLibrary_MeshNormalsFunctions` |
| `ComputeTangents` | 计算切线 | `UGeometryScriptLibrary_MeshNormalsFunctions` |
| `SimplifyMesh` | 简化网格 | `UGeometryScriptLibrary_MeshSimplifyFunctions` |
| `WeldMeshEdges` | 焊接网格边 | `UGeometryScriptLibrary_MeshRepairFunctions` |
| `FillAllMeshHoles` | 填补网格孔洞 | `UGeometryScriptLibrary_MeshRepairFunctions` |
| `ResolveMeshTJunctions` | 解决 T 型交叉 | `UGeometryScriptLibrary_MeshRepairFunctions` |
| `CopyMeshToStaticMesh` | 复制到 StaticMesh 资产 | `UGeometryScriptLibrary_MeshAssetFunctions` |
| `CopyMeshFromStaticMesh` | 从 StaticMesh 复制 | `UGeometryScriptLibrary_MeshAssetFunctions` |
| `RecomputeMeshUVs` | 重新计算 UV | `UGeometryScriptLibrary_MeshUVFunctions` |
| `RepackMeshUVs` | 重新打包 UV | `UGeometryScriptLibrary_MeshUVFunctions` |
| `LayoutMeshUVs` | UV 布局（Transform/Stack/Repack/Normalize） | `UGeometryScriptLibrary_MeshUVFunctions` |
| `ApplyMeshVertexColors` | 设置顶点颜色 | `UGeometryScriptLibrary_MeshVertexColorFunctions` |

### 基本图元创建节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AppendBox` | 创建盒体 | `UGeometryScriptLibrary_MeshPrimitiveFunctions` |
| `AppendSphere` | 创建球体 | `UGeometryScriptLibrary_MeshPrimitiveFunctions` |
| `AppendCylinder` | 创建圆柱体 | `UGeometryScriptLibrary_MeshPrimitiveFunctions` |
| `AppendTorus` | 创建圆环体 | `UGeometryScriptLibrary_MeshPrimitiveFunctions` |
| `AppendDisc` | 创建圆盘 | `UGeometryScriptLibrary_MeshPrimitiveFunctions` |
| `AppendRectangle` | 创建矩形 | `UGeometryScriptLibrary_MeshPrimitiveFunctions` |
| `AppendLinearStaircase` | 创建线性楼梯 | `UGeometryScriptLibrary_MeshPrimitiveFunctions` |
| `AppendSpiralStaircase` | 创建螺旋楼梯 | `UGeometryScriptLibrary_MeshPrimitiveFunctions` |
| `AppendSweepAlongPath` | 沿路径扫掠 | `UGeometryScriptLibrary_MeshPrimitiveFunctions` |
| `AppendRevolvePath` | 旋转体生成 | `UGeometryScriptLibrary_MeshPrimitiveFunctions` |
| `AppendOrientedBox` | 创建定向盒体 | `UGeometryScriptLibrary_MeshPrimitiveFunctions` |

### 变形操作节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ApplyBendWarp` | 弯曲变形 | `UGeometryScriptLibrary_MeshDeformFunctions` |
| `ApplyTwistWarp` | 扭曲变形 | `UGeometryScriptLibrary_MeshDeformFunctions` |
| `ApplyFlareWarp` | 喇叭口变形 | `UGeometryScriptLibrary_MeshDeformFunctions` |
| `ApplyPerlinNoiseToMesh` | Perlin 噪声变形 | `UGeometryScriptLibrary_MeshDeformFunctions` |
| `ApplyMathWarpToMesh` | 数学函数变形 | `UGeometryScriptLibrary_MeshDeformFunctions` |
| `ApplyIterativeSmoothingToMesh` | 迭代平滑 | `UGeometryScriptLibrary_MeshDeformFunctions` |
| `ApplyMeshDisplacementFromMap` | 贴图位移 | `UGeometryScriptLibrary_MeshDeformFunctions` |

### 碰撞与空间节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GenerateCollisionFromMesh` | 从网格生成碰撞体 | `UGeometryScriptLibrary_CollisionFunctions` |
| `SetCollisionFromMesh` | 设置网格碰撞 | `UGeometryScriptLibrary_CollisionFunctions` |
| `SetStaticMeshCollisionFromMesh` | 设置 StaticMesh 碰撞 | `UGeometryScriptLibrary_CollisionFunctions` |
| `TestPointInsideMesh` | 点在网格内部测试 | `UGeometryScriptLibrary_ContainmentFunctions` |
| `IsPointInsideMesh` | 点是否在网格内 | `UGeometryScriptLibrary_ContainmentFunctions` |
| `FindClosestPointOnMesh` | 查找最近点 | `UGeometryScriptLibrary_MeshSpatialFunctions` |
| `IsTriangleIntersectingMesh` | 三角形交叉测试 | `UGeometryScriptLibrary_MeshComparisonFunctions` |

### 使用示例（蓝图描述）

**示例 1：程序化创建并变换网格**

1. 创建一个 `Make Dynamic Mesh` 节点获取空网格
2. 连接到 `Append Box`（设置 Box 参数为 FGeometryScriptPrimitiveOptions）
3. 连接到 `Transform Mesh`（传入 FTransform 进行缩放/旋转）
4. 连接到 `Set Dynamic Mesh Material` 设置材质
5. 输出到 Dynamic Mesh Actor

**示例 2：布尔运算工作流**

1. 创建两个网格（例如 AppendBox + AppendSphere）
2. 使用 `Apply Mesh Boolean`，传入两个网格和 EGeometryScriptBooleanOperation::Subtract
3. 设置 FGeometryScriptMeshBooleanOptions（bFillHoles=true, bSimplifyOutput=true）
4. 输出差集结果网格

**示例 3：网格修复流水线**

1. 从资产复制网格：`Copy Mesh From Static Mesh`
2. 修复法线：`Repair Mesh Normals`
3. 焊接边：`Weld Mesh Edges`
4. 填补孔洞：`Fill All Mesh Holes`
5. 简化：`Simplify Mesh`（使用 FGeometryScriptSimplifyMeshOptions）
6. 写回资产：`Copy Mesh To Static Mesh`

## C++ 用法

### 头文件引入

```cpp
#include "GeometryScript/GeometryScriptTypes.h"
#include "GeometryScript/MeshQueryFunctions.h"
#include "GeometryScript/MeshBasicEditFunctions.h"
#include "GeometryScript/MeshBooleanFunctions.h"
#include "GeometryScript/MeshPrimitiveFunctions.h"
#include "GeometryScript/MeshTransformFunctions.h"
#include "GeometryScript/MeshRepairFunctions.h"
```

### 基本用法

Geometry Scripting 的核心数据类型是 `UDynamicMesh`，所有操作都通过静态蓝图函数库进行：

```cpp
// 创建动态网格并查询信息
UDynamicMesh* Mesh = NewObject<UDynamicMesh>();
FString Info = UGeometryScriptLibrary_MeshQueryFunctions::GetMeshInfoString(Mesh);
FBox Bounds = UGeometryScriptLibrary_MeshQueryFunctions::GetMeshBoundingBox(Mesh);

// 追加基本图元
FGeometryScriptPrimitiveOptions Options;
Options.PolygroupMode = EGeometryScriptPrimitivePolygroupMode::PerFace;
Options.bFlipOrientation = false;
Options.UVMode = EGeometryScriptPrimitiveUVMode::Uniform;

UGeometryScriptLibrary_MeshPrimitiveFunctions::AppendBox(
    Mesh, Options, FTransform::Identity, 100.0f, 100.0f, 100.0f);
```

### 进阶用法

```cpp
// 布尔运算
UDynamicMesh* TargetMesh = NewObject<UDynamicMesh>();
UDynamicMesh* ToolMesh = NewObject<UDynamicMesh>();

// ... 填充网格数据 ...

FGeometryScriptMeshBooleanOptions BoolOptions;
BoolOptions.bFillHoles = true;
BoolOptions.bSimplifyOutput = true;
BoolOptions.SimplifyPlanarTolerance = 0.01f;
BoolOptions.OutputTransformSpace = EGeometryScriptBooleanOutputSpace::TargetTransformSpace;

UGeometryScriptLibrary_MeshBooleanFunctions::ApplyMeshBoolean(
    TargetMesh, FTransform::Identity,
    ToolMesh, FTransform(FVector(50, 0, 0)),
    EGeometryScriptBooleanOperation::Subtract,
    BoolOptions);

// 网格修复流水线
FGeometryScriptWeldEdgesOptions WeldOptions;
WeldOptions.Tolerance = 1e-06f;
WeldOptions.bOnlyUniquePairs = true;
UGeometryScriptLibrary_MeshRepairFunctions::WeldMeshEdges(TargetMesh, WeldOptions);

FGeometryScriptFillHolesOptions FillOptions;
FillOptions.FillMethod = EGeometryScriptFillHolesMethod::Automatic;
int32 NumFilled = 0;
UGeometryScriptLibrary_MeshRepairFunctions::FillAllMeshHoles(TargetMesh, FillOptions, NumFilled);

// 简化
FGeometryScriptSimplifyMeshOptions SimplifyOptions;
SimplifyOptions.Method = EGeometryScriptRemoveMeshSimplificationType::AttributeAware;
SimplifyOptions.bAllowSeamCollapse = true;
UGeometryScriptLibrary_MeshSimplifyFunctions::SimplifyMesh(
    TargetMesh, SimplifyOptions, EGeometryScriptMeshSelectionType::Triangles, 500);

// 变换操作
UGeometryScriptLibrary_MeshTransformFunctions::TransformMesh(
    TargetMesh, FTransform(FRotator(0, 45, 0), FVector(100, 0, 0)));

// UV 操作
FGeometryScriptLayoutUVsOptions UVOptions;
UVOptions.LayoutType = EGeometryScriptUVLayoutType::Repack;
UVOptions.TextureResolution = 1024;
UVOptions.Scale = 1.0f;
UGeometryScriptLibrary_MeshUVFunctions::LayoutMeshUVs(
    TargetMesh, UVOptions, 0 /* UVLayer */);
```

### Asset 交互

```cpp
// 从 StaticMesh 复制到 DynamicMesh
FGeometryScriptCopyMeshFromAssetOptions CopyOptions;
CopyOptions.bApplyBuildSettings = true;
CopyOptions.bRequestTangents = true;

UGeometryScriptLibrary_MeshAssetFunctions::CopyMeshFromStaticMesh(
    StaticMeshAsset, TargetMesh, CopyOptions, FGeometryScriptMeshReadLOD());

// 从 DynamicMesh 复制回 StaticMesh
FGeometryScriptCopyMeshToAssetOptions AssetOptions;
AssetOptions.bEnableNanite = true;
AssetOptions.NaniteSettings.bPreserveArea = true;

UGeometryScriptLibrary_MeshAssetFunctions::CopyMeshToStaticMesh(
    TargetMesh, StaticMeshAsset, AssetOptions, FGeometryScriptMeshWriteLOD());
```

## Demo 示例

```cpp
// MyProceduralMeshActor.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DynamicMeshActor.h"
#include "MyProceduralMeshActor.generated.h"

UCLASS()
class AMyProceduralMeshActor : public AActor
{
    GENERATED_BODY()
public:
    AMyProceduralMeshActor();

    UPROPERTY(VisibleAnywhere)
    UDynamicMeshComponent* MeshComponent;

    virtual void BeginPlay() override;

    UFUNCTION(BlueprintCallable)
    void GenerateBooleanMesh();
};
```

```cpp
// MyProceduralMeshActor.cpp
#include "MyProceduralMeshActor.h"
#include "GeometryScript/GeometryScriptTypes.h"
#include "GeometryScript/MeshPrimitiveFunctions.h"
#include "GeometryScript/MeshBooleanFunctions.h"
#include "GeometryScript/MeshTransformFunctions.h"
#include "GeometryScript/MeshRepairFunctions.h"

AMyProceduralMeshActor::AMyProceduralMeshActor()
{
    MeshComponent = CreateDefaultSubobject<UDynamicMeshComponent>(TEXT("Mesh"));
    RootComponent = MeshComponent;
}

void AMyProceduralMeshActor::BeginPlay()
{
    Super::BeginPlay();
    GenerateBooleanMesh();
}

void AMyProceduralMeshActor::GenerateBooleanMesh()
{
    UDynamicMesh* Mesh = MeshComponent->GetDynamicMesh();
    if (!Mesh) return;

    // 创建基础盒体
    FGeometryScriptPrimitiveOptions PrimOpts;
    PrimOpts.PolygroupMode = EGeometryScriptPrimitivePolygroupMode::PerFace;

    UGeometryScriptLibrary_MeshPrimitiveFunctions::AppendBox(
        Mesh, PrimOpts, FTransform::Identity,
        200.0f, 200.0f, 200.0f);

    // 创建球体作为布尔运算工具
    UDynamicMesh* SphereMesh = NewObject<UDynamicMesh>();
    UGeometryScriptLibrary_MeshPrimitiveFunctions::AppendSphere(
        SphereMesh, PrimOpts, FTransform(FVector(100, 0, 0)),
        100.0f, 100.0f, 32, 16);

    // 布尔差集
    FGeometryScriptMeshBooleanOptions BoolOpts;
    BoolOpts.bFillHoles = true;
    BoolOpts.bSimplifyOutput = true;

    UGeometryScriptLibrary_MeshBooleanFunctions::ApplyMeshBoolean(
        Mesh, FTransform::Identity,
        SphereMesh, FTransform(FVector(100, 0, 0)),
        EGeometryScriptBooleanOperation::Subtract,
        BoolOpts);

    // 简化结果
    FGeometryScriptSimplifyMeshOptions SimplifyOpts;
    SimplifyOpts.Method = EGeometryScriptRemoveMeshSimplificationType::AttributeAware;
    UGeometryScriptLibrary_MeshSimplifyFunctions::SimplifyMesh(Mesh, SimplifyOpts);

    // 通知组件更新
    MeshComponent->NotifyMeshModified();
}
```

**Build.cs 依赖**：

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "GeometryCore",
    "GeometryFramework",
    "DynamicMesh",
    "GeometryScriptingCore"
});
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `PhysicsCore` | 物理核心（碰撞体相关） |
| `RenderCore` | 渲染核心 |
| `GeometryCore` | 几何核心算法（FDynamicMesh3, AABB 树等） |
| `GeometryFramework` | 几何框架（UDynamicMesh, UDynamicMeshComponent） |
| `DynamicMesh` | 动态网格资产类型 |

**私有依赖（使用时不需要）**：
- CoreUObject, Engine, MeshDescription, MeshConversion, GeometryAlgorithms, ModelingOperators, PlanarCut, Chaos

## 模块内部结构

GeometryScriptingCore 包含 42 个公共头文件，按功能分为以下类别：

### 核心类型
- `GeometryScriptTypes.h` — 基础枚举/结构体（LOD 类型、坐标空间、调试对象等）
- `GeometryScriptSelectionTypes.h` — 网格选择类型（顶点/三角形/PolyGroup 选择）

### 网格查询与信息
- `MeshQueryFunctions.h` — 网格信息查询（包围盒、体积、连通性、顶点/三角形查询）
- `MeshSpatialFunctions.h` — 空间查询（最近点、射线投射）
- `MeshComparisonFunctions.h` — 网格比较（相交测试、距离计算）
- `MeshSelectionQueryFunctions.h` — 选择集查询

### 网格创建
- `MeshPrimitiveFunctions.h` — 基本图元创建（盒体、球体、圆柱、圆环、扫掠体等）
- `ShapeFunctions.h` — 形状辅助函数（Transform 创建、Box/OBB 操作）
- `MeshPoolFunctions.h` — 网格池管理

### 网格编辑
- `MeshBasicEditFunctions.h` — 基础编辑（追加、合并、删除、设置顶点位置）
- `MeshBooleanFunctions.h` — 布尔运算（并集、交集、差集、平面切割、镜像）
- `MeshModelingFunctions.h` — 建模操作（偏移、挤出、倒角、插入边循环）
- `MeshDecompositionFunctions.h` — 网格分解

### 变形与变换
- `MeshTransformFunctions.h` — 变换操作（平移、旋转、缩放）
- `MeshDeformFunctions.h` — 变形操作（弯曲、扭曲、喇叭口、Perlin 噪声）

### 网格修复与优化
- `MeshRepairFunctions.h` — 网格修复（焊接边、填补孔洞、解决 T 型交叉）
- `MeshSimplifyFunctions.h` — 网格简化（QEM、体积保持、属性感知）
- `MeshRemeshFunctions.h` — 重新网格化（均匀重网格化）
- `MeshSubdivideFunctions.h` — 细分（PN Tessellate、选择性细分）

### 属性操作
- `MeshNormalsFunctions.h` — 法线操作（翻转、修复、计算切线）
- `MeshUVFunctions.h` — UV 操作（展开、打包、布局、变换）
- `MeshVertexColorFunctions.h` — 顶点颜色操作
- `MeshMaterialFunctions.h` — 材质操作
- `MeshBoneWeightFunctions.h` — 骨骼权重操作
- `MeshPolygroupFunctions.h` — PolyGroup 操作

### 空间与采样
- `MeshSamplingFunctions.h` — 网格采样
- `MeshGeodesicFunctions.h` — 测地线操作
- `MeshSpatialFunctions.h` — 空间查询

### 资产与场景
- `MeshAssetFunctions.h` — 资产交互（StaticMesh ↔ DynamicMesh）
- `MeshBakeFunctions.h` — 烘焙操作（法线贴图、AO 等）
- `VolumeTextureBakeFunctions.h` — 体积纹理烘焙
- `SceneUtilityFunctions.h` — 场景工具函数
- `TextureMapFunctions.h` — 纹理映射函数
- `CollisionFunctions.h` — 碰撞体生成
- `ContainmentFunctions.h` — 包含测试（点在网格内）
- `MeshSculptLayersFunctions.h` — 雕刻层

### 工具函数
- `ListUtilityFunctions.h` — 列表工具函数
- `VectorMathFunctions.h` — 向量数学
- `PolygonFunctions.h` — 多边形操作
- `PolyPathFunctions.h` — 多路径操作
- `PointSetFunctions.h` — 点集操作
- `MeshVoxelFunctions.h` — 体素操作

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-09-10 | `9046d13` | 移动 DynamicMesh MIKT 支持，修复网格覆盖层中未设置元素（法线、UV）的处理 |
| 2025-09-03 | `35e7aa5` | 修复新定向盒方法 — 对盒轴应用未缩放变换 + 修复 OBB→ABB 转换的显示名 |
| 2025-09-03 | `9c4ba7b` | 添加定向盒（Oriented Box）形状函数到 Geometry Script |

### 维护评价

- **活跃维护**：最近 6 个月内持续有功能性更新
- **创建时间**：2021 年 9 月（从 Experimental 迁移到 Runtime）
- **更新频率**：频繁，持续添加新功能（Oriented Box、MIKT 支持等）
- **稳定性**：已从实验性毕业为正式 Runtime 模块
- **推荐程度**：✅ 强烈推荐 — 这是 UE5 程序化几何操作的标准方案，蓝图和 C++ 均可使用，运行时可用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GeometryScripting)
- [官方文档]()（.uplugin 中未提供 DocsURL）
- [测试用例]()（本插件无独立测试文件）
