# TEDS Editor Data Storage Features

> Experimental UI Features for the Editor, built on TEDS: Editor Data Storage.

| 属性 | 值 |
|---|---|
| 中文名 | TEDS编辑器数据存储功能 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器UI功能框架） |
| 模块 | `TedsActorCompatibility` (Runtime), `TedsAlerts` (Runtime), `TedsAssetData` (Runtime), `TedsContentBrowser` (Runtime), `TedsDebugger` (Runtime), `TedsEditorCompatibility` (Runtime), `TedsEverythingPicker` (Runtime), `TedsOperations` (Runtime), `TedsOutliner` (Runtime), `TedsPropertyEditor` (Runtime), `TedsQueryStack` (Runtime), `TedsRevisionControl` (Runtime), `TedsSettings` (Runtime), `TedsTableViewer` (Runtime), `TedsTypeInfo` (Runtime), `TedsTypedElementBridge` (Runtime), `UnifiedFavorites` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-07-27 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorDataStorageFeatures) | |

## 用途

EditorDataStorageFeatures 插件是一个基于 TEDS (Editor Data Storage) 构建的编辑器 UI 功能集合。它并不是一个单一的、面向最终用户的功能插件，而是一个为其他编辑器 UI 组件（如大纲视图、内容浏览器、拖放系统等）提供底层、可扩展操作系统的框架。

其核心思想是**数据驱动**。编辑器中的各种操作（如拖放、删除、应用变更）被抽象为可注册到特定“操作系统”（如 `UDropOperationSystem`, `UDeletionOperationSystem`）中的“操作”（Operations）。这些操作系统根据输入的数据行（Rows），探查（Probe）、测试（Test）并执行（Apply）合适的操作。这使得编辑器功能更加模块化和可扩展，允许开发者通过添加新的“操作”来扩展或自定义编辑器行为，而无需修改核心 UI 代码。

## 使用场景

- **编辑器开发**：你需要为自定义编辑器工具实现标准化的、可扩展的拖放功能。
- **自定义资产工作流**：你希望扩展内容浏览器的拖放行为，以处理特定类型的资产或自定义数据。
- **批量操作**：你需要为“大纲视图”或资产视图中的元素实现复杂的批量删除或应用逻辑。
- **扩展引擎功能**：你想为引擎现有的编辑器 UI（如关卡编辑器视口）添加新的、数据驱动的交互行为。

## 蓝图用法

当前提供的源码文件（主要为 `TedsOperations` 模块）中未发现标记为 `BlueprintCallable` 或 `BlueprintReadWrite` 的函数。该插件的功能主要在 C++ 层面提供，用于构建和扩展编辑器框架。

## C++ 用法

该插件的核心是可扩展的操作系统。以下是基于源码分析的使用模式。

### 核心类

| 类 | 说明 |
|---|---|
| `UOperationSystem` | 操作系统基类。用于管理一组针对特定目的（如删除、拖放）的操作。 |
| `UDropOperationSystem` | 拖放操作系统的具体实现。 |
| `UDeletionOperationSystem` | 删除操作系统的具体实现。 |
| `FWidgetDropHandler` | 基于 TEDS 操作处理 UI Widget 拖放事件的工具类。 |
| `FViewportDropHandler` | 针对视口（Viewport）的拖放处理器，支持预览。 |

### 头文件引入

```cpp
#include "TedsOperationSystem.h"
#include "DragAndDrop/DropOperationSystem.h"
#include "DragAndDrop/Widgets/WidgetDropHandler.h"
#include "DragAndDrop/DropOperationInput.h" // 包含操作输入相关的列定义
```

### 基本用法：注册自定义操作

你可以创建一个 `UOperationSystem` 的子类，并向其中注册操作。

```cpp
// (示例，基于源码类推断，非来自特定测试用例)
// 1. 创建一个自定义的操作系统
UCLASS()
class UMyAssetDropOperationSystem : public UDropOperationSystem
{
    GENERATED_BODY()
public:
    UMyAssetDropOperationSystem();
    virtual void RegisterQueries(UE::Editor::DataStorage::ICoreProvider& Storage) override;
};

// 2. 在操作系统初始化时，注册操作
void UMyAssetDropOperationSystem::RegisterQueries(UE::Editor::DataStorage::ICoreProvider& Storage)
{
    Super::RegisterQueries(Storage);

    // 注册一个能处理特定资产类型拖放的操作
    AddOperation(
        TEXT("MyAssetDrop"), // 操作名称
        // Apply 回调：执行拖放逻辑
        [this](UE::Editor::DataStorage::ICoreProvider& Storage, UE::Editor::DataStorage::RowHandle InputRow) -> TOptional<UE::Editor::DataStorage::Operations::FResult>
        {
            // 获取输入数据
            auto* NameCol = Storage.GetColumn<UE::Editor::DataStorage::Operations::FDropNameColumn>(InputRow);
            if (NameCol)
            {
                // ... 执行资产放置逻辑 ...
                UE_LOG(LogTemp, Log, TEXT("Dropping asset: %s"), *NameCol->Value.ToString());
                return UE::Editor::DataStorage::Operations::FResult{}; // 返回成功结果
            }
            return {}; // 返回空表示失败
        },
        // Test 回调：检查操作是否能执行（可选）
        [this](UE::Editor::DataStorage::ICoreProvider& Storage, UE::Editor::DataStorage::RowHandle InputRow) -> bool
        {
            // 检查输入是否符合要求，例如是否有名字列
            return Storage.HasColumns<UE::Editor::DataStorage::Operations::FDropNameColumn>(InputRow);
        },
        // Probe 回调：轻量级探查，判断操作是否可能接受此输入（可选）
        [this](const UE::Editor::DataStorage::ICoreProvider& Storage, UE::Editor::DataStorage::RowHandle InputRow) -> bool
        {
            // 返回 true 表示愿意接受此输入
            return true;
        },
        100 // 优先级，数字越小越优先
    );
}
```

### 进阶用法：处理视口拖放

使用 `FViewportDropHandler` 来处理视口中的拖放事件。

```cpp
// (示例，基于 FViewportDropHandler 和 FWidgetDropHandler 的源码)
// 1. 在你的视口客户端（如自定义的FEditorViewportClient）中，持有处理器指针。
TSharedPtr<UE::Editor::FViewportDropHandler> MyDropHandler;

// 2. 初始化
void SMyViewport::Construct(const FArguments& InArgs)
{
    // ... 其他构造代码 ...
    // 创建视口拖放处理器
    MyDropHandler = MakeShared<UE::Editor::FViewportDropHandler>(
        EditorViewportClient,
        [WeakThis = TWeakPtr<SMyViewport>(SharedThis(this))](const FEditorViewportClient& ViewportClient) -> UE::Editor::DataStorage::RowHandle
        {
            // 返回一个“默认”的拖放目标行，例如当前关卡
            if (auto This = WeakThis.Pin())
            {
                // ... 获取目标行逻辑 ...
            }
            return UE::Editor::DataStorage::InvalidRowHandle;
        }
    );
}

// 3. 将 UI 事件转发给处理器
FReply SMyViewport::OnDrop(const FGeometry& MyGeometry, const FDragDropEvent& DragDropEvent)
{
    if (MyDropHandler.IsValid())
    {
        return MyDropHandler->OnDrop(MyGeometry, DragDropEvent);
    }
    return FReply::Unhandled();
}
```

## Demo 示例

由于该插件主要是底层框架，直接可用的示例是注册一个简单的删除操作。

```cpp
// MyDeletionOperation.h
#pragma once
#include "CoreMinimal.h"
#include "Deletion/DeletionOperationSystem.h"

class FMySimpleDeletionOperation
{
public:
    static void Register(UE::Editor::DataStorage::ICoreProvider& Storage, UDeletionOperationSystem& DeletionSystem);
};
```

```cpp
// MyDeletionOperation.cpp
#include "MyDeletionOperation.h"
#include "Deletion/DeletionOperationInput.h"
#include "TedsOperationInput.h"

void FMySimpleDeletionOperation::Register(UE::Editor::DataStorage::ICoreProvider& Storage, UDeletionOperationSystem& DeletionSystem)
{
    // 注册一个简单的“警告并删除”操作
    DeletionSystem.AddOperation(
        TEXT("WarnAndDelete"),
        // Apply 回调
        [](UE::Editor::DataStorage::ICoreProvider& Storage, UE::Editor::DataStorage::RowHandle InputRow) -> TOptional<UE::Editor::DataStorage::Operations::FResult>
        {
            // 获取要删除的源数据行
            auto* SourceCol = Storage.GetColumn<UE::Editor::DataStorage::Operations::FSourceColumn>(InputRow);
            if (SourceCol && SourceCol->Value != UE::Editor::DataStorage::InvalidRowHandle)
            {
                // 尝试获取描述并打印警告
                auto* DescCol = Storage.GetColumn<UE::Editor::DataStorage::Operations::FDescriptionColumn>(InputRow);
                FText Description = DescCol ? DescCol->Value : FText::FromString(TEXT("Unknown Object"));
                UE_LOG(LogTemp, Warning, TEXT("SimpleDeletion: Deleting %s"), *Description.ToString());

                // 返回结果，标记删除的行（实际的删除逻辑需要在其他地方执行，如TEDS系统）
                UE::Editor::DataStorage::Operations::FResult Result;
                Result.Removed.Add(SourceCol->Value);
                return Result;
            }
            return {};
        },
        // Test 回调：总是允许
        [](UE::Editor::DataStorage::ICoreProvider&, UE::Editor::DataStorage::RowHandle) -> bool { return true; },
        // Probe 回调：总是接受
        [](const UE::Editor::DataStorage::ICoreProvider&, UE::Editor::DataStorage::RowHandle) -> bool { return true; },
        50 // 优先级
    );
}
```

## 模块依赖

该插件由多个模块组成，依赖关系复杂。要使用其中的功能（例如 `TedsOperations` 模块），你的模块通常需要依赖：

| 模块 | 用途 |
|---|---|
| `EditorDataStorageFeatures` | 该插件提供的所有功能基础 |
| `TypedElementFramework` | TEDS 操作系统依赖的类型化元素框架 |
| `EditorDataStorage` | 核心的 TEDS 存储提供程序接口 |
| `DataStorage` | TEDS 底层数据存储实现 |

*注意：具体依赖取决于你使用哪个子模块的功能。上述为常见依赖，需根据实际 `Build.cs` 文件确认。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `c18be83c` | Enable the TEDS Outliner in Restricted UEFN | 在限制性UEFN环境中启用TEDS大纲视图 |
| 2026-05-14 | `bd93e418` | Hide unloaded actor rows inside non-editing level instances from TEDS Outliner | 从TEDS大纲中隐藏未加载的Actor行 |
| 2026-05-14 | `bdc9e0ac` | [TedsOutliner] Fix invalid cross-level drag and drops | 修复大纲中无效的跨关卡拖放 |
| 2026-05-14 | `6f329dd1` | [Backout] - CL53940377 | 回退更改 |
| 2026-05-14 | `ee0aab56` | Hide unloaded actor rows inside non-editing level instances from TEDS Outliner | 从TEDS大纲中隐藏未加载的Actor行 |

### 维护评价

该插件创建于 **2024年7月**，是一个非常年轻的实验性插件。从近期提交看，**主要维护活动集中在 `TedsOutliner` 等上层UI模块**，而核心的 `TedsOperations` 框架近期无显著更新。所有模块均为 `Runtime` 类型，且插件整体标记为实验性。

**结论**：该插件作为实验性基础设施处于**积极维护**中，但上层功能的迭代速度可能快于底层操作系统的稳定性改进。其设计允许灵活扩展，但作为实验性插件，API 和设计可能会发生变化。**推荐用于编辑器扩展的研究和原型开发，但暂不建议在需要长期稳定的生产项目中作为核心依赖。**

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorDataStorageFeatures)
- [官方文档]()（暂无）
- [测试用例]()（在提供的源码信息中未发现该插件专属的测试文件路径）