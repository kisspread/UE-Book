# TEDS: Editor Data Storage Features (TedsEditorCompatibility)

> Experimental UI Features for the Editor, built on TEDS: Editor Data Storage.

| 属性 | 值 |
|---|---|
| 中文名 | TEDS 编辑器兼容特性 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `TedsActorCompatibility` (Runtime), `TedsAlerts` (Runtime), `TedsAssetData` (Runtime), `TedsContentBrowser` (Runtime), `TedsDebugger` (Runtime), `TedsEditorCompatibility` (Runtime), `TedsEverythingPicker` (Runtime), `TedsOperations` (Runtime), `TedsOutliner` (Runtime), `TedsPropertyEditor` (Runtime), `TedsQueryStack` (Runtime), `TedsRevisionControl` (Runtime), `TedsSettings` (Runtime), `TedsTableViewer` (Runtime), `TedsTypeInfo` (Runtime), `TedsTypedElementBridge` (Runtime), `UnifiedFavorites` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-07-27 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorDataStorageFeatures) | |

## 用途

EditorDataStorageFeatures 是一个实验性插件，其核心目的是**为 TEDS (Editor Data Storage) 系统构建编辑器 (Editor) UI 功能**。TEDS 是一个基于 ECS (Entity Component System) 的数据存储系统，旨在优化编辑器处理大量数据的性能。本插件（特别是 `TedsEditorCompatibility` 模块）提供了一组**兼容性适配器**，将 Unreal 传统编辑器对象（如 `UWorld`, `ULevel`, `AActor`, 以及 World Partition Actor Descriptors）的数据和状态映射到 TEDS 的表和查询中。这使得 TEDS 驱动的新编辑器 UI（如重写的大纲视图 Outliner）能够无缝地与现有的、未迁移至 TEDS 的编辑器系统进行交互和显示。

## 使用场景

-   **开发新版 TEDS Outliner**：`TedsOutliner` 模块依赖 `TedsEditorCompatibility` 提供的世界、关卡和 Actor 描述数据。
-   **在 TEDS 驱动的 UI 中显示未加载的 Actor**：通过 `FEditorDataStorageActorDescTag` 标记行，并利用 `FEditorDataStorageWorldPartitionHandleColumn` 访问其 World Partition 信息。
-   **同步 World Partition Actor 的 Pin 状态**：`FWorldPartitionPinnedColumn` 允许 TEDS 查询监听并反映 World Partition 中 Actor 的 Pin/Unpin 操作。
-   **构建与传统编辑器资产兼容的 TEDS UI**：`FolderCompatibilityWidgetFactory` 等工厂类使得 TEDS 可以使用兼容的方式渲染文件夹等 UI 元素。

## 蓝图用法

此插件主要为 C++ 模块，旨在为 TEDS 编辑器功能提供底层数据支持。其公开 API 主要面向 TEDS 查询和列系统，而非直接供蓝图使用。蓝图开发者通常通过使用由这些底层数据支持的 **TEDS UI 组件**（如未来可能推出的 TEDS Outliner 蓝图控件）来间接使用其功能。

### 核心数据列与标签

以下结构体是 `TedsEditorCompatibility` 模块公开的核心数据定义，可在 TEDS 查询中作为组件使用。

| 组件 | 说明 | 所在头文件 |
|---|---|---|
| `FEditorDataStorageActorDescTag` | 标记一个行为“未加载的 Actor”（来自 Actor Descriptor）。 | `Public/ActorDesc/TedsActorDescColumns.h` |
| `FEditorDataStorageWorldPartitionHandleColumn` | 包含该行对应 Actor Descriptor 在 World Partition 中的句柄 (`FWorldPartitionHandle`)。 | `Public/ActorDesc/TedsActorDescColumns.h` |
| `FEditorDataStorageWorldPartitionPinnedColumn` | 存储该行对应 Actor 在 World Partition 中的 Pin 状态 (`bool bIsPinned`)。 | `Public/ActorDesc/TedsActorDescColumns.h` |

## C++ 用法

### 头文件引入

```cpp
#include "TedsEditorCompatibility/Public/ActorDesc/TedsActorDescColumns.h"
#include "TedsEditorCompatibility/Public/ActorDesc/TedsActorDescUtils.h"
#include "TedsEditorCompatibility/Public/Factories/TedsEditorHierarchyFactory.h"
```

### 基本用法

本模块的核心用法是实现 `UEditorDataStorageFactory` 的子类来注册数据、表和查询，将编辑器对象适配到 TEDS 中。

**注册一个自定义的兼容性工厂**
(基于 `TedsWorldFactory.h` 和 `TedsActorDescFactory.h` 的模式)

```cpp
// MyTedsCompatibilityFactory.h
#pragma once

#include "EditorDataStorageFactory.h"
#include "MyTedsCompatibilityFactory.generated.h"

UCLASS()
class UMyTedsCompatibilityFactory : public UEditorDataStorageFactory
{
	GENERATED_BODY()

public:
	// 注册自定义的表（用于存储特定数据）
	virtual void RegisterTables(UE::Editor::DataStorage::ICoreProvider& DataStorage) override;

	// 注册查询（用于同步、处理或响应数据变化）
	virtual void RegisterQueries(UE::Editor::DataStorage::ICoreProvider& DataStorage) override;

	// 注册前的初始化（如监听世界事件）
	virtual void PreRegister(UE::Editor::DataStorage::ICoreProvider& DataStorage) override;

	// 关闭前的清理（如移除监听器）
	virtual void PreShutdown(UE::Editor::DataStorage::ICoreProvider& DataStorage) override;

private:
	// 示例：处理新世界创建的回调
	void OnWorldCreated(UWorld* InWorld);

	// 存储兼容性接口指针，用于更复杂的 TEDS 操作
	UE::Editor::DataStorage::ICompatibilityProvider* DataStorageCompat = nullptr;
};
```

### 进阶用法：查询与数据同步

以下伪代码展示了 `UActorWorldPartitionPinnedDataStorageFactory` 如何注册查询，以保持 TEDS 中的 Pin 状态与 World Partition 同步。

```cpp
void UActorWorldPartitionPinnedDataStorageFactory::RegisterQueries(UE::Editor::DataStorage::ICoreProvider& DataStorage)
{
	// 查询1：给支持Pin且没有Pin列的Actor行，添加Pin列。
	DataStorage.RegisterQuery(
		// 查询条件
		Select(
			// 需要的数据
			TEXT("Add Pinned Column"),
			// 操作：为符合条件的行添加 FWorldPartitionPinnedColumn
			... // 具体查询定义
		)
	).Name = TEXT("Add Pinned Column");

	// 查询2：将World Partition的真实Pin状态同步到TEDS列。
	DataStorage.RegisterQuery(
		// 查询条件：监听带有Pin列且需要从世界同步的行
		Select(
			TEXT("Sync World Pin to Column"),
			// 操作：读取World Partition状态，更新列值
			... // 具体查询定义
		)
	).Name = TEXT("Sync Pin To Column");

	// 查询3：当TEDS列值改变（且有同步标记）时，将状态写回World Partition。
	DataStorage.RegisterQuery(
		// 查询条件：监听Pin列值变化，并带有同步标记
		Select(
			TEXT("Sync Column Pin to World"),
			// 操作：调用World Partition的Pin/Unpin API
			... // 具体查询定义
		)
	).Name = TEXT("Sync Pin To World");
}
```

## Demo 示例

**实现一个简单的 TEDS 世界工厂，用于跟踪所有 UWorld 实例。**

```cpp
// SimpleWorldFactory.h
#pragma once

#include "EditorDataStorageFactory.h"
#include "SimpleWorldFactory.generated.h"

UCLASS()
class USimpleWorldFactory : public UEditorDataStorageFactory
{
	GENERATED_BODY()

public:
	virtual void PreRegister(UE::Editor::DataStorage::ICoreProvider& DataStorage) override;
	virtual void RegisterTables(UE::Editor::DataStorage::ICoreProvider& DataStorage) override;
	virtual void PreShutdown(UE::Editor::DataStorage::ICoreProvider& DataStorage) override;

private:
	void OnPostWorldInitialization(UWorld* World, const UWorld::InitializationValues IVS);
	void OnPreWorldFinishDestroy(UWorld* World);

	UE::Editor::DataStorage::ICompatibilityProvider* DataStorage = nullptr;
};
```

```cpp
// SimpleWorldFactory.cpp
#include "SimpleWorldFactory.h"

// 定义一个简单的列，用于存储UWorld指针
USTRUCT()
struct FWorldPointerColumn : public FEditorDataStorageColumn
{
	GENERATED_BODY()
	TWeakObjectPtr<UWorld> World;
};

void USimpleWorldFactory::PreRegister(UE::Editor::DataStorage::ICoreProvider& InDataStorage)
{
	DataStorage = InDataStorage.GetCompatibilityProvider();
	// 监听世界创建和销毁事件
	UWorld::OnWorldInitialized.AddUObject(this, &USimpleWorldFactory::OnPostWorldInitialization);
	UWorld::OnPreWorldFinishDestroy.AddUObject(this, &USimpleWorldFactory::OnPreWorldFinishDestroy);
}

void USimpleWorldFactory::RegisterTables(UE::Editor::DataStorage::ICoreProvider& InDataStorage)
{
	// 创建一个名为“SimpleWorlds”的表来存储世界信息
	InDataStorage.RegisterTable<FWorldPointerColumn>(TEXT("SimpleWorlds"));
}

void USimpleWorldFactory::PreShutdown(UE::Editor::DataStorage::ICoreProvider& InDataStorage)
{
	// 移除监听器
	UWorld::OnWorldInitialized.RemoveAll(this);
	UWorld::OnPreWorldFinishDestroy.RemoveAll(this);
}

void USimpleWorldFactory::OnPostWorldInitialization(UWorld* World, const UWorld::InitializationValues IVS)
{
	if (DataStorage && World)
	{
		// 向TEDS表中添加一行，并写入世界指针
		UE::Editor::DataStorage::RowHandle Row = DataStorage->FindOrCreateRow(FStorageTableIdentifier(TEXT("SimpleWorlds")), World->GetFName());
		FWorldPointerColumn* Column = DataStorage->GetColumn<FWorldPointerColumn>(Row);
		if (Column)
		{
			Column->World = World;
		}
	}
}

void USimpleWorldFactory::OnPreWorldFinishDestroy(UWorld* World)
{
	if (DataStorage && World)
	{
		// 从TEDS表中移除对应行
		UE::Editor::DataStorage::RowHandle Row = DataStorage->FindRow(FStorageTableIdentifier(TEXT("SimpleWorlds")), World->GetFName());
		if (Row != UE::Editor::DataStorage::InvalidRowHandle)
		{
			// ... 移除行的逻辑
		}
	}
}
```

## 模块依赖

此插件（`TedsEditorCompatibility` 模块）的依赖非常集中，主要依赖于 TEDS 核心系统。

| 模块 | 用途 |
|---|---|
| `EditorDataStorage` | TEDS 的核心提供者接口（`ICoreProvider`, `ICompatibilityProvider`）。 |
| `UnrealEd` | 用于集成编辑器功能（如 Factory 模式）。 |
| `Engine` | 访问 `UWorld`, `AActor` 等基础类型。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `c18be83c` | Enable the TEDS Outliner in Restricted UEFN | 在受限 UEFN 环境中启用 TEDS 大纲视图 |
| 2026-05-14 | `bd93e418` | Hide unloaded actor rows inside non-editing level instances from TEDS Outliner | 在非编辑关卡实例中隐藏已卸载的 Actor 行 |
| 2026-05-14 | `bdc9e0ac` | [TedsOutliner] Fix invalid cross-level drag and drops | [Teds大纲] 修复跨关卡拖放的无效问题 |
| 2026-05-14 | `6f329dd1` | [Backout] - CL53940377 | [回退] - CL53940377 |
| 2026-05-14 | `ee0aab56` | Hide unloaded actor rows inside non-editing level instances from TEDS Outliner | 在非编辑关卡实例中隐藏已卸载的 Actor 行 |

### 维护评价

- **创建时间**：2024年7月，属于较新的实验性功能。
- **维护状态**：**活跃维护中**。从提交历史看，在2026年5月仍有频繁的功能提交和修复，表明该项目处于积极开发阶段，特别是围绕 TEDS Outliner 的集成和优化。
- **是否推荐使用**：对于**编辑器功能开发和研究**，特别是与 TEDS 系统集成相关的工作，**强烈推荐关注和学习**。但由于其 **`IsExperimentalVersion = true`** 且 `EnabledByDefault = false`，不建议在需要稳定性的生产环境项目中直接依赖。API 可能发生重大变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorDataStorageFeatures)
- 官方文档：无（实验性插件）
- [测试用例]：插件内部未发现明显的测试文件。相关测试可能位于 `Engine/Tests/` 目录或依赖模块中。