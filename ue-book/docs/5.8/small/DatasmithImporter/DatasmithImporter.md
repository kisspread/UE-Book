# Datasmith Importer

> Importer for Datasmith files.

| 属性 | 值 |
|---|---|
| 中文名 | Datasmith 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DatasmithImporter` (Runtime), `DatasmithTranslator` (Runtime), `DatasmithNativeTranslator` (Runtime), `DatasmithExternalSource` (Runtime), `ExternalSource` (Runtime), `DirectLinkExtension` (Runtime), `DirectLinkExtensionEditor` (Runtime), `DirectLinkTest` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 🏛️ 文物（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter) | |

## 用途

Datasmith Importer 是一个将外部 CAD/DCC 软件（如 3ds Max、Revit、SketchUp、CATIA、SolidWorks 等）生成的 Datasmith 格式场景文件（`.udatasmith`）导入到 Unreal Engine 的核心工具。它不仅仅是一个文件加载器，而是一套完整的资产管线，负责将外部场景的几何体（静态网格体）、材质、纹理、灯光、摄像机、层级结构、Level Sequence 动画以及 Level Variant Sets（变体集）等全部翻译并转换为 UE 原生资产和 Actor。

该插件解决了从专业设计/建筑/工程软件向 UE 高效迁移复杂三维场景的问题。与通用的 FBX 导入不同，Datasmith 能够保留 BIM 元数据、材质属性映射关系、以及增量更新（重新导入时保留手动修改）。它通过 IDatasmithTranslator 接口支持多种源格式，同时集成了 Dataprep 管线用于自动化批量导入处理。

**注意：** 默认未启用（`EnabledByDefault: false`），需要在 Plugins 面板中手动启用。

## 使用场景

- 你从 Revit/SketchUp/3ds Max/Rhino 等软件导出了 `.udatasmith` 文件 → 用此插件导入到 UE 项目中
- 你需要在 UE 中构建建筑/工业/汽车可视化项目，源数据来自 CAD 软件 → 用 Datasmith 导入
- 你需要批量导入整个目录下的多个 Datasmith 文件 → 用 Dataprep 的 `UDatasmithDirProducer`
- 你需要在蓝图中以编程方式控制导入流程（指定选项、目标路径等） → 用 `UDatasmithSceneElement` 蓝图 API
- 你需要对已导入的 Datasmith 场景进行增量更新（保留手动编辑） → 用 Reimport 功能
- 你需要通过 DirectLink 实时同步外部软件的场景变更 → 用 DirectLinkExtension 模块

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ConstructDatasmithSceneFromFile` | 从文件路径打开 .udatasmith 文件 | `UDatasmithSceneElement` |
| `ConstructDatasmithSceneFromSourceUri` | 从 URI（如 `file://`）打开 Datasmith 场景 | `UDatasmithSceneElement` |
| `ConstructDatasmithSceneFromCADFiles` | 从多个 CAD 文件创建单个 Datasmith 场景 | `UDatasmithSceneElement` |
| `GetExistingDatasmithScene` | 获取已导入的 DatasmithScene 资产 | `UDatasmithSceneElement` |
| `TranslateScene` | 执行翻译阶段，填充 DatasmithScene 数据 | `UDatasmithSceneElement` |
| `ImportScene` | 将 Datasmith 场景导入到指定文件夹 | `UDatasmithSceneElement` |
| `ImportScenes` | 批量导入多个场景到指定文件夹 | `UDatasmithSceneElement` |
| `ReimportScene` | 重新导入已存在的 DatasmithScene 资产 | `UDatasmithSceneElement` |
| `GetOptions` | 获取指定类型的导入选项 | `UDatasmithSceneElement` |
| `GetAllOptions` | 获取所有可用的导入选项映射 | `UDatasmithSceneElement` |
| `DestroyScene` | 释放 Datasmith 场景引用 | `UDatasmithSceneElement` |
| `ComputeLightmapResolution` | 计算并设置静态网格体的光照贴图分辨率 | `UDatasmithStaticMeshBlueprintLibrary` |
| `SetupStaticLighting` | 启用/禁用光照贴图 UV 生成 | `UDatasmithStaticMeshBlueprintLibrary` |
| `GenerateFlattenMappingUVs` | 在指定 UV 通道生成展平 UV 映射 | `UUVGenerationFlattenMapping` |

### 场景元素操作节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateMesh` / `GetMeshes` / `RemoveMesh` | 创建/获取/移除网格体元素 | `UDatasmithSceneElementBase` |
| `CreateMeshActor` / `GetMeshActors` / `RemoveMeshActor` | 创建/获取/移除网格体 Actor | `UDatasmithSceneElementBase` |
| `CreateCameraActor` / `GetCameraActors` / `RemoveCameraActor` | 创建/获取/移除摄像机 Actor | `UDatasmithSceneElementBase` |
| `CreateTexture` / `GetTextures` / `RemoveTexture` | 创建/获取/移除纹理元素 | `UDatasmithSceneElementBase` |
| `GetAllMaterials` / `RemoveMaterial` | 获取/移除材质元素 | `UDatasmithSceneElementBase` |
| `GetLightActors` / `GetAllLightActors` | 获取灯光 Actor 列表 | `UDatasmithSceneElementBase` |
| `AttachActor` / `AttachActorToSceneRoot` | 附加 Actor 到父级或场景根 | `UDatasmithSceneElementBase` |
| `GetMetaDataForObject` | 获取对象的元数据 | `UDatasmithSceneElementBase` |
| `CreateLevelVariantSets` / `GetAllLevelVariantSets` | 创建/获取变体集 | `UDatasmithSceneElementBase` |

### Actor 元素属性节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetTranslation` / `SetTranslation` | 获取/设置 Actor 平移 | `UDatasmithActorElement` |
| `GetRotation` / `SetRotation` | 获取/设置 Actor 旋转（四元数） | `UDatasmithActorElement` |
| `GetScale` / `SetScale` | 获取/设置 Actor 缩放 | `UDatasmithActorElement` |
| `GetLayer` / `SetLayer` | 获取/设置 Actor 所在层 | `UDatasmithActorElement` |
| `GetTags` / `SetTags` | 获取/设置 Actor 标签 | `UDatasmithActorElement` |
| `AddChild` / `GetChildren` / `RemoveChild` | 管理 Actor 子级 | `UDatasmithActorElement` |
| `GetVisibility` / `SetVisibility` | 获取/设置 Actor 可见性 | `UDatasmithActorElement` |

### 使用示例（蓝图描述）

**基础导入流程：**

1. 调用 `ConstructDatasmithSceneFromFile`，传入文件路径字符串（如 `"C:/Models/Building.udatasmith"`），返回 `UDatasmithSceneElement` 对象
2. 可选：调用 `GetOptions` 获取导入选项并修改（如碰撞设置、纹理分辨率等）
3. 调用 `TranslateScene` 执行翻译
4. 调用 `ImportScene`，传入目标文件夹路径（如 `"/Game/ImportedScenes"`）
5. 从返回的 `FDatasmithImportFactoryCreateFileResult` 中获取 `ImportedActors` 数组和 `Scene` 引用
6. 完成后调用 `DestroyScene` 释放资源

**批量 CAD 导入：**

1. 调用 `ConstructDatasmithSceneFromCADFiles`，传入文件路径数组
2. 调用 `ImportScenes` 批量导入到同一目标文件夹

**重新导入：**

1. 调用 `GetExistingDatasmithScene`，传入已导入资产的路径（如 `"/Game/MyScene/MyScene"`）
2. 调用 `ReimportScene` 执行增量更新

## C++ 用法

### 头文件引入

```cpp
#include "DatasmithBlueprintLibrary.h"
#include "DatasmithImportContext.h"
#include "DatasmithImporter.h"
#include "DatasmithActorImporter.h"
#include "DatasmithStaticMeshImporter.h"
#include "DatasmithLightImporter.h"
#include "DatasmithCameraImporter.h"
#include "DatasmithMaterialExpressions.h"
#include "DatasmithImporterUtils.h"
#include "DatasmithImportFactory.h"
```

### 基本用法

从蓝图库头文件提取的典型 C++ 导入流程：

```cpp
// 来源: Public/DatasmithBlueprintLibrary.h - UDatasmithSceneElement API
// 通过工厂类执行导入

#include "DatasmithImportFactory.h"
#include "DatasmithImportContext.h"

// 方法一：使用工厂类直接导入
UDatasmithImportFactory* Factory = NewObject<UDatasmithImportFactory>();
bool bCanceled = false;
FFeedbackContext* Warn = GetMutableDefault<UEngine>()->GetFeedbackContext();

UObject* ImportedScene = Factory->FactoryCreateFile(
    UDatasmithScene::StaticClass(),   // InClass
    nullptr,                          // InParent (会弹出路径选择)
    FName("MyScene"),                 // InName
    RF_Public | RF_Standalone,        // Flags
    TEXT("C:/Models/Building.udatasmith"), // Filename
    nullptr,                          // InParms
    Warn,                             // FeedbackContext
    bCanceled                         // bOutOperationCanceled
);
```

```cpp
// 方法二：通过 ExternalSource API（更底层的控制）
#include "DatasmithImporter.h"
#include "ExternalSource/ExternalSource.h"

// 创建 ExternalSource
TSharedPtr<UE::DatasmithImporter::FExternalSource> ExternalSource = 
    UE::DatasmithImporter::FExternalSource::Create(TEXT("file://C:/Models/Scene.udatasmith"));

// 构建导入上下文
FDatasmithImportContext ImportContext(
    ExternalSource,
    true,                           // bLoadConfig
    FName("DatasmithImport"),       // LoggerName
    NSLOCTEXT("Datasmith", "ImportLabel", "Datasmith Import") // LoggerLabel
);

// 初始化选项（弹出导入对话框）
if (ImportContext.InitOptions(nullptr, false))
{
    // 设置目标路径
    if (ImportContext.SetupDestination(TEXT("/Game/ImportedScene"), RF_Public | RF_Standalone, Warn, false))
    {
        // 翻译场景
        ExternalSource->Translate();
        ImportContext.InitScene(ExternalSource->GetScene());
        
        // 执行导入
        FDatasmithImporter::ImportStaticMeshes(ImportContext);
        FDatasmithImporter::ImportTextures(ImportContext);
        FDatasmithImporter::ImportMaterials(ImportContext);
        FDatasmithImporter::ImportActors(ImportContext);
        FDatasmithImporter::ImportLevelSequences(ImportContext);
        FDatasmithImporter::ImportLevelVariantSets(ImportContext);
        FDatasmithImporter::FinalizeImport(ImportContext, ValidAssets);
    }
}
```

```cpp
// 方法三：使用 DatasmithSceneElement（蓝图 API 的 C++ 等价）
#include "DatasmithBlueprintLibrary.h"

// 从文件创建场景
UDatasmithSceneElement* SceneElement = 
    UDatasmithSceneElement::ConstructDatasmithSceneFromFile(TEXT("C:/Models/Scene.udatasmith"));

if (SceneElement)
{
    // 翻译并导入
    SceneElement->TranslateScene();
    FDatasmithImportFactoryCreateFileResult Result = 
        SceneElement->ImportScene(TEXT("/Game/ImportedScene"));
    
    // 获取导入结果
    TArray<TObjectPtr<AActor>>& ImportedActors = Result.ImportedActors;
    bool bSuccess = Result.bImportSucceed;
    UDatasmithScene* Scene = Result.Scene;
    
    // 释放
    SceneElement->DestroyScene();
}
```

### 进阶用法

**静态网格体导入与光照贴图设置：**

```cpp
// 来源: Public/DatasmithStaticMeshImporter.h + Public/DatasmithBlueprintLibrary.h

#include "DatasmithStaticMeshImporter.h"
#include "DatasmithBlueprintLibrary.h"

// 导入单个静态网格体
TSharedRef<IDatasmithMeshElement> MeshElement = ...; // 从翻译器获取
FDatasmithMeshElementPayload Payload;
FDatasmithStaticMeshImportOptions ImportOptions;
FDatasmithAssetsImportContext AssetsContext(ImportContext);

UStaticMesh* Mesh = FDatasmithStaticMeshImporter::ImportStaticMesh(
    MeshElement, Payload, RF_Public, ImportOptions, AssetsContext, nullptr);

// 计算光照贴图权重
TMap<TSharedRef<IDatasmithMeshElement>, float> LightmapWeights = 
    FDatasmithStaticMeshImporter::CalculateMeshesLightmapWeights(SceneElement);

// 设置网格体（含光照贴图权重）
FDatasmithStaticMeshImporter::SetupStaticMesh(
    AssetsContext, MeshElement, Mesh, ImportOptions, LightmapWeight);

// 使用蓝图库设置光照贴图（蓝图和 C++ 都可用）
TArray<UObject*> MeshObjects = { Mesh };
UDatasmithStaticMeshBlueprintLibrary::ComputeLightmapResolution(MeshObjects, true, 0.2f);
UDatasmithStaticMeshBlueprintLibrary::SetupStaticLighting(
    MeshObjects, true, true, 0.2f);  // 启用光照贴图 UV 生成

// 生成展平 UV
UUVGenerationFlattenMapping::GenerateFlattenMappingUVs(Mesh, 1, 66.0f); // UV 通道 1
```

**自定义材质导入：**

```cpp
// 来源: Public/DatasmithMaterialExpressions.h

#include "DatasmithMaterialExpressions.h"

// 从 Datasmith 材质元素创建 UE 材质
TSharedPtr<IDatasmithMaterialElement> MaterialElement = ...;
UPackage* Package = CreatePackage(nullptr, TEXT("/Game/ImportedScene/Materials/MyMaterial"));

UMaterialInterface* Material = FDatasmithMaterialExpressions::CreateDatasmithMaterial(
    Package, MaterialElement, AssetsContext, nullptr, RF_Public | RF_Standalone);

// 从 UE PBR 材质元素创建材质实例
TSharedPtr<IDatasmithUEPbrMaterialElement> PbrElement = ...;
UMaterialInterface* ParentMaterial = ...;
UMaterialInterface* MatInstance = FDatasmithMaterialExpressions::CreateUEPbrMaterialInstance(
    Package, PbrElement, AssetsContext, ParentMaterial, RF_Public | RF_Standalone);
```

**资产查找工具：**

```cpp
// 来源: Public/Utility/DatasmithImporterUtils.h

#include "DatasmithImporterUtils.h"

// 查找已导入的资产（支持相对路径和绝对路径）
UStaticMesh* Mesh = FDatasmithImporterUtils::FindAsset<UStaticMesh>(AssetsContext, TEXT("MyMesh"));
UTexture* Texture = FDatasmithImporterUtils::FindAsset<UTexture>(AssetsContext, TEXT("/Game/Textures/MyTex"));

// 检查资产是否可以创建
FText FailReason;
bool bCanCreate = FDatasmithImporterUtils::CanCreateAsset<UStaticMesh>(
    TEXT("/Game/ImportedScene/Meshes/MyMesh"), FailReason);

// 查找场景中的所有 DatasmithSceneActor
TArray<ADatasmithSceneActor*> SceneActors = 
    FDatasmithImporterUtils::FindSceneActors(World, DatasmithSceneAsset);

// 将 Actor 列表转换为 DatasmithScene 元素
TSharedPtr<IDatasmithScene> SceneElement = ...;
TArray<AActor*> RootActors = { Actor1, Actor2 };
FDatasmithImporterUtils::FillSceneElement(SceneElement, RootActors);

// 查找对象关联的 DatasmithScene 资产
UDatasmithScene* Scene = FDatasmithImporterUtils::FindDatasmithSceneForAsset(SomeAsset);
```

**批量材质导入（按依赖顺序）：**

```cpp
// 来源: Public/Utility/DatasmithImporterUtils.h

// 获取按依赖排序的材质列表
TArray<FDatasmithImporterUtils::FFunctionAndMaterialsThatUseIt> OrderedMaterials = 
    FDatasmithImporterUtils::GetOrderedListOfMaterialsReferencedByMaterials(SceneElement);

for (auto& [MaterialFunction, MaterialsUsingIt] : OrderedMaterials)
{
    // 先导入材质函数
    UMaterialFunction* MatFunc = FDatasmithMaterialExpressions::CreateUEPbrMaterialFunction(
        Package, MaterialFunction, AssetsContext, nullptr, RF_Public);
    
    // 再导入使用它的材质
    for (auto& MatElement : MaterialsUsingIt)
    {
        FDatasmithMaterialExpressions::CreateUEPbrMaterial(
            Package, MatElement, AssetsContext, nullptr, RF_Public);
    }
}

// 使用迭代器遍历排序后的材质
FDatasmithImporterUtils::FDatasmithMaterialImportIterator MatIter(ImportContext);
while (MatIter)
{
    TSharedPtr<IDatasmithBaseMaterialElement> MaterialElement = MatIter.Value();
    // 处理材质...
    ++MatIter;
}
```

## Demo 示例

```cpp
// MyDatasmithImporter.h
#pragma once

#include "CoreMinimal.h"

class FMyDatasmithImporter
{
public:
    /** 导入单个 .udatasmith 文件到指定路径 */
    static bool ImportDatasmithFile(const FString& FilePath, const FString& DestinationFolder);

    /** 重新导入已存在的 Datasmith 场景 */
    static bool ReimportExistingScene(const FString& ExistingScenePath);

    /** 导入多个 CAD 文件到单个场景 */
    static bool ImportMultipleCADFiles(const TArray<FString>& CADFiles, const FString& DestinationFolder);
};
```

```cpp
// MyDatasmithImporter.cpp
#include "MyDatasmithImporter.h"
#include "DatasmithBlueprintLibrary.h"
#include "DatasmithImporterUtils.h"
#include "DatasmithScene.h"
#include "Engine/World.h"

bool FMyDatasmithImporter::ImportDatasmithFile(const FString& FilePath, const FString& DestinationFolder)
{
    // 步骤 1: 从文件创建场景元素
    UDatasmithSceneElement* SceneElement = 
        UDatasmithSceneElement::ConstructDatasmithSceneFromFile(FilePath);
    
    if (!SceneElement)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to construct Datasmith scene from: %s"), *FilePath);
        return false;
    }

    // 步骤 2: 获取并查看导入选项
    TMap<UClass*, UObject*> AllOptions = SceneElement->GetAllOptions();
    UE_LOG(LogTemp, Log, TEXT("Found %d option types"), AllOptions.Num());

    // 步骤 3: 翻译场景
    if (!SceneElement->TranslateScene())
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to translate Datasmith scene"));
        SceneElement->DestroyScene();
        return false;
    }

    // 步骤 4: 导入场景到目标文件夹
    FDatasmithImportFactoryCreateFileResult Result = 
        SceneElement->ImportScene(DestinationFolder);

    if (!Result.bImportSucceed)
    {
        UE_LOG(LogTemp, Error, TEXT("Import failed for: %s"), *FilePath);
        SceneElement->DestroyScene();
        return false;
    }

    // 步骤 5: 处理导入结果
    UE_LOG(LogTemp, Log, TEXT("Successfully imported %d actors"), Result.ImportedActors.Num());
    for (AActor* Actor : Result.ImportedActors)
    {
        if (Actor)
        {
            UE_LOG(LogTemp, Log, TEXT("  Actor: %s"), *Actor->GetActorLabel());
        }
    }

    // 步骤 6: 清理
    SceneElement->DestroyScene();
    return true;
}

bool FMyDatasmithImporter::ReimportExistingScene(const FString& ExistingScenePath)
{
    // 获取已存在的场景
    UDatasmithSceneElement* SceneElement = 
        UDatasmithSceneElement::GetExistingDatasmithScene(ExistingScenePath);

    if (!SceneElement)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to find existing Datasmith scene: %s"), *ExistingScenePath);
        return false;
    }

    // 重新导入（会保留手动修改）
    FDatasmithImportFactoryCreateFileResult Result = SceneElement->ReimportScene();
    
    UE_LOG(LogTemp, Log, TEXT("Reimport %s: %d actors"), 
        Result.bImportSucceed ? TEXT("succeeded") : TEXT("failed"),
        Result.ImportedActors.Num());

    SceneElement->DestroyScene();
    return Result.bImportSucceed;
}

bool FMyDatasmithImporter::ImportMultipleCADFiles(
    const TArray<FString>& CADFiles, const FString& DestinationFolder)
{
    // 从多个 CAD 文件创建单个场景
    UDatasmithSceneElement* SceneElement = 
        UDatasmithSceneElement::ConstructDatasmithSceneFromCADFiles(CADFiles);

    if (!SceneElement)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to construct scene from %d CAD files"), CADFiles.Num());
        return false;
    }

    // 翻译并导入
    SceneElement->TranslateScene();
    TArray<FDatasmithImportFactoryCreateFileResult> Results = 
        SceneElement->ImportScenes(DestinationFolder);

    int32 SuccessCount = 0;
    for (const auto& Result : Results)
    {
        if (Result.bImportSucceed)
        {
            ++SuccessCount;
        }
    }

    UE_LOG(LogTemp, Log, TEXT("Imported %d/%d scenes successfully"), SuccessCount, Results.Num());

    SceneElement->DestroyScene();
    return SuccessCount == Results.Num();
}
```

## 模块依赖

本插件有 8 个模块，以下是使用者需要关注的独特依赖：

| 模块 | 用途 |
|---|---|
| `DatasmithTranslator` | Datasmith 翻译器接口定义，自定义格式翻译器需实现此接口 |
| `DatasmithNativeTranslator` | 内置 `.udatasmith` 文件格式的翻译器实现 |
| `DatasmithExternalSource` | 外部数据源抽象，支持文件和 DirectLink 等来源 |
| `ExternalSource` | 通用外部源基类 |
| `DirectLinkExtension` | DirectLink 协议支持，用于与外部软件实时同步场景 |
| `DirectLinkExtensionEditor` | DirectLink 编辑器集成 |
| `DirectLinkTest` | DirectLink 测试模块 |
| `DataprepCore` | Dataprep 管线核心（FileProducer/DirProducer/Consumer 依赖） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移到新的 UE_LOGF 日志宏 |
| 2026-04-02 | `50a24ff6` | Deprecated GetObjects*/ForEachObjectWithOuter functions that take bool bIncludeNestedObjects. Introduced new versions. | 废弃旧版对象遍历函数，引入新版本 API |
| 2026-03-06 | `7b69892a` | clean up code changing texture properties with wrapping in PreEditChange/PostEditChange as required. | 规范纹理属性修改流程，确保 Pre/PostEditChange 正确配对 |
| 2026-03-05 | `1adb9f68` | New material translator work: | 材质翻译器新功能开发 |

### 维护评价

**活跃维护**。Datasmith Importer 是 Epic Games 官方维护的 Enterprise 级插件，持续获得功能性更新和质量改进。从近期提交记录来看：

- **更新频率高**：2026 年前 5 个月就有 5 次提交，涵盖材质翻译器新功能、API 迁移、编译警告修复等多个方面
- **持续演进**：材质翻译器正在积极开发新功能（`1adb9f68`），说明核心功能仍在扩展
- **代码质量关注**：定期进行 API 废弃替换（`UE_LOG → UE_LOGF`、`ForEachObjectWithOuter` 重构）和代码规范清理
- **无已知废弃风险**：未发现 deprecated/obsolete 标记，作为 Datasmith 生态的核心组件，Epic 没有理由放弃维护
- **推荐使用**：对于需要从 CAD/BIM 软件导入场景的项目，这是唯一官方支持的完整方案，稳定可靠

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)