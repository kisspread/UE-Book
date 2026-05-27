# Firebase

> Support for remote notifications using Firebase（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | Firebase 通知 |
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `Firebase` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-09-25 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Firebase) | |

## 用途

该插件是一个轻量级的包装器，主要用于在 Android 和 iOS 移动平台上集成 Firebase Cloud Messaging (FCM) 功能，以实现远程推送通知。它处理了与平台原生 SDK 的对接、设备令牌的获取与管理，以及基本的 Firebase 配置初始化。插件本身不包含 Firebase 的完整功能，而是提供了最基础的通知接收和令牌管理接口，需要开发者自行集成其他 Firebase 服务（如 Analytics, Crashlytics 等）的原生 SDK。

## 使用场景

- 你需要在 Unreal Engine 开发的移动游戏或应用中，接收来自 Firebase 后台的推送通知。
- 你的项目仅需在 Android 或 iOS 平台上使用 Firebase 的云消息传递服务，且希望最小化代码改动和依赖。

## 蓝图用法

在当前提供的源码中，该插件的核心功能（如 `Initialize`, `GetFirebaseToken`）均未通过 `UFUNCTION(BlueprintCallable)` 暴露给蓝图，因此**不支持直接在蓝图中调用**。功能主要通过 C++ 模块接口提供。

## C++ 用法

### 头文件引入

```cpp
#include "Firebase.h"
```

### 基本用法

该插件的核心接口是 `IFirebaseModuleInterface`。你需要通过它来初始化 Firebase 并访问通知相关的功能。

```cpp
// 检查模块是否可用
if (IFirebaseModuleInterface::IsAvailable())
{
    // 获取模块实例
    IFirebaseModuleInterface& FirebaseModule = IFirebaseModuleInterface::Get();

    // 注册到令牌更新事件
    FirebaseModule.OnTokenUpdate.AddLambda([](const FString& Token, const FString& Error)
    {
        if (!Error.IsEmpty())
        {
            UE_LOG(LogFirebase, Error, TEXT("Token update error: %s"), *Error);
        }
        else
        {
            UE_LOG(LogFirebase, Log, TEXT("Received new Firebase token: %s"), *Token);
            // 在这里将新令牌发送到你的后端服务器
        }
    });
}
```

**来源**：`Source/Public/Firebase.h`

### 进阶用法（iOS 平台特定）

在 iOS 平台上，你需要先配置 Firebase 并处理 APNs 令牌。以下是结合 `FFirebaseIOSNotifications` 的典型用法：

```cpp
#if PLATFORM_IOS
    #include "IOS/notifications/EpicFirebaseIOSNotifications.h"
#endif

// ... 在应用启动后的某个时间点（例如，在游戏实例初始化之后）
#if PLATFORM_IOS
    // 1. 配置 Firebase (通常使用项目的 GoogleService-Info.plist)
    FFirebaseIOSNotifications::ConfigureFirebase();

    // 2. 初始化 Firebase 消息服务，设置令牌查询超时（纳秒）和是否启用分析
    FFirebaseIOSNotifications::Initialize(5000000000LL, true); // 5秒超时，启用分析

    // 3. 当系统接收到 APNs 令牌后，你还需要调用此方法将其传递给 Firebase
    // FFirebaseIOSNotifications::OnAPNSTokenReceived(APNSToken);
#endif
```

**来源**：`Source/IOS/notifications/EpicFirebaseIOSNotifications.h`

### 测试用例参考

测试代码位于 `Engine/Tests/FirebaseTests/` 目录。它演示了如何测试模块的加载和基本接口。

```cpp
// 来自 Engine/Tests/FirebaseTests/FirebaseTests.cpp
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFirebaseModuleTest, "System.Plugins.Firebase.ModuleLoad",
                                  EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FFirebaseModuleTest::RunTest(const FString& Parameters)
{
    // 检查模块是否在支持的平台上可用
    IFirebaseModuleInterface* FirebaseModule = FModuleManager::GetModulePtr<IFirebaseModuleInterface>("Firebase");

    // 在不支持的平台上（如 Windows），模块应该未加载
    if (!IsRunningPlatformSupportingFirebase())
    {
        TestNull(TEXT("Firebase module should not be loaded on unsupported platforms"), FirebaseModule);
    }
    else
    {
        // 在支持的平台上，检查模块接口是否正确
        TestNotNull(TEXT("Firebase module should be available"), FirebaseModule);
        if (FirebaseModule)
        {
            // 验证模块实现了正确的接口
            TestTrue(TEXT("Module should implement IFirebaseModuleInterface"), FirebaseModule->Implements<UFirebaseModuleInterface>());
        }
    }
    return true;
}
```

## Demo 示例

```cpp
// FirebaseDemoComponent.h
#pragma once
#include "Components/ActorComponent.h"
#include "Firebase.h"
#include "FirebaseDemoComponent.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class UFirebaseDemoComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    FDelegateHandle TokenUpdateDelegateHandle;
    void HandleTokenUpdate(const FString& Token, const FString& Error);
};
```

```cpp
// FirebaseDemoComponent.cpp
#include "FirebaseDemoComponent.h"

void UFirebaseDemoComponent::BeginPlay()
{
    Super::BeginPlay();

    if (IFirebaseModuleInterface::IsAvailable())
    {
        auto& Firebase = IFirebaseModuleInterface::Get();
        TokenUpdateDelegateHandle = Firebase.OnTokenUpdate.AddUObject(this, &UFirebaseDemoComponent::HandleTokenUpdate);
        UE_LOG(LogTemp, Log, TEXT("Firebase module is available and listener registered."));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Firebase module is not available on this platform."));
    }
}

void UFirebaseDemoComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (IFirebaseModuleInterface::IsAvailable())
    {
        IFirebaseModuleInterface::Get().OnTokenUpdate.Remove(TokenUpdateDelegateHandle);
    }
    Super::EndPlay(EndPlayReason);
}

void UFirebaseDemoComponent::HandleTokenUpdate(const FString& Token, const FString& Error)
{
    if (Error.IsEmpty())
    {
        UE_LOG(LogTemp, Log, TEXT("FCM Token Updated: %s"), *Token);
        // 在这里将 Token 发送到你的服务器
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("FCM Token Error: %s"), *Error);
    }
}
```

## 模块依赖

从 `Source/Firebase.Build.cs` 分析，使用此插件需要你的项目模块依赖以下特定模块：

| 模块 | 用途 |
|---|---|
| `Launch` | 提供引擎启动和平台层基础功能，对于访问平台原生 API 是必需的。 |
| `Swift` | 用于支持 Firebase iOS SDK 中可能存在的 Swift 代码和互操作性。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移至 UE_LOGF 格式。 |
| 2026-01-27 | `a18eb61a` | [IOS] Setting the requires platform sdk flag in multiple modules that depends on them. | 为依赖平台 SDK 的多个模块设置所需标志。 |
| 2025-10-30 | `10e425ab` | IWYU unity compilation | 修复 IWYU（Include What You Use）和统一编译相关问题。 |
| 2025-10-21 | `c8971d1e` | iOS non unity build fix | 修复 iOS 平台非统一构建的编译错误。 |
| 2025-10-21 | `3dc7757e` | Added missing Firebase iOS integration check | 增加缺失的 Firebase iOS 集成检查。 |

### 维护评价

- **创建时间**：插件始于 2018 年，已有约 8 年历史。
- **维护状态**：**仍在维护中**。最近的提交记录（2026年）主要是针对引擎版本更新（如 IWYU、平台 SDK 依赖）的编译兼容性修复，而非功能性新增。这表明它仍在跟随引擎主线进行维护，但自身功能稳定，没有新特性。
- **已知限制**：
    1.  **功能基础**：插件仅提供最基础的令牌管理和事件分发，不包含完整的 Firebase 服务封装。
    2.  **无蓝图支持**：所有功能必须通过 C++ 调用。
    3.  **平台限制**：仅支持 Android 和 iOS，编辑器下无效。
    4.  **默认禁用**：需要在项目设置中手动启用。
- **推荐度**：如果你的项目**仅需要**在移动端接收 FCM 推送通知，并且愿意自行处理 Firebase SDK 的集成和配置，此插件可以作为一个有用的起点。但对于需要更完整 Firebase 服务（如数据库、分析、崩溃报告等）的项目，可能需要寻找或封装更全面的解决方案。鉴于其年龄和基础性，建议在使用前仔细评估其接口是否满足需求。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Firebase)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/FirebaseTests)