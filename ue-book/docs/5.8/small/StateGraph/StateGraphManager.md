# State Graph Manager

> Generic state machine management class.

| 属性 | 值 |
|---|---|
| 中文名 | 状态图管理器 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `StateGraphManager` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-08-02 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/StateGraph/Source/StateGraphManager) | |

## 用途

**StateGraphManager** 是 **StateGraph** 状态机框架的管理器模块。它的核心职责是为特定的游戏逻辑流程（如玩家登录、服务器注册等）提供一套标准、可复用的状态图实例化和管理机制。

它解决的主要问题是：避免在每个需要状态机的场景中重复编写创建、跟踪和销毁状态图实例的样板代码。通过提供基类 `FStateGraphManager` 和带跟踪功能的 `FStateGraphManagerTracked`，插件允许开发者专注于定义状态图内的步骤和逻辑，而将实例的生命周期管理交给管理器。该插件内已经为引擎的多个关键异步流程（PreLoginAsync, ClientJoin 等）提供了预置的管理器实现。

## 使用场景

- **游戏服务器开发**：当你正在开发一个多人在线游戏的服务器，需要处理玩家登录(`PreLogin`)、客户端加入(`ClientJoin`)、服务器重启(`RestartServer`)等复杂的、可能包含多个异步步骤的流程时，应使用该插件提供的对应管理器。
- **自定义复杂状态机**：当你需要在自己的游戏逻辑中（例如一个任务系统、一个过场动画序列）实现一个支持超时、可中途修改（热修复）的状态机，并希望将其与引擎的子系统集成以便统一管理时，可以基于 `FStateGraphManager` 或 `FStateGraphManagerTracked` 派生出自定义的管理器。
- **需要动态扩展状态**：如果你希望状态机的初始步骤不是硬编码的，而是由其他模块通过委托（Delegate）在运行时动态添加（例如，让不同的子系统注册自己关心的登录验证步骤），那么这套基于委托的创建机制非常适合。

## 蓝图用法

此插件提供的核心管理器类（如 `UPreLoginAsyncManager`, `UClientJoinManager`）均继承自 `UWorldSubsystem` 或 `UGameInstanceSubsystem`。它们的主要设计目标是服务于 C++ 模块，通过 `AddCreateDelegate` 注册 C++ 委托来扩展状态图。

在蓝图中，你可以**获取这些子系统实例**，但核心的 `Create` 和 `Find` 方法主要用于 C++ 逻辑内部。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Pre Login Async Manager` | 获取当前世界的 PreLoginAsync 状态图管理器子系统实例。 | `UPreLoginAsyncManager` |
| `Get Client Join Manager` | 获取当前游戏实例的 ClientJoin 状态图管理器子系统实例。 | `UClientJoinManager` |
| `Get Register Server Manager` | 获取当前世界的 RegisterServer 状态图管理器子系统实例。 | `URegisterServerManager` |
| `Get Restart Server Manager` | 获取当前世界的 RestartServer 状态图管理器子系统实例。 | `URestartServerManager` |

**使用示例（蓝图描述）**：
在蓝图中，你可以通过“Get World Subsystem”或“Get Game Instance Subsystem”节点获取到上述 Manager 对象。虽然你无法直接在蓝图图表中调用 `AddCreateDelegate`，但你可以观察这些子系统是否被正确初始化，或者在蓝图中触发依赖这些状态机流程的函数（例如，一个调用 `AGameModeBase::PreLogin` 的函数）。

## C++ 用法

### 头文件引入

根据你需要使用的具体管理器引入头文件：
```cpp
#include “StateGraphManager/Public/StateGraphManager.h” // 基类
#include “StateGraphManager/Public/PreLoginAsyncManager.h” // 预登录管理器
// 其他管理器头文件类似
```

### 基本用法

最基本的用法是获取内置的管理器，并通过它来创建状态图实例。

```cpp
// 来源：基于 Public/StateGraphManager.h 和 Public/PreLoginAsyncManager.h 的推断用法
// 假设在一个服务器游戏模式类中

// 1. 获取 PreLoginAsync 管理器（它是一个世界子系统）
UPreLoginAsyncManager* PreLoginManager = GetWorld()->GetSubsystem<UPreLoginAsyncManager>();
if (PreLoginManager)
{
    // 2. 通过管理器创建一个状态图实例
    UE::FStateGraphPtr StateGraph = PreLoginManager->Create(TEXT(“MyPreLoginContext_UniqueID”));
    
    // 3. 状态图创建后，其内部会执行已通过 AddCreateDelegate 注册的逻辑。
    //    你通常不需要在这里直接操作 StateGraph，而是通过 OnComplete 回调获取结果。
}
```

### 进阶用法

核心进阶用法是向管理器**注册自定义的委托**，以扩展状态机在创建时的初始步骤。这是实现模块化和热修复的关键。

```cpp
// 来源：基于 Public/StateGraphManager.h 的机制
// 假设在你的游戏模块的某个子系统初始化阶段

void UMyGameSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    
    // 获取目标管理器，例如 ClientJoinManager
    UClientJoinManager* ClientJoinManager = GetWorld()->GetSubsystem<UClientJoinManager>();
    if (ClientJoinManager)
    {
        // 注册一个委托，该委托将在每次通过此管理器创建状态图时被调用
        // 在委托中，你可以为状态图添加自定义的初始状态节点
        UE::FStateGraphManagerCreateDelegate MyCreateDelegate;
        MyCreateDelegate.BindUObject(this, &UMyGameSubsystem::OnCreateClientJoinStateGraph);
        
        ClientJoinManager->AddCreateDelegate(MyCreateDelegate);
    }
}

bool UMyGameSubsystem::OnCreateClientJoinStateGraph(UE::FStateGraph& StateGraph)
{
    // 在这里操作 StateGraph，例如添加一个自定义的“检查玩家存档”的状态节点
    // 添加成功返回 true，表示你已为此状态图贡献了逻辑。
    UE_LOG(LogMyGame, Log, TEXT(“Custom step added to ClientJoin state graph.”));
    // StateGraph.AddNode(...); // 假设的API
    return true;
}
```

**对于跟踪管理器** (`FStateGraphManagerTracked`)，你可以通过 `Find` 方法查询已存在的状态图实例。
```cpp
UE::FStateGraphPtr ExistingGraph = ClientJoinManager->Find(TEXT(“Player123_ConnectionID”));
if (ExistingGraph.IsValid())
{
    // 处理已存在的状态图...
}
```

## Demo 示例

以下是一个最简示例，展示如何自定义一个管理器并注册委托。

```cpp
// MyGameplayManager.h
#pragma once

#include “CoreMinimal.h”
#include “StateGraphManager/Public/StateGraphManager.h”

// 自定义一个跟踪管理器，用于管理“游戏内任务”的状态图
class UMyGameplayManager : public UGameInstanceSubsystem, public UE::FStateGraphManagerTracked
{
    GENERATED_BODY()

public:
    virtual FName GetStateGraphName() const override
    {
        return FName(“MyGameplayTask”);
    }
    
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

private:
    // 委托的实现函数
    bool InitializeTaskStateGraph(UE::FStateGraph& StateGraph);
};
```

```cpp
// MyGameplayManager.cpp
#include “MyGameplayManager.h”

void UMyGameplayManager::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    
    // 注册创建委托
    UE::FStateGraphManagerCreateDelegate InitDelegate;
    InitDelegate.BindUObject(this, &UMyGameplayManager::InitializeTaskStateGraph);
    AddCreateDelegate(InitDelegate);
    
    UE_LOG(LogTemp, Log, TEXT(“MyGameplayManager initialized with custom delegate.”));
}

void UMyGameplayManager::Deinitialize()
{
    Super::Deinitialize();
}

bool UMyGameplayManager::InitializeTaskStateGraph(UE::FStateGraph& StateGraph)
{
    // 在这里为任务状态图添加初始节点和转换逻辑
    // 例如：StateGraph.AddStartNode(…)
    // 例如：StateGraph.AddTransition(…)
    UE_LOG(LogTemp, Log, TEXT(“Initialized gameplay task state graph: %s”), *StateGraph.GetContextName());
    return true;
}
```

使用自定义管理器：
```cpp
// 在游戏逻辑中
UMyGameplayManager* TaskManager = GetGameInstance()->GetSubsystem<UMyGameplayManager>();
if (TaskManager)
{
    // 创建一个任务状态图，ContextName 应唯一标识这个任务实例
    UE::FStateGraphPtr TaskGraph = TaskManager->Create(TEXT(“Quest_FindTheSword_Instance1”));
    
    // 任务状态图此时已经通过委托被初始化，并开始运行。
    // 后续可以通过 TaskManager->Find() 来查找它。
}
```

## 模块依赖

从 `StateGraphManager.Build.cs` 分析，该模块依赖以下独特的模块：

| 模块 | 用途 |
|---|---|
| `StateGraph` | **核心依赖**。提供状态图 (`FStateGraph`) 的基础框架、节点和转换的定义。 |
| `OnlineSubsystem` | 用于处理 `FUniqueNetIdRepl`（玩家唯一网络ID），常见于网络登录流程。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `5b01134f` | Remove matchmaking attempt when CreateClientJoinStateGraph fails in TryMatchmaking. | 修复了当创建客户端加入状态图失败时，错误地尝试进行匹配的问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏统一迁移到新的 UE_LOGF 格式。 |
| 2026-02-10 | `0e0a7b5f` | UE: StateGraph remove timeout ticker when needed. | 优化了状态图的超时计时器，在不需要时及时移除以避免资源泄漏。 |
| 2025-12-09 | `bc24ccfb` | Complete PreLoginAsync stategraph with error if user disconnects before reaching PostLogin. | 增强了鲁棒性：如果玩家在到达 PostLogin 步骤前断开连接，状态图现在会正确地以错误状态完成。 |
| 2025-12-09 | `7a456323` | [Backout] - CL49078828 | 回滚了之前的一个提交。 |

### 维护评价

- **活跃维护**：从提交记录看，该插件在近一年内持续有功能增强、错误修复和代码优化的提交，维护非常活跃。
- **实验性**：插件明确标记为实验性 (`EnabledByDefault: false`)，这意味着其 API 可能不稳定，未来可能会有重大更改，不建议在追求稳定的生产项目中作为核心依赖使用。
- **推荐使用**：对于正在探索或开发基于状态图的复杂游戏流程（特别是多人游戏服务器逻辑）的开发者，这是一个值得关注和试用的高级框架。它可以显著提升复杂流程的模块化和可维护性。但由于其为实验性，建议在小型、非关键模块中先行尝试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/StateGraph/Source/StateGraphManager)
- [官方文档]() （暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/StateGraph/Tests/StateGraphTests)