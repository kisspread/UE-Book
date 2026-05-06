# Geometry Collection

> Adds Geometry Collection Container.

| 属性 | 值 |
|---|---|
| 中文名 | 几何集合容器 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（几何集合资产、数据流图、编辑器工具） |
| 模块 | `GeometryCollectionDepNodes` (Runtime), `GeometryCollectionEditor` (Runtime), `GeometryCollectionNodes` (Runtime), `GeometryCollectionSequencer` (Runtime), `GeometryCollectionTracks` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-06 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GeometryCollectionPlugin) | |

## 总体用途

Geometry Collection Plugin 为 Unreal Engine 提供了一套完整的 **几何集合（Geometry Collection）** 工作流。几何集合是一种用于高效存储和模拟大量松散碎片（如玻璃破碎、建筑倒塌）的数据结构。该插件通过数据流（Dataflow）图形化节点、编辑器集成和 Sequencer 轨道，允许用户创建、编辑、控制和回放复杂的破坏与碎片模拟，而无需编写 C++ 代码。

## 模块概览

| 模块 | 类型 | 一句话总结 |
|------|------|-----------|
| `GeometryCollectionDepNodes` | Runtime | 提供几何集合处理中依赖关系的专用数据流节点。 |
| `GeometryCollectionEditor` | Runtime | 编辑器集成，包括自定义资产编辑器、属性面板和可视化工具。 |
| `GeometryCollectionNodes` | Runtime | 通用的几何集合数据流节点库，用于构造和修改集合数据。 |
| `GeometryCollectionSequencer` | Runtime | 将几何集合与过场动画（Sequencer）对接，支持关键帧动画和触发。 |
| `GeometryCollectionTracks` | Runtime | 定义几何集合属性（如材质覆盖、可见性）的动画轨道类型。 |

每个模块的详细 API 及蓝图/C++ 用法请参考对应文档：
- [GeometryCollectionDepNodes 模块文档](GeometryCollectionDepNodes.md)
- [GeometryCollectionEditor 模块文档](GeometryCollectionEditor.md)
- [GeometryCollectionNodes 模块文档](GeometryCollectionNodes.md)
- [GeometryCollectionSequencer 模块文档](GeometryCollectionSequencer.md)
- [GeometryCollectionTracks 模块文档](GeometryCollectionTracks.md)

## 使用场景

- **电影级破坏序列**：利用 Sequencer 轨道精确控制建筑物倒塌或物体碎裂的时机与效果。
- **游戏中的动态破坏**：使用数据流节点在运行时生成或修改几何集合，实现可交互的碎片物理。
- **大规模碎片管理**：通过几何集合容器优化上千块碎片的渲染和模拟性能。
- **视觉特效预演**：直接在编辑器中预览和调整破坏效果，减少反复测试迭代。

## 维护状态

| 维度 | 评价 |
|------|------|
| 近期更新频率 | 活跃（近 3 周内 5 次 commits） |
| 最近更新内容 | 功能增强如材质覆盖支持、CVar 控制对话框、数据流编辑器设置、属性暴露等 |
| 维护评价 | 该插件为实验性项目，正处于积极开发中。功能持续丰富，但可能存在 API 不稳定或缺少正式文档的风险。推荐用于原型验证和特定项目，生产环境需谨慎评估。 |

### 近期更新（来自 git log）

- `745ebb56` (2025-09-25) — Add support for override materials for geometry collection root proxies
- `787ab8b2` (2025-09-24) — Geometry collection : add cvar to disable the dialog that ask to create a Dataflow graph when opening
- `29aa54b8` (2025-09-23) — Dataflow : add settings for Dataflow editor
- `9a2a2477` (2025-09-16) — Dataflow : fix Tetrahedron rendering crashing when the source collection was split in multiple geometries
- `38d85df2` (2025-09-06) — dataflow : expose all properties of TransformCollection node as inputs

## 相关链接

- [源码（插件根目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GeometryCollectionPlugin)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GeometryCollectionPlugin/Tests)
- 官方文档：暂无（实验性插件）