# Proxy LOD Plugin (Experimental)

> A plugin to generate Proxy LOD systems.

| 属性 | 值 |
|---|---|
| 中文名 | 代理LOD生成器 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（代码库） |
| 模块 | `ProxyLODMeshReduction` (Editor), `DirectXMesh` (External), `UVAtlas` (External) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-30 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/ProxyLODPlugin) | |

## 用途

ProxyLODPlugin 是一个实验性的编辑器插件，用于为复杂网格生成高效的代理 LOD（Level of Detail）几何体。其核心功能是将高精度网格进行简化，并将简化后的网格打包到 UV 图集中，从而为远处的物体创建低多边形的替代模型，以优化渲染性能。该插件整合了 DirectX Mesh 库（用于网格处理与优化）和 UVAtlas 库（用于 UV 图集生成），提供了一个完整的从输入网格到优化代理网格的流水线。

## 使用场景

- **开放世界优化**：为场景中大量远处物体（如建筑、岩石、树木）生成代理 LOD，减少渲染负载。
- **复杂场景优化**：处理由数百万个三角形组成的复杂模型，生成保持大致外观的简化版本，用于远景渲染。
- **批处理工具开发**：作为编辑器工具的基础，用于自动化生成资产的代理几何体。

## 蓝图用法

该插件主要面向编辑器操作和底层数据处理，未发现通过 UFUNCTION 暴露给蓝图的公开 API。其功能主要通过编辑器操作或 C++ 调用实现。

## C++ 用法

### 头文件引入

```cpp
// 引入第三方库头文件
#include "DirectXMesh.h"
#include "UVAtlas.h"

// 引入插件主模块头文件（根据需要）
#include "ProxyLODMeshReductionModule.h"
```

### 基本用法

从第三方库的公开 API 来看，主要涉及网格处理和 UV 图集生成。

**使用 DirectXMesh 进行网格优化**：
```cpp
// 假设已有顶点缓冲区 pPositions 和索引缓冲区 pIndices
std::vector<uint32_t> adjacency(nFaces * 3);

// 生成邻接信息
DirectX::GenerateAdjacencyAndPointReps(
    pIndices, nFaces,
    pPositions, nVerts,
    epsilon,
    nullptr, // pointRep
    adjacency.data()
);

// 优化顶点顺序以提高缓存命中率
std::vector<uint32_t> vertexRemap(nVerts);
DirectX::OptimizeVertices(pIndices, nFaces, nVerts, vertexRemap.data());

// 应用顶点重映射到索引缓冲区
DirectX::FinalizeIB(pIndices, nFaces, vertexRemap.data(), nVerts, pOptimizedIndices);
```

**使用 UVAtlas 生成 UV 图集**：
```cpp
std::vector<DirectX::UVAtlasVertex> vMeshOutVertexBuffer;
std::vector<uint8_t> vMeshOutIndexBuffer;
std::vector<uint32_t> pvFacePartitioning;
std::vector<uint32_t> pvVertexRemapArray;

// 创建 UV 图集
HRESULT hr = DirectX::UVAtlasCreate(
    positions, nVerts,
    indices, DXGI_FORMAT_R32_UINT, nFaces,
    maxChartNumber, maxStretch,
    textureWidth, textureHeight, gutter,
    adjacency,
    nullptr, // falseEdgeAdjacency
    nullptr, // pIMTArray
    nullptr, // statusCallBack
    0.0001f, // callbackFrequency
    DirectX::UVATLAS_DEFAULT,
    vMeshOutVertexBuffer,
    vMeshOutIndexBuffer,
    &pvFacePartitioning,
    &pvVertexRemapArray
);
```

### 进阶用法

结合两个库的功能，可以实现完整的代理 LOD 生成流程：
1. 使用 DirectXMesh 对原始网格进行清理、验证和优化。
2. 使用 UVAtlas 为优化后的网格生成 UV 图集，将多个图表（chart）打包到一张纹理中。
3. 根据 UV 图集结果，生成代理网格的顶点和索引数据。

## Demo 示例

由于该插件是底层处理库，没有独立的 Actor 或 Component。其使用示例通常体现在编辑器操作或作为其他工具模块的依赖。下面是一个概念性的 C++ 用法片段，展示了如何结合两个库：

```cpp
// ProxyLODGenerator.h
#pragma once
#include "CoreMinimal.h"

class FProxyLODGenerator
{
public:
    // 生成代理LOD网格
    bool GenerateProxyLOD(
        const void* OriginalVertices, size_t VertexCount, size_t VertexStride,
        const void* OriginalIndices, size_t FaceCount, DXGI_FORMAT IndexFormat,
        /* 输出参数 */
        void*& OutVertices, size_t& OutVertexCount,
        void*& OutIndices, size_t& OutFaceCount
    );

private:
    // 简化网格
    bool SimplifyMesh(/* ... */);
    // 生成UV图集
    bool PackUVAtlas(/* ... */);
};
```

```cpp
// ProxyLODGenerator.cpp
#include "ProxyLODGenerator.h"
#include "DirectXMesh.h"
#include "UVAtlas.h"

bool FProxyLODGenerator::GenerateProxyLOD(/* ... */)
{
    // 步骤1: 网格清理和优化
    std::vector<uint32_t> adjacency(FaceCount * 3);
    DirectX::GenerateAdjacencyAndPointReps(/* ... */);

    // 步骤2: (可选) 网格简化
    // SimplifyMesh(...);

    // 步骤3: 生成UV图集
    std::vector<DirectX::UVAtlasVertex> uvVertexBuffer;
    std::vector<uint8_t> uvIndexBuffer;
    HRESULT hr = DirectX::UVAtlasCreate(/* ... */);

    if (SUCCEEDED(hr))
    {
        // 步骤4: 将结果转换为引擎可用的格式
        // ... 转换 OutVertices, OutIndices
        return true;
    }
    return false;
}
```

## 模块依赖

从插件的模块结构推断，使用者可能需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `MeshDescription` | 用于读写和操作网格数据的引擎模块 |
| `MeshConversion` | 在不同网格表示形式之间进行转换的模块 |
| `DirectXMesh` | (由插件提供) 用于网格优化和处理的第三方库 |
| `UVAtlas` | (由插件提供) 用于 UV 图集生成的第三方库 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量转换为浮点数的警告。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修正了 32 位格式说明符在参数为 64 位时使用，反之亦然。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF。 |
| 2025-10-30 | `a0e12af6` | Ran UnrealCodeFixup on Engine to change all ~Type() {} to instead be ~Type() = default | 使用 UnrealCodeFixup 将所有 `~Type() {}` 改为 `~Type() = default`。 |
| 2025-09-15 | `8bdc434e` | Workaround to prevent crash in UVAtlas | 针对 UVAtlas 的崩溃问题进行了规避处理。 |

### 维护评价

该插件创建于2024年1月，目前处于**实验性状态**（`IsBetaVersion=true`，默认未启用）。从近期更新记录看，最近的提交集中在**代码质量修复和编译警告清理**上，而非功能性更新。最近一次实质性功能相关修复是2025年9月对 UVAtlas 库的崩溃规避。综合来看，该插件**处于维护中但活跃度不高**，主要用于内部或特定场景的网格优化流程。由于其实验性质且默认关闭，**不建议在生产环境或通用项目中依赖此插件**，更适合作为高级网格处理流程的参考或内部工具链的一部分。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/ProxyLODPlugin)
- [官方文档]() (无)
- [测试用例]() (插件目录内未发现测试文件)