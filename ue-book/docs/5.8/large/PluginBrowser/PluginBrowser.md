# Plugin Browser

> User interface for managing installed plugins and creating new ones.

| 属性 | 值 |
|---|---|
| 中文名 | 插件浏览器 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（插件模板） |
| 模块 | `PluginBrowser` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2015-04-25 |
| 年龄标签 | 👴 老古董（约 11 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/PluginBrowser) | |

## 用途

这个插件为 Unreal Engine 编辑器提供了核心的插件管理界面。它的存在是为了解决以下问题：

1.  **插件管理**：在编辑器中以图形化界面浏览、搜索、启用或禁用项目和引擎中的所有插件。它取代了手动编辑配置文件的方式。
2.  **插件创建**：通过向导式界面，引导用户从预定义的模板创建新的插件。用户可以选择插件类型（如空、基础、高级、编辑器模式、第三方库等），填写元数据，并自动生成完整的插件结构和代码框架。
3.  **插件编辑**：允许用户直接编辑已安装插件的 `.uplugin` 描述文件，管理其依赖、版本等元数据。
4.  **目录管理**：提供界面来管理额外的插件目录（来自项目、用户、命令行或环境变量）。

## 使用场景

- 你需要为项目安装或启用一个第三方插件（如市场下载的插件），在编辑器中搜索并勾选即可。
- 你的团队需要一个自定义的编辑器工具模块，可以通过 `Tools -> New Plugin` 从模板快速创建。
- 你正在开发一个插件，需要更新其版本、描述或依赖关系，可以通过插件浏览器直接编辑其 `.uplugin` 文件。
- 你需要检查哪些插件被启用、哪些有更新，或者查看插件之间的依赖关系。
- 你的项目需要使用位于非标准目录的插件，可以通过插件浏览器配置外部插件路径。

## 蓝图用法

该插件主要是编辑器界面和工具，不提供直接面向游戏运行时（Runtime）的蓝图节点。其核心功能通过编辑器的菜单、选项卡和按钮来触发。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `OnNewPluginCreated` | 当一个新插件被成功创建后广播的委托 | `FPluginBrowserModule` |
| `RegisterPluginTemplate` | 注册一个自定义的插件模板到创建向导中 | `FPluginBrowserModule` |
| `RegisterPluginEditorExtension` | 注册一个扩展，用于自定义插件编辑对话框 | `FPluginBrowserModule` |

### 使用示例（蓝图描述）

由于该插件的功能主要通过编辑器UI交互，没有典型的蓝图使用示例。其主要的交互入口是编辑器菜单栏的 **“编辑” -> “插件”** 以及 **“工具” -> “新建插件”**。

## C++ 用法

该插件的公共接口 `IPluginBrowser` 允许其他模块（如项目自定义的编辑器模块）与插件浏览器交互，例如注册自定义插件模板或扩展插件编辑器。

### 头文件引入

```cpp
#include "IPluginBrowser.h"
```

### 基本用法

以下示例展示了如何从其他模块访问插件浏览器并注册一个自定义插件模板。此代码可在项目的Editor模块中运行。

*来源文件路径：Private/PluginBrowserModule.h*

```cpp
// 确保PluginBrowser模块已加载
if (IPluginBrowser::IsAvailable())
{
    IPluginBrowser& PluginBrowser = IPluginBrowser::Get();

    // 创建一个自定义的插件模板描述
    TSharedRef<FPluginTemplateDescription> MyTemplate = MakeShared<FPluginTemplateDescription>(
        TEXT("MyCustomTemplate"), // 内部名称
        NSLOCTEXT("MyPlugin", "TemplateDesc", "A custom template for my specific needs."),
        // ... 其他参数如图标路径等
        );

    // 注册模板，使其出现在“新建插件”向导中
    PluginBrowser.RegisterPluginTemplate(MyTemplate);
}
```

### 进阶用法

注册一个插件编辑扩展，以便在编辑任何插件时，在属性面板中添加自定义的属性或按钮。

*来源文件路径：Private/PluginBrowserModule.h, Public/IPluginBrowser.h*

```cpp
// 定义一个扩展函数，当插件被编辑时调用
FOnPluginBeingEdited MyExtensionDelegate;
MyExtensionDelegate.BindLambda([](TSharedRef<IPlugin> Plugin, UPluginMetadataObject& MetadataObject)
{
    // 在这里可以向 MetadataObject 添加自定义的 UPROPERTY 字段，
    // 或者对现有属性进行过滤、验证等。
    // 这些修改会反映在插件编辑器的 Details 面板中。
});

// 注册扩展并获取一个句柄，以便后续移除
FPluginEditorExtensionHandle Handle = PluginBrowser.RegisterPluginEditorExtension(MyExtensionDelegate);

// 当不再需要时，取消注册
PluginBrowser.UnregisterPluginEditorExtension(Handle);
```

## Demo 示例

由于这是一个纯编辑器插件，且核心功能是UI，因此没有独立的、可编译的运行时示例。典型的使用方式就是在编辑器中操作其UI，或者在您自己的编辑器模块中调用其公共API（如上C++用法所示）。

## 模块依赖

从 `PluginBrowser.Build.cs` 的依赖关系中提取。要使用 `IPluginBrowser` 接口，您的模块（通常是 Editor 模块）需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `PluginUtils` | 提供插件工具函数，是 `PluginBrowser` 的直接依赖 |
| `PluginBrowser` | 本插件模块，提供 `IPluginBrowser` 接口 |

此外，您自己的模块在 `Build.cs` 中需要添加对 `PluginBrowser` 的依赖。例如：
```csharp
PublicDependencyModuleNames.AddRange(new string[] { "PluginBrowser" });
```

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点数产生的警告。 |
| 2026-05-12 | `d93da640` | Added new PluginToolset AI Toolset for managing plugins. | 新增用于管理插件的 PluginToolset AI 工具集。 |
| 2026-04-08 | `d6aa71b0` | function rename | 函数重命名。 |
| 2026-04-08 | `612e6b9b` | Fixup plugin wizard to check for the actual name of the plugin we'll create rather than the name the user typed. | 修复插件创建向导，使其检查实际将创建的插件名称，而非用户输入的名称。 |
| 2026-03-16 | `e20d084a` | Add a way to sort plugins by names to simplify merging: | 添加按名称排序插件的功能以简化合并。 |

### 维护评价

- **创建时间**：2015年，是UE4时代就存在的老插件。
- **近期更新**：在2026年有多次提交，包括功能添加（AI工具集）、bug修复（名称检查、编译警告）和改进（排序）。这表明它仍在被**积极维护和更新**，以适应新版本引擎和开发需求。
- **状态**：作为编辑器核心功能的一部分，它不太可能被废弃。最新更新显示其功能仍在扩展。
- **推荐使用**：**强烈推荐使用**。这是管理UE项目插件的官方和标准方式，功能完善且持续更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/PluginBrowser)
- 官方文档：未提供
- 测试用例：未在插件目录内发现明显测试文件。