# Motion Design

> Compositing, designer and broadcasting tool.

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `Avalanche` (Runtime), `AvalancheAttribute` (Runtime), `AvalancheAttributeEditor` (Runtime), `AvalancheCamera` (Runtime), `AvalancheComponentVisualizers` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), `AvalancheEditorCore` (Runtime), `AvalancheEffectors` (Runtime), `AvalancheEffectorsEditor` (Runtime), `AvalancheFunctionalTest` (Runtime), `AvalancheInteractiveTools` (Runtime), `AvalancheInteractiveToolsRuntime` (Runtime), `AvalancheLevelViewport` (Runtime), `AvalancheMRQ` (Runtime), `AvalancheMRQEditor` (Runtime), `AvalancheMask` (Runtime), `AvalancheMaskEditor` (Runtime), `AvalancheMaterial` (Runtime), `AvalancheMedia` (Runtime), `AvalancheMediaEditor` (Runtime), `AvalancheModifiers` (Runtime), `AvalancheModifiersEditor` (Runtime), `AvalancheOutliner` (Runtime), `AvalanchePropertyAnimator` (Runtime), `AvalanchePropertyAnimatorEditor` (Runtime), `AvalancheRemoteControl` (Runtime), `AvalancheRemoteControlEditor` (Runtime), `AvalancheSVGEditor` (Runtime), `AvalancheSceneRig` (Runtime), `AvalancheSceneRigEditor` (Runtime), `AvalancheSceneTree` (Runtime), `AvalancheSequence` (Runtime), `AvalancheSequencer` (Runtime), `AvalancheShapes` (Runtime), `AvalancheShapesEditor` (Runtime), `AvalancheTag` (Runtime), `AvalancheTagEditor` (Runtime), `AvalancheText` (Runtime), `AvalancheTextEditor` (Runtime), `AvalancheTransition` (Runtime), `AvalancheTransitionEditor` (Runtime), `AvalancheViewport` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Motion Design（Avalanche）是一个全面的虚拟制作和动态设计工具集，旨在为现场活动、广播和实时内容创作提供完整的合成、设计和播放解决方案。它不仅仅是一个简单的序列播放器，而是一个包含几何建模、材质设计、粒子特效（克隆器/效果器）、动态属性动画、场景过渡、远程控制、媒体合成和完整的序列播放管理的综合性工具集。

该插件的核心价值在于将传统影视后期制作的“合成”工作流与虚幻引擎的实时渲染能力结合，让用户能够在虚幻编辑器内直接创建复杂的动态图形（Motion Graphics），并将其输出到广播流、LED屏幕或作为虚拟制作场景的一部分。它解决的问题是：如何在虚幻引擎中高效地设计、编排、预览和播放复杂的动态内容序列。

## 使用场景

*   **现场活动与虚拟制作**：为演唱会、体育赛事或发布会创建实时变化的动态图形、背景和虚拟场景。
*   **广播和电视**：设计电视节目片头、新闻图表、天气预报动画等，并通过媒体输出框架进行实时播出。
*   **LED墙内容创作**：为XR虚拟制作中的LED墙设计和播放动态背景、环境序列。
*   **交互式展览和安装**：创建可以由观众交互控制或根据数据实时变化的动态内容。
*   **复杂动画序列管理**：管理包含大量动画、效果和交互逻辑的序列，支持按标签、名称查询和分组播放。

## 蓝图用法

Motion Design插件提供了强大的蓝图API，主要集中在序列的播放控制上。以下是从 `IAvaSequencePlaybackObject` 接口和 `UAvaSequenceLibrary` 提取的核心节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Playback Object` | 获取当前世界的序列播放对象。 | `UAvaSequenceLibrary` |
| `Make Single Frame Play Settings` | 创建单帧播放的配置参数。 | `UAvaSequenceLibrary` |
| `Play Sequence (by Soft Reference)` | 通过软引用播放单个序列。 | `IAvaSequencePlaybackObject` |
| `Play Sequences (by Label)` | 播放所有带有指定标签的序列。 | `IAvaSequencePlaybackObject` |
| `Play Sequences (by Tag)` | 播放所有匹配指定Gameplay标签的序列。 | `IAvaSequencePlaybackObject` |
| `Play Scheduled Sequences` | 播放预设的调度序列。 | `IAvaSequencePlaybackObject` |
| `Continue Sequences (by Label)` | 继续（从暂停或停止点恢复）所有带指定标签的序列。 | `IAvaSequencePlaybackObject` |
| `Pause Sequences (by Label)` | 暂停所有带指定标签的序列。 | `IAvaSequencePlaybackObject` |
| `Stop Sequences (by Label)` | 停止所有带指定标签的序列。 | `IAvaSequencePlaybackObject` |
| `Get All Sequence Players` | 获取所有活动的序列播放器。 | `IAvaSequencePlaybackObject` |
| `Has Active Sequence Players` | 检查是否有任何活动的序列播放器。 | `IAvaSequencePlaybackObject` |

### 使用示例（蓝图描述）

1.  **基本播放**：在事件图表中，从 `Get Playback Object` 节点获取播放对象，然后将其连接到 `Play Sequences (by Label)` 节点的 `Target` 引脚。将标签（如 `“Intro”`）连接到 `Sequence Label` 引脚，并配置 `Play Settings`（播放设置）。
2.  **带条件播放**：使用 `Play Sequences (by Tag)` 节点。首先定义一个 `FAvaTagHandle` 变量，设置为特定的Gameplay标签。将此变量连接到 `In Tag Handle` 引脚，并设置 `Exact Match` 布尔值。该节点会播放所有包含该标签（或精确匹配）的序列。
3.  **序列控制流**：在序列运行时，通过其他事件调用 `Continue Sequences` 或 `Stop Sequences` 来控制播放流程。例如，在某个自定义事件触发时，调用 `Stop Sequences (by Labels)` 来停止一组序列。

## C++ 用法

### 头文件引入

```cpp
#include "AvalancheSequence/Public/AvaSequenceSubsystem.h"
#include "AvalancheSequence/Public/AvaSequencePlaybackObject.h"
#include "AvalancheSequence/Public/AvaSequence.h"
```

### 基本用法

以下示例展示了如何在C++中获取序列子系统并播放序列。

```cpp
// 获取世界子系统
UAvaSequenceSubsystem* SequenceSubsystem = UAvaSequenceSubsystem::Get(GetWorld());
if (SequenceSubsystem)
{
    // 获取播放对象（需要有一个实现了IAvaSequencePlaybackObject的对象，例如AAvaSequencePlaybackActor）
    IAvaSequencePlaybackObject* PlaybackObject = SequenceSubsystem->FindPlaybackObject(GetLevel());
    if (PlaybackObject)
    {
        // 播放指定序列
        UAvaSequence* SequenceToPlay = ...; // 从资产加载或获取
        FAvaSequencePlayParams PlayParams;
        PlayParams.Start = FAvaSequenceTime(0.0); // 从第一帧开始
        PlayParams.PlayMode = EAvaSequencePlayMode::Forward;
        
        UAvaSequencePlayer* Player = PlaybackObject->PlaySequence(SequenceToPlay, PlayParams);
        if (Player)
        {
            // 可以监听播放完成等事件
        }
    }
}
```
**来源**：基于 `AvaSequenceSubsystem.h` 和 `AvaSequencePlaybackObject.h` 中的接口设计。

### 进阶用法：查询和控制序列

```cpp
// 通过标签查询并控制序列
FName SequenceLabel = TEXT("Outro");
IAvaSequencePlaybackObject* PlaybackObject = ...; // 获取方式同上

// 暂停所有带“Outro”标签的序列
PlaybackObject->PauseSequencesByLabel(SequenceLabel);

// 停止后，再次播放
TArray<UAvaSequencePlayer*> Players = PlaybackObject->PlaySequencesByLabel(SequenceLabel, FAvaSequencePlayParams());

// 检查是否有活动序列
bool bHasActive = PlaybackObject->HasActiveSequencePlayers();
```
**来源**：基于 `IAvaSequencePlaybackObject` 接口方法。

## Demo 示例

这是一个最小化的C++类，演示如何实现一个自定义的序列播放对象。

**AvaMyPlaybackActor.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "AvalancheSequence/Public/AvaSequencePlaybackObject.h"
#include "AvaMyPlaybackActor.generated.h"

UCLASS()
class AAvaMyPlaybackActor : public AActor, public IAvaSequencePlaybackObject
{
    GENERATED_BODY()
    
public:
    AAvaMyPlaybackActor();

    // IAvaSequencePlaybackObject 接口实现
    virtual UObject* ToUObject() override { return this; }
    virtual ULevel* GetPlaybackLevel() const override { return GetLevel(); }
    virtual void CleanupPlayers() override;
    virtual UAvaSequencePlayer* PlaySequence(UAvaSequence* InSequence, const FAvaSequencePlayParams& InPlaySettings = FAvaSequencePlayParams()) override;
    // ... 其他接口方法需要实现 ...
    
    // 为了简化，此处省略了其他必须实现的接口函数
    virtual TArray<UAvaSequencePlayer*> GetAllSequencePlayers() const override { return ActivePlayers; }
    virtual bool HasActiveSequencePlayers() const override { return !ActivePlayers.IsEmpty(); }
    // 其他函数实现略...

private:
    UPROPERTY()
    TArray<TObjectPtr<UAvaSequencePlayer>> ActivePlayers;
};
```

**AvaMyPlaybackActor.cpp**
```cpp
#include "AvaMyPlaybackActor.h"
#include "AvalancheSequence/Public/AvaSequence.h"
#include "AvalancheSequence/Public/AvaSequencePlayer.h"

AAvaMyPlaybackActor::AAvaMyPlaybackActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AAvaMyPlaybackActor::CleanupPlayers()
{
    for (UAvaSequencePlayer* Player : ActivePlayers)
    {
        if (Player)
        {
            Player->Stop();
        }
    }
    ActivePlayers.Empty();
}

UAvaSequencePlayer* AAvaMyPlaybackActor::PlaySequence(UAvaSequence* InSequence, const FAvaSequencePlayParams& InPlaySettings)
{
    if (!InSequence) return nullptr;

    UAvaSequencePlayer* NewPlayer = NewObject<UAvaSequencePlayer>(this);
    NewPlayer->InitSequence(InSequence, this, GetLevel(), FLevelSequenceCameraSettings());
    NewPlayer->SetPlaySettings(InPlaySettings);
    NewPlayer->PlaySequence();

    ActivePlayers.Add(NewPlayer);
    return NewPlayer;
}
```
**说明**：此示例仅用于展示接口结构。实际使用中，`AAvaSequencePlaybackActor` 已经提供了完整实现，通常无需自定义，除非需要深度定制播放行为。

## 模块依赖

`AvalancheSequence` 模块依赖以下独特模块：

| 模块 | 用途 |
|---|---|
| `AvalancheCore` | Motion Design插件的核心基础模块，提供通用类型和接口。 |
| `AvalancheTag` | 提供 `FAvaTagHandle` 等标签系统，用于序列查询和标识。 |
| `Sequencer` | 依赖虚幻引擎的Sequencer核心，用于扩展序列播放功能。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将编辑器中的Motion Design标签页（场景设置、大纲视图）移至独立分组。 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 添加了使用“节目单页面”设置时的MRQ（Movie Render Queue）分析功能。 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 在节目控制工具栏中添加了页面加载选项（全部、下一个、已选择），并增加了相关功能。 |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 添加了一个项目设置，可强制禁用Text3D和形状的碰撞。 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口：通过通知客户端关联或取消关联来重组必要的复制粘贴代码。 |

### 维护评价

Motion Design (Avalanche) 是一个非常新的插件，于2025年5月从实验性路径迁移至正式路径。从最近的Git提交历史看（截止到2026年5月），它正处于**非常活跃的开发和维护期**。更新频率高，涵盖了新功能添加、UI优化、性能分析、配置增强以及底层代码重构。尽管它从实验性迁移而来，但鉴于Epic Games的持续投入和其在虚拟制作领域的重要性，可以认为这是一个**稳定且持续演进**的核心插件。它目前没有已知的废弃迹象，强烈推荐有相关需求的用户使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/motion-design-in-unreal-engine/)