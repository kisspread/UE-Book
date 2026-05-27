# AI Behaviors

> Encapsulated fire-and-forget behaviors for AI agents

| 属性 | 值 |
|---|---|
| 中文名 | AI 行为系统 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GameplayBehaviorsModule` (Runtime), `GameplayBehaviorsModule` (UncookedOnly), `GameplayBehaviorsEditorModule` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-28 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GameplayBehaviors) | |

## 用途

这个插件为 AI 智能体提供了一套 **封装式的"触发即忘"（fire-and-forget）行为框架**。核心理念是：将 AI 的离散动作（播放动画、执行行为树等）封装为独立的 `UGameplayBehavior` 对象，通过统一的子系统触发和管理。

与直接在行为树或 AI 控制器中硬编码行为逻辑不同，这个插件允许你：
- 将每个 AI 行为（如巡逻动画、检查物体、执行一段行为树）封装为可复用的蓝图类
- 通过 `UGameplayBehaviorSubsystem` 统一管理每个 AI 代理当前活跃的行为
- 与 Smart Object 系统集成，在交互点触发对应行为
- 支持 CDO 复用和实例化两种策略，优化性能

插件还附带了实用的 **GameplayTag 黑板扩展**，包括 GameplayTag 黑板键类型、基于 Tag 查询的行为树装饰器等。

## 使用场景

- 你在用 Smart Object 系统构建 AI 交互点 → 用 GameplayBehavior 封装每个交互动作
- 你需要 AI 在某些场景下播放一段动画蒙太奇，然后自动结束 → 用 `UGameplayBehavior_AnimationBased`
- 你需要 AI 临时切换到另一个行为树，完成后恢复原来的 → 用 `UGameplayBehavior_BehaviorTree`
- 你需要在行为树中基于 GameplayTag 查询做条件判断 → 用 `UBTDecorator_GameplayTagQuery`
- 你需要在黑板中存储 GameplayTag 数据 → 用 `UBlackboardKeyType_GameplayTag`
- 你需要将"触发行为 → 等待完成 → 后续处理"这套模式标准化 → 用这个插件的完整框架

## 蓝图用法

### 核心节点

**行为控制（UGameplayBehavior）**：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `TriggerBehavior` | 触发行为，返回是否成功 | `UGameplayBehavior` |
| `EndBehavior` | 正常结束行为 | `UGameplayBehavior` |
| `AbortBehavior` | 中断行为（等同于 EndBehavior(bInterrupted=true)） | `UGameplayBehavior` |
| `GetNextActorIndexInSequence` | 获取相关演员序列中的下一个索引 | `UGameplayBehavior` |

**蓝图可实现事件（BlueprintImplementableEvent）**：

| 事件 | 说明 | 所在类 |
|---|---|---|
| `OnTriggered` | 通用触发回调 | `UGameplayBehavior` |
| `OnTriggeredPawn` | Pawn 类型专用触发回调（优先级更高） | `UGameplayBehavior` |
| `OnTriggeredCharacter` | Character 类型专用触发回调（优先级最高） | `UGameplayBehavior` |
| `OnFinished` | 通用完成回调 | `UGameplayBehavior` |
| `OnFinishedPawn` | Pawn 类型完成回调 | `UGameplayBehavior` |
| `OnFinishedCharacter` | Character 类型完成回调 | `UGameplayBehavior` |

**黑板工具函数（GameplayBehaviorsBlueprintFunctionLibrary）**：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetBlackboardValueAsGameplayTag` | 从黑板键获取 GameplayTag（行为树节点用） | `UGameplayBehaviorsBlueprintFunctionLibrary` |
| `SetBlackboardValueAsGameplayTag` | 向黑板键写入 GameplayTag（行为树节点用） | `UGameplayBehaviorsBlueprintFunctionLibrary` |
| `AddGameplayTagFilterToBlackboardKeySelector` | 给黑板键选择器添加 Tag 过滤器 | `UGameplayBehaviorsBlueprintFunctionLibrary` |
| `GetBlackboardValueAsGameplayTagFromBlackboardComp` | 从黑板组件获取 GameplayTag | `UGameplayBehaviorsBlueprintFunctionLibrary` |
| `SetValueAsGameplayTagForBlackboardComp` | 向黑板组件写入 GameplayTag | `UGameplayBehaviorsBlueprintFunctionLibrary` |
| `GetTagContainer` | 从 FValueOrBBKey 获取 Tag 容器 | `UValueOrBBKey_GameplayTagBlueprintUtility` |

### 使用示例（蓝图描述）

**创建自定义行为蓝图**：
1. 新建蓝图类，父类选择 `GameplayBehavior` 或其子类（如 `GameplayBehavior_AnimationBased`）
2. 在事件图表中实现 `OnTriggered`（或更具体的 `OnTriggeredPawn` / `OnTriggeredCharacter`）
3. 在事件图表中实现 `OnFinished` 处理完成逻辑
4. 行为逻辑完成后，调用 `EndBehavior` 通知框架行为已结束

**通过子系统触发行为**：
1. 获取 `GameplayBehaviorSubsystem`（通过 `GetCurrent` 节点传入 World 上下文）
2. 创建行为配置（如 `GameplayBehaviorConfig_Animation`），设置蒙太奇等参数
3. 调用 `TriggerBehavior`，传入配置、Avatar 和 SmartObject Owner
4. 行为完成后会自动触发 `OnBehaviorFinished` 委托

**在行为树中使用 GameplayTag 查询**：
1. 在行为树中添加 `GameplayTagQuery` 装饰器
2. 指定要检查的 Actor 黑板键
3. 配置 `GameplayTagQuery` 表达式
4. 只有当 Actor 的 Tag 匹配查询时，装饰器下的子节点才会执行

## C++ 用法

### 头文件引入

```cpp
#include "GameplayBehavior.h"
#include "GameplayBehaviorSubsystem.h"
#include "GameplayBehaviorConfig.h"
#include "GameplayBehaviorsBlueprintFunctionLibrary.h"
#include "GameplayBehavior_AnimationBased.h"
#include "GameplayBehavior_BehaviorTree.h"
```

### 基本用法：创建自定义行为

继承 `UGameplayBehavior` 创建自定义行为类：

```cpp
// MyGameplayBehavior.h
#pragma once

#include "GameplayBehavior.h"
#include "MyGameplayBehavior.generated.h"

UCLASS(Blueprintable)
class UMyGameplayBehavior : public UGameplayBehavior
{
    GENERATED_BODY()

public:
    UMyGameplayBehavior(const FObjectInitializer& ObjectInitializer = FObjectInitializer::Get());

protected:
    // 重写 Trigger 实现自定义行为逻辑
    virtual bool Trigger(AActor& Avatar, const UGameplayBehaviorConfig* Config = nullptr, AActor* SmartObjectOwner = nullptr) override;

    // 重写 EndBehavior 处理清理
    virtual void EndBehavior(AActor& Avatar, const bool bInterrupted = false) override;
};

// MyGameplayBehavior.cpp
#include "MyGameplayBehavior.h"

UMyGameplayBehavior::UMyGameplayBehavior(const FObjectInitializer& ObjectInitializer)
    : Super(ObjectInitializer)
{
}

bool UMyGameplayBehavior::Trigger(AActor& Avatar, const UGameplayBehaviorConfig* Config, AActor* SmartObjectOwner)
{
    // 先调用父类（会触发对应的 BlueprintImplementableEvent）
    if (!Super::Trigger(Avatar, Config, SmartObjectOwner))
    {
        return false;
    }

    // 自定义行为逻辑...
    // ...

    return true;
}

void UMyGameplayBehavior::EndBehavior(AActor& Avatar, const bool bInterrupted)
{
    // 清理逻辑...
    // ...

    Super::EndBehavior(Avatar, bInterrupted);
}
```

### 基本用法：通过子系统触发行为

```cpp
// 通过配置触发行为
UGameplayBehaviorSubsystem* Subsystem = UGameplayBehaviorSubsystem::GetCurrent(GetWorld());
if (Subsystem)
{
    UGameplayBehaviorConfig_Animation* Config = NewObject<UGameplayBehaviorConfig_Animation>();
    Config->SetAnimMontage(MyMontage);
    Config->SetPlayRate(1.0f);

    // 静态方法触发，自动处理实例化逻辑
    UGameplayBehaviorSubsystem::TriggerBehavior(*Config, *AvatarActor, SmartObjectOwner);
}
```

### 基本用法：直接触发行为对象

```cpp
// 直接触发一个行为对象
UGameplayBehavior* Behavior = GetMyBehaviorInstance();
if (Behavior)
{
    UGameplayBehaviorSubsystem::TriggerBehavior(*Behavior, *AvatarActor, Config, SmartObjectOwner);

    // 绑定完成回调
    Behavior->GetOnBehaviorFinishedDelegate().AddLambda(
        [](UGameplayBehavior& FinishedBehavior, AActor& Avatar, bool bInterrupted)
        {
            UE_LOG(LogTemp, Log, TEXT("Behavior %s finished on %s, interrupted: %d"),
                *FinishedBehavior.GetName(), *Avatar.GetName(), bInterrupted);
        });
}
```

### 进阶用法：创建自定义配置和实例化策略

```cpp
// 自定义配置类
UCLASS()
class UMyBehaviorConfig : public UGameplayBehaviorConfig
{
    GENERATED_BODY()
public:
    UPROPERTY(EditAnywhere, Category = "Config")
    float Duration = 5.0f;

    UPROPERTY(EditAnywhere, Category = "Config")
    FGameplayTagContainer RequiredTags;
};

// 在自定义行为中使用 NeedsInstance 控制实例化策略
UCLASS()
class UMyConditionalBehavior : public UGameplayBehavior
{
    GENERATED_BODY()
public:
    UMyConditionalBehavior(const FObjectInitializer& ObjectInitializer = FObjectInitializer::Get())
        : Super(ObjectInitializer)
    {
        // 条件实例化：只有特定配置下才创建实例
        InstantiationPolicy = EGameplayBehaviorInstantiationPolicy::ConditionallyInstantiate;
    }

protected:
    virtual bool NeedsInstance(const UGameplayBehaviorConfig* Config) const override
    {
        const UMyBehaviorConfig* MyConfig = Cast<UMyBehaviorConfig>(Config);
        // 仅当配置包含特定 Tag 时需要实例化
        return MyConfig && MyConfig->RequiredTags.HasTag(FGameplayTag::RequestGameplayTag(FName("AI.Action.Custom")));
    }
};
```

### 进阶用法：停止特定行为

```cpp
// 停止指定类型的行为
UGameplayBehaviorSubsystem* Subsystem = UGameplayBehaviorSubsystem::GetCurrent(GetWorld());
if (Subsystem)
{
    Subsystem->StopBehavior(AvatarActor, UMyGameplayBehavior::StaticClass());
}

// 或通过静态函数库停止
UGameplayBehaviorsBlueprintFunctionLibrary::StopGameplayBehavior(UMyGameplayBehavior::StaticClass(), AvatarActor);
```

## Demo 示例

一个完整的自定义行为类，实现简单的"等待并完成"模式：

```cpp
// GameplayBehavior_WaitAndFinish.h
#pragma once

#include "GameplayBehavior.h"
#include "GameplayBehavior_WaitAndFinish.generated.h"

UCLASS(Blueprintable, meta=(DisplayName="Wait And Finish"))
class UGameplayBehavior_WaitAndFinish : public UGameplayBehavior
{
    GENERATED_BODY()

public:
    UGameplayBehavior_WaitAndFinish(const FObjectInitializer& ObjectInitializer = FObjectInitializer::Get());

    virtual bool Trigger(AActor& Avatar, const UGameplayBehaviorConfig* Config = nullptr, AActor* SmartObjectOwner = nullptr) override;
    virtual void EndBehavior(AActor& Avatar, const bool bInterrupted = false) override;

protected:
    virtual UWorld* GetWorld() const override;

    UFUNCTION()
    void OnWaitTimerExpired();

    UPROPERTY(EditDefaultsOnly, Category = "Wait")
    float WaitDuration = 3.0f;

    FTimerHandle WaitTimerHandle;
    TWeakObjectPtr<AActor> CurrentAvatar;
};
```

```cpp
// GameplayBehavior_WaitAndFinish.cpp
#include "GameplayBehavior_WaitAndFinish.h"
#include "Engine/World.h"
#include "TimerManager.h"

UGameplayBehavior_WaitAndFinish::UGameplayBehavior_WaitAndFinish(const FObjectInitializer& ObjectInitializer)
    : Super(ObjectInitializer)
{
}

bool UGameplayBehavior_WaitAndFinish::Trigger(AActor& Avatar, const UGameplayBehaviorConfig* Config, AActor* SmartObjectOwner)
{
    if (!Super::Trigger(Avatar, Config, SmartObjectOwner))
    {
        return false;
    }

    CurrentAvatar = &Avatar;
    UWorld* World = Avatar.GetWorld();
    if (World)
    {
        World->GetTimerManager().SetTimer(
            WaitTimerHandle,
            this,
            &UGameplayBehavior_WaitAndFinish::OnWaitTimerExpired,
            WaitDuration,
            /*bLoop=*/false
        );
    }
    return true;
}

void UGameplayBehavior_WaitAndFinish::EndBehavior(AActor& Avatar, const bool bInterrupted)
{
    // 清理定时器
    if (UWorld* World = Avatar.GetWorld())
    {
        World->GetTimerManager().ClearTimer(WaitTimerHandle);
    }
    CurrentAvatar.Reset();

    Super::EndBehavior(Avatar, bInterrupted);
}

UWorld* UGameplayBehavior_WaitAndFinish::GetWorld() const
{
    if (CurrentAvatar.IsValid())
    {
        return CurrentAvatar->GetWorld();
    }
    return nullptr;
}

void UGameplayBehavior_WaitAndFinish::OnWaitTimerExpired()
{
    if (CurrentAvatar.IsValid())
    {
        EndBehavior(*CurrentAvatar, false);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AIModule` | 行为树、黑板键类型、AI 控制器等基础设施 |
| `GameplayAbilities` | AbilitySystemComponent（动画行为中播放蒙太奇） |
| `GameplayTags` | GameplayTag 系统，行为标识和黑板扩展 |
| `GameplayTasks` | GameplayTask 框架，行为类实现 IGameplayTaskOwnerInterface |

> 插件还声明了对 `GameplayAbilities` 插件的硬依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移到 UE_LOGF 新格式 |
| 2026-03-27 | `2ef401e4` | FValueOrBlackboardKeyBase::ToString is not tool only | 修复 ToString 方法的编译条件限制 |
| 2026-03-27 | `3d027aeb` | Node memory cleanup | 清理行为树节点内存管理代码 |
| 2025-06-26 | `ec900998` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. | 添加内联生成宏以优化编译 |
| 2025-04-23 | `93a13080` | Used LyraGame build target to find and convert all files to have dllstorage on methods/staticvar ins | 统一模块导出宏为 DLL 互操作格式 |

### 维护评价

- **状态**：实验性（Beta），默认未启用
- **活跃度**：近期（2025-2026）有零星维护性提交，但均为代码质量改进，**无功能性更新**
- **自 2021 年创建以来**，该插件一直处于实验性状态，未升级为正式功能
- **已知限制**：
  - `GameplayBehavior_AnimationBased` 对同一 Avatar 同时只支持播放一个蒙太奇
  - `GameplayBehavior_BehaviorTree` 仅对 AI 控制的 Pawn 有效
  - 插件仍标记为 Beta，API 可能在未来版本中变更
- **是否推荐使用**：如果你的项目需要与 Smart Object 系统配合构建 AI 行为框架，可以参考此插件的设计模式。但由于其实验性状态，**生产环境使用需谨慎**，建议关注引擎后续版本的变动。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GameplayBehaviors)
- [官方文档]()（无）