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

此插件并非一个单一功能的工具，而是一个庞大的**CAD文件导入框架集合**。它为Unreal Engine的Datasmith系统提供了一套完整的“后端”，用于读取、解析和转换多种工业CAD格式（如Alias/Wire、OpenNurbs、PLMXML等）的几何与材质数据，最终将其转换为引擎可用的静态网格体、材质等资产。

其核心作用是**连接专业CAD软件与虚幻引擎**，让来自汽车设计、产品设计、建筑等领域的复杂工程数据能够无损、高效地进入实时3D环境，用于可视化评审、数字孪生、虚拟展厅等场景。

## 使用场景

-   你在进行汽车外观设计评审，需要将**Alias**软件中设计的油泥模型（.wire文件）导入到UE中进行实时渲染和交互。
-   你需要导入**Rhino**、**Grasshopper**或其他支持**OpenNurbs**（.3dm）格式软件的复杂参数化曲面模型。
-   你工作流中有使用**PLM**（产品生命周期管理）系统，并需要将其中的**PLMXML**格式三维模型数据集成到UE项目。
-   你需要一套统一的框架来处理多种CAD格式，而不是为每种格式单独开发导入器。

## 蓝图用法

该插件主要是运行时（Runtime）和编辑器底层数据处理逻辑，其公开的蓝图接口非常有限。主要的导入功能通过Datasmith导入面板（编辑器UI）触发，或通过Datasmith的C++ API进行编程控制。

### 核心节点

由于模块多为内部实现，且面向数据处理管线，**未发现直接暴露给蓝图系统的 `UFUNCTION(BlueprintCallable)` 核心节点**。其功能主要通过Datasmith整体的导入/导出流程调用。

## C++ 用法

使用该插件的典型C++场景是扩展或自定义CAD格式的导入流程。使用者通常需要理解其内部的模块化架构。

### 头文件引入

```cpp
// 引入CAD数据模型与工具库
#include “CADLibrary/…”
#include “CADTools/…”

// 引入特定格式的翻译器接口（以Alias/Wire为例）
#include “DatasmithWireTranslator/…”
#include “WireInterface/WireInterfaceModule.h”
```

### 基本用法

C++层面的使用主要涉及调用翻译器接口来加载特定格式的CAD文件。以下是一个概念性的流程，展示了如何使用Wire接口来加载一个Alias文件。

```cpp
// (概念性代码，具体类名需根据源码确认)
// 1. 获取Wire翻译器模块
auto& WireModule = FDatasmithWireTranslatorModule::Get();
if (WireModule.IsAvailable())
{
    // 2. 实例化一个Wire翻译器实现
    // (FWireTranslatorImpl 是源码中 IWireInterface 的一个具体实现)
    TUniquePtr<IWireInterface> Translator = MakeUnique<FWireTranslatorImpl>();

    // 3. 设置导入选项（曲面细分精度、法线计算等）
    FWireSettings WireSettings;
    Translator->SetImportSettings(WireSettings);

    // 4. 初始化翻译器，指向.wire文件路径
    if (Translator->Initialize(TEXT(“C:/Models/car_design.wire”)))
    {
        // 5. 创建并关联一个Datasmith场景
        TSharedPtr<IDatasmithScene> DatasmithScene = …;
        Translator->Load(DatasmithScene);

        // 此时，DatasmithScene 中已包含从.wire文件转换而来的
        // 演员层次结构、网格体元素和材质元素。
    }
}
```

### 进阶用法

进阶用法涉及在导入管线中插入自定义逻辑，例如在`ICADModelConverter`阶段处理特定的几何体，或在材质生成时覆盖默认的`AlShader`到PBR材质的映射逻辑。这通常需要继承并扩展插件中提供的基类。

## Demo 示例

由于插件模块众多且复杂，提供一个完整的可编译最小示例并不现实。以下是一个基于`FWireTranslatorImpl`类的**概念性.h与.cpp文件**，展示了如何在你的项目中封装一个简单的CAD文件加载器。

```cpp
// MyCADLoader.h
#pragma once
#include “CoreMinimal.h”

namespace UE_DATASMITHWIRETRANSLATOR_NAMESPACE
{
    class IWireInterface;
}
class IDatasmithScene;

class MYPROJECT_API FMyAliasCADLoader
{
public:
    FMyAliasCADLoader();
    ~FMyAliasCADLoader();

    bool LoadFile(const FString& FilePath);
    TSharedPtr<IDatasmithScene> GetLoadedScene() const;

private:
    TSharedPtr<IDatasmithScene> LoadedScene;
    TUniquePtr<UE_DATASMITHWIRETRANSLATOR_NAMESPACE::IWireInterface> Translator;
};
```

```cpp
// MyCADLoader.cpp
#include “MyCADLoader.h”
#include “DatasmithSceneFactory.h”
#include “WireInterface/WireInterfaceModule.h”
// 注意：需要根据实际路径引入具体的翻译器头文件
// #include “DatasmithWireTranslator/…”

FMyAliasCADLoader::FMyAliasCADLoader()
{
    // 使用模块工厂或直接创建，此处为概念
    Translator = …; // 创建FWireTranslatorImpl实例
    LoadedScene = FDatasmithSceneFactory::CreateScene(TEXT(“MyCADImport”));
}

FMyAliasCADLoader::~FMyAliasCADLoader()
{
    Translator.Reset();
}

bool FMyAliasCADLoader::LoadFile(const FString& FilePath)
{
    if (!Translator || !LoadedScene)
    {
        return false;
    }

    Translator->SetImportSettings(FWireSettings());
    if (Translator->Initialize(*FilePath))
    {
        return Translator->Load(LoadedScene);
    }
    return false;
}

TSharedPtr<IDatasmithScene> FMyAliasCADLoader::GetLoadedScene() const
{
    return LoadedScene;
}
```

## 模块依赖

该插件依赖于强大的第三方库来解析CAD格式，并与UE的Datasmith核心框架集成。

| 模块 | 用途 |
|---|---|
| `TechSoft` | 提供对众多CAD格式（STEP， IGES， CATIA V4/V5， SolidWorks， Inventor等）的底层读写支持。是`CADInterfaces`模块的核心依赖。 |
| `OpenNurbs6` | 提供OpenNurbs几何库支持，用于处理`.3dm`（Rhino）格式的NURBS曲面数据。是`DatasmithOpenNurbsTranslator`模块的依赖。 |

**注意**：该插件的模块还广泛依赖于UE的`DatasmithCore`、`MeshDescription`等核心模块，此处省略。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了严格浮点模式下双精度常量隐式转换为浮点数产生的编译警告。 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | 添加逻辑，使Wire翻译器能在安装了Alias 2027版本的环境中正常工作。 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 更新了TechSoft库的版本至2026.3。 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新了DatasmithCAD缓存的版本。 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 使函数类型转换警告在MSVC和Clang编译器间可移植。 |

### 维护评价

-   **活跃维护**：尽管创建于2019年（约7年前），但根据git日志，在2026年5月仍有密集的功能更新、依赖库升级和兼容性修复，表明该项目处于**非常活跃的维护状态**。
-   **企业级支持**：由Epic Games官方维护，作为Enterprise插件的一部分，其稳定性和长期支持有保障。
-   **默认禁用**：`EnabledByDefault`为false，需要用户在项目设置中手动启用，这通常意味着它是一个可选的高级功能或大型依赖。
-   **推荐使用**：如果你的工作流涉及导入复杂的工业CAD数据，且格式在该插件支持范围内（特别是Alias/Wire、OpenNurbs等），强烈推荐使用。它是虚幻引擎处理专业级CAD数据的核心解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例]：（未在提供的路径中明确发现标准测试目录，可能集成在引擎测试套件中或为内部测试）