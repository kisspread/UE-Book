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

`TemplateSequence` 插件的核心是**模板序列 (Template Sequence)** 的运行时支持。模板序列是一种特殊的 `UMovieSceneSequence`，它定义了一个可重复使用的动画蓝图（例如镜头动画、对象动画），并可以在场景中多次实例化。

插件主要解决以下问题：
1.  **序列复用**：允许将一段复杂的动画（如摄像机运动）定义为模板，并在多个地方以不同的配置（如绑定到不同的对象）重复播放，而无需复制序列本身。
2.  **相机抖动与动画**：提供专门的 `UCameraAnimationSequence` 类及其播放器，用于高效地播放基于序列的相机抖动效果。这通过一个全局的 `UCameraAnimationSequenceSubsystem` 进行管理，优化了性能。
3.  **序列内属性缩放**：允许在父序列中嵌入模板序列时，对其内部的特定属性（如浮点数、变换的平移或旋转部分）进行缩放，提供了更灵活的动画控制。

## 使用场景

-   你制作了一个精致的过场镜头动画，并希望在不同关卡、不同摄像机位置重复使用它 → 将动画定义为 `UCameraAnimationSequence`。
-   你需要为游戏中的爆炸、命中等事件创建可配置且性能良好的相机抖动效果 → 使用 `USequenceCameraShakePattern`。
-   你有一个控制车辆或角色动画的序列，并希望在游戏逻辑中通过代码或蓝图控制其播放，同时能将动画效果应用到场景中的不同实例上 → 使用 `ATemplateSequenceActor`。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Template Sequence Player` | 静态函数，为指定的模板序列创建播放器和对应的 Actor，返回播放器引用 | `UTemplateSequencePlayer` |
| `Get Sequence` | 获取 Actor 当前关联的模板序列资产 | `ATemplateSequenceActor` |
| `Load Sequence` | 异步加载并返回 Actor 关联的模板序列 | `ATemplateSequenceActor` |
| `Set Sequence` | 设置 Actor 需要播放的模板序列资产 | `ATemplateSequenceActor` |
| `Get Sequence Player` | 获取 Actor 内部的序列播放器 | `ATemplateSequenceActor` |
| `Set Binding` | 设置模板序列的根对象绑定覆盖，将序列动画应用到指定的 Actor 上 | `ATemplateSequenceActor` |

### 使用示例（蓝图描述）

1.  **动态创建并播放模板序列**：
    *   使用 `Create Template Sequence Player` 节点，传入你的 `UTemplateSequence` 资产和播放设置。
    *   该节点会输出一个 `ATemplateSequenceActor` 和对应的 `UTemplateSequencePlayer`。
    *   可以直接使用返回的播放器调用 `Play`、`Stop` 等控制函数。

2.  **在场景中放置并配置模板序列 Actor**：
    *   在场景中放置一个 `ATemplateSequenceActor`。
    *   在其细节面板中，设置 `Template Sequence` 属性为你想要的序列资产。
    *   使用 `Set Binding` 节点或其 `Binding Override` 属性，将序列绑定到场景中的另一个 Actor（`Target Actor`）。
    *   使用返回的 `Sequence Player` 或 Actor 本身的播放设置来控制播放。

## C++ 用法

### 头文件引入

```cpp
#include "TemplateSequence.h"
#include "TemplateSequenceActor.h"
#include "TemplateSequencePlayer.h"
#include "SequenceCameraShake.h" // 用于相机抖动
```

### 基本用法

**创建并播放一个模板序列**

```cpp
// 假设 TemplateSequenceAsset 是一个已加载的 UTemplateSequence* 指针
// World 是当前的 UWorld* 指针

FMovieSceneSequencePlaybackSettings Settings;
Settings.bAutoPlay = true;

ATemplateSequenceActor* OutActor = nullptr;
UTemplateSequencePlayer* Player = UTemplateSequencePlayer::CreateTemplateSequencePlayer(
    World,
    TemplateSequenceAsset,
    Settings,
    OutActor
);

if (Player)
{
    // 播放器已自动开始播放，也可以手动控制
    // Player->Play();
    // Player->Stop();
}
```
*（参考 `Public/TemplateSequencePlayer.h` 中的 `CreateTemplateSequencePlayer` 函数）*

**使用 ATemplateSequenceActor 绑定到目标**

```cpp
// 假设已在场景中获取或 Spawn 了 ATemplateSequenceActor* SequenceActor
// TargetActor 是你希望应用动画效果的 AActor* 指针

// 设置要播放的序列
SequenceActor->SetSequence(MyTemplateSequence);

// 将序列的根对象绑定覆盖设置为目标 Actor
SequenceActor->SetBinding(TargetActor, true);

// 获取播放器并控制播放
if (UTemplateSequencePlayer* Player = SequenceActor->GetSequencePlayer())
{
    Player->PlayLooping();
}
```
*（参考 `Public/TemplateSequenceActor.h` 中的 `SetSequence` 和 `SetBinding` 函数）*

### 进阶用法

**创建序列化相机抖动 (Camera Shake)**

```cpp
// 在配置相机抖动效果的类中（如 APlayerCameraManager 或自定义抖动配置）
UCameraShakeBase* CreateCameraShakeInstance()
{
    USequenceCameraShakePattern* ShakePattern = NewObject<USequenceCameraShakePattern>();
    ShakePattern->Sequence = MyCameraAnimationSequence; // UCameraAnimationSequence*
    ShakePattern->PlayRate = 1.0f;
    ShakePattern->Scale = 1.0f;
    ShakePattern->BlendInTime = 0.2f;
    ShakePattern->BlendOutTime = 0.5f;

    UCameraShakeBase* CameraShake = UCameraShakeBase::StartCameraShake(
        PlayerCameraManager,
        UCameraShakeBase::StaticClass(),
        1.0f, // Scale
        ECameraShakePlaySpace::World,
        FRotator::ZeroRotator
    );

    if (CameraShake)
    {
        // 将配置好的模式应用到抖动实例上
        CameraShake->SetRootShakePattern(ShakePattern);
    }

    return CameraShake;
}
```
*（参考 `Public/SequenceCameraShake.h` 中的 `USequenceCameraShakePattern` 类及其属性）*

## Demo 示例

**MyTemplateSequenceDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyTemplateSequenceDemo.generated.h"

class UTemplateSequence;
class ATemplateSequenceActor;
class UTemplateSequencePlayer;

UCLASS()
class AMyTemplateSequenceDemo : public AActor
{
    GENERATED_BODY()

public:
    AMyTemplateSequenceDemo();

protected:
    virtual void BeginPlay() override;

    UPROPERTY(EditAnywhere, Category = "Demo")
    TObjectPtr<UTemplateSequence> DemoSequence;

    UPROPERTY()
    TObjectPtr<ATemplateSequenceActor> SequenceActor;

    UPROPERTY()
    TObjectPtr<UTemplateSequencePlayer> SequencePlayer;

    UFUNCTION()
    void OnSequenceFinished();
};
```

**MyTemplateSequenceDemo.cpp**
```cpp
#include "MyTemplateSequenceDemo.h"
#include "TemplateSequence.h"
#include "TemplateSequenceActor.h"
#include "TemplateSequencePlayer.h"
#include "MovieSceneSequencePlayer.h"

AMyTemplateSequenceDemo::AMyTemplateSequenceDemo()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyTemplateSequenceDemo::BeginPlay()
{
    Super::BeginPlay();

    if (!DemoSequence || !GetWorld())
    {
        return;
    }

    // 配置播放设置
    FMovieSceneSequencePlaybackSettings Settings;
    Settings.bAutoPlay = false; // 我们手动控制开始
    Settings.LoopCount.Value = 0; // 播放一次

    // 创建播放器和 Actor
    SequencePlayer = UTemplateSequencePlayer::CreateTemplateSequencePlayer(
        GetWorld(),
        DemoSequence,
        Settings,
        SequenceActor
    );

    if (SequencePlayer && SequenceActor)
    {
        // 可以选择绑定到自身或其他 Actor
        // SequenceActor->SetBinding(AnotherActor);

        // 监听播放完成事件
        SequencePlayer->OnFinished.AddDynamic(this, &AMyTemplateSequenceDemo::OnSequenceFinished);

        // 开始播放
        SequencePlayer->Play();

        UE_LOG(LogTemp, Log, TEXT("Template Sequence Demo Started: %s"), *DemoSequence->GetName());
    }
}

void AMyTemplateSequenceDemo::OnSequenceFinished()
{
    UE_LOG(LogTemp, Log, TEXT("Template Sequence Demo Finished."));
}
```

## 模块依赖

该插件依赖于 MovieScene 和 LevelSequence 生态系统。要使用此插件，你的模块通常需要依赖：

| 模块 | 用途 |
|---|---|
| `MovieScene` | 核心序列框架，提供序列、轨道、节等基础类 |
| `LevelSequence` | 提供关卡序列播放器、Spawn Register 等基础运行时功能 |
| `CameraShakeBase` (Engine) | 提供 `UCameraShakePattern` 基类，用于 `USequenceCameraShakePattern` |

*注：标准依赖如 `Core`, `CoreUObject`, `Engine` 等已省略。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量转为浮点数时产生的编译器警告。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将过时的 `UE_LOG` 宏迁移至新的 `UE_LOGF` 宏。 |
| 2026-04-10 | `c03b3afd` | PR #14610: Rep layout mismatch in level sequence player due to with editoronly data property | 修复因仅编辑器属性导致关卡序列播放器复制布局不匹配的问题。 |
| 2026-02-20 | `49054c9f` | Sequencer: Add Bake Transform to object binding menu | 在序列器对象绑定菜单中添加“烘焙变换”功能。 |
| 2026-02-11 | `5919e4fa` | Remove 7 virtual functions in UObject (either deprecated or toolonly) | 移除 UObject 中的 7 个虚函数（已弃用或仅工具函数）。 |

### 维护评价

`TemplateSequence` 插件创建于 **2019年**，已有约 7 年历史。从 git 历史看，它在 **2026 年仍有持续的功能性更新和编译修复**（如修复浮点警告、迁移日志宏、修复复制问题），表明它**仍在活跃维护中**，是引擎动画和相机系统的重要组成部分。

**注意**：该插件在 `.uplugin` 中标记为 **`IsBetaVersion: true`** 且 **`EnabledByDefault: false`**，这意味着它仍处于**实验性阶段**，API 和功能可能在未来版本中发生变化。使用前需在项目设置中手动启用。

**推荐**：如果你需要实现可复用的动画序列或高级相机抖动，该插件是官方提供的强大工具。鉴于其仍在维护且为 Epic 官方插件，可以放心用于生产环境，但需注意其实验性状态，并关注后续版本更新日志中的兼容性说明。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/TemplateSequence)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/TemplateSequence/Source/TemplateSequence/Private/Tests)