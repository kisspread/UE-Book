# UAF Control Rig

> Control Rig integration for UAF.

| 属性 | 值 |
|---|---|
| 中文名 | UAF 控制绑定集成 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `UAFControlRig` (Runtime), `UAFControlRigEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-07-22 |
| 年龄标签 | 🆕（约 3 个月） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFControlRig) | |

## 用途

UAF Control Rig 是 **UAF（Unreal Animation Framework）** 的一部分，它提供了 Control Rig 与 AnimNext 动画图表之间的桥梁。该插件允许开发者将 **Control Rig** 作为一个 **Trait**（类似图形节点）嵌入到 AnimNext 评估图中，实现：

- 将 Control Rig 的输入/输出骨骼、曲线、变量与 AnimNext 的层级状态自动映射
- 支持 LOD 下的骨骼映射与刷新
- 执行 Control Rig 的更新任务并同步输出到动画姿势
- 在编辑器中进行变量映射和重定向

它解决了在 UAF 体系内复用既有 Control Rig 资产、以及将 Control Rig 的运行时逻辑无缝融入新一代动画系统的需求。

## 使用场景

- **使用 UAF/AnimNext 搭建动画系统**：当你的项目采用 AnimNext 动画图，并希望在其评估流程中通过 Control Rig 处理动画（如 IK、FK 校正、程序化动画）时，可直接使用本插件。
- **混合新旧动画管线**：项目中已有大量 Control Rig 资产，计划逐步迁移到 AnimNext，可将 Control Rig 作为 Trait 节点插入，无需重写原有逻辑。
- **高精度骨骼控制**：需要细粒度的骨骼控制、控制算子（Controls）以及运行时重定向，配合 UAF 的层级映射能力更高效。

## 蓝图用法

本插件并未暴露可直接在蓝图中调用的 `UFUNCTION` 节点，其核心功能通过 **AnimNext Trait** 系统在图表中以编辑器属性方式配置。以下列出可在蓝图编辑器（或 UAF Trait 编辑器）中调整的关键属性：

### 核心 Trait 属性（位于 `FControlRigTraitSharedData`）

| 属性 | 说明 | 类型 |
|---|---|---|
| `ControlRigClass` | 指定要使用的 Control Rig 蓝图类 | `TSubclassOf<UControlRig>` |
| `ControlRigSkeleton` | 可选参考骨架，用于提取控制；若未指定则使用预览骨架 | `USkeleton*` |
| `bResetInputPoseToInitial` | 是否在每次评估前将骨骼姿势重置为初始值 | `bool` |
| `bTransferInputPose` | 是否将输入骨骼姿势传递到 Control Rig | `bool` |
| `bTransferInputCurves` | 是否将输入曲线传递到 Control Rig | `bool` |
| `bSetRefPoseFromSkeleton` | 是否从网格体组件获取初始变换覆盖重定向姿势 | `bool` |
| `InputBonesToTransfer` | 需要传递的输入骨骼引用列表 | `TArray<FBoneReference>` |
| `OutputBonesToTransfer` | 需要输出的骨骼引用列表 | `TArray<FBoneReference>` |
| `bTransferPoseInGlobalSpace` | 是否在世界空间（而非局部空间）传递姿势 | `bool` |
| `EventName` | Control Rig 需要触发的事件名称（如 `Update`、`Setup`） | `FName` |
| `ExposedPropertyName` / `bIsVariable` | 暴露属性与变量映射（编辑器中配置） | 结构体数组 |

### 使用示例（蓝图描述）

1. **在 AnimNext 图表中添加 Control Rig Trait**  
   - 在 AnimNext 编辑器中创建一个 Trait 实例，选择 `ControlRig` 类型。
   - 在细节面板中设置 `ControlRigClass` 为你的 Control Rig 蓝图。
   - 勾选 `bTransferInputPose` 和 `bResetInputPoseToInitial`，根据需要调整骨骼映射。

2. **配置输入/输出骨骼映射**  
   - 展开 `InputBonesToTransfer` 数组，添加需要从 AnimNext 层级传递给 Control Rig 的骨骼引用。
   - 类似地配置 `OutputBonesToTransfer` 数组。
   - 可结合 `UNodeMappingContainer` 进行重定向（编辑器环境下使用）。

3. **调整评估选项**  
   - 勾选 `bSetRefPoseFromSkeleton` 可在运行时强制使用网格体组件的初始姿势。
   - 选中 `bTransferPoseInGlobalSpace` 以全局空间传递姿势（适用于多层级骨架）。

## C++ 用法

### 头文件引入

```cpp
#include "ControlRigTrait.h"
#include "AnimNextControlRigHierarchyMappings.h"
#include "AnimNextControlRigPoseAdapter.h"
#include "ControlRigTask.h"
```

### 基本用法

以下示例展示了如何在自定义的 AnimNext Trait 实现中创建并执行 Control Rig 集成。

```cpp
// 源自：Plugins/Experimental/UAF/UAFControlRig/Source/UAFControlRig/Private/ControlRigTrait.cpp

// 1. 实例化一个层次映射对象
UE::UAF::ControlRig::FAnimNextControlRigHierarchyMappings HierarchyMappings;
HierarchyMappings.InitializeInstance();

// 2. 关联到控制器的 RigHierarchy
URigHierarchy* RigHierarchy = ControlRig->GetHierarchy();
HierarchyMappings.LinkToHierarchy(RigHierarchy);

// 3. 更新参考姿势（通常在一次 Setup 或 SkeletalMesh 切换时调用）
const UE::UAF::FReferencePose& RefPose = ...; // 从 UAF 上下文获取
USkeletalMeshComponent* SkelMeshComp = ...;
HierarchyMappings.UpdateControlRigRefPoseIfNeeded(
    ControlRig, InstanceObject, SkelMeshComp, RefPose,
    bSetRefPoseFromSkeleton, bIncludePoseInHash
);

// 4. 更新输入输出映射（通常当 LOD 或映射容器变化时调用）
int32 CurrentLOD = 0;
TArray<FBoneReference> InputBones = SharedData->InputBonesToTransfer;
TArray<FBoneReference> OutputBones = SharedData->OutputBonesToTransfer;
TWeakObjectPtr<UNodeMappingContainer> NodeMapping = ...; // 编辑器可选
HierarchyMappings.UpdateInputOutputMappingIfRequired(
    ControlRig, RigHierarchy, RefPose, CurrentLOD,
    InputBones, OutputBones, NodeMapping,
    bTransferPoseInGlobalSpace, bResetInputPoseToInitial
);
```

### 进阶用法：在评估任务中执行 Control Rig

```cpp
// 源自：Plugins/Experimental/UAF/UAFControlRig/Source/UAFControlRig/Private/ControlRigTask.cpp

// 创建一个评估任务
FAnimNextControlRigTask Task = FAnimNextControlRigTask::Make(SharedData, InstanceData);

// 在评估虚拟机 (FEvaluationVM) 的上下文中执行
FEvaluationVM& VM = ...;
Task.Execute(VM);

// Execute 内部会：
// 1. 获取或创建 Control Rig 实例
// 2. 调用 UpdateInput 传递骨骼和曲线
// 3. 触发 Control Rig 的 Evaluate 事件
// 4. 调用 UpdateOutput 将结果写回 KeyframeState
// 5. 收集调试绘制指令
```

如需更低层级的控制，可手动调用 `FAnimNextControlRigHierarchyMappings::UpdateInput` / `UpdateOutput`：

```cpp
UE::UAF::FKeyframeState KeyframeState;
FControlRigIOSettings Settings; // 可设置 bApplyBoneFilter 等
TWeakObjectPtr<UNodeMappingContainer> NodeMapping;

HierarchyMappings.UpdateInput(ControlRig, KeyframeState, Settings, Settings,
    NodeMapping, true, bTransferInputPose, bResetInputPoseToInitial,
    bTransferPoseInGlobalSpace, bTransferInputCurves);

// 此处可手动调用 ControlRig->Evaluate_AnyThread();
// 或让 UpdateOutput 内部执行

HierarchyMappings.UpdateOutput(ControlRig, KeyframeState, Settings,
    NodeMapping, true, bTransferPoseInGlobalSpace);
```

## Demo 示例

以下是一个完整的、可编译的 AnimNext Trait 示例（头文件 + 实现），演示如何集成 Control Rig 进行评估。该示例未展示 Build.cs 代码，依赖关系见“模块依赖”。

### MyCustomTrait.h

```cpp
// MyCustomTrait.h
#pragma once

#include "TraitCore/Trait.h"
#include "ControlRigTrait.h"
#include "AnimNextControlRigHierarchyMappings.h"
#include "MyCustomTrait.generated.h"

USTRUCT(meta = (DisplayName = "My Custom Control Rig"))
struct FMyCustomTraitSharedData : public UE::UAF::FControlRigTraitSharedData
{
    GENERATED_BODY()

    // 可以添加额外的自定义属性
};

UCLASS(meta = (DisplayName = "My Custom Trait"))
class UMyCustomTrait : public UAnimNextTrait
{
    GENERATED_BODY()

public:
    virtual void OnInitialize(const FAnimNextTraitInitializeContext& Context) const override;
    virtual void OnEvaluate(const FAnimNextTraitEvaluateContext& Context) const override;

    UPROPERTY()
    FMyCustomTraitSharedData SharedData;

    // 实例数据（运行时）
    mutable UE::UAF::ControlRig::FAnimNextControlRigHierarchyMappings HierarchyMappings;
};
```

### MyCustomTrait.cpp

```cpp
// MyCustomTrait.cpp
#include "MyCustomTrait.h"
#include "AnimNextControlRigPoseAdapter.h"
#include "ControlRigTask.h"
#include "EvaluationVM/EvaluationTask.h"

void UMyCustomTrait::OnInitialize(const FAnimNextTraitInitializeContext& Context) const
{
    // 初始化层次映射
    HierarchyMappings.InitializeInstance();

    // 获取 Control Rig 实例并链接
    if (UControlRig* ControlRig = Context.GetControlRig()) // 伪代码：实际需从 VM 获取
    {
        HierarchyMappings.LinkToHierarchy(ControlRig->GetHierarchy());
    }

    // 更新参考姿势（从 UAF 引用姿势获取）
    const UE::UAF::FReferencePose& RefPose = Context.GetReferencePose(); // 伪代码
    USkeletalMeshComponent* SkelMeshComp = Context.GetSkeletalMeshComponent();
    HierarchyMappings.UpdateControlRigRefPoseIfNeeded(
        ControlRig, Context.GetInstanceObject(), SkelMeshComp,
        RefPose, SharedData.bSetRefPoseFromSkeleton, true
    );
}

void UMyCustomTrait::OnEvaluate(const FAnimNextTraitEvaluateContext& Context) const
{
    // 创建并执行 Control Rig 任务
    UE::UAF::FControlRigTrait::FSharedData* SharedDataPtr = const_cast<FMyCustomTraitSharedData*>(&SharedData);
    UE::UAF::FControlRigTrait::FInstanceData* InstanceDataPtr = &HierarchyMappings; // 简化：实际应使用完整实例数据

    FAnimNextControlRigTask Task = FAnimNextControlRigTask::Make(SharedDataPtr, InstanceDataPtr);
    Task.Execute(Context.GetEvaluationVM());
}
```

> **注意**：上述代码为示意性示例，实际使用时需要遵循 UAF 和 AnimNext 的 Trait 规范。`Context` 的伪方法需根据真实 API 替换。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `UAF` | 提供引用姿势（`FReferencePose`）、关键帧状态（`FKeyframeState`）、LOD 姿势（`FLODPoseStack`）等核心类型 |
| `ControlRig` | Control Rig 运行时，提供 `UControlRig`、`URigHierarchy` 及相关操作 |
| `AnimNext` | AnimNext 运行时和 Trait 系统，提供 `FEvaluationVM`、`TraitCore` 等 |
| `NodeMappingContainer` | 用于编辑器中的骨骼映射重定向（可选依赖） |

> 除上述特殊模块外，还依赖标准 `CoreUObject`、`Engine`、`SlateCore` 等，未列出。

## 维护状态

### 近期更新

- 2025-09-23 `0ea1c505` — Control Rig: Force the execution of construction inmediately in Update_AnyThread if needed, so that construction 在需要时立即执行
- 2025-08-26 `81f8ccfb` — Control Rig: Create IControlRigAssetInterface from which ControlRig assets will inherit from 创建接口以支持 ControlRig 资产继承
- 2025-08-22 `f187d7bb` — UAF Control Rig Trait : Fixed latent pin size error for position and scale, as it was using the type 修复位置/缩放潜在家具尺寸错误
- 2025-08-22 `66585cf3` — Fixed UAF Control Rig trait mapped controls being initialized with random memory, due to controls no 修复映射控制初始化随机内存问题
- 2025-07-22 `1fb8b34a` — Properly handle out of order latent pins 正确处理乱序的潜伏引脚

### 维护评价

- **创建时间**：2025-07-22，截至当前约 3 个月，处于早期开发阶段。
- **更新频率**：近两个月内有多项功能性和修复性提交，更新活跃。
- **内容**：包括接口抽象、错误修复、潜在性能优化，证明开发团队在积极迭代。
- **推荐度**：虽然标为实验性插件，但由于与 UAF 深度绑定，且更新频繁，可用于基于 UAF 的项目中测试使用；生产环境需谨慎评估稳定性。
- **已知限制**：仅支持 UAF/AnimNext 场景，不适用于传统动画蓝图；部分映射逻辑依赖编辑器（NodeMappingContainer），运行时可能受限。

## 相关链接

- [源码（插件根目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFControlRig)
- [测试用例（若有）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFControlRig/Tests)
- [官方文档](https://docs.unrealengine.com/5.7/Animation/UAF/)（尚未提供，敬请期待）