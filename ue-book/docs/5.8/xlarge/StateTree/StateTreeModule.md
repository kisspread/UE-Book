# State Tree

> General purpose hierarchical state machine

| 属性 | 值 |
|---|---|
| 中文名 | 状态树 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、调试工具） |
| 模块 | `StateTreeModule` (Runtime), `StateTreeDeveloper` (Runtime), `StateTreeEditorModule` (Runtime), `StateTreeTestSuite` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-09-28 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/StateTree) | |

## 用途

StateTree 是 UE5 内置的**通用层级状态机框架**，用于替代和补充传统的行为树（Behavior Tree）系统。它通过将游戏逻辑组织为嵌套的状态、条件、任务和评估器，让开发者可以构建复杂且可维护的 AI 决策系统和游戏玩法逻辑。

核心解决的问题：
- **层级状态管理**：支持状态嵌套、链接状态、子树（Subtree）和跨资产链接，构建大规模逻辑而不失可读性
- **数据驱动决策**：通过属性绑定（Property Bindings）在节点间传递数据，支持运行时自动同步
- **工具链支持**：内置可视化编辑器、状态选择行为（随机、效用、顺序）、条件转换等，适合策划使用
- **并行执行**：支持在同一状态内并行运行多个子状态树
- **蓝图友好**：任务、条件、评估器均可通过蓝图实现，降低 C++ 门槛
- **调试支持**：集成 Unreal Insights 追踪系统，支持断点、状态回放、事件日志

与 Behavior Tree 的主要区别：StateTree 更通用，不限于 AI，支持游戏玩法脚本、UI 状态、动画状态机等任何需要状态管理的场景。

## 使用场景

- 你需要为 AI 角色构建复杂决策逻辑（巡逻、战斗、逃跑等） → 使用 StateTree 的状态 + 任务 + 条件
- 你需要基于效用（Utility）选择最佳行为 → 使用 `TrySelectChildrenWithHighestUtility` 选择行为
- 你需要多个状态树并行运行（如主行为 + 感知系统） → 使用 `FStateTreeRunParallelStateTreeTask`
- 你需要在不同角色间共享部分逻辑 → 使用 Linked State / Linked Asset
- 你需要策划友好的可视化状态编辑器 → StateTree 编辑器提供了完整的节点图编辑体验
- 你需要运行时事件驱动的转换 → 使用 `OnEvent` 触发器和 `FStateTreeEvent` 事件系统

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Finish Task` | 完成当前任务，设置成功/失败状态 | `UStateTreeTaskBlueprintBase` |
| `Broadcast Delegate` | 广播委托调度器，触发绑定的回调和转换 | `UStateTreeTaskBlueprintBase` |
| `Bind Delegate` | 注册监听器的委托回调 | `UStateTreeTaskBlueprintBase` |
| `Unbind Delegate` | 注销监听器的委托回调 | `UStateTreeTaskBlueprintBase` |
| `StateTree Send Event` | 向状态树发送事件 | `UStateTreeNodeBlueprintBase` |
| `StateTree Request Transition` | 请求状态转换 | `UStateTreeNodeBlueprintBase` |
| `Get Property Reference` | 获取状态树中属性的引用 | `UStateTreeNodeBlueprintBase` |
| `Set State Tree` | 设置 StateTree 引用和参数 | `UStateTreeFunctionLibrary` |
| `Make State Tree Reference` | 创建 StateTree 引用 | `UStateTreeFunctionLibrary` |
| `Set Parameter Property` | 设置 StateTree 参数属性 | `UStateTreeFunctionLibrary` |
| `Get Parameter Property` | 获取 StateTree 参数属性 | `UStateTreeFunctionLibrary` |

### 蓝图任务事件

| 事件 | 说明 |
|---|---|
| `ReceiveLatentEnterState` | 进入状态时调用，使用 `FinishTask` 控制完成 |
| `ReceiveExitState` | 退出状态时调用 |
| `ReceiveStateCompleted` | 状态完成后调用（倒序传播） |
| `ReceiveLatentTick` | 每帧更新调用（需启用 `bShouldCallTick`） |

### 使用示例（蓝图描述）

**创建蓝图任务**：
1. 创建 `UStateTreeTaskBlueprintBase` 的子类蓝图
2. 实现 `ReceiveLatentEnterState` 事件：执行启动逻辑，在完成时调用 `Finish Task`
3. 实现 `ReceiveLatentTick` 事件（可选）：监控条件并调用 `Finish Task`
4. 实现 `ReceiveExitState` 事件（可选）：清理资源

**创建蓝图条件**：
1. 创建 `UStateTreeConditionBlueprintBase` 的子类蓝图
2. 实现 `ReceiveTestCondition` 事件：返回 true/false

**发送事件**：
1. 在蓝图任务中调用 `StateTree Send Event` 节点
2. 指定 `GameplayTag` 和可选的 `Payload` 结构体
3. 配套的转换可设置 `OnEvent` 触发器来响应该事件

## C++ 用法

### 头文件引入

```cpp
#include "StateTreeExecutionContext.h"
#include "StateTreeTaskBase.h"
#include "StateTreeConditionBase.h"
#include "StateTreeEvaluatorBase.h"
#include "StateTreePropertyRef.h"
#include "StateTreeCommonConditions.h"
```

### 基本用法

**创建自定义任务（C++）**

来源：`Public/StateTreeTaskBase.h`，`Public/Blueprint/StateTreeTaskBlueprintBase.h`

```cpp
USTRUCT()
struct FMyTaskInstanceData
{
    GENERATED_BODY()
    
    UPROPERTY(EditAnywhere, Category = "Parameter")
    float Threshold = 100.0f;
};

USTRUCT(meta = (DisplayName = "My Custom Task"))
struct FMyTask : public FStateTreeTaskCommonBase
{
    GENERATED_BODY()
    
    using FInstanceDataType = FMyTaskInstanceData;
    
    virtual const UStruct* GetInstanceDataType() const override
    {
        return FInstanceDataType::StaticStruct();
    }
    
    virtual EStateTreeRunStatus EnterState(
        FStateTreeExecutionContext& Context,
        const FStateTreeTransitionResult& Transition) const override
    {
        // 进入状态时的逻辑
        const FMyTaskInstanceData& Data = Context.GetInstanceData(*this);
        UE_LOG(LogTemp, Log, TEXT("Threshold: %f"), Data.Threshold);
        return EStateTreeRunStatus::Running;
    }
    
    virtual EStateTreeRunStatus Tick(
        FStateTreeExecutionContext& Context,
        const float DeltaTime) const override
    {
        // 每帧更新逻辑
        return EStateTreeRunStatus::Running;
    }
    
    virtual void ExitState(
        FStateTreeExecutionContext& Context,
        const FStateTreeTransitionResult& Transition) const override
    {
        // 退出状态时清理
    }
};
```

**创建自定义条件**

来源：`Public/StateTreeConditionBase.h`

```cpp
USTRUCT(meta = (DisplayName = "My Check"))
struct FMyCondition : public FStateTreeConditionCommonBase
{
    GENERATED_BODY()
    
    virtual bool TestCondition(FStateTreeExecutionContext& Context) const override
    {
        // 返回 true 表示条件通过
        return true;
    }
};
```

### 进阶用法

**属性绑定（Property Binding）**

来源：`Public/StateTreePropertyBindings.h`

任务节点可以通过属性绑定引用其他节点的数据：

```cpp
USTRUCT()
struct FLinkedTaskInstanceData
{
    GENERATED_BODY()
    
    // 可在编辑器中绑定到其他节点的属性
    UPROPERTY(EditAnywhere, Category = "Input")
    float Health = 0.0f;
    
    UPROPERTY(EditAnywhere, Category = "Input")
    bool bIsAlive = true;
};
```

**使用 PropertyRef 访问外部属性**

来源：`Public/StateTreePropertyRef.h`

```cpp
USTRUCT()
struct FRefTaskInstanceData
{
    GENERATED_BODY()
    
    // 类型安全的属性引用
    UPROPERTY(EditAnywhere)
    TStateTreePropertyRef<float> RefToHealth;
    
    // 支持多种类型的引用
    UPROPERTY(EditAnywhere, meta = (RefType = "/Script/CoreUObject.Vector, /Script/Engine.Actor", CanRefToArray))
    FStateTreePropertyRef RefToLocationLikeTypes;
};

// 在任务中获取引用的指针
virtual EStateTreeRunStatus Tick(FStateTreeExecutionContext& Context, const float DeltaTime) const override
{
    const FRefTaskInstanceData& Data = Context.GetInstanceData(*this);
    float* HealthPtr = Data.RefToHealth.GetMutablePtr<float>(Context);
    if (HealthPtr)
    {
        // 使用 *HealthPtr
    }
    return EStateTreeRunStatus::Running;
}
```

**外部数据访问**

来源：`Public/StateTreeExecutionTypes.h`

```cpp
// 声明外部数据句柄
TStateTreeExternalDataHandle<UWorldSubsystem> WorldSubsystemHandle;

// 在 Link 中注册
bool Link(FStateTreeLinker& Linker) override
{
    Linker.LinkExternalData(WorldSubsystemHandle);
    return true;
}

// 在执行时获取
EStateTreeRunStatus EnterState(FStateTreeExecutionContext& Context, const FStateTreeTransitionResult& Transition) const override
{
    const UWorldSubsystem& Subsystem = Context.GetExternalData(WorldSubsystemHandle);
    // 使用 Subsystem...
    return EStateTreeRunStatus::Running;
}
```

**事件系统**

来源：`Public/StateTreeEvents.h`

```cpp
// 发送事件
Context.SendEvent(FGameplayTag::RequestGameplayTag("Event.Damage"), 
                  FConstStructView::Make(FDamageEvent{50.0f}));

// 在接收端的转换中使用 OnEvent 触发器
// 转换配置: Trigger = OnEvent, EventTag = "Event.Damage"
```

**并行运行子状态树**

来源：`Public/Tasks/StateTreeRunParallelStateTreeTask.h`

使用 `FStateTreeRunParallelStateTreeTask` 任务可以在当前状态中并行运行另一个状态树，而不阻塞主树的执行。

## Demo 示例

```cpp
// MyStateTreeTask.h
#pragma once

#include "StateTreeTaskBase.h"
#include "MyStateTreeTask.generated.h"

USTRUCT()
struct FMyPatrolTaskInstanceData
{
    GENERATED_BODY()
    
    UPROPERTY(EditAnywhere, Category = "Parameter")
    float PatrolSpeed = 300.0f;
    
    UPROPERTY(EditAnywhere, Category = "Parameter")
    float ArrivalThreshold = 50.0f;
    
    UPROPERTY(EditAnywhere, Category = "Input")
    FVector CurrentLocation = FVector::ZeroVector;
    
    UPROPERTY(EditAnywhere, Category = "Input")
    FVector TargetLocation = FVector::ZeroVector;
};

USTRUCT(meta = (DisplayName = "Patrol To Location"))
struct FMyPatrolTask : public FStateTreeTaskCommonBase
{
    GENERATED_BODY()
    
    using FInstanceDataType = FMyPatrolTaskInstanceData;
    
    virtual const UStruct* GetInstanceDataType() const override
    {
        return FInstanceDataType::StaticStruct();
    }
    
    virtual EStateTreeRunStatus EnterState(
        FStateTreeExecutionContext& Context,
        const FStateTreeTransitionResult& Transition) const override
    {
        return EStateTreeRunStatus::Running;
    }
    
    virtual EStateTreeRunStatus Tick(
        FStateTreeExecutionContext& Context,
        const float DeltaTime) const override
    {
        const FMyPatrolTaskInstanceData& Data = Context.GetInstanceData(*this);
        
        float Distance = FVector::Dist(Data.CurrentLocation, Data.TargetLocation);
        if (Distance < Data.ArrivalThreshold)
        {
            // 到达目标，任务成功完成
            return EStateTreeRunStatus::Succeeded;
        }
        
        // 仍在移动中
        return EStateTreeRunStatus::Running;
    }
    
    virtual void ExitState(
        FStateTreeExecutionContext& Context,
        const FStateTreeTransitionResult& Transition) const override
    {
        // 清理巡逻状态
    }
    
#if WITH_EDITOR
    virtual FText GetDescription(
        const FGuid& ID,
        FStateTreeDataView InstanceDataView,
        const IStateTreeBindingLookup& BindingLookup,
        EStateTreeNodeFormatting Formatting = EStateTreeNodeFormatting::Text) const override
    {
        return FText::FromString(TEXT("Patrol To Target Location"));
    }
#endif
};
```

```cpp
// MyStateTreeComponent.h
#pragma once

#include "Components/ActorComponent.h"
#include "StateTree.h"
#include "StateTreeExecutionContext.h"
#include "MyStateTreeComponent.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class UMyStateTreeComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, Category = "StateTree")
    TObjectPtr<UStateTree> StateTreeAsset;

    virtual void BeginPlay() override;
    virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

private:
    FStateTreeInstanceData InstanceData;
    FStateTreeExecutionContext* Context = nullptr;
};
```

```cpp
// MyStateTreeComponent.cpp
#include "MyStateTreeComponent.h"
#include "StateTreeExecutionContext.h"

void UMyStateTreeComponent::BeginPlay()
{
    Super::BeginPlay();

    if (StateTreeAsset && StateTreeAsset->IsReadyToRun())
    {
        Context = new FStateTreeExecutionContext(*GetOwner(), *StateTreeAsset, InstanceData);
        
        if (Context->IsValid())
        {
            // 设置上下文数据和外部数据收集回调
            Context->SetCollectExternalDataCallback(
                FOnCollectStateTreeExternalData::CreateUObject(
                    this, &UMyStateTreeComponent::CollectExternalData));
        }
    }
}

void UMyStateTreeComponent::TickComponent(float DeltaTime, ELevelTick TickType,
    FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

    if (Context && Context->IsValid())
    {
        Context->Tick(DeltaTime);
        
        // 检查状态树是否完成
        EStateTreeRunStatus Status = Context->GetStateTreeRunStatus();
        if (Status != EStateTreeRunStatus::Running)
        {
            UE_LOG(LogTemp, Log, TEXT("StateTree completed with status: %d"), (int32)Status);
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GameplayTags` | 游戏标签系统，用于事件匹配和转换触发 |
| `PropertyBindingUtils` | 属性绑定底层支持 |
| `StructUtils` | FInstancedStruct 等动态结构体工具 |
| `StateTreeEditorModule` | 编辑器 UI 和编译器（仅编辑器） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `2c528ff3` | [StateTree] Fix invalid memory access. | 修复无效内存访问的崩溃问题 |
| 2026-05-14 | `fbc95955` | [StateTree] Fix bas memory access in unittest | 修复单元测试中的基础内存访问错误 |
| 2026-05-14 | `4efd5cdb` | [StateTree] Compile pending StateTree assets in the editor before linking. This prevents link failure | 编辑器中链接前先编译待处理的 StateTree 资产，防止链接失败 |
| 2026-05-13 | `541c19e0` | Extend property binding compatibility to support task completion bindings | 扩展属性绑定兼容性以支持任务完成绑定 |
| 2026-05-12 | `ea25bb3b` | [StateTree] Copy-paste transition also copies the bindings. Fix the UI that displays the list of sta | 复制粘贴转换时同时复制绑定关系，修复状态列表的 UI 显示 |

### 维护评价

**活跃维护** 🟢

StateTree 是 Epic 重点维护的核心 Gameplay 框架，自 2021 年创建以来持续活跃更新。近期提交（2026 年 5 月）显示仍在进行功能扩展（任务完成绑定、编辑器改进）和稳定性修复（内存访问修复）。

优势：
- 持续获得 Epic 团队的功能迭代和 Bug 修复
- 作为 UE5 AI/Gameplay 基础设施，不会被轻易废弃
- 有完整的测试套件（`StateTreeTestSuite`）
- 调试工具完善（Unreal Insights 集成、断点系统）

注意事项：
- 默认未启用（`EnabledByDefault: false`），需手动在项目设置中启用
- API 仍在演进中，部分标记为 deprecated 的接口需要注意迁移（如 `FStateTreeWeakTaskRef`、`FStateTreePropertyRefExternalHandle`）
- 版本号为 0.1，说明 Epic 视其为尚未完全稳定的 API

**推荐使用**：对于新项目中需要状态机的场景，推荐优先使用 StateTree 而非传统 Behavior Tree。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/StateTree)
- [官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/state-tree-in-unreal-engine)