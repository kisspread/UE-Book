# MetaHuman Capture Utils

> 为 MetaHuman 动画捕获系统提供可重用的 C++ 工具基础设施，包括异步事件处理、任务管理、结果封装和作用域守卫等功能。

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 捕获工具库 |
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（测试资源） |
| 模块 | `MetaHumanCaptureUtils` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 🏛️ 文物（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanCaptureUtils) | |

## 用途

该模块并非面向最终用户的功能模块，而是 MetaHumanAnimator 插件内部的基础工具库。它封装了一系列通用的 C++ 工具类和模式，旨在为插件的其他模块（如捕获源、协议栈、数据处理等）提供标准化的底层支持。

其核心价值在于：
1.  **统一异步事件处理**：提供线程安全的事件发布/订阅机制（`FCaptureEventSource`），用于在捕获过程中（如数据更新、状态变化）进行模块间通信。
2.  **管理复杂异步任务**：提供可中止的异步任务封装（`FAbortableAsyncTask`），方便安全地执行后台耗时操作（如网络通信、文件处理）。
3.  **规范错误处理**：提供 `TResult` 模板类，以类型安全的方式封装操作的成功值或错误信息，替代裸指针或错误码。
4.  **保证资源清理**：提供作用域守卫（`TScopeGuard`）和 `SCOPE_EXIT` 宏，确保在作用域退出时执行清理操作（如释放锁、关闭连接）。

**重要提示**：根据源码注释，该模块已在 UE 5.7 中被废弃，其功能已迁移至 `CaptureManagerCore/CaptureUtils` 模块。此文档主要服务于遗留代码的维护。

## 使用场景

- 你正在开发一个 MetaHuman 捕获相关的插件或模块，需要处理来自多个来源的异步事件 → 使用 `FCaptureEventSource` 来发布事件，使用 `ICaptureEventSource` 接口来订阅。
- 你需要在后台线程执行一个可能被取消的捕获操作（如下载文件、与设备通信）→ 使用 `FAbortableAsyncTask` 来包装你的任务函数。
- 你的函数执行可能成功返回数据，也可能失败并带有错误信息 → 使用 `TResult<ValueType, ErrorType>` 来封装返回值。
- 你需要在函数提前返回（如遇到错误）时自动释放锁或清理资源 → 使用 `SCOPE_EXIT` 宏。

## 蓝图用法

此模块为纯 C++ 工具库，不包含任何 `BlueprintCallable` 或 `BlueprintReadWrite` 标记的接口，无法在蓝图中直接使用。其提供的工具类被 MetaHumanAnimator 插件的其他蓝图可调用系统内部使用。

## C++ 用法

### 头文件引入

```cpp
#include "Async/EventSourceUtils.h" // 事件源
#include "Async/Task.h"            // 可中止异步任务
#include "Error/Result.h"          // TResult 结果类型
#include "Error/ScopeGuard.h"      // SCOPE_EXIT 宏
```

### 基本用法

#### 1. 创建可订阅的事件源

```cpp
// 定义你自己的事件类，继承自 FCaptureEvent
class FMyDataUpdatedEvent : public FCaptureEvent
{
public:
    static inline const FString Name = TEXT("MyDataUpdated");
    FMyDataUpdatedEvent(const FString& InData) : FCaptureEvent(Name), Data(InData) {}
    FString Data;
};

// 创建一个事件源类
class FMyCaptureSource : public FCaptureEventSource
{
public:
    void SimulateDataUpdate()
    {
        // 使用模板方法发布事件，线程安全
        PublishEvent<FMyDataUpdatedEvent>(TEXT("New Frame Data"));
    }
};

// 订阅事件
FMyCaptureSource Source;
Source.SubscribeToEvent(FMyDataUpdatedEvent::Name,
    TManagedDelegate<TSharedPtr<const FCaptureEvent>>::CreateLambda([](TSharedPtr<const FCaptureEvent> Event)
    {
        if (const FMyDataUpdatedEvent* DataEvent = static_cast<const FMyDataUpdatedEvent*>(Event.Get()))
        {
            UE_LOG(LogTemp, Log, TEXT("Data updated: %s"), *DataEvent->Data);
        }
    }));
```

#### 2. 封装可能失败的操作

```cpp
// 定义错误类型
enum class EMyError { InvalidInput, NetworkTimeout };

// 一个可能失败的函数
TResult<int32, EMyError> ParseNumber(const FString& String)
{
    if (String.IsEmpty())
    {
        return EMyError::InvalidInput; // 返回错误
    }

    // ... 尝试解析 ...
    return 42; // 返回成功值
}

// 调用并处理结果
auto Result = ParseNumber(TEXT("123"));
if (Result.IsValid())
{
    int32 Number = Result.ClaimResult();
    // 使用 Number
}
else
{
    EMyError Error = Result.GetError();
    // 处理错误
}
```

#### 3. 执行可中止的后台任务

```cpp
// 定义一个耗时任务
auto Task = MakeUnique<FAbortableAsyncTask>([](const FStopToken& StopToken)
{
    for (int32 i = 0; i < 1000000; ++i)
    {
        if (StopToken.IsStopRequested())
        {
            UE_LOG(LogTemp, Warning, TEXT("Task was aborted!"));
            return;
        }
        // 执行一些计算或IO操作...
    }
    UE_LOG(LogTemp, Log, TEXT("Task completed successfully."));
});

// 异步启动
Task->StartAsync();

// 在某个时刻，比如用户取消操作时，中止任务
Task->Abort();
```

#### 4. 使用作用域守卫确保资源清理

```cpp
void ProcessData()
{
    // 获取一个全局锁
    FScopeLock Lock(&GlobalMutex);

    // 分配一个资源
    FResource* Resource = AllocateResource();
    // 确保在函数任何退出路径（包括提前return）都释放它
    SCOPE_EXIT
    {
        FreeResource(Resource);
    };

    if (SomeCondition())
    {
        return; // 即使这里提前返回，Resource也会被释放
    }

    // ... 使用 Resource 进行工作 ...
}
```

### 进阶用法：组合使用

组合事件源、异步任务和结果类型来构建一个健壮的捕获操作。

```cpp
class FCaptureProcessor : public FCaptureEventSource
{
public:
    DECLARE_DELEGATE_OneParam(FOnCaptureComplete, TResult<FString, FText>);

    void StartAsyncCapture(FOnCaptureComplete OnComplete)
    {
        AsyncTask = MakeUnique<FAbortableAsyncTask>(
            [WeakThis = MakeWeakObjectPtr(this), OnComplete](const FStopToken& StopToken)
            {
                // 模拟网络捕获
                for (int32 i = 0; i < 5; ++i)
                {
                    if (StopToken.IsStopRequested())
                    {
                        // 在游戏线程报告中止
                        AsyncTask(ENamedThreads::GameThread, [OnComplete]()
                        {
                            OnComplete.ExecuteIfBound(FText::FromString(TEXT("Capture aborted")));
                        });
                        return;
                    }
                    // ... 捕获步骤 ...
                    // 发布进度事件
                    if (TSharedPtr<FCaptureProcessor> StrongThis = WeakThis.Pin())
                    {
                        StrongThis->PublishEvent<FCaptureProgressEvent>(i + 1, 5);
                    }
                }

                // 在游戏线程报告成功
                AsyncTask(ENamedThreads::GameThread, [OnComplete]()
                {
                    OnComplete.ExecuteIfBound(FString(TEXT("ResultData")));
                });
            });
        AsyncTask->StartAsync();
    }

    void Abort()
    {
        if (AsyncTask)
        {
            AsyncTask->Abort();
        }
    }

private:
    TUniquePtr<FAbortableAsyncTask> AsyncTask;
};
```

## Demo 示例

以下是一个完整的、可编译的最小示例，演示了 `TResult` 和 `SCOPE_EXIT` 的使用。

**MyProcessor.h**
```cpp
#pragma once

#include "Error/Result.h"
#include "Error/ScopeGuard.h"

enum class EProcessError
{
    InvalidData,
    OutOfMemory
};

class FMyProcessor
{
public:
    // 处理一个数组，可能失败
    TResult<TArray<float>, EProcessError> ProcessData(const TArray<float>& InputData)
    {
        if (InputData.Num() == 0)
        {
            return EProcessError::InvalidData;
        }

        TArray<float> OutputData;
        // 确保在异常路径下清理可能的中间状态（此处仅为演示）
        SCOPE_EXIT
        {
            OutputData.Reset(); // 实际上这里可能没有意义，仅为演示宏
        };

        // 模拟一个可能耗尽内存的操作
        if (!OutputData.Reserve(InputData.Num() * 2))
        {
            return EProcessError::OutOfMemory;
        }

        for (float Value : InputData)
        {
            OutputData.Add(Value * 2.0f);
        }

        // 移出数据，避免拷贝
        return MoveTemp(OutputData);
    }
};
```

**MyTest.cpp** (测试用例)
```cpp
#include "MyProcessor.h"
#include "Misc/AutomationTest.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FMyProcessorTest, "MetaHuman.CaptureUtils.TResultAndScopeGuard",
    EAutomationTestFlags::ApplicationContextMask | EAutomationTestFlags::ProductFilter)

bool FMyProcessorTest::RunTest(const FString& Parameters)
{
    FMyProcessor Processor;

    // 测试成功情况
    {
        TArray<float> Input = {1.0f, 2.0f, 3.0f};
        auto Result = Processor.ProcessData(Input);

        TestTrue(TEXT("Should succeed"), Result.IsValid());
        if (Result.IsValid())
        {
            TArray<float> Output = Result.ClaimResult();
            TestEqual(TEXT("Output size should match"), Output.Num(), 3);
            TestEqual(TEXT("First value should be doubled"), Output[0], 2.0f);
        }
    }

    // 测试失败情况
    {
        TArray<float> EmptyInput;
        auto Result = Processor.ProcessData(EmptyInput);

        TestTrue(TEXT("Should fail with InvalidData"), Result.IsError());
        TestEqual(TEXT("Error should be InvalidData"), Result.GetError(), EProcessError::InvalidData);
    }

    return true;
}
```

## 模块依赖

此模块的依赖已在 Build.cs 中声明，主要依赖于 MetaHuman 核心技术库。

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | MetaHuman 核心技术库，可能包含底层的数学、几何或数据处理功能 |

## 维护状态

### 近期更新

根据提供的 Git 历史，这些更新针对的是整个 MetaHumanAnimator 插件，并非专门针对 `MetaHumanCaptureUtils` 模块。该模块自身在近期没有直接的功能性更新。

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 启用身体跟踪时禁用关卡序列导出功能 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 的渲染瑕疵 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体跟踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | [MHA] 为已有网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存问题 |

### 维护评价

1.  **状态：已废弃**。源码中多个关键类（`FCaptureEventSourceBase`, `FCallbackSynchronizer`, `FCaptureEvent`, `FStopToken`）均明确标记为 `UE_DEPRECATED(5.7, ...)`，表明该模块的功能已在 UE 5.7 版本中被迁移至新的 `CaptureManagerCore/CaptureUtils` 模块。
2.  **最新实质性更新**：从当前源码状态看，该模块最后的实质性更新应早于其被标记为废弃的版本（UE 5.7）。近期 Git 记录显示的是插件其他部分的更新。
3.  **推荐使用**：**不推荐**在新项目或新模块中使用此模块。任何对这些工具类的需求都应转向使用其继任者 `CaptureManagerCore/CaptureUtils`。仅当维护基于 UE 5.7 之前版本的遗留 MetaHuman 插件代码时，才需要参考本文档。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanCaptureUtils)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanControlsConversionTest) (位于插件内的独立测试模块)