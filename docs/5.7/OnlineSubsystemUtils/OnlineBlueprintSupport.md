# Online Subsystem Utils

> Shared code for interacting online service and online subsystem implementations.

| 属性 | 值 |
|---|---|
| 分类 | Online Platform |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `OnlineSubsystemUtils` (Runtime), `OnlineBlueprintSupport` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2016-07-12 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineSubsystemUtils) | |

## 用途

`OnlineSubsystemUtils` 插件是 Unreal Engine 在线功能的核心实用工具层。它并非一个独立的在线子系统实现，而是为 `OnlineSubsystem` 和 `OnlineServices` 插件提供共享的、跨平台的工具代码和蓝图支持。

**核心作用**：
1.  **抽象层**：提供统一的接口和数据结构（如 `IOnlineSubsystem`, `FUniqueNetId`, `FOnlineSessionSettings`），使游戏逻辑能够与底层平台特定的在线服务（如 Steam, Xbox Live, PlayStation Network）进行交互，而无需关心具体平台细节。
2.  **蓝图支持**：通过 `OnlineBlueprintSupport` 模块，将复杂的在线功能（如内购、排行榜查询、会话管理）封装成易于使用的蓝图异步节点，极大地方便了设计师和蓝图程序员。
3.  **实用工具**：包含用于网络会话管理、好友列表、排行榜、成就、内购（IAP）等常见在线功能的通用实现和辅助类。

简而言之，这个插件是连接你的游戏逻辑与各种在线平台服务的“桥梁”和“工具箱”。

## 使用场景

-   你的游戏需要支持多个平台（PC, 主机, 移动端）的在线功能，如多人游戏、排行榜、成就 → 使用 `OnlineSubsystemUtils` 提供的抽象接口。
-   你需要在蓝图中快速实现“查询排行榜”、“发起内购”、“创建游戏房间”等异步操作 → 使用 `OnlineBlueprintSupport` 提供的蓝图节点。
-   你正在开发一个需要集成 Steam、Epic Online Services (EOS) 或其他平台服务的项目 → 这个插件是基础依赖。

## 蓝图用法

`OnlineBlueprintSupport` 模块提供了大量用于在线功能的蓝图异步节点。这些节点通常继承自 `UK2Node_BaseAsyncTask`，在蓝图中表现为带有输出执行引脚的异步操作。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Start an In-App Purchase` | 发起一个应用内购买流程。 | `UK2Node_InAppPurchase2` |
| `Query for Owned In-App Products` | 查询当前用户已拥有的应用内产品。 | `UK2Node_InAppPurchaseQueryOwned2` |
| `Restore Owned In-App Products` | 恢复用户之前购买过的产品（通常用于跨设备同步）。 | `UK2Node_InAppPurchaseRestore2` |
| `Get known In-App Receipts` | 获取已知的、可能未处理的购买收据。 | `UK2Node_InAppPurchaseGetKnownReceipts` |
| `Query Leaderboards` | 查询在线排行榜数据。 | `UK2Node_LeaderboardQuery` |
| `Flush Leaderboard Writes` | 将本地缓存的排行榜分数写入提交到服务器。 | `UK2Node_LeaderboardFlush` |

### 使用示例（蓝图描述）

1.  **查询排行榜**：
    *   在蓝图中，从事件图表拖出执行线，搜索并添加 `Query Leaderboards` 节点。
    *   设置 `Leaderboard Name`（如 “HighScores”）和 `Query Settings`（如查询类型、范围）。
    *   连接 `On Success` 和 `On Failure` 输出执行引脚到后续逻辑。
    *   在 `On Success` 引脚后，可以通过 `Results` 输出引脚获取排行榜条目数组。

2.  **发起内购**：
    *   添加 `Start an In-App Purchase` 节点。
    *   设置 `Product ID`（对应你在平台后台配置的商品ID）。
    *   连接 `On Success`（购买成功）和 `On Failure`（购买失败或取消）引脚。
    *   在 `On Success` 引脚后，通常需要调用 `Finalize In-App Purchase` 节点来确认购买，防止欺诈。

## C++ 用法

`OnlineSubsystemUtils` 模块提供了 C++ 层面的核心接口和工具类。

### 头文件引入

```cpp
#include "OnlineSubsystem.h"
#include "OnlineSubsystemUtils.h"
// 根据具体功能，可能需要引入更具体的头文件，如：
#include "Interfaces/OnlineSessionInterface.h"
#include "Interfaces/OnlineLeaderboardInterface.h"
```

### 基本用法

**获取在线子系统实例并查询排行榜** (参考自引擎测试用例)：
```cpp
// 来源: Engine/Source/Runtime/Online/OnlineSubsystemUtils/Private/Tests/OnlineSubsystemTest.cpp
void QueryLeaderboards()
{
    // 1. 获取默认的在线子系统（通常是平台原生子系统或EOS）
    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get();
    if (OnlineSub)
    {
        // 2. 获取排行榜接口
        IOnlineLeaderboardsPtr LeaderboardsInterface = OnlineSub->GetLeaderboardsInterface();
        if (LeaderboardsInterface.IsValid())
        {
            // 3. 创建查询设置
            FOnlineLeaderboardReadRef ReadRef = MakeShared<FOnlineLeaderboardRead>();
            ReadRef->LeaderboardName = TEXT("MyLeaderboard");
            
            // 4. 定义回调委托
            FOnLeaderboardReadCompleteDelegate CompletionDelegate;
            CompletionDelegate.BindLambda([ReadRef](bool bSuccess)
            {
                if (bSuccess)
                {
                    // 处理排行榜数据
                    for (const FOnlineStatsRow& Row : ReadRef->Rows)
                    {
                        UE_LOG(LogTemp, Log, TEXT("Player: %s, Score: %d"), *Row.NickName, Row.Rank);
                    }
                }
            });
            
            // 5. 发起异步查询
            LeaderboardsInterface->ReadLeaderboards(ReadRef, CompletionDelegate);
        }
    }
}
```

### 进阶用法

**创建和加入在线会话** (综合多个测试用例)：
```cpp
// 来源: Engine/Source/Runtime/Online/OnlineSubsystemUtils/Private/Tests/OnlineSubsystemTest.cpp
void CreateAndJoinSession()
{
    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get();
    if (!OnlineSub) return;
    
    IOnlineSessionPtr SessionInterface = OnlineSub->GetSessionInterface();
    if (!SessionInterface.IsValid()) return;
    
    // 1. 配置会话设置
    FOnlineSessionSettings SessionSettings;
    SessionSettings.bIsLANMatch = false;
    SessionSettings.NumPublicConnections = 4;
    SessionSettings.bShouldAdvertise = true;
    SessionSettings.bUsesPresence = true;
    
    // 2. 创建会话
    FOnCreateSessionCompleteDelegate CreateDelegate;
    CreateDelegate.BindLambda([SessionInterface, OnlineSub](FName SessionName, bool bSuccess)
    {
        if (bSuccess)
        {
            UE_LOG(LogTemp, Log, TEXT("Session '%s' created successfully."), *SessionName.ToString());
            
            // 3. 会话创建成功后，可以搜索并加入（此处简化）
            // 通常另一个客户端会执行搜索和加入逻辑
        }
    });
    
    SessionInterface->CreateSession(0, NAME_GameSession, SessionSettings, CreateDelegate);
}
```

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何初始化并检查在线子系统状态。

**MyOnlineGameInstance.h**
```cpp
#pragma once
#include "Engine/GameInstance.h"
#include "MyOnlineGameInstance.generated.h"

UCLASS()
class UMyOnlineGameInstance : public UGameInstance
{
    GENERATED_BODY()
public:
    virtual void Init() override;
    
    UFUNCTION(BlueprintCallable, Category = "Online")
    void CheckOnlineSubsystemStatus();
};
```

**MyOnlineGameInstance.cpp**
```cpp
#include "MyOnlineGameInstance.h"
#include "OnlineSubsystem.h"
#include "OnlineSubsystemUtils.h"

void UMyOnlineGameInstance::Init()
{
    Super::Init();
    // GameInstance初始化时，在线子系统通常已经可用
    CheckOnlineSubsystemStatus();
}

void UMyOnlineGameInstance::CheckOnlineSubsystemStatus()
{
    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get();
    if (OnlineSub)
    {
        UE_LOG(LogTemp, Log, TEXT("Online Subsystem '%s' is available."), *OnlineSub->GetSubsystemName().ToString());
        
        // 检查特定接口
        IOnlineSessionPtr SessionInterface = OnlineSub->GetSessionInterface();
        UE_LOG(LogTemp, Log, TEXT("Session Interface: %s"), SessionInterface.IsValid() ? TEXT("Valid") : TEXT("Invalid"));
        
        IOnlineIdentityPtr IdentityInterface = OnlineSub->GetIdentityInterface();
        UE_LOG(LogTemp, Log, TEXT("Identity Interface: %s"), IdentityInterface.IsValid() ? TEXT("Valid") : TEXT("Invalid"));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("No Online Subsystem found."));
    }
}
```

## 模块依赖

从 `OnlineSubsystemUtils.Build.cs` 和 `OnlineBlueprintSupport.Build.cs` 分析，该插件有以下独特依赖：

| 模块 | 用途 |
|---|---|
| `OnlineSubsystem` | 核心在线子系统接口定义，是本插件的基础。 |
| `OnlineServices` | 新一代在线服务抽象层，与 `OnlineSubsystem` 并存或作为其演进。 |
| `BlueprintGraph` | (仅 `OnlineBlueprintSupport`) 用于创建自定义蓝图节点（K2Node）。 |
| `KismetCompiler` | (仅 `OnlineBlueprintSupport`) 用于编译包含自定义蓝图节点的蓝图。 |

## 维护状态

### 近期更新

```
- 2025-10-03 2739c3d30ebc Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types. Part 4/n
- 2025-09-15 66e9bb39ff7e Removed all #if UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes from the code base
- 2025-08-20 d06aabed8b76 Marked deprecated IAP blueprint nodes and created replacements:  - Make an In-App Purchase v2 -> Replaced by new "Start an In-App Purchase" node  - Process any New Unprocessed Purchases v2 -> Replaced by new "Get known In-App Receipts" node  - Query for Owned Purchases -> Replaced by new "Query for Owned In-App Products" node  - Restore In-App Purchases2 -> Replaced by new "Restore Owned In-App Products" node
```

### 维护评价

**综合评价：活跃维护中，但需注意API演进。**

*   **活跃维护**：最近的提交（2025年）表明 Epic 仍在积极维护此插件，主要进行代码现代化（移除废弃宏）、API 清理和蓝图节点更新。
*   **核心地位**：作为在线功能的基石，它不太可能被废弃，但会随着 `OnlineServices` 的成熟而逐步演进。
*   **API 变化**：从提交记录可以看到，蓝图节点（如内购相关）正在被标记为废弃并替换为新版本。在 C++ 层面，接口也可能随着引擎版本更新而变化。
*   **推荐使用**：**强烈推荐**。这是实现 UE5 在线功能的标准方式。使用时应关注引擎版本更新日志，及时适配 API 变化，特别是蓝图节点的迁移。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineSubsystemUtils)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/online-subsystem-in-unreal-engine/) (Online Subsystem 概述)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Source/Runtime/Online/OnlineSubsystemUtils/Private/Tests) (位于引擎运行时目录下)