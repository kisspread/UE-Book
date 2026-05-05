# Scribble

> A user interface plugin providing scribble capabilities.

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `Scribble` (Runtime), `ScribbleEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-10-29 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/Scribble) | |

## 用途

Scribble 是一个实验性的编辑器插件，它提供了一个基于节点图（Node Graph）的自由形式涂鸦式绘图界面。其核心功能是允许用户在编辑器中创建、编辑和管理由涂鸦式节点（Scribble Nodes）组成的图形数据（`FScribbleGraphData`）。这些节点不是传统的蓝图节点，而是具有自定义形状、大小和位置的自由形式元素，适用于快速原型设计、注释或创建非结构化的视觉布局。

该插件解决的问题是：在动画或可视化脚本工作流中，有时需要一种比标准节点图更自由、更接近草图的工具来快速勾勒想法、组织思路或创建自定义的视觉辅助。Scribble 提供了这种能力。

## 使用场景

-   你是一名动画师或技术美术，需要在动画蓝图中快速草拟状态机或逻辑流程的草图，用于团队讨论或个人记录。
-   你正在开发一个需要自定义可视化编辑器的工具，希望集成一个轻量级、可定制的节点绘图表面。
-   你需要在编辑器中创建自由形式的注释或图表，用于文档或设计参考。

## 蓝图用法

该插件主要在编辑器中使用，其核心功能通过 `SScribbleGraphPanel` Slate 控件暴露。以下是从头文件中提取的关键蓝图可用接口。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IsScribbleEnabled` | 查询涂鸦功能是否启用 | `SScribbleGraphPanel` |
| `HasActiveNodeType` | 查询是否有活动的节点类型（用于创建新节点） | `SScribbleGraphPanel` |
| `ActivateSelectionMode` | 激活选择模式 | `SScribbleGraphPanel` |
| `GetActiveNodeType` | 获取当前活动的节点类型 | `SScribbleGraphPanel` |
| `SetActiveNodeType` | 设置要创建的节点类型 | `SScribbleGraphPanel` |
| `GetScribbleEdGraph` | 获取关联的 `UScribbleEdGraph` 对象 | `SScribbleGraphPanel` |
| `GetScribbleGraph` | 获取底层的 `FScribbleGraphData` 数据 | `SScribbleGraphPanel` |

### 使用示例（蓝图描述）

1.  **创建图表面板**：在编辑器工具或自定义面板的 Slate 构造函数中，使用 `SNew(SScribbleGraphPanel)` 创建一个涂鸦图表面板。
2.  **配置面板**：通过 Slate 属性设置面板行为，例如：
    *   `ScribbleEnabled`: 控制涂鸦功能是否激活。
    *   `ScribbleNodeType`: 绑定一个变量，指定当前要绘制的节点类型。
    *   `ScribbleColor`, `ScribbleThickness`, `ScribblePrecision`: 控制绘制的视觉样式。
    *   `OnSetNodeType`: 绑定一个委托，当用户通过UI更改节点类型时触发。
3.  **交互**：用户可以在面板中通过鼠标点击和拖拽来创建、选择、移动和删除涂鸦节点。面板支持撤销/重做操作。

## C++ 用法

### 头文件引入

```cpp
#include "SScribbleGraphPanel.h"
#include "ScribbleEdGraph.h"
#include "ScribbleEdGraphNode.h"
```

### 基本用法

以下代码展示了如何在编辑器 Slate 界面中创建和配置一个涂鸦图表面板。

```cpp
// 在某个 Slate 窗口或面板的 Construct 函数中
void SMyEditorPanel::Construct(const FArguments& InArgs)
{
    // 假设我们有一个 FScribbleGraphData 的共享指针
    TSharedPtr<FScribbleGraphData> MyGraphData = MakeShared<FScribbleGraphData>();

    ChildSlot
    [
        SNew(SScribbleGraphPanel)
        .GraphData(MyGraphData) // 传入图数据
        .ScribbleEnabled(true) // 启用涂鸦
        .ScribbleNodeType(EScribbleNodeType::Rectangle) // 默认绘制矩形节点
        .ScribbleColor(FLinearColor::White) // 绘制颜色为白色
        .ScribbleThickness(2.0f) // 线条粗细
        .ScribblePrecision(10.0f) // 绘制精度
        .ShouldDrawBackground(true) // 绘制背景
        .AllowNavigation(true) // 允许平移和缩放
    ];
}
```

### 进阶用法

通过 `UScribbleEdGraph` 管理节点和选择状态。

```cpp
// 获取图表面板关联的 EdGraph
UScribbleEdGraph* EdGraph = ScribbleGraphPanel->GetScribbleEdGraph();
if (EdGraph)
{
    // 添加一个新节点到图中
    TSharedPtr<FScribbleNode> NewNode = MakeShared<FScribbleNode>();
    FGuid NewNodeId = EdGraph->AddScribbleNode(NewNode);

    // 选择特定节点
    TArray<FGuid> NodesToSelect = { NewNodeId };
    EdGraph->SelectNodes(NodesToSelect);

    // 获取所有选中的节点ID
    const TArray<FGuid>& SelectedIds = EdGraph->GetSelectedNodeIds();

    // 删除选中的节点
    EdGraph->RemoveSelectedNodes();

    // 对选中的节点进行分组
    EdGraph->GroupSelectedNodes();
}
```

## Demo 示例

一个最小的编辑器窗口，包含一个涂鸦面板。

**MyScribbleWindow.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Widgets/SCompoundWidget.h"

class SMyScribbleWindow : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SMyScribbleWindow) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs);

private:
    TSharedPtr<class SScribbleGraphPanel> ScribblePanel;
    TSharedPtr<struct FScribbleGraphData> GraphData;
};
```

**MyScribbleWindow.cpp**
```cpp
#include "MyScribbleWindow.h"
#include "SScribbleGraphPanel.h"
#include "ScribbleGraph.h"

void SMyScribbleWindow::Construct(const FArguments& InArgs)
{
    GraphData = MakeShared<FScribbleGraphData>();

    ChildSlot
    [
        SNew(SVerticalBox)
        + SVerticalBox::Slot()
        .AutoHeight()
        [
            SNew(STextBlock)
            .Text(FText::FromString(TEXT("Scribble Demo Window")))
        ]
        + SVerticalBox::Slot()
        .FillHeight(1.0f)
        [
            SAssignNew(ScribblePanel, SScribbleGraphPanel)
            .GraphData(GraphData)
            .ScribbleEnabled(true)
            .ScribbleNodeType(EScribbleNodeType::Freeform)
            .ScribbleColor(FLinearColor(0.2f, 0.8f, 1.0f))
        ]
    ];
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Scribble` | 提供核心的涂鸦图数据结构和运行时逻辑 |
| `GraphEditor` | 提供 `SGraphPanel` 等基础图编辑器控件 |
| `EditorFramework` | 提供编辑器框架和撤销/重做支持 |

## 维护状态

### 近期更新

- 2026-02-27 `4d4a6c4f` Slate Dynamic Invalidation - SNodePanel and SGraphPanel.
- 2025-12-17 `8a277ed0` Removing `SNodePanel`'s unused attributes
- 2025-11-03 `2dd6004c` Scribble: Fix uninitialized member
- 2025-10-30 `8c30ef9e` Scribble Plugin First Steps
- 2025-10-29 `d5d2f174` [Backout] - CL47509645

### 维护评价

-   **创建时间**：2025年10月，是一个非常新的插件。
-   **更新频率**：在创建初期有密集的提交，功能在快速迭代。
-   **活跃状态**：处于**活跃开发**阶段。
-   **已知限制**：作为实验性插件，API 可能不稳定，功能可能不完整。
-   **推荐使用**：适合用于**实验、原型开发或内部工具**。不建议在需要长期稳定支持的生产项目中直接依赖。可以关注其发展，待其成熟后考虑采用。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/Scribble)
-   [官方文档]() (暂无)