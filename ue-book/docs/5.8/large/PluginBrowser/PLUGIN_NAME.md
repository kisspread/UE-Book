# Plugin Browser

> User interface for managing installed plugins and creating new ones.

| 属性 | 值 |
|---|---|
| 中文名 | 插件浏览器 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `PluginBrowser` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2015-04-25 |
| 年龄标签 | 🏛️ 文物（约 11 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/PluginBrowser) | |

## 用途

PluginBrowser 是一个核心的编辑器工具插件，它为 Unreal Engine 编辑器提供了用于浏览、管理和创建新插件的完整用户界面。这个插件解决的核心问题是：在早期版本的 UE 中，创建一个新的插件需要开发者手动创建多个文件夹和配置文件，过程繁琐且容易出错。PluginBrowser 通过提供一个图形化向导，简化了整个插件创建流程，并集成了对已安装插件的管理功能。

它主要包含两个核心部分：
1. **插件浏览器界面**：一个停靠在编辑器中的面板，列出了所有已安装的插件。用户可以在此界面中启用/禁用插件、查看插件的详细信息（如描述、作者、版本）、搜索和筛选插件。
2. **插件创建向导**：一个引导式的创建流程，允许开发者选择插件类型（如空白、蓝图函数库、编辑器模式等），并自动生成符合规范的插件骨架代码和 `.uplugin` 文件，极大地提高了插件开发的起步效率。

## 使用场景

-   **UE 开发者需要快速创建一个新的自定义插件**：当你准备为游戏或工具开发一个新功能模块时，不想手动配置所有文件结构，可以通过 `编辑 -> 新建插件` 启动向导，选择合适的模板（如 `Blank` 或 `BlueprintLibrary`）。
-   **项目管理和调试时，需要启用或禁用特定插件**：例如，你的游戏不需要某个引擎自带的物理插件，可以使用插件浏览器将其禁用以优化项目。或者在调试时，临时禁用某个插件来排查问题。
-   **查看项目依赖了哪些插件及其版本信息**：快速浏览所有插件的状态，了解项目的插件依赖情况。

## 蓝图用法

此插件主要是一个编辑器工具，其核心功能通过编辑器 UI 触发，而非暴露给蓝图系统。在 `PluginBrowser` 模块的公开头文件中，未发现标记为 `UFUNCTION(BlueprintCallable)` 的函数。插件的管理功能（启用/禁用）通过编辑器偏好设置或插件浏览器面板的勾选框完成，创建功能则通过编辑器菜单触发。

### 核心节点

无直接可调用的蓝图节点。

### 使用示例（蓝图描述）

不适用。操作完全在编辑器 UI 内完成。

## C++ 用法

虽然此插件主要通过 UI 交互，但了解其内部 API 有助于理解插件创建逻辑或进行扩展。

### 头文件引入

```cpp
#include "PluginBrowserModule.h"
```

### 基本用法

获取插件浏览器模块实例，用于检查插件状态或触发内部流程。此为底层用法，通常无需直接调用。

```cpp
// 获取 PluginBrowser 模块
IPluginBrowser& PluginBrowserModule = FModuleManager::GetModuleChecked<IPluginBrowser>(TEXT("PluginBrowser"));

// 检查某个插件是否已启用（通常通过更高级的 IPluginManager 接口）
// bool bIsEnabled = PluginBrowserModule.Get()->IsPluginEnabled(TEXT("SomePlugin"));
```

### 进阶用法

更常见的用法是使用其依赖的 `PluginUtils` 模块来创建插件。`PluginUtils` 提供了更干净的 C++ API 来操作插件。

```cpp
#include "IPluginUtils.h"
// 假设 IPluginUtils 已被正确加载

// 创建插件描述符 (FPluginDescriptor)
FPluginDescriptor PluginDescriptor;
PluginDescriptor.Version = 1;
PluginDescriptor.VersionName = TEXT("1.0");
PluginDescriptor.FriendlyName = TEXT("My Awesome Plugin");
PluginDescriptor.Description = TEXT("Does awesome things.");
PluginDescriptor.Category = TEXT("MyCategory");
PluginDescriptor.CreatedBy = TEXT("Me");
PluginDescriptor.bCanContainContent = false;

// 创建插件模板参数 (FPluginTemplateDescription)
FPluginTemplateDescription TemplateDescription;
// ... 设置模板类型、源文件等参数 ...

// 使用 IPluginUtils 创建插件
FText FailReason;
bool bSuccess = IPluginUtils::Get().CreatePlugin(
    TEXT("MyAwesomePlugin"),
    FPaths::ProjectPluginsDir(), // 创建到项目 Plugins 目录
    TemplateDescription,
    PluginDescriptor,
    FailReason
);

if (!bSuccess)
{
    UE_LOG(LogTemp, Error, TEXT("Failed to create plugin: %s"), *FailReason.ToString());
}
```
*注：以上代码为根据常见插件创建逻辑推断的示例，具体类名和接口需参考 `PluginUtils` 模块的实际头文件。*

## Demo 示例

以下是一个最小化的、可编译的 C++ 模块示例，该模块依赖 `PluginBrowser` 和 `PluginUtils`，用于在模块启动时通过代码创建一个简单的插件。

**MyEditorTool.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FMyEditorToolModule : public IModuleInterface
{
public:
    /** IModule interface */
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    void CreateSimplePlugin();
};
```

**MyEditorTool.cpp**
```cpp
#include "MyEditorTool.h"

#include "IPluginUtils.h"
#include "PluginDescriptor.h"
#include "PluginTemplateDescription.h"
#include "Misc/Paths.h"

#define LOCTEXT_NAMESPACE "FMyEditorToolModule"

void FMyEditorToolModule::StartupModule()
{
    // 延迟创建，确保编辑器已完全初始化
    // 通常会在某个菜单点击或按钮事件中触发，这里仅作演示
    // CreateSimplePlugin();
}

void FMyEditorToolModule::ShutdownModule()
{
}

void FMyEditorToolModule::CreateSimplePlugin()
{
    // 1. 构建插件描述符
    FPluginDescriptor Desc;
    Desc.Version = 1;
    Desc.VersionName = TEXT("1.0");
    Desc.FriendlyName = LOCTEXT("PluginName", "AutoCreated Plugin");
    Desc.Description = LOCTEXT("PluginDesc", "A plugin created automatically by MyEditorTool.");
    Desc.Category = TEXT("Automation");
    Desc.CreatedBy = TEXT("Auto Creator");
    Desc.bCanContainContent = false;
    Desc.bIsBetaVersion = false;

    // 2. 选择一个插件模板（例如空白模板）
    FPluginTemplateDescription Template;
    Template.TemplateName = TEXT("Blank"); // 假设使用内置的空白模板

    // 3. 调用 PluginUtils 创建插件
    FText FailReason;
    FString PluginName = TEXT("AutoCreatedPlugin");
    FString PluginDirectory = FPaths::ProjectPluginsDir(); // 在项目目录下创建

    bool bSuccess = IPluginUtils::Get().CreatePlugin(
        PluginName,
        PluginDirectory,
        Template,
        Desc,
        FailReason
    );

    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("Successfully created plugin '%s' at '%s'"), *PluginName, *PluginDirectory);
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create plugin '%s': %s"), *PluginName, *FailReason.ToString());
    }
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyEditorToolModule, MyEditorTool)
```

## 模块依赖

除了几乎每个编辑器插件都依赖的 `Core`, `CoreUObject`, `Engine`, `Slate`, `SlateCore`, `UnrealEd`, `InputCore` 等模块外，`PluginBrowser` 还明确依赖以下插件/模块：

| 模块 | 用途 |
|---|---|
| `PluginUtils` | 提供了插件创建、描述符解析等底层工具函数，是 `PluginBrowser` 向导创建功能的核心依赖。 |
| `ContentBrowser` | 用于在创建插件后，快速定位并浏览新生成的插件资产。 |
| `WorkspaceMenuStructure` | 用于在编辑器工作区菜单中注册“插件”（Plugins）选项卡。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，双精度常量转换为浮点数时产生的编译器警告。 |
| 2026-05-12 | `d93da640` | Added new PluginToolset AI Toolset for managing plugins. | 新增了一个用于管理插件的AI工具集（PluginToolset）。 |
| 2026-04-08 | `d6aa71b0` | function rename | 对某个函数进行了重命名（代码重构）。 |
| 2026-04-08 | `612e6b9b` | Fixup plugin wizard to check for the actual name of the plugin we'll create rather than the name the user typed. | 修复了插件创建向导中的名称检查逻辑，现在基于实际生成的插件名进行验证，而非用户输入的原始名称。 |
| 2026-03-16 | `e20d084a` | Add a way to sort plugins by names to simplify merging: | 添加了按名称对插件进行排序的功能，以简化插件列表的合并流程。 |

### 维护评价

- **活跃维护**：该插件自 2015 年创建以来，至今（2026 年）仍有持续的功能更新和问题修复。
- **核心功能稳定**：作为编辑器的基础设施组件，其核心的浏览器和向导功能非常稳定。
- **近期更新积极**：最近几个月的更新集中在用户体验优化（插件排序、向导逻辑修复）、代码质量提升（消除警告）以及新功能探索（AI工具集）上，表明 Epic 团队仍在积极维护和迭代该插件。
- **推荐使用**：这是 Unreal Engine 编辑器的标准组件，所有默认创建的项目都已启用它。它对于插件管理是必不可少的工具，没有已知的严重限制或问题。

**结论**：`PluginBrowser` 是一个成熟、稳定且仍在活跃维护的核心编辑器插件。强烈推荐所有 UE 开发者使用和了解它。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/PluginBrowser)