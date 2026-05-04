# External GPU Statistics

> Plugin to find out more detailed GPU usage for NVIDIA, AMD, and Intel GPUs.

| 属性 | 值 |
|---|---|
| 分类 | Rendering |
| 默认启用 | false |
| 包含内容 | false |
| 模块 | ExternalGPUStatistics (Runtime) |
| 创建时间 | 2025-05-29 |
| 年龄标签 | 🆕 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/ExternalGPUStatistics) | |

## 用途

通过各 GPU 厂商的专有 API（NVIDIA NVML、Intel Level Zero），直接从驱动层查询 GPU 的全局和当前进程级别的利用率、显存占用以及时钟频率缩放比例。查询结果通过 `RHIGetGPUUsage` 函数指针注入 RHI 层，使得引擎内置的统计图表（如 Stat GPU）和自动化测试（Horde CSV 输出）能显示真实的外部 GPU 负载数据——这些数据是引擎自身 GPU 时间戳无法反映的。

与 UE 内置的 `Stat GPU`（只统计引擎自身渲染命令耗时）不同，本插件能告诉你**整个 GPU**（包括其他进程）和**当前 UE 进程**分别占用了多少 GPU 算力，非常适合性能分析和自动化回归测试场景。

## 使用场景

- 你正在做 GPU 性能分析，想知道 UE 进程到底吃掉了多少 GPU 算力 → 启用本插件查看 `CurrentProcessMHz`
- 你在跑自动化性能测试，需要在 CSV 中记录 GPU 利用率趋势 → 启用后 Horde 自动采集 `FRHIGPUUsageFractions`
- 你怀疑有其他程序在抢 GPU 资源 → 查看 `ExternalProcessesMHz` 字段判断外部负载
- 你需要监控 GPU 时钟频率是否被节流 → 查看 `ClockScaling` 字段（1.0 = 满频）

## 蓝图用法

本插件不暴露任何 BlueprintCallable 函数或 BlueprintReadWrite 属性。它完全在引擎底层 RHI 层运作，通过 `RHIGetGPUUsage` 函数指针向引擎提供数据。用户无需在蓝图中直接操作。

## C++ 用法

### 头文件引入

```cpp
#include "RHI.h"           // FRHIGPUUsageFractions, RHIGetGPUUsage, GRHISupportsGPUUsage
#include "IExternalGPUStatistics.h" // 模块接口（通常不需要直接引用）
```

### 基本用法

插件启用后，通过全局函数指针 `RHIGetGPUUsage` 查询 GPU 使用情况：

```cpp
// 确认插件已成功初始化
if (GRHISupportsGPUUsage && RHIGetGPUUsage)
{
    // 查询 GPU 0 的使用数据（参数为 GPU 索引，多 GPU 时为 0, 1, 2...）
    FRHIGPUUsageFractions Usage = RHIGetGPUUsage(0);

    // 全局 GPU 利用率（0.0 ~ 1.0）
    float TotalGPUUtilization = Usage.ExternalProcessesMHz;

    // 当前进程 GPU 利用率（仅 NVIDIA 有效）
    float CurrentProcessUtilization = Usage.CurrentProcessMHz;

    // GPU 时钟频率缩放（1.0 = 满频运行）
    float ClockScaling = Usage.ClockScaling;
}
```

> 来源：`ExternalGPUStatistics.cpp` 中 `GetGPUUsage()` 函数（第 337-343 行）

### FRHIGPUUsageFractions 结构体字段说明

| 字段 | 类型 | 说明 |
|---|---|---|
| `ExternalProcessesMHz` | float | 其他进程的 GPU 利用率（0.0~1.0） |
| `CurrentProcessMHz` | float | 当前 UE 进程的 GPU 利用率（仅 NVIDIA） |
| `ExternalProcessMemoryUsage` | uint64 | 其他进程的显存占用（字节） |
| `CurrentProcessMemoryUsage` | uint64 | 当前进程的显存占用（字节） |
| `ClockScaling` | float | GPU 时钟频率缩放比例（1.0 = 最大频率） |

### 进阶用法

插件通过 Console Variable 控制行为：

| CVar | 默认值 | 说明 |
|---|---|---|
| `r.GPUStatistics` | 1 | 启用/禁用 GPU 统计采集（运行时可切换） |
| `r.GPUStatisticsPerProcess` | 1 | 启用/禁用每进程级别数据采集 |
| `r.GPUStatistics.SkipFrames` | 0 | 跳过多少帧再更新缓存（降低采集频率） |
| `r.GPUStatistics.Async` | 1 | 异步更新（使用后台线程，避免阻塞渲染线程） |

```cpp
// 运行时禁用
static IAutoConsoleCommand CmdDisable(
    TEXT("stat.DisableGPUStats"),
    TEXT(""),
    FConsoleCommandDelegate::CreateLambda([]()
    {
        // 通过控制台设置即可，插件会自动响应
        // 或直接在控制台输入: r.GPUStatistics 0
    })
);
```

## Demo 示例

本插件不需要用户编写额外代码。启用方式：

1. 在 `.uproject` 或编辑器的 Plugins 面板中启用 "External GPU Statistics"
2. 运行时在控制台输入 `stat gpu` 即可看到外部 GPU 数据
3. 通过 `r.GPUStatistics 1` 确认开启

```cpp
// Build.cs 中添加依赖（如果需要从其他模块访问模块接口）
PublicDependencyModuleNames.Add("ExternalGPUStatistics");
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础模块 |
| `Engine` | 引擎核心（私有依赖） |
| `RenderCore` | 渲染核心（私有依赖） |
| `RHI` | RHI 层接口（私有依赖） |
| `NVML` | NVIDIA Management Library（Win64/Linux x64，条件编译） |
| `oneAPILevelZero` | Intel Level Zero API（Win64/Linux x64，条件编译） |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-06-24 | `cd2fbce3` | fixup ExternalGPUStatistics for Windows Arm64 | 修复 Windows ARM64 平台兼容性 |
| 2025-06-16 | `41010344` | NVML - 检查进程利用率返回码；处理 0.25s 采样间隔导致的过期数据 | 修复 NVIDIA 进程级数据的准确性问题 |
| 2025-06-12 | `a37bd35f` | 移除 unattended 检查，因为自动化测试确实使用此功能 | 让插件在自动化测试环境中正常工作 |

### 维护评价

- **创建时间**：2025-05-29，不到 1 年的新插件
- **活跃度**：创建后一个月内连续 3 次功能性提交，处于活跃开发期
- **状态**：`IsExperimentalVersion: true`，`EnabledByDefault: false`——这是一个实验性插件
- **平台支持**：仅 Win64 和 Linux，Shipping 构建被排除
- **厂商支持**：NVIDIA（通过 NVML）和 Intel（通过 Level Zero）已实现；AMD 部分代码仅有空框架（`Setup AMD-SMI` 注释占位）
- **推荐**：适合在开发和测试环境中用于 GPU 性能分析，但因为是实验性插件且排除了 Shipping 构建，不建议在生产环境中依赖它

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/ExternalGPUStatistics)
- [官方文档]()（无）
