# Motion Design

> Compositing, designer and broadcasting tool.
>
> Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 运动设计 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（编辑器工具、运行时组件） |
| 模块 | `Avalanche` (Runtime), `AvalancheAttribute` (Runtime), `AvalancheAttributeEditor` (Runtime), `AvalancheCamera` (Runtime), `AvalancheComponentVisualizers` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), `AvalancheEditorCore` (Runtime), `AvalancheEffectors` (Runtime), `AvalancheEffectorsEditor` (Runtime), `AvalancheFunctionalTest` (Runtime), `AvalancheInteractiveTools` (Runtime), `AvalancheInteractiveToolsRuntime` (Runtime), `AvalancheLevelViewport` (Runtime), `AvalancheMRQ` (Runtime), `AvalancheMRQEditor` (Runtime), `AvalancheMask` (Runtime), `AvalancheMaskEditor` (Runtime), `AvalancheMaterial` (Runtime), `AvalancheMedia` (Runtime), `AvalancheMediaEditor` (Runtime), `AvalancheModifiers` (Runtime), `AvalancheModifiersEditor` (Runtime), `AvalancheOutliner` (Runtime), `AvalanchePropertyAnimator` (Runtime), `AvalanchePropertyAnimatorEditor` (Runtime), `AvalancheRemoteControl` (Runtime), `AvalancheRemoteControlEditor` (Runtime), `AvalancheSVGEditor` (Runtime), `AvalancheSceneRig` (Runtime), `AvalancheSceneRigEditor` (Runtime), `AvalancheSceneTree` (Runtime), `AvalancheSequence` (Runtime), `AvalancheSequencer` (Runtime), `AvalancheShapes` (Runtime), `AvalancheShapesEditor` (Runtime), `AvalancheTag` (Runtime), `AvalancheTagEditor` (Runtime), `AvalancheText` (Runtime), `AvalancheTextEditor` (Runtime), `AvalancheTransition` (Runtime), `AvalancheTransitionEditor` (Runtime), `AvalancheViewport` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Avalanche (Motion Design) 是一个大型的虚拟制作工具集，其核心目标是为广播、虚拟制作和动态图形（Motion Graphics）提供一个集成的、实时的设计与合成环境。它不同于传统的静态场景编辑，专注于在虚拟生产管线中快速创建、动画化和控制复杂的2D/3D图形元素、UI、文本和形状。

它解决的关键问题包括：
1.  **实时图形设计**：在UE编辑器中提供类似图形设计软件的交互式工具，用于绘制矢量形状（`AvalancheShapes`）、排版（`AvalancheText`）和导入SVG（`AvalancheSVGEditor`）。
2.  **流程自动化**：通过克隆器/效果器（`AvalancheEffectors`）、属性动画器（`AvalanchePropertyAnimator`）和修改器（`AvalancheModifiers`）系统，批量控制对象属性，实现复杂的动态效果。
3.  **集成广播控制**：通过与媒体框架（`AvalancheMedia`）、远程控制（`AvalancheRemoteControl`）和场景编排（`AvalancheSceneRig`）的深度集成，支持在直播或录制环境中实时触发和管理图形内容。
4.  **一体化工作流**：将设计、动画、预览和最终输出（通过MRQ `AvalancheMRQ`）整合在一个插件生态内，避免在不同软件间切换。

它之前位于 `Experimental` 目录，现在被提升为核心虚拟制作工具，表明其成熟度和重要性已被Epic认可。

## 使用场景

-   你在制作一档虚拟新闻节目的背景图形、数据可视化图表和主播名牌 → 使用 Motion Design 的文本、形状和动画工具进行设计，并通过场景编排和远程控制实现直播切换。
-   你需要为一场大型虚拟演唱会创建动态的、随音乐变化的视觉元素 → 利用克隆器/效果器和属性动画器，基于音频或时间线驱动大量对象的动画。
-   你正在开发一个交互式信息亭或虚拟展厅，需要动态的UI和图标 → 使用SVG导入和矢量绘图工具快速创建资源，并通过蓝图或媒体集成实现交互。
-   你作为实时图形设计师，希望在一个统一的环境中完成从概念草图到最终渲染输出的整个流程 → 使用集成的编辑器工具和电影渲染队列（MRQ）模块。

## 蓝图用法

由于该插件主要以编辑器工具和底层系统的形式提供，其直接暴露给蓝图的核心节点相对较少，更多是通过编辑器内的专用工具和面板进行操作。以下是一些关键的可蓝图交互点：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ApplyModifier` | 对Actor应用指定的修改器实例（需通过修改器框架）。 | `UActorModifierCoreSubsystem` (来自依赖插件) |
| `Start/Stop Effectors` | 控制克隆器/效果器系统的播放状态。 | 相关效应器类 |
| `Trigger SceneRig Event` | 触发场景编排中的一个预设事件。 | `UAvaSceneRigSubsystem` |
| `Send Remote Control Command` | 通过远程控制协议发送参数或命令。 | `URemoteControlInterceptionSubsystem` |

### 使用示例（蓝图描述）

要通过蓝图控制一个场景编排：
1.  在关卡中放置一个 `AvaSceneRigActor`。
2.  在蓝图中，使用 `Get Game Instance` -> `Get Subsystem` -> `UAvaSceneRigSubsystem` 获取子系统引用。
3.  调用 `Trigger SceneRig Event` 节点，传入你的 `AvaSceneRigActor` 引用和要触发的事件名称（例如 “ShowIntro”），即可在运行时播放预设的图形动画序列。

## C++ 用法

该插件的API主要服务于编辑器扩展和深度集成，以下从可用头文件推断基本用法模式。

### 头文件引入

```cpp
#include "AvalancheSVGEditorModule.h"
```

### 基本用法：监听SVG图形事件

来自 `AvaSVGEditorModule.h`，展示了如何作为模块监听SVG相关的编辑器事件。

```cpp
// 在你自己的编辑器模块中
#include "AvalancheSVGEditorModule.h"

void FMyEditorModule::StartupModule()
{
    // 获取Avalanche SVG编辑器模块
    if (IAvalancheSVGEditorModule* SVGEditorModule = FModuleManager::GetModulePtr<IAvalancheSVGEditorModule>(“AvalancheSVGEditor”))
    {
        // 订阅一个自定义委托，当SVG图形被分割或更新时执行回调
        // 具体的委托签名需查看其Public头文件
        SVGEditorModule->OnSVGShapesUpdated().AddRaw(this, &FMyEditorModule::HandleSVGUpdate);
    }
}

void FMyEditorModule::HandleSVGUpdate(AActor* UpdatedActor)
{
    // 当SVG关联的Actor更新时，你可以在此执行自定义逻辑
    UE_LOG(LogTemp, Log, TEXT(“SVG Actor updated: %s”), *UpdatedActor->GetName());
}

void FMyEditorModule::ShutdownModule()
{
    // 取消订阅，避免野指针
    // ...
}
```
**来源文件**: `Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheSVGEditor/Private/AvaSVGEditorModule.h`

### 进阶用法：注册交互式工具

来自 `AvaSVGActorTool.h`，展示了如何定义和注册一个自定义的交互式编辑器工具（Edit Mode工具）。

```cpp
// 自定义一个用于放置或操作SVG Actor的工具
UCLASS()
class UAvaCustomSVGTool : public UAvaInteractiveToolsActorPointToolBase
{
    GENERATED_BODY()

public:
    UAvaCustomSVGTool();

    // 重写此函数来向交互式工具系统注册你的工具
    virtual void OnRegisterTool(IAvalancheInteractiveToolsModule* InAITModule) override
    {
        Super::OnRegisterTool(InAITModule);

        // 在此处添加自定义工具的属性、输入行为等设置
        // 例如：添加一个布尔属性来控制工具是否吸附网格
        AddProperty(FPropertyEditorMetadata(“bSnapToGrid”, true));
    }

    // 可能还需要重写 OnStart, OnUpdate, OnEnd 等函数来实现工具的具体交互逻辑
};

// 在模块启动时，通常会有地方调用类似这样的注册代码（具体流程需深入查看AvalancheInteractiveTools模块）：
// InAITModule->RegisterTool<UAvaCustomSVGTool>(“MyTools.SVG.CustomTool”, FText::FromString(“Custom SVG Tool”));
```
**来源文件**: `Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheSVGEditor/Private/Tool/AvaSVGActorTool.h`

## Demo 示例

以下是一个监听Motion Design中SVG更新事件的最小编辑器模块示例。

**MySVGWatcherModule.h**
```cpp
#pragma once

#include "Modules/ModuleManager.h"

class FMySVGWatcherModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    void OnSVGShapesUpdated(AActor* InActor);
    FDelegateHandle UpdateDelegateHandle;
};
```

**MySVGWatcherModule.cpp**
```cpp
#include "MySVGWatcherModule.h"
#include "AvalancheSVGEditorModule.h"

#define LOCTEXT_NAMESPACE "FMySVGWatcherModule"

void FMySVGWatcherModule::StartupModule()
{
    // 尝试获取Avalanche SVG编辑器模块
    IModuleInterface* SVGModuleRaw = FModuleManager::Get().LoadModule(“AvalancheSVGEditor”);
    if (SVGModuleRaw)
    {
        // 注意：这里假设存在一个公开的获取委托的接口，实际API需查阅头文件。
        // 下面为伪代码示例。
        // IAvalancheSVGEditorModule* SVGEditor = static_cast<IAvalancheSVGEditorModule*>(SVGModuleRaw);
        // if (SVGEditor)
        // {
        //     UpdateDelegateHandle = SVGEditor->GetOnSVGShapesUpdatedDelegate().AddRaw(this, &FMySVGWatcherModule::OnSVGShapesUpdated);
        // }
    }
}

void FMySVGWatcherModule::ShutdownModule()
{
    // 清理委托绑定
    // if (IAvalancheSVGEditorModule* SVGEditor = ...)
    // {
    //     SVGEditor->GetOnSVGShapesUpdatedDelegate().Remove(UpdateDelegateHandle);
    // }
}

void FMySVGWatcherModule::OnSVGShapesUpdated(AActor* InActor)
{
    // 你的自定义响应逻辑
    UE_LOG(LogTemp, Warning, TEXT(“SVG was updated! Actor: %s”), *InActor->GetName());
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMySVGWatcherModule, MySVGWatcher)
```

## 模块依赖

要使用或扩展Avalanche的SVG编辑器模块，你的项目或插件需要依赖以下模块（基于典型的Motion Design构建）：

| 模块 | 用途 |
|---|---|
| `AvalancheSVGEditor` | 提供SVG相关的编辑器工具和UI。 |
| `AvalancheInteractiveTools` | 提供交互式编辑工具（Edit Mode）的框架。 |
| `AvalancheShapes` | SVG图形在运行时的核心表示和基础功能。 |
| `SVGImporter` | 处理SVG文件的解析和导入。（Epic的独立插件） |
| `ActorModifierCore` | 为修改器系统提供核心支持。（Epic的独立插件） |

*(注：其他依赖如 `Core`, `Engine`, `Slate`, `UnrealEd` 等均为常见依赖，已省略)*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将运动设计的“场景设置”和“大纲”标签页移至独立分组，优化编辑器布局。 |
| 2025-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 为MRQ（电影渲染队列）在使用节目单页面设置时增加了数据统计功能。 |
| 2025-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 在节目控制工具栏中增加了页面加载选项（全部、下一个、已选）。 |
| 2025-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 增加了项目设置，可以强制禁用3D文本和形状的碰撞，简化场景管理。 |
| 2025-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口优化：通过通知客户端关联/断开事件，避免重复代码。 |

### 维护评价

**状态：活跃维护**
- **创建时间**：2025年5月，非常新的插件。
- **更新频率**：从git历史看，在创建后的短时间内（几天）就有多次密集的功能性提交，表明开发非常活跃。
- **内容质量**：最近的提交涉及UI优化、新功能添加（MRQ分析、页面加载选项）和性能/工作流改进（碰撞禁用、视口代码重构），而非简单的编译修复，说明插件处于积极的功能开发阶段。
- **稳定性**：已从 `Experimental` 晋升为 `Virtual Production` 核心插件，表明其通过了内部的质量评估。
- **推荐度**：强烈推荐有虚拟制作、动态图形或广播需求的团队使用。这是一个功能强大且得到官方支持的前沿工具集，将持续获得更新和改进。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [AvalancheSVGEditor子目录](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheSVGEditor)