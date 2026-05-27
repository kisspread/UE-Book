# Struct Utils

> Experimental Struct Utilities supplying InstancedStruct type（此插件已废弃，功能已合并至 CoreUObject）

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

> ⚠️ **废弃通知**：自 UE 5.5 起，此插件已被标记为废弃，其核心功能已合并至 `CoreUObject` 模块。新项目不应再依赖此插件，直接使用引擎内置的 `FInstancedStruct` 即可。

## 用途

StructUtils 提供了 **`FInstancedStruct`** 类型——一种可以在运行时持有任意 UScriptStruct 实例的容器。它解决了以下核心问题：

- **类型擦除的结构体容器**：无需为每种结构体类型创建单独的 UPROPERTY，一个 `FInstancedStruct` 即可持有任意结构体
- **运行时多态**：类似 UObject 的多态机制，但作用于结构体，避免堆分配开销
- **序列化与网络复制**：通过引擎内置序列化支持，可在蓝图资产和网络传输中安全使用

## 使用场景

- 你需要一个通用的"任意结构体"容器，例如实现灵活的属性系统、数据驱动的游戏逻辑
- 你需要在不创建 UProperty 的情况下存储不同类型结构体的实例
- 你希望在蓝图中传递和操作结构体，但具体类型在设计时未知

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| `StructUtils` | Runtime | 核心类型定义，包含 `FInstancedStruct`、`FConstStructView`、`FStructView` 等基础类型 |
| `StructUtilsEngine` | Runtime | 引擎扩展层，提供与 Gameplay 相关的结构体工具函数 |

详细 API 请参阅各子模块文档。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/StructUtils)
- [StructUtils 模块文档](StructUtils.md)
- [StructUtilsEngine 模块文档](StructUtilsEngine.md)

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2024-08-05 | `5bf7f335` | Iris - Move InstancedStructNetSerializer to IrisCore. | 网络序列化器已迁移至 Iris 核心模块 |
| 2024-08-01 | `0e320e33` | Iris - Crash fix for removing InstancedStruct from a replicated array and adding the same struct typ | 修复复制数组中移除并重新添加同类实例化结构体的崩溃 |
| 2024-06-28 | `8083cf8c` | Iris - Adjust includes due to StructUtils moving. | 适配 StructUtils 合并至 CoreUObject 的头文件路径变更 |
| 2024-06-28 | `3680fd08` | Iris - Initial naive but working version of FInstancedStructNetSerializer to be able to replicate FI | 为 FInstancedStruct 添加初始的网络复制序列化支持 |
| 2024-06-19 | `e6d36d75` | Remove references to deprecated plugin StructUtils (now part of CoreUObject) | 正式废弃此插件，功能已合并至 CoreUObject |

### 维护评价

**🚫 已废弃（Deprecated）**

此插件自 UE 5.5 起已被废弃，其功能已整合至引擎核心的 `CoreUObject` 模块。2024 年的更新均为 Iris 网络系统对 `FInstancedStruct` 的适配工作，而非此插件本身的迭代。

**不推荐在新项目中使用此插件。** 如果你需要 `FInstancedStruct`，直接使用 UE 5.5+ 内置版本即可，无需启用此实验性插件。