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
| 年龄标签 | 🏛️ 文物（约 11 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaPlayerEditor) | |

## 用途

MediaPlayerEditor 是 UE 媒体框架（Media Framework）的编辑器侧配套插件，为 `UMediaPlayer`、`UMediaSource`、`UMediaPlaylist`、`UMediaTexture` 等资产类型提供完整的编辑器界面。

它解决的核心问题是：**在编辑器内预览、调试和管理媒体播放资产**。没有这个插件，你就无法在编辑器中打开和预览视频/音频文件、浏览媒体播放列表、查看媒体纹理通道、或为媒体源配置平台播放器。它是媒体框架在编辑器工作流中的 UI 骨架。

## 使用场景

- 你创建了 `UMediaPlayer` 资产并想在编辑器中预览视频/音频 → 双击资产打开专属编辑器
- 你需要查看视频的帧率、分辨率、解码器等详细信息 → 媒体详情面板自动展示
- 你要编辑 `UMediaPlaylist` 的媒体源列表 → 播放列表编辑器支持拖拽添加
- 你需要调试视频的 RGBA 通道 → 支持单独切换 R/G/B/A 通道的灰度显示
- 你使用 `UFileMediaSource`、`UStreamMediaSource` 等不同媒体源类型 → 各类型有专属属性面板定制
- 你需要在编辑器中为缩略图生成媒体预览 → 支持缩略图生成功能

## 蓝图用法

MediaPlayerEditor 是纯 Editor 模块，不暴露运行时蓝图 API。它的所有功能通过编辑器 UI 交互使用。

### 模块接口（C++ 可用）

通过 `IMediaPlayerEditorModule` 接口可访问模块功能：

| 方法 | 说明 | 所在接口 |
|---|---|---|
| `GetStyle()` | 获取模块使用的 Slate 样式集 | `IMediaPlayerEditorModule` |
| `CreateMediaPlayerSliderWidget()` | 创建播放进度拖动条控件，支持多个 MediaPlayer | `IMediaPlayerEditorModule` |

### 播放器命令

编辑器内置以下播放控制命令（通过快捷键或工具栏触发）：

| 命令 | 说明 |
|---|---|
| PlayMedia / PauseMedia | 播放/暂停 |
| PlayReverseMedia | 反向播放 |
| ForwardMedia / ReverseMedia | 快进/快退（递增速度） |
| StepForwardMedia / StepBackwardMedia | 逐帧前进/后退 |
| RewindMedia / JumpToEndMedia | 跳转到开头/结尾 |
| OpenMedia / CloseMedia | 打开/关闭媒体 |
| NextMedia / PreviousMedia | 切换播放列表中的上一个/下一个 |
| ToggledRed/Green/Blue/AlphaTextureChannel | 切换 RGBA 通道显示 |

## C++ 用法

### 头文件引入

```cpp
#include "MediaPlayerEditorModule.h"
```

### 基本用法：获取模块接口

通过模块接口创建播放器滑块控件，可在自定义编辑器工具中嵌入媒体播放进度条。

```cpp
// 来源: Source/MediaPlayerEditor/Public/MediaPlayerEditorModule.h

#include "MediaPlayerEditorModule.h"
#include "MediaPlayer.h"

// 获取媒体播放器编辑器模块
IMediaPlayerEditorModule& MediaPlayerEditorModule = FModuleManager::Get().LoadModuleChecked<IMediaPlayerEditorModule>("MediaPlayerEditor");

// 创建一个媒体播放器滑块控件（可嵌入到自定义 Slate 面板中）
TArray<TWeakObjectPtr<UMediaPlayer>> MediaPlayers;
MediaPlayers.Add(MyMediaPlayer);

TSharedRef<IMediaPlayerSlider> SliderWidget = MediaPlayerEditorModule.CreateMediaPlayerSliderWidget(
    MediaPlayers,
    FCoreStyle::Get().GetWidgetStyle<FSliderStyle>("Slider")
);

// 自定义滑块外观
SliderWidget->SetSliderHandleColor(FSlateColor(FLinearColor::Red));
SliderWidget->SetSliderBarColor(FSlateColor(FLinearColor::Gray));
SliderWidget->SetVisibleWhenInactive(EVisibility::Visible);

// 订阅拖动事件
SliderWidget->GetScrubEvent().AddLambda([](IMediaPlayerSlider::EScrubEventType EventType,
    TConstArrayView<UMediaPlayer*> Players, float Value)
{
    switch (EventType)
    {
    case IMediaPlayerSlider::EScrubEventType::Begin:
        // 用户开始拖动
        break;
    case IMediaPlayerSlider::EScrubEventType::Update:
        // 拖动中，Value 为 0.0 ~ 1.0 的归一化位置
        break;
    case IMediaPlayerSlider::EScrubEventType::End:
        // 用户停止拖动
        break;
    }
});
```

### 进阶用法：通道遮罩控制

`SMediaPlayerEditorViewer` 提供了 RGBA 通道遮罩功能，可独立查看视频的各个颜色通道。

```cpp
// 来源: Source/MediaPlayerEditor/Public/Widgets/SMediaPlayerEditorViewer.h
// 来源: Source/MediaPlayerEditor/Public/Widgets/SMediaImage.h

#include "Widgets/SMediaPlayerEditorViewer.h"
#include "Widgets/SMediaImage.h"

using namespace MediaPlayerEditor::MediaImage;

// 仅显示红色通道（灰度模式）
ViewerWidget->SetChannelMask(ETextureChannelMask::Red);

// 显示 RGB 三通道
ViewerWidget->SetChannelMask(ETextureChannelMask::RGB);

// 切换单个通道
ViewerWidget->ToggleChannelMask(ETextureChannelMask::Alpha); // 开/关 Alpha

// 查询当前遮罩状态
ETextureChannelMask CurrentMask = ViewerWidget->GetChannelMask();
bool bRedEnabled = ViewerWidget->IsChannelMasked(ETextureChannelMask::Red);
```

## Demo 示例

一个完整的自定义编辑器面板示例，嵌入媒体播放器滑块控件：

```cpp
// MyMediaPlayerPanel.h
#pragma once

#include "Widgets/SCompoundWidget.h"
#include "MediaPlayerEditorModule.h"

class UMediaPlayer;

class SMyMediaPlayerPanel : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SMyMediaPlayerPanel) {}
        SLATE_ARGUMENT(UMediaPlayer*, MediaPlayer)
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs);

private:
    TSharedPtr<IMediaPlayerSlider> Slider;
    UMediaPlayer* MediaPlayer;
};

// MyMediaPlayerPanel.cpp
#include "MyMediaPlayerPanel.h"
#include "MediaPlayer.h"

void SMyMediaPlayerPanel::Construct(const FArguments& InArgs)
{
    MediaPlayer = InArgs._MediaPlayer;
    check(MediaPlayer);

    // 从编辑器模块创建滑块
    IMediaPlayerEditorModule& EditorModule =
        FModuleManager::Get().LoadModuleChecked<IMediaPlayerEditorModule>("MediaPlayerEditor");

    TArray<TWeakObjectPtr<UMediaPlayer>> Players;
    Players.Add(MediaPlayer);

    Slider = EditorModule.CreateMediaPlayerSliderWidget(Players);

    // 订阅拖动事件以响应用户操作
    Slider->GetScrubEvent().AddLambda(
        [](IMediaPlayerSlider::EScrubEventType EventType,
           TConstArrayView<UMediaPlayer*> InPlayers, float Value)
        {
            if (EventType == IMediaPlayerSlider::EScrubEventType::Update && InPlayers.Num() > 0)
            {
                // 拖动到新位置（Value 为归一化值）
                UE_LOG(LogTemp, Log, TEXT("Scrub to: %.2f"), Value);
            }
        });

    ChildSlot
    [
        SNew(SVerticalBox)
        + SVerticalBox::Slot()
        .AutoHeight()
        .Padding(10.0f)
        [
            SNew(STextBlock)
            .Text(FText::FromString(TEXT("播放进度")))
        ]
        + SVerticalBox::Slot()
        .AutoHeight()
        .Padding(10.0f)
        [
            Slider.ToSharedRef()
        ]
    ];
}
```

## 模块依赖

Build.cs 依赖信息未在提供的文件中完整列出。基于模块功能分析，MediaPlayerEditor 作为编辑器插件依赖以下模块：

| 模块 | 用途 |
|---|---|
| `MediaAssets` | UMediaPlayer、UMediaTexture、UMediaSource 等资产类型定义 |
| `MediaUtils` | 媒体框架工具类（设备信息、媒体事件等） |
| `MediaFrameworkUtilities` | 媒体框架公共工具和接口 |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-05-13 | `bd09d694` | [ImgMedia] Refresh paused-player tiles when visibility changes | 暂停播放时画面可见性变化后刷新图块 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 虚拟制片资产分类迁移 |
| 2026-05-12 | `44843d86` | [MediaPlayerEditor] 2D preview tile-visibility provider for the media output viewer(s) | 为媒体输出预览新增 2D 图块可见性提供器 |
| 2026-04-14 | `8d566979` | [ContentBrowser] New Add Menu Media Menu | 内容浏览器新增媒体菜单 |

### 维护评价

MediaPlayerEditor 自 2014 年创建至今已超过 11 年，是 UE 媒体框架的核心编辑器组件。从近期 git 历史看：

- **活跃维护**：2026 年仍有持续更新，包括功能增强（图块可见性优化）和编译兼容性修复
- **功能稳定**：插件功能成熟，主要更新集中在性能优化和新媒体格式支持
- **长期依赖**：作为媒体框架的编辑器 UI 层，只要 Media Framework 存在此插件就不会废弃
- **推荐使用**：这是使用 UE 媒体框架的必备插件，且默认启用，无需额外配置

唯一需要注意的是这是一个大型编辑器插件（101 个源文件），内部结构复杂，但对使用者透明——只需双击媒体资产即可使用全部功能。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaPlayerEditor)
- [官方文档](https://forums.unrealengine.com/showthread.php?46879-Media-Framework-Documentation-for-4-5-Preview)