# Datasmith Importer

> Importer for Datasmith files.

| 属性 | 值 |
|---|---|
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DatasmithExternalSource` (Runtime), `DatasmithImporter` (Runtime), `DatasmithNativeTranslator` (Runtime), `DatasmithTranslator` (Runtime), `DirectLinkExtension` (Runtime), `DirectLinkExtensionEditor` (Runtime), `DirectLinkTest` (Runtime), `ExternalSource.build` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithImporter) | |

## 用途

Datasmith Importer 是一个企业级插件，其核心功能远不止于简单的文件导入。它充当了连接 CAD、BIM 及其他专业设计软件（如 Revit, 3ds Max, SketchUp, SolidWorks 等）与 Unreal Engine 之间的**桥梁和转换引擎**。

该插件解决的核心问题是：**如何将复杂、高精度、包含丰富元数据的工业设计数据，高效、准确地转换为 UE 可用的实时 3D 资产（静态网格体、材质、灯光、相机、层级结构等），并支持增量更新和实时同步。**

它通过以下方式实现：
1.  **翻译层**：通过 `DatasmithTranslator` 模块定义通用接口，由 `DatasmithNativeTranslator` 等模块实现对特定文件格式（如 `.udatasmith`）的解析。
2.  **导入管线**：`DatasmithImporter` 模块包含一系列专用的导入器（如 `FDatasmithStaticMeshImporter`, `FDatasmithMaterialImporter`），负责将翻译后的数据转换为 UE 资产。
3.  **实时链接**：`DirectLinkExtension` 模块支持通过 DirectLink 协议与源应用程序建立实时连接，实现资产的实时同步更新。
4.  **蓝图与脚本支持**：提供 `UDatasmithSceneElement` 等蓝图接口，允许通过蓝图或 Python 脚本控制导入流程。

## 使用场景

-   **建筑可视化 (Arch Viz)**：将 Revit 或 ArchiCAD 的 BIM 模型导入 UE，用于创建交互式建筑漫游或 VR 体验。
-   **产品设计与制造**：导入 SolidWorks、CATIA 或 NX 的 CAD 模型，用于产品配置器、装配说明或虚拟展示。
-   **工业仿真与培训**：将工厂布局或复杂机械的 CAD 数据导入 UE，用于创建操作培训模拟或数字孪生。
-   **影视与广播**：从 3ds Max、Maya 或 Cinema 4D 导入场景，利用 UE 的实时渲染能力进行虚拟制片。
-   **需要增量更新的项目**：当源设计文件发生修改时，使用 Datasmith 的“重新导入”功能，仅更新变化的部分，保留 UE 中已做的修改（如材质调整、蓝图逻辑）。

## 蓝图用法

Datasmith 提供了丰富的蓝图 API，主要通过 `UDatasmithSceneElement` 类暴露。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Construct Datasmith Scene From File` | 从磁盘上的 `.udatasmith` 文件创建一个可操作的场景对象。 | `UDatasmithSceneElement` |
| `Construct Datasmith Scene From Source Uri` | 通过 URI（如 `file://` 或 DirectLink URI）创建场景对象。 | `UDatasmithSceneElement` |
| `Translate Scene` | 触发翻译阶段，将源数据解析为内部场景表示。必须在设置选项后、导入前调用。 | `UDatasmithSceneElement` |
| `Import Scene` | 将翻译后的场景导入到指定的 UE 内容文件夹中，生成资产和 Actor。 | `UDatasmithSceneElement` |
| `Get Existing Datasmith Scene` | 获取一个已存在的 `UDatasmithScene` 资产对应的场景元素，用于重新导入或检查。 | `UDatasmithSceneElement` |
| `Get Meshes` / `Get Mesh Actors` | 获取场景中所有的网格体或网格体 Actor 元素，用于检查或修改。 | `UDatasmithSceneElementBase` |
| `Get Host` / `Get Product Name` | 获取导出场景的源应用程序信息。 | `UDatasmithSceneElementBase` |

### 使用示例（蓝图描述）

1.  **基本文件导入**：
    *   使用 `Construct Datasmith Scene From File` 节点，输入 `.udatasmith` 文件路径，获得一个 `UDatasmithSceneElement` 对象。
    *   （可选）通过该对象的 `Get Import Options` 节点获取并修改导入选项。
    *   调用 `Translate Scene` 节点。
    *   调用 `Import Scene` 节点，指定目标文件夹（如 `/Game/ImportedAssets`）。
    *   从 `Import Scene` 的返回值 `FDatasmithImportFactoryCreateFileResult` 中获取 `Imported Actors` 和 `Imported Meshes`。

2.  **检查场景信息**：
    *   获取一个 `UDatasmithSceneElement` 对象（通过构造或 `Get Existing`）。
    *   调用 `Get Host`、`Get Product Version` 等节点，将结果打印到屏幕或日志，用于调试或信息显示。

## C++ 用法

### 头文件引入

```cpp
#include "DatasmithImporter.h"
#include "DatasmithBlueprintLibrary.h"
#include "DatasmithImporterHelper.h"
```

### 基本用法

以下示例展示了如何通过 C++ 代码触发一次完整的 Datasmith 文件导入流程。

```cpp
// 来源: 基于 DatasmithBlueprintLibrary.h 和 DatasmithImporterHelper.h 的用法推断
#include "DatasmithImporterHelper.h"
#include "DatasmithImportFactory.h"

void ImportMyDatasmithFile()
{
    // 方法一：使用工厂辅助函数（会弹出文件选择和导入选项对话框）
    FDatasmithImporterHelper::Import<UDatasmithImportFactory>();

    // 方法二：更底层的控制，直接使用工厂
    UDatasmithImportFactory* Factory = GetMutableDefault<UDatasmithImportFactory>();
    FString Filename = TEXT("C:/MyModel.udatasmith");
    bool bOperationCanceled = false;
    
    // 检查文件是否可导入
    if (Factory->FactoryCanImport(Filename))
    {
        // 准备导入参数（通常从对话框获取）
        // ... 设置 ImportContext 的选项 ...
        
        // 执行导入
        UObject* ImportedAsset = Factory->FactoryCreateFile(
            UDatasmithScene::StaticClass(), // 目标类
            GetTransientPackage(),          // 父包
            FName(TEXT("MyScene")),         // 资产名
            RF_NoFlags,                     // 对象标志
            Filename,                       // 文件名
            nullptr,                        // 参数
            GWarn,                          // 反馈上下文
            bOperationCanceled              // [out] 是否取消
        );
        
        if (ImportedAsset && !bOperationCanceled)
        {
            // 导入成功，处理导入的资产（如移动到正确的内容文件夹）
            UDatasmithScene* SceneAsset = Cast<UDatasmithScene>(ImportedAsset);
            // ...
        }
    }
}
```

### 进阶用法

使用 `FDatasmithImporter` 结构体中的静态方法，可以对导入过程进行更精细的控制，例如单独导入网格体或材质。

```cpp
// 来源: 基于 DatasmithImporter.h 的函数签名
#include "DatasmithImporter.h"
#include "DatasmithImportContext.h"

void ImportSpecificMesh(FDatasmithImportContext& ImportContext, TSharedRef<IDatasmithMeshElement> MeshElement)
{
    // 假设 ImportContext 已经通过某种方式（如从 .udatasmith 文件加载）初始化
    
    // 1. 导入单个静态网格体
    UStaticMesh* ImportedMesh = FDatasmithImporter::ImportStaticMesh(
        ImportContext,
        MeshElement,
        nullptr // ExistingStaticMesh，用于重新导入
    );
    
    if (ImportedMesh)
    {
        // 2. 最终确定网格体（将其从临时包移动到最终位置并构建）
        FString FinalPath = TEXT("/Game/Meshes/");
        UStaticMesh* FinalMesh = FDatasmithImporter::FinalizeStaticMesh(
            ImportedMesh,
            *FinalPath,
            nullptr // 如果是重新导入，传入现有的网格体
        );
        
        // 3. 创建资产导入数据（用于支持重新导入）
        TArray<UDatasmithAdditionalData*> AdditionalData;
        FDatasmithImporter::CreateStaticMeshAssetImportData(
            ImportContext,
            MeshElement,
            FinalMesh,
            AdditionalData
        );
    }
}
```

## Demo 示例

以下是一个最小化的 C++ 示例，演示如何创建一个自定义的 Datasmith 导入器工厂。

```cpp
// MyDatasmithImporter.h
#pragma once

#include "Factories/Factory.h"
#include "MyDatasmithImporter.generated.h"

UCLASS()
class UMyDatasmithImporterFactory : public UFactory
{
    GENERATED_BODY()

public:
    UMyDatasmithImporterFactory();

    virtual bool FactoryCanImport(const FString& Filename) override;
    virtual UObject* FactoryCreateFile(UClass* InClass, UObject* InParent, FName InName, EObjectFlags Flags, const FString& Filename, const TCHAR* Parms, FFeedbackContext* Warn, bool& bOutOperationCanceled) override;
};
```

```cpp
// MyDatasmithImporter.cpp
#include "MyDatasmithImporter.h"
#include "DatasmithImporterHelper.h"
#include "DatasmithImportFactory.h"

UMyDatasmithImporterFactory::UMyDatasmithImporterFactory()
{
    // 支持的格式
    Formats.Add(TEXT("myext;My Custom Datasmith Format"));
    SupportedClass = UDatasmithScene::StaticClass();
    bCreateNew = false;
    bEditorImport = true;
}

bool UMyDatasmithImporterFactory::FactoryCanImport(const FString& Filename)
{
    // 检查文件扩展名
    return FPaths::GetExtension(Filename).Equals(TEXT("myext"), ESearchCase::IgnoreCase);
}

UObject* UMyDatasmithImporterFactory::FactoryCreateFile(UClass* InClass, UObject* InParent, FName InName, EObjectFlags Flags, const FString& Filename, const TCHAR* Parms, FFeedbackContext* Warn, bool& bOutOperationCanceled)
{
    // 委托给标准的 Datasmith 导入工厂
    UDatasmithImportFactory* DatasmithFactory = GetMutableDefault<UDatasmithImportFactory>();
    if (DatasmithFactory)
    {
        return DatasmithFactory->FactoryCreateFile(InClass, InParent, InName, Flags, Filename, Parms, Warn, bOutOperationCanceled);
    }
    return nullptr;
}
```

## 模块依赖

要使用 Datasmith Importer 插件的功能，你的模块需要依赖以下独特模块：

| 模块 | 用途 |
|---|---|
| `DatasmithCore` | Datasmith 的核心数据结构和接口定义。 |
| `DatasmithContent` | 包含 Datasmith 场景资产 (`UDatasmithScene`) 和相关运行时组件。 |
| `InterchangeCore` | UE 的通用资产交换框架，Datasmith 使用其进行异步资产创建。 |
| `InterchangeEngine` | Interchange 框架的引擎集成部分。 |
| `InterchangeNodes` | Interchange 框架中用于表示资产节点的模块。 |
| `MeshDescription` | 用于处理网格体几何数据的中间表示。 |
| `FreeImage` | 用于图像处理（如纹理缩放）的第三方库。 |

## 维护状态

### 近期更新

```
- e56d67e43349 Landscape - Event system for ULandscapeLayerInfoObject data updates * Deprecates all public LandscapeInfo properties in favor of public accessors * ALandscapeProxy subscribes to events to make landscape changes as needed
- 1feaaa3e8345 Fixed rename crash on Datasmith reimport
- 8c4cad918a59 - Changed all WITH_EDITORONLY_DATA properties in StaticMesh to have accessors, and a few changes to SkeletalMesh to match (like making an accessor for NaniteSettings)
```

*   `e56d67e`：此提交主要针对 Landscape 系统，与 Datasmith 核心导入功能无直接关系，表明插件代码库随引擎主分支同步更新。
*   `1feaaa3`：修复了 Datasmith 重新导入时因重命名导致的崩溃，这是一个重要的稳定性修复。
*   `8c4cad9`：重构了 StaticMesh 的编辑器数据访问方式，属于引擎底层优化，Datasmith 导入器需要适配这些变化。

### 维护评价

Datasmith Importer 是一个**成熟且处于积极维护状态**的企业级插件。
-   **创建时间**：约 6 年前（2019年），已度过初期开发阶段。
-   **维护活跃度**：从提交记录看，它持续跟随 UE 主引擎进行更新和适配（如最近的 StaticMesh 访问器重构），并修复了实际使用中发现的 Bug（如重新导入崩溃）。这表明 Epic Games 将其作为核心企业功能进行维护。
-   **功能完整性**：插件架构清晰，模块化程度高，支持从文件导入、实时同步到蓝图控制的完整工作流。
-   **推荐使用**：**强烈推荐**用于任何需要将专业 CAD/BIM 数据引入 Unreal Engine 的项目。它是 Epic 官方支持的解决方案，稳定性和兼容性有保障。需要注意的是，它默认未启用 (`EnabledByDefault: false`)，需要在项目设置或插件菜单中手动启用。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithImporter)
-   [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithImporter/Source/DirectLinkTest) (DirectLinkTest 模块包含测试代码)