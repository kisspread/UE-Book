# Data Registry

> Adds Data Registry system that can be used as a generic interface for acquiring structure data from multiple sources at runtime

| 属性 | 值 |
|---|---|
| 中文名 | 数据注册表 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DataRegistry` (Runtime), `DataRegistryEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-01-08 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/DataRegistry) | |

## 用途

DataRegistry 是一个运行时数据管理系统，旨在为游戏提供一个统一、通用的数据获取接口。它解决的核心问题是将分散在不同数据源（如 DataTable、CSV、其他资产）中的结构化数据进行抽象和管理，允许游戏逻辑以标准化的方式查找、缓存和访问这些数据，而无需关心数据的具体来源或存储格式。这使得数据管理和游戏逻辑解耦，便于实现数据热更新、动态数据源切换以及集中化的数据访问监控。

## 使用场景

- 你正在开发一个拥有大量复杂配置数据（如物品、技能、角色属性）的 RPG 或策略游戏。
- 你需要将一部分数据（如平衡性参数）从代码或硬编码的资产中分离出来，以便策划人员可以独立修改并实现运行时热更新。
- 你希望在游戏逻辑中使用统一的、类型安全的接口来获取不同类型的数据，避免直接依赖特定的数据资产类型。
- 你需要为游戏数据访问层添加额外的逻辑，例如自动缓存、异步加载或基于条件的数据覆盖。

## 模块概览

| 模块 | 说明 |
|---|---|
| **DataRegistry** | 核心运行时模块，提供 `UDataRegistry`、`FDataRegistryCache` 等核心类，负责数据注册表的创建、管理、查找、缓存和资产解析。 |
| **DataRegistryEditor** | 编辑器专用模块，提供数据注册表资产的自定义编辑器界面、类型管理和相关的编辑器工具，仅在未烹饪（编辑器开发）阶段加载。 |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/DataRegistry)
- 官方文档：无
- 测试用例：未提供