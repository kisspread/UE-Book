# TedsSettings

> Experimental UI Features for the Editor, built on TEDS: Editor Data Storage.

| 属性 | 值 |
|---|---|
| 中文名 | 设置数据桥接 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `TedsSettings` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-25 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/EditorDataStorageFeatures) | |

## 用途

TedsSettings 是 TEDS（Typed Editor Data Storage）框架的一个子模块，它将编辑器设置系统（包括设置容器、分类、节区）转化为数据驱动的、基于表格的表示形式。

**核心动机**：传统的 `ISettingsCategory` / `ISettingsSection` 基于对象指针层次结构，难以被 TEDS 的查询/列系统高效处理。TedsSettings 将每一个设置容器、分类、节区映射为 TEDS 中的**数据行**，并附加语义标签（Tag）和引用列，使得 TEDS 查询可以像处理其他编辑器数据一样处理设置。

主要功能：
- 将设置容器（ISettingsContainer）、设置分类（ISettingsCategory）、设置节区（ISettingsSection）注册为 TEDS 表格行。
- 提供 `FindSettingsSection` / `FindOrAddSettingsSection` 等查询和修改接口。
- 在行上附加语义标签（`FSettingsContainerTag`、`FSettingsCategoryTag`、`FSettingsSectionTag`），便于 TEDS 查询筛选。
- 管理激活/未激活设置节区的区别（`FSettingsInactiveSectionTag` 标记未激活的行）。
- 提供 UI Widget 构造器（`FSettingsContainerReferenceWidgetConstructor`、`FSettingsCategoryReferenceWidgetConstructor`、`FSettingsSectionWidgetConstructor`），用于在 TEDS UI 系统中渲染设置引用。

## 使用场景

- **你正在构建一个基于 TEDS 的编辑器工具**（如自定义属性面板、资源浏览器），需要将原生 `ISettingsCategory` / `ISettingsSection` 整合为 TEDS 数据，以便与现有 TEDS 查询/列/UI 系统无缝集成。
- **你需要对设置节区进行数据驱动的筛选、排序或可视化**（例如，只显示激活的设置节区，或根据设置分类名称排序），TedsSettings 的标签和引用列让这些操作变得直接。
- **你需要在 TEDS UI 中显示一个可点击的设置引用**（如“点击跳转到项目设置→渲染”），使用 `FSettingsContainerReferenceWidgetConstructor` 等构造器可以自动生成带名称和点击行为的 Widget。

## 蓝图用法

本模块主要面向 C++ 和 TEDS 数据框架集成，蓝图 API 有限。头文件 `TedsSettingsEditorSubsystem.h` 提供了三个蓝图可调用的查询函数，用于在 Blueprint 中与设置行交互。

### 核心节点（UTedsSettingsEditorSubsystem）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FindSettingsSection` | 根据 ContainerName / CategoryName / SectionName 查找一个已有的设置节区行。返回 `InvalidRowHandle` 如果不存在。 | `UTedsSettingsEditorSubsystem` |
| `FindOrAddSettingsSection` | 查找或创建一个设置节区行（若不存在则创建不激活的行）。 | `UTedsSettingsEditorSubsystem` |
| `GetSettingsSectionFromRow` | 从已知的行句柄读出对应的 ContainerName / CategoryName / SectionName。成功返回 true。 | `UTedsSettingsEditorSubsystem` |

### 使用示例（蓝图描述）

1. **查找项目设置的一个节区**：
   - 获取 `TedsSettingsEditorSubsystem`（通过 Get Editor Subsystem 节点，选择 "TedsSettingsEditorSubsystem"）。
   - 调用 `FindSettingsSection`，输入容器名 `"Project"`、分类名 `"General"`、节区名 `"Description"`。
   - 输出 `RowHandle` 可用于后续的列操作（如添加列、读取数据）。

2. **创建或获取一个自定义设置节区（用于测试/动态注册）**：
   - 调用 `FindOrAddSettingsSection`，输入你自己的容器/分类/节区名称。
   - 如果未找到，系统会自动在 TEDS 中创建一个带 `FSettingsInactiveSectionTag` 的行。你可以后续手动通过 Manager 标记为激活。

## C++ 用法

### 头文件引入

```cpp
#include "TedsSettingsEditorSubsystem.h"
#include "TedsSettingsManager.h"          // 直接使用 Manager
#include "TedsSettingsColumns.h"          // 使用列/标签结构体
#include "TedsSettingsFactory.h"          // 注册 Widget 构造器
```

### 基本用法

#### 通过 Subsystem 查询设置节区

```cpp
// TEDSSETTINGS_API
UTedsSettingsEditorSubsystem* SettingsSubsystem = 
    GEditor->GetEditorSubsystem<UTedsSettingsEditorSubsystem>();

if (SettingsSubsystem && SettingsSubsystem->IsEnabled())
{
    // 查找项目设置→渲染→光追设置
    UE::Editor::DataStorage::RowHandle Found = 
        SettingsSubsystem->FindSettingsSection(TEXT("Project"), TEXT("Rendering"), TEXT("Raytracing"));

    if (Found != UE::Editor::DataStorage::InvalidRowHandle)
    {
        // 从行读取名称
        FName OutContainer, OutCategory, OutSection;
        if (SettingsSubsystem->GetSettingsSectionFromRow(Found, OutContainer, OutCategory, OutSection))
        {
            // ...
        }
    }
}
```

#### 通过 FTedsSettingsManager 直接管理

```cpp
// 在 TEDS 初始化完成后访问 Manager（通常通过 Subsystem）
TSharedPtr<FTedsSettingsManager> Manager = 
    SettingsSubsystem->GetSettingsManager(); // 假设有 Getter（实际代码中未暴露）

if (Manager && Manager->IsInitialized())
{
    // 强制注册一个新设置节区（即使原 ISettings 不存在）
    UE::Editor::DataStorage::RowHandle NewRow = 
        Manager->FindOrAddSettingsSection(TEXT("MyPlugin"), TEXT("MyCategory"), TEXT("MySection"));

    // 添加列数据
    // Manager->AddColumns(DataStorage, NewRow, Columns, ColumnTypes);
}
```

#### 注册自定义 Widget 构造器

```cpp
// 在 Factory 中注册
void UTedsSettingsFactory::RegisterWidgetConstructors(
    UE::Editor::DataStorage::ICoreProvider& DataStorage,
    UE::Editor::DataStorage::IUiProvider& DataStorageUi) const
{
    // 注册一个构造器，用于渲染 "FSettingsContainerReferenceColumn" 类型的数据行
    DataStorageUi.RegisterWidgetConstructor(
        FSettingsContainerReferenceColumn::StaticStruct(),
        FSettingsContainerReferenceWidgetConstructor::StaticStruct());
}
```

### 进阶用法

#### 通过 TEDS 查询筛选激活/未激活设置

利用标签列，你可以编写 TEDS 查询仅获取当前激活的设置节区：

```cpp
// 伪代码：使用 TEDS 查询引擎（假设你有 ICoreProvider）
// 构建一个查询，条件为 Row 包含 FSettingsSectionTag 且不包含 FSettingsInactiveSectionTag
UE::Editor::DataStorage::FQueryDescription Query;
Query.AddColumn<FSettingsSectionTag>();
Query.AddColumn<FSettingsNameColumn>();
Query.AddCondition([](const FEditorDataStorageRowHandle& Row) -> bool {
    return !Row.HasTag<FSettingsInactiveSectionTag>();
});

// 执行查询，获取所有激活的设置节区的名称
Query.Execute(DataStorage, [](const FEditorDataStorageRowHandle& Row) {
    const FSettingsNameColumn* NameCol = DataStorage.GetColumn<FSettingsNameColumn>(Row);
    // ...
});
```

## Demo 示例

以下是一个完整的 Minimal 示例，演示如何通过 `UTedsSettingsEditorSubsystem` 查询和读取设置节区。

**MyTedsSettingsDemo.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "TedsSettingsEditorSubsystem.h"

class FTedsSettingsDemo
{
public:
    static void DemoQueryProjectSettings();
};
```

**MyTedsSettingsDemo.cpp**

```cpp
#include "MyTedsSettingsDemo.h"
#include "Editor.h"

void FTedsSettingsDemo::DemoQueryProjectSettings()
{
    UTedsSettingsEditorSubsystem* Subsystem = 
        GEditor->GetEditorSubsystem<UTedsSettingsEditorSubsystem>();

    if (!Subsystem || !Subsystem->IsEnabled())
    {
        UE_LOG(LogTemp, Warning, TEXT("TedsSettings not enabled."));
        return;
    }

    // 查找项目设置→General→Description（标准节区）
    UE::Editor::DataStorage::RowHandle Row = 
        Subsystem->FindSettingsSection(TEXT("Project"), TEXT("General"), TEXT("Description"));

    if (Row == UE::Editor::DataStorage::InvalidRowHandle)
    {
        UE_LOG(LogTemp, Warning, TEXT("Section not found."));
        return;
    }

    FName ContainerName, CategoryName, SectionName;
    if (Subsystem->GetSettingsSectionFromRow(Row, ContainerName, CategoryName, SectionName))
    {
        UE_LOG(LogTemp, Log, TEXT("Found settings: %s → %s → %s"), 
            *ContainerName.ToString(), *CategoryName.ToString(), *SectionName.ToString());
    }

    // 尝试创建一个不存在的节区
    UE::Editor::DataStorage::RowHandle NewRow = 
        Subsystem->FindOrAddSettingsSection(TEXT("TestContainer"), TEXT("TestCategory"), TEXT("TestSection"));

    if (NewRow != UE::Editor::DataStorage::InvalidRowHandle)
    {
        UE_LOG(LogTemp, Log, TEXT("Created or found new section row."));
    }
}
```

**构建依赖**：在模块的 `Build.cs` 中（示例部分不展示，依赖见下章节）。

## 模块依赖

从 `TedsSettings.Build.cs` 分析（根据头文件引用推断）：

| 模块 | 用途 |
|---|---|
| `TypedElementDataStorage` | TEDS 核心框架：ICoreProvider、IUiProvider、RowHandle、Column/Tag 系统。 |
| `TypedElementDataStorageUI` | TEDS UI 系统：UiProvider、FSimpleWidgetConstructor。 |
| `EditorSubsystem` | 编辑器子系统基类（UEditorSubsystem）。 |
| `DeveloperSettings` | 设置容器/分类/节区管理（ISettingsCategory）。 |

**省略常见依赖**：无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

- 2025-10-14 `267e8191` 修复 TedsTypeInfo 在特定 Verse 自动测试中的断言。  
- 2025-10-02 `1f8278e6` 重新启用 TedsAssetData（解决测试和 FName 问题后）。  
- 2025-09-26 `7d070444` [TEDS Viewers] 允许排序持久化。  
- 2025-09-25 `8d9818a1` [TEDS Viewers] 创建新的复合层次视图（包括默认搜索和筛选）。  
- 2025-09-25 `4161c053` 添加 TEDSFilterBar Widget，将 TedsFilters 引入 TableViewer 模块。

### 维护评价

TedsSettings 是 **实验性**功能（`IsExperimentalVersion=true`），创建于 2025-09-25，距今不到半年。最近更新活跃，集中在 TEDS Viewers 增强、测试修复等方面。代码量适中（288 个源文件，TedsSettings 本模块 5 个头文件 + 若干 cpp），结构清晰，高度依赖 TEDS 核心。

**状态**：⚡活跃开发中，新功能不断加入。  
**推荐**：适合用于 TEDS 生态的实验性项目或编辑器扩展原型；不适合生产环境，因为接口和 API 可能在后续 UE 版本中发生较大变动。  
**已知问题**：未观察到明显的废弃标记或稳定性警告，但作为实验性模块，不保证向前兼容。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/EditorDataStorageFeatures)
- [测试用例（TedsSettings 相关）](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/EditorDataStorageFeatures/Source/TedsSettings/Tests/)
- [核心列定义](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/EditorDataStorageFeatures/Source/TedsSettings/Public/TedsSettingsColumns.h)
- [Subsystem 接口](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/EditorDataStorageFeatures/Source/TedsSettings/Public/TedsSettingsEditorSubsystem.h)