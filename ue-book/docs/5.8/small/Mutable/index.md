# Mutable

> Mutable adds the tools and runtime to create customizable objects for your games.

| 属性 | 值 |
|---|---|
| 中文名 | 可变对象系统 |
| 分类 | CustomizableObjects |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（可自定义对象系统、运行时、编辑器工具） |
| 模块 | `MutableRuntime` (Runtime), `CustomizableObject` (Runtime), `MutableTools` (Runtime), `MutableValidation` (Runtime), `CustomizableObjectEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-09-05 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable) | |

## 用途

Mutable 是一个用于创建可自定义和可变游戏对象的高级系统。它允许开发者定义复杂的对象变异逻辑，玩家可以在运行时（或由设计师在编辑器中）对这些对象进行修改。例如，你可以创建一个可高度自定义的角色，玩家可以独立调整其服装、发型、纹身、配饰、材质颜色等多个属性，系统会高效地合并这些变异并生成最终的网格体和材质，而无需预先烘焙所有可能的组合。

## 使用场景

- **角色/装备自定义系统**：为 RPG、体育、模拟类游戏创建深度的角色外观定制功能。
- **程序化生成与变异**：根据玩家选择或游戏规则，动态生成具有不同外观和属性的物品或敌人。
- **高效资产管理**：替代传统上需要为每种组合制作独立资产的工作流，通过基础资产 + 变异逻辑的方式，大幅减少美术资源数量和内存占用。
- **编辑器内的快速原型设计**：让策划或美术快速预览和调整对象的多种变体。

## 模块列表

| 模块 | 类型 | 功能概述 |
|---|---|---|
| `MutableRuntime` | Runtime | 核心运行时库，负责在运行时解析和执行变异逻辑，生成最终资源。 |
| `CustomizableObject` | Runtime | 定义可自定义对象资产（`UCustomizableObject`）及其相关实例的核心运行时类。 |
| `MutableTools` | Runtime | 提供用于在编辑器或构建时编译、优化和烘焙可自定义对象资产的工具。 |
| `MutableValidation` | Runtime | 包含用于验证可自定义对象资产和实例有效性的工具。 |
| `CustomizableObjectEditor` | Editor | 为 UE 编辑器提供自定义资产编辑器、节点图、预览窗口等开发工具界面。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `70229bdc` | [Mutable] Fix duplicated Skeletal Mesh geometry if there is multiple SKM with the same name. | 修复同名骨骼网格体导致几何体重复的 Bug。 |
| 2026-05-26 | `2b0ca8bd` | [mutable] Fixed "Clip mesh with UV Mask" op not loading the appropriate mask mip. | 修复了 UV 裁剪操作未加载正确遮罩 Mipmap 的问题。 |
| 2026-05-26 | `06ea27d3` | [Mutable] Fix texture parameters using the wrong method to compute the LODBias. | 修复了纹理参数计算 LOD 偏移值的方法错误。 |
| 2026-05-26 | `e9c39661` | [Mutable] Allow more clothing asset types by using the ClothingAssetBase interface. | 通过使用通用接口，支持更多类型的服装资产。 |
| 2026-05-25 | `c8ce9ff7` | [Mutable] Fix possible data race when comparing PassthroughObjects. | 修复了比较穿透对象时可能发生的潜在数据竞争。 |

### 维护评价

- **活跃维护**：插件处于 **Beta** 状态，自 2024 年 9 月从实验状态迁移而来，至今（2026 年 5 月）仍在频繁更新。
- **更新内容**：近期更新主要集中在修复运行时 Bug、提升稳定性和扩展功能兼容性，表明项目正在积极修复问题并准备正式发布。
- **推荐使用**：作为一个功能强大且相对年轻的系统，Mutable 非常适合需要深度对象自定义的项目。但由于仍处于 Beta 阶段，**建议在项目早期或评估后谨慎引入，并关注其版本更新和潜在的兼容性变化**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable)