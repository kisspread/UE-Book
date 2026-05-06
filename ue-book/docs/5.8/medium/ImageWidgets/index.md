# ImageWidgets

> Generic Slate widgets for displaying images and image-like content, and content related to images.

| 属性 | 值 |
|---|---|
| 中文名 | 图像控件 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（示例代码 ColorViewerSample） |
| 模块 | `ImageWidgets` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-03-21 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/ImageWidgets) | |

## 用途

该插件提供一组通用的 Slate 控件，用于在编辑器环境中显示图像、类图像内容以及与图像相关的元数据。核心组件包括：

- `SImageViewport`：一个可交互的 2D 视口，支持缩放、平移、MIP 选择、AB 比较和覆盖工具栏。
- `SImageCatalog`：一个可分组、支持多选的缩略图目录，用于展示并选择图像。
- `IImageViewer` 接口：将图像数据源与控件解耦，允许任意数据类型（纹理、颜色、缓冲区等）作为“图像”绘制。

插件解决现有编辑器缺乏统一、可复用的图像查看组件的问题，适用于需要可视化 2D 纹理、渲染目标、调色板、逐像素数据等的编辑器工具。

## 使用场景

- 开发纹理查看器、材质预览器、渲染图分析器等编辑器面板。
- 需要交互式缩放/平移、MIP 级别切换、AB 并排比较的功能。
- 需要同时展示多个缩略图并允许用户选择、分组的目录控件。
- 基于 `IImageViewer` 接口快速接入任意 2D 数据源。

## 蓝图用法

本插件未提供蓝图可调用函数。所有功能通过 C++ Slate 组件使用。

## C++ 用法

### 头文件引入

```cpp
#include "SImageViewport.h"
#include "SImageCatalog.h"
#include "IImageViewer.h"
```

### 基本用法

1. **实现 `IImageViewer` 接口**，将您的图像数据适配到插件：

```cpp
class FMyImageViewer : public UE::ImageWidgets::IImageViewer
{
public:
    virtual FImageInfo GetCurrentImageInfo() const override
    {
        return FImageInfo{ CurrentGuid, ImageSize, NumMips, true };
    }
    virtual void DrawCurrentImage(FViewport* Viewport, FCanvas* Canvas,
                                   const FDrawProperties& Properties) override
    {
        // 使用 Properties.GetPlacement().Offset/Size 在画布上绘制
        Canvas->DrawTile(Properties.GetPlacement().Offset.X,
                         Properties.GetPlacement().Offset.Y,
                         Properties.GetPlacement().Size.X,
                         Properties.GetPlacement().Size.Y,
                         0, 0, 1, 1,
                         FLinearColor::White, YourTexture,
                         Properties.GetMip().MipLevel > 0.0f);
    }
    // 其他虚函数：GetCurrentImagePixelColor, OnImageSelected, IsValidImage, GetImageName
};
```

2. **构建控件并添加到布局**（参考 `ColorViewerSample`）：

```cpp
TSharedPtr<FMyImageViewer> MyViewer = MakeShared<FMyImageViewer>();

// 创建目录
SImageCatalog::FArguments CatalogArgs;
CatalogArgs.DefaultGroupName(TEXT("All Images"));
CatalogArgs.DefaultGroupHeading(FText::FromString("All"));
// 填充数据（外部提供 FImageCatalogItemData 列表）
TArray<TSharedPtr<FImageCatalogItemData>> Items;
Items.Add(MakeShared<FImageCatalogItemData>(Guid, Brush, Name, Info, ToolTip));
SAssignNew(Catalog, SImageCatalog, MyViewer, Items) // 实际构造方式参见头文件
    .OnItemSelected(this, &FMyWidget::OnCatalogItemSelected);

// 创建视口
SAssignNew(Viewport, SImageViewport, MyViewer)
    .ViewportSize(FVector2D(800, 600));

// 组合布局
ChildSlot
[
    SNew(SSplitter)
    + SSplitter::Slot().Value(0.3f)
    [
        Catalog.ToSharedRef()
    ]
    + SSplitter::Slot().Value(0.7f)
    [
        Viewport.ToSharedRef()
    ]
];
```

### 进阶用法

**AB 比较**：通过 `FImageABComparison` 和 `SImageViewport::FStatusBarExtender` 实现并排对比。

```cpp
FImageABComparison ABComp(...);

// 在视口构造时绑定
SAssignNew(Viewport, SImageViewport, MyViewer)
    .ABComparison(&ABComp)
    .ControllerSettings(FImageWidgets::SImageViewport::FControllerSettings().DefaultZoomMode(SImageViewport::FControllerSettings::EDefaultZoomMode::Fit))
    .DrawSettings(SImageViewport::FDrawSettings().bBorderEnabled(true).BorderColor(FLinearColor::White));

// 自定义状态栏扩展
TSharedPtr<SImageViewport::FStatusBarExtender> StatusExt = MakeShared<SImageViewport::FStatusBarExtender>();
StatusExt->AddExtension("Zoom", EExtensionHook::After, CommandList,
    SImageViewport::FStatusBarExtender::FDelegate::CreateLambda([](SHorizontalBox& Box)
    {
        Box.AddSlot().AutoWidth()
        [
            SNew(STextBlock).Text(INVTEXT("Custom Info"))
        ];
    }));
Viewport->SetStatusBarExtender(StatusExt);
```

## Demo 示例

以下是一个最小可编译的示例，展示如何使用 `SImageViewport` 显示纯色方块。

**MyImageWidgetDemo.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "IImageViewer.h"

class FColorImageViewer : public UE::ImageWidgets::IImageViewer
{
public:
    FColorImageViewer(FColor InColor) : Color(InColor) {}

    virtual FImageInfo GetCurrentImageInfo() const override
    {
        return { FGuid::NewGuid(), FIntPoint(256,256), 1, true };
    }
    virtual void DrawCurrentImage(FViewport*, FCanvas* Canvas,
                                   const UE::ImageWidgets::IImageViewer::FDrawProperties& Properties) override
    {
        const auto& Place = Properties.GetPlacement();
        Canvas->DrawTile(Place.Offset.X, Place.Offset.Y,
                         Place.Size.X, Place.Size.Y,
                         0,0,1,1, Color);
    }
    virtual TOptional<TVariant<FColor, FLinearColor>> GetCurrentImagePixelColor(
        FIntPoint, int32) const override { return {}; }
    virtual void OnImageSelected(const FGuid&) override {}
    virtual bool IsValidImage(const FGuid&) const override { return true; }
    virtual FText GetImageName(const FGuid&) const override { return FText::FromString("Demo Color"); }

private:
    FColor Color;
};
```

**MyImageWidgetDemo.cpp**

```cpp
#include "MyImageWidgetDemo.h"
#include "SImageViewport.h"
#include "Widgets/Layout/SBorder.h"
#include "Widgets/SBoxPanel.h"

TSharedRef<SWidget> CreateDemo()
{
    TSharedPtr<FColorImageViewer> Viewer = MakeShared<FColorImageViewer>(FColor::Red);
    return SNew(SBorder)
    [
        SNew(SImageWidgets::SImageViewport, Viewer)
            .ViewportSize(FVector2D(400,400))
    ];
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate/Editor 模块）。使用该插件的模块需在 `Build.cs` 中添加：

```csharp
PrivateDependencyModuleNames.AddRange(new[] { "ImageWidgets" });
```

## 维护状态

### 近期更新

- 2026-04-14 `35e60df1` Migrate UE_LOG to UE_LOGF.
- 2026-03-23 `fb33fca8` Fix crash opening TextureGraph: initialize `_ToolbarExtenderStyle` in `SImageViewport`
- 2026-03-21 `3a2a91d3` ImageWidgets: Move out of Experimental

### 维护评价

插件发布于 2026 年 3 月，非常新，已从实验状态移出。最近有活跃的 bug 修复和日志迁移，表明团队正在积极维护。目前没有已知限制。推荐用于需要自定义图像查看器的编辑器开发。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/ImageWidgets)
- 官方文档：暂无
- [示例代码（ColorViewerSample）](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/ImageWidgets/Source/ImageWidgets/Private/ColorViewerSample)