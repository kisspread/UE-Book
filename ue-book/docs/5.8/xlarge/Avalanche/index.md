# Motion Design

> Compositing, designer and broadcasting tool.
>
> Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（资产、工具、示例） |
| 模块 | `Avalanche` (Runtime), `AvalancheAttribute` (Runtime), `AvalancheAttributeEditor` (Runtime), `AvalancheCamera` (Runtime), `AvalancheComponentVisualizers` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), `AvalancheEditorCore` (Runtime), `AvalancheEffectors` (Runtime), `AvalancheEffectorsEditor` (Runtime), `AvalancheFunctionalTest` (Runtime), `AvalancheInteractiveTools` (Runtime), `AvalancheInteractiveToolsRuntime` (Runtime), `AvalancheLevelViewport` (Runtime), `AvalancheMRQ` (Runtime), `AvalancheMRQEditor` (Runtime), `AvalancheMask` (Runtime), `AvalancheMaskEditor` (Runtime), `AvalancheMaterial` (Runtime), `AvalancheMedia` (Runtime), `AvalancheMediaEditor` (Runtime), `AvalancheModifiers` (Runtime), `AvalancheModifiersEditor` (Runtime), `AvalancheOutliner` (Runtime), `AvalanchePropertyAnimator` (Runtime), `AvalanchePropertyAnimatorEditor` (Runtime), `AvalancheRemoteControl` (Runtime), `AvalancheRemoteControlEditor` (Runtime), `AvalancheSVGEditor` (Runtime), `AvalancheSceneRig` (Runtime), `AvalancheSceneRigEditor` (Runtime), `AvalancheSceneTree` (Runtime), `AvalancheSequence` (Runtime), `AvalancheSequencer` (Runtime), `AvalancheShapes` (Runtime), `AvalancheShapesEditor` (Runtime), `AvalancheTag` (Runtime), `AvalancheTagEditor` (Runtime), `AvalancheText` (Runtime), `AvalancheTextEditor` (Runtime), `AvalancheTransition` (Runtime), `AvalancheTransitionEditor` (Runtime), `AvalancheViewport` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途
Motion Design 是一个综合性的虚拟制作工具套件，为广播图形、动态影像和实时合成提供了一个集成的设计环境。它解决的核心问题是将传统后期合成软件（如 After Effects）中的图层合成、动态图形设计和模板化工作流，与 Unreal Engine 的实时渲染和场景管理能力相结合。其存在是为了让广播设计师和动态影像艺术家能够在 Unreal Engine 中高效地创建、预览和播出复杂的、基于数据的实时图形内容。

## 使用场景
- **广播图形制作**：你需要为体育赛事、新闻或颁奖典礼制作实时更新的比分牌、标题栏、选手介绍等动态模板。
- **运动设计与动态影像**：你需要在 UE 中设计复杂的 Logo 动画、信息图表和产品展示动画。
- **实时合成与播出**：你需要将多个 2D/3D 图层、文本、图片、视频等元素进行实时合成，并控制其出入场动画，最终输出到广播级设备。
- **数据驱动可视化**：你需要将外部数据（如数据库、API）实时绑定到图形模板中，用于选举计票、金融数据显示等。

## 蓝图用法
本插件提供了一套完整的蓝图节点用于控制运动设计场景。核心功能通过 `UAMotionDesignScene` 等类暴露。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Motion Design Scene` | 在指定层级中创建一个新的运动设计场景资产。 | `UAMotionDesignSubsystem` |
| `Get Active Motion Design Scene` | 获取当前活动的运动设计场景对象。 | `UAMotionDesignSubsystem` |
| `Activate Scene` / `Deactivate Scene` | 激活或停用一个运动设计场景，控制其在编辑器和运行时中的渲染。 | `UAMotionDesignScene` |
| `Set Template Data` | 为场景中的模板设置数据参数，用于数据驱动。 | `UAMotionDesignScene` |
| `Trigger Transition` | 按名称触发场景中预设的过渡动画。 | `UAMotionDesignScene` |

### 使用示例（蓝图描述）
1.  在事件图表中，使用 `Get Motion Design Subsystem` 节点获取子系统。
2.  调用 `Create Motion Design Scene` 节点，指定一个父级 Actor，来在场景中生成一个运动设计场景容器。
3.  通过返回的场景对象，可以调用 `Activate Scene` 使其生效。
4.  后续使用 `Set Template Data` 节点将动态数据（如比分）注入场景，并用 `Trigger Transition` 控制画面切换。

## C++ 用法
### 头文件引入
```cpp
#include "AMotionDesignScene.h"
#include "AMotionDesignSubsystem.h"
```

### 基本用法
```cpp
// 获取运动设计子系统
UAMotionDesignSubsystem* MDSubsystem = GEditor->GetEditorSubsystem<UAMotionDesignSubsystem>();
if (MDSubsystem)
{
    // 在关卡上下文中创建一个新的运动设计场景
    UAMotionDesignScene* NewScene = MDSubsystem->CreateMotionDesignScene(GetWorld());
    if (NewScene)
    {
        NewScene->ActivateScene(); // 激活场景
    }
}
```

### 进阶用法
结合 Remote Control 和 Sequencer 模块，可以实现复杂的播出流程自动化，例如通过 C++ 逻辑在特定时间点批量设置模板参数并触发过渡。

## Demo 示例
一个最小的 C++ 示例，展示如何创建并激活一个运动设计场景。
```cpp
// MyMotionDesignActor.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyMotionDesignActor.generated.h"

class UAMotionDesignScene;

UCLASS()
class MYPROJECT_API AMyMotionDesignActor : public AActor
{
    GENERATED_BODY()

public:
    AMyMotionDesignActor();

    UPROPERTY(BlueprintReadOnly, Category = "Motion Design")
    UAMotionDesignScene* MotionDesignScene;

    virtual void BeginPlay() override;
};
```
```cpp
// MyMotionDesignActor.cpp
#include "MyMotionDesignActor.h"
#include "AMotionDesignScene.h"
#include "AMotionDesignSubsystem.h"

AMyMotionDesignActor::AMyMotionDesignActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyMotionDesignActor::BeginPlay()
{
    Super::BeginPlay();

    UAMotionDesignSubsystem* Subsystem = GEditor->GetEditorSubsystem<UAMotionDesignSubsystem>();
    if (Subsystem)
    {
        MotionDesignScene = Subsystem->CreateMotionDesignScene(GetWorld(), this);
        if (MotionDesignScene)
        {
            MotionDesignScene->ActivateScene();
            UE_LOG(LogTemp, Log, TEXT("Motion Design Scene created and activated."));
        }
    }
}
```

## 模块依赖
使用此插件不需要在你的项目模块的 `.Build.cs` 中添加特殊依赖，因为它的功能主要通过编辑器子系统、蓝图节点和资产来访问。如果需要通过 C++ 进行深度集成（如扩展编辑器），则需依赖 `AvalancheEditorCore`。

| 模块 | 用途 |
|---|---|
| `AvalancheCore` | 运动设计的核心运行时逻辑和场景管理。 |
| `AvalancheMedia` | 处理与媒体 I/O、合成和输出相关的功能。 |
| `AvalancheSequencer` | 与 Sequencer 集成，控制时间线和动画。 |
| `AvalancheRemoteControl` | 支持通过 Remote Control 面板进行参数控制和数据绑定。 |
| `AvalancheMRQ` | 集成 Movie Render Queue，用于高质量离线渲染输出。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将编辑器中的场景设置和大纲窗口移入独立分组，优化了编辑器UI组织结构。 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 在使用Rundown Page设置时添加了Movie Render Queue分析功能。 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 在播出控制工具栏添加了页面加载选项（全部、下一个、已选），并进行了相关增强。 |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 添加了项目设置，可强制禁用3D文本和形状的碰撞检测。 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构了视口模块代码，通过客户端通知机制处理关联与解除关联逻辑。 |

### 维护评价
Motion Design 插件正处于**活跃维护**状态。自2025年5月从实验性分支迁移到虚拟制片正式分类后，持续进行功能增强和优化。最近一次更新就在几天前，且更新内容涵盖了编辑器体验改进、新功能添加（如MRQ分析、页面加载）和项目设置，表明 Epic Games 对其开发非常积极。该插件是虚拟制片和广播图形工作流的核心组件，建议在相关项目中使用。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/motion-design-in-unreal-engine/)