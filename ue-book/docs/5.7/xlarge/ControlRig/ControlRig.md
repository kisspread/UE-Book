# Control Rig

> Framework for animation driven by user controls.

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `ControlRig` (Runtime), `ControlRigDeveloper` (Runtime), `ControlRigEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2017-02-08 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/ControlRig) | |

## 用途

ControlRig 是一个功能强大且高度可扩展的动画控制系统框架。它远不止于 `.uplugin` 描述中“由用户控件驱动的动画”，而是一个完整的**动画逻辑编程系统**。其核心是基于 **RigVM** 虚拟机执行的可视化图表（Graph），允许开发者和技术美术师通过连接节点（称为“Rig Unit”）来创建复杂的动画逻辑、程序化动画、IK/FK 解算、物理模拟以及动画重定向等。

它解决了以下问题：
1.  **复杂动画逻辑的可视化编程**：无需编写大量 C++ 代码，即可在编辑器中构建和调试复杂的动画逻辑。
2.  **程序化动画与运行时控制**：支持在运行时根据游戏逻辑（如瞄准、物理交互）动态修改骨骼变换。
3.  **动画重定向与适配**：提供工具将动画从一个骨架重定向到另一个不同比例或结构的骨架。
4.  **集成与扩展**：深度集成于 UE 动画系统（如 Sequencer、动画蓝图），并允许通过 C++ 或蓝图创建自定义的 Rig Unit 来扩展功能。

## 使用场景

-   你正在制作一个需要复杂 IK/FK 混合、物理模拟（如头发、布料）的角色动画 → 使用 ControlRig 构建解算逻辑。
-   你需要为游戏中的武器或载具创建程序化的动画（如枪械后坐力、车辆悬挂）→ 在 ControlRig 图表中实现。
-   你希望将动捕数据或现有动画重定向到不同体型的角色上 → 使用 ControlRig 的重定向工具。
-   你需要在 Sequencer 中精确控制角色的骨骼或控制器，制作过场动画 → 将 ControlRig 作为 Sequencer 轨道。
-   你希望为动画蓝图添加一个高度可定制、可复用的动画逻辑模块 → 将 ControlRig 作为动画蓝图中的一个节点。

## 蓝图用法

ControlRig 的蓝图 API 主要围绕**操作其内部的层级元素（骨骼、控制器、曲线等）**以及**驱动其执行**展开。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Curve Value` | 获取指定名称曲线的当前浮点值。 | `FRigUnit_GetCurveValue` |
| `Set Curve Value` | 设置指定名称曲线的浮点值。 | `FRigUnit_SetCurveValue` |
| `Unset Curve Value` | 使指定名称的曲线值失效。 | `FRigUnit_UnsetCurveValue` |
| `Curve Exists` | 检查指定名称的曲线是否存在。 | `FRigUnit_CurveExists` |
| `Find Closest Item` | 在给定的元素列表中，找到距离指定点最近的元素。 | `FRigUnit_FindClosestItem` |
| `Send Event` | 向引擎/编辑器发送一个事件（如请求自动关键帧）。 | `FRigUnit_SendEvent` |
| `Get Control Initial Transform` | 获取控制器的初始变换（已废弃，建议使用新接口）。 | `FRigUnit_GetControlInitialTransform` |
| `Get Initial Transform` | 获取骨骼的初始变换（已废弃，建议使用新接口）。 | `FRigUnit_GetInitialBoneTransform` |
| `Get Space Transform` | 获取空间（Space）的变换（已废弃，建议使用新接口）。 | `FRigUnit_GetSpaceTransform` |

### 使用示例（蓝图描述）

1.  **在动画蓝图中驱动曲线**：
    *   在动画蓝图的 `AnimGraph` 中，添加一个 `Control Rig` 节点。
    *   在该节点的细节面板中，指定要使用的 `ControlRig` 资产。
    *   在图表中，使用 `Set Curve Value` 节点，将 `Curve` 引脚连接到一个 `FName` 变量（如 `“LookAt_Weight”`），`Value` 引脚连接到一个计算出的浮点数（如基于角色朝向的权重）。这样就能在运行时动态控制动画曲线。

2.  **在 Sequencer 中控制角色**：
    *   将带有 `ControlRig` 组件的 Actor 添加到 Sequencer。
    *   为该 Actor 添加一个 `Control Rig` 轨道。
    *   在轨道中，你可以直接为 `ControlRig` 资产中定义的控制器（Controls）设置关键帧动画，实现精确的过场动画控制。

## C++ 用法

ControlRig 的 C++ 用法主要涉及**创建自定义的 Rig Unit**和**在代码中操作 ControlRig 实例**。

### 头文件引入

```cpp
#include "ControlRig.h"
#include "Units/RigUnit.h"
#include "ControlRigDefines.h"
```

### 基本用法：创建自定义 Rig Unit

以下是一个简单的自定义 Rig Unit 示例，它接收一个输入变换，输出一个缩放后的变换。

```cpp
// MyRigUnit.h
#pragma once

#include "Units/RigUnit.h"
#include "MyRigUnit.generated.h"

USTRUCT(meta=(DisplayName="My Scale Transform", Category="MyCustomUnits"))
struct FRigUnit_MyScaleTransform : public FRigUnit
{
    GENERATED_BODY()

    RIGVM_METHOD()
    virtual void Execute() override;

    // 输入变换
    UPROPERTY(meta=(Input))
    FTransform InputTransform;

    // 缩放系数
    UPROPERTY(meta=(Input))
    float ScaleFactor = 1.0f;

    // 输出变换
    UPROPERTY(meta=(Output))
    FTransform ScaledTransform;
};
```

```cpp
// MyRigUnit.cpp
#include "MyRigUnit.h"

void FRigUnit_MyScaleTransform::Execute()
{
    // 简单的缩放逻辑
    ScaledTransform = InputTransform;
    ScaledTransform.ScaleTranslation(FVector(ScaleFactor));
}
```
*（来源：基于 `FRigUnit` 的通用结构模式）*

### 进阶用法：在 C++ 中操作 ControlRig 实例

你可以在 C++ 中获取 `UControlRig` 实例，并设置其控制器的值或获取骨骼的变换。

```cpp
// 假设你已经有一个 UControlRig* ControlRigInstance
if (ControlRigInstance)
{
    // 获取层级控制器
    URigHierarchy* Hierarchy = ControlRigInstance->GetHierarchy();
    if (Hierarchy)
    {
        // 设置一个名为 “MyController” 的控制器的变换值
        FRigElementKey ControllerKey(“MyController”, ERigElementType::Control);
        FTransform NewTransform = /* ... 计算出的新变换 ... */;
        Hierarchy->SetGlobalTransform(ControllerKey, NewTransform);

        // 获取一个名为 “Spine_01” 的骨骼的当前全局变换
        FRigElementKey BoneKey(“Spine_01”, ERigElementType::Bone);
        FTransform BoneTransform = Hierarchy->GetGlobalTransform(BoneKey);
        // ... 使用 BoneTransform ...
    }
}
```
*（来源：基于 `URigHierarchy` 的通用操作模式）*

## Demo 示例

一个最小的自定义 Rig Unit，用于将输入向量归一化。

```cpp
// NormalizeVectorRigUnit.h
#pragma once

#include "Units/RigUnit.h"
#include "NormalizeVectorRigUnit.generated.h"

USTRUCT(meta=(DisplayName="Normalize Vector", Category="Math|Vector"))
struct FRigUnit_NormalizeVector : public FRigUnit
{
    GENERATED_BODY()

    RIGVM_METHOD()
    virtual void Execute() override;

    UPROPERTY(meta=(Input))
    FVector InputVector;

    UPROPERTY(meta=(Output))
    FVector NormalizedVector;

    UPROPERTY(meta=(Output))
    float VectorLength;
};
```

```cpp
// NormalizeVectorRigUnit.cpp
#include "NormalizeVectorRigUnit.h"

void FRigUnit_NormalizeVector::Execute()
{
    VectorLength = InputVector.Size();
    if (VectorLength > KINDA_SMALL_NUMBER)
    {
        NormalizedVector = InputVector.GetUnsafeNormal();
    }
    else
    {
        NormalizedVector = FVector::ZeroVector;
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `RigVM` | ControlRig 的核心虚拟机，负责图表的编译和执行。 |
| `AnimationCore` | 提供动画系统的基础数学和工具函数。 |

## 维护状态

### 近期更新

-   2025-10-03 65fb3e75ab41 Control Rig Pose: Guard against nullptr
-   2025-09-15 e4c1796bad0d [ControlRig & RigVM] replace function graph task with ExecuteOnGameThread to avoid scheduling tasks during package save, which can lead random crashes
-   2025-08-20 0c3e1f3d6451 Constraints: recursive anim evaluation (follow-up) - mark the parent for evaluation at least once as the constraint being created is not evaluated - if any of the component's parent is a skeletal mesh and has a valid evaluator, then it will be used to compose the global transform - get the transform from the last cached component space transforms (when possible) if the evluator update couldn't finish (existing parallel evaluation or post-evaluating)

### 维护评价

**活跃维护**。ControlRig 作为 UE 动画系统的核心组件之一，自 2017 年创建以来持续得到 Epic Games 的积极维护和功能增强。从近期的 Git 提交记录可以看出，团队仍在不断修复关键 bug（如崩溃问题）、优化性能（如动画求值）并完善功能（如约束系统）。尽管插件本身已较为成熟，但其底层依赖的 RigVM 和动画系统仍在演进，因此 ControlRig 也会随之更新。**强烈推荐使用**，它是 UE5 中实现高级程序化动画和复杂动画逻辑的首选方案。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/ControlRig)
-   [官方文档](https://docs.unrealengine.com/5.7/en-US/control-rig-in-unreal-engine/)（UE5 官方文档）
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/ControlRig/Tests)