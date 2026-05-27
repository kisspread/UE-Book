# MetaHumanRuntime

> Deprecated plugin now redirected to MetaHumanSDK

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman运行时（已弃用） |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（重定向） |
| 模块 | 无（纯内容/重定向插件） |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-06-10 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetaHuman/MetaHumanRuntime) | |

## 用途

MetaHumanRuntime 插件最初作为 MetaHuman 角色在 Unreal Engine 中的核心运行时支持组件而创建，主要用于封装和提供 MetaHuman 相关组件（如 MetaHumanComponent）的基础功能。

**当前状态**：该插件已被**弃用**，其功能已完全迁移至新插件 **MetaHumanSDK**（或 MetaHumanSDKRuntime）。它现在仅作为一个“重定向”或“迁移”占位符存在，以确保引用它的旧项目能够平滑过渡，避免立即编译错误。

## 使用场景

-   **旧项目维护**：如果你的项目在 2024 年 8 月之前集成了 MetaHumanRuntime 插件，在升级引擎版本后，此插件会引导你转向使用 MetaHumanSDK。
-   **新项目**：**不推荐使用**。新项目应直接使用功能更完整、仍在维护的 **MetaHumanSDK** 插件。

## 蓝图用法

由于该插件已被弃用且没有实际模块，因此**不提供任何蓝图节点**。
原先属于此插件的 `MetaHumanComponent` 等蓝图节点，现在应从 **MetaHumanSDK** 插件中获取。

### 核心节点

无。

## C++ 用法

由于该插件已被弃用且没有实际模块，因此**不提供任何可用的C++ API**。
原先属于此插件的头文件（如 `MetaHumanComponent.h`）和类，现在应从 **MetaHumanSDK** 插件中引入。

### 头文件引入

无。

## Demo 示例

该插件已弃用，没有独立的演示示例。
如需了解 MetaHuman 在 UE 中的运行时用法，请参考 **MetaHumanSDK** 插件的文档和示例。

## 模块依赖

本插件自身没有代码模块，但依赖以下插件：

| 插件 | 用途 |
|---|---|
| `MetaHumanSDK` | 实际提供所有 MetaHuman 运行时功能的新插件，MetaHumanRuntime 是其重定向。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2024-09-16 | `62f8cc0c` | Unable to load plugin, missing dependency MetaHumanRuntime | 修复无法加载插件的问题，因为缺少依赖 MetaHumanRuntime |
| 2024-08-19 | `79003ad1` | Move MetaHumanRuntime plugin to MetaHumanSDK plugin and rename it to MetaHumanSDKRuntime | **关键变更**：将 MetaHumanRuntime 功能迁移至 MetaHumanSDK 并重命名为 MetaHumanSDKRuntime |
| 2024-08-08 | `ea519b5c` | [MH-12702] Unreal Editor crashes after Playing a Level with an Optimized MetaHuman with MetaHuman Co | 修复编辑器在拥有优化后MetaHuman的关卡中运行后崩溃的问题 |
| 2024-07-31 | `8e8004fd` | MetaHuman component for UE improvements | 对用于UE的MetaHuman组件进行了改进 |
| 2024-07-24 | `bd22b183` | Fixed issue for control rigs not running on body parts | 修复控制绑定（Control Rig）在身体部件上不运行的问题 |

### 维护评价

-   **状态**：**已弃用，功能已迁移**。
-   **分析**：该插件在创建仅两个月后（2024年8月），其核心功能就被迁移至新的 `MetaHumanSDK` 插件。目前它仅作为一个兼容性重定向存在，以避免旧项目立即崩溃。最后一次实质性更新停留在 2024 年 8 月。
-   **建议**：**强烈不推荐在新项目中使用**。所有开发者都应迁移到 **MetaHumanSDK** 插件以获取最新功能和持续维护。

## 相关链接

-   [源码 (已弃用)](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetaHuman/MetaHumanRuntime)
-   **[替代插件：MetaHumanSDK]** (请查找对应的 MetaHumanSDK 插件文档)