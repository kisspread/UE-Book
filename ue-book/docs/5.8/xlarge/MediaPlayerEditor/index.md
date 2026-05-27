# Media Player Editor

> Content Editor for MediaPlayer Assets.

| 属性 | 值 |
|---|---|
| 中文名 | 媒体播放器编辑器 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `MediaPlayerEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2014-09-09 |
| 年龄标签 | 🏛️ 文物（约 12 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaPlayerEditor) | |

## 用途

MediaPlayerEditor 插件为 `UMediaPlayer`、`UMediaSource` 和 `UMediaPlaylist` 资产提供了一个完整的、集成在编辑器内的专用编辑工具包（Toolkit）。它不仅仅是内容浏览器的扩展，而是包含了一个完整的资产编辑器，内含视频预览视口、播放控件、播放列表管理、媒体属性详情面板等。其核心目的是为媒体框架（Media Framework）的用户提供一个可视化、可交互的开发和调试环境，用于测试媒体播放效果、管理播放列表和验证媒体源配置。

## 使用场景

- 你正在开发一个需要播放视频或音频内容的游戏或应用程序，并希望在编辑器中实时预览和调试 `UMediaPlayer` 资产的播放效果。
- 你需要创建和管理一个媒体播放列表（`UMediaPlaylist`），并希望直观地查看列表内容。
- 你需要检查一个 `UMediaSource` 资产的详细信息，如分辨率、帧率、解码器等，并验证其配置是否正确。
- 你需要一个带时间轴滑块的预览窗口，用于定位媒体播放位置或生成缩略图。

## 蓝图用法

该插件主要为编辑器功能，其公开的蓝图 API 专注于创建可复用的媒体播放器滑块控件。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateMediaPlayerSliderWidget` | 创建一个用于显示播放进度和拖动的滑块控件 | `IMediaPlayerEditorModule` |

### 使用示例（蓝图描述）

1.  **创建滑块控件**：通过 `IMediaPlayerEditorModule::CreateMediaPlayerSliderWidget` 函数（通常在 C++ 中调用，但该接口是模块的公开接口），你可以传入一个或多个 `UMediaPlayer` 对象和一个可选的 `FSliderStyle`，从而创建一个 `IMediaPlayerSlider` 控件。这个控件可以嵌入到你自定义的编辑器工具或 UMG 界面中。
2.  **配置滑块**：获取创建的 `IMediaPlayerSlider` 后，可以通过其接口函数 `SetSliderHandleColor` 和 `SetSliderBarColor` 来自定义滑块的颜色。`SetVisibleWhenInactive` 函数可以设置当没有媒体活动时滑块的可见性。
3.  **监听拖动事件**：通过 `GetScrubEvent` 获取一个委托（Delegate），你可以订阅它来响应用户对滑块的拖动操作。该委托会提供事件类型（`EScrubEventType`: Begin/Update/End）、受影响的 `UMediaPlayer` 数组以及当前的滑块值。

## C++ 用法

### 头文件引入

```cpp
#include "MediaPlayerEditorModule.h"
```

### 基本用法

从模块获取滑块控件实例。

```cpp
// Source: MediaPlayerEditorModule.h (IMediaPlayerEditorModule)
IMediaPlayerEditorModule& MediaPlayerEditorModule = FModuleManager::GetModuleChecked<IMediaPlayerEditorModule>("MediaPlayerEditor");

// 获取模块样式（可选，用于自定义外观）
TSharedPtr<ISlateStyle> Style = MediaPlayerEditorModule.GetStyle();

// 创建一个绑定到特定 UMediaPlayer 的滑块控件
TWeakObjectPtr<UMediaPlayer> MyMediaPlayerPtr = ...; // 你的媒体播放器实例
TSharedRef<IMediaPlayerSlider> Slider = MediaPlayerEditorModule.CreateMediaPlayerSliderWidget(
    MakeArrayView(&MyMediaPlayerPtr, 1), // 传入 TWeakObjectPtr 的数组视图
    FCoreStyle::Get().GetWidgetStyle<FSliderStyle>("Slider") // 使用默认样式
);

// 订阅滑块的拖动事件
Slider->GetScrubEvent().AddLambda([](IMediaPlayerSlider::EScrubEventType EventType, TConstArrayView<UMediaPlayer*> MediaPlayers, float Value){
    if (EventType == IMediaPlayerSlider::EScrubEventType::Update)
    {
        // Value 范围是 0.0 到 1.0
        UE_LOG(LogTemp, Log, TEXT("Scrubbing to %f"), Value);
    }
});
```

### 进阶用法

直接使用插件内部的 Slate Widget（如 `SMediaPlayerEditorViewer`）需要更多的模块内部知识，通常不被推荐给外部模块使用。这些 Widget 是编辑器 Toolkit 的一部分。更常见的“进阶”用法是通过该插件提供的 `AssetDefinition` 和 `AssetActions` 系统，来自定义这些媒体资产在内容浏览器中的行为。

## Demo 示例

一个完整的最小示例，展示如何创建并嵌入一个媒体播放器滑块控件。

```cpp
// MyMediaTools.h
#pragma once

#include "CoreMinimal.h"
#include "Widgets/SCompoundWidget.h"
#include "MediaPlayerEditorModule.h" // 引入插件模块头文件

class UMediaPlayer;
class IMediaPlayerSlider;

class SMyMediaSliderContainer : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SMyMediaSliderContainer) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs, UMediaPlayer* InMediaPlayer);
    
private:
    TSharedPtr<IMediaPlayerSlider> MediaPlayerSlider;
};
```

```cpp
// MyMediaTools.cpp
#include "MyMediaTools.h"
#include "MediaPlayer.h"

void SMyMediaSliderContainer::Construct(const FArguments& InArgs, UMediaPlayer* InMediaPlayer)
{
    ChildSlot
    [
        SNew(SVerticalBox)
        + SVerticalBox::Slot()
        .AutoHeight()
        [
            SNew(STextBlock)
            .Text(FText::FromString(TEXT("Media Scrubber:")))
        ]
        + SVerticalBox::Slot()
        .FillHeight(1.0f)
        .Padding(5.0f)
        [
            // 此处假设模块已加载且函数可用
            // 在实际插件中，通常会在构造时检查模块状态
            SAssignNew(MediaPlayerSlider, IMediaPlayerSlider) // 赋值给成员变量以便后续控制
            // 注意：这里需要调用模块函数来创建实际的控件
            // 以下为伪代码示意，实际实现需要调用 IMediaPlayerEditorModule
        ]
    ];

    // 在构造函数中，通过模块创建滑块并将其内容设置到上层布局
    IMediaPlayerEditorModule* MediaPlayerEditorModule = FModuleManager::GetModulePtr<IMediaPlayerEditorModule>("MediaPlayerEditor");
    if (MediaPlayerEditorModule && InMediaPlayer)
    {
        TWeakObjectPtr<UMediaPlayer> MediaPlayerPtr(InMediaPlayer);
        TSharedRef<IMediaPlayerSlider> Slider = MediaPlayerEditorModule->CreateMediaPlayerSliderWidget(MakeArrayView(&MediaPlayerPtr, 1));
        // 将 Slider Widget 插入到 ChildSlot 中（需要重新构建布局或使用其他方法）
        // 例如：将 Slider 作为 ChildSlot 的子控件。
        // 这里为了简洁，仅获取了引用。
        MediaPlayerSlider = Slider;
        // 实际嵌入：ChildSlot[SNew(SBox)[MediaPlayerSlider.ToSharedRef()]];
    }
}
```

## 模块依赖

从 `MediaPlayerEditor.Build.cs` 分析，该插件依赖于以下**非标准**模块：

| 模块 | 用途 |
|---|---|
| `MediaUtils` | 提供媒体工具函数和基础类型。 |
| `MediaPlayer` | 核心媒体播放器运行时模块。 |
| `MediaAssets` | 包含 `UMediaPlayer`, `UMediaSource` 等资产类。 |
| `MediaFrameworkUtilities` | 媒体框架的编辑器/工具程序扩展。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了严格浮点模式下双精度常量截断为浮点数的编译器警告。 |
| 2026-05-13 | `bd09d694` | [ImgMedia] Refresh paused-player tiles when visibility changes | [ImgMedia] 当暂停的播放器可见性改变时刷新瓦片。 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories... | 虚拟制作：将多种虚拟制作资产移至不同的资产分类。 |
| 2026-05-12 | `44843d86` | [MediaPlayerEditor] 2D preview tile-visibility provider for the media output viewer(s) | [MediaPlayerEditor] 为媒体输出查看器添加了 2D 预览瓦片可见性提供器。 |
| 2026-04-14 | `8d566979` | [ContentBrowser] New Add Menu Media Menu | [Content浏览器] 新增了媒体添加菜单。 |

### 维护评价

- **年龄**：创建于2014年，是一个历史非常悠久的插件。
- **活跃度**：尽管创建时间早，但从提交历史看，它仍在被积极维护和更新。最近的提交集中在2026年5月，主要涉及浮点精度警告修复、与媒体框架（ImgMedia）的集成改进、资产分类优化以及功能增强（如瓦片可见性提供器）。
- **状态**：属于**活跃维护**状态。作为媒体框架不可或缺的编辑器工具，它随着底层媒体模块的演进而持续更新。
- **推荐**：**强烈推荐使用**。这是在编辑器中使用 UE 媒体框架的标准方式，功能完善且稳定。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaPlayerEditor)
- [官方文档](https://forums.unrealengine.com/showthread.php?46879-Media-Framework-Documentation-for-4-5-Preview) (链接可能已过时，但包含历史信息)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaPlayerEditor/Tests) (如果存在)