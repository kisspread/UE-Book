# Chaos Cloth Asset

> Pattern based cloth asset using the Chaos Cloth simulation.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 混沌布料资产 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（资产类型、数据流节点） |
| 模块 | `ChaosClothAsset` (Runtime), `ChaosClothAssetEngine` (Runtime), `ChaosClothAssetTools` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-03-22 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAsset) | |

## 用途

该插件提供了一套完整的工作流，用于创建和编辑基于样片（Pattern）的布料资产，并利用 Chaos 物理引擎进行逼真的布料模拟。它旨在解决传统布料资产制作流程复杂、与物理模拟脱节的问题，通过数据流（Dataflow）节点系统将资产创建与物理模拟参数紧密集成，让美术师和开发者能够更直观、高效地制作和控制布料动画效果。

## 模块列表

- **`ChaosClothAsset` (Runtime)**: 核心运行时模块，管理布料资产的数据结构、资产类型和序列化。
- **`ChaosClothAssetEngine` (Runtime)**: 负责与 Chaos 布料物理引擎的集成，处理模拟逻辑的执行。
- **`ChaosClothAssetTools` (Editor)**: 提供编辑器工具和数据流节点，用于创建、编辑和预览布料资产。

## 使用场景

- 你需要为游戏角色创建逼真飘动的服装、披风或旗帜。
- 项目中有交互式的布料元素，如窗帘、桌布，需要实时物理模拟。
- 希望利用数据流（Dataflow）系统进行程序化或参数化的布料资产创建与调整。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAsset)
- [官方文档]() （暂无）
- [测试用例]() （暂无）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `89e20f15` | [ChaosClothAsset] Preserve the Cloth Component bSimulateInEditor and Asset properties across Blueprints | 修复布料组件在蓝图间复制时属性丢失的问题 |
| 2026-05-26 | `8953a713` | [Cloth] Move parallel cloth simulation wait from EOF to TG_LastDemotable. | 优化并行布料模拟的同步时机，提升性能 |
| 2026-05-25 | `1db5232a` | [ChaosCloth] Implement RefershBoneMapping for ClothAssetSKMClothingAsset. | 实现骨骼服装资产的骨骼映射刷新功能 |
| 2026-05-22 | `e98c5896` | [Chaos Cloth Asset] Refresh the editor-only Asset alias after a duplicate or paste of an actor. | 修复复制或粘贴Actor后，编辑器中资产别名不更新的问题 |
| 2026-05-20 | `b9a938ae` | Cleanup Chaos Cloth Asset converter | 清理布料资产转换器的代码 |

### 维护评价

该插件创建于2024年3月，历史不长，目前处于“Beta”测试阶段。从近期（2026年5月）的更新记录来看，开发团队正在**非常活跃**地进行功能完善、性能优化和问题修复，维护状态积极。主要集中在编辑器工具改进、物理模拟优化和资产数据处理的健壮性上。

**推荐使用**：对于需要高级布料模拟的项目，这是一个强大且正在快速发展的官方解决方案。但需注意其“Beta”状态，部分API或功能可能在未来版本中发生变化。