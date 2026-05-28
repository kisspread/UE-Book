# PCG Biome Sample

> PCG Biome Sample Plugin

| 属性 | 值 |
|---|---|
| 中文名 | PCG生态示例 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产，示例关卡） |
| 模块 | 无（纯内容插件） |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-02-07 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PCGBiomeSample) | |

## 用途

`PCGBiomeSample` 是 `PCGBiomeCore` 插件的示例与测试工程。它不包含任何代码模块，其核心价值在于提供一套完整的、可运行的蓝图资产示例，演示了如何利用 `PCGBiomeCore` 提供的节点和框架，在实际项目中创建和管理动态生态系统（Biome）。该插件旨在降低 `PCGBiomeCore` 的学习门槛，并为开发者提供一个快速上手的蓝图蓝图。

## 使用场景

- **学习与理解**：如果你想深入了解和学习如何使用 `PCGBiomeCore` 插件来生成复杂、动态的自然生态系统（如森林、草地、岩石群落），那么这个示例插件是你的必备起点。
- **快速原型**：在需要快速搭建一个基于程序化内容生成（PCG）的生态系统原型时，可以直接参考或迁移此插件中的资产与逻辑。
- **功能验证**：`PCGBiomeCore` 插件的开发者可以使用此示例插件来验证新功能、测试用例或演示最佳实践。

## 蓝图用法

此插件本身不提供可调用的蓝图节点或函数（UFUNCTION）。它主要由 **蓝图资产（`UPCGSubsystem` 等类）、PCG图表资产和示例关卡** 构成。
要学习其用法，你应该：
1. 启用 `PCGBiomeSample` 和 `PCGBiomeCore` 插件。
2. 打开该插件提供的示例地图或蓝图。
3. 在蓝图编辑器中分析这些资产是如何配置和调用 `PCGBiomeCore` 节点的。

### 核心资产（非函数）

| 资产类型 | 说明 |
|---|---|
| PCG Graph 资产 | 定义了生态系统生成的核心逻辑（如树木分布、草地密度规则）。 |
| 蓝图资产 | 可能包含 Biome Manager、Spawner 等蓝图类，用于管理场景中的生态系统实例。 |
| 示例关卡 | 一个已经配置好并应用了 `PCGBiomeCore` 生成逻辑的完整场景。 |

### 使用示例（蓝图描述）
由于是示例插件，你主要通过 **分析资产蓝图图** 来学习。典型的蓝图图节点连接可能如下：
1. **入口**：一个 `EventBeginPlay` 或自定义事件节点。
2. **获取系统**：调用 `Get PCG Subsystem` 节点。
3. **执行生成**：调用该子系统中用于触发 Biome 生成的函数，并传入对应的 PCG 图表资产引用。
4. **参数传递**：通过变量或数据表向 PCG 图表传递参数（如种子值、密度倍数）。
5. **结果应用**：PCG 图表执行后生成的点数据将自动驱动场景中 Actor（如植物、石头）的生成和变换。

## C++ 用法

此插件 **不包含任何 C++ 源代码模块**。它是一个纯内容（Content-Only）插件。
要以编程方式使用 `PCGBiomeCore` 的功能，你需要依赖 `PCGBiomeCore` 模块本身，而不是这个示例插件。

### 头文件引入
（不适用，此插件无代码模块）

### 基本用法
（不适用，此插件无代码模块）

### 进阶用法
（不适用，此插件无代码模块）

## Demo 示例

`PCGBiomeSample` 插件本身就是一个完整的、可编译运行的“Demo”。其核心是 **蓝图资产和示例关卡**。
启动插件后，打开其自带的示例关卡即可看到运行效果。要理解其构建方式，请在编辑器中查看并分析相关的蓝图图资产和 PCG 图表资产。这为你提供了一个脱离复杂代码、纯粹关注逻辑编排的学习路径。

## 模块依赖

该插件自身的 `.uplugin` 声明了以下插件依赖：
| 模块 | 用途 |
|---|---|
| `PCGBiomeCore` | 提供创建和管理 Biome 生态系统的核心功能库与蓝图节点。 |
| `PCG` | 基础程序化内容生成框架，`PCGBiomeCore` 构建于其上。 |

此外，由于这是一个包含蓝图资产的插件，你的项目必须 **启用** `PCGBiomeCore` 和 `PCG` 这两个运行时插件。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-03-28 | `8d218026` | PCG Biome Core V2 : updated uplugins version number to reflect biome core and sample major refactor | 配合PCG Biome Core V2大版本重构，更新插件版本号。 |
| 2024-06-27 | `5e4a560d` | PCG Biome Sample: added PCG plugin dependency to BiomeSample as well (was depending on BiomeCore bef | 为示例插件补充声明对基础PCG插件的依赖，确保运行时正确加载。 |
| 2024-02-07 | `7d78cbd1` | PCG BiomeSample Plugin: Moved from Restricted/NotForLicensees to Experimental | 插件从内部代码库迁移至Experimental目录，向开发者开放。 |

### 维护评价

`PCGBiomeSample` 作为核心功能 `PCGBiomeCore` 的配套示例插件，其更新与维护 **高度依赖于 `PCGBiomeCore` 的演进**。
- **活跃维护**：从提交历史看，它在2024年发布，并在2025年随着 `PCGBiomeCore` 的大版本更新（V2）进行了同步更新，表明**核心功能仍在积极开发中**。
- **实验性质**：插件本身标记为实验性 (`IsExperimentalVersion=true`)，且默认未启用。这意味着其API、资产结构和最佳实践可能会在未来的版本中发生 **破坏性变更**。
- **推荐使用**：**强烈推荐** 给所有对 `PCGBiomeCore` 感兴趣的学习者和开发者作为入门和参考。但**不建议**直接在生产项目中依赖此示例插件的资产，而应学习其方法后，创建自己的资产和逻辑。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PCGBiomeSample)
- 测试用例：此插件的测试逻辑主要集成在其依赖的 `PCGBiomeCore` 插件内部。