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

DatasmithCADImporter 是 Unreal Engine Datasmith 生态系统中的核心组件，专门用于将各种计算机辅助设计（CAD）软件生成的文件格式导入到 Unreal Engine 中。它不仅仅是一个简单的文件转换器，而是一套完整的工具集，旨在解决 CAD 数据（通常包含复杂的参数化曲面、精确的几何体和丰富的元数据）到游戏引擎实时渲染环境（通常使用三角形网格）的转换难题。

该插件通过一系列专用的翻译器模块（如 `DatasmithWireTranslator`、`DatasmithOpenNurbsTranslator`）来处理不同的 CAD 格式（如 Alias 的 .wire、Rhino 的 .3dm）。其核心价值在于：
1.  **保留设计意图**：尽可能保留原始 CAD 模型的层次结构、材质、元数据等信息。
2.  **优化网格生成**：将参数化曲面（NURBS）高效地转换为适合实时渲染的三角形网格，并提供控制选项。
3.  **集成与分发**：作为 Datasmith 框架的一部分，与 Datasmith Importer 和 Datasmith Direct Link 等功能无缝集成，支持大规模资产的批量处理和实时同步。

## 使用场景

-   **工业设计与汽车可视化**：将 Alias、CATIA、NX 等专业 CAD 软件创建的汽车、消费品模型导入 UE，用于创建高保真的产品配置器、虚拟展厅或营销视频。
-   **建筑、工程与施工（AEC）**：导入来自 Revit、ArchiCAD 或其他 BIM 软件的建筑模型，用于建筑可视化、虚拟漫游和施工模拟。
-   **需要精确几何体的场景**：任何需要从 CAD 软件导入具有精确尺寸和复杂曲面的模型，并在 UE 中进行实时渲染或交互的项目。

## 蓝图用法

该插件主要作为运行时数据处理模块，其核心功能通过 Datasmith 的导入流程（如 `Datasmith Import` 按钮或 `DatasmithScene` 资产）间接暴露。它本身不提供大量直接的蓝图节点，而是作为底层引擎被上层工具调用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetTempDir` | 获取用于 CAD 文件转换过程的临时目录路径。 | `FDatasmithWireTranslatorModule` |

### 使用示例（蓝图描述）

在蓝图中，你通常不会直接与 `WireInterface` 模块交互。相反，你会：
1.  使用 **Datasmith Import** 资源管理器按钮或 **DatasmithScene** 资产来导入 .wire 文件。
2.  在导入设置中，你可以找到与 CAD 导入相关的选项（如曲面细分质量、单位转换等），这些选项的底层逻辑由 `DatasmithCADImporter` 插件处理。
3.  如果你需要在运行时动态获取临时目录（例如用于自定义的预处理脚本），可以通过 C++ 调用 `FDatasmithWireTranslatorModule::Get().GetTempDir()`，然后将其暴露给蓝图。

## C++ 用法

### 头文件引入

```cpp
#include "WireInterfaceModule.h"
```

### 基本用法

该模块主要提供对翻译器生命周期和临时资源的管理。以下是如何检查模块是否可用并获取临时目录的示例。

```cpp
// 来源：基于 WireInterfaceModule.h 的典型使用模式
#include "WireInterfaceModule.h"

void CheckWireTranslator()
{
    // 检查 Datasmith Wire 翻译器模块是否已加载
    if (UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FDatasmithWireTranslatorModule::IsAvailable())
    {
        // 获取模块实例
        UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FDatasmithWireTranslatorModule& WireModule = 
            UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FDatasmithWireTranslatorModule::Get();

        // 获取用于转换过程的临时目录
        FString TempDir = WireModule.GetTempDir();
        UE_LOG(LogTemp, Log, TEXT("Wire Translator Temp Directory: %s"), *TempDir);
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Datasmith Wire Translator module is not loaded."));
    }
}
```

### 进阶用法

在实际的 Datasmith 导入流水线中，`WireInterface` 模块会被 `DatasmithCADTranslator` 或 `DatasmithDispatcher` 等上层模块调用。开发者通常不需要直接操作它，而是通过配置 Datasmith 的导入参数来影响其行为。例如，在导入设置中调整网格质量参数，这些参数会传递给底层的 `CADTools` 和 `ParametricSurface` 模块进行处理。

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何在你的模块中检查并使用 `DatasmithWireTranslator` 模块。

**MyActor.h**
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyActor.generated.h"

UCLASS()
class MYPROJECT_API AMyActor : public AActor
{
    GENERATED_BODY()

public:
    AMyActor();

    virtual void BeginPlay() override;

    UFUNCTION(BlueprintCallable, Category = "Datasmith")
    void CheckWireTranslatorStatus();
};
```

**MyActor.cpp**
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.

#include "MyActor.h"
#include "WireInterfaceModule.h" // 引入 WireInterface 模块头文件

AMyActor::AMyActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyActor::BeginPlay()
{
    Super::BeginPlay();
    CheckWireTranslatorStatus();
}

void AMyActor::CheckWireTranslatorStatus()
{
    // 使用模块提供的静态方法检查可用性
    if (UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FDatasmithWireTranslatorModule::IsAvailable())
    {
        UE_LOG(LogTemp, Log, TEXT("Datasmith Wire Translator is available."));
        
        // 获取模块实例并使用其功能
        const auto& WireModule = UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FDatasmithWireTranslatorModule::Get();
        FString TempPath = WireModule.GetTempDir();
        UE_LOG(LogTemp, Log, TEXT("Temp directory for CAD processing: %s"), *TempPath);
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Datasmith Wire Translator is not loaded. Ensure the plugin is enabled."));
    }
}
```

## 模块依赖

从各模块的 `Build.cs` 文件分析，该插件依赖于一些特定的第三方库来解析 CAD 格式。

| 模块 | 用途 |
|---|---|
| `TechSoft` | 提供对多种 CAD 格式（如 STEP, IGES, CATIA, NX 等）的读取和解析能力，是 `CADInterfaces` 模块的核心依赖。 |
| `OpenNurbs6` | 用于解析 Rhino 的 .3dm 文件格式，是 `DatasmithOpenNurbsTranslator` 模块的核心依赖。 |

## 维护状态

### 近期更新

```
- 90f00dd86ae6 Added support for Alias 2026.0
- 39994edb437c [Wire] Corrected missing incrementation The mesh was properly sectioned but the missing increment was assigning the same material to each section Somehow the increment step was deleted before submission :-(
- 61d36ec7677f [Wire] Fixed missing colors when using group option - Fixed coding error in FDatasmithStaticMeshImporter::SetupStaticMesh which was eliminating sections when some were sharing the same material - Simplified material assignment to MeshElement's slots. - removed redundant material assignment on MeshActor. - Fixed wrong material slot name used in FMeshDescription. It has to be an integer to work in Datasmith import.
```

**解读**：
1.  **功能更新**：添加了对最新版 Alias 2026.0 的支持，表明插件在持续跟进上游 CAD 软件的版本更新。
2.  **Bug 修复**：修复了在使用分组选项时材质丢失的问题，以及网格导入过程中材质分配和插槽命名的多个错误。这些修复提升了导入结果的准确性和可靠性。

### 维护评价

**综合评价：活跃维护中。**
-   **年龄**：插件已存在约6年，属于成熟的企业级功能。
-   **活跃度**：从最近的提交记录看，维护非常活跃。最新的提交（支持 Alias 2026.0）发生在近期，且之前的提交都是针对核心功能的实质性 Bug 修复和改进。
-   **状态**：作为 Epic Games 官方维护的企业级插件，其稳定性和长期支持有保障。
-   **推荐**：**强烈推荐**给需要处理专业 CAD 数据（尤其是 Alias .wire 格式）的用户。该插件是 Datasmith 工作流中不可或缺的一环，且维护状态良好。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithCADImporter)
-   [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithCADImporter/Tests) (路径推断，实际测试可能位于 `Engine/Tests/` 或插件内部)