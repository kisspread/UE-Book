# Chaos Cloth Editor

> Deprecated plugin, please use the Chaos Cloth plugin instead.

| 属性 | 值 |
|---|---|
| 中文名 | 旧版布料编辑器 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（无模块） |
| 模块 | 无（纯内容插件） |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-10-02 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosClothEditor) | |

## 用途

这是一个**已废弃**的插件。其核心用途是为早期基于 Chaos 物理系统构建的布料模拟功能提供一个独立的编辑器扩展入口。在当前的 Unreal Engine 版本中，其所有功能已被整合并由 `ChaosCloth` 插件取代。它的存在主要是为了**保持向后兼容性**，以便旧项目在升级引擎版本时不会因插件引用丢失而立即报错，但新项目不应再使用此插件。

## 使用场景

-   你正在维护一个**非常旧的、基于旧版 Chaos 布料插件**的项目，升级引擎时仍需要该旧版插件作为依赖过渡。
-   **对于所有新项目或新功能开发，应直接使用 `ChaosCloth` 插件**，而不是本插件。

## 蓝图用法

无专有蓝图节点。所有布料相关的蓝图功能请在 `ChaosCloth` 插件中查找。

## C++ 用法

无专有 C++ 类。所有布料模拟的 C++ API 请在 `ChaosCloth` 模块中查找。

## Demo 示例

不适用。此插件已废弃，不包含任何需要演示的代码。

## 模块依赖

此插件本身无模块，但通过 `.uplugin` 文件依赖于以下插件：

| 插件 | 用途 |
|---|---|
| `ChaosCloth` | 新的、功能完整的布料模拟与编辑插件，是本插件的替代品。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-01-13 | `7a30f6e2` | Chaos Cloth - Updated the name of the old redundant Chaos Cloth Editor plugin to make it more obviou | 重命名并明确标记此插件为“旧版”和“冗余”，以强调其废弃状态。 |
| 2024-03-22 | `f55988ce` | Chaos Cloth: | 对布料相关插件/系统的维护性更新。 |
| 2024-01-29 | `3148c950` | Property Editor: Added ctrl/shift multiplier increments to spin box. Default behavior is: Shift mult | 属性编辑器通用改进，非本插件专属功能。 |
| 2023-02-21 | `d5a5a356` | Remove unnecessary Public and Private entries for the current module being added to PublicIncludePat | 工程配置清理，移除冗余的 include 路径设置。 |

### 维护评价

**⚠️ 严重警告：此插件已明确标记为废弃。**

-   **状态**: 已废弃。插件的 `.uplugin` 描述和 `FriendlyName` 中均已明确注明 “Deprecated”。
-   **最后活动**: 最近一次实质性（非全局维护性）更新是在 2026 年初，仅仅是重命名以强调其废弃状态，而非功能开发。
-   **结论**: **强烈不推荐**在新项目中使用。此插件仅作为旧项目升级的兼容性桥梁存在。所有布料相关的开发工作都应直接使用 `ChaosCloth` 插件。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosClothEditor)
-   [官方文档](（无）)
-   [测试用例]（无）