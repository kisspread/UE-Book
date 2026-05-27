# Media Viewer

> Media viewer to display and compare media.

| 属性 | 值 |
|---|---|
| 中文名 | 媒体查看器 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产，如库设置、书签状态） |
| 模块 | `MediaViewer` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaViewer) | |

## 用途

Media Viewer 是一个编辑器插件，旨在提供一个统一、可扩展的媒体查看和比较界面。它解决的核心问题是：在游戏或项目开发过程中，开发者（如纹理美术师、技术美术师、视频编辑器）需要频繁查看和比较各种类型的媒体资产（如纹理、材质、视频），但缺乏一个功能丰富、可定制化的工具。

该插件通过引入“媒体查看器”概念，允许用户：
1.  **加载与显示**：在编辑器中显示各种类型的媒体，包括纹理（Texture2D）、材质接口（MaterialInterface）、媒体源（MediaSource，如视频文件）。
2.  **A/B 对比**：支持同时加载两张媒体（位置 A 和位置 B），并提供可切换的垂直/水平分屏模式，方便进行视觉对比（例如，比较不同质量的纹理、两种材质的效果、渲染前后的画面等）。
3.  **精细查看**：提供一系列查看控制，如缩放、平移、旋转、镜像、像素网格覆盖、Mip 级别切换等，满足对媒体细节的检查需求。
4.  **媒体库管理**：内置一个可持久化的媒体库（Library），用户可以将常用的媒体项分组管理，并支持历史记录、快照等功能。

本质上，它是 Unreal Editor 内置资产查看器的一个功能更强大、可扩展的替代品，专注于媒体内容的查看与比较。

## 使用场景

-   你是一名**纹理美术师**，需要检查贴图的细节、像素对齐、不同 Mip 级别的表现。 → 使用 Media Viewer 打开 Texture2D，启用像素网格和自动过滤切换。
-   你是一名**技术美术师**，需要对比新旧两版材质在不同光照下的效果。 → 使用 Media Viewer 的 A/B 对比功能，左右分别加载两个材质。
-   你是一名**视频编辑器或动画师**，需要在编辑器内预览视频序列，并逐帧分析。 → 使用 Media Viewer 加载 MediaSource（如 .mp4 文件），利用其内置的播放控制和时间轴滑块。
-   你是一名**开发者**，需要检查程序化生成的 RenderTarget 的输出结果。 → 通过 C++ 或蓝图，将 RenderTarget 设置到 Media Viewer 中查看。
-   你希望**管理项目中常用的媒体资源**，建立分类目录，方便快速访问。 → 使用 Media Viewer 的侧边栏库功能，创建分组并添加项目。

## 蓝图用法

插件主要通过 `IMediaViewerModule` 接口提供蓝图功能。以下节点用于在编辑器中控制媒体查看器。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Open Tab` | 打开（或聚焦）默认的媒体查看器标签页。可传入 `FMediaViewerArgs` 进行配置。 | `IMediaViewerModule` |
| `Set Image (AssetData)` | 在查看器的指定位置（A 或 B）加载一个资产。 | `IMediaViewerModule` |
| `Set Image (Object)` | 在查看器的指定位置加载一个 UObject（如 Texture2D）。 | `IMediaViewerModule` |
| `Clear Image` | 清空指定位置的图像。 | `IMediaViewerModule` |
| `Get Library` | 获取全局共享的媒体库对象引用。 | `IMediaViewerModule` |
| `Create Library Item (AssetData)` | 为一个资产数据创建对应的库条目。 | `IMediaViewerModule` |
| `Has Image` | 查询指定位置是否已加载图像。 | `IMediaViewerModule` |

### 使用示例（蓝图描述）

**示例1：打开查看器并加载纹理**
1.  从 `IMediaViewerModule` 获取实例。
2.  调用 `Open Tab` 节点确保查看器窗口打开。
3.  构造一个 `FAssetData` 节点，引用目标纹理。
4.  调用 `Set Image (AssetData)`，将 `Position` 设为 `First`，`AssetData` 连接纹理引用。这将纹理加载到查看器的 A 位置。

**示例2：进行 A/B 对比**
1.  调用 `Open Tab` 并传入一个配置了 `bAllowABComparison=true` 的 `FMediaViewerArgs`。
2.  调用 `Set Image (AssetData)` 两次，分别将 `Position` 设置为 `First` 和 `Second`，并传入两个不同的材质或纹理资产。

**示例3：使用媒体库**
1.  通过 `Get Library` 获取库对象。
2.  使用库对象的 `Add Item to Group` 等方法，将常用媒体项组织到自定义分组中。
3.  用户之后可以在查看器的侧边栏库面板中快速访问这些项。

## C++ 用法

核心交互通过 `IMediaViewerModule` 单例接口进行。

### 头文件引入

```cpp
#include "IMediaViewerModule.h"
```

### 基本用法

```cpp
// (Source: 测试用例或编辑器工具代码中常见的初始化模式)
#include "IMediaViewerModule.h"
#include "MediaViewer.h" // 用于 FMediaViewerArgs

void OpenMediaViewerForTexture(UTexture2D* InTexture)
{
    // 获取媒体查看器模块
    UE::MediaViewer::IMediaViewerModule& MediaViewerModule = UE::MediaViewer::IMediaViewerModule::Get();

    // 配置查看器参数
    UE::MediaViewer::FMediaViewerArgs ViewerArgs;
    ViewerArgs.bShowSidebar = true; // 显示媒体库侧边栏

    // 打开（或激活）查看器标签页
    MediaViewerModule.OpenTab(ViewerArgs);

    // 将纹理设置到查看器的 A 位置
    MediaViewerModule.SetImage(UE::MediaViewer::EMediaImageViewerPosition::First, InTexture);
}
```

### 进阶用法：注册自定义媒体查看器工厂

你可以通过实现 `IMediaImageViewerFactory` 接口，来让 Media Viewer 支持你自定义的资产或对象类型。

```cpp
// (Source: 参考 MediaViewer/Private/ImageViewers/ 下的实现，如 Texture2DImageViewer.h)
#include "IMediaViewerModule.h"
#include "ImageViewer/IMediaImageViewerFactory.h"
#include "MediaImageViewer.h"

class FMyCustomImageViewer : public UE::MediaViewer::FMediaImageViewer
{
public:
    FMyCustomImageViewer(/* ... */)
        : FMediaImageViewer(/* ... */)
    {}

    virtual TSharedPtr<FMediaViewerLibraryItem> CreateLibraryItem() const override;
    virtual void PaintImage(FMediaImageSlatePaintParams& InPaintParams, const FMediaImageSlatePaintGeometry& InPaintGeometry) override;
    // ... 实现其他必要的虚函数
};

struct FMyCustomImageViewerFactory : public UE::MediaViewer::IMediaImageViewerFactory
{
    virtual bool SupportsAsset(const FAssetData& InAssetData) const override
    {
        // 判断资产是否是你的自定义类型
        return InAssetData.GetClass() == UMyCustomAsset::StaticClass();
    }

    virtual TSharedPtr<UE::MediaViewer::FMediaImageViewer> CreateImageViewer(const FAssetData& InAssetData) const override
    {
        UMyCustomAsset* Asset = Cast<UMyCustomAsset>(InAssetData.GetAsset());
        if (Asset)
        {
            return MakeShared<FMyCustomImageViewer>(Asset);
        }
        return nullptr;
    }
    // ... 实现其他虚函数，如 SupportsObject, CreateLibraryItem
};

// 在你的模块启动时注册工厂
void MyModule::StartupModule()
{
    if (UE::MediaViewer::IMediaViewerModule* MediaViewerModule = FModuleManager::GetModulePtr<UE::MediaViewer::IMediaViewerModule>("MediaViewer"))
    {
        MediaViewerModule->RegisterFactory(
            FName(TEXT("MyCustomFactory")),
            MakeShared<FMyCustomImageViewerFactory>()
        );
    }
}

void MyModule::ShutdownModule()
{
    if (UE::MediaViewer::IMediaViewerModule* MediaViewerModule = FModuleManager::GetModulePtr<UE::MediaViewer::IMediaViewerModule>("MediaViewer"))
    {
        MediaViewerModule->UnregisterFactory(FName(TEXT("MyCustomFactory")));
    }
}
```

## Demo 示例

一个可编译的最小示例，演示如何创建一个显示指定纹理的媒体查看器。

**MyMediaViewerTool.h**
```cpp
// MyMediaViewerTool.h
#pragma once

#include "CoreMinimal.h"

class UTexture2D;

class FMyMediaViewerTool
{
public:
    static void ShowTextureInViewer(UTexture2D* Texture);
};
```

**MyMediaViewerTool.cpp**
```cpp
// MyMediaViewerTool.cpp
#include "MyMediaViewerTool.h"
#include "IMediaViewerModule.h"
#include "MediaViewer.h" // For FMediaViewerArgs

void FMyMediaViewerTool::ShowTextureInViewer(UTexture2D* Texture)
{
    if (!Texture)
    {
        return;
    }

    UE::MediaViewer::IMediaViewerModule& MediaViewerModule = UE::MediaViewer::IMediaViewerModule::Get();

    // 使用默认配置打开查看器
    UE::MediaViewer::FMediaViewerArgs Args;
    MediaViewerModule.OpenTab(Args);

    // 将纹理设置到 A 位置
    MediaViewerModule.SetImage(UE::MediaViewer::EMediaImageViewerPosition::First, Texture);
}
```

## 模块依赖

该插件的 `.uplugin` 文件声明了对其他插件的依赖。要使用 Media Viewer，你的编辑器模块通常不需要直接依赖它，因为它是通过编辑器 UI 交互的。但如果你计划**扩展**它（如注册自定义工厂），你需要确保你的模块的 `.Build.cs` 文件中依赖以下模块：

| 模块 | 用途 |
|---|---|
| `MediaViewer` | 插件的核心模块，提供 `IMediaViewerModule`, `FMediaImageViewer`, `IMediaImageViewerFactory` 等接口。 |
| `MediaStream` | 提供 `UMediaStream` 等用于处理流媒体（如视频）播放的功能，是查看视频类型媒体所必需的。 |
| `MediaPlayerEditor` | 提供与媒体播放器编辑器相关的 UI 和功能集成。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `bb77550d` | [MediaViewer] Making color picker TMV-Aware | 使颜色拾取器能够感知媒体查看器，可能实现了颜色拾取与查看器的交互。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下 double 常量截断为 float 产生警告的代码。 |
| 2026-05-13 | `bd09d694` | [ImgMedia] Refresh paused-player tiles when visibility changes | [ImgMedia] 当可见性改变时刷新暂停播放器的瓦片。 |
| 2026-05-12 | `4fc7c47c` | [MediaViewer] Fix drop-target image identification | 修复拖放目标图像识别错误的问题。 |
| 2026-05-12 | `0d1adb1e` | [MediaViewer] Fix tile visibility provider for non-tiled sources | 修复非瓦片源（如普通视频）的瓦片可见性提供程序问题。 |

### 维护评价

-   **创建时间**：插件创建于 2025 年 9 月，历史很短。
-   **近期更新频率**：从 git 记录看，在 2026 年 5 月仍有密集的功能和 bug 修复提交，表明插件处于**活跃开发和维护**中。
-   **实验性状态**：`.uplugin` 明确标记 `IsBetaVersion: true`，且默认未启用。这意味着它是一个功能可能不完全、API 可能变动的实验性插件。
-   **功能完善度**：源码量（101 个文件）较大，功能复杂（库管理、多种图像查看器、A/B 对比、丰富的查看设置），已具备相当的可用性。
-   **已知限制**：作为 Beta 版本，可能在稳定性、性能或边界情况处理上存在不足。
-   **推荐使用**：**推荐**给需要强大媒体查看和对比功能的开发者。虽然标记为实验性，但从近期的活跃提交来看，Epic 正在积极开发它。可以用于提高美术和开发工作流的效率，但应留意可能的版本更新带来的变化。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaViewer)