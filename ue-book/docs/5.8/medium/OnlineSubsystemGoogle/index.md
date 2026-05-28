# Online Subsystem Google

> Access to Google platform

| 属性 | 值 |
|---|---|
| 中文名 | 谷歌在线子系统 |
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `OnlineSubsystemGoogle` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2017-03-28 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineSubsystemGoogle) | |

## 用途

这个插件实现了 Google 平台的在线服务子系统（Online Subsystem），为 UE5 项目提供 **Google 登录认证**和 **Google 用户身份管理** 能力。

具体来说，它解决了以下问题：
- **Google OAuth2 登录流程**：处理完整的 Google 授权流程（发现服务 → 用户同意页面 → 令牌交换 → 获取用户资料）
- **跨平台 Google 认证**：在 Android、iOS、Windows/Mac/Linux 上以不同方式实现 Google 登录（Android 使用 JNI 调用原生 SDK，iOS 使用 GoogleSignIn SDK，桌面平台使用 REST API + 浏览器重定向）
- **令牌生命周期管理**：管理 Access Token、Refresh Token、Exchange Token 的获取、刷新和过期检测
- **JWT 令牌解析**：解析 Google 返回的 ID Token（JWT 格式），提取用户信息

该插件**默认不启用**（`EnabledByDefault: false`），需要在项目配置中手动启用。大多数标准在线服务接口（Session、Friends、Leaderboards 等）返回 `nullptr`，说明此插件**仅聚焦于身份认证**，不提供完整的多人游戏功能。

## 使用场景

- 你需要在移动端（Android/iOS）应用中实现 "Google 登录" 按钮 → 启用此插件
- 你需要通过 Google OAuth2 认证用户身份，然后将 token 发送到自定义后端服务器 → 使用此插件的 Identity 接口
- 你构建一个需要 Google 账号体系的跨平台游戏（Android + iOS + PC） → 此插件统一了各平台的 Google 登录实现
- 你需要静默刷新 Google Access Token 而不打扰用户 → 插件内置了 Refresh Auth 流程

## 蓝图用法

此插件的蓝图接口通过 `IOnlineSubsystem` 和 `IOnlineIdentity` 的标准在线服务蓝图节点暴露，没有额外的 `BlueprintCallable` 函数。

### 核心节点

所有功能通过标准的 Online Subsystem 蓝图节点访问：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetIdentityInterface` | 获取 Google 身份认证接口 | `FOnlineSubsystemGoogleCommon` |
| `GetExternalUIInterface` | 获取 Google 外部 UI 接口（登录界面） | `FOnlineSubsystemGoogleCommon` |
| `Login` | 发起 Google 登录流程 | `IOnlineIdentity` |
| `Logout` | 登出当前 Google 用户 | `IOnlineIdentity` |
| `GetLoginStatus` | 查询当前登录状态 | `IOnlineIdentity` |
| `GetUniquePlayerId` | 获取已登录用户的唯一 ID | `IOnlineIdentity` |
| `GetPlayerNickname` | 获取用户昵称 | `IOnlineIdentity` |
| `GetAuthToken` | 获取当前用户的 Access Token | `IOnlineIdentity` |
| `RevokeAuthToken` | 撤销用户的 Auth Token | `IOnlineIdentity` |
| `ShowLoginUI` | 显示 Google 登录 UI | `IOnlineExternalUI` |

### 使用示例（蓝图描述）

**初始化 Google 子系统：**
1. 在 Project Settings → Online Subsystem 中启用 Google 插件
2. 在 DefaultEngine.ini 中配置 `[OnlineSubsystemGoogle]` 段落，设置 `ClientId` 和 `ServerClientId`

**发起登录：**
1. 使用 `Get Online Subsystem` 节点（SubSystem Name 设为 `Google`）
2. 从返回值拉出 `Get Identity Interface`
3. 调用 `Login` 节点，Local User Num 为 0
4. 通过 `On Login Complete` 委托获取结果
5. 成功后使用 `Get Unique Player Id` 获取用户 ID，`Get Auth Token` 获取 Access Token

## C++ 用法

### 头文件引入

```cpp
#include "OnlineSubsystem.h"
#include "OnlineSubsystemGoogle.h"
#include "OnlineIdentityGoogleCommon.h"
```

### 基本用法

获取 Google 子系统并执行登录：

```cpp
// 获取 OnlineSubsystemGoogle 实例
IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(TEXT("Google"));
if (!OnlineSub)
{
    UE_LOG(LogOnline, Error, TEXT("OnlineSubsystemGoogle not found!"));
    return;
}

// 获取 Identity 接口
IOnlineIdentityPtr IdentityInterface = OnlineSub->GetIdentityInterface();
if (!IdentityInterface.IsValid())
{
    UE_LOG(LogOnline, Error, TEXT("Identity interface not available"));
    return;
}

// 绑定登录完成回调
IdentityInterface->AddOnLoginCompleteDelegate_Handle(
    0, // LocalUserNum
    FOnLoginCompleteDelegate::CreateLambda([](int32 LocalUserNum, bool bWasSuccessful, const FUniqueNetId& UserId, const FString& Error)
    {
        if (bWasSuccessful)
        {
            UE_LOG(LogOnline, Log, TEXT("Google login successful for user: %s"), *UserId.ToString());
        }
        else
        {
            UE_LOG(LogOnline, Error, TEXT("Google login failed: %s"), *Error);
        }
    })
);

// 发起登录（默认方式，会弹出 Google 登录页面）
IdentityInterface->Login(0, FOnlineAccountCredentials());
```

### 令牌管理

```cpp
// 登录成功后获取 Access Token
FString AccessToken = IdentityInterface->GetAuthToken(0);
UE_LOG(LogOnline, Log, TEXT("Access Token: %s"), *AccessToken);

// 查询登录状态
ELoginStatus::Type LoginStatus = IdentityInterface->GetLoginStatus(0);
if (LoginStatus == ELoginStatus::LoggedIn)
{
    // 用户已登录
    FUniqueNetIdPtr UserId = IdentityInterface->GetUniquePlayerId(0);
    FString Nickname = IdentityInterface->GetPlayerNickname(0);
}

// 撤销 Token
IdentityInterface->RevokeAuthToken(*UserId,
    FOnRevokeAuthTokenCompleteDelegate::CreateLambda([](const FUniqueNetId& UserId, const FOnlineError& Error)
    {
        UE_LOG(LogOnline, Log, TEXT("Token revoked: %s"), Error.bSucceeded ? TEXT("Success") : TEXT("Failed"));
    })
);
```

**来源：** 基于 `Source/Private/OnlineIdentityGoogleCommon.h` 和 `Source/Public/OnlineSubsystemGoogleCommon.h` 中的接口定义。

### 进阶用法

使用 `FGoogleAuthConfig` 覆盖默认认证配置（从 ini 文件加载后）：

```cpp
#include "OnlineSubsystemGoogleCommon.h"

// 覆盖 Google 认证配置（在子系统初始化前注册）
FOnlineSubsystemGoogleCommon::FGoogleConfigurationDelegate& ConfigDelegate =
    FOnlineSubsystemGoogleCommon::GetConfigurationDelegate();

ConfigDelegate.BindLambda([](const FString& ConfigOverride, FGoogleAuthConfig& OutConfig)
{
    OutConfig.Backend = TEXT("MyGameBackend");
    // 配置会通过 [OnlineSubsystemGoogle MyGameBackend] ini section 覆盖
});
```

使用 `FAuthTokenGoogle` 手动管理令牌（进阶场景）：

```cpp
#include "OnlineSubsystemGoogleTypes.h"

// 解析已有的 JWT ID Token
FJsonWebTokenGoogle JWT;
bool bParsed = JWT.Parse(InJWTString);

// 创建带 Refresh Token 的认证令牌
FAuthTokenGoogle RefreshToken(TEXT("your_refresh_token_here"), EGoogleRefreshToken);
if (RefreshToken.IsValid())
{
    // 可用于刷新获取新的 Access Token
}
```

## Demo 示例

```cpp
// GoogleLoginDemo.h
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "OnlineSubsystem.h"
#include "OnlineIdentityInterface.h"
#include "GoogleLoginDemo.generated.h"

UCLASS()
class UGoogleLoginDemoSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;

    UFUNCTION(BlueprintCallable, Category = "Google Login")
    void LoginWithGoogle();

    UFUNCTION(BlueprintCallable, Category = "Google Login")
    void LogoutFromGoogle();

    UFUNCTION(BlueprintCallable, Category = "Google Login")
    bool IsLoggedIn() const;

    UFUNCTION(BlueprintCallable, Category = "Google Login")
    FString GetUserDisplayName() const;

private:
    void OnLoginComplete(int32 LocalUserNum, bool bWasSuccessful, const FUniqueNetId& UserId, const FString& Error);
    void OnLogoutComplete(int32 LocalUserNum, bool bWasSuccessful);

    FDelegateHandle LoginDelegateHandle;
    FDelegateHandle LogoutDelegateHandle;
};
```

```cpp
// GoogleLoginDemo.cpp
#include "GoogleLoginDemo.h"

void UGoogleLoginDemoSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
}

void UGoogleLoginDemoSubsystem::LoginWithGoogle()
{
    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(TEXT("Google"));
    if (!OnlineSub)
    {
        UE_LOG(LogTemp, Error, TEXT("Google Online Subsystem not available. Ensure it is enabled in project settings."));
        return;
    }

    IOnlineIdentityPtr Identity = OnlineSub->GetIdentityInterface();
    if (!Identity.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Google Identity interface not valid."));
        return;
    }

    LoginDelegateHandle = Identity->AddOnLoginCompleteDelegate_Handle(
        0,
        FOnLoginCompleteDelegate::CreateUObject(this, &UGoogleLoginDemoSubsystem::OnLoginComplete)
    );

    // 触发 Google 登录，会弹出浏览器或原生 SDK 界面
    Identity->Login(0, FOnlineAccountCredentials());
}

void UGoogleLoginDemoSubsystem::LogoutFromGoogle()
{
    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(TEXT("Google"));
    if (!OnlineSub) return;

    IOnlineIdentityPtr Identity = OnlineSub->GetIdentityInterface();
    if (!Identity.IsValid()) return;

    LogoutDelegateHandle = Identity->AddOnLogoutCompleteDelegate_Handle(
        0,
        FOnLogoutCompleteDelegate::CreateUObject(this, &UGoogleLoginDemoSubsystem::OnLogoutComplete)
    );

    Identity->Logout(0);
}

bool UGoogleLoginDemoSubsystem::IsLoggedIn() const
{
    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(TEXT("Google"));
    if (!OnlineSub) return false;

    IOnlineIdentityPtr Identity = OnlineSub->GetIdentityInterface();
    if (!Identity.IsValid()) return false;

    return Identity->GetLoginStatus(0) == ELoginStatus::LoggedIn;
}

FString UGoogleLoginDemoSubsystem::GetUserDisplayName() const
{
    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(TEXT("Google"));
    if (!OnlineSub) return TEXT("");

    IOnlineIdentityPtr Identity = OnlineSub->GetIdentityInterface();
    if (!Identity.IsValid()) return TEXT("");

    return Identity->GetPlayerNickname(0);
}

void UGoogleLoginDemoSubsystem::OnLoginComplete(int32 LocalUserNum, bool bWasSuccessful, const FUniqueNetId& UserId, const FString& Error)
{
    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(TEXT("Google"));
    if (OnlineSub)
    {
        OnlineSub->GetIdentityInterface()->ClearOnLoginCompleteDelegate_Handle(LocalUserNum, LoginDelegateHandle);
    }

    if (bWasSuccessful)
    {
        UE_LOG(LogTemp, Log, TEXT("Google login succeeded! User: %s"), *UserId.ToString());
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Google login failed: %s"), *Error);
    }
}

void UGoogleLoginDemoSubsystem::OnLogoutComplete(int32 LocalUserNum, bool bWasSuccessful)
{
    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(TEXT("Google"));
    if (OnlineSub)
    {
        OnlineSub->GetIdentityInterface()->ClearOnLogoutCompleteDelegate_Handle(LocalUserNum, LogoutDelegateHandle);
    }

    UE_LOG(LogTemp, Log, TEXT("Google logout: %s"), bWasSuccessful ? TEXT("Success") : TEXT("Failed"));
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `OnlineSubsystem` | 在线子系统基础框架（.uplugin 显式依赖） |
| `OnlineSubsystemUtils` | 在线子系统通用工具类（如 `FOnlineSubsystemImpl`） |
| `Json` | Google API JSON 响应解析 |
| `JsonUtilities` | JSON 序列化/反序列化（`FJsonSerializable`） |
| `HTTP` | REST API 请求（OAuth2 令牌交换、用户资料获取） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-03-02 | `9758fa58` | FORT-984709 - Remove string duplication in FJsonObject to free memory | 优化 FJsonObject 内存使用，减少字符串重复 |
| 2026-01-27 | `113268fe` | Fixed include casing mismatch when compiling ios with case sensitive on | 修复 iOS 大小写敏感文件系统下的编译错误 |
| 2026-01-13 | `4c04edd1` | [IOS/Mac] Initial pass to remove iOS/macOS sdk headers from Engine platform header files where possi | 清理 iOS/macOS SDK 头文件，减少对引擎头文件的依赖 |
| 2025-09-02 | `7d7255e0` | Registered JNI functions. Made JNI classes for Java classes. Added thread_local Ue::Jni::Env global. | 重构 Android JNI 接口，改用 UE::Jni 命名空间新方案 |
| 2025-08-13 | `65515472` | - Deprecate OnlineJsonSerializer.h | 废弃旧的 OnlineJsonSerializer 头文件 |

### 维护评价

**维护状态：维护中（低频维护）**

- **年龄**：约 9 年，属于老古董级别的插件
- **更新频率**：最近一年有 5 次更新，但多为编译修复、平台头文件清理等基础设施更新，未涉及功能性改动
- **最后功能性更新**：2025 年 9 月的 JNI 重构（Android 平台相关）
- **已知限制**：
  - 大部分 IOnlineSubsystem 标准接口返回 `nullptr`（Session、Friends、Leaderboards 等），仅支持 Identity 和 ExternalUI
  - 需要手动在 `DefaultEngine.ini` 中配置 `ClientId` 和 `ServerClientId`
  - 桌面平台的 OAuth 流程依赖浏览器重定向，开发调试较为繁琐
- **推荐使用**：✅ 如果你需要在 UE5 项目中集成 Google 登录，这是 Epic 官方维护的实现，**推荐使用**。但请注意它只提供认证功能，不包含 Google Play Games Services 的成就、排行榜等游戏功能。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineSubsystemGoogle)
- [官方文档](https://docs.unrealengine.com/en-US/online-subsystem-google-in-unreal-engine/)