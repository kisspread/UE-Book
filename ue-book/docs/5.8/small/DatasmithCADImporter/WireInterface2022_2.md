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

该插件并非一个通用的CAD文件导入器，而是 **Datasmith 针对特定 CAD 软件（如 Autodesk Alias）的专用翻译器集合**。其核心功能是将工业设计软件（特别是Alias）生成的 `.wire` 格式文件，解析并转换为 Unreal Engine 可用的 Datasmith 场景元素（包括几何体、材质、层级结构）。

它解决的问题是：让 UE 能够直接读取和处理来自高端工业设计（特别是汽车A级曲面设计）软件的原始数据，实现设计数据到实时可视化的无缝对接，避免中间格式转换带来的数据损失。插件内部实现了复杂的模型遍历、B-Rep 曲面转换、网格化（Tessellation）和材质映射逻辑。

## 使用场景

- **汽车设计评审**：设计师将 Alias 中创建的汽车内饰/外饰 `.wire` 文件直接导入 UE，用于进行实时渲染、光影评估和设计评审。
- **产品数字样机**：在消费电子、家居产品等领域，利用 Alias 等软件进行外观设计后，直接导入 UE 构建高保真的数字样机进行展示。
- **与 Alias 工作流集成**：为需要将 Alias 设计模型与 UE 实时引擎结合的团队提供标准的数据管线。

## 蓝图用法

该插件主要提供 C++ 运行时和翻译器模块，**未发现公开的 BlueprintCallable 函数或蓝图资产**。其功能通过 Datasmith 的导入框架在后台调用。要启用它，通常需要在项目的 `Plugins` 设置中手动启用 `Datasmith CAD Importer` 插件，然后 UE 的 Datasmith 导入功能将自动识别并使用相应的翻译器来处理支持的 CAD 文件。

## C++ 用法

### 头文件引入

使用该插件时，通常需要链接其提供的模块。以下以核心的 `WireInterface2022_2` 模块为例：

```cpp
#include "WireInterfaceModule.h"
#include "WireInterfaceImpl.h"
```

### 基本用法

该插件的核心类 `FWireTranslatorImpl` 实现了 `IWireInterface` 接口，用于加载和解析 `.wire` 文件。以下是其核心流程的模拟：

```cpp
// 1. 获取并初始化翻译器模块
// 来源：Public/WireInterfaceModule.h
FDatasmithWireTranslatorModule& WireModule = FDatasmithWireTranslatorModule::Get();
if (WireModule.IsAvailable())
{
    // 通常由 Datasmith 框架在内部创建和管理翻译器实例
}

// 2. 创建翻译器实例并加载场景
// 来源：Private/WireInterfaceImpl.h
TSharedRef<UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FWireTranslatorImpl> Translator = MakeShared<UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FWireTranslatorImpl>();

// 设置导入参数
UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FWireSettings Settings;
// ... 配置导入设置 ...
Translator->SetImportSettings(Settings);

// 设置输出路径（用于缓存转换后的数据）
Translator->SetOutputPath(FPaths::ProjectSavedDir() / TEXT("DatasmithWireCache"));

// 初始化并加载 .wire 文件
const TCHAR* WireFilePath = TEXT("/path/to/your/model.wire");
bool bSuccess = Translator->Initialize(WireFilePath);

// 创建一个空的 Datasmith 场景容器
TSharedRef<IDatasmithScene> DatasmithScene = FDatasmithSceneFactory::CreateScene(TEXT("ImportedWireScene"));

if (bSuccess)
{
    // 将 .wire 文件内容解析并填充到 Datasmith 场景中
    bSuccess = Translator->Load(DatasmithScene);
}

// 此时，DatasmithScene 中包含了从 .wire 文件转换而来的 Actor、Mesh、Material 等元素。
// 后续可将此场景导入到 UE 的关卡中。
```

### 进阶用法：访问内部数据结构

以下代码展示了在翻译器内部，如何使用 `FAlDagNodePtr` 等封装类来处理 Alias 的 DAG（有向无环图）节点结构。这通常发生在翻译器的 `TraverseModel` 等内部方法中。

```cpp
// 来源：Private/OpenModelUtils.h
using namespace UE_DATASMITHWIRETRANSLATOR_NAMESPACE;

// FAlDagNodePtr 是对 Alias AlDagNode 的安全指针封装，提供类型查询和层信息
FAlDagNodePtr SomeDagNode( RawAlDagNodePointer );

if (SomeDagNode.HasGeometry())
{
    // 查询节点类型
    if (SomeDagNode.IsAMesh())
    {
        TAlObjectPtr<AlMesh> OutMesh;
        if (SomeDagNode.GetMesh(OutMesh))
        {
            // 处理网格数据
        }
    }
    else if (SomeDagNode.IsASurface())
    {
        TAlObjectPtr<AlSurface> OutSurface;
        if (SomeDagNode.GetSurface(OutSurface))
        {
            // 处理 B-Rep 曲面数据
        }
    }
}

// 获取节点所属的图层
TAlObjectPtr<AlLayer> Layer = SomeDagNode.GetLayer();
FString LayerName = SomeDagNode.GetLayerName();

// 将 Alias 的全局变换应用到 Datasmith Actor 上
TSharedRef<IDatasmithActorElement> Actor = FDatasmithActorFactory::CreateActor(TEXT("ConvertedActor"));
SomeDagNode.SetActorTransform(Actor.Get()); // 设置变换，内部处理坐标系转换

// 通过 FAliasModelToCADKernelConverter 或 FAliasModelToTechSoftConverter 将 Alias 几何体转换为中间格式
FAliasModelToCADKernelConverter Converter(TessellationOptions, ImportParameters);
// 假设已获取到某个 DagNode 的几何信息 FDagNodeGeometry
FDagNodeGeometry Geometry(/*...*/);
Converter.AddGeometry(Geometry);

// 进行网格化
FMeshDescription OutMesh;
CADLibrary::FMeshParameters MeshParams;
bool bTessellated = Converter.Tessellate(MeshParams, OutMesh);
```

## 模块依赖

该插件依赖于多个特定的外部库和内部 Datasmith 模块。

| 模块 | 用途 |
|---|---|
| `TechSoft` | 提供读取和转换多种 CAD 格式（如 CATIA， NX， SolidWorks）的核心库。 |
| `OpenNurbs6` | 提供读取 Rhino 3D 的 `.3dm` 文件格式的能力。 |
| `DatasmithCADTranslator` | Datasmith CAD 翻译器的核心基础模块。 |
| `CADInterfaces` | 提供与不同 CAD 内核交互的抽象接口。 |
| `CADLibrary` | 提供 CAD 数据转换过程中的通用工具库和结构体。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，双精度常量被截断为浮点数时产生的编译警告。 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | 增加了逻辑，确保即使安装了 Alias 2027，Wire 翻译器也能正常工作。 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 将内部使用的 TechSoft 库更新到了 2026.3 版本。 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新了 DatasmithCAD 缓存的版本标识。 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 使函数类型转换警告在 MSVC 和 Clang 编译器之间可移植。 |

### 维护评价

- **状态**：**活跃维护**。插件在最近一周内（2026年5月）有多次实质性更新，包括依赖库升级、兼容性改进和编译器适配。
- **推荐度**：**推荐使用**，但限于特定需求。该插件是专业工具链的关键环节，对于需要将 Alias 设计数据引入 UE 进行实时可视化的团队至关重要。插件本身持续更新以适应新版本的 Alias 软件和编译器。
- **注意事项**：
    1.  插件默认**未启用** (`EnabledByDefault: false`)，需手动在项目中启用。
    2.  它是一个**运行时 (Runtime)** 模块集合，意味着打包后的项目也可以使用此功能（例如用于加载用户提供的 `.wire` 文件）。
    3.  由于其专业性，功能和 API 可能随着上游 CAD 软件和 TechSoft 库的更新而变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter/Tests) （假设存在，路径为推断）