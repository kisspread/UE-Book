# Engine Cameras

> Default engine camera shakes and animations

| 属性 | 值 |
|---|---|
| 中文名 | 引擎相机 |
| 分类 | Cameras |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（动画序列、蓝图资产等） |
| 模块 | `EngineCameras` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-08-24 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/EngineCameras) | |

## 用途

`EngineCameras` 插件的核心目的是将 Unreal Engine 中“遗留的”（Legacy）相机抖动（Camera Shake）和相机动画序列（Camera Animation Sequence）功能从主引擎模块中剥离出来，形成一个独立的、便于维护的插件。

此举的动机是为了与新的 `GameplayCameras` 系统（计划在 UE 5.5 中作为实验性功能发布）进行清晰的分离。插件不仅承载了旧的相机行为，还为未来重构 `APlayerCameraManager` 以更好地支持自定义相机系统预留了位置。简而言之，它确保了旧有相机功能的向后兼容性和独立性。

## 使用场景

- **实现基础的相机抖动效果**：如爆炸冲击、武器后坐力、角色受击等。可以直接使用或继承 `ULegacyCameraShake`。
- **播放基于序列的相机动画**：使用 `UCameraAnimationSequence` 资产创建平滑的、由关键帧驱动的相机移动，常用于过场动画、技能特效或UI交互反馈。
- **需要对相机抖动/动画进行精细控制**：通过 `FCameraAnimationParams` 或 `FROscillator`、`FVOscillator` 等结构体精确调整混合时间、播放空间、振荡波形等参数。
- **维护旧版本项目**：项目如果从 UE 5.4 或更早版本升级而来，依赖于 `MatineeCameraShake` 等旧API，本插件提供了完整的向后兼容支持。

## 蓝图用法

本插件的主要蓝图功能围绕“播放、查询、停止相机动画”和“启动相机抖动”展开。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Play Camera Animation` | 播放一个相机动画序列，并返回一个句柄。 | `UEngineCamerasSubsystem` |
| `Stop Camera Animation` | 根据句柄停止一个特定的相机动画。 | `UEngineCamerasSubsystem` |
| `Stop All Camera Animations Of` | 停止所有播放中的指定序列的动画实例。 | `UEngineCamerasSubsystem` |
| `Is Camera Animation Active` | 检查某个相机动画是否正在播放。 | `UEngineCamerasSubsystem` |
| `Start Legacy Camera Shake` | 启动一个旧版相机抖动类实例。 | `ULegacyCameraShake` |
| `Get Camera Animation Camera Modifier` | 获取当前玩家控制器的相机动画修改器。 | `UCameraAnimationCameraModifier` |

### 使用示例（蓝图描述）

1.  **播放相机动画**：
    *   首先，通过 `Get Engine Cameras Subsystem` 节点获取世界子系统。
    *   连接 `Play Camera Animation` 节点，指定玩家控制器、要播放的序列资产（`UCameraAnimationSequence`）以及参数（`FCameraAnimationParams`，可设置播放速率、缩放、循环等）。
    *   将返回的 `FCameraAnimationHandle` 存储起来，用于后续控制（如停止或检查状态）。

2.  **启动带振荡的相机抖动**：
    *   从一个 `PlayerCameraManager` 引用开始。
    *   使用 `Start Legacy Camera Shake` 节点，指定一个继承自 `ULegacyCameraShake` 的蓝图类。
    *   可在该蓝图类中配置 `RotOscillation`、`LocOscillation` 等结构体来定义抖动模式。

## C++ 用法

### 头文件引入

```cpp
#include "EngineCamerasSubsystem.h"
#include "Animations/CameraAnimationCameraModifier.h"
#include "Shakes/LegacyCameraShake.h"
```

### 基本用法

以下代码演示了如何在 C++ 中播放一个相机动画序列。

```cpp
// 假设在 AMyCharacter 的某个函数内
void AMyCharacter::TriggerCameraShake()
{
    if (UWorld* World = GetWorld())
    {
        // 1. 获取引擎相机子系统
        if (UEngineCamerasSubsystem* CameraSubsystem = UEngineCamerasSubsystem::GetEngineCamerasSubsystem(World))
        {
            // 2. 准备动画参数
            FCameraAnimationParams Params;
            Params.Scale = 1.5f;
            Params.bLoop = false;

            // 3. 播放动画 (MyCameraSequence 是在编辑器中创建的 UCameraAnimationSequence 资产)
            if (UCameraAnimationSequence* Sequence = MyCameraSequence)
            {
                FCameraAnimationHandle Handle = CameraSubsystem->PlayCameraAnimation(
                    GetController<APlayerController>(),
                    Sequence,
                    Params
                );

                // 可以将 Handle 存储起来用于后续停止等操作
                CurrentAnimHandle = Handle;
            }
        }
    }
}
```

### 进阶用法

使用旧版相机抖动类创建一个自定义的爆炸抖动。

```cpp
// MyExplosionShake.h
UCLASS()
class UMyExplosionShake : public ULegacyCameraShake
{
    GENERATED_BODY()
public:
    UMyExplosionShake()
    {
        // 配置持续时间
        OscillationDuration = 0.5f;
        OscillationBlendInTime = 0.1f;
        OscillationBlendOutTime = 0.3f;

        // 配置旋转振荡 (剧烈但快速的衰减)
        RotOscillation.Pitch.Amplitude = 5.0f;
        RotOscillation.Pitch.Frequency = 20.0f;
        RotOscillation.Yaw.Amplitude = 3.0f;
        RotOscillation.Yaw.Frequency = 15.0f;

        // 配置位置振荡 (轻微的位移)
        LocOscillation.Z.Amplitude = 2.0f;
        LocOscillation.Z.Frequency = 10.0f;
    }
};

// 使用处
void AMyActor::Explode()
{
    if (APlayerController* PC = GetWorld()->GetFirstPlayerController())
    {
        if (APlayerCameraManager* PCM = PC->PlayerCameraManager)
        {
            // 启动自定义抖动
            ULegacyCameraShake* ShakeInstance = ULegacyCameraShake::StartLegacyCameraShake(
                PCM,
                UMyExplosionShake::StaticClass(),
                1.0f, // Scale
                ECameraShakePlaySpace::CameraLocal
            );
        }
    }
}
```

## Demo 示例

一个最小的可编译示例，展示如何通过一个自定义Actor触发相机抖动和动画。

**MyCameraTestActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Shakes/LegacyCameraShake.h"
#include "MyCameraTestActor.generated.h"

class UCameraAnimationSequence;

UCLASS()
class AMyCameraTestActor : public AActor
{
    GENERATED_BODY()
    
public:
    AMyCameraTestActor();

    UPROPERTY(EditAnywhere, Category = "Camera")
    TSubclassOf<ULegacyCameraShake> ShakeClassToUse;

    UPROPERTY(EditAnywhere, Category = "Camera")
    TObjectPtr<UCameraAnimationSequence> AnimSequenceToUse;

    UFUNCTION(BlueprintCallable)
    void TriggerEffects();

private:
    FCameraAnimationHandle CurrentAnimHandle;
};
```

**MyCameraTestActor.cpp**
```cpp
#include "MyCameraTestActor.h"
#include "Engine/World.h"
#include "Engine/EngineTypes.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/PlayerCameraManager.h"
#include "EngineCamerasSubsystem.h"
#include "Animations/CameraAnimationCameraModifier.h"

AMyCameraTestActor::AMyCameraTestActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyCameraTestActor::TriggerEffects()
{
    UWorld* World = GetWorld();
    if (!World) return;

    APlayerController* PC = World->GetFirstPlayerController();
    if (!PC) return;

    // 1. 播放相机动画序列
    UEngineCamerasSubsystem* SubSystem = UEngineCamerasSubsystem::GetEngineCamerasSubsystem(World);
    if (SubSystem && AnimSequenceToUse)
    {
        FCameraAnimationParams Params;
        Params.PlayRate = 1.0f;
        Params.Scale = 1.0f;
        CurrentAnimHandle = SubSystem->PlayCameraAnimation(PC, AnimSequenceToUse, Params);
    }

    // 2. 启动相机抖动
    APlayerCameraManager* PCM = PC->PlayerCameraManager;
    if (PCM && ShakeClassToUse)
    {
        ULegacyCameraShake::StartLegacyCameraShake(PCM, ShakeClassToUse, 1.0f, ECameraShakePlaySpace::CameraLocal);
    }
}
```

## 模块依赖

该插件自身依赖于 `TemplateSequence` 插件。
在构建你的模块时，如果需要使用此插件的功能，需要在你的 `.Build.cs` 文件中添加以下依赖：

| 模块 | 用途 |
|---|---|
| `EngineCameras` | 本插件的核心模块 |
| `AnimGraphRuntime` | 用于支持 `UCameraAnimationSequence` 的动画蓝图功能 |
| `GameplayTags` | `FCameraAnimationParams` 等结构体中使用了 GameplayTag |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏至新版格式。 |
| 2025-06-26 | `ec900998` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. | 为源文件添加内联生成宏，优化编译。 |
| 2025-05-07 | `ee22987e` | Don't restart a camera animation blend out when reaching the blend out time if we were already stopp | 修复相机动画混合输出逻辑，避免重复开始。 |
| 2025-04-23 | `6ae57335` | Used UnrealGame build target to find and convert all files to have dllstorage on methods/staticvar i | 为构建目标统一添加DLL导出标记。 |
| 2025-02-12 | `ef64d6c3` | Engine Cameras: API for EngineCamerasSubsystem | 完善 `EngineCamerasSubsystem` 的API接口。 |

### 维护评价

`EngineCameras` 是一个相对较新的插件（创建于2024年8月），旨在为UE的相机系统提供一个清晰的过渡和向后兼容方案。

*   **活跃维护**：从提交记录看，该插件在创建后的一年内有多次提交，内容涉及API完善、编译优化和逻辑修复，表明Epic Games仍在积极维护它。
*   **功能稳定**：它封装了旧有功能，API相对稳定，主要作为“遗产”代码的容器和提供向后兼容。
*   **推荐使用**：对于新项目，如果需要简单的相机抖动或序列动画，且不想直接使用更实验性的`GameplayCameras`系统，本插件是一个可靠且官方支持的选择。对于从旧版本升级的项目，它是保证功能正常的关键组件。
*   **注意事项**：它的设计初衷是向后兼容，未来可能会被更现代的`GameplayCameras`系统逐步取代。但对于UE 5.x的大多数项目而言，它仍然是实现相关功能的标准方式。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/EngineCameras)
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Cameras/EngineCameras/Source/EngineCameras/Private/Tests/)