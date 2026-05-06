# Media Compositing

> Actors, components and Sequencer extensions for compositing media

| 属性 | 值 |
|---|---|
| 中文名 | 媒体合成 |
| 分类 | Rendering |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、编辑器相关资源） |
| 模块 | `MediaCompositing` (Runtime), `MediaCompositingEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-09-24 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/MediaCompositing) | |

## 用途

Media Compositing 插件为 Unreal Engine 的 Sequencer（过场动画编辑器）提供了一组工具，用于将媒体文件（如视频、图片序列）合成到关卡序列中。它允许你在 Sequencer 轨道上直接引用媒体源，并提供了以下核心能力：

- **媒体轨道编辑**：在 Sequencer 中创建和管理 `MediaTrack`，可以关联 `UMediaSource` 资源。
- **媒体缩略图**：在轨道上显示媒体帧的缩略图，便于直观定位时间点。
- **媒体播放器录制**：支持将 `UMediaPlayer` 的播放状态及帧画面录制到关卡序列中，用于后期合成或回放。
- **属性动画**：通过 `MediaPlayerPropertyTrackEditor` 可以像动画化普通属性一样，对 `UMediaPlayer` 对象上的媒体相关属性进行关键帧控制。

简单来说，该插件解决了在 Sequencer 中直接整合和操控媒体内容的需求，使得电影级的时间线合成更加流畅。

## 使用场景

- 你在制作一个带有过场动画的游戏，需要在特定时间点播放一段视频（如开场动画、简报画面）→ 使用 `MediaTrack` 将媒体源拖入 Sequencer。
- 你需要预览媒体在时间线上的帧位置，而不必每次手动拖动播放头 → 缩略图功能自动生成媒体帧快照。
- 你想要录制一个正在播放的媒体播放器的画面和状态，以便在序列中重复使用 → 利用 `MediaPlayerRecording` 和录制扩展器。

## 蓝图用法

该插件主要提供编辑器扩展，**没有公开的蓝图可调用函数或可访问的蓝图类**。所有功能均通过 Sequencer 编辑器界面和 C++ 扩展实现。如果你需要在蓝图中播放和控制媒体，请使用 `Media Player` 和 `Media Texture` 相关节点；而此插件的价值体现在 Sequencer 编辑时的工作流中。

## C++ 用法

### 头文件引入

```cpp
// 使用轨道编辑器时
#include "MediaCompositingEditor/Sequencer/MediaTrackEditor.h"
#include "MediaCompositingEditor/Sequencer/MediaPlayerPropertyTrackEditor.h"
// 使用缩略图功能时
#include "MediaCompositingEditor/Sequencer/MediaThumbnailSection.h"
// 录制相关
#include "MediaCompositingEditor/Sequencer/MediaSequenceRecorderExtender.h"
#include "MediaCompositingEditor/Sequencer/MovieSceneMediaPlayerSectionRecorder.h"
```

### 基本用法

**1. 注册自定义媒体轨道编辑器**

在 `ISequencerModule` 初始化时，注册 `FMediaTrackEditor` 和 `FMediaPlayerPropertyTrackEditor`：

```cpp
// YourModule.cpp
#include "ISequencerModule.h"
#include "MediaCompositingEditor/Sequencer/MediaTrackEditor.h"
#include "MediaCompositingEditor/Sequencer/MediaPlayerPropertyTrackEditor.h"

void YourModule::StartupModule()
{
    ISequencerModule& SequencerModule = FModuleManager::Get().LoadModuleChecked<ISequencerModule>("Sequencer");
    
    // 注册通用媒体轨道编辑器
    SequencerModule.RegisterTrackEditor(FOnCreateTrackEditor::CreateStatic(&FMediaTrackEditor::CreateTrackEditor));
    
    // 注册媒体播放器属性轨道编辑器
    SequencerModule.RegisterTrackEditor(FOnCreateTrackEditor::CreateStatic(&FMediaPlayerPropertyTrackEditor::CreateTrackEditor));
}
```

**来源**: `MediaTrackEditor.h` 中 `CreateTrackEditor` 静态方法。

**2. 使用缩略图部分**

当创建自定义缩略图渲染时，可实例化 `FMediaThumbnailSection`：

```cpp
// 在某个 ISection 派生类中
void MySection::CreateThumbnail(const TSharedPtr<FTrackEditorThumbnailPool>& ThumbnailPool, TSharedPtr<ISequencer> Sequencer)
{
    // 传入关联的 UMovieSceneMediaSection 等参数
    ThumbnailSection = MakeShared<FMediaThumbnailSection>(*Section, ThumbnailPool, Sequencer);
}
```

**来源**: `MediaThumbnailSection.h`

**3. 录制媒体播放器到序列**

通过 `FMediaSequenceRecorderExtender` 扩展录制功能：

```cpp
// 在序列录制定制中
TSharedRef<FMediaSequenceRecorderExtender> RecorderExtender = MakeShared<FMediaSequenceRecorderExtender>();
RecorderExtender->AddNewQueueRecording(MediaPlayerObject);
```

然后通过 `BuildQueuedRecordings` 生成实际的 `FMovieSceneMediaPlayerSectionRecorder` 来创建轨道和段。

**来源**: `MediaSequenceRecorderExtender.h`、`MovieSceneMediaPlayerSectionRecorder.h`

### 进阶用法

**自定义媒体轨道的外观（使用 `FOnBuildOutlinerEditWidget` 事件）**

`FMediaTrackEditor` 暴露了一个静态事件 `OnBuildOutlinerEditWidget`，你可以插入自定义菜单项：

```cpp
#include "MediaCompositingEditor/Sequencer/MediaTrackEditor.h"

// 在启动时注册
FMediaTrackEditor::OnBuildOutlinerEditWidget.AddStatic([](FMenuBuilder& MenuBuilder)
{
    MenuBuilder.AddMenuEntry(
        FText::FromString("My Custom Source"),
        FText::FromString("Add a custom media source"),
        FSlateIcon(),
        FUIAction(FExecuteAction::CreateLambda([](){
            // 自定义逻辑
        }))
    );
});
```

**来源**: `MediaTrackEditor.h` 第 31 行声明 `DECLARE_EVENT_OneParam(FMediaTrackEditor, FOnBuildOutlinerEditWidget, FMenuBuilder&);`

## Demo 示例

以下是一个完整的最小 C++ 示例，展示如何在编辑器模块的启动时注册该插件的轨道编辑器，并在 Sequencer 中使用它们（依赖已通过 Build.cs 配置）。

### MediaTrackDemoModule.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleInterface.h"
#include "Modules/ModuleManager.h"

class FMediaTrackDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

### MediaTrackDemoModule.cpp

```cpp
#include "MediaTrackDemoModule.h"
#include "ISequencerModule.h"
#include "MediaCompositingEditor/Sequencer/MediaTrackEditor.h"
#include "MediaCompositingEditor/Sequencer/MediaPlayerPropertyTrackEditor.h"

void FMediaTrackDemoModule::StartupModule()
{
    ISequencerModule& SequencerModule = FModuleManager::Get().LoadModuleChecked<ISequencerModule>("Sequencer");

    // 注册媒体轨道编辑器
    SequencerModule.RegisterTrackEditor(FOnCreateTrackEditor::CreateStatic(&FMediaTrackEditor::CreateTrackEditor));
    SequencerModule.RegisterTrackEditor(FOnCreateTrackEditor::CreateStatic(&FMediaPlayerPropertyTrackEditor::CreateTrackEditor));
}

void FMediaTrackDemoModule::ShutdownModule()
{
}

IMPLEMENT_MODULE(FMediaTrackDemoModule, MediaTrackDemo)
```

### 编译后效果

启动 Editor 并打开 Sequencer，在“添加轨道”菜单中将出现 **Media** 和 **Media Player Property** 选项。拖入一个 `UMediaSource` 资源即可创建媒体轨道。

## 模块依赖

### MediaCompositingEditor 模块的独特依赖

| 模块 | 用途 |
|---|---|
| `MediaAssets` | 提供 `UMediaPlayer`、`UMediaSource`、`UMediaTexture` 等核心媒体资产类 |
| `MovieScene` | Sequencer 的底层轨道/片段/数据模型 |
| `Sequencer` | Sequencer 编辑器框架，注册轨道编辑器、缩略图等功能 |
| `PropertyEditor` | 用于录制设置面板的 `IDetailsView` |

**说明**：`UnrealEd`、`Slate`、`SlateCore`、`CoreUObject` 等常见依赖已省略。`MediaCompositing`（Runtime）模块可能还需要 `Media` 和 `MediaUtils`，但作为编辑器使用，上述依赖已足够。

## 维护状态

### 近期更新

- 2025-10-16 `45eb317d` — [MediaCompositing] Sequencer Media Track: Fix crash on exit when running a sequencer in game mode.
- 2025-10-08 `c039eab2` — [MediaCompositing] Sequencer Media Track: Revisiting the frame alignment for frame accuracy.
- 2025-10-03 `1d7d0e17` — [MediaCompositing] Frame Accuracy Fix
- 2025-09-29 `63374779` — [Media Track] Fixing inconsistent behavior - take 2.
- 2025-09-24 `689c7036` — [Media Track] Fix "missing media texture" message mistakenly appearing on sections under a media player.

### 维护评价

- **创建时间**：2025-09-24，距今仅 1 个月，属于新插件。
- **最近更新**：最近一周内仍有提交（2025-10-16），修复了游戏模式下 Sequencer 退出时的崩溃问题，并持续完善帧精度对齐。
- **活跃度**：非常活跃，几乎每周都有功能性修复和改进。
- **推荐度**：该插件目前处于 UE5 主分支，主线版本稳定，建议在需要 Sequencer 媒体合成的项目中使用。由于是较新加入的功能，建议关注后续更新以获取更完善的特性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/MediaCompositing)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/sequencer-media-tracks/)（假设存在，实际请访问官方 Sequencer 媒体轨道文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/MediaCompositing/Tests)（若存在）