# Field Notification Trace

> Add support to trace field notification object.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 字段通知追踪 |
| 分类 | UI |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `FieldNotificationTrace` (Runtime), `FieldNotificationTraceEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-05-24 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/FieldNotificationTrace) | |

## 用途

Field Notification Trace 是一个用于调试字段通知（Field Notification）机制的开发者工具。它解决了在使用 Unreal Engine 的字段通知系统（通常用于 MVVM 架构或 UI 数据绑定）时，难以追踪特定字段值变更原因和时机的问题。此插件通过集成到 **Rewind Debugger** 中，为开发者提供了可视化的追踪轨道，可以记录并回放字段通知对象的生命周期以及字段值发生变化的事件，从而极大地简化了 UI 数据绑定相关 Bug 的调试过程。

## 使用场景

- **你正在使用 MVVM 框架或自定义的字段通知系统来构建 UI**，当某个 UI 控件的显示值不符合预期时，可以使用此插件追踪是哪个数据源的字段值发生了变化，以及变化的具体时间点。
- **你需要调试一个复杂的、依赖多个数据源的 UI 界面**，此插件可以帮助你理清数据流动和更新的顺序。
- **你在开发一个需要高响应性和数据一致性的编辑器工具或运行时 UI**，并希望确保所有字段变更都被正确处理和响应。

## 蓝图用法

此插件主要通过 C++ 宏提供追踪功能，不直接暴露传统的蓝图节点。其调试信息通过 **Rewind Debugger** 的界面进行查看和分析。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| （无直接蓝图节点） | 此插件功能通过 C++ 宏集成，调试界面通过 Rewind Debugger 提供。 | N/A |

## C++ 用法

此插件的核心是提供一组用于在 C++ 代码中插入追踪点的宏。

### 头文件引入

要使用追踪宏，通常需要包含以下头文件，该文件会检查 `UE_FIELDNOTIFICATION_TRACE_ENABLED` 宏是否定义：
```cpp
#include "Trace/FieldNotificationTrace.h"
```

### 基本用法

在实现字段通知接口的类中，在对象创建和销毁时插入生命周期追踪宏。当字段值发生变化时，插入字段值更新追踪宏。

```cpp
// 假设你的类继承自 INotifyFieldValueChanged 接口
// 你的类创建时（如构造函数或初始化函数）
{
    UE_TRACE_FIELDNOTIFICATION_LIFETIME_BEGIN(this);
}

// 你的类销毁时（如析构函数）
{
    UE_TRACE_FIELDNOTIFICATION_LIFETIME_END(this);
}

// 当你更新一个字段的值并准备广播通知时
void UMyViewModel::SetMyValue(int32 NewValue)
{
    if (MyValue != NewValue)
    {
        MyValue = NewValue;
        // 广播字段变化通知之前或之后，插入追踪点
        // FFieldId 是通过 UE_FIELD_NOTIFICATION_DECLARE_FIELD 宏定义的
        UE_TRACE_FIELDNOTIFICATION_FIELD_VALUE_CHANGED(this, UMyViewModel::MyValueFieldId);
        // ... 广播通知 ...
    }
}
```

*（来源：根据 Public/Trace/FieldNotificationTrace.h 中宏定义推断的通用用法）*

### 进阶用法

结合 `FTrace` 类的静态方法，可以在不使用宏的情况下进行更灵活的追踪控制。

```cpp
#include "Trace/FieldNotificationTrace.h"

// 手动开始追踪一个对象的生命周期
TScriptInterface<INotifyFieldValueChanged> InterfacePtr = this;
UE::FieldNotification::FTrace::OutputObjectBegin(InterfacePtr);

// ... 对象存在期间的操作 ...

// 手动报告某个字段的值已更新
FFieldId MyFieldId = UMyViewModel::MyValueFieldId; // 通常由宏生成
UE::FieldNotification::FTrace::OutputUpdateField(this, MyFieldId);

// 对象结束前
UE::FieldNotification::FTrace::OutputObjectEnd(InterfacePtr);
```

*（来源：Public/Trace/FieldNotificationTrace.h 中的 FTrace 类 API）*

## Demo 示例

以下是一个最小示例，展示如何在一个自定义的 ViewModel 类中集成字段通知追踪。

**MyTraceableViewModel.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "UObject/Interface.h"
#include "UObject/NoExportTypes.h"
#include "INotifyFieldValueChanged.h"
#include "Trace/FieldNotificationTrace.h" // 包含追踪宏
#include "MyTraceableViewModel.generated.h"

UCLASS(BlueprintType)
class UMyTraceableViewModel : public UObject, public INotifyFieldValueChanged
{
    GENERATED_BODY()

public:
    UMyTraceableViewModel();
    virtual ~UMyTraceableViewModel();

    // 字段声明
    UE_FIELD_NOTIFICATION_DECLARE_CLASS_DESCRIPTOR;
    UE_FIELD_NOTIFICATION_DECLARE_FIELD(MyName);
    UE_FIELD_NOTIFICATION_DECLARE_FIELD(MyScore);

    UFUNCTION(BlueprintCallable, Category = "ViewModel")
    void SetMyName(const FString& NewName);

    UFUNCTION(BlueprintCallable, Category = "ViewModel")
    void SetMyScore(int32 NewScore);

    // INotifyFieldValueChanged 接口实现
    virtual FFieldValueChangedDelegate& GetFieldValueChangedDelegate(FFieldId InFieldId) override;
    virtual void BroadcastFieldValueChanged(FFieldId InFieldId) override;

private:
    FString MyName;
    int32 MyScore;
    FFieldValueChangedDelegate FieldValueChangedDelegate;
};
```

**MyTraceableViewModel.cpp**
```cpp
#include "MyTraceableViewModel.h"
#include "FieldNotification/FieldNotification.h"

// 初始化类描述符
UE_FIELD_NOTIFICATION_IMPLEMENT_CLASS(UMyTraceableViewModel, TEXT("MyTraceableViewModel"))
UE_FIELD_NOTIFICATION_IMPLEMENT_FIELD(UMyTraceableViewModel, MyName)
UE_FIELD_NOTIFICATION_IMPLEMENT_FIELD(UMyTraceableViewModel, MyScore)

UMyTraceableViewModel::UMyTraceableViewModel()
{
    // 在对象创建时开始生命周期追踪
    UE_TRACE_FIELDNOTIFICATION_LIFETIME_BEGIN(this);
}

UMyTraceableViewModel::~UMyTraceableViewModel()
{
    // 在对象销毁时结束生命周期追踪
    UE_TRACE_FIELDNOTIFICATION_LIFETIME_END(this);
}

void UMyTraceableViewModel::SetMyName(const FString& NewName)
{
    if (MyName != NewName)
    {
        MyName = NewName;
        // 追踪字段值变化
        UE_TRACE_FIELDNOTIFICATION_FIELD_VALUE_CHANGED(this, UMyViewModel::MyNameFieldId);
        BroadcastFieldValueChanged(UMyViewModel::MyNameFieldId);
    }
}

void UMyTraceableViewModel::SetMyScore(int32 NewScore)
{
    if (MyScore != NewScore)
    {
        MyScore = NewScore;
        // 追踪字段值变化
        UE_TRACE_FIELDNOTIFICATION_FIELD_VALUE_CHANGED(this, UMyViewModel::MyScoreFieldId);
        BroadcastFieldValueChanged(UMyViewModel::MyScoreFieldId);
    }
}

FFieldValueChangedDelegate& UMyTraceableViewModel::GetFieldValueChangedDelegate(FFieldId InFieldId)
{
    return FieldValueChangedDelegate;
}

void UMyTraceableViewModel::BroadcastFieldValueChanged(FFieldId InFieldId)
{
    FieldValueChangedDelegate.Broadcast(InFieldId);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GameplayInsights` | 作为父插件提供基础的 Insights 框架和调试功能。 |
| `RewindDebugger` | 提供回放调试器的框架和 UI，用于展示字段通知追踪轨道。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-01 | `fb04ebb6` | [MassDebug] | 集成到 MassDebug 框架中，增强大规模实体调试能力。 |
| 2026-03-30 | `6004f575` | [RewindDebugger] | 围绕 RewindDebugger 进行调整或集成。 |
| 2026-01-16 | `526a5a0a` | [RewindDebugger] Replaced included header by forward declaration for TraceService::Frame | 优化头文件依赖，用前向声明替代完整包含，编译优化。 |
| 2026-01-16 | `e2c597c8` | Fix missing debug tracks in rewind debugger for PoseSearch, SequenceInfo, and EvaluationTask when us | 修复多个调试轨道在特定情况下缺失的显示问题。 |
| 2026-01-15 | `1be36357` | [Backout] - CL49859133 | 回退了之前的某个提交。 |

### 维护评价

该插件创建于 2024 年 5 月，历史较短。最近一次更新在 2026 年 4 月，表明其仍在**活跃维护**中，并且持续集成到新的调试框架（如 MassDebug）中。由于它是 `IsBetaVersion=true` 且 `EnabledByDefault=false` 的实验性插件，**推荐仅在需要调试 UI 数据绑定问题时手动启用**。其功能相对专一，但作为开发和调试工具，对于解决复杂的 UI 数据流问题非常有价值。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/FieldNotificationTrace)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/FieldNotificationTrace/Tests)（如果存在）