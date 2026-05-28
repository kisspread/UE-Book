# Sequence Navigator

> An advanced sequence bread-crumbing tool with editing capabilities.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 序列导航器 |
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `SequenceNavigator` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-05-01 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SequenceNavigator) | |

## 用途

Sequence Navigator 是 UE5 Sequencer 的一个高级扩展，它为复杂的序列编辑提供了一个增强的、可定制的树状导航视图，替代了 Sequencer 原生的、功能相对固定的 Outliner（大纲）。

这个插件解决的核心问题是：当序列变得非常庞大和复杂（例如包含大量嵌套子序列、众多对象绑定和轨道）时，原生 Sequencer 的浏览和管理效率较低。它通过提供以下能力来解决这个问题：

1.  **清晰的层级浏览**：以树状结构清晰展示序列的层级关系（序列 → 绑定 → 轨道 → 片段等），并支持面包屑导航。
2.  **强大的过滤与搜索**：内置了完整的过滤栏，支持按类型（序列、轨道、绑定等）和自定义文本表达式进行快速过滤，便于在复杂序列中定位元素。
3.  **可扩展的编辑能力**：通过 Provider（提供者）机制，允许其他插件（如动画工具、电影工具集等）向导航器中注入自定义的项目类型（Item）、列（Column）和过滤器，从而使其适应特定的序列类型和工作流。
4.  **高级交互**：支持项目拖放、重命名、删除、颜色标记、锁定状态等丰富的编辑操作，并能与 Sequencer 的主视图保持选择同步。

简而言之，**它是一个专业、可扩展的序列管理面板，旨在提升在复杂序列项目中的生产力**。

## 使用场景

-   **你正在制作一部复杂的电影序列或大型过场动画**，其中包含了多层嵌套的子序列（Sub-Sequences）。使用 Sequence Navigator，你可以像浏览文件系统一样轻松地在这些子序列之间跳转，并使用过滤器快速找到特定的绑定或轨道。
-   **你正在开发一个自定义的动画编辑工具或电影编辑套件**，需要向 Sequencer 的侧边栏添加特殊的序列元素（例如，自定义的动画控制器、特效触发器）。通过实现一个 `FNavigationToolProvider`，你可以将这些自定义元素无缝集成到 Sequence Navigator 的树视图中，并为其添加专用的列和操作。
-   **你需要管理大量具有相似类型的轨道**（例如，几十个材质参数轨道）。你可以使用内置的文本过滤器（如 `Type="Material Track"`）一次性显示所有相关轨道，并进行批量操作。
-   **你在 Sequencer 中工作，希望有一个更强大、更可定制的大纲视图**。即使不使用扩展功能，Sequence Navigator 本身提供的树状结构、过滤栏和项目管理功能也优于原生 Outliner。

## 蓝图用法

经过对提供的源码文件（主要集中在 `Public` 头文件）的搜索，未发现 `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)` 标记。Sequence Navigator 主要是一个编辑器运行时（Editor Runtime）插件，其 API 和交互逻辑主要面向 C++ 开发人员，用于构建和扩展编辑器工具。

目前没有暴露直接的蓝图节点。

## C++ 用法

### 头文件引入

使用 Sequence Navigator 的核心 API，需要引入以下头文件：
```cpp
#include "NavigationToolExtender.h"
#include "INavigationTool.h"
#include "INavigationToolProvider.h"
#include "NavigationToolScopedSelection.h"
```

### 基本用法

1.  **查找 Sequencer 关联的导航工具实例**：
    通常，你需要从一个 `ISequencer` 实例来获取对应的 `INavigationTool`。
    ```cpp
    // 假设你有一个有效的 TSharedPtr<ISequencer> SequencerPtr
    TSharedPtr<UE::SequenceNavigator::INavigationTool> NavTool = UE::SequenceNavigator::FNavigationToolExtender::FindNavigationTool(SequencerPtr.ToSharedRef());
    if (NavTool.IsValid())
    {
        // 现在可以使用 NavTool 的接口了
        // 例如，获取当前选中的项目
        TArray<UE::SequenceNavigator::FNavigationToolViewModelWeakPtr> SelectedItems = NavTool->GetSelectedItems();
    }
    ```
    *(基于 `NavigationToolExtender.h` 中的 `FindNavigationTool` 方法)*

2.  **注册一个自定义的导航工具提供者 (Provider)**：
    这是扩展 Sequence Navigator 功能的核心步骤。
    ```cpp
    #include "Providers/NavigationToolProvider.h"

    // 定义一个自定义提供者
    class FMyAnimToolProvider : public UE::SequenceNavigator::FNavigationToolProvider
    {
    public:
        virtual FName GetIdentifier() const override { return TEXT("MyAnimTool"); }
        // 重写其他虚函数来定义行为...
        virtual TSet<TSubclassOf<UMovieSceneSequence>> GetSupportedSequenceClasses() const override
        {
            return { UMyCustomAnimSequence::StaticClass() };
        }
        // ...
    };

    // 在插件启动时注册
    void FMyAnimToolsModule::StartupModule()
    {
        // 假设你有一个目标 Sequencer 实例
        TSharedPtr<ISequencer> TargetSequencer = ...; // 获取方式取决于上下文
        if (TargetSequencer.IsValid())
        {
            TSharedRef<FMyAnimToolProvider> Provider = MakeShared<FMyAnimToolProvider>();
            UE::SequenceNavigator::FNavigationToolExtender::RegisterToolProvider(TargetSequencer.ToSharedRef(), Provider);
        }
    }
    ```
    *(基于 `NavigationToolExtender.h` 中的 `RegisterToolProvider` 方法和 `INavigationToolProvider.h` 接口)*

3.  **使用作用域选择 (Scoped Selection) 同步选择状态**：
    当你需要将 Sequence Navigator 中的选择同步到 Sequencer 主视图（例如，选中对应的轨道和片段）时。
    ```cpp
    #include "NavigationToolScopedSelection.h"

    void SelectSequenceInSequencer(ISequencer& Sequencer, UMovieSceneSequence* Sequence)
    {
        UE::SequenceNavigator::FNavigationToolScopedSelection ScopedSelection(Sequencer, UE::SequenceNavigator::ENavigationToolScopedSelectionPurpose::Sync);
        ScopedSelection.Select(Sequence);
        // 作用域结束时，ScopedSelection 的析构函数会调用 SyncSelections() 来应用选择
    }
    ```
    *(基于 `NavigationToolScopedSelection.h` 中的类定义)*

### 进阶用法：创建自定义项目代理 (Item Proxy)

Item Proxy 用于将具有共同特性的子项（例如，一个组件引用的所有材质）组合在一个虚拟父项下显示。

1.  定义你的 Item Proxy 类和对应的工厂类。
2.  在你的 `INavigationToolProvider` 的 `OnExtendItemProxiesForItem` 中创建并返回这些 Proxy。
3.  通过 `FNavigationToolExtender::GetItemProxyRegistry()` 全局注册，或通过 `INavigationTool` 实例的 `GetItemProxyFactory` 方法局部查找。
    *(此模式在 `INavigationToolItemProxyRegistry.h`、`INavigationToolItemProxyFactory` 相关接口及 `INavigationTool.h` 的模板方法 `GetOrCreateItemProxy` 中定义)*

## Demo 示例

以下是一个最简示例，展示如何创建一个自定义的 `INavigationToolProvider`，它仅为特定类型的序列在导航器中显示一条提示性信息。

### MyCustomProvider.h
```cpp
// MyCustomProvider.h
#pragma once

#include "Providers/NavigationToolProvider.h"

class UMySpecialSequence; // 你自定义的序列类型

class FMyCustomProvider : public UE::SequenceNavigator::FNavigationToolProvider
{
public:
    // 提供者的唯一标识符
    virtual FName GetIdentifier() const override;

    // 指定此提供者支持哪种序列类型
    virtual TSet<TSubclassOf<UMovieSceneSequence>> GetSupportedSequenceClasses() const override;

    // 当工具激活时，可以在此做初始化工作
    virtual void OnActivate() override;

    // 扩展子项：为根项目添加一个代表“我的工具”的子项
    virtual void OnExtendItemChildren(
        UE::SequenceNavigator::INavigationTool& InTool,
        const UE::SequenceNavigator::FNavigationToolViewModelPtr& InParentItem,
        TArray<UE::SequenceNavigator::FNavigationToolViewModelWeakPtr>& OutWeakChildren,
        const bool bInRecursive) override;

    // 决定项目是否应该被隐藏（这里我们不隐藏任何项）
    virtual bool ShouldHideItem(const UE::SequenceNavigator::FNavigationToolViewModelPtr& InItem) const override;

    // 工具是否只读
    virtual bool ShouldLockTool() const override;

    // 其他必要的重写函数（此处省略，使用基类默认实现）
    // ...
};
```

### MyCustomProvider.cpp
```cpp
// MyCustomProvider.cpp
#include "MyCustomProvider.h"
#include "Items/NavigationToolItem.h" // 基础项目类
#include "NavigationToolDefines.h"

// 一个简单的项目类，用于显示信息
class FMyInfoItem : public UE::SequenceNavigator::FNavigationToolItem
{
public:
    FMyInfoItem(UE::SequenceNavigator::INavigationTool& InTool, const UE::SequenceNavigator::FNavigationToolViewModelPtr& InParent)
        : FNavigationToolItem(InTool, InParent)
    {}

    virtual bool IsAllowedInTool() const override { return true; }
    virtual FText GetDisplayName() const override { return NSLOCTEXT("MyTool", "InfoItem", "My Custom Tool Active"); }
    virtual FText GetClassName() const override { return NSLOCTEXT("MyTool", "InfoClass", "Info"); }
    virtual bool CanBeTopLevel() const override { return false; } // 作为子项
    // ... 可以重写图标、颜色等
};

FName FMyCustomProvider::GetIdentifier() const
{
    return TEXT("MyCustomAnimationTool");
}

TSet<TSubclassOf<UMovieSceneSequence>> FMyCustomProvider::GetSupportedSequenceClasses() const
{
    return { UMySpecialSequence::StaticClass() };
}

void FMyCustomProvider::OnActivate()
{
    UE_LOG(LogTemp, Log, TEXT("MyCustomProvider Activated for a sequence!"));
}

void FMyCustomProvider::OnExtendItemChildren(
    UE::SequenceNavigator::INavigationTool& InTool,
    const UE::SequenceNavigator::FNavigationToolViewModelPtr& InParentItem,
    TArray<UE::SequenceNavigator::FNavigationToolViewModelWeakPtr>& OutWeakChildren,
    const bool bInRecursive)
{
    // 只在根项目下添加一个自定义项
    if (InParentItem.IsValid() && InParentItem->GetItemId() == UE::SequenceNavigator::FNavigationToolItemId::RootId)
    {
        // 使用 InTool 的 FindOrAdd 模板方法安全地创建或获取项目
        UE::SequenceNavigator::FNavigationToolViewModelPtr InfoItem = InTool.FindOrAdd<FMyInfoItem>(
            // 传入提供者自身作为上下文
            SharedThis(this) // 注意：这里需要根据实际情况调整，可能需要使用 InTool 的方法或缓存引用
            // 以及父项
        );
        if (InfoItem.IsValid())
        {
            OutWeakChildren.Add(InfoItem);
        }
    }
}

bool FMyCustomProvider::ShouldHideItem(const UE::SequenceNavigator::FNavigationToolViewModelPtr& InItem) const
{
    return false; // 不隐藏任何项
}

bool FMyCustomProvider::ShouldLockTool() const
{
    return false; // 不锁定工具
}
```

*(此示例模式基于 `INavigationToolProvider.h` 和 `INavigationTool.h` 中 `FindOrAdd` 方法的用法)*

## 模块依赖

| 模块 | 用途 |
|---|---|
| `SequencerCore` | Sequencer 核心模块，提供基础的 ViewModel、扩展接口和类型系统 |
| `MovieScene` | 电影场景模块，提供序列、轨道、片段等底层数据结构和运行时逻辑 |
| `EditorWidgets` | 编辑器控件模块，可能用于构建自定义的树视图行、列等 UI 组件 |
| `ToolMenus` | 工具菜单模块，用于在 Sequencer 工具栏或菜单中添加扩展项 |

*注：基于插件功能和 UE 编辑器插件的常见模式推断，`Build.cs` 中的 `PublicDependencyModuleNames` 和 `PrivateDependencyModuleNames` 应包含以上或类似模块。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-15 | `9ec79a5f` | [SequencerSimpleView] Force Sequence Navigator button to be immediately after the Curve Editor button | 调整工具栏按钮布局，将序列导航器按钮紧跟在曲线编辑器按钮之后。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志系统迁移：将UE_LOG宏迁移到UE_LOGF。 |
| 2026-03-10 | `c24c9de5` | Sequencer: Visbility of filter pills is now saved per UI area instead of per filter bar instance. | 优化过滤器设置存储逻辑，将过滤药丸的可见性按UI区域而非每个过滤栏实例保存。 |
| 2026-03-05 | `51ed8e99` | Sequencer: Remove vertical layout from Sequencer's filter bar. | 移除序列器过滤栏的垂直布局选项。 |
| 2026-01-29 | `1ad8c041` | [Sequencer] Fix "Name" text expression "!=" operator not working | 修复过滤器文本表达式中“Name”字段的“!=”运算符不生效的问题。 |

### 维护评价

-   **活跃维护**：插件处于**实验性**阶段（`IsExperimentalVersion = true`），从 2025 年 5 月创建至今（约 1 年），最近一次更新在 2026 年 4 月，表明 Epic 团队仍在积极开发和完善此功能。
-   **功能演进**：近期的更新集中在用户体验优化（按钮布局）、基础设施改进（日志系统）、设置存储逻辑优化和 Bug 修复，说明插件已进入功能稳定后的打磨阶段。
-   **潜在风险与建议**：作为**实验性插件**，其 API 和行为在未来 UE 版本中可能发生**不兼容的变更**。建议在项目中使用时密切关注版本更新日志，并做好迁移准备。目前适合在内部工具或早期项目中用于原型开发和工作流验证，但在追求稳定性的正式项目中使用需谨慎评估。
-   **推荐度**：如果你的需求是深度定制 Sequencer 的序列管理界面，且能接受实验性 API 带来的风险，那么**强烈推荐**使用此插件作为基础。否则，建议仅关注其设计理念，或等待其转为正式功能。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SequenceNavigator)
- 官方文档：无（`.uplugin` 中 `DocsURL` 字段为空）
- 测试用例：未在提供的源码路径中明确标识独立的测试目录。通常 UE 插件的自动化测试可能位于 `Engine/Tests/` 或插件内部的 `Tests/` 目录，需根据实际仓库结构确认。