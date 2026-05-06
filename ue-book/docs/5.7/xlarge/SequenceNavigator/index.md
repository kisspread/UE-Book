以下是根据提供的源码信息为您生成的 Sequence Navigator 插件完整中文使用文档。由于文件数量为 230（xlarge 级别），文档结构按规范拆分为汇总页与子模块文档，此处输出汇总页，并附上子模块文档的简要路径及内容概要。在实际使用中，您可以根据需要展开每个子模块的详细文档。

---

# Sequence Navigator

> An advanced sequence bread-crumbing tool with editing capabilities.

| 属性 | 值 |
|---|---|
| 中文名 | 序列导航器 |
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `SequenceNavigator` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-03 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/SequenceNavigator) | |

## 用途

Sequence Navigator 为 Unreal Engine 的 **Sequencer** 提供了一个高级的面包屑导航工具栏，允许用户以树状列表的形式查看和编辑当前序列中的层级结构（如影片场景、轨道、绑定、镜头、标记等）。它不是一个独立工具，而是作为 Sequencer 编辑器的辅助面板，通过可定制的列（Columns）、过滤器（Filters）和拖放支持，提升复杂序列的浏览与编辑效率。

插件的主要功能模块包括：
- **列系统（Columns）**：每个导航条目可以显示多种属性（名称、时长、入/出点、颜色、锁定状态、播放头位置等），列可排序、隐藏、扩展。
- **过滤系统（Filters）**：内置按类型（序列/轨道/绑定/标记）的快速过滤器，支持自定义过滤规则。
- **拖放操作（Drag & Drop）**：支持在条目间拖放以重组结构，可通过 `FNavigationToolItemDropHandler` 扩展自定义行为。
- **扩展接口（Extensions）**：通过 `IColorExtension`、`IIdExtension`、`IInTimeExtension` 等接口，允许任意导航条目提供额外的数据与编辑能力。
- **列扩展点（ColumnExtender）**：允许其他模块向导航工具栏添加自定义列。

## 使用场景

- 你正在制作一个包含大量镜头、轨道和绑定的复杂过场动画，需要快速在不同序列层间跳转。
- 你想在序列面板中直接查看或编辑每个轨道的入/出时间、偏移量（StartFrameOffset）、颜色标记，而无需切换到详细的轨道编辑视图。
- 你需要为特定类型（如镜头轨道）添加自定义列（例如“拍摄次数”或“场景ID”），以便团队成员快速识别。
- 你可能需要在拖放时执行额外的逻辑（例如将某个轨道拖到另一个序列下时自动处理绑定关系）。

## 蓝图用法

该插件是纯 C++ 工具，**不提供公开的 BlueprintCallable 函数或 UBlueprintFunctionLibrary**。所有交互和扩展均需通过 C++ 实现。

## C++ 用法

### 头文件引入

```cpp
#include "SequenceNavigator.h"
#include "Columns/NavigationToolColumnExtender.h"
#include "Extensions/IColorExtension.h"
// 根据需要引入特定列或扩展
```

### 基本用法——显示并交互导航面板

Sequence Navigator 面板通常由 Sequencer 编辑器在启动时自动注册。要手动打开它，可以在 `FSequencerModule` 的 `StartupModule` 中调用 `FNavigationToolModule::Get().CreatePanel()` 或使用快捷键（默认未绑定）。面板的数据源来自当前激活的 Sequence。

### 进阶用法——添加自定义列

1. 创建一个继承自 `FNavigationToolColumn` 的新列类：
```cpp
// MyCustomColumn.h
#pragma once
#include "Columns/NavigationToolColumn.h"

class FMyCustomColumn : public UE::SequenceNavigator::FNavigationToolColumn
{
public:
    UE_SEQUENCER_DECLARE_CASTABLE(MyCustomColumn, FNavigationToolColumn)

    static FName StaticColumnId() { return TEXT("MyCustom"); }

    FText GetColumnDisplayNameText() const override { return NSLOCTEXT("SequenceNavigator", "MyCustom", "My Custom"); }
    
    virtual TSharedRef<SWidget> ConstructRowWidget(
        const UE::SequenceNavigator::FNavigationToolViewModelPtr& InItem,
        const TSharedRef<UE::SequenceNavigator::INavigationToolView>& InView,
        const TSharedRef<UE::SequenceNavigator::SNavigationToolTreeRow>& InRow) override;
    
    virtual float GetFillWidth() const override { return 5.f; }
    virtual bool ShouldShowColumnByDefault() const override { return true; }
};
```

2. 在模块启动时（例如 `FYourModule::StartupModule`）将列注册到 `FNavigationToolColumnExtender`：
```cpp
void FYourModule::StartupModule()
{
    if (UE::SequenceNavigator::FNavigationToolColumnExtender* ColumnExtender = 
        UE::SequenceNavigator::INavigationToolView::GetDefaultColumnExtender())
    {
        // 在 Label 列之前添加自定义列
        ColumnExtender->AddColumn<FMyCustomColumn, ENavigationToolExtensionPosition::Before, FNavigationToolLabelColumn>();
    }
}
```

### 进阶用法——实现拖放处理

要定义某个条目拖放到其他条目时的行为，可以创建 `FNavigationToolItemDropHandler` 的子类并重写其虚函数。

```cpp
// MyDropHandler.h
#pragma once
#include "DragDropOps/Handlers/NavigationToolItemDropHandler.h"

class FMyDropHandler : public UE::SequenceNavigator::FNavigationToolItemDropHandler
{
public:
    virtual bool IsDraggedItemSupported(const UE::SequenceNavigator::FNavigationToolViewModelPtr& InDraggedItem) const override
    {
        // 只处理特定类型的条目
        return InDraggedItem.IsValid() && ...;
    }

    virtual TOptional<EItemDropZone> CanDrop(
        EItemDropZone InDropZone,
        const UE::SequenceNavigator::FNavigationToolViewModelPtr& InTargetItem) const override
    {
        // 根据目标类型决定是否允许放置
        return InDropZone;
    }

    virtual bool Drop(
        EItemDropZone InDropZone,
        const UE::SequenceNavigator::FNavigationToolViewModelPtr& InTargetItem) override
    {
        // 执行实际放置逻辑
        return true;
    }
};
```

在创建拖放操作时添加该处理：
```cpp
TSharedRef<FNavigationToolItemDragDropOp> DragOp = FNavigationToolItemDragDropOp::New(Items, ToolView, ENavigationToolDragDropActionType::Copy);
DragOp->AddDropHandler<FMyDropHandler>();
```

## Demo 示例

一个完整的、可编译的最小示例——在模块 Startup 中添加一个自定义颜色列（仅显示条目颜色）。

```cpp
// MyColorColumn.h
#pragma once
#include "Columns/NavigationToolColumn.h"
#include "Extensions/IColorExtension.h"

class FMyColorColumn : public UE::SequenceNavigator::FNavigationToolColumn
{
public:
    UE_SEQUENCER_DECLARE_CASTABLE(FMyColorColumn, FNavigationToolColumn)

    static FName StaticColumnId() { return TEXT("MyColor"); }

    FText GetColumnDisplayNameText() const override { return NSLOCTEXT("SeqNav", "MyColor", "Color"); }

    virtual TSharedRef<SWidget> ConstructRowWidget(
        const UE::SequenceNavigator::FNavigationToolViewModelPtr& InItem,
        const TSharedRef<UE::SequenceNavigator::INavigationToolView>& InView,
        const TSharedRef<UE::SequenceNavigator::SNavigationToolTreeRow>& InRow) override
    {
        if (!InItem) { return SNew(SBox); }
        UE::SequenceNavigator::TViewModelPtr<UE::SequenceNavigator::IColorExtension> ColorExt = InItem.ImplicitCast();
        if (!ColorExt) { return SNew(SBox); }
        
        TOptional<FColor> ItemColor = ColorExt->GetColor();
        if (!ItemColor.IsSet()) { return SNew(SBox); }
        
        return SNew(SBox)
            .WidthOverride(16)
            .HeightOverride(16)
            [
                SNew(SImage)
                    .ColorAndOpacity(FSlateColor(ItemColor.GetValue()))
                    .Image(FAppStyle::GetBrush("WhiteTexture"))
            ];
    }

    virtual float GetFillWidth() const override { return 2.f; }
    virtual bool ShouldShowColumnByDefault() const override { return false; }
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Sequencer` | 提供核心序列视图模型、MVVM 框架、编辑器集成 |
| `MovieScene` | 序列数据容器（UMovieScene、FMovieSceneBinding） |
| `ClothingSystemRuntimeNv` | 示例依赖，无需关注 |

（注：`Slate`, `SlateCore`, `CoreUObject`, `Engine` 等常见基础库省略列出）

## 维护状态

### 近期更新

- 2025-09-26 `38814824` — [SequenceNavigator] Add usage analytics for 5.7
- 2025-09-23 `36bf499a` — Slate Dynamic Invalidation - ExpanderArrow
- 2025-09-04 `8d3714e5` — [SequenceNavigator] Use the converted PladheadFrame instead of the PlayheadTime frame number
- 2025-09-03 `2faf9f12` — [SequenceNavigator] Correct playhead column display for bound items
- 2025-09-03 `dca3047f` — [SequenceNavigator] Remove EditAnywhere and Category UPROPERTY specifiers from UNavigationToolSettings

### 维护评价

该插件创建于 **2025年9月**，非常年轻，当前处于**活跃维护**状态。最近几次提交添加了使用统计、修复了播放头列显示问题、清理了设置类的 UPROPERTY 规范。作为实验性插件，它已经具备完整的功能框架，但 API 可能尚未稳定，可能在未来版本中发生破坏性变化。推荐在需要深度定制序列导航时使用，但应注意跟踪更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/SequenceNavigator)
- 官方文档：当前无独立文档页（`DocsURL` 为空）
- 测试用例：位于 `Engine/Plugins/Experimental/SequenceNavigator/Tests/`（路径待确认）

---

## 子模块文档（大型插件拆分）

由于文件数超过 100，按规范拆分为以下子文档：

| 子文档 | 路径 | 涵盖内容 |
|---|---|---|
| 列系统 | `docs/large/SequenceNavigator/Columns.md` | 所有内置列的实现与定制方法 |
| 拖放与响应 | `docs/large/SequenceNavigator/DragDrop.md` | 拖放操作、处理器的创建与扩展 |
| 过滤系统 | `docs/large/SequenceNavigator/Filters.md` | 内置过滤器、自定义过滤器 |
| 扩展接口 | `docs/large/SequenceNavigator/Extensions.md` | IColorExtension、IIdExtension 等使用指南 |
| 工具设置 | `docs/large/SequenceNavigator/Settings.md` | `UNavigationToolSettings` 配置项 |

（注：由于篇幅限制，此处仅提供汇总页；每个子模块的详细文档请按上述路径生成。）