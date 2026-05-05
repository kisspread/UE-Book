# Contextual Animation

> *(Description field is empty in .uplugin)*

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ContextualAnimation` (Runtime), `ContextualAnimationEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-01-25 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Animation/ContextualAnimation) | |

## 用途

Contextual Animation 是一个用于**编排多个角色之间协调同步动画交互**的系统。它解决的核心问题是：当两个或多个角色需要在空间上精确对齐并同步播放动画时（如格斗游戏中的抓取、处决动画、开门/上车等交互），如何自动化地处理角色定位、动画选择、空间对齐和网络同步。

系统通过定义"场景（Scene）"资产来描述一次交互的所有参与者角色（Role）、每个角色可选的动画集合（AnimSet）以及空间对齐规则（Warp Point），然后在运行时根据查询条件自动选择最合适的动画变体并驱动所有参与者同步播放。

该插件**强依赖 MotionWarping 插件**来实现运行时角色位移对齐（Warping），并使用 **IKRig** 来处理动画交互过程中的 IK 目标更新。

## 使用场景

- 你在做一个动作游戏，需要抓取/处决/摔投等两人或多人协调动画 → 用 ContextualAnimation
- 你需要角色从不同方向（左侧/右侧/前方）接近目标时自动选择对应的动画变体 → 用 ContextualAnimation
- 你需要在交互过程中自动对齐角色位置，使动画在空间上精确匹配 → 用 ContextualAnimation + MotionWarping
- 你需要多人游戏中的协调动画网络同步 → ContextualAnimation 内置了复制支持
- 你需要在交互动画中实时更新 IK 目标（如手放的位置） → ContextualAnimation 内置 IK Target 系统

## 模块总览

| 模块 | 类型 | 文件数 | 文档 |
|---|---|---|---|
| `ContextualAnimation` | Runtime | ~18 | [Runtime.md](Runtime.md) |
| `ContextualAnimationEditor` | Editor | ~48 | [Editor.md](Editor.md) |

## 核心概念

### Scene Asset（场景资产）

`UContextualAnimSceneAsset` 是整个系统的核心数据资产（`UDataAsset`），定义了一次交互的所有数据：

- **Roles（角色）**：通过 `UContextualAnimRolesAsset` 定义参与交互的所有角色（如 "Attacker"、"Victim"、"Car"）。每个角色有名称、是否为角色、Capsule 尺寸等属性
- **Primary Role（主角色）**：交互中作为定位参考点的角色，其他角色相对于它进行对齐
- **Sections（区段）**：一个场景可以有多个区段，每个区段代表交互的不同阶段（如"接近→抓取→处决"）
- **AnimSets（动画集合）**：每个区段包含多个 AnimSet，每个 AnimSet 是同一交互的一组动画变体（如从左边攻击 vs 从右边攻击）
- **AnimTrack（动画轨道）**：每个 AnimSet 中每个角色对应的动画及其参数

### Selection Criteria（选择标准）

每个 AnimTrack 可以附加选择标准（`UContextualAnimSelectionCriterion` 的子类），用于在运行时根据空间/方向条件筛选最佳动画变体：

| 标准类 | 说明 |
|---|---|
| `UContextualAnimSelectionCriterion_Cone` | 基于锥形区域的方向判断（从前/后/左/右接近） |
| `UContextualAnimSelectionCriterion_Distance` | 基于距离（2D/3D）的范围筛选 |
| `UContextualAnimSelectionCriterion_TriggerArea` | 基于自定义多边形区域的触发判断 |
| `UContextualAnimSelectionCriterion_Blueprint` | 蓝图可实现的自定义选择标准 |

### Warp Point（对齐点）

定义了交互中用于空间对齐的参考变换（Transform）。三种模式：

- **PrimaryActor**：直接使用主角色的变换（适合与静态物体交互）
- **Socket**：使用主角色某个 Socket 的变换（适合不同体型的物体复用同一动画）
- **Custom**：基于自定义规则计算（如两个角色之间的中点）

### Bindings（绑定）

`FContextualAnimSceneBindings` 将具体的 Actor 实例绑定到场景定义中的 Role，并记录选中的 Section 和 AnimSet 索引。它是运行时表示"谁在扮演什么角色"的核心结构。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `StartContextualAnimScene` | 启动一次上下文动画场景 | `UContextualAnimSceneActorComponent` |
| `LateJoinContextualAnimScene` | 让新角色中途加入正在播放的场景 | `UContextualAnimSceneActorComponent` |
| `TransitionContextualAnimScene` | 过渡到场景的不同区段 | `UContextualAnimSceneActorComponent` |
| `TransitionContextualAnimSceneToSpecificSet` | 过渡到指定区段的指定动画集合 | `UContextualAnimSceneActorComponent` |
| `TransitionSingleActor` | 只让一个角色过渡到新区段/集合 | `UContextualAnimSceneActorComponent` |
| `EarlyOutContextualAnimScene` | 提前退出场景 | `UContextualAnimSceneActorComponent` |
| `IsInActiveScene` | 查询是否正在参与一个活跃场景 | `UContextualAnimSceneActorComponent` |
| `GetBindings` | 获取当前绑定信息 | `UContextualAnimSceneActorComponent` |
| `Create Contextual Anim Scene Bindings` | 创建绑定（从多角色 Map） | `UContextualAnimUtilities` |
| `Create Contextual Anim Scene Bindings For Two Actors` | 创建绑定（两角色快捷方式） | `UContextualAnimUtilities` |
| `Find Animation For Role` | 查找指定角色的动画 | `UContextualAnimSceneAsset` |
| `Get Alignment Points For Secondary Role` | 获取次要角色的对齐点 | `UContextualAnimSceneAsset` |
| `Query` | 查询最佳动画（旧 API） | `UContextualAnimSceneAsset` |

### 事件委托

| 委托 | 说明 | 所在类 |
|---|---|---|
| `OnJoinedSceneDelegate` | 角色加入场景时触发 | `UContextualAnimSceneActorComponent` |
| `OnLeftSceneDelegate` | 角色离开场景时触发 | `UContextualAnimSceneActorComponent` |
| `OnPlayMontageNotifyBeginDelegate` | Montage 通知开始时触发 | `UContextualAnimSceneActorComponent` |
| `OnMontageBlendingOutDelegate` | Montage 混合出时触发 | `UContextualAnimSceneActorComponent` |

### 使用示例（蓝图描述）

**两角色交互的基本流程：**

1. 在两个角色上分别添加 `ContextualAnimSceneActorComponent`，并指向同一个 `UContextualAnimSceneAsset`
2. 创建 `FContextualAnimSceneBindingContext`（分别包装两个 Actor）
3. 使用 `BP_CreateContextualAnimSceneBindingsForTwoActors` 创建 Bindings
4. 在主角色上调用 `StartContextualAnimScene(Bindings)` 启动交互
5. 组件自动处理动画播放、空间对齐（通过 MotionWarping）、IK 更新和网络同步

**事件驱动的交互流程：**

1. 在攻击者的蓝图中，当玩家按下攻击键
2. 获取附近的目标 Actor
3. 创建 Bindings（Primary = 攻击者, Secondary = 目标）
4. 如果 Bindings 创建成功，调用 `StartContextualAnimScene`
5. 绑定 `OnMontageBlendingOutDelegate` 来检测动画播放完毕
6. 绑定 `OnPlayMontageNotifyBeginDelegate` 来响应动画中的特定时刻（如造成伤害）

## C++ 用法

### 头文件引入

```cpp
#include "ContextualAnimSceneAsset.h"
#include "ContextualAnimSceneActorComponent.h"
#include "ContextualAnimUtilities.h"
#include "ContextualAnimTypes.h"
```

### 基本用法 — 创建 Bindings 并启动场景

```cpp
// 来源: ContextualAnimSceneActorComponent.cpp 中 StartContextualAnimScene 的典型调用模式

// 1. 创建绑定上下文（包装 Actor 及其当前状态）
FContextualAnimSceneBindingContext PrimaryContext(AttackerActor);
FContextualAnimSceneBindingContext SecondaryContext(VictimActor);

// 2. 创建 Bindings — 系统自动根据 Selection Criteria 选择最佳 AnimSet
FContextualAnimSceneBindings Bindings;
bool bSuccess = FContextualAnimSceneBindings::TryCreateBindings(
    *SceneAsset,           // UContextualAnimSceneAsset*
    0,                     // SectionIdx
    PrimaryContext,
    SecondaryContext,
    Bindings
);

// 3. 通过 SceneActorComponent 启动场景
if (bSuccess)
{
    if (UContextualAnimSceneActorComponent* Comp = 
        AttackerActor->FindComponentByClass<UContextualAnimSceneActorComponent>())
    {
        Comp->StartContextualAnimScene(Bindings);
    }
}
```

### 使用 TMap 方式创建 Bindings（多角色场景）

```cpp
// 来源: ContextualAnimTypes.h 中 FContextualAnimSceneBindings::TryCreateBindings

TMap<FName, FContextualAnimSceneBindingContext> Params;
Params.Add("Attacker", FContextualAnimSceneBindingContext(AttackerActor));
Params.Add("Victim", FContextualAnimSceneBindingContext(VictimActor));
Params.Add("Car", FContextualAnimSceneBindingContext(CarActor));

FContextualAnimSceneBindings Bindings;
bool bSuccess = FContextualAnimSceneBindings::TryCreateBindings(
    *SceneAsset, 0, 0, Params, Bindings);
```

### 进阶用法 — Late Join 和 Transition

```cpp
// Late Join: 让新角色中途加入正在播放的交互
// 来源: ContextualAnimSceneActorComponent.h
UContextualAnimSceneActorComponent* Comp = GetSceneActorComponent();
Comp->LateJoinContextualAnimScene(NewActor, FName("Passenger"));

// Transition: 从一个区段过渡到另一个区段（如从"接近"过渡到"抓取"）
Comp->TransitionContextualAnimScene(FName("Grab"));

// Transition 到指定的动画集合
Comp->TransitionContextualAnimSceneToSpecificSet(FName("Grab"), 2);

// Early Out: 提前退出（如玩家按了取消）
Comp->EarlyOutContextualAnimScene(true); // true = 让所有人都退出
```

### 自定义选择标准（C++）

```cpp
// 来源: ContextualAnimSelectionCriterion.h

// 继承 UContextualAnimSelectionCriterion 实现自定义判断逻辑
UCLASS()
class UMySelectionCriterion : public UContextualAnimSelectionCriterion
{
    GENERATED_BODY()
public:
    virtual bool DoesQuerierPassCondition(
        const FContextualAnimSceneBindingContext& Primary,
        const FContextualAnimSceneBindingContext& Querier) const override
    {
        // 自定义条件：例如检查 Querier 是否持有特定武器
        return Querier.HasMatchingGameplayTag(FGameplayTag::RequestGameplayTag("Weapon.Sword"));
    }
};
```

### 获取 IK 目标

```cpp
// 来源: ContextualAnimSceneActorComponent.h

// 组件自动在每帧更新 IK 目标
UContextualAnimSceneActorComponent* Comp = ...;
const TArray<FContextualAnimIKTarget>& IKTargets = Comp->GetIKTargets();

for (const FContextualAnimIKTarget& Target : IKTargets)
{
    // Target.GoalName — IK 目标名称
    // Target.BoneName — 关联的骨骼
    // Target.Alpha — 混合权重（0-1）
    // Target.Transform — 世界空间变换
}

// 或通过名称获取特定目标
const FContextualAnimIKTarget& HandTarget = Comp->GetIKTargetByGoalName(FName("RightHand"));
```

## Demo 示例

### 最小交互组件子类

**MyInteractionComponent.h**

```cpp
#pragma once

#include "ContextualAnimSceneActorComponent.h"
#include "MyInteractionComponent.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class MYGAME_API UMyInteractionComponent : public UContextualAnimSceneActorComponent
{
    GENERATED_BODY()

public:
    UMyInteractionComponent(const FObjectInitializer& ObjectInitializer)
        : Super(ObjectInitializer) {}

    // 尝试对目标执行交互
    UFUNCTION(BlueprintCallable, Category = "Interaction")
    bool TryInteract(AActor* TargetActor);
};
```

**MyInteractionComponent.cpp**

```cpp
#include "MyInteractionComponent.h"
#include "ContextualAnimSceneAsset.h"
#include "ContextualAnimUtilities.h"

bool UMyInteractionComponent::TryInteract(AActor* TargetActor)
{
    if (!SceneAsset || !TargetActor)
    {
        return false;
    }

    // 创建两角色绑定
    FContextualAnimSceneBindingContext PrimaryContext(GetOwner());
    FContextualAnimSceneBindingContext SecondaryContext(TargetActor);

    FContextualAnimSceneBindings Bindings;
    if (FContextualAnimSceneBindings::TryCreateBindings(
            *SceneAsset, 0, PrimaryContext, SecondaryContext, Bindings))
    {
        return StartContextualAnimScene(Bindings);
    }

    return false;
}
```

**Build.cs 依赖：**

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Engine",
    "ContextualAnimation",    // Runtime 模块
    "MotionWarping",          // 必须依赖
    "GameplayTags"
});
```

### AnimNotifyState 用法

**IK Window** (`UAnimNotifyState_IKWindow`)：在动画的特定区间内启用 IK 求解，支持 Blend In/Out 和指定 Goal Name。

**Early Out Contextual Anim** (`UAnimNotifyState_EarlyOutContextualAnimWindow`)：在动画末尾定义一个窗口，允许玩家提前退出交互以提升操作响应性。可配置 `bStopEveryone` 控制是否所有人都退出。

## 模块依赖

### Runtime 模块（ContextualAnimation）

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `NetCore` | 网络复制基础设施 |
| `GameplayTags` | 标签系统（用于选择标准和绑定上下文） |
| `MotionWarping` | 运行时角色位移对齐（Warping），**核心依赖** |
| `IKRig` | IK 目标求解，用于交互过程中的手/脚 IK |

### Editor 模块（ContextualAnimationEditor）

| 模块 | 用途 |
|---|---|
| `AIModule` | 编辑器预览中 AI 相关支持 |
| `NavigationSystem` | 编辑器导航相关 |
| `MotionWarping` | 编辑器中的 Warp 窗口支持 |
| `UnrealEd` | 编辑器框架 |
| `Sequencer` / `MovieScene` | Sequencer 集成（交互动画的时间轴编辑） |
| `Persona` | 动画编辑器集成 |
| `AnimGraph` | 动画图集成 |

### 使用者的 Build.cs 最小依赖

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "ContextualAnimation",
    "MotionWarping",
    "GameplayTags"
});
```

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-07-22 | `818a66e` | 改进 FindAnimSet 的日志输出，便于调试 |
| 2025-07-15 | `9c92fa4` | **重要重构**：将 ContextualAnimSceneActorComponent 从 SceneComponent 改为 ActorComponent 以提升性能；新增 AlignmentOffset 属性用于偏移最终对齐变换 |
| 2025-06-12 | `52e089a` | 修复 OnLeftScene 委托的广播时机，防止在委托回调中启动新交互导致的无限循环 |

### 维护评价

- **状态**：**活跃维护中** — 2025 年 7 月仍有功能性更新和重构
- **实验性**：`.uplugin` 中 `IsExperimentalVersion=true`，`EnabledByDefault=false`，需手动启用
- **活跃度**：频繁更新，Epic 的 Samuele Rigamonti 和 Jose Villarroel 持续维护
- **已知限制**：
  - 仍标记为实验性，API 可能在未来版本中变化
  - 部分旧 API（如 `UContextualAnimSceneAsset::Query`、`FContextualAnimQueryResult`、`FContextualAnimQueryParams`）已标记为 DEPRECATED，将在未来移除
  - 不包含测试用例（无 Automation Test 文件）
  - 不包含内容资产（无 .uasset 示例文件）
- **推荐**：适合需要多角色协调动画的项目使用，但需注意实验性标记，做好应对 API 变更的准备

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Animation/ContextualAnimation)
- 官方文档：无（.uplugin 中 DocsURL 为空）
- [MotionWarping 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Animation/AnimNext) — 核心依赖
- 测试用例：无（插件目录内未发现测试文件）
