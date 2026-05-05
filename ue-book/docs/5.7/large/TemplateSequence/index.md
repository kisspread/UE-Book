# Template Sequence

> Runtime for template sequences

| 属性 | 值 |
|---|---|
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `TemplateSequence` (Runtime), `TemplateSequenceEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-10-01 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MovieScene/TemplateSequence) | |

## 用途

TemplateSequence 插件解决了一个 Sequencer（Level Sequence）的核心问题：**如何将一段动画序列作为可复用的"模板"嵌入到多个 Level Sequence 中，并在每个实例上应用独立的绑定和缩放**。

标准 Level Sequence 中的动画绑定是固定的——它绑定到特定的 Actor 或组件。但有时你需要创建一段"通用"动画（例如一个摄像机运镜），然后在不同场景中将其应用到不同的摄像机上。TemplateSequence 通过引入 **root spawnable 作为模板** 和 **binding override 机制** 来实现这一点。

该插件最核心的实际用途是 **Camera Animation Sequence（摄像机动画序列）**——一种专门用于驱动摄像机的模板序列，可以作为 Sequencer Section 嵌入到任何 Level Sequence 中，实现复用摄像机动画的能力。此外它还提供了基于 Sequencer 动画的 **Camera Shake Pattern**，将序列动画转化为摄像机抖动效果。

该插件标记为 `IsBetaVersion=true` 且 `EnabledByDefault=false`，但已被 Sequencer 内部深度依赖（如 Camera Cuts track 的实现），实际上是 UE5 摄像机系统的重要组成部分。

## 使用场景

- 你有一个 Level Sequence 中的摄像机，想为其添加一段精心制作的运镜动画 → 使用 Camera Animation Sequence
- 你想创建一个可复用的摄像机抖动效果（如爆炸震屏），且需要精确控制抖动曲线 → 使用 `USequenceCameraShakePattern`
- 你有一个 Actor 动画模板（如门的开关动画），想在不同关卡的多个同类型 Actor 上复用 → 使用 Template Sequence
- 你需要在 Sequencer 中对子序列的特定属性（如位移、旋转）进行动态缩放（如"这个运镜在远处使用时幅度放大 2 倍"） → 使用 Property Scale 功能
- 你想在运行时通过蓝图播放一段模板序列 → 使用 `UTemplateSequencePlayer::CreateTemplateSequencePlayer`

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Template Sequence Player` | 创建一个模板序列播放器，自动生成 Actor | `UTemplateSequencePlayer` |
| `Get Sequence` | 获取 Actor 当前播放的模板序列 | `ATemplateSequenceActor` |
| `Load Sequence` | 加载并返回 Actor 引用的模板序列 | `ATemplateSequenceActor` |
| `Set Sequence` | 设置要播放的模板序列（播放中不可调用） | `ATemplateSequenceActor` |
| `Get Sequence Player` | 获取序列播放器 | `ATemplateSequenceActor` |
| `Set Binding` | 设置模板序列根对象的绑定覆盖（将动画应用到指定 Actor） | `ATemplateSequenceActor` |

### 使用示例（蓝图描述）

**在运行时播放模板序列**：

1. 从任意事件（如 BeginPlay）连接到 `Create Template Sequence Player` 节点
2. 将你的 TemplateSequence 资产连接到 `TemplateSequence` 引脚
3. 配置 `PlaybackSettings`（是否自动播放、循环等）
4. 输出 `OutActor` 是 `ATemplateSequenceActor`，`ReturnValue` 是 `UTemplateSequencePlayer`
5. 如需将动画绑定到特定 Actor：对 OutActor 调用 `Set Binding`

**使用 Camera Shake Pattern**：

1. 创建一个 `UCameraShakeBase` 子类
2. 在其上添加 `USequenceCameraShakePattern` 作为 Pattern
3. 将 `CameraAnimationSequence` 属性指向你的 Camera Animation Sequence 资产
4. 调整 PlayRate、Scale、BlendInTime、BlendOutTime 等参数
5. 通过 `PlayerCameraManager->StartCameraShake()` 启动

## C++ 用法

### 头文件引入

```cpp
#include "TemplateSequencePlayer.h"
#include "TemplateSequenceActor.h"
#include "TemplateSequence.h"
#include "CameraAnimationSequence.h"
#include "CameraAnimationSequencePlayer.h"
#include "CameraAnimationSequenceSubsystem.h"
#include "SequenceCameraShake.h"
```

### 基本用法

**创建并播放 Template Sequence**（来源：`TemplateSequencePlayer.cpp`）

```cpp
// 通过静态工厂方法创建播放器和 Actor
ATemplateSequenceActor* OutActor = nullptr;
UTemplateSequencePlayer* Player = UTemplateSequencePlayer::CreateTemplateSequencePlayer(
    WorldContextObject,
    TemplateSequence,          // UTemplateSequence* 资产
    FMovieSceneSequencePlaybackSettings(),  // 播放设置
    OutActor                    // 输出的 Actor
);

// 将模板序列绑定到指定 Actor
if (OutActor)
{
    OutActor->SetBinding(TargetActor, true);  // true = 完全覆盖默认绑定
}

// 播放
Player->Play();
```

**在 Level Sequence Track 中嵌入 Template Sequence**：

```cpp
// 模板序列作为子 Section 嵌入到 Level Sequence 的 Object Binding 上
UTemplateSequenceTrack* Track = ...; // 通过 Sequencer UI 或代码获取
UTemplateSequenceSection* Section = Cast<UTemplateSequenceSection>(
    Track->AddNewTemplateSequenceSection(KeyTime, TemplateSequence)
);

// 设置属性缩放
FTemplateSectionPropertyScale PropertyScale;
PropertyScale.ObjectBinding = SomeBindingGuid;
PropertyScale.PropertyBinding = SomePropertyBinding;
PropertyScale.PropertyScaleType = ETemplateSectionPropertyScaleType::FloatProperty;
PropertyScale.FloatChannel = ...; // 缩放曲线
Section->AddPropertyScale(PropertyScale);
```

### 进阶用法

**Camera Animation Sequence 的底层播放**（来源：`CameraAnimationSequencePlayer.cpp`, `SequenceCameraShake.cpp`）

Camera Animation Sequence 使用轻量级的 `UCameraAnimationSequencePlayer`（不依赖 Actor），并通过 `UCameraAnimationSequenceCameraStandIn` 作为摄像机属性的代理对象：

```cpp
// 创建 Camera Animation Sequence Player
UCameraAnimationSequencePlayer* CameraPlayer = NewObject<UCameraAnimationSequencePlayer>();

// 初始化，可选起始帧偏移和持续时间覆盖
CameraPlayer->Initialize(CameraAnimationSequence, StartOffset, DurationOverride);

// 绑定到 CameraStandIn（代理摄像机对象）
UCameraAnimationSequenceCameraStandIn* StandIn = NewObject<UCameraAnimationSequenceCameraStandIn>();
StandIn->Initialize(CameraAnimationSequence);
CameraPlayer->SetBoundObjectOverride(StandIn);

// 开始播放
CameraPlayer->Play(bLoop, bRandomStartTime);

// 每帧更新
CameraPlayer->Update(NewFrameTime);

// 从 StandIn 获取动画后的摄像机属性
FTransform AnimatedTransform = StandIn->GetTransform();
float AnimatedFOV = StandIn->FieldOfView;
FPostProcessSettings AnimPP = StandIn->PostProcessSettings;
```

**CameraAnimationSequenceSubsystem 管理全局 Linker**：

```cpp
// 获取全局 Camera Animation 子系统
UCameraAnimationSequenceSubsystem* Subsystem =
    UCameraAnimationSequenceSubsystem::GetCameraAnimationSequenceSubsystem(World);

// 子系统持有全局的 Entity System Linker 和 Runner
// 所有 Camera Animation 共享同一个 Linker，避免重复实体化
UMovieSceneEntitySystemLinker* Linker = Subsystem->GetLinker();
TSharedPtr<FMovieSceneEntitySystemRunner> Runner = Subsystem->GetRunner();
```

## 架构概览

TemplateSequence 的核心设计分为三层：

### 1. 资产层（Asset）

```
UMovieSceneSequence
└── UTemplateSequence           ← 通用模板序列
    └── UCameraAnimationSequence ← 摄像机专用模板序列
```

`UTemplateSequence` 内部包含一个 `UMovieScene`，其第一个 spawnable 即为"root spawnable"（模板对象）。当模板序列被实例化时，这个 root spawnable 可以被绑定覆盖到任何实际对象上。

`BoundActorClass` 记录了该模板序列绑定的 Actor 类型，`BoundActorComponents` 记录了子组件的绑定映射。

### 2. 运行时层（Runtime）

```
ATemplateSequenceActor
├── UTemplateSequencePlayer     ← 标准播放器（用于 Level Sequence 嵌入场景）
│   └── FTemplateSequenceSpawnRegister
└── TemplateSequence (FSoftObjectPath)

UCameraAnimationSequencePlayer  ← 轻量播放器（用于 Camera Shake/Animation）
├── FSequenceCameraShakeSpawnRegister
├── UCameraAnimationSequenceCameraStandIn  ← 摄像机代理对象
└── UCameraAnimationSequenceSubsystem      ← 全局 WorldSubsystem
    ├── UCameraAnimationEntitySystemLinker
    └── FMovieSceneEntitySystemRunner
```

### 3. ECS 系统层（Entity Component System）

TemplateSequence 在 Sequencer 的 ECS 框架中注册了以下自定义系统：

| 系统 | 阶段 | 职责 |
|---|---|---|
| `UTemplateSequenceSystem` | Spawn | 管理模板序列的 binding override 建立/拆除 |
| `UTemplateSequencePropertyScalingInstantiatorSystem` | Instantiation | 跟踪哪些子序列实例有属性缩放 |
| `UTemplateSequencePropertyScalingEvaluatorSystem` | Scheduling | 在求值后对属性值应用缩放乘数 |
| `UCameraAnimationSpawnableSystem` | Spawn | 为摄像机动画处理 spawnable 对象（使用 StandIn） |
| `UCameraAnimationBoundObjectInstantiator` | Instantiation | 为摄像机动画实例化绑定对象 |

### 4. 编辑器层（Editor）

```
FTemplateSequenceEditorToolkit     ← 资产编辑器
FTemplateSequenceTrackEditor       ← Sequencer Track 编辑器
FTemplateSequenceCustomization     ← 通用模板序列的 Sequencer 定制
FCameraAnimationSequenceCustomization ← 摄像机动画的 Sequencer 定制
UTemplateSequenceFactoryNew        ← 创建资产工厂
UCameraAnimationSequenceFactoryNew ← 创建摄像机动画资产工厂
UTemplateSequenceCameraPreviewSystem ← 编辑器摄像机预览系统
```

## Demo 示例

### 最小示例：运行时播放 Template Sequence

**Build.cs 依赖**：

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
    "Engine",
    "TemplateSequence"
});
```

**MyComponent.h**：

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "MyComponent.generated.h"

class UTemplateSequence;
class UTemplateSequencePlayer;
class ATemplateSequenceActor;

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class UMyComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, Category="Animation")
    TObjectPtr<UTemplateSequence> AnimSequence;

    UFUNCTION(BlueprintCallable, Category="Animation")
    void PlayAnimation();

private:
    UPROPERTY()
    TObjectPtr<UTemplateSequencePlayer> Player;

    UPROPERTY()
    TObjectPtr<ATemplateSequenceActor> SequenceActor;
};
```

**MyComponent.cpp**：

```cpp
#include "MyComponent.h"
#include "TemplateSequence.h"
#include "TemplateSequencePlayer.h"
#include "TemplateSequenceActor.h"
#include "MovieSceneSequencePlaybackSettings.h"

void UMyComponent::PlayAnimation()
{
    if (!AnimSequence)
    {
        return;
    }

    UWorld* World = GetWorld();
    if (!World)
    {
        return;
    }

    FMovieSceneSequencePlaybackSettings Settings;
    Settings.bAutoPlay = true;
    Settings.bRestoreState = false;

    Player = UTemplateSequencePlayer::CreateTemplateSequencePlayer(
        World, AnimSequence, Settings, SequenceActor);

    if (SequenceActor && GetOwner())
    {
        SequenceActor->SetBinding(GetOwner(), true);
    }
}
```

### 最小示例：自定义 Camera Shake

**Build.cs 依赖**：

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
    "Engine",
    "TemplateSequence",
    "CinematicCamera"
});
```

**MyCameraShake.h**：

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Camera/CameraShakeBase.h"
#include "MyCameraShake.generated.h"

class UCameraAnimationSequence;

UCLASS()
class UMyCameraShake : public UCameraShakeBase
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, Category="Shake")
    TObjectPtr<UCameraAnimationSequence> ShakeSequence;

    UPROPERTY(EditAnywhere, Category="Shake", meta=(ClampMin="0.001"))
    float PlayRate = 1.0f;

    UPROPERTY(EditAnywhere, Category="Shake", meta=(ClampMin="0.0"))
    float Scale = 1.0f;
};
```

使用时，你需要在 Sequencer 中创建一个 Camera Animation Sequence 资产，将摄像机动画录制好，然后通过 `SequenceCameraShakePattern` 或自定义 `UCameraShakeBase` 子类来播放。

## 模块依赖

### TemplateSequence (Runtime)

| 模块 | 用途 |
|---|---|
| `Core` | 基础核心库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心（Actor、World 等） |
| `MovieScene` | Sequencer 核心框架 |
| `MovieSceneTracks` | Sequencer 标准 Track 实现 |
| `TimeManagement` | 时间管理和帧率转换 |
| `CinematicCamera` | CineCamera 组件支持 |
| `LevelSequence` | LevelSequence 框架（SpawnRegister 等） |

### TemplateSequenceEditor (Editor)

| 模块 | 用途 |
|---|---|
| `TemplateSequence` | Runtime 模块 |
| `Sequencer` | Sequencer 编辑器核心 |
| `SequencerCore` | Sequencer 核心 UI 框架 |
| `MovieSceneTools` | Sequencer 编辑器工具 |
| `LevelSequenceEditor` | LevelSequence 编辑器支持 |
| `AssetDefinition` | 资产定义系统 |
| `UnrealEd` | 编辑器核心 |
| `BlueprintGraph` | 蓝图图表支持 |
| `Kismet` | 蓝图编辑器 |
| `Slate` / `SlateCore` | UI 框架 |
| `PropertyEditor` | 属性编辑器（动态加载） |
| `LevelEditor` | 关卡编辑器（动态加载） |

## 维护状态

### 近期更新

1. **2025-08-20** `8dd5bb75` — Sequencer: Improved property traits variants, added type-erased property values, and unified many property track editors
   - 解读：对 Sequencer 属性系统进行了大规模改进，TemplateSequence 的属性缩放系统受到影响，属于框架级重构

2. **2025-08-05** `ae82625a` — Sequencer: Deprecate SetObjectGuid and GetBindings and FMovieSceneBinding constructors
   - 解读：Sequencer API 清理，标记了部分旧接口为废弃，TemplateSequence 的绑定相关代码需跟随更新

3. **2025-07-10** `9803c443` — Added UE_INLINE_GENERATED_CPP_BY_NAME to source files
   - 解读：编译优化，将 `.gen.cpp` 内联以减少编译时间

4. **2025-05-20** `c1d4eecb` — Replaced bool arguments with EFindObjectFlags
   - 解读：API 改进，用枚举替换布尔参数，提升可读性

5. **2025-04-23** `6ae57335` — Used UnrealGame build target to convert all files to have dllstorage
   - 解读：构建系统改进，将 `TEMPLATESEQUENCE_API` 宏应用于方法级而非类型级

### 维护评价

TemplateSequence 处于 **活跃维护** 状态：

- **创建时间**：2019 年 10 月，最初作为 UE4 的 Sequencer 模板化功能引入
- **更新频率**：2025 年有多次实质性更新，主要是跟随 Sequencer 框架的整体重构
- **维护状况**：虽然标记为 `IsBetaVersion=true`，但实际上已经被 Sequencer 的 Camera Cuts 系统深度依赖，是 UE5 摄像机动画基础设施的一部分
- **已知限制**：
  - `IsBetaVersion=true` 且 `EnabledByDefault=false`，需要手动在插件设置中启用（但作为 Sequencer 的内部依赖，实际已隐式启用）
  - `DocsURL` 为空，Epic 未提供官方文档
  - 模板序列的 Track 类型支持有限（`IsTrackSupportedImpl` 仅显式支持 SkeletalAnimation 和 Spawn Track）
- **推荐程度**：对于摄像机动画复用场景，这是 UE5 官方推荐且唯一的选择；对于通用模板化动画，属于实验性功能，建议谨慎使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MovieScene/TemplateSequence)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MovieScene/TemplateSequence/Source/TemplateSequence/Private/Tests)
