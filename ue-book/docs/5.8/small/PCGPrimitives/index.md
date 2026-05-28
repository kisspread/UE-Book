# PCG Primitives

> PCG Primitives and Examples Library for World Building（PCG 基本体与世界构建示例库）

| 属性 | 值 |
|---|---|
| 中文名 | PCG基本体库 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、PCG图资产、材质、示例场景） |
| 模块 | 无（纯内容插件） |
| 实验性 | ⚦ 是 |
| 创建时间 | 2026-04-27 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PCGPrimitives) | |

## 用途

`PCGPrimitives` 是一个**纯内容插件**，为 Unreal Engine 的程序化内容生成（PCG）框架提供一个基础几何体和示例的资源库。它并非提供新的 C++ 模块或蓝图函数，而是预制了一系列 PCG 图表（Graphs）、静态网格体（Static Meshes）、材质（Materials）和示例场景，旨在帮助开发者快速启动和构建基于 PCG 的世界生成工作流。它解决了从零开始创建 PCG 图表和查找合适基本体形状的麻烦。

## 使用场景

- **快速原型设计**：当你需要为一个关卡快速搭建程序化的环境布局（如森林、岩石地带）时，可以直接使用本插件提供的 PCG 图表和基本体资产，大幅缩短搭建时间。
- **学习 PCG 工作流**：插件内的示例图表和场景是优秀的学习材料，可以帮助你理解如何将 PCG 与 Geometry Script、Biome 系统等结合使用。
- **需要基础几何体**：在 PCG 生成中需要使用立方体、球体、圆柱体等作为生成器的种子表面或遮罩形状时，可以直接调用本插件提供的基本体资产。

## 蓝图用法

这是一个**纯内容插件**，不包含任何 C++ 模块或新的蓝图函数库。其价值体现在提供的资产上。

### 核心资产

| 资产类型 | 说明 | 用途 |
|---|---|---|
| PCG 图表（`PCGGraph`） | 预先配置好的 PCG 生成逻辑 | 作为模板直接使用或在其基础上修改 |
| 静态网格体（`StaticMesh`） | 基础几何体（立方体、球体等） | 作为 PCG 生成器输入的表面，或直接放置在关卡中 |
| 材质（`Material`） | 配套的材质实例 | 为基本体提供视觉效果 |

### 使用示例（蓝图描述）

1.  **启用插件**：在编辑器中，通过 `Edit -> Plugins` 搜索 “PCG Primitives” 并启用。
2.  **访问资产**：在 Content Browser 中，导航到 `Plugins/PCG Primitives Content` 目录，即可找到所有提供的 PCG 图表、网格体和材质。
3.  **使用 PCG 图表**：
    *   将一个预设的 `PCGGraph` 资产（例如生成树林的图表）拖入关卡。
    *   在图表的 `Input` 节点上，你可能会看到它接受一个或多个“表面”输入。此时，可以将本插件提供的基础几何体（如一个 `SM_Cube`）的静态网格体组件，或者关卡中的其他 Actor（如地形）作为输入。
    *   根据图表逻辑，它将在输入表面的上方/周围程序化地生成物体（如树木、岩石）。
4.  **组合使用**：你可以创建一个新的 PCG 图表，将插件中的基本体资产作为 `Surface Sampler` 或 `Projection` 节点的输入，来实现自定义的生成逻辑。

## C++ 用法

本插件**没有提供任何 C++ 代码或模块**，因此无法在 C++ 项目中进行代码层面的集成或调用。它的全部价值在于其提供的内容资产，这些资产可以在蓝图或编辑器中直接使用。

## Demo 示例

本插件自身就是一个完整的 Demo 库。最佳的示例体验方式是：

1.  确保 `PCGPrimitives` 及其依赖的插件（如 `PCG`）已启用。
2.  在 Content Browser 中找到并打开 `PCGPrimitives` 插件目录。
3.  探索其中的 `Examples` 或 `Maps` 子文件夹，打开预设的关卡场景。
4.  在场景中查看 PCG Actor 的运行效果，并双击关联的 `PCGGraph` 资产以学习其内部逻辑构建。
5.  尝试修改图表中的参数（如生成密度、随机种子）或替换输入表面，观察生成结果的变化。

## 模块依赖

本插件自身不包含代码模块，但它的功能依赖于一系列其他 PCG 框架插件。要正常使用 `PCGPrimitives`，你需要确保以下插件已启用（它们通常在启用 `PCGPrimitives` 时会被自动勾选）：

| 模块 | 用途 |
|---|---|
| `PCG` | 核心 PCG 框架插件，提供图表编辑器和执行逻辑。 |
| `PCGGeometryScriptInterop` | 允许在 PCG 图表中使用 Geometry Script 节点，用于动态网格体操作。 |
| `PCGBiomeCore` | PCG 生物群落系统的核心组件，用于管理和生成生态区域。 |
| `PCGBiomeSample` | 生物群落系统的示例内容，可能被本插件的示例图表所引用。 |
| `PCGExternalDataInterop` | 允许 PCG 读取外部数据源，扩展了数据输入的灵活性。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `d2353f53` | PCG Primitives plugins: small friendly name tweak to match other PCG data plugins. | 微调插件友好名称，以保持与其他PCG数据插件命名风格一致。 |
| 2026-04-27 | `8f1b41e9` | PCG Primitives: moved the PCG_Primitives plugin into public facing plugins/experimental folder. | 将PCG_Primitives插件从内部移至面向公众的experimental文件夹，标志其公开发布。 |

### 维护评价

该插件于 **2026 年 4 月底** 作为实验性功能首次公开，**维护状态为活跃**。最近一次更新（2026年5月）仅为名称微调，说明其初始版本发布后内容已相对稳定。作为 Epic Games 官方维护的实验性插件，其质量有一定保障，但**实验性状态意味着其 API 和资产结构在未来版本中可能发生破坏性变更**。

**建议**：如果你的项目正处于快速迭代期，或者你可以接受未来可能需要根据插件更新进行适配，那么可以积极使用本插件来加速开发。如果项目处于长期维护状态且追求稳定，则需谨慎评估实验性状态带来的风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PCGPrimitives)
- [PCG 官方文档](https://docs.unrealengine.com/5.8/en-US/procedural-content-generation-overview/) (PCG 框架总览)
- 测试用例：本插件为纯内容插件，无独立的代码测试用例。其测试体现在预置的示例场景中。