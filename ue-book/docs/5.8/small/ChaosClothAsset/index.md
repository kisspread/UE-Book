# Chaos Cloth Asset

> Pattern based cloth asset using the Chaos Cloth simulation.

| 属性 | 值 |
|---|---|
| 中文名 | 混沌布料资产 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、数据流节点） |
| 模块 | `ChaosClothAsset` (Runtime), `ChaosClothAssetEngine` (Runtime), `ChaosClothAssetTools` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-03-22 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAsset) | |

## 用途

ChaosClothAsset 是一个实验性的、基于图案（Pattern）的布料模拟系统。它使用 Unreal Engine 的 Chaos 物理引擎作为后端，允许艺术家和开发者在编辑器中设计布料图案（类似服装纸样），并将其转化为可在运行时进行高性能、逼真物理模拟的资产。它旨在提供比传统基于骨骼的布料模拟更精细的控制和更真实的布料行为，用于角色服装、旗帜、窗帘等任何需要复杂布料动画的场合。

## 使用场景

- 你正在开发一个需要高度逼真角色服装（如披风、长裙）的游戏，并希望衣服能随角色动作自然飘动。
- 你需要制作一个可交互的布料物体，如玩家可以拉动的桌布或可被风吹动的旗帜。
- 你希望美术人员能够像设计真实服装一样，通过绘制二维纸样（Pattern）来定义三维布料的模拟形状，以获得更精确的物理行为。

## 模块列表

本插件包含三个核心模块，共同构建了完整的布料资产创建工作流：

| 模块 | 类型 | 说明 |
|---|---|---|
| [`ChaosClothAsset`](./ChaosClothAsset.md) | Runtime | 插件的核心运行时模块，定义布料资产的数据结构和底层模拟接口。 |
| [`ChaosClothAssetEngine`](./ChaosClothAssetEngine.md) | Runtime | 集成引擎功能，负责管理布料资产在游戏运行时的实例化、模拟和渲染。 |
| [`ChaosClothAssetTools`](./ChaosClothAssetTools.md) | Editor | 提供编辑器工具和界面，用于创建、编辑布料图案，配置模拟参数，以及通过数据流节点构建处理流程。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `89e20f15` | [ChaosClothAsset] Preserve the Cloth Component bSimulateInEditor and Asset properties across Bluepri | 修复蓝图复制/粘贴时布料组件属性丢失的问题。 |
| 2026-05-26 | `8953a713` | [Cloth] Move parallel cloth simulation wait from EOF to TG_LastDemotable. | 优化布料并行模拟的等待阶段，可能提升性能。 |
| 2026-05-25 | `1db5232a` | [ChaosCloth] Implement RefershBoneMapping for ClothAssetSKMClothingAsset. | 为使用骨骼网格的布料资产实现了骨骼映射刷新功能。 |
| 2026-05-22 | `e98c5896` | [Chaos Cloth Asset] Refresh the editor-only Asset alias after a duplicate or paste of an actor. | 修复复制粘贴Actor后，编辑器内资产别名未刷新的问题。 |
| 2026-05-20 | `b9a938ae` | Cleanup Chaos Cloth Asset converter | 对布料资产转换器进行代码清理和优化。 |

### 维护评价

**活跃维护**。该插件创建于2024年3月，至今约2年，从近期（2026年5月）的提交记录看，仍在积极进行功能完善、性能优化和问题修复。需要特别注意的是，其 `.uplugin` 标记为 **Beta 版本**，且 `EnabledByDefault` 为 false，表明这是一个尚未完全稳定、需要用户手动启用的实验性功能。对于希望在生产项目中使用布料物理模拟的开发者，这是一个值得关注和尝试的先进解决方案，但需做好应对潜在 API 变更或行为调整的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAsset)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAsset/Tests) (推测路径，实际可能存在)