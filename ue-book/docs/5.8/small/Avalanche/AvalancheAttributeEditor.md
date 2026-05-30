# Motion Design

> Compositing, designer and broadcasting tool.
> 
> Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AvalancheCore` (Runtime), `AvalancheAttribute` (Runtime), `AvalancheEditor` (Runtime), `AvalancheMedia` (Runtime), `AvalancheText` (Runtime) ... 及其他共42个子模块 |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Avalanche (Motion Design) 是一套面向虚拟制作 (Virtual Production) 的综合性实时动态图形设计、合成与播放工具套件。它并非一个简单的单一功能插件，而是一个庞大的生态系统，旨在解决虚拟制作流程中对于实时、可编程、数据驱动的动态图形（Motion Graphics）的需求。

它解决了以下核心问题：
1.  **实时设计与合成**：允许设计师在编辑器或运行时，像使用 After Effects 一样创建、编排和预览复杂的 2D/3D 动态图形层（文本、形状、图片、视频），并进行实时合成。
2.  **数据驱动与自动化**：通过属性系统、修改器、效果器和远程控制，实现图形内容的程序化生成和实时数据绑定（如体育比分、天气、股票），适应直播和现场制作的快速变化需求。
3.  **工作流整合**：与虚幻引擎的 Sequencer（序列器）、材质系统、媒体框架（Media IO）深度集成，提供从设计、编排到最终渲染输出（通过 Movie Render Queue）的完整管线。

## 使用场景

-   **电视节目/直播制作**：为新闻、体育赛事、演唱会直播设计和播放实时更新的动态字幕、比分板、统计图表和节目包装。
-   **虚拟演播室**：为虚拟新闻播报、访谈节目创建动态的虚拟背景、下三分之一栏（Lower Thirds）和视觉特效。
-   **大型活动与投影映射**：为舞台演出、主题公园、建筑投影设计和控制复杂的动态视觉内容。
-   **交互式数据可视化**：创建实时响应外部数据（如IoT传感器、数据库）的仪表盘和信息图表。
-   **游戏内UI/特效原型**：快速原型设计和实现复杂的、可编排的游戏内UI动画或场景特效。

## 蓝图用法

Motion Design 的蓝图节点主要集中在运行时模块（如 `AvalancheCore`, `AvalancheAttribute`, `AvalancheModifiers`），用于在运行时动态操控设计元素。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Attribute Value` | 设置对象上动态属性的值，是数据驱动设计的核心 | `UAvaAttribute` 及其子类 |
| `Apply Modifier` | 在运行时对目标对象应用一个动态修改器（如旋转、缩放） | `UAvaModifier` |
| `Add Effector` | 为对象添加一个效果器，影响其周围元素（如排斥、吸引） | `UAvaEffector` |
| `Set Visibility` | 控制动态设计元素（如文本、形状）的显示/隐藏 | `AAvaPlayable` |
| `Trigger Transition` | 触发一个已定义的过渡动画（如淡入淡出） | `UAvaTransition` |

### 使用示例（蓝图描述）

1.  **创建一个简单的动态文本**：
    - 使用 `Spawn Actor from Class` 节点生成一个 `AAvaText3D` Actor。
    - 使用 `Set Attribute Value` 节点，连接到该 Actor，属性名选择 `Text`，设置要显示的字符串。
    - 使用 `Set Attribute Value` 节点，修改 `Color` 属性来改变文字颜色。

2.  **实时更新比分**：
    - 假设有一个 `AAvaText3D` Actor 用于显示分数。
    - 在接收到新比分数据的蓝图事件中，使用 `Set Attribute Value` 节点将新分数字符串传递给该 Actor 的 `Text` 属性，实现实时更新。

## C++ 用法

### 头文件引入

```cpp
// 引入核心模块
#include "AvalancheCore.h"
// 引入属性系统
#include "AvalancheAttribute.h"
// 若需要在编辑器中自定义属性面板，引入编辑器模块接口
#include "IAvaAttributeEditorModule.h"
```

### 基本用法

以下示例展示如何在 C++ 中为对象设置一个 Avalanche 属性。
（*注意：设置属性通常通过 `AvaAttribute` 子类实例化并调用方法，或在蓝图中更便捷*）

```cpp
// 假设你有一个拥有 UAvaAttribute* 属性的 UObject
UObject* TargetObject = ...; // 你的目标对象
FName AttributeName = TEXT("Color");

// 方法1：通过属性系统查找并设置值 (概念性代码)
// 在实际使用中，更多是通过蓝图或属性面板操作
if (UAvaAttribute* FoundAttribute = UAvaAttribute::FindAttribute(TargetObject, AttributeName))
{
    // 根据属性类型设置值，例如一个颜色属性
    // FoundAttribute->SetValueFromString(TEXT("(R=1.0, G=0.0, B=0.0, A=1.0)"));
}

// 方法2：直接获取和修改属性组件（如果设计如此）
// 具体接口取决于对象的实现方式。
```

*来源：基于 `UAvaAttribute` 类和 `AvalancheAttribute` 模块的通用接口设计推断。*

### 进阶用法：自定义属性编辑器界面

这是 `AvalancheAttributeEditor` 模块的核心功能。你可以通过实现 `IAvaAttributeEditorModule` 接口来自定义特定 `UAvaAttribute` 子类在细节面板中的显示方式。

```cpp
// 1. 在你的编辑器模块中，实现自定义细节面板自定义。
// 通常通过 IDetailCustomization 或 IPropertyTypeCustomization 完成。

// 2. 利用 IAvaAttributeEditorModule 提供的集中注册/自定义功能。
// 在模块 StartupModule 中，可以获取该模块接口来注册全局的自定义。
if (IAvaAttributeEditorModule::IsLoaded())
{
    IAvaAttributeEditorModule& AttributeEditorModule = IAvaAttributeEditorModule::Get();
    // AttributeEditorModule.CustomizeAttributes(...); // 通常由编辑器内部调用
}
```

*来源：`Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheAttributeEditor/Public/IAvaAttributeEditorModule.h`*

## Demo 示例

以下示例演示如何创建一个简单的自定义细节面板布局，用于展示和编辑一个属性数组。这是 `AvalancheAttributeEditor` 模块 `FAvaAttributeNodeBuilder` 的典型应用场景。

**MyAttributeCustomization.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "IDetailCustomization.h"

class IPropertyHandle;
class FMyAttributeCustomization : public IDetailCustomization
{
public:
    static TSharedRef<IDetailCustomization> MakeInstance();
    virtual void CustomizeDetails(IDetailLayoutBuilder& DetailBuilder) override;

private:
    // 用于操作属性数组的句柄
    TSharedPtr<IPropertyHandle> AttributesArrayHandle;
};
```

**MyAttributeCustomization.cpp**
```cpp
#include "MyAttributeCustomization.h"
#include "DetailLayoutBuilder.h"
#include "DetailCategoryBuilder.h"
#include "DetailWidgetRow.h"
#include "IDetailChildrenBuilder.h"
// 引入 Avalanche 的节点构建器，用于自定义数组项展示
#include "Customizations/AvaAttributeNodeBuilder.h"

TSharedRef<IDetailCustomization> FMyAttributeCustomization::MakeInstance()
{
    return MakeShareable(new FMyAttributeCustomization);
}

void FMyAttributeCustomization::CustomizeDetails(IDetailLayoutBuilder& DetailBuilder)
{
    // 获取我们想要自定义展示的数组属性
    AttributesArrayHandle = DetailBuilder.GetProperty(GET_MEMBER_NAME_CHECKED(UMyDesignObject, Attributes));

    // 为属性数组创建一个自定义分类
    IDetailCategoryBuilder& DesignCategory = DetailBuilder.EditCategory("Design Attributes");

    // 使用自定义构建器来替换默认的数组展示。
    // 这里我们使用了 Avalanche 提供的 FAvaAttributeNodeBuilder 作为示例概念。
    // 实际上，你需要根据自己的属性类型创建类似的构建器。
    DesignCategory.AddCustomBuilder(MakeShareable(new FAvaAttributeNodeBuilder(AttributesArrayHandle.ToSharedRef(), DetailBuilder.GetPropertyUtilities())));
}
```

*说明：此示例演示了如何接管一个属性数组的展示，为每个数组项使用自定义的 Header 和 Content 布局。`FAvaAttributeNodeBuilder` 来自 `AvalancheAttributeEditor` 模块，展示了该模块提供的核心自定义能力。*

## 模块依赖

使用 `Avalanche` 插件本身，你的项目模块通常无需直接依赖其子模块，因为这是通过插件系统集成的。但如果你需要**在 C++ 层面扩展或深度集成** `Avalanche` 的功能，你的模块需要依赖相应的子模块。

从 `AvalancheAttributeEditor` 模块的 `Build.cs`（推测）及插件依赖列表来看，除了标准引擎模块外，独特的依赖包括：

| 模块 | 用途 |
|---|---|
| `AvalancheCore` | 提供运动设计的核心运行时框架和基础类 |
| `AvalancheAttribute` | 动态属性系统，数据驱动设计的核心 |
| `ActorModifierCore` | Actor 修改器框架，用于程序化修改 Actor 属性 |
| `CustomDetailsView` | 提供高级细节面板自定义能力 |
| `DynamicMaterial` | 动态材质编辑器集成 |
| `Text3D` | 3D 文本生成与渲染 |
| `SVGImporter` | SVG 文件导入支持 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将 Motion Design 的场景设置和大纲窗口标签页移至编辑器独立分组，优化布局。 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 新增电影渲染队列（MRQ）分析功能，用于跟踪“节目单页面”设置的使用情况。 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 为节目控制工具栏添加了页面加载选项（全部、下一个、已选），并增加了相关UI。 |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 新增项目设置，可强制禁用 Text3D 和形状的碰撞，简化特定场景的配置。 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口代码重构：通过通知客户端关联/断开关联来优化必需的样板代码，提高清晰度。 |

### 维护评价

**综合评价：活跃维护，推荐使用**

- **活跃度**：该插件正处于密集的活跃开发期。从 git 历史看，在最近一周内有多次功能性提交，内容涉及新功能（如 MRQ 分析、页面加载选项）、UI/UX 优化（标签页分组）和项目配置增强。
- **成熟度**：虽然插件本身创建于 2025 年，但它是由成熟的 **Experimental** 插件（Motion Design 等）集体迁移而来，拥有长期的技术积累和功能完整性。
- **风险与限制**：由于功能庞大、模块众多（42个），学习和使用曲线较陡。作为虚拟制作的核心工具，其复杂性也意味着潜在的性能考量和特定的工作流要求。
- **推荐度**：**强烈推荐**给从事虚拟制作、实时图形设计、直播和动态数据可视化领域的项目。它是 Epic 官方力推的下一代实时图形解决方案，长期支持和功能扩展有保障。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- 官方文档： (待 Epic 发布正式文档，可关注 [官方虚拟制作文档](https://docs.unrealengine.com/5.8/en-US/virtual-production-in-unreal-engine/))
- 测试用例：该插件的测试通常集成在 `Engine/Tests/` 目录下或各子模块内，路径复杂，建议直接通过引擎自动化测试框架搜索 `Avalanche` 相关测试。