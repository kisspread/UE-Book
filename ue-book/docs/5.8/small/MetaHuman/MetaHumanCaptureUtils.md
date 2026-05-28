# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 动画工具 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、配置资源） |
| 模块 | `MetaHumanCaptureUtils` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime), 等共 28 个模块 |
| 实验性 | 否 |
| 创建时间 | 2021-05-13 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## ⚠️ 重要废弃提示

**MetaHumanCaptureUtils 模块已在 UE 5.7 中标记为废弃**，其全部功能已迁移至 `CaptureManagerCore/CaptureUtils` 模块。本文档基于废弃前的源码进行记录，新项目应直接使用替代模块。

涉及废弃的类包括：
- `FCaptureEventSourceBase`、`FCaptureEventSource`、`FCaptureEventSourceWithLimiter`
- `FCallbackSynchronizer`
- `FCaptureEvent`、`ICaptureEventSource`
- `FStopToken`

## 用途

**MetaHumanCaptureUtils** 是 MetaHuman Animator 插件的底层工具模块，为面部捕捉和动画处理流水线提供通用基础设施。它解决的核心问题是：在多线程的面部捕捉工作流中，如何安全地进行异步任务管理、事件发布/订阅、回调同步和错误处理。

该模块不直接面向最终用户，而是被 MetaHuman Animator 插件内部的其他模块（如 MetaHumanCaptureSource、MetaHumanFaceAnimationSolver 等）作为基础依赖使用。

主要功能包括：
- **异步事件系统**：线程安全的事件发布/订阅机制，支持限流发布
- **错误处理**：类似 Rust 的 `Result<T, E>` 模式，优雅处理成功/失败双态结果
- **委托管理**：自动在指定线程（游戏线程/工作线程）执行的委托封装
- **回调同步**：等待多个异步回调全部完成后触发统一完成回调
- **可中止异步任务**：支持外部取消的异步任务框架
- **作用域守卫**：RAII 风格的资源清理工具

## 使用场景

- 你需要构建自定义的面部捕捉数据处理流水线 → 使用事件系统和回调同步器
- 你需要在捕捉流程中处理可能的失败场景 → 使用 `TResult<T, E>` 模式
- 你需要从工作线程安全地通知游戏线程 → 使用 `TManagedDelegate`
- 你需要运行可被外部取消的长时间异步任务 → 使用 `FAbortableAsyncTask`
- 你需要确保在函数退出时执行清理操作 → 使用 `TScopeGuard` / `SCOPE_EXIT`

## 蓝图用法

**本模块不包含蓝图可调用 API。** MetaHumanCaptureUtils 是纯 C++ 工具模块，所有类和函数均无 `BlueprintCallable` 标记。蓝图层面的 MetaHuman 功能由其他模块（如 MetaHumanPerformance、MetaHumanIdentity 等）提供。

## C++ 用法

### 头文件引入

```cpp
// 核心工具类
#include "Error/Result.h"
#include "Error/ScopeGuard.h"

// 异步工具类（均已废弃）
#include "Async/Event.h"
#include "Async/EventSourceUtils.h"
#include "Async/ManagedDelegate.h"
#include "Async/CallbackSynchronizer.h"
#include "Async/Task.h"
#include "Async/StopToken.h"
```

> **注意**：所有 `Async/` 下的头文件在 UE 5.7+ 中已废弃，应使用 `CaptureManagerCore/CaptureUtils` 中的等价替代。

### 基本用法 — TResult 错误处理

`TResult<ResultType, ErrorType>` 提供了类型安全的成功/失败双态返回值，类似 Rust 的 `Result` 类型。

```cpp
#include "Error/Result.h"

// 自定义错误类型
struct FMyError
{
    FString Message;
    int32 ErrorCode;
};

// 返回成功值
TResult<int32, FMyError> Divide(int32 A, int32 B)
{
    if (B == 0)
    {
        return FMyError{ TEXT("Division by zero"), -1 };
    }
    return A / B;  // 隐式构造为成功结果
}

// 使用结果
void Example()
{
    auto Result = Divide(10, 2);

    if (Result.IsValid())
    {
        int32 Value = Result.GetResult();  // 5
    }
    if (Result.IsError())
    {
        const FMyError& Error = Result.GetError();
        UE_LOG(LogTemp, Error, TEXT("%s (Code: %d)"), *Error.Message, Error.ErrorCode);
    }

    // 移动语义取出结果（避免拷贝）
    int32 Value = Result.ClaimResult();
}
```

**void 特化** — 用于不需要返回值的场景：

```cpp
// 无需返回值时使用 void 特化
TResult<void, FString> SaveFile(const FString& Path)
{
    if (!FPaths::FileExists(Path))
    {
        return FString(TEXT("File not found"));
    }
    // ... 保存逻辑
    return ResultOk;  // 使用全局 constexpr FVoidResultTag
}
```

### 基本用法 — SCOPE_EXIT 作用域守卫

```cpp
#include "Error/ScopeGuard.h"

void ProcessData()
{
    FScopeLock Lock(&CriticalSection);
    AllocateResources();

    // 确保函数退出时释放资源，无论正常返回还是异常
    SCOPE_EXIT
    {
        ReleaseResources();
        UE_LOG(LogTemp, Log, TEXT("Resources released"));
    };

    DoWork();  // 即使这里抛出异常，SCOPE_EXIT 也会执行

    // 手动创建守卫
    auto Guard = MakeScopeGuard([]()
    {
        FPlatformProcess::Sleep(0.01f);  // 延迟清理
    });

    // 条件性取消守卫
    if (bSkipCleanup)
    {
        Guard.Dismiss();
    }
}
```

### 进阶用法 — 事件发布/订阅系统

> ⚠️ 以下代码已在 UE 5.7 废弃

```cpp
#include "Async/Event.h"
#include "Async/EventSourceUtils.h"

// 定义自定义事件
METAHUMAN_CAPTURE_DEFINE_EMPTY_EVENT(FMyFrameEvent, "MyFrameEvent")

// 自定义带数据的事件
struct FMyProgressEvent : public FCaptureEvent
{
    FMyProgressEvent(float InProgress)
        : FCaptureEvent(TEXT("MyProgressEvent"))
        , Progress(InProgress)
    {}

    float Progress;
};

// 创建事件源
class FMyCaptureService : public FCaptureEventSource
{
public:
    FMyCaptureService()
    {
        // 注册可订阅的事件
        RegisterEvent(FMyFrameEvent::Name);
        RegisterEvent(TEXT("MyProgressEvent"));
    }

    void ProcessFrame()
    {
        // 发布事件给所有订阅者（线程安全）
        PublishEvent<FMyFrameEvent>();

        float Progress = 0.5f;
        PublishEvent<FMyProgressEvent>(Progress);
    }
};

// 创建带限流的事件源（最多每 100ms 发布一次）
class FMyThrottledSource : public FCaptureEventSourceWithLimiter
{
public:
    FMyThrottledSource() : FCaptureEventSourceWithLimiter(100) {}

    void OnFrameUpdate(float InProgress)
    {
        // 大部分调用会被跳过，仅在距上次发布超过 100ms 时才发布
        PublishIfThresholdReached<FMyProgressEvent>(false, InProgress);
    }

    void OnFinalFrame(float InProgress)
    {
        // 强制发布最终事件（忽略限流）
        PublishIfThresholdReached<FMyProgressEvent>(true, InProgress);
    }
};
```

### 进阶用法 — 回调同步器

> ⚠️ 已在 UE 5.7 废弃

等待多个异步操作全部完成后执行汇总操作：

```cpp
#include "Async/CallbackSynchronizer.h"

void ProcessMultipleAssets()
{
    auto Sync = FCallbackSynchronizer::Create();

    // 创建受管理的回调（会自动计数）
    auto OnTextureLoaded = Sync->CreateCallback([](UTexture2D* Texture)
    {
        UE_LOG(LogTemp, Log, TEXT("Texture loaded: %s"), *Texture->GetName());
    });

    auto OnMeshLoaded = Sync->CreateCallback([](UStaticMesh* Mesh)
    {
        UE_LOG(LogTemp, Log, TEXT("Mesh loaded: %s"), *Mesh->GetName());
    });

    // 所有回调完成后执行
    Sync->AfterAll(FCallbackSynchronizer::FAfterAllDelegate::CreateLambda([]()
    {
        UE_LOG(LogTemp, Log, TEXT("All assets loaded!"));
    }));

    // 发起异步操作，将受管理的回调作为完成通知
    LoadTextureAsync(OnTextureLoaded);
    LoadMeshAsync(OnMeshLoaded);
}
```

### 进阶用法 — 线程管理委托

> ⚠️ 已在 UE 5.7 废弃

```cpp
#include "Async/ManagedDelegate.h"

void SetupCaptureCallbacks()
{
    // 创建在游戏线程执行的委托
    TManagedDelegate<FString> OnCaptureComplete(
        [](const FString& Result)
        {
            // 这段代码保证在游戏线程执行
            UE_LOG(LogTemp, Log, TEXT("Capture complete: %s"), *Result);
        },
        EDelegateExecutionThread::GameThread
    );

    // 创建在调用线程执行的委托
    TManagedDelegate<int32> OnProgress(
        [](int32 Percent)
        {
            // 在工作线程直接执行，不跳转游戏线程
            UpdateProgress(Percent);
        },
        EDelegateExecutionThread::InternalThread
    );

    // 多播委托版本
    TManagedMulticastDelegate<float> OnFrameProcessed;
    OnFrameProcessed.Add([](float DeltaTime)
    {
        // 注册多个处理器
    });

    // 从任意线程调用，委托会自动切换到指定线程执行
    OnCaptureComplete(TEXT("Success"));
    OnFrameProcessed(0.016f);
}
```

### 进阶用法 — 可中止异步任务

> ⚠️ 已在 UE 5.7 废弃

```cpp
#include "Async/Task.h"

void StartLongRunningTask()
{
    // 创建可中止的异步任务
    auto Task = MakeUnique<FAbortableAsyncTask>(
        [](const FStopToken& StopToken)
        {
            for (int32 i = 0; i < 1000000; ++i)
            {
                // 检查是否被请求停止
                if (StopToken.IsStopRequested())
                {
                    UE_LOG(LogTemp, Warning, TEXT("Task aborted at iteration %d"), i);
                    return;
                }
                ProcessFrame(i);
            }
        }
    );

    // 后台线程异步执行
    Task->StartAsync();

    // ... 某个时刻取消任务
    Task->Abort();

    // Task 析构时会自动 Abort + EnsureCompletion
}
```

## Demo 示例

完整的、可编译的最小示例，演示 `TResult` 错误处理和 `TScopeGuard` 作用域守卫的使用：

```cpp
// MyCaptureHelper.h
#pragma once

#include "Error/Result.h"
#include "Error/ScopeGuard.h"

struct FCaptureError
{
    FString Message;
    int32 Code;
};

class FMyCaptureHelper
{
public:
    // 带错误处理的数据处理函数
    TResult<FString, FCaptureError> ProcessCaptureData(const FString& InputPath);

    // 演示 SCOPE_EXIT 的资源管理
    bool InitializeCaptureDevice();
};
```

```cpp
// MyCaptureHelper.cpp
#include "MyCaptureHelper.h"

TResult<FString, FCaptureError> FMyCaptureHelper::ProcessCaptureData(const FString& InputPath)
{
    // 验证输入
    if (!FPaths::FileExists(InputPath))
    {
        return FCaptureError{ FString::Printf(TEXT("File not found: %s"), *InputPath), 404 };
    }

    // 读取数据
    FString RawData;
    if (!FFileHelper::LoadFileToString(RawData, *InputPath))
    {
        return FCaptureError{ TEXT("Failed to read file"), 500 };
    }

    // 处理成功
    return FString::Printf(TEXT("Processed %d characters"), RawData.Len());
}

bool FMyCaptureHelper::InitializeCaptureDevice()
{
    void* DeviceHandle = FPlatformMisc::GetDeviceHandle();
    if (!DeviceHandle)
    {
        return false;
    }

    // 使用 SCOPE_EXIT 确保设备句柄在函数退出时释放
    auto DeviceGuard = MakeScopeGuard([DeviceHandle]()
    {
        FPlatformMisc::ReleaseDeviceHandle(DeviceHandle);
    });

    // 初始化设备（可能失败）
    if (!FPlatformMisc::InitializeDevice(DeviceHandle))
    {
        return false;  // DeviceGuard 自动释放句柄
    }

    // 正常路径也自动释放
    return true;
}
```

## 模块依赖

本模块（MetaHumanCaptureUtils）的依赖关系简洁，无特殊依赖：

| 模块 | 用途 |
|---|---|
| 无特殊依赖 | 仅标准 Core/Engine 等基础模块 |

注：使用 MetaHuman Animator 插件的其他模块时有更复杂的依赖，例如 MetaHumanIdentity 依赖 `ControlRigDeveloper`、`MetaHumanSDKEditor`、`SkeletalMeshUtilitiesCommon` 等。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 启用身体追踪时禁用关卡序列导出 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 渲染瑕疵 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 支持为已有网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存问题 |

### 维护评价

**MetaHuman Animator 插件整体处于活跃维护状态**，但 **MetaHumanCaptureUtils 模块本身已废弃**。

- 插件整体仍被 Epic 积极维护，近期有功能更新和 bug 修复
- MetaHumanCaptureUtils 模块在 UE 5.7 中被标记为废弃，所有功能迁移至 `CaptureManagerCore/CaptureUtils`
- 模块内的 `Async/` 子目录下的类（事件源、回调同步器、停止令牌等）均标注了废弃宏
- `TResult` 和 `TScopeGuard` 等通用工具类未标注废弃，可能仍在使用或尚待迁移

**建议**：
- 🟢 如果使用 MetaHuman Animator 的完整功能 → 继续使用，插件活跃维护中
- 🔴 如果需要直接使用 MetaHumanCaptureUtils 中的底层工具 → **不要使用**，改用 `CaptureManagerCore/CaptureUtils`
- 🟡 `TResult` 和 `TScopeGuard` 是通用模式，可参考但建议使用 UE 标准库或独立实现

## 相关链接

- [源码（MetaHumanCaptureUtils）](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanCaptureUtils)
- [源码（MetaHuman Animator 插件根目录）](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [替代模块（CaptureManagerCore/CaptureUtils）](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanCaptureUtils) — UE 5.7+ 推荐使用