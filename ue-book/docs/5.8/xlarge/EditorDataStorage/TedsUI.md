# TEDS: Editor Data Storage (TedsUI 模块)

> A central extendable data storage for editors and their corresponding data with support for viewing and editing through a collection of widgets.

| 属性 | 值 |
|---|---|
| 中文名 | 编辑器数据存储 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `TedsCore` (UncookedOnly), `TedsUI` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-07-27 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorDataStorage) | |

## 用途

TEDS（Typed Element Data Storage）是 UE5 编辑器框架中一套**集中式可扩展数据存储系统**，用于统一管理和展示编辑器中的各种数据。TedsUI 模块是 TEDS 的 UI 层，提供了一套**Widget 工厂系统**，能够将存储在 TEDS 中的行数据（Row）自动转换为可交互的 Slate 控件进行查看和编辑。

核心设计理念是**数据驱动的 UI 生成**：每种数据类型（文本、路径、URL、颜色等）通过 Factory + WidgetConstructor 模式自动注册对应的显示控件，编辑器无需手动为每种数据类型编写 UI 代码。

## 使用场景

- 你在开发编辑器面板，需要**统一展示多种类型的数据**（资产路径、颜色、URL 等）→ 用 TEDS + TedsUI
- 你需要一个**可扩展的数据存储框架**，让不同模块注册自己的数据列和显示控件 → 用 TEDS
- 你在构建 **Chaos Visual Debugger** 等工具的编辑器界面 → TEDS 是推荐后端
- 你需要**按查询条件自动匹配并显示控件** → TedsUI 的 WidgetConstructor 查询系统

## 蓝图用法

TedsUI 是纯 C++ 编辑器模块，主要通过 **Unreal 反射系统**（UFactory 自动注册）工作，不暴露 BlueprintCallable 节点。开发者通过 C++ 继承基类来扩展。

## C++ 用法

### 头文件引入

```cpp
// Widget 工厂基类
#include "Widgets/GeneralWidgetRegistrationFactory.h"
#include "Widgets/LabelWidget.h"
#include "Widgets/ExportedTextWidget.h"
#include "Widgets/PackagePathWidget.h"
```

### 核心扩展模式

TedsUI 采用 **Factory + Constructor** 两层模式：

1. **Factory（工厂）**：继承 `UEditorDataStorageFactory`，负责注册 WidgetConstructor
2. **Constructor（构造器）**：继承 `FSimpleWidgetConstructor` 或 `FTypedElementWidgetConstructor`，负责创建具体控件

#### 自定义 Widget Factory

```cpp
// 参考源码：Public/Widgets/LabelWidget.h
UCLASS()
class UMyWidgetFactory : public UEditorDataStorageFactory
{
    GENERATED_BODY()

public:
    // 注册 Widget 构造器
    virtual void RegisterWidgetConstructors(
        UE::Editor::DataStorage::ICoreProvider& DataStorage,
        UE::Editor::DataStorage::IUiProvider& DataStorageUi) const override;

    // 注册 Widget 用途标签（如大单元格、表头等）
    virtual void RegisterWidgetPurposes(
        UE::Editor::DataStorage::IUiProvider& DataStorageUi) const override;
};
```

#### 自定义 Widget Constructor

```cpp
// 参考源码：Public/Widgets/ExportedTextWidget.h
USTRUCT()
struct FMyWidgetConstructor : public FSimpleWidgetConstructor
{
    GENERATED_BODY()

public:
    FMyWidgetConstructor();

    // 声明此控件需要的附加数据列
    virtual TConstArrayView<const UScriptStruct*> GetAdditionalColumnsList() const override;

    // 查询条件：决定哪些行适用此控件
    virtual const UE::Editor::DataStorage::Queries::FConditions* GetQueryConditions(
        const UE::Editor::DataStorage::ICoreProvider* Storage) const override;

    // 创建显示名称文本
    virtual FText CreateWidgetDisplayNameText(
        UE::Editor::DataStorage::ICoreProvider* DataStorage,
        UE::Editor::DataStorage::RowHandle Row) const override;

    // 创建控件
    virtual TSharedPtr<SWidget> CreateWidget(
        UE::Editor::DataStorage::ICoreProvider* DataStorage,
        UE::Editor::DataStorage::IUiProvider* DataStorageUi,
        UE::Editor::DataStorage::RowHandle TargetRow,
        UE::Editor::DataStorage::RowHandle WidgetRow,
        const UE::Editor::DataStorage::FMetaDataView& Arguments) override;
};
```

## Demo 示例

### 自定义数据列的 Widget Constructor

```cpp
// MyWidget.h
#pragma once

#include "Widgets/ExportedTextWidget.h"
#include "UObject/ObjectMacros.h"

// 定义一个自定义数据列
USTRUCT()
struct FMyCustomDataColumn
{
    GENERATED_BODY()

    UPROPERTY()
    FString DisplayValue;

    UPROPERTY()
    int32 Priority = 0;
};

// 注册标签（用于标识使用此控件的行）
USTRUCT(meta = (DisplayName = "My custom widget"))
struct FMyCustomWidgetTag : public FEditorDataStorageTag
{
    GENERATED_BODY()
};

// Widget 构造器
USTRUCT()
struct FMyCustomWidgetConstructor : public FSimpleWidgetConstructor
{
    GENERATED_BODY()

public:
    FMyCustomWidgetConstructor();
    virtual ~FMyCustomWidgetConstructor() override = default;

    virtual TConstArrayView<const UScriptStruct*> GetAdditionalColumnsList() const override;

    virtual TSharedPtr<SWidget> CreateWidget(
        UE::Editor::DataStorage::ICoreProvider* DataStorage,
        UE::Editor::DataStorage::IUiProvider* DataStorageUi,
        UE::Editor::DataStorage::RowHandle TargetRow,
        UE::Editor::DataStorage::RowHandle WidgetRow,
        const UE::Editor::DataStorage::FMetaDataView& Arguments) override;
};
```

```cpp
// MyWidget.cpp
#include "MyWidget.h"
#include "Elements/Framework/TypedElementList.h"

FMyCustomWidgetConstructor::FMyCustomWidgetConstructor()
{
}

TConstArrayView<const UScriptStruct*> FMyCustomWidgetConstructor::GetAdditionalColumnsList() const
{
    // 声明此控件需要 FMyCustomDataColumn 列
    static const UScriptStruct* Columns[] = {
        FMyCustomDataColumn::StaticStruct()
    };
    return Columns;
}

TSharedPtr<SWidget> FMyCustomWidgetConstructor::CreateWidget(
    UE::Editor::DataStorage::ICoreProvider* DataStorage,
    UE::Editor::DataStorage::IUiProvider* DataStorageUi,
    UE::Editor::DataStorage::RowHandle TargetRow,
    UE::Editor::DataStorage::RowHandle WidgetRow,
    const UE::Editor::DataStorage::FMetaDataView& Arguments)
{
    // 从数据存储读取列数据
    if (const FMyCustomDataColumn* Data = DataStorage->GetColumn<FMyCustomDataColumn>(TargetRow))
    {
        return SNew(STextBlock)
            .Text(FText::FromString(Data->DisplayValue));
    }
    return SNew(STextBlock).Text(FText::FromString(TEXT("No Data")));
}

// 工厂：自动注册到 TEDS
UCLASS()
class UMyCustomWidgetFactory : public UEditorDataStorageFactory
{
    GENERATED_BODY()

public:
    virtual void RegisterWidgetConstructors(
        UE::Editor::DataStorage::ICoreProvider& DataStorage,
        UE::Editor::DataStorage::IUiProvider& DataStorageUi) const override
    {
        DataStorageUi.RegisterWidgetConstructor<FMyCustomWidgetConstructor>(
            DataStorage, DataStorageUi);
    }
};
```

## 模块依赖

TedsUI 的实际 Build.cs 依赖需从源码确认，基于代码分析的已知依赖：

| 模块 | 用途 |
|---|---|
| `TedsCore` | TEDS 核心数据存储引擎（ICoreProvider, RowHandle, Queries 等） |
| `TypedElementFramework` | 类型化元素框架（FTypedElementWidgetConstructor 基类） |
| `TypedElementRuntime` | 类型化元素运行时（FEditorDataStorageTag） |

> 注：CableComponent 等标准依赖已省略。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `cc577021` | Fix race condition in TEDS Dynamic Column Generation | 修复动态列生成的竞态条件 |
| 2026-04-16 | `419974fc` | [TEDS] Fixed incorrect pre-check before calling `AddCompositionToEntity_GetDelta`. | 修复调用 AddCompositionToEntity 前的错误前置检查 |
| 2026-04-16 | `dfebe6ae` | [TEDS] Add Filter Config to allow filtering to continue if a row is hit that fails VerifyColumns | 添加过滤配置：列验证失败时允许过滤继续执行 |
| 2026-04-14 | `b78fe9c6` | [TEDS] Deprecated `CurrentRowHasColumns` and `CurrentBatchTableHasColumns` in favor of `CurrentTable...` | 废弃旧列检查 API，迁移到新接口 |
| 2026-04-14 | `86eacb4b` | [TEDS] Fixed the result counter in FQueryResult not being atomic. | 修复 FQueryResult 结果计数器的原子性问题 |

### 维护评价

**活跃维护中** 🔥

- 插件创建于 2024-07-27，约 2 年历史
- 最近更新密集（2026-04 至 2026-05 连续修复和改进）
- 持续修复竞态条件、API 改进（废弃旧接口）和过滤功能增强
- 标记为 `IsExperimentalVersion=true`，仍处于实验阶段
- 作为 ChaosVisualDebugger 的支持程序之一，有明确的内部使用场景

⚠️ **注意**：虽然积极维护，但 API 尚不稳定（近期有废弃 API 的改动），生产环境使用需谨慎。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorDataStorage)
- TedsCore 模块文档（如已生成）
- TypedElementFramework 插件文档