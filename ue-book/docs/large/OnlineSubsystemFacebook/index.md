# Online Subsystem Facebook

> Access to Facebook platform

| 属性 | 值 |
|---|---|
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `OnlineSubsystemFacebook` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2016-07-12 |
| 年龄标签 | 🏛️ 文物（约 10 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineSubsystemFacebook) | |

## 用途

OnlineSubsystemFacebook 是 Unreal Engine 的 Facebook 平台集成插件，通过 `IOnlineSubsystem` 接口提供 Facebook 社交功能的统一访问。该插件实现了 Facebook 登录认证、好友列表读取、社交分享（权限管理）、用户信息查询以及外部 UI 集成（浏览器登录流程）等功能。

该插件并非通用的社交登录方案，而是专门针对 Facebook 平台 API 的深度集成。它支持三种平台实现：

- **iOS**：通过 Facebook SDK（FBSDK）原生集成，支持 Classic Login 和 Limited Login 两种模式
- **Android**：通过 JNI 桥接 Facebook SDK
- **桌面端（Win64/Mac/Linux）**：通过 RESTful HTTP API 与 Facebook Graph API 通信，使用浏览器 OAuth 登录流程

**不支持的功能**：Session、Leaderboard、Achievement、Store、Purchase、Voice、Cloud、Chat、Presence、Stats 等接口均返回 `nullptr`，Facebook 本身不提供这些游戏服务功能。

## 使用场景

- 你的手游需要 Facebook 登录获取用户身份 → 使用 Identity 接口
- 你想展示玩家的 Facebook 好友列表（例如好友排行榜、邀请好友） → 使用 Friends 接口
- 你需要请求额外的 Facebook 权限（如 `user_friends`、`email`） → 使用 Sharing 接口的权限管理
- 你在桌面端需要 Facebook OAuth 登录流程 → 使用 ExternalUI 接口打开浏览器登录
- 你需要获取用户的 Facebook 个人资料（头像、姓名等） → 使用 User 接口 + Account 数据

**不适合的场景**：

- 需要 Facebook Gaming Services 的实时多人对战 → 应使用专用的 OnlineSubsystem
- 需要 IAP/商店功能 → Facebook 不提供此类接口
- 需要跨平台统一的社交系统 → Facebook 仅覆盖社交登录部分

## 蓝图用法

该插件没有暴露任何 `BlueprintCallable` 或 `BlueprintReadWrite` 的蓝图节点。所有功能通过 `IOnlineSubsystem` C++ 接口访问。

## C++ 用法

### 头文件引入

```cpp
#include "OnlineSubsystem.h"
#include "Interfaces/OnlineIdentityInterface.h"
#include "Interfaces/OnlineFriendsInterface.h"
#include "Interfaces/OnlineSharingInterface.h"
#include "Interfaces/OnlineExternalUIInterface.h"
#include "Interfaces/OnlineUserInterface.h"
```

### 配置（DefaultEngine.ini）

使用前必须在 `DefaultEngine.ini` 中配置 Facebook App ID 和 API 版本：

```ini
[OnlineSubsystemFacebook]
ClientId=YOUR_FACEBOOK_APP_ID
APIVer=v2.12

[OnlineSubsystemFacebook.OnlineIdentityFacebook]
MeURL=https://graph.facebook.com/`ver/me?access_token=`token
ProfileFields=id,name,first_name,last_name,picture,email

[OnlineSubsystemFacebook.OnlineSharingFacebook]
PermissionsURL=https://graph.facebook.com/`ver/me/permissions?access_token=`token

[OnlineSubsystemFacebook.OnlineFriendsFacebook]
FriendsURL=https://graph.facebook.com/`ver/me/friends?access_token=`token
FriendsFields=id,name,first_name,last_name,picture
```

还需要在 `DefaultEngine.ini` 中启用该子系统：

```ini
[OnlineSubsystem]
DefaultPlatformService=Facebook

[OnlineSubsystemFacebook]
Enabled=true
```

### 基本用法 - 登录

```cpp
// 获取 Facebook OnlineSubsystem
IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(FACEBOOK_SUBSYSTEM);
if (OnlineSub)
{
    // 获取 Identity 接口
    IOnlineIdentityPtr IdentityInterface = OnlineSub->GetIdentityInterface();
    if (IdentityInterface.IsValid())
    {
        // 绑定登录完成回调
        IdentityInterface->AddOnLoginCompleteDelegate_Handle(0,
            FOnLoginCompleteDelegate::CreateLambda([](int32 LocalUserNum, bool bWasSuccessful, 
                const FUniqueNetId& UserId, const FString& Error)
            {
                if (bWasSuccessful)
                {
                    UE_LOG(LogTemp, Log, TEXT("Facebook login succeeded: %s"), *UserId.ToString());
                }
                else
                {
                    UE_LOG(LogTemp, Warning, TEXT("Facebook login failed: %s"), *Error);
                }
            }));
        
        // 发起登录
        FOnlineAccountCredentials Credentials;
        Credentials.Type = TEXT("facebook");
        IdentityInterface->Login(0, Credentials);
    }
}
```

### 基本用法 - 获取好友列表

```cpp
IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(FACEBOOK_SUBSYSTEM);
IOnlineFriendsPtr FriendsInterface = OnlineSub->GetFriendsInterface();

FriendsInterface->AddOnReadFriendsListCompleteDelegate_Handle(0,
    FOnReadFriendsListComplete::CreateLambda([FriendsInterface](int32 LocalUserNum, bool bWasSuccessful, 
        const FString& ListName, const FString& Error)
    {
        if (bWasSuccessful)
        {
            TArray<TSharedRef<FOnlineFriend>> Friends;
            FriendsInterface->GetFriendsList(LocalUserNum, ListName, Friends);
            
            for (const auto& Friend : Friends)
            {
                UE_LOG(LogTemp, Log, TEXT("Friend: %s (ID: %s)"), 
                    *Friend->GetRealName(), *Friend->GetUserId()->ToString());
            }
        }
    }));

FriendsInterface->ReadFriendsList(0, EFriendsLists::ToString(EFriendsLists::Default));
```

### 进阶用法 - 权限请求

```cpp
IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(FACEBOOK_SUBSYSTEM);
IOnlineSharingPtr SharingInterface = OnlineSub->GetSharingInterface();

// 请求读取好友权限
SharingInterface->AddOnRequestNewReadPermissionsCompleteDelegate_Handle(0,
    FOnRequestNewReadPermissionsComplete::CreateLambda([](int32 LocalUserNum, bool bWasSuccessful)
    {
        UE_LOG(LogTemp, Log, TEXT("Read permissions request %s"), 
            bWasSuccessful ? TEXT("succeeded") : TEXT("failed"));
    }));

SharingInterface->RequestNewReadPermissions(0, EOnlineSharingCategory::Friends);

// 请求发布权限
SharingInterface->AddOnRequestNewPublishPermissionsCompleteDelegate_Handle(0,
    FOnRequestNewPublishPermissionsComplete::CreateLambda([](int32 LocalUserNum, bool bWasSuccessful)
    {
        UE_LOG(LogTemp, Log, TEXT("Publish permissions request %s"), 
            bWasSuccessful ? TEXT("succeeded") : TEXT("failed"));
    }));

SharingInterface->RequestNewPublishPermissions(0, EOnlineSharingCategory::Friends, EOnlineStatusUpdatePrivacy::Everyone);
```

### 进阶用法 - 获取用户资料

```cpp
IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(FACEBOOK_SUBSYSTEM);
IOnlineUserPtr UserInterface = OnlineSub->GetUserInterface();

TArray<FUniqueNetIdRef> UserIds;
UserIds.Add(OnlineSub->GetIdentityInterface()->GetUniquePlayerId(0).ToSharedRef());

UserInterface->AddOnQueryUserInfoCompleteDelegate_Handle(0,
    FOnQueryUserInfoComplete::CreateLambda([UserInterface](int32 LocalUserNum, bool bWasSuccessful, 
        const TArray<FUniqueNetIdRef>& QueriedUserIds, const FString& ErrorStr)
    {
        if (bWasSuccessful)
        {
            for (const auto& UserId : QueriedUserIds)
            {
                TSharedPtr<FOnlineUser> UserInfo = UserInterface->GetUserInfo(LocalUserNum, *UserId);
                if (UserInfo.IsValid())
                {
                    FString PictureURL;
                    UserInfo->GetUserAttribute(TEXT("picture"), PictureURL);
                    UE_LOG(LogTemp, Log, TEXT("User %s: %s"), *UserInfo->GetRealName(), *PictureURL);
                }
            }
        }
    }));

UserInterface->QueryUserInfo(0, UserIds);
```

### 控制台命令

该插件注册了以下控制台命令用于调试：

```
FACEBOOK LOGIN <LocalNum>           // 登录 Facebook
FACEBOOK LOGOUT <LocalNum>          // 登出 Facebook
FACEBOOK FRIENDS <LocalNum>         // 读取好友列表
FACEBOOK REQUESTREADSCOPES <Hex> <LocalNum>    // 请求读取权限
FACEBOOK REQUESTPUBLISHSCOPES <Hex> <LocalNum> // 请求发布权限
```

## Demo 示例

### 最小登录示例

```cpp
// MyGameInstance.h
#pragma once
#include "Engine/GameInstance.h"
#include "OnlineSubsystem.h"
#include "Interfaces/OnlineIdentityInterface.h"
#include "MyGameInstance.generated.h"

UCLASS()
class UMyGameInstance : public UGameInstance
{
    GENERATED_BODY()

public:
    virtual void Init() override;

    UFUNCTION(BlueprintCallable)
    void LoginFacebook();

private:
    FDelegateHandle LoginDelegateHandle;
    void OnLoginComplete(int32 LocalUserNum, bool bWasSuccessful, const FUniqueNetId& UserId, const FString& Error);
};
```

```cpp
// MyGameInstance.cpp
#include "MyGameInstance.h"
#include "OnlineError.h"

void UMyGameInstance::Init()
{
    Super::Init();
}

void UMyGameInstance::LoginFacebook()
{
    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(FACEBOOK_SUBSYSTEM);
    if (!OnlineSub)
    {
        UE_LOG(LogTemp, Error, TEXT("Facebook OnlineSubsystem not available"));
        return;
    }

    IOnlineIdentityPtr Identity = OnlineSub->GetIdentityInterface();
    if (!Identity.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Identity interface not available"));
        return;
    }

    LoginDelegateHandle = Identity->AddOnLoginCompleteDelegate_Handle(0,
        FOnLoginCompleteDelegate::CreateUObject(this, &UMyGameInstance::OnLoginComplete));

    FOnlineAccountCredentials Credentials;
    Credentials.Type = TEXT("facebook");
    Identity->Login(0, Credentials);
}

void UMyGameInstance::OnLoginComplete(int32 LocalUserNum, bool bWasSuccessful, 
    const FUniqueNetId& UserId, const FString& Error)
{
    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(FACEBOOK_SUBSYSTEM);
    IOnlineIdentityPtr Identity = OnlineSub->GetIdentityInterface();
    
    Identity->ClearOnLoginCompleteDelegate_Handle(LocalUserNum, LoginDelegateHandle);

    if (bWasSuccessful)
    {
        FString Nickname = Identity->GetPlayerNickname(LocalUserNum);
        FString AccessToken = Identity->GetAuthToken(LocalUserNum);
        UE_LOG(LogTemp, Log, TEXT("Facebook login OK: %s (Token: %s)"), *Nickname, *AccessToken.Left(20));
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Facebook login failed: %s"), *Error);
    }
}
```

**Build.cs 依赖**：

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
    "Engine",
    "OnlineSubsystem",
    "OnlineSubsystemFacebook"
});
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心库 |
| `CoreOnline` | 在线平台基础类型（FUniqueNetId 等） |
| `CoreUObject` | UObject 系统 |
| `ApplicationCore` | 平台应用层抽象 |
| `HTTP` | HTTP 请求（用于 Facebook Graph API 调用） |
| `ImageCore` | 图片处理（头像加载） |
| `Json` | JSON 序列化/反序列化（Facebook API 响应解析） |
| `OnlineSubsystem` | 在线子系统框架（IOnlineSubsystem 基类） |
| `Facebook` (ThirdParty) | Facebook SDK 静态库（iOS/Android 原生集成） |
| `Launch` (Android only) | Android 启动模块，JNI 支持 |

## 架构概览

该插件采用三层架构设计：

```
FOnlineSubsystemFacebook (平台特定层)
    ├── IOS/OnlineSubsystemFacebook.cpp     → iOS FBSDK 集成
    ├── IOS/OnlineIdentityFacebook.cpp      → iOS 登录（Classic/Limited）
    ├── IOS/OnlineFriendsFacebook.cpp       → iOS 好友
    ├── IOS/OnlineSharingFacebook.cpp       → iOS 分享
    ├── IOS/OnlineExternalUIInterfaceFacebook.cpp → iOS 外部 UI
    ├── Android/OnlineIdentityFacebook.cpp  → Android JNI 登录
    ├── Android/OnlineSharingFacebook.cpp   → Android 分享
    └── Rest/OnlineSubsystemFacebookRest.cpp → 桌面端 REST 实现
        ├── Rest/OnlineIdentityFacebookRest.cpp
        ├── Rest/OnlineFriendsFacebookRest.cpp
        ├── Rest/OnlineSharingFacebookRest.cpp
        └── Rest/OnlineExternalUIInterfaceFacebookRest.cpp

FOnlineSubsystemFacebookCommon (跨平台公共层)
    ├── OnlineIdentityFacebookCommon.cpp    → 身份认证（HTTP /me 请求）
    ├── OnlineFriendsFacebookCommon.cpp     → 好友列表（HTTP /me/friends）
    ├── OnlineSharingFacebookCommon.cpp     → 权限管理
    ├── OnlineUserFacebookCommon.cpp        → 用户信息查询
    ├── OnlineExternalUIFacebookCommon.cpp  → 外部 UI 基础
    └── OnlineAccountFacebookCommon.cpp     → 用户账户数据

FUniqueNetIdFacebook (类型系统)
    └── OnlineSubsystemFacebookTypes.h      → ID 类型、错误解析、头像数据
```

**平台选择逻辑**（在 Build.cs 中）：

- iOS → 使用 Facebook SDK 原生实现
- Android → 使用 JNI 桥接 Facebook SDK
- Win64/Mac/Linux → 使用 RESTful HTTP API（`USES_RESTFUL_FACEBOOK=1`）
- 其他平台 → 不编译（`WITH_FACEBOOK=0`）

**iOS 登录模式**：

- **Classic Login**（`bUseClassicLogin=true`，默认）：使用传统 Facebook SDK 登录，需要 `AppTrackingTransparency` 框架
- **Limited Login**：iOS 13+ 的隐私友好登录模式，不追踪用户

通过 `[OnlineSubsystemFacebook]` 配置节的 `bUseClassicLogin` 控制。

## 维护状态

### 近期更新

1. **2025-09-02** `5a48f72f` — Registered JNI functions. Made JNI classes for Java classes. Added thread_local Ue::Jni::Env global. Various JNI bug fixes and cleanup
   - 解读：Android JNI 层重构，修复了多个 JNI 相关 bug，添加了线程本地 JNI 环境全局变量。属于基础设施改进。

2. **2025-08-13** `65515472` — Deprecate OnlineJsonSerializer.h
   - 解读：废弃旧的 JSON 序列化头文件，属于代码清理。

3. **2025-06-26** `d2ec2238` — Generalized IOSAsyncTask to AppleAsyncTask in preparation for using WebKit in the macOS WebBrowser engine plugin with deprecation warnings
   - 解读：iOS 异步任务重构为通用 Apple 平台任务，为 macOS WebKit 支持做准备。

### 维护评价

- **创建时间**：2016 年 7 月，至今约 10 年
- **最近更新**：2025 年 9 月仍有更新，但均为基础设施维护（JNI 重构、废弃 API 清理、平台抽象改进）
- **实质性功能更新**：长期未有新功能添加，最近的更新都是跟随引擎整体重构
- **Facebook API 版本**：硬编码的 fallback 版本为 `v2.12`（2018 年发布），说明核心逻辑多年未变
- **平台限制**：仅支持 iOS、Android、Win64，不支持主机平台
- **不推荐原因**：
  - Facebook Gaming Services 已成为 Meta 主推方案，该插件使用的是旧版 Graph API
  - Facebook 对第三方游戏的 API 访问限制越来越严格
  - Meta 已将重心转向 VR/AR 平台（Quest），传统移动社交登录优先级降低
  - `EnabledByDefault=false` 说明 Epic 也不认为这是主流方案

⚠️ **警告**：该插件仍可使用，但 Facebook 社交登录在游戏中的使用率持续下降。如果是新项目，建议评估是否真正需要 Facebook 登录，或考虑使用更通用的 OAuth 方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineSubsystemFacebook)
- [Facebook Graph API 文档](https://developers.facebook.com/docs/graph-api)
- [Facebook Login for Games](https://developers.facebook.com/docs/games/services/login)
