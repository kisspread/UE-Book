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
| 年龄标签 | 🏛️ 文物（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Performance/PerformanceMonitor) | |

## 用途

PerformanceMonitor 是一个轻量级运行时性能数据采集插件，专门用于**将游戏运行时的关键性能指标导出为 CSV 文件**，便于后续分析。

与内置的 `stat` 命令不同，这个插件的设计目标是：
- **自动化采集**：设定采集间隔和时长，自动记录多帧数据
- **可消费格式**：输出 CSV，可直接导入 Excel 或数据分析工具
- **定向追踪**：只记录你关心的特定统计指标，避免数据噪声
- **CI/CD 集成**：支持指定地图、超时退出、完成后自动退出，适合性能回归测试流水线

插件默认禁用（`EnabledByDefault: false`），需要手动启用后才能通过控制台命令使用。

## 使用场景

- 你需要**持续监控**某几项性能指标（如帧时间、DrawCall 数量），并在游戏运行一段时间后导出 CSV 报告
- 你在做**性能回归测试**，需要在 CI 流程中自动采集数据并与基准对比
- 你需要对比**不同地图或场景**的性能表现，为每个场景生成独立的 CSV 文件
- 你希望在**非编辑器环境**（打包后的游戏）中也能采集性能数据

## 蓝图用法

该插件**不暴露任何蓝图可调用接口**。所有功能通过控制台命令和 C++ API 访问。

### 控制台命令

插件注册了 `PerformanceMonitor` 控制台命令（通过 `FSelfRegisteringExec`），在游戏中输入：

```
PerformanceMonitor help
```

获取完整的命令用法说明。核心子命令包括启动采集、停止采集、设置间隔等。

## C++ 用法

### 头文件引入

```cpp
#include "PerformanceMonitorModule.h"
```

### 基本用法

通过模块单例接口访问所有功能：

```cpp
// 检查模块是否可用
if (FPerformanceMonitorModule::IsAvailable())
{
    FPerformanceMonitorModule& PerfMonitor = FPerformanceMonitorModule::Get();

    // 指定要记录的统计项和输出文件名
    TArray<FString> StatsToRecord;
    StatsToRecord.Add(TEXT("STAT_FrameTime"));
    StatsToRecord.Add(TEXT("STAT_DrawCalls"));

    // 开始录制（文件名不含路径，输出到 Profiling 目录）
    PerfMonitor.StartRecordingPerfTimers(TEXT("MyPerfTest"), StatsToRecord);

    // 设置录制间隔（秒）
    PerfMonitor.SetRecordInterval(1.0f);
}
```

### 停止录制并导出

```cpp
// 停止录制，自动清理文件句柄并生成报告
FPerformanceMonitorModule& PerfMonitor = FPerformanceMonitorModule::Get();
PerfMonitor.StopRecordingPerformanceTimers();
```

### 手动触发帧录制

```cpp
// 在自定义 Tick 中手动触发录制
FPerformanceMonitorModule& PerfMonitor = FPerformanceMonitorModule::Get();
if (PerfMonitor.IsRecordingPerfTimers())
{
    PerfMonitor.RecordFrame();
}
```

## Demo 示例

```cpp
// MyPerfTest.h
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "MyPerfTest.generated.h"

UCLASS()
class UMyPerfTestSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

    UFUNCTION(BlueprintCallable)
    void RunPerfCapture(float DurationSeconds);
};
```

```cpp
// MyPerfTest.cpp
#include "MyPerfTest.h"
#include "PerformanceMonitorModule.h"

void UMyPerfTestSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
}

void UMyPerfTestSubsystem::Deinitialize()
{
    // 确保关闭时停止录制
    if (FPerformanceMonitorModule::IsAvailable() &&
        FPerformanceMonitorModule::Get().IsRecordingPerfTimers())
    {
        FPerformanceMonitorModule::Get().StopRecordingPerformanceTimers();
    }
    Super::Deinitialize();
}

void UMyPerfTestSubsystem::RunPerfCapture(float DurationSeconds)
{
    if (!FPerformanceMonitorModule::IsAvailable())
    {
        UE_LOG(LogTemp, Warning, TEXT("PerformanceMonitor module not available"));
        return;
    }

    FPerformanceMonitorModule& PerfMonitor = FPerformanceMonitorModule::Get();

    // 配置要采集的统计项
    TArray<FString> StatsToRecord;
    StatsToRecord.Add(TEXT("STAT_FrameTime"));
    StatsToRecord.Add(TEXT("STAT_GameThread"));
    StatsToRecord.Add(TEXT("STAT_RenderThread"));
    StatsToRecord.Add(TEXT("STAT_DrawCalls"));

    // 设置采集参数
    PerfMonitor.SetRecordInterval(0.5f);  // 每0.5秒采集一次

    // 开始采集（文件名为时间戳）
    FString FileName = FString::Printf(TEXT("PerfCapture_%s"),
        *FDateTime::Now().ToString(TEXT("%Y%m%d_%H%M%S")));
    PerfMonitor.StartRecordingPerfTimers(FileName, StatsToRecord);

    // 延迟停止（在实际项目中可用 TimerManager 处理）
    FTimerHandle Handle;
    GetWorld()->GetTimerManager().SetTimer(Handle, [DurationSeconds]()
    {
        if (FPerformanceMonitorModule::IsAvailable())
        {
            FPerformanceMonitorModule::Get().StopRecordingPerformanceTimers();
            UE_LOG(LogTemp, Log, TEXT("Performance capture completed. CSV saved."));
        }
    }, DurationSeconds, false);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Stats` | 性能统计数据系统，插件通过 `#if STATS` 条件编译依赖此模块读取运行时统计数据 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-03-16 | `1f05dc85` | Adding includes before upcoming header cleanup. | 为即将到来的头文件清理预先添加 include |
| 2026-03-15 | `2caebd20` | Add more missing includes and forward declarations for various rendering headers to files that have | 补充缺失的 include 和前向声明 |
| 2025-09-12 | `fd5c41be` | Addressing instances "ignoring return value of function declared with 'nodiscard' attribute" issue f | 修复 nodiscard 返回值未使用警告 |
| 2025-04-23 | `b6f496e4` | Remove timestamp-based dynamic resolution heuristic method | 移除基于时间戳的动态分辨率启发式方法 |
| 2025-03-14 | `9ccff8c3` | [Backout] - CL40651793 - needs further discussing | 回退 CL40651793，需进一步讨论 |

### 维护评价

**⚠️ 维护不活跃，谨慎使用**

- **创建时间**：2017 年，已超过 9 年历史
- **代码规模**：仅 2 个源文件，功能非常有限
- **近期更新**：最近的 commit 全部是编译兼容性修复（添加 include、处理 nodiscard 警告），**没有功能性更新**
- **默认禁用**：`EnabledByDefault: false`，说明 Epic 并不认为这是一个面向所有用户的必备工具
- **历史背景**：最初由 Ben.Salem 在 2017 年作为"V0 版本"提交，从 commit 消息看此后基本没有迭代

该插件更像是一个内部调试工具，功能远不如 Unreal Insights 完善。如果你需要现代化的性能分析方案，建议使用 **Unreal Insights**（引擎内置的性能分析系统）或 **Automation 测试框架**中的性能测试能力。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Performance/PerformanceMonitor)