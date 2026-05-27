# Performance Monitor

> A plugin for tracking the value of certain timers during gameplay.

| 属性 | 值 |
|---|---|
| 中文名 | 性能监视器 |
| 分类 | Performance |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PerformanceMonitor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2017-01-27 |
| 年龄标签 | 🏛️ 文物（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Performance/PerformanceMonitor) | |

## 用途

PerformanceMonitor 是一个运行时性能数据采集工具，专为自动化性能测试和回归测试场景设计。它通过 Unreal 的 Stat 系统捕获指定计时器的帧级数据（平均值、最大值），并将结果输出为 CSV 文件。

与引擎内置的 `stat` 控制台命令不同，该插件面向**程序化使用**场景：你可以通过控制台命令设定要采集哪些 Stats、采集多少帧、采集间隔是多少，插件会在后台自动收集数据，采集完毕后自动输出 CSV 报告。这使得它非常适合集成到 CI/CD 流水线中进行自动化性能回归检测。

## 使用场景

- 你需要在 CI 管道中自动运行性能基准测试，采集帧时间、DrawCall 等指标并输出 CSV 报告
- 你需要程序化地控制"录制哪些 Stat、录制多少帧、间隔多久采集一次"，而非手动在屏幕上观察
- 你需要在特定地图中运行自动化性能采集，并在完成后自动退出（`-exitoncompletion`）

## 蓝图用法

该插件没有暴露任何蓝图 API。所有功能通过控制台命令（Console Commands）访问。

### 控制台命令

| 命令 | 说明 |
|---|---|
| `PerformanceMonitor help` | 显示使用帮助和所有可用命令 |
| `PerformanceMonitor start <文件名> <Stat名1> <Stat名2> ...` | 开始录制指定的 Stats 到 CSV 文件 |
| `PerformanceMonitor stop` | 停止录制并输出 CSV 报告 |
| `PerformanceMonitor setinterval <秒>` | 设置采集间隔时间 |

### 使用示例（命令行）

```bash
# 启动游戏并运行性能采集（通过命令行参数）
UE5Editor.exe MyProject MyMap -game -ExecCmds="PerformanceMonitor start perf_report stat.frametime stat.drawcall" -FPS=60 -nomovie

# 或在运行时通过控制台手动触发
# 1. 打开控制台 (~)
# 2. 输入: PerformanceMonitor start MyPerfTest Stat.FPS Stat.DrawCall
# 3. 等待采集完成后自动生成 CSV 文件
```

## C++ 用法

该插件的 C++ 接口完全封装在 `FPerformanceMonitorModule` 中，通过模块单例访问。

### 头文件引入

```cpp
#include "PerformanceMonitor.h"
```

### 基本用法

通过模块单例控制录制流程：

```cpp
// 获取模块实例
FPerformanceMonitorModule& PerfMonitor = FPerformanceMonitorModule::Get();

// 检查模块是否可用
if (FPerformanceMonitorModule::IsAvailable())
{
    // 定义要采集的 Stats 列表
    TArray<FString> StatsToRecord;
    StatsToRecord.Add(TEXT("stat.frametime"));
    StatsToRecord.Add(TEXT("stat.drawcall"));
    StatsToRecord.Add(TEXT("GameThread"));

    // 开始录制（指定输出文件名和要采集的 Stats）
    PerfMonitor.StartRecordingPerfTimers(TEXT("MyPerfReport"), StatsToRecord);
}
```

### 进阶用法

配置录制参数和手动停止：

```cpp
FPerformanceMonitorModule& PerfMonitor = FPerformanceMonitorModule::Get();

// 设置采集间隔（秒），避免每帧都采集
PerfMonitor.SetRecordInterval(1.0f);

// 开始录制
TArray<FString> StatsToRecord;
StatsToRecord.Add(TEXT("RenderThread"));
StatsToRecord.Add(TEXT("GPU"));
PerfMonitor.StartRecordingPerfTimers(TEXT("GPU_Benchmark"), StatsToRecord);

// 在某个条件满足时停止录制
if (ShouldStopRecording())
{
    PerfMonitor.StopRecordingPerformanceTimers();
    // 内部会自动调用 FinalizeFTestPerfReport() 输出 CSV 并清理文件句柄
}

// 检查当前是否正在录制
if (PerfMonitor.IsRecordingPerfTimers())
{
    // 录制中...
}
```

## Demo 示例

以下是一个自定义性能测试辅助类，封装了 PerformanceMonitor 的常用功能：

```cpp
// MyPerfTestHelper.h
#pragma once

#include "CoreMinimal.h"

class FMyPerfTestHelper
{
public:
    // 启动性能采集
    static bool StartCapture(const FString& ReportName, const TArray<FString>& StatsToTrack, float Interval = 1.0f);

    // 停止采集并生成报告
    static void StopCapture();

    // 是否正在采集
    static bool IsCapturing();
};
```

```cpp
// MyPerfTestHelper.cpp
#include "MyPerfTestHelper.h"
#include "PerformanceMonitor.h"

bool FMyPerfTestHelper::StartCapture(const FString& ReportName, const TArray<FString>& StatsToTrack, float Interval)
{
    if (!FPerformanceMonitorModule::IsAvailable())
    {
        UE_LOG(LogTemp, Error, TEXT("PerformanceMonitor plugin is not loaded!"));
        return false;
    }

    FPerformanceMonitorModule& PerfMonitor = FPerformanceMonitorModule::Get();

    // 设置采集间隔
    PerfMonitor.SetRecordInterval(Interval);

    // 开始录制
    PerfMonitor.StartRecordingPerfTimers(ReportName, StatsToTrack);

    UE_LOG(LogTemp, Log, TEXT("Performance capture started: %s"), *ReportName);
    return true;
}

void FMyPerfTestHelper::StopCapture()
{
    if (!FPerformanceMonitorModule::IsAvailable())
    {
        return;
    }

    FPerformanceMonitorModule& PerfMonitor = FPerformanceMonitorModule::Get();

    if (PerfMonitor.IsRecordingPerfTimers())
    {
        PerfMonitor.StopRecordingPerformanceTimers();
        UE_LOG(LogTemp, Log, TEXT("Performance capture stopped and CSV report generated."));
    }
}

bool FMyPerfTestHelper::IsCapturing()
{
    if (!FPerformanceMonitorModule::IsAvailable())
    {
        return false;
    }

    return FPerformanceMonitorModule::Get().IsRecordingPerfTimers();
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-03-16 | `1f05dc85` | Adding includes before upcoming header cleanup. | 为即将进行的头文件清理预先添加必要的 include |
| 2026-03-15 | `2caebd20` | Add more missing includes and forward declarations for various rendering headers to files that have | 补充缺失的头文件引用和前向声明以解决编译问题 |
| 2025-09-12 | `fd5c41be` | Addressing instances "ignoring return value of function declared with 'nodiscard' attribute" issue f | 修复 [[nodiscard]] 属性函数返回值未使用导致的警告 |
| 2025-04-23 | `b6f496e4` | Remove timestamp-based dynamic resolution heuristic method | 移除基于时间戳的动态分辨率启发式方法（非本插件直接改动） |
| 2025-03-14 | `9ccff8c3` | [Backout] - CL40651793 - needs further discussing | 回退一个需要进一步讨论的变更（非本插件直接改动） |

### 维护评价

⚠️ **该插件自 2017 年创建以来，从未有过功能性更新。**

- **创建时间**：2017 年 1 月，已近 9 年
- **最后实质性更新**：2017 年 1 月（初始提交），此后无任何功能变更
- **近期改动**：均为全引擎范围的头文件清理和编译警告修复，不是针对性的功能更新
- **代码规模**：仅 2 个源文件，功能非常有限
- **默认状态**：`EnabledByDefault=false`，需手动启用

该插件本质上是一个简单的开发辅助工具，功能范围窄但完成度尚可。它仍能正常编译运行，但 Epic 似乎已经不再积极维护。如果你需要更现代的性能分析能力，建议使用 Unreal Insights（引擎内置的性能分析工具），它提供了远超此插件的采集粒度和分析能力。

**推荐**：仅在需要简单 CSV 输出的自动化测试场景中使用，其他场景优先选择 Unreal Insights。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Performance/PerformanceMonitor)
- 官方文档：无