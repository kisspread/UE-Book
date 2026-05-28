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

该插件是 Unreal Engine 中 **Datasmith** 生态系统的一部分，专门用于处理工业和设计领域广泛使用的**计算机辅助设计（CAD）** 文件。其核心功能是将来自 CATIA、SolidWorks、JT、ACIS、Parasolid 等数十种专业 CAD 软件的复杂 3D 模型数据，转换为 Unreal Engine 能够高效渲染和处理的中间几何表示（如网格体、材质参数）。

它解决了以下核心问题：
1.  **格式兼容性**：桥接了工业 CAD 软件与游戏/实时引擎之间的格式鸿沟，支持种类繁多的专有 CAD 格式。
2.  **几何精度转换**：CAD 模型通常由高精度的参数化曲面（B-Rep）构成，而非实时渲染所用的多边形网格。此插件包含先进的**曲面细分（Tessellation）** 引擎（如 CADKernel），能够将这些精确曲面转化为适合 Unreal 渲染的网格，并提供对弦高公差、最大边长等参数的精细控制。
3.  **数据清理与优化**：在导入过程中对几何体进行清理、修复（如缝合不连续边）、去除重复面或薄面，并管理材质和颜色信息的继承与映射。
4.  **性能与缓存**：支持导入结果的缓存，避免重复计算，并利用多线程处理以提高大型模型的导入速度。

## 使用场景

-   **建筑、工程与施工（AEC）**：将 Revit、ArchiCAD 或其他 BIM 软件生成的复杂建筑模型（通常包含 IFC、DWG 文件）导入到 Unreal 中进行建筑可视化或虚拟现实演练。
-   **汽车与工业设计**：导入 CATIA、SolidWorks、Creo 或 NX 生成的汽车零部件、完整车辆或工业设备模型，用于设计评审、营销展示或培训模拟。
-   **产品配置与展示**：需要将精确的 CAD 产品模型（如带有多种配置的 JT 文件）导入 UE，并保持其结构层次和材质属性，以创建交互式产品配置器。
-   **数字孪生**：将工厂布局、机械结构等高精度 CAD 数据导入，用于构建与物理实体同步的实时数字孪生系统。

## 蓝图用法

该插件的核心功能主要由 **Datasmith 导入框架**在后台调用，其大部分 API 是面向 C++ 的模块接口，**并未直接暴露可供蓝图直接调用的节点**。用户通常通过以下方式与之交互：

1.  **Datasmith 导入对话框**：在 Unreal Editor 中使用标准的 “File -> Import Into Level” 并选择支持的 CAD 文件（如 .jt, .catpart, .sldprt），在导入设置对话框中调整 CAD 特定的选项。
2.  **蓝图中的间接使用**：通过 `DatasmithContent` 插件中的蓝图节点（如 `Import Datasmith Scene`）来驱动导入流程，但具体的 CAD 解析和细分参数通常在 C++ 层或通过配置进行设置。

因此，本节不列出具体的蓝图节点，实际操作依赖于 Datasmith 的通用导入管道。

## C++ 用法

该插件的 API 主要服务于 Datasmith 翻译器模块内部以及需要进行深度定制的开发者。

### 头文件引入

```cpp
#include “CADTools/CADData.h”
#include “CADTools/CADOptions.h”
```

### 基本用法

**1. 配置导入参数**

你可以创建一个 `FImportParameters` 实例来配置 CAD 模型的曲面细分和清理行为。

```cpp
// 来源: Public/CADOptions.h
using namespace CADLibrary;

// 创建一个默认导入参数，使用 Z-up 右手坐标系
FImportParameters ImportParams(FDatasmithUtils::EModelCoordSystem::ZUp_RightHanded);

// 设置曲面细分参数：弦高公差为 0.5，最大边长 0，最大法线角度 25 度，使用缝合修复技术
ImportParams.SetTesselationParameters(0.5, 0.0, 25.0, EStitchingTechnique::StitchingHeal);

// 设置静态全局变量，这些变量会影响所有后续导入操作（注意线程安全）
FImportParameters::bGEnableCADCache = true; // 启用缓存
FImportParameters::bGOverwriteCache = false; // 不覆盖缓存
FImportParameters::GStitchingTolerance = 0.01f; // 设置缝合容差
```

**2. 描述 CAD 文件**

使用 `FFileDescriptor` 来描述一个待导入的 CAD 文件。

```cpp
// 来源: Public/CADData.h
// 描述一个位于指定路径的 CAD 文件
FFileDescriptor FileDesc(TEXT(“D:/Models/EngineBlock.jt”));

// 或者，为 JT 等支持配置的文件指定一个特定配置或子文件
FFileDescriptor FileDescWithConfig(TEXT(“D:/Models/CarAssembly.jt”),
                                   TEXT(“Configuration=V6_Engine”),
                                   TEXT(“D:/Models/”));

ECADFormat Format = FileDesc.GetFileFormat(); // 获取文件格式，如 ECADFormat::JT
bool bCanRef = FileDesc.CanReferenceOtherFiles(); // 检查该文件格式是否可能引用外部文件
```

**3. 处理网格数据（通常由内部流程完成）**

`FBodyMesh` 和 `FTessellationData` 是存储从 CAD 模型转换而来的网格数据的核心结构。

```cpp
// 来源: Public/CADData.h
// 创建一个空的体网格对象，用于存储一个 CAD 体（Body）的网格数据
FBodyMesh BodyMesh;
BodyMesh.BodyID = 123; // 设置 CAD 文件中的体 ID
BodyMesh.MeshActorUId = 456; // 关联到 UE 中的 Actor 或 StaticMesh 的唯一 ID

// 添加该体使用的材质/颜色信息
BodyMesh.AddGraphicPropertiesFrom(SomeGraphicProperties);

// 通常，数据会从转换器（如 CADKernel）填充到 BodyMesh.VertexArray 和 BodyMesh.Faces 数组中。
// Faces 数组中的每个 FTessellationData 代表一个面（Face）的网格。

// 将一组体网格序列化到文件以进行缓存或传输
SerializeBodyMeshSet(TEXT(“D:/Cache/BodyMeshSet.ugeom”), BodyMeshArray);
// 从文件反序列化体网格
TArray<FBodyMesh> LoadedBodyMeshes;
DeserializeBodyMeshFile(TEXT(“D:/Cache/BodyMeshSet.ugeom”), LoadedBodyMeshes);
```

### 进阶用法

**1. 材质与颜色标识**

插件使用整数 ID 来标识和管理颜色和材质，以提高效率和避免重复。

```cpp
// 来源: Public/CADData.h
// 从 FColor 创建一个唯一颜色 ID
FColor Red(255, 0, 0);
FMaterialUId RedColorId = BuildColorUId(Red);

// 从 FCADMaterial 结构创建材质 ID
FCADMaterial MatDesc;
MatDesc.MaterialName = TEXT(“Steel”);
MatDesc.Diffuse = FColor(128, 128, 128);
MatDesc.Specular = FColor(200, 200, 200);
MatDesc.Shininess = 0.8f;
FMaterialUId SteelMatId = BuildMaterialUId(MatDesc);
```

**2. 网格修复与缝合选项控制**

可以通过静态变量精细控制网格缝合（Sew）过程的行为。

```cpp
// 来源: Public/CADOptions.h
// 启用强制缝合，并移除薄面和重复面
FImportParameters::bGStitchingForceSew = true;
FImportParameters::bGStitchingRemoveThinFaces = true;
FImportParameters::bGStitchingRemoveDuplicatedFaces = true;
FImportParameters::GStitchingForceFactor = 2.0f; // 调整缝合力系数

// 根据当前全局参数构建 ESewOption 标志
ESewOption CurrentSewOpt = SewOption::GetFromImportParameters();
// CurrentSewOpt 将包含 ForceJoining | RemoveThinFaces | RemoveDuplicatedFaces
```

## Demo 示例

以下示例演示了如何在 C++ 中配置 CAD 导入参数并构建一个 `FFileDescriptor` 对象。请注意，实际的网格转换是由 Datasmith 框架调度的，通常不直接在用户代码中调用细分器。

**MyCADImporter.h**
```cpp
#pragma once
#include “CoreMinimal.h”
#include “CADTools/CADData.h”
#include “CADTools/CADOptions.h”

using namespace CADLibrary;

DECLARE_LOG_CATEGORY_EXTERN(LogMyCADImporter, Log, All);

class FMyCADImporter
{
public:
    /** 配置并描述一个待导入的 CAD 文件 */
    static FFileDescriptor PrepareCADImport(const FString& FilePath);

    /** 显示当前的全局导入设置 */
    static void PrintCurrentSettings();
};
```

**MyCADImporter.cpp**
```cpp
#include “MyCADImporter.h”

DEFINE_LOG_CATEGORY(LogMyCADImporter);

FFileDescriptor FMyCADImporter::PrepareCADImport(const FString& FilePath)
{
    // 1. 配置全局导入参数 (会影响此进程内所有导入)
    FImportParameters::bGEnableCADCache = true;
    FImportParameters::GStitchingTolerance = 0.01f;
    FImportParameters::bGStitchingRemoveDuplicatedFaces = true;

    // 2. 创建文件描述符
    FFileDescriptor FileDesc(*FilePath);

    UE_LOG(LogMyCADImporter, Log, TEXT(“Preparing import for file: %s (Format: %d)“),
        *FileDesc.GetFileName(), static_cast<int32>(FileDesc.GetFileFormat()));

    return FileDesc;
}

void FMyCADImporter::PrintCurrentSettings()
{
    UE_LOG(LogMyCADImporter, Log, TEXT(“=== Current CAD Import Global Settings ===”));
    UE_LOG(LogMyCADImporter, Log, TEXT(“Cache Enabled: %s”), FImportParameters::bGEnableCADCache ? TEXT(“True”) : TEXT(“False”));
    UE_LOG(LogMyCADImporter, Log, TEXT(“Stitching Tolerance: %f”), FImportParameters::GStitchingTolerance);
    UE_LOG(LogMyCADImporter, Log, TEXT(“Remove Duplicated Faces: %s”), FImportParameters::bGStitchingRemoveDuplicatedFaces ? TEXT(“True”) : TEXT(“False”));
    // ... 可以打印更多参数
}

// 使用示例（可能在某个 Editor Utility 或测试模块中）
// FFileDescriptor Descriptor = FMyCADImporter::PrepareCADImport(“D:/Models/Part.step”);
// FMyCADImporter::PrintCurrentSettings();
// 此后，将 Descriptor 提交给 Datasmith 导入器...
```

## 模块依赖

要使用此插件（特别是其提供的 CAD 工具类），你的模块需要依赖以下**独特**模块：

| 模块 | 用途 |
|---|---|
| `CADTools` | 提供核心数据类型（`FBodyMesh`, `FCADMaterial`）、文件描述（`FFileDescriptor`）和导入参数（`FImportParameters`）。 |
| `DatasmithCore` | Datasmith 插件的核心框架，提供了转换、导入的基础类和接口。 |
| `TechSoft` | 可选依赖，支持 ACIS (.sat, .sab), Parasolid (.x_t, .x_b), STEP (.stp, .step), IGES (.igs, .iges) 等格式的转换。需要单独安装 TechSoft 许可和库。 |
| `OpenNurbs6` | 用于支持 Rhino 的 3DM 文件格式解析。 |
| `DatasmithContent` | 提供用于蓝图和内容浏览器中管理 Datasmith 资产的工具和资产类型。 |

*注意：其他如 `CADKernel`, `CADInterfaces` 等是插件内部模块，通常不需要直接引用。常见依赖如 `Core`, `Engine` 已省略。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下 double 常量截断为 float 产生的编译器警告。 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | 增加逻辑，确保即使安装了 Alias 2027，Wire 翻译器也能正常工作。 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 将 TechSoft 库升级到 2026.3 版本。 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新了 DatasmithCAD 缓存版本（可能涉及格式变更）。 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 让函数类型转换警告在 MSVC 和 Clang 编译器之间保持可移植性。 |

### 维护评价

**维护状态：活跃维护**

-   **活跃度**：插件在 2026 年 5 月仍有频繁且实质性的更新（如第三方库升级、新版本支持、编译器兼容性修复），表明它处于**积极维护**中。
-   **创建时间**：插件于 2019 年创建，已成熟多年，但并未停止开发。
-   **技术栈**：依赖外部库（TechSoft, OpenNurbs），并需要支持不断更新的 CAD 软件版本（如文件夹名 WireInterface2026_0 所示），这驱动了持续的更新。
-   **注意事项**：
    1.  该插件**默认未启用** (`EnabledByDefault: false`)，需要在项目中手动启用。
    2.  部分格式（如 ACIS, Parasolid）需要有效的 **TechSoft SDK 许可证**，这可能增加额外成本和集成复杂度。
    3.  插件规模庞大（21个模块），深度定制需要理解 Datasmith 的整体架构。

**推荐**：对于需要从专业 CAD 软件导入高精度模型的 UE 项目，此插件是**官方且核心的解决方案**，推荐使用。建议确保使用最新的引擎版本以获得最佳的兼容性和性能。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)