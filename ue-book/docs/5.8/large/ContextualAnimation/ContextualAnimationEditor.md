# ContextualAnimation

> （描述为空，基于源码分析编写）一个用于编排和管理多个角色之间复杂上下文动画交互的系统，允许精确定义每个参与者在特定交互中的动画、对齐和同步。

| 属性 | 值 |
|---|---|
| 中文名 | 上下文动画 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（动画资产、编辑器工具） |
| 模块 | `ContextualAnimation` (Runtime), `ContextualAnimationEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-01-25 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/ContextualAnimation) | |

## 用途

ContextualAnimation 是一个高级动画系统，旨在解决多人协作动画中的复杂问题。它不仅仅播放一个动画，而是为一场“交互”（例如一次抓取、一次治疗、一次协同攻击）定义了一个完整的“场景”。

核心思想是：一个交互场景（Scene）由多个“角色”（Role）参与，每个角色有一系列可能的动画集合（AnimSet），每个动画集合可以包含多个动画轨道（AnimTrack）。系统通过定义“选择标准”（Selection Criterion）来根据运行时的环境（如相对位置、朝向）自动选择最合适的动画集合。它与 MotionWarping 插件深度集成，以确保角色在播放动画时能精确地对齐到指定的交互点（如攻击者的武器准确命中目标）。这主要用于实现电影化、高质量且交互性强的过场动画和游戏玩法动画。

## 使用场景

- **动作游戏中的处决/反击动画**：玩家从不同角度、距离攻击敌人时，系统自动选择最合适的处决动画，并确保两者的模型位置和朝向精确匹配。
- **合作游戏中的协同动作**：例如，一名角色推开一扇门，另一名角色随即冲入，系统协调两者的动画起始时间和动作。
- **RPG 中的 NPC 交互**：玩家与商人交易、治疗伤员等，根据双方的相对位置选择不同的动画组合。
- **任何需要精确同步、对齐的多人动画序列**，特别是当动画的起始条件（如方位、距离）会动态变化时。

## 蓝图用法

蓝图主要通过 `UContextualAnimComponent` 和 `UContextualAnimSceneAsset` 来使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `StartContextualAnimScene` | 启动一个上下文动画场景。传入参与者 Actor 列表、场景资产等。 | `UContextualAnimComponent` |
| `StopContextualAnimScene` | 停止当前正在播放的上下文动画场景。 | `UContextualAnimComponent` |
| `TryStartContextualAnimScene` | 尝试启动场景，并根据输入的参数和选择标准返回是否成功。 | `UContextualAnimComponent` |
| `GetContextualAnimRole` | 获取指定 Actor 在当前场景中扮演的角色名称。 | `UContextualAnimComponent` |
| `GetAnimSetForRole` | 为指定角色获取当前选中的动画集合。 | `UContextualAnimComponent` |
| `GetAnimationForRole` | 获取指定角色当前正在播放的动画。 | `UContextualAnimComponent` |
| `GetAlignmentTrackTransform` | 获取指定角色在其动画轨道中的目标对齐变换（由 MotionWarping 使用）。 | `UContextualAnimComponent` |

### 使用示例（蓝图描述）

1.  **准备资产**：在编辑器中创建一个 `UContextualAnimSceneAsset`，定义好场景中的角色（如 `Attacker`, `Victim`）、每个角色的动画集合（AnimSet）以及每个动画集合内的动画和对齐数据。
2.  **添加组件**：给参与交互的每个 Actor 添加 `UContextualAnimComponent`。
3.  **启动交互**：在合适的时机（如玩家按下攻击键），获取玩家和敌人的 `UContextualAnimComponent`，调用 `TryStartContextualAnimScene` 节点。传入场景资产、参与者映射（例如一个 Map，键为 Role 名称如 `“Attacker”`，值为对应的 Actor），以及一个 `CriterionData`（可选，用于传递更精确的选择参数，如命中的位置）。
4.  **处理结果**：该节点会返回一个布尔值，表示是否成功匹配并启动了场景。成功启动后，所有参与者的 `UContextualAnimComponent` 会开始协调播放各自对应的动画。

## C++ 用法

### 头文件引入

```cpp
#include “ContextualAnim/Public/ContextualAnimComponent.h”
#include “ContextualAnim/Public/ContextualAnimSceneAsset.h”
#include “ContextualAnim/Public/ContextualAnimSubsystem.h” // 用于更底层的控制
```

### 基本用法

```cpp
// 假设你有一个 UContextualAnimSceneAsset* Asset 指向你编辑好的场景资产
// 并且有两个 AActor* AttackerActor 和 VictimActor

// 获取参与者的 ContextualAnimComponent
UContextualAnimComponent* AttackerComp = AttackerActor->FindComponentByClass<UContextualAnimComponent>();
UContextualAnimComponent* VictimComp = VictimActor->FindComponentByClass<UContextualAnimComponent>();

if (AttackerComp && VictimComp)
{
    // 准备参与者映射
    TMap<FName, AActor*> ContextualAnimActors;
    ContextualAnimActors.Add(Asset->GetRoleForComponent(AttackerComp), AttackerActor);
    ContextualAnimActors.Add(Asset->GetRoleForComponent(VictimComp), VictimActor);
    
    // 可选：准备选择标准数据
    FContextualAnimQueryResult QueryResult;
    
    // 尝试启动场景
    if (AttackerComp->TryStartContextualAnimScene(Asset, ContextualAnimActors, QueryResult))
    {
        UE_LOG(LogTemp, Log, TEXT(“上下文动画场景启动成功！”));
        // 动画将自动在相关组件上开始播放和协调
    }
}
```

### 进阶用法

使用 `UContextualAnimSubsystem` 进行更底层的控制，例如手动选择动画集合并启动场景实例。

```cpp
UContextualAnimSubsystem* AnimSubsystem = GetWorld()->GetSubsystem<UContextualAnimSubsystem>();
if (AnimSubsystem)
{
    // 根据当前条件（如距离、角度）为场景资产查询最合适的动画集合
    FContextualAnimQueryContext QueryContext;
    QueryContext.Transform = AttackerActor->GetActorTransform(); // 以攻击者为参考
    
    FContextualAnimQueryResult QueryResult;
    if (Asset->Query(QueryContext, QueryResult))
    {
        // 手动启动一个场景实例
        FContextualAnimSceneContext Context;
        Context.SceneAsset = Asset;
        Context.AnimSetIdx = QueryResult.AnimSetIdx; // 来自查询结果
        // ... 设置其他参与者信息
        
        FContextualAnimSceneInstance SceneInstance;
        AnimSubsystem->StartScene(Context, SceneInstance);
        
        // SceneInstance 现在可以用来控制场景的播放、获取参与者的蒙太奇等
    }
}
```

## Demo 示例

### MyCharacter.h
```cpp
#pragma once

#include “CoreMinimal.h”
#include “GameFramework/Character.h”
#include “ContextualAnim/Public/ContextualAnimComponent.h”
#include “MyCharacter.generated.h”

UCLASS()
class AMyCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    AMyCharacter();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = “Contextual Anim”)
    UContextualAnimComponent* ContextualAnimComp;

    // 其他角色代码...
};
```

### MyCharacter.cpp
```cpp
#include “MyCharacter.h”
#include “ContextualAnim/Public/ContextualAnimSceneAsset.h”

AMyCharacter::AMyCharacter()
{
    ContextualAnimComp = CreateDefaultSubobject<UContextualAnimComponent>(TEXT(“ContextualAnim”));
    // 组件需要挂在角色上
}

// 在某个技能或游戏事件中调用
void AMyCharacter::PerformInteraction(AActor* OtherActor)
{
    UContextualAnimSceneAsset* InteractionAsset = LoadObject<UContextualAnimSceneAsset>(nullptr, TEXT(“/Game/Animations/Contextual/CA_Grab.CA_Grab”));
    if (!InteractionAsset) return;

    TMap<FName, AActor*> Participants;
    // “Attacker” 和 “Victim” 是在 InteractionAsset 中定义的角色名称
    Participants.Add(FName(“Attacker”), this);
    Participants.Add(FName(“Victim”), OtherActor);

    ContextualAnimComp->StartContextualAnimScene(InteractionAsset, Participants);
}
```

## 模块依赖

该插件本身依赖于两个外部插件，你的项目也必须启用它们才能使用 ContextualAnimation。

| 模块 | 用途 |
|---|---|
| `MotionWarping` | 核心依赖。用于在动画播放期间实现根运动偏移，以实现精确的位移和对齐。 |
| `IKRig` | 用于支持动画中的反向运动学目标（IK Target），例如让角色的手准确抓住某个点。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志系统宏迁移更新。 |
| 2026-04-06 | `76545631` | [CAS] Override Support for CAS Actors | 为上下文动画场景中的演员添加了覆盖支持功能。 |
| 2026-03-27 | `5c7c61e7` | Contextual Anim Editor: | 上下文动画编辑器相关更新。 |
| 2026-03-11 | `4f7e0527` | Contextual Anim Editor - Added warning message to validate that a preview actor class has a Contextu... | 编辑器增加了验证预览演员类是否包含所需组件的警告。 |
| 2026-03-11 | `9d29e89e` | Contextual Anim - Added option to let the system find ideal start time for the interaction based on ... | 为交互系统增加了基于条件自动寻找理想开始时间的选项。 |

### 维护评价

**状态：实验性，但持续维护中**

该插件自 2021 年创建，标记为 **实验性 (IsExperimentalVersion=true)** 且默认不启用，表明 Epic 可能仍在评估其稳定性和最终设计。然而，从 git 记录看，它在 2026 年仍有实质性更新（功能新增、编辑器增强、底层系统改进），这表明它仍在**积极维护**。

**优势**：
1.  解决了多人精确动画协调的复杂问题。
2.  与 MotionWarping、IKRig 深度集成，技术栈现代且强大。
3.  编辑器工具（自定义 EdMode， Sequencer 集成）完整，方便美术和设计师使用。

**风险与限制**：
1.  **实验性标签**：API 和功能在未来版本中可能发生不兼容的改动。
2.  **复杂性**：相比播放单个 Montage，学习曲线较陡峭，需要理解场景、角色、动画集合、选择标准等概念。
3.  **依赖**：必须同步启用 MotionWarping 和 IKRig 插件。

**推荐**：如果你的项目需要高质量、动态的多人动画交互（例如动作游戏），并且愿意承担未来 API 可能调整的风险，这个插件是非常强大且值得尝试的工具。对于原型开发或对动画精度要求不高的项目，使用标准的 Montage 和 AnimNotify 可能更简单直接。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/ContextualAnimation)
- [官方文档]()（无）