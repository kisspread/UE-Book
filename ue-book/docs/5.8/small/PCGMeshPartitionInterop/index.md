# Procedural Content Generation Framework (PCG) Mesh Partition Interop

> Interoperability of Mesh Partition with PCG.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | PCG网格分区互操作 |
| 分类 | Mesh Partition |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（资产） |
| 模块 | `PCGMeshPartitionInterop` (Runtime), `PCGMeshPartitionInteropEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-03-05 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PCGMeshPartitionInterop) | |

## 用途

该插件在UE5的程序化内容生成框架（PCG）与网格体分区（Mesh Partition）系统之间提供了互操作性。它允许用户在PCG图表中直接使用网格体分区的功能，例如将复杂的静态网格体动态分区以用于优化的渲染、碰撞或LOD管理。插件本身不包含复杂的算法，而是作为连接两个独立系统的桥梁，使开发者能够利用PCG的程序化控制能力来管理网格体分区。

## 使用场景

- 你需要将大型、复杂的静态网格体在运行时动态分割成更小的部分，以便进行GPU剔除、LOD或流式加载优化 → 在PCG图表中使用该插件的节点来触发和管理分区过程。
- 你正在使用PCG生成大型关卡，并希望自动对生成的网格体资产应用分区规则以提升性能 → 通过该插件将分区逻辑集成到PCG工作流中。
- 你需要对程序化生成的网格体集合进行批量分区操作，并希望用PCG的控制流（如循环、条件）来管理 → 利用该插件提供的节点在PCG图表内实现。

## 模块列表

| 模块 | 类型 | 简述 |
|---|---|---|
| `PCGMeshPartitionInterop` | Runtime | 提供PCG与网格体分区互操作的运行时核心逻辑和数据结构。 |
| `PCGMeshPartitionInteropEditor` | Editor | 提供在编辑器中与PCG和网格体分区交互的工具和UI支持。 |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PCGMeshPartitionInterop)
- [PCG框架官方文档](https://docs.unrealengine.com/latest/en-US/procedural-content-generation--framework-in-unreal-engine/)