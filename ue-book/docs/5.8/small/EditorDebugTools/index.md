# EditorDebugTools

> Consolidated toolbox, gammaui, and module ui into a single debug tools plugin. The goal of the plugin is to house editor debug UIs going forward.

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

`EditorDebugTools` 插件是一个专为 UE 编辑器开发者设计的内部调试工具集。它旨在将多个原本分散的、用于调试编辑器或渲染问题的用户界面（如模块加载管理、Gamma 校准、纹理图集查看等）统一整合到一个插件中。其核心目标是为 Epic 内部开发提供一个便捷的“调试工具箱”，方便快速访问各种底层调试功能，而不是面向最终游戏内容的生产工具。

## 使用场景

- 你需要在编辑器中动态加载、卸载或重新编译特定的运行时模块，以调试模块依赖或加载问题时。
- 你需要精确调整编辑器的 Gamma 值来检查渲染颜色或排查显示问题时。
- 你需要查看引擎当前加载了哪些纹理图集、字体图集，或需要强制刷新字体缓存时。

## 蓝图用法

此插件主要提供 Slate UI 界面，并未暴露任何 `BlueprintCallable` 函数或 `BlueprintReadWrite` 属性供蓝图直接调用。其功能通过编辑器菜单（如 “Window” > “Editor Debug Tools”）访问。

## C++ 用法

此插件的核心是 Editor 模块和 Slate UI，通常在 C++ 中通过注册命令和菜单项来集成，而不是提供可调用的 API。以下是其内部结构的基本用法。

### 头文件引入

```cpp
#include "EditorDebugToolsModule.h"
#include "EditorDebugToolsCommands.h"
#include "EditorDebugToolsStyle.h"
```

### 基本用法

插件的启动和关闭遵循标准的 `IModuleInterface` 流程。

```cpp
// 源文件: Source/EditorDebugTools/Private/EditorDebugToolsModule.cpp
void FEditorDebugToolsModule::StartupModule()
{
    FEditorDebugToolsStyle::Initialize();
    FEditorDebugToolsCommands::Register();

    // 注册命令和生成器，用于在菜单和工具栏中创建入口
    PluginCommands = MakeShareable(new FUICommandList);
    PluginCommands->MapAction(
        FEditorDebugToolsCommands::Get().OpenPluginWindow,
        FExecuteAction::CreateRaw(this, &FEditorDebugToolsModule::PluginButtonClicked),
        FCanExecuteAction());

    UToolMenus::RegisterStartupCallback(FSimpleMulticastDelegate::FDelegate::CreateRaw(this, &FEditorDebugToolsModule::RegisterMenus));
}

void FEditorDebugToolsModule::ShutdownModule()
{
    UToolMenus::UnRegisterStartupCallback(this);
    UToolMenus::UnregisterOwner(this);
    FEditorDebugToolsStyle::Shutdown();
    FEditorDebugToolsCommands::Unregister();
}
```

### 进阶用法

插件内部定义了多个 Slate 控件来实现具体功能，例如 `SModuleUI` 用于模块管理。

```cpp
// 源文件: Source/EditorDebugTools/Private/SModuleUI.h
// SModuleUI 继承自 SCompoundWidget，用于展示和操作模块列表
class SModuleUI : public SCompoundWidget
{
    // ...
    // 内部结构 FModuleListItem 定义了模块的操作（加载、卸载、重载、重编译）
    struct FModuleListItem
    {
        FName ModuleName;
        FReply OnLoadClicked();
        FReply OnUnloadClicked();
        FReply OnReloadClicked();
        FReply OnRecompileClicked();
        // ...
    };
    // 使用 SListView 展示模块列表，并支持搜索过滤
    void OnModulesChanged(FName ModuleThatChanged, EModuleChangeReason ReasonForChange);
    void UpdateModuleListItems();
    void OnFilterTextChanged(const FText& InFilterText);
    // ...
};
```

## Demo 示例

以下是一个简化示例，演示如何在插件的 Slate UI 中添加一个自定义的调试面板标签页。此代码需在插件的模块类中实现。

```cpp
// MyDebugPanel.h
#pragma once
#include "Widgets/SCompoundWidget.h"

class SMyDebugPanel : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SMyDebugPanel) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs);
};
```

```cpp
// MyDebugPanel.cpp
#include "MyDebugPanel.h"
#include "Widgets/Text/STextBlock.h"

void SMyDebugPanel::Construct(const FArguments& InArgs)
{
    ChildSlot
    [
        SNew(STextBlock)
        .Text(FText::FromString(TEXT("Hello from my custom debug panel!")))
    ];
}
```

然后，在 `FEditorDebugToolsModule::PluginButtonClicked()` 函数创建主窗口时，可以将 `SMyDebugPanel` 作为一个新的标签页加入到 `SDebugPanel` 或类似的多标签控件中。

## 模块依赖

无特殊依赖（仅标准 Editor/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移旧版日志宏到新版 UE_LOGF，属于代码现代化。 |
| 2026-03-10 | `a69ab07d` | [IsSavingPackage] | 可能与保存包状态检查相关的修复或优化。 |
| 2024-10-22 | `98a8e0e0` | Removed lots of UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes | 清理了大量因引擎5.2版本头文件包含顺序改变而产生的废弃宏，是编译兼容性修复。 |
| 2024-05-01 | `a2b56134` | Slate: Deprecate SListView::ItemHeight and STreeViewItemHeight. ... | 跟随 Slate 框架更新，废弃了旧的列表项高度设置方式。 |
| 2023-05-15 | `da92084a` | Optimized out more private modules includes and dependencies. | 优化了私有模块的头文件包含和依赖，减小编译耦合。 |

### 维护评价

- **创建时间**：2020年创建，已有约6年历史。
- **最近更新频率**：最近的实质性更新停留在2023年5月。2024年和2026年的更新均为跟随引擎整体框架（如日志、Slate、头文件规范）的技术性维护，没有新功能添加。
- **活跃度**：插件功能已基本完善和稳定，处于**维护状态**，但更新频率低，不再有活跃的功能开发。
- **已知限制**：作为 Epic 内部调试工具，其UI和功能可能未经广泛的用户体验优化，且未来可能随引擎架构调整而变动。
- **推荐使用**：适用于需要快速访问引擎底层调试功能的**引擎开发者和高级用户**。对于普通游戏项目开发者，此插件提供的功能场景较为特定，**通常不推荐主动集成到游戏项目中**，但保持启用（默认状态）不会对项目产生影响。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/EditorDebugTools)
- 官方文档：无