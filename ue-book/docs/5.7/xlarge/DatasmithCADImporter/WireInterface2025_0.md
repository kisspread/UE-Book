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

DatasmithCADImporter 是 Unreal Engine Datasmith 框架的核心扩展，专门用于将复杂的 CAD（计算机辅助设计）文件导入到引擎中。它解决的核心问题是：将工业设计软件（如 Alias、Rhino、CATIA、NX 等）生成的高精度、参数化 CAD 模型，高效、准确地转换为 UE 可用的网格（Mesh）和材质数据。

该插件的存在是为了支持建筑、工程、施工（AEC）以及汽车、工业设计等领域的专业工作流。它不仅仅是简单的格式转换，还包含了一系列高级功能：
1.  **参数化曲面处理**：能够理解并转换 CAD 模型中的精确数学曲面（NURBS），在导入时进行曲面细分（Tessellation），以在精度和性能之间取得平衡。
2.  **网格优化与修复**：对导入的网格进行清理、修复和优化，以适应实时渲染的需求。
3.  **材质与元数据保留**：尽可能保留原始 CAD 文件中的材质定义、图层结构、元数据等信息。
4.  **多格式支持**：通过一系列专用的翻译器（Translator）模块，支持广泛的 CAD 文件格式，包括 `.wire` (Alias)、`.3dm` (Rhino)、`.plmxml`、`.step`、`.iges` 等。
5.  **分布式处理**：通过 `DatasmithDispatcher` 模块，支持将繁重的 CAD 转换任务分发到其他进程或机器上执行，避免阻塞编辑器主线程。

## 使用场景

-   **建筑可视化**：建筑师使用 Revit 或其他 CAD 软件创建建筑模型，需要将其导入 UE 进行高质量的实时可视化或 VR 漫游。
-   **工业设计与产品展示**：汽车设计师使用 Alias 设计车身曲面，需要将 `.wire` 文件导入 UE 进行实时渲染、配置器制作或虚拟评审。
-   **数字孪生**：工程师将工厂或设备的 CAD 模型（如来自 SolidWorks 或 CATIA）导入 UE，创建用于监控和仿真的数字孪生体。
-   **游戏资产制作**：从 CAD 软件中导出高精度的机械、载具模型，作为游戏资产的基础。

## 蓝图用法

由于该插件主要作为底层导入/翻译框架，其核心功能通常通过 Datasmith 的通用导入流程（如使用 `DatasmithScene` 或编辑器中的导入按钮）触发，而非直接暴露大量蓝图节点。主要的蓝图交互点在于配置导入过程。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Import Datasmith Scene` | 通用的 Datasmith 场景导入节点，内部会调用本插件的翻译器处理 CAD 文件。 | `UDatasmithSceneFactory` |
| `Get Datasmith Import Options` | 获取或创建用于控制导入行为的选项对象，可以设置 CAD 特定的参数（如曲面细分质量）。 | `UDatasmithImportOptions` |

### 使用示例（蓝图描述）

1.  **通过蓝图导入 CAD 文件**：
    -   使用 `Construct Object from Class` 节点创建一个 `UDatasmithSceneFactory` 对象。
    -   调用 `Import Datasmith Scene` 节点，将 CAD 文件路径（如 `C:\Model.car`）作为 `FilePath` 输入。
    -   可以创建一个 `UDatasmithCADImportOptions` 对象，设置 `TessellationOptions`（曲面细分选项）等参数，并通过 `ImportOptions` 引脚传入。
    -   导入完成后，会生成一个 `UDatasmithScene` 对象，其中包含了转换后的 Actor 和资产信息。

## C++ 用法

本插件的 C++ 用法主要面向需要深度定制导入流程或开发自定义翻译器的开发者。核心接口定义在 `CADLibrary` 和 `DatasmithCADTranslator` 模块中。

### 头文件引入

```cpp
#include "DatasmithCADTranslatorModule.h"
#include "CADLibrary/Public/CADModel.h"
```

### 基本用法

检查 CAD 翻译器模块是否可用，并获取其提供的临时目录（用于存放转换过程中的中间文件）。

```cpp
// 来源：基于 WireInterfaceModule.h 的用法推断
#include "Modules/ModuleManager.h"

void CheckCADTranslatorAvailability()
{
    // 检查模块是否已加载
    if (FModuleManager::Get().IsModuleLoaded(TEXT("DatasmithCADTranslator")))
    {
        UE_LOG(LogTemp, Log, TEXT("Datasmith CAD Translator module is loaded."));
        
        // 获取模块实例（如果需要访问其特定方法）
        // FDatasmithCADTranslatorModule& TranslatorModule = FModuleManager::GetModuleChecked<FDatasmithCADTranslatorModule>(TEXT("DatasmithCADTranslator"));
        // FString TempDir = TranslatorModule.GetTempDir();
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Datasmith CAD Translator module is not available."));
    }
}
```

### 进阶用法

直接使用 `CADLibrary` 中的数据结构来表示和操作 CAD 模型数据。这通常发生在编写自定义的网格处理管线时。

```cpp
// 来源：基于 CADLibrary 模块功能推断
#include "CADLibrary/Public/CADModel.h"
#include "CADLibrary/Public/MeshParameters.h"

void ProcessCADModel()
{
    // 创建一个 CAD 模型对象
    CADLibrary::FCADModel CADModel;
    
    // 设置网格参数，例如曲面细分公差
    CADLibrary::FMeshParameters MeshParams;
    MeshParams.ChordTolerance = 0.1f; // 弦高公差
    MeshParams.MaxEdgeLength = 10.0f; // 最大边长
    MeshParams.NormalTolerance = 10.0f; // 法线角度公差
    
    // 将参数应用到模型（具体API需查阅源码）
    // CADModel.SetMeshParameters(MeshParams);
    
    // ... 后续可能调用转换函数，将 CADModel 转换为 FMeshDescription
}
```

## Demo 示例

以下示例展示了一个最小化的 C++ 类，用于在运行时检查 DatasmithCADTranslator 模块的状态并获取临时目录路径。

**MyCADHelper.h**
```cpp
// MyCADHelper.h
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "MyCADHelper.generated.h"

UCLASS(BlueprintType)
class MYPROJECT_API UMyCADHelper : public UObject
{
    GENERATED_BODY()

public:
    /** 检查 CAD 导入器模块是否可用 */
    UFUNCTION(BlueprintCallable, Category = "CAD")
    bool IsCADImporterAvailable() const;

    /** 获取 CAD 导入器使用的临时目录路径 */
    UFUNCTION(BlueprintCallable, Category = "CAD")
    FString GetCADTempDirectory() const;
};
```

**MyCADHelper.cpp**
```cpp
// MyCADHelper.cpp
#include "MyCADHelper.h"
#include "Modules/ModuleManager.h"

bool UMyCADHelper::IsCADImporterAvailable() const
{
    // 检查核心翻译器模块是否加载
    return FModuleManager::Get().IsModuleLoaded(TEXT("DatasmithCADTranslator"));
}

FString UMyCADHelper::GetCADTempDirectory() const
{
    // 注意：直接获取模块实例并调用方法需要模块已加载
    // 此处仅为演示，实际使用时应先检查 IsCADImporterAvailable()
    if (IsCADImporterAvailable())
    {
        // 通过模块名获取模块实例
        // FDatasmithCADTranslatorModule& Module = FModuleManager::GetModuleChecked<FDatasmithCADTranslatorModule>(TEXT("DatasmithCADTranslator"));
        // return Module.GetTempDir();
        
        // 由于模块接口可能不直接暴露，这里返回一个示例路径
        return FPaths::ProjectSavedDir() / TEXT("CADTemp");
    }
    return TEXT("");
}
```

## 模块依赖

要使用此插件的功能，你的项目模块需要依赖以下独特的模块（除了标准的 Core/Engine 等）：

| 模块 | 用途 |
|---|---|
| `DatasmithCore` | Datasmith 框架的核心库，提供场景、资产等基础数据结构。 |
| `CADLibrary` | 提供 CAD 模型的数据表示、网格参数和基础处理工具。 |
| `CADInterfaces` | 定义与外部 CAD 处理库（如 TechSoft）交互的接口。 |
| `TechSoft` | 第三方库，用于读取和解析多种 CAD 文件格式（如 STEP, IGES）。 |
| `OpenNurbs6` | 第三方库，用于读取和解析 Rhino 的 `.3dm` 文件格式。 |
| `CADKernel` | 用于处理参数化曲面（NURBS）和进行曲面细分的内核。 |
| `DatasmithCADTranslator` | CAD 文件翻译器的核心调度和管理模块。 |

## 维护状态

### 近期更新

```
- 90f00dd86ae6 Added support for Alias 2026.0
- 39994edb437c [Wire] Corrected missing incrementation The mesh was properly sectioned but the missing increment was assigning the same material to each section Somehow the increment step was deleted before submission :-(
- 61d36ec7677f [Wire] Fixed missing colors when using group option - Fixed coding error in FDatasmithStaticMeshImporter::SetupStaticMesh which was eliminating sections when some were sharing the same material - Simplified material assignment to MeshElement's slots. - removed redundant material assignment on MeshActor. - Fixed wrong material slot name used in FMeshDescription. It has to be an integer to work in Datasmith import.
```

**解读**：
1.  **功能更新**：添加了对最新版工业设计软件 Alias 2026.0 的支持，表明插件在持续跟进上游软件版本。
2.  **Bug 修复**：修复了 `.wire` (Alias) 文件导入时材质分配错误的严重问题（缺少递增导致所有网格段使用同一材质）。
3.  **Bug 修复与优化**：修复了使用分组选项时颜色丢失的问题，并优化了材质分配逻辑，修复了 `FMeshDescription` 中材质槽命名错误。

### 维护评价

**综合评价：活跃维护，推荐使用。**

-   **年龄**：插件创建于2019年，已有约6年历史，属于成熟的企业级功能。
-   **活跃度**：从最近的提交记录看，维护非常活跃。最近的更新不仅包含对新软件版本的支持，还修复了影响导入结果正确性的关键Bug。
-   **功能完整性**：作为 Datasmith 生态的核心组件，它功能完整，支持格式广泛，是工业和建筑可视化领域的标准解决方案。
-   **注意事项**：该插件默认禁用（`EnabledByDefault: false`），需要在项目设置中手动启用。它依赖于第三方库（TechSoft, OpenNurbs），这些库的许可和分发可能受限制，通常包含在 Unreal Engine 的企业版或特定构建中。
-   **推荐**：对于需要处理专业 CAD 数据的工作流，此插件是必不可少且值得信赖的选择。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithCADImporter)
-   [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithCADImporter/Tests) (如果存在)