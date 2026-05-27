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

EngineCameras 是从引擎核心中拆分出来的插件，负责承载 **传统相机抖动（Camera Shake）** 和 **相机动画序列（Camera Animation Sequence）** 系统。

在 UE 5.5 中，Epic 引入了新的 GameplayCameras 系统（实验性），为了避免新旧系统耦合，将已有的相机抖动和动画代码迁移到此独立插件中。它的核心职责是：

1. **播放和管理相机动画序列**：通过 `UCameraAnimationSequence` 驱动相机的位移、旋转、FOV 变化，支持缓入缓出、循环、随机起始时间等高级参数。
2. **提供多种相机抖动模式**：正弦波振荡（Wave Oscillator）、柏林噪声（Perlin Noise）、组合抖动（Composite）以及传统兼容的 Legacy 振荡抖动。
3. **兼容旧版 API**：保留 `ULegacyCameraShake` 及其蓝图节点，确保从 UE4/早期 UE5 迁移的项目不会蓝图断裂。

简而言之：**你需要相机抖动或相机动画？这个插件提供了开箱即用的实现。**

## 使用场景

- 你需要在爆炸、射击、受击时让镜头震动 → 使用 `UWaveOscillatorCameraShakePattern` 或 `UPerlinNoiseCameraShakePattern`
- 你需要播放一段 Sequencer 制作的相机运镜（如过场动画镜头） → 使用 `UCameraAnimationSequence` + `UEngineCamerasSubsystem`
- 你有老项目使用 `UCameraShake` 蓝图节点 → 继续使用 `ULegacyCameraShake`，无需改动
- 你需要同时组合多种抖动效果（如位置抖动 + FOV 抖动） → 使用 `UCompositeCameraShakePattern`
- 你在编写自定义相机系统，需要按需启停动画 → 通过 `FCameraAnimationHandle` 精确控制每个动画实例

## 蓝图用法

### 核心节点

#### 相机动画序列（Camera Animation）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `PlayCameraAnimation` | 播放一个相机动画序列，返回句柄 | `UEngineCamerasSubsystem` |
| `IsCameraAnimationActive` | 查询指定动画是否正在播放 | `UEngineCamerasSubsystem` |
| `StopCameraAnimation` | 停止指定相机动画（可选立即停止或混合淡出） | `UEngineCamerasSubsystem` |
| `StopAllCameraAnimationsOf` | 停止某个序列的所有动画实例 | `UEngineCamerasSubsystem` |
| `StopAllCameraAnimations` | 停止所有相机动画 | `UEngineCamerasSubsystem` |

#### 传统相机抖动（Legacy Camera Shake）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `StartLegacyCameraShake` | 启动一个传统相机抖动，返回抖动对象 | `ULegacyCameraShake` |
| `StartLegacyCameraShakeFromSource` | 从声音/物理源启动相机抖动 | `ULegacyCameraShake` |
| `ReceivePlayShake` | 蓝图可实现事件：抖动开始时调用 | `ULegacyCameraShake` |
| `BlueprintUpdateCameraShake` | 蓝图可实现事件：每帧更新视角 | `ULegacyCameraShake` |
| `ReceiveIsFinished` | 蓝图原生事件：决定抖动是否结束 | `ULegacyCameraShake` |
| `ReceiveStopShake` | 蓝图可实现事件：抖动被停止时调用 | `ULegacyCameraShake` |

#### 工具/类型转换

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetCameraAnimationCameraModifier` | 按 PlayerIndex 获取动画修改器 | `UCameraAnimationCameraModifier` |
| `GetCameraAnimationCameraModifierFromPlayerController` | 从 PlayerController 获取动画修改器 | `UCameraAnimationCameraModifier` |
| `Conv_LegacyCameraShake` | 将基类 UCameraShakeBase 自动转换为 ULegacyCameraShake | `ULegacyCameraShakeFunctionLibrary` |
| `Conv_CameraAnimationCameraModifier` | 将 PlayerCameraManager 自动转换为动画修改器 | `UEngineCameraAnimationFunctionLibrary` |

### 使用示例

**播放相机动画序列**：

1. 创建一个 `UCameraAnimationSequence` 资产（在 Sequencer 中编辑相机的位移/旋转/FOV 曲线）
2. 蓝图中调用 `PlayCameraAnimation`，传入 PlayerController、序列资产和参数
3. 保存返回的 `FCameraAnimationHandle`
4. 需要停止时，用该句柄调用 `StopCameraAnimation`

**播放传统相机抖动**：

1. 创建一个继承自 `ULegacyCameraShake` 的蓝图类
2. 在类中设置振荡参数（RotOscillation、LocOscillation、FOVOscillation）或指定 AnimSequence
3. 蓝图中调用 `StartLegacyCameraShake`，传入 PlayerCameraManager 和抖动类

**创建柏林噪声抖动**：

1. 创建一个继承自 `UCameraShakeBase` 的蓝图类
2. 将其 Root Pattern 设置为 `UPerlinNoiseCameraShakePattern`
3. 分别配置 Location（X/Y/Z）、Rotation（Pitch/Yaw/Roll）和 FOV 的振幅与频率
4. 通过 `Start Camera Shake` 节点启动

## C++ 用法

### 头文件引入

```cpp
#include "EngineCamerasSubsystem.h"
#include "Animations/CameraAnimationCameraModifier.h"
#include "Shakes/LegacyCameraShake.h"
#include "Shakes/PerlinNoiseCameraShakePattern.h"
#include "Shakes/WaveOscillatorCameraShakePattern.h"
```

### 基本用法：播放和停止相机动画序列

```cpp
// 获取引擎相机子系统
UEngineCamerasSubsystem* CameraSubsystem = UEngineCamerasSubsystem::GetEngineCamerasSubsystem(GetWorld());

// 设置播放参数
FCameraAnimationParams Params;
Params.PlayRate = 1.0f;
Params.Scale = 1.0f;
Params.bLoop = false;
Params.EaseInType = ECameraAnimationEasingType::Sinusoidal;
Params.EaseInDuration = 0.3f;
Params.EaseOutType = ECameraAnimationEasingType::Sinusoidal;
Params.EaseOutDuration = 0.3f;

// 播放动画
FCameraAnimationHandle Handle = CameraSubsystem->PlayCameraAnimation(PlayerController, MyAnimationSequence, Params);

// 检查是否正在播放
if (CameraSubsystem->IsCameraAnimationActive(PlayerController, Handle))
{
    // 动画仍在播放
}

// 停止动画（带混合淡出）
CameraSubsystem->StopCameraAnimation(PlayerController, Handle, false);

// 立即停止所有动画
CameraSubsystem->StopAllCameraAnimations(PlayerController, true);
```

### 基本用法：启动传统相机抖动

```cpp
APlayerCameraManager* PCM = PlayerController->PlayerCameraManager;

// 直接启动 Legacy 抖动
ULegacyCameraShake* ShakeInstance = ULegacyCameraShake::StartLegacyCameraShake(
    PCM,
    UMyLegacyCameraShake::StaticClass(),
    1.0f,  // Scale
    ECameraShakePlaySpace::CameraLocal,
    FRotator::ZeroRotator
);
```

### 进阶用法：C++ 中自定义 Legacy Camera Shake

```cpp
// MyLegacyCameraShake.h
UCLASS()
class UMyLegacyCameraShake : public ULegacyCameraShake
{
    GENERATED_BODY()
public:
    UMyLegacyCameraShake();
};

// MyLegacyCameraShake.cpp
UMyLegacyCameraShake::UMyLegacyCameraShake()
{
    // 持续时间
    OscillationDuration = 2.0f;
    OscillationBlendInTime = 0.2f;
    OscillationBlendOutTime = 0.4f;

    // 旋转振荡（左右晃动 + 前后倾斜）
    RotOscillation.Pitch.Amplitude = 5.0f;
    RotOscillation.Pitch.Frequency = 20.0f;
    RotOscillation.Pitch.Waveform = EOscillatorWaveform::PerlinNoise;

    RotOscillation.Yaw.Amplitude = 3.0f;
    RotOscillation.Yaw.Frequency = 15.0f;
    RotOscillation.Yaw.Waveform = EOscillatorWaveform::PerlinNoise;

    // 位置振荡
    LocOscillation.Z.Amplitude = 2.0f;
    LocOscillation.Z.Frequency = 12.0f;
    LocOscillation.Z.Waveform = EOscillatorWaveform::PerlinNoise;

    // FOV 振荡
    FOVOscillation.Amplitude = 3.0f;
    FOVOscillation.Frequency = 8.0f;
    FOVOscillation.Waveform = EOscillatorWaveform::SineWave;
}
```

### 进阶用法：使用 Wave Oscillator 抖动模式

```cpp
// 创建抖动并设置 Wave Oscillator 模式
UCameraShakeBase* Shake = NewObject<UCameraShakeBase>();
UWaveOscillatorCameraShakePattern* Pattern = Shake->ChangeRootShakePattern<UWaveOscillatorCameraShakePattern>();

Pattern->Duration = 1.5f;
Pattern->BlendInTime = 0.1f;
Pattern->BlendOutTime = 0.3f;

// 位置
Pattern->X.Amplitude = 5.0f;
Pattern->X.Frequency = 25.0f;
Pattern->Y.Amplitude = 3.0f;
Pattern->Y.Frequency = 18.0f;
Pattern->Z.Amplitude = 4.0f;
Pattern->Z.Frequency = 20.0f;

// 旋转
Pattern->Pitch.Amplitude = 8.0f;
Pattern->Pitch.Frequency = 22.0f;
Pattern->Yaw.Amplitude = 5.0f;
Pattern->Yaw.Frequency = 16.0f;
Pattern->Roll.Amplitude = 3.0f;
Pattern->Roll.Frequency = 10.0f;
Pattern->RotationAmplitudeMultiplier = 1.5f;

// 启动
PlayerController->PlayerCameraManager->StartCameraShake(Shake);
```

## Demo 示例

### 自定义相机抖动（兼容 Legacy API）

```cpp
// ExplosionCameraShake.h
#pragma once

#include "Shakes/LegacyCameraShake.h"
#include "ExplosionCameraShake.generated.h"

UCLASS()
class UExplosionCameraShake : public ULegacyCameraShake
{
    GENERATED_BODY()

public:
    UExplosionCameraShake();
};

// ExplosionCameraShake.cpp
#include "ExplosionCameraShake.h"

UExplosionCameraShake::UExplosionCameraShake()
{
    OscillationDuration = 0.8f;
    OscillationBlendInTime = 0.05f;
    OscillationBlendOutTime = 0.3f;

    // 强烈的上下抖动
    LocOscillation.Z.Amplitude = 10.0f;
    LocOscillation.Z.Frequency = 25.0f;
    LocOscillation.Z.Waveform = EOscillatorWaveform::PerlinNoise;

    // 旋转晃动
    RotOscillation.Pitch.Amplitude = 6.0f;
    RotOscillation.Pitch.Frequency = 20.0f;
    RotOscillation.Pitch.Waveform = EOscillatorWaveform::PerlinNoise;

    RotOscillation.Yaw.Amplitude = 4.0f;
    RotOscillation.Yaw.Frequency = 15.0f;
    RotOscillation.Yaw.Waveform = EOscillatorWaveform::PerlinNoise;

    // FOV 冲击
    FOVOscillation.Amplitude = 5.0f;
    FOVOscillation.Frequency = 10.0f;
    FOVOscillation.Waveform = EOscillatorWaveform::SineWave;
}
```

使用方式：

```cpp
// 在需要触发的地方
ULegacyCameraShake::StartLegacyCameraShake(
    PlayerController->PlayerCameraManager,
    UExplosionCameraShake::StaticClass(),
    1.5f  // 强度倍率
);
```

## 模块依赖

该插件依赖 `TemplateSequence` 插件（在 .uplugin 中声明）。从源码推断，模块内部依赖如下：

| 模块 | 用途 |
|---|---|
| `TemplateSequence` | 提供 UCameraAnimationSequence 和相关播放器基础设施 |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移到 UE_LOGF 新宏格式 |
| 2025-06-26 | `ec900998` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applie | 添加内联生成宏以优化编译 |
| 2025-05-07 | `ee22987e` | Don't restart a camera animation blend out when reaching the blend out time if we were already stopp | 修复相机动画淡出重复触发的 Bug |
| 2025-04-23 | `6ae57335` | Used UnrealGame build target to find and convert all files to have dllstorage on methods/staticvar i | 修正 DLL 导出符号声明 |
| 2025-02-12 | `ef64d6c3` | Engine Cameras: API for EngineCamerasSubsystem | 新增 EngineCamerasSubsystem 子系统 API |

### 维护评价

EngineCameras 是一个 **2024 年 8 月**从引擎核心拆分出来的新插件（约 2 年历史），属于 UE 5.5 相机系统重构的一部分。

- **创建背景**：从 `GameplayCameras`（实验性）中分离出传统相机抖动和动画代码，确保旧版 API 不受影响
- **更新频率**：2025 年有多次实质性更新，包括功能 API 新增（Subsystem API）、Bug 修复（淡出逻辑）和构建系统优化
- **活跃度**：维护活跃，最近一次更新在 2026 年 4 月，且 Epic 持续投入维护
- **稳定性**：作为引擎默认启用的插件，承载大量现有项目的相机抖动功能，预计会持续维护
- **推荐使用**：✅ **强烈推荐**。这是使用相机抖动和相机动画的官方标准路径。旧版 `UCameraShake` 已废弃头文件指向此处，新项目应直接使用本插件的 API

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/EngineCameras)
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Cameras/EngineCameras/Source/EngineCameras/Private/Tests/)