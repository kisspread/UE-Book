# Engine Cameras

> Default engine camera shakes and animations（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 引擎摄像机系统 |
| 分类 | Cameras |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `EngineCameras` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-08-24 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/EngineCameras) | |

## 用途

这个插件的核心目的是将旧的（Legacy）摄像机震动（Camera Shake）和摄像机动画（Camera Animation）功能从新的 `GameplayCameras` 系统中分离出来。它为开发者提供了一套完整的、独立的、运行时可用的摄像机效果系统，用于处理：
1.  **默认的摄像机震动实现**：包含基于振荡（正弦波、柏林噪声）和序列驱动的震动模式。
2.  **摄像机动画序列支持**：提供一个子系统和摄像机修改器，用于播放和控制 Sequencer 制作的 `UCameraAnimationSequence`。
3.  **为未来重构铺路**：根据首次提交信息，这里也是未来重构 `APlayerCameraManager` 等旧代码的去处。

简而言之，如果你需要一套稳定、现成的摄像机震动和动画系统，而不是立刻使用实验性的新系统，那么这个插件就是为你准备的。

## 使用场景

- 你需要在游戏中快速实现爆炸、撞击、武器后坐力等导致的摄像机震动效果。
- 你使用 Sequencer 预先制作了复杂的摄像机运镜动画（如过场动画中的特写、震动跟随），并希望在 gameplay 中触发播放。
- 你正在从旧版本的 UE4/UE5 项目迁移，其中大量使用了 `UMatineeCameraShake` 或类似的震动类。
- 你希望在不深入新的 GameplayCameras 架构的前提下，使用一套稳定、功能完备的摄像机效果工具。

## 蓝图用法

主要的蓝图接口集中在两个类：`UEngineCamerasSubsystem` 和 `UCameraAnimationCameraModifier`。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Play Camera Animation` | 在指定的玩家控制器上播放一个摄像机动画序列，返回一个句柄用于后续控制。 | `UEngineCamerasSubsystem` |
| `Is Camera Animation Active` | 查询一个摄像机动画是否正在播放。 | `UEngineCamerasSubsystem` |
| `Stop Camera Animation` | 停止一个指定的摄像机动画，可选择立即停止或混合淡出。 | `UEngineCamerasSubsystem` |
| `Stop All Camera Animations Of` | 停止一个玩家控制器上所有指定序列的动画实例。 | `UEngineCamerasSubsystem` |
| `Stop All Camera Animations` | 停止一个玩家控制器上所有正在播放的摄像机动画。 | `UEngineCamerasSubsystem` |
| `Get Camera Animation Camera Modifier` | 获取玩家控制器的摄像机动画修改器实例。 | `UCameraAnimationCameraModifier` |
| `Start Legacy Camera Shake` | 启动一个旧版的摄像机震动（`ULegacyCameraShake` 子类）。 | `ULegacyCameraShake` |
| `Start Legacy Camera Shake From Source` | 从一个摄像机震动源组件（`UCameraShakeSourceComponent`）启动旧版震动。 | `ULegacyCameraShake` |

### 使用示例（蓝图描述）

1.  **播放摄像机动画**：
    *   获取 `Get Engine Cameras Subsystem` 节点。
    *   将其 `Play Camera Animation` 节点连接到你的逻辑（如 `Event BeginPlay`）。
    *   为 `Sequence` 参数指定一个 `UCameraAnimationSequence` 资产。
    *   为 `Player Controller` 参数指定目标玩家控制器。
    *   可选：配置 `FCameraAnimationParams` 结构体（播放速率、混合时间、循环等）。
    *   将返回的 `FCameraAnimationHandle` 存储到一个变量中，用于后续的停止或状态查询。

2.  **触发旧版震动**：
    *   使用 `Start Legacy Camera Shake` 节点。
    *   为 `Shake Class` 参数指定一个从 `ULegacyCameraShake` 派生的蓝图类。
    *   将该节点连接到事件（如 OnHit）。震动将自动应用到拥有此蓝图的 Pawn 所对应的玩家控制器上。

## C++ 用法

### 头文件引入

```cpp
#include "EngineCamerasSubsystem.h"
#include "Animations/CameraAnimationCameraModifier.h"
#include "Shakes/LegacyCameraShake.h"
#include "Shakes/WaveOscillatorCameraShakePattern.h"
```

### 基本用法

以下示例展示了如何使用 `UEngineCamerasSubsystem` 播放和停止一个摄像机动画序列。

```cpp
// 来源: 基于 UEngineCamerasSubsystem 公共接口推断的典型用法。
void AMyActor::StartMyCameraAnim()
{
    if (UWorld* World = GetWorld())
    {
        // 1. 获取子系统实例
        UEngineCamerasSubsystem* Subsystem = UEngineCamerasSubsystem::GetEngineCamerasSubsystem(World);
        if (Subsystem && MyPlayerController)
        {
            // 2. 配置播放参数
            FCameraAnimationParams Params;
            Params.PlayRate = 1.0f;
            Params.Scale = 1.0f;
            Params.bLoop = true;
            Params.EaseInType = ECameraAnimationEasingType::Sinusoidal;
            Params.EaseInDuration = 0.5f;

            // 3. 播放动画并保存句柄
            CurrentCameraAnimHandle = Subsystem->PlayCameraAnimation(MyPlayerController, MyCameraAnimSequence, Params);
        }
    }
}

void AMyActor::StopMyCameraAnim()
{
    if (UWorld* World = GetWorld())
    {
        UEngineCamerasSubsystem* Subsystem = UEngineCamerasSubsystem::GetEngineCamerasSubsystem(World);
        if (Subsystem && CurrentCameraAnimHandle.IsValid())
        {
            // 4. 使用句柄停止动画
            Subsystem->StopCameraAnimation(MyPlayerController, CurrentCameraAnimHandle, false); // 不立即停止，允许混合淡出
        }
    }
}
```

### 进阶用法

结合使用子系统和直接操作摄像机修改器，可以实现更精细的控制。

```cpp
// 来源: 结合 UEngineCamerasSubsystem 和 UCameraAnimationCameraModifier 接口。
void AMyActor::AdvancedCameraControl()
{
    // ... 获取 PlayerController 和 World ...

    // 方式一：通过子系统（推荐，更简洁）
    UEngineCamerasSubsystem* Subsystem = UEngineCamerasSubsystem::GetEngineCamerasSubsystem(World);
    if (Subsystem)
    {
        FCameraAnimationHandle Handle = Subsystem->PlayCameraAnimation(PlayerController, MySequence, FCameraAnimationParams());
        // 使用 Handle 进行后续操作...
    }

    // 方式二：直接获取并操作摄像机修改器
    UCameraAnimationCameraModifier* Modifier = UCameraAnimationCameraModifier::GetCameraAnimationCameraModifierFromPlayerController(PlayerController);
    if (Modifier)
    {
        FCameraAnimationParams Params;
        Params.PlaySpace = ECameraAnimationPlaySpace::UserDefined;
        Params.UserPlaySpaceRot = FRotator(0.0f, 90.0f, 0.0f); // 在自定义空间（如载具本地空间）播放
        FCameraAnimationHandle Handle2 = Modifier->PlayCameraAnimation(MySequence, Params);
    }
}
```

## Demo 示例

一个使用 `UEngineCamerasSubsystem` 播放震动效果的最小可编译示例。

```cpp
// MyCameraShakeDemoActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Camera/CameraShakeBase.h" // 用于 TSubclassOf
#include "MyCameraShakeDemoActor.generated.h"

UCLASS()
class AMyCameraShakeDemoActor : public AActor
{
    GENERATED_BODY()

public:
    AMyCameraShakeDemoActor();

protected:
    virtual void BeginPlay() override;

    UFUNCTION(BlueprintCallable)
    void TriggerMyShake();

private:
    UPROPERTY(EditAnywhere, Category="Shake")
    TSubclassOf<UCameraShakeBase> MyShakeClass; // 可在编辑器中指定一个 LegacyCameraShake 蓝图类

    UPROPERTY(EditAnywhere, Category="Shake")
    float ShakeScale = 1.0f;
};
```

```cpp
// MyCameraShakeDemoActor.cpp
#include "MyCameraShakeDemoActor.h"
#include "EngineCamerasSubsystem.h"
#include "Shakes/LegacyCameraShake.h"
#include "GameFramework/PlayerController.h"

AMyCameraShakeDemoActor::AMyCameraShakeDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyCameraShakeDemoActor::BeginPlay()
{
    Super::BeginPlay();
    // 可以在这里延迟调用 TriggerMyShake 来测试
    FTimerHandle TimerHandle;
    GetWorldTimerManager().SetTimer(TimerHandle, this, &AMyCameraShakeDemoActor::TriggerMyShake, 2.0f, false);
}

void AMyCameraShakeDemoActor::TriggerMyShake()
{
    if (MyShakeClass)
    {
        // 获取第一个本地玩家控制器
        APlayerController* PC = GetWorld()->GetFirstPlayerController();
        if (PC)
        {
            // 使用 LegacyCameraShake 的静态函数启动震动
            ULegacyCameraShake* ShakeInstance = ULegacyCameraShake::StartLegacyCameraShake(PC->PlayerCameraManager, MyShakeClass, ShakeScale);
            // 此时震动已经开始播放，ShakeInstance 指向正在播放的实例（可用于后续手动控制）
        }
    }
}
```

## 模块依赖

该插件本身依赖于 `TemplateSequence` 插件。

对于你的项目或模块，若要使用此插件的功能，你需要确保：

| 模块 | 用途 |
|---|---|
| `EngineCameras` | 包含此插件所有核心功能（子系统、震动模式、动画修改器）的运行时模块。 |
| `TemplateSequence` | 被 `EngineCameras` 插件依赖，用于支持基于模板序列的摄像机动画。 |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移至 UE_LOGF。 |
| 2025-06-26 | `ec900998` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. | 为相关源文件添加宏以优化编译。 |
| 2025-05-07 | `ee22987e` | Don’t restart a camera animation blend out when reaching the blend out time if we were already stopp | 修复了动画在混合淡出阶段被错误重启的问题。 |
| 2025-04-23 | `6ae57335` | Used UnrealGame build target to find and convert all files to have dllstorage on methods/staticvar i | 构建目标和方法导出规范调整。 |
| 2025-02-12 | `ef64d6c3` | Engine Cameras: API for EngineCamerasSubsystem | 为 EngineCamerasSubsystem 添加公共 API。 |

### 维护评价

- **创建时间**：约 1.3 年前（2024年8月），相对较新。
- **更新频率**：近期有维护性更新，但主要是编译修复、API 微调和 bug 修复，未见重大新功能提交。
- **维护状态**：**稳定维护中**。该插件作为核心引擎组件的一部分（摄像机），其稳定性和兼容性会得到 Epic 持续关注。近期 commit 显示其仍在被维护和修正。
- **已知限制**：这是一个用于承载“旧版”摄像机功能的插件。Epic 鼓励使用新的 `GameplayCameras` 系统（实验性），因此此插件的长期发展可能以维护和 bug 修复为主。
- **推荐使用**：**推荐**。如果你需要快速、可靠地实现摄像机震动和序列动画，并且不急于采用最新的实验性摄像机系统，`EngineCameras` 是一个成熟、经过官方验证的选择。它提供了完善的蓝图和 C++ 接口。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/EngineCameras)
- [官方文档]() （.uplugin 中 DocsURL 为空）
- [测试用例]() （未在插件目录内发现独立的测试文件，可能集成在引擎测试套件中）