# Mutable Groom Extensions

> Adds Mutable functionality to work with Grooms from the HairStrands plugin（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 可扩展发型 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `HairStrandsMutable` (Runtime), `HairStrandsMutableEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-08-08 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/HairStrandsMutable) | |

## 用途

本插件是 **HairStrands** (负责毛发/发型渲染和模拟) 与 **Mutable** (负责运行时角色/物体的模块化定制与组合) 之间的桥梁。它解决了在 Mutable 的可定制对象（Customizable Object）系统中，如何将发型（Groom）作为一种可定制的资产进行集成和管理的问题。没有此插件，用户无法在 Mutable 的节点图中定义和控制发型的变体，也就无法实现角色身体与发型的独立、动态定制。

简单来说，它让你能在角色创建或装备更换界面中，像切换盔甲或发型一样，动态地更换角色的发型资产。

## 使用场景

-   你正在开发一个拥有深度角色自定义系统的 RPG 或 MMO 游戏（例如《赛博朋克2077》的角色编辑器）。玩家不仅可以选择脸型、身体，还能从数十种发型中挑选。你使用 **Mutable** 来管理所有身体部件和服装的组合与优化，现在你需要将发型也纳入这个系统，实现一键生成包含正确发型的完整角色模型。
-   你的游戏允许玩家装备不同的“帽子”或“头盔”，这些装备可能需要移除或改变原始发型（例如，戴上头盔后隐藏长发）。通过此插件，你可以在 Mutable 的逻辑中根据装备状态来动态添加、移除或替换发型组件。

## 蓝图用法

本插件的核心功能主要在编辑器中的 **Customizable Object** 节点图中通过专用节点实现，而非直接在运行时蓝图中调用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Groom Constant` | 在 Mutable 节点图中创建一个代表发型资产的常量节点。 | 通过编辑器 UI 创建 |

### 使用示例（蓝图/节点图描述）

在打开 **Customizable Object Editor** 后，你可以：
1.  在节点图右键菜单中，找到 **Add Groom Constant Node** 选项。
2.  该节点会创建一个具有特定输入引脚（Pin）的节点，用于连接发型数据。
3.  将这个 Groom Constant 节点的输出引脚，连接到你的可定制对象主节点（Object Node）上的 **Grooms** 引脚。
4.  在 Groom Constant 节点的属性面板中，配置 `FGroomPinData` 结构体的各项内容，如指定使用的 `GroomAsset`、绑定到哪个网格体组件（`ComponentName`）等。
5.  当 Mutable 系统编译并生成实例时，插件会自动根据这些数据，在运行时实例化或移除对应的 `UGroomComponent`，并将其附加到指定的网格体上。

## C++ 用法

主要涉及两个方面：在编辑器工具中扩展，以及在运行时理解数据结构。

### 头文件引入

```cpp
#include "HairStrandsMutableExtension.h" // 核心扩展和数据类型
#include "HairStrandsMutableModule.h"   // 模块加载
```

### 基本用法：理解并使用发型数据结构

当你在编写涉及 Mutable 扩展或处理运行时生成的定制数据时，需要了解其核心数据结构。

```cpp
// 来源: Public/HairStrandsMutableExtension.h
// FGroomPinData 结构体用于在编辑器图和运行时之间传递发型配置信息
FGroomPinData GroomPinData;
GroomPinData.ComponentName = FName("Head"); // 指定发型要附加到哪个主网格体组件（如角色的头部网格体）
GroomPinData.GroomAsset = MyGroomAsset; // 设置要使用的发型资产
GroomPinData.BindingAsset = MyBindingAsset; // 可选：设置绑定资产（用于将发型绑定到特定网格体）
GroomPinData.OverrideMaterials.Add(MyGroomMaterial); // 可选：覆盖发型使用的材质

// UGroomCompiledData 是运行时实际使用的 UObject，包含与 FGroomPinData 相似的属性。
// 通常，用户代码不需要直接创建或操作 UGroomCompiledData 实例，它由 Mutable 系统内部管理。
```

### 进阶用法：实现自定义的 Mutable 扩展（高级）

对于需要深度集成或类似功能的开发者，可以参考 `UHairStrandsMutableExtension` 的实现模式。

```cpp
// 来源: Public/HairStrandsMutableExtension.h
// UHairStrandsMutableExtension 继承自 UCustomizableObjectExtension
// 它为 Mutable 系统注册了新的引脚类型（GroomPinType）和节点输入引脚（GroomsBaseNodePinName）。
// 并实现了几个关键的回调：
// 1. GetPinTypes(): 注册新的引脚类型，使 Mutable 编辑器能识别发型引脚。
// 2. GetAdditionalObjectNodePins(): 为可定制对象节点添加额外的输入引脚（即 Grooms 引脚）。
// 3. OnCustomizableObjectInstanceUsageUpdated(): 当可定制对象实例使用情况更新时，负责实例化或移除 GroomComponent。
// 4. OnCustomizableObjectInstanceUsageDiscarded(): 当实例被丢弃时，负责清理 GroomComponent。
```

## Demo 示例

以下是一个极度简化的示例，展示如何在 C++ 中定义一个使用 `FGroomPinData` 的自定义结构，以及扩展 `UCustomizableObjectExtension` 的基本思路。

```cpp
// MyGroomCustomizationData.h
#pragma once
#include "HairStrandsMutableExtension.h" // 引入 FGroomPinData

// 你可以在自己的模块中定义一个结构体，包含发型配置，供你的游戏逻辑使用
USTRUCT(BlueprintType)
struct FMyGameGroomSlot
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, Category = "Groom")
	FName SlotName;

	UPROPERTY(EditAnywhere, Category = "Groom")
	FGroomPinData GroomConfig; // 内嵌核心的发型配置数据
};
```

```cpp
// MyGroomExtension.h (假设你要实现类似功能)
#pragma once
#include "CustomizableObjectExtension.h"
#include "MyGroomExtension.generated.h"

UCLASS(MinimalAPI)
class UMyGroomExtension : public UCustomizableObjectExtension
{
	GENERATED_BODY()

public:
	// 注册自定义的引脚类型（例如，用于不同的发型类别）
	virtual TArray<FCustomizableObjectPinType> GetPinTypes() const override
	{
		TArray<FCustomizableObjectPinType> PinTypes;
		// PinTypes.Add(FCustomizableObjectPinType(...)); // 定义你的引脚类型
		return PinTypes;
	}

	// 为 Object 节点添加额外的输入引脚
	virtual TArray<FObjectNodeInputPin> GetAdditionalObjectNodePins() const override
	{
		TArray<FObjectNodeInputPin> Pins;
		// Pins.Add(FObjectNodeInputPin(...)); // 定义你的引脚，例如 "SecondaryGrooms"
		return Pins;
	}

	// 当实例更新时，根据附加的扩展数据（ExtensionData）来管理组件
	virtual void OnCustomizableObjectInstanceUsageUpdated(
		UCustomizableObjectInstanceUsage& Usage,
		TArray<TObjectPtr<const UObject>>& ExtensionData) const override
	{
		// 在这里，你可以遍历 ExtensionData（可能是 UGroomCompiledData 或你自定义的 UObject）
		// 并调用类似的操作来实例化、更新或移除组件。
		// UHairStrandsMutableExtension 内部正是如此处理发型组件的。
	}
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `HairStrands` | 提供发型资产（`UGroomAsset`）、组件（`UGroomComponent`）和相关管理类。 |
| `Mutable` | 提供可定制对象系统的核心框架，本插件为其提供发型扩展。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-21 | `814648b2` | [mutable] Fixed check failure when trying to spawn a new object on a PostLoad call. | 修复了在 PostLoad 期间尝试生成新对象时发生的断言失败。 |
| 2026-03-11 | `aeecf60f` | [HairStrandsMutable] Fix ensure when registgering to Movie Sequence Template actors. | 修复了向影片序列模板演员注册时触发的 ensure 断言。 |
| 2026-03-06 | `87b39b7f` | [Mutable] Fix Extension Data not being applied when an Instance is already generated. | 修复了当实例已生成时，扩展数据未被应用的问题。 |
| 2026-02-27 | `f8a35ec8` | [Mutable] Add support for UAssetUserData in SKM Parameter and Constants nodes. | 为骨骼网格体参数和常量节点添加了对 UAssetUserData 的支持。 |
| 2026-01-29 | `17d7a59b` | [Mutable] Fix PSO check with grooms. | 修复了与发型相关的管线状态对象（PSO）检查问题。 |

### 维护评价

该插件处于**实验性**阶段，但维护状态**活跃**。创建于2024年8月，最近一次更新在2026年5月，表明 Epic Games 正在持续对其开发和修复。更新内容涵盖了功能增加（如AssetUserData支持）和关键Bug修复，主要集中在确保其与 Mutable 和 HairStrands 核心插件的稳定集成上。由于其实验性质，API 和行为在未来版本中可能发生变动，但目前是实现角色发型与 Mutable 系统集成的**唯一官方途径**，对于有此需求的项目是**推荐尝试和关注**的。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/HairStrandsMutable)
- [依赖插件：HairStrands](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/HairStrands)
- [依赖插件：Mutable](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable)