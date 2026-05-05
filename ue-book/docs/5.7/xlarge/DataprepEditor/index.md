# Dataprep Editor

> A tool to simplify creation and execution of data preparation pipelines from within the Unreal Editor.

| 属性 | 值 |
|---|---|
| 分类 | Dataprep |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、预设） |
| 模块 | `DataprepCore` (Runtime), `DataprepEditor` (Runtime), `DataprepEditorScriptingUtilities` (Runtime), `DataprepLibraries` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-11-22 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DataprepEditor) | |

## 用途

Dataprep Editor 是一个企业级数据准备工具，旨在简化从外部数据源（如 CAD、BIM、点云等）导入资产到 Unreal Engine 的流程。它提供了一个可视化的、基于节点的编辑器，允许用户创建可重复使用的数据准备管道（Pipeline）。这些管道可以对导入的原始数据进行一系列自动化操作，例如清理、优化、转换和组织，从而将复杂、冗余的原始数据转化为适合游戏引擎使用的干净、高效的资产。其核心价值在于将繁琐的手动数据处理流程自动化、标准化，特别适用于建筑可视化、工业仿真、数字孪生等需要处理大量企业数据的领域。

## 使用场景

- **建筑可视化**：从 Revit、SketchUp 等软件导入复杂的建筑模型后，使用 Dataprep 管道自动合并网格、简化几何体、生成 LOD、设置材质和碰撞体。
- **工业仿真与数字孪生**：处理从 CAD 软件（如 CATIA, NX）导入的精密机械模型，自动移除内部不可见结构、优化面数、分配物理资产。
- **大型场景组装**：批量处理从不同来源（如 GIS 数据、点云扫描）导入的资产，统一坐标系、比例尺，并进行场景组织和优化。
- **资产标准化**：为团队建立统一的数据导入和预处理标准，确保所有导入的资产都符合项目的性能和质量要求。

## 模块列表与总结

本插件由四个核心模块组成，共同构建了完整的数据准备功能：

| 模块 | 一句话总结 | 详细文档 |
|---|---|---|
| **DataprepCore** | 核心运行时模块，定义了数据准备管道、操作（Action）和选择器（Selector）的基础框架与数据结构。 | [DataprepCore.md](DataprepCore.md) |
| **DataprepEditor** | 编辑器模块，提供了可视化的节点图编辑器界面，用于创建、编辑和执行数据准备管道。 | [DataprepEditor.md](DataprepEditor.md) |
| **DataprepEditorScriptingUtilities** | 脚本工具模块，提供了蓝图和 Python 脚本接口，用于以编程方式控制数据准备流程。 | [DataprepEditorScriptingUtilities.md](DataprepEditorScriptingUtilities.md) |
| **DataprepLibraries** | 操作库模块，包含了一系列预置的、常用的数据准备操作（如网格合并、LOD 生成、材质设置等）。 | [DataprepLibraries.md](DataprepLibraries.md) |

## 蓝图用法

本插件的核心功能主要通过其专用的编辑器界面（节点图）使用。对于希望通过蓝图或脚本进行自动化控制的高级用户，主要的蓝图接口位于 `DataprepEditorScriptingUtilities` 模块中。

详细的蓝图节点和用法，请参阅 [DataprepEditorScriptingUtilities.md](DataprepEditorScriptingUtilities.md)。

## C++ 用法

C++ 开发者可以扩展 Dataprep 的功能，例如创建自定义的数据准备操作（Action）或选择器（Selector）。核心的基类和接口定义在 `DataprepCore` 模块中。

详细的 C++ API 和扩展方法，请参阅 [DataprepCore.md](DataprepCore.md)。

## Demo 示例

由于本插件规模庞大且功能复杂，完整的使用示例请参考各子模块文档中的代码片段和说明。一个典型的使用流程是：
1.  在编辑器中启用 `DataprepEditor` 插件。
2.  通过内容浏览器右键菜单创建新的 `Dataprep Asset`。
3.  双击打开资产，进入节点图编辑器。
4.  从 `DataprepLibraries` 中拖拽操作节点（如 `Merge Meshes`, `Set Material`）并连接它们，构建处理流程。
5.  执行管道，查看处理后的资产。

## 模块依赖

要使用或扩展此插件，你的模块可能需要依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `DataprepCore` | 访问数据准备管道的核心数据结构和基类。 |
| `DataprepLibraries` | 使用或引用预置的数据准备操作。 |
| `GeometryProcessing` | 用于网格处理相关的操作（如合并、简化）。 |
| `MeshDescription` | 用于底层网格数据的读写和处理。 |
| `MeshConversion` | 用于不同网格格式之间的转换。 |
| `ProceduralMeshComponent` | 可能用于动态生成或修改网格。 |

## 维护状态

### 近期更新
（基于提供的创建时间信息推断，具体 commit 需在源码仓库中查询）
- 创建于 2019-11-22，属于较早期的企业功能插件。
- 作为 Epic 官方维护的企业级工具，通常会跟随引擎版本进行兼容性更新。
- 由于其功能相对独立且成熟，可能不会像核心引擎模块那样频繁更新。

### 维护评价
- **年龄**：插件已存在约5年，属于成熟功能。
- **活跃度**：作为企业版功能，其更新可能主要集中在引擎大版本的兼容性维护和关键问题修复上，而非频繁的功能迭代。
- **状态**：**维护中**。虽然更新可能不频繁，但作为官方支持的企业功能，预计会持续维护以确保在新版引擎中可用。
- **推荐度**：**推荐使用**。对于有大量企业数据导入和处理需求的项目，这是官方提供的最专业、最集成的解决方案。对于小型项目或简单导入需求，可能显得过于复杂。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DataprepEditor)
- [官方文档]() (待补充，通常可在 Unreal Engine 官方文档的企业功能部分找到)
- [测试用例]() (待补充，可在源码仓库的 `Tests` 目录下查找)