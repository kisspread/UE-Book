# TEDS: Editor Data Storage Features

> Experimental UI Features for the Editor, built on TEDS: Editor Data Storage.

| 属性 | 值 |
|---|---|
| 中文名 | TEDS 编辑器数据存储功能 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器UI功能） |
| 模块 | `TedsActorCompatibility` (Runtime), `TedsAlerts` (Runtime), `TedsAssetData` (Runtime), `TedsContentBrowser` (Runtime), `TedsDebugger` (Runtime), `TedsEditorCompatibility` (Runtime), `TedsEverythingPicker` (Runtime), `TedsOperations` (Runtime), `TedsOutliner` (Runtime), `TedsPropertyEditor` (Runtime), `TedsQueryStack` (Runtime), `TedsRevisionControl` (Runtime), `TedsSettings` (Runtime), `TedsTableViewer` (Runtime), `TedsTypeInfo` (Runtime), `TedsTypedElementBridge` (Runtime), `UnifiedFavorites` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-07-27 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorDataStorageFeatures) | |

## 用途

该插件是 Epic Games 为 Unreal Engine 编辑器构建的新一代 UI 框架的**实验性实现**。它并非一个独立的、面向最终用户的插件，而是 **TEDS (Editor Data Storage)** 框架之上的一系列 **编辑器功能模块集合**。

其核心目标是利用 TEDS 提供的高性能、数据库驱动的数据存储系统，重新构建传统的编辑器 UI（如大纲视图、属性编辑器、内容浏览器等），以获得更好的性能、灵活性和可扩展性。简单来说，它是 TEDS 框架的“示例应用”和“功能扩展包”。

## 使用场景

- **引擎开发者/扩展开发者**：希望使用 TEDS 数据库模式来构建自定义的编辑器面板、检查器或工具窗口。
- **需要高性能、数据驱动的编辑器界面**：传统的 Slate/Widget 模式在数据量极大时可能存在性能瓶颈，TEDS 架构旨在解决此问题。
- **参与 Unreal Engine 核心开发**：理解或贡献下一代编辑器 UI 基础设施。

## 蓝图用法

该插件的主要功能通过 C++ 的 TEDS 系统集成，蓝图直接交互有限。核心交互点在于 `FTedsTypeInfoModule` 对 TEDS 类型信息集成的控制。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `EnableTedsTypeInfoIntegration` | 启用 TEDS 类型信息集成，开始将 Unreal 类型系统同步到 TEDS 表中 | `FTedsTypeInfoModule` |
| `DisableTedsTypeInfoIntegration` | 禁用 TEDS 类型信息集成 | `FTedsTypeInfoModule` |
| `IsTedsTypeInfoIntegrationEnabled` | 查询 TEDS 类型信息集成是否已启用 | `FTedsTypeInfoModule` |
| `RefreshTypeInfo` | 请求刷新所有已注册的类型信息 | `FTedsTypeInfoModule` |

### 使用示例（蓝图描述）

由于该插件主要面向引擎底层，蓝图用法非常有限。通常在 C++ 模块的 `StartupModule` 或编辑器初始化逻辑中调用 `EnableTedsTypeInfoIntegration()`。在蓝图中，你可能只能通过蓝图函数库调用 `IsTedsTypeInfoIntegrationEnabled` 等查询函数，但无法通过蓝图节点直接构建复杂的 TEDS 查询。

## C++ 用法

本插件的核心用法是通过实现 `UEditorDataStorageFactory` 来向 TEDS 系统注册自定义的表、查询和层次结构。

### 头文件引入

```cpp
#include "TedsTypeInfoModule.h"
#include "Elements/Columns/TedsTypeInfoColumns.h"
```

### 基本用法

以下是一个简化示例，展示如何创建一个 Factory 来注册一个自定义表，并定义其列。此模式是插件中所有模块（如 `TedsOutliner`, `TedsPropertyEditor`）的基础。

（*注：此为基于插件架构推断的典型用法，非特定文件摘录*）

```cpp
// MyCustomTedsFactory.h
#pragma once
#include "Elements/Columns/TedsTypeInfoColumns.h" // 用于演示引用现有列
#include "EditorDataStorageFactory.h"

UCLASS()
class UMyCustomTedsFactory : public UEditorDataStorageFactory
{
	GENERATED_BODY()

public:
	virtual void RegisterTables(UE::Editor::DataStorage::ICoreProvider& DataStorage, UE::Editor::DataStorage::ICompatibilityProvider& Compatibility) override;
	virtual void RegisterQueries(UE::Editor::DataStorage::ICoreProvider& DataStorage) override;
};
```

```cpp
// MyCustomTedsFactory.cpp
#include "MyCustomTedsFactory.h"
#include "Elements/Columns/TedsTypeInfoColumns.h"

void UMyCustomTedsFactory::RegisterTables(ICoreProvider& DataStorage, ICompatibilityProvider& Compatibility)
{
	// 定义一个名为 “MyCustomTable” 的新表，并添加一些列
	DataStorage.CreateTable(
		TEXT("MyCustomTable"),
		{ FDataStorageTypeInfoObjectPathColumn::StaticStruct(), // 复用插件中定义的列
		  FDataStoragePropertyNameColumn::StaticStruct() });
}

void UMyCustomTedsFactory::RegisterQueries(ICoreProvider& DataStorage)
{
	// 注册一个查询，从表中读取数据
	auto QueryBuilder = DataStorage.Query({ FDataStorageTypeInfoObjectPathColumn::StaticStruct() });
	// ... 设置过滤和处理逻辑
}
```

### 进阶用法

**利用类型层次结构**：插件通过 `RegisterHierarchies` 建立了 `ClassHierarchy` 和 `PropertyHierarchy`。你可以编写查询，利用这些层次结构进行父子关系遍历。

```cpp
// 查询所有继承自特定类的类信息
auto ClassQuery = DataStorage.Query<Editor::DataStorage::FTypeInfoObjectPathColumn>(
	[&](const auto& RowView)
	{
		// 检查 Row 是否在 ClassHierarchy 中，且父类是 UMyBaseClass
		const bool bIsChild = DataStorage.GetHierarchy(ClassHierarchyName).IsChildOf(RowView.GetRow(), UMyBaseClass::StaticClass());
		return bIsChild;
	});
```

**监听表更新**：通过 `DataStorage.GetOnTableUpdateCompletedDelegate().AddLambda(...)` 可以监听特定表（如 `Type Information`）的更新完成事件，从而触发依赖此数据的UI刷新。

## Demo 示例

由于此插件是基础设施，一个完整的可运行 Demo 需要集成到编辑器中。以下是一个最小化的 **Factory** 头文件与实现框架，展示了如何开始构建自己的 TEDS 功能。

```cpp
// DemoTedsFeatureFactory.h
#pragma once
#include "EditorDataStorageFactory.h"
#include "DemoTedsFeatureFactory.generated.h"

// 1. 定义一个简单的自定义列
USTRUCT()
struct FDemoFeatureIdColumn : public FEditorDataStorageColumn
{
	GENERATED_BODY()

	UPROPERTY()
	int32 UniqueId = 0;
};

UCLASS()
class UDemoTedsFeatureFactory final : public UEditorDataStorageFactory
{
	GENERATED_BODY()

public:
	//~ Begin UEditorDataStorageFactory interface
	virtual void RegisterTables(ICoreProvider& DataStorage, ICompatibilityProvider& Compatibility) override;
	virtual void RegisterQueries(ICoreProvider& DataStorage) override;
	//~ End UEditorDataStorageFactory interface
};
```

```cpp
// DemoTedsFeatureFactory.cpp
#include "DemoTedsFeatureFactory.h"

void UDemoTedsFeatureFactory::RegisterTables(ICoreProvider& DataStorage, ICompatibilityProvider& Compatibility)
{
	// 创建一个用于演示的表
	static const FName DemoTableName(TEXT("DemoFeatureTable"));
	DataStorage.CreateTable(DemoTableName, { FDemoFeatureIdColumn::StaticStruct() });
}

void UDemoTedsFeatureFactory::RegisterQueries(ICoreProvider& DataStorage)
{
	// 创建一个简单的查询，用于迭代演示表中的所有行
	DataStorage.RegisterQuery(
		TEXT("IterateDemoTable"),
		UE::Editor::DataStorage::Queries::FQueryDescription()
			.ReadOnly({ FDemoFeatureIdColumn::StaticStruct() })
			.SetExecution(UE::Editor::DataStorage::Queries::EExecutionPolicy::GameThread),
		[](const auto& Context)
		{
			// 在此回调中处理每一行数据
			for (const auto& [IdColumn] : Context.GetColumns<FDemoFeatureIdColumn>())
			{
				UE_LOG(LogTemp, Log, TEXT("Demo Row ID: %d"), IdColumn.UniqueId);
			}
		});
}
```

## 模块依赖

该插件的核心模块（如 `TedsTypeInfo`）是 TEDS 生态系统的一部分，其依赖关系主要体现在对 `EditorDataStorage` 核心库的依赖上。

| 模块 | 用途 |
|---|---|
| `EditorDataStorage` | TEDS 核心库，提供数据存储、查询、层次结构等基础功能。本插件所有功能均基于此。 |
| `TypedElementFramework` | 提供类型化元素（Typed Element）的抽象层，`TedsTypedElementBridge` 模块用于桥接两者。 |
| `TypeRegistry` | Unreal 类型系统（UStruct， UClass）的注册表，`TedsTypeInfo` 模块用于从中读取元数据。 |

*（注：由于未提供 Build.cs 文件，此依赖列表基于插件功能推断。实际项目开发中，请查阅相关模块的 Build.cs 文件以获取准确的依赖信息。）*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `c18be83c` | Enable the TEDS Outliner in Restricted UEFN | 在受限 UEFN 环境中启用 TEDS 大纲视图 |
| 2026-05-14 | `bd93e418` | Hide unloaded actor rows inside non-editing level instances from TEDS Outliner | 从 TEDS 大纲中隐藏非编辑关卡实例内的未加载 Actor 行 |
| 2026-05-14 | `bdc9e0ac` | [TedsOutliner] Fix invalid cross-level drag and drops | [TEDS大纲] 修复无效的跨层级拖放操作 |
| 2026-05-14 | `6f329dd1` | [Backout] - CL53940377 | [回滚] - CL53940377 |
| 2026-05-14 | `ee0aab56` | Hide unloaded actor rows inside non-editing level instances from TEDS Outliner | 从 TEDS 大纲中隐藏非编辑关卡实例内的未加载 Actor 行 |

### 维护评价

- **创建时间**：2024年7月创建，年龄约2年。
- **近期更新**：最近一次更新在 2026 年 5 月，包含功能启用（UEFN支持）、Bug 修复（拖放、UI显示）和代码回滚。更新频率表明该插件仍在**积极开发和维护**中。
- **实验性状态**：插件标记为 `IsExperimentalVersion=true`，`EnabledByDefault=false`，是**实验性功能**。这意味着其 API 和行为可能在未来版本中发生重大变更，且未经充分测试，不建议在正式项目中作为核心依赖使用。
- **综合评价**：这是一个面向引擎开发者、用于探索下一代编辑器架构的活跃实验性项目。对于学习 TEDS 框架或参与引擎 UI 开发有价值，但对于生产环境项目，应谨慎评估其稳定性和长期支持计划。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorDataStorageFeatures)
- [官方文档]( ) （暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorDataStorageFeatures/Tests) （需确认是否存在）