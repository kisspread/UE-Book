# Asset Tags

> Provides high-level management and access to asset tags and collections for runtime and editor scripting.

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ✅ 是 |
| 包含内容 | 否 |
| 模块 | AssetTags (Runtime) |
| 创建时间 | 2019-10-01 |
| 年龄标签 | 👴 老古董 (>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/AssetTags) | |

## 用途

AssetTags 插件提供了一个引擎子系统 `UAssetTagsSubsystem`，用于在运行时和编辑器中查询和管理 **资产集合（Collections）**。

集合是 UE 编辑器中的一种资产组织机制——你可以在 Content Browser 中创建集合（如 "Characters"、"VFX"、"Level1Assets"），将资产分组管理。AssetTags 插件的作用是让你能通过蓝图和 C++ 访问这些集合数据。

**关键设计**：该插件在编辑器和打包后的游戏中使用不同的底层实现：
- **编辑器**：通过 `CollectionManager` 直接访问集合管理器
- **打包后（运行时）**：通过 `AssetRegistry` 查询集合标签（集合标签在 Cook 时写入资产注册表）

> ⚠️ **重要提示（UE 5.6+）**：编辑器端的集合管理函数（创建、删除、重命名、添加/移除资产等）已在 5.6 中被标记为废弃。新的替代方案是 `UCollectionManagerScriptingSubsystem`。**运行时查询函数仍然正常可用。**

## 使用场景

- 你在游戏运行时需要查询某个集合中包含哪些资产（例如动态加载某个集合中的所有关卡资产）
- 你需要在运行时判断某个资产属于哪些集合
- 你需要枚举项目中所有可用的集合名称
- 你在编辑器工具脚本中需要操作集合（但建议改用 CollectionManagerScriptingSubsystem）

## 蓝图用法

该插件通过引擎子系统暴露蓝图节点。在蓝图中通过 **Get Engine Subsystem → Asset Tags Subsystem** 获取实例。

### 核心查询节点（运行时可用）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Collection Exists` | 检查指定名称的集合是否存在 | `UAssetTagsSubsystem` |
| `Get Collections` | 获取所有可用集合的名称列表 | `UAssetTagsSubsystem` |
| `Get Assets In Collection` | 获取指定集合中的所有资产（返回 `FAssetData` 数组） | `UAssetTagsSubsystem` |
| `Get Collections Containing Asset` | 获取包含指定资产的所有集合名称 | `UAssetTagsSubsystem` |
| `Get Collections Containing Asset Data` | 同上，接受 `FAssetData` 参数 | `UAssetTagsSubsystem` |
| `Get Collections Containing Asset Ptr` | 同上，接受 `UObject*` 参数 | `UAssetTagsSubsystem` |

### 已废弃的编辑器节点（5.6 废弃）

以下节点仅在编辑器中可用，且已在 UE 5.6 中标记为废弃：

| 节点 | 说明 | 替代方案 |
|---|---|---|
| `Create Collection` | 创建新集合 | `UCollectionManagerScriptingSubsystem` |
| `Destroy Collection` | 销毁集合 | `UCollectionManagerScriptingSubsystem` |
| `Rename Collection` | 重命名集合 | `UCollectionManagerScriptingSubsystem` |
| `Reparent Collection` | 更改集合的父级 | `UCollectionManagerScriptingSubsystem` |
| `Empty Collection` | 清空集合中的所有资产 | `UCollectionManagerScriptingSubsystem` |
| `Add Asset To Collection` | 添加单个资产到集合 | `UCollectionManagerScriptingSubsystem` |
| `Add Assets To Collection` | 批量添加资产到集合 | `UCollectionManagerScriptingSubsystem` |
| `Remove Asset From Collection` | 从集合中移除单个资产 | `UCollectionManagerScriptingSubsystem` |
| `Remove Assets From Collection` | 从集合中批量移除资产 | `UCollectionManagerScriptingSubsystem` |

### 使用示例（蓝图描述）

**查询集合中的资产：**
1. 从任意 Event 节点引出执行线
2. 添加 **Get Engine Subsystem** 节点，选择 `Asset Tags Subsystem` 类
3. 从返回值引出，添加 **Get Collections** 节点 → 获取所有集合名
4. 添加 **Get Assets In Collection** 节点，将集合名作为 `Name` 参数传入
5. 返回的 `FAssetData` 数组可用于获取资产路径、类型等信息

**检查资产所属集合：**
1. 使用 **Get Engine Subsystem → Asset Tags Subsystem**
2. 添加 **Get Collections Containing Asset** 节点
3. 传入资产的 `SoftObjectPath`（如 `/Game/MyFolder/MyAsset.MyAsset`）
4. 返回包含该资产的所有集合名称数组

## C++ 用法

### 头文件引入

```cpp
#include "AssetTagsSubsystem.h"
```

### 获取子系统实例

```cpp
UAssetTagsSubsystem* AssetTagsSubsystem = GEngine->GetEngineSubsystem<UAssetTagsSubsystem>();
```

### 基本用法：运行时查询

```cpp
// 获取子系统
UAssetTagsSubsystem* Subsystem = GEngine->GetEngineSubsystem<UAssetTagsSubsystem>();

// 检查集合是否存在
bool bExists = Subsystem->CollectionExists(TEXT("MyCollection"));

// 获取所有集合名称
TArray<FName> AllCollections = Subsystem->GetCollections();

// 获取某个集合中的所有资产
TArray<FAssetData> Assets = Subsystem->GetAssetsInCollection(TEXT("Characters"));
for (const FAssetData& Asset : Assets)
{
    UE_LOG(LogTemp, Log, TEXT("Asset: %s, Class: %s"), *Asset.GetSoftObjectPath().ToString(), *Asset.AssetClassPath.ToString());
}

// 查询某个资产属于哪些集合
FSoftObjectPath AssetPath(TEXT("/Game/MyFolder/MyAsset.MyAsset"));
TArray<FName> Collections = Subsystem->K2_GetCollectionsContainingAsset(AssetPath);
```

### 进阶用法：编辑器中操作集合（已废弃，仅供参考）

```cpp
#if WITH_EDITOR
UAssetTagsSubsystem* Subsystem = GEngine->GetEngineSubsystem<UAssetTagsSubsystem>();

// 创建集合（5.6 废弃，建议用 UCollectionManagerScriptingSubsystem）
Subsystem->CreateCollection(TEXT("NewCollection"), ECollectionScriptingShareType::Shared);

// 添加资产到集合
FSoftObjectPath AssetPath(TEXT("/Game/Meshes/MyMesh.MyMesh"));
Subsystem->K2_AddAssetToCollection(TEXT("NewCollection"), AssetPath);

// 批量添加
TArray<FSoftObjectPath> AssetPaths = { /* ... */ };
Subsystem->K2_AddAssetsToCollection(TEXT("NewCollection"), AssetPaths);

// 清空集合
Subsystem->EmptyCollection(TEXT("NewCollection"));

// 销毁集合
Subsystem->DestroyCollection(TEXT("NewCollection"));
#endif
```

## Demo 示例

以下是一个完整的最小运行时查询示例，列出项目中所有集合及其资产数量：

```cpp
// MyCollectionQuery.h
#pragma once

#include "CoreMinimal.h"

class FMyCollectionQuery
{
public:
    static void QueryAllCollections();
};
```

```cpp
// MyCollectionQuery.cpp
#include "MyCollectionQuery.h"
#include "AssetTagsSubsystem.h"
#include "AssetRegistry/AssetData.h"
#include "Engine/Engine.h"

void FMyCollectionQuery::QueryAllCollections()
{
    UAssetTagsSubsystem* Subsystem = GEngine->GetEngineSubsystem<UAssetTagsSubsystem>();
    if (!Subsystem)
    {
        UE_LOG(LogTemp, Warning, TEXT("AssetTagsSubsystem not available"));
        return;
    }

    // 获取所有集合
    TArray<FName> Collections = Subsystem->GetCollections();
    UE_LOG(LogTemp, Log, TEXT("Found %d collections"), Collections.Num());

    for (const FName& CollectionName : Collections)
    {
        TArray<FAssetData> Assets = Subsystem->GetAssetsInCollection(CollectionName);
        UE_LOG(LogTemp, Log, TEXT("  Collection '%s': %d assets"), *CollectionName.ToString(), Assets.Num());
    }
}
```

**Build.cs 依赖：**

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
    "Engine",
    "AssetTags"    // 添加此依赖
});
```

## 模块依赖

从 Build.cs 的 `PublicDependencyModuleNames` 提取。如果你要在自己的模块中使用 AssetTags，需要添加以下依赖：

| 模块 | 用途 |
|---|---|
| `Core` | 基础核心库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心（UEngineSubsystem 基类） |
| `AssetRegistry` | 资产注册表（运行时查询集合标签的底层实现） |

**编辑器额外依赖**（仅编辑器构建）：

| 模块 | 用途 |
|---|---|
| `CollectionManager` | 集合管理器（编辑器端操作集合） |
| `UnrealEd` | 编辑器引擎（`UEditorEngine` / `GEditor`） |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-04-23 | `89df8c170d23` | 将所有文件转换为 DLL 导出宏 | 编译基础设施更新，非功能性变更 |
| 2025-03-31 | `6256a02a7c4b` | 废弃编辑器端集合管理 BP API，推荐使用 CollectionManagerScriptingSubsystem | **重大变更**：标志着该插件功能拆分，编辑器管理功能迁移至新子系统 |
| 2025-03-28 | `8eb36a6dfc21` | 重命名 `CollectionExistsWithAnyShareType` 为 `GetCollectionsByName` | API 清理，为废弃做准备 |

### 维护评价

- **创建时间**：2019 年 10 月，已有 6 年以上历史
- **当前状态**：**维护中，但处于功能缩减阶段**
  - 2025 年 3 月的更新明确将编辑器端集合管理功能废弃，迁移到新的 `CollectionManagerScriptingSubsystem`
  - 运行时查询功能（`CollectionExists`、`GetCollections`、`GetAssetsInCollection`、`GetCollectionsContainingAsset` 等）仍然活跃且未被废弃
- **推荐使用**：
  - ✅ **运行时查询集合**：完全可用，这是该插件的核心价值
  - ❌ **编辑器端管理集合**：已废弃，请使用 `UCollectionManagerScriptingSubsystem`
- **风险**：未来版本可能进一步缩减功能，或将运行时查询也迁移至其他子系统

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/AssetTags)
- 官方文档：无（.uplugin 中 DocsURL 为空）
- 测试用例：未找到专用测试文件
