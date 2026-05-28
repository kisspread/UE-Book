# MetaHuman Capture Utils

> A collection of low-level async utilities for the MetaHuman capture pipeline.

| 属性 | 值 |
|---|---|
| 中文名 | 捕获工具集 |
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `MetaHumanCaptureUtils` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 未知 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanCaptureUtils) | |

**⚠️ 重要提示**: 该模块已在 UE 5.7 中被标记为**废弃 (Deprecated)**。其功能已迁移至 `CaptureManagerCore/CaptureUtils` 模块。新项目应避免使用此模块，并考虑迁移至新模块。本文档内容主要用于理解和维护遗留代码。

## 用途

`MetaHumanCaptureUtils` 是一个底层工具模块，为 MetaHuman Animator 的捕获管线提供核心的异步编程和错误处理工具。它并不是直接面向用户的高层功能，而是服务于捕获数据摄入、面部跟踪、动画解决等流程的内部基础设施。主要解决在复杂、可能多线程的捕获与处理流程中，如何安全地发布事件、同步异步回调、管理后台任务以及优雅地处理错误等基础架构问题。

## 使用场景

该模块的组件被其他 MetaHuman Animator 模块（如 `MetaHumanCaptureSource`, `MetaHumanFaceContourTracker`）内部广泛使用。典型的场景包括：
- 在捕获设备（如iPhone的ARKit）实时获取数据时，通过事件系统（`FCaptureEventSource`）向多个处理器广播状态更新或捕获事件。
- 同时启动多个异步面部特征点跟踪任务，并使用回调同步器（`FCallbackSynchronizer`）等待所有任务完成后再执行下一步（如动画解决）。
- 在后台线程执行耗时的数据导入或处理任务，并提供中途取消的能力（`FAbortableAsyncTask`）。

## 蓝图用法

`MetaHumanCaptureUtils` 模块主要提供 C++ 层面的底层工具类，其大部分核心类（如模板化的 `TResult`, `TManagedDelegate`）**没有直接暴露为蓝图节点**。它主要作为其他高级模块（如 `MetaHumanCaptureSource`, `MetaHumanPerformance`）的底层支撑，而这些高级模块可能会将功能封装为蓝图可用的节点。

### 核心节点

此模块本身不直接提供蓝图节点。

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanCaptureUtils/Async/EventSourceUtils.h"
#include "MetaHumanCaptureUtils/Async/CallbackSynchronizer.h"
#include "MetaHumanCaptureUtils/Async/Task.h"
#include "MetaHumanCaptureUtils/Error/Result.h"
#include "MetaHumanCaptureUtils/Error/ScopeGuard.h"
```

### 基本用法

**1. 使用 `TResult` 进行错误处理**
`TResult` 是一个类似于 Rust 的 `Result` 或 C++ 的 `std::expected` 的模板类，用于函数返回值，明确区分成功结果和错误。
*(来源: `Public/Error/Result.h`)*

```cpp
#include "MetaHumanCaptureUtils/Error/Result.h"

// 定义一个错误类型
struct FMyError
{
    FString Message;
};

// 返回类型可以是 TResult<成功类型, 错误类型>
TResult<int32, FMyError> Divide(int32 a, int32 b)
{
    if (b == 0)
    {
        return FMyError{TEXT("Division by zero")}; // 返回错误
    }
    return a / b; // 返回结果
}

void UseTResult()
{
    auto Result = Divide(10, 2);
    if (Result.IsValid())
    {
        int32 Value = Result.GetResult(); // 获取成功值
    }
    else if (Result.IsError())
    {
        FMyError Error = Result.GetError(); // 获取错误
        UE_LOG(LogTemp, Warning, TEXT("Error: %s"), *Error.Message);
    }
}

// 对于无返回值（void）但可能失败的操作
TResult<void, FMyError> PerformOperation()
{
    bool bSuccess = true; // ... 执行操作
    if (!bSuccess)
    {
        return FMyError{TEXT("Operation failed")};
    }
    return ResultOk; // 表示成功
}
```

**2. 使用 `FCallbackSynchronizer` 同步多个异步回调**
当需要等待多个异步操作全部完成后再执行某个函数时使用。
*(来源: `Public/Async/CallbackSynchronizer.h`)*

```cpp
#include "MetaHumanCaptureUtils/Async/CallbackSynchronizer.h"

void AsyncTaskSimulation(const FCallbackSynchronizer::FAfterAllDelegate& OnComplete)
{
    // ... 模拟一个异步任务完成后的回调
    OnComplete.ExecuteIfBound();
}

void UseCallbackSynchronizer()
{
    // 创建同步器实例
    auto Sync = FCallbackSynchronizer::Create();

    // 创建带计数的回调。每创建一个，内部计数器+1
    auto Callback1 = Sync->CreateCallback([](){ UE_LOG(LogTemp, Log, TEXT("Task 1 Done")); });
    auto Callback2 = Sync->CreateCallback([](){ UE_LOG(LogTemp, Log, TEXT("Task 2 Done")); });

    // 模拟将回调传递给异步任务
    AsyncTaskSimulation(Callback1);
    AsyncTaskSimulation(Callback2);

    // 当所有被创建的回调都被执行后（计数器归零），将执行 AfterAll 的委托
    Sync->AfterAll(FCallbackSynchronizer::FAfterAllDelegate::CreateLambda([]()
    {
        UE_LOG(LogTemp, Log, TEXT("All tasks completed!"));
    }));
}
```

**3. 使用 `FAbortableAsyncTask` 执行可中止的后台任务**
*(来源: `Public/Async/Task.h`)*

```cpp
#include "MetaHumanCaptureUtils/Async/Task.h"

void UseAbortableAsyncTask()
{
    // 创建一个可以访问 FStopToken 以判断是否应中止的任务
    auto AbortableTask = new FAbortableAsyncTask([](const FStopToken& StopToken)
    {
        for (int32 i = 0; i < 100; ++i)
        {
            // 在耗时操作前检查中止信号
            if (StopToken.IsStopRequested())
            {
                UE_LOG(LogTemp, Log, TEXT("Task aborted at step %d"), i);
                return;
            }
            // 模拟耗时工作
            FPlatformProcess::Sleep(0.1f);
        }
        UE_LOG(LogTemp, Log, TEXT("Task completed normally"));
    });

    // 在后台线程启动
    AbortableTask->StartAsync();

    // ... 在某个时刻（例如用户点击取消）请求中止
    // AbortableTask->Abort();

    // 析构函数会确保任务完成（如果还未中止），避免悬垂线程。
    delete AbortableTask;
}
```

**4. 使用 `FCaptureEventSource` 发布/订阅事件**
*(来源: `Public/Async/EventSourceUtils.h`, `Public/Async/Event.h`)*

```cpp
#include "MetaHumanCaptureUtils/Async/EventSourceUtils.h"
#include "MetaHumanCaptureUtils/Async/Event.h"

// 1. 定义自定义事件
METAHUMAN_CAPTURE_DEFINE_EMPTY_EVENT(FMyCaptureStartEvent, "MyCaptureStart");

// 2. 创建一个事件源类
class FMyCaptureDevice : public FCaptureEventSource
{
public:
    void StartCapture()
    {
        // 发布事件，所有订阅了 “MyCaptureStart” 的处理器都会收到通知
        PublishEvent<FMyCaptureStartEvent>();
        // ... 开始捕获逻辑
    }
};

// 3. 订阅并处理事件
void SubscribeToEvents()
{
    FMyCaptureDevice Device;
    
    // 创建一个处理函数，这里使用 TManagedDelegate 确保在游戏线程执行
    FCaptureEventHandler Handler(
        [](TSharedPtr<const FCaptureEvent> Event)
        {
            UE_LOG(LogTemp, Log, TEXT("Received event: %s"), *Event->GetName());
        },
        EDelegateExecutionThread::GameThread // 指定在游戏线程执行
    );

    Device.SubscribeToEvent(FMyCaptureStartEvent::Name, Handler);
    Device.StartCapture(); // 触发事件
}
```

### 进阶用法

**组合使用 `TResult` 和 `TScopeGuard`**
确保资源在作用域结束时被释放，即使提前返回错误。
*(来源: `Public/Error/ScopeGuard.h`)*

```cpp
#include "MetaHumanCaptureUtils/Error/Result.h"
#include "MetaHumanCaptureUtils/Error/ScopeGuard.h"

TResult<FString, FMyError> LoadDataAndProcess(const FString& FilePath)
{
    // 获取一个模拟的“文件句柄”
    void* FileHandle = FPlatformFileManager::Get().GetPlatformFile().OpenRead(*FilePath);
    if (!FileHandle)
    {
        return FMyError{TEXT("Failed to open file")};
    }

    // 注册一个作用域守卫，确保文件句柄在函数退出时（无论成功、失败还是提前返回）被关闭
    auto Guard = MakeScopeGuard([FileHandle]()
    {
        FPlatformFileManager::Get().GetPlatformFile().CloseHandle(FileHandle);
        UE_LOG(LogTemp, Log, TEXT("File handle closed by scope guard."));
    });

    // 模拟处理失败
    bool bProcessingFailed = true;
    if (bProcessingFailed)
    {
        return FMyError{TEXT("Processing failed")}; // 此时 Guard 会自动关闭文件
    }

    return FString(TEXT("Processed data"));
}
```

## Demo 示例

一个最小示例，演示如何集成 `TResult` 和 `FCallbackSynchronizer` 来处理一组可能失败的并行任务。

**MyCaptureProcessor.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "MetaHumanCaptureUtils/Error/Result.h"
#include "MetaHumanCaptureUtils/Async/CallbackSynchronizer.h"

struct FProcessingError
{
    FString Reason;
};

class FMyCaptureProcessor
{
public:
    // 开始处理多个捕获片段，并在所有处理完成后回调
    void ProcessMultipleClips(const TArray<FString>& ClipIds,
                              TFunction<void(TResult<void, FProcessingError>)> OnAllProcessingDone);

private:
    // 处理单个片段的异步任务（模拟）
    void ProcessSingleClip(const FString& ClipId,
                           FCallbackSynchronizer::FAfterAllDelegate InSyncCallback);
};
```

**MyCaptureProcessor.cpp**
```cpp
#include "MyCaptureProcessor.h"
#include "Async/Async.h"

void FMyCaptureProcessor::ProcessMultipleClips(const TArray<FString>& ClipIds,
                                                TFunction<void(TResult<void, FProcessingError>)> OnAllProcessingDone)
{
    if (ClipIds.Num() == 0)
    {
        OnAllProcessingDone(ResultOk); // 没有任务，直接成功
        return;
    }

    // 1. 创建同步器
    auto Sync = FCallbackSynchronizer::Create();
    // 用于收集第一个遇到的错误（如果有的话）
    TSharedPtr<TOptional<FProcessingError>> FirstError = MakeShared<TOptional<FProcessingError>>();

    // 2. 为每个片段创建同步回调
    for (const FString& ClipId : ClipIds)
    {
        auto SyncCallback = Sync->CreateCallback([FirstError]() {
            // 这个 lambda 本身不需要做任何事，只是用于计数
        });

        // 3. 启动异步处理，并将回调传入
        AsyncTask(ENamedThreads::AnyBackgroundThreadNormalTask, [this, ClipId, SyncCallback, FirstError]()
        {
            // 模拟处理单个片段
            ProcessSingleClip(ClipId, FCallbackSynchronizer::FAfterAllDelegate::CreateLambda([FirstError]()
            {
                // 在单个片段处理完成的回调里，我们可以处理错误收集
                // 这里简化处理，假设失败信息可以通过其他方式传递
            }));
        });
    }

    // 4. 设置“全部完成”回调
    Sync->AfterAll(FCallbackSynchronizer::FAfterAllDelegate::CreateLambda([OnAllProcessingDone, FirstError]()
    {
        if (FirstError->IsSet())
        {
            OnAllProcessingDone(**FirstError); // 返回第一个错误
        }
        else
        {
            OnAllProcessingDone(ResultOk); // 全部成功
        }
    }));
}

void FMyCaptureProcessor::ProcessSingleClip(const FString& ClipId,
                                             FCallbackSynchronizer::FAfterAllDelegate InSyncCallback)
{
    // 模拟耗时操作
    FPlatformProcess::Sleep(0.5f);
    UE_LOG(LogTemp, Log, TEXT("Processed clip: %s"), *ClipId);
    
    // 任务完成，调用同步回调，通知 CallbackSynchronizer 计数-1
    InSyncCallback.ExecuteIfBound();
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | MetaHuman 核心算法库（通过 `MetaHumanConfig` 间接依赖） |

*注：`MetaHumanCaptureUtils` 自身的 Build.cs 可能只包含非常基础的核心引擎模块依赖。它作为工具库，被其他更具体的 MetaHuman 模块依赖。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 身体跟踪启用时禁用关卡序列导出 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 的渲染伪影问题 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体跟踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 为已有网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存问题 |

### 维护评价

- **整体状态**: **活跃维护中**，但**本模块 (`MetaHumanCaptureUtils`) 已被废弃**。
- **依据**: 尽管 `MetaHumanAnimator` 插件整体在持续更新（最近提交在2026年5月），但 `MetaHumanCaptureUtils` 模块本身已被 Epic 官方标记为废弃 (`UE_DEPRECATED(5.7, ...)`)，并指明其功能已迁移至 `CaptureManagerCore/CaptureUtils`。
- **建议**:
    1. 对于新项目，**强烈建议**避免直接使用 `MetaHumanCaptureUtils`。
    2. 如果维护旧代码，应计划迁移至 `CaptureManagerCore/CaptureUtils` 模块以获取新特性和持续支持。
    3. 本模块可能仅接收与 `MetaHumanAnimator` 整体兼容性相关的维护性更新，而不会有新功能开发。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanCaptureUtils)
- 官方文档 (无)
- [测试用例] (位于 `MetaHumanControlsConversionTest` 模块，路径: `Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanControlsConversionTest`)