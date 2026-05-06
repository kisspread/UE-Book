# TEDS: Editor Data Storage Features - TedsAlerts

> Experimental UI Features for the Editor, built on TEDS: Editor Data Storage.

| 属性 | 值 |
|---|---|
| 中文名 | TEDS 告警模块 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器功能） |
| 模块 | `TedsActorCompatibility` (Runtime), `TedsAlerts` (Runtime), `TedsAssetData` (Runtime), `TedsContentBrowser` (Runtime), `TedsDebugger` (Runtime), `TedsEditorCompatibility` (Runtime), `TedsEverythingPicker` (Runtime), `TedsOutliner` (Runtime), `TedsPropertyEditor` (Runtime), `TedsQueryStack` (Runtime), `TedsRevisionControl` (Runtime), `TedsSettings` (Runtime), `TedsTableViewer` (Runtime), `TedsTypeInfo` (Runtime), `TedsTypedElementBridge` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-25 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EditorDataStorageFeatures) | |

## 用途

`TedsAlerts` 模块为 TEDS（Editor Data Storage）提供了一套 **轻量级的告警系统**。该系统允许开发者在 TEDS 数据行上附加告警（Alert），并通过统一的 UI 展示告警图标、消息及操作回调。告警会自动在父子行之间传播计数，使得像 Outliner 这样的工具能够直观地显示警告和错误数量。

**解决什么问题？**  
在基于 TEDS 的编辑器工具中（如内容浏览器、大纲视图），经常需要向用户展示某些行（例如资产、Actor）的状态异常（如编译错误、配置冲突）。`TedsAlerts` 提供了标准化的方式添加、更新和移除这些告警，并自动管理告警链（按优先级排序）和父子层级计数，无需开发者手动跟踪复杂的 UI 状态。

## 使用场景

- 在 TEDS 驱动的 **Outliner** 中，为有错误的 Actor 行显示红色图标，并附带错误数量和工具提示。
- 在 **资产资产管理** 流程中，当资产校验失败时，在资产行上添加警告告警，点击告警可打开修复对话框。
- 任何需要向用户提示 TEDS 行级别状态信息的编辑器工具。

## 蓝图用法

本模块的公共 API 均为 C++ 函数（`AddAlert`、`RemoveAlert` 等），**未暴露为蓝图可调用节点**。如需在蓝图中使用，需要创建包装函数或通过 C++ 间接调用。

## C++ 用法

### 头文件引入

```cpp
#include "TedsAlerts.h"
#include "TedsAlertColumns.h"
```

### 基本用法

以下示例展示如何在 TEDS 行上添加一个错误告警，并设置一个简单的操作回调（例如打开日志窗口）。

```cpp
using namespace UE::Editor::DataStorage;

// 获取 DataStorage 实例（通常在模块中通过注入获得）
ICoreProvider& DataStorage = /* ... */;

// 目标行句柄
RowHandle TargetRow = /* ... */;

// 添加告警
Alerts::AddAlert(DataStorage, TargetRow,
    FName("CompileError"),                      // 唯一名称
    FText::FromString("Actor 编译失败"),         // 消息文本
    Columns::FAlertColumnType::Error,           // 类型：Error
    200,                                        // 优先级（0-255，越高越靠前）
    [](RowHandle TriggeredRow)                  // 可选回调：点击告警时触发
    {
        UE_LOG(LogTemp, Warning, TEXT("Alert triggered for row %d"), TriggeredRow);
    });
```

文件来源：`Source/TedsAlerts/Public/TedsAlerts.h`

### 移除告警

```cpp
Alerts::RemoveAlert(DataStorage, TargetRow, FName("CompileError"));
```

### 更新告警消息

```cpp
Alerts::UpdateAlertText(DataStorage, TargetRow, FName("CompileError"), 
    FText::FromString("新版编译错误详情"));
```

### 在查询上下文中使用

如果在 TEDS 查询回调中运行，可以使用 `IQueryContext` 重载以避免额外的查询开销：

```cpp
void MyQueryCallback(UE::Editor::DataStorage::IQueryContext& Context, RowHandle Row, FSomeColumn& Column)
{
    Alerts::AddAlert(Context, Row, FName("MyAlert"), FText::GetEmpty(), 
        Columns::FAlertColumnType::Warning);
}
```

## Demo 示例

以下是一个完整的 C++ 工厂类示例，演示如何在模块启动时注册告警查询，并在特定行上添加告警。

```cpp
// MyAlertFactory.h
#pragma once
#include "Elements/Interfaces/TypedElementDataStorageFactory.h"
#include "MyAlertFactory.generated.h"

UCLASS()
class UMyAlertFactory : public UEditorDataStorageFactory
{
    GENERATED_BODY()
public:
    void RegisterQueries(UE::Editor::DataStorage::ICoreProvider& DataStorage) override;
};

// MyAlertFactory.cpp
#include "MyAlertFactory.h"
#include "TedsAlerts.h"
#include "TedsAlertColumns.h"

void UMyAlertFactory::RegisterQueries(UE::Editor::DataStorage::ICoreProvider& DataStorage)
{
    using namespace UE::Editor::DataStorage;

    // 注册一个查询：当某列存在时添加告警
    DataStorage.RegisterQuery({
        .Name = "DemoAlertQuery",
        .OnAdd = [](IQueryContext& Context, RowHandle Row)
        {
            // 为这个新行添加一个警告告警
            Alerts::AddAlert(Context, Row, FName("DemoWarning"),
                FText::FromString("这是一个演示告警"),
                Columns::FAlertColumnType::Warning);
        },
        .OnRemove = [](IQueryContext& Context, RowHandle Row)
        {
            // 行被移除时清除告警
            Alerts::RemoveAlert(Context, Row, FName("DemoWarning"));
        }
    });
}
```

## 模块依赖

仅列出非标准依赖：

| 模块 | 用途 |
|---|---|
| `TypedElementDataStorage` | 提供核心数据存储接口（`ICoreProvider`、`IQueryContext`） |
| `TypedElementDataStorageUi` | 提供 UI 构造函数接口（`IUiProvider`）和 Widget 构造函数基类 |
| `DataStorage` | 提供基础数据类型（`FEditorDataStorageColumn`、`FEditorDataStorageTag`） |

其他依赖为常见核心模块（Core、CoreUObject、Engine 等），不赘述。

## 维护状态

### 近期更新

- 2025-10-14 `267e8191` — Fix TedsType info assert when running certain Verse automated tests
- 2025-10-02 `1f8278e6` — Re-enable Teds AssetData after resolving test and FName issues
- 2025-09-26 `7d070444` — [TEDS Viewers] Allow Sorting to be persisted via IsEnabled and GetColumnSort functions
- 2025-09-25 `8d9818a1` — [TEDS Viewers] Create a new composite hierarchy viewer (include searching and filtering by default)
- 2025-09-25 `4161c053` — Add a new TEDSFilterBar Widget and add TedsFilters to the TableViewer module

### 维护评价

插件创建于 2025 年 9 月，至今约 1 个月，处于**早期开发阶段**。近期提交显示活跃的功能更新和修复，属于正在积极开发中的实验性功能。由于是 **Experimental** 插件，API 和结构可能发生变动，不建议在生产项目中使用。若需要稳定的告警系统，建议等待正式发布或使用现有的 `MessageLog` 方案。

## 相关链接

- [源码（插件根目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EditorDataStorageFeatures)
- [测试用例（路径推测）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EditorDataStorageFeatures/Tests) （实际可能不存在）