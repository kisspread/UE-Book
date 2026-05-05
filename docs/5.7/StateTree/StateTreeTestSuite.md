# State Tree

> General purpose hierarchical state machine（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（状态树资产） |
| 模块 | `StateTreeModule` (Runtime), `StateTreeEditorModule` (Runtime), `StateTreeDeveloper` (Runtime), `StateTreeTestSuite` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-09-28 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/StateTree) | |

## 用途

StateTree 是一个通用的、层次化的状态机框架，旨在管理复杂的游戏逻辑和AI行为。它超越了传统的状态机，支持并行执行、数据绑定、条件检查、任务执行和状态转换等高级功能。其核心目的是为开发者提供一个强大、灵活且可视化友好的工具，用于构建和调试复杂的游戏系统，例如AI决策、游戏流程控制、动画状态管理等。

## 使用场景

- **AI 行为控制**：你需要为NPC创建复杂的、分层的行为逻辑（例如：巡逻 -> 发现敌人 -> 追击 -> 攻击 -> 撤退），并且希望这些逻辑能够可视化编辑和调试。
- **游戏流程管理**：你需要管理游戏的主循环、关卡流程、UI状态等，这些流程可能包含多个并行或嵌套的子状态。
- **复杂动画状态管理**：你需要一个比状态机图表更强大的系统来管理角色的动画状态，支持条件分支和并行动画层。
- **任务系统**：你需要一个框架来执行一系列有依赖关系、可中断、可并行的游戏任务。

## 蓝图用法

StateTree 的蓝图API主要围绕状态树资产的创建、配置和执行。以下是从源码中提取的核心节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create State Tree` | 创建一个状态树实例，用于后续执行。 | `UStateTreeSubsystem` |
| `Set State Tree Parameters` | 在执行状态树前，设置其全局参数（黑板数据）。 | `UStateTreeSubsystem` |
| `Start State Tree` | 启动一个状态树实例的执行。 | `UStateTreeSubsystem` |
| `Stop State Tree` | 停止一个正在运行的状态树实例。 | `UStateTreeSubsystem` |
| `Get State Tree Instance` | 根据句柄获取一个正在运行的状态树实例，用于查询其状态。 | `UStateTreeSubsystem` |
| `Is State Tree Running` | 检查一个状态树实例是否正在运行。 | `UStateTreeSubsystem` |

### 使用示例（蓝图描述）

1.  **创建并启动一个简单的状态树**：
    *   在角色蓝图中，使用 `Create State Tree` 节点创建一个实例，指定要使用的 `UStateTree` 资产。
    *   使用 `Set State Tree Parameters` 节点设置初始参数（例如，目标Actor）。
    *   使用 `Start State Tree` 节点启动执行，并保存返回的 `FStateTreeInstanceHandle`。
2.  **查询状态树状态**：
    *   在需要时（例如，每帧），使用保存的 `FStateTreeInstanceHandle` 调用 `Get State Tree Instance`。
    *   从返回的实例对象中，可以查询当前活动的状态、任务执行情况等信息。
3.  **停止状态树**：
    *   当角色死亡或游戏结束时，使用 `Stop State Tree` 节点并传入句柄来安全地停止状态树。

## C++ 用法

C++ 用法主要涉及状态树的编程式创建、参数设置和执行控制。以下示例基于测试用例提炼。

### 头文件引入

```cpp
#include "StateTree.h"
#include "StateTreeSubsystem.h"
#include "StateTreeExecutionContext.h"
```

### 基本用法

以下代码演示了如何创建一个简单的状态树实例并执行它。来源文件：`Engine/Plugins/Runtime/StateTree/Source/StateTreeTestSuite/Tests/StateTreeTest.cpp`

```cpp
// 假设我们已经有一个 UStateTree* StateTreeAsset 指向编辑器中创建的状态树资产
// 假设我们有一个 AActor* OwnerActor 作为状态树的执行上下文所有者

// 1. 获取状态树子系统
UStateTreeSubsystem* StateTreeSubsystem = OwnerActor->GetWorld()->GetSubsystem<UStateTreeSubsystem>();
if (!StateTreeSubsystem) return;

// 2. 创建状态树实例
FStateTreeInstanceHandle InstanceHandle = StateTreeSubsystem->CreateStateTree(*StateTreeAsset, OwnerActor);
if (!InstanceHandle.IsValid()) return;

// 3. (可选) 设置全局参数
// 假设状态树有一个名为 “TargetActor” 的全局参数
FStateTreeExternalDataDesc TargetDataDesc;
TargetDataDesc.Name = TEXT("TargetActor");
TargetDataDesc.Struct = AActor::StaticClass();
StateTreeSubsystem->SetStateTreeExternalData(InstanceHandle, TargetDataDesc, SomeTargetActor);

// 4. 启动状态树
StateTreeSubsystem->StartStateTree(InstanceHandle);

// 5. 在后续的 Tick 或需要时，可以查询状态
// FStateTreeInstance* Instance = StateTreeSubsystem->GetStateTreeInstance(InstanceHandle);
// if (Instance) { /* 查询状态 */ }

// 6. 在对象销毁或不再需要时，停止状态树
StateTreeSubsystem->StopStateTree(InstanceHandle);
```

### 进阶用法

更复杂的用法包括直接使用 `FStateTreeExecutionContext` 来手动驱动状态树的执行，这在自定义的 `UActorComponent` 或 `UBrainComponent` 中很常见。来源文件：`Engine/Plugins/Runtime/StateTree/Source/StateTreeTestSuite/Tests/StateTreeTest.cpp`

```cpp
// 在自定义组件中
void UMyAIComponent::InitializeStateTree()
{
    // ... 创建或获取 StateTreeAsset ...
    
    // 初始化执行上下文
    ExecutionContext = FStateTreeExecutionContext(*StateTreeAsset, *GetOwner(), *this);
    
    // 设置外部数据（例如，感知组件、移动组件等）
    // ExecutionContext.SetExternalData(...);
    
    // 启动执行
    if (ExecutionContext.Start())
    {
        bIsRunning = true;
    }
}

void UMyAIComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
    
    if (bIsRunning && ExecutionContext.IsValid())
    {
        // 手动驱动状态树 Tick
        const EStateTreeRunStatus Status = ExecutionContext.Tick(DeltaTime);
        
        if (Status == EStateTreeRunStatus::Failed || Status == EStateTreeRunStatus::Succeeded)
        {
            // 状态树执行完成或失败
            bIsRunning = false;
            // 处理结果...
        }
    }
}

void UMyAIComponent::StopStateTree()
{
    if (ExecutionContext.IsValid())
    {
        ExecutionContext.Stop();
        bIsRunning = false;
    }
}
```

## Demo 示例

一个最小的可编译示例，展示如何在 Actor 组件中集成和执行一个状态树。

### MyAIComponent.h
```cpp
// MyAIComponent.h
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "StateTreeExecutionContext.h"
#include "MyAIComponent.generated.h"

class UStateTree;

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class YOURPROJECT_API UMyAIComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UMyAIComponent();

    virtual void BeginPlay() override;
    virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    UPROPERTY(EditAnywhere, Category = "AI")
    TObjectPtr<UStateTree> StateTreeAsset;

private:
    FStateTreeExecutionContext ExecutionContext;
    bool bIsRunning = false;
};
```

### MyAIComponent.cpp
```cpp
// MyAIComponent.cpp
#include "MyAIComponent.h"
#include "StateTree.h"

UMyAIComponent::UMyAIComponent()
{
    PrimaryComponentTick.bCanEverTick = true;
}

void UMyAIComponent::BeginPlay()
{
    Super::BeginPlay();

    if (StateTreeAsset && GetOwner())
    {
        // 初始化执行上下文
        ExecutionContext = FStateTreeExecutionContext(*StateTreeAsset, *GetOwner(), *this);
        
        // 在这里可以设置外部数据，例如：
        // ExecutionContext.SetExternalData(TEXT("Blackboard"), GetOwner()->FindComponentByClass<UBlackboardComponent>());
        
        // 启动状态树
        if (ExecutionContext.Start())
        {
            bIsRunning = true;
            UE_LOG(LogTemp, Log, TEXT("StateTree started for %s"), *GetOwner()->GetName());
        }
    }
}

void UMyAIComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

    if (bIsRunning && ExecutionContext.IsValid())
    {
        const EStateTreeRunStatus Status = ExecutionContext.Tick(DeltaTime);
        
        if (Status == EStateTreeRunStatus::Failed)
        {
            UE_LOG(LogTemp, Warning, TEXT("StateTree failed for %s"), *GetOwner()->GetName());
            bIsRunning = false;
        }
        else if (Status == EStateTreeRunStatus::Succeeded)
        {
            UE_LOG(LogTemp, Log, TEXT("StateTree succeeded for %s"), *GetOwner()->GetName());
            bIsRunning = false;
        }
    }
}

void UMyAIComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (bIsRunning)
    {
        ExecutionContext.Stop();
        bIsRunning = false;
    }
    Super::EndPlay(EndPlayReason);
}
```

## 模块依赖

从 `StateTreeModule.Build.cs` 分析，使用该插件的核心功能，你的模块需要依赖以下独特模块：

| 模块 | 用途 |
|---|---|
| `GameplayTags` | 状态树广泛使用 GameplayTag 进行状态标识、条件判断和事件触发。 |
| `GameplayTasks` | 状态树中的“任务”节点可能基于或与 GameplayTasks 系统集成。 |

## 维护状态

### 近期更新

- 2025-10-03 `35845c105210` [State Tree] fixed property not inisitalized properly
- 2025-09-15 `291028cf6b91` [StateTree] allow state selection to continue when reaching the source state of the transition if it is completed (requires SelectionRules to use CompletedTransitionStatesCreateNewStates) #jira UE-333382 #rb jacob.wang
- 2025-08-20 `44d2e9a4dabe` [State Tree][Property Binding] Introduced output binding feature. Target property reversely bound to source property will write back to the source property instead of copying from the source property, at the end of each node processing scope(EnterState, Tick, ExitState). Property can only be reversely bound to state or global parameters. Only allow output property to be reversely bound as a clear UX to the user is being figured out.

### 维护评价

StateTree 是一个相对较新（约3年）且处于**活跃维护**状态的插件。从近期提交记录可以看出，Epic 团队正在持续为其添加新功能（如输出绑定）、修复缺陷（属性初始化）并优化核心逻辑（状态选择规则）。它被标记为 `EnabledByDefault: false`，表明它可能仍处于快速迭代期，API和功能可能发生变化，但已具备生产可用性。对于需要复杂状态管理的项目，**推荐使用**，但需注意关注其版本更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/StateTree)
- [官方文档]() (暂无)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/StateTree/Source/StateTreeTestSuite)