# Motion Design

> Compositing, designer and broadcasting tool. Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（运行时与编辑器模块） |
| 模块 | `Avalanche` (Runtime), `AvalancheEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Motion Design (Avalanche) 是一个专为虚拟制作打造的综合性2D/3D动态图形（Motion Graphics）设计与播出系统。它并非一个简单的合成器，而是一个完整的场景管理、渲染控制、动画编排和实时播出框架。其核心目标是解决在广播、虚拟演播室、产品展示等场景中，需要高效、实时地创建、管理和播出复杂动态图形内容的问题。

插件通过 `AAvaScene` Actor 作为核心容器，管理整个动态设计场景的属性、层级树、动画序列、远程控制预设以及与媒体输出的集成。它提供了专用的视口、交互工具（如对齐吸附）、场景过渡逻辑（StateTree）、属性动画以及与Media IO和电影渲染管线的深度集成，从而形成了一套端到端的解决方案。

## 使用场景

- **虚拟制作图形播出**：在虚拟演播室或实景增强节目中，实时播出新闻标题、比分板、天气图表等动态图形。
- **产品发布与展示**：为产品发布会创建可交互的3D动画和图形序列，并通过Media IO输出到外部设备。
- **广播级动态图形制作**：利用其设计师界面和丰富的组件（文本、形状、克隆效果器）快速创建高质量的动态图形资产。
- **需要实时交互与预览的媒体内容制作**：在编辑器内即可获得接近最终播出效果的实时预览，并可通过远程控制进行调整。

## 蓝图用法

蓝图功能主要通过场景子系统、特定组件和过渡逻辑库暴露。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IsReadyToPlay` | 检查Motion Design场景是否已准备好播放 | `UAvaSceneSubsystem` |
| `FlushBuilds` | 完成所有待处理的Motion Design构建系统工作（如Text3D） | `UAvaSceneSubsystem` |
| `GatherSceneTreeActors` | 按场景树顺序收集Actor | `UAvaSceneSubsystem` |
| `QueueActor` | 将指定Actor加入滚动队列 | `UAvaTickerComponent` |
| `SetStartLocation` / `SetVelocity` | 设置滚动队列的起始位置和移动速度 | `UAvaTickerComponent` |
| `AddTagAttribute` / `RemoveTagAttribute` | 在场景过渡逻辑中添加或移除标签属性 | `UAvaTransitionAttributeLibrary` |
| `CompareRCControllerValues` | 在过渡逻辑中比较远程控制控制器的值 | `UAvaTransitionRCLibrary` |

### 使用示例（蓝图描述）

1.  **查询场景状态**：在任何蓝图中，使用 `Get Game Instance` -> `Get Subsystem` -> `Ava Scene Subsystem`，然后调用 `IsReady To Play` 来判断当前世界是否是一个就绪的Motion Design场景。
2.  **控制滚动字幕**：将 `Ava Ticker Component` 添加到一个Actor上。在另一个蓝图中，获取该组件引用，调用 `Queue Actor` 将预制的字幕Actor加入队列，它会按照组件设定的速度自动滚动显示。
3.  **构建过渡逻辑**：在StateTree的状态节点中，使用 `Ava Transition Attribute Library` 的 `Add Tag Attribute` 节点，为当前场景的“退出”状态添加一个自定义标签，以便在其他条件中进行检查。

## C++ 用法

### 头文件引入

```cpp
// 获取场景子系统接口
#include "AvaSceneSubsystem.h"

// 访问场景接口
#include "IAvaSceneInterface.h"

// 使用滚动组件
#include "Framework/Ticker/AvaTickerComponent.h"

// 使用对齐和吸附点
#include "Viewport/Interaction/AvaSnapPoint.h"
```

### 基本用法

获取当前世界的Motion Design场景接口，并查询其状态和序列。

```cpp
// 假设在拥有UWorld的上下文中
UWorld* World = GetWorld();
if (World)
{
    // 获取场景子系统
    UAvaSceneSubsystem* SceneSubsystem = World->GetSubsystem<UAvaSceneSubsystem>();
    if (SceneSubsystem)
    {
        // 检查场景是否就绪
        bool bIsReady = SceneSubsystem->IsReadyToPlay(this);

        // 获取场景接口以访问详细数据
        IAvaSceneInterface* SceneInterface = SceneSubsystem->GetSceneInterface();
        if (SceneInterface)
        {
            // 获取场景设置
            UAvaSceneSettings* Settings = SceneInterface->GetSceneSettings();

            // 获取动画序列列表
            IAvaSequenceProvider* SequenceProvider = SceneInterface->GetSequenceProvider();
            if (SequenceProvider)
            {
                const TArray<TObjectPtr<UAvaSequence>>& Sequences = SequenceProvider->GetSequences();
                // ... 遍历或操作序列
            }

            // 获取远程控制预设
            URemoteControlPreset* RCPreSet = SceneInterface->GetRemoteControlPreset();
        }
    }
}
```
*（用法基于 `UAvaSceneSubsystem` 和 `IAvaSceneInterface` 的公共接口）*

### 进阶用法

为Actor添加并配置Motion Design Gizmo组件，以控制其渲染外观（如设为线框显示）。

```cpp
#include "Framework/AvaGizmoComponent.h"

AActor* TargetActor = /* ... */;
if (TargetActor)
{
    // 添加Gizmo组件
    UAvaGizmoComponent* GizmoComponent = NewObject<UAvaGizmoComponent>(TargetActor);
    GizmoComponent->RegisterComponent();
    TargetActor->AddInstanceComponent(GizmoComponent);

    // 配置Gizmo属性
    GizmoComponent->SetGizmoEnabled(true);
    GizmoComponent->SetShowWireframe(true);
    GizmoComponent->SetWireframeColor(FLinearColor::Red);
    GizmoComponent->SetCastShadow(false);
    GizmoComponent->SetHiddenInGame(true); // 仅在编辑器中显示

    // 应用设置到Actor的所有原始组件
    GizmoComponent->ApplyGizmoValues();
}
```
*（用法基于 `UAvaGizmoComponent` 的公共方法）*

## Demo 示例

一个最小示例，展示如何在C++中创建一个简单的Motion Design场景查询。

```cpp
// MyMotionDesignActor.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyMotionDesignActor.generated.h"

UCLASS()
class AMyMotionDesignActor : public AActor
{
    GENERATED_BODY()
public:
    AMyMotionDesignActor();
    virtual void BeginPlay() override;

private:
    void QueryMotionDesignScene();
};

// MyMotionDesignActor.cpp
#include "MyMotionDesignActor.h"
#include "AvaSceneSubsystem.h"
#include "IAvaSceneInterface.h"
#include "AvaSequenceProvider.h"

AMyMotionDesignActor::AMyMotionDesignActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyMotionDesignActor::BeginPlay()
{
    Super::BeginPlay();
    QueryMotionDesignScene();
}

void AMyMotionDesignActor::QueryMotionDesignScene()
{
    if (UWorld* World = GetWorld())
    {
        if (UAvaSceneSubsystem* Subsystem = World->GetSubsystem<UAvaSceneSubsystem>())
        {
            UE_LOG(LogTemp, Log, TEXT("Motion Design Scene Ready to Play: %s"), Subsystem->IsReadyToPlay(this) ? TEXT("Yes") : TEXT("No"));

            if (IAvaSceneInterface* Scene = Subsystem->GetSceneInterface())
            {
                if (IAvaSequenceProvider* SeqProvider = Scene->GetSequenceProvider())
                {
                    UE_LOG(LogTemp, Log, TEXT("Number of Animations in Scene: %d"), SeqProvider->GetSequences().Num());
                }
            }
        }
    }
}
```

## 模块依赖

要使用Avalanche插件，你的项目模块通常需要依赖其核心模块。以下是关键且独特的依赖项：

| 模块 | 用途 |
|---|---|
| `RemoteControl` | 用于通过远程控制API操作场景属性和预设 |
| `Sequencer` | 用于驱动和播放 `UAvaSequence` 动画序列 |
| `MediaCompositing` | 用于与媒体输出通道集成 |
| `MediaIOFramework` | 提供媒体输入输出的底层框架支持 |
| `ActorModifierCore` | 核心的Actor修改器系统，用于动态修改Actor属性 |
| `Text3D` | 提供3D文本组件支持 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own group | 将Motion Design的场景设置和大纲视图选项卡移至编辑器独立分组，优化界面组织。 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 使用Rundown页面设置时，新增了对电影渲染管线(MRQ)的使用分析数据收集。 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and added | 在节目控制工具栏中增加了页面加载选项（全部、下一个、选定），并增加了新功能。 |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 新增项目设置，可强制禁用Text3D和形状组件的碰撞。 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated with the viewport | 重构视口相关代码，通过通知客户端其与视口的关联状态来消除冗余代码。 |

### 维护评价

**活跃维护**。Avalanche插件于2025年5月从Experimental目录迁移至VirtualProduction，标志着其进入正式生产环境。从提交历史看，自2025年5月至2026年5月，开发团队持续且频繁地提交更新，内容涵盖新功能（如页面加载选项、MRQ分析）、用户体验优化（UI重组）、项目配置增强以及底层代码重构。这些更新表明该插件是Epic Games在虚拟制作领域重点投入并持续演进的核心组件之一，**强烈推荐**在相关的虚拟制作和动态图形项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [官方文档]() (在.uplugin中未提供)