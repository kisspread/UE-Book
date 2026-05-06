# Subtitles and Closed Captions

> Standalone plugin for displaying Subtitles and Closed Captions

| 属性 | 值 |
|---|---|
| 中文名 | 字幕与封闭式字幕 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、字幕数据资产、Sequencer 轨道、迁移工具） |
| 模块 | `SubtitlesAndClosedCaptions` (Runtime), `SubtitlesAndClosedCaptionsEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-25 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/SubtitlesAndClosedCaptions) | |

---

## 用途

该插件提供了一个独立的字幕与封闭式字幕系统，完全脱离旧的 `DialogueWave` / `DialogueVoice` 框架。它包含：

- **字幕资产** (`USubtitleAssetUserData`)：存储结构化字幕数据（文本、时间码、样式等）。
- **运行时子系统** (`USubtitlesSubsystem`)：负责字幕的播放、暂停、停止、队列管理及 UI 显示。
- **编辑器集成**：在内容浏览器中创建字幕资产，在 Sequencer 中直接拖拽字幕资产生成轨道和片段，并提供旧版字幕的迁移工具。

该插件解决了以下问题：

- UE 旧版字幕系统绑定在 DialogueWave 上，不够灵活且缺乏独立的可重用资产。
- 需要严格时间线控制和多语言支持的项目（如过场动画、直播、无障碍功能）。
- 希望将字幕系统与音频系统解耦，允许字幕独立于声音播放。

---

## 使用场景

- **游戏过场动画**：在播放视频或音频时显示同步字幕。
- **实时解说/语音聊天**：为多人游戏中的语音聊天提供实时字幕。
- **无障碍功能**：为听障玩家提供完整的封闭式字幕体验。
- **多语言本地化**：字幕资产可直接使用 LocText 或手动翻译，便于本地化部署。

---

## 蓝图用法

> 基于插件 Runtime 模块的公开接口（从 Git 描述和标准实现推测），实际节点名称以插件安装后的蓝图库为准。

### 核心节点（运行时系统）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Queue Subtitles From Asset` | 将一个 `USubtitleAssetUserData` 中的所有字幕条目加入播放队列 | `USubtitlesSubsystem` |
| `Stop Subtitles In Asset` | 停止指定资产中正在播放的字幕 | `USubtitlesSubsystem` |
| `Set Subtitle Widget` | 热切换用于显示字幕的 UMG Widget（支持在运行时更换样式） | `USubtitlesSubsystem` |
| `On Subtitle Started` / `On Subtitle Finished` | 字幕开始/结束时的多播委托 | `USubtitlesSubsystem` |

### 编辑器操作（Call in Editor）

在内容浏览器中右键字幕资产时，可通过 `Asset Action Utility` 执行以下操作：

| 操作 | 说明 |
|---|---|
| `Convert Basic Overlays To Subtitles` | 将 `UBasicOverlays` 资产转换为新的字幕资产格式 |
| `Add Blank Subtitle` | 在当前字幕资产中追加一条空白条目 |
| `Remove Legacy Subtitles` | 从当前世界中移除所有旧版 DialogueWave 字幕 |
| `Convert Legacy Subtitles` | 将场景中存在的旧版字幕转换为新插件格式 |

---

## C++ 用法

### 头文件引入

```cpp
#include "SubtitlesAndClosedCaptions.h"          // 运行时模块主头文件
#include "Subtitles/SubtitlesAndClosedCaptionsDelegates.h" // 委托定义
#include "Subtitles/SubtitleAssetUserData.h"     // 字幕资产类
#include "Subtitles/SubtitlesSubsystem.h"        // 字幕子系统
```

### 基本用法

```cpp
// 获取字幕子系统
USubtitlesSubsystem* SubtitleSystem = GEngine->GetEngineSubsystem<USubtitlesSubsystem>();

// 加载一个字幕资产
USubtitleAssetUserData* MySubtitleAsset = LoadObject<USubtitleAssetUserData>(nullptr, TEXT("/Game/Subtitles/MySubtitle.MySubtitle"));
if (MySubtitleAsset)
{
    // 将资产中所有字幕条目加入队列
    SubtitleSystem->QueueSubtitlesFromAsset(MySubtitleAsset);
}

// 停止该资产的字幕播放
SubtitleSystem->StopSubtitlesInAsset(MySubtitleAsset);

// 监听委托
SubtitleSystem->OnSubtitleStarted.AddDynamic(this, &AMyActor::OnSubtitleStart);
```

### 进阶用法

#### 自定义字幕 Widget

通过继承 `USubtitlesSubsystem` 的 `SetSubtitleWidget` 方法动态替换 UI：

```cpp
// 在游戏开始时设置自定义 Widget
TSubclassOf<UUserWidget> MyWidgetClass = LoadClass<UUserWidget>(nullptr, TEXT("/Game/UI/WBP_MySubtitles.WBP_MySubtitles_C"));
if (MyWidgetClass)
{
    SubtitleSystem->SetSubtitleWidget(MyWidgetClass);
}
```

#### 在 Sequencer 中创建字幕轨道（编辑器）

```cpp
// 使用 FSubtitlesTrackEditor 提供的拖拽支持
// 当用户从内容浏览器拖拽字幕资产到 Sequencer 轨道区时，自动创建 UMovieSceneSubtitlesTrack 和片段。
// 后台调用 AddNewSubtitle() 或 AddNewAttachedSubtitle() 实现关键帧写入。
```

---

## Demo 示例

完整的最小示例，展示如何在运行时加载并播放字幕资产。

### `MySubtitlePlayer.h`

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Subtitles/SubtitlesSubsystem.h"
#include "MySubtitlePlayer.generated.h"

UCLASS()
class AMySubtitlePlayer : public AActor
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Subtitles")
    USubtitleAssetUserData* SubtitleAsset;

    UFUNCTION(BlueprintCallable, CallInEditor, Category = "Subtitles")
    void PlaySubtitles();

    UFUNCTION(BlueprintCallable, CallInEditor, Category = "Subtitles")
    void StopSubtitles();

protected:
    USubtitlesSubsystem* SubtitleSystem;
};

```

### `MySubtitlePlayer.cpp`

```cpp
#include "MySubtitlePlayer.h"
#include "Engine/Engine.h"

void AMySubtitlePlayer::PlaySubtitles()
{
    if (!SubtitleAsset || !SubtitleSystem)
    {
        SubtitleSystem = GEngine->GetEngineSubsystem<USubtitlesSubsystem>();
    }
    if (SubtitleSystem && SubtitleAsset)
    {
        SubtitleSystem->QueueSubtitlesFromAsset(SubtitleAsset);
    }
}

void AMySubtitlePlayer::StopSubtitles()
{
    if (SubtitleSystem && SubtitleAsset)
    {
        SubtitleSystem->StopSubtitlesInAsset(SubtitleAsset);
    }
}
```

---

## 模块依赖

| 模块 | 用途 |
|---|---|
| `SubtitlesAndClosedCaptions` | 运行时核心（字幕资产、子系统、UI） |
| `MovieScene` | Sequencer 轨道与片段支持 |
| `MovieSceneTracks` | 通用轨道编辑器支持 |
| `Sequencer` | 编辑器轨道创建与 UI |
| `ContentBrowser` | 资产拖拽和选择 |
| `AssetTools` | 资产定义和工厂注册 |
| `AssetDefinition` | 字幕资产的自定义操作 |

> 以上依赖基于代码分析推断。实际 `.Build.cs` 中可能包含更多或更少的依赖。

---

## 维护状态

### 近期更新

- 2025-10-01 `12c746a0` — Subtitles: Add StopSubtitlesInAsset BP function, remove External timing as an option for QueueSubtitles
- 2025-09-29 `55041f2a` — [Subtitles] Adds a function to USubtitlesSubsystem for hot-swapping the Widget.
- 2025-09-29 `167c097b` — [Subtitles] Ensure plugin subtitles don't autoplay from DialogueWaves without the migration cvar set
- 2025-09-25 `2e75074a` — Add a Blueprint node for queueing all subtitles in a USubtitleAssetUserData.
- 2025-09-25 `3a00635c` — [Backout] - CL46211601

### 维护评价

该插件是 **实验性** 版本，创建时间仅几天（2025-09-25），但提交频率非常高（几乎每天都有功能更新）。从提交信息看，团队正在积极添加核心功能（蓝图节点、Widget 热切换、迁移支持）并修复回归。由于仍处于早期开发阶段，API 可能不稳定，不建议在生产项目中使用。推荐用于原型开发或评估新字幕系统。

---

## 相关链接

- [源码（主仓库 5.7 分支）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/SubtitlesAndClosedCaptions)
- [运行时模块头文件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/SubtitlesAndClosedCaptions/Source/SubtitlesAndClosedCaptions/Public)
- [编辑器模块头文件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/SubtitlesAndClosedCaptions/Source/SubtitlesAndClosedCaptionsEditor/Public)