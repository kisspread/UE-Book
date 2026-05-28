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
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/EngineCameras) | |

## 用途

此插件是 UE5.5 版本重构中，从引擎核心分离出的“旧版”相机系统模块。它将原先 `APlayerCameraManager` 中与相机摇动（Camera Shake）和相机动画序列（Camera Animation Sequence）相关的代码独立出来，作为一个标准的插件进行管理。

其主要作用是：
1.  **统一管理**：提供一个世界子系统 `UEngineCamerasSubsystem`，作为播放和管理相机动画序列的统一入口。
2.  **提供实现**：包含了多种内置的相机摇动模式（Perlin 噪声、波振荡器等）和播放相机动画序列的核心逻辑。
3.  **保持兼容**：保留了旧版的 `ULegacyCameraShake`，并为旧有的 `APlayerCameraManager` 接口提供了兼容层，确保存量蓝图和代码能平稳过渡。

## 使用场景

-   你需要为游戏中的角色受伤、爆炸、车辆碰撞等事件添加**屏幕震动效果**。
-   你希望使用**序列资产（Camera Animation Sequence）** 来制作精确、可编排的复杂镜头动画（如过场动画、技能特写）。
-   你正在维护一个 UE5.5 之前版本的项目，其中使用了旧的 `UCameraShake` 或 `StartCameraShake` 函数。
-   你需要一个全局、易访问的接口来控制某个玩家控制器的相机动画。

## 蓝图用法

蓝图功能主要通过 `UEngineCamerasSubsystem` 和 `UCameraAnimationCameraModifier` 提供。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Engine Cameras Subsystem` | 获取当前世界的 `UEngineCamerasSubsystem` 实例，用于管理相机动画。 | `UEngineCamerasSubsystem` |
| `Play Camera Animation` | 在指定的玩家控制器上播放一个相机动画序列。 | `UEngineCamerasSubsystem` |
| `Stop Camera Animation` | 停止一个正在播放的相机动画。 | `UEngineCamerasSubsystem` |
| `Stop All Camera Animations` | 停止指定玩家控制器上的所有相机动画。 | `UEngineCamerasSubsystem` |
| `Get Camera Animation Camera Modifier` | 通过玩家控制器索引获取底层的 `UCameraAnimationCameraModifier`，用于更底层的控制。 | `UCameraAnimationCameraModifier` |
| `Start Legacy Camera Shake` | **兼容性节点**，播放一个 `ULegacyCameraShake` 类，返回具体的摇动实例以便设置其属性。 | `ULegacyCameraShake` |
| `Conv_LegacyCameraShake` | 自动转换节点，将基类 `UCameraShakeBase*` 转换为 `ULegacyCameraShake*`。 | `ULegacyCameraShakeFunctionLibrary` |

### 使用示例（蓝图描述）

**示例1：通过子系统播放一个相机动画序列**

1.  在蓝图中，使用 `Get Engine Cameras Subsystem` 节点获取子系统引用。
2.  拖拽引出一个玩家控制器变量（如 `Get Player Controller`）。
3.  引用或创建一个 `Camera Animation Sequence` 资产。
4.  将以上节点连接到 `Play Camera Animation` 节点。你可以设置 `FCameraAnimationParams` 结构体中的参数（如播放速率、缩放、是否循环等）。
5.  该节点会返回一个 `FCameraAnimationHandle`，你可以保存它以便后续停止该动画。

**示例2：播放一个传统的屏幕震动**

1.  获取目标玩家的 `Player Camera Manager`。
2.  使用 `Start Legacy Camera Shake` 节点，选择一个继承自 `ULegacyCameraShake` 的蓝图类。
3.  节点返回的 `ULegacyCameraShake*` 引用可以直接用于在蓝图中设置其 `RotOscillation`、`LocOscillation` 等属性来控制震动。

## C++ 用法

### 头文件引入

```cpp
#include "EngineCamerasSubsystem.h" // 用于管理相机动画序列
#include "Animations/CameraAnimationCameraModifier.h" // 用于底层访问
#include "Shakes/LegacyCameraShake.h" // 用于旧版相机摇动
```

### 基本用法

以下示例展示了如何使用 `UEngineCamerasSubsystem` 播放一个相机动画序列。

```cpp
// 假设你拥有一个有效的 PlayerController 和一个 UCameraAnimationSequence 资产指针
void AMyActor::PlayMyCameraAnimation()
{
    if (UWorld* World = GetWorld())
    {
        // 获取世界子系统
        UEngineCamerasSubsystem* Subsystem = UEngineCamerasSubsystem::GetEngineCamerasSubsystem(World);
        if (Subsystem && MyPlayerController && MyCameraAnimationSequence)
        {
            // 设置播放参数
            FCameraAnimationParams Params;
            Params.Scale = 1.5f;
            Params.PlayRate = 1.0f;
            Params.bLoop = false;
            
            // 播放动画并获取句柄
            FCameraAnimationHandle Handle = Subsystem->PlayCameraAnimation(MyPlayerController, MyCameraAnimationSequence, Params);
            
            // 保存句柄，以便后续停止
            CurrentAnimationHandle = Handle;
        }
    }
}

void AMyActor::StopMyCameraAnimation()
{
    if (UWorld* World = GetWorld())
    {
        UEngineCamerasSubsystem* Subsystem = UEngineCamerasSubsystem::GetEngineCamerasSubsystem(World);
        if (Subsystem && MyPlayerController && CurrentAnimationHandle.IsValid())
        {
            // 立即停止动画（忽略淡出）
            Subsystem->StopCameraAnimation(MyPlayerController, CurrentAnimationHandle, true);
        }
    }
}
```

### 进阶用法

你可以直接访问 `UCameraAnimationCameraModifier` 以获得更底层的控制，或者创建和配置自定义的 `ULegacyCameraShake`。

```cpp
#include "Shakes/PerlinNoiseCameraShakePattern.h" // 引入具体的摇动模式

void AMyActor::StartCustomPerlinShake()
{
    if (APlayerController* PC = GetWorld()->GetFirstPlayerController())
    {
        // 获取相机动画修改器（它本质上是 Player Camera Manager 上的一个 Modifier）
        UCameraAnimationCameraModifier* CamMod = UCameraAnimationCameraModifier::GetCameraAnimationCameraModifierFromPlayerController(PC);
        if (CamMod)
        {
            // 你可以使用它来播放动画，或者访问其内部状态
            // ...
        }
        
        // 或者，直接启动一个使用特定模式的旧版摇动
        ULegacyCameraShake* ShakeInstance = ULegacyCameraShake::StartLegacyCameraShake(
            PC->PlayerCameraManager,
            ULegacyCameraShake::StaticClass(), // 使用基类，通常你会传入自定义子类
            1.0f,
            ECameraShakePlaySpace::CameraLocal
        );
        
        if (ShakeInstance)
        {
            // 直接配置摇动参数
            ShakeInstance->RotOscillation.Pitch.Amplitude = 5.0f;
            ShakeInstance->RotOscillation.Pitch.Frequency = 10.0f;
            ShakeInstance->RotOscillation.Yaw.Amplitude = 2.0f;
            ShakeInstance->OscillationDuration = 2.0f; // 持续2秒
        }
    }
}
```

## Demo 示例

以下是一个自定义 Actor 的简单示例，该 Actor 在开始游戏后播放一个相机动画。

**MyCameraActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyCameraActor.generated.h"

class UCameraAnimationSequence;
struct FCameraAnimationHandle;

UCLASS()
class MYPROJECT_API AMyCameraActor : public AActor
{
	GENERATED_BODY()
	
public:	
	AMyCameraActor();

protected:
	virtual void BeginPlay() override;

public:	
	// 拖入一个相机动画序列资产
	UPROPERTY(EditAnywhere, Category = "Camera")
	TObjectPtr<UCameraAnimationSequence> CameraSequence;

private:
	FCameraAnimationHandle ActiveAnimationHandle;
};
```

**MyCameraActor.cpp**
```cpp
#include "MyCameraActor.h"
#include "EngineCamerasSubsystem.h"

AMyCameraActor::AMyCameraActor()
{
	PrimaryActorTick.bCanEverTick = false;
}

void AMyCameraActor::BeginPlay()
{
	Super::BeginPlay();

	UWorld* World = GetWorld();
	if (!World || !CameraSequence) return;

	// 获取本地玩家控制器
	APlayerController* PC = World->GetFirstPlayerController();
	if (!PC) return;

	// 获取相机子系统
	UEngineCamerasSubsystem* Subsystem = UEngineCamerasSubsystem::GetEngineCamerasSubsystem(World);
	if (!Subsystem) return;

	// 配置播放参数
	FCameraAnimationParams Params;
	Params.Scale = 1.0f;
	Params.PlayRate = 1.0f;
	Params.bLoop = true;
	Params.PlaySpace = ECameraAnimationPlaySpace::CameraLocal;

	// 播放动画
	ActiveAnimationHandle = Subsystem->PlayCameraAnimation(PC, CameraSequence, Params);
}
```

## 模块依赖

从插件的依赖和模块类型分析，此插件提供了相机动画的核心功能。你的模块若要使用它，通常不需要额外的、不常见的模块依赖。

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移至新的 UE_LOGF 格式。 |
| 2025-06-26 | `ec900998` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. | 为有对应 .gen.cpp 的文件添加了内联生成宏，可能优化编译。 |
| 2025-05-07 | `ee22987e` | Don’t restart a camera animation blend out when reaching the blend out time if we were already stopp | 修复了动画在停止时，如果达到淡出时间会错误地重新开始淡出的 Bug。 |
| 2025-04-23 | `6ae57335` | Used UnrealGame build target to find and convert all files to have dllstorage on methods/staticvar i | 为导出符号添加了 DLL 存储属性，属于内部构建系统维护。 |
| 2025-02-12 | `ef64d6c3` | Engine Cameras: API for EngineCamerasSubsystem | 为 `EngineCamerasSubsystem` 添加了 API，这是该子系统的核心功能提交。 |

### 维护评价

该插件创建于 2024 年 8 月，用于 UE5.5 版本的相机系统重构。从 Git 历史看，它至今（2026年）仍有**活跃维护**，最近一次提交是 2026 年 4 月。更新内容包括功能增强（API 完善）、Bug 修复（动画淡出逻辑）以及引擎内部的代码质量改进（日志、编译优化）。

**结论**：这是一个处于活跃维护状态的官方插件。它是 UE5.5+ 中处理“旧版”相机动画和摇动的**标准方式**。对于新项目或升级到 UE5.5 的项目，如果你想使用基于序列的相机动画或保留传统的屏幕震动功能，**强烈推荐使用此插件**。它取代了之前散落在引擎各处的相关代码，提供了更清晰、更模块化的架构。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/EngineCameras)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/camera-shakes-in-unreal-engine/)（注：这是关于相机摇动的官方文档，此插件是其中的实现之一）
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Cameras/EngineCameras/Private/Tests/)