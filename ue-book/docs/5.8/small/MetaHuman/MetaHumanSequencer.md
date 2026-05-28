# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（动画性能资产） |
| 模块 | `MetaHumanSequencer` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanCaptureSource` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 未知 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是一个完整的工具包，旨在将现实世界的面部表演（通过摄像头或音频）捕获、处理并应用到虚幻引擎中的 MetaHuman 角色上。它不仅仅是单一工具，而是一整套包含数据捕获（`MetaHumanCaptureSource`）、面部追踪（`MetaHumanFaceContourTracker`）、动画求解（`MetaHumanFaceAnimationSolver`）、网格体适配（`MetaHumanFaceFittingSolver`）、身份管理（`MetaHumanIdentity`）、性能动画（`MetaHumanPerformance`）以及序列器集成（`MetaHumanSequencer`）的流水线。

其核心目的是：**将原始表演数据（视频、音频）转化为高质量、可在引擎中实时驱动或离线渲染的 MetaHuman 面部动画资产**，解决影视、游戏及虚拟制片领域中数字人表演的真实感问题。

## 使用场景

- **虚拟制片与数字人表演**：你需要将真人演员的面部表演实时或离线应用到一个高保真度的 MetaHuman 角色上，用于电影预览或最终渲染。
- **语音驱动面部动画**：你拥有一段音频录音，希望自动生成对应的口型和面部表情动画，用于游戏对话或快速内容制作。
- **精细化的动画编辑**：你已经通过其他方式获得了一段面部动画，需要在虚幻引擎的序列器中对其进行精细的编辑、清理或混合。
- **批量处理与资产创建**：你需要为一个项目中的多个角色快速生成和配置面部动画资产。

## 蓝图用法

该插件主要为动画师和后期制作人员提供工作流工具，其核心蓝图 API 聚焦于序列器集成与动画通道的操控。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Evaluate` | 在指定时间评估该布尔通道的值，用于驱动面部动画中的特定效果（如眨眼、张嘴）的开关状态。 | `FMetaHumanMovieSceneChannel` |
| `BindPossessableObject` | 将一个 UObject（如 MetaHuman 角色）绑定到序列中的特定 ID，以便序列可以驱动其属性。 | `UMetaHumanSceneSequence` |
| `GetMetaHumanChannelRef` | 获取媒体片段中用于控制 MetaHuman 特有动画效果（如排除帧）的布尔通道引用。 | `UMetaHumanMovieSceneMediaSection` |
| `OnKeyAddedEventDelegate` | 返回一个委托，当在 MetaHuman 通道上添加关键帧时广播，可用于响应性更新UI或逻辑。 | `UMetaHumanMovieSceneMediaSection` |

### 使用示例（蓝图描述）

1.  **创建并绑定序列**：在蓝图中，首先使用 `Spawn Actor from Class` 或通过 `Load Asset` 加载一个 `UMetaHumanSceneSequence`。然后，调用 `BindPossessableObject` 函数，将你的 MetaHuman 角色 Actor 绑定到序列上。
2.  **播放与控制**：在需要时，将这个 `UMetaHumanSceneSequence` 对象连接到 `Level Sequence Player` 组件的 `Sequence` 属性上，即可播放由 MetaHuman Animator 管理的复杂面部动画。
3.  **读取或修改通道数据**：在编辑器工具或运行时蓝图中，通过序列器上下文获取到 `UMetaHumanMovieSceneMediaSection` 对象后，调用 `GetMetaHumanChannelRef` 获取通道，然后使用其 `GetData` 方法返回的 `TMovieSceneChannelData` 接口来添加、删除或查询关键帧。

## C++ 用法

### 头文件引入

```cpp
// 访问序列和通道核心功能
#include "MetaHumanSequencerModule.h"
#include "MetaHumanSequence.h"
#include "MetaHumanMovieSceneChannel.h"

// 访问媒体轨道和片段的自定义版本
#include "MetaHumanMovieSceneMediaTrack.h"
#include "MetaHumanMovieSceneMediaSection.h"
```

### 基本用法

以下示例展示了如何以编程方式创建一个 `UMetaHumanSceneSequence` 并评估其内部的一个布尔通道。
*(注意：此为基于头文件推断的示例，非实际测试用例)*

```cpp
// 假设你已经有了一个已加载的 MetaHuman 角色 Actor
AActor* MyMetaHumanActor = ...;

// 1. 创建 MetaHuman 序列对象
UMetaHumanSceneSequence* NewSequence = NewObject<UMetaHumanSceneSequence>(GetTransientPackage());

// 2. 将角色绑定到序列
if (NewSequence && MyMetaHumanActor)
{
    FGuid ObjectId = FGuid::NewGuid();
    NewSequence->BindPossessableObject(ObjectId, *MyMetaHumanActor, MyMetaHumanActor->GetWorld());
}

// 3. 获取序列中的 MovieScene 并添加一个自定义的媒体轨道和片段
// （此部分逻辑通常发生在编辑器模块中，此处仅为逻辑示意）
UMovieScene* MovieScene = NewSequence->GetMovieScene();
UMetaHumanMovieSceneMediaTrack* NewTrack = MovieScene->AddTrack<UMetaHumanMovieSceneMediaTrack>();
UMetaHumanMovieSceneMediaSection* NewSection = Cast<UMetaHumanMovieSceneMediaSection>(NewTrack->CreateNewSection());

// 4. 操作片段中的 MetaHuman 通道
FMetaHumanMovieSceneChannel& MHChannel = NewSection->GetMetaHumanChannelRef();

// 添加一个关键帧：在第 0 帧，值为 true (例如，表示一个“激活”状态)
TArray<FFrameNumber> KeyTimes;
KeyTimes.Add(0);
TArray<bool> KeyValues;
KeyValues.Add(true);
MHChannel.GetData().AddKeys(KeyTimes, KeyValues);

// 评估通道在第 0 帧的值
bool bCurrentValue = false;
if (MHChannel.Evaluate(FFrameTime(0), bCurrentValue))
{
    // bCurrentValue 此时应为 true
    UE_LOG(LogTemp, Log, TEXT("Channel value at frame 0: %s"), bCurrentValue ? TEXT("True") : TEXT("False"));
}
```

### 进阶用法

结合排除帧信息进行更复杂的动画管理。`UMetaHumanSceneSequence` 提供了 `GetExcludedFrameInfo` 委托，允许查询哪些帧在动画处理中被排除（例如，因为角色头部未在画面内）。

```cpp
// 获取序列的排除帧信息
FFrameRate SourceRate;
FFrameRangeMap ExcludedFramesMap;
int32 MediaStartFrame;
TRange<FFrameNumber> ProcessingLimit;

NewSequence->GetExcludedFrameInfo.ExecuteIfBound(SourceRate, ExcludedFramesMap, MediaStartFrame, ProcessingLimit);

// 可以使用这些信息来优化动画回放，或跳过不需要处理的帧
if (ExcludedFramesMap.Num() > 0)
{
    UE_LOG(LogTemp, Warning, TEXT("Sequence has %d excluded frame ranges."), ExcludedFramesMap.Num());
}
```

## Demo 示例

一个最小化的示例，展示如何定义一个包含 MetaHuman 序列的 Actor。
**MetaHumanAnimDemoActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MetaHumanSequence.h"
#include "MetaHumanAnimDemoActor.generated.h"

UCLASS()
class AMetaHumanAnimDemoActor : public AActor
{
	GENERATED_BODY()
	
public:	
	AMetaHumanAnimDemoActor();

	virtual void BeginPlay() override;

	// 要播放的 MetaHuman 序列资产
	UPROPERTY(EditAnywhere, Category = "MetaHuman")
	TObjectPtr<UMetaHumanSceneSequence> MetaHumanSequence;

private:
	UPROPERTY()
	TObjectPtr<ULevelSequencePlayer> SequencePlayer;
};
```

**MetaHumanAnimDemoActor.cpp**
```cpp
#include "MetaHumanAnimDemoActor.h"
#include "LevelSequencePlayer.h"
#include "LevelSequenceActor.h"

AMetaHumanAnimDemoActor::AMetaHumanAnimDemoActor()
{
	PrimaryActorTick.bCanEverTick = false;
}

void AMetaHumanAnimDemoActor::BeginPlay()
{
	Super::BeginPlay();

	if (MetaHumanSequence)
	{
		// 创建序列播放器
		FMovieSceneSequencePlaybackSettings Settings;
		SequencePlayer = ULevelSequencePlayer::CreateLevelSequencePlayer(
			GetWorld(),
			MetaHumanSequence,
			Settings,
			/* ... */ // 可能需要 ALLevelSequenceActor 引用
		);

		// 绑定自身为序列控制的对象（假设序列被设计为控制拥有该Actor的实体）
		if (SequencePlayer)
		{
			FGuid ObjectId = FGuid::NewGuid();
			MetaHumanSequence->BindPossessableObject(ObjectId, *this, GetWorld());
			SequencePlayer->Play();
		}
	}
}
```

## 模块依赖

以下模块是使用 MetaHuman Animator 功能时，你的项目模块可能需要依赖的**独特模块**（依赖于你使用的具体功能）：

| 模块 | 用途 |
|---|---|
| `MetaHumanSequencer` | 如果你需要在自己的代码中与 MetaHuman 序列、通道或自定义轨道进行交互。 |
| `MetaHumanCore` | MetaHuman 插件的核心基础功能模块。 |
| `MetaHumanIdentity` | 如果你需要以编程方式管理 MetaHuman 角色的身份资产（如设置目标网格体）。 |
| `MetaHumanCaptureSource` | 如果你需要集成或扩展面部捕获数据源。 |

*注意：该插件本身依赖大量的 `UnrealEd`, `Slate`, `Core` 等标准模块，但这些在编写 Runtime 逻辑时通常不需要显式依赖。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用身体追踪时，禁用关卡序列导出功能，以避免数据冲突。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复了 MetaHuman 角色上的渲染伪影问题。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 在身体追踪模式下过滤可视化的辅助对象，保持视图清晰。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 为已存在的网格体支持导出动画序列。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复了序列器相关的缓存问题，提升稳定性和性能。 |

### 维护评价

- **活跃维护**：尽管创建时间未知，但从近期密集的 git 提交历史（集中在 2026 年 5 月）来看，该插件正在被积极开发和维护。最近的更新主要集中在功能完善（如身体追踪集成）、渲染问题修复和稳定性提升上。
- **实验性/稳定性**：`.uplugin` 中 `IsBetaVersion` 和 `IsExperimentalVersion` 均为 `false`，表明插件已达到正式发布版本的稳定水平。
- **推荐使用**：对于需要在虚幻引擎中进行高质量 MetaHuman 面部动画制作的项目，**强烈推荐使用**。它是 Epic Games 官方提供的工具，与引擎深度集成，且维护活跃。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- 官方文档：无（`.uplugin` 中 `DocsURL` 为空）
- 测试用例：无公开路径（测试可能位于插件内部的私有测试模块中）