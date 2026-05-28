# Full Body IK

> 

| 属性 | 值 |
|---|---|
| 中文名 | 全身逆向运动学 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `FullBodyIK` (Runtime), `PBIK` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 🆕（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/FullBodyIK) | |

## 用途

这是一个基于物理的全身逆向运动学（Full Body IK）求解器插件，专为 ControlRig 系统设计。它解决了在动画蓝图中进行复杂、真实感全身角色动画控制的核心问题，特别是当需要精确控制末端效应器（如双手和双脚）位置，同时保持整个骨骼链（包括脊柱、骨盆）自然、符合物理约束的运动时。该插件是 ControlRig 框架下的高级功能模块。

## 使用场景

- 你需要让角色在游戏中精准地抓取不同高度和位置的物体，同时保持身体平衡和自然姿态。
- 你在开发 VR 应用，需要将用户的头部和手部控制器输入映射到虚拟角色的全身，实现逼真的动作同步。
- 你正在制作动画重定向系统，需要将一个角色的全身动画适配到体型不同的另一个角色身上，保持末端效应器的精确对位。

## 蓝图用法

本插件的功能主要通过 ControlRig 蓝图节点来使用，而非独立的蓝图节点。

### 核心节点（在 ControlRig 蓝图中）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Full Body IK Settings` | 配置全身IK求解器的参数（如迭代次数、容错值等）。 | `UControlRig` |
| `Set Bone Goal` | 为指定的骨骼（如手、脚）设置目标位置和旋转。 | `UControlRig` |
| `Solve` | 执行一次全身IK解算，根据目标更新所有骨骼。 | `UControlRig` |

### 使用示例（蓝图描述）

在你的 ControlRig 蓝图中：
1.  使用 `Set Full Body IK Settings` 节点配置求解器，通常连接到 `Begin Execution` 或 `Construction` 事件。
2.  为角色的双手、双脚等末端骨骼分别使用 `Set Bone Goal` 节点。这些节点的目标位置通常来自于动画蓝图中的输入变量（如追踪数据、鼠标点击位置等）。
3.  在 `Forwards Solve` 事件中，将上述配置好的 `Set Full Body IK Settings` 和 `Set Bone Goal` 节点按顺序连接，最后连接到 `Solve` 节点。
4.  `Solve` 节点的输出会自动应用到控制的角色骨骼网格体上。

## C++ 用法

### 头文件引入

```cpp
#include "FullBodyIK.h" // 核心求解器
#include "PBIK.h" // 底层物理IK库
```

### 基本用法

```cpp
// 假设你在一个与 ControlRig 集成的系统中
// 获取 ControlRig 实例
UControlRig* ControlRig = ...;

// 配置 FFullBodyIKSolver (具体类名需查阅模块头文件)
FFullBodyIKSolver Solver;
Solver.Settings.Iterations = 10;
Solver.Settings.Tolerance = 0.01f;

// 设置目标
Solver.SetGoal("LeftHand", FTransform(TargetPosition));
Solver.SetGoal("RightFoot", FTransform(FootTargetTransform));

// 执行解算
Solver.Solve(ControlRig->GetHierarchy());
```
*注：此为概念性示例，实际 API 需参考 `FullBodyIK` 模块的源码。*

### 进阶用法

结合 PBIK 模块可以访问更底层的物理约束和求解器控制，用于实现更复杂的行为，如：
- 动态调整求解器的刚度以适应不同动画阶段。
- 在求解过程中添加或移除临时约束。
- 与动画通知系统结合，在特定动画帧触发或改变 IK 行为。

## Demo 示例

由于该插件深度集成于 ControlRig，一个最小示例通常是一个包含 FBIK 节点的 ControlRig 资产。C++ 层面的独立集成示例较少。

```cpp
// MyAnimInstance.h
#pragma once

#include "CoreMinimal.h"
#include "Animation/AnimInstance.h"
#include "MyAnimInstance.generated.h"

UCLASS()
class UMyAnimInstance : public UAnimInstance
{
    GENERATED_BODY()

public:
    // 通常不直接持有求解器，而是通过 ControlRig 资产管理
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "IK")
    UControlRig* ControlRigAsset;

    virtual void NativeUpdateAnimation(float DeltaSeconds) override;
};

// MyAnimInstance.cpp
#include "MyAnimInstance.h"
#include "ControlRig.h"

void UMyAnimInstance::NativeUpdateAnimation(float DeltaSeconds)
{
    Super::NativeUpdateAnimation(DeltaSeconds);

    if (ControlRigAsset)
    {
        // ControlRig 的更新通常由系统自动处理
        // 这里可以设置一些蓝图变量，供 ControlRig 蓝图中的节点读取
        // 例如，将外部目标位置设置给 ControlRig 的输入
    }
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。`.uplugin` 中声明的 `ControlRig` 是关键的外部依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 统一日志宏格式，升级至 UE_LOGF。 |
| 2025-11-21 | `3c12f7ef` | [FBIK] Added back previously removed debug properties. | 恢复了之前被删除的 FBIK 调试属性。 |
| 2025-10-30 | `0990a715` | Ran UnrealCodeFixup on Fortnite to change all ~Type() {} to instead be ~Type() = default | 使用代码修复工具，统一析构函数写法为默认。 |
| 2025-10-30 | `a0e12af6` | Ran UnrealCodeFixup on Engine to change all ~Type() {} to instead be ~Type() = default | 引擎范围内的代码风格统一修复。 |
| 2025-10-21 | `8555965b` | [FBIK] Fixed crash bug from intermediate effectors on fork joints. | 修复了在分叉关节上使用中间效应器导致的崩溃 bug。 |

### 维护评价

该插件仍处于**活跃维护**状态。尽管位于 `Experimental` 目录下，但近期（2025年至2026年）有多次实质性更新，包括 bug 修复（解决了崩溃问题）和代码维护（风格统一、调试功能恢复）。这表明 Epic 仍在使用和维护此插件，它可能是 ControlRig 生态中一个重要的高级功能，正在向稳定版本过渡。对于需要在 ControlRig 中实现高级全身 IK 的项目，这是一个可依赖但需注意其“实验性”标签的选项。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/FullBodyIK)