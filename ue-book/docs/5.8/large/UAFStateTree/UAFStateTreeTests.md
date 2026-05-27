# UAF State Tree

> StateTree integration for UAF.

| 属性 | 值 |
|---|---|
| 中文名 | UAF状态树 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（具体内容待定） |
| 模块 | `UAFStateTree` (Runtime), `UAFStateTreeEditor` (Runtime), `UAFStateTreeUncookedOnly` (Runtime), `UAFStateTreeTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-27 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFStateTree) | |

## 用途

UAFStateTree 是 UE5 状态树（StateTree）系统与 Unreal Animation Framework (UAF) 的集成插件。它解决了在 UAF 动画系统中使用状态树进行复杂逻辑、状态管理和过渡的问题。状态树是一种可扩展的、可视化的决策系统，通过此插件，动画师和开发者可以在 UAF 的动画蓝图或动画实例中无缝地利用状态树来控制动画逻辑，实现更复杂和可维护的动画状态机。

## 使用场景

- 你需要在一个复杂的角色动画系统中管理多个动画状态和过渡逻辑。
- 你希望在动画蓝图中使用状态树的可视化编辑器来设计动画行为，而不是传统的动画状态机。
- 你已经在使用 UAF 进行动画管理，并希望引入状态树来增强逻辑控制能力。

## 蓝图用法

由于这是一个集成插件，其核心功能在于为状态树系统提供与 UAF 的对接。蓝图用法主要体现在动画蓝图中使用 UAF 提供的状态树相关节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetOrAddComponent` | 获取或添加指定类型的状态树组件，用于与 UAF 系统交互。 | `UUAFStateTreeComponent` |

### 使用示例（蓝图描述）

在动画蓝图的事件图中，你可以通过 `GetOrAddComponent` 节点获取 `UUAFStateTreeComponent` 实例。然后，你可以调用该实例上的方法来初始化状态树、发送事件或查询状态。状态树资产本身则在状态树编辑器中进行设计。

## C++ 用法

测试用例是了解此插件 C++ 用法的最佳来源。

### 头文件引入

```cpp
#include "UAFStateTree.h"
```

### 基本用法

从测试用例中可以看出，基本用法是获取 `UUAFStateTreeComponent` 并与其交互。

```cpp
// 来源: Tests/UAFStateTreeTests.Build.cs (依赖关系) 和相关测试文件
#include "UAFStateTreeComponent.h"

// 在某个对象（如 Actor 或 AnimInstance）中
UUAFStateTreeComponent* StateTreeComponent = GetOrAddComponent<UUAFStateTreeComponent>();
if (StateTreeComponent)
{
    // 通常会有一个状态树资产
    UStateTree* MyStateTree = LoadObject<UStateTree>(nullptr, TEXT("/Path/To/Your/StateTreeAsset"));
    
    // 初始化状态树组件
    StateTreeComponent->SetStateTree(MyStateTree);
    StateTreeComponent->StartLogic();
}
```

### 进阶用法

更复杂的用法涉及状态树事件、数据绑定和条件判断，这些通常在状态树编辑器中配置，并通过组件进行管理。

```cpp
// 假设状态树中定义了一个事件
StateTreeComponent->SendStateTreeEvent(MyEventTag);
```

## Demo 示例

一个最小的、展示如何初始化 UAF 状态树组件的 C++ 示例。

```cpp
// MyAnimInstance.h
#pragma once
#include "Animation/AnimInstance.h"
#include "MyAnimInstance.generated.h"

class UUAFStateTreeComponent;

UCLASS()
class UMyAnimInstance : public UAnimInstance
{
    GENERATED_BODY()

public:
    virtual void NativeInitializeAnimation() override;

    UPROPERTY(BlueprintReadOnly)
    TObjectPtr<UUAFStateTreeComponent> StateTreeComponent;
};

// MyAnimInstance.cpp
#include "MyAnimInstance.h"
#include "UAFStateTreeComponent.h"

void UMyAnimInstance::NativeInitializeAnimation()
{
    Super::NativeInitializeAnimation();
    
    // 在动画实例中获取或创建状态树组件
    StateTreeComponent = GetOrAddComponent<UUAFStateTreeComponent>();
    
    if (StateTreeComponent)
    {
        // 加载或引用一个状态树资产
        static ConstructorHelpers::FObjectFinder<UStateTree> StateTreeAsset(TEXT("/Game/Animation/ST_MyBehavior"));
        if (StateTreeAsset.Succeeded())
        {
            StateTreeComponent->SetStateTree(StateTreeAsset.Object);
            StateTreeComponent->StartLogic();
        }
    }
}
```

## 模块依赖

从 `UAFStateTreeTests.Build.cs` 可以推断，使用此插件需要以下独特模块依赖。请注意，这是针对测试模块的，但核心运行时模块可能需要类似依赖。

| 模块 | 用途 |
|---|---|
| `StateTree` | 状态树核心运行时模块 |
| `UAF` | Unreal Animation Framework 核心模块 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将UE_LOG宏迁移到UE_LOGF，更新日志系统 |
| 2026-04-13 | `6f1ea925` | State Tree: Updated state tree reference struct details to show the display name of the struct rathe | 状态树：更新引用结构详情，显示结构体的显示名称 |
| 2026-04-13 | `5078d880` | Add UAFSharedAssets plugin for content we want to provide that references UAF assets defined in sepa | 新增UAFSharedAssets插件，用于提供引用独立定义UAF资产的共享内容 |
| 2026-04-10 | `797a6da6` | Rename GetComponent to GetOrAddComponent to match functionality | 将GetComponent重命名为GetOrAddComponent以匹配其功能 |
| 2026-03-31 | `4e41a45f` | Fix crash attempting to manually create UAF ST by hiding UAF ST Schema | 通过隐藏UAF状态树Schema来修复手动创建UAF状态树时的崩溃 |

### 维护评价

UAFStateTree 是一个非常新的实验性插件（创建于 2025 年 6 月），目前处于积极开发和维护中。从最近的提交记录可以看出，更新频繁，涵盖了功能改进、bug 修复和依赖整理。由于其状态为“实验性”且默认不启用，它可能尚未稳定，API 可能会有变化。目前不建议在生产项目中使用，但可以用于原型开发和功能评估。如果你对 UAF 和状态树的集成有强烈需求，并且愿意接受实验性功能的风险，可以进行尝试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFStateTree)
- [官方文档]()（暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFStateTree/Tests)