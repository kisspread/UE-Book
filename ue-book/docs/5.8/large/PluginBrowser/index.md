# Plugin Browser

> User interface for managing installed plugins and creating new ones.

| 属性 | 值 |
|---|---|
| 中文名 | 插件浏览器 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `PluginBrowser` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2015-04-25 |
| 年龄标签 | 🏛️ 文物（约 11 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/PluginBrowser) | |

## 用途

Plugin Browser 是虚幻编辑器的核心编辑器工具，提供了一个图形化界面，用于集中管理引擎和项目中的所有插件。其主要功能包括：
1.  **浏览与搜索**：以分类树的形式展示所有已安装的插件，支持按名称、类别或状态（如已启用/已禁用、工程/引擎插件）进行筛选和搜索。
2.  **启用与禁用**：允许用户在编辑器内直接启用或禁用任何插件，无需手动编辑 `.uplugin` 文件或重启编辑器。
3.  **创建新插件**：集成了一套插件创建向导，引导用户从多种预设模板（如空白、蓝图库、编辑器模式等）快速生成一个新的、结构完整的插件项目框架。
4.  **查看插件信息**：显示每个插件的详细信息，包括描述、作者、依赖关系、包含的模块和资产等。

它解决了在复杂项目中管理大量插件不便、以及从头创建插件结构繁琐的问题，是虚幻引擎插件开发和管理的一站式入口。

## 使用场景

- 你正在开发一个大型项目，安装了数十个第三方或自研插件，需要快速查找、启用或禁用某个功能 → **使用插件浏览器的搜索和过滤功能**。
- 你需要为项目创建一个全新的自定义插件，并希望包含标准的目录结构和基础代码 → **使用插件创建向导选择合适的模板**。
- 你收到了一个新的插件包，想查看其具体内容（如蓝图资产、C++模块）和依赖关系 → **在插件浏览器中查看详情**。

## 蓝图用法

此插件主要为编辑器界面工具，其核心功能通过编辑器菜单（`Edit -> Plugins`）访问，并不向运行时游戏蓝图暴露通用的 `BlueprintCallable` 函数。其API主要用于编辑器扩展和工具开发。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| 无通用运行时节点 | 此插件为编辑器工具，不提供运行时蓝图API | - |

### 使用示例（蓝图描述）

不适用。用户通过虚幻编辑器菜单栏的“编辑(Edits)” -> “插件(Plugins)”来调用此插件的完整功能界面。

## C++ 用法

Plugin Browser 本身主要是一个编辑器UI模块。对于其他编辑器模块或工具，通常通过其提供的服务或直接引用其头文件来与其交互，或者在创建新插件时参考其生成的模板结构。

### 头文件引入

```cpp
// 访问插件浏览器提供的服务或类型（如有需要）
#include "IPluginBrowser.h"
```

### 基本用法

通常，开发者在创建新插件时，会直接使用由 Plugin Browser 生成的模板代码。例如，一个由其“Advanced”模板生成的插件模块头文件可能如下所示（结构由插件浏览器向导定义）：

```cpp
// 源自 Template/Advanced 模板生成的示例
// 文件路径: Templates/Advanced/Source/PLUGIN_NAME/PluginName.h
#pragma once

#include "Modules/ModuleManager.h"

class FMyPluginModule : public IModuleInterface
{
public:
    /** 模块启动时调用 */
    virtual void StartupModule() override;
    /** 模块关闭时调用 */
    virtual void ShutdownModule() override;
};
```

### 进阶用法

更复杂的用法通常涉及扩展插件浏览器本身或自动化插件创建流程。这需要深入理解 `FPluginBrowserModule` 和 `SPluginBrowser` 等内部类。对于大多数用户，主要通过向导交互，无需直接编写此级别的代码。

## Demo 示例

一个从 Plugin Browser 的 “Blank” 模板生成的、可编译的最小插件框架结构：

**MyBlankPlugin.h**
```cpp
#pragma once

#include "Modules/ModuleManager.h"

class FMyBlankPluginModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

**MyBlankPlugin.cpp**
```cpp
#include "MyBlankPlugin.h"

#define LOCTEXT_NAMESPACE "FMyBlankPluginModule"

void FMyBlankPluginModule::StartupModule()
{
    // 在此处添加模块启动逻辑
}

void FMyBlankPluginModule::ShutdownModule()
{
    // 在此处添加模块关闭逻辑
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyBlankPluginModule, MyBlankPlugin)
```

（注：`Build.cs` 文件由模板自动生成，定义了基本的模块类型和依赖，详见模块依赖章节。）

## 模块依赖

使用或扩展 Plugin Browser 功能的模块，除了标准的 Core/Engine/Slate 等，通常需要依赖以下特殊模块：

| 模块 | 用途 |
|---|---|
| `PluginUtils` | 提供插件管理、发现和操作的底层工具函数，是 Plugin Browser 的后端支撑。 |
| `WorkspaceMenuStructure` | 提供编辑器“工作区”菜单的结构，用于将“插件”菜单项正确地注册到编辑器菜单栏。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了严格浮点模式下双精度常量截断为浮点数导致的编译警告。 |
| 2026-05-12 | `d93da640` | Added new PluginToolset AI Toolset for managing plugins. | 新增了用于管理插件的 AI 工具集（PluginToolset）。 |
| 2026-04-08 | `d6aa71b0` | function rename | 对函数进行了重命名（内部重构）。 |
| 2026-04-08 | `612e6b9b` | Fixup plugin wizard to check for the actual name of the plugin we’ll create rather than the name the | 修复插件创建向导，使其检查将要创建的插件的实际名称，而非输入的临时名称。 |
| 2026-03-16 | `e20d084a` | Add a way to sort plugins by names to simplify merging: | 新增了按名称排序插件的功能，以简化版本管理合并。 |

### 维护评价

- **创建时间**：创建于 2015 年，是历史悠久的“文物”级插件。
- **更新频率**：尽管已存在 11 年，但至今仍在进行积极的功能更新和 Bug 修复（如近期的 AI 工具集、向导优化和编译修复）。
- **维护状态**：**活跃维护中**。作为编辑器核心功能组件，由 Epic Games 和社区持续维护。
- **推荐程度**：**强烈推荐**。这是管理虚幻引擎插件的标准和必备工具，没有替代品。其持续的更新保证了与最新引擎版本的兼容性和功能的演进。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/PluginBrowser)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/Editor/PluginBrowser) (路径假设，通常测试代码位于此结构下)