# GameplayStateTree

> StateTree for AI/Gameplay Behaviors（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | AI 状态树组件 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GameplayStateTreeModule` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-05-02 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GameplayStateTree) | |

## 用途

GameplayStateTree 是 **StateTree 系统与 AI/游戏行为之间的桥梁**。基础的 StateTree 插件只提供通用的状态树框架（编辑器、编译、执行上下文），但它本身不关心状态树跑在哪里、怎么跑。本插件解决了以下核心问题：

1. **运行时执行载体**：提供 `UStateTreeComponent`（挂在 Actor 上自动运行状态树）和 `UStateTreeAIComponent`（专为 AIController 设计），替代了早期版本中嵌在 StateTree 模块里的 `StateTreeBrainComponent`。
2. **Schema 定义**：`StateTreeComponentSchema` 和 `StateTreeAIComponentSchema` 定义了状态树能访问哪些上下文数据（Actor、AIController、Pawn 等），确保状态树节点在运行时能获取正确的外部数据。
3. **行为树集成**：提供 `UBTTask_RunStateTree` 和 `UBTTask_RunDynamicStateTree`，让状态树可以直接嵌入行为树节点中执行，实现两种 AI 系统的混合使用。
4. **内置 AI 任务**：提供 `FStateTreeMoveToTask`（移动到目标）和 `FStateTreeRunEnvQueryTask`（运行 EQS 查询）等常用 AI 行为任务。

简而言之：**StateTree 插件提供了引擎，本插件提供了引擎的 AI 驾驶舱**。

> ⚠️ 此插件默认未启用（`EnabledByDefault: false`），使用前需在项目设置中手动启用，或在 `.uproject` 中添加 `Enabled: true`。

## 使用场景

- 你的 AI 需要比行为树更灵活的状态管理（支持分层、子状态树覆盖）→ 用 StateTreeComponent 替代行为树
- 你已经在用行为树，但想在某些节点中嵌入状态树逻辑 → 用 `UBTTask_RunStateTree`
- 你需要在运行时动态选择不同的状态树资产 → 用 `UBTTask_RunDynamicStateTree`
- 你需要 AI 通过 EQS 查询环境信息并根据结果决策 → 用 `FStateTreeRunEnvQueryTask`
- 你需要一个通用组件让任意 Actor 运行状态树（不限于 AI）→ 用 `UStateTreeComponent`

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetStateTree` | 设置要运行的状态树资产（运行中不可设置） | `UStateTreeComponent` |
| `SetStateTreeReference` | 设置状态树引用（运行中不可设置） | `UStateTreeComponent` |
| `AddLinkedStateTreeOverrides` | 添加子状态树覆盖（按 GameplayTag 匹配） | `UStateTreeComponent` |
| `RemoveLinkedStateTreeOverrides` | 移除子状态树覆盖 | `UStateTreeComponent` |
| `SetStartLogicAutomatically` | 设置是否在 BeginPlay 时自动启动 | `UStateTreeComponent` |
| `SendStateTreeEvent` | 向运行中的状态树发送事件 | `UStateTreeComponent` |
| `GetStateTreeRunStatus` | 获取当前运行状态 | `UStateTreeComponent` |
| `RunStateTree` | 静态函数，一键在 Actor 上运行状态树（自动添加组件） | `UGameplayStateTreeBlueprintFunctionLibrary` |
| `OnStateTreeRunStatusChanged` | 委托：运行状态变化时触发 | `UStateTreeComponent` |

### 使用示例（蓝图描述）

**基本用法**：在 Actor 蓝图中添加 `StateTreeComponent`，在详情面板指定 `StateTreeRef` 资产。默认 `bStartLogicAutomatically = true`，BeginPlay 时自动启动。也可以将其设为 false，之后手动调用 `StartLogic()`。

**发送事件**：当游戏事件发生时（如玩家进入视野），调用 `SendStateTreeEvent` 节点，传入 `FStateTreeEvent`（包含 GameplayTag 和可选 Payload），状态树中的 Event 任务会响应。

**一键运行**：不需要手动添加组件时，调用静态节点 `RunStateTree`，传入目标 Actor 和状态树资产即可。如果 Actor 上没有 StateTreeComponent，会自动添加。

**子状态树覆盖**：使用 `AddLinkedStateTreeOverrides`，传入一个 GameplayTag 和对应的状态树引用，状态树在运行到带该 Tag 的 Link 节点时，会使用被覆盖的状态树资产。

## C++ 用法

### 头文件引入

```cpp
#include "Components/StateTreeComponent.h"
#include "Components/StateTreeAIComponent.h"
#include "GameplayStateTreeBlueprintFunctionLibrary.h"
```

### 基本用法：在 Actor 上运行状态树

```cpp
// 在 AIController 中获取 StateTreeAIComponent
UStateTreeAIComponent* STComp = GetOwner()->FindComponentByClass<UStateTreeAIComponent>();
if (STComp)
{
    // 获取当前运行状态
    EStateTreeRunStatus Status = STComp->GetStateTreeRunStatus();
    
    // 停止当前逻辑
    STComp->StopLogic(TEXT("Switching behavior"));
    
    // 设置新的状态树资产
    STComp->SetStateTree(NewStateTreeAsset);
    
    // 重新启动
    STComp->StartLogic();
}
```

### 进阶用法：发送事件和监听状态变化

```cpp
// 绑定状态变化委托
if (UStateTreeComponent* STComp = OwnerActor->FindComponentByClass<UStateTreeComponent>())
{
    STComp->OnStateTreeRunStatusChanged.AddDynamic(this, &AMyAI::OnStateTreeStatusChanged);
    
    // 发送事件（带 GameplayTag 和 Payload）
    FStateTreeEvent Event;
    Event.Tag = FGameplayTag::RequestGameplayTag(FName("AI.Event.PlayerSpotted"));
    Event.Payload = FConstStructView::Make(PlayerLocation);
    STComp->SendStateTreeEvent(Event);
}

// 回调函数
void AMyAI::OnStateTreeStatusChanged(EStateTreeRunStatus NewStatus)
{
    // 状态树运行状态变化时的处理逻辑
}
```

### 一键运行（从蓝图函数库）

```cpp
// 最简单的方式：一行代码在任意 Actor 上运行状态树
bool bSuccess = UGameplayStateTreeBlueprintFunctionLibrary::RunStateTree(
    TargetActor, 
    MyStateTreeAsset
);
```

> 来源：`GameplayStateTreeBlueprintFunctionLibrary.h`

## Demo 示例

以下示例展示一个自定义 AIController，使用 StateTreeAIComponent 运行状态树并处理事件：

```cpp
// MyAIController.h
#pragma once

#include "AIController.h"
#include "Components/StateTreeAIComponent.h"
#include "MyAIController.generated.h"

UCLASS()
class AMyAIController : public AAIController
{
    GENERATED_BODY()
    
public:
    AMyAIController();
    
    UFUNCTION(BlueprintCallable)
    void AlertToPlayer(FVector PlayerLocation);
    
    UFUNCTION(BlueprintCallable)
    void ReturnToPatrol();

protected:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    TObjectPtr<UStateTreeAIComponent> StateTreeComp;
};

// MyAIController.cpp
#include "MyAIController.h"
#include "StateTreeEvent.h"

AMyAIController::AMyAIController()
{
    StateTreeComp = CreateDefaultSubobject<UStateTreeAIComponent>(TEXT("StateTreeComp"));
}

void AMyAIController::AlertToPlayer(FVector PlayerLocation)
{
    FStateTreeEvent Event;
    Event.Tag = FGameplayTag::RequestGameplayTag(FName("AI.Event.Combat.Alert"));
    Event.Payload = FConstStructView::Make(PlayerLocation);
    StateTreeComp->SendStateTreeEvent(Event);
}

void AMyAIController::ReturnToPatrol()
{
    StateTreeComp->StopLogic(TEXT("Return to patrol"));
    StateTreeComp->StartLogic();
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `StateTree` | 状态树核心框架（编辑器、执行上下文、Schema 基类） |
| `GameplayTasks` | GameplayTask 框架（IGameplayTaskOwnerInterface） |
| `AIModule` | AI 控制器、AITask_MoveTo、行为树框架 |
| `NavigationSystem` | 导航查询（MoveTo 任务依赖） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移至新格式 |
| 2026-04-13 | `6f1ea925` | State Tree: Updated state tree reference struct details to show the display name of the struct rathe | 状态树引用结构体显示优化 |
| 2026-03-03 | `407eb03c` | [StateTree] Ensure the StateTree asset is compiled before using it in a StateTreeComponent | 确保 StateTree 资产使用前已编译 |
| 2025-11-17 | `0c9f3796` | [StateTree] Execution context uses a view instead of the property bag. Deprecated the property bag v | 执行上下文改用视图替代属性包 |
| 2025-10-07 | `96352708` | - Renaming Base<Plugin>.ini to Default<Plugin>.ini | 配置文件命名规范更新 |

### 维护评价

**活跃维护**。该插件在 2026 年 4 月仍有功能性更新（日志迁移、资产编译检查），维护频率高。作为 StateTree AI 集成的核心组件，它随 StateTree 系统持续演进。

需要注意：
- **默认未启用**：需手动在项目中开启
- **依赖 StateTree 插件**：必须同时启用
- **仍在持续演进**：API 有渐进式重构（如属性包→视图迁移），升级引擎版本时需关注兼容性变化

**推荐使用**。如果你的项目使用 StateTree 系统做 AI 行为，本插件是必不可少的运行时基础。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GameplayStateTree)
- [官方文档]()（暂无）
- [StateTree 依赖插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/StateTree)