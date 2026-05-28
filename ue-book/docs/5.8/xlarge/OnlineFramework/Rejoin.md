# Online Framework - Rejoin

> Shared code for interacting with online gameplay services.

| 属性 | 值 |
|---|---|
| 中文名 | 重连检查 |
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `Rejoin` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2016-07-13 |
| 年龄标签 | 🏛️ 文物（约 10 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineFramework/Source/Rejoin) | |

## 用途

`Rejoin` 模块提供了一个用于处理游戏会话重连的核心框架。它主要解决玩家在游戏过程中因网络中断、游戏崩溃或意外退出后，能够自动检测并重新加入之前游戏会话的问题。该模块通过 `URejoinCheck` 抽象基类定义了一套标准流程：查询后端是否存在玩家的活跃会话、管理重连尝试状态、并最终将玩家传送回原服务器。开发者需要继承该基类以实现特定的平台或游戏逻辑。

## 使用场景

- 你的游戏支持在线多人对战 → 玩家意外掉线后，希望在重新登录时能快速返回之前的对局。
- 你使用 Epic 的 Party 和 Lobby 系统管理会话 → 重连检查可以无缝集成，确保会话的连续性。
- 你需要一个标准化的重连状态管理机（如 `NoMatchToRejoin`, `RejoinAvailable`）来驱动 UI 显示或执行其他逻辑。

## 蓝图用法

`URejoinCheck` 本身是一个 C++ 抽象基类，通常不直接在蓝图中实例化。其定义的状态枚举和委托类型是蓝图友好的，可用于子类实现或状态读取。

### 核心枚举

| 枚举 | 说明 |
|---|---|
| `ERejoinStatus` | 表示重连检查的当前状态（如 `RejoinAvailable` 有会话可重连）。 |
| `ERejoinAttemptResult` | 表示一次重连尝试的结果（如 `RejoinSuccess` 成功， `JoinSessionFailure` 加入失败）。 |

### 核心委托

| 委托 | 说明 |
|---|---|
| `FOnRejoinCheckComplete` | 单次重连状态检查完成时触发。 |
| `FOnRejoinCheckStatusChanged` | 重连状态发生变化时触发的多播委托。 |
| `FOnRejoinLastSessionComplete` | 重连尝试完成时触发。 |

### 使用示例（蓝图描述）
假设你创建了一个 `UMyGameRejoinCheck` 子类。在你的游戏逻辑中，你可以：
1. 调用 `CheckRejoinStatus` 来异步检查是否存在可重连的会话。
2. 监听 `OnRejoinCheckStatusChanged` 委托来更新 UI（例如，当状态变为 `RejoinAvailable` 时显示“重新加入”按钮）。
3. 当用户点击按钮时，调用 `RejoinLastSession` 发起重连。
4. 监听 `FOnRejoinLastSessionComplete` 来处理重连结果（成功则等待传送，失败则提示用户）。

## C++ 用法

核心用法是继承 `URejoinCheck` 并实现其纯虚函数。

### 头文件引入
```cpp
#include “RejoinCheck.h”
```

### 基本用法
继承 `URejoinCheck` 并实现必需的纯虚函数。你需要实现 `GetRejoinStateFromSearchResult` 来定义如何从平台返回的搜索结果判断是否可重连，并实现 `RejoinViaSession` 来执行实际的加入和传送逻辑。
```cpp
// MyGameRejoinCheck.h
#pragma once
#include "RejoinCheck.h"
#include "MyGameRejoinCheck.generated.h"

UCLASS()
class UMyGameRejoinCheck : public URejoinCheck
{
    GENERATED_BODY()

public:
    // 实现判断搜索结果是否代表一个可重连的会话
    virtual ERejoinStatus GetRejoinStateFromSearchResult(const FOnlineSessionSearchResult& InSearchResult) const override;

    // 实现具体的会话重连和地图传送逻辑
    virtual void RejoinViaSession() override;
};

// MyGameRejoinCheck.cpp
#include “MyGameRejoinCheck.h”

ERejoinStatus UMyGameRejoinCheck::GetRejoinStateFromSearchResult(const FOnlineSessionSearchResult& InSearchResult) const
{
    // 这里可以添加你自己的判断逻辑，例如检查会话是否在同一个游戏模式下、地图是否相同等。
    // 示例：总是返回可重连状态
    return ERejoinStatus::RejoinAvailable;
}

void UMyGameRejoinCheck::RejoinViaSession()
{
    const FOnlineSessionSearchResult& SearchResult = GetSearchResult();
    if (SearchResult.IsValid())
    {
        // 调用在线子系统接口加入会话
        // IOnlineSessionPtr Sessions = Online::GetSubsystem(GetWorld())->GetSessionInterface();
        // Sessions->JoinSession(...);
        // 加入成功后，在回调中调用 TravelToSession() 进行传送
    }
    else
    {
        // 没有有效的搜索结果，通知基类失败
        OnRejoinFailure(ERejoinAttemptResult::NothingToRejoin);
    }
}
```
> 来源: `Engine/Plugins/Online/OnlineFramework/Source/Rejoin/Public/RejoinCheck.h`

### 进阶用法
你可以覆盖更多虚函数来自定义行为，例如 `Analytics_RecordRejoinDetected` 来记录重连分析事件，或重写 `IsRejoinCheckEnabled` 来实现更复杂的启用逻辑。利用 `ClearTimers` 和 `StartRejoinChecks` 可以控制周期性检查。

## Demo 示例

一个最小的 `URejoinCheck` 子类实现，仅处理基础重连流程。

```cpp
// MinimalRejoinCheck.h
#pragma once
#include "RejoinCheck.h"
#include "MinimalRejoinCheck.generated.h"

UCLASS(MinimalAPI)
class UMinimalRejoinCheck : public URejoinCheck
{
	GENERATED_BODY()

public:
	UMinimalRejoinCheck();

protected:
	// 简单地认为有搜索结果就可重连
	virtual ERejoinStatus GetRejoinStateFromSearchResult(const FOnlineSessionSearchResult& InSearchResult) const override;
	// 调用基类的 TravelToSession
	virtual void RejoinViaSession() override;
};

// MinimalRejoinCheck.cpp
#include "MinimalRejoinCheck.h"

UMinimalRejoinCheck::UMinimalRejoinCheck()
{
}

ERejoinStatus UMinimalRejoinCheck::GetRejoinStateFromSearchResult(const FOnlineSessionSearchResult& InSearchResult) const
{
	return InSearchResult.IsValid() ? ERejoinStatus::RejoinAvailable : ERejoinStatus::NoMatchToRejoin;
}

void UMinimalRejoinCheck::RejoinViaSession()
{
	// 调用基类提供的方法来处理会话加入和传送
	TravelToSession();
}
```

## 模块依赖

从 `Rejoin.Build.cs` 和头文件包含关系来看，使用此模块需要依赖：
- `OnlineSubsystem`：用于访问平台会话接口 (`FOnlineSessionSearchResult`, `FindFriendSession` 等)。
- `Engine`：用于 `UObject` 基类、`UWorld` 访问、计时器 (`FTimerHandle`) 等核心功能。
- `OnlineSubsystemGDK`：在 `Rejoin.Build.cs` 中声明的依赖。

## 维护状态

### 近期更新
基于提供的在线框架插件整体 git 历史，`Rejoin` 模块本身在近期没有专门的提交记录。最近的更新主要集中在 `Hotfix`, `Party` 等其他模块。

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `09a2dfc6` | [Hotfix on Load] Fix issue where certain baked hotfixes will not apply when no backend hotfixes exis | 修复预烘焙热修复应用问题。 |
| 2026-05-12 | `0b9170a8` | Guard Invite and RTJ social party calls when epic parties mirroring is enabled. | 在 Epic Party 镜像模式下保护邀请和重连调用。 |
| 2026-04-30 | `fe1eaff2` | Add a hook for PartyPlatformSessionMonitor to allow the game party to add a special key to the platf | 为 PartyPlatformSessionMonitor 添加钩子。 |

### 维护评价
`Rejoin` 模块作为 `OnlineFramework` 插件的一部分，创建于 **2016 年**，是一个历史悠久的基础组件。其核心功能 `URejoinCheck` 框架稳定，但近年来没有针对该模块的功能性更新。考虑到其抽象基类的性质，它更倾向于被其他具体实现（如特定游戏或平台模块）所使用，而非频繁修改自身。该模块的状态可以认为是**维护不活跃**但**稳定**。如果只是需要标准的重连状态管理框架，它仍然是一个可靠的选择，但需注意其可能未适配最新的 UE 网络或在线服务变更。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineFramework/Source/Rejoin)
- [官方文档](https://docs.unrealengine.com) (通用文档，无特定页面)
- [测试用例] (未在提供信息中找到 Rejoin 模块的特定测试文件)