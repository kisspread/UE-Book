# Chaos Insights

> Plugin to gather insights into Chaos

| 属性 | 值 |
|---|---|
| 中文名 | Chaos 洞察分析 |
| 分类 | Insights |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ChaosInsightsAnalysis` (EditorAndProgram), `ChaosInsightsUI` (EditorAndProgram) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-11 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosInsights) | |

## 用途

ChaosInsights 是 Chaos 物理引擎在 Unreal Insights 中的分析扩展插件。它解决了一个在多线程物理模拟中非常隐蔽但影响严重的性能问题——**物理场景锁争用（Physics Scene Lock Contention）**。

在 Chaos 物理引擎中，主线程和工作线程会竞争同一个物理场景锁。物理查询需要获取读锁，而任何对物体位置的更新需要获取写锁。当工作线程发起大量查询或长时间持锁时，游戏线程的移动组件操作或物理同步操作会被阻塞，导致明显的帧率卡顿。这类问题很难通过常规手段发现，因此 ChaosInsights 通过可视化锁区域来帮助开发者直观地定位这些瓶颈。

## 使用场景

- 你使用 Chaos 物理引擎，游戏出现不明原因的主线程卡顿 → 用 ChaosInsights 的锁争用分析来诊断是否是物理场景锁导致
- 你在开发多线程物理密集型场景（大量刚体、复杂碰撞查询）→ 在 Unreal Insights 中启用 `ChaosLocks` 通道捕获锁争用数据
- 你需要区分物理模拟中读锁和写锁的等待时间分布 → 用 ChaosInsights 的锁区域轨道来分别可视化读写锁状态
- 你想分析物理查询操作密度，了解每个锁区域内的递归锁数量 → 使用 ChaosInsights 的递归锁计数报告

## 蓝图用法

此插件不包含蓝图节点。它是一个纯 Insights 分析扩展，通过 Unreal Insights 的 Timing View 界面操作。

## C++ 用法

此插件作为 Unreal Insights 的扩展程序运行，主要面向引擎开发者。终端用户通过 Unreal Insights 捕获工具使用，无需直接编写 C++ 代码。

### 头文件引入

```cpp
#include "ChaosInsightsUIModule.h"
#include "LockRegionTrack.h"
```

### 基本用法

此插件不对外暴露用户级 C++ API。其核心功能通过 Unreal Insights 的 Timing View 扩展机制工作，用户只需在 Insights 捕获中启用 `ChaosLocks` 通道即可。

### 进阶用法

如需在自定义 Insights 扩展中复用锁区域分析能力，可参考 `FLockRegionsSharedState` 实现 `ITimingViewExtender` 接口的模式：

```cpp
// 参考 LockRegionTrack.h - FLockRegionsSharedState 的实现方式
class FMyCustomExtender : public UE::Insights::Timing::ITimingViewExtender
{
public:
    virtual void OnBeginSession(UE::Insights::Timing::ITimingViewSession& InSession) override
    {
        // 会话开始时注册自定义轨道
    }

    virtual void OnEndSession(UE::Insights::Timing::ITimingViewSession& InSession) override
    {
        // 会话结束时清理资源
    }

    virtual void Tick(UE::Insights::Timing::ITimingViewSession& InSession,
                      const TraceServices::IAnalysisSession& InAnalysisSession) override
    {
        // 每帧更新轨道数据
    }
};
```

## Demo 示例

此插件无需用户编写代码。使用步骤如下：

1. 确保插件已启用（默认已启用）
2. 在 Unreal Insights 捕获设置中启用 **`ChaosLocks`** 通道
3. 进行游戏/PIE 运行并捕获 Insights 数据
4. 在 Timing View 中查看新增的 **Lock Regions** 轨道
5. 轨道中会分别显示读锁（Read）和写锁（Write）区域，以及线程等待锁的时间段

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Insights` | Unreal Insights 框架，提供 TimingView 扩展接口和轨道渲染 |
| `TraceServices` | Trace 分析服务，提供 IAnalysisSession 用于读取追踪数据 |
| `ChaosInsightsAnalysis` | 本插件的分析模块，提供 FLockRegion 等数据结构供 UI 模块消费 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 批量迁移日志宏到新格式 UE_LOGF |
| 2025-05-30 | `20572801` | Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of ty | 修复 DLL 导出符号声明，确保宏应用在方法上而非类型 |
| 2025-04-30 | `e9656f2e` | [Insights] Chaos Insights: Fixed crash due to usage of a ITimingViewSession pointer after the Timing | 修复 TimingView 会话销毁后仍使用悬空指针导致的崩溃 |
| 2025-04-29 | `ee649d35` | Fix Unreal Insights Trace crashes after enabling and disabling the Timing Tab. | 修复反复开关 Timing Tab 导致的 Insights 崩溃问题 |
| 2025-04-11 | `7565ac94` | Added ChaosInsights module for Chaos related extensions to insights and implemented a physics scene lock profiler. | 初始提交，实现物理场景锁分析器和 Insights 扩展框架 |

### 维护评价

ChaosInsights 是一个 **较新且处于实验阶段** 的插件，创建于 2025 年 4 月。从提交历史看，开发初期（2025-04 至 2025-05）集中修复了会话生命周期管理相关的崩溃问题，说明这是一个刚投入使用的功能。最近一次更新（2026-04）是代码格式迁移，属于维护性改动。

**注意事项**：
- `IsBetaVersion=true`，属于实验性功能，API 和行为可能随版本变化
- 仅在 `UnrealInsights` 程序中加载，不参与游戏运行时或编辑器主程序
- 开发初期有多个崩溃修复，使用时需关注稳定性
- 推荐在物理性能调优场景中使用，但需注意其 beta 状态

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosInsights)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosInsights/Tests)（未发现独立测试文件）