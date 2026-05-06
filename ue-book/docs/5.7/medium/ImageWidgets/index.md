# Image Widgets

> Generic Slate widgets for displaying images and image-like content, and content related to images.

| 属性 | 值 |
|---|---|
| 中文名 | 图像小部件 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（示例代码） |
| 模块 | `ImageWidgets` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-09-07 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ImageWidgets) | |

## 用途

该插件提供了一套通用的 Slate 小部件，用于在编辑器环境内显示、浏览和对比图像（或任何 2D 的、由轴对齐矩形界定的内容）。它解决了需要在内置纹理编辑器之外独立展示图像、进行缩放/平移操作、以及并排或覆盖对比不同图像（A/B 对比）的需求。插件本身不持有具体图像数据，而是通过接口 `IImageViewer` 让调用方提供绘制参数，从而保持与具体图像格式的解耦。

主要包含两个核心小部件：
- **SImageCatalog**：一个可分组、支持多选和右键菜单的图像目录列表。
- **SImageViewport**：一个功能完整的图像视口，支持缩放、平移、MIP 选择、覆盖层（Overlay）、以及 A/B 对比。

插件还附带一个简单的 `ColorViewer` 示例，演示如何实现 `IImageViewer` 接口并与这些小部件集成。

## 使用场景

- 你需要在编辑器中创建一个自定义的图像浏览器或纹理查看工具。
- 你需要实现两个相似图像（如渲染前后、压缩前后）的并排或分屏对比。
- 你希望为已有图像数据提供标准化的缩放、平移、MIP 切换等交互。
- 你正在开发一个依赖于图像预览的编辑器模块（如关卡截图、艺术资产浏览器）。

## 蓝图用法

该插件的所有小部件均为 C++ Slate 组件，**不暴露任何 BlueprintCallable 函数或 BlueprintReadWrite 属性**。因此无法在蓝图中直接使用。交互均需通过 C++ 编写 Slate UI。

## C++ 用法

### 头文件引入

```cpp
#include "IImageViewer.h"           // 图像查看器接口
#include "SImageViewport.h"         // 图像视口
#include "SImageCatalog.h"          // 图像目录
```

### 基本用法

你需要实现 `IImageViewer` 接口以提供图像数据。以下代码片段来自 `ColorViewer` 示例（`Engine/Plugins/Experimental/ImageWidgets/Source/ImageWidgets/Private/ColorViewerSample/ColorViewer.cpp`）：

```cpp
class FColorViewer : public UE::ImageWidgets::IImageViewer
{
public:
    // 返回当前图像的信息（尺寸、MIP 数、有效性等）
    virtual FImageInfo GetCurrentImageInfo() const override
    {
        return FImageInfo{ .Guid = CurrentGuid, .Size = Size, .NumMips = 1, .bIsValid = true };
    }

    // 实际绘制图像到 Canvas
    virtual void DrawCurrentImage(FViewport* Viewport, FCanvas* Canvas, const FDrawProperties& Properties) override
    {
        FDrawProperties::FPlacement Placement = Properties.Placement;
        // 使用 Placement.Offset, Placement.Size, Properties.Mip 等绘制颜色矩形
        // ...
    }

    // 查询像素颜色（用于拾色器等）
    virtual TOptional<TVariant<FColor, FLinearColor>> GetCurrentImagePixelColor(FIntPoint PixelCoords, int32 MipLevel) const override
    {
        // 返回颜色
    }
    // ... 其他接口方法
};
```

然后构建视口和目录：

```cpp
using namespace UE::ImageWidgets;

TSharedPtr<FColorViewer> ColorViewer = MakeShared<FColorViewer>();

// 构建图像视口
SImageViewport::FArguments ViewportArgs;
ViewportArgs._ImageViewer = ColorViewer;
// 可选的绘制设置、控制器设置等
SAssignNew(Viewport, SImageViewport, GetAssetEditorWidgetsHost())
    .ImageViewer(ColorViewer)
    .DrawSettings(SImageViewport::FDrawSettings{...})
    .ControllerSettings(SImageViewport::FControllerSettings{...});

// 构建图像目录
SAssignNew(Catalog, SImageCatalog)
    .DefaultGroupName(TEXT("All"))
    .DefaultGroupHeading(LOCTEXT("AllGroup", "All"))
    .OnItemSelected(FOnItemSelected::CreateLambda([&](const FGuid& Guid) {
        ColorViewer->OnImageSelected(Guid);
    }));
```

### 进阶用法

**A/B 对比**：通过 `SImageViewport` 的 `FControllerSettings` 可以启用 A/B 对比。需要提供 `FImageABComparison` 对象，并设置两个图像的 GUID。

```cpp
// 设置 A/B 对比
FImageABComparison ABComparison(
    FImageABComparison::FImageIsValid::CreateRaw(ColorViewer.Get(), &FColorViewer::IsValidImage),
    FImageABComparison::FGetCurrentImageGuid::CreateRaw(ColorViewer.Get(), &FColorViewer::GetCurrentGuid),
    FImageABComparison::FGetImageName::CreateRaw(ColorViewer.Get(), &FColorViewer::GetImageName)
);
ABComparison.SetABComparison(FImageABComparison::EAorB::A, GuidA);
ABComparison.SetABComparison(FImageABComparison::EAorB::B, GuidB);

SImageViewport::FControllerSettings ControllerSettings;
ControllerSettings.ABComparison = &ABComparison;
// ...
```

**工具栏扩展**：通过 `SImageViewport::FStatusBarExtender` 或 `FExtender` 可以在视口工具栏上添加自定义按钮。

```cpp
TSharedPtr<FExtender> ToolbarExtender = MakeShared<FExtender>();
ToolbarExtender->AddToolBarExtension(
    "Left",
    EExtensionHook::After,
    CommandList,
    FToolBarExtensionDelegate::CreateRaw(this, &FMyWidget::AddCustomButtons)
);

SImageViewportToolbar::FConstructParameters ToolbarParams;
ToolbarParams.ToolbarExtender = ToolbarExtender;
// ...
```

## Demo 示例

以下是一个最小化的工作示例，它创建一个简单的图像视口并显示一个彩色矩形图像。完整可编译示例可参考插件自带的 `ColorViewerSample`（位于 `Source/Private/ColorViewerSample/`）。

**ColorViewerDemo.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "SEditorViewport.h"
#include "IImageViewer.h"

class FColorViewerSample : public UE::ImageWidgets::IImageViewer
{
public:
    FColorViewerSample()
    {
        // 初始化一个简单的图像（128x128 红色矩形）
        CurrentGuid = FGuid::NewGuid();
        Size = FIntPoint(128, 128);
        Color = FColor::Red;
    }

    // IImageViewer interface
    virtual FImageInfo GetCurrentImageInfo() const override
    {
        return { CurrentGuid, Size, 1, true };
    }

    virtual void DrawCurrentImage(FViewport* Viewport, FCanvas* Canvas, const FDrawProperties& Properties) override
    {
        // 使用 FDrawingCanvas 或其他方式绘制填充矩形
        FCanvasBoxItem BoxItem(Properties.Placement.Offset, Properties.Placement.Size);
        BoxItem.SetColor(Color);
        Canvas->DrawItem(BoxItem);
    }

    virtual TOptional<TVariant<FColor, FLinearColor>> GetCurrentImagePixelColor(FIntPoint PixelCoords, int32 MipLevel) const override
    {
        return Color;
    }

    virtual void OnImageSelected(const FGuid& Guid) override {}
    virtual bool IsValidImage(const FGuid& Guid) const override { return Guid == CurrentGuid; }
    virtual FText GetImageName(const FGuid& Guid) const override { return FText::FromString("Red Square"); }

private:
    FGuid CurrentGuid;
    FIntPoint Size;
    FColor Color;
};
```

**ColorViewerDemo.cpp** (省略 `Build.cs` 和模块注册，仅展示如何使用)
```cpp
#include "ColorViewerDemo.h"
#include "SImageViewport.h"
#include "FColorViewerSample.h"

// 在你的编辑器模块中，例如构造一个 Slate 窗口时
TSharedRef<SOverlay> MakeImageViewerDemo()
{
    auto ColorViewer = MakeShared<FColorViewerSample>();
    auto Viewport = SNew(UE::ImageWidgets::SImageViewport, nullptr)
                        .ImageViewer(ColorViewer)
                        .DrawSettings({ FLinearColor::Black, false, 1.f, FLinearColor::White });

    return SNew(SOverlay) + SOverlay::Slot()
        .HAlign(HAlign_Fill)
        .VAlign(VAlign_Fill)
        [
            Viewport.ToSharedRef()
        ];
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| 无特殊依赖 | 仅标准编辑器相关模块（EditorStyle, EditorWidgets, LevelEditor 等） |

## 维护状态

### 近期更新

- 2025-07-12 3413adf — Ran UnrealCodeFixup to fix dll storage
- 2025-06-10 bb3758b — SEditorViewport::MakeViewportToolbar() is deprecated.
- 2024-10-15 21d9de1 — ImageWidgets: Fix viewport showing incorrect zoom label when using DPI scaling
- 2024-09-09 32914ad — ColorViewerWidget: Fixed duplicate LOCTEXT key 'DeleteGroupItems'
- 2024-09-07 688daee — ImageWidgets: initial implementation

### 维护评价

该插件创建于 2024 年 9 月，至今约 1 年。最近一次实质性更新在 2025 年 7 月（修复 DPI 缩放标签问题），总体处于活跃维护状态。代码结构清晰，接口设计合理，推荐用于需要自定义图像查看工具的场景。作为实验性插件（`IsExperimentalVersion=true`），其 API 可能在后续版本有调整，但核心功能稳定。

## 相关链接

- [源码目录](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ImageWidgets)
- [示例代码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ImageWidgets/Source/ImageWidgets/Private/ColorViewerSample)