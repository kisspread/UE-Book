# UAF Layering

> Framework to define a layering setup in UAF

| 属性 | 值 |
|---|---|
| 中文名 | UAF 层叠系统 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（Layer Stack 资产、编辑器集成） |
| 模块 | `UAFLayering` (Runtime), `UAFLayeringEditor` (Runtime), `UAFLayeringUncookedOnly` (Runtime), `UAFLayeringTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-01-13 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFLayering) | |

## 用途

UAFLayering 是 Unreal Animation Framework (UAF) 的扩展插件，为动画系统提供一个**层级堆栈 (Layer Stack)** 框架。它允许动画师和程序员定义复杂的动画层混合逻辑，通过资产化的方式管理动画层，而不是在蓝图或代码中硬编码。其核心是创建和编辑 Layer Stack 资产，这些资产定义了动画层的堆叠、混合和过渡规则，然后在运行时由 UAF 系统消费这些资产来驱动动画状态。

该插件解决了在复杂动画系统中（如角色定制、装备换装、状态组合）对动画层进行可配置、可视化和高效管理的需求，是 UAF 动画框架向更高级动画编辑工具链发展的一部分。

## 使用场景

-   **角色装备系统**：当角色穿戴不同护甲或服装时，可以通过 Layer Stack 定义装备层如何覆盖、混合或附加到基础动画层上。
-   **复杂状态组合**：实现诸如“受伤状态下的奔跑”、“携带武器时的跳跃”等需要将多个动画状态组合在一起的效果。
-   **动画编辑器工具**：作为自定义动画资产编辑器的基础，让动画师能在编辑器中直观地可视化、编辑和调试复杂的动画层堆栈。
-   **程序化动画混合**：在代码中创建和修改动画层堆栈，实现动态的、基于游戏逻辑的动画混合。

## 蓝图用法

由于这是一个实验性的 Runtime 和编辑器框架，且当前模块是测试模块，直接可调用的蓝图节点信息有限。核心功能更多地通过 C++ API 和自定义编辑器界面暴露。可以预期未来会有用于加载、查询和应用 Layer Stack 资产的蓝图节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| *（预计未来提供）* | 加载和应用 Layer Stack 资产到动画实例 | `UAnimationLayerManager`（推测） |

### 使用示例（蓝图描述）

在蓝图中，预期的典型用法可能是：
1.  获取一个 `UAnimLayerStack` 资产的引用。
2.  将该资产传递给角色动画蓝图中的一个管理节点（例如 “Apply Layer Stack”）。
3.  动画蓝图在更新时，会根据该资产的定义来混合基础动画和多个动画层。

## C++ 用法

用法主要体现在创建和测试 Layer Stack 资产以及其运行时组件。

### 头文件引入

```cpp
#include "AnimationLayerStack.h" // 推测的主要头文件
#include "AnimationLayerManagerComponent.h" // 推测的组件头文件
```

### 基本用法

以下代码模式基于测试用例和框架逻辑的常见模式推断：

```cpp
// 假设的用法：创建或加载一个 Layer Stack 资产
UAnimLayerStack* LayerStackAsset = LoadObject<UAnimLayerStack>(nullptr, TEXT("/Game/Animation/LayerStacks/LS_BaseArmor"));

// 假设的用法：在动画实例或组件上应用该 Layer Stack
UAnimationLayerManagerComponent* LayerManager = CharacterMesh->FindComponentByClass<UAnimationLayerManagerComponent>();
if (LayerManager && LayerStackAsset)
{
    LayerManager->SetLayerStack(LayerStackAsset);
}
```

### 进阶用法

进阶用法涉及动态地修改 Layer Stack 的层定义或混合权重，这通常通过继承和重写相关类来实现，或者在运行时通过代码修改资产实例（如果设计允许）。

## Demo 示例

由于这是底层框架，没有独立的可运行 Demo。其 Demo 是其自身的测试用例，验证了核心数据结构的正确性。一个最小的 C++ 示例可能涉及定义自定义的动画层数据结构：

```cpp
// MyAnimationLayers.h
#pragma once

#include "AnimationLayerStack.h" // 包含基础框架
#include "MyAnimationLayers.generated.h"

// 定义一个自定义的动画层数据结构，用于描述一个具体的动画层（如“受伤遮罩”）
USTRUCT(BlueprintType)
struct FMyInjuryMaskLayer : public FAnimLayerBase // 假设存在基类
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    float InjuryWeight = 1.0f;

    // 其他受伤遮罩相关的属性...
};

// 创建一个包含此层的 Layer Stack
// 通常在编辑器中或通过工厂类创建，这里仅为概念示例
// UAnimLayerStack* MyStack = NewObject<UAnimLayerStack>();
// MyStack->AddLayer<FMyInjuryMaskLayer>();
```

## 模块依赖

从各模块的 `Build.cs` 文件和插件依赖关系推断。

| 模块 | 用途 |
|---|---|
| `UAF` | Unreal Animation Framework 核心，提供动画资产和评估系统的基础 |
| `Workspace` | 用于在编辑器中创建和集成自定义资产编辑器（如 Layer Stack 编辑器） |
| `AnimationLayeringRuntime` | 提供动画层评估的底层运行时支持 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将调试日志迁移到新的日志宏，保持代码风格统一。 |
| 2026-04-10 | `797a6da6` | Rename GetComponent to GetOrAddComponent to match functionality | 将组件获取函数重命名为“获取或添加”，更准确地描述其延迟创建行为。 |
| 2026-03-05 | `dd5531fb` | UAF Layering: | （提交信息不完整，推测为与 UAF 层叠系统相关的更新或修复） |
| 2026-03-04 | `d9a06590` | Update UAF blend profiles | 更新了 UAF 的混合配置文件，可能影响层叠混合的默认行为或数据结构。 |
| 2026-03-04 | `95766f52` | UAF Layering: Expand outliner items per default | 改进了编辑器中大纲视图的默认显示行为，让层叠项目的子项默认展开，提升可用性。 |

### 维护评价

-   **活跃维护**：插件创建于 2026 年 1 月，最近一次提交在 2026 年 4 月，更新频繁，表明项目处于活跃开发阶段。
-   **实验性阶段**：插件标记为 `IsExperimentalVersion: true` 且默认禁用，这意味着其 API 和功能可能会发生 breaking changes。
-   **推荐使用**：由于处于实验阶段，不建议在面向生产的稳定项目中直接使用。但对于参与引擎开发、研究动画技术或愿意承担迭代风险的项目和开发者，这是一个值得关注的前沿功能。建议将其视为一个学习和贡献的前沿领域。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFLayering)
- [官方文档]() (暂无)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFLayering/Tests)