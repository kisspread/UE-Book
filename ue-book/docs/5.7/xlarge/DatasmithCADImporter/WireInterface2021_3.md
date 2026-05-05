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

DatasmithCADImporter 是 Unreal Engine Datasmith 生态系统中的核心企业级插件，专门用于将各种 CAD（计算机辅助设计）格式的文件导入到引擎中。它解决了工业设计、建筑和制造领域中，将复杂的参数化 CAD 模型（如 CATIA, NX, SolidWorks, Alias 等）转换为可用于实时渲染、虚拟现实和数字孪生应用的优化网格和材质数据的难题。

该插件并非一个单一的导入器，而是一个**模块化的工具集合**。它通过多个子模块（如 `DatasmithCADTranslator`, `DatasmithWireTranslator`, `DatasmithOpenNurbsTranslator`）来支持不同的 CAD 文件格式和数据结构。其核心价值在于：
1.  **格式支持广泛**：通过集成 TechSoft 和 OpenNurbs 等第三方库，支持 `.wire` (Alias), `.3dm` (Rhino), `.step`, `.iges`, `.jt` 等数十种工业标准格式。
2.  **数据保真度高**：能够保留 CAD 模型的层级结构、元数据、材质定义和精确的几何信息（包括 NURBS 曲面）。
3.  **流程集成**：与 Datasmith 的整体工作流无缝集成，支持通过 Datasmith 导入器、Direct Link 或 Command Line 进行批量处理。

## 使用场景

-   **汽车设计**：将 Alias 或 CATIA 创建的汽车外观和内饰模型导入 UE，用于实时可视化评审和虚拟展示。
-   **建筑与施工 (AEC)**：导入 Revit 或其他 BIM 软件生成的 PLMXML 或 STEP 文件，创建建筑信息模型的数字孪生。
-   **工业设备与制造**：将 SolidWorks 或 NX 设计的机械零件和装配体导入，用于创建交互式维护手册或工厂仿真。
-   **产品设计与营销**：将 Rhino (`.3dm`) 或其他 CAD 软件设计的产品模型导入，制作高质量的产品配置器和营销动画。

## 蓝图用法

该插件主要作为运行时导入工具集，其核心功能通过 Datasmith 的标准导入流程（如 `UDatasmithStaticMeshImportOptions`）和命令行工具暴露，而非直接提供大量蓝图节点。主要的交互发生在编辑器导入对话框或自动化脚本中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| （无直接暴露的蓝图节点） | 该插件的功能主要通过编辑器菜单（文件 -> 导入）或 Datasmith 场景导入器触发。 | N/A |

### 使用示例（蓝图描述）

在蓝图中，通常不直接调用此插件的函数。相反，你会：
1.  在编辑器中，通过“文件”->“导入”菜单选择支持的 CAD 文件（如 `.wire`, `.3dm`, `.step`）。
2.  在弹出的 Datasmith 导入选项窗口中，配置导入选项（如几何体简化、材质处理等）。
3.  导入过程由 `DatasmithCADTranslator` 和相应的 `WireInterface` 或 `OpenNurbsTranslator` 模块在后台处理。
4.  对于自动化，可以使用 `UnrealEditor-Cmd.exe` 配合 `-run=Datasmith` 命令和相应的 `.udatasmith` 场景描述文件来批量导入 CAD 数据。

## C++ 用法

### 头文件引入

```cpp
// 引入 WireInterface 模块接口
#include "WireInterfaceModule.h"
```

### 基本用法

以下示例展示了如何检查 WireInterface 模块是否可用并获取其临时目录，这在开发自定义导入流程时可能用到。
（来源：`Engine/Plugins/Enterprise/DatasmithCADImporter/Source/WireInterface/Public/WireInterfaceModule.h`）

```cpp
#include "WireInterfaceModule.h"

void CheckWireInterfaceAvailability()
{
    // 检查模块是否已加载
    if (UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FDatasmithWireTranslatorModule::IsAvailable())
    {
        // 获取模块实例
        UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FDatasmithWireTranslatorModule& WireModule = 
            UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FDatasmithWireTranslatorModule::Get();
        
        // 获取用于处理 .wire 文件的临时目录
        FString TempDirectory = WireModule.GetTempDir();
        UE_LOG(LogTemp, Log, TEXT("Wire Interface Temp Dir: %s"), *TempDirectory);
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Datasmith Wire Translator module is not available."));
    }
}
```

### 进阶用法

该插件的高级用法通常涉及直接使用其底层库（如 TechSoft 的 A3DSDK）或扩展 `DatasmithCADTranslator` 模块以支持新的自定义 CAD 格式。这需要深入理解 CAD 数据结构和 Datasmith 的翻译器架构，通常由插件开发者或需要深度集成的企业用户完成。

## Demo 示例

一个最小的 C++ 示例，展示如何在运行时检查 Datasmith CAD Importer 插件中 WireInterface 模块的状态。

**MyCADHelper.h**
```cpp
#pragma once

#include "CoreMinimal.h"

class FMyCADHelper
{
public:
    static void LogWireInterfaceStatus();
};
```

**MyCADHelper.cpp**
```cpp
#include "MyCADHelper.h"
#include "WireInterfaceModule.h"

void FMyCADHelper::LogWireInterfaceStatus()
{
    // 使用宏来获取模块名，确保与编译时的模块名一致
    const FName ModuleName(PREPROCESSOR_TO_STRING(UE_DATASMITHWIRETRANSLATOR_MODULE_NAME));
    
    if (FModuleManager::Get().IsModuleLoaded(ModuleName))
    {
        UE_LOG(LogTemp, Display, TEXT("Module '%s' is loaded."), *ModuleName.ToString());
        
        // 安全地获取模块实例并调用方法
        auto* Module = FModuleManager::GetModulePtr<UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FDatasmithWireTranslatorModule>(ModuleName);
        if (Module)
        {
            FString TempDir = Module->GetTempDir();
            UE_LOG(LogTemp, Display, TEXT("Temp directory for .wire processing: %s"), *TempDir);
        }
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Module '%s' is not loaded. CAD Wire import functionality may be unavailable."), *ModuleName.ToString());
    }
}
```

## 模块依赖

该插件依赖于多个特殊的第三方库和 Datasmith 核心模块。要在你的项目或插件中使用其功能，需要在 `.Build.cs` 文件中添加相应依赖。

| 模块 | 用途 |
|---|---|
| `TechSoft` | 提供对多种 CAD 格式（如 STEP, IGES, JT, CATIA V4/V5, NX, SolidWorks 等）的读取支持。 |
| `OpenNurbs6` | 提供对 Rhino 3DM 文件格式的读取支持。 |
| `DatasmithCore` | Datasmith 的核心运行时库，提供场景、网格、材质等基础数据结构。 |
| `DatasmithTranslator` | Datasmith 翻译器框架，用于实现自定义文件格式的导入。 |

## 维护状态

### 近期更新

```
- 90f00dd86ae6 Added support for Alias 2026.0
- 39994edb437c [Wire] Corrected missing incrementation The mesh was properly sectioned but the missing increment was assigning the same material to each section Somehow the increment step was deleted before submission :-(
- 61d36ec7677f [Wire] Fixed missing colors when using group option - Fixed coding error in FDatasmithStaticMeshImporter::SetupStaticMesh which was eliminating sections when some were sharing the same material - Simplified material assignment to MeshElement's slots. - removed redundant material assignment on MeshActor. - Fixed wrong material slot name used in FMeshDescription. It has to be an integer to work in Datasmith import.
```

### 维护评价

**积极维护中**。该插件作为 Epic Games 官方支持的企业级功能，保持着稳定的更新节奏。
-   **活跃度**：最近的提交（支持 Alias 2026.0）表明插件仍在积极跟进主流 CAD 软件的版本更新。
-   **问题修复**：近期的提交修复了材质分配和颜色显示等关键导入问题，说明团队在持续改进导入质量和稳定性。
-   **推荐度**：对于需要将工业 CAD 数据引入 Unreal Engine 的企业用户和开发者，**强烈推荐使用**。它是目前 UE 中处理复杂 CAD 数据最专业、最全面的解决方案。请注意，该插件默认未启用，需要在插件管理器中手动开启。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithCADImporter)
-   [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithCADImporter/Tests) (如果存在)