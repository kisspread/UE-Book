# Datasmith CAD Importer

> Collection of tools to work with CAD files.

| 属性 | 值 |
|---|---|
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CADInterfaces` (Runtime), `CADKernelSurface` (Runtime), `CADLibrary` (Runtime), `CADTools` (Runtime), `DatasmithCADTranslator` (Runtime), `DatasmithDispatcher` (Runtime), `DatasmithOpenNurbsTranslator` (Runtime), `DatasmithPLMXMLTranslator` (Runtime), `DatasmithWireTranslator` (Runtime), `ParametricSurface` (Runtime), `ParametricSurfaceExtension` (Runtime), `WireInterface2020` (Runtime), `WireInterface2021_3` (Runtime), `WireInterface2022` (Runtime), `WireInterface2022_1` (Runtime), `WireInterface2022_2` (Runtime), `WireInterface2023_0` (Runtime), `WireInterface2023_1` (Runtime), `WireInterface2024_1` (Runtime), `WireInterface2025_0` (Runtime), `WireInterface2026_0` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

## 用途

Datasmith CAD Importer 是一个企业级插件，其核心功能是**将多种专业 CAD（计算机辅助设计）格式的文件导入到 Unreal Engine 中**。它并非一个简单的文件加载器，而是一个复杂的转换管道，能够解析 CAD 软件（如 Alias、Rhino、CATIA 等）生成的精确几何体、层级结构、材质和元数据，并将其转换为 UE 可用的网格体（Mesh）、材质和场景图。

该插件解决了工业设计、汽车设计、建筑可视化等领域中，将高精度、参数化的 CAD 模型无缝引入实时渲染环境的关键问题。它通过 Datasmith 框架工作，支持增量更新和数据优化，是连接专业 CAD 软件与 UE 实时 3D 体验的核心桥梁。

## 使用场景

- **汽车设计评审**：将 Alias 或 CATIA 中的整车模型导入 UE，用于虚拟评审、材质配置和灯光渲染。
- **工业产品可视化**：将 SolidWorks 或 Rhino 中的产品模型导入 UE，创建交互式产品配置器或营销动画。
- **建筑信息模型 (BIM) 可视化**：将 PLMXML 等格式的建筑或工厂模型导入 UE，进行施工模拟或运营维护培训。
- **需要保留 CAD 数据层级与元数据**：当您不仅需要几何体，还需要保留原始 CAD 文件中的组件命名、层级关系和自定义属性时。

## 蓝图用法

该插件主要作为 Datasmith 导入流程的后端运行时模块，其核心功能通过 Datasmith 导入器（如 `.udatasmith` 文件或编辑器中的“导入”功能）自动调用，**不直接暴露公开的蓝图节点**。用户通过标准的 Datasmith 导入工作流使用此插件。

## C++ 用法

该插件的模块主要为内部运行时模块，为 Datasmith 翻译器提供底层支持。开发者通常不直接调用其 API，而是通过 Datasmith 框架进行交互。以下是模块内部的一些关键接口示例。

### 头文件引入

```cpp
#include "WireInterfaceModule.h"
```

### 基本用法

检查 Wire 翻译器模块是否可用并获取其临时目录。

```cpp
// 来源：Engine/Plugins/Enterprise/DatasmithCADImporter/Source/WireInterface/Public/WireInterfaceModule.h
using namespace UE_DATASMITHWIRETRANSLATOR_NAMESPACE;

// 检查模块是否已加载
if (FDatasmithWireTranslatorModule::IsAvailable())
{
    // 获取模块实例
    FDatasmithWireTranslatorModule& WireModule = FDatasmithWireTranslatorModule::Get();
    
    // 获取用于处理 .wire 文件的临时目录
    FString TempDirectory = WireModule.GetTempDir();
    UE_LOG(LogTemp, Log, TEXT("Wire Translator Temp Dir: %s"), *TempDirectory);
}
```

### 进阶用法

该插件的复杂性体现在其多模块协作上。`DatasmithCADTranslator` 模块作为主协调器，会根据文件类型（如 `.wire`, `.3dm`, `.plmxml`）调度对应的翻译器模块（如 `DatasmithWireTranslator`, `DatasmithOpenNurbsTranslator`, `DatasmithPLMXMLTranslator`）。这些翻译器模块进一步依赖 `CADInterfaces`、`CADLibrary`、`ParametricSurface` 等模块来完成几何体解析、曲面细分和材质转换。整个流程由 `DatasmithDispatcher` 进行任务分发和管理。

## Demo 示例

该插件作为 Datasmith 导入管线的一部分，没有独立的最小可运行示例。其使用完全集成在 UE 的编辑器导入流程中。要测试其功能，您需要：
1.  在插件设置中启用 `DatasmithCADImporter`。
2.  准备一个支持的 CAD 文件（例如，一个 `.wire` 文件）。
3.  在 UE 编辑器中，使用“文件” -> “导入”功能，或直接将文件拖入内容浏览器。
4.  在导入对话框中，选择 Datasmith 作为导入格式，插件将自动处理转换。

## 模块依赖

该插件依赖于一些特定的第三方库来处理不同的 CAD 格式。

| 模块 | 用途 |
|---|---|
| `TechSoft` | 用于解析和处理多种工业标准 CAD 格式（如 STEP, IGES, CATIA, NX 等）的核心库。 |
| `OpenNurbs6` | 用于解析 Rhino 3D 的 `.3dm` 文件格式的开源库。 |

其他模块主要依赖 UE 标准模块（Core, Engine, MeshDescription 等）以及 Datasmith 核心模块。

## 维护状态

### 近期更新

- 90f00dd86ae6 Added support for Alias 2026.0
  *解读：为最新的 Alias 2026.0 版本添加了支持，表明插件在跟进上游 CAD 软件的更新。*
- 39994edb437c [Wire] Corrected missing incrementation The mesh was properly sectioned but the missing increment was assigning the same material to each section Somehow the increment step was deleted before submission :-(
  *解读：修复了 .wire 文件导入时材质分配错误的 Bug，这是一个重要的功能修复。*
- 61d36ec7677f [Wire] Fixed missing colors when using group option - Fixed coding error in FDatasmithStaticMeshImporter::SetupStaticMesh which was eliminating sections when some were sharing the same material - Simplified material assignment to MeshElement's slots. - removed redundant material assignment on MeshActor. - Fixed wrong material slot name used in FMeshDescription. It has to be an integer to work in Datasmith import.
  *解读：一系列针对 .wire 文件导入的材质和颜色修复，优化了材质分配逻辑，提升了导入结果的准确性。*

### 维护评价

该插件**仍在积极维护中**。从近期提交记录看，维护活动集中在：
1.  **跟进上游 CAD 软件版本**（如添加 Alias 2026.0 支持）。
2.  **修复关键的导入 Bug**，特别是材质和颜色相关的错误。
3.  **优化内部逻辑**。

插件创建于约 6 年前，作为企业级 Datasmith 套件的核心部分，其稳定性和持续更新对于依赖 CAD 数据工作流的用户至关重要。目前没有迹象表明它被废弃。**推荐在需要导入专业 CAD 文件的项目中使用。**

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithCADImporter/Tests)