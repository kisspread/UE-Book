# AI Behaviors

> Encapsulated fire-and-forget behaviors for AI agents

| 属性 | 值 |
|---|---|
| 中文名 | 行为管理器 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GameplayBehaviorsModule` (Runtime), `GameplayBehaviorsModule` (UncookedOnly), `GameplayBehaviorsEditorModule` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-28 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GameplayBehaviors) | |

## 用途

`GameplayBehaviors` 插件提供了一套用于管理 AI 代理“即发即忘”行为的系统。它允许开发者将复杂的行为逻辑封装成可复用的模块。其核心思想是将行为分解为三个部分：
1.  **行为定义 (`UGameplayBehaviorDefinition`)**: 定义行为的静态数据和属性。
2.  **行为实例 (`UGameplayBehavior`)**: 在运行时表示一个正在执行的行为，并处理具体逻辑。
3.  **行为节点 (`UGameplayBehaviorNode`)**: 用于在行为图（如 StateTree 或自定义图表）中编排行为，控制其执行流程。

这个系统旨在简化 AI 行为（如施放技能、进行特定动作序列）的创建、组合和管理，特别适用于需要模块化、事件驱动的 AI 逻辑。

## 使用场景

- **ARPG 怪物行为管理**：为不同怪物类型定义一套行为库（如远程攻击、近战连招、召唤），并根据战况动态触发。
- **射击游戏中的 NPC 逻辑**：封装“寻找掩体”、“投掷手雷”、“呼叫支援”等独立行为，在交战状态下选择性地执行。
- **动作游戏的组合攻击**：将每个攻击招式（上段斩、下段刺）定义为一个行为，实现连续技的触发。
- **需要与 GameplayAbility 系统协同的 AI**：该插件的依赖项包含 `GameplayAbilities`，因此非常适合管理由技能系统驱动的 AI 行为。

## 蓝图用法

本插件的蓝图接口主要通过其核心类暴露。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateNewDefinition` | 创建一个新的行为定义资产。 | `UGameplayBehaviorDefinition` |
| `Set` | 设置行为定义中的属性值。 | `UGameplayBehaviorDefinition` |
| `AddNewNode` | 向行为定义中添加一个新的行为节点。 | `UGameplayBehaviorDefinition` |
| `Start` | 在一个行为定义上启动一个行为实例。 | `UGameplayBehavior` |
| `Abort` | 中止一个正在运行的行为实例。 | `UGameplayBehavior` |
| `Finish` | 通知行为已完成。 | `UGameplayBehavior` |

### 使用示例（蓝图描述）

1.  **创建行为定义**：在内容浏览器中右键创建一个新的 `GameplayBehaviorDefinition` 资产。
2.  **编排行为节点**：打开该资产，在图表编辑器中拖入不同的 `GameplayBehaviorNode`（如 “SpawnProjectile” 节点），并将它们连接起来。
3.  **配置节点参数**：在节点的细节面板中，设置技能标识、目标Actor、生成物类等参数。这些参数可以硬编码或绑定到黑板键。
4.  **AI角色触发**：在AI的行为树或状态树中，使用“启动行为”节点，引用您创建的行为定义资产来触发整个行为序列。

## C++ 用法

本插件的 C++ 用法主要集中在创建自定义的行为节点和在代码中驱动行为流程。

### 头文件引入

```cpp
#include "GameplayBehaviorsModule.h"
```

### 基本用法

创建并启动一个简单的行为定义（来源: `GameplayBehaviorsTestSuite`）：
```cpp
// 假设您已经有了一个 UGameplayBehaviorDefinition* 变量 BehaviorDef
UGameplayBehavior* RunningBehavior = UGameplayBehavior::Start(*BehaviorDef, *OwnerActor, *AvatarActor);

if (RunningBehavior)
{
    // 行为已成功启动，可以存储指针以便后续控制
    // ...
}
```

### 进阶用法

自定义行为评估器（Evaluator），用于判断节点是否可以执行（来源: `GameplayBehaviorsModule`）：
```cpp
// 创建一个自定义的评估器类
class UMyBehaviorEvaluator : public UGameplayBehaviorEvaluator
{
    GENERATED_BODY()
public:
    // 重写评估函数，返回true表示条件满足
    virtual bool Evaluate(const FGameplayBehaviorContext& Context) const override
    {
        // 例如：检查AI的法力值是否足够
        const APawn* Pawn = Cast<APawn>(Context.AvatarActor);
        if (Pawn)
        {
            // 这里可以访问黑板、角色属性等进行复杂判断
            return true;
        }
        return false;
    }
};

// 在构建行为节点时，将其设置为评估器
// MyBehaviorNode->SetEvaluator(UMyBehaviorEvaluator::StaticClass());
```

## Demo 示例

一个最小的自定义行为节点头文件（`.h`）和实现（`.cpp`）示例。

**MyCustomBehaviorNode.h**
```cpp
#pragma once

#include "GameplayBehaviorNode.h"
#include "MyCustomBehaviorNode.generated.h"

UCLASS()
class MYPROJECT_API UMyCustomBehaviorNode : public UGameplayBehaviorNode
{
    GENERATED_BODY()

public:
    UMyCustomBehaviorNode();

    // 重写以实现节点激活时的逻辑
    virtual void OnActivate(FGameplayBehaviorContext& Context) override;

    // 可选：重写以实现节点结束时的清理逻辑
    virtual void OnFinished(const FGameplayBehaviorContext& Context) override;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MyBehavior")
    float MyCustomDuration = 2.0f;
};
```

**MyCustomBehaviorNode.cpp**
```cpp
#include "MyCustomBehaviorNode.h"
#include "TimerManager.h"

UMyCustomBehaviorNode::UMyCustomBehaviorNode()
{
    NodeName = TEXT("My Custom Action");
}

void UMyCustomBehaviorNode::OnActivate(FGameplayBehaviorContext& Context)
{
    Super::OnActivate(Context);

    // 执行自定义逻辑，例如播放特效或动画
    if (Context.AvatarActor)
    {
        UE_LOG(LogTemp, Warning, TEXT("My custom behavior node activated!"));
        
        // 设置一个计时器，MyCustomDuration秒后结束此节点
        Context.AvatarActor->GetWorldTimerManager().SetTimer(
            TimerHandle, 
            this, 
            &UMyCustomBehaviorNode::Execute_FinishNode, // 假设父类提供的完成节点方法
            MyCustomDuration, 
            false
        );
    }
}

void UMyCustomBehaviorNode::OnFinished(const FGameplayBehaviorContext& Context)
{
    Super::OnFinished(Context);
    // 清理资源
    Context.AvatarActor->GetWorldTimerManager().ClearTimer(TimerHandle);
}
```

## 模块依赖

要使用此插件，你的模块需要依赖 `GameplayBehaviorsModule`。它本身又依赖于 `GameplayAbilities` 插件。

| 模块 | 用途 |
|---|---|
| `GameplayAbilities` | 核心技能系统，行为管理器与其深度集成 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志系统到新宏，无功能影响。 |
| 2026-03-27 | `2ef401e4` | FValueOrBlackboardKeyBase::ToString is not tool only | 使黑板键的ToString函数在非编辑器工具环境也可用。 |
| 2026-03-27 | `3d027aeb` | Node memory cleanup | 节点内存清理与优化。 |
| 2025-06-26 | `ec900998` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files... | 为生成的源文件添加内联宏，改善编译性能。 |
| 2025-04-23 | `93a13080` | Used LyraGame build target to find and convert all files to have dllstorage... | 使用Lyra构建目标转换文件，设置DLL导出宏。 |

### 维护评价

该插件**状态为实验性且未默认启用**，表明 Epic 仍在评估和开发其功能。
- **年龄**：约 5 年，但作为从内部项目迁移出来的模块，其设计已相对成熟。
- **更新频率**：近期更新主要是引擎框架层面的适配（如日志系统、编译宏、DLL导出）和底层优化（内存清理），**没有重大的功能性新增或API变更**。
- **活跃度**：维护不活跃，属于底层基础维护状态。
- **已知问题/限制**：作为实验性插件，其API和行为可能在未来版本中发生破坏性更改。依赖关系可能带来额外的编译和运行时复杂度。
- **推荐使用**：适用于需要高度模块化、可组合AI行为的复杂项目，并且团队愿意承担实验性API变更的风险。对于简单AI，建议使用更成熟的行为树或状态树方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GameplayBehaviors)
- [官方文档]() (暂无)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GameplayBehaviors/Source/GameplayBehaviorsTestSuite)