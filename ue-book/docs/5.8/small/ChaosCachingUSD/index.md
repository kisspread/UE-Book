# Chaos Caching USD

> Adds support for using USD files for caching Chaos flesh simulations

| 属性 | 值 |
|---|---|
| 中文名 | 混沌缓存USD支持 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ChaosCachingUSD` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-08-02 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosCachingUSD) | |

## 用途

该插件为 Chaos 布料（Flesh）模拟数据提供了 USD 格式的缓存与读写功能。它允许开发者将 Chaos 物理引擎生成的复杂布料模拟结果（如顶点位置、速度、肌肉激活状态、四面体拓扑结构）序列化为通用的 USD 文件格式，从而实现模拟结果的保存、跨平台交换、以及在不同 DCC 工具中的回放与处理。它特别支持 USD 的 Value Clips 特性，用于将庞大的时序模拟数据分帧存储到多个文件中，优化存储与加载效率。

## 使用场景

- 你需要将 UE5 中运行的 Chaos 布料模拟结果导出为 USD 文件，以便在 Maya、Houdini 等第三方软件中进行后期处理或渲染。
- 你需要一个标准化的文件格式来存储和交换复杂的物理模拟数据，用于技术美术（Tech Art）管线或数据驱动动画工作流。
- 你的项目使用了 Chaos 的四面体网格（Tetrahedral Mesh）进行模拟，并且需要将其拓扑结构及变形数据持久化保存。

## 蓝图用法

此插件主要提供 C++ 接口，用于在编辑器或运行时与 USD 数据交互。未暴露蓝图可用的函数。

## C++ 用法

### 头文件引入

使用该插件提供的操作函数，需包含以下头文件：

```cpp
#include "ChaosCachingUSD/Operations.h"
```

### 基本用法

以下示例展示了如何创建一个 USD 阶段（Stage），并向其中写入模拟数据的点（顶点）和速度信息。

**创建 USD 阶段并写入点数据**
```cpp
#include "ChaosCachingUSD/Operations.h"
#include "UObject/UObjectGlobals.h"

void SaveSimulationToUSD()
{
    using namespace UE::ChaosCachingUSD;

    UE::FUsdStage Stage;
    const FString StagePath = FPaths::ProjectSavedDir() / TEXT("SimulationCache.usd");

    // 1. 创建一个新的 USD 阶段
    if (!NewStage(StagePath, Stage))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create USD stage"));
        return;
    }

    // 2. 准备模拟数据（示例数据）
    const FString PrimPath = TEXT("/World/ClothMesh");
    const double Time = 0.0; // 使用 USD 的 ‘default’ 时间
    TArray<Chaos::TVector<float, 3>> Points, Velocities;
    // ... (此处填充 Points 和 Velocities 数据)

    // 3. 将点与速度数据写入 USD 阶段
    if (!WritePoints(Stage, PrimPath, Time, Points, Velocities))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to write points to USD stage"));
    }

    // 4. 保存并关闭阶段
    const double FirstFrame = 0.0;
    const double LastFrame = 100.0;
    SaveStage(Stage, FirstFrame, LastFrame);
    CloseStage(Stage);
}
```
*来源参考：`Operations.h` 中 `WritePoints`, `NewStage`, `SaveStage` 的函数声明与注释。*

### 进阶用法

对于需要分帧存储大量模拟数据的场景，应使用 USD 的 Value Clips 功能。以下示例展示了初始化 Value Clips 模板并写入多帧数据的流程。

**使用 Value Clips 存储分帧数据**
```cpp
#include "ChaosCachingUSD/Operations.h"

void SaveSimulationWithValueClips()
{
    using namespace UE::ChaosCachingUSD;

    const FString ParentStagePath = FPaths::ProjectSavedDir() / TEXT("ClothSim.usd");
    FString TopologyPath, TimeVaryingTemplate;

    // 1. 根据父阶段路径生成拓扑阶段和时间模板文件名
    GenerateValueClipStageNames(ParentStagePath, TopologyPath, TimeVaryingTemplate);

    UE::FUsdStage ParentStage, TopologyStage;
    // 2. 创建父阶段和拓扑阶段（存储不变的拓扑数据，如网格连接关系）
    if (!NewValueClipsStages(ParentStagePath, TopologyPath, ParentStage, TopologyStage))
    {
        return;
    }

    // 3. 将拓扑数据写入 TopologyStage
    const FString PrimPath = TEXT("/World/ClothMesh");
    FManagedArrayCollection Collection; // 包含网格拓扑信息
    // ... (此处从模拟器获取拓扑数据到 Collection)
    WriteTetMesh(TopologyStage, PrimPath, Collection); // 示例：写入四面体网格

    // 4. 初始化 Value Clips 元数据
    const TArray<FString> PrimPaths = { PrimPath };
    const double StartTime = 0.0, EndTime = 10.0, Stride = 0.033; // 30FPS
    InitValueClipsTemplate(
        ParentStage, TopologyStage,
        ParentStagePath, TopologyPath, TimeVaryingTemplate,
        PrimPaths, StartTime, EndTime, Stride
    );

    // 5. 循环写入每一帧的点数据
    for (double CurrentTime = StartTime; CurrentTime <= EndTime; CurrentTime += Stride)
    {
        FString FrameStageName;
        UE::FUsdStage FrameStage;
        // 为当前帧创建单独的 USD 文件
        if (!NewValueClipsFrameStage(TimeVaryingTemplate, CurrentTime, FrameStageName, FrameStage))
        {
            continue;
        }

        // 获取当前帧的模拟结果
        TArray<Chaos::TVector<float, 3>> Points, Velocities;
        // ... (此处获取当前帧数据)
        WritePoints(FrameStage, PrimPath, CurrentTime, Points, Velocities);
        
        // 保存并关闭当前帧的阶段
        SaveStage(FrameStage, -DBL_MAX, -DBL_MAX);
        CloseStage(FrameStage);
    }

    // 6. 保存并关闭父阶段和拓扑阶段
    SaveStage(ParentStage, StartTime, EndTime);
    SaveStage(TopologyStage, -DBL_MAX, -DBL_MAX);
    CloseStage(ParentStage);
    CloseStage(TopologyStage);
}
```
*来源参考：`Operations.h` 中 `GenerateValueClipStageNames`, `NewValueClipsStages`, `InitValueClipsTemplate`, `NewValueClipsFrameStage`, `WriteTetMesh` 的组合使用。*

## Demo 示例

一个完整的、可编译的最小 C++ 示例，演示如何利用 `UE::ChaosCachingUSD` 命名空间中的函数创建一个 USD 文件并写入基础数据。

**ChaosCachingUSDDemo.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "ChaosCachingUSD/Operations.h"

class FChaosCachingUSDDemo
{
public:
    static void RunDemo();
};
```

**ChaosCachingUSDDemo.cpp**
```cpp
#include "ChaosCachingUSDDemo.h"
#include "HAL/FileManager.h"

void FChaosCachingUSDDemo::RunDemo()
{
    using namespace UE::ChaosCachingUSD;
    
    const FString DemoFilePath = FPaths::ProjectSavedDir() / TEXT("ChaosCacheUSD_Demo.usd");
    UE::FUsdStage Stage;

    // 创建阶段
    if (!NewStage(DemoFilePath, Stage))
    {
        UE_LOG(LogTemp, Warning, TEXT("ChaosCachingUSDDemo: Failed to create stage."));
        return;
    }

    // 写入一些示例点数据（一个三角形）
    const FString DemoPrimPath = TEXT("/DemoPrim");
    TArray<Chaos::TVector<float, 3>> DemoPoints = {
        Chaos::TVector<float, 3>(0.f, 0.f, 0.f),
        Chaos::TVector<float, 3>(1.f, 0.f, 0.f),
        Chaos::TVector<float, 3>(0.f, 1.f, 0.f)
    };
    TArray<Chaos::TVector<float, 3>> DemoVelocities = {
        Chaos::TVector<float, 3>(0.f, 0.f, 0.f),
        Chaos::TVector<float, 3>(0.f, 0.f, 0.f),
        Chaos::TVector<float, 3>(0.f, 0.f, 0.f)
    };

    if (WritePoints(Stage, DemoPrimPath, -DBL_MAX, DemoPoints, DemoVelocities))
    {
        // 保存并关闭
        SaveStage(Stage, -DBL_MAX, -DBL_MAX);
        CloseStage(Stage);
        UE_LOG(LogTemp, Log, TEXT("ChaosCachingUSDDemo: Successfully created USD file at %s"), *DemoFilePath);
    }
    else
    {
        CloseStage(Stage);
        UE_LOG(LogTemp, Error, TEXT("ChaosCachingUSDDemo: Failed to write points."));
    }
}
```

## 模块依赖

此插件本身依赖于 `ChaosCaching` 和 `USDImporter` 插件，并在 `.uplugin` 文件中声明了这些依赖。

| 模块 | 用途 |
|---|---|
| `ChaosCaching` | 提供核心的 Chaos 模拟缓存框架和数据结构（如 `FManagedArrayCollection`）。 |
| `USDImporter` | 提供底层的 USD SDK 封装（`UE::FUsdStage`）、导入导出基础功能以及 USD 基础设施。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从UE_LOG迁移至新的UE_LOGF格式。 |
| 2026-02-03 | `20825e79` | Fix duplicate symbol linker errors | 修复了因符号重复导致的链接错误。 |
| 2025-10-29 | `470e8976` | USDCore: remove use of deprecated Usd-level file format headers | 移除了对已弃用的USD文件格式头文件的使用。 |
| 2025-10-24 | `19dfa25d` | USD: Centralized and exposed a single function to check if the USD SDK is enabled in UnrealUSDWrappe | 将检查USD SDK是否启用的功能集中并暴露为一个函数。 |
| 2025-10-17 | `b322ef48` | [Backout] - CL47041219 | 回滚了编号为CL47041219的改动。 |

### 维护评价

该插件创建于 2023 年 8 月，**处于活跃维护中**。从近期提交记录可以看出，虽然其核心功能（模拟数据USD读写）已基本稳定，但开发团队仍在持续进行维护工作，包括修复编译链接问题、跟进上游USD SDK的API变更（如移除弃用头文件）、以及改进内部代码（日志宏迁移）。由于其依赖的`USDImporter`和`ChaosCaching`插件本身也在积极更新，此插件得以保持兼容性。

**推荐使用**，尤其是在需要与第三方DCC工具进行Chaos模拟数据交换的USD工作流中。需要注意的是，该插件被标记为`IsExperimentalVersion=true`且`EnabledByDefault=false`，属于实验性功能，未来API或有变动。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosCachingUSD)
- [官方文档]() (无)
- [测试用例]() (源码中未发现独立的测试文件)