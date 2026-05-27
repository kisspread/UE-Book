```markdown
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

FieldNotificationTrace 是一个**开发者调试工具**，用于在 Unreal Insights 的 Rewind Debugger 中追踪和可视化 Field Notification（字段通知）事件。

UE5 的 Field Notification 系统是属性变更通知机制，广泛用于 UMG 数据绑定和 MVVM 模式。当绑定的属性值发生变化时，系统会触发字段通知。本插件的核心功能是：

1. **记录**：在运行时捕获所有字段通知事件（属性值何时变化、哪个字段触发了通知）
2. **可视化**：在 Rewind Debugger 时间轴中以轨道形式展示每个对象的字段通知事件
3. **回放分析**：配合 Rewind Debugger 的时间回溯功能，回放并检查字段通知的触发时机

这解决了开发者在调试 UI 数据绑定问题时"不知道通知何时触发、是否遗漏"的痛点。

## 使用场景

- 你在用 UMG + Field Notification 做数据绑定，但 UI 没有正确更新 → 用 FieldNotificationTrace 查看通知是否被触发
- 你需要排查 MVVM ViewModel 中属性变更通知的时序问题 → 在 Rewind Debugger 中回放查看
- 你需要确认某个属性变更是否正确传播到了 UI 层 → 通过时间轴对齐分析

**前提条件**：需要先启用 `GameplayInsights` 插件。

## 蓝图用法

本插件**没有暴露任何蓝图接口**。它是一个纯开发者工具，通过 Unreal Insights 和 Rewind Debugger 界面使用，无需编写任何代码。

### 使用方式

1. 启用插件（`Edit > Plugins > Field Notification Trace`）
2. 启用 `GameplayInsights` 插件（如果未启用）
3. 打开 `Window > Developer Tools > Insights`（或使用命令行参数 `-trace=default,fieldnotification`）
4. 在 Unreal Insights 中连接到运行中的游戏实例
5. 启用 Rewind Debugger（`Tools > Rewind Debugger`）
6. 在 Rewind Debugger 时间轴中找到对应的 Field Notification 轨道

## C++ 用法

本插件的核心是 Trace Services 集成，以下是从源码中提取的关键 API。

### 头文件引入

```cpp
// Runtime 模块 - 追踪服务
#include "FieldNotificationTraceServices.h"
#include "FieldNotificationTraceProvider.h"
#include "FieldNotificationTraceAnalyzer.h"

// Editor 模块 - Rewind Debugger 集成
#include "FieldNotificationTrack.h"
#include "FieldNotificationRewindDebugger.h"
```

### 基本用法：自定义追踪服务模块

以下代码展示了 `FTraceServiceModule` 如何向 Trace Services 注册字段通知追踪模块。

```cpp
// 来源: Private/FieldNotificationTraceServices.h

// FTraceServiceModule 实现了 TraceServices::IModule 接口
// 当 Unreal Insights 启动分析会话时，OnAnalysisBegin 会被调用
// 它会创建 FTraceProvider 和 FTraceAnalyzer 实例
class FTraceServiceModule : public TraceServices::IModule
{
    virtual void OnAnalysisBegin(TraceServices::IAnalysisSession& Session) override;
    virtual void GetLoggers(TArray<const TCHAR*>& OutLoggers) override;
    // 命令行参数: -trace=fieldnotification
    virtual const TCHAR* GetCommandLineArgument() override
    {
        return TEXT("fieldnotification");
    }
};
```

### 基本用法：追踪提供者（数据存储层）

`FTraceProvider` 是数据存储层，负责保存字段通知事件数据。

```cpp
// 来源: Private/FieldNotificationTraceProvider.h

using namespace UE::FieldNotification;

// 获取追踪提供者实例
FTraceProvider* Provider = /* 从分析会话中获取 */;

// 记录对象生命周期
Provider->AppendObjectBegin(ObjectId, ProfileTime);
Provider->AppendObjectEnd(ObjectId, ProfileTime);

// 记录字段值变更事件
Provider->AppendFieldValueChanged(ObjectId, ProfileTime, RecordingTime, FieldNotifyId);

// 注册字段通知名称
Provider->AppendFieldNotify(FieldNotifyId, FName("MyPropertyName"));
```

### 进阶用法：枚举追踪数据

通过回调模式枚举存储的字段通知事件，用于 UI 渲染和分析报告。

```cpp
// 来源: Private/FieldNotificationTraceProvider.h

// 枚举时间范围内的所有对象
Provider->EnumerateObjects(StartTime, EndTime,
    [&](double InStartTime, double InEndTime, uint32 InDepth, const FTraceProvider::FObject& Object)
    {
        // 处理每个对象的时间段
        uint64 ObjectId = Object.SelfObjectId;
    });

// 枚举指定对象的字段通知事件
Provider->EnumerateFieldNotifies(ObjectId, StartTime, EndTime,
    [&](double InStartTime, double InEndTime, uint32 InDepth,
        const FTraceProvider::FFieldNotifyEvent& Event)
    {
        // Event.FieldNotifyId 可用于获取字段名称
        FFieldNotificationId FieldId = Provider->GetFieldNotificationId(Event.FieldNotifyId);
        FName FieldName = FieldId.GetFieldName();
    });

// 枚举录制期间的字段通知（用于实时录制模式）
Provider->EnumerateRecordingFieldNotifies(ObjectId, StartTime, EndTime,
    [&](double InStartTime, double InEndTime, uint32 InDepth,
        const FTraceProvider::FFieldNotifyEvent& Event)
    {
        // 处理录制中的事件
    });
```

### 进阶用法：Rewind Debugger 轨道扩展

以下代码展示了如何为 Rewind Debugger 创建自定义的字段通知轨道。

```cpp
// 来源: Private/FieldNotificationTrack.h

using namespace UE::FieldNotification;

// FObjectTrack: 代表一个拥有字段通知的对象
// 在 Rewind Debugger 的对象树中作为父节点
class FObjectTrack : public RewindDebugger::FRewindDebuggerTrack
{
    // 子轨道：每个字段通知一个 FFieldNotifyTrack
    TArray<TSharedPtr<FFieldNotifyTrack>> Children;
};

// FFieldNotifyTrack: 代表单个字段的通知事件
// 在时间轴上显示为事件点
class FFieldNotifyTrack : public RewindDebugger::FRewindDebuggerTrack
{
    FFieldNotifyTrack(uint64 InObjectId, uint32 InFieldNotifyId,
                      FFieldNotificationId InFieldNotify);
    // 双击轨道可跳转到相关代码位置
    virtual bool HandleDoubleClickInternal() override;
};

// FTracksCreator: 负责发现和创建轨道
// 通过 IRewindDebuggerTrackCreator 接口注册
class FTracksCreator : public RewindDebugger::IRewindDebuggerTrackCreator
{
    virtual TSharedPtr<RewindDebugger::FRewindDebuggerTrack>
        CreateTrackInternal(const RewindDebugger::FObjectId& InObjectId) const override;
    virtual bool HasDebugInfoInternal(const RewindDebugger::FObjectId& InObjectId) const override;
};
```

## Demo 示例

以下展示如何为自定义类型集成字段通知追踪。本插件本身不需要用户编写代码，但如果你想要扩展追踪能力，可以参考以下模式。

```cpp
// MyViewModel.h
#pragma once

#include "FieldNotification/FieldNotification.h"
#include "UObject/Object.h"
#include "MyViewModel.generated.h"

UCLASS()
class UMyViewModel : public UObject
{
    GENERATED_BODY()

public:
    // 声明带字段通知的属性
    // UE5 的 FieldNotification 系统会在属性变化时自动触发通知
    UPROPERTY(BlueprintReadWrite, FieldNotify)
    FString PlayerName;

    UPROPERTY(BlueprintReadWrite, FieldNotify)
    int32 Score;

    // BlueprintCallable 函数，修改属性时会自动触发字段通知
    UFUNCTION(BlueprintCallable)
    void UpdateScore(int32 NewScore)
    {
        Score = NewScore;
        // FieldNotification 系统自动通知，FieldNotificationTrace 会自动捕获
    }
};

// 使用说明：
// 1. 启用 FieldNotificationTrace 插件
// 2. 运行游戏，连接 Unreal Insights
// 3. 在 Rewind Debugger 中即可看到 Score 和 PlayerName 的通知事件时间轴
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GameplayInsights` | 父级插件依赖，提供 Insights 基础设施和 Rewind Debugger 框架 |
| `TraceServices` | Trace 分析会话和时间轴数据存储 |
| `RewindDebugger` | 时间回溯调试器框架，提供 Track/Extension 接口 |
| `UnrealInsights` | Trace 分析器接口（IAnalyzer） |
| `FieldNotification` | 字段通知核心类型（FFieldNotificationId） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-01 | `fb04ebb6` | [MassDebug] | 与 MassDebug 框架相关的改动 |
| 2026-03-30 | `6004f575` | [RewindDebugger] | Rewind Debugger 框架层面更新 |
| 2026-01-16 | `526a5a0a` | [RewindDebugger] Replaced included header by forward declaration for TraceService::Frame | 将 TraceService::Frame 头文件替换为前向声明，减少编译依赖 |
| 2026-01-16 | `e2c597c8` | Fix missing debug tracks in rewind debugger for PoseSearch, SequenceInfo, and EvaluationTask when us | 修复多个模块调试轨道缺失的 bug |
| 2026-01-15 | `1be36357` | [Backout] - CL49859133 | 回退某次提交 |

### 维护评价

- **状态**：仍在维护中，作为 Rewind Debugger 生态的一部分持续更新
- **风险**：标记为 **Beta 版**且**默认未启用**，API 可能发生变化
- **活跃度**：最近几个月有持续更新，主要是跟随 Rewind Debugger 框架的维护和修复
- **限制**：仅用于开发调试，不应用于生产环境；依赖 GameplayInsights 插件；当前仅支持 Editor 模块的可视化（Runtime 追踪录制的扩展仍在 TODO 中，参见 `FieldNotificationRewindDebugger.h` 中的 `@todo` 注释）
- **推荐**：如果你在项目中大量使用 Field Notification 进行 UI 数据绑定调试，推荐启用此插件；否则无需关注

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/FieldNotificationTrace)
- 官方文档（暂无）
```