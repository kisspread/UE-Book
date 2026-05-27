# USD Multi-User synchronization

> Enables opt-in multi-user synchronization for the USD Importer plugin.

| 属性 | 值 |
|---|---|
| 中文名 | USD多用户同步 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `USDMultiUser` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-03-05 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDMultiUser) | |

## 用途

这个插件解决了在多人协作环境中使用 USD 资产时的数据同步问题。当团队成员通过 Unreal 的 Multi-User Editing（Concert）系统协作时，USD Importer 导入的资产默认不会被纳入同步范围。本插件作为桥接层，将 USD Importer 的操作注册到 Multi-User Client 的事务过滤器（Transaction Filter）中，使得 USD 资产的导入和修改能够在多人会话中被正确传播。

简单来说：**没有这个插件，你的同事在多人编辑会话中导入或修改 USD 资产时，你什么也看不到。**

## 使用场景

- 你的团队使用 Multi-User Editing 进行关卡协作，同时需要导入/更新 USD 格式的资产（从 Maya、Houdini、Blender 等 DCC 工具导出）
- 你在做一个使用 USD 工作流的虚拟制片项目，多人需要实时看到 USD 场景的更新
- 你需要在多人编辑会话中保持 USD Stage Actor 的状态同步

## 蓝图用法

本插件不暴露任何蓝图节点。它是一个纯注册型插件，启用后自动将 USD Importer 的操作挂接到 Multi-User 事务系统中。

## C++ 用法

本插件仅包含一个 `Build.cs` 文件和模块注册代码，不提供公开的 C++ API。其功能通过模块初始化时自动注册事务过滤器实现，无需用户代码调用。

### 头文件引入

本插件无公开头文件，无需引入。

## Demo 示例

无。本插件为系统级桥接模块，启用即生效，无独立示例代码。

## 模块依赖

从 `.uplugin` 的 `Plugins` 字段提取：

| 模块 | 用途 |
|---|---|
| `MultiUserClient` | 提供多用户编辑（Concert）客户端框架，本插件将 USD 事务注册到该系统 |
| `USDImporter` | 提供 USD 资产导入功能，本插件为其添加多用户同步支持 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移，统一使用新格式化接口 |
| 2024-06-03 | `6f6faa16` | Change signature of IConcertClientTransactionBridge::RegisterTransactionFilter: replaces FTransactio... | 事务过滤器注册接口签名变更，适配新的事务桥接 API |
| 2024-05-31 | `177057a8` | [Backout] - CL34028050 | 回退上一次提交 |
| 2024-05-31 | `7dfa271c` | Change signature of IConcertClientTransactionBridge::RegisterTransactionFilter: replaces FTransactio... | 事务过滤器注册接口签名变更（后被回退） |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | Engine/Plugins 目录级别的批量改动 |

### 维护评价

- **创建时间**：2021 年 3 月，已存在约 5 年
- **更新频率**：更新极其稀少，5 年间仅有零星几次改动，且多为被动适配（API 签名变更、日志宏迁移）
- **当前状态**：⚠️ **实验性（Beta）**，且 `EnabledByDefault=false`，Epic 并未将其作为默认功能推广
- **代码规模**：仅 1 个源文件，功能单一，仅做桥接注册
- **推荐程度**：如果你正在使用 Multi-User Editing + USD 工作流，本插件是必需的；但它仍是 Beta 状态，可能在未来版本中发生变化或被整合进 USDImporter 主体

⚠️ **注意**：本插件标记为 `IsBetaVersion=true`，在生产环境中使用需谨慎。接口可能随引擎版本更新而变更（如 2024 年的事务桥接 API 签名变动）。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDMultiUser)
- [USDImporter 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter)
- [MultiUserClient 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/MultiUserClient)