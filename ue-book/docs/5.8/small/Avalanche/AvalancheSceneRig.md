# Motion Design

> Compositing, designer and broadcasting tool.

| 属性 | 值 |
|---|---|
| 中文名 | 动态图形设计 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（运行时代码） |
| 模块 | `Avalanche` (Runtime), `AvalancheSceneRig` (Runtime), `AvalancheMedia` (Runtime), `AvalancheOutliner` (Runtime), `AvalancheEditor` (Runtime), ... (共 43 个模块) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Motion Design (Avalanche) 是 Unreal Engine 虚拟制作工具集的核心组成部分，专为实时图形设计、合成与广播而构建。它解决的问题是如何在 UE 内高效地创建、编辑和播出复杂的动态图形（Motion Graphics），适用于电视广播、现场活动、虚拟演播室等场景。

该插件并非单一功能模块，而是一个包含数十个子模块的庞大生态系统。其核心功能包括：
1.  **场景绑定与管理**：通过 `SceneRig` 系统将特定类型的 Actor（如摄像机、灯光、几何体）组织到可管理的“场景装备”中，实现快速场景切换和准备。
2.  **媒体合成与播出**：集成媒体输入/输出、合成与播出控制，是虚拟制作中画面输出和信号管理的关键。
3.  **动态图形设计工具**：提供文本、形状、材质、特效器（Effectors）、克隆器（Cloners）、修改器（Modifiers）、属性动画（Property Animation）等一系列工具，用于创建复杂的 2D/3D 动态图形。
4.  **编辑器集成与工作流**：提供专用的大纲视图（Outliner）、视口（Viewport）、交互式工具（Interactive Tools）以及与 Sequencer、远程控制（Remote Control）、SVG 导入等系统的深度集成，优化设计师的创作流程。
5.  **渲染与输出**：支持通过 Movie Render Queue (MRQ) 进行高质量最终输出。

它的存在是为了填补 UE 在专业广播级动态图形实时设计与播出方面的空白，将传统离线图形工作站的工作流整合到实时引擎环境中。

## 使用场景

-   **你在为虚拟演播室或电视直播节目设计动态图形、下三分之一标题（Lower Thirds）、转场和全屏插件** → 使用 Motion Design 的文本、形状、材质和动画工具。
-   **你需要为现场活动（如演唱会、发布会）创建和管理复杂的多机位场景** → 使用 `SceneRig` 系统来快速准备和切换场景配置。
-   **你需要将外部视频源、NDI 信号或实时生成的图形合成到最终输出画面中** → 使用 `AvalancheMedia` 和相关合成模块。
-   **你需要批量制作大量基于模板的动态图形变体** → 结合 `ClonerEffector` 和 `PropertyAnimator`。
-   **你需要一个统一的编辑器环境来管理所有动态图形元素，并与场景、摄像机、Sequencer 时间线无缝协作** → 使用 Motion Design 专用的编辑器组件，如大纲视图和视口工具。

## 蓝图用法

由于 Motion Design 是一个庞大的插件，其蓝图 API 分布在多个子模块中。以 `AvalancheSceneRig` 子模块为例，展示其核心节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ForWorld` | 获取指定 `UWorld` 的场景绑定子系统实例。 | `UAvaSceneRigSubsystem` |
| `IsSceneRigAsset` | 判断给定对象是否为场景绑定（Scene Rig）资产。 | `UAvaSceneRigSubsystem` |
| `GetSceneRigAssetSuffix` | 获取用于区分场景绑定关卡资产的后缀字符串。 | `UAvaSceneRigSubsystem` |
| `RegisterSupportedActorClasses` | 注册允许添加到场景绑定中的 Actor 类。 | `UAvaSceneRigSubsystem` |
| `FindFirstActiveSceneRig` | 在持久关卡中查找第一个活动的场景绑定流送关卡。 | `UAvaSceneRigSubsystem` |
| `SceneRigFromActor` | 获取指定 Actor 所属的活动场景绑定。 | `UAvaSceneRigSubsystem` |
| `AreActorsSupported` | 检查给定的 Actor 列表是否都属于受支持的场景绑定类。 | `UAvaSceneRigSubsystem` |

### 使用示例（蓝图描述）

1.  **获取子系统**：在任何需要操作场景绑定的蓝图（如关卡蓝图或 Actor 蓝图）中，使用 `For World` 节点，传入 `Get World` 的结果，获取 `UAvaSceneRigSubsystem` 的引用。
2.  **查找活动场景**：使用该子系统引用调用 `Find First Active Scene Rig` 节点，可以获取当前世界中活动的场景绑定流送关卡对象。
3.  **查询 Actor 归属**：使用 `Scene Rig From Actor` 节点，传入某个 Actor（例如玩家摄像机或特定的动态图形 Actor），可以查询它是否属于某个活动的场景绑定。
4.  **自定义受支持的类**：在游戏初始化时，可以使用 `Register Supported Actor Classes` 节点，传入一个包含您自定义的、希望能在场景绑定中使用的 Actor 类集合（例如，一个特殊的灯光 Actor 类）。

## C++ 用法

重点从 `AvalancheSceneRig` 子模块的 API 文档和用法模式中提取。

### 头文件引入

```cpp
#include "AvaSceneRigSubsystem.h"
#include "AvaSceneRigAssetTags.h" // 如果需要使用资产标签常量
```

### 基本用法

获取子系统并查询当前世界的活动场景绑定。

```cpp
// 假设代码位于一个有效的 UWorld 上下文中（例如，Actor 的 BeginPlay）
UWorld* World = GetWorld();
if (World)
{
    // 获取场景绑定子系统
    UAvaSceneRigSubsystem* SceneRigSubsystem = UAvaSceneRigSubsystem::ForWorld(World);
    if (SceneRigSubsystem)
    {
        // 查找第一个活动的场景绑定关卡
        ULevelStreaming* ActiveSceneRig = SceneRigSubsystem->FindFirstActiveSceneRig();
        if (ActiveSceneRig)
        {
            UE_LOG(LogTemp, Log, TEXT("找到了活动场景绑定关卡: %s"), *ActiveSceneRig->GetWorldAssetPackageName());
        }

        // 检查某个 Actor 是否属于场景绑定
        AActor* SomeActor = /* ... */;
        if (SomeActor && SceneRigSubsystem->IsActiveSceneRigActor(SomeActor))
        {
            UE_LOG(LogTemp, Log, TEXT("Actor %s 是当前活动场景绑定的一部分。"), *SomeActor->GetName());
        }
    }
}
```
*（来源：基于 `AvaSceneRigSubsystem.h` 中的公开 API 推断的典型用法）*

### 进阶用法

动态注册自定义 Actor 类到受支持的场景绑定类列表中，并遍历所有活动场景绑定中的 Actor。

```cpp
// 在某个初始化模块（如游戏模块或自定义子系统）中
void UMyGameModule::StartupModule()
{
    // 定义一个包含自定义 Actor 类的集合
    TSet<TSubclassOf<AActor>> CustomActorClasses;
    CustomActorClasses.Add(AMySpecialLight::StaticClass());
    CustomActorClasses.Add(AMyDynamicBillboard::StaticClass());

    // 注册到全局的场景绑定子系统支持列表中
    UAvaSceneRigSubsystem::RegisterSupportedActorClasses(CustomActorClasses);
}

void UMyGameModule::ShutdownModule()
{
    // 取消注册
    TSet<TSubclassOf<AActor>> CustomActorClasses;
    CustomActorClasses.Add(AMySpecialLight::StaticClass());
    CustomActorClasses.Add(AMyDynamicBillboard::StaticClass());
    UAvaSceneRigSubsystem::UnregisterSupportedActorClasses(CustomActorClasses);
}

// 在游戏逻辑中，遍历并操作活动场景绑定内的所有 Actor
void AMyManagerActor::ProcessActiveSceneRigActors()
{
    UAvaSceneRigSubsystem* Subsystem = UAvaSceneRigSubsystem::ForWorld(GetWorld());
    if (Subsystem)
    {
        // 使用 ForEachActiveSceneRigActor 遍历
        Subsystem->ForEachActiveSceneRigActor([](AActor* const InActor)
        {
            // 对每个 Actor 执行操作，例如调整其材质参数
            if (UStaticMeshComponent* MeshComp = InActor->FindComponentByClass<UStaticMeshComponent>())
            {
                // ... 修改材质
            }
        });
    }
}
```
*（来源：结合 `AvaSceneRigSubsystem.h` 中的静态注册/注销函数与实例遍历函数的用法示例）*

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何创建一个 Actor，其 BeginPlay 函数会查询并打印当前活动场景绑定的信息。

```cpp
// MySceneRigReaderActor.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MySceneRigReaderActor.generated.h"

UCLASS()
class AMySceneRigReaderActor : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
};

// MySceneRigReaderActor.cpp
#include "MySceneRigReaderActor.h"
#include "AvaSceneRigSubsystem.h"

void AMySceneRigReaderActor::BeginPlay()
{
    Super::BeginPlay();

    if (HasAuthority()) // 通常只在服务器或单机端执行查询
    {
        UAvaSceneRigSubsystem* SRSubsystem = UAvaSceneRigSubsystem::ForWorld(GetWorld());
        if (SRSubsystem)
        {
            ULevelStreaming* ActiveRig = SRSubsystem->FindFirstActiveSceneRig();
            if (ActiveRig)
            {
                UE_LOG(LogTemp, Display, TEXT("Actor [%s] 在 BeginPlay 时检测到活动场景绑定: [%s]"),
                    *GetName(),
                    *ActiveRig->GetWorldAssetPackageName());
            }
            else
            {
                UE_LOG(LogTemp, Display, TEXT("Actor [%s] 在 BeginPlay 时未找到活动场景绑定。"), *GetName());
            }
        }
    }
}
```

## 模块依赖

`Avalanche` 插件本身依赖众多其他 UE 模块和插件。作为使用者，在你的 `Build.cs` 中需要根据你使用的具体功能添加依赖。以下是关键依赖（已省略 Core, CoreUObject, Engine 等常见依赖）：

| 模块 | 用途 |
|---|---|
| `Sequencer` | 动画序列编辑器，用于时间线动画和场景绑定。 |
| `MediaIOCore`, `MediaIOFramework` | 媒体输入输出框架，用于捕获和发送视频信号。 |
| `MediaCompositing` | 媒体合成，用于将外部视频源混合到场景中。 |
| `GeometryScriptingCore` | 几何体脚本，为动态图形修改器提供程序化几何体操作能力。 |
| `MeshModelingToolsetExp` | 网格建模工具集，用于高级几何体创建和编辑。 |
| `RemoteControlAPI`, `RemoteControl` | 远程控制 API，允许从外部控制场景属性。 |
| `SVGImporter` | SVG 导入器，支持导入矢量图形资产。 |
| `Text3D` | 3D 文本组件，用于创建立体文字。 |
| `CustomDetailsView` | 自定义细节面板视图，用于创建复杂的属性编辑界面。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将场景设置和大纲视图标签页移至独立的编辑器选项卡组，优化布局。 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 为使用节目单页面设置时添加了 Movie Render Queue (MRQ) 分析功能。 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 在播出控制工具栏中添加了页面加载选项（全部、下一个、选中），并新增了相关功能。 |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 新增项目设置，可强制禁用 Text3D 和形状的碰撞检测。 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构视口客户端关联通知逻辑，减少重复代码。 |

### 维护评价

Motion Design (Avalanche) 是一个**积极维护中**的大型虚拟制作工具集。

-   **活跃度**：从最近的提交记录（截至 2026 年 5 月）可以看出，Epic Games 的团队在持续为其添加新功能（如 MRQ 分析、页面加载选项）和优化现有工作流（如编辑器布局调整）。
-   **重要性**：作为虚拟制作的核心插件之一，它集成了媒体、图形、动画和控制等多个关键领域，是实时动态图形和广播工作流的基石。
-   **状态**：插件最初来源于多个实验性插件（如 ClonerEffector, PropertyAnimator 等）的整合，并于 2025 年正式迁移至 `VirtualProduction` 目录，标志着其从实验性转向生产就绪状态。
-   **推荐使用**：**强烈推荐**用于任何涉及虚拟制作、动态图形设计、实时合成或广播控制的 UE 项目。由于其复杂性和模块众多，建议用户根据具体需求逐步引入相关子模块。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [AvalancheSceneRig 模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheSceneRig)