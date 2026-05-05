# Online Subsystem Google

> Access to Google platform

| 属性 | 值 |
|---|---|
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `OnlineSubsystemGoogle` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2017-03-28 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineSubsystemGoogle) | |

## 用途

OnlineSubsystemGoogle 是 UE5 Online Subsystem 框架下对 **Google 账号认证服务**的集成实现。它不是 Google Play Games Services 的完整封装（没有排行榜、成就、多人游戏等），而是专注于一件事：**通过 Google OAuth 2.0 完成用户身份认证**。

插件实现了 `IOnlineIdentity` 和 `IOnlineExternalUI` 两个接口，其余所有接口（Session、Friends、Leaderboards、Voice 等）均返回 `nullptr`。这意味着它的核心价值是：让你的 UE5 游戏能用 Google 账号登录，获取用户的 access token、用户资料（姓名、邮箱、头像等），然后用这些信息与你自己的后端服务进行身份验证。

插件根据目标平台采用三种不同的底层实现：
- **Android**：通过 `androidx.credentials.CredentialManager`（新的 Android Credential Manager API）调用 Google Sign-In
- **iOS**：通过嵌入的 GoogleSignIn SDK（ObjC `FGoogleHelper`）调用原生 Google Sign-In
- **Windows / Mac / Linux**：通过纯 HTTP REST 方式走 OAuth 2.0 Authorization Code 流程（在浏览器中打开 Google 登录页，捕获 redirect 回调的授权码，再用 HTTP 请求交换 token）

## 使用场景

- 你的游戏需要 Google 账号登录功能 → 使用此插件配合 OnlineSubsystem 框架
- 你需要获取 Google ID Token 来向自己的后端服务器证明用户身份 → 此插件会解析 JWT 并提供 ID Token
- 你已经在使用其他 Online Subsystem（如 EOS、Steam）但仍需 Google 登录作为辅助认证方式 → 可以将此插件作为独立的子系统实例使用
- 你只在移动端（Android/iOS）需要 Google 登录 → 原生 SDK 集成开箱即用
- 你在桌面端也需要 Google 登录 → REST 实现通过浏览器 OAuth 流程完成（需要配置 ClientId 和 ClientSecret）

**不需要此插件的场景**：如果你使用 Google Play Games Services 的排行榜、成就、多人游戏等功能，此插件不能满足需求，你需要使用专门的 Google Play Games 插件。

## 配置

### DefaultEngine.ini 基本配置

```ini
[OnlineSubsystemGoogle]
bEnabled=true
ClientId=你的GoogleClientId.apps.googleusercontent.com

[OnlineSubsystemGoogle.OnlineIdentityGoogle]
bRequestOfflineAccess=true
```

### 各平台配置差异

| 配置项 | Android | iOS | Windows/Mac/Linux (REST) |
|---|---|---|---|
| `ClientId` | 不需要（由 ServerClientId 决定） | 需要（写入 Info.plist `GIDClientID`） | 需要（OAuth Client ID） |
| `ServerClientId` | 必需（OAuth 2.0 Web Client ID） | 可选（bRequestOfflineAccess 时写入 `GIDServerClientID`） | 不需要 |
| `bRequestOfflineAccess` | ✅ | ✅ | ✅（控制是否请求 refresh token） |
| `ClientSecret` | 不需要 | 不需要 | 需要（REST token 交换用） |
| `ReversedClientId` | 不需要 | 需要（写入 `CFBundleURLSchemes`，用于 OAuth 回调） | 不需要 |

### iOS 特殊配置

iOS 平台需要在 `[OnlineSubsystemGoogle.OnlineIdentityGoogle]` 中配置 `ReversedClientId`（Google Client ID 的反转版本），该值会自动写入 Info.plist 的 `CFBundleURLSchemes`，用于处理 Google Sign-In 的 URL 回调。

### REST 平台的 Redirect 配置

桌面端 REST 实现默认监听 `http://localhost:9000` 作为 OAuth 回调地址。`LoginRedirectUrl` 需要在 ini 中配置。

## 蓝图用法

此插件没有暴露任何 `BlueprintCallable` 或 `BlueprintReadWrite` 接口。所有操作通过标准的 Online Subsystem 接口进行，蓝图中通过 `Get Identity Interface` 和 `Get External UI Interface` 节点访问。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Identity Interface` | 获取 Google 身份认证接口 | 通过 `IOnlineSubsystem` 访问 |
| `Login` | 发起 Google 登录 | `IOnlineIdentity` |
| `Logout` | 登出当前 Google 账号 | `IOnlineIdentity` |
| `Get Login Status` | 查询登录状态 | `IOnlineIdentity` |
| `Get Player Nickname` | 获取用户真实姓名 | `IOnlineIdentity` |
| `Get Auth Token` | 获取 Google Access Token | `IOnlineIdentity` |
| `Get Unique Player Id` | 获取 Google 用户唯一 ID | `IOnlineIdentity` |
| `Show Login UI` | 显示 Google 登录界面 | `IOnlineExternalUI` |

### 使用示例（蓝图描述）

1. 在蓝图中使用 `Get Subsystem` 节点，传入 `Online Subsystem Google` 作为子系统名称
2. 从返回的子系统对象调用 `Get Identity Interface`
3. 调用 `Login`，`Local User Num` 设为 0，`Account Credentials` 留空（各平台会自行处理认证流程）
4. 监听 `On Login Complete` 委托，获取登录结果
5. 登录成功后，使用 `Get Auth Token` 获取 Google Access Token，或使用 `Get Unique Player Id` 获取用户 ID

## C++ 用法

### 头文件引入

```cpp
#include "OnlineSubsystem.h"
#include "OnlineIdentityInterface.h"
#include "OnlineSubsystemGoogle.h"
```

### 基本用法

获取 Google 子系统并执行登录（来源：`OnlineSubsystemGoogleCommon.cpp`、`OnlineIdentityGoogleCommon.cpp`）：

```cpp
// 获取 Google Online Subsystem
IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(FName(TEXT("GOOGLE")));
if (OnlineSub)
{
    // 获取身份接口
    IOnlineIdentityPtr IdentityInterface = OnlineSub->GetIdentityInterface();
    if (IdentityInterface.IsValid())
    {
        // 绑定登录完成回调
        IdentityInterface->AddOnLoginCompleteDelegate_Handle(
            0,  // LocalUserNum
            FOnLoginCompleteDelegate::CreateLambda(
                [](int32 LocalUserNum, bool bWasSuccessful, const FUniqueNetId& UserId, const FString& Error)
                {
                    if (bWasSuccessful)
                    {
                        UE_LOG(LogTemp, Log, TEXT("Google login succeeded! UserId: %s"), *UserId.ToString());
                    }
                    else
                    {
                        UE_LOG(LogTemp, Error, TEXT("Google login failed: %s"), *Error);
                    }
                })
        );

        // 发起登录（各平台会自行处理认证 UI）
        FOnlineAccountCredentials Credentials;
        IdentityInterface->Login(0, Credentials);
    }
}
```

登录成功后获取用户信息：

```cpp
// 获取用户账号信息
FUniqueNetIdPtr UserId = IdentityInterface->GetUniquePlayerId(0);
if (UserId.IsValid())
{
    // 获取 Access Token
    FString AccessToken = IdentityInterface->GetAuthToken(0);
    
    // 获取用户昵称（真实姓名）
    FString Nickname = IdentityInterface->GetPlayerNickname(0);
    
    // 获取完整用户账号对象
    TSharedPtr<FUserOnlineAccount> UserAccount = IdentityInterface->GetUserAccount(*UserId);
    if (UserAccount.IsValid())
    {
        // 获取用户属性（如 email、picture 等）
        FString Email;
        UserAccount->GetUserAttribute(TEXT("email"), Email);
        
        FString Picture;
        UserAccount->GetUserAttribute(TEXT("picture"), Picture);
    }
}
```

### 进阶用法

使用 `FGoogleConfigurationDelegate` 在初始化时动态覆盖配置（来源：`OnlineSubsystemGoogleCommon.cpp`）：

```cpp
// 在子系统初始化前绑定配置委托，动态覆盖 ClientId
FOnlineSubsystemGoogleCommon::GetConfigurationDelegate().BindLambda(
    [](const FString& ConfigOverride, FGoogleAuthConfig& OutConfig)
    {
        // 可以设置 Backend 名称来从不同的 ini section 读取配置
        OutConfig.Backend = TEXT("MyBackend");
        
        // 对应 [OnlineSubsystemGoogle MyBackend] section
        // 可以在其中定义不同的 ClientId
    }
);
```

手动使用带 Token 的登录（来源：`Rest/OnlineIdentityGoogleRest.h`、`IOS/OnlineIdentityGoogle.h`）：

```cpp
// 如果你已经有一个 exchange token 或 refresh token，可以直接用它登录
// 这在 REST 桌面端和 iOS 端都可用
IOnlineIdentityPtr IdentityInterface = OnlineSub->GetIdentityInterface();

// 使用已有的 access token 登录
FAuthTokenGoogle ExistingToken;
ExistingToken.AccessToken = TEXT("your_existing_token");
ExistingToken.AuthType = EGoogleAuthTokenType::AccessToken;

// 注意：这需要通过平台特定的 Login 重载来使用
// REST 实现: FOnlineIdentityGoogle::Login(LocalUserNum, FAuthTokenGoogle, Delegate)
// iOS 实现: FOnlineIdentityGoogle::Login(LocalUserNum, FAuthTokenGoogle, Delegate)
```

## 架构概览

### 平台实现分层

```
FOnlineSubsystemGoogleCommon          ← 公共基类，管理接口引用和配置
    ├── FOnlineSubsystemGoogle (Android)   ← bPlatformRequiresClientId=false, 需要 ServerClientId
    ├── FOnlineSubsystemGoogle (iOS)       ← 需要 ClientId，使用 GoogleSignIn SDK
    └── FOnlineSubsystemGoogle (Rest)      ← 需要 ClientId，使用浏览器 OAuth 流程
```

### 认证流程

**Android**：
1. 调用 `FGoogleLoginWrapper` → JNI → Java `GoogleLogin.java`
2. Java 层使用 `androidx.credentials.CredentialManager` + `GetGoogleIdOption` 发起认证
3. 获取 ID Token 后，通过 `Identity.getAuthorizationClient().authorize()` 请求 scope 授权
4. 结果通过 JNI native 回调返回 C++ 层
5. C++ 层解析 ID Token (JWT)，创建用户账号

**iOS**：
1. 调用 `FGoogleHelper`（ObjC 类）→ GoogleSignIn SDK
2. SDK 提供 Access Token / Refresh Token / ID Token
3. C++ 层解析 token，请求用户 profile（HTTP GET to Google UserInfo endpoint）
4. 创建用户账号

**Windows / Mac / Linux (REST)**：
1. 先请求 Google Discovery Document 获取端点信息
2. 在浏览器中打开 Google OAuth 授权页面
3. 用户授权后，浏览器 redirect 到本地 HTTP server（localhost:9000）
4. 捕获授权码，通过 HTTP POST 交换 Access Token / Refresh Token
5. 使用 Access Token 请求 UserInfo endpoint 获取用户资料
6. 创建用户账号

### 关键类型

| 类 | 说明 |
|---|---|
| `FOnlineSubsystemGoogleCommon` | 子系统基类，管理 Identity 和 ExternalUI 接口 |
| `FOnlineIdentityGoogleCommon` | 身份认证公共实现，包含 JWT 解析、profile 请求、discovery 请求 |
| `FOnlineExternalUIGoogleCommon` | External UI 公共实现 |
| `FUserOnlineAccountGoogleCommon` | 用户账号信息，包含姓名、token、自定义属性 |
| `FAuthTokenGoogle` | Google OAuth token 封装（Access/Refresh/Exchange Token） |
| `FJsonWebTokenGoogle` | Google ID Token (JWT) 解析器 |
| `FGoogleOpenIDConfiguration` | Google OpenID Connect 发现文档配置 |
| `FGoogleAuthConfig` | 认证配置覆盖 |
| `FUniqueNetIdGoogle` | Google 用户唯一 ID（基于字符串） |

### 实现的接口

| 接口 | 实现状态 |
|---|---|
| `IOnlineIdentity` | ✅ 完整实现（Login/Logout/GetAuthToken/GetLoginStatus 等） |
| `IOnlineExternalUI` | ✅ 部分实现（ShowLoginUI 已实现，其他返回 false） |
| `IOnlineSession` | ❌ 返回 nullptr |
| `IOnlineFriends` | ❌ 返回 nullptr |
| `IOnlineLeaderboards` | ❌ 返回 nullptr |
| `IOnlineAchievements` | ❌ 返回 nullptr |
| `IOnlineVoice` | ❌ 返回 nullptr |
| `IOnlineStoreV2` | ❌ 返回 nullptr |
| 其他所有接口 | ❌ 返回 nullptr |

### 已知限制

- `RevokeAuthToken` 未实现，调用后会返回错误
- `ShowAccountCreationUI` 未实现（NYI - Not Yet Implemented）
- REST 实现中 JWT 签名验证代码被 `#if 0` 禁用（不验证签名，只验证 issuer、audience、expiry）
- `ShowFriendsUI`、`ShowInviteUI`、`ShowAchievementsUI` 等 External UI 方法全部返回 false
- `AutoLogin` 固定返回 false，不支持自动登录

## Demo 示例

### 最小登录示例

**Build.cs 依赖**：
```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
    "Engine",
    "OnlineSubsystem",
    "OnlineSubsystemUtils"
});
```

注意：不需要直接依赖 `OnlineSubsystemGoogle` 模块。通过 `IOnlineSubsystem::Get(TEXT("GOOGLE"))` 动态获取即可。

**GoogleLoginDemo.h**：
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "OnlineSubsystem.h"
#include "OnlineIdentityInterface.h"
#include "GoogleLoginDemo.generated.h"

UCLASS()
class AGoogleLoginDemo : public AActor
{
    GENERATED_BODY()

public:
    AGoogleLoginDemo();

    UFUNCTION(BlueprintCallable, Category = "Google Login")
    void LoginWithGoogle();

    UFUNCTION(BlueprintCallable, Category = "Google Login")
    void LogoutGoogle();

    UFUNCTION(BlueprintCallable, Category = "Google Login")
    FString GetGoogleAccessToken() const;

    UFUNCTION(BlueprintCallable, Category = "Google Login")
    FString GetGoogleUserName() const;

private:
    void OnLoginComplete(int32 LocalUserNum, bool bWasSuccessful, 
                         const FUniqueNetId& UserId, const FString& Error);
};
```

**GoogleLoginDemo.cpp**：
```cpp
#include "GoogleLoginDemo.h"
#include "OnlineSubsystem.h"
#include "OnlineIdentityInterface.h"

AGoogleLoginDemo::AGoogleLoginDemo()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AGoogleLoginDemo::LoginWithGoogle()
{
    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(FName(TEXT("GOOGLE")));
    if (!OnlineSub)
    {
        UE_LOG(LogTemp, Error, TEXT("Google Online Subsystem not available"));
        return;
    }

    IOnlineIdentityPtr Identity = OnlineSub->GetIdentityInterface();
    if (!Identity.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Identity interface not available"));
        return;
    }

    // 绑定回调
    Identity->ClearOnLoginCompleteDelegates(0, this);
    Identity->AddOnLoginCompleteDelegate_Handle(
        0,
        FOnLoginCompleteDelegate::CreateUObject(this, &AGoogleLoginDemo::OnLoginComplete)
    );

    // 发起登录（空 credentials，各平台自行处理）
    FOnlineAccountCredentials Credentials;
    Identity->Login(0, Credentials);
    
    UE_LOG(LogTemp, Log, TEXT("Google login initiated..."));
}

void AGoogleLoginDemo::LogoutGoogle()
{
    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(FName(TEXT("GOOGLE")));
    if (OnlineSub)
    {
        IOnlineIdentityPtr Identity = OnlineSub->GetIdentityInterface();
        if (Identity.IsValid())
        {
            Identity->Logout(0);
            UE_LOG(LogTemp, Log, TEXT("Google logout completed"));
        }
    }
}

FString AGoogleLoginDemo::GetGoogleAccessToken() const
{
    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(FName(TEXT("GOOGLE")));
    if (OnlineSub)
    {
        IOnlineIdentityPtr Identity = OnlineSub->GetIdentityInterface();
        if (Identity.IsValid())
        {
            return Identity->GetAuthToken(0);
        }
    }
    return FString();
}

FString AGoogleLoginDemo::GetGoogleUserName() const
{
    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(FName(TEXT("GOOGLE")));
    if (OnlineSub)
    {
        IOnlineIdentityPtr Identity = OnlineSub->GetIdentityInterface();
        if (Identity.IsValid())
        {
            return Identity->GetPlayerNickname(0);
        }
    }
    return FString();
}

void AGoogleLoginDemo::OnLoginComplete(int32 LocalUserNum, bool bWasSuccessful, 
                                        const FUniqueNetId& UserId, const FString& Error)
{
    if (bWasSuccessful)
    {
        UE_LOG(LogTemp, Log, TEXT("Google login succeeded! UserId: %s, Name: %s, Token: %s"),
            *UserId.ToString(),
            *GetGoogleUserName(),
            *GetGoogleAccessToken().Left(20) + TEXT("..."));
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Google login failed: %s"), *Error);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `CoreOnline` | 在线子系统核心类型（FUniqueNetId 等） |
| `ApplicationCore` | 平台应用层抽象 |
| `HTTP` | HTTP 请求（用于 Google API 通信、REST 实现） |
| `Json` | JSON 序列化/反序列化（解析 Google API 响应、JWT token） |
| `OnlineSubsystem` | Online Subsystem 框架基类和接口定义 |
| `Launch` | Android 平台专用（JNI 集成） |

### 平台特定依赖

**iOS**：
- 系统 Framework：CoreGraphics、CoreText、Foundation、LocalAuthentication、SafariServices、Security
- Weak Framework：AuthenticationServices
- 嵌入 Framework：GoogleSignIn、AppAuth、GTMAppAuth、GTMSessionFetcher

**Android**：
- Gradle 依赖：`androidx.credentials:credentials:1.2.2`、`androidx.credentials:credentials-play-services-auth:1.2.2`、`com.google.android.libraries.identity.googleid:googleid:1.1.0`
- Java 源码：`com.epicgames.unreal.GoogleLogin`

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-09-02 | `5a48f72f` | Registered JNI functions. Made JNI classes for Java classes. Added thread_local Ue::Jni::Env global. Various JNI bug fixes and cleanup | JNI 系统重构：注册了 JNI 函数，为 Java 类创建了 JNI 类包装，引入了 thread_local 的 JNI Env 全局变量。这是 Android 平台 JNI 调用方式的现代化改造 |
| 2025-08-13 | `65515472` | Deprecate OnlineJsonSerializer.h | 废弃旧的 OnlineJsonSerializer 头文件，迁移到标准的 Json 序列化方式 |
| 2025-07-18 | `55499a78` | Fix compile failure due to recent iOS rotation code changes | 修复 iOS 平台因旋转代码改动导致的编译失败 |

### 维护评价

- **创建时间**：2017 年 3 月，已有约 9 年历史
- **最近更新**：2025 年 9 月有实质性更新（JNI 重构），说明仍在活跃维护
- **维护频率**：近 3 个月有 3 次提交，频率适中
- **重要变化**：Android 端从旧的 Google Sign-In SDK 迁移到了新的 `androidx.credentials.CredentialManager` API（从 `GoogleLogin.java` 代码可以看到使用了 `GetGoogleIdOption` 和 `CredentialManager`），这是 Google 推荐的新一代认证方式
- **平台覆盖**：支持 Android、iOS、Windows、Mac、Linux 六个平台
- **功能范围**：仅实现 Identity 和 ExternalUI，功能范围有限但专注
- **已知问题**：JWT 签名验证未启用；`RevokeAuthToken` 未实现

**综合评价**：插件仍在活跃维护中，Android 端已迁移到最新的 Credential Manager API。虽然功能范围仅限于身份认证，但对于需要 Google 登录的项目来说是一个可靠的选择。推荐使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineSubsystemGoogle)
- [官方文档](https://docs.unrealengine.com/en-US/OnlineSubsystems/Google/)(无专门文档页面)
- [Google OpenID Connect Discovery](https://accounts.google.com/.well-known/openid-configuration)
- [Google OAuth 2.0 文档](https://developers.google.com/identity/protocols/oauth2)
- [Android Credential Manager](https://developer.android.com/training/sign-in/credential-manager)
- [GoogleSignIn SDK (iOS)](https://developers.google.com/identity/sign-in/ios/start)
