# Gameplay Abilities

> Adds GameplayEffect and GameplayAbility classes to handle complicated gameplay interactions.

| 属性 | 值 |
|---|---|
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GameplayAbilities` (Runtime), `GameplayAbilitiesEditor` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2016-11-15 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GameplayAbilities) | |

## 用途

GameplayAbilities (GAS) 是 Unreal Engine 中用于构建复杂游戏逻辑的核心框架。它不仅仅是一个技能系统，而是一个完整的、可扩展的**游戏性效果与能力管理框架**。它解决了以下核心问题：

1.  **技能生命周期管理**：提供 `UGameplayAbility` 类来标准化技能的激活、执行、结束流程，支持实例化策略、网络同步策略等。
2.  **属性与效果系统**：通过 `UGameplayEffect` 和 `FGameplayAttribute` 管理角色的属性（如生命值、法力值），并定义临时或永久的效果来修改这些属性（如伤害、治疗、增益/减益）。
3.  **标签驱动逻辑**：深度集成 `GameplayTags`，用于驱动技能的激活条件、效果的应用规则、以及游戏逻辑的触发（如 `GameplayCue`）。
4.  **网络同步与预测**：内置对客户端预测和服务器权威逻辑的支持，简化了多人游戏中的技能同步问题。
5.  **可扩展性**：通过蓝图、C++ 以及数据驱动的方式，允许开发者构建从简单的被动技能到复杂的、多阶段、多目标的主动技能。

## 使用场景

-   **MOBA/ARPG 游戏**：实现英雄的主动技能、被动天赋、装备效果、Buff/Debuff 系统。
-   **射击游戏**：管理武器开火、弹药消耗、换弹、特殊能力（如冲刺、格挡）的逻辑。
-   **回合制策略游戏**：处理单位行动、技能释放、状态效果（如中毒、眩晕）的结算。
-   **任何需要复杂游戏逻辑的项目**：当游戏逻辑涉及属性修改、状态管理、条件触发和网络同步时，GAS 提供了一个经过验证的、结构化的解决方案。

## 蓝图用法

GameplayAbilitiesEditor 模块为蓝图编辑器提供了专门的节点和工具，用于创建和编辑能力蓝图。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GameplayCue.*` 事件 | 在蓝图中响应 `GameplayCue` 事件的自定义事件节点。 | `UK2Node_GameplayCueEvent` |
| 延迟能力调用 | 用于在能力蓝图中调用异步（延迟）的 `GameplayTask`。 | `UK2Node_LatentAbilityCall` |

### 使用示例（蓝图描述）

1.  **创建能力蓝图**：
    -   在内容浏览器中右键，选择 `Blueprint Class`。
    -   在父类选择窗口中，搜索并选择 `GameplayAbility` 或其子类。
    -   这将使用 `UGameplayAbilitiesBlueprintFactory` 创建一个新的能力蓝图。

2.  **处理 GameplayCue**：
    -   在角色蓝图的事件图表中，右键添加事件。
    -   搜索 `GameplayCue`，选择如 `GameplayCue.Hero.Skill.Fire` 这样的事件。
    -   这会创建一个 `UK2Node_GameplayCueEvent` 节点，用于处理该特定 Cue 的触发（如播放特效、音效）。

3.  **编辑 GameplayEffect**：
    -   创建 `GameplayEffect` 资产后，其属性面板会使用 `FAttributeDetails` 和 `FScalableFloatDetails` 进行自定义显示，方便配置属性修改和基于等级的缩放曲线。

## C++ 用法

GameplayAbilitiesEditor 模块主要提供编辑器扩展功能，其核心运行时逻辑在 `GameplayAbilities` 模块中。以下示例基于编辑器模块的头文件。

### 头文件引入

```cpp
#include "GameplayAbilitiesEditorModule.h"
#include "GameplayAbilityAudit.h"
```

### 基本用法

**自定义 GameplayEffect 创建菜单**：
你可以通过配置 `UGameplayEffectCreationMenu` 来定制在编辑器中创建新 `GameplayEffect` 时的菜单路径和默认名称。
（来源：`Engine/Plugins/Runtime/GameplayAbilities/Source/GameplayAbilitiesEditor/Public/GameplayEffectCreationMenu.h`）

```cpp
// 在你的项目设置或模块启动代码中
UGameplayEffectCreationMenu* Menu = GetMutableDefault<UGameplayEffectCreationMenu>();
if (Menu)
{
    FGameplayEffectCreationData NewEntry;
    NewEntry.MenuPath = "Damage|Physical|Melee";
    NewEntry.BaseName = "GE_MeleeAttack";
    NewEntry.ParentGameplayEffect = UGameplayEffect::StaticClass(); // 或你的自定义GE基类
    Menu->Definitions.Add(NewEntry);
}
```

### 进阶用法

**扩展 GameplayAbility 审计功能**：
`GameplayAbilityAudit` 提供了对能力蓝图进行数据审计的功能。你可以继承 `FGameplayAbilityAuditRow` 来收集自定义数据。
（来源：`Engine/Plugins/Runtime/GameplayAbilities/Source/GameplayAbilitiesEditor/Public/GameplayAbilityAudit.h`）

```cpp
// MyGameplayAbilityAuditRow.h
#pragma once
#include "GameplayAbilityAudit.h"

USTRUCT()
struct FMyGameplayAbilityAuditRow : public FGameplayAbilityAuditRow
{
    GENERATED_BODY()

    // 添加你关心的自定义数据字段
    UPROPERTY()
    bool bUsesCustomTargeting = false;

    // 重写以填充自定义数据
    virtual void FillDataFromGameplayAbilityBlueprint(const UBlueprint& GameplayAbilityBlueprint) override
    {
        Super::FillDataFromGameplayAbilityBlueprint(GameplayAbilityBlueprint);
        // 在这里分析蓝图图表，查找特定节点或变量
        // bUsesCustomTargeting = ...;
    }

    virtual void FillDataFromGameplayAbility(const UGameplayAbility& GameplayAbility) override
    {
        Super::FillDataFromGameplayAbility(GameplayAbility);
        // 在这里检查运行时能力实例的属性
    }
};
```

## Demo 示例

一个最小化的示例，展示如何创建一个自定义的 `GameplayAbility` 审计行类。

**MyGameplayAbilityAuditRow.h**
```cpp
#pragma once
#include "GameplayAbilityAudit.h"
#include "MyGameplayAbilityAuditRow.generated.h"

USTRUCT(BlueprintInternalUseOnlyHierarchical)
struct FMyGameplayAbilityAuditRow : public FGameplayAbilityAuditRow
{
    GENERATED_BODY()

    // 自定义审计数据：是否使用了自定义目标选择逻辑
    UPROPERTY()
    bool bUsesCustomTargeting = false;

    // 重写蓝图数据填充方法
    virtual void FillDataFromGameplayAbilityBlueprint(const UBlueprint& GameplayAbilityBlueprint) override;
};
```

**MyGameplayAbilityAuditRow.cpp**
```cpp
#include "MyGameplayAbilityAuditRow.h"
#include "K2Node.h"
#include "EdGraph/EdGraph.h"

void FMyGameplayAbilityAuditRow::FillDataFromGameplayAbilityBlueprint(const UBlueprint& GameplayAbilityBlueprint)
{
    // 首先调用父类填充基础数据
    Super::FillDataFromGameplayAbilityBlueprint(GameplayAbilityBlueprint);

    // 遍历蓝图中的所有图表，查找特定类型的节点
    for (UEdGraph* Graph : GameplayAbilityBlueprint.FunctionGraphs)
    {
        if (!Graph) continue;

        for (UEdGraphNode* Node : Graph->Nodes)
        {
            // 假设我们有一个自定义的 K2Node_CustomTargeting
            if (Node && Node->GetClass()->GetName().Contains(TEXT("CustomTargeting")))
            {
                bUsesCustomTargeting = true;
                break;
            }
        }
        if (bUsesCustomTargeting) break;
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GameplayTasks` | `GameplayAbilitiesEditor` 模块依赖此模块，用于支持异步能力任务（Latent Ability Calls）的蓝图节点。 |
| `Niagara` | 运行时模块依赖，用于支持与 Niagara 粒子系统的集成（如通过 GameplayCue 触发特效）。 |
| `DataRegistry` | 运行时模块依赖，用于支持数据驱动的能力配置。 |

## 维护状态

### 近期更新

```
- ef29054a8817 Consolidates code that checks whether an AttributeSet's FProperty represents a gameplay attribute, and improved coverage and stability.
- 9803c443cfab Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applied using UnrealCodeFixup)
- 9cd64c454782 fix unreachable code warning
```

### 维护评价

-   **创建时间**：2016年，是一个非常成熟和核心的系统。
-   **最近更新**：最近的提交主要是代码清理、编译警告修复和稳定性改进，没有重大的新功能添加。这表明该系统已进入**稳定维护期**。
-   **活跃度**：作为 UE 的核心插件，它仍然被 Epic Games 维护以确保与引擎新版本的兼容性，但功能性更新频率较低。
-   **已知问题/限制**：GAS 功能强大但学习曲线陡峭，初始设置和概念理解需要投入时间。对于非常简单的游戏，可能会显得过于复杂。
-   **推荐使用**：**强烈推荐**用于任何中等及以上复杂度、特别是涉及多人同步的游戏项目。它是 UE 官方推荐的、经过大量项目验证的解决方案。对于小型或原型项目，可以考虑更简单的自定义方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GameplayAbilities)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/gameplay-ability-system-in-unreal-engine/)（UE 官方文档链接，非 .uplugin 内提供）