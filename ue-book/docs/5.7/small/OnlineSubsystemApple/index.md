# Online Subsystem Apple

> Access to Sign in with Apple platform

| 属性 | 值 |
|---|---|
| 分类 | Online Platform |
| 默认启用 | false |
| 包含内容 | false |
| 模块 | OnlineSubsystemApple (Runtime) |
| 支持平台 | Mac, iOS, tvOS |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineSubsystemApple) | |

## 用途

OnlineSubsystemApple 是 UE5 的 **Sign in with Apple** 认证集成插件。它通过 Apple 的 `AuthenticationServices` 框架，在 iOS/tvOS/Mac 平台上为玩家提供 Apple ID 登录能力。

这个插件的定位非常聚焦——它**只实现了两个接口**：Identity（身份认证）和 ExternalUI（登录弹窗）。其余所有 OnlineSubsystem 接口（Session、Friends、Leaderboards 等）均返回 `nullptr`。这意味着它不是一个完整的在线子系统，而是一个纯粹的 **Apple 登录适配层**，通常与其他在线子系统（如 OnlineSubsystemIOS 的 Game Center）配合使用。

插件在运行时注册为 `APPLE_SUBSYSTEM`，子系统名称为 `"Game Center"`（这可能是历史遗留命名，实际功能是 Sign in with Apple）。

## 使用场景

- 你的游戏需要支持 Apple ID 登录（iOS App Store 要求部分应用支持 Sign in with Apple）
- 你需要一个跨 Apple 平台（iOS/tvOS/Mac）的统一登录入口
- 你想获取用户授权的邮箱和姓名信息
- 你想在已有的在线子系统基础上叠加 Apple 身份认证

**不适用的场景：**
- 需要 Game Center 成就/排行榜/好友等功能 → 使用 OnlineSubsystemIOS
- 需要完整的多人在线功能 → 需配合其他在线子系统

## 蓝图用法

本插件**没有暴露任何 BlueprintCallable 节点**。所有功能均为 C++ 层面的 OnlineSubsystem 接口调用。身份认证和登录 UI 的触发通过 `IOnlineIdentity` 和 `IOnlineExternalUI` 接口完成。

## C++ 用法

### 前置配置

**1. 启用插件**（默认不启用）

在 `DefaultEngine.ini` 中添加：

```ini
[OnlineSubsystem]
DefaultPlatformService=Apple

[OnlineSubsystemApple]
bEnabled=true
```

**2. iOS 平台需启用 Sign in with Apple 支持**

在 iOS 项目的 `DefaultEngine.ini` 中设置：

```ini
[/Script/IOSRuntimeSettings.IOSRuntimeSettings]
bEnableSignInWithAppleSupport=True
```

这会触发 `Build.cs` 中的条件编译宏 `ONLINESUBSYSTEMAPPLE_IDENTITY_ENABLE_SIWA=1`，并链接 `AuthenticationServices` 框架。

**3. 配置权限范围（Scope Fields）**

在 `DefaultEngine.ini` 中配置请求的用户信息范围：

```ini
[OnlineSubsystemApple.OnlineIdentityApple]
+ScopeFields=email
+ScopeFields=fullName
```

可选值：
- `email` — 请求用户邮箱
- `fullName` — 请求用户姓名

> ⚠️ 注意：邮箱和姓名仅在**首次登录授权时**可获取。一旦用户授权后再次登录，Apple 不再提供这些信息。

### 头文件引入

```cpp
#include "OnlineSubsystem.h"
#include "OnlineSubsystemApple.h"
#include "Interfaces/OnlineIdentityInterface.h"
#include "OnlineSubsystemAppleAttributes.h"
```

### 基本用法 — 登录

获取 Identity 接口并触发登录：

```cpp
// 获取在线子系统
IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(APPLE_SUBSYSTEM);
if (OnlineSub)
{
    // 获取身份接口
    IOnlineIdentityPtr IdentityInterface = OnlineSub->GetIdentityInterface();
    if (IdentityInterface.IsValid())
    {
        // 绑定登录完成回调
        IdentityInterface->AddOnLoginCompleteDelegate_Handle(
            0,  // LocalUserNum
            FOnLoginCompleteDelegate::CreateLambda([](int32 LocalUserNum, bool bWasSuccessful, const FUniqueNetId& UserId, const FString& Error)
            {
                if (bWasSuccessful)
                {
                    UE_LOG(LogTemp, Display, TEXT("Apple login succeeded: %s"), *UserId.ToString());
                }
                else
                {
                    UE_LOG(LogTemp, Warning, TEXT("Apple login failed: %s"), *Error);
                }
            })
        );

        // 触发登录（无已保存凭据时会弹出 Sign in with Apple UI）
        IdentityInterface->Login(0, FOnlineAccountCredentials());
    }
}
```

### 基本用法 — 使用已保存凭据登录

如果已保存用户的 Apple User ID，可以尝试静默验证：

```cpp
FOnlineAccountCredentials Credentials;
Credentials.Id = TEXT("保存的AppleUserID");  // 之前的登录获取的 User ID

IdentityInterface->Login(0, Credentials);
```

此时插件会调用 `ASAuthorizationAppleIDProvider.getCredentialStateForUserID:` 验证凭据是否仍有效，不会弹出 UI。

### 进阶用法 — 获取用户信息

登录成功后，可以从用户账户中提取信息：

```cpp
IOnlineIdentityPtr IdentityInterface = OnlineSub->GetIdentityInterface();
FUniqueNetIdPtr UserId = IdentityInterface->GetUniquePlayerId(0);

if (UserId.IsValid())
{
    TSharedPtr<FUserOnlineAccount> UserAccount = IdentityInterface->GetUserAccount(*UserId);
    if (UserAccount.IsValid())
    {
        // 获取 Apple User ID
        FString AppleUserId = UserAccount->GetUserId()->ToString();

        // 获取授权 Token（identity token）
        FString AuthToken = UserAccount->GetAccessToken();

        // 获取用户属性（仅首次登录可用）
        FString Email, FirstName, LastName;
        UserAccount->GetUserAttribute(TEXT("email"), Email);
        UserAccount->GetUserAttribute(TEXT("firstName"), FirstName);
        UserAccount->GetUserAttribute(TEXT("lastName"), LastName);

        // 获取显示名称（从 NSPersonNameComponents 格式化）
        FString DisplayName = UserAccount->GetDisplayName();
    }
}
```

### 进阶用法 — 登出

```cpp
IdentityInterface->AddOnLogoutCompleteDelegate_Handle(
    0,
    FOnLogoutCompleteDelegate::CreateLambda([](int32 LocalUserNum, bool bWasSuccessful)
    {
        UE_LOG(LogTemp, Display, TEXT("Apple logout: %s"), bWasSuccessful ? TEXT("success") : TEXT("failed"));
    })
);

IdentityInterface->Logout(0);
```

## Demo 示例

### 最小登录示例

```cpp
// AppleLoginDemo.h
#pragma once

#include "CoreMinimal.h"
#include "OnlineSubsystem.h"
#include "OnlineSubsystemApple.h"
#include "OnlineSubsystemAppleAttributes.h"
#include "Interfaces/OnlineIdentityInterface.h"

class FAppleLoginDemo
{
public:
    void DoLogin()
    {
        IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(APPLE_SUBSYSTEM);
        if (!OnlineSub)
        {
            UE_LOG(LogTemp, Error, TEXT("OnlineSubsystemApple not available"));
            return;
        }

        IOnlineIdentityPtr Identity = OnlineSub->GetIdentityInterface();
        if (!Identity.IsValid()) return;

        // 绑定回调
        Identity->AddOnLoginCompleteDelegate_Handle(0,
            FOnLoginCompleteDelegate::CreateRaw(this, &FAppleLoginDemo::OnLoginComplete));

        // 启动登录
        Identity->Login(0, FOnlineAccountCredentials());
    }

private:
    void OnLoginComplete(int32 LocalUserNum, bool bWasSuccessful,
                         const FUniqueNetId& UserId, const FString& Error)
    {
        if (bWasSuccessful)
        {
            UE_LOG(LogTemp, Display, TEXT("Logged in as: %s"), *UserId.ToString());

            // 读取用户信息
            IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(APPLE_SUBSYSTEM);
            IOnlineIdentityPtr Identity = OnlineSub->GetIdentityInterface();
            auto Account = Identity->GetUserAccount(UserId);
            if (Account.IsValid())
            {
                FString Email;
                Account->GetUserAttribute(TEXT("email"), Email);
                UE_LOG(LogTemp, Display, TEXT("Email: %s"), *Email);
            }
        }
    }
};
```

### Build.cs 依赖

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "OnlineSubsystem",
    "OnlineSubsystemApple",
});
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `OnlineSubsystem` | 在线子系统基础框架 |

运行时还会链接 Apple 的 `AuthenticationServices.framework`（弱链接，仅在启用 SIWA 时）。

## 维护状态

### 近期更新

| 日期 | Hash | 说明 |
|---|---|---|
| 2023-11-16 | `b1ad5aee` | `GetUserPrivilege` 方法添加 `ShowResolveUI` 参数 — 跟随 Identity 接口签名变更 |
| 2023-06-24 | `82ea6a76` | 回退 VisionOS 早期支持（构建问题） — 尝试将 Build.cs 平台检查改为 `UnrealPlatformGroup.Apple` |
| 2023-06-23 | `1fd1a774` | 回退 VisionOS 相关改动 — 同上，因 CIS 构建失败而回退 |

### 维护评价

- **创建时间**：2020 年 9 月，已有约 5.6 年历史
- **最近更新**：最后一次实质性更新是 2023 年 11 月，超过 2 年未有功能性改动
- **功能范围**：仅实现 Identity 和 ExternalUI 两个接口，功能非常有限
- **代码质量**：存在 TODO 注释（Mac 窗口支持未完成）、debug 代码被注释而非删除
- **Mac 支持**：不完整。`presentationAnchorForAuthorizationController:` 在 Mac 上返回 `nullptr`，Sign in with Apple 在 Mac 上实际无法使用
- **已知限制**：
  - `RevokeAuthToken` 未实现（打印日志后返回错误）
  - 大量接口返回 `nullptr`（Session、Friends、Leaderboards 等）
  - Mac 平台的 presentation anchor 未完成
  - VisionOS 支持已回退
- **维护评价**：⚠️ **维护不活跃**。最后的功能性更新（非构建修复）可以追溯到更早。考虑到 Apple 持续更新 Sign in with Apple API，此插件可能无法兼容最新的 Apple 认证特性。

**推荐**：如果你只需要基本的 Sign in with Apple 登录功能，此插件可以作为起点。但需要注意 Mac 平台不完整、功能有限，且可能需要自行维护以跟上 Apple API 的变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineSubsystemApple)
- [Apple Sign in with Apple 文档](https://developer.apple.com/documentation/authenticationservices)
