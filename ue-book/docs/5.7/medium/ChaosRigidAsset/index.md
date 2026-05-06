# Chaos Rigid Asset

> Rigid Asset plugin for creating and utilising collections of rigid bodies

| 属性 | 值 |
|---|---|
| 中文名 | 刚体资产 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（物理资产、蓝图） |
| 模块 | `ChaosRigidAssetEditor` (Editor), `ChaosRigidAssetEngine` (Runtime), `ChaosRigidAssetNodes` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-15 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosRigidAsset) | |

## 总体用途

Chaos Rigid Asset 是实验性插件，用于创建和管理**刚体集合**（一组碰撞体）。它深度集成 Dataflow 系统，允许通过可视化节点（Box、Capsule、Convex 等简单几何构建器）程序化地生成物理碰撞体，并将其导出为物理资产（Physics Asset）。插件主要解决以下问题：

- 在 Dataflow 工作流中直接生成和组合简单刚体（替代手动在物理资产编辑器中逐个添加）。
- 将刚体集合作为独立资产存储、复用和传递。
- 为需要大量简化碰撞体的程序化场景（如破碎、物理模拟）提供高效的生成路径。

## 使用场景

- **程序化物理资产生成**：使用 Dataflow 节点生成盒子、胶囊、凸体等碰撞体，自动构建 Physics Asset，适合批量创建或动态调整碰撞体。
- **物理模拟预处理**：在 Dataflow 中组合多个刚体集合，生成复杂碰撞体布局，应用于破碎、废墟、物理装饰等场景。
- **编辑器扩展**：通过自定义资产类型和编辑器面板，快速创建和管理刚体集合数据。
- **建筑/场景工具**：为大型场景中的静态物体自动生成轻量碰撞体集合。

## 模块列表

| 模块 | 类型 | 一句话说明 |
|---|---|---|
| [ChaosRigidAssetEditor](ChaosRigidAssetEditor.md) | Editor | 提供资产工厂、类型操作、Dataflow 节点设置和编辑器集成。 |
| [ChaosRigidAssetEngine](ChaosRigidAssetEngine.md) | Runtime | 运行时核心，管理刚体集合的数据结构、创建与碰撞体生成逻辑。 |
| [ChaosRigidAssetNodes](ChaosRigidAssetNodes.md) | Runtime | 提供 Dataflow 节点（如 BoxBuilder、CapsuleBuilder、ConvexBuilder），用于在 Dataflow 图中生成物理碰撞体。 |

### 各模块关系

- **ChaosRigidAssetEngine** 定义数据模型和运行时处理；**ChaosRigidAssetNodes** 依赖 Engine 模块实现 Dataflow 节点；**ChaosRigidAssetEditor** 依赖 Engine 和 Nodes 模块提供编辑器支持。

## 依赖关系

- **依赖插件**：`Dataflow`（必需）
- **无其他独特外部依赖**（标准 Core/Engine/Slate 等省略）。

## 维护状态

### 近期更新

- 2025-09-30	5c0a4ef4	[Dataflow] Added Box, Capsule and Convex simple builders as geometry generators for dataflow physics
- 2025-09-29	6813b43d	[Dataflow] Fixed physics asset generation not correctly setting base joint names on constraints lead
- 2025-09-26	3f07f94a	[Dataflow] Added Box, Capsule and Convex simple builders as geometry generators for dataflow physics
- 2025-08-15	4499bef8	Fix warning due to passing derived member to multi-pin constructor. The reference isn't used within

### 维护评价

- **创建时间**：2025-08-15（不足半年）
- **更新频率**：近 2 个月内有功能性更新（新增几何生成器、修复物理资产关节设置）
- **稳定性**：实验性插件（`IsExperimentalVersion=true`），API 可能变化，不建议用于生产项目
- **推荐度**：适合技术预研和原型验证，待插件稳定后可考虑用于正式项目

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosRigidAsset)
- [模块文档](ChaosRigidAssetEditor.md) · [ChaosRigidAssetEngine.md](ChaosRigidAssetEngine.md) · [ChaosRigidAssetNodes.md](ChaosRigidAssetNodes.md)