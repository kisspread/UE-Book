# Engine Asset Definitions

> 为引擎内置资产类型提供编辑器定义，统一管理其在编辑器中的显示、交互和版本控制行为。

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `EngineAssetDefinitions` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2022-11-09 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/EngineAssetDefinitions) | |

## 用途

该插件是 Unreal Engine 资产定义系统 (`UAssetDefinition`) 的核心实现之一。它为引擎内置的多种基础资产类型（如 `UWorld`、`UBlueprint`、`UDataTable`、`UDataAsset` 等）提供了具体的编辑器定义。

这些定义决定了资产在内容浏览器中的**显示名称**、**颜色**、**缩略图**、**所属分类**，以及用户双击或右键时的**默认行为**（如打开编辑器、执行差异比较、合并等）。它解决了“引擎内置资产在编辑器中如何表现”这一基础问题，是编辑器能够正确识别和操作这些资产的关键。

## 使用场景

- 你希望了解或自定义引擎内置资产（如关卡、蓝图、数据表）在编辑器中的外观和交互方式。
- 你需要为自定义资产类型创建定义，并参考引擎内置资产的实现作为模板。
- 你在进行版本控制（如 Perforce、Git）时，需要对蓝图、数据表等资产进行差异比较或合并，该插件提供了这些操作的底层支持。

## 蓝图用法

此插件主要为编辑器扩展，不提供公开的蓝图节点。其功能通过编辑器界面（如内容浏览器、资产编辑器）和 C++ API 暴露。

## C++ 用法

该插件的核心是继承 `UAssetDefinitionDefault` 并重写其虚函数，以定义特定资产类型的行为。

### 头文件引入

```cpp
#include "AssetDefinitionDefault.h"
// 对于特定资产类型，可能需要包含其对应的头文件，如：
#include "Engine/World.h"
#include "Engine/Blueprint.h"
```

### 基本用法：创建自定义资产定义

以下示例展示了如何为一个自定义资产类型 `UMyAsset` 创建定义，模仿 `UAssetDefinition_DataAsset` 的结构。

```cpp
// MyAssetDefinition.h
#pragma once

#include "AssetDefinitionDefault.h"
#include "MyAsset.h" // 你的自定义资产头文件

#include "MyAssetDefinition.generated.h"

UCLASS(MinimalAPI)
class UMyAssetDefinition : public UAssetDefinitionDefault
{
	GENERATED_BODY()

public:
	// 设置此定义始终包含在资产过滤器中
	UMyAssetDefinition()
	{
		IncludeClassInFilter = EIncludeClassInFilter::Always;
	}

	// 在内容浏览器中显示的名称
	virtual FText GetAssetDisplayName() const override
	{
		return NSLOCTEXT("MyAsset", "DisplayName", "My Custom Asset");
	}

	// 内容浏览器中资产的颜色标识
	virtual FLinearColor GetAssetColor() const override
	{
		return FLinearColor(FColor(100, 200, 50)); // 自定义颜色
	}

	// 此定义关联的资产类
	virtual TSoftClassPtr<UObject> GetAssetClass() const override
	{
		return UMyAsset::StaticClass();
	}

	// 双击资产时的默认行为：打开资产编辑器
	virtual EAssetCommandResult OpenAssets(const FAssetOpenArgs& OpenArgs) const override
	{
		// 此处应实现打开自定义资产编辑器的逻辑
		// 通常使用 FAssetEditorManager 或创建自定义编辑器
		return EAssetCommandResult::Handled;
	}
};
```
*来源：参考 `Engine/Plugins/Editor/EngineAssetDefinitions/Source/Public/AssetDefinition_DataAsset.h`*

### 进阶用法：支持差异比较与合并

`UAssetDefinition_Blueprint` 和 `UAssetDefinition_DataAsset` 展示了如何为资产启用版本控制功能。

```cpp
// 在你的资产定义类中重写以下函数
virtual bool CanMerge() const override { return true; } // 声明支持合并

// 实现自动合并（通常用于解决简单冲突）
virtual EAssetCommandResult Merge(const FAssetAutomaticMergeArgs& MergeArgs) const override
{
	// 调用资产合并工具或自定义合并逻辑
	// 可参考 FBlueprintMerger 或 FDataTableMerger 的实现
	return EAssetCommandResult::Handled;
}

// 实现手动合并（打开合并工具界面）
virtual EAssetCommandResult Merge(const FAssetManualMergeArgs& MergeArgs) const override
{
	// 打开合并编辑器
	return EAssetCommandResult::Handled;
}

// 实现差异比较
virtual EAssetCommandResult PerformAssetDiff(const FAssetDiffArgs& DiffArgs) const override
{
	// 调用差异比较工具，如 FBlueprintDiff、FDataTableDiff
	return EAssetCommandResult::Handled;
}
```
*来源：参考 `Engine/Plugins/Editor/EngineAssetDefinitions/Source/Public/AssetDefinition_Blueprint.h` 和 `AssetDefinition_DataAsset.h`*

## Demo 示例

以下是一个完整的、可编译的最小示例，为自定义资产 `UMyItemData` 创建编辑器定义。

**MyItemData.h**
```cpp
#pragma once

#include "Engine/DataAsset.h"
#include "MyItemData.generated.h"

UCLASS(BlueprintType)
class UMyItemData : public UDataAsset
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, BlueprintReadOnly)
	FString ItemName;

	UPROPERTY(EditAnywhere, BlueprintReadOnly)
	int32 ItemID;
};
```

**AssetDefinition_MyItemData.h**
```cpp
#pragma once

#include "AssetDefinitionDefault.h"
#include "MyItemData.h"

#include "AssetDefinition_MyItemData.generated.h"

UCLASS(MinimalAPI)
class UAssetDefinition_MyItemData : public UAssetDefinitionDefault
{
	GENERATED_BODY()

public:
	UMyItemData()
	{
		IncludeClassInFilter = EIncludeClassInFilter::Always;
	}

	virtual FText GetAssetDisplayName() const override
	{
		return NSLOCTEXT("MyItemData", "DisplayName", "Item Data");
	}

	virtual FLinearColor GetAssetColor() const override
	{
		return FLinearColor(FColor(255, 165, 0)); // 橙色
	}

	virtual TSoftClassPtr<UObject> GetAssetClass() const override
	{
		return UMyItemData::StaticClass();
	}

	// 使用默认的资产编辑器打开
	virtual EAssetCommandResult OpenAssets(const FAssetOpenArgs& OpenArgs) const override
	{
		// 默认行为会打开属性编辑器，对于简单的 DataAsset 通常足够
		return Super::OpenAssets(OpenArgs);
	}
};
```

## 模块依赖

此插件为编辑器插件，其依赖主要为编辑器和资产系统模块。

| 模块 | 用途 |
|---|---|
| `AssetDefinition` | 提供 `UAssetDefinitionDefault` 基类和资产定义框架 |
| `AssetTools` | 提供资产操作工具，如差异比较、合并的接口 |
| `UnrealEd` | 提供编辑器核心功能，如资产编辑器管理、缩略图渲染 |
| `Merge` | 提供蓝图、数据表等资产的合并工具实现 |
| `Diff` | 提供资产差异比较工具实现 |

## 维护状态

### 近期更新

```
- 107f4ba7df54 Static Mesh LOD:  add clamping by MAX_STATIC_MESH_LODS in a few places where static meshes are modified, where it wasn't present.  Goal is to close off all code pathways that could allow content to be created that exceeds the LOD count, leading to runtime asserts.
- 429081a6c5bd Add a basic diff tool for Materail and Material Instance assets
- 4ef2ce388522 Transform Provider Data Refactor - Remove hardcoding of anim banks, transform provider ID, lack of plugin extensibility, and fixed numerous order of operation issues with registering providers.
- d46feb4ad0c8 Ensure override editors can open multiple assets
- 1ebddd4628f5 Add a modular feature that physics assets will query when opening allowing for a decoupled bypass feature where a plugin can implement a new editor paradigm for physics assets.
```

**解读**：
- `107f4ba7df54`: 修复了静态网格体 LOD 数量可能超出限制的问题，属于底层稳定性修复。
- `429081a6c5bd`: 为材质和材质实例资产添加了基础的差异比较工具，是功能增强。
- `4ef2ce388522`: 对动画相关的 Transform Provider 进行了重构，提升了插件扩展性。
- `d46feb4ad0c8` 和 `1ebddd4628f5`: 改进了资产编辑器的打开逻辑和物理资产编辑器的扩展性。

### 维护评价

**活跃维护**。该插件创建于 2022 年底，年龄较新。从最近的提交记录看，更新频繁且内容多样，包括功能增强（新增差异工具）、架构改进（重构）和稳定性修复。作为引擎核心编辑器功能的一部分，它受到 Epic Games 的持续关注和维护，是**推荐使用**的基础插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/EngineAssetDefinitions)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Tests/Editor/AssetDefinitionTests) (推测路径，通常在 Engine/Tests 下)