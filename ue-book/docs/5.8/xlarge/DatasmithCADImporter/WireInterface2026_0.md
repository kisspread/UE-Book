# Datasmith CAD Importer

> Collection of tools to work with CAD files.

| 属性 | 值 |
|---|---|
| 中文名 | CAD 导入工具集 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CADInterfaces` (Runtime), `CADKernelSurface` (Runtime), `CADLibrary` (Runtime), `CADTools` (Runtime), `DatasmithCADTranslator` (Runtime), `DatasmithDispatcher` (Runtime), `DatasmithOpenNurbsTranslator` (Runtime), `DatasmithPLMXMLTranslator` (Runtime), `DatasmithWireTranslator` (Runtime), `ParametricSurface` (Runtime), `ParametricSurfaceExtension` (Runtime), `WireInterface2020` (Runtime), `WireInterface2021_3` (Runtime), `WireInterface2022` (Runtime), `WireInterface2022_1` (Runtime), `WireInterface2022_2` (Runtime), `WireInterface2023_0` (Runtime), `WireInterface2023_1` (Runtime), `WireInterface2024_1` (Runtime), `WireInterface2025_0` (Runtime), `WireInterface2026_0` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

## 用途

这是一个为**工业级 CAD 数据**（如 Alias/Wire、Step、IGES、Parasolid、JT 等）提供高级导入支持的插件集合。它不仅仅是简单的格式转换，更是一个**完整的 CAD 模型处理与转换管线**。

插件解决的核心问题是：将带有精确 B-Rep（边界表示）拓扑、修剪曲线、参数化曲面的复杂 CAD 模型，可靠地转换为 UE 可用的 Datasmith 场景和 Mesh。这与普通的多边形网格导入有本质区别，它专注于保留 CAD 模型的设计意图和几何精度，是面向制造业、汽车设计、工业仿真等领域的专业工具。

插件的结构高度模块化，`DatasmithCADTranslator` 是主协调器，而不同的 `WireInterface20XX` 模块则对应特定年份版本的 Alias/Wire CAD 软件内核，以确保与不同版本软件的兼容性。

## 使用场景

- **汽车/工业设计**：你需要将 Autodesk Alias 创建的复杂车身 A 级曲面 (.wire) 导入 UE5 进行实时可视化评审。
- **数字孪生/虚拟仿真**：你需要将 CAD 软件（如 CATIA, NX, SolidWorks）导出的 STEP/IGES 模型导入引擎，用于创建精确的虚拟样机或仿真环境。
- **建筑信息模型 (BIM)**：你需要处理 PLMXML 等格式的模型数据。
- **需要高精度模型**：你的项目依赖于模型的精确几何信息，而不仅仅是视觉外观。

## 蓝图用法

该插件主要作为数据导入管线的一部分，由 Datasmith 导入流程在后台调用，**不直接向蓝图暴露大量可调用的函数**。其核心功能通过 Datasmith 的通用导入界面（如 Datasmith Scene Import UI）触发。

### 核心节点

该模块的主要 API 是 C++ 侧的接口，蓝图直接交互较少。与蓝图的交互主要发生在数据导入完成后，通过 Datasmith Actor 层级和资产进行。

| 节点 | 说明 | 所在类 |
|---|---|---|
| （无直接蓝图可调用节点） | 该插件的蓝图接口通过 Datasmith 导入流程间接使用 | `IDatasmithTranslator` (C++ 接口) |

### 使用示例（蓝图描述）

1.  在编辑器内容浏览器中，右键点击，选择 **Import**。
2.  在文件选择对话框中，选择一个支持的 CAD 文件（如 .wire, .step, .iges）。
3.  **Datasmith CAD Importer** 插件会作为可用的导入器出现在导入选项中。
4.  配置导入选项（如曲面细分精度、单位等），点击导入。
5.  插件会将 CAD 数据转换为 `.udatasmith` 资产，并生成相应的 Mesh 和材质资产，最终以 Datasmith Actor 的形式放置到场景中。

## C++ 用法

该插件的 C++ 用法主要体现在**开发自定义翻译器**或**扩展导入管线**时。它提供了一套内部接口和转换器基类。

### 头文件引入

```cpp
#include "WireInterfaceModule.h"
```

### 基本用法

该模块没有公开的“基础用法”，因为它是一个**基础设施插件**。其使用方式是通过实现 `IWireInterface` 接口来完成具体的 CAD 文件解析。
以下代码展示了翻译器模块的核心结构（概念性代码，来源于 `WireInterfaceImpl.h`）：

```cpp
// 来源：Source/WireInterface/WireInterface2026_0/Private/WireInterfaceImpl.h
// FWireTranslatorImpl 实现了 IWireInterface 接口，负责具体的 .wire 文件处理。
namespace UE_DATASMITHWIRETRANSLATOR_NAMESPACE
{
    class FWireTranslatorImpl : public IWireInterface
    {
    public:
        // 初始化翻译器，传入场景文件路径
        virtual bool Initialize(const TCHAR* InSceneFullName) override;
        // 加载场景数据到 DatasmithScene
        virtual bool Load(TSharedPtr<IDatasmithScene> InScene) override;
        // 设置导入选项
        virtual void SetImportSettings(const FWireSettings& Options) override;
        
        // 核心：加载静态网格体数据
        bool LoadStaticMesh(const TSharedPtr<IDatasmithMeshElement> MeshElement, 
                            FDatasmithMeshElementPayload& OutMeshPayload,
                            const FDatasmithTessellationOptions& InTessellationOptions);
        // ... 内部模型遍历、材质创建、几何检索等私有方法。
    };
}
```

### 进阶用法

开发者可以基于 `CADLibrary` 模块中的 `ICADModelConverter` 接口，以及 `CADKernelSurface` 等模块提供的功能，编写自定义的 CAD 转换器。例如，`AliasModelToCADKernelConverter.h` 展示了如何将 Alias 的 `AlDagNode` 转换为 UE::CADKernel 的 `FTopologicalFace`。

```cpp
// 概念性进阶用法，展示转换器扩展点
// 来源：Source/WireInterface/WireInterface2026_0/Private/AliasModelToCADKernelConverter.h
class FAliasModelToCADKernelConverter : public FCADModelToCADKernelConverterBase
{
public:
    // 覆盖基类的曲面细分方法
    virtual bool Tessellate(const CADLibrary::FMeshParameters& InMeshParameters, FMeshDescription& OutMeshDescription) override;
    
    // 添加 B-Rep 几何体（边界表示）
    bool AddBRep(const FAlDagNodePtr& DagNode, const FColor& Color, EAliasObjectReference ObjectReference);
    
    // 内部使用 AddFace, AddShell 等方法构建 CADKernel 拓扑
    // ...
};
```

## Demo 示例

该插件是一个复杂的后端服务，没有简单的可独立编译运行的最小示例。其完整功能需要配合整个 Datasmith 导入管线和特定的 CAD 文件才能体现。最佳的“示例”是通过 UE 编辑器的导入功能测试一个 `.wire` 或 `.step` 文件。

一个概念性的、模拟插件初始化的片段如下：

```cpp
// MyCADProcessingModule.h
#pragma once
#include "Modules/ModuleManager.h"

class FMyCADProcessingModule : public IModuleInterface
{
public:
    /** IModuleInterface implementation */
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

    // 模拟调用 WireInterface 来初始化和处理一个模型
    void ProcessSampleCADFile(const FString& FilePath);
};

// MyCADProcessingModule.cpp
#include "MyCADProcessingModule.h"
#include "WireInterfaceModule.h" // 引入 WireInterface 模块
#include "WireInterfaceImpl.h"  // 引入具体的实现类

void FMyCADProcessingModule::StartupModule()
{
    // 模块启动时可以做一些准备工作
}

void FMyCADProcessingModule::ShutdownModule()
{
}

void FMyCADProcessingModule::ProcessSampleCADFile(const FString& FilePath)
{
    // 1. 获取 WireInterface 模块实例
    if (UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FDatasmithWireTranslatorModule::IsAvailable())
    {
        auto& WireModule = UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FDatasmithWireTranslatorModule::Get();
        UE_LOG(LogTemp, Log, TEXT("Wire Interface Temp Directory: %s"), *WireModule.GetTempDir());
    }

    // 2. 创建具体的翻译器实现（实际中由 Datasmith 调度器创建）
    TSharedPtr<UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FWireTranslatorImpl> Translator = 
        MakeShareable(new UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FWireTranslatorImpl());

    // 3. 设置并加载（简化流程）
    if (Translator->Initialize(*FilePath))
    {
        TSharedPtr<IDatasmithScene> Scene = FDatasmithSceneFactory::CreateScene(TEXT("SampleScene"));
        Translator->Load(Scene);
        // ... 后续将 Scene 导入到引擎
    }
}
```

**注意**：以上代码仅为演示模块和类的依赖关系，实际使用时，导入流程由引擎的 Datasmith 子系统统一管理，用户无需手动实例化 `FWireTranslatorImpl`。

## 模块依赖

该插件依赖于两个关键的第三方技术库，这是使用者在构建项目或扩展功能时必须配置的依赖。

| 模块 | 用途 |
|---|---|
| `TechSoft` | 核心的 CAD 几何内核库，用于处理多种工业 CAD 格式（如 STEP, IGES, JT）的几何和拓扑数据。是 `CADInterfaces` 模块的直接依赖。 |
| `OpenNurbs6` | 用于处理 Rhino 3D 软件使用的 .3dm 文件格式，是 `DatasmithOpenNurbsTranslator` 模块的依赖。 |

*其他如 `Core`, `Engine`, `DatasmithCore`, `MeshDescription` 等为通用依赖，不予列出。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了严格浮点模式下 double 常量截断为 float 的编译警告。 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | 增加逻辑，使 Wire 翻译器在安装 Alias 2027 后仍能工作。 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 将 TechSoft 库更新至 2026.3 版本。 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新了 Datasmith CAD 缓存的版本。 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 使函数类型转换警告在 MSVC 和 Clang 编译器间保持可移植性。 |

### 维护评价

该插件仍在**积极维护**中。最近的提交（2026年5月）显示团队正在处理兼容性问题（如支持 Alias 2027）、升级关键依赖（TechSoft）以及进行编译器警告清理。这属于**正常的维护和迭代**。

- **优点**：更新频率稳定，跟随 UE 版本和主要 CAD 软件版本更新，保障了工业管线的长期可用性。
- **注意事项**：该插件**默认禁用** (`EnabledByDefault: false`)，且属于**企业版** (`Enterprise`) 功能。用户需要在插件设置中手动启用，并可能需要获得相应的授权。
- **推荐**：如果你的项目涉及从专业 CAD 软件导入高精度模型，此插件是**必要且值得信赖**的选择。对于简单的多边形模型导入，可以使用更轻量级的工具。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例]（未在给定信息中明确指定，通常位于引擎的自动化测试模块中）