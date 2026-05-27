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

PerformanceMonitor 是一个**运行时性能数据采集工具**，用于在游戏运行过程中自动记录各类性能计时器（stat）的数值，并输出为 CSV 格式的文本文件。

与内置的 `stat` 命令不同，这个插件专注于：
- **自动化采集**：按可配置的时间间隔自动记录性能数据，无需手动截图
- **批量导出**：将数据直接写入 CSV 文件，便于后续用 Excel 或 Python 分析
- **CI/CD 集成**：支持设置超时自动退出（`bExitOnCompletion`），适合在自动化测试流水线中使用

插件本身默认不启用，是一个面向开发和 QA 团队的辅助工具。

## 使用场景

- 你需要在连续的游戏流程中收集帧率、渲染耗时等性能指标 → 用 PerformanceMonitor 自动记录到 CSV
- 你在做性能回归测试，需要对比两个版本的性能数据 → 让插件输出 CSV 后用脚本 diff
- 你在 CI 流水线中跑自动化性能测试，希望跑完后自动退出 → 使用 `bExitOnCompletion` 模式
- 你需要在特定地图上跑固定时长的性能基准测试 → 配合 `MapToTest` 和 `NumOfFramesToCapture`

## 蓝图用法

该插件**没有暴露任何蓝图接口**。所有功能通过控制台命令（Console Command）访问。

### 控制台命令

启用插件后，在控制台输入 `PerformanceMonitor help` 查看详细用法。

| 命令 | 说明 |
|---|---|
| `PerformanceMonitor help` | 显示使用帮助 |
| `PerformanceMonitor start` | 开始录制性能数据 |
| `PerformanceMonitor stop` | 停止录制并写入文件 |

录制的数据会写入 `Saved/Profiling/` 目录下的 CSV 文件。

## C++ 用法

### 头文件引入

```cpp
#include "PerformanceMonitor.h"
```

### 基本用法

该插件的核心类是 `FPerformanceMonitorModule`，它同时实现了 `IModuleInterface` 和 `FSelfRegisteringExec`（注册控制台命令）。

```cpp
// 检查插件是否可用
if (FPerformanceMonitorModule::IsAvailable())
{
    // 获取插件实例
    FPerformanceMonitorModule& PerfMon = FPerformanceMonitorModule::Get();

    // 检查当前是否正在录制
    bool bRecording = PerfMon.IsRecordingPerfTimers();
}
```

### 进阶用法

通过 C++ 可以直接调用录制 API，无需通过控制台命令：

```cpp
FPerformanceMonitorModule& PerfMon = FPerformanceMonitorModule::Get();

// 配置录制参数
TArray<FString> StatsToRecord;
StatsToRecord.Add(TEXT("STAT_FrameTime"));
StatsToRecord.Add(TEXT("STAT_GameThreadTime"));
StatsToRecord.Add(TEXT("STAT_RenderThreadTime"));

PerfMon.SetRecordInterval(1.0f); // 每秒记录一次

// 开始录制，指定输出文件名
PerfMon.StartRecordingPerfTimers(TEXT("MyPerformanceLog"), StatsToRecord);

// ... 游戏运行中，插件会自动按间隔采集数据 ...

// 停止录制
PerfMon.StopRecordingPerformanceTimers();
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

该插件的 Build.cs 使用了标准的 `Core`、`CoreUObject`、`Engine`、`Stats` 等基础模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-03-16 | `1f05dc85` | Adding includes before upcoming header cleanup. | 为即将到来的头文件清理补充 include |
| 2026-03-15 | `2caebd20` | Add more missing includes and forward declarations for various rendering headers | 补充缺失的头文件包含和前向声明 |
| 2025-09-12 | `fd5c41be` | Addressing instances "ignoring return value of function declared with 'nodiscard' attribute" issue | 修复 nodiscard 属性相关的编译警告 |
| 2025-04-23 | `b6f496e4` | Remove timestamp-based dynamic resolution heuristic method | 移除基于时间戳的动态分辨率启发式方法 |
| 2025-03-14 | `9ccff8c3` | [Backout] - CL40651793 - needs further discussing | 回退一个需要进一步讨论的改动 |

### 维护评价

⚠️ **该插件维护不活跃，不推荐用于新项目。**

- **年龄**：2017 年创建，至今约 8 年
- **更新内容**：最近的提交全部是编译修复和头文件清理，没有任何功能性更新
- **活跃程度**：最后一次功能性改动（移除 dynamic resolution 启发式）也不是核心功能，且已回退
- **代码规模**：仅 2 个源文件（1 个头文件 + 1 个实现文件），功能非常有限
- **推荐程度**：作为 Epic 内部遗留工具仍可使用，但对于新项目建议使用 Unreal Insights 等更现代的性能分析工具。Unreal Insights 提供了更强大的数据采集、可视化和分析能力。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Performance/PerformanceMonitor)
- 官方文档：无