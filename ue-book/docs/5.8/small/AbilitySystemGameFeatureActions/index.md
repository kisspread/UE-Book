# Gameplay Abilities Game Feature Actions

> Game feature actions to support modular use of the gameplay abilities system（照抄）

| 属性 | 值 |
|---|---|
| 中文名 | 能力系统游戏特性动作 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AbilitySystemGameFeatureActions` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-08-04 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AbilitySystemGameFeatureActions) | |

## 用途

本插件为 **GameFeatures** 插件提供特定的游戏特性动作（Game Feature Action），用于管理 Gameplay Ability System (GAS) 中的**属性集默认表（Attribute Set Defaults）**。

它的核心价值在于实现 GAS 的**模块化**。在使用 GameFeatures 插件进行游戏内容模块化开发时，不同的游戏特性（例如一个“火焰魔法”特性）可能需要添加自己的属性默认表（例如 `FlameMagic_AttributeDefaults`）。本插件提供的 `UGameFeatureAction_AddAttributeDefaults` 动作，能够在游戏特性被**注册**或**激活**时，自动将指定的属性默认表加载并应用到 Ability System Component 上；在特性**注销**或**停用**时，则自动移除这些表，从而保证了属性状态的清洁和模块间的解耦。

## 使用场景

- 你的项目采用了 GameFeatures 插件来划分游戏内容（如不同职业、技能树、关卡扩展包）。
- 你希望在某个独立的游戏特性（Game Feature）模块中，包含该特性独有的 Gameplay Ability 属性默认值。
- 你需要在游戏特性的生命周期（加载/卸载）中，动态地添加和移除这些属性默认值。

## 蓝图用法

本插件提供的主要是一个编辑器内配置的动作资产，而非运行时蓝图节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Add Attribute Defaults` (Game Feature Action) | 编辑器中配置的动作资产，用于在游戏特性激活时加载属性默认表。 | `UGameFeatureAction_AddAttributeDefaults` |

### 使用示例（蓝图描述）

在 GameFeatures 插件的工作流中使用：

1.  创建一个 **Game Feature** 资产（例如 `M_FireMagic`）。
2.  在该资产的 **Actions** 数组中，添加一个元素，类型选择 `Add Attribute Defaults`。
3.  在该动作的属性面板中：
    *   **Attrib Default Table Names**: 添加你的属性默认表资产路径（`FSoftObjectPath`），例如指向一个 `DataTable` 资产。
    *   **Apply On Register**: 勾选此项，表示在游戏特性被**注册**（而非激活）时就应用这些默认值。取消勾选则会在特性**激活**时应用。

## C++ 用法

本插件主要提供了一个 `UGameFeatureAction` 的子类，供开发者在 C++ 中直接创建或继承。

### 头文件引入

```cpp
#include "GameFeatureAction_AddAttributeDefaults.h"
```

### 基本用法

以下示例展示了如何在 C++ 中创建一个配置好的 `UGameFeatureAction_AddAttributeDefaults` 实例。

*来源文件: `Source/AbilitySystemGameFeatureActions/Public/GameFeatureAction_AddAttributeDefaults.h`*

```cpp
// 在你的游戏模块初始化代码或数据资产中
#include "GameFeatureAction_AddAttributeDefaults.h"
#include "Engine/DataTable.h"

// 假设你已经有一个属性默认表的软引用
FSoftObjectPath MyAttributeDefaultsTablePath = TEXT("/Game/Data/DA_MyCharacterAttributeDefaults");

// 创建动作实例
UGameFeatureAction_AddAttributeDefaults* AddDefaultsAction = NewObject<UGameFeatureAction_AddAttributeDefaults>();
AddDefaultsAction->bApplyOnRegister = true; // 设置为注册时应用
AddDefaultsAction->AttribDefaultTableNames.Add(MyAttributeDefaultsTablePath);

// 这个 Action 对象通常会被添加到某个 UGameFeatureData 资产的 Actions 数组中。
```

### 进阶用法

了解其生命周期管理，以便进行自定义扩展或调试。

*来源文件: `Source/AbilitySystemGameFeatureActions/Public/GameFeatureAction_AddAttributeDefaults.h`*

```cpp
// 该类重写了 GameFeatureAction 的关键生命周期方法
virtual void OnGameFeatureRegistering() override;   // 特性被注册时
virtual void OnGameFeatureActivating(FGameFeatureActivatingContext& Context) override; // 特性被激活时
virtual void OnGameFeatureUnregistering() override; // 特性被注销前
virtual void OnGameFeatureDeactivating(FGameFeatureDeactivatingContext& Context) override; // 特性被停用前

// 内部使用 bApplyOnRegister 标志和 bAttributesHaveBeenSet 状态来判断
// 在哪一步（注册/激活）应用或移除属性默认表。
```

## Demo 示例

一个简单的自定义游戏特性动作类，扩展了添加属性默认值的功能，在激活时打印日志。

```cpp
// MyGameFeatureAction_AddAttributeDefaults.h
#pragma once

#include "CoreMinimal.h"
#include "GameFeatureAction_AddAttributeDefaults.h"
#include "MyGameFeatureAction_AddAttributeDefaults.generated.h"

UCLASS(MinimalAPI, meta = (DisplayName = "Add Attribute Defaults With Log"))
class UMyGameFeatureAction_AddAttributeDefaults : public UGameFeatureAction_AddAttributeDefaults
{
	GENERATED_BODY()

public:
	virtual void OnGameFeatureActivating(FGameFeatureActivatingContext& Context) override
	{
		// 调用父类逻辑以应用属性默认表
		Super::OnGameFeatureActivating(Context);
		UE_LOG(LogTemp, Log, TEXT("Game Feature activated, attribute defaults applied."));
	}

	virtual void OnGameFeatureDeactivating(FGameFeatureDeactivatingContext& Context) override
	{
		Super::OnGameFeatureDeactivating(Context);
		UE_LOG(LogTemp, Log, TEXT("Game Feature deactivated, attribute defaults removed."));
	}
};
```

```cpp
// MyGameFeatureAction_AddAttributeDefaults.cpp
#include "MyGameFeatureAction_AddAttributeDefaults.h"

// 通常，这个类只需要头文件中的声明和重写，无需额外的 .cpp 实现。
// 如果需要添加成员变量或更复杂的逻辑，则在此文件中实现。
```

## 模块依赖

本插件自身的 `Build.cs` 文件声明了以下依赖，使用本插件的项目或模块通常也需要依赖这些模块：

| 模块 | 用途 |
|---|---|
| `GameFeatures` | 核心依赖，提供 Game Feature Action 的基类和生命周期管理框架。 |
| `GameplayAbilities` | 核心依赖，提供 Gameplay Ability System 的核心功能，包括属性集（AttributeSet）相关接口。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2024-11-10 | `66e9bb39` | Removed all #if UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes from the code base | 移除过时的头文件包含顺序保护宏，代码维护性更新。 |
| 2024-05-29 | `898df968` | Added toggle to apply attribute set defaults in OnGameFeatureActivating | 新增`bApplyOnRegister`选项，控制属性默认表在注册或激活时应用。 |
| 2024-01-30 | `92cb46cb` | Fix GameFeatureAction_AddAttributeDefaults not cleaning up references to objects when unregistered | 修复了注销特性时未正确清理对象引用的缺陷。 |
| 2023-10-10 | `a3071245` | #UE Do not load attribute tables if you do not have them. This can happen if folks opt to not sync c | 优化逻辑，仅在属性表存在时加载，避免不必要的错误。 |
| 2023-05-15 | `da92084a` | Optimized out more private modules includes and dependencies. | 优化私有模块依赖，减少编译影响。 |

### 维护评价

该插件创建于2021年，作为**实验性** (`IsBetaVersion=true`) 且**默认禁用**的功能。从近期提交记录看，它在过去1年内仍有功能增强（添加开关选项）和 Bug 修复活动，表明 Epic 仍在进行维护。最近一次更新是2024年11月的代码清理，属于常规维护。

**综合评价**：
- **优点**：提供了解决 GAS 模块化加载特定问题的标准方案，代码量小，职责单一。
- **注意点**：仍处于实验性状态，API 或行为在 UE 后续版本中可能发生变化。`EnabledByDefault=false` 需要手动启用。
- **推荐**：如果你的项目严重依赖 GameFeatures 和 GameplayAbilities 的模块化组合，那么**推荐使用**此插件来管理属性默认值的生命周期。在生产环境中应留意其实验性标签，关注版本更新说明。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AbilitySystemGameFeatureActions)
- 官方文档: 无
- 测试用例: 无（插件目录内未包含测试文件）