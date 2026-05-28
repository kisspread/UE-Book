# Datasmith CAD Importer

> Collection of tools to work with CAD files.

| 属性 | 值 |
|---|---|
| 中文名 | CAD 导入工具集 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CADInterfaces` (Runtime), `CADKernelSurface` (Runtime), `CADLibrary` (Runtime), `CADTools` (Runtime), `DatasmithCADTranslator` (Runtime), `DatasmithDispatcher` (Runtime), `DatasmithOpenNurbsTranslator` (Runtime), `DatasmithPLMXMLTranslator` (Runtime), `DatasmithWireTranslator` (Runtime), `ParametricSurface` (Runtime), `ParametricSurfaceExtension` (Runtime), `WireInterface2020` (Runtime), `WireInterface2021_3` (Runtime), `WireInterface2022` (Runtime), `WireInterface2022_1` (Runtime), `WireInterface2022_2` (Runtime), `WireInterface2023_0` (Runtime), `WireInterface2023_1` (Runtime), `WireInterface2024_1` (Runtime), `WireInterface2025_0` (Runtime), `WireInterface2026_0` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 🏛️ 文物（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

## 用途

此插件并非一个单一的转换器，而是一个庞大的 CAD 数据处理与导入框架。其核心目的是将工业级 CAD 软件（如 CATIA, NX, SolidWorks, Rhino, STEP, IGES 等）生成的复杂模型数据，通过 Datasmith 管线高效、精确地导入到 Unreal Engine 中。它解决了直接转换 CAD 原生文件（包含精确几何、装配体结构、材质和元数据）到游戏引擎实时格式（如多边形网格）时的精度、拓扑和性能挑战。

## 使用场景

- **工业数字孪生与可视化**：在 UE 中精确重现复杂的机械装配体、工厂布局或产品设计，用于设计评审、运维模拟。
- **建筑 BIM 模拟**：导入来自 Revit 等软件的 BIM 模型，保留楼层、构件类别等信息，用于建筑可视化与交互演示。
- **跨软件资产管线**：建立从 CAD 设计软件到 UE 虚拟制作或实时应用的自动化数据管线，减少手动转换工作量。
- **处理大型 CAD 装配体**：利用其调度器（DatasmithDispatcher）和多线程功能，处理包含成千上万个零部件的超大装配体。

## 模块概述

此插件采用模块化架构，主要分为以下几类：

### 核心基础模块
| 模块 | 功能简介 |
|---|---|
| `CADInterfaces` | 定义与各种 CAD 格式交互的统一接口，依赖 TechSoft 内核。 |
| `CADKernelSurface` | 处理基于内核的参数化曲面几何数据。 |
| `CADLibrary` | 提供 CAD 数据转换所需的核心库和工具。 |
| `CADTools` | 包含 CAD 文件处理和几何操作的通用工具集。 |
| `ParametricSurface` / `ParametricSurfaceExtension` | 处理参数化曲面的细分与网格生成。 |

### 格式翻译器模块
| 模块 | 功能简介 |
|---|---|
| `DatasmithCADTranslator` | 主翻译器，协调其他特定格式翻译器工作。 |
| `DatasmithOpenNurbsTranslator` | 专门处理 .3dm (Rhino) 等 OpenNurbs 格式。 |
| `DatasmithPLMXMLTranslator` | 处理 PLMXML 格式，常用于 PLM 系统数据交换。 |
| `DatasmithWireTranslator` | 处理 CATIA V5 的 .model 和 .CATPart 等 Wire 格式。 |

### WireInterface 版本适配模块
`WireInterface2020` 至 `WireInterface2026_0` 等一系列模块，每个对应不同年份版本的 CATIA Wire 内核，以确保对各版本 CATIA 文件的精确支持。

### 调度模块
| 模块 | 功能简介 |
|---|---|
| `DatasmithDispatcher` | 负责并行化处理大型 CAD 装配体的导入任务，管理子进程或线程。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告。 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | 使 Wire 翻译器在安装了 Alias 2027 的系统上也能工作。 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 将核心的 TechSoft CAD 内核更新至 2026.3 版本。 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新了 Datasmith CAD 缓存的版本格式。 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 提升了类型转换警告在 MSVC 和 Clang 编译器之间的可移植性。 |

### 维护评价

**活跃维护**。该插件作为 Epic 企业内容管线的核心组件，持续受到积极维护。从近期提交记录可见，团队定期更新底层的 CAD 内核库（TechSoft），适配最新的行业软件版本（如 Alias 2027），并修复跨平台编译问题。插件创建于 2019 年，已相当成熟稳定。由于 `EnabledByDefault=false`，它不会自动加载，适合有明确 CAD 导入需求的项目启用。**推荐在需要处理专业 CAD 数据的生产项目中使用。**

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter/Tests)