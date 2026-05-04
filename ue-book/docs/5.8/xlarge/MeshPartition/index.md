# Mesh Partition

> Large-scale mesh authoring system through spatial partitioning, non-destructive modifier editing, and platform-adaptive runtime representations.

| 属性 | 值 |
|---|---|
| 分类 | Mesh Partition |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MeshPartition` (Runtime), `MeshPartitionCompute` (Runtime), `MeshPartitionEditor` (Runtime), `MeshPartitionEditorUI` (Runtime), `MeshPartitionModelingToolset` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-23 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MeshPartition) | |

## 用途

Mesh Partition 是一个用于处理超大规模网格（如开放世界地形、巨型建筑或程序化生成环境）的编辑与运行时系统。它通过将大型网格在空间上划分为多个独立的“分区”来解决传统网格编辑器在处理海量几何体时面临的性能瓶颈和工作流限制。该系统的核心优势在于其非破坏性编辑流程（通过修改器栈实现）以及能够根据目标平台（如主机、PC、移动端）生成优化的运行时表示，从而在编辑灵活性和运行时性能之间取得平衡。

## 使用场景

- **开放世界地形编辑**：你需要编辑一个覆盖数百平方公里的地形网格，传统编辑器会卡顿或崩溃。使用 Mesh Partition 可以将地形划分为区块，仅加载和编辑视野内的部分。
- **程序化生成大型环境**：你正在使用程序化方法生成一个巨大的城市或洞穴系统。Mesh Partition 可以帮助你管理生成的海量网格数据，并在运行时高效地流式加载。
- **非破坏性迭代**：你希望对一个复杂模型（如一座城堡）进行多次修改（如添加窗户、改变材质区域），但又不想破坏原始几何体。修改器栈允许你随时调整或禁用任何修改步骤。
- **多平台适配**：你的项目需要同时在高性能主机和移动设备上运行。Mesh Partition 可以为不同平台生成细节层次（LOD）和分区策略不同的网格表示。

## 模块列表

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| `MeshPartition` | Runtime | 核心运行时库，定义分区网格的数据结构、空间划分逻辑和运行时管理。 |
| `MeshPartitionCompute` | Runtime | 计算模块，负责网格分区的生成、修改器应用等计算密集型任务。 |
| `MeshPartitionEditor` | Runtime | 编辑器核心逻辑，提供分区网格的编辑工具、资产管理和编辑器集成。 |
| `MeshPartitionEditorUI` | Runtime | 编辑器用户界面，包含用于操作分区网格和修改器的 Slate/UMG 控件。 |
| `MeshPartitionModelingToolset` | Runtime | 建模工具集，提供基于分区网格的特定建模操作（如雕刻、绘制）。 |

### 近期更新

- 2026-04-24 `44085aba` Mesh Partition: avoid passing hard-coded SM6 argument to GenerateMips. Fixes a crash on projects wit
- 2026-04-24 `473e05b1` Mesh Terrain sculpt layer tools:
- 2026-04-24 `bb6e1b38` Guard against empty UV-Layers and unset element triangles
- 2026-04-23 `2a27739c` Add a path where the for-all-modifiers iteration allows null modifiers to be silently skipped, to av
- 2026-04-23 `dbed6742` Fix broken handling of UV seams at mesh skirt vertices -- take care to copy the UVs from the vertice

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MeshPartition)
- [官方文档](https://dev.epicgames.com/community/learning/knowledge-base/nK7J/unreal-engine-introduction-to-mesh-terrain)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MeshPartition/Tests)