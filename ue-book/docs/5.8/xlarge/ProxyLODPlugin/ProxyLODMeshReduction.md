# Proxy LOD Plugin

> A plugin to generate Proxy LOD systems.

| 属性 | 值 |
|---|---|
| 中文名 | 代理LOD插件 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ProxyLODMeshReduction` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-30 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/ProxyLODPlugin) | |

## 用途

ProxyLODPlugin 是一个**基于体素化的代理网格 LOD 生成系统**，用于将高面数几何体自动简化为低面数代理网格，同时保留视觉外观。

其核心工作流程如下：
1. **体素化**：将源高面数网格通过 OpenVDB 转换为有符号距离场（SDF）
2. **等值面提取**：从 SDF 中提取等值面，生成初始低面数网格
3. **网格简化**：使用基于二次误差度量（Quadric Error Metric）的边折叠算法进一步简化
4. **UV 展开**：使用 DirectX 的 Iso-Charts 算法为简化网格生成新的 UV
5. **材质烘焙**：通过光线投射建立简化网格与源网格之间的对应关系，将材质属性（漫反射、法线、金属度、粗糙度等）烘焙到新的纹理图集中

与 UE 内置的 Simplygon 或 Nanite 不同，ProxyLOD 专注于**远距离场景**的代理几何生成，特别适合建筑群、城市环境等需要远处使用极低面数代理网格的场景。它通过封闭门窗等小孔洞来移除内部几何，从而显著降低面数。

## 使用场景

- 你在开发大型开放世界游戏，需要为远处建筑生成极简代理网格 → 用 ProxyLODPlugin
- 你有一组高面数建筑模型，需要自动生成带正确材质的低面数 LOD → 用 ProxyLODPlugin
- 你需要对多个网格进行体素化 CSG 布尔运算（并集、差集、交集） → 用 `IVoxelBasedCSG`
- 你需要为已有网格生成高质量 UV 展开 → 用 `IProxyLODParameterization`
- 你需要生成基于体素的 SDF 距离场用于距离查询 → 用 `IProxyLODVolume`

## 蓝图用法

此插件为纯 C++ 编辑器模块，不暴露蓝图接口（`UFUNCTION(BlueprintCallable)` 和 `UPROPERTY(BlueprintReadWrite)`）。所有功能通过 C++ API 调用。

## C++ 用法

### 头文件引入

```cpp
#include "IProxyLODPlugin.h"
#include "ProxyLODVolume.h"
#include "ProxyLODParameterization.h"
```

### 基本用法 — SDF 体素化

从源网格生成有符号距离场（SDF），并提取等值面为低面数网格。

```cpp
#include "ProxyLODVolume.h"
#include "MeshDescription.h"

// 假设有多个源网格
TArray<FMeshMergeData> Geometry;
// ... 填充 Geometry 数组

// 1. 从网格数组创建 SDF 体素体积
TUniquePtr<IProxyLODVolume> Volume = 
    IProxyLODVolume::CreateSDFVolumeFromMeshArray(Geometry, /*Step=*/ 0.05f);

// 2. 关闭小孔洞（如门窗），使其封闭
Volume->CloseGaps(/*GapRadius=*/ 50.0, /*MaxDilations=*/ 3);

// 3. 查询某点到表面的距离
float Distance = Volume->QueryDistance(FVector(100, 200, 300));

// 4. 将 SDF 转换回网格
FMeshDescription ResultMesh;
Volume->ConvertToRawMesh(ResultMesh);

// 5. 获取体素尺寸和边界框
double VoxelSize = Volume->GetVoxelSize();
IProxyLODVolume::FVector3i BBoxSize = Volume->GetBBoxSize();
```

### 基本用法 — CSG 布尔运算

基于体素化实现网格的并集、差集和交集运算。

```cpp
#include "ProxyLODVolume.h"

// 创建 CSG 工具
TUniquePtr<IVoxelBasedCSG> CSGTool = 
    IVoxelBasedCSG::CreateCSGTool(/*VoxelSize=*/ 1.0f);

// 准备网格数据
IVoxelBasedCSG::FPlacedMesh MeshA(&MeshDescriptionA, TransformA);
IVoxelBasedCSG::FPlacedMesh MeshB(&MeshDescriptionB, TransformB);

FMeshDescription ResultMesh;
FVector AverageTranslation;

// 并集运算
CSGTool->ComputeUnion(MeshA, MeshB, ResultMesh, 
    /*Adaptivity=*/ 0.1, /*IsoSurface=*/ 0.0);

// 差集运算：从 A 中减去 B
CSGTool->ComputeDifference(MeshA, MeshB, ResultMesh,
    /*Adaptivity=*/ 0.1, /*IsoSurface=*/ 0.0);

// 交集运算
CSGTool->ComputeIntersection(MeshA, MeshB, ResultMesh,
    /*Adaptivity=*/ 0.1, /*IsoSurface=*/ 0.0);

// 批量并集
TArray<IVoxelBasedCSG::FPlacedMesh> MeshArray;
MeshArray.Add(MeshA);
MeshArray.Add(MeshB);
CSGTool->ComputeUnion(MeshArray, ResultMesh);
```

### 基本用法 — UV 参数化

为网格生成基于 Iso-Charts 的 UV 展开。

```cpp
#include "ProxyLODParameterization.h"

// 创建参数化工具
TUniquePtr<IProxyLODParameterization> ParamTool = 
    IProxyLODParameterization::CreateTool();

// 对 FMeshDescription 进行 UV 参数化
FMeshDescription Mesh;
bool bSuccess = ParamTool->ParameterizeMeshDescription(
    Mesh,
    /*Width=*/ 1024,            // 纹理图集宽度（像素）
    /*Height=*/ 1024,           // 纹理图集高度（像素）
    /*GutterSpace=*/ 2.0f,      // 纹理间距
    /*Stretch=*/ 0.5f,          // 最大拉伸量 (0=无拉伸, 1=任意)
    /*ChartNum=*/ 0,            // 最大图表数 (0=仅按拉伸控制)
    /*bUseNormals=*/ false,     // 是否使用法线计算度量张量
    /*bRecomputeTangentSpace=*/ true, // 是否重计算切线空间
    /*bPrintDebugMessages=*/ false
);
```

### 进阶用法 — 网格内部数据类型

ProxyLOD 内部使用多种网格格式，理解它们有助于深入使用该系统。

```cpp
#include "ProxyLODMeshTypes.h"

// FMeshDescriptionArrayAdapter: 将多个 FMeshDescription 视为单一网格
// 用于批量体素化多个网格
TArray<FMeshMergeData> MergeData;
// ... 填充
openvdb::math::Transform::Ptr Transform = openvdb::math::Transform::createLinearTransform(voxelSize);
FMeshDescriptionArrayAdapter MeshAdapter(MergeData, Transform);

// 访问多边形数量和点数量
size_t NumPolys = MeshAdapter.polygonCount();
size_t NumPoints = MeshAdapter.pointCount();

// 获取单个三角形的原始数据
int32 MeshIdx, InstanceIdx, LocalFaceNumber;
auto RawPoly = MeshAdapter.GetRawPoly(FaceNumber, MeshIdx, InstanceIdx, LocalFaceNumber);

// FVertexDataMesh: 用于 UV 生成和切线空间计算
FVertexDataMesh VertexMesh;
// 支持: Indices, Points, Normal, Tangent, BiTangent, UVs, FaceColors

// FAOSMesh: 用于网格简化（Array-of-Structs 格式）
FAOSMesh AOSMesh;
// 内部使用 FPositionNormalVertex（位置 + 法线 + 材质索引）
```

## Demo 示例

以下展示完整的 ProxyLOD 管线：从源网格生成代理 LOD 网格。

### ProxyLODExample.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "MeshDescription.h"

struct FMeshMergeData;

class FProxyLODExample
{
public:
    /** 从源网格生成代理 LOD 网格 */
    static bool GenerateProxyLOD(
        const TArray<FMeshMergeData>& SourceGeometry,
        FMeshDescription& OutProxyMesh,
        int32 TextureAtlasSize = 1024,
        float VoxelSize = 0.05f
    );
};
```

### ProxyLODExample.cpp

```cpp
#include "ProxyLODExample.h"
#include "ProxyLODVolume.h"
#include "ProxyLODParameterization.h"

bool FProxyLODExample::GenerateProxyLOD(
    const TArray<FMeshMergeData>& SourceGeometry,
    FMeshDescription& OutProxyMesh,
    int32 TextureAtlasSize,
    float VoxelSize)
{
    // 步骤 1: 创建 SDF 体积
    TUniquePtr<IProxyLODVolume> Volume =
        IProxyLODVolume::CreateSDFVolumeFromMeshArray(SourceGeometry, VoxelSize);

    if (!Volume)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create SDF volume"));
        return false;
    }

    // 步骤 2: 关闭小孔洞以移除内部几何
    double GapRadius = 3.0 * Volume->GetVoxelSize();
    Volume->CloseGaps(GapRadius, /*MaxDilations=*/ 3);

    // 步骤 3: 提取代理网格
    Volume->ConvertToRawMesh(OutProxyMesh);

    // 步骤 4: 生成 UV
    TUniquePtr<IProxyLODParameterization> ParamTool =
        IProxyLODParameterization::CreateTool();

    bool bUVSuccess = ParamTool->ParameterizeMeshDescription(
        OutProxyMesh,
        TextureAtlasSize,
        TextureAtlasSize,
        /*GutterSpace=*/ 2.0f,
        /*Stretch=*/ 0.5f,
        /*ChartNum=*/ 0,
        /*bUseNormals=*/ false,
        /*bRecomputeTangentSpace=*/ true,
        /*bPrintDebugMessages=*/ false
    );

    if (!bUVSuccess)
    {
        UE_LOG(LogTemp, Warning, TEXT("UV generation failed, using default UVs"));
    }

    UE_LOG(LogTemp, Log, TEXT("ProxyLOD generated: %d triangles"),
        OutProxyMesh.Triangles().Num());

    return true;
}
```

## 模块依赖

### 主模块依赖

| 模块 | 用途 |
|---|---|
| `OpenVDB` | 体素化、SDF 距离场生成与等值面提取的核心依赖 |

### 第三方库依赖

| 库 | 用途 |
|---|---|
| `DirectXMesh` | 网格法线/切线空间计算、网格邻接信息生成 |
| `UVAtlas` | 基于 Iso-Charts 的 UV 展开参数化 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点的编译警告 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复格式化字符串中 32/64 位类型不匹配的问题 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 日志宏 |
| 2025-10-30 | `a0e12af6` | Ran UnrealCodeFixup on Engine to change all ~Type() {} to instead be ~Type() = default | 批量将空析构函数体替换为 = default |
| 2025-09-15 | `8bdc434e` | Workaround to prevent crash in UVAtlas | 修复 UVAtlas 中可能导致崩溃的问题 |

### 维护评价

**⚠️ 实验性且维护不活跃的插件**

- **创建时间**：2024 年 1 月，从 ue5-main 分支迁移而来（原始 CL 编号 31023870 暗示更早的内部开发历史）
- **更新频率**：2025-2026 年间仅有编译修复和代码清理，**无功能性更新**
- **实验性状态**：`.uplugin` 标记为 `IsBetaVersion=true`，默认未启用（`EnabledByDefault=false`），仅限 Win64 平台
- **维护趋势**：所有近期 commit 均为代码质量改进（浮点警告、格式化字符串、日志宏迁移、析构函数现代化），无新功能开发
- **已知限制**：
  - 仅支持 Win64 平台
  - 依赖 OpenVDB 和 Intel TBB，增加构建复杂度
  - 2025-09 的 UVAtlas 崩溃修复说明第三方库存在稳定性问题
- **推荐**：适合需要体素化代理 LOD 或 CSG 布尔运算的高级用例。由于是实验性插件，不建议在生产环境中依赖。建议关注 UE 官方是否有后续替代方案（如 Nanite 用于远距离渲染）。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/ProxyLODPlugin)
- [官方文档]() （无官方文档链接）