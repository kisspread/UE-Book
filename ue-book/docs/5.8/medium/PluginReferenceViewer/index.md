# Plugin Reference Viewer

> Editor plugin for viewing plugin references.

| 属性 | 值 |
|---|---|
| 中文名 | 插件引用查看器 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PluginReferenceViewer` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-06-09 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PluginReferenceViewer) | |

## 用途

Plugin Reference Viewer 是一个专为 UE5 项目设计的编辑器工具，用于**可视化插件之间的依赖关系**。

在大型项目中，插件之间常常存在复杂的依赖网络。当需要排查插件冲突、优化项目结构或理解现有架构时，手动梳理这些关系既困难又容易出错。该插件通过图形化的方式（类似蓝图节点图）展示指定插件所依赖或被哪些插件依赖，帮助开发者快速理解插件间的耦合程度、发现不必要的依赖、并支持导出详细的依赖报告。

## 使用场景

- **架构优化**：当你想要清理项目，移除不必要的插件依赖时，可以使用它来查看插件A依赖了哪些其他插件，以及哪些插件依赖于插件A。
- **问题排查**：当某个插件出现加载错误或性能问题时，使用它检查该插件的依赖链，快速定位问题来源。
- **团队协作**：在新成员加入项目时，通过该工具快速了解项目插件架构的整体依赖关系。
- **项目迁移**：在将项目模块化或迁移到新架构前，分析现有插件的依赖情况，制定合理的重构策略。

## 蓝图用法

此插件主要通过编辑器界面交互，没有直接暴露给游戏逻辑的蓝图函数。其核心用法是通过编辑器菜单启动。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `OpenPluginReferenceViewerUI` | 打开插件引用查看器并聚焦于指定插件 | `FPluginReferenceViewerModule` |

### 使用示例（蓝图描述）

1.  **通过插件浏览器打开**：
    -   打开编辑器主菜单 -> `编辑 (Edit)` -> `插件 (Plugins)`，打开插件浏览器。
    -   在插件列表中找到目标插件，其所在的“插件磁贴”上会有一个“引用查看器 (Reference Viewer)”超链接，点击即可打开以该插件为根的依赖关系图。

2.  **通过控制台命令或自定义UI打开**：
    -   由于这是一个编辑器模块，可以在编辑器工具栏或菜单中添加一个按钮。
    -   按钮的点击事件中，调用 `FPluginReferenceViewerModule::Get().OpenPluginReferenceViewerUI(InPlugin)` 来启动查看器。`InPlugin` 是你希望查看的 `IPlugin` 对象引用。

## C++ 用法

该插件主要作为编辑器工具使用，但提供了一组用于查询和导出插件依赖关系的静态工具函数。

### 头文件引入

```cpp
#include "PluginReferenceViewerUtils.h"
```

### 基本用法

以下示例展示了如何查询特定插件的资产依赖。

```cpp
// 假设我们有一个指向目标插件的引用
TSharedRef<IPlugin> MyPlugin = IPluginManager::Get().FindPlugin(TEXT("MyPlugin"));
if (MyPlugin.IsValid())
{
    // 获取该插件所有资产的依赖关系图
    TMap<FAssetIdentifier, TArray<FAssetIdentifier>> DependencyMap =
        FPluginReferenceViewerUtils::GetAssetDependencyMap(MyPlugin);

    // 或者仅获取该插件的资产所依赖的其他资产列表（扁平化）
    TArray<FAssetIdentifier> AllDependencies =
        FPluginReferenceViewerUtils::GetAssetDependencies(MyPlugin);

    UE_LOG(LogTemp, Log, TEXT("MyPlugin has %d direct asset dependencies."), AllDependencies.Num());
}
```

### 进阶用法

组合使用多个函数来分析和导出详细的插件依赖报告。

```cpp
// 1. 分析两个插件之间的具体资产引用
TSharedRef<IPlugin> PluginA = IPluginManager::Get().FindPlugin(TEXT("PluginA"));
TSharedRef<IPlugin> PluginB = IPluginManager::Get().FindPlugin(TEXT("PluginB"));
FPluginIdentifier PluginAId(PluginA);
FPluginIdentifier PluginBId(PluginB);

TArray<FAssetIdentifier> AssetsFromAToB;
// 注意：此函数需要一个完整的 EdGraph 上下文，通常在查看器内部使用。直接使用较为复杂。

// 2. 将依赖关系按所属插件分组（更实用）
TArray<FAssetIdentifier> DependenciesOfPluginA =
    FPluginReferenceViewerUtils::GetAssetDependencies(PluginA);

TMap<FString, TArray<FAssetIdentifier>> DependenciesGroupedByPlugin =
    FPluginReferenceViewerUtils::SplitByPlugins(PluginA, DependenciesOfPluginA);

for (const auto& Pair : DependenciesGroupedByPlugin)
{
    UE_LOG(LogTemp, Log, TEXT("PluginA depends on Plugin '%s' via %d assets."), *Pair.Key, Pair.Value.Num());
}

// 3. 导出整个插件的依赖关系到 CSV 文件，便于外部分析
FString OutputPath = FPaths::ProjectSavedDir() / TEXT("PluginDependencyReport.csv");
FPluginReferenceViewerUtils::ExportPlugins({ TEXT("PluginA") }, OutputPath);
```

## Demo 示例

以下是一个编辑器实用工具类，用于在编辑器按钮点击时打开插件引用查看器。

```cpp
// MyEditorUtils.h
#pragma once

class FMyEditorUtils
{
public:
    /** 打开指定插件的引用查看器 */
    static void OpenPluginDependencyViewer(const FString& PluginName);
};

// MyEditorUtils.cpp
#include "MyEditorUtils.h"
#include "PluginReferenceViewerModule.h"
#include "PluginDescriptor.h"
#include "IPluginManager.h"

void FMyEditorUtils::OpenPluginDependencyViewer(const FString& PluginName)
{
    TSharedPtr<IPlugin> Plugin = IPluginManager::Get().FindPlugin(PluginName);
    if (Plugin.IsValid())
    {
        FPluginReferenceViewerModule::Get().OpenPluginReferenceViewerUI(Plugin.ToSharedRef());
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Could not find plugin: %s"), *PluginName);
    }
}
```

## 模块依赖

从 `PluginReferenceViewer.Build.cs` 和 `.uplugin` 分析，使用该插件无需为你的模块添加额外依赖，因为它本身是一个完整的编辑器工具插件。但如果你希望在自己的编辑器工具中调用其功能函数（如 `FPluginReferenceViewerUtils`），你的模块需要依赖 `PluginReferenceViewer`。

| 模块 | 用途 |
|---|---|
| `AssetManagerEditor` | 提供资产依赖查询和缓存的基础设施 |
| `PluginUtils` | 提供插件枚举、信息查询等通用工具函数 |
| `PluginBrowser` | 集成到插件浏览器的UI，提供“引用查看器”超链接入口 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下双精度常量截断为浮点数导致的警告。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF。 |
| 2026-02-25 | `c0dd9731` | StringBuilder: Removing construction of TStringBuilderBase<T> | 移除了 TStringBuilderBase<T> 的构造，优化代码。 |
| 2026-02-04 | `74e75dba` | Expose AssetTableTreeView as part of context menu in PluginReferenceViewer to make it easier to find | 在引用查看器的上下文菜单中新增资产表树视图，便于查找。 |
| 2026-02-04 | `80b637db` | Fixed printf format specifiers. | 修复了 printf 格式说明符。 |

### 维护评价

Plugin Reference Viewer 是一个相对较新的实验性插件，创建于 2023 年。从 git 历史看，其最近（2026年初至年中）有多次更新，包括功能增强（如集成资产表视图）和代码质量改进（日志、浮点警告修复），表明它**仍在活跃维护中**，但主要围绕稳定性和小功能迭代。

**优点**：
- 解决了分析插件间复杂依赖关系的痛点。
- 提供了直观的图形化界面和实用的导出功能。

**限制与注意事项**：
- **实验性状态**：标记为 `IsBetaVersion` 和 `IsExperimental`，且默认未启用。这意味着其API或功能在后续版本中可能发生不兼容的变更。
- **编辑器专用**：所有功能都运行在编辑器中，不能用于运行时游戏逻辑。
- **复杂依赖**：对于超大型项目，生成的依赖图可能非常庞大，需要一定的手动筛选和解读。

**推荐**：如果你在开发一个包含众多自定义插件的中大型UE5项目，此插件对于项目管理和架构分析**值得尝试**。但应意识到其实验性，并在升级引擎版本时注意检查兼容性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PluginReferenceViewer)
- [官方文档]( ) （暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PluginReferenceViewer/Tests) （插件目录下通常包含Tests文件夹）