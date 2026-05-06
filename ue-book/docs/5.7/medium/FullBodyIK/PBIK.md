# PBIK

> 基于物理的逆运动学（PBIK）求解器，用于 Control Rig 中的全身 IK 解算。

| 属性 | 值 |
|---|---|
| 中文名 | 物理IK求解器 |
| 分类 | Other |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `PBIK` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-07-29 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/FullBodyIK) | |

## 用途

PBIK（Physics-Based Inverse Kinematics）是 Unreal Engine 中专为 **Control Rig** 设计的高性能 IK 求解器。与传统的 CCD（Cyclic Coordinate Descent）或 FABRIK 算法不同，PBIK 通过将骨骼建模为带有质量、刚度和约束的物理链，能够更稳定、自然地处理复杂骨架（如人体全身）的 IK 问题。它支持：

- **多效应器同时求解**：可同时控制四肢、头部等多个目标点。
- **关节限制**：对每个骨骼可独立设置旋转角度限制（Free/Limited/Locked）。
- **刚度控制**：通过旋转/平移刚度调整骨骼抗弯曲能力。
- **链式预解（Pull Chain）**：自动将骨架划分为子链，整体旋转/平移以加速收敛。
- **偏好角度**：在链压缩时使骨骼倾向特定弯曲方向（如膝盖向前）。

该求解器旨在为角色动画提供高质量、高鲁棒性的全身 IK 结果，尤其适合需要自然姿态保持（如抓取、踩地、攀爬等）的场景。

## 使用场景

- **角色抓取物体**：同时将双手和双脚定位到指定世界位置，保持躯干自然不动。
- **地形自适应**：角色站在地面或台阶上时，自动调整双脚、臀部位置以贴合地形。
- **复杂机械臂控制**：需要精确角度限制和刚度调节的工业机械臂。
- **动画混合与重定向**：在 Control Rig 中作为基础 IK 单元，与其它 Rig 节点配合实现高级姿势。

## 蓝图用法

PBIK 模块在蓝图中主要通过 **Control Rig 节点** 使用，不暴露单独的 BlueprintCallable 函数。其核心数据结构 `FPBIKBoneSetting` 和 `FPBIKEffector` 支持在蓝图或细节面板中编辑。

### 核心节点（Control Rig 节点）

在 Control Rig 编辑器中搜索 `PBIK` 即可放置 `PBIK` 节点，该节点包含以下主要输入引脚（来自 `FPBIKEffector` 和 `FPBIKBoneSetting`）：

| 属性 | 说明 | 类型 |
|---|---|---|
| 根骨 | 求解器根骨骼，所有效应器链的根。 | 骨骼名称 |
| 骨骼设置 | 每个骨骼的刚度、限制、偏好角度数组。 | `TArray<FPBIKBoneSetting>` |
| 效应器 | 每个效应器关联的骨骼、目标变换、Alpha 值等。 | `TArray<FPBIKEffector>` |
| 迭代次数 | 求解器迭代次数，越高越精确但性能降低。 | int32 |
| 质量倍增器 | 全局质量缩放，影响骨骼刚度和收敛速度。 | float |
| 调试模式 | 是否绘制调试线。 | `FPBIKDebug` |

### 骨骼设置（`FPBIKBoneSetting`）

- `Bone`：应用设置的骨骼名称。
- `RotationStiffness` / `PositionStiffness`：范围 0~1，控制骨骼旋转/平移抗性。
- `X` / `Y` / `Z`：`EPBIKLimitType` 枚举（Free / Limited / Locked）。
- `MinX` / `MaxX` 等：限制模式下的角度边界（度）。
- `bUsePreferredAngles` / `PreferredAngles`：偏好角度模式开关及欧拉角。

### 效应器设置（`FPBIKEffector`）

- `Bone`：效应器要控制的骨骼。
- `Transform`：目标位置和旋转（世界或局部空间依上下文）。
- `PositionAlpha` / `RotationAlpha`：混合目标位置/旋转的强度（0~1）。
- `StrengthAlpha`：效应器拉拽力（0~1）。
- `ChainDepth`：显式设置的链深度，0 为自动检测。
- `PullChainAlpha`：链预解强度（0~1）。
- `PinRotation`：锁定效应器骨骼旋转到目标旋转的程度（0~1）。

### 使用示例（蓝图描述）

1. 在 Control Rig 资产中新建一个 `PBIK` 节点。
2. 输入根骨名称（如 `pelvis`）。
3. 创建 `FPBIKBoneSetting` 数组，为每块需要限制的骨骼（如 `thigh_l`、`calf_l` 等）设置刚度、角度限制和偏好角度。
4. 创建 `FPBIKEffector` 数组，分别设置左右手、左右脚的效应器，提供目标变换（通常来自外部引用的 Actor 或 IK 目标）。
5. 连接迭代次数（默认 5~10 即可），运行 Rig，观察骨骼被拉向目标。

## C++ 用法

### 头文件引入

```cpp
#include "PBIK.h"
#include "Core/PBIKSolver.h"
#include "Core/PBIKBody.h"
#include "Core/PBIKConstraint.h"
#include "PBIK_Shared.h"
```

### 基本用法

以下示例展示如何在 C++ 中手动初始化和执行 PBIK 求解器（基于 `FPBIKSolver` 类，源码位于 `Source/PBIK/Private/Core/PBIKSolver.cpp`）：

```cpp
// 创建求解器实例
FPBIKSolver Solver;

// 定义骨骼数组（例如简化的四肢链）
TArray<PBIK::FBone*> AllBones;

// 添加根骨骼
PBIK::FBone* Root = new PBIK::FBone(TEXT("root"), -1, FVector(0,0,100), FQuat::Identity, true);
AllBones.Add(Root);

// 添加子骨骼
PBIK::FBone* Child = new PBIK::FBone(TEXT("child"), 0, FVector(0,0,50), FQuat::Identity, false);
AllBones.Add(Child);

// 初始化求解器（内部会创建 RigidBody、Pin Constraint 等）
Solver.Initialize(AllBones);

// 设置骨骼约束参数（可选）
FPBIKBoneSetting BoneSetting;
BoneSetting.Bone = TEXT("child");
BoneSetting.RotationStiffness = 0.5f;
BoneSetting.X = EPBIKLimitType::Limited;
BoneSetting.MinX = -45.0f;
BoneSetting.MaxX = 45.0f;
Solver.SetBoneSetting(BoneSetting);

// 添加效应器
PBIK::FEffector* Effector = Solver.AddEffector(Child);
if (Effector)
{
    FEffectorSettings Settings;
    Settings.PositionAlpha = 1.0f;
    Settings.StrengthAlpha = 1.0f;
    Effector->SetGoal(FVector(0, 0, 30), FQuat::Identity, Settings);
}

// 执行求解
FPBIKSolverSettings SolverSettings;
SolverSettings.Iterations = 10;
Solver.Solve(SolverSettings);

// 更新骨骼最终变换
for (auto* Bone : AllBones)
{
    // Bone->Position 和 Bone->Rotation 已更新为解算结果
    // 可以进一步应用到骨架组件
}

// 清理（需手动释放）
for (auto* Bone : AllBones)
    delete Bone;
Solver.Reset();
```

*注意：实际使用时，PBIK 模块通常通过 Control Rig 节点调用，无需手动管理骨骼对象。上述代码仅为演示核心 API。*

### 进阶用法

**多效应器与链分割**  
当设置多个效应器时，求解器会自动检测链根（分支点或另一个效应器的位置）。通过 `FPBIKEffector::ChainDepth` 可强制指定链的长度。`PullChainAlpha` 可控制是否对整链进行预旋转/平移，加快收敛。

```cpp
// 为右脚效应器设置显式链深度（从脚跟到髋骨共 3 节）
FPBIKEffector FootEffector;
FootEffector.Bone = TEXT("foot_r");
FootEffector.ChainDepth = 3; // 包括 foot_r、calf_r、thigh_r
FootEffector.PullChainAlpha = 0.8f;
```

**角度限制与偏好角度**  
对于膝关节等需要固定弯曲方向的骨骼，建议先使用 `bUsePreferredAngles` 和 `PreferredAngles` 设定偏好方向，避免使用角度限制（限制可能需要更多迭代才能收敛）。

```cpp
FPBIKBoneSetting KneeSetting;
KneeSetting.Bone = TEXT("knee_l");
KneeSetting.bUsePreferredAngles = true;
KneeSetting.PreferredAngles = FVector(0.0f, 0.0f, -20.0f); // 让膝盖沿 Z 轴轻微向后弯曲
```

**调试可视化**  
启用 `FPBIKDebug::bDrawDebug = true` 可在视口中绘制骨骼线和效应器目标位置，辅助调试。

## Demo 示例

以下是一个完整的 Control Rig 节点实现（作为模块的一部分，不是独立运行示例），展示了如何在自定义 Rig 单元中集成 PBIK。由于 PBIK 模块本身已提供 `RigUnit_PBIK`，通常无需重新实现。此处仅提供最小化 C++ 示意框架。

### MyCustomRigUnit.h

```cpp
#pragma once
#include "RigVMCore/RigVMFunction.h"
#include "PBIK_Shared.h"
#include "Core/PBIKSolver.h"
#include "Core/PBIKBody.h"
#include "MyCustomRigUnit.generated.h"

USTRUCT(BlueprintType)
struct FMyCustomRigUnit : public FRigUnit
{
    GENERATED_BODY()

    // 输入
    UPROPERTY(EditAnywhere, Category = "Input")
    TArray<FPBIKBoneSetting> BoneSettings;

    UPROPERTY(EditAnywhere, Category = "Input")
    TArray<FPBIKEffector> Effectors;

    UPROPERTY(EditAnywhere, Category = "Input", meta = (ClampMin = "1", ClampMax = "50"))
    int32 Iterations = 10;

    // 输出
    UPROPERTY(EditAnywhere, Category = "Output")
    FTransform OutputTransform;

    virtual void Execute(FRigUnitContext& Context) override;
};
```

### MyCustomRigUnit.cpp

```cpp
#include "MyCustomRigUnit.h"
#include "BoneContainer.h"
#include "ControlRigDefines.h"

void FMyCustomRigUnit::Execute(FRigUnitContext& Context)
{
    PBIK::FPBIKSolver Solver;

    // 从 Context 中获取当前骨架数据（简化）
    // 实际需要从 ControlRig 上下文的 hierarchy 构建骨骼
    TArray<PBIK::FBone*> Bones;
    // ... 填充 Bones ...

    Solver.Initialize(Bones);

    // 应用骨骼设置
    for (const auto& Setting : BoneSettings)
    {
        Solver.SetBoneSetting(Setting);
    }

    // 添加效应器
    for (const auto& Eff : Effectors)
    {
        PBIK::FEffector* NewEff = Solver.AddEffectorByName(Eff.Bone);
        if (NewEff)
        {
            FEffectorSettings Settings;
            Settings.PositionAlpha = Eff.PositionAlpha;
            Settings.RotationAlpha = Eff.RotationAlpha;
            Settings.StrengthAlpha = Eff.StrengthAlpha;
            Settings.PullChainAlpha = Eff.PullChainAlpha;
            Settings.PinRotation = Eff.PinRotation;
            NewEff->SetGoal(Eff.Transform.GetLocation(), Eff.Transform.GetRotation(), Settings);
        }
    }

    // 求解
    FPBIKSolverSettings SolverSettings;
    SolverSettings.Iterations = Iterations;
    Solver.Solve(SolverSettings);

    // 输出结果（示例：输出效应器对应骨骼的变换）
    // 实际应将结果写回 Context 的骨骼姿势
    if (Effectors.Num() > 0)
    {
        const FName FirstBone = Effectors[0].Bone;
        // 查找骨骼并获取变换
        for (auto* Bone : Bones)
        {
            if (Bone->Name == FirstBone)
            {
                OutputTransform = FTransform(Bone->Rotation, Bone->Position);
                break;
            }
        }
    }

    // 清理
    for (auto* B : Bones) delete B;
}
```

## 模块依赖

PBIK 模块的 Build.cs 中声明了以下依赖。使用时请在您的模块 `.Build.cs` 中添加：

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "ControlRig",
    "RigVM",
    "FullBodyIK"   // 需要同时依赖 FullBodyIK（包含共享类型）
});
```

### 特殊依赖说明

| 模块 | 用途 |
|---|---|
| `ControlRigDeveloper` | 提供 ControlRig 节点注册与编译支持 |
| `ControlRigEditor` | 编辑器部分（节点创建、属性面板） |
| `RigVMDeveloper` | RigVM 节点运行时支持 |
| `RigVMEditor` | RigVM 编辑器图功能 |
| `AssetTools` | 资产操作支持 |
| `UnrealEd` | 编辑器基础设施 |
| `Engine` | 核心引擎功能（骨骼、动画） |

*注：以上部分模块在运行时可能不需要加载（如 Editor 模块），但在编译阶段必须链接。*

## 维护状态

### 近期更新

- 2025-11-18 e6c40773 修复了中间效应器在分叉关节上的崩溃错误。
- 2025-09-24 61d61d54 移除了 PBIK Rig 单元中损坏的旧调试绘制。
- 2025-07-29 3057849d 修复了非归一化旋转导致求解爆炸的问题。
- 2025-07-29 9bfb5815 修复求解器返回非归一化旋转的问题。

### 维护评价

PBIK 模块自 2025 年 7 月创建以来，在 4 个月内收到了至少 4 次功能性或 bug 修复更新，包括关键崩溃修复和旋转归一化问题。这表明该模块处于**活跃维护**状态。虽为较新模块，但已在稳定迭代。推荐在需要高质量全身 IK 的新项目中使用，尤其搭配 Control Rig。已知限制包括：高度约束的骨骼链可能需要较多迭代才能收敛；链自动检测在复杂分支下可能不够准确，建议手动设置 `ChainDepth`。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/FullBodyIK)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/FullBodyIK/Source/PBIK/Private/Tests)（如果存在）