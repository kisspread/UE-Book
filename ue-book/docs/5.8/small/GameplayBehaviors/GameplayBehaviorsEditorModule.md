# AI Behaviors

> Encapsulated fire-and-forget behaviors for AI agents

| 属性 | 值 |
|---|---|
| 中文名 | AI 行为封装 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GameplayBehaviorsModule` (Runtime), `GameplayBehaviorsModule` (UncookedOnly), `GameplayBehaviorsEditorModule` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-28 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GameplayBehaviors) | |

## 用途

GameplayBehaviors 提供了一套**可封装的"触发即忘"（fire-and-forget）AI 行为系统**。核心思想是：将 AI 代理（Agent）需要执行的行为封装为独立、自管理的对象，调用方触发行为后无需关心其生命周期——行为自行运行到完成或被中断，系统负责清理资源。

该插件与 **GameplayAbilities（GAS）** 紧密集成，利用 GameplayTags 作为行为标识和调度机制。它解决的核心问题是：在 GAS 框架下，AI 角色需要执行一系列复杂行为（如移动到目标、播放动画、交互等），但这些行为不应与某个特定 Ability 深度耦合，而应该是可复用、可独立调度的封装单元。

### 与传统 Ability/Task 的区别

| 传统方式 | GameplayBehaviors |
|---|---|
| 行为逻辑分散在多个 Ability 中 | 行为封装为独立对象，可跨 Ability 复用 |
| 调用方需管理行为生命周期 | 火即忘，系统自动管理 |
| 行为中断逻辑复杂 | 内置中断/排队机制 |

## 使用场景

- 你在做一个 AI 密集的游戏，AI 角色需要执行大量独立行为（巡逻、交互、战斗反应等）→ 用 GameplayBehaviors 将每个行为封装为独立单元
- 你已经在使用 GAS，但发现 Ability 中的行为逻辑难以复用 → 用 GameplayBehaviors 将行为从 Ability 中抽离
- 你需要 AI 行为的中断优先级管理（高优先级行为打断低优先级行为）→ GameplayBehaviors 内置行为栈管理
- 你在开发类似 Lyra 的项目，需要一套标准化的 AI 行为调度框架

## 蓝图用法

> ⚠️ 注意：该插件为实验性（IsBetaVersion=true）且默认未启用（EnabledByDefault=false），蓝图 API 可能在后续版本中发生变化。

### 核心节点

基于插件结构和 GAS 集成模式，核心类和功能如下：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `TriggerGameplayBehavior` | 在 AI 代理上触发一个封装行为 | `UGameplayBehaviorSubsystem` / `UGameplayBehavior` |
| `GetActiveGameplayBehavior` | 获取当前正在执行的行为 | `UGameplayBehaviorSubsystem` |

> 注：由于该插件仍处于实验阶段，具体 BlueprintCallable 函数需在启用插件后在编辑器中确认。

### 使用示例（蓝图描述）

典型使用流程：

1. 在 AI 控制器或 Pawn 上获取/创建 GameplayBehaviors 子系统引用
2. 通过 GameplayTag 或行为类引用来触发特定行为
3. 行为自动执行，无需额外管理其完成或清理
4. 如需响应行为完成事件，可通过委托/回调监听

## C++ 用法

### 头文件引入

```cpp
#include "GameplayBehaviorsModule.h"
```

### 模块检查

编辑器模块提供标准的单例访问模式：

```cpp
// 检查编辑器模块是否可用
if (IGameplayBehaviorsEditorModule::IsAvailable())
{
    IGameplayBehaviorsEditorModule& EditorModule = IGameplayBehaviorsEditorModule::Get();
}
```

来源：`Source/GameplayBehaviorsEditorModule/Public/GameplayBehaviorsEditorModule.h`

### 编辑器样式集成

编辑器模块提供了 GameplayTag 类型的可视化颜色标识：

```cpp
// 引用编辑器样式中的 GameplayTag 颜色
#include "GameplayBehaviorsEditorStyle.h"

FColor TagColor = FGameplayBehaviorsEditorStyle::GameplayTagTypeColor;
```

来源：`Source/GameplayBehaviorsEditorModule/Private/GameplayBehaviorsEditorStyle.h`

## Demo 示例

以下展示如何在自己的代码中正确加载和检查 GameplayBehaviors 模块：

```cpp
// MyAIController.h
#pragma once

#include "CoreMinimal.h"
#include "AIController.h"
#include "MyAIController.generated.h"

UCLASS()
class AMyAIController : public AAIController
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;

    UFUNCTION(BlueprintCallable, Category = "AI|Behaviors")
    void RequestBehavior(FGameplayTag BehaviorTag);

protected:
    UPROPERTY(EditAnywhere, Category = "AI|Behaviors")
    TArray<FGameplayTag> DefaultBehaviorTags;
};
```

```cpp
// MyAIController.cpp
#include "MyAIController.h"
#include "GameplayBehaviorsModule.h"
#include "GameplayTagsModule.h"

void AMyAIController::BeginPlay()
{
    Super::BeginPlay();

    // 确保 GameplayBehaviors 运行时模块已加载
    FModuleManager::Get().LoadModuleChecked<IGameplayBehaviorsModule>("GameplayBehaviorsModule");

    // 触发默认行为
    for (const FGameplayTag& Tag : DefaultBehaviorTags)
    {
        RequestBehavior(Tag);
    }
}

void AMyAIController::RequestBehavior(FGameplayTag BehaviorTag)
{
    // 通过 GameplayTag 触发封装行为
    // 行为将自行管理生命周期（fire-and-forget）
    // 具体 API 请参考插件内部 UGameplayBehavior 子类实现
}
```

> 注：完整的行为触发 API 取决于 `GameplayBehaviorsModule` 内部的 `UGameplayBehavior` 子类实现，建议在启用插件后查看源码中的具体类定义。

## 模块依赖

### GameplayBehaviorsModule 依赖

| 模块 | 用途 |
|---|---|
| `GameplayAbilities` | GAS 集成，提供 Ability 系统交互基础 |
| `GameplayTags` | 行为标识和调度的 GameplayTag 支持 |
| `AIModule` | AI 控制器和黑板集成 |

### GameplayBehaviorsEditorModule 依赖

| 模块 | 用途 |
|---|---|
| `GameplayBehaviorsModule` | 编辑器扩展依赖运行时模块 |
| `GameplayTags` | 编辑器中的 Tag 类型可视化 |

### GameplayBehaviorsTestSuite 依赖

| 模块 | 用途 |
|---|---|
| `EditorFramework` | 测试框架中的编辑器上下文 |
| `UnrealEd` | 编辑器自动化测试支持 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 宏 |
| 2026-03-27 | `2ef401e4` | FValueOrBlackboardKeyBase::ToString is not tool only | 修正 FValueOrBlackboardKeyBase::ToString 的模块限制 |
| 2026-03-27 | `3d027aeb` | Node memory cleanup | 节点内存清理优化 |
| 2025-06-26 | `ec900998` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. | 为源文件添加内联生成宏优化编译 |
| 2025-04-23 | `93a13080` | Used LyraGame build target to find and convert all files to have dllstorage on methods/staticvar ins | 使用 LyraGame 构建目标转换导出符号声明 |

### 维护评价

- **状态**：**维护中** — 最近一次更新在 2026 年 4 月，保持活跃
- **更新模式**：近期更新主要是编译器宏迁移、内存优化等基础维护工作，尚无重大功能新增
- **实验性警告**：该插件仍标记为 `IsBetaVersion=true` 且 `EnabledByDefault=false`，API 不稳定，可能在后续版本中发生 breaking changes
- **GAS 依赖**：强依赖 GameplayAbilities 插件，使用前需确保 GAS 已启用
- **推荐程度**：⚠️ **谨慎使用** — 适合对 GAS 有深入了解的开发者在原型阶段使用，不建议在生产环境中作为核心系统依赖。持续有维护更新但实验性标记意味着 Epic 尚未承诺长期支持

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GameplayBehaviors)
- 官方文档：无（.uplugin 中 DocsURL 为空）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GameplayBehaviors/Source/GameplayBehaviorsTestSuite)