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

Datasmith CAD Importer 是一个企业级插件，其核心功能是为 Unreal Engine 提供对多种专业 CAD（计算机辅助设计）文件格式的原生导入支持。它解决了工业设计、建筑、工程和制造（AEC & MFG）领域用户将复杂的 CAD 模型（如来自 CATIA, NX, SolidWorks, Alias 等软件）无缝引入 UE5 进行可视化、实时交互或数字孪生构建的难题。该插件并非简单的网格导入器，它能够解析 CAD 文件中的精确几何体（B-Rep）、层级结构、元数据、材质和装配关系，并将其转换为 UE5 可用的资产。

## 使用场景

- 你是一名汽车设计师，需要将 Alias 或 CATIA 创建的汽车油泥模型导入 UE5 进行实时渲染和评审。
- 你是一名建筑师或工程师，需要将 Revit 或 SolidWorks 生成的建筑或机械装配体导入 UE5 制作交互式演示或 VR 体验。
- 你正在构建一个工业数字孪生项目，需要将来自 PLM 系统（如 Teamcenter）的 PLMXML 格式的产品数据精确导入 UE5。
- 你需要导入 Rhino 3D 的 .3dm 文件（通过 OpenNurbs 支持）进行可视化。

## 蓝图用法

该插件主要作为 Datasmith 导入流程的后端翻译器工作，其核心功能通过 Datasmith 导入器（如 `.udatasmith` 文件或直接导入 CAD 文件）触发，而非提供大量直接的蓝图节点。用户通常在编辑器中通过“导入”操作或使用 `DatasmithScene` 资产来使用它。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FDatasmithWireTranslatorModule::Get()` | 获取 Wire 翻译器模块的单例引用，用于内部管理。 | `FDatasmithWireTranslatorModule` |
| `FDatasmithWireTranslatorModule::IsAvailable()` | 检查 Wire 翻译器模块是否已加载。 | `FDatasmithWireTranslatorModule` |

### 使用示例（蓝图描述）

在蓝图中，你通常不会直接调用此插件的函数。标准工作流是：
1.  在内容浏览器中右键，选择“导入到 /Game/...”。
2.  在文件选择对话框中，选择支持的 CAD 文件（如 `.catpart`, `.sldprt`, `.wire`, `.3dm` 等）。
3.  UE5 会自动调用 Datasmith CAD Importer 插件进行翻译和导入。
4.  导入完成后，生成 `.udatasmith` 资产和相关的静态网格体、材质等。

## C++ 用法

### 头文件引入

```cpp
// 引入 Wire 翻译器模块接口
#include "WireInterfaceModule.h"
```

### 基本用法

该插件的模块通常作为 Datasmith 翻译器框架的一部分被自动加载和调用。开发者主要与 `DatasmithCADTranslator` 模块交互，后者负责调度具体的格式翻译器（如 `WireInterface2026_0`）。

```cpp
// 检查特定版本的 Wire 翻译器是否可用（示例）
// 来源：基于 WireInterfaceModule.h 的推断用法
if (UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FDatasmithWireTranslatorModule::IsAvailable())
{
    UE_LOG(LogTemp, Log, TEXT("Datasmith Wire Translator module is loaded."));
    // 通常不需要直接调用其方法，导入流程会自动使用。
}
```

### 进阶用法

对于需要深度集成或扩展 CAD 导入流程的开发者，可以研究 `CADTools` 和 `DatasmithCADTranslator` 模块。这些模块定义了翻译器接口和几何处理工具。例如，你可以实现自定义的 `IDatasmithTranslator` 来支持新的 CAD 格式。

## Demo 示例

以下示例展示了如何在 C++ 中检查并引用 Wire 翻译器模块。请注意，实际的 CAD 文件导入通常由编辑器或 Datasmith 系统驱动。

```cpp
// MyCADImporterHelper.h
#pragma once

#include "CoreMinimal.h"

class FMyCADImporterHelper
{
public:
    static void CheckWireTranslatorStatus();
};
```

```cpp
// MyCADImporterHelper.cpp
#include "MyCADImporterHelper.h"
#include "WireInterfaceModule.h" // 引入 Wire 翻译器模块头文件

void FMyCADImporterHelper::CheckWireTranslatorStatus()
{
    // 使用模块提供的静态方法检查可用性
    if (UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FDatasmithWireTranslatorModule::IsAvailable())
    {
        UE_LOG(LogTemp, Display, TEXT("Datasmith Wire Translator (for Alias) is ready."));
        // 可以获取模块实例，但通常无需直接操作
        auto& WireModule = UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FDatasmithWireTranslatorModule::Get();
        FString TempDir = WireModule.GetTempDir();
        UE_LOG(LogTemp, Display, TEXT("Wire Translator Temp Directory: %s"), *TempDir);
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Datasmith Wire Translator module is not loaded. Ensure the plugin is enabled."));
    }
}
```

## 模块依赖

该插件的模块依赖较为复杂，且包含多个版本特定的 WireInterface 模块。以下是其**独特**的依赖项：

| 模块 | 用途 |
|---|---|
| `TechSoft` | 提供对多种 CAD 格式（如 CATIA, NX, SolidWorks, STEP, IGES）的核心读取和转换能力。 |
| `OpenNurbs6` | 用于读取和解析 Rhino 3D 的 `.3dm` 文件格式。 |
| `DatasmithCore` | Datasmith 的核心框架，提供场景、资产和翻译器的基础接口。 |
| `DatasmithContent` | 提供 Datasmith 特有的资产类型和蓝图功能。 |

## 维护状态

### 近期更新

```
- 90f00dd86ae6 Added support for Alias 2026.0
  （解读：为最新的 Alias 2026.0 版本添加了文件格式支持，表明插件在跟进上游软件更新。）
- 39994edb437c [Wire] Corrected missing incrementation The mesh was properly sectioned but the missing increment was assigning the same material to each section Somehow the increment step was deleted before submission :-(
  （解读：修复了材质分配逻辑中的一个关键 Bug，该 Bug 导致网格体的不同部分被错误地赋予了相同材质。）
- 61d36ec7677f [Wire] Fixed missing colors when using group option - Fixed coding error in FDatasmithStaticMeshImporter::SetupStaticMesh which was eliminating sections when some were sharing the same material - Simplified material assignment to MeshElement's slots. - removed redundant material assignment on MeshActor. - Fixed wrong material slot name used in FMeshDescription. It has to be an integer to work in Datasmith import.
  （解读：一系列针对 Wire 格式导入的修复和优化，包括颜色丢失、材质槽分配错误等问题，提升了导入的稳定性和正确性。）
```

### 维护评价

该插件处于**活跃维护**状态。尽管创建于约6年前，但近期的提交记录（特别是针对 Alias 2026.0 的支持和多个 Bug 修复）表明 Epic Games 仍在持续更新它，以支持最新的 CAD 软件版本并修复问题。作为企业版 Datasmith 套件的核心组件，其重要性不言而喻。对于需要在 UE5 中处理专业 CAD 数据的用户，**强烈推荐使用**。需要注意的是，该插件默认未启用，用户需在插件列表中手动开启。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithCADImporter/Tests) (如果存在)