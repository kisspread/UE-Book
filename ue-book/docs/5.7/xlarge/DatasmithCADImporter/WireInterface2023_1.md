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

Datasmith CAD Importer 是一个企业级插件，其核心功能是将各种专业的计算机辅助设计（CAD）文件格式（如 `.wire` (Alias), `.3dm` (Rhino), `.plmxml` 等）转换为 Unreal Engine 可以理解和使用的资产（如静态网格体、材质）。它解决了工程设计、工业设计、汽车设计等领域与游戏引擎之间的数据互通问题，允许设计师和工程师将高精度的 CAD 模型直接导入 UE 进行可视化、交互式体验或虚拟样机评审，而无需通过中间格式（如 FBX）进行繁琐的转换和优化。

## 使用场景

- 你是一名汽车设计师，需要将 Autodesk Alias 创建的 `.wire` 曲面模型导入 UE 进行实时渲染和评审。
- 你是一名建筑师或工程师，需要将 Rhino 的 `.3dm` 文件或 PLMXML 数据导入 UE 进行建筑信息模型（BIM）可视化或工厂布局模拟。
- 你需要在 UE 中创建一个基于真实 CAD 数据的数字孪生（Digital Twin）应用。
- 你的工作流程依赖于 Datasmith，并且需要处理来自专业 CAD 软件的原始数据。

## 蓝图用法

该插件主要作为数据导入的底层翻译器，其核心功能通过 Datasmith 的导入流程触发，而非提供大量直接的蓝图节点。用户通常通过编辑器中的“导入”按钮或 Datasmith 导入器来使用它。插件本身提供的蓝图接口有限，主要集中在模块状态查询上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IsAvailable` | 检查特定版本的 WireInterface 模块是否已加载。 | `FDatasmithWireTranslatorModule` |

### 使用示例（蓝图描述）

在蓝图中，你可以通过调用 `FDatasmithWireTranslatorModule::IsAvailable()` 的静态方法（需要通过 C++ 暴露或使用模块加载节点）来检查当前环境是否支持特定版本的 Alias `.wire` 文件导入。这通常用于在导入前进行环境检查。

## C++ 用法

该插件的 C++ 用法主要涉及模块的加载、检查以及与 Datasmith 导入管线的集成。对于大多数用户，直接使用 C++ API 的场景不多，更多是作为 Datasmith 框架的一部分被调用。

### 头文件引入

```cpp
#include "WireInterfaceModule.h"
```

### 基本用法

检查并获取 WireInterface 模块实例。
（来源：`Engine/Plugins/Enterprise/DatasmithCADImporter/Source/WireInterface/Public/WireInterfaceModule.h`）

```cpp
// 检查模块是否可用
if (UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FDatasmithWireTranslatorModule::IsAvailable())
{
    // 获取模块实例
    UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FDatasmithWireTranslatorModule& WireModule = 
        UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FDatasmithWireTranslatorModule::Get();
    
    // 获取模块使用的临时目录路径
    FString TempDir = WireModule.GetTempDir();
    UE_LOG(LogTemp, Log, TEXT("Wire Translator Temp Dir: %s"), *TempDir);
}
else
{
    UE_LOG(LogTemp, Warning, TEXT("Wire Translator module is not loaded."));
}
```

### 进阶用法

该插件的进阶用法通常涉及扩展或自定义 CAD 导入流程。这需要深入理解 `DatasmithCADTranslator`、`CADLibrary` 等核心模块的接口，并可能涉及实现自定义的 `IDatasmithTranslator`。由于其复杂性，通常建议参考引擎源码中现有的翻译器实现（如 `DatasmithOpenNurbsTranslator`）。

## Demo 示例

以下示例展示了如何在 C++ 中检查 WireInterface 模块的状态并获取其临时目录。

**MyCADImporterHelper.h**
```cpp
#pragma once

#include "CoreMinimal.h"

class FMyCADImporterHelper
{
public:
    static bool CheckWireInterfaceSupport();
    static FString GetWireInterfaceTempPath();
};
```

**MyCADImporterHelper.cpp**
```cpp
#include "MyCADImporterHelper.h"
#include "WireInterfaceModule.h"

bool FMyCADImporterHelper::CheckWireInterfaceSupport()
{
    return UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FDatasmithWireTranslatorModule::IsAvailable();
}

FString FMyCADImporterHelper::GetWireInterfaceTempPath()
{
    if (CheckWireInterfaceSupport())
    {
        return UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FDatasmithWireTranslatorModule::Get().GetTempDir();
    }
    return FString();
}
```

## 模块依赖

该插件依赖于一些特定的第三方库来解析不同的 CAD 格式。

| 模块 | 用途 |
|---|---|
| `TechSoft` | 用于读取和解析多种 CAD 格式（如 STEP, IGES, CATIA 等）的核心库。 |
| `OpenNurbs6` | 用于读取和解析 Rhino 的 `.3dm` 文件格式。 |

## 维护状态

### 近期更新

```
- 90f00dd86ae6 Added support for Alias 2026.0
  *解读：为最新的 Alias 2026.0 版本添加了支持，表明插件在积极跟进上游 CAD 软件的更新。*
- 39994edb437c [Wire] Corrected missing incrementation The mesh was properly sectioned but the missing increment was assigning the same material to each section Somehow the increment step was deleted before submission :-(
  *解读：修复了材质分配逻辑中的一个错误，该错误导致网格体的不同部分被错误地分配了相同的材质。*
- 61d36ec7677f [Wire] Fixed missing colors when using group option - Fixed coding error in FDatasmithStaticMeshImporter::SetupStaticMesh which was eliminating sections when some were sharing the same material - Simplified material assignment to MeshElement's slots. - removed redundant material assignment on MeshActor. - Fixed wrong material slot name used in FMeshDescription. It has to be an integer to work in Datasmith import.
  *解读：修复了使用分组选项时颜色丢失的问题，并优化了材质分配和网格体导入的逻辑，修复了多个相关的编码错误。*
```

### 维护评价

该插件处于**活跃维护**状态。从近期提交记录可以看出，开发团队不仅在修复已知的 Bug（如材质分配、颜色丢失），还在持续添加对新版本 CAD 软件（Alias 2026.0）的支持。作为 Epic Games 官方维护的企业级插件，其稳定性和兼容性有保障。**推荐使用**，特别是对于有专业 CAD 数据导入需求的项目。需要注意的是，该插件默认是禁用的（`EnabledByDefault: false`），需要在项目设置中手动启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)