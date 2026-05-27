# Datasmith Importer

> Importer for Datasmith files.

| 属性 | 值 |
|---|---|
| 中文名 | 数据导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DatasmithExternalSource` (Runtime), `DatasmithImporter` (Runtime), `DatasmithNativeTranslator` (Runtime), `DatasmithTranslator` (Runtime), `DirectLinkExtension` (Runtime), `DirectLinkExtensionEditor` (Runtime), `DirectLinkTest` (Runtime), `ExternalSource` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter) | |

> **注意**：此插件默认未启用（`EnabledByDefault=false`），需要在"Edit > Plugins"中手动启用。

## 用途

Datasmith Importer 是 Unreal Engine 的企业级数据导入系统核心模块，负责将其他 DCC（数字内容创建）工具导出的 `.udatasmith` 文件（以及 CAD、BIM 等格式）转换为 Unreal Engine 原生资产。

它解决的核心问题是：**工业设计、建筑和制造领域的 CAD/BIM 数据（来自 Revit、3ds Max、SketchUp、Rhino、CATIA、SolidWorks 等几十种专业工具）无法直接被 Unreal Engine 使用**。Datasmith 通过标准化的中间格式，将这些数据（几何体、材质、纹理、灯光、相机、层级关系、元数据、变体集等）完整地转换为 UE 的 Static Mesh、Material、Texture、Actor 等资产，同时保留原始数据的语义信息和层级结构。

本模块 `DatasmithImporter` 是整个导入管线的执行层，包括：
- 文件工厂（Factory）和重导入（Reimport）流程
- 静态网格体、材质、纹理、灯光、相机、景观、环境等各类资产的导入器
- 导入上下文（ImportContext）管理
- 蓝图 API 暴露（供脚本化导入使用）
- Dataprep 生产者（Producer）和消费者（Consumer）集成
- UV 工具（展开 UV 生成、光照图设置）

## 使用场景

- 你在做一个建筑可视化项目，需要将 Revit/SketchUp 模型导入 UE → 使用 Datasmith 导入 `.udatasmith` 文件
- 你需要将 3ds Max 场景（包含灯光、相机、材质）完整迁移到 UE → 使用 Datasmith 保留场景语义
- 你需要在蓝图中批量导入 CAD 文件并自动化处理 → 使用 `UDatasmithSceneElement` 蓝图 API
- 你需要将 CAD 数据通过 Dataprep 流程自动处理后再导入 → 使用 `UDatasmithFileProducer` / `UDatasmithDirProducer`
- 你需要为导入的静态网格体自动生成光照图 UV 并设置分辨率 → 使用 `UDatasmithStaticMeshBlueprintLibrary`
- 你需要生成展开 UV（Flatten Mapping）用于 lightmap → 使用 `UUVGenerationFlattenMapping`

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ConstructDatasmithSceneFromFile` | 从 .udatasmith 文件路径构造场景对象 | `UDatasmithSceneElement` |
| `ConstructDatasmithSceneFromSourceUri` | 从 SourceUri 构造场景对象（支持 `file://` 等协议） | `UDatasmithSceneElement` |
| `ConstructDatasmithSceneFromCADFiles` | 将一组 CAD 文件构造为单个 Datasmith 场景 | `UDatasmithSceneElement` |
| `GetExistingDatasmithScene` | 获取已存在的 DatasmithScene 资产用于重新导入 | `UDatasmithSceneElement` |
| `TranslateScene` | 触发翻译阶段，填充场景数据 | `UDatasmithSceneElement` |
| `ImportScene` | 将场景导入到指定文件夹，返回导入结果（创建的 Actor 列表） | `UDatasmithSceneElement` |
| `ImportScenes` | 批量导入多个场景 | `UDatasmithSceneElement` |
| `ReimportScene` | 重新导入已存在的场景 | `UDatasmithSceneElement` |
| `GetOptions` | 获取指定类型的导入选项对象 | `UDatasmithSceneElement` |
| `GetAllOptions` | 获取所有适用的导入选项 | `UDatasmithSceneElement` |
| `DestroyScene` | 释放场景引用 | `UDatasmithSceneElement` |
| `ComputeLightmapResolution` | 根据理想的光照图密度比计算并设置光照图分辨率 | `UDatasmithStaticMeshBlueprintLibrary` |
| `SetupStaticLighting` | 设置光照图 UV 生成开关和分辨率 | `UDatasmithStaticMeshBlueprintLibrary` |
| `GenerateFlattenMappingUVs` | 为静态网格体生成展开 UV | `UUVGenerationFlattenMapping` |

### 场景元素操作节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateMesh` / `GetMeshes` / `RemoveMesh` | 创建/获取/移除网格体元素 | `UDatasmithSceneElementBase` |
| `CreateMeshActor` / `GetMeshActors` / `RemoveMeshActor` | 创建/获取/移除网格体 Actor 元素 | `UDatasmithSceneElementBase` |
| `GetLightActors` / `GetAllLightActors` / `RemoveLightActor` | 获取/移除灯光 Actor | `UDatasmithSceneElementBase` |
| `CreateCameraActor` / `GetCameraActors` / `RemoveCameraActor` | 创建/获取/移除相机 Actor | `UDatasmithSceneElementBase` |
| `CreateTexture` / `GetTextures` / `RemoveTexture` | 创建/获取/移除纹理 | `UDatasmithSceneElementBase` |
| `GetAllMaterials` / `RemoveMaterial` | 获取/移除材质 | `UDatasmithSceneElementBase` |
| `CreateLevelVariantSets` / `GetAllLevelVariantSets` | 创建/获取级别变体集 | `UDatasmithSceneElementBase` |
| `AttachActor` / `AttachActorToSceneRoot` | 设置 Actor 父子关系 | `UDatasmithSceneElementBase` |
| `GetMetaDataForObject` / `GetMetaDataValueForKey` | 获取对象元数据 | `UDatasmithSceneElementBase` |

### Actor 元素操作节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetTranslation` / `SetTranslation` | 获取/设置位移 | `UDatasmithActorElement` |
| `GetRotation` / `SetRotation` | 获取/设置旋转（四元数） | `UDatasmithActorElement` |
| `GetScale` / `SetScale` | 获取/设置缩放 | `UDatasmithActorElement` |
| `GetLayer` / `SetLayer` | 获取/设置所在图层 | `UDatasmithActorElement` |
| `GetTags` / `SetTags` | 获取/设置标签 | `UDatasmithActorElement` |
| `AddChild` / `GetChildren` / `RemoveChild` | 管理子级 | `UDatasmithActorElement` |
| `GetVisibility` / `SetVisibility` | 获取/设置可见性 | `UDatasmithActorElement` |

### 使用示例（蓝图描述）

**示例 1：基本导入流程**

1. 调用 `ConstructDatasmithSceneFromFile`，传入文件路径 `C:/Models/Building.udatasmith`
2. 调用 `GetOptions` 获取导入选项，设置材质和网格体的导入选项
3. 调用 `ImportScene`，传入目标路径 `/Game/ImportedModels`
4. 从返回的 `FDatasmithImportFactoryCreateFileResult` 中获取 `ImportedActors` 和 `ImportedMeshes`
5. 检查 `bImportSucceed` 确认导入是否成功
6. 调用 `DestroyScene` 释放资源

**示例 2：重新导入已有资产**

1. 调用 `GetExistingDatasmithScene`，传入资产路径 `/Game/ImportedModels/Building`
2. 调用 `ReimportScene` 更新场景

**示例 3：批量 CAD 文件导入**

1. 调用 `ConstructDatasmithSceneFromCADFiles`，传入文件路径数组
2. 调用 `TranslateScene` 翻译场景
3. 调用 `ImportScenes` 批量导入

## C++ 用法

### 头文件引入

```cpp
#include "DatasmithImporter.h"
#include "DatasmithImportContext.h"
#include "DatasmithBlueprintLibrary.h"
#include "DatasmithStaticMeshImporter.h"
#include "DatasmithMaterialImporter.h"
#include "DatasmithTextureImporter.h"
#include "DatasmithLightImporter.h"
#include "DatasmithActorImporter.h"
```

### 基本用法

**静态网格体导入**（来源：`Public/DatasmithStaticMeshImporter.h`）：

```cpp
// 从 MeshElement 导入单个静态网格体
TSharedRef<IDatasmithMeshElement> MeshElement = /* ... */;
FDatasmithMeshElementPayload Payload;
FDatasmithStaticMeshImportOptions ImportOptions;
UStaticMesh* ExistingMesh = nullptr; // 首次导入为 nullptr，重新导入时传入现有资产

UStaticMesh* ImportedMesh = FDatasmithStaticMeshImporter::ImportStaticMesh(
    MeshElement, Payload, RF_Public | RF_Standalone, ImportOptions, AssetsContext, ExistingMesh
);
```

**材质导入**（来源：`Public/DatasmithMaterialImporter.h`）：

```cpp
// 创建材质
TSharedRef<IDatasmithBaseMaterialElement> MaterialElement = /* ... */;
UMaterialInterface* ExistingMaterial = nullptr;
UMaterialInterface* ImportedMaterial = FDatasmithMaterialImporter::CreateMaterial(
    ImportContext, MaterialElement, ExistingMaterial
);

// 创建材质函数
UMaterialFunction* MaterialFunc = FDatasmithMaterialImporter::CreateMaterialFunction(
    ImportContext, MaterialElement
);
```

**灯光导入**（来源：`Public/DatasmithLightImporter.h`）：

```cpp
// 导入灯光 Actor
TSharedRef<IDatasmithLightActorElement> LightElement = /* ... */;
AActor* LightActor = FDatasmithLightImporter::ImportLightActor(LightElement, ImportContext);

// 创建 HDRI 天光
TSharedPtr<IDatasmithShaderElement> ShaderElement = /* ... */;
AActor* SkyLight = FDatasmithLightImporter::CreateHDRISkyLight(ShaderElement, ImportContext);
```

### 进阶用法

**完整的场景导入管线**（来源：`Public/DatasmithImporter.h`）：

```cpp
// 1. 过滤要导入的元素
FDatasmithImporter::FilterElementsToImport(ImportContext);

// 2. 导入各类型资产
FDatasmithImporter::ImportTextures(ImportContext);
FDatasmithImporter::ImportMaterials(ImportContext);
FDatasmithImporter::ImportStaticMeshes(ImportContext);

// 3. 导入 Actor 层级
FDatasmithImporter::ImportActors(ImportContext);

// 4. 导入动画和变体
FDatasmithImporter::ImportLevelSequences(ImportContext);
FDatasmithImporter::ImportLevelVariantSets(ImportContext);

// 5. 最终化所有资产（从临时包移到最终包）
TSet<UObject*> ValidAssets;
FDatasmithImporter::FinalizeImport(ImportContext, ValidAssets);
```

**使用 ExternalSource 进行程序化导入**（来源：`Public/DatasmithImportContext.h`）：

```cpp
// 创建 ExternalSource（支持多种数据源）
TSharedPtr<UE::DatasmithImporter::FExternalSource> ExternalSource = /* ... */;

// 创建导入上下文
FDatasmithImportContext ImportContext(
    ExternalSource,
    true,                          // bLoadConfig
    TEXT("DatasmithImport"),       // LoggerName
    NSLOCTEXT("Datasmith", "Import", "Datasmith Import")
);

// 初始化选项（静默模式，使用 JSON 配置）
TSharedPtr<FJsonObject> ImportSettingsJson = /* ... */;
bool bSilent = true;
ImportContext.InitOptions(ImportSettingsJson, TOptional<FString>(), bSilent);

// 设置目标路径
ImportContext.SetupDestination(TEXT("/Game/ImportedScene"), RF_Public | RF_Standalone, GWarn, true);

// 初始化场景并执行导入
ImportContext.InitScene(SceneToImport);
FDatasmithImporter::ImportTextures(ImportContext);
FDatasmithImporter::ImportStaticMeshes(ImportContext);
FDatasmithImporter::ImportMaterials(ImportContext);
FDatasmithImporter::ImportActors(ImportContext);
```

**光照图 UV 生成**（来源：`Public/UVTools/UVGenerationFlattenMapping.h`）：

```cpp
// 为静态网格体生成展开 UV
UStaticMesh* Mesh = /* ... */;
int32 TargetUVChannel = UVGenerationUtils::GetNextOpenUVChannel(Mesh, 0);
float AngleThreshold = 66.0f;
UUVGenerationFlattenMapping::GenerateFlattenMappingUVs(Mesh, TargetUVChannel, AngleThreshold);

// 设置光照图分辨率
UVGenerationUtils::SetupGeneratedLightmapUVResolution(Mesh, 0);
```

**使用 FDatasmithImporterUtils 工具类**（来源：`Public/Utility/DatasmithImporterUtils.h`）：

```cpp
// 从 UDatasmithScene 资产加载 IDatasmithScene
UDatasmithScene* SceneAsset = /* ... */;
TSharedPtr<IDatasmithScene> Scene = FDatasmithImporterUtils::LoadDatasmithScene(SceneAsset);

// 查找场景中的所有 SceneActor
TArray<ADatasmithSceneActor*> SceneActors = FDatasmithImporterUtils::FindSceneActors(World, SceneAsset);

// 查找资产（支持相对路径和绝对路径）
UStaticMesh* Mesh = FDatasmithImporterUtils::FindAsset<UStaticMesh>(AssetsContext, TEXT("MyMesh"));

// 检查是否可以创建资产
FText FailReason;
bool bCanCreate = FDatasmithImporterUtils::CanCreateAsset<UStaticMesh>(Package, TEXT("NewMesh"), FailReason);

// 获取材质的依赖排序列表
auto OrderedMaterials = FDatasmithImporterUtils::GetOrderedListOfMaterialsReferencedByMaterials(SceneElement);
```

## Demo 示例

**最小的蓝图脚本化导入示例**（.h + .cpp）：

```cpp
// MyDatasmithImporter.h
#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "MyDatasmithImporter.generated.h"

UCLASS()
class UMyDatasmithImporter : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "My Tools | Datasmith")
    static bool ImportDatasmithFile(const FString& FilePath, const FString& DestinationFolder);
};
```

```cpp
// MyDatasmithImporter.cpp
#include "MyDatasmithImporter.h"
#include "DatasmithBlueprintLibrary.h"

bool UMyDatasmithImporter::ImportDatasmithFile(
    const FString& FilePath,
    const FString& DestinationFolder)
{
    // 1. 从文件构造场景
    UDatasmithSceneElement* SceneElement =
        UDatasmithSceneElement::ConstructDatasmithSceneFromFile(FilePath);

    if (!SceneElement)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to construct Datasmith scene from: %s"), *FilePath);
        return false;
    }

    // 2. 获取并修改导入选项（可选）
    // UObject* Options = SceneElement->GetOptions(nullptr);

    // 3. 执行导入
    FDatasmithImportFactoryCreateFileResult Result = SceneElement->ImportScene(DestinationFolder);

    // 4. 处理结果
    if (Result.bImportSucceed)
    {
        UE_LOG(LogTemp, Log, TEXT("Successfully imported %d actors, %d meshes"),
            Result.ImportedActors.Num(),
            Result.ImportedMeshes.Num());
    }

    // 5. 清理
    SceneElement->DestroyScene();

    return Result.bImportSucceed;
}
```

## 模块依赖

DatasmithImporter 模块（`DatasmithImporter.Build.cs`）的独特依赖：

| 模块 | 用途 |
|---|---|
| `DatasmithTranslator` | Datasmith 翻译器接口，定义元素抽象层 |
| `DatasmithNativeTranslator` | 原生 Datasmith 文件（.udatasmith）的翻译器实现 |
| `DatasmithExternalSource` | External Source 框架，支持多种数据源接入 |
| `ExternalSource` | External Source 核心接口 |
| `DatasmithContent` | Datasmith 资产类型定义（UDatasmithScene、UDatasmithSceneActor 等） |
| `MeshDescription` | 网格体描述数据结构，用于导入网格体 |
| `MeshUtilities` | 网格体工具函数，用于构建光照图 UV 等 |
| `InterchangeFramework` | UE 交换框架，部分资产（如纹理）通过此框架导入 |
| `DataprepCore` | Dataprep 核心模块，支持 Producer/Consumer 集成 |
| `FreeImageLib` | 图片处理库（纹理缩放支持） |

> 注：省略了 Core、CoreUObject、Engine、Slate、SlateCore、UMG、InputCore、UnrealEd、EditorStyle、PropertyEditor、Projects、DeveloperSettings 等标准依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 新日志宏 |
| 2026-04-02 | `50a24ff6` | Deprecated GetObjects*/ForEachObjectWithOuter functions that take bool bIncludeNestedObjects. Introduced new overloads that use an enum class instead of a boolean flag. | 废弃旧的对象遍历 API，引入枚举参数替代布尔标志 |
| 2026-03-06 | `7b69892a` | clean up code changing texture properties with wrapping in PreEditChange/PostEditChange as required. | 整理纹理属性修改代码，正确使用 PreEditChange/PostEditChange 包装 |
| 2026-03-05 | `1adb9f68` | New material translator work: | 新材质翻译器开发工作 |

### 维护评价

- **年龄**：约 7 年（2019 年创建），从 Enterprise 分支迁入
- **更新频率**：近期（2026 年）仍有多次更新，包括编译修复、日志迁移、API 清理和材质翻译器开发
- **维护状态**：**活跃维护中**。作为 Epic Games 官方企业级插件，持续获得更新。近期更新以基础设施改进（编译警告修复、日志宏迁移）和功能开发（新材质翻译器）为主
- **已知限制**：
  - 默认未启用，需要手动开启
  - 布料导入器（Cloth Importer）已在 UE 5.5 中废弃
  - 部分功能标记为 Experimental（Dataprep Producer/Consumer、UV 展开操作）
- **推荐使用**：✅ 强烈推荐。这是 Unreal Engine 官方的 CAD/BIM 数据导入方案，功能完善且持续维护。适合建筑可视化、工业设计和数字孪生项目

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter/Tests)