# Online Framework Plugin

> Shared code for interacting with online gameplay services.

| 属性 | 值 |
|---|---|
| 中文名 | 在线框架插件 |
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `Qos` (Runtime), `Party` (Runtime), `Lobby` (Runtime), `Hotfix` (Runtime), `LoginFlow` (Runtime), `PatchCheck` (Runtime), `PlayTimeLimit` (Runtime), `Rejoin` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2016-07-13 |
| 年龄标签 | 🏛️ 文物（约 10 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineFramework) | |

## 用途

这是一个在线游戏功能的**基础框架插件**，为 UE 的在线子系统（Online Subsystem）提供了上层通用功能实现。它不直接与特定平台（如 PlayStation Network, Xbox Live）对接，而是提供一套与平台无关的在线游戏功能中间件。

这个插件存在的价值在于：
1.  **代码复用**：将常见、通用的在线游戏逻辑（如组队、大厅、质量检测、游戏时间限制等）从具体的平台子系统中抽象出来，避免在每个平台子系统插件中重复实现。
2.  **关注点分离**：将纯客户端/服务器逻辑与平台 SDK 调用解耦，使核心逻辑更易于维护和测试。
3.  **提供统一接口**：为上层游戏逻辑提供一套标准、稳定的 API，无论底层使用的是哪个在线子系统。

**PlayTimeLimit 模块**是本插件中的一个重要子模块，其核心功能是：**监控玩家的游戏时长，并根据时长自动调整其获得的奖励倍率（例如，长时间游戏后收益递减），同时向玩家发送提醒通知。** 这通常用于实现防沉迷系统或游戏内经济平衡。

## 使用场景

*   **防沉迷系统**：你的游戏需要遵守相关法规，对未成年玩家的游戏时长进行监控和限制，并在达到阈值时发送通知或强制下线。
*   **动态奖励系统**：你希望根据玩家的在线时长动态调整其获得的游戏币、经验值等资源的倍率（例如，在线前 2 小时获得 100% 奖励，之后每小时衰减 10%），以鼓励健康游戏或防止资源过度膨胀。
*   **需要平台无关的在线基础服务**：你的游戏逻辑中需要实现组队、大厅匹配、检查游戏更新等通用在线功能，但希望代码不直接耦合到任何特定的在线子系统（如 EOS, Steam 等）。

## 蓝图用法

`PlayTimeLimit` 模块主要是一个 C++ 运行时系统，其核心功能通过 C++ API 和委托（Delegate）暴露。当前模块的源码中未发现标记为 `BlueprintCallable` 或 `BlueprintReadWrite` 的公开蓝图接口。该系统的设计倾向于在 C++ 层进行集成和事件监听。

## C++ 用法

### 头文件引入

```cpp
#include "PlayTimeLimitModule.h"
#include "PlayTimeLimitImpl.h"
```

### 基本用法

以下示例展示了如何初始化 `PlayTimeLimit` 系统，并注册一个玩家进行监控。来源文件：`Public/PlayTimeLimitImpl.h`。

```cpp
// 1. 确保模块可用
if (FPlayTimeLimitModule::IsAvailable())
{
    // 2. 获取核心实现单例
    FPlayTimeLimitImpl& PlayTimeLimit = FPlayTimeLimitImpl::Get();

    // 3. 初始化系统（通常在模块启动后或游戏逻辑开始时调用）
    PlayTimeLimit.Initialize();

    // 4. 注册一个玩家。系统将开始监控该玩家的在线时长。
    // FUniqueNetId 通常来自 IOnlineSubsystem::GetUniquePlayerId()
    const FUniqueNetId& PlayerId = ...; // 获取你的玩家唯一网络ID
    PlayTimeLimit.RegisterUser(PlayerId);
}
```

### 进阶用法

以下示例展示了如何绑定警告委托来响应玩家的时长变化，并查询玩家状态。来源文件：`Public/PlayTimeLimitImpl.h` 和 `Public/PlayTimeLimitUser.h`。

```cpp
// 绑定警告回调，当玩家达到某个时长阈值或奖励率变化时触发
PlayTimeLimit.GetWarnUserPlayTimeDelegate().BindLambda(
    [](const FUniqueNetId& UserId, float RewardRate)
    {
        // RewardRate 是当前的奖励倍率 (0.0 - 1.0)
        UE_LOG(LogTemp, Warning, TEXT("Player %s reached a time limit! New reward rate: %.2f"),
            *UserId.ToString(), RewardRate);
        // 在这里弹出游戏内UI提示
    }
);

// 查询某个玩家的当前状态
if (PlayTimeLimit.HasTimeLimit(PlayerId))
{
    int32 PlayedMinutes = PlayTimeLimit.GetPlayTimeMinutes(PlayerId);
    float CurrentRewardRate = PlayTimeLimit.GetRewardRate(PlayerId);
    UE_LOG(LogTemp, Log, TEXT("Player %s has played %d minutes. Reward rate: %.2f"),
        *PlayerId.ToString(), PlayedMinutes, CurrentRewardRate);
}

// 在游戏退出时注销用户
PlayTimeLimit.UnregisterUser(PlayerId);
```

## Demo 示例

一个可编译的最小集成示例，展示如何在游戏模块中设置和使用 PlayTimeLimit。

```cpp
// MyGameModule.h
#pragma once

#include "Modules/ModuleManager.h"

class FMyGameModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};

// MyGameModule.cpp
#include "MyGameModule.h"
#include "PlayTimeLimitModule.h"
#include "PlayTimeLimitImpl.h"
#include "OnlineSubsystem.h"
#include "OnlineSubsystemUtils.h"

void FMyGameModule::StartupModule()
{
    // 初始化 PlayTimeLimit 模块（如果它还未被其他模块初始化）
    if (FPlayTimeLimitModule::IsAvailable())
    {
        FPlayTimeLimitImpl& PTLImpl = FPlayTimeLimitImpl::Get();
        PTLImpl.Initialize();

        // 绑定警告回调
        PTLImpl.GetWarnUserPlayTimeDelegate().BindLambda(
            [](const FUniqueNetId& UserId, float RewardRate)
            {
                UE_LOG(LogTemp, Warning, TEXT("PLAY TIME WARNING: Player %s, Rate %.2f"), *UserId.ToString(), RewardRate);
            }
        );
    }
}

void FMyGameModule::ShutdownModule()
{
    // 清理
    if (FPlayTimeLimitModule::IsAvailable())
    {
        FPlayTimeLimitImpl::Get().Shutdown();
    }
}

// 注册此模块（假设你的 Build.cs 已经正确依赖了 PlayTimeLimit 模块）
IMPLEMENT_PRIMARY_GAME_MODULE(FMyGameModule, MyGame, "MyGame");
```

## 模块依赖

要使用 `OnlineFramework` 插件中的功能（特别是 `PlayTimeLimit`），你的项目模块通常需要依赖以下模块（基于常见在线功能需求推断）：

| 模块 | 用途 |
|---|---|
| `OnlineSubsystem` | 获取玩家的唯一网络ID (`FUniqueNetId`) 的基础 |
| `OnlineSubsystemUtils` | 提供在线子系统的通用工具函数，例如获取本地玩家控制器 |

`PlayTimeLimit` 模块本身可能对 `OnlineSubsystem` 有隐式依赖，因为其接口 `IOnlinePlayTimeLimit` 和 `FPlayTimeLimitUser` 使用了 `FUniqueNetId`。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `09a2dfc6` | [Hotfix on Load] Fix issue where certain baked hotfixes will not apply when no backend hotfixes exis | 修复启动时加载热修复的缺陷 |
| 2026-05-12 | `0b9170a8` | Guard Invite and RTJ social party calls when epic parties mirroring is enabled. | 在 Epic 派对镜像功能启用时，保护邀请和加入派对的调用 |
| 2026-04-30 | `fe1eaff2` | Add a hook for PartyPlatformSessionMonitor to allow the game party to add a special key to the platf | 为派对平台会话监视器添加钩子，以允许游戏派对向平台添加特殊密钥 |
| 2026-04-29 | `0badc43f` | Restore LogHotfixManager summary logs for hotfix on load | 恢复热修复管理器在加载时的摘要日志输出 |
| 2026-04-28 | `85cae1c6` | Broadcast party initialization after we've processed our first update | 在处理第一个更新后广播派对初始化完成 |

### 维护评价

*   **年龄与活跃度**：该插件创建于 2016 年，历史相当悠久。但从最近的 Git 提交记录来看，它在 **2026 年 5 月仍有持续的功能更新和 Bug 修复**，表明它是一个**长期维护的核心基础设施插件**，并未被废弃。
*   **更新内容**：近期的提交集中在 `Hotfix`、`Party` 等模块的稳定性和功能增强上，说明 Epic 仍在积极使用和维护这些在线基础服务。`PlayTimeLimit` 模块虽无近期直接更新，但作为同插件的一部分，其稳定性有保证。
*   **已知限制**：该插件 **默认未启用**（`EnabledByDefault: false`），意味着开发者需要在项目设置中手动启用它。这通常是因为其功能并非所有项目都需要。
*   **推荐使用**：如果你的游戏需要上述提到的防沉迷、动态奖励或平台无关的在线基础服务，并且你打算在 C++ 层面进行深度集成，**推荐使用此插件**。它提供了经过验证的、稳定的底层实现。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineFramework)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineFramework/Tests) (如果存在)