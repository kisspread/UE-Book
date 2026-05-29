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

本插件并非一个简单的“文件导入器”，而是 **Datasmith 管线中专门用于处理复杂 CAD 数据的核心后端引擎集合**。它解决的核心问题是：**将来自工业设计软件（如 Autodesk Alias）的高级几何与拓扑数据，精确、高效地转换并网格化为 Unreal Engine 可用的 Mesh 和材质资产**。

其主要工作包括：
1.  **解析多种 CAD 格式**：通过多个 `Translator` 模块（如 `DatasmithWireTranslator`、`DatasmithOpenNurbsTranslator`）支持 `.wire`（Alias）、`.3dm`（Rhino/OpenNurbs）、`.plmxml` 等格式。
2.  **集成专业内核**：集成了 **CADKernel** 和 **TechSoft** 两个工业级几何内核，用于进行高精度的曲面细分、修复和转换，这是其处理复杂 CAD 数据的关键。
3.  **构建场景图**：将 CAD 模型的层级结构（Group、Layer、Body）映射为 Datasmith 的 `IDatasmithActorElement` 场景树。
4.  **材质转换**：将 CAD 软件中的着色器（如 Alias 的 Blinn、Phong）转换为 UE 的 PBR 材质。
5.  **多进程调度**：通过 `DatasmithDispatcher` 模块可能支持分布式处理，加速大型模型的导入。

简而言之，当通过 Datasmith 导入 CAD 文件时，实际的数据转换、几何处理工作由此插件的各个模块协作完成。

## 使用场景

-   你是汽车设计师或工业设计师，使用 **Autodesk Alias** 设计复杂曲面，并需要在 Unreal Engine 中创建实时交互的虚拟评审环境或营销素材 → 使用此插件的 **DatasmithWireTranslator** 模块。
-   你需要将 **Rhino** 或其他使用 OpenNurbs 内核的软件中的 3D 模型导入引擎，且模型包含复杂的裁剪曲面 (Trimmed Surfaces) → 使用此插件的 **DatasmithOpenNurbsTranslator** 模块。
-   你在实现一个完整的 **数字样机 (Digital Mock-up)** 或 **产品配置器** 管线，需要将 PLM（产品生命周期管理）系统中的 CAD 数据（PLMXML 格式）导入 Unreal → 使用此插件的 **DatasmithPLMXMLTranslator** 模块。
-   你希望在导入过程中获得最高质量的曲面细分结果，并需要在 **CADKernel** 和 **TechSoft** 两种后端之间进行选择或切换。

## 蓝图用法

本插件主要作为 **运行时翻译器模块**，其核心 API 是 `IWireInterface`，通常不直接暴露给蓝图使用。实际的导入流程由 Datasmith 框架自动调用。开发者主要通过 **Datasmith Importer 的设置** 来间接影响其行为。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetImportSettings` | 为 Wire 翻译器配置导入选项（如细分精度、坐标转换等）。 | `FWireTranslatorImpl` (实现 `IWireInterface`) |
| `Load` | 加载指定的 .wire 文件场景。 | `FWireTranslatorImpl` (实现 `IWireInterface`) |
| `LoadStaticMesh` | 根据已加载的网格元素数据，生成实际的 `FMeshDescription`。 | `FWireTranslatorImpl` (实现 `IWireInterface`) |

### 使用示例（蓝图描述）

由于本插件是底层引擎，蓝图中通常不直接调用其函数。用户交互层面，主要通过以下方式影响其工作：
1.  在 **Datasmith Import** 面板中选择要导入的 `.wire` 或其他支持的 CAD 文件。
2.  在 **Import Settings** 面板中，配置 **Datasmith CAD Translator** 相关的参数，例如：
    *   **Tessellation Options**：控制曲面网格化的精度（如公差、最大边长）。
    *   **Geometry Kernel**：选择使用 CADKernel 还是 TechSoft 后端。
    *   **Scale** 和 **Coordinate System**：设置单位和坐标系转换。
3.  执行导入，Datasmith 框架会自动实例化对应的翻译器模块（如 `DatasmithWireTranslator`）来处理文件。

## C++ 用法

本插件的设计允许开发者集成自定义的 CAD 转换逻辑。以下示例基于源码中 `FWireTranslatorImpl` 和转换器类的模式。

### 头文件引入

```cpp
#include "WireInterfaceModule.h" // 模块基础
#include "WireInterfaceImpl.h"   // Wire翻译器实现
// 如果需要使用 CADKernel 或 TechSoft 进行自定义转换
#include "AliasModelToCADKernelConverter.h"
#include "AliasModelToTechSoftConverter.h"
```

### 基本用法（调用现有翻译器流程）

通常，以下流程由 Datasmith 框架管理。如果需要编程式导入，可参考此模式。

```cpp
// 1. 获取并加载翻译器模块
auto& WireModule = UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FDatasmithWireTranslatorModule::Get();
// ... 确保模块已加载

// 2. 创建翻译器实例并配置
TSharedPtr<UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FWireTranslatorImpl> Translator = MakeShared<UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FWireTranslatorImpl>();
// 来源：Private/WireInterfaceImpl.h
Translator->SetImportSettings(MyWireSettings); // 配置导入参数
Translator->SetOutputPath(MyOutputPath);

// 3. 初始化并加载场景
if (Translator->Initialize(TEXT("C:/MyModel.wire")))
{
    // 创建一个用于接收数据的 Datasmith 场景
    TSharedPtr<IDatasmithScene> DatasmithScene = FDatasmithSceneFactory::CreateScene(TEXT("MyCADScene"));
    if (Translator->Load(DatasmithScene))
    {
        // 此时 DatasmithScene 应已被填充了从 .wire 文件解析出的 Actor、Mesh、Material 等元素
        // 可以将这个场景对象进一步传递给 Datasmith 的其他工具进行序列化或直接应用到世界中
    }
}
```

### 进阶用法（自定义几何转换器）

如果需要扩展支持新的几何类型，可以继承并实现 `FCADModelToCADKernelConverterBase` 或 `FCADModelToTechSoftConverterBase`。

```cpp
// 来源：Private/AliasModelToCADKernelConverter.h
// 假设我们需要支持一个新的 Alias 节点类型
class FMyCustomAliasConverter : public UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FAliasModelToCADKernelConverter
{
public:
    using FAliasModelToCADKernelConverter::FAliasModelToCADKernelConverter;

    // 重写添加几何的方法，处理我们的自定义节点
    virtual bool AddGeometry(const CADLibrary::FCADModelGeometry& Geometry) override
    {
        if (const FAliasGeometry* AliasGeom = static_cast<const FAliasGeometry*>(&Geometry))
        {
            // 获取 Alias DAG 节点
            const FAlDagNodePtr& DagNode = ...; // 从某种映射中获取
            if (DagNode.IsValid())
            {
                // 这里可以调用 AddBRep 或其他基类方法，并传入我们自定义的处理逻辑
                // 例如，对特定类型的节点进行特殊的拓扑修复
                return AddBRep(DagNode, 0, EAliasObjectReference::LocalReference);
            }
        }
        return false;
    }

    // 可能需要重写网格化或拓扑修复方法
    virtual bool Tessellate(const CADLibrary::FMeshParameters& InMeshParameters, FMeshDescription& OutMeshDescription) override
    {
        // 在调用基类前进行自定义预处理
        bool bResult = FAliasModelToCADKernelConverter::Tessellate(InMeshParameters, OutMeshDescription);
        // 在网格生成后进行自定义后处理，例如添加特定的顶点属性
        return bResult;
    }
};
```

## Demo 示例

一个最小化的、编程式调用 Datasmith Wire 翻译器的控制台应用示例。假设已有一个有效的 `.wire` 文件路径。

```cpp
// MyCADImporter.h
#pragma once
#include "CoreMinimal.h"

class FMyCADImporter
{
public:
    static bool ImportWireFile(const FString& WireFilePath, const FString& OutputDir);
};
```

```cpp
// MyCADImporter.cpp
#include "MyCADImporter.h"
#include "WireInterfaceModule.h"
#include "WireInterfaceImpl.h"
#include "DatasmithSceneFactory.h" // 来自 Datasmith 核心模块

bool FMyCADImporter::ImportWireFile(const FString& WireFilePath, const FString& OutputDir)
{
    // 检查并加载翻译器模块
    if (!UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FDatasmithWireTranslatorModule::IsAvailable())
    {
        UE_LOG(LogTemp, Error, TEXT("WireInterface module is not available."));
        return false;
    }
    auto& WireModule = UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FDatasmithWireTranslatorModule::Get();

    // 创建翻译器
    auto Translator = MakeShared<UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FWireTranslatorImpl>();
    Translator->SetOutputPath(OutputDir);

    // 设置导入参数 (示例)
    FWireSettings Settings;
    // ... 填充 Settings ...
    Translator->SetImportSettings(Settings);

    // 初始化并加载
    if (!Translator->Initialize(*WireFilePath))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to initialize translator for: %s"), *WireFilePath);
        return false;
    }

    // 创建 Datasmith 场景对象
    TSharedPtr<IDatasmithScene> Scene = FDatasmithSceneFactory::CreateScene(TEXT("ImportedWireScene"));
    if (!Translator->Load(Scene))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to load wire file: %s"), *WireFilePath);
        return false;
    }

    // 导入成功，此时 Scene 中应包含转换后的数据
    UE_LOG(LogTemp, Log, TEXT("Successfully imported wire file. Scene has %d children."), Scene->GetActorsCount());

    // 这里可以将 Scene 序列化为 .udatasmith 文件，或用于其他处理
    // 例如: FDatasmithSceneExporter::ExportSceneToUAsset(Scene, OutputPath);

    return true;
}
```

## 模块依赖

从模块名和源码分析推断，此插件的核心依赖。要使用此插件，你的模块通常不需要直接依赖它，因为调用由 Datasmith 框架完成。但如果你要**集成或扩展**此插件，你的模块可能需要以下依赖。

| 模块 | 用途 |
|---|---|
| `TechSoft` | 提供 A3DSDK 库，用于解析和处理 A3D CAD 内核数据（如 STEP、IGES、CATIA 等）。 |
| `OpenNurbs6` | 提供 OpenNurbs 工具包，用于解析和处理 Rhino 的 3DM 文件格式。 |
| `CADKernel` | Epic 自研的 CAD 几何内核，用于高精度曲面细分、修复和网格化。 |
| `CADLibrary` | 提供通用的 CAD 数据结构、导入参数和转换器基础类。 |
| `DatasmithCore` | Datasmith 框架的核心库，提供场景、元素、材质等基础接口。 |

*注意：常见的 Core, CoreUObject, Engine 等依赖已省略。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，双精度常量转换为浮点数时产生的编译警告。 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | 添加了兼容性逻辑，使 Wire 翻译器在安装了 Alias 2027 版本的环境下也能正常工作。 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 将 TechSoft 依赖库更新到了 2026.3 版本。 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新了 Datasmith CAD 缓存的版本机制。 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 修复了函数类型转换警告，使其在 MSVC 和 Clang 编译器间都能正常编译。 |

### 维护评价

**活跃维护**。该插件近期（2026年5月）有密集的更新活动，内容涵盖：
-   **编译修复**：解决编译器警告，提升代码可移植性。
-   **功能更新**：更新关键的第三方库（TechSoft）和内部缓存版本。
-   **兼容性增强**：主动适配新版 CAD 软件（Alias 2027），表明其跟随着上游软件生态在积极维护。
-   作为 **Enterprise** 分类下的插件，属于 Epic 官方支持的商业工具链的一部分，长期维护有保障。

该插件是工业/汽车设计领域使用 Unreal Engine 进行实时可视化的关键基础设施。虽然其默认不启用，但对于有相关需求的项目来说，是经过充分验证和持续维护的可靠选择。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- 测试用例：此插件的主要测试逻辑可能集成在 Datasmith 的整体测试套件或企业级项目中，插件目录内未发现独立的测试文件。