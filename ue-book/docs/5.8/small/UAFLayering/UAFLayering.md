# UAF Layering

> Framework to define a layering setup in UAF

| 属性 | 值 |
|---|---|
| 中文名 | UAF 动画层叠 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（层叠资产、蓝图工具） |
| 模块 | `UAFLayering` (Runtime), `UAFLayeringEditor` (Runtime), `UAFLayeringUncookedOnly` (Runtime), `UAFLayeringTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-01-13 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFLayering) | |

## 用途

UAF Layering 是构建在 Unreal Animation Framework（UAF）上的**动画层叠系统**。它解决的核心问题是：如何将多个动画源（如基础移动、上半身覆盖、表情叠加等）以分层方式组合在一起，并在运行时动态控制每一层的启用/禁用、权重和混合行为。

该插件基于 UAF 的 Trait（特质）架构构建，引入了以下关键概念：

- **Layer Stack（层叠栈）**：一种特殊的动画图资产（`UUAFLayerStack`），用于组织和定义多个动画层的堆叠关系
- **Layer Data Provider Trait**：运行时特质，负责管理每层的权重、混合时间、启用状态等属性，并通过事件系统响应外部控制
- **Layer Asset Data Provider Trait**：在运行时根据层叠配置中的资产数据创建 UAF 动画图，并将其推入混合栈
- **Montage Layer Trait**：支持基于动画蒙太奇运行时数据动态修改已有层的行为
- **Cache Pose Trait**：缓存姿态（当前尚未完整实现）

插件必须手动启用（`EnabledByDefault=false`），且标记为实验性（`IsExperimentalVersion=true`），说明 API 尚未稳定。

## 使用场景

- 你在开发角色动画系统，需要将**基础动画、上半身覆盖、武器持握、面部表情**等多个动画源以分层方式混合 → 用 UAF Layering
- 你需要在运行时动态**启用/禁用某个动画层**（如切换武器时启用持枪层） → 用 UAF Layering 的层控制 API
- 你需要让动画层在**激活/停用时有平滑的混合过渡**（而非瞬间切换） → 用 Layer Data Provider 的 BlendIn/BlendOut 时间
- 你使用 UAF 的蒙太奇系统，并希望**蒙太奇播放时自动影响层叠状态** → 用 Montage Layer Trait

## 蓝图用法

蓝图 API 主要通过 `UUAFLayeringUtils` 工具类暴露，所有方法均为 `BlueprintCallable`，分类为 `UAF|Layering`。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `EnableLayer` | 按名称启用指定层叠栈中的某个层 | `UUAFLayeringUtils` |
| `DisableLayer` | 按名称禁用指定层叠栈中的某个层 | `UUAFLayeringUtils` |
| `SetLayerWeight` | 按名称设置指定层的权重（0.0~1.0） | `UUAFLayeringUtils` |
| `EnableLayerByIndex` | 按索引启用指定层叠栈中的某个层 | `UUAFLayeringUtils` |
| `DisableLayerByIndex` | 按索引禁用指定层叠栈中的某个层 | `UUAFLayeringUtils` |
| `SetLayerWeightByIndex` | 按索引设置指定层的权重 | `UUAFLayeringUtils` |

### 使用示例（蓝图描述）

**按名称控制层**：

1. 获取角色的 `UAFComponent` 引用
2. 创建一个指向 `UUAFLayerStack` 资产的软对象引用（Soft Object Pointer）
3. 连接到 `EnableLayer` 节点：`UAFComponent` → 第一个引脚，层名称（如 `"UpperBody"`）→ `LayerName`，层叠栈资产 → `LayerStackPath`
4. 如需调整权重，连接 `SetLayerWeight` 节点，将 `Weight` 设为 0.0~1.0 之间的浮点值

**按索引控制层**（适合性能敏感场景，避免名称查找）：

1. 同样获取 `UAFComponent` 和层叠栈资产引用
2. 连接 `EnableLayerByIndex`，将 `LayerIndex` 设为目标层在层叠栈中的索引位置

## C++ 用法

### 头文件引入

```cpp
#include "UAFLayeringUtils.h"
#include "UAFLayeringTypes.h"
```

### 基本用法

通过 `UUAFLayeringUtils` 在 C++ 中控制动画层：

```cpp
// 引自 UAFLayeringTypes.h 及 UAFLayeringUtils.h
#include "UAFLayeringUtils.h"
#include "UAFLayeringTypes.h"

// 假设已有 UAFComponent 和层叠栈资产引用
UUAFComponent* UAFComp = /* 获取角色的 UAFComponent */;
TSoftObjectPtr<UUAFLayerStack> LayerStack = /* 层叠栈资产引用 */;

// 按名称启用层
UUAFLayeringUtils::EnableLayer(UAFComp, FName("UpperBody"), LayerStack);

// 按名称设置层权重（0.0 = 完全透明, 1.0 = 完全应用）
UUAFLayeringUtils::SetLayerWeight(UAFComp, FName("UpperBody"), LayerStack, 0.75f);

// 按索引禁用层
UUAFLayeringUtils::DisableLayerByIndex(UAFComp, 0, LayerStack);
```

### 进阶用法

通过 UAF 事件系统直接发送层事件，可获得更多控制：

```cpp
// 引自 UAFLayeringTypes.h
#include "UAFLayeringTypes.h"

using namespace UE::UAF::Layering;

// 创建层事件 - 启用层
FSoftObjectPath StackPath = LayerStack->GetPathName();
FLayerStack_LayerEvent EnableEvent(FName("ArmLayer"), StackPath);
EnableEvent.Action = ELayerEventAction::EnableLayer;
EnableEvent.bAutoConsumeEvent = true;  // 第一个匹配的层消费此事件

// 创建层事件 - 设置权重
FLayerStack_LayerEvent WeightEvent(FName("ArmLayer"), StackPath);
WeightEvent.Action = ELayerEventAction::SetFloatValue;
WeightEvent.PropertyToSet = FLayerStack_LayerEvent::LayerWeightProperty;
WeightEvent.FloatValue = 0.5f;

// 通过索引创建事件
FLayerStack_LayerEvent IndexEvent(0, StackPath);
IndexEvent.Action = ELayerEventAction::DisableLayer;
```

**层属性配置**（`FUAFLayerProperties`）：

```cpp
#include "Traits/LayerDataProviderTraitData.h"

// 配置层属性（通常在资产编辑器中设置）
FUAFLayerProperties LayerProps;
LayerProps.bLayerEnabled = true;
LayerProps.DesiredLayerWeight = 1.0f;
LayerProps.BlendInTime = 0.2f;        // 激活时 0.2 秒混合进入
LayerProps.BlendOutTime = 0.3f;       // 停用时 0.3 秒混合退出
LayerProps.BlendCurve = MyBlendCurve; // 自定义混合曲线
LayerProps.BlendOption = EAlphaBlendOption::EaseInOut;
```

## Demo 示例

以下展示如何在自定义组件中封装层叠控制逻辑：

```cpp
// MyLayerController.h
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "UAFLayeringUtils.h"
#include "UAFLayeringTypes.h"
#include "UAFComponent.h"
#include "UAFLayerStack.h"
#include "MyLayerController.generated.h"

UCLASS(ClassGroup=(UAF), meta=(BlueprintSpawnableComponent))
class MYGAME_API UMyLayerController : public UActorComponent
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Layering")
	TSoftObjectPtr<UUAFLayerStack> LayerStack;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Layering")
	TMap<FName, float> LayerWeights;

	// 启用指定层
	UFUNCTION(BlueprintCallable, Category = "Layering")
	void ActivateLayer(FName LayerName);

	// 禁用指定层
	UFUNCTION(BlueprintCallable, Category = "Layering")
	void DeactivateLayer(FName LayerName);

	// 设置层权重
	UFUNCTION(BlueprintCallable, Category = "Layering")
	void SetWeight(FName LayerName, float Weight);
};
```

```cpp
// MyLayerController.cpp
#include "MyLayerController.h"

void UMyLayerController::ActivateLayer(FName LayerName)
{
	UUAFComponent* UAFComp = GetOwner()->FindComponentByClass<UUAFComponent>();
	if (UAFComp && !LayerStack.IsNull())
	{
		UUAFLayeringUtils::EnableLayer(UAFComp, LayerName, LayerStack);
		LayerWeights.FindOrAdd(LayerName) = 1.0f;
	}
}

void UMyLayerController::DeactivateLayer(FName LayerName)
{
	UUAFComponent* UAFComp = GetOwner()->FindComponentByClass<UUAFComponent>();
	if (UAFComp && !LayerStack.IsNull())
	{
		UUAFLayeringUtils::DisableLayer(UAFComp, LayerName, LayerStack);
	}
}

void UMyLayerController::SetWeight(FName LayerName, float Weight)
{
	UUAFComponent* UAFComp = GetOwner()->FindComponentByClass<UUAFComponent>();
	if (UAFComp && !LayerStack.IsNull())
	{
		UUAFLayeringUtils::SetLayerWeight(UAFComp, LayerName, LayerStack, Weight);
		LayerWeights.FindOrAdd(LayerName) = Weight;
	}
}
```

## 模块依赖

基于源码中的类型引用（UAFComponent、UUAFAnimGraph、FAnimNextTraitSharedData、FGraphAssetHandle 等）以及 .uplugin 中声明的插件依赖：

| 模块 | 用途 |
|---|---|
| `UAF` | 核心动画框架，提供 UAFComponent、UUAFAnimGraph 等基础类型 |
| `AnimNext` | 动画特质系统（Trait System），提供 FAnimNextTraitSharedData 等基础设施 |
| `Workspace` | 工作区集成，用于资产编辑器中的层叠栈编辑 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF |
| 2026-04-10 | `797a6da6` | Rename GetComponent to GetOrAddComponent to match functionality | 将 GetComponent 重命名为 GetOrAddComponent 以匹配实际功能 |
| 2026-03-05 | `dd5531fb` | UAF Layering: | UAF Layering 相关更新（提交信息不完整） |
| 2026-03-04 | `d9a06590` | Update UAF blend profiles | 更新 UAF 混合配置文件 |
| 2026-03-04 | `95766f52` | UAF Layering: Expand outliner items per default | UAF Layering：默认展开大纲视图条目 |

### 维护评价

- **状态**：活跃开发中
- **创建时间**：2026-01-13，至今约 3 个月，属于全新插件
- **更新频率**：近期有持续更新（最近一次 2026-04-14），包括代码质量改进（日志宏迁移）、API 重命名、功能迭代
- **已知限制**：
  - 标记为实验性（`IsExperimentalVersion=true`），API 可能发生破坏性变更
  - 默认未启用（`EnabledByDefault=false`），需要手动在项目设置中启用
  - Cache Pose Trait 的注释明确说明"尚未完整实现"（`TODO: Not implemented yet`）
  - `FUAFLayerProperties` 中多个属性带有 `TODO: this should be a binding` 标记，表明绑定系统尚未完成
- **推荐程度**：如果你正在使用或评估 UAF 动画框架，且需要分层混合功能，可以关注此插件的进展。但由于其处于早期实验阶段，不建议在生产项目中直接依赖。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFLayering)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFLayering/Tests)