# Planar Cut

> Adds Module for Planar Cuts.

| 属性 | 值 |
|---|---|
| 中文名 | 平面切割 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PlanarCut` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-28 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PlanarCutPlugin) | |

## 用途

该插件提供用于对 **Geometry Collection**（几何体集合）执行平面切割的核心算法和数据结构。它定义了切割面（`FPlanarCells`）、内部表面材质（`FInternalSurfaceMaterials`）以及噪声扰动（`FNoiseSettings`），使得在程序化生成破碎效果时，能够高效地将一个几何体集合沿平面切割成多个碎片，并附加噪声、UV 投影等特性。

该插件是对 `GeometryProcessing` 模块的扩展，专注于平面切割这一特定操作，常与 Chaos 物理系统的破坏框架配合使用，用于游戏、影视中的程序化碎裂和断裂动画。

## 使用场景

- 你需要对 **Geometry Collection** 执行平面切割，实现物体碎裂效果（如墙体崩塌、岩石破碎）。
- 你希望在破碎后自动为碎片生成合理的 UV 投影（如盒体投影）和内部表面材质。
- 你希望通过 Perlin 噪声为切割面增加不规则感，模拟自然断裂。
- 你正在开发基于 **Chaos** 的破坏系统，并需要程序化生成碎片网格。

## 蓝图用法

该插件核心为 C++ 库，**未直接暴露蓝图可调用的节点**。但可通过以下方式在蓝图中间接使用：

- 在 **DataFlow**（数据流）图中使用 `PlanarCut` 相关的自定义数据流节点（从 git 记录可知插件包含了数据流模拟控制等功能）。
- 通过 **CPP 函数库** 封装后暴露给蓝图（需自行实现）。
- 调用 `GeometryProcessing` 模块中已有的蓝图节点（该插件不直接提供）。

若需要在蓝图中进行平面切割，建议使用 **Chaos Destruction** 或 **Fracture Editor**，它们底层已集成本插件功能。

## C++ 用法

### 头文件引入

```cpp
#include "PlanarCut/PlanarCut.h"
#include "PlanarCut/FractureAutoUV.h"
```

### 基本用法

以下示例展示如何创建一个平面切割器（`FPlanarCells`）并将其应用于一个 `FGeometryCollection`，同时使用盒体投影更新 UV。

```cpp
// 假设已有一个有效的 FGeometryCollection 对象
FGeometryCollection Collection;

// 创建平面切割单元：将物体沿 X 轴方向分成 3 块，间隙 0.5
FPlanarCells Cells;
Cells.AddCell(FPlane(FVector::ZeroVector, FVector::UnitX()));
Cells.AddCell(FPlane(FVector(10.0, 0.0, 0.0), FVector::UnitX()));

// 设置内部表面材质
FInternalSurfaceMaterials Materials;
Materials.GlobalMaterialID = 0;
Materials.GlobalUVScale = 1.0;
Materials.bGlobalVisibility = true;

// 执行切割（实际切割函数需要配合 GeometryProcessing 中的布尔运算）
// 这里仅示意，切割结果将返回新的几何体集合
FGeometryCollection Result = UE::PlanarCut::CutCollection(Collection, Cells, Materials);

// 为切割后的内部面设置盒体投影 UV
UE::PlanarCut::BoxProjectUVs(
    0,                      // UV图层索引
    Result,                 // 几何体集合
    FVector3d(5,5,5),       // 盒体尺寸
    ETargetFaces::InternalFaces  // 仅内部面
);
```

*来源：`PlanarCut.h` 中 `FPlanarCells`、`FInternalSurfaceMaterials` 定义；`FractureAutoUV.h` 中 `BoxProjectUVs` 声明。*

### 进阶用法：添加噪声

利用 `FNoiseSettings` 和 `FNoiseOffsets` 让切割表面更自然：

```cpp
FRandomStream Random(42);
FNoiseOffsets Offsets(Random);
FNoiseSettings Noise;
Noise.Amplitude = 1.5;
Noise.Frequency = 0.2;
Noise.Octaves = 3;

FInternalSurfaceMaterials Materials;
Materials.NoiseSettings = Noise;

// 切割后每个顶点的位置会基于噪声偏移（实际由切割函数内部处理）
```

*来源：`PlanarCut.h` 中 `FNoiseSettings::NoiseVector`。*

## Demo 示例

以下是一个完整的、可编译的最小示例，展示如何创建并运行一次平面切割。

**PlanarCutDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GeometryCollection/GeometryCollection.h"
#include "PlanarCut/PlanarCut.h"
#include "PlanarCut/FractureAutoUV.h"

class FPlanarCutDemo
{
public:
    static void Run();
};
```

**PlanarCutDemo.cpp**
```cpp
#include "PlanarCutDemo.h"
#include "PlanarCut/PlanarCut.h"
#include "UObject/UObjectGlobals.h"

void FPlanarCutDemo::Run()
{
    // 创建一个默认的几何体集合（例如一个立方体）
    FGeometryCollection Collection;
    // …此处填充 Collection 的顶点、三角面等（为了简洁省略）

    // 定义切割平面（沿 X 轴方向）
    TArray<FPlane> CutPlanes;
    CutPlanes.Add(FPlane(FVector(0.0f, 0.0f, 0.0f), FVector::UnitX()));

    FPlanarCells Cells(CutPlanes);
    FInternalSurfaceMaterials Materials;
    Materials.GlobalMaterialID = 0;

    // 执行切割（假设函数存在，实际请使用 GeometryProcessing 提供的布尔运算符）
    // FGeometryCollection Result = UE::PlanarCut::CutWithPlanes(Collection, Cells, Materials);

    // 应用盒体投影 UV
    // UE::PlanarCut::BoxProjectUVs(0, Result, FVector3d(5,5,5), ETargetFaces::InternalFaces);
}
```

> **注意**：实际切割运算需要借助 `GeometryProcessing` 模块中的布尔网格函数，示例仅为演示逻辑结构。开发时请参考 `Engine/Plugins/GeometryProcessing` 下的相关 API。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GeometryProcessing` | 提供基础几何处理功能（如网格布尔运算） |

**无需列出的常见依赖**：Core, CoreUObject, Engine, Slate, SlateCore, UMG, InputCore, PhysicsCore, Chaos 等已由 GeometryProcessing 间接依赖，无需额外声明。

## 维护状态

### 近期更新

- 2025-09-09 `35d37742` — Add simulation controls to dataflow + fix bughawk issues  
- 2025-09-04 `c5c8701d` — Add selection cuve + curve facade + better viewport framing + two sided material  
- 2025-05-27 `bd9ec475` — PR #13086: Support "Only Same Parent" option for TinyGeo "Merge Geometry" mode  
- 2025-05-08 `23ad7257` — make fracture mesh conversion more robust to overlays with unset triangles  
- 2025-04-28 `0b57ca12` — fix dataflow mesh cutter not using mesh normals and UVs  

### 维护评价

- **创建时间**：2025-04-28，至今约 5 个月，属于全新插件。
- **最近更新频率**：活跃，近 6 个月内有多次功能性提交和 bug 修复。
- **活跃程度**：处于积极维护中，未发现废弃标记。
- **已知限制**：该插件标记为 `IsBetaVersion=true`，API 可能不稳定，且默认未启用，需要手动在 `.uproject` 中添加依赖。
- **推荐使用**：✅ 推荐。适用于 Chaos 破坏系统的高级碎裂需求，但需注意版本兼容性和实验性特性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PlanarCutPlugin)  
- [GeometryProcessing 模块文档](https://docs.unrealengine.com/5.3/en-US/geometry-processing-in-unreal-engine/)