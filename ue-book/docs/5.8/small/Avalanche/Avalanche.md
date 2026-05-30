# Motion Design

> Compositing, designer and broadcasting tool.
> 
> Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `Avalanche` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), `AvalancheEditorCore` (Runtime), `AvalancheMedia` (Runtime), `AvalancheMediaEditor` (Runtime), `AvalancheSceneRig` (Runtime), `AvalancheSceneRigEditor` (Runtime), `AvalancheMRQ` (Runtime), `AvalancheMRQEditor` (Runtime), `AvalancheSequencer` (Runtime), `AvalancheOutliner` (Runtime) ... 等 42 个模块 |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Motion Design 是一个功能强大的虚幻引擎插件，专为广播和虚拟制作场景中的动态图形（Motion Graphics）、场景管理和播出流程集成而设计。它远不止是一个简单的合成工具，而是一个完整的生态系统，旨在简化和加速从设计到播出的整个工作流程。

**核心问题与存在意义：**
1.  **统一工作流：** 它将场景构建、图形设计、动画控制、远程操控和最终输出（如通过 Media Render Queue 输出到 SDI）整合到一个基于虚幻引擎的统一环境中，解决了广播和虚拟制作中工具链分散的问题。
2.  **专业化场景管理：** 通过 `AAvaScene`、`IAvaSceneInterface`、`UAvaSceneSubsystem` 和 `FAvaSceneTree` 等核心类，为动态图形项目提供了专门的场景层次结构和状态管理（属性、标签、序列），替代了通用关卡蓝图的复杂性。
3.  **播出就绪特性：** 内置了对播出关键功能的支持，例如：
    *   **过渡系统 (`AvalancheTransition`)**：基于状态树的复杂场景切换逻辑。
    *   **远程控制集成 (`AvalancheRemoteControl`)**：允许通过网络或自定义接口控制场景参数。
    *   **序列与播放 (`AvalancheSequence`, `AvalancheSequencer`)**：精细的动画时间线控制。
    *   **独立播放实例 (`UAvaGameInstance`)**：支持在编辑器内或通过 Media IO Framework 为输出通道创建独立的播放世界。
4.  **专业化组件与工具：** 提供了专为 2D/2.5D 动态图形设计的组件，如 `UAvaGizmoComponent`（用于对象的视觉表示控制）、`UAvaTickerComponent`（滚动字幕）、`AAvaNullActor`（空组）等，以及精确的视口交互和对齐工具。

## 使用场景

*   **你正在制作虚拟制作项目的动态图形包**（Lower Thirds, Over-the-Shoulders, 全屏模板），需要快速设计、预览和管理这些图形资源 → 使用 Motion Design 的场景树、组件和材质系统进行设计。
*   **你需要为一场直播或录播节目准备多个可切换的场景状态**（如“待机”、“播放”、“结束”），并且需要复杂的过渡逻辑（如检查遥控参数变化、场景标签） → 使用 `AvalancheTransition` 模块和状态树来定义切换规则。
*   **你的播出系统需要接收来自虚幻引擎的 4K SDI 信号输出**，并且需要在不关闭主编辑器的情况下，通过“节目输出”通道独立播放内容 → 使用 `UAvaGameInstance` 和 `AvalancheMedia` 模块来创建和管理独立的播放实例和输出通道。
*   **你希望艺术家或设计师能在不编写代码的情况下，通过简单的界面调整远程控制的场景参数**（如修改颜色、位置、播放动画） → 使用 `AvalancheRemoteControl` 模块将场景属性暴露为可通过远程控制预设（Remote Control Preset）管理的控制器。
*   **你需要构建一个带有滚动字幕（Ticker）的新闻或体育节目图形系统** → 使用 `UAvaTickerComponent` 和 `AAvaTickerActor` 来创建和管理滚动条目队列。

## 蓝图用法

Motion Design 的蓝图 API 主要通过子系统、实用工具库和特定组件暴露。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Is Ready To Play` | 检查当前关卡的 Motion Design 场景是否已完成所有构建任务（如 Text3D 生成），可以安全开始播放。 | `UAvaSceneSubsystem` |
| `Flush Builds` | 强制完成所有挂起的 Motion Design 构建任务，确保场景在播放前完全就绪。 | `UAvaSceneSubsystem` |
| `Gather Scene Tree Actors` | 按照场景树顺序收集 Actor。可指定父 Actor 和是否包含后代，是遍历场景结构的官方方式。 | `UAvaSceneSubsystem` |
| `Add Tag Attribute` / `Remove Tag Attribute` | 向当前过渡上下文（场景）添加或移除一个标签属性。 | `UAvaTransitionAttributeLibrary` |
| `Contains Tag Attribute` | 检查当前过渡上下文（场景）是否包含指定的标签属性。 | `UAvaTransitionAttributeLibrary` |
| `Compare RC Controller Values` | 比较一个远程控制控制器的值在不同过渡上下文（场景）之间是否相同或不同。 | `UAvaTransitionRCLibrary` |
| `Get Changed RC Controllers` | 获取在上一次场景切换中值发生变化的远程控制控制器列表。 | `UAvaTransitionRCLibrary` |
| `Queue Actor` | 将一个 Actor 添加到 Ticker 组件的队列中，使其成为滚动条目。 | `UAvaTickerComponent` |

### 使用示例（蓝图描述）

**示例1：检查场景就绪并开始播放**
1.  在关卡蓝图或一个管理器 Actor 中，使用 `Get Motion Design Scene Subsystem` 节点获取子系统。
2.  将其连接到 `Is Ready To Play` 节点，并将 `self`（当前 Actor）作为 `Context Object`。
3.  将 `Is Ready To Play` 的返回值连接到一个分支节点。
4.  在 `True` 分支中，调用 `Flush Builds` 节点，然后执行播放逻辑（例如，触发一个序列或通知媒体输出通道开始）。

**示例2：使用过渡系统切换场景状态**
1.  在过渡状态树中，使用 `A scene contains tag attribute` 条件节点。
2.  设置 `Scene Type` 为 `This` 或 `Other`，`Layer Type` 为 `Same`。
3.  在 `Tag Attribute` 字段指定要检查的标签（如 “Live”）。
4.  当该条件满足时，连接到一个 `Add tag attribute to this scene` 任务节点，为目标场景添加另一个标签（如 “OnAir”）。

## C++ 用法

Motion Design 的 C++ API 主要围绕场景接口、子系统和核心框架类构建。

### 头文件引入

```cpp
// 核心场景和子系统
#include "AvaScene.h"
#include "AvaSceneSubsystem.h"
#include "IAvaSceneInterface.h"

// 过渡系统
#include "Transition/Conditions/AvaSceneContainsTagAttributeCondition.h"
#include "Transition/Tasks/AvaSceneAddTagAttributeTask.h"

// 组件
#include "Framework/AvaGizmoComponent.h"
#include "Framework/Ticker/AvaTickerComponent.h"
```

### 基本用法

```cpp
// 从任意 Actor 获取当前关卡的 Motion Design 场景接口
void AMyManagerActor::CheckMotionDesignScene()
{
    if (UAvaSceneSubsystem* SceneSubsystem = UWorld::GetSubsystem<UAvaSceneSubsystem>(GetWorld()))
    {
        if (IAvaSceneInterface* SceneInterface = SceneSubsystem->GetSceneInterface())
        {
            // 访问场景设置、属性容器等
            UAvaSceneSettings* Settings = SceneInterface->GetSceneSettings();
            UAvaAttributeContainer* Attributes = SceneInterface->GetAttributeContainer();
            
            // 检查场景是否就绪
            bool bReady = SceneSubsystem->IsReadyToPlay(this);
        }
    }
}
```

### 进阶用法

```cpp
// 在代码中安全地创建或获取 AAvaScene 实例
void AMyLevelSetup::EnsureAvaSceneExists()
{
    if (ULevel* CurrentLevel = GetLevel())
    {
        // GetScene 会查找现有场景，如果找不到且 bCreateSceneIfNotFound 为 true，则创建一个。
        AAvaScene* Scene = AAvaScene::GetScene(CurrentLevel, true);
        if (Scene)
        {
            // 可以从这里访问 IAvaSequenceProvider, IAvaRemoteControlInterface 等。
            IAvaSequenceProvider* SeqProvider = Scene->GetSequenceProvider();
        }
    }
}

// 为自定义 Actor 添加 Gizmo 行为
void AMyGraphicActor::SetupGizmoBehavior()
{
    if (UAvaGizmoComponent* GizmoComp = FindComponentByClass<UAvaGizmoComponent>())
    {
        // 自定义 gizmo 的渲染属性
        GizmoComp->SetGizmoEnabled(true);
        GizmoComp->SetMaterial(MyCustomMaterial);
        GizmoComp->SetCastShadow(false);
        GizmoComp->SetRenderInMainPass(true);
        GizmoComp->SetRenderDepth(false);
    }
}
```

## Demo 示例

一个最小的 C++ 示例，展示如何获取场景子系统并查询场景状态。

**MyMotionDesignActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyMotionDesignActor.generated.h"

UCLASS()
class MYPROJECT_API AMyMotionDesignActor : public AActor
{
    GENERATED_BODY()

public:
    AMyMotionDesignActor();

    UFUNCTION(BlueprintCallable, Category = "Motion Design")
    void PrintSceneStatus();

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY()
    bool bLastReadyState = false;
};
```

**MyMotionDesignActor.cpp**
```cpp
#include "MyMotionDesignActor.h"
#include "AvaSceneSubsystem.h" // 核心子系统
#include "IAvaSceneInterface.h" // 场景接口

AMyMotionDesignActor::AMyMotionDesignActor()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AMyMotionDesignActor::BeginPlay()
{
    Super::BeginPlay();
    PrintSceneStatus();
}

void AMyMotionDesignActor::PrintSceneStatus()
{
    // 1. 获取当前世界对应的 Motion Design 场景子系统
    UAvaSceneSubsystem* SceneSubsystem = UWorld::GetSubsystem<UAvaSceneSubsystem>(GetWorld());
    if (!SceneSubsystem)
    {
        UE_LOG(LogTemp, Warning, TEXT("Motion Design Scene Subsystem not available."));
        return;
    }

    // 2. 使用子系统检查场景是否就绪（这是推荐的异步就绪检查方式）
    const bool bCurrentlyReady = SceneSubsystem->IsReadyToPlay(this);
    
    if (bCurrentlyReady != bLastReadyState)
    {
        UE_LOG(LogTemp, Log, TEXT("Motion Design scene ready state changed: %s"), bCurrentlyReady ? TEXT("READY") : TEXT("NOT READY"));
        bLastReadyState = bCurrentlyReady;

        // 3. 如果场景就绪，获取并访问场景接口以获取更多信息
        if (bCurrentlyReady)
        {
            if (IAvaSceneInterface* SceneInterface = SceneSubsystem->GetSceneInterface())
            {
                UAvaAttributeContainer* Attributes = SceneInterface->GetAttributeContainer();
                UE_LOG(LogTemp, Log, TEXT("Scene Attributes Container address: %p"), Attributes);
                
                // 强制完成所有挂起的构建（例如，Text3D 网格生成）
                SceneSubsystem->FlushBuilds();
            }
        }
    }
}
```

## 模块依赖

Motion Design 依赖一系列专用功能插件。要在你的项目中使用它，你的模块（例如，`MyGameModule.Build.cs`）需要依赖 `Avalanche` 核心运行时模块。

| 模块 | 用途 |
|---|---|
| `Sequencer` | 用于 `AvalanchePropertyAnimator` 模块，提供属性动画的时间线控制能力。 |
| **(无其他特殊依赖)** | 核心 `Avalanche` 模块依赖标准的 UE 模块（Core, Engine, Slate 等）以及几个由 Epic 维护的其他 VirtualProduction / Experimental 插件（如 Remote Control, MediaCompositing, Text3D, ActorModifierCore），这些插件在启用 Motion Design 时会自动作为依赖项被加载。 |

**注意**：由于 Motion Design 是一个大型插件集，许多功能被拆分到独立的子模块（如 `AvalancheTransition`, `AvalancheRemoteControl`, `AvalancheMRQ` 等）。通常，你只需要依赖主 `Avalanche` 模块，具体的子模块会根据你使用的功能被隐式引入。如果你的代码需要直接使用特定子模块的功能（例如，直接使用过渡任务），则需要在 Build.cs 中显式添加对 `AvalancheTransition` 等模块的依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own group | 将 Motion Design 的标签页（场景设置、大纲视图）在关卡编辑器中移至独立的分组。 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 使用 MRQ（媒体渲染队列）的节目单页面设置时，增加了分析功能。 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and added MRQ rundown page selection to playback control toolbar | 为播出控制工具栏添加了页面加载选项（全部、下一个、选定），并将 MRQ 节目单页面选择添加到了播放控制工具栏。 |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 添加了项目设置，可强制禁用 Text3D 和形状的碰撞。 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated with a viewport. | 重构了视口关联逻辑，当客户端与视口关联或取消关联时会收到通知。 |

### 维护评价

*   **创建时间**：2025年5月，是一个相对年轻的插件（约1年）。
*   **最近更新频率**：**非常活跃**。仅在提供的时间范围内（2026年5月14日至20日）就有5次提交，且都是功能增强和改进，而非简单的编译修复。
*   **维护团队**：由 Epic Games, Inc. 官方维护，属于 Virtual Production 套件的核心部分。
*   **功能状态**：插件从 `Experimental` 迁移到 `VirtualProduction` 目录，表明其已从实验阶段毕业，进入正式支持阶段。源码显示持续有新功能（如 MRQ 分析、页面控制）和用户体验优化（UI 分组）加入。
*   **推荐程度**：**强烈推荐**。对于涉及广播、虚拟制作、实时图形播出的项目，Motion Design 是虚幻引擎官方提供的最成熟、功能最全面的解决方案。尽管模块众多，但其架构清晰，且由 Epic 积极维护和迭代。建议始终使用最新引擎版本以获得最佳功能和稳定性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- 官方文档（暂无直接链接，请查阅虚幻引擎官方文档中的 “Motion Design” 部分）