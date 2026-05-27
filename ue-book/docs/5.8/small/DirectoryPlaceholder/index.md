# Directory Placeholder

> Adds a lightweight Directory Placeholder asset type, which can be added to otherwise empty folders in order to add them to source control.

| 属性 | 值 |
|---|---|
| 中文名 | 目录占位符 |
| 分类 | Source Control |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DirectoryPlaceholder` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-01-29 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/DirectoryPlaceholder) | |

**模块类型勘误**：`.uplugin` 中模块类型标记为 `Runtime`，但根据其依赖编辑器功能（如内容浏览器过滤器）及代码分析，应为 `Editor` 类型模块。文档以实际功能为准。

## 用途

这个插件的核心是解决**版本控制系统无法追踪空文件夹**的问题。在游戏开发中，有时需要保留一些空的文件夹结构（用于规划未来的内容），但诸如 Git、Perforce 等源代码管理系统默认不会包含空目录。

`DirectoryPlaceholder` 插件提供了一种轻量级的资产类型 `UDirectoryPlaceholder`，它的文件极小且不包含任何数据。只需将这个资产放入空文件夹中，该文件夹就能被版本控制系统识别和跟踪。此外，插件还提供了自动化工具，可以批量管理这些占位符资产。

## 使用场景

- 你的项目使用 Git 或 Perforce 进行源代码控制。
- 你在项目目录中创建了一些“空”的文件夹（例如 `Characters/Enemies/Bosses/`），用于规划未来的内容模块。
- 你希望这些空文件夹的结构能够被提交到版本库中，以确保团队成员拉取代码后目录结构完整。
- 你需要工具来清理或管理项目中已经不再需要这些占位符的文件夹。

## 蓝图用法

插件通过 `UDirectoryPlaceholderLibrary` 提供了三个核心的蓝图函数，用于管理占位符资产。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CleanupPlaceholdersInPath` | 清理指定路径及其子路径下**所有不再必要**的占位符资产（即，当文件夹内有其它资产时，占位符就会被视为不必要）。 | `UDirectoryPlaceholderLibrary` |
| `CleanupPlaceholdersInPaths` | 清理多个指定路径及其子路径下所有不再必要的占位符资产。 | `UDirectoryPlaceholderLibrary` |
| `DeletePlaceholdersInPath` | **强制删除**指定路径及其子路径下的**所有**占位符资产，无论其是否必要。 | `UDirectoryPlaceholderLibrary` |

### 使用示例（蓝图描述）

1.  **清理一个文件夹**：
    - 从内容浏览器拖入一个 `Folder` 引用（或使用 `Make Literal String` 节点输入路径，如 `/Game/MyEmptyFolder/`）。
    - 连接到 `CleanupPlaceholdersInPath` 节点的 `Path` 引脚。
    - 执行该节点，插件会自动检查该路径，如果文件夹内有了其他资产（如纹理、网格体），则删除多余的占位符。

2.  **批量清理多个文件夹**：
    - 使用 `Make Array` 节点创建一个字符串数组，包含多个文件夹路径。
    - 将该数组连接到 `CleanupPlaceholdersInPaths` 节点的 `Paths` 引脚。
    - 执行该节点，即可一次性清理所有指定文件夹中的不必要占位符。

## C++ 用法

### 头文件引入

```cpp
#include "DirectoryPlaceholder.h" // 核心资产类
#include "DirectoryPlaceholderUtils.h" // 工具函数
```

### 基本用法

创建一个自定义的目录占位符资产。

```cpp
// 来源: Engine/Plugins/Developer/DirectoryPlaceholder/Source/DirectoryPlaceholder/Public/DirectoryPlaceholder.h
// 直接使用插件提供的类
UDirectoryPlaceholder* Placeholder = NewObject<UDirectoryPlaceholder>();
// 通常你会在编辑器工具或工厂类中通过 Asset Tools 创建它，而不是直接 NewObject。
```

### 进阶用法（编辑器工具开发）

如果你正在编写一个编辑器工具，需要根据项目路径创建目录占位符，可以参考插件内部的工厂逻辑。

```cpp
// 灵感来源: Engine/Plugins/Developer/DirectoryPlaceholder/Source/DirectoryPlaceholder/Private/DirectoryPlaceholderFactory.h
#include "AssetToolsModule.h"
#include "DirectoryPlaceholder.h"

void CreatePlaceholderInFolder(const FString& FolderPath)
{
    IAssetTools& AssetTools = FModuleManager::LoadModuleChecked<FAssetToolsModule>("AssetTools").Get();
    // 创建一个“新建资产”操作，类为 UDirectoryPlaceholder
    TArray<UObject*> NewAssets = AssetTools.CreateAssetsWithDialog(
        TEXT("Placeholder"),
        FPackageName::GetLongPackagePath(FolderPath),
        UDirectoryPlaceholder::StaticClass()
    );

    if (NewAssets.Num() > 0)
    {
        // 创建成功，保存新资产
        TArray<UPackage*> PackagesToSave;
        for (UObject* Asset : NewAssets)
        {
            PackagesToSave.Add(Asset->GetPackage());
        }
        AssetTools.SavePackages(PackagesToSave);
    }
}
```

## Demo 示例

一个最小的、演示如何创建自定义目录占位符资产的 C++ 类。

```cpp
// MyDirectoryPlaceholder.h
#pragma once

#include "CoreMinimal.h"
#include "DirectoryPlaceholder.h"
#include "MyDirectoryPlaceholder.generated.h"

/**
 * 一个自定义的目录占位符资产示例，可以添加额外元数据。
 */
UCLASS()
class MYPROJECT_API UMyDirectoryPlaceholder : public UDirectoryPlaceholder
{
    GENERATED_BODY()

public:
    /** 可选：在此处添加你想存储的元数据，例如创建原因 */
    UPROPERTY(EditAnywhere, Category = "Metadata")
    FString Reason;
};
```

```cpp
// MyDirectoryPlaceholder.cpp
#include "MyDirectoryPlaceholder.h"
// 此文件为空，UCLASS 宏和 GENERATED_BODY() 已完成所有必要工作。
```

## 模块依赖

要使用此插件提供的功能，你的模块需要依赖以下编辑器模块：

| 模块 | 用途 |
|---|---|
| `ContentBrowserFilters` | 为内容浏览器提供过滤功能（用于隐藏/显示占位符资产） |
| `AssetDefinition` | 定义资产在编辑器中的显示和操作方式 |
| `DeveloperSettings` | 用于读取和存储插件的项目级设置 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the ... | 整理了虚拟生产相关的资产分类，可能涉及占位符资产的组织方式调整。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移至新的格式，属于代码质量改进。 |
| 2025-09-29 | `2d2bcf61` | DirectoryPlaceholders: Add support to automatically create placeholders in new folders within additi... | **功能新增**：支持在额外的插件目录中自动创建占位符。 |
| 2025-09-12 | `82645780` | DirectoryPlaceholders: Fix issue where placeholder assets could get created in ExternalActors and Ex... | **Bug修复**：修复了占位符资产可能错误创建在 ExternalActors 等不应存在的目录中的问题。 |
| 2025-05-16 | `28ae7a11` | DirectoryPlaceholders: Fix crash when trying to save a large number of placeholder assets one at a t... | **Bug修复**：修复了尝试一次性保存大量占位符资产时可能发生崩溃的问题。 |

### 维护评价

- **状态**：**活跃维护中**。虽然插件本身创建时间不长（约1年），但自创建以来有持续的、实质性的功能更新和Bug修复。
- **实验性**：该插件被标记为 `IsExperimentalVersion: true`，这意味着其 API 或功能在未来版本中可能发生改变，不建议在生产环境中作为核心依赖。
- **推荐**：**推荐试用**。这是一个解决实际痛点（版本控制空目录）的轻量级工具，代码简单，且由 Epic Games 开发维护，质量有保障。非常适合在开发过程中使用以提高工作流效率。鉴于其实验性状态，请关注版本更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/DirectoryPlaceholder)
- [官方文档]() (暂无)
- [测试用例]() (插件自身无测试用例，其功能通过编辑器UI进行测试)