# PCG Primitives Mesh Partition Interop

> Extra PCG Primitives and Examples Library for Mesh Partition interop

| 属性 | 值 |
|---|---|
| 中文名 | PCG 图元网格分区互操作 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（PCG 原始资产与 Mesh Partition 互操作示例） |
| 模块 | 无（纯内容插件） |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-27 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PCGPrimitives_MeshPartitionInterop) | |

## 用途

这是一个**纯内容插件**，不包含任何 C++ 源码，仅提供蓝图资产和示例资源。其核心作用是为 **PCG（Procedural Content Generation）系统**与 **Mesh Partition（网格分区）** 之间的互操作提供额外的原始图元（Primitives）和示例配置。

具体来说，它作为"胶水层"将以下系统连接起来：

- **PCG**：程序化内容生成框架，用于自动生成关卡、植被、建筑等内容
- **PCGPrimitives**：PCG 的基础图元库
- **MeshPartition**：网格分区系统，用于将大型网格拆分为可管理的区域
- **MeshTerrainMode**：网格地形模式
- **PCGMeshPartitionInterop**：PCG 与网格分区的底层互操作模块
- **PCGBiomeSample**：PCG 生物群落示例

该插件的存在使得用户可以在 PCG 图表中方便地使用 Mesh Partition 功能，而无需自行编写复杂的互操作逻辑。

## 使用场景

- 你正在使用 PCG 系统进行**程序化地形/环境生成**，需要将生成的网格自动分区 → 使用此插件获取预制的图元和示例配置
- 你需要参考**官方如何将 PCG 与 Mesh Partition 集成** → 查看本插件中的示例资产
- 你在开发需要**大规模网格管理**的项目（如开放世界），想利用 PCG + Mesh Partition 的组合方案 → 安装此插件作为起点

## 蓝图用法

本插件为纯内容插件，不包含自定义蓝图节点。所有功能通过其依赖插件提供的节点实现。

请参阅以下依赖插件的文档获取蓝图 API：

- **PCG** — 提供 `UPCGGraph`、`UPCGSettings` 等核心节点
- **PCGPrimitives** — 提供基础 PCG 图元节点
- **PCGMeshPartitionInterop** — 提供 PCG 与 Mesh Partition 之间的互操作节点

## C++ 用法

本插件不包含 C++ 源码，无 C++ 用法。

## Demo 示例

本插件本身就是示例集合。安装后，可在 Content Browser 中浏览插件内容目录，查看预置的 PCG 图表和配置资产。

## 模块依赖

本插件为纯内容插件，无 Build.cs 文件。但它通过 `.uplugin` 声明了以下插件依赖（所有依赖均默认启用）：

| 依赖插件 | 用途 |
|---|---|
| `PCG` | 程序化内容生成核心框架 |
| `PCGPrimitives` | PCG 基础图元库 |
| `MeshPartition` | 网格分区系统 |
| `MeshTerrainMode` | 网格地形模式支持 |
| `PCGMeshPartitionInterop` | PCG 与 Mesh Partition 的底层互操作逻辑 |
| `PCGBiomeSample` | PCG 生物群落示例（可能提供参考资产） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `d2353f53` | PCG Primitives plugins: small friendly name tweak to match other PCG data plugins. | 调整插件友好名称，与其他 PCG 数据插件保持一致 |
| 2026-04-27 | `b1bc0d70` | PCG Primitives: moved the PCGPrimitives_MeshPartitionInterop plugin into public facing plugins/experimental folder. | 将插件从内部目录迁移至公开的 Experimental 文件夹 |

### 维护评价

- **创建时间**：2026-04-27，极其年轻的插件（约 2 周）
- **更新频率**：创建后仅 1 次功能性更新（名称调整），目前为初始阶段
- **状态**：刚从 Epic 内部迁移至公开 Experimental 目录，处于早期发布阶段
- **实验性标记**：`IsExperimentalVersion=true`，`Installed=false`，需要手动启用
- **已知限制**：纯内容插件，功能完全依赖其 6 个插件依赖项；如果任何依赖缺失或未启用，本插件将无法正常工作
- **推荐**：适合对 PCG + Mesh Partition 集成感兴趣的用户参考使用，但作为实验性插件，API 和资产结构可能在未来版本中发生变化，不建议直接用于生产环境

⚠️ **注意**：此插件刚于 2026 年创建，尚无足够历史数据评估长期维护情况。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PCGPrimitives_MeshPartitionInterop)