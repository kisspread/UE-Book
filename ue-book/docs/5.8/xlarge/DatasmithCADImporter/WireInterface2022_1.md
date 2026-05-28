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
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

## 用途

DatasmithCADImporter 是一个插件集合，专门用于处理和导入各种计算机辅助设计（CAD）文件格式到虚幻引擎中。其核心用途是作为工业设计数据（如汽车、建筑、产品原型）与游戏引擎之间的桥梁，将复杂的 CAD 模型（包括 B-Rep 几何、曲面、材质等信息）高效、准确地转换为 UE5 可用的资产（Static Mesh、Material 等）。

该插件通过一系列专用的翻译器模块（如 `DatasmithCADTranslator`, `DatasmithWireTranslator`）和底层几何处理库（如 `CADLibrary`, `CADKernelSurface`），解决了 CAD 软件（如 Alias）产生的 `.wire` 等文件在导入 UE 时面临的几何拓扑复杂性、材质映射和坐标系转换等问题。它使得艺术家和开发者能够在 UE 中直接使用工程级的高质量 CAD 数据。

## 使用场景

-   你是一名汽车可视化或工业设计师，需要在 UE5 中实时渲染使用 Autodesk Alias 设计的汽车外观模型 → 使用 `WireInterface` 系列模块导入 `.wire` 文件。
-   你的项目需要精确导入来自 PLM (产品生命周期管理) 系统的 CAD 数据进行审查或虚拟展示 → 使用 `DatasmithPLMXMLTranslator`。
-   你正在使用其他 CAD 格式（如 STEP, IGES），该插件也提供了相应的转换路径（通过 `DatasmithCADTranslator` 和底层的 TechSoft 库）。

## 蓝图用法

此插件的模块主要为运行时翻译器和底层几何处理库，其核心功能（如场景加载、网格生成）并不直接暴露为蓝图节点。它通常通过 Datasmith 导入流程在幕后工作，用户主要通过编辑器中的“导入”选项或 Datasmith 面板与之交互。对于高级控制，需要通过 C++ 接口调用。

## C++ 用法

### 头文件引入

要使用 Wire 文件翻译功能，主要引入翻译器接口头文件。

```cpp
#include "WireInterface/IWireInterface.h"
```

### 基本用法

使用 `FWireTranslatorImpl` 加载一个 `.wire` 场景文件。此示例展示了初始化和加载场景的基本流程。

*（来源：基于 `WireInterfaceImpl.h` 中类的接口推断）*

```cpp
#include "WireInterface/IWireInterface.h"
#include "WireInterfaceModule.h"

void ImportWireFile(const FString& WireFilePath, const FString& OutputPath)
{
    // 1. 获取或创建 Wire Translator 实例
    // 注意：实际中可能通过模块获取工厂方法
    UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FWireTranslatorImpl Translator;

    // 2. 初始化翻译器，指向 .wire 文件
    if (!Translator.Initialize(*WireFilePath))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to initialize Wire translator for file: %s"), *WireFilePath);
        return;
    }

    // 3. 配置导入设置（可选）
    FWireSettings Settings;
    Translator.SetImportSettings(Settings);
    Translator.SetOutputPath(OutputPath);

    // 4. 加载场景到一个 IDatasmithScene 对象中
    TSharedPtr<IDatasmithScene> Scene = MakeShared<IDatasmithScene>();
    if (Translator.Load(Scene))
    {
        UE_LOG(LogTemp, Log, TEXT("Wire file loaded successfully."));
        // 此时，`Scene` 包含从 .wire 文件解析出的层次结构和几何数据引用。
        // 这些数据需要进一步通过 Datasmith 管道转换为最终的 UE 资产。
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to load Wire file."));
    }
}
```

### 进阶用法

更复杂的使用涉及直接处理 CAD 几何数据并将其转换为 `FMeshDescription`。这通常发生在翻译器内部，但理解其过程有助于进行自定义扩展。

*（来源：基于 `WireInterfaceImpl.h` 中的私有方法）*

```cpp
// 假设已经有一个代表几何体的 FAlDagNodePtr (来自 Alias 模型)
FAlDagNodePtr GeomNode = ...; // 通过遍历 .wire 场景获得
TSharedPtr<IDatasmithMeshElement> MeshElement = MakeShared<IDatasmithMeshElement>(TEXT("MyMesh"));
CADLibrary::FMeshParameters MeshParams;

// 使用翻译器内部的模型转换器获取网格描述
// 注意：此方法属于 FWireTranslatorImpl 的私有成员，此处仅为示意
TSharedPtr<CADLibrary::ICADModelConverter> ModelConverter = Translator.GetModelConverter();
if (ModelConverter.IsValid())
{
    TOptional<FMeshDescription> MeshDesc = Translator.GetMeshDescription(MeshElement, MeshParams);
    if (MeshDesc.IsSet())
    {
        // MeshDesc 中现在包含了转换后的网格数据，可以用于创建 UStaticMesh
        // 这个过程通常由更上层的 Datasmith 导入模块处理
    }
}
```

## Demo 示例

一个演示如何初始化并尝试加载 Wire 文件的最小 C++ 示例。

```cpp
// WireFileImporterDemo.h
#pragma once

#include "CoreMinimal.h"

class FWireFileImporterDemo
{
public:
    static void RunImportDemo(const FString& FilePath);
};
```

```cpp
// WireFileImporterDemo.cpp
#include "WireFileImporterDemo.h"
#include "WireInterface/IWireInterface.h"
#include "Modules/ModuleManager.h"

void FWireFileImporterDemo::RunImportDemo(const FString& FilePath)
{
    // 检查翻译器模块是否可用
    if (!FModuleManager::Get().IsModuleLoaded(UE_DATASMITHWIRETRANSLATOR_MODULE_NAME))
    {
        UE_LOG(LogTemp, Warning, TEXT("Wire Translator Module is not loaded."));
        return;
    }

    // 创建翻译器实例
    UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FWireTranslatorImpl Translator;

    // 设置输入文件和输出目录
    FString OutputDir = FPaths::ProjectSavedDir() / TEXT("WireImport");

    // 初始化并加载
    if (Translator.Initialize(*FilePath))
    {
        Translator.SetOutputPath(OutputDir);

        TSharedPtr<IDatasmithScene> ImportedScene = MakeShared<IDatasmithScene>();
        if (Translator.Load(ImportedScene))
        {
            UE_LOG(LogTemp, Log, TEXT("Demo: Successfully parsed Wire file: %s"), *FilePath);
            // 在实际应用中，需要将 ImportedScene 传递给 Datasmith 的后续处理流程。
        }
        else
        {
            UE_LOG(LogTemp, Error, TEXT("Demo: Failed to load Wire file content."));
        }
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Demo: Could not initialize translator with file: %s"), *FilePath);
    }
}
```

## 模块依赖

从 `CADInterfaces` 的构建文件可知其对 `TechSoft` 库有依赖。使用者在编写涉及底层 CAD 几何处理的代码时需注意。

| 模块 | 用途 |
|---|---|
| `TechSoft` | 提供处理多种 CAD 格式（如 STEP, IGES）的底层几何和拓扑内核。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，双精度常量截断为单精度 float 时产生的编译警告。 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | 新增逻辑，确保即使安装了 Alias 2027，Wire 文件翻译器也能正常工作。 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 将底层 CAD 库 TechSoft 更新至 2026.3 版本。 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新了 Datasmith CAD 缓存的版本。 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 解决了函数类型转换警告在 MSVC 和 Clang 编译器之间的兼容性问题。 |

### 维护评价

该插件自 **2019 年** 创建以来，一直得到持续维护。从最近的 Git 提交记录（2026 年 5 月）来看，维护**非常活跃**。更新内容包括：
-   **核心依赖更新**：升级了关键的 TechSoft 库，以支持新特性和修复。
-   **兼容性扩展**：主动添加了对新版 Alias 软件（2027）的支持，体现了良好的向前兼容性。
-   **代码质量**：持续修复编译警告和跨平台兼容性问题。

这是一个**稳定、活跃维护**的企业级功能插件。对于需要将 Alias 或其它 CAD 数据导入 UE5 的专业流程，**强烈推荐使用**。需要注意的是，它默认未启用（`EnabledByDefault: false`），用户需根据项目需求手动在插件设置中启用。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
-   [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
-   测试用例：（用户提供的源码中未包含测试文件信息）