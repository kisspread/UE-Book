# Optimus

> Deprecated plugin now redirected to DeformerGraph（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 动画优化器（已废弃） |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `无（纯内容插件）` |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-09-22 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/Optimus) | |

## 用途

`Optimus` 插件本身是一个**已废弃（Deprecated）** 的空壳插件。它存在的唯一目的，是为了**向后兼容**那些在历史版本（尤其是 5.1 版本之前）中使用了 `Optimus` 插件名称的项目或代码引用。启用 `Optimus` 插件，实际上会自动启用其替代者——功能更完善的 `DeformerGraph` 插件。它解决的是旧项目迁移和依赖引用的平滑过渡问题。

## 使用场景

- **项目迁移**：你的项目是从 Unreal Engine 5.1 或更早版本升级上来的，并且原先启用了 `Optimus` 插件。在升级到 5.2+ 版本后，启用此插件可以确保原有的依赖链自动指向新的 `DeformerGraph` 插件，避免直接报错。
- **历史代码引用**：你的 C++ 代码或配置文件中明确引用了 `Optimus` 模块或插件名称。

对于全新的项目或代码，**不建议**再使用 `Optimus` 插件，应直接使用 `DeformerGraph`。

## 蓝图用法

不适用。此插件为纯重定向插件，无自己的蓝图节点或资产。

## C++ 用法

不适用。此插件无自身模块，不提供头文件或 API。

## Demo 示例

不适用。此插件无任何可执行或展示的功能代码。

## 模块依赖

此插件的核心依赖是其重定向的目标插件。

| 模块 | 用途 |
|---|---|
| `DeformerGraph` | 被 Optimus 插件声明为强制启用的依赖，是其功能的实际实现者。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 更新了插件内置链接的协议以使用安全协议。 |
| 2022-09-22 | `c2ba631d` | #jira UE-164818 Optimus: Re-add old Optimus plugin, just as a dependency wrapper for DeformerGraph. | 创建该插件，仅作为 DeformerGraph 的依赖包装器。 |

### 维护评价

- **创建时间**：2022年9月22日，插件年龄约为3年。
- **最近更新**：最后一次功能性（非编译修复）更新停留在其创建之时（2022年9月22日），仅在一个月后进行了一次无关的链接协议更新。此后超过3年没有任何实质性维护。
- **活跃状态**：**可能废弃**。此插件被明确标记为“Deprecated”，且 Epic 官方已提供替代方案 `DeformerGraph`。
- **已知限制**：它没有自身功能，只是一个指向新插件的占位符。
- **推荐使用**：**不推荐**。对于新项目或新功能开发，请直接使用 `DeformerGraph` 插件。仅在你维护一个需要从非常旧的版本（使用 `Optimus`）平滑升级的项目时，才需要考虑保留对它的引用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/Optimus)
- [替代插件 DeformerGraph](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/DeformerGraph)