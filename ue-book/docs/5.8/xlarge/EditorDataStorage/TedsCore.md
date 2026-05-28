# TEDS: Editor Data Storage

> A central extendable data storage for editors and their corresponding data with support for viewing and editing through a collection of widgets.

| 属性 | 值 |
|---|---|
| 中文名 | 编辑器数据存储 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（设置资产、蓝图资产） |
| 模块 | `TedsCore` (UncookedOnly), `TedsUI` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-07-27 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorDataStorage) | |

## 用途

TEDS（Typed Element Data Storage 的缩写）是 UE5 编辑器的**中心化 ECS 数据存储引擎**，构建于 Mass Entity 框架之上。它解决了以下核心问题：

1. **编辑器数据碎片化**：传统编辑器中，各类数据（资产信息、选择状态、UI 属性等）分散在不同子系统中。TEDS 将它们统一存储在列式数据库（Columnar Store）中，每一行代表一个"可寻址的编辑器元素"，每一列代表该元素的一个属性。

2. **高性能批量查询与处理**：基于 Mass 的 Chunk 架构，TEDS 支持对海量编辑器数据进行缓存友好的批量遍历和条件筛选，适合 Outliner、Details 面板等需要处理大量节点的场景。

3. **UObject 兼容性**：通过 `UEditorDataStorageCompatibility` 自动将场景中的 UObject（Actor、Component 等）映射到 TEDS 行，支持属性变更监听、对象重建（Reinstancing）恢复和 Undo/Redo Memento。

4. **可扩展的 UI 小部件系统**：`TedsUI` 模块提供基于 Purpose 的小部件工厂注册机制，能根据数据类型自动匹配和构造 UI 控件（如属性编辑器、表格列渲染器等）。

5. **层次结构与关系建模**：内建层次关系（Hierarchy）和通用关系（Relation）系统，支持父子遍历、祖先/后代查询、区间编码快速判断等功能，适用于场景层级、资产引用链等场景。

简单来说：**TEDS 是编辑器的"统一数据库"，让不同编辑器面板能高效共享、查询和编辑同一份结构化数据。**

## 使用场景

- **你需要构建一个高性能的编辑器面板**，需要查询数万个节点的状态（如自定义 Outliner、资产浏览器）→ 用 TEDS 查询系统批量筛选行
- **你想让自定义编辑器面板自动展示 UObject 属性**→ 用 TedsUI 的 Purpose + WidgetFactory 注册机制
- **你需要在编辑器中维护自定义的父子层级关系**（如任务列表、依赖图）→ 用 TEDS 的 Hierarchy/Relation 系统
- **你需要对编辑器数据做增量更新和变更通知**→ 用 TEDS 的 Query Observer 和 Change Column 机制
- **你在为 Chaos Visual Debugger 等工具构建内部数据管道**→ TEDS 的 SupportedPrograms 已包含 ChaosVisualDebugger

## 蓝图用法

TEDS 本身主要面向 C++ 开发者（UncookedOnly / Editor 模块），不直接暴露蓝图节点。编辑器 UI 端通过 Slate Widget 间接使用。以下是面向 C++ 开发者的关键接口分类：

### 核心接口

TEDS 通过三个 Provider 接口暴露功能：

| 接口 | 所在类 | 用途 |
|---|---|---|
| `ICoreProvider` | 接口（由 `UEditorDataStorage` 实现） | 行/列增删、查询、层次结构、关系、作用域等核心操作 |
| `ICompatibilityProvider` | 接口（由 `UEditorDataStorageCompatibility` 实现） | UObject 自动注册/反注册、兼容层 |
| `IUiProvider` | 接口（由 `UEditorDataStorageUi` 实现） | 小部件目的注册、小部件工厂、属性搜索/排序器注册 |

### 数据操作节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ReserveRow()` | 预留一个行句柄，稍后绑定到表 | `UEditorDataStorage` |
| `AddRow(Table, Callback)` | 向指定表添加新行 | `UEditorDataStorage` |
| `RemoveRow(Row)` | 删除指定行 | `UEditorDataStorage` |
| `AddColumn(Row, ColumnType)` | 给行添加列 | `UEditorDataStorage` |
| `RemoveColumn(Row, ColumnType)` | 从行移除列 | `UEditorDataStorage` |
| `GetColumnData(Row, ColumnType)` | 获取列数据指针 | `UEditorDataStorage` |
| `HasColumns(Row, Columns)` | 检查行是否包含指定列 | `UEditorDataStorage` |

### 查询操作节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RegisterQuery(QueryDescription)` | 注册一个查询，返回 QueryHandle | `UEditorDataStorage` |
| `UnregisterQuery(QueryHandle)` | 注销查询 | `UEditorDataStorage` |
| `RunQuery(QueryHandle)` | 执行查询 | `UEditorDataStorage` |
| `RunQuery(QueryHandle, Callback)` | 执行查询并传入回调 | `UEditorDataStorage` |
| `ActivateQueries(ActivationName)` | 激活一次性查询 | `UEditorDataStorage` |

### 关系操作节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RegisterRelationType(Params)` | 注册关系类型 | `UEditorDataStorage` |
| `CreateRelation(Type, Subject, Object)` | 创建关系实例 | `UEditorDataStorage` |
| `DestroyRelation(Type, Subject, Object)` | 销毁关系实例 | `UEditorDataStorage` |
| `IsDescendantOf(Type, Descendant, Ancestor)` | 判断是否为后代 | `UEditorDataStorage` |
| `GetHierarchyRoot(Type, Row)` | 获取层次根节点 | `UEditorDataStorage` |
| `TraverseDescendants(Type, Row, Callback)` | 遍历所有后代 | `UEditorDataStorage` |

### 层次结构节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RegisterHierarchy(Params)` | 注册层次结构类型 | `UEditorDataStorage` |
| `SetParentRow(Handle, Target, Parent)` | 设置父子关系 | `UEditorDataStorage` |
| `GetParentRow(Handle, Target)` | 获取父行 | `UEditorDataStorage` |
| `WalkDepthFirst(Handle, Row, Callback)` | 深度优先遍历 | `UEditorDataStorage` |

### UI 小部件节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RegisterWidgetPurpose(PurposeID, PurposeInfo)` | 注册小部件用途 | `UEditorDataStorageUi` |
| `RegisterWidgetFactory(PurposeRow, Constructor)` | 注册小部件工厂 | `UEditorDataStorageUi` |
| `ConstructWidgets(PurposeRow, Arguments, Callback)` | 构造匹配的小部件 | `UEditorDataStorageUi` |
| `RegisterSearcherGeneratorForProperty(PropertyType, Callback)` | 注册属性搜索器 | `UEditorDataStorageUi` |
| `RegisterSorterGeneratorForProperty(PropertyType, Callback)` | 注册属性排序器 | `UEditorDataStorageUi` |

## C++ 用法

### 头文件引入

```cpp
// 核心数据存储接口
#include "Elements/Interfaces/TypedElementDataStorageInterface.h"

// 查询构建器
#include "Elements/Framework/TypedElementQueryBuilder.h"

// 兼容层接口（UObject 注册）
#include "Elements/Interfaces/TypedElementDataStorageCompatibilityInterface.h"

// UI 提供者接口
#include "Elements/Interfaces/TypedElementUiProviderInterface.h"

// Memento 系统（Undo/Redo）
#include "Memento/TypedElementMementoTranslators.h"
```

### 基本用法：行与列操作

```cpp
// 获取 TEDS 核心提供者
UE::Editor::DataStorage::ICoreProvider* Storage = UE::Editor::DataStorage::GetMutableStorage();
if (!Storage) return;

// 预留行
UE::Editor::DataStorage::RowHandle ReservedRow = Storage->ReserveRow();

// 将预留行添加到指定表
// 表事先通过 RegisterTable 注册，包含所需的列类型
Storage->AddRow(ReservedRow, MyTableHandle,
    UE::Editor::DataStorage::RowCreationCallbackRef([](UE::Editor::DataStorage::RowHandle Row)
    {
        // 行创建后的初始化回调
    }));

// 添加列
Storage->AddColumn(ReservedRow, FMyDataColumn::StaticStruct());

// 获取列数据指针（可写）
FMyDataColumn* DataPtr = reinterpret_cast<FMyDataColumn*>(
    Storage->GetColumnData(ReservedRow, FMyDataColumn::StaticStruct()));

// 检查行是否包含某些列
if (Storage->HasColumns(ReservedRow, {FMyDataColumn::StaticStruct(), FMyTagColumn::StaticStruct()}))
{
    // 行同时包含数据列和标签
}

// 删除列
Storage->RemoveColumn(ReservedRow, FMyDataColumn::StaticStruct());

// 删除行
Storage->RemoveRow(ReservedRow);
```

### 基本用法：查询系统

```cpp
// 定义查询：查找同时拥有 FMyDataColumn 和 FMyTagColumn 的所有行
UE::Editor::DataStorage::FQueryDescription QueryDesc = 
    UE::Editor::DataStorage::Queries::Select()
        .ReadWrite<FMyDataColumn>()
        .ConstChecked<FMyTagColumn>()
        .Compile();

// 注册查询
UE::Editor::DataStorage::QueryHandle QueryHandle = Storage->RegisterQuery(MoveTemp(QueryDesc));

// 执行查询（直接回调模式）
Storage->RunQuery(QueryHandle,
    UE::Editor::DataStorage::EDirectQueryExecutionFlags::None,
    [](UE::Editor::DataStorage::IDirectQueryContext& Context)
    {
        // 获取当前批次行
        FRowHandleArrayView Rows = Context.GetBatchRows();
        for (UE::Editor::DataStorage::RowHandle Row : Rows)
        {
            FMyDataColumn* Data = Context.GetMutableColumn<FMyDataColumn>(Row);
            // 处理数据...
        }
    });

// 注销查询
Storage->UnregisterQuery(QueryHandle);
```

### 基本用法：UObject 兼容层

```cpp
// 获取兼容层
UE::Editor::DataStorage::ICompatibilityProvider* CompatStorage = 
    UE::Editor::DataStorage::GetMutableCompatibilityStorage();

// 将 UObject 显式注册到 TEDS
UObject* MyObject = GetSomeObject();
UE::Editor::DataStorage::RowHandle ObjectRow = CompatStorage->AddCompatibleObjectExplicit(MyObject);

// 查找 UObject 对应的行
UE::Editor::DataStorage::RowHandle FoundRow = CompatStorage->FindRowWithCompatibleObjectExplicit(MyObject);

// 移除 UObject
CompatStorage->RemoveCompatibleObjectExplicit(MyObject);
```

### 进阶用法：注册表并添加外键

```cpp
// 定义列类型
USTRUCT()
struct FAssetPathColumn : public UE::Editor::DataStorage::FEditorDataStorageColumn
{
    GENERATED_BODY()
    UPROPERTY() FString AssetPath;
};

USTRUCT()
struct FSelectedTag : public UE::Editor::DataStorage::FEditorDataStorageTag
{
    GENERATED_BODY()
};

// 在 Factory 中注册表
class UMyDataStorageFactory : public UEditorDataStorageFactory
{
    GENERATED_BODY()
public:
    virtual void RegisterTables(UE::Editor::DataStorage::ICoreProvider& Storage) override
    {
        Storage.RegisterTable(
            {FAssetPathColumn::StaticStruct(), FSelectedTag::StaticStruct()},
            TEXT("MyCustomTable"));
    }
    
    virtual void RegisterQueries(UE::Editor::DataStorage::ICoreProvider& Storage) override
    {
        // 注册周期性查询（自动在 TickGroup 中执行）
        auto QueryDesc = UE::Editor::DataStorage::Queries::Select()
            .ReadWrite<FAssetPathColumn>()
            .FilterOn<FSelectedTag>()
            .Compile();
        
        Storage.RegisterQuery(MoveTemp(QueryDesc));
    }
};
```

### 进阶用法：关系系统

```cpp
// 注册关系类型
UE::Editor::DataStorage::FRelationRegistrationParams RelationParams;
RelationParams.Name = TEXT("AssetDependency");
RelationParams.bHierarchical = true;
RelationParams.InitialGap = 1000; // 区间编码初始间距

UE::Editor::DataStorage::RelationTypeHandle RelationType = 
    Storage->RegisterRelationType(RelationParams);

// 创建关系
UE::Editor::DataStorage::RowHandle SubjectRow = /* ... */;
UE::Editor::DataStorage::RowHandle ObjectRow = /* ... */;
Storage->CreateRelation(RelationType, SubjectRow, ObjectRow);

// 查询层次关系
bool bIsDesc = Storage->IsDescendantOf(RelationType, SomeRow, PotentialAncestor);
UE::Editor::DataStorage::RowHandle Root = Storage->GetHierarchyRoot(RelationType, SomeRow);
int32 Depth = Storage->GetHierarchyDepth(RelationType, SomeRow);

// 遍历所有后代
Storage->TraverseDescendants(RelationType, StartRow,
    [&](UE::Editor::DataStorage::RowHandle Descendant, int32 CurrentDepth)
    {
        // 处理每个后代
    });
```

### 进阶用法：Memento 系统（对象重建恢复）

```cpp
// 定义 Memento Translator，使列数据在对象删除/重建时自动保存/恢复
UCLASS()
class UMyDataColumnMementoTranslator : public UTedsDefaultMementoTranslator
{
    GENERATED_BODY()
public:
    virtual const UScriptStruct* GetColumnType() const override 
    { 
        return FMyDataColumn::StaticStruct(); 
    }
};

// 添加 Memento 标签，使行在删除时自动创建快照
Storage->AddColumn(MyRow, FTypedElementMementoOnDelete::StaticStruct());
```

## Demo 示例

```cpp
// MyDataStorageFactory.h
#pragma once

#include "Elements/Interfaces/TypedElementDataStorageFactory.h"
#include "MyDataStorageFactory.generated.h"

USTRUCT()
struct FTaskNameColumn : public UE::Editor::DataStorage::FEditorDataStorageColumn
{
    GENERATED_BODY()
    UPROPERTY() FName TaskName;
};

USTRUCT()
struct FTaskCompletedTag : public UE::Editor::DataStorage::FEditorDataStorageTag
{
    GENERATED_BODY()
};

UCLASS()
class UMyDataStorageFactory final : public UEditorDataStorageFactory
{
    GENERATED_BODY()
public:
    virtual int32 GetOrder() const override { return 0; }
    virtual void RegisterTables(UE::Editor::DataStorage::ICoreProvider& Storage) override;
    virtual void RegisterQueries(UE::Editor::DataStorage::ICoreProvider& Storage) override;
};
```

```cpp
// MyDataStorageFactory.cpp
#include "MyDataStorageFactory.h"
#include "Elements/Interfaces/TypedElementDataStorageInterface.h"
#include "Elements/Framework/TypedElementQueryBuilder.h"

void UMyDataStorageFactory::RegisterTables(UE::Editor::DataStorage::ICoreProvider& Storage)
{
    Storage.RegisterTable(
        {FTaskNameColumn::StaticStruct()},
        TEXT("TaskTable"));
}

void UMyDataStorageFactory::RegisterQueries(UE::Editor::DataStorage::ICoreProvider& Storage)
{
    // 查询所有未完成的任务
    auto QueryDesc = UE::Editor::DataStorage::Queries::Select()
        .ReadWrite<FTaskNameColumn>()
        .Exclude<FTaskCompletedTag>()
        .Compile();

    Storage.RegisterQuery(MoveTemp(QueryDesc));
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MassEntity` | Mass Entity 框架，TEDS 底层 ECS 实现 |
| `MassSpawner` | Mass Spawner，与 Mass 生态集成 |
| `TypedElementFramework` | Typed Element 框架，定义核心接口（ICoreProvider 等） |
| `TypedElementRuntime` | Typed Element 运行时，TypedElement 相关运行时功能 |
| `PropertyEditor` | 属性编辑器，TedsUI 中属性搜索/排序器依赖 |
| `EditorFramework` | 编辑器框架 |
| `ChaosVisualDebugger` | Chaos Visual Debugger 集成（SupportedPrograms） |

> **注意**：MassEntity 是最核心的依赖，TEDS 所有的行（Row）实际上就是 Mass Entity，所有的表（Table）就是 Mass Archetype。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `cc577021` | Fix race condition in TEDS Dynamic Column Generation | 修复动态列生成中的竞态条件 |
| 2026-04-16 | `419974fc` | [TEDS] Fixed incorrect pre-check before calling `AddCompositionToEntity_GetDelta`. | 修复调用实体组合添加前的错误预检查 |
| 2026-04-16 | `dfebe6ae` | [TEDS] Add Filter Config to allow filtering to continue if a row is hit that fails VerifyColumns | 新增过滤配置：行验证失败时允许继续过滤 |
| 2026-04-14 | `b78fe9c6` | [TEDS] Deprecated `CurrentRowHasColumns` and `CurrentBatchTableHasColumns` in favor of `CurrentTable` | 废弃旧 API，统一使用 CurrentTable 系列查询 |
| 2026-04-14 | `86eacb4b` | [TEDS] Fixed the result counter in FQueryResult not being atomic. | 修复查询结果计数器的原子性问题 |

### 维护评价

**维护状态：活跃维护中** 🟢

- **创建时间**：2024-07-27，约 2 年前
- **最近更新**：最近一次提交在 2026-05-26，距今不到 1 个月，更新频率较高
- **更新内容**：近期提交集中在竞态条件修复、API 重构（废弃旧接口统一为新接口）、原子性修复等，表明项目处于活跃的稳定化阶段
- **实验性状态**：`IsExperimentalVersion=true`，但 `EnabledByDefault=true`，说明 Epic 内部已在使用，但对外接口可能仍有变动
- **API 稳定性**：近期有明确的 API 废弃标记（`b78fe9c6`），说明接口正在向更一致的方向演进
- **代码规模**：117 个源文件，属于大型插件，架构成熟
- **已知限制**：
  - 实验性插件，接口可能在后续版本变动
  - UncookedOnly / Editor 模块，不可在 Shipping 构建中使用
  - 依赖 MassEntity 框架，需要理解 Mass ECS 范式

**推荐使用**：如果你在开发编辑器扩展、自定义面板或需要高性能批量处理编辑器数据的工具，TEDS 是推荐的方案。但要注意它是实验性插件，生产环境使用前需评估接口稳定性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorDataStorage)
- [TypedElementFramework 源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Source/Runtime/TypedElementFramework)
- [MassEntity 源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay)