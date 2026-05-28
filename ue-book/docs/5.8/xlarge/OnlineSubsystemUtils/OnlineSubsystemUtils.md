# Online Subsystem Utils

> Shared code for interacting online service and online subsystem implementations.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 在线子系统工具 |
| 分类 | Online Platform |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（本地化资源） |
| 模块 | `OnlineSubsystemUtils` (Runtime), `OnlineBlueprintSupport` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2016-07-13 |
| 年龄标签 | 🏛️ 文物（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineSubsystemUtils) | |

## 用途

OnlineSubsystemUtils 是 UE 在线服务框架的**核心基础设施层**，提供三大关键能力：

1. **引擎与在线子系统之间的桥接**：`UOnlineEngineInterfaceImpl` / `UOnlineServicesEngineInterfaceImpl` 实现了 `UOnlineEngineInterface` 抽象，将引擎层（Session、Identity、Voice 等）的请求路由到正确的在线子系统实例。支持 PIE 多实例场景下的子系统隔离。

2. **底层网络传输**：`UIpNetDriver` / `UIpConnection` 提供基于 IP Socket 的完整网络驱动实现，包括地址解析（DNS）、Socket 重建、接收线程、NAT 穿透等，是 UE 所有基于 UDP 的在线通信的基石。

3. **派对/观众预约系统（Beacon）**：提供 `APartyBeaconHost/Client` 和 `ASpectatorBeaconHost/Client`，用于在专用服务器上管理玩家席位预留，支持团队分配、跨平台限制、竞技完整性等。

**为什么存在**：OnlineSubsystem（如 Steam、EOS）只定义接口，实际的引擎集成逻辑（PIE 支持、Beacon、蓝图代理、IP 网络驱动）都在本插件中。所有使用在线功能的 UE 项目本质上都依赖这个插件。

## 使用场景

- 你需要创建多人游戏房间 → 使用 `UCreateSessionCallbackProxy` 蓝图代理
- 你需要实现派对系统（一组玩家一起进入专用服务器） → 使用 `APartyBeaconHost` / `APartyBeaconClient`
- 你需要在专用服务器上管理观众席位预留 → 使用 `ASpectatorBeaconHost` / `ASpectatorBeaconClient`
- 你需要通过蓝图查询排行榜/成就 → 使用 `ULeaderboardQueryCallbackProxy` / `UAchievementBlueprintLibrary`
- 你需要实现游戏内购买（IAP）→ 使用 `UInAppPurchaseCheckoutCallbackProxy` 等代理
- 你需要实现回合制匹配 → 使用 `UFindTurnBasedMatchCallbackProxy`
- 你需要在代码中获取当前世界的在线子系统 → 使用 `Online::GetSubsystem(World)`
- 你需要在 PIE 中测试多人在线功能 → 本插件提供完整的 PIE 在线登录支持

## 文档结构

本插件包含 189 个源文件，按功能划分为以下子模块：

| 子模块 | 说明 | 文档 |
|---|---|---|
| 核心接口与桥接 | IOnlineSubsystemUtils、Online:: 命名空间、EngineInterface | 本文 |
| IP 网络驱动 | UIpNetDriver、UIpConnection、地址解析 | [IPNetworking.md](IPNetworking.md) |
| Voice 语音系统 | 语音引擎、语音包缓冲、VoIP 组件 | [VoiceSystem.md](VoiceSystem.md) |
| Beacon 预约系统 | Party/Spectator Beacon Host/Client/State | [BeaconSystem.md](BeaconSystem.md) |
| 蓝图代理 | Session、Leaderboard、Achievement、IAP、TurnBased 代理 | [BlueprintProxies.md](BlueprintProxies.md) |

## 蓝图用法

### 核心节点 — Session 管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateSession` | 创建在线会话 | `UCreateSessionCallbackProxy` |
| `FindSessions` | 搜索在线会话 | `UFindSessionsCallbackProxy` |

### 核心节点 — 成就与排行榜

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetCachedAchievementProgress` | 获取已缓存的成就进度 | `UAchievementBlueprintLibrary` |
| `GetCachedAchievementDescription` | 获取成就描述信息 | `UAchievementBlueprintLibrary` |
| `WriteProgress` | 写入成就进度 | `UAchievementWriteCallbackProxy` |
| `CreateProxyObjectForIntQuery` | 查询排行榜数值 | `ULeaderboardQueryCallbackProxy` |
| `WriteLeaderboardInteger` | 写入排行榜整数值 | `ULeaderboardBlueprintLibrary` |

### 核心节点 — 应用内购买

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Start an In-App Purchase` | 发起购买 | `UInAppPurchaseCheckoutCallbackProxy` |
| `Get known In-App Receipts` | 获取已知收据 | `UInAppPurchaseReceiptsCallbackProxy` |
| `Query for Owned In-App Products` | 查询已拥有产品 | `UInAppPurchaseReceiptsCallbackProxy` |
| `Restore Owned In-App Products` | 恢复已购买产品 | `UInAppPurchaseReceiptsCallbackProxy` |
| `Read In App Purchase Information2` | 查询产品信息（已废弃） | `UInAppPurchaseQueryCallbackProxy2` |

### 核心节点 — 回合制

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FindTurnBasedMatch` | 寻找回合制匹配 | `UFindTurnBasedMatchCallbackProxy` |
| `EndMatch` | 结束回合制比赛 | `UEndMatchCallbackProxy` |
| `GetIsMyTurn` | 是否轮到当前玩家 | `UTurnBasedBlueprintLibrary` |
| `GetMyPlayerIndex` | 获取当前玩家索引 | `UTurnBasedBlueprintLibrary` |

### 使用示例 — 创建并搜索会话

**创建会话**：在蓝图中拖出 `CreateSession` 节点，连接 PlayerController、设置 PublicConnections 和 LAN 参数，将 OnSuccess/OnFailure 引脚分别连到后续逻辑。

**搜索会话**：使用 `FindSessions` 节点，返回 `FBlueprintSessionResult` 数组，可用 `GetServerName`、`GetPingInMs`、`GetCurrentPlayers`、`GetMaxPlayers` 提取信息。

## C++ 用法

### 头文件引入

```cpp
#include "OnlineSubsystemUtils.h"
```

### 基本用法 — 获取在线子系统

通过 `Online::` 命名空间获取当前世界的在线子系统（PIE 感知）：

```cpp
// 来源: Public/OnlineSubsystemUtils.h
#include "OnlineSubsystemUtils.h"

void UMyClass::DoSomething(UWorld* World)
{
    // 获取默认在线子系统
    IOnlineSubsystem* OSS = Online::GetSubsystem(World);
    if (OSS)
    {
        // 获取各种接口
        IOnlineSessionPtr SessionInt = OSS->GetSessionInterface();
        IOnlineIdentityPtr IdentityInt = OSS->GetIdentityInterface();
        IOnlineFriendsPtr FriendsInt = OSS->GetFriendsInterface();
    }
    
    // 使用便捷宏自动获取接口
    IOnlineSessionPtr SessionInt = Online::GetSessionInterface(World);
    IOnlineIdentityPtr IdentityInt = Online::GetIdentityInterface(World);
}
```

### 基本用法 — IOnlineSubsystemUtils 工具接口

```cpp
// 来源: Public/OnlineSubsystemUtils.h
IOnlineSubsystemUtils* Utils = Online::GetUtils();
if (Utils)
{
    // 创建用于传输层的唯一ID（仅用于网络复制，非通用ID创建）
    FUniqueNetIdPtr ForeignId = Utils->CreateForeignUniqueNetId(IdString, FName("Steam"));
    
    // 获取子系统的复制哈希（用于跨平台网络传输）
    uint8 Hash = Utils->GetReplicationHashForSubsystem(FName("Steam"));
    FName SubsystemName = Utils->GetSubsystemFromReplicationHash(Hash);
}
```

### 基本用法 — 获取语音相关辅助函数

```cpp
// 来源: Public/OnlineSubsystemUtils.h
// 创建语音音频组件
UAudioComponent* AudioComp = CreateVoiceAudioComponent(SampleRate, NumChannels);

// 创建语音合成组件（用于远程语音播放）
UVoipListenerSynthComponent* SynthComp = CreateVoiceSynthComponent(World, SampleRate);

// 获取语音聊天团队ID
uint64 BaseId = GetBaseVoiceChatTeamId(World);
uint64 TeamId = GetVoiceChatTeamId(BaseId, TeamIndex);
```

### 进阶用法 — PIE 在线登录

```cpp
// 来源: Private/OnlineEngineInterfaceImpl.h (PIE 相关函数)
#if WITH_EDITOR
IOnlineSubsystemUtils* Utils = Online::GetUtils();
if (Utils && Utils->SupportsOnlinePIE())
{
    // 启用 PIE 在线功能
    Utils->SetShouldTryOnlinePIE(true);
    
    int32 NumLogins = Utils->GetNumPIELogins();
    for (int32 i = 0; i < NumLogins; ++i)
    {
        TArray<FOnlineAccountCredentials> Logins;
        Utils->GetPIELogins(Logins);
        // 使用 Logins[i] 进行 PIE 登录
    }
}
#endif
```

### 进阶用法 — 静态 PIE 在线检查（可在启动早期调用）

```cpp
// 来源: Public/OnlineSubsystemUtils.h
// 安全的早期检查，使用 CDO 或回退到 INI/命令行
bool bOnlinePIE = IOnlineSubsystemUtils::IsOnlinePIEEnabledStatic();
```

### 进阶用法 — Online Services (OSSv2) 工具

```cpp
// 来源: Public/Online/OnlineServicesEngineUtils.h
#include "Online/OnlineServicesEngineUtils.h"

using namespace UE::Online;

// 获取 Online Services 实例
IOnlineServicesPtr Services = GetServices(World, EOnlineServices::Default);
FName InstanceName = GetServicesInstanceName(World);

// 获取引擎级工具
IOnlineServicesEngineUtils* ServicesUtils = UE::Online::GetServicesEngineUtils();
```

## Demo 示例

### 最小示例 — 在线子系统工具类

```cpp
// MyOnlineHelper.h
#pragma once

#include "CoreMinimal.h"
#include "OnlineSubsystemUtils.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "MyOnlineHelper.generated.h"

UCLASS()
class UMyOnlineHelper : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    /** 获取当前世界对应的所有在线接口 */
    void GetAllInterfaces();

    /** 检查子系统是否已加载 */
    bool IsSubsystemLoaded(FName SubsystemName = NAME_None);

    /** 打印当前在线子系统状态 */
    void DumpOnlineState();
};
```

```cpp
// MyOnlineHelper.cpp
#include "MyOnlineHelper.h"
#include "OnlineSubsystem.h"
#include "OnlineSessionSettings.h"

void UMyOnlineHelper::GetAllInterfaces()
{
    UWorld* World = GetWorld();
    if (!World) return;

    IOnlineSubsystem* OSS = Online::GetSubsystem(World);
    if (!OSS)
    {
        UE_LOG(LogTemp, Warning, TEXT("No online subsystem found"));
        return;
    }

    // 获取所有标准接口
    IOnlineSessionPtr SessionInt = Online::GetSessionInterface(World);
    IOnlineIdentityPtr IdentityInt = Online::GetIdentityInterface(World);
    IOnlineFriendsPtr FriendsInt = Online::GetFriendsInterface(World);
    IOnlineLeaderboardsPtr LeaderboardsInt = Online::GetLeaderboardsInterface(World);
    IOnlineAchievementsPtr AchievementsInt = Online::GetAchievementsInterface(World);

    UE_LOG(LogTemp, Log, TEXT("OSS: %s"), *OSS->GetSubsystemName().ToString());
    UE_LOG(LogTemp, Log, TEXT("Session: %s"), SessionInt.IsValid() ? TEXT("OK") : TEXT("NULL"));
    UE_LOG(LogTemp, Log, TEXT("Identity: %s"), IdentityInt.IsValid() ? TEXT("OK") : TEXT("NULL"));
    UE_LOG(LogTemp, Log, TEXT("Friends: %s"), FriendsInt.IsValid() ? TEXT("OK") : TEXT("NULL"));
}

bool UMyOnlineHelper::IsSubsystemLoaded(FName SubsystemName)
{
    UWorld* World = GetWorld();
    if (!World) return false;

    return Online::IsLoaded(World, SubsystemName);
}

void UMyOnlineHelper::DumpOnlineState()
{
    IOnlineSubsystemUtils* Utils = Online::GetUtils();
    if (Utils && GetWorld())
    {
        Utils->DumpSessionState(GetWorld());
        Utils->DumpVoiceState(GetWorld());
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `OnlineSubsystem` | 在线子系统核心接口定义 |
| `OnlineServices` | Online Services (OSSv2) 核心接口定义 |
| `Voice` | 语音捕获/编解码引擎 |
| `AudioMixer` | 音频混合器（VoIP 合成组件） |
| `Networking` | 网络 Socket 抽象层 |
| `Sockets` | Socket 实现 |
| `Net` | 网络驱动与连接基础 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点的警告 |
| 2026-05-12 | `4ad1dbcc` | [OnlineSubsystem][OnlineServices] Guard SetPort callers against bogus port values from EOS:<PUID> ad | 防御 EOS 返回的无效端口值导致的异常 |
| 2026-04-30 | `7b87ee43` | Null-check Driver->GetSocketSubsystem() in UIpConnection::LowLevelSend synchronous send-failure path | 修复 IP 连接发送失败路径中的空指针检查 |
| 2026-04-29 | `bef86caa` | Whitespace: followup to migrate UE_LOG to UE_LOGF: Restore newlines in multi-line format strings tha | 日志宏迁移后的格式修复 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复作用域枚举在格式化函数中导致的乱码输出 |

### 维护评价

- **活跃维护**：近期（2026年）有多次实质性提交，涉及网络驱动修复、平台兼容性改进、编译警告修复
- **核心地位**：作为 UE 在线功能的基础设施，几乎所有使用在线功能的项目都隐式依赖此插件
- **稳定性**：创建于 2016 年，经过 9 年迭代，API 非常成熟稳定
- **兼容性**：同时支持 OSSv1（OnlineSubsystem）和 OSSv2（OnlineServices），通过 `bOnlineServicesCompatibilityEnabled` 配置切换
- **已知限制**：部分蓝图代理（如 `UInAppPurchaseQueryCallbackProxy2`、`UInAppPurchaseRestoreCallbackProxy2`）已标记 `DeprecatedFunction`，建议使用新的收据式购买 API
- **推荐使用**：✅ **强烈推荐**。这是 UE 在线功能的必选插件，默认启用，无需额外操作即可使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineSubsystemUtils)
- [在线子系统核心文档](https://docs.unrealengine.com/en-US/InteractiveExperiences/Networking/OnlineSubsystem/)