# Level Snapshots - Filter Module

> （无描述）

| 属性 | 值 |
|---|---|
| 中文名 | 关卡快照过滤器 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `FoliageSupport` (Runtime), `LevelSnapshotFilters` (Runtime), `LevelSnapshots` (Runtime), `LevelSnapshotsEditor` (Runtime), `nDisplaySupport` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-02-03 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LevelSnapshots) | |

## 用途

LevelSnapshots 插件（及其 Filter 模块）的核心目的是为关卡（Level）提供“快照”与“回滚”能力。它允许在编辑器中保存关卡的完整状态（快照），并在后续任意时间点，有选择地将关卡中的 Actor 和属性恢复到快照中的版本。

`LevelSnapshotFilters` 模块专门提供了**过滤机制**。在应用快照时，它解决了“如何精细控制恢复哪些内容”的问题。通过定义和组合各种过滤器，用户可以指定：
- 哪些 Actor 应该被恢复（或忽略）。
- 哪些 Actor 的哪些具体属性（如变换、材质、自定义数据）应该被恢复。
- 如何处理快照后新增或删除的 Actor 及组件。

该模块是插件灵活应用的关键，使得从“全量恢复”到“条件性部分恢复”成为可能，是关卡迭代和版本管理的强大工具。

## 使用场景

- **关卡迭代与回滚**：你正在进行关卡设计，想保存一个“稳定版”快照。之后进行的修改可能导致问题，你可以使用过滤器（如只恢复特定类型的 Actor 或特定名称的属性）安全地回滚部分改动，而不是整个关卡。
- **团队协作**：不同成员负责关卡不同部分（如 A 做地形，B 做灯光）。应用来自 A 的快照时，可以使用过滤器只恢复地形相关的 Actor，不影响 B 的灯光设置。
- **数据修复**：某个 Blueprint 的默认值意外被批量修改，导致场景中大量实例异常。你可以拍摄修改前的快照，然后仅针对该 Blueprint 的实例，应用快照中正确的默认值。
- **场景清理与优化**：快照后，你新增了大量用于测试的 Actor。应用快照时，通过过滤器排除“新增 Actor”，可以快速清理测试对象，恢复场景。

## 蓝图用法

蓝图中主要通过继承 `ULevelSnapshotBlueprintFilter` 来创建自定义过滤器，或使用内置的过滤器类进行组合。`LevelSnapshotFilters` 模块暴露了创建和配置过滤器的节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Filter By Class` | 根据指定的 `ULevelSnapshotFilter` 子类创建一个新的过滤器实例。 | `UFilterBlueprintFunctionLibrary` |
| `Load Snapshot Actor` | 根据快照参数加载快照中保存的 Actor 实例（用于高级过滤查询）。 | `UPropertyBlueprintFunctionLibrary` |
| `Get Actor Class From Deleted Params` | 从已删除 Actor 的参数中获取其原始类信息。 | `UPropertyBlueprintFunctionLibrary` |
| `Get Property Origin Path` | 获取声明属性的类的路径字符串。 | `UPropertyBlueprintFunctionLibrary` |
| `Get Property Name` | 仅获取属性的名称部分。 | `UPropertyBlueprintFunctionLibrary` |
| `Is Actor Valid` (事件) | 在自定义过滤器中重写此事件，以决定是否包含某个 Actor。 | `ULevelSnapshotBlueprintFilter` |
| `Is Property Valid` (事件) | 在自定义过滤器中重写此事件，以决定是否恢复某个属性。 | `ULevelSnapshotBlueprintFilter` |

### 使用示例（蓝图描述）

1.  **创建一个仅作用于静态网格体的过滤器**：
    - 创建一个新的 `ULevelSnapshotBlueprintFilter` 子类蓝图。
    - 重写 `Is Actor Valid` 事件。
    - 使用 `Is Valid` 节点检查 `Snapshot Actor` 或 `Level Actor` 是否是 `StaticMeshActor` 的子类。
    - 如果是，返回 `Include`；否则返回 `Exclude`。

2.  **创建一个只恢复位置属性的过滤器**：
    - 使用 `Create Filter By Class` 节点，选择 `UTransformPropertyFilter` 类。
    - 获取其 `Location`、`Rotation`、`Scale` 属性。
    - 设置 `Location` 为 `Include`，`Rotation` 和 `Scale` 为 `Exclude`。

3.  **组合多个过滤器（逻辑与）**：
    - 使用 `Create Filter By Class` 节点，选择 `UAndFilter` 类。
    - 使用 `Create Child` 函数，分别为 `UAndFilter` 添加上面创建的“静态网格体过滤器”和“仅恢复位置过滤器”作为子过滤器。
    - 应用此 `AndFilter`，即可实现“仅恢复静态网格体的位置信息”。

## C++ 用法

在 C++ 中，你可以继承 `ULevelSnapshotFilter` 来创建高性能的自定义过滤器，或者利用 `ULambdaFilter` 进行快速原型开发。

### 头文件引入

```cpp
#include "LevelSnapshotFilters.h"
#include "Builtin/LambdaFilter.h"
// 如果需要特定过滤器，例如：
#include "Builtin/ActorHasTagFilter.h"
```

### 基本用法

最直接的方式是继承 `ULevelSnapshotFilter` 并重写虚函数。

```cpp
// MyCustomFilter.h
#pragma once
#include "LevelSnapshotFilters.h"
#include "MyCustomFilter.generated.h"

UCLASS()
class UMyCustomFilter : public ULevelSnapshotFilter
{
	GENERATED_BODY()
public:
	// 只包含带有 “Important” 标签的 Actor
	virtual EFilterResult::Type IsActorValid(const FIsActorValidParams& Params) const override
	{
		if (Params.LevelActor && Params.LevelActor->ActorHasTag(FName("Important")))
		{
			return EFilterResult::Include;
		}
		return EFilterResult::Exclude;
	}

	// 对于通过的 Actor，不关心具体属性，全部使用默认规则
	virtual EFilterResult::Type IsPropertyValid(const FIsPropertyValidParams& Params) const override
	{
		return EFilterResult::DoNotCare;
	}
};
```

### 进阶用法

使用 `ULambdaFilter` 可以快速定义过滤逻辑，无需创建新类。

```cpp
// 在某个函数或测试用例中
#include "Builtin/LambdaFilter.h"

void CreateAndApplyLambdaFilter()
{
	// 创建一个 lambda 过滤器，只包含路径包含 “/Game/Environment” 的 Actor
	ULambdaFilter* LambdaFilter = ULambdaFilter::Create(
		// IsActorValid Lambda
		[](const FIsActorValidParams& Params) -> EFilterResult::Type
		{
			if (Params.LevelActor)
			{
				FString ActorPath = Params.LevelActor->GetPathName();
				if (ActorPath.Contains(TEXT("/Game/Environment")))
				{
					return EFilterResult::Include;
				}
			}
			return EFilterResult::Exclude;
		},
		// IsPropertyValid Lambda
		[](const FIsPropertyValidParams& Params) -> EFilterResult::Type
		{
			return EFilterResult::DoNotCare;
		},
		// IsDeletedActorValid Lambda
		[](const FIsDeletedActorValidParams& Params) -> EFilterResult::Type
		{
			return EFilterResult::DoNotCare;
		},
		// IsAddedActorValid Lambda
		[](const FIsAddedActorValidParams& Params) -> EFilterResult::Type
		{
			return EFilterResult::Exclude; // 排除新增的 Actor
		}
	);

	// 假设你已经有了一个 ULevelSnapshot* Snapshot 和应用它的逻辑
	// Snapshot->ApplyToWorld(LambdaFilter);
}
```

## Demo 示例

以下是一个完整的自定义过滤器示例，该过滤器只允许恢复名字中包含 “Light” 且其变换发生变化的 Actor 的变换属性。

```cpp
// LightTransformFilter.h
#pragma once
#include "LevelSnapshotFilters.h"
#include "Builtin/ActorSelector/ActorSelectorFilter.h"
#include "LightTransformFilter.generated.h"

UCLASS()
class ULightTransformFilter : public ULevelSnapshotBlueprintFilter
{
	GENERATED_BODY()

public:
	ULightTransformFilter();

	virtual EFilterResult::Type IsActorValid(const FIsActorValidParams& Params) const override;
	virtual EFilterResult::Type IsPropertyValid(const FIsPropertyValidParams& Params) const override;
};
```

```cpp
// LightTransformFilter.cpp
#include "LightTransformFilter.h"
#include "GameFramework/Actor.h"
#include "Components/SceneComponent.h"

ULightTransformFilter::ULightTransformFilter()
{
}

EFilterResult::Type ULightTransformFilter::IsActorValid(const FIsActorValidParams& Params) const
{
	if (!Params.LevelActor)
	{
		return EFilterResult::Exclude;
	}

	// 1. 检查 Actor 名字是否包含 “Light” (不区分大小写)
	FString ActorName = Params.LevelActor->GetName();
	if (!ActorName.Contains(TEXT("Light"), ESearchCase::IgnoreCase))
	{
		return EFilterResult::Exclude;
	}

	// 2. 检查变换是否发生了变化 (简化：仅比较根组件变换)
	const USceneComponent* SnapRoot = Params.SnapshotActor ? Params.SnapshotActor->GetRootComponent() : nullptr;
	const USceneComponent* LevelRoot = Params.LevelActor->GetRootComponent();
	if (!SnapRoot || !LevelRoot)
	{
		return EFilterResult::Exclude;
	}

	bool bTransformChanged = !SnapRoot->GetRelativeTransform().Equals(LevelRoot->GetRelativeTransform(), 0.01f);
	return bTransformChanged ? EFilterResult::Include : EFilterResult::Exclude;
}

EFilterResult::Type ULightTransformFilter::IsPropertyValid(const FIsPropertyValidParams& Params) const
{
	// 对于符合条件的 Actor，我们只关心变换属性
	// 通过属性路径判断是否是变换相关的属性 (如 bHidden, RelativeLocation 等)
	const FString PropertyName = Params.Property->GetName();
	if (PropertyName == TEXT("RelativeLocation") ||
		PropertyName == TEXT("RelativeRotation") ||
		PropertyName == TEXT("RelativeScale3D"))
	{
		return EFilterResult::Include;
	}
	// 其他属性一概不关心，不恢复
	return EFilterResult::Exclude;
}
```

## 模块依赖

从 `LevelSnapshotFilters.Build.cs` 分析，该模块没有引入不常见的外部依赖。

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine/Slate 等） | |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下双精度常量截断为浮点数产生的警告。 |
| 2026-05-12 | `d6533f70` | Virtual Production: Fixed warning regarding EngineAssetDefinitions plugin not being included when it | 虚拟制片：修复了当 EngineAssetDefinitions 插件未被包含时产生的警告。 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 虚拟制片：将各种虚拟制片资产迁移到不同的资产分类，并将其迁移至新位置。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志输出宏 UE_LOG 迁移至 UE_LOGF。 |
| 2026-04-02 | `5cc4482f` | Add descriptions to trace channels and a few other places. | 为追踪通道和其他几处添加了描述信息。 |

### 维护评价

- **创建时间**：2021 年 2 月，已有约 5 年历史。
- **近期活跃度**：最近一次更新在 2026 年 5 月，包含代码质量修复和资产组织优化，表明插件仍在**维护中**。
- **状态**：虽然 `.uplugin` 标记为 `IsBetaVersion: true` 且 `EnabledByDefault: false`，表明其仍处于测试阶段，但持续的维护记录显示 Epic 对其进行了持续的投入和改进。
- **推荐**：该插件功能明确且强大，是虚拟制片和复杂关卡管理中的重要工具。尽管是 Beta 状态，但鉴于其活跃维护和实际应用场景，**推荐在需要关卡版本控制和选择性恢复功能的项目中使用**。使用者应注意其 Beta 标签，可能在未来的版本中有 API 变动。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LevelSnapshots)
- [官方文档](https://epicgames.com) (来自 .uplugin，但无具体链接)