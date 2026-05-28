# IK Rig

> 

| 属性 | 值 |
|---|---|
| 中文名 | IK绑骨插件 |
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（编辑器图标、Slate资源） |
| 模块 | `IKRig` (Runtime), `IKRigDeveloper` (Runtime), `IKRigEditor` (Editor), `IKRigUAF` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-11-25 |
| 年龄标签 | 🆕（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/IKRig) | |

## 用途

IKRig 插件是 UE5 中用于**IK 绑定（IK Rig）和动画重定向（Animation Retargeting）**的核心动画系统。它解决两个关键问题：

1. **IK Rig 定义与运行**：允许用户在任意骨骼网格体上定义 IK 目标（Goals）、骨骼链（Chains）和 IK 求解器栈（Solver Stack，如 FullBodyIK、LimbIK、PoleVector 等），然后在运行时通过 `FAnimNode_IKRig` 节点驱动角色姿态。

2. **动画重定向**：将一个骨骼网格体的动画数据无损地转移到另一个骨骼比例完全不同的网格体上。这是通过 `UIKRetargeter` 资产完成的，它定义了源/目标 IK Rig、链映射、重定向姿态（Retarget Pose）以及一个可扩展的操作栈（Op Stack），支持 FK/IK 链重定向、步幅变形（Stride Warp）、速度植根（Speed Planting）、极向量（Pole Vector）、地板约束、混合到源骨骼等多种后处理操作。

该插件比传统 UE4 的重定向系统（基于骨骼名称匹配）更强大：它能处理骨骼层级完全不同、比例差异巨大的角色之间的动画迁移，并支持批量导出。

## 使用场景

- 你有一个写实人类角色和一个卡通比例角色，需要共享同一套动画库 → 使用 **IK Retargeter** 批量重定向动画
- 你需要为角色的手部/脚部添加程序化 IK 效果（如脚部贴地、手部抓握） → 使用 **IK Rig** 定义 Goals 和 Solver Stack
- 你正在从 Mixamo 或其他动画库导入动画，需要应用到自定义骨骼的角色上 → 使用 **Batch Retarget** 窗口一键完成
- 你需要构建一个支持多种角色骨架共用动画的游戏（如 RPG 中的多体型角色） → 使用 IK Retargeter 配合 Override Sets 为不同角色微调设置
- 你的角色有蜘蛛/四足等非标准骨架，需要重定向人形动画 → 使用 IK Retargeter（支持非标准骨架命名约定）

## 蓝图用法

IKRig 插件提供了丰富的蓝图 API，通过两个核心控制器（Controller）类暴露功能。

### 核心节点

#### IK Rig 控制器（UIKRigController）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get IK Rig Controller` | 获取指定 IK Rig 资产的控制器 | `UIKRigController` |
| `Set IK Rig Skeletal Mesh` | 设置 IK Rig 使用的骨骼网格体 | `UIKRigController` |
| `Add Solver` | 向求解器栈添加新的 IK 求解器（如 FullBodyIK、LimbIK） | `UIKRigController` |
| `Remove Solver` | 从求解器栈移除指定求解器 | `UIKRigController` |
| `Move Solver In Stack` | 在求解器栈中移动求解器顺序 | `UIKRigController` |
| `Set Solver Enabled` | 启用/禁用求解器 | `UIKRigController` |
| `Add New Goal` | 创建新的 IK 目标（绑定到骨骼） | `UIKRigController` |
| `Remove Goal` | 删除 IK 目标 | `UIKRigController` |
| `Connect Goal To Solver` | 将 Goal 连接到求解器 | `UIKRigController` |
| `Disconnect Goal From Solver` | 从求解器断开 Goal | `UIKRigController` |
| `Set Bone Excluded` | 排除/包含骨骼参与求解 | `UIKRigController` |
| `Add Retarget Chain` | 添加重定向链 | `UIKRigController` |
| `Set Retarget Chain Start Bone` | 设置重定向链的起始骨骼 | `UIKRigController` |
| `Set Retarget Chain End Bone` | 设置重定向链的结束骨骼 | `UIKRigController` |

#### IK Retargeter 控制器（UIKRetargeterController）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get IK Retarget Controller` | 获取指定 IK Retargeter 资产的控制器 | `UIKRetargeterController` |
| `Set IK Rig` | 设置源/目标 IK Rig | `UIKRetargeterController` |
| `Get IK Rig` | 获取源/目标 IK Rig | `UIKRetargeterController` |
| `Set Preview Mesh` | 设置预览网格体 | `UIKRetargeterController` |
| `Add Retarget Op` | 向操作栈添加重定向操作 | `UIKRetargeterController` |
| `Remove Retarget Op` | 从操作栈移除操作 | `UIKRetargeterController` |
| `Remove All Ops` | 清空操作栈 | `UIKRetargeterController` |
| `Add Default Ops` | 自动添加基础重定向操作组合 | `UIKRetargeterController` |
| `Set Retarget Op Enabled` | 启用/禁用操作 | `UIKRetargeterController` |
| `Auto Map Chains` | 自动映射源/目标骨骼链 | `UIKRetargeterController` |
| `Set Source Chain` | 手动映射源链到目标链 | `UIKRetargeterController` |
| `Create Retarget Pose` | 创建新的重定向姿态 | `UIKRetargeterController` |
| `Remove Retarget Pose` | 删除重定向姿态 | `UIKRetargeterController` |
| `Set Current Retarget Pose` | 设置当前使用的重定向姿态 | `UIKRetargeterController` |
| `Set Rotation Offset For Retarget Pose Bone` | 设置骨骼旋转偏移 | `UIKRetargeterController` |
| `Set Root Offset In Retarget Pose` | 设置根骨骼位移偏移 | `UIKRetargeterController` |
| `Auto Align All Bones` | 自动对齐所有骨骼 | `UIKRetargeterController` |
| `Add New Retarget Override Set` | 添加覆盖集 | `UIKRetargeterController` |

#### 批量重定向（UIKRetargetBatchOperation）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Run Batch Retarget` | 批量重定向动画资产（传入 FIKRetargetBatchOperationInputs 结构体） | `UIKRetargetBatchOperation` |

### 使用示例（蓝图描述）

**场景：在蓝图中批量重定向动画**

1. 创建一个 `FIKRetargetBatchOperationInputs` 结构体变量
2. 填充 `SourceMesh`（源骨骼网格体）、`TargetMesh`（目标骨骼网格体）、`IKRetargetAsset`（IK Retargeter 资产）
3. 将要重定向的动画序列添加到 `AssetsToRetarget` 数组
4. 设置 `Prefix`、`Suffix`、`TargetPath` 等命名规则
5. 调用 `Run Batch Retarget` 节点，传入该结构体
6. 返回值为新创建的动画资产列表

**场景：在蓝图中动态修改 IK Rig**

1. 通过 `Get IK Rig Controller` 节点获取控制器
2. 使用 `Add Solver` 添加 FullBodyIK 求解器
3. 使用 `Add New Goal` 为手脚骨骼创建 IK 目标
4. 使用 `Connect Goal To Solver` 将 Goal 连接到求解器
5. 使用 `Get Solver Controller` 获取求解器控制器以进一步调整参数

## C++ 用法

### 头文件引入

```cpp
// IK Rig 定义和控制
#include "Rig/IKRigDefinition.h"
#include "RigEditor/IKRigController.h"

// IK Retargeter 控制
#include "Retargeter/IKRetargeter.h"
#include "RetargetEditor/IKRetargeterController.h"

// 批量重定向
#include "RetargetEditor/IKRetargetBatchOperation.h"

// 动画节点
#include "AnimNodes/AnimNode_IKRig.h"
#include "Retargeter/AnimNode_RetargetPoseFromMesh.h"
```

### 基本用法：通过代码创建和修改 IK Rig

以下示例展示了如何通过 `UIKRigController` API 创建一个完整的 IK Rig 设置。

```cpp
// 来源：UIKRigController API 以及 UIKRigDefinitionFactory

// 1. 创建新的 IK Rig 资产
UIKRigDefinition* NewRig = UIKRigDefinitionFactory::CreateNewIKRigAsset(
    TEXT("/Game/MyIKRigs/"), TEXT("IK_MyCharacter"));

// 2. 获取控制器
UIKRigController* Controller = UIKRigController::GetController(NewRig);

// 3. 设置骨骼网格体（这会加载骨骼层级到 IK Rig 的内部骨架）
Controller->SetSkeletalMesh(MySkeletalMesh);

// 4. 添加 FullBodyIK 求解器
int32 SolverIndex = Controller->AddSolver(TEXT("/Script/IKRig.FullBodyIKSolver"));

// 5. 创建 IK 目标
FName LeftHandGoal = Controller->AddNewGoal(TEXT("LeftHandGoal"), TEXT("hand_l"));
FName RightHandGoal = Controller->AddNewGoal(TEXT("RightHandGoal"), TEXT("hand_r"));
FName LeftFootGoal = Controller->AddNewGoal(TEXT("LeftFootGoal"), TEXT("foot_l"));
FName RightFootGoal = Controller->AddNewGoal(TEXT("RightFootGoal"), TEXT("foot_r"));

// 6. 将 Goal 连接到求解器
Controller->ConnectGoalToSolver(LeftHandGoal, SolverIndex);
Controller->ConnectGoalToSolver(RightHandGoal, SolverIndex);
Controller->ConnectGoalToSolver(LeftFootGoal, SolverIndex);
Controller->ConnectGoalToSolver(RightFootGoal, SolverIndex);

// 7. 添加重定向链（用于动画重定向场景）
Controller->AddRetargetChain(TEXT("Spine"), TEXT("pelvis"), TEXT("spine_03"), NAME_None);
Controller->AddRetargetChain(TEXT("LeftArm"), TEXT("clavicle_l"), TEXT("hand_l"), LeftHandGoal);
Controller->AddRetargetChain(TEXT("RightArm"), TEXT("clavicle_r"), TEXT("hand_r"), RightHandGoal);
Controller->AddRetargetChain(TEXT("LeftLeg"), TEXT("thigh_l"), TEXT("foot_l"), LeftFootGoal);
Controller->AddRetargetChain(TEXT("RightLeg"), TEXT("thigh_r"), TEXT("foot_r"), RightFootGoal);

// 8. 通知需要重新初始化
Controller->BroadcastNeedsReinitialized();
```

### 进阶用法：配置 IK Retargeter 进行动画重定向

```cpp
// 来源：UIKRetargeterController API

// 1. 获取 Retargeter 控制器
UIKRetargeterController* RetargetController = UIKRetargeterController::GetController(MyRetargeterAsset);

// 2. 设置源和目标 IK Rig
RetargetController->SetIKRig(ERetargetSourceOrTarget::Source, SourceIKRig);
RetargetController->SetIKRig(ERetargetSourceOrTarget::Target, TargetIKRig);

// 3. 设置预览网格体
RetargetController->SetPreviewMesh(ERetargetSourceOrTarget::Source, SourceMesh);
RetargetController->SetPreviewMesh(ERetargetSourceOrTarget::Target, TargetMesh);

// 4. 添加默认操作栈（Pelvis Motion, FK Chains, IK Chains, IK Solve, Root Motion）
RetargetController->AddDefaultOps();

// 5. 自动映射骨骼链（使用模糊匹配）
RetargetController->AutoMapChains(EAutoMapChainType::Fuzzy, true);

// 6. 手动调整特定链的映射
RetargetController->SetSourceChain(TEXT("LeftArm"), TEXT("LeftArm"));

// 7. 创建自定义重定向姿态
FName PoseName = RetargetController->CreateRetargetPose(TEXT("CustomPose"), ERetargetSourceOrTarget::Target);

// 8. 设置骨骼旋转偏移
RetargetController->SetRotationOffsetForRetargetPoseBone(
    TEXT("spine_01"),
    FQuat(FVector::UpVector, FMath::DegreesToRadians(15.0f)),
    ERetargetSourceOrTarget::Target);

// 9. 设置根骨骼偏移（解决身高差异）
RetargetController->SetRootOffsetInRetargetPose(
    FVector(0, 0, 10.0f), ERetargetSourceOrTarget::Target);

// 10. 自动对齐所有骨骼
RetargetController->AutoAlignAllBones(ERetargetSourceOrTarget::Target);

// 11. 创建覆盖集（Override Set），用于针对特定目标覆盖参数
FName OverrideSetName = RetargetController->AddNewRetargetOverrideSet(TEXT("LargeCharacter"));
```

### 进阶用法：通过代码执行批量重定向

```cpp
// 来源：UIKRetargetBatchOperation 和 FIKRetargetBatchOperationInputs

FIKRetargetBatchOperationInputs Inputs;
Inputs.AssetsToRetarget = SelectedAnimAssets;  // TArray<FAssetData>
Inputs.SourceMesh = SourceSkeletalMesh;
Inputs.TargetMesh = TargetSkeletalMesh;
Inputs.IKRetargetAsset = MyRetargeter;
Inputs.Search = TEXT("");
Inputs.Replace = TEXT("");
Inputs.Suffix = TEXT("_Retargeted");
Inputs.TargetPath = TEXT("/Game/Animations/Retargeted/");
Inputs.bUseSourcePath = false;
Inputs.bIncludeReferencedAssets = true;
Inputs.bOverwriteExistingFiles = false;
Inputs.bRetainAdditiveFlags = true;

TArray<FAssetData> NewAssets = UIKRetargetBatchOperation::RunBatchRetarget(Inputs);

for (const FAssetData& NewAsset : NewAssets)
{
    UE_LOG(LogTemp, Log, TEXT("Created retargeted asset: %s"), *NewAsset.GetSoftObjectPath().ToString());
}
```

## Demo 示例

以下是一个完整的最小 C++ 示例，展示如何在 AnimInstance 中使用 IKRig 动画节点。

### MyAnimInstance.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Animation/AnimInstance.h"
#include "MyAnimInstance.generated.h"

class UIKRigDefinition;

UCLASS()
class UMyAnimInstance : public UAnimInstance
{
    GENERATED_BODY()

public:
    // 在蓝图编辑器中指定 IK Rig 资产
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "IK Rig")
    TObjectPtr<UIKRigDefinition> IKRigAsset;

    // 可选：设置要应用 IK 的目标 Goal 名称
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "IK Rig")
    FName LeftHandGoalName = TEXT("LeftHandGoal");

    // 左手 Goal 的目标位置（世界空间）
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "IK Rig")
    FVector LeftHandTargetLocation;

    // 左手 Goal 的目标旋转
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "IK Rig")
    FRotator LeftHandTargetRotation;
};
```

### MyAnimInstance.cpp

```cpp
#include "MyAnimInstance.h"
// 引入 IK Rig 处理器头文件（如需在 C++ 中直接操控 Processor）
// #include "Rig/IKRigProcessor.h"
```

### 说明

在实际使用中，IKRig 通常通过 **动画蓝图（Anim Blueprint）** 中的 `IKRig` 节点来驱动。操作流程：

1. 在编辑器中创建 `IKRigDefinition` 资产（右键 → Animation → IK Rig）
2. 在 IK Rig 编辑器中设置骨骼网格体、添加 Goals、配置 Solver Stack 和重定向链
3. 在动画蓝图中添加 `IKRig` 节点，指定 IKRigDefinition 资产
4. 通过 `Set SkeletalMeshComponent` 输入连接目标网格体组件
5. 在运行时通过蓝图或代码设置 Goal 的目标位置/旋转

## 模块依赖

IKRig 插件的模块依赖情况：

| 模块 | 用途 |
|---|---|
| `ControlRig` | IK Rig 的求解器实现依赖 ControlRig 框架 |
| `FullBodyIK` | 提供 FullBodyIK 求解器（IKRig 的核心求解器之一） |

**注意**：IKRig 同时也是 ControlRig 生态系统的一部分。如果你只使用重定向功能（IK Retargeter）而不需要自定义 IK 求解器，则不需要直接依赖 FullBodyIK。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `d96c8edf` | Fix root motion trajectory visualization in IK Retarget editor | 修复 IK 重定向编辑器中根运动轨迹可视化问题 |
| 2026-05-12 | `b9da6b61` | [IK Retargeter] Fix curve-bound override values having no effect on exported batch retarget animation | 修复曲线绑定覆盖值对批量重定向导出动画无效的问题 |
| 2026-05-12 | `553f4a7e` | [IK Retargeter] Fix pre-5.6 RTG assets having all ops enabled in 5.8: narrow PostLoad version guard | 修复 5.6 之前的重定向资产在 5.8 中所有操作被默认启用的问题 |
| 2026-05-12 | `0171c6fd` | [IK Retargeter] Fix null deref crashes in GenerateAssetLists: guard GC'd weak ptrs, uncompiled bluep | 修复 GenerateAssetLists 中因弱指针被 GC 和未编译蓝图导致的空指针崩溃 |
| 2026-05-12 | `f8c7fc88` | [IK Retargeter] Fix active-by-default Override Sets not applied when exporting animations through the batch window | 修复批量导出窗口中默认激活的覆盖集未被应用的问题 |

### 维护评价

IKRig 是 UE5 动画系统的核心组件，由 Epic Games 官方团队持续维护。

- **活跃维护**：最近 3 个月内持续有功能性更新和 bug 修复，最近的 commit 集中在 2026 年 5 月，修复了重定向器的多个关键问题（曲线覆盖、版本兼容性、空指针崩溃、批量导出覆盖集应用等）
- **重要性极高**：作为 UE5 官方动画重定向和 IK 系统的基础设施，广泛用于所有使用 Unreal Engine 的项目
- **持续演进**：插件从 2020 年 UE5 Early Access 发展至今，经历了大量重构和功能增强（如 Op Stack 架构、Override Sets、变量系统等），代码规模从初始版本增长到 243 个源文件
- **⚠️ 已知注意事项**：插件依赖 ControlRig 和 FullBodyIK 模块，版本间升级时需注意 PostLoad 兼容性（如最近修复的 5.6→5.8 迁移问题）

**推荐使用**：任何需要动画重定向或程序化 IK 的 UE5 项目都应使用此插件。它是 Epic 官方推荐的方案，取代了 UE4 时代的传统重定向系统。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/IKRig)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/ik-rig-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/IKRig/Source/IKRigDeveloper) (IKRigDeveloper 模块包含开发者/测试相关代码)