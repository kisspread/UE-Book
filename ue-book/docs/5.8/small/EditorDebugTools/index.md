# Editor Debug Tools

> 集成编辑器调试界面的工具插件。

| 属性 | 值 |
|---|---|
| 中文名 | 编辑器调试工具 |
| 分类 | Other |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `EditorDebugTools` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2020-10-19 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/EditorDebugTools) | |

## 用途

`EditorDebugTools` 插件的核心目的是将多个分散的编辑器调试和诊断界面整合到一个统一的插件中。从代码来看，它至少包含三个主要功能：
1.  **模块管理 UI (`SModuleUI`)**：提供一个图形化界面，用于查看、加载、卸载、重新加载和重新编译引擎与项目模块。
2.  **调试面板 (`SDebugPanel`)**：提供一系列快速操作按钮，如重新加载纹理、显示纹理/字体图集、刷新字体缓存和启动测试套件。
3.  **Gamma 校正面板 (`SGammaUIPanel`)**：允许开发者在编辑器内动态调整 Gamma 值，方便进行视觉调试。

这个插件存在是为了方便开发者和 QA 在编辑器内进行常见的运行时调试和资源状态检查，无需编写代码或使用复杂的命令行工具。

## 使用场景

- 你正在开发一个大型项目，模块众多，需要频繁地加载/卸载/重新编译特定模块进行测试。
- 你需要快速查看当前引擎加载了哪些模块及其状态（已加载、可关闭等）。
- 你在进行材质或渲染相关的开发，需要快速检查纹理图集或字体图集的打包情况。
- 你需要临时调整编辑器的 Gamma 值以匹配特定显示设备或进行视觉校准。
- 你需要快速刷新字体缓存以查看字体修改效果。

## 蓝图用法

此插件主要为编辑器工具面板，提供用户界面交互，而非传统的蓝图函数节点。其核心功能封装在 Slate Widget 中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `OnLoadClicked` | 加载选中的模块 | `SModuleUI::FModuleListItem` |
| `OnUnloadClicked` | 卸载选中的模块 | `SModuleUI::FModuleListItem` |
| `OnReloadClicked` | 重新加载选中的模块 | `SModuleUI::FModuleListItem` |
| `OnRecompileClicked` | 重新编译选中的模块 | `SModuleUI::FModuleListItem` |
| `OnReloadTexturesClicked` | 触发重新加载所有纹理 | `SDebugPanel` |
| `OnFlushFontCacheClicked` | 触发刷新字体缓存 | `SDebugPanel` |

### 使用示例（蓝图描述）

此插件的功能通过编辑器菜单或快捷键打开其停靠面板来使用，而非在蓝图图表中直接连接节点。通常，开发者通过主菜单栏（例如“Window > Developer Tools > Debug Tools”）或自定义快捷键打开该插件的窗口，然后在窗口中点击相应按钮执行操作。

## C++ 用法

此插件主要通过其提供的 Slate 面板与用户交互。其公共接口相对简单，主要是模块的注册和样式管理。

### 头文件引入

```cpp
#include "EditorDebugTools.h"
// 注意：SModuleUI 等主要功能类位于 Private 目录下，不作为公共API暴露，仅供插件内部使用。
```

### 基本用法

`EditorDebugTools` 模块作为编辑器模块加载，其 `StartupModule` 和 `ShutdownModule` 函数负责注册命令和样式。插件用户通常无需直接调用其 C++ 接口，而是使用其提供的 UI。

如果你正在扩展编辑器并希望以编程方式访问类似模块列表的信息，应该直接使用 `FModuleManager` API，而不是依赖此插件内部的 `SModuleUI`。

## Demo 示例

此插件本身即为一个完整的编辑器工具面板。以下是其内部主要 UI 组件 `SModuleUI` 的简化构造逻辑示例，展示了它如何构建模块列表：

```cpp
// SModuleUI::Construct 内部逻辑示意 (Source/EditorDebugTools/Private/SModuleUI.h)
void SModuleUI::Construct(const FArguments& InArgs)
{
    // 1. 创建搜索框
    ModuleNameSearchBox = SNew(SSearchBox)
        .HintText(NSLOCTEXT("ModuleUI", "SearchHint", "Search Modules"))
        .OnTextChanged(this, &SModuleUI::OnFilterTextChanged);

    // 2. 创建模块列表视图
    ModuleListView = SNew(SModuleListView)
        .ListItemsSource(&ModuleListItems)
        .OnGenerateRow(this, &SModuleUI::OnGenerateWidgetForModuleListView)
        .SelectionMode(ESelectionMode::Single);

    // 3. 布局：将搜索框和列表视图垂直排列
    ChildSlot
    [
        SNew(SVerticalBox)
        + SVerticalBox::Slot()
        .AutoHeight()
        [
            ModuleNameSearchBox.ToSharedRef()
        ]
        + SVerticalBox::Slot()
        [
            ModuleListView.ToSharedRef()
        ]
    ];

    // 4. 初始化模块列表
    UpdateModuleListItems();
    // 5. 注册模块变更回调
    FModuleManager::Get().OnModulesChanged().AddRaw(this, &SModuleUI::OnModulesChanged);
}
```

## 模块依赖

插件本身作为编辑器工具，其构建依赖主要为编辑器和 UI 框架。要使用此插件的功能，你的模块通常不需要直接依赖它，因为其功能是通过编辑器界面提供的。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移至 UE_LOGF 宏。 |
| 2026-03-10 | `a69ab07d` | [IsSavingPackage] | 添加对包保存状态的检查相关更新。 |
| 2024-10-22 | `98a8e0e0` | Removed lots of UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes | 移除了大量旧的包含顺序宏（UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2）。 |
| 2024-05-01 | `a2b56134` | Slate: Deprecate SListView::ItemHeight and STreeViewItemHeight. ItemHeight and ItemWidth are only us | Slate: 废弃 SListView::ItemHeight 等旧属性，统一使用新属性。 |
| 2023-05-15 | `da92084a` | Optimized out more private modules includes and dependencies. | 优化，移除了更多的私有模块包含和依赖。 |

### 维护评价

`EditorDebugTools` 是一个维护状态良好的**编辑器工具插件**。它创建于 2020 年，至今约 6 年，属于“老古董”级别，但近期仍有更新（最新至 2026 年）。更新内容主要是跟随引擎的代码现代化和重构（如日志宏迁移、废弃 API 更新、依赖清理），这表明它仍在被 Epic Games 主动维护，并确保其与最新引擎版本的兼容性。

**结论**：这是一个稳定、持续维护的编辑器实用工具。虽然功能较为基础，但因其提供了便捷的调试界面，对于开发者而言依然有价值。**推荐使用**，尤其是在需要频繁进行模块管理和资源调试的场景下。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/EditorDebugTools)
- 官方文档：无
- 测试用例：未在此插件目录内发现标准测试文件。