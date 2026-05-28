# Customizable Sequencer Tracks (Experimental)

> Library that provides a blueprintable track type that can be added to sequencer

| 属性 | 值 |
|---|---|
| 中文名 | 自定义轨道插件 |
| 分类 | Runtime |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CustomizableSequencerTracks` (Runtime), `CustomizableSequencerTracksEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-08-11 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/CustomizableSequencerTracks) | |

## 用途

该插件旨在为开发者提供一种通过蓝图扩展虚幻引擎 Sequencer 序列编辑器的能力。其核心是允许开发者在蓝图中定义新的轨道（Track）和片段（Section）类型，从而在不编写 C++ 代码的情况下，为 Sequencer 添加自定义的动画、事件或数据通道。它解决了 Sequencer 原生轨道类型有限，且 C++ 扩展门槛较高的问题。

**注意：** 此插件为实验性（`IsBetaVersion=true`）且默认禁用（`EnabledByDefault=false`），表明其 API 和功能在未来版本中可能发生重大变化，不建议用于正式生产项目。

## 使用场景

- 你需要为 Sequencer 创建一个全新的轨道，用于驱动一个自定义的游戏系统（例如粒子特效、音频混合、AI 行为调度），并且希望全部通过蓝图实现。
- 你正在开发一个工具链，希望提供给设计师一套在 Sequencer 中可用的、易于使用的自定义控制轨道。
- 你希望快速原型化一个 Sequencer 扩展功能，暂时不需要复杂的 C++ 项目配置。

## 蓝图用法

该插件的蓝图功能主要通过 `USequencerTrackBP` 和 `USequencerSectionBP` 两个核心蓝图类来实现。开发者需要创建这些类的蓝图子类来定义自定义的轨道和片段行为。

### 核心类

| 类名 | 说明 |
|---|---|
| `USequencerTrackBP` | 代表 Sequencer 中的一个自定义轨道。所有蓝图自定义轨道均需继承自此类。 |
| `USequencerSectionBP` | 代表 Sequencer 轨道上的一个片段（Section）。它定义了片段的具体数据和逻辑。每个 `USequencerTrackBP` 可以关联一个或多个 `USequencerSectionBP` 类型。 |

### 使用示例（蓝图描述）

1.  在内容浏览器中右键，选择 `蓝图类`，在父类选择窗口中搜索并选择 `SequencerTrackBP`。
2.  在蓝图编辑器中，打开新创建的蓝图类。你可以重写 `GetSupportedSections` 函数来指定该轨道支持哪些类型的片段（即你的 `USequencerSectionBP` 子类）。
3.  同样，创建一个继承自 `SequencerSectionBP` 的蓝图类。在此类中，你可以重写 `OnSectionAdded`, `OnSectionRemoved` 等函数来定义当片段被添加到或移除出 Sequencer 时的行为，以及通过重写 `Tick` 函数来定义每帧更新逻辑。
4.  回到你的 `USequencerTrackBP` 蓝图，在 `GetSupportedSections` 中返回你创建的 `USequencerSectionBP` 子类。
5.  启用 `CustomizableSequencerTracks` 插件后，在 Sequencer 编辑器中，为对象添加轨道时，你的自定义轨道应出现在菜单中。

## C++ 用法

C++ 用法主要涉及该插件的编辑器模块，它负责将蓝图定义的轨道类型集成到 Sequencer 编辑器中。

### 头文件引入

```cpp
#include "CustomizableSequencerTracksEditorModule.h"
```

### 基本用法

该插件的 C++ 部分主要是框架，大部分扩展工作在蓝图中完成。但了解其内部结构有助于排查问题。主要的编辑器逻辑在 `FSequencerTrackBPEditor` 中处理。

```cpp
// 来源：Source/CustomizableSequencerTracksEditor/Private/SequencerTrackBPEditor.h
// FSequencerTrackBPEditor 是核心编辑器类，负责管理所有 USequencerTrackBP 类型的轨道。
// 它实现了 FMovieSceneTrackEditor 接口，处理轨道的创建、UI 构建和编辑逻辑。

// 例如，它通过 SupportsType 函数判断是否支持某个轨道类型：
// bool FSequencerTrackBPEditor::SupportsType(TSubclassOf<UMovieSceneTrack> Type) const;
// 当传入的 Type 是 USequencerTrackBP 或其子类时，返回 true。
```

### 进阶用法

如果你想通过 C++ 与这些蓝图轨道交互，或了解其注册机制，可以参考 `FCustomizableSequencerTracksStyle` 类。

```cpp
// 来源：Source/CustomizableSequencerTracksEditor/Private/CustomizableSequencerTracksStyle.h
// FCustomizableSequencerTracksStyle 负责在编辑器中注册新的轨道类型的图标和样式。
// 当一个新的 USequencerTrackBP 子类被创建时，系统会调用 RegisterNewTrackType 来确保它在编辑器中有正确的视觉表现。
// FCustomizableSequencerTracksStyle::Get().RegisterNewTrackType(MyCustomTrackClass);
```

## Demo 示例

由于该插件的大部分功能通过蓝图实现，此处提供一个最小化的 C++ 模块设置示例，用于在你的项目中加载和使用该插件。

```cpp
// MyProject.Build.cs (片段)
PublicDependencyModuleNames.AddRange(new string[]
{
    "CustomizableSequencerTracks", // 运行时功能
    "CustomizableSequencerTracksEditor" // 编辑器集成，如果需要在编辑器扩展中使用
});
```

```cpp
// MyProjectModule.h
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FMyProjectModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

```cpp
// MyProjectModule.cpp
#include "MyProjectModule.h"
#include "CustomizableSequencerTracksEditorModule.h" // 包含编辑器模块头文件以访问其功能

#define LOCTEXT_NAMESPACE "FMyProjectModule"

void FMyProjectModule::StartupModule()
{
    // 此处可以添加一些初始化逻辑，例如监听自定义轨道类型的创建
    // UCustomizableSequencerTracksEditorModule& EditorModule = FModuleManager::LoadModuleChecked<UCustomizableSequencerTracksEditorModule>("CustomizableSequencerTracksEditor");
    // EditorModule.OnCustomTrackRegistered().AddRaw(this, &FMyProjectModule::HandleCustomTrackRegistered);
}

void FMyProjectModule::ShutdownModule()
{
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyProjectModule, MyProject)
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MovieScene` | 提供 Sequencer 的核心运行时框架，是轨道和片段的基类所在。 |
| `SequencerCore` | 提供 Sequencer 编辑器和运行时的核心工具集。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2024-01-29 | `c262d4f9` | Sequencer: Outliner UX improvements | Sequencer 大纲视图用户体验改进 |
| 2023-12-09 | `64658cf6` | GetAssetRegistryTags deprecation: Make the old GetAssetRegistryTags and related functions deprecated | 适配资产注册表标签 API 废弃警告 |
| 2023-07-19 | `574e8e6e` | Add a ShortName to modules that generated paths over the 200 chars limit and a few modules that were | 为路径过长的模块添加短名称以解决兼容性问题 |
| 2023-05-16 | `de8db5ff` | Converting ARO-facing raw pointers to TObjectPtr ahead of raw pointer ARO API deprecation. | 将 ARO 相关的原始指针转换为 TObjectPtr，为后续 API 变更做准备 |
| 2023-02-21 | `d5a5a356` | Remove unnecessary Public and Private entries for the current module being added to PublicIncludePat | 清理构建文件中的冗余包含路径配置 |

### 维护评价

该插件自 2020 年创建以来，虽仍处于“实验性”状态且默认禁用，但近年来仍有持续的维护更新。更新内容主要集中在**适配引擎 API 变更**（如资产注册表标签废弃、TObjectPtr 迁移）和**修复构建/路径问题**，而不是功能上的重大新增。这表明 Epic Games 将其维持在一个可用的“维护模式”，但**并没有投入资源将其推向正式版或移除实验性标记**。对于希望扩展 Sequencer 的开发者，它仍然是一个有价值的参考和工具，但需意识到其未来可能发生变化或被废弃的风险。鉴于其持续的维护迹象，短期内可以谨慎使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/CustomizableSequencerTracks)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests)（注：测试用例通常位于引擎测试目录下，此插件的具体测试文件可能包含在 Sequencer 的整体测试中）