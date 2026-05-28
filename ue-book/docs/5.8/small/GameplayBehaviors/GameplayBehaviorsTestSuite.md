# AI Behaviors

> Encapsulated fire-and-forget behaviors for AI agents

| 属性 | 值 |
|---|---|
| 中文名 | AI 行为模块 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GameplayBehaviorsModule` (Runtime), `GameplayBehaviorsModule` (UncookedOnly), `GameplayBehaviorsEditorModule` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-28 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GameplayBehaviors) | |

## 用途

GameplayBehaviors 插件为 AI 代理（Agent）提供了一套**封装式、即发即忘（fire-and-forget）的行为系统**。其核心设计理念是将 AI 的具体行为（如移动到目标、播放蒙太奇、使用物品等）封装为独立的 `UGameplayBehavior` 对象，由外部系统（如行为树、StateTree 或其他 AI 决策逻辑）触发执行，行为完成后自动结束，无需调用方持续管理生命周期。

该插件与 **GameplayAbilities（GAS）** 深度集成，复用了 GAS 的任务（AbilityTask）机制来处理异步操作（如等待动画播放完毕、等待移动到达等），使得行为可以复用 GAS 生态中的各种异步任务。同时，它通过 `UGameplayBehaviorConfig` 提供数据驱动的配置方式，支持在编辑器中序列化行为参数。

与传统的状态机或行为树节点不同，GameplayBehaviors 专注于**封装具体执行逻辑**，而将"何时触发"和"如何选择"留给上层决策系统，实现了关注点分离。

## 使用场景

- 你需要让 AI 角色执行一系列具体的动作（移动到位置、攻击、使用道具），但不想将这些逻辑硬编码在行为树节点中 → 用 GameplayBehaviors 封装为独立行为单元
- 你已经在使用 GAS（GameplayAbilities），希望 AI 行为也能复用 AbilityTask 的异步能力 → GameplayBehaviors 与 GAS 共享任务机制
- 你需要一种可序列化、可配置的 AI 行为定义方式，支持编辑器内调整参数 → 使用 `UGameplayBehaviorConfig` 进行数据驱动配置
- 你在构建 StateTree 或行为树驱动的 AI 系统，需要标准化的行为执行层 → GameplayBehaviors 作为底层行为执行引擎

## 蓝图用法

由于该插件版本为 0.1 且处于实验阶段，蓝图暴露的 API 较为有限。核心行为类主要通过 C++ 继承扩展。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| 触发行为 | 通过 SmartObject 或直接调用触发一个 GameplayBehavior | `UGameplayBehavior` |
| 行为配置 | 数据驱动的行为参数定义，可在编辑器中调整 | `UGameplayBehaviorConfig` |
| 行为子系统 | 管理全局 GameplayBehavior 的运行时子系统 | `UGameplayBehaviorSubsystem` |

### 使用示例（蓝图描述）

1. 创建一个自定义的 `UGameplayBehavior` 子类（蓝图或 C++）
2. 在 AI 决策逻辑（行为树 Task 或 StateTree Task）中，实例化该行为并调用 `Trigger` 方法
3. 行为内部通过 AbilityTask 机制执行异步操作（移动、播放动画等）
4. 行为执行完毕后自动清理，无需调用方管理

## C++ 用法

### 头文件引入

```cpp
#include "GameplayBehavior.h"
#include "GameplayBehaviorConfig.h"
#include "GameplayBehaviorSubsystem.h"
```

### 基本用法

基于 GameplayBehaviors 的架构设计，自定义一个最简单的行为：

```cpp
// 自定义 GameplayBehavior 子类
// 参考源码结构：GameplayBehaviorsModule/Classes/GameplayBehavior.h

#include "GameplayBehavior.h"

UCLASS()
class UMyGameplayBehavior : public UGameplayBehavior
{
    GENERATED_BODY()

public:
    // 行为被触发时调用
    virtual void Trigger(AActor& Owner, UGameplayBehaviorConfig* Config = nullptr) override;

protected:
    // 行为结束时的清理
    virtual void EndBehavior(AActor& Owner, bool bInterrupted = false);
};
```

### 进阶用法

结合 GameplayAbilities 的 AbilityTask 机制，在行为中执行异步操作：

```cpp
// 在行为中使用 AbilityTask 实现异步逻辑
// 参考源码：GameplayBehaviorsModule 中与 GAS 集成的任务相关代码

void UMyGameplayBehavior::Trigger(AActor& Owner, UGameplayBehaviorConfig* Config)
{
    Super::Trigger(Owner, Config);

    // 创建移动任务
    UAbilityTask* MoveTask = CreateMoveToLocationTask(/* params */);
    // 任务完成时回调
    MoveTask->OnCompleted.AddDynamic(this, &UMyGameplayBehavior::OnMoveCompleted);
}

void UMyGameplayBehavior::OnMoveCompleted()
{
    // 行为完成，通知上层
    EndBehavior(*GetOwnerActor(), false);
}
```

## Demo 示例

### .h 文件

```cpp
// MyAttackBehavior.h
#pragma once

#include "CoreMinimal.h"
#include "GameplayBehavior.h"
#include "MyAttackBehavior.generated.h"

class UGameplayBehaviorConfig;

UCLASS()
class MYGAME_API UMyAttackBehavior : public UGameplayBehavior
{
    GENERATED_BODY()

public:
    virtual void Trigger(AActor& Owner, UGameplayBehaviorConfig* Config = nullptr) override;

protected:
    virtual void EndBehavior(AActor& Owner, bool bInterrupted) override;

private:
    UFUNCTION()
    void OnMontageEnded(UAnimMontage* Montage, bool bInterrupted);
};
```

### .cpp 文件

```cpp
// MyAttackBehavior.cpp
#include "MyAttackBehavior.h"
#include "GameplayBehaviorConfig.h"
#include "GameFramework/Character.h"

void UMyAttackBehavior::Trigger(AActor& Owner, UGameplayBehaviorConfig* Config)
{
    Super::Trigger(Owner, Config);

    ACharacter* Character = Cast<ACharacter>(&Owner);
    if (!Character)
    {
        EndBehavior(Owner, true);
        return;
    }

    // 根据 Config 决定播放哪个攻击动画
    UAnimMontage* AttackMontage = nullptr;
    if (Config)
    {
        // 从配置中读取蒙太奇资产
    }

    if (AttackMontage)
    {
        UAnimInstance* AnimInstance = Character->GetMesh()->GetAnimInstance();
        if (AnimInstance)
        {
            AnimInstance->Montage_Play(AttackMontage);
            FOnMontageEnded EndDelegate;
            EndDelegate.BindUObject(this, &UMyAttackBehavior::OnMontageEnded);
            AnimInstance->Montage_SetEndDelegate(EndDelegate, AttackMontage);
        }
    }
    else
    {
        EndBehavior(Owner, false);
    }
}

void UMyAttackBehavior::OnMontageEnded(UAnimMontage* Montage, bool bInterrupted)
{
    EndBehavior(*GetOwnerActor(), bInterrupted);
}

void UMyAttackBehavior::EndBehavior(AActor& Owner, bool bInterrupted)
{
    Super::EndBehavior(Owner, bInterrupted);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GameplayAbilities` | 插件级别的依赖，提供 GAS 任务机制和 AbilitySystemComponent 集成 |
| `AIModule` | AI 行为树和感知系统集成 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移到新的 UE_LOGF 宏 |
| 2026-03-27 | `2ef401e4` | FValueOrBlackboardKeyBase::ToString is not tool only | 黑板键的 ToString 方法改为非仅工具可见 |
| 2026-03-27 | `3d027aeb` | Node memory cleanup | 节点内存清理优化 |
| 2025-06-26 | `ec900998` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files... | 为源文件添加内联生成代码宏优化编译 |
| 2025-04-23 | `93a13080` | Used LyraGame build target to find and convert all files... | 批量添加 DLL 导出标记 |

### 维护评价

- **版本状态**：版本号 0.1，标记为 Beta 和 Experimental，且 `EnabledByDefault=false`，表明这仍是一个未完成的实验性功能
- **更新活跃**：最近的更新集中在引擎基础设施升级（日志宏、编译优化、DLL导出标记），而非功能性更新
- **功能完善度**：作为一个"fire-and-forget"行为框架，核心架构已搭建，但缺乏公开的详细文档和丰富的内置行为类型
- **依赖关系**：强依赖 GameplayAbilities 插件，使用时需确保 GAS 已启用
- **建议**：适合用于 AI 行为系统的研究和原型开发，不建议在生产环境中重度依赖。如果项目已使用 GAS，可以考虑以该插件为基础构建自定义 AI 行为层

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GameplayBehaviors)
- [官方文档]()（暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GameplayBehaviors/Source/GameplayBehaviorsTestSuite)