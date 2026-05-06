# TedsEverythingPicker

> Experimental UI Features for the Editor, built on TEDS: Editor Data Storage.

| 属性 | 值 |
|---|---|
| 中文名 | 通用拾取器 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（Slate UI控件、查询上下文） |
| 模块 | `TedsEverythingPicker` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-25 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EditorDataStorageFeatures/Source/TedsEverythingPicker) | |

## 用途

该模块提供了一个**通用的“选择任何东西”的拾取器 UI 控件**，基于 TEDS（Editor Data Storage）数据层构建。它允许用户在编辑器中选择任意类型的对象、资源或数据行，并通过可插拔的上下文视图（Context View）进行限定的选择。

主要解决以下问题：
- 在复杂的编辑器工作流中，需要一种统一的、可扩展的方式让用户选择“某样东西”，而无需为每种类型单独编写拾取对话框。
- 结合 TEDS 查询栈（QueryStack），可以实现高效的数据过滤、排序和复合视图（如同时显示对象引用和类型列表）。

## 使用场景

- 在编辑器工具中，需要让用户选择一个**UObject 引用**（例如选择一个材质、蓝图或 Actor）。
- 需要让用户从 TEDS 数据存储中选择一个**特定类型的所有行**（例如选择所有具有某个标签的组件）。
- 构建自定义面板，让用户通过**多个上下文标签页**（比如“对象引用”和“类型列表”）切换选择。

## 蓝图用法

该控件是纯 Slate 实现，**不暴露任何蓝图可调用函数或属性**。所有配置均在 C++ 构造函数或 Slate 声明中完成。

## C++ 用法

### 头文件引入

```cpp
#include "Widgets/SEverythingPicker.h"
#include "Context/TedsPickerContext.h"
#include "Context/TedsPickerContextUtil.h" // 提供 SObjectReferenceContextView 和 STypeListContextView
```

### 基本用法：创建并显示一个通用拾取器

```cpp
// 创建一个包含两个上下文标签页的拾取器：对象引用和类型列表
using namespace UE::Editor::DataStorage::Picker;

// 准备查询描述（示例：选择所有具有 FClassTypeInfoTag 的行）
FQueryDescription ClassQuery;
// ... 构建查询（详细见 TedsQueryStack 文档）

// 创建拾取器
SNew(SEverythingPicker)
+ SEverythingPicker::Context()
    .Label(INVTEXT("Object Reference"))
    .OnMakeWidget_Lambda([&]()
    {
        return SNew(SObjectReferenceContextView)
            .Query(ClassQuery)
            .SearchingEnabled(true)
            .OnSelectionChanged_Lambda([](RowHandle SelectedRow)
            {
                // 处理选择
            });
    })
+ SEverythingPicker::Context()
    .Label(INVTEXT("Type List"))
    .OnMakeWidget_Lambda([&]()
    {
        return SNew(STypeListContextView)
            .BaseType(UStaticMeshComponent::StaticClass())
            .SearchingEnabled(true)
            .OnSelectionChanged_Lambda([](RowHandle SelectedRow) {});
    })
```

### 进阶用法：自定义 QueryStack

```cpp
// 使用 IRowNode 构建更复杂的查询
#include "TedsQueryStackInterfaces.h"
using namespace UE::Editor::DataStorage::QueryStack;

// 创建一个节点链：从所有 Actor 中筛选出具有特定组件的
TSharedPtr<IRowNode> Node = 
    FRowFilterNode::Create()
    ->And(TedsPickersQueryFilter::MakeFilter_ObjectTypes({ AActor::StaticClass() }))
    ->And(TedsPickersQueryFilter::MakeFilter_TagPresent(TEXT("MyCustomTag")));

// 然后将 Node 传递给 SObjectReferenceContextView
SNew(SObjectReferenceContextView)
    .QueryStack(Node)
    .SearchingEnabled(true)
    .OnSelectionChanged(MyDelegate)
```

## Demo 示例

以下是一个完整的编辑器模块示例，注册一个工具栏按钮，点击后弹出拾取器对话框：

```cpp
// TedsEverythingPickerDemo.h
#pragma once
#include "CoreMinimal.h"
#include "Modules/ModuleInterface.h"

class FTedsEverythingPickerDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

```cpp
// TedsEverythingPickerDemo.cpp
#include "TedsEverythingPickerDemo.h"
#include "Widgets/SEverythingPicker.h"
#include "Context/TedsPickerContextUtil.h"
#include "Framework/Application/SlateApplication.h"
#include "Widgets/SWindow.h"

void FTedsEverythingPickerDemoModule::StartupModule()
{
    // 注册一个简单的命令（通过 Editor 扩展）
    // 此处省略命令注册，仅展示创建窗口的代码

    TSharedRef<SWindow> PickerWindow = SNew(SWindow)
        .Title(INVTEXT("Everything Picker"))
        .ClientSize(FVector2D(600, 400))
        .Content()
        [
            SNew(UE::Editor::DataStorage::Picker::SEverythingPicker)
            + UE::Editor::DataStorage::Picker::FPickerContext::FSlotArguments() // 注意实际语法
        ];

    FSlateApplication::Get().AddWindow(PickerWindow);
}

void FTedsEverythingPickerDemoModule::ShutdownModule() {}
```

> 注意：上述代码为语法示意，实际使用时需根据最新的 Slate 声明方式调整。建议参考 Plugin 源码中的 Test 或 Example 文件。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `TedsCore` | 提供 TEDS 数据存储基础类型和行句柄 |
| `TedsUI` | 提供基础 UI 控件（如 `ITedsTableViewer`） |
| `TedsQueryStack` | 提供查询栈节点和过滤机制 |
| `TedsTypedElementBridge` | 支持 TypedElement 桥接（可间接依赖） |
| `SlateCore` / `Slate` | UI 框架（已省略在常见依赖中） |

**注意**：使用本模块时无需额外添加自己的 `PublicDependencyModuleNames`，在 `.Build.cs` 中引入 `TedsEverythingPicker` 即可自动包含上述依赖。

## 维护状态

### 近期更新

- 2025-10-14 `267e8191` Fix TedsType info assert when running certain Verse automated tests
- 2025-10-02 `1f8278e6` Re-enable Teds AssetData after resolving test and FName issues
- 2025-09-26 `7d070444` [TEDS Viewers] Allow Sorting to be persisted via IsEnabled and GetColumnSort functions
- 2025-09-25 `8d9818a1` [TEDS Viewers] Create a new composite hierarchy viewer (include searching and filtering by default)
- 2025-09-25 `4161c053` Add a new TEDSFilterBar Widget and add TedsFilters to the TableViewer module

### 维护评价

- **创建时间**：2025-09-25（不到 1 年）
- **近期更新频率**：高速迭代，几乎每周都有功能性更新（修复、新控件、持久化排序等）
- **活跃度**：非常活跃，属实验性早期开发阶段，Epic 频繁提交
- **已知问题/限制**：
  - API 仍在快速变化，不保证向后兼容
  - 仅限编辑器使用，不可在运行时打包
  - 文档和示例较少，需要参考源码
- **推荐使用**：如果你是 TEDS 生态的早期采用者或需要构建复杂编辑器拾取交互，可以尝试使用，但需要准备应对 API 变动。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EditorDataStorageFeatures/Source/TedsEverythingPicker)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EditorDataStorageFeatures/Tests/TedsEverythingPicker)（可能不存在，需自行查阅）