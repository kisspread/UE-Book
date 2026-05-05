# Actor Sequence (Experimental)

> Runtime for embedded actor sequences

| 属性 | 值 |
|---|---|
| 分类 | MovieScene |
| 默认启用 | ✅ true |
| 包含内容 | ❌ false |
| 模块 | ActorSequence (Runtime), ActorSequenceEditor (Editor) |
| 创建时间 | 2017-09-07 |
| 年龄标签 | 👴 老古董(>8年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MovieScene/ActorSequence) | |

## 用途

ActorSequence 是一个轻量级的 Sequencer 集成方案，允许你将 **MovieScene 动画直接嵌入到 Actor 内部**，而无需创建独立的 Level Sequence 资产。

核心思路：与 Level Sequence Actor 需要外部 `.uasset` 文件不同，ActorSequence 把序列数据作为 **组件的子对象** 存储在 Actor 自身内部。这意味着序列数据随 Actor 一起序列化、复制和管理，非常适合：

- 每个 Actor 实例拥有自己独立的、内嵌的动画时间线
- 蓝图中直接编辑组件动画，无需管理外部资产
- 简单的属性动画、变换动画、材质参数动画等场景

它本质上是 `UMovieSceneSequence` 的一个特化实现（`UActorSequence`），通过 `UActorSequenceComponent` 暴露给用户，底层使用与 Level Sequence 相同的 Sequencer 编辑器和 MovieScene 播放框架。

## 使用场景

- 你在做一个需要 **内嵌简单动画** 的 Actor（如门的开关、灯的闪烁、平台移动），不想为每个实例创建独立的 Level Sequence 资产 → 用 ActorSequence
- 你需要在 **蓝图中** 为 Actor 编辑属性动画，并希望动画数据随蓝图一起保存 → 用 ActorSequence
- 你需要一个 **每个 Actor 实例可独立控制播放** 的轻量动画方案 → 用 ActorSequence
- 你只需要 **运行时播放** 嵌入的序列，不需要 Sequencer 编辑器的全部功能 → 用 ActorSequence

**不推荐场景**：需要跨多个 Actor 协同的复杂动画、需要多个子序列嵌套、需要高级 Sequencer 功能（如 Master Sequence）→ 用 Level Sequence Actor。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Play Sequence` | 正向播放嵌入的序列 | `UActorSequenceComponent` |
| `Play Sequence Reverse` | 反向播放嵌入的序列 | `UActorSequenceComponent` |
| `Pause Sequence` | 暂停当前播放 | `UActorSequenceComponent` |
| `Stop Sequence` | 停止播放并重置 | `UActorSequenceComponent` |

所有节点位于 **Sequencer → Player** 分类下，均为 `BlueprintCallable`。

### 属性

| 属性 | 类型 | 说明 |
|---|---|---|
| `Playback Settings` | `FMovieSceneSequencePlaybackSettings` | 播放配置（循环、自动播放、播放速率等） |
| `Sequence` | `UActorSequence*` | 嵌入的序列数据（Instanced 子对象） |
| `Sequence Player` | `UActorSequencePlayer*` | 运行时播放器实例（Transient，自动生成） |

### 使用示例（蓝图描述）

**基本用法 — 自动播放动画：**

1. 在你的 Actor 蓝图中，添加 `Actor Sequence Component`
2. 在 Details 面板中，勾选 `Playback Settings → Auto Play`
3. 点击组件 Details 面板中的 **"Open in Tab"** 按钮，打开内嵌 Sequencer 编辑器
4. 在 Sequencer 中添加属性/变换轨道，编辑关键帧
5. 运行游戏时，动画自动播放

**手动控制播放：**

1. 获取 `Actor Sequence Component` 引用
2. 连接到 `Play Sequence` / `Pause Sequence` / `Stop Sequence` 节点
3. 例如：`OnComponentBeginOverlap` → `Play Sequence`

## C++ 用法

### 头文件引入

```cpp
#include "ActorSequenceComponent.h"
#include "ActorSequence.h"
#include "ActorSequencePlayer.h"
```

### 基本用法

`UActorSequenceComponent` 是 `UActorComponent` 的子类，可以像普通组件一样添加到 Actor 中：

```cpp
// 在 Actor 的构造函数中创建组件
AMyActor::AMyActor()
{
    SequenceComponent = CreateDefaultSubobject<UActorSequenceComponent>(TEXT("SequenceComponent"));
}
```

通过 C++ 控制播放：

```cpp
// 播放
SequenceComponent->PlaySequence();

// 暂停
SequenceComponent->PauseSequence();

// 停止
SequenceComponent->StopSequence();

// 反向播放（5.7 新增）
SequenceComponent->PlaySequenceReverse();
```

获取底层播放器和序列对象进行更精细的控制：

```cpp
UActorSequence* Sequence = SequenceComponent->GetSequence();
UActorSequencePlayer* Player = SequenceComponent->GetSequencePlayer();

if (Player)
{
    // 使用继承自 UMovieSceneSequencePlayer 的方法
    Player->Play();
    Player->SetPlaybackPosition(/* ... */);
    FFrameNumber CurrentFrame = Player->GetCurrentTime().GetFrame();
}
```

### 进阶用法

**对象绑定机制**：`UActorSequence` 通过 `FActorSequenceObjectReference` 系统实现对象绑定，支持三种引用类型：

| 引用类型 | 说明 |
|---|---|
| `ContextActor` | 序列所属的 Actor 自身 |
| `ExternalActor` | 同 Level 中的外部 Actor（通过 GUID 引用） |
| `Component` | Actor 的组件（通过路径引用） |

```cpp
// 手动创建绑定
FGuid BindingId = MovieScene->AddPossessable(TEXT("MyComponent"), UStaticMeshComponent::StaticClass());
FActorSequenceObjectReference Ref = FActorSequenceObjectReference::CreateForComponent(MyComponent);
// 通过 UActorSequence::BindPossessableObject 内部会自动调用
```

**Console 变量配置**：

| CVar | 默认值 | 说明 |
|---|---|---|
| `ActorSequence.DefaultEvaluationType` | `0` | 0=帧锁定，1=子帧插值 |
| `ActorSequence.DefaultTickResolution` | `24000fps` | 新建序列的默认 tick 分辨率 |
| `ActorSequence.DefaultDisplayRate` | `30fps` | 新建序列的默认显示帧率 |

**支持的轨道类型**（通过 `IsTrackSupportedImpl`）：

- `UMovieSceneAudioTrack` — 音频
- `UMovieSceneEventTrack` — 事件
- `UMovieSceneMaterialParameterCollectionTrack` — 材质参数
- `UMovieSceneSkeletalAnimationTrack` — 骨骼动画
- `UMovieSceneTimeWarpTrack` — 时间扭曲

加上所有 `UMovieSceneSequence` 基类默认支持的轨道。

## Demo 示例

### 最小可运行示例

**MyAnimatedActor.h**：

```cpp
#pragma once

#include "GameFramework/Actor.h"
#include "MyAnimatedActor.generated.h"

class UActorSequenceComponent;

UCLASS()
class AMyAnimatedActor : public AActor
{
    GENERATED_BODY()

public:
    AMyAnimatedActor();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Animation")
    TObjectPtr<UActorSequenceComponent> SequenceComponent;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Mesh")
    TObjectPtr<UStaticMeshComponent> MeshComponent;

    /** 由碰撞触发播放动画 */
    UFUNCTION(BlueprintCallable, Category = "Animation")
    void TriggerAnimation();
};
```

**MyAnimatedActor.cpp**：

```cpp
#include "MyAnimatedActor.h"
#include "ActorSequenceComponent.h"
#include "Components/StaticMeshComponent.h"

AMyAnimatedActor::AMyAnimatedActor()
{
    // 创建网格组件
    MeshComponent = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
    RootComponent = MeshComponent;

    // 创建内嵌序列组件
    SequenceComponent = CreateDefaultSubobject<UActorSequenceComponent>(TEXT("Sequence"));
    // Sequence 组件会自动创建 UActorSequence 子对象
}

void AMyAnimatedActor::TriggerAnimation()
{
    if (SequenceComponent)
    {
        SequenceComponent->PlaySequence();
    }
}
```

**Build.cs 依赖**：

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
    "Engine",
    "ActorSequence"  // 运行时模块
});
```

> **注意**：编辑器中的 Sequencer 编辑功能由 `ActorSequenceEditor` 模块提供，该模块仅在 Editor 构建中可用。打包后的游戏只需要 `ActorSequence` 运行时模块。

## 模块依赖

### ActorSequence（Runtime 模块）

| 模块 | 用途 |
|---|---|
| `Core` | 基础核心库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心（Actor、Component 等） |
| `MovieScene` | MovieScene 序列框架 |
| `MovieSceneTracks` | MovieScene 轨道实现 |
| `TimeManagement` | 时间管理 |

### ActorSequenceEditor（Editor 模块）

| 模块 | 用途 |
|---|---|
| `ActorSequence` | 对应的运行时模块 |
| `Sequencer` | Sequencer 编辑器框架 |
| `MovieSceneTools` | MovieScene 编辑器工具 |
| `Kismet` | 蓝图编辑器集成 |
| `UnrealEd` | 编辑器核心 |
| `PropertyEditor` | Details 面板自定义（动态加载） |
| `LevelEditor` | 关卡编辑器集成（动态加载） |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-09-10 | `13ee80361ffd` | UMG: 在不支持的情况下禁用 Dynamic Possession 菜单 |
| 2025-07-14 | `b010bdd4ff0a` | **PR #13519**: 为 ActorSequenceComponent 添加 `PlayReverse` 反向播放功能 |
| 2025-06-26 | `a2e75189887d` | 添加 `UE_INLINE_GENERATED_CPP_BY_NAME` 宏（代码清理/编译优化） |

**解读**：

- 2025-07 的 `PlayReverse` 是一个重要的功能增强，补充了播放控制的完整性
- 其余更新为维护性改动和编辑器集成调整
- 更新频率约 2-3 个月一次，属于正常维护节奏

### 维护评价

- **年龄**：2017 年创建，至今约 8 年，属于老古董级插件
- **状态**：`IsBetaVersion = true`，仍标记为实验性（Experimental），但 `EnabledByDefault = true`
- **活跃度**：最近 3 个月内有实质性功能更新（PlayReverse），维护中
- **稳定性**：作为 UE 内置插件，自 2017 年以来一直在引擎中，虽然标记为实验性但持续维护
- **推荐**：✅ 推荐用于简单的内嵌动画场景。但注意它仍是实验性插件，API 可能在未来版本变化。对于复杂动画需求，建议使用 Level Sequence Actor。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MovieScene/ActorSequence)
- 官方文档：无（.uplugin 中 DocsURL 为空）
- [Level Sequence Actor 文档](https://docs.unrealengine.com/en-US/AnimatingObjects/Sequencer/overview/)（相关参考）
