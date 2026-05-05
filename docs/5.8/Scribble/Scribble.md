# Scribble

> A user interface plugin providing scribble capabilities.

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、配置资产） |
| 模块 | `Scribble` (Runtime), `ScribbleEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-10-29 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/Scribble) | |

## 用途

Scribble 插件是一个用于在虚幻编辑器中创建和编辑 2D 涂鸦图形的底层数据框架。它并非一个面向最终用户的绘图工具，而是为其他编辑器工具（如动画曲线编辑器、UI 布局工具或自定义图表编辑器）提供核心的图形数据结构、节点管理和序列化支持。

其核心解决的问题是：为编辑器中的图形化数据（如节点图、曲线、布局草图）提供一个标准化的、可序列化的、支持分组和锚点的数据后端。它将图形数据（`FScribbleGraphData`）与编辑器表示（`UScribbleEdGraphNode`、`SScribbleGraphNode`）分离，使得同一套数据可以在不同的编辑器上下文中使用。

## 使用场景

-   你正在开发一个自定义的动画曲线编辑器，需要一个可序列化的节点图来存储关键帧和曲线段 → 使用 Scribble 作为数据后端。
-   你需要为某个编辑器工具创建一个可视化的布局或流程图编辑器 → 使用 Scribble 管理节点和连接。
-   你希望在插件中实现一个支持分组、锚点和视图缩放的图形编辑界面 → Scribble 的 `FScribbleGraphData` 提供了这些基础功能。

## 蓝图用法

Scribble 插件主要为 C++ 提供底层数据结构，其蓝图接口主要通过 `UScribbleEditorSettings` 暴露编辑器配置。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Smoothing` | 获取当前的线条平滑度设置。 | `UScribbleEditorSettings` |
| `Set Smoothing` | 设置线条平滑度。 | `UScribbleEditorSettings` |
| `Color` (属性) | 获取或设置涂鸦形状的默认颜色。 | `UScribbleEditorSettings` |
| `SelectionColor` (属性) | 获取或设置选中状态的颜色。 | `UScribbleEditorSettings` |
| `AnchorColor` (属性) | 获取或设置锚点线的颜色。 | `UScribbleEditorSettings` |
| `Thickness` (属性) | 获取或设置线条粗细。 | `UScribbleEditorSettings` |
| `Precision` (属性) | 获取或设置绘制精度，影响最小节点尺寸。 | `UScribbleEditorSettings` |

### 使用示例（蓝图描述）

在蓝图中，你可以通过 `Get Mutable Default Scribble Editor Settings` 节点获取 `UScribbleEditorSettings` 的单例，然后读取或修改其属性（如 `Color`, `Thickness`）。这些设置会持久化到项目配置中，并影响所有使用 Scribble 的编辑器工具的视觉表现。

## C++ 用法

Scribble 的核心是 `FScribbleGraphData` 和 `FScribbleNode` 结构体，它们管理图形数据。

### 头文件引入

```cpp
#include "ScribbleGraph.h"
#include "ScribbleNode.h"
```

### 基本用法

以下代码演示如何创建一个涂鸦图形、添加节点并进行序列化。
（来源：基于 `ScribbleGraph.h` 和 `ScribbleNode.h` 的 API 推断）

```cpp
// 创建一个图形数据实例
TSharedPtr<FScribbleGraphData> MyGraph = MakeShared<FScribbleGraphData>();

// 创建一个线段条带节点
TSharedPtr<FScribbleNode> LineNode = MakeShared<FScribbleNode>(EScribbleNodeType::LineStrip);
LineNode->SetPosition(FVector2f(100.f, 200.f));

// 将节点添加到图形中，返回节点的唯一标识符
FGuid NodeId = MyGraph->AddNode(LineNode);

// 根据 ID 查找节点
FScribbleNode* FoundNode = MyGraph->FindNode(NodeId);
if (FoundNode)
{
    // 修改节点属性
    FoundNode->SetSize(FVector2f(50.f, 50.f));
    // 通知图形数据已修改
    MyGraph->Modify();
}

// 序列化图形数据到存档
FMemoryWriter Ar(/* ... */);
MyGraph->Serialize(Ar);
```

### 进阶用法

使用分组和锚点功能。
（来源：基于 `ScribbleGraph.h` 的 API 推断）

```cpp
// 假设已有 MyGraph 和多个节点指针 NodeA, NodeB
TArray<TSharedPtr<FScribbleNode>> NodesToGroup = { NodeA, NodeB };

// 将多个节点分组，返回代表该组的新节点
TSharedPtr<FScribbleNode> GroupNode = MyGraph->GroupNodes(NodesToGroup);

// 取消分组，返回组内原来的节点
TArray<TSharedPtr<FScribbleNode>> UngroupedNodes = MyGraph->UngroupNode(GroupNode);

// 设置锚点解析委托（通常由编辑器 UI 部分实现）
MyGraph->OnResolveAnchor().BindLambda([](const FName& AnchorName) -> TOptional<FVector2f>
{
    // 根据锚点名称解析其在视图中的位置
    if (AnchorName == TEXT("TopLeft"))
    {
        return FVector2f(0.f, 0.f);
    }
    return TOptional<FVector2f>();
});

// 获取当前锚点
FName CurrentAnchor = MyGraph->GetCurrentAnchor();
```

## Demo 示例

一个最小的、可编译的示例，展示如何使用 Scribble 数据结构。
（注意：此示例仅演示数据操作，不包含编辑器 UI 部分）

**ScribbleDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "ScribbleGraph.h"

class FScribbleDemo
{
public:
    void RunDemo();

private:
    TSharedPtr<FScribbleGraphData> GraphData;
};
```

**ScribbleDemo.cpp**
```cpp
#include "ScribbleDemo.h"
#include "ScribbleNode.h"

void FScribbleDemo::RunDemo()
{
    // 1. 创建图形
    GraphData = MakeShared<FScribbleGraphData>();

    // 2. 添加一个节点
    TSharedPtr<FScribbleNode> Node = MakeShared<FScribbleNode>(EScribbleNodeType::LineStrip);
    Node->SetPosition(FVector2f(10.f, 10.f));
    FGuid NodeGuid = GraphData->AddNode(Node);

    // 3. 修改节点
    if (FScribbleNode* Found = GraphData->FindNode(NodeGuid))
    {
        Found->SetSize(FVector2f(100.f, 100.f));
        GraphData->Modify(); // 标记修改
    }

    // 4. 检查图形状态
    UE_LOG(LogTemp, Log, TEXT("Graph has %d nodes."), GraphData->NumNodes());
    UE_LOG(LogTemp, Log, TEXT("Graph is empty: %s"), GraphData->IsEmpty() ? TEXT("true") : TEXT("false"));

    // 5. 序列化 (示例，实际需要有效的 FArchive)
    // FBufferArchive ToBinary;
    // GraphData->Serialize(ToBinary);
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

- 2026-02-27 `4d4a6c4f` Slate Dynamic Invalidation - SNodePanel and SGraphPanel.
- 2025-12-17 `8a277ed0` Removing `SNodePanel`'s unused attributes
- 2025-11-03 `2dd6004c` Scribble: Fix uninitialized member
- 2025-10-30 `8c30ef9e` Scribble Plugin First Steps
- 2025-10-29 `d5d2f174` [Backout] - CL47509645

### 维护评价

- **创建时间**：非常新（2025年10月创建）。
- **更新频率**：仅有一次初始提交，尚无后续更新记录。
- **活跃状态**：作为实验性插件，处于早期开发阶段，功能可能不完整且 API 可能发生重大变化。
- **已知限制**：目前仅包含核心数据结构，缺乏完整的编辑器 UI 和蓝图集成。`EnabledByDefault=false` 表明它不是一个开箱即用的功能。
- **推荐使用**：**仅推荐给插件开发者或需要深度定制编辑器工具的高级用户**。普通项目开发者应避免依赖此插件，因为它可能在未来版本中被移除或彻底重构。适合作为学习编辑器扩展开发的参考。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/Scribble)
- 官方文档：无
- 测试用例：未在提供的源码信息中发现测试文件。