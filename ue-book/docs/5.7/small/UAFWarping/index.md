# UAF Warping

> Framework for animation and pose warping for UAF.

| 属性 | 值 |
|---|---|
| 中文名 | UAF 扭曲框架 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `UAFWarping` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-27 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFWarping) | |

## 用途

UAF Warping 插件为 **UAF（Unreal Animation Framework）** 提供了动画和姿态扭曲的核心 Trait 集合，主要用于使角色在移动时能够动态调整身体朝向和脚步位置，实现平滑的转向与扫射扭曲效果。它解决了传统动画播放过程中角色方向与输入方向不匹配、转向生硬的问题，特别适用于第三人称射击、动作冒险等需要灵活转向的游戏。

该插件通过两种技术叠加实现扭曲：  
1. **缩放根运动**（Scale Root Motion）——根据目标方向调整动画本身的旋转根运动强度。  
2. **附加校正**（Additive Correction）——在缩放后仍存在误差时，通过弹簧系统添加额外的旋转补偿。

## 使用场景

- 制作一个第三人称射击游戏，角色需要根据瞄准方向动态调整身体朝向，实现自然的扫射步态。
- 需要角色在移动中快速转向且不打断动画流畅性的系统（如平台跳跃、赛车漂移）。
- 自定义动作系统（如 Mover 2.0）中需要与动画扭曲集成的场景。

## 蓝图用法

UAF Warping 的 Traits 主要通过 C++ 在工作流图中直接使用或通过继承扩展，蓝图不直接暴露具体的执行节点。但 Traits 的共享数据（SharedData）部分属性可在蓝图中编辑（标记了 `meta = (PinShownByDefault)` 的属性）。以下为可配置的核心参数（通过 Trait 编辑工具访问）：

| 参数（所属 Trait） | 类型 | 说明 |
|---|---|---|
| **Steering（转向）** | | |
| `Alpha` | float | 控制强度，0-1 |
| `TargetOrientation` | FQuat | 目标朝向 |
| `ProceduralTargetTime` | float | 无根运动旋转时的未来时间（秒） |
| `AnimatedTargetTime` | float | 有根运动旋转时的未来时间（秒） |
| `RootMotionThreshold` | float | 启用根运动缩放的旋转阈值（度） |
| `MinScaleRatio` / `MaxScaleRatio` | float | 缩放比例范围 |
| **Strafe Warping（扫射扭曲）** | | |
| `TargetOrientation` | FQuat | 身体朝向目标 |
| `RotationAxis` | EAxis | 旋转轴（默认 Z） |
| `DistributedBoneOrientationAlpha` | float | 身体旋转 vs IK 脚之间的分配比例 |
| `RotationInterpSpeed` | float | 插值速率（0 瞬间，>0 平滑） |
| `CounterCompensateInterpSpeed` | float | 反补偿插值速率（保留动画根运动特征） |
| `MaxCorrectionDegrees` | float | 每秒最大纠正角度 |
| **WarpTest（测试）** | | |
| `Transforms` | TArray\<FTransform\> | 循环切换的目标变换数组 |
| `SecondsToWait` | float | 切换间隔（秒） |

在 UAF 动画工作流中，可以通过添加 `FSteeringTrait`、`FStrafeWarpingTrait` 等 Traits 到 AnimNext 层次结构，然后在蓝图中调整上述参数。

## C++ 用法

### 头文件引入

```cpp
#include "SteeringTrait.h"
#include "StrafeWarpingTrait.h"
#include "WarpTestTrait.h"   // 仅测试用途
```

### 基本用法

以下代码展示了如何在自定义动画节点或流程图中实例化并使用 Steering Trait。**注意**：实际 Traits 必须通过 UAF 的 Trait 系统注册和调度，此处仅为演示数据结构的直接使用。

```cpp
// 来源：Engine/Plugins/Experimental/UAF/UAFWarping/Private/SteeringTrait.h

// 创建 Steering Trait 共享数据
FSteeringTraitSharedData SteeringData;
SteeringData.Alpha = 1.0f;
SteeringData.TargetOrientation = FQuat(FRotator(0.0f, 90.0f, 0.0f)); // 目标朝向 Yaw +90°
SteeringData.RootBoneTransform = CurrentRootBoneTransform; // 来自动画缓存
SteeringData.ProceduralTargetTime = 0.2f;
SteeringData.AnimatedTargetTime = 0.2f;
SteeringData.RootMotionThreshold = 1.0f;
SteeringData.MinScaleRatio = 0.5f;
SteeringData.MaxScaleRatio = 1.5f;
```

对于 Strafe Warping，类似地创建并填充参数。WarpTest 通常仅用于内部单元测试。

### 进阶用法：与 UAF 流程集成

Steering 和 Strafe Warping 子类化 `FAdditiveTrait` 并实现了 `IUpdate` 和 `IEvaluate` 接口。正确用法是向 UAF AnimNext 图表注册这些 Trait：

```cpp
// 伪代码，演示注册过程
UAF::FAnimNextGraph* Graph = ...;
Graph->AddTrait<FSteeringTrait>(SteeringData);
Graph->AddTrait<FStrafeWarpingTrait>(StrafeWarpingData);
```

然后框架会在 PreUpdate 阶段读取目标朝向和根骨变换，在 PostEvaluate 阶段应用最终的偏移。开发者无需直接调用这些方法。

## Demo 示例

以下是一个最小 C++ 模块，展示如何创建并应用 Steering Trait 到模拟动画控制器中（仅用于演示概念，实际集成需要更复杂的 UAF 上下文）：

**WarpingController.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Animation/AnimInstance.h"
#include "SteeringTrait.h"
#include "StrafeWarpingTrait.h"
#include "WarpingController.generated.h"

UCLASS()
class UWarpingController : public UAnimInstance
{
    GENERATED_BODY()

public:
    void UpdateSteering(FQuat TargetOrientation, float DeltaTime)
    {
        // 1. 获取当前根骨变换（示例中直接从姿态缓存）
        FTransform CurrentRoot = GetOwningComponent()->GetComponentTransform();
        // 2. 填充 Steering 数据
        SteeringData.Alpha = 1.0f;
        SteeringData.TargetOrientation = TargetOrientation;
        SteeringData.RootBoneTransform = CurrentRoot;
        // 其他参数使用默认值
        // 3. 框架将在内部处理 IUpdate / IEvaluate
        //    （实际会通过 UAF 的 Trait 更新管道调用）
    }

private:
    FSteeringTraitSharedData SteeringData;
};
```

**注意**：上述代码未包含完整的 UAF 集成，仅用于展示数据结构填充。实际项目中应通过 UAF 提供的 Trait 编辑工具（如 AnimNext 编辑器）来配置，而不是直接编写更新逻辑。

## 模块依赖

你的项目模块需要在 `Build.cs` 中添加以下依赖以使用 UAF Warping：

| 模块 | 用途 |
|---|---|
| `UAF` | 基础动画框架，提供 Trait 系统 |
| `UAFAnimGraph` | 用于在 UAF 动画图表中编辑 Traits |
| `RigVM` | 负责执行动画计算（如后处理重定向） |

另外，`CoreUObject`, `Engine`, `Core` 等常见模块为隐式依赖，无需额外添加。

## 维护状态

### 近期更新

- 2025-09-23 `500535bc` — Tweaks to SpringMath API（微调弹簧数学API）
- 2025-09-12 `70c9e98a` — SpringMath API Updates for 5.7 release（为5.7版本更新弹簧数学API）
- 2025-08-08 `97776670` — Add SmoothWalkingMode to Mover2.0（为Mover2.0添加平滑行走模式）
- 2025-06-27 `ee0441e9` — UAF: Rename/move plugins（UAF：重命名/移动插件）

### 维护评价

- **创建时间**：2025年6月（约1个月）。
- **最近更新**：2025年9月，包含功能性调整（SpringMath API）。更新频率高，属于活跃开发状态。
- **实验性**：标记为 `IsExperimentalVersion=true`，API 和功能可能不成熟。
- **推荐使用**：适合愿意跟踪最新 UAF 迭代的开发者。由于插件仍处于实验阶段，不建议用于正式生产项目，除非接受潜在的不稳定和 API 变动。

## 相关链接

- [源码（插件根目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFWarping)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/AnimNext/)（UAF 整体文档，Warping 部分可能后续更新）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFWarping/Private)（头文件和实现中包含单元测试结构）