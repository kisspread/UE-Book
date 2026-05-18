# PCG Primitives Mesh Partition Interop

> Extra PCG Primitives and Examples Library for Mesh Partition interop

| 属性 | 值 |
|---|---|
| 中文名 | PCG 图元网格分区互操作 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（PCG 数据资产、示例蓝图） |
| 模块 | 无（纯内容插件） |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-27 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PCGPrimitives_MeshPartitionInterop) | |

## 用途

该插件是一个**纯内容资产包**，提供了 PCG（Procedural Content Generation）系统与 Mesh Partition 系统之间互操作所需的额外图元数据和示例资源。

核心功能：当你需要将 PCG 程序化生成的内容（如植被、岩石、装饰物等）与网格分区系统（用于大型开放世界的流式加载和分区管理）结合使用时，该插件提供了预制的图元定义和配置示例，帮助开发者快速实现两者之间的数据对接。

它解决的问题是：PCG 生成的内容如何正确地映射到 Mesh Partition 的分区系统中，确保程序化生成的资产能够正确参与世界分区和流式加载。

## 使用场景

- 你在使用 PCG 框架生成开放世界内容，需要让生成的物体正确参与 Mesh Partition 分区 → 启用此插件获取示例和图元定义
- 你需要参考 Epic 官方的 PCG + Mesh Partition 互操作最佳实践 → 查看此插件中的示例资产
- 你正在开发基于 PCG 的生物群系系统，需要与地形网格分区协同工作 → 依赖此插件提供的基础图元

## 蓝图用法

此插件为纯内容插件，不包含 C++ 代码。提供的资产主要是 PCG 数据资产（PCG Data Assets），可在 PCG 图表中直接引用。

### 使用方式

1. 启用插件后，可在内容浏览器中找到相关资产
2. 在 PCG 图表（PCG Graph）中使用提供的图元作为生成器或修改器
3. 参考示例了解如何配置 PCG 输出以兼容 Mesh Partition 系统

### 所需前置插件

使用此插件前，需确保以下插件已启用（该插件会自动启用它们）：

| 插件 | 用途 |
|---|---|
| `PCG` | 核心 PCG 框架 |
| `PCGPrimitives` | PCG 图元基础库 |
| `MeshPartition` | 网格分区系统 |
| `MeshTerrainMode` | 网格地形模式 |
| `PCGMeshPartitionInterop` | PCG 与网格分区互操作核心模块 |
| `PCGBiomeSample` | PCG 生物群系示例 |

## C++ 用法

此插件为纯内容插件，不包含 C++ 代码，无需引入头文件或编写 C++ 代码。

如需在 C++ 项目中以编程方式与 PCG + Mesh Partition 系统交互，请参考 `PCGMeshPartitionInterop` 插件的 API。

## Demo 示例

此插件本身就是示例资产集合。启用后可直接在内容浏览器中浏览提供的 PCG 数据资产和配置示例。

建议结合 `PCGBiomeSample` 插件一起使用，以获取完整的生物群系 + 网格分区互操作示例。

## 模块依赖

无特殊依赖（纯内容插件，通过插件依赖声明获取功能）

该插件通过 `.uplugin` 的 `Plugins` 字段声明了对以下插件的依赖，启用时会自动加载：

| 依赖插件 | 用途 |
|---|---|
| `PCGPrimitives` | 提供基础 PCG 图元定义 |
| `MeshPartition` | 提供网格分区功能 |
| `MeshTerrainMode` | 提供网格地形模式支持 |
| `PCGMeshPartitionInterop` | PCG 与 Mesh Partition 的核心互操作逻辑 |
| `PCG` | UE5 核心 PCG 框架 |
| `PCGBiomeSample` | 生物群系示例资产 |

## 维护状态

### 近期更新

```
- 2026-05-12 d2353f53 PCG Primitives plugins: small friendly name tweak to match other PCG data plugins.
- 2026-04-27 b1bc0d70 PCG Primitives: moved the PCGPrimitives_MeshPartitionInterop plugin into public facing plugins/experimental
```

### 维护评价

- **创建时间**：2026-04-27，极其年轻的插件（不到 1 个月）
- **更新频率**：2 次提交，均为初期调整（命名规范化、迁移到公开路径）
- **维护状态**：🆕 新发布，尚处于早期阶段
- **实验性标记**：`IsExperimentalVersion=true`，`Installed=false`，属于实验性插件
- **注意事项**：
  - 这是一个非常新的实验性插件，API 和资产内容可能随时变化
  - 作为纯内容插件，其稳定性依赖于所依赖的功能插件（如 PCGMeshPartitionInterop）
  - 当前处于 Experimental 目录下，可能在后续版本中被移除或合并

**推荐**：仅在需要参考 PCG + Mesh Partition 互操作的官方示例时使用，不建议在生产环境中直接依赖此实验性内容插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PCGPrimitives_MeshPartitionInterop)
- [PCG 框架文档](https://docs.unrealengine.com/5.8/en-US/procedural-content-generation-framework-in-unreal-engine/)（PCG 核心文档）
- 无官方文档链接（`.uplugin` 中 DocsURL 为空）