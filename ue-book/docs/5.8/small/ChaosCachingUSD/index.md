# Chaos Caching USD

> Adds support for using USD files for caching Chaos flesh simulations

| 属性 | 值 |
|---|---|
| 中文名 | 混沌缓存USD |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `ChaosCachingUSD` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-08-02 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosCachingUSD) | |

## 用途

该插件提供了一套完整的工具集，用于将 Chaos 物理系统（特别是 `flesh` 肌肉/软体模拟）的仿真数据（如顶点位置、速度、激活度）与 Pixar 的通用场景描述 (USD) 格式进行互操作。

其核心价值在于：
1.  **数据持久化**：将 Chaos 仿真过程中产生的逐帧数据（如网格顶点位置）保存为 USD 文件。
2.  **工作流集成**：利用 USD 的 “Value Clips” 机制高效存储和读取大量时间变化数据，便于与外部 DCC 工具（如 Houdini, Maya）交换数据。
3.  **自定义 Schema**：通过定义 `UEUsdGeomTetMesh` 这一自定义 USD Schema，能够精确描述四面体网格（TetMesh）的拓扑结构（顶点索引、朝向），这是 Chaos 物理引擎内部使用的关键数据结构。

它解决的问题是：如何标准化、高效地存储和交换高精度的物理仿真结果，以便进行后续的分析、可视化或集成到其他生产管线中。

## 使用场景

-   你需要将角色的 Chaos 肌肉/软体仿真结果导出，供下游美术师在 Houdini 中进行二次调整或渲染。
-   你需要将复杂的物理仿真序列保存为标准格式，以便进行版本管理或长期存档。
-   你需要一个批处理流程，能够生成 USD 格式的仿真缓存，然后在 Unreal Engine 的其他位置或工具中回放。
-   你正在开发一个涉及复杂物理变形（如生物体、柔性物体）的管线，需要将物理状态数据结构化地交换给其他系统。

## 蓝图用法

本插件**不提供任何蓝图公开的接口**。其所有功能均通过 C++ API 暴露。

## C++ 用法

### 头文件引入

```cpp
#include "ChaosCachingUSD/Operations.h"
```

### 基本用法

基本流程涉及创建/打开 USD Stage，写入或读取数据，然后保存和关闭 Stage。

```cpp
// 示例：创建一个新的 USD Stage 并写入一帧点数据
#include "ChaosCachingUSD/Operations.h"
#include "UsdWrappers/UsdStage.h"

void WriteOneFrame()
{
    UE::FUsdStage Stage;
    FString StagePath = TEXT("C:/SimCache/MySimulation.usd");

    // 1. 创建 Stage
    if (!UE::ChaosCachingUSD::NewStage(StagePath, Stage))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create USD stage"));
        return;
    }

    // 2. 准备要写入的点数据 (假设来自某个物理集合)
    TArray<Chaos::TVector<float, 3>> Points;
    TArray<Chaos::TVector<float, 3>> Velocities;
    // ... 填充 Points 和 Velocities 数据 ...

    // 3. 写入点数据到 Stage 中指定的 Prim 路径下，时间码为 1.0
    const FString PrimPath = TEXT("/World/SimResult");
    const double Time = 1.0;
    UE::ChaosCachingUSD::WritePoints(Stage, PrimPath, Time, Points, Velocities);

    // 4. 保存并设置帧范围
    UE::ChaosCachingUSD::SaveStage(Stage, /*FirstFrame*/ 1.0, /*LastFrame*/ 1.0);

    // 5. 关闭 Stage (通常在作用域结束时自动关闭，或显式调用)
    UE::ChaosCachingUSD::CloseStage(Stage);
}
```

### 进阶用法

使用 “Value Clips” 机制来存储一个动画序列，将拓扑信息（不随时间变化）和逐帧的点位置信息分开存储。

```cpp
void WriteAnimationWithClips()
{
    // 1. 生成 Value Clips 所需的文件名模板
    FString ParentStageName = TEXT("C:/SimCache/AnimSequence.usd");
    FString TopologyStageName, TimeVaryingStageTemplate;
    UE::ChaosCachingUSD::GenerateValueClipStageNames(ParentStageName, TopologyStageName, TimeVaryingStageTemplate);

    // 2. 创建父级 Stage 和拓扑 Stage
    UE::FUsdStage ParentStage, TopologyStage;
    if (!UE::ChaosCachingUSD::NewValueClipsStages(ParentStageName, TopologyStageName, ParentStage, TopologyStage))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create clip stages"));
        return;
    }

    // 3. 初始化 Value Clips 模板（在父级 Stage 上设置元数据）
    const TArray<FString> PrimPaths = { TEXT("/World/SimResult") };
    const double StartTime = 0.0, EndTime = 10.0, Stride = 1.0 / 30.0; // 30fps
    if (!UE::ChaosCachingUSD::InitValueClipsTemplate(ParentStage, TopologyStage,
        ParentStageName, TopologyStageName, TimeVaryingStageTemplate,
        PrimPaths, StartTime, EndTime, Stride))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to init value clips"));
        return;
    }

    // 4. 写入不随时间变化的数据到拓扑 Stage (例如，四面体拓扑)
    UE::FManagedArrayCollection Collection; // 假设已从 Chaos Solver 获取
    UE::ChaosCachingUSD::WriteTetMesh(TopologyStage, PrimPaths[0], Collection);

    // 5. 逐帧创建并写入时间变化数据
    for (double Time = StartTime; Time <= EndTime; Time += Stride)
    {
        UE::FUsdStage FrameStage;
        FString FrameStageName;
        if (UE::ChaosCachingUSD::NewValueClipsFrameStage(TimeVaryingStageTemplate, Time, FrameStageName, FrameStage))
        {
            // 从当前仿真状态获取点数据
            TArray<Chaos::TVector<float, 3>> FramePoints, FrameVels;
            // ... 获取 FramePoints 和 FrameVels ...

            // 写入点数据
            UE::ChaosCachingUSD::WritePoints(FrameStage, PrimPaths[0], pxr::UsdTimeCode::Default(), FramePoints, FrameVels);
            // 注意：帧 Stage 的 TimeCode 通常设为 Default()，因为文件本身已经代表了该时间点
            UE::ChaosCachingUSD::CloseStage(FrameStage);
        }
    }

    // 6. 保存并关闭所有 Stage
    UE::ChaosCachingUSD::SaveStage(ParentStage, StartTime, EndTime);
    UE::ChaosCachingUSD::SaveStage(TopologyStage, StartTime, EndTime);
    UE::ChaosCachingUSD::CloseStage(TopologyStage);
    UE::ChaosCachingUSD::CloseStage(ParentStage);
}
```

## Demo 示例

以下是一个最小完整示例，演示如何将一组静态点数据写入 USD 文件，然后读取回来。

**MyUSDWriter.h**
```cpp
#pragma once
#include "CoreMinimal.h"

class FMyUSDWriter
{
public:
    static void WriteStaticPointsToUSD(const FString& FilePath);
    static TArray<FVector> ReadPointsFromUSD(const FString& FilePath);
};
```

**MyUSDWriter.cpp**
```cpp
#include "MyUSDWriter.h"
#include "ChaosCachingUSD/Operations.h"
#include "UsdWrappers/UsdStage.h"

void FMyUSDWriter::WriteStaticPointsToUSD(const FString& FilePath)
{
    UE::FUsdStage Stage;
    if (!UE::ChaosCachingUSD::NewStage(FilePath, Stage))
    {
        return;
    }

    // 创建一个简单的点阵列
    TArray<Chaos::TVector<float, 3>> Points;
    Points.Add(Chaos::TVector<float, 3>(0, 0, 0));
    Points.Add(Chaos::TVector<float, 3>(100, 0, 0));
    Points.Add(Chaos::TVector<float, 3>(100, 100, 0));

    TArray<Chaos::TVector<float, 3>> Vels; // 速度可以为空
    Vels.SetNumZeroed(Points.Num());

    // 写入数据，Time 设为 -DBL_MAX 表示写入 USD 的 Default 时间（非时间变化数据）
    if (UE::ChaosCachingUSD::WritePoints(Stage, TEXT("/Root/MyPoints"), -DBL_MAX, Points, Vels))
    {
        UE::ChaosCachingUSD::SaveStage(Stage, 1.0, 1.0);
    }
    UE::ChaosCachingUSD::CloseStage(Stage);
}

TArray<FVector> FMyUSDWriter::ReadPointsFromUSD(const FString& FilePath)
{
    TArray<FVector> OutPoints;
    UE::FUsdStage Stage;
    if (!UE::ChaosCachingUSD::OpenStage(FilePath, Stage))
    {
        return OutPoints;
    }

    pxr::VtArray<pxr::GfVec3f> VtPoints, VtVels;
    // 读取默认时间的数据
    if (UE::ChaosCachingUSD::ReadPoints(Stage, TEXT("/Root/MyPoints"), -DBL_MAX, VtPoints, VtVels))
    {
        for (const auto& Pt : VtPoints)
        {
            OutPoints.Add(FVector(Pt[0], Pt[1], Pt[2]));
        }
    }
    UE::ChaosCachingUSD::CloseStage(Stage);
    return OutPoints;
}
```

## 模块依赖

从 .uplugin 的 `Plugins` 字段可知，要使用此插件，你的模块需要依赖以下插件提供的模块：

| 模块 | 用途 |
|---|---|
| `ChaosCaching` | Chaos 物理缓存核心系统 |
| `USDImporter` | UE5 的 USD 导入/导出和包装层 |
| `UsdUtilities` | USD 工具函数库 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 日志宏迁移至新的 UE_LOGF 宏。 |
| 2026-02-03 | `20825e79` | Fix duplicate symbol linker errors | 修复了链接器的重复符号错误。 |
| 2025-10-29 | `470e8976` | USDCore: remove use of deprecated Usd-level file format headers | USDCore: 移除了对已弃用的 Usd 层文件格式头的使用。 |
| 2025-10-24 | `19dfa25d` | USD: Centralized and exposed a single function to check if the USD SDK is enabled in UnrealUSDWrapper | USD: 集中并暴露了一个单一函数来检查 USD SDK 在 UnrealUSDWrapper 中是否启用。 |
| 2025-10-17 | `b322ef48` | [Backout] - CL47041219 | [回退] - CL47041219 提交。 |

### 维护评价

-   **创建时间**：该插件于 2023 年 8 月创建，历史较短。
-   **近期更新**：最近的提交（截至 2026 年 4 月）均为维护性更新，包括日志宏迁移、链接错误修复和清理废弃 API。自首次创建提交 (`4198242d`) 之后，**没有新增功能的实质性提交**。
-   **维护活跃度**：**维护不活跃**。虽然仍有零星的维护性提交以适配引擎版本更新，但核心功能自 2023 年 8 月后无任何发展。
-   **已知限制**：
    1.  **实验性**：标记为 `IsExperimentalVersion=true`，且默认禁用 (`EnabledByDefault=false`)。
    2.  **平台限制**：目前仅支持 `Win64` 平台。
    3.  **状态未知**：作为从 USDImporter 迁移出的独立插件，其长期维护计划和功能完善度尚不明确。
-   **推荐使用**：**谨慎使用**。如果你有明确的、静态的 Chaos 物理仿真数据需要与 USD 工作流集成，可以作为实验性方案尝试。但不应将其视为长期稳定的核心管线组件。在项目中使用前，建议进行充分的测试，并关注其后续的弃用或合并动向。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosCachingUSD)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosCachingUSD/Tests) (如果存在，通常在此路径下)