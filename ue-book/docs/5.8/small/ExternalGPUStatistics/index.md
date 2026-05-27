# External GPU Statistics

> Plugin to find out more detailed GPU usage for NVIDIA, AMD, and Intel GPUs.

| 属性 | 值 |
|---|---|
| 中文名 | 外部 GPU 统计 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ExternalGPUStatistics` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-05-29 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ExternalGPUStatistics) | |

## 用途

该插件通过各 GPU 厂商的专用 API 获取底层硬件级别的详细 GPU 使用信息，包括 GPU 核心频率、GPU 利用率和显存使用量。与 UE 内置的通用 GPU 性能统计不同，该插件直接调用 NVML（NVIDIA）和 oneAPI Level Zero（Intel）等厂商专有库，能提供更精确、更丰富的硬件监控数据。

该插件目前处于实验阶段，仅实现了 NVIDIA（通过 NVML）和 Intel（通过 oneAPI Level Zero）的支持，AMD 尚未实现。插件默认禁用，不适用于 Shipping 构建和 Server 目标。

## 使用场景

- 你需要在开发/测试阶段监控 NVIDIA 或 Intel GPU 的实时核心频率、利用率和显存占用 → 启用该插件
- 你正在做 GPU 性能分析工具或自定义性能 HUD，需要获取比 UE 内置统计更底层的硬件数据
- 你在做跨平台 GPU 性能对比测试（Win64/Linux），需要统一的厂商 API 抽象层

> ⚠️ 注意：该插件在 Shipping 构建中被禁止使用（TargetConfigurationDenyList 包含 Shipping），仅用于开发和测试。

## 蓝图用法

该插件未暴露任何 `BlueprintCallable` 函数，仅提供 C++ 模块接口。所有功能通过 C++ 代码访问。

## C++ 用法

### 头文件引入

```cpp
#include "IExternalGPUStatistics.h"
```

### 基本用法

通过模块接口访问 GPU 统计信息：

```cpp
// 检查模块是否可用
if (IExternalGPUStatistics::IsAvailable())
{
    // 获取模块实例
    IExternalGPUStatistics& GPUStats = IExternalGPUStatistics::Get();
}
```

> 模块加载阶段为 `PostEngineInit`，因此只能在引擎初始化完成后使用。

### Intel GPU 指标获取（内部实现）

以下代码展示了 Intel GPU 指标获取的核心流程（来自 `Source/ExternalGPUStatistics/Private/Vendors/Intel.h`）：

```cpp
#include "ze_api.h"
#include "zet_api.h"

namespace UE::GPUStats::Intel
{
    // 1. 获取驱动列表
    TArray<FIntelDriver> Drivers;
    GetDrivers(Drivers);

    // 2. 获取驱动下的设备
    for (const FIntelDriver& Driver : Drivers)
    {
        TArray<FIntelDevice> Devices;
        GetDevicesForDriver(Driver, Devices);

        for (const FIntelDevice& Device : Devices)
        {
            // 3. 设置指标组
            TArray<zet_metric_group_handle_t> MetricsForDevice;
            SetupMetricsForDevice(Device, MetricsForDevice);

            // 4. 创建指标流
            TArray<FIntelMetricsStreamer> Streamers;
            SetupMetricsStreamersForDevice(Device, MetricsForDevice, Streamers);

            // 5. 计算指标
            float FrequencyScaling = 0.f;
            float GPUUtilization = 0.f;
            uint64 GPUMemoryUsage = 0;
            CalculateMetrics(Device, MetricsForDevice, Streamers,
                             FrequencyScaling, GPUUtilization, GPUMemoryUsage);
        }
    }
}
```

### 进阶用法

该插件采集的三类核心指标（以 Intel 为例）：

| 指标枚举 | 说明 |
|---|---|
| `AvgGpuCoreFrequencyMHz` | GPU 核心平均频率 (MHz) |
| `GpuBusy` | GPU 利用率百分比 |
| `SlmBytesWritten` | 共享本地内存写入字节数 |

## Demo 示例

```cpp
// MyGPUMonitor.h
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "MyGPUMonitor.generated.h"

UCLASS()
class UMyGPUMonitor : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

    /** 尝试读取 GPU 统计信息，返回是否成功 */
    UFUNCTION(BlueprintCallable)
    bool QueryGPUStats(float& OutUtilization, float& OutFrequencyScaling, uint64& OutMemoryUsage);

private:
    double LastQueryTime = 0.0;
};
```

```cpp
// MyGPUMonitor.cpp
#include "MyGPUMonitor.h"
#include "IExternalGPUStatistics.h"

void UMyGPUMonitor::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
}

void UMyGPUMonitor::Deinitialize()
{
    Super::Deinitialize();
}

bool UMyGPUMonitor::QueryGPUStats(float& OutUtilization, float& OutFrequencyScaling, uint64& OutMemoryUsage)
{
    if (!IExternalGPUStatistics::IsAvailable())
    {
        UE_LOG(LogTemp, Warning, TEXT("ExternalGPUStatistics module is not available."));
        return false;
    }

    // 模块可用，可在此扩展具体查询逻辑
    // 当前 IExternalGPUStatistics 接口未公开具体查询方法，
    // 底层厂商 API（NVML / Level Zero）的具体调用在 Private 模块中实现
    return true;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `NVML` | NVIDIA Management Library，用于获取 NVIDIA GPU 硬件级统计信息 |
| `oneAPILevelZero` | Intel oneAPI Level Zero API，用于获取 Intel GPU 硬件级指标数据 |

> 该插件不依赖 UE 内部的 `RenderCore` 或 `RHI` 等渲染模块，而是直接通过厂商原生库获取硬件数据。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移到新的 UE_LOGF 格式 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复错误的批量替换后的重试 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退一个有问题的提交 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 修复引擎初始化委托的注册问题 |
| 2026-02-02 | `4e9f614b` | *(无描述)* | 提交信息缺失，推测为常规维护 |

### 维护评价

- **创建时间**：2025 年 5 月，非常年轻的插件
- **实验状态**：`IsExperimentalVersion=true`，`EnabledByDefault=false`，明确标记为实验性
- **最近活动**：最近一次更新在 2026 年 4 月，主要为内部 API 迁移（日志宏），属于维护性更新
- **功能完整性**：目前仅 NVIDIA 实现完整，Intel 已有框架代码，AMD 尚未实现
- **平台限制**：仅支持 Win64 和 Linux，不支持 Shipping 构建
- **存在回退/修复提交**：2026-02-27 有多次回退和修复，说明代码仍在积极调试中

**综合评价**：该插件仍处于早期实验阶段，功能尚不完整（缺少 AMD 支持），接口尚未对外公开具体查询方法。近期更新主要是内部维护和 API 迁移，而非新功能开发。**建议仅用于内部实验和测试，不建议在正式项目中依赖该插件。**

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ExternalGPUStatistics)
- [NVML 文档](https://docs.nvidia.com/deploy/nvml-api/)（NVIDIA GPU 统计底层 API）
- [oneAPI Level Zero 文档](https://spec.oneapi.io/level-zero/latest/)（Intel GPU 指标底层 API）