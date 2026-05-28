# Image Widgets

> Generic Slate widgets for displaying images and image-like content, and content related to images.

| 属性 | 值 |
|---|---|
| 中文名 | 图像控件 |
| 分类 | Other |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ImageWidgets` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-03-21 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/ImageWidgets) | |

## 用途

ImageWidgets 为 Unreal Editor 中的 2D 图像查看/编辑工具提供**通用 Slate 控件框架**。它不直接处理任何图像格式的渲染，而是通过 `IImageViewer` 接口将实际图像绘制逻辑委托给使用方实现，自身只负责：

1. **图像目录浏览**（`SImageCatalog`）：提供带缩略图、分组、多选、上下文菜单的图像列表，类似一个轻量级"内容浏览器"。
2. **图像视口交互**（`SImageViewport`）：提供平移、缩放（自适应/填充）、MIP 级别切换、AB 对比、颜色拾取、分辨率显示等功能的 2D 视口。

插件从 Experimental 目录迁移而来，目前仍处于 Beta 状态，供引擎内部编辑器工具（如 TextureGraph）和外部工具开发者复用。

## 使用场景

- 你在构建纹理查看器/编辑器 → 使用 `SImageViewport` + `IImageViewer` 实现
- 你需要在工具面板中浏览大量图像缩略图 → 使用 `SImageCatalog`
- 你需要对比两张纹理的差异（如压缩前后）→ 启用 `SImageViewport` 的 AB 对比功能
- 你需要在自定义编辑器工具中嵌入可缩放的 2D 图像预览 → 复用整个控件集

## 蓝图用法

本插件的所有核心类均为 Slate 控件（`SCompoundWidget`、`SEditorViewport`），不暴露 `UFUNCTION`/`UPROPERTY`，**无蓝图 API**。仅可通过 C++ 使用。

## C++ 用法

### 头文件引入

```cpp
#include "SImageCatalog.h"
#include "SImageViewport.h"
#include "IImageViewer.h"
```

### 基本用法：实现 IImageViewer 接口

所有图像渲染逻辑通过实现 `IImageViewer` 接口提供。以下是最小实现骨架（参考 `ColorViewer.h`）：

```cpp
// MyImageViewer.h
#include "IImageViewer.h"

class FMyImageViewer final : public UE::ImageWidgets::IImageViewer
{
public:
    // 返回当前要显示的图像元信息
    virtual FImageInfo GetCurrentImageInfo() const override
    {
        FImageInfo Info;
        Info.Guid = CurrentImageGuid;
        Info.Size = CurrentImageSize;   // e.g. 512x512
        Info.NumMips = 0;               // 无 MIP 支持设为 0
        Info.bIsValid = true;
        return Info;
    }

    // 在 Canvas 上绘制图像
    virtual void DrawCurrentImage(FViewport* Viewport, FCanvas* Canvas,
        const FDrawProperties& Properties) override
    {
        // 根据 Properties.Placement 中的 Offset/Size/ZoomFactor 绘制内容
        // Properties.Mip.MipLevel 指定 MIP 级别
        // Properties.ABComparison 指定 AB 对比状态
    }

    // 返回指定像素坐标处的颜色值
    virtual TOptional<TVariant<FColor, FLinearColor>> GetCurrentImagePixelColor(
        FIntPoint PixelCoords, int32 MipLevel) const override
    {
        return {}; // 无有效像素时返回空
    }

    // 图像被选中时的回调
    virtual void OnImageSelected(const FGuid& Guid) override
    {
        CurrentImageGuid = Guid;
        // 更新内部状态以切换当前显示的图像
    }

    // 检查 GUID 是否代表一个可用图像
    virtual bool IsValidImage(const FGuid& Guid) const override
    {
        return ImageMap.Contains(Guid);
    }

    // 返回图像名称（用于 UI 显示）
    virtual FText GetImageName(const FGuid& Guid) const override
    {
        return FText::FromString(TEXT("My Image"));
    }

private:
    FGuid CurrentImageGuid;
    FIntPoint CurrentImageSize = FIntPoint(512, 512);
    TMap<FGuid, /* your data type */> ImageMap;
};
```

> 来源：`Source/ImageWidgets/Public/IImageViewer.h`

### 基本用法：创建图像目录

```cpp
using namespace UE::ImageWidgets;

// 创建目录控件
SAssignNew(Catalog, SImageCatalog)
    .DefaultGroupName(NAME_None)
    .DefaultGroupHeading(FText::FromString(TEXT("All Images")))
    .SelectionMode(ESelectionMode::Multi)
    .bAllowSelectionAcrossGroups(true)
    .bShowEmptyGroups(false)
    .OnItemSelected_Lambda([this](const FGuid& Guid)
    {
        // 切换视口中的当前图像
        ImageViewer->OnImageSelected(Guid);
        Viewport->RequestRedraw();
    })
    .OnGetGroupContextMenu_Lambda([this](FName GroupName) -> TSharedPtr<SWidget>
    {
        // 返回自定义右键菜单，或 SNullWidget::NullWidget
        return SNullWidget::NullWidget;
    })
    .OnGetItemsContextMenu_Lambda([this](const TArray<FGuid>& Guids) -> TSharedPtr<SWidget>
    {
        return SNullWidget::NullWidget;
    });

// 添加自定义分组
Catalog->AddGroup(FName("Favorites"), FText::FromString(TEXT("收藏夹")));

// 向默认组添加项目
FImageCatalogItemData ItemData(FGuid::NewGuid(), ThumbnailBrush, 
    FText::FromString(TEXT("Texture")), FText::FromString(TEXT("256x256")),
    FText::FromString(TEXT("A sample texture")));
Catalog->AddItem(MakeShared<FImageCatalogItemData>(MoveTemp(ItemData)));

// 向指定组添加项目
Catalog->AddItem(AnotherItem, FName("Favorites"));
```

> 来源：`Source/ImageWidgets/Public/SImageCatalog.h`

### 进阶用法：创建图像视口

```cpp
using namespace UE::ImageWidgets;

auto ImageViewerRef = MakeSharedRef<IImageViewer>(MyImageViewer);

// 定义绘制设置
SImageViewport::FDrawSettings DrawSettings;
DrawSettings.ClearColor = FLinearColor(0.1f, 0.1f, 0.1f);
DrawSettings.bBorderEnabled = true;
DrawSettings.BorderThickness = 2.0f;
DrawSettings.bBackgroundCheckerEnabled = true;
DrawSettings.BackgroundCheckerSize = 16;

// 定义控制器设置
SImageViewport::FControllerSettings ControllerSettings;
ControllerSettings.DefaultZoomMode = SImageViewport::FControllerSettings::EDefaultZoomMode::Fit;
ControllerSettings.bZoomOnResize = true;

// 创建工具栏扩展
auto ToolbarExtender = MakeShared<FExtender>();
ToolbarExtender->AddToolBarExtension("ToolbarCenter", EExtensionHook::After,
    CommandList, FToolBarExtensionDelegate::CreateLambda(
        [](FToolBarBuilder& Builder)
        {
            Builder.AddToolBarButton(/* custom action */);
        }));

// 创建状态栏扩展
auto StatusBarExtender = MakeShared<SImageViewport::FStatusBarExtender>();
StatusBarExtender->AddExtension("StatusBarLeft", EExtensionHook::After,
    CommandList, SImageViewport::FStatusBarExtender::FDelegate::CreateLambda(
        [](SHorizontalBox& Box)
        {
            Box.AddSlot().AutoWidth() /* custom widget */;
        }));

// 创建视口
SAssignNew(Viewport, SImageViewport)
    .ToolbarExtender(ToolbarExtender)
    .StatusBarExtender(StatusBarExtender)
    .DrawSettings(DrawSettings)
    .bABComparisonEnabled(true)
    .ControllerSettings(ControllerSettings)
    (ImageViewerRef); // 传入 IImageViewer 实现
```

> 来源：`Source/ImageWidgets/Public/SImageViewport.h`、`Source/ImageWidgets/Private/ColorViewerSample/ColorViewerWidget.h`

### 进阶用法：AB 对比与像素拾取

```cpp
// 获取光标下的像素坐标（用于颜色拾取）
auto Result = Viewport->GetPixelCoordinatesUnderCursor();
if (Result.bIsValid)
{
    int32 MipLevel = 0;
    auto Color = ImageViewer->GetCurrentImagePixelColor(
        FIntPoint(Result.Coordinates.X, Result.Coordinates.Y), MipLevel);
    if (Color.IsSet())
    {
        // 处理颜色值（可能是 FColor 或 FLinearColor）
    }
}

// 重置视口控制器（如图像尺寸变化后）
Viewport->ResetController(ImageSize);
Viewport->ResetZoom(ImageSize);
Viewport->ResetMip();

// 强制重绘
Viewport->RequestRedraw();
```

> 来源：`Source/ImageWidgets/Public/SImageViewport.h`

## Demo 示例

以下是一个最小可编译示例，展示如何创建一个带目录和视口的图像查看面板：

```cpp
// SimpleImageViewer.h
#pragma once

#include "IImageViewer.h"
#include "SImageCatalog.h"
#include "SImageViewport.h"
#include "Widgets/Layout/SSplitter.h"

class FSimpleImageViewer final : public UE::ImageWidgets::IImageViewer
{
public:
    virtual FImageInfo GetCurrentImageInfo() const override
    {
        FImageInfo Info;
        Info.Guid = CurrentGuid;
        Info.Size = FIntPoint(512, 512);
        Info.NumMips = 0;
        Info.bIsValid = CurrentGuid.IsValid();
        return Info;
    }

    virtual void DrawCurrentImage(FViewport* Viewport, FCanvas* Canvas,
        const FDrawProperties& Properties) override
    {
        // 在此处绘制你的图像内容
        // 使用 Properties.Placement 中的 Offset 和 Size 确定绘制位置
    }

    virtual TOptional<TVariant<FColor, FLinearColor>> GetCurrentImagePixelColor(
        FIntPoint PixelCoords, int32 MipLevel) const override { return {}; }

    virtual void OnImageSelected(const FGuid& Guid) override { CurrentGuid = Guid; }
    virtual bool IsValidImage(const FGuid& Guid) const override { return Guid.IsValid(); }
    virtual FText GetImageName(const FGuid& Guid) const override
    {
        return FText::FromString(TEXT("Image"));
    }

    FGuid CurrentGuid;
};

class SSimpleImageViewerPanel : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SSimpleImageViewerPanel) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& Args)
    {
        ImageViewer = MakeShared<FSimpleImageViewer>();
        auto ViewerRef = StaticCastSharedRef<UE::ImageWidgets::IImageViewer>(ImageViewer.ToSharedRef());

        ChildSlot
        [
            SNew(SSplitter)
            .Orientation(Orient_Horizontal)
            + SSplitter::Slot()
            .Value(0.3f)
            [
                SAssignNew(Catalog, UE::ImageWidgets::SImageCatalog)
                    .OnItemSelected_Lambda([this](const FGuid& Guid)
                    {
                        ImageViewer->OnImageSelected(Guid);
                        if (Viewport.IsValid()) Viewport->RequestRedraw();
                    })
            ]
            + SSplitter::Slot()
            .Value(0.7f)
            [
                SAssignNew(Viewport, UE::ImageWidgets::SImageViewport)
                    .bABComparisonEnabled(false)
                    (ViewerRef)
            ]
        ];

        // 添加一个示例项目
        FSlateBrush Brush;
        auto Item = MakeShared<UE::ImageWidgets::FImageCatalogItemData>(
            FGuid::NewGuid(), Brush, FText::FromString(TEXT("Sample")),
            FText::FromString(TEXT("512x512")), FText::FromString(TEXT("A sample entry")));
        Catalog->AddItem(Item);
    }

private:
    TSharedPtr<FSimpleImageViewer> ImageViewer;
    TSharedPtr<UE::ImageWidgets::SImageCatalog> Catalog;
    TSharedPtr<UE::ImageWidgets::SImageViewport> Viewport;
};
```

> 参考：`Source/ImageWidgets/Private/ColorViewerSample/ColorViewerWidget.h`、`Source/ImageWidgets/Private/ColorViewerSample/ColorViewer.h`

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate/SlateCore/UnrealEd 等）。

使用方的 `Build.cs` 需添加：

```cpp
PublicDependencyModuleNames.Add("ImageWidgets");
```

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧版 UE_LOG 宏迁移为新版 UE_LOGF 宏 |
| 2026-03-23 | `fb33fca8` | Fix crash opening TextureGraph: initialize _ToolbarExtenderStyle in SImageViewport | 修复打开 TextureGraph 时的崩溃：初始化工具栏扩展样式指针 |
| 2026-03-21 | `3a2a91d3` | ImageWidgets: Move out of Experimental | 插件从 Experimental 目录迁移至 Editor 目录 |

### 维护评价

- **年龄**：约 7 个月（2026-03-21 创建），刚刚从 Experimental 迁出
- **更新频率**：创建后有 1 次紧急 bug 修复和 1 次代码维护更新，之后约 6 个月无更新
- **Beta 状态**：`IsBetaVersion=true`，API 可能发生变化
- **已知风险**：曾出现因初始化遗漏导致的崩溃（`fb33fca8`），表明该插件仍处于磨合期
- **推荐程度**：作为 Epic 官方提供的通用图像控件框架，适合内部编辑器工具集成使用。但由于 Beta 状态，**不建议用于对 API 稳定性要求高的外部项目**，需关注后续版本的 API 变更。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/ImageWidgets)
- [SImageCatalog 头文件](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Editor/ImageWidgets/Source/ImageWidgets/Public/SImageCatalog.h)
- [SImageViewport 头文件](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Editor/ImageWidgets/Source/ImageWidgets/Public/SImageViewport.h)
- [IImageViewer 接口](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Editor/ImageWidgets/Source/ImageWidgets/Public/IImageViewer.h)
- [ColorViewer 示例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/ImageWidgets/Source/ImageWidgets/Private/ColorViewerSample)