# AI Behaviors

> Encapsulated fire-and-forget behaviors for AI agents

| 属性 | 值 |
|---|---|
| 中文名 | AI 行为 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GameplayBehaviorsModule` (Runtime), `GameplayBehaviorsModule` (UncookedOnly), `GameplayBehaviorsEditorModule` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-28 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GameplayBehaviors) | |

## 用途

GameplayBehaviors 提供了一套 **AI 行为封装框架**，让 AI 代理（Agent）能够执行"触发即忘"（fire-and-forget）的离散行为。该插件解决的核心问题是：在 Smart Object 或行为树驱动的 AI 系统中，如何以统一的方式定义、触发和管理一段自包含的 AI 行为（如播放动画、运行临时行为树、执行移动等）。

插件建立了一套完整的生命周期管理机制（Trigger → 执行 → EndBehavior/AbortBehavior），并通过 `UGameplayBehaviorSubsystem` 世界子系统追踪每个 AI 代理当前活跃的行为，支持行为中断和回调通知。同时提供了 GameplayTag 在黑板（Blackboard）中的原生支持，以及基于标签查询的行为树装饰器节点。

该插件依赖 **GameplayAbilities** 插件，与 GAS（Gameplay Ability System）生态深度整合。

## 使用场景

- 你在做 Smart Object 系统，需要 AI 角色到达交互点后执行特定动作（如坐在长椅上播放坐下动画）→ 使用 `UGameplayBehavior_AnimationBased`
- 你需要 AI 角色临时切换到另一个行为树执行一段任务（如调查声响），完成后恢复原始行为树 → 使用 `UGameplayBehavior_BehaviorTree`
- 你需要在行为树中基于 GameplayTag 条件控制分支逻辑 → 使用 `UBTDecorator_GameplayTagQuery`
- 你需要在黑板中存储和读取 GameplayTag 值 → 使用 `UBlackboardKeyType_GameplayTag` 及相关蓝图函数库
- 你需要自定义全新的 AI 行为类型（如交互、巡逻等）→ 继承 `UGameplayBehavior` 并蓝图实现

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `K2_TriggerBehavior` | 触发一个游戏行为，传入 Avatar、配置和 SmartObject 拥有者 | `UGameplayBehavior` |
| `K2_EndBehavior` | 正常结束行为 | `UGameplayBehavior` |
| `K2_AbortBehavior` | 中断行为（内部调用 EndBehavior 并标记 bInterrupted=true） | `UGameplayBehavior` |
| `K2_GetNextActorIndexInSequence` | 在 RelevantActors 数组中获取下一个有效 Actor 索引 | `UGameplayBehavior` |
| `StopGameplayBehavior` | 静态函数，强制停止指定 Avatar 上的特定类型行为 | `UGameplayBehaviorsBlueprintFunctionLibrary` |
| `GetBlackboardValueAsGameplayTag` | 从行为树节点获取黑板中的 GameplayTag 值 | `UGameplayBehaviorsBlueprintFunctionLibrary` |
| `SetBlackboardValueAsGameplayTag` | 在行为树节点中设置黑板的 GameplayTag 值 | `UGameplayBehaviorsBlueprintFunctionLibrary` |
| `GetBlackboardValueAsGameplayTagFromBlackboardComp` | 直接从 BlackboardComponent 获取 GameplayTag | `UGameplayBehaviorsBlueprintFunctionLibrary` |
| `SetValueAsGameplayTagForBlackboardComp` | 直接向 BlackboardComponent 设置 GameplayTag | `UGameplayBehaviorsBlueprintFunctionLibrary` |
| `AddGameplayTagFilterToBlackboardKeySelector` | 为黑板键选择器添加 GameplayTag 过滤 | `UGameplayBehaviorsBlueprintFunctionLibrary` |
| `GetTagContainer` | 从 FValueOrBBKey_GameplayTagContainer 提取标签容器 | `UValueOrBBKey_GameplayTagBlueprintUtility` |

### 蓝图可实现事件（BlueprintImplementableEvent）

创建 `UGameplayBehavior` 的蓝图子类时，可以选择性实现以下事件：

| 事件 | 说明 | 优先级 |
|---|---|---|
| `OnTriggered` | 通用触发事件，Avatar 为 AActor | 最低 |
| `OnTriggeredPawn` | Avatar 为 Pawn 时触发 | 中 |
| `OnTriggeredCharacter` | Avatar 为 Character 时触发（最具体，优先级最高） | 最高 |
| `OnFinished` | 通用完成事件 | 最低 |
| `OnFinishedPawn` | Pawn 完成事件 | 中 |
| `OnFinishedCharacter` | Character 完成事件 | 最高 |

触发时，系统会按 **Character > Pawn > Actor** 的优先级选择最具体的事件调用。

### 使用示例（蓝图描述）

**创建自定义行为蓝图：**

1. 右键创建新蓝图类，父类选择 `GameplayBehavior`
2. 在蓝图中实现 `OnTriggeredCharacter` 事件
3. 在事件中编写你的行为逻辑（如播放蒙太奇、等待一段时间等）
4. 行为完成后调用 `K2_EndBehavior` 结束行为

**在行为树中使用：**

1. 添加 `BTTask_StopGameplayBehavior` 节点来停止当前行为
2. 添加 `BTDecorator_GameplayTagQuery` 装饰器，配置 GameplayTag 查询条件
3. 添加 `BTTask_SetKeyValueGameplayTag` 节点在黑板中设置标签值
4. 在黑板中创建 `GameplayTag` 类型的键（使用 `BlackboardKeyType_GameplayTag`）

## C++ 用法

### 头文件引入

```cpp
#include "GameplayBehavior.h"
#include "GameplayBehaviorSubsystem.h"
#include "GameplayBehaviorConfig_Animation.h"
#include "GameplayBehaviorConfig_BehaviorTree.h"
#include "GameplayBehaviorsBlueprintFunctionLibrary.h"
```

### 基本用法

通过子系统触发行为，来源：`GameplayBehaviorSubsystem.h`

```cpp
// 获取世界子系统
UGameplayBehaviorSubsystem* Subsystem = UGameplayBehaviorSubsystem::GetCurrent(GetWorld());

// 方式1：通过行为对象触发
UGameplayBehavior* Behavior = NewObject<UGameplayBehavior_AnimationBased>(this);
UGameplayBehaviorSubsystem::TriggerBehavior(*Behavior, *AvatarActor, /*Config=*/nullptr, /*SmartObjectOwner=*/SmartObjectActor);

// 方式2：通过配置触发（配置会自行创建或获取行为实例）
UGameplayBehaviorConfig_Animation* Config = NewObject<UGameplayBehaviorConfig_Animation>();
UGameplayBehaviorSubsystem::TriggerBehavior(*Config, *AvatarActor, SmartObjectActor);
```

### 进阶用法

**自定义行为子类并管理生命周期：**

来源：`GameplayBehavior.h`、`GameplayBehaviorSubsystem.h`

```cpp
// 停止特定类型的行为
bool bStopped = Subsystem->StopBehavior(AvatarActor, UMyCustomBehavior::StaticClass());

// 静态函数直接停止
bool bStopped = UGameplayBehaviorsBlueprintFunctionLibrary::StopGameplayBehavior(
    UMyCustomBehavior::StaticClass(), AvatarActor);

// 监听行为完成回调
FOnGameplayBehaviorFinished& Delegate = Behavior->GetOnBehaviorFinishedDelegate();
Delegate.AddUObject(this, &AMyActor::OnBehaviorCompleted);

void AMyActor::OnBehaviorCompleted(UGameplayBehavior& Behavior, AActor& Avatar, const bool bInterrupted)
{
    // bInterrupted 为 true 表示行为被中断而非正常完成
}
```

**行为实例化策略：**

来源：`GameplayBehavior.h`

```cpp
// 通过 InstantiationPolicy 控制行为的实例化方式：
// - Instantiate: 始终创建新实例
// - ConditionallyInstantiate: 根据 NeedsInstance() 决定是否创建实例
// - DontInstantiate: 直接使用 CDO
bool bInstanced = Behavior->IsInstanced(Config);
```

## Demo 示例

```cpp
// MyPunchBehavior.h
#pragma once

#include "GameplayBehavior.h"
#include "MyPunchBehavior.generated.h"

UCLASS()
class UMyPunchBehavior : public UGameplayBehavior
{
    GENERATED_BODY()

public:
    UMyPunchBehavior(const FObjectInitializer& ObjectInitializer);

protected:
    // C++ 中重写 Trigger 实现自定义逻辑
    virtual bool Trigger(AActor& InAvatar, const UGameplayBehaviorConfig* Config, AActor* SmartObjectOwner) override;
};
```

```cpp
// MyPunchBehavior.cpp
#include "MyPunchBehavior.h"

UMyPunchBehavior::UMyPunchBehavior(const FObjectInitializer& ObjectInitializer)
    : Super(ObjectInitializer)
{
}

bool UMyPunchBehavior::Trigger(AActor& InAvatar, const UGameplayBehaviorConfig* Config, AActor* SmartObjectOwner)
{
    // 调用父类 Trigger（会自动调用蓝图事件）
    if (!Super::Trigger(InAvatar, Config, SmartObjectOwner))
    {
        return false;
    }

    // 你的自定义逻辑
    // ...

    // 行为完成后结束
    EndBehavior(InAvatar, /*bInterrupted=*/false);
    return true;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GameplayAbilities` | 插件级依赖，提供 AbilitySystemComponent 集成 |
| `GameplayTags` | GameplayTag 系统支持 |
| `GameplayTasks` | 行为中使用 GameplayTask（IGameplayTaskOwnerInterface） |
| `AIModule` | 行为树相关类（UBTDecorator、UBTTaskNode、UBehaviorTreeComponent） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 宏 |
| 2026-03-27 | `2ef401e4` | FValueOrBlackboardKeyBase::ToString is not tool only | 修复 ToString 方法的工具限定符 |
| 2026-03-27 | `3d027aeb` | Node memory cleanup | 行为树节点内存清理优化 |
| 2025-06-26 | `ec900998` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applie | 添加内联生成宏优化编译 |
| 2025-04-23 | `93a13080` | Used LyraGame build target to find and convert all files to have dllstorage on methods/staticvar ins | 修复 DLL 导出符号声明 |

### 维护评价

- **状态**：活跃维护中。最近的更新集中在 2026 年 3-4 月，主要是代码质量改进（日志宏迁移、内存清理、编译优化）
- **创建时间**：2021 年 9 月，已有约 5 年历史
- **实验性标记**：仍标记为 `IsBetaVersion=true`，且 `EnabledByDefault=false`，说明 Epic 尚未将其定为稳定 API
- **推荐程度**：该插件与 Smart Object 系统深度关联，如果你的项目使用 Smart Object 驱动 AI 行为，这是必需的基础设施。但由于仍处于实验阶段，API 可能在未来版本中发生变化，建议做好适配准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GameplayBehaviors)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GameplayBehaviors/Source/GameplayBehaviorsTestSuite)