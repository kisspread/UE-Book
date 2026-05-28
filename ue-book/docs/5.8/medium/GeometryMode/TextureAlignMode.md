# Geometry Mode

> Geometry and BSP editing

| 属性 | 值 |
|---|---|
| 中文名 | 几何体编辑模式 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（编辑器模式） |
| 模块 | `GeometryMode` (Editor), `BspMode` (Editor), `TextureAlignMode` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2019-10-28 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/GeometryMode) | |

## 用途

GeometryMode 插件为 UE5 提供了一套专门用于编辑 BSP（Binary Space Partitioning，二分空间分割）几何体的编辑器模式集合。它解决了在编辑器中直接创建、修改和操作 BSP 几何体（如墙壁、地板、坡道等）的问题，这是构建传统关卡原型和简单几何结构的基础工具。尽管现代 UE5 推荐使用静态网格体（Static Mesh），但在某些快速原型设计或特定风格的项目（如复古风格）中，BSP 几何体及其直观的编辑流程仍有其价值。

该插件将原内置于引擎的 BSP 和相关编辑模式提取为独立插件，使得开发者可以在不需要这些功能的项目中禁用它，从而优化编辑器启动时间和资源占用。

## 使用场景

- **关卡快速原型设计**：你需要快速搭建一个房间、走廊或建筑的白模（Graybox）来测试关卡流程和布局。
- **简单几何体创建**：你需要创建一些基础的立方体、圆柱体或楔形体作为占位或场景中的简单道具。
- **BSP 几何体操作**：你需要对场景中的 BSP 几何体进行移动、旋转、缩放、切割（CSG操作）或翻转法线。
- **BSP 表面纹理对齐**：你需要精确地调整附着在 BSP 表面上的纹理的偏移、旋转和缩放。

## 蓝图用法

此插件主要提供编辑器模式（EdMode），而非运行时蓝图节点。其功能通过编辑器的用户界面（工具栏、工具面板）进行交互。然而，`TextureAlignMode` 模块的核心交互逻辑封装在 C++ 类中，可以通过蓝图编辑器感知其存在。

### 核心模式

| 模式 | 说明 | 所在类 |
|---|---|---|
| `BspMode` | 提供创建、操作BSP几何体（如盒体、锥体、CSG操作）的主要工具集。 | `FEdModeBsp` (推断) |
| `TextureAlignMode` | 提供对BSP表面纹理进行平移、旋转、缩放对齐的专用工具。 | `FEdModeTexture` |

### 使用示例（编辑器交互描述）

1.  在编辑器工具栏中，点击“模式”（Modes）面板，选择“几何体”（Geometry）或“纹理”（Texture）选项卡。
2.  **几何体模式**：选中一个BSP Actor，在细节面板中可以调整其几何体属性（如长度、宽度、高度），或在视口中使用平移、旋转、缩放Widget直接操作。
3.  **纹理模式**：选中一个BSP Actor后进入此模式，在视口中会出现专用的纹理操作Widget。通过拖拽该Widget，可以实时移动、旋转该BSP表面上的纹理。

## C++ 用法

该插件的核心是编辑器模式（`FEdMode`）的注册与实现。

### 头文件引入

```cpp
#include "TextureAlignMode/Public/TextureAlignEdMode.h" // 示例：引入纹理对齐模式
```

### 基本用法：自定义编辑器模式

GeometryMode 插件本身是作为示例，展示了如何继承 `FEdMode` 来创建自定义编辑器模式。

```cpp
// 来源：Engine/Plugins/Editor/GeometryMode/Source/TextureAlignMode/Public/TextureAlignEdMode.h
// 一个继承自FEdMode的简单纹理对齐编辑器模式
class FEdModeTexture : public FEdMode
{
public:
    // 进入模式时调用
    virtual void Enter() override;
    // 退出模式时调用
    virtual void Exit() override;
    // 获取模式小部件的位置
    virtual FVector GetWidgetLocation() const override;
    // 判断是否应绘制模式小部件
    virtual bool ShouldDrawWidget() const override;
    // ... 更多重写函数处理输入、坐标系等
};
```

### 进阶用法：自定义模式工具

在编辑器模式内部，可以定义更细分的“工具”（`FModeTool`）来处理特定交互。

```cpp
// 来源：Engine/Plugins/Editor/GeometryMode/Source/TextureAlignMode/Public/TextureAlignEdMode.h
// 一个处理纹理拖拽输入的模式工具
class FModeTool_Texture : public FModeTool
{
public:
    // 处理输入增量（如鼠标拖拽）
    virtual bool InputDelta(FEditorViewportClient* InViewportClient, FViewport* InViewport, FVector& InDrag, FRotator& InRot, FVector& InScale);
    // 开始修改操作
    virtual bool StartModify() { PreviousInputDrag = FVector::ZeroVector; return true; }
    // 结束修改操作
    virtual bool EndModify() { return true; }

private:
    FVector PreviousInputDrag;
};
```

## Demo 示例

以下示例演示了如何注册一个简单的编辑器模式，类似于 `TextureAlignMode` 的基本结构。

### MyCustomEdMode.h
```cpp
#pragma once
#include "EdMode.h"

class FMyCustomEdMode : public FEdMode
{
public:
    virtual void Enter() override;
    virtual void Exit() override;
    virtual FVector GetWidgetLocation() const override;
    virtual bool ShouldDrawWidget() const override;
};
```

### MyCustomEdMode.cpp
```cpp
#include "MyCustomEdMode.h"

void FMyCustomEdMode::Enter()
{
    FEdMode::Enter();
    UE_LOG(LogTemp, Log, TEXT("Entered MyCustomEdMode"));
}

void FMyCustomEdMode::Exit()
{
    UE_LOG(LogTemp, Log, TEXT("Exited MyCustomEdMode"));
    FEdMode::Exit();
}

FVector FMyCustomEdMode::GetWidgetLocation() const
{
    // 返回小部件应位于的位置（例如选中对象的位置）
    return FVector::ZeroVector;
}

bool FMyCustomEdMode::ShouldDrawWidget() const
{
    return true; // 始终绘制小部件
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine/Slate 等） | 该插件作为编辑器模式，主要依赖引擎和编辑器基础框架，其功能相对独立。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `fbd199ea` | [Backout] - CL53903539 | 回退了一次更改（CL53903539）。 |
| 2026-05-14 | `5c94be5d` | Global snapping toggle in toolbar, and (red) indicator when one or more snapping options are enabled | 工具栏中添加了全局捕捉开关，并在启用捕捉选项时显示红色指示器。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从UE_LOG迁移至UE_LOGF。 |
| 2026-02-25 | `12a309dc` | Remove as many PVS suppressions as possible that are no longer needed | 移除了大量不再需要的PVS抑制项。 |
| 2026-02-03 | `61433296` | Rename FViewMatrices members to follow the <Source>To<Target> pattern for transforms, to reduce ambi | 重命名了FViewMatrices的成员以遵循<源>到<目标>的变换命名模式，减少歧义。 |

### 维护评价

**活跃维护**。该插件创建于2019年，属于一个成熟的编辑器功能。从提交历史看，最近6个月内有持续的更新，包括功能增强（全局捕捉开关）、代码现代化（迁移日志宏）和底层优化（重命名、清理）。这些更新表明该插件仍在被积极维护和改进，以确保其与最新引擎版本的兼容性和稳定性。虽然BSP编辑在UE5中不是最主流的建模方式，但它依然是官方工具链的一部分，因此推荐在需要其功能时使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/GeometryMode)
- [官方文档](https://docs.unrealengine.com/)（通用文档，该插件无专属页面）
- [测试用例]()（未在提供的信息中发现）