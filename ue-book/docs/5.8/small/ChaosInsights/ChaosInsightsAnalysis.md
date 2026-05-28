# Chaos Insights

> Plugin to gather insights into Chaos

| 属性 | 值 |
|---|---|
| 中文名 | Chaos 物理锁洞察 |
| 分类 | Insights |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ChaosInsightsAnalysis` (EditorAndProgram), `ChaosInsightsUI` (EditorAndProgram) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-11 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosInsights) | |

## 用途

ChaosInsights 是 **Unreal Insights** 的扩展插件，专门用于分析 Chaos 物理引擎的**锁竞争问题**。

在多线程物理模拟中，物理场景的主锁（Physics Scene Lock）是高频竞争的瓶颈：
- **读锁（Read Lock）**：物理查询（Query）需要获取读锁来访问场景数据
- **写锁（Write Lock）**：游戏线程移动组件或同步物理模拟结果时需要获取写锁

当工作线程持有锁的时间过长（例如运行大量查询），或在游戏线程需要移动组件/同步物理模拟的时间窗口内持锁，就会导致游戏线程卡顿。这类问题通常很难通过常规手段发现。

本插件通过在 Unreal Insights 的 Trace 捕获中启用 `ChaosLocks` 通道，可视化所有尝试获取物理场景锁的线程行为，帮助开发者定位锁竞争问题。它分别显示读锁和写锁，并清晰展示线程等待锁的时间，同时报告每个锁区域内的递归锁获取次数（用于分析操作密度）。

## 使用场景

- 你的游戏使用 Chaos 物理引擎且遇到间歇性卡顿 → 用本插件检查物理锁竞争
- 你在多线程环境中进行大量物理查询（射线检测、重叠检测等）→ 验证查询是否阻塞游戏线程
- 你需要分析物理模拟的同步阶段是否有瓶颈 → 可视化锁等待模式
- 你在优化物理性能但找不到瓶颈来源 → 启用 ChaosLocks 通道进行详细分析

**重要**：本插件仅在 **Unreal Insights 应用程序**（独立分析工具）和 **Editor** 中加载（`ProgramAllowList: ["UnrealInsights"]`），不会在打包的游戏运行时加载。

## 蓝图用法

本插件是 Unreal Insights 的 Trace 分析扩展，不包含任何蓝图可调用接口。所有功能均在 Unreal Insights 应用程序的 Timing View 中呈现。

### 使用方式（Insights 操作步骤）

1. 在你的项目中启用 Trace 捕获，并勾选 `ChaosLocks` 通道
2. 录制一段包含物理操作的游戏运行数据
3. 在 Unreal Insights 中打开捕获文件
4. Timing View 中会出现 Chaos Lock 区域，每条 Lane 代表一个线程的锁状态
5. 蓝色区域为读锁持有时间，红色区域为写锁持有时间
6. 线程等待锁的时间会以不同颜色标注，便于识别阻塞点

## C++ 用法

本插件的 C++ API 面向 **Insights 分析扩展开发者**，用于读取和扩展物理锁分析数据。

### 头文件引入

```cpp
#include "ChaosInsightsAnalysis/Model/LockRegions.h"
```

### 基本用法

通过 `LockRegions.h` 中的公共 API 访问锁区域分析数据。

```cpp
#include "ChaosInsightsAnalysis/Model/LockRegions.h"

// 在 Insights 分析会话中获取锁区域数据提供者
const ChaosInsightsAnalysis::ILockRegionProvider& Provider = 
    ChaosInsightsAnalysis::ReadRegionProvider(AnalysisSession);

// 获取总区域数和 Lane 数
uint64 TotalRegions = Provider.GetRegionCount();
int32 LaneCount = Provider.GetLaneCount();

// 遍历指定时间范围内的锁区域
Provider.ForEachRegionInRange(StartTime, EndTime, 
    [](const ChaosInsightsAnalysis::FLockRegion& Region) -> bool
    {
        // 判断是否为写锁
        bool bIsWriteLock = Region.bIsWrite;
        
        // 获取锁的等待时间（从尝试获取到实际获得）
        double WaitDuration = Region.AcquireTime - Region.BeginTime;
        
        // 获取锁的持有时间（从获得到释放）
        double HoldDuration = Region.EndTime - Region.AcquireTime;
        
        // 获取递归锁计数
        int32 RecursiveLockCount = Region.LockCount;
        
        // 获取持锁线程
        const TCHAR* ThreadName = Region.Text;
        uint64 ThreadId = Region.Thread;
        
        return true; // 返回 true 继续遍历，false 停止
    });
```

*来源: `Public/ChaosInsightsAnalysis/Model/LockRegions.h`*

### 进阶用法

遍历所有 Lane 并分别分析每个线程的锁行为：

```cpp
// 按 Lane 遍历所有线程的锁数据
Provider.ForEachLane(
    [](const ChaosInsightsAnalysis::FLockRegionLane& Lane, const int32 LaneIndex) -> void
    {
        // 获取该 Lane 的区域总数
        int32 RegionCount = Lane.Num();
        
        // 遍历该线程在指定时间范围内的所有锁区域
        Lane.ForEachRegionInRange(0.0, MaxTime,
            [&LaneIndex](const ChaosInsightsAnalysis::FLockRegion& Region) -> bool
            {
                if (Region.bIsWrite && Region.AcquireTime - Region.BeginTime > 0.001)
                {
                    // 发现写锁等待超过 1ms 的情况，可能是性能瓶颈
                    UE_LOG(LogTemp, Warning, 
                        TEXT("Lane %d: Write lock waited %.3fms"), 
                        LaneIndex, 
                        (Region.AcquireTime - Region.BeginTime) * 1000.0);
                }
                return true;
            });
    });
```

*来源: `Public/ChaosInsightsAnalysis/Model/LockRegions.h`*

## Demo 示例

以下示例展示如何创建一个简单的锁区域分析器，在分析会话中统计锁竞争情况。

**ChaosLockAnalyzer.h**:

```cpp
#pragma once

#include "ChaosInsightsAnalysis/Model/LockRegions.h"
#include "TraceServices/AnalysisService.h"

// 自定义的锁统计分析器
class FChaosLockStatsAnalyzer
{
public:
    struct FLockStats
    {
        int32 TotalReadLocks = 0;
        int32 TotalWriteLocks = 0;
        double MaxWaitTime = 0.0;
        double TotalHoldTime = 0.0;
    };

    static FLockStats AnalyzeSession(const TraceServices::IAnalysisSession& Session, 
                                      double StartTime, double EndTime)
    {
        using namespace ChaosInsightsAnalysis;
        
        FLockStats Stats;
        const ILockRegionProvider& Provider = ReadRegionProvider(Session);
        
        Provider.ForEachRegionInRange(StartTime, EndTime,
            [&Stats](const FLockRegion& Region) -> bool
            {
                double WaitTime = Region.AcquireTime - Region.BeginTime;
                double HoldTime = Region.EndTime - Region.AcquireTime;
                
                if (Region.bIsWrite)
                {
                    Stats.TotalWriteLocks++;
                }
                else
                {
                    Stats.TotalReadLocks++;
                }
                
                if (WaitTime > Stats.MaxWaitTime)
                {
                    Stats.MaxWaitTime = WaitTime;
                }
                
                Stats.TotalHoldTime += HoldTime;
                return true;
            });
        
        return Stats;
    }
};
```

## 模块依赖

从源码头文件分析，本插件依赖以下 Unreal Insights 专用模块：

| 模块 | 用途 |
|---|---|
| `TraceServices` | Insights 分析会话、线性分配器、分页数组、提供者接口 |
| `TraceAnalysis` | Trace 事件分析器基类 `UE::Trace::IAnalyzer` |

无其他特殊依赖（仅标准 Core/Engine 等基础模块）。

> **注意**：本插件的模块类型为 `EditorAndProgram`，且通过 `ProgramAllowList` 限制为仅在 `UnrealInsights` 程序中加载。你的模块若要依赖本插件，也必须在 Insights 程序上下文中构建。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移至 UE_LOGF 新接口 |
| 2025-05-30 | `20572801` | Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of ty | 修复 DLL 导出声明，确保 dllexport 正确标注在方法上 |
| 2025-04-30 | `e9656f2e` | [Insights] Chaos Insights: Fixed crash due to usage of a ITimingViewSession pointer after the Timing View is destroyed | 修复 Timing View 销毁后使用悬空指针导致的崩溃 |
| 2025-04-29 | `ee649d35` | Fix Unreal Insights Trace crashes after enabling and disabling the Timing Tab. | 修复反复启用/禁用 Timing 标签页时的崩溃问题 |
| 2025-04-11 | `7565ac94` | Added ChaosInsights module for Chaos related extensions to insights and implemented a physics scene lock profiler. | 初始提交，实现物理场景锁性能分析器 |

### 维护评价

- **创建时间**：2025-04-11，约 1 年前的新插件
- **近期活跃度**：2026-04 仍有更新（日志宏迁移），插件处于**活跃维护**状态
- **早期修复密集**：创建后 3 周内连续修复了 2 个崩溃问题，说明当时处于快速迭代阶段
- **稳定性**：2025-05 后无功能性变更，仅有代码质量改进（DLL 导出、日志宏迁移），表明功能已趋于稳定
- **实验性标记**：`IsBetaVersion=true`，仍标记为 Beta 版本
- **推荐使用**：✅ 推荐用于 Chaos 物理锁竞争分析。虽然是 Beta 状态，但功能完整且已有约 1 年的实际使用验证。注意它仅作为 Insights 扩展使用，不影响游戏运行时。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosInsights)
- [ChaosInsightsAnalysis 模块](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosInsights/Source/ChaosInsightsAnalysis)
- [ChaosInsightsUI 模块](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosInsights/Source/ChaosInsightsUI)
- [LockRegions 模型头文件](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/ChaosInsights/Source/ChaosInsightsAnalysis/Public/ChaosInsightsAnalysis/Model/LockRegions.h)