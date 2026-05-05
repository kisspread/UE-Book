# Smart Objects

> Support for ambient life populating the game world

| 属性 | 值 |
|---|---|
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、测试资源） |
| 模块 | `SmartObjectsModule` (Runtime), `SmartObjectsEditorModule` (Runtime), `SmartObjectsTestSuite` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-09-28 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/SmartObjects) | |

## 用途

Smart Objects 插件为游戏世界中的物体提供了一个标准化的框架，使其能够被 AI 角色（或玩家）识别和交互。它解决的核心问题是：如何让游戏世界中的物体（如椅子、门、工作台、武器架）能够被 AI 系统动态地发现、评估和使用，而无需为每个物体编写硬编码的交互逻辑。

插件通过“智能对象”（Smart Object）的概念，将物体的交互能力（如“可坐”、“可开门”、“可拾取”）抽象为可配置的定义（Definition）和行为（Behavior）。AI 角色通过查询“智能对象子系统”（SmartObjectSubsystem）来寻找附近可用的交互点，并根据自身需求（如“需要休息”、“需要武器”）选择最合适的对象进行交互。这使得 AI 的行为更加动态和环境感知，是构建沉浸式开放世界或复杂 AI 系统的关键基础设施。

## 使用场景

- **开放世界游戏**：让 NPC 能够自主寻找并使用世界中的长椅休息、在酒吧吧台喝酒、在铁匠铺工作等。
- **角色扮演游戏 (RPG)**：玩家或同伴角色可以与场景中的各种物体（宝箱、祭坛、书架）进行标准化交互。
- **模拟经营类游戏**：顾客 AI 能够自动寻找并使用店内的设施（收银台、货架、试衣间）。
- **任何需要 AI 与环境进行标准化交互的游戏**：避免为每个可交互物体编写特定的 AI 行为树或黑板逻辑。

## 蓝图用法

由于 Smart Objects 主要是一个底层框架，其蓝图 API 侧重于配置和查询。核心节点通常通过 `SmartObjectSubsystem` 访问。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Find Smart Objects for Actor` | 为指定的 Actor 查找附近可用的智能对象。 | `USmartObjectSubsystem` |
| `Find Smart Objects in Box` | 在指定的盒型区域内查找智能对象。 | `USmartObjectSubsystem` |
| `Claim Smart Object` | 为指定的 Actor 声明对某个智能对象槽位（Slot）的使用权。 | `USmartObjectSubsystem` |
| `Use Smart Object` | 通知子系统 Actor 开始使用已声明的智能对象。 | `USmartObjectSubsystem` |
| `Release Smart Object` | 释放 Actor 对智能对象槽位的占用。 | `USmartObjectSubsystem` |
| `Get Smart Object Component` | 从 Actor 身上获取其 `SmartObjectComponent`。 | `UBlueprintFunctionLibrary` |

### 使用示例（蓝图描述）

1.  **配置智能对象**：
    *   在场景中的一个 Actor（如一把椅子）上添加 `SmartObjectComponent`。
    *   在该组件的详情面板中，指定一个 `SmartObjectDefinition` 资产。该资产定义了交互点（槽位）的位置、旋转以及关联的行为（例如，一个 `SmartObjectBehaviorDefinition` 资产，描述了“坐下”这个行为）。

2.  **AI 查询与使用**：
    *   在 AI 的行为树或蓝图中，使用 `Find Smart Objects for Actor` 节点，传入 AI 的 Pawn 和所需的 `GameplayTag`（例如 `“Interaction.Sit”`）。
    *   节点会返回一个可用的智能对象列表。
    *   选择其中一个，调用 `Claim Smart Object` 节点进行声明。
    *   成功后，AI 移动到槽位位置，然后调用 `Use Smart Object` 节点。此时，与该智能对象关联的 `BehaviorDefinition` 会被触发（例如，播放坐下动画）。
    *   交互完成后，调用 `Release Smart Object` 释放占用。

## C++ 用法

### 头文件引入

```cpp
#include "SmartObjectSubsystem.h"
#include "SmartObjectComponent.h"
#include "SmartObjectDefinition.h"
```

### 基本用法

以下示例展示了如何在 C++ 中查询和使用智能对象。

```cpp
// 来源：基于 SmartObjectsTestSuite 中的测试逻辑推断
void AMyAIController::FindAndUseSmartObject()
{
    USmartObjectSubsystem* SmartObjectSubsystem = UWorld::GetSubsystem<USmartObjectSubsystem>(GetWorld());
    if (!SmartObjectSubsystem)
    {
        return;
    }

    // 1. 定义查询参数
    FSmartObjectRequestFilter Filter;
    // 可以设置所需的 GameplayTag，例如只寻找可坐下的对象
    // Filter.RequiredTags.AddTag(FGameplayTag::RequestGameplayTag(TEXT(“Interaction.Sit”)));

    FSmartObjectRequest Request;
    Request.Filter = &Filter;
    // 设置搜索范围，例如以 AI 为中心，半径 1000 单位
    Request.QueryBox = FBox(GetPawn()->GetActorLocation() - FVector(1000.f), GetPawn()->GetActorLocation() + FVector(1000.f));

    // 2. 执行查询
    TArray<FSmartObjectRequestResult> Results;
    SmartObjectSubsystem->FindSmartObjects(Request, Results);

    if (Results.Num() > 0)
    {
        // 3. 选择第一个结果并尝试声明
        const FSmartObjectRequestResult& Result = Results[0];
        FSmartObjectClaimHandle ClaimHandle = SmartObjectSubsystem->ClaimSmartObject(Result.SmartObjectHandle, GetPawn());

        if (ClaimHandle.IsValid())
        {
            // 4. 声明成功，移动到槽位并使用
            // ... 移动逻辑 ...
            // 移动完成后
            SmartObjectSubsystem->UseSmartObject(ClaimHandle);
        }
    }
}
```

### 进阶用法

自定义行为定义（Behavior Definition）是扩展插件功能的关键。你可以创建自己的 `USmartObjectBehaviorDefinition` 子类来定义独特的交互逻辑。

```cpp
// 来源：参考 SmartObjectsTestSuite/Public/SmartObjectTestTypes.h
// 1. 定义自定义行为数据（可选）
USTRUCT()
struct FMyCustomBehaviorData : public FSmartObjectDefinitionData
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere)
    float InteractionDuration = 2.0f;

    UPROPERTY(EditAnywhere)
    UAnimMontage* InteractionMontage = nullptr;
};

// 2. 定义自定义行为定义类
UCLASS()
class UMyCustomBehaviorDefinition : public USmartObjectBehaviorDefinition
{
    GENERATED_BODY()

public:
    // 当智能对象被使用时，此函数被调用
    virtual void Activate(FSmartObjectBehaviorContext& Context) const override
    {
        // 从 Context 中获取用户数据（例如 AI 控制器）
        AActor* User = Context.UserActor;
        // 获取关联的槽位数据
        const FSmartObjectSlotStateData* SlotData = Context.SlotStateData;
        // 获取定义数据
        const FMyCustomBehaviorData* MyData = Context.SmartObjectDefinition->GetDefinitionData<FMyCustomBehaviorData>();

        if (User && MyData)
        {
            // 执行自定义逻辑，例如播放动画、触发事件等
            UE_LOG(LogTemp, Log, TEXT(“%s is interacting with smart object for %f seconds.”), *User->GetName(), MyData->InteractionDuration);
        }
    }

    virtual void Deactivate(FSmartObjectBehaviorContext& Context) const override
    {
        // 交互结束时的清理逻辑
    }
};
```

## Demo 示例

一个最小的自定义行为定义示例。

**MySmartObjectBehavior.h**
```cpp
#pragma once

#include "SmartObjectBehaviorDefinition.h"
#include "MySmartObjectBehavior.generated.h"

UCLASS()
class UMySimpleBehaviorDefinition : public USmartObjectBehaviorDefinition
{
    GENERATED_BODY()

public:
    virtual void Activate(FSmartObjectBehaviorContext& Context) const override;
    virtual void Deactivate(FSmartObjectBehaviorContext& Context) const override;
};
```

**MySmartObjectBehavior.cpp**
```cpp
#include "MySmartObjectBehavior.h"

void UMySimpleBehaviorDefinition::Activate(FSmartObjectBehaviorContext& Context) const
{
    if (AActor* User = Context.UserActor)
    {
        UE_LOG(LogTemp, Warning, TEXT(“%s started using a simple smart object!”), *User->GetName());
        // 在这里添加你的交互开始逻辑，例如播放一个通用动画
    }
}

void UMySimpleBehaviorDefinition::Deactivate(FSmartObjectBehaviorContext& Context) const
{
    if (AActor* User = Context.UserActor)
    {
        UE_LOG(LogTemp, Warning, TEXT(“%s stopped using the simple smart object.”), *User->GetName());
        // 交互结束清理
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GameplayTags` | 用于通过标签系统对智能对象进行分类和查询（例如 `Interaction.Sit`）。 |
| `GameplayTasks` | 智能对象的使用过程可能被建模为一个任务（Task），与 AI 行为树集成。 |
| `AIModule` | AI 控制器和感知系统是智能对象的主要使用者。 |
| `NavigationSystem` | AI 角色移动到智能对象槽位时需要导航支持。 |

## 维护状态

### 近期更新

```
- a2e75189887d Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applied using UnrealCodeFixup using LyraEditor win64 development as target)
- 2739c3d30ebc Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types. Part 4/n
- 8b11c1f25df0 [SmartObject] misc updates to follow coding standard
```

### 维护评价

Smart Objects 插件创建于 2021 年，相对较新。从最近的提交记录看，最后一次实质性功能更新（`misc updates to follow coding standard`）发生在 2023 年初，之后主要是代码维护和格式修复（如添加 `UE_INLINE_GENERATED_CPP_BY_NAME` 和调整 DLL 导出标记）。这表明插件的核心功能已经稳定，目前处于**维护中**状态，没有重大的新功能开发，但仍在进行必要的代码维护以确保其与引擎版本的兼容性。

该插件是构建复杂 AI 环境交互的**推荐基础框架**。虽然默认未启用（`EnabledByDefault: false`），但其设计成熟，测试用例完整，适合在项目中集成和使用。需要注意的是，它是一个底层系统，需要与行为树、AI 控制器等上层系统配合使用才能发挥全部作用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/SmartObjects)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/SmartObjects/Source/SmartObjectsTestSuite)