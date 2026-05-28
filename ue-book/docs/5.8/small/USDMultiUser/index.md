# USD Multi-User synchronization

> Enables opt-in multi-user synchronization for the USD Importer plugin.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | USD多用户同步 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `USDMultiUser` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-03-05 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDMultiUser) | |

## 用途

该插件为 UE 的 USD (Universal Scene Description) 导入器 (`USDImporter`) 提供了**多用户同步（Multi-User Editing）** 功能。它通过将 USD 相关的资产操作（如创建、修改、删除图元）转换为可同步的“事务”，并利用 `MultiUserClient` 插件的框架，使得多个用户可以通过 Multi-User Editing 服务器在同一个 UE 会话中协作编辑 USD 资产。它解决了 USD 资产在多人协作编辑场景下的数据同步问题。

## 使用场景

- 你的团队正在使用 UE 的 USD 流程，并且需要多个艺术家或开发者**同时编辑同一个 USD 场景或资产**。
- 你需要在一个基于服务器的协作编辑环境（Multi-User Editing）中**追踪和同步 USD 层（Layer）或图元（Prim）的更改**。
- 你在开发需要整合 USD 和 Multi-User Editing 功能的工具链或管线。

## 蓝图用法

该插件主要提供 C++ 层面的集成，不包含可直接在蓝图中使用的函数节点。其核心功能是通过 C++ 类注册到 Multi-User 事务系统。

### 核心节点
该插件不提供蓝图可调用节点。

### 使用示例（蓝图描述）
不适用。

## C++ 用法

该插件的核心是提供一个基类，用于自定义 USD 操作的同步行为。用户需要创建该基类的子类来实现具体的同步逻辑。

### 头文件引入

```cpp
#include "USDMultiUser.h"
```

### 基本用法

**来源文件**: `Engine/Plugins/Importers/USDMultiUser/Source/USDMultiUser/Private/USDMultiUser.cpp`

要启用 USD 多用户同步，你需要创建一个 `FUSDMultiUser` 的子类并重写其方法。基本步骤是实现对 USD 操作的拦截和转换。

```cpp
// MyCustomUSDMultiUser.h
#pragma once
#include "USDMultiUser.h"

class FMyCustomUSDMultiUser : public FUSDMultiUser
{
public:
    // 重写以自定义事务过滤和操作转换
    virtual void RegisterTransactionFilter() override;
    virtual void UnregisterTransactionFilter() override;
};
```

### 进阶用法

结合 `IConcertClientTransactionBridge` 接口，你的自定义多用户类需要将 USD 操作（如添加、修改图元）转换为 `FConcertTransactionFinalized` 事务对象，并通过 `IConcertClientTransactionBridge::RegisterTransactionFilter` 方法注册一个过滤器，由 Multi-User 系统进行广播。

## Demo 示例

一个最小化的自定义 USD 多用户同步类实现。

```cpp
// MyCustomUSDMultiUser.h
#pragma once
#include "CoreMinimal.h"
#include "USDMultiUser.h"

class FMyCustomUSDMultiUser : public FUSDMultiUser
{
public:
    virtual void RegisterTransactionFilter() override;
    virtual void UnregisterTransactionFilter() override;

private:
    // 可以在此添加自定义的 USD 操作处理逻辑
    void HandleUSDOperation(/* 参数 */);
};
```

```cpp
// MyCustomUSDMultiUser.cpp
#include "MyCustomUSDMultiUser.h"

void FMyCustomUSDMultiUser::RegisterTransactionFilter()
{
    // 调用父类或 Multi-User 桥接接口来注册你的自定义过滤器
    // 例如，通过 IConcertClientTransactionBridge::RegisterTransactionFilter(...)
    UE_LOG(LogTemp, Log, TEXT("Custom USD Multi-User transaction filter registered."));
}

void FMyCustomUSDMultiUser::UnregisterTransactionFilter()
{
    // 注销过滤器
    UE_LOG(LogTemp, Log, TEXT("Custom USD Multi-User transaction filter unregistered."));
}

void FMyCustomUSDMultiUser::HandleUSDOperation(/* 参数 */)
{
    // 在此将具体的 USD 操作（如 UsdPrim 创建）转换为
    // Multi-User 事务系统可识别的格式。
}
```

## 模块依赖

该插件的模块 `USDMultiUser` 依赖于以下非标准核心模块（来自其 `Build.cs` 和插件依赖）：

| 模块 | 用途 |
|---|---|
| `USDMultiUser` | 提供 `FUSDMultiUser` 基类，是同步逻辑的核心 |
| `USD` | 处理 USD 资产的底层操作 |
| `USDExporter` | 与 USD 导出相关功能 |
| `USDStage` | 管理 USD 舞台（Stage） |
| `MultiUserClient` | 提供多用户编辑的客户端框架，是事务同步的基础 |
| `ConcertSyncClient` | 多用户同步的底层客户端实现 |
| `Concert` | 多用户同步的核心事务和协议定义 |

**注意**：使用者自己的模块还需要依赖 `USDMultiUser` 以及相关的 USD 模块（如 `USD`）来使用此功能。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF，属于引擎日志系统更新。 |
| 2024-06-03 | `6f6faa16` | Change signature of IConcertClientTransactionBridge::RegisterTransactionFilter: replaces FTransactio | 修改了多用户事务桥接口 `RegisterTransactionFilter` 的签名，是底层API变更。 |
| 2024-05-31 | `177057a8` | [Backout] - CL34028050 | 撤销了一次更改（CL34028050），可能是一次有问题的提交。 |
| 2024-05-31 | `7dfa271c` | Change signature of IConcertClientTransactionBridge::RegisterTransactionFilter: replaces FTransactio | 同上，修改了多用户事务桥接口签名。 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 引擎插件的通用维护或编译修复。 |

### 维护评价

- **创建时间**：该插件创建于 2021 年，是一个相对较新的功能插件。
- **更新频率**：最近的更新主要集中在 2024 年和 2026 年，间隔较长。更新内容多为适配 Multi-User 底层接口变更（如 `IConcertClientTransactionBridge`）和引擎通用日志系统迁移，**并非功能增强**。
- **维护状态**：**维护不活跃**。该插件自创建以来仅经历几次适配性更新，没有看到新功能的开发。其依赖的底层 Multi-User 框架接口（Concert）也在变化，这增加了维护成本。
- **实验性**：`.uplugin` 明确标记为 `IsBetaVersion: true`，表明它仍处于测试阶段，API 和功能可能不稳定。
- **推荐使用**：**谨慎使用**。该插件解决了特定场景（USD + 多用户编辑）的需求，但由于是实验性功能且更新维护节奏慢，在生产环境中使用前需充分测试，并准备好应对未来可能的接口变更。它更适合作为内部工具链或研究性用途。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDMultiUser)
- [官方文档]( ) （无）
- [测试用例]( ) （未发现专门的测试用例目录）