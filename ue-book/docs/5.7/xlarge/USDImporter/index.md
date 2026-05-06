# USD Importer

> Adds support for importing the USD file format into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | USD 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `GeometryCacheUSD` (Runtime), `USDClassesEditor` (Runtime), `USDExporter` (Runtime), `USDSchemas` (Runtime), `USDStage` (Runtime), `USDStageEditor` (Runtime), `USDStageEditorViewModels` (Runtime), `USDStageImporter` (Runtime), `USDTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-10-01 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Importers/USDImporter) | |

## 总体用途

USD Importer 是 Unreal Engine 中完整的 USD 工作流集成插件。它不仅仅提供导入功能，还涵盖了：

- **导入**：将 `.usd`、`.usda`、`.usdc` 等格式的 USD 场景、模型、动画、材质等资产导入到 UE 中。
- **导出**：将 UE 中的静态网格体、骨骼网格体、关卡序列、材质等导出为 USD 格式。
- **舞台编辑**：在编辑器中直接操作 USD 舞台（Stage），查看层级、属性、时间采样等。
- **Schema 支持**：解析 USD 标准 Schema（如 GeomMesh、SkelRoot、Material 等），并映射为 UE 原生表示。
- **Geometry Cache 集成**：支持 USD 中的动画缓存直接作为 Geometry Cache 资产使用。

该插件解决了美术和设计团队在跨工具（Maya、Houdini、Blender 等）协作中使用 USD 作为通用交换格式的需求，使 UE 能够无缝接入现代 DCC 工具流水线。

## 模块列表

| 模块 | 一句话说明 | 文档 |
|---|---|---|
| `GeometryCacheUSD` | 解析 USD 时序几何数据并生成 Geometry Cache 资产 | [GeometryCacheUSD.md](GeometryCacheUSD.md) |
| `USDClassesEditor` | 提供编辑器特有的 USD 资产类、工厂、上下文菜单 | [USDClassesEditor.md](USDClassesEditor.md) |
| `USDExporter` | 将 UE 场景/资产导出为 USD 格式 | [USDExporter.md](USDExporter.md) |
| `USDSchemas` | 定义 USD Schema 到 UE 数据结构的映射逻辑 | [USDSchemas.md](USDSchemas.md) |
| `USDStage` | 管理 USD 舞台的打开、关闭、层次的运行时核心 | [USDStage.md](USDStage.md) |
| `USDStageEditor` | 在编辑器中显示 USD 舞台内容的 UI 面板（场景大纲、属性窗口等） | [USDStageEditor.md](USDStageEditor.md) |
| `USDStageEditorViewModels` | 编辑器 UI 的视图模型层，处理数据绑定和交互逻辑 | [USDStageEditorViewModels.md](USDStageEditorViewModels.md) |
| `USDStageImporter` | 实现 USD 导入的主要逻辑，包括资产生成、材质烘焙、碰撞设置等 | [USDStageImporter.md](USDStageImporter.md) |
| `USDTests` | 自动化测试模块，覆盖导入、导出、Schema 解析等关键流程 | [USDTests.md](USDTests.md) |

## 使用场景

- **跨 DCC 工具流水线**：团队使用 Maya、Houdini、Blender 等工具，通过 USD 作为中间格式，在 UE 中查看和编辑最终效果。导入和导出功能保证双向数据流通。
- **大型场景参考**：将外部制作的巨大城市、自然环境以 USD 引用方式加载，UE 通过舞台管理按需流送。
- **程序化内容生成**：从 Houdini 导出 USD 动画缓存（如布料模拟、粒子），在 UE 中作为 Geometry Cache 直接使用。
- **资产版本管理**：利用 USD 的层（Layer）和变体（Variant）机制，在 UE 中切换不同 LOD、材质、动画片段。
- **可视化协作审查**：使用 USD 舞台编辑器查看完整场景层级，检查属性、时间范围，无需导入所有内容就能预览。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Importers/USDImporter)
- [官方文档（USD 集成）](https://docs.unrealengine.com/5.7/en-US/usd-integration-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Importers/USDImporter/Source/USDTests/Private)