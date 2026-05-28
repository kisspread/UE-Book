# Online Subsystem NULL

> Access to NULL platform

| 属性 | 值 |
|---|---|
| 中文名 | 空在线子系统 |
| 分类 | Online Platform |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `OnlineSubsystemNull` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2016-07-13 |
| 年龄标签 | 🏛️ 文物（约 10 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineSubsystemNull) | |

## 用途

OnlineSubsystemNull 是一个**不连接任何真实在线服务**的在线子系统实现。它为 Unreal 的在线子系统（Online Subsystem）框架提供了一个"空壳"参考实现，所有在线接口（会话、身份、好友、排行榜、成就、商店等）均返回模拟数据或以本地/LAN 方式工作。

**核心价值**：
- **开发调试**：在没有平台 SDK（如 Steam、PlayStation、Xbox）的环境下，依然能测试多人游戏逻辑
- **LAN 局域网测试**：提供完整的 LAN 会话发现/创建/加入功能，用于本地多人联调
- **行为模拟**：通过静态配置变量（如 `bAutoLoginAtStartup`、`bRequireLoginCredentials`、`bForceOfflineMode`）模拟不同平台的登录流程差异
- **自动化测试**：作为默认的在线子系统，为引擎的多人相关功能提供无副作用的测试环境

**为什么存在**：UE 的 Online Subsystem 采用插件化架构，每个平台（Steam、EOS、PlayStation 等）各自实现接口。在编辑器开发阶段或没有接入具体平台时，需要一个"什么都不做但不会崩溃"的实现——这就是 Null 的作用。它默认启用 (`EnabledByDefault=true`)，作为回退方案确保任何使用在线子系统的代码都不会因为缺少平台实现而失败。

## 使用场景

- 你在编辑器中开发多人游戏原型，暂时没有接入任何在线平台 → 使用 Null 子系统进行 LAN 联机测试
- 你在编写依赖 `IOnlineSubsystem` 接口的游戏逻辑，需要先跑通流程 → 用 Null 子系统做本地验证
- 你在写自动化的多人功能测试，不希望依赖外部服务 → 用 Null 子系统确保测试稳定
- 你需要模拟不同平台的登录行为差异（单用户自动登录 vs 需要外部 UI 登录）→ 通过配置变量切换模式
- 你在团队中做早期原型，还没决定用哪个在线平台 → 用 Null 作为占位实现，后续只需替换子系统名称

## 蓝图用法

OnlineSubsystemNull 本身不暴露 `BlueprintCallable` 节点。它是 `IOnlineSubsystem` 接口的运行时实现，蓝图通过通用的 Online Subsystem 蓝图节点（如 `Create Session`、`Find Sessions`、`Join Session`）间接使用它，只要当前活动的在线子系统是 `NULL` 即可。

### 核心节点（通过通用 Online Subsystem 蓝图 API）

| 节点 | 说明 | 所在类 |
|---|---|---|
| Create Session | 创建 LAN 会话 | `FOnlineSessionNull` |
| Find Sessions | 通过 LAN 广播搜索会话 | `FOnlineSessionNull` |
| Join Session | 加入发现的 LAN 会话 | `FOnlineSessionNull` |
| Login | 模拟用户登录（自动或带凭证） | `FOnlineIdentityNull` |
| Read Leaderboards | 读取本地排行榜数据 | `FOnlineLeaderboardsNull` |
| Query Achievements | 从配置文件读取成就描述 | `FOnlineAchievementsNull` |

### 使用示例（蓝图描述）

**多人联机测试流程**：
1. 在 Project Settings → Online → Default Platform Service 设置为 `NULL`
2. 游戏启动时，`FOnlineIdentityNull` 自动登录本地用户（取决于 `bAutoLoginAtStartup` 配置）
3. 主机调用 **Create Session** 节点 → 创建 LAN 会话并开始广播
4. 客户端调用 **Find Sessions** 节点 → 通过 LAN Beacon 搜索到主机的会话
5. 客户端调用 **Join Session** 节点 → 通过 LAN 连接到主机
6. 双方通过 `OnCreateSessionComplete` / `OnJoinSessionComplete` 委托收到结果后，获取连接字符串开始游戏

## C++ 用法

### 头文件引入

```cpp
#include "OnlineSubsystemNull.h"
#include "OnlineSubsystem.h"
```

### 基本用法

**获取 Null 子系统实例**（来源：`Source/Public/OnlineSubsystemNull.h`）：

```cpp
// 获取当前活动的在线子系统（如果默认配置为 NULL，则返回 FOnlineSubsystemNull）
IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get();
if (OnlineSub)
{
    // 获取各接口，此时实际返回的是 Null 子系统的实现
    IOnlineIdentityPtr IdentityInterface = OnlineSub->GetIdentityInterface();
    IOnlineSessionPtr SessionInterface = OnlineSub->GetSessionInterface();
    IOnlineLeaderboardsPtr LeaderboardsInterface = OnlineSub->GetLeaderboardsInterface();
    IOnlineAchievementsPtr AchievementsInterface = OnlineSub->GetAchievementsInterface();
}
```

**显式指定 Null 子系统**：

```cpp
#include "OnlineSubsystem.h"

// 显式获取名为 NULL 的子系统
IOnlineSubsystem* NullSub = IOnlineSubsystem::Get(NULL_SUBSYSTEM);
// NULL_SUBSYSTEM 是定义的常量名 "NULL"
```

**配置 Null 子系统行为**（来源：`Source/Public/OnlineSubsystemNull.h` 中的静态变量）：

```ini
; Engine.ini 或 DefaultEngine.ini 中配置
[OnlineSubsystemNull]
bAutoLoginAtStartup=true          ; 启动时自动登录第一个用户（模拟单用户平台）
bSupportExternalUI=false           ; 是否支持外部 UI 接口
bRequireShowLoginUI=false          ; 登录是否需要调用 ShowLoginUI
bRequireLoginCredentials=false     ; 登录是否需要用户名密码
bAddUserNumToNullId=false          ; 用户名是否包含本地玩家编号
bForceStableNullId=false           ; 是否使用稳定的 Null ID（而非随机）
bForceOfflineMode=false            ; 是否强制离线模式（所有查询返回失败）
bOnlineRequiresSecondLogin=false   ; 第一次登录仅本地，第二次才在线
```

### 进阶用法

**LAN 会话创建与搜索**（来源：`Source/Private/OnlineSessionInterfaceNull.h`）：

```cpp
// 创建会话（主机端）
FOnlineSessionSettings SessionSettings;
SessionSettings.bIsLANMatch = true;
SessionSettings.NumPublicConnections = 4;
SessionSettings.bShouldAdvertise = true;
SessionSettings.bUsesPresence = false;

IOnlineSessionPtr SessionInterface = OnlineSub->GetSessionInterface();
SessionInterface->AddOnCreateSessionCompleteDelegate_Handle(
    FOnCreateSessionCompleteDelegate::CreateLambda(
        [](FName SessionName, bool bWasSuccessful) {
            UE_LOG(LogOnline, Log, TEXT("Session %s create: %s"),
                *SessionName.ToString(), bWasSuccessful ? TEXT("Success") : TEXT("Failed"));
        }));

SessionInterface->CreateSession(0, NAME_GameSession, SessionSettings);
```

```cpp
// 搜索会话（客户端端）
TSharedRef<FOnlineSessionSearch> SearchSettings = MakeShared<FOnlineSessionSearch>();
SearchSettings->bIsLanQuery = true;
SearchSettings->MaxSearchResults = 10;

SessionInterface->AddOnFindSessionsCompleteDelegate_Handle(
    FOnFindSessionsCompleteDelegate::CreateLambda(
        [SessionInterface, SearchSettings](bool bWasSuccessful) {
            if (bWasSuccessful && SearchSettings->SearchResults.Num() > 0)
            {
                // 加入第一个找到的会话
                SessionInterface->JoinSession(0, NAME_GameSession,
                    SearchSettings->SearchResults[0]);
            }
        }));

SessionInterface->FindSessions(0, SearchSettings);
```

**自定义成就配置**（来源：`Source/Private/OnlineAchievementsInterfaceNull.h`）：

```ini
; 在 Engine.ini 中配置模拟成就
[OnlineSubsystemNull]
Achievement_0_Id=FirstKill
Achievement_0_Title=First Blood
Achievement_0_LockedDesc=Get your first kill
Achievement_0_UnlockedDesc=You got your first kill!
Achievement_0_bIsHidden=false
Achievement_1_Id=WinMatch
Achievement_1_Title=Victory
Achievement_1_LockedDesc=Win a match
Achievement_1_UnlockedDesc=You won a match!
Achievement_1_bIsHidden=false
```

## Demo 示例

一个完整的最小示例：通过 Null 子系统创建 LAN 会话并搜索。

```cpp
// MyOnlineTestComponent.h
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "OnlineSubsystem.h"
#include "OnlineSessionSettings.h"
#include "Interfaces/OnlineSessionInterface.h"
#include "MyOnlineTestComponent.generated.h"

UCLASS(ClassGroup=(Online), meta=(BlueprintSpawnableComponent))
class UMyOnlineTestComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    /** 创建 LAN 会话（主机端） */
    UFUNCTION(BlueprintCallable, Category = "Online")
    void HostSession();

    /** 搜索 LAN 会话（客户端端） */
    UFUNCTION(BlueprintCallable, Category = "Online")
    void FindAndJoinSession();

private:
    void OnCreateSessionComplete(FName SessionName, bool bWasSuccessful);
    void OnFindSessionsComplete(bool bWasSuccessful);
    void OnJoinSessionComplete(FName SessionName, EOnJoinSessionCompleteResult::Type Result);

    TSharedPtr<FOnlineSessionSearch> SessionSearch;
    FDelegateHandle CreateHandle;
    FDelegateHandle FindHandle;
    FDelegateHandle JoinHandle;
};
```

```cpp
// MyOnlineTestComponent.cpp
#include "MyOnlineTestComponent.h"

void UMyOnlineTestComponent::HostSession()
{
    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get();
    if (!OnlineSub) return;

    IOnlineSessionPtr Sessions = OnlineSub->GetSessionInterface();
    if (!Sessions.IsValid()) return;

    CreateHandle = Sessions->AddOnCreateSessionCompleteDelegate_Handle(
        FOnCreateSessionCompleteDelegate::CreateUObject(
            this, &UMyOnlineTestComponent::OnCreateSessionComplete));

    FOnlineSessionSettings Settings;
    Settings.bIsLANMatch = true;
    Settings.NumPublicConnections = 4;
    Settings.bShouldAdvertise = true;
    Settings.bUsesPresence = false;

    Sessions->CreateSession(0, NAME_GameSession, Settings);
}

void UMyOnlineTestComponent::FindAndJoinSession()
{
    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get();
    if (!OnlineSub) return;

    IOnlineSessionPtr Sessions = OnlineSub->GetSessionInterface();
    if (!Sessions.IsValid()) return;

    SessionSearch = MakeShared<FOnlineSessionSearch>();
    SessionSearch->bIsLanQuery = true;
    SessionSearch->MaxSearchResults = 10;

    FindHandle = Sessions->AddOnFindSessionsCompleteDelegate_Handle(
        FOnFindSessionsCompleteDelegate::CreateUObject(
            this, &UMyOnlineTestComponent::OnFindSessionsComplete));

    Sessions->FindSessions(0, SessionSearch.ToSharedRef());
}

void UMyOnlineTestComponent::OnCreateSessionComplete(FName SessionName, bool bWasSuccessful)
{
    IOnlineSubsystem::Get()->GetSessionInterface()
        ->ClearOnCreateSessionCompleteDelegate_Handle(CreateHandle);

    UE_LOG(LogTemp, Log, TEXT("Host session '%s': %s"),
        *SessionName.ToString(),
        bWasSuccessful ? TEXT("SUCCESS") : TEXT("FAILED"));
}

void UMyOnlineTestComponent::OnFindSessionsComplete(bool bWasSuccessful)
{
    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get();
    IOnlineSessionPtr Sessions = OnlineSub->GetSessionInterface();
    Sessions->ClearOnFindSessionsCompleteDelegate_Handle(FindHandle);

    if (bWasSuccessful && SessionSearch.IsValid() && SessionSearch->SearchResults.Num() > 0)
    {
        UE_LOG(LogTemp, Log, TEXT("Found %d sessions, joining first one"),
            SessionSearch->SearchResults.Num());

        JoinHandle = Sessions->AddOnJoinSessionCompleteDelegate_Handle(
            FOnJoinSessionCompleteDelegate::CreateUObject(
                this, &UMyOnlineTestComponent::OnJoinSessionComplete));

        Sessions->JoinSession(0, NAME_GameSession, SessionSearch->SearchResults[0]);
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("No sessions found"));
    }
}

void UMyOnlineTestComponent::OnJoinSessionComplete(FName SessionName, EOnJoinSessionCompleteResult::Type Result)
{
    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get();
    IOnlineSessionPtr Sessions = OnlineSub->GetSessionInterface();
    Sessions->ClearOnJoinSessionCompleteDelegate_Handle(JoinHandle);

    if (Result == EOnJoinSessionCompleteResult::Success)
    {
        FString ConnectString;
        if (Sessions->GetResolvedConnectString(SessionName, ConnectString))
        {
            UE_LOG(LogTemp, Log, TEXT("Connect to: %s"), *ConnectString);
            // GetWorld()->GetFirstPlayerController()->ClientTravel(ConnectString, ETravelType::TRAVEL_Absolute);
        }
    }
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。插件自身依赖 `OnlineSubsystem` 和 `OnlineSubsystemUtils` 插件（已在 `.uplugin` 的 Plugins 声明中自动启用）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式说明符不匹配问题 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移至 UE_LOGF |
| 2026-03-26 | `03bb7402` | UE: Fix OSS Null not finding multiple LAN sessions from a single host. | 修复 Null 子系统无法发现同一主机的多个 LAN 会话的问题 |
| 2026-02-09 | `8e8bb266` | [Hotfix] Fixing a bug in the perforce hotfix implementation that would cause us to place the downloa | 修复 Perforce 热修复文件下载路径的 Bug |
| 2026-02-03 | `0a3bf18a` | [TitleFile][Hotfix] Adding support for TitleFilePath=p4://<path> (windows only) to fetch the files f | TitleFile 接口新增支持 p4:// 路径从 Perforce 拉取文件（仅 Windows） |

### 维护评价

OnlineSubsystemNull 是一个**活跃维护中**的核心基础设施插件：

- **历史**：2016 年随 Online Subsystem 插件化重构一并创建，已存在约 10 年
- **近期活跃**：2026 年有多次实质性更新，包括 LAN 会话发现修复、日志迁移、TitleFile 新功能等，说明仍在持续使用和改进
- **性质稳定**：作为 Null 实现，其核心功能长期不变，更新主要是引擎层面的适配和小 Bug 修复
- **推荐使用**：这是 UE 多人功能开发的**基础设施级插件**，在没有真实平台 SDK 的场景下是唯一选择。默认启用，无需额外配置即可开始多人功能开发

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineSubsystemNull)
- [官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/online-subsystem-in-unreal-engine)