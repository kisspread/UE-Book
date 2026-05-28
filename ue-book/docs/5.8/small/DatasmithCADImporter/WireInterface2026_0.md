# Wire Interface 2026_0

> 为 WireInterface2026_0 模块生成文档。此模块是 DatasmithCADImporter 插件的一部分，提供特定版本的 Alias .wire 文件格式解析与转换功能。

| 属性 | 值 |
|---|---|
| 中文名 | CAD线框导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `WireInterface2026_0` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

## 用途

本模块是 Datasmith CAD Importer 插件中专门用于处理 Autodesk Alias 软件生成的 `.wire` 格式文件（版本 2026.0）的核心翻译器。它并非通用 CAD 文件导入器，而是专注于解析 Alias 模型中的 DAG（有向无环图）节点结构、几何体（网格、曲面、壳体）、材质（着色器）及图层信息，并将其转换为 Unreal Engine 的 Datasmith 场景元素（如 `IDatasmithMeshElement`, `IDatasmithActorElement`）。其存在是为了让汽车、产品设计等领域的艺术家和设计师能够将复杂的 Alias NURBS 曲面模型高效地导入到 UE 中进行实时可视化、评审或虚拟样机制作。

## 使用场景

- 你在使用 **Autodesk Alias** 进行汽车A级曲面或工业产品设计，需要将带有复杂曲面、修剪边界和精细材质的 `.wire` 模型导入到 **Unreal Engine** 中进行实时渲染或虚拟评审。
- 你需要通过 Datasmith 管线自动化处理 Alias 模型，利用其缓存机制提高大型模型导入的效率。
- 你需要保留原始 Alias 模型的图层结构、对称信息和材质属性。

## 蓝图用法

本模块主要提供运行时翻译功能，其核心逻辑封装在 C++ 接口中，不直接暴露大量蓝图节点。蓝图交互通常通过上层的 Datasmith 导入系统完成。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FDatasmithWireTranslatorModule::Get()` | 获取 WireTranslator 模块的单例实例 | `FDatasmithWireTranslatorModule` |
| `FDatasmithWireTranslatorModule::IsAvailable()` | 检查模块是否已加载并可用 | `FDatasmithWireTranslatorModule` |
| `FDatasmithWireTranslatorModule::GetTempDir()` | 获取模块用于临时文件处理的目录路径 | `FDatasmithWireTranslatorModule` |

### 使用示例（蓝图描述）

在蓝图中，你通常不会直接调用此模块的函数。取而代之的是，你会：
1. 使用 **Datasmith** 相关的蓝图节点（如 `DatasmithImportScene`）。
2. 在导入设置中选择或指定导入器类型为针对 `.wire` 格式的翻译器（由 `WireInterface2026_0` 模块提供支持）。
3. 整个加载、解析和场景构建过程会在模块内部自动执行，最终将生成的 UE 场景元素应用到关卡中。

## C++ 用法

### 头文件引入

```cpp
#include "WireInterfaceModule.h"
```

### 基本用法

以下示例展示了如何检查模块并获取其临时目录，这通常在工具链或自动化脚本中使用。
**来源文件**: `Public/WireInterfaceModule.h`

```cpp
// 检查 WireInterface2026_0 模块是否已加载
if (UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FDatasmithWireTranslatorModule::IsAvailable())
{
    // 获取模块实例
    auto& WireModule = UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FDatasmithWireTranslatorModule::Get();
    
    // 获取临时工作目录，用于存放中间转换文件
    FString TempDir = WireModule.GetTempDir();
    UE_LOG(LogTemp, Log, TEXT("Wire Translator Temp Directory: %s"), *TempDir);
}
else
{
    UE_LOG(LogTemp, Warning, TEXT("WireInterface2026_0 module is not loaded. Ensure the DatasmithCADImporter plugin is enabled."));
}
```

### 进阶用法

本模块的核心是 `IWireInterface` 和 `FWireTranslatorImpl`。高级用户可能需要直接实例化并驱动翻译器，但这通常由 Datasmith 导入器框架内部管理。以下代码片段展示了翻译器接口的核心方法签名。
**来源文件**: `Private/WireInterfaceImpl.h`

```cpp
// 假设你通过某种方式（例如工厂模式）获取到了 IWireInterface 的实例
TSharedPtr<UE_DATASMITHWIRETRANSLATOR_NAMESPACE::IWireInterface> WireTranslator = ...;

// 1. 设置导入选项
UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FWireSettings Settings;
// ... 配置 Settings ...
WireTranslator->SetImportSettings(Settings);

// 2. 指定输出路径（用于缓存）
WireTranslator->SetOutputPath(FPaths::ProjectSavedDir() / TEXT("DatasmithCache"));

// 3. 初始化翻译器并指定要导入的 .wire 文件
const TCHAR* WireFilePath = TEXT("C:/Models/CarBody.wire");
if (WireTranslator->Initialize(WireFilePath))
{
    // 4. 创建一个空的 Datasmith 场景容器
    TSharedPtr<IDatasmithScene> DatasmithScene = FDatasmithSceneFactory::CreateScene(TEXT("ImportedWireScene"));
    
    // 5. 执行加载，将 .wire 文件解析为 Datasmith 场景元素
    if (WireTranslator->Load(DatasmithScene))
    {
        // 6. 此时 DatasmithScene 中已填充了从 .wire 文件提取的 Actor、Mesh、Material 等元素。
        //    你可以将其应用到关卡中，或进行后续处理。
        //    例如，遍历场景根元素：
        for (int32 i = 0; i < DatasmithScene->GetActorsCount(); ++i)
        {
            TSharedPtr<IDatasmithActorElement> Actor = DatasmithScene->GetActor(i);
            UE_LOG(LogTemp, Log, TEXT("Loaded Actor: %s"), *Actor->GetName());
        }
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to load .wire file."));
    }
}
```

## Demo 示例

以下是一个最小化的 C++ 类，用于展示如何在编辑器工具中调用 WireInterface 模块进行文件检查。

**MyWireImportTool.h**
```cpp
#pragma once

#include "CoreMinimal.h"

class FMyWireImportTool
{
public:
    static bool IsWireFileSupported(const FString& FilePath);
};
```

**MyWireImportTool.cpp**
```cpp
#include "MyWireImportTool.h"
#include "WireInterfaceModule.h"

bool FMyWireImportTool::IsWireFileSupported(const FString& FilePath)
{
    // 检查文件扩展名是否为 .wire
    if (!FilePath.EndsWith(TEXT(".wire")))
    {
        return false;
    }

    // 检查对应的翻译模块是否可用
    if (!UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FDatasmithWireTranslatorModule::IsAvailable())
    {
        UE_LOG(LogTemp, Warning, TEXT("Cannot check .wire file: WireInterface module is not loaded."));
        return false;
    }

    // 模块已加载，可以认为该文件类型受支持
    // 实际的格式验证会在调用 Initialize 时进行
    return true;
}
```

## 模块依赖

要编译和使用依赖于 `WireInterface2026_0` 模块的代码，你需要在你的模块的 `.Build.cs` 文件中添加以下依赖：

| 模块 | 用途 |
|---|---|
| `DatasmithContent` | 提供 `IDatasmithScene`, `IDatasmithMeshElement` 等核心 Datasmith 接口和工厂类 |
| `CADLibrary` | 提供通用的 CAD 模型转换器基类、网格参数、导入参数等基础设施 |
| `CADInterfaces` | 提供与底层 CAD 内核（如 TechSoft）交互的接口定义 |
| `TechSoft` | 提供 TechSoft HOOPS Exchange 的封装，用于解析多种 CAD 文件格式（包括 .wire） |
| `MeshDescription` | 用于处理和构建网格描述数据 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下双精度常量截断为浮点数导致的警告。 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | 添加逻辑，确保即使安装了 Alias 2027，线框翻译器也能正常工作。 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 将 TechSoft 库更新至 2026.3 版本。 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新了 Datasmith CAD 缓存的版本标识。 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 使函数类型转换警告在 MSVC 和 Clang 编译器之间可移植。 |

### 维护评价

该模块属于 DatasmithCADImporter 插件的一部分，**目前处于活跃维护状态**。
- **创建时间**：约 7 年前，属于企业级长期支持插件。
- **更新频率**：最近有密集的更新，主要集中在提升兼容性（如支持新版 Alias）、修复编译警告、更新底层依赖库（TechSoft）和维护缓存机制。这表明 Epic Games 仍在积极确保其对最新版 CAD 软件（Alias）和编译器环境的兼容性。
- **维护状态**：**活跃维护中**。更新内容显示团队在主动跟进上游软件（Alias, TechSoft）的变化并修复问题。
- **推荐使用**：是。如果你的工作流中需要处理 Autodesk Alias 的 `.wire` 文件，并且使用的是 2026 年左右或之后的版本，这个模块是官方提供的、经过维护的可靠解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter/Tests)