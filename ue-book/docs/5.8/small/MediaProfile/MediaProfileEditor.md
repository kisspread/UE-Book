# Media Profile

> This plugin contains the Media Profile asset and related entities, which help manage media sources and outputs

| 属性 | 值 |
|---|---|
| 中文名 | 媒体配置 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（媒体配置资产） |
| 模块 | `MediaProfile` (Runtime), `MediaProfileEditor` (Runtime) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2026-04-23 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaProfile) | |

## 用途

Media Profile 插件的核心目的是**集中管理媒体资源的配置**。它引入了“媒体配置文件”（Media Profile）这一资产类型，作为一组媒体源（Media Source）和媒体输出（Media Output）配置的容器。通过将相关的媒体资产（如代理媒体源、代理媒体输出）打包到一个配置文件中，用户可以方便地在不同媒体配置间进行切换，例如在不同的虚拟制作摄像机源、录制的媒体文件源或不同的显示输出设备之间快速切换。这避免了在场景中逐个修改媒体组件的繁琐操作，确保了配置的一致性。

该插件是为**专业媒体制作和虚拟制片**场景设计的，用于解决管理复杂媒体管道时的配置混乱问题。

## 使用场景

- **虚拟制片（Virtual Production）**：在演播室中，你可能需要在实时摄像机源（通过 MediaSource）和录制好的视频文件之间切换。使用 Media Profile 可以保存并快速切换这两种状态的媒体配置。
- **广播或活动制作**：你需要管理多个屏幕或通道的媒体输出（Media Output）。通过为不同的输出场景（如主屏、侧屏、预览屏）创建不同的 Media Profile，可以一键切换整个输出设置。
- **测试与开发**：开发媒体播放器相关功能时，需要频繁地在不同的媒体源（本地文件、流媒体、硬件设备）间切换测试。Media Profile 可以保存测试配置，提高效率。

## 蓝图用法

从提供的源码分析，该插件的**运行时模块 (`MediaProfile`) 没有暴露直接的蓝图 API**（如 `UFUNCTION(BlueprintCallable)`）。其功能主要在编辑器环境中使用。

编辑器模块 (`MediaProfileEditor`) 提供了用于创建和管理媒体配置文件的编辑器工具和UI，但这些是编辑器扩展，不直接在运行时蓝图图中使用。

## C++ 用法

该插件的核心用法体现在其编辑器扩展和资产创建上。

### 头文件引入

若要在编辑器插件中集成或扩展 Media Profile 功能，需要引入其编辑器模块头文件。

```cpp
// 引入媒体配置编辑器模块接口
#include "IMediaProfileEditorModule.h"
// 引入媒体配置菜单工具函数
#include "MediaProfileMenus.h"
```

### 基本用法

**访问媒体配置编辑器模块**
通过单例模式获取 `IMediaProfileEditorModule` 接口，可用于扩展编辑器菜单或获取功能扩展器。
```cpp
// 获取媒体配置编辑器模块
IMediaProfileEditorModule& MediaProfileEditorModule = IMediaProfileEditorModule::Get();

// 获取可用于扩展媒体配置相关菜单的扩展器
TSharedPtr<FExtender> MenuExtender = MediaProfileEditorModule.GetMediaProfileMenuExtender();
```

**创建媒体配置管理按钮/菜单**
`MediaProfileMenus` 命名空间提供了用于构建编辑器UI的便捷函数。
```cpp
// 在编辑器中，创建一个按钮，点击后可以打开现有的 Media Profile 或创建一个新的
UE::MediaProfile::Menus::OpenExistingOrCreateNewMediaProfile();

// 生成一个包含当前媒体配置相关选项的下拉菜单
TSharedRef<SWidget> DropdownMenu = UE::MediaProfile::Menus::GenerateMediaProfileDropdownMenu();

// 创建一个工具栏下拉按钮，通常和上面的下拉菜单一起使用
TSharedRef<SWidget> ToolbarButton = UE::MediaProfile::Menus::CreateMediaProfileToolBarButton(FText::FromString(“Media Profile”));
```

### 进阶用法

**扩展媒体配置纹理拾取器**：
插件提供了 `SMediaProfileSourceTexturePicker` 控件，这是一个增强版的资产拾取器，专门用于从当前活动的 Media Profile 中选择媒体纹理。你可以在自定义属性编辑器中使用它。
```cpp
// 在Slate UI构建中使用此控件（伪代码示意）
SNew(SMediaProfileSourceTexturePicker)
    .TexturePropertyHandle(MyPropertyHandle)
    .ThumbnailPool(MyThumbnailPool)
    .OnMediaSourceSelected(MyDelegate) // 绑定一个处理用户选择媒体源的委托
    .AdditionalContent(SNew(STextBlock).Text(FText::FromString(“My Label”)));
```

## Demo 示例

以下是一个简单的编辑器面板示例，展示了如何集成 Media Profile 的菜单按钮。

**MediaProfileDemoPanel.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Widgets/Docking/SDockTab.h"

class SMediaProfileDemoPanel : public SDockTab
{
public:
    SLATE_BEGIN_ARGS(SMediaProfileDemoPanel) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs);
};
```

**MediaProfileDemoPanel.cpp**
```cpp
#include "MediaProfileDemoPanel.h"
#include "MediaProfileMenus.h"
#include "Widgets/Layout/SBox.h"
#include "Widgets/Input/SButton.h"
#include "Widgets/Text/STextBlock.h"

void SMediaProfileDemoPanel::Construct(const FArguments& InArgs)
{
    // 调用父类 Construct
    SDockTab::Construct( SDockTab::FArguments() );

    // 创建一个工具栏按钮，点击后可以管理 Media Profile
    TSharedRef<SWidget> MediaProfileButton = UE::MediaProfile::Menus::CreateMediaProfileToolBarButton(
        FText::FromString(“Manage Media Profiles”)
    );

    // 创建一个下拉菜单按钮
    TSharedRef<SWidget> DropdownButton = SNew(SComboButton)
        .ButtonContent(MediaProfileButton)
        .MenuContent(UE::MediaProfile::Menus::GenerateMediaProfileDropdownMenu());

    // 将按钮放入面板布局
    SetContent(
        SNew(SBox)
        .HAlign(HAlign_Center)
        .VAlign(VAlign_Center)
        [
            SNew(SVerticalBox)
            + SVerticalBox::Slot()
            .AutoHeight()
            .Padding(5.0f)
            [
                SNew(STextBlock)
                .Text(FText::FromString(“Media Profile Demo Panel”))
            ]
            + SVerticalBox::Slot()
            .AutoHeight()
            .Padding(5.0f)
            [
                DropdownButton
            ]
        ]
    );
}
```

## 模块依赖

要使用 `MediaProfile` 插件的功能，你的项目模块需要添加以下依赖。这些依赖已在 `MediaProfileEditor` 的 `Build.cs` 中列出。

| 模块 | 用途 |
|---|---|
| `MediaProfile` | 媒体配置文件核心运行时资产和逻辑 |
| `MediaAssets` | 媒体资产类型（UMediaTexture, UMediaSource, UMediaPlayer 等）的基础 |
| `PropertyCustomizationHelpers` | 提供 `SObjectPropertyEntryBox` 等高级属性自定义控件 |
| `AssetDefinition` | 用于定义资产在编辑器中的显示名称、图标和行为（如 `UAssetDefinition_ProxyMediaSource`） |
| `AssetTools` | 资产创建和操作工具 |
| `EditorStyle` | 编辑器样式集 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-21 | `ff9996e8` | Media Profile: Fixed issue where ElectraProtron issue would not play a new video after it had alread | 修复了 ElectraPlayer 在播放过视频后无法播放新视频的问题。 |
| 2026-05-20 | `54cbb9f8` | Ensure a transient MediaProfile always exists from startup | 确保插件启动时始终存在一个临时的 MediaProfile，以避免空指针错误。 |
| 2026-05-20 | `de6434f1` | Composure: Add final new icons for composite actors, layers, and passes, and minor tweaks to menu co | （此提交与 MediaProfile 目录相关但主要针对 Composure 插件）更新了合成器相关图标和菜单。 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | （此提交与 MediaProfile 目录相关但主要针对视口）重构了视口客户端关联逻辑。 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回滚了之前的某个提交（CL53913857）。 |

### 维护评价

**活跃维护**。
该插件创建时间非常近（2026年4月），并且在创建后的一个月内持续收到了针对其核心功能（如ElectraPlayer集成、稳定性）的修复和改进提交。这表明它是一个正在被积极开发和集成的实验性功能。

**注意**：该插件被标记为 **实验性** (`IsExperimentalVersion: true`) 且**默认未启用** (`EnabledByDefault: false`)。这意味着其API和功能在未来版本中可能发生不兼容的变化，不建议在需要长期稳定性的正式生产环境中直接依赖。适合用于早期技术验证、原型开发或对最新媒体功能有特定需求的项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaProfile)
- [官方文档]() （无）
- [测试用例]() （未提供明确路径）