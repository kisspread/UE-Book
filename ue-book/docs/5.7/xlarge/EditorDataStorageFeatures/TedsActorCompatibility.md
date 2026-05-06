# TEDS Actor Compatibility

> Experimental UI Features for the Editor, built on TEDS: Editor Data Storage.

| 属性 | 值 |
|---|---|
| 中文名 | TEDS 角色兼容性 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器资产、蓝图类） |
| 模块 | `TedsActorCompatibility` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-25 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EditorDataStorageFeatures) | |

## 用途

`TedsActorCompatibility` 是 TEDS（Typed Element Data Storage）在编辑器中的角色兼容性模块。它解决的核心问题是：**将 Unreal 传统 Actor 的属性（如标签、可见性、移动性、层级、级别、父级等）同步到 TEDS 数据存储中，并支持从 TEDS 列回写到 Actor**。该模块通过注册一系列查询和工厂类，在 Actor 创建、修改、销毁时自动维护 TEDS 中的对应列数据，使基于 TEDS 的 UI 组件（如 Content Browser、Outliner）能够直接读取和操作 Actor 的属性，而无需每次都从世界对象查询。

该模块是 TEDS 编辑器生态的基础组件，它建立了从 Actor 世界到 TEDS 数据存储的桥梁。

## 使用场景

- **你在开发基于 TEDS 的编辑器工具**，需要让 Actor 的属性（如可见性、父级、标签）在 TEDS 数据存储中自动同步。
- **你需要实现一个自定义的 Outliner 或 Property Panel**，并希望统一使用 TEDS 列来显示 Actor 信息，而不直接依赖 `AActor` 的运行时查询。
- **你需要将 Actor 的移动性、图标覆盖、视图轮廓颜色等特性映射到 TEDS 列**，以便在 TEDS 驱动的 UI 中直接排序、筛选和显示。

## 蓝图用法

该模块主要提供 C++ 工厂类和内部查询逻辑，不直接暴露 `BlueprintCallable` 函数。但可以通过继承 `UEditorDataStorageFactory` 并重写 `RegisterQueries` 来扩展同步逻辑。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RegisterQueries` | 注册数据同步查询，在模块加载时自动调用 | `UEditorDataStorageFactory`（基类） |

实际使用中，无需在蓝图中手动调用任何函数；模块在启动时自动注册所有查询。

## C++ 用法

### 头文件引入

根据模块公开的列定义和工厂基类，引入所需文件：

```cpp
#include "Columns/TedsActorMobilityColumns.h"     // 使用移动性列
#include "Columns/TedsActorComponentCompatibilityColumns.h" // 使用组件类型标签
#include "TedsActorCompatibilityFactory.h"         // 如果需要自定义工厂（不推荐直接实例化）
```

### 基本用法

本模块通过 `UEditorDataStorageFactory` 子类自动注册同步查询。开发者若需要读取 Actor 的 TEDS 列数据，可以使用 TEDS 核心 API：

```cpp
// 假设 DataStorage 为 ICoreProvider 指针
using namespace UE::Editor::DataStorage;

// 获取某个 Actor 对应的 RowHandle
RowHandle ActorRow = DataStorage->FindRow(AActor*);

// 读取移动性列
if (const FTedsActorMobilityColumn* MobilityCol = DataStorage->GetColumn<FTedsActorMobilityColumn>(ActorRow))
{
    EComponentMobility::Type Mobility = MobilityCol->Mobility;
}
```

### 进阶用法

#### 自定义同步列

若需要为 Actor 添加新的同步属性，可继承 `UEditorDataStorageFactory` 并注册自己的查询：

```cpp
// MyActorCustomFactory.h
UCLASS()
class UMyActorCustomFactory : public UEditorDataStorageFactory
{
    GENERATED_BODY()
public:
    virtual void RegisterQueries(ICoreProvider& DataStorage) override;
};

// MyActorCustomFactory.cpp
void UMyActorCustomFactory::RegisterQueries(ICoreProvider& DataStorage)
{
    // 1. 注册将 Actor 属性复制到列的查询
    DataStorage.RegisterQuery({
        .Name = "MyPropertyToColumnQuery",
        .TickGroup = ETedsTickGroup::SyncToData,
        .Conditions = ...,
        .Callback = [](IDirectQueryContext& Context, ...) { /* 复制逻辑 */ }
    });

    // 2. 注册将列写回 Actor 的查询（当带有 FTypedElementSyncBackToWorldTag 时）
    DataStorage.RegisterQuery({
        .Name = "MyColumnToActorQuery",
        .TickGroup = ETedsTickGroup::SyncToWorld,
        .Conditions = ...,
        .Callback = [](IDirectQueryContext& Context, ...) { /* 写回逻辑 */ }
    });
}
```

## Demo 示例

以下是一个完整的 C++ 模块示例，展示如何通过 `TedsActorCompatibility` 提供的列读取 Actor 的移动性并在控制台打印。

```cpp
// MyActorDebugger.h
#pragma once
#include "CoreMinimal.h"
#include "Modules/ModuleInterface.h"
#include "Containers/Ticker.h"

class FMyActorDebuggerModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    FTSTicker::FDelegateHandle TickHandle;
    void OnTick(float DeltaTime);
};

// MyActorDebugger.cpp
#include "MyActorDebugger.h"
#include "Elements/Interfaces/TypedElementDataStorageInterface.h"
#include "Columns/TedsActorMobilityColumns.h"

#define LOCTEXT_NAMESPACE "MyActorDebugger"

IMPLEMENT_MODULE(FMyActorDebuggerModule, MyActorDebugger)

void FMyActorDebuggerModule::StartupModule()
{
    TickHandle = FTSTicker::GetCoreTicker().AddTicker(
        FTickerDelegate::CreateRaw(this, &FMyActorDebuggerModule::OnTick));
}

void FMyActorDebuggerModule::ShutdownModule()
{
    FTSTicker::GetCoreTicker().RemoveTicker(TickHandle);
}

void FMyActorDebuggerModule::OnTick(float DeltaTime)
{
    using namespace UE::Editor::DataStorage;
    ICoreProvider* DataStorage = IDataStorageProvider::Get();
    if (!DataStorage || !DataStorage->IsReady())
        return;

    // 获取所有具有 FTedsActorMobilityColumn 的行
    DataStorage->ForEachRow(
        DataStorage->CreateQueryBuilder()
            .Include<FTedsActorMobilityColumn>()
            .Build(),
        [](IDirectQueryContext& Context, RowHandle Row)
        {
            const FTedsActorMobilityColumn* Col = Context.GetColumn<FTedsActorMobilityColumn>(Row);
            UE_LOG(LogTemp, Display, TEXT("Row %llu has mobility: %d"), Row, Col ? Col->Mobility : -1);
            return true;
        });
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `TypedElementDataStorage` | 提供核心数据存储接口和列定义 |
| `TypedElementDataStorageUI` | 提供 UI 相关工厂基类（如 `UEditorDataStorageFactory`） |
| `TedsActorCompatibility` | 本模块自身，无需额外依赖 |
| `Engine` | 访问 `AActor`、`UWorld` 等引擎类 |

其他不常见依赖：无（所有依赖均为 TEDS 生态标准模块）。

## 维护状态

### 近期更新

- 2025-10-14 267e8191 Fix TedsType info assert when running certain Verse automated tests
- 2025-10-02 1f8278e6 Re-enable Teds AssetData after resolving test and FName issues
- 2025-09-26 7d070444 [TEDS Viewers] Allow Sorting to be persisted via IsEnabled and GetColumnSort functions
- 2025-09-25 8d9818a1 [TEDS Viewers] Create a new composite hierarchy viewer (include searching and filtering by default)
- 2025-09-25 4161c053 Add a new TEDSFilterBar Widget and add TedsFilters to the TableViewer module

### 维护评价

该模块创建于2025年9月，至今不到1个月，属于全新模块。最近的提交活跃，包含功能更新和测试修复。模块仍处于实验阶段（`IsExperimentalVersion=true`），但开发进度迅速，适合用于原型和探索性项目。由于存在大量依赖和实验性标记，不建议用于生产环境。

综合评级：🟢 活跃开发中，推荐在实验性项目中使用。

## 相关链接

- [源码（插件根目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EditorDataStorageFeatures)
- [本模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EditorDataStorageFeatures/Source/TedsActorCompatibility)
- [TEDS 官方文档（暂无）]()