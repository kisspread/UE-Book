# Motion Design

> Compositing, designer and broadcasting tool. Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（核心运行时模块、编辑器扩展、资产管线、特效、媒体集成等） |
| 模块 | `Avalanche` (Runtime), `AvalancheAttribute` (Runtime), `AvalancheAttributeEditor` (Runtime), `AvalancheCamera` (Runtime), `AvalancheComponentVisualizers` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), `AvalancheEditorCore` (Runtime), `AvalancheEffectors` (Runtime), `AvalancheEffectorsEditor` (Runtime), `AvalancheFunctionalTest` (Runtime), `AvalancheInteractiveTools` (Runtime), `AvalancheInteractiveToolsRuntime` (Runtime), `AvalancheLevelViewport` (Runtime), `AvalancheMRQ` (Runtime), `AvalancheMRQEditor` (Runtime), `AvalancheMask` (Runtime), `AvalancheMaskEditor` (Runtime), `AvalancheMaterial` (Runtime), `AvalancheMedia` (Runtime), `AvalancheMediaEditor` (Runtime), `AvalancheModifiers` (Runtime), `AvalancheModifiersEditor` (Runtime), `AvalancheOutliner` (Runtime), `AvalanchePropertyAnimator` (Runtime), `AvalanchePropertyAnimatorEditor` (Runtime), `AvalancheRemoteControl` (Runtime), `AvalancheRemoteControlEditor` (Runtime), `AvalancheSVGEditor` (Runtime), `AvalancheSceneRig` (Runtime), `AvalancheSceneRigEditor` (Runtime), `AvalancheSceneTree` (Runtime), `AvalancheSequence` (Runtime), `AvalancheSequencer` (Runtime), `AvalancheShapes` (Runtime), `AvalancheShapesEditor` (Runtime), `AvalancheTag` (Runtime), `AvalancheTagEditor` (Runtime), `AvalancheText` (Runtime), `AvalancheTextEditor` (Runtime), `AvalancheTransition` (Runtime), `AvalancheTransitionEditor` (Runtime), `AvalancheViewport` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Motion Design（Avalanche）是一个专为虚拟制作（Virtual Production）和广播（Broadcast）场景打造的综合动态图形（Motion Graphics）设计与合成工具集。它解决的核心问题是：在Unreal Engine内提供一个专业、高效的工作流，用于创建、编辑和播放实时的动态图形内容，例如广播新闻的标题、体育赛事的数据图表、舞台演出的视觉效果等。与传统的离线渲染工作流不同，它强调实时合成、交互式设计以及与媒体输入/输出框架的深度集成，旨在成为虚拟演播室、XR舞台和实时广播流水线的核心视觉内容创作工具。

## 使用场景

-   你需要在虚拟演播室中，为新闻主播身后实时生成并更新数据驱动的图表和标题 → 使用Motion Design的文本、形状和数据驱动功能。
-   你需要为一场大型体育赛事制作实时比分牌、选手信息板和动态过渡效果 → 使用Motion Design的合成、场景树和过渡系统。
-   你需要为一场演唱会或发布会的XR舞台设计复杂的粒子效果、几何体动画和灯光交互 → 使用Motion Design的效果器（Effectors）、修改器（Modifiers）和属性动画器（Property Animator）。
-   你需要将外部视频源（如NDI、SDI）与Unreal场景中的3D元素进行实时抠像和合成 → 使用Motion Design的媒体合成（Media Compositing）和掩码（Mask）功能。
-   你需要远程控制屏幕上的图形内容，例如切换场景、更新文本 → 使用Motion Design的远程控制（Remote Control）模块。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetTag` | 设置单个标签句柄 | `UAvaTagAttribute` |
| `SetTagContainer` | 设置包含多个标签的容器 | `UAvaTagContainerAttribute` |
| `ContainsTag` | 检查属性是否包含指定的标签句柄 | `UAvaTagAttributeBase` |
| `HasValidTagHandle` | 检查属性是否拥有有效的标签句柄 | `UAvaTagAttributeBase` |
| `SetName` | 设置名称属性 | `UAvaNameAttribute` |

### 使用示例（蓝图描述）

1.  **创建一个带有标签的属性**：在任意支持`EditInlineNew`的Actor组件上，添加一个`AvaTagAttribute`类型的属性。在蓝图中，使用`SetTag`节点将其设置为某个具体的标签（FAvaTagHandle）。
2.  **基于标签进行查询或筛选**：在需要根据标签处理对象的地方，调用`ContainsTag`节点，传入要检查的标签句柄，即可判断该对象是否拥有此标签，用于实现如“影响所有带‘Hero’标签的对象”等逻辑。
3.  **管理复杂的对象分类**：对于一个对象需要拥有多个标签的情况，使用`AvaTagContainerAttribute`，并通过`SetTagContainer`一次性设置一个标签容器，方便进行批量查询和管理。

## C++ 用法

### 头文件引入

```cpp
#include "AvaAttribute.h"
#include "Tags/AvaTagAttribute.h"
#include "Tags/AvaTagContainerAttribute.h"
#include "AvaNameAttribute.h"
```

### 基本用法

Motion Design的属性系统（AvaAttribute）为Actor或组件提供了一种灵活的、可编辑内联的方式来附加描述性数据。其核心是`UAvaAttribute`基类。

```cpp
// 来源：Public/AvaAttribute.h
// 1. 定义一个自定义属性类
UCLASS(MinimalAPI, EditInlineNew, DisplayName = “My Custom Attribute”)
class UMyCustomAttribute : public UAvaAttribute
{
    GENERATED_BODY()
public:
    UPROPERTY(EditAnywhere, Category = “Attributes”)
    int32 CustomValue;

    virtual FText GetDisplayName() const override { return NSLOCTEXT(“MyAttr”, “DisplayName”, “My Custom”); }
};
```

### 进阶用法

利用标签属性系统为对象建立可查询的元数据网络。这常用于实现解耦的交互和影响系统。

```cpp
// 来源：Public/Tags/AvaTagAttributeBase.h 及其子类
// 1. 从某个对象（例如一个SceneComponent）上获取标签属性
UAvaTagAttribute* TagAttr = MyComponent->FindAttribute<UAvaTagAttribute>();
if (TagAttr)
{
    // 2. 添加一个标签
    FAvaTagHandle MyTagHandle = UMyTagDefinition::GetTagHandle(); // 通过某种方式获取标签句柄
    TagAttr->SetTagHandle(MyTagHandle);
}

// 3. 在另一个地方查询标签
if (TagAttr && TagAttr->ContainsTag(MyTagHandle))
{
    // 执行与该标签相关联的逻辑，例如应用一个特效或修改材质
}
```

## Demo 示例

下面是一个在自定义Actor组件上使用Motion Design属性系统的最小示例。

```cpp
// MyDesignableComponent.h
#pragma once

#include "Components/ActorComponent.h"
#include "MyDesignableComponent.generated.h"

class UAvaNameAttribute;
class UAvaTagAttribute;

UCLASS(ClassGroup=(MotionDesign), meta=(BlueprintSpawnableComponent))
class UMyDesignableComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UMyDesignableComponent();

    // 在编辑器中可内联编辑的属性
    UPROPERTY(Instanced, EditAnywhere, Category = “Design”)
    TObjectPtr<UAvaNameAttribute> DisplayNameAttr;

    UPROPERTY(Instanced, EditAnywhere, Category = “Design”)
    TObjectPtr<UAvaTagAttribute> EffectTagAttr;

    UFUNCTION(BlueprintCallable, Category = “Design”)
    void ApplyDesignToActor(AActor* TargetActor);
};
```

```cpp
// MyDesignableComponent.cpp
#include “MyDesignableComponent.h”
#include “AvaNameAttribute.h”
#include “Tags/AvaTagAttribute.h”

UMyDesignableComponent::UMyDesignableComponent()
{
    // 构造并实例化子对象，使其出现在属性面板中可编辑
    DisplayNameAttr = CreateDefaultSubobject<UAvaNameAttribute>(TEXT(“DisplayName”));
    EffectTagAttr = CreateDefaultSubobject<UAvaTagAttribute>(TEXT(“EffectTag”));
}

void UMyDesignableComponent::ApplyDesignToActor(AActor* TargetActor)
{
    if (!TargetActor || !EffectTagAttr || !DisplayNameAttr) return;

    // 1. 设置目标Actor的显示名称（伪代码）
    // TargetActor->SetActorLabel(DisplayNameAttr->Name.ToString());

    // 2. 将设计时指定的标签“复制”或“附加”给目标Actor上的某个可接收标签的组件（伪代码）
    // 例如，找到目标Actor上一个负责视觉效果的组件，并设置其标签
    /*
    if (UAvaTagAttribute* TargetEffectTag = TargetActor->FindComponent<UEffectComponent>()->FindAttribute<UAvaTagAttribute>())
    {
        TargetEffectTag->SetTag(EffectTagAttr->Tag);
    }
    */
    UE_LOG(LogTemp, Log, TEXT(“Applying design [%s] with tag [%s] to [%s]“),
        *DisplayNameAttr->Name.ToString(),
        *EffectTagAttr->Tag.ToString(),
        *TargetActor->GetName());
}
```

## 模块依赖

从当前模块 `AvalancheAttribute` 的 `Build.cs` 及整体插件结构分析：

| 模块 | 用途 |
|---|---|
| `AvalancheCore` | 提供Motion Design框架的核心基类、接口和实用程序 |
| `Sequencer` | 与虚幻引擎的序列器（Sequencer）深度集成，用于动画编辑和回放 |

**注意**：整个Motion Design插件还有大量其他依赖（如MediaIO, RemoteControl等），使用相应功能时需在 `Build.cs` 中添加对应模块依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 优化编辑器布局，将场景设置和大纲等面板整理到专用分组中 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 增强MRQ渲染分析功能，新增针对节目单页面的使用数据追踪 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 丰富节目控制工具栏，新增页面加载（全部、下一个、选中）等选项 |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 增加项目级设置，允许全局强制禁用Text3D和形状的碰撞检测 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构视口通信机制，明确客户端关联/解除关联的事件通知 |

### 维护评价

Motion Design（Avalanche）插件处于**非常活跃的维护和功能开发阶段**。自2025年5月从实验区迁移到正式插件目录以来，始终保持高频更新（截至2026年5月，最近一次更新在几天内）。更新内容主要集中在功能增强（如MRQ分析、节目控制工具）、编辑器体验优化（如面板整理）和稳定性/项目设置改进。作为Epic Games官方推出的虚拟制作核心工具链之一，其开发优先级高，稳定性有保障。该插件功能极其庞大且复杂，适合在需要专业、实时动态图形设计与合成的虚拟制作项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [官方文档](https://docs.unrealengine.com/en-US/InteractiveExperiences/AvalancheMotionDesign/) (占位符，需查找实际官方文档链接)