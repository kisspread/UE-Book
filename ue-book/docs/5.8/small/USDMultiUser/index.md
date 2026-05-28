# USD Multi-User synchronization

> Enables opt-in multi-user synchronization for the USD Importer plugin.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | USD多人同步 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `USDMultiUser` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-03-05 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDMultiUser) | |

## 用途

本插件是 `USDImporter` 插件的扩展，专为 Unreal Engine 的**多人编辑（Multi-User Editing）** 功能设计。它解决了在多人协作编辑同一关卡时，如何同步 USD（Universal Scene Description）数据变更的问题。没有此插件，通过 `USDImporter` 插件导入或编辑的 USD 资产（如网格体、材质等）在多人会话中不会被自动同步，导致不同客户端看到的状态不一致。本插件通过监听和同步 USD 相关的操作，确保所有参与者都能看到一致的 USD 数据修改。

## 使用场景

- 你的团队使用 Unreal Engine 的多人编辑功能进行关卡协作。
- 你导入了 USD 格式的资产（例如来自 Maya、Houdini 或 Blender），并需要在多人会话中对其进行实时修改和同步。
- 你需要确保团队中一个人对 USD 资产所做的变换、材质或几何体修改，能实时反映到其他所有成员的编辑器中。

## 蓝图用法

本插件主要提供后台同步功能，其核心节点并非直接暴露给蓝图使用，而是作为 `MultiUserClient` 和 `USDImporter` 插件之间的桥梁自动运行。启用该插件后，在多人编辑会话中对 USD 资产的**蓝图**操作（例如通过蓝图脚本修改 USD Stage 的属性）应能被自动同步。具体的同步逻辑是自动化的，无需在蓝图中直接调用特定函数。

## C++ 用法

该插件的用法主要体现在其模块依赖和作为“粘合剂”的自动注册行为。在 C++ 代码层面，你通常**不直接**调用该插件提供的函数，而是依赖其自动生效的同步机制。

### 头文件引入

无需直接引入。插件的 `USDMultiUser` 模块类型为 `UncookedOnly`，其功能在编辑器打包/开发环境中自动生效。

### 基本用法

1.  **启用插件**：在你的项目插件列表中启用 `USDMultiUser`。
2.  **启动多人会话**：像往常一样通过 `Multi-User Editing` 面板启动或加入一个会话。
3.  **编辑 USD 资产**：在参与多人会话的任意编辑器实例中，使用 `USDImporter` 插件的功能导入或编辑 USD Stage。你的修改应会自动同步给会话中的其他参与者。

### 进阶用法

插件的核心代码通过实现 `IConcertClientTransactionBridge::RegisterTransactionFilter` 来注册一个事务过滤器。这个过滤器会拦截与 USD 相关的编辑器事务（Transaction），并将其序列化为可在网络上传输的格式，从而实现同步。

```cpp
// 概念性代码，展示插件如何注册其同步逻辑
// 来源：插件模块初始化代码
void FUSDMultiUserModule::StartupModule()
{
    // 注册一个事务过滤器，用于处理USD相关的操作同步
    if (IConcertClientTransactionBridge* TransactionBridge = ...)
    {
        TransactionBridge->RegisterTransactionFilter(
            MakeShared<FUSDMultiUserTransactionFilter>()
        );
    }
}
```

## Demo 示例

本插件无需单独的 Demo 项目。其效果通过启用插件后，在多人编辑工作流中体现。

**验证步骤：**
1.  在两台或多台机器上打开同一个 Unreal Engine 项目。
2.  在所有实例中启用 `USDMultiUser` 和 `USDImporter` 插件。
3.  使用一台机器作为“服务器”发起多人会话，其他机器加入。
4.  在**客户端A**上导入一个 USD 文件，并将其放置到关卡中。
5.  在**客户端B**上，观察 USD 资产是否出现。
6.  在**客户端A**上移动该 USD 资产，或在**USD Stage**窗口修改其属性。
7.  验证**客户端B**是否实时看到了相同的修改。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MultiUserClient` | 提供多人编辑客户端的核心功能和接口，是本插件服务的目标。 |
| `USDImporter` | 提供 USD 资产导入和编辑的基础功能，本插件负责将其操作同步化。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志系统迁移，将旧版 UE_LOG 宏替换为新版 UE_LOGF。 |
| 2024-06-03 | `6f6faa16` | Change signature of IConcertClientTransactionBridge::RegisterTransactionFilter: replaces FTransactio | 底层接口签名变更，使用新的事务过滤器类型。 |
| 2024-05-31 | `177057a8` | [Backout] - CL34028050 | 回退了一次之前的提交（可能是因引入问题）。 |
| 2024-05-31 | `7dfa271c` | Change signature of IConcertClientTransactionBridge::RegisterTransactionFilter: replaces FTransactio | 尝试修改接口签名，但随后被回退。 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 引擎插件目录的通用维护性提交。 |

### 维护评价

该插件创建于 2021 年，标记为**实验性（Beta）**，且**默认未启用**。从提交历史看，其最近的更新（2026年）仅是日志宏迁移，无功能性改动。之前的实质性改动停留在 2024 年年中，且主要是适应底层 `MultiUserClient` 插件的接口变更，而非插件自身功能增强。最近一次明确的功能性相关更新在 2023 年初。综合来看，该插件处于**维护不活跃**状态，更像一个依赖于 `MultiUserClient` 和 `USDImporter` 的“胶水”模块，功能已基本完成且稳定，但可能缺乏对新 UE 版本的主动适配和功能扩展。**推荐在需要 USD 多人同步功能的项目中谨慎使用，并充分测试其与当前引擎版本的兼容性。**

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDMultiUser)
- [官方文档]()（无）
- [测试用例]()（未提供）