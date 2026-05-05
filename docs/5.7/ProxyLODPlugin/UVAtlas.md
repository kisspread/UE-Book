# Proxy LOD Plugin (Experimental)

> A plugin to generate Proxy LOD systems.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ProxyLODMeshReduction` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2017-12-13 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/ProxyLODPlugin) | |

## 用途

ProxyLODPlugin 是一个用于生成 **代理 LOD（Proxy LOD）** 网格的编辑器工具。它解决的核心问题是：当场景中有大量静态网格体时，如何将多个复杂网格合并简化为一个低细节的代理网格，从而大幅减少绘制调用（Draw Calls）和提升渲染性能。

该插件的工作流程是：
1. **网格合并**：将多个输入网格合并为单一网格
2. **UV 图表生成**：使用 Isochart 算法将合并后的网格分割为 UV 图表（Charts），并生成最优的 UV 布局
3. **UV 打包**：将所有 UV 图表打包到指定大小的纹理空间中
4. **网格简化**：使用渐进网格（Progressive Mesh）算法简化几何体

插件集成了两个微软的第三方库：
- **UVAtlas**：用于 UV 图表生成、测地线距离计算和 UV 打包
- **DirectXMesh**：用于网格拓扑处理、法线计算和网格优化

> ⚠️ **注意**：此插件标记为实验性（IsBetaVersion=true），且默认未启用（EnabledByDefault=false）。仅支持 Win64 平台。

## 使用场景

- 你在做开放世界游戏，需要为远处的建筑群生成 HLOD 代理网格 → 用 ProxyLODPlugin
- 你需要将多个静态网格合并为一个低面数代理体以减少 Draw Calls → 用 ProxyLODPlugin
- 你需要为大型场景生成简化的碰撞体 → 用 ProxyLODPlugin
- 你需要在打包前自动为 LOD 生成优化的 UV 布局 → 用 ProxyLODPlugin

## 蓝图用法

此插件为 Editor 模块，主要通过编辑器 UI（如 HLOD 系统）间接使用，不直接暴露蓝图节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| 无直接蓝图暴露 | 此插件通过编辑器工具链集成，不提供 BlueprintCallable 函数 | — |

### 使用示例（编辑器操作）

1. 在项目设置中启用 `ProxyLODPlugin`
2. 通过 World Partition / HLOD 系统配置使用 Proxy LOD 生成器
3. 在 HLOD 设置中选择 Proxy LOD 作为简化方法

## C++ 用法

### 头文件引入

```cpp
#include "ProxyLODMeshReduction.h"
```

### 基本用法

该插件的核心功能通过 `ProxyLODMeshReduction` 模块提供，主要涉及网格简化和 UV 图表生成。以下展示了底层 UVAtlas 库的典型用法：

```cpp
// 来源: Engine/Plugins/Editor/ProxyLODPlugin/Source/ThirdParty/UVAtlasCode/UVAtlas/inc/UVAtlas.h
// 使用 UVAtlas API 进行 UV 图表生成和打包

#include "UVAtlas.h"

// 准备输入数据
const void* pVertexArray = /* 顶点数据 */;
size_t VertexCount = /* 顶点数量 */;
size_t VertexStride = /* 顶点步长 */;
DXGI_FORMAT IndexFormat = DXGI_FORMAT_R32_UINT;
const void* pFaceIndexArray = /* 索引数据 */;
size_t FaceCount = /* 面数量 */;
const uint32_t* pAdjacency = /* 邻接数据 */;

// 输出容器
std::vector<DirectX::UVAtlasVertex> vertexArrayOut;
std::vector<uint8_t> faceIndexArrayOut;
std::vector<uint32_t> vertexRemapArrayOut;
size_t chartNumberOut = 0;
float maxStretchOut = 0.0f;

// 一次性执行图表生成和打包
HRESULT hr = DirectX::UVAtlasCreate(
    pVertexArray,
    VertexCount,
    VertexStride,
    IndexFormat,
    pFaceIndexArray,
    FaceCount,
    0,              // maxChartNumber (0 = 基于 stretch 参数化)
    0.5f,           // maxStretch
    512,            // width
    512,            // height
    2.0f,           // gutter (图表间距)
    pAdjacency,
    nullptr,        // falseEdgeAdjacency
    nullptr,        // pIMTArray
    nullptr,        // statusCallback
    0.01f,          // callbackFrequency
    DirectX::UVATLAS_DEFAULT,
    &vertexArrayOut,
    &faceIndexArrayOut,
    &vertexRemapArrayOut,
    &chartNumberOut,
    &maxStretchOut
);
```

### 进阶用法

分步执行图表生成和打包，以便在中间步骤进行自定义处理：

```cpp
// 来源: Engine/Plugins/Editor/ProxyLODPlugin/Source/ThirdParty/UVAtlasCode/UVAtlas/inc/UVAtlas.h

// 步骤 1: 仅执行图表分区
std::vector<DirectX::UVAtlasVertex> vertexArrayOut;
std::vector<uint8_t> faceIndexArrayOut;
std::vector<uint32_t> vertexRemapArrayOut;
std::vector<uint32_t> attributeIDOut;
std::vector<uint32_t> adjacencyOut;
size_t chartNumberOut = 0;
float maxStretchOut = 0.0f;

HRESULT hr = DirectX::UVAtlasPartition(
    pVertexArray,
    VertexCount,
    VertexStride,
    IndexFormat,
    pFaceIndexArray,
    FaceCount,
    nullptr,        // pIMTArray
    10,             // maxChartNumber
    0.5f,           // maxStretch
    pAdjacency,
    &vertexArrayOut,
    &faceIndexArrayOut,
    &vertexRemapArrayOut,
    &attributeIDOut,
    &adjacencyOut,
    &chartNumberOut,
    &maxStretchOut,
    nullptr,        // statusCallback
    0.01f           // callbackFrequency
);

// 步骤 2: 打包 UV 图表
hr = DirectX::UVAtlasPack(
    &vertexArrayOut,
    512,            // width
    512,            // height
    2.0f,           // gutter
    adjacencyOut,
    nullptr,        // statusCallback
    0.01f           // callbackFrequency
);

// 步骤 3: 应用结果到原始网格
hr = DirectX::UVAtlasApplyRemap(
    pVertexArray,
    VertexStride,
    VertexCount,
    faceIndexArrayOut.size() / (IndexFormat == DXGI_FORMAT_R16_UINT ? 2 : 4),
    IndexFormat,
    vertexRemapArrayOut.data(),
    vertexRemapArrayOut.size(),
    &vertexArrayOut,
    &faceIndexArrayOut
);
```

## Demo 示例

### 最小示例：使用 UVAtlas 生成 UV 布局

```cpp
// ProxyLODExample.h
#pragma once

#include "CoreMinimal.h"

class FProxyLODExample
{
public:
    /** 为输入网格生成 Proxy LOD UV 布局 */
    static bool GenerateProxyLODUV(
        const TArray<FVector>& Vertices,
        const TArray<uint32>& Indices,
        int32 TextureSize,
        TArray<FVector2D>& OutUVs
    );
};
```

```cpp
// ProxyLODExample.cpp
#include "ProxyLODExample.h"
#include "UVAtlas.h"

bool FProxyLODExample::GenerateProxyLODUV(
    const TArray<FVector>& Vertices,
    const TArray<uint32>& Indices,
    int32 TextureSize,
    TArray<FVector2D>& OutUVs)
{
    // 计算邻接信息
    const size_t FaceCount = Indices.Num() / 3;
    TArray<uint32> Adjacency;
    Adjacency.SetNumUninitialized(FaceCount * 3);
    
    // 使用 DirectXMesh 计算邻接
    std::vector<uint32_t> adj(FaceCount * 3);
    HRESULT hr = DirectX::GenerateAdjacencyAndPointReps(
        reinterpret_cast<const uint16_t*>(Indices.GetData()),
        FaceCount,
        reinterpret_cast<const DirectX::XMFLOAT3*>(Vertices.GetData()),
        Vertices.Num(),
        0.001f,  // epsilon
        nullptr,
        adj.data()
    );
    
    if (FAILED(hr)) return false;
    
    // 执行 UVAtlas 生成
    std::vector<DirectX::UVAtlasVertex> uvVertices;
    std::vector<uint8_t> outIndices;
    std::vector<uint32_t> remap;
    size_t chartCount = 0;
    float maxStretch = 0.0f;
    
    hr = DirectX::UVAtlasCreate(
        Vertices.GetData(),
        Vertices.Num(),
        sizeof(FVector),
        DXGI_FORMAT_R32_UINT,
        Indices.GetData(),
        FaceCount,
        0,                  // 自动确定图表数量
        0.5f,               // 最大拉伸
        TextureSize,
        TextureSize,
        2.0f,               // gutter
        adj.data(),
        nullptr, nullptr, nullptr, 0.01f,
        DirectX::UVATLAS_DEFAULT,
        &uvVertices,
        &outIndices,
        &remap,
        &chartCount,
        &maxStretch
    );
    
    if (FAILED(hr)) return false;
    
    // 提取 UV 坐标
    OutUVs.SetNum(uvVertices.size());
    for (int32 i = 0; i < uvVertices.size(); ++i)
    {
        OutUVs[i] = FVector2D(uvVertices[i].uv.x, uvVertices[i].uv.y);
    }
    
    return true;
}
```

### Build.cs 依赖说明

```csharp
// YourModule.Build.cs
using UnrealBuildTool;

public class YourModule : ModuleRules
{
    public YourModule(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        
        PublicDependencyModuleNames.AddRange(new string[]
        {
            "Core",
            "CoreUObject",
            "Engine"
        });
        
        // 依赖 ProxyLOD 模块
        PrivateDependencyModuleNames.AddRange(new string[]
        {
            "ProxyLODMeshReduction"
        });
    }
}
```

## 模块依赖

从 Build.cs 分析，该插件包含以下模块依赖关系：

| 模块 | 用途 |
|---|---|
| `DirectXMesh` (External) | 微软 DirectX 网格几何库，提供网格拓扑处理、邻接计算、法线/切线计算、网格优化等功能 |
| `UVAtlas` (External) | 微软 UVAtlas 库，提供 UV 图表生成（Isochart 算法）、测地线距离计算、UV 打包/重打包功能 |

> 无特殊依赖（仅标准 Core/Engine/Slate 等），但依赖两个微软第三方库（DirectXMesh 和 UVAtlas），这些库已包含在插件源码中。

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2024-xx-xx | `2916cb0` | Add Windows Arm64 libs for ProxyLOD plugin | 为插件添加 Windows Arm64 平台的预编译库支持，表明 Epic 在扩展平台兼容性 |
| 2024-xx-xx | `bc63a88` | Redirect old cppcompilewarning properties to new *.CppCompileWarningSettings | 构建系统重构，更新编译警告配置方式 |
| 2024-xx-xx | `761ea07` | UnrealBuildTool: Use warning level for undefined identifier property | UBT 构建工具更新，调整未定义标识符的警告级别 |

### 维护评价

**综合评价：维护不活跃，谨慎使用**

- **创建时间**：2017 年 12 月，已存在约 8 年
- **实验性状态**：标记为 `IsBetaVersion=true`，且 `EnabledByDefault=false`，说明 Epic 从未将其视为正式功能
- **近期更新**：最近的提交主要是构建系统维护（编译警告配置、Arm64 库支持），没有功能性更新
- **平台限制**：仅支持 Win64，限制了跨平台项目的使用
- **第三方依赖**：依赖微软的 DirectXMesh 和 UVAtlas 库，这些库本身也在维护中
- **与 UE5 HLOD 的关系**：UE5 的 HLOD 系统已经内置了 Mesh Merge 和 Mesh Simplify 功能，ProxyLODPlugin 可能是早期的实验性实现

> ⚠️ **警告**：此插件标记为实验性且默认禁用，超过 6 年没有实质性功能更新。建议优先使用 UE5 内置的 HLOD 系统和 Nanite 虚拟几何体方案。如果确实需要 Proxy LOD 功能，请在 Win64 平台上充分测试后再用于生产环境。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/ProxyLODPlugin)
- [UVAtlas 官方文档](https://github.com/microsoft/DirectXMesh/wiki/UVAtlas)
- [DirectXMesh 官方文档](https://github.com/microsoft/DirectXMesh/wiki)
- [UE5 HLOD 文档](https://docs.unrealengine.com/5.0/en-US/Hierarchical-Level-of-Detail-in-Unreal-Engine/)