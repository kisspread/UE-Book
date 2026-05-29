# Motion Design Sequence Navigator Bridge

> Sequence Navigator Bridge for embedded Motion Design Sequences

| 属性 | 值 |
|---|---|
| 中文名 | 动效序列导航桥 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AvalancheSequenceNavigator` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-05-21 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AvalancheSequenceNavigator) | |

## 用途

此插件是 **Motion Design (Avalanche)** 和 **Sequencer** 系统之间的桥梁。它为 Motion Design 场景中使用的嵌入式序列（`UAvaSequence`）在 Sequencer 的 **Sequence Navigator** 面板中提供了一个专门的视图和操作能力。

简单来说，它解决了在复杂的动效项目中，管理多个 Motion Design 序列的效率问题。用户不再需要在单独的窗口或管理器中操作这些序列，而是可以直接在 Sequencer 强大的导航器中，像处理普通电影序列一样查看、排序、复制、删除和播放它们。

## 使用场景

- 你正在使用 **Motion Design** 工具制作复杂的产品展示或广告动画，场景中包含多个独立的动画序列片段。
- 你需要在 Sequencer 窗口中**统一管理**这些动画序列，而不是在 Motion Design 的单独界面中来回切换。
- 你需要**重排、复制、删除**某些动画序列的播放顺序，或者需要**快速预览**特定序列的播放效果。
- 你希望利用 Sequence Navigator 现有的列视图、过滤、拖放等高级功能来组织你的 Motion Design 序列。

## 蓝图用法

此插件主要以编辑器扩展和 C++ 模块的形式工作，**没有暴露任何蓝图可调用的函数或属性（BlueprintCallable/BlueprintReadWrite）**。它的核心逻辑完全在编辑器工具和 Sequencer UI 层面实现。

### 核心节点

（无）

### 使用示例（蓝图描述）

此插件不提供蓝图节点。其功能通过 Sequencer 的 Sequence Navigator 面板自动集成。当你的项目启用了此插件并在编辑器中打开包含 Motion Design 序列的关卡时，Sequence Navigator 会自动识别并列出这些序列。

## C++ 用法

插件的核心是将 Motion Design 的序列和操作适配到 Sequence Navigator 的框架中。主要扩展点是提供数据（Provider）、定义树节点（Item）和添加自定义列（Column）。

### 头文件引入

```cpp
#include "AvalancheSequenceNavigatorModule.h" // 模块管理
#include "AvaNavigationToolProvider.h"         // 导航器提供者
#include "Items/NavigationToolAvaSequence.h"   // 序列树节点
```

### 基本用法

以下是如何通过 C++ 代码访问和操作由该插件管理的序列项（通常在扩展或测试中使用）。

```cpp
// 假设你已经通过某种方式获得了对 INavigationTool 的引用 (InTool)
// 以及对该插件提供的提供者 (InProvider) 的引用

// 获取由提供者管理的顶级序列项
TArray<FNavigationToolViewModelPtr> TopLevelItems;
InProvider->OnExtendItemChildren(InTool, nullptr /*InParentItem*/, TopLevelItems, false /*bInRecursive*/);

// 遍历这些序列项
for (const FNavigationToolViewModelPtr& Item : TopLevelItems)
{
    // 尝试将其转换为 Motion Design 序列项
    if (FNavigationToolAvaSequence* AvaSeqItem = Item->Cast<FNavigationToolAvaSequence>())
    {
        // 获取底层的 UAvaSequence 资产
        UAvaSequence* Sequence = AvaSeqItem->GetAvaSequence();
        if (Sequence)
        {
            // 获取序列的显示名称
            FText DisplayName = AvaSeqItem->GetDisplayName();
            UE_LOG(LogTemp, Log, TEXT("Found Motion Design Sequence: %s"), *DisplayName.ToString());

            // 检查是否可以重命名
            if (AvaSeqItem->CanRename())
            {
                // AvaSeqItem->Rename(FText::FromString(TEXT("NewSequenceName")));
            }
        }
    }
}
```
*来源：基于 `NavigationToolAvaSequence.h` 中的接口和 `AvaNavigationToolProvider.h` 中的扩展逻辑推断。*

### 进阶用法：扩展插件功能

你可以创建自己的类来扩展或覆盖此插件的行为，例如添加新的自定义列。

```cpp
// 1. 定义一个自定义列
class FMyCustomAvaSequenceColumn : public SequenceNavigator::FNavigationToolColumn
{
    UE_SEQUENCER_DECLARE_CASTABLE(FMyCustomAvaSequenceColumn, FNavigationToolColumn);

    virtual FName GetColumnId() const override { return TEXT("MyCustomColumn"); }
    virtual FText GetColumnDisplayNameText() const override { return FText::FromString(TEXT("Custom Info")); }
    // ... 实现其他虚函数，如 ConstructRowWidget
};

// 2. 在某个编辑器模块中扩展提供者的列视图
void FMyEditorModule::ExtendAvaNavigatorColumns(SequenceNavigator::FNavigationToolColumnExtender& OutExtender)
{
    // 确保只在 Motion Design 提供者激活时扩展
    OutExtender.AddColumn(FMyCustomAvaSequenceColumn::StaticColumnId());
}
```
*来源：基于 `FAvaNavigationToolProvider` 的 `OnExtendColumns` 虚函数机制推断。*

## Demo 示例

以下示例展示了如何在你的编辑器模块中，当 Motion Design 序列导航器激活时，添加一个简单的自定义列来显示序列的资产路径。

**MySequenceNavigatorExtension.h**
```cpp
// Copyright Your Company. All Rights Reserved.
#pragma once

#include "Columns/NavigationToolColumn.h"

#define UE_API YOURMODULE_API

class FMyAvaSequencePathColumn : public UE::SequenceNavigator::FNavigationToolColumn
{
    UE_SEQUENCER_DECLARE_CASTABLE_API(UE_API, FMyAvaSequencePathColumn, UE::SequenceNavigator::FNavigationToolColumn);

public:
    static FName StaticColumnId() { return TEXT("AssetPath"); }

protected:
    // 列的基本信息
    virtual FName GetColumnId() const override { return StaticColumnId(); }
    virtual FText GetColumnDisplayNameText() const override;
    virtual float GetFillWidth() const override { return 2.0f; }

    // 为每一行创建显示此列数据的控件
    virtual TSharedRef<SWidget> ConstructRowWidget(
        const UE::SequenceNavigator::FNavigationToolViewModelPtr& InItem,
        const TSharedRef<UE::SequenceNavigator::INavigationToolView>& InView,
        const TSharedRef<UE::SequenceNavigator::SNavigationToolTreeRow>& InRow) override;
};

#undef UE_API
```

**MySequenceNavigatorExtension.cpp**
```cpp
// Copyright Your Company. All Rights Reserved.
#include "MySequenceNavigatorExtension.h"
#include "Items/NavigationToolAvaSequence.h"
#include "Widgets/Text/STextBlock.h"

FText FMyAvaSequencePathColumn::GetColumnDisplayNameText() const
{
    return NSLOCTEXT("MyColumns", "AvaSeqPath", "Path");
}

TSharedRef<SWidget> FMyAvaSequencePathColumn::ConstructRowWidget(
    const UE::SequenceNavigator::FNavigationToolViewModelPtr& InItem,
    const TSharedRef<UE::SequenceNavigator::INavigationToolView>& InView,
    const TSharedRef<UE::SequenceNavigator::SNavigationToolTreeRow>& InRow)
{
    FText PathText = FText::FromString(TEXT("--"));

    // 尝试将节点项转换为 AvaSequence 项
    if (UE::SequenceNavigator::FNavigationToolAvaSequence* AvaSeqItem = InItem->Cast<UE::SequenceNavigator::FNavigationToolAvaSequence>())
    {
        if (UAvaSequence* Sequence = AvaSeqItem->GetAvaSequence())
        {
            // 获取序列资产的路径
            PathText = FText::FromString(Sequence->GetPathName());
        }
    }

    return SNew(STextBlock)
        .Text(PathText)
        .Font(FCoreStyle::GetDefaultFontStyle("Regular", 10));
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MotionDesign` 或 `Avalanche` | 提供核心的 `UAvaSequence`、`IAvaSequencer` 等类和编辑器功能。 |
| `SequenceNavigator` | 提供 Sequence Navigator 面板的框架、提供者接口、列视图系统等。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-09-22 | `9f83bb07` | [SequenceNavigator] Change or remove "Navigation Tool" comment references to "Sequence Navigator" fo | 将代码注释中的“Navigation Tool”统一更正为“Sequence Navigator”，保持术语一致。 |
| 2025-09-10 | `b6a4d358` | Motion Design: fix issue where having an operator stack, or material designer details opened would c | 修复了当操作符栈或材质设计器详情打开时导致编辑器崩溃的问题。 |
| 2025-08-18 | `2d3d7c8d` | [SequenceNavigator] | 通用的代码维护或小功能提交。 |
| 2025-07-29 | `fda9994c` | [SequenceNavigator] Fix Horde loop variable error | 修复了一个与 Horde 相关的循环变量错误。 |
| 2025-07-29 | `9a8d5bc1` | [SequenceNavigator] Refactor to use Sequencer view models and type macros | 重构代码以使用 Sequencer 视图模型和类型宏，提升代码规范性和可维护性。 |

### 维护评价

**维护状态：活跃**

该插件自 2025 年 5 月创建以来，一直处于**积极的维护状态**。从 Git 历史来看，最近 3 个月内有多次提交，内容涵盖：
1.  **功能重构**：引入更现代的 Sequencer 视图模型（ViewModel）架构。
2.  **Bug 修复**：解决了具体的崩溃和运行时错误。
3.  **代码规范化**：统一术语，清理注释。

这是一个非常新的插件（约 0 年），处于**实验性阶段**（`IsExperimentalVersion=true`，`EnabledByDefault=false`）。这表明它功能已基本成型，但 API 和行为可能在未来版本中发生变化。目前**推荐用于评估和测试**，在生产环境中使用时需留意其实验性状态。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AvalancheSequenceNavigator)
- [官方文档]() (暂无)
- [测试用例]() (当前信息未提供明确测试文件路径)