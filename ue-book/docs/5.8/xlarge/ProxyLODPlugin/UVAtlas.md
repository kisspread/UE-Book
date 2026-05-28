# Proxy LOD Plugin

> A plugin to generate Proxy LOD systems.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 代理LOD插件 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ProxyLODMeshReduction` (Editor), `DirectXMesh` (External), `UVAtlas` (External) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-30 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/ProxyLODPlugin) | |

## 用途

ProxyLODPlugin 用于从高面数静态网格生成**代理 LOD（Proxy Level of Detail）**网格。其核心思路是：将复杂几何体简化为一个更低面数的代理网格，同时通过 UV Atlas 算法重新计算 UV 坐标，使得简化后的网格能够正确贴图。

该插件内部集成了两个微软 DirectX 工具库：

- **UVAtlas**：UV 图集生成库。负责将 3D 网格的表面"展开"到 2D 纹理空间，通过图分区（chart partitioning）和打包（packing）算法，生成高效利用纹理空间的 UV 布局。
- **DirectXMesh**：网格处理工具库。提供邻接关系计算、法线/切线计算、索引/顶点缓冲读写、网格清理和优化等底层功能。

插件通过 `ProxyLODMeshReduction` 编辑器模块调用这两个第三方库，实现从输入网格到代理 LOD 网格的完整流水线：网格简化 → UV 重计算 → 纹理烘焙。

## 使用场景

- 你在做开放世界游戏，需要为远距离场景生成低面数代理网格以降低渲染开销
- 你有复杂的建筑/地形模型，需要自动生成简化的碰撞体或遮挡体
- 你需要将多个网格合并为一个代理网格，同时保持正确的纹理映射
- 你在制作 LOD 流水线，希望在 UV 空间中智能分配纹理精度（高频细节区域获得更多纹理空间）

## 蓝图用法

该插件为纯编辑器 C++ 模块，未暴露 BlueprintCallable API。所有操作通过编辑器命令或 C++ 接口完成。

## C++ 用法

### 模块概述

该插件的源码主要由三个部分组成：

| 模块 | 用途 |
|---|---|
| `ProxyLODMeshReduction` | 编辑器模块，代理 LOD 生成的主逻辑 |
| `UVAtlas` | 第三方库，UV 图集算法 |
| `DirectXMesh` | 第三方库，网格处理工具 |

### 核心 API：UVAtlas（第三方库）

UVAtlas 提供了完整的 UV 图集生成流水线，分为三个阶段：

#### 1. 一步完成：UVAtlasCreate

```cpp
#include "UVAtlas.h"

using namespace DirectX;

HRESULT UVAtlasCreate(
    const XMFLOAT3* positions,        // 顶点位置数组
    size_t nVerts,                     // 顶点数量
    const void* indices,               // 索引缓冲（uint16_t 或 uint32_t）
    DXGI_FORMAT indexFormat,           // DXGI_FORMAT_R16_UINT 或 R32_UINT
    size_t nFaces,                     // 面数量
    size_t maxChartNumber,             // 最大图表数量（0 表示仅按拉伸度约束）
    float maxStretch,                  // 最大拉伸度（0=无拉伸，1=任意拉伸）
    size_t width,                      // 纹理宽度（像素）
    size_t height,                     // 纹理高度（像素）
    float gutter,                      // 图表间最小间距（纹素）
    const uint32_t* adjacency,         // 邻接关系（3 * nFaces）
    const uint32_t* falseEdgeAdjacency,// 可选：假边邻接（四边形网格中部的边不被切割）
    const float* pIMTArray,            // 可选：集成度量张量（3 * nFaces）
    std::function<HRESULT(float)> statusCallBack,
    float callbackFrequency,
    DWORD options,                     // UVATLAS_DEFAULT / GEODESIC_FAST / GEODESIC_QUALITY
    std::vector<UVAtlasVertex>& vMeshOutVertexBuffer,  // [输出] 顶点缓冲
    std::vector<uint8_t>& vMeshOutIndexBuffer,         // [输出] 索引缓冲
    std::vector<uint32_t>* pvFacePartitioning = nullptr, // [输出] 面分区
    std::vector<uint32_t>* pvVertexRemapArray = nullptr, // [输出] 顶点重映射
    float* maxStretchOut = nullptr,    // [输出] 实际最大拉伸度
    size_t* numChartsOut = nullptr     // [输出] 实际图表数量
);
```

输出顶点格式 `UVAtlasVertex` 包含位置和 UV：

```cpp
struct UVAtlasVertex {
    DirectX::XMFLOAT3 pos;
    DirectX::XMFLOAT2 uv;
};
```

#### 2. 分步流水线：Partition + Pack

当需要在分区和打包之间插入自定义逻辑时使用：

```cpp
// 第一步：分区（生成图表）
HRESULT UVAtlasPartition(
    const XMFLOAT3* positions, size_t nVerts,
    const void* indices, DXGI_FORMAT indexFormat, size_t nFaces,
    size_t maxChartNumber, float maxStretch,
    const uint32_t* adjacency,
    const uint32_t* falseEdgeAdjacency,
    const float* pIMTArray,
    std::function<HRESULT(float)> statusCallBack, float callbackFrequency,
    DWORD options,
    std::vector<UVAtlasVertex>& vMeshOutVertexBuffer,
    std::vector<uint8_t>& vMeshOutIndexBuffer,
    std::vector<uint32_t>* pvFacePartitioning,
    std::vector<uint32_t>* pvVertexRemapArray,
    std::vector<uint32_t>& vPartitionResultAdjacency,  // [输出] 分区结果邻接
    float* maxStretchOut = nullptr,
    size_t* numChartsOut = nullptr
);

// 第二步：打包（将图表排列到纹理空间）
HRESULT UVAtlasPack(
    std::vector<UVAtlasVertex>& vMeshVertexBuffer,
    std::vector<uint8_t>& vMeshIndexBuffer,
    DXGI_FORMAT indexFormat,
    size_t width, size_t height,
    float gutter,
    const std::vector<uint32_t>& vPartitionResultAdjacency,
    std::function<HRESULT(float)> statusCallBack,
    float callbackFrequency
);
```

#### 3. IMT（集成度量张量）计算

IMT 允许你控制每个三角形在 UV 空间中的拉伸方向和强度，用于自适应纹理精度分配：

```cpp
// 从逐顶点信号计算 IMT
HRESULT UVAtlasComputeIMTFromPerVertexSignal(
    const XMFLOAT3* positions, size_t nVerts,
    const void* indices, DXGI_FORMAT indexFormat, size_t nFaces,
    const float* pVertexSignal,       // 每顶点信号（如颜色、法线）
    size_t signalDimension,            // 信号维度
    size_t signalStride,               // 每顶点字节步长
    std::function<HRESULT(float)> statusCallBack,
    float* pIMTArray                   // [输出] 3 * nFaces
);

// 从纹理数据计算 IMT
HRESULT UVAtlasComputeIMTFromTexture(
    const XMFLOAT3* positions,
    const XMFLOAT2* texcoords,
    size_t nVerts,
    const void* indices, DXGI_FORMAT indexFormat, size_t nFaces,
    const float* pTexture,             // 纹理数据（每纹素 4 floats）
    size_t width, size_t height,
    DWORD options,                     // UVATLAS_IMT_WRAP_U/V/UV
    std::function<HRESULT(float)> statusCallBack,
    float* pIMTArray
);

// 从自定义回调信号计算 IMT
HRESULT UVAtlasComputeIMTFromSignal(
    const XMFLOAT3* positions,
    const XMFLOAT2* texcoords,
    size_t nVerts,
    const void* indices, DXGI_FORMAT indexFormat, size_t nFaces,
    size_t signalDimension,
    float maxUVDistance,
    std::function<HRESULT(const XMFLOAT2*, size_t, size_t, void*, float*)> signalCallback,
    void* userData,
    std::function<HRESULT(float)> statusCallBack,
    float* pIMTArray
);
```

#### 4. 高级引擎接口

```cpp
// 创建引擎实例
IIsochartEngine* engine = IIsochartEngine::CreateIsochartEngine();

// 初始化
engine->Initialize(
    pVertexArray, nVerts, vertexStride, indexFormat,
    pFaceIndexArray, nFaces, pIMTArray,
    pAdjacency, pSplitHint, dwOptions
);

// 设置进度回调
engine->SetCallback(callback, frequency);

// 分区
engine->Partition(maxChartNumber, stretch, chartNumberOut, maxStretchOut, pFaceAttributeIDOut);

// 导出分区结果
engine->ExportPartitionResult(
    &vVertexArrayOut, &vFaceIndexArrayOut,
    &vVertexRemapArrayOut, &vAttributeIDOut, &vAdjacencyOut
);

// 打包
engine->InitializePacking(&vVertexBuffer, nVerts, &vFaceIndexBuffer, nFaces, pAdjacency);
engine->Pack(width, height, gutter, pOrigIndexBuffer,
    &vVertexArrayOut, &vFaceIndexArrayOut, &vVertexRemapArrayOut, pAttributeID);

// 释放
IIsochartEngine::ReleaseIsochartEngine(engine);
```

### 核心 API：DirectXMesh（第三方库）

```cpp
#include "DirectXMesh.h"

// 邻接关系计算
DirectX::GenerateAdjacencyAndPointReps(
    indices, nFaces, positions, nVerts, epsilon,
    pointRep, adjacency
);

// 法线计算
DirectX::ComputeNormals(indices, nFaces, positions, nVerts, flags, normals);

// 切线/副切线计算
DirectX::ComputeTangentFrame(indices, nFaces, positions, normals, texcoords, nVerts, tangents, bitangents);

// 网格验证和清理
DirectX::Validate(indices, nFaces, nVerts, adjacency, flags, msgs);
DirectX::Clean(indices, nFaces, nVerts, adjacency, attributes, dupVerts, breakBowties);

// 面排序优化（提高顶点缓存命中率）
DirectX::OptimizeFaces(indices, nFaces, adjacency, faceRemap);

// 顶点重排序（按使用顺序）
DirectX::OptimizeVertices(indices, nFaces, nVerts, vertexRemap);
```

### Geodesic Distance 计算

UVAtlas 内部使用两种测地线距离算法：

```cpp
// 精确模式（窗口传播算法，适用于小面数网格）
CExactOneToAll exactGeo;
exactGeo.SetSrcVertexIdx(srcIndex);
exactGeo.Run();

// 近似模式（快速但精度稍低）
CApproximateOneToAll approxGeo;
approxGeo.SetSrcVertexIdx(srcIndex);
approxGeo.Run();
```

选择策略由 `ISOCHARTOPTION` 控制：
- `_OPTION_ISOCHART_DEFAULT`：面数低于阈值时用精确模式，否则用快速模式
- `_OPTION_ISOCHART_GEODESIC_FAST`：始终用快速模式
- `_OPTION_ISOCHART_GEODESIC_QUALITY`：始终用精确模式

## Demo 示例

### 最小 UV Atlas 生成示例

```cpp
// UVAtlasDemo.h
#pragma once
#include "CoreMinimal.h"

class FUVAtlasDemo
{
public:
    static void GenerateUVAtlas(
        const TArray<FVector>& Positions,
        const TArray<uint32>& Indices,
        uint32 TextureWidth,
        uint32 TextureHeight,
        TArray<FVector2D>& OutUVs);
};
```

```cpp
// UVAtlasDemo.cpp
#include "UVAtlasDemo.h"
#include "UVAtlas.h"
#include "DirectXMesh.h"

using namespace DirectX;

void FUVAtlasDemo::GenerateUVAtlas(
    const TArray<FVector>& Positions,
    const TArray<uint32>& Indices,
    uint32 TextureWidth,
    uint32 TextureHeight,
    TArray<FVector2D>& OutUVs)
{
    const size_t nVerts = Positions.Num();
    const size_t nFaces = Indices.Num() / 3;

    // 转换顶点坐标为 XMFLOAT3
    TArray<XMFLOAT3> DXPositions;
    DXPositions.SetNum(nVerts);
    for (int32 i = 0; i < Positions.Num(); ++i)
    {
        DXPositions[i] = XMFLOAT3(
            static_cast<float>(Positions[i].X),
            static_cast<float>(Positions[i].Y),
            static_cast<float>(Positions[i].Z));
    }

    // 计算邻接关系
    TArray<uint32> Adjacency;
    Adjacency.SetNum(nFaces * 3);
    DirectX::GenerateAdjacencyAndPointReps(
        Indices.GetData(), nFaces,
        DXPositions.GetData(), nVerts,
        0.0f, nullptr, Adjacency.GetData());

    // 执行 UV Atlas 创建
    std::vector<UVAtlasVertex> OutVertexBuffer;
    std::vector<uint8_t> OutIndexBuffer;
    std::vector<uint32_t> FacePartitioning;

    HRESULT hr = DirectX::UVAtlasCreate(
        DXPositions.GetData(), nVerts,
        Indices.GetData(), DXGI_FORMAT_R32_UINT, nFaces,
        0,                    // maxChartNumber: 0 = 按拉伸度约束
        0.5f,                 // maxStretch: 最大拉伸度
        TextureWidth, TextureHeight,
        2.0f,                 // gutter: 图表间距（纹素）
        Adjacency.GetData(),
        nullptr,              // falseEdgeAdjacency
        nullptr,              // pIMTArray
        nullptr,              // callback
        0.0001f,
        UVATLAS_DEFAULT,
        OutVertexBuffer,
        OutIndexBuffer,
        &FacePartitioning
    );

    if (SUCCEEDED(hr))
    {
        // 提取 UV 坐标
        OutUVs.SetNum(OutVertexBuffer.size());
        for (size_t i = 0; i < OutVertexBuffer.size(); ++i)
        {
            OutUVs[i] = FVector2D(
                OutVertexBuffer[i].uv.x,
                OutVertexBuffer[i].uv.y);
        }
    }
}
```

## 模块依赖

`ProxyLODMeshReduction` 模块的依赖关系：

| 模块 | 用途 |
|---|---|
| `DirectXMesh` | 第三方网格处理库（邻接计算、法线、切线、网格优化） |
| `UVAtlas` | 第三方 UV 图集算法库（图表分区、打包、IMT 计算） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的警告 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式说明符与参数类型不匹配的问题 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移到 UE_LOGF 新接口 |
| 2025-10-30 | `a0e12af6` | Ran UnrealCodeFixup on Engine to change all ~Type() {} to instead be ~Type() = default | 批量将析构函数实现改为 = default |
| 2025-09-15 | `8bdc434e` | Workaround to prevent crash in UVAtlas | 修复 UVAtlas 中的崩溃问题 |

### 维护评价

- **创建时间**：2024 年 1 月，从 ue5-main 分支的现有代码迁移而来，实际算法代码更早
- **维护状态**：定期收到编译器警告修复和代码规范化更新，2025-09 有关键崩溃修复。近期更新多为全局代码质量维护而非功能增强
- **平台限制**：仅支持 Win64
- **实验性声明**：IsBetaVersion=true 且 EnabledByDefault=false，官方标记为实验性
- **已知限制**：UVAtlas 是微软 DirectXTK 的第三方集成，升级受限于上游版本；是纯 C++ 库无蓝图接口
- **推荐**：⚠️ 谨慎使用。该插件标记为实验性，不建议在生产环境依赖。适合作为 Proxy LOD 生成流水线的内部组件，但需关注上游 UVAtlas/DirectXMesh 的兼容性。如果你需要独立的 UV Atlas 功能，建议直接集成 UVAtlas 库而非依赖此插件。

## 相关链接

- [源码（插件根目录）](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/ProxyLODPlugin)
- [Microsoft UVAtlas 文档](https://github.com/microsoft/DirectXMesh/wiki/UVAtlas)
- [Microsoft DirectXMesh 文档](https://github.com/microsoft/DirectXMesh/wiki)