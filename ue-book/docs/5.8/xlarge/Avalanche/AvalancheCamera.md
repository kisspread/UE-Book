# Motion Design

> Compositing, designer and broadcasting tool.
> Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 动效设计 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（运动设计工具集、场景构建器、媒体合成工具、远程控制、材质设计器等） |
| 模块 | `Avalanche` (Runtime), `AvalancheAttribute` (Runtime), `AvalancheAttributeEditor` (Runtime), `AvalancheCamera` (Runtime), `AvalancheComponentVisualizers` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), `AvalancheEditorCore` (Runtime), `AvalancheEffectors` (Runtime), `AvalancheEffectorsEditor` (Runtime), `AvalancheFunctionalTest` (Runtime), `AvalancheInteractiveTools` (Runtime), `AvalancheInteractiveToolsRuntime` (Runtime), `AvalancheLevelViewport` (Runtime), `AvalancheMRQ` (Runtime), `AvalancheMRQEditor` (Runtime), `AvalancheMask` (Runtime), `AvalancheMaskEditor` (Runtime), `AvalancheMaterial` (Runtime), `AvalancheMedia` (Runtime), `AvalancheMediaEditor` (Runtime), `AvalancheModifiers` (Runtime), `AvalancheModifiersEditor` (Runtime), `AvalancheOutliner` (Runtime), `AvalanchePropertyAnimator` (Runtime), `AvalanchePropertyAnimatorEditor` (Runtime), `AvalancheRemoteControl` (Runtime), `AvalancheRemoteControlEditor` (Runtime), `AvalancheSVGEditor` (Runtime), `AvalancheSceneRig` (Runtime), `AvalancheSceneRigEditor` (Runtime), `AvalancheSceneTree` (Runtime), `AvalancheSequence` (Runtime), `AvalancheSequencer` (Runtime), `AvalancheShapes` (Runtime), `AvalancheShapesEditor` (Runtime), `AvalancheTag` (Runtime), `AvalancheTagEditor` (Runtime), `AvalancheText` (Runtime), `AvalancheTextEditor` (Runtime), `AvalancheTransition` (Runtime), `AvalancheTransitionEditor` (Runtime), `AvalancheViewport` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Avalanche（内部代号 Motion Design）是一个为**虚拟制作**和**广播**场景打造的大型、集成化的运动设计工具集。它并非单一功能的插件，而是一个包含场景构建、动效设计、媒体合成、远程控制、材质设计、形状与文本创建等数十个子模块的**平台级插件**。

该插件从原先的实验性目录迁移而来，旨在为UE提供一套专业级的、类似After Effects或C4D的图形设计与直播控制工作流。它解决了将复杂的动态图形、实时合成与场景过渡无缝集成到虚拟制作流水线中的问题，主要面向电视节目、直播活动、虚拟场景和动态图形包装等应用场景。

## 使用场景

- 你需要为虚拟演播室或直播活动设计和控制复杂的动态图形、场景过渡和合成效果 → 使用 Motion Design 提供的完整工具链。
- 你需要在UE中进行非线性编辑、时间轴控制和场景序列管理 → 使用 `AvalancheSequence`, `AvalancheSequencer` 等模块。
- 你需要创建和编辑自定义的3D形状、文本、材质和SVG图形，并实时应用动效 → 使用 `AvalancheShapes`, `AvalancheText`, `AvalancheMaterial`, `AvalancheSVGEditor` 等模块。
- 你需要远程控制UE场景中的参数，实现现场直播的快速调整 → 使用 `AvalancheRemoteControl` 模块。
- 你需要精细控制场景过渡期间的相机行为，实现平滑的镜头切换 → 使用 `AvalancheCamera` 模块。
- 你需要将多个工具（如克隆器、效果器、属性动画器、修改器）组合起来，创建复杂的程序化动效和场景修改 → 使用 `AvalancheEffectors`, `AvalanchePropertyAnimator`, `AvalancheModifiers` 等模块。

## 蓝图用法

### 核心节点（相机与过渡）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get` | 获取当前世界对应的 Motion Design 相机子系统单例 | `UAvaCameraSubsystem` |
| `RegisterScene` | 注册一个关卡，使其参与到 Motion Design 的相机优先级计算中 | `UAvaCameraSubsystem` |
| `UnregisterScene` | 取消一个关卡的注册 | `UAvaCameraSubsystem` |
| `UpdatePlayerControllerViewTarget` | 根据当前注册场景中所有 Actor 的优先级，更新玩家控制器的视角目标（相机） | `UAvaCameraSubsystem` |
| `ConditionallyUpdateViewTarget` | 条件性地更新视角目标，通常在场景过渡逻辑中调用 | `UAvaTransitionCameraLibrary` |
| `GetPriority` | 获取关联 Actor 上的相机优先级（来自 `UAvaCameraPriorityModifier`） | `FAvaViewTarget` |

### 使用示例（蓝图描述）

1.  **场景启动时注册相机子系统**：
    - 在关卡蓝图（Level Blueprint）的 `BeginPlay` 事件中，获取 `UAvaCameraSubsystem` 的实例，并调用 `RegisterScene` 节点，将当前关卡（`Get Level`）作为输入进行注册。
2.  **控制场景过渡时的相机切换**：
    - 在场景过渡蓝图（State Tree 或自定义过渡逻辑）中，使用 `ConditionallyUpdateViewTarget` 节点。将过渡节点的引用（`self`）作为 `InTransitionNode` 输入。该节点内部会查询 `UAvaCameraSubsystem` 来决定是否切换相机。
3.  **为Actor设置相机优先级**：
    - 为需要成为相机目标的 Actor 添加一个 `UAvaCameraPriorityModifier` 组件（通过“添加组件”菜单搜索“Motion Design Camera Priority”）。
    - 在修改器的详情面板中设置 `Priority`（整数，越高越优先）和 `TransitionParams`（混合时间、混合函数等）。

## C++ 用法

### 头文件引入

```cpp
#include "AvaCameraSubsystem.h"
#include "AvaCameraPriorityModifier.h"
#include "AvaTransitionCameraLibrary.h"
```

### 基本用法

以下示例展示了如何在代码中获取相机子系统并响应场景过渡。

```cpp
// 来源: Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheCamera/Public/AvaCameraSubsystem.h
// 在任何需要访问相机子系统的地方
UAvaCameraSubsystem* CameraSubsystem = UAvaCameraSubsystem::Get(GetWorld());
if (CameraSubsystem)
{
    // 注册当前关卡（通常在关卡初始化时调用）
    CameraSubsystem->RegisterScene(GetLevel());

    // 手动触发一次视角目标更新（例如，在用户操作后）
    CameraSubsystem->UpdatePlayerControllerViewTarget();
}

// 来源: Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheCamera/Private/Transition/AvaTransitionCameraLibrary.h
// 在过渡逻辑（例如 State Tree 任务）中调用
bool bViewTargetUpdated = UAvaTransitionCameraLibrary::ConditionallyUpdateViewTarget(this);
```

### 进阶用法

自定义一个 State Tree 任务来驱动相机混合。

```cpp
// 来源: Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheCamera/Public/Transition/Tasks/AvaCameraBlendTask.h
// 1. 创建一个继承自 FAvaTransitionTask 的任务结构体
USTRUCT(DisplayName="My Custom Camera Blend Task")
struct FMyCameraBlendTask : public FAvaTransitionTask
{
    GENERATED_BODY()

    // ... (省略部分固定框架代码)

    virtual EStateTreeRunStatus EnterState(FStateTreeExecutionContext& InContext, const FStateTreeTransitionResult& InTransition) const override
    {
        // 获取相机子系统数据
        const UAvaCameraSubsystem* CameraSubsystem = InContext.GetExternalData(CameraSubsystemHandle);
        const ULevel* TransitionLevel = GetTransitionLevel(InContext);

        if (CameraSubsystem && TransitionLevel && CameraSubsystem->ConditionallyUpdateViewTarget(TransitionLevel))
        {
            return EStateTreeRunStatus::Running; // 正在混合
        }
        return EStateTreeRunStatus::Succeeded;
    }

    virtual EStateTreeRunStatus Tick(FStateTreeExecutionContext& InContext, const float InDeltaTime) const override
    {
        // 检查混合是否完成
        const UAvaCameraSubsystem* CameraSubsystem = InContext.GetExternalData(CameraSubsystemHandle);
        const ULevel* TransitionLevel = GetTransitionLevel(InContext);
        if (CameraSubsystem && !CameraSubsystem->IsBlendingToViewTarget(TransitionLevel))
        {
            return EStateTreeRunStatus::Succeeded;
        }
        return EStateTreeRunStatus::Running;
    }
};
```

## Demo 示例

一个最小的可编译示例，展示如何与 `AvalancheCamera` 模块交互。

**MyCameraManager.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "MyCameraManager.generated.h"

class UAvaCameraSubsystem;

UCLASS()
class UMyCameraManager : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

    UFUNCTION(BlueprintCallable)
    void SetupMotionDesignCameraForLevel(ULevel* InLevel);

private:
    FDelegateHandle OnWorldBeginPlayHandle;
    UPROPERTY()
    TWeakObjectPtr<UAvaCameraSubsystem> CachedCameraSubsystem;
};
```

**MyCameraManager.cpp**
```cpp
#include "MyCameraManager.h"
#include "AvaCameraSubsystem.h"
#include "Engine/World.h"

void UMyCameraManager::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    // 监听世界开始播放的事件，以延迟初始化相机子系统引用
    if (UWorld* World = GetWorld())
    {
        OnWorldBeginPlayHandle = World->OnWorldBeginPlay.AddUObject(this, &UMyCameraManager::SetupMotionDesignCameraForLevel, World->PersistentLevel);
    }
}

void UMyCameraManager::Deinitialize()
{
    if (UWorld* World = GetWorld())
    {
        World->OnWorldBeginPlay.Remove(OnWorldBeginPlayHandle);
    }
    CachedCameraSubsystem.Reset();
    Super::Deinitialize();
}

void UMyCameraManager::SetupMotionDesignCameraForLevel(ULevel* InLevel)
{
    if (InLevel)
    {
        UAvaCameraSubsystem* CameraSubsystem = UAvaCameraSubsystem::Get(InLevel);
        if (CameraSubsystem)
        {
            CachedCameraSubsystem = CameraSubsystem;
            // 为指定关卡注册 Motion Design 相机系统
            CameraSubsystem->RegisterScene(InLevel);
            UE_LOG(LogTemp, Log, TEXT("Motion Design Camera Subsystem registered for level: %s"), *InLevel->GetOuter()->GetName());
        }
    }
}
```

## 模块依赖

Avalanche 是一个庞大的插件集，其模块依赖众多且复杂。以下是其**独特**的核心依赖（除了标准的 Core/Engine/Slate 等）：

| 模块 | 用途 |
|---|---|
| `MediaIOFramework` | 媒体输入输出框架，用于捕获和播放外部视频/音频信号 |
| `MediaCompositing` | 媒体合成，用于将媒体纹理与其他场景元素分层合成 |
| `RemoteControl` | 远程控制，用于通过API或UI远程调整引擎内的属性 |
| `GeometryCache` | 几何体缓存，用于存储和播放预计算的动画网格体 |
| `GeometryScripting` | 几何体脚本，用于程序化创建和修改几何体 |
| `MeshModelingToolsetExp` | 网格建模工具集（实验版），提供高级建模操作 |
| `Text3D` | 3D文本，用于在场景中创建和渲染3D文字 |
| `ActorModifierCore` | Actor修改器核心，为Avalanche的修改器（如相机优先级修改器）提供基础框架 |
| `StateTree` | 状态树，被用于驱动复杂的场景过渡逻辑（如相机混合任务） |
| `Sequencer` | 定序器，与 `AvalancheSequence` 模块紧密集成，用于时间轴编辑 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将动效设计面板（场景设置、大纲）移至独立分组，优化编辑器布局 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 在使用节目单页面设置时添加了 MRQ 分析功能 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 在节目控制工具栏中添加了页面加载选项（全部、下一个、选中项） |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 添加了项目设置，用于强制禁用 Text3D 和形状的碰撞检测 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构了视口相关代码，通过客户端通知简化了关联/解除关联逻辑 |

### 维护评价

**积极维护中**。Avalanche 插件非常年轻（约1年），但自首次提交以来，保持着非常高的更新频率（最近一周内有多次提交）。从提交记录看，开发团队正在**非常活跃**地开发新功能（如节目单控制、分析功能）、优化编辑器UI/UX（面板布局调整）、修复问题（碰撞设置、代码重构）并提升性能。

该插件是 Epic 为虚拟制作领域布局的核心产品之一，预计将持续获得大量投入。**强烈推荐**在虚拟制作、动态图形和广播项目中使用，但需要注意其庞大的模块体系可能带来较高的学习曲线和包体体积。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/motion-design-in-unreal-engine)（预计将在此发布）