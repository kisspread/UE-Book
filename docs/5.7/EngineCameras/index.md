# Engine Cameras

> Default engine camera shakes and animations

| 属性 | 值 |
|---|---|
| 分类 | Cameras |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `EngineCameras` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-08-24 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Cameras/EngineCameras) | |

## 用途

EngineCameras 是 UE5 的相机震动（Camera Shake）和相机动画（Camera Animation）核心实现插件。它从引擎核心代码中提取出来，独立封装了两大功能：

1. **Camera Shake Pattern 系统**：基于 Pattern 的模块化相机震动框架，支持 Perlin 噪声、正弦波振荡、组合模式等多种震动方式。
2. **Camera Animation 系统**：通过 `UCameraAnimationSequence` 驱动的相机动画播放，支持混合、缓入缓出等高级功能。

该插件还包含向后兼容的 `ULegacyCameraShake`（原名 `UMatineeCameraShake`），使旧版蓝图和 C++ 代码无需修改即可继续运行。

**为什么存在**：UE4/早期 UE5 的相机震动逻辑内嵌在 Engine 模块中，与引擎耦合过紧。UE5 将其抽取为独立插件，便于维护、测试和替代（如新的 GameplayCameras 插件可完全替换此实现）。

## 使用场景

- 你需要爆炸、冲击、脚步等基于物理事件的相机震动 → 使用 Perlin Noise 或 Wave Oscillator 震动模式
- 你需要通过 Sequencer 制作复杂的相机运镜动画（如过场镜头、瞄准镜晃动） → 使用 Camera Animation Sequence
- 你正在从 UE4 迁移项目，蓝图中大量使用 `MatineeCameraShake` → 使用 `ULegacyCameraShake` 保持兼容
- 你需要组合多种震动效果同时生效（如同时叠加爆炸震动和心跳效果） → 使用 `UCompositeCameraShakePattern`

## 蓝图用法

### Camera Shake 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `StartLegacyCameraShake` | 启动传统相机震动，返回 LegacyCameraShake 引用 | `ULegacyCameraShake` |
| `StartLegacyCameraShakeFromSource` | 从指定源组件启动震动（距离衰减） | `ULegacyCameraShake` |
| `Conv_LegacyCameraShake` | 将 `UCameraShakeBase` 自动转换为 `ULegacyCameraShake` | `ULegacyCameraShakeFunctionLibrary` |

### Camera Animation 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `PlayCameraAnimation` | 播放一个 CameraAnimationSequence，返回 Handle | `UEngineCamerasSubsystem` |
| `IsCameraAnimationActive` | 查询动画是否正在播放 | `UEngineCamerasSubsystem` |
| `StopCameraAnimation` | 停止指定动画实例 | `UEngineCamerasSubsystem` |
| `StopAllCameraAnimationsOf` | 停止某个 Sequence 的所有实例 | `UEngineCamerasSubsystem` |
| `StopAllCameraAnimations` | 停止所有相机动画 | `UEngineCamerasSubsystem` |
| `GetCameraAnimationCameraModifier` | 获取 PlayerCameraManager 上的动画 Modifier | `UCameraAnimationCameraModifier` |
| `GetCameraAnimationCameraModifierFromPlayerController` | 从 PlayerController 获取动画 Modifier | `UCameraAnimationCameraModifier` |
| `Conv_CameraAnimationCameraModifier` | PlayerCameraManager 自动转换为 Modifier | `UEngineCameraAnimationFunctionLibrary` |

### 使用示例

**播放相机震动**：
1. 创建一个继承自 `ULegacyCameraShake` 或 `UDefaultCameraShakeBase` 的蓝图类
2. 在震动蓝图中配置震动参数（振荡幅度、频率、持续时间等）
3. 在游戏中通过 `Start Camera Shake` 节点启动震动，传入 PlayerCameraManager 引用

**播放相机动画**：
1. 创建 `UCameraAnimationSequence` 资产（在 Sequencer 中编辑相机关键帧）
2. 通过 `Get Camera Animation Camera Modifier` 获取 Modifier 引用
3. 调用 `Play Camera Animation` 传入 Sequence 和 `FCameraAnimationParams`（PlayRate、Scale、循环等）
4. 保存返回的 Handle，用于后续查询状态或停止动画

## C++ 用法

### 头文件引入

```cpp
// Camera Shake 系统
#include "Shakes/PerlinNoiseCameraShakePattern.h"
#include "Shakes/WaveOscillatorCameraShakePattern.h"
#include "Shakes/CompositeCameraShakePattern.h"
#include "Shakes/DefaultCameraShakeBase.h"
#include "Shakes/LegacyCameraShake.h"

// Camera Animation 系统
#include "Animations/CameraAnimationCameraModifier.h"
#include "EngineCamerasSubsystem.h"
```

### 基本用法 — 启动 Perlin 噪声震动

来自测试用例 `CameraShakeTests.cpp`：

```cpp
// 创建一个带 WaveOscillator Pattern 的震动
UCameraShakeBase* TestShake = NewObject<UDefaultCameraShakeBase>();
UWaveOscillatorCameraShakePattern* OscPattern =
    TestShake->ChangeRootShakePattern<UWaveOscillatorCameraShakePattern>();

// 配置震动参数
OscPattern->BlendInTime = 1.f;
OscPattern->BlendOutTime = 2.f;
OscPattern->Duration = 5.f;
OscPattern->X.Amplitude = 8.f;    // X轴振幅
OscPattern->X.Frequency = 1.f;    // X轴频率（每秒振荡次数）
OscPattern->X.InitialOffsetType = EInitialWaveOscillatorOffsetType::Zero;

// 启动震动（相机本地空间）
FMinimalViewInfo ViewInfo;
TestShake->StartShake(nullptr, 1.f, ECameraShakePlaySpace::CameraLocal);

// 每帧更新并应用到 POV
TestShake->UpdateAndApplyCameraShake(DeltaTime, 1.f, ViewInfo);
```

*来源：`EngineCameras/Source/EngineCameras/Private/Tests/CameraShakeTests.cpp`*

### 基本用法 — 使用 CameraAnimationSubsystem

```cpp
// 通过 Subsystem 播放相机动画
UEngineCamerasSubsystem* Subsystem =
    UEngineCamerasSubsystem::GetEngineCamerasSubsystem(GetWorld());

FCameraAnimationParams Params;
Params.PlayRate = 1.f;
Params.Scale = 1.f;
Params.bLoop = true;
Params.PlaySpace = ECameraAnimationPlaySpace::CameraLocal;

FCameraAnimationHandle Handle =
    Subsystem->PlayCameraAnimation(PlayerController, MySequence, Params);

// 检查状态
bool bPlaying = Subsystem->IsCameraAnimationActive(PlayerController, Handle);

// 停止（允许混合出）
Subsystem->StopCameraAnimation(PlayerController, Handle, false);
```

### 进阶用法 — 组合震动模式

来自测试用例 `CameraShakeTests.cpp` 的 Composite 模式：

```cpp
// 创建组合震动
auto TestShake = UTestCameraShake::CreateWithPattern<UCompositeCameraShakePattern>();

// 添加子震动 1：短时高强度
UConstantCameraShakePattern* Child1 =
    TestShake.Pattern->AddChildPattern<UConstantCameraShakePattern>();
Child1->Duration = 1.f;
Child1->BlendInTime = Child1->BlendOutTime = 0.2f;
Child1->LocationOffset = FVector(1.f, 0, 0);

// 添加子震动 2：长时低强度
UConstantCameraShakePattern* Child2 =
    TestShake.Pattern->AddChildPattern<UConstantCameraShakePattern>();
Child2->Duration = 2.f;
Child2->BlendInTime = Child2->BlendOutTime = 0.3f;
Child2->LocationOffset = FVector(1.f, 0, 0);

// 启动后，两个子震动独立运行，各自有自己的混合曲线
TestShake.Shake->StartShake(nullptr, 1.f, ECameraShakePlaySpace::CameraLocal);
```

*来源：`EngineCameras/Source/EngineCameras/Private/Tests/CameraShakeTests.cpp`*

### 进阶用法 — Camera Animation 的缓入缓出

```cpp
FCameraAnimationParams Params;
Params.EaseInType = ECameraAnimationEasingType::Sinusoidal;
Params.EaseInDuration = 0.5f;
Params.EaseOutType = ECameraAnimationEasingType::Cubic;
Params.EaseOutDuration = 1.0f;
Params.Scale = 2.f;
Params.PlaySpace = ECameraAnimationPlaySpace::UserDefined;
Params.UserPlaySpaceRot = FRotator(0.f, 45.f, 0.f);

FCameraAnimationHandle Handle =
    Modifier->PlayCameraAnimation(MySequence, Params);
```

支持的缓动类型：`Linear`、`Sinusoidal`、`Quadratic`、`Cubic`、`Quartic`、`Quintic`、`Exponential`、`Circular`。

## Demo 示例

### 自定义 Perlin Noise 震动蓝图

**C++ 头文件**：

```cpp
// MyCameraShake.h
#pragma once

#include "Shakes/DefaultCameraShakeBase.h"
#include "MyCameraShake.generated.h"

UCLASS()
class UMyExplosionShake : public UDefaultCameraShakeBase
{
    GENERATED_BODY()

public:
    UMyExplosionShake(const FObjectInitializer& ObjInit);
};
```

**C++ 实现**：

```cpp
// MyCameraShake.cpp
#include "MyCameraShake.h"
#include "Shakes/PerlinNoiseCameraShakePattern.h"

UMyExplosionShake::UMyExplosionShake(const FObjectInitializer& ObjInit)
    : Super(ObjInit)
{
    UPerlinNoiseCameraShakePattern* Pattern =
        ChangeRootShakePattern<UPerlinNoiseCameraShakePattern>();

    Pattern->Duration = 0.5f;
    Pattern->BlendInTime = 0.05f;
    Pattern->BlendOutTime = 0.3f;

    // 位置震动
    Pattern->LocationAmplitudeMultiplier = 5.f;
    Pattern->LocationFrequencyMultiplier = 20.f;
    Pattern->X.Amplitude = 1.f;
    Pattern->X.Frequency = 25.f;
    Pattern->Y.Amplitude = 1.f;
    Pattern->Y.Frequency = 25.f;
    Pattern->Z.Amplitude = 0.5f;
    Pattern->Z.Frequency = 20.f;

    // 旋转震动
    Pattern->RotationAmplitudeMultiplier = 2.f;
    Pattern->RotationFrequencyMultiplier = 15.f;
    Pattern->Pitch.Amplitude = 1.f;
    Pattern->Pitch.Frequency = 20.f;
    Pattern->Yaw.Amplitude = 1.f;
    Pattern->Yaw.Frequency = 18.f;
    Pattern->Roll.Amplitude = 0.5f;
    Pattern->Roll.Frequency = 15.f;
}
```

**Build.cs 依赖**：

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "EngineCameras",
    "Core",
    "CoreUObject",
    "Engine"
});
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `CinematicCamera` | 电影摄像机组件支持 |
| `Core` | 基础类型、数学库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心（PlayerCameraManager 等） |
| `HeadMountedDisplay` | VR 头显支持 |
| `MovieScene` | Sequencer 底层框架 |
| `MovieSceneTracks` | Sequencer 轨道实现 |
| `TemplateSequence` | 模板序列支持（插件依赖） |
| `TraceLog` | 追踪日志 |

## 维护状态

### 近期更新

| 日期 | Hash | 提交信息 | 解读 |
|---|---|---|---|
| 2025-06-26 | `ec90099` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files | 代码规范化，性能优化（减少编译依赖） |
| 2025-05-07 | `ee22987` | Don't restart a camera animation blend out when reaching the blend out time if we were already stopping | **Bug 修复**：修复相机动画在已处于 blend-out 状态时到达 blend-out 时间点会错误重新启动 blend-out 的问题 |
| 2025-04-23 | `6ae5733` | Used UnrealGame build target to find and convert all files to have dllstorage on methods | 构建系统适配，将方法级 dllstorage 从类型级迁移 |

### 维护评价

- **创建时间**：2024-08-24，约 2 年前从引擎核心提取为独立插件
- **更新频率**：2025 年有多次实质性更新（包括 Bug 修复），维护活跃
- **维护状态**：**活跃维护** — 最近一次功能性 Bug 修复在 2025 年 5 月
- **兼容性**：包含 Legacy 兼容层（`MatineeCameraShake.h` → `LegacyCameraShake.h`），旧代码可无缝迁移
- **推荐**：✅ 推荐使用。这是 UE5 相机震动和动画的官方默认实现，`EnabledByDefault=true`，几乎所有项目都会自动加载。如果需要更高级的相机系统，可以考虑 `GameplayCameras` 插件作为替代。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Cameras/EngineCameras)
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Cameras/EngineCameras/Source/EngineCameras/Private/Tests/CameraShakeTests.cpp)
