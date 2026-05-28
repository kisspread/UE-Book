# Android Background Service

> Allows you to use AndroidX WorkManager to perform background work on Android

| 属性 | 值 |
|---|---|
| 中文名 | 安卓后台服务 |
| 分类 | Android Background Service |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AndroidBackgroundService` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-06-22 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AndroidBackgroundService) | |

## 用途

此插件为 UE5 的 Android 目标平台提供了一个用于调度和管理后台任务的封装层。它通过 JNI（Java Native Interface）桥接了 Unreal Engine C++ 代码与 Android Jetpack 库中的 `WorkManager`。`WorkManager` 是 Android 官方推荐的用于执行可靠、可延迟的后台任务的 API，即使应用程序退出或设备重启，也能保证任务的执行。插件的核心作用是让开发者能够使用 C++ 配置后台工作的约束条件（如网络状态、电量、充电状态等）、调度一次性或周期性任务，并在 UE 侧接收任务开始和结束的回调。

## 使用场景

- **游戏后台下载**：当玩家在前台游玩时，在后台静默下载新地图、DLC 资源或更新包，利用 `WorkManager` 的智能调度优化网络和电量使用。
- **离线数据同步**：当设备重新连接到网络时，自动同步本地的游戏存档、设置或分析数据。
- **周期性任务**：定期检查服务器消息、更新排行榜或执行游戏内的“每日任务”重置逻辑。
- **需要特定条件的任务**：调度仅在设备充电、连接 Wi-Fi 或电量充足时执行的资源密集型后台任务。

## 蓝图用法

该插件的主要接口为 C++ API，未在头文件中暴露 `BlueprintCallable` 函数。后台任务的调度和管理需通过 C++ 代码完成。

## C++ 用法

### 头文件引入

```cpp
#include “UEWorkManagerNativeWrapper.h”
```

### 基本用法

首先，创建一个 `FWorkRequestParametersNative` 结构体来配置后台任务。然后，使用 `FUEWorkManagerNativeWrapper::ScheduleBackgroundWork` 来调度任务。

```cpp
// 示例：调度一个需要网络连接、充电时执行的一次性后台任务
#include “UEWorkManagerNativeWrapper.h”

void ScheduleMyBackgroundTask()
{
    // 1. 创建并配置任务参数
    FUEWorkManagerNativeWrapper::FWorkRequestParametersNative TaskParams;
    TaskParams.bRequireAnyInternet = true; // 需要任何网络连接
    TaskParams.bRequireCharging = true;    // 需要设备正在充电
    TaskParams.bStartAsForegroundService = false;
    TaskParams.InitialStartDelayInSeconds = 10; // 延迟10秒开始

    // 2. 给任务附加一些数据（可选）
    // 注意：此处 AddDataToWorkerParameters 的参数是 Java 对象，在 UE C++ 中通常需要通过 JNI 创建。
    // 简单类型如 int, bool 等可以使用对应的重载。
    TaskParams.AddDataToWorkerParameters(TEXT(”RetryCount“), 3);
    TaskParams.AddDataToWorkerParameters(TEXT(”DownloadURL“), TEXT(”https://example.com/resource.pak“));

    // 3. 调度任务
    FString UniqueTaskName = TEXT(”MyResourceDownloadTask”);
    bool bSuccess = FUEWorkManagerNativeWrapper::ScheduleBackgroundWork(UniqueTaskName, TaskParams);

    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT(”Background task '%s' scheduled successfully.”), *UniqueTaskName);
    }
}
```

### 进阶用法

你可以绑定回调来接收任务开始和结束的通知。

```cpp
// 绑定回调以监控任务状态
#include “UEWorkManagerNativeWrapper.h”

void MonitorBackgroundTask()
{
    // 绑定任务开始回调
    FAndroidBackgroundServicesDelegates::AndroidBackgroundServices_OnWorkerStart.AddLambda(
        [](const FString& WorkID, jobject WorkerObject)
        {
            UE_LOG(LogTemp, Log, TEXT(”Background work '%s' has started.”), *WorkID);
            // 在这里可以更新 UI 或记录日志
        }
    );

    // 绑定任务结束回调
    FAndroidBackgroundServicesDelegates::AndroidBackgroundServices_OnWorkerStop.AddLambda(
        [](const FString& WorkID, jobject WorkerObject)
        {
            UE_LOG(LogTemp, Log, TEXT(”Background work '%s' has stopped.”), *WorkID);
            // 获取任务结果
            FUEWorkManagerNativeWrapper::EAndroidBackgroundWorkResult Result =
                FUEWorkManagerNativeWrapper::GetWorkResultOnWorker(WorkerObject);

            if (Result == FUEWorkManagerNativeWrapper::EAndroidBackgroundWorkResult::Success)
            {
                UE_LOG(LogTemp, Log, TEXT(”Task '%s' completed successfully.”), *WorkID);
            }
            // 处理其他结果（Failure, Retry, NotSet）...
        }
    );

    // 之后再调度任务，回调便会生效
}
```

## Demo 示例

一个完整的、可在 Android 模块中运行的最小示例。

**MyBackgroundTaskManager.h**
```cpp
#pragma once

class FMyBackgroundTaskManager
{
public:
    static void Initialize();
    static void Shutdown();

private:
    static void ScheduleSampleTask();
    static void OnTaskStarted(const FString& WorkID, jobject WorkerObject);
    static void OnTaskStopped(const FString& WorkID, jobject WorkerObject);
};
```

**MyBackgroundTaskManager.cpp**
```cpp
#include “MyBackgroundTaskManager.h”
#include “UEWorkManagerNativeWrapper.h”

// 保存委托句柄以便后续解绑
static FDelegateHandle OnStartHandle;
static FDelegateHandle OnStopHandle;

void FMyBackgroundTaskManager::Initialize()
{
    // 绑定回调
    OnStartHandle = FAndroidBackgroundServicesDelegates::AndroidBackgroundServices_OnWorkerStart.AddStatic(&FMyBackgroundTaskManager::OnTaskStarted);
    OnStopHandle = FAndroidBackgroundServicesDelegates::AndroidBackgroundServices_OnWorkerStop.AddStatic(&FMyBackgroundTaskManager::OnTaskStopped);

    // 调度一个示例任务
    ScheduleSampleTask();
}

void FMyBackgroundTaskManager::Shutdown()
{
    // 解绑回调
    if (FAndroidBackgroundServicesDelegates::AndroidBackgroundServices_OnWorkerStart.IsBound())
    {
        FAndroidBackgroundServicesDelegates::AndroidBackgroundServices_OnWorkerStart.Remove(OnStartHandle);
    }
    if (FAndroidBackgroundServicesDelegates::AndroidBackgroundServices_OnWorkerStop.IsBound())
    {
        FAndroidBackgroundServicesDelegates::AndroidBackgroundServices_OnWorkerStop.Remove(OnStopHandle);
    }

    // 可选：取消所有已调度的任务
    FUEWorkManagerNativeWrapper::CancelBackgroundWork(TEXT(”DemoBackgroundTask”));
}

void FMyBackgroundTaskManager::ScheduleSampleTask()
{
    FUEWorkManagerNativeWrapper::FWorkRequestParametersNative Params;
    Params.bRequireAnyInternet = true; // 需要网络
    Params.bIsPeriodicWork = false;    // 非周期性任务
    Params.InitialStartDelayInSeconds = 5; // 5秒后开始

    // 调度任务
    bool bScheduled = FUEWorkManagerNativeWrapper::ScheduleBackgroundWork(
        TEXT(”DemoBackgroundTask”), Params);

    check(bScheduled);
}

void FMyBackgroundTaskManager::OnTaskStarted(const FString& WorkID, jobject WorkerObject)
{
    UE_LOG(LogTemp, Display, TEXT(”[Demo] Background task '%s' started.”), *WorkID);
}

void FMyBackgroundTaskManager::OnTaskStopped(const FString& WorkID, jobject WorkerObject)
{
    FUEWorkManagerNativeWrapper::EAndroidBackgroundWorkResult Result =
        FUEWorkManagerNativeWrapper::GetWorkResultOnWorker(WorkerObject);

    UE_LOG(LogTemp, Display, TEXT(”[Demo] Background task '%s' stopped with result: %d.”),
        *WorkID, static_cast<int32>(Result));

    if (Result == FUEWorkManagerNativeWrapper::EAndroidBackgroundWorkResult::Success)
    {
        UE_LOG(LogTemp, Display, TEXT(”[Demo] Task completed successfully!”));
    }
}
```

## 模块依赖

此插件主要封装了 Android 平台特有库。对于希望在自身模块中使用此插件功能的 UE 开发者，需要添加对 `AndroidBackgroundService` 模块的依赖。

| 模块 | 用途 |
|---|---|
| `AndroidBackgroundService` | 访问后台任务调度 API (`FUEWorkManagerNativeWrapper` 及相关结构体) |

*注意：`AndroidBackgroundService` 模块内部依赖 Android SDK/JNI 以及 AndroidX WorkManager 库，这些依赖由模块自身的 `Build.cs` 处理，使用者无需直接管理。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `65d405ac` | Changed androidx WorkManager auto initialization to on-demand to prevent certain WorkManager crashes | 将 WorkManager 的自动初始化改为按需初始化，以防止某些崩溃 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF |
| 2026-02-03 | `51855179` | Fixes to AsyncDownloader and WorkManager | 修复异步下载器和 WorkManager 相关的问题 |
| 2026-01-12 | `69d8f2f1` | Fix for installation stalling | 修复安装过程可能卡住的问题 |
| 2025-12-17 | `8563a09d` | Fixed Potential Hang in Android Background Downloader | 修复安卓后台下载器中的潜在挂起问题 |

### 维护评价

该插件自 2021 年创建以来，一直处于**活跃维护**状态。从近期的 Git 提交历史来看，维护频率较高，更新内容主要集中在 **稳定性修复和性能优化** 上，例如解决崩溃、卡顿问题以及调整内部初始化逻辑。这些更新表明 Epic 仍然在持续关注并改进此插件。尽管它默认未启用，且使用场景特定于 Android 后台任务，但对于有相关需求的项目，这是一个**稳定可靠且推荐使用**的官方解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AndroidBackgroundService)