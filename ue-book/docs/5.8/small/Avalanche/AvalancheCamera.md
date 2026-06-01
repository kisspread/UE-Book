# Motion Design

> Compositing, designer and broadcasting tool.
> 
> Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 动作设计 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（完整创作套件，包含大量模块、编辑器工具及资产） |
| 模块 | `Avalanche` (Runtime), `AvalancheAttribute` (Runtime), `AvalancheAttributeEditor` (Runtime), `AvalancheCamera` (Runtime), `AvalancheComponentVisualizers` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), `AvalancheEditorCore` (Runtime), `AvalancheEffectors` (Runtime), `AvalancheEffectorsEditor` (Runtime), `AvalancheFunctionalTest` (Runtime), `AvalancheInteractiveTools` (Runtime), `AvalancheInteractiveToolsRuntime` (Runtime), `AvalancheLevelViewport` (Runtime), `AvalancheMRQ` (Runtime), `AvalancheMRQEditor` (Runtime), `AvalancheMask` (Runtime), `AvalancheMaskEditor` (Runtime), `AvalancheMaterial` (Runtime), `AvalancheMedia` (Runtime), `AvalancheMediaEditor` (Runtime), `AvalancheModifiers` (Runtime), `AvalancheModifiersEditor` (Runtime), `AvalancheOutliner` (Runtime), `AvalanchePropertyAnimator` (Runtime), `AvalanchePropertyAnimatorEditor` (Runtime), `AvalancheRemoteControl` (Runtime), `AvalancheRemoteControlEditor` (Runtime), `AvalancheSVGEditor` (Runtime), `AvalancheSceneRig` (Runtime), `AvalancheSceneRigEditor` (Runtime), `AvalancheSceneTree` (Runtime), `AvalancheSequence` (Runtime), `AvalancheSequencer` (Runtime), `AvalancheShapes` (Runtime), `AvalancheShapesEditor` (Runtime), `AvalancheTag` (Runtime), `AvalancheTagEditor` (Runtime), `AvalancheText` (Runtime), `AvalancheTextEditor` (Runtime), `AvalancheTransition` (Runtime), `AvalancheTransitionEditor` (Runtime), `AvalancheViewport` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

**Motion Design (Avalanche)** 是一个为**虚拟制作（Virtual Production）**和**现场广播**打造的综合性内容创作套件。它远不止于一个简单的工具，而是一个完整的**设计环境**和**播放控制**框架。

该插件旨在解决以下核心问题：
1.  **动态内容创作**：为广播和现场活动快速创建、编辑和预演复杂的2D/3D动态图形、UI和场景布局。
2.  **实时场景切换与播放**：管理多个“场景”（Scenes）或“页面”（Pages），并通过时间轴或触发器控制它们之间的切换、过渡和效果。
3.  **资产与属性动画**：内置了对3D文字、基本形状、SVG、材质、克隆/效果器等资产的创建和动画支持，并提供了强大的属性动画系统。
4.  **媒体集成与编排**：集成了媒体播放、IO框架，允许将视频源、摄像头输入无缝合成到场景中。
5.  **远程控制与同步**：通过Remote Control等模块支持远程操控和多设备同步（StormSync），适用于复杂的现场制作环境。

其下的子模块 `AvalancheCamera` 具体负责管理广播场景中的摄像机视图，允许在不同的“场景”切换时，自动混合和过渡虚拟摄像机的位置和视角。

## 使用场景

-   **电视节目/直播制作**：制作动态节目包装、片头片尾、实时比分板、观众互动UI等。
-   **虚拟演唱会/舞台活动**：控制虚拟背景、灯光、特效和虚拟摄像机位。
-   **多机位虚拟制作**：在绿幕拍摄中，实时预览和切换不同虚拟环境与摄像机角度。
-   **数据可视化与演示**：创建交互式的数据仪表盘或产品演示场景。
-   **任何需要实时、动态、可序列化内容输出的项目**，超越了传统静态场景编辑的范畴。

## 蓝图用法

> **注意**：Motion Design 是一个极其庞大的插件体系。以下仅列出 **AvalancheCamera** 子模块中可公开访问的核心蓝图节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RegisterScene` | 向摄像机子系统注册一个关卡（场景），使其能够参与视图目标的混合计算。 | `UAvaCameraSubsystem` |
| `UnregisterScene` | 取消注册一个关卡，停止其对视图目标的影响。 | `UAvaCameraSubsystem` |
| `ConditionallyUpdateViewTarget` | （静态）尝试根据当前的场景状态和优先级，有条件地更新玩家的摄像机视图目标。通常用于过渡逻辑中。 | `UAvaCameraSubsystem` |
| `ConditionallyUpdateViewTarget` | （静态库函数）在过渡节点中调用，尝试执行视图目标更新。 | `UAvaTransitionCameraLibrary` |
| `Priority` | （属性）在 Actor 修改器上设置的摄像机优先级，用于决定当多个场景同时存在时，哪个场景的摄像机应该生效。 | `UAvaCameraPriorityModifier` |
| `TransitionParams` | （属性）在 Actor 修改器上设置的摄像机混合过渡参数（如淡入时间、插值函数）。 | `UAvaCameraPriorityModifier` |

### 使用示例（蓝图描述）

**示例：创建一个高优先级的虚拟摄像机**
1.  在场景中的一个 Actor（例如一个 `PlayerStart` 或空的 `Actor`）上，添加 `UAvaCameraPriorityModifier` 组件。
2.  在该组件的细节面板中，将 `Priority` 设置为一个较高的值（如 100）。
3.  调整 `TransitionParams` 中的 `BlendTime` 来控制切换到此视角时的过渡时间。
4.  当你的 Motion Design 场景被激活时，`UAvaCameraSubsystem` 会自动评估所有已注册场景的 Actor 上的 `UAvaCameraPriorityModifier`，并将玩家视图平滑地过渡到优先级最高的那个 Actor 所代表的虚拟摄像机位置。

**示例：在过渡逻辑中强制更新视图**
在一个 `FAvaCameraBlendTask` 状态树任务（用于管理场景切换过渡）中，其 `EnterState` 和 `Tick` 函数内部会调用 `UAvaCameraSubsystem::ConditionallyUpdateViewTarget` 来驱动摄像机的混合过程。

## C++ 用法

### 头文件引入

```cpp
#include "AvaCameraSubsystem.h"
#include "AvaCameraPriorityModifier.h"
```

### 基本用法

以下示例展示了如何在 C++ 中与 `AvalancheCamera` 子系统交互。
*来源：`Public/AvaCameraSubsystem.h`*

```cpp
// 在游戏逻辑中，获取当前世界的摄像机子系统
UAvaCameraSubsystem* CameraSubsystem = UAvaCameraSubsystem::Get(MyWorldContextObject);
if (CameraSubsystem)
{
    // 当某个“场景”关卡加载时，向系统注册
    ULevel* SceneLevel = GetLoadedSceneLevel(); // 假设的函数
    CameraSubsystem->RegisterScene(SceneLevel);

    // ... 场景运行 ...

    // 当场景卸载时，取消注册
    CameraSubsystem->UnregisterScene(SceneLevel);
}
```

### 进阶用法

创建一个自定义的 Actor，使其能够通过优先级影响摄像机系统。
*来源：`Public/AvaCameraPriorityModifier.h`*

```cpp
// 在你的 Actor 类中，可以动态添加或操作相机优先级修改器
// 假设我们有一个 AMyBroadcastActor 类
void AMyBroadcastActor::EnableHighPriorityCamera()
{
    // 查找或创建相机优先级修改器组件
    UAvaCameraPriorityModifier* CamModifier = FindComponentByClass<UAvaCameraPriorityModifier>();
    if (!CamModifier)
    {
        CamModifier = NewObject<UAvaCameraPriorityModifier>(this);
        CamModifier->RegisterComponent();
    }

    // 设置高优先级和自定义过渡参数
    FViewTargetTransitionParams TransitionParams;
    TransitionParams.BlendTime = 2.0f; // 2秒淡入
    TransitionParams.BlendFunction = VTBlend_EaseInOut;
    // 注意：这些属性通常在编辑器中设置。在运行时，你需要通过修改器的实例来设置（可能需要暴露 setter 或使用特定API）。
    // CamModifier->SetPriority(100);
    // CamModifier->SetTransitionParams(TransitionParams);
}
```

## Demo 示例

一个最小的示例，演示如何创建一个拥有自定义摄像机优先级的 Actor。
```cpp
// MyBroadcastSpotlight.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "AvaCameraPriorityModifier.h"
#include "MyBroadcastSpotlight.generated.h"

UCLASS()
class AMyBroadcastSpotlight : public AActor
{
    GENERATED_BODY()

public:
    AMyBroadcastSpotlight();

    // 暴露给蓝图和编辑器，用于调整优先级
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Broadcast")
    int32 CameraPriority = 50;

protected:
    // 相机组件，用于定义该 Actor 在场景中的虚拟摄像机位置
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Broadcast")
    UCameraComponent* VirtualCamera;

    // 相机优先级修改器组件，将 Actor 注册到 Motion Design 相机系统
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Broadcast")
    UAvaCameraPriorityModifier* CameraPriorityModifier;
};

// MyBroadcastSpotlight.cpp
#include "MyBroadcastSpotlight.h"
#include "Camera/CameraComponent.h"

AMyBroadcastSpotlight::AMyBroadcastSpotlight()
{
    // 创建根组件和虚拟摄像机
    VirtualCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("VirtualCamera"));
    RootComponent = VirtualCamera;

    // 创建并附加相机优先级修改器
    CameraPriorityModifier = CreateDefaultSubobject<UAvaCameraPriorityModifier>(TEXT("CameraPriority"));
    CameraPriorityModifier->SetupAttachment(RootComponent);
}
```

## 模块依赖

`Avalanche` 插件是一个庞大的套件，其依赖关系复杂。`AvalancheCamera` 模块作为其中一部分，除了标准核心模块外，主要依赖于插件自身的其他子系统和 Epic 的状态树/ Actor 修改器框架。

| 模块 | 用途 |
|---|---|
| `Sequencer` | 用于将相机过渡和动画集成到 Sequencer 时间轴中。 |
| `StateTree` | `FAvaCameraBlendTask` 是一个状态树任务，用于在状态逻辑中驱动相机混合。 |
| `ActorModifierCore` | `UAvaCameraPriorityModifier` 继承自 `UActorModifierCoreBase`，这是实现 Actor 修改器功能的基础框架。 |
| `AvalancheTransition` | 相机混合逻辑通常作为场景过渡（Transition）的一部分被触发和执行。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own group | 将 Motion Design 的标签页在关卡编辑器中归类到独立分组，优化了UI组织。 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 当使用节目单页面设置时，增加了MRQ（Movie Render Queue）的分析数据收集。 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and added... | 为节目控制工具栏添加了页面加载选项（全部、下一个、选中项），并增加了相关功能。 |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 增加了一个项目设置，可以强制禁用3D文字和形状的碰撞。 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it or its associated player is created or destroyed | 重构了视口代码，通过客户端通知机制替代了部分重复代码，提升了代码整洁度。 |

### 维护评价

**✅ 活跃维护中**
-   **创建时间**：约1年前（2025年5月），是一个相对较新的大型功能插件。
-   **更新频率**：从 git 历史看，在 2026 年 5 月仍有**密集的功能性更新**（新功能、UI改进、设置项添加），表明处于**积极开发和迭代期**。
-   **代码质量**：插件从 Experimental 目录迁移至正式的 VirtualProduction 目录，表明其已通过 Epic 的内部评估，达到了一定的稳定性和成熟度。
-   **推荐**：**强烈推荐**给所有涉及**虚拟制作**和**广播**领域的项目。它是 Epic 官方为该领域提供的核心创作工具链之一。由于其规模庞大，建议从官方示例项目或文档开始学习。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/motion-design-in-unreal-engine/)