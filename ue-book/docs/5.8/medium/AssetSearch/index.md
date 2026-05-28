# Asset Search

> 

| 属性 | 值 |
|---|---|
| 中文名 | 资产搜索 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AssetSearch` (EditorNoCommandlet) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-03-03 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/AssetSearch) | |

## 用途

AssetSearch 是一个编辑器内资产全文搜索插件，解决了在海量资产中按内容（而非仅按名称）查找信息的问题。它通过可扩展的索引器（Indexer）体系，将 DataTable 行数据、蓝图图表节点文本、材质参数、关卡 Actor 属性等资产内部结构化数据提取并存储到 SQLite 数据库中，从而支持跨资产类型的全文检索。

核心设计理念：
- **可插拔索引**：通过 `IAssetIndexer` 接口注册自定义索引器，每种资产类型独立索引
- **两种中间存储模式**：索引结果可存入 DDC（Derived Data Cache）共享给团队，或存入资产 Tag Data 随资产分发
- **异步后台处理**：资产扫描、索引构建、DDC 下载均在后台线程完成，不阻塞编辑器
- **增量更新**：基于文件哈希判断资产是否需要重新索引，避免重复工作

该插件默认关闭且标记为 Beta，说明 Epic 内部有使用但尚未作为正式功能发布。

## 使用场景

- 你在制作大型项目，有上千个 DataTable，需要找到某个特定值出现在哪张表中 → 用 AssetSearch 全文搜索
- 你想在蓝图图表中搜索某个函数名或注释文本，但不想逐个打开蓝图 → 用 AssetSearch 索引蓝图节点
- 你的团队需要一个项目内资产内容搜索引擎，且希望扩展支持自定义资产类型 → 实现 `IAssetIndexer` 接口注册自定义索引器
- 你需要查找某个材质参数名被哪些材质实例使用 → AssetSearch 会索引材质表达式参数

## 启用方法

该插件默认关闭（`EnabledByDefault: false`），需要手动启用：

1. **插件面板**：Edit → Plugins → 搜索 "Asset Search" → 启用 → 重启编辑器
2. **设置面板**：启用后在 Project Settings → Search 或 Editor Preferences → Search 中打开 `bEnableSearch`

该插件依赖 `SQLiteCore` 插件，会自动启用。

## 蓝图用法

AssetSearch 主要是 C++ 编辑器插件，没有暴露 BlueprintCallable 节点。用户交互通过以下方式：

### 编辑器设置

设置通过 `UDeveloperSettings` 暴露，在编辑器 Settings 面板中可配置：

| 设置类 | 位置 | 说明 |
|---|---|---|
| `USearchProjectSettings` | Project Settings → Search | 项目级设置（存储模式、忽略路径） |
| `USearchUserSettings` | Editor Preferences → Search | 用户级设置（启用搜索、性能参数） |

### 搜索浏览器面板

启用插件后，通过 Window 菜单（或自定义快捷键 `FAssetSearchCommands::ViewAssetSearch`）打开搜索浏览器面板 `SSearchBrowser`，在搜索框中输入关键词即可跨资产全文检索。

## C++ 用法

### 头文件引入

```cpp
#include "IAssetSearchModule.h"
#include "IAssetIndexer.h"
#include "ISearchProvider.h"
#include "SearchQuery.h"
#include "SearchSerializer.h"
#include "Utility/IndexerUtilities.h"
```

### 基本用法 — 执行搜索

```cpp
// 来源: Source/Public/SearchQuery.h + IAssetSearchModule.h

// 1. 创建搜索查询
FSearchQueryPtr Query = MakeShared<FSearchQuery>(TEXT("FireDamage"));

// 2. 设置结果回调（线程安全）
Query->SetResultsCallback([](TArray<FSearchRecord>&& Results)
{
    for (const FSearchRecord& Record : Results)
    {
        UE_LOG(LogTemp, Log, TEXT("Found in asset '%s': %s = %s (score: %.2f)"),
            *Record.AssetName, *Record.property_name, *Record.value_text, Record.Score);
    }
});

// 3. 提交搜索
IAssetSearchModule& SearchModule = IAssetSearchModule::Get();
SearchModule.Search(Query);

// 4. 检查索引进度
FSearchStats Stats = SearchModule.GetStats();
if (Stats.IsUpdating())
{
    UE_LOG(LogTemp, Log, TEXT("Still indexing: %d scanning, %d processing, %d updating"),
        Stats.Scanning, Stats.Processing, Stats.Updating);
}

// 5. 查询完成后可清除回调
Query->ClearResultsCallback();
```

### 自定义资产索引器

```cpp
// 来源: Source/Public/IAssetIndexer.h

class FMyCustomAssetIndexer : public IAssetIndexer
{
public:
    virtual FString GetName() const override { return TEXT("MyCustomAsset"); }
    
    virtual int32 GetVersion() const override { return 1; }

    virtual void IndexAsset(const UObject* InAssetObject, FSearchSerializer& Serializer) const override
    {
        // 开始索引该对象
        Serializer.BeginIndexingObject(InAssetObject, TEXT("My Custom Asset"));

        // 使用工具遍历所有可索引属性
        FIndexerUtilities::IterateIndexableProperties(InAssetObject,
            [&Serializer](const FProperty* Property, const FString& Value)
            {
                Serializer.IndexProperty(Property, Value);
            });

        // 也可以手动索引特定字段
        Serializer.IndexProperty(TEXT("DisplayName"), InAssetObject->GetName());

        Serializer.EndIndexingObject();
    }
};

// 注册索引器
IAssetSearchModule& Module = IAssetSearchModule::Get();
Module.RegisterAssetIndexer(
    UMyCustomAsset::StaticClass(),
    MakeUnique<FMyCustomAssetIndexer>()
);
```

### 自定义搜索提供器

```cpp
// 来源: Source/Public/ISearchProvider.h

class FMySearchProvider : public ISearchProvider
{
public:
    virtual void Search(FSearchQueryPtr SearchQuery) override
    {
        // 在自己的数据源中搜索
        TArray<FSearchRecord> MyResults;
        // ... 执行搜索逻辑 ...

        // 通过回调返回结果
        if (auto Callback = SearchQuery->GetResultsCallback())
        {
            Callback(MoveTemp(MyResults));
        }
    }
};

// 注册搜索提供器
Module.RegisterSearchProvider(
    FName("MyCustomSource"),
    MakeUnique<FMySearchProvider>()
);
```

### 嵌套资产索引

```cpp
// 来源: Source/Public/IAssetIndexer.h + Source/Private/Indexers/LevelIndexer.h

// 索引器可以声明其关注的嵌套资产类型（如蓝图嵌套在关卡中）
virtual void GetNestedAssetTypes(TArray<UClass*>& OutTypes) const override
{
    OutTypes.Add(UBlueprint::StaticClass());
}

// 索引时，使用 Serializer.IndexNestedAsset() 处理嵌套资产
Serializer.IndexNestedAsset(NestedBlueprint);
```

## Demo 示例

```cpp
// MyAssetSearchExtension.h
#pragma once

#include "IAssetIndexer.h"
#include "SearchSerializer.h"

class FWeaponDataIndexer : public IAssetIndexer
{
public:
    virtual FString GetName() const override { return TEXT("WeaponData"); }
    virtual int32 GetVersion() const override { return 1; }
    virtual void IndexAsset(const UObject* InAssetObject, FSearchSerializer& Serializer) const override;
};
```

```cpp
// MyAssetSearchExtension.cpp
#include "MyAssetSearchExtension.h"
#include "IAssetSearchModule.h"
#include "Utility/IndexerUtilities.h"

void FWeaponDataIndexer::IndexAsset(const UObject* InAssetObject, FSearchSerializer& Serializer) const
{
    Serializer.BeginIndexingObject(InAssetObject, TEXT("Weapon Data"));

    // 遍历所有可索引的文本属性（名称、描述、标签等）
    FIndexerUtilities::IterateIndexableProperties(InAssetObject,
        [&Serializer](const FProperty* Property, const FString& Value)
        {
            Serializer.IndexProperty(Property, Value);
        });

    Serializer.EndIndexingObject();
}

// 在编辑器模块启动时注册
void FMyEditorModule::StartupModule()
{
    if (IAssetSearchModule::IsAvailable())
    {
        IAssetSearchModule& SearchModule = IAssetSearchModule::Get();
        SearchModule.RegisterAssetIndexer(
            UWeaponDataTable::StaticClass(),
            MakeUnique<FWeaponDataIndexer>()
        );
    }
}

void FMyEditorModule::ShutdownModule()
{
    // 索引器生命周期由模块管理，无需手动注销
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `SQLiteCore` | SQLite 数据库引擎，存储搜索索引和文件哈希 |
| `AssetRegistry` | 资产注册表，用于资产发现和资产扫描 |
| `DerivedDataCache` | 派生数据缓存，用于存储/下载索引数据（DDC 模式） |
| `Json` | JSON 序列化，索引数据以 JSON 格式存储 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到新的 UE_LOGF 格式 |
| 2026-04-02 | `50a24ff6` | Deprecated GetObjects*/ForEachObjectWithOuter functions that take bool bIncludeNestedObjects. | 适配 UObject 迭代 API 的弃用变更 |
| 2026-03-10 | `a69ab07d` | [IsSavingPackage] | 适配 IsSavingPackage 相关 API 变更 |
| 2025-10-17 | `fbdbd5d3` | Asset Search Manager: Do not reload all packages after each AT. | 修复资产扫描后不再重新加载所有包，提升性能 |

### 维护评价

AssetSearch 插件创建于 2020 年，至今约 5 年。它始终处于 **Beta 状态**（`IsBetaVersion: true`）且**默认未启用**（`EnabledByDefault: false`）。

**积极信号**：
- 最近一次更新在 2026 年 5 月，说明仍在跟随引擎主分支维护
- 有实质性功能修复（如 2025-10-17 的包重新加载优化）
- 架构完整，支持自定义扩展（索引器、搜索提供器）

**风险提示**：
- 始终标记为 Beta，从未升级为正式功能
- 未提供官方文档（DocsURL 为空）
- 近期更新多为编译适配而非功能增强

**推荐程度**：适合需要全文搜索资产内容的团队使用，但需接受其 Beta 状态。对于大型项目中查找 DataTable 数据、蓝图节点等场景非常有价值。不建议作为关键路径依赖，因为 Epic 随时可能修改或移除此插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/AssetSearch)
- [测试用例]（未发现独立测试文件）