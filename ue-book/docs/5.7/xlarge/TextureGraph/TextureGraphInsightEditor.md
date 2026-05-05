# Texture Graph Insight Editor

> Texture creation tool using graphs.

| 属性 | 值 |
|---|---|
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `TextureGraph` (Runtime), `TextureGraphEditor` (Runtime), `TextureGraphEngine` (Runtime), `TextureGraphInsight` (Runtime), `TextureGraphInsightEditor` (Runtime), `Continuable` (External), `Function2` (External) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-12-20 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/TextureGraph) | |

## 用途

TextureGraph 是一个基于节点图的程序化纹理创建系统。它允许用户在编辑器中通过连接各种功能节点（如噪声生成、数学运算、图像处理等）来构建复杂的纹理生成逻辑，类似于 Substance Designer 或 Blender 的 Shader Editor 在 Unreal Engine 中的集成。其核心目标是提供一种高效、灵活且可复用的纹理创作工作流，特别适用于需要动态生成或高度定制化纹理的场景。

`TextureGraphInsightEditor` 模块是 TextureGraph 插件的**编辑器扩展和调试工具**。它主要负责在 Unreal Editor 中提供用户界面，用于可视化、调试和分析 TextureGraph 的执行过程、节点状态和性能数据，帮助开发者理解和优化他们的纹理图。

## 使用场景

- **材质与纹理艺术家**：需要创建复杂的程序化纹理（如地形、岩石、金属表面），但不想或无法使用外部软件时。
- **技术美术 (TA)**：需要快速原型化材质效果，或创建可动态响应游戏参数（如天气、时间）的纹理。
- **开发者调试**：当 TextureGraph 生成的纹理出现意外结果时，使用 Insight 工具来追踪每个节点的输入输出，定位问题节点。
- **性能优化**：分析 TextureGraph 的执行时间，找出计算开销大的节点，进行优化。

## 蓝图用法

`TextureGraphInsightEditor` 模块主要提供编辑器扩展功能，其核心 API 面向 C++ 和编辑器 UI。该模块本身不直接暴露 `BlueprintCallable` 函数供游戏逻辑使用。纹理图的创建和操作 API 通常位于 `TextureGraphEngine` 或 `TextureGraph` 模块中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `PluginButtonClicked` | 触发插件主按钮点击事件，通常用于打开 Insight 窗口 | `FTextureGraphInsightEditorModule` |

### 使用示例（蓝图描述）

由于此模块主要服务于编辑器扩展，其功能通常通过编辑器菜单或工具栏按钮触发，而非在游戏运行时蓝图中直接调用。用户可以在编辑器中通过自定义的菜单项或快捷键来启动 TextureGraph Insight 调试窗口。

## C++ 用法

本模块提供了编辑器扩展的基础设施，包括样式、命令和主模块生命周期管理。

### 头文件引入

```cpp
#include "TextureGraphInsightEditor.h"
#include "TextureGraphInsightEditorCommands.h"
#include "TextureGraphInsightEditorStyle.h"
```

### 基本用法

以下代码展示了如何注册一个简单的编辑器命令并将其绑定到一个函数。这是扩展编辑器 UI 的典型模式。

```cpp
// 来源: TextureGraphInsightEditorCommands.h
// 注册自定义命令
class FMyCustomCommands : public TCommands<FMyCustomCommands>
{
public:
    FMyCustomCommands()
        : TCommands<FMyCustomCommands>(
            TEXT("MyPlugin"),
            NSLOCTEXT("Contexts", "MyPlugin", "My Plugin"),
            NAME_None,
            FTextureGraphInsightEditorStyle::GetStyleSetName() // 复用或创建自己的样式集
        )
    {}

    virtual void RegisterCommands() override
    {
        UI_COMMAND(OpenMyWindow, "Open My Window", "Opens the custom window", EUserInterfaceActionType::Button, FInputChord());
    }

    TSharedPtr<FUICommandInfo> OpenMyWindow;
};

// 在模块的 StartupModule 中绑定命令
void FMyModule::StartupModule()
{
    FMyCustomCommands::Register();
    
    Commands = MakeShareable(new FUICommandList);
    Commands->MapAction(
        FMyCustomCommands::Get().OpenMyWindow,
        FExecuteAction::CreateRaw(this, &FMyModule::OnOpenMyWindowClicked),
        FCanExecuteAction()
    );
    
    // ... 将命令注册到工具栏或菜单
}

void FMyModule::OnOpenMyWindowClicked()
{
    // 执行打开窗口的逻辑
    FGlobalTabmanager::Get()->TryInvokeTab(MyTabName);
}
```

### 进阶用法

结合 `FTextureGraphInsightEditorModule` 的实现，可以学习如何管理一个带有自定义布局的停靠标签页（Dock Tab）。

```cpp
// 来源: TextureGraphInsightEditor.h
// 在模块中定义标签页的生成逻辑
TSharedRef<SDockTab> FTextureGraphInsightEditorModule::OnSpawnPluginTab(const FSpawnTabArgs& SpawnTabArgs)
{
    // 创建标签页的内容，例如一个 SGraphEditor 或自定义的 Slate 控件
    TSharedRef<SDockTab> NewTab = SNew(SDockTab)
        .TabRole(ETabRole::NomadTab)
        [
            // 在这里放置你的 Slate 控件树
            SNew(STextBlock)
            .Text(FText::FromString(TEXT("Texture Graph Insight Window")))
        ];
    
    return NewTab;
}

// 在 StartupModule 中注册标签页
void FTextureGraphInsightEditorModule::StartupModule()
{
    // ... 其他初始化
    
    // 注册标签页生成器
    FGlobalTabmanager::Get()->RegisterNomadTabSpawner("TextureGraphInsightTab", FOnSpawnTab::CreateRaw(this, &FTextureGraphInsightEditorModule::OnSpawnPluginTab))
        .SetDisplayName(NSLOCTEXT("TextureGraphInsight", "TabTitle", "Texture Graph Insight"))
        .SetMenuType(ETabSpawnerMenuType::Hidden);
}

// 通过命令或菜单打开该标签页
void FTextureGraphInsightEditorModule::PluginButtonClicked()
{
    FGlobalTabmanager::Get()->TryInvokeTab("TextureGraphInsightTab");
}
```

## Demo 示例

一个最小化的编辑器扩展模块示例，演示了如何创建一个带按钮的简单窗口。

**MySimpleEditorModule.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FMySimpleEditorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    void RegisterMenus();
    TSharedRef<class SDockTab> OnSpawnMyTab(const class FSpawnTabArgs& SpawnTabArgs);
    void OnButtonClicked();

    TSharedPtr<class FUICommandList> PluginCommands;
};
```

**MySimpleEditorModule.cpp**
```cpp
#include "MySimpleEditorModule.h"
#include "Styling/SlateStyle.h"
#include "Framework/Docking/TabManager.h"
#include "Widgets/Docking/SDockTab.h"
#include "Widgets/Text/STextBlock.h"
#include "Widgets/Input/SButton.h"
#include "ToolMenus.h"

static const FName MyTabName("MySimpleTab");

#define LOCTEXT_NAMESPACE "FMySimpleEditorModule"

void FMySimpleEditorModule::StartupModule()
{
    // 注册标签页
    FGlobalTabmanager::Get()->RegisterNomadTabSpawner(MyTabName, FOnSpawnTab::CreateRaw(this, &FMySimpleEditorModule::OnSpawnMyTab))
        .SetDisplayName(LOCTEXT("TabTitle", "My Simple Tab"))
        .SetMenuType(ETabSpawnerMenuType::Hidden);

    // 注册命令和菜单
    RegisterMenus();
}

void FMySimpleEditorModule::ShutdownModule()
{
    FGlobalTabmanager::Get()->UnregisterNomadTabSpawner(MyTabName);
}

void FMySimpleEditorModule::RegisterMenus()
{
    // 将按钮添加到编辑器的某个菜单中，例如“窗口”菜单
    UToolMenus::RegisterStartupCallback(FSimpleMulticastDelegate::FDelegate::CreateLambda([]()
    {
        UToolMenu* Menu = UToolMenus::Get()->ExtendMenu("LevelEditor.MainMenu.Window");
        FToolMenuSection& Section = Menu->FindOrAddSection("MySection");
        Section.AddMenuEntry(
            "OpenMyTab",
            LOCTEXT("OpenMyTab", "My Simple Tab"),
            LOCTEXT("OpenMyTabTooltip", "Opens the simple demo tab"),
            FSlateIcon(),
            FUIAction(FExecuteAction::CreateLambda([]() {
                FGlobalTabmanager::Get()->TryInvokeTab(MyTabName);
            }))
        );
    }));
}

TSharedRef<SDockTab> FMySimpleEditorModule::OnSpawnMyTab(const FSpawnTabArgs& SpawnTabArgs)
{
    return SNew(SDockTab)
        .TabRole(ETabRole::NomadTab)
        [
            SNew(SVerticalBox)
            + SVerticalBox::Slot()
            .AutoHeight()
            .Padding(10)
            [
                SNew(STextBlock)
                .Text(LOCTEXT("WelcomeText", "Welcome to My Simple Editor Tab!"))
            ]
            + SVerticalBox::Slot()
            .AutoHeight()
            .Padding(10)
            [
                SNew(SButton)
                .Text(LOCTEXT("ClickMe", "Click Me"))
                .OnClicked_Lambda([this]() -> FReply {
                    OnButtonClicked();
                    return FReply::Handled();
                })
            ]
        ];
}

void FMySimpleEditorModule::OnButtonClicked()
{
    UE_LOG(LogTemp, Warning, TEXT("Button in My Simple Tab was clicked!"));
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMySimpleEditorModule, MySimpleEditor)
```

## 模块依赖

`TextureGraphInsightEditor` 模块作为编辑器扩展，其依赖主要集中在 Slate UI 和编辑器框架。

| 模块 | 用途 |
|---|---|
| `Slate`, `SlateCore` | 构建编辑器用户界面 |
| `EditorStyle` | 获取编辑器标准样式 |
| `EditorFramework` | 编辑器框架和停靠标签页管理 |
| `ToolMenus` | 扩展编辑器菜单和工具栏 |
| `InputCore` | 处理输入和快捷键 |

## 维护状态

### 近期更新

```
- ce6ff392ddca 修复了忽略 FTSTicker::RemoveTicker 返回值的 “nodiscard” 属性警告问题。
- 731c336e7fff 将 Texture Graph 移动到标准的 Engine/Plugins 目录，作为 5.6 版本达到 Beta 阶段工作的一部分。
```

### 维护评价

TextureGraph 插件创建于 2023 年底，是一个相对年轻的项目。从最近的提交记录来看，它正在被积极地整合到 Unreal Engine 的标准插件目录中，并为 5.6 版本的 Beta 发布做准备。提交内容涉及代码质量改进（修复编译警告）和项目结构优化，表明 Epic Games 正在对其进行正式化维护。

**综合评价**：
- **活跃度**：高。插件正在被主动重构和准备发布。
- **状态**：实验性/Beta。虽然 `.uplugin` 中 `IsExperimentalVersion` 为 `false`，但 `VersionName` 为 “1.0 Beta”，且 `EnabledByDefault` 为 `false`，表明它仍处于测试阶段。
- **推荐度**：对于需要程序化纹理生成工作流的项目，这是一个值得关注和尝试的官方插件。但由于其 Beta 状态，不建议在需要高度稳定性的生产项目中作为核心依赖。适合用于原型开发、内部工具或学习目的。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/TextureGraph)
- [官方文档]() （暂无）
- [测试用例]() （暂未在提供的信息中发现）