# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 动画师 |
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（C++ 工具模块、资产等） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | ❌ 否 |
| 创建时间 | 未知 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方提供的 MetaHuman 工具包，用于将真实人物的面部表演（通过 iPhone 等设备捕获）转换为 MetaHuman 角色的动画数据。它提供了一整套从数据捕获、处理、求解到最终应用到虚幻引擎中数字角色的工作流。
MetaHuman CaptureUtils 模块是该插件的基础工具模块之一，为插件内其他模块（如 MetaHumanCaptureSource、MetaHumanFaceAnimationSolver）提供了底层的、可复用的异步事件处理、错误管理和任务协调工具。它本身不直接面向最终用户，而是作为内部组件，解决了在实时或接近实时的捕获数据流中处理异步事件、传播错误以及管理复杂异步任务生命周期的问题。

## 使用场景

- 你正在开发一个需要处理**实时视频流**（如 iPhone TrueDepth 相机）或面部追踪数据的插件。
- 你的工具需要发布一系列带有时间限制或速率控制的**异步事件**，并通知订阅者。
- 你需要一个线程安全的、可组合的**回调同步机制**，以确保多个异步操作完成后触发后续逻辑。
- 你需要一种清晰的方式来处理可能失败的操作，并在 C++ 中传递**成功/错误**的结果。

## 蓝图用法

`MetaHumanCaptureUtils` 模块主要是一个 C++ 运行时工具库，其核心功能（如事件源、任务管理、结果类型）均通过 C++ 类提供，**没有直接暴露蓝图节点**。
该模块提供的工具被其他模块（如 MetaHumanCaptureSource）使用，这些上层模块可能会提供蓝图接口。如果您需要蓝图层面的 MetaHuman 动画功能，请查阅 `MetaHumanToolkit` 或 `MetaHumanPipeline` 等模块的文档。

## C++ 用法

`MetaHumanCaptureUtils` 模块提供了一组基础的 C++ 工具类。

### 核心工具类

| 类/模板 | 说明 | 头文件 |
|---|---|---|
| `FCaptureEventSource` | 线程安全的事件源基类，用于发布和订阅自定义事件。 | `Async/EventSourceUtils.h` |
| `FCaptureEventSourceWithLimiter` | 带速率限制的事件源，可控制事件发布的频率。 | `Async/EventSourceUtils.h` |
| `TResult<ResultType, ErrorType>` | 表示一个可能成功（返回 `ResultType`）或失败（返回 `ErrorType`）的操作结果。 | `Error/Result.h` |
| `TScopeGuard<FuncType>` | RAII 风格的作用域守卫，确保在离开作用域时执行清理操作。 | `Error/ScopeGuard.h` |
| `TManagedDelegate<Args...>` | 可指定在游戏线程或调用线程执行的委托。 | `Async/ManagedDelegate.h` |
| `FAbortableAsyncTask` | 支持中止的异步任务，可用于执行耗时操作。 | `Async/Task.h` |
| `FStopToken` | 用于向异步任务发送停止信号的令牌。 | `Async/StopToken.h` |

### 头文件引入

```cpp
// 引入事件源
#include "Async/EventSourceUtils.h"
// 引入结果类型
#include "Error/Result.h"
// 引入作用域守卫
#include "Error/ScopeGuard.h"
// 引入可中止任务
#include "Async/Task.h"
```

### 基本用法 (来自公共头文件)

#### 1. 创建和使用自定义事件源
```cpp
// MyEventSource.h
#pragma once
#include "Async/EventSourceUtils.h"

// 定义一个自定义事件
struct FMyFrameProcessedEvent : public FCaptureEvent
{
    static inline const FString EventName = TEXT("FrameProcessed");
    int32 FrameIndex;
    FMyFrameProcessedEvent(int32 InFrameIndex)
        : FCaptureEvent(EventName), FrameIndex(InFrameIndex)
    {}
};

// 创建一个事件发布者
class FMyCaptureDevice : public FCaptureEventSource
{
public:
    void ProcessFrame(int32 FrameIndex)
    {
        // ... 处理帧的逻辑 ...

        // 发布事件，通知所有订阅者
        PublishEvent<FMyFrameProcessedEvent>(FrameIndex);
    }
};

// 使用示例
void Example_EventSource()
{
    FMyCaptureDevice Device;

    // 订阅事件
    Device.SubscribeToEvent(FMyFrameProcessedEvent::EventName,
        TManagedDelegate<TSharedPtr<const FCaptureEvent>>::CreateLambda(
            [](TSharedPtr<const FCaptureEvent> Event)
            {
                auto ProcessedEvent = StaticCastSharedPtr<const FMyFrameProcessedEvent>(Event);
                UE_LOG(LogTemp, Log, TEXT("Frame %d processed!"), ProcessedEvent->FrameIndex);
            }));

    Device.ProcessFrame(42);
}
```

#### 2. 使用 TResult 处理可能失败的操作
```cpp
#include "Error/Result.h"

// 模拟一个可能失败的加载操作
TResult<UTexture2D*, FString> LoadTexture(const FString& Path)
{
    UTexture2D* Texture = Cast<UTexture2D>(StaticLoadObject(UTexture2D::StaticClass(), nullptr, *Path));
    if (Texture)
    {
        return Texture; // 成功
    }
    else
    {
        return FString::Printf(TEXT("Failed to load texture: %s"), *Path); // 错误
    }
}

void Example_ResultType()
{
    auto Result = LoadTexture(TEXT("/Game/MyTexture"));
    if (Result.IsValid())
    {
        UTexture2D* LoadedTexture = Result.GetResult();
        // 使用纹理...
    }
    else
    {
        FString ErrorMessage = Result.GetError();
        UE_LOG(LogTemp, Error, TEXT("%s"), *ErrorMessage);
    }
}
```

#### 3. 使用 ScopeGuard 确保资源释放
```cpp
#include "Error/ScopeGuard.h"

void Example_ScopeGuard()
{
    FArchive* Archive = IFileManager::Get().CreateFileReader(TEXT("data.bin"));
    auto Guard = MakeScopeGuard([&]() {
        if (Archive)
        {
            delete Archive;
            Archive = nullptr;
        }
    });

    // ... 使用 Archive 进行读写操作 ...
    // 如果此处发生异常或提前返回，Guard 的析构函数仍会执行，释放 Archive。

    // 如果一切正常，可以提前取消守卫（例如，将所有权转移给其他对象）
    // Guard.Dismiss();
}
```

### 进阶用法 (来自公共头文件)

#### 使用 FCallbackSynchronizer 协调多个异步回调
```cpp
#include "Async/CallbackSynchronizer.h"

void Example_CallbackSynchronizer()
{
    auto Synchronizer = FCallbackSynchronizer::Create();

    // 创建多个需要等待的回调
    auto CallbackA = Synchronizer->CreateCallback([](bool bSuccess) {
        UE_LOG(LogTemp, Log, TEXT("Task A finished: %s"), bSuccess ? TEXT("OK") : TEXT("Fail"));
    });
    auto CallbackB = Synchronizer->CreateCallback([](const FString& Data) {
        UE_LOG(LogTemp, Log, TEXT("Task B finished with data: %s"), *Data);
    });

    // 模拟启动两个异步任务，并将上述回调作为完成句柄
    AsyncTask(ENamedThreads::AnyBackgroundThreadNormalTask, [CallbackA]() {
        FPlatformProcess::Sleep(1.0f);
        CallbackA.ExecuteIfBound(true);
    });
    AsyncTask(ENamedThreads::AnyBackgroundThreadNormalTask, [CallbackB]() {
        FPlatformProcess::Sleep(0.5f);
        CallbackB.ExecuteIfBound(TEXT("AsyncData"));
    });

    // 当所有通过 Synchronizer 创建的回调都执行后，触发 AfterAll 委托
    Synchronizer->AfterAll(FCallbackSynchronizer::FAfterAllDelegate::CreateLambda([]() {
        UE_LOG(LogTemp, Log, TEXT("All async tasks completed!"));
    }), true); // bExecuteIfCounterZero=true: 如果添加时计数器已经为0，则立即执行
}
```

## Demo 示例

一个最小的示例，演示如何创建自定义事件源并使用 `TResult` 处理错误。

**MyDemoModule.h**
```cpp
#pragma once
#include "Modules/ModuleManager.h"
#include "Async/EventSourceUtils.h"
#include "Error/Result.h"

// 自定义事件
struct FDemoEvent : public FCaptureEvent
{
    static inline const FString Name = TEXT("DemoEvent");
    int32 Value;
    FDemoEvent(int32 InValue) : FCaptureEvent(Name), Value(InValue) {}
};

// 一个简单的事件发布者
class FDemoPublisher : public FCaptureEventSource
{
public:
    void DoWorkAndPublish(int32 Input)
    {
        // 模拟一些计算
        int32 Result = Input * 2;
        // 发布事件
        PublishEvent<FDemoEvent>(Result);
    }
};

// 模拟一个可能失败的函数
TResult<int32, FString> SafeDivide(int32 A, int32 B)
{
    if (B == 0)
    {
        return FString(TEXT("Division by zero!"));
    }
    return A / B;
}
```

**MyDemoModule.cpp**
```cpp
#include "MyDemoModule.h"
#include "CoreMinimal.h"

class FMyDemoModule : public IModuleInterface
{
    virtual void StartupModule() override
    {
        // 测试事件源
        FDemoPublisher Publisher;
        Publisher.SubscribeToEvent(FDemoEvent::Name,
            TManagedDelegate<TSharedPtr<const FCaptureEvent>>::CreateLambda(
                [](TSharedPtr<const FCaptureEvent> Event)
                {
                    auto DemoEvent = StaticCastSharedPtr<const FDemoEvent>(Event);
                    UE_LOG(LogTemp, Display, TEXT("Received DemoEvent: %d"), DemoEvent->Value);
                }));
        Publisher.DoWorkAndPublish(21); // 将输出 “Received DemoEvent: 42”

        // 测试 TResult
        auto DivResult = SafeDivide(10, 2);
        if (DivResult)
        {
            UE_LOG(LogTemp, Display, TEXT("10 / 2 = %d"), DivResult.GetResult());
        }

        auto FailResult = SafeDivide(10, 0);
        if (!FailResult)
        {
            UE_LOG(LogTemp, Error, TEXT("Error: %s"), *FailResult.GetError());
        }
    }
};

IMPLEMENT_MODULE(FMyDemoModule, MyDemoModule);
```

## 模块依赖

`MetaHumanCaptureUtils` 模块的依赖相对基础，主要依赖虚幻引擎的核心模块。

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/CoreUObject/Engine） | 作为底层工具库，其依赖被最小化。 |

## 维护状态

### 近期更新

从 Git 历史记录来看，`MetaHumanAnimator` 插件整体处于活跃维护状态。最近的更新集中在 2026 年 5 月，涉及动画导出、渲染修复和可视化改进等功能性更新。`MetaHumanCaptureUtils` 作为基础模块，其改动通常伴随着上层功能模块的更新。

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 在启用身体追踪时禁用关卡序列导出功能 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 上的渲染伪影问题 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | [MHA] 为现有网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复定序器缓存问题 |

### 维护评价

`MetaHumanAnimator` 插件是 Epic Games 的官方产品，从最近的提交记录看，它在 2026 年 5 月仍有频繁且具体的功能性更新和 Bug 修复，表明它处于**积极维护**状态。`MetaHumanCaptureUtils` 作为其内部组件，其代码质量、API 设计（包括部分标记为 `UE_DEPRECATED` 的 API 迁移）都体现了成熟项目的特征。该模块作为基础工具，稳定且必要。

**注意**：虽然插件本身维护活跃，但 `MetaHumanCaptureUtils` 模块中一些较旧的类（如 `FCallbackSynchronizer`、`FCaptureEventSourceBase`）已被标记为在 5.7 版本废弃，并提示用户迁移到 `CaptureManagerCore/CaptureUtils` 模块。在新项目中，建议评估是否使用新模块。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanCaptureUtils)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/metahuman-animator-in-unreal-engine/)（MetaHuman Animator 官方文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanControlsConversionTest)（相关测试模块）