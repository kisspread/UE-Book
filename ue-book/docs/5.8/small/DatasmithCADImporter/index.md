# Datasmith CAD Importer

> Collection of tools to work with CAD files.

| 属性 | 值 |
|---|---|
| 中文名 | CAD 工具导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CADInterfaces` (Runtime), `CADKernelSurface` (Runtime), `CADLibrary` (Runtime), `CADTools` (Runtime), `DatasmithCADTranslator` (Runtime), `DatasmithDispatcher` (Runtime), `DatasmithOpenNurbsTranslator` (Runtime), `DatasmithPLMXMLTranslator` (Runtime), `DatasmithWireTranslator` (Runtime), `ParametricSurface` (Runtime), `ParametricSurfaceExtension` (Runtime), `WireInterface2020` ~ `WireInterface2026_0` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 🆕（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

## 用途

本插件是 Datasmith 生态系统中专门处理 **CAD 工业格式**（如 STEP、IGES、JT、Parasolid、Rhino、3DXML 等）的导入管线。它解决了 CAD 文件（包含参数化曲面、精确几何体、B-Rep 拓扑结构）转换为 UE 可渲染网格的核心问题。与通用 3D 格式（FBX、OBJ）不同，CAD 文件包含数学精确的曲面定义，本插件负责将这些精确几何体进行曲面细分（tessellation），生成适用于实时渲染的三角形网格，同时保留 CAD 层级结构和元数据。

本插件**默认不启用**，需要在编辑器中手动启用或通过项目配置启用。

## 模块列表

| 模块 | 说明 |
|---|---|
| **CADInterfaces** | 与第三方 CAD 内核（TechSoft 等）的接口层，封装底层 CAD 读取能力 |
| **CADLibrary** | CAD 数据处理公共库，定义通用 CAD 数据结构和工具函数 |
| **CADTools** | CAD 工具集，提供高层 CAD 操作封装 |
| **CADKernelSurface** | 基于 CADKernel 的参数化曲面细分（tessellation）引擎 |
| **ParametricSurface** | 参数化曲面处理核心，负责 B-Rep 曲面到网格的转换 |
| **ParametricSurfaceExtension** | ParametricSurface 的扩展功能模块 |
| **DatasmithCADTranslator** | CAD 格式的 Datasmith 翻译器，主入口模块，协调整个 CAD 导入流程 |
| **DatasmithDispatcher** | 导入任务调度器，管理多进程/多线程的 CAD 文件解析分发 |
| **DatasmithOpenNurbsTranslator** | OpenNurbs（.3dm Rhino 文件）专用翻译器 |
| **DatasmithPLMXMLTranslator** | PLMXML 格式专用翻译器（用于 PLM 系统数据交换） |
| **DatasmithWireTranslator** | Wire 文件格式翻译器（Alias 工业设计软件专用） |
| **WireInterface2020 ~ WireInterface2026_0** | Alias Wire 格式不同年份版本的接口模块，各版本独立以支持不同年代的 Alias 文件 |

## 架构概览

```
用户操作（导入 CAD 文件）
        │
        ▼
DatasmithCADTranslator  ← 主翻译器入口
        │
        ├── DatasmithDispatcher  ← 任务分发（多进程）
        │
        ├── CADInterfaces  ← 第三方内核接口（TechSoft）
        │       │
        │       └── WireInterface20xx  ← Alias Wire 版本适配
        │
        ├── CADLibrary / CADTools  ← 公共数据结构与工具
        │
        ├── ParametricSurface / CADKernelSurface  ← 曲面细分引擎
        │
        └── 翻译器集合
            ├── DatasmithOpenNurbsTranslator  ← .3dm
            ├── DatasmithPLMXMLTranslator     ← PLMXML
            └── DatasmithWireTranslator       ← Wire
```

## 使用场景

- 你正在做**建筑可视化**（ArchViz），需要导入 Revit 导出的 CAD 资产 → 使用 DatasmithCADImporter 配合 Datasmith
- 你正在做**工业产品可视化**，需要导入 STEP/IGES/JT 等 CAD 格式的机械零件 → 本插件直接处理
- 你使用 **Alias（Autodesk）** 做汽车/A 级曲面设计，需要导入 .wire 文件 → 通过 WireInterface 模块链
- 你使用 **Rhino** 进行建筑设计/工业设计，需要导入 .3dm 文件 → 通过 OpenNurbs 翻译器
- 你从 **PLM 系统**（如 Teamcenter、Windchill）导出 PLMXML 数据 → 通过 PLMXML 翻译器
- 你需要在**生产线/自动化流程**中批量导入 CAD 文件 → 通过 DatasmithDispatcher 调度多进程并行处理

## 模块依赖

| 模块 | 用途 |
|---|---|
| `TechSoft` | TechSoft 内核接口，用于解析 STEP/IGES/JT/Parasolid 等 CAD 格式（第三方商业库） |
| `OpenNurbs6` | OpenNurbs 库，用于解析 Rhino .3dm 文件 |
| `DatasmithContent` | Datasmith 核心内容模块，提供 Datasmith 资产基础结构 |
| `DatasmithCore` | Datasmith 核心框架 |

> 注：TechSoft 和 OpenNurbs 为 CAD 专业格式解析的关键依赖，所有常见 Core/Engine/Slate 等标准依赖已省略。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 截断为 float 的编译警告 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | 支持已安装 Alias 2027 时 Wire 翻译器仍可正常工作 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 升级 TechSoft 内核到 2026.3 版本 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新 DatasmithCAD 缓存版本 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 增强类型转换警告在 MSVC 和 Clang 间的兼容性 |

### 维护评价

本插件处于**活跃维护**状态。最近提交集中在 2026 年 5 月，包含第三方库升级（TechSoft 2026.3）、编译警告修复和新版本兼容性适配（Alias 2027）。WireInterface 模块链持续随 Alias 年度版本更新（已覆盖至 2026 版），表明 Epic 与 Autodesk 保持同步维护。作为 Datasmith 企业级工具链的核心组件，该插件在工业/建筑可视化领域具有重要地位，推荐有 CAD 导入需求的项目使用。注意：**默认未启用**，需手动启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [子模块文档](CADInterfaces.md)、[CADKernelSurface](CADKernelSurface.md)、[CADLibrary](CADLibrary.md)、[CADTools](CADTools.md)、[DatasmithCADTranslator](DatasmithCADTranslator.md)、[DatasmithDispatcher](DatasmithDispatcher.md)、[DatasmithOpenNurbsTranslator](DatasmithOpenNurbsTranslator.md)、[DatasmithPLMXMLTranslator](DatasmithPLMXMLTranslator.md)、[DatasmithWireTranslator](DatasmithWireTranslator.md)、[ParametricSurface](ParametricSurface.md)、[ParametricSurfaceExtension](ParametricSurfaceExtension.md)