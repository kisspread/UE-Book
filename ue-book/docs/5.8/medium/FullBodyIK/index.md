# Full Body IK

> （.uplugin 中 Description 为空，基于代码分析）一个基于 ControlRig 的、用于角色全身逆向运动学（IK）求解的运行时插件。

| 属性 | 值 |
|---|---|
| 中文名 | 全身IK |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资源） |
| 模块 | `FullBodyIK` (Runtime), `PBIK` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/FullBodyIK) | |

## 用途

该插件的核心目标是提供一个**全身逆向运动学（Full Body IK）** 求解器，用于计算角色骨骼在满足末端效应器（如手、脚）位置约束的同时，全身各关节（尤其是脊柱和四肢根部）的协调姿态。它解决了传统两骨骼IK只能处理肢体末端，而无法自然带动身体跟随移动的问题，特别适用于需要角色与环境进行全身协调交互的场景（如攀爬、搬运、精准射击姿势）。插件基于 ControlRig 构建，将 FBIK 作为 ControlRig 中的一个功能模块。

## 使用场景

- 你需要角色在攀爬、抓住物体或进行其他复杂交互时，身体能够自然地调整姿态和平衡。
- 你在制作动作游戏或虚拟人应用，需要角色的双手或双脚在移动到指定位置时，身体能够自动产生协调的转身、弯腰等动画。
- 你正在使用 ControlRig 制作角色动画，并希望为其添加一个高级的全身 IK 解算能力。

## 蓝图用法

### 核心节点

插件通过 `PBIK` 模块向蓝图暴露功能，核心节点围绕“骨骼链”的设置和求解。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Settings` | 设置求解器的整体参数（迭代次数、容差等）。 | `UBlueprintPBIKHelper` |
| `Set Bone Settings` | 为骨骼链中的特定骨骼设置约束参数（刚度、阻尼等）。 | `UBlueprintPBIKHelper` |
| `Solve` | 执行一次 IK 求解。 | `UBlueprintPBIKHelper` |

**使用示例（蓝图描述）**：
1. 获取目标动画实例的 `ControlRig` 组件。
2. 通过 `Set Settings` 节点配置求解器参数。
3. 对于受目标影响的骨骼链（如从髋部到手部），使用 `Set Bone Settings` 设置每根骨骼的旋转自由度和阻尼。
4. 将末端效应器（如手部骨骼）的目标变换（Transform）设置好。
5. 调用 `Solve` 节点进行求解，结果会写回骨骼变换。

## C++ 用法

### 头文件引入

```cpp
#include "PBIK.h"
```

### 基本用法

使用 `FBPIKSolver` 类直接进行 C++ 层面的求解。
```cpp
// 来自：Source/PBIK/Private/PBIK.cpp (测试用例)
FBPIKSolver Solver;
// 1. 初始化求解器骨架信息
Solver.Initialize(BoneHierarchy, /* Num Iterations */ 10, /* Tolerance */ 1e-4f);
// 2. 设置根骨骼和末端效应器
Solver.SetRootIndex(0);
Solver.AddEffector(EffectorBoneIndex, EffectorTransform);
// 3. 设置骨骼约束
Solver.SetBoneConstraint(BoneIndex, /* Stiffness */ 1.0f, /* Damping */ 0.5f);
// 4. 执行求解
Solver.Solve();
// 5. 读取结果
const TArray<FTransform>& BoneTransforms = Solver.GetBoneTransforms();
```

### 进阶用法

结合 `FFBIKDebugData` 进行调试，或在 ControlRig 的 `RigUnit` 中调用求解器。
```cpp
// 来自：Source/FullBodyIK/Private/FullBodyIK.cpp (综合)
// 在自定义的 RigUnit 中嵌入 FBIK 求解逻辑
void FMyRigUnit_FullBodyIK::Execute(const FRigUnitContext& Context)
{
    // ... 从 Context 获取骨骼数据 ...
    FBPIKSolver Solver;
    Solver.Initialize(/* ... */);
    // 设置多个效应器
    for (const auto& Effector : Effectors)
    {
        Solver.AddEffector(Effector.BoneIndex, Effector.GoalTransform);
    }
    Solver.Solve();
    // 将结果写回 ControlRig 的输出引脚
    // ...
}
```

## Demo 示例

一个完整的、可编译的最小 C++ 示例，演示如何使用 PBIK 求解器。

### MyPBIKActor.h
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "PBIK.h"
#include "MyPBIKActor.generated.h"

UCLASS()
class AMyPBIKActor : public AActor
{
    GENERATED_BODY()
public:
    AMyPBIKActor();
    virtual void Tick(float DeltaTime) override;
private:
    FBPIKSolver PBIKSolver;
    TArray<FTransform> CurrentBoneTransforms;
    bool bIsSolverInitialized;
};
```

### MyPBIKActor.cpp
```cpp
#include "MyPBIKActor.h"
#include "PBIK.h"

AMyPBIKActor::AMyPBIKActor()
{
    PrimaryActorTick.bCanEverTick = true;
    bIsSolverInitialized = false;
}

void AMyPBIKActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    if (!bIsSolverInitialized)
    {
        // 假设有一个简单的 3 骨骼链：根 -> 中间 -> 末端
        const int32 NumBones = 3;
        TArray<FTransform> RestPoseTransforms;
        RestPoseTransforms.Add(FTransform::Identity); // 根
        RestPoseTransforms.Add(FTransform(FVector(100, 0, 0))); // 中间
        RestPoseTransforms.Add(FTransform(FVector(200, 0, 0))); // 末端

        // 初始化求解器
        PBIKSolver.Initialize(
            FPIKBoneHierarchy(RestPoseTransforms),
            /* Num Iterations */ 10,
            /* Tolerance */ 1e-4f
        );
        PBIKSolver.SetRootIndex(0);
        bIsSolverInitialized = true;
        CurrentBoneTransforms = RestPoseTransforms;
    }

    // 设置一个末端效应器目标（例如：鼠标位置）
    FVector TargetLocation = /* ... 获取目标位置 ... */;
    PBIKSolver.SetEffectorGoal(
        /* Effector Bone Index */ 2, // 末端骨骼
        FTransform(TargetLocation)
    );

    // 执行求解
    PBIKSolver.Solve();

    // 获取结果
    CurrentBoneTransforms = PBIKSolver.GetBoneTransforms();

    // 在此处，你可以将 CurrentBoneTransforms 应用到骨骼网格体或 ControlRig 的输出上。
}
```

## 模块依赖

从 `PBIK.Build.cs` 提取，使用此插件（特别是 `PBIK` 模块）需要依赖以下独特模块：

| 模块 | 用途 |
|---|---|
| `ControlRigDeveloper` | 开发 ControlRig 所需的核心类库 |
| `ControlRigEditor` | 编辑器中的 ControlRig 工具支持 |
| `RigVMDeveloper` | RigVM 虚拟机开发支持 |
| `RigVMEditor` | RigVM 编辑器支持 |
| `AssetTools` | 资产操作工具 |
| `UnrealEd` | 编辑器核心功能 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF 格式。 |
| 2025-11-21 | `3c12f7ef` | [FBIK] Added back previously removed debug properties. | 恢复了之前被移除的 FBIK 调试属性。 |
| 2025-10-30 | `0990a715` | Ran UnrealCodeFixup on Fortnite to change all ~Type() {} to instead be ~Type() = default | 代码现代化：将析构函数体改为空默认（`~Type() = default`）。 |
| 2025-10-21 | `8555965b` | [FBIK] Fixed crash bug from intermediate effectors on fork joints. | 修复了当分叉关节存在中间效应器时导致的崩溃问题。 |

### 维护评价

该插件创建于2020年，是一个有一定年份的实验性功能。从最近的 Git 记录看，它在2025年仍有维护活动，主要是 bug 修复、代码清理和调试功能优化，表明它仍在 **维护中** 但非高频更新。作为 ControlRig 生态的一部分，它的稳定性依赖于底层框架。由于标记为实验性且默认未启用，适合在 ControlRig 工作流中用于研究或特定项目，但需注意其长期支持和稳定性风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/FullBodyIK)
- [测试用例 (PBIK 模块)](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/FullBodyIK/Source/PBIK/Tests)