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

该插件为 `FieldNotify` 系统（常用于属性绑定和模型-视图-视图模型（MVVM）模式）添加了运行时追踪和分析支持。它的核心功能是记录 `FieldNotify` 属性的值变化事件，并将这些事件数据集成到 Unreal Insights 的追踪系统和 **Rewind Debugger** 中。

解决的问题是：开发者难以在运行时调试属性绑定的流程。例如，一个 UI 控件的数值意外改变，开发者很难知道是哪个对象的哪个 `FieldNotify` 属性在何时改变了，以及改变的源头是什么。该插件通过提供一个可视化的时间线，将这些事件记录并回放，极大地简化了这类 UI 状态绑定问题的调试过程。

## 使用场景

- 你正在使用 **FieldNotify** 和 **属性绑定** 来构建复杂的 UI 逻辑，但界面的值出现了意料之外的变化，需要回溯是哪个属性在何时被修改的。
- 你需要分析 UI 或游戏逻辑中 `FieldNotify` 事件的性能，例如它们在某一帧内触发了多少次、是否有冗余的广播。
- 你正在开发一个使用 MVVM 模式的游戏或应用，需要监控视图模型（ViewModel）中属性变化对视图（View）的驱动过程。

## 蓝图用法

该插件主要提供**编辑器内分析和可视化**功能，而非暴露可直接在运行时调用的蓝图节点。其核心交互界面是通过 **Rewind Debugger** 提供的。

### 核心节点

该插件不提供 `BlueprintCallable` 节点。其功能通过以下方式访问：

1.  **在编辑器中**：打开 **Rewind Debugger** 窗口。
2.  **在追踪轨道中**：你将看到一个名为 “Field Notify” 或类似的轨道，它会根据追踪的 `FieldNotify` 事件在时间线上绘制标记。
3.  **查看详情**：点击事件标记，可以在详情面板中查看事件相关的对象 ID、字段名称等信息。

## C++ 用法

该插件的 C++ 用法主要分为两部分：运行时插件（用于数据生产）和编辑器插件（用于数据消费和可视化）。

### 头文件引入

对于运行时数据记录（假设你正在扩展或测试追踪系统）：
```cpp
#include "FieldNotificationTrace/FieldNotificationTraceModule.h" // 假设的公共头文件
```

对于编辑器端分析或与 Rewind Debugger 集成：
```cpp
#include "FieldNotificationTraceEditorModule.h"
#include "FieldNotificationTraceProvider.h"
#include "FieldNotificationTrack.h"
```

### 基本用法

该插件的核心逻辑是自动注册到 Unreal Insights 的分析会话中。一个典型的用例是，当 `FieldNotify` 属性的值发生变化时，系统会通过 `FTraceProvider` 记录一次事件。

以下代码展示了如何从 `FTraceProvider` 中查询已记录的事件（通常在编辑器分析器中使用）：
```cpp
// 来自 Private/FieldNotificationTraceProvider.h
// 假设已有一个有效的 FTraceProvider 实例 (Provider)
// 和时间范围 (StartTime, EndTime)
Provider->EnumerateFieldNotifies(ObjectId, StartTime, EndTime,
    [&](double EventTime, double RecordingTime, uint32 Depth, const FTraceProvider::FFieldNotifyEvent& Event)
    {
        // EventTime: 事件发生时的时间戳
        // Event.FieldNotifyId: 变化的字段的 ID
        FFieldNotificationId FieldId = Provider->GetFieldNotificationId(Event.FieldNotifyId);
        UE_LOG(LogTemp, Log, TEXT("Field %s changed at time %f"), *FieldId.ToString(), EventTime);
    }
);
```

### 进阶用法

更复杂的用法涉及集成到 **Rewind Debugger** 中，创建自定义的轨道来可视化 `FieldNotify` 事件。这主要由 `FieldNotificationTraceEditor` 模块中的 `FTracksCreator` 和 `FFieldNotifyTrack` 类完成。

你可以通过继承 `IRewindDebuggerExtension` 来扩展调试器的功能，例如在录制开始/停止时执行自定义逻辑：
```cpp
// 来自 Private/FieldNotificationRewindDebugger.h
class FMyCustomExtension : public UE::FieldNotification::FRewindDebuggerRuntimeExtension
{
public:
    virtual void RecordingStarted() override
    {
        // 当 Rewind Debugger 开始录制时，你可以进行自定义初始化
        // 例如，确保特定的 FieldNotify 跟踪通道已开启
        Super::RecordingStarted();
    }
};
```

## Demo 示例

以下示例演示了如何在自定义模块中注册一个简单的 FieldNotify 事件追踪（简化版，实际实现需处理更多细节）。

### `MyFieldNotifyDemo.h`
```cpp
#pragma once
#include "CoreMinimal.h"
#include "FieldNotification/FieldNotificationId.h"
#include "MyFieldNotifyDemo.generated.h"

UCLASS(BlueprintType)
class UMyDataObject : public UObject
{
    GENERATED_BODY()

public:
    UPROPERTY(BlueprintReadWrite, FieldNotify)
    int32 Health = 100;
};
```

### `MyFieldNotifyDemo.cpp`
```cpp
#include "MyFieldNotifyDemo.h"
// 假设我们通过某种方式获取到了全局的 Trace Provider (这通常由引擎内部完成)
// 在实际开发中，你通常不需要直接调用 Provider，而是通过 FieldNotify 的广播机制间接触发。
// 下面仅为演示追踪器的底层调用逻辑。
// extern UE::FieldNotification::FTraceProvider* GFieldNotificationTraceProvider;

void SimulateFieldNotifyChange(UMyDataObject* DataObject)
{
    if (DataObject)
    {
        // 修改属性值
        DataObject->Health = 95;
        
        // 通常，广播事件由引擎或用户代码完成，例如：
        // DataObject->FFieldNotifyClass::BroadcastFieldValueChanged(FFieldNotificationId(GET_MEMBER_NAME_CHECKED(UMyDataObject, Health)));
        // 此时，FieldNotificationTrace 插件的运行时部分（如果启用并激活了追踪）会自动捕获这个广播事件，
        // 并通过内部机制记录到 Trace Stream 中。
    }
}
```

## 模块依赖

要使用此插件，你的项目模块需要依赖：

### FieldNotificationTrace (Runtime 模块) 依赖
| 模块 | 用途 |
|---|---|
| `GameplayInsights` | 插件核心依赖，提供 Insights 追踪框架 |
| `TraceAnalysis` | 用于分析追踪会话中的数据 |
| `TraceServices` | 提供追踪服务和会话管理 |

### FieldNotificationTraceEditor (Editor 模块) 依赖
| 模块 | 用途 |
|---|---|
| `FieldNotificationTrace` | 依赖其运行时模块 |
| `RewindDebugger` | 集成回放调试器的核心框架 |
| `TraceAnalysis` | 在编辑器中分析追踪数据 |
| `TraceServices` | 在编辑器中访问追踪服务 |

**注意**：该插件本身还依赖 `GameplayInsights` 插件（在 .uplugin 中声明）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-01 | `fb04ebb6` | [MassDebug] | 与 Mass 框架调试工具相关的更新 |
| 2026-03-30 | `6004f575` | [RewindDebugger] | 与回放调试器相关的通用更新 |
| 2026-01-16 | `526a5a0a` | [RewindDebugger] Replaced included header by forward declaration for TraceService::Frame | 重构代码，将头文件包含替换为前置声明，优化编译依赖 |
| 2026-01-16 | `e2c597c8` | Fix missing debug tracks in rewind debugger for PoseSearch, SequenceInfo, and EvaluationTask when us | 修复了多个调试轨道在特定情况下不显示的 Bug |
| 2026-01-15 | `1be36357` | [Backout] - CL49859133 | 回滚了某个之前的改动 |

### 维护评价

该插件由 Epic Games 创建于 2024 年 5 月，相对年轻。从 Git 历史看，**2026 年初仍有持续的维护活动**，包括功能更新、重构和 Bug 修复，表明它仍处于活跃开发中，但更新频率不算高。

**主要特点**：
- **Beta 状态**：插件被明确标记为 `IsBetaVersion=true`，意味着其 API 可能不稳定，功能和接口在未来版本中可能会发生改变。
- **编辑器专用**：主要功能（可视化、分析）集中在编辑器模块 (`FieldNotificationTraceEditor`)，适用于开发调试，而非游戏运行时。
- **深度集成**：与 Unreal Insights 和 Rewind Debugger 深度绑定，是引擎调试工具链的一部分。

**推荐使用**：
- 如果你在项目中大量使用 `FieldNotify` 属性绑定，并且遇到了难以调试的状态同步问题，**强烈建议启用此插件**，它能提供宝贵的可视化调试信息。
- 由于其 Beta 状态和编辑器侧重点，不建议在最终的游戏打包中启用此插件。
- 使用时需注意，它需要配合 **Gameplay Insights** 和 **Rewind Debugger** 工具使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/FieldNotificationTrace)
- [官方文档](https://docs.unrealengine.com) (无特定文档，属于引擎内部调试工具)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/FieldNotificationTrace) (可能存在，路径为推测)