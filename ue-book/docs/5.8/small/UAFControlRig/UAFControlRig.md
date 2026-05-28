# UAF Control Rig

> Control Rig integration for UAF.

| 属性 | 值 |
|---|---|
| 中文名 | UAF控制绑定 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `UAFControlRig` (Runtime), `UAFControlRigEditor` (Runtime), `UAFControlRigTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFControlRig) | |

## 用途

本插件将 Unreal 的 **Control Rig** 程序化动画系统集成到 **UAF (Unreal Animation Framework)** 动画求值图中。它允许开发者在 UAF 的动画节点图（AnimNext Trait Graph）中直接使用 Control Rig 资产作为动画节点，从而在统一的动画流程中利用 Control Rig 强大的程序化动画能力（如 IK、物理模拟、程序化骨骼驱动等）来处理或增强动画输出。其核心是提供了一个 Trait（特征），能够接收上一个动画节点的输出（骨骼 Pose），将其作为输入传给 Control Rig 进行处理，然后输出处理后的新 Pose。

## 使用场景

- **在 UAF 动画管线中添加程序化动画**：当你的角色动画需要基于游戏逻辑（如瞄准、跳跃、受击）进行动态调整（如 IK 手部放置、程序化摆动），并且希望这些调整作为 UAF 动画图的一部分时。
- **使用现有 Control Rig 资产**：当你已经有为 Control Rig 编辑器创建的 Control Rig 蓝图资产，并希望将其作为模块化的动画处理单元复用到 UAF 系统中。
- **需要在 UAF 流程中利用 Control Rig 的调试绘制**：本插件支持将 Control Rig 的调试绘制指令输出到 UAF 的调试绘制系统中。

## 蓝图用法

该插件主要在 UAF 动画图编辑器中通过节点使用，本身不直接暴露新的蓝图节点给 Animation Blueprint。其功能通过 UAF 的 Trait 系统体现。开发者主要在编辑器中配置 Control Rig 节点的属性。

### 核心配置属性 (在 UAF 动画图节点的详情面板中)

| 属性 | 说明 | 所在类 |
|---|---|---|
| `ControlRigAssetReference` | 指定要使用的 Control Rig 资产。 | `FControlRigTraitSharedData_v2` |
| `bResetInputPoseToInitial` | 在求值前是否将 Control Rig 的 Pose 重置为其初始状态。 | `FControlRigTraitSharedDataBase` |
| `bTransferInputPose` | 是否将上游输入的骨骼 Pose 传递到 Control Rig 中。 | `FControlRigTraitSharedDataBase` |
| `bTransferInputCurves` | 是否将上游输入的动画曲线传递到 Control Rig 中。 | `FControlRigTraitSharedDataBase` |
| `bSetRefPoseFromSkeleton` | 是否从网格体组件获取初始变换，覆盖 Control Rig 的初始变换。 | `FControlRigTraitSharedDataBase` |
| `bTransferPoseInGlobalSpace` | 是否在全局空间传递 Pose（而非局部空间）。 | `FControlRigTraitSharedDataBase` |
| `EventQueue` | 配置在求值时发送给 Control Rig 的自定义事件队列。 | `FControlRigTraitSharedDataBase` |
| (自动生成的输入/输出Pin) | 插件会根据 Control Rig 资产中暴露的变量和控件，自动在 Trait 节点上创建对应的输入和输出 Pin。 | `TControlRigTraitBase` (Editor) |

### 使用示例（蓝图描述）

1.  在 UAF 动画图中，右键添加一个 “Control Rig” 或 “Control Rig (Legacy)” 节点。
2.  在节点的细节面板中，将你的 Control Rig 蓝图资产赋值给 “Control Rig Asset Reference” 属性。
3.  节点会自动获得一个 “Input” 输入引脚和一个 “Output” 输出引脚，用于连接动画流。
4.  根据 Control Rig 中定义的变量和控件，节点上会自动生成额外的输入/输出引脚。你可以将这些引脚连接到其他 UAF 节点的输出，或暴露为 Trait 的输入输出参数，从而在运行时传递数据（如 IK 目标位置）给 Control Rig。
5.  根据需要调整 `bResetInputPoseToInitial` 等设置，控制 Control Rig 的求值行为。

## C++ 用法

### 头文件引入

```cpp
#include "UAFControlRig/Public/ControlRigTask.h"
#include "UAFControlRig/Internal/ControlRigTrait.h"
```

### 基本用法

该插件主要通过其 Trait 系统在动画图中使用。在 C++ 中，你可能需要获取动画任务的结果或进行调试。以下示例展示了如何检查一个 Control Rig 任务是否有效并获取其控件值（假设你有一个 `FAnimNextControlRigTask` 的实例）。

```cpp
// 假设你已经通过某种方式获得了一个 FAnimNextControlRigTask 实例 (TaskInstance)
const FAnimNextControlRigTask& ControlRigTask = ...; // 获取任务实例

// 1. 检查任务内部的 Control Rig 是否有效
UControlRig* Rig = ControlRigTask.GetControlRig();
if (Rig)
{
    UE_LOG(LogTemp, Log, TEXT("Control Rig: %s"), *Rig->GetName());
    
    // 2. 获取变量映射信息，查看哪些变量是被暴露和映射的
    const FControlRigVariableMappings& VarMappings = ControlRigTask.GetControlRigVariableMappings();
    // VarMappings 包含了输入输出映射信息，可用于调试或高级操作
    
    // 3. (高级) 通过 Control Rig 的公共 API 操作控件或变量
    // FRigControlElement* AimControl = Rig->FindControl(FName("Aim"));
    // if (AimControl) { ... }
}
else
{
    UE_LOG(LogTemp, Warning, TEXT("Control Rig task has no valid Control Rig instance."));
}
```

### 进阶用法

自定义 Control Rig 事件。可以在动画图节点的 `EventQueue` 属性中配置，也可以在 C++ 中动态触发。

```cpp
// 在运行时，通过 UAF 的动画实例或 Trait 绑定，向 Control Rig 发送事件
// 具体路径取决于你的 UAF 图设置。一种方式是修改 Trait 的共享数据。
// 假设你持有对 FControlRigTraitSharedData_v2 的引用 (SharedData)
FControlRigTraitSharedData_v2& SharedData = ...;

// 添加一个名为 "TriggerIK" 的事件
FControlRigEventName NewEvent;
NewEvent.EventName = FName("TriggerIK");
SharedData.EventQueue.Add(NewEvent);

// 注意：修改共享数据可能需要在特定的时机（如图重新初始化时）才能生效。
```

## Demo 示例

以下是一个简单的示例，展示如何在自定义的 UAF 动画模块中，通过代码检查或利用 Control Rig Trait 提供的功能。这不是一个独立的 Actor 示例，而是 UAF 系统内部使用方式的简化。

**ControlRigDemoTrait.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "AnimNext/AnimNextTrait.h"
#include "UAFControlRig/Internal/ControlRigTrait.h" // 引入 ControlRig Trait 的头文件

// 自定义一个 Trait，它内部使用 ControlRig Trait 的信息
struct FMyTrait : public UE::UAF::FBaseTrait
{
    GENERATED_BODY()
    
    ANIM_NEXT_IMPL_DECLARE_ANIM_TRAIT_BASIC(FMyTrait, FBaseTrait)
    
    virtual void PostEvaluate(UE::UAF::FEvaluateTraversalContext& Context, const UE::UAF::TTraitBinding<UE::UAF::IEvaluate>& Binding) const override
    {
        // 在求值后，尝试检查是否存在上游的 ControlRig Trait
        // 这只是一个逻辑示例，实际 Trait 链可能需要更严谨的查询方式
        if (const FControlRigTraitSharedData_v2* CRSharedData = Binding.GetSharedData<FControlRigTraitSharedData_v2>())
        {
            if (CRSharedData->HasValidControlRigReference())
            {
                UE_LOG(LogTemp, Log, TEXT("Found upstream Control Rig Trait using asset: %s"), *CRSharedData->ControlRigAssetReference.GetAssetPathName());
            }
        }
        // 继续其他 Trait 逻辑...
    }
};
```

**MyAnimInstance.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Animation/AnimInstance.h"
#include "MyAnimInstance.generated.h"

UCLASS()
class UMyAnimInstance : public UAnimInstance
{
    GENERATED_BODY()

    // 这里可以定义一些属性，用于向 UAF 图中的 ControlRig Trait 节点的自定义引脚传递数据
    UPROPERTY(BlueprintReadWrite, Category = "Animation")
    FVector IKTargetLocation;

    // 动画图的实例通常在 UAF 框架中管理，这里仅为结构示意
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ControlRig` | 核心依赖，提供 Control Rig 运行时、资产和控件系统。 |
| `AnimationCore` | 提供基础的动画数据结构（如骨骼引用、变换）。 |
| `AnimNext` | UAF 的核心模块，提供 Trait、任务、求值上下文等基础框架。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF。 |
| 2026-03-03 | `fb006c07` | Control Rig: Fix ControlRigTrait not finding newer BP-independent rigs | 修复 ControlRigTrait 无法找到较新的、不依赖蓝图的 Control Rig 资产的问题。 |
| 2026-03-03 | `3757a39a` | [Backout] - CL51376416 | 回退了 CL 51376416 的修改。 |
| 2026-03-03 | `fc9640e7` | Control Rig: Fix ControlRigTrait not finding newer BP-independent rigs | 同上，修复 Control Rig 资产查找问题。 |
| 2026-02-27 | `6f697f67` | Allow system and graph factory initializer callbacks to add custom variable references | 允许系统和图工厂初始化器回调添加自定义变量引用。 |

### 维护评价

**活跃维护中**。该插件自 2025 年 6 月创建以来，至 2026 年 4 月仍有持续的功能性更新和 Bug 修复（如修复资产查找问题、增强变量引用机制）。这表明它仍处于积极开发和迭代阶段。然而，它被标记为**实验性** (`IsExperimentalVersion: true`) 且**默认未启用**，这意味着其 API 和功能在未来版本中可能会发生重大变化，不建议在需要稳定性的生产项目中深度依赖。推荐用于研究、原型开发或对动画管线有高度定制需求的内部工具开发。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFControlRig)
- [官方文档]() (暂无)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFControlRig/Tests) (路径可能包含 UAFControlRigTests 模块)