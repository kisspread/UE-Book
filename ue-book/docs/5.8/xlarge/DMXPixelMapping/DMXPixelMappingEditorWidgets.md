# DMX Pixel Mapping

> Tools set for map LED digital pixel strip or fixture arrays regardless of shape or size

| 属性 | 值 |
|---|---|
| 中文名 | DMX 像素映射 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `DMXPixelMappingBlueprintGraph` (Runtime), `DMXPixelMappingCore` (Runtime), `DMXPixelMappingEditor` (Runtime), `DMXPixelMappingEditorWidgets` (Runtime), `DMXPixelMappingRenderer` (Runtime), `DMXPixelMappingRuntime` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-08-04 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXPixelMapping) | |

## 用途

DMX Pixel Mapping 插件是一个用于将 DMX 信号映射到 LED 像素阵列或灯具阵列的专业工具集。它解决了虚拟制片和现场演出中，如何将数字 DMX 信号精确地映射到复杂形状、不规则排列的 LED 像素条或灯具矩阵的问题。

插件的核心功能是提供一套可视化的编辑和运行时工具，允许用户：
1.  **定义像素布局**：在编辑器中直观地绘制和设计各种形状（矩形、圆形、任意多边形等）的像素阵列。
2.  **映射 DMX 通道**：将 DMX 信号的 Universe、通道（Address）映射到布局中的每一个虚拟“像素点”或灯具。
3.  **驱动视觉效果**：在运行时，将 DMX 信号实时转换为灯光颜色、强度等数据，驱动场景中的灯光、材质或粒子效果。

**注意**：当前文档描述的 `DMXPixelMappingEditorWidgets` 模块已被标记为**废弃**（UE_DEPRECATED）。该模块中的旧版编辑器小部件（如 `SDMXPixelMappingScreenLayout`）已不再维护，官方建议根据每个视图自行实现，并参考 `SDMXPixelMappingOutputComponent` 作为示例。插件的核心功能已迁移到其他模块。

## 使用场景

-   **虚拟制片（Virtual Production）**：在 LED 虚拟摄影棚中，实时控制 LED 墙幕的像素色彩，使其与场景中的环境光或背景相匹配。
-   **现场演出（Live Events）**：为舞台灯光秀、建筑立面投影等创建复杂的、可编程的像素映射效果。
-   **互动装置（Interactive Installations）**：将 DMX 信号（可能来自传感器或交互程序）映射到 LED 墙或艺术装置上，实现实时互动。
-   **灯光设计师工作流**：在 Unreal Engine 内部完成从灯光设计到效果预览的完整流程，无需切换到其他软件。

## 蓝图用法

由于 `DMXPixelMappingEditorWidgets` 模块主要提供编辑器 UI 逻辑且已被废弃，其内部类（如 `SDMXPixelMappingScreenLayout`）不包含暴露给蓝图的 `UFUNCTION`。像素映射的核心蓝图 API 主要存在于 `DMXPixelMappingRuntime` 模块中。以下为相关功能的节点概览：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `DMX Pixel Mapping` 相关节点 | 用于在运行时从像素映射蓝图组件获取/设置 DMX 数据、颜色等 | `UDMXPixelMapping*Component` (Runtime 模块) |

*注意：具体节点需查阅 `DMXPixelMappingRuntime` 模块。本模块提供的旧版 Slate 控件不直接暴露给蓝图。*

## C++ 用法

**重要提示**：以下代码示例使用的是**已废弃**的 `DMXPixelMappingEditorWidgets` 模块中的类。这些类仅作为历史参考，不建议在新的编辑器视图中直接使用。Epic 建议查看 `SDMXPixelMappingOutputComponent` 等新实现。

### 头文件引入

```cpp
// 引入已废弃的编辑器小部件头文件（仅供了解历史代码）
#include "SDMXPixelMappingEditorWidgets.h"
#include "DMXPixelMappingComponentWidget.h"
```

### 基本用法（已废弃）

以下示例展示了如何创建和使用一个简单的像素网格布局控件（已废弃）。

```cpp
// 示例：创建一个简单的屏幕布局小部件（已废弃类 SDMXPixelMappingScreenLayout）
// 文件路径：历史代码或测试用例中可能使用

// 1. 在 Slate 控件树中构建该小部件
SNew(SDMXPixelMappingScreenLayout)
    .NumXCells(10) // X 方向像素数量
    .NumYCells(5)  // Y 方向像素数量
    .Distribution(EDMXPixelMappingDistribution::TopLeftToRight) // 像素排列分布顺序
    .PixelFormat(EDMXCellFormat::PF_RGB) // 像素数据格式
    .bShowAddresses(true) // 是否显示 DMX 地址
    .bShowUniverse(true)  // 是否显示 Universe 号
    .LocalUniverse(1)     // 本地 Universe 号
    .StartAddress(1)      // 起始地址

// 2. 后续可以通过成员函数更新布局参数
TSharedPtr<SDMXPixelMappingScreenLayout> MyLayout = SNew(SDMXPixelMappingScreenLayout) /* ... */;
// 假设有一个更新参数的函数
MyLayout->RebuildGrid(FDMXPixelMappingScreenComponentGridParams{ 20, 10, ... });
```

### 进阶用法（已废弃 - 组合组件控件）

`FDMXPixelMappingComponentWidget` 是一个管理复合 Slate 控件的旧版包装类，用于在画布上定位和显示像素映射组件。

```cpp
// 示例：创建和使用一个组件控件包装器（已废弃类 FDMXPixelMappingComponentWidget）

// 1. 创建自定义的组件框和标签
TSharedPtr<SDMXPixelMappingComponentBox> MyComponentBox = SNew(SDMXPixelMappingComponentBox);
TSharedPtr<SDMXPixelMappingComponentLabel> MyComponentLabel = SNew(SDMXPixelMappingComponentLabel);

// 2. 创建包装器
FDMXPixelMappingComponentWidget ComponentWidget(MyComponentBox, MyComponentLabel, true); // true 表示标签在上方

// 3. 将其添加到画布中
ComponentWidget.AddToCanvas(MyCanvas, 0.0f); // MyCanvas 是 TSharedRef<SConstraintCanvas>

// 4. 更新其位置和大小
ComponentWidget.SetPosition(FVector2D(100.0f, 50.0f));
ComponentWidget.SetSize(FVector2D(200.0f, 100.0f));
ComponentWidget.SetLabelText(FText::FromString(TEXT("LED Strip 1")));
ComponentWidget.SetColor(FLinearColor::Green);
```

## Demo 示例

鉴于该模块已废弃，这里不提供基于旧类的新 Demo。强烈建议参考 `DMXPixelMappingRenderer` 和 `DMXPixelMappingRuntime` 模块中的代码，特别是 `SDMXPixelMappingOutputComponent`，这是官方推荐的新实现方式。可以在引擎源码中搜索该类，查看其如何处理视图和渲染逻辑。

## 模块依赖

`DMXPixelMappingEditorWidgets` 模块的依赖相对简单，主要依赖于 DMX 核心模块和 Slate UI 框架。

| 模块 | 用途 |
|---|---|
| `DMXPixelMappingCore` | DMX 像素映射的核心类型定义（如枚举） |
| `Slate`, `SlateCore` | 用于构建编辑器 UI 控件 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `5f2a2a90` | DMX - Fix a crash when pixel mapping has unpatched components and draws patch colors | 修复了当像素映射包含未连接组件并绘制补丁颜色时发生的崩溃。 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口：重构与客户端关联/解除关联时的通知逻辑。 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回滚了变更 CL53913857。 |
| 2026-05-14 | `9ede83f2` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口：重构与客户端关联/解除关联时的通知逻辑（不同版本）。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，双精度常量截断为浮点数产生警告的代码。 |

### 维护评价

**评价**：**维护中，但该模块已废弃**。

1.  **创建时间与年龄**：插件整体创建于 2021 年，约 5 年历史，属于较新的插件。但 `DMXPixelMappingEditorWidgets` 模块自 5.1 版本起已被标记为废弃。
2.  **更新频率**：从 git log 看，DMX 像素映射相关的提交在 2026 年 5 月仍有活跃，表明**整个 DMX 像素映射功能仍在维护**。但最近的改动主要涉及崩溃修复和重构，并未涉及被废弃的 `EditorWidgets` 模块。
3.  **已知问题**：主要问题就是该模块已被官方废弃，其中的类和小部件不再被支持，且可能在未来的引擎版本中被移除。
4.  **推荐建议**：
    *   **不要使用** `DMXPixelMappingEditorWidgets` 模块中的任何类或控件。
    *   **推荐使用** `DMXPixelMappingRuntime`、`DMXPixelMappingRenderer` 等模块的功能来实现运行时像素映射。
    *   对于编辑器视图的实现，请研究并参考引擎中更新的实现模式（如 `SDMXPixelMappingOutputComponent`）。

## 相关链接

-   [源码 (Plugin Root)](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXPixelMapping)
-   [官方文档](https://docs.unrealengine.com/) (搜索 "DMX" 或 "Pixel Mapping")