# TEDS: Editor Data Storage Features

> Experimental UI Features for the Editor, built on TEDS: Editor Data Storage.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | TEDS 编辑器数据存储功能 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（实验性编辑器UI功能） |
| 模块 | `TedsSettings` (Runtime), `TedsOutliner` (Runtime), `TedsContentBrowser` (Runtime), `TedsPropertyEditor` (Runtime), `TedsTableViewer` (Runtime), `TedsEverythingPicker` (Runtime), `TedsAssetData` (Runtime), `TedsAlerts` (Runtime), `TedsDebugger` (Runtime), `TedsOperations` (Runtime), `TedsRevisionControl` (Runtime), `TedsQueryStack` (Runtime), `TedsTypeInfo` (Runtime), `TedsActorCompatibility` (Runtime), `TedsEditorCompatibility` (Runtime), `TedsTypedElementBridge` (Runtime), `UnifiedFavorites` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-07-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorDataStorageFeatures) | |

## 用途

该插件是 **TEDS (Typed Element Data Storage) 系统的编辑器功能扩展**，旨在使用 TEDS 的数据存储框架来构建实验性的编辑器 UI 和功能。它不是一个独立的插件，而是 TEDS 基础架构上的一系列实验性功能模块的集合。其核心目标是探索如何利用高性能的 ECS (Entity Component System) 风格的 TEDS 数据库来驱动编辑器界面（如大纲视图、内容浏览器、属性编辑器等），以期获得更好的性能和数据一致性。

简单来说，这个插件是 Epic 用来**试验下一代编辑器 UI 框架**的试验场。

## 使用场景

- **编辑器工具开发者**：希望了解或参与实验性 TEDS 编辑器 UI 框架的开发。
- **技术美术/技术策划**：在特定实验性分支中，可能遇到或使用这些基于 TEDS 的编辑器功能（如新的大纲视图）。
- **UE 源码研究者**：学习 Epic 如何设计基于数据驱动的大型编辑器系统。

**注意**：由于这是实验性插件，且默认未启用，普通用户通常不会在正式项目中使用它。

## 蓝图用法

该插件中的功能主要面向 C++，且为实验性功能，未提供蓝图可调用的公共接口。无公开的 `BlueprintCallable` 或 `BlueprintReadWrite` 函数。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| （无） | 该插件模块无公开蓝图节点 | - |

## C++ 用法

### 头文件引入

```cpp
// 使用 TEDS 设置子系统
#include "TedsSettings/Public/TedsSettingsEditorSubsystem.h"
```

### 基本用法

`TedsSettings` 模块提供了一个编辑器子系统，用于查询和管理基于 TEDS 存储的设置项。

```cpp
// 获取 TEDS 设置子系统实例
UTedsSettingsEditorSubsystem* TedsSettingsSubsystem = GEditor->GetEditorSubsystem<UTedsSettingsEditorSubsystem>();

if (TedsSettingsSubsystem && TedsSettingsSubsystem->IsEnabled())
{
    // 查找一个名为 "ProjectSettings" 的设置容器
    UE::Editor::DataStorage::RowHandle ContainerRow = TedsSettingsSubsystem->FindSettingsContainer(FName("ProjectSettings"));
    
    // 在容器中查找一个名为 "Rendering" 的类别
    UE::Editor::DataStorage::RowHandle CategoryRow = TedsSettingsSubsystem->FindSettingsCategory(FName("ProjectSettings"), FName("Rendering"));
    
    // 进一步查找一个名为 "PostProcessing" 的设置节
    UE::Editor::DataStorage::RowHandle SectionRow = TedsSettingsSubsystem->FindSettingsSection(FName("ProjectSettings"), FName("Rendering"), FName("PostProcessing"));
    
    // 根据一个节的行句柄反向获取其路径信息
    FName ContainerName, CategoryName, SectionName;
    if (TedsSettingsSubsystem->GetSettingsSectionFromRow(SectionRow, ContainerName, CategoryName, SectionName))
    {
        UE_LOG(LogTemp, Log, TEXT("Setting path: %s/%s/%s"), *ContainerName.ToString(), *CategoryName.ToString(), *SectionName.ToString());
    }
}
```
*（代码来源：基于 `Public/TedsSettingsEditorSubsystem.h` 接口描述推断）*

### 进阶用法

结合 TEDS 的查询系统，可以高效地检索所有属于特定模块的设置项。

```cpp
// 假设你有一个 TEDS 查询句柄，用于查询所有带有 FSettingsModuleTag 且模块名为 "Renderer" 的行
UE::Editor::DataStorage::QueryHandle Query = ...; // 通过 TEDS API 创建的查询

// 执行查询，遍历结果
DataStorage->RunQuery(Query, [&](UE::Editor::DataStorage::RowHandle Row)
{
    // 对于每个找到的设置行，可以获取其设置细节
    FName Container, Category, Section;
    if (TedsSettingsSubsystem->GetSettingsSectionFromRow(Row, Container, Category, Section))
    {
        // 进行处理...
    }
});
```
*（概念示例，展示与 TEDS 查询系统的结合使用）*

## Demo 示例

一个最小示例，演示如何在自定义编辑器模式中注册一个基于 TEDS 的简单设置项。这需要创建一个 `UDeveloperSettings` 子类并确保 TEDS 设置子系统已初始化。

```cpp
// MyGameSettings.h
#pragma once

#include "CoreMinimal.h"
#include "Engine/DeveloperSettings.h"
#include "MyGameSettings.generated.h"

UCLASS(config=Game, defaultconfig, meta=(DisplayName="My Game Settings"))
class UMyGameSettings : public UDeveloperSettings
{
    GENERATED_BODY()

public:
    UPROPERTY(config, EditAnywhere, BlueprintReadOnly, Category="Performance")
    int32 MaxQualityLevel = 5;
};
```

```cpp
// MyEditorModule.cpp (在编辑器模块的 StartupModule 中)
#include "TedsSettings/Public/TedsSettingsEditorSubsystem.h"

void FMyEditorModule::StartupModule()
{
    // TEDS 设置子系统会在其自己的 Initialize 中监听模块加载和设置注册。
    // 这里我们只需要确保我们的设置类被注册到 SettingsModule。
    // 系统会自动将其同步到 TEDS 数据存储中，如果 TEDS 设置子系统已启用的话。
    UMyGameSettings* MySettings = GetMutableDefault<UMyGameSettings>();
    ISettingsModule* SettingsModule = FModuleManager::GetModulePtr<ISettingsModule>("Settings");
    if (SettingsModule && MySettings)
    {
        SettingsModule->RegisterSettings("Project", "Game", "MyGameSettings",
            FText::FromString("My Game Settings"),
            FText::FromString("Configure custom game settings."),
            MySettings);
    }
}
```

## 模块依赖

该插件的模块依赖广泛且深度集成 UE 核心编辑器系统。对于 `TedsSettings` 模块：

| 模块 | 用途 |
|---|---|
| `TypedElementFramework` | TEDS 的核心框架，提供类型化元素和行句柄系统 |
| `TypedElementDataStorage` | TEDS 的数据存储核心，提供表、列、查询和层级系统 |
| `EditorDataStorage` | TEDS 的编辑器层扩展 |
| `Settings` | UE 的设置模块，用于发现和管理 `UDeveloperSettings` |

**注意**：该插件的大多数模块都依赖于 `EditorDataStorage` 和 `TypedElementDataStorage`，它们是 TEDS 的核心组成部分。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `c18be83c` | Enable the TEDS Outliner in Restricted UEFN | 在受限的 UEFN 环境中启用 TEDS 大纲视图 |
| 2026-05-14 | `bd93e418` | Hide unloaded actor rows inside non-editing level instances from TEDS Outliner | 从 TEDS 大纲视图中隐藏非编辑级别实例内的未加载 Actor 行 |
| 2026-05-14 | `bdc9e0ac` | [TedsOutliner] Fix invalid cross-level drag and drops | 修复 TEDS 大纲视图中跨级别拖放的无效操作 |
| 2026-05-14 | `6f329dd1` | [Backout] - CL53940377 | 回退某个变更 |
| 2026-05-14 | `ee0aab56` | Hide unloaded actor rows inside non-editing level instances from TEDS Outliner | 隐藏非编辑级别实例中的未加载 Actor 行（重复提交或修正） |

### 维护评价

- **创建时间**：2024年7月，插件非常年轻（约1岁）。
- **更新频率**：从提供的 git 历史看，最近（2026年5月）有多次针对 `TedsOutliner` 的修复和功能调整，表明**模块仍在积极开发中**。
- **活跃度**：作为 Epic 的实验性项目，其更新集中在特定团队（如 TEDS 团队）的功能迭代和 Bug 修复上，频率不定。
- **状态**：**实验性且活跃**。`.uplugin` 中明确标记为 `IsExperimentalVersion: true`，且 `EnabledByDefault: false`。
- **推荐使用**：**不推荐**普通项目使用。仅适用于源码研究、参与 Epic 实验性开发，或在特定实验分支中测试其功能。其 API 和行为可能随时发生破坏性更改。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorDataStorageFeatures)
- 官方文档：无 (`DocsURL` 为空)
- 测试用例：位于各模块的 `Tests/` 目录下，例如 `TedsSettings/Tests/TestSettings.h` 用于验证设置同步功能。