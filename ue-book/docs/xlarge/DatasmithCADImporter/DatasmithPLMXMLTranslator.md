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

DatasmithCADImporter 是一个企业级插件，其核心功能是将各种工业标准的 CAD（计算机辅助设计）文件格式转换为 Unreal Engine 可用的资产。它不仅仅是一个简单的文件导入器，而是一个完整的 CAD 数据处理工具集。它解决了将复杂的、参数化的 CAD 模型（如来自 CATIA, NX, SolidWorks, STEP, IGES 等）转换为适合实时渲染和交互的三角网格（Mesh）的难题，同时尽可能保留原始模型的结构、材质和元数据。

该插件通过一系列“翻译器”（Translator）模块来支持不同的 CAD 格式，并通过 CAD 库和工具模块来处理几何计算、曲面细分和网格优化。它是 Datasmith 工作流中处理工程和制造业 CAD 数据的关键组件。

## 使用场景

- **建筑、工程与施工 (AEC)**：导入来自 Revit, ArchiCAD 或其他 BIM 软件的模型，用于建筑可视化、虚拟漫游或施工模拟。
- **汽车与交通运输**：导入来自 CATIA, NX, Alias 等软件的汽车、飞机或船舶的复杂曲面模型，用于设计评审、虚拟展示或驾驶模拟器。
- **产品设计与制造**：导入来自 SolidWorks, Inventor, Creo 等软件的机械零件和装配体，用于产品配置器、维护手册或数字孪生。
- **通用 CAD 数据交换**：当需要将 STEP (.stp), IGES (.igs), PLMXML 等中性格式的 CAD 数据引入 UE 进行进一步开发时。

## 蓝图用法

该插件主要作为 Datasmith 导入管线的后端运行，其核心翻译逻辑通常不直接暴露为蓝图节点。用户主要通过 Datasmith 导入器 UI 或 Datasmith 场景导入蓝图节点来使用其功能。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Import Datasmith Scene` | 通用的 Datasmith 场景导入节点，会根据文件扩展名自动调用对应的 CAD 翻译器。 | `UDatasmithImportFactory` |

### 使用示例（蓝图描述）

1.  在蓝图中，使用 `Import Datasmith Scene` 节点。
2.  将 `.catpart`, `.step`, `.plmxml` 等 CAD 文件路径连接到 `File Path` 输入引脚。
3.  设置 `Options`（可选），如导入缩放、材质处理等。
4.  执行该节点，引擎将自动调用 `DatasmithCADTranslator` 及其子模块（如 `DatasmithPLMXMLTranslator`）来处理文件，并将生成的静态网格体、材质等资产导入到指定内容路径。

## C++ 用法

对于需要深度集成或自定义 CAD 导入流程的开发者，可以在 C++ 中直接调用翻译器模块。

### 头文件引入

```cpp
#include "DatasmithPlmXmlTranslatorModule.h"
// 其他翻译器模块的头文件，如 DatasmithOpenNurbsTranslatorModule.h
```

### 基本用法

以下示例展示了如何检查并加载 PLMXML 翻译器模块。

```cpp
// 来源: Engine/Plugins/Enterprise/DatasmithCADImporter/Source/DatasmithPLMXMLTranslator/Public/DatasmithPlmXmlTranslatorModule.h
if (IDatasmithPlmXmlTranslatorModule::IsAvailable())
{
    IDatasmithPlmXmlTranslatorModule& PlmXmlModule = IDatasmithPlmXmlTranslatorModule::Get();
    // 模块已加载，可以进行后续操作，例如注册自定义的翻译器扩展。
    // 注意：实际的翻译过程通常由 Datasmith 主模块协调，此处仅为模块访问示例。
}
```

### 进阶用法

更复杂的用法涉及直接使用 `CADLibrary` 或 `CADTools` 中的几何处理工具，但这通常需要深入了解 CAD 数据结构和 UE 的网格构建流程。大多数情况下，通过 Datasmith 的标准导入接口即可满足需求。

## Demo 示例

一个最小的 C++ 示例，展示如何确保 CAD 翻译器模块可用。

```cpp
// MyCADImporter.h
#pragma once
#include "CoreMinimal.h"

class FMyCADImporter
{
public:
    static bool InitializeCADSupport();
};
```

```cpp
// MyCADImporter.cpp
#include "MyCADImporter.h"
#include "DatasmithPlmXmlTranslatorModule.h" // 引入特定翻译器模块

bool FMyCADImporter::InitializeCADSupport()
{
    // 检查 PLMXML 翻译器是否可用
    if (!IDatasmithPlmXmlTranslatorModule::IsAvailable())
    {
        UE_LOG(LogTemp, Warning, TEXT("Datasmith PLMXML Translator module is not loaded."));
        return false;
    }

    // 模块可用，可以安全地获取引用
    IDatasmithPlmXmlTranslatorModule& Module = IDatasmithPlmXmlTranslatorModule::Get();
    UE_LOG(LogTemp, Log, TEXT("Datasmith PLMXML Translator module is ready."));

    // 在实际应用中，你可能需要在这里注册自定义的资产处理器或材质映射。
    // 但核心的文件解析和网格生成由模块内部处理。

    return true;
}
```

## 模块依赖

该插件的模块依赖关系复杂，且大部分是内部模块间的依赖。对于插件使用者（即在自己的项目模块中依赖此插件），主要需要依赖其顶层翻译器模块。

| 模块 | 用途 |
|---|---|
| `TechSoft` | CADInterfaces 模块的依赖，用于提供底层的 CAD 文件读取能力（如来自 Tech Soft 3D 的 HOOPS Exchange）。 |
| `OpenNurbs6` | DatasmithOpenNurbsTranslator 模块的依赖，用于解析 Rhino 的 .3dm 文件格式。 |
| `DatasmithCore` | 所有翻译器模块的基础，提供 Datasmith 场景元素、材质等核心数据结构。 |

**注意**：`TechSoft` 和 `OpenNurbs6` 是第三方库，其源码可能不包含在 UE 公开仓库中。使用这些翻译器功能需要确保相应的库文件可用。

## 维护状态

### 近期更新

```
- 7c3a01920766 #jira UE-188376 Fix import PlmXml
- 325d472511b2 Switch mesher in case of failure #jira UE-186713 #rb jeanluc.corenthin #preflight 6478514b3a1270a6fd13bb3c
- a7f401a01a17 CAD Qualifier improvements #rb none #preflight 64215cd27a393e211ad2c192
```

- `7c3a01920766`: 修复了 PLMXML 文件导入的具体问题。
- `325d472511b2`: 在网格生成失败时切换网格生成器，提高了导入的鲁棒性。
- `a7f401a01a17`: 改进了 CAD 资产的分类（Qualifier）功能。

### 维护评价

该插件创建于 2019 年，属于企业级功能，维护状态**活跃**。从近期的 git 提交记录可以看出，Epic 团队仍在持续修复 bug（如 PLMXML 导入问题）并改进核心功能（如网格生成器切换、资产分类）。作为 Datasmith 套件的关键组成部分，它随着 UE 版本的更新而持续迭代，以支持更新的 CAD 软件版本（从 WireInterface 模块的版本号可以看出）。

**推荐使用**：对于需要将工业 CAD 数据引入 Unreal Engine 的项目，尤其是建筑、汽车和产品设计领域，此插件是官方推荐且持续维护的解决方案。需要注意的是，它默认是禁用的，需要在插件列表中手动启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithCADImporter/Tests)