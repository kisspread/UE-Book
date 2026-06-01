# Avalanche Text Editor

> Compositing, designer and broadcasting tool.\n\nPlugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 运动设计-文本编辑 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（编辑器扩展、可视化控件） |
| 模块 | `AvalancheTextEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheTextEditor) | |

## 用途

**AvalancheTextEditor** 是 Motion Design（Avalanche）插件中用于在编辑器内可视化编辑 3D 文本（`UText3DComponent`）属性的模块。它并非用于运行时，而是扩展了 Unreal Editor 的视口交互能力，让用户能够通过拖拽视口中的直观控件（Handles）来调整 3D 文本的尺寸约束（最大宽/高）、比例缩放以及渐变（Gradient）效果，从而简化了复杂文本样式的编辑流程。该模块是“设计师友好型”工作流的核心组件，将抽象的属性面板设置转化为可视化的空间操作。

## 使用场景

- 你在使用 Motion Design（Avalanche）插件制作广播级图形或虚拟制作素材，需要快速、直观地调整 3D 文本的布局（如最大宽度、换行）和视觉效果（如渐变色彩）。
- 你希望避免在细节面板中反复输入数值，而是通过在视口中拖拽控件来获得即时反馈。
- 你需要精细控制 3D 文本的字符间距（Kerning）。

## 蓝图用法

此模块主要提供编辑器扩展功能，而非直接暴露给蓝图的运行时功能。其核心价值在于增强编辑器中的文本编辑体验。

### 核心功能（编辑器内）

| 功能 | 说明 |
|---|---|
| 文本尺寸可视化 | 在视口中显示并允许拖拽调整文本的最大宽度和高度约束手柄。 |
| 渐变编辑 | 提供中心点、起止点、平滑度等控件，直接在视口内编辑文本渐变效果。 |
| 字符间距调整 | 允许通过控件调整单个字符之间的间距。 |
| 交互工具注册 | 将 3D 文本创建工具集成到 Motion Design 工具栏中。 |

## C++ 用法

该模块是一个标准的编辑器模块，其核心在于模块启动时注册必要的编辑器扩展。

### 头文件引入

```cpp
#include "AvaTextEditorModule.h"
```

### 基本用法

从 `AvaTextEditorModule.h` 可以看出模块启动时会注册组件可视化器（Component Visualizers）和相关命令。以下是模块启动的基本逻辑：

```cpp
// Source: AvalancheTextEditor/Private/AvaTextEditorModule.h
void FAvaTextEditorModule::StartupModule()
{
    // 注册组件可视化器，使视口能绘制和处理文本控件
    RegisterComponentVisualizers();
    // 注册其他编辑器扩展，如命令、样式、工具工厂等
    RegisterDynamicMaterialPropertyGenerator();
}

void FAvaTextEditorModule::ShutdownModule()
{
    // 清理在 StartupModule 中注册的资源
}
```

### 进阶用法

`FAvaTextVisualizer` 类是该模块的核心，它继承自 `FAvaVisualizerBase`，负责处理与 `UText3DComponent` 相关的所有视口交互。其主要功能通过重写基类虚函数实现：

```cpp
// Source: AvalancheTextEditor/Private/Visualizer/AvaTextVisualizer.h
class FAvaTextVisualizer : public FAvaVisualizerBase
{
public:
    // 处理点击视口可视化代理（如某个手柄）的事件
    virtual bool VisProxyHandleClick(...) override;
    // 根据当前编辑状态，提供不同的小部件模式（如平移、缩放）
    virtual bool GetWidgetMode(...) const override;
    // 处理用户在视口中拖拽产生的输入增量（位移、旋转、缩放）
    virtual bool HandleInputDeltaInternal(...) override;
    
protected:
    // 根据当前状态（是否正在编辑宽度/高度/渐变）绘制不同的视口可视化内容
    virtual void DrawVisualizationNotEditing(...) override;
    virtual void DrawVisualizationEditing(...) override;
};
```

## Demo 示例

以下示例展示了一个最小化的编辑器模块，其结构与 `AvalancheTextEditor` 相似，演示如何启动并注册可视化器。

**AvaMyEditorModule.h**
```cpp
#pragma once
#include "Modules/ModuleManager.h"

class FAvaMyEditorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

**AvaMyEditorModule.cpp**
```cpp
#include "AvaMyEditorModule.h"
#include "Editor/UnrealEd/Classes/ComponentVisualizers/MyComponentVisualizer.h"

void FAvaMyEditorModule::StartupModule()
{
    // 注册一个自定义组件的可视化器
    if (GUnrealEd)
    {
        TSharedPtr<FMyComponentVisualizer> Visualizer = MakeShareable(new FMyComponentVisualizer());
        GUnrealEd->RegisterComponentVisualizer(UMyComponent::StaticClass()->GetFName(), Visualizer);
        Visualizer->OnRegister();
    }
}

void FAvaMyEditorModule::ShutdownModule()
{
    if (GUnrealEd)
    {
        GUnrealEd->UnregisterComponentVisualizer(UMyComponent::StaticClass()->GetFName());
    }
}

IMPLEMENT_MODULE(FAvaMyEditorModule, AvaMyEditor)
```

## 模块依赖

基于其在 Motion Design 插件中的位置和提供的功能，该模块可能依赖于以下模块（具体依赖需查看 `AvalancheTextEditor.Build.cs`）：

| 模块 | 用途 |
|---|---|
| `AvalancheEditorCore` | 提供 Motion Design 编辑器共用的基础类和接口，如 `FAvaVisualizerBase`。 |
| `AvalancheInteractiveTools` | 提供交互式工具框架，用于注册和实现文本创建工具。 |
| `Text3D` | 提供 `UText3DComponent` 的运行时核心，是本模块编辑功能的目标对象。 |

**注意**：用户模块如果要使用本模块的编辑器功能，通常不需要直接依赖它，因为它仅扩展编辑器本身。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将场景设置和大纲面板标签页移至独立组，优化编辑器布局。 |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 新增项目设置，可强制禁用3D文本和形状的碰撞检测。 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 优化了视口客户端关联与解除关联时的通知逻辑。 |

### 维护评价

**活跃维护**。该模块作为 Motion Design 插件的一部分，自 2025 年 5 月从实验性功能移入正式版后，持续获得更新和改进。从近期提交记录看（截至 2026 年 5 月），维护团队仍在积极添加新功能（如碰撞控制设置）和优化现有工作流（如编辑器布局调整）。该模块是 Epic 官方维护的虚拟生产工具链的重要组成部分，代码质量高，推荐在 Motion Design 工作流中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheTextEditor)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/virtual-production-and-broadcast-with-unreal-engine/)（Motion Design 插件文档通常位于虚拟制作章节下）