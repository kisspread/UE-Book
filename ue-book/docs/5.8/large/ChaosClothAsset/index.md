# Chaos Cloth Asset

> Pattern based cloth asset using the Chaos Cloth simulation.

| 属性 | 值 |
|---|---|
| 中文名 | Chaos 布料资产 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（布料资产、数据流节点） |
| 模块 | `ChaosClothAsset` (Runtime), `ChaosClothAssetEngine` (Runtime), `ChaosClothAssetTools` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-03-22 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAsset) | |

## 用途

Chaos Cloth Asset 是基于**版片（Pattern）**的布料资产系统，使用 Chaos 物理引擎驱动布料模拟。与传统基于网格体顶点的布料不同，该插件引入了服装设计领域常见的版片工作流——通过定义二维版片形状、缝合关系和物理属性来创建布料，再由 Chaos Cloth 求解器进行实时物理模拟。

该插件从 Experimental 文件夹迁出并标记为 Beta，与 ChaosCloth、GeometryCache、Dataflow 三个插件协同工作，提供了从资产创建、数据流节点编辑到运行时模拟的完整布料管线。适用于角色服装、旗帜、布幔等需要真实物理模拟的场景。

## 使用场景

- 你在制作角色服装系统，需要基于版片定义布料形状和缝合关系
- 你需要通过 Dataflow 节点图来可视化编辑布料资产的构建流程
- 你希望使用 Chaos Cloth 求解器获得高质量的实时布料物理模拟
- 你需要将布料模拟结果缓存为 GeometryCache 用于回放或烘焙

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| [`ChaosClothAsset`](ChaosClothAsset.md) | Runtime | 布料资产核心数据结构：版片、缝合、导入导出等基础类型定义 |
| [`ChaosClothAssetEngine`](ChaosClothAssetEngine.md) | Runtime | 布料资产引擎层：资产类型、组件、LOD、渲染器集成及运行时模拟逻辑 |
| [`ChaosClothAssetTools`](ChaosClothAssetTools.md) | Editor | 编辑器工具：资产编辑器、自定义资产操作、Dataflow 节点等编辑器功能 |

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ChaosCloth` | Chaos 布料物理求解器，提供底层模拟能力 |
| `GeometryCache` | 几何缓存系统，用于布料模拟结果的存储与回放 |
| `Dataflow` | 数据流节点图框架，用于可视化布料资产构建管线 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `89e20f15` | [ChaosClothAsset] Preserve the Cloth Component bSimulateInEditor and Asset properties across Blueprint | 修复蓝图继承中布料组件模拟属性丢失的问题 |
| 2026-05-26 | `8953a713` | [Cloth] Move parallel cloth simulation wait from EOF to TG_LastDemotable | 优化并行布料模拟同步时机，避免阻塞渲染末尾 |
| 2026-05-25 | `1db5232a` | [ChaosCloth] Implement RefreshBoneMapping for ClothAssetSKMClothingAsset | 实现骨骼网格体布料资产的骨骼映射刷新功能 |
| 2026-05-22 | `e98c5896` | [Chaos Cloth Asset] Refresh the editor-only Asset alias after a duplicate or paste of an actor | 修复复制粘贴 Actor 后布料资产别名未刷新的问题 |
| 2026-05-20 | `b9a938ae` | Cleanup Chaos Cloth Asset converter | 清理布料资产转换器代码 |

### 维护评价

该插件处于**活跃维护**状态。自 2024 年 3 月从 Experimental 迁出以来，持续有功能性更新和 Bug 修复。最近一周内有多次提交，涵盖性能优化、功能完善和代码清理。作为 Chaos 物理布料系统的资产层，是 Epic 官方重点推进的布料工作流方向。当前标记为 Beta，API 可能仍有变动，建议关注后续版本升级带来的兼容性变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAsset)
- [ChaosCloth 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosCloth)
- [Dataflow 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Dataflow)