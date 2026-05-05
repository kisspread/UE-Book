# World Conditions

> General purpose cached conditions

| 属性 | 值 |
|---|---|
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器自定义 Property Editor） |
| 模块 | `WorldConditions` (Runtime), `WorldConditionsEditor` (Editor), `WorldConditionsTestSuite` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-11-15 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/WorldConditions) | |

## 用途

World Conditions 是一个通用的、支持缓存的条件表达式求值系统。它解决的核心问题是：**在游戏运行时，如何高效地组合和求值一组条件（conditions），并自动缓存那些不会频繁变化的结果**。

这个插件常被其他系统（如 Smart Objects、Gameplay Ability System 等）用来定义前置条件（preconditions）。例如："当玩家在附近 **且** 拥有某个物品 **且** 任务未完成时，才能与 Smart Object 交互"。

核心设计思路：
- **Definition（定义）** 是"常量"部分，可以存储在资产中
- **State（状态）** 是运行时实例数据，包含缓存和临时状态
- **Schema（模式）** 定义了某个使用场景下可用的上下文数据和条件类型
- **Context Data（上下文数据）** 是条件求值时可访问的输入数据，分为 Dynamic（每次调用可能变化）和 Persistent（生命周期内不变）两种

这种 Definition/State 分离的设计使得多个实例可以共享同一份定义，只需分配少量运行时内存。

## 使用场景

- 你在做 AI 决策系统，需要一组可复用的前置条件 → 用 World Conditions
- 你在做 Smart Object 交互，需要定义"什么时候可以使用" → 用 World Conditions（这是该插件目前最主要的消费者）
- 你需要条件表达式支持 AND/OR/NOT 和括号分组 → World Conditions 内置表达式求值器
- 你需要条件结果缓存（基于 Persistent 上下文数据的条件结果不会重复计算）→ World Conditions 自动处理
- 你需要条件的热修复（Hotfix）支持 → World Conditions 的序列化设计支持从文本导入条件更新

## 蓝图用法

World Conditions 主要是一个 C++ 框架，编辑器端提供 Property Editor 自定义界面来可视化编辑条件表达式。没有暴露 BlueprintCallable 节点。

在编辑器中使用时：
1. 在包含 `FWorldConditionQueryDefinition` 的属性上，编辑器会显示一个条件列表 UI
2. 每个条件可以选择类型、设置 AND/OR 操作符、设置表达式深度（括号分组）、是否取反
3. 表达式会以 `IF ([A] OR [B]) AND (([C] AND [D]) OR [E])` 的形式显示描述

## C++ 用法

### 头文件引入

```cpp
#include "WorldConditionBase.h"
#include "WorldConditionQuery.h"
#include "WorldConditionContext.h"
#include "WorldConditionSchema.h"
#include "WorldConditionTypes.h"
```

### 基本用法：定义 Schema

Schema 定义了你的使用场景中可用的上下文数据和允许的条件类型。

```cpp
// 来源: WorldConditionsTestTypes.h
UCLASS()
class UMyWorldConditionSchema : public UWorldConditionSchema
{
    GENERATED_BODY()
public:
    explicit UMyWorldConditionSchema(const FObjectInitializer& ObjectInitializer)
        : Super(ObjectInitializer)
    {
        // 注册上下文数据：Actor（Persistent，生命周期内不变）
        ActorRef = AddContextDataDesc(TEXT("Actor"), AActor::StaticClass(), EWorldConditionContextDataType::Persistent);
        // 注册上下文数据：Value（Dynamic，每次求值可能变化）
        ValueRef = AddContextDataDesc(TEXT("Value"), FMyData::StaticStruct(), EWorldConditionContextDataType::Dynamic);
    }

    // 过滤允许使用的条件类型
    virtual bool IsStructAllowed(const UScriptStruct* InScriptStruct) const override
    {
        return InScriptStruct && InScriptStruct->IsChildOf(TBaseStructure<FWorldConditionBase>::Get());
    }

    FWorldConditionContextDataRef GetActorRef() const { return ActorRef; }
    FWorldConditionContextDataRef GetValueRef() const { return ValueRef; }

private:
    FWorldConditionContextDataRef ActorRef;
    FWorldConditionContextDataRef ValueRef;
};
```

### 基本用法：定义条件

```cpp
// 来源: WorldConditionTestTypes.h
USTRUCT(meta=(Hidden))
struct FMyWorldCondition : public FWorldConditionBase
{
    GENERATED_BODY()

    // 条件需要的运行时状态类型（无状态则返回 nullptr）
    virtual TObjectPtr<const UStruct>* GetRuntimeStateType() const override { return nullptr; }

    // 初始化时解析 Schema 中的上下文数据引用
    virtual bool Initialize(const UWorldConditionSchema& Schema) override
    {
        const UMyWorldConditionSchema* MySchema = Cast<UMyWorldConditionSchema>(&Schema);
        if (MySchema == nullptr) return false;

        ValueRef = MySchema->GetValueRef();
        bCanCacheResult = false; // Dynamic 数据不可缓存
        return true;
    }

    virtual bool Activate(const FWorldConditionContext& Context) const override
    {
        return true; // 激活成功
    }

    // 核心求值逻辑
    virtual FWorldConditionResult IsTrue(const FWorldConditionContext& Context) const override
    {
        FWorldConditionResult Result(EWorldConditionResultValue::IsFalse, bCanCacheResult);
        if (const FMyData* Data = Context.GetContextDataPtr<FMyData>(ValueRef))
        {
            if (Data->Value == ExpectedValue)
            {
                Result.Value = EWorldConditionResultValue::IsTrue;
            }
        }
        return Result;
    }

    virtual void Deactivate(const FWorldConditionContext& Context) const override {}

    virtual FText GetDescription() const override
    {
        return FText::Format(FText::FromString(TEXT("Value == {0}")), FText::AsNumber(ExpectedValue));
    }

protected:
    FWorldConditionContextDataRef ValueRef;
    int32 ExpectedValue = 0;
};
```

### 基本用法：使用 FWorldConditionQuery（最简方式）

```cpp
// 来源: WorldConditionsTest.cpp (FWorldConditionTest_Eval)
FWorldConditionQuery Query;

// 初始化查询（编辑器环境用 DebugInitialize）
Query.DebugInitialize(nullptr, UMyWorldConditionSchema::StaticClass(),
    {
        FWorldConditionEditable(0, EWorldConditionOperator::Copy, FConstStructView::Make(FMyWorldCondition(1))),
        FWorldConditionEditable(0, EWorldConditionOperator::And, FConstStructView::Make(FMyWorldCondition(1)))
    });

// 准备上下文数据
FMyData TestData(1);
const UMyWorldConditionSchema* Schema = GetDefault<UMyWorldConditionSchema>();
FWorldConditionContextData ContextData(*Schema);
ContextData.SetContextData(Schema->GetValueRef(), &TestData);

// 激活 → 求值 → 停用
Query.Activate(GetWorld(), ContextData);
bool bResult = Query.IsTrue(ContextData);  // true
Query.Deactivate(ContextData);
```

### 进阶用法：带缓存的条件（Persistent 数据 + 失效回调）

```cpp
// 来源: WorldConditionTestTypes.h (FWorldConditionTestCached)
// 条件带有运行时状态（FStateType），用于存储委托句柄
USTRUCT()
struct FMyCachedConditionState
{
    GENERATED_BODY()
    FDelegateHandle DelegateHandle;
};

USTRUCT()
struct FMyCachedCondition : public FWorldConditionBase
{
    GENERATED_BODY()

    using FStateType = FMyCachedConditionState;

    virtual TObjectPtr<const UStruct>* GetRuntimeStateType() const override
    {
        static TObjectPtr<const UStruct> Ptr{FStateType::StaticStruct()};
        return &Ptr;
    }

    virtual bool Initialize(const UWorldConditionSchema& Schema) override
    {
        // ...
        // 根据上下文数据类型决定是否可以缓存
        bCanCacheResult = Schema.GetContextDataTypeByRef(ValueRef) == EWorldConditionContextDataType::Persistent;
        return true;
    }

    virtual bool Activate(const FWorldConditionContext& Context) const override
    {
        if (Context.GetContextDataType(ValueRef) == EWorldConditionContextDataType::Persistent)
        {
            if (const FMyData* Data = Context.GetContextDataPtr<FMyData>(ValueRef))
            {
                FStateType& State = Context.GetState(*this);
                FMyData* MutableData = const_cast<FMyData*>(Data);

                // 注册失效回调：当数据变化时，使缓存结果失效
                State.DelegateHandle = MutableData->OnChanged.AddLambda(
                    [InvalidationHandle = Context.GetInvalidationHandle(*this)]()
                    {
                        InvalidationHandle.InvalidateResult();
                    });
                return true;
            }
            return false;
        }
        return true;
    }

    virtual FWorldConditionResult IsTrue(const FWorldConditionContext& Context) const override
    {
        FStateType& State = Context.GetState(*this);
        // 只有成功注册了回调才允许缓存
        const bool bResultCanBeCached = State.DelegateHandle.IsValid();
        FWorldConditionResult Result(EWorldConditionResultValue::IsFalse, bResultCanBeCached);
        // ...
        return Result;
    }

    virtual void Deactivate(const FWorldConditionContext& Context) const override
    {
        FStateType& State = Context.GetState(*this);
        if (State.DelegateHandle.IsValid())
        {
            if (const FMyData* Data = Context.GetContextDataPtr<FMyData>(ValueRef))
            {
                const_cast<FMyData*>(Data)->OnChanged.Remove(State.DelegateHandle);
                State.DelegateHandle.Reset();
            }
        }
    }

protected:
    FWorldConditionContextDataRef ValueRef;
};
```

### 进阶用法：复杂表达式（括号分组）

```cpp
// 来源: WorldConditionsTest.cpp (FWorldConditionTest_EvalComplex)
// 表达式: IF (A OR B) AND ((C AND D) OR E)
Query.DebugInitialize(nullptr, UMyWorldConditionSchema::StaticClass(),
    {
        FWorldConditionEditable(/*Depth*/0, EWorldConditionOperator::Copy, FConstStructView::Make(FConditionA)),  // IF  (A
        FWorldConditionEditable(/*Depth*/1, EWorldConditionOperator::Or,   FConstStructView::Make(FConditionB)),  //  .   OR B)
        FWorldConditionEditable(/*Depth*/0, EWorldConditionOperator::And,  FConstStructView::Make(FConditionC)),  //  AND ( (C
        FWorldConditionEditable(/*Depth*/2, EWorldConditionOperator::And,  FConstStructView::Make(FConditionD)),  //  .   .   AND D)
        FWorldConditionEditable(/*Depth*/1, EWorldConditionOperator::Or,   FConstStructView::Make(FConditionE)),  //  .   OR E)
    });
```

`ExpressionDepth` 控制括号层级（最大深度为 4）。深度递增表示开括号，递减表示闭括号。

### 进阶用法：分离 Definition 和 State

对于需要多个实例共享定义的场景，可以手动分离 Definition 和 State：

```cpp
// 定义存储在资产/组件中
UPROPERTY()
FWorldConditionQueryDefinition QueryDefinition;

// 每个实例有自己的 State
FWorldConditionQueryState QueryState;

// 初始化
QueryDefinition.Initialize(Outer, USchema::StaticClass(), Conditions);
QueryState.Initialize(*Owner, QueryDefinition);

// 使用 Context 绑定求值
FWorldConditionContextData ContextData(*DefaultSchema);
ContextData.SetContextData(DefaultSchema->GetActorRef(), MyActor);

FWorldConditionContext Context(QueryState, ContextData);
Context.Activate();
bool bResult = Context.IsTrue();
Context.Deactivate();

// 清理
QueryState.Free();
```

## Demo 示例

### 最小可编译示例

**Build.cs 依赖：**

```csharp
PublicDependencyModuleNames.AddRange(new[] { "WorldConditions" });
```

**自定义 Schema（MySchema.h）：**

```cpp
#pragma once
#include "WorldConditionSchema.h"
#include "MySchema.generated.h"

USTRUCT()
struct FMyConditionData
{
    GENERATED_BODY()
    int32 Health = 100;
};

UCLASS()
class UMyConditionSchema : public UWorldConditionSchema
{
    GENERATED_BODY()
public:
    explicit UMyConditionSchema(const FObjectInitializer& ObjectInitializer)
        : Super(ObjectInitializer)
    {
        HealthRef = AddContextDataDesc(TEXT("Health"), FMyConditionData::StaticStruct(), EWorldConditionContextDataType::Dynamic);
    }

    virtual bool IsStructAllowed(const UScriptStruct* InScriptStruct) const override
    {
        return InScriptStruct && InScriptStruct->IsChildOf(TBaseStructure<FWorldConditionBase>::Get());
    }

    FWorldConditionContextDataRef GetHealthRef() const { return HealthRef; }

private:
    FWorldConditionContextDataRef HealthRef;
};
```

**自定义条件（MyCondition.h）：**

```cpp
#pragma once
#include "WorldConditionBase.h"
#include "MyCondition.generated.h"

USTRUCT(meta=(Hidden))
struct FHealthAboveThreshold : public FWorldConditionBase
{
    GENERATED_BODY()

    virtual TObjectPtr<const UStruct>* GetRuntimeStateType() const override { return nullptr; }

    virtual bool Initialize(const UWorldConditionSchema& Schema) override
    {
        if (const UMyConditionSchema* MySchema = Cast<UMyConditionSchema>(&Schema))
        {
            HealthRef = MySchema->GetHealthRef();
            bCanCacheResult = false;
            return true;
        }
        return false;
    }

    virtual FWorldConditionResult IsTrue(const FWorldConditionContext& Context) const override
    {
        FWorldConditionResult Result(EWorldConditionResultValue::IsFalse, bCanCacheResult);
        if (const FMyConditionData* Data = Context.GetContextDataPtr<FMyConditionData>(HealthRef))
        {
            if (Data->Health >= Threshold)
            {
                Result.Value = EWorldConditionResultValue::IsTrue;
            }
        }
        return Result;
    }

    virtual FText GetDescription() const override
    {
        return FText::Format(FText::FromString(TEXT("Health >= {0}")), FText::AsNumber(Threshold));
    }

protected:
    FWorldConditionContextDataRef HealthRef;
    int32 Threshold = 50;
};
```

**使用：**

```cpp
FWorldConditionQuery Query;
Query.DebugInitialize(nullptr, UMyConditionSchema::StaticClass(),
    {
        FWorldConditionEditable(0, EWorldConditionOperator::Copy, FConstStructView::Make(FHealthAboveThreshold()))
    });

FMyConditionData Data;
Data.Health = 75;
const UMyConditionSchema* Schema = GetDefault<UMyConditionSchema>();
FWorldConditionContextData ContextData(*Schema);
ContextData.SetContextData(Schema->GetHealthRef(), &Data);

Query.Activate(*this, ContextData);
bool bHealthy = Query.IsTrue(ContextData);  // true (75 >= 50)
Query.Deactivate(ContextData);
```

## 模块依赖

要使用 World Conditions，你的模块需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型、容器、内存管理 |
| `CoreUObject` | UObject 系统、反射、序列化 |
| `Engine` | AActor、UWorld 等引擎核心类型 |
| `GameplayTags` | GameplayTag 系统（Build.cs 中声明） |
| `PropertyBindingUtils` | 属性绑定路径支持（私有依赖，编辑器端使用） |

编辑器模块额外依赖：`PropertyEditor`、`SlateCore`、`Slate`、`UnrealEd`、`StructUtilsEditor`。

## 维护状态

### 近期更新

1. **2025-09-23** `b2d483e` — [WorldConditions] used binary serialization when required by the archive
   - 修复了 cooked build 中使用 `bOptimizeBPComponentData` 标志时的序列化问题。针对 `FBlueprintComponentInstanceDataWriter` 使用二进制序列化的场景。

2. **2025-08-01** `3c87f32` — [WorldConditions] fixed serialization unit test
   - 修复序列化单元测试，因 `PostSerialize` 现在需要有效的序列化对象才能 link（CIS Issue 989062）。

3. **2025-07-31** `6ee04af` — [WorldCondition] improved error logging on link failure
   - 改进了 link 失败时的错误日志。避免在每种序列化后都尝试 link，仅在加载后执行（UE-307952）。

### 维护评价

- **创建时间**: 2022 年 11 月，相对年轻的插件
- **维护状态**: 活跃维护中 — 最近 3 次更新在 2025 年 7-9 月，均为实质性修复
- **实验性标记**: `.uplugin` 中 `IsExperimentalVersion=true`，`EnabledByDefault=false`
- **消费者**: 主要被 Smart Objects 和其他 Gameplay 系统使用
- **代码质量**: 架构清晰，Definition/State 分离设计合理，缓存机制完善
- **已知限制**: 标记为实验性，API 可能在未来版本中变化；最大表达式深度限制为 4
- **推荐**: ✅ 可以在项目中使用，但需注意实验性标记，关注后续版本更新

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/WorldConditions)
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Runtime/WorldConditions/Source/WorldConditionsTestSuite/Private/WorldConditionsTest.cpp)
