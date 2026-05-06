# TEDS 编辑器兼容性模块 (TedsEditorCompatibility)

> Experimental UI Features for the Editor, built on TEDS: Editor Data Storage.

| 属性 | 值 |
|---|---|
| 中文名 | TEDS 编辑器兼容性模块 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（代码模块） |
| 模块 | `TedsEditorCompatibility` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-25 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/EditorDataStorageFeatures/Source/TedsEditorCompatibility) | |

## 用途

`TedsEditorCompatibility` 是 TEDS（Typed Editor Data Storage）框架中负责将传统编辑器对象（如 `UWorld`、`ULevel`）的生命周期与 TEDS 数据存储进行桥接的模块。它解决了以下问题：

- 当编辑器创建、销毁或修改 World/Level 时，TEDS 需要同步更新相应的数据行（Row）和标签（Tag）。
- 提供工厂类（`UTedsLevelFactory`、`UTedsWorldFactory`）来自动监听原生编辑器事件并转换为 TEDS 数据操作。
- 使 TEDS 功能模块（如 Outliner、PropertyEditor）能够感知并正确反映编辑器中 Level/World 的变更，无需用户手动管理同步。

该模块属于 TEDS 编辑器功能（EditorDataStorageFeatures）的核心基础设施，不属于最终用户直接调用的功能，而是供其他 TEDS 子模块依赖使用。

## 使用场景

- 你在构建一个基于 TEDS 的编辑器 UI 功能（如自定义大纲、属性面板）→ 需要依赖此模块来保证 Level/World 状态与 TEDS 数据一致。
- 你需要让 TEDS 查询（Query）能正确筛选或关联到编辑器中的 World 和 Level 对象。
- 你在开发 TEDS 扩展工厂时，需要注册与 World/Level 生命周期绑定的表（Table）和查询（Query）。

## 蓝图用法

本模块不提供任何可直接在蓝图中调用的节点或函数。所有操作均在 C++ 层通过 `UEditorDataStorageFactory` 接口完成。

## C++ 用法

### 头文件引入

```cpp
#include "Level/TedsLevelFactory.h"
#include "World/TedsWorldFactory.h"
```

### 基本用法

创建工厂子类并注册到 TEDS 系统。以下示例来自模块源文件：

```cpp
// TedsLevelFactory.cpp (路径: Source/TedsEditorCompatibility/Private/Level/TedsLevelFactory.cpp)
void UTedsLevelFactory::RegisterTables(UE::Editor::DataStorage::ICoreProvider& DataStorage)
{
    // 注册与 Level 相关的表
    DataStorage.RegisterTable(...);
}

void UTedsLevelFactory::PreRegister(UE::Editor::DataStorage::ICoreProvider& DataStorage)
{
    // 在注册前获取兼容性提供者
    DataStorageCompat = DataStorage.GetCompatibilityProvider();
}

void UTedsLevelFactory::RegisterQueries(UE::Editor::DataStorage::ICoreProvider& DataStorage)
{
    // 注册查询以响应 Level 添加/移除
    DataStorage.RegisterQuery(...);
}

void UTedsLevelFactory::OnLevelAddedToWorld(ULevel* InLevel, UWorld* InWorld)
{
    // 当 Level 被添加到世界时，创建对应的 TEDS 行并附加标签
    DataStorageCompat->CreateRow(InLevel);
}
```

### 进阶用法

组合使用 `UTedsLevelFactory` 和 `UTedsWorldFactory` 来同步 World 和 Level 的生命周期：

```cpp
// 通常在模块启动时自动创建和注册，无需手动调用
class FTedsEditorCompatibilityModule : public IModuleInterface
{
    virtual void StartupModule() override
    {
        // TEDS 内核会自动发现并注册所有 UEditorDataStorageFactory 子类
        // 只需确保模块被加载即可
    }
};
```

## Demo 示例

创建一个自定义工厂类，监听特定编辑器对象（如 `AActor`）的创建：

```cpp
// MyCustomFactory.h
#pragma once

#include "Elements/Interfaces/TypedElementDataStorageFactory.h"
#include "MyCustomFactory.generated.h"

UCLASS()
class UMyCustomFactory : public UEditorDataStorageFactory
{
    GENERATED_BODY()

public:
    virtual void RegisterTables(UE::Editor::DataStorage::ICoreProvider& DataStorage) override;
    virtual void RegisterQueries(UE::Editor::DataStorage::ICoreProvider& DataStorage) override;
};

// MyCustomFactory.cpp
#include "MyCustomFactory.h"
#include "DataStorage/CompatibilityProvider.h"

void UMyCustomFactory::RegisterTables(UE::Editor::DataStorage::ICoreProvider& DataStorage)
{
    // 注册表结构...
}

void UMyCustomFactory::RegisterQueries(UE::Editor::DataStorage::ICoreProvider& DataStorage)
{
    // 添加对 AActor 创建事件的监听
    DataStorage.RegisterQuery(
        UE::Editor::DataStorage::Query::Select()
            .Where<FMyRowTag>()
            .ForEach([](UE::Editor::DataStorage::IQueryContext& Context, UE::Editor::DataStorage::RowHandle Row)
            {
                // 处理逻辑
            })
    );
}
```

## 模块依赖

在 `TedsEditorCompatibility.Build.cs` 中声明了以下独特依赖：

| 模块 | 用途 |
|---|---|
| `TypedElementFramework` | 提供 `UEditorDataStorageFactory` 基类和 TEDS 接口 |
| `EditorDataStorage` | TEDS 核心数据存储与查询引擎 |
| `UnrealEd` | 访问编辑器 World/Level 生命周期事件 |

（省略了 `Core`, `CoreUObject`, `Engine`, `Slate` 等常见依赖）

## 维护状态

### 近期更新

- 2025-10-14 `267e8191` — Fix TedsType info assert when running certain Verse automated tests（跨模块修复）
- 2025-10-02 `1f8278e6` — Re-enable Teds AssetData after resolving test and FName issues（相关功能恢复）
- 2025-09-26 `7d070444` — [TEDS Viewers] Allow Sorting to be persisted via IsEnabled and GetColumnSort functions on the TEDS S（排序持久化）
- 2025-09-25 `8d9818a1` — [TEDS Viewers] Create a new composite hierarchy viewer (include searching and filtering by default)（新复合视图查看器）
- 2025-09-25 `4161c053` — Add a new TEDSFilterBar Widget and add TedsFilters to the TableViewer module (TedsOutlinerFilter to（新增过滤器条和过滤器）

### 维护评价

- **创建时间**：2025年9月25日（约 2 个月）
- **活跃度**：非常活跃，几乎每天都有提交，且涉及功能增强和错误修复。
- **是否推荐使用**：✅ 推荐，但请注意此模块仍为实验性（`IsExperimentalVersion=true`），接口可能随 TEDS 框架演进而变化。适合用于基于 TEDS 的自定义编辑器功能开发。
- **已知限制**：实验性阶段，文档较少，可能需要阅读源码理解细节。API 仍在快速迭代中。

## 相关链接

- [源码目录](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/EditorDataStorageFeatures/Source/TedsEditorCompatibility)
- [插件根目录](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EditorDataStorageFeatures)
- [TEDS 核心文档（Unreal Engine 官方）](https://docs.unrealengine.com/5.7/en-US/typed-data-storage-in-unreal-engine/)