# State Tree

> General purpose hierarchical state machine

| 属性 | 值 |
|---|---|
| 中文名 | 状态树 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（状态机资产、编辑器工具、调试器） |
| 模块 | `StateTreeModule` (Runtime), `StateTreeDeveloper` (Runtime), `StateTreeEditorModule` (Runtime), `StateTreeTestSuite` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-09-28 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/StateTree) | |

## 用途

StateTree 是一个通用的分层状态机插件，它提供了一种比蓝图状态机更结构化、更可维护的方式来管理复杂的游戏逻辑。它主要用于：

1.  **复杂的游戏逻辑管理**：为 NPC、玩家角色、游戏系统（如任务系统、对话系统）提供清晰的状态转换和行为管理。
2.  **可预测的行为**：通过显式的状态定义和转换条件，使游戏逻辑更易于调试和理解。
3.  **编辑器可视化**：提供强大的可视化编辑器，允许设计师直接在编辑器中创建和编辑复杂的状态机，无需编写代码。
4.  **内置调试支持**：集成 UE 的调试工具（如 Gameplay Debugger），提供状态机运行时的可视化调试。

与简单的状态枚举或蓝图中的分支相比，StateTree 将状态、转换、条件和任务集成在一个统一的资产中，特别适合管理具有多个层次、嵌套状态和复杂转换逻辑的游戏系统。

## 使用场景

- **AI 行为**：为敌人或 NPC 创建复杂的行为模式，例如巡逻、追击、攻击、逃跑等状态的切换。
- **游戏流程控制**：管理游戏关卡、任务、对话等系统的不同阶段（如开始、进行中、成功、失败）。
- **玩家状态机**：管理玩家角色的不同状态（如站立、行走、跳跃、攻击、技能施放）。
- **任何需要清晰状态管理的游戏系统**：当系统的行为取决于多个条件的组合，并且状态之间需要明确的转换规则时。

## 蓝图用法

StateTree 的核心使用是通过资产编辑器进行配置，然后在运行时通过组件驱动。以下是关键的蓝图节点：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Start Logic` | 启动状态机的逻辑执行 | `UStateTreeComponent` |
| `Stop Logic` | 停止状态机的逻辑执行 | `UStateTreeComponent` |
| `Set Active State` | 在蓝图中强制设置当前活动的状态（谨慎使用） | `UStateTreeComponent` |
| `Get Active State` | 获取当前活动的状态 ID | `UStateTreeComponent` |
| `Send State Tree Event` | 向状态机发送一个自定义事件，可能触发状态转换 | `UStateTreeComponent` |
| `Set Context Data` | 设置传递给状态机运行时的上下文数据（如拥有者角色、目标） | `UStateTreeComponent` |

### 使用示例（蓝图描述）

1.  **创建资产**：在内容浏览器中，右键 -> Artificial Intelligence -> State Tree，创建新的 `UStateTree` 资产。
2.  **添加组件**：在需要驱动状态机的 Actor（如 AI 角色）蓝图中，添加 `UStateTreeComponent`。
3.  **配置组件**：在组件的详细信息面板中，将上一步创建的 StateTree 资产指定给 `StateTree` 属性。设置 `Auto Start` 为 `On Begin Play` 或 `On Input` 以自动开始。
4.  **设置上下文**：通常在事件 `BeginPlay` 或 `On Start Logic` 中，调用 `Set Context Data` 节点，将 `Self`（Actor 自身）和任何其他相关对象（如 AI 感知到的目标）作为上下文传递给状态机。
5.  **事件驱动**：在游戏逻辑中，可以通过 `Send State Tree Event` 节点发送自定义事件，以响应游戏内的变化（如被攻击、目标丢失），从而触发状态机内部定义的转换。

## C++ 用法

在 C++ 中，StateTree 通常通过 `UStateTreeComponent` 来使用和扩展。

### 头文件引入

```cpp
#include "StateTreeComponent.h"
```

### 基本用法

**创建和配置组件** (来源: `StateTreeComponent.h`)

```cpp
// 在 Actor 的构造函数或 BeginPlay 中
UStateTreeComponent* StateTreeComp = CreateDefaultSubobject<UStateTreeComponent>(TEXT("MyStateTree"));
StateTreeComp->SetStateTree(MyStateTreeAsset); // UStateTree*
StateTreeComp->bAutoStart = true; // 设置为自动开始

// 在 BeginPlay 后，手动设置上下文
void AMyAICharacter::BeginPlay()
{
    Super::BeginPlay();
    if (StateTreeComp)
    {
        // 设置上下文，第一个参数是 Owner，通常是自己
        StateTreeComp->SetContextData(this);
        // 如果有其他上下文，如黑板，可以继续添加
        // StateTreeComp->SetContextData(MyBlackboardComponent);
    }
}
```

**监听状态机事件**

```cpp
// 在 Actor 头文件中声明
UPROPERTY()
TObjectPtr<UStateTreeComponent> StateTreeComp;

// 在 .cpp 中绑定委托
void AMyCharacter::SetupStateTreeEvents()
{
    if (StateTreeComp)
    {
        // 绑定状态机完成事件（例如，所有叶子状态执行完毕）
        StateTreeComp->OnStateTreeCompleted.AddDynamic(this, &AMyCharacter::OnStateTreeCompleted);
    }
}

void AMyCharacter::OnStateTreeCompleted(UStateTreeComponent& Component, const bool bSucceeded)
{
    UE_LOG(LogTemp, Log, TEXT("StateTree finished with success: %s"), bSucceeded ? TEXT("True") : TEXT("False"));
    // 进行后续处理，例如重新开始或通知其他系统
}
```

### 进阶用法

**扩展任务（Task）**

StateTree 的强大之处在于其可扩展性。你可以创建自定义的任务、条件和评估器。

1.  **创建自定义任务**：继承自 `UStateTreeTaskBlueprintBase`（蓝图）或 `FStateTreeTaskBase`（纯 C++）。
2.  **在状态树资产中使用**：在状态树编辑器中，你的自定义任务将出现在节点列表中，可以直接使用。

```cpp
// 示例：一个简单的移动到位置的任务
UCLASS()
class UMyStateTreeTask_MoveToLocation : public UStateTreeTaskBlueprintBase
{
    GENERATED_BODY()

public:
    // 任务的输入参数，在编辑器中配置
    UPROPERTY(EditAnywhere, Category = "Context")
    FVector TargetLocation;

    // 任务激活时调用
    virtual EStateTreeRunStatus EnterState(FStateTreeExecutionContext& Context, const FStateTreeTransitionResult& Transition) const override
    {
        // 获取拥有者 Actor
        AActor* Owner = Context.GetOwner<AActor>();
        if (Owner)
        {
            // 调用 AI 移动或执行逻辑
            // 这里只是一个示例框架
            UE_LOG(LogTemp, Log, TEXT("Moving to: %s"), *TargetLocation.ToString());
            // 返回 Running，表示任务正在执行
            return EStateTreeRunStatus::Running;
        }
        return EStateTreeRunStatus::Failed;
    }

    // 任务退出时调用
    virtual void ExitState(FStateTreeExecutionContext& Context, const FStateTreeTransitionResult& Transition) const override
    {
        // 清理资源
    }
};
```

## Demo 示例

以下是一个简单的 C++ Actor 示例，它拥有并驱动一个 StateTreeComponent。

**头文件 (MyStateTreeCharacter.h)**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "MyStateTreeCharacter.generated.h"

class UStateTreeComponent;

UCLASS()
class AMyStateTreeCharacter : public ACharacter
{
	GENERATED_BODY()

public:
	AMyStateTreeCharacter();

protected:
	virtual void BeginPlay() override;

public:
	virtual void Tick(float DeltaTime) override;

	// 向状态机发送事件的函数
	UFUNCTION(BlueprintCallable, Category = "StateTree")
	void TriggerAttackEvent();

protected:
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<UStateTreeComponent> StateTreeComp;

private:
	UFUNCTION()
	void OnStateTreeLogicCompleted(UStateTreeComponent& InStateTreeComp, const bool bSucceeded);
};
```

**源文件 (MyStateTreeCharacter.cpp)**
```cpp
#include "MyStateTreeCharacter.h"
#include "StateTreeComponent.h"

AMyStateTreeCharacter::AMyStateTreeCharacter()
{
	PrimaryActorTick.bCanEverTick = true;

	StateTreeComp = CreateDefaultSubobject<UStateTreeComponent>(TEXT("StateTreeComp"));
}

void AMyStateTreeCharacter::BeginPlay()
{
	Super::BeginPlay();

	// 配置状态树（通常资产在蓝图中设置，这里假设有资产引用）
	// StateTreeComp->SetStateTree(MyStateTreeAsset);

	// 设置上下文数据，让状态树可以访问这个角色自身
	StateTreeComp->SetContextData(this);

	// 绑定完成事件
	StateTreeComp->OnStateTreeCompleted.AddDynamic(this, &AMyStateTreeCharacter::OnStateTreeLogicCompleted);

	// 如果没有设置 AutoStart，可以手动启动
	// StateTreeComp->StartLogic();
}

void AMyStateTreeCharacter::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);
}

void AMyStateTreeCharacter::TriggerAttackEvent()
{
	// 发送自定义事件到状态机，假设在状态树中定义了 "Attack" 事件
	if (StateTreeComp)
	{
		// 构造事件（需要与状态树中定义的事件匹配）
		// FGameplayTag AttackEventTag = FGameplayTag::RequestGameplayTag(FName("StateTree.Event.Attack"));
		// StateTreeComp->SendStateTreeEvent(AttackEventTag);
	}
}

void AMyStateTreeCharacter::OnStateTreeLogicCompleted(UStateTreeComponent& InStateTreeComp, const bool bSucceeded)
{
	UE_LOG(LogTemp, Log, TEXT("State Tree Logic Completed. Succeeded: %s"), bSucceeded ? TEXT("Yes") : TEXT("No"));
	// 在这里可以重新启动逻辑或执行其他操作
	// InStateTreeComp.StartLogic();
}
```

## 模块依赖

从 Build.cs 和模块结构分析，StateTree 插件本身高度自包含。对于要**使用**该插件的用户模块，主要需要依赖核心运行时模块。

| 模块 | 用途 |
|---|---|
| `StateTreeModule` | 核心运行时模块，包含状态机引擎、状态树资产类型、任务基类等。这是你在模块中必须依赖的模块。 |
| `GameplayTags` | 状态树广泛使用 GameplayTags 来标识状态、事件和属性。你的模块很可能需要此模块。 |
| `AIModule` | 如果使用状态树进行 AI 行为控制，可能需要依赖此模块来使用 AI 相关的任务或功能。 |
| `NavigationSystem` | 如果自定义任务需要导航（如移动到位置），则需要依赖此模块。 |

**注意**：`StateTreeDeveloper`、`StateTreeEditorModule` 和 `StateTreeTestSuite` 是编辑器和测试专用模块，游戏运行时模块**不应**依赖它们。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `2c528ff3` | [StateTree] Fix invalid memory access. | 修复无效内存访问问题，提升稳定性。 |
| 2026-05-14 | `fbc95955` | [StateTree] Fix bas memory access in unittest | 修复单元测试中的基础内存访问错误。 |
| 2026-05-14 | `4efd5cdb` | [StateTree] Compile pending StateTree assets in the editor before linking. This prevents link failur | 在链接前编译编辑器中待处理的状态树资产，防止链接失败。 |
| 2026-05-13 | `541c19e0` | Extend property binding compatibility to support task completion bindings | 扩展属性绑定兼容性，以支持任务完成绑定。 |
| 2026-05-12 | `ea25bb3b` | [StateTree] Copy-paste transition also copies the bindings. Fix the UI that displays the list of sta | 复制粘贴转换时也复制绑定关系。修复显示状态列表的 UI 问题。 |

### 维护评价

**活跃维护**。StateTree 是 Epic 重点开发和维护的系统，与 MetaHumans、Lyra 等项目深度集成。从最近的提交记录可以看出，团队在持续修复 bug、优化编辑器工作流并扩展功能（如属性绑定）。该插件自创建以来一直得到稳定更新，是 UE5 中推荐用于复杂 AI 和游戏逻辑管理的系统。尽管仍被标记为版本 0.1，但其成熟度和功能完整性已非常高，适合在生产项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/StateTree)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/state-tree-in-unreal-engine/) (UE5.8 官方文档站)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/StateTree/Source/StateTreeTestSuite)