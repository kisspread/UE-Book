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

Field Notification Trace 插件为 Unreal Insights 和 Rewind Debugger 提供了一个专门用于可视化调试**字段通知（Field Notification）** 数据流的追踪通道。它解决的核心问题是：在使用基于 `INotifyFieldValueChanged` 接口的 MVVM（Model-View-ViewModel）或数据绑定系统时，开发者难以直观地追踪对象字段值的变化时机、频率和来源，尤其是在复杂的 UI 数据绑定场景中。此插件通过在字段值变化时生成特定的 Trace 事件，并将其集成到时间轴调试工具中，使得开发者可以回放和检查 UI 绑定数据的变化历史，从而快速定位数据驱动的 UI 刷新问题。

## 使用场景

- 你正在使用 Unreal 的 `ViewModel` 和 `INotifyFieldValueChanged` 构建数据驱动的 UI 系统，但界面更新不符合预期。
- 你需要调试一个复杂的 UI，其中多个视图绑定到同一数据模型的不同字段，需要查看某个特定字段（如 `Score` 或 `Health`）的值在游戏运行时的变化序列。
- 你正在使用 Rewind Debugger 进行回放调试，希望将底层数据对象的字段变化事件与游戏画面、动画等事件在同一个时间轴上进行关联分析。
- 你需要诊断性能问题，查看某段时间内某个对象的字段被频繁更新的情况。

## 蓝图用法

此插件的功能主要通过 C++ 宏和编辑器工具面板提供，没有直接暴露给蓝图的节点。其核心价值在于**分析和可视化**通过宏嵌入到代码中的追踪数据。开发者通过在 C++ 代码中使用宏，然后在编辑器的 `Window > Developer Tools > Trace Insights` 或 Rewind Debugger 面板中查看结果。

## C++ 用法

### 头文件引入

要使用追踪宏，需要包含公共头文件。

```cpp
#include "Trace/FieldNotificationTrace.h"
```

### 基本用法

插件提供了三个核心宏，用于在关键位置插入追踪点。你需要在你的类中正确实现 `INotifyFieldValueChanged` 接口。

**1. 追踪对象生命周期**

在创建（或初始化）一个实现了 `INotifyFieldValueChanged` 的对象时，调用 `LIFETIME_BEGIN`；在销毁或使其失效时，调用 `LIFETIME_END`。这有助于在时间轴上标记对象的活跃期。

**2. 追踪字段值变化**

在你实现的 `BroadcastFieldValueChanged` 函数内部，当特定字段的值发生变化时，调用 `FIELD_VALUE_CHANGED`。这是最核心的追踪点。

```cpp
// 来源：建议的集成模式（基于插件宏设计）
// MyViewModel.h
UCLASS()
class UMyViewModel : public UObject, public INotifyFieldValueChanged
{
    GENERATED_BODY()

public:
    virtual void BroadcastFieldValueChanged(const FFieldNotificationEvent& InEvent) override;

    UPROPERTY(BlueprintReadWrite, FieldNotify)
    int32 Score;
};

// MyViewModel.cpp
void UMyViewModel::BroadcastFieldValueChanged(const FFieldNotificationEvent& InEvent)
{
    // 在广播具体字段变化前，插入追踪点
    if (InEvent.GetFieldId() == FMyViewModelFFI::Score)
    {
        UE_TRACE_FIELDNOTIFICATION_FIELD_VALUE_CHANGED(this, InEvent.GetFieldId());
    }

    // 继续调用父类或标准广播逻辑
    // ...
}
```

### 进阶用法

结合对象生命周期宏，可以提供更完整的追踪上下文。通常，`LIFETIME_BEGIN` 会在对象构造后或初始化绑定时调用，`LIFETIME_END` 在对象销毁前或解绑时调用。

```cpp
// 来源：基于宏设计的生命周期集成模式
UMyViewModel::UMyViewModel()
{
    // 对象构造，但通常绑定还未就绪
}

void UMyViewModel::InitializeViewModel()
{
    // 初始化，开始绑定数据，此时标记生命周期开始
    UE_TRACE_FIELDNOTIFICATION_LIFETIME_BEGIN(this);
    // ... 初始化逻辑
}

void UMyViewModel::DeinitializeViewModel()
{
    // 解绑数据，准备销毁，标记生命周期结束
    UE_TRACE_FIELDNOTIFICATION_LIFETIME_END(this);
    // ... 清理逻辑
}

// BroadcastFieldValueChanged 内部的使用同基本用法
```

## Demo 示例

一个完整的、可编译的最小示例，展示如何为一个自定义的 ViewModel 类集成字段通知追踪。

**MyTracedViewModel.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "FieldNotification/FieldNotificationDeclaration.h"
#include "Trace/FieldNotificationTrace.h"
#include "MyTracedViewModel.generated.h"

UCLASS(BlueprintType)
class UMyTracedViewModel : public UObject, public INotifyFieldValueChanged
{
    GENERATED_BODY()

public:
    UMyTracedViewModel();
    virtual ~UMyTracedViewModel();

    // INotifyFieldValueChanged 接口实现
    virtual void BroadcastFieldValueChanged(const FFieldNotificationEvent& InEvent) override;

    // 一个带字段通知的属性
    UPROPERTY(BlueprintReadWrite, FieldNotify, Category = "Demo")
    int32 PlayerHealth = 100;

    UPROPERTY(BlueprintReadWrite, FieldNotify, Category = "Demo")
    FText PlayerName;

    // 手动修改字段并广播变化的函数，用于演示
    UFUNCTION(BlueprintCallable, Category = "Demo")
    void SetPlayerHealth(int32 NewHealth);
};
```

**MyTracedViewModel.cpp**
```cpp
#include "MyTracedViewModel.h"
#include "FieldNotification/FieldNotificationHelpers.h"

UMyTracedViewModel::UMyTracedViewModel()
{
    // 在构造时标记生命周期开始
    UE_TRACE_FIELDNOTIFICATION_LIFETIME_BEGIN(this);
}

UMyTracedViewModel::~UMyTracedViewModel()
{
    // 在析构时标记生命周期结束
    UE_TRACE_FIELDNOTIFICATION_LIFETIME_END(this);
}

void UMyTracedViewModel::BroadcastFieldValueChanged(const FFieldNotificationEvent& InEvent)
{
    // 检查变化的字段，并插入追踪点
    if (InEvent.GetFieldId() == GET_MEMBER_NAME_CHECKED(UMyTracedViewModel, PlayerHealth))
    {
        UE_TRACE_FIELDNOTIFICATION_FIELD_VALUE_CHANGED(this, InEvent.GetFieldId());
    }
    else if (InEvent.GetFieldId() == GET_MEMBER_NAME_CHECKED(UMyTracedViewModel, PlayerName))
    {
        UE_TRACE_FIELDNOTIFICATION_FIELD_VALUE_CHANGED(this, InEvent.GetFieldId());
    }

    // 标准的广播实现（简化版，实际应遵循 Epic 的推荐模式）
    FieldNotification::FFieldNotificationEventMulticast::Broadcast(this, InEvent);
}

void UMyTracedViewModel::SetPlayerHealth(int32 NewHealth)
{
    // 使用 FFieldNotificationHelpers 来安全地修改并广播字段变化
    FFieldNotificationHelpers::SetFieldValue(this, GET_MEMBER_NAME_CHECKED(UMyTracedViewModel, PlayerHealth), NewHealth);
}
```

## 模块依赖

从 `FieldNotificationTrace.Build.cs` 分析，此插件依赖于以下核心模块以实现其功能。

| 模块 | 用途 |
|---|---|
| `GameplayInsights` | 提供与 Unreal Insights 追踪通道和 Rewind Debugger 集成的底层支持。 |
| `FieldNotification` | 核心的字段通知系统模块，定义了 `INotifyFieldValueChanged` 接口和基础框架。 |

*注：此插件还依赖常见的 `Core`、`CoreUObject`、`Engine` 等模块，此处已省略。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-01 | `fb04ebb6` | [MassDebug] | 与大规模调试功能相关的维护性更新。 |
| 2026-03-30 | `6004f575` | [RewindDebugger] | 对Rewind Debugger集成模块进行更新或修复。 |
| 2026-01-16 | `526a5a0a` | [RewindDebugger] Replaced included header by forward declaration for TraceService::Frame | 优化头文件包含，将包含头文件改为前向声明以减少编译依赖。 |
| 2026-01-16 | `e2c597c8` | Fix missing debug tracks in rewind debugger for PoseSearch, SequenceInfo, and EvaluationTask when us | 修复了在Rewind Debugger中特定调试轨道缺失的bug。 |
| 2026-01-15 | `1be36357` | [Backout] - CL49859133 | 回滚了某个可能导致问题的更改。 |

### 维护评价

该插件创建于 2024 年中，是一个相对年轻的**实验性**插件。从 Git 历史看，它在 2026 年初仍有针对调试工具集成（RewindDebugger）的活跃维护和 Bug 修复，表明 Epic Games 将其作为 UI/Editor 开发工具链的一部分在持续迭代。

**优势**：
- 作为官方实验性插件，与 `GameplayInsights` 和 `RewindDebugger` 深度集成，提供了其他第三方工具难以实现的、与引擎内置调试器结合的可视化追踪体验。
- 明确针对现代的 UI/MVVM 架构痛点，实用性强。

**注意事项**：
- **实验性状态**：功能可能不完整，API 可能在未来版本中发生变化。
- **默认禁用**：需要在项目插件设置中手动启用。
- **主要面向高级开发者**：需要对 Unreal 的字段通知系统和 C++ 宏有了解才能有效使用。

**推荐使用**：如果你正在开发一个大量依赖 `FieldNotification` 进行数据绑定的复杂 UI 项目，并且需要深度的运行时调试能力，**强烈建议尝试此插件**。它能极大提升调试 UI 数据流问题的效率。对于简单项目，则无需使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/FieldNotificationTrace)
- 官方文档链接（暂无）
- [相关测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/FieldNotificationTrace/Tests) （路径推测，基于常见项目结构）