# PCG Primitives

> PCG Primitives and Examples Library for World Building（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | PCG 图元库 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | 无（纯内容插件） |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2026-04-27 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PCGPrimitives) | |

## 用途

该插件是 **PCG（Procedural Content Generation，程序化内容生成）框架** 的一个**示例资产库**。它本身不提供新的 C++ 代码模块，而是提供了一套预制的蓝图资产和 PCG 图（PCG Graph），旨在作为“图元”和“示例”供开发者使用和学习。

它的存在是为了：
1.  **加速世界构建**：提供基础几何体（图元）的程序化生成示例，用户可以直接使用或在此基础上修改，快速搭建场景。
2.  **展示最佳实践**：通过示例展示如何结合 PCG 框架与相关的生态系统插件（如 Biome 核心、几何体脚本互操作等）来完成复杂的世界生成任务。
3.  **降低学习门槛**：为想学习 PCG 框架的开发者提供可直接研究、拆解的实用案例。

## 使用场景

-   你正在使用 UE5 的 **PCG 框架** 进行大规模世界构建，需要现成的、基于规则的图元生成方案。
-   你想为地形、植被、建筑等生成标准化的程序化基础结构（如道路网络、建筑地基、河流网格等）。
-   你是 PCG 框架的新手，希望通过官方示例来理解 PCG 图（PCG Graph）的编写逻辑和节点用法。
-   你的项目依赖于 `PCGBiomeCore` 等插件，并需要参考相关的集成示例。

## 蓝图用法

由于本插件是纯内容插件（`CanContainContent: true`），其“用法”主要体现在对内置资产的**引用、学习和修改**上。

### 核心资产（示例）

本插件的核心内容是蓝图和 PCG 图资产，位于插件的 `Content` 文件夹下。您可以在内容浏览器中找到并查看。

| 资产类型 | 说明 |
|---|---|
| `PCG Graph` 蓝图 | 这是插件的核心。它们定义了生成世界元素的规则和逻辑。您可以直接拖入关卡使用，或作为子图被其他更大的 PCG 图引用。 |
| `PCG Component` 蓝图 | 可能包含将 PCG 图应用到 Actor 上的组件类。 |
| `Data Asset` | 存储生成规则所需的参数和配置。 |

### 使用示例（蓝图描述）

1.  **在内容浏览器中**：导航至 `Plugins/PCG Primitives Content`。
2.  **找到一个 PCG Graph 资产**（例如，一个用于生成道路网络的图）。
3.  **将其直接拖拽到您的关卡视口中**。通常，这会自动创建一个带有 `PCG Component` 的 Actor 并运行该图。
4.  **选中关卡中的该 Actor**，在细节面板中找到 `PCG Component`，您可以修改其属性（如生成范围、种子等）或直接**点击“Generate”按钮**来重新生成内容。
5.  **双击 PCG Graph 资产**，打开 PCG 图编辑器，您可以研究其内部节点网络，学习节点连接方式，并复制、修改这些逻辑到您自己的 PCG 图中。

## C++ 用法

本插件是一个**纯内容插件**，不包含任何 C++ 代码模块。因此，它**不提供直接的 C++ API**。

其用法完全在蓝图和编辑器层面完成。如果您需要在 C++ 项目中引用本插件的资产（例如，一个 Data Asset），您需要通过资产路径进行加载，但这通常不常见。

## Demo 示例

本插件本身就是一系列 Demo 示例。

您可以直接在编辑器中通过以下方式体验：
1.  启用插件（在“插件”设置中搜索“PCG Primitives”并启用）。
2.  重启编辑器。
3.  在内容浏览器中，定位到 `Plugins/PCG Primitives Content` 目录。
4.  将您感兴趣的任何 `PCG Graph` 资产拖入关卡即可观察其生成效果。

## 模块依赖

本插件自身无模块。要使其内容资产正常工作，您的项目需要启用以下插件（这些是本插件运行时隐含的依赖）：

| 插件/模块 | 用途 |
|---|---|
| `PCG` | 程序化内容生成框架的核心，所有 PCG 图运行的基础。 |
| `PCGGeometryScriptInterop` | 允许 PCG 系统与 Geometry Script 进行交互，用于高级几何体操作。 |
| `PCGBiomeCore` | 生物群落生成系统的核心，本插件示例可能演示了如何与生物群落结合。 |
| `PCGBiomeSample` | 提供生物群落系统的示例内容。 |
| `PCGExternalDataInterop` | 允许 PCG 从外部源（如表格）读取数据。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `d2353f53` | PCG Primitives plugins: small friendly name tweak to match other PCG data plugins. | 调整了插件的“友好名称”，以与其他 PCG 数据类插件保持一致。 |
| 2026-04-27 | `8f1b41e9` | PCG Primitives: moved the PCG_Primitives plugin into public facing plugins/experimental folder. | 首次提交：将插件从内部路径移至公开的实验性文件夹，标志着该插件的发布。 |

### 维护评价

-   **实验性**：该插件明确标记为 `IsExperimentalVersion: true`，且位于 `Experimental` 文件夹，表明它仍处于开发和验证阶段，API 和内容未来可能发生重大变化。
-   **活跃维护**：插件创建于 2026 年 4 月底，最近一次更新在 2026 年 5 月，表明它正被 Epic 积极调整和维护。
-   **内容导向**：作为示例库，其主要价值在于提供学习范本和快速启动方案，其本身可能不会频繁添加新“功能”，但会随着 PCG 框架的更新而维护兼容性。
-   **推荐使用**：**推荐用于实验、原型设计和学习**。由于是实验性插件，**不建议在需要高度稳定性的正式生产项目中作为核心依赖**，但可以借鉴其思路和资产。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PCGPrimitives)
-   官方文档：暂无
-   测试用例：暂无