# Cinematic Sequence Navigator Bridge

> Sequence Navigator Bridge for Cinematic Assemblies

| 属性 | 值 |
|---|---|
| 中文名 | 过场序列导航桥接 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CinematicSequenceNavigator` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-05-31 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/CinematicSequenceNavigator) | |

## 用途

该插件是 **Sequence Navigator** 与 **Cinematic Assembly Tools** 之间的桥接层。它通过实现 `FNavigationToolProvider` 接口，将过场动画组装（Cinematic Assembly）专用的序列类型、列定义、过滤器、工具栏和右键菜单扩展注入到 Sequence Navigator 中。

简单来说：Sequence Navigator 是 Sequencer 内嵌的通用序列导航面板，而此插件让它能够识别并正确显示 Cinematic Assembly 专属的内容结构（如列视图、子项层级、拖放操作等），使过场动画工作流中的序列管理更加完整。

## 使用场景

- 你使用 **Cinematic Assembly**（过场动画组装）工作流管理多个子序列 → 安装此插件后，Sequence Navigator 会自动适配过场组装序列的层级结构
- 你需要在 Sequence Navigator 中查看、过滤和组织过场组装相关的序列节点 → 此插件提供了专用的列视图、过滤器和上下文菜单扩展
- 你正在开发或扩展 Sequence Navigator 的自定义 Provider → 此插件是一个完整的 Provider 实现参考

## 蓝图用法

该插件不暴露任何 `BlueprintCallable` 或 `BlueprintReadWrite` API。它是一个纯 C++ 编辑器扩展，通过模块启动时注册 Provider 的方式自动集成到 Sequence Navigator 中，无需蓝图配置。

## C++ 用法

该插件的核心是一个 **Navigation Tool Provider** 实现。以下是其架构和使用方式：

### 头文件引入

```cpp
#include "NavigationToolProvider.h"
#include "CinematicNavigationToolProvider.h"
```

### 基本用法 — Provider 结构

Provider 继承自 `SequenceNavigator::FNavigationToolProvider`，通过覆写虚函数来扩展 Sequence Navigator 的行为。

```cpp
// 来源: Source/CinematicSequenceNavigator/Private/CinematicNavigationToolProvider.h

namespace UE::CineAssemblyTools
{

class FCinematicNavigationToolProvider : public SequenceNavigator::FNavigationToolProvider
{
public:
    // 标识符，用于注册和查找
    static const FName Identifier;

    // 获取 Provider 的唯一标识
    virtual FName GetIdentifier() const override;

    // 声明支持的序列类型（Cinematic Assembly 序列）
    virtual TSet<TSubclassOf<UMovieSceneSequence>> GetSupportedSequenceClasses() const override;

    // 指定默认列视图名称
    virtual FText GetDefaultColumnView() const override;

    // 保存/恢复导航工具的状态
    virtual FNavigationToolSaveState* GetSaveState(const INavigationTool& InTool) const override;
    virtual void SetSaveState(const INavigationTool& InTool, const FNavigationToolSaveState& InSaveState) const override;
};

} // namespace UE::CineAssemblyTools
```

### 进阶用法 — 扩展 UI 与交互

Provider 通过覆写以下虚函数来扩展 Sequence Navigator 的各个维度：

```cpp
// 来源: Source/CinematicSequenceNavigator/Private/CinematicNavigationToolProvider.h

// 扩展列定义（添加自定义列）
virtual void OnExtendColumns(FNavigationToolColumnExtender& OutExtender) override;

// 扩展列视图（定义列的显示组合）
virtual void OnExtendColumnViews(TSet<FNavigationToolColumnView>& OutColumnViews) override;

// 扩展项的子节点（注入过场组装的层级结构）
virtual void OnExtendItemChildren(INavigationTool& InTool,
    const FNavigationToolViewModelPtr& InParentItem,
    TArray<FNavigationToolViewModelWeakPtr>& OutWeakChildren,
    const bool bInRecursive) override;

// 扩展内置过滤器
virtual void OnExtendBuiltInFilters(TArray<FNavigationToolBuiltInFilterParams>& OutFilterParams) override;

// 绑定命令到 UI CommandList
virtual void BindCommands(const TSharedRef<FUICommandList>& InCommandList) override;

// Provider 激活/停用时的回调
virtual void OnActivate() override;
virtual void OnDeactivate() override;
```

模块启动时自动注册 Sequencer 的创建/关闭回调：

```cpp
// 来源: Source/CinematicSequenceNavigator/Private/CinematicSequenceNavigatorModule.h

void FCinematicSequenceNavigatorModule::StartupModule()
{
    // 监听 Sequencer 实例的创建
    SequencerCreatedHandle = FEditorDelegates::OnSequencerCreated.AddRaw(
        this, &FCinematicSequenceNavigatorModule::OnSequencerCreated);
}

void FCinematicSequenceNavigatorModule::ShutdownModule()
{
    // 清理委托
    FEditorDelegates::OnSequencerCreated.Remove(SequencerCreatedHandle);
    FEditorDelegates::OnSequencerClosed.Remove(SequencerClosedHandle);
}
```

## Demo 示例

该插件是纯编辑器扩展，不提供独立的可运行示例。以下是实现一个自定义 NavigationToolProvider 的最小骨架：

```cpp
// MyCustomNavigatorProvider.h
#pragma once

#include "Providers/NavigationToolProvider.h"

class FMyCustomNavigatorProvider : public SequenceNavigator::FNavigationToolProvider
{
public:
    static const FName Identifier;

    FMyCustomNavigatorProvider(const TSharedRef<ISequencer>& InSequencer);

    virtual FName GetIdentifier() const override { return Identifier; }
    virtual TSet<TSubclassOf<UMovieSceneSequence>> GetSupportedSequenceClasses() const override;
    virtual void OnExtendColumns(SequenceNavigator::FNavigationToolColumnExtender& OutExtender) override;
    virtual void OnExtendItemChildren(SequenceNavigator::INavigationTool& InTool,
        const SequenceNavigator::FNavigationToolViewModelPtr& InParentItem,
        TArray<SequenceNavigator::FNavigationToolViewModelWeakPtr>& OutWeakChildren,
        const bool bInRecursive) override;

private:
    TWeakPtr<ISequencer> WeakSequencer;
};
```

```cpp
// MyCustomNavigatorProvider.cpp
#include "MyCustomNavigatorProvider.h"

const FName FMyCustomNavigatorProvider::Identifier(TEXT("MyCustomNavigator"));

FMyCustomNavigatorProvider::FMyCustomNavigatorProvider(const TSharedRef<ISequencer>& InSequencer)
    : WeakSequencer(InSequencer)
{
}

TSet<TSubclassOf<UMovieSceneSequence>> FMyCustomNavigatorProvider::GetSupportedSequenceClasses() const
{
    // 返回此 Provider 支持的序列类型
    return { UMovieSceneSequence::StaticClass() };
}

void FMyCustomNavigatorProvider::OnExtendColumns(
    SequenceNavigator::FNavigationToolColumnExtender& OutExtender)
{
    // 在此处添加自定义列
}

void FMyCustomNavigatorProvider::OnExtendItemChildren(
    SequenceNavigator::INavigationTool& InTool,
    const SequenceNavigator::FNavigationToolViewModelPtr& InParentItem,
    TArray<SequenceNavigator::FNavigationToolViewModelWeakPtr>& OutWeakChildren,
    const bool bInRecursive)
{
    // 在此处注入子节点层级
}
```

## 模块依赖

从源码分析，该插件依赖了以下模块（省略常见依赖）：

| 模块 | 用途 |
|---|---|
| `SequenceNavigator` | 核心依赖，提供 `FNavigationToolProvider` 基类、`INavigationTool` 接口及所有导航工具基础设施 |
| `LevelSequenceEditor` | Sequencer 编辑器支持，提供 `ISequencer` 接口 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-09-22 | `9f83bb07` | [SequenceNavigator] Change or remove "Navigation Tool" comment references to "Sequence Navigator" fo | 重命名注释中的 "Navigation Tool" 为 "Sequence Navigator"，统一命名规范 |
| 2025-08-21 | `b340c11c` | Sequencer: Add id column, extension | 新增 ID 列及对应的扩展支持 |
| 2025-07-29 | `9a8d5bc1` | [SequenceNavigator] Refactor to use Sequencer view models and type macros | 重构为使用 Sequencer 视图模型和类型宏 |
| 2025-05-31 | `9ea86d8f` | [SequenceNavigator] Add new CinematicSequenceNavigator plugin that implements its provider for the navigator. | 初始创建，实现 Cinematic Assembly 的导航 Provider |

### 维护评价

- **年龄**：创建于 2025 年 5 月，是一个非常新的实验性插件
- **更新频率**：约每月一次实质性更新，处于早期快速迭代阶段
- **状态**：⚠️ **实验性插件**（`IsExperimentalVersion=true`），API 和功能可能随时变化
- **已知限制**：尚未启用 `EnabledByDefault=false`，需要手动在插件管理器中启用；源码中的 Commands 类尚为空（`@TODO: Add commands here`），表明功能仍在开发中
- **推荐**：仅建议关注过场动画组装工作流的开发者试用。作为 Experimental 插件，不建议在生产环境中依赖

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/CinematicSequenceNavigator)
- 官方文档：暂无