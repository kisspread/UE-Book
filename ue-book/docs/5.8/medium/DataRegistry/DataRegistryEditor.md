# Data Registry

> Adds Data Registry system that can be used as a generic interface for acquiring structure data from multiple sources at runtime

| 属性 | 值 |
|---|---|
| 中文名 | 数据注册表 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DataRegistry` (Runtime), `DataRegistryEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-01-08 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/DataRegistry) | |

## 用途

Data Registry 是一个运行时数据获取的统一抽象层。它解决了以下问题：

- **多数据源统一接口**：游戏中的结构体数据可能来自 DataTable、GameplayTag 资产、或其他自定义源，Data Registry 提供了统一的 `FDataRegistryId` 来标识数据条目，屏蔽底层数据源差异
- **运行时按需获取**：数据不是一次性全部加载，而是通过 `UDataRegistrySubsystem` 在运行时按需获取（acquire），支持异步获取和状态回调
- **灵活的数据映射**：每个 Data Registry 资产关联一个 `UScriptStruct`，并可配置多个数据源（Source），运行时按优先级依次查找

简而言之，它是 DataTable 的高级替代方案，适用于需要从多种来源动态解析结构体数据的场景。

## 使用场景

- 你需要一个物品属性系统，但物品数据分散在多个 DataTable 或其他资产中 → 用 Data Registry 统一获取
- 你希望运行时动态解析数据，而不是一次性加载整个 DataTable → 用 Data Registry 的按需获取机制
- 你需要基于 GameplayTag 来索引数据条目 → Data Registry 原生支持 Tag 作为条目名称
- 你需要在 DataTable 和 DataRegistry 之间灵活切换 → 提供了 `FDataRegistryOrTableRow` / `FSoftDataRegistryOrTable` 兼容结构体

## 蓝图用法

Data Registry 的运行时蓝图接口主要通过 `UDataRegistrySubsystem` 提供。编辑器模块则提供了 UI 选择器节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `MakeDataRegistryTypeSelector` | 创建一个 DataRegistry 类型选择器控件 | `FDataRegistryEditorModule` |
| `MakeDataRegistryItemNameSelector` | 创建一个条目名称选择器控件（根据类型自动切换 Tag/Combo UI） | `FDataRegistryEditorModule` |
| `GenerateDataRegistryTypeComboBoxStrings` | 生成有效的 DataRegistry 类型列表 | `FDataRegistryEditorModule` |

> 注意：以上为编辑器专用 UI 工具函数。运行时的核心 API（GetItem、AcquireItem 等）定义在 `DataRegistry` 运行时模块中，通过 `UDataRegistrySubsystem` 访问。

### 使用示例（蓝图描述）

1. **创建 Data Registry 资产**：在 Content Browser 中右键 → Miscellaneous → Data Registry，选择关联的 ScriptStruct 类型
2. **配置数据源**：在 Data Registry 编辑器中添加数据源（如 DataTable），设置优先级
3. **运行时获取数据**：通过 `UDataRegistrySubsystem` 的 Acquire 方法，传入 `FDataRegistryId`（Type + Name），获取对应的结构体数据

## C++ 用法

### 头文件引入

```cpp
// 运行时模块
#include "DataRegistrySubsystem.h"
#include "DataRegistryId.h"
#include "DataRegistryType.h"

// 编辑器模块
#include "DataRegistryEditorModule.h"
```

### 基本用法

使用 `UDataRegistrySubsystem` 获取数据条目：

```cpp
// 获取子系统
UDataRegistrySubsystem* RegistrySubsystem = UDataRegistrySubsystem::Get();

// 构造 DataRegistryId（类型 + 名称）
FDataRegistryId RegistryId;
RegistryId.Type = FDataRegistryType(TEXT("ItemAttributes"));
RegistryId.Name = FName(TEXT("Sword_01"));

// 查询数据源条目信息
const FDataRegistrySourceItemId* SourceItem = nullptr;
// 通过子系统获取结构体数据（具体 API 取决于运行时模块公开接口）
```

> 来源推断自：`FDataRegistryEditorToolkit::GetSourceItemForName`、`SDataRegistryItemNameWidget` 中对 `UDataRegistrySubsystem` 的使用

### 编辑器扩展：创建自定义选择器

```cpp
// 创建类型选择器
TSharedRef<SWidget> TypeSelector = FDataRegistryEditorModule::MakeDataRegistryTypeSelector(
    FOnGetDataRegistryDisplayText::CreateLambda([]() -> FText {
        return FText::FromString(TEXT("选择数据类型"));
    }),
    FOnSetDataRegistryType::CreateLambda([](FDataRegistryType NewType) {
        UE_LOG(LogTemp, Log, TEXT("Selected type: %s"), *NewType.ToString());
    }),
    true,  // bAllowClear
    NAME_None  // FilterStructName
);

// 创建条目名称选择器
TSharedRef<SWidget> NameSelector = FDataRegistryEditorModule::MakeDataRegistryItemNameSelector(
    FOnGetDataRegistryDisplayText::CreateLambda([]() -> FText {
        return FText::FromString(TEXT("选择条目"));
    }),
    FOnGetDataRegistryId::CreateLambda([this]() -> FDataRegistryId {
        return CurrentRegistryId;
    }),
    FOnSetDataRegistryId::CreateLambda([this](FDataRegistryId NewId) {
        CurrentRegistryId = NewId;
    }),
    FOnGetCustomDataRegistryItemNames(),  // 可选自定义名称委托
    true  // bAllowClear
);
```

> 来源：`Public/DataRegistryEditorModule.h`

### 进阶用法：属性自定义

为你的 USTRUCT 中的 `FDataRegistryId` 字段注册属性自定义：

```cpp
// 在编辑器模块启动时注册
FPropertyEditorModule& PropertyModule = FModuleManager::LoadModuleChecked<FPropertyEditorModule>("PropertyEditor");
PropertyModule.RegisterCustomPropertyTypeLayout(
    FDataRegistryId::StaticStruct()->GetFName(),
    FOnGetPropertyTypeCustomizationInstance::CreateStatic(&FDataRegistryIdCustomization::MakeInstance)
);
PropertyModule.RegisterCustomPropertyTypeLayout(
    FDataRegistryType::StaticStruct()->GetFName(),
    FOnGetPropertyTypeCustomizationInstance::CreateStatic(&FDataRegistryTypeCustomization::MakeInstance)
);
```

> 来源：`Private/DataRegistryIdCustomization.h`、`Private/DataRegistryTypeCustomization.h`

## Demo 示例

以下示例展示如何在编辑器工具中创建 Data Registry 类型选择器：

```cpp
// MyToolPanel.h
#pragma once

#include "CoreMinimal.h"
#include "Widgets/SCompoundWidget.h"
#include "DataRegistryEditorModule.h"

class SMyToolPanel : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SMyToolPanel) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs);

private:
    FDataRegistryId SelectedId;

    void OnTypeChanged(FDataRegistryType NewType);
    void OnIdChanged(FDataRegistryId NewId);
    FText GetDisplayText() const;
};
```

```cpp
// MyToolPanel.cpp
#include "MyToolPanel.h"
#include "DataRegistryId.h"

void SMyToolPanel::Construct(const FArguments& InArgs)
{
    ChildSlot
    [
        SNew(SVerticalBox)
        + SVerticalBox::Slot()
        .AutoHeight()
        .Padding(4.0f)
        [
            FDataRegistryEditorModule::MakeDataRegistryTypeSelector(
                FOnGetDataRegistryDisplayText::CreateSP(this, &SMyToolPanel::GetDisplayText),
                FOnSetDataRegistryType::CreateSP(this, &SMyToolPanel::OnTypeChanged),
                true
            )
        ]
        + SVerticalBox::Slot()
        .AutoHeight()
        .Padding(4.0f)
        [
            FDataRegistryEditorModule::MakeDataRegistryItemNameSelector(
                FOnGetDataRegistryDisplayText::CreateSP(this, &SMyToolPanel::GetDisplayText),
                FOnGetDataRegistryId::CreateLambda([this]() -> FDataRegistryId {
                    return SelectedId;
                }),
                FOnSetDataRegistryId::CreateSP(this, &SMyToolPanel::OnIdChanged)
            )
        ]
    ];
}

void SMyToolPanel::OnTypeChanged(FDataRegistryType NewType)
{
    SelectedId.Type = NewType;
    SelectedId.Name = NAME_None;
}

void SMyToolPanel::OnIdChanged(FDataRegistryId NewId)
{
    SelectedId = NewId;
}

FText SMyToolPanel::GetDisplayText() const
{
    if (SelectedId.IsValid())
    {
        return FText::FromString(SelectedId.ToString());
    }
    return FText::FromString(TEXT("None"));
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GameplayTags` / `GameplayTagsEditor` | 条目名称支持 GameplayTag 作为索引键 |
| `DataTableEditor` | 编辑器 UI 复用 DataTable 编辑器的列表视图和行数据结构 |
| `GraphEditor` | 蓝图引脚工厂支持（`FDataRegistryGraphPanelPinFactory`） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-28 | `ffe59a83` | Added toolsets for data registries. Current implemented commands include: | 为数据注册表新增工具集支持 |
| 2026-04-16 | `0b4d09a4` | [ContentBrowser] New Add Menu Data Menu | ContentBrowser 新增数据菜单入口 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF | 日志宏迁移至 UE_LOGF |
| 2026-03-27 | `254999bd` | Removing ensure triggering with intentionally null data | 修复空数据时误触 ensure 断言 |
| 2026-03-20 | `992fad6c` | Gameplay systems deprecation removal pass for 5.4 and earlier | 清理 5.4 及更早版本的废弃代码 |

### 维护评价

- **状态**：活跃维护中。最近的 commit（2026-04）显示仍在持续添加功能和修复问题
- **实验性警告**：`.uplugin` 中 `IsBetaVersion=true`、`EnabledByDefault=false`，表明该插件仍处于测试阶段，API 可能发生变化
- **近期趋势**：功能还在扩展（工具集、菜单集成），同时在做代码清理（日志迁移、废弃代码移除）
- **建议**：可以用于原型开发和内部项目评估，但暂不建议在需要长期稳定的生产项目中作为核心依赖。API 仍可能在后续版本中变更

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/DataRegistry)
- 官方文档：无（`.uplugin` 中 DocsURL 为空）