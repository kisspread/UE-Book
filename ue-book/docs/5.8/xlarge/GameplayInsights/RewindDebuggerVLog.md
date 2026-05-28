# Rewind Debugger VLog

> Allows debugging of animation systems via Unreal Insights

| 属性 | 值 |
|---|---|
| 中文名 | 可视化日志调试器 |
| 分类 | Insights |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `RewindDebuggerVLog` (Runtime), `RewindDebuggerVLogRuntime` (Runtime), `GameplayInsights` (Runtime), `GameplayInsightsEditor` (Runtime), `RewindDebugger` (Runtime), `RewindDebuggerRuntime` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-15 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/GameplayInsights) | |

## 用途

此模块是 `GameplayInsights` 大型插件的一部分，它为 **Rewind Debugger（回放调试器）** 扩展了 **Visual Logger（可视化日志）** 的调试能力。它的核心功能是：
1.  **时间线整合**：将 Visual Logger 记录的各类日志条目（如文本、形状、状态）集成到 Rewind Debugger 的时间线视图中，允许开发者按照游戏进程回放并查看这些日志。
2.  **数据跟踪与分析**：通过 Unreal Insights 的跟踪（Trace）系统，记录、分析和序列化 Visual Logger 的数据，支持对历史日志的检索和报告生成。
3.  **场景渲染**：在游戏场景中直接渲染 Visual Logger 记录的调试形状（如点、线、盒体），并根据类别和详细级别（Verbosity）进行过滤显示。
4.  **实时过滤**：提供 UI 控件，允许用户在录制时和回放时，按类别和日志详细级别过滤显示的日志条目，聚焦于特定系统的调试信息。

它解决了在复杂游戏逻辑、动画状态机或 AI 行为的调试过程中，需要将离散的日志信息与游戏事件和对象状态同步回放、关联分析的需求。

## 使用场景

- 你在调试一个复杂的 **角色动画状态机**，需要查看在状态切换瞬间记录的调试日志和形状。→ 使用此模块在 Rewind Debugger 中回放该时段，选择“Visual Logging”轨道即可查看。
- 你需要验证一个 **AI 行为树** 的决策逻辑，该行为树在关键节点使用了 Visual Logger 记录当前状态和考虑的目标。→ 通过此模块的过滤功能，只显示与该 AI 类别相关的日志，集中分析其决策过程。
- 你的游戏有一个 **复杂的空间解谜系统**，会在解谜过程中绘制碰撞区域、视线射线等调试形状。→ 使用此模块在回放时，让这些形状随时间线重现，便于观察交互逻辑。
- 你想**生成一份报告**，汇总某个时间段内所有 “Combat” 类别的日志。→ 利用 `FVLogTraceModule` 提供的报告生成功能，或通过 `FVisualLoggerProvider` 接口编程读取数据。

## 蓝图用法

此模块主要作为 **Rewind Debugger 的扩展** 存在，其核心交互通过编辑器内的 Rewind Debugger 面板和 Unreal Insights 窗口完成。蓝图中的直接控制较少，主要通过对设置对象的访问来实现。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get` | 获取 Rewind Debugger Visual Logger 设置的单例。 | `URewindDebuggerVLogSettings` |
| `ToggleCategory` | 切换指定 Visual Logger 类别在 Rewind Debugger 中的显示状态。 | `URewindDebuggerVLogSettings` |
| `SetCategoryVerbosity` | 设置指定 Visual Logger 类别在回放时的显示详细级别。 | `URewindDebuggerVLogSettings` |
| `GetCategoryVerbosity` | 获取指定 Visual Logger 类别在回放时的显示详细级别。 | `URewindDebuggerVLogSettings` |

### 使用示例（蓝图描述）

1.  **控制日志类别显示**：
    - 创建一个 `Get` 节点获取 `URewindDebuggerVLogSettings` 对象。
    - 连接 `ToggleCategory` 节点，将 `Category` 引脚连接到一个 `MakeLiteralName` 节点（值为 `"MyAISystem"`）。
    - 执行该蓝图节点，即可在 Rewind Debugger 中切换 `"MyAISystem"` 类别日志的显示状态。

2.  **设置日志详细级别**：
    - 同样先获取设置对象。
    - 连接 `SetCategoryVerbosity` 节点。
    - `Category` 设为 `"Physics"`。
    - `Verbosity` 设为 `ELogVerbosity::Warning`（通过枚举变量）。
    - 执行后，在回放时将只显示 “Physics” 类别中警告级别及以上的日志。

## C++ 用法

### 头文件引入

```cpp
// 访问 Visual Logger 的数据提供者接口
#include "IVisualLoggerProvider.h"

// 访问 Rewind Debugger 的 Visual Logger 扩展（如需扩展或交互）
#include "RewindDebuggerVLog.h"
```

### 基本用法

通过 `FVisualLoggerProvider` 读取已记录的 Visual Logger 时间线数据。
*（示例灵感来源于 `Private/VisualLoggerProvider.h` 及其接口定义）*

```cpp
// 在需要分析 Visual Logger 数据的上下文中（例如一个自定义分析工具模块）
void AnalyzeVisualLogData(const TraceServices::IAnalysisSession& Session)
{
    // 获取 Visual Logger 数据提供者
    const IVisualLoggerProvider* VLogProvider = Session.ReadProvider<IVisualLoggerProvider>(IVisualLoggerProvider::ProviderName);
    if (!VLogProvider)
    {
        return;
    }

    // 开始读访问
    VLogProvider->BeginRead();

    // 为一个特定对象（例如某个角色的 ID）读取其 Visual Logger 时间线
    const uint64 TargetObjectId = /* ... */;
    VLogProvider->ReadVisualLogEntryTimeline(TargetObjectId, [&](const IVisualLoggerProvider::VisualLogEntryTimeline& Timeline)
    {
        // 遍历时间线上的每个日志条目
        Timeline.EnumerateEvents(0.0, 100000.0, [&](double Time, const FVisualLogEntry& Entry)
        {
            // 处理日志条目，例如解析其类别、日志文本、调试形状等
            UE_LOG(LogTemp, Log, TEXT("Time: %.2f, Object: %llu, Log Category: %s"), Time, TargetObjectId, *Entry.Category.ToString());
            // ... 更多处理逻辑
            return TraceServices::EEventEnumerate::Continue;
        });
    });

    // 结束读访问
    VLogProvider->EndRead();
}
```

### 进阶用法

扩展 `FRewindDebuggerVLog` 以添加自定义的回放时行为（例如，对特定日志条目进行特殊渲染）。
*（示例灵感来源于 `Private/RewindDebuggerVLog.h`）*

```cpp
#include "RewindDebuggerVLog.h"

// 创建一个派生自 FRewindDebuggerVLog 的类，或直接使用它
class FMyCustomVLogExtension : public FRewindDebuggerVLog
{
public:
    // 重写 Update 函数以在回放每帧执行自定义逻辑
    virtual void Update(float DeltaTime, IRewindDebugger* RewindDebugger) override
    {
        // 调用父类更新逻辑，确保基础功能正常
        FRewindDebuggerVLog::Update(DeltaTime, RewindDebugger);

        // 在此处添加你的自定义更新逻辑
        // 例如，检查当前回放时间，获取特定对象的日志，执行分析或触发其他事件
    }

    // 可以重写 OnShowDebugInfo 来在 HUD 上绘制自定义信息
    virtual void OnShowDebugInfo(UCanvas* Canvas, APlayerController* Player) override
    {
        FRewindDebuggerVLog::OnShowDebugInfo(Canvas, Player);

        // 在 Canvas 上绘制额外的调试文本
        if (Canvas)
        {
            Canvas->SetDrawColor(FColor::Cyan);
            Canvas->DrawText(GEngine->GetSmallFont(), TEXT("My Custom VLog Info"), 10, 100);
        }
    }
};
```

## Demo 示例

以下是一个最小化示例，演示如何创建一个简单的自定义 Visual Logger 扩展，在回放时将特定类别的日志输出到编辑器输出日志窗口。

**MyVisualLogExtension.h**
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.
#pragma once

#include "RewindDebuggerVLog.h"

// 一个简单的 Rewind Debugger VLog 扩展，用于在回放时输出自定义日志
class FMyVisualLogExtension : public FRewindDebuggerVLog
{
public:
    FMyVisualLogExtension();
    virtual ~FMyVisualLogExtension();

    // IModuleInterface 的初始化/关闭可以在此处理，或在模块启动时注册
    void Initialize();

protected:
    // 重写 Update 以插入自定义逻辑
    virtual void Update(float DeltaTime, IRewindDebugger* RewindDebugger) override;

private:
    // 内部函数，用于输出特定类别日志
    void OutputCustomCategoryLogs(float CurrentTime, IRewindDebugger* RewindDebugger);

    // 标记，确保每帧只输出一次日志以避免刷屏
    bool bLogOutputThisFrame = false;
};
```

**MyVisualLogExtension.cpp**
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.
#include "MyVisualLogExtension.h"
#include "VisualLogger/VisualLogger.h"
#include "RewindDebugger.h" // 获取 IRewindDebugger 接口

DEFINE_LOG_CATEGORY_STATIC(LogMyVLogExt, Log, All);

FMyVisualLogExtension::FMyVisualLogExtension()
{
}

FMyVisualLogExtension::~FMyVisualLogExtension()
{
}

void FMyVisualLogExtension::Initialize()
{
    // 此处可以注册一些回调或菜单项
}

void FMyVisualLogExtension::Update(float DeltaTime, IRewindDebugger* RewindDebugger)
{
    // 先调用父类 Update，确保标准的 Visual Logger 轨道和渲染正常工作
    FRewindDebuggerVLog::Update(DeltaTime, RewindDebugger);

    // 重置每帧标记
    bLogOutputThisFrame = false;

    // 检查是否在回放中
    if (RewindDebugger && RewindDebugger->IsRecording())
    {
        return; // 不在录制时才进行回放输出
    }

    // 输出 “AIDecision” 类别的日志
    OutputCustomCategoryLogs(RewindDebugger->GetScrubTime(), RewindDebugger);
}

void FMyVisualLogExtension::OutputCustomCategoryLogs(float CurrentTime, IRewindDebugger* RewindDebugger)
{
    if (bLogOutputThisFrame || !RewindDebugger)
    {
        return;
    }

    // 假设我们关注一个特定对象的日志（例如通过 RewindDebugger 获取当前调试对象）
    const FDebugObjectInfo* DebugObject = RewindDebugger->GetDebugObjectInfo();
    if (!DebugObject)
    {
        return;
    }

    // 通过 Visual Logger 提供者接口获取数据（此处简化，实际需通过 IVisualLoggerProvider）
    // 这里仅为演示目的，假设我们已经获得了该对象的日志时间线引用
    // const IVisualLoggerProvider::VisualLogEntryTimeline& Timeline = ...;

    // 枚举当前时间点附近（例如 +-0.1 秒）的日志条目
    const float TimeWindow = 0.1f;
    // Timeline.EnumerateEvents(CurrentTime - TimeWindow, CurrentTime + TimeWindow,
    //     [&](double Time, const FVisualLogEntry& Entry)
    //     {
    //         if (Entry.Category == FName("AIDecision"))
    //         {
    //             UE_LOG(LogMyVLogExt, Warning, TEXT("[VLog Replay] Object %llu at Time %.2f: %s"),
    //                 DebugObject->ObjectId, Time, *Entry.LogMessage);
    //         }
    //         return TraceServices::EEventEnumerate::Continue;
    //     });

    bLogOutputThisFrame = true;
}
```

## 模块依赖

此模块 (`RewindDebuggerVLog`) 的构建依赖于以下独特或关键模块。使用该功能的项目模块也应包含这些依赖。

| 模块 | 用途 |
|---|---|
| `TraceServices` | 提供 Unreal Insights 的跟踪数据容器、时间线和分析会话的基础设施。 |
| `RewindDebugger` | 核心回放调试器框架，提供 `IRewindDebugger`, `FRewindDebuggerTrack`, `IRewindDebuggerExtension` 等接口和基类。 |
| `VisualLogger` | 引擎的可视化日志系统，提供 `FVisualLogEntry` 数据结构、日志记录宏和基础渲染支持。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `a3d17a57` | fix Rewind Debugger eyedropper to cancel when reattaching player control while it's active | 修复了回放调试器中取色器在玩家控制器重新附加时未正确取消的问题。 |
| 2026-05-13 | `ec80c6b8` | [RewindDebugger] Add programmable scrub and view-centring surface on `IRewindDebugger`. | 为 `IRewindDebugger` 接口添加了可编程的进度拖拽和视图居中功能。 |
| 2026-04-28 | `7805b240` | Rewind Debugger toolbar UX pass. | 对回放调试器的工具栏进行了用户体验优化。 |
| 2026-04-15 | `4b250a9d` | [RewindDebugger] | 提交信息不完整，推测为 Rewind Debugger 相关更新。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将代码中的 `UE_LOG` 宏迁移到了 `UE_LOGF` 宏。 |

### 维护评价

该模块作为 `GameplayInsights` 大型插件的一部分，**维护状态活跃**。
- **年龄**：创建于 2019 年，约有 6 年历史，属于“老古董”级别，但仍在持续迭代。
- **更新频率**：最近在 2026 年 5 月仍有功能性更新（如 UX 改进、接口扩展）和 Bug 修复，表明处于积极维护中。
- **功能状态**：虽然是插件的一部分且默认未启用，但功能完整，与引擎核心调试工具深度集成，是动画和 Gameplay 调试的重要工具。
- **推荐使用**：推荐。对于需要深度利用 Unreal Insights 和 Visual Logger 进行动画、AI 或复杂游戏逻辑调试的项目，这是一个非常有价值的工具。需要注意的是，它需要启用插件并可能依赖 Unreal Insights 的分析工具。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/GameplayInsights)
- [官方文档]()（暂无）
- [测试用例]()（暂无）