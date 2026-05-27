# Chaos Cloth Editor

> Deprecated plugin, please use the Chaos Cloth plugin instead.

| 属性 | 值 |
|---|---|
| 中文名 | 混沌布料编辑器 (已废弃) |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（旧版布料编辑功能重定向与资产） |
| 模块 | 无（纯内容/重定向插件） |
| 实验性 | 否 |
| 创建时间 | 2019-10-02 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosClothEditor) | |

## 用途

此插件是一个**已废弃的旧版插件**。它的核心作用是作为重定向器（Redirector）和向后兼容的占位符。在旧版本的 Unreal Engine 中，用于布料模拟的编辑器功能位于此插件内。随着 Chaos 物理系统的发展，其布料编辑功能已被整合并优化到新的 `ChaosCloth` 插件中。此插件不再包含实际的功能代码，其存在是为了确保使用旧插件名称的旧项目在升级引擎后不会完全中断，并引导开发者使用正确的、新的插件。

**它存在的问题**：插件本身已停止功能开发和维护。继续使用它会导致依赖过时的 API 和功能缺失。

## 使用场景

**不推荐在任何新项目中使用此插件。**

您可能会遇到此插件的情况：
- 您正在升级一个非常古老的（大约 2019-2020 年左右创建的）使用布料模拟的项目。
- 您参考了过时的教程或示例，其中提到了“ChaosClothEditor”插件。

在这些情况下，正确的操作是：
1.  **禁用** `ChaosClothEditor` 插件。
2.  **启用** `ChaosCloth` 插件。
3.  根据引擎版本和迁移指南，对项目资产和蓝图进行必要的迁移和适配。

## 蓝图用法

此插件已废弃，**没有可用的蓝图节点或资产**。其所有功能均已迁移至 `ChaosCloth` 插件。

## C++ 用法

此插件已废弃，**没有可用的公共头文件或 C++ 接口**。不应在代码中引用此插件的任何模块或头文件。

## Demo 示例

不适用。此插件已废弃，没有可用的示例。请查阅 `ChaosCloth` 插件的文档以获取新的用法示例。

## 模块依赖

此插件本身**没有代码模块**，因此没有直接的 C++ 模块依赖。

它的运行依赖于：
| 模块 | 用途 |
|---|---|
| `ChaosCloth` | 新版布料模拟插件，是此废弃插件的功能替代者。启用此插件时会自动启用 `ChaosCloth`。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-01-13 | `7a30f6e2` | Chaos Cloth - Updated the name of the old redundant Chaos Cloth Editor plugin to make it more obviou | 更新了旧插件名称，使其“废弃”状态更明显 |
| 2024-03-22 | `f55988ce` | Chaos Cloth: | （上下文关联的改动，可能涉及兼容性） |
| 2024-01-29 | `3148c950` | Property Editor: Added ctrl/shift multiplier increments to spin box. Default behavior is: Shift mult | 属性编辑器的通用更新，非此插件特有 |
| 2023-02-21 | `d5a5a356` | Remove unnecessary Public and Private entries for the current module being added to PublicIncludePat | 项目结构清理，移除不必要的包含路径 |
| 2023-01-13 | `3c9aacb1` | [Engine/Plugins] | 引擎插件层面的通用维护 |

### 维护评价

**已废弃 / 停止维护**。

此插件自创建之日起（2019年）就是一个实验性过渡产品。其核心功能早已被 `ChaosCloth` 插件完全取代。从 Git 历史看，近期对它的改动仅限于重命名以强调其废弃状态，以及跟随引擎整体的基础设施维护，没有任何实质性的功能更新或 bug 修复。

**强烈不推荐使用**。任何新开发或维护中的项目都应直接使用 `ChaosCloth` 插件。

## 相关链接

- [源码（已废弃）](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosClothEditor)
- [替代插件：Chaos Cloth](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosCloth)