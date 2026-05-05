# MetaHuman Core Tech

> The core technology behind the MetaHuman Creator and MetaHuman Animator plugins.

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（核心库、蓝图资产） |
| 模块 | `MetaHumanCaptureData` (Runtime), `MetaHumanCoreTech` (Runtime), `MetaHumanCoreTechLib` (Runtime), `MetaHumanImageViewer` (Runtime), `MetaHumanPipelineCore` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-01-20 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanCoreTechLib) | |

## 用途

MetaHuman Core Tech 是 MetaHuman Creator 和 MetaHuman Animator 插件的底层技术基石。它并非一个面向最终用户的独立功能插件，而是一个提供核心算法、数据结构和处理流程的**技术库**。其主要目的是为上层应用（如创建数字人、驱动面部动画）提供统一的、高性能的底层支持，解决数字人创建与动画流程中的复杂技术问题，例如面部网格处理、图像分析、数据管道编排等。

## 使用场景

- **开发 MetaHuman 相关工具**：当你需要开发自定义的 MetaHuman 创建或编辑工具时，可以调用此插件提供的核心算法。
- **处理面部捕捉数据**：在构建自定义的面部动画捕捉或驱动流程时，可以使用 `MetaHumanCaptureData` 和 `MetaHumanPipelineCore` 模块来处理原始数据。
- **集成图像查看与处理**：在编辑器工具中需要显示和交互式地查看图像（如面部扫描图、深度图）时，可以使用 `MetaHumanImageViewer` 模块提供的 Slate 控件。

## 蓝图用法

基于当前提供的模块信息（`MetaHumanImageViewer`），该插件主要提供底层的 C++ API 和 Slate 控件，而非直接暴露给蓝图的节点。其核心功能更多是作为其他 MetaHuman 插件（如 MetaHuman Creator）的依赖库被调用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| （无直接蓝图节点） | 该模块主要提供 Slate 控件和底层 C++ 类，未发现直接暴露的 `BlueprintCallable` 函数。 | - |

### 使用示例（蓝图描述）

由于该插件主要作为技术库，其功能通常通过其他 MetaHuman 插件间接使用，或在 C++ 层面调用。在蓝图中直接使用此插件的场景较少。

## C++ 用法

### 头文件引入

```cpp
#include "SMetaHumanImageViewer.h"
```

### 基本用法

`SMetaHumanImageViewer` 是一个继承自 `SImage` 的 Slate 控件，用于显示图像并支持交互式平移和缩放。

```cpp
// 创建一个 SMetaHumanImageViewer 控件
TSharedRef<SMetaHumanImageViewer> ImageViewer = SNew(SMetaHumanImageViewer)
    .Image(MySlateBrush) // 设置要显示的图像资源
    .CommandList(MyCommandList); // 可选：绑定命令列表

// 监听视图变化（例如平移/缩放后）
ImageViewer->OnViewChanged.AddLambda([](const FBox2f& NewView) {
    UE_LOG(LogTemp, Log, TEXT("View changed to: %s"), *NewView.ToString());
});

// 重置视图
ImageViewer->ResetView();
```

### 进阶用法

可以重写 `SMetaHumanImageViewer` 的方法来自定义行为，例如处理特定的鼠标事件或绘制逻辑。

```cpp
class SMyCustomImageViewer : public SMetaHumanImageViewer
{
public:
    // 重写鼠标按下事件，添加自定义逻辑
    virtual FReply OnMouseButtonDown(const FGeometry& InGeometry, const FPointerEvent& InMouseEvent) override
    {
        if (InMouseEvent.GetEffectingButton() == EKeys::MiddleMouseButton)
        {
            // 自定义中键点击行为
            return FReply::Handled();
        }
        // 否则，调用父类默认处理
        return SMetaHumanImageViewer::OnMouseButtonDown(InGeometry, InMouseEvent);
    }

    // 重写绘制逻辑
    virtual int32 OnPaint(const FPaintArgs& InArgs, const FGeometry& InAllottedGeometry,
        const FSlateRect& InWidgetClippingRect, FSlateWindowElementList& OutDrawElements,
        int32 InLayerId, const FWidgetStyle& InWidgetStyle, bool InParentEnabled) const override
    {
        // 先调用父类绘制图像
        int32 NewLayerId = SMetaHumanImageViewer::OnPaint(InArgs, InAllottedGeometry, InWidgetClippingRect, OutDrawElements, InLayerId, InWidgetStyle, InParentEnabled);
        
        // 在图像上绘制自定义覆盖层（例如一个十字准星）
        // ... 绘制代码 ...
        
        return NewLayerId;
    }
};
```

## Demo 示例

一个最小的示例，展示如何在编辑器工具窗口中使用 `SMetaHumanImageViewer`。

**MyImageViewerTool.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Widgets/SCompoundWidget.h"

class SMyImageViewerTool : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SMyImageViewerTool) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs);

private:
    TSharedPtr<class SMetaHumanImageViewer> ImageViewer;
    TSharedPtr<FSlateBrush> ImageBrush;
};
```

**MyImageViewerTool.cpp**
```cpp
#include "MyImageViewerTool.h"
#include "SMetaHumanImageViewer.h"
#include "Styling/SlateBrush.h"

void SMyImageViewerTool::Construct(const FArguments& InArgs)
{
    // 创建一个用于测试的纯色图像画刷
    ImageBrush = MakeShareable(new FSlateBrush());
    ImageBrush->TintColor = FLinearColor(0.2f, 0.5f, 0.8f, 1.0f); // 蓝色

    ChildSlot
    [
        SNew(SVerticalBox)
        + SVerticalBox::Slot()
        .FillHeight(1.0f)
        [
            SAssignNew(ImageViewer, SMetaHumanImageViewer)
            .Image(ImageBrush.Get())
        ]
        + SVerticalBox::Slot()
        .AutoHeight()
        .Padding(5.0f)
        [
            SNew(SButton)
            .Text(FText::FromString(TEXT("Reset View")))
            .OnClicked_Lambda([this]() -> FReply {
                if (ImageViewer.IsValid())
                {
                    ImageViewer->ResetView();
                }
                return FReply::Handled();
            })
        ]
    ];
}
```

## 模块依赖

该插件的模块之间存在内部依赖，对于外部使用者，主要依赖 `MetaHumanCoreTechLib` 模块。

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | 核心技术库的主模块，提供基础类型和功能。 |
| `MetaHumanImageViewer` | 提供用于查看图像的 Slate 控件。 |
| `OpenCV` | 用于图像处理和计算机视觉算法（被 `MetaHumanPipelineCore` 依赖）。 |
| `OpenCVHelper` | OpenCV 的 UE 封装辅助模块。 |
| `DirectoryWatcher` | 用于监控文件系统目录变化（被 `MetaHumanCaptureData` 依赖）。 |

## 维护状态

### 近期更新

```
- 2025-01-20 52e3dac151e1 Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types. Part 3/n
- 2025-01-20 0d6a5f406236 [UEMHC] move a couple of files which are dragging MetaHumanCoreTechLib into runtime build #rb aleksandr.cicenkov, jon.cook
- 2025-01-20 29ddcc3ce7f4 [MH-Plugin] Move Core Tech plugin to be inside the MetaHuman folder #rb Jane.Haslam
```

### 维护评价

- **创建时间**：非常新（2025年1月）。
- **更新频率**：在创建初期有密集的提交，主要用于代码整理、模块结构优化和构建修复。
- **活跃度**：作为 MetaHuman 技术栈的核心，预计会持续维护和更新，以支持 MetaHuman Creator 和 Animator 的新功能。
- **已知限制**：这是一个底层技术库，`EnabledByDefault=false`，通常由其他 MetaHuman 插件自动启用，不建议单独启用。
- **推荐使用**：**仅推荐给需要深度定制或扩展 MetaHuman 功能的开发者**。普通用户应使用上层的 MetaHuman Creator 或 Animator 插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanCoreTechLib)
- [官方文档]() （暂无）
- [测试用例]() （暂未在提供的路径中发现）