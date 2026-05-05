# Asset Search

> 

| 属性 | 值 |
|---|---|
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AssetSearch` (EditorNoCommandlet) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-03-03 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/AssetSearch) | |

## 用途

Asset Search 是 UE5 的**全文搜索索引系统**，为编辑器内的资产提供超越 Asset Registry 标签的深度内容搜索能力。

核心问题：UE 内置的 Content Browser 搜索只能按资产名称、路径、类名等元数据过滤。如果你想搜索"哪个蓝图里调用了 `ApplyDamage` 函数"或"哪个 DataTable 里包含 `Gold` 字符串"，标准搜索无能为力。

Asset Search 的解决方案是：在后台线程中加载每个资产，遍历其内部属性（包括蓝图图表节点、CDO 属性、组件模板、DataTable 行数据、材质表达式参数等），将可索引内容序列化为 JSON，存入 SQLite 数据库。搜索时对数据库执行 LIKE 查询，返回匹配的记录及其上下文（资产名、对象路径、属性名、属性值等）。

系统架构分为三层：
1. **Indexer 层** — 针对不同资产类型（Blueprint、DataTable、Material、Level 等）的专用索引器
2. **Storage 层** — SQLite 数据库 + 文件哈希数据库，支持增量更新
3. **Provider 层** — 搜索提供者，除了 SQLite 索引外还包含 Asset Registry 元数据搜索

## 使用场景

- 你需要在一个大型项目中找到**引用了某个特定函数或变量的蓝图** → Asset Search 会索引蓝图图表中的所有节点，包括 `UK2Node_CallFunction`、`UK2Node_Variable` 等
- 你需要搜索 **DataTable/CurveTable 中的文本数据** → 逐行索引所有行列值
- 你需要找到**使用了某个材质参数的材质资产** → 索引材质表达式图中的节点和参数
- 你需要搜索关卡中**某个特定 Actor 的属性值** → LevelIndexer + ActorIndexer 组合索引
- 你需要搜索 **SoundCue 节点图**或 **DialogueWave 上下文** → 专用索引器支持
- 你有大量资产需要**增量索引**，不想每次启动都全量扫描 → 文件哈希 + DDC 双重缓存机制

## 内置索引器

Asset Search 在启动时注册了以下索引器（见 `FAssetSearchManager::Start()`）：

| 索引器类 | 目标资产类型 | 索引内容 |
|---|---|---|
| `FGenericObjectIndexer` | `UDataAsset` | 所有可索引属性 |
| `FDataTableIndexer` | `UDataTable` | 表格行名和值 |
| `FCurveTableIndexer` | `UCurveTable` | 曲线表行数据 |
| `FBlueprintIndexer` | `UBlueprint` | CDO 属性、组件模板、图表节点（函数调用、变量、事件、注释、Pin 值）、蓝图扩展 |
| `FWidgetBlueprintIndexer` | `UWidgetBlueprint` | UMG Widget 蓝图 |
| `FDialogueWaveIndexer` | `UDialogueWave` | 对话波上下文 |
| `FLevelIndexer` | `UWorld` | 关卡资产，支持嵌套 Actor 索引 |
| `FActorIndexer` | `AActor` | Actor 属性 |
| `FSoundCueIndexer` | `USoundCue` | 声音节点图 |
| `FMaterialExpressionIndexer` | `UMaterial` | 材质表达式节点和参数 |
| `FMaterialExpressionIndexer` | `UMaterialFunction` | 材质函数表达式 |
| `FGenericObjectIndexer` | `UMaterialParameterCollection` | 参数集合属性 |
| `FGenericObjectIndexer` | `UMaterialInstance` | 材质实例属性 |

## 蓝图用法

Asset Search 没有暴露任何 `BlueprintCallable` 函数或 `BlueprintReadWrite` 属性。它是一个纯编辑器工具，通过 Search 面板（`Window → Search`）使用。

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

### 模块检查与访问

```cpp
// 检查模块是否可用
if (IAssetSearchModule::IsAvailable())
{
    IAssetSearchModule& SearchModule = IAssetSearchModule::Get();
    
    // 获取索引统计信息
    FSearchStats Stats = SearchModule.GetStats();
    UE_LOG(LogTemp, Log, TEXT("Total indexed records: %lld"), Stats.TotalRecords);
    UE_LOG(LogTemp, Log, TEXT("Is updating: %d"), Stats.IsUpdating());
}
```

### 执行搜索

```cpp
// 创建搜索查询（线程安全的共享指针）
FSearchQueryPtr Query = MakeShared<FSearchQuery, ESPMode::ThreadSafe>(TEXT("ApplyDamage"));

// 设置结果回调
Query->SetResultsCallback([](TArray<FSearchRecord>&& Results)
{
    for (const FSearchRecord& Record : Results)
    {
        UE_LOG(LogTemp, Log, TEXT("Asset: %s | Object: %s | Property: %s | Value: %s"),
            *Record.AssetName,
            *Record.object_name,
            *Record.property_name,
            *Record.value_text);
    }
});

// 提交搜索
IAssetSearchModule::Get().Search(Query);

// 取消搜索：清除回调即可，查询会自动检测 IsQueryStillImportant()
Query->ClearResultsCallback();
```

### 自定义索引器

```cpp
// 创建自定义资产索引器
class FMyCustomIndexer : public IAssetIndexer
{
public:
    virtual FString GetName() const override { return TEXT("MyCustom"); }
    
    virtual int32 GetVersion() const override { return 1; }
    
    virtual void IndexAsset(const UObject* InAssetObject, FSearchSerializer& Serializer) const override
    {
        // 开始索引对象
        Serializer.BeginIndexingObject(InAssetObject, TEXT("$self"));
        
        // 遍历所有可索引属性
        FIndexerUtilities::IterateIndexableProperties(InAssetObject,
            [&Serializer](const FProperty* Property, const FString& Value)
        {
            Serializer.IndexProperty(Property, Value);
        });
        
        // 索引自定义数据
        if (const UMyAsset* MyAsset = Cast<UMyAsset>(InAssetObject))
        {
            Serializer.IndexProperty(TEXT("CustomField"), MyAsset->SomeTextProperty);
        }
        
        Serializer.EndIndexingObject();
    }
};

// 注册索引器（在模块启动后调用）
IAssetSearchModule::Get().RegisterAssetIndexer(
    UMyAsset::StaticClass(),
    MakeUnique<FMyCustomIndexer>()
);
```

### 自定义搜索提供者

```cpp
class FMySearchProvider : public ISearchProvider
{
public:
    virtual void Search(FSearchQueryPtr SearchQuery) override
    {
        // 实现自定义搜索逻辑
        // 可以搜索非索引数据源
        TArray<FSearchRecord> Results;
        // ... 填充结果 ...
        
        if (FSearchQuery::ResultsCallbackFunction Callback = SearchQuery->GetResultsCallback())
        {
            Callback(MoveTemp(Results));
        }
    }
};

// 注册搜索提供者
IAssetSearchModule::Get().RegisterSearchProvider(
    FName("MyCustomProvider"),
    MakeUnique<FMySearchProvider>()
);
```

### FSearchRecord 结构

搜索结果以 `FSearchRecord` 返回，包含完整的上下文信息：

```cpp
struct FSearchRecord
{
    FString AssetName;          // 资产名称
    FString AssetPath;          // 资产路径
    FTopLevelAssetPath AssetClass; // 资产类路径

    FString object_name;        // 内部对象名称（如 "Class Defaults"、组件名）
    FString object_path;        // 对象路径
    FString object_native_class; // 对象原生类名

    FString property_name;      // 属性显示名称
    FString property_field;     // 属性字段名
    FString property_class;     // 属性类名

    FString value_text;         // 匹配的值（可见）
    FString value_hidden;       // 隐藏的值（如 GUID）

    float Score;                // 匹配分数
};
```

## Demo 示例

### 自定义索引器完整示例

```cpp
// MyAssetIndexer.h
#pragma once

#include "IAssetIndexer.h"

class FMyAssetIndexer : public IAssetIndexer
{
public:
    virtual FString GetName() const override { return TEXT("MyAsset"); }
    virtual int32 GetVersion() const override { return 1; }
    virtual void IndexAsset(const UObject* InAssetObject, FSearchSerializer& Serializer) const override;
};
```

```cpp
// MyAssetIndexer.cpp
#include "MyAssetIndexer.h"
#include "SearchSerializer.h"
#include "Utility/IndexerUtilities.h"
#include "MyGame/MyAsset.h"

void FMyAssetIndexer::IndexAsset(const UObject* InAssetObject, FSearchSerializer& Serializer) const
{
    const UMyAsset* MyAsset = CastChecked<UMyAsset>(InAssetObject);

    // 索引资产自身属性
    Serializer.BeginIndexingObject(MyAsset, TEXT("$self"));
    FIndexerUtilities::IterateIndexableProperties(MyAsset,
        [&Serializer](const FProperty* Property, const FString& Value)
    {
        Serializer.IndexProperty(Property, Value);
    });
    Serializer.EndIndexingObject();
}
```

```cpp
// MyGameModule.cpp - 注册索引器
#include "IAssetSearchModule.h"
#include "MyAssetIndexer.h"

void FMyGameModule::StartupModule()
{
    if (IAssetSearchModule::IsAvailable())
    {
        IAssetSearchModule::Get().RegisterAssetIndexer(
            UMyAsset::StaticClass(),
            MakeUnique<FMyAssetIndexer>()
        );
    }
}
```

**Build.cs 依赖**:

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
    "AssetSearch"  // 需要依赖 AssetSearch 模块
});
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型、字符串、容器 |
| `CoreUObject` | UObject 系统、反射、序列化 |
| `Engine` | 引擎核心类型（DataTable、Material、SoundCue 等） |
| `Json` | JSON 序列化（索引数据格式） |
| `StudioTelemetry` | 遥测数据上报 |
| `SQLiteCore` | SQLite 数据库存储（私有依赖） |
| `AssetRegistry` | 资产注册表，监听资产变更事件 |
| `UnrealEd` | 编辑器框架 |
| `UMG` / `UMGEditor` | Widget 蓝图索引支持 |
| `BlueprintGraph` | 蓝图图表节点索引 |
| `DerivedDataCache` | DDC 存储索引数据（可选） |

## 设置

### 项目设置（Settings → Project Settings → Search）

| 设置 | 说明 |
|---|---|
| Intermediate Storage | 索引中间数据存储方式：`DerivedDataCache`（默认）或 `AssetTagData`（嵌入资产标签） |
| Ignored Paths | 不索引的目录路径列表 |
| Disable DDC | 禁用 DDC 读写操作 |

### 用户设置（Settings → Editor Preferences → Search）

| 设置 | 说明 |
|---|---|
| Enable Search | 启用搜索功能（需要手动开启） |
| Enable Integrity Checks | 启用 SQLite 完整性检查（慢） |
| Ignored Paths | 用户级忽略路径 |
| Show Assets Needing Indexing | 显示需要索引的资产数量 |
| Auto Expand Assets | 自动展开搜索结果中的资产 |
| Throttle In Background | 编辑器在后台时降低索引速率 |
| Default Performance | 前台时的并行下载数、处理速率、扫描速率 |
| Background Performance | 后台时的性能参数 |

## 控制台变量

| CVar | 说明 |
|---|---|
| `Search.ForceEnable` | 强制启用搜索（忽略用户设置） |
| `Search.TryIndexAssetsOnLoad` | 在资产加载时尝试索引 |
| `Search.TryToGCDuringMissingIndexing` | 索引缺失资产时偶尔触发 GC |

## 维护状态

### 近期更新

1. `ce6ff392ddca` | 2025-09-12 | 修复 `FTSTicker::RemoveTicker` 的 `nodiscard` 警告 — 编译警告修复，无功能变更
2. `84880cbcdd0a` | 2025-06-25 | 更新 DLL 导出符号（UnrealCodeFixup） — 构建系统调整
3. `7e59f1578685` | 2025-03-18 | 修复 printf 格式不匹配 — 编译警告修复

### 维护评价

Asset Search 创建于 2020 年 3 月，至今约 6 年。最近 3 次提交（2025 年 3 月-9 月）全部是编译警告修复和构建系统调整，**没有实质性功能更新**。

关键观察：
- `.uplugin` 中 `IsBetaVersion=true`，`EnabledByDefault=false` — 这是一个**未完成的实验性功能**
- 最近 2 年内没有功能性更新（新增索引器、搜索能力改进等）
- 系统架构设计良好（可扩展的索引器/提供者模式、SQLite 存储、DDC 缓存），但缺乏维护投入
- 没有找到对应的测试用例
- `.uplugin` 的 Description 字段为空，官方文档链接也为空

**评价**：这是一个有潜力但被搁置的功能。架构设计合理，支持自定义索引器和搜索提供者扩展，但 Epic 似乎没有继续投入开发。**可以用于学习和内部工具开发**，但不建议作为生产级搜索方案的核心依赖。如果需要类似功能，建议评估是否基于此代码自行维护 fork。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/AssetSearch)
- 官方文档（无）
- 测试用例（无）
