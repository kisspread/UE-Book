# Spatially Aware Retarget Ops

> A collection of Retarget Ops for preserving spatial relationships on retargeted animations

| 属性 | 值 |
|---|---|
| 中文名 | 空间感知重定向操作 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `BodyIntersectIKOp` (Runtime), `PreviewPropOp` (Runtime), `RelativeBodyAnimInfo` (Runtime), `RelativeBodyAnimUtils` (Runtime), `RelativeIKOp` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-07-23 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/RelativeIKOp) | |

## 用途

`RelativeIKOp` 是一个实验性插件，它提供了一套增强的 IK 重定向操作（`Ops`），用于在动画重定向过程中保留角色肢体与环境、道具之间的相对空间关系。传统的 IK 重定向可能仅根据骨骼链长度进行调整，而此插件通过分析源动画中的物理资产（`PhysicsAsset`）的碰撞体（`Bodies`）空间位置关系，并将这些“相对”关系映射到目标骨骼上，从而实现更精确的交互式动画重定向。例如，确保角色手扶栏杆、脚踩地面或紧握道具等动作在不同体型的角色间重定向后，仍然保持正确的接触点和空间位置。

## 使用场景

- 当你需要将一个角色与特定道具或环境（如椅子、武器、墙壁）交互的动画，重定向到另一个骨骼比例不同的角色时，希望保持手或脚与道具/环境的相对位置不变。
- 在制作需要高度物理准确性的动画重定向（如坐姿、攀爬、抓取）时，需要 IK 目标点根据接触关系动态调整。
- 在测试或调试动画重定向效果时，需要可视化查看身体部位对、接触关系以及 IK 目标点的贡献和生成过程。

## 蓝图用法

该插件主要通过 IK Retargeter 栈中的操作（`Ops`）进行配置和使用。核心是两个主要操作及其对应的控制器（`Controller`），控制器提供了蓝图 API 来获取和设置参数。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Settings` | 获取 `Relative IK` 操作的当前所有设置参数。 | `UIKRetargetRelativeIKController` |
| `Set Settings` | 应用一个 `FIKRetargetRelativeIKOpSettings` 结构体来设置 `Relative IK` 操作的参数。 | `UIKRetargetRelativeIKController` |
| `Get Settings` | 获取 `Relative Pelvic Motion` 操作的当前所有设置参数。 | `UIKRetargetPelvicMotionController` |
| `Set Settings` | 应用一个 `FIKRetargetPelvicMotionOpSettings` 结构体来设置 `Relative Pelvic Motion` 操作的参数。 | `UIKRetargetPelvicMotionController` |

### 使用示例（蓝图描述）

1.  在 `IK Retargeter` 资产中，向重定向栈（`Retarget Pose Stack`）添加一个 `Relative IK Goals` 或 `Relative Pelvic Motion` 操作。
2.  在该操作的详细信息面板中，配置基本参数，如 `Target Physics Asset Override`（目标物理资产）、`Body Mapping`（身体映射）、`Pin Prop Bones`（固定道具骨骼）等。
3.  如果需要更精细地控制或通过蓝图动态调整，可以获取该操作的 `Controller`（例如 `UIKRetargetRelativeIKController`）。
4.  使用 `Get Settings` 节点获取当前设置的结构体。
5.  修改结构体中的参数（如 `DistanceThreshold`、`bDebugDrawBodyPairs` 等）。
6.  使用 `Set Settings` 节点将修改后的结构体应用回操作。

## C++ 用法

该插件通常作为 IK 重定向系统的一部分使用。核心用法是配置 `FIKRetargetRelativeIKOpSettings` 结构体，并将其关联到 `FIKRetargetRelativeIKOp` 操作上。

### 头文件引入

```cpp
#include "RelativeIKOp/Public/RelativeIKOp.h"
```

### 基本用法

配置并初始化一个 Relative IK Op。

```cpp
// 引用来源：基于 Public/RelativeIKOp.h 中的结构体定义和 Op 类
// 假设你已经有了一个 FIKRetargetProcessor 实例 (Processor)
// 以及对应的源、目标骨架 (SourceSkeleton, TargetSkeleton)

// 1. 创建设置结构体并配置关键参数
FIKRetargetRelativeIKOpSettings RelativeIKSettings;
RelativeIKSettings.TargetPhysicsAssetOverride = MyTargetPhysicsAsset; // 设置目标物理资产
RelativeIKSettings.DistanceThreshold = 70.0f;
RelativeIKSettings.bMultiBoneSolve = true;
// ... 其他参数设置

// 2. 创建操作实例
FIKRetargetRelativeIKOp RelativeIKOp;
RelativeIKOp.Settings = RelativeIKSettings;

// 3. 初始化操作 (通常由重定向处理器在管线中调用)
FIKRigLogger Log;
bool bSuccess = RelativeIKOp.Initialize(Processor, SourceSkeleton, TargetSkeleton, /*InParentOp (e.g., IK Rig Op)*/, Log);
```

### 进阶用法

操作可以在运行时（`Run`）被重定向处理器调用，更新目标姿态。同时，操作还支持调试绘制。

```cpp
// 在重定向管线的运行阶段，处理器会调用操作的 Run 方法
// 以下为概念性示意，展示操作如何与姿态数据交互
TArray<FTransform> SourceGlobalPose; // 当前源姿态
TArray<FTransform> TargetGlobalPose; // 输出目标姿态

// 模拟一帧的运行
RelativeIKOp.Run(Processor, DeltaTime, SourceGlobalPose, TargetGlobalPose);

// 如果需要在编辑器中查看调试信息，操作实现了 DebugDraw
#if WITH_EDITOR
// FIKRetargetDebugDrawState 包含了绘制所需的状态信息
// RelativeIKOp.DebugDraw(InPDI, SourceTransform, ComponentTransform, ComponentScale, EditorState);
#endif
```

## Demo 示例

一个演示如何创建和配置 `Relative IK Op` 的最小 C++ 示例。

```cpp
// MyAnimRetargeter.h
#pragma once
#include "CoreMinimal.h"
#include "IKRetargeter/IKRetargetOpBase.h"

class FMyRelativeIKDemo
{
public:
    static void SetupAndRunRelativeIKDemo();
};
```

```cpp
// MyAnimRetargeter.cpp
#include "MyAnimRetargeter.h"
#include "RelativeIKOp/Public/RelativeIKOp.h"
#include "IKRetarget/IKRetargetProcessor.h"

void FMyRelativeIKDemo::SetupAndRunRelativeIKDemo()
{
    // 注意：此示例省略了创建 Processor、加载骨架和物理资产等前置步骤。
    // 假设我们已经有以下对象：
    // FIKRetargetProcessor Processor;
    // FRetargetSkeleton SourceSkeleton;
    // FTargetSkeleton TargetSkeleton;
    // UPhysicsAsset* MyPhysicsAsset = ...;

    // 1. 配置 Relative IK 操作设置
    FIKRetargetRelativeIKOpSettings Settings;
    Settings.TargetPhysicsAssetOverride = MyPhysicsAsset;
    Settings.BodyMapping.Add(TEXT("pelvis"), TEXT("pelvis")); // 示例映射
    Settings.DistanceThreshold = 50.0f;
    Settings.bDebugDrawBodyPairs = true; // 启用调试绘制

    // 2. 创建操作并应用设置
    FIKRetargetRelativeIKOp RelativeIKOp;
    RelativeIKOp.Settings = Settings;

    // 3. 初始化 (需要处理器、骨架和日志)
    FIKRigLogger Log;
    bool bInitialized = RelativeIKOp.Initialize(Processor, SourceSkeleton, TargetSkeleton, nullptr, Log);

    if (bInitialized)
    {
        // 4. 模拟一帧更新 (实际由处理器驱动)
        TArray<FTransform> DummySourcePose; // 需要填充源数据
        TArray<FTransform> TargetPose;      // 输出缓冲
        RelativeIKOp.Run(Processor, 0.016f, DummySourcePose, TargetPose);

        // TargetPose 现在包含了应用了相对 IK 逻辑的目标骨骼变换
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `PhysicsCore` | 访问 `UPhysicsAsset`、`FKShapeElem` 等物理资产和形状数据。 |
| `AnimationCore` | 基础的动画和骨骼变换操作。 |
| `AnimGraphRuntime` | 动画图运行时支持。 |
| `AnimGraph` | （编辑器）调试绘制等功能。 |
| `IKRig` | 核心的 IK 重定向框架，提供 `UIKRetargeter`、`FIKRetargetProcessor` 等基础类。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-23 | `b70e3bb0` | [IK Retargeter] Add NotOverrideable meta to scalar TArrays in RelativeIK plugin retarget ops | 为插件中设置项的TArray属性添加`NotOverrideable`元数据，防止被错误覆盖。 |
| 2026-04-14 | `66a98b79` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 `UE_LOG` 迁移为更现代的 `UE_LOGF`。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 同上，另一个相关提交。 |
| 2026-04-14 | `701659c5` | RIK: Prop Intersection Pushout fix | 修复了道具相交推离（Intersection Pushout）功能的一个问题。 |
| 2026-04-08 | `23ef9e5c` | RelativeIK: Prop push out | 添加了基于相交的道具推离功能。 |

### 维护评价

`RelativeIKOp` 是一个相对较新（创建于 2025 年中）且仍处于**实验性**阶段的插件。从近期的 Git 提交记录来看，它在 2026 年 4 月仍有活跃的开发和维护，包括功能添加（如道具推离）、Bug 修复和代码优化（日志迁移）。

由于其**实验性**状态，API 和功能可能在未来版本中发生变化。它旨在解决高级动画重定向中的特定痛点（空间关系保持），对于有此需求的项目来说，是一个值得关注和测试的工具。建议在生产环境中谨慎使用，并密切关注其后续更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/RelativeIKOp)
- [官方文档]() (暂无)
- [测试用例]() (未在插件目录内发现，可能位于引擎测试套件中)