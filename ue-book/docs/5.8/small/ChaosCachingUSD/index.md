# Chaos Caching USD

> Adds support for using USD files for caching Chaos flesh simulations（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 混沌缓存 USD |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（USD 资产） |
| 模块 | `ChaosCachingUSD` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-08-02 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosCachingUSD) | |

## 用途

本插件为 Chaos 物理系统（特别是布料/肌肉模拟）的缓存数据提供了 USD (Universal Scene Description) 格式的读写支持。它不是一个通用的 USD 导入/导出工具，而是一个专用的桥接层，允许用户将 Chaos 模拟的结果（如顶点位置、速度、肌肉激活度、四面体网格拓扑等）以 USD 的 `Value Clips` 格式进行存储和加载。这种格式将数据按时间序列拆分成多个文件，便于高效地处理大型模拟缓存。

简单来说，它解决了 **将 Chaos 模拟结果序列化到专业 VFX 流水线（基于 USD）的需求**。

## 使用场景

- **动画与 VFX 流水线**：你在使用 Chaos 制作角色布料或肌肉模拟，需要将这些模拟结果导出给其他 DCC 工具（如 Maya, Houdini）进行进一步的渲染或合成。
- **模拟缓存管理**：你需要将耗时的物理模拟结果缓存到磁盘，并在后续快速回放或编辑，同时保持与 USD 生态的兼容性。
- **数据交换与归档**：你需要一种标准化的格式来长期存储或在不同部门间共享 Chaos 模拟数据。

## 蓝图用法

本插件 **不提供蓝图接口**。其所有功能均通过 C++ API 实现，面向需要编写自定义导出/导入管线或工具的程序员。

## C++ 用法

### 头文件引入

```cpp
#include "ChaosCachingUSD/Operations.h"
```

### 基本用法：写入 Value Clips 缓存

以下代码演示了如何将 Chaos 布料模拟的逐帧数据写入一个 USD Value Clips 结构。来源：`Operations.h` 中的函数签名及文档注释。

```cpp
// 1. 定义 Value Clips 的文件结构
FString ParentStagePath = TEXT("/Game/MySimCache.usd");
FString TopologyStagePath;
FString TimeVaryingTemplate;
UE::ChaosCachingUSD::GenerateValueClipStageNames(ParentStagePath, TopologyStagePath, TimeVaryingTemplate);
// 结果: TopologyStagePath = “/Game/MySimCache.topology.usd”
//       TimeVaryingTemplate = “/Game/MySimCache.###.###.usd”

// 2. 创建并初始化 Value Clips 的父级和拓扑阶段
UE::FUsdStage ParentStage, TopologyStage;
bool bSuccess = UE::ChaosCachingUSD::NewValueClipsStages(ParentStagePath, TopologyStagePath, ParentStage, TopologyStage);
if (!bSuccess) return;

// 3. 初始化 Value Clips 模板（定义 Prim 层级和时间范围）
TArray<FString> PrimPaths = { TEXT("/ChaosCloth") };
double StartTime = 0.0;
double EndTime = 100.0;
double Stride = 1.0 / 30.0; // 30 FPS
UE::ChaosCachingUSD::InitValueClipsTemplate(
    ParentStage, TopologyStage,
    ParentStagePath, TopologyStagePath, TimeVaryingTemplate,
    PrimPaths, StartTime, EndTime, Stride
);

// 4. 循环每一帧，创建帧阶段并写入数据
for (double Time = StartTime; Time <= EndTime; Time += Stride)
{
    FString FrameStagePath;
    UE::FUsdStage FrameStage;
    UE::ChaosCachingUSD::NewValueClipsFrameStage(TimeVaryingTemplate, Time, FrameStagePath, FrameStage);

    // 从你的 Chaos 模拟收集器（FManagedArrayCollection）中获取当前帧数据
    const FManagedArrayCollection& Collection = GetSimulationDataForFrame(Time);
    
    // 写入点和速度数据
    UE::ChaosCachingUSD::WritePoints(
        FrameStage, TEXT("/ChaosCloth"), Time, Collection
    );

    // 关闭当前帧阶段，确保数据写入磁盘
    UE::ChaosCachingUSD::CloseStage(FrameStage);
}

// 5. 保存并关闭父级和拓扑阶段
UE::ChaosCachingUSD::SaveStage(ParentStage, StartTime, EndTime);
UE::ChaosCachingUSD::CloseStage(ParentStage);
UE::ChaosCachingUSD::CloseStage(TopologyStage);
```

### 进阶用法：读取缓存与时间插值

以下代码演示了如何读取一个已存在的 Value Clips 缓存，并在特定时间进行插值采样。来源：`Operations.h` 中的 `ReadPoints` 和 `ReadTimeSamples` 函数。

```cpp
// 打开已存在的缓存阶段
UE::FUsdStage Stage;
UE::ChaosCachingUSD::OpenStage(TEXT("/Game/MySimCache.usd"), Stage);

FString PrimPath = TEXT("/ChaosCloth");
TArray<double> TimeSamples;
UE::ChaosCachingUSD::ReadTimeSamples(Stage, PrimPath, TimeSamples);

// 查询并插值位于 TimeSamples[10] 和 TimeSamples[11] 之间的目标时间
double TargetTime = (TimeSamples[10] + TimeSamples[11]) / 2.0;
double LowerTime, UpperTime;
UE::ChaosCachingUSD::GetBracketingTimeSamples(Stage, PrimPath, TEXT("points"), TargetTime, &LowerTime, &UpperTime);

// 分别读取两个边界时间的数据
pxr::VtArray<pxr::GfVec3f> PointsLower, PointsUpper;
UE::ChaosCachingUSD::ReadPoints(Stage, PrimPath, LowerTime, PointsLower);
UE::ChaosCachingUSD::ReadPoints(Stage, PrimPath, UpperTime, PointsUpper);

// 使用 Util.h 中的 CastLerp 进行线性插值
float Alpha = (TargetTime - LowerTime) / (UpperTime - LowerTime);
TArray<Chaos::TVector<float,3>> InterpolatedPoints;
UE::ChaosCachingUSDUtil::Private::CastLerp(PointsLower, PointsUpper, InterpolatedPoints, Alpha);

UE::ChaosCachingUSD::CloseStage(Stage);
```

## Demo 示例

以下是一个完整的、可编译的最小示例，演示如何将一组测试点写入 USD 文件。

**MyCacheWriter.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FMyCacheWriterModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
    
    void WriteTestCacheToUSD();
};
```

**MyCacheWriter.cpp**
```cpp
#include "MyCacheWriter.h"
#include "ChaosCachingUSD/Operations.h"
#include "Misc/FileHelper.h"

#define LOCTEXT_NAMESPACE "FMyCacheWriterModule"

void FMyCacheWriterModule::StartupModule()
{
    // 可在此添加启动逻辑
}

void FMyCacheWriterModule::ShutdownModule()
{
    // 可在此添加清理逻辑
}

void FMyCacheWriterModule::WriteTestCacheToUSD()
{
    const FString FilePath = FPaths::ProjectSavedDir() / TEXT("TestChaosCache.usd");
    UE::FUsdStage Stage;
    
    // 创建新阶段
    if (!UE::ChaosCachingUSD::NewStage(FilePath, Stage))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create USD stage"));
        return;
    }
    
    // 准备测试数据：3个点，3帧
    const int32 NumPoints = 3;
    const int32 NumFrames = 3;
    for (int32 Frame = 0; Frame < NumFrames; ++Frame)
    {
        const double Time = static_cast<double>(Frame);
        TArray<Chaos::TVector<float,3>> Points, Velocities;
        Points.SetNum(NumPoints);
        Velocities.SetNum(NumPoints);
        
        for (int32 i = 0; i < NumPoints; ++i)
        {
            // 创建简单的动画：点在Z轴上移动
            Points[i] = Chaos::TVector<float,3>(i * 100.f, 0.f, Frame * 50.f);
            Velocities[i] = Chaos::TVector<float,3>(0.f, 0.f, 50.f); // Z轴速度
        }
        
        // 写入这一帧的数据
        UE::ChaosCachingUSD::WritePoints(
            Stage, TEXT("/TestPoints"), Time, Points, Velocities
        );
    }
    
    // 保存并关闭
    UE::ChaosCachingUSD::SaveStage(Stage, 0.0, static_cast<double>(NumFrames - 1));
    UE::ChaosCachingUSD::CloseStage(Stage);
    
    UE_LOG(LogTemp, Log, TEXT("Test cache saved to: %s"), *FilePath);
}

#undef LOCTEXT_NAMESPACE
    
IMPLEMENT_MODULE(FMyCacheWriterModule, MyCacheWriter)
```

## 模块依赖

从 `.uplugin` 的 `Plugins` 字段和典型用法推断：

| 模块 | 用途 |
|---|---|
| `ChaosCaching` | Chaos 模拟缓存的核心模块 |
| `USDImporter` | UE 的通用 USD 导入功能，提供 `FUsdStage` 等基础类型 |
| `USDCore` | 底层 USD SDK 的封装和绑定 |
| `GeometryCollectionEngine` | 提供 `FManagedArrayCollection`，是 Chaos 几何数据的容器 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧的 UE_LOG 宏迁移到新的 UE_LOGF 格式。 |
| 2026-02-03 | `20825e79` | Fix duplicate symbol linker errors | 修复了链接时出现的重复符号错误。 |
| 2025-10-29 | `470e8976` | USDCore: remove use of deprecated Usd-level file format headers | 移除了对已废弃的 USD 底层文件格式头文件的依赖。 |
| 2025-10-24 | `19dfa25d` | USD: Centralized and exposed a single function to check if the USD SDK is enabled in UnrealUSDWrappe | 集中并暴露了一个用于检查 USD SDK 是否启用的函数。 |
| 2025-10-17 | `b322ef48` | [Backout] - CL47041219 | 回退了之前的提交 CL47041219。 |

### 维护评价

该插件创建于 **2023年8月**，相对年轻。近期（2025年底至2026年初）仍有更新，但主要集中在 **编译修复、日志系统迁移和与底层 USD SDK 的兼容性维护** 上，而非重大功能更新。它是一个 **实验性** 插件 (`IsExperimentalVersion=true`)，并且默认未启用 (`EnabledByDefault=false`)。

**结论**：该插件处于 **“维护中但开发不活跃”** 状态。它能正常工作，但属于实验性功能，接口和功能可能会变化。仅推荐给有明确 Chaos 模拟缓存 USD 导出需求的项目使用，并注意跟进 Epic 官方的更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosCachingUSD)
- 官方文档：无
- 测试用例：未在提供的信息中找到。