# Datasmith CAD Importer

> Collection of tools to work with CAD files.

| 属性 | 值 |
|---|---|
| 中文名 | CAD 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CADInterfaces` (Runtime), `CADKernelSurface` (Runtime), `CADLibrary` (Runtime), `CADTools` (Runtime), `DatasmithCADTranslator` (Runtime), `DatasmithDispatcher` (Runtime), `DatasmithOpenNurbsTranslator` (Runtime), `DatasmithPLMXMLTranslator` (Runtime), `DatasmithWireTranslator` (Runtime), `ParametricSurface` (Runtime), `ParametricSurfaceExtension` (Runtime), `WireInterface2020` (Runtime), `WireInterface2021_3` (Runtime), `WireInterface2022` (Runtime), `WireInterface2022_1` (Runtime), `WireInterface2022_2` (Runtime), `WireInterface2023_0` (Runtime), `WireInterface2023_1` (Runtime), `WireInterface2024_1` (Runtime), `WireInterface2025_0` (Runtime), `WireInterface2026_0` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

## 用途

该插件是 **Datasmith CAD 导入流水线**的核心组件，专门用于将各种专业 CAD（计算机辅助设计）软件生成的复杂文件格式（如 .wire、.step、.iges 等）转换并导入到 Unreal Engine 中。

与通用的网格文件（如 FBX）不同，CAD 文件通常包含**精确的几何体（B-Rep）**、**参数化曲面**和**高级材质信息**。此插件的主要功能是：

1.  **解析与转换**：解析不同 CAD 软件的私有数据结构（如 Alias 的 .wire 文件），并将其转换为 UE 可以理解的中间格式。
2.  **曲面细分（Tessellation）**：将精确的参数化曲面转换为适用于实时渲染的三角形网格。这个过程可以控制精度，平衡模型细节与性能。
3.  **材质映射**：读取 CAD 文件中的材质和着色器信息（如 Blinn、Phong、Lambert 模型），并将其转换为 Unreal Engine 的 PBR（物理基础渲染）材质。
4.  **结构保持**：尽可能保留原始 CAD 文件中的层级结构（图层、组），并将其映射为 UE 中的 Actor 树形结构。

**为什么需要这个插件？** 工业设计、建筑和制造行业的工作流程通常始于 CAD 软件。要将这些设计实时可视化或进行虚拟评审，就必须有一个可靠的工具将庞大的 CAD 模型高效、保真地导入到游戏引擎中。此插件就是 Epic Games 为此目的提供的专业解决方案。

## 使用场景

- **工业设计与产品可视化**：你使用 Alias、CATIA、NX 等软件设计了一款汽车或消费电子产品，需要将精确的 CAD 模型导入 UE 中创建产品配置器或交互式 3D 展示。
- **建筑、工程与施工 (AEC)**：你拥有 Revit 或其他 BIM 软件生成的建筑模型，需要将其导入 UE 以制作建筑漫游或施工流程可视化。
- **虚拟样机评审**：工程团队需要在 VR 环境中评审大型、复杂的装配体（如飞机引擎、工厂设备），并需要保留原始 CAD 的精确几何和结构信息。

## 蓝图用法

此插件主要提供**运行时数据转换**功能，其核心 API 主要面向 C++，用于在导入流程中被调用。在蓝图层面，你通常不直接使用此插件的函数，而是通过 **Datasmith 导入器** 的界面或通过 Datasmith 导入蓝图节点来使用其底层功能。

### 核心节点

由于该插件的核心是底层转换器，没有直接暴露大量 `BlueprintCallable` 节点。其工作流程是集成在 Datasmith 导入管线中的。主要的可交互蓝图节点来自 Datasmith 主模块，例如 `FDatasmithImporter`。

## C++ 用法

此插件的 API 主要用于扩展或自定义 CAD 文件的导入过程。开发者可以创建自定义的转换器来支持新的 CAD 格式。

### 头文件引入

要使用 WireInterface（例如处理 Alias .wire 文件），你需要包含：

```cpp
#include "WireInterfaceModule.h"
```

### 基本用法

以下是如何使用 `FWireTranslatorImpl`（`WireInterface2021_3` 模块的核心类）的基本流程，展示了如何将 .wire 文件加载到 Datasmith 场景中。

```cpp
// 假设已包含必要头文件
#include "WireInterfaceModule.h"
#include "IWireInterface.h"
#include "WireInterfaceImpl.h"

using namespace UE_DATASMITHWIRETRANSLATOR_NAMESPACE;

bool ImportWireFile(const FString& WireFilePath, const FString& OutputPath, TSharedPtr<IDatasmithScene>& OutScene)
{
    // 1. 创建 Wire 转译器实例
    TUniquePtr<IWireInterface> WireTranslator = MakeUnique<FWireTranslatorImpl>();

    // 2. 设置导入选项（可选）
    FWireSettings ImportSettings;
    // ImportSettings.SomeOption = Value;
    WireTranslator->SetImportSettings(ImportSettings);
    WireTranslator->SetOutputPath(OutputPath);

    // 3. 初始化转译器，指向 .wire 文件
    if (!WireTranslator->Initialize(*WireFilePath))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to initialize Wire Translator for file: %s"), *WireFilePath);
        return false;
    }

    // 4. 创建一个空的 Datasmith 场景
    TSharedRef<IDatasmithScene> NewScene = FDatasmithSceneFactory::CreateScene(*FPaths::GetBaseFilename(WireFilePath));

    // 5. 加载并解析 .wire 文件，将内容填充到场景中
    if (!WireTranslator->Load(NewScene))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to load .wire file into Datasmith scene."));
        return false;
    }

    // 6. 成功，返回构建好的场景
    OutScene = NewScene;
    return true;
}
```

*（代码示例基于 `Private/WireInterfaceImpl.h` 中的 `FWireTranslatorImpl` 类）*

### 进阶用法：获取网格数据

在某些情况下，你可能需要直接获取解析后的网格数据（`FMeshDescription`），而不是完整的 Datasmith 场景。

```cpp
#include "WireInterfaceImpl.h"
#include "MeshDescription.h"
#include "DatasmithMesh.h"

using namespace UE_DATASMITHWIRETRANSLATOR_NAMESPACE;

// 假设已经有一个已初始化的 FWireTranslatorImpl 实例 (WireTranslator)
// 并且已知一个有效的 MeshElement (例如从 Load 过程中获取)
bool GetMeshPayloadForElement(FWireTranslatorImpl* WireTranslator, const TSharedPtr<IDatasmithMeshElement>& MeshElement, FDatasmithMeshElementPayload& OutPayload)
{
    FDatasmithTessellationOptions TessOptions;
    // TessOptions参数可以根据需要设置

    // 调用核心方法获取网格数据
    return WireTranslator->LoadStaticMesh(MeshElement, OutPayload, TessOptions);
}
```

*（代码示例基于 `Private/WireInterfaceImpl.h` 中的 `LoadStaticMesh` 方法）*

## Demo 示例

由于此插件是深度集成的工业级转换器，一个完整的、可编译的最小示例会非常庞大且依赖众多第三方 CAD 库（如 TechSoft, OpenNurbs）。通常，开发者是通过扩展或调试 Datasmith 导入流程来使用它，而不是创建独立的示例。

一个概念性的使用场景是：你正在开发一个需要支持 `.wire` 文件的自定义导入器。你会继承或使用 `IWireInterface`，并如上面“C++ 用法”部分所示进行调用。

## 模块依赖

使用此插件的特定模块（如 `WireInterface2021_3`）需要依赖其底层的支持库。从模块名称和常见依赖推断，主要依赖如下：

| 模块 | 用途 |
|---|---|
| `TechSoft` | 提供 A3DSDK，用于解析 STEP、IGES 等主流 CAD 数据交换格式。 |
| `OpenNurbs6` | 提供 OpenNurbs 库，用于解析 Rhino 3DM 文件格式。 |
| `DatasmithCore` | 提供 Datasmith 的核心数据结构和场景工厂。 |
| `CADLibrary` | 提供 CAD 模型转换的通用工具类和接口。 |
| `MeshDescription` | 提供网格数据的描述和处理。 |

**注意**：你的 `Build.cs` 文件中需要链接这些模块才能成功编译使用了此插件功能的代码。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下，双精度常量向单精度转换时产生的编译器警告。 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | 增加逻辑，确保即使安装了 Alias 2027，Wire 转译器也能正常工作。 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 将 TechSoft 库更新至 2026.3 版本。 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新了 Datasmith CAD 缓存的版本。 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 使函数类型转换警告在 MSVC 和 Clang 编译器间保持可移植性。 |

### 维护评价

**活跃维护**。该插件（或其关键子模块）在最近几个月内（截至示例日期）仍在持续进行更新。更新内容包括：

1.  **兼容性维护**：修复编译警告、确保与新版 CAD 软件（Alias 2027）的兼容性。
2.  **依赖库更新**：升级第三方库（TechSoft）至最新版本，以获取新格式支持或性能改进。
3.  **跨平台与构建改进**：关注代码在不同编译器（MSVC/Clang）下的可移植性。

该插件作为 Epic Games 的官方企业级解决方案，是 Datasmith 生态系统的重要组成部分，预计会长期得到支持。**推荐使用**，特别是对于有专业 CAD 文件导入需求的工业可视化项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)