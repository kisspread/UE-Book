# Datasmith CAD Importer

> Collection of tools to work with CAD files.

| 属性 | 值 |
|---|---|
| 中文名 | 数据架构CAD导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CADInterfaces` (Runtime), `CADKernelSurface` (Runtime), `CADLibrary` (Runtime), `CADTools` (Runtime), `DatasmithCADTranslator` (Runtime), `DatasmithDispatcher` (Runtime), `DatasmithOpenNurbsTranslator` (Runtime), `DatasmithPLMXMLTranslator` (Runtime), `DatasmithWireTranslator` (Runtime), `ParametricSurface` (Runtime), `ParametricSurfaceExtension` (Runtime), `WireInterface2020` (Runtime), `WireInterface2021_3` (Runtime), `WireInterface2022` (Runtime), `WireInterface2022_1` (Runtime), `WireInterface2022_2` (Runtime), `WireInterface2023_0` (Runtime), `WireInterface2023_1` (Runtime), `WireInterface2024_1` (Runtime), `WireInterface2025_0` (Runtime), `WireInterface2026_0` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

## 用途

DatasmithCADImporter 是一个功能庞大的企业级插件集，其核心用途是为 Unreal Engine 提供对多种专业 CAD（计算机辅助设计）和工业设计格式文件的直接导入支持。它不仅仅是一个简单的文件转换器，而是一个完整的数据转换和处理管线。

**解决的问题：**
1.  **格式兼容性**：直接支持如 Autodesk Alias (.wire)、NURBS (.3dm)、PLMXML 等工业级、高精度的 CAD 格式，这些格式通常包含参数化曲面、贝塞尔曲线、修剪边界等复杂几何信息，无法被引擎标准网格导入流程处理。
2.  **数据保真度**：将 CAD 模型中精确的几何形状（B-Rep）转换为引擎可用的三角化网格（Mesh），同时尽可能保留原始设计意图、层级结构、材质属性和变换信息。
3.  **流程集成**：通过 Datasmith 框架，将转换后的模型资产（包括几何体、材质、场景层次）无缝导入到 UE 项目中，支持自动或手动重新导入以同步设计变更。

简而言之，这个插件是连接高端工业设计软件（如 CAD、CAID）与实时 3D 引擎（Unreal Engine）之间的关键桥梁，让建筑、汽车、产品设计等领域的资产能够高效、高质量地进入游戏引擎或可视化应用。

## 使用场景

-   **建筑与施工（AEC）**：从 Revit、CATIA、SolidWorks 等软件导出的复杂 BIM 模型，需要导入 UE 进行实时可视化、虚拟样板间或施工流程模拟。
-   **汽车设计与制造**：汽车内外饰的 Alias 曲面模型 (.wire) 需要导入 UE 进行评审、配置器开发或营销材料制作。
-   **工业产品可视化**：高端消费电子、家电等产品的参数化 CAD 模型，用于创建产品展示、交互式手册或数字孪生。
-   **虚拟仿真与培训**：将精密的机械装配体 CAD 模型导入 UE，用于创建交互式维修手册、操作培训或数字孪生仿真环境。

## 蓝图用法

DatasmithCADImporter 主要作为一个底层的翻译器和转换器库存在，其核心功能（如解析.wire文件、转换NURBS曲面）并不直接暴露给蓝图。蓝图用户通常通过以下方式间接受益：

1.  **Datasmith 导入流程**：当在编辑器中通过 `Datasmith` > `Import` 菜单导入一个支持的 CAD 文件（如 .wire, .3dm）时，引擎会自动调用此插件中对应的翻译器模块完成转换。
2.  **Datasmith 场景重新导入**：对于已通过 Datasmith 导入的场景资产，修改源 CAD 文件后，在内容浏览器中右键选择“重新导入 Datasmith 场景”会再次触发这些翻译器进行更新。

因此，**蓝图节点层面没有可直接调用的核心函数**。所有操作都封装在编辑器菜单和资产管理流程中。

## C++ 用法

此插件的 C++ 接口主要供引擎内部或其他高级插件扩展使用，以集成新的 CAD 格式翻译器。

### 头文件引入

```cpp
#include “WireInterfaceModule.h”
#include “IWireInterface.h” // 核心接口，所有 Wire (.wire) 翻译器的基类
#include “CADLibrary/Public/CADModelConverterBase.h” // CAD 模型转换基类
```

### 基本用法：初始化与加载一个 .wire 文件

以下代码展示了如何使用 `FWireTranslatorImpl`（来自 `WireInterface2023_1` 模块）来加载一个 Alias 文件。

```cpp
// 来源: Private/WireInterfaceImpl.h - FWireTranslatorImpl 类
void ImportWireFile(const FString& WireFilePath)
{
    // 1. 创建翻译器实例（需要选择正确的 WireInterface 版本模块）
    auto Translator = MakeShared<UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FWireTranslatorImpl>();

    // 2. 初始化翻译器，传入源文件路径
    if (!Translator->Initialize(*WireFilePath))
    {
        UE_LOG(LogTemp, Error, TEXT(“Failed to initialize wire translator for: %s”), *WireFilePath);
        return;
    }

    // 3. 设置导入选项（如曲面细分精度）
    FWireSettings ImportSettings;
    // ... 配置 ImportSettings 字段
    Translator->SetImportSettings(ImportSettings);

    // 4. 创建一个空的 Datasmith 场景对象用于接收数据
    TSharedPtr<IDatasmithScene> DatasmithScene = FDatasmithSceneFactory::CreateScene(*FPaths::GetBaseFilename(WireFilePath));

    // 5. 执行加载，将 .wire 文件内容解析并填充到 DatasmithScene
    if (!Translator->Load(DatasmithScene))
    {
        UE_LOG(LogTemp, Error, TEXT(“Failed to load wire file: %s”), *WireFilePath);
        return;
    }

    // 6. 此时，DatasmithScene 包含了从 .wire 文件转换而来的所有 Actor、Mesh、Material 等元素
    // 通常，Datasmith Importer 会接手后续步骤，将此场景序列化为 .udatasmith 文件并导入项目。
    // 这里可以遍历 DatasmithScene 获取信息：
    for (int32 i = 0; i < DatasmithScene->GetActorsCount(); ++i)
    {
        TSharedPtr<IDatasmithActorElement> Actor = DatasmithScene->GetActor(i);
        UE_LOG(LogTemp, Log, TEXT(“Found Actor: %s”), *Actor->GetName());
    }
}
```

### 进阶用法：自定义转换管线

对于需要深度集成 CAD 数据的项目，可以扩展或替换默认的转换器。以下展示了如何继承并实现一个将 Alias 几何体转换为自定义格式的转换器。

```cpp
// 来源: Private/AliasModelToCADKernelConverter.h - FAliasModelToCADKernelConverter
// 这是一个将 Alias 几何体转换为 UE 内部 CADKernel 表示的示例。
#include “CADKernel/Core/Session.h” // CADKernel 是 UE 的内部 CAD 内核

class FMyCustomAliasConverter : public UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FAliasModelToCADKernelConverter
{
public:
    FMyCustomAliasConverter(const FDatasmithTessellationOptions& Options, CADLibrary::FImportParameters InImportParameters)
        : FAliasModelToCADKernelConverter(Options, InImportParameters)
    {
    }

    // 重写 AddGeometry 以拦截并处理特定的几何体
    virtual bool AddGeometry(const CADLibrary::FCADModelGeometry& Geometry) override
    {
        // 检查几何体是否为 Alias DAG 节点
        if (const auto* AliasGeometry = static_cast<const UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FAliasGeometry*>(&Geometry))
        {
            // 对特定类型的几何体进行特殊处理
            // 例如，只导入可见层的几何体
            if (AliasGeometry->Reference == UE_DATASMITHWIRETRANSLATOR_NAMESPACE::EAliasObjectReference::LocalReference)
            {
                // 调用基类方法进行默认处理
                return FAliasModelToCADKernelConverter::AddGeometry(Geometry);
            }
            return true; // 跳过其他参考系的几何体
        }
        return FAliasModelToCADKernelConverter::AddGeometry(Geometry);
    }

    // 可以在此实现自定义的网格细分或拓扑修复逻辑
    virtual bool RepairTopology() override
    {
        // 在调用基类的通用修复之前，添加自定义的 CAD 特定修复规则
        // 例如，处理特定版本 Alias 文件中已知的拓扑问题
        bool bBaseResult = FAliasModelToCADKernelConverter::RepairTopology();
        // ... 添加自定义修复逻辑 ...
        return bBaseResult;
    }
};
```

## Demo 示例

一个最小的、可运行的示例，展示如何通过代码触发一个 .wire 文件的导入流程（通常由编辑器工具调用）。

**WireImporterDemo.h**
```cpp
#pragma once
#include “CoreMinimal.h”
#include “IWireInterface.h” // 需要依赖 DatasmithCADTranslator 模块

class FWireImporterDemo
{
public:
    static bool ImportWireToDatasmithScene(const FString& SourceFilePath, const FString& OutputDirectory);
};
```

**WireImporterDemo.cpp**
```cpp
#include “WireImporterDemo.h”
#include “DatasmithSceneFactory.h”
#include “WireInterfaceModule.h”

bool FWireImporterDemo::ImportWireToDatasmithScene(const FString& SourceFilePath, const FString& OutputDirectory)
{
    // 注意：实际使用中，WireInterface 的版本需要与目标 Alias 文件版本匹配。
    // 这里仅为演示，实际应根据需要加载的模块名进行动态加载。
    if (!FModuleManager::Get().IsModuleLoaded(UE_DATASMITHWIRETRANSLATOR_MODULE_NAME))
    {
        UE_LOG(LogTemp, Warning, TEXT(“Wire translator module is not loaded.”));
        return false;
    }

    // 通过模块获取翻译器实例（此处为简化，直接使用已知的实现类）
    // 在实际的 Datasmith 流程中，会根据文件扩展名选择翻译器。
    auto Translator = MakeShared<UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FWireTranslatorImpl>();

    // 步骤 1: 初始化
    if (!Translator->Initialize(*SourceFilePath))
    {
        UE_LOG(LogTemp, Error, TEXT(“Initialization failed for file: %s”), *SourceFilePath);
        return false;
    }

    // 步骤 2: 配置（可选）
    FWireSettings Settings;
    Translator->SetImportSettings(Settings);
    Translator->SetOutputPath(OutputDirectory);

    // 步骤 3: 创建目标 Datasmith 场景
    FString SceneName = FPaths::GetBaseFilename(SourceFilePath);
    TSharedPtr<IDatasmithScene> TargetScene = FDatasmithSceneFactory::CreateScene(*SceneName);

    // 步骤 4: 执行转换/加载
    if (!Translator->Load(TargetScene))
    {
        UE_LOG(LogTemp, Error, TEXT(“Loading/Conversion failed for file: %s”), *SourceFilePath);
        return false;
    }

    UE_LOG(LogTemp, Log, TEXT(“Successfully processed %s. Scene contains %d actors.”),
        *SourceFilePath, TargetScene->GetActorsCount());

    // 步骤 5：（后续）将 TargetScene 序列化保存为 .udatasmith 文件
    // 此步骤通常由 FDatasmithSceneExporter 或编辑器导入工具完成，此处省略。
    return true;
}
```

## 模块依赖

要在自己的模块中使用此插件提供的功能（例如，实现自定义的 CAD 格式支持），需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `DatasmithCADTranslator` | 提供 Datasmith 翻译器的基类和 CAD 相关的公共接口。 |
| `CADLibrary` | CAD 数据处理的核心库，包含几何体表示、转换参数、模型转换器基类等。 |
| `CADInterfaces` | 定义了与外部 CAD 库（如 TechSoft）交互的接口层。 |
| `TechSoft` | TechSoft 公司提供的 3D 数据访问库（HOOPS），用于读写多种 3D 和 CAD 格式（非开源）。 |
| `OpenNurbs6` | 用于读写 Rhinoceros (.3dm) 文件格式的开源库。 |
| `CADKernel` | UE 内部的 CAD 几何内核，用于 B-Rep 数据的表示、操作和三角化。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下 double 常量截断为 float 导致的编译警告。 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | 增加逻辑，使 Wire 翻译器即使在安装了 Alias 2027 的环境下也能工作。 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 将第三方库 TechSoft 更新至 2026.3 版本。 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新了 DatasmithCAD 缓存的版本。 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 使函数类型转换警告在 MSVC 和 Clang 编译器之间可移植。 |

### 维护评价

**评价：活跃维护中，推荐用于生产环境。**

-   **创建与成熟度**：该插件自 2019 年引入，已有 6 年历史，属于成熟的“老古董”级插件。其代码结构复杂，模块众多，表明它是一个经过长期打磨的核心功能模块。
-   **维护活跃度**：最近的更新集中在 **2026 年 5 月**，且内容包含重要的功能更新（支持 Alias 2027）、第三方库升级（TechSoft）和编译兼容性修复。这表明它仍在被 **积极维护和更新**，以支持最新的行业软件版本和编译器。
-   **适用性**：作为 Epic 官方维护的企业版插件，其稳定性和功能完整性有保障。对于需要将高端 CAD 数据引入 UE 的项目（特别是汽车、建筑可视化），它是**推荐且必要**的工具。注意它默认未启用，需在项目设置中手动开启，并且依赖非开源的 TechSoft 库，这可能涉及额外的许可证。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter/Tests)