# AI Behaviors

> Encapsulated fire-and-forget behaviors for AI agents

| 属性 | 值 |
|---|---|
| 中文名 | AI行为 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GameplayBehaviorsModule` (Runtime), `GameplayBehaviorsModule` (UncookedOnly), `GameplayBehaviorsEditorModule` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-09-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GameplayBehaviors) | |

---

## 用途

该插件提供一套封装好的“即发即弃”行为机制，专为 AI agent 设计。它基于 `UGameplayBehavior` 抽象基类，允许开发者快速定义一次性的行为任务（如播放动画、运行行为树等），并自动管理其生命周期。同时配套了行为树节点（黑板键类型、装饰器、任务节点）和蓝图函数库，方便与现有 AI 体系集成。

**核心解决的问题**：
- 避免在行为树中频繁编写重复的、需手动清理的临时任务。
- 通过 `GameplayBehaviorSubsystem` 统一管理 agent 当前激活的行为，支持中断和替换。
- 与 `GameplayAbilities` 和 `SmartObjects` 生态联动，实现复杂交互。

---

## 使用场景

- **播放一次性动画**：AI 执行特殊动作（如开门、挥舞武器），播放完毕后自动结束，无需额外计时器或回调。
- **运行临时行为树**：AI 在执行完一个子行为树后自动恢复之前的决策逻辑。
- **与 SmartObject 交互**：当 AI 使用 SmartObject 时，自动触发关联的 `GameplayBehavior`，并监控完成状态。
- **基于标签的动态条件判断**：利用 `BTDecorator_GameplayTagQuery` 根据 Agent 身上的 `GameplayTag` 决定是否执行分支。

---

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `StopGameplayBehavior` | 强制停止指定类型的行为实例（给定 Avatar） | `UGameplayBehaviorsBlueprintFunctionLibrary` |
| `GetBlackboardValueAsGameplayTag` | 从黑板的 `GameplayTag` 键中读取值（行为树节点上下文中） | `UGameplayBehaviorsBlueprintFunctionLibrary` |
| `SetBlackboardValueAsGameplayTag` | 将 `GameplayTag` 值写入黑板的对应键 | `UGameplayBehaviorsBlueprintFunctionLibrary` |
| `AddGameplayTagFilterToBlackboardKeySelector` | 为黑板的 `GameplayTag` 类型键添加标签过滤器，方便在编辑器中筛选 | `UGameplayBehaviorsBlueprintFunctionLibrary` |
| `GetBlackboardValueAsGameplayTagFromBlackboardComp` | 直接通过 `BlackboardComponent` 和键名读取 `GameplayTag` | `UGameplayBehaviorsBlueprintFunctionLibrary` |
| `SetValueAsGameplayTagForBlackboardComp` | 直接通过 `BlackboardComponent` 和键名写入 `GameplayTag` | `UGameplayBehaviorsBlueprintFunctionLibrary` |

### 自定义 Behavior 的蓝图事件

在 `UGameplayBehavior` 的子类 Blueprint 中，您可以重写以下事件（按优先级调用）：

- `OnTriggered`（通用）
- `OnTriggeredPawn`（当 Avatar 为 `APawn` 时触发）
- `OnTriggeredCharacter`（当 Avatar 为 `ACharacter` 时触发）
- `OnEnded`（行为结束时调用）

**典型蓝图连接**：
1. 创建 `UGameplayBehavior` 子蓝图（例如 `BP_MyBehavior`）。
2. 在子蓝图中实现 `OnTriggered` 事件，播放动画蒙太奇或运行自定义逻辑。
3. 在其他蓝图（如 AI Controller 或 Behavior Tree）中使用 `GameplayBehaviorSubsystem->TriggerBehavior` 节点（需通过 C++ 或蓝图函数库间接调用），传入行为配置和 Avatar。

---

## C++ 用法

### 头文件引入

```cpp
#include "GameplayBehavior.h"
#include "GameplayBehaviorSubsystem.h"
#include "GameplayBehaviorConfig.h"
```

### 基本用法

**触发一个简单的动画行为**：

```cpp
// 创建一个配置对象，指定要播放的蒙太奇
UGameplayBehaviorConfig_Animation* Config = NewObject<UGameplayBehaviorConfig_Animation>();
Config->AnimMontage = MyMontage;
Config->PlayRate = 1.0f;

// 获取 GameplayBehaviorSubsystem
if (UWorld* World = GetWorld())
{
    if (UGameplayBehaviorSubsystem* Subsystem = UGameplayBehaviorSubsystem::GetCurrent(World))
    {
        AActor* Avatar = MyPawn;
        Subsystem->TriggerBehavior(*Config, *Avatar);
    }
}
```

**停止指定类型的行为**：

```cpp
UGameplayBehaviorsBlueprintFunctionLibrary::StopGameplayBehavior(
    UGameplayBehavior_AnimationBased::StaticClass(),
    Avatar);
```

**创建一个自定义行为子类**：

```cpp
UCLASS()
class UMyCustomBehavior : public UGameplayBehavior
{
    GENERATED_BODY()
public:
    virtual bool Trigger(AActor& Avatar, const UGameplayBehaviorConfig* Config, AActor* SmartObjectOwner) override
    {
        // 自定义触发逻辑
        // ...
        return true; // 表示行为开始，需要后续调用 EndBehavior
    }

    virtual void EndBehavior(AActor& Avatar, const bool bInterrupted) override
    {
        // 清理资源
        Super::EndBehavior(Avatar, bInterrupted);
    }
};
```

**行为树中使用装饰器 `BTDecorator_GameplayTagQuery`**：

在行为树中添加该装饰器节点，在 `GameplayTagQuery` 属性中设置查询条件，`ActorForGameplayTagQuery` 指定从黑板读取哪个 Actor。运行时，装饰器会监听标签变化并实时更新条件。

### 进阶用法

#### 与 SmartObject 联动

`GameplayBehaviorConfig_BehaviorTree` 允许将一个行为树配置为行为，当 AI 使用 SmartObject 时自动运行：

```cpp
UGameplayBehaviorConfig_BehaviorTree* BTConfig = NewObject<UGameplayBehaviorConfig_BehaviorTree>();
BTConfig->BehaviorTree = LoadObject<UBehaviorTree>(nullptr, TEXT("/Game/AI/BT_SmartObjectAction"));
BTConfig->bRevertToPreviousBTOnFinish = true; // 结束后恢复之前的 BT

UGameplayBehaviorSubsystem::TriggerBehavior(*BTConfig, *Avatar, SmartObjectActor);
```

#### 自定义行为实例化策略

`EGameplayBehaviorInstantiationPolicy` 控制是否实例化行为对象：

- `Instantiate`：每次触发都创建新实例。
- `ConditionallyInstantiate`：通过 `NeedsInstance` 方法动态决定。
- `DontInstantiate`：使用 CDO，节省内存。

在自定义子类中重写 `virtual bool NeedsInstance(const UGameplayBehaviorConfig* Config) const override;`。

#### 黑板的 GameplayTag 键类型

`UBlackboardKeyType_GameplayTag` 允许在黑板上存储 `FGameplayTagContainer`，行为树节点可以直接读写。在编辑器中将 Blackboard 键的类型设为 `GameplayTag`，然后使用 `GetBlackboardValueAsGameplayTag` / `SetBlackboardValueAsGameplayTag` 访问。

---

## Demo 示例

以下是一个完整的 C++ 示例，演示自定义行为类及其使用。

**MyBehavior.h**:
```cpp
#pragma once

#include "GameplayBehavior.h"
#include "MyBehavior.generated.h"

UCLASS()
class UMyBehavior : public UGameplayBehavior
{
    GENERATED_BODY()
public:
    virtual bool Trigger(AActor& Avatar, const UGameplayBehaviorConfig* Config, AActor* SmartObjectOwner) override;
    virtual void EndBehavior(AActor& Avatar, const bool bInterrupted) override;
};
```

**MyBehavior.cpp**:
```cpp
#include "MyBehavior.h"
#include "GameFramework/Character.h"

bool UMyBehavior::Trigger(AActor& Avatar, const UGameplayBehaviorConfig* Config, AActor* SmartObjectOwner)
{
    // 可以在这里播放动画或执行自定义逻辑
    UE_LOG(LogTemp, Log, TEXT("MyBehavior triggered on %s"), *Avatar.GetName());

    // 行为开始，返回 true 表示需要后续调用 EndBehavior
    return true;
}

void UMyBehavior::EndBehavior(AActor& Avatar, const bool bInterrupted)
{
    UE_LOG(LogTemp, Log, TEXT("MyBehavior ended (interrupted=%d) on %s"), bInterrupted, *Avatar.GetName());
    Super::EndBehavior(Avatar, bInterrupted);
}
```

**调用示例（在 AIController 或某个地方）**:

```cpp
void AMyAIController::ExecuteCustomBehavior()
{
    UMyBehavior* Behavior = NewObject<UMyBehavior>();
    if (UGameplayBehaviorSubsystem* Subsystem = UGameplayBehaviorSubsystem::GetCurrent(GetWorld()))
    {
        Subsystem->TriggerBehavior(*Behavior, *GetPawn(), nullptr);
    }
}
```

---

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GameplayAbilities` | 需与 `AbilitySystemComponent` 交互（如动画蒙太奇播放） |
| `AIModule` | 行为树系统（`UBTDecorator`, `UBTTask` 等基类） |
| `GameplayTasks` | `UGameplayBehavior` 实现了 `IGameplayTaskOwnerInterface` |
| `GameplayTags` | 核心标签与查询支持 |
| `AnimationCore`（隐式） | 蒙太奇播放 |

**注意**：以上是编译本模块时必须的依赖。使用本插件的项目只需额外添加 `GameplayAbilities`（如已包含其他 AI 模块则通常已具备 `AIModule` 和 `GameplayTags`）。

---

## 维护状态

### 近期更新

- 2025-06-26 `ec900998` Added UE_INLINE_GENERATED_CPP_BY_NAME to source files (编译改进)
- 2025-04-23 `93a13080` Used LyraGame build target to find and convert... (DLL 存储改进)
- 2025-01-16 `4a9936fa` [BehaviorTree] replaced some ensure on blackboard asset by error reporting (健壮性提升)
- 2024-11-10 `66e9bb39` Removed all #if UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes (代码清理)
- 2024-09-27 `58cf817b` Create BTTask_SetKeyValueX for all blackboard key type (初始创建)

### 维护评价

- **创建时间**：2024年9月，至今约1年。
- **更新频率**：近一年内有多次实质性更新，最近一次在2025年6月，说明持续维护。
- **活跃度**：处于实验性阶段，但修复和改进较为积极。模块内的 `IsBetaVersion = true` 表明 API 可能仍会有变化。
- **推荐使用**：适合需要轻量级“即发即弃”行为机制的项目，尤其是与 SmartObject 或 GameplayAbilities 结合的场景。由于是实验性插件，建议在正式发布前关注 API 变动。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GameplayBehaviors)
- [官方文档](https://docs.unrealengine.com)（该插件暂无独立文档页）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GameplayBehaviors/Source/GameplayBehaviorsTestSuite)