# Engine Cameras

> Default engine camera shakes and animations

| 属性 | 值 |
|---|---|
| 中文名 | 引擎相机 |
| 分类 | Cameras |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `EngineCameras` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-08-24 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/EngineCameras) | |

## 用途

EngineCameras 插件是一个运行时模块，其核心目的是将 Unreal Engine 中传统的相机震动（Camera Shake）实现和相机动画播放系统从引擎核心代码中独立出来，形成一个模块化的插件。

从创建记录可以看出，此举是为了将 `APlayerCameraManager` 中的“遗留”相机管理代码逐步迁移至此插件，从而允许引擎新的实验性 `GameplayCameras` 系统独立发展。插件提供了：
1.  **传统相机震动**：基于振荡或 Perlin 噪声的屏幕抖动效果。
2.  **相机动画播放**：通过 `UCameraAnimationSequence` 资产驱动的、更复杂的相机运动和变换。
3.  **子系统接口**：提供了 `UEngineCamerasSubsystem` 世界子系统，简化了相机动画的播放与控制。

## 使用场景

-   **游戏反馈效果**：在爆炸、受到攻击、重型武器开火等场景，需要屏幕产生剧烈抖动以增强打击感时，使用 `ULegacyCameraShake` 或 `UPerlinNoiseCameraShakePattern`。
-   **剧情演出与镜头语言**：在过场动画或特定技能释放时，需要相机按照预设轨迹平滑移动、旋转或变焦，使用 `UCameraAnimationSequence` 进行播放。
-   **统一的相机控制**：当需要为一个玩家控制器（`APlayerController`）管理多个并行的相机震动或动画实例时，使用 `UEngineCamerasSubsystem` 或 `UCameraAnimationCameraModifier`。

## 蓝图用法

### 核心节点

#### 相机动画子系统 (`UEngineCamerasSubsystem`)

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Engine Cameras Subsystem` | 获取当前世界的引擎相机子系统实例 | `UEngineCamerasSubsystem` |
| `Play Camera Animation` | 在指定的玩家控制器上播放一个相机动画序列，返回一个句柄用于后续控制 | `UEngineCamerasSubsystem` |
| `Is Camera Animation Active` | 查询指定的相机动画是否仍在播放 | `UEngineCamerasSubsystem` |
| `Stop Camera Animation` | 停止播放指定的相机动画 | `UEngineCamerasSubsystem` |
| `Stop All Camera Animations Of` | 停止播放指定序列资产的所有实例 | `UEngineCamerasSubsystem` |
| `Stop All Camera Animations` | 停止播放所有正在运行的相机动画 | `UEngineCamerasSubsystem` |

#### 传统相机震动 (`ULegacyCameraShake`)

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Start Legacy Camera Shake` | 在玩家相机管理器上启动一个传统的相机震动类实例 | `ULegacyCameraShake` |
| `Start Legacy Camera Shake From Source` | 从一个相机震动源组件启动震动（受距离衰减影响） | `ULegacyCameraShake` |

#### 函数库与类型转换

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Conv_CameraAnimationCameraModifier` | 将玩家相机管理器（`APlayerCameraManager*`）自动转换为相机动画修改器，便于直接调用其播放接口 | `UEngineCameraAnimationFunctionLibrary` |
| `Conv_LegacyCameraShake` | 将基础相机震动（`UCameraShakeBase*`）安全地向下转型为传统震动类，以便访问其振荡参数 | `ULegacyCameraShakeFunctionLibrary` |
| `Conv_CameraAnimationPlaySpace` / `Conv_CameraShakePlaySpace` | 在 `ECameraAnimationPlaySpace` 和 `ECameraShakePlaySpace` 枚举之间转换 | `UEngineCameraAnimationFunctionLibrary` |

### 使用示例（蓝图描述）

1.  **播放一个简单的屏幕震动**：
    *   创建一个继承自 `ULegacyCameraShake` 的蓝图类，配置其 `RotOscillation` (旋转振荡) 和 `LocOscillation` (位置振荡) 参数。
    *   在事件图表中，获取 `Player Camera Manager` 节点，连接 `Start Legacy Camera Shake` 节点，并选择你创建的震动蓝图类作为 `Shake Class`。
    *   连接 `Scale` 参数控制强度。

2.  **播放一个过场动画相机**：
    *   创建一个 `UCameraAnimationSequence` 资产，在 Sequencer 中录制或编辑相机的运动。
    *   在事件图表中，使用 `Get Engine Cameras Subsystem` 节点获取子系统。
    *   连接 `Play Camera Animation` 节点，将玩家控制器、创建的序列资产和 `Camera Animation Params` 结构体传入。
    *   保存返回的 `Camera Animation Handle`。
    *   需要停止动画时，使用 `Stop Camera Animation` 节点并传入该句柄。

## C++ 用法

### 头文件引入

```cpp
#include "EngineCamerasSubsystem.h"
#include "Animations/CameraAnimationCameraModifier.h"
#include "Shakes/LegacyCameraShake.h"
```

### 基本用法

以下代码演示了如何通过子系统播放和停止相机动画。
*来源：`EngineCamerasSubsystem.h` 及相关接口分析*

```cpp
// 假设我们已经有了一个有效的玩家控制器和相机动画序列资产
APlayerController* MyPlayerController = GetWorld()->GetFirstPlayerController();
UCameraAnimationSequence* MyAnimationSequence = LoadObject<UCameraAnimationSequence>(nullptr, TEXT("/Game/MySequence"));

// 1. 获取引擎相机子系统
UEngineCamerasSubsystem* CameraSubsystem = UEngineCamerasSubsystem::GetEngineCamerasSubsystem(GetWorld());

// 2. 配置播放参数
FCameraAnimationParams AnimParams;
AnimParams.PlayRate = 1.0f;
AnimParams.Scale = 1.0f;
AnimParams.bLoop = false;
AnimParams.EaseInType = ECameraAnimationEasingType::Sinusoidal;
AnimParams.EaseInDuration = 0.3f;

// 3. 播放动画，获取句柄
FCameraAnimationHandle AnimHandle = CameraSubsystem->PlayCameraAnimation(MyPlayerController, MyAnimationSequence, AnimParams);

// 4. 稍后检查或停止动画
if (CameraSubsystem->IsCameraAnimationActive(MyPlayerController, AnimHandle))
{
    // ... 动画仍在播放
}
// 停止动画，使用混合退出
CameraSubsystem->StopCameraAnimation(MyPlayerController, AnimHandle, false);
```

### 进阶用法

直接访问和操作 `UCameraAnimationCameraModifier`，这提供了更底层的控制，但通常更推荐使用 `UEngineCamerasSubsystem`。
*来源：`CameraAnimationCameraModifier.h`*

```cpp
#include "Animations/CameraAnimationCameraModifier.h"

// 获取特定玩家的相机动画修改器
APlayerController* PlayerCtrl = ...;
UCameraAnimationCameraModifier* AnimModifier = UCameraAnimationCameraModifier::GetCameraAnimationCameraModifierFromPlayerController(PlayerCtrl);

if (AnimModifier)
{
    // 使用修改器直接播放动画，语法与子系统类似
    FCameraAnimationParams Params;
    Params.PlaySpace = ECameraAnimationPlaySpace::World; // 在世界空间播放
    
    UCameraAnimationSequence* Sequence = ...;
    FCameraAnimationHandle Handle = AnimModifier->PlayCameraAnimation(Sequence, Params);
    
    // ... 后续控制
}
```

## Demo 示例

下面是一个完整的最小化示例，演示如何在 C++ Actor 中触发一次传统相机震动。
*注意：需要为你的项目模块添加对 `EngineCameras` 插件的依赖。*

**MyActor.h**
```cpp
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

    UPROPERTY(EditAnywhere, Category = "Camera Shakes")
    TSubclassOf<class ULegacyCameraShake> ExplosionShakeClass;

    UFUNCTION(BlueprintCallable, Category = "Camera Shakes")
    void TriggerExplosionShake();

protected:
    virtual void BeginPlay() override;
};
```

**MyActor.cpp**
```cpp
#include "MyActor.h"
#include "Shakes/LegacyCameraShake.h"
#include "Kismet/GameplayStatics.h"

AMyActor::AMyActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyActor::BeginPlay()
{
    Super::BeginPlay();
    // 可以在此加载或赋值震动类资产
    // ExplosionShakeClass = LoadClass<ULegacyCameraShake>(...);
}

void AMyActor::TriggerExplosionShake()
{
    // 获取第一个玩家控制器的相机管理器
    APlayerController* PC = UGameplayStatics::GetPlayerController(GetWorld(), 0);
    if (PC && PC->PlayerCameraManager && ExplosionShakeClass)
    {
        // 启动传统相机震动
        ULegacyCameraShake* ShakeInstance = ULegacyCameraShake::StartLegacyCameraShake(
            PC->PlayerCameraManager,
            ExplosionShakeClass,
            1.0f, // 强度
            ECameraShakePlaySpace::CameraLocal,
            FRotator::ZeroRotator
        );
        
        // 你也可以在这里对 ShakeInstance 进行进一步配置
        // ShakeInstance->RotOscillation.Pitch.Amplitude = 5.0f;
    }
}
```

## 模块依赖

该插件有一个独特的运行时依赖：
| 模块 | 用途 |
|---|---|
| `TemplateSequence` | 用于支持基于模板序列的相机动画播放 |

使用该插件时，你的项目模块通常只需要依赖 `EngineCameras` 即可，它内部已包含了 `TemplateSequence`。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式日志宏迁移至新的带格式化版本的 `UE_LOGF` 宏。 |
| 2025-06-26 | `ec900998` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applied | 为包含 .gen.cpp 的源文件添加内联生成宏，优化编译。 |
| 2025-05-07 | `ee22987e` | Don’t restart a camera animation blend out when reaching the blend out time if we were already stopp | 修复了在动画已停止状态下，到达混合退出时间时错误重启混合退出的 bug。 |
| 2025-04-23 | `6ae57335` | Used UnrealGame build target to find and convert all files to have dllstorage on methods/staticvar i | 为所有方法添加了 DLL 导出标记，支持作为模块链接。 |
| 2025-02-12 | `ef64d6c3` | Engine Cameras: API for EngineCamerasSubsystem | 完善了 `EngineCamerasSubsystem` 的蓝图 API 接口。 |

### 维护评价

EngineCameras 是一个相对年轻（约1.5年）但功能明确的插件。它作为 Unreal 引擎相机系统演进过程中的关键模块，承载了从旧版 `APlayerCameraManager` 代码中分离出来的核心功能。从提交历史看，虽然更新频率不是极高，但近期（2025-2026）仍有实质性的问题修复、API 完善和代码优化工作，表明它**正在被积极维护**。

该插件设计清晰，分为“传统震动”和“序列动画”两大模块，提供了从蓝图到 C++ 的完整接口。对于需要使用传统相机震动效果或基于序列的相机动画的项目，这是一个稳定可靠的选择。**推荐使用**。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/EngineCameras)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Cameras/EngineCameras/Source/EngineCameras/Private/Tests)