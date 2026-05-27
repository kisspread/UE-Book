# Performance Monitor

> A plugin for tracking the value of certain timers during gameplay.

| 属性 | 值 |
|---|---|
| 中文名 | 性能监控器 |
| 分类 | Performance |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PerformanceMonitor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2017-01-27 |
| 年龄标签 | 🏛️ 文物（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Performance/PerformanceMonitor) | |

## 用途

这是一个用于在游戏运行时收集性能统计数据并导出为 CSV 文件的工具插件。它通过控制台命令（Console Command）驱动，允许开发者指定要追踪的统计项（如帧时间、渲染线程耗时等），按设定间隔采样，并将结果写入文件。主要用于自动化性能测试、CI/CD 流水线中的帧率基准测试，以及 QA 团队在特定场景下的性能数据收集。

插件设计为**默认关闭**，需要手动启用后通过 `PerformanceMonitor` 控制台命令交互。

## 使用场景

- 你需要在自动化测试中收集帧率和 GPU 时间数据并导出 CSV → 用 PerformanceMonitor
- QA 团队需要在特定地图上运行固定时长的性能基准测试 → 用 PerformanceMonitor
- 你希望在 CI 流水线中自动收集性能指标用于回归检测 → 用 PerformanceMonitor

## 蓝图用法

该插件没有暴露任何蓝图可调用接口。所有功能通过控制台命令（Console Command）访问。

### 控制台命令

启用插件后，在控制台输入以下命令：

| 命令 | 说明 |
|---|---|
| `PerformanceMonitor help` | 显示使用帮助和可用选项 |
| `PerformanceMonitor start <文件名> [统计项列表]` | 开始录制性能数据到指定文件 |
| `PerformanceMonitor stop` | 停止录制并最终化输出文件 |

## C++ 用法

### 头文件引入

```cpp
#include "PerformanceMonitor.h"
```

### 基本用法

通过模块接口访问性能监控功能：

```cpp
#include "PerformanceMonitor.h"

// 检查模块是否可用
if (FPerformanceMonitorModule::IsAvailable())
{
    FPerformanceMonitorModule& PerfMonitor = FPerformanceMonitorModule::Get();
    
    // 检查当前是否正在录制
    if (!PerfMonitor.IsRecordingPerfTimers())
    {
        // 开始录制，指定输出文件和要追踪的统计项
        TArray<FString> StatsToRecord;
        StatsToRecord.Add(TEXT("STAT_FrameTime"));
        StatsToRecord.Add(TEXT("STAT_GPUFrameTime"));
        StatsToRecord.Add(TEXT("STAT_GameThreadTime"));
        
        PerfMonitor.StartRecordingPerfTimers(TEXT("PerfTest_Output.csv"), StatsToRecord);
    }
}
```

### 进阶用法

配置录制间隔和停止录制：

```cpp
#include "PerformanceMonitor.h"

FPerformanceMonitorModule& PerfMonitor = FPerformanceMonitorModule::Get();

// 设置采样间隔（秒），默认可能较短
PerfMonitor.SetRecordInterval(0.5f); // 每 0.5 秒记录一次

// 手动触发一帧数据记录（通常由 Tick 自动处理）
PerfMonitor.RecordFrame();

// 停止录制，触发数据汇总和文件最终化
PerfMonitor.StopRecordingPerformanceTimers();
```

## Demo 示例

```cpp
// MyPerfTest.h
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "MyPerfTest.generated.h"

UCLASS()
class MYGAME_API UMyPerfTestSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

    UFUNCTION(BlueprintCallable, Category = "Performance")
    void StartPerfCapture(const FString& OutputPath);

    UFUNCTION(BlueprintCallable, Category = "Performance")
    void StopPerfCapture();
};
```

```cpp
// MyPerfTest.cpp
#include "MyPerfTest.h"
#include "PerformanceMonitor.h"

void UMyPerfTestSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
}

void UMyPerfTestSubsystem::Deinitialize()
{
    // 确保退出时停止录制
    if (FPerformanceMonitorModule::IsAvailable() &&
        FPerformanceMonitorModule::Get().IsRecordingPerfTimers())
    {
        FPerformanceMonitorModule::Get().StopRecordingPerformanceTimers();
    }
    Super::Deinitialize();
}

void UMyPerfTestSubsystem::StartPerfCapture(const FString& OutputPath)
{
    if (!FPerformanceMonitorModule::IsAvailable())
    {
        UE_LOG(LogTemp, Warning, TEXT("PerformanceMonitor module not available"));
        return;
    }

    FPerformanceMonitorModule& PerfMon = FPerformanceMonitorModule::Get();
    if (PerfMon.IsRecordingPerfTimers())
    {
        UE_LOG(LogTemp, Warning, TEXT("Already recording performance data"));
        return;
    }

    TArray<FString> Stats;
    Stats.Add(TEXT("STAT_FrameTime"));
    Stats.Add(TEXT("STAT_GameThreadTime"));
    Stats.Add(TEXT("STAT_RenderThreadTime"));
    Stats.Add(TEXT("STAT_GPUFrameTime"));

    PerfMon.StartRecordingPerfTimers(OutputPath, Stats);
    UE_LOG(LogTemp, Log, TEXT("Started performance capture to: %s"), *OutputPath);
}

void UMyPerfTestSubsystem::StopPerfCapture()
{
    if (FPerformanceMonitorModule::IsAvailable() &&
        FPerformanceMonitorModule::Get().IsRecordingPerfTimers())
    {
        FPerformanceMonitorModule::Get().StopRecordingPerformanceTimers();
        UE_LOG(LogTemp, Log, TEXT("Performance capture stopped and file finalized"));
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine 等） | |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-03-16 | `1f05dc85` | Adding includes before upcoming header cleanup. | 为即将到来的头文件清理添加必要的 include 引用 |
| 2026-03-15 | `2caebd20` | Add more missing includes and forward declarations for various rendering headers | 补充缺失的头文件引用和前向声明 |
| 2025-09-12 | `fd5c41be` | Addressing instances "ignoring return value of function declared with 'nodiscard' attribute" issue f | 修复 nodiscard 属性相关的编译警告 |
| 2025-04-23 | `b6f496e4` | Remove timestamp-based dynamic resolution heuristic method | 移除基于时间戳的动态分辨率启发式方法 |
| 2025-03-14 | `9ccff8c3` | [Backout] - CL40651793 - needs further discussing | 回滚一次改动，需要进一步讨论 |

### 维护评价

PerformanceMonitor 是一个功能完整但较为简单的工具插件，自 2017 年创建以来一直作为 Runtime 模块存在。近期更新均为**编译维护性改动**（头文件清理、警告修复、代码回滚），没有任何功能性增强。

**关键观察**：
- 最近 2 年内无实质性功能更新
- 该插件默认禁用，属于冷门工具
- 插件规模极小（仅 2 个源文件），维护负担低
- `Win32` 平台在早期版本已被排除支持（CL 3265330）

⚠️ **注意**：该插件超过 8 年未有实质性功能更新，属于 Epic 内部遗留工具。虽然仍能编译，但可能不适用于新项目。如果需要性能数据收集，建议考虑 Unreal Insights（UE5 内置的现代化性能分析工具）作为替代方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Performance/PerformanceMonitor)