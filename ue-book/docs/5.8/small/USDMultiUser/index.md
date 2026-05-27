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
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDMultiUser) | |

## 用途

该插件的核心功能是为 Unreal Engine 的 USD 导入/导出流程（由 `USDImporter` 插件提供）添加多人协作（Multi-User）同步支持。它通过注册事务（Transaction）过滤器，确保 USD 资产的导入和修改操作能够被多人会话（Concert）系统正确地识别、同步和冲突解决，从而允许团队在同一个 USD 场景中进行实时协作。

## 使用场景

- **团队协作处理 USD 资产**：当美术师、动画师和技术美术（TA）在同一个 USD 场景（例如 Pixar USD 格式的动画场景或复杂场景资产）上工作时，使用此插件可以将各自的修改实时同步给其他协作者。
- **使用 Multi-User Editing 功能**：你的项目启用了 Unreal Engine 内置的多用户编辑（Multi-User Editing）功能，并且需要确保在编辑 USD 格式的资产（如通过 USD Stage 窗口导入）时，这些操作能够正确地广播给会话中的其他参与者，而不是仅在本地生效。

## 蓝图用法

此插件是作为底层同步桥接层存在的，主要面向引擎和 C++ 系统集成，不直接暴露蓝图节点。其功能在 `USDImporter` 插件提供的 USD Stage 等编辑器工具中自动生效。

## C++ 用法

此插件是一个 `UncookedOnly` 类型的编辑器扩展模块，主要工作在编辑器管线内部，不面向游戏运行时。其内部通过实现并注册 `IConcertClientTransactionBridge` 的过滤器来拦截和处理特定于 USD 的事务。

## Demo 示例

此插件作为内部功能扩展，无需也不提供直接使用的独立示例。其效果通过 `USDImporter` 插件的功能体现。

## 模块依赖

此插件声明了对以下其他插件的依赖，使用者需要确保这些插件已启用：

| 插件 | 用途 |
|---|---|
| `MultiUserClient` | 提供多用户协作编辑的核心客户端功能和事务桥接接口。 |
| `USDImporter` | 提供 USD 资产的导入、导出和场景编辑功能，是本插件进行同步的目标。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF。 |
| 2024-06-03 | `6f6faa16` | Change signature of IConcertClientTransactionBridge::RegisterTransactionFilter: replaces FTransactio | 更改了多用户事务桥接口的注册过滤器函数签名。 |
| 2024-05-31 | `177057a8` | [Backout] - CL34028050 | 回滚了之前的某个改动（CL34028050）。 |
| 2024-05-31 | `7dfa271c` | Change signature of IConcertClientTransactionBridge::RegisterTransactionFilter: replaces FTransactio | （同 6f6faa16）更改了多用户事务桥接口的注册过滤器函数签名。 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 属于引擎插件目录下的常规维护或整理提交。 |

### 维护评价

该插件自 2021 年创建，已有 5 年历史。尽管它是一个 `IsBetaVersion=true` 且 `EnabledByDefault=false` 的实验性功能，但其**维护状态较为活跃**。最近一次功能性更新记录在 2024 年，涉及适配底层多人编辑 API 的签名变更，这表明它仍在与引擎的核心多用户系统保持同步更新。2026 年的日志迁移也说明它被纳入了引擎的常规现代化维护中。

对于需要在多人会话中协作处理 USD 资产的团队，**推荐使用此插件**。但需注意其“实验性”标签，意味着 API 或行为在未来版本中仍有变动的可能性。使用前请确保 `MultiUserClient` 和 `USDImporter` 插件已正确启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDMultiUser)
- [官方文档]() (无)
- [测试用例]() (未在提供的信息中发现)