# AI Behaviors

> Encapsulated fire-and-forget behaviors for AI agents

| 属性 | 值 |
|---|---|
| 中文名 | AI行为封装 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GameplayBehaviorsModule` (Runtime), `GameplayBehaviorsModule` (UncookedOnly), `GameplayBehaviorsEditorModule` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-28 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GameplayBehaviors) | |

## 用途
此插件为AI智能体提供了一套封装好的、可独立触发和执行的“行为”管理系统。它解决的核心问题是：如何将复杂的AI决策分解为一系列可复用、可组合、状态独立的“行为”单元。这些行为类似于“一次性”任务，执行完成即结束，旨在简化AI逻辑的模块化开发，特别适合与 Gameplay Ability System (GAS) 集成，为AI提供标准化的行为触发和执行框架。

## 使用场景
- 当你需要为AI角色定义一系列标准化的、可被状态树、行为树或其他AI逻辑触发执行的独立任务时。
- 当你的AI系统需要与 Gameplay Ability System (GAS) 深度集成，希望利用GAS的网络同步、预测和冷却等能力来管理AI行为时。
- 当你希望避免在行为树节点中编写大量复杂逻辑，转而将具体行为封装成独立的、可配置的“行为”资产或类时。

## 蓝图用法
该插件主要面向程序员，蓝图中暴露的核心接口有限，主要用于配置和触发行为。

### 核心类
| 类名 | 说明 |
|---|---|
| `UGameplayBehaviorConfig` | 行为配置的基类，用于定义一个行为的参数。 |
| `UGameplayBehavior` | 行为逻辑的基类，定义了行为执行的生命周期（激活、执行、结束）。 |
| `UGameplayBehaviorSubsystem` | 子系统，用于管理行为的注册和查找。 |
| `AActor` | 任何Actor都可以作为行为的执行者（`Subject`）。 |

### 使用示例
1.  在C++中创建自定义的 `UGameplayBehavior` 子类，并重写 `ActivateBehavior`, `OnFinished` 等函数。
2.  在需要触发的逻辑中（如AI控制器、游戏模式或通过GAS），获取 `UGameplayBehaviorSubsystem`，调用 `TriggerBehavior` 并传入行为类、执行者（Subject）、目标Actor和配置对象。

## C++ 用法
主要用法是通过继承 `UGameplayBehavior` 来创建自定义行为，并通过子系统来触发它们。

### 头文件引入
```cpp
#include "GameplayBehavior.h"
#include "GameplayBehaviorSubsystem.h"
```

### 基本用法
定义并触发一个简单的行为。
```cpp
// MyGameplayBehavior.h
#pragma once
#include "GameplayBehavior.h"
#include "MyGameplayBehavior.generated.h"

UCLASS()
class UMyGameplayBehavior : public UGameplayBehavior
{
    GENERATED_BODY()
public:
    virtual void ActivateBehavior(AActor& Subject, AActor* SmartObjectOwner = nullptr, UGameplayBehaviorConfig* Config = nullptr) override;
};

// MyGameplayBehavior.cpp
#include "MyGameplayBehavior.h"

void UMyGameplayBehavior::ActivateBehavior(AActor& Subject, AActor* SmartObjectOwner, UGameplayBehaviorConfig* Config)
{
    Super::ActivateBehavior(Subject, SmartObjectOwner, Config);
    // 行为逻辑，例如播放动画、移动到点等
    UE_LOG(LogTemp, Log, TEXT("MyGameplayBehavior Activated on: %s"), *Subject.GetName());
    // ... 逻辑完成后调用 EndBehavior
    EndBehavior(Subject, *Config);
}

// 在某个地方触发行为（例如在AI控制器中）
if (UGameplayBehaviorSubsystem* Subsystem = UGameplayBehaviorSubsystem::Get(Subject->GetWorld()))
{
    Subsystem->TriggerBehavior(UMyGameplayBehavior::StaticClass(), *Subject, nullptr, nullptr);
}
```

### 进阶用法
与 Gameplay Ability System 集成，行为内部可以拥有并激活GAS技能。
```cpp
// 在你的UGameplayBehavior子类中
UPROPERTY(EditDefaultsOnly, Category = "GAS")
TSubclassOf<UGameplayAbility> AbilityToGrantAndActivate;

virtual void ActivateBehavior(AActor& Subject, ...) override
{
    Super::ActivateBehavior(Subject, ...);
    // ... 省略查找ASC逻辑
    if (UAbilitySystemComponent* ASC = UAbilitySystemBlueprintLibrary::GetAbilitySystemComponent(&Subject))
    {
        FGameplayAbilitySpec AbilitySpec(AbilityToGrantAndActivate, 1, INDEX_NONE, this);
        ASC->GiveAbility(AbilitySpec);
        ASC->TryActivateAbilityByClass(AbilityToGrantAndActivate);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GameplayAbilities` | 核心依赖，提供GAS框架，用于行为与技能的集成。 |
| `AIModule` | 可能用于AI行为树或黑板的高级集成。 |
| `NavigationSystem` | 若行为涉及寻路，可能需要此模块。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏统一迁移到 UE_LOGF。 |
| 2026-03-27 | `2ef401e4` | FValueOrBlackboardKeyBase::ToString is not tool only | 移除了对特定方法的编辑器工具限制。 |
| 2026-03-27 | `3d027aeb` | Node memory cleanup | 清理了节点内存，可能涉及状态树节点。 |
| 2025-06-26 | `ec900998` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. | 为源文件添加了内联生成代码宏，优化编译。 |
| 2025-04-23 | `93a13080` | Used LyraGame build target to find and convert all files to have dllstorage on methods/staticvar ins | 统一了DLL导出宏，以确保二进制兼容性。 |

### 维护评价
该插件仍处于**实验性阶段**（`IsBetaVersion=true`），默认未启用（`EnabledByDefault=false`）。虽然版本号仅为0.1，但从Git历史看，在2026年初仍有活跃的底层维护更新（如代码清理、编译优化、二进制兼容性修复），表明它仍在被关注和维护，但并非核心功能模块。由于其“实验性”标签和较低的版本号，**不建议在生产项目中直接依赖**，更适合作为技术研究、原型开发或学习AI行为框架设计的参考。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GameplayBehaviors)
- [官方文档]() (无)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GameplayBehaviors/Source/GameplayBehaviorsTestSuite)