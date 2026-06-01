# Motion Design

> Compositing, designer and broadcasting tool. Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 运动设计 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `Avalanche` (Runtime), `AvalancheAttribute` (Runtime), `AvalancheAttributeEditor` (Runtime), `AvalancheCamera` (Runtime), `AvalancheComponentVisualizers` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), `AvalancheEditorCore` (Runtime), `AvalancheEffectors` (Runtime), `AvalancheEffectorsEditor` (Runtime), `AvalancheFunctionalTest` (Runtime), `AvalancheInteractiveTools` (Runtime), `AvalancheInteractiveToolsRuntime` (Runtime), `AvalancheLevelViewport` (Runtime), `AvalancheMRQ` (Runtime), `AvalancheMRQEditor` (Runtime), `AvalancheMask` (Runtime), `AvalancheMaskEditor` (Runtime), `AvalancheMaterial` (Runtime), `AvalancheMedia` (Runtime), `AvalancheMediaEditor` (Runtime), `AvalancheModifiers` (Runtime), `AvalancheModifiersEditor` (Runtime), `AvalancheOutliner` (Runtime), `AvalanchePropertyAnimator` (Runtime), `AvalanchePropertyAnimatorEditor` (Runtime), `AvalancheRemoteControl` (Runtime), `AvalancheRemoteControlEditor` (Runtime), `AvalancheSVGEditor` (Runtime), `AvalancheSceneRig` (Runtime), `AvalancheSceneRigEditor` (Runtime), `AvalancheSceneTree` (Runtime), `AvalancheSequence` (Runtime), `AvalancheSequencer` (Runtime), `AvalancheShapes` (Runtime), `AvalancheShapesEditor` (Runtime), `AvalancheTag` (Runtime), `AvalancheTagEditor` (Runtime), `AvalancheText` (Runtime), `AvalancheTextEditor` (Runtime), `AvalancheTransition` (Runtime), `AvalancheTransitionEditor` (Runtime), `AvalancheViewport` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Avalanche (Motion Design) 是一个面向虚拟制作的综合性运动设计工具集。它并非一个单一功能的插件，而是一个庞大的插件系统，集成了合成、2D/3D图形设计、实时广播、媒体管理和自动化动画等功能。

该插件系统的核心解决的是**在UE5中高效、专业地创建实时动态图形（Motion Graphics）和广播级内容**的问题。它提供了从基础图形创建（文本、形状、SVG）、复杂场景编排（克隆/效果器）、材质动态编辑、媒体流处理、到远程控制和最终渲染输出的全链条工具，旨在让设计师和广播工程师能够在UE引擎内完成传统上需要借助After Effects等外部软件的工作，并直接用于电视广播、虚拟场景墙、现场活动等实时应用。

## 使用场景

- **电视广播和直播**：为直播节目、新闻频道、体育赛事制作实时图形、比分板、动态Logo和过渡动画。
- **虚拟布景和媒体墙**：设计和控制LED墙或虚拟演播室中播放的实时动态背景、图形元素和交互式内容。
- **活动和展览**：为现场活动、展览创建大型互动投影、沉浸式视觉效果。
- **社交媒体和在线内容**：快速制作高质量的动态缩略图、宣传片和视频片段。
- **产品可视化和广告**：创建产品展示动画、动态UI元素和品牌宣传片。

## 蓝图用法

Avalanche插件提供了大量蓝图节点，但由于其模块化结构，功能分散在不同子系统中。此处以核心的`AvalancheAttribute`模块为例，展示基于属性的蓝图用法。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Tag Handle` | 设置或添加一个标签句柄到标签属性中 | `UAvaTagAttributeBase` |
| `Clear Tag Handle` | 清除或移除一个标签句柄 | `UAvaTagAttributeBase` |
| `Contains Tag` | 检查标签属性是否包含指定句柄解析后的标签 | `UAvaTagAttributeBase` |
| `Has Valid Tag Handle` | 检查标签属性是否有任何可解析为有效标签的句柄 | `UAvaTagAttributeBase` |
| `Set Tag` | 设置单标签属性的标签句柄 | `UAvaTagAttribute` |
| `Set Tag Container` | 设置标签容器属性的句柄容器 | `UAvaTagContainerAttribute` |
| `Set Name` | 设置名称属性的值 | `UAvaNameAttribute` |

### 使用示例（蓝图描述）

要创建一个带有运动设计属性的Actor，可以在Actor的蓝图中：
1. 添加一个`AvaAttributeComponent`组件。
2. 在该组件的`Attributes`数组中，添加一个新的`UAvaTagAttribute`。
3. 在`Details`面板中，为新属性的`Tag`属性指定一个预定义的`AvaTag`资产。
4. 在事件图表中，使用`Get Attributes By Class`节点获取该`UAvaTagAttribute`实例，然后调用`Contains Tag`节点来检查某个标签是否存在，用于条件逻辑（如控制动画是否播放）。

## C++ 用法

### 头文件引入

```cpp
#include "Attribute/AvaAttribute.h"
#include "Tags/AvaTagAttribute.h"
#include "Tags/AvaTagContainerAttribute.h"
#include "AvaNameAttribute.h"
```

### 基本用法

从`AvalancheAttribute`模块的源码中，可以看到其核心是提供了一个可扩展的属性系统。

```cpp
// 创建一个自定义的运动设计属性类
// 来源: Public/AvaAttribute.h
UCLASS(BlueprintType, EditInlineNew, DefaultToInstanced)
class UMyMovementAttribute : public UAvaAttribute
{
    GENERATED_BODY()

public:
    virtual FText GetDisplayName() const override
    {
        return FText::FromString(TEXT("My Movement"));
    }

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Movement")
    FVector MovementDirection;
};
```

### 进阶用法

结合`UAvaTagAttribute`进行标签驱动的设计：

```cpp
// 假设我们有一个基于标签控制显隐的组件
void AMyMotionActor::CheckVisibilityBasedOnTag()
{
    // 从组件获取属性（假设Actor上挂载了AvaAttributeComponent）
    if (UAvaAttributeComponent* AttrComp = FindComponentByClass<UAvaAttributeComponent>())
    {
        // 获取第一个UAvaTagAttribute
        UAvaTagAttribute* TagAttr = AttrComp->GetFirstAttributeByClass<UAvaTagAttribute>();
        if (TagAttr)
        {
            // 假设我们有一个定义好的FAvaTagHandle代表“高亮”标签
            FAvaTagHandle HighlightTagHandle;
            // ... 初始化 HighlightTagHandle ...
            
            // 检查是否包含该标签
            bool bShouldHighlight = TagAttr->ContainsTag(HighlightTagHandle);
            SetActorHiddenInGame(!bShouldHighlight);
        }
    }
}
```

## Demo 示例

一个最小的自定义运动设计属性示例。

**MyColorAttribute.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Attribute/AvaAttribute.h"
#include "MyColorAttribute.generated.h"

UCLASS(BlueprintType, EditInlineNew, DefaultToInstanced, DisplayName = "Color Attribute")
class UMyColorAttribute : public UAvaAttribute
{
	GENERATED_BODY()

public:
	virtual FText GetDisplayName() const override
	{
		return FText::FromString(TEXT("My Color"));
	}

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Setter, Category = "Attributes")
	FLinearColor Color = FLinearColor::White;
};
```

**MyColorAttribute.cpp**
```cpp
#include "MyColorAttribute.h"
```

## 模块依赖

该插件的依赖非常广泛，远超出一个插件本身。对于希望使用Avalanche（Motion Design）功能的模块，其依赖项取决于具体使用的子功能。以下是从其核心构建和描述中推断出的关键依赖：

| 模块 | 用途 |
|---|---|
| `Sequencer` | 用于驱动属性动画和时间线控制 (`AvalanchePropertyAnimator` 依赖) |
| `MediaCompositing` | 处理视频源和实时媒体合成 (`AvalancheMedia` 依赖) |
| `RemoteControl` | 实现对运动设计参数的远程控制 (`AvalancheRemoteControl` 依赖) |
| `Text3D` | 提供3D文本生成能力 (`AvalancheText` 依赖) |
| `GeometryScripting` | 用于程序化生成和操作几何体 (`AvalancheShapes`, `AvalancheModifiers` 依赖) |
| `ActorModifierCore` | Actor修改器核心框架 (`AvalancheModifiers` 依赖) |
| `SVGImporter` | 导入SVG文件并转化为可编辑的几何体 (`AvalancheSVGEditor` 依赖) |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将Motion Design的场景设置和大纲视图标签页从关卡编辑器移入独立分组。 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 在使用Rundown页面设置时，新增了Movie Render Queue的分析功能。 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 为节目控制工具栏添加了页面加载选项（全部、下一个、选中项）。 |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 新增项目设置，可强制禁用Text3D和形状的碰撞。 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口：通过通知客户端关联/断开关联来重构重复代码。 |

### 维护评价

**活跃维护**。
- 该插件于2025年5月9日创建，历史不长，但从实验区迁移到正式区。
- **最近更新极为频繁**（查看的提交跨越2026年5月14日至20日），且均为功能性更新和新特性添加（如MRQ分析、页面控制、碰撞设置），表明项目正在**积极开发和迭代**。
- 代码库庞大（2060个源文件），包含43个模块，表明这是一个复杂且功能完整的生产级工具集。
- 作为Epic Games官方维护的虚拟制作工具，其稳定性和兼容性有较高保障。
- **强烈推荐**给所有需要在UE5中进行专业运动设计和实时广播内容的团队使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/motion-design-in-unreal-engine/)（通用Motion Design文档）