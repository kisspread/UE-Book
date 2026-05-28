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
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/FieldNotificationTrace) | |

## 用途

此插件是 **MVVM (Model-View-ViewModel) 调试工具链**的一部分，旨在解决字段通知（Field Notification）机制的运行时调试问题。

在 Unreal 的 MVVM 模式中，数据模型（Model）通常使用 `FieldNotify` 属性来标记哪些字段变化需要通知视图（View）更新。然而，当这些通知没有按预期触发、触发顺序错误或引起性能问题时，开发者缺乏有效的诊断手段。

`FieldNotificationTrace` 通过集成 Unreal Insights 和 **Rewind Debugger**，实现了对字段通知事件的**实时捕获与可视化**。它允许开发者在时间轴上精确回放，查看哪个对象的哪个字段在何时发生了变化，从而快速定位数据绑定相关的问题。

## 使用场景

- **MVVM 架构调试**：你使用 UE 的 MVVM 框架构建 UI，但发现某个字段变化后界面未更新，或者更新不正确。启用此插件后，可以在 Rewind Debugger 中查看该字段的通知是否被正确发出，以及发出的时机。
- **数据同步问题排查**：在多对象交互的复杂逻辑中，需要追踪某个关键数据字段（如玩家生命值、任务状态）的变化历史，以分析同步逻辑的正确性。
- **性能分析**：如果怀疑频繁的字段通知导致了性能瓶颈，可以通过追踪工具分析通知的频率和来源。
- **自动化测试验证**：在自动化测试中，可以结合追踪提供的数据，验证特定操作后字段通知是否被正确触发。

## 蓝图用法

此插件主要提供编辑器调试功能，**不暴露**任何供游戏逻辑调用的蓝图节点。其核心功能是通过编辑器 UI（如 Rewind Debugger）呈现的。

## C++ 用法

此插件的使用通常隐含在开发流程中（通过启用插件和使用 Rewind Debugger），开发者无需直接调用其 C++ API。然而，其内部实现遵循了 TraceServices 的标准模式。

### 头文件引入

由于是内部实现，通常无需直接引入。相关核心概念定义在：
```cpp
#include "FieldNotification/FieldNotificationId.h"
```

### 基本用法 (从测试逻辑推断)

插件的核心是提供追踪数据。以下是模拟其追踪目标（字段通知）的简化示例，展示了其需要监控的数据类型。
**来源**: 基于 `FTraceAnalyzer` 和 `FTraceProvider` 的设计推断。
```cpp
#include "FieldNotification/FieldNotificationId.h"
#include "UObject/Class.h"

// 定义一个带有 FieldNotify 属性的类
UCLASS()
class UMyViewModel : public UObject
{
    GENERATED_BODY()

public:
    UPROPERTY(BlueprintReadWrite, FieldNotify, Category="Data")
    int32 Health = 100;

    // 这个函数可能会被插件内部追踪
    void SetHealth(int32 NewHealth)
    {
        if (Health != NewHealth)
        {
            Health = NewHealth;
            // FieldNotification 系统会在此处记录变化事件
        }
    }
};
```

### 进阶用法 (模拟追踪验证)

在插件的测试或验证场景中，可以模拟触发字段通知并检查追踪记录是否正确。
**来源**: 基于 `FTraceProvider` 的 `AppendFieldValueChanged` 方法逻辑。
```cpp
#include "FieldNotification/FieldNotificationId.h"
#include "TraceServices/Model/AnalysisSession.h"
#include "TraceServices/AnalysisService.h"

void SimulateAndVerifyTrace()
{
    // 1. 创建一个分析会话和 Provider (插件内部逻辑)
    TraceServices::IAnalysisSession& Session = TraceServices::GetSession(TEXT("TestSession"));
    UE::FieldNotification::FTraceProvider Provider(Session);

    // 2. 模拟一个对象生命周期
    const uint64 ObjectId = 12345;
    Provider.AppendObjectBegin(ObjectId, FPlatformTime::Seconds());
    Provider.AppendObjectEnd(ObjectId, FPlatformTime::Seconds() + 1.0);

    // 3. 模拟字段变化
    const FFieldNotificationId HealthField(FName("Health"));
    const uint32 HealthFieldId = HealthField.GetFieldId(); // 需要插件注册字段ID
    Provider.AppendFieldValueChanged(ObjectId, FPlatformTime::Seconds(), FPlatformTime::Seconds(), HealthFieldId);

    // 4. 查询并验证 (在编辑器插件中或测试中)
    Provider.EnumerateFieldNotifies(ObjectId, 0.0, 10.0, [](double StartTime, double EndTime, uint32 Depth, const UE::FieldNotification::FTraceProvider::FFieldNotifyEvent& Event)
    {
        UE_LOG(LogTemp, Log, TEXT("Field %u changed at time %f"), Event.FieldNotifyId, StartTime);
        // 此处可加入测试断言，验证 Event.FieldNotifyId 是否匹配 HealthFieldId
    });
}
```

## Demo 示例

一个最小的自动化测试示例，验证字段通知追踪功能。
**文件**: `FieldNotificationTraceTest.cpp`

```cpp
// FieldNotificationTraceTest.h
#pragma once

#include "CoreMinimal.h"
#include "Misc/AutomationTest.h"
#include "FieldNotification/FieldNotificationId.h"

class FFieldNotificationTraceTestBase : public FAutomationTestBase
{
public:
    FFieldNotificationTraceTestBase(const FString& InName, const bool bInComplexTest)
        : FAutomationTestBase(InName, bInComplexTest)
    {
    }
    virtual uint32 GetTestFlags() const override { return EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter; }
};

// FieldNotificationTraceTest.cpp
#include "FieldNotificationTraceTest.h"
#include "TraceServices/Model/AnalysisSession.h"
#include "TraceServices/AnalysisService.h"
#include "FieldNotificationTrace/FieldNotificationTraceProvider.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFieldNotificationTraceBasicTest,
    "FieldNotificationTrace.Basic.Test",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FFieldNotificationTraceBasicTest::RunTest(const FString& Parameters)
{
    // 使用 Unreal Insights 分析会话
    TraceServices::IAnalysisSession& Session = TraceServices::GetSession(TEXT("FieldNotificationTest"));
    UE::FieldNotification::FTraceProvider Provider(Session);

    // 测试1: 对象生命周期追踪
    const uint64 TestObjectId = 1001;
    Provider.AppendObjectBegin(TestObjectId, 0.0);
    TestTrue("Provider has data for object after begin", Provider.HasData(TestObjectId));
    Provider.AppendObjectEnd(TestObjectId, 1.0);

    // 测试2: 字段变化追踪
    const FFieldNotificationId TestField(FName("TestValue"));
    const uint32 TestFieldId = 1; // 假设 ID
    Provider.AppendFieldValueChanged(TestObjectId, 0.5, 0.5, TestFieldId);
    TestTrue("Provider has data after field change", Provider.HasData());

    bool bFoundEvent = false;
    Provider.EnumerateFieldNotifies(TestObjectId, 0.0, 1.0,
        [&](double, double, uint32, const UE::FieldNotification::FTraceProvider::FFieldNotifyEvent& Event)
    {
        if (Event.FieldNotifyId == TestFieldId)
        {
            bFoundEvent = true;
        }
    });
    TestTrue("Found the recorded field notify event", bFoundEvent);

    return true;
}
```

## 模块依赖

插件自身依赖特定的调试和追踪框架，因此你的项目（或使用其数据的编辑器模块）可能需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `GameplayInsights` | 提供了插件所依赖的 Insight 追踪分析框架和 Rewind Debugger 集成基础设施 |
| `RewindDebugger` | 核心依赖，插件为其添加了字段通知的轨道和数据源 |
| `TraceServices` | UE 内部追踪和分析服务的基础模块 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-01 | `fb04ebb6` | [MassDebug] | 集成 MassDebug 相关功能或修复 |
| 2026-03-30 | `6004f575` | [RewindDebugger] | 对接或适配 Rewind Debugger 的更新 |
| 2026-01-16 | `526a5a0a` | [RewindDebugger] Replaced included header by forward declaration for TraceService::Frame | 代码优化：用前向声明替代了不必要的头文件包含 |
| 2026-01-16 | `e2c597c8` | Fix missing debug tracks in rewind debugger for PoseSearch, SequenceInfo, and EvaluationTask when us | 修复了多个动画/任务模块在调试器中轨道缺失的问题，涉及协同修复 |
| 2026-01-15 | `1be36357` | [Backout] - CL49859133 | 回退了某个之前的提交（可能是引入了问题） |

### 维护评价

- **状态**：**实验性且处于积极开发中**。
- **依据**：
    1.  插件标记为 `IsBetaVersion=true` 且 `EnabledByDefault=false`，表明它尚未完全稳定。
    2.  创建时间（2024年5月）很近，是一个**非常年轻**的插件。
    3.  **Git 历史显示其在 2026 年初仍在进行重要更新和修复**，特别是与核心调试框架（RewindDebugger, MassDebug）的集成工作，证明其仍在积极维护和演进。
- **建议**：此插件是 UE5 MVVM 生态的重要调试工具。如果你的项目深度使用 MVVM 的 `FieldNotify`，**强烈建议在开发期间启用此插件**以极大提升调试效率。由于是实验性插件，在打包发布时应禁用它。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/FieldNotificationTrace)
- [官方文档](https://docs.unrealengine.com/)（暂无专门文档，功能描述可参考 MVVM 和 Rewind Debugger 相关文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/FieldNotificationTrace/Tests)（路径为推测，需验证）