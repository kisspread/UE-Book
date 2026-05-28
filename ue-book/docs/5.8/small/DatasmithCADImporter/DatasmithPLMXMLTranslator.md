# Datasmith CAD Importer

> Collection of tools to work with CAD files.

| 属性 | 值 |
|---|---|
| 中文名 | CAD文件导入工具 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CADInterfaces` (Runtime), `CADKernelSurface` (Runtime), `CADLibrary` (Runtime), `CADTools` (Runtime), `DatasmithCADTranslator` (Runtime), `DatasmithDispatcher` (Runtime), `DatasmithOpenNurbsTranslator` (Runtime), `DatasmithPLMXMLTranslator` (Runtime), `DatasmithWireTranslator` (Runtime), `ParametricSurface` (Runtime), `ParametricSurfaceExtension` (Runtime), `WireInterface2020` (Runtime), `WireInterface2021_3` (Runtime), `WireInterface2022` (Runtime), `WireInterface2022_1` (Runtime), `WireInterface2022_2` (Runtime), `WireInterface2023_0` (Runtime), `WireInterface2023_1` (Runtime), `WireInterface2024_1` (Runtime), `WireInterface2025_0` (Runtime), `WireInterface2026_0` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

## 用途

该插件是 Epic Games 开发的一套企业级 CAD 文件导入工具集。它并非一个单一的导入器，而是一个**模块化框架**，用于支持各种 CAD 文件格式（如 CATIA, NX, SolidWorks, Rhino, PLM XML 等）的转换和导入。其核心价值在于：

1.  **统一转换层**：通过 `DatasmithCADTranslator` 模块，将不同格式的 CAD 文件转换为 Datasmith 可理解的中间格式，再由 Datasmith 管线导入到 Unreal Engine。
2.  **几何处理**：包含 `CADKernelSurface`, `ParametricSurface` 等模块，负责处理 CAD 软件中常见的参数化曲面、B-Rep 等高级几何数据，并将其转换为 UE 可使用的网格（Mesh）。
3.  **数据接口**：`CADInterfaces` 和 `WireInterface` 等模块封装了与特定 CAD 软件内核（如 TechSoft, Alias）的交互接口。
4.  **分布式处理**：`DatasmithDispatcher` 模块支持将复杂的 CAD 模型转换任务分发到多个工作进程（或机器），以提升大型模型的导入效率。

简单来说，这个插件解决了将**复杂、高精度的工业 CAD 模型**高效、准确地导入到 Unreal Engine 进行可视化、仿真或培训应用的问题。它允许开发者在 UE 中直接使用来自工程团队的原始 CAD 数据，而无需先在其他 DCC 软件中进行手动转换和拓扑优化。

## 使用场景

-   你是一名汽车或航空领域的工程师，需要在 Unreal Engine 中创建一辆新车的数字孪生模型，而原始数据是 CATIA 或 NX 格式 → 使用此插件直接导入 CAD 文件。
-   你正在为大型工厂或建筑项目制作交互式培训模拟器，需要导入 Revit 或 SolidWorks 设计的精确设备模型 → 使用此插件，并可能利用其分布式处理能力加速大型装配体的导入。
-   你是一名技术美术，需要将来自不同 CAD 软件（如 Rhino, Alias）的工业设计模型统一导入 UE，并保持其参数化曲面特征 → 使用此插件，它内置了对不同格式的专用翻译器（`DatasmithOpenNurbsTranslator`, `DatasmithWireTranslator`）。
-   你需要在运行时动态加载 CAD 数据，或对导入的模型进行拓扑优化（如减面） → 该插件提供了 `LoadStaticMesh` 等运行时接口，以及 `FDatasmithTessellationOptions` 来控制网格生成的质量。

## 蓝图用法

该插件主要通过 **Datasmith 导入流程** 使用，在蓝图中直接暴露的节点有限。其核心功能在编辑器导入时自动调用。以下是通过模块公开接口可能进行的操作：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IDatasmithPlmXmlTranslatorModule::Get()` | 获取 PLMXML 翻译器模块的单例，用于检查其可用性或进行高级配置（通常由编辑器自动调用） | `IDatasmithPlmXmlTranslatorModule` |

**注意**：更常见的用法是通过 Datasmith 的标准导入界面（如“导入”按钮或 `UDatasmithImportFactory`）来使用此插件，蓝图中通常不需要直接与这些模块交互。

## C++ 用法

### 头文件引入

要使用特定翻译器（如 PLMXML），你需要包含其模块头文件：

```cpp
#include "DatasmithPlmXmlTranslatorModule.h"
```

### 基本用法

虽然插件通常由编辑器自动调用，但你可以在 C++ 中直接使用其翻译器接口进行编程导入。以下示例展示了如何检查一个翻译器模块是否可用（基于提供的头文件）。

```cpp
// 来源: Private/DatasmithPlmXmlTranslator.h 的简化使用
// 检查 DatasmithPlmXmlTranslator 模块是否已加载
if (IDatasmithPlmXmlTranslatorModule::IsAvailable())
{
    // 获取模块引用，可以用于进一步的操作（如获取其内部翻译器实例）
    IDatasmithPlmXmlTranslatorModule& PlmXmlModule = IDatasmithPlmXmlTranslatorModule::Get();
    UE_LOG(LogTemp, Log, TEXT("PLMXML Translator Module is available."));
}
else
{
    UE_LOG(LogTemp, Warning, TEXT("PLMXML Translator Module is not loaded. Ensure the DatasmithCADImporter plugin is enabled."));
}
```

### 进阶用法

在插件内部，`FDatasmithPlmXmlTranslator` 类展示了如何通过 `IDatasmithTranslator` 接口实现一个完整的文件导入流程。以下是其生命周期的关键步骤：

1.  **初始化**：调用 `Initialize` 设置翻译器的能力（支持哪些文件格式）。
2.  **加载场景**：调用 `LoadScene` 解析文件（如 PLM XML 文件），将其内容转换为 `IDatasmithScene` 对象。
3.  **加载网格**：当场景中的网格元素被请求时，调用 `LoadStaticMesh` 来实际生成网格数据（`FDatasmithMeshElementPayload`），这个过程会利用 `FDatasmithPlmXmlImporter` 和内部的 `FPlmXmlMeshLoader`。
4.  **获取/设置选项**：通过 `GetSceneImportOptions` 和 `SetSceneImportOptions` 来配置细分曲面的质量（`UDatasmithCommonTessellationOptions`）等参数。
5.  **卸载**：调用 `UnloadScene` 释放资源。

## Demo 示例

以下是一个简化的示例，演示如何在插件模块内部注册并使用一个自定义翻译器。实际使用中，翻译器的注册和调用由 Datasmith 核心系统管理。

```cpp
// MyCustomTranslatorModule.h
#pragma once
#include "Modules/ModuleManager.h"

class IMyCustomTranslatorModule : public IModuleInterface
{
public:
    static inline const TCHAR* ModuleName = TEXT("MyCustomTranslatorModule");
    static IMyCustomTranslatorModule& Get();
    static bool IsAvailable();
};

// MyCustomTranslatorModule.cpp
#include "MyCustomTranslatorModule.h"

IMyCustomTranslatorModule& IMyCustomTranslatorModule::Get()
{
    return FModuleManager::LoadModuleChecked<IMyCustomTranslatorModule>(ModuleName);
}

bool IMyCustomTranslatorModule::IsAvailable()
{
    return FModuleManager::Get().IsModuleLoaded(ModuleName);
}

// 在你的 .uplugin 中注册该模块，并在模块启动时向 Datasmith 注册你的自定义翻译器。
// 具体实现需参照 Datasmith 的扩展文档。
```

## 模块依赖

此插件的模块依赖高度分散，每个翻译器模块依赖其对应的外部 CAD 内核库。以下是一些**关键的、非标准**的依赖：

| 模块 | 用途 |
|---|---|
| `TechSoft` (外部库) | 由 `CADInterfaces` 模块依赖，用于支持多种主流 CAD 格式（如 CATIA, NX, STEP, IGES 等）的核心转换库。 |
| `OpenNurbs6` (外部库) | 由 `DatasmithOpenNurbsTranslator` 模块依赖，用于支持 Rhino 3DM 文件格式的解析。 |

**注意**：这些依赖项通常是预编译的二进制库（如 .lib, .dll），在插件的 `Source` 目录或第三方目录下提供。普通用户不需要直接编译这些库，但需要确保它们在运行时可用。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下将双精度常量截断为浮点数时产生的编译警告。 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | 增加了逻辑，使 Wire 翻译器在安装了 Alias 2027 的环境下也能正常工作。 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 将 TechSoft 库更新至 2026.3 版本。 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新了 DatasmithCAD 缓存版本。 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 使函数类型转换警告在 MSVC 和 Clang 编译器之间可移植。 |

### 维护评价

-   **活跃维护**：该插件在最近（2026年5月）仍有**频繁且实质性**的更新，包括底层CAD内核库（TechSoft, Alias）的兼容性更新和编译修复，表明 Epic Games 正在**积极维护**。
-   **企业级插件**：作为 `Engine/Plugins/Enterprise` 目录下的插件，它面向专业用户，更新通常与下游CAD软件的新版本（如Alias 2027）保持同步。
-   **默认禁用**：由于其较大的体积和特定的使用场景，插件默认未启用，需要用户手动在插件列表中激活。
-   **推荐使用**：对于有工业CAD数据导入需求的项目，**强烈推荐**使用此插件。它是官方提供的、最完整和稳定的CAD导入解决方案。建议关注其更新日志，特别是与目标CAD软件版本相关的更新。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
-   [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
-   [测试用例]（由于是企业级插件，测试用例可能不公开，或位于内部引擎测试目录中，无法提供公开链接）