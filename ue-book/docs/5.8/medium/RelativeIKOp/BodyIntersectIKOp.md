# Spatially Aware Retarget Ops

> A collection of Retarget Ops for preserving spatial relationships on retargeted animations

| 属性 | 值 |
|---|---|
| 中文名 | 空间感知重定向 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `BodyIntersectIKOp` (Runtime), `PreviewPropOp` (Runtime), `RelativeBodyAnimInfo` (Runtime), `RelativeBodyAnimUtils` (Runtime), `RelativeIKOp` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-07-23 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/RelativeIKOp) | |

## 用途

此插件提供了一套**IK 重定向操作器（Retarget Ops）**，专门用于解决动画重定向（Retargeting）过程中常见的**空间穿透和关系丢失**问题。标准的 IK 重定向主要关注骨骼链的朝向和长度，但当原角色和目标角色的体型、比例差异很大时，简单的重定向会导致手部、武器或道具穿透身体、武器与手部错位等视觉问题。

本插件的核心思想是利用目标角色的**物理资产（Physics Asset）** 作为参考，在重定向动画后执行一次空间修正。它会检测 IK 目标点（如手部、脚部）与目标物理资产身体（如胸腔、骨盆）的交叉情况，并应用一个推力（Push-out）来修正位置，从而确保重定向后的动画在目标骨架上依然保持合理的空间关系，避免穿模。

**主要解决的问题：**
1.  **手部/脚部穿透身体**：当重定向的动画比目标角色的体型更紧凑时，手或脚可能会陷入胸腔或骨盆。
2.  **道具穿透身体**：角色手持的武器、工具或其他道具在动画重定向后可能嵌入角色模型。
3.  **保持相对位置**：提供对道具（Prop）和极向量（Pole Vector）的空间修正能力，以维持动画的整体空间逻辑。

## 使用场景

- **角色换装/体型差异大的动画重定向**：将瘦小角色的动画重定向到魁梧角色时，避免手部陷入身体。
- **武器/道具动画制作**：为不同尺寸的角色制作持枪、持剑动画时，确保武器不会穿透角色模型。
- **复杂的 IK 动画后期修正**：在已有的 IK 重定向流程后，作为一道空间安全网，自动修复潜在的穿插问题。

## 蓝图用法

本插件主要通过 **IK Retargeter** 资产中的 **重定向操作栈（Retarget Op Stack）** 进行配置，其控制器类暴露了蓝图可调用的设置接口。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetSettings` | 获取当前 `BodyIntersectIK` 操作器的所有设置 | `UIKRetargetBodyIntersectController` |
| `SetSettings` | 设置 `BodyIntersectIK` 操作器的所有配置 | `UIKRetargetBodyIntersectController` |

### 使用示例（蓝图描述）

1.  打开或创建一个 **IK Retargeter** 资产。
2.  在目标骨架的操作栈（Op Stack）中，添加一个 `Body Intersect Goals` 操作器。
3.  在该操作器的细节面板中，配置以下关键项：
    - **TargetPhysicsAssetOverride**: 指定目标角色使用的物理资产。这是碰撞检测的基础。
    - **IntersectGoalSettings**: 数组，用于定义哪些 IK 目标（如 `LeftHand`, `RightFoot`）需要进行碰撞检测，以及它们的检测形状（缩放、偏移）。
    - **PropIntersectSettings**: 数组，用于配置道具骨骼（如 `weapon_r`）的检测胶囊体参数。
    - **PoleVectorIntersectSettings**: 数组，用于配置极向量骨骼的碰撞修正。
4.  运行时，可通过蓝图控制器动态修改这些设置。

## C++ 用法

### 头文件引入

```cpp
#include "BodyIntersectIKOp.h"
#include "PhysicsBodyHelpers.h"
```

### 基本用法：配置并应用 BodyIntersectIK Op

以下代码演示了如何在 C++ 中创建并配置一个 `FIKRetargetBodyIntersectIKOp` 操作器。（注：在实际 IK Retargeter 资产编辑中，此操作通常在编辑器内完成，C++ 用法更侧重于动态控制）。

```cpp
// 假设我们已经有了一个 FIkRetargetProcessor* Processor 和相关的目标骨架信息
// 1. 创建并配置设置
FIKRetargetBodyIntersectIKOpSettings IntersectSettings;
IntersectSettings.TargetPhysicsAssetOverride = MyTargetPhysicsAsset; // 设置目标物理资产
IntersectSettings.bEnableGoalIntersect = true;

// 2. 配置一个需要修正的 IK 目标，例如左手
FIKGoalIntersectShapeSettings LeftHandGoalSettings;
LeftHandGoalSettings.Goal = FName("LeftHand");
LeftHandGoalSettings.GoalShapeScale = FVector(1.0f, 1.0f, 1.0f); // 调整检测形状大小
IntersectSettings.IntersectGoalSettings.Add(LeftHandGoalSettings);

// 3. (可选) 配置一个道具骨骼，例如右手持枪的骨骼
FIKPropIntersectSettings WeaponBoneSettings;
WeaponBoneSettings.BoneName = FName("weapon_r");
WeaponBoneSettings.CapsuleRadius = 5.0f;
WeaponBoneSettings.CapsuleLength = 20.0f;
IntersectSettings.PropIntersectSettings.Add(WeaponBoneSettings);

// 4. 将设置应用到操作器实例 (FIKRetargetBodyIntersectIKOp 是操作器的具体实现)
FIKRetargetBodyIntersectIKOp BodyIntersectOp;
BodyIntersectOp.Settings = IntersectSettings;

// 5. 在重定向流程中，调用操作器的 Run 或 RunAfterParent 方法
// (这通常由 FIKRetargetProcessor 在其内部流程中处理)
BodyIntersectOp.Initialize(/* Processor, SourceSkeleton, TargetSkeleton, ... */);
BodyIntersectOp.Run(/* Processor, DeltaTime, SourceGlobalPose, OutTargetGlobalPose */);
```

### 进阶用法：使用 PhysicsBodyHelpers 计算形状交叉

`FBodyIntersectUtils` 提供了底层的几何体交叉检测函数，可用于自定义的物理交互逻辑。

```cpp
#include "PhysicsBodyHelpers.h"

// 获取两个物理形状的交叉推力向量
void CheckPropIntersection(const UPhysicsAsset* PhysAsset, FName PropBoneName, FName BodyBoneName, FVector& OutPushDir, double& OutPushStrength)
{
    // 1. 获取道具骨骼和身体骨骼的物理形状
    const FKShapeElem* PropShape = FPhysShapeUtils::FindBodyShape(PhysAsset, PropBoneName);
    const FKShapeElem* BodyShape = FPhysShapeUtils::FindBodyShape(PhysAsset, BodyBoneName);

    if (PropShape && BodyShape)
    {
        // 2. 假设我们有这两个骨骼的当前世界变换
        FTransform PropWorldTfm = /* ... 获取世界变换 */;
        FTransform BodyWorldTfm = /* ... 获取世界变换 */;

        // 3. 计算交叉推力
        OutPushStrength = FBodyIntersectUtils::CalcIntersectionPairDelta(
            PropWorldTfm,
            PropShape,
            BodyWorldTfm,
            BodyShape,
            OutPushDir
        );
        // OutPushStrength > 0 表示有交叉，值为交叉深度，OutPushDir 是推力方向
    }
}
```

## Demo 示例

一个最小的、演示如何创建 `BodyIntersectIKOp` 设置结构体的示例。

**文件：MyIntersectSettings.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "BodyIntersectIKOp.h"

UCLASS(Blueprintable)
class UMyIntersectSettingsFactory : public UObject
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "IK")
    static FIKRetargetBodyIntersectIKOpSettings CreateDefaultIntersectSettings()
    {
        FIKRetargetBodyIntersectIKOpSettings Settings;
        Settings.bEnableGoalIntersect = true;
        Settings.bEnablePoleVectorIntersect = false; // 仅启用目标点修正

        // 为“左右手”目标创建修正规则
        FIKGoalIntersectShapeSettings HandGoal;
        HandGoal.Goal = FName("LeftHand");
        HandGoal.GoalShapeScale = FVector(1.0f); // 使用默认缩放
        Settings.IntersectGoalSettings.Add(HandGoal);

        HandGoal.Goal = FName("RightHand");
        Settings.IntersectGoalSettings.Add(HandGoal);

        // 配置一些通用的身体检测体名称（这些名称需要与目标物理资产中的身体部位匹配）
        Settings.IntersectBodies.Add(FName("pelvis"));
        Settings.IntersectBodies.Add(FName("spine_01"));
        Settings.IntersectBodies.Add(FName("spine_02"));

        return Settings;
    }
};
```

## 模块依赖

要使用本插件，你的模块（通常是在编辑器扩展或运行时游戏中）需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `IKRetargetRuntime` | 提供 IK 重定向处理器 (`FIKRetargetProcessor`)、骨架结构和操作器基类，是本插件功能的运行时基础。 |
| `PhysicsCore` | 提供物理资产 (`UPhysicsAsset`)、物理形状元素 (`FKShapeElem`) 等核心物理类型，用于碰撞检测。 |

（注：`Core`, `CoreUObject`, `Engine`, `PhysicsCore` 为常见依赖，已按规范省略列表中的 `PhysicsCore` 为本插件关键依赖。）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-23 | `b70e3bb0` | [IK Retargeter] Add NotOverrideable meta to scalar TArrays in RelativeIK plugin retarget ops | 为重定向操作器中的标量TArray添加了`NotOverrideable`元数据，防止运行时被意外覆盖。 |
| 2026-04-14 | `66a98b79` | Migrate UE_LOG to UE_LOGF. | 将旧式`UE_LOG`宏迁移到格式化更安全的`UE_LOGF`。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 同上，继续进行日志宏迁移工作。 |
| 2026-04-14 | `701659c5` | RIK: Prop Intersection Pushout fix | 修复了道具（Prop）交叉检测推力计算的错误。 |
| 2026-04-08 | `23ef9e5c` | RelativeIK: Prop push out | 增强了道具推力功能。 |

### 维护评价

该插件创建于 **2025年7月**，非常新。从最近的 Git 提交记录看，它处于 **活跃开发状态**：
1.  **频繁更新**：最近一个月内有多次提交，内容涉及 **功能增强** (Prop push out)、**错误修复** (Prop Intersection Pushout fix) 和 **代码维护** (迁移日志宏)。
2.  **实验性标记**：插件明确标记为实验性 (`IsExperimentalVersion: true`)，且未默认启用，表明 Epic 可能正在内部测试和迭代该功能，API 未来可能存在变化。
3.  **实用性**：针对动画重定向中真实存在的痛点（空间穿透）提供了解决方案，有明确的使用场景。
4.  **推荐程度**：**建议关注和试用**。对于需要处理复杂体型差异或道具动画重定向的项目，值得一试。但由于其**实验性**状态，在生产项目中使用需谨慎，并准备好应对可能的 API 变更或行为调整。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/RelativeIKOp)
- 官方文档：暂无。