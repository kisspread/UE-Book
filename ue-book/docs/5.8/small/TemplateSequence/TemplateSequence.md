# Template Sequence

> Runtime for template sequences（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 模板序列 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `TemplateSequence` (Runtime), `TemplateSequenceEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-10-02 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/TemplateSequence) | |

## 用途

TemplateSequence 插件提供了一套运行时系统，用于在游戏世界中实例化和播放“模板序列”（`UTemplateSequence`）。与传统的关卡序列（`ULevelSequence`）主要用于过场动画和编辑器内的预览不同，模板序列设计为一种可复用、可实例化的动画资产。它本质上是一个序列蓝图，可以在运行时被绑定到不同的对象上播放，特别适用于需要重复使用相同动画逻辑的场景，例如相机抖动效果、角色技能动画或环境交互动画。插件的核心是提供了一个轻量级的序列播放器和配套的实体系统，确保序列播放能够高效地集成到游戏运行时逻辑中。

## 使用场景

-   **相机抖动与后处理效果**：你可以创建一个定义相机移动和后处理变化的序列（`UCameraAnimationSequence`），然后将其用作 `USequenceCameraShakePattern` 的输入，在游戏内触发爆炸、撞击等事件时，以可控的方式播放复杂的相机抖动效果。
-   **可复用的动画模板**：当你设计了一个复杂的动画序列（例如，一系列摄像机运镜或道具动画），并希望在游戏的不同地点、不同时间、绑定到不同物体上重复使用时，可以使用模板序列。
-   **动态过场与事件动画**：在需要由游戏逻辑（如NPC对话、触发器）动态触发过场动画，而不是依赖固定的时间轴或编辑器放置时，模板序列可以与 `ATemplateSequenceActor` 结合使用，在蓝图中通过 `CreateTemplateSequencePlayer` 动态创建并播放。
-   **属性缩放动画**：当需要对序列中某个对象的特定属性（如浮点数、变换的位置或旋转部分）进行基于另一个曲线或值的动态缩放时，可以利用 `UTemplateSequenceSection` 中的 `PropertyScales` 功能。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Template Sequence Player` | 静态函数，用于在指定世界中创建一个模板序列播放器，并返回关联的 Actor。这是在蓝图中动态实例化并播放模板序列的主要方法。 | `UTemplateSequencePlayer` |
| `Get Sequence Player` | 获取此 Actor 内部拥有的序列播放器实例。 | `ATemplateSequenceActor` |
| `Set Binding` | 将模板序列的根对象绑定（覆盖）到世界中的另一个 Actor 上播放。 | `ATemplateSequenceActor` |
| `Get Sequence` / `Load Sequence` | 获取此 Actor 引用的模板序列资产，或尝试加载它。 | `ATemplateSequenceActor` |
| `Play Rate` | `USequenceCameraShakePattern` 上的属性，控制序列的播放速度。 | `USequenceCameraShakePattern` |
| `Scale` | `USequenceCameraShakePattern` 上的属性，控制动画效果的强度缩放。 | `USequenceCameraShakePattern` |

### 使用示例（蓝图描述）

1.  **动态播放模板序列**：
    -   使用 `Create Template Sequence Player` 节点。
    -   指定一个 `UWorld` 上下文（通常从 `Get World` 获得）。
    -   赋值一个 `UTemplateSequence` 资产引用。
    -   配置 `FMovieSceneSequencePlaybackSettings`（如循环、播放速率）。
    -   节点会输出一个 `ATemplateSequenceActor` 引用，其 `Sequence Player` 将自动开始播放。
2.  **将序列绑定到特定对象**：
    -   首先，在场景中放置一个 `ATemplateSequenceActor`。
    -   在其细节面板中，设置 `Template Sequence` 属性。
    -   在蓝图中，调用该 Actor 的 `Set Binding` 函数，并传入你想要播放此序列的目标 `AActor`。
    -   之后，当序列播放时，其内部的对象变换、属性等将应用到目标 Actor 上。
3.  **创建序列化的相机抖动**：
    -   创建一个 `UCameraAnimationSequence` 资产，在其中动画相机。
    -   在需要应用抖动的相机管理器（`Player Camera Manager`）中，通过蓝图添加一个 `USequenceCameraShakePattern`。
    -   将刚创建的 `UCameraAnimationSequence` 赋值给该抖动模式的 `Sequence` 属性。
    -   可以设置 `Play Rate`、`Scale`、混合时间以及 `Random Segment` 等参数来自定义效果。

## C++ 用法

### 头文件引入

```cpp
#include "TemplateSequence/TemplateSequencePlayer.h"
#include "TemplateSequence/TemplateSequenceActor.h"
#include "TemplateSequence/SequenceCameraShake.h"
#include "TemplateSequence/CameraAnimationSequencePlayer.h"
#include "TemplateSequence/CameraAnimationSequenceSubsystem.h"
```

### 基本用法

以下代码展示了如何在C++中动态创建并播放一个模板序列。

**来源文件**: 推断自 `UTemplateSequencePlayer::CreateTemplateSequencePlayer` 的接口设计。

```cpp
// 1. 获取需要播放的模板序列资产（通常在编辑器中设置或通过资产路径加载）
UTemplateSequence* MyTemplateSequence = LoadObject<UTemplateSequence>(nullptr, TEXT("/Game/Sequences/MyTemplateSeq"));

// 2. 准备播放设置
FMovieSceneSequencePlaybackSettings PlaybackSettings;
PlaybackSettings.bLoop = true;
PlaybackSettings.PlayRate = 1.0f;

// 3. 创建播放器和关联的Actor
ATemplateSequenceActor* OutActor = nullptr;
UTemplateSequencePlayer* SequencePlayer = UTemplateSequencePlayer::CreateTemplateSequencePlayer(
    GetWorld(), // WorldContextObject
    MyTemplateSequence,
    PlaybackSettings,
    OutActor
);

if (SequencePlayer && OutActor)
{
    // 序列将在此Actor上播放。你也可以通过 OutActor->SetBinding(SomeOtherActor) 绑定到其他对象。
    UE_LOG(LogTemp, Log, TEXT("Template sequence player created and playback started."));
}
```

### 进阶用法

**使用 `UCameraAnimationSequenceSubsystem` 手动管理相机动画播放**（更底层、更高效的用法，适用于需要精细控制多个相机动画的场景）。

**来源文件**: `Public/CameraAnimationSequenceSubsystem.h`, `Public/CameraAnimationSequencePlayer.h`。

```cpp
// 获取或创建当前世界的相机动画子系统
UCameraAnimationSequenceSubsystem* AnimSubsystem = UCameraAnimationSequenceSubsystem::GetCameraAnimationSequenceSubsystem(GetWorld());
if (AnimSubsystem)
{
    // 获取子系统管理的全局Runner
    TSharedPtr<FMovieSceneEntitySystemRunner> Runner = AnimSubsystem->GetRunner();

    // 创建一个轻量级的播放器
    UCameraAnimationSequencePlayer* CamAnimPlayer = NewObject<UCameraAnimationSequencePlayer>(this);

    // 初始化，传入一个UCameraAnimationSequence资产
    UCameraAnimationSequence* CamAnimSeq = LoadObject<UCameraAnimationSequence>(nullptr, TEXT("/Game/Camera/Shakes/ExplosionShake"));
    CamAnimPlayer->Initialize(CamAnimSeq, /* StartOffset */ 0, /* DurationOverride */ 0.f);

    // 开始播放（例如循环播放）
    CamAnimPlayer->Play(true, false);

    // 在每帧的Tick中，需要手动更新播放器位置
    // ... 获取 DeltaTime，计算 NewPosition (FFrameTime)
    // CamAnimPlayer->Update(NewPosition);
}
```

**属性缩放示例**：
这通常在编辑器中通过模板序列轨道的属性面板设置，但在运行时，系统会读取 `UTemplateSequenceSection` 中的 `PropertyScales` 数据，并通过 `UTemplateSequencePropertyScalingEvaluatorSystem` 应用。

## Demo 示例

这是一个最小的、可编译的示例，展示如何在 Actor 中创建并播放一个模板序列。

**MySequenceDemoActor.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "TemplateSequence/TemplateSequencePlayer.h"
#include "TemplateSequence/TemplateSequenceActor.h"
#include "MySequenceDemoActor.generated.h"

UCLASS()
class AMySequenceDemoActor : public AActor
{
    GENERATED_BODY()

public:
    AMySequenceDemoActor();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    UPROPERTY(EditAnywhere, Category = "Template Sequence")
    UTemplateSequence* TemplateSequenceToPlay;

    UPROPERTY(Transient)
    ATemplateSequenceActor* SpawnedSequenceActor;
};
```

**MySequenceDemoActor.cpp**
```cpp
#include "MySequenceDemoActor.h"
#include "TemplateSequence/TemplateSequencePlayer.h"

AMySequenceDemoActor::AMySequenceDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMySequenceDemoActor::BeginPlay()
{
    Super::BeginPlay();

    if (TemplateSequenceToPlay && GetWorld())
    {
        FMovieSceneSequencePlaybackSettings Settings;
        Settings.bLoop = false;

        // 使用静态函数创建播放器
        UTemplateSequencePlayer* Player = UTemplateSequencePlayer::CreateTemplateSequencePlayer(
            GetWorld(),
            TemplateSequenceToPlay,
            Settings,
            SpawnedSequenceActor // 输出参数，会创建一个新的 ATemplateSequenceActor
        );

        if (Player && SpawnedSequenceActor)
        {
            // 可选：将序列绑定到自身播放
            SpawnedSequenceActor->SetBinding(this, true);
            UE_LOG(LogTemp, Log, TEXT("Template sequence started on actor: %s"), *GetName());
        }
    }
}

void AMySequenceDemoActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    // 清理：当Demo Actor销毁时，销毁生成的序列Actor
    if (SpawnedSequenceActor)
    {
        SpawnedSequenceActor->Destroy();
        SpawnedSequenceActor = nullptr;
    }
    Super::EndPlay(EndPlayReason);
}
```

## 模块依赖

从 `TemplateSequence.Build.cs` 分析，该运行时模块依赖于 Sequencer 核心模块以提供序列评估和实体系统支持。

| 模块 | 用途 |
|---|---|
| `MovieScene` | Sequencer的核心运行时模块，提供序列、轨道、求值模板等基础架构。 |
| `MovieSceneTracks` | 包含标准轨道（如变换、浮点等）的实现。 |
| `LevelSequence` | 提供关卡序列相关的运行时功能，如SpawnRegister。 |
| `EntityCore` | 实体组件系统(ECS)核心，支持模板序列使用的现代Sequencer后端。 |

*注：`Core`, `CoreUObject`, `Engine`, `Slate` 等通用依赖已省略。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断到浮点数的警告。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧版的 `UE_LOG` 宏迁移到新的 `UE_LOGF` 宏。 |
| 2026-04-10 | `c03b3afd` | PR #14610: Rep layout mismatch in level sequence player due to with editoronly data property | 修复因仅编辑器数据属性导致的关卡序列玩家复制布局不匹配问题。 |
| 2026-02-20 | `49054c9f` | Sequencer: Add Bake Transform to object binding menu | 在序列器的对象绑定菜单中添加“烘焙变换”功能。 |
| 2026-02-11 | `5919e4fa` | Remove 7 virtual functions in UObject (either deprecated or toolonly) | 移除了UObject中的7个虚函数（已废弃或仅工具使用）。 |

### 维护评价

TemplateSequence 插件创建于2019年（约6年前），至今仍标记为 `IsBetaVersion: true`，且默认未启用（`EnabledByDefault: false`），表明它仍处于**实验性/测试阶段**。从近期的 git 历史来看，更新主要集中在**编译警告修复、宏迁移、引擎内部架构兼容性调整**等方面，而非功能性的重大更新或bug修复。这表明该插件处于**低活跃度维护**状态，其核心功能已经稳定，但 Epic 并未将其推广为正式的、必备的运行时功能。

**建议**：该插件适用于有特定需求（如复杂的相机抖动系统、需要运行时序列实例化）且不介意使用实验性功能的项目。在生产环境中使用时，需要充分测试，因为其API在未来版本中可能会发生变化。对于简单的过场动画，传统的关卡序列仍是更成熟和推荐的选择。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/TemplateSequence)
-   官方文档：无
-   测试用例：插件内部的 `Private/Tests` 目录（路径：`Engine/Plugins/MovieScene/TemplateSequence/Source/TemplateSequence/Private/Tests/`）