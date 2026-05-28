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
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

## 用途

该插件是 Epic Games 为工业设计软件（如 Autodesk Alias）创建的 `.wire` 格式文件提供的专用导入器。它的核心功能是作为 Datasmith 框架的一个翻译器模块，负责读取 `.wire` 文件中的复杂 CAD 数据（包括几何体、层级结构、材质/着色器），并将其转换为虚幻引擎的 Datasmith 场景元素（如 `IDatasmithActorElement`, `IDatasmithMeshElement`, `IDatasmithUEPbrMaterialElement`）。它解决了工业设计资产（`.wire`）无缝、高保真地进入虚幻引擎进行渲染、评审和进一步加工的问题。

## 使用场景

-   你在使用 Autodesk Alias 进行汽车或产品的A级曲面设计，完成模型后需要将其导入虚幻引擎进行实时渲染预览、设计评审或创建营销素材。
-   你需要将一个包含复杂曲面、分层和材质信息的 `.wire` 文件，通过 Datasmith Importer 导入虚幻引擎，并希望保留原始的设计结构（如层、组）和材质属性。

## 蓝图用法

该插件主要为 Runtime 翻译器，其核心功能（解析 `.wire` 文件）被集成在 Datasmith 的导入管线中，通常不直接暴露蓝图节点供用户调用。用户通过编辑器中的 Datasmith Import 操作或相关蓝图节点（如 `Import Datasmith Scene`）间接触发其功能。插件内部没有面向蓝图的公开接口。

## C++ 用法

此插件的 C++ 模块主要为 Datasmith 框架内部服务，其核心接口 `IWireInterface` 并不对外公开。使用方通常是 Datasmith 翻译器工厂。下面的代码示例基于其核心实现类，展示其内部工作流程。

### 头文件引入

```cpp
// 引入 WireTranslator 实现头文件
#include "WireInterfaceImpl.h"
```

### 基本用法

该插件的用法通常不直接实例化其翻译器，而是通过 Datasmith 框架自动调度。核心工作流程围绕 `FWireTranslatorImpl` 类展开。

```cpp
// 模拟内部初始化过程 (通常由框架调用)
// 来源: Private/WireInterfaceImpl.h (FWireTranslatorImpl::Initialize)
TSharedPtr<FWireTranslatorImpl> Translator = MakeShared<FWireTranslatorImpl>();
if (Translator->Initialize(TEXT("C:/path/to/model.wire")))
{
    // 设置导入参数
    FWireSettings Settings;
    Translator->SetImportSettings(Settings);
    Translator->SetOutputPath(TEXT("C:/output/"));

    // 加载场景 (这会触发 DAG 遍历和几何体转换)
    TSharedPtr<IDatasmithScene> Scene = MakeShared<IDatasmithScene>();
    bool bLoaded = Translator->Load(Scene);

    // 在某个时刻，加载静态网格体
    FDatasmithMeshElementPayload Payload;
    FDatasmithTessellationOptions TessellationOptions;
    // ... 获取一个 MeshElement ...
    bool bMeshLoaded = Translator->LoadStaticMesh(SomeMeshElement, Payload, TessellationOptions);
}
```

### 进阶用法

更复杂的用法体现在其内部的模型遍历和材质转换逻辑上。例如，它为不同类型的 Alias 着色器（Blinn, Lambert, Phong）创建对应的 PBR 材质。

```cpp
// 概念性代码，展示了处理材质的过程 (来自 Private/WireInterfaceImpl.h 中的方法)
// 假设有一个 AlShader 对象
TAlObjectPtr<AlShader> AliasShader = ...;

// 根据着色器类型，调用不同的方法来填充材质元素
TSharedPtr<IDatasmithUEPbrMaterialElement> MaterialElement = ...;
switch (GetShaderModelType(AliasShader))
{
case EAlShaderModelType::BLINN:
    Translator->AddAlBlinnParameters(AliasShader, MaterialElement);
    break;
case EAlShaderModelType::PHONG:
    Translator->AddAlPhongParameters(AliasShader, MaterialElement);
    break;
// ... 其他类型
}

// 几何体转换依赖于一个 CADModelConverter (如 CADKernel 或 TechSoft)
TSharedPtr<CADLibrary::ICADModelConverter> Converter = Translator->GetModelConverter();
// ... 使用 Converter 进行曲面细分等操作
```

## Demo 示例

此插件为底层翻译器，没有独立的可运行 Demo。其典型应用是通过 Datasmith Importer 导入一个 `.wire` 文件。在 C++ 层面，使用其功能依赖于 Datasmith 框架的调度，无法提供一个最小化的独立编译示例。

## 模块依赖

该插件本身包含许多模块，但用户模块若要使用其功能（通常通过 Datasmith 框架），主要需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `DatasmithCore` | Datasmith 的核心接口和数据结构 |
| `CADLibrary` | CAD 模型转换和网格处理的通用库 |
| `TechSoft` | 用于处理通用 CAD 格式（如 STEP， IGES）的第三方库 |
| `CADKernel` | Epic 的内核曲面细分库 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下 double 常量转换为 float 时产生的编译器警告。 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | 增加逻辑，确保即使安装了 Alias 2027，Wire 翻译器也能正常工作。 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 将第三方库 TechSoft 更新至 2026.3 版本。 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新了 DatasmithCAD 缓存的版本。 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 使函数类型转换警告在 MSVC 和 Clang 编译器之间具有可移植性。 |

### 维护评价

该插件创建于 2019 年，已有约 5 年历史，属于企业级功能插件。从近期（2026年5月）的提交记录看，它仍在**积极维护**中。更新内容包括：修复编译警告、增强对新版 Alias 软件（2027）的兼容性、更新关键依赖库（TechSoft）以及缓存版本更新。这些更新表明 Epic 持续关注其稳定性和对新软件版本的支持。插件默认禁用 (`EnabledByDefault: false`)，表明它面向特定用户群体（使用 Alias 等 CAD 软件的设计师）。总体而言，这是一个功能明确、维护良好的专业工具。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- 测试用例：该插件的测试用例可能位于 `Engine/Tests/` 或企业版测试目录下，具体路径未在提供的信息中。