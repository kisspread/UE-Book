# Semantic Search

> Very early work in progress of a semantic search system for assets（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SemanticSearch` (Editor), `SemanticSearchEditorIntegrations` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-10 |
| 年龄标签 | 🆕（约 -1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SemanticSearch) | |

## 用途

该插件旨在为虚幻引擎资产系统提供基于语义的搜索功能。传统的资产搜索依赖于精确的标签、命名或路径，而语义搜索的目标是理解资产的自然语言描述（例如“一个破旧的木箱”、“科幻风格的UI元素”），并找到语义上最匹配的资产。这能极大提升在大型项目中查找特定风格或功能资产的效率。目前插件处于非常早期的实验阶段。

## 使用场景

- 你的项目拥有庞大的资产库，美术或设计师需要快速找到符合特定“感觉”或“描述”的资产（例如：“找到所有看起来很古老的石头材质”）。
- 你希望为资产添加更丰富的自然语言描述，并基于这些描述进行智能检索。
- 你正在探索将AI或向量搜索技术集成到引擎的资产管理工作流中。

## 蓝图用法

该插件主要提供编辑器集成和对话框，蓝图可调用的公开接口较少。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Open` | 以独立窗口形式打开语义搜索索引管理对话框。 | `SSemanticSearchIndexDialog` |
| `RegisterContentBrowserExtension` | 注册内容浏览器的语义搜索扩展。 | `UE::SemanticSearch::ContentBrowser` |
| `UnregisterContentBrowserExtension` | 注销内容浏览器的语义搜索扩展。 | `UE::SemanticSearch::ContentBrowser` |

### 使用示例（蓝图描述）

1.  **打开索引对话框**：在编辑器工具蓝图中，调用 `SSemanticSearchIndexDialog::Open` 节点，即可弹出一个管理语义搜索索引的窗口，用于查看索引状态、触发重建等。
2.  **集成到内容浏览器**：在插件或编辑器模块的初始化阶段，调用 `RegisterContentBrowserExtension` 节点，这会在内容浏览器中添加与语义搜索相关的UI元素或右键菜单选项。

## C++ 用法

### 头文件引入

```cpp
#include "ISemanticSearchModule.h"
#include "ContentBrowser/SemanticSearchCB.h"
```

### 基本用法

从头文件分析，该模块的核心是管理语义搜索索引并与编辑器集成。

```cpp
// 来源: Public/ContentBrowser/SemanticSearchCB.h
// 在编辑器模块启动时注册内容浏览器扩展
void FMyEditorModule::StartupModule()
{
    UE::SemanticSearch::ContentBrowser::RegisterContentBrowserExtension();
}

void FMyEditorModule::ShutdownModule()
{
    UE::SemanticSearch::ContentBrowser::UnregisterContentBrowserExtension();
}
```

### 进阶用法

直接操作索引对话框，例如在自定义的编辑器面板中嵌入或触发索引操作。

```cpp
// 来源: Private/Widgets/SSemanticSearchIndexDialog.h
// 在某个编辑器命令或按钮的回调中打开索引对话框
void FMyEditorCommands::OnOpenSemanticSearchIndexDialog()
{
    UE::SemanticSearch::SSemanticSearchIndexDialog::Open();
}
```

## Demo 示例

一个最小化的编辑器模块示例，展示如何集成语义搜索的内容浏览器扩展。

```cpp
// MySemanticSearchEditorModule.h
#pragma once
#include "Modules/ModuleManager.h"

class FMySemanticSearchEditorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

```cpp
// MySemanticSearchEditorModule.cpp
#include "MySemanticSearchEditorModule.h"
#include "ContentBrowser/SemanticSearchCB.h"

void FMySemanticSearchEditorModule::StartupModule()
{
    // 注册语义搜索在内容浏览器中的扩展
    UE::SemanticSearch::ContentBrowser::RegisterContentBrowserExtension();
}

void FMySemanticSearchEditorModule::ShutdownModule()
{
    // 注销扩展
    UE::SemanticSearch::ContentBrowser::UnregisterContentBrowserExtension();
}

IMPLEMENT_MODULE(FMySemanticSearchEditorModule, MySemanticSearchEditor)
```

## 模块依赖

由于未提供 `SemanticSearchEditorIntegrations.Build.cs` 的具体内容，无法列出精确的依赖。但根据其功能（集成内容浏览器）和命名，可以推断其很可能依赖以下模块：

| 模块 | 用途 |
|---|---|
| `SemanticSearch` | 核心语义搜索逻辑模块 |
| `ContentBrowser` | 用于在内容浏览器中添加扩展点 |
| `WorkspaceMenuStructure` | 可能用于注册编辑器菜单或面板 |

## 维护状态

### 近期更新

（由于未提供 git log 信息，无法列出具体 commit。基于创建时间 2026-04-10 判断，这是一个非常新的插件。）

### 维护评价

- **创建时间**：2026-04-10，非常新。
- **维护状态**：作为标记为 `IsExperimentalVersion: true` 且 `EnabledByDefault: false` 的插件，它处于早期实验阶段。功能、API 和集成方式可能会发生重大变化。
- **推荐使用**：**不推荐**在生产项目中使用。仅适用于对引擎前沿功能进行研究、原型开发或内部工具实验的开发者。使用时需做好API不稳定、功能不完善的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SemanticSearch)
- [官方文档]()（暂无）
- [测试用例]()（未在提供的信息中发现）