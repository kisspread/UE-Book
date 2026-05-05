# Google Cloud Messaging

> Support for remote notifications using Google Cloud Messaging

| 属性 | 值 |
|---|---|
| 分类 | Online Platform |
| 默认启用 | true |
| 包含内容 | false |
| 模块 | GoogleCloudMessaging (Runtime) |
| 创建时间 | 2017-02-09 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GoogleCloudMessaging) | |

## 用途

GoogleCloudMessaging plugin 是 UE5 在 **Android** 平台上接收 **Google Cloud Messaging (GCM)** 推送通知的原生桥接层。它通过 Java 服务注册 GCM、接收消息，并通过 JNI 回调将事件传递到 UE 的 `FCoreDelegates`，使 C++ / 蓝图层能统一处理远程通知。

**⚠️ 重要提示：Google 已于 2018 年弃用 GCM，推荐使用 Firebase Cloud Messaging (FCM)。** 此 plugin 使用的是 `play-services-gcm:17.0.0`，属于过时技术栈。新项目应使用 FCM 插件或自行集成 Firebase SDK。

## 使用场景

- 你的 Android 游戏需要接收服务器推送的通知（如活动提醒、版本更新提示）
- 你需要通过 GCM topic 订阅机制向所有玩家广播消息
- 你维护的是一个老项目，已经在使用 GCM 且暂未迁移到 FCM

## 蓝图用法

此 plugin **没有暴露任何 BlueprintCallable 函数**。它是一个纯原生桥接模块，所有通信通过 `FCoreDelegates` 广播委托完成。

### 接收通知的蓝图方式

虽然 plugin 本身没有蓝图节点，但你可以在蓝图中通过 **Event Dispatcher** 监听远程通知：

1. 在 C++ 中绑定 `FCoreDelegates::ApplicationReceivedRemoteNotificationDelegate`
2. 将收到的消息通过自定义事件分发到蓝图

## C++ 用法

### 头文件引入

```cpp
#include "GoogleCloudMessaging.h"
#include "Misc/CoreDelegates.h"
```

### 基本用法

Plugin 的核心工作流程完全通过 `FCoreDelegates` 委托完成。你需要绑定以下三个委托：

```cpp
// 注册成功 — 收到 GCM token
FCoreDelegates::ApplicationRegisteredForRemoteNotificationsDelegate.AddLambda(
    [](const TArray<uint8>& TokenBytes)
    {
        FString Token = FString(UTF8_TO_TCHAR(TokenBytes.GetData()));
        UE_LOG(LogTemp, Log, TEXT("GCM Token: %s"), *Token);
        // 将 token 发送到你的后端服务器
    }
);

// 注册失败
FCoreDelegates::ApplicationFailedToRegisterForRemoteNotificationsDelegate.AddLambda(
    [](const FString& ErrorMessage)
    {
        UE_LOG(LogTemp, Error, TEXT("GCM Registration Failed: %s"), *ErrorMessage);
    }
);

// 收到推送消息
FCoreDelegates::ApplicationReceivedRemoteNotificationDelegate.AddLambda(
    [](const FString& Message, int32 AppState)
    {
        // AppState: 1=Inactive, 2=Background, 3=Active
        UE_LOG(LogTemp, Log, TEXT("GCM Message (State=%d): %s"), AppState, *Message);
        // 处理通知内容
    }
);
```

> **来源**: `GoogleCloudMessagingAndroid.cpp` — 三个 JNI 回调分别广播上述委托。

### 进阶用法：模块可用性检查

```cpp
if (IGoogleCloudMessagingModuleInterface::IsAvailable())
{
    IGoogleCloudMessagingModuleInterface& GCMModule = IGoogleCloudMessagingModuleInterface::Get();
    // 模块已加载，可以安全使用
}
```

## Demo 示例

### 最小通知监听器

```cpp
// MyNotificationListener.h
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "MyNotificationListener.generated.h"

UCLASS()
class UMyNotificationListener : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

    DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnRemoteNotification, FString, Message, int32, AppState);

    UPROPERTY(BlueprintAssignable)
    FOnRemoteNotification OnRemoteNotificationReceived;

private:
    FDelegateHandle MessageHandle;
};

// MyNotificationListener.cpp
#include "MyNotificationListener.h"
#include "Misc/CoreDelegates.h"

void UMyNotificationListener::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);

    MessageHandle = FCoreDelegates::ApplicationReceivedRemoteNotificationDelegate.AddLambda(
        [this](const FString& Message, int32 AppState)
        {
            OnRemoteNotificationReceived.Broadcast(Message, AppState);
        }
    );
}

void UMyNotificationListener::Deinitialize()
{
    FCoreDelegates::ApplicationReceivedRemoteNotificationDelegate.Remove(MessageHandle);
    Super::Deinitialize();
}
```

**Build.cs 依赖**:

```csharp
PublicDependencyModuleNames.AddRange(new string[] { "Core", "CoreUObject", "Engine" });
```

无需显式依赖 `GoogleCloudMessaging` 模块——该 plugin 通过 UPL 自动注入 Java 代码和 AndroidManifest 配置，运行时自动生效。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 引擎核心 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎运行时 |
| `Launch` | 启动阶段支持 |
| `EditorFramework` | 编辑器框架（仅编辑器构建） |
| `UnrealEd` | 编辑器工具（仅编辑器构建） |

**外部依赖** (Android): `com.google.android.gms:play-services-gcm:17.0.0`

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2023-12-18 | `13ed363e` | 修复更多 GameActivity._activity 引用问题 |
| 2023-12-14 | `3dcdaa23` | 修复 _activity 使用错误 |
| 2023-04-10 | `c3a3d4f2` | 修复 Google Play Services 支持（移除 CVE-2022-2390 安全问题），添加 AdMob app id |

### 维护评价

- **创建时间**: 2017 年 2 月，已有 **9 年**历史
- **最近更新**: 2023-12-18，最近 3 次提交均为编译/兼容性修复，无功能性更新
- **维护状态**: ⚠️ **可能废弃**
- **技术栈过时**: Google 已于 2018 年弃用 GCM，改用 FCM (Firebase Cloud Messaging)。此 plugin 依赖的 `play-services-gcm:17.0.0` 已停止更新
- **无 Blueprint 暴露**: 纯原生桥接，无 UFUNCTION/UPROPERTY 暴露给蓝图
- **仅 Android**: 平台限制明确

**⚠️ 不推荐新项目使用。** 如果你需要 Android 推送通知，应使用 Firebase Cloud Messaging (FCM) 并自行集成 Firebase SDK。此 plugin 仅适用于维护已有 GCM 集成的老项目。

## 内部架构

Plugin 由三层组成：

1. **Java 服务层** (`Source/Java/`)
   - `RemoteNotificationsRegistrationIntentService` — 向 GCM 注册设备，获取 token，订阅 `/topics/global`
   - `RemoteNotificationsListener` — 监听 GCM 消息，通过 JNI 回调到 C++
   - `RemoteNotificationsInstanceIDListener` — 监听 token 刷新事件

2. **C++ JNI 桥接层** (`GoogleCloudMessagingAndroid.cpp`)
   - 接收 Java 回调，转发到游戏线程的 `FCoreDelegates`

3. **UPL 配置** (`GoogleCloudMessaging_UPL.xml`)
   - 自动修改 `AndroidManifest.xml` 添加 GCM 权限和服务声明
   - 从项目设置读取 `GCMClientSenderID`（位于 `Engine` INI 的 `/Script/AndroidRuntimeSettings.AndroidRuntimeSettings` 节）

### 配置要求

使用此 plugin 需要在 **项目设置 → Android Runtime Settings** 中配置 `GCMClientSenderID`（即 Google API Console 中创建的 Sender ID）。如果该值为空，UPL 会跳过所有 Android 配置注入。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GoogleCloudMessaging)
- 官方文档: 无
- 测试用例: 无
