# External GPU Statistics

> Plugin to find out more detailed GPU usage for NVIDIA, AMD, and Intel GPUs.

| 属性 | 值 |
|---|---|
| 中文名 | 外部GPU统计 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ExternalGPUStatistics` (Runtime) |
| 实验性 | ⚚️ 是 |
| 创建时间 | 2025-05-29 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ExternalGPUStatistics) | |

## 用途

本插件旨在绕过通用的图形API层，通过直接调用硬件厂商（NVIDIA、AMD、Intel）提供的专用库，来获取更精确、更详细的GPU硬件状态信息。它解决了引擎内置性能统计信息不够精细的问题，能为开发者提供如GPU核心频率、GPU繁忙率、显存占用等底层硬件指标，用于深度性能分析和调试。

## 使用场景

- 你正在开发一款对GPU性能有极致要求的图形应用（如电影级渲染、高精度科学可视化），需要监控GPU核心频率和占用率以排除瓶颈。
- 你是一名图形程序员或技术美术，需要分析特定GPU厂商硬件在Unreal Engine中的实际表现。
- 你需要在运行时动态调整渲染策略，依据GPU的实际负载（如繁忙率）来做决策。

## 蓝图用法

当前版本（1.0）的插件主要通过C++模块接口暴露功能，未提供任何 `BlueprintCallable` 或 `BlueprintReadWrite` 的蓝图节点。所有GPU统计信息的获取均需在C++层完成。

### 核心节点
无可用蓝图节点。

## C++ 用法

### 头文件引入

```cpp
#include "IExternalGPUStatistics.h"
```

### 基本用法

此插件的核心是模块接口和其封装的厂商特定API。以下示例展示了如何初始化并查询NVIDIA GPU的利用率和显存信息（基于源码中 `NVML` 相关实现推断）。

```cpp
// 1. 检查模块是否可用
if (IExternalGPUStatistics::IsAvailable())
{
    // 2. 获取模块实例
    IExternalGPUStatistics& GPUStats = IExternalGPUStatistics::Get();
    
    // 注意：实际接口需查阅具体厂商封装类。
    // 以下为基于 NVML 接口伪代码示例。
    // 假设存在一个 NVML 的封装类 `NVMLLibrary`
    if (GPUStats.IsNVMLInitialized()) // 假设的初始化检查函数
    {
        uint32 GpuUtilization = 0;
        uint64 MemoryUsed = 0;
        
        // 假设的查询函数，返回第一个GPU的利用率
        GPUStats.GetNvidiaGPUUtilization(0, GpuUtilization);
        // 假设的查询函数，返回第一个GPU的显存使用
        GPUStats.GetNvidiaGPUMemoryUsage(0, MemoryUsed);
        
        UE_LOG(LogTemp, Log, TEXT("GPU Utilization: %u%%"), GpuUtilization);
        UE_LOG(LogTemp, Log, TEXT("GPU Memory Used: %llu MB"), MemoryUsed / (1024 * 1024));
    }
}
```
**注意**：以上 `GetNvidiaGPUUtilization` 等函数为基于插件设计推断的示例函数名。实际API请参考源码 `Source/ExternalGPUStatistics/Public/` 和 `Private/Vendors/` 下的头文件。插件当前公开的模块接口 `IExternalGPUStatistics` 主要作为模块加载和生命周期的入口。

### 进阶用法

从 `Intel.h` 源码分析可知，Intel的实现使用了 `oneAPI Level Zero` 来设置Metrics Streamer并收集数据。以下是一个模拟Intel GPU统计收集的流程片段（基于 `Intel.h` 中的函数签名）：

```cpp
#include "Vendors/Intel.h"

// ... 在某个初始化函数中
TArray<UE::GPUStats::Intel::FIntelDriver> Drivers;
if (UE::GPUStats::Intel::GetDrivers(Drivers) && Drivers.Num() > 0)
{
    TArray<UE::GPUStats::Intel::FIntelDevice> Devices;
    if (UE::GPUStats::Intel::GetDevicesForDriver(Drivers[0], Devices) && Devices.Num() > 0)
    {
        TArray<zet_metric_group_handle_t> MetricsForDevice;
        if (UE::GPUStats::Intel::SetupMetricsForDevice(Devices[0], MetricsForDevice))
        {
            TArray<UE::GPUStats::Intel::FIntelMetricsStreamer> MetricsStreamers;
            if (UE::GPUStats::Intel::SetupMetricsStreamersForDevice(Devices[0], MetricsForDevice, MetricsStreamers))
            {
                // 在后续帧中调用以获取数据
                float FrequencyScaling, GPUUtilization;
                uint64 GPUMemoryUsage;
                UE::GPUStats::Intel::CalculateMetrics(Devices[0], MetricsForDevice, MetricsStreamers, FrequencyScaling, GPUUtilization, GPUMemoryUsage);
                
                // ... 使用数据
            }
        }
    }
}

// ... 在引擎关闭时，需要清理资源
// 对每个 MetricsStreamer 调用 ShutdownMetricStreamer
// 对每个 Driver 调用 ShutdownDriver
```

## Demo 示例

一个最小的C++示例，演示如何初始化插件并假设查询一次GPU统计信息。

```cpp
// MyGPUStatsActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyGPUStatsActor.generated.h"

UCLASS()
class AMyGPUStatsActor : public AActor
{
    GENERATED_BODY()

public:
    AMyGPUStatsActor();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

public:
    virtual void Tick(float DeltaTime) override;

private:
    bool bGPUStatsInitialized = false;
};

// MyGPUStatsActor.cpp
#include "MyGPUStatsActor.h"
#include "IExternalGPUStatistics.h"

AMyGPUStatsActor::AMyGPUStatsActor()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AMyGPUStatsActor::BeginPlay()
{
    Super::BeginPlay();
    
    // 尝试初始化GPU统计（此函数为假设，实际初始化可能发生在模块加载时或需要调用特定API）
    if (IExternalGPUStatistics::IsAvailable())
    {
        // 这里可能需要调用具体厂商的初始化函数，例如 NVML 的 nvmlInit()
        // 为简化示例，假设模块加载即代表可用。
        bGPUStatsInitialized = true;
        UE_LOG(LogTemp, Log, TEXT("External GPU Statistics module is available."));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("External GPU Statistics module is not available."));
    }
}

void AMyGPUStatsActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    if (bGPUStatsInitialized)
    {
        // 伪代码：查询并打印GPU信息
        // 假设通过模块接口有一个简单的查询方法
        /*
        uint32 Utilization;
        if (IExternalGPUStatistics::Get().QueryGPUUtilization(Utilization))
        {
            UE_LOG(LogTemp, Log, TEXT("Current GPU Utilization: %u%%"), Utilization);
        }
        */
        // 实际调用应基于插件暴露的真实API
    }
}

void AMyGPUStatsActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    Super::EndPlay(EndPlayReason);
    
    // 清理工作可能需要在模块级别进行，Actor销毁时可能无需特别操作。
    bGPUStatsInitialized = false;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `NVML` | 提供与 NVIDIA GPU 管理库交互的封装。 |
| `oneAPILevelZero` | 提供与 Intel oneAPI Level Zero 运行时交互的封装，用于获取 Intel GPU 底层指标。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复一次错误的查找替换后进行的第二次提交。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退了变更列表 CL51314860 的改动。 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist... | 将委托获取方式从静态变量改为函数调用，以修复注册丢失问题。 |
| 2026-02-02 | `4e9f614b` | （无消息） | 提交信息为空。 |

### 维护评价

该插件创建于一年前（2025年5月），属于实验性功能。从Git历史看，自创建后有过几次维护性更新（如委托API迁移、日志格式变更、错误修复），最近一次实质性功能更新可能在2025年7月（基于初始提交描述的规划）。近几个月的更新主要是跟随引擎代码风格的调整。由于仍标记为实验性且`EnabledByDefault=false`，表明Epic官方可能仍在评估其稳定性和功能完整性。它目前处于**维护中**状态，适合用于研究和实验，但不建议在生产环境的主关键路径上依赖此插件。推荐关注其后续版本，以确认AMD和Android支持的进展。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ExternalGPUStatistics)
- [官方文档]()（暂无）
- [测试用例]()（插件目录内未提供公开测试用例）