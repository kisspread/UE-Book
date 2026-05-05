# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `MetaHumanSequencer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-02-02 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方提供的 MetaHuman 工具包，旨在将真实世界的人脸表演（通常来自 iPhone 或专业摄像设备）转化为高质量的 MetaHuman 角色动画。它解决的核心问题是**高保真面部动画的捕获、处理和集成**。

该插件并非一个简单的动画播放器，而是一个完整的**面部动画制作管线**。它包含从原始视频/深度数据导入、面部特征点追踪、动画求解器、到最终在 Sequencer 中与音频、视频精确同步的全套工具。其存在是为了让影视、游戏开发者能够高效地将演员的细腻表演赋予数字人角色，实现“表演驱动动画”。

## 使用场景

- 你正在开发一个需要大量高质量面部动画的叙事驱动型游戏或虚拟制片项目 → 使用 MetaHuman Animator 从 iPhone 捕获的视频中提取动画数据。
- 你已经创建了一个 MetaHuman 角色，需要为其制作一段与配音演员口型完美匹配的对话动画 → 使用 MetaHuman Animator 的音频驱动面部动画功能。
- 你需要在一个 Sequencer 序列中，精确地将一段面部动画视频、对应的音频轨道以及生成的动画数据同步在一起进行编辑和预览 → 使用 MetaHuman Animator 提供的定制化 Sequencer 轨道和序列。
- 你需要批量处理大量的面部动画捕获数据 → 使用 MetaHumanBatchProcessor 模块。

## 蓝图用法

MetaHuman Animator 主要是一个编辑器和数据处理工具，其核心功能通过编辑器 UI 和 Sequencer 集成暴露。可蓝图化的节点相对较少，主要集中在序列和媒体控制上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Tick Rate` | 根据捕获数据的帧率设置序列的 Tick 速率，确保动画播放速度正确。 | `UMetaHumanSceneSequence` |
| `Get Playback Context` | 获取当前序列播放的上下文（通常是 World），用于正确解析绑定对象。 | `FMetaHumanSequencerPlaybackContext` |
| `Get MetaHuman Channel Ref` | 获取媒体 Section 中用于标记排除帧（如眨眼、遮挡）的布尔通道引用。 | `UMetaHumanMovieSceneMediaSection` |
| `Add Channel To Movie Scene Section` | 向媒体 Section 添加自定义的 MetaHuman 通道。 | `UMetaHumanMovieSceneMediaSection` |

### 使用示例（蓝图描述）

1.  **创建并配置 MetaHuman 序列**：
    *   使用 `Create MetaHuman Scene Sequence` 节点（或通过编辑器创建）生成一个 `UMetaHumanSceneSequence` 资产。
    *   在序列编辑器中，通过 `Add Track` 菜单添加 `MetaHuman Media Track` 和 `MetaHuman Audio Track`。
    *   将对应的视频媒体源和音频源分别拖拽到这两个轨道上。

2.  **同步与排除帧标记**：
    *   在 Sequencer 中选中媒体 Section，通过细节面板或右键菜单访问 `MetaHuman Movie Scene Media Section` 的属性。
    *   使用 `Get MetaHuman Channel Ref` 获取通道，然后通过蓝图或编辑器 UI 在该通道上添加关键帧（`true`/`false`），以标记视频中需要排除处理的帧（如演员闭眼的瞬间）。

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanSequence.h"
#include "MetaHumanMovieSceneMediaSection.h"
#include "MetaHumanMediaTrackEditor.h"
```

### 基本用法

以下代码演示了如何以编程方式创建一个 MetaHuman 序列并设置其帧率。

```cpp
// 来源：基于 MetaHumanSequence.h 和 MetaHumanSequencerModule.h 的推断用法
#include "MetaHumanSequence.h"
#include "MovieScene.h"

// 创建一个新的 MetaHuman 场景序列
UMetaHumanSceneSequence* NewSequence = NewObject<UMetaHumanSceneSequence>(GetTransientPackage(), NAME_None, RF_Transient);
if (NewSequence)
{
    // 获取其内部的 MovieScene 对象
    UMovieScene* MovieScene = NewSequence->GetMovieScene();
    if (MovieScene)
    {
        // 设置序列的显示帧率，例如 30fps
        MovieScene->SetDisplayRate(FFrameRate(30, 1));
        MovieScene->SetTickResolution(FFrameRate(30, 1));
    }

    // 如果有对应的捕获数据，可以设置正确的 Tick Rate
    // UFootageCaptureData* CaptureData = ...;
    // NewSequence->SetTickRate(CaptureData);
}
```

### 进阶用法

以下代码片段展示了如何访问和操作媒体 Section 中的排除帧通道。

```cpp
// 来源：基于 MetaHumanMovieSceneMediaSection.h 和 MetaHumanMediaSection.h 的推断用法
#include "MetaHumanMovieSceneMediaSection.h"
#include "MetaHumanMovieSceneChannel.h"

// 假设我们已经获取了一个 UMetaHumanMovieSceneMediaSection* MediaSection
UMetaHumanMovieSceneMediaSection* MediaSection = ...;
if (MediaSection)
{
    // 获取用于标记排除帧的布尔通道
    FMetaHumanMovieSceneChannel& ExclusionChannel = MediaSection->GetMetaHumanChannelRef();

    // 在特定时间（帧号）添加一个“排除”关键帧 (值为 true)
    FFrameNumber FrameToExclude(100); // 第100帧
    FKeyHandle NewKeyHandle = ExclusionChannel.GetData().AddKey(FrameToExclude, true);

    // 或者，评估某个时间点是否被排除
    bool bIsExcluded = false;
    FFrameTime TimeToCheck(150, 0.5f); // 第150帧的中间
    if (ExclusionChannel.Evaluate(TimeToCheck, bIsExcluded))
    {
        UE_LOG(LogTemp, Log, TEXT("Frame %d is excluded: %s"), TimeToCheck.GetFrame().Value, bIsExcluded ? TEXT("Yes") : TEXT("No"));
    }
}
```

## Demo 示例

一个最小的示例，展示如何创建一个 `UMetaHumanSceneSequence` 并查询其信息。

**MetaHumanSequenceDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "MetaHumanSequenceDemo.generated.h"

class UMetaHumanSceneSequence;

UCLASS()
class UMetaHumanSequenceDemoSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "MetaHuman Demo")
    UMetaHumanSceneSequence* CreateDemoSequence();

    UFUNCTION(BlueprintCallable, Category = "MetaHuman Demo")
    void PrintSequenceInfo(UMetaHumanSceneSequence* Sequence);
};
```

**MetaHumanSequenceDemo.cpp**
```cpp
#include "MetaHumanSequenceDemo.h"
#include "MetaHumanSequence.h"
#include "MovieScene.h"

UMetaHumanSceneSequence* UMetaHumanSequenceDemoSubsystem::CreateDemoSequence()
{
    UMetaHumanSceneSequence* DemoSequence = NewObject<UMetaHumanSceneSequence>(GetTransientPackage(), TEXT("DemoMetaHumanSeq"), RF_Transient);
    if (DemoSequence)
    {
        UMovieScene* MS = DemoSequence->GetMovieScene();
        if (MS)
        {
            MS->SetDisplayRate(FFrameRate(24, 1)); // 电影标准 24fps
            MS->SetPlaybackRangeLocked(true);
        }
    }
    return DemoSequence;
}

void UMetaHumanSequenceDemoSubsystem::PrintSequenceInfo(UMetaHumanSceneSequence* Sequence)
{
    if (!Sequence) return;

    UMovieScene* MS = Sequence->GetMovieScene();
    if (MS)
    {
        FFrameRate DisplayRate = MS->GetDisplayRate();
        UE_LOG(LogTemp, Warning, TEXT("MetaHuman Sequence '%s' Info:"), *Sequence->GetName());
        UE_LOG(LogTemp, Warning, TEXT("  Display Rate: %s"), *DisplayRate.ToPrettyText().ToString());
        UE_LOG(LogTemp, Warning, TEXT("  Playback Range: %s"), *MS->GetPlaybackRange().ToString());
    }
}
```

## 模块依赖

从 `MetaHumanSequencer.Build.cs` 分析，该模块依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `MovieScene` | Sequencer 的核心序列和轨道数据结构。 |
| `MediaAssets` | 处理媒体源（如视频文件）的基础模块。 |
| `MediaUtils` | 媒体播放相关的工具函数。 |
| `LevelSequence` | 与关卡序列（Level Sequence）相关的基础功能。 |
| `Sequencer` | Sequencer 编辑器的核心框架和 UI。 |
| `MediaCompositing` | 媒体合成相关的功能，用于在 Sequencer 中预览媒体。 |

## 维护状态

### 近期更新

```
- 2025-10-03 9803c443cfab 为包含对应 .gen.cpp 的源文件添加了 UE_INLINE_GENERATED_CPP_BY_NAME。
- 2025-09-15 08bc754e441a 将 MetaHuman 模块中的一些 FORCEINLINE 用法替换为 inline。
- 2025-08-20 52e3dac151e1 使用 UnrealCodeFixup 更新头文件，确保 dllstorage 位于方法/静态变量上而非类型上。
```

### 维护评价

MetaHuman Animator 是一个相对较新的插件（创建于 2024 年初），但作为 MetaHuman 工具链的核心部分，它得到了 Epic Games 的持续维护。从近期的提交记录看，更新主要集中在**代码质量、编译兼容性和内部重构**上（如内联函数优化、DLL 导出规范），而非新功能开发。这表明该插件已进入一个**稳定维护期**，核心功能已经完备。

**综合评价**：
- **活跃度**：中等。有定期维护性更新，但无重大功能变更。
- **稳定性**：高。作为官方工具，经过了充分测试。
- **推荐度**：**强烈推荐**给所有需要制作高质量 MetaHuman 面部动画的项目。它是目前 UE 内集成度最高、最官方的解决方案。
- **注意事项**：该插件默认未启用（`Installed: false`），需要在项目设置中手动启用。它依赖于 Epic 的专有技术栈，部分高级功能（如云处理）可能需要网络连接和 Epic 账户。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档]() (暂无公开的独立文档，主要参考 MetaHuman Creator 和 UE 官方教程)
- [测试用例]() (测试文件路径未在提供信息中明确，通常位于 `Engine/Plugins/MetaHuman/MetaHumanAnimator/Tests/` 或 `Engine/Tests/` 下)