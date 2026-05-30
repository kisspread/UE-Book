# Motion Design

> Compositing, designer and broadcasting tool.
>
> Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 运动设计 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器工具、组件可视化、媒体处理、场景管理、远程控制、材质编辑等） |
| 模块 | `Avalanche` (Runtime), `AvalancheAttribute` (Runtime), `AvalancheAttributeEditor` (Runtime), `AvalancheCamera` (Runtime), `AvalancheComponentVisualizers` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), `AvalancheEditorCore` (Runtime), `AvalancheEffectors` (Runtime), `AvalancheEffectorsEditor` (Runtime), `AvalancheFunctionalTest` (Runtime), `AvalancheInteractiveTools` (Runtime), `AvalancheInteractiveToolsRuntime` (Runtime), `AvalancheLevelViewport` (Runtime), `AvalancheMRQ` (Runtime), `AvalancheMRQEditor` (Runtime), `AvalancheMask` (Runtime), `AvalancheMaskEditor` (Runtime), `AvalancheMaterial` (Runtime), `AvalancheMedia` (Runtime), `AvalancheMediaEditor` (Runtime), `AvalancheModifiers` (Runtime), `AvalancheModifiersEditor` (Runtime), `AvalancheOutliner` (Runtime), `AvalanchePropertyAnimator` (Runtime), `AvalanchePropertyAnimatorEditor` (Runtime), `AvalancheRemoteControl` (Runtime), `AvalancheRemoteControlEditor` (Runtime), `AvalancheSVGEditor` (Runtime), `AvalancheSceneRig` (Runtime), `AvalancheSceneRigEditor` (Runtime), `AvalancheSceneTree` (Runtime), `AvalancheSequence` (Runtime), `AvalancheSequencer` (Runtime), `AvalancheShapes` (Runtime), `AvalancheShapesEditor` (Runtime), `AvalancheTag` (Runtime), `AvalancheTagEditor` (Runtime), `AvalancheText` (Runtime), `AvalancheTextEditor` (Runtime), `AvalancheTransition` (Runtime), `AvalancheTransitionEditor` (Runtime), `AvalancheViewport` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Motion Design 是一个为虚拟制片、现场活动和广播行业设计的综合性动态图形和实时合成工具集。它解决了在虚幻引擎中快速创建、预览和播放广播级动态图形、字幕条、信息图形以及实时合成内容的问题。该插件将多个功能模块（如3D文本、形状、材质、克隆器/效果器、远程控制、场景树管理等）集成到一个统一的Motion Design工作流中，允许设计师和广播操作员在引擎内直接完成从设计到播出的全流程。

## 使用场景

-   **广播节目包装**：你需要为新闻、体育、天气等节目制作动态的字幕条、角标和全屏动画。 → 使用 Motion Design 的文本、形状、材质和动画模块进行设计和预览。
-   **虚拟演播室**：你需要在实时演播室环境中控制图形元素（如计分板、选手信息）的出现和动画。 → 使用 Motion Design 的场景树、远程控制和序列器模块与演播室系统集成。
-   **现场活动与演唱会**：你需要为现场活动设计和播放动态视觉内容（如舞台背景、歌词显示）。 → 使用 Motion Design 的媒体合成和MRQ（Movie Render Queue）模块进行内容准备和高质量渲染输出。
-   **交互式信息亭**：你需要创建交互式的3D信息展示界面。 → 使用 Motion Design 的交互工具和动画功能。

## 蓝图用法

Motion Design 主要是一个编辑器工具集，其运行时组件（如 `UText3DComponent`）通常通过蓝图进行配置。核心的可视化器和交互逻辑主要在编辑器C++中实现。

### 核心节点（示例 - 基于AvalancheText模块）

由于 `AvalancheTextEditor` 是一个纯编辑器模块，它主要负责提供可视化编辑器和组件可视化器。其对应的运行时模块 `AvalancheText` 可能暴露了以下类型的蓝图节点（需参考 `AvalancheText` 模块的头文件）：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Text` | 设置文本内容 | `UText3DComponent` |
| `Set Font` | 设置文本字体 | `UText3DComponent` |
| `Set Extrusion` | 设置文本挤出深度 | `UText3DComponent` |
| `Set Bevel` | 设置文本斜面 | `UText3DComponent` |

### 使用示例（蓝图描述）

1.  在场景中放置一个 `Text3DActor`。
2.  在细节面板中，通过 `UText3DComponent` 的属性（如 `Text`, `Font`, `Extrude`, `Bevel`）调整文本外观。
3.  在蓝图中，可以通过获取该组件并调用其上的函数（如 `Set Text`）来动态更改文本。

## C++ 用法

Motion Design 的强大功能主要通过其丰富的C++ API实现，特别是编辑器内的可视化器和交互工具。

### 头文件引入

```cpp
// 使用文本组件可视化器
#include "AvalancheTextEditor/Private/Visualizer/AvaTextVisualizer.h"

// 注册文本组件可视化器
#include "AvalancheTextEditor/Private/AvaTextEditorModule.h"
```

### 基本用法（组件可视化器）

此示例展示了如何将 `FAvaTextVisualizer` 与 `UText3DComponent` 关联，使其在编辑器视口中显示交互式控件。
*来源：`AvalancheTextEditor/Private/Visualizer/AvaTextVisualizer.h`*

```cpp
// 在编辑器模块启动时注册组件可视化器
void FAvaTextEditorModule::RegisterComponentVisualizers()
{
    // 创建文本可视化器实例
    TSharedPtr<FAvaTextVisualizer> TextVisualizer = MakeShareable(new FAvaTextVisualizer());
    
    // 将可视化器与 UText3DComponent 关联
    if (GUnrealEd)
    {
        GUnrealEd->RegisterComponentVisualizer(UText3DComponent::StaticClass()->GetFName(), TextVisualizer);
    }
    // 保存引用以在模块关闭时注销
    Visualizers.Add(TextVisualizer);
}
```

### 进阶用法（处理可视化器交互）

`FAvaTextVisualizer` 内部处理视口点击、控件拖拽和数值重置等交互。
*来源：`AvalancheTextEditor/Private/Visualizer/AvaTextVisualizer.h`*

```cpp
// 处理在组件可视化器上的点击
bool FAvaTextVisualizer::VisProxyHandleClick(FEditorViewportClient* InViewportClient, 
                                              HComponentVisProxy* VisProxy,
                                              const FViewportClick& Click)
{
    // 检查点击的代理类型，例如宽度手柄
    if (VisProxy->IsA(HAvaTextMaxTextWidthHandleProxy::StaticGetType()))
    {
        // 开始编辑宽度
        bEditingWidth = true;
        // 存储初始值
        StoreInitialValues();
        // 返回 true 表示已处理点击
        return true;
    }
    // 处理其他代理类型...
    return false;
}

// 处理在编辑过程中鼠标/触笔的增量移动
bool FAvaTextVisualizer::HandleInputDeltaInternal(FEditorViewportClient* InViewportClient, 
                                                   FViewport* InViewport,
                                                   const FVector& InAccumulatedTranslation, ...)
{
    if (bEditingWidth)
    {
        // 根据鼠标移动计算新的最大宽度值
        float NewMaxWidth = InitialMaxWidth + InAccumulatedTranslation.X;
        // 更新到组件属性
        TextComponent->SetMaxWidth(FMath::Max(0.f, NewMaxWidth));
        return true;
    }
    // 处理其他编辑状态...
    return false;
}
```

## Demo 示例

一个最小的编辑器模块示例，展示如何初始化 `AvalancheTextEditor` 模块并注册可视化器。

**AvalancheTextEditorDemoModule.h**
```cpp
#pragma once
#include "Modules/ModuleManager.h"

class FAvalancheTextEditorDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

**AvalancheTextEditorDemoModule.cpp**
```cpp
#include "AvalancheTextEditorDemoModule.h"
#include "AvalancheTextEditor/Private/AvaTextEditorModule.h"

void FAvalancheTextEditorDemoModule::StartupModule()
{
    // 实例化并启动真实的AvalancheTextEditor模块逻辑
    // 通常，AvalancheTextEditor模块在自己的StartupModule中会自动处理这些。
    // 这里仅为演示，展示其核心组件。
    FAvaTextEditorModule TextEditorModule;
    TextEditorModule.StartupModule(); // 内部会注册可视化器等
}

void FAvalancheTextEditorDemoModule::ShutdownModule()
{
    // 清理工作...
}

IMPLEMENT_MODULE(FAvalancheTextEditorDemoModule, AvalancheTextEditorDemo)
```

## 模块依赖

以下模块是 `AvalancheTextEditor` 功能实现所**独特依赖**的，已排除常见的 Core/Engine/Slate 等。

| 模块 | 用途 |
|---|---|
| `Text3D` | 提供核心的 `UText3DComponent`，是本模块可视化的对象。 |
| `AvalancheCore` | 提供 Motion Design 框架的基础类和接口，如 `FAvaVisualizerBase`。 |
| `AvalancheInteractiveTools` | 提供交互工具的框架，`AvaTextActorTool` 基于此实现。 |
| `AvalancheEditorCore` | 提供编辑器工具和命令注册的通用基础设施。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将Motion Design的场景设置和大纲视图选项卡独立成组，优化编辑器布局。 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 为使用Rundown页面设置时的MRQ（电影渲染队列）渲染过程添加了分析数据收集。 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 在节目控制工具栏中增加了页面加载选项（全部、下一个、已选），并优化了相关功能。 |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 新增了项目级设置，可强制禁用Text3D和形状的碰撞检测。 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构视口代码，通过在客户端关联或解除关联时进行通知来优化必需的代码复用。 |

### 维护评价

**活跃维护**。Motion Design 插件自2025年5月从实验性功能迁移至虚拟制片分类后，一直在持续进行活跃的功能开发和优化。近一个月的提交记录显示，团队专注于完善编辑器UI（如独立化选项卡）、增强与MRQ渲染管线的集成、增加用户控制选项（如页面加载策略、碰撞设置）以及进行底层代码重构以提高代码质量。该插件是Epic Games为专业虚拟制片和广播市场打造的核心工具，预计将持续得到长期维护和更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/using-motion-design-in-unreal-engine/)（虚幻引擎官方文档中关于Motion Design的章节）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Tests)