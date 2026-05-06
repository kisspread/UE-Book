# Subtitles and Closed Captions

> Standalone plugin for displaying Subtitles and Closed Captions

| 属性 | 值 |
|---|---|
| 中文名 | 字幕与隐藏式字幕 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、用户控件、测试资源） |
| 模块 | `SubtitlesAndClosedCaptions` (Runtime), `SubtitlesAndClosedCaptionsEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-25 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/SubtitlesAndClosedCaptions) | |

## 用途

该插件提供了一个**独立且可扩展的字幕和隐藏式字幕（Closed Captions）显示系统**。相比于引擎内建的手动播放对白字幕方式，它支持：

- 通过 `USubtitlesSubsystem`（WorldSubsystem）集中管理字幕队列，按优先级和延迟偏移自动切换显示。
- 与 **MovieScene** 深度集成，允许在 Sequence 轨道上精确安排字幕起止时间，并响应播放、暂停、跳跃等状态变化。
- 自动为 **DialogueWave**（通过 `UDialogueSoundWaveProxy`）产生的 `ActiveSound` 排队字幕，无需手动触发。
- 提供 **可替换的 Widget**（`USubtitleWidget`），方便美术和设计师定制字幕的样式、字体、边框等。
- 支持**三种字幕类型**：对话（Dialog）、说明（Description）、隐藏式字幕（Caption），可分别控制文本块和边框显示。

该插件解决了官方字幕系统缺乏统一管理、无法在 Sequencer 中直接使用、样式难以自定义等问题，适合任何需要高质量字幕支撑的游戏或交互体验。

## 使用场景

- **剧情过场动画**：在电影序列（MovieScene）中按秒级精度显示对白字幕和环境说明。
- **2D/3D 横版叙事游戏**：角色说话时自动弹出字幕，并支持持续时间的灵活控制（内部计时或外部计时）。
- **无障碍支持**：为听障玩家提供隐藏式字幕，描述音效、背景语音等非对白信息。
- **交互式对话系统**：与 DialogueWave 和声音系统自动联动，设计人员只需放置声音即可触发字幕。
- **动态 UI 定制**：不同角色或语言使用不同字体/颜色，通过替换 `USubtitleWidget` 子类轻松切换样式。

## 蓝图用法

以下蓝图节点均定义在 `USubtitlesBlueprintFunctionLibrary` 中，可通过“蓝图→函数库→SubtitlesLibrary”分类找到。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Queue Subtitles From Asset` | 将整个 `USubtitleAssetUserData` 中的字幕条目全部加入队列，每个条目按自身的 `StartOffset` 和 `Duration` 内部计时 | `USubtitlesBlueprintFunctionLibrary` |
| `Queue Subtitle` | 单独将一个 `FSubtitleAssetData` 结构排入队列，可指定计时方式为内部计时或外部计时 | `USubtitlesBlueprintFunctionLibrary` |
| `Stop Subtitles In Asset` | 停止指定资产中所有已经加入队列或正在显示的（含延迟未显示的）字幕 | `USubtitlesBlueprintFunctionLibrary` |
| `Stop Subtitle` | 停止单个 `FSubtitleAssetData` 对应的字幕 | `USubtitlesBlueprintFunctionLibrary` |
| `Stop All Subtitles` | 立即停止当前所有的字幕显示，包括延迟队列中的条目 | `USubtitlesBlueprintFunctionLibrary` |
| `Is Subtitle Active` | 检查某个 `FSubtitleAssetData` 是否正在显示（不一定队列中，仅正在显示） | `USubtitlesBlueprintFunctionLibrary` |
| `Replace Subtitle Widget` | 运行时动态替换全局使用的字幕控件，传入新的 `USubtitleWidget` 子类 | `USubtitlesBlueprintFunctionLibrary` |

### 使用示例（蓝图描述）

1. **播放序列中的字幕**  
   - 在 Sequencer 中添加“Subtitles Track”（由 `UMovieSceneSubtitlesTrack` 提供），然后为每个需要显示字幕的时间段添加 `UMovieSceneSubtitleSection`，并将 `Subtitle` 属性指定为一个 `USubtitleAssetUserData` 资产。  
   - 播放序列时，系统自动在指定区间内显示/隐藏字幕，无需额外蓝图逻辑。

2. **通过蓝图手动触发字幕**  
   - 准备一个 `USubtitleAssetUserData` 数据资产，在“字幕数组”中填入若干条 `FSubtitleAssetData`（含文本、类型、偏移、持续时长等）。  
   - 调用 `Queue Subtitles From Asset` 节点，传入该资产。  
   - 如需中途停止，调用 `Stop Subtitles In Asset`。

3. **监听字幕事件**  
   - 在关卡蓝图中绑定“字幕委托”（`OnSubtitleStarted` / `OnSubtitleEnded`），以实现自定义反馈（如角色口型动画）。这些委托通过 `FSubtitlesAndClosedCaptionsDelegates` 向外广播，蓝图端使用“为特定委托添加自定义事件”即可绑定。

## C++ 用法

### 头文件引入

```cpp
// 核心功能
#include "SubtitlesSubsystem.h"
#include "SubtitlesBlueprintFunctionLibrary.h"
#include "Subtitles/SubtitlesAndClosedCaptionsDelegates.h"

// 如果需要操作 USubtitleAssetUserData
#include "SubtitleAssetUserData.h" // 假设存在，实际可能需要自定义资产头文件

// MovieScene 集成
#include "MovieSceneSubtitlesTrack.h"
#include "MovieSceneSubtitleSection.h"
```

### 基本用法

```cpp
// 1. 获取 WorldSubsystem
if (UWorld* World = GetWorld())
{
    USubtitlesSubsystem* SubtitleSys = World->GetSubsystem<USubtitlesSubsystem>();
    if (SubtitleSys)
    {
        // 2. 构造一条字幕数据
        FSubtitleAssetData SubtitleData;
        SubtitleData.Text = FText::FromString("Hello from C++!");
        SubtitleData.Type = ESubtitleType::Dialog;   // 对话类型
        SubtitleData.StartOffset = 0.f;               // 立即开始
        SubtitleData.Duration = 3.0f;                 // 显示3秒
        SubtitleData.Priority = 0;

        // 3. 排入队列（采用内部计时）
        FQueueSubtitleParameters Params;
        Params.SubtitleData = SubtitleData;
        // Params.Duration = 3.0f; // 已经包含在 SubtitleData 中，但仍可覆盖
        SubtitleSys->QueueSubtitle(Params, ESubtitleTiming::InternallyTimed);
    }
}
```

**说明**：该例展示了如何用 C++ 手动创建字幕并加入队列。`FQueueSubtitleParameters` 结构体提供额外的参数（如覆盖时长），但最简用法只需填充 `SubtitleData`。

### 进阶用法

```cpp
// 与 MovieScene 配合，创建轨道上的字幕 Section
UMovieSceneSubtitlesTrack* Track = MovieScene->AddTrack<UMovieSceneSubtitlesTrack>(BoundObject);
if (Track)
{
    // 获取 USubtitleAssetUserData 资产（假设已加载）
    USubtitleAssetUserData* SubtitleAsset = LoadObject<USubtitleAssetUserData>(nullptr, TEXT("/Game/Subtitles/MySubtitleAsset.MySubtitleAsset"));
    if (SubtitleAsset)
    {
        FFrameNumber StartFrame(100);   // 第100帧开始
        UMovieSceneSubtitleSection* Section = Track->AddNewSubtitle(*SubtitleAsset, StartFrame);
        // 设置 section 的时长（自动计算或手动设置）
        Section->SetEndFrame(StartFrame + 300);
    }
}

// 监听字幕状态变化（通过委托）
FSubtitlesAndClosedCaptionsDelegates::OnSubtitleStarted.AddLambda([](const FSubtitleAssetData& Subtitle)
{
    UE_LOG(LogTemp, Log, TEXT("Subtitle started: %s"), *Subtitle.Text.ToString());
});
FSubtitlesAndClosedCaptionsDelegates::OnSubtitleEnded.AddLambda([](const FSubtitleAssetData& Subtitle)
{
    // 取消角色口型等
});
```

**说明**：进阶用法展示了如何在 C++ 中动态创建 MovieScene 字幕轨道并与全局委托交互，实现字幕生命周期回调。

## Demo 示例

以下示例创建一个简单的 `ASubtitleDemoActor`，附着于关卡，开始时自动播放一条字幕。

### DemoActor.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SubtitlesSubsystem.h"
#include "Subtitles/SubtitlesAndClosedCaptionsDelegates.h"
#include "SubtitleAssetUserData.h"
#include "SubtitleDataComponent.h"
#include "SubtitleWidget.h"

#include "SubtitleDemoActor.generated.h"

UCLASS()
class ASubtitleDemoActor : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;

    UFUNCTION()
    void OnSubtitleStarted(const FSubtitleAssetData& Subtitle);

    UFUNCTION()
    void OnSubtitleFinished(const FSubtitleAssetData& Subtitle);

private:
    void QueueDemoSubtitle();
};
```

### DemoActor.cpp

```cpp
#include "SubtitleDemoActor.h"
#include "Engine/World.h"

void ASubtitleDemoActor::BeginPlay()
{
    Super::BeginPlay();

    // 绑定全局字幕事件
    FSubtitlesAndClosedCaptionsDelegates::OnSubtitleStarted.AddUObject(this, &ASubtitleDemoActor::OnSubtitleStarted);
    FSubtitlesAndClosedCaptionsDelegates::OnSubtitleEnded.AddUObject(this, &ASubtitleDemoActor::OnSubtitleFinished);

    QueueDemoSubtitle();
}

void ASubtitleDemoActor::QueueDemoSubtitle()
{
    USubtitlesSubsystem* SubtitleSys = GetWorld()->GetSubsystem<USubtitlesSubsystem>();
    if (!SubtitleSys) return;

    // 直接使用蓝图函数库简化（需要 include SubtitlesBlueprintFunctionLibrary.h）
    FSubtitleAssetData DemoData;
    DemoData.Text = FText::FromString(TEXT("This is a demo subtitle from C++!"));
    DemoData.Type = ESubtitleType::Caption;
    DemoData.StartOffset = 0.5f;  // 延迟0.5秒开始
    DemoData.Duration = 5.0f;
    DemoData.Priority = 1;

    FQueueSubtitleParameters Params;
    Params.SubtitleData = DemoData;
    SubtitleSys->QueueSubtitle(Params, ESubtitleTiming::InternallyTimed);
}

void ASubtitleDemoActor::OnSubtitleStarted(const FSubtitleAssetData& Subtitle)
{
    UE_LOG(LogTemp, Log, TEXT("Subtitle started: %s"), *Subtitle.Text.ToString());
}

void ASubtitleDemoActor::OnSubtitleFinished(const FSubtitleAssetData& Subtitle)
{
    UE_LOG(LogTemp, Log, TEXT("Subtitle finished: %s"), *Subtitle.Text.ToString());
}
```

**说明**：该演示在 BeginPlay 时排入一条隐藏式字幕，并在字幕开始/结束时输出日志。实际使用时可将 `DemoActor` 放置到关卡中即可观察效果。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MovieScene` | 提供序列轨道支持（`UMovieSceneSubtitlesTrack`、`UMovieSceneSubtitleSection`）及实体系统评估 |
| `AudioEngine` | 订阅 `IActiveSoundUpdateInterface`，自动监听 `DialogueWave` 声音创建事件 |
| `UMG` | 提供 `USubtitleWidget` 基类（`UUserWidget`），用于在视口显示字幕文本 |
| `DeveloperSettings` | 提供 `USubtitlesSettings` 全局配置类（运行时设置） |

> **注意**：`UMG` 和 `DeveloperSettings` 属于常见依赖（大部分插件均会使用），此处列出仅为说明该插件确实依赖它们。

## 维护状态

### 近期更新

- 2025-10-01 `12c746a0` Subtitles: Add StopSubtitlesInAsset BP function, remove External timing as an option for QueueSubtitles
- 2025-09-29 `55041f2a` [Subtitles] Adds a function to USubtitlesSubsystem for hot-swapping the Widget.
- 2025-09-29 `167c097b` [Subtitles] Ensure plugin subtitles don't autoplay from DialogueWaves without the migration cvar set
- 2025-09-25 `2e75074a` Add a Blueprint node for queueing all subtitles in a USubtitleAssetUserData.
- 2025-09-25 `3a00635c` [Backout] - CL46211601

### 维护评价

- **创建时间**：2025-09-25，至今不足 2 个月，属于全新插件。
- **更新频率**：发布后几乎每天都有功能性提交，开发活跃。
- **内容**：不断添加蓝图节点、修复边缘情况、增加热替换 Widget 等实用性功能。
- **风险标签**：⚠️ 实验性（IsExperimentalVersion = true），API 可能发生较频繁变动。
- **推荐使用**：适合新项目快速集成字幕系统，但需注意后续版本兼容性。建议在项目初期启用并跟踪插件更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/SubtitlesAndClosedCaptions)
- [测试用例（插件内置）](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/SubtitlesAndClosedCaptions/Source/SubtitlesAndClosedCaptions/Private/SubtitlesSubsystem.cpp)（搜索 `WITH_DEV_AUTOMATION_TESTS` 块）
- [官方文档](https://docs.unrealengine.com/)（暂无针对该插件的独立页面，可参考通用字幕文档）