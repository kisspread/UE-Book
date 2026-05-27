# Animation Warping

> Framework for animation and pose warping. This plugin includes Stride, Orientation, and Slope Warping alongside the Root Motion Delta animation attribute.

| 属性 | 值 |
|---|---|
| 中文名 | 动画扭曲 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `AnimationWarpingRuntime` (Runtime), `AnimationWarpingEditor` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2021-12-04 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/AnimationWarping) | |

## 用途

AnimationWarping 是一套**程序化骨骼动画扭曲框架**，用于根据角色的运动状态（速度、方向、地形坡度等）动态调整骨骼姿态，使动画能够适应不同的游戏环境而无需为每种情况制作独立动画。

核心解决的问题是：**如何让少量动画资产适应无限多的运动场景**。例如：

- **步幅扭曲（Stride Warping）**：角色以不同速度移动时，自动拉伸或压缩腿部步幅，避免滑步
- **朝向扭曲（Orientation Warping）**：角色向不同方向移动时，下半身转向运动方向，上半身保持朝向，实现自然的转向动画
- **坡度扭曲（Slope Warping）**：角色在斜坡上行走时，自动调整骨盆和脚部位置以贴合地面
- **脚步放置（Foot Placement）**：精确控制脚部 IK，实现脚底贴合地形、锁定脚部防止滑动等高级效果
- **根骨骼偏移（Offset Root Bone）**：在动画根运动基础上叠加额外的位移/旋转偏移，用于移动平台、程序化位移等场景
- **转向控制（Steering）**：通过缩放动画根运动旋转来精确匹配目标朝向

插件默认**未启用**，需要在项目设置中手动启用。

## 使用场景

- 你在做第三人称动作游戏，角色需要在不同速度下自然跑步 → 用 **Stride Warping**
- 你需要角色在瞄准时上半身朝向目标，下半身跟随移动方向 → 用 **Orientation Warping**
- 角色在复杂地形（斜坡、台阶）上行走，脚部需要贴合地面 → 用 **Foot Placement** 或 **Slope Warping**
- 你需要角色站在移动平台上，同时保持脚步稳定 → 用 **Offset Root Bone**
- 你需要角色转弯时动画根运动精确对齐目标方向 → 用 **Steering**

## 蓝图用法

### 核心节点（AnimationWarpingLibrary）

插件通过 `UAnimationWarpingLibrary` 暴露蓝图可用的静态函数：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetOffsetRootTransform` | 获取 Offset Root Bone 节点当前的世界空间变换 | `UAnimationWarpingLibrary` |
| `GetCurveValueFromAnimation` | 从动画序列中按时间采样曲线值 | `UAnimationWarpingLibrary` |
| `GetFloatValueFromCurve` | 从 Float 曲线资产中按时间采样值 | `UAnimationWarpingLibrary` |
| `GetVectorValueFromCurve` | 从 Vector 曲线资产中按时间采样值 | `UAnimationWarpingLibrary` |
| `ConvertToOffsetRootBoneNodePure` | 将 AnimNode 引用转换为 Offset Root Bone 节点引用 | `UAnimationWarpingLibrary` |
| `ApplyDeltaToOffsetRootBone` | 对 Offset Root Bone 的内部模拟变换施加增量位移/旋转 | `UAnimationWarpingLibrary` |

### 使用示例（蓝图描述）

**场景：让角色站在移动平台上，脚步跟随平台移动**

1. 在动画蓝图中添加 `Offset Root Bone` 节点，放在姿态求值链的合适位置
2. 在事件图表中，使用 `Convert to Offset Root Bone node` 获取节点引用
3. 当角色进入移动平台时，每帧调用 `ApplyDeltaToOffsetRootBone`，传入平台的帧位移增量（世界空间），节点会自动累积偏移

**场景：根据速度自动调整跑步步幅**

1. 在动画蓝图中添加 `Stride Warping` 节点
2. 将 `Mode` 设为 `Graph`（自动从根运动属性计算）或 `Manual`（手动输入 `StrideScale`）
3. 如果使用 Manual 模式，将角色移动速度连接到 `LocomotionSpeed`，将根运动速度连接到相关计算节点
4. 配置 `FootDefinitions`，指定每条腿的 IK 脚骨、FK 脚骨和大腿骨

## C++ 用法

### 头文件引入

```cpp
#include "BoneControllers/AnimNode_StrideWarping.h"
#include "BoneControllers/AnimNode_OrientationWarping.h"
#include "BoneControllers/AnimNode_FootPlacement.h"
#include "BoneControllers/AnimNode_OffsetRootBone.h"
#include "BoneControllers/AnimNode_SlopeWarping.h"
#include "BoneControllers/AnimNode_Steering.h"
#include "AnimationWarpingLibrary.h"
```

### 基本用法 — Orientation Warping

```cpp
// 在自定义 AnimInstance 或 AnimNode 中使用 Orientation Warping
// 来源: Public/BoneControllers/AnimNode_OrientationWarping.h

FAnimNode_OrientationWarping OrientationWarpingNode;

// 配置模式为 Manual，手动传入角度
OrientationWarpingNode.Mode = EWarpingEvaluationMode::Manual;

// 设置朝向角度（上半身应保持的朝向与运动方向的差值，单位：度）
OrientationWarpingNode.OrientationAngle = 45.0f;

// 设置运动方向角度（运动速度与角色朝向的差值）
OrientationWarpingNode.LocomotionAngle = CalculateDirection(Velocity, ActorRotation);

// 配置脊椎骨骼（从下到上，用于分配旋转）
OrientationWarpingNode.SpineBones.Add(FBoneReference(TEXT("spine_01")));
OrientationWarpingNode.SpineBones.Add(FBoneReference(TEXT("spine_02")));
OrientationWarpingNode.SpineBones.Add(FBoneReference(TEXT("spine_03")));

// 配置 IK 脚部骨骼
OrientationWarpingNode.IKFootRootBone = FBoneReference(TEXT("ik_foot_root"));
OrientationWarpingNode.IKFootBones.Add(FBoneReference(TEXT("ik_foot_l")));
OrientationWarpingNode.IKFootBones.Add(FBoneReference(TEXT("ik_foot_r")));

// 设置旋转插值速度（0 = 瞬间切换，> 0 = 平滑过渡）
OrientationWarpingNode.RotationInterpSpeed = 10.0f;

// 上下半身旋转分配比例（0 = 全部给下半身，1 = 全部给上半身）
OrientationWarpingNode.DistributedBoneOrientationAlpha = 0.5f;
```

### 基本用法 — Stride Warping

```cpp
// 来源: Public/BoneControllers/AnimNode_StrideWarping.h

FAnimNode_StrideWarping StrideWarpingNode;

// 设置扭曲方向（通常设为角色前方向量）
StrideWarpingNode.StrideDirection = FVector::ForwardVector;

// 手动设置步幅缩放（1.0 = 原始，0.5 = 半步，2.0 = 双倍步幅）
StrideWarpingNode.StrideScale = 1.0f;

// 或者通过运动速度自动计算（Graph 模式下由根运动自动处理）
StrideWarpingNode.LocomotionSpeed = CurrentSpeed;

// 配置腿部定义
FStrideWarpingFootDefinition FootDef;
FootDef.IKFootBone = FBoneReference(TEXT("ik_foot_l"));
FootDef.FKFootBone = FBoneReference(TEXT("foot_l"));
FootDef.ThighBone = FBoneReference(TEXT("thigh_l"));
StrideWarpingNode.FootDefinitions.Add(FootDef);

// 骨盆骨骼
StrideWarpingNode.PelvisBone = FBoneReference(TEXT("pelvis"));

// 步幅缩放修正器（可选的钳制/插值）
StrideWarpingNode.StrideScaleModifier.ClampMinEnabled = true;
StrideWarpingNode.StrideScaleModifier.ClampMin = 0.5f;
StrideWarpingNode.StrideScaleModifier.ClampMaxEnabled = true;
StrideWarpingNode.StrideScaleModifier.ClampMax = 2.0f;
```

### 进阶用法 — Offset Root Bone + 移动平台

```cpp
// 来源: Public/BoneControllers/AnimNode_OffsetRootBone.h, Public/AnimationWarpingLibrary.h

// 在 C++ 中获取 Offset Root Bone 节点并施加增量
// 适用于角色站在移动平台上的场景

// 通过 AnimationWarpingLibrary 的静态函数
// 假设你在 AnimInstance 的 BlueprintThreadSafe 函数中操作

FOffsetRootBoneAnimNodeReference OffsetNodeRef;
bool bResult = false;

// 从动画蓝图节点上下文转换
UAnimationWarpingLibrary::ConvertToOffsetRootBoneNodePure(
    AnimNodeContext, OffsetNodeRef, bResult);

if (bResult)
{
    // 计算移动平台的帧增量（世界空间）
    FVector DeltaTranslation = PlatformVelocity * DeltaTime;
    FQuat DeltaRotation = FQuat::Identity; // 可选旋转增量

    // 施加到偏移根骨骼
    UAnimationWarpingLibrary::ApplyDeltaToOffsetRootBone(
        OffsetNodeRef, DeltaTranslation, DeltaRotation);
}
```

## Demo 示例

以下是一个最小的自定义 AnimNode，演示如何在动画蓝图中使用 Orientation Warping 和 Stride Warping：

```cpp
// MyWarpingAnimInstance.h
#pragma once

#include "Animation/AnimInstance.h"
#include "BoneControllers/AnimNode_OrientationWarping.h"
#include "BoneControllers/AnimNode_StrideWarping.h"
#include "MyWarpingAnimInstance.generated.h"

UCLASS()
class UMyWarpingAnimInstance : public UAnimInstance
{
    GENERATED_BODY()

public:
    /** 更新朝向扭曲参数 */
    UFUNCTION(BlueprintCallable, Category = "Animation Warping")
    void UpdateOrientationWarping(float InLocomotionAngle, float InOrientationAngle);

    /** 更新步幅扭曲参数 */
    UFUNCTION(BlueprintCallable, Category = "Animation Warping")
    void UpdateStrideWarping(float InLocomotionSpeed);
};
```

```cpp
// MyWarpingAnimInstance.cpp
#include "MyWarpingAnimInstance.h"

void UMyWarpingAnimInstance::UpdateOrientationWarping(
    float InLocomotionAngle, float InOrientationAngle)
{
    // 这些值通常通过 Property Access 或直接在蓝图中设置节点属性
    // 此处演示数值计算逻辑
    //
    // LocomotionAngle = CalculateDirection(Velocity, ActorRotation)
    // OrientationAngle = 通常由其他系统设置（如瞄准方向）
    //
    // 在动画蓝图中直接连线即可，此处仅做概念演示
}

void UMyWarpingAnimInstance::UpdateStrideWarping(float InLocomotionSpeed)
{
    // LocomotionSpeed 应与动画图的 DeltaTime 对齐
    // 通常从 CharacterMovementComponent 获取速度
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AnimationModifierLibrary` | 插件级依赖（用于动画修改器基础功能） |

无其他特殊依赖（仅标准 Animation/Core/Engine 模块）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `42c8bcfa` | Fix tooltip on ABP steering node | 修复转向节点的工具提示显示错误 |
| 2026-04-24 | `afab60f0` | UE-363190 - Replace crash-assert NaN guards with UE_LOGF + safe-default in StrideWarping and Orienta | 将步幅/朝向扭曲中的 NaN 崩溃断言改为日志警告+安全默认值 |
| 2026-04-24 | `42548e51` | Fix non-unity build: forward-declare UAnimationAsset in anim node headers | 修复非 unity 构建，前向声明 UAnimationAsset |
| 2026-04-23 | `23ccd2bd` | Add Anim Node Functions to support applying a delta to the offset root bone's internal simulated tra | 新增动画节点函数，支持对偏移根骨骼的内部模拟变换施加增量 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到 UE_LOGF |

### 维护评价

**活跃维护**。该插件在最近几个月持续有功能性更新和稳定性修复：

- 2026 年 4-5 月期间有多次实质性的代码改动，包括新功能（OffsetRootBone 增量 API）和稳定性改进（NaN 安全处理）
- 插件从 2021 年 12 月创建（从 Experimental 迁移到正式版本），经过约 4 年发展已较为成熟
- 部分节点仍标记为 `Experimental`（如 FAnimNode_FootPlacement、FAnimNode_SlopeWarping、FAnimNode_OverrideRootMotion），使用时需注意 API 可能变化
- 插件默认未启用（`EnabledByDefault: false`），但代码质量较高，由 Epic Games 官方维护
- **推荐使用**，尤其是 Stride Warping 和 Orientation Warping 已足够稳定用于生产项目

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/AnimationWarping)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/AnimationWarping/Tests)