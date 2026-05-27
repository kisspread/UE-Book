# Datasmith FBX Importer

> Adds support for importing content from DeltaGen and VRED into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | 数据导入-FBX |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DatasmithVREDTranslator` (Editor), `DatasmithDeltaGenTranslator` (Editor), `DatasmithFBXTranslator` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 🆕（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithFBXImporter) | |

## 用途

此插件是 **Datasmith 生态系统**的一部分，专门用于将特定的工业设计软件（**DeltaGen** 和 **VRED**）的场景和资产导入到 Unreal Engine 中。它解决的核心问题是：这些专业的可视化软件使用了复杂的 FBX 格式变体，标准的 FBX 导入器无法正确处理其高级材质、光照和场景层次结构。DatasmithFBXImporter 提供了专门的翻译器，能够解析这些特定格式，并将其转换为 Unreal Engine 可用的资产（如 Mesh、材质、光照和场景层级），是汽车、产品可视化和建筑可视化等行业工作流的关键环节。

## 使用场景

- 你在 **汽车设计** 或 **产品可视化** 领域工作，需要将使用 **DeltaGen** 或 **VRED** 制作的复杂渲染场景导入到 Unreal Engine 中进行实时渲染、虚拟评审或创建营销内容。
- 你正在使用 **Datasmith 工作流**，并且需要处理来自上述特定软件的资产，而标准的 `.fbx` 或 `.udatasmith` 导入器无法满足需求。
- 你需要保留原始设计软件中定义的**高级材质属性**、**精确的场景层级**和**光照设置**，以实现尽可能接近源软件的视觉效果。

## 模块列表

| 模块 | 功能简述 |
|---|---|
| `DatasmithDeltaGenTranslator` | 负责解析和导入来自 **DeltaGen** 软件的 FBX 格式文件。 |
| `DatasmithVREDTranslator` | 负责解析和导入来自 **VRED** 软件的 FBX 格式文件。 |
| `DatasmithFBXTranslator` | 提供基础的 FBX 格式解析和场景构建功能，作为 DeltaGen 和 VRED 翻译器的底层支撑。 |

## 使用场景示例

1.  **在编辑器中导入**：
    - 启用插件（`Plugins` 窗口中搜索并启用 `Datasmith FBX Importer`）。
    - 通过 `File -> Import Into Level` 或 Content Browser 的 `Import` 按钮。
    - 选择从 DeltaGen 或 VRED 导出的 `.fbx` 文件。
    - 导入器会自动识别文件类型，并使用对应的翻译器进行处理。

2.  **自动材质和场景构建**：
    - 导入后，插件会尝试重建原始软件中的材质层次结构。
    - 场景中的对象（如汽车模型、装配体）会保留其父子层级关系。
    - 标准的 FBX 属性（如网格、法线、UV）和 DeltaGen/VRED 特有的属性会被正确转换。

## 模块依赖

此插件依赖于核心的 Datasmith 模块，无其他特殊依赖。

| 模块 | 用途 |
|---|---|
| `DatasmithImporter` | 提供基础的 Datasmith 导入框架和核心功能。 |
| `DatasmithContent` | 提供 Datasmith 导入后生成的资产类型定义（如 `DatasmithScene`）。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了严格浮点模式下，double 常量截断为 float 产生的警告。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移到 UE_LOGF 新格式。 |
| 2026-02-03 | `88ba268b` | Fix unreachable code errors | 修复了代码中不可达的错误。 |
| 2025-03-13 | `b059f7b4` | Fix trivial unreachable code warnings. | 修复了微不足道的不可达代码警告。 |
| 2024-10-02 | `0a14cf0e` | Update VRED python exporter to support API changes in VRED | 更新了 VRED 的 Python 导出器以支持 VRED 的 API 变更。 |

### 维护评价

**维护状态：活跃维护中。**

- **创建时间**：约 7 年前（2019年），属于企业级插件，生命周期较长。
- **更新频率**：从近期提交记录看，插件仍在积极维护，最近的更新在 2026 年。更新内容以代码质量改进（修复警告、错误）和适配上游软件（VRED）的API变化为主，表明它仍在跟随最新的开发环境和目标软件进行维护。
- **推荐使用**：**推荐使用**。如果你的生产工作流依赖于从 DeltaGen 或 VRED 导入资产，此插件是官方提供的标准解决方案，且维护状态良好。需要注意的是，它默认不启用（`EnabledByDefault: false`），需要在项目设置或插件列表中手动开启。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithFBXImporter)
- [Datasmith 官方文档](https://docs.unrealengine.com/5.8/en-US/datasmith-plugins-in-unreal-engine/) (包含此插件的上下文)
- 子模块文档：[DatasmithDeltaGenTranslator.md](DatasmithDeltaGenTranslator.md), [DatasmithFBXTranslator.md](DatasmithFBXTranslator.md), [DatasmithVREDTranslator.md](DatasmithVREDTranslator.md)