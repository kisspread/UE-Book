# Datasmith Importer

> Importer for Datasmith files.

| 属性 | 值 |
|---|---|
| 中文名 | Datasmith导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DatasmithImporter` (Runtime), `DatasmithExternalSource` (Runtime), `DatasmithNativeTranslator` (Runtime), `DatasmithTranslator` (Runtime), `DirectLinkExtension` (Runtime), `DirectLinkExtensionEditor` (Runtime), `DirectLinkTest` (Runtime), `ExternalSource` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter) | |

## 用途

Datasmith Importer 插件的核心功能是将来自工业 CAD、建筑信息模型 (BIM) 以及其他专业 3D 设计软件（如 Revit, SketchUp, 3ds Max, CATIA, SolidWorks 等）的复杂场景和资产，完整、高效地导入到虚幻引擎中。它不仅仅是一个文件转换器，更是一个智能的数据映射和优化系统。

这个插件解决的关键问题是：
1.  **数据保真度**：完整保留原始设计软件中的复杂层次结构、材质属性、灯光设置、相机视角和元数据。
2.  **工作流集成**：为建筑师、设计师和工程师提供从设计工具到实时引擎的无缝衔接，支持从导入到实时可视化的全链条。
3.  **资产优化**：自动处理网格、纹理和材质的优化，例如生成光照贴图 UV、计算合适的分辨率，确保在虚幻引擎中高效渲染。
4.  **支持批量与重导入**：能够导入单个文件、多个文件、整个文件夹，并支持增量更新（重导入）场景，保持与源设计的同步。
5.  **扩展性**：通过与 Dataprep（数据准备）工具集成，允许用户在导入前或导入过程中自动化执行资产清理和准备操作。

简而言之，Datasmith 是连接专业设计软件与虚幻引擎实时 3D 世界的桥梁，主要用于建筑可视化、产品设计展示、数字孪生和 VR/AR 体验等企业级应用。

## 使用场景

-   **你在使用 Revit 或 ArchiCAD 进行建筑设计** → 使用 Datasmith 将完整的建筑信息模型（BIM）导入虚幻引擎，保留楼层、房间、材质和门窗信息，用于创建交互式可视化或 VR 漫游。
-   **你在使用 SolidWorks 或 CATIA 设计复杂的机械产品** → 使用 Datasmith 将装配体模型连同其层次结构和材质导入 UE，用于创建产品配置器或拆解动画。
-   **你需要将 3ds Max 或 Maya 的场景批量导入 UE，并保持灯光和材质设置** → 使用 Datasmith 的文件夹导入功能，并利用其预设的材质和灯光翻译规则。
-   **你希望定期更新 UE 中的场景，以匹配上游 CAD 软件的最新设计变更** → 使用 Datasmith 的重导入功能，它会智能地只更新发生变化的部分。
-   **你想在导入前自动清理或简化数百万面的 CAD 模型** → 与 Dataprep 工具结合，使用 `UDatasmithFileProducer` 和 `UDatasmithConsumer` 在自动化流程中处理资产。

## 蓝图用法

Datasmith Importer 提供了丰富的蓝图 API，主要用于在编辑器脚本中程序化地控制导入流程。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ConstructDatasmithSceneFromFile` | 从文件路径（.udatasmith）构造一个可修改和导入的场景对象。 | `UDatasmithSceneElement` |
| `ConstructDatasmithSceneFromSourceUri` | 从 URI（如 `file://`）构造场景对象，支持更灵活的数据源。 | `UDatasmithSceneElement` |
| `GetExistingDatasmithScene` | 获取一个已存在的 `UDatasmithScene` 资产，用于后续的重导入。 | `UDatasmithSceneElement` |
| `TranslateScene` | 触发翻译阶段，将源文件数据填充到场景对象中。**必须在设置选项后、导入前调用**。 | `UDatasmithSceneElement` |
| `ImportScene` | 将翻译后的场景导入到指定的虚幻引擎内容文件夹中。 | `UDatasmithSceneElement` |
| `ReimportScene` | 重新导入一个已存在的 Datasmith 场景，更新其内容。 | `UDatasmithSceneElement` |
| `GetOptions` / `GetAllOptions` | 获取用于控制导入过程的特定类型选项对象（如网格、材质选项）。 | `UDatasmithSceneElement` |
| `ComputeLightmapResolution` | 为静态网格列表计算并应用合适的光照贴图分辨率。 | `UDatasmithStaticMeshBlueprintLibrary` |
| `SetupStaticLighting` | 为资产列表设置光照贴图 UV 生成标志和理想分辨率比率。 | `UDatasmithStaticMeshBlueprintLibrary` |

### 使用示例（蓝图描述）

**示例1：基本文件导入流程**
1.  使用 `ConstructDatasmithSceneFromFile` 节点，传入 `.udatasmith` 文件的路径，获得 `UDatasmithSceneElement` 对象。
2.  调用该对象的 `GetAllOptions` 节点，获取所有可配置的选项对象。
3.  对这些选项对象进行配置（例如设置网格合并策略）。
4.  调用 `TranslateScene` 节点进行翻译。
5.  调用 `ImportScene` 节点，并指定目标文件夹（如 `/Game/ImportedScene`）。该节点会返回一个 `FDatasmithImportFactoryCreateFileResult` 结构体，其中包含导入的演员和网格体数组。
6.  使用 `GetImportedActors` 等函数处理导入结果。

**示例2：批量导入 CAD 文件**
1.  使用 `ConstructDatasmithSceneFromCADFiles` 节点，传入多个 CAD 文件路径的数组。
2.  获取并配置选项。
3.  调用 `TranslateScene`。
4.  调用 `ImportScenes` 节点，它会返回一个数组，每个元素对应一个输入文件的导入结果。

## C++ 用法

Datasmith Importer 的 C++ API 设计为一个流水线式的导入过程，核心是 `FDatasmithImportContext` 上下文对象和一系列静态的导入器类。

### 头文件引入

```cpp
#include "DatasmithImporter.h"
#include "DatasmithImportContext.h"
#include "DatasmithBlueprintLibrary.h" // 用于蓝图结构体
```

### 基本用法

以下是一个模拟蓝图 `ImportScene` 功能的 C++ 最小流程，展示了核心步骤。
*来源参考: `DatasmithBlueprintLibrary.h`, `DatasmithImporter.h`*

```cpp
// 1. 构造场景上下文 (通常由工厂内部完成，此处为演示)
FDatasmithImportContext ImportContext(ExternalSourcePtr, /*bLoadConfig=*/true, LoggerName, LoggerLabel);

// 2. 初始化选项 (可能显示UI让用户配置)
bool bSilent = false; // 设为true则跳过UI，使用JSON配置
TSharedPtr<FJsonObject> SettingsJson = /* ... */;
if (!ImportContext.InitOptions(SettingsJson, OptionalImportPath, bSilent))
{
    // 用户取消了选项窗口
    return;
}

// 3. 设置目标包和标志
FString DestinationPath = TEXT("/Game/MyDatasmithImport");
if (!ImportContext.SetupDestination(DestinationPath, RF_Public | RF_Standalone, GWarn, /*bSilent=*/false))
{
    // 设置目标失败或用户取消
    return;
}

// 4. 加载并翻译场景 (ExternalSource 内部处理了文件读取和翻译)
if (!ExternalSourcePtr->LoadScene(ImportContext))
{
    // 加载/翻译失败
    return;
}
// 或者手动设置场景： ImportContext.InitScene(SceneElement);

// 5. 执行导入
FDatasmithImporter::FinalizeImport(ImportContext, ValidAssets);
```

### 进阶用法

更精细的控制可以分步调用各个子系统的导入和定型函数。
*来源参考: `DatasmithImporter.h`, `DatasmithStaticMeshImporter.h`, `DatasmithMaterialImporter.h`*

```cpp
// 步骤A: 过滤需要导入的元素
FDatasmithImporter::FilterElementsToImport(ImportContext);

// 步骤B: 分别导入各类资产
FDatasmithImporter::ImportStaticMeshes(ImportContext); // 导入网格到临时包
FDatasmithImporter::ImportTextures(ImportContext);    // 导入纹理
FDatasmithImporter::ImportMaterials(ImportContext);   // 导入材质

// 步骤C: 定型资产 (从临时包移动到最终包并构建)
for (auto& Pair : ImportContext.ImportedStaticMeshes)
{
    UStaticMesh* FinalMesh = FDatasmithImporter::FinalizeStaticMesh(Pair.Value, *FinalFolderPath, nullptr);
}
for (auto& Pair : ImportContext.ImportedTextures)
{
    UTexture* FinalTexture = FDatasmithImporter::FinalizeTexture(Pair.Value.Get(), *TexturePath, nullptr);
}
// ... 对材质、材质函数等执行类似操作

// 步骤D: 导入和定型演员（场景层级）
FDatasmithImporter::ImportActors(ImportContext);
TMap<UObject*, UObject*> ReferencesToRemap;
FDatasmithImporter::FinalizeActors(ImportContext, &ReferencesToRemap);

// 步骤E: 最终处理，修复引用，保存场景资产
FDatasmithImporter::FinalizeImport(ImportContext, ValidAssets);
```

## Demo 示例

这是一个展示如何在 C++ 中程序化导入一个 `.udatasmith` 文件的最小可编译示例。

*MyDatasmithImporter.h*
```cpp
#pragma once

#include "CoreMinimal.h"
#include "DatasmithImportContext.h"

class FMyDatasmithImporter
{
public:
    static bool ImportFile(const FString& FilePath, const FString& DestinationFolder);
};
```

*MyDatasmithImporter.cpp*
```cpp
#include "MyDatasmithImporter.h"
#include "DatasmithImporter.h"
#include "DatasmithExternalSource.h"
#include "DatasmithImporterUtils.h"

bool FMyDatasmithImporter::ImportFile(const FString& FilePath, const FString& DestinationFolder)
{
    // 1. 创建外部源 (代表要导入的文件)
    TSharedRef<UE::DatasmithImporter::FExternalSource> ExternalSource = MakeShared<UE::DatasmithImporter::FExternalSource>(FSourceUri(FilePath));

    // 2. 创建导入上下文
    FName LoggerName(TEXT("MyImporter"));
    FText LoggerLabel = NSLOCTEXT("MyImporter", "LogLabel", "My Datasmith Import");
    FDatasmithImportContext ImportContext(ExternalSource, /*bLoadConfig=*/true, LoggerName, LoggerLabel);

    // 3. 初始化（无UI模式，使用默认选项）
    if (!ImportContext.InitOptions(/*ImportSettingsJson=*/nullptr, DestinationFolder, /*bSilent=*/true))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to initialize import options."));
        return false;
    }

    // 4. 设置目标
    if (!ImportContext.SetupDestination(DestinationFolder, RF_Public | RF_Standalone, GWarn, /*bSilent=*/true))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to setup destination."));
        return false;
    }

    // 5. 加载并翻译场景
    if (!ExternalSource->LoadScene(ImportContext))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to load and translate scene from source."));
        return false;
    }

    // 6. 执行导入
    TSet<UObject*> ValidAssets;
    FDatasmithImporter::FinalizeImport(ImportContext, ValidAssets);

    UE_LOG(LogTemp, Log, TEXT("Datasmith import completed for: %s"), *FilePath);
    return true;
}
```

## 模块依赖

从 `DatasmithImporter.Build.cs` 分析，使用此插件的核心模块需要依赖以下特定模块：

| 模块 | 用途 |
|---|---|
| `DatasmithSDK` | 提供 Datasmith 核心数据结构（`IDatasmithScene` 等）和翻译器接口。 |
| `DatasmithTranslator` | 提供默认的场景翻译器实现。 |
| `DatasmithNativeTranslator` | 提供针对原生 `.udatasmith` 文件格式的翻译器。 |
| `DirectLinkExtension` | 提供通过 DirectLink 协议进行实时数据同步的功能。 |
| `ExternalSource` | 提供抽象的外部数据源支持。 |
| `Interchange` | (通过依赖链) 使用 Interchange 框架进行纹理导入和管道处理。 |
| `MeshDescription` | 处理和操作网格描述数据（用于网格导入和UV生成）。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下双精度常量截断为浮点数时产生的编译警告。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到更新的 UE_LOGF。 |
| 2026-04-02 | `50a24ff6` | Deprecated GetObjects*/ForEachObjectWithOuter functions that take bool bIncludeNestedObjects. Introd... | 废弃了带有 `bIncludeNestedObjects` 布尔参数的 `GetObjects*` 和 `ForEachObjectWithOuter` 函数。 |
| 2026-03-06 | `7b69892a` | clean up code changing texture properties with wrapping in PreEditChange/PostEditChange as required. | 清理修改纹理属性的代码，确保遵循 `PreEditChange/PostEditChange` 的包装要求。 |
| 2026-03-05 | `1adb9f68` | New material translator work: ... | 新材质翻译器相关工作（提交信息不完整，可能涉及翻译器逻辑的增强）。 |

### 维护评价

Datasmith Importer 是 Epic Games 官方维护的核心企业级插件，自 2019 年引入以来一直是活跃项目。

**优势：**
-   **活跃维护**：最近的提交（截至 2026 年 5 月）表明项目仍在持续维护和改进，最近的提交主要是代码质量提升、编译警告修复和内部 API 迁移。
-   **功能稳定**：作为 Epic 官方推荐的 CAD/BIM 数据导入方案，其核心功能（文件导入、场景翻译、资产定型）非常成熟稳定。
-   **生态整合**：与 Dataprep、DirectLink、Interchange 等引擎子系统深度集成，形成了一个完整的企业内容准备和导入流程。

**注意事项：**
-   **默认禁用**：此插件 `EnabledByDefault=false`，需要在编辑器的“插件”面板中手动启用，或者通过项目配置启用。
-   **复杂性**：插件体系庞大（包含8个模块），源码复杂，二次开发或深度定制需要深入理解其架构。
-   **主要面向编辑器**：大部分导入功能在编辑器环境下运行，用于打包后的运行时场景导入支持有限。

**结论**：**强烈推荐使用**。它是 UE 中处理工业设计数据的事实标准解决方案。尽管默认禁用，但其稳定性和官方支持使其成为建筑可视化、工业设计和数字孪生项目的首选工具。用户应关注其官方文档以获取最佳实践和格式支持信息。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter)
-   [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter/Tests) (路径基于常规结构推断，实际可能存在)