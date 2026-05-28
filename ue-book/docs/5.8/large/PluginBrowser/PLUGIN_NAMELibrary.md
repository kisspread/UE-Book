# Plugin Browser

> User interface for managing installed plugins and creating new ones.

| 属性 | 值 |
|---|---|
| 中文名 | 插件浏览器 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（插件模板：Basic、Advanced、Blank、BlueprintLibrary、EditorMode、ThirdPartyLibrary） |
| 模块 | `PluginBrowser` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2015-04-25 |
| 年龄标签 | 🏛️ 文物（约 10 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/PluginBrowser) | |

## 用途

Plugin Browser 是 UE 编辑器的插件管理中心，提供两个核心功能：

1. **插件浏览与管理** — 在编辑器的 Plugins 面板中查看所有已安装插件，按分类筛选、启用/禁用插件、搜索插件
2. **插件创建向导** — 通过可视化向导从模板创建新插件，支持多种模板类型（基础、高级、空白、蓝图库、编辑器模式、第三方库）

该插件是每个 UE 项目开发中几乎必用的编辑器工具，用户无需了解它存在——它就是编辑器中"Edit > Plugins"菜单背后的功能实现。插件依赖 `PluginUtils` 插件来处理底层的插件文件操作（复制、移动、重命名等）。

## 使用场景

- 你在开发过程中需要启用或禁用某个引擎插件 → 打开 Plugins 面板浏览和切换
- 你需要为项目创建一个全新的 C++ 插件 → 使用插件创建向导选择模板
- 你需要查看某个插件的依赖关系、版本信息或加载状态 → 在 Plugins 面板中查看详情
- 你需要搜索引擎中已安装的所有插件 → 使用搜索框按名称过滤

## 蓝图用法

Plugin Browser 是纯编辑器 UI 插件，不暴露 BlueprintCallable API。所有功能通过编辑器菜单访问：

### 访问方式

| 入口 | 说明 |
|---|---|
| **Edit > Plugins** | 打开插件浏览器面板 |
| **Content Browser > New Plugin** | 通过插件创建向导新建插件 |

### 插件创建向导支持的模板

| 模板名 | 说明 |
|---|---|
| Basic | 最小化插件结构，含基本模块 |
| Advanced | 完整插件结构，含 Editor 模块分离 |
| Blank | 空白插件骨架 |
| BlueprintLibrary | 为蓝图暴露 C++ 函数的插件模板 |
| EditorMode | 自定义编辑器模式插件模板 |
| ThirdPartyLibrary | 集成第三方库的插件模板 |

## C++ 用法

Plugin Browser 主要是一个 UI 层插件，不提供公共 API 供外部模块调用。其内部实现涉及 Slate UI 构建、IPluginBrowser 接口等，以下是相关内部结构供参考。

### 头文件引入

```cpp
// 引入插件浏览器模块（仅编辑器模块使用）
#include "PluginBrowserModule.h"
```

### 插件模板结构参考

当你通过 Plugin Browser 创建插件时，生成的 Basic 模板结构如下：

```cpp
// Templates/Basic/Source/PLUGIN_NAME/PLUGIN_NAME.Build.cs 的生成逻辑
using UnrealBuildTool;

public class PLUGIN_NAME : ModuleRules
{
    public PLUGIN_NAME(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        PublicDependencyModuleNames.AddRange(new string[] { "Core", "CoreUObject", "Engine" });
    }
}
```

### 第三方库模板中的导出宏示例

Plugin Browser 的 ThirdPartyLibrary 模板展示了如何声明外部库函数：

```cpp
// Templates/ThirdPartyLibrary/Source/ThirdParty/PLUGIN_NAMELibrary/Public/PLUGIN_NAMELibrary/ExampleLibrary.h
#include "PLUGIN_NAMELibrary/ExampleLibraryExport.h"

// 导出一个第三方库函数供模块调用
EXAMPLELIBRARY_IMPORT void ExampleLibraryFunction();
```

## Demo 示例

Plugin Browser 不提供可编程 API，因此无需示例代码。以下是典型使用流程：

### 创建新插件的步骤

```
1. 打开编辑器
2. 菜单: Tools > New Plugin（或 Content Browser 右键 > New Plugin）
3. 选择模板（如 Basic）
4. 填写插件名称、描述、作者
5. 选择是否包含 Content 目录
6. 点击 "Create Plugin"
7. 插件生成到项目目录的 Plugins/ 文件夹下
```

### 启用/禁用插件的步骤

```
1. 菜单: Edit > Plugins
2. 左侧分类树选择类别（如 Rendering、Editor 等）
3. 或在搜索框中输入插件名
4. 勾选/取消 Enabled 复选框
5. 确认重启编辑器以使更改生效
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `PluginUtils` | 插件级别的依赖，提供插件文件操作工具（复制、重命名、删除等） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-05-12 | `d93da640` | Added new PluginToolset AI Toolset for managing plugins. | 新增 AI 工具集用于管理插件 |
| 2026-04-08 | `d6aa71b0` | function rename | 函数重命名（代码清理） |
| 2026-04-08 | `612e6b9b` | Fixup plugin wizard to check for the actual name of the plugin we'll create rather than the name the | 修复插件向导中名称校验逻辑，使用实际创建名而非用户输入名 |
| 2026-03-16 | `e20d084a` | Add a way to sort plugins by names to simplify merging: | 新增按名称排序插件的功能，简化合并流程 |

### 维护评价

**🟢 活跃维护中**

Plugin Browser 作为编辑器核心组件，持续受到维护和改进：

- **创建于 2015 年**，已有 10 年历史，是 UE 编辑器的基础设施级插件
- **持续更新**：最近的提交包括功能增强（AI 工具集、排序功能）和 Bug 修复（名称校验、编译警告），表明仍在积极开发
- **由 Epic Games 官方维护**，不会被废弃
- **推荐使用**：这是所有 UE 开发者的必备工具，无需额外安装即可使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/PluginBrowser)
- [PluginUtils 依赖插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/PluginUtils)