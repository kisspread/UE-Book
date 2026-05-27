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
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/CurveEditorTools) | |

## 用途

本插件并非简单地为曲线编辑器提供额外工具，而是**彻底重构了 UE 的曲线编辑器**，为其建立了一个基于插件的、可扩展的架构。它解决了在 Sequencer 或 UMG 等场景中编辑复杂动画曲线时，功能单一、操作低效的问题。其核心价值在于：

1.  **模块化与可扩展性**：允许开发者通过插件添加新的编辑工具、视图和滤镜。
2.  **高效的批量编辑**：提供了变换工具（Transform Tool）和重定时工具（Retime Tool），允许用户框选关键帧并进行平移、缩放，或使用一维晶格来调整关键帧时间，支持非线性衰减。
3.  **强大的数据可视化**：支持绝对视图、堆叠视图和归一化视图，方便处理范围差异大的曲线数据。
4.  **便捷的管理工具**：引入了树形视图来管理大量曲线，并支持曲线固定、聚焦播放时间/范围、以及基于时间范围的选择等扩展功能。
5.  **内置高级滤镜**：通过 FFT 滤镜（支持 Butterworth 和 Chebyshev 响应）提供低通/高通平滑功能。
6.  **无缝集成**：其工具、视图和滤镜同样适用于独立的曲线资产编辑器（浮点、向量、颜色曲线）。

## 使用场景

*   你在 Sequencer 中为一个角色制作了复杂的骨骼动画，需要批量移动或缩放一组关键帧的时间位置 → 使用 **变换工具 (Transform Tool)**。
*   你需要调整一段动画的节奏，或实现更自然的动画混合效果 → 使用 **重定时工具 (Retime Tool)** 的晶格变形功能。
*   你的曲线数据范围差异巨大（例如，一条曲线在0-1，另一条在0-1000），直接查看重叠在一起很难分析 → 切换到 **归一化视图 (Normalized View)** 或 **堆叠视图 (Stacked View)**。
*   你需要对动画曲线进行平滑处理以消除抖动 → 应用 **FFT 滤镜** 的低通功能。
*   在编辑大量曲线（如物理动画数据）时，需要快速找到并固定关键曲线 → 使用 **树形视图 (Tree View)**。

## 蓝图用法

本插件的核心工具类是 C++ 编写的编辑器扩展，其工具选项（如变换工具、多缩放工具的选项）通过 `USTRUCT` 暴露为蓝图可编辑的属性。滤镜类（如 `UCurveEditorFFTFilter`）是蓝图类型，可在滤镜选择器中找到并配置。

### 核心节点/属性

| 工具/滤镜 | 可配置属性 | 所在类/结构体 |
|---|---|---|
| **变换工具** | `FalloffInterpType` (衰减插值类型), `ScaleCenterX/Y` (缩放中心), `LeftBound/RightBound` (边界) | `FTransformToolOptions` |
| **多缩放工具** | `XScale/YScale` (缩放值), `PivotType` (枢轴类型：平均、边界中心、首/末关键帧) | `FMultiScaleToolOptions` |
| **FFT 滤镜** | `CutoffFrequency` (截止频率), `Type` (低通/高通), `Response` (Butterworth/Chebyshev), `Order` (阶数) | `UCurveEditorFFTFilter` |

### 使用示例（蓝图描述）

在 Sequencer 或 UMG 的曲线编辑器中，工具栏上会自动出现“Transform”、“Retime”、“Multi Scale”和“Lattice”等工具按钮。点击激活对应工具后，可以在编辑器的详细信息面板或工具栏下拉菜单中修改上述属性值（如调整缩放比例、选择衰减类型等）。对于滤镜，通常在工具栏或菜单中找到“Filter”选项，选择“Fourier Transform (FFT)”即可看到并调整其属性。

## C++ 用法

本插件的核心是其可扩展的架构。开发者可以基于 `ICurveEditorToolExtension` 接口创建自定义的曲线编辑工具。

### 头文件引入

```cpp
#include "CurveEditorToolsModule.h"
#include "ICurveEditorToolExtension.h"
#include "CurveEditor.h"
```

### 基本用法：创建一个自定义的曲线编辑工具

1.  **创建工具类**：继承 `ICurveEditorToolExtension` 接口。
2.  **实现必要方法**：如 `OnPaint`、`OnMouseButtonDown` 等，以处理绘制和用户输入。
3.  **注册工具**：在模块启动时，通过 `FCurveEditorToolsModule` 注册你的工具。

```cpp
// MyCurveEditorTool.h
#pragma once

#include "ICurveEditorToolExtension.h"

class FMyCurveEditorTool : public ICurveEditorToolExtension
{
public:
    explicit FMyCurveEditorTool(TWeakPtr<FCurveEditor> InCurveEditor);

    // ICurveEditorToolExtension Interface
    virtual void OnPaint(const FPaintArgs& Args, const FGeometry& AllottedGeometry, ...) const override;
    virtual FReply OnMouseButtonDown(TSharedRef<SWidget> OwningWidget, const FGeometry& MyGeometry, const FPointerEvent& MouseEvent) override;
    virtual FText GetLabel() const override;
    virtual FSlateIcon GetIcon() const override;
    // ... 其他重写方法

private:
    TWeakPtr<FCurveEditor> WeakCurveEditor;
    // ... 工具内部数据
};
```

```cpp
// MyCurveEditorTool.cpp
#include "MyCurveEditorTool.h"

FMyCurveEditorTool::FMyCurveEditorTool(TWeakPtr<FCurveEditor> InCurveEditor)
    : WeakCurveEditor(InCurveEditor)
{
}

void FMyCurveEditorTool::OnPaint(const FPaintArgs& Args, const FGeometry& AllottedGeometry, ...) const
{
    // 在这里绘制你的自定义工具界面（例如，选中框、控制柄等）
    if (TSharedPtr<FCurveEditor> CurveEditor = WeakCurveEditor.Pin())
    {
        // ... 使用 CurveEditor 获取选中的关键帧等信息
    }
}

FReply FMyCurveEditorTool::OnMouseButtonDown(TSharedRef<SWidget> OwningWidget, const FGeometry& MyGeometry, const FPointerEvent& MouseEvent)
{
    // 处理鼠标点击，实现你的工具逻辑
    return FReply::Handled();
}

FText FMyCurveEditorTool::GetLabel() const
{
    return NSLOCTEXT("MyTools", "MyCurveTool", "My Tool");
}

FSlateIcon FMyCurveEditorTool::GetIcon() const
{
    return FSlateIcon(FAppStyle::GetAppStyleSetName(), "Icons.Plus");
}

// 在模块启动时注册工具
void FMyCurveEditorToolsModule::StartupModule()
{
    // ... 其他初始化代码
    if (CurveEditorToolsModule)
    {
        CurveEditorToolsModule->RegisterToolExtensionFactory<FMyCurveEditorTool>();
    }
}
```

### 进阶用法：使用晶格变形器 (Lattice Deformer)

晶格工具（`FCurveEditorLatticeTool`）是复杂工具的一个典范，它展示了如何与曲线编辑器数据、绘制系统和撤销系统深度集成。开发者可以参考其源码实现自己的高级变形工具。

*   **核心类**：`FLatticeDeformer2D` 实现了二维晶格变形的数学逻辑。
*   **状态管理**：`FLatticeDeformerState` 持有晶格状态、每条曲线的变换矩阵以及视图监听器。
*   **交互处理**：通过 `FLatticeDragOp` 及其子类（如 `FLatticeDragOp_MoveControlPoints`）处理拖拽控制点、边或单元格的交互。
*   **镜像操作**：`FLatticeEdgeTangentsMirrorOp` 和 `FLatticePointTangentsMirrorOp` 实现了拖拽边或点时的切线镜像功能。

## Demo 示例

以下是一个极简的“框选计数”工具示例，它会在工具激活时显示选中关键帧的数量。

```cpp
// SelectionCounterTool.h
#pragma once

#include "ICurveEditorToolExtension.h"

class FSelectionCounterTool : public ICurveEditorToolExtension
{
public:
    explicit FSelectionCounterTool(TWeakPtr<FCurveEditor> InCurveEditor);

    //~ ICurveEditorToolExtension Interface
    virtual void OnPaint(const FPaintArgs& Args, const FGeometry& AllottedGeometry, const FSlateRect& MyCullingRect, FSlateWindowElementList& OutDrawElements, int32 PaintOnLayerId, const FWidgetStyle& InWidgetStyle, bool bParentEnabled) const override;
    virtual FText GetLabel() const override { return NSLOCTEXT("CounterTool", "Label", "Selection Counter"); }
    virtual FSlateIcon GetIcon() const override;
    //~

private:
    TWeakPtr<FCurveEditor> WeakCurveEditor;
};

// SelectionCounterTool.cpp
#include "SelectionCounterTool.h"
#include "CurveEditor.h"

FSelectionCounterTool::FSelectionCounterTool(TWeakPtr<FCurveEditor> InCurveEditor)
    : WeakCurveEditor(InCurveEditor)
{
}

FSlateIcon FSelectionCounterTool::GetIcon() const
{
    return FSlateIcon(FAppStyle::GetAppStyleSetName(), "GenericCurveEditor.Filter");
}

void FSelectionCounterTool::OnPaint(const FPaintArgs& Args, const FGeometry& AllottedGeometry, const FSlateRect& MyCullingRect, FSlateWindowElementList& OutDrawElements, int32 PaintOnLayerId, const FWidgetStyle& InWidgetStyle, bool bParentEnabled) const
{
    if (TSharedPtr<FCurveEditor> CurveEditor = WeakCurveEditor.Pin())
    {
        // 获取所有选中的关键柄数量
        int32 TotalSelectedKeys = 0;
        for (const TTuple<FCurveModelID, FKeyHandleSet>& Pair : CurveEditor->GetSelection())
        {
            TotalSelectedKeys += Pair.Value.Num();
        }

        // 在视图左上角绘制文本
        if (TotalSelectedKeys > 0)
        {
            const FVector2D TextLocation(10.0f, 10.0f);
            FSlateDrawElement::MakeText(
                OutDrawElements,
                PaintOnLayerId,
                AllottedGeometry.ToPaintGeometry(TextLocation, FVector2D(200.0f, 30.0f)),
                FText::Format(NSLOCTEXT("CounterTool", "Display", "Selected Keys: {0}"), TotalSelectedKeys),
                FAppStyle::GetFontStyle("NormalFont"),
                ESlateDrawEffect::None,
                FLinearColor::White
            );
        }
    }
}
```

## 模块依赖

本插件依赖一个独特的插件：

| 模块/插件 | 用途 |
|---|---|
| `TweeningUtils` | 提供缓动（Tweening）功能的基础框架，用于曲线关键帧的混合操作。 |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `51e61d5d` | Curve Editor: Lattice tool now mirrors user tangents on x-axis | 晶格工具新增功能：在X轴上镜像用户设置的切线 |
| 2026-03-30 | `17e19999` | Tweening Utils: Add hotkeys to change slider position. By default: | 缓动工具新增快捷键以更改滑块位置（默认键位已设定） |
| 2026-03-27 | `f6f50393` | Anim In Engine: Hotkeys for 1) Zoom To/Frame Selection Range Command in Sequencer and Curve Editor, | 新增快捷键用于在序列器和曲线编辑器中缩放至/框选选择范围 |
| 2026-03-23 | `979bfe32` | Curve Editor: Fix non-unity compile issue. | 修复非统一编译（non-unity build）的编译问题 |
| 2026-03-23 | `c3b4873e` | Curve Editor: Fix lattice tool flipping bool values on bool curves, like IK switches, when only movi | 修复晶格工具在布尔曲线（如IK开关）上仅移动时会反转布尔值的问题 |

### 维护评价

*   **维护状态**：**活跃维护**。从提交历史看，2026年仍有新功能开发（晶格工具切线镜像、缓动工具快捷键）和持续的 Bug 修复。
*   **创建时间**：2019年创建，是较早期的引擎插件，功能成熟稳定。
*   **架构价值**：作为曲线编辑器的核心重构，其插件化架构影响深远，是 UE 编辑器扩展的优秀范例。
*   **推荐使用**：**强烈推荐**。该插件是 UE5 中进行高级动画曲线编辑不可或缺的工具，功能强大且维护良好。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/CurveEditorTools)
- [官方文档]()（暂无）
- [测试用例]()（暂无独立测试用例，功能测试通常集成在引擎的自动化测试中）