# Motion Design

> Compositing, designer and broadcasting tool. Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（工具和编辑器资产） |
| 模块 | `Avalanche` (Runtime), `AvalancheAttribute` (Runtime), `AvalancheAttributeEditor` (Runtime), `AvalancheCamera` (Runtime), `AvalancheComponentVisualizers` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), `AvalancheEditorCore` (Runtime), `AvalancheEffectors` (Runtime), `AvalancheEffectorsEditor` (Runtime), `AvalancheFunctionalTest` (Runtime), `AvalancheInteractiveTools` (Runtime), `AvalancheInteractiveToolsRuntime` (Runtime), `AvalancheLevelViewport` (Runtime), `AvalancheMRQ` (Runtime), `AvalancheMRQEditor` (Runtime), `AvalancheMask` (Runtime), `AvalancheMaskEditor` (Runtime), `AvalancheMaterial` (Runtime), `AvalancheMedia` (Runtime), `AvalancheMediaEditor` (Runtime), `AvalancheModifiers` (Runtime), `AvalancheModifiersEditor` (Runtime), `AvalancheOutliner` (Runtime), `AvalanchePropertyAnimator` (Runtime), `AvalanchePropertyAnimatorEditor` (Runtime), `AvalancheRemoteControl` (Runtime), `AvalancheRemoteControlEditor` (Runtime), `AvalancheSVGEditor` (Runtime), `AvalancheSceneRig` (Runtime), `AvalancheSceneRigEditor` (Runtime), `AvalancheSceneTree` (Runtime), `AvalancheSequence` (Runtime), `AvalancheSequencer` (Runtime), `AvalancheShapes` (Runtime), `AvalancheShapesEditor` (Runtime), `AvalancheTag` (Runtime), `AvalancheTagEditor` (Runtime), `AvalancheText` (Runtime), `AvalancheTextEditor` (Runtime), `AvalancheTransition` (Runtime), `AvalancheTransitionEditor` (Runtime), `AvalancheViewport` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Motion Design 是一个用于创建复杂视觉效果、动态图形和实时广播内容的综合性设计工具集。它本质上是一个**非线性设计环境**，允许设计师和艺术家在不依赖传统编程的情况下，通过拖放、参数调整和时间轴编辑来创作动态视觉效果。该插件整合了多个子系统（模块），涵盖了从2D/3D文字、形状、材质、动画、特效到媒体合成、场景控制和广播输出的完整工作流程，是虚幻引擎中用于**广播、现场活动视觉设计和虚拟制作**的核心工具。

## 使用场景

- **现场活动视觉设计**：为演唱会、颁奖典礼或体育赛事设计和实时播放动态背景、转场效果和实时图形。
- **虚拟制作**：在虚拟影棚中，快速迭代和调整虚拟场景中的动态元素（如标志、信息显示板、粒子效果）。
- **新闻与体育广播**：创建实时数据驱动的图形叠加层、比分板、选手信息等。
- **品牌推广与广告**：制作产品发布视频、社交媒体动态广告等需要复杂动态图形的商业内容。
- **交互式装置**：为博物馆、展览或零售空间设计交互式视觉体验。

## 蓝图用法

由于 Motion Design 插件规模巨大（2060+ 文件），其蓝图 API 分布在数十个模块中。以下仅列出核心设计工作流中常见的节点类别。

### 核心节点（示例）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Material Parameter` | 运行时动态设置材质参数，用于动画或交互式效果 | `UActorModifier` |
| `Apply Effect` | 应用预定义的视觉效果或滤镜 | `UAvaEffect` |
| `Start/Stop Media Playback` | 控制媒体（视频/图片序列）的播放 | `UAvaMediaSource` |
| `Trigger Scene Transition` | 触发场景之间的预设过渡动画 | `UAvaTransition` |
| `Bind to Data Source` | 将视觉元素绑定到外部数据源（如文本、数值）进行实时更新 | `UAvaDataBinding` |

> **注**：由于插件由众多子模块构成，实际使用时需根据具体功能（如文字、形状、特效）查找对应的 `UObject` 和 `AActor` 子类。设计工作流通常在编辑器中的专用面板（如 Rundown, Scene Outliner）完成，蓝图主要用于运行时控制和数据驱动。

### 使用示例（蓝图描述）

要创建一个简单的“欢迎”文字动画：
1. 在场景中放置一个 `AvaText` Actor。
2. 在“Motion Design”编辑器面板中，为其添加一个 `Appear` 效果。
3. 通过蓝图，当玩家进入触发区域时，调用该 Actor 上的 `PlayEffect` 函数。
4. 通过 `Set Actor Text` 节点动态更改显示的文字内容。

## C++ 用法

该插件的 C++ API 同样复杂且模块化。以下是与 MRQ（Movie Render Queue）集成和特效控制相关的基础用法示例。

### 头文件引入

```cpp
// 核心模块
#include "AvalancheMRQ.h"
// 如果操作特定 Actor 或组件，可能需要包含对应模块的头文件
#include "AvaText.h"
```

### 基本用法

以下示例展示了如何在 C++ 中通过 Motion Design 的 MRQ 模块渲染指定页面。此代码逻辑来源于 `AvalancheMRQEditor` 模块的工具集。

**来源文件**: `Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheMRQEditor/Private/AvaMRQEditorRundownUtils.h`

```cpp
#include "AvaMRQEditorRundownUtils.h"
#include "AvaRundownEditor.h"

// 假设你已经获取了 FAvaRundownEditor 的指针数组
TArray<TWeakPtr<const FAvaRundownEditor>> RundownEditors = /* ... */;

// 调用静态工具函数来渲染所有在 Rundown 中选中的页面
FAvaMRQEditorRundownUtils::RenderSelectedPages(RundownEditors);
```

### 进阶用法

1. **扩展 Rundown 编辑器工具栏**：你可以创建自定义的编辑器扩展，将你的按钮或菜单项添加到 Rundown 页面的工具栏上。
2. **自定义 MRQ 渲染预设**：通过 `UAvaMRQEditorSettings` 类，你可以为 Motion Design 项目指定一个默认的 Movie Pipeline 配置资产。

**来源文件**: `Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheMRQEditor/Private/AvaMRQEditorSettings.h`

```cpp
#include "AvaMRQEditorSettings.h"

// 获取或设置项目级的 MRQ 预设配置
UAvaMRQEditorSettings* Settings = GetMutableDefault<UAvaMRQEditorSettings>();
if (Settings)
{
    // 设置一个软引用指向你的 UMoviePipelinePrimaryConfig 资产
    Settings->PresetConfig = YourPresetConfigAsset;
    Settings->SaveConfig();
}
```

## Demo 示例

由于插件极其庞大且高度依赖编辑器 UI，一个独立的可编译最小 C++ 示例难以涵盖其核心功能。推荐的做法是创建一个引用了 `Avalanche` 核心运行时模块的 Actor，该 Actor 可以在场景中承载一个简单的动态文字或形状，并通过 MRQ 渲染。

```cpp
// MyMotionDesignActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "MyMotionDesignActor.generated.h"

UCLASS()
class MYPROJECT_API AMyMotionDesignActor : public AActor
{
    GENERATED_BODY()
public:
    AMyMotionDesignActor();
    virtual void BeginPlay() override;

    // 指向一个在编辑器中设置的 AvaText 组件
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Motion Design")
    UText3DComponent* TextComponent;
};
```

```cpp
// MyMotionDesignActor.cpp
#include "MyMotionDesignActor.h"
#include "Components/Text3DComponent.h"

AMyMotionDesignActor::AMyMotionDesignActor()
{
    PrimaryActorTick.bCanEverTick = true;
    TextComponent = CreateDefaultSubobject<UText3DComponent>(TEXT("MDText"));
    RootComponent = TextComponent;
}

void AMyMotionDesignActor::BeginPlay()
{
    Super::BeginPlay();
    if (TextComponent)
    {
        TextComponent->SetText(FText::FromString(TEXT("Hello Motion Design!")));
    }
}
```

## 模块依赖

由于 Motion Design 是一个功能聚合器，其具体子模块的依赖各不相同。以下是其 **运行时核心模块** 最主要的、独特的依赖。使用者的 `Build.cs` 文件应根据实际调用的 API 来引入对应的模块。

| 模块 | 用途 |
|---|---|
| `MediaCompositing` | 提供媒体合成、播放和输出框架，是广播功能的基础。 |
| `RemoteControl` | 用于远程控制和自动化，是实现场景控制和参数调节的关键。 |
| `ActorModifierCore` | 提供 Actor 修改器系统的核心接口，是效果和动画系统的基础。 |
| `Text3D` | 提供 3D 文字渲染功能。 |
| `GeometryCache` | 用于存储和播放预计算的几何体缓存动画。 |
| `SVGImporter` | 提供 SVG 文件的导入和解析功能，用于导入矢量图形。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将Motion Design的场景设置和大纲面板从关卡编辑器中分离到独立窗口组。 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 在使用Rundown页面设置进行Movie Render Queue渲染时添加了数据统计分析功能。 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 在节目控制工具栏中增加了页面加载选项（全部、下一个、已选择），并优化了相关功能。 |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 增加了项目设置，用于强制禁用Text3D和形状的碰撞检测。 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it or disassociated with viewport client | 重构了视口客户端关联逻辑，通过通知机制减少重复代码。 |

### 维护评价

Motion Design 是一个**非常活跃**且**持续更新**的插件。它于 2025 年从实验性路径移至正式的 Virtual Production 路径，表明其已经成熟并得到官方的正式支持。最近（2026年5月）的更新频率很高，内容涉及新功能（如MRQ分析、页面加载选项）、UX改进（面板重组）和底层优化（碰撞设置、代码重构）。这些迹象表明，Epic Games 正在持续投入开发和维护此插件。**强烈推荐**在虚拟制作和广播项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/virtual-production-tools-in-unreal-engine/) (需在官方文档站中搜索“Motion Design”)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheFunctionalTest) (插件内含功能测试模块)