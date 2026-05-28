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

FieldNotificationTrace 为实现了 `INotifyFieldValueChanged` 接口的对象提供运行时追踪能力。它通过 Unreal Insights 追踪系统，记录字段通知对象的生命周期（创建/销毁）和字段值变更事件，并将这些数据集成到 RewindDebugger 中，使开发者能够回溯查看字段值的变化历史。

该插件解决了调试 MVVM 架构中数据绑定变更难以追踪的问题——当 UI 绑定的字段值发生变化时，开发者可以在 RewindDebugger 的时间线上直观地看到变化发生的时机和对象。

## 使用场景

- 你使用 MVVM 框架或自定义的 `INotifyFieldValueChanged` 实现，需要调试字段变更通知是否正确触发 → 用 FieldNotificationTrace
- 你正在使用 GameplayInsights 和 RewindDebugger，希望在回放调试器中查看字段通知事件的时间线 → 用 FieldNotificationTrace
- 你在排查 UI 不刷新的问题，需要确认字段变更事件是否被正确广播 → 用 FieldNotificationTrace

## 蓝图用法

本插件不提供蓝图节点，完全通过 C++ 宏和静态函数使用。

## C++ 用法

### 头文件引入

```cpp
#include "Trace/FieldNotificationTrace.h"
```

### 基本用法

FieldNotificationTrace 的核心是通过宏在对象生命周期和字段变更处插入追踪点。以下宏在 `UE_FIELDNOTIFICATION_TRACE_ENABLED` 未定义时会自动展开为空，不会产生任何开销。

#### 追踪对象生命周期

在实现了 `INotifyFieldValueChanged` 的对象中，标记其生命周期起止：

```cpp
class UMyViewModel : public UObject, public INotifyFieldValueChanged
{
public:
    UMyViewModel()
    {
        // 对象创建时记录追踪起点
        UE_TRACE_FIELDNOTIFICATION_LIFETIME_BEGIN(this);
    }

    virtual ~UMyViewModel()
    {
        // 对象销毁时记录追踪终点
        UE_TRACE_FIELDNOTIFICATION_LIFETIME_END(this);
    }
};
```

#### 追踪字段值变更

在字段值发生变化时，调用追踪宏记录变更事件：

```cpp
void UMyViewModel::SetHealth(int32 NewHealth)
{
    if (Health != NewHealth)
    {
        Health = NewHealth;
        // 追踪字段值变更，Field_Health 是通过 FieldNotification 宏生成的 FFieldId
        UE_TRACE_FIELDNOTIFICATION_FIELD_VALUE_CHANGED(this, Field_Health);
    }
}
```

### 进阶用法

可以直接使用底层静态 API 进行更精细的控制：

```cpp
#include "Trace/FieldNotificationTrace.h"

void CustomTracingExample(TScriptInterface<INotifyFieldValueChanged> NotifyObject)
{
    // 显式开始追踪对象
    UE::FieldNotification::FTrace::OutputObjectBegin(NotifyObject);

    // 追踪某个字段的变更
    UE::FieldNotification::FTrace::OutputUpdateField(
        Cast<UObject>(NotifyObject),
        FFieldId(TEXT("MyFieldName"))
    );

    // 结束追踪对象
    UE::FieldNotification::FTrace::OutputObjectEnd(NotifyObject);
}

// 手动控制追踪的启停
void EnableTracing()
{
    UE::FieldNotification::FTrace::StartTracing();
}

void DisableTracing()
{
    UE::FieldNotification::FTrace::StopTracing();
}
```

## Demo 示例

一个完整的最小示例，展示如何在自定义 ViewModel 中集成 FieldNotificationTrace：

### MyViewModel.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "UObject/Interface.h"
#include "FieldNotification/FieldNotificationDeclaration.h"
#include "Trace/FieldNotificationTrace.h"
#include "MyViewModel.generated.h"

DECLARE_FIELD_NOTIFICATION_DECLARE_DELEGATE(FOnHealthChanged, Health);
DECLARE_FIELD_NOTIFICATION_DECLARE_DELEGATE(FOnNameChanged, Name);

UCLASS(BlueprintType)
class UMyViewModel : public UObject, public INotifyFieldValueChanged
{
    GENERATED_BODY()

public:
    UMyViewModel();
    virtual ~UMyViewModel();

    UPROPERTY(BlueprintReadWrite, FieldNotify)
    int32 Health = 100;

    UPROPERTY(BlueprintReadWrite, FieldNotify)
    FString Name = TEXT("Player");

    UFUNCTION(BlueprintCallable)
    void SetHealth(int32 NewHealth);

    UFUNCTION(BlueprintCallable)
    void SetName(const FString& NewName);

    //~ Begin INotifyFieldValueChanged Interface
    virtual FFieldNotificationId GetFieldNotificationId(const FName& PropertyName) const override;
    virtual void BroadcastFieldValueChanged(const FFieldNotificationId& FieldId) override;
    //~ End INotifyFieldValueChanged Interface
};
```

### MyViewModel.cpp

```cpp
#include "MyViewModel.h"

UMyViewModel::UMyViewModel()
{
    UE_TRACE_FIELDNOTIFICATION_LIFETIME_BEGIN(this);
}

UMyViewModel::~UMyViewModel()
{
    UE_TRACE_FIELDNOTIFICATION_LIFETIME_END(this);
}

void UMyViewModel::SetHealth(int32 NewHealth)
{
    if (Health != NewHealth)
    {
        Health = NewHealth;
        UE_TRACE_FIELDNOTIFICATION_FIELD_VALUE_CHANGED(this, FFieldNotificationId(GET_MEMBER_NAME_CHECKED(UMyViewModel, Health)));
        BroadcastFieldValueChanged(FFieldNotificationId(GET_MEMBER_NAME_CHECKED(UMyViewModel, Health)));
    }
}

void UMyViewModel::SetName(const FString& NewName)
{
    if (Name != NewName)
    {
        Name = NewName;
        UE_TRACE_FIELDNOTIFICATION_FIELD_VALUE_CHANGED(this, FFieldNotificationId(GET_MEMBER_NAME_CHECKED(UMyViewModel, Name)));
        BroadcastFieldValueChanged(FFieldNotificationId(GET_MEMBER_NAME_CHECKED(UMyViewModel, Name)));
    }
}

FFieldNotificationId UMyViewModel::GetFieldNotificationId(const FName& PropertyName) const
{
    FFieldNotificationId Id(PropertyName);
    return Id;
}

void UMyViewModel::BroadcastFieldValueChanged(const FFieldNotificationId& FieldId)
{
    // 标准字段通知广播
    INotifyFieldValueChanged::BroadcastFieldValueChanged(FieldId);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GameplayInsights` | 追踪数据输出和 RewindDebugger 集成（插件依赖） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-01 | `fb04ebb6` | [MassDebug] | Mass 框架调试相关改动 |
| 2026-03-30 | `6004f575` | [RewindDebugger] | RewindDebugger 集成改动 |
| 2026-01-16 | `526a5a0a` | [RewindDebugger] Replaced included header by forward declaration for TraceService::Frame | 用前向声明替换 TraceService::Frame 的头文件包含 |
| 2026-01-16 | `e2c597c8` | Fix missing debug tracks in rewind debugger for PoseSearch, SequenceInfo, and EvaluationTask when us | 修复回放调试器中缺失的调试轨道 |
| 2026-01-15 | `1be36357` | [Backout] - CL49859133 | 回退之前的改动 |

### 维护评价

该插件创建于 2024 年 5 月，约 1 年历史，属于较新的插件。近期（2026 年 1-4 月）持续有更新，主要集中在 RewindDebugger 集成的维护和 bug 修复，表明仍在活跃维护中。

需要注意的是，该插件标记为 `IsBetaVersion: true` 且 `EnabledByDefault: false`，说明 API 尚未稳定，可能会有变动。作为开发者工具，其使用门槛较高，需要配合 GameplayInsights 和 RewindDebugger 使用。

**推荐度**：如果你的项目大量使用 MVVM 或 FieldNotification 机制且需要调试支持，推荐启用。对于简单的项目，暂无必要。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/FieldNotificationTrace)