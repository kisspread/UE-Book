# Engine Asset Definitions

> （无描述）

| 属性 | 值 |
|---|---|
| 中文名 | 资产定义系统 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `EngineAssetDefinitions` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2022-11-10 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/EngineAssetDefinitions) | |

## 用途

这个插件是 UE5 编辑器资产类型系统的核心基础架构。它旨在**替代旧的 `IAssetTypeActions` 接口**，解决其固有的设计缺陷。

**核心问题**：旧的 `IAssetTypeActions` 将大量功能（显示、颜色、分类、右键菜单动作、双击行为等）集中在一个类中。这导致即使只是在内容浏览器中选择一个资产并右键单击，引擎也可能需要加载所有已注册的资产类型类来构建菜单，严重影响了编辑器性能和启动速度。

**解决方案**：`UAssetDefinition` 系统采用更现代、模块化的 `UObject` 基础设计。每个引擎内置资产类型（如 `StaticMesh`, `Blueprint`, `Material` 等）都对应一个 `UAssetDefinition` 子类。这个插件**包含了引擎所有基础资产类型的定义**。这些定义是轻量级的，只在需要时才被实例化和查询，从而实现了高效的延迟加载和按需加载。它是构建现代化、可扩展的编辑器内容浏览器和资产交互系统的基础。

## 使用场景

- **你是一名引擎或工具程序员**：当你需要为自定义资产类型创建编辑器集成时，你会继承 `UAssetDefinitionDefault` 并重写相关函数，而不是旧的 `IAssetTypeActions`。
- **你在使用或扩展 UE5 编辑器**：你在内容浏览器中看到的每个资产的显示名称、颜色、图标、右键菜单选项、双击行为等，都由对应的 `UAssetDefinition` 类定义。本插件提供了所有内置资产类型的定义。
- **你遇到了内容浏览器性能问题**：理解这个插件的工作原理有助于你诊断和优化资产加载行为，因为它控制着哪些资产信息需要被提前加载。

## 蓝图用法

此插件主要是 **C++ 框架和实现**，为编辑器提供底层的资产类型元数据和行为。它**没有暴露任何公开的、可直接在蓝图中调用的函数（UFUNCTION(BlueprintCallable)）**。

其“使用”方式是间接的：通过在 C++ 中定义新的 `UAssetDefinition` 子类，你的资产类型就能自动集成到编辑器中（内容浏览器、拖放、右键菜单等）。蓝图资产（`UBlueprint`）本身的行为由 `UAssetDefinition_Blueprint` 定义，但这属于引擎内部实现。

## C++ 用法

### 头文件引入

要为你的自定义资产创建定义，你需要包含基类头文件。
```cpp
#include "AssetDefinitionDefault.h"
```

### 基本用法：创建自定义资产的定义

这是此插件最常见的使用模式。假设你有一个 `UMyGameAsset` 类。

**头文件 (MyGameAssetDefinition.h):**
```cpp
// 示例来源: 模仿 Source/Private/AssetDefinition_StaticMesh.h 等多个文件的通用模式
#pragma once
#include "AssetDefinitionDefault.h"
#include "MyGameAssetDefinition.generated.h"

UCLASS()
class UMyGameAssetDefinition : public UAssetDefinitionDefault
{
	GENERATED_BODY()

public:
	// 资产在编辑器中的显示名称
	virtual FText GetAssetDisplayName() const override
	{
		return NSLOCTEXT("MyGame", "AssetTypeActions_MyGameAsset", "My Game Asset");
	}

	// 资产在内容浏览器中的颜色
	virtual FLinearColor GetAssetColor() const override
	{
		return FLinearColor(FColor(128, 255, 0)); // 亮绿色
	}

	// 此定义关联的资产 UObject 类型
	virtual TSoftClassPtr<UObject> GetAssetClass() const override
	{
		return UMyGameAsset::StaticClass();
	}

	// 资产在内容浏览器中所属的分类
	virtual TConstArrayView<FAssetCategoryPath> GetAssetCategories() const override
	{
		static const TArray<FAssetCategoryPath> Categories = {
			FAssetCategoryPath(
				EAssetCategoryPaths::Gameplay,
				NSLOCTEXT("MyGame", "AssetSubMenu", "My Mod"),
				ECategoryMenuType::Section
			)
		};
		return Categories;
	}

	// 定义双击资产时的行为（打开编辑器）
	virtual EAssetCommandResult OpenAssets(const FAssetOpenArgs& OpenArgs) const override
	{
		// 实现打开你的自定义资产编辑器的逻辑
		// 示例: UAssetEditorManager::Get().OpenEditorForAssets(OpenArgs.LoadObjects<UMyGameAsset>());
		return EAssetCommandResult::Handled;
	}
};
```

### 进阶用法：控制资产的导入、重命名和差异比较

你可以在定义中控制更多高级行为，这些都继承自 `UAssetDefinition` 的虚函数。

**源文件 (MyGameAssetDefinition.cpp):**
```cpp
// 示例来源: 模仿 Source/Private/AssetDefinition_DataTable.h, AssetDefinition_DataAsset.h 等
#include "MyGameAssetDefinition.h"
// ... 其他必要的头文件

// 是否支持从文件导入？
bool UMyGameAssetDefinition::CanImport() const
{
	return true; // 如果你的资产支持导入（如 CSV -> DataTable），则返回 true
}

// 资产是否可以被重命名？
FAssetSupportResponse UMyGameAssetDefinition::CanRename(const FAssetData& InAsset) const
{
	// 可以添加自定义逻辑，例如检查资产是否被特定系统引用
	return FAssetSupportResponse::Supported();
}

// 资产是否支持自动合并（用于版本控制）？
bool UMyGameAssetDefinition::CanMerge() const
{
	return true;
}

// 执行资产的合并操作（自动或手动）
EAssetCommandResult UMyGameAssetDefinition::Merge(const FAssetManualMergeArgs& MergeArgs) const
{
	// 实现你的资产合并逻辑
	// 通常，对于数据资产，你需要比较两个版本并生成合并后的资产。
	return EAssetCommandResult::Handled;
}

// 执行资产差异比较
EAssetCommandResult UMyGameAssetDefinition::PerformAssetDiff(const FAssetDiffArgs& DiffArgs) const
{
	// 实现打开差异比较工具的逻辑
	// 示例: FAssetDiff::PerformDiff(DiffArgs.OldAsset, DiffArgs.NewAsset);
	return EAssetCommandResult::Handled;
}
```

## Demo 示例

以下是一个完整的、可编译的自定义资产定义最小示例。

**MySimpleAssetDefinition.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "AssetDefinitionDefault.h"
#include "MySimpleAssetDefinition.generated.h"

UCLASS()
class UMySimpleAssetDefinition : public UAssetDefinitionDefault
{
	GENERATED_BODY()

public:
	virtual FText GetAssetDisplayName() const override;
	virtual FLinearColor GetAssetColor() const override;
	virtual TSoftClassPtr<UObject> GetAssetClass() const override;
	virtual TConstArrayView<FAssetCategoryPath> GetAssetCategories() const override;
};
```

**MySimpleAssetDefinition.cpp**
```cpp
#include "MySimpleAssetDefinition.h"

// 假设你有一个 UObject 子类叫 UMySimpleAsset
// #include "MySimpleAsset.h"

#define LOCTEXT_NAMESPACE "MySimpleAssetDefinition"

FText UMySimpleAssetDefinition::GetAssetDisplayName() const
{
	return LOCTEXT("DisplayName", "Simple Asset");
}

FLinearColor UMySimpleAssetDefinition::GetAssetColor() const
{
	return FLinearColor(FColor::Yellow);
}

TSoftClassPtr<UObject> UMySimpleAssetDefinition::GetAssetClass() const
{
	// 替换为你的实际资产类
	// return UMySimpleAsset::StaticClass();
	return UObject::StaticClass(); // 仅作示例，请替换
}

TConstArrayView<FAssetCategoryPath> UMySimpleAssetDefinition::GetAssetCategories() const
{
	static const TArray<FAssetCategoryPath> Categories = {
		FAssetCategoryPath(EAssetCategoryPaths::Basic)
	};
	return Categories;
}

#undef LOCTEXT_NAMESPACE
```

## 模块依赖

此插件是编辑器核心功能的一部分。要基于它开发，你的模块只需要链接最基本的引擎模块。

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine 等） | 作为 Editor 模块，它依赖于引擎基础。对于继承 `UAssetDefinitionDefault` 来定义新资产类型的模块，通常只需要在其 `.Build.cs` 中依赖 `Engine` 和 `AssetDefinition`（即 `EngineAssetDefinitions` 模块本身）。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `c9ef5202` | Fix early check for derived anim blueprints causing crashes when parent class skeletons were deleted | 修复了一个导致派生动画蓝图在父类骨骼被删除时崩溃的问题。 |
| 2026-05-13 | `f933819f` | EditorUsability : Textures | 改进了纹理资产在编辑器中的易用性。 |
| 2026-05-12 | `4c024ae7` | [Subsurface Profile] Add back the default toolbar for quick save and browse. | 恢复了次表面配置文件的默认工具栏，以便快速保存和浏览。 |
| 2026-04-24 | `12940ee6` | EditorUsability : AssetDefinitions | 改进了资产定义本身的编辑器易用性。 |
| 2026-04-16 | `0b4d09a4` | [ContentBrowser] New Add Menu Data Menu | 内容浏览器新增“添加菜单”数据菜单。 |

### 维护评价

- **状态**：**活跃维护中**。
- **分析**：该插件于 2022 年底创建，是 UE5 资产系统现代化的关键一环。从提交记录看，Epic 工程师仍在持续改进它，最近的更新（2026年5月）集中在修复动画蓝图相关的问题，并优化编辑器易用性。作为编辑器基础设施，它随着每个引擎版本更新而演进。
- **推荐**：**强烈推荐使用**。对于任何需要创建自定义资产类型并深度集成到 UE5 编辑器的开发者来说，理解并使用此插件提供的 `UAssetDefinition` 框架是**唯一正确且官方的方式**。旧的 `IAssetTypeActions` 应被视为已废弃。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/EngineAssetDefinitions)
- [官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/) (未找到专属页面，相关信息在引擎源码和社区讨论中)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests) (搜索 `AssetDefinition` 相关测试文件)