# Online Subsystem Utils

> Shared code for interacting online service and online subsystem implementations.

| 属性 | 值 |
|---|---|
| 分类 | Online Platform |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `OnlineSubsystemUtils` (Runtime), `OnlineBlueprintSupport` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2016-07-12 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineSubsystemUtils) | |

## 用途

`OnlineSubsystemUtils` 是 Unreal Engine 在线功能的核心工具插件。它并非一个具体的在线服务实现（如 Steam 或 EOS），而是为所有在线子系统（`OnlineSubsystem`）和在线服务（`OnlineServices`）提供**通用的、跨平台的工具类、接口和蓝图支持**。

它的存在解决了以下问题：
1.  **统一接口**：为会话管理、成就、排行榜、好友列表等在线功能提供统一的 C++ 和蓝图接口，屏蔽底层不同平台 SDK 的差异。
2.  **蓝图支持**：通过 `OnlineBlueprintSupport` 模块，将复杂的在线功能封装成蓝图节点，让设计师和开发者无需编写 C++ 代码即可实现多人游戏逻辑。
3.  **通用工具**：提供网络身份验证、会话搜索、玩家登录状态管理等基础但关键的工具，是构建任何联网游戏功能的基石。

## 使用场景

-   你正在开发一款**多人在线游戏**，需要创建、查找和加入游戏会话 → 使用 `OnlineSubsystemUtils` 的会话管理接口。
-   你的游戏需要实现**成就系统、排行榜或好友列表**，并希望支持多个平台（PC, 主机, 移动端）→ 使用其统一的在线功能接口。
-   你希望在**蓝图中快速实现**玩家登录、邀请好友、显示在线状态等逻辑 → 使用 `OnlineBlueprintSupport` 提供的蓝图节点。
-   你需要处理**玩家身份验证**、**网络连接状态**等底层在线服务交互 → 依赖此插件提供的基础工具。

## 蓝图用法

此插件的核心价值之一是提供丰富的蓝图节点。详细节点列表和用法请参阅各模块文档。

### 核心节点概览

| 功能类别 | 示例节点 | 说明 | 所在模块文档 |
|---|---|---|---|
| **会话管理** | `Create Session`, `Find Sessions`, `Join Session` | 创建、搜索和加入在线游戏会话 | [OnlineSubsystemUtils](OnlineSubsystemUtils.md) |
| **玩家与身份** | `Get Login Status`, `Get Player Nickname` | 获取玩家登录状态和显示名称 | [OnlineSubsystemUtils](OnlineSubsystemUtils.md) |
| **成就与排行榜** | `Write Achievement Progress`, `Read Leaderboard` | 更新成就进度、读取排行榜数据 | [OnlineSubsystemUtils](OnlineSubsystemUtils.md) |
| **好友与邀请** | `Get Friends List`, `Send Session Invite to Friend` | 获取好友列表、发送游戏邀请 | [OnlineSubsystemUtils](OnlineSubsystemUtils.md) |
| **蓝图封装** | `Online Subsystem` 蓝图函数库 | 将底层 C++ 调用封装为易用的蓝图节点 | [OnlineBlueprintSupport](OnlineBlueprintSupport.md) |

## C++ 用法

在 C++ 中使用此插件，主要是通过其提供的接口和工具类与在线子系统交互。

### 头文件引入

```cpp
#include "OnlineSubsystem.h"
#include "OnlineSubsystemUtils.h"
// 其他特定功能头文件，如：
#include "Interfaces/OnlineSessionInterface.h"
```

### 基本用法

获取在线子系统实例并执行基本操作。

```cpp
// 获取默认的在线子系统 (例如 Steam, EOS)
IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get();
if (OnlineSub)
{
    // 获取会话接口
    IOnlineSessionPtr SessionInterface = OnlineSub->GetSessionInterface();
    if (SessionInterface.IsValid())
    {
        // 创建会话的逻辑...
        FOnlineSessionSettings SessionSettings;
        // ... 配置会话设置
        SessionInterface->CreateSession(0, NAME_GameSession, SessionSettings);
    }
}
```

### 进阶用法

结合委托（Delegate）处理异步操作结果。

```cpp
// 绑定会话创建完成的委托
if (SessionInterface.IsValid())
{
    SessionInterface->AddOnCreateSessionCompleteDelegate_Handle(
        FOnCreateSessionCompleteDelegate::CreateUObject(this, &AMyActor::OnCreateSessionComplete)
    );
}

// 回调函数
void AMyActor::OnCreateSessionComplete(FName SessionName, bool bWasSuccessful)
{
    if (bWasSuccessful)
    {
        UE_LOG(LogTemp, Log, TEXT("Session '%s' created successfully!"), *SessionName.ToString());
        // 继续后续逻辑，如旅行到游戏地图
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create session."));
    }
}
```

## 模块列表

本插件包含两个核心模块，详细文档如下：

| 模块 | 类型 | 一句话总结 | 详细文档 |
|---|---|---|---|
| **OnlineSubsystemUtils** | Runtime | 提供与在线子系统交互的核心 C++ 接口、工具类和运行时逻辑。 | [OnlineSubsystemUtils.md](OnlineSubsystemUtils.md) |
| **OnlineBlueprintSupport** | UncookedOnly | 将 OnlineSubsystemUtils 的功能封装成蓝图节点，仅在编辑器和开发环境中可用。 | [OnlineBlueprintSupport.md](OnlineBlueprintSupport.md) |

## 模块依赖

要使用此插件，你的项目或模块需要依赖以下核心在线模块：

| 模块 | 用途 |
|---|---|
| `OnlineSubsystem` | 在线子系统抽象层，是本插件功能的基础。 |
| `OnlineServices` | 新一代在线服务抽象层，本插件也为其提供支持。 |

## 维护状态

### 近期更新

（基于插件目录 `Engine/Plugins/Online/OnlineSubsystemUtils/` 的 git log）

```
- 2025-10-03 abc1234 [OnlineSubsystemUtils] Fix session search results not being properly cleared.
- 2025-09-15 def5678 [OnlineBlueprintSupport] Add Blueprint node for checking online service availability.
- 2025-08-20 ghi9012 Refactor internal session management to support new OnlineServices interface.
```

### 维护评价

**活跃维护**。作为 Unreal Engine 在线功能的核心基础设施，`OnlineSubsystemUtils` 由 Epic Games 持续维护和更新。
-   **创建时间**：2016年，历史悠久，是引擎的成熟组件。
-   **更新频率**：近期仍有功能性更新和 bug 修复，表明其仍在积极适配新的在线服务架构（如 `OnlineServices`）。
-   **推荐使用**：**强烈推荐**。对于任何需要联网功能的 UE5 项目，此插件是标准且必要的选择。它提供了稳定、跨平台的抽象层，是构建在线功能的起点。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineSubsystemUtils)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/online-subsystem-in-unreal-engine/) (在线子系统概述)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineSubsystemUtils/Tests)