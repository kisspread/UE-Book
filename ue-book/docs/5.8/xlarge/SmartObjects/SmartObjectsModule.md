# Smart Objects

> Support for ambient life populating the game world（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 智能对象系统 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资源，调试渲染，示例资产） |
| 模块 | `SmartObjectsModule` (Runtime), `SmartObjectsEditorModule` (Runtime), `SmartObjectsTestSuite` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-09-28 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/SmartObjects) | |

## 用途

Smart Objects 系统是 UE5 中用于管理游戏世界中“可交互点”的核心框架。它解决的核心问题是：**如何让 AI 角色（或任何游戏实体）高效地发现、预约并使用场景中的特定位置或物体（如座位、武器架、工作站、载具、可拾取物品等），并管理整个交互生命周期。**

它不仅仅是一个空间查询系统，更是一个完整的交互点管理系统。它通过以下方式工作：
1.  **定义交互点**：使用 `USmartObjectDefinition` 数据资产来定义“智能对象”（如一把椅子）包含哪些可用的“槽位”（如座位），每个槽位的属性（如活动标签、使用条件）、行为定义（如坐下动画蓝图）以及进入点。
2.  **注册与管理**：在游戏世界中放置带有 `USmartObjectComponent` 的 Actor，该组件会引用一个定义资产。系统会在运行时将这些交互点注册到 `USmartObjectSubsystem` 子系统中，进行空间索引和管理。
3.  **查询与预约**：AI 控制器或任何实体可以通过子系统提供的查询接口（如 `FindSmartObjects`），根据位置、标签、条件等查找合适的交互槽位。
4.  **占用与状态管理**：查询到槽位后，可以通过“声明”（Claim）进行预约，防止其他实体抢占，然后“占用”（Occupy）开始交互，最后“释放”（Release）完成交互。系统严格管理槽位的状态（空闲、已声明、已占用）。

它的存在是为了在复杂的游戏世界中，为大量 AI 实体提供一个标准化、高效且可扩展的交互管理方案，避免在 AI 行为树或蓝图中硬编码复杂的交互逻辑。

## 使用场景

- **AI 生态系统**：让 NPC 能够自主寻找并使用世界中的物体，例如：市民找座位、士兵找掩体、工匠找工作站。
- **开放世界游戏**：管理成百上千个分散的交互点（如采集点、任务板、储物柜），确保玩家和 AI 能正确互动。
- **多人游戏**：在服务器上权威地管理交互点的占用状态，防止冲突。
- **场景逻辑**：基于标签和条件系统，触发与特定物体相关的游戏事件（如“找到一份报纸”、“使用控制台”）。

## 蓝图用法

蓝图 API 主要通过 `USmartObjectBlueprintFunctionLibrary` 暴露，节点清晰分组。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddSmartObject` / `RemoveSmartObject` | 将一个包含 SmartObjectComponent 的 Actor 注册到/从仿真中移除。移除会中断进行中的交互。 | `USmartObjectBlueprintFunctionLibrary` |
| `SetSmartObjectEnabled` | 使能/禁用一个智能对象。禁用不会中断当前交互，但会阻止新的查询。 | `USmartObjectBlueprintFunctionLibrary` |
| `FindSmartObjects` | 核心查询节点。在一个盒形区域内查找符合过滤器（如用户标签、行为定义）的可用智能对象槽位。 | `USmartObjectSubsystem` |
| `MarkSmartObjectSlotAsClaimed` | 将一个空闲的槽位声明为“已声明”，返回一个 `ClaimHandle`。 | `USmartObjectBlueprintFunctionLibrary` |
| `MarkSmartObjectSlotAsOccupied` | 将已声明的槽位标记为“已占用”，并获取其行为定义（例如用于播放特定动画的蓝图类）。 | `USmartObjectBlueprintFunctionLibrary` |
| `MarkSmartObjectSlotAsFree` | 释放一个已声明或已占用的槽位，使其可再次被查询。 | `USmartObjectBlueprintFunctionLibrary` |
| `GetSlotEntranceOffsetAndRotation` | 获取槽位特定进入点的偏移和旋转，用于导航。 | `USmartObjectBlueprintFunctionLibrary` |
| `Is Valid (Smart Object Claim Handle)` / `Is Valid (Smart Object Handle)` | 检查各类句柄是否有效。 | `USmartObjectBlueprintFunctionLibrary` |

### 使用示例（蓝图描述）

假设一个 AI 角色需要找一个座位坐下：
1.  **创建请求**：使用 `Make FSmartObjectRequest` 节点，设置一个查询盒（通常基于AI当前位置）和一个过滤器（例如，过滤器中的 `ActivityRequirements` 设为 “Seat” 标签）。
2.  **执行查询**：将请求连到 `FindSmartObjects` 节点。输出一个 `Results` 数组。
3.  **选择结果**：从 `Results` 数组中选择一个（例如第一个 `Result`）。
4.  **声明槽位**：将 `Result` 中的 `SlotHandle` 和当前 AI Actor 连到 `MarkSmartObjectSlotAsClaimed` 节点，获得一个 `ClaimHandle`。
5.  **占用并获取行为**：将 `ClaimHandle` 连到 `MarkSmartObjectSlotAsOccupied`，并提供你期望的 `DefinitionClass`（例如 `USmartObjectBehaviorDefinition` 的子类），获取具体的行为定义对象，进而驱动 AI 的动画或逻辑。
6.  **释放**：交互完成后，使用 `MarkSmartObjectSlotAsFree` 释放 `ClaimHandle`。

## C++ 用法

C++ API 提供了更高效和底层的控制，核心类是 `USmartObjectSubsystem`。

### 头文件引入

```cpp
#include “SmartObjectSubsystem.h”
#include “SmartObjectTypes.h”
#include “SmartObjectRequestTypes.h”
#include “SmartObjectRuntime.h”
```

### 基本用法

以下代码演示了基本的查询和占用流程：

```cpp
// 获取子系统（确保在有效的UWorld上下文中）
USmartObjectSubsystem* SOSubsystem = UWorld::GetSubsystem<USmartObjectSubsystem>(GetWorld());
if (!SOSubsystem) return;

// 构造查询过滤器
FSmartObjectRequestFilter Filter;
Filter.ActivityRequirements = FGameplayTagQuery::MakeQuery_MatchAllTags(FGameplayTagContainer::CreateFromArray(TArray<FGameplayTag>{FGameplayTag(“Activity.Sit”)}));
Filter.bShouldEvaluateConditions = true; // 评估槽位和对象的前置条件

// 构造查询请求（在AI周围搜索）
FBox QueryBox = FBox(EForceInit::ForceInitToZero).ExpandBy(FVector(500.0f)).TranslateBy(GetActorLocation());
FSmartObjectRequest Request(QueryBox, Filter);

// 执行查询
TArray<FSmartObjectRequestResult> Results;
if (SOSubsystem->FindSmartObjects(Request, Results, FConstStructView()))
{
    // 选择第一个有效结果
    FSmartObjectRequestResult SelectedResult = Results[0];
    
    // 声明槽位
    FSmartObjectClaimHandle ClaimHandle = SOSubsystem->MarkSlotAsClaimed(SelectedResult.SlotHandle, this, ESmartObjectClaimPriority::Normal);
    if (ClaimHandle.IsValid())
    {
        // 占用槽位并获取行为定义
        const USmartObjectBehaviorDefinition* BehaviorDef = SOSubsystem->MarkSlotAsOccupied(ClaimHandle, USmartObjectBehaviorDefinition::StaticClass());
        if (BehaviorDef)
        {
            // 使用行为定义... (例如，获取动画资产或逻辑)
        }
        
        // ... 一段时间后，交互完成 ...
        
        // 释放槽位
        SOSubsystem->MarkSlotAsFree(ClaimHandle);
    }
}
```

### 进阶用法

C++ 允许更精细的控制，例如：
- **多线程支持**：子系统通过编译开关 `WITH_SMARTOBJECT_MT_INSTANCE_LOCK` 支持线程安全的实例访问（非查询线程安全）。
- **自定义条件**：继承 `FSmartObjectWorldConditionBase` 并在定义资产中设置，实现基于游戏状态的复杂过滤。
- **自定义空间分区**：继承 `USmartObjectSpacePartition`（默认提供八叉树和网格哈希）。
- **程序化创建智能对象**：使用 `CreateSmartObject` 动态生成运行时智能对象实例。

## Demo 示例

一个最小可运行的示例，展示如何创建并查询一个智能对象。

```cpp
// MyActor.h
#pragma once
#include “CoreMinimal.h”
#include “GameFramework/Actor.h”
#include “MyActor.generated.h”

class USmartObjectComponent;
class USmartObjectDefinition;

UCLASS()
class AMyActor : public AActor
{
    GENERATED_BODY()
public:
    AMyActor();

    virtual void BeginPlay() override;

    UFUNCTION(BlueprintCallable)
    void TestSmartObjectQuery();

protected:
    UPROPERTY(VisibleAnywhere)
    TObjectPtr<USmartObjectComponent> SmartObjectComp;

    UPROPERTY(EditAnywhere)
    TObjectPtr<USmartObjectDefinition> SmartObjectDefinition;
};
```

```cpp
// MyActor.cpp
#include “MyActor.h”
#include “SmartObjectSubsystem.h”
#include “SmartObjectComponent.h”
#include “SmartObjectDefinition.h”
#include “SmartObjectRuntime.h”

AMyActor::AMyActor()
{
    SmartObjectComp = CreateDefaultSubobject<USmartObjectComponent>(TEXT(“SmartObjectComp”));
    RootComponent = SmartObjectComp;
}

void AMyActor::BeginPlay()
{
    Super::BeginPlay();
    if (SmartObjectDefinition)
    {
        SmartObjectComp->SetDefinition(SmartObjectDefinition);
    }
}

void AMyActor::TestSmartObjectQuery()
{
    USmartObjectSubsystem* Subsystem = GetWorld()->GetSubsystem<USmartObjectSubsystem>();
    if (!Subsystem) return;

    // 1. 查询当前Actor拥有的所有槽位
    TArray<FSmartObjectSlotHandle> Slots;
    Subsystem->GetAllSlots(SmartObjectComp->GetRegisteredHandle(), Slots);

    if (Slots.Num() > 0)
    {
        // 2. 声明第一个槽位
        FSmartObjectClaimHandle ClaimHandle = Subsystem->MarkSlotAsClaimed(Slots[0], this);
        if (ClaimHandle.IsValid())
        {
            UE_LOG(LogTemp, Log, TEXT(“Successfully claimed slot on smart object: %s”), *ClaimHandle.SmartObjectHandle.ToString());

            // 3. 立即释放（演示）
            Subsystem->MarkSlotAsFree(ClaimHandle);
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GameplayTags` | 核心依赖，用于基于标签的查询、过滤和分类。 |
| `WorldConditions` | 用于评估槽位和对象的前置条件。 |
| `TargetingSystem` | `FindSmartObjectsInTargetingRequest` 函数用于在目标系统的结果中查找智能对象。 |
| `MassEntity` | 子系统被特化支持 Mass 框架，允许大量 AI 实体高效查询。 |
| `GameplayBehaviors` | （可选）常用于定义智能对象触发的具体行为逻辑。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移到新的 UE_LOGF 格式。 |
| 2026-04-13 | `f10a2daf` | [ContentBrowser] New Add Menu AI Menu | 在内容浏览器的“添加”菜单中新增“AI”子菜单。 |
| 2026-04-01 | `58888966` | [MassCore] Move headers to Public/Mass/ subdirectory, strip Mass prefix from filenames | 重构 Mass 模块头文件目录结构，移除文件名前缀。 |
| 2026-03-31 | `d7c5497a` | [SmartObjects][Debug] Three-level debug rejection tracking in FindSlotsInternal and FindMatchingSlot | 为智能对象的查询调试添加三级拒绝跟踪功能，便于定位问题。 |
| 2026-03-30 | `161605b0` | [Mass] Extract MassCore module from MassEntity | 从 MassEntity 模块中分离出 MassCore 模块。 |

### 维护评价

**综合评价：活跃维护中的核心系统。**

- **创建时间**：约 4 年前（2021年），是 UE5 的早期组件，成熟度高。
- **最近更新**：近期（2026年3-4月）仍有实质性更新，包括功能增强（调试跟踪）、代码重构（日志、模块结构）和与新系统（Mass、ContentBrowser AI 菜单）的集成。这表明它仍在被 Epic Games 积极使用和维护。
- **活跃度**：非常活跃，是支撑 UE5 AI 生态和 Mass 框架的关键基础设施。
- **已知限制**：子系统本身不是线程安全的（查询需在游戏线程），但提供了有限的多线程实例操作支持。功能非常丰富，学习曲线相对陡峭。
- **推荐使用**：强烈推荐。对于任何需要标准化、可扩展智能交互管理的项目，Smart Objects 是官方提供的、功能完备且持续维护的最佳解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/SmartObjects)
- [官方文档]()（无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/SmartObjects/Source/SmartObjectsTestSuite)