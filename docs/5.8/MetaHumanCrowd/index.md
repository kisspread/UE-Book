# MetaHuman Crowd

> Support for crowds of MetaHumans

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、预设等） |
| 模块 | `MetaHumanCrowd` (Runtime), `MetaHumanCrowdEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-21 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanCrowd) | |

## 用途

MetaHuman Crowd 插件旨在解决在 Unreal Engine 场景中高效生成和管理大规模 MetaHuman 角色群体的问题。它超越了简单的角色复制，提供了一套工具来创建具有多样化外观、行为和动画的密集人群，适用于需要大量高保真数字人类的场景，如开放世界游戏、影视预览或建筑可视化。

## 使用场景

- **开放世界游戏**：你需要在城市街道、广场或体育场等场景中填充大量背景 NPC，以营造生动的世界氛围。
- **影视预览与虚拟制片**：你需要快速生成大量具有电影级质量的数字人类作为背景演员或群众。
- **建筑与城市可视化**：你需要在建筑漫游或城市规划演示中模拟真实的人流和人群密度。
- **任何需要“人群感”的场景**：当场景需要从几十到成百上千个外观各异、行为自然的 MetaHuman 角色时，此插件是理想选择。

## 模块列表

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| `MetaHumanCrowd` | Runtime | 提供核心的群体生成、管理、LOD 和动画逻辑。 |
| `MetaHumanCrowdEditor` | Runtime | 提供编辑器内的工具、资产和 UI，用于在编辑器中设计和预览人群。 |

### 近期更新

- 2026-04-24 `56296dcc` MetaHuman Crowd 管线现已主要基于网格描述进行处理，并从中构建骨骼网格体。
- 2026-04-24 `8d3ed3d0` [MHCrowd] 添加了缺失的插件依赖项。
- 2026-04-24 `16907471` [MHCrowd] 为 MetaHuman 人群添加了实验性的 UAF 支持示例。
- 2026-04-23 `a0e976cb` [MHCrowd] 修复了动画合并问题。
- 2026-04-21 `227124bc` [MHCrowd] 将 MetaHuman Mass 类添加到 MHCrowd 插件中。

### 维护评价

该插件在四天内有五次提交，维护频率很高，处于**活跃开发**阶段。提交内容涵盖了核心功能优化、依赖修复、实验性功能引入及问题修复，表明团队正在快速迭代并扩展其功能。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanCrowd)