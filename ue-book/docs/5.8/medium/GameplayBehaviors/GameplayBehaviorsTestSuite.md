# AI Behaviors

> Encapsulated fire-and-forget behaviors for AI agents

| 属性 | 值 |
|---|---|
| 中文名 | 游戏行为系统 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GameplayBehaviorsModule` (Runtime), `GameplayBehaviorsModule` (UncookedOnly), `GameplayBehaviorsEditorModule` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-28 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GameplayBehaviors) | |

## 用途

GameplayBehaviors 插件为 AI 代理（Agent）提供了一套**封装式的"发射即忘"（fire-and-forget）行为系统**。它允许开发者将 AI 的一次性或短期行为（如执行攻击、使用物品、移动到某处）封装为独立的行为对象，由 AI 控制器或行为树系统触发后自主执行，无需持续管理。

该插件与 **GameplayAbilities** 紧密集成，意味着它可以利用 GAS（Gameplay Ability System）的能力激活、效果应用等基础设施，将 AI 行为与游戏玩法系统统一管理。

**核心价值**：将 AI 行为从复杂的黑板/行为树逻辑中解耦，使其成为可复用、可测试、可数据驱动的独立单元。

## 使用场景

- 你在制作一个需要 AI 角色执行复杂一次性行为（如施法、互动、巡逻切换）的游戏 → 用 GameplayBehaviors 封装这些行为
- 你已经在使用 GAS（GameplayAbilities）管理角色能力，希望 AI 也复用同一套能力系统 → 用 GameplayBehaviors 将 GA 与 AI 行为桥接
- 你需要 AI 行为能够被动态添加/移除，而不修改行为树结构 → 用 GameplayBehaviors 作为行为的容器
- 你在用 StateTree 或其他高级 AI 系统，需要可组合的行为片段 → GameplayBehaviors 提供行为封装层

## 蓝图用法

该插件作为运行时行为框架，其核心 API 以 C++ 类为主，蓝图可调用函数较少，主要面向开发者在 C++ 层扩展。

### 核心节点

由于该插件为实验性框架层，核心交互多通过 C++ 子类化实现。蓝图层面主要通过行为组件（Behavior Component）与 AI 控制器交互。

| 节点 | 说明 | 所在类 |
|---|---|---|
| 行为激活/停止 | 触发或终止一个封装行为 | 通过 AI 控制器集成 |

## C++ 用法

### 头文件引入

```cpp
#include "GameplayBehaviorsModule.h"
```

### 基本用法

GameplayBehaviors 的核心模式是：定义一个行为类，由 AI 系统在需要时激活。

```cpp
// 1. 定义一个自定义游戏行为
UCLASS()
class UMyGameplayBehavior : public UGameplayBehavior
{
    GENERATED_BODY()

public:
    // 行为激活时的入口
    virtual void ActivateBehavior(AActor& Avatar, UGameplayBehaviorConfig* Config = nullptr) override;
    
    // 行为结束时的清理
    virtual void EndBehavior(AActor& Avatar, bool bInterrupted = false) override;
};
```

### 进阶用法

结合 GameplayAbilities 系统，将 GA 能力作为行为触发的桥梁：

```cpp
// 在 GameplayAbility 中触发一个 Behavior
void UMyAbility::ActivateAbility(...)
{
    Super::ActivateAbility(...);
    
    UGameplayBehavior* Behavior = NewObject<UMyGameplayBehavior>(this);
    // 将行为与当前 Avatar Actor 关联并激活
    Behavior->ActivateBehavior(*GetAvatarActorFromActorInfo(), BehaviorConfig);
}
```

```cpp
// 通过 BehaviorComponent 管理多个并发行为
if (UBehaviorComponent* BehaviorComp = Avatar.FindComponentByClass<UBehaviorComponent>())
{
    BehaviorComp->RequestGameplayBehavior(NewBehavior, Config);
}
```

## Demo 示例

```cpp
// MyGameplayBehavior.h
#pragma once

#include "GameplayBehavior.h"
#include "MyGameplayBehavior.generated.h"

UCLASS()
class MYGAME_API UMyGameplayBehavior : public UGameplayBehavior
{
    GENERATED_BODY()

public:
    virtual void ActivateBehavior(AActor& Avatar, UGameplayBehaviorConfig* Config = nullptr) override
    {
        Super::ActivateBehavior(Avatar, Config);
        
        // 执行行为逻辑，例如：播放动画、应用效果等
        UE_LOG(LogTemp, Log, TEXT("GameplayBehavior activated on %s"), *Avatar.GetName());
        
        // 完成后自动结束（fire-and-forget 模式）
        EndBehavior(Avatar, false);
    }

    virtual void EndBehavior(Actor& Avatar, bool bInterrupted = false) override
    {
        // 清理逻辑
        UE_LOG(LogTemp, Log, TEXT("GameplayBehavior ended (interrupted: %s)"),
            bInterrupted ? TEXT("true") : TEXT("false"));
        
        Super::EndBehavior(Avatar, bInterrupted);
    }
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GameplayAbilities` | GAS 能力系统集成，行为可桥接 GA 能力 |
| `GameplayBehaviorsTestSuite` | 自动化测试套件（仅测试用） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到 UE_LOGF 新格式 |
| 2026-03-27 | `2ef401e4` | FValueOrBlackboardKeyBase::ToString is not tool only | 移除 ToString 的仅工具限制 |
| 2026-03-27 | `3d027aeb` | Node memory cleanup | 节点内存清理优化 |
| 2025-06-26 | `ec900998` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. | 添加内联生成宏优化编译 |
| 2025-04-23 | `93a13080` | Used LyraGame build target to find and convert all files to have dllstorage on methods/staticvar | 修正 DLL 导出符号 |

### 维护评价

- **状态**：仍处于实验性阶段（`IsBetaVersion=true`，位于 `Experimental` 目录）
- **活跃度**：2026 年仍有持续更新（宏迁移、内存清理等），属于**活跃维护**
- **风险**：实验性插件 API 可能随时变化，不建议在生产环境重度依赖
- **建议**：适合探索性项目或原型开发使用；正式项目中建议关注其是否会在后续版本移出 Experimental 阶段

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GameplayBehaviors)
- [官方文档]()（暂无）