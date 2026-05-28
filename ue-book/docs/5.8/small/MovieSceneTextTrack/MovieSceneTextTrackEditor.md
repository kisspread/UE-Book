# MovieSceneTextTrack

> Deprecated plugin. Text support moved to Movie Scene Tracks (built-in).（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 序列文本轨道 |
| 分类 | Text |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MovieSceneTextTrack` (Runtime), `MovieSceneTextTrackEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-06-09 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/MovieSceneTextTrack) | |

## 用途

该插件为 Unreal Engine 的 Sequencer（序列器）提供了一个专门的 `MovieSceneTextTrack`（电影场景文本轨道）。其核心功能是允许用户在 Sequencer 中为物体的 `FText` 类型属性（例如 UMG 的 Text Block 的 Text 属性、3D 文本组件的文本等）创建关键帧动画。它解决了在 Sequencer 中动画化本地化文本的需求，支持对包含本地化信息的文本进行关键帧编辑。

**重要提示**：此插件已被**废弃**。根据最后一次提交记录（`b074e345`），其文本轨道功能已迁移到内置的 `MovieSceneTracks` 模块中。这意味着在新版本的 UE5 中，相关功能是引擎原生支持的，不再需要此插件。此插件仅作为旧项目的兼容性保留。

## 使用场景

- **为旧项目提供兼容性**：如果你的项目基于此插件开发了包含文本动画的 Sequencer 序列，并且暂时不想迁移代码，可以继续使用此插件。
- **代码迁移参考**：作为已废弃功能的参考实现，帮助理解内置的文本轨道功能是如何工作的。

## 蓝图用法

此插件的核心功能集成在 Sequencer 编辑器中，其 API 主要面向 C++ 和编辑器扩展。在蓝图中，用户通过 Sequencer 的图形化界面（为文本属性添加轨道和关键帧）来使用此功能，而非直接调用蓝图节点。根据代码分析，未发现专门为蓝图暴露的 `UFUNCTION(BlueprintCallable)` 用于创建或操作文本轨道。

## C++ 用法

### 头文件引入

```cpp
// 如果需要操作运行时文本轨道数据
#include "MovieSceneTextTrack.h"

// 如果需要编辑器扩展（例如注册新的轨道类型）
#include "MovieSceneTextTrackEditor.h"
```

### 基本用法

以下代码展示了如何通过 C++ 为一个 UActorComponent 的文本属性在 Sequencer 中创建一个文本轨道（假设文本轨道功能尚未迁移，仍在使用此插件）。**注意：此插件已废弃，实际新功能实现请参考内置模块。**

```cpp
// 假设 UTextBlock* MyTextBlock 是一个 UMG 控件
// 该示例主要说明原理，实际编辑器操作通常通过UI完成

#include "MovieSceneTextTrack.h"
#include "MovieScene.h"
#include "MovieSceneSequence.h"
#include "ISequencer.h"

// 获取当前 Sequencer 实例（通常在编辑器工具或面板中）
// ISequencer* Sequencer = ...;

// 获取或创建当前 Sequencer 的 MovieScene
UMovieScene* MovieScene = Sequencer->GetFocusedMovieSceneSequence()->GetMovieScene();

// 为组件添加文本轨道
// 通常，轨道的添加由编辑器模块（MovieSceneTextTrackEditor）处理，
// 这里展示底层轨道对象的创建原理。
UMovieSceneTextTrack* TextTrack = Cast<UMovieSceneTextTrack>(MovieScene->FindTrack<UMovieSceneTextTrack>(MyTextBlock->GetFName()));
if (!TextTrack)
{
    TextTrack = MovieScene->AddTrack<UMovieSceneTextTrack>(MyTextBlock->GetFName());
}

// 文本轨道的具体操作（添加、设置关键帧）由 Sequencer UI 驱动
```

**来源**：代码逻辑推断自 `MovieSceneTextTrack` 模块的核心类定义及 Sequencer 文本支持的一般原理。

### 进阶用法

文本轨道的复杂功能（如处理文本本地化、缓存评估值）被封装在轨道和段（Section）类中。编辑器模块 (`MovieSceneTextTrackEditor`) 负责提供用户界面来编辑这些关键帧。一个典型的自定义编辑器扩展可能会：

1.  注册一个新的轨道类型（如果此插件未被废弃）。
2.  为轨道段（Section）创建自定义的编辑器界面，用于精确编辑本地化文本。

由于此插件已废弃，其进阶用法主要体现在维护旧代码或理解文本轨道的实现架构上。

## Demo 示例

以下示例展示了如何定义一个简单的组件，其文本属性理论上可以被 `MovieSceneTextTrack` 动画化。**再次强调，此插件已废弃，示例仅供理解原理。**

**MyTextComponent.h**
```cpp
#pragma once

#include "Components/ActorComponent.h"
#include "MyTextComponent.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMyTextComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UMyTextComponent();

    // 可被 Sequencer 的文本轨道动画化的 FText 属性
    UPROPERTY(BlueprintReadWrite, EditAnywhere, Category="Text")
    FText AnimatedText;

    UFUNCTION(BlueprintCallable, Category="Text")
    FText GetAnimatedText() const { return AnimatedText; }

    UFUNCTION(BlueprintCallable, Category="Text")
    void SetAnimatedText(FText InText) { AnimatedText = InText; }
};
```

**MyTextComponent.cpp**
```cpp
#include "MyTextComponent.h"

UMyTextComponent::UMyTextComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}
```

**使用说明（在 Sequencer 中 - 基于废弃插件的功能）**：
1.  将 `UMyTextComponent` 添加到场景中的一个 Actor 上。
2.  打开 Sequencer，将该 Actor 添加到序列中。
3.  在 Actor 的轨道区域，点击 “+ Track” -> “Text” -> “AnimatedText (FText)”。此选项由 `MovieSceneTextTrackEditor` 模块提供。
4.  在时间轴上点击添加关键帧，并在属性面板中编辑关键帧对应的 `FText` 值。
5.  播放序列时，组件的 `AnimatedText` 属性将随时间动画化。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MovieScene` | Sequencer 核心模块，提供轨道、片段等基础类。 |
| `MovieSceneTextTrack` | 本插件的运行时模块，定义文本轨道和段的核心类。 |
| `MovieSceneTracks` | 包含其他基础轨道类型，此插件的功能最终被迁移到此模块。 |
| `Sequencer` | Sequencer 编辑器 UI 逻辑。 |
| `LevelSequence` | 关卡序列资产相关支持。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-08-07 | `b074e345` | Movie Scene: migrate text track to movie scene tracks | 将文本轨道功能迁移到内置的 MovieSceneTracks 模块，此插件完成历史使命。 |
| 2025-06-13 | `b3edcb21` | Replace some usages of FORCEINLINE with inline in MovieScene modules. | 代码规范化，替换宏。 |
| 2024-12-02 | `027924bd` | Sequencer: Added missing CurveValueType typedefs, SupportsDefaults, and EvaluateChannel | Sequencer 核心API更新，插件随之适配。 |
| 2024-11-27 | `33517915` | - Movied previously committed sequencer changes for music mode into a new Musical Mode plugin | 功能重组，与音乐模式相关变更分离。 |
| 2024-10-23 | `6145872a` | MUSIC_IN_SEQUENCER [Initial Check-In] | Sequencer 音乐模式功能的初始提交。 |

### 维护评价

- **状态**：**已废弃 (Deprecated)**。
- **活动频率**：最后一次实质性更新（功能迁移）在2025年8月。之后的更新仅为适配引擎核心代码的例行修改。
- **推荐使用**：**不推荐**在新项目中使用。应直接使用引擎内置的 Sequencer 文本动画功能（位于 `MovieSceneTracks` 模块中）。对于老项目，如果仍依赖此插件，应考虑计划迁移到内置功能，以确保长期兼容性。
- **已知限制**：作为实验性且已废弃的插件，未来版本可能被彻底移除，且不再获得新功能支持。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/MovieSceneTextTrack)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/MovieSceneTextTrack/Tests) (如果存在)
- **功能迁移目标**：[MovieSceneTracks](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/MovieSceneTracks) (内置模块)