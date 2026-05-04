# Asset Manager Editor

> Editor UI and utilities for managing and auditing Assets on disk

| 属性 | 值 |
|---|---|
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AssetManagerEditor` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2017-03-22 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/AssetManagerEditor) | |

## 用途

AssetManagerEditor 是 UE5 编辑器中资产管理和审计的核心工具插件。它解决的核心问题是：**当项目规模增长后，如何可视化地理解资产之间的依赖关系、分析资产磁盘占用、审计资产属性？**

该插件提供了三个主要的编辑器工具窗口：

1. **Reference Viewer（引用查看器）**：以图形节点的方式可视化展示资产之间的依赖关系图（谁引用了谁、谁被谁依赖），支持深度/广度限制、软/硬引用过滤、集合过滤、插件过滤、查找路径等功能。
2. **Size Map（大小地图）**：以 TreeMap 可视化方式展示资产及其依赖的磁盘/内存占用，帮助开发者识别"最重"的资产。
3. **Asset Audit（资产审计）**：以表格形式展示资产的详细管理信息，包括 ResourceSize、DiskSize、CookRule、Chunk 分配、插件归属等。

此外，该插件还提供了：
- `FPrimaryAssetType` 和 `FPrimaryAssetId` 的属性自定义编辑器（Details 面板中的下拉选择器）
- 蓝图图钉（Graph Pin）自定义 UI
- 资产右键上下文菜单扩展（View References、View Size Map、Asset Audit 等）
- 源代码管理（Source Control）上下文菜单集成
- 控制台命令用于脚本化资产审计

## 使用场景

- 你想知道某个资产被哪些其他资产引用，或者它依赖了哪些资产 → 右键资产 → **View References**，打开 Reference Viewer
- 你想分析某个资产及其所有依赖占用了多少磁盘空间 → 右键资产 → **View Size Map**，打开 Size Map
- 你想批量审查一组资产的 Cook 规则、Chunk 分配、Primary Asset 信息 → **Asset Audit** 窗口
- 你想找出从资产 A 到资产 B 之间的依赖链路 → Reference Viewer 中的 **Find Path** 功能
- 你想在蓝图中使用 `FPrimaryAssetId` 或 `FPrimaryAssetType` 类型的变量 → 该插件提供自定义下拉选择器
- 你想通过控制台命令批量导出资产依赖信息 → `AssetManager.DumpAssetDependencies`

## 蓝图用法

该插件不暴露 `BlueprintCallable` 函数。它是一个纯编辑器工具插件，其功能通过编辑器 UI 和 C++ API 提供。

不过，它为蓝图中的 `FPrimaryAssetType` 和 `FPrimaryAssetId` 类型变量提供了自定义的属性编辑器（Property Customization）：

| 属性类型 | 自定义 UI | 说明 |
|---|---|---|
| `FPrimaryAssetType` | 下拉选择器 | 从 AssetManager 注册的所有 Primary Asset 类型中选择 |
| `FPrimaryAssetId` | 资产选择器 | 带缩略图的资产拾取器，按类型过滤 |

## C++ 用法

### 头文件引入

```cpp
#include "AssetManagerEditorModule.h"
```

### 基本用法 — 打开 Reference Viewer

```cpp
// 通过模块接口打开引用查看器
IAssetManagerEditorModule& EditorModule = IAssetManagerEditorModule::Get();

TArray<FAssetIdentifier> Identifiers;
Identifiers.Add(FAssetIdentifier("/Game/MyAsset"));

// 使用默认参数打开（显示 referencers 和 dependencies）
EditorModule.OpenReferenceViewerUI(Identifiers);
```

来源：`IAssetManagerEditorModule::OpenReferenceViewerUI()`

### 基本用法 — 打开 Asset Audit

```cpp
IAssetManagerEditorModule& EditorModule = IAssetManagerEditorModule::Get();

TArray<FAssetData> SelectedAssets;
// ... 从 AssetRegistry 获取资产数据
EditorModule.OpenAssetAuditUI(SelectedAssets);
```

来源：`IAssetManagerEditorModule::OpenAssetAuditUI()`

### 基本用法 — 打开 Size Map

```cpp
IAssetManagerEditorModule& EditorModule = IAssetManagerEditorModule::Get();

TArray<FAssetIdentifier> Identifiers;
Identifiers.Add(FAssetIdentifier("/Game/Characters/Hero"));
EditorModule.OpenSizeMapUI(Identifiers);
```

来源：`IAssetManagerEditorModule::OpenSizeMapUI()`

### 获取自定义列的值

该插件为 Content Browser 等列表视图提供了自定义列（ResourceSize、DiskSize、ManagedResourceSize 等）：

```cpp
IAssetManagerEditorModule& EditorModule = IAssetManagerEditorModule::Get();

FString Value;
bool bFound = EditorModule.GetStringValueForCustomColumn(
    AssetData, IAssetManagerEditorModule::DiskSizeName, Value);

int64 IntValue;
bool bFoundInt = EditorModule.GetIntegerValueForCustomColumn(
    AssetData, IAssetManagerEditorModule::ResourceSizeName, IntValue);
```

### 创建假的 AssetData（用于 Primary Asset 和 Chunk）

```cpp
// 从 Chunk ID 创建假的 FAssetData，用于在 UI 中表示 Chunk
FAssetData FakeChunkData = IAssetManagerEditorModule::CreateFakeAssetDataFromChunkId(0);

// 从 PrimaryAssetId 创建假的 FAssetData
FPrimaryAssetId AssetId("MyPrimaryAssetType", "MyAssetName");
FAssetData FakeAssetData = IAssetManagerEditorModule::CreateFakeAssetDataFromPrimaryAssetId(AssetId);

// 反向提取
int32 ChunkId = IAssetManagerEditorModule::ExtractChunkIdFromFakeAssetData(FakeChunkData);
FPrimaryAssetId ExtractedId = IAssetManagerEditorModule::ExtractPrimaryAssetIdFromFakeAssetData(FakeAssetData);
```

### Registry Source 管理

该插件支持从不同来源加载 AssetRegistry 数据（编辑器实时数据、目标平台 Cook 后的数据、或自定义路径）：

```cpp
IAssetManagerEditorModule& EditorModule = IAssetManagerEditorModule::Get();

// 获取当前 Registry Source
const FAssetManagerEditorRegistrySource* CurrentSource = EditorModule.GetCurrentRegistrySource(true);

// 切换到目标平台数据
EditorModule.SetCurrentRegistrySource("Windows");  // 目标平台名

// 切换到自定义路径（会弹出文件选择对话框）
EditorModule.SetCurrentRegistrySource(FAssetManagerEditorRegistrySource::CustomSourceName);

// 获取所有可用的 Registry Sources
TArray<const FAssetManagerEditorRegistrySource*> Sources;
EditorModule.GetAvailableRegistrySources(Sources);
```

### 进阶用法 — 写入集合（Collection）

将一组资产写入 Content Browser 的集合，便于分组管理：

```cpp
IAssetManagerEditorModule& EditorModule = IAssetManagerEditorModule::Get();

TArray<FName> PackageNames;
PackageNames.Add("/Game/Characters/Hero/Mesh");
PackageNames.Add("/Game/Characters/Hero/Material");

// 写入本地集合
EditorModule.WriteCollection(
    FName("MyCharacterAssets"),
    ECollectionShareType::CST_Local,
    PackageNames,
    true  // 显示反馈
);
```

### 进阶用法 — 过滤 AssetIdentifier 列表

根据当前 Registry Source 过滤资产标识符列表，移除不存在的资产：

```cpp
TArray<FAssetIdentifier> Identifiers;
// ... 填充标识符

FAssetManagerDependencyQuery Query;
Query.Categories = UE::AssetRegistry::EDependencyCategory::All;

bool bAnyRemaining = EditorModule.FilterAssetIdentifiersForCurrentRegistrySource(
    Identifiers, Query, true /* bForwardDependency */);
```

## 控制台命令

该插件注册了以下控制台命令（仅在编辑器中可用）：

| 命令 | 说明 |
|---|---|
| `AssetManager.AssetAudit` | 将资产统计信息转储到日志 |
| `AssetManager.FindDepChain <TargetPath> <SearchPath> [-hardonly/-softonly]` | 查找从搜索路径到目标包的所有依赖链 |
| `AssetManager.FindDepClasses <PackagePath> <ClassName1> [ClassName2...]` | 查找指定类名的依赖资产 |
| `AssetManager.DumpAssetRegistry <Mode>` | 打印 AssetRegistry 条目（需编译启用 `ASSET_REGISTRY_STATE_DUMPING_ENABLED`） |
| `AssetManager.DumpAssetDependencies` | 列出所有 Primary Assets 及其依赖的 Secondary Assets，并输出 .graphviz 文件 |

## Demo 示例

### 最小示例 — 注册自定义 Reference Viewer 命令

```cpp
// MyModule.Build.cs
PublicDependencyModuleNames.AddRange(new string[] {
    "AssetManagerEditor"
});
```

```cpp
// MyModule.cpp
#include "AssetManagerEditorModule.h"

void FMyModule::StartupModule()
{
    if (IAssetManagerEditorModule::IsAvailable())
    {
        IAssetManagerEditorModule& EditorModule = IAssetManagerEditorModule::Get();

        // 注册额外的 Reference Viewer 上下文菜单命令
        EditorModule.OnRegisterAdditionalReferenceViewerCommands().AddLambda(
            [this](TSharedRef<FUICommandList> CmdList, TArray<TSharedPtr<FUICommandInfo>>& CmdInfos)
            {
                // 添加自定义命令到 Reference Viewer 的右键菜单
            }
        );
    }
}
```

### 示例 — 自定义 Primary Asset Id 选择器

```cpp
// 创建一个不绑定 PropertyHandle 的 PrimaryAssetId 选择器
TSharedRef<SWidget> Picker = IAssetManagerEditorModule::MakePrimaryAssetIdSelector(
    FOnGetPrimaryAssetDisplayText::CreateLambda([]() -> FText {
        return FText::FromString(TEXT("Select Asset..."));
    }),
    FOnSetPrimaryAssetId::CreateLambda([](FPrimaryAssetId NewId) {
        UE_LOG(LogTemp, Log, TEXT("Selected: %s"), *NewId.ToString());
    }),
    true,  // bAllowClear
    TArray<FPrimaryAssetType>(),      // AllowedTypes (empty = all)
    TArray<const UClass*>(),          // AllowedClasses
    TArray<const UClass*>()           // DisallowedClasses
);
```

## 模块依赖

### PublicDependencyModuleNames（使用者需引用）

| 模块 | 用途 |
|---|---|
| `Core` | 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心（AssetManager、AssetRegistry 等） |
| `TargetPlatform` | 目标平台接口（用于加载平台 AssetRegistry） |

### PrivateDependencyModuleNames（插件内部依赖）

| 模块 | 用途 |
|---|---|
| `Slate` / `SlateCore` | UI 框架 |
| `UnrealEd` | 编辑器框架 |
| `AssetRegistry` | 资产注册表查询 |
| `ContentBrowser` / `ContentBrowserData` / `ContentBrowserAssetDataSource` | 内容浏览器集成 |
| `PropertyEditor` | 属性自定义（FPrimaryAssetType/Id 的下拉 UI） |
| `GraphEditor` | Reference Viewer 的图形编辑器 |
| `BlueprintGraph` / `KismetCompiler` | 蓝图图钉自定义 |
| `CollectionManager` | 集合管理（用于过滤和写入集合） |
| `AssetTools` / `AssetDefinition` | 资产工具扩展 |
| `SourceControl` / `SourceControlWindows` | 源代码管理集成 |
| `ToolMenus` | 工具菜单扩展 |
| `TreeMap` | Size Map 的 TreeMap 可视化 |
| `CookMetadata` | Cook 元数据读取（Asset Disk Size 视图） |
| `TraceInsightsCore` | Insights 表格视图基础设施 |

## 维护状态

### 近期更新

1. **2025-08-20** `d5085b6e` — 改进文件中已存在的 "master" 和 "slave" 字符串的不可接受词汇检查
   - 解读：代码规范维护，将旧术语替换为更包容的替代词（如 master→main）

2. **2025-08-11** `17ffeee3` — 从 StartupModule() 加载 SourceControl 模块，确保其生命周期长于本模块
   - 解读：Bug 修复，解决了模块卸载顺序可能导致的崩溃问题

3. **2025-07-23** `9f54b4f0` — 跟踪字符串表键引用作为可搜索名称
   - 解读：功能增强，Reference Viewer 现在能追踪 String Table Key 类型的引用关系

### 维护评价

- **创建时间**：2017 年，是 UE 的老牌编辑器工具
- **最近更新**：2025 年 8 月，持续有维护更新（编译修复、Bug 修复、功能增强）
- **维护状态**：**活跃维护中** — 作为 UE 编辑器核心工具链的一部分，Epic 持续投入
- **模块类型**：UncookedOnly（仅编辑器，不参与打包），LoadingPhase 为 PreDefault
- **推荐程度**：✅ **强烈推荐** — 这是 UE 编辑器内置的资产管理工具，无需额外安装，直接可用。理解这个插件对大型项目的资产优化至关重要

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/AssetManagerEditor)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/AssetManagerEditor) — 该插件无独立测试文件，功能通过编辑器自动化测试覆盖
