# Online Subsystem Amazon

> Access to Amazon platform

| 属性 | 值 |
|---|---|
| 分类 | Online Platform |
| 默认启用 | false |
| 包含内容 | false |
| 模块 | OnlineSubsystemAmazon (Runtime) |
| 创建时间 | 2016-07-12 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineSubsystemAmazon) | |

## 用途

OnlineSubsystemAmazon 是 Unreal Engine 的 Online Subsystem 框架中针对 Amazon 平台的实现插件。它通过 `IOnlineIdentity` 接口为运行在 Amazon 设备（如 Kindle Fire 系列平板）上的游戏提供身份认证功能。

该插件实现了 **Amazon OAuth 2.0 授权码流程**：在用户触发登录后，通过系统浏览器打开 Amazon 授权页面，用户完成授权后回调 URL 中携带的 token 信息被引擎截获并解析为 `accessToken`、`refreshToken` 和 `amazonCustomerId`。

**重要限制**：这是 OnlineSubsystem 家族中功能最精简的实现之一。它**仅实现了 Identity 接口**，其余所有接口（Session、Friends、Leaderboards、Achievements、Store 等）均返回 `nullptr`。这意味着它只能用于基本的 Amazon 账号登录认证，不支持任何社交或在线功能。

## 使用场景

- 你在开发针对 Amazon Fire 平台的游戏，需要实现 Amazon 账号登录
- 你需要获取 Amazon 的 `accessToken` 来调用自定义的 Amazon 后端服务
- 你使用 OnlineSubsystem 的抽象接口，只需切换底层平台实现即可支持 Amazon 设备

**不适合的场景**：

- 需要好友列表、排行榜、成就等功能 → 改用其他 OnlineSubsystem（如 EOS、Steam）
- 需要会话管理（Matchmaking）→ 该插件不支持 Session 接口
- 非 Amazon 设备上的 Amazon 账号登录 → 该插件是平台级子系统，不是通用 Amazon 登录库

## 蓝图用法

该插件没有暴露任何 `BlueprintCallable` 或 `BlueprintReadWrite` 接口。所有交互都通过 Online Subsystem 框架的标准蓝图节点间接完成：

### 通过通用节点访问

| 节点 | 说明 | 前提 |
|---|---|---|
| `Get Online Subsystem` | 获取 `AMAZON_SUBSYSTEM` 名称的子系统实例 | 项目需配置为默认使用 Amazon 子系统 |
| `Login` (Identity 通用节点) | 触发 Amazon OAuth 登录流程 | 子系统实例有效 |

## C++ 用法

### 头文件引入

```cpp
#include "OnlineSubsystem.h"
#include "OnlineIdentityInterface.h"
#include "OnlineSubsystemNames.h"
```

### 基本用法 — 获取 Identity 接口并登录

```cpp
// 获取 Amazon Online Subsystem 实例
IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(AMAZON_SUBSYSTEM);
if (OnlineSub)
{
    // 获取 Identity 接口
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
                        UE_LOG(LogTemp, Log, TEXT("Amazon Login Success! UserId: %s"), *UserId.ToString());
                    }
                    else
                    {
                        UE_LOG(LogTemp, Error, TEXT("Amazon Login Failed: %s"), *Error);
                    }
                }
            )
        );

        // 触发登录（会打开系统浏览器进行 Amazon OAuth 授权）
        FOnlineAccountCredentials Credentials;
        IdentityInterface->Login(0, Credentials);
    }
}
```

### 获取 Access Token

```cpp
IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(AMAZON_SUBSYSTEM);
if (OnlineSub)
{
    IOnlineIdentityPtr IdentityInterface = OnlineSub->GetIdentityInterface();
    if (IdentityInterface.IsValid())
    {
        // 获取 LocalUserNum 0 的 auth token（即 Amazon accessToken）
        FString AccessToken = IdentityInterface->GetAuthToken(0);
        
        // 使用 AccessToken 调用 Amazon API...
    }
}
```

### 登出

```cpp
IOnlineIdentityPtr IdentityInterface = OnlineSub->GetIdentityInterface();
if (IdentityInterface.IsValid())
{
    IdentityInterface->AddOnLogoutCompleteDelegate_Handle(
        0,
        FOnLogoutCompleteDelegate::CreateLambda(
            [](int32 LocalUserNum, bool bWasSuccessful)
            {
                UE_LOG(LogTemp, Log, TEXT("Amazon Logout: %s"), bWasSuccessful ? TEXT("Success") : TEXT("Failed"));
            }
        )
    );
    
    IdentityInterface->Logout(0);
}
```

## 配置要求

在 `DefaultEngine.ini` 中必须配置以下项，否则登录将失败：

```ini
[OnlineSubsystemAmazon.OnlineSubsystemAmazon]
AmazonEndpoint=https://www.amazon.com/ap/oa
RedirectUrl=https://your-app-callback-url.com
ClientId=your-amazon-app-client-id
RegistrationTimeout=30.0
```

| 配置项 | 说明 |
|---|---|
| `AmazonEndpoint` | Amazon OAuth 授权端点 URL |
| `RedirectUrl` | 授权完成后的回调 URL（需在 Amazon 开发者控制台注册） |
| `ClientId` | Amazon 应用的 Client ID |
| `RegistrationTimeout` | 等待用户完成授权的超时时间（秒），默认 30 |

同时需要在 `DefaultEngine.ini` 中设置默认 Online Subsystem：

```ini
[OnlineSubsystem]
DefaultPlatformService=Amazon
```

## 模块依赖

从 `OnlineSubsystemAmazon.Build.cs` 提取：

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `CoreUObject` | UE 对象系统 |
| `ApplicationCore` | 平台应用基础功能 |
| `HTTP` | HTTP 请求（用于与 Amazon 服务通信） |
| `Json` | JSON 解析（用于解析认证响应） |
| `OnlineSubsystem` | Online Subsystem 框架基础 |

插件还声明了对 `OnlineSubsystem` 插件的依赖（.uplugin 中的 Plugins 字段）。

**使用者无需额外依赖**：该插件的所有依赖都是 `PrivateDependencyModuleNames`，外部模块只需通过 `IOnlineSubsystem::Get(AMAZON_SUBSYSTEM)` 获取实例即可。

## Demo 示例

### 完整的最小登录示例

```cpp
// MyGameInstance.h
#pragma once
#include "Engine/GameInstance.h"
#include "OnlineSubsystem.h"
#include "OnlineIdentityInterface.h"
#include "MyGameInstance.generated.h"

UCLASS()
class UMyGameInstance : public UGameInstance
{
    GENERATED_BODY()

public:
    virtual void Init() override;

    UFUNCTION(BlueprintCallable)
    void LoginWithAmazon();

    UFUNCTION(BlueprintCallable)
    void LogoutAmazon();

private:
    void OnLoginComplete(int32 LocalUserNum, bool bWasSuccessful, const FUniqueNetId& UserId, const FString& Error);
    void OnLogoutComplete(int32 LocalUserNum, bool bWasSuccessful);
    
    FDelegateHandle LoginDelegateHandle;
    FDelegateHandle LogoutDelegateHandle;
};
```

```cpp
// MyGameInstance.cpp
#include "MyGameInstance.h"
#include "OnlineSubsystemNames.h"

void UMyGameInstance::Init()
{
    Super::Init();
}

void UMyGameInstance::LoginWithAmazon()
{
    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(AMAZON_SUBSYSTEM);
    if (!OnlineSub)
    {
        UE_LOG(LogTemp, Error, TEXT("Amazon Online Subsystem not available!"));
        return;
    }

    IOnlineIdentityPtr Identity = OnlineSub->GetIdentityInterface();
    if (!Identity.IsValid()) return;

    LoginDelegateHandle = Identity->AddOnLoginCompleteDelegate_Handle(
        0, FOnLoginCompleteDelegate::CreateUObject(this, &UMyGameInstance::OnLoginComplete));

    FOnlineAccountCredentials Credentials;
    Identity->Login(0, Credentials);
}

void UMyGameInstance::LogoutAmazon()
{
    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(AMAZON_SUBSYSTEM);
    if (!OnlineSub) return;

    IOnlineIdentityPtr Identity = OnlineSub->GetIdentityInterface();
    if (!Identity.IsValid()) return;

    LogoutDelegateHandle = Identity->AddOnLogoutCompleteDelegate_Handle(
        0, FOnLogoutCompleteDelegate::CreateUObject(this, &UMyGameInstance::OnLogoutComplete));

    Identity->Logout(0);
}

void UMyGameInstance::OnLoginComplete(int32 LocalUserNum, bool bWasSuccessful, const FUniqueNetId& UserId, const FString& Error)
{
    if (bWasSuccessful)
    {
        UE_LOG(LogTemp, Log, TEXT("Amazon login success: %s"), *UserId.ToString());
        
        IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(AMAZON_SUBSYSTEM);
        IOnlineIdentityPtr Identity = OnlineSub->GetIdentityInterface();
        FString Token = Identity->GetAuthToken(0);
        UE_LOG(LogTemp, Log, TEXT("Access Token: %s"), *Token);
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Amazon login failed: %s"), *Error);
    }
}

void UMyGameInstance::OnLogoutComplete(int32 LocalUserNum, bool bWasSuccessful)
{
    UE_LOG(LogTemp, Log, TEXT("Amazon logout: %s"), bWasSuccessful ? TEXT("OK") : TEXT("Failed"));
}
```

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-08-13 | `6551547` | Deprecate OnlineJsonSerializer.h | 例行清理：将旧的 JSON 序列化头文件标记为废弃，属于框架层重构，非功能性变更 |
| 2024-06-24 | `f40be2d` | Fixed some 'deprecated' FString usage | 编译警告修复：替换已废弃的 FString API，维护性更新 |
| 2023-11-16 | `b1ad5ea` | Add ShowResolveUI param to GetUserPrivilege | 接口适配：Identity 接口签名变更，该插件跟随更新参数 |

### 维护评价

- **年龄**：2016 年创建，已超过 9 年
- **最后实质性功能更新**：无。该插件自创建以来从未有过功能性更新，所有近期 commit 都是跟随框架接口变更的被动适配
- **代码质量**：多处 `@todo - not implemented` 注释（如 `GetPlayerNickname`），部分方法（如 `RevokeAuthToken`）显式返回未实现错误
- **活跃度**：**极低**。这是一个功能冻结的骨架实现
- **是否推荐使用**：⚠️ **有条件推荐**。如果你确实在 Amazon Fire 设备上开发游戏且只需基本登录功能，它是唯一选择。但对于其他场景，建议使用 EOS 或其他更完善的 OnlineSubsystem 实现

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineSubsystemAmazon)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineSubsystemAmazon)（无独立测试文件）
