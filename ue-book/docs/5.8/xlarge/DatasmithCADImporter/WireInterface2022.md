# Datasmith CAD Importer

> Collection of tools to work with CAD files.

| 属性 | 值 |
|---|---|
| 中文名 | 2022版 Alias 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CADInterfaces` (Runtime), `CADKernelSurface` (Runtime), `CADLibrary` (Runtime), `CADTools` (Runtime), `DatasmithCADTranslator` (Runtime), `DatasmithDispatcher` (Runtime), `DatasmithOpenNurbsTranslator` (Runtime), `DatasmithPLMXMLTranslator` (Runtime), `DatasmithWireTranslator` (Runtime), `ParametricSurface` (Runtime), `ParametricSurfaceExtension` (Runtime), `WireInterface2020` (Runtime), `WireInterface2021_3` (Runtime), `WireInterface2022` (Runtime), `WireInterface2022_1` (Runtime), `WireInterface2022_2` (Runtime), `WireInterface2023_0` (Runtime), `WireInterface2023_1` (Runtime), `WireInterface2024_1` (Runtime), `WireInterface2025_0` (Runtime), `WireInterface2026_0` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

## 用途

`DatasmithCADImporter` 是一个企业级插件集合，其核心功能是将多种 CAD 格式的文件（如 Alias .wire、Step、IGES 等）转换为 Unreal Engine 可识别的 Datasmith 场景和资产。本文档聚焦于其中的 `WireInterface2022` 模块，该模块专门负责处理 **Alias 2022 版本** 的 `.wire` 文件。

该模块通过内部算法遍历 Alias 文件的 DAG（有向无环图）结构，将几何体（网格、曲面、壳体）、材质（着色器）、层级（图层）等信息，转换为 UE 的 `IDatasmithScene`、`IDatasmithMeshElement` 和 `IDatasmithMaterialElement` 等元素。它解决了工业设计软件（如 Alias AutoStudio）的模型资产如何高保真地进入游戏引擎或可视化应用的问题，是 Datasmith 工作流中针对特定 CAD 格式的关键后端。

## 使用场景

- **工业设计可视化**：你是一名汽车设计师，在 Alias 中完成了车辆外形设计，需要将其导入 Unreal Engine 制作高质量的产品展示或虚拟评审。
- **实时渲染管线集成**：你的团队使用 Alias 作为主要 CAD 工具，需要将设计资产自动导入 UE，用于构建数字孪生、虚拟展厅或实时渲染项目。
- **跨软件资产管线**：你负责维护一个从 Alias 到 UE 的自动化资产发布流水线，需要一个稳定可靠的翻译器模块。

## 蓝图用法

`WireInterface2022` 模块主要作为 Datasmith 内部管线的一个环节，其核心类 `FWireTranslatorImpl` 实现的是 `IWireInterface` 内部接口，并未暴露供蓝图直接调用的 `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)`。其使用通常是通过上层的 Datasmith 导入器或 C++ 代码驱动的。

因此，该模块不提供蓝图节点。

## C++ 用法

### 头文件引入

虽然 `WireInterface2022` 模块主要被 `DatasmithCADTranslator` 模块内部使用，但其提供的接口定义在以下头文件中：
```cpp
#include "WireInterfaceModule.h" // 模块入口
#include "IWireInterface.h" // 核心接口 (可能位于 CADInterfaces 或 DatasmithCADTranslator 模块)
```

### 基本用法

以下代码片段展示了如何初始化并使用 Wire 翻译器的基本流程（基于 `FWireTranslatorImpl` 的接口）。

```cpp
// 假设我们已经拥有一个有效的 Datasmith Scene 对象
TSharedPtr<IDatasmithScene> DatasmithScene = ...;

// 1. 获取并初始化 Wire 模块
if (FDatasmithWireTranslatorModule::IsAvailable())
{
    // 模块通常由 Datasmith 管线自动加载和管理
}

// 2. 创建翻译器实例并初始化
FWireTranslatorImpl Translator;
if (Translator.Initialize(TEXT("C:/Models/MyModel.wire")))
{
    // 3. 设置导入选项（如曲面细分参数）
    FWireSettings Settings;
    Settings.TessellationOptions = FDatasmithTessellationOptions::Current;
    Translator.SetImportSettings(Settings);

    // 4. 设置输出路径（用于缓存中间数据）
    Translator.SetOutputPath(FPaths::ProjectSavedDir() / TEXT("DatasmithCache"));

    // 5. 加载场景数据，将 Alias 模型转换为 Datasmith 元素
    if (Translator.Load(DatasmithScene))
    {
        // 加载成功，DatasmithScene 已被填充
        UE_LOG(LogTemp, Log, TEXT("Alias .wire file loaded successfully."));
    }
}
```
*来源：`Private/WireInterfaceImpl.h` 中 `FWireTranslatorImpl` 的公开方法。*

### 进阶用法

更高级的使用场景涉及对单个网格的按需加载和几何转换过程的介入。

```cpp
// 在场景加载后，可能需要按需加载特定的网格资产
TSharedPtr<IDatasmithMeshElement> MeshElement = ...; // 从 DatasmithScene 中获取
FDatasmithMeshElementPayload OutPayload;
FDatasmithTessellationOptions TessOptions;

// 使用翻译器为特定的 MeshElement 生成网格数据
if (Translator.LoadStaticMesh(MeshElement, OutPayload, TessOptions))
{
    // 成功获取网格有效载荷，可用于创建 StaticMesh 资产
    // OutPayload 中包含 FMeshDescription 等数据
}

// 内部流程涉及复杂的场景图遍历 (TraverseDag) 和几何处理
// 例如，ProcessGeometryNode 方法会根据节点类型（网格、曲面、壳体）选择不同的网格提取策略
// (GetMeshDescriptionFromParametricNode, GetMeshDescriptionFromMeshNode, GetMeshDescriptionFromBodyNode等)
```
*来源：`Private/WireInterfaceImpl.h` 中的 `LoadStaticMesh`、`TraverseDag`、`ProcessGeometryNode` 等方法。*

## Demo 示例

一个概念性的最小示例，展示如何使用 `WireInterface2022` 模块加载 Alias 文件。

```cpp
// MyAliasLoader.h
#pragma once
#include "CoreMinimal.h"

class IDatasmithScene;
class FWireTranslatorImpl;

class FMyAliasLoader
{
public:
    bool LoadAliasFile(const FString& FilePath, TSharedPtr<IDatasmithScene>& OutScene);

private:
    TUniquePtr<FWireTranslatorImpl> Translator;
};
```

```cpp
// MyAliasLoader.cpp
#include "MyAliasLoader.h"
#include "WireInterfaceModule.h"
#include "IWireInterface.h" // 假设接口头文件路径
#include "DatasmithSceneFactory.h"

bool FMyAliasLoader::LoadAliasFile(const FString& FilePath, TSharedPtr<IDatasmithScene>& OutScene)
{
    if (!FDatasmithWireTranslatorModule::IsAvailable())
    {
        UE_LOG(LogTemp, Error, TEXT("WireInterface2022 module is not available."));
        return false;
    }

    // 创建 Datasmith 场景
    OutScene = FDatasmithSceneFactory::CreateScene(TEXT("MyAliasImport"));

    // 实例化翻译器 (注意：直接实例化内部类通常不被推荐，应通过 Datasmith 管线)
    Translator = MakeUnique<FWireTranslatorImpl>();

    if (!Translator->Initialize(*FilePath))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to initialize Wire translator for file: %s"), *FilePath);
        return false;
    }

    // 使用默认设置
    FWireSettings Settings;
    Translator->SetImportSettings(Settings);
    Translator->SetOutputPath(FPaths::ProjectSavedDir());

    if (!Translator->Load(OutScene))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to load Alias file into Datasmith scene."));
        return false;
    }

    return true;
}
```

## 模块依赖

根据构建文件和代码引用，`WireInterface2022` 及相关模块依赖以下**独特**的外部或内部模块：

| 模块 | 用途 |
|---|---|
| `TechSoft` | 核心的 CAD 几何内核库，用于高级的 B-Rep（边界表示）几何处理和转换。`CADInterfaces` 模块直接依赖它。 |
| `OpenNurbs6` | 用于解析 OpenNurbs（.3dm）文件格式的库。由 `DatasmithOpenNurbsTranslator` 模块使用。 |

其他依赖（如 `CADKernel`, `CADLibrary`, `DatasmithCore` 等）属于 Datasmith 框架内部模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 导致的编译警告。 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | 增加逻辑，确保即使安装了 Alias 2027，翻译器也能正常工作。 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 将底层 TechSoft 库升级至 2026.3 版本。 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新了 DatasmithCAD 缓存的版本格式。 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 使函数类型转换警告在 MSVC 和 Clang 编译器之间可移植。 |

### 维护评价

`DatasmithCADImporter` 插件及其核心的 `WireInterface` 模块处于**活跃维护**状态。从近期提交记录（均为2026年5月）可以看出，Epic 持续在更新其依赖的外部库（TechSoft）和处理编译器兼容性问题。虽然插件创建于约6年前，但其作为企业级工具链的一部分，更新节奏稳定。

主要限制在于：
1.  **版本特异性**：存在大量版本化的 `WireInterface` 模块，意味着需要为不同版本的 Alias 文件维护不同的翻译器。
2.  **外部依赖强**：高度依赖闭源的 TechSoft 库，且需要用户或构建系统自行配置该库。
3.  **默认禁用**：插件默认未启用，需要用户手动在插件面板或项目配置中启用。

**总体推荐**：如果你的工作流明确需要导入 Alias 2022 的 .wire 文件到 Unreal Engine，并且可以解决 TechSoft 库的配置问题，那么此模块是必备且活跃维护的选择。对于新项目，建议检查是否有更新的 `WireInterface` 版本（如 2023, 2024）以支持更新的 Alias 版本。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter/Tests) *(如果存在)*