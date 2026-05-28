# Contextual Animation

> A simulated cable component.

| 属性 | 值 |
|---|---|
| 中文名 | 上下文动画 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、动画资产、测试资源） |
| 模块 | `ContextualAnimation` (Runtime), `ContextualAnimationEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-01-25 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/ContextualAnimation) | |

## 用途

Contextual Animation 系统用于创建和管理**多个角色之间的上下文感知动画交互**。它解决了多个角色需要同时、协调地播放相关动画的复杂场景问题，例如：
- 格斗游戏中角色间的连续招式
- 合作解谜中的同步动作
- 角色间的交互行为（如跳舞、格斗、共同操作物体）

与传统的动画蒙太奇系统不同，Contextual Animation 允许：
1. 预定义多个角色在特定情境中的动画轨道（Tracks）
2. 自动计算角色间的空间对齐（Alignment）
3. 支持运行时动态选择动画变体
4. 集成运动变形（Motion Warping）和反向动力学（IK）
5. 内置网络复制支持，用于多人游戏

## 使用场景

- **格斗游戏**：创建复杂的连招系统，每个招式都有对应的受击动画
- **合作游戏**：两个玩家需要同时进行开门、搬运等协作动作
- **NPC 交互**：NPC 与玩家或其他 NPC 之间的对话、交易等动画序列
- **过场动画**：实时过场动画，角色位置会根据游戏状态动态调整
- **环境交互**：角色与可交互环境物体（如梯子、载具）的动画

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `BP_CreateContextualAnimSceneBindings` | 根据场景资产和角色绑定创建场景绑定 | `UContextualAnimUtilities` |
| `BP_CreateContextualAnimSceneBindingsForTwoActors` | 为两个角色创建场景绑定（简化版） | `UContextualAnimUtilities` |
| `BP_FindAnimationForRole` | 在指定章节和动画集中查找特定角色的动画 | `UContextualAnimSceneAsset` |
| `BP_GetAlignmentTransformForRoleRelativeToWarpPoint` | 获取角色相对于扭曲点的对齐变换 | `UContextualAnimSceneAsset` |
| `BP_GetIKTargetTransformForRoleAtTime` | 在指定时间获取角色的 IK 目标变换 | `UContextualAnimSceneAsset` |
| `BP_SceneBindings_CalculateWarpPointsForSectionAtIndex` | 计算场景绑定的扭曲点 | `UContextualAnimUtilities` |
| `BP_SceneBindings_GetAlignmentTransformForRoleRelativeToOtherRole` | 获取一个角色相对于另一个角色的对齐变换 | `UContextualAnimUtilities` |
| `StartContextualAnimScene` | 开始上下文动画场景 | `UContextualAnimSceneActorComponent` |
| `LateJoinContextualAnimScene` | 让角色中途加入正在播放的动画场景 | `UContextualAnimSceneActorComponent` |
| `TransitionContextualAnimScene` | 过渡到同一场景资产中的不同章节 | `UContextualAnimSceneActorComponent` |

### 使用示例（蓝图描述）

1. **创建场景资产**：创建 `UContextualAnimSceneAsset` 资产，定义角色、章节和动画集
2. **分配组件**：为每个参与动画的角色添加 `UContextualAnimSceneActorComponent`
3. **创建场景绑定**：
   - 使用 `BP_CreateContextualAnimSceneBindings` 节点
   - 传入场景资产和角色映射（`RoleToActorMap`）
   - 指定要使用的章节和动画集（或让系统自动选择）
4. **启动动画**：调用 `StartContextualAnimScene` 并传入场景绑定
5. **响应事件**：监听 `OnJoinedSceneDelegate`、`OnLeftSceneDelegate` 等委托

## C++ 用法

### 头文件引入

```cpp
#include "ContextualAnimation.h"
#include "ContextualAnimSceneAsset.h"
#include "ContextualAnimSceneActorComponent.h"
#include "ContextualAnimUtilities.h"
```

### 基本用法

从测试用例中提取，展示如何创建和使用场景资产：

```cpp
// 创建角色绑定上下文
FContextualAnimSceneBindingContext PrimaryContext(PrimaryActor);
FContextualAnimSceneBindingContext SecondaryContext(SecondaryActor);

// 创建场景绑定
FContextualAnimSceneBindings Bindings;
bool bSuccess = UContextualAnimUtilities::BP_CreateContextualAnimSceneBindingsForTwoActors(
    SceneAsset, PrimaryContext, SecondaryContext, Bindings);

if (bSuccess)
{
    // 在角色上获取或创建场景组件
    UContextualAnimSceneActorComponent* PrimaryComp = 
        PrimaryActor->FindComponentByClass<UContextualAnimSceneActorComponent>();
    
    // 开始动画场景
    PrimaryComp->StartContextualAnimScene(Bindings);
}
```

### 进阶用法

结合选择标准和外部扭曲目标：

```cpp
// 创建复杂的选择标准
UContextualAnimSelectionCriterion_Cone* ConeCriterion = NewObject<UContextualAnimSelectionCriterion_Cone>();
ConeCriterion->Mode = EContextualAnimCriterionConeMode::ToPrimary;
ConeCriterion->Distance = 300.f;
ConeCriterion->HalfAngle = 45.f;

// 添加到动画集的选择标准
FContextualAnimTrack& Track = AnimSet.Tracks[0];
Track.SelectionCriteria.Add(ConeCriterion);

// 添加外部扭曲目标
TArray<FContextualAnimWarpTarget> ExternalTargets;
FContextualAnimWarpTarget WarpTarget(
    FName("ExternalTarget"), 
    FName("SocketName"), 
    FTransform(FVector(100.f, 200.f, 0.f))
);
ExternalTargets.Add(WarpTarget);

// 使用外部扭曲目标启动动画
SceneComponent->StartContextualAnimScene(Bindings, ExternalTargets);
```

## Demo 示例

```cpp
// MyCharacter.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "ContextualAnimSceneActorComponent.h"
#include "MyCharacter.generated.h"

UCLASS()
class AMyCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    AMyCharacter();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "ContextualAnim")
    UContextualAnimSceneActorComponent* ContextualAnimComponent;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "ContextualAnim")
    UContextualAnimSceneAsset* InteractionSceneAsset;

    UFUNCTION(BlueprintCallable, Category = "ContextualAnim")
    void StartInteraction(AActor* OtherActor);

    UFUNCTION(BlueprintCallable, Category = "ContextualAnim")
    void LateJoinInteraction(AActor* OtherActor, FName Role);

    UFUNCTION(BlueprintCallable, Category = "ContextualAnim")
    void TransitionToLoop();

protected:
    UFUNCTION()
    void OnJoinedScene();

    UFUNCTION()
    void OnLeftScene();

    UFUNCTION()
    void OnMontageBlendingOut(UAnimMontage* Montage, bool bInterrupted);

    virtual void BeginPlay() override;
};

// MyCharacter.cpp
#include "MyCharacter.h"
#include "ContextualAnimUtilities.h"

AMyCharacter::AMyCharacter()
{
    ContextualAnimComponent = CreateDefaultSubobject<UContextualAnimSceneActorComponent>(TEXT("ContextualAnimComp"));
}

void AMyCharacter::BeginPlay()
{
    Super::BeginPlay();

    // 绑定事件
    ContextualAnimComponent->OnJoinedSceneDelegate.AddDynamic(this, &AMyCharacter::OnJoinedScene);
    ContextualAnimComponent->OnLeftSceneDelegate.AddDynamic(this, &AMyCharacter::OnLeftScene);
    ContextualAnimComponent->OnMontageBlendingOutDelegate.AddDynamic(this, &AMyCharacter::OnMontageBlendingOut);
}

void AMyCharacter::StartInteraction(AActor* OtherActor)
{
    if (!InteractionSceneAsset || !OtherActor) return;

    // 创建场景绑定上下文
    FContextualAnimSceneBindingContext MyContext(this);
    FContextualAnimSceneBindingContext OtherContext(OtherActor);

    TMap<FName, FContextualAnimSceneBindingContext> RoleToActorMap;
    RoleToActorMap.Add(FName("Attacker"), MyContext);
    RoleToActorMap.Add(FName("Victim"), OtherContext);

    // 创建场景绑定
    FContextualAnimSceneBindings Bindings;
    UContextualAnimUtilities::BP_CreateContextualAnimSceneBindings(
        InteractionSceneAsset, RoleToActorMap, Bindings);

    // 开始动画
    ContextualAnimComponent->StartContextualAnimScene(Bindings);
}

void AMyCharacter::LateJoinInteraction(AActor* OtherActor, FName Role)
{
    ContextualAnimComponent->LateJoinContextualAnimScene(OtherActor, Role);
}

void AMyCharacter::TransitionToLoop()
{
    // 过渡到名为 "Loop" 的章节
    ContextualAnimComponent->TransitionContextualAnimScene(FName("Loop"));
}

void AMyCharacter::OnJoinedScene()
{
    UE_LOG(LogTemp, Log, TEXT("Actor joined contextual anim scene"));
}

void AMyCharacter::OnLeftScene()
{
    UE_LOG(LogTemp, Log, TEXT("Actor left contextual anim scene"));
}

void AMyCharacter::OnMontageBlendingOut(UAnimMontage* Montage, bool bInterrupted)
{
    if (!bInterrupted)
    {
        UE_LOG(LogTemp, Log, TEXT("Montage completed: %s"), *Montage->GetName());
    }
}
```

## 模块依赖

从 Build.cs 中提取的独特依赖：

| 模块 | 用途 |
|---|---|
| `MotionWarping` | 运动变形支持，用于动态调整动画中的运动轨迹 |
| `IKRig` | 反向动力学支持，用于动画过程中的脚部 IK 等效果 |
| `GameplayTags` | 标签系统，用于上下文判断和动画选择 |
| `AnimationBudgetAllocator` | 动画预算分配，用于优化动画计算 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志系统到新宏格式 |
| 2026-04-06 | `76545631` | [CAS] Override Support for CAS Actors | 为场景演员添加覆盖支持 |
| 2026-03-27 | `5c7c61e7` | Contextual Anim Editor: | 上下文动画编辑器功能更新 |
| 2026-03-11 | `4f7e0527` | Contextual Anim Editor - Added warning message to validate that a preview actor class has a Contextu | 编辑器添加验证警告消息 |
| 2026-03-11 | `9d29e89e` | Contextual Anim - Added option to let the system find ideal start time for the interaction based on | 添加系统自动寻找理想开始时间的选项 |

### 维护评价

**活跃维护**：Contextual Animation 插件处于活跃维护状态，最近的更新集中在 2026 年 3-4 月，主要增强了编辑器功能和运行时覆盖支持。作为实验性插件，它仍在积极开发中，但已具备完整的功能集。

**特点**：
- 完整的运行时和编辑器模块
- 网络复制支持，适合多人游戏
- 与 MotionWarping 和 IKRig 深度集成
- 提供丰富的蓝图和 C++ API
- 内置调试可视化功能

**注意事项**：
- 默认不启用（`EnabledByDefault: false`），需要在项目设置中手动启用
- 实验性功能，API 可能在未来版本中变化
- 依赖 MotionWarping 和 IKRig 插件

**推荐**：对于需要复杂多角色动画交互的项目，特别是格斗游戏、合作游戏或叙事驱动的游戏，推荐使用此插件。它提供了比传统蒙太奇系统更强大和灵活的多角色动画管理方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/ContextualAnimation)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/ContextualAnimation/Source/ContextualAnimationTests)