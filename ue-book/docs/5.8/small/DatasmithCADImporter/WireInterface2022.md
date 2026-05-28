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

这个插件是 Datasmith CAD 导入管道的核心组件，专门用于处理和转换 CAD（计算机辅助设计）文件，特别是来自工业设计软件（如 Autodesk Alias）的 `.wire` 格式文件。

它解决的核心问题是将复杂的 CAD 几何体、材质和层次结构，高效、准确地转换为 Unreal Engine 可以直接使用的资产（如 Static Mesh 和 Material）。其存在是为了支持需要在虚幻引擎中可视化的工业、建筑、汽车设计等专业 CAD 数据，是连接专业 CAD 软件与实时引擎的桥梁。

## 使用场景

- 你正在制作一个汽车配置器应用，需要将 Alias 设计的车身模型导入 UE → 使用此插件的 `DatasmithWireTranslator` 模块。
- 你需要将复杂的机械零件或装配体从 CAD 软件导入 UE 进行虚拟原型评审 → 此插件提供的 CAD 导入器是 Datasmith 框架的一部分。
- 你需要在保持原始 CAD 模型层级（层、组、材质）的同时进行导入 → 该插件实现了从 CAD DAG（有向无环图）到 UE Actor 层级的转换。

## 蓝图用法

该插件的功能主要通过 Datasmith 框架的导入界面和流程暴露，而非提供独立的蓝图节点。核心的转换逻辑在 C++ 模块内部实现。

用户通常在编辑器中通过 **Datasmith 导入窗口** 选择 `.wire` 文件进行导入。插件的各个模块（如 `WireInterface2022`）会在后台被调用，处理文件解析、几何体转换和材质映射。

### 核心节点

该插件本身不直接暴露通用的 `BlueprintCallable` 节点。其“节点”是集成在 Datasmith 导入器中的 **文件类型支持** 和 **转换器**。

| 节点 | 说明 | 所在类/模块 |
|---|---|---|
| `.wire` 文件导入支持 | 使 Datasmith 导入器能够识别并处理 Autodesk Alias 的 .wire 文件格式。 | `FDatasmithWireTranslatorModule` / `WireInterface20XX` 模块 |

## C++ 用法

该插件的功能主要通过内部的转换器类实现。公共 API 面向 Datasmith 框架。

### 头文件引入

要使用 Datasmith 框架，通常需要包含以下头文件：
```cpp
#include "DatasmithSceneFactory.h"
#include "IDatasmithSceneElements.h"
```

### 基本用法

此插件的主要用途是在 Datasmith 导入流程中被内部调用。开发者通常不会直接实例化 `FWireTranslatorImpl`。其生命周期由 `DatasmithDispatcher` 管理。

以下代码片段展示了 `FWireTranslatorImpl` 的核心接口，体现了加载场景和网格的基本流程（来源：`Private/WireInterfaceImpl.h`）：

```cpp
// 该类是 .wire 文件转换器的核心实现，实现了 IWireInterface 接口
class FWireTranslatorImpl : public IWireInterface
{
public:
    // 初始化转换器，传入 .wire 文件的完整路径
    virtual bool Initialize(const TCHAR* InSceneFullName) override;
    
    // 将解析的场景数据加载到提供的 Datasmith 场景对象中
    virtual bool Load(TSharedPtr<IDatasmithScene> InScene) override;
    
    // 应用导入设置（如镶嵌选项）
    virtual void SetImportSettings(const FWireSettings& Options) override;
    
    // 加载单个静态网格体并获取其有效负载数据
    bool LoadStaticMesh(const TSharedPtr<IDatasmithMeshElement> MeshElement, 
                        FDatasmithMeshElementPayload& OutMeshPayload, 
                        const FDatasmithTessellationOptions& InTessellationOptions);
};
```

### 进阶用法

更深入的理解涉及 CAD 数据到 CADKernel 或 TechSoft 中间格式的转换。例如，`FAliasModelToCADKernelConverter` 类负责将 Alias 的 B-Rep（边界表示）几何体转换为 CADKernel 的拓扑面和边（来源：`Private/AliasModelToCADKernelConverter.h`）：

```cpp
// 负责将 Alias 模型（B-Rep）转换为 CADKernel 内部表示
class FAliasModelToCADKernelConverter : public FCADModelToCADKernelConverterBase
{
public:
    // 对已添加的几何体执行镶嵌（Tessellation），生成 FMeshDescription
    virtual bool Tessellate(const CADLibrary::FMeshParameters& InMeshParameters, 
                            FMeshDescription& OutMeshDescription) override;
    
    // 将 Alias DAG 节点的 B-Rep 几何体添加到转换器中
    bool AddBRep(const FAlDagNodePtr& DagNode, 
                 uint32 SlotID, 
                 EAliasObjectReference ObjectReference);
};
```

## Demo 示例

以下是一个简化的示例，展示如何通过 Datasmith API 间接触发包含此插件的 CAD 文件导入。实际使用中，导入通常由编辑器菜单或脚本触发。

```cpp
// MyCADImporter.h
#pragma once
#include "CoreMinimal.h"

class FMyCADImporter
{
public:
    // 使用 Datasmith 导入一个 .wire 文件
    static bool ImportWireFile(const FString& FilePath, const FString& OutputFolder);
};

// MyCADImporter.cpp
#include "MyCADImporter.h"
#include "DatasmithSceneFactory.h"
#include "DatasmithTranslator.h"
#include "DatasmithImportOptions.h"

bool FMyCADImporter::ImportWireFile(const FString& FilePath, const FString& OutputFolder)
{
    // 创建一个 Datasmith 场景
    TSharedRef<IDatasmithScene> Scene = FDatasmithSceneFactory::CreateScene(TEXT("CADImportScene"));
    
    // 配置导入选项（通常从编辑器界面获取）
    TSharedRef<FDatasmithImportOptions> ImportOptions = MakeShared<FDatasmithImportOptions>();
    // ... 设置具体的导入选项
    
    // 使用 Datasmith 翻译器（内部会调用 WireInterface 等模块）
    FDatasmithTranslator Translator;
    // 初始化并执行导入（此过程会处理 .wire 文件）
    bool bSuccess = Translator.ImportScene(FilePath, OutputFolder, Scene, ImportOptions);
    
    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("Successfully imported CAD file: %s"), *FilePath);
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to import CAD file: %s"), *FilePath);
    }
    
    return bSuccess;
}
```

## 模块依赖

该插件由多个内部模块组成，它们依赖于一些独特的外部或引擎模块。

| 模块 | 用途 |
|---|---|
| `TechSoft` | 处理来自 TechSoft 的几何内核和数据结构，用于部分 CAD 格式的解析和转换。 |
| `CADKernel` | UE 内置的 CAD 几何内核，用于进行高级的 B-Rep 几何体操作和镶嵌。 |
| `OpenNurbs6` | 处理 Rhino 3DM 等基于 NURBS 的文件格式（由 `DatasmithOpenNurbsTranslator` 模块使用）。 |
| `DatasmithSDK` | Datasmith 框架的核心 SDK，提供场景元素、导入器和翻译器的基础接口。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量隐式转换为 float 产生的编译警告。 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | 增加逻辑，确保即使安装了 Alias 2027，Wire 转换器也能正常工作。 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 将 TechSoft 依赖库更新至 2026.3 版本。 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新了 Datasmith CAD 缓存的版本标识。 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 使函数类型转换警告在 MSVC 和 Clang 编译器之间保持可移植性。 |

### 维护评价

该插件处于 **活跃维护** 状态。从近期的 Git 提交记录可以看出，开发团队仍在持续更新和优化，包括：修复兼容性问题、升级第三方依赖库、以及提升代码的健壮性和可移植性。插件创建于 2019 年，已发展 7 年，属于成熟的企业级组件。

尽管 `EnabledByDefault` 为 `false`（这是企业插件的常见设置），但它作为 Datasmith 生态系统的关键部分，得到了 Epic Games 的持续支持。

**推荐使用**：对于需要导入 Alias (.wire) 或其他 CAD 格式的 UE 项目，这是一个官方且得到积极维护的解决方案。启用后，通过 Datasmith 导入界面即可使用其全部功能。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter/Tests)