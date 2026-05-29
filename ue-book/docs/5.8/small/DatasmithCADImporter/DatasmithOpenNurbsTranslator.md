# Datasmith CAD Importer

> Collection of tools to work with CAD files.

| 属性 | 值 |
|---|---|
| 中文名 | CAD导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CADInterfaces` (Runtime), `CADKernelSurface` (Runtime), `CADLibrary` (Runtime), `CADTools` (Runtime), `DatasmithCADTranslator` (Runtime), `DatasmithDispatcher` (Runtime), `DatasmithOpenNurbsTranslator` (Runtime), `DatasmithPLMXMLTranslator` (Runtime), `DatasmithWireTranslator` (Runtime), `ParametricSurface` (Runtime), `ParametricSurfaceExtension` (Runtime), `WireInterface2020` (Runtime), `WireInterface2021_3` (Runtime), `WireInterface2022` (Runtime), `WireInterface2022_1` (Runtime), `WireInterface2022_2` (Runtime), `WireInterface2023_0` (Runtime), `WireInterface2023_1` (Runtime), `WireInterface2024_1` (Runtime), `WireInterface2025_0` (Runtime), `WireInterface2026_0` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

## 用途

Datasmith CAD Importer 是 Unreal Engine 中专门用于导入 CAD (计算机辅助设计) 文件的核心插件集。它解决的核心问题是将工业设计领域常用的 CAD 格式（如 Rhino/OpenNurbs, Alias/Wire, CATIA, NX, STEP, IGES 等）转化为 Unreal Engine 能够识别和高效渲染的网格（Mesh）数据。

这个插件存在的意义在于，它并非简单的网格导入器，而是包含了一套完整的、针对 CAD 数据（如 BRep 边界表示、参数化曲面）的解析、转换和优化管线。它能够处理 CAD 模型中的精确几何信息、拓扑关系（面、边、环），并将其转化为适合实时渲染的三角形网格，同时提供高级选项来控制导入时的曲面细分（Tessellation）质量和精度，是连接专业 CAD 软件与实时 3D 引擎的关键桥梁。

## 使用场景

-   **工业设计与产品可视化**：你在使用 Rhino, Alias 或 CATIA 等 CAD 软件完成产品设计后，需要直接将原始的 `.3dm`，`.wire` 或 `.step` 文件导入 Unreal Engine 进行交互式产品展示、配置器开发或营销视频制作。
-   **建筑、工程与施工（AEC）**：你需要导入大型建筑信息模型（BIM）或机械图纸（如 `.ifc`, `.dwg` 文件），在 Unreal Engine 中创建建筑漫游、施工流程模拟或数字孪生应用。
-   **汽车设计**：你需要将用 ICEM Surf 或 Alias 设计的复杂汽车 A 级曲面模型（通常以 `.wire` 格式保存）导入引擎，进行实时可视化评审和光照测试。
-   **需要保留原始 CAD 精度的场景**：你不满足于从其他软件导出为 `.fbx` 等通用格式可能带来的数据丢失或精度下降，希望直接使用 CAD 原始文件进行导入，以确保几何体和尺寸的绝对精确。

## 蓝图用法

Datasmith CAD 导入功能主要通过 Datasmith 的标准导入选项界面暴露给用户。其核心蓝图可用类和枚举定义了导入时的具体行为。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `UDatasmithOpenNurbsImportOptions` | 用于配置 OpenNurbs（如 Rhino .3dm）文件导入选项的对象。 | `UDatasmithOpenNurbsImportOptions` |
| `FDatasmithOpenNurbsOptions::Geometry` | 控制 BRep 几何体的细分（Tessellation）来源。 | `UDatasmithOpenNurbsImportOptions` |

### 使用示例（蓝图描述）

1.  **设置 OpenNurbs 导入选项**：在进行 Datasmith 导入操作（如通过 `Datasmith Import` 资产或在编辑器中直接拖入文件）之前，可以通过蓝图获取或创建 `UDatasmithOpenNurbsImportOptions` 对象，并修改其 `Options.Geometry` 属性。该属性是一个 `EDatasmithOpenNurbsBrepTessellatedSource` 枚举：
    -   `UseUnrealNurbsTessellation`：在 Unreal Engine 内部对导入的 NURBS 曲面进行细分。这种方式精度更高，但导入时间更长。
    -   `UseRenderMeshes`：直接使用 CAD 文件（如 Rhino）中预先计算好的网格和 UV 数据。这种方式导入速度极快，但网格质量取决于原始 CAD 软件中的设置。
2.  **通过 Datasmith 场景导入**：这个选项通常集成在“Datasmith 导入”对话框的“高级选项”中。在 C++ 或蓝图中，你可以构建包含此选项的数组，传递给 Datasmith 的导入函数。

## C++ 用法

### 头文件引入

```cpp
#include "DatasmithOpenNurbsImportOptions.h"
#include "DatasmithOpenNurbsTranslatorModule.h"
```

### 基本用法：访问导入模块与设置选项

此示例展示了如何检查 OpenNurbs 翻译器模块是否可用，以及如何程序化地设置导入选项。

```cpp
// 来自对 Public/DatasmithOpenNurbsTranslatorModule.h 和 Public/DatasmithOpenNurbsImportOptions.h 的推断
#include "DatasmithOpenNurbsTranslatorModule.h"
#include "DatasmithOpenNurbsImportOptions.h"
#include "DatasmithImportOptions.h" // 对于 FDatasmithImportBaseOptions

void ProgrammaticImportSettings()
{
    // 1. 检查 DatasmithOpenNurbs 模块是否已加载
    if (FDatasmithOpenNurbsTranslatorModule::IsAvailable())
    {
        UE_LOG(LogTemp, Log, TEXT("Datasmith OpenNurbs Translator is available."));
        
        // 2. 获取临时目录（模块可能用于缓存）
        const FString& TempDir = FDatasmithOpenNurbsTranslatorModule::Get().GetTempDir();
        UE_LOG(LogTemp, Log, TEXT("Temporary directory: %s"), *TempDir);
    }

    // 3. 创建并配置 OpenNurbs 导入选项
    UDatasmithOpenNurbsImportOptions* ImportOptions = NewObject<UDatasmithOpenNurbsImportOptions>();
    if (ImportOptions)
    {
        // 设置几何体细分策略为使用文件中的渲染网格（快速导入）
        ImportOptions->Options.Geometry = EDatasmithOpenNurbsBrepTessellatedSource::UseRenderMeshes;
        
        // 可以通过基类 FDatasmithTessellationOptions 设置更广泛的公差参数
        // ImportOptions->Options.SetGeometricTolerance(0.1);
        // ImportOptions->Options.SetStitchingTolerance(0.01);

        // 4. 在调用 Datasmith 导入流程前，将此选项对象添加到选项数组中
        TArray<TObjectPtr<UDatasmithOptionsBase>> OptionsArray;
        OptionsArray.Add(ImportOptions);

        // 5. 此处应调用实际的 Datasmith 导入函数，并将 OptionsArray 传入
        // 例如：DatasmithImportAction->SetSceneImportOptions(OptionsArray);
    }
}
```

### 进阶用法：使用 BRep 转换器

此示例展示了底层 BRep 转换器的使用逻辑，通常由翻译器内部调用，但理解其过程有助于调试导入问题。

```cpp
// 基于对 Private/OpenNurbsBRepConverter.h, OpenNurbsBRepToCADKernelConverter.h, OpenNurbsBRepToTechSoftConverter.h 的分析
#include "OpenNurbsBRepToCADKernelConverter.h"
#include "CADLibrary.h" // 对于 FImportParameters
#include "DatasmithImportOptions.h" // 对于 FDatasmithTessellationOptions

// 假设我们有一个从 OpenNurbs 文件解析出的 BRep (ON_Brep*) 和导入参数
void ConvertBRepData(ON_Brep* Brep, const CADLibrary::FImportParameters& ImportParams)
{
    if (!Brep) return;

    // 1. 配置细分选项
    FDatasmithTessellationOptions TessOptions;
    TessOptions.SetGeometricTolerance(0.05f); // 设置几何公差
    TessOptions.SetStitchingTolerance(0.01f); // 设置缝合公差

    // 2. 创建一个指向 CADKernel 的转换器（一种后端）
    FOpenNurbsBRepToCADKernelConverter CADKernelConverter(ImportParams, TessOptions);
    
    // 设置缩放因子（例如，从文件单位毫米转换到引擎单位厘米）
    CADKernelConverter.SetScaleFactor(0.1); // 1mm = 0.1cm

    // 3. 添加 BRep 进行转换。偏移向量用于调整网格的枢轴点。
    ON_3dVector Offset(0.0, 0.0, 0.0); // 或根据 BoundingBox 中心计算
    bool bSuccess = CADKernelConverter.AddBRep(*Brep, Offset);
    
    if (bSuccess)
    {
        // 转换后的 CADKernel 拓扑面/边数据现在存储在转换器内部，
        // 后续流程会将其进一步处理为可渲染的网格数据。
        UE_LOG(LogTemp, Log, TEXT("BRep conversion to CADKernel initiated successfully."));
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to convert BRep data."));
    }

    // 注：另一种后端是 TechSoft (FOpenNurbsBRepToTechSoftConverter)，需要 TechSoft SDK 支持。
}
```

## Demo 示例

一个最小化的示例，展示如何在 Actor 组件中访问 CAD 导入模块和设置选项。

**CADImporterDemoComponent.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "CADImporterDemoComponent.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class YOURPROJECT_API UCADImporterDemoComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UCADImporterDemoComponent();

    virtual void BeginPlay() override;

    UFUNCTION(BlueprintCallable, Category="CAD Import")
    void SetOpenNurbsImportMethod(bool bUseRenderMeshes);

private:
    bool bUseRenderMeshesByDefault = true;
};
```

**CADImporterDemoComponent.cpp**
```cpp
#include "CADImporterDemoComponent.h"
#include "DatasmithOpenNurbsTranslatorModule.h"
#include "DatasmithOpenNurbsImportOptions.h"

UCADImporterDemoComponent::UCADImporterDemoComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UCADImporterDemoComponent::BeginPlay()
{
    Super::BeginPlay();

    // 检查模块状态
    if (FDatasmithOpenNurbsTranslatorModule::IsAvailable())
    {
        UE_LOG(LogTemp, Log, TEXT("OpenNurbs Translator Module is ready. Temp Dir: %s"),
            *FDatasmithOpenNurbsTranslatorModule::Get().GetTempDir());
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("OpenNurbs Translator Module is not available. Is the plugin enabled?"));
    }
}

void UCADImporterDemoComponent::SetOpenNurbsImportMethod(bool bUseRenderMeshes)
{
    bUseRenderMeshesByDefault = bUseRenderMeshes;
    UE_LOG(LogTemp, Log, TEXT("OpenNurbs import method set to: %s"),
        bUseRenderMeshes ? TEXT("Use Render Meshes") : TEXT("Use Unreal NURBS Tessellation"));
    
    // 此处可以创建 UDatasmithOpenNurbsImportOptions 对象并设置其 Geometry 属性
    // 然后将其保存或用于后续的导入操作。
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `OpenNurbs6` | 提供解析 OpenNurbs (.3dm) 文件格式的核心库。 |
| `TechSoft` (通过 CADInterfaces) | 提供对多种工业 CAD 格式（STEP, IGES, CATIA, NX 等）的高级翻译和处理能力。这是该插件支持多 CAD 格式的底层基础。 |
| `CADKernel` (通过 CADKernelSurface, CADLibrary) | 提供参数化曲面和边界表示（BRep）的数学内核，用于在 Unreal 内部处理和细分从 CAD 文件导入的精确几何体。 |
| `DatasmithCore` | 提供 Datasmith 导入框架的基础接口和数据结构。 |
| `ParametricSurface` / `ParametricSurfaceExtension` | 提供将 CAD 内核的参数化曲面转换为 Unreal 可用网格数据的功能扩展。 |
| `Dispatcher` (DatasmithDispatcher) | 管理可能耗时的 CAD 转换任务，支持并行处理。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下 double 常量被截断为 float 的编译警告。 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | 增加逻辑使 Wire 翻译器在安装 Alias 2027 时仍能工作。 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 将底层 TechSoft 库升级到 2026.3 版本。 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新了 DatasmithCAD 缓存的版本格式。 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 使函数类型转换警告在 MSVC 和 Clang 编译器间具有一致性。 |

### 维护评价

Datasmith CAD Importer 是 Epic Games 为企业级用户维护的关键插件，自 2019 年创建以来持续更新。从近期（2026 年 5 月）的提交历史可以看出，插件仍在 **活跃维护** 中。更新内容不仅包括底层依赖库（TechSoft）的升级以支持最新 CAD 软件版本（如 Alias 2027），还包括对编译器兼容性、代码规范和缓存机制的改进，这表明 Epic 将其作为长期支持的功能。

尽管该插件（`EnabledByDefault=false`）默认不启用，且包含大量模块，架构复杂，但对于有明确工业 CAD 数据导入需求的用户（如建筑、汽车、产品设计行业）来说，它是 **官方推荐且功能完整** 的解决方案。**推荐使用**，但需注意启用后会带来额外的插件体积和可能的第三方库依赖（TechSoft SDK）。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
-   [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter/Tests) (路径推断，位于插件根目录下的 `Tests` 文件夹)