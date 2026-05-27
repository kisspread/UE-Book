# Directory Placeholder

> Adds a lightweight Directory Placeholder asset type, which can be added to otherwise empty folders in order to add them to source control.

| 属性 | 值 |
|---|---|
| 中文名 | 目录占位符 |
| 分类 | Source Control |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `DirectoryPlaceholder` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-01-29 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/DirectoryPlaceholder) | |

## 用途

`DirectoryPlaceholder` 插件解决了一个版本控制系统（如 Git, Perforce）中的常见问题：**空文件夹无法被提交**。许多版本控制工具只跟踪包含文件的目录，这使得在项目中保留必要的但暂时为空的目录结构变得困难。

该插件通过提供一个**极简的、无实际内容的资产类型**（`UDirectoryPlaceholder`）来解决此问题。用户可以在内容浏览器中右键点击一个空文件夹并创建此资产，或者通过设置让插件在创建文件夹时自动放置。这个占位符资产本身没有任何功能或数据，其唯一目的就是作为一个“标记文件”存在，从而让整个目录（包括父文件夹链）能被源代码管理系统识别和跟踪。它本质上是项目目录结构的“元数据”占位符。

## 使用场景

- 你在维护一个项目，其中包含许多用于未来模块或资产的空文件夹结构（例如，`/Game/Levels/Chapter1/`，`/Game/Characters/Hero/Materials/`），你需要这些路径在版本控制中被保留。
- 你正在开发一个引擎插件或游戏模块，其目录结构非常重要，但某些子文件夹在初始阶段是空的。
- 你在使用 CI/CD 流水线或自动化工具，这些工具依赖于特定的目录结构存在，而版本控制系统必须先能“看到”这些空目录。
- 你需要一个干净的方法来管理项目中的占位文件，避免使用真实的 `.txt` 或 `.gitkeep` 等文件，希望有专门的资产类型和管理工具（如批量清理）。

## 蓝图用法

插件提供了一个蓝图函数库 `UDirectoryPlaceholderLibrary`，用于在编辑器中对占位符资产进行批量操作。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Cleanup Placeholders In Path` | 删除指定路径（及其子文件夹）下所有**不必要**的占位符资产（例如，文件夹内已有其他资产）。 | `UDirectoryPlaceholderLibrary` |
| `Cleanup Placeholders In Paths` | 删除多个指定路径下所有不必要的占位符资产。 | `UDirectoryPlaceholderLibrary` |
| `Delete Placeholders In Path` | 强制删除指定路径（及其子文件夹）下的**所有**占位符资产，无论文件夹是否为空。 | `UDirectoryPlaceholderLibrary` |

### 使用示例（蓝图描述）

1.  **清理项目**：在蓝图编辑器中，你可以创建一个编辑器工具蓝图（Editor Utility Blueprint），拖入 `Cleanup Placeholders In Path` 节点。将 `Path` 参数设置为 `/Game`，即可一键清理整个项目内容目录下所有多余的占位符。
2.  **批量删除**：如果你决定不再使用占位符策略，可以使用 `Delete Placeholders In Path` 节点，输入路径 `/Game` 来清除所有相关资产。
3.  **在事件图表中使用**：你也可以在任何蓝图的函数中调用这些节点，例如在一个定时器事件或自定义编辑器按钮触发时执行清理操作。

## C++ 用法

### 头文件引入

```cpp
#include "DirectoryPlaceholder.h"
#include "DirectoryPlaceholderUtils.h"
```

### 基本用法

在 C++ 中，`UDirectoryPlaceholder` 类本身主要用于资产实例化和工厂创建。作为开发者，你通常不需要直接操作这个类的实例，而是通过编辑器 UI 或蓝图函数库与之交互。但是，理解其存在是关键。

```cpp
// 创建一个 UDirectoryPlaceholder 的实例（通常由工厂自动完成）
UDirectoryPlaceholder* Placeholder = NewObject<UDirectoryPlaceholder>(GetTransientPackage(), UDirectoryPlaceholder::StaticClass());
```

### 进阶用法

使用蓝图函数库中的静态方法进行程序化清理或管理。

```cpp
// 清理指定路径下不必要的占位符
FString ContentPath = TEXT("/Game/MyFolder");
UDirectoryPlaceholderLibrary::CleanupPlaceholdersInPath(ContentPath);

// 强制删除指定路径下的所有占位符
UDirectoryPlaceholderLibrary::DeletePlaceholdersInPath(ContentPath);
```

## Demo 示例

以下是一个最小化的编辑器工具类示例，用于在编辑器菜单中添加一个清理占位符的按钮。

**DirectoryPlaceholderCleanupTool.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "DirectoryPlaceholderCleanupTool.generated.h"

UCLASS()
class UDirectoryPlaceholderCleanupTool : public UObject
{
    GENERATED_BODY()

public:
    // 蓝图可调用的静态函数，用于清理整个项目的占位符
    UFUNCTION(BlueprintCallable, Category = "Tools")
    static void CleanupProjectPlaceholders();
};
```

**DirectoryPlaceholderCleanupTool.cpp**
```cpp
#include "DirectoryPlaceholderCleanupTool.h"
#include "DirectoryPlaceholderUtils.h" // 包含清理函数

void UDirectoryPlaceholderCleanupTool::CleanupProjectPlaceholders()
{
    // 清理 /Game 路径下的所有不必要占位符
    UDirectoryPlaceholderLibrary::CleanupPlaceholdersInPath(TEXT("/Game"));
    
    UE_LOG(LogTemp, Display, TEXT("Project directory placeholders cleaned up."));
}
```

## 模块依赖

从源码结构推断，此插件依赖关系简单。

| 模块 | 用途 |
|---|---|
| `ContentBrowser` | 提供内容浏览器前端过滤器扩展 (`UDirectoryPlaceholderSearchFilter`) 和资产定义接口。 |
| `AssetDefinition` | 提供资产定义基类 (`UAssetDefinitionDefault`)，用于定义资产在编辑器中的显示和行为。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the ... | 调整虚拟制作资产的分类，并可能迁移了相关资产，插件本身未直接修改。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF，是引擎层面的日志系统更新。 |
| 2025-09-29 | `2d2bcf61` | DirectoryPlaceholders: Add support to automatically create placeholders in new folders within additi... | **重要功能更新**：新增了在“附加插件”目录中自动创建占位符的设置项。 |
| 2025-09-12 | `82645780` | DirectoryPlaceholders: Fix issue where placeholder assets could get created in ExternalActors and Ex... | 修复了一个重要 Bug：占位符资产可能错误地创建在 `ExternalActors` 和 `ExternalPackages` 目录下。 |
| 2025-05-16 | `28ae7a11` | DirectoryPlaceholders: Fix crash when trying to save a large number of placeholder assets one at a t... | 修复了当尝试逐一保存大量占位符资产时可能导致的崩溃问题。 |

### 维护评价

该插件创建于 **2025 年初**，至今约有 **1.7 年**历史。从提交记录看，它**仍在活跃维护**中。最近的更新（2025年9月）集中在功能增强和关键 Bug 修复上，解决了资产误创建和批量操作崩溃的问题，表明 Epic 团队正在积极完善它。2026 年的提交主要是跟随引擎整体的技术更新（日志系统）。

鉴于其功能专一、代码轻量（仅10个源文件）、且由 Epic 官方维护并纳入主仓库，**这是一个稳定可靠的工具**。实验性标志（`IsExperimentalVersion: true`）可能意味着其 API 或行为在未来的引擎版本中仍有微调的可能，但核心功能已足够用于生产环境。**强烈推荐**有空目录版本控制需求的项目使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/DirectoryPlaceholder)