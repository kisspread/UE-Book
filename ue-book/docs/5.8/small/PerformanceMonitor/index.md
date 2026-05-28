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

PerformanceMonitor 是一个轻量级的运行时性能数据采集插件，主要用于**自动化性能测试**和**性能数据记录**。

与 Unreal Insights 或 Stat 命令等交互式分析工具不同，这个插件的设计目标是在**无人值守的自动化场景**中工作：它可以按设定的时间间隔自动采集指定的性能计时器数据，将结果输出为 CSV 文件，并支持采集指定帧数后自动停止、自动退出等流程控制。

**典型使用场景**：QA 团队在 CI 流水线中运行游戏，使用 PerformanceMonitor 记录特定地图的帧时间、GPU 耗时等指标，生成 CSV 用于回归分析和性能基准对比。

## 使用场景

- 你在 CI/CD 流水线中需要自动采集性能基准数据，输出 CSV 用于对比分析
- 你需要在特定地图上录制一段时间的性能数据，用于性能回归测试
- 你需要一个简单的命令行接口来启动/停止性能录制，而非交互式调试工具

## 蓝图用法

本插件不公开任何蓝图 API。所有功能通过**控制台命令**访问。

### 控制台命令

在运行时输入 `PerformanceMonitor help` 可查看完整用法说明。

常用命令格式：

```
PerformanceMonitor help                    # 查看帮助信息
PerformanceMonitor start <文件名> <统计项1> <统计项2> ...  # 开始录制
PerformanceMonitor stop                    # 停止录制并输出 CSV
```

录制过程中的关键控制参数：

| 参数 | 说明 |
|---|---|
| 录制间隔 | 通过 `SetRecordInterval` 控制采样频率 |
| 采集帧数 | 设置 `NumOfFramesToCapture`，达到帧数后自动停止 |
| 超时时间 | 设置 `TestTimeOut`，超时后自动停止 |
| 目标地图 | 设置 `MapToTest`，仅在指定地图生效 |
| 自动退出 | 设置 `bExitOnCompletion`，录制完成后自动退出进程 |

## C++ 用法

本插件没有公开的 API 接口，所有功能封装在模块内部，通过控制台命令驱动。

### 头文件引入

```cpp
#include "PerformanceMonitor.h"
```

### 基本用法

本插件的典型使用方式是通过控制台变量和命令在打包后的游戏中触发录制：

```cpp
// 通过控制台命令启动录制（在游戏运行时）
// 控制台输入: PerformanceMonitor start MyPerfTest FrameTime GameThread RenderThread
// 这会将 FrameTime、GameThread、RenderThread 等统计项录制到 CSV 文件

// 模块内部工作流程（来自 PerformanceMonitor/Private/PerformanceMonitor.h）：
// 1. StartRecordingPerfTimers() 设置文件名和要采集的统计项
// 2. Tick() 按 TimeBetweenRecords 间隔调用 RecordFrame()
// 3. RecordFrame() 从统计线程获取帧数据
// 4. 达到 NumOfFramesToCapture 或 TestTimeOut 后自动停止
// 5. StopRecordingPerformanceTimers() 输出最终 CSV 并清理资源
```

### 进阶用法

从源码可以看到，该模块支持 CVS Tools 模式的数据录制：

```cpp
// 来源: PerformanceMonitor/Private/PerformanceMonitor.h
// 模块支持两种录制模式：
// - 标准模式: 数据通过 FArchive 写入 CSV 文件
// - CVS Tools 模式: 数据通过 RecordDataInCvsToolsMode() 处理（bCvsToolsMode = true）

// 内部使用 STATS 宏保护的统计消息存储
#if STATS
    TArray<TArray<FStatMessage>> StoredMessages;
    TArray<FStatMessage> ReceivedFramePayload[10];  // 环形缓冲区存储帧数据
#endif
```

## Demo 示例

本插件不提供可复用的类或函数，其唯一入口是通过控制台命令。以下是在打包游戏中使用的最小流程：

```cpp
// 无需编写代码。在游戏控制台中执行：
// PerformanceMonitor start BenchmarkTest FrameTime GameThread RenderThread
// 等待录制完成（或手动 stop）
// 输出的 CSV 文件位于 LogFileName 指定的路径
```

若需在 C++ 中程序化触发，可访问模块实例：

```cpp
#include "PerformanceMonitor.h"

// 检查模块是否可用并启动录制
if (FPerformanceMonitorModule::IsAvailable())
{
    FPerformanceMonitorModule& PerfMon = FPerformanceMonitorModule::Get();
    if (!PerfMon.IsRecordingPerfTimers())
    {
        TArray<FString> StatsToRecord = { TEXT("FrameTime"), TEXT("GameThread"), TEXT("RenderThread") };
        PerfMon.StartRecordingPerfTimers(TEXT("MyBenchmark"), StatsToRecord);
        PerfMon.SetRecordInterval(1.0f);  // 每秒采集一次
    }
}
```

## 模块依赖

本插件模块依赖极为精简，仅依赖标准引擎核心模块，无特殊依赖。

无特殊依赖（仅标准 Core/Engine/Slate 等）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-03-16 | `1f05dc85` | Adding includes before upcoming header cleanup. | 添加头文件包含，为即将进行的头文件清理做准备 |
| 2026-03-15 | `2caebd20` | Add more missing includes and forward declarations for various rendering headers to files that have | 补充缺失的头文件包含和前向声明 |
| 2025-09-12 | `fd5c41be` | Addressing instances "ignoring return value of function declared with 'nodiscard' attribute" issue f | 修复 nodiscard 属性返回值被忽略的编译警告 |
| 2025-04-23 | `b6f496e4` | Remove timestamp-based dynamic resolution heuristic method | 移除基于时间戳的动态分辨率启发式方法 |
| 2025-03-14 | `9ccff8c3` | [Backout] - CL40651793 - needs further discussing | 回退一个变更，需要进一步讨论 |

### 维护评价

- **创建时间**：2017 年 1 月，已存在约 9 年
- **维护状态**：**低活跃维护**。近期所有提交均为被动维护性质（头文件清理、编译警告修复），没有任何功能性更新
- **最后一次实质性功能更新**：约 2017 年（初始版本），此后从未添加新功能
- **代码规模**：极小（仅 1 个 .h + 1 个 .cpp），说明此插件功能非常基础
- **默认启用**：否（`EnabledByDefault: false`），需手动启用

⚠️ **注意**：此插件自 2017 年创建以来从未有过功能增强，是一个极其简单的 CSV 性能数据采集工具。对于现代 UE5 项目，Unreal Insights 提供了远比此插件强大的性能分析能力。此插件可能仅在某些遗留 CI 流水线中仍有使用价值。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Performance/PerformanceMonitor)