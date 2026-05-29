# Tet Meshing

> Adds Module for Generating and Refining Tetrahedral Meshes.

| 属性 | 值 |
|---|---|
| 中文名 | 四面体网格生成 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `TetMeshing` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-09-07 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TetMeshing) | |

## 用途

TetMeshing 插件提供了一套用于**生成和细化四面体网格**的运行时模块。它主要解决从隐式曲面（例如符号距离函数或快速缠绕数函数）生成高质量四面体网格的问题。其核心算法是 **Isosurface Stuffing**，一种在给定边界框内，通过体素化空间并使用隐式函数定义的等值面来生成四面体网格的方法。该插件是实验性的，旨在为物理模拟、有限元分析或需要将连续几何体离散化为四面体网格的场景提供基础工具。

## 使用场景

- **物理模拟**：为刚体动力学或可变形体模拟生成精确的碰撞体或内部结构。
- **有限元分析（FEA）**：将复杂的隐式几何体转换为四面体网格，用于应力、热传导等模拟。
- **程序化几何生成**：结合隐式建模技术，动态生成并网格化物体。
- **研究与开发**：研究四面体网格生成算法或进行相关算法原型开发。

## 蓝图用法

目前，插件的核心功能主要封装在 C++ 模板类中，未暴露 `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)` 接口。因此，无法直接在蓝图中使用。用户需要通过 C++ 代码调用。

## C++ 用法

该插件提供了一组模板类，用于构建四面体网格生成器。主要流程是：定义一个继承自 `TTetMeshGenerator` 的生成器，配置其参数并调用 `Generate()` 方法。

### 头文件引入

```cpp
#include "TetMeshingPlugin.h"
#include "Generate/TetMeshGenerator.h"
#include "Generate/IsosurfaceStuffing.h"
```

### 基本用法

以下示例展示了如何使用 `TIsosurfaceStuffing` 类从一个隐式球体函数生成四面体网格。

**来源文件**：`Source/TetMeshing/Public/Generate/IsosurfaceStuffing.h`

```cpp
#include "Generate/IsosurfaceStuffing.h"
#include "Math/Box.h"
#include "Math/Vector.h"

void GenerateTetrahedralMeshFromSphere()
{
    // 1. 定义隐式函数（例如，一个半径为 50 的球体）
    auto SphereImplicit = [](UE::Math::TVector<float> Point) -> float
    {
        return 50.0f - Point.Size(); // 在球体内部返回正值，外部返回负值
    };

    // 2. 创建 IsosurfaceStuffing 生成器实例（使用 float 类型和二分法求根）
    UE::Geometry::TIsosurfaceStuffing<float, UE::Geometry::ERootFindingMethod::Bisection> StuffingGenerator;

    // 3. 配置生成器参数
    StuffingGenerator.Bounds = UE::Math::TBox<float>(UE::Math::TVector<float>(-60, -60, -60), UE::Math::TVector<float>(60, 60, 60));
    StuffingGenerator.CellSize = 10.0f; // 每个 BCC 单元格的大小
    StuffingGenerator.Implicit = SphereImplicit;
    StuffingGenerator.IsoValue = 0.0f; // 等值面值为 0

    // 4. 执行生成
    StuffingGenerator.Generate();

    // 5. 访问生成的网格数据
    const TArray<UE::Math::TVector<float>>& Vertices = StuffingGenerator.Vertices;
    const TArray<FIntVector4>& Tetrahedra = StuffingGenerator.Tets;
    const TArray<FIntVector3>& Triangles = StuffingGenerator.Triangles; // 可选的边界三角形

    UE_LOG(LogTetMeshing, Log, TEXT("Generated %d vertices, %d tetrahedra, %d triangles."), Vertices.Num(), Tetrahedra.Num(), Triangles.Num());
}
```

### 进阶用法

**获取边界三角形**：`TIsosurfaceStuffing` 生成器在生成四面体的同时，也会生成位于隐式曲面边界上的三角形（存储在 `Triangles` 数组中）。这对于可视化或提取网格表面很有用。

**重置并重新生成**：可以调用 `Reset()` 方法清空生成器的内部状态和输出数组，然后用新的参数再次调用 `Generate()`。

```cpp
// 重置生成器
StuffingGenerator.Reset();
// 修改参数（例如，改变隐式函数或网格大小）
StuffingGenerator.CellSize = 5.0f;
// 重新生成
StuffingGenerator.Generate();
```

**自定义网格生成器**：你可以继承 `TTetMeshGenerator<float>` 来创建自己的四面体网格生成算法，并填充 `Vertices`、`Tets` 等数组。

## Demo 示例

以下是一个完整的最小示例，展示如何在一个控制台应用或测试中使用该插件生成一个简单的四面体网格。

```cpp
// TetMeshingDemo.h
#pragma once

#include "CoreMinimal.h"
#include "Generate/IsosurfaceStuffing.h"

class FTetMeshingDemo
{
public:
    static void RunDemo();
};

// TetMeshingDemo.cpp
#include "TetMeshingDemo.h"
#include "HAL/PlatformMisc.h"

void FTetMeshingDemo::RunDemo()
{
    // 定义隐式函数：一个简单的 Box，内部为正，外部为负
    auto BoxImplicit = [](UE::Math::TVector<float> Point) -> float
    {
        UE::Math::TBox<float> Box(UE::Math::TVector<float>(-30, -30, -30), UE::Math::TVector<float>(30, 30, 30));
        // 计算到 Box 边界的有符号距离（简化版，使用点到中心距离）
        UE::Math::TVector<float> Center = Box.GetCenter();
        UE::Math::TVector<float> Extent = Box.GetExtent();
        UE::Math::TVector<float> DistanceToFace = Extent - (Point - Center).GetAbs();
        // 如果所有分量都为正，则在内部，返回最小分量作为距离；否则为外部，返回最大负分量
        float MinComponent = FMath::Min(DistanceToFace.X, FMath::Min(DistanceToFace.Y, DistanceToFace.Z));
        return MinComponent;
    };

    UE::Geometry::TIsosurfaceStuffing<float> Generator;
    Generator.Bounds = UE::Math::TBox<float>(UE::Math::TVector<float>(-40, -40, -40), UE::Math::TVector<float>(40, 40, 40));
    Generator.CellSize = 15.0f;
    Generator.Implicit = BoxImplicit;
    Generator.IsoValue = 0.0f;

    Generator.Generate();

    // 输出结果
    UE_LOG(LogTemp, Warning, TEXT("Demo: Generated a tetrahedral mesh with %d vertices and %d tetrahedra."), Generator.Vertices.Num(), Generator.Tets.Num());
}
```

## 模块依赖

插件依赖于 GeometryProcessing 插件。

| 模块 | 用途 |
|---|---|
| `GeometryProcessing` | 提供几何处理的基础工具和框架 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2023-11-20 | `763a6119` | Fix C4072 warnings | 修复编译器 C4072 警告（函数参数未使用） |
| 2023-02-17 | `73c74eaf` | Removing redundant include paths: | 移除多余的头文件包含路径 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 更新内置插件的供应商链接以使用安全协议 |
| 2022-09-17 | `73159497` | CIS fix for PVS studio warning in IsosurfaceStuffing.h | 修复 PVS Studio 在 IsosurfaceStuffing.h 中发出的静态分析警告 |
| 2022-09-16 | `b13eab1b` | fix CIS issue: PVS Studio warnings in IsosurfaceStuffing.h | 修复持续集成（CIS）流程中报告的 PVS Studio 警告 |

### 维护评价

- **创建时间**：2022 年 9 月，相对年轻。
- **最近更新频率**：最近一次实质性更新（修复编译器警告）在 2023 年 11 月，距今已超过 1 年。前期的更新主要是警告修复和路径整理，没有功能增强。
- **活跃度**：**维护不活跃**。已经超过 1 年没有新的功能提交。
- **已知限制**：该插件处于实验阶段（`IsBetaVersion=true`），且默认禁用。目前仅包含一个基础的 Isosurface Stuffing 算法，功能有限。
- **推荐使用**：适用于研究和原型开发。如果需要在生产环境中使用四面体网格生成，建议评估其稳定性和功能是否满足需求，或寻找更成熟的替代方案。由于长期未更新，可能存在未修复的问题。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TetMeshing)
- [官方文档]()（无）