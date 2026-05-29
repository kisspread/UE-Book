# PlayTimeLimit

> Shared code for interacting with online gameplay services.（用于与在线游戏服务交互的共享代码。）

| 属性 | 值 |
|---|---|
| 中文名 | 游玩时长限制 |
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PlayTimeLimit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2016-07-13 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineFramework) | |

## 用途
PlayTimeLimit 模块实现了基于游玩时长的奖励衰减和通知系统。它并非一个简单的计时器，而是一个完整的游戏行为管理框架，允许游戏根据玩家已游玩的时间动态调整其获得的奖励倍率（例如经验、金币获取速率），并在特定时间点向玩家发送通知提醒。其核心目的是帮助游戏实现防沉迷机制或平衡游戏经济，确保长时间游玩的玩家不会获得不成比例的奖励优势，符合如中国市场对未成年人游戏时间的相关政策要求。

## 使用场景
- **合规性要求**：你的游戏需要在中国大陆等有严格防沉迷法规的市场上线，必须根据玩家游玩时长调整奖励。
- **游戏经济平衡**：你设计的开放世界或MMORPG希望鼓励玩家适度游戏，防止长时间“肝”导致经济体系崩溃或玩家疲劳。
- **家长控制功能**：你需要为游戏提供家长可监控的游戏时长报告和自动下线/惩罚机制。

## 蓝图用法
该模块的核心逻辑主要通过 C++ 接口暴露，未直接提供丰富的 `BlueprintCallable` 节点。其主要交互点在于通过 C++ 注册和管理玩家，并通过委托机制通知游戏逻辑。

### 核心节点（通过委托通知游戏逻辑）

虽然没有直接的蓝图节点，但其核心 `WarnUserPlayTime` 委托是蓝图与逻辑交互的桥梁。游戏需要在 C++ 中绑定此委托，然后将相关信息传递给蓝图或 UMG UI 来显示警告。

## C++ 用法
### 头文件引入

```cpp
#include "PlayTimeLimitImpl.h"
```

### 基本用法
模块主要通过其单例 `FPlayTimeLimitImpl` 进行控制。以下代码展示了典型的集成流程，包括初始化、注册用户和处理通知。

```cpp
// 在你的游戏实例或子系统中
#include "PlayTimeLimitImpl.h"
#include "OnlineSubsystem.h"
#include "OnlineSubsystemTypes.h"

// 1. 初始化（通常在模块加载后或游戏初始化时）
FPlayTimeLimitImpl& PlayTimeLimit = FPlayTimeLimitImpl::Get();
PlayTimeLimit.Initialize();

// 2. 绑定“警告用户”的委托，以便接收通知
PlayTimeLimit.GetWarnUserPlayTimeDelegate().BindLambda(
    [](const FUniqueNetId& UserId, int32 PlayTimeMinutes, float RewardRate, const FString& Title, const FString& Message, const FString& ButtonText)
    {
        // 在这里向玩家显示UI警告（例如，弹出一个UMG Widget）
        UE_LOG(LogTemp, Warning, TEXT("玩家 %s 已游玩 %d 分钟，当前奖励倍率 %.2f。标题：%s"), *UserId.ToString(), PlayTimeMinutes, RewardRate, *Title);
        // 例如: UMyGameUI::ShowPlaytimeWarning(UserId, Title, Message, ButtonText);
    }
);

// 3. 当玩家登录时，注册他们进行监控
FUniqueNetIdPtr PlayerUniqueId = GetLocalPlayerUniqueId(); // 从OnlineSubsystem获取
if (PlayerUniqueId.IsValid())
{
    PlayTimeLimit.RegisterUser(*PlayerUniqueId);
}

// 4. 当玩家登出时，取消注册
PlayTimeLimit.UnregisterUser(*PlayerUniqueId);

// 5. 在游戏主循环中进行 Tick，系统会自动检查并触发通知
// 通常在你自己的 Tick 函数或通过委托注册到 Ticker 中
PlayTimeLimit.Tick(DeltaTime);
```

*来源：基于 `Public/PlayTimeLimitImpl.h` 的 API 推断。*

### 进阶用法：测试与调试
`MockUser` 函数允许你快速测试通知和奖励衰减逻辑，而无需实际等待数小时。

```cpp
// 测试：假设一个玩家已游玩120分钟，并且有时间限制
FUniqueNetIdPtr TestPlayerUniqueId = /* ... */;
PlayTimeLimit.MockUser(*TestPlayerUniqueId, true /* bHasTimeLimit */, 120.0 /* CurrentPlayTimeMinutes */);

// 此后立即或在下一次 Tick 中，系统将根据配置的规则计算奖励率并可能触发通知。
// 你可以通过 Cheat 命令立即触发通知进行调试。
// 在控制台输入: `PlayTimeLimit.NotifyNow`
// 其 Exec 实现在 FPlayTimeLimitModule 中处理。
```
*来源：`Public/PlayTimeLimitImpl.h` 中的 `MockUser` 函数，以及 `Public/PlayTimeLimitModule.h` 中的 `Exec_Runtime` 函数。*

## Demo 示例
一个展示如何在你的游戏模块中集成 `PlayTimeLimit` 的最小示例。

**MyGameSubsystem.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "MyGameSubsystem.generated.h"

class IOnlineSubsystem;
class FPlayTimeLimitImpl;

UCLASS()
class MYGAME_API UMyGameSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

private:
    /** 处理玩家登录事件 */
    void OnPlayerLogin(int32 LocalUserNum, FUniqueNetIdPtr UniqueNetId, const FString& NetIdString);

    /** 游玩时长限制系统的单例引用 */
    FPlayTimeLimitImpl* PlayTimeLimitSystem = nullptr;
};
```

**MyGameSubsystem.cpp**
```cpp
#include "MyGameSubsystem.h"
#include "PlayTimeLimitImpl.h"
#include "OnlineSubsystem.h"
#include "OnlineSubsystemUtils.h"

void UMyGameSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);

    // 获取 PlayTimeLimit 系统
    if (FPlayTimeLimitModule::IsAvailable())
    {
        PlayTimeLimitSystem = &FPlayTimeLimitImpl::Get();
        PlayTimeLimitSystem->Initialize();
    }

    // 监听玩家登录事件
    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get();
    if (OnlineSub)
    {
        OnlineSub->AddOnLoginCompleteDelegate_Handle(0, FOnLoginCompleteDelegate::CreateUObject(this, &UMyGameSubsystem::OnPlayerLogin));
    }
}

void UMyGameSubsystem::Deinitialize()
{
    if (PlayTimeLimitSystem)
    {
        PlayTimeLimitSystem->Shutdown();
    }

    Super::Deinitialize();
}

void UMyGameSubsystem::OnPlayerLogin(int32 LocalUserNum, FUniqueNetIdPtr UniqueNetId, const FString& NetIdString)
{
    if (UniqueNetId.IsValid() && PlayTimeLimitSystem)
    {
        PlayTimeLimitSystem->RegisterUser(*UniqueNetId);
        UE_LOG(LogTemp, Log, TEXT("已为玩家 %s 注册游玩时长监控"), *UniqueNetId->ToString());
    }
}
```

## 模块依赖
`PlayTimeLimit` 模块的构建依赖相对标准，主要用于在线身份验证和核心游戏功能。

| 模块 | 用途 |
|---|---|
| `OnlineSubsystem` | 提供玩家唯一网络ID (`FUniqueNetId`) 和在线身份验证服务 |
| `OnlineSubsystemUtils` | 可能用于获取在线子系统的便捷工具 |

## 维护状态

### 近期更新
以下提交记录属于整个 `OnlineFramework` 插件，表明该插件仍在活跃维护，`PlayTimeLimit` 作为其子模块会随主插件一同更新和修复。

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `09a2dfc6` | [Hotfix on Load] Fix issue where certain baked hotfixes will not apply when no backend hotfixes exist | 修复加载时特定内置热修复在后端无热修复时不生效的问题 |
| 2026-05-12 | `0b9170a8` | Guard Invite and RTJ social party calls when epic parties mirroring is enabled. | 在启用 Epic 派对镜像时，保护邀请和加入派对的社交调用。 |
| 2026-04-30 | `fe1eaff2` | Add a hook for PartyPlatformSessionMonitor to allow the game party to add a special key to the platform | 为 PartyPlatformSessionMonitor 增加钩子，允许游戏派对向平台会话添加特殊键值。 |
| 2026-04-29 | `0badc43f` | Restore LogHotfixManager summary logs for hotfix on load | 恢复加载时 HotfixManager 的摘要日志输出。 |
| 2026-04-28 | `85cae1c6` | Broadcast party initialization after we've processed our first update | 在我们处理第一次更新后广播派对初始化事件。 |

### 维护评价
- **状态**：**活跃维护中**。`OnlineFramework` 作为 Epic 在线服务的核心框架插件，持续有功能更新和错误修复。
- **年龄**：插件创建于 2016 年，已超过 9 年，属于成熟组件。
- **推荐度**：**高**。如果你需要实现严格的基于时间的奖励衰减或防沉迷逻辑，这是一个官方且稳定的起点。但需注意，其核心价值在于底层规则引擎和通知调度，具体的玩家数据存储（如累计游玩时间）仍需你自行实现或与具体的 `OnlineSubsystem` 后端集成。
- **注意**：该插件默认未启用 (`EnabledByDefault=false`)，你需要在 `.uproject` 文件或编辑器中手动启用它。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineFramework/Source/PlayTimeLimit)
- [官方文档](https://docs.unrealengine.com) (无直接页面，属于高级在线子系统功能)