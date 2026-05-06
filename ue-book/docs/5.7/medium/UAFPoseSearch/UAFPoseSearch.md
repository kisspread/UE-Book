# UAF Pose Search

> Pose Search integration for UAF.

| 属性 | 值 |
|---|---|
| 中文名 | UAF 姿势搜索 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `UAFPoseSearch` (Runtime), `UAFPoseSearchUncookedOnly` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-20 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFPoseSearch) | |

## 用途

UAFPoseSearch 是 UE5 动画框架 **UAF (Animation Next)** 的姿势搜索集成插件。它使 UAF 动画图表能够直接使用引擎的 Pose Search 子系统，实现基于运动匹配（Motion Matching）的动画选择。插件提供了以下核心能力：

- **运动匹配 Trait**：在 UAF 图形中添加 `MotionMatchingTrait`，根据轨迹和姿势历史自动搜索最佳动画片段。
- **姿势历史收集**：通过 `HistoryCollectorTrait` 记录角色骨骼变换历史，为运动匹配提供输入。
- **轨迹生成**：提供 RigUnit 节点（如 `Generate Character Movement Component Trajectory`）从角色移动组件生成轨迹，或从 UAF 变量直接读取。
- **调试工具**：`Debug Draw Trajectory` 节点可在编辑器中可视化轨迹。
- **数据库辅助**：`Get Database Tags`、`Get Selected Database` 等节点方便在动画图表中查询姿势搜索数据库。

该插件的存在前提是已启用 UAF 插件和引擎的 Pose Search 模块。它本质上是将 Pose Search 的数据库查询、轨迹匹配等功能封装为 UAF 的 Trait 和 RigUnit，使开发者可以在 UAF 的节点化动画图中直接使用运动匹配，无需编写 C++ 集成代码。

## 使用场景

- **角色移动动画**：使用运动匹配自动混合跑、走、跳跃等动作，减少状态机复杂度。
- **动作匹配**：在需要精确匹配角色轨迹（如转弯、停止）时，通过姿势搜索获得最合适的动画片段。
- **性能敏感项目**：利用搜索节流（`SearchThrottleTime`）和缓存机制控制每帧搜索频率。
- **调试与原型**：通过 `PoseSearchResultEmulatorTrait` 手动指定动画结果，方便迭代。

## 蓝图用法

该插件提供的主要 UAF RigUnit 节点可在 UAF 动画图表（Animation Graph）中直接使用。以下为常用节点：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Motion Matching` | 运动匹配 Trait，根据轨迹和姿势历史搜索最佳动画 | `FMotionMatchingTraitSharedData` |
| `Pose History` | 姿势历史收集 Trait，记录骨骼变换历史 | `FAnimNextHistoryCollectorTraitSharedData` |
| `Generate Trajectory from Character Movement Component` | 从 `UCharacterMovementComponent` 生成轨迹数据 | `FRigUnit_GenerateCharacterMovementComponentTrajectory` |
| `Multi Anim Get Animation Asset` | 从 `MultiAnimAsset` 中根据角色名获取动画资源 | `FRigUnit_MultiAnimGetAnimationAsset` |
| `Get Database Tags` | 获取姿势搜索数据库的元数据标签 | `FRigUnit_PoseSearchDatabaseGetTags` |
| `Get Selected Database` | 从姿势搜索结果中获取被选中的数据库 | `FRigUnit_PoseSearchResultGetSelectedDatabase` |
| `Debug Draw Trajectory` | 可视化调试轨迹 | `FRigUnit_DebugDrawTrajectory` |
| `Pose Search Result Emulator` | 手动模拟姿势搜索结果，用于测试 | `FPoseSearchResultEmulatorTraitSharedData` |

### 使用示例（蓝图描述）

1. **基本运动匹配**  
   在 UAF 动画图表中添加 `Motion Matching` 节点，设置其 `Databases` 属性为一个或多个 `UPoseSearchDatabase` 资源。连接输入轨迹（可通过 `Generate Trajectory from Character Movement Component` 节点输出）到 `Trajectory` 引脚。节点自动搜索并输出最佳动画结果。

2. **轨迹生成**  
   将 `Generate Trajectory from Character Movement Component` 节点连接到角色移动组件，设置采样参数（历史/预测数量、间隔），输出 `FTransformTrajectory` 供运动匹配使用。

3. **姿势历史收集**  
   在图表中添加 `Pose History` 节点，设置 `PoseCount`、`SamplingInterval` 和要记录的骨骼（`CollectedBones`）。启用 `bInitializeWithRefPose` 可在开始时使用参考姿势填充历史。

## C++ 用法

### 头文件引入

```cpp
#include "PoseSearch/PoseSearchLibrary.h"                // 引擎姿势搜索库
#include "PoseSearch/PoseSearchHistory.h"                // 姿势历史相关
#include "UAFPoseSearch/Public/PoseHistoryEvaluation.h"  // 评估栈定义
#include "UAFPoseSearch/Private/MotionMatchingTrait.h"   // 运动匹配 Trait
#include "UAFPoseSearch/Private/HistoryCollectorTrait.h" // 历史收集 Trait
```

### 基本用法

**在 UAF Trait 图配置中使用（C++ Trait 定义）**  
以下示例演示如何在自定义 UAF Trait 中通过 `IPoseHistory` 接口获取历史数据：

```cpp
// 来源：IPoseHistory.h (私有接口)
void MyTrait::PreUpdate(FUpdateTraversalContext& Context, const TTraitBinding<IUpdate>& Binding, const FTraitUpdateState& TraitState) const
{
    // 获取姿势历史（需要从绑定中查询另一条Trait的IPoseHistory接口）
    if (const IPoseHistory* PoseHistoryInterface = Binding.FindTraitInterface<IPoseHistory>())
    {
        const UE::PoseSearch::IPoseHistory* PoseHistory = PoseHistoryInterface->GetPoseHistory(Context, Binding);
        // 使用 PoseHistory ...
    }
}
```

**直接使用运动匹配状态**  
运动匹配 Trait 的内部状态 `FMotionMatchingState` 可在 `FInstanceData` 中获取，用于自定义处理：

```cpp
// 来源：MotionMatchingTrait.h
void FMotionMatchingTrait::PublishResults(const TTraitBinding<IUpdate>& Binding) const
{
    const FInstanceData& InstanceData = Binding.GetInstanceData<FInstanceData>();
    const FMotionMatchingState& State = InstanceData.MotionMatchingState;
    // 读取 State.SelectedAnimation, State.BlendParameters 等
}
```

### 进阶用法

**结合 Chooser 系统**  
插件提供了 `FPoseHistoryAnimProperty` 作为 Chooser 参数，可在 Chooser 表中引用 UAF 变量的姿势历史：

```cpp
// 来源：PoseHistoryChooserParameter.h
UPROPERTY(DisplayName = "Variable", EditAnywhere, Category="Variable")
FAnimNextVariableReference Variable; // 引用 UAF 变量（如 PoseHistory 对象）
```
在 C++ Chooser 评估中通过 `GetValue` 获取 `FPoseHistoryReference`，然后传递给运动匹配。

**自定义姿势搜索特征通道**  
`UPoseSearchFeatureChannel_DistanceFromAnimNextVar` 允许从 AnimNext 变量读取距离数据作为搜索特征：

```cpp
// 来源：PoseSearchFeatureChannel_DistanceFromAnimNextVar.h
UPROPERTY(DisplayName = "Variable", EditAnywhere, Category="Variable")
FAnimNextVariableReference DistanceVariable;

virtual void BuildQuery(UE::PoseSearch::FSearchContext& SearchContext) const override;
```

## Demo 示例

以下是一个完整的 UAF Trait 类，展示如何结合 `HistoryCollectorTrait` 和 `MotionMatchingTrait` 实现自定义运动匹配逻辑。文件假设项目已启用 UAF 和 UAFPoseSearch 插件。

**MyCustomMotionMatchingTrait.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "TraitCore/Trait.h"
#include "TraitInterfaces/IUpdate.h"
#include "TraitInterfaces/IEvaluate.h"
#include "UAFPoseSearch/Private/MotionMatchingTrait.h"
#include "UAFPoseSearch/Private/HistoryCollectorTrait.h"

USTRUCT(BlueprintType)
struct FMyCustomMotionMatchingTraitSharedData : public FAnimNextTraitSharedData
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, Category = "Custom")
    TObjectPtr<const UPoseSearchDatabase> Database;
};

struct FMyCustomMotionMatchingTrait : public FAdditiveTrait, public IUpdate, public IEvaluate
{
    DECLARE_ANIM_TRAIT(FMyCustomMotionMatchingTrait, FAdditiveTrait)

    using FSharedData = FMyCustomMotionMatchingTraitSharedData;

    struct FInstanceData : FTrait::FInstanceData
    {
        UE::UAF::FMotionMatchingTrait::FInstanceData BaseMMTraitData;
        // 可扩展自定义状态
    };

    virtual void PreUpdate(FUpdateTraversalContext& Context, const TTraitBinding<IUpdate>& Binding, const FTraitUpdateState& TraitState) const override
    {
        const auto& SharedData = Binding.GetSharedData<FSharedData>();
        auto& InstanceData = Binding.GetInstanceData<FInstanceData>();
        
        // 获取运动匹配 Trait 的绑定引脚（假设图表中串联了 MotionMatching Trait）
        TTraitBinding<IUpdate> MMUpdateBinding = Binding.FindNextUpdateTrait(); // 实际需通过图表布局获取
        if (MMUpdateBinding.IsValid())
        {
            Context.PushOverride(MMUpdateBinding, SharedData.Database); // 示例：重写数据库
            // 再调用原始 PreUpdate
        }
    }

    virtual void PostEvaluate(FEvaluateTraversalContext& Context, const TTraitBinding<IEvaluate>& Binding) const override
    {
        // 读取最终结果（例如从 Module Variables）
    }
};
```

**MyCustomMotionMatchingTrait.cpp**
```cpp
#include "MyCustomMotionMatchingTrait.h"

// 无需额外实现，UE 宏会生成注册代码。
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `UAF` | 动画框架核心，提供 Trait、评估 VM、图形 |
| `PoseSearch` | 引擎姿势搜索库，提供数据库、特征通道、运动匹配算法 |
| `AnimNext` | UAF 的评估栈和变量系统 |
| `Chooser` | 选择器系统，用于 `FPoseHistoryAnimProperty` |

**注意**：`UAFPoseSearchUncookedOnly` 模块仅在未打包编辑器时使用，包含编辑器专用功能（如调试绘制）。

## 维护状态

### 近期更新

- 2025-10-03 `ff6147ec` Updated UAF Trajectory functions to have an execution pin.
- 2025-10-03 `61a8ba04` Added UAF GenerateTrajectory version for CharacterMovementComponent.
- 2025-10-01 `604a7718` PoseSearch - fix for MM trait timeline and MM node interaction blendstack synchronizations
- 2025-09-04 `d443289c` PoseSearch (初始提交，包含核心功能)
- 2025-08-20 `6cd89387` PoseSearch - making FPoseSearchColumn::InterruptMode pinnable

### 维护评价

该插件创建于 2025 年 8 月，至文档生成时仅约 2 个月，仍处于实验阶段。最近 1 个月内（2025年10月）有功能性更新（添加执行引脚、新增轨迹生成节点）和修复（混合栈同步问题），维护较为活跃。**由于实验性标记，API 可能发生变动，不建议用于正式项目**。测试覆盖度和性能表现尚未充分验证，社区使用较少。推荐仅用于原型开发和内部实验。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFPoseSearch)
- [官方文档](https://docs.unrealengine.com/5.7/AnimationNext)（UAF 通用文档，非本插件专有）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFPoseSearch/Tests)（如存在）