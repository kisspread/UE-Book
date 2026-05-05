# Content Browser - Asset Data Source

> Data Source plugin providing Asset Data to the Content Browser

| 属性 | 值 |
|---|---|
| 分类 | Content Browser |
| 默认启用 | true |
| 包含内容 | false |
| 模块 | ContentBrowserAssetDataSource (Editor) |
| 创建时间 | 2020-06-10 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/ContentBrowser/ContentBrowserAssetDataSource) | |

## 用途

这个 plugin 是 UE5 Content Browser 架构的核心数据后端之一。它实现了 `UContentBrowserDataSource` 接口，将 **Asset Registry**（资产注册表）中的数据桥接到 Content Browser 的统一虚拟文件系统中。

简单来说：Content Browser 显示的所有 `.uasset` 文件夹和资产，都是通过这个 data source 插件从 Asset Registry 翻译过来的。它负责：

- **监听 Asset Registry 事件**（资产增删改重命名、路径变化），实时同步 Content Browser 的显示
- **编译过滤器**：将 Content Browser 的 UI 筛选条件（类型、路径、集合等）编译成 Asset Registry 的 `FARFilter`
- **枚举资产和文件夹**：按过滤器查询并返回 Content Browser 可展示的 `FContentBrowserItemData`
- **CRUD 操作**：创建文件夹、创建/复制/移动/重命名/删除资产
- **右键菜单集成**：注入资产文件夹和资产文件的上下文菜单
- **处理不支持的资产**：当资产类型没有注册 `AssetDefinition` 时，显示为 unsupported 类型

## 使用场景

- **普通开发者**：你不需要直接使用这个 plugin，它在编辑器启动时自动工作。当你在 Content Browser 中浏览、搜索、筛选资产时，幕后就是这个 plugin 在提供数据。
- **自定义 Content Browser 数据源**：如果你要为 Content Browser 实现新的数据源（如虚拟资产、远程资产），可以参考这个 plugin 的实现模式。它继承 `UContentBrowserDataSource` 并实现了所有必需的虚函数。
- **扩展 Content Browser 行为**：理解这个 plugin 的工作方式有助于你扩展 Content Browser 的过滤器、菜单和资产操作。
- **LiveLinkHub 支持**：此 plugin 也支持 LiveLinkHub 程序（`SupportedPrograms: ["LiveLinkHub"]`）。

## 蓝图用法

此 plugin **不提供 BlueprintCallable 接口**。它是纯 C++ 编辑器基础设施，所有 API 都是 C++ 层面的。

## C++ 用法

### 核心架构

整个 plugin 由三层构成：

```
UContentBrowserAssetDataSource          ← 数据源主类，继承 UContentBrowserDataSource
  ├── ContentBrowserAssetData 命名空间  ← 工具函数层（CRUD、属性查询等）
  └── Payload 类                        ← 数据载体（Folder/File/Unsupported）
```

### 头文件引入

```cpp
#include "ContentBrowserAssetDataSource.h"  // 主数据源类
#include "ContentBrowserAssetDataCore.h"    // 工具函数命名空间
#include "ContentBrowserAssetDataPayload.h" // Payload 类定义
```

### 基本用法：创建和初始化数据源

数据源在模块启动时自动创建并初始化（来自 `ContentBrowserAssetDataSourceModule.cpp`）：

```cpp
// 模块启动时自动执行（无需手动调用）
UContentBrowserAssetDataSource* DataSource = NewObject<UContentBrowserAssetDataSource>(
    GetTransientPackage(), "AssetData");
DataSource->Initialize();  // 监听 Asset Registry、注册菜单扩展
```

`Initialize()` 内部会：
1. 获取 `IAssetRegistry`、`IAssetTools`、`FContentBrowserModule` 的引用
2. 绑定 Asset Registry 的 `OnAssetsAdded`、`OnAssetRemoved`、`OnAssetRenamed` 等委托
3. 绑定 `OnObjectPropertyChanged`、`OnObjectPreSave` 等对象生命周期委托
4. 注册 Content Browser 的右键菜单动态段（AddNew、ToolBar、FolderContext、AssetContext、DragDropContext）
5. 枚举所有已缓存路径和资产，建立初始的文件夹属性和 trie 加速结构

### 进阶用法：自定义 Content Browser 数据源

如果你要实现自己的 data source，`UContentBrowserAssetDataSource` 提供了可复用的静态工具函数：

```cpp
// 在你的 CompileFilter() 实现中使用
UContentBrowserAssetDataSource::FAssetFilterInputParams Params;
bool bCanDisplay = UContentBrowserAssetDataSource::PopulateAssetFilterInputParams(
    Params, this, AssetRegistry, InFilter, OutCompiledFilter);

if (bCanDisplay)
{
    // 构建路径过滤器
    UContentBrowserAssetDataSource::CreatePathFilter(
        Params, InPath, InFilter, OutCompiledFilter,
        [this](FName Path, TFunctionRef<bool(FName)> Callback, bool bRecursive) {
            // 提供子路径枚举逻辑
            SubPathEnumeration(Path, Callback, bRecursive);
        });

    // 构建资产过滤器
    UContentBrowserAssetDataSource::CreateAssetFilter(
        Params, InPath, InFilter, OutCompiledFilter);
}
```

枚举文件夹时：

```cpp
UContentBrowserAssetDataSource::EnumerateFoldersMatchingFilter(
    this,
    AssetDataFilter,
    InSink,
    SubPathEnumerationFunc,
    CreateFolderItemFunc);
```

检查单个文件夹是否通过过滤器：

```cpp
bool bPasses = UContentBrowserAssetDataSource::DoesItemPassFolderFilter(
    this, InItem, *AssetDataFilter);
```

### 进阶用法：工具函数（ContentBrowserAssetData 命名空间）

```cpp
using namespace ContentBrowserAssetData;

// 创建项目
FContentBrowserItemData FolderItem = CreateAssetFolderItem(DataSource, VirtualPath, InternalPath);
FContentBrowserItemData FileItem = CreateAssetFileItem(DataSource, VirtualPath, InternalPath, AssetData);
FContentBrowserItemData UnsupportedItem = CreateUnsupportedAssetFileItem(DataSource, VirtualPath, InternalPath, AssetData);

// 获取 Payload
auto FolderPayload = GetAssetFolderItemPayload(DataSource, Item);
auto FilePayload = GetAssetFileItemPayload(DataSource, Item);

// 批量枚举 Payload
EnumerateAssetItemPayloads(DataSource, Items,
    [](const TSharedRef<const FContentBrowserAssetFolderItemDataPayload>& Folder) { /* 处理文件夹 */ return true; },
    [](const TSharedRef<const FContentBrowserAssetFileItemDataPayload>& File) { /* 处理文件 */ return true; });

// 权限检查
FText ErrorMsg;
bool bCanModify = CanModifyItem(AssetTools, DataSource, Item, &ErrorMsg);
bool bCanEdit = CanEditItem(AssetTools, DataSource, Item, &ErrorMsg);
bool bCanDelete = CanDeleteItem(ContentBrowserModule, AssetTools, AssetRegistry, DataSource, Item, &ErrorMsg);

// CRUD 操作
bool bRenamed = RenameItem(AssetTools, AssetRegistry, DataSource, Item, "NewName");
bool bMoved = MoveItems(AssetTools, DataSource, Items, DestPath);
bool bCopied = CopyItems(AssetTools, DataSource, Items, DestPath);
bool bDeleted = DeleteItems(ContentBrowserModule, AssetTools, AssetRegistry, DataSource, Items);

// 属性查询
FContentBrowserItemDataAttributeValue AttrValue;
bool bHasAttr = GetItemAttribute(ContentBrowserModule, DataSource, Item, true, "AttributeKey", AttrValue);
```

### 进阶用法：Payload 类

Payload 是 ContentBrowserItemData 携带的实际数据载体：

| 类 | 说明 | 关键方法 |
|---|---|---|
| `FContentBrowserAssetFolderItemDataPayload` | 文件夹项 | `GetInternalPath()`, `GetFilename()` |
| `FContentBrowserAssetFileItemDataPayload` | 资产文件项 | `GetAssetData()`, `GetPackage()`, `LoadPackage()`, `GetAsset()`, `LoadAsset()`, `GetAssetTypeActions()`, `GetAssetDefinition()`, `UpdateThumbnail()` |
| `FContentBrowserAssetFileItemDataPayload_Creation` | 正在创建中的资产 | 继承 FilePayload + `GetAssetClass()`, `GetFactory()` |
| `FContentBrowserAssetFileItemDataPayload_Duplication` | 正在复制中的资产 | 继承 FilePayload + `GetSourceObject()` |
| `FContentBrowserUnsupportedAssetFileItemDataPayload` | 不支持的资产类型 | `GetAssetDataIfAvailable()`, `GetFilename()`, `GetPackage()` |

### 控制台变量

| CVar | 默认值 | 说明 |
|---|---|---|
| `AssetDataSource.AllowInternalParallelism` | `1` | 设为 `0` 可禁用数据源内部的并行处理（出现线程问题时使用） |
| `AssetDataSource.OptimizeEnumerateInMemoryAssets` | `1` | 设为 `1` 时仅对新建/脏资产刷新数据；`0` 时对所有已加载资产刷新 |

## Demo 示例

### 自定义数据源骨架

这是一个自定义 Content Browser 数据源的最小骨架，展示如何利用 `UContentBrowserAssetDataSource` 的静态工具函数：

```cpp
// MyDataSource.h
#pragma once
#include "ContentBrowserDataSource.h"
#include "ContentBrowserAssetDataSource.h"
#include "MyDataSource.generated.h"

UCLASS()
class UMyDataSource : public UContentBrowserDataSource
{
    GENERATED_BODY()
public:
    void Initialize(bool bAutoRegister = true);
    virtual void Shutdown() override;

    virtual void CompileFilter(const FName InPath, const FContentBrowserDataFilter& InFilter,
        FContentBrowserDataCompiledFilter& OutCompiledFilter) override
    {
        UContentBrowserAssetDataSource::FAssetFilterInputParams Params;
        if (!UContentBrowserAssetDataSource::PopulateAssetFilterInputParams(
                Params, this, AssetRegistry, InFilter, OutCompiledFilter))
        {
            return;
        }

        UContentBrowserAssetDataSource::CreatePathFilter(
            Params, InPath, InFilter, OutCompiledFilter,
            [this](FName Path, TFunctionRef<bool(FName)> Callback, bool bRecursive) {
                // 你的子路径枚举逻辑
            });

        UContentBrowserAssetDataSource::CreateAssetFilter(
            Params, InPath, InFilter, OutCompiledFilter);
    }

    // ... 实现其他虚函数
};
```

```cpp
// MyDataSource.Build.cs
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
    "ContentBrowserData",
    "ContentBrowserAssetDataSource",  // 依赖此模块
});
```

## 模块依赖

### Public 依赖（你的模块也需要这些）

| 模块 | 用途 |
|---|---|
| `Core` | UE 基础库 |
| `CoreUObject` | UObject 系统 |
| `ContentBrowserData` | Content Browser 数据抽象层（`UContentBrowserDataSource`、`FContentBrowserItemData` 等） |

### Public Include Path（头文件可用，无需链接）

| 模块 | 用途 |
|---|---|
| `AssetRegistry` | 资产注册表接口（`IAssetRegistry`、`FAssetData`、`FARFilter`） |

### Private 依赖（此 plugin 内部使用）

| 模块 | 用途 |
|---|---|
| `AssetDefinition` | 资产类型定义（`UAssetDefinition`） |
| `AssetTools` | 资产操作工具（`IAssetTools`） |
| `CollectionManager` | 集合管理 |
| `ContentBrowser` | Content Browser 模块（菜单、UI） |
| `Engine` | 引擎核心 |
| `UnrealEd` | 编辑器框架 |
| `ToolMenus` | 菜单系统 |
| `SourceControl` | 源码控制集成 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-10-01 | `413346fe` | Added Asset Context filtering to the Tagged Asset Browser. CreateAsset window will use the "last save directory" path as context. | 功能更新：为 Tagged Asset Browser 添加资产上下文过滤，改善创建资产时的默认路径 |
| 2025-09-04 | `8218a798` | Exposed FullyLoadPackages/FullyLoadAssets functions to editor scripting via EditorLoadingAndSavingUtils | 功能更新：将包加载函数暴露给编辑器脚本 |
| 2025-09-02 | `f28b34d1` | The asset view will now display, filter and sort by Verse paths, object paths or package paths in the path column | 功能更新：资产视图支持 Verse 路径的显示、过滤和排序 |

### 维护评价

- **创建时间**：2020-06-10（~5.9 年）
- **活跃度**：最近一次更新在 2025 年 10 月，属于**活跃维护**状态
- **更新类型**：近期更新都是功能性改进（Verse 路径支持、资产上下文过滤），说明仍在持续迭代
- **稳定性**：作为 Content Browser 的核心基础设施，已运行 5+ 年，接口成熟稳定
- **已知限制**：`SupportedPrograms` 仅限 `LiveLinkHub`，意味着此模块只在编辑器和 LiveLinkHub 中加载，不会在运行时游戏或纯命令行工具中加载
- **推荐**：**推荐使用**。如果你需要扩展 Content Browser 的数据源能力，这是最佳参考实现。但注意这是 Epic 内部基础设施代码，通常不需要直接修改或替换。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/ContentBrowser/ContentBrowserAssetDataSource)
- 官方文档：无（`.uplugin` 中 DocsURL 为空）
- 测试用例：未找到独立测试文件（此 plugin 作为 Content Browser 基础设施，测试覆盖在 ContentBrowser 相关测试中）
