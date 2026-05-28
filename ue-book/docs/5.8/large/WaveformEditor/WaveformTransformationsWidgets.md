# Waveform Editor

> Editor tool for waveforms（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 波形编辑器 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器工具） |
| 模块 | `WaveformEditor` (Editor), `WaveformEditorWidgets` (Runtime), `WaveformTransformations` (Runtime), `WaveformTransformationsWidgets` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-08-18 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/WaveformEditor) | |

## 用途

WaveformEditor 是一个用于在 UE5 编辑器中可视化编辑音频波形数据的工具集。它解决的核心问题是为音频设计师提供直观的界面，以便在波形级别对音频资产进行精确操作和变换，而无需离开引擎环境。其主要功能包括：

1.  **波形可视化与交互**：提供专业的波形显示，并支持通过鼠标交互（如拖拽、缩放、选择）进行编辑。
2.  **非破坏性变换**：支持对音频波形应用各种变换（如淡入淡出、修剪、标记），这些变换以元数据形式存储，不直接修改原始音频数据。
3.  **自定义渲染与交互框架**：提供了基础框架和接口，允许开发者为特定的波形变换（Transformation）创建自定义的编辑器渲染器和交互逻辑。

插件的存在使得 UE5 的音频工作流更加完整，将高级的音频编辑能力直接集成到编辑器中，提升了游戏音频制作的效率和灵活性。

## 使用场景

-   你是一名音频设计师，需要为游戏中的环境音效（如风声、水流）调整淡入淡出的曲线和时长 → 使用内置的淡入淡出（Fade）变换和渲染器。
-   你需要精确地标记音频文件中的关键点（如音乐循环点、语音同步点） → 使用标记（Markers）变换和渲染器来放置和拖拽标记。
-   你需要在引擎内快速修剪音频剪辑的开头和结尾 → 使用修剪淡变（TrimFade）变换。
-   你正在开发一个自定义的音频处理效果（如动态范围压缩），并希望为其创建配套的编辑器UI以便于调整参数 → 基于 `IWaveformTransformationRenderer` 接口和 `FWaveformTransformationRendererBase` 类创建自定义渲染器。

## 蓝图用法

由于这是一个编辑器工具，其核心功能是通过编辑器UI（Slate控件）交互实现的，而非暴露给蓝图运行时。因此，该插件**没有提供公开的蓝图节点**。

## C++ 用法

本插件的 C++ 用法主要集中在**创建自定义的波形变换渲染器**上。下面介绍核心概念和用法。

### 头文件引入

使用波形变换渲染器框架，通常需要引入以下头文件：

```cpp
#include "WaveformTransformationRendererBase.h" // 自定义渲染器基类
#include "IWaveformTransformationRenderer.h"   // 渲染器接口
```

### 基本用法：理解渲染器接口

所有自定义渲染器都需要实现 `IWaveformTransformationRenderer` 接口。`FWaveformTransformationRendererBase` 是它的一个便捷基类，提供了许多常用交互事件的默认实现。

**渲染器核心职责**：
- `OnPaint`：在波形控件上绘制自定义的UI元素（如标记点、淡变曲线）。
- `Tick`：用于动画或每帧更新。
- `OnMouse*`：处理各种鼠标交互，以实现拖拽、选择等操作。
- `SetWaveformTransformation`：绑定到具体的 `UWaveformTransformationBase` 数据对象。
- `SetTransformationWaveInfo`：获取波形的基本信息（采样率、通道数等）。

### 进阶用法：注册自定义渲染器

插件通过 `FWaveformTransformationRendererMapper` 单例来管理不同变换类型与渲染器的映射。要让编辑器识别你的自定义渲染器，需要在你的模块启动时进行注册。

```cpp
// 在你的模块 StartupModule 中注册
#include "WaveformTransformationRendererMapper.h"
#include "MyCustomTransformation.h" // 你的UWaveformTransformationBase子类
#include "MyCustomTransformationRenderer.h" // 你的渲染器

void FMyModule::StartupModule()
{
    // 将渲染器与变换类关联
    FWaveformTransformationRendererMapper::Get().RegisterRenderer<FMyCustomTransformationRenderer>(UMyCustomTransformation::StaticClass());
}
```

**渲染器映射器 (`FWaveformTransformationRendererMapper`) 工作原理**：
- 它是一个单例，存储了从 `UClass`（变换类）到渲染器创建函数（`TFunction<TSharedPtr<IWaveformTransformationRenderer>()>`）的映射。
- 当波形编辑器需要为某个特定变换显示UI时，会查询此映射器，获取对应的渲染器实例。

## Demo 示例

下面是一个自定义波形变换渲染器的最小实现示例。它会在波形上绘制一条简单的彩色区域，并允许通过鼠标拖拽来调整区域大小。

**MyTransformationRenderer.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "WaveformTransformationRendererBase.h"

// 假设这是你的变换数据类
class UMyTransformation;

class FMyTransformationRenderer : public FWaveformTransformationRendererBase
{
public:
    FMyTransformationRenderer();

    // 重写核心绘制函数
    virtual int32 OnPaint(const FPaintArgs& Args, const FGeometry& AllottedGeometry, const FSlateRect& MyCullingRect, FSlateWindowElementList& OutDrawElements, int32 LayerId, const FWidgetStyle& InWidgetStyle, bool bParentEnabled) const override;

    // 重写交互函数
    virtual FReply OnMouseButtonDown(SWidget& OwnerWidget, const FGeometry& MyGeometry, const FPointerEvent& MouseEvent) override;
    virtual FReply OnMouseButtonUp(SWidget& OwnerWidget, const FGeometry& MyGeometry, const FPointerEvent& MouseEvent) override;
    virtual FReply OnMouseMove(SWidget& OwnerWidget, const FGeometry& MyGeometry, const FPointerEvent& MouseEvent) override;
    virtual FCursorReply OnCursorQuery(const FGeometry& MyGeometry, const FPointerEvent& CursorEvent) const override;

    // 重写数据绑定函数
    virtual void SetWaveformTransformation(TObjectPtr<UWaveformTransformationBase> InTransformation) override;

private:
    // 持有对具体变换数据对象的强引用
    TStrongObjectPtr<UMyTransformation> StrongTransformation;

    // 交互状态
    bool bIsDragging = false;
    FVector2D DragStartMousePos;
    float DragStartRegionEnd = 0.f;

    // 视觉参数
    FLinearColor RegionColor = FLinearColor(0.2f, 0.8f, 0.2f, 0.5f);
};
```

**MyTransformationRenderer.cpp**
```cpp
#include "MyTransformationRenderer.h"
#include "MyTransformation.h" // 你的变换类

FMyTransformationRenderer::FMyTransformationRenderer()
{
}

int32 FMyTransformationRenderer::OnPaint(const FPaintArgs& Args, const FGeometry& AllottedGeometry, const FSlateRect& MyCullingRect, FSlateWindowElementList& OutDrawElements, int32 LayerId, const FWidgetStyle& InWidgetStyle, bool bParentEnabled) const
{
    // 首先，调用基类绘制（如果有需要）
    LayerId = FWaveformTransformationRendererBase::OnPaint(Args, AllottedGeometry, MyCullingRect, OutDrawElements, LayerId, InWidgetStyle, bParentEnabled);

    if (StrongTransformation.IsValid())
    {
        // 计算波形区域对应的屏幕像素
        const float PixelsPerFrame = AllottedGeometry.GetLocalSize().X / TransformationWaveInfo.NumSamplesAvailable;
        const float RegionStartX = 0.0f; // 示例：从头开始
        const float RegionEndX = StrongTransformation->RegionEndFrame * PixelsPerFrame; // 使用变换中的数据

        // 绘制一个半透明的矩形区域
        FSlateDrawElement::MakeBox(
            OutDrawElements,
            LayerId,
            AllottedGeometry.ToPaintGeometry(FVector2D(RegionStartX, 0.0f), FVector2D(RegionEndX - RegionStartX, AllottedGeometry.GetLocalSize().Y)),
            FCoreStyle::Get().GetDefaultBrush(),
            ESlateDrawEffect::None,
            RegionColor
        );
    }
    return LayerId;
}

FReply FMyTransformationRenderer::OnMouseButtonDown(SWidget& OwnerWidget, const FGeometry& MyGeometry, const FPointerEvent& MouseEvent)
{
    if (MouseEvent.GetEffectingButton() == EKeys::LeftMouseButton)
    {
        // 检查鼠标是否在区域的右边缘附近（实现拖拽边缘）
        const FVector2D LocalCursorPos = MyGeometry.AbsoluteToLocal(MouseEvent.GetScreenSpacePosition());
        const float PixelsPerFrame = MyGeometry.GetLocalSize().X / TransformationWaveInfo.NumSamplesAvailable;
        const float RegionEndScreenX = StrongTransformation.IsValid() ? StrongTransformation->RegionEndFrame * PixelsPerFrame : 0.f;

        if (FMath::Abs(LocalCursorPos.X - RegionEndScreenX) < 10.f) // 10像素容差
        {
            bIsDragging = true;
            DragStartMousePos = LocalCursorPos;
            DragStartRegionEnd = StrongTransformation.IsValid() ? StrongTransformation->RegionEndFrame : 0.f;
            // 开始一个撤销/重做事务
            BeginTransaction(TEXT("AdjustMyRegion"), FText::FromString(TEXT("Adjust Region End")));
            return FReply::Handled().CaptureMouse(SharedThis(this));
        }
    }
    // 调用基类处理其他情况（如右键菜单）
    return FWaveformTransformationRendererBase::OnMouseButtonDown(OwnerWidget, MyGeometry, MouseEvent);
}

FReply FMyTransformationRenderer::OnMouseButtonUp(SWidget& OwnerWidget, const FGeometry& MyGeometry, const FPointerEvent& MouseEvent)
{
    if (bIsDragging)
    {
        bIsDragging = false;
        EndTransaction(); // 结束撤销事务
        return FReply::Handled().ReleaseMouseCapture();
    }
    return FWaveformTransformationRendererBase::OnMouseButtonUp(OwnerWidget, MyGeometry, MouseEvent);
}

FReply FMyTransformationRenderer::OnMouseMove(SWidget& OwnerWidget, const FGeometry& MyGeometry, const FPointerEvent& MouseEvent)
{
    if (bIsDragging)
    {
        const FVector2D LocalCursorPos = MyGeometry.AbsoluteToLocal(MouseEvent.GetScreenSpacePosition());
        const float PixelsPerFrame = MyGeometry.GetLocalSize().X / TransformationWaveInfo.NumSamplesAvailable;
        const float DeltaX = LocalCursorPos.X - DragStartMousePos.X;
        const float DeltaFrames = DeltaX / PixelsPerFrame;

        // 更新变换数据
        if (StrongTransformation.IsValid())
        {
            StrongTransformation->RegionEndFrame = FMath::Clamp(
                DragStartRegionEnd + DeltaFrames,
                0.0f,
                (float)TransformationWaveInfo.NumSamplesAvailable
            );
        }
        return FReply::Handled();
    }
    return FWaveformTransformationRendererBase::OnMouseMove(OwnerWidget, MyGeometry, MouseEvent);
}

FCursorReply FMyTransformationRenderer::OnCursorQuery(const FGeometry& MyGeometry, const FPointerEvent& CursorEvent) const
{
    // 当拖拽边缘或悬停在边缘附近时，显示调整大小的光标
    if (bIsDragging)
    {
        return FCursorReply::Cursor(EMouseCursor::ResizeLeftRight);
    }
    const FVector2D LocalCursorPos = MyGeometry.AbsoluteToLocal(CursorEvent.GetScreenSpacePosition());
    const float PixelsPerFrame = MyGeometry.GetLocalSize().X / TransformationWaveInfo.NumSamplesAvailable;
    const float RegionEndScreenX = StrongTransformation.IsValid() ? StrongTransformation->RegionEndFrame * PixelsPerFrame : 0.f;
    if (FMath::Abs(LocalCursorPos.X - RegionEndScreenX) < 10.f)
    {
        return FCursorReply::Cursor(EMouseCursor::ResizeLeftRight);
    }
    return FCursorReply::Cursor(EMouseCursor::Default);
}

void FMyTransformationRenderer::SetWaveformTransformation(TObjectPtr<UWaveformTransformationBase> InTransformation)
{
    // 将基类指针转换为你的具体类型
    StrongTransformation.Reset();
    if (UMyTransformation* MyTransformation = Cast<UMyTransformation>(InTransformation))
    {
        StrongTransformation = MakeStrongObjectPtr(MyTransformation);
    }
}
```

## 模块依赖

从模块名称推断，要使用此插件，你的模块可能需要依赖以下模块（除了常见的 Core, Engine, Slate 等）：

| 模块 | 用途 |
|---|---|
| `WaveformEditor` | 插件的主编辑器模块，提供波形编辑器的核心功能。 |
| `WaveformEditorWidgets` | 提供波形编辑器使用的 Slate 控件（如波形显示、时间轴）。 |
| `WaveformTransformations` | 定义了各种波形变换（Transformation）的 Uobject 类和数据结构。 |
| `WaveformTransformationsWidgets` | 提供了渲染器基础类和映射器，是创建自定义渲染器的核心依赖。 |

**特别注意**：由于 `WaveformEditor` 模块类型为 `Editor`，任何依赖它的模块在非编辑器构建（如打包后）中必须小心处理。通常，与波形编辑交互的代码应限于编辑器模块（`UncookedOnly` 或 `Editor` 类型）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `40a5c76a` | [Waveform] Performance regression when dragging trimfade extents | 修复了拖拽修剪淡变边缘时的性能回退问题。 |
| 2026-05-14 | `1f67ea84` | [Waveform editor] Remove no-op trimfade transform option | 移除了无效的修剪淡变变换选项，简化了UI。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下双精度常量截断为浮点数引发的编译警告。 |
| 2026-04-28 | `d67c3aa3` | [Waveform editor] - Shift + space returns playhead to start, but playback does not start at beginning | 修复了Shift+空格将播放头返回开头但播放不从头开始的问题。 |
| 2026-04-17 | `93be7d91` | [Waveform] Performance regression when dragging trimfade extents | 另一次关于拖拽修剪淡变边缘性能问题的修复。 |

### 维护评价

-   **活跃维护**：插件创建于 2022 年，属于较新的工具。从 git 历史看，截至 2026 年 5 月仍有频繁的更新，主要集中在**性能优化**和**bug 修复**（如交互、播放问题）。这表明它仍处于**积极维护和打磨**阶段。
-   **实验性状态**：`.uplugin` 标记 `IsBetaVersion: true`，且默认未启用 (`EnabledByDefault: false`)。这明确提示用户该插件功能可能还不完全稳定，API 可能在未来版本中发生变化。
-   **推荐使用**：对于需要在编辑器中进行高级波形编辑的音频工作流，此插件是官方提供的**唯一选择**，且功能在持续完善中。**推荐在了解其实验性状态的前提下使用**。对于生产关键路径，建议密切关注引擎更新日志，并做好应对潜在API变更的准备。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/WaveformEditor)
-   [官方文档]()

*注：根据提供的元数据，该插件没有官方文档链接 (`DocsURL` 为空)。*