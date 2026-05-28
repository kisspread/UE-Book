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

## 用途

大多数版本控制系统（如 Perforce、Git）只追踪文件，不追踪空目录。当你的项目中有需要纳入源码管理的空文件夹时（例如预留的目录结构），这些空目录无法被提交。

Directory Placeholder 插件解决的就是这个问题：它提供了一个极轻量的资产类型 `UDirectoryPlaceholder`（本质上就是一个空的 UObject），你只需在空文件夹中放置一个该资产，文件夹就能被源码管理系统识别和提交。

此外，该插件还支持**自动创建**——当你在 Content Browser 中新建文件夹时，可以在指定路径下自动生成占位符资产，无需手动操作。

## 使用场景

- 你在团队项目中建立了规范的目录结构（如 `/Game/Characters/Weapons/`），其中部分文件夹暂时为空，但需要提交到版本控制
- 你使用 Perforce 管理 UE 项目，Perforce 默认不追踪空目录
- 你需要在项目插件或附加插件中维护目录骨架结构

## 蓝图用法

该插件提供了一个 `UBlueprintFunctionLibrary`，暴露了 3 个静态清理节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CleanupPlaceholdersInPath` | 删除指定路径下所有**不必要的**占位符资产（仅当文件夹内已有其他资产时才删除） | `UDirectoryPlaceholderLibrary` |
| `CleanupPlaceholdersInPaths` | 批量版本：对多个路径执行同样的清理逻辑 | `UDirectoryPlaceholderLibrary` |
| `DeletePlaceholdersInPath` | 删除指定路径下的**所有**占位符资产（不论文件夹是否为空） | `UDirectoryPlaceholderLibrary` |

### 使用示例

**清理单个路径**：在一个宏或函数中，输入 `Cleanup Placeholders In Path` 节点，Path 参数设为 `/Game/MyFolder/`。该节点会递归扫描子目录，仅移除那些同级已有其他资产的占位符（即保留了空目录的占位符）。

**批量清理**：构建一个 `TArray<FString>`，包含所有待清理的路径，传入 `Cleanup Placeholders In Paths`。

**彻底删除**：如果你不再需要某个目录结构被提交，用 `Delete Placeholders In Path` 可以删除路径下所有占位符（即使文件夹会因此变空）。

## C++ 用法

### 头文件引入

```cpp
#include "DirectoryPlaceholderUtils.h"
```

### 基本用法

```cpp
// 清理某个路径下不必要的占位符（保留必要的空目录占位符）
UDirectoryPlaceholderLibrary::CleanupPlaceholdersInPath(TEXT("/Game/MyFolder/"));

// 批量清理多个路径
TArray<FString> PathsToClean = { TEXT("/Game/FolderA/"), TEXT("/Game/FolderB/") };
UDirectoryPlaceholderLibrary::CleanupPlaceholdersInPaths(PathsToClean);

// 彻底删除某个路径下所有占位符
UDirectoryPlaceholderLibrary::DeletePlaceholdersInPath(TEXT("/Game/TempFolder/"));
```

### 进阶用法：通过设置控制自动创建

```cpp
#include "DirectoryPlaceholderSettings.h"

// 获取设置对象（通过 GetMutableDefault）
UDirectoryPlaceholderSettings* Settings = GetMutableDefault<UDirectoryPlaceholderSettings>();

// 禁用自动创建
Settings->bAutomaticallyCreatePlaceholders = false;
Settings->TryUpdateDefaultConfigFile();

// 排除特定路径
Settings->ExcludePaths.Add(TEXT("/Game/Temp/"));
Settings->TryUpdateDefaultConfigFile();
```

设置项说明：

| 设置 | 默认值 | 说明 |
|---|---|---|
| `bAutomaticallyCreatePlaceholders` | `true` | 是否在新建文件夹时自动生成占位符 |
| `bAutomaticallyCreatePlaceholdersInProjectContent` | `true` | 在项目 Content 目录下自动创建 |
| `bAutomaticallyCreatePlaceholdersInProjectPlugins` | `true` | 在项目插件目录下自动创建 |
| `bAutomaticallyCreatePlaceholdersInAdditionalPlugins` | `true` | 在附加插件目录下自动创建 |
| `ExcludePaths` | 空 | 排除路径列表（Content Browser 格式） |

## Demo 示例

```cpp
// MyDirectoryManager.h
#pragma once
#include "CoreMinimal.h"

class FMyDirectoryManager
{
public:
    /** 初始化项目目录结构并确保占位符存在 */
    static void EnsureProjectDirectories(const FString& BasePath);
    
    /** 项目完成资产导入后，清理多余的占位符 */
    static void CleanupAfterImport(const TArray<FString>& ImportedPaths);
};
```

```cpp
// MyDirectoryManager.cpp
#include "MyDirectoryManager.h"
#include "DirectoryPlaceholderUtils.h"
#include "HAL/FileManager.h"

void FMyDirectoryManager::EnsureProjectDirectories(const FString& BasePath)
{
    // 创建目录结构
    TArray<FString> Directories = {
        TEXT("Characters"),
        TEXT("Characters/Weapons"),
        TEXT("UI"),
        TEXT("Maps")
    };

    for (const FString& Dir : Directories)
    {
        const FString FullPath = FPaths::Combine(BasePath, Dir);
        IFileManager::Get().MakeDirectory(*FullPath, true);
    }

    // 如果启用了自动创建，占位符会自动生成
    // 否则需要手动创建 UDirectoryPlaceholder 资产
}

void FMyDirectoryManager::CleanupAfterImport(const TArray<FString>& ImportedPaths)
{
    // 导入资产后，清理那些已不需要占位符的目录
    UDirectoryPlaceholderLibrary::CleanupPlaceholdersInPaths(ImportedPaths);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ContentBrowser` | Content Browser 前端过滤器扩展（隐藏/显示占位符资产） |
| `AssetDefinition` | UE5 资产定义系统（自定义资产显示名称、颜色、分类） |
| `DeveloperSettings` | 项目级设置面板支持 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the ... | VP 资产分类迁移（非本插件核心改动） |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移到新格式 UE_LOGF |
| 2025-09-29 | `2d2bcf61` | DirectoryPlaceholders: Add support to automatically create placeholders in new folders within additi... | 新增附加插件目录下自动创建占位符的支持 |
| 2025-09-12 | `82645780` | DirectoryPlaceholders: Fix issue where placeholder assets could get created in ExternalActors and Ex... | 修复占位符可能错误创建在 ExternalActors 目录中的问题 |
| 2025-05-16 | `28ae7a11` | DirectoryPlaceholders: Fix crash when trying to save a large number of placeholder assets one at a t... | 修复批量保存大量占位符资产时的崩溃问题 |

### 维护评价

该插件于 2025-01-29 创建，至今约 1 年，仍处于**实验性**阶段（`IsExperimentalVersion=true`，`Installed=false`）。从 git 历史来看，2025 年有多次实质性功能更新和 bug 修复，2026 年的更新主要是日志宏迁移等维护性改动。

插件功能简洁明确，代码量小（10 个源文件），维护负担低。作为 Epic 官方开发工具链的一部分，虽然标记为实验性，但已从 VP Shots 插件中独立出来成为通用工具，说明有一定的使用基础。

**⚠️ 注意**：该插件标记为实验性且默认未安装，生产环境中使用需谨慎。建议仅在内部开发流程中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/DirectoryPlaceholder)
- [官方文档]()（无）