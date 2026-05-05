# Android Background Service

> Allows you to use AndroidX WorkManager to perform background work on Android

| 属性 | 值 |
|---|---|
| 分类 | Android Background Service |
| 默认启用 | false |
| 包含内容 | false |
| 模块 | AndroidBackgroundService (RuntimeNoCommandlet) |
| 创建时间 | 2021-06-14 |
| 年龄标签 | 🆕 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/AndroidBackgroundService) | |

## 用途

这个 Plugin 是 UE5 与 AndroidX WorkManager 之间的 JNI 桥梁层。它解决的核心问题是：**在 Android 上，当 UE 应用处于后台或进程被杀时，仍然能够调度和执行可靠的工作任务**。

AndroidX WorkManager 是 Android Jetpack 提供的后台任务调度库，它能够：
- 在应用后台运行时执行任务
- 在设备重启后自动恢复任务
- 根据约束条件（电量、网络、充电状态等）智能调度
- 支持一次性任务和周期性任务

该 Plugin 的 C++ 层通过 JNI 将 UE 的工作请求转发给 Java 层的 `UEWorkManagerJavaInterface`，由后者使用 AndroidX WorkManager API 创建和管理工作任务。当 Worker 被执行时，Java 层会通过 JNI 回调通知 UE 的 C++ 代码（通过 `FAndroidBackgroundServicesDelegates` 代理），实现双向通信。

**注意：** 该 Plugin 默认禁用（`EnabledByDefault: false`），仅支持 Android 平台，需要手动启用。

## 使用场景

- **后台数据同步：** 你的游戏需要在后台定期将统计数据上报服务器 → 配置周期性后台任务，约束为需要网络连接
- **后台资源下载：** 需要在应用后台时继续下载大文件（该 Plugin 内置了对 `DownloadWorkerParameterKeys` 的支持）→ 使用 `bStartAsForegroundService` 确保不被系统杀死
- **延迟任务执行：** 需要在特定条件满足时（如设备充电 + WiFi）才执行任务 → 配置 WorkManager 约束条件
- **跨进程重启的可靠任务：** 任务必须完成，即使应用被系统回收后重新打开 → WorkManager 会自动重新调度未完成的任务

## 蓝图用法

该 Plugin 没有暴露任何 BlueprintCallable 函数或 BlueprintReadWrite 属性。所有 API 均为 C++ 级别，通过 JNI 与 Java 层交互。蓝图层面无法直接使用此 Plugin。

## C++ 用法

该 Plugin 的 C++ API 全部在 `#if USE_ANDROID_JNI` 宏保护下，仅在 Android 构建时可用。

### 头文件引入

```cpp
#include "UEWorkManagerNativeWrapper.h"
```

### 基本用法：调度一个后台任务

```cpp
// 来源: UEWorkManagerNativeWrapper.h 的 ScheduleBackgroundWork 接口

// 1. 创建参数对象
FUEWorkManagerNativeWrapper::FWorkRequestParametersNative WorkParams;

// 2. 配置约束条件（可选，所有默认为 false）
WorkParams.bRequireAnyInternet = true;  // 需要网络
WorkParams.bRequireCharging = false;     // 不要求充电

// 3. 设置初始延迟（可选，默认 0）
WorkParams.InitialStartDelayInSeconds = 30;  // 延迟 30 秒

// 4. 调度任务
bool bSuccess = FUEWorkManagerNativeWrapper::ScheduleBackgroundWork(
    TEXT("MyUniqueWorkName"),  // 唯一标识，用于取消或防止重复
    WorkParams
);
```

### 基本用法：取消后台任务

```cpp
// 来源: UEWorkManagerNativeWrapper.h 的 CancelBackgroundWork 接口
FUEWorkManagerNativeWrapper::CancelBackgroundWork(TEXT("MyUniqueWorkName"));
```

### 基本用法：监听 Worker 生命周期

```cpp
// 来源: UEWorkManagerNativeWrapper.h 的 FAndroidBackgroundServicesDelegates

// 绑定 Worker 启动回调
FAndroidBackgroundServicesDelegates::AndroidBackgroundServices_OnWorkerStart.AddLambda(
    [](FString WorkID, jobject Worker) {
        UE_LOG(LogTemp, Log, TEXT("Worker started: %s"), *WorkID);
        
        // 执行你的后台逻辑...
        
        // 设置结果为成功
        FUEWorkManagerNativeWrapper::SetWorkResultOnWorker(
            Worker, 
            FUEWorkManagerNativeWrapper::EAndroidBackgroundWorkResult::Success
        );
    }
);

// 绑定 Worker 停止回调
FAndroidBackgroundServicesDelegates::AndroidBackgroundServices_OnWorkerStop.AddLambda(
    [](FString WorkID, jobject Worker) {
        UE_LOG(LogTemp, Log, TEXT("Worker stopped: %s"), *WorkID);
        
        // 查询结果
        auto Result = FUEWorkManagerNativeWrapper::GetWorkResultOnWorker(Worker);
        // Result 可能是 Success, Failure, Retry, NotSet
    }
);
```

### 进阶用法：传递自定义数据到 Worker

```cpp
// 来源: UEWorkManagerNativeWrapper.h 的 FWorkRequestParametersNative::AddDataToWorkerParameters

FUEWorkManagerNativeWrapper::FWorkRequestParametersNative WorkParams;

// 支持多种数据类型
WorkParams.AddDataToWorkerParameters(TEXT("TaskType"), TEXT("SyncStats"));
WorkParams.AddDataToWorkerParameters(TEXT("Priority"), 5);
WorkParams.AddDataToWorkerParameters(TEXT("Score"), 99.5f);
WorkParams.AddDataToWorkerParameters(TEXT("IsImportant"), true);
WorkParams.AddDataToWorkerParameters(TEXT("Timestamp"), (long)1234567890L);

// 这些数据会通过 AndroidX WorkManager 的 Data 传递到 Worker
// 在 Java 侧可通过 getInputData() 读取
```

### 进阶用法：配置高级约束

```cpp
FUEWorkManagerNativeWrapper::FWorkRequestParametersNative WorkParams;

// 电量约束
WorkParams.bRequireBatteryNotLow = true;  // 电量不能太低
WorkParams.bRequireCharging = true;        // 需要在充电时执行

// 网络约束
WorkParams.bRequireWifi = true;            // 需要 WiFi（优先级高于下面两项）
WorkParams.bRequireAnyInternet = true;     // 需要任意网络（如果上面 WiFi 为 false）
WorkParams.bAllowRoamingInternet = false;  // 是否允许漫游网络

// 存储约束
WorkParams.bRequireStorageNotLow = true;   // 存储空间不能太低

// 设备状态约束
WorkParams.bRequireDeviceIdle = true;      // 需要设备空闲时

// 前台服务（防止系统杀死）
WorkParams.bStartAsForegroundService = true;
```

### 进阶用法：设置任务重试策略

```cpp
FUEWorkManagerNativeWrapper::FWorkRequestParametersNative WorkParams;

// 退避策略
WorkParams.bUseLinearBackoffPolicy = false;  // false=指数退避, true=线性退避
WorkParams.InitialBackoffDelayInSeconds = 10; // 初始退避延迟

// 注意：如果 Worker 回调中没有调用 SetWorkResultOnWorker，
// 默认行为是 Retry（重试）
```

## Demo 示例

以下是一个完整的最小示例，演示如何在 UE5 Android 项目中使用后台服务。

### Build.cs

```csharp
using UnrealBuildTool;

public class MyGame : ModuleRules
{
    public MyGame(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

        PublicDependencyModuleNames.AddRange(new string[] {
            "Core",
            "CoreUObject",
            "Engine",
        });
    }
}
```

**注意：** 你不需要在 Build.cs 中显式依赖 `AndroidBackgroundService` 模块。该 Plugin 的所有依赖项（Core, CoreUObject, Engine, Launch）均为私有依赖。你需要做的是在 `.uproject` 文件中启用该 Plugin，然后通过 `#include "UEWorkManagerNativeWrapper.h"` 引入头文件即可（因为头文件在 Public 目录下）。

### MyBackgroundTaskComponent.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "MyBackgroundTaskComponent.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class MYGAME_API UMyBackgroundTaskComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UMyBackgroundTaskComponent();

    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    /** 调度一个后台任务 */
    UFUNCTION(BlueprintCallable, Category = "Background Service")
    void ScheduleTask(const FString& TaskName);

    /** 取消一个后台任务 */
    UFUNCTION(BlueprintCallable, Category = "Background Service")
    void CancelTask(const FString& TaskName);

private:
    void OnWorkerStart(FString WorkID, jobject Worker);
    void OnWorkerStop(FString WorkID, jobject Worker);

    FDelegateHandle OnWorkerStartHandle;
    FDelegateHandle OnWorkerStopHandle;
};
```

### MyBackgroundTaskComponent.cpp

```cpp
#include "MyBackgroundTaskComponent.h"

#if USE_ANDROID_JNI
#include "UEWorkManagerNativeWrapper.h"
#endif

UMyBackgroundTaskComponent::UMyBackgroundTaskComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UMyBackgroundTaskComponent::BeginPlay()
{
    Super::BeginPlay();

#if USE_ANDROID_JNI
    OnWorkerStartHandle = FAndroidBackgroundServicesDelegates::AndroidBackgroundServices_OnWorkerStart.AddUObject(
        this, &UMyBackgroundTaskComponent::OnWorkerStart);
    OnWorkerStopHandle = FAndroidBackgroundServicesDelegates::AndroidBackgroundServices_OnWorkerStop.AddUObject(
        this, &UMyBackgroundTaskComponent::OnWorkerStop);
#endif
}

void UMyBackgroundTaskComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
#if USE_ANDROID_JNI
    FAndroidBackgroundServicesDelegates::AndroidBackgroundServices_OnWorkerStart.Remove(OnWorkerStartHandle);
    FAndroidBackgroundServicesDelegates::AndroidBackgroundServices_OnWorkerStop.Remove(OnWorkerStopHandle);
#endif

    Super::EndPlay(EndPlayReason);
}

void UMyBackgroundTaskComponent::ScheduleTask(const FString& TaskName)
{
#if USE_ANDROID_JNI
    FUEWorkManagerNativeWrapper::FWorkRequestParametersNative WorkParams;
    WorkParams.bRequireAnyInternet = true;
    WorkParams.InitialStartDelayInSeconds = 10;

    WorkParams.AddDataToWorkerParameters(TEXT("TaskType"), TaskName);

    bool bSuccess = FUEWorkManagerNativeWrapper::ScheduleBackgroundWork(TaskName, WorkParams);
    UE_LOG(LogTemp, Log, TEXT("ScheduleTask '%s': %s"), *TaskName, bSuccess ? TEXT("OK") : TEXT("Failed"));
#else
    UE_LOG(LogTemp, Warning, TEXT("AndroidBackgroundService is only available on Android"));
#endif
}

void UMyBackgroundTaskComponent::CancelTask(const FString& TaskName)
{
#if USE_ANDROID_JNI
    FUEWorkManagerNativeWrapper::CancelBackgroundWork(TaskName);
    UE_LOG(LogTemp, Log, TEXT("CancelTask '%s'"), *TaskName);
#endif
}

void UMyBackgroundTaskComponent::OnWorkerStart(FString WorkID, jobject Worker)
{
#if USE_ANDROID_JNI
    UE_LOG(LogTemp, Log, TEXT("Worker started: %s"), *WorkID);

    // 执行你的后台逻辑...

    // 设置结果为成功
    FUEWorkManagerNativeWrapper::SetWorkResultOnWorker(
        Worker,
        FUEWorkManagerNativeWrapper::EAndroidBackgroundWorkResult::Success
    );
#endif
}

void UMyBackgroundTaskComponent::OnWorkerStop(FString WorkID, jobject Worker)
{
#if USE_ANDROID_JNI
    auto Result = FUEWorkManagerNativeWrapper::GetWorkResultOnWorker(Worker);
    UE_LOG(LogTemp, Log, TEXT("Worker stopped: %s, Result: %d"), *WorkID, (int32)Result);
#endif
}
```

## 模块依赖

该 Plugin 的 `Build.cs` 中均为 **PrivateDependencyModuleNames**，意味着使用者不需要在自己的模块中显式依赖这些模块（它们是 Plugin 内部使用的）：

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心库（基础类型、日志、文件系统等） |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心功能 |
| `Launch` | 启动模块（提供 GameActivity 等 Android 入口） |

使用者需要确保：
1. 在 `.uproject` 中启用 `AndroidBackgroundService` Plugin
2. 项目的目标平台包含 Android
3. 最低 SDK API 级别为 28（Android 9.0），由 UPL 自动设置

### Gradle 依赖（自动管理）

Plugin 通过 UPL 自动添加以下 Gradle 依赖，无需手动配置：

| 依赖 | 版本 | 用途 |
|---|---|---|
| `androidx.appcompat:appcompat` | 1.6.1 | AndroidX 基础兼容库 |
| `androidx.work:work-runtime` | 2.8.1 | WorkManager 运行时 |
| `androidx.concurrent:concurrent-futures` | 1.1.0 | 并发 Future 支持 |
| `androidx.multidex:multidex` | 2.0.1 | MultiDex 支持 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-10-02 | `e37dc67c76e4` | Fix TargetSDK 35 compat issues with background download | 修复 Android SDK 35 的兼容性问题，说明在跟进最新 Android 版本 |
| 2025-09-11 | `6312e16dd97c` | Fix crash from pending JNI exception in non-Shipping builds | 修复 JNI 异常导致的崩溃，提高稳定性 |
| 2025-09-02 | `5a48f72f610f` | Registered JNI functions. Made JNI classes for Java classes. Added thread_local UE::Jni::Env global. Various JNI bug fixes and cleanup | 重大重构：使用新的 UE JNI 框架（`UE::Jni::TInitialize`），提升代码质量和线程安全性 |

### 维护评价

- **创建时间：** 2021-06-14（约 5 年前）
- **最近更新：** 2025-10-02（约 7 个月前）
- **维护状态：** ✅ **活跃维护** — 最近 3 次提交集中在 2025 年 9-10 月，包含 SDK 兼容性修复、崩溃修复和 JNI 框架重构
- **已知限制：**
  - 仅支持 Android 平台
  - 默认禁用，需要手动启用
  - 周期性任务（`bIsRecurringWork`）的 Java 实现中有 `return false`，说明该功能**尚未完成**
  - 不提供蓝图接口，仅限 C++ 使用
  - 所有 JNI 操作必须在 GameThread 上执行（`FJavaClassInfo::Initialize` 中有 `check(IsInGameThread())`）
- **推荐程度：** ⭐⭐⭐ 推荐用于需要 Android 后台任务调度的项目，但需要注意周期性任务功能尚未完整实现

## 架构概览

```
┌─────────────────────────────────────────────────────┐
│  UE C++ (GameThread)                                │
│  ┌─────────────────────────────────────────────┐    │
│  │ FUEWorkManagerNativeWrapper                  │    │
│  │  ├── ScheduleBackgroundWork()               │    │
│  │  ├── CancelBackgroundWork()                 │    │
│  │  ├── FWorkRequestParametersNative           │    │
│  │  └── EAndroidBackgroundWorkResult           │    │
│  └──────────────┬──────────────┬────────────────┘    │
│                 │ JNI          │ JNI                 │
│  ┌──────────────▼──┐  ┌───────▼────────────────┐    │
│  │ OnWorkerStart   │  │ RegisterWork / Cancel   │    │
│  │ OnWorkerStop    │  │                         │    │
│  │ (回调 delegates) │  │                         │    │
│  └─────────────────┘  └─────────────────────────┘    │
└───────────────────┬─────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────┐
│  Java Layer                                         │
│  ┌─────────────────────────────────────────────┐    │
│  │ UEWorkManagerJavaInterface                   │    │
│  │  ├── AndroidThunkJava_RegisterWork()        │    │
│  │  ├── AndroidThunkJava_CancelWork()          │    │
│  │  └── FWorkRequestParametersJavaInterface    │    │
│  └──────────────┬──────────────────────────────┘    │
│                 │                                    │
│  ┌──────────────▼──────────────────────────────┐    │
│  │ AndroidX WorkManager                         │    │
│  │  └── UEWorker extends Worker                 │    │
│  │       ├── doWork() → OnWorkerStart()        │    │
│  │       ├── SetWorkResult_Success/Failure/Retry│    │
│  │       └── CallNativeOnWorkerStart/Stop()    │    │
│  └──────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────┘
```

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/AndroidBackgroundService)
- [AndroidX WorkManager 官方文档](https://developer.android.com/topic/libraries/architecture/workmanager)
- [Android WorkManager Constraints 参考](https://developer.android.com/reference/androidx/work/Constraints.Builder)
