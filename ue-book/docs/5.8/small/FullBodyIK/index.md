# Full Body IK

> （Description 字段为空，根据源码分析填写）一个基于物理的全身逆运动学（Full Body IK）求解器模块，集成于 ControlRig 框架中。

| 属性 | 值 |
|---|---|
| 中文名 | 全身逆运动学 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（可能包含资产、示例） |
| 模块 | `FullBodyIK` (Runtime), `PBIK` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/FullBodyIK) | |

## 用途

该插件提供了一套在 ControlRig 框架内实现的、基于物理约束的全身逆运动学（Full Body IK）求解算法。它旨在解决需要高度物理真实性和角色肢体协调性的动画驱动问题。通过让角色的四肢在遵循物理规律（如重力、碰撞、关节限制）的同时，达到目标姿态或位置，实现动画驱动与物理模拟的平衡。插件的核心是 `PBIK`（Physics-Based IK）求解器，而 `FullBodyIK` 模块为其提供了在 UE 动画系统（如 ControlRig）中的集成层。

## 使用场景

- 你需要一个角色在保持物理稳定性的前提下，伸手去抓取一个物体。
- 你在制作格斗或体育游戏，需要角色在击打或跳跃落地时，根据接触面和物理环境自动调整身体姿态。
- 你在创建需要与环境进行复杂物理交互的角色动画，例如角色在不平整地形上行走或攀爬。

## 模块文档概览

| 模块 | 类型 | 说明 |
|---|---|---|
| **FullBodyIK** | Runtime | 核心集成模块，将物理IK求解器（PBIK）暴露给ControlRig系统。 |
| **PBIK** | Runtime | 物理逆运动学（Physics-Based IK）求解器实现，包含核心算法和节点。 |

## 蓝图用法

插件主要通过 ControlRig 图表节点提供功能。以下是基于源码的核心节点分组：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FBIK Solver` | 全身物理逆运动学求解器节点，作为控制流的起点。 | `UPBIKSolver` |
| `Set Skeletal Mesh Component` | 为求解器绑定目标骨骼网格体组件。 | - |
| `Set Physics Asset` | 为求解器设置物理资产，用于定义碰撞和约束。 | - |
| `Set Effector Transform` | 设置末端效应器（如手、脚）的目标变换。 | - |
| `Set Bone Settings` | 为特定骨骼设置求解权重、刚度等参数。 | - |

*(更详细的节点说明请参考各模块的专属文档 `FullBodyIK.md` 和 `PBIK.md`)*

### 使用示例（蓝图描述）

1. 在 ControlRig 图表中，拖入一个 `FBIK Solver` 节点。
2. 在初始化阶段，使用 `Set Skeletal Mesh Component` 节点将你的角色骨骼网格体赋值给求解器。
3. 使用 `Set Physics Asset` 节点指定角色的物理资产。
4. 在每帧更新时，使用 `Set Effector Transform` 节点，通过一个 `Transform` 变量（可能来自场景中的某个 Actor 或计算值）来驱动角色手脚的位置和旋转。
5. 根据需要使用 `Set Bone Settings` 节点调整特定骨骼（如脊椎）的求解优先级和物理属性。
6. 最终，求解结果会写回骨骼网格体，影响动画姿态。

## C++ 用法

以下示例演示了如何在 C++ 中创建和使用 PBIK 求解器。主要逻辑来源于引擎测试用例。

### 头文件引入

```cpp
#include "PBIK.h" // 引入PBIK模块头文件
// 通常也需要引入 ControlRig 相关头文件
#include "ControlRig.h"
```

### 基本用法

(来源于测试用例 `PBIKTest.cpp`)

```cpp
// 1. 创建 PBIK 求解器实例
FPBIKSolver Solver;

// 2. 初始化求解器，传入一个骨架数据 (USkeleton)
Solver.Initialize(SkeletonData);

// 3. 设置求解目标（例如，一个末端效应器的目标位置）
FPBIKEffector Effector;
Effector.Bone = TEXT("hand_r");
Effector.Transform = TargetTransform; // FTransform
Solver.SetEffector(Effector);

// 4. 设置物理约束和骨骼参数（可选）
Solver.SetBoneSettings(BoneName, Stiffness, Weight);

// 5. 每帧运行求解
Solver.Solve(DeltaTime);

// 6. 从求解器中提取结果（骨骼变换）
const TArray<FTransform>& BoneTransforms = Solver.GetBoneTransforms();
```

### 进阶用法

结合 ControlRig 框架使用，通常涉及创建一个自定义的 `UControlRig` 子类，并在其 `Initialize` 和 `Execute` 函数中操作 PBIK 求解器。

## Demo 示例

一个最小化的 C++ 示例，展示求解器的基本生命周期。

**FBIKDemo.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "PBIK.h"

class FFBIKDemo
{
public:
    void Init(USkeleton* InSkeleton);
    void Update(float DeltaTime, const FTransform& HandTargetTransform);
    const TArray<FTransform>& GetSolvedBoneTransforms() const;

private:
    FPBIKSolver Solver;
};
```

**FBIKDemo.cpp**
```cpp
#include "FBIKDemo.h"

void FFBIKDemo::Init(USkeleton* InSkeleton)
{
    Solver.Initialize(InSkeleton);
}

void FFBIKDemo::Update(float DeltaTime, const FTransform& HandTargetTransform)
{
    // 设置右手为末端效应器
    FPBIKEffector RightHandEff;
    RightHandEff.Bone = TEXT("hand_r");
    RightHandEff.Transform = HandTargetTransform;
    Solver.SetEffector(RightHandEff);

    // 可以在此处添加更多骨骼的设置

    // 执行求解
    Solver.Solve(DeltaTime);
}

const TArray<FTransform>& FFBIKDemo::GetSolvedBoneTransforms() const
{
    return Solver.GetBoneTransforms();
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ControlRig` | 核心依赖。PBIK 求解器作为 ControlRig 节点运行的基础。 |
| `ControlRigDeveloper`, `ControlRigEditor` | PBIK 模块的依赖，用于在编辑器中开发和调试 ControlRig 及其节点。 |
| `RigVMDeveloper`, `RigVMEditor` | ControlRig 底层虚拟机和编辑器的开发支持，被 PBIK 模块间接依赖。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移，代码现代化。 |
| 2025-11-21 | `3c12f7ef` | [FBIK] Added back previously removed debug properties. | 恢复了之前被移除的调试属性，增强调试能力。 |
| 2025-10-30 | `0990a715` | Ran UnrealCodeFixup on Fortnite to change all ~Type() {} to instead be ~Type() = default | 代码清理，统一析构函数写法。 |
| 2025-10-30 | `a0e12af6` | Ran UnrealCodeFixup on Engine to change all ~Type() {} to instead be ~Type() = default | 引擎级代码清理，与上一条属于同一批次。 |
| 2025-10-21 | `8555965b` | [FBIK] Fixed crash bug from intermediate effectors on fork joints. | 修复了在分支关节上使用中间效应器导致的崩溃Bug。 |

### 维护评价

该插件创建于 2020 年，处于 **活跃维护** 状态。近期（2025-2026年）持续有实质性的更新，包括 **Bug 修复**（如崩溃问题）、**功能恢复**（调试属性）和 **代码质量改进**（日志迁移、代码风格统一）。这表明 Epic Games 内部仍在使用和维护此模块。作为实验性插件（位于 `Experimental` 目录），其 API 稳定性可能低于核心模块，但当前维护状态良好，**推荐**在需要高级物理角色动画的项目中探索和使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/FullBodyIK)
- [官方文档]()（暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Experimental/FullBodyIK/Source/PBIK/Tests/PBIKTest.cpp) (PBIK 模块测试)