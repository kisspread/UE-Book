# Firebase

> Support for remote notifications using Firebase

| 属性 | 值 |
|---|---|
| 分类 | Online Platform |
| 默认启用 | false |
| 包含内容 | false |
| 模块 | Firebase (Runtime) |
| 创建时间 | 2018-09-25 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Firebase) | |

## 用途

Firebase plugin 是 Epic Games 为 UE5 提供的 **FCM (Firebase Cloud Messaging) 推送通知集成层**。它并非对整个 Firebase SDK 的完整封装，而是专注于 **远程推送通知（Remote Notifications）** 这一单一功能。

plugin 的核心职责：
- 在 **Android** 和 **iOS** 上初始化 Firebase SDK 并获取 FCM token
- 管理 token 的缓存、刷新和项目切换检测
- 在 Android 上接收和展示推送通知（前台/后台）
- 将 token 变更事件通过 delegate 桥接到 UE 的 GameThread

> ⚠️ **重要说明**：此 plugin 默认关闭（`EnabledByDefault: false`），且仅支持 Android 和 iOS 平台，不支持桌面平台。PC/Mac 编译时该模块不会被编入。

## 使用场景

- 你的移动游戏需要从后端服务器向玩家设备发送推送通知（如活动提醒、好友消息）
- 你需要集成 Firebase Analytics 进行用户行为追踪（iOS 端支持）
- 你需要在 UE5 中使用自定义的 `google-services.json` / `GoogleService-Info.plist` 配置 Firebase 项目

## 蓝图用法

此 plugin **没有暴露任何蓝图节点**。它是一个纯 C++ 模块，不包含任何 `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)`。所有操作都在 C++ 层面完成。

如果你需要在蓝图中触发推送通知相关的逻辑，需要自行封装一个 BlueprintFunctionLibrary 来桥接。

## C++ 用法

### 头文件引入

```cpp
#include "Firebase.h"
```

### 基本用法

#### 监听 FCM Token 更新

当 Firebase token 发生刷新时（首次获取、token 过期、项目切换），plugin 会通过 `OnTokenUpdate` multicast delegate 广播通知：

```cpp
// 来源: Source/Public/Firebase.h (line 42)
// 在模块加载后绑定 token 更新回调
if (IFirebaseModuleInterface::IsAvailable())
{
    IFirebaseModuleInterface::Get().OnTokenUpdate.AddLambda(
        [](const FString& PreviousToken, const FString& NewToken)
        {
            UE_LOG(LogTemp, Log, TEXT("Firebase token updated: %s -> %s"),
                *PreviousToken, *NewToken);
            // 将 NewToken 发送到你的后端服务器注册设备
        });
}
```

### iOS 平台进阶用法

iOS 端通过 `FFirebaseIOSNotifications` 提供更多控制（需在 `Build.cs` 中启用 `WITH_IOS_FIREBASE_INTEGRATION`）：

```cpp
// 来源: Source/IOS/notifications/EpicFirebaseIOSNotifications.h
#if PLATFORM_IOS && WITH_IOS_FIREBASE_INTEGRATION

// 使用默认 GoogleService-Info.plist 配置
FFirebaseIOSNotifications::ConfigureFirebase();

// 或使用自定义配置文件
FFirebaseIOSNotifications::ConfigureFirebaseWithCustomFile(TEXT("CustomFirebase-Info.plist"));

// 初始化（设置 token 查询超时，可选启用 Analytics）
FFirebaseIOSNotifications::Initialize(
    10000000000ULL,  // TokenQueryTimeoutNanoseconds (10秒)
    true             // bEnableAnalytics
);

// 获取当前缓存的 FCM token
FString Token = FFirebaseIOSNotifications::GetFirebaseToken();

// 启用 Firebase 自动初始化
FFirebaseIOSNotifications::EnableFirebaseAutoInit();

// 删除 token（用于用户退出登录等场景）
FFirebaseIOSNotifications::DeleteFirebaseToken();

#endif
```

### Android 平台配置

Android 端的初始化由 Gradle 构建系统自动处理，但需要在 `Engine.ini` 中启用：

```ini
[/Script/AndroidRuntimeSettings.AndroidRuntimeSettings]
FirebaseEnabled=true

; 可选：禁用自动初始化（手动控制初始化时机）
FirebaseDisableAutoInit=false

; 可选：自定义 Messaging Service 类名
FirebaseService=com.epicgames.unreal.notifications.EpicFirebaseMessagingService
```

此外需要将 `google-services.json` 放入构建目录。

### 自定义 Firebase 配置（Android）

```cpp
// 来源: Source/Java/notifications/EpicFirebaseMessagingService.java (line 433)
// 从 assets 中的自定义 JSON 文件初始化 Firebase
// 文件格式：
// {
//   "project_info": {
//     "project_number": "...",
//     "firebase_url": "...",
//     "project_id": "...",
//     "storage_bucket": "..."
//   },
//   "client": [{
//     "client_info": { "mobilesdk_app_id": "..." },
//     "api_key": [{ "current_key": "..." }]
//   }]
// }
```

## Demo 示例

### 最小 C++ 集成示例

#### Build.cs

```csharp
// YourGame.Build.cs
using UnrealBuildTool;

public class YourGame : ModuleRules
{
    public YourGame(ReadOnlyTargetRules Target) : base(Target)
    {
        PublicDependencyModuleNames.AddRange(new string[]
        {
            "Core",
            "CoreUObject",
            "Engine",
            "Firebase"  // 依赖 Firebase 模块
        });
    }
}
```

#### YourGameSubsystem.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "Firebase.h"
#include "YourGameSubsystem.generated.h"

UCLASS()
class YOURGAME_API UYourGameSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

private:
    void OnFirebaseTokenUpdated(const FString& OldToken, const FString& NewToken);
    FDelegateHandle TokenDelegateHandle;
};
```

#### YourGameSubsystem.cpp

```cpp
#include "YourGameSubsystem.h"

void UYourGameSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);

    if (IFirebaseModuleInterface::IsAvailable())
    {
        TokenDelegateHandle = IFirebaseModuleInterface::Get().OnTokenUpdate.AddUObject(
            this, &UYourGameSubsystem::OnFirebaseTokenUpdated);
    }
}

void UYourGameSubsystem::Deinitialize()
{
    if (IFirebaseModuleInterface::IsAvailable())
    {
        IFirebaseModuleInterface::Get().OnTokenUpdate.Remove(TokenDelegateHandle);
    }
    Super::Deinitialize();
}

void UYourGameSubsystem::OnFirebaseTokenUpdated(const FString& OldToken, const FString& NewToken)
{
    UE_LOG(LogTemp, Log, TEXT("Firebase token changed! Sending to backend..."));
    // 在此将 NewToken 注册到你的推送服务后端
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `Launch` | 启动流程（Android 额外依赖） |
| `Swift` | Swift 互操作（仅 iOS） |

**注意**：这些依赖都在 `PrivateDependencyModuleNames` 中，意味着使用方 **不需要** 额外声明这些模块依赖——它们是 Firebase 模块自身的内部依赖。使用方只需依赖 `Firebase` 模块本身。

### iOS Framework 依赖

iOS 构建时会自动链接以下 Firebase 框架：

| Framework | 用途 |
|---|---|
| `FirebaseAnalytics` | 分析数据收集 |
| `FirebaseCore` | Firebase 核心 |
| `FirebaseCoreInternal` | 核心内部实现 |
| `FirebaseMessaging` | FCM 消息推送 |
| `FirebaseInstallations` | 安装实例管理 |
| `GoogleAppMeasurement` | Google 测量 |
| `GoogleDataTransport` | 数据传输 |
| `GoogleUtilities` | Google 工具库 |
| `FBLPromises` | 异步任务 |
| `nanopb` | Protocol Buffers 轻量实现 |

### Android Gradle 依赖

| 依赖 | 版本 |
|---|---|
| `com.google.firebase:firebase-core` | 21.1.1 |
| `com.google.firebase:firebase-messaging` | 23.0.8 |
| `com.google.gms:google-services` | 4.4.2 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-08-26 | `0e2917ff` | Firebase will log project ID in non-shipping builds | 调试改进：非发布构建下打印 Firebase 项目 ID，方便排查配置问题 |
| 2025-08-14 | `f453eb51` | Ensure java sources are wiped when FirebaseEnabled is toggled off | 修复 bug：关闭 Firebase 开关后残留的 Java 源文件导致编译失败；同时注册了 UPL 构建设置 |
| 2025-05-14 | `65a9455f` | Fixes missing include | 编译修复 |

### 维护评价

- **年龄**：约 7.6 岁（2018年9月创建）
- **最近更新**：2025年8月，有功能性改进和 bug 修复
- **活跃度**：维护中。近3次提交集中在构建系统健壮性和调试便利性，说明 Epic 在持续维护此 plugin
- **特殊说明**：此 plugin 是 Epic Games 在 `Fortnite` 等移动产品中使用的内部基础设施，因此不会出现在 Marketplace 上，DocsURL 也为空
- **是否推荐使用**：**推荐**。作为 UE5 官方维护的 Firebase 集成方案，比第三方插件更可靠。但注意功能范围仅限于推送通知，不包含 Firestore、Auth、Realtime Database 等 Firebase 服务

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Firebase)
- 官方文档：无（.uplugin 中 DocsURL 为空）
- 测试用例：无（未找到任何自动化测试）
