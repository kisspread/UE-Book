# PerformanceMonitor

> A plugin for tracking the value of certain timers during gameplay.

| 属性 | 值 |
|---|---|
| 分类 | Performance |
| 默认启用 | false |
| 包含内容 | false |
| 模块 | PerformanceMonitor (Runtime) |
| 创建时间 | 2017-01-26 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Performance/PerformanceMonitor) | |

## 用途

PerformanceMonitor 是一个**运行时性能数据录制工具**，用于在游戏运行期间按固定间隔采样帧时间等性能指标，并将结果导出为 CSV 文件。

它解决的核心问题是：**在自动化测试或长时间游戏会话中，持续记录 CPU/GPU 帧时间等关键性能数据**，以便事后分析。与 `stat unit` 等实时显示工具不同，PerformanceMonitor 专注于**离线数据采集和报告生成**，支持超时自动停止、指定帧数采集、异常值过滤等功能。

该插件没有公开的 C++ API 或蓝图接口——它完全通过 **控制台命令（Console Command）** 操作，设计上面向开发者和 QA 自动化流程。

> **注意**：2025 年 3 月曾有人尝试删除此插件（commit message: "Delete unused plugin (PerformanceMonitor) that outlived its purpose"），但该提交被回退。插件仍然存在，但可能处于半废弃状态。

## 使用场景

- 你需要在 CI/CD 流程中自动采集游戏帧时间数据并生成 CSV 报告 → 用 PerformanceMonitor
- 你需要长时间录制 GPU/CPU 帧时间用于性能回归检测 → 用 PerformanceMonitor
- 你想在控制台快速启停性能录制而不需要额外工具 → 用 PerformanceMonitor

## 蓝图用法

此插件**没有蓝图接口**。所有功能通过控制台命令访问。

## C++ 用法

此插件**没有公开头文件**（所有代码位于 `Private/` 目录），不提供可被外部模块直接调用的 C++ API。功能完全通过控制台命令暴露。

### 控制台命令

插件注册了 `PerformanceMonitor` 前缀的 Exec 命令，可在控制台或代码中通过 `GEngine->Exec()` 调用。

#### 基本流程

```
// 1. 添加要监控的计时器（可选）
PerformanceMonitor addtimer STAT_MyCustomTimer

// 2. 设置采样间隔（可选，默认 0.01 秒）
PerformanceMonitor setinterval 0.1

// 3. 开始录制（文件名参数必填）
PerformanceMonitor start MyPerfTest

// 4. 停止录制
PerformanceMonitor stop
```

#### 命令列表

| 命令 | 说明 |
|---|---|
| `PerformanceMonitor start <filename>` | 开始录制，数据保存到 `Saved/FXPerformance/<filename>.csv` |
| `PerformanceMonitor stop` | 停止录制并写入文件 |
| `PerformanceMonitor addtimer <timername>` | 添加自定义 stat 计时器名称 |
| `PerformanceMonitor setinterval <seconds>` | 设置采样间隔（浮点数，单位秒） |
| `PerformanceMonitor cvstoolsmode <true\|false>` | 切换 CSV 输出格式（CVS Tools 兼容模式） |

#### 预置采集指标

录制开始后，以下指标**自动采集**，无需手动添加：

| 指标名 | 说明 |
|---|---|
| `FrameTime` | 总帧时间 (ms) |
| `RenderThreadTime` | 渲染线程时间 (ms) |
| `GameThreadTime` | 游戏线程时间 (ms) |
| `GPUFrameTime` | GPU 帧时间 (ms) |
| `GlobalRenderThreadTime` | 全局渲染线程时间 (ms) |
| `GlobalGameThreadTime` | 全局游戏线程时间 (ms) |
| `GlobalGPUFrameTime` | 全局 GPU 帧时间 (ms) |

### Game.ini 配置

插件支持从 `Game.ini` 读取配置，节名为 `[PerformanceMonitor/<ProfileName>]`：

```ini
[/Plugins/PerformanceMonitor/MyPerfTest]
PerformanceMonitorInterval=0.1
PerformanceMonitorTimeout=60.0
PerformanceMonitorNumOfFramesToCapture=1000
PerformanceMonitorTimers=STAT_MyCustomTimer,STAT_AnotherTimer
PerformanceMonitorStatGroups=STATGROUP_Game,STATGROUP_Rendering
PerformanceMonitorMap=/Game/Maps/TestMap
PerformanceMonitorExitOnFinish=true
PerformanceMonitorRequireCutsceneStart=false
```

| 配置项 | 类型 | 说明 |
|---|---|---|
| `PerformanceMonitorInterval` | float | 采样间隔（秒） |
| `PerformanceMonitorTimeout` | float | 超时时间（秒），超时后自动停止 |
| `PerformanceMonitorNumOfFramesToCapture` | int | 采集帧数上限，达到后自动停止 |
| `PerformanceMonitorTimers` | string[] | 要监控的自定义 stat 计时器名称列表 |
| `PerformanceMonitorStatGroups` | string[] | 要启用的 stat 组（其余全部禁用以提高效率） |
| `PerformanceMonitorMap` | string | 测试完成后要加载的地图 |
| `PerformanceMonitorExitOnFinish` | bool | 录制完成后是否退出引擎 |
| `PerformanceMonitorRequireCutsceneStart` | bool | 录制开始时是否自动启动过场动画 (`ce start`) |

## Demo 示例

### 通过代码启动录制

由于没有公开 API，需通过 `Exec` 调用控制台命令：

```cpp
#include "Engine/Engine.h"

// 添加自定义计时器
GEngine->Exec(GetWorld(), TEXT("PerformanceMonitor addtimer STAT_MyWork"));

// 设置采样间隔
GEngine->Exec(GetWorld(), TEXT("PerformanceMonitor setinterval 0.1"));

// 开始录制
GEngine->Exec(GetWorld(), TEXT("PerformanceMonitor start MyBenchmarkRun"));

// ... 游戏运行中 ...

// 停止录制
GEngine->Exec(GetWorld(), TEXT("PerformanceMonitor stop"));
```

### 输出文件格式

**标准模式** 输出到 `Saved/FXPerformance/<filename>.csv`，包含两个部分：

```csv
Interval (s),0.1000
FrameTime,16.2340,16.4560,16.1230,...
RenderThreadTime,4.5670,4.8900,4.3210,...
...
Timer Name, Min Val, Max Val, Avg Val, Timer Active Frames
FrameTime,15.2340,18.4560,16.1230,600
RenderThreadTime,3.5670,6.8900,4.3210,600
...
```

**CVS Tools 模式** (`cvstoolsmode true`) 输出更简单的列式格式：

```csv
FrameTime,RenderThreadTime,GameThreadTime,...
16.2340,4.5670,3.4560,...
16.4560,4.8900,3.7890,...
```

### 异常值过滤

`GetAverageOfArray` 方法实现了异常值过滤逻辑：采集开始时的前几帧通常有较大波动（资源加载等），插件会自动检测并过滤掉**开头部分**超过均值 2 倍的异常值，同时在日志中输出被过滤的异常帧数量和最大异常值。

## 模块依赖

从 `PerformanceMonitor.Build.cs` 的 `PublicDependencyModuleNames` 提取：

| 模块 | 用途 |
|---|---|
| `Core` | 基础模块 |
| `CoreUObject` | 对象系统 |
| `Engine` | 引擎核心（World、GEngine 等） |
| `InputCore` | 输入核心 |
| `RHI` | 渲染硬件接口（获取 GPU 帧时间） |
| `RenderCore` | 渲染核心（渲染线程时间） |

> **注意**：由于此插件没有公开 API，外部模块不需要依赖它。它是一个自包含的运行时工具。

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-09-12 | `ce6ff392` | 修复 `FTSTicker::RemoveTicker` 的 nodiscard 属性警告 | 编译修复，非功能性更新 |
| 2025-04-23 | `b6f496e4` | 移除基于时间戳的动态分辨率启发式方法 | 间接影响，非插件本身功能更新 |
| 2025-03-14 | `9ccff8c3` | [Backout] 尝试删除此插件，被回退 | **重要信号**：有人认为此插件已过时，但删除被阻止 |

### 维护评价

- **创建时间**：2017 年 1 月，已存在约 9 年
- **最后实质性功能更新**：很久以前（近期仅有编译修复）
- **维护状态**：**可能废弃** — 2025 年 3 月的 "delete unused plugin" 提交（虽被回退）表明 Epic 内部已有人认为此插件已过时
- **代码质量**：代码较老，使用了 `#if STATS` 条件编译，部分函数注释掉了（如 `GetStatsBreakdown`），有遗留的 Orion/旧项目引用痕迹
- **是否推荐使用**：⚠️ **谨慎使用**。此插件功能有限且可能在未来版本中被移除。对于现代 UE5 项目，建议使用 Unreal Insights 或其他官方性能分析工具替代

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Performance/PerformanceMonitor)
- 官方文档：无（`.uplugin` 中 DocsURL 为空）
- 测试用例：无（未找到专用测试文件）
