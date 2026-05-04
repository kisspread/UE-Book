# Online Subsystem Tencent

> Access to Tencent platform

| 属性 | 值 |
|---|---|
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `OnlineSubsystemTencent` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-04-30 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineSubsystemTencent) | |

## 用途

OnlineSubsystemTencent 是 Unreal Engine 对腾讯平台（WeGame）的在线子系统实现。它通过腾讯的 **Rail SDK**（也叫 WeGame SDK）提供身份认证、会话管理、好友系统、在线状态、外部 UI、商店和购买等在线服务接口。

该插件有两个运行模式：
- **仅 TencentSDK 模式**（`WITH_TENCENTSDK=1, WITH_TENCENT_RAIL_SDK=0`）：仅提供基础身份认证（TCLS 登录支持）和会话接口（TSS 反作弊处理），用于**专用服务器**（Dedicated Server）场景。
- **Rail SDK 模式**（`WITH_TENCENT_RAIL_SDK=1`）：完整功能模式，额外提供好友列表、在线状态（Presence）、外部 UI、用户查询、消息过滤、商店和购买接口。仅在**非专用服务器**客户端使用。

插件默认不启用（`EnabledByDefault: false`），需要手动在项目配置中启用，并且仅支持 **Win64** 和 **Linux** 平台。使用前还需要在 Engine.ini 中配置 `RailGameId`。

## 使用场景

- 你的游戏要在 **WeGame** 平台发行 → 使用此插件对接腾讯在线服务
- 你需要腾讯平台的**身份认证**（TCLS 登录流程）→ 通过 `IOnlineIdentity` 接口
- 你需要实现腾讯平台的**防沉迷系统**（Anti-Addiction）→ 插件集成了 `PlayTimeLimit` 模块
- 你需要通过 WeGame 进行**游戏内购买**→ 通过 `IOnlinePurchase` 和 `IOnlineStoreV2` 接口
- 你只需要**专用服务器端的反作弊**（TSS），不需要完整 Rail SDK → 仅启用 TencentSDK 模式

## 蓝图用法

该插件**没有暴露任何 BlueprintCallable 函数**。所有功能通过标准的 Online Subsystem 接口（`IOnlineIdentity`、`IOnlineSession` 等）以 C++ 方式访问。

如果需要在蓝图中使用腾讯在线服务，应通过其他插件（如 Advanced Sessions Plugin）间接调用 OnlineSubsystem 接口。

## C++ 用法

### 头文件引入

```cpp
#include "OnlineSubsystem.h"
#include "OnlineSubsystemTencent.h"
#include "OnlineIdentityTencent.h"
#include "Interfaces/OnlineSessionInterface.h"
#include "Interfaces/OnlineFriendsInterface.h"
```

### 获取子系统实例

```cpp
// 通过 Online Subsystem 框架获取 Tencent 子系统
IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(TENCENT_SUBSYSTEM);
if (OnlineSub)
{
    // 获取身份接口
    IOnlineIdentityPtr Identity = OnlineSub->GetIdentityInterface();
    
    // 获取会话接口
    IOnlineSessionPtr Sessions = OnlineSub->GetSessionInterface();
    
    // 获取好友接口（仅 Rail SDK 模式可用）
    IOnlineFriendsPtr Friends = OnlineSub->GetFriendsInterface();
}
```

### 身份认证（Login）

```cpp
// 获取身份接口
IOnlineIdentityPtr Identity = OnlineSub->GetIdentityInterface();

// 绑定登录完成回调
Identity->AddOnLoginCompleteDelegate_Handle(
    0,  // LocalUserNum
    FOnLoginCompleteDelegate::CreateLambda(
        [](int32 LocalUserNum, bool bWasSuccessful, const FUniqueNetId& UserId, const FString& Error)
        {
            if (bWasSuccessful)
            {
                UE_LOG(LogTemp, Log, TEXT("Login successful: %s"), *UserId.ToString());
            }
        }
    )
);

// 发起登录（TCLS 模式下使用 Type 和 Token 字段传递凭据）
FOnlineAccountCredentials Credentials;
Credentials.Type = TEXT("TCLS");
Credentials.Token = TEXT("...");
Identity->Login(0, Credentials);
```

### 会话管理

```cpp
// 创建会话
IOnlineSessionPtr Sessions = OnlineSub->GetSessionInterface();

// 绑定会话创建完成回调
Sessions->AddOnCreateSessionCompleteDelegate_Handle(
    FOnCreateSessionCompleteDelegate::CreateLambda(
        [](FName SessionName, bool bWasSuccessful)
        {
            UE_LOG(LogTemp, Log, TEXT("Session %s created: %d"), *SessionName.ToString(), bWasSuccessful);
        }
    )
);

FOnlineSessionSettings SessionSettings;
SessionSettings.bIsLANMatch = false;
SessionSettings.NumPublicConnections = 4;
SessionSettings.bShouldAdvertise = true;
SessionSettings.bUsesPresence = true;

Sessions->CreateSession(0, NAME_GameSession, SessionSettings);
```

### 好友列表查询（Rail SDK 模式）

```cpp
IOnlineFriendsPtr Friends = OnlineSub->GetFriendsInterface();

Friends->AddOnReadFriendsListCompleteDelegate_Handle(
    0,  // LocalUserNum
    FOnReadFriendsListComplete::CreateLambda(
        [](int32 LocalUserNum, bool bWasSuccessful, const FString& ListName, const FString& ErrorStr)
        {
            if (bWasSuccessful)
            {
                IOnlineFriendsPtr FriendsInt = IOnlineSubsystem::Get()->GetFriendsInterface();
                TArray<TSharedRef<FOnlineFriend>> FriendsList;
                FriendsInt->GetFriendsList(0, ListName, FriendsList);
                
                for (const auto& Friend : FriendsList)
                {
                    UE_LOG(LogTemp, Log, TEXT("Friend: %s"), *Friend->GetDisplayName());
                }
            }
        }
    )
);

Friends->ReadFriendsList(0, TEXT("default"));
```

### 在线状态查询（Rail SDK 模式）

```cpp
IOnlinePresencePtr Presence = OnlineSub->GetPresenceInterface();

// 查询好友的在线状态
Presence->QueryPresence(FriendUserId,
    IOnlinePresence::FOnPresenceTaskCompleteDelegate::CreateLambda(
        [](const FUniqueNetId& UserId, bool bWasSuccessful)
        {
            if (bWasSuccessful)
            {
                IOnlinePresencePtr PresenceInt = IOnlineSubsystem::Get()->GetPresenceInterface();
                TSharedPtr<FOnlineUserPresence> UserPresence;
                if (PresenceInt->GetCachedPresence(UserId, UserPresence) == EOnlineCachedResult::Success)
                {
                    UE_LOG(LogTemp, Log, TEXT("User %s is %s"),
                        *UserId.ToString(),
                        UserPresence->bIsOnline ? TEXT("Online") : TEXT("Offline"));
                }
            }
        }
    )
);
```

### 防沉迷系统（Anti-Addiction）

```cpp
// 防沉迷通过 PlayTimeLimit 模块集成
// 当需要显示防沉迷对话框时，会触发 OnAASDialog 委托
FOnlineSubsystemTencent* TencentSub = static_cast<FOnlineSubsystemTencent*>(OnlineSub);

TencentSub->AddOnAASDialogDelegate_Handle(
    FOnAASDialogDelegate::CreateLambda(
        [](const FString& DialogTitle, const FString& DialogText, const FString& ButtonText)
        {
            // 显示防沉迷提示对话框
            UE_LOG(LogTemp, Warning, TEXT("AAS: %s - %s"), *DialogTitle, *DialogText);
        }
    )
);
```

### 控制台命令

该插件注册了以下控制台命令用于调试：

```
SESSION DUMPMETADATA    - 转储会话元数据（从邀请命令行键获取）
SESSION METAINVITE      - 基于本地用户会话数据获取会话邀请
PRESENCE REPORTPLAYERS  - 报告一起游玩的玩家
PRESENCE DUMP           - 转储本地用户和好友的在线状态
USERS DUMPALL           - 转储所有缓存的用户信息
USERS QUERYUSER <id>    - 查询指定用户信息
USERS QUERYALLFRIENDS   - 查询所有好友信息
FRIENDS DUMP            - 转储好友列表
RAILSDKWRAPPER <cmd>    - Rail SDK 包装器命令
DUMPKEYS [userid]       - 转储元数据缓存键值对
```

## Demo 示例

### Build.cs 依赖配置

```csharp
using UnrealBuildTool;

public class MyGame : ModuleRules
{
    public MyGame(ReadOnlyTargetRules Target) : base(Target)
    {
        PublicDependencyModuleNames.AddRange(new string[]
        {
            "Core",
            "CoreUObject",
            "Engine",
            "OnlineSubsystem",
            "OnlineSubsystemUtils"
        });
        
        // 添加对 Tencent 子系统的支持
        PrivateDependencyModuleNames.Add("OnlineSubsystemTencent");
    }
}
```

### GameEngine.ini 配置

```ini
[OnlineSubsystem]
DefaultPlatformService=Tencent

[OnlineSubsystemTencent]
; WeGame 的 Rail Game ID，从 WeGame 开发者后台获取
RailGameId=12345678
```

### 完整登录流程示例

```cpp
// MyGameInstance.h
#pragma once

#include "Engine/GameInstance.h"
#include "OnlineSubsystem.h"
#include "OnlineSubsystemTencent.h"
#include "Interfaces/OnlineIdentityInterface.h"
#include "MyGameInstance.generated.h"

UCLASS()
class UMyGameInstance : public UGameInstance
{
    GENERATED_BODY()

public:
    virtual void Init() override;

    void LoginToTencent();
    
private:
    void OnLoginComplete(int32 LocalUserNum, bool bWasSuccessful, 
                         const FUniqueNetId& UserId, const FString& Error);
    
    FDelegateHandle LoginDelegateHandle;
};

// MyGameInstance.cpp
#include "MyGameInstance.h"

void UMyGameInstance::Init()
{
    Super::Init();
    LoginToTencent();
}

void UMyGameInstance::LoginToTencent()
{
    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(FName(TEXT("Tencent")));
    if (!OnlineSub)
    {
        UE_LOG(LogTemp, Error, TEXT("Tencent Online Subsystem not found!"));
        return;
    }

    IOnlineIdentityPtr Identity = OnlineSub->GetIdentityInterface();
    if (!Identity.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Identity interface not available!"));
        return;
    }

    LoginDelegateHandle = Identity->AddOnLoginCompleteDelegate_Handle(
        0, FOnLoginCompleteDelegate::CreateUObject(this, &UMyGameInstance::OnLoginComplete));

    // 通过 WeGame 启动时会自动处理登录
    // 或者使用 AutoLogin
    Identity->AutoLogin(0);
}

void UMyGameInstance::OnLoginComplete(int32 LocalUserNum, bool bWasSuccessful,
                                       const FUniqueNetId& UserId, const FString& Error)
{
    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(FName(TEXT("Tencent")));
    IOnlineIdentityPtr Identity = OnlineSub->GetIdentityInterface();
    
    Identity->ClearOnLoginCompleteDelegate_Handle(0, LoginDelegateHandle);
    
    if (bWasSuccessful)
    {
        FString PlayerName = Identity->GetPlayerNickname(0);
        UE_LOG(LogTemp, Log, TEXT("Tencent login successful: %s (%s)"), 
               *PlayerName, *UserId.ToString());
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Tencent login failed: %s"), *Error);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础引擎功能 |
| `CoreUObject` | UObject 系统 |
| `Sockets` | 网络通信基础（私有依赖） |
| `HTTP` | HTTP 请求支持（私有依赖） |
| `Json` | JSON 序列化（私有依赖） |
| `OnlineSubsystem` | 在线子系统基础框架（私有依赖） |
| `PacketHandler` | 网络包处理（私有依赖） |
| `PlayTimeLimit` | 游戏时长限制/防沉迷系统（私有依赖） |
| `Engine` | 引擎核心（条件依赖，仅在 `bCompileAgainstEngine` 时） |
| `OnlineSubsystemUtils` | 在线子系统工具（条件依赖，仅在 `bCompileAgainstEngine` 时） |

### 插件依赖

| 插件 | 用途 |
|---|---|
| `OnlineSubsystem` | 提供 `IOnlineSubsystem` 基础框架 |
| `OnlineSubsystemUtils` | 提供在线子系统工具类 |
| `OnlineFramework` | 提供在线框架支持 |

### 第三方 SDK 依赖

| SDK | 用途 |
|---|---|
| `WeGame`（Tencent/WeGame） | WeGame Rail SDK 动态库，提供完整平台功能 |
| `Tencent`（Restricted/NotForLicensees） | 腾讯内部 SDK，用于 TencentSDK 模式（非公开） |

## 接口实现清单

该插件实现了以下 `IOnlineSubsystem` 接口：

| 接口 | 实现类 | 可用模式 | 说明 |
|---|---|---|---|
| `IOnlineIdentity` | `FOnlineIdentityTencent` | 全部 | TCLS 登录、身份管理 |
| `IOnlineSession` | `FOnlineSessionTencent` / `FOnlineSessionTencentRail` | 全部 | 会话创建/加入/销毁，Rail SDK 模式支持邀请和元数据 |
| `IOnlineFriends` | `FOnlineFriendsTencent` | Rail SDK | 好友列表、最近玩家、屏蔽列表 |
| `IOnlinePresence` | `FOnlinePresenceTencent` | Rail SDK | 在线状态查询/设置 |
| `IOnlineExternalUI` | `FOnlineExternalUITencent` | Rail SDK | 好友 UI、邀请 UI、成就 UI、商店 UI |
| `IOnlineUser` | `FOnlineUserTencent` | Rail SDK | 用户信息查询 |
| `IOnlineStoreV2` | `FOnlineStoreTencent` | Rail SDK | 商品目录和优惠查询 |
| `IOnlinePurchase` | `FOnlinePurchaseTencent` | Rail SDK | 购买和收据管理 |
| `IMessageSanitizer` | `FMessageSanitizerTencent` | Rail SDK | 聊天消息过滤/敏感词过滤 |

以下接口返回 `nullptr`（未实现）：
- `IOnlineParty`、`IOnlineGroups`、`IOnlineSharedCloud`、`IOnlineUserCloud`
- `IOnlineEntitlements`、`IOnlineLeaderboards`、`IOnlineVoice`
- `IOnlineTime`、`IOnlineTitleFile`、`IOnlineEvents`
- `IOnlineAchievements`、`IOnlineSharing`、`IOnlineMessage`
- `IOnlineChat`、`IOnlineStats`、`IOnlineTurnBased`、`IOnlineTournament`

## 关键类型

### FUniqueNetIdRail

Rail SDK 特有的用户 ID 实现，基于 `uint64` 类型的 `rail::RailID`。用于标识 WeGame 平台用户。

```cpp
// 从字符串创建
FUniqueNetIdRailRef UserId = FUniqueNetIdRail::Create(TEXT("123456789"));

// 转换为 RailID
rail::RailID RailId = static_cast<rail::RailID>(*UserId);

// 转换为字符串
FString IdStr = UserId->ToString(); // "123456789"
```

### FMetadataPropertiesRail

用于存储用户在线状态和会话元数据的键值对集合。

```cpp
FMetadataPropertiesRail Metadata;
Metadata.Add(TEXT("Status"), FVariantData(FString(TEXT("In Game"))));
Metadata.Add(TEXT("Level"), FVariantData(42));
```

### Metadata 键常量

在 `MetadataKeysRail.h` 中定义的元数据键：

| 常量 | 值 | 类型 | 说明 |
|---|---|---|---|
| `RAIL_PRESENCE_STATUS_KEY` | `"Status"` | FString | 在线状态消息 |
| `RAIL_PRESENCE_APPID_KEY` | `"AppId"` | FString | 用户运行的应用 ID |
| `RAIL_PRESENCE_SESSION_ID_KEY` | `"PresenceSessionId"` | FString | 会话 ID |
| `RAIL_PRESENCE_PRESENCEBITS_KEY` | `"PresenceBits"` | uint32 | 基本状态位掩码 |
| `RAIL_SESSION_ID_KEY` | `"SessionId"` | FString | 会话 ID |
| `RAIL_SESSION_OWNING_USER_ID_KEY` | `"OwningUserId"` | uint64 | 会话拥有者 ID |
| `RAIL_SESSION_SESSIONBITS_KEY` | `"SessionBits"` | uint32 | 会话标志位 |
| `RAIL_SESSION_BUILDUNIQUEID_KEY` | `"BuildUniqueId"` | int32 | 构建 ID |

## 架构概览

```
FOnlineSubsystemTencent (主子系统类)
├── FOnlineIdentityTencent          ← 身份认证 (TCLS)
├── FOnlineSessionTencent           ← 基础会话接口
│   └── FOnlineSessionTencentRail   ← Rail SDK 会话 (邀请/元数据)
├── FOnlineFriendsTencent           ← 好友列表 [Rail SDK]
├── FOnlinePresenceTencent          ← 在线状态 [Rail SDK]
├── FOnlineExternalUITencent        ← 外部 UI [Rail SDK]
├── FOnlineUserTencent              ← 用户查询 [Rail SDK]
├── FMessageSanitizerTencent        ← 消息过滤 [Rail SDK]
├── FOnlineStoreTencent             ← 商店 [Rail SDK]
├── FOnlinePurchaseTencent          ← 购买 [Rail SDK]
├── FOnlinePlayTimeLimitUserTencent ← 防沉迷 [Rail SDK]
└── FOnlineAsyncTaskManagerTencent  ← 异步任务管理器
    └── RailSdkWrapper              ← Rail SDK 单例包装器
```

## 异步任务系统

所有 Rail SDK 操作都通过异步任务执行。基础类 `FOnlineAsyncTaskRail` 继承自 `FOnlineAsyncTaskBasic` 和 `rail::IRailEvent`，通过事件驱动模式处理 Rail SDK 回调。

主要异步任务：

| 任务类 | 说明 |
|---|---|
| `FOnlineAsyncTaskRailAcquireSessionTicket` | 获取会话票据（登录验证） |
| `FOnlineAsyncTaskRailSetUserMetadata` | 设置用户元数据 |
| `FOnlineAsyncTaskRailSetUserPresence` | 设置用户在线状态 |
| `FOnlineAsyncTaskRailSetSessionMetadata` | 设置会话元数据 |
| `FOnlineAsyncTaskRailGetUserMetadata` | 获取用户元数据 |
| `FOnlineAsyncTaskRailGetUserPresence` | 获取用户在线状态 |
| `FOnlineAsyncTaskRailGetInviteCommandline` | 获取邀请命令行 |
| `FOnlineAsyncTaskRailGetUserInvite` | 获取用户邀请信息 |
| `FOnlineAsyncTaskRailShowFloatingWindow` | 显示浮动窗口（好友/成就等） |
| `FOnlineAsyncTaskRailReportPlayedWithUsers` | 报告一起游玩的玩家 |

任务超时时间：Shipping 构建 20 秒，其他构建 80 秒。

## 维护状态

### 近期更新

| 日期 | Commit | 内容 |
|---|---|---|
| 2025-09-12 | `ce6ff392ddca` | 修复 `FTSTicker::RemoveTicker` 的 `nodiscard` 属性警告 |
| 2025-08-13 | `655154721295` | 废弃 `OnlineJsonSerializer.h` |
| 2025-06-11 | `afdf8d7528de` | 将部分 `FORCEINLINE` 替换为 `inline` |

### 维护评价

- **创建时间**：2019 年 4 月，约 7 年历史
- **最近更新**：2025 年 9 月，最近的更新均为编译警告修复和代码风格调整，**没有功能性更新**
- **维护状态**：**维护不活跃**。最近 3 次提交均为机械性代码清理（`nodiscard` 修复、`FORCEINLINE` 替换、头文件废弃），没有任何功能增强或 bug 修复
- **平台依赖**：强依赖腾讯 WeGame Rail SDK，SDK 位于 `ThirdParty/Tencent/WeGame` 和 `Restricted/NotForLicensees/Source/ThirdParty/Tencent`，外部开发者通常无法获取
- **使用限制**：该插件主要面向腾讯/WeGame 平台发行的游戏，普通开发者使用场景有限
- **是否推荐**：如果游戏不在 WeGame 平台发行，无需使用此插件。如果需要，建议确认 Rail SDK 的可用性和兼容性

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineSubsystemTencent)
- [WeGame 开发者文档](https://www.wegame.com.cn/)（腾讯 WeGame 平台）
