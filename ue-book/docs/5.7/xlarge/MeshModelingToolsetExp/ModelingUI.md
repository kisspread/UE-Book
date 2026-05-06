# Experimental Mesh Modeling Toolset

> A set of experimental modules implementing 3D mesh creation and editing based on the Interactive Tools Framework

| 属性 | 值 |
|---|---|
| 中文名 | 实验性网格建模工具集 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（工具集相关资源） |
| 模块 | `GeometryProcessingAdapters` (Runtime), `MeshModelingToolsEditorOnlyExp` (Runtime), `MeshModelingToolsExp` (Runtime), `ModelingEditorUI` (Runtime), `ModelingUI` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-29 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MeshModelingToolsetExp) | |

---

## 当前模块：ModelingUI (Runtime)

本模块提供了一个可拖拽的覆盖层（Draggable Box Overlay）UI 组件，用于在视口（Viewport）或其他大型 Widget 中放置可自由拖动的面板。该组件是建模模式（Modeling Mode）中常用工具面板的底层基础。

> **注意**：原 `SDraggableBoxOverlay`、`SDraggableBox` 和 `FDraggableBoxUIDragOperation` 已在 UE 5.6 中废弃，请改用 `UE::ToolWidgets::SDraggableBoxOverlay`。

---

## 用途

- 解决在视口中放置浮动 UI 面板时无法直接拖拽定位的问题。
- 提供统一的拖拽交互机制，使得工具面板可以像窗口一样被用户随意拖动。
- 替代早期版本中复杂的拖放操作逻辑，简化开发。

## 使用场景

- 你正在开发一个基于交互工具框架的编辑器模式，需要为工具面板提供可拖拽功能。
- 你需要在视口中放置一个半透明操作面板，并允许用户随意调整其位置。
- 你需要自定义一个不受视口边界裁剪的浮动 UI。

## 蓝图用法

本模块不提供任何 `BlueprintCallable` 或 `BlueprintReadWrite` 成员，所有功能均通过 C++ 的 Slate 组件实现。

## C++ 用法

### 头文件引入

```cpp
#include "ModelingUIModule.h"
#include "ModelingWidgets/SDraggableBox.h"   // 已废弃，但仍可使用（UE 5.6 以前）
#include "ToolWidgets/SDraggableBoxOverlay.h" // 推荐使用的新类
```

### 基本用法

创建并使用新的 `UE::ToolWidgets::SDraggableBoxOverlay`：

```cpp
// 在 viewport overlay 中放置可拖拽面板
SAssignNew(MyOverlay, SOverlay)
+ SOverlay::Slot()
.HAlign(HAlign_Right)
.VAlign(VAlign_Bottom)
[
    SNew(UE::ToolWidgets::SDraggableBoxOverlay)
    .Visibility(EVisibility::Visible)
    [
        // 你的内容
        SNew(SBorder)
        .BorderImage(FCoreStyle::Get().GetBrush("ToolPanel.GroupBorder"))
        .Padding(4.0f)
        [
            SNew(STextBlock)
            .Text(FText::FromString("Drag me"))
        ]
    ]
];
```

### 进阶用法

如果你需要精确控制位置，可以获取 `SDraggableBoxOverlay` 的指针并调用 `SetBoxPosition`：

```cpp
TSharedPtr<UE::ToolWidgets::SDraggableBoxOverlay> MyDraggableBox;
SAssignNew(MyDraggableBox, UE::ToolWidgets::SDraggableBoxOverlay)
.bPositionRelativeToBottom(true)
[
    // ...
];

// 在某个时刻设置位置（距离左边缘 200px，距离下边缘 100px）
MyDraggableBox->SetBoxPosition(200.0f, 100.0f);
```

## Demo 示例

一个完整的、可编译的最小示例，展示如何在一个编辑器视口中添加可拖拽面板。

**MyDemoWidget.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Widgets/SCompoundWidget.h"
#include "ToolWidgets/SDraggableBoxOverlay.h"

class SMyDemoWidget : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SMyDemoWidget) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs);

private:
    TSharedPtr<UE::ToolWidgets::SDraggableBoxOverlay> DragBox;
};
```

**MyDemoWidget.cpp**

```cpp
#include "MyDemoWidget.h"
#include "Widgets/Layout/SOverlay.h"
#include "Widgets/Text/STextBlock.h"
#include "Widgets/Layout/SBorder.h"
#include "Styling/CoreStyle.h"

void SMyDemoWidget::Construct(const FArguments& InArgs)
{
    ChildSlot
    [
        SNew(SOverlay)
        + SOverlay::Slot()
        .HAlign(HAlign_Left)
        .VAlign(VAlign_Top)
        [
            SAssignNew(DragBox, UE::ToolWidgets::SDraggableBoxOverlay)
            .bPositionRelativeToBottom(false)
            [
                SNew(SBorder)
                .BorderImage(FCoreStyle::Get().GetBrush("ToolPanel.GroupBorder"))
                .Padding(10.0f)
                [
                    SNew(STextBlock)
                    .Text(FText::FromString("Drag me anywhere"))
                    .ColorAndOpacity(FLinearColor::White)
                ]
            ]
        ]
    ];

    // 初始位于左上角
    DragBox->SetBoxPosition(100.0f, 50.0f);
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

| 模块 | 用途 |
|---|---|
| `Slate` | 所有 UI 组件的基础 |
| `UMG` | 仅在需要与 UserWidget 交互时使用（非必需） |

## 维护状态

### 近期更新

- 2025-12-18 `79bdb336` — #jira UE-356302（修复或更新）
- 2025-11-18 `e352ab23` — 修复将多个动态网格源转换为静态网格时在建模模式下的崩溃
- 2025-10-03 `fea318f1` — PR #13360: 为 CubeGrid 添加“Assign and Start New”键盘命令
- 2025-10-03 `53d4840d` — ModelingTools: 修复 CubeGrid “Accept and Start New” 在编辑现有网格时无法正确工作
- 2025-09-29 `300d2503` — Merge Actor - Approximate: 使用正确的合并材质以避免显示默认引擎纹理

### 维护评价

- **活跃维护**：最近两个月内仍有功能性更新和 bug 修复。
- **实验性警告**：插件标记为实验性，API 可能随版本变化。
- **推荐使用**：如果使用建模模式或需要自定义可拖拽 UI，该模块提供的组件已趋于稳定（UE 5.6 后使用命名空间版本），建议迁移至新 API。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MeshModelingToolsetExp)
- [官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/modeling-mode)（建模模式概述）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MeshModelingToolsetExp/Tests)（若有）