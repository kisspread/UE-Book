# PlayTimeLimit

> Shared code for interacting with online gameplay services.

| 属性 | 值 |
|---|---|
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `Qos` (Runtime), `Party` (Runtime), `Lobby` (Runtime), `Hotfix` (Runtime), `LoginFlow` (Runtime), `PatchCheck` (Runtime), `PlayTimeLimit` (Runtime), `Rejoin` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2016-07-12 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineFramework) | |

## 用途

PlayTimeLimit 是 OnlineFramework 插件中的一个子模块，专门用于**根据玩家游戏时长动态调整奖励倍率**。该系统解决的核心问题是：在需要实施游戏时长限制的地区（如中国、韩国等对未成年人有游戏时长法规要求的市场），游戏需要监控每个玩家的在线时长，并在超过阈值后降低游戏内奖励（如经验值、金币等），甚至在达到上限时强制退出游戏。

该模块提供：
- **用户注册/注销**：将需要监控的玩家注册到系统中
- **时长追踪**：实时追踪每个玩家的累计游戏时间
- **奖励倍率调整**：根据配置的时间阈值自动降低奖励倍率（如 100% → 50% → 0%）
- **通知系统**：定期向玩家发送游戏时长提醒通知
- **Mock 测试支持**：提供 Mock 用户实现，方便在不实际等待数小时的情况下测试系统行为
- **游戏退出请求**：当时长达到上限时触发退出游戏的委托

## 使用场景

- 你的游戏需要在中国大陆或韩国等地区上线，需要遵守未成年人游戏时长限制法规
- 你需要实现"疲劳系统"，让长时间游戏的玩家获得递减的奖励
- 你需要在玩家游戏超过一定时长后发送提醒通知
- 你需要在开发阶段快速测试时长限制逻辑，而不必真正等待数小时

## 蓝图用法

PlayTimeLimit 模块主要面向 C++ 层，没有暴露 BlueprintCallable 节点。该模块通过 `IOnlinePlayTimeLimit` 接口和 `FPlayTimeLimitImpl` 单例进行交互，属于底层在线服务框架。

## C++ 用法

### 头文件引入

```cpp
#include "PlayTimeLimitImpl.h"
#include "PlayTimeLimitModule.h"
```

### 基本用法

**注册玩家并查询游戏时长状态**

```cpp
// 获取 PlayTimeLimit 实现的单例
FPlayTimeLimitImpl& PlayTimeLimit = FPlayTimeLimitImpl::Get();

// 初始化系统（通常在模块启动时调用）
PlayTimeLimit.Initialize();

// 注册一个需要监控的玩家
FUniqueNetIdRef UserId = /* 获取玩家的唯一网络 ID */;
PlayTimeLimit.RegisterUser(UserId);

// 查询玩家是否有时间限制
bool bHasLimit = PlayTimeLimit.HasTimeLimit(UserId);

// 查询玩家当前的游戏时长（分钟）
int32 PlayMinutes = PlayTimeLimit.GetPlayTimeMinutes(UserId);

// 查询当前奖励倍率（1.0 = 正常，0.5 = 半额，0.0 = 无奖励）
float RewardRate = PlayTimeLimit.GetRewardRate(UserId);
```

### 进阶用法

**配置时间阈值与奖励倍率**

系统通过 `FOnlinePlayLimitConfigEntry` 配置多个时间阶梯：

```cpp
// 配置示例（通常从配置文件读取）：
// 玩家游戏 60 分钟后，奖励降至 50%，每 30 分钟通知一次
FOnlinePlayLimitConfigEntry Entry1(60, 30, 0.5f);

// 玩家游戏 120 分钟后，奖励降至 0%，每 15 分钟通知一次
FOnlinePlayLimitConfigEntry Entry2(120, 15, 0.0f);
```

**监听游戏退出请求**

```cpp
// 绑定游戏退出请求委托
FPlayTimeLimitImpl& PlayTimeLimit = FPlayTimeLimitImpl::Get();

PlayTimeLimit.OnGameExitRequested.AddLambda([]()
{
    // 当所有监控用户都达到时长上限时触发
    // 执行退出游戏逻辑，例如返回主菜单或显示退出提示
    UE_LOG(LogPlayTimeLimit, Warning, TEXT("Play time limit reached, requesting game exit"));
});
```

**使用 Mock 用户进行测试**

```cpp
// 在非 Shipping 构建中，可以使用 Mock 用户快速测试
#if ALLOW_PLAY_LIMIT_MOCK
// 模拟一个有 2 小时时间限制、已玩 90 分钟的玩家
PlayTimeLimit.MockUser(UserId, /*bHasTimeLimit=*/true, /*CurrentPlayTimeMinutes=*/90.0);

// 模拟一个没有时间限制的玩家
PlayTimeLimit.MockUser(UserId2, /*bHasTimeLimit=*/false, 0.0);
#endif

// 立即触发通知（调试用）
PlayTimeLimit.NotifyNow();
```

**自定义用户实现**

```cpp
// 继承 FPlayTimeLimitUser 实现平台特定的时长追踪
class FMyPlatformPlayTimeUser : public FPlayTimeLimitUser
{
public:
    FMyPlatformPlayTimeUser(const FUniqueNetIdRef& InUserId)
        : FPlayTimeLimitUser(InUserId)
    {}

    virtual bool HasTimeLimit() const override
    {
        // 从平台服务查询该用户是否有时间限制
        return MyPlatformService->HasPlayTimeRestriction(UserId);
    }

    virtual int32 GetPlayTimeMinutes() const override
    {
        // 从平台服务获取累计游戏时长
        return MyPlatformService->GetAccumulatedPlayMinutes(UserId);
    }

    virtual float GetRewardRate() const override
    {
        // 根据当前时长计算奖励倍率
        int32 Minutes = GetPlayTimeMinutes();
        if (Minutes >= 120) return 0.0f;
        if (Minutes >= 60) return 0.5f;
        return 1.0f;
    }
};
```

## Demo 示例

**PlayTimeLimitSubsystem.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "PlayTimeLimitSubsystem.generated.h"

/**
 * 游戏实例子系统，封装 PlayTimeLimit 的生命周期管理
 */
UCLASS()
class MYGAME_API UPlayTimeLimitSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

    /** 注册本地玩家到时长监控系统 */
    void RegisterLocalPlayer(int32 LocalPlayerIndex);

    /** 获取当前奖励倍率 */
    UFUNCTION(BlueprintPure, Category = "Play Time Limit")
    float GetRewardRate() const;

    /** 获取当前游戏时长（分钟） */
    UFUNCTION(BlueprintPure, Category = "Play Time Limit")
    int32 GetPlayTimeMinutes() const;

private:
    FDelegateHandle GameExitDelegateHandle;
};
```

**PlayTimeLimitSubsystem.cpp**

```cpp
#include "PlayTimeLimitSubsystem.h"
#include "PlayTimeLimitImpl.h"

void UPlayTimeLimitSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);

    if (FPlayTimeLimitModule::IsAvailable())
    {
        FPlayTimeLimitImpl& Impl = FPlayTimeLimitImpl::Get();
        Impl.Initialize();

        // 绑定游戏退出请求
        GameExitDelegateHandle = Impl.OnGameExitRequested.AddLambda([]()
        {
            UE_LOG(LogTemp, Warning, TEXT("Play time limit reached!"));
        });
    }
}

void UPlayTimeLimitSubsystem::Deinitialize()
{
    if (FPlayTimeLimitModule::IsAvailable())
    {
        FPlayTimeLimitImpl& Impl = FPlayTimeLimitImpl::Get();
        if (GameExitDelegateHandle.IsValid())
        {
            Impl.OnGameExitRequested.Remove(GameExitDelegateHandle);
        }
        Impl.Shutdown();
    }

    Super::Deinitialize();
}

void UPlayTimeLimitSubsystem::RegisterLocalPlayer(int32 LocalPlayerIndex)
{
    if (!FPlayTimeLimitModule::IsAvailable()) return;

    // 获取本地玩家的唯一网络 ID 并注册
    // FUniqueNetIdRef PlayerId = GetLocalPlayerNetId(LocalPlayerIndex);
    // FPlayTimeLimitImpl::Get().RegisterUser(PlayerId);
}

float UPlayTimeLimitSubsystem::GetRewardRate() const
{
    if (!FPlayTimeLimitModule::IsAvailable()) return 1.0f;
    // return FPlayTimeLimitImpl::Get().GetRewardRate(LocalUserId);
    return 1.0f;
}

int32 UPlayTimeLimitSubsystem::GetPlayTimeMinutes() const
{
    if (!FPlayTimeLimitModule::IsAvailable()) return 0;
    // return FPlayTimeLimitImpl::Get().GetPlayTimeMinutes(LocalUserId);
    return 0;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `OnlineSubsystemUtils` | 在线子系统工具函数 |
| `OnlineSubsystem` | 核心在线子系统接口（提供 `FUniqueNetId` 等类型） |

## 维护状态

### 近期更新

```
- 2415c7aa20ad Fix two types of nodiscard warnings seen when building with Clang 20
- 93a13080d9ef Used LyraGame build target to find and convert all files to have dllstorage on methods/staticvar instead of on types.
- 66e9bb39ff7e Removed all #if UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes from the code base
```

以上三次提交均为编译兼容性修复（Clang 20 警告、DLL 导出符号、头文件包含顺序清理），没有功能性更新。

### 维护评价

PlayTimeLimit 模块自 2016 年创建以来已有约 9 年历史。该模块属于 OnlineFramework 的一部分，是一个相对稳定的基础设施模块。近期的提交均为编译器兼容性维护，没有新功能开发，说明该模块已进入**成熟稳定期**。

**注意事项**：
- 该插件默认未启用（`EnabledByDefault: false`），需要在项目设置中手动启用
- Mock 功能仅在非 Shipping 构建中可用（`ALLOW_PLAY_LIMIT_MOCK` 宏控制）
- 该模块主要面向需要遵守特定地区法规的游戏项目，通用性有限
- 推荐在需要实现游戏时长限制功能时使用，但需注意该模块本身不包含平台特定实现，需要配合具体的 OnlineSubsystem 使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineFramework)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineFramework/Source/PlayTimeLimit)