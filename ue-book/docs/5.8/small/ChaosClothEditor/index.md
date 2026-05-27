# Chaos Cloth Editor (Deprecated)

> Deprecated plugin, please use the Chaos Cloth plugin instead.

| 属性 | 值 |
|---|---|
| 中文名 | 混沌布料编辑器 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（已废弃插件所需的资产和配置） |
| 模块 | 无（纯内容插件） |
| 实验性 | ⚠️ 是（位于Experimental目录且已废弃） |
| 创建时间 | 2019-10-02 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosClothEditor) | |

## 用途

这是一个**已被官方明确废弃**的插件。它最初是作为 Chaos 布料（Chaos Cloth）物理系统的一个**编辑器扩展插件**而创建的，可能提供了用于调试、编辑或预览布料模拟的专用工具和资产。然而，根据其元数据，该插件的所有功能已被整合到主 `ChaosCloth` 插件中。此插件的存在现在仅是为了保持向后兼容性或历史记录，**强烈不建议**在新项目中使用或依赖它。

## 使用场景

- **历史遗留项目**：你的项目在很久以前（约 2019-2020 年）就基于此插件构建了布料工作流，并且尚未迁移到新的 `ChaosCloth` 插件。
- **插件依赖**：其他某个旧插件或模块仍然依赖于此插件中的特定资产。

**重要提示**：对于任何新的布料模拟需求，请直接使用 `ChaosCloth` 插件。本插件文档仅作历史参考。

## 蓝图用法

由于此插件已废弃且不包含可调用的代码模块，它不提供任何蓝图可调用函数或属性节点。其可能包含的资产（如材质、预设等）也已不建议使用。

## C++ 用法

此插件不包含可编译的 C++ 模块，因此无法在 C++ 代码中直接引用或调用其 API。

## Demo 示例

不提供示例。请参考 `ChaosCloth` 插件的文档。

## 模块依赖

此插件本身不包含任何模块。它依赖于 `ChaosCloth` 插件（如 `.uplugin` 的 `Plugins` 部分所示），但鉴于其废弃状态，这种依赖关系也已过时。

| 模块 | 用途 |
|---|---|
| `ChaosCloth` | 它所依赖的、取代了它功能的活动插件 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-01-13 | `7a30f6e2` | Chaos Cloth - Updated the name of the old redundant Chaos Cloth Editor plugin to make it more obviou | 更新废弃插件名称，使其废弃状态更明显 |
| 2024-03-22 | `f55988ce` | Chaos Cloth: | Chaos Cloth 相关更新，可能包含对废弃插件的引用修改 |
| 2024-01-29 | `3148c950` | Property Editor: Added ctrl/shift multiplier increments to spin box. Default behavior is: Shift mult | 属性编辑器通用更新，非本插件功能改动 |
| 2023-02-21 | `d5a5a356` | Remove unnecessary Public and Private entries for the current module being added to PublicIncludePat | 清理构建配置，非功能性改动 |
| 2023-01-13 | `3c9aacb1` | [Engine/Plugins] | 引擎插件目录的大范围变更 |

### 维护评价

**已废弃，不建议使用。**

该插件创建于 2019 年，是 Chaos 布料系统的早期编辑器组成部分。从 2023 年起，对其目录的修改主要是构建系统清理或引用更新。2026 年的最新更新更是直接将其名称更改为 “(Deprecated)”，并添加了明确的废弃说明。这表明 Epic Games 已彻底将其功能整合至 `ChaosCloth` 插件，并希望开发者停止使用此旧版本。所有布料相关的新功能和修复都会在 `ChaosCloth` 插件中进行。**请将你的项目迁移到 `ChaosCloth` 插件**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosClothEditor)
- [官方文档]() 无
- [替代插件：ChaosCloth]() 请查找 `ChaosCloth` 插件的文档