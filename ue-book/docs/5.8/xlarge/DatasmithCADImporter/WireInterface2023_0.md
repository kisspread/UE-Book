# Datasmith CAD Importer

> Collection of tools to work with CAD files.

| 属性 | 值 |
|---|---|
| 中文名 | CAD文件导入 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CADInterfaces` (Runtime), `CADKernelSurface` (Runtime), `CADLibrary` (Runtime), `CADTools` (Runtime), `DatasmithCADTranslator` (Runtime), `DatasmithDispatcher` (Runtime), `DatasmithOpenNurbsTranslator` (Runtime), `DatasmithPLMXMLTranslator` (Runtime), `DatasmithWireTranslator` (Runtime), `ParametricSurface` (Runtime), `ParametricSurfaceExtension` (Runtime), `WireInterface2020` (Runtime), `WireInterface2021_3` (Runtime), `WireInterface2022` (Runtime), `WireInterface2022_1` (Runtime), `WireInterface2022_2` (Runtime), `WireInterface2023_0` (Runtime), `WireInterface2023_1` (Runtime), `WireInterface2024_1` (Runtime), `WireInterface2025_0` (Runtime), `WireInterface2026_0` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

## 用途

本插件是一个大型的 CAD 文件导入工具集，是 Epic Games Datasmith 生态系统的一部分。其核心目的是将多种工业 CAD 格式（如 Alias (.wire), STEP, IGES, CATIA, NX, SolidWorks, Rhino, PLMXML 等）转换为 Unreal Engine 可用的网格、材质和场景层级。

**`WireInterface2023_0` 模块** 是此插件中专门用于处理 **Autodesk Alias** `.wire` 格式文件的导入器实现（针对 2023 年版本的文件格式）。它通过 Autodesk 的官方 API（Alias SDK）读取 `.wire` 文件，解析其几何、材质、层级信息，并将其转换为 Datasmith 资产（`IDatasmithScene`, `IDatasmithMeshElement` 等），最终由 Datasmith CAD Translator 模块导入到 Unreal Engine。

## 使用场景

- 你在为汽车行业创建 VR/AR 展厅或设计评审应用 → 使用本插件导入设计师在 Alias 中创建的车身、内饰 `.wire` 模型。
- 你需要将工业设计软件（如 Alias）中的复杂曲面模型导入 UE 进行实时渲染或交互 → 本插件可以处理 Alias 的 B-Rep 和多边形几何。
- 你的工作流程需要保持 CAD 设计数据（如层级、材质）的完整性 → 本插件可以保留 `.wire` 文件中的图层结构和材质属性。

## 蓝图用法

`WireInterface2023_0` 是一个纯 C++ 的运行时模块，主要用于底层的 `.wire` 文件解析和转换。它**不直接提供蓝图可调用的函数 (UFUNCTION)**。

蓝图用户通常通过上层 **Datasmith CAD Translator** 模块提供的蓝图功能或编辑器 UI 来触发整个 CAD 导入流程，该流程在内部会调用如本模块在内的具体格式解析器。

## C++ 用法

本模块主要通过实现 `IWireInterface` 接口，为 Datasmith CAD 导入管线提供对 `.wire` 文件的支持。

### 头文件引入

要使用本模块的功能，你需要引入对应的头文件，通常包括：

```cpp
#include "WireInterfaceModule.h" // 模块加载和访问
#include "WireTranslatorImpl.h"  // Wire 文件解析器的实现
```

### 基本用法

**加载并查询一个 .wire 文件：**

```cpp
// 来源: WireInterfaceImpl.h (FWireTranslatorImpl)
// 1. 获取模块实例（如果已加载）
UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FDatasmithWireTranslatorModule& WireModule = UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FDatasmithWireTranslatorModule::Get();

// 2. 创建 .wire 文件的 Translator 实例
TSharedPtr<UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FWireTranslatorImpl> Translator = MakeShared<UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FWireTranslatorImpl>();

// 3. 初始化 Translator，指向 .wire 文件路径
FString WireFilePath = TEXT("/Path/To/YourModel.wire");
bool bInitialized = Translator->Initialize(*WireFilePath);

if (bInitialized)
{
    // 4. 创建或获取一个 IDatasmithScene 用于存放导入的数据
    TSharedPtr<IDatasmithScene> Scene = FDatasmithSceneFactory::CreateScene(TEXT("AliasImport"));
    
    // 5. 执行加载和解析
    bool bLoaded = Translator->Load(Scene);

    if (bLoaded)
    {
        // 6. (可选) 设置导入选项
        UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FWireSettings ImportSettings;
        Translator->SetImportSettings(ImportSettings);

        // 此时，`Scene` 对象中已填充了从 .wire 文件解析出的演员、网格、材质等元素。
        // 你可以遍历 Scene 来查看或处理这些数据。
        UE_LOG(LogTemp, Log, TEXT("Successfully loaded %d actors from .wire file"), Scene->GetActorsCount());
    }
}
```

### 进阶用法

**加载静态网格资产 (Mesh Payload)：**

除了构建场景，`FWireTranslatorImpl` 还可以独立加载单个网格体的详细数据，这对于延迟加载或动态加载场景部分很有用。

```cpp
// 来源: WireInterfaceImpl.h
TSharedPtr<IDatasmithMeshElement> MeshElement = ...; // 从已加载的Scene中获取，或通过其他方式创建
FDatasmithMeshElementPayload MeshPayload;
FDatasmithTessellationOptions TessellationOptions; // 配置曲面细分选项

// 直接从 Translator 加载该网格元素的几何数据
bool bMeshLoaded = Translator->LoadStaticMesh(MeshElement, MeshPayload, TessellationOptions);

if (bMeshLoaded)
{
    // MeshPayload 中现在包含了该网格的顶点、索引等数据
    // 可以用于构建 FMeshDescription 或 UStaticMesh
}
```

## Demo 示例

一个完整的、可编译的最小示例，展示如何初始化 `WireInterface` 模块并基本使用 `FWireTranslatorImpl` 来读取一个 `.wire` 文件。

### 头文件 (MyAliasImporter.h)

```cpp
#pragma once

#include "CoreMinimal.h"

// 前向声明
class IDatasmithScene;

namespace UE_DATASMITHWIRETRANSLATOR_NAMESPACE
{
    class FWireTranslatorImpl;
}

class FMyAliasImporter
{
public:
    FMyAliasImporter();
    ~FMyAliasImporter();

    /**
     * 导入一个 Alias .wire 文件到指定的 Datasmith Scene 中。
     * @param WireFilePath .wire 文件的完整路径。
     * @param OutScene 用于接收导入数据的 IDatasmithScene 对象。
     * @return 是否成功导入。
     */
    bool ImportWireFile(const FString& WireFilePath, TSharedPtr<IDatasmithScene> OutScene);

private:
    TSharedPtr<UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FWireTranslatorImpl> Translator;
};
```

### 源文件 (MyAliasImporter.cpp)

```cpp
#include "MyAliasImporter.h"
#include "WireInterfaceModule.h"
#include "WireTranslatorImpl.h"
#include "DatasmithSceneFactory.h"

FMyAliasImporter::FMyAliasImporter()
{
    // 确保 Wire Translator 模块已加载
    if (UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FDatasmithWireTranslatorModule::IsAvailable())
    {
        Translator = MakeShared<UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FWireTranslatorImpl>();
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Datasmith Wire Translator module is not loaded. Cannot import .wire files."));
    }
}

FMyAliasImporter::~FMyAliasImporter()
{
    Translator.Reset();
}

bool FMyAliasImporter::ImportWireFile(const FString& WireFilePath, TSharedPtr<IDatasmithScene> OutScene)
{
    if (!Translator || !OutScene.IsValid())
    {
        UE_LOG(LogTemp, Warning, TEXT("ImportWireFile: Invalid translator or scene."));
        return false;
    }

    // 初始化解析器
    if (!Translator->Initialize(*WireFilePath))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to initialize Wire translator for file: %s"), *WireFilePath);
        return false;
    }

    // 加载文件内容到场景
    if (!Translator->Load(OutScene))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to load .wire file: %s"), *WireFilePath);
        return false;
    }

    UE_LOG(LogTemp, Log, TEXT("Successfully imported .wire file: %s"), *WireFilePath);
    return true;
}
```

## 模块依赖

`WireInterface2023_0` 模块（以及所有其他 `WireInterfaceXXXX` 模块）依赖于 Autodesk Alias 的官方 SDK 进行文件解析。在 Unreal Engine 的构建系统中，这个依赖通过一个外部模块 `TechSoft` 来桥接。

| 模块 | 用途 |
|---|---|
| `TechSoft` | 提供 Autodesk Alias SDK 的封装和访问，是解析 `.wire` 文件格式的核心依赖。 |
| `CADLibrary` | 提供通用的 CAD 工具类、几何表示和转换器基类。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下，双精度常量截断为浮点数导致的警告。 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | 添加逻辑，确保在安装了 Alias 2027 的情况下，Wire 解析器仍能工作。 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 将 TechSoft 依赖更新至 2026.3 版本。 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新了 Datasmith CAD 缓存的版本标识。 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 使函数类型转换警告在 MSVC 和 Clang 编译器之间可移植。 |

### 维护评价

**活跃维护中。**
该插件（及其子模块）由 Epic Games 的 Enterprise 团队维护，更新非常频繁。最近的提交记录显示，仅在 2026 年 5 月 13 日当天就有多个实质性更新，包括：
1.  **兼容性更新**：支持最新版本的 Autodesk Alias 2027。
2.  **依赖更新**：升级了核心依赖 TechSoft。
3.  **质量改进**：修复编译警告，提升跨平台兼容性。
这些更新表明插件仍在积极适配最新的 CAD 软件版本和引擎开发环境，对于需要在工业/设计领域使用 Unreal Engine 的用户来说，是一个可靠的选择。**推荐使用**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter/Tests)