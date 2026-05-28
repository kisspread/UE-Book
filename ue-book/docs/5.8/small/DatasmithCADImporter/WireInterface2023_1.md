# Datasmith CAD Importer

> Collection of tools to work with CAD files.

| 属性 | 值 |
|---|---|
| 中文名 | Datasmith CAD 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CADInterfaces` (Runtime), `CADKernelSurface` (Runtime), `CADLibrary` (Runtime), `CADTools` (Runtime), `DatasmithCADTranslator` (Runtime), `DatasmithDispatcher` (Runtime), `DatasmithOpenNurbsTranslator` (Runtime), `DatasmithPLMXMLTranslator` (Runtime), `DatasmithWireTranslator` (Runtime), `ParametricSurface` (Runtime), `ParametricSurfaceExtension` (Runtime), `WireInterface2020` (Runtime), `WireInterface2021_3` (Runtime), `WireInterface2022` (Runtime), `WireInterface2022_1` (Runtime), `WireInterface2022_2` (Runtime), `WireInterface2023_0` (Runtime), `WireInterface2023_1` (Runtime), `WireInterface2024_1` (Runtime), `WireInterface2025_0` (Runtime), `WireInterface2026_0` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

## 用途

这个插件是 Unreal Engine 中 Datasmith 技术栈的关键组成部分，专门用于将各种工业 CAD（计算机辅助设计）格式的文件导入到引擎中。它不是一个单一的转换器，而是一个**模块化的导入管线框架**。其核心功能是将结构化的 CAD 模型（包含精确的几何体、层级结构、材质和装配关系）转换为 UE 可以理解的 Datasmith 格式，最终生成静态网格、材质和 Actor 层级。

**`WireInterface2023_1` 模块的具体作用**是提供对 Autodesk Alias ( `.wire` 格式) 文件的转换支持。它实现了 `IWireInterface` 接口，负责解析 Alias 的模型数据（DAG 节点、曲面、壳体、网格等），并将其映射到 Datasmith 的场景元素（`IDatasmithScene`, `IDatasmithActorElement`, `IDatasmithMeshElement` 等）。

## 使用场景

- 你是一名汽车设计师或工业设计师，使用 Autodesk Alias 进行 A 级曲面建模，需要将设计模型实时预览在 Unreal Engine 中进行可视化评审。
- 你的团队使用 Alias 创建产品原型，并需要将其无缝集成到 UE 的虚拟展厅、培训模拟器或数字孪生项目中。
- 你需要批量导入一系列 Alias 文件，并希望保留原始模型的组织结构（图层、组）和材质信息。

## 蓝图用法

该模块主要作为数据导入管线的底层引擎运行，不直接暴露面向设计师的蓝图 API。其功能通过 Datasmith 导入器的通用界面（如 `UDatasmithStaticMeshImportOptions`）间接被调用。开发者通常不直接在蓝图中与此模块交互。

## C++ 用法

此模块是 Datasmith 导入管线的内部组件。核心交互发生在 `FDatasmithWireTranslatorModule` 和 `IWireInterface` 接口层面。

### 头文件引入

```cpp
#include "WireInterfaceModule.h"
#include "WireInterface.h"
```

### 基本用法

从模块获取接口实例并执行导入的基本流程。

```cpp
// 来源：WireInterfaceModule.h
// 1. 获取并检查 Wire 翻译器模块
FDatasmithWireTranslatorModule& WireModule = FDatasmithWireTranslatorModule::Get();
if (!FDatasmithWireTranslatorModule::IsAvailable())
{
    UE_LOG(LogTemp, Error, TEXT("Wire Interface module is not available."));
    return;
}

// 2. 创建一个 IWireInterface 的实例（通常由翻译器工厂内部完成）
// TSharedPtr<IWireInterface> Translator = ... // 通过工厂创建

// 3. 初始化翻译器并设置选项
// Translator->Initialize(TEXT("C:/Path/To/Model.wire"));
// FWireSettings Settings;
// Settings.SomeOption = ...;
// Translator->SetImportSettings(Settings);

// 4. 加载场景（转换过程在此执行）
// TSharedPtr<IDatasmithScene> DatasmithScene = MakeShared<FDatasmithScene>();
// Translator->Load(DatasmithScene);

// 5. 此时，DatasmithScene 中已经填充了从 Alias 文件转换而来的 Actor、Mesh 和 Material 元素。
//    后续流程由通用的 Datasmith 导入器处理，将这些元素实例化为 UE 对象。
```

### 进阶用法

高级开发者可能会研究其内部转换逻辑，特别是材质和几何体的映射方式。

```cpp
// 来源：Private/WireInterfaceImpl.h
// 核心转换逻辑在 FWireTranslatorImpl 中。
// - 模型遍历：TraverseModel() -> TraverseDag() 递归处理 Alias 的 DAG 节点。
// - 几何体处理：根据节点类型（Mesh, Surface, Shell）调用不同的处理函数，如 ProcessGeometryNode(), ProcessBodyNode(), ProcessPatchMesh()。
// - 材质转换：FindOrAddMaterial() 将 Alias 的着色器（AlShader）映射为 Datasmith 的 PBR 材质（IDatasmithUEPbrMaterialElement）。
//   支持 Blinn, Lambert, Phong 等着色模型。
// - 几何体获取：GetMeshDescription* 系列函数从不同的 Alias 几何表示中提取 FMeshDescription 数据。

// 来源：Private/AliasModelToCADKernelConverter.h 和 AliasModelToTechSoftConverter.h
// 模块内部使用两种不同的后端来处理复杂的 B-Rep（边界表示）几何体：
// 1. CADKernel Converter: 使用 UE 内置的 CADKernel 库进行高精度曲面细分。
// 2. TechSoft Converter: 集成第三方 TechSoft 库进行 CAD 数据转换。
// 这些转换器负责将 Alias 的 Trimmed Surface (带修剪边界的曲面) 转换为三角网格。
```

## Demo 示例

一个演示如何通过模块接口启动 Alias 文件导入流程的最小 C++ 示例。

```cpp
// MyAliasImporter.h
#pragma once

#include "CoreMinimal.h"
#include "WireInterfaceModule.h"
#include "WireInterface.h" // 假设这是 IWireInterface 的头文件

class FMyAliasImporter
{
public:
    bool ImportAliasFile(const FString& FilePath);
};
```

```cpp
// MyAliasImporter.cpp
#include "MyAliasImporter.h"
#include "DatasmithScene.h"

bool FMyAliasImporter::ImportAliasFile(const FString& FilePath)
{
    // 1. 检查模块可用性
    if (!FDatasmithWireTranslatorModule::IsAvailable())
    {
        UE_LOG(LogTemp, Error, TEXT("Datasmith Wire Translator module is not loaded."));
        return false;
    }

    // 2. 创建翻译器实例 (注意：实际中可能通过工厂获取，此处为示例)
    // TSharedPtr<IWireInterface> Translator = MakeShared<FWireTranslatorImpl>();

    // 3. 初始化
    // if (!Translator->Initialize(*FilePath))
    // {
    //     UE_LOG(LogTemp, Error, TEXT("Failed to initialize translator for file: %s"), *FilePath);
    //     return false;
    // }

    // 4. 设置导入选项 (可选)
    // FWireSettings ImportSettings;
    // Translator->SetImportSettings(ImportSettings);

    // 5. 加载到 Datasmith 场景
    // TSharedPtr<IDatasmithScene> Scene = MakeShared<FDatasmithScene>();
    // if (!Translator->Load(Scene))
    // {
    //     UE_LOG(LogTemp, Error, TEXT("Failed to load alias file into Datasmith scene."));
    //     return false;
    // }

    // 6. 此时，Scene 对象包含了转换后的数据。
    //    在实际的 Datasmith 导入流程中，会有一个后续步骤来将这个 Scene 对象‘烘焙’到 UE 项目。
    UE_LOG(LogTemp, Log, TEXT("Alias file parsed successfully. Datasmith scene built."));

    return true;
}
```

## 模块依赖

从代码分析推断，使用此模块（或整个插件）需要以下依赖：

| 模块 | 用途 |
|---|---|
| `CADLibrary` | 提供 CAD 模型转换的公共基础库和接口（如 `ICADModelConverter`）。 |
| `DatasmithCore` | Datasmith 的核心库，定义了场景、元素等数据结构（如 `IDatasmithScene`, `IDatasmithMeshElement`）。 |
| `CADInterfaces` | 提供与第三方 CAD 内核（如 TechSoft）的接口。 |
| `TechSoft` | 第三方商业 CAD 数据交换库，用于处理复杂的 B-Rep 几何。 |

*注意：模块依赖关系复杂，实际开发中通常通过 `DatasmithCADImporter` 插件的整体依赖来引入。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下双精度常量截断为浮点数导致的编译警告。 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | 添加逻辑，使 Wire 翻译器在安装了 Alias 2027 的情况下也能工作。 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 更新 TechSoft 库版本至 2026.3。 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新 DatasmithCAD 缓存版本号。 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 使函数类型转换警告在 MSVC 和 Clang 编译器间可移植。 |

### 维护评价

- **活跃维护**：插件创建于 2019 年，但最近一次提交就在 2026 年 5 月，更新非常密集。
- **持续更新**：近期的提交主要集中在兼容性更新（支持新版 Alias 和 TechSoft 库）、编译问题修复和代码质量改进，表明 Epic 仍在积极维护此企业级功能。
- **稳定性**：作为 `EnabledByDefault: false` 的企业插件，其更新通常偏向于稳定性和兼容性，而非新功能。
- **推荐使用**：**强烈推荐**有 CAD 文件（特别是 Alias）导入需求的专业用户或团队使用。它是一个成熟、受到官方持续支持的专业工具链。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- 测试用例：此插件的测试通常集成在 Datasmith 的整体测试套件中，路径可能位于 `Engine/Plugins/Enterprise/Datasmith/DatasmithImporter/Tests/` 或 `Engine/Tests/Datasmith/`。