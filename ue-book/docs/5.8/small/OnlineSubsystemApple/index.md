# Online Subsystem Apple

> Access to Sign in with Apple platform

| 属性 | 值 |
|---|---|
| 中文名 | 苹果登录 |
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `OnlineSubsystemApple` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineSubsystemApple) | |

## 用途

此插件为虚幻引擎提供了 **“Sign in with Apple”** 功能的集成。它实现了一个在线子系统（`IOnlineSubsystem`），使得游戏能够在支持的苹果平台（iOS， macOS， tvOS）上使用苹果账号进行身份验证。其核心功能是封装苹果原生的登录API，并与虚幻的在线子系统框架对接，使玩家可以通过苹果账号登录游戏，并获取用户基本信息（如邮箱、姓名，需用户授权）。

## 使用场景

- 你正在开发一款面向苹果设备的游戏（iOS, macOS），并需要遵循苹果的指南提供“Sign in with Apple”登录选项。
- 你的游戏需要在多个苹果平台上提供统一的登录体验。
- 你需要一个标准化的接口来处理苹果用户的认证流程，包括获取认证令牌和用户属性。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Login` | 使用指定的本地用户编号和凭证进行登录。对于苹果登录，凭证参数通常可以留空或使用特定配置。 | `IOnlineIdentity` |
| `ShowLoginUI` | 调用苹果原生的“Sign in with Apple”登录UI。 | `IOnlineExternalUI` |
| `GetLoginStatus` | 查询指定本地用户编号或用户ID的当前登录状态。 | `IOnlineIdentity` |
| `GetUserAccount` | 获取已登录用户的账户信息对象。 | `IOnlineIdentity` |
| `GetUserAttribute` | 从用户账户对象中获取特定的属性值（如邮箱）。 | `FUserOnlineAccountApple` |

### 使用示例（蓝图描述）

1.  **获取子系统接口**：在需要登录的蓝图中，使用 `Get Online Subsystem` 节点，并指定子系统名称为 “APPLE” 或使用默认（根据平台配置），获取 `IOnlineSubsystem` 对象。
2.  **调用登录**：
    *   **方法A（自动调用UI）**：从 `IOnlineSubsystem` 获取 `ExternalUI` 接口，然后调用 `ShowLoginUI` 节点。苹果的原生登录界面会弹出。绑定 `OnLoginUIClosed` 委托来处理登录结果。
    *   **方法B（编程方式）**：从 `IOnlineSubsystem` 获取 `Identity` 接口，调用 `Login` 节点。这通常会触发后台认证流程。
3.  **处理结果**：在登录完成的委托回调中，检查返回的 `UniqueNetId` 和 `Error`。成功登录后，可以调用 `GetUserAccount` 和 `GetUserAttribute` 来获取用户信息。

## C++ 用法

### 头文件引入

```cpp
#include "OnlineSubsystem.h"
#include "OnlineSubsystemApple.h"
#include "OnlineIdentityInterface.h"
#include "OnlineExternalUIInterface.h"
```

### 基本用法

演示如何获取苹果在线子系统并进行登录。
```cpp
// (概念代码)
IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(APPLE_SUBSYSTEM);
if (OnlineSub)
{
    // 尝试通过身份接口登录
    IOnlineIdentityPtr IdentityInterface = OnlineSub->GetIdentityInterface();
    if (IdentityInterface.IsValid())
    {
        FOnlineAccountCredentials Credentials;
        // 对于苹果登录，有时需要配置特定字段或留空
        Credentials.Type = TEXT(“apple”);
        IdentityInterface->Login(0, Credentials);
    }
}
```

### 进阶用法

监听登录状态变更。
```cpp
// 获取身份接口后，绑定登录状态变更委托
IOnlineIdentityPtr IdentityInterface = OnlineSub->GetIdentityInterface();
if (IdentityInterface.IsValid())
{
    IdentityInterface->AddOnLoginStatusChangedDelegate_Handle(
        0, // LocalUserNum
        FOnLoginStatusChangedDelegate::CreateUObject(this, &UMyClass::OnLoginStatusChanged)
    );
}

// 委托回调函数
void UMyClass::OnLoginStatusChanged(int32 LocalUserNum, ELoginStatus::Type OldStatus, ELoginStatus::Type NewStatus, const FUniqueNetId& NewId)
{
    if (NewStatus == ELoginStatus::Type::LoggedIn)
    {
        // 登录成功，处理 NewId
        UE_LOG(LogOnline, Log, TEXT("Apple Login Succeeded for user: %s"), *NewId.ToString());
    }
}
```

## Demo 示例

以下是一个简单的 Actor，演示了苹果登录的基本流程。

```cpp
// MyAppleLoginActor.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "OnlineSubsystem.h"
#include "OnlineSubsystemApple.h"
#include "OnlineIdentityInterface.h"
#include "OnlineExternalUIInterface.h"
#include "MyAppleLoginActor.generated.h"

UCLASS()
class AMyAppleLoginActor : public AActor
{
    GENERATED_BODY()

public:
    AMyAppleLoginActor();

protected:
    virtual void BeginPlay() override;

    UFUNCTION(BlueprintCallable, Category = "Apple Login")
    void RequestAppleLogin();

private:
    void OnLoginStatusChanged(int32 LocalUserNum, ELoginStatus::Type OldStatus, ELoginStatus::Type NewStatus, const FUniqueNetId& NewId);

    FDelegateHandle LoginStatusDelegateHandle;
};
```

```cpp
// MyAppleLoginActor.cpp
#include "MyAppleLoginActor.h"
#include "Online.h"

AMyAppleLoginActor::AMyAppleLoginActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyAppleLoginActor::BeginPlay()
{
    Super::BeginPlay();

    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(APPLE_SUBSYSTEM);
    if (OnlineSub)
    {
        IOnlineIdentityPtr IdentityInterface = OnlineSub->GetIdentityInterface();
        if (IdentityInterface.IsValid())
        {
            // 监听登录状态
            LoginStatusDelegateHandle = IdentityInterface->AddOnLoginStatusChangedDelegate_Handle(
                0, // LocalUserNum
                FOnLoginStatusChangedDelegate::CreateUObject(this, &AMyAppleLoginActor::OnLoginStatusChanged)
            );
        }
    }
}

void AMyAppleLoginActor::RequestAppleLogin()
{
    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(APPLE_SUBSYSTEM);
    if (!OnlineSub) return;

    // 方式1： 弹出原生登录UI
    IOnlineExternalUIPtr ExternalUI = OnlineSub->GetExternalUIInterface();
    if (ExternalUI.IsValid())
    {
        ExternalUI->ShowLoginUI(0, true, false, FOnLoginUIClosedDelegate());
    }
    /* // 方式2： 编程登录
    IOnlineIdentityPtr IdentityInterface = OnlineSub->GetIdentityInterface();
    if (IdentityInterface.IsValid())
    {
        FOnlineAccountCredentials Credentials;
        Credentials.Type = TEXT("apple");
        IdentityInterface->Login(0, Credentials);
    }
    */
}

void AMyAppleLoginActor::OnLoginStatusChanged(int32 LocalUserNum, ELoginStatus::Type OldStatus, ELoginStatus::Type NewStatus, const FUniqueNetId& NewId)
{
    if (NewStatus == ELoginStatus::Type::LoggedIn)
    {
        UE_LOG(LogTemp, Log, TEXT("Apple Login Success! User: %s"), *NewId.ToString());
        // 此处可获取用户属性
        IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(APPLE_SUBSYSTEM);
        if (OnlineSub)
        {
            IOnlineIdentityPtr IdentityInterface = OnlineSub->GetIdentityInterface();
            if (IdentityInterface.IsValid())
            {
                TSharedPtr<FUserOnlineAccount> UserAccount = IdentityInterface->GetUserAccount(NewId);
                if (UserAccount.IsValid())
                {
                    FString Email;
                    UserAccount->GetUserAttribute(TEXT("email"), Email);
                    UE_LOG(LogTemp, Log, TEXT("User Email: %s"), *Email);
                }
            }
        }
    }
    else if (NewStatus == ELoginStatus::Type::NotLoggedIn)
    {
        UE_LOG(LogTemp, Warning, TEXT("Apple User Logged Out."));
    }
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。此插件是 `OnlineSubsystem` 框架的一个具体实现，依赖于引擎核心的 `OnlineSubsystem` 模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-01-27 | `113268fe` | Fixed include casing mismatch when compiling ios with case sensitive on | 修复在大小写敏感的iOS编译环境下，头文件包含路径大小写不匹配的问题。 |
| 2026-01-24 | `e793e61e` | Fixed more compile errors when using portable toolchain | 修复使用便携式工具链时出现的更多编译错误。 |
| 2026-01-14 | `1a097717` | Fix IOS CIS Issues. | 修复iOS持续集成(CIS)构建中出现的问题。 |
| 2023-11-17 | `b1ad5aee` | Add ShowResolveUI param to GetUserPrivilege method of identity interface. | 为身份接口的GetUserPrivilege方法添加了ShowResolveUI参数。 |
| 2023-06-24 | `82ea6a76` | [Backout] - CL26223564 | 回滚了之前的某个变更集(CLS)。 |

### 维护评价

该插件创建于2020年，近期（2026年初）仍有针对编译问题的修复提交，表明它仍在维护中，以确保在新版引擎和工具链下能正常编译运行。然而，其核心功能（苹果登录）相对稳定，过去几年的更新多为构建兼容性修复和小的接口调整，功能性新特性较少。**推荐使用**：如果你需要在苹果平台上集成登录功能，这是一个官方提供的、维护中的标准解决方案。请注意，由于其`EnabledByDefault`为`false`，你需要在项目设置中手动启用它，或在代码中配置正确的子系统名称。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineSubsystemApple)
- [官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/online-subsystem-apple-in-unreal-engine) (UE官方文档 - Online Subsystem Apple)