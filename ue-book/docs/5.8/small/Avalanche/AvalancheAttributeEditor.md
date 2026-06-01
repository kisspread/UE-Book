# Motion Design

> Compositing, designer and broadcasting tool.
> Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 运动设计 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `Avalanche` (Runtime), `AvalancheAttribute` (Runtime), `AvalancheAttributeEditor` (Runtime), `AvalancheCamera` (Runtime), `AvalancheComponentVisualizers` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), `AvalancheEditorCore` (Runtime), `AvalancheEffectors` (Runtime), `AvalancheEffectorsEditor` (Runtime), `AvalancheFunctionalTest` (Runtime), `AvalancheInteractiveTools` (Runtime), `AvalancheInteractiveToolsRuntime` (Runtime), `AvalancheLevelViewport` (Runtime), `AvalancheMRQ` (Runtime), `AvalancheMRQEditor` (Runtime), `AvalancheMask` (Runtime), `AvalancheMaskEditor` (Runtime), `AvalancheMaterial` (Runtime), `AvalancheMedia` (Runtime), `AvalancheMediaEditor` (Runtime), `AvalancheModifiers` (Runtime), `AvalancheModifiersEditor` (Runtime), `AvalancheOutliner` (Runtime), `AvalanchePropertyAnimator` (Runtime), `AvalanchePropertyAnimatorEditor` (Runtime), `AvalancheRemoteControl` (Runtime), `AvalancheRemoteControlEditor` (Runtime), `AvalancheSVGEditor` (Runtime), `AvalancheSceneRig` (Runtime), `AvalancheSceneRigEditor` (Runtime), `AvalancheSceneTree` (Runtime), `AvalancheSequence` (Runtime), `AvalancheSequencer` (Runtime), `AvalancheShapes` (Runtime), `AvalancheShapesEditor` (Runtime), `AvalancheTag` (Runtime), `AvalancheTagEditor` (Runtime), `AvalancheText` (Runtime), `AvalancheTextEditor` (Runtime), `AvalancheTransition` (Runtime), `AvalancheTransitionEditor` (Runtime), `AvalancheViewport` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Avalanche（内部代号 Motion Design）是一套功能极其强大的运动图形设计套件，专为虚拟制作和广播级内容创作而构建。它不仅仅是一个插件，而是由超过40个模块组成的完整生态系统。其核心目标是让用户能够在虚幻引擎中直接创建、设计和驱动复杂的动态视觉效果，包括但不限于广播包装、虚拟演唱会背景、LED墙内容以及交互式视觉元素。

它解决了传统工作流中需要将静态内容在第三方软件中设计再导入引擎的痛点，提供了一个集成的、实时的设计与播放环境。从模块划分来看，它涵盖了从核心几何体（`AvalancheShapes`）、文本（`AvalancheText`）、材质（`AvalancheMaterial`）的创建，到动态效果器（`AvalancheEffectors`）、克隆器、蒙版（`AvalancheMask`）、属性动画（`AvalanchePropertyAnimator`）、过渡效果（`AvalancheTransition`）的完整设计链条，并提供了专门的场景管理（`AvalancheSceneTree`）、远程控制（`AvalancheRemoteControl`）和播出控制（`AvalancheMedia`）功能。

## 使用场景

- **电视/直播图形包装**：设计实时的下三分之一字幕、全屏动画、转场效果和虚拟广告牌。
- **虚拟演唱会/活动**：创建并驱动舞台背景、灯光视觉效果和实时交互内容。
- **虚拟制作 (ICVFX)**：为LED墙或体积捕捉制作动态背景、环境元素和交互式视觉反馈。
- **交互式装置与展览**：利用其远程控制和属性动画能力，创建由传感器或用户输入驱动的动态视觉作品。
- **产品可视化动态演示**：为产品发布或展示制作富有动感的动画和过渡效果。

## 蓝图用法

由于Avalanche是一个庞大的系统，其蓝图API分布在众多模块中。核心的设计和控制逻辑通常封装在Runtime模块，而编辑器定制功能则位于Editor模块。

### 核心节点（示例）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CustomizeAttributes` | 用于在详细信息面板中定制Ava属性的显示与编辑方式（编辑器专用） | `IAvaAttributeEditorModule` |

*（注意：要获取完整的、用于创建和操控形状、效果器、材质等的蓝图节点，需要深入研究如 `AvalancheShapes`、`AvalancheEffectors`、`AvalancheMaterial` 等具体子模块的公共头文件。）*

### 使用示例（蓝图描述）

假设要通过蓝图动态创建一个文本来显示分数：
1.  拖拽一个 `AvalancheText` 组件到Actor上。
2.  在蓝图中，通过该组件的引用，找到其文本内容属性（如 `SetText`），将其连接到一个变量节点。
3.  使用 `SetWorldLocation` 等节点控制其位置。
4.  （更高级）通过 `AvalanchePropertyAnimator` 模块，可以为其属性（如位置、颜色）添加基于时间轴或触发器的动画。

## C++ 用法

C++ API 主要面向需要深度扩展或集成Motion Design功能的开发者，例如创建新的自定义属性类型、构建新的编辑器工具或实现自动化流程。

### 头文件引入

```cpp
// 引入核心属性编辑器模块接口
#include "IAvaAttributeEditorModule.h"
```

### 基本用法

来自 `IAvaAttributeEditorModule` 的用法示例，用于在编辑器中自定义属性展示。

```cpp
// 检查模块是否已加载
if (IAvaAttributeEditorModule::IsLoaded())
{
    // 获取模块实例
    IAvaAttributeEditorModule& AttributeEditorModule = IAvaAttributeEditorModule::Get();
    
    // 在某个细节面板构建时，调用此方法来自定义属性处理
    // (此调用通常在自定义细节面板类的 CustomizeDetails 方法内进行)
    TSharedRef<IPropertyHandle> AttributesHandle = ...; // 获取属性句柄
    IDetailLayoutBuilder& DetailBuilder = ...; // 获取细节构建器
    AttributeEditorModule.CustomizeAttributes(AttributesHandle, DetailBuilder);
}
```
*（来源：`Public/IAvaAttributeEditorModule.h`）*

### 进阶用法

从 `FAvaArrayItemDragDropHandler` 可以看出Avalanche在编辑器定制上的精细程度，它为自定义构建器中的数组项实现了拖拽排序功能，解决了标准Property Editor API在此场景下的限制。

```cpp
// 在自定义的IDetailCustomization或IDetailCustomizationBuilder中，
// 为数组项的行（Row）创建并设置拖拽处理器。
TSharedRef<IPropertyHandle> ArrayItemHandle = ...; // 获取数组中某一项的属性句柄
TSharedRef<SWidget> RowWidget = ...; // 该属性对应的行控件
TWeakPtr<IPropertyUtilities> PropertyUtilities = ...; // 属性工具

TSharedRef<FAvaArrayItemDragDropHandler> DragDropHandler = MakeShared<FAvaArrayItemDragDropHandler>(
    ArrayItemHandle,
    RowWidget,
    PropertyUtilities
);
// 将此处理器与行控件关联，以实现拖拽重排序
```
*（来源：`Private/DragDrop/AvaArrayItemDragDropHandler.h`）*

## Demo 示例

由于Avalanche过于庞大，这里提供一个使用其属性编辑器模块进行扩展的极简C++示例，展示如何集成一个自定义的属性编辑器。

**MyAvaAttributeCustomization.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "IAvaAttributeEditorModule.h" // 引入Avalanche属性编辑器模块接口

// 一个假设的自定义属性编辑器类
class FMyAvaAttributeCustomization
{
public:
    // 假设我们需要对一组属性进行特殊定制
    void CustomizeMyAttributes(const TSharedRef<IPropertyHandle>& InAttributesHandle, IDetailLayoutBuilder& InDetailBuilder);
};
```

**MyAvaAttributeCustomization.cpp**
```cpp
#include "MyAvaAttributeCustomization.h"

void FMyAvaAttributeCustomization::CustomizeMyAttributes(const TSharedRef<IPropertyHandle>& InAttributesHandle, IDetailLayoutBuilder& InDetailBuilder)
{
    // 这里可以实现具体的定制化逻辑
    // 例如：添加自定义行、隐藏某些子属性、替换编辑控件等
    // 我们可以直接调用Avalanche模块提供的标准定制方法作为起点或辅助
    if (IAvaAttributeEditorModule::IsLoaded())
    {
        // 委托给Avalanche模块进行基础定制
        IAvaAttributeEditorModule::Get().CustomizeAttributes(InAttributesHandle, InDetailBuilder);
        
        // 然后在此基础上添加我们自己的额外定制...
        // InDetailBuilder.EditCategory(...).AddCustomRow(...);
    }
}
```

**使用场景（在某个细节面板自定义类中）：**
```cpp
// 在某个类的细节面板自定义代码中（例如 UMyActor 的细节面板）
void FMyActorDetails::CustomizeDetails(IDetailLayoutBuilder& DetailBuilder)
{
    // ... 获取到需要定制的属性句柄 ...
    TSharedRef<IPropertyHandle> AvaAttributesHandle = DetailBuilder.GetProperty(GET_MEMBER_NAME_CHECKED(UMyActor, AvaAttributes));
    
    FMyAvaAttributeCustomization Customization;
    Customization.CustomizeMyAttributes(AvaAttributesHandle, DetailBuilder);
}
```

## 模块依赖

Avalanche依赖于一系列Epic官方和社区提供的专门插件。要在你的项目中使用或扩展Avalanche，需要确保以下依赖项可用（根据`Description`字段）：

| 模块 | 用途 |
|---|---|
| `AdvancedRenamer` | 提供高级批量重命名功能 |
| `CustomDetailsView` | 支持在详细信息面板中进行更深度的自定义 |
| `DynamicMaterial` | 用于创建和管理动态材质实例 |
| `GeometryCache` | 处理和播放几何体缓存动画 |
| `GeometryScripting` | 提供基于脚本的几何体操作工具 |
| `MediaCompositing` | 处理媒体合成与播放 |
| `MediaIOFramework` | 提供媒体输入输出的框架支持 |
| `MeshModelingToolsetExp` | 实验性网格建模工具集 |
| `RemoteControl` | 实现远程控制接口 |
| `SVGImporter` | 导入SVG矢量图形 |
| `Text3D` | 创建和渲染3D文本 |
| `ActorModifierCore` | Actor修改器核心系统 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own group | 将运动设计的场景设置和大纲视图标签页移至关卡编辑器中的独立分组，优化界面布局。 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 当使用节目单页面设置时，添加了MRQ（Movie Render Queue）的分析数据记录功能。 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 为节目控制工具栏添加了页面加载选项（全部、下一个、已选），并新增了相关功能。 |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 新增项目设置，可以强制禁用3D文本和形状的碰撞检测。 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口改进：通过在客户端关联或断开关联时发送通知，重构了必要的重复代码。 |

### 维护评价

**活跃维护中**。
- **创建时间**：2025年5月，这是一个相对较新的插件套件（约1年历史）。
- **更新频率**：近期（2026年5月）仍有密集的功能更新和优化，涉及UI布局、数据分析、工作流改进和性能设置。
- **活跃度**：从提交历史看，Epic团队正在持续投入开发，将其作为虚拟制作和广播工具链的核心组成部分。
- **状态**：从Experimental迁移到VirtualProduction目录，标志着其从实验阶段进入正式支持阶段。目前没有发现废弃标记。
- **推荐度**：**强烈推荐**。对于从事虚拟制作、实时广播图形和高级运动设计工作的团队和个人，这是一个功能全面、官方支持且持续更新的顶级工具集。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [官方文档]() (待补充，通常会在Epic官方文档站发布)
- [测试用例]() (待补充，通常位于 `Engine/Tests/Plugins/` 相应目录下)