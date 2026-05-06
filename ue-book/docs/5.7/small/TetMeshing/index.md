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
| 创建时间 | 2022-09-16 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/TetMeshing) | |

## 用途

该插件提供**四面体（Tetrahedral）网格的生成与优化**功能，是几何处理管线中用于体网格（Volumetric Mesh）构造的基础模块。  
它实现了经典的「等值面填充（Isosurface Stuffing）」算法（Labelle & Shewchuk），能够从隐式曲面（如 SDF、快速缠绕数）快速生成包含良好二面角（Dihedral Angles）的符合性四面体网格。

为什么存在？  
在物理仿真（有限元分析、形变模拟）、医学成像、体渲染等场景中，需要将连续几何体离散化为四面体单元。该插件提供了纯 CPU 端的算法实现，可作为几何处理工具链的底层生成器。

## 使用场景

- **物理仿真预处理** — 为形变体模拟生成四面体网格（如布料、软体、肌肉）。
- **医学/科学可视化** — 基于 CT/MRI 数据（体素隐式函数）生成四面体网格。
- **几何算法研究** — 作为 Isosurface Stuffing 算法的实验性实现，可用于比较不同四面体生成策略。
- **自定义体网格生成** — 可继承 `TTetMeshGenerator` 实现其他四面体化算法（如 Delaunay、 Advancing Front）。

## 蓝图用法

该插件为纯 C++ 模块，未暴露任何 `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)` 给蓝图。  
所有 API 仅可通过 C++ 调用。

| 节点 | 说明 | 所在类 |
|---|---|---|
| — | 无可用蓝图节点 | — |

## C++ 用法

### 头文件引入

```cpp
#include "Generate/TetMeshGenerator.h"
#include "Generate/IsosurfaceStuffing.h"
```

### 基本用法

以下示例演示如何使用 `TIsosurfaceStuffing` 生成一个球体（隐式函数为 `|p| - Radius`）的四面体网格。

```cpp
// 创建一个填充器实例，使用 double 精度，二分法求根
using RealType = double;
UE::Geometry::TIsosurfaceStuffing<RealType> Stuffing;

// 1. 设置生成参数
Stuffing.Bounds = UE::Math::TBox<RealType>({-10, -10, -10}, {10, 10, 10}); // 包围盒
Stuffing.CellSize = 2.0; // 体素尺寸（越小网格越密）
Stuffing.IsoValue = 0;   // 等值面值
Stuffing.Implicit = [](UE::Math::TVector<RealType> P) -> RealType
{
    // 半径为 5 的球体的符号距离函数
    return P.Length() - 5.0;
};
Stuffing.RootModeSteps = 5; // 根查找迭代次数

// 2. 生成网格
Stuffing.Generate();

// 3. 访问结果
const auto& Vertices = Stuffing.Vertices;     // TArray<FVector3d>
const auto& Tets = Stuffing.Tets;            // TArray<FIntVector4>
const auto& Triangles = Stuffing.Triangles;  // TArray<FIntVector3>（表面三角面）

// 注意：生成器仅产生拓扑数据，不直接创建 UProceduralMeshComponent 或 AStaticMeshActor
```

**来源文件**：`Engine/Plugins/Experimental/TetMeshing/Source/TetMeshing/Public/Generate/IsosurfaceStuffing.h`

### 进阶用法

通过继承 `TTetMeshGenerator` 实现自定义四面体生成器：

```cpp
class FMyGenerator : public UE::Geometry::TTetMeshGenerator<float>
{
public:
    virtual TTetMeshGenerator& Generate() override
    {
        // 手动构造一个简单的四面体（顶点索引 0,1,2,3）
        SetBufferSizes(4, 1, true, 4, true);
        Vertices[0] = FVector3f(0,0,0);
        Vertices[1] = FVector3f(1,0,0);
        Vertices[2] = FVector3f(0,1,0);
        Vertices[3] = FVector3f(0,0,1);
        Tets[0] = FIntVector4(0,1,2,3);
        TetIDs[0] = 0;
        Triangles[0] = FIntVector3(0,1,2);
        Triangles[1] = FIntVector3(0,2,3);
        Triangles[2] = FIntVector3(0,3,1);
        Triangles[3] = FIntVector3(1,3,2);
        TriangleIDs[0] = 0;
        TriangleIDs[1] = 1;
        TriangleIDs[2] = 2;
        TriangleIDs[3] = 3;
        return *this;
    }
};
```

## Demo 示例

以下是一个完整的可编译最小示例，展示如何在 C++ 插件模块中使用 `TIsosurfaceStuffing` 生成四面体网格并打印统计信息。

```cpp
// TetMeshingDemo.h
#pragma once
#include "CoreMinimal.h"
#include "Stats/Stats.h"

class FTetMeshingDemo
{
public:
    static void RunTetMeshingTest();
};

// TetMeshingDemo.cpp
#include "TetMeshingDemo.h"
#include "Generate/IsosurfaceStuffing.h"
#include "Math/Box.h"

void FTetMeshingDemo::RunTetMeshingTest()
{
    using Real = double;
    UE::Geometry::TIsosurfaceStuffing<Real> Stuffing;

    Stuffing.Bounds = FBox3d(FVector3d(-5), FVector3d(5));
    Stuffing.CellSize = 1.0;
    Stuffing.IsoValue = 0.0;
    Stuffing.Implicit = [](FVector3d P) -> Real
    {
        return P.Length() - 3.0; // 半径 3 的球
    };
    Stuffing.Generate();

    UE_LOG(LogTemp, Log, TEXT("Generated %d vertices, %d tetrahedra, %d surface triangles"),
        Stuffing.Vertices.Num(), Stuffing.Tets.Num(), Stuffing.Triangles.Num());
    
    // 输出前 5 个四面体（测试用）
    for (int32 i = 0; i < FMath::Min(5, Stuffing.Tets.Num()); ++i)
    {
        const auto& Tet = Stuffing.Tets[i];
        UE_LOG(LogTemp, Log, TEXT("Tet %d: v%d v%d v%d v%d"),
            i, Tet.X, Tet.Y, Tet.Z, Tet.W);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GeometryProcessing` | 提供基础几何类型（`FBox3d`, `FVector3` 等）及隐式函数工具 |

> 注意：插件内 `TetMeshing.Build.cs` 的 `PublicDependencyModuleNames` 包含 `GeometryProcessing`。其他常见依赖（Core、CoreUObject、Engine）已省略。

## 维护状态

### 近期更新

```
- 2023-11-20 763a6119 Fix C4072 warnings（修复编译器警告）
- 2023-02-17 73c74eaf Removing redundant include paths（移除冗余包含路径）
- 2022-10-21 610c4676 Update vendor links for built-in plugins to use secure protocol（更新第三方链接协议）
- 2022-09-17 73159497 CIS fix for PVS studio warning in IsosurfaceStuffing.h（PVS 静态分析警告修复）
- 2022-09-16 b13eab1b fix CIS issue: PVS Studio warnings in IsosurfaceStuffing.h（初始提交后立即修复）
```

### 维护评价

- **创建时间**：2022-09-16，至今约 3 年。
- **最近实质性功能更新**：2022-09-16（初始提交）后，未添加新功能或算法改进，均为编译修复和警告清理。
- **当前状态**：维护不活跃（超过 1 年无功能性更新）。
- **风险**：插件标记为 `IsBetaVersion=true`，且 `EnabledByDefault=false`，表明仍处于实验阶段，算法实现**不完整**（源码中有多处 `// TODO` 标记，如只实现了 `Bisection` 根查找方法，未实现基于种子点的稀疏网格采样）。`Generate()` 函数体内大量延续性代码被注释或留空。
- **推荐使用**：仅建议用于**学习研究**或**实验性验证**。不推荐用于生产项目，除非你能自行完善缺失功能。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/TetMeshing)
- [官方文档](https://docs.unrealengine.com/)（该插件无独立文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/TetMeshing/Tests)（插件目录下未包含测试，可能位于主仓库引擎测试目录）