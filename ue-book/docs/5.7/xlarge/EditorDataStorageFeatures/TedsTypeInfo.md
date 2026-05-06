# TEDS Type Info

> Experimental UI Features for the Editor, built on TEDS: Editor Data Storage.

| 属性 | 值 |
|---|---|
| 中文名 | 类型信息模块 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `TedsActorCompatibility` (Runtime), `TedsAlerts` (Runtime), `TedsAssetData` (Runtime), `TedsContentBrowser` (Runtime), `TedsDebugger` (Runtime), `TedsEditorCompatibility` (Runtime), `TedsEverythingPicker` (Runtime), `TedsOutliner` (Runtime), `TedsPropertyEditor` (Runtime), `TedsQueryStack` (Runtime), `TedsRevisionControl` (Runtime), `TedsSettings` (Runtime), `TedsTableViewer` (Runtime), `TedsTypeInfo` (Runtime), `TedsTypedElementBridge` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-25 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EditorDataStorageFeatures) | |

## 用途

`TedsTypeInfo` 是 **EditorDataStorageFeatures** 插件的一部分，负责在 TEDS（Typed Editor Data Storage）系统中管理编辑器中的类型元数据。它收集 `UClass`、`UScriptStruct`、`UVerseClass` 等类型信息，并将其作为数据行注册到 TEDS 表中，以供其他编辑器组件（如 Outliner、Property Editor、Asset Data 等）查询和使用。

核心功能包括：
- 自动发现和过滤编辑器中的类型（类、结构体、Verse 类型）。
- 为每种类型创建数据行并填充列（如名称、继承信息、接口、嵌套结构等）。
- 提供刷新和清空类型信息的接口，以响应类型注册/反注册事件。
- 在 TEDS 数据存储更新后自动维护类型层级关系。

该模块是 TEDS 生态的基础设施，使得编辑器能够通过 TEDS 统一访问类型相关的结构化数据。

## 使用场景

- 你正在开发一个基于 TEDS 的自定义编辑器面板（如类型浏览器、属性查看器），需要获取编辑器内所有类的元数据。
- 你需要为场景中的 Actor/Component 类型建立层级关系，以便在 TEDS 查询中按类型过滤。
- 你希望将 Verse 类型的访问级别信息暴露给 TEDS 查询，方便实现版本控制或权限显示。

## 蓝图用法

当前模块未公开任何蓝图可调用函数（`UFUNCTION(BlueprintCallable)`）。所有类型信息的注册和刷新由模块内部自动完成，无需手动触发。如果需要手动刷新，可通过 C++ 调用 `FTedsTypeInfoModule::RefreshTypeInfo()`，但该方法未暴露给蓝图。

## C++ 用法

### 头文件引入

```cpp
#include "TedsTypeInfoModule.h"
#include "Elements/Columns/TedsTypeInfoColumns.h"
```

### 基本用法

#### 启用/禁用类型信息集成

```cpp
// 在模块 StartupModule 或适当位置启用类型信息集成
UE::Editor::DataStorage::TypeInfo::FTedsTypeInfoModule& TypeInfoModule = UE::Editor::DataStorage::TypeInfo::FTedsTypeInfoModule::GetChecked();
TypeInfoModule.EnableTedsTypeInfoIntegration();

// 之后即可在 TEDS 查询中使用类型相关列查询
```

#### 手动刷新所有类型信息

```cpp
// 如果类型注册发生变化（如新模块加载），调用此函数重新填充类型表
TypeInfoModule.RefreshTypeInfo();
```

#### 清空并刷新类型信息

```cpp
// 先清空，再触发完整刷新
TypeInfoModule.FlushTypeInfo();   // 清空现有类型行
TypeInfoModule.RefreshTypeInfo(); // 重新填充
```

### 进阶用法

#### 在查询中使用类型列

```cpp
// 创建一个 TEDS 查询，筛选所有“类”类型的行
using namespace UE::Editor::DataStorage;
QueryDescription::Selection SelectAllClasses;
SelectAllClasses.AddTagCondition<FDataStorageClassTypeInfoTag>(TagCondition::Require);

// 执行查询并处理结果...
```

#### 自定义类型过滤

```cpp
// 通过子类化 UTypeInfoFactory 可以覆盖过滤逻辑
class UMyTypeInfoFactory final : public UTypeInfoFactory
{
public:
    virtual bool FilterClassInfo(const UClass* ClassInfo) override
    {
        // 只保留非引擎、非抽象类
        return !ClassInfo->IsNative() && !ClassInfo->HasAnyClassFlags(CLASS_Abstract);
    }
};
```

## Demo 示例

以下示例演示如何在自定义 TEDS 模块中使用 `TedsTypeInfo` 获取所有类的行句柄。

```cpp
// MyTypeQuery.cpp
#include "DataStorage/Query.h"
#include "Elements/Columns/TedsTypeInfoColumns.h"
#include "TedsTypeInfoModule.h"

void QueryAllClassTypes()
{
    using namespace UE::Editor::DataStorage;
    ICoreProvider& Provider = GetDataStorageProvider(); // 假定存在全局访问函数

    // 构建查询：选择拥有 FDataStorageClassTypeInfoTag 的行
    QueryDescription Query;
    Query.Selection.AddTagCondition<FDataStorageClassTypeInfoTag>(TagCondition::Require);

    // 执行查询
    Provider.Select(Query, [](const QueryContext& Context, const RowHandle* Rows, int32 RowCount)
    {
        for (int32 i = 0; i < RowCount; ++i)
        {
            // 处理每个类型行...
        }
    });
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `TypedElementFramework` | 提供 TEDS 核心接口（数据存储、查询、表） |
| `EditorDataStorage` | 提供编辑器特有的数据存储扩展（`ICompatibilityProvider`、`IHierarchyAccessInterface`） |
| `TedsCore` | TEDS 核心模块，包含基础列和工厂基类 |

其他依赖均为标准 Core/Engine 模块，此处不列出。

## 维护状态

### 近期更新

- 2025-10-14 `267e8191` — Fix TedsType info assert when running certain Verse automated tests
- 2025-10-02 `1f8278e6` — Re-enable Teds AssetData after resolving test and FName issues
- 2025-09-26 `7d070444` — [TEDS Viewers] Allow Sorting to be persisted via IsEnabled and GetColumnSort functions
- 2025-09-25 `8d9818a1` — [TEDS Viewers] Create a new composite hierarchy viewer (include searching and filtering by default)
- 2025-09-25 `4161c053` — Add a new TEDSFilterBar Widget and add TedsFilters to the TableViewer module

### 维护评价

- **创建时间**：2025-09-25（约 1 个月前）
- **最近更新**：活跃，本模块最近一次是修复 Verse 测试断言
- **活跃度**：整个插件近期有多项新增功能和修复，TedsTypeInfo 作为基础模块稳定维护
- **可能的问题**：仍处于实验阶段，API 可能变动；依赖的 TEDS 核心仍在演进
- **推荐使用**：若项目已采用 TEDS 架构，推荐使用；若未使用 TEDS，则无直接价值

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EditorDataStorageFeatures/Source/TedsTypeInfo)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EditorDataStorageFeatures/Tests)（插件级别测试）