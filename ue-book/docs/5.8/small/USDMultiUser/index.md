# USD Multi-User synchronization

> Enables opt-in multi-user synchronization for the USD Importer plugin.

| 属性 | 值 |
|---|---|
| 中文名 | USD多人同步 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `USDMultiUser` (UncookedOnly) |
| 实验性 | ⚦ 是 |
| 创建时间 | 2021-03-05 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDMultiUser) | |

## 用途

USDMultiUser 插件为 Unreal Engine 的 USD Importer 插件提供了**多人实时协作编辑 USD 场景**的能力。它解决了在多人编辑（Multi-User Editing）会话中，基础 USD 导入器可能产生的状态不一致或冲突问题。该插件通过将 USD 相关的操作（如 Stage 打开、修改、保存）转换为可被多人会话同步的“事务”（Transaction），确保所有参与者的 USD 资产状态保持一致。它本质上是连接 USD 导入器和多人编辑系统（Concert）的桥梁，使 USD 工作流能够无缝融入 UE 的协作开发流程中。

## 使用场景

- **团队协作构建大型虚拟场景**：你的团队正在使用 USD 格式构建一个复杂的影视或建筑可视化场景。你需要多人同时打开同一个 USD Stage，并对其中的 Prim 进行移动、缩放、材质修改等操作，所有人的修改需要实时同步给其他人。
- **需要版本控制的 USD 资产迭代**：你正在使用 Multi-User Editing 进行基于会话的版本管理和协作，同时项目中大量资产以 USD 格式管理。启用此插件后，确保 USD 资产的修改也被纳入版本控制的范围。
- **混合工作流**：项目同时使用了 UE 的原生资产和 USD 资产。你希望整个团队都能在一个统一的编辑环境中工作，无论他们操作的是哪种格式的资产。

**注意**：此插件是**可选**且**实验性**的。启用它需要你的项目同时依赖 `USDImporter` 和 `MultiUserClient` 插件。请仅在明确需要多人协作编辑 USD 场景时启用。

## 蓝图用法

该插件主要通过 C++ 在引擎初始化阶段与底层多人同步系统集成，提供的蓝图节点较少，侧重于模块的初始化和生命周期管理。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Initialize` | 初始化 USD 多人同步模块，注册事务过滤器以同步 USD 操作。通常由引擎自动调用。 | `USDMultiUserSubsystem` |
| `Shutdown` | 清理并关闭 USD 多人同步模块。 | `USDMultiUserSubsystem` |

### 使用示例（蓝图描述）

在蓝图中直接使用该插件的场景非常有限，因为其核心逻辑是“幕后”自动运行的。典型的使用流程如下：

1.  **项目设置**：在项目设置中同时启用 `USDMultiUser`、`USDImporter` 和 `MultiUserClient` 插件。
2.  **启动多人会话**：使用标准的 Multi-User Editing 功能建立或加入一个编辑会话。
3.  **操作 USD 资产**：在编辑器中正常打开、编辑一个 USD Stage 或其包含的 Actor/Component。
4.  **自动同步**：`USDMultiUser` 插件会拦截你的 USD 操作，将其转化为事务并发送给服务器，再同步给会话中的其他参与者。其他参与者会自动看到对应的 USD 场景变化。

你通常不需要在蓝图中手动调用 `Initialize`，因为它会在模块加载时（`PostEngineInit` 阶段）自动执行。

## C++ 用法

该插件主要为引擎内部服务，但了解其 C++ 接口有助于理解其工作原理或进行深度定制。

### 头文件引入

```cpp
#include "USDMultiUser.h"
```

### 基本用法

插件的核心是自动注册一个事务过滤器。以下是一个简化的概念性代码，展示了插件内部可能的初始化逻辑（实际实现在插件模块的 `StartupModule` 中）：

```cpp
// 假设这是在某个模块初始化时（例如 USDMultiUserSubsystem）
#include "IConcertClientTransactionBridge.h"

void SomeInitializationFunction()
{
    // 获取多人编辑的事务桥接接口
    IConcertClientTransactionBridge* TransactionBridge = IConcertClientTransactionBridge::Get();
    if (TransactionBridge)
    {
        // 注册一个自定义的事务过滤器，用于处理 USD 相关的资产操作
        TransactionBridge->RegisterTransactionFilter(MyUSDTransactionFilter);
    }
}
```
*来源：基于 `IConcertClientTransactionBridge` 接口和插件注册逻辑推断。*

### 进阶用法

在多人会话中，USD 操作最终会被转换为 `UConcertClientTransactionBridge` 能理解的事务对象。开发者如果想扩展或调试此行为，可以研究如何将自定义的 USD 修改操作（例如通过 `UsdUtils` 修改了一个 Prim 的属性）封装成一个标准的 UE 事务（`FTransaction`），以便被多人会话系统捕获和同步。

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何在自定义模块中检查或引用 USD 多人同步的状态。这并非插件本身的典型用法，而是展示与其进行基础交互的可能。

**MyActor.h**
```cpp
// MyActor.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyActor.generated.h"

UCLASS()
class AMyActor : public AActor
{
    GENERATED_BODY()

public:
    AMyActor();

    // 检查 USD 多人同步模块是否加载并初始化
    UFUNCTION(BlueprintCallable, Category = "USD")
    bool IsUSDMultiUserActive() const;
};
```

**MyActor.cpp**
```cpp
// MyActor.cpp
#include "MyActor.h"
#include "Modules/ModuleManager.h"

AMyActor::AMyActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

bool AMyActor::IsUSDMultiUserActive() const
{
    // 检查 ‘USDMultiUser’ 模块是否已加载
    // 这只是一个检查示例，实际使用中插件的状态管理更为复杂
    return FModuleManager::Get().IsModuleLoaded(TEXT("USDMultiUser"));
}
```

## 模块依赖

要在你的项目中使用或依赖此插件，需要在你的模块 `.Build.cs` 文件中添加对以下**独特**模块的依赖：

| 模块 | 用途 |
|---|---|
| `USDImporter` | 核心 USD 导入和编辑功能，是本插件的基础。 |
| `MultiUserClient` (或 `ConcertClient`) | 提供多人编辑和会话同步的客户端核心功能。 |
| `Concert` | 多人同步系统的底层事务和通信框架。 |

`USDMultiUser` 模块本身是 `UncookedOnly` 类型，意味着它仅在编辑器或未打包的开发版本中加载。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式日志宏迁移到新的 `UE_LOGF` 格式，属于代码现代化。 |
| 2024-06-03 | `6f6faa16` | Change signature of IConcertClientTransactionBridge::RegisterTransactionFilter: replaces FTransactio... | 修改了多人事务桥接接口的注册方法签名，属于底层 API 变更。 |
| 2024-05-31 | `177057a8` | [Backout] - CL34028050 | 回滚了一次之前的代码提交，说明可能修复了引入的兼容性问题。 |
| 2024-05-31 | `7dfa271c` | Change signature of IConcertClientTransactionBridge::RegisterTransactionFilter: replaces FTransactio... | 与 `6f6faa16` 类似，是对多人事务桥接口签名的修改尝试（后被回滚）。 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 一次涉及引擎插件的通用改动或合并。 |

### 维护评价

**综合评价：维护中，但有明确限制。**

1.  **活跃度**：插件在近一年内仍有活动（2024年），主要涉及跟随底层多人同步框架（Concert）的 API 变更和日志系统更新，表明它仍在随引擎主版本维护。
2.  **成熟度**：插件自 2021 年创建，已存在约 4 年，但仍标记为 `IsBetaVersion: true`。这表明其 API 和功能可能尚未完全稳定，未来可能会有变化。
3.  **状态**：属于 `UncookedOnly` 的实验性插件，仅在需要时手动启用。这是一个非常小众的功能，服务于特定的协作工作流。
4.  **推荐**：如果你的团队**必须**进行多人实时协作编辑 USD 场景，且能够接受 Beta 状态可能带来的限制或未来变更，那么此插件是必要的。对于单人开发或不需要实时 USD 协作的项目，则无需启用。

**警告**：该插件是实验性的 Beta 版本，在升级引擎版本时需特别注意兼容性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDMultiUser)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDMultiUser/Tests)