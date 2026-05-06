# TEDS 调试器 (TedsDebugger)

> Experimental UI Features for the Editor, built on TEDS: Editor Data Storage.

| 属性 | 值 |
|---|---|
| 中文名 | TEDS 调试器 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容资产） |
| 模块 | `TedsDebugger` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-25 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EditorDataStorageFeatures) | |

## 用途

`TedsDebugger` 是 TEDS（Typed Element Data Storage）的交互式查询编辑与调试工具。它提供了一个 Slate 界面，允许开发者：

- 可视化构建 TEDS 查询条件（`Select`、`All`、`Any`、`None` 等操作符）。
- 实时查看查询结果的行、列及属性值。
- 切换表格视图与层级视图，支持排序与过滤。
- 检查行内存储的具体列数据，包括引用和 Slate 控件。

该模块是 TEDS 生态系统中的核心调试组件，用于理解数据流向、验证查询逻辑以及排查数据存储问题。

## 使用场景

- 你在开发基于 TEDS 的编辑器 UI 功能（如内容浏览器、大纲视图），需要实时验证查询是否正确返回预期行。
- 你需要排查某个 TEDS 查询的性能问题或逻辑错误，希望通过图形界面调整条件并观察结果。
- 你正在学习 TEDS 查询语法，希望直观地看到不同操作符组合的效果。
- 你需要在调试过程中查看特定行的完整列数据，包括自定义元数据。

## 蓝图用法

暂无蓝图暴露的 API。所有交互逻辑均在 C++ Slate 层实现，编辑器内通过 `Window > Developer Tools > TEDS Debugger` 菜单项启动。

## C++ 用法

### 头文件引入

```cpp
#include "TedsDebuggerModule.h"
#include "STedsDebugger.h"
```

### 基本用法

启动调试器选项卡（通常在模块启动时注册）：

```cpp
// 在模块 StartupModule 中注册 SpawnTab
FGlobalTabmanager::Get()->RegisterTabSpawner(
    "TedsDebugger",
    FOnSpawnTab::CreateLambda([](const FSpawnTabArgs& Args)
    {
        TSharedRef<SDockTab> DockTab = SNew(SDockTab)
            .TabRole(ETabRole::NomadTab);
        TSharedRef<UE::Editor::DataStorage::Debug::STedsDebugger> Debugger = 
            SNew(UE::Editor::DataStorage::Debug::STedsDebugger, DockTab, Args.GetOwnerWindow());
        DockTab->SetContent(Debugger);
        return DockTab;
    })
).SetDisplayName(NSLOCTEXT("TedsDebugger", "TabTitle", "TEDS Debugger"));
```

### 进阶用法

通过 `FTedsQueryEditorModel` 手动构造查询：

```cpp
using namespace UE::Editor::DataStorage;
// 获取 CoreProvider（通常来自其他模块）
ICoreProvider& DataStorage = ...;

Debug::QueryEditor::FTedsQueryEditorModel Model(DataStorage);
Model.Reset();

// 添加 Select 条件：选择包含特定列的行
auto Handle = Model.CreateEntry(QueryEditor::EOperatorType::Select);
Model.SetOperatorType(Handle, QueryEditor::EOperatorType::Select);
// 假设有一个 UObject 列，可以添加
Model.AddColumn(Handle, FExampleColumn::StaticStruct());

// 生成查询描述
FQueryDescription QueryDesc = Model.GenerateQueryDescription();
// 执行查询
QueryHandle Query = DataStorage.CreateQuery(QueryDesc);
```

## Demo 示例

以下示例展示如何在自定义模块中集成 `STedsDebugger` 作为独立控件（非选项卡形式）。

**TedsDebuggerDemoWidget.h**

```cpp
#pragma once
#include "Widgets/SCompoundWidget.h"
#include "DataStorage/Handles.h"

class SDockTab;
class SWindow;

namespace UE::Editor::DataStorage::Debug
{
    class STedsDebugger;

    class STedsDebuggerDemoWidget : public SCompoundWidget
    {
    public:
        SLATE_BEGIN_ARGS(STedsDebuggerDemoWidget) {}
        SLATE_END_ARGS()

        void Construct(const FArguments& InArgs);
    private:
        TSharedPtr<STedsDebugger> Debugger;
    };
}
```

**TedsDebuggerDemoWidget.cpp**

```cpp
#include "TedsDebuggerDemoWidget.h"
#include "STedsDebugger.h"
#include "Widgets/Docking/SDockTab.h"
#include "Framework/Docking/TabManager.h"

void STedsDebuggerDemoWidget::Construct(const FArguments& InArgs)
{
    // 模拟 SDockTab 环境（仅用于演示，实际请传入真实 Tab 和 Window）
    TSharedRef<SDockTab> DummyTab = SNew(SDockTab);
    TSharedPtr<SWindow> DummyWindow;

    ChildSlot
    [
        SAssignNew(Debugger, UE::Editor::DataStorage::Debug::STedsDebugger)
        (SNew(SDockTab), DummyWindow)
    ];
}
```

## 模块依赖

以下为 `TedsDebugger` 特有的依赖（省略常见 Core/Engine/Slate 模块）：

| 模块 | 用途 |
|---|---|
| `TypedElementDataStorage` | TEDS 核心接口，用于查询创建与行操作 |
| `TedsCore` | TEDS 基础设施，提供 `ICoreProvider` 等 |
| `TedsTableViewer` | 表格视图组件，用于显示查询结果 |
| `TedsUi` | TEDS UI 提供器，用于注册自定义控件构造器 |
| `TedsQueryStack` | 查询堆栈节点，支持层级切换 |
| `TedsTypeInfo` | 类型信息查询，用于获取列名等 |
| `WorkspaceMenuStructure` | 编辑器菜单结构，用于注册调试器菜单项 |

## 维护状态

### 近期更新

- 2025-10-14 267e8191 — Fix TedsType info assert when running certain Verse automated tests  
- 2025-10-02 1f8278e6 — Re-enable Teds AssetData after resolving test and FName issues  
- 2025-09-26 7d070444 — [TEDS Viewers] Allow Sorting to be persisted via IsEnabled and GetColumnSort functions  
- 2025-09-25 8d9818a1 — [TEDS Viewers] Create a new composite hierarchy viewer (include searching and filtering by default)  
- 2025-09-25 4161c053 — Add a new TEDSFilterBar Widget and add TedsFilters to the TableViewer module  

### 维护评价

该模块创建于 2025 年 9 月，属于全新实验性功能。近期更新频繁（几乎每天都有提交），集中在功能增强与稳定性修复上。由于是实验性版本，API 可能不稳定，但团队正在积极开发。**建议仅用于测试和功能评估，不宜用于生产环境**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EditorDataStorageFeatures/Source/TedsDebugger)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EditorDataStorageFeatures/Tests/TedsDebugger) (假设路径，实际可能位于 `Engine/Plugins/Experimental/EditorDataStorageFeatures/Tests`)