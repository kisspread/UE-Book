# Evaluation Notifies

> A system for animation notifies which have animation evaluation time code.

| 属性 | 值 |
|---|---|
| 中文名 | 评估通知 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `EvaluationNotifiesRuntime` (Runtime), `EvaluationNotifiesEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-11-23 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EvaluationNotifies) | |

## 用途

本插件提供了一个动画通知系统，其核心特点是通知的执行与动画求值（Evaluation）的时间点紧密同步。传统的动画通知（`UAnimNotify` / `UAnimNotifyState`）在动画蓝图或动画序列的更新阶段（`Tick`）触发，而本插件的通知则在动画求值阶段（`Evaluate`）执行。

这解决了在动画求值阶段需要执行关键逻辑（如调整根骨骼变换、应用IK）时，通知时序与动画状态不精确的问题。特别适用于以下场景：
1.  **运动扭曲（Motion Warping）**：需要根据动画求值出的精确根运动来计算目标位置。
2.  **动画同步**：在求值阶段精确地修改骨骼变换，以实现动画之间的无缝混合或适配。
3.  **AnimNext / UAF 管线**：插件集成了 Unreal Animation Framework (UAF) 的特性（Trait）系统，使其能无缝融入新的动画评估管线。

## 使用场景

-   你正在开发一个需要精确动画同步的动作游戏（如《荣耀战魂》式的战斗），并且使用了运动匹配（Motion Matching）或运动扭曲技术 → 可以用本插件的 `Alignment` 通知来精确地将角色对齐到目标位置或方向。
-   你需要在动画求值阶段（例如在 AnimGraph 的节点中）根据当前动画状态动态应用IK或地面适配 → 可以用 `AlignToGround` 或 `TwoBoneIK` 通知。
-   你正在迁移到或使用新的 UAF（Unreal Animation Framework）动画系统，并希望通知能在 Trait 评估流程中执行 → 本插件提供了 `FEvaluationNotifiesTrait` 来实现。

## 蓝图用法

本插件的核心用法是作为动画通知状态（`AnimNotifyState`）的基类，在动画资产编辑器中配置。

### 核心通知类

| 通知类 | 说明 | 主要用途 |
|---|---|---|
| `UNotifyState_AlignmentBase` | 对齐通知的基类 | 管理对齐的扭曲曲线、转向设置等通用参数。 |
| `UNotifyState_Alignment` | 继承自 `AlignmentBase`，具体对齐实现 | 需要根据一个**命名变换（Named Transform）** 将角色对齐到目标点（如交互点、攀爬点）。 |
| `UNotifyState_AlignToGround` | 继承自 `AlignmentBase`，地面适配 | 通过射线检测自动寻找地面目标高度，并可动态调整播放速率。 |
| `UNotifyState_TwoBoneIK` | 两骨骼IK通知 | 在通知期间应用IK，可配置效果器、关节目标等。 |

### 使用示例（蓝图描述）

1.  **配置对齐通知**：
    *   在 `AnimSequence` 的通知轨道上，添加一个 `Alignment` 类型的通知状态。
    *   在通知详情面板中，设置 `TransformName` 为你在动画图中定义的“命名变换”（例如，来自一个“目标点”变量）。
    *   调整 `TranslationWarpingCurve` 和 `RotationWarpingCurve` 来控制扭曲的时序和权重。
    *   启用 `bEnableSteering` 以确保角色在扭曲时面部朝向运动方向。

2.  **配置地面适配通知**：
    *   添加 `AlignToGround` 通知状态。
    *   配置 `TraceSettings`（如检测半径、起始/结束偏移）来定义射线检测参数。
    *   可选：连接 `PlaybackRateOutputVariableReference` 来根据地面距离动态控制动画播放速度。

## C++ 用法

### 头文件引入

```cpp
// 使用运行时核心通知功能
#include "EvaluationNotifies/AnimNode_EvaluationNotifies.h"
#include "EvaluationNotifies/AnimNotifyState_Alignment.h"
#include "EvaluationNotifies/AnimNotifyState_TwoBoneIK.h"

// 如果使用 UAF/Trait 系统
#include "AnimNext/EvaluationNotifiesTrait.h"
```

### 基本用法：继承并创建自定义评估通知

**1. 创建自定义通知实例（继承 `FEvaluationNotifyInstance`）**

```cpp
// MyGroundStabilizationNotifyInstance.h
#pragma once
#include "EvaluationNotifies/AnimNode_EvaluationNotifies.h"

USTRUCT()
struct FMyGroundStabilizationNotifyInstance : public FEvaluationNotifyInstance
{
    GENERATED_BODY()

    // 通知开始时调用
    virtual void Start(const UAnimSequenceBase* AnimationAsset) override;
    
    // 每帧在动画求值时调用
    virtual void Update(const UAnimSequenceBase* AnimationAsset, float CurrentTime, float DeltaTime, bool bIsMirrored, const UMirrorDataTable* MirrorDataTable,
        FTransform& RootBoneTransform, const TMap<FName, FTransform>& NamedTransforms, FComponentSpacePoseContext& Output, TArray<FBoneTransform>& OutBoneTransforms) override;
    
    // 通知结束时调用
    virtual void End() override;
    
    // 你的自定义数据
    float GroundTraceRadius = 50.f;
    FVector PreviousGroundOffset = FVector::ZeroVector;
};
```

**2. 创建对应的通知状态资产（继承 `UAnimNotifyState`）**

```cpp
// MyGroundStabilizationNotify.h
#pragma once
#include "Animation/AnimNotifies/AnimNotifyState.h"
#include "MyGroundStabilizationNotifyInstance.h"

UCLASS(BlueprintType, DisplayName = "MyGroundStabilization")
class UMyGroundStabilizationNotify : public UAnimNotifyState
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, Category = "Settings")
    float TraceRadius = 50.f;

    // 重写此方法以提供你的自定义实例
    virtual UScriptStruct* GetNotifyInstanceType() const override
    {
        return FMyGroundStabilizationNotifyInstance::StaticStruct();
    }
};
```

**3. 注册自定义通知处理器**

在游戏模块的 `StartupModule` 中注册你的自定义通知，使其能被系统识别。

```cpp
// MyGameModule.cpp
#include "MyGameModule.h"
#include "MyGroundStabilizationNotify.h"
#include "EvaluationNotifies/AnimNode_EvaluationNotifies.h"

void FMyGameModule::StartupModule()
{
    // 注册你的自定义评估通知处理器
    FAnimNode_EvaluationNotifies::RegisterEvaluationHandler(
        UMyGroundStabilizationNotify::StaticClass(),
        FMyGroundStabilizationNotifyInstance::StaticStruct()
    );
}

void FMyGameModule::ShutdownModule()
{
    // 在模块卸载时取消注册
    FAnimNode_EvaluationNotifies::UnregisterEvaluationHandler(
        UMyGroundStabilizationNotify::StaticClass()
    );
}
```

## Demo 示例

以下是一个最小示例，展示如何创建一个简单的“冻结根运动”评估通知，在通知期间停止角色的水平根运动。

**FreezeRootMotionNotifyInstance.h**
```cpp
#pragma once
#include "EvaluationNotifies/AnimNode_EvaluationNotifies.h"

USTRUCT()
struct FFreezeRootMotionNotifyInstance : public FEvaluationNotifyInstance
{
    GENERATED_BODY()

    virtual void Update(const UAnimSequenceBase* AnimationAsset, float CurrentTime, float DeltaTime, bool bIsMirrored, const UMirrorDataTable* MirrorDataTable,
        FTransform& RootBoneTransform, const TMap<FName, FTransform>& NamedTransforms, FComponentSpacePoseContext& Output, TArray<FBoneTransform>& OutBoneTransforms) override
    {
        // 仅保留垂直方向的根运动，冻结水平运动
        FVector NewTranslation = RootBoneTransform.GetTranslation();
        NewTranslation.X = 0.f;
        NewTranslation.Y = 0.f;
        RootBoneTransform.SetTranslation(NewTranslation);
        
        // 冻结旋转（可选）
        RootBoneTransform.SetRotation(FQuat::Identity);
        
        // 注意：直接修改 RootBoneTransform 会影响后续动画求值的根运动输出
        // 通常需要配合运动扭曲或根运动提取系统使用
    }
};
```

**FreezeRootMotionNotify.h**
```cpp
#pragma once
#include "Animation/AnimNotifies/AnimNotifyState.h"
#include "FreezeRootMotionNotifyInstance.h"

UCLASS(BlueprintType, DisplayName = "FreezeRootMotion")
class UFreezeRootMotionNotify : public UAnimNotifyState
{
    GENERATED_BODY()

public:
    virtual UScriptStruct* GetNotifyInstanceType() const override
    {
        return FFreezeRootMotionNotifyInstance::StaticStruct();
    }
};
```

**模块注册（在你的游戏模块 StartupModule 中）**
```cpp
#include "EvaluationNotifies/AnimNode_EvaluationNotifies.h"
#include "FreezeRootMotionNotify.h"

FAnimNode_EvaluationNotifies::RegisterEvaluationHandler(
    UFreezeRootMotionNotify::StaticClass(),
    FFreezeRootMotionNotifyInstance::StaticStruct()
);
```

## 模块依赖

要使用本插件，你的项目或模块需要依赖以下插件（在 `.uplugin` 或 `Build.cs` 中声明）。

| 模块/插件 | 用途 |
|---|---|
| `AnimationWarping` | 为对齐（Alignment）通知提供运动扭曲的底层功能。 |
| `UAF` (Unreal Animation Framework) | 评估通知 Trait (`FEvaluationNotifiesTrait`) 的运行基础。 |
| `UAFAnimGraph` | 将评估通知集成到 UAF 的动画图系统中。 |
| `RigVM` | UAF 动画系统的依赖，评估通知可能使用其虚拟机执行。 |

**无其他特殊依赖（仅标准 Core/Engine/Slate 等）**。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-24 | `42548e51` | Fix non-unity build: forward-declare UAnimationAsset in anim node headers | 修复非统一构建，前置声明头文件以解决编译问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF。 |
| 2026-04-10 | `8ce934ce` | MotionWarping - fix for FAlignmentNotifyInstance::GetWeight and URootMotionModifier_PrecomputedWarp: | 修复了运动扭曲中权重计算和预计算扭曲修改器的bug。 |
| 2026-02-09 | `1be7393a` | Gracefully handle notify dispatch failure when no animation sequence is playing | 当没有播放动画序列时，优雅地处理通知分发失败，避免崩溃。 |
| 2025-11-24 | `1e8772b6` | UAF: Timelines can now fail state & delta queries | UAF 时间线现在可以处理状态和增量查询失败的情况。 |

### 维护评价

-   **活跃维护**：该插件在最近6个月内持续有实质性更新，包括功能修复、兼容性改进和日志规范调整，表明它处于积极开发和维护中。
-   **实验性**：`.uplugin` 中标记为 `IsExperimentalVersion: true`，且默认禁用 (`EnabledByDefault: false`)。这意味着其API和行为在未来版本中可能发生重大变更。
-   **推荐使用**：如果你的项目正在使用或计划使用 **运动扭曲** 或 **新的 UAF 动画系统**，并且需要精确的动画评估同步，那么本插件是必要的。否则，对于传统的游戏逻辑和简单动画通知，使用标准的 `UAnimNotify` 即可。由于其**实验性**，建议在生产环境中使用前做好评估和风险预案。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EvaluationNotifies)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Experimental/EvaluationNotifies/Tests/) (路径推断)
-   [官方文档](https://docs.unrealengine.com) (暂无专属文档)