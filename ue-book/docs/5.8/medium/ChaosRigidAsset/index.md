# Chaos Rigid Asset

> Rigid Asset plugin for creating and utilising collections of rigid bodies

| 属性 | 值 |
|---|---|
| 中文名 | 混沌刚体资产 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、数据流图资产） |
| 模块 | `ChaosRigidAssetEditor` (Editor), `ChaosRigidAssetNodes` (Runtime), `ChaosRigidAssetEngine` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-15 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosRigidAsset) | |

## 用途

该插件提供了一套基于 **Dataflow（数据流图）** 的工作流，用于**程序化创建和编辑物理资产（Physics Asset）**。传统方式下，创建物理资产需要手动在 Physics Asset Editor 中逐个添加骨骼体和约束，而该插件允许用户通过数据流图节点来：

- 程序化生成 `UPhysicsAsset`
- 选择和操控骨骼、约束、刚体（body）的选择集
- 使用生成器为骨骼创建碰撞几何体（如球体生成器，更多生成器后续支持）
- 使用生成器为骨骼创建关节（如摆动/扭转生成器）
- 当数据流附件存在时，自动跳过传统物理资产编辑器，优先使用数据流编辑器

本质上，它将物理资产的创建流程从手动操作转变为可编程、可复用的数据流图工作流。

## 模块说明

| 模块 | 类型 | 说明 |
|---|---|---|
| `ChaosRigidAssetEngine` | Runtime | 核心运行时逻辑，定义刚体资产的数据结构和引擎集成 |
| `ChaosRigidAssetNodes` | Runtime | 数据流节点定义，包含各种程序化生成刚体几何体和关节的节点 |
| `ChaosRigidAssetEditor` | Runtime | 编辑器集成，提供数据流编辑器与物理资产编辑器之间的桥接 |

## 使用场景

- 你需要**批量、程序化地创建物理资产** → 用数据流图定义生成规则，自动创建骨骼体和约束
- 你想通过**数据流可视化节点图**来设计角色的物理碰撞体，而非手动逐个配置
- 你需要为不同体型的角色**参数化生成物理资产**，只需调整输入参数即可适配新骨骼
- 你想利用 Dataflow 编辑器的实时预览能力来**迭代调整物理资产配置**

## 相关插件依赖

该插件依赖以下其他插件：

| 插件 | 用途 |
|---|---|
| `Dataflow` | 提供数据流图编辑器和节点执行框架，是本插件的核心基础设施 |
| `GeometryProcessing` | 提供几何处理工具，用于生成和操作碰撞几何体 |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosRigidAsset)
- [子模块文档 - Engine](ChaosRigidAssetEngine.md)
- [子模块文档 - Nodes](ChaosRigidAssetNodes.md)
- [子模块文档 - Editor](ChaosRigidAssetEditor.md)

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-28 | `1a41cebd` | Dataflow : fix Dataflow nodes not properly referencing the node when outputing error messages causin | 修复数据流节点错误消息未正确引用节点的 bug |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移至新格式 UE_LOGF |
| 2026-04-10 | `36646cb9` | Rigid asset - Update rigid asset asset to use the unified dataflow menu command so that the user exp | 统一数据流菜单命令，改善用户体验 |
| 2026-04-10 | `5c4d7272` | Dataflow : added an API to dataflow attachment to get the preview actor path for the Dataflow Editor | 新增 API 用于获取数据流编辑器预览 Actor 路径 |
| 2026-04-07 | `b7596b26` | Fixup docs on rigid caching node | 修复刚体缓存节点的文档 |

### 维护评价

- **状态**: 🟢 活跃维护中
- **创建时间**: 2025-08-15，至今约 9 个月
- **更新频率**: 非常活跃，最近 1 个月内有多次功能性更新
- **注意**: 该插件标记为 `Experimental`（`IsExperimentalVersion=true`），且默认未启用（`EnabledByDefault=false`）。API 可能在未来版本中发生较大变动
- **推荐**: 适合早期探索和原型开发，暂不建议用于生产环境