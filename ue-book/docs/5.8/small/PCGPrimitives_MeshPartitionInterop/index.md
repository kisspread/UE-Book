# PCG Primitives Mesh Partition Interop

> Extra PCG Primitives and Examples Library for Mesh Partition interop（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | PCG网格分区互操作 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | 无（纯内容插件） |
| 实验性 | ⚦ 是 |
| 创建时间 | 2026-04-27 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PCGPrimitives_MeshPartitionInterop) | |

## 用途

这是一个纯内容（资产）插件，**不包含**任何 C++ 源码模块。其核心功能是为 `PCG` 框架与 `Mesh Partition`（网格分区）系统提供互操作的蓝图资产和示例。它主要解决在 PCG（程序化内容生成）工作流中，如何利用 `Mesh Partition` 插件对生成的场景几何体（如地形、大型网格体）进行高效分区管理的演示和原型构建问题。

## 使用场景

- 当你使用 `PCG` 框架生成了包含大量网格体（如地形、建筑群、植被散布体）的开放世界场景，并希望利用 `Mesh Partition` 插件对这些网格体进行空间划分和优化时，可以使用此插件提供的示例和预制蓝图资产进行学习和快速原型设计。

## 蓝图用法

由于这是一个纯内容插件，其核心价值在于提供的**预制蓝图资产和PCG图表**，而非可调用的函数节点。用户应直接在内容浏览器中查找并打开由该插件提供的 `.uasset` 文件，学习其内部蓝图节点连接方式和PCG图表示例，以了解 `PCG` 与 `Mesh Partition` 互操作的具体实现模式。

### 使用示例（蓝图描述）

1.  在内容浏览器中，导航至此插件的 `Content` 目录。
2.  查找示例关卡地图或蓝图资产。
3.  打开它们，查看其构成，重点关注：
    *   PCG 图表（PCG Graph）如何设置数据输入。
    *   蓝图中如何使用与 `Mesh Partition` 相关的节点或逻辑。
    *   了解示例是如何将PCG生成的数据（点、网格体）传递给分区系统进行处理。

## C++ 用法

不适用。此插件不包含任何 C++ 模块，无法通过 C++ 直接调用。其所有功能均通过蓝图资产实现，依赖其他插件（如 `PCG`, `MeshPartition`）提供的底层 API。

## Demo 示例

这是一个**内容资产集合**，其本身就是演示。最直接的示例用法是：

1.  启用此插件。
2.  启用其依赖的所有插件（`PCG`, `PCGPrimitives`, `MeshPartition`, `MeshTerrainMode`, `PCGMeshPartitionInterop`, `PCGBiomeSample`）。
3.  在内容浏览器中浏览 `PCGPrimitives_MeshPartitionInterop` 文件夹下的资产，逐个打开蓝图和PCG图表进行学习。

## 模块依赖

该插件本身无模块，但作为“胶水”插件，它声明了对多个其他插件的运行时依赖。要使用此插件，你的项目必须启用以下插件：

| 插件 | 用途 |
|---|---|
| `PCG` | 核心程序化内容生成框架 |
| `PCGPrimitives` | 提供PCG使用的几何体图元 |
| `MeshPartition` | 网格体分区系统核心插件 |
| `MeshTerrainMode` | 与网格化地形相关的模式 |
| `PCGMeshPartitionInterop` | PCG与网格分区互操作的核心逻辑插件 |
| `PCGBiomeSample` | PCG生物群落示例插件 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `d2353f53` | PCG Primitives plugins: small friendly name tweak to match other PCG data plugins. | 对插件友好名称进行了微调，以与其他PCG数据插件保持一致。 |
| 2026-04-27 | `b1bc0d70` | PCG Primitives: moved the PCGPrimitives_MeshPartitionInterop plugin into public facing plugins/experimental folder. | 将该插件移至公开的 `Experimental` 文件夹，是插件的首次公开创建。 |

### 维护评价

此插件创建于近期（2026年4月），是 `Experimental` 状态下的**纯内容资产**。它最近一次更新是友好的名称调整，表明其资产结构已相对稳定，处于维护状态。

**建议**：作为实验性插件，推荐用于学习、评估 `PCG` 与 `Mesh Partition` 的互操作方案，或用于项目原型开发。在生产环境中使用前，应仔细评估其依赖插件（特别是 `MeshPartition`）的成熟度和稳定性。由于没有C++代码，其“维护”主要体现在资产内容的更新上。

## 相关链接

- [源码（资产目录）](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PCGPrimitives_MeshPartitionInterop)
- [官方文档] 无