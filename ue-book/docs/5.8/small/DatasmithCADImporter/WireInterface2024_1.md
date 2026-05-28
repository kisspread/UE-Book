# Datasmith CAD Importer

> Collection of tools to work with CAD files.

| 属性 | 值 |
|---|---|
| 中文名 | CAD导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DatasmithCADTranslator` (Runtime), `CADLibrary` (Runtime), `WireInterface2025_0` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

## 用途

DatasmithCADImporter 是一组专用于处理 CAD 文件的工具集，其主要目的是将复杂的 CAD 软件（如 Autodesk Alias）生成的设计文件（`.wire` 格式）导入到 Unreal Engine 中。它不仅仅是一个简单的模型导入器，更是一个处理 CAD 数据转换的框架。

该插件解决了以下核心问题：
1.  **格式与数据兼容性**：将 Alias 的 DAG（有向无环图）节点结构、几何体、材质、层级关系转换为 UE 的 Datasmith 场景格式。
2.  **几何处理**：通过集成 TechSoft 或 CADKernel 库，将 CAD 文件中的精确 NURBS 曲面或网格体转换为可用于实时渲染的网格体（`FMeshDescription`）。
3.  **版本管理**：通过 `WireInterface` 模块（如 `WireInterface2024_1`， `WireInterface2025_0`）支持不同年份版本的 Alias 文件格式。
4.  **工作流集成**：作为 Datasmith 翻译器链的一部分，实现 CAD 数据与 Unreal Engine 的无缝对接，支持材质、层级、变换等信息的完整映射。

## 使用场景

-   **汽车设计**：汽车设计师使用 Alias 创建车辆外观曲面，需要将设计导入 Unreal Engine 进行可视化评审、VR 体验或制作营销素材。
-   **工业设计**：任何使用 Alias 作为主要建模工具的工业设计领域（如消费电子、家具），需要将高精度 CAD 模型带入实时引擎。
-   **数据转换管线**：作为企业级内容制作管线的一部分，用于批量或自动化地将 CAD 数据转换为游戏引擎或虚拟制作项目可用的资产。
-   **需要 CAD 精确几何的场景**：当项目对模型的曲面质量和拓扑结构有严格要求时，使用此插件比通用 FBX 导入更能保留原始设计意图。

## 蓝图用法

根据提供的源码分析，此插件的核心功能主要通过 C++ 模块提供，**没有发现标记为 `BlueprintCallable` 或 `BlueprintReadWrite` 的公开蓝图接口**。其交互主要发生在 Datasmith 导入流程的底层。

主要的“使用”方式是通过 Datasmith 导入器自动调用。当在 Unreal Editor 中导入 `.wire` 文件时，系统会自动加载并使用 `DatasmithCADTranslator` 和对应的 `WireInterface` 模块进行处理。

## C++ 用法

### 头文件引入

使用此插件主要需要引入以下模块的头文件：
```cpp
#include "DatasmithCADTranslatorModule.h"
// 根据具体功能，可能需要引入 WireInterface 的头文件
#include "WireInterfaceModule.h"
// 以及 CAD 核心库
#include "CADLibrary.h"
```

### 基本用法（加载与初始化）

核心翻译器通过 `IWireInterface` 接口进行操作。以下是基于 `FWireTranslatorImpl` 类的基本使用流程（概念性示例）：

**来源文件：** `Private/WireInterfaceImpl.h`

```cpp
// 1. 获取模块实例（通常由 Datasmith 导入器内部完成）
FDatasmithWireTranslatorModule& WireModule = FDatasmithWireTranslatorModule::Get();
if (!WireModule.IsAvailable())
{
    // 处理模块不可用的情况
    return;
}

// 2. 创建 Wire 翻译器实例（具体实现由版本模块提供，例如 WireInterface2025_0）
// 实际使用中，此实例通常由 DatasmithCADTranslator 模块根据文件版本创建
TSharedPtr<UE_DATASMITHWIRETRANSLATOR_NAMESPACE::IWireInterface> WireTranslator = /* ... */;

// 3. 初始化翻译器，传入 Wire 文件路径
const TCHAR* ScenePath = TEXT("D:/Design/model.wire");
if (!WireTranslator->Initialize(ScenePath))
{
    // 处理初始化失败
    return;
}

// 4. 设置导入选项和输出路径
FWireSettings ImportSettings;
ImportSettings.SomeOption = /* ... */;
WireTranslator->SetImportSettings(ImportSettings);
WireTranslator->SetOutputPath(TEXT("D:/UE_Project/Content/ImportedModel/"));

// 5. 创建一个空的 Datasmith 场景并加载
TSharedPtr<IDatasmithScene> DatasmithScene = /* ... */;
if (!WireTranslator->Load(DatasmithScene))
{
    // 处理加载失败
    return;
}

// 此时，DatasmithScene 中已经填充了从 .wire 文件转换而来的 Actor、Mesh、Material 等元素
// 后续由 Datasmith 导入器将场景元素创建为 UE 资产
```

### 进阶用法（模型遍历与材质处理）

`FWireTranslatorImpl` 内部实现了复杂的模型遍历逻辑，将 Alias 的 DAG 结构映射到 Datasmith 的层次结构。

**来源文件：** `Private/WireInterfaceImpl.h`， `Private/OpenModelUtils.h`

```cpp
// 内部遍历示例（在 FWireTranslatorImpl::TraverseModel 中）
// 1. 从根节点开始深度遍历 DAG
TSharedPtr<IDatasmithActorElement> RootActor = TraverseDag(RootDagNode);

// 2. 根据节点类型分派处理
TSharedPtr<IDatasmithActorElement> TraverseDag(const FAlDagNodePtr& DagNode)
{
    if (!DagNode || !DagNode.IsVisible()) return nullptr;

    TSharedPtr<IDatasmithActorElement> ActorElement;
    if (DagNode.HasGeometry())
    {
        // 处理几何节点（Mesh, Surface, Shell）
        ActorElement = ProcessGeometryNode(DagNode);
    }
    else if (DagNode.IsAGroup())
    {
        // 处理组节点，递归遍历子节点
        ActorElement = TraverseGroupNode(DagNode);
    }
    // ... 设置 Actor 的变换、查找或创建对应的 Mesh 和 Material 等
    if (ActorElement)
    {
        // 应用从 Alias 节点获取的全局变换矩阵
        DagNode.SetActorTransform(*ActorElement);
    }
    return ActorElement;
}

// 3. 材质创建（从 Alias 的 AlShader 转换）
TSharedPtr<IDatasmithBaseMaterialElement> FindOrAddMaterial(const TAlObjectPtr<AlShader>& Shader)
{
    // 检查缓存
    FString ShaderName = Shader->GetName();
    if (TSharedPtr<IDatasmithBaseMaterialElement>* Found = ShaderNameToMaterial.Find(ShaderName))
    {
        return *Found;
    }
    // 根据着色器模型类型（BLINN, PHONG等）创建对应的 PBR 材质
    TSharedPtr<IDatasmithUEPbrMaterialElement> MaterialElement = /* ... */;
    switch (Shader->GetModelType())
    {
    case EAlShaderModelType::PHONG:
        AddAlPhongParameters(Shader, MaterialElement);
        break;
    // ... 其他类型
    }
    ShaderNameToMaterial.Add(ShaderName, MaterialElement);
    return MaterialElement;
}
```

## Demo 示例

以下是一个最小化的 C++ 示例，演示如何加载并查询一个 `.wire` 文件的基本信息。

**WireImporterDemo.h**
```cpp
#pragma once
#include "CoreMinimal.h"

class FWireImporterDemo
{
public:
    /** 尝试加载一个 .wire 文件并打印其根节点信息 */
    static void ImportAndPrintInfo(const FString& WireFilePath);
};
```

**WireImporterDemo.cpp**
```cpp
#include "WireImporterDemo.h"
#include "WireInterfaceModule.h"
#include "DatasmithTranslatorModule.h"
#include "IWireInterface.h"

using namespace UE_DATASMITHWIRETRANSLATOR_NAMESPACE;

void FWireImporterDemo::ImportAndPrintInfo(const FString& WireFilePath)
{
    // 1. 确保 WireInterface 模块可用
    FDatasmithWireTranslatorModule& WireModule = FDatasmithWireTranslatorModule::Get();
    if (!WireModule.IsAvailable())
    {
        UE_LOG(LogTemp, Error, TEXT("Datasmith Wire Translator module is not available."));
        return;
    }

    // 注意：IWireInterface 的具体实例（如 FWireTranslatorImpl）通常由翻译器模块内部创建。
    // 以下为模拟创建过程，实际项目中应通过 FDatasmithCADTranslatorModule 获取正确的翻译器。
    // TSharedPtr<IWireInterface> Translator = FDatasmithCADTranslatorModule::Get().CreateTranslatorForFile(WireFilePath);

    // 2. 为演示，我们假设已获得一个 Translator 实例
    TSharedPtr<IWireInterface> Translator = /* 通过合适的方式获取 */;
    if (!Translator.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create Wire translator for file: %s"), *WireFilePath);
        return;
    }

    // 3. 初始化并加载
    if (!Translator->Initialize(*WireFilePath))
    {
        UE_LOG(LogTemp, Error, TEXT("Initialization failed for: %s"), *WireFilePath);
        return;
    }

    FWireSettings Settings;
    Translator->SetImportSettings(Settings);

    TSharedPtr<IDatasmithScene> Scene = FDatasmithSceneFactory::CreateScene(TEXT("DemoScene"));
    if (Translator->Load(Scene))
    {
        UE_LOG(LogTemp, Log, TEXT("Successfully loaded Wire file: %s"), *WireFilePath);
        UE_LOG(LogTemp, Log, TEXT("Root actors count: %d"), Scene->GetActorsCount());
        // 可以进一步遍历 Scene 中的元素进行分析...
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Loading failed for: %s"), *WireFilePath);
    }
}
```

## 模块依赖

要使用 DatasmithCADImporter 插件，你的模块需要依赖其提供的特定模块。以下为关键依赖项（已排除常见的 Core/Engine 等基础模块）：

| 模块 | 用途 |
|---|---|
| `DatasmithCADTranslator` | 核心翻译器模块，管理不同 CAD 格式的翻译器创建和调度。 |
| `CADLibrary` | CAD 核心功能库，提供 CAD 数据模型、几何处理工具等通用功能。 |
| `WireInterface2025_0` | 具体版本的 Alias .wire 文件解析与翻译实现（此处以2025.0版本为例）。 |
| `TechSoft` (如使用) | 提供高级的 CAD 数据转换与曲面处理能力，是某些转换路径的后端依赖。 |
| `CADKernelSurface` (如使用) | 提供基于 CADKernel 的曲面细分和网格生成能力。 |

**注意：** 该插件默认未启用。在项目的 `.uproject` 文件或编辑器插件设置中，你需要手动启用 `DatasmithCADImporter`。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下 double 常量截断为 float 的警告。 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | 增加逻辑以支持在安装了 Alias 2027 的环境下，Wire 翻译器仍能工作。 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 将 TechSoft 库更新至 2026.3 版本。 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新了 DatasmithCAD 的缓存版本。 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 使函数类型转换警告在 MSVC 和 Clang 编译器之间更具可移植性。 |

### 维护评价

该插件**处于活跃维护状态**。
-   **创建时间**：约 6 年前（2019年），属于成熟的商业级插件。
-   **更新频率**：近期（2026年5月）有密集的更新活动，表明仍在积极开发。
-   **维护内容**：近期更新主要包括**兼容性改进**（支持新版 Alias）、**依赖更新**（TechSoft）和**编译问题修复**，这些都是保持插件与现代软件环境同步的关键工作。
-   **已知限制**：需要特定的第三方库（TechSoft）支持，这可能增加集成复杂性。默认未启用，用户需主动配置。
-   **推荐**：对于需要将 Alias（.wire）文件高保真导入 Unreal Engine 的汽车、工业设计等工作流，**强烈推荐使用**。它提供了比通用格式更精确的数据转换。对于简单的模型导入，可能过于重型。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例] (根据插件结构，测试文件通常位于 `Engine/Plugins/Enterprise/DatasmithCADImporter/Tests/` 或 `Engine/Tests/DatasmithCADImporter/` 目录下)