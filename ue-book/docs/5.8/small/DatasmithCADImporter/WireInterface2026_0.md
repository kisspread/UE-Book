# Datasmith CAD Importer

> Collection of tools to work with CAD files.

| 属性 | 值 |
|---|---|
| 中文名 | CAD 文件导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CADInterfaces` (Runtime), `CADKernelSurface` (Runtime), `CADLibrary` (Runtime), `CADTools` (Runtime), `DatasmithCADTranslator` (Runtime), `DatasmithDispatcher` (Runtime), `DatasmithOpenNurbsTranslator` (Runtime), `DatasmithPLMXMLTranslator` (Runtime), `DatasmithWireTranslator` (Runtime), `ParametricSurface` (Runtime), `ParametricSurfaceExtension` (Runtime), `WireInterface2020` (Runtime), `WireInterface2021_3` (Runtime), `WireInterface2022` (Runtime), `WireInterface2022_1` (Runtime), `WireInterface2022_2` (Runtime), `WireInterface2023_0` (Runtime), `WireInterface2023_1` (Runtime), `WireInterface2024_1` (Runtime), `WireInterface2025_0` (Runtime), `WireInterface2026_0` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 🆕（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

## 用途

该插件并非一个通用的 CAD 文件导入器，而是一个**专用于 Autodesk Alias 软件 .wire 格式文件的高级解析与转换系统**。它的核心功能是深度解析 Alias 的场景文件（.wire），提取其中复杂的几何体（如 NURBS 曲面、贝塞尔曲面、多边形网格）、材质（着色器）、场景层级结构以及变换信息，并将其转换为 Unreal Engine 中的 `IDatasmithScene` 表示。

最终目标是将 Alias 中创建的、以参数化 NURBS 曲面为主的高精度工业设计模型，转换为 UE 可用的网格体（`MeshDescription`）和材质资产，支持在引擎中进行实时渲染、虚拟评审和可视化开发。它为汽车、工业设计等领域的设计师将 Alias 设计模型无缝引入 UE 的实时环境提供了关键技术支持。

## 使用场景

- **汽车设计可视化**：在 Unreal Engine 中实时查看和评审由 Alias 设计的汽车 A 级曲面模型。
- **工业设计原型**：将 Alias 中设计的复杂产品外观模型导入 UE，用于制作产品发布动画或交互式配置器。
- **与 UE 高级功能结合**：将 Alias 的 NURBS 曲面数据转换为高质量网格后，可利用 UE 的 Lumen、Nanite、Niagara 等系统进行渲染和特效制作。

## 蓝图用法

该插件主要通过编辑器集成提供功能，无特定蓝图节点。用户主要通过 Datasmith 导入流程（文件 > 导入到关卡）来使用该插件处理 .wire 文件。插件的核心逻辑在 C++ 运行时模块中实现。

## C++ 用法

### 头文件引入

该插件的核心是 `WireInterface` 模块。要使用其转换功能，通常需要引入相应的头文件：

```cpp
#include "WireInterfaceModule.h"
#include "WireInterfaceImpl.h"
#include "OpenModelUtils.h"
```

### 基本用法

核心的 `FWireTranslatorImpl` 类实现了 `IWireInterface` 接口，负责整个 .wire 文件的解析和场景转换流程。以下是其核心接口的说明：

```cpp
// 实例化 Wire 文件解析器
UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FWireTranslatorImpl Translator;

// 初始化解析器，传入 .wire 文件的完整路径
bool bInitialized = Translator.Initialize(TEXT("C:/Path/To/Your/AliasModel.wire"));

if (bInitialized)
{
    // 创建一个 Datasmith 场景对象来存储转换结果
    TSharedPtr<IDatasmithScene> Scene = FDatasmithSceneFactory::CreateScene(TEXT("AliasImportScene"));
    
    // 执行加载与解析，将 .wire 文件内容转换为 IDatasmithScene
    bool bLoaded = Translator.Load(Scene);

    // 此时，`Scene` 对象中包含了从 .wire 文件解析出的所有 Actor、Mesh、Material 等元素
    // 后续可以使用 Datasmith 的导入管线将此 Scene 应用到 Unreal Engine 中
}

// 通过模块单例访问转换器（更常见的用法）
if (FDatasmithWireTranslatorModule::IsAvailable())
{
    auto& WireModule = FDatasmithWireTranslatorModule::Get();
    // WireModule 可用于管理临时目录等资源
    FString TempDir = WireModule.GetTempDir();
}
```

*（参考源码: `Public/WireInterfaceModule.h`, `Private/WireInterfaceImpl.h`）*

### 进阶用法

该插件内部包含两套主要的几何转换后端：
1.  **CADKernel 后端** (`FAliasModelToCADKernelConverter`)：将 Alias 的 `AlDagNode` 几何体转换为 CADKernel 内部表示 (`FTopologicalFace`, `FTopologicalEdge` 等)，然后进行高精度细分曲面和三角化。
2.  **TechSoft 后端** (`FAliasModelToTechSoftConverter`)：将 Alias 几何体转换为 TechSoft HOOPS Exchange 的表示 (`A3DTopoFace`, `A3DTopoCoEdge` 等)。

你可以直接调用这些转换器来处理单个几何节点，但通常插件的导入管线（`DatasmithCADTranslator` 模块）会统一调度它们。

```cpp
// 示例：手动处理单个几何节点（概念性代码）
using namespace UE_DATASMITHWIRETRANSLATOR_NAMESPACE;

// ... 假设已从 .wire 文件获取到一个 AlDagNode 指针 ...
FAlDagNodePtr MyDagNode(RawAlDagNode);

// 1. 使用 CADKernel 转换器
CADLibrary::FImportParameters ImportParams;
FAliasModelToCADKernelConverter CADKernelConverter(TessellationOptions, ImportParams);
CADKernelConverter.AddBRep(MyDagNode, Color, EAliasObjectReference::LocalReference);
// ... 接下来可调用 RepairTopology 和 Tessellate 获取 MeshDescription ...

// 2. 使用 TechSoft 转换器
FAliasModelToTechSoftConverter TechSoftConverter(ImportParams);
TechSoftConverter.AddBRep(MyDagNode, Color, EAliasObjectReference::LocalReference);
```

*（参考源码: `Private/AliasModelToCADKernelConverter.h`, `Private/AliasModelToTechSoftConverter.h`）*

## Demo 示例

一个完整的 C++ 示例，展示如何通过 `WireInterface` 模块启动一个 .wire 文件的转换过程，并获取网格数据。此示例更贴近插件内部管线的用法，通常由 Datasmith 导入器框架调用。

**MyWireProcessor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "WireInterfaceModule.h"
#include "WireInterfaceImpl.h"

class FMyWireProcessor
{
public:
    /** 处理一个 .wire 文件并提取第一个网格体的 MeshDescription */
    TOptional<FMeshDescription> ProcessWireFile(const FString& WireFilePath);

private:
    UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FWireTranslatorImpl WireTranslator;
};
```

**MyWireProcessor.cpp**
```cpp
#include "MyWireProcessor.h"
#include "DatasmithSceneFactory.h"
#include "MeshDescription.h"
#include "StaticMeshAttributes.h"

TOptional<FMeshDescription> FMyWireProcessor::ProcessWireFile(const FString& WireFilePath)
{
    // 1. 初始化解析器
    if (!WireTranslator.Initialize(*WireFilePath))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to initialize wire translator for file: %s"), *WireFilePath);
        return TOptional<FMeshDescription>();
    }

    // 2. 创建临时场景
    TSharedPtr<IDatasmithScene> TempScene = FDatasmithSceneFactory::CreateScene(TEXT("TempAliasScene"));
    TempScene->SetHost(TEXT("MyProcessor"));

    // 3. 执行加载，解析 .wire 文件
    if (!WireTranslator.Load(TempScene))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to load wire file: %s"), *WireFilePath);
        return TOptional<FMeshDescription>();
    }

    // 4. 从转换结果中查找第一个网格元素
    TSharedPtr<IDatasmithMeshElement> FirstMeshElement;
    for (int32 i = 0; i < TempScene->GetMeshesCount(); ++i)
    {
        FirstMeshElement = TempScene->GetMesh(i);
        if (FirstMeshElement.IsValid())
        {
            break;
        }
    }

    if (!FirstMeshElement.IsValid())
    {
        UE_LOG(LogTemp, Warning, TEXT("No mesh found in the wire file."));
        return TOptional<FMeshDescription>();
    }

    // 5. 获取该网格的详细负载（包括 MeshDescription）
    // 注意：此过程会触发实际的细分和三角化，可能较慢
    FDatasmithMeshElementPayload MeshPayload;
    FDatasmithTessellationOptions TessOptions;
    WireTranslator.LoadStaticMesh(FirstMeshElement, MeshPayload, TessOptions);

    if (MeshPayload.GetMeshDescription().IsValid())
    {
        UE_LOG(LogTemp, Log, TEXT("Successfully extracted mesh: %s"), *FirstMeshElement->GetName());
        return *MeshPayload.GetMeshDescription();
    }

    return TOptional<FMeshDescription>();
}
```

## 模块依赖

该插件依赖多个非标准的外部和内部模块，这是其能处理复杂 CAD 格式的关键。

| 模块 | 用途 |
|---|---|
| `TechSoft` | 提供对多种工业 CAD 格式（如 STEP, IGES, CATIA）的底层读写支持，本插件中主要用于 TechSoft 后端转换。 |
| `CADKernel` | Epic 自研的、用于表示和操作 CAD 核心数据（曲面、拓扑边等）的库，是插件中高精度几何转换的核心。 |
| `CADLibrary` | 提供 CAD 转换相关的基础类、接口和工具函数（如 `ICADModelConverter`, `FImportParameters`）。 |
| `DatasmithCore` | Datasmith 框架的核心库，提供 `IDatasmithScene`, `IDatasmithMeshElement` 等基础接口。 |
| `OpenNurbs6` | 用于处理 .3dm (Rhino) 等格式的 NURBS 几何库，由 `DatasmithOpenNurbsTranslator` 模块依赖。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下，双精度常量隐式转换为浮点数产生的编译警告。 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | 增加了兼容性逻辑，使 Wire 转换器在安装了 Alias 2027 版本时也能正常工作。 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 升级了底层依赖 TechSoft 库至 2026.3 版本。 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新了 Datasmith CAD 缓存的版本标识。 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 使函数类型转换警告在 MSVC 和 Clang 编译器下表现一致。 |

### 维护评价

该插件处于**活跃维护**状态。从 Git 历史看，在 2026 年仍有频繁的功能性更新（如支持新版本 Alias、升级依赖库）和编译兼容性修复。作为 Epic 官方支持的 Enterprise 级插件，它随着 Unreal Engine 版本同步更新，并持续适配 Autodesk Alias 软件的新版本。对于需要将 Alias 工作流集成到 Unreal Engine 的汽车与工业设计领域用户，这是一个关键且值得信赖的工具。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)