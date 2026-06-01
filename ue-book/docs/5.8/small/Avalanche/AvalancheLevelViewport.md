# Motion Design

> Compositing, designer and broadcasting tool.
> Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（编辑器工具、视口增强、蓝图资产、运行时组件） |
| 模块 | `Avalanche` (Runtime), `AvalancheAttribute` (Runtime), `AvalancheAttributeEditor` (Runtime), `AvalancheCamera` (Runtime), `AvalancheComponentVisualizers` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), `AvalancheEditorCore` (Runtime), `AvalancheEffectors` (Runtime), `AvalancheEffectorsEditor` (Runtime), `AvalancheFunctionalTest` (Runtime), `AvalancheInteractiveTools` (Runtime), `AvalancheInteractiveToolsRuntime` (Runtime), `AvalancheLevelViewport` (Runtime), `AvalancheMRQ` (Runtime), `AvalancheMRQEditor` (Runtime), `AvalancheMask` (Runtime), `AvalancheMaskEditor` (Runtime), `AvalancheMaterial` (Runtime), `AvalancheMedia` (Runtime), `AvalancheMediaEditor` (Runtime), `AvalancheModifiers` (Runtime), `AvalancheModifiersEditor` (Runtime), `AvalancheOutliner` (Runtime), `AvalanchePropertyAnimator` (Runtime), `AvalanchePropertyAnimatorEditor` (Runtime), `AvalancheRemoteControl` (Runtime), `AvalancheRemoteControlEditor` (Runtime), `AvalancheSVGEditor` (Runtime), `AvalancheSceneRig` (Runtime), `AvalancheSceneRigEditor` (Runtime), `AvalancheSceneTree` (Runtime), `AvalancheSequence` (Runtime), `AvalancheSequencer` (Runtime), `AvalancheShapes` (Runtime), `AvalancheShapesEditor` (Runtime), `AvalancheTag` (Runtime), `AvalancheTagEditor` (Runtime), `AvalancheText` (Runtime), `AvalancheTextEditor` (Runtime), `AvalancheTransition` (Runtime), `AvalancheTransitionEditor` (Runtime), `AvalancheViewport` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Avalanche (Motion Design) 是 Epic Games 为 Unreal Engine 开发的**核心动态图形（Motion Graphics）设计与广播工具集**。它并非一个单一功能的插件，而是一个庞大的、模块化的生态系统，旨在将 UE 打造为专业级的 2D/3D 动态图形创作与实时渲染平台。

**核心价值：**
1.  **专业视口与布局工具**：提供增强的编辑器视口，支持像素对齐网格、安全框、参考线、对齐吸附、虚拟画布尺寸设置等，满足广播级图形设计的精确需求。
2.  **矢量与形状创作**：集成 SVG 导入、2D/3D 矢量形状创建与编辑工具（AvalancheShapes），是制作图形元素的基础。
3.  **高级文本系统**：依赖 Text3D 插件，提供强大的三维文字排版与动画能力。
4.  **非线性动画与过渡**：包含属性动画器、克隆/效果器、过渡效果等，用于创建复杂的动画序列和视觉特效。
5.  **合成与媒体集成**：支持与 Media IO 框架集成，用于实时视频合成、直播图形叠加。
6.  **远程控制与自动化**：通过 Remote Control 插件支持，允许外部设备（如 MIDI 控制器、触摸屏）实时控制场景参数。
7.  **场景与设备管理**：提供场景树、场景设备、节目单（Rundown）管理功能，适用于广播现场的多屏、多场景切换控制。

简而言之，Avalanche 的存在是为了让创作者能够在 UE 中像使用 After Effects 或 Cinema 4D 的 MoGraph 模块一样，高效地设计、动画和渲染用于广播、活动、虚拟制片等领域的动态图形内容。

## 使用场景

- 你正在为一场**演唱会或颁奖典礼**制作实时渲染的舞台背景和视觉特效 → 使用 Motion Design 的形状、文本、克隆效果器和属性动画工具。
- 你需要为**电视直播**（如新闻、体育赛事）设计并实时驱动画中画、比分板、动态标题等图形模板 → 使用 Media Compositing 和 Remote Control 功能。
- 你在制作一个**虚拟发布会或在线展览**，需要复杂的 UI 动画和过渡效果 → 使用 Transition、PropertyAnimator 和 Sequencer 进行设计。
- 你需要精确地**对齐多个图形元素**以匹配设计稿 → 使用 AvalancheLevelViewport 增强视口中的网格、参考线和对齐工具。

## 蓝图用法

Motion Design 的大部分核心蓝图接口分布在其众多子模块中。从当前分析的 `AvalancheLevelViewport` 模块来看，其功能主要通过 **编辑器命令** 和 **视口交互** 暴露，而非传统的蓝图函数节点。以下是通过命令和组件暴露的核心功能分组：

### 核心命令 (FAvaLevelViewportCommands)

这些命令可通过 `FAvaLevelViewportCommands::Get()` 访问，并通常绑定到编辑器的键盘快捷键或工具栏按钮。

| 命令 | 说明 | 所在类 |
|---|---|---|
| `ToggleOverlay` | 切换视口中的各种覆盖显示（如网格、安全框）。 | `FAvaLevelViewportCommands` |
| `ToggleBoundingBoxes` | 切换选中Actor的边界框显示。 | `FAvaLevelViewportCommands` |
| `ToggleIsolateActors` | 切换隔离选中Actor的显示模式。 | `FAvaLevelViewportCommands` |
| `ToggleSafeFrames` | 切换广播安全框的显示。 | `FAvaLevelViewportCommands` |
| `ToggleChildActorLock` | 切换拖动时子Actor跟随的锁定状态。 | `FAvaLevelViewportCommands` |
| `TogglePostProcessBackground` | 切换后处理通道中的背景显示。 | `FAvaLevelViewportCommands` |
| `CameraZoomInCenter` / `CameraZoomOutCenter` | 以视口中心为基准进行视图缩放。 | `FAvaLevelViewportCommands` |
| `ToggleGrid` | 切换网格显示。 | `FAvaLevelViewportCommands` |
| `ToggleSnapping` | 切换全局吸附开关。 | `FAvaLevelViewportCommands` |
| `ToggleGridSnapping` / `ToggleScreenSnapping` / `ToggleActorSnapping` | 分别切换吸附到网格、屏幕元素、其他Actor。 | `FAvaLevelViewportCommands` |
| `VirtualSize1920x1080` | 将视口虚拟画布尺寸设置为1920x1080。 | `FAvaLevelViewportCommands` |
| `AddGuideHorizontal` / `AddGuideVertical` | 添加水平或垂直参考线。 | `FAvaLevelViewportCommands` |
| `DisableAnimators` / `EnableAnimators` | 批量禁用或启用场景中所有的属性动画器。 | `FAvaLevelViewportCommands` |

### 使用示例（蓝图描述）

由于该模块的功能主要集成在编辑器视口和菜单中，蓝图中更常见的用法是：
1.  **通过 Remote Control 或自定义 UI** 调用场景中对象的属性，这些属性可能已被 `PropertyAnimator` 等组件动画化。
2.  在**编译时**，通过 C++ 调用 `FAvaLevelViewportCommands::GetExternal()` 获取命令列表，并将其集成到自定义的编辑器扩展或工具中。

## C++ 用法

### 头文件引入

```cpp
#include "AvaLevelViewportCommands.h" // 用于访问视口命令
#include "AvaViewportColorPickerActorClassRegistry.h" // 用于注册自定义颜色选择器适配器
#include "IAvaViewportColorPickerAdapter.h" // 颜色适配器接口
```

### 基本用法

#### 1. 注册自定义 Actor 的颜色选择器适配器
让编辑器的 Motion Design 颜色选择器能够识别并编辑你的自定义 Actor 颜色。

```cpp
// MyActorColorAdapter.h
#pragma once
#include "IAvaViewportColorPickerAdapter.h"

class AMyColorPickableActor : public AActor
{
public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FLinearColor PrimaryColor;

    // 满足 CAvaViewportColorPickable 概念的函数
    FAvaColorChangeData GetColorData() const;
    void SetColorData(const FAvaColorChangeData& InData);
};

struct FMyActorColorAdapter : public IAvaViewportColorPickerAdapter
{
    virtual bool GetColorData(const AActor& InActor, FAvaColorChangeData& OutColorData) const override
    {
        if (const AMyColorPickableActor* MyActor = Cast<AMyColorPickableActor>(&InActor))
        {
            OutColorData = MyActor->GetColorData();
            return true;
        }
        return false;
    }

    virtual void SetColorData(AActor& InActor, const FAvaColorChangeData& InColorData) const override
    {
        if (AMyColorPickableActor* MyActor = Cast<AMyColorPickableActor>(&InActor))
        {
            MyActor->SetColorData(InColorData);
        }
    }
};
```

```cpp
// MyActorColorAdapter.cpp (模块启动时注册)
#include "AvaViewportColorPickerActorClassRegistry.h"

void FMyModule::StartupModule()
{
    // 方式1：使用默认适配器（要求 Actor 类有 GetColorData/SetColorData）
    FAvaViewportColorPickerActorClassRegistry::RegisterDefaultClassAdapter<AMyColorPickableActor>();
    
    // 方式2：使用自定义适配器
    FAvaViewportColorPickerActorClassRegistry::RegisterClassAdapter<AMyColorPickableActor, FMyActorColorAdapter>();
}
```

#### 2. 访问并使用视口命令
```cpp
#include "AvaLevelViewportCommands.h"

void FMyEditorUtility::PerformViewportAction()
{
    const FAvaLevelViewportCommands& Commands = FAvaLevelViewportCommands::GetExternal();
    
    // 模拟执行“切换安全框”命令
    if (Commands.ToggleSafeFrames)
    {
        FUICommandInfo::ExecuteCommand(Commands.ToggleSafeFrames);
    }
    
    // 或者，你可以将命令绑定到你自己的 UI 元素
    // TSharedPtr<FUICommandInfo> MySafeFrameButton = Commands.ToggleSafeFrames;
}
```

### 进阶用法

结合 `AvalancheCore` 和 `AvalancheOutliner` 模块，可以编程式地控制 Motion Design 场景的层次结构和动画状态。例如，通过 C++ 批量查询场景树中的特定类型节点，并对其应用统一的动画控制。这通常涉及操作 `UAvaSceneTree` 和 `IAvaObjectNode` 接口。

## Demo 示例

以下示例展示如何让你的自定义 Actor `AMyWidgetActor` 能够使用 Motion Design 的颜色选择器。

```cpp
// MyWidgetActor.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "AvaDefs.h" // 用于 FAvaColorChangeData
#include "MyWidgetActor.generated.h"

UCLASS()
class MYMODULE_API AMyWidgetActor : public AActor
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Appearance")
    FLinearColor WidgetColor = FLinearColor::White;

    // Motion Design 颜色选择器所需的接口函数
    FAvaColorChangeData GetColorData() const;
    void SetColorData(const FAvaColorChangeData& InColorData);
};

// MyWidgetActor.cpp
#include "MyWidgetActor.h"
#include "AvaDefs.h"

FAvaColorChangeData AMyWidgetActor::GetColorData() const
{
    FAvaColorChangeData Data;
    // 简单实现：将我们的单一颜色作为主色
    Data.SolidColor = WidgetColor;
    return Data;
}

void AMyWidgetActor::SetColorData(const FAvaColorChangeData& InColorData)
{
    // 更新颜色并通知编辑器
    Modify();
    WidgetColor = InColorData.SolidColor;
    // 通常还需要处理子组件材质等，这里简化
}

// MyModule.cpp (模块启动时)
#include "AvaViewportColorPickerActorClassRegistry.h"
#include "MyWidgetActor.h"

void FMyModule::StartupModule()
{
    // 注册适配器，使编辑器能识别 AMyWidgetActor
    FAvaViewportColorPickerActorClassRegistry::RegisterDefaultClassAdapter<AMyWidgetActor>();
}
```

## 模块依赖

Motion Design 是一个庞大的插件，其内部模块依赖关系复杂。以下是 `AvalancheLevelViewport` 模块（及整个插件）的一些**独特外部依赖**：

| 模块 | 用途 |
|---|---|
| `SvgImporter` | 提供 SVG 文件导入功能，是矢量图形工作流的基础。 |
| `Text3D` | 提供强大的三维文字创建和渲染功能。 |
| `RemoteControl` | 允许通过网络或本地协议远程控制引擎和 Actor 属性，用于广播自动化。 |
| `GeometryScripting` / `GeometryCache` | 提供程序化几何体创建和缓存功能，用于高级形状和效果器。 |
| `MediaCompositing` / `MediaIOFramework` | 提供媒体合成、视频输入/输出和实时合成支持。 |
| `DynamicMaterial` | 支持运行时动态创建和修改材质实例。 |
| `ActorModifierCore` | 提供 Actor 修改器的核心框架，是很多视觉效果组件的基础。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将关卡编辑器中的动态设计标签页移至独立分组，优化界面布局。 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 为节目单页面设置添加了 MRQ（Movie Render Queue）分析功能。 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 在演出控制工具栏增加了页面加载选项（全部、下一个、选定），并新增功能。 |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 新增项目设置，可强制禁用 Text3D 和形状的碰撞。 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口：通过客户端关联/解关联通知来重构必要的模板代码。 |

### 维护评价

**活跃维护**。Motion Design (Avalanche) 是 Epic Games 虚拟制片战略的核心组件之一，自 2025 年 5 月从实验性状态正式发布以来，保持着**非常活跃的开发节奏**。近期的提交记录（2026年5月）显示，团队正在持续添加新功能（如节目单分析、页面加载选项）、优化用户体验（如标签页布局）并修复底层问题（如碰撞设置）。该插件拥有庞大的模块和文件数量，表明其功能复杂且仍在快速迭代。对于虚拟制片和广播图形领域，这是一个**强烈推荐使用**的官方解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/motion-design-in-unreal-engine/) (基于UE5.8文档结构推测，可能为Beta版文档)