# Chaos Cloth Editor

> Deprecated plugin, please use the Chaos Cloth plugin instead.

| 属性 | 值 |
|---|---|
| 中文名 | 布料编辑器 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（标记为已废弃） |
| 模块 | 无（纯内容插件） |
| 实验性 | ⚠️ 是（已废弃） |
| 创建时间 | 2019-10-02 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosClothEditor) | |

## 用途

这是一个已被官方废弃的插件。其最初目的是为基于 Chaos 物理引擎的布料模拟提供编辑器工具和相关资产支持。随着 Chaos 物理引擎的整合和优化，其功能已被更成熟、更稳定的 `ChaosCloth` 插件完全取代。目前，此插件的存在主要是为了提供向后兼容性（避免依赖它的旧项目直接报错），并明确地指引开发者迁移至新插件。

## 使用场景

- **遗留项目维护**：你的项目在很早期的 UE4 版本中基于此插件的前代版本开发，现在进行升级维护。
- **参考学习**：研究 Unreal Engine 中 Chaos 布料编辑器工具的早期实现架构和设计思路。
- **不推荐用于任何新项目**。所有新项目应直接使用 `ChaosCloth` 插件来实现布料模拟。

## 蓝图用法

该插件已被标记为废弃，且不包含任何公开的模块或蓝图功能接口。所有布料相关的蓝图节点应通过 `ChaosCloth` 插件获取。

## C++ 用法

该插件已被废弃，且不包含任何公开的 C++ 模块或 API。在新项目中进行 Chaos 布料开发时，请引入 `ChaosCloth` 模块。

### 头文件引入

```cpp
// 不推荐引入此插件。应使用：
#include "ChaosCloth/ChaosClothConfig.h" // 来自 ChaosCloth 插件
```

## Demo 示例

该插件已被废弃，无有效示例。请参考 `ChaosCloth` 插件的文档和示例。

## 模块依赖

此插件本身无任何 C++ 模块。
根据其 `.uplugin` 文件，它依赖 `ChaosCloth` 插件，并以此作为其功能的替代品。

| 模块 | 用途 |
|---|---|
| `ChaosCloth` | 此插件的功能替代品，提供实际的 Chaos 布料模拟功能。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-01-13 | `7a30f6e2` | Chaos Cloth - Updated the name of the old redundant Chaos Cloth Editor plugin to make it more obviou | 将插件名称添加“(Deprecated)”后缀，使其废弃状态更明确。 |
| 2024-03-22 | `f55988ce` | Chaos Cloth: | 可能是 Chaos 布料相关的基础维护或编译修复，无新功能。 |
| 2024-01-29 | `3148c950` | Property Editor: Added ctrl/shift multiplier increments to spin box. Default behavior is: Shift mult | 属性编辑器通用改进，可能间接影响此插件的配置界面。 |
| 2023-02-21 | `d5a5a356` | Remove unnecessary Public and Private entries for the current module being added to PublicIncludePat | 清理项目结构，移除多余的模块包含路径，属于维护性提交。 |
| 2023-01-13 | `3c9aacb1` | [Engine/Plugins] | 仓库插件结构的通用调整或同步。 |

### 维护评价

**维护状态：已废弃 (Deprecated)**

该插件创建于 2019 年，从 `Experimental` 目录下的命名和历史提交可以看出，它是一个早期实验性功能的编辑器部分。随着 `ChaosCloth` 插件在主分支的成熟和稳定，此插件的功能已被完全取代。

- **最后实质性更新**：该插件在很久以前就已停止功能开发。近期（2026年）的提交仅为重命名以更清晰地标识其废弃状态，而非功能更新。
- **活跃度**：仅进行最低限度的维护（如重命名提示、编译兼容性修复），无新功能开发。
- **推荐度**：**强烈不推荐在任何新项目中使用**。对于现有项目，应制定计划迁移至 `ChaosCloth` 插件。继续使用此插件将无法获得新的布料特性、性能优化和 bug 修复。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosClothEditor)
- 官方文档：无
- 测试用例：无