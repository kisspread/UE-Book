# PCG Primitives Mesh Partition Interop

> Extra PCG Primitives and Examples Library for Mesh Partition interop

| 属性 | 值 |
|---|---|
| 中文名 | PCG网格分区互操作示例库 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（示例资产） |
| 模块 | `无（纯内容插件）` |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2026-04-27 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PCGPrimitives_MeshPartitionInterop) | |

## 用途

该插件并非提供新的运行时功能或编辑器工具，而是一个**示例和资产集合**。它的核心目的是演示如何将 PCG（程序化内容生成）框架与 Mesh Partition（网格分区）系统结合使用。

- **解决什么问题**：帮助开发者理解如何利用 PCG 的强大程序化生成能力，来驱动和配置 Mesh Partition 系统，从而高效地管理大型静态网格体（特别是地形相关网格）的生成和分区。
- **为什么存在**：作为官方提供的示例库，降低了学习 PCG 与 Mesh Partition 互操作的门槛，是 Epic Games 推广和文档化这套工作流的一部分。

## 使用场景

- **你正在开发一个开放世界游戏，需要程序化生成地形并放置大量静态网格物体** → 此插件的示例可以展示如何利用 PCG 根据地形特征（如高度、坡度）智能地将网格体分配到不同的分区，以优化渲染和内存管理。
- **你需要优化一个包含大量静态网格物体的大型场景的性能** → 参考插件中的 Mesh Partition 配置示例，学习如何通过分区策略来实现视距剔除、细节层次（LOD）切换等优化。
- **你想学习如何将 PCG 数据（如点、线、体）用作 Mesh Partition 系统的输入** → 此插件提供了从 PCG 生成数据到驱动网格分区配置的完整蓝图或图表示例。

## 蓝图用法

由于该插件本身没有源码文件（纯内容），其提供的资产本身就是用法示例。

### 核心资产（非节点）

| 资产类型 | 预计内容 | 说明 |
|---|---|---|
| `PCG Graph` | PCG 图表 | 预配置的 PCG 图表，演示如何生成点数据、处理网格体属性，并将其输出给下游的网格分区逻辑。 |
| `Mesh Partition 配置资产` | 数据资产 | 预配置的 Mesh Partition 规则或数据资产，展示了如何根据 PCG 生成的属性（如密度、类型）来划分网格。 |
| `蓝图` | Actor 蓝图 | 包含了将 PCG 图表、网格体组件和分区逻辑整合在一起的 Actor 蓝图。用户可以直接拖入关卡并运行查看效果。 |
| `示例关卡` | 地图文件 | 一个演示关卡，展示了上述所有资产协同工作的最终效果。 |

### 使用示例（资产操作描述）

1.  **启用插件**：在项目设置中启用 `PCGPrimitives_MeshPartitionInterop` 及其依赖的插件（如 `PCG`, `MeshPartition`）。
2.  **查看示例关卡**：打开插件内容目录（`/Game/Plugins/PCGPrimitives_MeshPartitionInterop/`），找到示例关卡（`.umap` 文件）并打开。这是最直接的学习方式。
3.  **研究 PCG 图表**：在内容浏览器中找到示例的 `PCG Graph` 资产并双击打开。分析其节点构成，重点关注 `Input` 节点如何获取场景数据，`Transform Points`、`Spline Sampler` 等节点如何处理几何体，以及 `Output` 节点如何向 Mesh Partition 系统传递数据。
4.  **学习配置**：查看示例中的 Mesh Partition 数据资产，理解其分区规则是如何与 PCG 图表输出的数据（如点属性）相关联的。
5.  **复制与修改**：最高效的学习方法是复制这些示例资产到你的项目 Content 目录，然后根据你的游戏需求修改 PCG 图表中的生成逻辑或 Mesh Partition 的分区规则。

## C++ 用法

不适用。本插件为纯内容插件，不包含任何 C++ 模块或源代码。

## Demo 示例

虽然无法提供可编译的 C++ 代码，但以下是一个基于此插件示例资产的典型**工作流程描述**：

**目标**：在丘陵地形上随机生成树木，并将它们按类型（松树、橡树）分区，以便后续进行统一的 LOD 管理。

1.  **资产准备**：
    *   从插件中复制或参考 `PCG_GenerateTreePoints` 图表。
    *   复制或参考 `MP_TreeForest` 网格分区配置资产。
2.  **配置 PCG 图表**：
    *   使用 `Surface Sampler` 节点在地形丘陵上采样点。
    *   使用 `Attribute Transfer` 节点根据地形高度或坡度为点添加 `TreeType` 属性（例如：高度 > 500 为 `Pine`， 否则为 `Oak`）。
    *   使用 `Static Mesh Spawner` 节点，并根据 `TreeType` 属性选择不同的树木网格体。
    *   将这些点和它们的属性通过 `Output` 节点输出。
3.  **配置 Mesh Partition**：
    *   创建一个新的 Mesh Partition 资产，添加两个分区规则（`PineForest`, `OakForest`）。
    *   设置每个规则的**过滤器**：`PineForest` 规则过滤 `TreeType == Pine` 的网格实例，`OakForest` 规则过滤 `TreeType == Oak` 的网格实例。
    *   为每个分区配置合适的 LOD 切换距离和碰撞策略。
4.  **整合到关卡**：
    *   创建一个 Actor 蓝图。
    *   添加一个 `PCG Component`，并分配步骤 2 中配置好的 PCG 图表。
    *   添加一个 `Mesh Partition Component`，并分配步骤 3 中配置好的网格分区资产。
    *   将此 Actor 蓝图放入关卡。
5.  **运行与观察**：
    *   运行关卡，PCG 图表会根据地形程序化生成树木点。
    *   Mesh Partition 系统会自动根据树木的 `TreeType` 属性将其分配到对应的森林分区中，实现统一的渲染优化管理。

## 模块依赖

本插件本身无模块。但它依赖的其他插件，意味着你的项目需要启用它们：

| 依赖插件 | 用途 |
|---|---|
| `PCG` | 核心程序化内容生成框架 |
| `PCGPrimitives` | 提供 PCG 框架的基础节点和功能 |
| `MeshPartition` | 提供网格分区与管理的核心功能 |
| `MeshTerrainMode` | 提供与地形网格相关的特定模式或功能 |
| `PCGMeshPartitionInterop` | 提供 PCG 数据与网格分区系统之间互操作的桥梁功能 |
| `PCGBiomeSample` | 提供生态系统（Biome）相关的 PCG 示例，可能包含更复杂的环境生成逻辑 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `d2353f53` | PCG Primitives plugins: small friendly name tweak to match other PCG data plugins. | 对插件的友好名称进行了微小调整，以与其他PCG数据插件保持一致。 |
| 2026-04-27 | `b1bc0d70` | PCG Primitives: moved the PCGPrimitives_MeshPartitionInterop plugin into public facing plugins/experimental folder. | 将此插件从内部目录移动到了公开的实验性插件文件夹。 |

### 维护评价

- **创建时间**：插件于 2026 年 4 月底创建，非常新。
- **最近更新**：创建后仅进行了一次名称调整。由于插件性质为纯内容示例，除非底层依赖的插件（如 PCG、Mesh Partition）API 发生重大变化，否则其内容本身可能不需要频繁更新。
- **活跃状态**：**实验性且内容固定**。作为一个实验性的示例库，它的主要目的是提供参考。其“活跃维护”更多地体现在 Epic Games 对 `PCG` 和 `MeshPartition` 这两个核心插件的维护上。
- **已知问题**：作为示例，它可能没有针对所有边缘情况进行优化，也可能在特定引擎版本上因依赖插件的更新而需要手动调整资产。
- **推荐使用**：**强烈推荐给正在学习或评估“PCG + Mesh Partition”工作流的开发者**。它是理解这套官方推荐组合用法的绝佳起点。但不应将其作为生产环境中的直接依赖项，而应将其作为学习资源，将其中学到的原理应用到你自己的资产和图表配置中。

**注意**：由于此插件标记为 `IsExperimentalVersion`，且默认未安装 (`Installed: false`)，它可能包含实验性功能，并且在未来的引擎版本中其内容、结构或位置可能会发生变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PCGPrimitives_MeshPartitionInterop)
- [官方文档]( ) （无）
- [测试用例]( ) （无，此插件为纯内容插件）