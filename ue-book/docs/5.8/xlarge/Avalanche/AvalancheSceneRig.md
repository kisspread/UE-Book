# Motion Design

> Compositing, designer and broadcasting tool.

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、工具、预设、测试） |
| 模块 | `Avalanche` (Runtime), `AvalancheAttribute` (Runtime), `AvalancheAttributeEditor` (Runtime), `AvalancheCamera` (Runtime), `AvalancheComponentVisualizers` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), `AvalancheEditorCore` (Runtime), `AvalancheEffectors` (Runtime), `AvalancheEffectorsEditor` (Runtime), `AvalancheFunctionalTest` (Runtime), `AvalancheInteractiveTools` (Runtime), `AvalancheInteractiveToolsRuntime` (Runtime), `AvalancheLevelViewport` (Runtime), `AvalancheMRQ` (Runtime), `AvalancheMRQEditor` (Runtime), `AvalancheMask` (Runtime), `AvalancheMaskEditor` (Runtime), `AvalancheMaterial` (Runtime), `AvalancheMedia` (Runtime), `AvalancheMediaEditor` (Runtime), `AvalancheModifiers` (Runtime), `AvalancheModifiersEditor` (Runtime), `AvalancheOutliner` (Runtime), `AvalanchePropertyAnimator` (Runtime), `AvalanchePropertyAnimatorEditor` (Runtime), `AvalancheRemoteControl` (Runtime), `AvalancheRemoteControlEditor` (Runtime), `AvalancheSVGEditor` (Runtime), `AvalancheSceneRig` (Runtime), `AvalancheSceneRigEditor` (Runtime), `AvalancheSceneTree` (Runtime), `AvalancheSequence` (Runtime), `AvalancheSequencer` (Runtime), `AvalancheShapes` (Runtime), `AvalancheShapesEditor` (Runtime), `AvalancheTag` (Runtime), `AvalancheTagEditor` (Runtime), `AvalancheText` (Runtime), `AvalancheTextEditor` (Runtime), `AvalancheTransition` (Runtime), `AvalancheTransitionEditor` (Runtime), `AvalancheViewport` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Avalanche（Motion Design）是 Unreal Engine 为虚拟制作（Virtual Production）和广播领域打造的一套综合性创作工具集。它解决的核心问题是：在虚幻引擎中进行实时、非线性、数据驱动的视觉内容创作、合成与播出。

与传统的游戏开发或线性影片制作不同，虚拟制作和广播需要高度的灵活性、实时预览能力以及对复杂场景元素的精细控制。Motion Design 插件通过提供模块化的工具（如克隆器/效应器、材质设计器、形状工具、文本3D、场景装备、远程控制等），让设计师和广播工程师能够：
1.  **快速构建和迭代**：在编辑器中直接创建和操控复杂的动态场景，无需编写大量代码。
2.  **实现数据驱动的内容**：通过远程控制和序列器，将场景元素与外部数据源（如社交媒体、数据库）或时间线绑定，实现自动化播出。
3.  **进行非破坏性工作流**：利用场景装备（Scene Rig）、操作符堆栈（Operator Stack）等概念，将场景拆分为可管理、可复用的模块，便于协作和版本管理。
4.  **集成专业媒体流程**：通过媒体合成、媒体IO框架等依赖，与外部视频信号、广播设备无缝对接。

它本质上是一个为“制作人”而非“程序员”设计的，用于在虚幻引擎中制作电视节目、现场直播图形、虚拟演播室、动态艺术装置等内容的专业级工具箱。

## 使用场景

*   你需要制作电视节目、新闻频道或颁奖典礼的实时播出图形（Lower Thirds, Transitions, Full-frame Graphics）。
*   你在搭建一个虚拟演播室，需要实时控制虚拟摄像机、灯光、以及与观众互动的动态元素。
*   你需要创建数据驱动的仪表盘、信息可视化或交互式艺术装置，并让它们实时反映数据变化。
*   你希望以非线性、模块化的方式构建复杂的场景，方便不同的设计师（如建模师、材质师、动画师）并行工作。
*   你需要使用高级材质编辑（动态材质、材质设计器）和网格建模工具来快速创建和迭代视觉资产。

## 蓝图用法

**当前模块聚焦：`AvalancheSceneRig`（场景装备子系统）**

`UAvaSceneRigSubsystem` 是管理“场景装备”概念的核心子系统。场景装备是一种特殊的关卡，用于将场景的某个逻辑部分（如一个虚拟演播室区域、一个动态装置）封装为独立的、可管理的单元。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `For World` | 获取指定世界对象（UWorld）的场景装备子系统实例。所有操作通常从这里开始。 | `UAvaSceneRigSubsystem` |
| `Is Scene Rig Asset Data` | 判断给定的资产数据（FAssetData）是否代表一个场景装备关卡。 | `UAvaSceneRigSubsystem` |
| `Is Scene Rig Asset` | 判断给定的对象（UObject*）是否是一个场景装备关卡资产。 | `UAvaSceneRigSubsystem` |
| `Get Scene Rig Asset Suffix` | 获取推荐的场景装备资产名称后缀（如“_SceneRig”），用于区分普通关卡。 | `UAvaSceneRigSubsystem` |
| `Register Supported Actor Classes` | 注册允许被添加到场景装备关卡中的 Actor 类型白名单。 | `UAvaSceneRigSubsystem` |
| `Get Supported Actor Classes` | 获取当前注册的、允许放入场景装备的 Actor 类型列表。 | `UAvaSceneRigSubsystem` |
| `Is Supported Actor Class` | 判断给定的 Actor 类是否被允许加入场景装备。 | `UAvaSceneRigSubsystem` |
| `Scene Rig From Actor` | 查询给定的 Actor 属于哪个活跃的场景装备。 | `UAvaSceneRigSubsystem` |
| `Find All Scene Rigs` | 在当前持久关卡中查找所有已加载的场景装备流式关卡。 | `UAvaSceneRigSubsystem` |
| `Find First Active Scene Rig` | 获取第一个活跃的（已加载的）场景装备流式关卡。文档指出一个世界中通常同时只有一个活跃场景装备。 | `UAvaSceneRigSubsystem` |
| `Is Active Scene Rig Actor` | 判断给定的 Actor 是否属于当前活跃的场景装备。 | `UAvaSceneRigSubsystem` |
| `For Each Active Scene Rig Actor` | 遍历活跃场景装备中的每一个 Actor。 | `UAvaSceneRigSubsystem` |

### 使用示例（蓝图描述）

1.  **在任意蓝图中获取子系统**：使用 `For World` 节点，传入 `Get World` 的返回值。
2.  **检查一个 Actor 是否在场景装备中**：获取子系统后，使用 `Is Active Scene Rig Actor` 节点，输入你的 Actor 引用。
3.  **获取某个 Actor 所属的场景装备关卡**：使用 `Scene Rig From Actor` 节点。
4.  **在初始化时注册允许的 Actor 类**：在游戏或编辑器启动时，调用 `Register Supported Actor Classes`，传入你希望允许放入场景装备的 Actor 类数组（例如，只允许灯光、摄像机、静态网格体）。

## C++ 用法

### 头文件引入

```cpp
#include "AvaSceneRigSubsystem.h"
```

### 基本用法

获取子系统实例并执行查询操作。

```cpp
// 获取当前世界的场景装备子系统
if (UAvaSceneRigSubsystem* SceneRigSubsystem = UAvaSceneRigSubsystem::ForWorld(GetWorld()))
{
    // 查找所有场景装备
    TArray<ULevelStreaming*> AllRigs = SceneRigSubsystem->FindAllSceneRigs();
    UE_LOG(LogTemp, Log, TEXT("Found %d scene rigs."), AllRigs.Num());

    // 获取第一个活跃的场景装备
    ULevelStreaming* ActiveRig = SceneRigSubsystem->FindFirstActiveSceneRig();
    if (ActiveRig)
    {
        UE_LOG(LogTemp, Log, TEXT("Active scene rig: %s"), *ActiveRig->GetWorldAssetPackageName());
    }

    // 遍历活跃场景装备中的所有 Actor
    SceneRigSubsystem->ForEachActiveSceneRigActor([](AActor* const Actor)
    {
        UE_LOG(LogTemp, Log, TEXT("Actor in active scene rig: %s"), *Actor->GetName());
    });
}
```

*来源：基于 `UAvaSceneRigSubsystem` 公共API接口的典型使用模式。*

### 进阶用法

管理场景装备支持的 Actor 类型，并进行资产检查。

```cpp
// 在应用初始化时，注册允许添加到场景装备的 Actor 类
TSet<TSubclassOf<AActor>> AllowedClasses;
AllowedClasses.Add(AStaticMeshActor::StaticClass());
AllowedClasses.Add(ALight::StaticClass());
AllowedClasses.Add(ACameraActor::StaticClass());
UAvaSceneRigSubsystem::RegisterSupportedActorClasses(AllowedClasses);

// 检查一个资产是否是场景装备
FAssetData AssetData = /* 通过资产注册表获取 */;
if (UAvaSceneRigSubsystem::IsSceneRigAssetData(AssetData))
{
    UE_LOG(LogTemp, Log, TEXT("Asset %s is a scene rig level."), *AssetData.AssetName.ToString());
}

// 检查一个 Actor 是否属于某个特定关卡（场景装备）
UObject* MyObject = /* ... */;
if (AActor* MyActor = Cast<AActor>(MyObject))
{
    if (ULevel* ActorLevel = MyActor->GetLevel())
    {
        if (UAvaSceneRigSubsystem::AreSomeActorsInLevel(ActorLevel, {MyActor}))
        {
            UE_LOG(LogTemp, Log, TEXT("Actor %s is in its level (which may be a scene rig)."), *MyActor->GetName());
        }
    }
}
```

*来源：基于 `UAvaSceneRigSubsystem` 的静态和实例方法组合。*

## Demo 示例

一个最小化的示例，展示如何在 C++ Actor 中查询和使用场景装备子系统。

**MySceneRigQueryActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MySceneRigQueryActor.generated.h"

class UAvaSceneRigSubsystem;

UCLASS()
class MYPROJECT_API AMySceneRigQueryActor : public AActor
{
	GENERATED_BODY()
	
public:	
	AMySceneRigQueryActor();

protected:
	virtual void BeginPlay() override;

public:	
	virtual void Tick(float DeltaTime) override;

private:
	UPROPERTY()
	TObjectPtr<UAvaSceneRigSubsystem> CachedSubsystem;

	void QuerySceneRigInfo();
};
```

**MySceneRigQueryActor.cpp**
```cpp
#include "MySceneRigQueryActor.h"
#include "AvaSceneRigSubsystem.h"

AMySceneRigQueryActor::AMySceneRigQueryActor()
{
	PrimaryActorTick.bCanEverTick = true;
}

void AMySceneRigQueryActor::BeginPlay()
{
	Super::BeginPlay();
	// 缓存子系统指针
	CachedSubsystem = UAvaSceneRigSubsystem::ForWorld(GetWorld());
	QuerySceneRigInfo();
}

void AMySceneRigQueryActor::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);
	// 可以在这里进行每帧的场景装备状态检查
}

void AMySceneRigQueryActor::QuerySceneRigInfo()
{
	if (!CachedSubsystem)
	{
		return;
	}

	// 查询第一个活跃的场景装备
	if (ULevelStreaming* ActiveRig = CachedSubsystem->FindFirstActiveSceneRig())
	{
		UE_LOG(LogTemp, Warning, TEXT("Found active scene rig: %s"), *ActiveRig->GetWorldAssetPackageName());
		
		// 检查自身是否属于该场景装备
		if (CachedSubsystem->IsActiveSceneRigActor(this))
		{
			UE_LOG(LogTemp, Warning, TEXT("This actor is part of the active scene rig!"));
		}
	}
	else
	{
		UE_LOG(LogTemp, Warning, TEXT("No active scene rig found in this world."));
	}
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。`AvalancheSceneRig` 模块的公共头文件仅依赖 UE 核心类型（`UWorldSubsystem`, `ULevelStreaming`, `FAssetData` 等）。其构建系统依赖在 `AvalancheCore` 之上，但后者属于插件内部依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将场景设置和大纲视图等专用标签页移至编辑器独立分组，优化工作区组织。 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 当使用“节目单页”设置时，为电影渲染队列（MRQ）添加了分析功能。 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 在节目控制工具栏中增加了页面加载选项（全部、下一个、选中），并添加了相关功能。 |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 添加了一个项目设置，可强制禁用 Text3D 和形状的碰撞。 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构了视口代码，当客户端关联或分离时进行通知，以消除必要的重复代码。 |

### 维护评价

**Avalanche (Motion Design)** 是 Epic Games 为虚幻引擎虚拟制作管线打造的核心工具插件。
*   **活跃维护**：从 Git 历史看，该插件处于非常活跃的开发中（最近更新在 2026 年 5 月）。提交内容涵盖功能添加（节目单控制、分析）、工作流优化（编辑器布局）和设置增加（碰撞控制），表明其功能在持续扩展和完善。
*   **成熟度**：尽管创建于 2025 年初，但它是由多个成熟的实验性插件（如 ActorModifier, Material Designer, ClonerEffector 等）整合迁移而来，因此其底层功能已经过长时间迭代，并非全新项目。
*   **推荐**：**强烈推荐**给从事虚拟制作、广播、实时图形工作的团队使用。它是 UE 在该领域的官方解决方案，集成度高，更新频繁，是构建专业虚拟演播室和播出系统的基石。由于模块众多且仍在快速发展，建议密切关注版本更新说明。

## 相关链接

*   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
*   [官方文档](https://docs.unrealengine.com/5.8/en-US/motion-design-in-unreal-engine/) (需 Epic Games 账户访问)
*   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheFunctionalTest)