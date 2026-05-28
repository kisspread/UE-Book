# TEDS: Editor Data Storage Features

> Experimental UI Features for the Editor, built on TEDS: Editor Data Storage.

| 属性 | 值 |
|---|---|
| 中文名 | 编辑器数据存储功能 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器UI功能） |
| 模块 | `TedsActorCompatibility` (Runtime), `TedsAlerts` (Runtime), `TedsAssetData` (Runtime), `TedsContentBrowser` (Runtime), `TedsDebugger` (Runtime), `TedsEditorCompatibility` (Runtime), `TedsEverythingPicker` (Runtime), `TedsOperations` (Runtime), `TedsOutliner` (Runtime), `TedsPropertyEditor` (Runtime), `TedsQueryStack` (Runtime), `TedsRevisionControl` (Runtime), `TedsSettings` (Runtime), `TedsTableViewer` (Runtime), `TedsTypeInfo` (Runtime), `TedsTypedElementBridge` (Runtime), `UnifiedFavorites` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-07-27 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorDataStorageFeatures) | |

## 用途

TEDS: Editor Data Storage Features 是一个基于 TEDS（Typed Element Data Storage）构建的实验性插件，旨在为 Unreal Editor 提供新的数据驱动 UI 功能。它的核心价值在于利用 TEDS 的高性能查询和存储能力来实现编辑器界面的现代化和模块化。

这个插件解决的主要问题是：传统编辑器 UI（如细节面板、大纲视图等）直接绑定到引擎内部数据结构，导致扩展性差、查询效率低且难以跨模块协同工作。本插件将编辑器 UI 的各种功能（如警报系统、资产数据、大纲视图等）解耦为独立的 TEDS 模块，通过数据列（Column）和查询（Query）来驱动 UI 行为，使得功能更灵活、可复用且易于维护。

## 使用场景

- **你需要在大纲视图（Outliner）中显示复杂的、数据驱动的警告和通知** → 使用 `TedsAlerts` 模块
- **你希望自定义内容浏览器的显示和筛选逻辑** → 使用 `TedsContentBrowser` 模块
- **你需要一个可视化的 TEDS 数据表调试器** → 使用 `TedsDebugger` 模块
- **你想要构建一个高性能、可定制的资产选择器** → 使用 `TedsEverythingPicker` 模块
- **你需要在细节面板中展示基于 TEDS 数据的属性** → 使用 `TedsPropertyEditor` 模块
- **你想要为编辑器中的行（Row）添加一个统一的收藏夹功能** → 使用 `UnifiedFavorites` 模块

## 蓝图用法

**重要提示**：此插件主要为**编辑器扩展开发者**和**程序化内容生成工具**设计，其核心 API 为 C++。蓝图支持有限，主要集中在数据列（Column）的定义上。

### 核心列类型（蓝图可用结构体）

这些结构体定义了可以在 TEDS 中存储的数据，是构建其他功能的基础。

| 结构体 | 说明 | 所在模块 |
|---|---|---|
| `FTedsAlertColumn` | 存储单个警报信息，包括消息、类型和优先级。 | `TedsAlerts` |
| `FTedsChildAlertColumn` | 存储子级警报的统计计数（按类型）。 | `TedsAlerts` |
| `FTedsAlertActionColumn` | 为警报附加一个可点击的回调函数。 | `TedsAlerts` |

### 使用示例（蓝图描述）

1.  **创建一个带有警报的行**：虽然不能直接通过蓝图创建警报（需要C++），但你可以在蓝图中操作使用这些列的 `RowHandle`。例如，你可以通过蓝图函数库获取一个行的 `FTedsAlertColumn`，然后读取其 `Message` 和 `AlertType` 来在自定义UI中显示。
2.  **在自定义编辑器工具中显示警报**：你可以创建一个 Slate Widget，在其中查询具有 `FTedsAlertColumn` 的行，并根据 `AlertType`（警告或错误）显示不同颜色的图标。

## C++ 用法

### 头文件引入

使用警报系统的核心头文件：
```cpp
#include "TedsAlerts.h"
```

包含警报列定义的头文件：
```cpp
#include "TedsAlertColumns.h"
```

### 基本用法

以下示例展示了如何为一个行添加、更新和移除一个警告类型的警报。代码逻辑来源于 `TedsAlerts` 模块的公共API设计。

```cpp
// 伪代码，基于公共API和数据结构推导
#include "TedsAlerts.h"
#include "TedsAlertColumns.h"

using namespace UE::Editor::DataStorage;

// 假设你已经有一个 ICoreProvider 引用和一个有效的 RowHandle
void ManageAlerts(ICoreProvider& DataStorage, RowHandle TargetRow)
{
    // 1. 添加一个警告警报
    Alerts::AddAlert(
        DataStorage,
        TargetRow,
        FName("TestWarning"),
        NSLOCTEXT("MyTool", "TestWarningMsg", "This is a test warning."),
        Columns::FAlertColumnType::Warning,
        128 // 高优先级
    );

    // 2. 更新该警报的消息
    Alerts::UpdateAlertText(
        DataStorage,
        TargetRow,
        FName("TestWarning"),
        NSLOCTEXT("MyTool", "UpdatedMsg", "Warning has been updated!")
    );

    // 3. 移除该警报
    Alerts::RemoveAlert(
        DataStorage,
        TargetRow,
        FName("TestWarning")
    );
}
```

### 进阶用法

在 TEDS 查询回调中操作警报。`IQueryContext` 版本的 API 允许在处理器内部高效地修改警报，避免频繁地与核心数据存储交互。

```cpp
// 在一个 TEDS 查询处理器中使用警报系统
void MyQueryProcessor::Run(FQueryResult& QueryResult)
{
    QueryResult.ForEachRow([this](RowHandle Row, FTedsAlertColumn& AlertCol)
    {
        // 在查询上下文中直接添加警报，效率更高
        Alerts::AddAlert(
            *QueryContext, // IQueryContext& 从查询结果中获取
            Row,
            FName("DynamicAlert"),
            FText::FromString(TEXT("This alert was added during a query.")),
            Columns::FAlertColumnType::Error,
            200,
            [](RowHandle ActionRow) { /* 处理警报点击 */ }
        );
    });
}
```

## Demo 示例

下面是一个最小的 C++ 示例，展示如何在自定义编辑器工具中注册一个警报，并在工具被销毁时清理它。这模拟了一个常见的“检查工具”场景。

**MyEditorTool.h**
```cpp
#pragma once

#include "CoreMinimal.h"

namespace UE::Editor::DataStorage
{
    class ICoreProvider;
    struct RowHandle;
}

class FMyEditorTool
{
public:
    FMyEditorTool();
    ~FMyEditorTool();

private:
    void PerformCheck();
    void ClearAlert();

    UE::Editor::DataStorage::RowHandle MonitoredRow;
    FName AlertName;
};
```

**MyEditorTool.cpp**
```cpp
#include "MyEditorTool.h"
#include "TedsAlerts.h"
#include "Modules/ModuleManager.h"

using namespace UE::Editor::DataStorage;

FMyEditorTool::FMyEditorTool()
    : MonitoredRow(InvalidRowHandle)
    , AlertName(FName("MyToolAlert"))
{
    // 假设通过某种方式（如选择）获得了一个需要监控的行
    MonitoredRow = /* ... */;
    PerformCheck();
}

FMyEditorTool::~FMyEditorTool()
{
    ClearAlert();
}

void FMyEditorTool::PerformCheck()
{
    if (!ensure(MonitoredRow != InvalidRowHandle))
    {
        return;
    }

    // 通过模块获取数据存储实例
    ICoreProvider& DataStorage = IModuleManager::Get().LoadModuleChecked<FTedsAlertsModule>(TEXT("TedsAlerts")).GetDataStorage();

    // 执行检查...
    bool bHasError = /* ... */;

    if (bHasError)
    {
        Alerts::AddAlert(
            DataStorage,
            MonitoredRow,
            AlertName,
            NSLOCTEXT("MyTool", "CheckFailed", "The selected object has an error."),
            Columns::FAlertColumnType::Error,
            255 // 最高优先级
        );
    }
}

void FMyEditorTool::ClearAlert()
{
    if (MonitoredRow != InvalidRowHandle)
    {
        ICoreProvider& DataStorage = IModuleManager::Get().LoadModuleChecked<FTedsAlertsModule>(TEXT("TedsAlerts")).GetDataStorage();
        Alerts::RemoveAlert(DataStorage, MonitoredRow, AlertName);
    }
}
```

## 模块依赖

要使用 `TedsAlerts` 模块，你的 `.Build.cs` 文件需要添加以下依赖。注意，由于这是实验性插件，其模块依赖链可能较深。

| 模块 | 用途 |
|---|---|
| `EditorDataStorage` | 提供 TEDS 核心功能，如 `ICoreProvider`, `RowHandle` 等。 |
| `TedsAlerts` | 本模块，提供警报管理的公共API。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `c18be83c` | Enable the TEDS Outliner in Restricted UEFN | 在受限的 UEFN 环境中启用了 TEDS 大纲视图 |
| 2026-05-14 | `bd93e418` | Hide unloaded actor rows inside non-editing level instances from TEDS Outliner | 在 TEDS 大纲中隐藏非编辑关卡实例内未加载的 Actor 行 |
| 2026-05-14 | `bdc9e0ac` | [TedsOutliner] Fix invalid cross-level drag and drops | 修复了跨关卡拖放操作无效的问题 |
| 2026-05-14 | `6f329dd1` | [Backout] - CL53940377 | 回退了之前的变更 CL53940377 |
| 2026-05-14 | `ee0aab56` | Hide unloaded actor rows inside non-editing level instances from TEDS Outliner | 在 TEDS 大纲中隐藏非编辑关卡实例内未加载的 Actor 行 |

### 维护评价

- **活跃度**：**非常活跃**。该插件近期（2026年5月）有密集的提交，主要集中在 `TedsOutliner` 模块的功能完善和 bug 修复上。
- **状态**：**实验性（Experimental）**。`.uplugin` 文件中明确标记 `IsExperimentalVersion: true` 且 `EnabledByDefault: false`，表明这是一个前沿的、API 可能发生变化的实验性功能。
- **年龄**：插件创建于约 2 年前（2024年7月），对于一个实验性项目来说仍处于早期发展阶段。
- **推荐度**：**强烈推荐给编辑器扩展开发者和引擎开发人员**。如果你正在构建需要高性能数据查询的复杂编辑器UI，或者希望探索 TEDS 的未来方向，这是一个绝佳的学习和实验对象。但不建议在稳定的生产项目中直接依赖，因为其 API 随时可能变动。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorDataStorageFeatures)
- [官方文档](https://docs.unrealengine.com/) (暂无专用文档，建议参考 TEDS 和编辑器扩展的通用文档)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorDataStorageFeatures/Tests) (路径为推测，具体请查看插件内部)