# Template Sequence

> Runtime for template sequences

| 属性 | 值 |
|---|---|
| 中文名 | 模板序列 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `TemplateSequence` (Runtime), `TemplateSequenceEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-10-02 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/TemplateSequence) | |

## 用途

Template Sequence 解决的核心问题是**动画模板的可复用实例化**。

在标准 Sequencer 工作流中，一个 Level Sequence 绑定到特定的 Actor。如果你希望相同的动画（例如一段摄像机运动、一个镜头震动效果）应用到不同对象上，你不得不复制整个序列并重新绑定——这既冗余又难以维护。

Template Sequence 通过引入"模板"概念来解决这个问题：

1. **可复用动画资产**：`UTemplateSequence` 定义了一个以 Spawnable 对象为根的序列模板，这个模板可以在多个 Level Sequence 中被实例化，每次实例化可以绑定到不同的目标对象
2. **摄像机动画专门化**：`UCameraAnimationSequence` 是专门为摄像机设计的模板序列，配合轻量级播放器 `UCameraAnimationSequencePlayer` 和虚拟摄像机对象 `UCameraAnimationSequenceCameraStandIn`，无需真实 Actor 即可驱动摄像机动画
3. **镜头震动集成**：`USequenceCameraShakePattern` 将 Sequencer 动画包装为镜头震动模式，可通过内置 Camera Shake 系统播放
4. **属性缩放**：模板序列实例化时支持对特定属性进行缩放（浮点属性、变换的位移/旋转分量），使得同一个模板在不同上下文可以产生不同强度的效果

简单来说：**你需要一段预设的镜头运动或摄像机动画，在不同场景中重复使用但参数各异 → 用 Template Sequence**。

## 使用场景

- 你在做一个 FPS 游戏，需要多种枪械后坐力镜头震动 → 用 `USequenceCameraShakePattern` 定义基于 Sequencer 的镜头震动
- 你有标准化的过场镜头运动（推拉摇移），需要在不同关卡中复用但绑定到不同摄像机 → 用 `ATemplateSequenceActor` 配合 `UTemplateSequence`
- 你希望同一个震动效果在不同武器上强度不同 → 利用 Template Sequence 的属性缩放功能
- 你在 Sequencer 中编辑一组动画，希望它能成为可复用的子序列模板 → 在 Level Sequence 中添加 Template Sequence Track

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Template Sequence Player` | 静态工厂方法，创建模板序列播放器并生成对应的 Actor | `UTemplateSequencePlayer` |
| `Get Sequence` | 获取当前播放的模板序列资产 | `ATemplateSequenceActor` |
| `Load Sequence` | 加载并返回模板序列资产 | `ATemplateSequenceActor` |
| `Set Sequence` | 设置要播放的模板序列资产 | `ATemplateSequenceActor` |
| `Get Sequence Player` | 获取序列播放器实例 | `ATemplateSequenceActor` |
| `Set Binding` | 设置模板序列根对象的绑定覆盖，指定目标 Actor | `ATemplateSequenceActor` |

### 镜头震动属性

`USequenceCameraShakePattern` 作为镜头震动模式，所有属性均可在蓝图/编辑器中配置：

| 属性 | 说明 |
|---|---|
| `Sequence` | 源摄像机动画序列资产 |
| `PlayRate` | 播放速度倍率（最小 0.001） |
| `Scale` | 震动强度缩放（最小 0.0） |
| `BlendInTime` | 线性淡入时间（秒） |
| `BlendOutTime` | 线性淡出时间（秒） |
| `bRandomSegment` | 是否播放序列的随机片段 |
| `RandomSegmentDuration` | 随机片段持续时长（仅 bRandomSegment=true 时生效） |

### 使用示例（蓝图描述）

**场景 1：在世界中播放模板序列**

1. 在场景中放置 `ATemplateSequenceActor`
2. 在 Details 面板中设置 `Template Sequence` 属性指向你的 `UTemplateSequence` 资产
3. 配置 `Playback Settings`（是否自动播放、循环等）
4. 调用 `Set Binding` 节点，传入目标 Actor 参数，将模板序列绑定到该 Actor
5. 游戏运行时，模板序列会自动在目标 Actor 上播放

**场景 2：运行时动态创建播放器**

1. 调用 `Create Template Sequence Player` 静态节点
2. 传入 World Context、`UTemplateSequence` 资产和播放设置
3. 输出参数 `OutActor` 会生成对应的 `ATemplateSequenceActor`
4. 通过返回的 `UTemplateSequencePlayer` 控制播放、暂停等

**场景 3：创建基于序列的镜头震动**

1. 创建 `UCameraAnimationSequence` 资产，在 Sequencer 中编辑摄像机动画
2. 在代码或配置中创建 `USequenceCameraShakePattern`
3. 将 `Sequence` 属性设为步骤 1 的资产
4. 设置 `PlayRate`、`Scale`、`BlendInTime` 等参数
5. 将该震动模式注册到 Camera Manager 或通过 Play Camera Shake 节点触发

## C++ 用法

### 头文件引入

```cpp
// 运行时模块
#include "TemplateSequence.h"
#include "TemplateSequencePlayer.h"
#include "TemplateSequenceActor.h"
#include "CameraAnimationSequence.h"
#include "CameraAnimationSequencePlayer.h"
#include "SequenceCameraShake.h"
#include "CameraAnimationSequenceSubsystem.h"
```

### 基本用法：动态创建模板序列播放器

```cpp
// 来源: Public/TemplateSequencePlayer.h
// 通过静态工厂方法创建模板序列播放器和对应的 Actor
UTemplateSequence* MyTemplateSequence = LoadObject<UTemplateSequence>(nullptr, TEXT("/Game/Sequences/MyTemplateSeq"));

FMovieSceneSequencePlaybackSettings PlaybackSettings;
PlaybackSettings.bAutoPlay = true;
PlaybackSettings.LoopCount.Value = 0; // 无限循环

ATemplateSequenceActor* SpawnedActor = nullptr;
UTemplateSequencePlayer* Player = UTemplateSequencePlayer::CreateTemplateSequencePlayer(
    GetWorld(),
    MyTemplateSequence,
    PlaybackSettings,
    SpawnedActor
);

// 通过 Actor 设置绑定
if (SpawnedActor)
{
    SpawnedActor->SetBinding(MyTargetActor, true);
}
```

### 基本用法：使用摄像机动画序列播放器

```cpp
// 来源: Public/CameraAnimationSequencePlayer.h
// 创建轻量级摄像机动画播放器（不需要 Actor）
UCameraAnimationSequencePlayer* CamPlayer = NewObject<UCameraAnimationSequencePlayer>();

// 初始化，可选起始偏移和时长覆盖
CamPlayer->Initialize(MyCameraAnimSequence, /*StartOffset=*/0, /*DurationOverride=*/5.0f);

// 开始播放
CamPlayer->Play(/*bLoop=*/false, /*bRandomStartTime=*/false);

// 每帧更新
CamPlayer->Update(CurrentFrameTime);

// 跳转到指定时间
CamPlayer->Jump(FFrameTime(120));

// 停止播放
CamPlayer->Stop();
```

### 进阶用法：通过 Camera Animation Subsystem 管理全局摄像机动画

```cpp
// 来源: Public/CameraAnimationSequenceSubsystem.h
// 获取世界子系统
UCameraAnimationSequenceSubsystem* Subsystem = 
    UCameraAnimationSequenceSubsystem::GetCameraAnimationSequenceSubsystem(GetWorld());

// 获取全局 Sequencer Linker（用于 ECS 实体系统）
UMovieSceneEntitySystemLinker* Linker = Subsystem->GetLinker(/*bAutoCreate=*/true);

// 获取全局 Runner
TSharedPtr<FMovieSceneEntitySystemRunner> Runner = Subsystem->GetRunner();
```

### 进阶用法：自定义镜头震动

```cpp
// 来源: Public/SequenceCameraShake.h
// 在代码中配置基于 Sequencer 的镜头震动
USequenceCameraShakePattern* ShakePattern = NewObject<USequenceCameraShakePattern>();
ShakePattern->Sequence = LoadObject<UCameraAnimationSequence>(
    nullptr, TEXT("/Game/CameraAnimations/Recoil_CameraShake"));
ShakePattern->PlayRate = 1.0f;
ShakePattern->Scale = 1.5f;         // 1.5 倍强度
ShakePattern->BlendInTime = 0.1f;   // 0.1 秒淡入
ShakePattern->BlendOutTime = 0.3f;  // 0.3 秒淡出
ShakePattern->bRandomSegment = false;

// 通过 PlayerController 的 Camera Manager 触发
APlayerController* PC = GetWorld()->GetFirstPlayerController();
if (PC && PC->PlayerCameraManager)
{
    FCameraShakeStartParams Params;
    Params.bIsRestarted = false;
    // ShakePattern 会被 Camera Manager 管理其生命周期
}
```

## Demo 示例

以下示例展示如何创建一个模板序列 Actor 并将摄像机动画绑定到目标对象上播放。

```cpp
// MyTemplateSequenceDemo.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyTemplateSequenceDemo.generated.h"

class UTemplateSequence;
class UTemplateSequencePlayer;
class ATemplateSequenceActor;

UCLASS()
class AMyTemplateSequenceDemo : public AActor
{
    GENERATED_BODY()

public:
    AMyTemplateSequenceDemo();

    virtual void BeginPlay() override;

    /** 要播放的模板序列资产 */
    UPROPERTY(EditAnywhere, Category = "Demo")
    TSoftObjectPtr<UTemplateSequence> TemplateSequenceAsset;

    /** 模板序列应用到的目标 Actor */
    UPROPERTY(EditAnywhere, Category = "Demo")
    AActor* BindingTarget;

private:
    UPROPERTY()
    TObjectPtr<ATemplateSequenceActor> SequenceActor;
};
```

```cpp
// MyTemplateSequenceDemo.cpp
#include "MyTemplateSequenceDemo.h"
#include "TemplateSequence.h"
#include "TemplateSequencePlayer.h"
#include "TemplateSequenceActor.h"

AMyTemplateSequenceDemo::AMyTemplateSequenceDemo()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyTemplateSequenceDemo::BeginPlay()
{
    Super::BeginPlay();

    UTemplateSequence* LoadedSequence = TemplateSequenceAsset.LoadSynchronous();
    if (!LoadedSequence)
    {
        UE_LOG(LogTemp, Warning, TEXT("TemplateSequenceDemo: Failed to load template sequence asset"));
        return;
    }

    // 通过静态工厂方法创建播放器和 Actor
    FMovieSceneSequencePlaybackSettings Settings;
    Settings.bAutoPlay = true;
    Settings.bPauseAtEnd = false;

    UTemplateSequencePlayer* Player = UTemplateSequencePlayer::CreateTemplateSequencePlayer(
        GetWorld(),
        LoadedSequence,
        Settings,
        SequenceActor  // 输出参数
    );

    if (Player && SequenceActor && BindingTarget)
    {
        // 将模板序列的根对象绑定到目标 Actor
        SequenceActor->SetBinding(BindingTarget, /*bOverridesDefault=*/true);
        UE_LOG(LogTemp, Log, TEXT("TemplateSequenceDemo: Started playing on %s"), 
            *BindingTarget->GetName());
    }
}
```

## 模块依赖

从源码中的类继承关系和组件使用推断，以下为 TemplateSequence 模块的独特依赖：

| 模块 | 用途 |
|---|---|
| `MovieScene` | 核心 Sequencer 框架，提供序列播放、实体系统、组件类型等基础设施 |
| `MovieSceneTracks` | Sequencer 轨道和通道实现 |
| `LevelSequence` | Level Sequence 框架，提供 Spawn 注册和子序列支持 |
| `CinematicCamera` | 电影摄像机参数结构体（Filmback、Lens、Focus 设置） |
| `CameraShake` / `Engine` | 镜头震动基类 `UCameraShakePattern` 和 `FMinimalViewInfo` |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为 float 的编译警告 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移到 UE_LOGF 新宏 |
| 2026-04-10 | `c03b3afd` | PR #14610: Rep layout mismatch in level sequence player due to with editoronly data property | 修复 Level Sequence Player 因编辑器专用属性导致的复制布局不匹配 |
| 2026-02-20 | `49054c9f` | Sequencer: Add Bake Transform to object binding menu | Sequencer 对象绑定菜单新增烘焙变换功能 |
| 2026-02-11 | `5919e4fa` | Remove 7 virtual functions in UObject (either deprecated or toolonly) | 移除 UObject 中 7 个已废弃或仅工具用的虚函数 |

### 维护评价

- **年龄**：创建于 2019 年 10 月，已约 7 年
- **实验性标记**：`.uplugin` 中 `IsBetaVersion=true`，表明 Epic 官方仍将其视为实验性功能
- **默认启用**：`EnabledByDefault=false`，需要手动在项目设置中启用
- **近期活跃度**：2026 年有多次更新，但均为全局性维护工作（编译警告修复、宏迁移、虚函数清理），并非 Template Sequence 的功能增强
- **功能稳定性**：核心 API（Player、Actor、ShakePattern、Section）结构长期未变，说明功能已趋于成熟
- **风险提示**：虽然仍在维护中，但 `IsBetaVersion` 标记意味着 API 可能仍会有 breaking changes。该插件自 2019 年起就处于 Beta 状态且从未"毕业"，建议在生产环境中谨慎使用，并关注版本迁移时的 API 变化

**综合推荐**：✅ 可用，但需注意 Beta 身份。对于镜头震动和可复用动画模板场景，该插件是目前 UE5 唯一的官方解决方案，实际使用中已足够稳定。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/TemplateSequence)
- [TemplateSequence 模块](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/TemplateSequence/Source/TemplateSequence)
- [TemplateSequenceEditor 模块](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/TemplateSequence/Source/TemplateSequenceEditor)