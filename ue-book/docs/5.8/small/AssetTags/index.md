# Asset Tags

> Provides high-level management and access to asset tags and collections for runtime and editor scripting.

| 属性 | 值 |
|---|---|
| 中文名 | 资产标签 |
| 分类 | Other |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AssetTags` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-02 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AssetTags) | |

## 用途

Asset Tags 插件提供了一个引擎子系统 (`UAssetTagsSubsystem`)，用于在运行时脚本（如蓝图或 C++）中以编程方式查询和访问在编辑器中组织的“资产集合”（Collections）。它允许开发者在游戏运行时动态获取一个集合中包含的所有资产信息，而无需预先硬编码资产路径。在编辑器环境下，该子系统还提供创建、修改集合等管理功能（但此部分功能在 5.6 版本后已被标记为废弃，推荐使用新的 `CollectionManagerScriptingSubsystem`）。

## 使用场景

- 你在游戏运行时，需要动态加载或查询一个预先在编辑器中定义好的资产集合（如“所有敌人模型”、“所有关卡资源”）。
- 你需要在蓝图或 C++ 代码中，基于集合名称获取其包含的资产列表，用于动态生成内容或资源验证。
- 你需要在编辑器工具脚本（Python/蓝图编辑器工具）中管理资产集合（注：此功能已建议迁移）。

## 蓝图用法

所有蓝图节点均来自 `UAssetTagsSubsystem` 类。可通过“Get Game Instance Subsystem”节点获取该子系统实例。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Collection Exists` | 检查指定名称的资产集合是否存在。 | `UAssetTagsSubsystem` |
| `Get Collections` | 获取所有可用资产集合的名称列表。 | `UAssetTagsSubsystem` |
| `Get Assets In Collection` | 获取指定集合中的所有资产 (`FAssetData` 数组)。 | `UAssetTagsSubsystem` |
| `Get Collections Containing Asset` | 获取包含指定资产（通过路径）的所有集合名称。 | `UAssetTagsSubsystem` |
| `Get Collections Containing Asset Data` | 获取包含指定资产（通过资产数据）的所有集合名称。 | `UAssetTagsSubsystem` |
| `Get Collections Containing Asset Ptr` | 获取包含指定资产（通过对象指针）的所有集合名称。 | `UAssetTagsSubsystem` |

**注意**：以下函数在 UE 5.6 中被标记为**废弃**，应使用 `CollectionManagerScriptingSubsystem` 替代：
- `Create Collection`
- `Destroy Collection`
- `Rename Collection`
- `Reparent Collection`
- `Empty Collection`
- `Add Asset To Collection`
- `Remove Asset From Collection`

### 使用示例（蓝图描述）

1.  **查询并使用集合资产**：
    *   在事件图表中，使用“Get Game Instance Subsystem”节点获取 `AssetTagsSubsystem`。
    *   调用 `Get Collections` 获取所有集合名。
    *   使用 `Get Assets In Collection` 并传入一个集合名，获取资产列表。
    *   遍历返回的 `AssetData` 数组，可以用于后续的资产加载或信息查询。

2.  **反向查询资产所属集合**：
    *   已知一个资产的 `SoftObjectPath`（例如通过其他节点获取）。
    *   调用 `Get Collections Containing Asset`，传入该路径。
    *   返回的结果是包含该资产的所有集合名称列表。

## C++ 用法

### 头文件引入

```cpp
#include "AssetTagsSubsystem.h"
```

### 基本用法

获取子系统实例并查询集合。

```cpp
// 来自源码：Source/AssetTags/Public/AssetTagsSubsystem.h
UAssetTagsSubsystem* AssetTagsSubsystem = GEngine->GetEngineSubsystem<UAssetTagsSubsystem>();
if (AssetTagsSubsystem)
{
    // 检查名为 “ImportantAssets” 的集合是否存在
    if (AssetTagsSubsystem->CollectionExists(FName(TEXT("ImportantAssets"))))
    {
        // 获取该集合中的所有资产
        TArray<FAssetData> Assets = AssetTagsSubsystem->GetAssetsInCollection(FName(TEXT("ImportantAssets")));
        for (const FAssetData& AssetData : Assets)
        {
            UE_LOG(LogTemp, Log, TEXT("Asset in collection: %s"), *AssetData.GetSoftObjectPath().ToString());
        }
    }
    
    // 获取包含特定资产的所有集合
    FSoftObjectPath MyAssetPath(TEXT("/Game/Characters/Player/PlayerMesh.PlayerMesh"));
    TArray<FName> ContainingCollections = AssetTagsSubsystem->K2_GetCollectionsContainingAsset(MyAssetPath);
}
```

### 进阶用法

在编辑器环境下（使用 `#if WITH_EDITOR` 宏保护）管理集合。**请注意，这些 API 在 5.6 中已被废弃。**

```cpp
#if WITH_EDITOR
    UAssetTagsSubsystem* EditorAssetTagsSubsystem = GEngine->GetEngineSubsystem<UAssetTagsSubsystem>();
    if (EditorAssetTagsSubsystem)
    {
        // 创建一个本地集合（已废弃）
        EditorAssetTagsSubsystem->CreateCollection(FName(TEXT("NewLocalCollection")), ECollectionScriptingShareType::Local);
        
        // 向集合中添加一个资产（通过 FAssetData，已废弃）
        FAssetData SomeAssetData = /* ... 通过 Asset Registry 或其他方式获取 ... */;
        EditorAssetTagsSubsystem->AddAssetDataToCollection(FName(TEXT("NewLocalCollection")), SomeAssetData);
    }
#endif
```

## Demo 示例

一个简单的 Actor，用于在开始游戏时打印所有资产集合及其内容。

**AssetTagsDemoActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "AssetTagsDemoActor.generated.h"

UCLASS()
class YOURPROJECT_API AAssetTagsDemoActor : public AActor
{
    GENERATED_BODY()
    
public:
    virtual void BeginPlay() override;
};
```

**AssetTagsDemoActor.cpp**
```cpp
#include "AssetTagsDemoActor.h"
#include "AssetTagsSubsystem.h"
#include "Engine/AssetManager.h"

void AAssetTagsDemoActor::BeginPlay()
{
    Super::BeginPlay();
    
    UAssetTagsSubsystem* AssetTagsSubsystem = GEngine->GetEngineSubsystem<UAssetTagsSubsystem>();
    if (!AssetTagsSubsystem)
    {
        UE_LOG(LogTemp, Warning, TEXT("AssetTagsSubsystem is not available."));
        return;
    }
    
    // 获取所有集合名称
    TArray<FName> CollectionNames = AssetTagsSubsystem->GetCollections();
    UE_LOG(LogTemp, Log, TEXT("Found %d asset collections."), CollectionNames.Num());
    
    for (const FName& CollectionName : CollectionNames)
    {
        UE_LOG(LogTemp, Log, TEXT("--- Collection: %s ---"), *CollectionName.ToString());
        
        // 获取集合内的资产
        TArray<FAssetData> AssetsInCollection = AssetTagsSubsystem->GetAssetsInCollection(CollectionName);
        for (const FAssetData& AssetData : AssetsInCollection)
        {
            UE_LOG(LogTemp, Log, TEXT("  Asset: %s"), *AssetData.GetSoftObjectPath().ToString());
        }
    }
}
```

## 模块依赖

基于插件的性质（运行时引擎子系统），它依赖于 UE 的核心框架模块。你的模块如果要使用它，需要确保在 Build.cs 中添加依赖。

| 模块 | 用途 |
|---|---|
| `AssetRegistry` | 子系统内部通过 Asset Registry 获取资产元数据。 |

**说明**：你的模块通常也需要依赖 `Core`, `CoreUObject`, `Engine` 等基础模块来使用子系统功能。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧的 UE_LOG 宏迁移到新的 UE_LOGF 格式。 |
| 2025-04-23 | `6ae57335` | Used UnrealGame build target to find and convert all files to have dllstorage on methods/staticvar i | 为文件添加 `dllexport`/`dllimport` 标记，以支持动态链接库构建。 |
| 2025-03-31 | `6256a02a` | Deprecating the AssetTagsSubsystem's editor-only Collection BP APIs in favor of the new CollectionMa | **重要更新**：废弃 `AssetTagsSubsystem` 的编辑器集合管理 API，推荐使用新的 `CollectionManagerScriptingSubsystem`。 |
| 2025-03-28 | `8eb36a6d` | Renamed CollectionExistsWithAnyShareType to GetCollectionsByName. | 重命名函数 `CollectionExistsWithAnyShareType` 为 `GetCollectionsByName`。 |
| 2025-03-18 | `bf633ad3` | CollectionManagerScriptingSubsystem is a new subsystem exposing the Collection Container system to B | 引入了新的 `CollectionManagerScriptingSubsystem`，作为管理资产集合的主要蓝图接口。 |

### 维护评价

Asset Tags 插件自 2019 年创建，目前仍在维护中，但其角色正在发生变化。最新的提交记录（2025年3月）明确表示，该插件中用于**编辑器内管理集合**的功能已被废弃，并建议使用新引入的 `CollectionManagerScriptingSubsystem`。然而，其**运行时查询集合**的功能（如 `GetCollections`, `GetAssetsInCollection`）仍然可用且未被废弃，适用于游戏内逻辑。

**总结**：该插件的核心价值已从“全功能管理工具”转变为“轻量级运行时查询接口”。如果你只需要在运行时读取集合信息，该插件仍然适用且得到维护。如果你需要在编辑器或工具中创建/修改集合，应优先使用新的 `CollectionManagerScriptingSubsystem`。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AssetTags)
- [官方文档](https://docs.unrealengine.com)（暂无专属页面）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/Runtime/AssetTags)（路径待确认，通常位于 Engine/Tests 下）