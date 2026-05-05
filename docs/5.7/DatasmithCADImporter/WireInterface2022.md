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

Datasmith CAD Importer 是一个企业级插件，为 Unreal Engine 提供了对多种专业 CAD（计算机辅助设计）文件格式的深度支持。它不仅仅是一个简单的文件导入器，而是一个完整的 CAD 数据处理管线。其核心价值在于能够将来自 Alias、CATIA、NX、SolidWorks、Rhino 等工业设计软件的复杂、高精度参数化模型，转换为适合实时渲染和交互的网格（Mesh）数据，同时尽可能保留原始的材质、图层、元数据和装配结构。

该插件解决了将工程和设计领域的精确模型引入游戏引擎或可视化应用时面临的几何精度、数据完整性和性能优化等关键挑战。它通过一系列专用的翻译器（Translator）模块和底层库（如 TechSoft、OpenNurbs）来实现对不同 CAD 格式的解析和转换。

## 使用场景

- **工业设计与制造可视化**：将汽车、飞机、消费品等产品的 CAD 设计模型导入 UE，用于创建交互式产品配置器、虚拟展厅或装配指导。
- **建筑、工程与施工 (AEC)**：导入来自 Revit、ArchiCAD 等软件的 BIM 模型，进行建筑可视化、施工模拟或设施管理。
- **数字孪生**：将工厂产线、机械设备等的精确 CAD 模型作为数字孪生体的基础，在 UE 中进行仿真、监控和预测性维护。
- **培训与仿真**：利用复杂的机械 CAD 模型创建高保真的操作培训或维修仿真应用。

## 蓝图用法

该插件主要作为底层数据处理管线运行，其大部分功能通过 Datasmith 的标准导入流程（如通过内容浏览器导入 .wire、.catpart 等文件）或 C++ API 暴露。直接暴露给蓝图的高级节点较少。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetTempDir` | 获取用于 CAD 文件转换过程的临时目录路径。 | `FDatasmithWireTranslatorModule` |

### 使用示例（蓝图描述）

由于核心功能集成在导入流程中，蓝图中通常不直接调用 CAD 转换函数。更常见的用法是：
1.  在项目设置中启用 `DatasmithCADImporter` 插件。
2.  通过内容浏览器的“导入”按钮或 Datasmith 工作流，选择支持的 CAD 文件（如 `.wire`, `.catpart`, `.step`）。
3.  在导入对话框中配置导入选项（如曲面细分精度、材质处理等）。
4.  导入完成后，生成的静态网格体、材质和 Actor 会出现在内容浏览器和场景中。

## C++ 用法

该插件的 C++ API 主要用于扩展和自定义导入流程，或在运行时程序化地处理 CAD 数据。

### 头文件引入

```cpp
#include "WireInterfaceModule.h"
```

### 基本用法

获取 WireInterface 模块实例并查询其状态。

```cpp
// 检查 WireInterface 模块是否可用
if (UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FDatasmithWireTranslatorModule::IsAvailable())
{
    // 获取模块实例
    UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FDatasmithWireTranslatorModule& WireModule = 
        UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FDatasmithWireTranslatorModule::Get();
    
    // 获取用于文件转换的临时目录
    FString TempDirectory = WireModule.GetTempDir();
    UE_LOG(LogTemp, Log, TEXT("CAD转换临时目录: %s"), *TempDirectory);
}
```

### 进阶用法

更复杂的用法涉及与 `DatasmithCADTranslator` 和 `CADTools` 模块交互，以编程方式控制 CAD 文件的解析、几何处理和网格生成。这通常需要深入理解 Datasmith 的翻译器架构和 CAD 内部数据结构。

## Demo 示例

以下示例展示了如何在 C++ 中检查并初始化 WireInterface 模块。

**MyCADProcessor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "WireInterfaceModule.h"
#include "MyCADProcessor.generated.h"

UCLASS()
class AMyCADProcessor : public AActor
{
    GENERATED_BODY()

public:
    AMyCADProcessor();

    virtual void BeginPlay() override;

    UFUNCTION(BlueprintCallable, Category = "CAD Processing")
    bool InitializeCADProcessor();

    UFUNCTION(BlueprintCallable, Category = "CAD Processing")
    FString GetCADTempDirectory() const;

private:
    bool bIsProcessorReady;
};
```

**MyCADProcessor.cpp**
```cpp
#include "MyCADProcessor.h"
#include "WireInterfaceModule.h"

AMyCADProcessor::AMyCADProcessor()
{
    PrimaryActorTick.bCanEverTick = false;
    bIsProcessorReady = false;
}

void AMyCADProcessor::BeginPlay()
{
    Super::BeginPlay();
    InitializeCADProcessor();
}

bool AMyCADProcessor::InitializeCADProcessor()
{
    if (!UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FDatasmithWireTranslatorModule::IsAvailable())
    {
        UE_LOG(LogTemp, Warning, TEXT("Datasmith Wire Translator 模块未加载。请确保 DatasmithCADImporter 插件已启用。"));
        bIsProcessorReady = false;
        return false;
    }

    UE_LOG(LogTemp, Log, TEXT("CAD 处理器初始化成功。"));
    bIsProcessorReady = true;
    return true;
}

FString AMyCADProcessor::GetCADTempDirectory() const
{
    if (!bIsProcessorReady)
    {
        return TEXT("");
    }

    return UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FDatasmithWireTranslatorModule::Get().GetTempDir();
}
```

## 模块依赖

该插件的模块依赖于以下专业库，这些是其核心功能的基础：

| 模块 | 用途 |
|---|---|
| `TechSoft` | 提供对多种主流 CAD 格式（如 CATIA, NX, SolidWorks, STEP, IGES）的读取和解析能力。 |
| `OpenNurbs6` | 用于解析 Rhino 的 `.3dm` 文件格式，处理 NURBS 曲面和几何体。 |

## 维护状态

### 近期更新

```
- 90f00dd86ae6 Added support for Alias 2026.0
- 39994edb437c [Wire] Corrected missing incrementation The mesh was properly sectioned but the missing increment was assigning the same material to each section Somehow the increment step was deleted before submission :-(
- 61d36ec7677f [Wire] Fixed missing colors when using group option - Fixed coding error in FDatasmithStaticMeshImporter::SetupStaticMesh which was eliminating sections when some were sharing the same material - Simplified material assignment to MeshElement's slots. - removed redundant material assignment on MeshActor. - Fixed wrong material slot name used in FMeshDescription. It has to be an integer to work in Datasmith import.
```

### 维护评价

**活跃维护**。该插件作为 Epic Games 企业级 Datasmith 解决方案的核心组件，持续得到更新和维护。从近期提交记录可以看出：
1.  **功能扩展**：正在添加对最新版本 CAD 软件（如 Alias 2026.0）的支持。
2.  **Bug 修复**：积极修复材质分配、网格分段等关键导入流程中的问题。
3.  **代码优化**：对导入逻辑进行简化和重构，提高稳定性和效率。

该插件是 UE 中处理专业 CAD 数据的官方且推荐的方式，适合在企业级项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)