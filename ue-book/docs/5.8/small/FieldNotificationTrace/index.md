# Field Notification Trace

> Add support to trace field notification object.

| 属性 | 值 |
|---|---|
| 中文名 | 字段通知追踪 |
| 分类 | UI |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `FieldNotificationTrace` (Runtime), `FieldNotificationTraceEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-05-24 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/FieldNotificationTrace) | |

## 用途

`FieldNotificationTrace` 是一个**调试工具**，旨在解决使用“字段通知”（Field Notification）模式（如 MVVM 或数据绑定）时，难以追踪和诊断字段值变化序列的问题。它并非提供新的字段通知功能，而是在运行时**捕获和记录**字段通知对象的事件（如值变更），并将这些事件数据提供给引擎的**RewindDebugger**，从而让开发者能在时间线上回溯和查看字段变化的精确历史，简化复杂 UI 逻辑的调试过程。

## 使用场景

- 你正在开发一个使用 MVVM 或类似数据绑定模式的 UI 系统，当绑定的数据没有按预期更新或更新顺序出错时 → 启用此插件，通过 RewindDebugger 查看字段通知的触发时序，快速定位逻辑错误。
- 你需要对某个特定对象的字段变化进行历史回溯分析，以验证动画、状态机或游戏逻辑的正确性。

## 蓝图用法

此插件主要作为底层运行时追踪和编辑器可视化工具，**不提供**公开的、用于蓝图逻辑构建的核心节点。其功能通过集成在 **RewindDebugger** 面板中，以时间轴轨道的形式呈现。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| *（无）* | 本插件功能通过引擎编辑器集成（RewindDebugger）交互，不暴露蓝图节点 | - |

### 使用示例（蓝图描述）

1.  在编辑器中启用 `FieldNotificationTrace` 插件。
2.  确保你的 Actor 或 Widget 使用了 `FieldNotify` 宏标记的属性（例如 `UPROPERTY(FieldNotify)`）。
3.  打开 **RewindDebugger** 窗口（通常位于 `Window > Developer Tools > Rewind Debugger`）。
4.  开始游戏会话或“倒回调试”录制。
5.  当字段值发生变化时，你将在 RewindDebugger 的时间线上看到对应的 “FieldNotification” 轨道和事件标记。
6.  点击事件标记可以查看触发通知的对象和字段信息。

## C++ 用法

本插件的核心是引擎内部集成的追踪逻辑，普通开发者通常无需直接调用其 C++ API。它的价值体现在**通过 RewindDebugger 可视化呈现**的数据。

### 头文件引入

作为引擎内部调试工具，通常不需要在你的游戏代码中包含其头文件。其模块主要在引擎编辑器（`FieldNotificationTraceEditor`）和底层运行时（`FieldNotificationTrace`）中工作。

### 基本用法

本插件的使用主要是“启用后自动工作”。开发者需要做的是确保自己的类使用了 UE 的字段通知宏。当这些字段的值发生变化时，追踪模块会自动记录事件。

```cpp
// 在你的 ViewModel 类中使用 FieldNotify 宏（这是你自己的代码，不是直接调用本插件 API）
UCLASS(BlueprintType)
class UMyViewModel : public UObject
{
    GENERATED_BODY()

public:
    UPROPERTY(BlueprintReadWrite, FieldNotify) // 标记此属性支持字段通知
    int32 Score = 0;

    // 修改值的函数，框架会自动发送通知
    UFUNCTION(BlueprintCallable)
    void SetScore(int32 NewScore)
    {
        if (Score != NewScore)
        {
            Score = NewScore;
            // UE 字段通知系统会自动广播 FFieldNotificationId(TEXT("Score"))
            // FieldNotificationTrace 模块会在此处捕获这个广播。
        }
    }
};
```

## Demo 示例

作为引擎内部调试工具，没有面向最终用户的独立可运行示例。其“演示”过程即上述 **RewindDebugger 的使用场景**。启动编辑器，启用插件，对一个包含 `FieldNotify` 属性的对象进行操作，并在 RewindDebugger 中观察其字段变化时间线。

## 模块依赖

使用此插件本身（启用它）不需要在你的项目模块中添加依赖。但其运行和编辑功能依赖以下**引擎内部模块**：

| 模块 | 用途 |
|---|---|
| `GameplayInsights` | 提供游戏玩法分析和追踪的基础设施，是本插件功能实现的基石 |
| `RewindDebugger` | 提供时间线回放调试界面，本插件将追踪数据可视化到此界面 |
| `TraceServices` | 提供底层的事件追踪和分析服务，用于记录和查询追踪数据 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-01 | `fb04ebb6` | [MassDebug] | 与 Mass 框架调试系统相关的集成或修复 |
| 2026-03-30 | `6004f575` | [RewindDebugger] | 与 RewindDebugger 集成相关的改动 |
| 2026-01-16 | `526a5a0a` | [RewindDebugger] Replaced included header by forward declaration for TraceService::Frame | 优化头文件包含，使用前向声明以减少编译依赖 |
| 2026-01-16 | `e2c597c8` | Fix missing debug tracks in rewind debugger for PoseSearch, SequenceInfo, and EvaluationTask when us | 修复了在某些使用场景下，多个调试轨道在RewindDebugger中缺失的问题 |
| 2026-01-15 | `1be36357` | [Backout] - CL49859133 | 回退了之前的某次变更 |

### 维护评价

- **创建时间**：插件于 2024 年 5 月首次提交，是一个相对年轻的工具。
- **更新频率**：近期（2026年初）有两次与 `RewindDebugger` 和 `MassDebug` 相关的更新，表明它仍与引擎的调试系统保持同步维护。
- **状态**：**维护中**。作为 **Beta** 版本的开发者工具，其功能和 API 可能不稳定，但仍在积极集成到新的调试框架（如 Mass）中。
- **推荐度**：推荐给**正在使用或计划使用 UE 字段通知/数据绑定模式**进行复杂 UI 或逻辑开发的团队。它是一个强大的调试助手，能显著降低排查数据流问题的难度。由于是 Beta 版本，建议在开发环境中使用，并关注其随引擎版本更新可能带来的变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/FieldNotificationTrace)
- [官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine) （此插件作为引擎内置工具，可能无独立文档，需查阅通用调试工具文档）
- **测试用例**：未在提供的路径中发现特定测试文件。其功能验证通常集成在引擎整体的自动化测试中。