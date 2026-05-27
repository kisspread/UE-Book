# Media Profile

> This plugin contains the Media Profile asset and related entities, which help manage media sources and outputs

| 属性 | 值 |
|---|---|
| 中文名 | 媒体配置 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（资产定义、代理媒体源/输出） |
| 模块 | `MediaProfile` (Runtime), `MediaProfileEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-23 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaProfile) | |

## 用途

Media Profile 插件的核心是创建一个“媒体配置系统”。它不仅仅是一个资产容器，而是一个**上下文感知的配置管理工具**。其主要解决的问题是：在一个复杂的媒体制作流程中，可能需要频繁地切换不同的媒体源（如不同的摄像机输入、视频文件）和输出（如不同的预览窗口、录制格式、流媒体服务）。手动管理这些切换既繁琐又容易出错。

此插件通过 `UMediaProfile` 资产，允许用户将一系列媒体源（`UMediaSource`）和媒体输出（`UMediaOutput`）**绑定到一个逻辑配置文件**。在虚幻引擎中，可以设置一个“当前激活的”媒体配置。许多相关的编辑器UI和工具会自动感知这个当前配置，并为其提供快捷选择功能，从而实现媒体输入输出的快速切换和管理。

## 使用场景

- **影视虚拟制作 (Virtual Production)**：在拍摄现场，可能需要同时处理多个摄像机输入（用于实时合成预览）、一个录制输出和一个直播输出。通过创建不同的 Media Profile，可以在“现场拍摄”、“后期渲染预览”、“直播推流”等模式间一键切换。
- **广播与大型活动**：管理多个视频源（VTR、现场摄像机、图形引擎输出）并将其分配到不同的输出目的地（现场大屏、导播台、网络流）。
- **测试与开发**：为不同的硬件设置（例如，不同的采集卡配置）或不同的项目阶段（开发、QA、演示）保存特定的媒体配置。

## 蓝图用法

此插件主要提供编辑器UI组件和菜单功能，不直接暴露大量蓝图节点用于运行时逻辑。其核心蓝图相关功能是为编辑器内的资产选择器提供增强功能。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SMediaProfileSourceTexturePicker` | 一个增强型的纹理选择器控件。除了标准资产浏览器，它还提供一个下拉菜单，可以快速从当前激活的 Media Profile 中选择媒体源对应的媒体纹理。 | `SMediaProfileSourceTexturePicker` |
| `OpenExistingOrCreateNewMediaProfile()` | 用于在编辑器工具栏或菜单中调用。如果存在当前 Media Profile，则在专用编辑器中打开它；否则，弹出资产创建对话框。 | `UE::MediaProfile::Menus` (命名空间函数) |
| `GenerateMediaProfileDropdownMenu()` | 创建一个填充了与当前 Media Profile 相关操作的下拉菜单部件。 | `UE::MediaProfile::Menus` (命名空间函数) |
| `CreateMediaProfileToolBarButton()` | 创建一个可用于工具栏的下拉按钮部件，其内容与 Media Profile 相关。 | `UE::MediaProfile::Menus` (命名空间函数) |

### 使用示例（蓝图描述）

虽然不能直接在蓝图图表中使用这些 Slate 控件，但可以通过 C++ 或 Editor Utility Widget 来利用它们。例如，在一个自定义的媒体控制面板中，你可以放置一个 `SMediaProfileSourceTexturePicker` 控件。当用户在属性面板中需要选择一个 `UMediaTexture` 时，这个控件不仅会提供标准的资产浏览器，还会在控件旁边显示一个下拉箭头。点击该箭头会列出当前 `Media Profile` 中所有已配置的媒体源，选择其一便会自动将对应的 `UMediaTexture` 资产设置到属性中，极大简化了在多个预设源之间的切换过程。

## C++ 用法

### 头文件引入

```cpp
#include "IMediaProfileEditorModule.h"
#include "MediaProfileMenus.h"
```

### 基本用法

获取 Media Profile 编辑器模块的实例，并使用其提供的功能来扩展编辑器菜单。

```cpp
// 在你的编辑器模块或工具代码中
#include "IMediaProfileEditorModule.h"

void ExtendMyToolMenu(FMenuBuilder& MenuBuilder)
{
    // 获取 Media Profile 编辑器模块
    IMediaProfileEditorModule& MediaProfileEditorModule = IMediaProfileEditorModule::Get();
    
    // 获取 Media Profile 的菜单扩展器，并将你的菜单部分添加到其中
    TSharedPtr<FExtender> ProfileMenuExtender = MediaProfileEditorModule.GetMediaProfileMenuExtender();
    if (ProfileMenuExtender.IsValid())
    {
        // 定义一个扩展，将你的操作添加到 Media Profile 菜单中
        ProfileMenuExtender->AddMenuExtension(
            "MediaProfile", // 目标扩展点名称
            EExtensionHook::After,
            nullptr, // 不需要命令列表
            FMenuExtensionDelegate::CreateLambda(
                [](FMenuBuilder& Builder)
                {
                    Builder.AddMenuEntry(
                        FText::FromString("My Custom Action"),
                        FText::FromString("Performs a custom action related to the current media profile"),
                        FSlateIcon(),
                        FUIAction(FExecuteAction::CreateStatic(&ExecuteMyAction))
                    );
                }
            )
        );
    }
}
```
*来源：基于 `IMediaProfileEditorModule.h` 和 `FExtender` 的通用用法推断。*

### 进阶用法

直接使用 `MediaProfileMenus` 命名空间提供的函数来创建符合插件风格的 UI 控件，集成到自定义编辑器窗口或工具栏中。

```cpp
#include "MediaProfileMenus.h"

void SetupMyEditorToolbar(FToolBarBuilder& ToolBarBuilder)
{
    // 在自定义工具栏中添加一个 Media Profile 下拉按钮
    TSharedRef<SWidget> MediaProfileButton = UE::MediaProfile::Menus::CreateMediaProfileToolBarButton(
        FText::FromString("Manage active Media Profile")
    );
    
    ToolBarBuilder.AddWidget(MediaProfileButton);
}

void CreateMyCustomMenu(FMenuBarBuilder& MenuBarBuilder)
{
    // 在自定义菜单栏中添加一个包含 Media Profile 操作的下拉菜单
    MenuBarBuilder.AddPullDownMenu(
        FText::FromString("Media Settings"),
        FText::FromString("Media Profile settings and quick actions"),
        FNewMenuDelegate::CreateStatic([](FMenuBuilder& MenuBuilder)
        {
            TSharedRef<SWidget> ProfileMenu = UE::MediaProfile::Menus::GenerateMediaProfileDropdownMenu();
            MenuBuilder.AddWidget(ProfileMenu, FText::GetEmpty(), true);
        })
    );
}
```
*来源：基于 `MediaProfileMenus.h` 中声明的 API。*

## Demo 示例

下面的示例展示了如何编写一个简单的编辑器工具模块，它会在“工具”菜单中添加一个条目，用于打开或创建 Media Profile，并且它扩展了 Media Profile 自身的菜单。

**MyMediaProfileToolModule.h**
```cpp
#pragma once

#include "Modules/ModuleManager.h"

class FMyMediaProfileToolModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

**MyMediaProfileToolModule.cpp**
```cpp
#include "MyMediaProfileToolModule.h"
#include "IMediaProfileEditorModule.h"
#include "MediaProfileMenus.h"
#include "ToolMenus.h"
#include "LevelEditor.h"

#define LOCTEXT_NAMESPACE "FMyMediaProfileToolModule"

void FMyMediaProfileToolModule::StartupModule()
{
    // 1. 向“工具”菜单添加一个条目，用于打开 Media Profile
    UToolMenus::RegisterStartupCallback(FSimpleMulticastDelegate::FDelegate::CreateLambda([]()
    {
        UToolMenu* Menu = UToolMenus::Get()->ExtendMenu("LevelEditor.MainMenu.Tools");
        FToolMenuSection& Section = Menu->AddSection("MediaProfileSection", LOCTEXT("MediaProfileHeading", "Media Profile"));
        Section.AddMenuEntry(
            "OpenMediaProfile",
            LOCTEXT("OpenMediaProfile", "Open Media Profile"),
            LOCTEXT("OpenMediaProfileTooltip", "Opens the active media profile editor or creates a new one."),
            FSlateIcon(),
            FUIAction(FExecuteAction::CreateStatic(&UE::MediaProfile::Menus::OpenExistingOrCreateNewMediaProfile))
        );
    }));

    // 2. 扩展 Media Profile 自身的下拉菜单，添加一个自定义选项
    IMediaProfileEditorModule& MediaProfileModule = IMediaProfileEditorModule::Get();
    TSharedPtr<FExtender> MenuExtender = MediaProfileModule.GetMediaProfileMenuExtender();
    if (MenuExtender.IsValid())
    {
        MenuExtender->AddMenuExtension(
            "MediaProfile", // 假设的扩展点名称
            EExtensionHook::After,
            nullptr,
            FMenuExtensionDelegate::CreateLambda([](FMenuBuilder& Builder)
            {
                Builder.AddSeparator();
                Builder.AddMenuEntry(
                    FText::FromString("My Plugin Action"),
                    FText::FromString("Does something cool with the current media profile."),
                    FSlateIcon(),
                    FUIAction()
                );
            })
        );
    }
}

void FMyMediaProfileToolModule::ShutdownModule()
{
    UToolMenus::UnRegisterStartupCallback(this);
    UToolMenus::UnregisterOwner(this);
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyMediaProfileToolModule, MyMediaProfileTool)
```

## 模块依赖

要使用此插件的功能，你的模块（特别是编辑器模块）需要链接以下插件提供的模块。

| 模块 | 用途 |
|---|---|
| `MediaProfile` | 包含核心资产类（如 `UMediaProfile`），是 `MediaProfileEditor` 的基础依赖。 |
| `MediaProfileEditor` | 提供编辑器 UI、菜单、资产定义和工厂类。你的编辑器工具应主要依赖此模块。 |

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-21 | `ff9996e8` | Media Profile: Fixed issue where ElectraProtron issue would not play a new video after it had alread | 修复了 ElectraProtron 播放器在播放后无法加载新视频的问题。 |
| 2026-05-20 | `54cbb9f8` | Ensure a transient MediaProfile always exists from startup | 确保编辑器启动时总存在一个临时的 MediaProfile，提升稳定性。 |
| 2026-05-20 | `de6434f1` | Composure: Add final new icons for composite actors, layers, and passes, and minor tweaks to menu co | (关联改动) Composure 插件更新，可能涉及图标和菜单协同。 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | (关联改动) 视口系统代码重构。 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回退了编号为 CL53913857 的变更。 |

### 维护评价

- **创建时间**：该插件于 2026 年 4 月创建，是一个相对较新的功能模块。
- **最近更新频率**：最近一次功能更新和Bug修复在 2026 年 5 月，距文档生成时间不足 1 个月，**更新非常活跃**。
- **维护状态**：该插件目前处于**实验性**（`IsExperimentalVersion: true`）阶段，由 Epic Games 官方维护。根据提交记录，开发团队正在积极修复问题和改进稳定性。
- **已知限制**：作为实验性功能，其API和功能在未来版本中可能发生变动。它需要手动启用（`EnabledByDefault: false`）。
- **推荐使用**：对于**影视虚拟制作、广播等需要复杂媒体流管理的项目**，强烈推荐尝试使用此插件。它能显著提升多输入输出场景下的工作流效率。对于一般游戏开发，除非有特定的媒体管理需求，否则无需关注。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaProfile)
- [官方文档]()（无）
- [测试用例]()（未在提供的信息中发现）