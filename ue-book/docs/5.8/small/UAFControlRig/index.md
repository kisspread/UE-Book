# UAF Control Rig

> Control Rig integration for UAF.（照抄，不翻译）

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

UAF（Unreal Animation Framework）是UE的动画框架，Control Rig是程序化动画控制系统。此插件的核心目的是**在 UAF 动画流程中集成 Control Rig 的功能**。它并非一个独立的动画解决方案，而是一个“桥梁”或“适配器”，旨在让使用 UAF 管线的项目能够利用 Control Rig 进行动画驱动、IK 解算、动画重定向或创建复杂的程序化动画混合。本质上，它扩展了 UAF 的动画能力边界。

## 使用场景

-   **场景一**：你的角色动画系统基于 UAF 框架构建，但需要根据程序逻辑（如地形适应、目标追踪）实时调整骨骼姿态。此插件允许你在 UAF 的动画图中无缝插入 Control Rig 单元，实现程序化动画控制。
-   **场景二**：你希望使用 UAF 管理动画状态机和蒙太奇，但需要利用 Control Rig 的强大功能（如全身 IK、物理模拟）来处理最终的输出姿态或进行动画重定向。

## 蓝图用法

作为运行时集成模块，其蓝图接口主要面向动画图表（Anim Graph）和运行时控制。

### 核心节点

*由于插件为实验性且聚焦于底层集成，直接暴露的独立蓝图节点可能有限。其主要作用体现在动画蓝图的图表编辑器中。*

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Run Control Rig` | 在 UAF 动画流程中运行一个 Control Rig 实例。 | `UControlRigAnimNode` |
| `设置 Control Rig 输入` | 将 UAF 动画数据（如变换、速度）传递给 Control Rig。 | （通过属性访问） |

### 使用示例（蓝图描述）

1.  在角色的 **动画蓝图（Animation Blueprint）** 中，编辑动画图表。
2.  从右键菜单添加一个 **“Run Control Rig”** 节点。
3.  为该节点指定一个 **Control Rig 蓝图资产**（已在 Control Rig 编辑器中创建）。
4.  将此节点连接到动画状态机输出或本地空间姿势节点之后，最终输出经过 Control Rig 处理后的姿势。
5.  通过 **“设置 Control Rig 输入”** 节点或蓝图中的属性引用，将 UAF 提供的动画数据（如根骨骼速度、视锥角等）传递给 Control Rig，以驱动其内部的控制器。

## C++ 用法

此插件的 C++ 用法侧重于扩展 UAF 的动画节点系统和运行时环境。

### 头文件引入

```cpp
#include "UAFControlRig.h"
```

### 基本用法

集成 Control Rig 到自定义的 UAF 动画节点或蓝图函数库中。
```cpp
// 来源：自定义动画节点示例
#include "UAFControlRig.h"
#include "AnimNode_UAFControlRig.h" // 假设此为插件定义的动画节点

class FAnimNode_MyCustomNode : public FAnimNode_Base
{
    // ... 其他成员 ...
    
    // 引用一个 Control Rig 实例
    UPROPERTY(EditAnywhere, Category = "Settings")
    TSubclassOf<UControlRig> ControlRigClass;

    // 在节点初始化时，可能需要与 UAF 系统交互并设置 Control Rig
    virtual void Initialize_AnyThread(const FAnimationInitializeContext& Context) override;

    // 在 Evaluate 中驱动 Control Rig
    virtual void Evaluate_AnyThread(FPoseContext& Output) override;
};
```

### 进阶用法

结合 UAF 的系统服务和 Control Rig 的宿主能力，实现更复杂的动画逻辑。
```cpp
// 来源：运行时服务或组件
#include "UAFControlRig.h"
#include "ControlRig.h"
#include "UAFAnimationService.h" // 假设存在此服务

class UMyAnimationComponent : public UActorComponent
{
    // ... 其他成员 ...

    void UpdateAnimation(float DeltaTime)
    {
        // 1. 从 UAF 服务获取当前动画状态或目标
        FAnimStateData StateData = UAFAnimationService::GetStateData(GetOwner());
        
        // 2. 准备 Control Rig 输入
        FControlRigExecuteContext RigContext;
        RigContext.SetVariableValue(FName("TargetLocation"), StateData.TargetLocation);
        
        // 3. 运行 Control Rig 并获取结果
        if (ControlRigInstance)
        {
            ControlRigInstance->Execute(RigContext);
            FTransform FinalRootTransform = ControlRigInstance->GetHierarchy()->GetGlobalTransform(FName("Root"));
            // 4. 将结果应用回 UAF 动画流程或直接应用到骨骼网格体
        }
    }
};
```

## Demo 示例

一个最小集成示例，展示如何在 UAF 动画蓝图中设置一个简单的 Control Rig 进行头部 IK。

```cpp
// MyHeadIKAnimNode.h
#pragma once
#include "UAFControlRig.h"
#include "Animation/AnimNodeBase.h"

USTRUCT(BlueprintInternalUseOnly)
struct FAnimNode_MyHeadIK : public FAnimNode_Base
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, Category = "IK Settings")
    FBoneReference HeadBone;

    UPROPERTY(EditAnywhere, Category = "IK Settings")
    TSubclassOf<UControlRig> HeadIKControlRigClass;

    UPROPERTY()
    UControlRig* ControlRigInstance;

    virtual void Initialize_AnyThread(const FAnimationInitializeContext& Context) override;
    virtual void CacheBones_AnyThread(const FAnimationCacheBonesContext& Context) override;
    virtual void Evaluate_AnyThread(FPoseContext& Output) override;
};
```

```cpp
// MyHeadIKAnimNode.cpp
#include "MyHeadIKAnimNode.h"
#include "ControlRig.h"
#include "UAFControlRig.h"

void FAnimNode_MyHeadIK::Initialize_AnyThread(const FAnimationInitializeContext& Context)
{
    FAnimNode_Base::Initialize_AnyThread(Context);
    
    // 初始化并创建 Control Rig 实例
    if (HeadIKControlRigClass)
    {
        ControlRigInstance = NewObject<UControlRig>(Context.AnimInstance, HeadIKControlRigClass);
        if (ControlRigInstance)
        {
            // 这里可能调用 UAFControlRig 模块提供的辅助函数进行绑定
            // UAFControlRigModule::InitializeControlRigForNode(ControlRigInstance, Context);
            ControlRigInstance->Initialize();
        }
    }
}

void FAnimNode_MyHeadIK::Evaluate_AnyThread(FPoseContext& Output)
{
    // 获取输入姿势
    FPoseContext LocalPoseContext(Output);
    // ... 评估输入链接 ...

    if (ControlRigInstance && HeadBone.BoneIndex != INDEX_NONE)
    {
        // 将当前头部骨骼位置设置为 Control Rig 的输入变量
        FTransform HeadTransform = Output.Pose[HeadBone.BoneIndex];
        ControlRigInstance->SetVariableValue(FName("CurrentHeadLocation"), HeadTransform.GetLocation());
        
        // 执行 Control Rig
        ControlRigInstance->Execute();
        
        // 从 Control Rig 获取解算结果并应用到输出姿势
        FVector AdjustedHeadLocation = ControlRigInstance->GetVariableValue<FVector>(FName("AdjustedHeadLocation"));
        Output.Pose[HeadBone.BoneIndex].SetLocation(AdjustedHeadLocation);
    }
    else
    {
        Output = LocalPoseContext;
    }
}
```

## 模块依赖

从插件性质和 Build.cs 推断，使用者的模块需要依赖以下内容：

| 模块 | 用途 |
|---|---|
| `ControlRig` | 核心依赖，提供 Control Rig 运行时和编辑器框架。 |
| `AnimationCore` | 提供基础的动画数学和骨骼操作功能。 |
| `AnimGraphRuntime` | 提供动画图运行时基础，用于创建自定义动画节点。 |
| `UAF` | 提供 UAF 框架的核心接口和服务（此依赖可能为隐式或通过接口依赖）。 |

*注意：由于插件处于实验阶段，具体的公共依赖可能随版本变化。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 统一日志系统，迁移到新的日志宏格式。 |
| 2026-03-03 | `fb006c07` | Control Rig: Fix ControlRigTrait not finding newer BP-independent rigs | 修复了一个关键缺陷，使得 ControlRigTrait 能正确发现新版独立于蓝图的 Control Rig 资产。 |
| 2026-03-03 | `3757a39a` | [Backout] - CL51376416 | 回退了之前的某次提交。 |
| 2026-03-03 | `fc9640e7` | Control Rig: Fix ControlRigTrait not finding newer BP-independent rigs | 同 `fb006c07`，是修复同一问题的另一个提交。 |
| 2026-02-27 | `6f697f67` | Allow system and graph factory initializer callbacks to add custom variable references | 扩展了系统和图表工厂的初始化回调功能，允许添加自定义变量引用。 |

### 维护评价

UAFControlRig 是一个**非常新且处于活跃开发阶段的实验性插件**。创建时间不足一年，但近期（2026年2-4月）有连续的实质性更新，包括重要的 Bug 修复和功能扩展。日志系统的迁移也表明它跟随引擎整体的技术演进。

-   **优点**：处于活跃开发中，能及时修复问题并扩展功能。
-   **风险**：作为 `Experimental` 插件，其 API 和功能集可能在未来版本中发生**不兼容的变更**甚至被移除。
-   **建议**：适用于希望在其 UAF 动画管线中集成 Control Rig 并愿意承担实验性风险的高级开发者或项目进行技术预研。**不建议在对稳定性要求高的商业项目中作为核心依赖使用**。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFControlRig)
-   （无官方文档链接）
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFControlRig/Tests)