# Actor Sequence

> Runtime for embedded actor sequences（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | Actor 序列 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ActorSequence` (Runtime), `ActorSequenceEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2017-09-07 |
| 年龄标签 | 🏛️ 文物（约 10 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/ActorSequence) | |

## 用途

Actor Sequence 插件提供了一种轻量级的序列化方案，允许将 Sequencer 序列直接嵌入（Embed）到 Actor 蓝图中，而不是创建独立的 Level Sequence 资产。它的核心是 `UActorSequenceComponent`，用于存储和管理一个内嵌的 `UActorSequence`。此序列可以驱动 Actor 自身及其子对象的属性和变换动画。其主要解决的问题是：对于那些自身就是一个完整动画单元（例如，一个带有复杂开合动画的宝箱、一个带有机头旋转动画的飞行器）的 Actor，无需额外的资产文件，即可实现其内部动画逻辑，便于打包和重用。

## 使用场景

- 你在制作一个需要内置播放动画（如开门、爆炸、机关启动）的 Actor，且希望该动画成为 Actor 的一部分。
- 你需要一个自包含的 Actor，不依赖外部的 Level Sequence 资产文件。
- 你正在编写 Actor 蓝图，并希望在蓝图编辑器中直接嵌入和编辑其动画序列，而不是跳转到独立的 Level Sequence 编辑器。

## 蓝图用法

核心功能通过 `UActorSequenceComponent` 暴露。你可以在 Actor 蓝图中添加此组件。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Play` | 正向播放嵌入的 Actor 序列。 | `UActorSequenceComponent` |
| `PlayReverse` | 反向播放嵌入的 Actor 序列。 | `UActorSequenceComponent` |
| `Stop` | 停止序列播放。 | `UActorSequenceComponent` |
| `SetPlaybackPosition` | 跳转到序列的指定时间点。 | `UActorSequenceComponent` |
| `GetPlaybackPosition` | 获取序列当前的播放时间。 | `UActorSequenceComponent` |
| `IsPlaying` | 判断序列是否正在播放。 | `UActorSequenceComponent` |
| `IsReversed` | 判断序列是否处于反向播放状态。 | `UActorSequenceComponent` |
| `SetReversePlayback` | 设置序列是否反向播放。 | `UActorSequenceComponent` |

### 使用示例（蓝图描述）

1.  **创建与播放**：在你的 Actor 蓝图中，添加一个 `ActorSequenceComponent`。在组件详情面板中，你可以直接点击“Open Sequence Editor”按钮来编辑内嵌序列。在事件图表中，使用 `Play` 节点并连接到某个事件（如 `BeginPlay` 或自定义事件），即可在运行时播放序列。
2.  **控制播放**：使用 `Stop` 节点停止，使用 `SetPlaybackPosition` 节点（输入时间值）跳转到特定时间点。
3.  **双向播放**：在序列组件的属性中，可以设置 `bReversePlayback` 来改变默认播放方向，或者在运行时通过 `SetReversePlayback` 节点动态切换。`PlayReverse` 节点提供了一次性的反向播放。

## C++ 用法

### 头文件引入

```cpp
#include "ActorSequenceComponent.h"
```

### 基本用法

在 C++ 中动态创建和播放一个 Actor 序列组件。
(灵感源自 `ActorSequenceComponent` 的基本使用模式)

```cpp
// MyActor.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyActor.generated.h"

UCLASS()
class AMyActor : public AActor
{
	GENERATED_BODY()

public:
	AMyActor();

protected:
	virtual void BeginPlay() override;

private:
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, meta = (AllowPrivateAccess = "true"))
	TObjectPtr<UActorSequenceComponent> SequenceComponent;

	UFUNCTION()
	void OnSequenceFinished();
};
```

```cpp
// MyActor.cpp
#include "MyActor.h"
#include "ActorSequenceComponent.h"

AMyActor::AMyActor()
{
	PrimaryActorTick.bCanEverTick = false;

	SequenceComponent = CreateDefaultSubobject<UActorSequenceComponent>(TEXT("SequenceComponent"));
}

void AMyActor::BeginPlay()
{
	Super::BeginPlay();

	// 假设组件中已经通过编辑器设置了内嵌序列
	if (SequenceComponent)
	{
		// 播放序列
		SequenceComponent->Play();

		// 绑定播放结束委托（如果需要）
		// SequenceComponent->OnSequenceFinished().AddUObject(this, &AMyActor::OnSequenceFinished);
	}
}

void AMyActor::OnSequenceFinished()
{
	UE_LOG(LogTemp, Log, TEXT("Actor sequence playback finished!"));
}
```

### 进阶用法

在运行时动态控制序列播放状态。
(灵感源自对播放状态和位置的控制)

```cpp
// ... 在某个函数内
if (SequenceComponent && SequenceComponent->IsPlaying())
{
	// 跳转到序列的第 10 秒
	SequenceComponent->SetPlaybackPosition(10.0f);

	// 切换为反向播放
	SequenceComponent->SetReversePlayback(!SequenceComponent->IsReversed());

	// 或者直接播放一次反向
	// SequenceComponent->PlayReverse();
}

// 停止播放
SequenceComponent->Stop();
```

## Demo 示例

一个最小的 Actor，包含一个序列组件，并在开始时播放它。

```cpp
// SequenceDemoActor.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SequenceDemoActor.generated.h"

class UActorSequenceComponent;

UCLASS()
class ASequenceDemoActor : public AActor
{
	GENERATED_BODY()

public:
	ASequenceDemoActor();

protected:
	virtual void BeginPlay() override;

private:
	// 在蓝图编辑器中可见的序列组件，用于内嵌动画
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Animation", meta = (AllowPrivateAccess = "true"))
	TObjectPtr<UActorSequenceComponent> AnimationSequence;
};
```

```cpp
// SequenceDemoActor.cpp
#include "SequenceDemoActor.h"
#include "ActorSequenceComponent.h"

ASequenceDemoActor::ASequenceDemoActor()
{
	PrimaryActorTick.bCanEverTick = false;

	// 创建并设置序列组件为根组件的子组件（或根据需要）
	AnimationSequence = CreateDefaultSubobject<UActorSequenceComponent>(TEXT("AnimationSequence"));
	// 通常序列组件会作为根组件或附加到根组件，具体取决于你的 Actor 结构
}

void ASequenceDemoActor::BeginPlay()
{
	Super::BeginPlay();

	// 播放内嵌的序列
	if (AnimationSequence)
	{
		AnimationSequence->Play();
	}
}
```

## 模块依赖

要使用 Actor Sequence 插件，你的模块需要依赖以下模块（除了常见的 Core, Engine 等）：

| 模块 | 用途 |
|---|---|
| `MovieScene` | 序列编辑器的核心框架 |
| `MovieSceneTracks` | 包含各种序列轨道（TransformTrack 等）的实现 |
| `LevelSequence` | 与通用的 Level Sequence 系统交互的基础 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-10 | `c03b3afd` | PR #14610: Rep layout mismatch in level sequence player due to with editoronly data property | 修复了由于 EditorOnly 数据属性导致的 Level Sequence 玩家网络复制布局不匹配问题。 |
| 2026-03-20 | `992fad6c` | Gameplay systems deprecation removal pass for 5.4 and earlier, I skipped anything that was still in | 进行了一次游戏系统相关废弃代码的清理工作，针对 5.4 及更早版本。 |
| 2025-09-25 | `f04d06c7` | Sequencer: Limit Viewport Selection UX Tweaks | 对 Sequencer 的视口选择用户体验进行了微调和优化。 |
| 2025-09-10 | `bb165be8` | UMG: Disable Dynamic Possession menu if it's not supported | 在 UMG 中，如果当前情况不支持动态 Possess，则禁用相关菜单。 |
| 2025-07-14 | `b010bdd4` | PR #13519: [Sequences] Add PlayReverse function to actor sequence components | **为 Actor 序列组件新增了 `PlayReverse` 函数**，允许直接反向播放序列。 |

### 维护评价

- **活跃维护**：尽管该插件创建于 2017 年（约 10 年前），但从最近的 git 历史来看，它在 2025 年和 2026 年仍有**功能性更新**（如新增 `PlayReverse` 函数）和持续的 Bug 修复，表明它仍处于活跃维护状态。
- **实验性状态**：`.uplugin` 中标记为 `IsBetaVersion: true`，且描述中包含 (Experimental)，表明它仍被视为实验性功能。
- **推荐使用**：对于上述“使用场景”中描述的需求，Actor Sequence 是一个成熟且仍在改进的解决方案。其内置编辑器集成度高。但由于其“实验性”标签，在大规模生产环境中使用前应进行充分测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/ActorSequence)
- [官方文档]()（无）