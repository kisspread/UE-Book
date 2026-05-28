# Datasmith Content

> Content for Datasmith Importer.

| 属性 | 值 |
|---|---|
| 中文名 | Datasmith 内容 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（材质模板、数据资产） |
| 模块 | `DatasmithContent` (Runtime), `DatasmithContentEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2017-12-08 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithContent) | |

## 用途

DatasmithContent 是 Datasmith 导入系统的**运行时数据骨架**。它本身不执行导入操作（那是 `DatasmithImporter` 的工作），而是定义了导入后资产需要携带的所有数据结构：元数据标签、导入选项配置、对象模板（Object Template）以及场景管理 Actor。

简单来说，这个插件解决三个问题：

1. **数据持久化**：将 CAD/3D 设计软件（如 3ds Max、Revit、CATIA、SketchUp 等）中导入的元信息（材质参数、层级关系、动画设置）以标准化方式存储在 UE 资产中。
2. **重导入保护**：通过 Object Template 机制，在重导入时保护用户手动修改过的属性不被覆盖（三路合并算法）。
3. **运行时访问**：提供蓝图可调用的 API，让游戏运行时也能读取 Datasmith 附加的元数据。

该插件依赖 `VariantManagerContent`（变体管理内容），说明 Datasmith 导入的场景支持与 Variant Manager 联动。

## 使用场景

- 你从 CAD 软件（SolidWorks、CATIA、Revit）导入了大型装配体 → 用 DatasmithContent 存储曲面细分参数、材质映射关系
- 你导入了建筑可视化场景并需要在蓝图中读取构件的属性标签（如"承重墙"、"窗户类型"）→ 用 `UDatasmithAssetUserData` 的元数据
- 你需要在重导入时保留对灯光强度、材质参数的手动调整 → Object Template 机制自动处理
- 你在制作 AEC/汽车可视化，需要基于元数据创建交互式热点 → 用蓝图读取 Datasmith User Data

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Datasmith User Data` | 获取对象上的 Datasmith 用户数据对象 | `UDatasmithContentBlueprintLibrary` |
| `Get Datasmith User Data Value For Key` | 按键名查询单个元数据值（支持部分匹配） | `UDatasmithContentBlueprintLibrary` |
| `Get Datasmith User Data Values For Key` | 按键名查询所有匹配的元数据值 | `UDatasmithContentBlueprintLibrary` |
| `Get Datasmith User Data Keys And Values For Value` | 按值内容反查所有匹配的键值对 | `UDatasmithContentBlueprintLibrary` |
| `Get All Datasmith User Data` | （仅编辑器）查找所有已加载对象的 Datasmith 数据 | `UDatasmithContentBlueprintLibrary` |
| `Get All Objects And Values For Key` | （仅编辑器）查找含指定键的所有对象及其值 | `UDatasmithContentBlueprintLibrary` |
| `Play Level Sequence` | 播放导入的关卡序列 | `ADatasmithImportedSequencesActor` |

### 使用示例：查询导入构件的元数据

假设你有一个从 Revit 导入的静态网格体，想知道它的构件类型：

1. 选中该 Static Mesh 资产，添加 `Datasmith Asset User Data`
2. 在运行时蓝图中：
   - 对目标 Actor 调用 `Get Datasmith User Data Value For Key`
   - Key 设为 `"family"`，bPartialMatchKey 为 false
   - 输出即为 Revit 中的 Family 名称

### 使用示例：遍历所有标记了特定标签的对象

在编辑器工具蓝图中：
1. 调用 `Get All Objects And Values For Key`
2. Key 设为 `"ElementId"`，ObjectClass 设为 `StaticMesh`
3. 得到所有从 BIM 软件导入的、带有 ElementId 的网格体列表

## C++ 用法

### 头文件引入

```cpp
#include "DatasmithContentBlueprintLibrary.h"
#include "DatasmithAssetUserData.h"
#include "DatasmithImportOptions.h"
#include "DatasmithScene.h"
```

### 基本用法：读取和设置 Datasmith 元数据

```cpp
// 在任意 UObject 上读取 Datasmith 用户数据
UDatasmithAssetUserData* UserData = UDatasmithAssetUserData::GetDatasmithUserData(MyActor);
if (UserData)
{
    FString FamilyName = UserData->MetaData.FindRef(FName("family"));
    UE_LOG(LogTemp, Log, TEXT("构件族名: %s"), *FamilyName);
}

// 设置元数据
UDatasmithAssetUserData::SetDatasmithUserDataValueForKey(MyActor, FName("CustomTag"), TEXT("承重墙"));
```

### 基本用法：访问导入场景的资源映射

```cpp
// 获取 Datasmith 场景资产
UDatasmithScene* DatasmithScene = /* 从 ADatasmithSceneActor 获取 */;

#if WITH_EDITORONLY_DATA
// 遍历该场景引用的所有静态网格体
for (const auto& Pair : DatasmithScene->StaticMeshes)
{
    FName MeshName = Pair.Key;
    TSoftObjectPtr<UStaticMesh> MeshPtr = Pair.Value;
    UStaticMesh* Mesh = MeshPtr.LoadSynchronous();
    if (Mesh)
    {
        UE_LOG(LogTemp, Log, TEXT("场景网格体: %s"), *MeshName.ToString());
    }
}

// 同样可访问材质、纹理、序列等
for (const auto& Pair : DatasmithScene->Materials)
{
    // 处理材质...
}
#endif
```

### 进阶用法：自定义导入选项

```cpp
#include "DatasmithImportOptions.h"

// 配置曲面细分选项（用于 CAD 模型导入）
FDatasmithTessellationOptions TessOptions;
TessOptions.ChordTolerance = 0.1f;           // 弦公差（厘米），越小三角面越多
TessOptions.MaxEdgeLength = 10.0f;           // 最大边长（厘米）
TessOptions.NormalTolerance = 15.0f;         // 法线容差（度），越小细节越丰富
TessOptions.StitchingTechnique = EDatasmithCADStitchingTechnique::StitchingSew;

// 配置基础导入选项
FDatasmithImportBaseOptions BaseOptions;
BaseOptions.bIncludeGeometry = true;
BaseOptions.bIncludeMaterial = true;
BaseOptions.bIncludeLight = true;
BaseOptions.bIncludeCamera = false;
BaseOptions.bIncludeAnimation = false;
BaseOptions.StaticMeshOptions.bGenerateLightmapUVs = true;
BaseOptions.StaticMeshOptions.MinLightmapResolution = EDatasmithImportLightmapMin::LIGHTMAP_64;
BaseOptions.StaticMeshOptions.MaxLightmapResolution = EDatasmithImportLightmapMax::LIGHTMAP_1024;
```

### 进阶用法：Object Template 三路合并保护用户修改

```cpp
#include "ObjectTemplates/DatasmithObjectTemplate.h"

// Object Template 的核心思想：
// 1. 导入时存储初始值（Load）
// 2. 重导入时比较新旧模板，只更新未被用户修改的属性（UpdateObject + bForce=false）
// 3. 强制更新所有属性（UpdateObject + bForce=true）

// 获取某个对象的模板
UDatasmithObjectTemplate* Template = FDatasmithObjectTemplateUtils::GetObjectTemplate(MyStaticMesh, UDatasmithStaticMeshTemplate::StaticClass());

// 应用模板（bForce=false 时保护用户修改）
if (Template)
{
    Template->Apply(MyStaticMesh, false);
}

// 两个集合的三路合并（处理标签、层级等集合属性）
TSet<FName> OldTags = { FName("Wall"), FName("Structural") };
TSet<FName> CurrentTags = { FName("Wall"), FName("Structural"), FName("CustomTag") }; // 用户添加了 CustomTag
TSet<FName> NewTags = { FName("Wall"), FName("Exterior") }; // 源文件中 Structural 改名为 Exterior

TSet<FName> MergedTags = FDatasmithObjectTemplateUtils::ThreeWaySetMerge(OldTags, CurrentTags, NewTags);
// 结果: { "Wall", "Exterior", "CustomTag" }
// - Wall: 三方都有，保留
// - Exterior: 新导入的，添加
// - Structural: 用户保留但源已删除，移除
// - CustomTag: 用户添加的，保留
```

## Demo 示例

一个完整的最小示例：在编辑器中查询所有 Datasmith 导入资产的元数据。

```cpp
// DatasmithMetadataHelper.h
#pragma once

#include "CoreMinimal.h"
#include "DatasmithAssetUserData.h"

class FDatasmithMetadataHelper
{
public:
    // 查找所有带有指定 Datasmith 元数据键的资产
    static TArray<UObject*> FindAssetsWithDatasmithKey(FName Key, TSubclassOf<UObject> ObjectClass = nullptr)
    {
        TArray<UObject*> Results;

#if WITH_EDITOR
        TArray<UDatasmithAssetUserData*> AllUserData;
        UDatasmithContentBlueprintLibrary::GetAllDatasmithUserData(ObjectClass, AllUserData);

        for (UDatasmithAssetUserData* UserData : AllUserData)
        {
            if (UserData && UserData->MetaData.Contains(Key))
            {
                // 获取拥有此 UserData 的外部对象
                UObject* Outer = UserData->GetOuter();
                if (Outer)
                {
                    Results.Add(Outer);
                }
            }
        }
#endif

        return Results;
    }

    // 打印对象的所有 Datasmith 元数据
    static void PrintAllMetadata(UObject* Object)
    {
        if (!Object) return;

        UDatasmithAssetUserData* UserData = UDatasmithAssetUserData::GetDatasmithUserData(Object);
        if (!UserData)
        {
            UE_LOG(LogTemp, Warning, TEXT("对象 '%s' 没有 Datasmith 用户数据"), *Object->GetName());
            return;
        }

        UE_LOG(LogTemp, Log, TEXT("=== %s 的 Datasmith 元数据 ==="), *Object->GetName());
        for (const auto& Pair : UserData->MetaData)
        {
            UE_LOG(LogTemp, Log, TEXT("  %s = %s"), *Pair.Key.ToString(), *Pair.Value);
        }
    }
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `DatasmithCore` | Datasmith 核心数据类型和接口定义 |
| `VariantManagerContent` | 变体管理内容（插件级依赖，用于支持 Level Variant Sets） |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移至新的 UE_LOGF 格式 |
| 2026-03-24 | `69a7403a` | Fixed cooking failure duue to ensure | 修复了烹饪打包时因 ensure 断言导致的失败 |
| 2026-03-24 | `76f61985` | Deprecated UDatasmithStaticMeshCADImportData class as it is not used anymore and introduces a securi | 废弃 UDatasmithStaticMeshCADImportData 类，因存在安全隐患且不再使用 |
| 2026-03-23 | `06410f9f` | [Backout] - CL52072615 | 回退了一次变更 |
| 2026-03-23 | `c14d73ba` | Deprecated UDatasmithStaticMeshCADImportData class as it is not used anymore and introduces a securi | 废弃 UDatasmithStaticMeshCADImportData 类（首次尝试） |

### 维护评价

- **创建于 2017 年**，作为 Epic Enterprise 分支的一部分，历史较长
- **活跃维护中**：最近更新集中在 2026 年 3-4 月，主要是代码清理（废弃旧类、修复烹饪问题、日志宏迁移）
- 作为 Datasmith 生态系统的核心内容层，不太可能被废弃，因为整个 Datasmith 导入管线依赖它
- 正在进行**代际更新**：旧的 CAD 导入数据类（`UDatasmithStaticMeshCADImportData`）已被废弃，推荐使用新的 `UDatasmithParametricSurfaceData` 体系
- **推荐使用**：任何使用 Datasmith 导入工作流的项目都需要此插件，它是默认启用的

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithContent)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithContent/Tests)（如果存在）