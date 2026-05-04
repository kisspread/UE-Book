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

Datasmith CAD Importer 是一套完整的 CAD 文件导入管线，用于将工业设计、建筑和制造领域常用的 CAD 格式（如 CATIA, NX, SolidWorks, STEP, IGES, JT, Rhino 等）转换并导入到 Unreal Engine 中。它不仅仅是简单的格式转换，更是一个包含高级功能的处理框架，解决了 CAD 模型在游戏引擎中应用的核心挑战：

1.  **参数化曲面处理**：支持将 CAD 软件中的精确参数化曲面（NURBS）转换为引擎可用的多边形网格，并提供精细的曲面细分控制。
2.  **网格修复与优化**：自动处理 CAD 模型中常见的几何问题，如缝隙、重叠面、薄壁等，通过缝合（Stitching）和修复（Healing）技术生成干净的网格。
3.  **材质与显示属性保留**：尽可能保留原始 CAD 文件中的材质、颜色、图层等显示属性，并将其映射为 UE 材质。
4.  **大型装配体支持**：通过分布式处理（Dispatcher）和缓存机制，高效处理包含成千上万个零件的大型装配体。
5.  **多版本 CAD 格式支持**：通过独立的 `WireInterface` 模块，支持不同年份版本的 CAD 软件原生格式。

该插件默认禁用 (`EnabledByDefault: false`)，需要用户在项目设置中手动启用，因为它依赖于特定的第三方库（如 TechSoft, OpenNurbs）。

## 使用场景

-   **汽车设计可视化**：将 CATIA 或 NX 中的汽车内外饰模型导入 UE，用于实时渲染、虚拟评审或配置器。
-   **建筑与施工 (AEC)**：导入 Revit 或其他 BIM 软件生成的 IFC 文件，用于建筑可视化、施工模拟或数字孪生。
-   **工业设备与机械**：将 SolidWorks 或 Inventor 中的复杂机械装配体导入 UE，用于产品展示、交互式手册或培训模拟。
-   **消费电子产品**：导入 Creo 或 Solid Edge 的产品模型，用于创建高质量的产品发布视频或 AR/VR 体验。
-   **Rhino/Grasshopper 设计**：通过 OpenNurbs 支持，将 Rhino 的 3DM 文件直接导入 UE，适用于建筑设计和艺术创作。

## 蓝图用法

该插件主要通过 C++ 接口和编辑器操作（如 Datasmith 导入器）使用，直接暴露给蓝图的节点较少。核心功能通过 `FImportParameters` 类进行配置。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetTesselationParameters` | 设置网格细分参数（弦公差、最大边长、法线角度） | `CADLibrary::FImportParameters` |
| `SetStitchingTechnique` | 设置网格缝合/修复技术（无、修复、缝合） | `CADLibrary::FImportParameters` |
| `SetMesher` | 选择网格生成器（CADKernel 或 TechSoft） | `CADLibrary::FImportParameters` |
| `SetModelCoordSystem` | 设置导入模型的坐标系 | `CADLibrary::FImportParameters` |
| `GetCacheVersion` | 获取当前 CAD 缓存版本号，用于判断缓存是否过期 | `FCADToolsModule` |

### 使用示例（蓝图描述）

在蓝图中，通常不直接调用这些函数。它们更多地被 C++ 的导入逻辑内部使用。用户通过编辑器中的 **Datasmith 导入** 窗口来配置这些参数。例如，在导入一个 STEP 文件时，可以在导入对话框的 **高级** 选项中找到“网格化方法”、“缝合选项”等设置，这些设置最终会映射到 `FImportParameters` 的相应属性上。

## C++ 用法

### 头文件引入

```cpp
#include "CADToolsModule.h"
#include "CADOptions.h"
#include "CADData.h"
```

### 基本用法

以下示例展示了如何获取 CADTools 模块并配置基本的导入参数。

```cpp
// 来源：基于 CADToolsModule.h 和 CADOptions.h 推断
#include "CADToolsModule.h"
#include "CADOptions.h"

void ConfigureCADImport()
{
    // 1. 检查 CADTools 模块是否可用
    if (FCADToolsModule::IsAvailable())
    {
        UE_LOG(LogTemp, Log, TEXT("CADTools 模块已加载，缓存版本: %u"), FCADToolsModule::GetCacheVersion());
    }

    // 2. 创建并配置导入参数
    CADLibrary::FImportParameters ImportParams;

    // 设置网格细分质量（弦公差越小，网格越精细）
    ImportParams.SetTesselationParameters(
        0.1,  // ChordTolerance (mm)
        0.0,  // MaxEdgeLength (0 表示自动)
        15.0, // MaxNormalAngle (度)
        CADLibrary::EStitchingTechnique::StitchingHeal // 使用修复技术
    );

    // 选择网格生成器
    ImportParams.SetMesher(CADLibrary::EMesher::CADKernel);

    // 设置坐标系（例如，Z轴向上，右手系）
    ImportParams.SetModelCoordSystem(FDatasmithUtils::EModelCoordSystem::ZUp_RightHanded);

    // 3. 这些参数随后会被传递给 Datasmith 的导入流程
    // 例如，在自定义的 Datasmith Translator 中使用
}
```

### 进阶用法

通过全局静态变量控制更底层的导入行为。

```cpp
// 来源：基于 CADOptions.h 中的静态变量推断
#include "CADOptions.h"

void AdvancedCADImportSettings()
{
    // 启用 CAD 缓存以加速重复导入
    CADLibrary::FImportParameters::bGEnableCADCache = true;

    // 强制覆盖现有缓存
    CADLibrary::FImportParameters::bGOverwriteCache = true;

    // 设置全局缝合容差
    CADLibrary::FImportParameters::GStitchingTolerance = 0.05f;

    // 启用缝合时强制连接
    CADLibrary::FImportParameters::bGStitchingForceSew = true;

    // 设置最大线程数用于并行处理
    CADLibrary::GMaxImportThreads = 8;

    // 禁用 CADKernel 细分，仅使用 TechSoft
    CADLibrary::FImportParameters::bGDisableCADKernelTessellation = true;
}
```

## Demo 示例

一个最小的示例，展示如何在自定义模块中使用 CADTools 模块进行初始化和参数检查。

**MyCADProcessor.h**
```cpp
#pragma once

#include "CoreMinimal.h"

class FMyCADProcessor
{
public:
    void Initialize();
    bool CanProcessCADFile(const FString& FilePath) const;
};
```

**MyCADProcessor.cpp**
```cpp
#include "MyCADProcessor.h"
#include "CADToolsModule.h"
#include "CADOptions.h"
#include "CADData.h"

void FMyCADProcessor::Initialize()
{
    // 确保 CADTools 模块已加载
    if (!FCADToolsModule::IsAvailable())
    {
        UE_LOG(LogTemp, Error, TEXT("CADTools 模块不可用，无法处理 CAD 文件。"));
        return;
    }

    UE_LOG(LogTemp, Log, TEXT("CAD 处理器初始化完成。缓存版本: %u"), FCADToolsModule::GetCacheVersion());

    // 可以在此处设置一些默认的全局参数
    CADLibrary::FImportParameters::bGEnableCADCache = true;
}

bool FMyCADProcessor::CanProcessCADFile(const FString& FilePath) const
{
    // 使用 CADLibrary 中的工具函数检查文件扩展名
    FString Extension = CADLibrary::GetExtension(FilePath);

    // 检查是否为支持的 CAD 格式
    static const TArray<FString> SupportedExtensions = {
        TEXT(".catpart"), TEXT(".catproduct"), TEXT(".cgr"),
        TEXT(".step"), TEXT(".stp"), TEXT(".iges"), TEXT(".igs"),
        TEXT(".jt"), TEXT(".3dm"), TEXT(".ifc"), TEXT(".sldprt")
    };

    return SupportedExtensions.Contains(Extension);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `TechSoft` | 提供对多种 CAD 格式（如 CATIA, NX, SolidWorks, STEP, IGES, JT）的读取和几何处理核心能力。 |
| `OpenNurbs6` | 用于读取和解析 Rhino 的 3DM 文件格式。 |
| `DatasmithCore` | 提供 Datasmith 导入框架的基础类和接口。 |

## 维护状态

### 近期更新

-   70cdacc72d5f Upgraded TechSoft SDK from 2025.3.0 to 2025.6.1
    *解读：升级了核心的第三方 CAD 处理库，以支持更新的 CAD 软件版本和格式。*
-   82ae470e2dc2 Enabled FBX import into level by default at the global variable instead of ConsoleVariables.ini Remove unnecessary CAD releated CVArs from ConsoleVariables.ini. The default values are updated in the cpp file.
    *解读：优化了配置方式，将部分设置从配置文件移至代码默认值，并清理了过时的控制台变量。*
-   0651a18aeb67 Upgraded version of TechSoft SDK to 2024.6 Updated version of cache sub-directory #jira UE-210616 #rnx #rb alexis.matte
    *解读：持续更新 TechSoft SDK，并修复了缓存目录版本管理的问题。*

### 维护评价

**活跃维护**。该插件作为 Epic Games 企业级功能的一部分，保持着稳定的更新节奏。近期的提交主要集中在：
1.  **核心依赖更新**：持续跟进 TechSoft SDK 的新版本，确保对最新 CAD 软件格式的支持。
2.  **功能优化与清理**：改进配置逻辑，移除冗余代码，提升用户体验。
3.  **问题修复**：根据内部任务跟踪系统（Jira）修复已知问题。

尽管插件创建于约 6 年前，但其核心功能（CAD 导入）在工业可视化领域需求稳定，且 Epic 通过定期更新第三方库来维持其兼容性。**推荐在需要导入专业 CAD 格式的项目中使用**，但需注意其默认禁用，且可能依赖特定的第三方许可。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithCADImporter)
-   [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)