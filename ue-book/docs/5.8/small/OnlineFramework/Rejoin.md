# Online Framework Plugin - Rejoin

> Shared code for interacting with online gameplay services.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 重新加入框架 |
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（代码模块） |
| 模块 | `Rejoin` (Runtime), `Hotfix` (Runtime), `Lobby` (Runtime), `LoginFlow` (Runtime), `Party` (Runtime), `PatchCheck` (Runtime), `PlayTimeLimit` (Runtime), `Qos` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2016-07-13 |
| 年龄标签 | 🏛️ 文物（约 10 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineFramework) | |

## 用途

`Rejoin` 模块提供了一个基础框架，用于处理玩家重新加入正在进行的游戏会话（比赛）的逻辑。它解决了一个常见的游戏体验问题：当玩家因网络波动、客户端崩溃或其他原因意外退出一场多人游戏时，如何检测并允许其重新连接回刚才的比赛，以减少挫败感并保持游戏连续性。

该模块的核心是一个抽象基类 `URejoinCheck`，它定义了与后端服务交互以检查会话状态、尝试重新加入的通用流程和接口。具体的游戏实现需要继承此类，并根据所使用的在线子系统（Online Subsystem）和游戏会话逻辑来提供具体的重连逻辑。

## 使用场景

- 你在开发一款竞技性多人在线游戏（如 FPS、MOBA、大逃杀等），需要实现断线重连功能。
- 你的游戏会话有明确的“进行中”状态，且允许中途加入（至少对特定玩家）。
- 你希望有一个统一的框架来管理重连的检查、状态和尝试过程，而不是在每个游戏中从头实现。

## 蓝图用法

该模块主要为 C++ 设计，但暴露了部分接口给蓝图使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetStatus` | 获取当前重新加入检查的状态。 | `URejoinCheck` |
| `HasCompletedCheck` | 检查是否已完成一次检查，无需立即重新运行。 | `URejoinCheck` |
| `IsRejoinAvailable` | 检查当前是否有可重新加入的比赛。 | `URejoinCheck` |
| `OnRejoinCheckStatusChanged` | 委托，在重新加入检查的状态发生变化时触发。 | `URejoinCheck` |

### 使用示例（蓝图描述）

1.  在你的游戏逻辑中（例如游戏模式或玩家控制器），持有 `URejoinCheck` 子类实例的引用。
2.  当玩家返回主菜单或登录成功后，调用 `CheckRejoinStatus` 节点。
3.  绑定 `OnRejoinCheckStatusChanged` 委托，监听状态变化。
4.  当状态变为 `RejoinAvailable` 时，在 UI 上显示“重新加入比赛”的按钮。
5.  玩家点击按钮后，调用 `RejoinLastSession` 节点发起重连尝试。

## C++ 用法

### 头文件引入

```cpp
#include "Rejoin/RejoinCheck.h"
```

### 基本用法

`URejoinCheck` 是一个抽象基类，你需要创建自己的子类来实现具体逻辑。以下是基于源码注释的用法框架。

```cpp
// MyRejoinCheck.h
#pragma once
#include "Rejoin/RejoinCheck.h"
#include "MyRejoinCheck.generated.h"

UCLASS()
class UMyRejoinCheck : public URejoinCheck
{
    GENERATED_BODY()
public:
    // 实现检查结果状态解析的纯虚函数
    virtual ERejoinStatus GetRejoinStateFromSearchResult(const FOnlineSessionSearchResult& InSearchResult) const override;

    // 实现通过会话重新加入比赛的纯虚函数
    virtual void RejoinViaSession() override;

protected:
    // 可以重写失败处理，添加游戏特定逻辑
    virtual void OnRejoinFailure(ERejoinAttemptResult Result) override;
};
```

```cpp
// MyRejoinCheck.cpp
#include "MyRejoinCheck.h"
#include "OnlineSubsystem.h"

// 解析后端返回的搜索结果，决定其是否代表一个可重连的会话
ERejoinStatus UMyRejoinCheck::GetRejoinStateFromSearchResult(const FOnlineSessionSearchResult& InSearchResult) const
{
    // 根据你的游戏会话设置（例如GameSettings）判断该会话是否可加入
    if (InSearchResult.Session.SessionSettings.bShouldAdvertise &&
        /* 其他条件 */)
    {
        return ERejoinStatus::RejoinAvailable;
    }
    return ERejoinStatus::NoMatchToRejoin;
}

// 执行实际的重连操作（例如加载地图并Travel到服务器）
void UMyRejoinCheck::RejoinViaSession()
{
    // 1. 调用 Online Session 的 JoinSession
    // 2. 在 JoinSession 成功的回调中，调用基类的 TravelToSession() 方法
}

// 自定义失败处理
void UMyRejoinCheck::OnRejoinFailure(ERejoinAttemptResult Result)
{
    Super::OnRejoinFailure(Result);
    // 显示错误消息给用户
}
```

*来源：Public/RejoinCheck.h*

### 进阶用法

你可以在游戏中集成 `UMyRejoinCheck` 实例，并连接状态更新到游戏逻辑。

```cpp
// 在你的游戏实例或玩家控制器中
void AMyPlayerController::BeginPlay()
{
    Super::BeginPlay();
    MyRejoinCheck = NewObject<UMyRejoinCheck>(this);
    MyRejoinCheck->OnRejoinCheckStatusChanged().AddUObject(this, &AMyPlayerController::HandleRejoinStatusChanged);
}

void AMyPlayerController::CheckForRejoin()
{
    if (MyRejoinCheck && MyRejoinCheck->IsRejoinCheckEnabled())
    {
        MyRejoinCheck->CheckRejoinStatus();
    }
}

void AMyPlayerController::AttemptRejoin()
{
    if (MyRejoinCheck && MyRejoinCheck->IsRejoinAvailable())
    {
        MyRejoinCheck->RejoinLastSession(FOnRejoinLastSessionComplete::CreateUObject(this, &AMyPlayerController::OnRejoinAttemptComplete));
    }
}

void AMyPlayerController::HandleRejoinStatusChanged(ERejoinStatus NewStatus)
{
    // 更新 UI 或触发其他游戏逻辑
    UpdateRejoinUI(NewStatus);
}
```

*来源：Public/RejoinCheck.h 中类的使用模式*

## Demo 示例

以下是一个最小的、可编译的 `URejoinCheck` 子类实现骨架。

**MinimalRejoinCheck.h**
```cpp
#pragma once
#include "Rejoin/RejoinCheck.h"
#include "MinimalRejoinCheck.generated.h"

UCLASS()
class UMinimalRejoinCheck : public URejoinCheck
{
    GENERATED_BODY()
public:
    UMinimalRejoinCheck();

protected:
    // 必须实现的纯虚函数
    virtual ERejoinStatus GetRejoinStateFromSearchResult(const FOnlineSessionSearchResult& InSearchResult) const override;
    virtual void RejoinViaSession() override;
};
```

**MinimalRejoinCheck.cpp**
```cpp
#include "MinimalRejoinCheck.h"

UMinimalRejoinCheck::UMinimalRejoinCheck()
{
    // 基类构造函数已处理初始化
}

ERejoinStatus UMinimalRejoinCheck::GetRejoinStateFromSearchResult(const FOnlineSessionSearchResult& InSearchResult) const
{
    // 这里只是演示，真实逻辑需要根据SessionSettings判断
    if (InSearchResult.IsValid())
    {
        return ERejoinStatus::RejoinAvailable;
    }
    return ERejoinStatus::NoMatchToRejoin;
}

void UMinimalRejoinCheck::RejoinViaSession()
{
    // 简单演示：直接调用基类的TravelToSession
    // 真实实现通常需要先 JoinSession
    TravelToSession();
}
```

## 模块依赖

`Rejoin` 模块自身的 `Build.cs` 文件未提供，但根据其核心功能（会话管理、网络连接）推断，它依赖于以下模块。用户模块需要包含这些依赖才能使用 `Rejoin` 模块。

| 模块 | 用途 |
|---|---|
| `OnlineSubsystem` | 与平台或自定义在线服务进行会话、好友等交互的核心抽象层。 |
| `OnlineSubsystemUtils` | 在线子系统的工具类和蓝图支持。 |

*注：Core, CoreUObject, Engine 等基础模块已省略。*

## 维护状态

### 近期更新

从提供的 git 历史看，最近的提交均未直接修改 `Rejoin` 模块代码，改动集中在 `Hotfix` 和 `Party` 模块。

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `09a2dfc6` | [Hotfix on Load] Fix issue where certain baked hotfixes will not apply when no backend hotfixes exis | 修复在无后端热修复时部分内置热修复不生效的问题。 |
| 2026-05-12 | `0b9170a8` | Guard Invite and RTJ social party calls when epic parties mirroring is enabled. | 当启用 Epic 聚会镜像功能时，为邀请和加入聚会社交功能添加了防护。 |
| 2026-04-30 | `fe1eaff2` | Add a hook for PartyPlatformSessionMonitor to allow the game party to add a special key to the platf | 为 PartyPlatformSessionMonitor 添加钩子，允许游戏派对向平台会话添加特殊键。 |
| 2026-04-29 | `0badc43f` | Restore LogHotfixManager summary logs for hotfix on load | 恢复 HotfixManager 在加载时输出的摘要日志。 |
| 2026-04-28 | `85cae1c6` | Broadcast party initialization after we've processed our first update | 在处理完第一次更新后广播派对初始化事件。 |

### 维护评价

`Rejoin` 模块自 2016 年创建以来，作为 `OnlineFramework` 的一部分存在，但其核心架构（`URejoinCheck` 抽象类）在很长时间内保持稳定。最近的提交历史显示，**该模块没有近期实质性更新**，所有活动都发生在同插件内的其他模块（Hotfix， Party）上。这表明 `Rejoin` 模块的代码可能已进入“维护模式”，功能稳定但未有新特性开发。

**结论**：
- **创建时间久远**：属于引擎的“文物”级模块。
- **代码稳定**：作为抽象接口，其设计经受了时间考验。
- **活跃度低**：近年无相关更新，意味着 Epic 可能认为其核心功能足够，或其职责已被其他系统（如更现代的在线子系统集成）部分取代。
- **推荐使用**：如果你的游戏需要一个结构清晰、基于 UObject 的重连检查框架，并且你愿意继承并实现具体逻辑，它仍然有用。但需注意其底层可能依赖的 `OnlineSubsystem` 接口是否已过时。对于新项目，应优先考虑最新的在线服务插件方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineFramework/Source/Rejoin)
- [官方文档] (无直接对应文档)
- [测试用例] (未在插件目录内发现明显测试文件)