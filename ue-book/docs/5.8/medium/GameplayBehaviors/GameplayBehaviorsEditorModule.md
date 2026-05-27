# AI Behaviors

> Encapsulated fire-and-forget behaviors for AI agents

| 属性 | 值 |
|---|---|
| 中文名 | 游戏行为 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GameplayBehaviorsModule` (Runtime, UncookedOnly), `GameplayBehaviorsEditorModule` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-28 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GameplayBehaviors) | |

## 用途

GameplayBehaviors 插件为 AI 代理提供了一种**封装式、即发即忘（fire-and-forget）**的行为系统。它建立在 GameplayAbilities（GAS）系统之上，允许将 AI 行为定义为独立的、可复用的组件，无需维护持续状态即可触发执行。

该插件解决了以下问题：

- **行为封装**：将复杂的 AI 行为逻辑封装成独立单元，降低行为树节点的复杂度
- **与 GAS 集成**：利用 GameplayAbilities 的标签系统、效果系统来驱动 AI 行为，实现与角色技能系统的统一管理
- **黑板键支持**：通过 `FValueOrBlackboardKeyBase` 等类型支持行为树黑板键的灵活取值，既可使用固定值也可引用黑板变量
- **节点内存管理**：提供行为树节点的内存清理机制，避免 AI 行为节点的内存泄漏

简而言之，这个插件让 AI 的行为逻辑可以像技能一样被触发、管理和复用，而不是全部塞进行为树节点里。

## 使用场景

- 你在做 AI 驱动的游戏，需要让 NPC 触发一次性行为（如施放技能、播放特定动画序列）→ 用 GameplayBehaviors
- 你已经在项目中使用 GameplayAbilities（GAS），希望 AI 也能复用相同的技能标签和效果系统 → 用 GameplayBehaviors
- 你需要在行为树节点中引用黑板变量，同时支持固定值回退 → 插件的 `FValueOrBlackboardKeyBase` 体系可满足需求
- 你希望将 AI 行为从庞大的行为树节点中解耦出来，做成可复用模块 → 用 GameplayBehaviors

> ⚠️ **注意**：此插件当前默认禁用（`EnabledByDefault: false`），且处于 Beta 实验阶段。需要在项目设置中手动启用，并确保 GameplayAbilities 插件已启用。

## 蓝图用法

> 由于当前可用的源码仅包含编辑器模块（GameplayBehaviorsEditorModule），运行时模块（GameplayBehaviorsModule）的核心 BlueprintCallable API 未在本次分析范围内。以下基于编辑器模块的功能进行说明。

### 编辑器功能

GameplayBehaviorsEditorModule 主要提供编辑器集成支持：

| 功能 | 说明 |
|---|---|
| 模块接口 | 通过 `IGameplayBehaviorsEditorModule` 提供模块的单例访问 |
| 编辑器样式 | `FGameplayBehaviorsEditorStyle` 提供 GameplayTag 类型的专属颜色标识（`GameplayTagTypeColor`） |

### 模块可用性检查（蓝图中不直接可用，但 C++ 中常用）

在使用前检查模块是否已加载：

```cpp
if (IGameplayBehaviorsEditorModule::IsAvailable())
{
    auto& EditorModule = IGameplayBehaviorsEditorModule::Get();
    // 使用编辑器模块功能
}
```

## C++ 用法

### 头文件引入

```cpp
// 编辑器模块
#include "GameplayBehaviorsEditorModule.h"

// 运行时模块（核心功能）
#include "GameplayBehaviorsModule.h"
```

### 基本用法 - 编辑器模块访问

```cpp
// 检查模块可用性并获取单例
if (IGameplayBehaviorsEditorModule::IsAvailable())
{
    IGameplayBehaviorsEditorModule& EditorModule = IGameplayBehaviorsEditorModule::Get();
    // 使用编辑器模块提供的功能
}
```

### 获取编辑器样式

```cpp
#include "GameplayBehaviorsEditorStyle.h"

// 获取编辑器样式实例
FGameplayBehaviorsEditorStyle& Style = FGameplayBehaviorsEditorStyle::Get();

// 使用 GameplayTag 类型的颜色
FColor TagColor = FGameplayBehaviorsEditorStyle::GameplayTagTypeColor;
```

### 黑板键值引用

基于 git 历史中的 `FValueOrBlackboardKeyBase` 类型，插件支持黑板键引用模式：

```cpp
// 典型用法：一个值可以是固定值，也可以引用黑板键
// 当实际使用时通过解析获取最终值
// 具体 API 请参考运行时模块源码中的 FValueOrBlackboardKeyBase 及其子类
```

## Demo 示例

> 由于此插件为实验性 Beta 且默认禁用，以下为最小化集成示例。

### 启用插件

在项目的 `.uproject` 文件中添加：

```json
{
    "Plugins": [
        {
            "Name": "GameplayAbilities",
            "Enabled": true
        },
        {
            "Name": "GameplayBehaviors",
            "Enabled": true
        }
    ]
}
```

### 最小 C++ 集成示例

**MyAIBehaviorComponent.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "GameplayBehaviorsEditorModule.h"
#include "MyAIBehaviorComponent.generated.h"

UCLASS(ClassGroup=(AI), meta=(BlueprintSpawnableComponent))
class MYGAME_API UMyAIBehaviorComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UMyAIBehaviorComponent();

    virtual void BeginPlay() override;

    /** 检查 GameplayBehaviors 插件是否可用 */
    UFUNCTION(BlueprintPure, Category = "AI|Behaviors")
    bool IsBehaviorSystemAvailable() const;

protected:
    /** 触发一个 fire-and-forget 行为 */
    UFUNCTION(BlueprintCallable, Category = "AI|Behaviors")
    void TriggerBehavior(FGameplayTag BehaviorTag);
};
```

**MyAIBehaviorComponent.cpp**

```cpp
#include "MyAIBehaviorComponent.h"
#include "GameplayBehaviorsModule.h"

UMyAIBehaviorComponent::UMyAIBehaviorComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UMyAIBehaviorComponent::BeginPlay()
{
    Super::BeginPlay();

    if (IsBehaviorSystemAvailable())
    {
        UE_LOG(LogTemp, Log, TEXT("GameplayBehaviors system is ready for AI: %s"),
            *GetOwner()->GetName());
    }
}

bool UMyAIBehaviorComponent::IsBehaviorSystemAvailable() const
{
    // 检查 GameplayBehaviors 模块是否已加载
    return FModuleManager::Get().IsModuleLoaded(TEXT("GameplayBehaviorsModule"));
}

void UMyAIBehaviorComponent::TriggerBehavior(FGameplayTag BehaviorTag)
{
    if (!IsBehaviorSystemAvailable())
    {
        UE_LOG(LogTemp, Warning, TEXT("GameplayBehaviors module not loaded"));
        return;
    }

    // 在此触发具体的 gameplay behavior
    // 具体 API 取决于运行时模块提供的行为类接口
}
```

## 模块依赖

### 插件依赖

| 插件 | 用途 |
|---|---|
| `GameplayAbilities` | 提供 GAS（Gameplay Ability System）基础设施，包括标签系统、效果系统 |

### 模块依赖

| 模块 | 用途 |
|---|---|
| `GameplayAbilities` | 核心 GAS 模块，提供 GameplayTag、GameplayEffect 等基础设施 |
| `AIModule` | AI 子系统，提供行为树、黑板等基础能力 |

> 测试模块 GameplayBehaviorsTestSuite 还额外依赖 `EditorFramework` 和 `UnrealEd`。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到新的 UE_LOGF 格式 |
| 2026-03-27 | `2ef401e4` | FValueOrBlackboardKeyBase::ToString is not tool only | 移除 ToString 方法的工具限制，使其在非工具环境下可用 |
| 2026-03-27 | `3d027aeb` | Node memory cleanup | 清理行为树节点的内存管理逻辑 |
| 2025-06-26 | `ec900998` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. | 为源文件添加内联生成宏，优化编译性能 |
| 2025-04-23 | `93a13080` | Used LyraGame build target to find and convert all files to have dllstorage on methods/staticvar | 统一方法和静态变量的 DLL 导出声明 |

### 维护评价

- **状态**：**活跃维护中** — 最近一次更新距今不到 1 个月（2026-04-14）
- **更新频率**：2026 年内已有 3 次提交，2025 年有 2 次提交，更新节奏稳定
- **更新内容**：包含实质性功能改进（黑板键值 API 修正、节点内存清理），不仅是编译适配
- **成熟度**：仍处于 **Beta 实验阶段**，API 可能随版本变化
- **风险提示**：
  - 默认禁用，需手动启用
  - 依赖 GameplayAbilities 插件，增加了耦合性
  - 作为实验性插件，未来可能被合并到其他系统或发生重大变更

**推荐**：如果你的项目已经使用 GAS（GameplayAbilities），且需要封装式的 AI 行为管理，可以尝试使用。但由于仍在 Beta，不建议在生产关键路径上深度依赖。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GameplayBehaviors)
- [GameplayAbilities 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GameplayBehaviors)（前置依赖）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GameplayBehaviors/Source/GameplayBehaviorsTestSuite)