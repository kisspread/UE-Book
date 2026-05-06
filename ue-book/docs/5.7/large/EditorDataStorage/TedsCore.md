# TEDS: Editor Data Storage

> A central extendable data storage for editors and their corresponding data with support for viewing and editing through a collection of widgets.

| 属性 | 值 |
|---|---|
| 中文名 | 编辑器数据存储 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（脚本/配置资源） |
| 模块 | `TedsCore` (EditorAndProgram), `TedsUI` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-19 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EditorDataStorage) | |

## 用途

TEDS（Typed Element Data Storage）是一个基于 Mass Entity 框架的编辑器数据层。它提供一个可扩展的中央数据存储，用于高效管理编辑器中的对象（如 Actor、组件等）及其属性。TEDS 将编辑器数据解耦为列（Columns）和行（Rows），支持动态列生成、层次结构、数据快照（Mementos）以及通过小部件（Widgets）进行可视化与编辑。它的核心目标是将编辑器数据存储逻辑从 UI 和具体类型中分离，使开发者可以声明式地定义数据关系与处理流程，而无需关心底层存储细节。

## 使用场景

- 你需要构建一个编辑器工具，需要存储和查询大量临时或持久数据（如场景对象属性、选择状态、变换等）
- 你希望为编辑器对象添加自定义属性或标签，并能够通过统一的查询系统进行过滤和排序
- 你需要实现编辑器内对象的层级关系管理（如 Actor 间父子关系）
- 你希望为编辑器数据提供统一的撤销/重做支持（通过 Memento 系统）
- 你需要为编辑器数据表动态生成 UI 小部件，减少手动创建 Slate 控件的代码量

## 蓝图用法

TEDS 核心设计为 C++ 扩展系统，蓝图原生支持有限。但开发者可以通过 C++ 子类化 `UEditorDataStorageFactory` 或 `UTedsMementoTranslatorBase` 并将它们暴露为蓝图类型，间接在蓝图中使用。目前没有找到直接的 `BlueprintCallable` 函数或 `BlueprintReadWrite` 属性供蓝图节点调用。

对于需要蓝图交互的场景，建议将 TEDS 操作封装为自定义蓝图函数库或 Actor 组件。

## C++ 用法

### 头文件引入

```cpp
#include "TypedElementsDataStorage.h"           // 主模块头
#include "Elements/Interfaces/TypedElementDataStorageInterface.h" // ICoreProvider
#include "Elements/Interfaces/TypedElementDataStorageCompatibilityInterface.h" // ICompatibilityProvider
```

### 基本用法

以下代码演示如何通过 `UE::Editor::DataStorage::ICoreProvider` 创建一个新的表格，并添加一行带有整数列的数据。

```cpp
// 从模块或其他地方获取 ICoreProvider（通常通过 UEditorDataStorage 对象）
UEditorDataStorage* DataStorage = /* 从全局获取或通过模块接口 */;
UE::Editor::DataStorage::ICoreProvider& Storage = *DataStorage;

// 1. 注册一个包含自定义列的新表
// 首先需要一个列类型结构（必须继承自 FEditorDataStorageColumn）
USTRUCT()
struct FMyIntColumn : public FEditorDataStorageColumn
{
    GENERATED_BODY()
    UPROPERTY()
    int32 Value = 0;
};

// 注册表（返回 TableHandle）
TArray<const UScriptStruct*> Columns = { FMyIntColumn::StaticStruct() };
const FName TableName = TEXT("MyTable");
UE::Editor::DataStorage::TableHandle Table = Storage.RegisterTable(Columns, TableName);

// 2. 向表中添加一行（返回 RowHandle）
auto OnRowCreated = [](UE::Editor::DataStorage::RowHandle Row, const ICoreProvider& Provider)
{
    // 可以在创建后设置列数据（如果需要）
};
UE::Editor::DataStorage::RowHandle Row = Storage.AddRow(Table, OnRowCreated);
// 或者添加一行并设置数据
Storage.AddRow(Row, Table); // 如果已经预留了行

// 3. 获取并修改列数据
Storage.AddColumn(Row, FMyIntColumn::StaticStruct()); // 如果列是片段类型（非共享）
// 对于数据列，需要先添加
void* Data = Storage.GetMutableColumnData(Row, FMyIntColumn::StaticStruct());
if (Data)
{
    static_cast<FMyIntColumn*>(Data)->Value = 42;
}

// 4. 查询行上的列数量
uint32 ColumnCount = Storage.GetColumnCount(Row);
```

### 进阶用法

#### 动态列生成

TEDS 支持基于模板结构体动态生成列类型。以下示例使用 `FDynamicColumnGenerator` 创建一个值标签列：

```cpp
// 假设在 Environment 中持有 DynamicColumnGenerator
UE::Editor::DataStorage::FEnvironment& Env = /* ... */;
const UScriptStruct& Template = *FTedsValueTagColumn::StaticStruct();
const FName TagIdentifier = TEXT("MyTagValue");
const UScriptStruct* GeneratedType = Env.GenerateDynamicColumn(Template, TagIdentifier);
// 返回的动态列类型可用于注册表、添加列等
```

#### 层次结构注册

通过 `FTedsHierarchyRegistrar` 可以注册新的层次类型，并利用自动维护父子关系的处理器：

```cpp
UE::Editor::DataStorage::FTedsHierarchyRegistrar& Registrar = Env.GetHierarchyRegistrar();
UE::Editor::DataStorage::FHierarchyRegistrationParams Params;
Params.Name = TEXT("MyHierarchy");
Params.ChildTagTemplate = FEditorDataHierarchyChildTag_Template::StaticStruct();
Params.ParentTagTemplate = FEditorDataHierarchyParentTag_Template::StaticStruct();
Params.HierarchyDataTemplate = FEditorDataHierarchyData_Template::StaticStruct();
// 其他参数...
UE::Editor::DataStorage::FHierarchyHandle Handle = Registrar.RegisterHierarchy(&Storage, Params);

// 获取访问接口并设置父子关系
const auto* AccessInterface = Registrar.GetAccessInterface(Handle);
AccessInterface->SetParentRow(Storage, ChildRow, ParentRow);
```

#### 数据快照（Memento）

用于撤销/重做或对象替换。首先需要注册一个翻译器（`UTedsMementoTranslatorBase` 子类），然后通过 `FMementoSystem` 创建和恢复快照：

```cpp
// 在工厂或初始化中注册翻译器
class UMyIntColumnMementoTranslator : public UTedsDefaultMementoTranslator
{
    GENERATED_BODY()
public:
    virtual const UScriptStruct* GetColumnType() const override { return FMyIntColumn::StaticStruct(); }
};

// 创建快照
UE::Editor::DataStorage::RowHandle SourceRow = /* ... */;
UE::Editor::DataStorage::RowHandle MementoRow = Env.GetMementoSystem().CreateMemento(SourceRow);

// 恢复快照
Env.GetMementoSystem().RestoreMemento(MementoRow, TargetRow);
```

## Demo 示例

以下是一个最小化的 C++ 模块示例，演示了如何创建一个自定义列类型并将其用于 TEDS 存储。

**MyTedsDemoModule.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

DECLARE_LOG_CATEGORY_EXTERN(LogMyTedsDemo, Log, All);

class FMyTedsDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    void InitializeTeds();
};
```

**MyTedsDemoModule.cpp**
```cpp
#include "MyTedsDemoModule.h"
#include "Elements/Interfaces/TypedElementDataStorageInterface.h"
#include "TypedElementsDataStorage.h" // UEditorDataStorage

IMPLEMENT_MODULE(FMyTedsDemoModule, MyTedsDemo);
DEFINE_LOG_CATEGORY(LogMyTedsDemo);

// 自定义列类型
USTRUCT()
struct FMyDemoIntColumn : public FEditorDataStorageColumn
{
    GENERATED_BODY()
    UPROPERTY()
    int32 DemoValue = 0;
};

void FMyTedsDemoModule::StartupModule()
{
    InitializeTeds();
}

void FMyTedsDemoModule::ShutdownModule()
{}

void FMyTedsDemoModule::InitializeTeds()
{
    if (UEditorDataStorage* DataStorage = FModuleManager::GetModuleChecked<FEditorDataStorageModule>("EditorDataStorage").GetDataStorage())
    {
        UE::Editor::DataStorage::ICoreProvider& Provider = *DataStorage;

        // 注册表
        TArray<const UScriptStruct*> Columns = { FMyDemoIntColumn::StaticStruct() };
        UE::Editor::DataStorage::TableHandle Table = Provider.RegisterTable(Columns, FName(TEXT("DemoTable")));

        // 添加行
        UE::Editor::DataStorage::RowHandle Row = Provider.AddRow(Table,
            [](UE::Editor::DataStorage::RowHandle RowHandle, const UE::Editor::DataStorage::ICoreProvider& P)
            {
                UE_LOG(LogMyTedsDemo, Log, TEXT("Row %llu created."), RowHandle);
            });

        // 设置列数据
        Provider.AddColumn(Row, FMyDemoIntColumn::StaticStruct());
        if (FMyDemoIntColumn* Data = reinterpret_cast<FMyDemoIntColumn*>(Provider.GetMutableColumnData(Row, FMyDemoIntColumn::StaticStruct())))
        {
            Data->DemoValue = 100;
        }

        UE_LOG(LogMyTedsDemo, Log, TEXT("Demo TEDS integration complete."));
    }
}
```

**注意**：此示例假设 `FEditorDataStorageModule` 暴露了 `GetDataStorage()` 方法。实际使用时建议通过模块接口获取，或者通过 `UEditorDataStorage` 全局单例（可自行注入）。

## 模块依赖

本插件依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `MassEntity` | 底层实体管理（ECS 核心）|
| `MassCommon` | Mass 通用类型和工具 |
| `StructUtils` | 动态结构生成（`FInstancedStruct`, `FPropertyBag`）|
| `MassSpawner` | （可能）处理器注册和管理 |
| `TypedElementFramework` | 类型化元素框架（接口定义）|

此外，`TedsUI` 模块还依赖于 `Slate` 和 `SlateCore` 等 UI 模块（标准依赖不列出）。`TedsCore` 本身没有 UI 依赖。

## 维护状态

### 近期更新

- 2025-08-21 5883629 — FRegistrationCommandChange 和 FDeregistrationCommandChange 增加对空 DataStorage 的防御。
- 2025-08-21 80aef2f — UEditorDataStorageCompatibility: 在 Deinitialize 中释放 Environment 引用。
- 2025-08-20 881afb9 — FEnvironment: 添加析构函数以清除 Legacy::FCommandBuffer 中待处理的命令。
- 2025-08-19 d054c8d — [TEDS] 添加了基本的协作时间切片支持。
- 2025-08-19 5273c34 — TEDS 层次结构: 当 SetParent() 导致行层次变化时（有效旧父→有效新父）正确处理。

### 维护评价

- **创建时间**：2025-08-19，年龄不足一个月。
- **更新频率**：非常活跃，几乎每天都有功能性提交。
- **活跃度**：项目在积极开发中，有多位贡献者参与。
- **稳定性**：标记为**实验性**（`IsExperimentalVersion=true`），API 和架构可能随时变动，不推荐用于生产环境。
- **推荐使用**：适合探索和原型开发，但需要做好后期升级的准备。若需要稳定编辑器数据存储方案，建议关注后续正式版本。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EditorDataStorage)
- [官方文档](https://docs.unrealengine.com)（目前未提供独立文档，可参考 TEDS 相关内容）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Source/Programs/Tests/EditorDataStorage)（假设存在，实际路径可能需要确认）