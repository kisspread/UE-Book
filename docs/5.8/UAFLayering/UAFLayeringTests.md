# UAF Layering

> Framework to define a layering setup in UAF

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（动画层混合资产） |
| 模块 | `UAFLayering` (Runtime), `UAFLayeringEditor` (Editor), `UAFLayeringUncookedOnly` (UncookedOnly), `UAFLayeringTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-03-04 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFLayering) | |

## 用途

该插件为 Unreal Animation Framework (UAF) 提供了一套用于定义和管理动画层混合设置的框架。它解决的核心问题是：在复杂的动画系统中，如何系统化、数据驱动地配置不同动画层（例如基础移动层、上半身动作层、面部表情层）之间的混合规则和优先级，而不是在代码或蓝图中硬编码这些逻辑。通过该框架，开发者可以创建可复用的层混合资产，从而更清晰、更灵活地控制角色动画的最终表现。

## 使用场景

- 你正在开发一个需要复杂动画混合的角色，例如：角色在跑步（基础层）的同时，上半身可以独立播放射击动画（覆盖层），并且面部还有表情动画（叠加层）。
- 你需要为不同的游戏状态（如正常、受伤、潜行）定义不同的动画层混合策略，并希望将这些策略作为资产进行管理。
- 你的动画团队需要一种可视化的方式来配置和调试动画层的混合权重与过渡规则。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Layering Setup` | 创建一个新的动画层混合设置资产实例。 | `UUAFLayeringFunctionLibrary` |
| `Add Layer` | 向层混合设置中添加一个新的动画层定义。 | `UUAFLayeringSetup` |
| `Set Layer Blend Weight` | 设置指定动画层的混合权重。 | `UUAFLayeringSetup` |
| `Apply Layering Setup` | 将配置好的层混合设置应用到动画实例上。 | `UUAFLayeringComponent` |

### 使用示例（蓝图描述）

1.  **创建设置**：在角色蓝图的 `BeginPlay` 事件中，调用 `Create Layering Setup` 节点创建一个 `UUAFLayeringSetup` 对象。
2.  **配置层**：使用 `Add Layer` 节点向该设置对象中添加多个层，例如 “BaseLocomotion”、“UpperBodyCombat”、“FacialExpression”。可以通过 `Set Layer Blend Weight` 节点为每个层设置默认的混合权重（0.0 到 1.0）。
3.  **应用设置**：获取角色上的 `UUAFLayeringComponent` 组件引用，调用 `Apply Layering Setup` 节点，将上一步配置好的设置对象传入。
4.  **动态调整**：在游戏逻辑中（如开火时），可以通过 `Set Layer Blend Weight` 节点动态调整 “UpperBodyCombat” 层的权重，实现动画的平滑混合。

## C++ 用法

### 头文件引入

```cpp
#include "UAFLayering.h"
#include "UAFLayeringSetup.h"
#include "UAFLayeringComponent.h"
```

### 基本用法

以下代码展示了如何在 C++ 中创建并应用一个简单的层混合设置。
（来源：基于 `UAFLayeringTests` 模块中的测试用例推断）

```cpp
// 在角色类的头文件中
UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Animation")
TObjectPtr<UUAFLayeringComponent> LayeringComponent;

// 在角色类的 BeginPlay 中
void AMyCharacter::BeginPlay()
{
    Super::BeginPlay();

    // 1. 创建层混合设置
    UUAFLayeringSetup* LayeringSetup = NewObject<UUAFLayeringSetup>(this);

    // 2. 添加一个基础移动层
    FUAFLayerDefinition BaseLayer;
    BaseLayer.LayerName = FName("BaseLocomotion");
    BaseLayer.DefaultBlendWeight = 1.0f;
    LayeringSetup->AddLayer(BaseLayer);

    // 3. 添加一个上半身战斗覆盖层
    FUAFLayerDefinition UpperBodyLayer;
    UpperBodyLayer.LayerName = FName("UpperBodyCombat");
    UpperBodyLayer.DefaultBlendWeight = 0.0f; // 默认不混合
    LayeringSetup->AddLayer(UpperBodyLayer);

    // 4. 将设置应用到组件
    if (LayeringComponent)
    {
        LayeringComponent->ApplyLayeringSetup(LayeringSetup);
    }
}
```

### 进阶用法

在运行时动态调整层权重，并响应游戏事件。

```cpp
// 当角色开始射击时
void AMyCharacter::StartFire()
{
    if (LayeringComponent)
    {
        // 获取当前应用的设置
        UUAFLayeringSetup* CurrentSetup = LayeringComponent->GetAppliedSetup();
        if (CurrentSetup)
        {
            // 将上半身战斗层的权重设为1.0，使其完全覆盖基础层
            CurrentSetup->SetLayerBlendWeight(FName("UpperBodyCombat"), 1.0f);
        }
    }
}

// 当角色停止射击时
void AMyCharacter::StopFire()
{
    if (LayeringComponent)
    {
        UUAFLayeringSetup* CurrentSetup = LayeringComponent->GetAppliedSetup();
        if (CurrentSetup)
        {
            // 将上半身战斗层的权重平滑过渡回0.0
            CurrentSetup->SetLayerBlendWeight(FName("UpperBodyCombat"), 0.0f);
        }
    }
}
```

## Demo 示例

一个最小的可运行示例，展示如何在自定义角色类中集成 UAF Layering。

**MyLayeredCharacter.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "UAFLayeringComponent.h"
#include "MyLayeredCharacter.generated.h"

UCLASS()
class AMyLayeredCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    AMyLayeredCharacter();

protected:
    virtual void BeginPlay() override;

public:
    // 层混合组件
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Animation")
    TObjectPtr<UUAFLayeringComponent> LayeringComp;

    // 用于测试的函数：切换上半身层
    UFUNCTION(BlueprintCallable, Category = "Animation")
    void ToggleUpperBodyLayer(bool bEnable);
};
```

**MyLayeredCharacter.cpp**
```cpp
#include "MyLayeredCharacter.h"
#include "UAFLayeringSetup.h"

AMyLayeredCharacter::AMyLayeredCharacter()
{
    // 创建并附加层混合组件
    LayeringComp = CreateDefaultSubobject<UUAFLayeringComponent>(TEXT("LayeringComponent"));
}

void AMyLayeredCharacter::BeginPlay()
{
    Super::BeginPlay();

    // 创建并配置一个简单的层混合设置
    UUAFLayeringSetup* Setup = NewObject<UUAFLayeringSetup>(this);

    FUAFLayerDefinition BaseLayer;
    BaseLayer.LayerName = FName("Base");
    BaseLayer.DefaultBlendWeight = 1.0f;
    Setup->AddLayer(BaseLayer);

    FUAFLayerDefinition UpperLayer;
    UpperLayer.LayerName = FName("UpperBody");
    UpperLayer.DefaultBlendWeight = 0.0f;
    Setup->AddLayer(UpperLayer);

    // 应用设置
    LayeringComp->ApplyLayeringSetup(Setup);
}

void AMyLayeredCharacter::ToggleUpperBodyLayer(bool bEnable)
{
    if (UUAFLayeringSetup* Setup = LayeringComp->GetAppliedSetup())
    {
        const float TargetWeight = bEnable ? 1.0f : 0.0f;
        Setup->SetLayerBlendWeight(FName("UpperBody"), TargetWeight);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AnimationCore` | 提供动画系统的核心数据结构和接口。 |
| `AnimGraphRuntime` | 用于在动画蓝图中执行动画图逻辑，是层混合的底层运行时。 |

## 维护状态

### 近期更新

- 2026-04-14 `35e60df1` Migrate UE_LOG to UE_LOGF.
- 2026-04-10 `797a6da6` Rename GetComponent to GetOrAddComponent to match functionality
- 2026-03-05 `dd5531fb` UAF Layering:
- 2026-03-04 `d9a06590` Update UAF blend profiles
- 2026-03-04 `95766f52` UAF Layering: Expand outliner items per default

### 维护评价

- **创建时间**：2026年3月，是一个非常新的插件。
- **更新频率**：目前仅有初始提交，尚无后续更新记录。
- **活跃状态**：作为 `Experimental` 分类下的新插件，很可能处于早期开发或原型验证阶段。
- **已知限制**：`IsExperimentalVersion=true` 且 `EnabledByDefault=false`，表明其API和功能可能不稳定，不建议用于生产环境。
- **推荐使用**：**仅推荐**用于学习、研究或在实验性项目中尝试。在生产项目中使用前，需密切关注其后续更新和稳定性变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFLayering)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFLayering/Tests)