# World Conditions

> General purpose cached conditions

| 属性 | 值 |
|---|---|
| 中文名 | 游戏条件评估系统 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资源、编辑器扩展） |
| 模块 | `WorldConditions` (Runtime), `WorldConditionsEditor` (Editor), `WorldConditionsTestSuite` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-11-16 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/WorldConditions) | |

## 用途

World Conditions 插件提供了一套通用的游戏条件（World Condition）评估框架。它解决的核心问题是：在游戏逻辑中频繁评估复杂条件组合时的性能开销。

该插件通过将条件查询的**定义**（`FWorldConditionQueryDefinition`）与运行时**状态**（`FWorldConditionQueryState`）分离，并引入**缓存**机制，实现了高效评估。条件评估的结果可以被缓存，仅当相关的上下文数据发生变化时才重新计算，从而避免了每帧或每次查询时都执行开销较大的条件逻辑。它支持构建基于各种上下文数据（如子系统、Actor、组件等）的布尔表达式，并将表达式求值过程优化到极致。

简而言之，它是一个为游戏逻辑（如 AI 决策、任务触发、环境状态检查等）提供高性能、可缓存、可组合条件判断的底层工具。

## 使用场景

- **任务系统/触发器**：你需要检查多个前置条件（如玩家等级、物品持有、世界状态）是否同时满足，来决定是否激活一个任务或触发器。
- **AI 决策**：AI 的行为树或决策系统需要频繁评估复杂的环境条件（如敌人距离、自身血量、掩体状态），且这些条件可能基于多个组件或子系统。
- **游戏规则**：你需要评估一组游戏规则（如回合结束条件、胜利条件），这些规则可能由多个玩家状态和世界事件组合而成。
- **UI 状态**：你需要根据玩家的状态和游戏世界的变化，动态地显示或隐藏 UI 元素（如技能可用性提示、任务目标列表）。

## 蓝图用法

### 核心节点

在蓝图中，主要通过 `FWorldConditionQueryDefinition` (蓝图中显示为 `World Condition Query Definition`) 来配置条件查询。此结构体是 `BlueprintType` 的，可以在蓝图编辑器中作为变量或属性进行编辑。运行时的激活、评估和停用则通过 C++ 接口或暴露的蓝图函数进行。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetSchemaClass` | 设置查询所使用的上下文数据模式（Schema） | `FWorldConditionQueryDefinition` |
| `AddCondition` | 向定义中添加一个条件 | `FWorldConditionQueryDefinition` (编辑器专用) |
| `Initialize` | 根据编辑器中的条件列表，构建运行时所需的共享定义 | `FWorldConditionQueryDefinition` |
| `Activate` | 激活查询，为条件分配状态并调用所有条件的 `Activate` | `FWorldConditionQuery` |
| `IsTrue` | 评估查询表达式的结果，利用缓存和数据变化驱动重评估 | `FWorldConditionQuery` |
| `Deactivate` | 停用查询，释放资源并调用条件的 `Deactivate` | `FWorldConditionQuery` |

### 使用示例（蓝图描述）

1.  **在蓝图类中**：定义一个 `FWorldConditionQueryDefinition` 类型的变量（例如 `PreconditionsDefinition`），并为其分配一个自定义的 `UWorldConditionSchema` 类。
2.  **在编辑器中**：选中该蓝图实例，在“详细信息”面板中找到 `PreconditionsDefinition` 属性。在 `EditableConditions` 数组中，添加你想要的条件，并设置 `Operator`（And/Or）和 `bInvert`。
3.  **在游戏逻辑中**（如 `BeginPlay` 或需要时）：调用 `PreconditionsDefinition.Initialize()`。
4.  **在需要检查时**：创建 `FWorldConditionQuery` 实例，并调用其 `Activate` 函数，传入所有者对象和符合 Schema 的上下文数据（`FWorldConditionContextData`）。随后，可以多次调用 `IsTrue` 进行高效评估。最后调用 `Deactivate`。

## C++ 用法

### 头文件引入

```cpp
#include "WorldConditionBase.h"
#include "WorldConditionQuery.h"
#include "WorldConditionSchema.h"
#include "WorldConditionTypes.h"
```

### 基本用法

**1. 定义自定义 Schema**

Schema 定义了可用的上下文数据和可用的条件类型。

```cpp
// MyGameWorldConditionSchema.h
#pragma once
#include "WorldConditionSchema.h"
#include "MyGameWorldConditionSchema.generated.h"

UCLASS()
class UMyGameWorldConditionSchema : public UWorldConditionSchema
{
    GENERATED_BODY()
public:
    UMyGameWorldConditionSchema(const FObjectInitializer& ObjectInitializer)
        : Super(ObjectInitializer)
    {
        // 定义可提供的上下文数据：一个 AActor* 类型的上下文数据，名为“Actor”，且数据在评估期间可能变化（Dynamic）
        ActorRef = AddContextDataDesc(TEXT("Actor"), AActor::StaticClass(), EWorldConditionContextDataType::Dynamic);
        // 定义另一个上下文数据：一个自定义的 FGameStats 结构体，数据在条件激活后保持不变（Persistent）
        StatsRef = AddContextDataDesc(TEXT("Stats"), TBaseStructure<FGameStats>::Get(), EWorldConditionContextDataType::Persistent);
    }

    // 便捷方法，方便在已知 Schema 的情况下设置上下文数据
    FWorldConditionContextDataRef GetActorRef() const { return ActorRef; }
    FWorldConditionContextDataRef GetStatsRef() const { return StatsRef; }

protected:
    // 可选：过滤允许在此 Schema 中使用的具体条件类型
    virtual bool IsStructAllowed(const UScriptStruct* InScriptStruct) const override
    {
        return Super::IsStructAllowed(InScriptStruct)
            || InScriptStruct->IsChildOf(FMyGameWorldConditionBase::StaticStruct());
    }

private:
    FWorldConditionContextDataRef ActorRef;
    FWorldConditionContextDataRef StatsRef;
};
```

**2. 定义自定义条件**

条件结构体必须继承自 `FWorldConditionBase` 或其子类。

```cpp
// MyGameWorldConditions.h
#pragma once
#include "WorldConditionBase.h"
#include "WorldConditionTypes.h"
#include "MyGameWorldConditions.generated.h"

// 基础条件，需要 Actor 上下文
USTRUCT()
struct FWorldCondition_HasTag : public FWorldConditionCommonActorBase
{
    GENERATED_BODY()

    FWorldCondition_HasTag()
    {
        bCanCacheResult = false; // 标签可能动态变化，不缓存结果
    }

    // 定义所需的状态（可选）
    struct FState
    {
        FGameplayTagContainer CachedTags;
        FDelegateHandle OnTagsChangedHandle;
    };
    using FStateType = FState;

    // 初始化时解析上下文数据引用
    virtual bool Initialize(const UWorldConditionSchema& Schema) override
    {
        if (!FWorldConditionBase::Initialize(Schema))
        {
            return false;
        }
        // 解析 ActorRef，它需要指向一个 AActor 类型的数据
        return Schema.ResolveContextDataRef<AActor>(ActorRef);
    }

    // 激活时，可以注册回调以在数据变化时使缓存失效
    virtual bool Activate(const FWorldConditionContext& Context) const override
    {
        FState& State = Context.GetState(*this);
        if (AActor* Actor = Context.GetMutableContextDataPtr<AActor>(ActorRef))
        {
            // 示例：如果 Actor 有 TagsChanged 委托，则注册以使查询缓存失效
            // FOnGameplayEffectTagsChanged* TagsDelegate = ...;
            // State.OnTagsChangedHandle = TagsDelegate->AddLambda([...InvalidationHandle = Context.GetInvalidationHandle(*this)]()
            // {
            //     InvalidationHandle.InvalidateResult();
            // });
            return true;
        }
        return false;
    }

    // 评估条件
    virtual FWorldConditionResult IsTrue(const FWorldConditionContext& Context) const override
    {
        if (AActor* Actor = Context.GetMutableContextDataPtr<AActor>(ActorRef))
        {
            const bool bHasTag = Actor->ActorHasTag(RequiredTag);
            // 返回结果，并指示此结果不应被缓存（因为我们在 Activate 中设置了 bCanCacheResult=false）
            return FWorldConditionResult(bHasTag ? EWorldConditionResult::IsTrue : EWorldConditionResult::IsFalse, false);
        }
        return FWorldConditionResult(EWorldConditionResult::IsFalse, false);
    }

    // 停用时，清理状态
    virtual void Deactivate(const FWorldConditionContext& Context) const override
    {
        // FState& State = Context.GetState(*this);
        // 清理注册的委托等...
    }

    // 条件的属性，在编辑器中可编辑
    UPROPERTY(EditAnywhere, Category="Default")
    FName RequiredTag;

    // 上下文数据引用，在 Initialize 中解析
    UPROPERTY()
    FWorldConditionContextDataRef ActorRef;
};
```

**3. 设置和使用查询**

```cpp
// 在某个游戏对象（如 PlayerController, Subsystem）中
#include "MyGameWorldConditionSchema.h"
#include "MyGameWorldConditions.h"

// ... 在类定义中 ...
UPROPERTY()
FWorldConditionQueryDefinition MyQueryDefinition;

UPROPERTY(Transient)
FWorldConditionQuery MyQuery;

// ... 初始化 ...
void AMyPlayerController::SetupConditions()
{
    // 1. 设置 Schema
    MyQueryDefinition.SetSchemaClass(UMyGameWorldConditionSchema::StaticClass());

    // 2. 添加条件（编辑器中，通常在 PostEditChangeProperty 或数据资产中完成）
    FWorldConditionEditable ConditionEdit;
    ConditionEdit.Condition.InitializeAs<FWorldCondition_HasTag>();
    auto& CondData = ConditionEdit.Condition.GetMutable<FWorldCondition_HasTag>();
    CondData.RequiredTag = TEXT("Player");
    MyQueryDefinition.AddCondition(ConditionEdit);

    // 3. 初始化定义，构建内部的共享数据
    MyQueryDefinition.Initialize(this);

    // 4. 激活查询（通常在需要时）
    UMyGameWorldConditionSchema* Schema = GetDefault<UMyGameWorldConditionSchema>();
    FWorldConditionContextData ContextData(*Schema);
    ContextData.SetContextData(Schema->GetActorRef(), this);
    // 设置其他上下文数据... ContextData.SetContextData(Schema->GetStatsRef(), &MyStats);

    if (MyQuery.Activate(*this, ContextData))
    {
        // 5. 评估结果
        bool bResult = MyQuery.IsTrue(ContextData);
        UE_LOG(LogTemp, Log, TEXT("Condition result: %s"), bResult ? TEXT("True") : TEXT("False"));
    }
}

// 6. 在不需要时停用
void AMyPlayerController::CleanupConditions()
{
    UMyGameWorldConditionSchema* Schema = GetDefault<UMyGameWorldConditionSchema>();
    FWorldConditionContextData ContextData(*Schema); // 可以复用或重新创建，停用时只关心 Schema
    MyQuery.Deactivate(ContextData);
}
```

### 进阶用法

使用带有状态（`FStateType` 或 `UStateType`）的条件，并利用 `FWorldConditionResultInvalidationHandle` 实现真正的按需缓存更新。

```cpp
// 在自定义条件的 Activate 中注册回调
bool FWorldCondition_HasTag::Activate(const FWorldConditionContext& Context) const
{
    FState& State = Context.GetState(*this);
    if (AActor* Actor = Context.GetMutableContextDataPtr<AActor>(ActorRef))
    {
        // 假设 Actor 有一个 TagsChangedEvent
        FGameplayTagContainer& ActorTags = State.CachedTags;
        ActorTags = Actor->GetOwnedGameplayTags(); // 缓存一次

        State.OnTagsChangedHandle = Actor->OnTagsChanged.AddLambda(
            [&State, InvalidationHandle = Context.GetInvalidationHandle(*this)]()
        {
            // 当标签变化时，使条件查询的缓存失效
            InvalidationHandle.InvalidateResult();
            UE_LOG(LogTemp, Verbose, TEXT("Tags changed, query cache invalidated."));
        });
        return true;
    }
    return false;
}
```

## Demo 示例

一个最小的、可编译的示例，演示如何定义一个检查 Actor 是否具有指定标签的条件，并使用查询进行评估。

```cpp
// DemoWorldCondition.h
#pragma once
#include "CoreMinimal.h"
#include "WorldConditionBase.h"
#include "WorldConditionSchema.h"
#include "GameplayTagContainer.h"
#include "DemoWorldCondition.generated.h"

// 1. 定义 Schema
UCLASS()
class UDemoConditionSchema : public UWorldConditionSchema
{
    GENERATED_BODY()
public:
    UDemoConditionSchema(const FObjectInitializer& ObjectInitializer)
        : Super(ObjectInitializer)
    {
        ActorRef = AddContextDataDesc(TEXT("Actor"), AActor::StaticClass(), EWorldConditionContextDataType::Dynamic);
    }
    FWorldConditionContextDataRef GetActorRef() const { return ActorRef; }
private:
    FWorldConditionContextDataRef ActorRef;
};

// 2. 定义条件
USTRUCT()
struct FWorldCondition_DemoHasTag : public FWorldConditionCommonActorBase
{
    GENERATED_BODY()

    virtual bool Initialize(const UWorldConditionSchema& Schema) override
    {
        if (!FWorldConditionBase::Initialize(Schema))
        {
            return false;
        }
        return Schema.ResolveContextDataRef<AActor>(ActorRef);
    }

    virtual FWorldConditionResult IsTrue(const FWorldConditionContext& Context) const override
    {
        if (const AActor* Actor = Context.GetContextDataPtr<AActor>(ActorRef))
        {
            const bool bHasTag = Actor->ActorHasTag(TagToCheck);
            return FWorldConditionResult(
                bHasTag ? EWorldConditionResultValue::IsTrue : EWorldConditionResultValue::IsFalse,
                bCanCacheResult // 使用基类的缓存设置
            );
        }
        return FWorldConditionResult(EWorldConditionResultValue::IsFalse, false);
    }

    UPROPERTY(EditAnywhere, Category="Condition")
    FName TagToCheck;

    UPROPERTY()
    FWorldConditionContextDataRef ActorRef;
};
```

```cpp
// DemoWorldConditionSubsystem.h
#pragma once
#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "WorldConditionQuery.h"
#include "DemoWorldConditionSubsystem.generated.h"

UCLASS()
class UDemoWorldConditionSubsystem : public UWorldSubsystem
{
    GENERATED_BODY()
public:
    void TestConditions(AActor* TestActor);

private:
    UPROPERTY()
    FWorldConditionQueryDefinition TestQueryDef;

    FWorldConditionQuery TestQuery;
};
```

```cpp
// DemoWorldConditionSubsystem.cpp
#include "DemoWorldConditionSubsystem.h"
#include "DemoWorldCondition.h"

void UDemoWorldConditionSubsystem::TestConditions(AActor* TestActor)
{
    if (!TestActor) return;

    // 设置定义
    TestQueryDef.SetSchemaClass(UDemoConditionSchema::StaticClass());

    FWorldConditionEditable EditCond;
    EditCond.Condition.InitializeAs<FWorldCondition_DemoHasTag>();
    auto& Cond = EditCond.Condition.GetMutable<FWorldCondition_DemoHasTag>();
    Cond.TagToCheck = TEXT("Important");
    TestQueryDef.AddCondition(EditCond);

    if (!TestQueryDef.Initialize(this))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to initialize query definition."));
        return;
    }

    // 设置上下文并激活
    const UDemoConditionSchema* Schema = GetDefault<UDemoConditionSchema>();
    FWorldConditionContextData ContextData(*Schema);
    ContextData.SetContextData(Schema->GetActorRef(), TestActor);

    if (TestQuery.Activate(*this, ContextData))
    {
        // 评估
        const bool bResult = TestQuery.IsTrue(ContextData);
        UE_LOG(LogTemp, Log, TEXT("Actor '%s' has tag 'Important': %s"),
            *TestActor->GetName(), bResult ? TEXT("YES") : TEXT("NO"));

        // 停用
        TestQuery.Deactivate(ContextData);
    }
}
```

## 模块依赖

从 `.uplugin` 文件可见，本插件有一个外部插件依赖。

| 模块 | 用途 |
|---|---|
| `PropertyBindingUtils` | 提供属性路径解析和绑定的工具类，被 WorldConditions 内部使用，以支持在编辑器中引用对象属性。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-28 | `cfaec1a0` | [WorldConditions] Build SharedDefinition before serialize so name harvest matches write | 修复序列化问题，确保共享定义在序列化前构建完毕，使名称收集与写入匹配。 |
| 2026-04-23 | `f49c6ff0` | [WorldConditions][Stability] Do not dereference Owner during GC in FWorldConditionQueryState destruc | **稳定性修复**：在 FWorldConditionQueryState 析构函数中避免在垃圾回收期间解引用 Owner，防止崩溃。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将内部日志宏从 UE_LOG 迁移到更现代的 UE_LOGF。 |
| 2026-03-24 | `2da4cdac` | [AI][WorldConditions] Add WorldConditionsToolset plugin for MCP inspection | 添加了用于 MCP (Model Context Protocol) 检查的 WorldConditionsToolset 插件。 |
| 2026-03-10 | `ba65d06d` | [WorldCondition] fixed case where world condition queries would not be properly linked when embedded | 修复了嵌入式世界条件查询可能无法正确链接的问题。 |

### 维护评价

WorldConditions 插件处于**活跃维护**状态。

- **创建时间**：约 3 年，属于较新的功能模块。
- **维护频率**：近 2 个月内有 5 次提交，更新频繁，且包含重要的稳定性修复和功能增强。
- **功能状态**：标记为实验性 (`IsExperimentalVersion: true`)，且默认未启用 (`EnabledByDefault: false`)。这意味着它尚未被视为最终稳定 API，接口可能发生变化，但由 Epic Games 核心团队积极开发和迭代。
- **结论**：这是一个**性能关键、设计先进但仍在演进中**的系统。推荐在新项目中尝试使用，但需做好跟随版本更新和 API 变动的准备。对于生产环境，建议密切关注其版本更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/WorldConditions)
- [官方文档]()
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/WorldConditions/Source/WorldConditionsTestSuite)