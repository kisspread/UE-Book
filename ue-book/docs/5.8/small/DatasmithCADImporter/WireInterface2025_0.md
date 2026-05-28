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

这个插件是 Datasmith 导入框架的一个后端组件，其核心功能并非提供通用的 CAD 文件处理工具，而是**作为 Datasmith 的 CAD 翻译器**，专门用于将 Alias 的 `.wire` 格式文件解析并转换为 Unreal Engine 可识别的 Datasmith 场景。它解决了在 Unreal Engine 中直接导入和利用高保真工业设计 CAD 模型（特别是 Alias 数据）的难题。插件通过一系列模块（如 `DatasmithCADTranslator`、`WireInterface` 系列）实现 CAD 模型的几何提取、材质映射、层级遍历和网格曲面化，并通过 Datasmith 框架将转换后的资产导入到引擎中。

## 使用场景

- **工业设计可视化**：汽车、消费品设计师在 Alias 软件中完成模型后，希望直接在 Unreal Engine 中创建高保真的实时可视化、动画或 VR 体验。
- **A面数据转换**：需要将 Alias 的 A 级曲面（A-Side）数据转换为游戏引擎可用的多边形网格，同时尽可能保留设计意图和材质属性。
- **CAD 资产入库**：在项目资产管线中，需要将 CAD 工程师提供的 `.wire` 文件批量转换并集成到 Unreal 项目的内容库中。

## 蓝图用法

经过对源码（特别是 `Public/*.h` 文件）的分析，**此插件没有暴露任何 `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)` 接口**。它的核心逻辑（如 `FWireTranslatorImpl`）是内部实现，用于在 Datasmith 导入流程中被自动调用。用户通过 Unreal Editor 的 Datasmith 导入界面（或通过 C++ 调用 `UDatasmithSubsystem`）触发 `.wire` 文件的导入，该插件的模块会在后台自动工作，无需在蓝图中进行直接操作。

## C++ 用法

本插件主要用于后台处理，C++ 交互通常发生在 Datasmith 框架内部或需要自定义导入管线时。以下示例展示了如何启动一个 Wire 文件的翻译过程（仅供理解流程，实际集成通常由 Datasmith 系统管理）。

### 头文件引入

```cpp
#include "DatasmithDispatcher/Public/DatasmithDispatcherLog.h"
#include "DatasmithCADTranslator/Public/DatasmithCADTranslatorModule.h"
// 引入 WireInterface 模块（版本需匹配）
#include "WireInterface2025_0/Public/WireInterfaceModule.h"
```

### 基本用法

从 `FWireTranslatorImpl` 类的方法可以推断出调用流程。
*来源：`Private/WireInterfaceImpl.h`*

```cpp
// 假设已通过 Datasmith Dispatcher 获得了一个 IWireInterface 实例
TSharedPtr<IWireInterface> WireTranslator = /* ... */;

// 1. 设置导入配置
FWireSettings Settings;
// ... 配置选项 ...
WireTranslator->SetImportSettings(Settings);

// 2. 设置输出路径（用于中间文件）
WireTranslator->SetOutputPath(TEXT("D:/Temp/DatasmithCache/"));

// 3. 初始化翻译器，指向 .wire 源文件
const TCHAR* WireFilePath = TEXT("C:/Models/MyModel.wire");
bool bInitialized = WireTranslator->Initialize(WireFilePath);

if (bInitialized)
{
    // 4. 加载并翻译文件到 Datasmith 场景
    TSharedPtr<IDatasmithScene> DatasmithScene = MakeShared<IDatasmithScene>();
    bool bLoaded = WireTranslator->Load(DatasmithScene);

    if (bLoaded)
    {
        // 翻译成功，DatasmithScene 现在包含了转换后的场景数据
        // 接下来可以将其导入到 Unreal Engine 中
    }
}
```

### 进阶用法

在某些需要单独处理网格数据的场景（如自定义几何管线），可以直接使用 `LoadStaticMesh` 方法。
*来源：`Private/WireInterfaceImpl.h`*

```cpp
// 假设已有一个有效的 WireTranslator 实例和目标 MeshElement
TSharedPtr<IDatasmithMeshElement> TargetMeshElement = /* ... */;
FDatasmithTessellationOptions TessOptions;
TessOptions.StitchingTechnique = EDatasmithCADStitchingTechnique::StitchingNone;

FDatasmithMeshElementPayload MeshPayload;
// 单独加载并获取一个网格元素的网格数据
bool bMeshLoaded = WireTranslator->LoadStaticMesh(TargetMeshElement, MeshPayload, TessOptions);

if (bMeshLoaded)
{
    // MeshPayload 中包含了 FMeshDescription 数据，可用于进一步处理或导入
    FMeshDescription& MeshDesc = MeshPayload.GetMeshDescription();
    // ... 对 MeshDesc 进行操作 ...
}
```

## Demo 示例

一个展示如何在 C++ 中启动 Wire 文件翻译的最小示例。注意：完整功能需要 Datasmith 和 WireInterface 插件同时启用。

```cpp
// MyWireImporter.h
#pragma once
#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FMyWireImporter
{
public:
    static bool ImportWireFile(const FString& WireFilePath, const FString& OutputPath);
};
```

```cpp
// MyWireImporter.cpp
#include "MyWireImporter.h"
#include "IWireInterface.h" // 来自 WireInterface 模块
#include "DatasmithScene.h"

bool FMyWireImporter::ImportWireFile(const FString& WireFilePath, const FString& OutputPath)
{
    // 注意：实际获取 IWireInterface 实例的逻辑由 DatasmithCADTranslator 模块管理，
    // 此处为简化演示，假设可以创建。通常你会通过 FDatasmithCADTranslatorModule::Get().GetWireInterface(Version) 获取。
    // 以下为模拟流程。

    // 1. 创建翻译器实例（简化，实际应从模块获取）
    // TSharedPtr<IWireInterface> Translator = /* ... */;

    // 2. 配置
    /*
    FWireSettings Settings;
    Translator->SetImportSettings(Settings);
    Translator->SetOutputPath(OutputPath);
    */

    // 3. 初始化和加载
    /*
    if (Translator->Initialize(*WireFilePath))
    {
        TSharedPtr<IDatasmithScene> Scene = MakeShared<IDatasmithScene>();
        if (Translator->Load(Scene))
        {
            UE_LOG(LogTemp, Log, TEXT("Wire file '%s' imported successfully."), *WireFilePath);
            // 此处可以将 Scene 持久化或进一步处理
            return true;
        }
    }
    UE_LOG(LogTemp, Error, TEXT("Failed to import wire file: '%s'"), *WireFilePath);
    */
    return false;
}
```

## 模块依赖

从各 `Build.cs` 文件分析，使用者（特别是需要与 `CADLibrary` 交互的自定义模块）需要关注以下独特依赖：

| 模块 | 用途 |
|---|---|
| `CADLibrary` | 提供 CAD 模型处理的核心抽象层、几何类型和工具函数。是此插件内部及二次开发的基础。 |
| `TechSoft` | 第三方库模块，为某些 CAD 格式（如 STEP, IGES）的转换提供支持。被 `CADInterfaces` 等模块依赖。 |

无其他特殊依赖（仅标准 Core/Engine/Datasmith 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下双精度常量截断到浮点数的警告。 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | 增加了逻辑以确保即使安装了 Alias 2027，Wire 翻译器也能正常工作。 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 将 TechSoft 库更新到 2026.3 版本。 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新了 Datasmith CAD 缓存版本。 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 使函数类型转换警告在 MSVC 和 Clang 编译器间更具可移植性。 |

### 维护评价

- **创建时间**：约 7 年（2019 年创建）。
- **最近更新**：非常活跃，2026 年 5 月有多次提交，内容包括**兼容性更新**（支持新版本 Alias、TechSoft 库）、**编译警告修复**和**功能改进**。
- **维护状态**：**活跃维护中**。作为 Unreal Engine 官方 Datasmith 插件套件的一部分，它随着 Datasmith 框架和第三方 CAD SDK 的更新而持续迭代。
- **已知问题/限制**：插件默认**未启用**（`EnabledByDefault: false`），需要在项目设置或 .uplugin 中手动启用。其功能高度依赖特定版本的第三方 SDK（如 TechSoft, OpenNurbs），兼容性需要关注。
- **推荐使用**：**推荐**。对于需要将 Alias `.wire` 文件集成到 Unreal Engine 工作流的工业设计、汽车等领域，这是官方且维护良好的解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter/Tests) (如果存在)