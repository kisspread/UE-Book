# PCG Primitives

> PCG Primitives and Examples Library for World Building

| 属性 | 值 |
|---|---|
| 中文名 | PCG基础图元库 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、示例关卡、材质等） |
| 模块 | 无（纯内容插件） |
| 实验性 | ⚦ 是 |
| 创建时间 | 2026-04-27 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PCGPrimitives) | |

## 用途

该插件是一个**内容集合**，旨在为使用程序化内容生成（PCG）框架进行世界构建的开发者提供一套基础的几何形状（图元）和实用示例。它不是一个功能插件，而是一个资源库，用于加速PCG工作流的原型设计和学习过程。

## 使用场景

- 当你使用 PCG 框架进行场景布局时，需要快速使用基础几何形状（如立方体、圆柱体、球体）作为生成点的载体或视觉参考。
- 当你在学习 PCG 时，需要查看官方如何设置图表、应用滤镜、处理数据以及与其它PCG插件（如Biome系统）协作的完整示例。
- 当你需要在PCG图表中生成简单的代理几何体进行碰撞检测或视觉填充，而无需依赖复杂网格体时。

## 蓝图用法

此插件主要提供资产，因此其“蓝图用法”主要体现在对这些资产的引用和PCG图表中的节点使用上。

### 核心资产

所有资产位于 `Content/PCGPrimitives` 目录下。

| 资产类型 | 路径示例 | 说明 |
|---|---|---|
| PCG Graph | `Content/PCGPrimitives/Graphs/...` | 包含使用基础图元的PCG图表示例。 |
| Static Mesh | `Content/PCGPrimitives/Meshes/...` | 基础几何体网格，如立方体、球体。 |
| Material | `Content/PCGPrimitives/Materials/...` | 配套的材质，常用于生成可视化标记。 |
| Blueprient | `Content/PCGPrimitives/Blueprints/...` | 可能包含特定于示例的蓝图或数据资产。 |

### 使用示例（蓝图描述）

1.  **在PCG图表中使用**：打开一个示例PCG图表，你会看到 `Surface Sampler`、`Density Filter` 等节点直接引用了插件提供的基础网格体作为“Surface Mesh”或“Instanced Mesh”。
2.  **内容浏览器访问**：在内容浏览器中导航到 `Plugins/PCG Primitives Content`，即可找到所有提供的资产。你可以直接将其中的网格体或材质复制到你的项目中使用。

## C++ 用法

此插件不包含任何C++模块，因此**不需要**在C++代码中引入任何头文件或链接任何模块。所有功能通过蓝图资产和PCG图表实现。

## Demo 示例

该插件本身即为一个大型的Demo示例库。一个典型的用法步骤如下：

1.  启用插件。
2.  在内容浏览器中找到 `Content/PCGPrimitives/Graphs`。
3.  打开一个示例图表（例如，一个在地形上撒布基础几何体的图表）。
4.  运行该PCG图表，观察生成的效果。
5.  研究图表中的节点设置和数据流动，以此为基础创建你自己的PCG图表。

## 模块依赖

此插件本身无代码模块，但其正常运行依赖于一系列PCG生态系统插件。这些插件通常也需要启用。

| 插件 | 用途 |
|---|---|
| `PCG` | 核心程序化内容生成框架，提供PCG图表、节点等基础功能。 |
| `PCGGeometryScriptInterop` | 提供PCG与几何脚本的交互能力，用于处理网格体数据。 |
| `PCGBiomeCore` | 生物群系核心系统，用于定义环境规则。 |
| `PCGBiomeSample` | 生物群系示例，展示如何使用BiomeCore。 |
| `PCGExternalDataInterop` | 提供PCG与外部数据源（如JSON， CSV）的交互能力。 |

## 维护状态

### 近期更新

```
- 2026-05-12 d2353f53 PCG Primitives plugins: small friendly name tweak to match other PCG data plugins.
- 2026-04-27 8f1b41e9 PCG Primitives: moved the PCG_Primitives plugin into public facing plugins/experimental folder.
```

### 维护评价

**实验性内容插件**。该插件于2026年4月底创建，非常新。目前仅有两次提交，一次为创建，一次为小的名称调整，表明它仍处于**实验性早期阶段**。作为内容库，其更新频率取决于PCG框架核心功能的变化和示例的扩展。

**建议**：适合用于学习PCG框架和快速原型验证。由于是实验性插件，不建议在正式发布的项目中直接深度依赖，其资产结构或内容可能在未来版本中发生变化。推荐用于开发和学习阶段。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PCGPrimitives)
- [测试用例]（该插件为纯内容插件，其“测试”即为插件内提供的示例关卡和图表资产。）