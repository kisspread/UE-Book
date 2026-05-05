# Geometry Script

> Geometry Script provides a library of functions for creating and editing Meshes in Blueprints and Python

| 属性 | 值 |
|---|---|
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、测试资源） |
| 模块 | `GeometryScriptingCore` (Runtime), `GeometryScriptingEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2021-09-12 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GeometryScripting) | |

## 用途

Geometry Script 是 UE5 中最全面的程序化网格操作库，提供了数百个蓝图/Python 可调用的函数，覆盖网格的创建、查询、编辑、修复、简化、布尔运算、烘焙等全流程。

**核心价值**：让非 C++ 开发者（蓝图/Python 用户）也能进行复杂的几何处理操作。传统上这些操作需要编写 C++ 代码调用 GeometryProcessing 模块，而 Geometry Script 将这些能力封装为蓝图节点，极大降低了程序化建模的门槛。

**解决的问题**：
- 在蓝图/Python 中无法直接操作网格几何数据
- 需要程序化生成、编辑或分析 3D 网格
- 需要将网格操作集成到游戏逻辑或自动化流程中
- 需要在运行时动态修改网格（如地形变形、程序化建筑）

## 使用场景

- 你在做一个程序化生成的游戏 → 用 Geometry Script 在运行时创建和编辑网格
- 你需要在蓝图中执行布尔运算（合并/相交/减去） → 用 MeshBooleanFunctions
- 你需要从场景中的组件提取网格数据进行分析 → 用 SceneUtilityFunctions
- 你需要对网格进行简化以优化性能 → 用 MeshSimplifyFunctions
- 你需要在网格表面采样点用于放置物体 → 用 MeshSamplingFunctions
- 你需要生成碰撞体 → 用 CollisionFunctions
- 你需要烘焙法线/AO 等纹理 → 用 MeshBakeFunctions
- 你需要在 Python 脚本中批量处理资产 → 用 Geometry Script 的 Python 绑定

## 蓝图用法

Geometry Script 的蓝图 API 按功能域组织为多个函数库类，所有函数均为静态方法，通过 `UBlueprintFunctionLibrary` 暴露。

### 核心节点

#### 网格查询

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetMeshInfoString` | 获取网格信息字符串（顶点数、三角形数等） | `UGeometryScriptLibrary_MeshQueryFunctions` |
| `GetMeshBoundingBox` | 计算网格的局部空间包围盒 | `UGeometryScriptLibrary_MeshQueryFunctions` |
| `GetMeshVolumeArea` | 计算网格的体积和表面积 | `UGeometryScriptLibrary_MeshQueryFunctions` |
| `GetIsClosedMesh` | 判断网格是否封闭（无边界边） | `UGeometryScriptLibrary_MeshQueryFunctions` |
| `GetNumConnectedComponents` | 获取网格中独立连通分量的数量 | `UGeometryScriptLibrary_MeshQueryFunctions` |
| `GetIsDenseMesh` | 判断网格是否密集（无 ID 间隙） | `UGeometryScriptLibrary_MeshQueryFunctions` |

#### 网格变换

| 节点 | 说明 | 所在类 |
|---|---|---|
| `TransformMesh` | 对整个网格应用变换 | `UGeometryScriptLibrary_MeshTransformFunctions` |
| `TranslateMesh` | 平移网格 | `UGeometryScriptLibrary_MeshTransformFunctions` |
| `RotateMesh` | 旋转网格 | `UGeometryScriptLibrary_MeshTransformFunctions` |
| `ScaleMesh` | 缩放网格 | `UGeometryScriptLibrary_MeshTransformFunctions` |
| `TransformMeshSelection` | 对选区内的顶点应用变换 | `UGeometryScriptLibrary_MeshTransformFunctions` |

#### 布尔运算

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ApplyMeshBoolean` | 执行网格布尔运算（并集/交集/减去） | `UGeometryScriptLibrary_MeshBooleanFunctions` |
| `ApplyMeshSelfUnion` | 网格自并集运算（消除自相交） | `UGeometryScriptLibrary_MeshBooleanFunctions` |
| `ApplyMeshPlaneCut` | 用平面切割网格 | `UGeometryScriptLibrary_MeshBooleanFunctions` |
| `ApplyMeshMirror` | 镜像网格 | `UGeometryScriptLibrary_MeshBooleanFunctions` |

#### 网格简化

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ApplySimplifyToTriangleCount` | 简化到目标三角形数量 | `UGeometryScriptLibrary_MeshSimplifyFunctions` |
| `ApplySimplifyToTolerance` | 简化到给定误差容差 | `UGeometryScriptLibrary_MeshSimplifyFunctions` |
| `ApplySimplifyToVertexCount` | 简化到目标顶点数量 | `UGeometryScriptLibrary_MeshSimplifyFunctions` |
| `ApplySimplifyToEdgeLength` | 简化到目标边长度 | `UGeometryScriptLibrary_MeshSimplifyFunctions` |
| `ApplyPlanarSimplify` | 平面简化（合并共面三角形） | `UGeometryScriptLibrary_MeshSimplifyFunctions` |

#### 网格修复

| 节点 | 说明 | 所在类 |
|---|---|---|
| `WeldMeshEdges` | 焊接重合边 | `UGeometryScriptLibrary_MeshRepairFunctions` |
| `FillAllMeshHoles` | 填充所有网格孔洞 | `UGeometryScriptLibrary_MeshRepairFunctions` |
| `ResolveMeshTJunctions` | 修复 T 型交叉 | `UGeometryScriptLibrary_MeshRepairFunctions` |
| `RemoveSmallComponents` | 移除过小的连通分量 | `UGeometryScriptLibrary_MeshRepairFunctions` |
| `CompactMesh` | 紧缩网格（消除 ID 间隙） | `UGeometryScriptLibrary_MeshRepairFunctions` |

#### 法线与切线

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ComputeNormalsForMesh` | 重新计算法线 | `UGeometryScriptLibrary_MeshNormalsFunctions` |
| `FlipNormals` | 翻转法线方向 | `UGeometryScriptLibrary_MeshNormalsFunctions` |
| `ComputeTangentsForMesh` | 计算切线 | `UGeometryScriptLibrary_MeshNormalsFunctions` |
| `SplitMeshNormals` | 按角度/组分割法线 | `UGeometryScriptLibrary_MeshNormalsFunctions` |

#### 建模操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ApplyMeshExtrude` | 挤出网格面 | `UGeometryScriptLibrary_MeshModelingFunctions` |
| `ApplyMeshOffset` | 偏移网格表面 | `UGeometryScriptLibrary_MeshModelingFunctions` |
| `ApplyMeshBevel` | 倒角 | `UGeometryScriptLibrary_MeshModelingFunctions` |
| `ApplyMeshInsetOutset` | 内缩/外扩 | `UGeometryScriptLibrary_MeshModelingFunctions` |
| `ApplyMeshLinearExtrude` | 线性挤出 | `UGeometryScriptLibrary_MeshModelingFunctions` |

#### 变形

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ApplyBendWarpToMesh` | 弯曲变形 | `UGeometryScriptLibrary_MeshDeformFunctions` |
| `ApplyTwistWarpToMesh` | 扭曲变形 | `UGeometryScriptLibrary_MeshDeformFunctions` |
| `ApplyFlareWarpToMesh` | 喇叭形变形 | `UGeometryScriptLibrary_MeshDeformFunctions` |
| `ApplyPerlinNoiseToMesh` | Perlin 噪声变形 | `UGeometryScriptLibrary_MeshDeformFunctions` |
| `ApplyIterativeSmoothingToMesh` | 迭代平滑 | `UGeometryScriptLibrary_MeshDeformFunctions` |
| `ApplyMathWarpToMesh` | 数学函数变形 | `UGeometryScriptLibrary_MeshDeformFunctions` |

#### 空间查询

| 节点 | 说明 | 所在类 |
|---|---|---|
| `BuildBVHForMesh` | 构建 BVH 加速结构 | `UGeometryScriptLibrary_MeshSpatial` |
| `RaycastBVH` | BVH 射线检测 | `UGeometryScriptLibrary_MeshSpatial` |
| `IsPointInsideMesh` | 判断点是否在网格内部 | `UGeometryScriptLibrary_MeshSpatial` |
| `FindNearestPointOnMesh` | 查找网格上最近点 | `UGeometryScriptLibrary_MeshSpatial` |

#### 采样

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SamplePointsOnMesh` | 在网格表面均匀采样点 | `UGeometryScriptLibrary_MeshSamplingFunctions` |
| `SampleNonUniformPointsOnMesh` | 非均匀采样（可变半径） | `UGeometryScriptLibrary_MeshSamplingFunctions` |
| `ComputeVertexWeightedPointSampling` | 基于顶点权重的采样 | `UGeometryScriptLibrary_MeshSamplingFunctions` |

#### 资产操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CopyMeshFromStaticMesh` | 从 StaticMesh 复制网格 | `UGeometryScriptLibrary_MeshAssetFunctions` |
| `CopyMeshToStaticMesh` | 将网格写回 StaticMesh | `UGeometryScriptLibrary_MeshAssetFunctions` |
| `CopyMeshFromComponent` | 从场景组件复制网格 | `UGeometryScriptLibrary_SceneUtilityFunctions` |

#### 烘焙

| 节点 | 说明 | 所在类 |
|---|---|---|
| `BakeTexture` | 烘焙纹理（法线/AO/位置等） | `UGeometryScriptLibrary_MeshBakeFunctions` |
| `BakeVertexColors` | 烘焙顶点颜色 | `UGeometryScriptLibrary_MeshBakeFunctions` |

#### 碰撞

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GenerateCollisionFromMesh` | 从网格生成碰撞体 | `UGeometryScriptLibrary_CollisionFunctions` |
| `SetStaticMeshCollisionFromMesh` | 设置 StaticMesh 的碰撞 | `UGeometryScriptLibrary_CollisionFunctions` |

### 使用示例（蓝图描述）

**示例 1：从 StaticMesh 读取 → 简化 → 写回**

1. 使用 `CopyMeshFromStaticMesh` 节点，输入 StaticMesh 引用，输出 UDynamicMesh
2. 连接到 `ApplySimplifyToTriangleCount`，设置目标三角形数为 500
3. 连接到 `CopyMeshToStaticMesh`，将结果写回（可选新资产路径）

**示例 2：布尔运算**

1. 使用两个 `CopyMeshFromStaticMesh` 分别获取两个网格
2. 使用 `TransformMesh` 调整其中一个网格的位置
3. 将两个网格输入 `ApplyMeshBoolean`，设置 Operation 为 `Subtract`
4. 将结果写回 StaticMesh 或 DynamicMeshComponent

**示例 3：程序化网格采样放置**

1. 使用 `CopyMeshFromComponent` 从场景中的 StaticMeshComponent 获取网格
2. 使用 `BuildBVHForMesh` 构建加速结构
3. 使用 `SamplePointsOnMesh` 在表面采样点
4. 在每个采样点位置 Spawn Actor

## C++ 用法

### 头文件引入

```cpp
#include "GeometryScriptingCoreModule.h"
#include "GeometryScript/GeometryScriptTypes.h"
#include "GeometryScript/MeshQueryFunctions.h"
#include "GeometryScript/MeshTransformFunctions.h"
#include "GeometryScript/MeshBooleanFunctions.h"
#include "GeometryScript/MeshAssetFunctions.h"
#include "GeometryScript/MeshSpatialFunctions.h"
#include "GeometryScript/MeshSamplingFunctions.h"
```

### 基本用法

```cpp
// 从 StaticMesh 复制网格到 DynamicMesh 进行操作
// 来源: GeometryScript/MeshAssetFunctions.h

UDynamicMesh* DynamicMesh = NewObject<UDynamicMesh>();

FGeometryScriptCopyMeshFromAssetOptions CopyOptions;
CopyOptions.bApplyBuildSettings = true;
CopyOptions.bRequestTangents = true;

EGeometryScriptOutcomePins Outcome;
UGeometryScriptLibrary_MeshAssetFunctions::CopyMeshFromStaticMesh(
    SourceStaticMesh,
    DynamicMesh,
    CopyOptions,
    FGeometryScriptMeshReadLOD(),
    Outcome
);

if (Outcome == EGeometryScriptOutcomePins::Success)
{
    // 网格复制成功，可以进行后续操作
}
```

### 进阶用法

```cpp
// 完整流程：读取网格 → 构建BVH → 射线检测 → 简化 → 写回
// 来源: GeometryScript/MeshSpatialFunctions.h, MeshSimplifyFunctions.h, MeshAssetFunctions.h

// 1. 读取网格
UDynamicMesh* Mesh = NewObject<UDynamicMesh>();
FGeometryScriptCopyMeshFromAssetOptions CopyOpts;
EGeometryScriptOutcomePins CopyResult;
UGeometryScriptLibrary_MeshAssetFunctions::CopyMeshFromStaticMesh(
    StaticMesh, Mesh, CopyOpts, FGeometryScriptMeshReadLOD(), CopyResult);

// 2. 构建 BVH 并执行射线检测
FGeometryScriptDynamicMeshBVH BVH;
UGeometryScriptLibrary_MeshSpatial::BuildBVHForMesh(Mesh, BVH);

FGeometryScriptRayHitResult HitResult;
UGeometryScriptLibrary_MeshSpatial::RaycastBVH(
    Mesh, BVH,
    FRay(FVector(0, 0, 100), FVector(0, 0, -1)),
    HitResult);

// 3. 简化网格
FGeometryScriptSimplifyMeshOptions SimplifyOpts;
SimplifyOpts.Method = EGeometryScriptRemoveMeshSimplificationType::AttributeAware;
UGeometryScriptLibrary_MeshSimplifyFunctions::ApplySimplifyToTriangleCount(
    Mesh, SimplifyOpts, 1000);

// 4. 写回 StaticMesh
FGeometryScriptCopyMeshToAssetOptions WriteOpts;
TArray<UMaterialInterface*> MaterialList;
EGeometryScriptOutcomePins WriteResult;
UGeometryScriptLibrary_MeshAssetFunctions::CopyMeshToStaticMesh(
    Mesh, TargetStaticMesh, WriteOpts, MaterialList, WriteResult);
```

## Demo 示例

### .h 文件

```cpp
// GeometryScriptDemoComponent.h
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "GeometryScript/GeometryScriptTypes.h"
#include "GeometryScriptDemoComponent.generated.h"

class UDynamicMesh;
class UStaticMesh;
class UDynamicMeshComponent;

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class YOURPROJECT_API UGeometryScriptDemoComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Demo")
    UStaticMesh* SourceMesh;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Demo")
    int32 TargetTriangleCount = 500;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Demo")
    float NoiseMagnitude = 5.0f;

    UFUNCTION(BlueprintCallable, Category = "Demo")
    void ProcessMesh();

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY()
    UDynamicMesh* WorkingMesh;

    UPROPERTY()
    UDynamicMeshComponent* PreviewComponent;
};
```

### .cpp 文件

```cpp
// GeometryScriptDemoComponent.cpp
#include "GeometryScriptDemoComponent.h"

#include "DynamicMeshActor.h"
#include "Components/DynamicMeshComponent.h"
#include "GeometryScript/GeometryScriptTypes.h"
#include "GeometryScript/MeshAssetFunctions.h"
#include "GeometryScript/MeshSimplifyFunctions.h"
#include "GeometryScript/MeshDeformFunctions.h"
#include "GeometryScript/MeshNormalsFunctions.h"
#include "GeometryScript/MeshRepairFunctions.h"
#include "GeometryScript/MeshQueryFunctions.h"

void UGeometryScriptDemoComponent::BeginPlay()
{
    Super::BeginPlay();

    WorkingMesh = NewObject<UDynamicMesh>(this);

    // 创建预览组件
    PreviewComponent = NewObject<UDynamicMeshComponent>(GetOwner());
    PreviewComponent->SetDynamicMesh(WorkingMesh);
    PreviewComponent->RegisterComponent();
    PreviewComponent->AttachToComponent(
        GetOwner()->GetRootComponent(),
        FAttachmentTransformRules::KeepRelativeTransform);
}

void UGeometryScriptDemoComponent::ProcessMesh()
{
    if (!SourceMesh || !WorkingMesh) return;

    // 1. 从 StaticMesh 复制网格
    FGeometryScriptCopyMeshFromAssetOptions CopyOpts;
    CopyOpts.bApplyBuildSettings = true;
    CopyOpts.bRequestTangents = true;
    EGeometryScriptOutcomePins CopyOutcome;
    UGeometryScriptLibrary_MeshAssetFunctions::CopyMeshFromStaticMesh(
        SourceMesh, WorkingMesh, CopyOpts,
        FGeometryScriptMeshReadLOD(), CopyOutcome);

    if (CopyOutcome != EGeometryScriptOutcomePins::Success)
    {
        UE_LOG(LogTemp, Warning, TEXT("Failed to copy mesh from StaticMesh"));
        return;
    }

    // 2. 简化网格
    FGeometryScriptSimplifyMeshOptions SimplifyOpts;
    SimplifyOpts.Method = EGeometryScriptRemoveMeshSimplificationType::AttributeAware;
    UGeometryScriptLibrary_MeshSimplifyFunctions::ApplySimplifyToTriangleCount(
        WorkingMesh, SimplifyOpts, TargetTriangleCount);

    // 3. 应用 Perlin 噪声变形
    FGeometryScriptPerlinNoiseLayerOptions NoiseOpts;
    NoiseOpts.Magnitude = NoiseMagnitude;
    NoiseOpts.Frequency = 0.1f;
    UGeometryScriptLibrary_MeshDeformFunctions::ApplyPerlinNoiseToMesh(
        WorkingMesh, NoiseOpts, 1);

    // 4. 重新计算法线
    FGeometryScriptCalculateNormalsOptions NormOpts;
    NormOpts.bAngleWeighted = true;
    NormOpts.bAreaWeighted = true;
    UGeometryScriptLibrary_MeshNormalsFunctions::ComputeNormalsForMesh(
        WorkingMesh, NormOpts);

    // 5. 修复可能的网格问题
    UGeometryScriptLibrary_MeshRepairFunctions::CompactMesh(WorkingMesh);

    // 6. 输出信息
    FString Info = UGeometryScriptLibrary_MeshQueryFunctions::GetMeshInfoString(WorkingMesh);
    UE_LOG(LogTemp, Log, TEXT("Processed mesh: %s"), *Info);
}
```

### Build.cs 依赖

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Engine",
    "GeometryScriptingCore",
    "GeometryFramework"  // UDynamicMesh, UDynamicMeshComponent
});
```

## 模块依赖

从 Build.cs 和 .uplugin 的 Plugins 依赖中提取：

| 模块 | 用途 |
|---|---|
| `GeometryFramework` | UDynamicMesh、UDynamicMeshComponent 等核心动态网格类型 |
| `GeometryProcessing` | 底层几何处理算法（布尔运算、简化、重网格化等） |
| `MeshModelingToolset` | 网格建模工具集（挤出、倒角、偏移等操作） |
| `PlanarCut` | 平面切割算法 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 近期 | `9046d13` | move dynamic mesh mikkt support out of the calculate tangents op so it can be used by geometry script + fix handling of unset elements (normals, uvs) in the mesh overlay | 将 MikkT 切线计算从操作中解耦，使 Geometry Script 可直接使用；修复网格覆盖层中未设置元素的处理 |
| 近期 | `35e7aa5` | fixes for new geometry script oriented box methods -- apply unscaled transform for box axes + fix displayname on OBB->ABB convert | 修复新增的有向包围盒方法的变换和显示名称问题 |
| 近期 | `9c4ba7b` | Add oriented box shape functions to geometry script | 新增有向包围盒（OBB）形状函数 |

### 维护评价

**活跃维护** ✅

- **创建时间**：2021 年 9 月，约 4 年历史，属于较新的插件
- **更新频率**：持续有功能性更新，最近的提交包括新增 OBB 功能和切线计算改进
- **维护状态**：Epic Games 官方维护，作为 UE5 核心几何处理能力的一部分
- **重要性**：这是 UE5 程序化建模的基石插件，被 Nanite、PCG 等系统依赖
- **已知限制**：
  - `EnabledByDefault=false`，需要手动在项目设置中启用
  - 依赖 GeometryProcessing、MeshModelingToolset、PlanarCut 三个插件
  - 运行时使用需要注意性能，某些操作（如布尔运算、简化）计算量较大
- **推荐程度**：强烈推荐。任何需要在蓝图/Python 中操作网格的项目都应该启用此插件

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GeometryScripting)
- [官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/geometry-scripting-in-unreal-engine)