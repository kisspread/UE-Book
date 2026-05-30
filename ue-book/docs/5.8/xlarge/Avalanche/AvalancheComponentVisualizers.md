# Motion Design

> Compositing, designer and broadcasting tool.
> Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源等） |
| 模块 | `Avalanche` (Runtime), `AvalancheAttribute` (Runtime), `AvalancheAttributeEditor` (Runtime), `AvalancheCamera` (Runtime), `AvalancheComponentVisualizers` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), `AvalancheEditorCore` (Runtime), `AvalancheEffectors` (Runtime), `AvalancheEffectorsEditor` (Runtime), `AvalancheFunctionalTest` (Runtime), `AvalancheInteractiveTools` (Runtime), `AvalancheInteractiveToolsRuntime` (Runtime), `AvalancheLevelViewport` (Runtime), `AvalancheMRQ` (Runtime), `AvalancheMRQEditor` (Runtime), `AvalancheMask` (Runtime), `AvalancheMaskEditor` (Runtime), `AvalancheMaterial` (Runtime), `AvalancheMedia` (Runtime), `AvalancheMediaEditor` (Runtime), `AvalancheModifiers` (Runtime), `AvalancheModifiersEditor` (Runtime), `AvalancheOutliner` (Runtime), `AvalanchePropertyAnimator` (Runtime), `AvalanchePropertyAnimatorEditor` (Runtime), `AvalancheRemoteControl` (Runtime), `AvalancheRemoteControlEditor` (Runtime), `AvalancheSVGEditor` (Runtime), `AvalancheSceneRig` (Runtime), `AvalancheSceneRigEditor` (Runtime), `AvalancheSceneTree` (Runtime), `AvalancheSequence` (Runtime), `AvalancheSequencer` (Runtime), `AvalancheShapes` (Runtime), `AvalancheShapesEditor` (Runtime), `AvalancheTag` (Runtime), `AvalancheTagEditor` (Runtime), `AvalancheText` (Runtime), `AvalancheTextEditor` (Runtime), `AvalancheTransition` (Runtime), `AvalancheTransitionEditor` (Runtime), `AvalancheViewport` (Runtime) |
| 实验性 | ⚦ 是 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Motion Design（原Avalanche）插件是虚幻引擎中一个综合性的虚拟制作与广播设计工具集。它不仅仅是一个简单的工具，而是一个完整的生态系统，旨在支持从创意设计到最终播出的整个流程。其核心解决的问题是：为设计师和广播工程师提供一套在引擎内进行**实时合成、动态图形设计、场景编排和播出控制**的强大工具，替代传统需要在多个专业软件间切换的工作流。

该插件由众多子模块构成，覆盖了以下关键领域：
- **场景构建与编排**：如形状（AvalancheShapes）、文本3D（AvalancheText）、几何体缓存、场景树（AvalancheSceneTree）和场景装备（AvalancheSceneRig）。
- **视觉效果与动画**：包括材质设计器（AvalancheMaterial）、克隆器与效果器（AvalancheEffectors）、属性动画（AvalanchePropertyAnimator）、过渡效果（AvalancheTransition）和蒙版（AvalancheMask）。
- **媒体与合成**：集成媒体播放（AvalancheMedia）、远程控制（AvalancheRemoteControl）以及电影渲染管线（AvalancheMRQ）支持，用于高质量的离线渲染和合成输出。
- **编辑器与交互**：提供专用的视口（AvalancheViewport）、大纲视图（AvalancheOutliner）、组件可视化系统（AvalancheComponentVisualizers）和一系列交互式工具（AvalancheInteractiveTools），以优化设计体验。
- **播出与同步**：包含场景同步（StormSync）、序列器集成（AvalancheSequencer）以及用于虚拟制作的Rundown页管理功能。

简单来说，Motion Design让你可以在虚幻引擎内部完成传统上需要After Effects、Cinema 4D和专业播出软件才能完成的工作。

## 使用场景

- **虚拟演播室/广播包装**：实时设计和播出新闻模板、体育比分板、选举地图等动态图形，所有元素都可以在引擎内实时修改和驱动。
- **舞台活动与演唱会视觉**：创建实时响应的舞台视觉效果、LED墙内容，并与灯光、音频系统同步。
- **商业广告与产品可视化**：快速迭代产品展示动画和场景，并利用MRQ输出电影级质量的最终渲染。
- **交互式装置与体验**：构建对用户输入或外部数据做出实时反应的动态视觉装置。
- **元宇宙场景构建**：高效搭建和装饰复杂的3D场景，管理大量资产。

## 蓝图用法

Motion Design的核心功能主要通过其丰富的编辑器工具和资产系统暴露，直接暴露给蓝图的`UFUNCTION(BlueprintCallable)`较少。其核心价值在于扩展编辑器工作流，而非提供运行时蓝图节点。

### 核心节点

大部分功能通过专用资产类型（如 `UAvaSequence`）和编辑器中的自定义面板、工具栏访问。对于希望扩展或集成Motion Design的开发者，重点在于C++层面。

## C++ 用法

Motion Design的设计高度模块化，为开发者提供了强大的扩展接口，尤其是通过组件可视化系统（AvalancheComponentVisualizers）和自定义资产类型。

### 头文件引入

```cpp
#include "AvalancheComponentVisualizers/Public/IAvalancheComponentVisualizersModule.h"
#include "AvalancheComponentVisualizers/Public/AvaVisBase.h"
```

### 基本用法：注册自定义组件可视化器

要让你的组件在Motion Design视口中获得独特的交互式控件，需要子类化 `FAvaVisualizerBase` 并注册。

```cpp
// MyComponentVisualizer.h
#pragma once
#include "AvaVisBase.h"

class FMyComponentVisualizer : public FAvaVisualizerBase
{
public:
    // 实现绘制可视化，例如绘制自定义手柄、图标
    virtual void DrawVisualization(const UActorComponent* InComponent, const FSceneView* InView, FPrimitiveDrawInterface* InPDI) override;

    // 定义哪些属性可以通过该可视化器进行交互式编辑
    virtual TMap<UObject*, TArray<FProperty*>> GatherEditableProperties(UObject* InObject) const override;

    // 处理来自视口小部件的输入
    virtual bool HandleInputDeltaInternal(FEditorViewportClient* InViewportClient, FViewport* InViewport,
        const FVector& InAccumulatedTranslation, const FRotator& InAccumulatedRotation, const FVector& InAccumulatedScale) override;
};
```

```cpp
// MyComponentVisualizer.cpp
#include "MyComponentVisualizer.h"
#include "MyComponent.h"

void FMyComponentVisualizer::DrawVisualization(const UActorComponent* InComponent, const FSceneView* InView, FPrimitiveDrawInterface* InPDI)
{
    // 调用基类绘制（图标等）
    FAvaVisualizerBase::DrawVisualization(InComponent, InView, InPDI);

    // 添加你自己的绘制代码，例如：
    const UMyComponent* MyComp = Cast<const UMyComponent>(InComponent);
    if (MyComp)
    {
        // 在组件位置绘制一个球体
        InPDI->DrawPoint(MyComp->GetComponentLocation(), FLinearColor::Red, 10.f, SDPG_Foreground);
    }
}

// 在模块启动时注册
// 通常在你的 Editor 模块的 StartupModule 中
void FMyEditorModule::StartupModule()
{
    IAvalancheComponentVisualizersModule::RegisterComponentVisualizer<UMyComponent, FMyComponentVisualizer>();
}
```

### 进阶用法：处理交互与事务

`FAvaVisualizerBase` 封装了完整的交互逻辑（选择、拖拽、撤销/重做）。你需要重写 `GatherEditableProperties` 来告诉系统哪些属性是可编辑的，并重写 `HandleInputDeltaInternal` 来响应用户拖拽。

```cpp
TMap<UObject*, TArray<FProperty*>> FMyComponentVisualizer::GatherEditableProperties(UObject* InObject) const
{
    TMap<UObject*, TArray<FProperty*>> Properties;
    if (UMyComponent* Comp = Cast<UMyComponent>(InObject))
    {
        // 指定 MyComponent 的 Rotation 和 Scale 属性可通过此可视化器交互编辑
        Properties.Add(Comp, {FMyComponent::StaticStruct()->FindPropertyByName(GET_MEMBER_NAME_CHECKED(UMyComponent, Rotation)),
                             FMyComponent::StaticStruct()->FindPropertyByName(GET_MEMBER_NAME_CHECKED(UMyComponent, Scale))});
    }
    return Properties;
}

bool FMyComponentVisualizer::HandleInputDeltaInternal(FEditorViewportClient* InViewportClient, FViewport* InViewport,
    const FVector& InAccumulatedTranslation, const FRotator& InAccumulatedRotation, const FVector& InAccumulatedScale)
{
    UMyComponent* MyComp = const_cast<UMyComponent*>(Cast<const UMyComponent>(GetEditedComponent()));
    if (!MyComp)
    {
        return false;
    }

    // 使用基类提供的 ModifyProperty 进行安全的属性修改（包含撤销/重做）
    // 修改旋转
    ModifyProperty(MyComp, FMyComponent::StaticStruct()->FindPropertyByName(GET_MEMBER_NAME_CHECKED(UMyComponent, Rotation)),
        EPropertyChangeType::ValueSet,
        [&]()
        {
            MyComp->Rotation = /* 根据InAccumulatedRotation计算新值 */;
        });
    return true;
}
```

## Demo 示例

以下是一个最小化的组件可视化器实现示例。

**AvaMyComponent.h**
```cpp
#pragma once
#include "Components/ActorComponent.h"
#include "AvaMyComponent.generated.h"

UCLASS(ClassGroup=(MotionDesign), meta=(BlueprintSpawnableComponent))
class UAvaMyComponent : public UActorComponent
{
    GENERATED_BODY()
public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Motion Design")
    FVector MyOffset = FVector::ZeroVector;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Motion Design")
    float MyRadius = 50.f;
};
```

**AvaMyComponentVisualizer.h**
```cpp
#pragma once
#include "AvalancheComponentVisualizers/Public/AvaVisBase.h"

class FAvaMyComponentVisualizer : public FAvaVisualizerBase
{
public:
    virtual void DrawVisualizationNotEditing(const UActorComponent* InComponent, const FSceneView* InView,
        FPrimitiveDrawInterface* InPDI, int32& InOutIconIndex) override;

    virtual TMap<UObject*, TArray<FProperty*>> GatherEditableProperties(UObject* InObject) const override;
};
```

**AvaMyComponentVisualizer.cpp**
```cpp
#include "AvaMyComponentVisualizer.h"
#include "AvaMyComponent.h"

void FAvaMyComponentVisualizer::DrawVisualizationNotEditing(const UActorComponent* InComponent, const FSceneView* InView,
    FPrimitiveDrawInterface* InPDI, int32& InOutIconIndex)
{
    // 基类处理图标绘制等，先调用它
    FAvaVisualizerBase::DrawVisualizationNotEditing(InComponent, InView, InPDI, InOutIconIndex);

    if (const UAvaMyComponent* MyComp = Cast<const UAvaMyComponent>(InComponent))
    {
        const FTransform CompTransform = MyComp->GetComponentTransform();
        const FVector WorldOffset = CompTransform.TransformVector(MyComp->MyOffset);

        // 在组件位置 + 偏移处绘制一个线框球体
        const FMatrix SphereMatrix = FTranslationMatrix(CompTransform.GetLocation() + WorldOffset);
        DrawWireSphere(InPDI, SphereMatrix, FLinearColor::Cyan, MyComp->MyRadius, 24, SDPG_Foreground);
    }
}

TMap<UObject*, TArray<FProperty*>> FAvaMyComponentVisualizer::GatherEditableProperties(UObject* InObject) const
{
    TMap<UObject*, TArray<FProperty*>> Props;
    if (UAvaMyComponent* Comp = Cast<UAvaMyComponent>(InObject))
    {
        // 允许交互式编辑 MyOffset 属性
        Props.Add(Comp, {UAvaMyComponent::StaticClass()->FindPropertyByName(GET_MEMBER_NAME_CHECKED(UAvaMyComponent, MyOffset))});
    }
    return Props;
}
```

## 模块依赖

Avalanche插件内部模块高度耦合，且依赖众多其他插件。使用 `AvalancheComponentVisualizers` 模块，你的 `Build.cs` 通常需要添加：

| 模块 | 用途 |
|---|---|
| `AvalancheComponentVisualizers` | 本模块，提供可视化器框架和注册接口 |
| `AvalancheCore` | Motion Design 核心框架和基础类 |
| `AvalancheEditorCore` | 编辑器专用核心功能 |
| `InteractiveToolsFramework` | 提供交互式工具的基础框架 |

此外，根据你要扩展的组件类型，可能还需要依赖 `AvalancheShapes`, `AvalancheText`, `AvalancheMedia` 等具体功能模块。完整的依赖关系极其庞大，请参考 `.uplugin` 中的 `PluginDependencies` 列表。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将Motion Design的“场景设置”和“大纲”标签页移至其独立分组，优化了编辑器布局。 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 为使用“节目单页”设置时的MRQ（电影渲染队列）功能添加了使用分析。 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 在演出控制工具栏中增加了页面加载选项（全部、下一个、选定）等新功能。 |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 增加了项目设置，可以强制禁用Text3D和形状的碰撞，简化布局设计。 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构了视口客户端关联逻辑，减少了重复代码。 |

### 维护评价

- **活跃维护**：该插件在近期（2026年5月）仍有频繁且功能性的更新，包括UI优化、新功能添加和代码重构。
- **发展阶段**：插件于2025年5月从实验性（Experimental）文件夹迁移至正式的虚拟生产（VirtualProduction）文件夹，标志着其从“实验性”阶段进入“正式支持”阶段，但仍在快速迭代。
- **已知复杂性**：这是一个极其庞大和复杂的插件，拥有43个子模块和深厚的依赖关系。学习曲线陡峭，适合有明确广播或虚拟制作需求的专业团队。
- **推荐使用**：**推荐**。对于虚幻引擎的虚拟制作、广播和动态图形领域，Motion Design是Epic官方提供的核心解决方案，功能全面且与引擎深度集成。尽管复杂，但它是解决相关问题的正确工具。开发者应优先使用其提供的工具和框架，而不是自行造轮子。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/animation-design-tools-in-unreal-engine/) (Motion Design概述)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheFunctionalTest)