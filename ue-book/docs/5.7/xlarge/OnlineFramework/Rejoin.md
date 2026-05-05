# Online Framework Plugin

> Shared code for interacting with online gameplay services.（照抄，不翻译）

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

OnlineFramework 是一个大型的、模块化的在线游戏基础框架插件。它并非一个具体的在线子系统实现（如 EOS 或 Steam），而是提供了一套**与具体平台无关的、可复用的在线游戏功能组件**。这些组件解决了在线游戏中常见的、跨平台的通用问题，例如：玩家组队（Party）、大厅管理（Lobby）、游戏会话重连（Rejoin）、服务质量检测（QoS）、客户端热更新（Hotfix）、登录流程（LoginFlow）、补丁检查（PatchCheck）和游戏时间限制（PlayTimeLimit）。

它的存在是为了让游戏开发者能够快速集成标准化的在线功能，而无需从零开始实现这些复杂的逻辑，并且这些功能可以适配不同的在线子系统后端。

## 使用场景

- 你需要为你的多人游戏实现标准化的玩家组队和邀请系统 → 使用 `Party` 模块。
- 你的游戏需要一个自定义的、跨平台的大厅或房间系统 → 使用 `Lobby` 模块。
- 你希望玩家在意外断开后能快速重新加入正在进行的比赛 → 使用 `Rejoin` 模块。
- 你需要在游戏启动时检查并应用客户端的热修复补丁 → 使用 `Hotfix` 模块。
- 你的游戏需要一个统一的登录和身份验证流程界面 → 使用 `LoginFlow` 模块。
- 你需要在连接游戏服务器前检测网络延迟和质量 → 使用 `Qos` 模块。
- 你的游戏需要强制进行版本检查或内容更新 → 使用 `PatchCheck` 模块。
- 你的游戏需要遵守某些地区的防沉迷规定，限制玩家游戏时间 → 使用 `PlayTimeLimit` 模块。

## 蓝图用法

由于 OnlineFramework 是一个基础框架，其大部分核心逻辑在 C++ 层。蓝图接口主要暴露在各个子模块中。以下以 `Rejoin` 模块为例说明。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Check Rejoin Status` | 向后端查询当前玩家是否有可重连的比赛会话。 | `URejoinCheck` |
| `Rejoin Last Session` | 尝试重新加入上一次的游戏会话。 | `URejoinCheck` |
| `Get Rejoin Status` | 获取当前的重连状态枚举值。 | `URejoinCheck` |

### 使用示例（蓝图描述）

1.  **检查重连**：在玩家登录成功后，调用 `Check Rejoin Status` 节点。绑定 `On Rejoin Check Status Changed` 多播委托来监听状态变化。当状态变为 `RejoinAvailable` 时，UI 可以显示“重新加入比赛”的按钮。
2.  **执行重连**：当玩家点击“重新加入”按钮时，调用 `Rejoin Last Session` 节点。绑定 `On Rejoin Last Session Complete` 委托来处理重连结果（成功、失败、比赛已结束等）。

## C++ 用法

### 头文件引入

```cpp
#include "RejoinCheck.h"
```

### 基本用法

`URejoinCheck` 是一个抽象基类，你需要创建一个子类来实现具体的重连检查逻辑。以下是一个简化的子类框架。

```cpp
// MyRejoinCheck.h
#pragma once
#include "RejoinCheck.h"
#include "MyRejoinCheck.generated.h"

UCLASS()
class UMyRejoinCheck : public URejoinCheck
{
    GENERATED_BODY()

protected:
    // 实现具体的重连状态检查逻辑
    virtual void PerformRejoinCheck() override;
    // 实现具体的重连会话逻辑
    virtual void PerformRejoinLastSession() override;
};
```

```cpp
// MyRejoinCheck.cpp
#include "MyRejoinCheck.h"

void UMyRejoinCheck::PerformRejoinCheck()
{
    // 在这里调用你的在线子系统接口，查询玩家是否有进行中的会话
    // 例如：IOnlineSessionPtr SessionInterface = Online::GetSubsystem(GetWorld())->GetSessionInterface();
    // 查询完成后，调用 OnRejoinCheckComplete(ERejoinStatus::RejoinAvailable) 或 OnRejoinCheckComplete(ERejoinStatus::NoMatchToRejoin)
}

void UMyRejoinCheck::PerformRejoinLastSession()
{
    // 在这里实现加入之前会话的逻辑
    // 例如：SessionInterface->JoinSession(...)
    // 加入成功后，调用 OnRejoinLastSessionComplete(ERejoinAttemptResult::RejoinSuccess)
}
```

### 进阶用法

你可以将 `URejoinCheck` 子类集成到你的游戏流程管理器中，在合适的时机（如登录后、返回主菜单时）自动触发检查，并根据状态更新UI或执行自动重连。

## Demo 示例

以下是一个最小化的 `URejoinCheck` 子类示例，它模拟了检查和重连的过程。

```cpp
// SimpleRejoinCheck.h
#pragma once
#include "RejoinCheck.h"
#include "SimpleRejoinCheck.generated.h"

UCLASS()
class USimpleRejoinCheck : public URejoinCheck
{
    GENERATED_BODY()

public:
    USimpleRejoinCheck();

protected:
    virtual void PerformRejoinCheck() override;
    virtual void PerformRejoinLastSession() override;

private:
    // 模拟一个“可重连”的状态
    bool bHasRejoinableSession = true;
    FTimerHandle SimulateCheckTimerHandle;
};
```

```cpp
// SimpleRejoinCheck.cpp
#include "SimpleRejoinCheck.h"
#include "Engine/World.h"
#include "TimerManager.h"

USimpleRejoinCheck::USimpleRejoinCheck()
{
    // 模拟初始状态
    bHasRejoinableSession = FMath::RandBool();
}

void USimpleRejoinCheck::PerformRejoinCheck()
{
    // 模拟一个异步的后端检查
    if (UWorld* World = GetWorld())
    {
        World->GetTimerManager().SetTimer(SimulateCheckTimerHandle, [this]()
        {
            // 检查完成，根据模拟状态回调
            if (bHasRejoinableSession)
            {
                OnRejoinCheckComplete.ExecuteIfBound(ERejoinStatus::RejoinAvailable);
            }
            else
            {
                OnRejoinCheckComplete.ExecuteIfBound(ERejoinStatus::NoMatchToRejoin);
            }
        }, 1.0f, false); // 延迟1秒模拟网络请求
    }
}

void USimpleRejoinCheck::PerformRejoinLastSession()
{
    // 模拟重连尝试
    if (bHasRejoinableSession)
    {
        // 模拟成功
        OnRejoinLastSessionComplete.ExecuteIfBound(ERejoinAttemptResult::RejoinSuccess);
        bHasRejoinableSession = false; // 重连后状态改变
    }
    else
    {
        // 模拟失败
        OnRejoinLastSessionComplete.ExecuteIfBound(ERejoinAttemptResult::NothingToRejoin);
    }
}
```

## 模块依赖

从 `Rejoin.Build.cs` 分析，该模块依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `OnlineSubsystem` | 核心在线子系统接口，用于与具体的在线平台（如 EOS, Steam）交互。 |
| `OnlineSubsystemUtils` | 在线子系统的工具函数和辅助类。 |

## 维护状态

### 近期更新

```
- a60b2b5c1723 Fixup API macros for merged modules, PURE_VIRTUAL does not need API export
- 93a13080d9ef Used LyraGame build target to find and convert all files to have dllstorage on methods/staticvar instead of on types.
- 66e9bb39ff7e Removed all #if UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes from the code base
```
最近的提交主要是代码维护性工作：修复API宏、统一DLL导出符号规范、清理废弃的预处理指令。没有新的功能特性。

### 维护评价

OnlineFramework 插件创建于 2016 年，是一个历史悠久的“老古董”级插件。从最近的提交记录看，它仍在被 Epic Games 维护，但更新内容主要是为了适应引擎版本升级（如 5.2, 5.6）和代码规范统一，属于**维护性更新**，而非功能性迭代。

**优点**：作为官方插件，其架构稳定，经过了大量项目的检验，是构建复杂在线功能的可靠基础。
**缺点**：由于其抽象和模块化的设计，直接使用需要开发者自行实现每个子模块的具体逻辑（如 `URejoinCheck` 的子类），学习曲线较陡。且默认禁用，需要开发者主动集成。

**结论**：推荐需要构建标准化、跨平台在线功能的中大型项目使用。对于小型项目或只需特定在线功能的项目，直接使用对应的在线子系统（OnlineSubsystem）可能更简单直接。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineFramework)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineFramework/Tests) (如果存在)