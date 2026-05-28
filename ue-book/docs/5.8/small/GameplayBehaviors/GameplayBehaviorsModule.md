# AI Behaviors

> Encapsulated fire-and-forget behaviors for AI agents（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | AI 行为系统 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GameplayBehaviorsModule` (Runtime), `GameplayBehaviorsModule` (UncookedOnly), `GameplayBehaviorsEditorModule` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-28 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GameplayBehaviors) | |

## 用途

GameplayBehaviors 提供了一个**封装式的 AI 行为框架**，用于让 AI 代理执行"即发即忘"（fire-and-forget）的独立行为单元。

该插件解决的核心问题是：在使用行为树或 EQS 驱动的 AI 系统中，某些复杂行为（播放动画蒙太奇、运行临时行为树、与 SmartObject 交互等）需要被封装为独立的、可组合的行为模块，而不是直接硬编码在行为树节点里。

关键设计思路：
- 每个行为是一个 `UGameplayBehavior` 子类，可被蓝图继承
- 行为通过 `UGameplayBehaviorSubsystem` 统一管理，跟踪每个 AI 代理当前活跃的行为
- 行为配置与行为实例分离，通过 `UGameplayBehaviorConfig` 传递参数
- 深度集成 GameplayAbilities、行为树黑板、SmartObjects 系统

## 使用场景

- 你需要让 AI 角色执行一个完整的动画序列（如坐下、拾取物品），并在完成后自动通知调用方 → 用 `UGameplayBehavior_AnimationBased`
- 你需要让 AI 角色临时运行一棵行为树（如调查声音来源），完成后恢复原行为树 → 用 `UGameplayBehavior_BehaviorTree`
- 你需要一个统一的子系统来跟踪多个 AI 代理各自正在进行的行为，并支持中断 → 用 `UGameplayBehaviorSubsystem`
- 你需要在行为树装饰器中基于 GameplayTag 查询来决定节点是否激活 → 用 `UBTDecorator_GameplayTagQuery`
- 你需要在黑板中存储和查询 GameplayTag 类型的值 → 用 `UBlackboardKeyType_GameplayTag`

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `K2_TriggerBehavior` | 在指定 Avatar 上触发一个行为 | `UGameplayBehavior` |
| `K2_EndBehavior` | 正常结束指定 Avatar 上的行为 | `UGameplayBehavior` |
| `K2_AbortBehavior` | 中断指定 Avatar 上的行为 | `UGameplayBehavior` |
| `K2_GetNextActorIndexInSequence` | 从 RelevantActors 列表中获取下一个有效的 Actor 索引 | `UGameplayBehavior` |
| `OnTriggered` | 行为被触发时的蓝图事件（泛型） | `UGameplayBehavior` |
| `OnTriggeredPawn` | 行为被触发时的蓝图事件（Pawn 专用，优先级高于 OnTriggered） | `UGameplayBehavior` |
| `OnTriggeredCharacter` | 行为被触发时的蓝图事件（Character 专用，最高优先级） | `UGameplayBehavior` |
| `OnFinished` | 行为完成时的蓝图事件 | `UGameplayBehavior` |
| `OnFinishedPawn` | 行为完成时的蓝图事件（Pawn 专用） | `UGameplayBehavior` |
| `OnFinishedCharacter` | 行为完成时的蓝图事件（Character 专用） | `UGameplayBehavior` |
| `GetTagContainer` | 从 FValueOrBBKey_GameplayTagContainer 获取 Tag 容器值 | `UValueOrBBKey_GameplayTagBlueprintUtility` |
| `StopGameplayBehavior` | 强制停止指定类的行为（静态函数） | `UGameplayBehaviorsBlueprintFunctionLibrary` |
| `GetBlackboardValueAsGameplayTag` | 从行为树节点读取黑板中的 GameplayTag | `UGameplayBehaviorsBlueprintFunctionLibrary` |
| `SetBlackboardValueAsGameplayTag` | 向行为树节点的黑板写入 GameplayTag | `UGameplayBehaviorsBlueprintFunctionLibrary` |
| `AddGameplayTagFilterToBlackboardKeySelector` | 为黑板 Key 选择器添加 GameplayTag 过滤 | `UGameplayBehaviorsBlueprintFunctionLibrary` |

### 使用示例（蓝图描述）

**创建自定义行为子类：**
1. 创建一个新的蓝图类，父类选择 `GameplayBehavior`
2. 重写 `OnTriggeredCharacter` 事件（如果目标是 Character）
3. 在事件中执行你的逻辑，完成后调用 `K2_EndBehavior` 通知系统行为已完成

**触发行为：**
1. 获取 `GameplayBehaviorSubsystem` 实例（通过 `GetCurrent` 静态函数）
2. 调用 `TriggerBehavior` 静态函数，传入行为配置、Avatar Actor 和可选的 SmartObject Owner
3. 注册 `OnBehaviorFinished` 委托以接收完成通知

**行为树中停止行为：**
1. 在行为树中添加 `BTTask_StopGameplayBehavior` 节点
2. 设置 `BehaviorToStop` 为要停止的行为类（留空则停止所有行为）

## C++ 用法

### 头文件引入

```cpp
#include "GameplayBehaviorSubsystem.h"
#include "GameplayBehavior.h"
#include "GameplayBehaviorConfig.h"
#include "GameplayBehavior_AnimationBased.h"
#include "GameplayBehaviorConfig_Animation.h"
#include "GameplayBehaviorsBlueprintFunctionLibrary.h"
#include "BlackboardKeyType_GameplayTag.h"
```

### 基本用法

通过子系统触发一个行为：

```cpp
// 来源: Public/GameplayBehaviorSubsystem.h

// 获取当前世界的子系统
UGameplayBehaviorSubsystem* Subsystem = UGameplayBehaviorSubsystem::GetCurrent(GetWorld());

// 静态方法直接触发（会自动获取子系统实例）
UGameplayBehaviorConfig Config;  // 或其子类
AActor* AvatarActor = /* 你的 AI 代理 */;
AActor* SmartObjectOwner = nullptr;  // 可选

// 方式一：通过 Config 触发（会自动创建行为实例或使用 CDO）
UGameplayBehaviorSubsystem::TriggerBehavior(Config, *AvatarActor, SmartObjectOwner);

// 方式二：直接传入行为实例
UGameplayBehavior* Behavior = /* 获取或创建行为实例 */;
UGameplayBehaviorSubsystem::TriggerBehavior(*Behavior, *AvatarActor, &Config, SmartObjectOwner);
```

停止指定代理上的行为：

```cpp
// 来源: Public/GameplayBehaviorSubsystem.h
UGameplayBehaviorSubsystem* Subsystem = UGameplayBehaviorSubsystem::GetCurrent(GetWorld());
if (Subsystem)
{
    // 停止特定类的行为
    Subsystem->StopBehavior(*AvatarActor, UGameplayBehavior_AnimationBased::StaticClass());
}
```

### 进阶用法

**自定义行为子类（C++）：**

```cpp
// 来源: Public/GameplayBehavior.h + Public/GameplayBehavior_AnimationBased.h

UCLASS()
class UMyCustomBehavior : public UGameplayBehavior
{
    GENERATED_BODY()

protected:
    // 重写 Trigger 来自定义触发逻辑
    virtual bool Trigger(AActor& Avatar, const UGameplayBehaviorConfig* Config, AActor* SmartObjectOwner) override
    {
        // 自定义逻辑...
        
        // 调用父类以触发蓝图事件
        return Super::Trigger(Avatar, Config, SmartObjectOwner);
    }

    virtual void EndBehavior(AActor& Avatar, const bool bInterrupted) override
    {
        // 清理逻辑...
        Super::EndBehavior(Avatar, bInterrupted);
    }

    // 如果需要按配置条件决定是否创建实例
    virtual bool NeedsInstance(const UGameplayBehaviorConfig* Config) const override
    {
        // 返回 true 表示即使是 CDO 也要创建实例
        return true;
    }
};
```

**播放动画蒙太奇行为：**

```cpp
// 来源: Public/GameplayBehavior_AnimationBased.h + Public/GameplayBehaviorConfig_Animation.h

// 配置动画行为
UGameplayBehaviorConfig_Animation* AnimConfig = NewObject<UGameplayBehaviorConfig_Animation>();
// AnimMontage, PlayRate, StartSectionName, bLoop 通过 Config 的属性设置

// 或直接使用 Behavior 的 PlayMontage 方法
UGameplayBehavior_AnimationBased* AnimBehavior = NewObject<UGameplayBehavior_AnimationBased>();
UAnimMontage* Montage = /* 加载的蒙太奇 */;
AnimBehavior->PlayMontage(*AvatarActor, *Montage, 1.0f, NAME_None, false);
```

**在行为树装饰器中使用 GameplayTag 查询：**

```cpp
// 来源: Public/AI/BTDecorator_GameplayTagQuery.h
// 在行为树编辑器中配置：
// - ActorForGameplayTagQuery: 指向要检查的黑板 Actor Key
// - GameplayTagQuery: 设置要匹配的 Tag 查询表达式
// 装饰器会自动监听 Tag 变化并更新条件状态
```

**黑板中存储 GameplayTag：**

```cpp
// 来源: Public/BlackboardKeyType_GameplayTag.h + Public/GameplayBehaviorsBlueprintFunctionLibrary.h

// 通过蓝图函数库读写
FGameplayTagContainer Tags = UGameplayBehaviorsBlueprintFunctionLibrary::GetBlackboardValueAsGameplayTag(
    BTNodeOwner, BlackboardKeySelector);

// 直接通过黑板组件读写
FGameplayTagContainer Tags = UGameplayBehaviorsBlueprintFunctionLibrary::GetBlackboardValueAsGameplayTagFromBlackboardComp(
    BlackboardComp, FName("MyTagKey"));

UGameplayBehaviorsBlueprintFunctionLibrary::SetValueAsGameplayTagForBlackboardComp(
    BlackboardComp, FName("MyTagKey"), NewTagContainer);
```

## Demo 示例

### 自定义行为子类

```cpp
// MyPatrolBehavior.h
#pragma once

#include "CoreMinimal.h"
#include "GameplayBehavior.h"
#include "MyPatrolBehavior.generated.h"

UCLASS()
class UMyPatrolBehavior : public UGameplayBehavior
{
    GENERATED_BODY()

public:
    UMyPatrolBehavior(const FObjectInitializer& ObjectInitializer = FObjectInitializer::Get());

protected:
    // Character 专用触发事件（最高优先级）
    UFUNCTION(BlueprintImplementableEvent, Category = GameplayBehavior, DisplayName = "OnPatrolTriggered")
    void K2_OnPatrolTriggered(ACharacter* Avatar);

    // 通用触发：路由到最具体的事件
    virtual bool Trigger(AActor& Avatar, const UGameplayBehaviorConfig* Config, AActor* SmartObjectOwner) override;
    virtual void EndBehavior(AActor& Avatar, const bool bInterrupted) override;

private:
    // 使用 RelevantActors 作为巡逻路径点
    int32 CurrentWaypointIndex = 0;

    UFUNCTION()
    void OnReachedWaypoint();
};
```

```cpp
// MyPatrolBehavior.cpp
#include "MyPatrolBehavior.h"
#include "GameplayBehaviorConfig.h"
#include "GameplayTasksComponent.h"

UMyPatrolBehavior::UMyPatrolBehavior(const FObjectInitializer& ObjectInitializer)
    : Super(ObjectInitializer)
{
    ActionTag = FGameplayTag::RequestGameplayTag(FName("AI.Behavior.Patrol"));
}

bool UMyPatrolBehavior::Trigger(AActor& Avatar, const UGameplayBehaviorConfig* Config, AActor* SmartObjectOwner)
{
    if (!Super::Trigger(Avatar, Config, SmartObjectOwner))
    {
        return false;
    }

    CurrentWaypointIndex = 0;

    // 如果有配置，从配置中读取参数
    if (Config)
    {
        // 从 Config 获取自定义参数...
    }

    // 利用 RelevantActors 作为巡逻路径点
    if (RelevantActors.Num() > 0)
    {
        // 开始向第一个路径点移动...
        // 移动完成后调用 OnReachedWaypoint
    }

    return true;
}

void UMyPatrolBehavior::EndBehavior(AActor& Avatar, const bool bInterrupted)
{
    // 清理移动状态
    CurrentWaypointIndex = 0;

    Super::EndBehavior(Avatar, bInterrupted);
}

void UMyPatrolBehavior::OnReachedWaypoint()
{
    CurrentWaypointIndex++;
    if (CurrentWaypointIndex >= RelevantActors.Num())
    {
        // 巡逻完成
        if (TransientAvatar)
        {
            EndBehavior(*TransientAvatar, false);
        }
    }
    else
    {
        // 继续前往下一个路径点...
    }
}
```

## 模块依赖

从 Build.cs 分析，该插件的运行时模块依赖 GameplayAbilities 插件。

| 模块 | 用途 |
|---|---|
| `GameplayAbilities` | Gameplay Ability System 集成（GAS 核心模块） |
| `GameplayTags` | GameplayTag 系统支持 |
| `GameplayTasks` | GameplayTask 框架（行为可拥有任务） |
| `AIModule` | 行为树、黑板、AI 控制器集成 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF | 将 UE_LOG 日志宏迁移到 UE_LOGF 新宏 |
| 2026-03-27 | `2ef401e4` | FValueOrBlackboardKeyBase::ToString is not tool only | 修正 ToString 函数的编译条件，不再限于工具模块 |
| 2026-03-27 | `3d027aeb` | Node memory cleanup | 行为树节点内存清理优化 |
| 2025-06-26 | `ec900998` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files | 为源文件添加内联生成代码宏以优化编译 |
| 2025-04-23 | `93a13080` | Used LyraGame build target to find and convert all files to have dllstorage on methods/staticvar ins | 修正 DLL 导出符号（DLL export）声明 |

### 维护评价

- **年龄**：约 5 年，自 2021 年 9 月创建
- **状态**：仍处于**实验性**阶段（`IsBetaVersion=true`，`EnabledByDefault=false`），从未正式毕业到稳定版
- **更新频率**：近期有零星更新（2025-2026 年），但均为编译兼容性和代码规范化修复，**无功能性更新**
- **已知限制**：
  - `GameplayBehavior_AnimationBased` 同一 Avatar 同时只支持一个蒙太奇播放，多次请求会相互覆盖
  - `GameplayBehavior_BehaviorTree` 仅适用于 AI 控制的 Pawn
  - API 标记为 `MinimalAPI`，外部模块可访问的接口有限
- **综合评价**：该插件已被 Lyra 示例项目使用（从 recent commit 可见 LyraGame 相关改动），但 Epic 可能已在用 StateTree 等新系统替代。作为实验性插件，API 可能在未来版本发生破坏性变更。适合在原型开发和内部项目中使用，不建议作为生产系统的核心依赖。

⚠️ **警告**：该插件自创建起一直处于实验性状态，且超过 1 年无实质性功能更新。Epic 可能已将注意力转向 StateTree 等替代方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GameplayBehaviors)
- 官方文档（无）
- [GameplayAbilities 依赖插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GameplayBehaviors)