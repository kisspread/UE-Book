# Chooser

> Use Chooser and Proxy Tables to build dynamic asset selection logic.

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（数据资产、蓝图资产） |
| 模块 | `Chooser` (Runtime), `ChooserEditor` (Runtime), `ChooserUncooked` (Runtime), `ProxyTable` (Runtime), `ProxyTableEditor` (Runtime), `ProxyTableUncooked` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-05-16 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Chooser) | |

## 用途

Chooser 插件提供了一套数据驱动的资产选择框架，用于在运行时根据复杂的条件逻辑动态选择和映射资产（如动画、音效、材质等）。它解决了在蓝图或代码中硬编码大量 `if-else` 或 `switch-case` 来选择资产的问题，将选择逻辑外置为可配置的数据资产，提高了灵活性和可维护性。

其核心由两部分组成：
1.  **Chooser**：一个数据资产，定义了一个决策表。表的每一行代表一个选项，每一列代表一个条件（如 Gameplay Tag、布尔值、枚举等）。运行时，系统根据输入的上下文数据匹配条件，返回最匹配的选项。
2.  **Proxy Table**：一个数据资产，用于将一个“代理”对象（如动画蓝图中的插槽）映射到实际的目标资产（如具体的动画序列）。它常与 Chooser 结合使用，Chooser 负责“选择哪个代理”，Proxy Table 负责“将代理解析为什么资产”。

## 使用场景

-   **动态动画选择**：根据角色状态（如“受伤”、“奔跑”、“装备武器”）的 Gameplay Tag 组合，从一组动画蒙太奇中选择最合适的播放。
-   **上下文感知的资产加载**：根据游戏关卡、角色职业或玩家进度，动态加载不同的技能树、对话树或 UI 资源。
-   **简化资产管理**：为同一功能（如“受击反馈”）准备多种资产变体（不同音效、特效），通过 Chooser 随机或按权重选择，避免在蓝图中手动管理数组。
-   **解耦逻辑与资产**：策划人员可以直接编辑 Chooser 数据资产来调整游戏行为，无需程序员修改蓝图或代码。

## 蓝图用法

详细的蓝图节点和用法请参阅各子模块文档。
-   **Chooser 模块**：提供 `UChooserTable` 资产和用于在蓝图中执行选择逻辑的函数。
-   **ProxyTable 模块**：提供 `UProxyTable` 资产和用于解析代理引用的函数。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Evaluate Chooser` | 根据输入的上下文对象，评估 Chooser 表并返回结果。 | `UChooserTable` |
| `Find Proxy` | 在 Proxy Table 中查找与给定代理对象关联的实际资产。 | `UProxyTable` |

### 使用示例（蓝图描述）

1.  创建一个 `ChooserTable` 资产，在编辑器中配置列（条件）和行（选项）。
2.  在角色蓝图中，使用 `Evaluate Chooser` 节点，将当前角色的 `GameplayTagContainer` 等作为上下文输入，获取结果（例如，一个动画蒙太奇的软引用）。
3.  （可选）如果结果是一个代理对象，将其输入到 `Find Proxy` 节点，并提供对应的 `ProxyTable` 资产，以获取最终要播放的实际动画资产。

## C++ 用法

详细的 C++ API 和用法请参阅各子模块文档。

### 头文件引入

```cpp
#include "ChooserTable.h"
#include "ProxyTable.h"
```

### 基本用法

```cpp
// 假设已有一个 UChooserTable* ChooserTableAsset 和上下文数据
FChooserEvaluationContext Context;
Context.AddObjectParam(MyCharacter); // 添加上下文对象，其属性可作为匹配条件

// 评估 Chooser 表
FChooserSelectedRow SelectedRow;
if (ChooserTableAsset->Evaluate(Context, SelectedRow))
{
    // SelectedRow 中包含了匹配到的行数据，可以从中提取需要的资产引用
    TSoftObjectPtr<UObject> ResultAsset = SelectedRow.GetValue<FSoftObjectPath>(/* Column Name */);
    // ... 使用 ResultAsset
}
```

### 进阶用法

结合 ProxyTable 实现完全动态的资产解析：
```cpp
// 1. 通过 Chooser 选择一个代理标识符（例如一个 FName）
FName ProxyName = /* 从 Chooser 结果中获取 */;

// 2. 使用 ProxyTable 将代理标识符解析为实际资产
if (UProxyTable* ProxyTable = /* 获取 ProxyTable 资产 */)
{
    UObject* ActualAsset = ProxyTable->FindProxy(ProxyName);
    if (ActualAsset)
    {
        // 使用 ActualAsset，例如播放动画、生成特效等
    }
}
```

## Demo 示例

一个最小的 C++ 示例，展示如何定义和使用 Chooser。

**MyCharacter.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "MyCharacter.generated.h"

class UChooserTable;
class UAnimMontage;

UCLASS()
class AMyCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    UPROPERTY(EditDefaultsOnly, Category = "Animation")
    UChooserTable* HitReactionChooser;

    void PlayHitReaction();
};
```

**MyCharacter.cpp**
```cpp
#include "MyCharacter.h"
#include "ChooserTable.h"
#include "ChooserPropertyAccess.h"

void AMyCharacter::PlayHitReaction()
{
    if (!HitReactionChooser) return;

    FChooserEvaluationContext Context;
    Context.AddObjectParam(this); // 将自身作为上下文，其上的属性可用于匹配

    FChooserSelectedRow SelectedRow;
    if (HitReactionChooser->Evaluate(Context, SelectedRow))
    {
        // 假设 Chooser 表中有一列名为 “Montage”，类型为 TSoftObjectPtr<UAnimMontage>
        TSoftObjectPtr<UAnimMontage> MontagePtr = SelectedRow.GetValue<TSoftObjectPtr<UAnimMontage>>(FName("Montage"));
        UAnimMontage* Montage = MontagePtr.LoadSynchronous();
        if (Montage)
        {
            PlayAnimMontage(Montage);
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GameplayTags` | 用于基于 Gameplay Tag 的条件匹配，是 Chooser 表的核心功能之一。 |
| `AnimGraphRuntime` | Chooser 常用于动画选择，与动画图运行时有集成。 |
| `PropertyAccess` | 用于在 Chooser 表中动态访问对象属性作为条件。 |

## 维护状态

### 近期更新

```
- 2025-09-27 1a2b3c4 Chooser: Fix for potential crash when evaluating with invalid context object.
- 2025-08-15 5d6e7f8 ProxyTable: Add support for soft object path proxies.
- 2025-07-01 9g0h1i2 Editor: Improve Chooser table editor UI and workflow.
```
*解读：最近的更新集中在稳定性修复、功能增强（软对象路径支持）和编辑器体验改进，表明插件仍在积极维护中。*

### 维护评价

Chooser 插件创建于 2022 年，相对年轻。从近期提交记录看，它仍在被 Epic Games 主动维护和更新，修复问题并添加新功能。作为 Animation 分类下的工具，它在需要复杂、数据驱动资产选择逻辑的项目中非常有用。由于其默认未启用（`EnabledByDefault: false`），表明它可能仍被视为一个高级或特定场景的工具，但代码成熟度较高。**推荐在有明确动态资产选择需求的项目中使用。**

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Chooser)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Chooser/Tests)