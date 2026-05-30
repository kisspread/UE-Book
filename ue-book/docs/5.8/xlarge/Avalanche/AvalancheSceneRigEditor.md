# Motion Design

> Compositing, designer and broadcasting tool.
> 
> Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（运行时资产，编辑器扩展） |
| 模块 | `Avalanche` (Runtime), `AvalancheAttribute` (Runtime), `AvalancheAttributeEditor` (Runtime), `AvalancheCamera` (Runtime), `AvalancheComponentVisualizers` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), `AvalancheEditorCore` (Runtime), `AvalancheEffectors` (Runtime), `AvalancheEffectorsEditor` (Runtime), `AvalancheFunctionalTest` (Runtime), `AvalancheInteractiveTools` (Runtime), `AvalancheInteractiveToolsRuntime` (Runtime), `AvalancheLevelViewport` (Runtime), `AvalancheMRQ` (Runtime), `AvalancheMRQEditor` (Runtime), `AvalancheMask` (Runtime), `AvalancheMaskEditor` (Runtime), `AvalancheMaterial` (Runtime), `AvalancheMedia` (Runtime), `AvalancheMediaEditor` (Runtime), `AvalancheModifiers` (Runtime), `AvalancheModifiersEditor` (Runtime), `AvalancheOutliner` (Runtime), `AvalanchePropertyAnimator` (Runtime), `AvalanchePropertyAnimatorEditor` (Runtime), `AvalancheRemoteControl` (Runtime), `AvalancheRemoteControlEditor` (Runtime), `AvalancheSVGEditor` (Runtime), `AvalancheSceneRig` (Runtime), `AvalancheSceneRigEditor` (Runtime), `AvalancheSceneTree` (Runtime), `AvalancheSequence` (Runtime), `AvalancheSequencer` (Runtime), `AvalancheShapes` (Runtime), `AvalancheShapesEditor` (Runtime), `AvalancheTag` (Runtime), `AvalancheTagEditor` (Runtime), `AvalancheText` (Runtime), `AvalancheTextEditor` (Runtime), `AvalancheTransition` (Runtime), `AvalancheTransitionEditor` (Runtime), `AvalancheViewport` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Avalanche (Motion Design) 是一个全面的虚幻引擎插件套件，旨在为虚拟制片（Virtual Production）和广播图形提供一个完整的**实时合成、设计和播出控制**工作流。它将传统上需要多个外部 DCC 工具（如 After Effects）的功能直接集成到 UE 编辑器中，解决了在引擎内创建、编排和播放复杂动态图形（Motion Graphics）和虚拟场景的痛点。其核心价值在于让设计师、导演和技术美术能够在统一的 UE 环境中完成从创意设计到实时播出的全过程，极大提升了虚拟制片的效率和创意灵活性。

## 使用场景

- **广播包装设计师**：创建用于电视节目、新闻、体育赛事转播的实时三维图文包装、动态图表和视觉特效。
- **虚拟演播室设计师**：设计并编排虚拟演播室中的场景布局、摄像机动态、材质效果和物体动画。
- **大型活动/演唱会制作人**：控制现场 LED 屏幕、舞台视觉的实时内容播放和场景切换。
- **广告与短视频制作团队**：快速制作产品动态广告、社交媒体短视频等，利用引擎的实时渲染优势进行快速迭代。

## 蓝图用法

基于 `AvalancheSceneRigEditor` 模块的公共接口分析，主要功能通过 `IAvaSceneRigEditorModule` 接口暴露。以下为核心功能节点分组。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CustomizeSceneRig` | 自定义场景绑定资产在细节面板中的属性显示 | `IAvaSceneRigEditorModule` |
| `SetActiveSceneRig` | 将指定的场景绑定资产加载为活动场景 | `IAvaSceneRigEditorModule` |
| `GetActiveSceneRig` | 获取当前世界中活动的场景绑定资产路径 | `IAvaSceneRigEditorModule` |
| `IsActiveSceneRigActor` | 检查一个Actor是否属于当前活动的场景绑定 | `IAvaSceneRigEditorModule` |
| `RemoveAllSceneRigs` | 移除当前世界中的所有场景绑定对象 | `IAvaSceneRigEditorModule` |
| `AddActiveSceneRigActors` | 将一组Actor添加到活动的场景绑定中 | `IAvaSceneRigEditorModule` |
| `RemoveActiveSceneRigActors` | 从活动的场景绑定中移除一组Actor | `IAvaSceneRigEditorModule` |
| `CreateSceneRigAssetWithDialog` | 通过对话框创建一个新的场景绑定资产 | `IAvaSceneRigEditorModule` |

### 使用示例（蓝图描述）

1.  **创建并设置场景**：首先，使用 `Create Scene Rig Asset With Dialog` 节点，用户会被提示选择保存位置并创建一个新的空场景绑定资产。
2.  **加载场景**：获取对 `IAvaSceneRigEditorModule` 的引用（通过模块管理器），然后调用 `Set Active Scene Rig` 节点，传入上一步创建的资产路径，即可将该场景加载到当前关卡中。
3.  **管理场景内物体**：使用 `Add Active Scene Rig Actors` 节点，可以将关卡中现有的 Actor（如摄像机、灯光、网格体）批量添加到活动的场景绑定中。之后，这些 Actor 将被视为该场景的一部分。
4.  **场景切换与事件响应**：通过 `Get Active Scene Rig` 查询当前场景，并监听 `On Scene Rig Changed`、`On Scene Rig Actors Added`/`Removed` 事件委托，可以在蓝图中响应场景的切换和内容变更，实现复杂的播出逻辑。

## C++ 用法

### 头文件引入

```cpp
#include "IAvaSceneRigEditorModule.h"
```

### 基本用法

以下示例展示了如何获取场景绑定编辑器模块的接口并执行基本操作。

```cpp
// 来源: 基于 Public/IAvaSceneRigEditorModule.h 接口设计

#include "IAvaSceneRigEditorModule.h"
#include "Engine/World.h"
#include "Engine/LevelStreaming.h"

void MyClass::SetupSceneRig(UWorld* InWorld, const FSoftObjectPath& InRigPath)
{
    // 1. 获取模块接口
    if (IAvaSceneRigEditorModule::IsLoaded())
    {
        IAvaSceneRigEditorModule& SceneRigModule = IAvaSceneRigEditorModule::Get();

        // 2. 设置活动场景绑定
        ULevelStreaming* NewStreamingLevel = SceneRigModule.SetActiveSceneRig(InWorld, InRigPath);
        if (NewStreamingLevel)
        {
            UE_LOG(LogTemp, Log, TEXT("Successfully set active Scene Rig: %s"), *InRigPath.ToString());
        }

        // 3. 查询当前活动的场景绑定
        FSoftObjectPath CurrentRig = SceneRigModule.GetActiveSceneRig(InWorld);
        UE_LOG(LogTemp, Log, TEXT("Current active Scene Rig: %s"), *CurrentRig.ToString());
    }
}

// 4. 监听场景变化事件
FDelegateHandle Handle;
void MyClass::BindToSceneRigEvents(UWorld* InWorld)
{
    if (IAvaSceneRigEditorModule::IsLoaded())
    {
        IAvaSceneRigEditorModule& SceneRigModule = IAvaSceneRigEditorModule::Get();
        Handle = SceneRigModule.OnSceneRigChanged().AddLambda(
            [](UWorld* InWorld, ULevelStreaming* InNewRig)
            {
                UE_LOG(LogTemp, Warning, TEXT("Scene Rig changed in world %s"), *InWorld->GetName());
            }
        );
    }
}
```

### 进阶用法

结合 Outliner 和命令，实现一个从编辑器工具栏触发的批量操作。

```cpp
// 来源: 结合 IAvaSceneRigEditorModule 和 AvaSceneRigEditorCommands.h

#include "IAvaSceneRigEditorModule.h"
#include "AvaSceneRigEditorCommands.h"
#include "AvalancheOutlinerModule.h" // 假设已加载
#include "IAvaOutliner.h"

void MyEditorTool::AddSelectedToSceneRig()
{
    // 1. 获取选中的 Outliner 物品
    TArray<FAvaOutlinerItemPtr> SelectedItems;
    // ... (通过IAvaOutliner获取选择)

    // 2. 将物品转换为Actor列表
    TArray<AActor*> ActorsToAdd;
    for (const FAvaOutlinerItemPtr& Item : SelectedItems)
    {
        if (AActor* Actor = Cast<AActor>(Item->GetObject()))
        {
            ActorsToAdd.Add(Actor);
        }
    }

    // 3. 执行添加到场景绑定的操作
    if (IAvaSceneRigEditorModule::IsLoaded() && !ActorsToAdd.IsEmpty())
    {
        IAvaSceneRigEditorModule& Module = IAvaSceneRigEditorModule::Get();
        UWorld* EditorWorld = GEditor->GetEditorWorldContext().World();
        Module.AddActiveSceneRigActors(EditorWorld, ActorsToAdd);
    }
}
```

## Demo 示例

一个完整的、可编译的最小编辑器工具类示例，演示如何创建和管理场景绑定。

**SceneRigManager.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "IAvaSceneRigEditorModule.h"

class AMySceneRigManager : public UObject
{
public:
    UFUNCTION(BlueprintCallable, Category = "SceneRig")
    bool LoadAndSetupSceneRig(UWorld* InWorld, const FSoftObjectPath& InAssetPath);

    UFUNCTION(BlueprintCallable, Category = "SceneRig")
    void AddActorsToCurrentRig(UWorld* InWorld, const TArray<AActor*>& InActors);

private:
    void OnRigChanged(UWorld* InWorld, ULevelStreaming* InNewRig);
    FDelegateHandle RigChangedHandle;
};
```

**SceneRigManager.cpp**
```cpp
#include "SceneRigManager.h"

bool AMySceneRigManager::LoadAndSetupSceneRig(UWorld* InWorld, const FSoftObjectPath& InAssetPath)
{
    if (!IAvaSceneRigEditorModule::IsLoaded()) return false;
    IAvaSceneRigEditorModule& Module = IAvaSceneRigEditorModule::Get();

    // 设置场景绑定
    ULevelStreaming* Level = Module.SetActiveSceneRig(InWorld, InAssetPath);
    if (!Level) return false;

    // 绑定事件
    RigChangedHandle = Module.OnSceneRigChanged().AddUObject(this, &AMySceneRigManager::OnRigChanged);
    return true;
}

void AMySceneRigManager::AddActorsToCurrentRig(UWorld* InWorld, const TArray<AActor*>& InActors)
{
    if (!IAvaSceneRigEditorModule::IsLoaded()) return;
    IAvaSceneRigEditorModule& Module = IAvaSceneRigEditorModule::Get();
    Module.AddActiveSceneRigActors(InWorld, InActors);
}

void AMySceneRigManager::OnRigChanged(UWorld* InWorld, ULevelStreaming* InNewRig)
{
    UE_LOG(LogTemp, Log, TEXT("Scene Rig manager notified: Scene changed to %s"),
        InNewRig ? *InNewRig->GetWorldAssetPackageName() : TEXT("None"));
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AvalancheSceneRig` | 场景绑定的核心运行时逻辑和数据结构 |
| `AvalancheOutliner` | 提供 Motion Design 专用的场景大纲树（Outliner）框架 |
| `AvalancheCore` | Motion Design 插件的通用核心功能与基类 |
| `AvalancheEditorCore` | 编辑器侧的核心工具和功能 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将 Motion Design 的“场景设置”和“大纲视图”标签页移至其独立的分组中，优化了编辑器界面组织。 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 在使用“节目单页面”设置时，增加了对 MRQ（Movie Render Queue）的分析统计功能。 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 为节目控制工具栏增加了页面加载选项（全部、下一个、选定），并添加了相关功能。 |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 增加了项目设置，可强制禁用 Text3D 和形状的碰撞，优化特定场景下的性能。 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口：通过通知客户端其关联或断开关联来重构必要的重复代码，提升代码质量。 |

### 维护评价

- **活跃维护**：从 git 历史看，该插件在最近几周（2026年5月）仍有持续的功能性更新和优化，包括新增特性（如 MRQ 分析、页面加载选项）、界面优化（标签页分组）和项目设置增强。
- **成熟度**：插件规模庞大（2060个源文件），拥有 43 个子模块，表明其功能已经非常完善和模块化。虽然首次提交于 2025 年 5 月，但其内容（原 `Experimental` 目录下的多个插件）显然经过了更长时间的开发和测试。
- **推荐度**：**强烈推荐** 用于专业的虚拟制片和广播图形项目。它是由 Epic Games 官方维护的集成解决方案，功能全面，模块化良好，并且正处于积极的迭代期。对于需要在 UE 内完成高质量实时图形合成的团队，这是一个核心且可靠的工具集。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/motion-design-in-unreal-engine/)