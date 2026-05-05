# Datasmith Content

> Content for Datasmith Importer.

| 属性 | 值 |
|---|---|
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（材质模板、纹理、图标、蓝图） |
| 模块 | `DatasmithContent` (Runtime), `DatasmithContentEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2017-12-08 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithContent) | |

## 用途

Datasmith Content 是 Datasmith 导入管线的**运行时内容与类型基础设施插件**。它不负责实际的文件解析（那是 Datasmith Importer 的工作），而是提供：

1. **Object Template 系统**：一套用于 reimport（重新导入）的属性模板，记录上次导入时对象的状态，使重新导入时能检测用户修改、保留用户覆盖、仅更新源文件变更。
2. **核心资产类型定义**：`UDatasmithScene`（场景资产）、`ADatasmithAreaLightActor`（区域灯光）、`ADatasmithSceneActor`（场景根 Actor）等，是 Datasmith 导入结果的数据容器。
3. **导入选项与配置**：所有 Datasmith 导入对话框中可见的选项结构体（曲面细分、Lightmap、冲突策略等）。
4. **蓝图函数库**：提供运行时查询 Datasmith 元数据的蓝图节点。
5. **材质与纹理资产**：VRED/DeltaGen 等 CAD 软件专用的材质模板，以及通用的 Datasmith 材质。
6. **自定义动作扩展点**：允许开发者注册自定义的后处理动作（Content Browser 右键菜单）。

简言之：这个插件是 Datasmith 生态系统的**类型层和资产层**，为导入器提供数据模型和默认资源。

## 使用场景

- 你从 3ds Max、Revit、SketchUp、CATIA 等 DCC/CAO 工具通过 Datasmith 导入了场景 → 此插件提供场景资产、灯光 Actor、材质模板等运行时类型
- 你需要重新导入 Datasmith 场景并保留你在 UE 中做的修改 → Object Template 系统负责三方合并（旧导入、用户修改、新导入）
- 你需要在蓝图中查询 Datasmith 对象的元数据（如来源文件、唯一 ID）→ 使用 `DatasmithContentBlueprintLibrary` 节点
- 你使用 VRED 或 DeltaGen 导入 FBX 场景 → 此插件包含专用材质（MetallicCarpaint、Glass、Chrome 等）
- 你想为 Datasmith 导入流程添加自定义后处理步骤 → 继承 `UDatasmithCustomActionBase`

## 子模块概览

本插件包含 34 个头文件 + 34 个 cpp 文件（共 68 个源文件），分为以下子模块：

| 子模块 | 关键类 | 说明 |
|---|---|---|
| 核心场景类型 | `UDatasmithScene`, `ADatasmithSceneActor` | 场景资产和根 Actor |
| 区域灯光 | `ADatasmithAreaLightActor` | Datasmith 区域灯光 Actor |
| Object Template 系统 | `UDatasmithObjectTemplate` 及 16 个子类 | reimport 属性跟踪与三方合并 |
| 导入选项 | `UDatasmithImportOptions`, `FDatasmithTessellationOptions` 等 | 导入配置结构体 |
| 导入数据 | `UDatasmithAssetImportData` 及多个格式子类 | 各格式的导入元数据 |
| Asset User Data | `UDatasmithAssetUserData` | Datasmith 元数据存储 |
| 自定义动作 | `UDatasmithCustomActionBase`, `FDatasmithCustomActionManager` | 后处理扩展点 |
| 蓝图函数库 | `UDatasmithContentBlueprintLibrary` | 蓝图可调用的查询节点 |
| 编辑器扩展 | `DatasmithContentEditor` 模块 | 资产定义、详情面板、样式 |

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Datasmith User Data` | 获取对象的 Datasmith 用户数据组件 | `UDatasmithContentBlueprintLibrary` |
| `Get Datasmith User Data Value For Key` | 按 key 查询单个元数据值 | `UDatasmithContentBlueprintLibrary` |
| `Get Datasmith User Data Values For Key` | 按 key 查询多个元数据值（支持部分匹配） | `UDatasmithContentBlueprintLibrary` |
| `Get Datasmith User Data Keys And Values For Value` | 按值内容反查所有匹配的 key-value 对 | `UDatasmithContentBlueprintLibrary` |
| `Play Level Sequence` | 播放导入的 Level Sequence | `ADatasmithImportedSequencesActor` |

### 编辑器专用节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get All Datasmith User Data` | 查找所有已加载对象的 Datasmith 用户数据（慢操作） | `UDatasmithContentBlueprintLibrary` |
| `Get All Objects And Values For Key` | 按 key 查找所有匹配的对象及其值（慢操作） | `UDatasmithContentBlueprintLibrary` |

### 使用示例（蓝图描述）

**查询物体的来源文件：**
1. 放置一个 "Get Datasmith User Data Value For Key" 节点
2. Object 引脚连接到你想查询的 Actor 或组件
3. Key 引脚输入 `"_DatasmithUniqueId"`（或自定义 key）
4. 输出即为该 key 对应的字符串值

**按材质名称查找所有物体：**
1. 放置一个 "Get All Objects And Values For Key" 节点（编辑器蓝图）
2. Key 引脚输入材质相关的 key
3. Object Class 选择 `AActor`（或 `UStaticMeshComponent` 等）
4. Out Objects 和 Out Values 输出匹配的物体和值

## C++ 用法

### 头文件引入

```cpp
// 核心场景类型
#include "DatasmithScene.h"
#include "DatasmithSceneActor.h"

// 区域灯光
#include "DatasmithAreaLightActor.h"

// 蓝图函数库
#include "DatasmithContentBlueprintLibrary.h"

// Asset User Data
#include "DatasmithAssetUserData.h"

// 导入选项
#include "DatasmithImportOptions.h"

// Object Template 系统
#include "ObjectTemplates/DatasmithObjectTemplate.h"

// 自定义动作
#include "DatasmithCustomAction.h"

// 额外数据扩展
#include "DatasmithAdditionalData.h"
```

### 基本用法：查询 Datasmith 元数据

从 `DatasmithContentBlueprintLibrary.cpp` 提取的典型用法：

```cpp
// 获取对象的 Datasmith 用户数据
UDatasmithAssetUserData* UserData = UDatasmithAssetUserData::GetDatasmithUserData(MyActor);

if (UserData)
{
    // 查询特定 key 的值
    FString Value = UDatasmithAssetUserData::GetDatasmithUserDataValueForKey(
        MyActor, FName("MyKey"), /*bPartialMatchKey=*/ false
    );
    
    // 查询一个 key 对应的所有值
    TArray<FString> Values = UDatasmithAssetUserData::GetDatasmithUserDataValuesForKey(
        MyActor, FName("MyKey"), /*bPartialMatchKey=*/ true
    );
    
    // 设置元数据
    UDatasmithAssetUserData::SetDatasmithUserDataValueForKey(
        MyActor, FName("CustomTag"), TEXT("MyValue")
    );
    
    // 直接访问 MetaData map
    for (const auto& Kvp : UserData->MetaData)
    {
        UE_LOG(LogTemp, Log, TEXT("Key: %s, Value: %s"), *Kvp.Key.ToString(), *Kvp.Value);
    }
}
```

### Object Template 系统：reimport 时的三方合并

```cpp
#include "ObjectTemplates/DatasmithObjectTemplate.h"
#include "DatasmithAssetUserData.h"

// 获取对象上的某个 template
UDatasmithLightComponentTemplate* LightTemplate =
    FDatasmithObjectTemplateUtils::GetObjectTemplate<UDatasmithLightComponentTemplate>(MyLightComponent);

if (LightTemplate)
{
    // 从当前对象状态加载 template（记录当前值）
    LightTemplate->Load(MyLightComponent);
    
    // 将 template 应用到目标对象（仅覆盖未被用户修改的属性）
    LightTemplate->Apply(MyOtherLightComponent, /*bForce=*/ false);
}

// 三方合并：旧集合、用户修改后的集合、新导入的集合
TSet<FName> MergedSet = FDatasmithObjectTemplateUtils::ThreeWaySetMerge(
    OldImportedSet,    // 上次导入的数据
    CurrentUserSet,    // 当前用户修改后的数据
    NewImportedSet     // 新导入的数据
);
```

### 自定义动作

```cpp
#include "DatasmithCustomAction.h"

// 继承 UDatasmithCustomActionBase 创建自定义动作
UCLASS()
class UMyDatasmithAction : public UDatasmithCustomActionBase
{
    GENERATED_BODY()

public:
    virtual const FText& GetLabel() override
    {
        static FText Label = NSLOCTEXT("MyPlugin", "ActionLabel", "My Custom Action");
        return Label;
    }

    virtual const FText& GetTooltip() override
    {
        static FText Tooltip = NSLOCTEXT("MyPlugin", "ActionTooltip", "Apply custom processing");
        return Tooltip;
    }

    virtual bool CanApplyOnAssets(const TArray<FAssetData>& SelectedAssets) override
    {
        // 判断是否对选中资产可用
        for (const FAssetData& Asset : SelectedAssets)
        {
            if (Asset.GetClass() == UStaticMesh::StaticClass())
                return true;
        }
        return false;
    }

    virtual void ApplyOnAssets(const TArray<FAssetData>& SelectedAssets) override
    {
        // 执行自定义处理
        for (const FAssetData& Asset : SelectedAssets)
        {
            // 处理逻辑...
        }
    }

    virtual bool CanApplyOnActors(const TArray<AActor*>& SelectedActors) override { return false; }
    virtual void ApplyOnActors(const TArray<AActor*>& SelectedActors) override {}
};
```

### 进阶用法：自定义 AdditionalData

```cpp
#include "DatasmithAdditionalData.h"
#include "DatasmithAssetImportData.h"

// 定义自定义附加数据
UCLASS()
class UMyAdditionalData : public UDatasmithAdditionalData
{
    GENERATED_BODY()
public:
    UPROPERTY()
    FString CustomProperty;
};

// 创建附加数据实例
UMyAdditionalData* Data = Datasmith::MakeAdditionalData<UMyAdditionalData>();
Data->CustomProperty = TEXT("Hello");

// 获取资产上的附加数据
FAssetData AssetData = FAssetData(MyAsset);
UMyAdditionalData* Found = Datasmith::GetAdditionalData<UMyAdditionalData>(AssetData);

// 获取所有同类型附加数据
TArray<UMyAdditionalData*> AllData = Datasmith::GetMultipleAdditionalData<UMyAdditionalData>(AssetData);
```

## Demo 示例

### 最小示例：查询 Datasmith 元数据

**Build.cs 依赖：**

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Engine",
    "DatasmithContent"  // Runtime 模块
});
```

**DatasmithMetadataQuery.h：**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "DatasmithAssetUserData.h"

class FDatasmithMetadataHelper
{
public:
    /** 查询指定 Actor 上所有 Datasmith 元数据 */
    static void LogAllMetadata(AActor* Actor)
    {
        if (!Actor) return;

        UDatasmithAssetUserData* UserData = UDatasmithAssetUserData::GetDatasmithUserData(Actor);
        if (!UserData)
        {
            UE_LOG(LogTemp, Warning, TEXT("No Datasmith metadata on %s"), *Actor->GetName());
            return;
        }

        UE_LOG(LogTemp, Log, TEXT("=== Datasmith Metadata for %s ==="), *Actor->GetName());
        for (const auto& Kvp : UserData->MetaData)
        {
            UE_LOG(LogTemp, Log, TEXT("  %s = %s"), *Kvp.Key.ToString(), *Kvp.Value);
        }
    }

    /** 按来源 URI 查找物体 */
    static TArray<UObject*> FindObjectsBySourceUri(const FString& SourceUri)
    {
        TArray<UObject*> Results;
        // 在编辑器中使用 GetAllObjectsAndValuesForKey 遍历
        // 这里展示 C++ 直接用法
        for (TObjectIterator<UDatasmithAssetUserData> It; It; ++It)
        {
            UDatasmithAssetUserData* UserData = *It;
            for (const auto& Kvp : UserData->MetaData)
            {
                if (Kvp.Value.Contains(SourceUri))
                {
                    Results.Add(UserData->GetOuter());
                    break;
                }
            }
        }
        return Results;
    }
};
```

## 模块依赖

### DatasmithContent（Runtime 模块）

| 模块 | 用途 |
|---|---|
| `CinematicCamera` | 相机 Actor 模板支持 |
| `Core` | 核心类型和容器 |
| `CoreUObject` | UObject 反射系统 |
| `Engine` | Actor、组件、材质等引擎核心 |
| `RenderCore` | 渲染核心类型 |
| `Landscape` | 地形模板支持（Private） |
| `LevelSequence` | Level Sequence 导入支持（Private） |
| `MeshDescription` | 网格描述数据（Private） |
| `StaticMeshDescription` | 静态网格描述（Private） |
| `VariantManagerContent` | 变体管理器支持（Private） |
| `Projects` | 插件系统（Private） |

### DatasmithContentEditor（Editor 模块）

| 模块 | 用途 |
|---|---|
| `DatasmithContent` | Runtime 模块（Public） |
| `AssetDefinition` | 资产定义系统 |
| `ContentBrowser` | 内容浏览器集成 |
| `DesktopPlatform` | 桌面平台对话框 |
| `EditorFramework` | 编辑器框架 |
| `UnrealEd` | 编辑器核心 |
| `PropertyEditor` | 属性面板自定义（Private） |
| `SlateCore` / `Slate` | UI 框架（Private） |
| `ToolMenus` | 菜单扩展（Private） |
| `DetailCustomizations` | 详情面板自定义（Private） |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-07-14 | `8c4cad91` | Changed all WITH_EDITORONLY_DATA properties in StaticMesh to have accessors | 引擎级重构：将 StaticMesh 的编辑器属性改为 accessor 模式，此插件需要适配 |
| 2025-07-10 | `abb369e2` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files | 代码质量优化，减少编译时间 |
| 2025-06-25 | `84880cbc` | Updated dll storage on code using UnrealCodeFixup | DLL 导出符号规范化 |

### 维护评价

- **创建时间**：2017 年 12 月，是 Datasmith 功能发布时的伴生插件
- **最近更新**：最近一次实质性更新在 2025 年 7 月，但主要是引擎级重构的被动适配，非功能更新
- **维护状态**：**被动维护**。Datasmith 作为 Enterprise 功能已趋于稳定，此插件主要随引擎重构被动更新
- **已知限制**：Cloth 导入功能在 UE 5.5 中已废弃（`UE_DEPRECATED(5.5, "The experimental Cloth importer is no longer supported.")`）
- **推荐使用**：✅ 是。如果你使用 Datasmith 导入管线，此插件是必需的基础设施。它默认启用，无需手动配置

## 核心类层次结构

```
UObject
├── UDatasmithScene                    ← 场景资产（存储所有导入资源的映射）
├── UDatasmithOptionsBase              ← 导入选项基类
│   ├── UDatasmithImportOptions        ← 完整导入选项
│   └── UDatasmithCommonTessellationOptions ← 曲面细分选项
├── UDatasmithObjectTemplate           ← Object Template 基类
│   ├── UDatasmithActorTemplate        ← Actor 层级/标签模板
│   ├── UDatasmithStaticMeshTemplate   ← 静态网格模板
│   ├── UDatasmithMaterialInstanceTemplate ← 材质实例模板
│   ├── UDatasmithLightComponentTemplate ← 灯光组件模板
│   ├── UDatasmithPointLightComponentTemplate
│   ├── UDatasmithSpotLightComponentTemplate
│   ├── UDatasmithSkyLightComponentTemplate
│   ├── UDatasmithSceneComponentTemplate
│   ├── UDatasmithStaticMeshComponentTemplate
│   ├── UDatasmithAreaLightActorTemplate
│   ├── UDatasmithCineCameraActorTemplate
│   ├── UDatasmithCineCameraComponentTemplate
│   ├── UDatasmithPostProcessVolumeTemplate
│   ├── UDatasmithDecalComponentTemplate
│   └── UDatasmithLandscapeTemplate
├── UDatasmithAssetImportData          ← 导入元数据基类
│   ├── UDatasmithStaticMeshImportData
│   │   └── UDatasmithStaticMeshCADImportData
│   ├── UDatasmithSceneImportData
│   │   ├── UDatasmithTranslatedSceneImportData
│   │   ├── UDatasmithCADImportSceneData
│   │   ├── UDatasmithMDLSceneImportData
│   │   ├── UDatasmithGLTFSceneImportData
│   │   └── UDatasmithFBXSceneImportData
│   │       ├── UDatasmithDeltaGenSceneImportData
│   │       └── UDatasmithVREDSceneImportData
│   └── ...
├── UDatasmithAssetUserData            ← 元数据存储
├── UDatasmithAdditionalData           ← 附加数据扩展基类
└── UDatasmithCustomActionBase         ← 自定义动作基类（UObject）

AActor
├── ADatasmithSceneActor               ← 场景根 Actor
├── ADatasmithAreaLightActor           ← 区域灯光 Actor
└── ADatasmithImportedSequencesActor   ← 导入序列 Actor
```

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithContent)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
