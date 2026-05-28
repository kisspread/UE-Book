# Online Subsystem Facebook

> Access to Facebook platform

| 属性 | 值 |
|---|---|
| 中文名 | Facebook 在线子系统 |
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `OnlineSubsystemFacebook` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2016-07-13 |
| 年龄标签 | 👴 老古董（约 10 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineSubsystemFacebook) | |

## 用途

该插件为 Unreal Engine 的 Online Subsystem 框架提供 Facebook 平台的完整集成。它实现了 Facebook 用户身份验证、好友列表获取、社交分享、权限管理以及外部 UI 登录等核心功能。

插件采用**平台分离架构**：共用基类（`FOnlineSubsystemFacebookCommon`）位于 `Source/Private`，而 Android、iOS、Windows 三个平台各自拥有独立的实现：
- **Android**：通过 JNI 调用 Facebook Java SDK
- **iOS**：通过 Objective-C 桥接调用 FBSDK（支持经典登录和 Limited Login）
- **Windows**：通过 REST API + OAuth 浏览器重定向流程

该插件默认不启用（`EnabledByDefault: false`），需要在项目设置中手动启用。由于 Facebook 社交 API 政策变化，此插件的功能范围已大幅缩减，主要保留身份验证和基本好友查询能力。

## 使用场景

- 你的移动游戏需要 Facebook 登录功能 → 使用 Identity 接口进行 OAuth 认证
- 你需要获取玩家的 Facebook 好友列表用于社交功能 → 使用 Friends 接口
- 你的游戏需要请求 Facebook 用户的额外权限（如邮箱、好友列表）→ 使用 Sharing 接口管理权限
- 你需要在 Windows 桌面端通过浏览器弹出 Facebook 登录页 → 使用 ExternalUI 接口

## 蓝图用法

该插件本身不直接暴露蓝图节点。所有功能通过 UE 标准的 **Online Subsystem 蓝图接口** 调用，例如 `Login`、`Get Friends List` 等节点。

### 核心访问方式

需要先通过 `IOnlineSubsystem::Get()` 获取 Facebook 子系统实例：

```cpp
// 在 DefaultEngine.ini 中配置
[OnlineSubsystem]
DefaultPlatformService=Facebook

[OnlineSubsystemFacebook]
ClientId=你的FacebookAppID
```

然后在蓝图中使用标准的 Online Subsystem 蓝图节点（如 `Call Login`），系统会自动路由到 Facebook 实现。

## C++ 用法

### 头文件引入

```cpp
#include "OnlineSubsystemFacebook.h"
```

### 基本用法

通过 Online Subsystem 接口访问 Facebook 功能（基于源码结构推断）：

```cpp
#include "OnlineSubsystem.h"
#include "OnlineSubsystemFacebook.h"
#include "Interfaces/OnlineIdentityInterface.h"
#include "Interfaces/OnlineFriendsInterface.h"

// 获取 Facebook Online Subsystem
IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(FName(TEXT("Facebook")));
if (OnlineSub)
{
    // 获取身份接口 - 用于登录
    IOnlineIdentityPtr IdentityInterface = OnlineSub->GetIdentityInterface();
    if (IdentityInterface.IsValid())
    {
        // 发起登录请求
        FOnlineAccountCredentials Credentials;
        Credentials.Type = TEXT("facebook");
        IdentityInterface->Login(0, Credentials);
    }

    // 获取好友接口 - 读取好友列表
    IOnlineFriendsPtr FriendsInterface = OnlineSub->GetFriendsInterface();
    if (FriendsInterface.IsValid())
    {
        FOnReadFriendsListComplete Delegate;
        FriendsInterface->ReadFriendsList(0, TEXT("default"), Delegate);
    }
}
```

### 进阶用法

处理 Facebook 登录回调并获取用户信息：

```cpp
// 绑定登录完成委托
IdentityInterface->AddOnLoginCompleteDelegate_Handle(
    0,
    FOnLoginCompleteDelegate::CreateLambda(
        [](int32 LocalUserNum, bool bWasSuccessful, const FUniqueNetId& UserId, const FString& Error)
        {
            if (bWasSuccessful)
            {
                // 获取用户账户信息
                TSharedPtr<FUserOnlineAccount> Account = 
                    IdentityInterface->GetUserAccount(UserId);
                if (Account.IsValid())
                {
                    // 获取访问令牌
                    FString AccessToken = Account->GetAccessToken();
                    
                    // 获取用户属性（姓名、头像等）
                    FString RealName;
                    Account->GetUserAttribute(TEXT("name"), RealName);
                }
            }
        }
    )
);

// 获取分享接口 - 请求额外权限
IOnlineSharingPtr SharingInterface = OnlineSub->GetSharingInterface();
if (SharingInterface.IsValid())
{
    FOnRequestCurrentPermissionsComplete PermDelegate;
    SharingInterface->RequestCurrentPermissions(0, PermDelegate);
    
    // 请求新的读取权限（如好友列表）
    SharingInterface->RequestNewReadPermissions(0, EOnlineSharingCategory::Friends);
}
```

## Demo 示例

最小示例：实现 Facebook 登录并获取用户信息。

```cpp
// FacebookLoginDemo.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Interfaces/OnlineIdentityInterface.h"
#include "FacebookLoginDemo.generated.h"

UCLASS()
class AFacebookLoginDemo : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;

    UFUNCTION(BlueprintCallable)
    void LoginToFacebook();

private:
    void OnLoginComplete(int32 LocalUserNum, bool bWasSuccessful, 
                         const FUniqueNetId& UserId, const FString& Error);

    IOnlineIdentityPtr IdentityInterface;
};
```

```cpp
// FacebookLoginDemo.cpp
#include "FacebookLoginDemo.h"
#include "OnlineSubsystem.h"
#include "OnlineSubsystemFacebook.h"

void AFacebookLoginDemo::BeginPlay()
{
    Super::BeginPlay();

    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(FName(TEXT("Facebook")));
    if (OnlineSub)
    {
        IdentityInterface = OnlineSub->GetIdentityInterface();
        if (IdentityInterface.IsValid())
        {
            IdentityInterface->AddOnLoginCompleteDelegate_Handle(
                0,
                FOnLoginCompleteDelegate::CreateUObject(
                    this, &AFacebookLoginDemo::OnLoginComplete)
            );
        }
    }
}

void AFacebookLoginDemo::LoginToFacebook()
{
    if (IdentityInterface.IsValid())
    {
        FOnlineAccountCredentials Credentials;
        Credentials.Type = TEXT("facebook");
        IdentityInterface->Login(0, Credentials);
    }
}

void AFacebookLoginDemo::OnLoginComplete(int32 LocalUserNum, bool bWasSuccessful, 
                                          const FUniqueNetId& UserId, const FString& Error)
{
    if (bWasSuccessful)
    {
        UE_LOG(LogTemp, Log, TEXT("Facebook login successful! UserId: %s"), *UserId.ToString());
        
        FString PlayerName = IdentityInterface->GetPlayerNickname(LocalUserNum);
        UE_LOG(LogTemp, Log, TEXT("Player Name: %s"), *PlayerName);
        
        FString AuthToken = IdentityInterface->GetAuthToken(LocalUserNum);
        UE_LOG(LogTemp, Log, TEXT("Auth Token obtained: %s"), 
            AuthToken.IsEmpty() ? TEXT("Empty") : TEXT("Available"));
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Facebook login failed: %s"), *Error);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `OnlineSubsystem` | Online Subsystem 基础框架，提供接口定义 |
| `OnlineSubsystemUtils` | Online Subsystem 工具函数 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 64 位整数的格式化字符串 |
| 2026-01-27 | `113268fe` | Fixed include casing mismatch when compiling ios with case sensitive on | 修复 iOS 大小写敏感编译问题 |
| 2026-01-14 | `1a097717` | Fix IOS CIS Issues. | 修复 iOS CI 构建问题 |
| 2025-09-02 | `7d7255e0` | Registered JNI functions. Made JNI classes for Java classes. Added thread_local Ue::Jni::Env global. | 重构 Android JNI 框架适配 |
| 2025-08-13 | `65515472` | Deprecate OnlineJsonSerializer.h | 废弃旧版 JSON 序列化头文件 |

### 维护评价

该插件创建于 2016 年，已有约 10 年历史。近期的提交均为**编译修复和框架适配**（如 JNI 重构、大小写修复），没有功能性更新。

**关键问题**：
- Facebook 的 Graph API 权限政策已大幅收紧，`user_friends` 等权限需要应用审核
- Epic Games 自 2020 年后逐步减少对 Facebook SDK 的主动维护
- 该插件默认不启用（`EnabledByDefault: false`），表明 Epic 不推荐新项目使用
- 依赖 Facebook 的第三方 SDK，存在版本兼容性风险

**推荐**：仅在已有项目依赖 Facebook 登录功能时使用。新项目建议评估其他社交登录方案（如 Google Play Games、Apple Sign-In 或 Epic Online Services）。该插件处于**维护状态**，不建议用于关键路径功能。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineSubsystemFacebook)
- [Online Subsystem 基础插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineSubsystem)