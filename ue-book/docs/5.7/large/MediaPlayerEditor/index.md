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
| 创建时间 | 2025-04-28 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/MediaPlayerEditor) | |

## 用途

Media Player Editor 为 `UMediaPlayer`、`UMediaSource`、`UMediaPlaylist`、`UMediaTexture` 等媒体相关资产提供了完整的编辑器支持。它允许开发者在编辑器内创建、预览和调试媒体播放，而无需启动游戏或构建项目。该插件注册了这些资产类型的右键菜单操作、资产工厂、属性面板自定义以及专用的编辑工具（如媒体播放器查看器、播放列表编辑器）。它解决了在编辑器环境中直接操作媒体资产的需求，是 Media Framework 的编辑配套模块。

## 使用场景

- 准备媒体资源（视频、音频、流媒体）时，需要创建 `MediaSource` 资产并指定文件路径或 URL。
- 编辑 `MediaPlayer` 资产以配置播放参数、查看播放详情、调试播放行为。
- 管理多个媒体源，使用 `MediaPlaylist` 资产创建播放列表，并为不同平台指定不同的媒体源。
- 需要在编辑器视口中预览媒体播放效果，测试播放控制功能（如暂停、快进、跳转）。
- 需要为媒体源生成缩略图，或在内容浏览器中直接查看媒体纹理的预览。

## 蓝图用法

该插件是一个纯编辑器模块，**不提供任何运行时蓝图可调用函数**。所有功能均集中在编辑器界面中，通过资产右键菜单、属性面板和专用编辑器窗口暴露。

### 核心功能（编辑器操作）

| 节点 / 操作 | 说明 | 位置 |
|---|---|---|
| 右键菜单创建资产 | 在内容浏览器中右键 → 媒体 → 选择所需的媒体资产类型（MediaPlayer、MediaSource、MediaPlaylist、MediaTexture） | 资产工厂 |
| 编辑 MediaPlayer | 双击 MediaPlayer 资产，打开专用编辑器（包含查看器、播放列表、媒体详情等标签页） | `FMediaPlayerEditorToolkit` |
| 编辑 MediaPlaylist | 双击 MediaPlaylist 资产，打开列表编辑器，可添加 / 删除 / 替换媒体源条目 | `SMediaPlaylistEditorTracks` |
| 属性面板自定义 | 在详情面板中为 MediaSource 子类（如 FileMediaSource、PlatformMediaSource）提供专属 UI | `FBaseMediaSourceCustomization` 等 |
| 缩略图预览 | 内容浏览器中直接显示媒体源的视频缩略图（需要媒体源支持） | `UMediaSourceThumbnailRenderer` |

## C++ 用法

### 头文件引入

```cpp
#include "MediaPlayerEditorModule.h"
#include "AssetTools/MediaSourceActions.h"
#include "Toolkits/MediaPlayerEditorToolkit.h"
```

### 基本用法

#### 创建自定义媒体播放器滑块控件

通过 `IMediaPlayerEditorModule` 接口的 `CreateMediaPlayerSliderWidget` 方法，可以创建可拖拽的播放进度条，并订阅 scrub 事件。

```cpp
// 文件来源: Source/MediaPlayerEditor/Public/MediaPlayerEditorModule.h
#include "MediaPlayerEditorModule.h"
#include "Styling/SlateTypes.h"

// 获取模块实例
IMediaPlayerEditorModule& MediaPlayerEditorModule = FModuleManager::LoadModuleChecked<IMediaPlayerEditorModule>("MediaPlayerEditor");

// 准备媒体玩家列表
TArrayView<TWeakObjectPtr<UMediaPlayer>> MediaPlayers = { MediaPlayer1, MediaPlayer2 };

// 创建滑块控件（使用默认样式）
TSharedRef<IMediaPlayerSlider> Slider = MediaPlayerEditorModule.CreateMediaPlayerSliderWidget(MediaPlayers);

// 设置滑块外观
Slider->SetSliderHandleColor(FSlateColor(FLinearColor::Yellow));
Slider->SetSliderBarColor(FSlateColor(FLinearColor::White));
Slider->SetVisibleWhenInactive(EVisibility::Collapsed);

// 订阅 scrub 事件
Slider->GetScrubEvent().AddLambda([](IMediaPlayerSlider::EScrubEventType EventType, TConstArrayView<UMediaPlayer*> Players, float Value)
{
    if (EventType == IMediaPlayerSlider::EScrubEventType::Update)
    {
        // 将所有播放器的播放位置设置为 Value
        for (UMediaPlayer* Player : Players)
        {
            if (Player)
            {
                Player->Seek(FTimespan::FromSeconds(Value * Player->GetDuration().GetTotalSeconds()));
            }
        }
    }
});
```

#### 以编程方式创建媒体源资产

使用工厂类可以在编辑器中自动化创建媒体资产。

```cpp
// 文件来源: Source/MediaPlayerEditor/Private/Factories/FileMediaSourceFactoryNew.h
#include "Factories/FileMediaSourceFactoryNew.h"
#include "AssetRegistry/AssetRegistryModule.h"

// 创建工厂实例
UFileMediaSourceFactoryNew* Factory = NewObject<UFileMediaSourceFactoryNew>();
Factory->AddToRoot();

// 创建资产
FString PackagePath = TEXT("/Game/Media/MyVideo");
UPackage* Package = CreatePackage(*PackagePath);
UFileMediaSource* MediaSource = Cast<UFileMediaSource>(Factory->FactoryCreateNew(
    UFileMediaSource::StaticClass(),
    Package,
    FName(TEXT("MyVideo")),
    RF_Public | RF_Standalone | RF_Transactional,
    nullptr,
    GWarn
));

// 保存资产
FAssetRegistryModule::AssetCreated(MediaSource);
MediaSource->MarkPackageDirty();
Package->SetDirtyFlag(true);

Factory->RemoveFromRoot();
```

### 进阶用法

#### 自定义媒体源属性面板

继承 `FBaseMediaSourceCustomization` 可进一步定制 MediaSource 子类的详情面板。例如为自定义媒体源添加特殊选项：

```cpp
// 文件来源: Source/MediaPlayerEditor/Private/Customizations/BaseMediaSourceCustomization.h
class FMyMediaSourceCustomization : public IDetailCustomization
{
public:
    static TSharedRef<IDetailCustomization> MakeInstance()
    {
        return MakeShareable(new FMyMediaSourceCustomization);
    }

    virtual void CustomizeDetails(IDetailLayoutBuilder& DetailBuilder) override
    {
        // 隐藏默认的 PlayerOverrides 属性，添加自定义 UI
        TSharedRef<IPropertyHandle> PlayerOverrides = DetailBuilder.GetProperty(GET_MEMBER_NAME_CHECKED(UMediaSource, PlayerOverrides));
        PlayerOverrides->MarkHiddenByCustomization();

        // 添加自定义按钮
        IDetailCategoryBuilder& Category = DetailBuilder.EditCategory("Media");
        Category.AddCustomRow(FText::FromString("Actions"))
            .WholeRowContent()
            [
                SNew(SButton)
                .Text(LOCTEXT("GenerateThumbnail", "Generate Thumbnail"))
                .OnClicked_Lambda([]() -> FReply { /* ... */ return FReply::Handled(); })
            ];
    }
};
```

## Demo 示例

以下是一个完整的编辑器模块示例，演示如何利用 MediaPlayerEditor 模块创建一个带播放进度条的编辑器窗口。

### `MyMediaPlayerEditorDemo.h`

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Widgets/SCompoundWidget.h"
#include "MediaPlayerEditorModule.h"
#include "Styling/CoreStyle.h"
#include "Styling/SlateTypes.h"

class UMediaPlayer;

class SMyMediaPlayerEditorDemo : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SMyMediaPlayerEditorDemo) 
        : _MediaPlayer(nullptr) 
    {}
        SLATE_ARGUMENT(UMediaPlayer*, MediaPlayer)
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs);
    virtual ~SMyMediaPlayerEditorDemo() override;

private:
    TSharedPtr<IMediaPlayerSlider> SliderWidget;
    UMediaPlayer* MediaPlayer;
};
```

### `MyMediaPlayerEditorDemo.cpp`

```cpp
#include "MyMediaPlayerEditorDemo.h"
#include "Modules/ModuleManager.h"

void SMyMediaPlayerEditorDemo::Construct(const FArguments& InArgs)
{
    MediaPlayer = InArgs._MediaPlayer;
    
    // 获取 MediaPlayerEditor 模块
    IMediaPlayerEditorModule& Module = FModuleManager::LoadModuleChecked<IMediaPlayerEditorModule>("MediaPlayerEditor");
    
    // 创建滑块（只关联一个玩家）
    TArrayView<TWeakObjectPtr<UMediaPlayer>> Players = { MediaPlayer };
    SliderWidget = Module.CreateMediaPlayerSliderWidget(Players, FCoreStyle::Get().GetWidgetStyle<FSliderStyle>("Slider"));
    
    // 订阅 scrub 事件
    SliderWidget->GetScrubEvent().AddLambda([this](IMediaPlayerSlider::EScrubEventType EventType, TConstArrayView<UMediaPlayer*> Players, float Value)
    {
        if (EventType == IMediaPlayerSlider::EScrubEventType::Update && Players.Num() > 0 && Players[0])
        {
            Players[0]->Seek(FTimespan::FromSeconds(Value * Players[0]->GetDuration().GetTotalSeconds()));
        }
    });

    ChildSlot
    [
        SliderWidget.ToSharedRef()
    ];
}

SMyMediaPlayerEditorDemo::~SMyMediaPlayerEditorDemo()
{
    SliderWidget->GetScrubEvent().RemoveAll(this);
}
```

## 模块依赖

**注意**：以下仅列出非标准依赖（省略了 Core, CoreUObject, Engine, Slate, SlateCore 等常见模块）。

| 模块 | 用途 |
|---|---|
| `Media` | 核心媒体框架，提供播放管道 |
| `MediaAssets` | 媒体资产类型（UMediaPlayer, UMediaSource 等） |
| `MediaUtils` | 媒体实用工具类与函数 |
| `ToolMenus` | 编辑器菜单系统扩展 |
| `WorkspaceMenuStructure` | 工作区菜单结构注册 |
| `AssetTools` | 资产类型行为注册与资产编辑 |
| `InputCore` | 键盘/鼠标输入事件处理 |

## 维护状态

### 近期更新

- 2025-08-18 `b9d68562` — Media Viewer / Media Player Editor: 修复播放器信息在媒体详情面板中不显示的问题
- 2025-07-10 `9803c443` — 为包含 .gen.cpp 文件的源文件添加 UE_INLINE_GENERATED_CPP_BY_NAME 宏
- 2025-05-31 `52e3dac1` — 使用 UnrealCodeFixup 更新头文件，确保 DLL 存储位于方法 / 静态变量而非类型上
- 2025-05-01 `8e059901` — 修复媒体 IO 在播放时详情面板不显示播放器信息的问题
- 2025-04-28 `50e40753` — 在打开媒体源前验证全局指定的首选播放器

### 维护评价

- **创建时间**：2025-04-28（约1年前）
- **最近更新**：2025-08-18（约1个月前），频率高
- **活跃度**：非常活跃，持续修复 Bug 和更新代码适配引擎变化
- **已知问题**：无已知重大限制
- **推荐度**：✅ 强烈推荐，作为 Media Framework 的标准编辑器配套模块，与引擎同步维护

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/MediaPlayerEditor)
- [官方文档（论坛帖）](https://forums.unrealengine.com/showthread.php?46879-Media-Framework-Documentation-for-4-5-Preview)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/MediaPlayerEditor/Tests)（该目录可能不存在，官方测试位于引擎其他位置）