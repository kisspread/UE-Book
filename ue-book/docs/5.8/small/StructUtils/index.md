# Struct Utils

> Experimental Struct Utilities supplying InstancedStruct type

| 属性 | 值 |
|---|---|
| 中文名 | 结构体工具 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `StructUtils` (Runtime), `StructUtilsEngine` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-04-20 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/StructUtils) | |

## 用途

StructUtils 插件主要提供 `FInstancedStruct` 类型，用于在运行时安全地存储和操作任意 USTRUCT 数据。它解决的问题是：在不知道具体结构体类型的情况下，以类型安全的方式处理异构结构体集合。这类似于面向对象中的多态，但作用于值类型（结构体）层面。

**重要提示**：根据 Git 历史，此插件的核心功能（`FInstancedStruct`）已在 UE 5.5 之后的版本中被迁移至 `CoreUObject` 模块。此插件本身已标记为**废弃**，不建议在新项目中直接使用。当前版本主要是为了向后兼容和用于特定的受支持程序（如 LiveLinkHub）。

## 模块列表

| 模块 | 说明 |
|---|---|
| `StructUtils` | 提供 `FInstancedStruct` 核心类型及基础工具函数。 |
| `StructUtilsEngine` | 提供引擎扩展，如资产处理工具和 `UObject` 相关的辅助功能。 |

## 使用场景

- **数据驱动系统**：当需要存储一组类型可能不同的配置数据时（例如游戏中的不同状态效果配置）。
- **资产序列化**：在资产中存储可以是多种不同结构的数据字段。
- **插件间通信**：作为传递复杂、类型不固定数据的容器。

**建议**：对于新项目，应直接使用 `CoreUObject` 模块中的 `FInstancedStruct`。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/StructUtils)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/StructUtils/Tests)