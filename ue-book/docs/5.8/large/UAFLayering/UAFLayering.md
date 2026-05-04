# UAF Layering

> Framework to define a layering setup in UAF

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（动画层叠资产） |
| 模块 | `UAFLayering` (Runtime), `UAFLayeringEditor` (Editor), `UAFLayeringUncookedOnly` (UncookedOnly), `UAFLayeringTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-03-04 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFLayering) | |

## 用途

UAFLayering 是 Unreal Animation Framework (UAF) 的一个实验性插件，为 UAF 动画图系统提供了一个**动画层叠（Layering）框架**。它解决的核心问题是：在运行时动态、灵活地管理和混合多个动画层。

传统的动画状态机或混合树在处理复杂的、需要动态叠加和控制的动画效果（如同时播放基础移动、上半身攻击、面部表情和布料物理）时可能变得笨重。UAFLayering 通过引入“层叠栈”（Layer Stack）的概念，允许开发者预先定义一组动画层，并在运行时通过事件系统独立控制每一层的启用/禁用、权重、混合时间等属性。这使得实现诸如“在跑步时叠加一个受伤动画”、“根据游戏状态动态调整上半身动画权重”等需求变得更加直观和模块化。

## 使用场景

- 你在开发一个需要复杂角色动画的游戏，例如动作RPG或第三人称射击游戏，需要同时处理移动、战斗、交互等多种动画状态的叠加 → 使用 UAFLayering 来管理这些动画层。
- 你需要根据游戏逻辑（如装备、状态效果、技能）在运行时动态地启用、禁用或调整特定动画部分的强度（权重） → 使用 `UUAFLayeringUtils` 蓝图函数库来发送控制事件。
- 你希望将基于蒙太奇（Montage）的动画与基础动画层进行混合，并自动处理蒙太奇播放时对应层的启用和混合时间 → 使用 `MontageLayer` 特性。

## 蓝图用法

核心蓝图功能通过 `UUAFLayeringUtils` 函数库提供，用于在运行时与层叠栈交互。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `EnableLayer` | 根据名称启用指定层叠栈中的某个层 | `UUAFLayeringUtils` |
| `DisableLayer` | 根据名称禁用指定层叠栈中的某个层 | `UUAFLayeringUtils` |
| `SetLayerWeight` | 根据名称设置指定层叠栈中某个层的权重 | `UUAFLayeringUtils` |
| `EnableLayerByIndex` | 根据索引启用指定层叠栈中的某个层 | `UUAFLayeringUtils` |
| `DisableLayerByIndex` | 根据索引禁用指定层叠栈中的某个层 | `UUAFLayeringUtils` |
| `SetLayerWeightByIndex` | 根据索引设置指定层叠栈中某个层的权重 | `UUAFLayeringUtils` |

### 使用示例（蓝图描述）

1.  **控制特定层**：假设你有一个名为 `LayerStack_Enemy` 的层叠栈资产，其中包含一个名为 `UpperBodyAttack` 的层。要启用它，可以：
    - 获取角色的 `UAFComponent` 引用。
    - 调用 `EnableLayer` 节点，将 `UAFComponent`、`LayerName`（`UpperBodyAttack`）和 `LayerStackPath`（指向 `LayerStack_Enemy` 的软引用）连接起来。

2.  **动态调整权重**：要让 `UpperBodyAttack` 层以 50% 的权重混合，可以：
    - 调用 `SetLayerWeight` 节点，将 `Weight` 参数设置为 `0.5`。

3.  **使用索引控制**：如果你知道层在栈中的索引（例如 `0`），可以使用 `EnableLayerByIndex` 等节点，这在某些动态生成层栈的场景下可能更方便。

## C++ 用法

### 头文件引入

```cpp
#include "UAFLayeringTypes.h"
#include "UAFLayeringUtils.h"
```

### 基本用法

通过发送 Trait 事件来与层叠系统交互。这是比蓝图函数更底层的控制方式。

```cpp
// 假设我们有一个 UAFComponent 和一个指向层叠栈资产的路径
UUAFComponent* MyUAFComponent = GetUAFComponent();
FSoftObjectPath LayerStackPath = TEXT("/Game/Animation/LayerStacks/LS_Player.LS_Player");

// 创建一个针对名为 “Locomotion” 层的事件
UE::UAF::Layering::FLayerStack_LayerEvent LayerEvent(FName("Locomotion"), LayerStackPath);

// 设置动作为启用该层
LayerEvent.Action = UE::UAF::Layering::ELayerEventAction::EnableLayer;

// 将事件发送到 UAF 系统进行处理
MyUAFComponent->SendTraitEvent(LayerEvent);
```
*（基于 `UAFLayeringTypes.h` 中的事件结构推断）*

### 进阶用法

可以组合使用事件来实现更复杂的逻辑，例如在启用一个层的同时设置其权重和混合时间。

```cpp
// 创建事件并设置多个属性
UE::UAF::Layering::FLayerStack_LayerEvent BlendEvent(FName("UpperBody"), LayerStackPath);
BlendEvent.Action = UE::UAF::Layering::ELayerEventAction::SetFloatValue;

// 设置权重
BlendEvent.PropertyToSet = UE::UAF::Layering::FLayerStack_LayerEvent::LayerWeightProperty;
BlendEvent.FloatValue = 0.75f;
MyUAFComponent->SendTraitEvent(BlendEvent);

// 设置混合进入时间
BlendEvent.PropertyToSet = UE::UAF::Layering::FLayerStack_LayerEvent::BlendInTimeProperty;
BlendEvent.FloatValue = 0.2f;
MyUAFComponent->SendTraitEvent(BlendEvent);
```
*（基于 `UAFLayeringTypes.h` 中的静态属性名推断）*

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何在 Actor 中通过事件控制动画层。

**MyLayeredCharacter.h**
```cpp
#pragma once
#include "GameFramework/Character.h"
#include "MyLayeredCharacter.generated.h"

class UUAFComponent;
class UUAFLayerStack;

UCLASS()
class AMyLayeredCharacter : public ACharacter
{
	GENERATED_BODY()

public:
	AMyLayeredCharacter();

protected:
	virtual void BeginPlay() override;

public:
	// 蓝图可调用的函数，用于测试层控制
	UFUNCTION(BlueprintCallable, Category = "Layering")
	void ToggleAttackLayer(bool bEnable);

private:
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Animation", meta = (AllowPrivateAccess = "true"))
	TObjectPtr<UUAFComponent> UAFComponent;

	// 在编辑器中指定的层叠栈资产
	UPROPERTY(EditDefaultsOnly, Category = "Animation")
	TSoftObjectPtr<UUAFLayerStack> LayerStackAsset;
};
```

**MyLayeredCharacter.cpp**
```cpp
#include "MyLayeredCharacter.h"
#include "UAFComponent.h"
#include "UAFLayeringTypes.h"
#include "UAFLayerStack.h"

AMyLayeredCharacter::AMyLayeredCharacter()
{
	UAFComponent = CreateDefaultSubobject<UUAFComponent>(TEXT("UAFComponent"));
}

void AMyLayeredCharacter::BeginPlay()
{
	Super::BeginPlay();
	// 确保层叠栈资产已加载
	LayerStackAsset.LoadSynchronous();
}

void AMyLayeredCharacter::ToggleAttackLayer(bool bEnable)
{
	if (!UAFComponent || LayerStackAsset.IsNull())
	{
		return;
	}

	// 构造层事件
	UE::UAF::Layering::FLayerStack_LayerEvent Event(
		FName("AttackLayer"), // 假设层叠栈中有一个名为 “AttackLayer” 的层
		LayerStackAsset.ToSoftObjectPath()
	);

	Event.Action = bEnable
		? UE::UAF::Layering::ELayerEventAction::EnableLayer
		: UE::UAF::Layering::ELayerEventAction::DisableLayer;

	// 发送事件
	UAFComponent->SendTraitEvent(Event);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `UAF` | 核心动画框架，提供基础图、组件和事件系统 |
| `AnimNext` | 提供 Trait 系统、评估 VM 和动画图基础设施 |
| `Workspace` | （插件依赖）提供工作区编辑器功能 |

## 维护状态

### 近期更新

- 2026-04-14 `35e60df1` Migrate UE_LOG to UE_LOGF.
- 2026-04-10 `797a6da6` Rename GetComponent to GetOrAddComponent to match functionality
- 2026-03-05 `dd5531fb` UAF Layering:
- 2026-03-04 `d9a06590` Update UAF blend profiles
- 2026-03-04 `95766f52` UAF Layering: Expand outliner items per default

### 维护评价

- **创建时间**：标记为 2026 年，这很可能是一个占位符或错误日期。实际创建时间应更早。
- **实验性状态**：插件明确标记为 `IsExperimentalVersion: true` 且 `EnabledByDefault: false`，表明它仍处于早期开发阶段，API 和功能可能不稳定。
- **维护状态**：基于其“实验性”标签和作为 UAF 框架一部分的定位，它很可能处于**活跃开发**中，但仅建议用于实验和原型开发。
- **已知限制**：从代码注释（如 `CachePoseTrait` 的 TODO）可以看出，部分功能尚未完全实现。
- **推荐使用**：**仅推荐用于学习和实验**。不建议在生产项目中依赖此插件，除非你愿意跟进 Epic 的快速迭代并处理可能的破坏性更改。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFLayering)
- [官方文档]() （暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFLayering/Tests/UAFLayeringTests)