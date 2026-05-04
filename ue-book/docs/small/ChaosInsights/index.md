# Chaos Insights

> Plugin to gather insights into Chaos

| 属性 | 值 |
|---|---|
| 分类 | Insights |
| 默认启用 | true |
| 包含内容 | false |
| 模块 | ChaosInsightsAnalysis (EditorAndProgram), ChaosInsightsUI (EditorAndProgram) |
| 创建时间 | 2025-04-11 |
| 年龄标签 | 🆕 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/ChaosInsights) | |

## 用途

ChaosInsights 是 Unreal Insights 的扩展插件，专门用于可视化 Chaos 物理引擎的锁竞争（lock contention）情况。它在 Unreal Insights 的 Timing 视图中添加一条名为 **"Physics Scene Locks"** 的轨道，以颜色编码的方式展示：

- 🔴 **红色**：线程正在等待获取锁（Wait Duration）
- 🟡 **黄色**：已获取读锁（Read Lock Acquired）
- 🟢 **绿色**：已获取写锁（Write Lock Acquired）

通过这个插件，开发者可以直观地看到物理模拟中各线程的锁等待和持有时长，快速定位物理场景锁竞争瓶颈。

## 使用场景

- 你正在开发高并发物理模拟的项目，发现物理线程有卡顿 → 用 ChaosInsights 分析锁等待时间
- 你需要排查 Chaos 物理引擎的性能瓶颈 → 用 Timing 视图查看锁区域分布
- 你需要优化多线程物理任务的调度 → 观察读锁与写锁的分布模式

## 蓝图用法

本插件不提供蓝图接口。它是一个纯 Editor/Program 级别的 Unreal Insights 扩展模块，仅在 UnrealInsights 程序中加载。

## C++ 用法

### 使用方式

本插件不需要在你的项目代码中直接调用。它的功能通过 Unreal Insights 的 Trace 系统自动工作：

1. **录制 Trace 数据**：在运行游戏/编辑器时启用 `Chaos` Trace Channel
2. **打开 Unreal Insights**：启动 UnrealInsights 程序并加载 .utrace 文件
3. **查看 Timing 视图**：自动出现 "Physics Scene Locks" 轨道

### Trace 事件

插件通过 Unreal Trace 系统接收以下 Chaos 锁事件（在 `Chaos` 通道下）：

| Trace 事件 | 说明 |
|---|---|
| `Chaos::LockAcquireBegin` | 线程开始尝试获取锁，包含 Cycle 时间戳和 bIsWrite 标志 |
| `Chaos::LockAcquired` | 线程成功获取锁，包含 Cycle 时间戳 |
| `Chaos::LockAcquireEnd` | 线程释放锁，包含 Cycle 时间戳 |

### 编程接口

如果你需要在自定义分析工具中读取锁区域数据，可以使用插件暴露的 Provider 接口：

```cpp
#include "ChaosInsightsAnalysis/Model/LockRegions.h"

// 从分析会话中获取只读的 LockRegion Provider
const ChaosInsightsAnalysis::ILockRegionProvider& Provider = 
    ChaosInsightsAnalysis::ReadRegionProvider(AnalysisSession);

// 遍历所有锁区域
TraceServices::FProviderReadScopeLock ScopedLock(Provider);
Provider.ForEachLane([&](const ChaosInsightsAnalysis::FLockRegionLane& Lane, int32 Depth)
{
    Lane.ForEachRegionInRange(StartTime, EndTime, 
        [](const ChaosInsightsAnalysis::FLockRegion& Region) -> bool
    {
        // Region.BeginTime   - 尝试获取锁的时间
        // Region.AcquireTime - 实际获取锁的时间
        // Region.EndTime     - 释放锁的时间
        // Region.bIsWrite    - 是否是写锁
        // Region.Thread      - 线程 ID
        return true; // 继续遍历
    });
});
```

#### FLockRegion 结构体字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `BeginTime` | `double` | 尝试获取锁的时间 |
| `AcquireTime` | `double` | 实际获取锁的时间（含等待） |
| `EndTime` | `double` | 释放锁的时间 |
| `Text` | `const TCHAR*` | 线程名称 |
| `Thread` | `uint64` | 线程本地 ID |
| `Depth` | `int32` | UI 显示深度 |
| `LockCount` | `int32` | 区域内锁获取次数 |
| `LockDepth` | `int32` | 锁嵌套深度（用于合并递归锁） |
| `bIsWrite` | `bool` | 是否为写锁（否则为读锁） |

## Demo 示例

### 在 Unreal Insights 中使用

```
1. 启动游戏并录制带 Chaos 通道的 Trace：
   > UnrealEditor.exe -trace=cpu,gpu,frame,bookmark,Chaos

2. 打开 UnrealInsights 并加载 .utrace 文件

3. 切换到 Timing 面板，找到 "Physics Scene Locks" 轨道

4. 鼠标悬停在锁区域上可查看：
   - Type: Read / Write
   - Wait Duration: 等待获取锁的时长
   - Exec Duration: 持有锁的时长
   - Max Lock Depth: 锁嵌套深度
```

## 模块依赖

本插件的模块依赖（**你不需要**在项目 Build.cs 中引用这些，除非要编写自定义 Trace 分析）：

### ChaosInsightsUI

| 模块 | 用途 |
|---|---|
| `Core` | 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `SlateCore` / `Slate` | UI 框架 |
| `InputCore` | 输入系统 |
| `TraceInsights` / `TraceInsightsCore` | Unreal Insights 框架 |
| `TraceServices` | Trace 分析服务 |
| `ChaosInsightsAnalysis` | 本插件的分析模块 |

### ChaosInsightsAnalysis

| 模块 | 用途 |
|---|---|
| `Core` | 核心基础库（Public） |
| `CoreUObject` | UObject 系统 |
| `TraceLog` | Trace 日志系统 |
| `TraceAnalysis` | Trace 分析框架 |
| `TraceServices` | Trace 分析服务 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-05-30 | `2057280165b3` | Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types. Part 1/n | 代码规范化，DLL 导出符号修正 |
| 2025-04-30 | `e9656f2efa7f` | Fixed crash due to usage of a ITimingViewSession pointer after the TimingView widget was destroyed | 修复了一个 use-after-destroy 崩溃 |
| 2025-04-29 | `ee649d354715` | Fix Unreal Insights Trace crashes after enabling and disabling the Timing Tab | 修复了 Timing Tab 开关导致的 Trace 崩溃 |

### 维护评价

- **状态**：🆕 实验性（IsBetaVersion=true）
- **创建时间**：2025-04-11，约 1 年前
- **活跃度**：活跃维护，2025 年 5 月仍有连续 bug 修复
- **注意事项**：
  - 标记为 Beta，API 可能变动
  - `SupportedPrograms` 仅限 `UnrealInsights`，不在主编辑器中加载
  - 仅支持 `EditorAndProgram` 加载类型，不会在打包游戏中运行
- **推荐度**：如果你需要分析 Chaos 物理锁竞争，推荐使用。这是 Epic 官方工具，与 Unreal Insights 深度集成。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/ChaosInsights)
