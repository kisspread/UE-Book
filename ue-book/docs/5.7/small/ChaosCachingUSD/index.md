# Chaos Caching USD

> Adds support for using USD files for caching Chaos flesh simulations

| 属性 | 值 |
|---|---|
| 中文名 | Chaos缓存USD |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ChaosCachingUSD` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-09 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosCachingUSD) | |

## 用途

Chaos Caching USD 是一个实验性编辑器插件，提供了一套 C++ API 和自定义 USD 模式（Schema），用于将 Chaos 布料/肉体（Flesh）模拟的缓存结果导出为 USD 文件格式。它利用 USD 的 **Value Clips（值剪辑）** 机制，将随时间变化的顶点数据分割到多个较小的 .usd 文件中，从而提高大场景数据传输和协作的效率。

该插件解决了以下问题：
- 将实时模拟的 Chaos 缓存（如布料顶点位置、四面体网格变形）持久化到 USD 标准格式。
- 支持四面体网格（TetMesh）的自定义几何体模式，保留完整的拓扑和形变信息。
- 利用 USD Value Clips 实现稀疏存储和渐进式加载，便于在 DCC 工具（如 Maya、Houdini）中回放或进一步处理。

## 使用场景

- 你正在制作一个需要导出布料/肉体模拟回放给动画师或特效师的项目 → 使用此插件输出 USD 缓存。
- 你需要将 Chaos 仿真结果集成到基于 USD 的管线中，例如在内部工具或第三方软件中查看模拟效果。
- 希望将模拟数据分帧存储以节省磁盘空间并支持部分加载。

## 蓝图用法

此插件未暴露任何 `BlueprintCallable` 函数或 `BlueprintReadWrite` 属性。所有功能均为 C++ API，需要编写 C++ 代码或通过蓝图函数库包装后才能使用。

## C++ 用法

### 头文件引入

```cpp
#include "ChaosCachingUSD/Operations.h"
#include "ChaosCachingUSD/UEUsdGeomTetMesh.h" // 若需使用四面体网格模式
```

### 基本用法：创建并保存 USD 舞台

以下示例展示了如何使用 `Operations.h` 中的函数新建一个 USD 舞台，写入静态拓扑数据，并保存为值剪辑格式。

```cpp
// 来源：Engine/Plugins/Experimental/ChaosCachingUSD/Source/ChaosCachingUSD/Public/ChaosCachingUSD/Operations.h
// 示例：创建一个值剪辑场景

#include "ChaosCachingUSD/Operations.h"
#include "USDIncludesStart.h"
#include "pxr/usd/usdGeom/mesh.h"
#include "USDIncludesEnd.h"

// 假设有一个 UE::FUsdStage 对象
UE::FUsdStage RootStage;
FString RootStageName = TEXT("/Game/MyCache/Simulation.usd");
FString TopologyName, TimeVaryingTemplate;
UE::ChaosCachingUSD::GenerateValueClipStageNames(RootStageName, TopologyName, TimeVaryingTemplate);

// 新建父舞台和拓扑舞台
UE::ChaosCachingUSD::NewValueClipsStages(
    RootStageName,
    TopologyName,
    RootStage,
    TopologyStage);

// 在拓扑舞台上写入不随时间变化的几何数据（如顶点位置、四面体拓扑）
// ... 此处填充 pxr::UsdGeomMesh 或自定义 UEUsdGeomTetMesh

// 保存舞台，并设置帧范围
UE::ChaosCachingUSD::SaveStage(RootStage, 1.0, 100.0);
UE::ChaosCachingUSD::SaveStage(TopologyStage, 1.0, 100.0);

// 关闭舞台
UE::ChaosCachingUSD::CloseStage(RootStage);
UE::ChaosCachingUSD::CloseStage(TopologyStage);
```

### 进阶用法：写入动态帧数据（值剪辑）

将每帧变化的顶点位置写入独立的时间片文件：

```cpp
// 来源：同上 Operations.h

double Time = 1.0;
FString FrameStageName;
UE::FUsdStage FrameStage;
UE::ChaosCachingUSD::NewValueClipsFrameStage(
    TimeVaryingTemplate,
    Time,
    FrameStageName,
    FrameStage);

// 获取当前帧的顶点位置数组（例如从 Chaos 缓存读取）
pxr::VtArray<pxr::GfVec3f> Positions = { ... };

// 写入到帧舞台的网格（需先定义 UsdGeomMesh 或 UEUsdGeomTetMesh）
pxr::UsdGeomMesh FrameMesh = pxr::UsdGeomMesh::Define(FrameStage.GetPrim(), pxr::SdfPath(TEXT("/Mesh")));
FrameMesh.CreatePointsAttr().Set(Positions);

// 保存并关闭帧舞台
UE::ChaosCachingUSD::SaveStage(FrameStage, Time, Time);
UE::ChaosCachingUSD::CloseStage(FrameStage);
```

### 使用自定义四面体模式（UEUsdGeomTetMesh）

此插件定义了 `UEUsdGeomTetMesh` 模式，用于描述 Chaos 四面体网格的顶点和拓扑。

```cpp
// 来源：Engine/Plugins/Experimental/ChaosCachingUSD/Source/ChaosCachingUSD/Private/ChaosCachingUSD/UEUsdGeomTetMesh.h

#include "ChaosCachingUSD/UEUsdGeomTetMesh.h"

// 在舞台上定义四面体网格
pxr::UsdStagePtr Stage = ...;
pxr::SdfPath TetMeshPath(TEXT("/Flesh/TetMesh"));
UEUsdGeomTetMesh TetMesh = UEUsdGeomTetMesh::Define(Stage, TetMeshPath);

// 设置顶点位置
pxr::VtArray<pxr::GfVec3f> Points = { ... };
TetMesh.CreatePointsAttr().Set(Points);

// 设置四面体索引（每个四面体由4个顶点索引组成）
pxr::VtArray<pxr::GfVec4i> TetIndices = { ... };
TetMesh.CreateTetVertexIndicesAttr().Set(TetIndices);

// 设置四面体朝向（可选）
pxr::TfToken Orientation(TEXT("rightHanded")); // "rightHanded" 或 "leftHanded"
TetMesh.CreateTetOrientationAttr().Set(Orientation);
```

## Demo 示例

以下是一个最小但完整的 C++ 示例，演示创建一个包含单帧四面体网格的 USD 值剪辑场景。

**BarabaraFleshExporter.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FBarabaraFleshExporterImpl
{
public:
    static bool ExportSingleFrame(
        const FString& OutputDir,
        const TArray<FVector>& Points,
        const TArray<FIntVector4>& TetIndices,
        int32 FrameNumber);
};
```

**BarabaraFleshExporter.cpp**
```cpp
#include "BarabaraFleshExporter.h"
#include "ChaosCachingUSD/Operations.h"
#include "ChaosCachingUSD/UEUsdGeomTetMesh.h"

#include "USDIncludesStart.h"
#include "pxr/usd/usd/stage.h"
#include "pxr/usd/usdGeom/tokens.h"
#include "USDIncludesEnd.h"

bool FBarabaraFleshExporterImpl::ExportSingleFrame(
    const FString& OutputDir,
    const TArray<FVector>& Points,
    const TArray<FIntVector4>& TetIndices,
    int32 FrameNumber)
{
    // 1. 准备舞台名（使用值剪辑模板）
    FString RootStageName = OutputDir / TEXT("FleshCache.usd");
    FString TopologyName, TimeVaryingTemplate;
    UE::ChaosCachingUSD::GenerateValueClipStageNames(RootStageName, TopologyName, TimeVaryingTemplate);

    // 2. 创建父舞台和拓扑舞台
    UE::FUsdStage ParentStage, TopologyStage;
    if (!UE::ChaosCachingUSD::NewValueClipsStages(
            RootStageName, TopologyName, ParentStage, TopologyStage))
    {
        return false;
    }

    // 3. 定义四面体网格拓扑（仅在拓扑舞台上写入一次）
    pxr::UsdStageRefPtr TopologyUsdStage = TopologyStage.Get(); // 从 UE::FUsdStage 获取 pxr 句柄
    UEUsdGeomTetMesh TetMesh = UEUsdGeomTetMesh::Define(TopologyUsdStage, pxr::SdfPath(TEXT("/Flesh/TetMesh")));
    
    // 写入顶点（此处可只写第一帧的静态顶点，若变化则放帧舞台）
    pxr::VtArray<pxr::GfVec3f> UsdPoints;
    for (const auto& P : Points)
    {
        UsdPoints.push_back(pxr::GfVec3f(P.X, P.Y, P.Z));
    }
    TetMesh.CreatePointsAttr().Set(UsdPoints);
    
    pxr::VtArray<pxr::GfVec4i> UsdTets;
    for (const auto& T : TetIndices)
    {
        UsdTets.push_back(pxr::GfVec4i(T.X, T.Y, T.Z, T.W));
    }
    TetMesh.CreateTetVertexIndicesAttr().Set(UsdTets);
    
    // 4. 创建帧舞台（包含该帧的变形数据，若顶点变化则写入）
    double Time = static_cast<double>(FrameNumber);
    FString FrameStageName;
    UE::FUsdStage FrameStage;
    if (!UE::ChaosCachingUSD::NewValueClipsFrameStage(
            TimeVaryingTemplate, Time, FrameStageName, FrameStage))
    {
        UE::ChaosCachingUSD::CloseStage(TopologyStage);
        UE::ChaosCachingUSD::CloseStage(ParentStage);
        return false;
    }

    // 写入该帧的顶点位置（若与拓扑不同）
    // 注：此处省略真实的帧数据；实际应从外部传入动态数据
    // FrameStage 中可定义相同的网格 Prim 并写入 points 属性

    // 5. 保存并关闭
    bool bSuccess = UE::ChaosCachingUSD::SaveStage(ParentStage, Time, Time);
    bSuccess &= UE::ChaosCachingUSD::SaveStage(TopologyStage, Time, Time);
    bSuccess &= UE::ChaosCachingUSD::SaveStage(FrameStage, Time, Time);

    UE::ChaosCachingUSD::CloseStage(FrameStage);
    UE::ChaosCachingUSD::CloseStage(TopologyStage);
    UE::ChaosCachingUSD::CloseStage(ParentStage);

    return bSuccess;
}
```

## 模块依赖

要使用此插件，你的模块的 `Build.cs` 需要添加以下依赖（省略常见标准模块）：

| 模块 | 用途 |
|---|---|
| `ChaosCaching` | 提供 Chaos 缓存数据结构（如帧数据） |
| `USDImporter` | 提供 USD SDK 集成、舞台包装、值剪辑工具 |
| `UnrealUSDWrapper` | 提供 UE 对 USD 类型（如 `UE::FUsdStage`）的封装（通常由 USDImporter 传递） |

注意：插件本身为 Editor 模块，因此也需要间接依赖 `UnrealEd` 等编辑器基础模块（已属常见依赖，不再列出）。

## 维护状态

### 近期更新

- 2025-10-22 a1039b21 USD: Disabled UE allocator in USD for Windows.
- 2025-10-17 be609b71 [Backout] - CL47041219
- 2025-10-17 7ab79237 USD: Disabled UE allocator in USD for Windows.
- 2025-09-15 d7ab5176 For merged module only enable python if it's set to be compiled by the target and in editor.
- 2025-09-09 4f303d57 Disabled UE allocators in OpenUSD for Linux.

### 维护评价

- **创建时间**：2025-09-09（约 1 个月前）
- **更新频率**：近 1 个月内有多次修复性提交，主要专注于编译器兼容性和 UE5 的分配器集成。
- **活跃度**：作为实验性插件，仍处于早期开发阶段，提交主要集中在基础设施修复，尚未有大规模功能更新。
- **已知限制**：插件被标记为实验性，API 可能随时变更；仅支持 Win64 目标平台；需要开启 USD Importer 插件；当前未提供任何蓝图节点，仅限 C++ 使用。
- **推荐使用**：适合需要将 Chaos 缓存以 USD 格式导出的高级用户，但应做好 API 变动的准备。对于正式生产管线，建议等待其脱离实验期。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosCachingUSD)
- [USDImporter 插件文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/usd-importer-for-unreal-engine)（暂无独立官方文档）