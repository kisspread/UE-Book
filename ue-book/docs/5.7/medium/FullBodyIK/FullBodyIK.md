# Full Body IK

> 

| 属性 | 值 |
|---|---|
| 中文名 | 全身 IK |
| 分类 | Other |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无（纯代码插件，包含 ControlRig 节点） |
| 模块 | `FullBodyIK` (Runtime), `PBIK` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-07-29 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/FullBodyIK) | |

## 用途

Full Body IK 插件提供基于雅可比（Jacobian）的全身逆运动学求解器，专门为 ControlRig 系统设计。它支持多个同时作用的位置/旋转端效应器（如手脚、头部），并允许对每个关节定义刚度、角度限制、极点向量等约束。相比于简单的两骨 IK（如 LookAt、TwoBoneIK），全身 IK 能处理复杂的多支链结构，使角色以自然协调的方式适应环境。

为什么存在？标准 ControlRig 提供的 IK 节点（如 TwoBoneIK、CCD）只能处理单链或少关节，而全身 IK 需要同时满足多个约束（如脚踩地面、手抓物体、头看目标），并且保持身体姿态合理（例如脊柱弯曲、肩部旋转）。这个插件填补了多目标、多约束 IK 的空白，特别适合复杂交互动画（攀爬、搬运、三脚架站立等）。

## 使用场景

- **交互式环境适应**：角色站在不平整地形上，双脚和单手同时接触物体
- **复杂抓取**：角色双手和头部同时定位到指定目标
- **三脚架姿态**：双脚和一只手作为支撑点，另一只手自由活动
- **动画重定向**：在运行时根据外部定位设备（如 VR 控制器）调整角色末端
- **物理混合**：与物理模拟结合，实现部分动态、部分 IK 的混合控制

## 蓝图用法

插件核心节点通过 ControlRig 图暴露。在蓝图或动画蓝图中的 ControlRig 组件中，可以放置 **Full Body IK** 节点（对应 `FRigUnit_FullbodyIK`）。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Full Body IK` | 全身 IK 求解节点 | `FRigUnit_FullbodyIK` |

### 节点输入引脚

| 引脚名 | 类型 | 说明 |
|---|---|---|
| `Root` | `Bone` | 指定 IK 链的根骨骼 |
| `Effectors` | `Array<FFBIKEndEffector>` | 端效应器列表，每个包含目标位置、旋转、权重、Pull 因子等 |
| `Constraints` | `Array<FFBIKConstraintOption>` | 关节约束选项，包括线性/角刚度、角度限制、极点向量 |
| `SolverSettings` | `FSolverInput` | 求解参数（迭代次数、精度、阻尼、刚度缩放） |
| `DebugOption` | `FFBIKDebugOption` | 调试可视化开关 |
| `PoleVectorOption` | (通过 ConstraintOption 设置) | 极点向量方向/位置模式 |

### 使用示例（蓝图描述）

1. 在 ControlRig 蓝图中，将 `Full Body IK` 节点拖入事件图。
2. 连接 `Root` 引脚到你的根骨骼（如 `pelvis`）。
3. 将 `Effectors` 引脚连接到一个 Make Array 节点，然后为每个端效应器（如左右脚、手）创建 `FFBIKEndEffector` 结构：
   - 设置 `Item` 为目标骨骼（例如 `foot_l`）。
   - 设置 `Position` 和 `Rotation` 来自外部输入（如动画通知或场景组件位置）。
   - 调整 `Pull` 值（0~1）来控制该效应器“拉动”强度，避免奇异点。
4. 将 `Constraints` 引脚连接到一个 Make Array 节点，为链中的每个重要关节创建约束选项：
   - 设置关节 `Item`（如 `knee_l`）。
   - 开启 `bUseStiffness` 并设置 `LinearStiffness` / `AngularStiffness`（0~1，1表示完全锁定）。
   - 如需角度限制，打开 `bUseAngularLimit` 并设置各轴限制。
   - 如要极点向量控制，打开 `bUsePoleVector` 并设置方向和模式。
5. 设置 `SolverSettings`：`MaxIterations`（4~16 常见）、`Precision`（0.1~1.0）、`Damping`（15~30）。
6. 运行 ControlRig，观察骨骼自动调整姿势。

## C++ 用法

插件核心 API 位于 `FullBodyIK` 和 `PBIK` 模块，但主要求解器类 `FJacobianSolver_FullbodyIK` 封装了雅可比求解逻辑，可直接在 C++ 中使用（无需经过 ControlRig 图）。

### 头文件引入

```cpp
#include "FBIKConstraint.h"
#include "FBIKShared.h"
#include "JacobianSolver.h"
```

### 基本用法

以下示例演示如何手动设置一个简单的全身 IK 求解：

```cpp
// 来源：Engine/Plugins/Experimental/FullBodyIK/Source/FullBodyIK/Private/JacobianSolver.cpp (假设)

// 创建求解器
FJacobianSolver_FullbodyIK Solver;

// 1. 构建链路数据 (TArray<FFBIKLinkData>)
TArray<FFBIKLinkData> LinkData;
// 假设已有骨骼链转换数据，逐个填充：
FFBIKLinkData RootLink;
RootLink.SetParentLinkIndex(INDEX_NONE);
RootLink.SetTransform(FTransform::Identity);
RootLink.SetLength(10.0f);
// 添加运动轴（默认三个轴，可自定义刚度）
RootLink.AddMotionBase(FMotionBase(FVector(1,0,0)));
...
LinkData.Add(RootLink);
// 重复添加后续关节...

// 2. 构建端效应器
TMap<int32, JacobianIK::FFBIKEffectorTarget> EffectorTargets;
FFBIKEffectorTarget Target;
Target.bPositionEnabled = true;
Target.Position = FVector(100, 0, 50);
Target.bRotationEnabled = false;
Target.LinearMotionStrength = 0.8f;
Target.TargetClampScale = 0.2f;
// 关联到链路索引 (设最后一个关节为效应器)
EffectorTargets.Add(LinkData.Num() - 1, Target);

// 3. 设置求解参数
FSolverParameter SolverParam;
SolverParam.MaxIterations = 10;
SolverParam.Tolerance = 0.5f;
SolverParam.Damping = 15.0f;
SolverParam.UseJacobianTranspose = false; // 默认使用 PIDLS

// 4. 执行求解
TArray<FJacobianDebugData> DebugData;
bool bConverged = Solver.SolveJacobianIK(
    LinkData, 
    EffectorTargets, 
    SolverParam, 
    SolverParam.MaxIterations, 
    SolverParam.Tolerance, 
    &DebugData
);

// 5. 读取更新后的链路变换
FTransform NewRoot = LinkData[0].GetTransform();
```

### 进阶用法

结合 ControlRig 单位自定义求解：如果需要更灵活的流程，可以继承 `FJacobianSolver_FullbodyIK` 并重写 `InitializeSolver` / `PreSolve` 来修改数据或应用自定义约束。

```cpp
class FMySolver : public FJacobianSolver_FullbodyIK
{
protected:
    virtual void PreSolve(
        TArray<FFBIKLinkData>& InOutLinkData,
        const TMap<int32, FFBIKEffectorTarget>& InEndEffectors) const override
    {
        // 在每次迭代前调整刚度或应用外部力
        for (auto& Link : InOutLinkData)
        {
            // 例如根据时间动态改变线性刚度
            if (Link.LinearMotionStrength > 0.5f)
                Link.LinearMotionStrength *= 0.9f;
        }
    }
};
```

然后使用 `FPostProcessDelegateForIteration` 添加每帧后处理：

```cpp
Solver.SetPostProcessDelegateForIteration(
    FPostProcessDelegateForIteration::CreateLambda(
        [](TArray<FFBIKLinkData>& InOutLinkData)
        {
            // 应用约束库中定义的硬限制
            TArray<ConstraintType> Constraints;
            FBIKConstraintLib::BuildConstraints(/*...*/);
            FBIKConstraintLib::ApplyConstraint(InOutLinkData, &Constraints);
        }
    )
);
```

## Demo 示例

以下是一个完整的 .h + .cpp 示例，演示如何在一个自定义 Actor 组件中每帧运行全身 IK（不使用 ControlRig）。

### FullBodyIKComponent.h

```cpp
#pragma once

#include "Components/ActorComponent.h"
#include "FBIKConstraint.h"
#include "FBIKShared.h"
#include "JacobianSolver.h"
#include "FullBodyIKComponent.generated.h"

UCLASS(ClassGroup=(IK), meta=(BlueprintSpawnableComponent))
class UFullBodyIKComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UFullBodyIKComponent();

    virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "IK")
    FSolverInput SolverInput;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "IK")
    TArray<FFBIKLinkData> LinkData; // 实际应用中应从骨骼 Mesh 填充

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "IK")
    TMap<int32, JacobianIK::FFBIKEffectorTarget> EffectorTargets;

private:
    FJacobianSolver_FullbodyIK Solver;
};
```

### FullBodyIKComponent.cpp

```cpp
#include "FullBodyIKComponent.h"

UFullBodyIKComponent::UFullBodyIKComponent()
{
    PrimaryComponentTick.bCanEverTick = true;
}

void UFullBodyIKComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

    // 检查是否有链路数据
    if (LinkData.Num() == 0 || EffectorTargets.Num() == 0) return;

    // 将 SolverInput 转换为 FSolverParameter
    FSolverParameter SolverParam;
    SolverParam.MaxIterations = SolverInput.MaxIterations;
    SolverParam.Tolerance = SolverInput.Precision;
    SolverParam.Damping = SolverInput.Damping;
    SolverParam.UseJacobianTranspose = SolverInput.bUseJacobianTranspose;
    // 注意：FSolverInput 中的 LinearMotionStrength / AngularMotionStrength 在 EffectorTarget 中设置

    TArray<FJacobianDebugData> DebugData;
    bool bSolved = Solver.SolveJacobianIK(
        LinkData,
        EffectorTargets,
        SolverParam,
        SolverParam.MaxIterations,
        SolverParam.Tolerance,
        &DebugData
    );

    // 求解后，LinkData 中的变换已更新，可用于驱动骨骼
    // 示例：将结果应用到某种动画或物理驱动
}
```

## 模块依赖

### FullBodyIK 模块

| 模块 | 用途 |
|---|---|
| `ControlRig` | 提供 RigVM 执行环境和单位节点（运行时必需） |
| `RigVM` | 底层虚拟机（由 ControlRig 间接依赖） |
| `Eigen`（内联） | 矩阵运算库（无需额外链接） |

### PBIK 模块

| 模块 | 用途 |
|---|---|
| `ControlRigDeveloper` | 编辑器开发工具 |
| `ControlRigEditor` | 编辑器集成（如节点图 UI） |
| `Engine` | 标准引擎 |
| `AssetTools` | 资产工具 |
| `UnrealEd` | 编辑器基础设施 |
| `RigVMDeveloper` | RigVM 开发助手 |
| `RigVMEditor` | RigVM 编辑器功能 |

> **注意**：使用本插件的 C++ API 时，只需依赖 `FullBodyIK` 和 `PBIK` 模块，引擎会自动处理间接依赖。如果仅在蓝图中使用 ControlRig 节点，无需任何额外模块依赖。

## 维护状态

### 近期更新

- 2025-11-18 e6c40773 — [FBIK] Fixed crash bug from intermediate effectors on fork joints.  
- 2025-09-24 2190b05c — [Backout] - CL46141850  
- 2025-09-24 61d61d54 — [FBIK] Removed broken old debug drawing from FBIK rig unit.  
- 2025-07-29 3057849d — [FBIK] Fixed issue with non-normalized rotations exploding the solve.  
- 2025-07-29 9bfb5815 — Fullbody IK: Fix non-normalized rotation coming from solver  

### 维护评价

该插件自 2025 年 7 月创建以来，持续收到 bug 修复和优化更新。最近一次更新（2025-11-18）修复了分支关节中间效应器的崩溃，表明活跃维护。虽然仍标记为实验性（路径为 Experimental），但官方已在内建 ControlRig 中集成该功能。**推荐使用**，但注意：

- 它不提供高级 UI 调试工具（2025-09-24 移除了旧的调试绘制）。
- 对于简单 IK 任务（如单链手臂），建议仍使用 TwoBoneIK 或 CCD 节点以节省性能。
- 求解器依赖 Eigen 库，首次编译可能稍慢。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/FullBodyIK)
- [ControlRig 官方文档](https://docs.unrealengine.com/5.7/en-US/control-rig-in-unreal-engine/)（通用，无专为此插件编写文档）
- 测试用例：`Engine/Plugins/Experimental/FullBodyIK/Tests/`（未收录，可参考插件内 Test 目录）