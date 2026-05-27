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
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/TemplateSequence) | |

## 用途

Template Sequence 解决的核心问题是 **Sequencer 动画的可复用实例化**。

在标准的 Level Sequence 中，动画是"一对一"绑定的——一个序列绑定到一组特定对象。而 Template Sequence 允许你创建一个**模板化的动画资产**，其中包含一个根可生成对象（Spawnable），这个模板可以在多个 Level Sequence 中被多次实例化，每次实例可以绑定到不同的目标对象。

最典型的应用场景是 **摄像机动画**：`UCameraAnimationSequence` 继承自 `UTemplateSequence`，专门用于创建可复用的摄像机摇晃/运镜动画。配合 `USequenceCameraShakePattern`，可以用 Sequencer 动画替代传统的程序化 Camera Shake，实现更精细的摄像机效果控制。

简而言之：**模板序列 = 可复用的 Sequencer 动画模板 + 实例化时绑定到不同对象**。

## 使用场景

- 你有一段精心设计的摄像机运镜动画，需要在多个关卡/多个场景中复用 → 创建 CameraAnimationSequence 模板
- 你需要基于 Sequencer 动画制作真实的摄像机摇晃效果（爆炸、撞击、脚步等）→ 使用 SequenceCameraShakePattern
- 你需要在 Sequencer 中嵌套可复用的子动画，每次实例可以绑定到不同角色/物体 → 使用 TemplateSequenceTrack
- 你需要对模板序列中的属性进行缩放（如不同强度的摄像机摇晃）→ 使用 PropertyScale 系统

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Template Sequence Player` | 静态函数：创建模板序列播放器并生成对应的 Actor | `UTemplateSequencePlayer` |
| `Get Sequence` | 获取正在播放的模板序列（软引用自动加载） | `ATemplateSequenceActor` |
| `Load Sequence` | 加载并返回正在播放的模板序列 | `ATemplateSequenceActor` |
| `Set Sequence` | 设置要播放的模板序列 | `ATemplateSequenceActor` |
| `Get Sequence Player` | 获取序列播放器实例 | `ATemplateSequenceActor` |
| `Set Binding` | 设置模板序列根对象的绑定覆盖（将动画应用到指定 Actor） | `ATemplateSequenceActor` |

### 创建并播放模板序列（蓝图）

1. **方式一：通过 `CreateTemplateSequencePlayer` 节点**
   - 输入：World Context Object、UTemplateSequence 资产、PlaybackSettings
   - 输出：UTemplateSequencePlayer 引用 + ATemplateSequenceActor 引用
   - 调用播放器的 `Play` 方法开始播放

2. **方式二：放置 ATemplateSequenceActor**
   - 在场景中放置 `ATemplateSequenceActor`
   - 在 Details 面板中设置 `Template Sequence` 属性（指定模板序列资产）
   - 配置 `Playback Settings`（是否循环、播放速率等）
   - 通过 `Set Binding` 节点将动画绑定到场景中的目标 Actor
   - 调用播放器的 `Play` 开始播放

### 配置 Camera Shake（蓝图）

1. 在 Camera Shake 配置中选择 `SequenceCameraShakePattern` 类型
2. 设置 `Sequence` 属性为一个 `UCameraAnimationSequence` 资产
3. 调整 `PlayRate`（播放速率）、`Scale`（强度缩放）、`BlendInTime`/`BlendOutTime`（混合时间）
4. 可选：启用 `bRandomSegment` 播放随机片段

## C++ 用法

### 头文件引入

```cpp
#include "TemplateSequencePlayer.h"
#include "TemplateSequenceActor.h"
#include "TemplateSequence.h"
#include "CameraAnimationSequence.h"
#include "SequenceCameraShake.h"
```

### 基本用法：创建并播放模板序列

```cpp
// 基于 Public/TemplateSequencePlayer.h 中的 CreateTemplateSequencePlayer 接口

UTemplateSequence* MyTemplateSequence = LoadObject<UTemplateSequence>(nullptr, TEXT("/Game/MyAnimations/MyTemplateSequence"));
FMovieSceneSequencePlaybackSettings Settings;
Settings.bAutoPlay = false;
Settings.LoopCount.Value = 0;  // 无限循环

ATemplateSequenceActor* SpawnedActor = nullptr;
UTemplateSequencePlayer* Player = UTemplateSequencePlayer::CreateTemplateSequencePlayer(
    GetWorld(), MyTemplateSequence, Settings, SpawnedActor);

if (Player)
{
    // 将模板序列绑定到场景中的某个 Actor
    SpawnedActor->SetBinding(MyTargetActor, true);

    // 开始播放
    Player->Play();
}
```

### 进阶用法：使用 Camera Animation Sequence Player

```cpp
// 基于 Public/CameraAnimationSequencePlayer.h 的接口
// 用于低级别的摄像机动画播放控制

UCameraAnimationSequencePlayer* CameraPlayer = NewObject<UCameraAnimationSequencePlayer>();
CameraPlayer->Initialize(MyCameraAnimSequence, /*StartOffset=*/ 0, /*DurationOverride=*/ 2.0f);

// 设置绑定对象覆盖（将摄像机动画应用到指定对象）
CameraPlayer->SetBoundObjectOverride(MyCameraActor);

// 开始播放（循环 + 随机起始时间）
CameraPlayer->Play(/*bLoop=*/true, /*bRandomStartTime=*/true);

// 每帧更新（获取当前时间并推进）
FFrameTime CurrentTime = CameraPlayer->GetCurrentPosition();
CameraPlayer->Update(CurrentTime + FFrameTime(1));

// 跳转到指定时间
CameraPlayer->Jump(FFrameTime(30));

// 停止播放
CameraPlayer->Stop();
```

### 进阶用法：Camera Animation Sequence Subsystem

```cpp
// 基于 Public/CameraAnimationSequenceSubsystem.h 的接口
// 用于管理全局的摄像机动画运行器和链接器

UCameraAnimationSequenceSubsystem* Subsystem =
    UCameraAnimationSequenceSubsystem::GetCameraAnimationSequenceSubsystem(GetWorld());

if (Subsystem)
{
    // 获取 Sequencer 链接器
    UMovieSceneEntitySystemLinker* Linker = Subsystem->GetLinker(/*bAutoCreate=*/true);

    // 获取摄像机动画运行器
    TSharedPtr<FMovieSceneEntitySystemRunner> Runner = Subsystem->GetRunner();
}
```

## Demo 示例

一个完整的最小示例：创建一个自定义 Camera Shake Pattern 并触发摄像机摇晃。

```cpp
// MyCameraShakeComponent.h
#pragma once

#include "Components/ActorComponent.h"
#include "MyCameraShakeComponent.generated.h"

class UCameraAnimationSequence;

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class MYGAME_API UMyCameraShakeComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UMyCameraShakeComponent();

    /** 触发摄像机摇晃 */
    UFUNCTION(BlueprintCallable, Category = "Camera")
    void TriggerCameraShake(float InScale = 1.0f);

    /** 要播放的摄像机动画序列 */
    UPROPERTY(EditAnywhere, Category = "Camera")
    TObjectPtr<UCameraAnimationSequence> CameraAnimationSequence;

protected:
    virtual void BeginPlay() override;
};
```

```cpp
// MyCameraShakeComponent.cpp
#include "MyCameraShakeComponent.h"
#include "CameraAnimationSequence.h"
#include "SequenceCameraShake.h"
#include "GameFramework/PlayerController.h"
#include "Camera/CameraModifier_CameraShake.h"

UMyCameraShakeComponent::UMyCameraShakeComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UMyCameraShakeComponent::BeginPlay()
{
    Super::BeginPlay();
}

void UMyCameraShakeComponent::TriggerCameraShake(float InScale)
{
    if (!CameraAnimationSequence)
    {
        return;
    }

    APlayerController* PC = GetWorld()->GetFirstPlayerController();
    if (!PC)
    {
        return;
    }

    // 创建 Sequence Camera Shake Pattern
    USequenceCameraShakePattern* ShakePattern = NewObject<USequenceCameraShakePattern>();
    ShakePattern->Sequence = CameraAnimationSequence;
    ShakePattern->PlayRate = 1.0f;
    ShakePattern->Scale = InScale;
    ShakePattern->BlendInTime = 0.2f;
    ShakePattern->BlendOutTime = 0.5f;

    // 启动摄像机摇晃
    PC->ClientStartCameraShake(ShakePattern->GetClass(), InScale);
}
```

## 模块依赖

该插件依赖以下非标准模块（`TemplateSequence.Build.cs` 推断）：

| 模块 | 用途 |
|---|---|
| `MovieScene` | Sequencer 核心运行时，提供序列、轨道、通道等基础设施 |
| `MovieSceneTracks` | Sequencer 标准轨道实现（Transform、Float 等轨道） |
| `LevelSequence` | Level Sequence 运行时，提供 Spawn Register 和序列播放支持 |

插件级依赖：

| 插件 | 用途 |
|---|---|
| `LevelSequenceEditor` | 编辑器中的 Level Sequence 编辑功能（TemplateSequenceEditor 模块需要） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的警告 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移到 UE_LOGF 宏 |
| 2026-04-10 | `c03b3afd` | PR #14610: Rep layout mismatch in level sequence player due to with editoronly data property | 修复 Level Sequence Player 中因 editoronly 属性导致的复制布局不匹配问题 |
| 2026-02-20 | `49054c9f` | Sequencer: Add Bake Transform to object binding menu | Sequencer 对象绑定菜单新增烘焙变换功能 |
| 2026-02-11 | `5919e4fa` | Remove 7 virtual functions in UObject (either deprecated or toolonly) | 移除 UObject 中 7 个已废弃或仅工具使用的虚函数 |

### 维护评价

**状态：活跃维护中**

该插件创建于 2019 年（UE 4.24 时期），至今约 6 年历史。从近期提交记录看，2026 年 2-5 月持续有更新，主要集中在：
- 代码现代化（UE_LOG 迁移、废弃函数清理）
- 编译警告修复（浮点精度问题）
- Bug 修复（复制同步问题）

值得注意的是，该插件至今仍标记为 `IsBetaVersion = true` 且 `EnabledByDefault = false`，说明 Epic 将其视为实验性功能。这可能意味着 API 可能在未来版本中发生变化。

**推荐程度：可用但需谨慎**。功能成熟稳定，在 Sequencer 摄像机系统中被广泛使用（Camera Animation 是其核心应用场景），但由于 Beta 标记和 `EnabledByDefault=false`，正式项目中需要手动启用并做好版本升级时 API 变动的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/TemplateSequence)
- 官方文档（无）