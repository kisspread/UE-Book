# TEDS: Editor Data Storage (TedsUI 模块)

> A central extendable data storage for editors and their corresponding data with support for viewing and editing through a collection of widgets.

| 属性 | 值 |
|---|---|
| 中文名 | TEDS UI 模块 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（内容资源） |
| 模块 | `TedsUI` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-19 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EditorDataStorage) | |

## 用途

TEDS（Typed Element Data Storage）是 Unreal Editor 的一种中央可扩展数据存储机制。TedsUI 模块为 TEDS 提供了基于 Slate 的 UI 组件系统，允许开发者注册自定义 Widget 构造器，用于在编辑器用户界面中直观地显示和编辑存储在 TEDS 中的各种列（Column）数据。本模块解决了如何将抽象的数据存储映射为可视、可交互的编辑器控件的问题。

## 使用场景

- 开发编辑器工具或面板（如内容浏览器、资源检视器），需要与 TEDS 数据系统集成。
- 需要为自定义 TEDS 列类型创建专用的显示/编辑控件（例如颜色选择器、URL 链接、世界名称标签等）。
- 希望利用 TEDS 的统一查询和 UI 注册机制，快速构建数据驱动的编辑器界面。

## 蓝图用法

本模块是 C++ 扩展层，**不暴露任何蓝图可调用（BlueprintCallable）函数或蓝图可读写（BlueprintReadWrite）属性给蓝图**。蓝图无法直接创建或配置 TedsUI 的 Widget 构造器，所有注册逻辑均需在 C++ 中完成。

## C++ 用法

### 头文件引入

```cpp
#include "TedsUIModule.h"
#include "Widgets/LabelWidget.h"
#include "Widgets/SlateColorWidget.h"
#include "Widgets/UrlWidget.h"
#include "Widgets/WorldWidget.h"
#include "Widgets/ExportedTextWidget.h"
#include "Widgets/PackagePathWidget.h"
#include "Widgets/GeneralWidgetRegistrationFactory.h"
#include "Processors/WidgetReferenceColumnUpdateProcessor.h"
```

### 基本用法

TedsUI 的核心机制是通过 `UEditorDataStorageFactory` 的子类来注册 Widget 构造器和 Widget 用途。在模块的 `StartupModule` 中，TedsUI 的 `FTedsUIModule` 会触发各工厂的注册。

**示例：注册一个自定义 Widget 构造器**

假设你已经有一个 TEDS 列类型 `FMyCustomColumn`，并希望为它创建一个简单的文本显示 Widget。

1. 创建一个 Widget 构造器结构体（继承 `FSimpleWidgetConstructor` 或 `FTypedElementWidgetConstructor`）：

```cpp
// MyCustomWidget.h
#pragma once

#include "Elements/Interfaces/TypedElementDataStorageFactory.h"
#include "Elements/Interfaces/TypedElementDataStorageUiInterface.h"
#include "MyCustomWidget.generated.h"

USTRUCT()
struct FMyCustomWidgetConstructor : public FSimpleWidgetConstructor
{
    GENERATED_BODY()

public:
    FMyCustomWidgetConstructor();
    virtual ~FMyCustomWidgetConstructor() override = default;

    virtual TSharedPtr<SWidget> CreateWidget(
        UE::Editor::DataStorage::ICoreProvider* DataStorage,
        UE::Editor::DataStorage::IUiProvider* DataStorageUi,
        UE::Editor::DataStorage::RowHandle TargetRow,
        UE::Editor::DataStorage::RowHandle WidgetRow,
        const UE::Editor::DataStorage::FMetaDataView& Arguments) override;
};
```

2. 实现该构造器：

```cpp
// MyCustomWidget.cpp
#include "MyCustomWidget.h"
#include "Widgets/Text/STextBlock.h"
#include "MyCustomColumn.h" // 假设你的列定义

FMyCustomWidgetConstructor::FMyCustomWidgetConstructor()
    : FSimpleWidgetConstructor(/* 列类型 UStruct 指针，例如 FMyCustomColumn::StaticStruct() */)
{
}

TSharedPtr<SWidget> FMyCustomWidgetConstructor::CreateWidget(
    UE::Editor::DataStorage::ICoreProvider* DataStorage,
    UE::Editor::DataStorage::IUiProvider* DataStorageUi,
    UE::Editor::DataStorage::RowHandle TargetRow,
    UE::Editor::DataStorage::RowHandle WidgetRow,
    const UE::Editor::DataStorage::FMetaDataView& Arguments)
{
    // 读取列数据并创建 Widget
    const FMyCustomColumn* Column = DataStorage->GetColumn<FMyCustomColumn>(TargetRow);
    if (!Column)
    {
        return SNullWidget::NullWidget;
    }
    return SNew(STextBlock).Text(FText::FromString(Column->MyString));
}
```

3. 注册构造器（通常在模块启动或工厂中）：

你需要创建一个继承 `UEditorDataStorageFactory` 的类，并在 `RegisterWidgetConstructors` 中调用 `DataStorageUi.RegisterWidgetConstructor`。

参考 `ULabelWidgetFactory` 的实现：

```cpp
// 出自 ULabelWidgetFactory::RegisterWidgetConstructors
void ULabelWidgetFactory::RegisterWidgetConstructors(
    UE::Editor::DataStorage::ICoreProvider& DataStorage,
    UE::Editor::DataStorage::IUiProvider& DataStorageUi) const
{
    // 注册标签 Widget 构造器，关联到某个列类型
    DataStorageUi.RegisterWidgetConstructor<FLabelWidgetConstructor>(DataStorage, /* 列类型 */);
}
```

### 进阶用法

**处理 Widget 引用列的生命周期**

`UWidgetReferenceColumnUpdateFactory` 提供了两个处理器：
- `RegisterDeleteRowOnWidgetDeleteQuery`：当引用的 Slate Widget 被销毁时，删除整个数据行。
- `RegisterDeleteColumnOnWidgetDeleteQuery`：当引用的 Slate Widget 被销毁时，仅删除该列。

这些处理器由系统自动触发，无需手动调用。如果你有自定义的 Widget 引用列，可以注册类似的查询。

**为不同目的注册 Widget**

`UGeneralWidgetRegistrationFactory` 注册了两个通用的 Widget 用途：
- `LargeCellPurpose`：用于大单元格（通常是主要显示区域）。
- `HeaderPurpose`：用于表头。

这些用途允许同一列在不同上下文中显示不同的 Widget（例如，表格列头显示简短标签，单元格显示完整内容）。

**示例：注册一个自定义用途**

```cpp
// 在你的工厂类的 RegisterWidgetPurposes 中
void UMyCustomFactory::RegisterWidgetPurposes(UE::Editor::DataStorage::IUiProvider& DataStorageUi) const
{
    static const FName MyPurpose = TEXT("MyCustomPurpose");
    // 可以注册一个目的，然后 Widget 构造器可以根据目的调整行为
}
```

## Demo 示例

以下是一个完整的、可编译的最小示例，演示如何为自定义列创建 Widget 并注册。

### MyCustomColumn.h

```cpp
#pragma once

#include "Elements/Interfaces/TypedElementDataStorageInterface.h"
#include "UObject/ObjectMacros.h"
#include "MyCustomColumn.generated.h"

USTRUCT(meta = (DisplayName = "My Custom Column"))
struct FMyCustomColumn : public FEditorDataStorageColumn
{
    GENERATED_BODY()

    UPROPERTY()
    FString Name;
};
```

### MyCustomWidget.h

```cpp
#pragma once

#include "Elements/Interfaces/TypedElementDataStorageFactory.h"
#include "Elements/Interfaces/TypedElementDataStorageUiInterface.h"
#include "MyCustomWidget.generated.h"

USTRUCT()
struct FMyCustomWidgetConstructor : public FSimpleWidgetConstructor
{
    GENERATED_BODY()
public:
    FMyCustomWidgetConstructor();
    virtual ~FMyCustomWidgetConstructor() override = default;

    virtual TSharedPtr<SWidget> CreateWidget(
        UE::Editor::DataStorage::ICoreProvider* DataStorage,
        UE::Editor::DataStorage::IUiProvider* DataStorageUi,
        UE::Editor::DataStorage::RowHandle TargetRow,
        UE::Editor::DataStorage::RowHandle WidgetRow,
        const UE::Editor::DataStorage::FMetaDataView& Arguments) override;
};
```

### MyCustomWidget.cpp

```cpp
#include "MyCustomWidget.h"
#include "MyCustomColumn.h"
#include "Widgets/Text/STextBlock.h"

FMyCustomWidgetConstructor::FMyCustomWidgetConstructor()
    : FSimpleWidgetConstructor(FMyCustomColumn::StaticStruct())
{
}

TSharedPtr<SWidget> FMyCustomWidgetConstructor::CreateWidget(
    UE::Editor::DataStorage::ICoreProvider* DataStorage,
    UE::Editor::DataStorage::IUiProvider* DataStorageUi,
    UE::Editor::DataStorage::RowHandle TargetRow,
    UE::Editor::DataStorage::RowHandle WidgetRow,
    const UE::Editor::DataStorage::FMetaDataView& Arguments)
{
    const FMyCustomColumn* Column = DataStorage->GetColumn<FMyCustomColumn>(TargetRow);
    if (!Column)
    {
        return SNullWidget::NullWidget;
    }
    return SNew(STextBlock).Text(FText::FromString(Column->Name));
}
```

### MyCustomFactory.h

```cpp
#pragma once

#include "Elements/Interfaces/TypedElementDataStorageFactory.h"
#include "MyCustomFactory.generated.h"

UCLASS()
class UMyCustomFactory : public UEditorDataStorageFactory
{
    GENERATED_BODY()
public:
    virtual void RegisterWidgetConstructors(
        UE::Editor::DataStorage::ICoreProvider& DataStorage,
        UE::Editor::DataStorage::IUiProvider& DataStorageUi) const override;
};
```

### MyCustomFactory.cpp

```cpp
#include "MyCustomFactory.h"
#include "MyCustomWidget.h"

void UMyCustomFactory::RegisterWidgetConstructors(
    UE::Editor::DataStorage::ICoreProvider& DataStorage,
    UE::Editor::DataStorage::IUiProvider& DataStorageUi) const
{
    DataStorageUi.RegisterWidgetConstructor<FMyCustomWidgetConstructor>(DataStorage, FMyCustomColumn::StaticStruct());
}
```

## 模块依赖

使用 `TedsUI` 模块时，你的模块的 `Build.cs` 需要依赖以下独特模块（省略标准依赖）：

| 模块 | 用途 |
|---|---|
| `TedsCore` | TEDS 核心数据存储与查询接口 |
| `EditorWidgets` | 某些 Widget 构造器可能用到的编辑器通用控件 |

其余依赖为常见模块（Core、CoreUObject、Engine、Slate、SlateCore、UMG、InputCore 等），此处不赘述。

## 维护状态

### 近期更新

- 2025-08-21 `58836292` 修复注销命令中的空指针保护
- 2025-08-21 `80aef2fc` 在反初始化时释放环境引用
- 2025-08-20 `881afb9e` 在 FEnvironment 析构函数中清理待处理命令
- 2025-08-19 `d054c8d3` [TEDS] 添加协同时间切片基本支持
- 2025-08-19 `5273c342` TEDS 层级：SetParent 改变层级时正确触发

### 维护评价

该模块于 **2025 年 8 月** 创建，目前仍处于 **活跃开发** 阶段。从提交记录看，几乎每天都有实质性更新，涉及功能增强和稳定性修复。插件标注为实验性（`IsExperimentalVersion = true`），API 和行为可能频繁变更。**强烈建议仅用于学习或实验性项目**，生产环境使用需谨慎。无已知的废弃或性能警告。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EditorDataStorage)
- [TEDS 官方文档](https://docs.unrealengine.com/5.7/en-US/editor-data-storage/)（假设存在）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EditorDataStorage/Tests)（若存在）