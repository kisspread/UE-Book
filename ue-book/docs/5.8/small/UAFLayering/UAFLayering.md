# UAF Layering

> Framework to define a layering setup in UAF

| 属性 | 值 |
|---|---|
| 中文名 | UAF动画层栈 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `UAFLayering` (Runtime), `UAFLayeringEditor` (Runtime), `UAFLayeringUncookedOnly` (Runtime), `UAFLayeringTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-01-13 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFLayering) | |

## 用途

该插件是 UE5 新动画框架 UAF (Unreal Animation Framework) 的一部分，专门用于**管理和运行动画层栈 (Layer Stack)**。它并非一个简单的动画混合节点，而是一个完整的框架，允许开发者：
1.  **资产化地定义层栈**：通过 `UUAFLayerStack` 资产来配置一系列动画层及其初始属性（如权重、混合时间）。
2.  **运行时动态控制**：在游戏运行时，通过 API 或蓝图精确控制每个层的启用/禁用、权重以及混合过程。
3.  **与 UAF 系统深度集成**：它解决了在新的 Trait-based 动画系统中实现复杂、可控的层叠混合的架构问题，是 UAF 处理高级动画分层逻辑的核心组件。

## 使用场景

- 你在开发一个角色动画系统，需要角色同时播放基础移动动画、上半身武器动画和受伤反馈动画，且每层动画的混合权重和时机需要独立控制。
- 你的游戏需要为 AI 或玩家角色实现一个状态驱动的动画层栈，根据“战斗”、“潜行”、“游泳”等状态动态混合不同的动画层集。
- 你需要运行时根据游戏逻辑（如装备更换、技能释放）平滑地过渡动画层，而不是硬切换。

## 蓝图用法

核心 API 集中在 `UUAFLayeringUtils` 蓝图函数库中，提供了通过名称或索引控制层的能力。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `EnableLayer` | 按名称启用指定层栈中的特定层 | `UUAFLayeringUtils` |
| `DisableLayer` | 按名称禁用指定层栈中的特定层 | `UUAFLayeringUtils` |
| `SetLayerWeight` | 按名称设置指定层栈中特定层的权重 (0.0 - 1.0) | `UUAFLayeringUtils` |
| `EnableLayerByIndex` | 按索引启用指定层栈中的特定层 | `UUAFLayeringUtils` |
| `DisableLayerByIndex` | 按索引禁用指定层栈中的特定层 | `UUAFLayeringUtils` |
| `SetLayerWeightByIndex` | 按索引设置指定层栈中特定层的权重 | `UUAFLayeringUtils` |

### 使用示例（蓝图描述）

1.  **获取 UAF 组件**：首先从角色蓝图中获取 `UAFComponent` 的引用。
2.  **引用层栈资产**：创建一个 `UUAFLayerStack` 类型的软对象引用变量，指向你项目中定义好的层栈资产。
3.  **控制层**：例如，当玩家按下“冲刺”键时，调用 `SetLayerWeight` 节点，将 `UAFComponent`、层名（如 `SprintLayer`）、层栈资产引用和目标权重（如 `1.0`）连接起来，实现冲刺动画层的平滑混合。

## C++ 用法

### 头文件引入

```cpp
#include “UAFLayeringUtils.h”
#include “UAFComponent.h”
#include “UAFLayerStack.h”
```

### 基本用法

通过 `UUAFLayeringUtils` 的静态函数控制层。你需要一个 `UUAFComponent*` 和一个指向 `UUAFLayerStack` 资产的软引用。
*(基于 `Public/UAFLayeringUtils.h` 源码)*

```cpp
// 假设你已经拥有角色的 UAFComponent 和一个层栈资产引用
UUAFComponent* MyUAFComponent = GetCharacterUAFComponent();
TSoftObjectPtr<UUAFLayerStack> MyLayerStackAsset = LayerStackAssetPath;

// 按名称禁用一个层
UUAFLayeringUtils::DisableLayer(MyUAFComponent, FName(“HitReactLayer”), MyLayerStackAsset);

// 按索引设置一个层的权重
UUAFLayeringUtils::SetLayerWeightByIndex(MyUAFComponent, 0, MyLayerStackAsset, 0.5f);
```

### 进阶用法

层栈的底层通过 `FLayerStack_LayerEvent` 事件进行驱动。虽然高级用户可以直接构造并触发事件，但更推荐使用 `UUAFLayeringUtils` 提供的封装接口，它们内部已经处理了事件的创建和分发。
*(基于 `Public/UAFLayeringTypes.h` 和 `Private/Traits/LayerDataProviderTrait.h` 源码)*

```cpp
// 理解层状态 (概念性代码，非直接 API)
// 一个层 (FLayerDataProviderTrait) 的实例数据 (FInstanceData) 包含：
// - bLayerEnabled: 当前是否启用
// - TargetLayerWeight: 目标权重
// - EffectiveLayerWeight: 考虑了混合过程后的实际权重
// - AlphaBlend: 控制混合过程的插值器
```

## Demo 示例

以下是一个在 C++ 中响应游戏事件，动态调整动画层的最小示例。

**头文件 (CharacterAnimController.h)**
```cpp
#pragma once
#include “CoreMinimal.h”
#include “Components/ActorComponent.h”
#include “UAFLayerStack.h” // 需要包含层栈类型定义
#include “CharacterAnimController.generated.h”

class UUAFComponent;

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class YOURPROJECT_API UCharacterAnimController : public UActorComponent
{
    GENERATED_BODY()

public:
    UCharacterAnimController();

    UFUNCTION(BlueprintCallable, Category = “Animation”)
    void TriggerSprintAnimation();

    UFUNCTION(BlueprintCallable, Category = “Animation”)
    void StopSprintAnimation();

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY()
    TWeakObjectPtr<UUAFComponent> CachedUAFComponent;

    // 在蓝图或编辑器中设置
    UPROPERTY(EditAnywhere, Category = “Animation Layers”)
    TSoftObjectPtr<UUAFLayerStack> CharacterLayerStackAsset;
};
```

**源文件 (CharacterAnimController.cpp)**
```cpp
#include “CharacterAnimController.h”
#include “UAFLayeringUtils.h”
#include “UAFComponent.h”

UCharacterAnimController::UCharacterAnimController()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UCharacterAnimController::BeginPlay()
{
    Super::BeginPlay();
    // 在开始游戏时缓存UAF组件的引用
    CachedUAFComponent = GetOwner()->FindComponentByClass<UUAFComponent>();
}

void UCharacterAnimController::TriggerSprintAnimation()
{
    if (CachedUAFComponent.IsValid() && !CharacterLayerStackAsset.IsNull())
    {
        // 启用“冲刺”层并将其权重设为1.0
        UUAFLayeringUtils::EnableLayer(CachedUAFComponent.Get(), FName(“SprintLayer”), CharacterLayerStackAsset);
        UUAFLayeringUtils::SetLayerWeight(CachedUAFComponent.Get(), FName(“SprintLayer”), CharacterLayerStackAsset, 1.0f);
    }
}

void UCharacterAnimController::StopSprintAnimation()
{
    if (CachedUAFComponent.IsValid() && !CharacterLayerStackAsset.IsNull())
    {
        // 禁用“冲刺”层（权重会平滑混合回0，具体时间由层栈资产中定义的BlendOutTime决定）
        UUAFLayeringUtils::DisableLayer(CachedUAFComponent.Get(), FName(“SprintLayer”), CharacterLayerStackAsset);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AnimNext` | UAF 的核心动画系统，提供 Trait、事件、评估任务等基础设施。 |
| `Workspace` | 为层栈资产 (`UUAFLayerStack`) 提供编辑器集成和资产编辑功能。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志输出宏迁移到新的 UE_LOGF 格式。 |
| 2026-04-10 | `797a6da6` | Rename GetComponent to GetOrAddComponent to match functionality | 重命名函数 `GetComponent` 为 `GetOrAddComponent` 以更准确地反映其“获取或创建”的行为。 |
| 2026-03-05 | `dd5531fb` | UAF Layering: ... | UAF 层栈相关更新，具体信息被省略。 |
| 2026-03-04 | `d9a06590` | Update UAF blend profiles | 更新 UAF 的混合配置文件（Blend Profiles）。 |
| 2026-03-04 | `95766f52` | UAF Layering: Expand outliner items per default | UAF 层栈编辑器默认展开大纲视图项目。 |

### 维护评价

这是一个**非常新的实验性插件**，首次提交于 2026 年 1 月，最近一次更新在 2026 年 4 月。从提交记录看，它正处在**早期积极开发阶段**，更新内容涉及功能完善（重命名、编辑器体验）、底层系统迁移（日志）和核心逻辑调整（混合配置）。

- **优点**：与 Epic 主导的新动画框架 UAF 深度绑定，代表了动画技术的前沿方向。代码结构清晰，事件驱动的设计灵活。
- **风险**：标记为“实验性”且默认禁用，表明其 API 和功能可能尚未稳定，未来版本可能会有破坏性更改。
- **推荐**：如果你正在使用或评估 UAF 框架，并需要复杂的动画层管理，可以尝试集成此插件。但应做好预期，关注其更新日志，并准备好应对可能的接口变化。不建议在寻求稳定性的生产项目中直接使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFLayering)
- 官方文档: （暂无）
- 测试用例: 位于 `Tests/UAFLayeringTests` 模块内。