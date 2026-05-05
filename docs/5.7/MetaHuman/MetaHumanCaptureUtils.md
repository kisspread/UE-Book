# MetaHuman Capture Utils

> The official MetaHuman Unreal Engine toolkit（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（工具类库） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-02-02 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

`MetaHumanCaptureUtils` 是 MetaHuman Animator 插件中的一个基础工具模块，提供了一系列用于异步任务管理、事件发布订阅、错误处理和作用域守卫的 C++ 工具类。它主要服务于 MetaHuman Animator 工作流中的数据处理、设备通信和动画求解等底层功能，为上层模块（如 `MetaHumanCaptureSource`, `MetaHumanFaceAnimationSolver` 等）提供可复用的基础设施。

**重要提示**：根据源码中的 `UE_DEPRECATED` 宏，此模块（连同 `MetaHumanCaptureSource`, `MetaHumanFootageIngest` 等）在 UE 5.7 中已被标记为废弃。其功能已迁移至新的 `CaptureManagerCore/CaptureUtils` 模块。新项目应避免直接依赖此模块。

## 使用场景

- 你需要在 MetaHuman 动画制作流程中管理可中止的后台异步任务（例如，处理视频帧、运行求解器）。
- 你需要在不同的捕获设备或处理组件之间建立基于事件的松耦合通信机制。
- 你需要一种统一的方式来处理可能失败的操作，并以类型安全的方式传递错误信息。
- 你需要确保在作用域退出时（无论是正常返回还是异常）自动执行清理操作。

## 蓝图用法

本模块主要提供底层的 C++ 工具类，没有直接暴露给蓝图的 `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)` 接口。其功能被上层模块（如 `MetaHumanPerformance`, `MetaHumanIdentity`）封装后，才通过蓝图可用的资产和组件提供给设计师使用。

### 核心节点

无直接蓝图节点。

### 使用示例（蓝图描述）

不适用。此模块的使用完全在 C++ 层面。

## C++ 用法

### 头文件引入

```cpp
#include "Async/StopToken.h"
#include "Async/Task.h"
#include "Async/Event.h"
#include "Async/EventSourceUtils.h"
#include "Async/CallbackSynchronizer.h"
#include "Error/Result.h"
#include "Error/ScopeGuard.h"
```

### 基本用法

**1. 使用 `FStopToken` 和 `FAbortableAsyncTask` 管理可中止任务**
（来源：`Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanCaptureUtils/Public/Async/Task.h`）

```cpp
// 创建一个可中止的异步任务
FAbortableAsyncTask MyTask([/* 捕获列表 */](const FStopToken& StopToken)
{
    // 在长时间运行的任务中定期检查是否被请求停止
    for (int32 i = 0; i < 1000; ++i)
    {
        if (StopToken.IsStopRequested())
        {
            UE_LOG(LogTemp, Warning, TEXT("Task aborted!"));
            return; // 提前退出
        }
        // ... 执行耗时工作 ...
        FPlatformProcess::Sleep(0.01f);
    }
    UE_LOG(LogTemp, Log, TEXT("Task completed normally."));
});

// 启动任务
MyTask.StartAsync();

// ... 在某个时刻，例如用户取消操作时 ...
MyTask.Abort(); // 请求停止任务

// 析构函数会自动调用 Abort() 并等待任务完成
```

**2. 使用 `TScopeGuard` 进行作用域清理**
（来源：`Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanCaptureUtils/Public/Error/ScopeGuard.h`）

```cpp
void ProcessData()
{
    // 获取一个需要手动释放的资源
    SomeResource* Resource = AcquireResource();

    // 创建一个作用域守卫，确保在函数退出时释放资源
    auto Guard = MakeScopeGuard([Resource]()
    {
        ReleaseResource(Resource);
        UE_LOG(LogTemp, Log, TEXT("Resource released via scope guard."));
    });

    // ... 使用 Resource 进行操作 ...
    if (SomeErrorCondition())
    {
        return; // Guard 的析构函数会自动调用，资源被释放
    }

    // 正常执行完毕，Guard 的析构函数也会被调用
}

// 使用宏的简便写法
void AnotherFunction()
{
    FILE* File = fopen("test.txt", "r");
    SCOPE_EXIT { fclose(File); }; // 确保文件在作用域结束时关闭

    // ... 使用文件 ...
}
```

**3. 使用 `TResult` 进行错误处理**
（来源：`Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanCaptureUtils/Public/Error/Result.h`）

```cpp
// 定义一个可能成功（返回 FString）或失败（返回 FText 错误信息）的函数
TResult<FString, FText> LoadConfiguration(const FString& Path)
{
    if (!FPaths::FileExists(Path))
    {
        return FText::Format(NSLOCTEXT("Config", "FileNotFound", "File not found: {0}"), FText::FromString(Path));
    }
    // ... 加载并解析文件 ...
    FString ConfigData = TEXT("Loaded Data");
    return ConfigData;
}

// 调用并处理结果
void UseConfiguration()
{
    auto Result = LoadConfiguration(TEXT("MyConfig.cfg"));

    if (Result.IsValid())
    {
        const FString& Data = Result.GetResult();
        UE_LOG(LogTemp, Log, TEXT("Config loaded: %s"), *Data);
    }
    else if (Result.IsError())
    {
        const FText& ErrorMsg = Result.GetError();
        UE_LOG(LogTemp, Error, TEXT("Failed to load config: %s"), *ErrorMsg.ToString());
    }
}
```

### 进阶用法

**使用事件系统 (`FCaptureEventSource`) 进行组件间通信**
（来源：`Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanCaptureUtils/Public/Async/EventSourceUtils.h`）

```cpp
// 1. 定义自定义事件
METAHUMAN_CAPTURE_DEFINE_EMPTY_EVENT(FTrackingDataUpdatedEvent, "TrackingDataUpdated")

// 2. 创建一个事件源类
class UMyCaptureComponent : public UActorComponent, public FCaptureEventSource
{
public:
    UMyCaptureComponent()
    {
        // 注册事件
        RegisterEvent(FTrackingDataUpdatedEvent::Name);
    }

    void OnNewTrackingDataReceived()
    {
        // ... 处理数据 ...

        // 发布事件，通知所有订阅者
        PublishEvent<FTrackingDataUpdatedEvent>();
    }
};

// 3. 订阅事件
void UMyAnimationProcessor::BeginPlay()
{
    Super::BeginPlay();

    // 假设找到了场景中的 UMyCaptureComponent
    UMyCaptureComponent* CaptureComp = FindComponentByClass<UMyCaptureComponent>();
    if (CaptureComp)
    {
        // 订阅事件，并指定在游戏线程回调
        CaptureComp->SubscribeToEvent(
            FTrackingDataUpdatedEvent::Name,
            FCaptureEventHandler::CreateLambda([this](TSharedPtr<const FCaptureEvent> Event)
            {
                // 在游戏线程安全地处理事件
                UE_LOG(LogTemp, Log, TEXT("Tracking data updated!"));
                UpdateAnimation();
            },
            EDelegateExecutionThread::GameThread)
        );
    }
}
```

## Demo 示例

一个展示 `FAbortableAsyncTask` 和 `TResult` 基本用法的最小示例。

**MyAsyncProcessor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Async/Task.h"
#include "Error/Result.h"
#include "MyAsyncProcessor.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMyAsyncProcessor : public UActorComponent
{
    GENERATED_BODY()

public:
    UMyAsyncProcessor();

    // 启动一个可中止的后台任务
    UFUNCTION(BlueprintCallable, Category = "Async")
    void StartHeavyTask();

    // 中止当前任务
    UFUNCTION(BlueprintCallable, Category = "Async")
    void AbortCurrentTask();

private:
    // 模拟一个可能失败的计算
    TResult<float, FString> CalculateValue(float Input);

    TUniquePtr<FAbortableAsyncTask> CurrentTask;
};
```

**MyAsyncProcessor.cpp**
```cpp
#include "MyAsyncProcessor.h"

UMyAsyncProcessor::UMyAsyncProcessor()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UMyAsyncProcessor::StartHeavyTask()
{
    // 先中止可能存在的旧任务
    AbortCurrentTask();

    // 创建新任务
    CurrentTask = MakeUnique<FAbortableAsyncTask>([this](const FStopToken& StopToken)
    {
        UE_LOG(LogTemp, Log, TEXT("Heavy task started on thread."), );

        for (int32 Iteration = 0; Iteration < 100; ++Iteration)
        {
            if (StopToken.IsStopRequested())
            {
                UE_LOG(LogTemp, Warning, TEXT("Task aborted at iteration %d."), Iteration);
                return;
            }

            // 模拟耗时计算
            FPlatformProcess::Sleep(0.1f);

            // 使用 TResult 处理可能失败的子计算
            auto Result = CalculateValue(static_cast<float>(Iteration));
            if (Result.IsValid())
            {
                UE_LOG(LogTemp, Verbose, TEXT("Iteration %d result: %f"), Iteration, Result.GetResult());
            }
            else
            {
                UE_LOG(LogTemp, Error, TEXT("Iteration %d error: %s"), Iteration, *Result.GetError());
            }
        }

        UE_LOG(LogTemp, Log, TEXT("Heavy task completed successfully."));
    });

    // 异步启动任务
    CurrentTask->StartAsync();
}

void UMyAsyncProcessor::AbortCurrentTask()
{
    if (CurrentTask.IsValid())
    {
        CurrentTask->Abort(); // 请求停止
        // CurrentTask 的析构函数会确保任务完成后再销毁
        CurrentTask.Reset();
    }
}

TResult<float, FString> UMyAsyncProcessor::CalculateValue(float Input)
{
    // 模拟一个可能出错的计算
    if (Input < 0)
    {
        return FString(TEXT("Input cannot be negative"));
    }
    if (FMath::IsNearlyZero(Input))
    {
        return FString(TEXT("Division by zero risk"));
    }
    return 100.0f / Input; // 成功时返回结果
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。此模块作为基础工具库，设计为自包含，不依赖其他 MetaHuman 特定模块。

## 维护状态

### 近期更新

```
- 77f392c7c872 [MetaHumanAnimator] Deprecated CaptureSource, CaptureUtils, FootageIngest and the remainder of CaptureProtocolStack.
- 9afffeda15e1 [Backout] - CL45863710 [FYI] peter.wigg #rnx Original CL Desc ----------------------------------------------------------------- [MetaHumanAnimator] Deprecated CaptureSource, CaptureUtils, FootageIngest and the remainder of CaptureProtocolStack.
- 207cd4d313ff [MetaHumanAnimator] Deprecated CaptureSource, CaptureUtils, FootageIngest and the remainder of CaptureProtocolStack.
```

### 维护评价

**不推荐使用**。`MetaHumanCaptureUtils` 模块已被官方标记为废弃（`UE_DEPRECATED(5.7, ...)`），其功能正在被迁移到新的 `CaptureManagerCore/CaptureUtils` 模块。最近的提交记录全部是关于添加废弃警告或回退相关更改，表明 Epic Games 正在积极地将用户从旧模块引导至新模块。

- **创建时间**：2024年2月，相对年轻。
- **最近更新**：最近的更新（2024年及以后）全部是废弃标记，没有功能性增强或错误修复。
- **维护状态**：**废弃中**。此模块处于生命周期末期，仅为了向后兼容而保留。
- **已知问题/限制**：使用此模块编译时会产生大量废弃警告。在未来的引擎版本中，此模块可能被完全移除。
- **推荐**：**强烈不推荐**在新项目中使用。现有项目应计划迁移至 `CaptureManagerCore/CaptureUtils`。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanCaptureUtils)
- 官方文档：无
- 测试用例：无（未在提供的路径中发现）