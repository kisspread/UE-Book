# Chaos Caching USD

> Adds support for using USD files for caching Chaos flesh simulations

| 属性 | 值 |
|---|---|
| 中文名 | Chaos缓存USD导出 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（USD自定义Schema定义） |
| 模块 | `ChaosCachingUSD` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-08-02 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosCachingUSD) | |

## 用途

该插件为 Chaos 物理系统的 **Flesh（软体/肉体）模拟** 提供 USD 文件格式的缓存导出支持。它将 Chaos 物理模拟产生的四面体网格（TetMesh）、顶点位置、速度和肌肉激活数据写入 USD 文件，并支持读取和回放这些缓存数据。

核心问题：Chaos Flesh 模拟计算代价高昂，需要将模拟结果缓存到文件以便回放。该插件利用 USD 的 **Value Clips** 机制将大量帧数据拆分为多个文件，实现高效存储和按需加载。

该插件从 `USDImporter` 插件中独立拆分出来（见首次提交信息），专门处理 Chaos 缓存与 USD 之间的数据转换。

## 使用场景

- 你使用 Chaos Flesh 系统进行软体物理模拟（如肌肉、皮肤变形），需要将模拟结果导出为 USD 文件以便离线回放或跨软件交换
- 你需要将 Chaos 模拟缓存存储为 USD Value Clips 格式，以获得高效的分帧存储能力
- 你需要从 USD 文件中读取之前缓存的 Chaos 模拟数据并回放

## 蓝图用法

该插件没有暴露任何蓝图节点。所有 API 均为 C++ 接口，面向编辑器工具和资产导入管线使用。

## C++ 用法

### 头文件引入

```cpp
#include "ChaosCachingUSD/Operations.h"
```

### 基本用法 — USD Stage 管理

操作 USD Stage 的基本流程：创建、打开、保存、关闭。

```cpp
#include "ChaosCachingUSD/Operations.h"

using namespace UE::ChaosCachingUSD;

// 创建新的 USD Stage
FUsdStage Stage;
bool bCreated = NewStage(TEXT("C:/Cache/MySimulation.usd"), Stage);

// 打开已有的 USD Stage
FUsdStage ExistingStage;
bool bOpened = OpenStage(TEXT("C:/Cache/MySimulation.usd"), ExistingStage);

// 保存并设置帧范围
bool bSaved = SaveStage(Stage, 0.0, 100.0);

// 关闭 Stage
bool bClosed = CloseStage(Stage);
// 也可以通过名称关闭
bool bClosedByName = CloseStage(TEXT("C:/Cache/MySimulation.usd"));
```

### 基本用法 — 写入模拟数据

将 Chaos 模拟数据写入 USD Stage：

```cpp
#include "ChaosCachingUSD/Operations.h"

using namespace UE::ChaosCachingUSD;

FUsdStage Stage;
NewStage(TEXT("C:/Cache/FleshSim.usd"), Stage);

FString PrimPath = TEXT("/Root/TetMesh");

// 写入四面体网格拓扑（不随时间变化的几何数据）
FManagedArrayCollection Collection;
WriteTetMesh(Stage, PrimPath, Collection, 0);

// 写入顶点位置和速度（随时间变化的每帧数据）
TArray<Chaos::TVector<float, 3>> Points;
TArray<Chaos::TVector<float, 3>> Vels;
// ... 填充 Points 和 Vels 数据 ...

for (double Time = 0.0; Time <= 100.0; Time += 1.0)
{
    WritePoints(Stage, PrimPath, Time, Points, Vels);
}

SaveStage(Stage, 0.0, 100.0);
CloseStage(Stage);
```

### 进阶用法 — USD Value Clips

Value Clips 是 USD 的分帧存储机制，将每帧数据存为独立文件，主文件仅做引用。适合大量帧的模拟缓存。

```cpp
#include "ChaosCachingUSD/Operations.h"

using namespace UE::ChaosCachingUSD;

FString ParentName = TEXT("C:/Cache/MySimulation.usd");
FString TopologyName, TimeVaryingTemplate;

// 根据主文件名生成拓扑文件和帧模板文件名
// "MySimulation.usd" → "MySimulation.topology.usd" + "MySimulation.###.###.usd"
GenerateValueClipStageNames(ParentName, TopologyName, TimeVaryingTemplate);

// 创建 Value Clips 的主 Stage 和拓扑 Stage
FUsdStage ParentStage, TopologyStage;
NewValueClipsStages(ParentName, TopologyName, ParentStage, TopologyStage);

// 初始化 Value Clips 模板（设置帧范围和步长）
TArray<FString> PrimPaths = { TEXT("/Root/TetMesh") };
InitValueClipsTemplate(
    ParentStageName, TopologyStageName, TimeVaryingTemplate,
    PrimPaths, 0.0, 100.0, 1.0  // StartTime, EndTime, Stride
);

// 为每一帧创建独立的 Stage 并写入数据
for (double Time = 0.0; Time <= 100.0; Time += 1.0)
{
    FString FrameStageName;
    FUsdStage FrameStage;
    NewValueClipsFrameStage(TimeVaryingTemplate, Time, FrameStageName, FrameStage);
    
    // 写入该帧的顶点数据
    WritePoints(FrameStage, PrimPath, Time, Points, Vels);
    
    // 每帧单独保存并关闭
    SaveStage(FrameStage, -DBL_MAX, -DBL_MAX);
    CloseStage(FrameStage);
}

// 保存主 Stage
SaveStage(ParentStage, 0.0, 100.0);
CloseStage(ParentStage);
CloseStage(TopologyStage);
```

### 进阶用法 — 读取缓存数据

从 USD 文件读取之前缓存的模拟数据：

```cpp
#include "ChaosCachingUSD/Operations.h"

using namespace UE::ChaosCachingUSD;

FUsdStage Stage;
OpenStage(TEXT("C:/Cache/FleshSim.usd"), Stage);

FString PrimPath = TEXT("/Root/TetMesh");

// 获取所有可用的时间采样点
TArray<double> TimeSamples;
ReadTimeSamples(Stage, PrimPath, TimeSamples);

// 读取特定时间的顶点位置和速度
pxr::VtArray<pxr::GfVec3f> Points, Vels;
ReadPoints(Stage, PrimPath, 50.0, Points, Vels);

// 读取肌肉激活数据
pxr::VtArray<float> Activations;
ReadMuscleActivation(Stage, PrimPath, 50.0, Activations);

// 获取包围时间采样（用于插值）
double Lower, Upper;
GetBracketingTimeSamples(Stage, PrimPath, GetPointsAttrName(), 49.5, &Lower, &Upper);

CloseStage(Stage);
```

## Demo 示例

以下是一个完整的最小示例，演示如何将 Chaos 模拟数据缓存到 USD 并读取回来：

```cpp
// SimCacheToUSD.h
#pragma once

class FSimCacheToUSDExample
{
public:
    /** 将模拟数据导出到 USD 文件 */
    static bool ExportSimulationCache(const FString& USDFilePath, int32 NumFrames);
    
    /** 从 USD 文件读取模拟数据 */
    static bool ImportSimulationCache(const FString& USDFilePath);
};
```

```cpp
// SimCacheToUSD.cpp
#include "SimCacheToUSD.h"
#include "ChaosCachingUSD/Operations.h"

using namespace UE::ChaosCachingUSD;

bool FSimCacheToUSDExample::ExportSimulationCache(const FString& USDFilePath, int32 NumFrames)
{
    FUsdStage Stage;
    if (!NewStage(USDFilePath, Stage))
    {
        return false;
    }

    const FString PrimPath = TEXT("/Root/SimMesh");

    // 写入拓扑数据（第一帧）
    FManagedArrayCollection Collection;
    // ... 填充 Collection ...
    WriteTetMesh(Stage, PrimPath, Collection, INDEX_NONE);

    // 逐帧写入位置和速度
    for (int32 Frame = 0; Frame < NumFrames; ++Frame)
    {
        TArray<Chaos::TVector<float, 3>> Points, Vels;
        // ... 模拟或获取第 Frame 帧的数据 ...
        const double Time = static_cast<double>(Frame);
        
        if (!WritePoints(Stage, PrimPath, Time, Points, Vels))
        {
            CloseStage(Stage);
            return false;
        }
    }

    SaveStage(Stage, 0.0, static_cast<double>(NumFrames - 1));
    CloseStage(Stage);
    return true;
}

bool FSimCacheToUSDExample::ImportSimulationCache(const FString& USDFilePath)
{
    FUsdStage Stage;
    if (!OpenStage(USDFilePath, Stage))
    {
        return false;
    }

    const FString PrimPath = TEXT("/Root/SimMesh");

    // 获取所有时间采样
    TArray<double> TimeSamples;
    ReadTimeSamples(Stage, PrimPath, TimeSamples);

    // 读取每一帧的数据
    for (double Time : TimeSamples)
    {
        pxr::VtArray<pxr::GfVec3f> Points, Vels;
        if (ReadPoints(Stage, PrimPath, Time, Points, Vels))
        {
            // 处理 Points 和 Vels ...
        }
    }

    CloseStage(Stage);
    return true;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `USDUtilities` | USD 工具函数，提供 Stage 管理等基础能力 |
| `UnrealUSDWrapper` | UE 对 USD SDK 的封装层 |

该插件还依赖以下插件：
- **ChaosCaching** — Chaos 模拟缓存系统，提供 `FManagedArrayCollection` 等数据结构
- **USDImporter** — USD 导入基础功能

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到新的 UE_LOGF 宏 |
| 2026-02-03 | `20825e79` | Fix duplicate symbol linker errors | 修复链接器重复符号错误 |
| 2025-10-29 | `470e8976` | USDCore: remove use of deprecated Usd-level file format headers | 移除已弃用的 USD 文件格式头文件引用 |
| 2025-10-24 | `19dfa25d` | USD: Centralized and exposed a single function to check if the USD SDK is enabled in UnrealUSDWrappe | 集中化 USD SDK 启用检查功能 |
| 2025-10-17 | `b322ef48` | [Backout] - CL47041219 | 回退一次代码提交 |

### 维护评价

该插件创建于 2023 年 8 月，处于**实验性**阶段（`IsExperimentalVersion=true`），且默认未启用。近期更新以**维护性修复**为主（日志迁移、链接错误修复、弃用 API 清理），未见功能性更新。

- **活跃度**：低频维护，最近一次功能性 commit 需追溯到更早版本
- **稳定性**：实验性插件，API 可能发生变化
- **平台限制**：仅支持 Win64 平台
- **风险提示**：该插件仍标记为实验性，且自 2025 年 10 月起仅有被动维护（跟随 UE 代码库整体变更），未来可能被移除或合并

**建议**：仅在 Chaos Flesh 相关开发中按需启用，不建议用于生产环境的核心功能依赖。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosCachingUSD)
- [ChaosCaching 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosCaching)
- [USDImporter 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/USDImporter)