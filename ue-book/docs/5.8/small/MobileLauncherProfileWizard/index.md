# Mobile Launcher Profile Wizard

> Wizard for mobile packaging scenarios（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 移动端打包向导 |
| 分类 | Misc |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `MobileLauncherProfileWizard` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2016-07-19 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/MobileLauncherProfileWizard) | |

## 用途

`MobileLauncherProfileWizard` 是一个编辑器插件，其核心功能是提供一个向导（Wizard）界面，用于简化和引导开发者创建适用于 **Android** 和 **iOS** 平台的“项目启动器（Project Launcher）”打包配置文件（Profile）。

该插件主要解决以下问题：
1.  **简化复杂打包配置**：手动在项目启动器中配置移动端打包流程（特别是涉及应用程序本体与可下载内容分离的场景）步骤繁多且容易出错。该向导通过分步引导，将配置过程结构化。
2.  **支持分离式打包**：专门为 **“最小化应用程序本体 + 可下载内容（DLC）”** 的打包场景设计。开发者可以方便地为应用本体和DLC分别指定地图、烹饪风味（Cook Flavor）等参数。
3.  **多平台支持**：内置了针对 Android 和 iOS 两个移动平台的独立向导流程。
4.  **配置存档**：允许用户指定构建产物的存档目录。

## 使用场景

当你遇到以下需求时，可以使用此插件：
- 你的移动端项目采用**应用本体与额外内容（DLC/更新）分离**的发布模式，需要为两者分别创建打包配置。
- 你需要**快速创建**针对 Android 或 iOS 平台的、包含多个烹饪风味（如 ETC1, ETC2 等）的打包配置文件。
- 你希望在打包完成后，**自动将构建产物复制**到一个指定的目录进行归档。

## 蓝图用法

该插件主要提供**编辑器内的图形界面**，用于配置项目启动器的打包配置文件（Profile）。它本身不暴露任何可供蓝图调用的节点（`BlueprintCallable`）或变量（`BlueprintReadWrite`）。其交互完全通过编辑器中的向导窗口完成。

## C++ 用法

该插件是一个**编辑器模块**，不直接在运行时（Runtime）或游戏逻辑中使用。其主要编程接口是模块本身。

### 头文件引入

```cpp
#include "IMobileLauncherProfileWizard.h"
```

### 基本用法

检查该模块是否可用，并获取其引用。这通常用于其他需要感知该向导插件是否存在的编辑器功能中。

```cpp
// 检查模块是否已加载并可用
if (IMobileLauncherProfileWizardModule::IsAvailable())
{
    // 获取模块的单例引用
    IMobileLauncherProfileWizardModule& WizardModule = IMobileLauncherProfileWizardModule::Get();
    // 可以进一步调用模块接口（如果定义了的话）
    // ...
}
```

## Demo 示例

由于此插件提供的是一个用户界面向导，因此没有可编译的 C++ 代码示例。其使用方式是交互式的：

1.  **启用插件**：默认情况下插件已启用。
2.  **打开向导**：在编辑器中，通过 **“平台” > “项目启动器”** 菜单打开项目启动器窗口。
3.  **选择向导**：在项目启动器窗口中，你会看到由本插件提供的向导选项，例如“Android 最小应用 + 下载内容”或“iOS 最小应用 + 下载内容”。
4.  **跟随步骤**：按照向导界面的提示，逐步选择目标平台、构建配置、应用本体的地图、DLC的地图、烹饪风味（Android）以及构建产物的存档目录。
5.  **完成创建**：向导将根据你的选择，在项目启动器中自动生成一个或多个配置好的打包配置文件。

## 模块依赖

从 `Build.cs` 分析，该插件主要依赖以下编辑器模块，无特殊依赖（仅标准 Core/Engine/Slate 等）：

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-01-28 | `7b9c3120` | Launch profile items that moved to the inner BuildCookRun are marked as deprecated | 标记了移动到内部构建烹饪运行流程的启动配置项为废弃 |
| 2025-10-31 | `3498a569` | Project Launcher changes for incremental cook: | 项目启动器针对增量烹饪功能的改动 |
| 2025-04-16 | `819d4140` | Changes to reflect the new incremental cook and zen snapshot import options: | 变更以反映新的增量烹饪和快照导入选项 |
| 2024-05-01 | `a2b56134` | Slate: Deprecate SListView::ItemHeight and STreeViewItemHeight. ItemHeight and ItemWidth are only us | Slate框架废弃了SListView和STreeView的相关高度属性 |

### 维护评价

**基本维护中，但功能可能正在被逐步取代或集成。**

-  **创建时间**：该插件创建于2016年，是一个历史悠久的编辑器工具。
-  **更新频率**：最近几年有提交记录（最新在2026年1月），表明仍在进行维护和适配引擎新特性（如增量烹饪）。
-  **活跃度**：更新主要是适配引擎底层功能的变化和API废弃，而非添加新功能。这表明该插件的核心功能已趋于稳定。
-  **状态判断**：从2026年的提交记录看，部分功能项被标记为**弃用（deprecated）**，这通常意味着它们将被新的实现方式所取代。虽然插件本身仍在运行，但其内部的一些机制可能在未来的引擎版本中被移除或重构。
-  **推荐使用**：该插件**默认启用**，是UE项目启动器中一个方便的配置工具。如果你需要快速创建移动端分离打包的配置文件，仍然可以使用它。但需注意，随着引擎的迭代，其内部实现可能会发生变化，且未来可能有更好的集成方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/MobileLauncherProfileWizard)