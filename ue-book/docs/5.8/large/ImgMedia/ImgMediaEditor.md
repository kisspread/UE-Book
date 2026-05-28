# Image Sequence Media Player

> Implements a media player for image sequences in EXR and other formats.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 图像序列媒体播放器 |
| 分类 | Media Players |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ImgMedia` (Runtime), `ImgMediaEditor` (Runtime), `ImgMediaEngine` (Runtime), `ImgMediaFactory` (Runtime), `OpenExrWrapper` (Runtime), `ExrReaderGpu` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2017-08-30 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ImgMedia) | |

## 用途

ImgMedia 插件专为播放**图像序列**而设计，这是影视后期制作和视觉特效（VFX）工作流中的核心需求。它并非通用的视频播放器，而是将一系列单独的图像文件（如 EXR、BMP、JPG、PNG）作为连续的视频源进行加载和播放。

其核心价值在于：
1.  **格式支持**：特别是对行业标准的 OpenEXR 格式提供强大支持，包括处理复杂的 Data Window 和 Display Window、多层通道以及高动态范围（HDR）数据。
2.  **性能优化**：通过智能的帧缓存（LRU Cache）、异步加载和 GPU 加速解码（`ExrReaderGpu` 模块）来保证高分辨率图像序列的流畅播放。
3.  **专业工具集成**：提供了用于预处理图像序列（如生成 Mipmap、分块/瓦片化以优化加载）的编辑器工具，这对管理庞大的 VFX 素材至关重要。
4.  **带宽管理**：内置带宽监控，帮助用户理解和管理序列播放时的数据吞吐需求。

简而言之，当你的项目需要从一系列渲染好的图像帧中播放动画或特效时（例如虚拟制片中的背景板、电影级过场动画），ImgMedia 是 Unreal Engine 的原生解决方案。

## 使用场景

-   你在制作影视级过场动画，需要播放由 After Effects 或 Nuke 等软件渲染输出的 EXR 序列。
-   你在进行虚拟制片，需要将 LED 墙或背景屏幕上的图像序列作为实时视频源。
-   你需要将游戏中的某一场景或动画烘焙成一系列图像，并在特定场景下回放。
-   你有一个包含大量高分辨率贴图的序列，需要优化其内存占用和加载性能（通过预处理生成 Mipmap 和分块）。

## 蓝图用法

ImgMedia 插件的功能主要通过 C++ 和编辑器工具实现，暴露给蓝图的高级接口相对有限。其核心交互通常通过标准的 `UMediaPlayer`、`UMediaTexture` 和 `UImgMediaSource` 资产完成，这些资产的使用方式在“媒体框架”通用文档中有描述。

插件特有的蓝图节点主要集中在编辑器模块，用于自动化处理任务，这些通常在内容浏览器或专用面板中操作，而非在游戏蓝图中调用。

## C++ 用法

ImgMedia 的 C++ 用法主要集中在**编辑器扩展**和**底层媒体处理**。

### 头文件引入

```cpp
// 引用媒体源资产
#include "ImgMediaSource.h"

// 引用编辑器工具（如果需要在插件或编辑器脚本中调用）
#include "ImgMediaEditor/Widgets/SImgMediaProcessEXR.h"
```

### 基本用法

使用 `UImgMediaSource` 资产来指向一个图像序列文件夹。这通常在编辑器中完成，但也可以在运行时通过代码设置。

```cpp
// 假设你已经有一个指向图像序列目录的路径
FString SequencePath = TEXT("/Game/MySequences/RenderOutput");

// 创建或获取一个 UImgMediaSource 对象
UImgMediaSource* ImgMediaSource = NewObject<UImgMediaSource>();
ImgMediaSource->SetSequencePath(SequencePath);

// 然后将这个源赋给 UMediaPlayer
UMediaPlayer* MediaPlayer = ...; // 获取或创建你的媒体播放器
MediaPlayer->OpenSource(ImgMediaSource);
```

### 进阶用法

**1. 使用编辑器处理工具 (`SImgMediaProcessEXR`)**

这是插件提供的一个关键编辑器工具，用于优化图像序列。

```cpp
// 在编辑器插件或自定义编辑器工具中
#include "ImgMediaEditor/Widgets/SImgMediaProcessEXR.h"

// 创建一个 Slate 窗口或面板来容纳处理工具
TSharedRef<SWindow> ProcessingWindow = SNew(SWindow)
    .Title(FText::FromString(TEXT("Process Image Sequence")))
    .ClientSize(FVector2D(600, 400));

// 创建处理控件并添加到窗口
TSharedRef<SImgMediaProcessEXR> ProcessWidget = SNew(SImgMediaProcessEXR);
ProcessingWindow->SetContent(ProcessWidget);

// 设置输入路径（指向你的原始图像序列文件夹）
ProcessWidget->SetInputPath(TEXT("/Path/To/Your/ImageSequence"));

// 配置处理选项（通过 UImgMediaProcessEXROptions 对象）
UImgMediaProcessEXROptions* Options = NewObject<UImgMediaProcessEXROptions>();
Options->bEnableMipMapping = true;
Options->bEnableTiling = true;
Options->TileSizeX = 256;
Options->TileSizeY = 256;
Options->bRemoveAlphaChannel = false;
// ... 设置更多选项

// 注意：SImgMediaProcessEXR 内部会管理一个 UImgMediaProcessEXROptions 实例。
// 真正的“处理”操作由该控件内部的按钮（OnProcessImagesClicked）触发。

FSlateApplication::Get().AddWindow(ProcessingWindow);
```

**2. 监控媒体带宽 (`SImgMediaBandwidth`)**

这个控件用于实时监控各个图像序列播放器的带宽消耗，常用于性能分析和调试。

```cpp
#include "ImgMediaEditor/Widgets/SImgMediaBandwidth.h"

// 在编辑器的某个面板中创建带宽监控控件
TSharedRef<SImgMediaBandwidth> BandwidthWidget = SNew(SImgMediaBandwidth);

// 该控件会自动查询当前场景中所有活跃的 FImgMediaPlayer 实例并显示其带宽信息。
// 你需要将其放置在 Slate 面板（如 SDockTab）中，并确保它的 Tick 函数能够被调用。
```

## Demo 示例

以下示例展示了如何在 C++ 中**创建一个简单的编辑器面板，用于加载和查看图像序列的带宽**。这综合了 `UImgMediaSource` 和 `SImgMediaBandwidth` 的使用。

```cpp
// MyMediaBandwidthTab.h
#pragma once

#include "CoreMinimal.h"
#include "Widgets/Docking/SDockTab.h"

class SImgMediaBandwidth;

class FMyMediaBandwidthTab
{
public:
    static const FName TabId;
    static void RegisterTabSpawner();
    static void UnregisterTabSpawner();

private:
    static TSharedRef<SDockTab> CreateTab(const FSpawnTabArgs& Args);
    static TSharedPtr<SImgMediaBandwidth> BandwidthWidget;
};
```

```cpp
// MyMediaBandwidthTab.cpp
#include "MyMediaBandwidthTab.h"
#include "ImgMediaEditor/Widgets/SImgMediaBandwidth.h"
#include "Widgets/Docking/SDockTab.h"
#include "Framework/Docking/TabManager.h"

const FName FMyMediaBandwidthTab::TabId = FName("MyMediaBandwidthTab");
TSharedPtr<SImgMediaBandwidth> FMyMediaBandwidthTab::BandwidthWidget;

void FMyMediaBandwidthTab::RegisterTabSpawner()
{
    FGlobalTabmanager::Get()->RegisterNomadTabSpawner(TabId,
        FOnSpawnTab::CreateStatic(&FMyMediaBandwidthTab::CreateTab))
        .SetDisplayName(FText::FromString(TEXT("Image Media Bandwidth")))
        .SetMenuType(ETabSpawnerMenuType::Hidden); // 可通过命令打开
}

void FMyMediaBandwidthTab::UnregisterTabSpawner()
{
    FGlobalTabmanager::Get()->UnregisterNomadTabSpawner(TabId);
}

TSharedRef<SDockTab> FMyMediaBandwidthTab::CreateTab(const FSpawnTabArgs& Args)
{
    // 创建带宽监控控件
    BandwidthWidget = SNew(SImgMediaBandwidth);

    // 创建并返回一个包含该控件的停靠标签页
    return SNew(SDockTab)
        .TabRole(ETabRole::NomadTab)
        [
            // 将带宽控件作为标签页的内容
            BandwidthWidget.ToSharedRef()
        ];
}

// 在你的编辑器模块启动函数中调用 RegisterTabSpawner()
// 在模块关闭函数中调用 UnregisterTabSpawner()
```

## 模块依赖

要使用 ImgMedia 插件，你的模块通常**无需直接依赖这些插件模块**，除非你需要直接调用其提供的编辑器工具类或底层功能。

| 模块 | 用途 |
|---|---|
| `OpenExrWrapper` | 用于读取和解析 OpenEXR 格式文件的核心库封装。 |
| `ExrReaderGpu` | 提供利用 GPU 加速 EXR 解码的功能。 |
| `MediaAssets` | 引擎核心媒体资产模块，`UImgMediaSource` 依赖于此。 |

**对于大多数项目**：只需在内容浏览器中创建 `UImgMediaSource` 和 `UMediaPlayer` 资产即可使用，无需在 `Build.cs` 中添加特殊依赖。
**对于需要扩展编辑器工具**：你的编辑器模块可能需要依赖 `ImgMediaEditor` 模块，并引入相应的头文件。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `edcd0d53` | [ImgMedia] refresh single-frame sequences on tile visibility changes | 优化单帧序列在瓦片可见性变化时的刷新逻辑。 |
| 2026-05-26 | `cf292c45` | [ImgMedia] Use AR-constrained view rect for tile mip selection | 在瓦片 Mip 选择时使用宽高比约束的视图矩形，提升视觉质量。 |
| 2026-05-26 | `96b8b04b` | Media IO: Fix to recent CL 54396736 for ImgMedia and NDI players emitting incorrect SourceOpened analytics | 修复了 ImgMedia 和 NDI 播放器发送错误 SourceOpened 分析事件的问题。 |
| 2026-05-23 | `42746f7a` | Media IO: Added additional engine analytics information to various media players and capture and pro | 为多种媒体播放器和采集源添加了额外的引擎分析信息。 |
| 2026-05-22 | `7d256b73` | [Media] Add shared Media category to the Level Editor Window menu | 在关卡编辑器的“窗口”菜单中添加了统一的“媒体”分类。 |

### 维护评价

-   **创建时间**：约 8 年前，是一个成熟的插件。
-   **近期活动**：在 2026 年 5 月仍有连续的提交，内容涉及功能优化（瓦片选择逻辑）、性能改进和错误修复。这表明该插件处于**积极维护**状态。
-   **功能稳定性**：作为影视和虚拟制片工作流的关键组件，其核心功能（播放 EXR 等序列）非常稳定。
-   **推荐程度**：**强烈推荐**用于任何涉及图像序列播放的专业工作流。它是引擎原生方案，性能经过优化，且仍在持续更新。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ImgMedia)
-   [官方文档](https://forums.unrealengine.com/showthread.php?46879-Media-Framework-Documentation-for-4-5-Preview) (Note: This link may point to older Media Framework docs, but the core concepts apply)
-   测试用例：引擎自动化测试中可能包含相关测试，但通常位于 `Engine/Tests` 目录下，而非插件目录内。