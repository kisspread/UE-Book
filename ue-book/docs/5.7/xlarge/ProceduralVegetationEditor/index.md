# Procedural Vegetation Editor

> Node Graph based Editor that allows users to create Nanite Foliage ready vegetation directly in the engine. Users can load Procedural Vegetation Presets that contain prebuilt data for a species, and customize/create variations using the node graph.

| 属性 | 值 |
|---|---|
| 中文名 | 程序化植被编辑器 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（运行时模块 + 编辑器模块） |
| 模块 | `ProceduralVegetation` (Runtime), `ProceduralVegetationEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-12-18 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ProceduralVegetationEditor) | |

## 总体用途

Procedural Vegetation Editor 是一个基于节点图的编辑器工具，允许用户直接在引擎内部创建、编辑和定制程序化植被资源。它支持加载预设的植被种类数据，并通过图形化节点网络自定义生成规则、形状、材质等，最终输出可直接用于场景的 Nanite 植被实例。该插件旨在简化传统外部 DCC 工具的工作流，将植被的创作与资产生成完全集成到 Unreal Engine 编辑器中。

## 模块列表

| 模块 | 类型 | 一句话总结 | 详细文档 |
|---|---|---|---|
| ProceduralVegetation | Runtime | 提供程序化植被的核心数据模型、运行时生成逻辑及预设管理。 | [ProceduralVegetation.md](./ProceduralVegetation.md) |
| ProceduralVegetationEditor | Runtime | 提供基于节点图的编辑器界面、节点类型、交互操作与资产创建流程。 | [ProceduralVegetationEditor.md](./ProceduralVegetationEditor.md) |

> **注意**：虽然`ProceduralVegetationEditor`的类型标记为 Runtime，但它实际包含编辑器功能，需在编辑器模式下使用。

## 使用场景

- **开放世界植被生成**：快速创建大范围的树木、灌木、草地等植被，并利用节点图控制分布密度、高度变化、颜色偏移等。
- **植被变体创作**：基于一种植物预设，通过节点图调整枝干、叶片、花朵等部分的结构和外观，生成多种变体。
- **Nanite 优化准备**：直接生成支持 Nanite 的高密度植被，无需额外手动优化流程。
- **实验性原型开发**：在游戏早期阶段快速迭代植被外观，无需依赖外部 3D 软件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ProceduralVegetationEditor)
- [ProceduralVegetation 模块文档](./ProceduralVegetation.md)
- [ProceduralVegetationEditor 模块文档](./ProceduralVegetationEditor.md)