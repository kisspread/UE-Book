# Online Subsystem Amazon

> Access to Amazon platform

| 属性 | 值 |
|---|---|
| 中文名 | 亚马逊在线子系统 |
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `OnlineSubsystemAmazon` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2016-07-13 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineSubsystemAmazon) | |

## 用途

这是一个 Unreal Engine 的在线子系统插件，为 Amazon 平台（如 Amazon GameCircle、Amazon Underground 等）提供基础的身份认证集成。它实现了 `IOnlineSubsystem` 接口，但**仅实现了身份验证（Identity）接口**，而会话、好友、排行榜等其他在线功能接口均返回 `nullptr`，这意味着它专注于亚马逊平台的用户登录和身份管理。

## 使用场景

- **游戏需要集成亚马逊账号登录**：当你的游戏需要支持使用亚马逊账号进行登录时，可以使用此插件。
- **针对亚马逊平台（如 Fire TV、Kindle 设备）发布游戏**：在这些设备上，可以使用此插件对接亚马逊的认证服务。

## 蓝图用法

该插件的使用主要通过引擎的在线子系统管理器（`IOnlineSubsystem`）进行，蓝图中通常不直接使用其类，而是使用引擎提供的通用在线子系统节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Online Subsystem` | 获取在线子系统实例，指定 `Amazon` 名称即可获取此插件的实例。 | `IOnlineSubsystem` (通过引擎节点) |
| `Login` | 调用登录功能，使用亚马逊平台账号。 | `IOnlineIdentity` (由 `FOnlineIdentityAmazon` 实现) |
| `Get Login Status` | 获取指定本地用户的登录状态。 | `IOnlineIdentity` (由 `FOnlineIdentityAmazon` 实现) |
| `Get Player Nickname` | 获取玩家的昵称。 | `IOnlineIdentity` (由 `FOnlineIdentityAmazon` 实现) |

### 使用示例（蓝图描述）

1.  **获取子系统**: 在蓝图中，使用“Get Online Subsystem”节点，将“Subsystem Name”设置为 `Amazon`。
2.  **登录**: 调用获取到的子系统的“Login”方法，传入 `Local User Num`（通常为0）和 `Account Credentials`（账号凭证）。凭证需要包含亚马逊平台要求的信息。
3.  **检查状态**: 登录后，可以通过“Get Login Status”或“Get Player Nickname”来获取登录结果。

## C++ 用法

### 头文件引入

```cpp
#include "OnlineSubsystemAmazon.h"
```

### 基本用法

通过 `IOnlineSubsystem` 接口获取亚马逊子系统实例，并访问其身份接口。

```cpp
// OnlineSubsystemAmazon.h 定义了 FOnlineSubsystemAmazon 类
#include "OnlineSubsystem.h"
#include "OnlineSubsystemAmazon.h"

// 获取亚马逊在线子系统实例
IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(FName(TEXT("Amazon")));
if (OnlineSub)
{
    // 获取身份接口
    IOnlineIdentityPtr IdentityInterface = OnlineSub->GetIdentityInterface();
    if (IdentityInterface.IsValid())
    {
        // 调用登录，例如自动登录
        IdentityInterface->AutoLogin(0); // 0 代表本地用户索引
    }
}
```

### 进阶用法

直接使用 `FOnlineSubsystemAmazon` 和 `FOnlineIdentityAmazon` 类进行更底层的控制（通常不推荐，建议使用接口）。

```cpp
// OnlineIdentityAmazon.h 定义了 FOnlineIdentityAmazon 类
#include "OnlineIdentityAmazon.h"

// 假设已经通过某种方式获得了 FOnlineSubsystemAmazon 指针
FOnlineSubsystemAmazon* AmazonSubsystem = ...;
if (AmazonSubsystem)
{
    FOnlineIdentityAmazonPtr Identity = AmazonSubsystem->GetIdentityInterface();
    if (Identity.IsValid())
    {
        // 直接调用登录，需要构造 FOnlineAccountCredentials
        FOnlineAccountCredentials Credentials;
        // 填充亚马逊平台要求的凭证字段...
        Credentials.Type = TEXT("amazon"); // 凭证类型，可能需根据平台文档调整
        Credentials.Id = TEXT("...");
        Credentials.Token = TEXT("...");

        // 调用登录
        Identity->Login(0, Credentials);
    }
}
```

## Demo 示例

以下是一个最小的 C++ 类，演示如何在 Actor 中初始化并使用亚马逊在线子系统进行登录。

### MyAmazonLoginActor.h
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "OnlineSubsystem.h"
#include "OnlineIdentityInterface.h"
#include "MyAmazonLoginActor.generated.h"

UCLASS()
class AMyAmazonLoginActor : public AActor
{
    GENERATED_BODY()

public:
    AMyAmazonLoginActor();

protected:
    virtual void BeginPlay() override;

private:
    void HandleLoginComplete(int32 LocalUserNum, bool bWasSuccessful, const FUniqueNetId& UserId, const FString& Error);

    IOnlineIdentityPtr IdentityInterface;
};
```

### MyAmazonLoginActor.cpp
```cpp
#include "MyAmazonLoginActor.h"
#include "OnlineSubsystemAmazon.h"

AMyAmazonLoginActor::AMyAmazonLoginActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyAmazonLoginActor::BeginPlay()
{
    Super::BeginPlay();

    // 1. 获取亚马逊在线子系统
    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(FName(TEXT("Amazon")));
    if (!OnlineSub)
    {
        UE_LOG(LogTemp, Error, TEXT("Amazon Online Subsystem not available."));
        return;
    }

    // 2. 获取身份接口
    IdentityInterface = OnlineSub->GetIdentityInterface();
    if (!IdentityInterface.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to get Amazon Identity Interface."));
        return;
    }

    // 3. 绑定登录完成委托
    IdentityInterface->AddOnLoginCompleteDelegate_Handle(0,
        FOnLoginCompleteDelegate::CreateUObject(this, &AMyAmazonLoginActor::HandleLoginComplete));

    // 4. 触发自动登录（如果支持）或手动登录
    UE_LOG(LogTemp, Log, TEXT("Attempting Amazon auto-login..."));
    IdentityInterface->AutoLogin(0);
}

void AMyAmazonLoginActor::HandleLoginComplete(int32 LocalUserNum, bool bWasSuccessful, const FUniqueNetId& UserId, const FString& Error)
{
    if (bWasSuccessful)
    {
        UE_LOG(LogTemp, Log, TEXT("Amazon Login Successful! User ID: %s"), *UserId.ToString());
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Amazon Login Failed. Error: %s"), *Error);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `OnlineSubsystem` | 在线子系统基础框架，此插件的依赖项。 |

**说明**：除了对 `OnlineSubsystem` 插件的依赖外，该插件没有其他特殊模块依赖。使用者需要在自己的 `.Build.cs` 文件中添加对 `OnlineSubsystemAmazon` 模块的依赖。

```csharp
// 你的模块的 Build.cs
PublicDependencyModuleNames.AddRange(new string[] {
    "OnlineSubsystemAmazon"
});
```

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-08-13 | `65515472` | - Deprecate OnlineJsonSerializer.h | 废弃了旧的 JSON 序列化器头文件。 |
| 2024-06-24 | `f40be2d7` | Fixed some 'deprecated' FString usage. | 修复了一些已废弃的 FString 用法，属于代码现代化维护。 |
| 2023-11-17 | `b1ad5aee` | Add ShowResolveUI param to GetUserPrivilege method of identity interface. | 为身份接口的 GetUserPrivilege 方法添加了 ShowResolveUI 参数，是接口层面的小更新。 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 对引擎插件目录进行了整理或构建修复。 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 更新了内置插件的供应商链接以使用 HTTPS 协议。 |

### 维护评价

- **维护状态**：**不活跃**。该插件自创建以来，更新非常稀少，且近年来的更新主要集中在代码清理、编译修复和接口微调上，没有实质性的新功能或平台集成更新。
- **功能完整性**：**功能非常有限**。它仅实现了亚马逊平台的身份验证，缺少其他常见的在线功能（如会话、好友、排行榜等）。
- **推荐度**：**不推荐用于新项目**。该插件很可能是针对多年前特定亚马逊平台（如 Kindle 设备、Amazon Underground）的过时实现。鉴于亚马逊游戏平台（Amazon Games）的战略方向已发生改变，此插件可能已无法与当前亚马逊的登录服务正常工作。除非你有明确的、针对特定历史亚马逊平台的需求，否则建议寻找或开发更现代的解决方案。
- **警告**：该插件创建于 2016 年，已超过 **5 年没有功能性更新**，且维护活动多为被动维护。在新项目中集成前，请务必验证其与目标亚马逊 SDK 和服务的兼容性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineSubsystemAmazon)
- [官方文档](https://docs.unrealengine.com) (无特定插件文档，需查阅 Unreal Engine 在线子系统通用文档)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests) (无特定测试用例，可参考引擎通用在线子系统测试)