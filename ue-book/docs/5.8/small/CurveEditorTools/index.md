# Curve Editor Tools

> This provides a default set of editing tools for the Curve Editor.

| 属性 | 值 |
|---|---|
| 中文名 | 曲线编辑工具 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `CurveEditorTools` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2019-05-24 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/CurveEditorTools) | |

## 用途

Curve Editor Tools 是一个编辑器插件，为 UE 的曲线编辑器提供了一套**核心的、可扩展的交互式编辑工具集**。它解决了在 Sequencer、UMG 或曲线资产编辑器中手动调整关键帧时操作繁琐、效率低下的问题。

**为什么存在？**
该插件的诞生是为了将曲线编辑器的工具架构从单体式重构为**插件式**。通过此架构，第三方开发者可以轻松扩展或替换默认工具。插件内置了最常用的编辑工具（如平移、缩放、重定时、网格变形、滤波等），并提供了树形视图、多视图模式（绝对、堆叠、归一化）等管理功能，极大地增强了曲线编辑的生产力和灵活性。

## 使用场景

- **动画师调整动画曲线**：使用平移、缩放工具快速调整关键帧的位置和时间。
- **调整事件曲线的时间节奏**：使用重定时工具（Retime Tool）通过拖拽锚点来非线性地调整事件发生的时间。
- **批量编辑多条曲线**：使用多缩放工具（Multi Scale Tool）同时缩放多条曲线的关键帧。
- **平滑或锐化曲线**：使用内置的 FFT 滤波器（低通/高通）对曲线进行频率域处理。
- **精确的网格变形**：使用网格工具（Lattice Tool）创建一个二维网格，通过移动网格控制点来平滑地变形曲线形状。
- **在 Sequencer 或 UMG 中管理大量曲线**：使用树形视图（Tree View）来组织、搜索和固定（Pin）需要编辑的曲线。

## 蓝图用法

插件主要通过编辑器工具栏按钮和快捷键激活，不提供大量蓝图可调用节点。核心操作在曲线编辑器UI中完成。

### 核心工具激活节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ActivateTransformTool` | 激活变换工具（移动/缩放选中的关键帧） | `FCurveEditorToolCommands` |
| `ActivateRetimeTool` | 激活重定时工具（调整时间节奏） | `FCurveEditorToolCommands` |
| `ActivateMultiScaleTool` | 激活多缩放工具（独立缩放X/Y轴） | `FCurveEditorToolCommands` |
| `ActivateLatticeTool` | 激活网格工具（二维网格变形） | `FCurveEditorToolCommands` |

### 使用示例（蓝图描述）

在曲线编辑器中，可以通过以下方式使用工具：
1.  打开曲线编辑器（例如在 Sequencer 中）。
2.  在工具栏中找到新出现的工具图标（移动、重定时、多缩放、网格）。
3.  点击图标激活对应工具。
4.  在曲线视图区：
    *   **变换工具**：框选关键帧，拖拽移动，或拖拽边角缩放。按住 Ctrl 可进行软选择（Falloff）。
    *   **重定时工具**：在时间轴上点击添加锚点，拖动锚点来压缩或拉伸其影响范围内的关键帧。
    *   **网格工具**：选中一组关键帧后激活，会出现一个四边形网格。拖动网格点或边来变形选中的关键帧。
5.  在工具栏或细节面板中，可以调整活动工具的选项（如缩放中心、软选择衰减类型等）。

## C++ 用法

插件通过 `ICurveEditorToolExtension` 接口注册工具。要扩展曲线编辑器，可以实现该接口或使用其子类。

### 头文件引入

```cpp
#include "ICurveEditorToolExtension.h"
#include "CurveEditorToolCommands.h"
```

### 基本用法：注册自定义工具

（来源：插件自身工具注册逻辑 `FCurveEditorToolsModule::StartupModule`）

```cpp
// 获取曲线编辑器工具管理器
TSharedPtr<FExtensibilityManager> ToolManager = FCurveEditorModule::Get().GetToolsExtensibilityManager();

// 创建并注册一个自定义工具
TSharedPtr<ICurveEditorToolExtension> MyCustomTool = MakeShared<FMyCurveEditorTool>(CurveEditor);
ToolManager->AddTool(MyCustomTool);
```

### 进阶用法：实现工具接口

（来源：`FCurveEditorTransformTool` 类定义）

一个完整的工具需要实现 `ICurveEditorToolExtension` 接口，处理绘制、鼠标输入和工具选项。

```cpp
// MyCurveEditorTool.h
#pragma once
#include "ICurveEditorToolExtension.h"

class FMyCurveEditorTool : public ICurveEditorToolExtension
{
public:
    explicit FMyCurveEditorTool(TWeakPtr<FCurveEditor> InCurveEditor);
    
    // ICurveEditorToolExtension 接口
    virtual void OnPaint(const FPaintArgs& Args, const FGeometry& AllottedGeometry, 
                         const FSlateRect& MyCullingRect, FSlateWindowElementList& OutDrawElements, 
                         int32 PaintOnLayerId, const FWidgetStyle& InWidgetStyle, bool bParentEnabled) const override;
    virtual FReply OnMouseButtonDown(TSharedRef<SWidget> OwningWidget, const FGeometry& MyGeometry, 
                                     const FPointerEvent& MouseEvent) override;
    virtual void OnToolActivated() override;
    virtual void OnToolDeactivated() override;
    virtual TSharedPtr<FStructOnScope> GetToolOptions() const override;

private:
    TWeakPtr<FCurveEditor> WeakCurveEditor;
    // 工具状态...
};
```

```cpp
// MyCurveEditorTool.cpp
#include "MyCurveEditorTool.h"

FMyCurveEditorTool::FMyCurveEditorTool(TWeakPtr<FCurveEditor> InCurveEditor)
    : WeakCurveEditor(InCurveEditor)
{
}

void FMyCurveEditorTool::OnPaint(const FPaintArgs& Args, const FGeometry& AllottedGeometry,
                                 const FSlateRect& MyCullingRect, FSlateWindowElementList& OutDrawElements,
                                 int32 PaintOnLayerId, const FWidgetStyle& InWidgetStyle, bool bParentEnabled) const
{
    // 在这里绘制自定义工具的视觉元素
    // 例如：绘制选择框、控制手柄等
}

FReply FMyCurveEditorTool::OnMouseButtonDown(TSharedRef<SWidget> OwningWidget, const FGeometry& MyGeometry,
                                             const FPointerEvent& MouseEvent)
{
    if (MouseEvent.GetEffectingButton() == EKeys::LeftMouseButton)
    {
        // 处理鼠标点击，开始操作
        return FReply::Handled();
    }
    return FReply::Unhandled();
}

void FMyCurveEditorTool::OnToolActivated()
{
    // 工具激活时初始化状态
    if (TSharedPtr<FCurveEditor> CurveEditor = WeakCurveEditor.Pin())
    {
        // 可以访问和操作曲线编辑器
        CurveEditor->GetSelection();
    }
}

void FMyCurveEditorTool::OnToolDeactivated()
{
    // 清理工作
}

TSharedPtr<FStructOnScope> FMyCurveEditorTool::GetToolOptions() const
{
    // 返回用于在细节面板中显示选项的 UStruct
    struct FMyToolOptions
    {
        UPROPERTY(EditAnywhere)
        float MyFloatValue = 1.0f;
    };
    
    static UScriptStruct* OptionsStruct = FMyToolOptions::StaticStruct();
    TSharedPtr<FStructOnScope> Options = MakeShared<FStructOnScope>(OptionsStruct);
    // 填充默认值...
    return Options;
}
```

## 模块依赖

插件依赖于 `TweeningUtils` 插件。

| 模块 | 用途 |
|---|---|
| `TweeningUtils` | 提供关键帧混合（Tweening）功能，用于缓动工具。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `51e61d5d` | Curve Editor: Lattice tool now mirrors user tangents on x-axis | 网格工具支持沿X轴镜像用户切线 |
| 2026-03-30 | `17e19999` | Tweening Utils: Add hotkeys to change slider position. By default: | 为缓动工具添加改变滑块位置的快捷键 |
| 2026-03-27 | `f6f50393` | Anim In Engine: Hotkeys for 1) Zoom To/Frame Selection Range Command in Sequencer and Curve Editor, | 在 Sequencer 和曲线编辑器中添加缩放至/框选选择范围的快捷键 |
| 2026-03-23 | `979bfe32` | Curve Editor: Fix non-unity compile issue. | 修复非统一编译时的编译错误 |
| 2026-03-23 | `c3b4873e` | Curve Editor: Fix lattice tool flipping bool values on bool curves, like IK switches, when only movi | 修复网格工具在仅移动关键帧时错误地翻转布尔曲线（如IK开关）值的问题 |

### 维护评价

该插件处于**活跃维护**状态。
1.  **年龄**：插件创建于 2019 年，已有 7 年历史，属于成熟的核心编辑器工具。
2.  **近期更新**：最近 3 个月内有 5 次提交，内容包括新功能开发（网格工具镜像切线、快捷键增强）和关键 Bug 修复（布尔曲线翻转、编译问题），表明 Epic 持续投入维护。
3.  **状态**：作为 UnrealEd 和 Sequencer 工作流的核心组成部分，插件被深度集成并依赖，不太可能被废弃。
4.  **已知限制**：无。
5.  **推荐使用**：**强烈推荐**。这是进行任何曲线编辑工作的基础，所有使用曲线编辑器（动画、音频、事件等）的用户都会直接或间接受益于这些工具。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/CurveEditorTools)
- [官方文档]()（无专用文档，功能集成于[曲线编辑器文档](https://docs.unrealengine.com/5.8/en-US/curve-editor-in-unreal-engine/)）