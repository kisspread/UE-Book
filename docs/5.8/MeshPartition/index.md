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
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshPartition) | |

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

- 2026-04-24 `44085aba` 修复了在使用 DefaultGraphicsRHI 的项目中，向 GenerateMips 传递硬编码 SM6 参数导致的崩溃问题。
- 2026-04-24 `473e05b1` 新增网格地形雕刻层工具。
- 2026-04-24 `bb6e1b38` 增加了对空 UV 层和未设置元素三角形的防护。
- 2026-04-23 `2a27739c` 新增一种路径，允许在遍历所有修改器时静默跳过空修改器，以避免在撤销操作时触发 ensure 断言。
- 2026-04-23 `dbed6742` 修复了网格裙边顶点处 UV 接缝处理错误的问题——现在会正确地从实际源顶点复制 UV。

### 维护评价

该插件处于**活跃维护**状态。在短短两天内有5次提交，修复了关键崩溃和功能缺陷，并添加了新工具和防护逻辑，表明开发团队响应迅速且持续改进。提交内容均为实质性的功能增强与问题修复，而非实验性代码，体现了稳定且积极的维护节奏。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshPartition)
- [官方文档](https://dev.epicgames.com/community/learning/knowledge-base/nK7J/unreal-engine-introduction-to-mesh-terrain)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshPartition/Tests)