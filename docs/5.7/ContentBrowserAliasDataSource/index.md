# Content Browser - Alias Data Source

> Data Source plugin providing allowing Content Browser items to appear in other directories other than their original location

| 属性 | 值 |
|---|---|
| 分类 | Content Browser |
| 默认启用 | false |
| 包含内容 | false |
| 模块 | ContentBrowserAliasDataSource (Editor) |
| 创建时间 | 2024-05-19 |
| 年龄标签 | 🆕 |
| [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Editor/ContentBrowser/ContentBrowserAliasDataSource) | |

## 用途

ContentBrowserAliasDataSource 是 Content Browser 的扩展数据源插件，允许资产在 Content Browser 中**出现在多个文件夹位置**——除了其真实的物理路径之外，还能显示在指定的"别名路径"下。

核心概念是 **Alias（别名）**：一个别名是一个 `<源资产路径>:<别名路径>` 的映射对，例如 `/Game/MyAsset.MyAsset` → `/Game/SomeFolder/MyAlias`。别名在 Content Browser 中看起来和原始资产几乎完全一样——可以编辑、保存、显示缩略图，但不允许移动或删除别名项本身。

这个插件解决了什么问题？
- **Verse 等系统需要在 Content Browser 中以自定义路径展示资产**，而 Verse 类并不是真正的 UE 资产包，无法通过标准 Asset Registry 路径访问
- **多视角组织资产**：同一个资产可以同时出现在"按类型分类"和"按功能分类"的文件夹中，方便不同工作流的团队成员查找
- **子系统集成**：如 Verse 设备等虚拟资产需要在 Content Browser 中有"存在感"

插件默认不启用（`EnabledByDefault: false`），且标记为 Beta（`IsBetaVersion: true`），需要在项目设置中手动开启。

## 使用场景

- 你在使用 Verse 编程，Verse 类/设备需要在 Content Browser 的自定义路径下可见 → 用此插件
- 你想让同一个 Mesh 资产同时出现在 `/Game/Characters/` 和 `/Game/Weapons/` 下 → 用此插件
- 你需要为 Content Browser 中的虚拟文件夹提供本地化显示名称 → 用此插件

## 蓝图用法

此插件没有暴露 BlueprintCallable 函数。所有 API 都是 C++ 层面的，因为它面向的是引擎子系统集成开发者，而非蓝图用户。

## C++ 用法

### 头文件引入

```cpp
#include "ContentBrowserAliasDataSource.h"
#include "ContentBrowserAliasDataSourceModule.h"
#include "ContentBrowserLocalizedAlias.h"
```

### 基本用法

#### 获取 AliasDataSource 实例

插件启动时自动创建 `UContentBrowserAliasDataSource` 单例，通过模块类获取：

```cpp
// 获取 AliasDataSource 实例
FContentBrowserAliasDataSourceModule& Module = FModuleManager::Get().LoadModuleChecked<FContentBrowserAliasDataSourceModule>("ContentBrowserAliasDataSource");
UContentBrowserAliasDataSource* AliasDataSource = Module.TryGetAliasDataSource();
```

#### 手动添加别名

```cpp
// 假设已获取 AliasDataSource 和 FAssetData
FAssetData AssetData = /* ... */;

// 添加单个别名
AliasDataSource->AddAlias(AssetData, FName("/Game/MyAliases/DisplayName"));

// 添加多个别名
TArray<FName> Aliases = {
    FName("/Game/Aliases/Folder1/DisplayName"),
    FName("/Game/Aliases/Folder2/DisplayName")
};
AliasDataSource->AddAliases(AssetData, Aliases);
```

#### 移除别名

```cpp
// 移除单个别名
AliasDataSource->RemoveAlias(AssetData.GetSoftObjectPath(), FName("/Game/MyAliases/DisplayName"));

// 移除某个资产的所有别名
AliasDataSource->RemoveAliases(AssetData);
```

#### 通过资产元数据自动创建别名

给资产添加 `ContentBrowserAliases` 标签（Tag），值为逗号分隔的别名路径列表：

```cpp
// 在资产的 UCLASS 或 UPROPERTY metadata 中设置
// 或通过 AssetRegistry Tag 设置
FString AliasTagValue = "/Game/Aliases/Path1,/Game/Aliases/Path2";
AssetData.GetTagValueRef<FString>(UContentBrowserAliasDataSource::AliasTagName);
```

当资产的此标签被修改时，插件会自动调用 `ReconcileAliasesFromMetaData` 增量更新别名。

#### 协调（Reconcile）别名

```cpp
// 从元数据重新协调（自动添加/移除不匹配的别名）
AliasDataSource->ReconcileAliasesFromMetaData(AssetData);

// 手动指定新别名列表进行协调
TArray<FName> NewAliases = { FName("/Game/NewPath/Asset1") };
AliasDataSource->ReconcileAliasesForAsset(AssetData, NewAliases);
```

### 进阶用法

#### 带本地化显示名称的别名

使用 `FContentBrowserLocalizedAlias` 可以为别名指定自定义显示名称：

```cpp
FContentBrowserLocalizedAlias LocalizedAlias;
LocalizedAlias.Alias = FName("/Game/LocalizedAliases/MyAsset");
LocalizedAlias.DisplayName = NSLOCTEXT("MyModule", "AliasName", "我的资产");

AliasDataSource->AddAlias(AssetData, LocalizedAlias);
```

#### 文件夹显示名称

```cpp
// 为别名文件夹设置自定义显示名称
AliasDataSource->AddAliasFolderDisplayName(FName("/Game/MyAliases"), FText::FromString("My Custom Aliases"));

// 移除自定义显示名称
AliasDataSource->RemoveAliasFolderDisplayName(FName("/Game/MyAliases"));
```

#### 监听别名重建

```cpp
AliasDataSource->OnRebuildAliases().AddLambda([]()
{
    // 重新添加你的别名
    UE_LOG(LogTemp, Log, TEXT("Aliases were rebuilt, re-adding custom aliases..."));
    // ... AddAlias calls ...
});

// 触发重建（清除所有别名并广播 OnRebuildAliases）
AliasDataSource->RebuildAliases();
```

#### 调试：在控制台查看所有别名

在编辑器控制台输入：

```
ContentBrowser.LogAliases
```

或在 C++ 中调用：

```cpp
AliasDataSource->LogAliases();
```

## Demo 示例

### 最小示例：为资产创建别名

**MyModule.Build.cs:**

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "ContentBrowserAliasDataSource",
    "ContentBrowserAssetDataSource",
    "ContentBrowserData",
    "AssetRegistry"
});
```

**MyAliasRegistrar.h:**

```cpp
#pragma once

#include "CoreMinimal.h"

class FMyAliasRegistrar
{
public:
    static void RegisterAliases();
};
```

**MyAliasRegistrar.cpp:**

```cpp
#include "MyAliasRegistrar.h"

#include "ContentBrowserAliasDataSource.h"
#include "ContentBrowserAliasDataSourceModule.h"
#include "AssetRegistry/AssetRegistryModule.h"

void FMyAliasRegistrar::RegisterAliases()
{
    FContentBrowserAliasDataSourceModule& Module =
        FModuleManager::Get().LoadModuleChecked<FContentBrowserAliasDataSourceModule>(
            "ContentBrowserAliasDataSource");
    UContentBrowserAliasDataSource* AliasDS = Module.TryGetAliasDataSource();
    if (!AliasDS)
    {
        return;
    }

    // 监听重建事件
    AliasDS->OnRebuildAliases().AddLambda([AliasDS]()
    {
        IAssetRegistry& AR = FModuleManager::LoadModuleChecked<FAssetRegistryModule>("AssetRegistry").Get();

        // 为特定资产添加别名
        TArray<FAssetData> Assets;
        AR.GetAssetsByPackageName(FName("/Game/MyAsset"), Assets);
        for (const FAssetData& Asset : Assets)
        {
            AliasDS->AddAlias(Asset, FName("/Game/CustomView/MyAsset"));
        }
    });

    // 如果需要，手动触发重建
    AliasDS->RebuildAliases();
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AssetRegistry` | 资产注册表，用于查询和监听资产变更 |
| `Core` | UE 核心库 |
| `CoreUObject` | UObject 系统 |
| `ContentBrowserAssetDataSource` | Content Browser 资产数据源基类，此插件的别名功能基于此模块构建 |
| `ContentBrowserData` | Content Browser 数据子系统 |
| `AssetTools` (Private) | 资产编辑/保存/查看等工具操作 |
| `Engine` (Private) | 引擎核心功能 |

**插件依赖：** 此插件显式依赖 `ContentBrowserAssetDataSource` 插件（在 .uplugin 的 Plugins 字段中声明）。

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-08-21 | `b787d80` | Updated to hold ContentBrowserModule pointers instead of using GetModuleChecked for on demand usage | 性能优化：将按需模块查找改为持有指针，减少运行时开销 |
| 2025-08-19 | `916ed52` | Updated navigation bar to use friendly user facing paths; alias/class data source no longer returns internal path as package path | 改善 UX：导航栏显示友好路径而非内部虚拟路径，修复别名路径复制行为 |
| 2025-07-28 | `f918108` | Fixed navigation bar path issues for virtual paths, class paths, and aliased paths | Bug 修复：修复导航栏对虚拟路径、类路径和别名路径的跳转问题 |

### 维护评价

- **创建时间**：2024 年 5 月，不到 2 年历史
- **Beta 状态**：标记为 `IsBetaVersion: true`，`EnabledByDefault: false`
- **活跃度**：最近一次更新在 2025 年 8 月，**活跃维护中**
- **更新模式**：近期更新集中在 Content Browser 导航栏和路径显示的改进上，说明此插件与 Content Browser 的核心导航体验深度集成
- **推荐使用**：✅ 如果你需要 Verse 类或自定义路径在 Content Browser 中显示，这是官方推荐的实现方式。注意它仍处于 Beta 阶段，API 可能在未来版本中变化

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Editor/ContentBrowser/ContentBrowserAliasDataSource)
- [官方文档]()（暂无）
- [测试用例]()（此插件无独立测试文件）
