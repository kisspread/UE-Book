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
| 创建时间 | 2024-06-19 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/StructUtils) | |

## 总体用途

`StructUtils` 插件提供实验性的结构体工具，核心是 `FInstancedStruct` 类型。它允许在运行时动态创建、修改和序列化任意结构体的实例，而不需要编译时固定类型绑定。该功能在以下场景非常有用：

- 游戏玩法数据架构需要灵活的结构体容器（例如 `FGameplayTag` 带自定义数据）
- 网络复制多个不同类型的结构体实例（通过 Iris 的 `FInstancedStructNetSerializer`）
- 蓝图或 C++ 中需要形如“任意结构体”的变量类型

该插件最初是 `CoreUObject` 的一部分，后分离为独立插件，目前处于实验阶段，推荐用于原型和评估。

## 模块列表

| 模块 | 一句话总结 | 详细文档 |
|---|---|---|
| `StructUtils` (Runtime) | 提供 `FInstancedStruct`、`FInstancedPropertyBag` 等核心类型及基础操作函数。 | [StructUtils.md](StructUtils.md) |
| `StructUtilsEngine` (Runtime) | 集成引擎功能：序列化、资产注册、Iris 网络序列化支持。 | [StructUtilsEngine.md](StructUtilsEngine.md) |

## 使用场景

- **动态数据容器**：例如制作一个“技能效果”系统，每个效果附带不同结构体参数（伤害、buff 时长、曲线等），可在运行时通过 `FInstancedStruct` 统一存储。
- **网络复制任意结构体**：利用 Iris 提供的 `FInstancedStructNetSerializer` 在 Replicated 数组中复制不同类型结构体（参考 git 提交 `8083cf8c`）。
- **蓝图灵活性**：蓝图节点可以直接操作 `InstancedStruct` 变量，无需为每种结构体创建独立变量。
- **属性包裹器**：使用 `FInstancedPropertyBag` 可以在运行时动态添加/移除属性，适合数据驱动系统。

## 相关链接

- [源码仓库 (5.7)](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/StructUtils)
- [模块文档 - StructUtils](StructUtils.md)
- [模块文档 - StructUtilsEngine](StructUtilsEngine.md)
- [Iris 网络序列化相关提交](https://github.com/EpicGames/UnrealEngine/commit/8083cf8c)