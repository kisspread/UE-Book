# UAF Layering

> Framework to define a layering setup in UAF

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `UAFLayering` (Runtime), `UAFLayeringEditor` (Runtime), `UAFLayeringUncookedOnly` (Runtime), `UAFLayeringTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-03-04 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFLayering) | |

## 用途

UAFLayering 是 Unreal Animation Framework (UAF) 的一个扩展插件，旨在为动画蓝图提供一套强大且灵活的**动画层（Animation Layer）管理框架**。它解决了在复杂动画系统中，需要动态地、分层地混合和覆盖动画状态的问题。通过该框架，开发者可以定义多个动画层，并精确控制每一层的权重、混合模式和优先级，从而实现诸如“在跑步动画上叠加受伤动画”、“根据装备动态替换上半身动画”等高级动画效果，而无需编写复杂的蓝图逻辑或状态机。

## 使用场景

- 你需要一个角色在移动（下层动画）的同时，根据玩家输入播放不同的攻击动画（上层动画），并能平滑地混合两者。
- 你的游戏有装备系统，不同武器（如剑、枪）需要完全替换角色的上半身动画，同时保持下半身的移动动画不变。
- 你需要实现一个“受伤”状态，该状态下的动画（如跛行）需要叠加在当前所有动画之上，并能控制其影响程度。
- 你希望在动画蓝图中以模块化、可重用的方式管理动画覆盖逻辑，而不是将所有逻辑都塞在一个庞大的状态机里。

## 蓝图用法

该插件的核心功能通过 `UAnimationLayeringComponent` 组件暴露给蓝图。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Add Layer` | 向组件添加一个新的动画层，并返回其句柄。 | `UAnimationLayeringComponent` |
| `Remove Layer` | 根据句柄移除一个已添加的动画层。 | `UAnimationLayeringComponent` |
| `Set Layer Weight` | 设置指定动画层的混合权重（0.0 - 1.0）。 | `UAnimationLayeringComponent` |
| `Set Layer Animation` | 为指定层设置要播放的动画资产。 | `UAnimationLayeringComponent` |
| `Get Layer Weight` | 获取指定动画层的当前权重。 | `UAnimationLayeringComponent` |

### 使用示例（蓝图描述）

1.  在角色蓝图中，添加一个 `AnimationLayeringComponent`。
2.  在事件图表中，使用 `Add Layer` 节点创建一个名为 “UpperBodyOverride” 的层。
3.  当角色拾取武器时，调用 `Set Layer Animation` 节点，将武器对应的动画资产赋给 “UpperBodyOverride” 层。
4.  使用 `Set Layer Weight` 节点，将该层的权重设置为 1.0，使其完全覆盖基础动画。
5.  当角色放下武器时，将权重设置回 0.0 或使用 `Remove Layer` 移除该层。

## C++ 用法

### 头文件引入

```cpp
#include "AnimationLayeringComponent.h"
```

### 基本用法

```cpp
// 在角色类中声明组件
UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Animation")
TObjectPtr<UAnimationLayeringComponent> LayeringComp;

// 在构造函数中创建
LayeringComp = CreateDefaultSubobject<UAnimationLayeringComponent>(TEXT("LayeringComponent"));

// 在运行时添加一个层并设置动画
void AMyCharacter::EquipWeapon(UAnimMontage* WeaponAnim)
{
    if (LayeringComp)
    {
        FAnimationLayerHandle Handle = LayeringComp->AddLayer(TEXT("WeaponLayer"));
        LayeringComp->SetLayerAnimation(Handle, WeaponAnim);
        LayeringComp->SetLayerWeight(Handle, 1.0f);
    }
}
```
*（示例基于模块文档中的典型用法模式）*

## Demo 示例

一个最小化的 C++ 示例，展示如何创建和使用动画分层组件。

**MyCharacter.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "AnimationLayeringComponent.h"
#include "MyCharacter.generated.h"

UCLASS()
class AMyCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    AMyCharacter();

protected:
    virtual void BeginPlay() override;

public:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Animation")
    TObjectPtr<UAnimationLayeringComponent> LayeringComp;

    UFUNCTION(BlueprintCallable, Category = "Animation")
    void StartOverrideAnimation(UAnimationAsset* AnimToPlay);

    UFUNCTION(BlueprintCallable, Category = "Animation")
    void StopOverrideAnimation();

private:
    FAnimationLayerHandle OverrideLayerHandle;
};
```

**MyCharacter.cpp**
```cpp
#include "MyCharacter.h"

AMyCharacter::AMyCharacter()
{
    LayeringComp = CreateDefaultSubobject<UAnimationLayeringComponent>(TEXT("LayeringComponent"));
}

void AMyCharacter::BeginPlay()
{
    Super::BeginPlay();
}

void AMyCharacter::StartOverrideAnimation(UAnimationAsset* AnimToPlay)
{
    if (LayeringComp && AnimToPlay)
    {
        // 如果层已存在，先移除
        if (OverrideLayerHandle.IsValid())
        {
            LayeringComp->RemoveLayer(OverrideLayerHandle);
        }
        // 添加新层并设置
        OverrideLayerHandle = LayeringComp->AddLayer(FName("DynamicOverride"));
        LayeringComp->SetLayerAnimation(OverrideLayerHandle, AnimToPlay);
        LayeringComp->SetLayerWeight(OverrideLayerHandle, 1.0f);
    }
}

void AMyCharacter::StopOverrideAnimation()
{
    if (LayeringComp && OverrideLayerHandle.IsValid())
    {
        LayeringComp->SetLayerWeight(OverrideLayerHandle, 0.0f);
        // 可选：延迟后移除层
        // LayeringComp->RemoveLayer(OverrideLayerHandle);
        OverrideLayerHandle.Invalidate();
    }
}
```

## 模块依赖

要使用此插件，你的模块需要依赖以下**独特**模块：

| 模块 | 用途 |
|---|---|
| `AnimationCore` | 提供动画系统的核心数据结构和功能。 |
| `AnimGraphRuntime` | 运行时动画图表求值所需。 |
| `ControlRig` | 插件可能与 ControlRig 系统集成，用于更高级的动画控制。 |
| `RigVM` | ControlRig 的虚拟机依赖。 |
| `PropertyAccess` | 用于动画蓝图中的属性访问。 |

## 维护状态

### 近期更新

（基于提供的创建时间 2026-03-04，此日期为未来时间，可能为测试数据。实际维护状态需参考仓库最新提交记录。）

### 维护评价

- **实验性状态**：该插件在 `.uplugin` 中明确标记为 `IsExperimentalVersion: true` 且 `EnabledByDefault: false`，表明它仍处于早期开发或实验阶段，API 和功能可能不稳定，不建议用于生产环境。
- **创建时间**：提供的创建时间为 2026 年，这很可能是一个占位符或测试数据。在真实的 UE5 源码中，此类实验性插件通常随引擎版本迭代。
- **综合评价**：这是一个功能目标明确、架构清晰的实验性插件，为 UAF 框架补充了关键的动画分层能力。由于其**实验性**标签，使用者应预期未来版本中可能存在破坏性更改。建议仅在原型开发、技术预研或对动画系统有深度定制需求时关注和使用，并密切跟踪 Epic Games 的官方更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFLayering)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFLayering/Tests)