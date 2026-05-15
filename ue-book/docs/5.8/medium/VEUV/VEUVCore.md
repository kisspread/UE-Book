# VEUV - Volume Encoded UV Maps

> Volume encoded UV parameterization

| 属性 | 值 |
|---|---|
| 中文名 | 体积编码UV贴图 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产） |
| 模块 | `VEUVCore` (Runtime), `VEUVEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-05-12 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/VEUV) | |

## 用途

VEUV 是一种用于 3D 网格表面参数化（UV 展开）的实验性算法，它使用体素网格和数学优化方法来生成高质量的 UV 映射。与传统的 UV 展开方法（如 ABF、LSCM 等）相比，它旨在通过体积编码（Volume Encoded）的技术，在保持模型几何细节的同时，实现更优的 UV 覆盖率和更少的接缝。该插件主要用于需要自动化或高质量 UV 展开的场景，特别是在处理复杂几何体时，能够改善纹理利用率和接缝分布。

## 使用场景

- **复杂角色模型**：为具有复杂拓扑结构（如手指、发缕、装甲缝隙）的角色模型自动生成 UV，减少手动拆分和接缝处理的工作量。
- **程序化生成资产**：结合 Houdini 或其他程序化工具，对动态生成的模型进行实时的 UV 展开，确保纹理能正确映射。
- **游戏开发中的 LOD 制作**：为不同细节层次的模型自动生成并优化 UV，以配合纹理流送或虚拟纹理系统。
- **工业可视化与 CAD 模型**：处理 CAD 软件导出的、缺乏良好 UV 信息的模型，以便为其贴上纹理进行可视化。

## 蓝图用法

本插件的核心功能主要通过 C++ API (`VEUV::FOptimizer::Compute`) 暴露。蓝图中主要使用其配置结构体 (`FVEUVConfig`) 来调整优化参数，具体计算通常在 C++ 侧完成。编辑器工具（如工具菜单或资产编辑器）可能提供蓝图接口。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Compute` | 对给定的网格执行体积编码 UV 参数化优化。输入网格和配置，返回包含优化后 UV 的网格结果。 | `VEUV::FOptimizer` (C++ only) |

### 使用示例（蓝图描述）

由于核心计算函数是 C++ 的静态函数，在蓝图中使用通常需要一个 C++ 包装器或者通过编辑器工具操作。一个可能的蓝图工作流是：
1.  从场景或资产中获取网格的顶点和索引数据。
2.  创建一个 `FVEUVConfig` 结构体并设置参数（如体素数量、采样数量等）。
3.  将这些数据传递给一个自定义的 Blueprint 函数库节点或 C++ 暴露的异步任务节点。
4.  接收返回的 `FResult` 结构体，其中包含优化后的顶点位置（包含 UV）和三角形索引。
5.  将结果应用到你的网格组件或创建新的静态网格体。

## C++ 用法

### 头文件引入

```cpp
#include "VEUV/VEUVOptimizer.h"
#include "VEUV/VEUVTypes.h"
```

### 基本用法

使用 `VEUV::FOptimizer::Compute` 函数为网格计算 UV。

```cpp
// 示例代码，展示了使用 VEUV 优化器的基本流程
// 假设你已经有了从静态网格体获取的顶点和三角形数据
TArray<FVector3f> InVertices = ...; // 从源网格获取的顶点位置
TArray<FInt32Vector3> InFaces = ...; // 从源网格获取的三角形索引

// 1. 构建输入网格
VEUV::FMesh InputMesh;
InputMesh.Vertices = InVertices;
InputMesh.Faces = InFaces;

// 2. 配置优化参数
VEUV::FVEUVConfig Config;
// 根据需要调整参数，例如：
// Config.VoxelCount = 64;
// Config.Sampling.TotalSamples = 8192;
// Config.Solver.GlobalIterations = 500;

// 3. 执行优化计算
VEUV::FResult Result = VEUV::FOptimizer::Compute(InputMesh, Config);

// 4. 使用结果
if (Result.bSuccess)
{
    // Result.Mesh 包含优化后的网格数据
    // 其中 Result.Mesh.Vertices 的 XY 分量可以视为优化后的 UV 坐标
    // 你可以将这些 UV 应用到你的实际网格体上
    ApplyUVsToMesh(Result.Mesh);
}
```

### 进阶用法

结合配置的各个部分进行更精细的控制。

```cpp
// 创建一个更复杂的配置
VEUV::FVEUVConfig AdvancedConfig;
AdvancedConfig.VoxelCount = 128; // 提高体素分辨率以获得更精细的细节
AdvancedConfig.Sampling.TotalSamples = 16384; // 增加采样以提高质量
AdvancedConfig.Sampling.ComplexityAlpha = 10.0f; // 更强调复杂区域的采样
AdvancedConfig.Sampling.AdaptiveFraction = 0.7f; // 增加自适应采样的比例
AdvancedConfig.Solver.bEnableGlobalSolve = true; // 启用全局求解
AdvancedConfig.Solver.GlobalIterations = 2000; // 增加全局迭代次数
AdvancedConfig.Packing.bOrientCharts = true; // 启用图表定向

VEUV::FResult HighQualityResult = VEUV::FOptimizer::Compute(InputMesh, AdvancedConfig);
```

## Demo 示例

一个完整的、可编译的最小示例，展示如何从 C++ 调用 VEUV 优化器。

### VEUVDemo.h
```cpp
// VEUVDemo.h
#pragma once

#include "CoreMinimal.h"

class FVEUVDemo
{
public:
    static void RunDemo();
};
```

### VEUVDemo.cpp
```cpp
// VEUVDemo.cpp
#include "VEUVDemo.h"
#include "VEUV/VEUVOptimizer.h"
#include "VEUV/VEUVTypes.h"
#include "MeshDescription.h"
#include "StaticMeshAttributes.h"

void FVEUVDemo::RunDemo()
{
    // 1. 获取一个简单的立方体网格数据
    VEUV::FMesh CubeMesh;
    // 8个顶点
    CubeMesh.Vertices.Add(FVector3f(-1, -1, -1));
    CubeMesh.Vertices.Add(FVector3f( 1, -1, -1));
    CubeMesh.Vertices.Add(FVector3f( 1,  1, -1));
    CubeMesh.Vertices.Add(FVector3f(-1,  1, -1));
    CubeMesh.Vertices.Add(FVector3f(-1, -1,  1));
    CubeMesh.Vertices.Add(FVector3f( 1, -1,  1));
    CubeMesh.Vertices.Add(FVector3f( 1,  1,  1));
    CubeMesh.Vertices.Add(FVector3f(-1,  1,  1));
    // 12个三角形（每个面2个）
    CubeMesh.Faces.Add(FInt32Vector3(0, 3, 1)); // 后面
    CubeMesh.Faces.Add(FInt32Vector3(1, 3, 2));
    CubeMesh.Faces.Add(FInt32Vector3(4, 5, 7)); // 前面
    CubeMesh.Faces.Add(FInt32Vector3(5, 6, 7));
    CubeMesh.Faces.Add(FInt32Vector3(0, 1, 5)); // 底面
    CubeMesh.Faces.Add(FInt32Vector3(0, 5, 4));
    CubeMesh.Faces.Add(FInt32Vector3(2, 3, 7)); // 顶面
    CubeMesh.Faces.Add(FInt32Vector3(2, 7, 6));
    CubeMesh.Faces.Add(FInt32Vector3(0, 4, 3)); // 左面
    CubeMesh.Faces.Add(FInt32Vector3(3, 4, 7));
    CubeMesh.Faces.Add(FInt32Vector3(1, 2, 5)); // 右面
    CubeMesh.Faces.Add(FInt32Vector3(2, 6, 5));

    // 2. 配置（使用较低的分辨率以快速演示）
    VEUV::FVEUVConfig DemoConfig;
    DemoConfig.VoxelCount = 32;
    DemoConfig.Sampling.TotalSamples = 2048;
    DemoConfig.Solver.GlobalIterations = 200;

    // 3. 执行优化
    VEUV::FResult Result = VEUV::FOptimizer::Compute(CubeMesh, DemoConfig);

    if (Result.bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("VEUV Demo Succeeded!"));
        UE_LOG(LogTemp, Log, TEXT("Resulting mesh has %d vertices and %d triangles."), 
            Result.Mesh.Vertices.Num(), Result.Mesh.Faces.Num());
        // 此时 Result.Mesh.Vertices[i].X 和 .Y 包含了优化后的 UV 坐标
        // .Z 可能被用作其他用途或保持原样，取决于算法实现
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("VEUV Demo Failed!"));
    }
}
```

## 模块依赖

从代码结构和构建文件推断，VEUV 核心模块依赖于一个重要的第三方数学库。

| 模块 | 用途 |
|---|---|
| `Eigen` | 用于高性能的线性代数运算（矩阵、向量、稀疏矩阵求解），是 VEUV 算法数学计算的核心。 |

## 维护状态

### 近期更新

```
- 2026-05-14 5d715960 Volume Encoded UVs, temporarily disabled injectivity term and moved to dense initial R78 solve
- 2026-05-13 df17886a VEUV: fail out with an empty chart rather than crash if the grid ends up with nothing allocated
- 2026-05-12 e76e4ca8 Volume Encoded UVs, disabled forced injectivity on refinement (too prone to exploding)
- 2026-05-12 cd2e1403 VEUV: add failure reporting -- detect failed packing, empty charts, inf/nan entries, inverted tris i
- 2026-05-12 34b3773a VEUV: distribute complexity sample budget remainder across bins so low-budget voxels are not silentl
```

### 维护评价

VEUV 是一个**非常新的实验性插件**（创建于 2026-05-12）。从最近的 git 提交记录可以看出：
1.  **活跃开发中**：最近几天（2026-05-12 至 05-14）有多次密集的提交，表明它正处于积极的开发和调试阶段。
2.  **问题与修复**：提交记录显示开发者正在处理算法稳定性问题（例如“disabled forced injectivity on refinement (too prone to exploding)”），并添加了错误检测和报告机制（“add failure reporting”）。这表明算法可能还不完全稳定。
3.  **实验性状态**：插件元数据明确标记为 `IsExperimentalVersion: true`，并且默认禁用 (`EnabledByDefault: false`)。这意味着 Epic 将其视为前沿技术研究，不保证 API 稳定性或生产就绪。
4.  **结论**：**目前仅适用于实验和研究目的**。对于生产环境，建议等待其进一步成熟。可以关注其后续更新，评估算法的稳定性和生成质量是否满足项目需求。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/VEUV)
- [官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/) (待 VEUV 正式发布后可能会有相关页面)