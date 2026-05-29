# Actor Sequence

> Runtime for embedded actor sequences

| 属性 | 值 |
|---|---|
| 中文名 | Actor序列 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ActorSequence` (Runtime), `ActorSequenceEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2017-09-07 |
| 年龄标签 | 🏛️ 文物（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/ActorSequence) | |

## 用途

ActorSequence 插件解决的核心问题是：**将 Sequencer 动画直接嵌入到 Actor 内部**，而不是作为独立的 Level Sequence 资产存在于外部。

传统的 Sequencer 工作流需要创建独立的 `ULevelSequence` 资产，再通过 `ALevelSequenceActor` 放置到关卡中播放。这种方式适合全局过场动画，但对于那些"自身携带动画"的可复用 Actor（如自动门、旋转平台、带动画的装饰物等），流程就显得繁琐——你需要同时管理 Actor 资产和序列资产。

ActorSequence 让你：
- 在 Actor 内部直接编辑时间轴动画
- 通过组件方式将序列绑定到 Actor 及其子组件
- 运行时通过简单的 API 播放/暂停/停止这些动画
- 序列与 Actor 一起打包，方便复用

本质上，它把 Level Sequence 的能力"压缩"成了一个 ActorComponent，让每个 Actor 都能自带动画。

## 使用场景

- 你需要制作一个带有开/关动画的门 → 在门 Actor 上添加 ActorSequenceComponent，在其内嵌编辑器中录制动画
- 你需要制作可复用的动画道具（旗帜飘动、灯光闪烁、机关运动） → 用 ActorSequence 将动画嵌入预制体
- 你需要在蓝图中按事件触发动画（如按下按钮后播放机关动画） → 通过组件的 Play/Stop 函数控制
- 你想让动画随 Actor 一起被 Spawn 出来，不需要额外管理 Level Sequence 资产

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Play Sequence` | 正向播放嵌入的序列 | `UActorSequenceComponent` |
| `Play Sequence Reverse` | 反向播放嵌入的序列 | `UActorSequenceComponent` |
| `Pause Sequence` | 暂停当前播放 | `UActorSequenceComponent` |
| `Stop Sequence` | 停止播放并重置 | `UActorSequenceComponent` |

### 属性

| 属性 | 类型 | 说明 | 所在类 |
|---|---|---|---|
| `Playback Settings` | `FMovieSceneSequencePlaybackSettings` | 播放设置（循环、播放速率、自动播放等） | `UActorSequenceComponent` |
| `Sequence` | `UActorSequence*` | 嵌入的序列数据 | `UActorSequenceComponent` |
| `SequencePlayer` | `UActorSequencePlayer*` | 运行时播放器（只读） | `UActorSequenceComponent` |

### 使用示例（蓝图描述）

**场景：按下按钮播放门的开启动画**

1. 在门 Actor 上添加 `ActorSequenceComponent`
2. 在组件的 `Animation` 分类下，点击 `Sequence` 属性进入嵌入式序列编辑器
3. 录制门的旋转/位移动画
4. 在按钮的 `OnPressed` 事件中，获取门 Actor → 获取 `ActorSequenceComponent` 引用 → 调用 `PlaySequence`

**场景：门关闭动画**

1. 同上获取组件引用
2. 调用 `PlaySequenceReverse` 实现反向播放（即关门动画）

## C++ 用法

### 头文件引入

```cpp
#include "ActorSequence.h"
#include "ActorSequenceComponent.h"
#include "ActorSequencePlayer.h"
```

### 基本用法

```cpp
// 获取 Actor 上的 ActorSequenceComponent
UActorSequenceComponent* SeqComp = MyActor->FindComponentByClass<UActorSequenceComponent>();
if (SeqComp)
{
    // 正向播放
    SeqComp->PlaySequence();
    
    // 暂停
    SeqComp->PauseSequence();
    
    // 停止
    SeqComp->StopSequence();
}
```

### 进阶用法

```cpp
// 直接操作播放器获取更精细的控制
UActorSequenceComponent* SeqComp = MyActor->FindComponentByClass<UActorSequenceComponent>();
if (SeqComp)
{
    UActorSequencePlayer* Player = SeqComp->GetSequencePlayer();
    if (Player)
    {
        // 设置播放速率
        Player->SetPlayRate(0.5f);
        
        // 获取当前播放位置
        FFrameNumber CurrentFrame = Player->GetCurrentTime().Time.GetFrame();
        
        // 跳转到指定时间
        FFrameTime TargetTime(120); // 第120帧
        Player->SetPlaybackPosition(FMovieSceneSequencePlaybackParams(TargetTime, EUpdatePositionMethod::Play));
    }
    
    // 获取嵌入的序列对象，用于检查轨道信息
    UActorSequence* Seq = SeqComp->GetSequence();
    if (Seq)
    {
        UMovieScene* MovieScene = Seq->GetMovieScene();
        // 可以检查 MovieScene 中的轨道、片段等信息
    }
}
```

## Demo 示例

```cpp
// AnimatedDoor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "AnimatedDoor.generated.h"

class UActorSequenceComponent;
class UBoxComponent;

UCLASS()
class AAnimatedDoor : public AActor
{
    GENERATED_BODY()

public:
    AAnimatedDoor();

    UFUNCTION(BlueprintCallable)
    void ToggleDoor();

    UFUNCTION(BlueprintCallable)
    void OpenDoor();

    UFUNCTION(BlueprintCallable)
    void CloseDoor();

protected:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    TObjectPtr<UActorSequenceComponent> SequenceComponent;

    UPROPERTY(VisibleAnywhere)
    TObjectPtr<UStaticMeshComponent> DoorMesh;

    UPROPERTY(VisibleAnywhere)
    TObjectPtr<UBoxComponent> TriggerVolume;

    UPROPERTY(BlueprintReadOnly)
    bool bIsOpen = false;

    UFUNCTION()
    void OnTriggerBeginOverlap(UPrimitiveComponent* OverlappedComp, AActor* OtherActor,
        UPrimitiveComponent* OtherComp, int32 OtherBodyIndex,
        bool bFromSweep, const FHitResult& SweepResult);
};
```

```cpp
// AnimatedDoor.cpp
#include "AnimatedDoor.h"
#include "ActorSequenceComponent.h"
#include "Components/BoxComponent.h"
#include "Components/StaticMeshComponent.h"

AAnimatedDoor::AAnimatedDoor()
{
    DoorMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("DoorMesh"));
    RootComponent = DoorMesh;

    TriggerVolume = CreateDefaultSubobject<UBoxComponent>(TEXT("TriggerVolume"));
    TriggerVolume->SetupAttachment(RootComponent);
    TriggerVolume->SetBoxExtent(FVector(200.f, 200.f, 100.f));
    TriggerVolume->SetCollisionProfileName(TEXT("Trigger"));

    // 添加 ActorSequenceComponent —— 关键组件
    SequenceComponent = CreateDefaultSubobject<UActorSequenceComponent>(TEXT("Sequence"));
    // Sequence 内容在编辑器中配置，不需要在 C++ 中创建

    PrimaryActorTick.bCanEverTick = false;
}

void AAnimatedDoor::BeginPlay()
{
    Super::BeginPlay();

    if (TriggerVolume)
    {
        TriggerVolume->OnComponentBeginOverlap.AddDynamic(
            this, &AAnimatedDoor::OnTriggerBeginOverlap);
    }
}

void AAnimatedDoor::ToggleDoor()
{
    if (bIsOpen)
    {
        CloseDoor();
    }
    else
    {
        OpenDoor();
    }
}

void AAnimatedDoor::OpenDoor()
{
    if (SequenceComponent)
    {
        SequenceComponent->PlaySequence();
        bIsOpen = true;
    }
}

void AAnimatedDoor::CloseDoor()
{
    if (SequenceComponent)
    {
        SequenceComponent->PlaySequenceReverse();
        bIsOpen = false;
    }
}

void AAnimatedDoor::OnTriggerBeginOverlap(UPrimitiveComponent* OverlappedComp, AActor* OtherActor,
    UPrimitiveComponent* OtherComp, int32 OtherBodyIndex,
    bool bFromSweep, const FHitResult& SweepResult)
{
    if (OtherActor && OtherActor->IsA<ACharacter>())
    {
        ToggleDoor();
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MovieScene` | Sequencer 核心模块，提供 UMovieScene、UMovieSceneSequence 等基类 |
| `MovieSceneTracks` | Sequencer 轨道实现（Transform、Property 等轨道） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-10 | `c03b3afd` | PR #14610: Rep layout mismatch in level sequence player due to with editoronly data property | 修复序列播放器因编辑器专用数据属性导致的复制布局不匹配 |
| 2026-03-20 | `992fad6c` | Gameplay systems deprecation removal pass for 5.4 and earlier, I skipped anything that was still in | 清理 5.4 及更早版本的废弃系统，移除相关引用 |
| 2025-09-25 | `f04d06c7` | Sequencer: Limit Viewport Selection UX Tweaks | Sequencer 视口选择 UX 调整，涉及本插件适配 |
| 2025-09-10 | `bb165be8` | UMG: Disable Dynamic Possession menu if it's not supported | 当不支持时禁用动态占有菜单 |
| 2025-07-14 | `b010bdd4` | PR #13519: [Sequences] Add PlayReverse function to actor sequence components | 为 Actor 序列组件添加反向播放功能 |

### 维护评价

ActorSequence 创建于 2017 年，距今约 8 年，属于较早期的 Sequencer 功能模块。虽然 `.uplugin` 中标记为 `Experimental`（`IsBetaVersion=true`），但实际上它已经被广泛使用。

**正面信号**：
- 2025 年 7 月刚刚添加了 `PlaySequenceReverse` 功能（`b010bdd4`），说明 Epic 仍在积极维护
- 2026 年仍有编译兼容性和废弃清理方面的更新
- 默认启用（`EnabledByDefault=true`），表明 Epic 认为它足够稳定

**风险信号**：
- 8 年仍未脱离 `Experimental` 标签，可能意味着 Epic 不打算将其提升为正式 API
- 功能较为基础，没有看到持续的功能增强计划
- 标记为 `Experimental` 的类可能在大版本更新中被重构或移除

**总体评价**：功能稳定，适合生产使用，但需注意 `Experimental` 标签意味着 API 不保证长期稳定。建议关注版本更新日志中的 deprecation 警告。推荐使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/ActorSequence)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/ActorSequence/Tests)（如有）