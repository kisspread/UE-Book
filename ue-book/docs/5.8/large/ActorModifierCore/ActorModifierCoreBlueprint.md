# Actor Modifier Core

> Use modifier objects on actors to apply a custom behavior（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | Actor修改器核心 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产， 蓝图编辑器资源） |
| 模块 | `ActorModifierCore` (Runtime), `ActorModifierCoreBlueprint` (UncookedOnly), `ActorModifierCoreEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/ActorModifierCore) | |

## 用途
Actor Modifier Core 是一个用于虚拟制片（Virtual Production）工作流的核心插件。它提供了一套框架，允许用户为 Actor 附加一种称为“修改器”（Modifier）的对象。这些修改器可以在运行时或编辑器中程序化地改变 Actor 的外观、属性或行为。

此插件的核心价值在于**非破坏性工作流**。它解决了在虚拟制片场景中，需要对大量 Actor（如灯光、相机、几何体）进行程序化、可堆叠、可配置的复杂变换或效果应用的痛点。例如，你可以创建一个“抖动”修改器并将其应用到多个灯光上，而无需手动动画或修改每个灯光的蓝图。

## 使用场景
- 你在进行虚拟制片，需要为场景中的多个灯光添加程序化的闪烁或呼吸效果。
- 你需要在不修改原始资产蓝图的情况下，为几何体动态添加变形、替换材质或应用后处理效果。
- 你想要创建可重用的效果模块（修改器），并在不同项目、不同 Actor 上快速复用。
- 你需要一个类似堆栈（Stack）的工作流，可以为同一个 Actor 添加、排序、启用/禁用多个修改器。

## 蓝图用法
此插件主要通过编辑器扩展和蓝图资产来工作。`ActorModifierCoreBlueprint` 模块专门用于支持基于蓝图的修改器创建。

### 核心概念
- **修改器蓝图（Modifier Blueprint）**：基于 `UActorModifierCoreBlueprint` 创建的特殊蓝图，用于定义修改器的具体逻辑。
- **修改器堆栈（Modifier Stack）**：附加在 Actor 上的组件，管理该 Actor 上所有激活的修改器实例及其执行顺序。

### 使用示例（蓝图描述）
1.  **创建自定义修改器**：在内容浏览器中右键 -> Blueprint Class -> 选择 `ActorModifierCoreBlueprint` 作为父类。
2.  **定义修改器行为**：在新创建的蓝图中，实现事件图表来定义当修改器被应用时，如何改变目标 Actor。这可能包括修改变换、调用函数、更改材质等。
3.  **应用修改器**：在编辑器中选中一个或多个 Actor，在细节面板中找到“Modifier Stack”组件，添加你创建的修改器蓝图类。可以在堆栈中调整多个修改器的执行顺序。

## C++ 用法
### 头文件引入
```cpp
// 核心运行时模块
#include "ActorModifierCore.h"

// 蓝图支持模块 (用于创建蓝图修改器)
#include "ActorModifierCoreBlueprint.h"

// 编辑器扩展模块 (用于编辑器集成)
#include "ActorModifierCoreEditor.h"
```

### 基本用法
基于插件结构，典型的 C++ 用法是创建自定义的 C++ 修改器类，供编辑器或蓝图使用。

```cpp
// MyCustomModifier.h
#pragma once

#include "CoreMinimal.h"
#include "ActorModifierCore/ActorModifierCoreBase.h" // 假设的基类头文件
#include "MyCustomModifier.generated.h"

UCLASS(Blueprintable)
class UMyCustomModifier : public UActorModifierCoreBase // 继承自修改器基类
{
	GENERATED_BODY()

public:
	virtual void ApplyModifier(AActor* TargetActor) override;
	virtual void RemoveModifier(AActor* TargetActor) override;

protected:
	// 可在蓝图或编辑器中配置的属性
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Custom")
	float Intensity = 1.0f;
};
```

```cpp
// MyCustomModifier.cpp
#include "MyCustomModifier.h"

void UMyCustomModifier::ApplyModifier(AActor* TargetActor)
{
	if (TargetActor)
	{
		// 实现应用修改器的逻辑
		UE_LOG(LogTemp, Log, TEXT("Applying custom modifier with intensity: %f"), Intensity);
	}
}

void UMyCustomModifier::RemoveModifier(AActor* TargetActor)
{
	if (TargetActor)
	{
		// 实现移除修改器的逻辑
		UE_LOG(LogTemp, Log, TEXT("Removing custom modifier."));
	}
}
```

### 进阶用法
该插件与 `OperatorStack` 插件有依赖关系，表明它可能提供了一个可视化的堆栈编辑器界面。C++ 开发者可以利用这个框架创建具有复杂交互和实时预览能力的修改器，并在编辑器的自定义面板中为它们提供配置界面。

## Demo 示例
以下是一个最简单的 C++ 修改器示例，当应用时会打印一条消息到日志。

```cpp
// File: SimplePrintModifier.h
#pragma once

#include "CoreMinimal.h"
#include "ActorModifierCore/ActorModifierCoreBase.h" // 假设的基类头文件
#include "SimplePrintModifier.generated.h"

UCLASS(Blueprintable)
class USimplePrintModifier : public UActorModifierCoreBase
{
	GENERATED_BODY()

public:
	// 当修改器被应用到Actor时调用
	virtual void ApplyModifier(AActor* TargetActor) override
	{
		if (TargetActor)
		{
			UE_LOG(LogTemp, Warning, TEXT("SimplePrintModifier applied to: %s"), *TargetActor->GetName());
		}
	}

	// 当修改器从Actor移除时调用
	virtual void RemoveModifier(AActor* TargetActor) override
	{
		if (TargetActor)
		{
			UE_LOG(LogTemp, Warning, TEXT("SimplePrintModifier removed from: %s"), *TargetActor->GetName());
		}
	}
};
```

## 模块依赖
你的模块需要依赖此插件的模块才能使用其功能。

| 模块 | 用途 |
|---|---|
| `ActorModifierCore` | 修改器运行时的核心逻辑，是必须依赖的模块。 |
| `OperatorStack` | 为修改器堆栈提供可视化的编辑器界面和操作逻辑。 |

## 维护状态

### 近期更新
该插件从实验性目录迁移至正式目录后，保持着稳定的更新。

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `2d1c7712` | Motion Design: fixed issue where duplicating actors with modifiers and deleting those new duplicates | 修复了复制带有修改器的Actor并删除新副本时的问题 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复了格式化函数中作用域枚举可能导致乱码输出的问题 |
| 2026-04-14 | `abb26688` | Actor Modifiers: added experimental freeze modifier feature. | Actor修改器：增加了实验性的冻结修改器功能。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将UE_LOG日志宏迁移至UE_LOGF。 |
| 2026-04-09 | `bdd66985` | Motion Design: made render state dirty reason optional + added some fixes to the text3d update causi | 运动设计：将渲染状态脏标记设为可选，并修复了导致Text3D更新的若干问题 |

### 维护评价
- **创建时间**：2025年5月，相对较新。
- **更新频率**：自2025年5月创建以来，截至2026年5月仍有功能性更新和Bug修复，维护活跃。
- **维护状态**：**活跃维护中**。该插件是 Epic Games 官方维护的虚拟制片工具链的一部分。
- **推荐使用**：✅ **推荐**。对于需要程序化、非破坏性地管理 Actor 行为和外观的虚拟制片项目，这是一个官方且持续维护的核心工具。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/ActorModifierCore)