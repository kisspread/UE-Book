# DataflowVolumetric

> Adds volumetric support to Dataflow

| 属性 | 值 |
|---|---|
| 分类 | Dataflow |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有 |
| 模块 | `DataflowVolumeCore` (Editor), `DataflowVolumeNodes` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-01-24 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/DataflowVolumetricPlugin) | |

## 用途

本插件将 [OpenVDB](https://www.openvdb.org/) 体素化体积数据处理能力集成到 UE5 的 **Dataflow** 节点图框架中。它提供了一套完整的体积数据类型（浮点、整数、布尔、向量）以及基于这些类型的 SDF（有符号距离场）操作，使开发者能够在 Dataflow 节点图中执行以下核心任务：

- **网格↔体积转换**：将 `FMeshDescription` 转换为 SDF 体素网格，或将 SDF 转换回网格
- **SDF 基元生成**：程序化生成球体、立方体、柏拉图多面体的 SDF
- **SDF 布尔运算**：并集、交集、差集等 CSG 操作
- **球体填充**：将 SDF 体积转换为球体集合（用于破碎、散布等）
- **向量场分析**：计算散度、旋度、幅值、归一化等
- **雾体积转换**：SDF 与 Fog Volume 之间的互转

本质上，这是一个面向**程序化内容生成（PCG）和物理模拟**的体素化工具集，让 Dataflow 图能够操作和分析三维体积数据。

## 使用场景

- 你需要在 Dataflow 图中对几何体进行**布尔运算**（CSG Union/Intersect/Difference）→ 使用 SDF Combine 节点
- 你需要将网格转换为 **SDF** 并进行球体填充（sphere packing）用于破碎或散布 → 使用 `VolumeToSpheres` / `VolumeToSpheresImproved`
- 你需要生成程序化 **SDF 基元**（球、立方体、正多面体）→ 使用 `CreateSphereSDF` / `CreateCubeSDF` / `CreatePlatonicSolidSDF`
- 你需要在 Dataflow 中分析**向量场**（如速度场、梯度场）→ 使用 `ComputeDivergence` / `ComputeCurl` / `ComputeMagnitude`
- 你需要将 SDF 转换为 **Fog Volume** 用于体积雾效果 → 使用 `CovertSDFToFogVolume`

## 蓝图用法

本插件的核心类型均为 `USTRUCT`，主要通过 **Dataflow 节点**在蓝图/节点图中使用。`DataflowVolumeNodes` 模块提供了具体的节点实现（源码未在本次分析范围内）。

### 核心数据类型

| 类型 | TypeName | 说明 |
|---|---|---|
| `FDataflowVolume` | — | 基类，提供通用体积操作（活跃体素查询、包围盒、纹理创建） |
| `FDataflowFloatVolume` | `FloatVolume` | 浮点体积，用于 SDF 和 Fog Volume |
| `FDataflowIntVolume` | `IntVolume` | 整数体积，用于面索引等离散数据 |
| `FDataflowBoolVolume` | `BoolVolume` | 布尔体积，用作掩码 |
| `FDataflowFloatVectorVolume` | `FloatVectorVolume` | 向量浮点体积，用于梯度/速度场 |

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateSphereSDF` | 创建球体 SDF | `FDataflowFloatVolume` |
| `CreateCubeSDF` | 创建立方体 SDF | `FDataflowFloatVolume` |
| `CreatePlatonicSolidSDF` | 创建柏拉图多面体 SDF（四面体/八面体/十二面体/二十面体） | `FDataflowFloatVolume` |
| `CreateVolumeFromMeshDescription` | 从网格创建 SDF/USDF/Fog Volume | `FDataflowFloatVolume` |
| `VolumeToSpheres` | SDF 球体填充（原始算法） | `FDataflowFloatVolume` |
| `VolumeToSpheresImproved` | SDF 球体填充（改进算法，支持散布类型和随机种子） | `FDataflowFloatVolume` |
| `CovertSDFToFogVolume` | SDF 转 Fog Volume | `FDataflowFloatVolume` |
| `CovertFogVolumeToSDF` | Fog Volume 转 SDF | `FDataflowFloatVolume` |
| `ComputeDivergence` | 计算向量场散度（返回标量场） | `FDataflowFloatVectorVolume` |
| `ComputeMagnitude` | 计算向量场幅值（返回标量场） | `FDataflowFloatVectorVolume` |
| `ComputeCurl` | 计算向量场旋度 | `FDataflowFloatVectorVolume` |
| `ComputeNormalize` | 归一化向量场 | `FDataflowFloatVectorVolume` |
| `VolumeSample` | 在指定点采样体积值 | `FDataflowIntVolume`, `FDataflowFloatVectorVolume` |
| `GetActiveVoxels` | 获取活跃体素列表 | `FDataflowVolume` |
| `CreateVolumeTexture` | 将体积数据写入 `UVolumeTexture` | `FDataflowVolume` |

### 枚举选项

| 枚举 | 用途 |
|---|---|
| `EDataflowVolumeOutputType` | 输出类型：SDF / USDF / FogVolume |
| `EDataflowVolumeSDFCombineOperation` | SDF 组合操作：18 种模式（含 CSG 布尔、算术、活动区域操作） |
| `EDataflowVolumeSDFCombineResample` | 重采样策略：关闭 / B匹配A / A匹配B / 高分辨率匹配低 / 低匹配高 |
| `EDataflowVolumeSDFCombineInterpolation` | 插值方式：最近邻 / 线性 / 二次 |
| `EDataflowVolumePlatonicSolidType` | 柏拉图多面体类型：四面体 / 立方体 / 八面体 / 十二面体 / 二十面体 |
| `EDataflowVolumeScatterType` | 散布类型（用于球体填充改进算法） |

### 使用示例（蓝图描述）

在 Dataflow 节点图中，典型的工作流如下：

1. **网格转 SDF**：将 `FMeshDescription` 输入到 `CreateVolumeFromMeshDescription` 节点，设置体素大小和输出类型为 SDF，得到 `FDataflowFloatVolume`
2. **SDF 布尔运算**：将两个 SDF 体积输入到 SDF Combine 节点，选择 `SDFUnion` / `SDFIntersect` / `SDFDifference` 操作
3. **球体填充**：将 SDF 体积输入到 `VolumeToSpheresImproved` 节点，设置球体数量范围、半径范围、散布类型，输出球体中心和半径数组
4. **向量场分析**：将 `FDataflowFloatVectorVolume` 输入到 `ComputeDivergence` 节点，可选传入 `FDataflowBoolVolume` 作为掩码

## C++ 用法

### 头文件引入

```cpp
#include "Dataflow/DataflowVolume.h"
#include "Dataflow/DataflowFloatVolume.h"
#include "Dataflow/DataflowIntVolume.h"
#include "Dataflow/DataflowBoolVolume.h"
#include "Dataflow/DataflowFloatVectorVolume.h"
```

### 基本用法

创建 SDF 基元并查询信息：

```cpp
// 创建一个半径为 50、体素大小为 1.0 的球体 SDF
FDataflowFloatVolume SphereSDF = FDataflowFloatVolume::CreateSphereSDF(
    1.0f,           // InVoxelSize
    50.0f,          // InRadius
    FVector::ZeroVector  // InCenter
);

// 查询体积信息
FString Info = SphereSDF.VolumeInfo();
UE_LOG(LogTemp, Log, TEXT("Volume Info: %s"), *Info);

// 获取体素大小
FVector VoxelSize = SphereSDF.GetVoxelSize();

// 获取活跃体素数量（isovalue=0 表示表面）
int32 ActiveCount = SphereSDF.GetNumActiveVoxels(0.0f);

// 获取包围盒
FBox BoundingBox = SphereSDF.GetVolumeBoundingBox();

// 获取活跃体素列表
TArray<FBox> ActiveVoxels;
SphereSDF.GetActiveVoxels(0.0f, ActiveVoxels);
```

### 进阶用法

从网格创建 SDF 并进行球体填充：

```cpp
// 假设已有 FMeshDescription 和参考网格
FDataflowFloatVolume MeshSDF = FDataflowFloatVolume::CreateVolumeFromMeshDescription(
    MeshDescription,        // 输入网格
    FTransform::Identity,   // 变换
    1.0f,                   // 体素大小
    ReferenceVolume,        // 参考网格（用于对齐体素）
    EDataflowVolumeOutputType::SDF,  // 输出类型
    TEXT("MeshSDF"),        // 网格名称
    true,                   // 使用世界空间单位
    3.0f,                   // 外部带宽
    3.0f,                   // 内部带宽
    3,                      // 外部带宽体素数
    3,                      // 内部带宽体素数
    true,                   // 填充内部
    false,                  // 保留孔洞
    0.0f,                   // 等值面值
    FaceIndexVolume         // 输出：面索引体积
);

// 球体填充（改进算法）
TArray<FVector> SphereCenters;
TArray<float> SphereRadii;
MeshSDF.VolumeToSpheresImproved(
    10,     // 最小球体数
    100,    // 最大球体数
    false,  // 是否允许重叠
    1.0f,   // 最小半径
    20.0f,  // 最大半径
    0.0f,   // 等值面值
    1,      // 实例数
    42,     // 随机种子
    EDataflowVolumeScatterType::Uniform,  // 散布类型
    1.0f,   // 扩散
    1.0f,   // 每体素最小点数
    5.0f,   // 每体素最大点数
    SphereCenters,
    SphereRadii
);
```

### 类型转换

使用基类的 `Cast` 模板进行安全类型转换：

```cpp
// 从 Dataflow 上下文获取通用体积
const FDataflowVolume& Volume = GetValue(Context, &MyVolumePin);

// 安全向下转型
if (const FDataflowFloatVolume* FloatVolume = Volume.Cast<FDataflowFloatVolume>())
{
    // 处理浮点体积
    FVector VoxelSize = FloatVolume->GetVoxelSize();
}
else if (const FDataflowIntVolume* IntVolume = Volume.Cast<FDataflowIntVolume>())
{
    // 处理整数体积
    TArray<FVector> Points = { FVector(0, 0, 0), FVector(10, 10, 10) };
    TArray<int32> Values;
    IntVolume->VolumeSample(Points, Values);
}
else if (const FDataflowFloatVectorVolume* VecVolume = Volume.Cast<FDataflowFloatVectorVolume>())
{
    // 处理向量体积 - 计算散度
    FDataflowFloatVolume Divergence = VecVolume->ComputeDivergence(
        EDataflowVolumeAnalysisOutputName::Default,
        TEXT("Divergence")
    );
}
```

### AnyType 注册

在模块启动时注册体积类型系统：

```cpp
#include "Dataflow/DataflowVolumeAnyType.h"

// 在模块 StartupModule 中调用
void MyModule::StartupModule()
{
    UE::Dataflow::RegisterVolumeAnyTypes();
}
```

## Demo 示例

一个完整的最小示例，展示如何创建 SDF 并将其转换为体积纹理：

```cpp
// MyVolumeExample.h
#pragma once

#include "CoreMinimal.h"

class FMyVolumeExample
{
public:
    static void RunExample();
};
```

```cpp
// MyVolumeExample.cpp
#include "MyVolumeExample.h"

#include "Dataflow/DataflowVolume.h"
#include "Dataflow/DataflowFloatVolume.h"
#include "Dataflow/DataflowBoolVolume.h"
#include "Dataflow/DataflowFloatVectorVolume.h"
#include "VolumeTexture.h"

void FMyVolumeExample::RunExample()
{
    // 1. 创建一个立方体 SDF
    FDataflowFloatVolume CubeSDF = FDataflowFloatVolume::CreateCubeSDF(
        100.0f,             // InScale
        FVector::ZeroVector, // InCenter
        1.0f                // InVoxelSize
    );

    // 2. 创建一个球体 SDF
    FDataflowFloatVolume SphereSDF = FDataflowFloatVolume::CreateSphereSDF(
        1.0f,               // InVoxelSize
        60.0f,              // InRadius
        FVector(30, 0, 0)   // InCenter（偏移以产生交集）
    );

    // 3. 将 SDF 转换为 Fog Volume
    FDataflowFloatVolume FogVolume = CubeSDF.CovertSDFToFogVolume(
        true,   // InPruneTolerance
        0.01f,  // InTolerance
        true,   // InFloodFillOutput
        true    // InActivateInterior
    );

    // 4. 查询活跃体素
    TArray<FBox> ActiveVoxels;
    CubeSDF.GetActiveVoxels(0.0f, ActiveVoxels);
    UE_LOG(LogTemp, Log, TEXT("Active voxels: %d"), ActiveVoxels.Num());

    // 5. 创建体积纹理（需要已创建的 UVolumeTexture 资产）
    // UVolumeTexture* VolumeTexture = NewObject<UVolumeTexture>();
    // CubeSDF.CreateVolumeTexture(VolumeTexture);

    // 6. 球体填充
    TArray<FVector> Centers;
    TArray<float> Radii;
    CubeSDF.VolumeToSpheres(
        5,      // 最小球体数
        20,     // 最大球体数
        false,  // 重叠
        2.0f,   // 最小半径
        15.0f,  // 最大半径
        0.0f,   // 等值面
        1,      // 实例数
        Centers,
        Radii
    );

    UE_LOG(LogTemp, Log, TEXT("Generated %d spheres"), Centers.Num());
    for (int32 i = 0; i < Centers.Num(); ++i)
    {
        UE_LOG(LogTemp, Log, TEXT("  Sphere %d: Center=(%.1f, %.1f, %.1f) Radius=%.2f"),
            i, Centers[i].X, Centers[i].Y, Centers[i].Z, Radii[i]);
    }
}
```

## 模块依赖

本插件依赖 `Dataflow` 插件（已在 .uplugin 中声明）。

从源码头文件可推断以下关键依赖：

| 模块 | 用途 |
|---|---|
| `OpenVDB` | 第三方体素化库，提供核心体积数据结构和算法 |
| `Dataflow` | UE5 Dataflow 节点图框架，本插件为其扩展体积支持 |
| `GeometryCollection` | 提供 `ManagedArrayCollection`，用于几何体数据管理 |
| `MeshDescription` | 网格描述，用于网格↔体积转换 |
| `TBB` (Intel Threading Building Blocks) | 并行计算，用于体积操作的多线程加速 |

> 注意：`OpenVDB` 和 `TBB` 是 UE5 内置的第三方库，无需额外安装。

## 维护状态

### 近期更新

- 2026-04-17 `49f946b4` [Dataflow]
- 2026-01-27 `bc6b71b7` Dataflow:
- 2026-01-24 `fa3617d8` [Backout] - CL50148102
- 2026-01-24 `b815c490` Dataflow:
- 2026-01-24 `67495252` Dataflow:

### 维护评价

- **状态**：🆕 全新实验性插件
- **实验性标记**：`IsExperimentalVersion=true`，`Installed=false`（默认未安装）
- **平台支持**：仅 Win64、Linux、Mac
- **依赖关系**：依赖 `Dataflow` 插件，后者本身也在持续发展中
- **风险提示**：作为实验性插件，API 可能发生重大变更，不建议在生产环境中使用
- **推荐程度**：适合早期探索和原型开发，关注 Dataflow 生态的开发者应持续跟踪

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/DataflowVolumetricPlugin)
- [OpenVDB 官方文档](https://www.openvdb.org/documentation/)
- [Dataflow 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Dataflow)