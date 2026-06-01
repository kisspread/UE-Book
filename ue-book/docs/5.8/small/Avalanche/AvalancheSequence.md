# AvalancheSequence

> Compositing, designer and broadcasting tool.
>
> Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计序列系统 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AvalancheSequence` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheSequence) | |

## 用途

AvalancheSequence 是 Motion Design（动态设计）插件的**序列播放管理模块**，为虚拟制片中的动态图形设计提供一套完整的序列控制系统。

该模块解决的核心问题是：在 Motion Design 场景中，需要一种不同于传统 Sequencer 的方式来播放、控制和组合动画序列。它在此基础上引入了以下关键概念：

1. **Playback Object 模式**：通过 `IAvaSequencePlaybackObject` 接口抽象播放上下文，允许多个序列在同一个播放对象中并发运行，由系统统一管理生命周期。
2. **标签与名称查找**：支持通过 Label（标签名）或 GameplayTag 批量查找并播放一组序列，无需硬编码序列引用。
3. **Marks 系统**：在序列的标记帧上绑定"角色"（停止、暂停、跳转、反转），实现交互式的非线性播放控制，类似于 DVD 菜单的章节跳转功能。
4. **Scheduled Playback**：允许预先调度一批序列，一次调用统一触发。
5. **StateTree 转场集成**：通过 `FAvaTransitionTask` 体系与 Unreal 的 StateTree 系统集成，可以在状态切换时自动播放/等待/停止序列。

## 使用场景

- 你在做虚拟制片中的**动态图形场景**（如演播室大屏、LED 墙内容）→ 用 AvalancheSequence 管理复杂的动画序列编排
- 你需要在场景中实现**交互式动画**（如用户操作后触发特定动画、动画到达关键帧时暂停等待输入）→ 利用 Marks 系统的 Stop/Pause/Jump 角色
- 你需要通过**标签批量控制**一组动画的播放、暂停或停止（如同时停止所有"Blink"标签的动画）→ 使用 Play/Stop/Pause ByTag API
- 你在使用 **StateTree** 做状态机，在状态转场时需要播放动画并等待完成 → 使用 FAvaTransitionPlaySequenceTask / FAvaTransitionWaitForSequenceTask
- 你需要预调度多组序列，一键触发执行 → 使用 PlayScheduledSequences

## 蓝图用法

### 播放对象获取

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Playback Object` | 获取当前世界的序列播放对象 | `UAvaSequenceLibrary` |
| `Make Single Frame Play Settings` | 创建单帧播放参数（用于预览特定帧） | `UAvaSequenceLibrary` |

### 序列播放控制（IAvaSequencePlaybackObject）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Play Sequence (by Soft Reference)` | 通过软引用播放单个序列 | `IAvaSequencePlaybackObject` |
| `Play Sequences (by Label)` | 播放所有匹配标签名的序列 | `IAvaSequencePlaybackObject` |
| `Play Sequences (by Soft Reference)` | 通过软引用数组批量播放 | `IAvaSequencePlaybackObject` |
| `Play Sequences (by Labels)` | 通过标签名数组批量播放 | `IAvaSequencePlaybackObject` |
| `Play Sequences (by Tag)` | 通过 GameplayTag 匹配并播放序列 | `IAvaSequencePlaybackObject` |
| `Play Scheduled Sequences` | 播放所有已调度的序列 | `IAvaSequencePlaybackObject` |
| `Continue Sequences (by Label)` | 继续已暂停的序列（通过标签名） | `IAvaSequencePlaybackObject` |
| `Continue Sequences (by Tag)` | 继续已暂停的序列（通过 Tag） | `IAvaSequencePlaybackObject` |
| `Pause Sequences (by Label)` | 暂停匹配标签名的序列 | `IAvaSequencePlaybackObject` |
| `Pause Sequences (by Tag)` | 暂停匹配 Tag 的序列 | `IAvaSequencePlaybackObject` |
| `Stop Sequences (by Label)` | 停止匹配标签名的序列 | `IAvaSequencePlaybackObject` |
| `Stop Sequences (by Tag)` | 停止匹配 Tag 的序列 | `IAvaSequencePlaybackObject` |
| `Get Active Sequence Players` | 获取所有正在播放的序列播放器 | `IAvaSequencePlaybackObject` |
| `Has Active Sequence Players` | 检查是否有正在播放的序列 | `IAvaSequencePlaybackObject` |

### 序列查询与属性（UAvaSequence）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Label` | 获取序列标签名 | `UAvaSequence` |
| `Set Label` | 设置序列标签名 | `UAvaSequence` |
| `Get Sequence Tag` | 获取序列的 GameplayTag | `UAvaSequence` |
| `Get Start Time` | 获取序列起始时间 | `UAvaSequence` |
| `Get End Time` | 获取序列结束时间 | `UAvaSequence` |
| `Get Marks` | 获取序列所有标记 | `UAvaSequence` |
| `Get Mark` | 通过标签获取单个标记信息 | `UAvaSequence` |
| `Set Mark` | 设置标记信息 | `UAvaSequence` |

### Director 蓝图内播放（UAvaSequenceDirector）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Play Scheduled Sequences` | 在 Director 蓝图中播放已调度序列 | `UAvaSequenceDirector` |
| `Play Sequences By Label` | 在 Director 蓝图中通过标签名播放序列 | `UAvaSequenceDirector` |
| `Get Playback Object` | 获取 Director 关联的播放对象 | `UAvaSequenceDirector` |

### 使用示例（蓝图描述）

**示例 1：通过标签名播放一组序列**

1. 调用 `Get Playback Object` 节点获取当前世界的播放对象
2. 将返回的 Playback Object 连接到 `Play Sequences (by Label)` 节点
3. 设置 `Sequence Label` 为 "Intro"，配置 `Play Settings`（可选设置起止帧、播放模式、循环次数等）
4. 返回值为 `UAvaSequencePlayer` 数组，可用于后续暂停/停止操作

**示例 2：通过 Tag 播放并等待完成**

1. 调用 `Get Playback Object` 获取播放对象
2. 连接到 `Play Sequences (by Tag)`，设置 `Tag Handle` 和 `Exact Match`
3. 调用 `Has Active Sequence Players` 轮询，直到返回 false 表示所有序列播放完毕

**示例 3：在 Director 蓝图中控制播放**

1. 创建一个继承自 `UAvaSequenceDirector` 的 Director 蓝图
2. 在蓝图中直接调用 `Play Sequences By Label` 或 `Play Scheduled Sequences`
3. Director 蓝图会自动绑定到序列的播放上下文

## C++ 用法

### 头文件引入

```cpp
#include "AvaSequence.h"
#include "AvaSequencePlayer.h"
#include "AvaSequenceSubsystem.h"
#include "AvaSequencePlaybackObject.h"
#include "AvaSequenceShared.h"
#include "AvaSequenceLibrary.h"
```

### 基本用法

**获取播放对象并播放序列（基于 AvaSequenceLibrary 和 AvaSequenceSubsystem）**

```cpp
// 获取序列子系统
UAvaSequenceSubsystem* Subsystem = UAvaSequenceSubsystem::Get(GetWorld());
if (!Subsystem) return;

// 获取当前关卡的播放对象
IAvaSequencePlaybackObject* PlaybackObject = Subsystem->FindPlaybackObject(GetWorld()->GetCurrentLevel());
if (!PlaybackObject) return;

// 通过标签名播放序列
FAvaSequencePlayParams PlayParams;
PlayParams.PlayMode = EAvaSequencePlayMode::Forward;
PlayParams.Start = FAvaSequenceTime(0.0);  // 从头播放
PlayParams.End = FAvaSequenceTime(FAvaSequenceTime::NoTimeConstraint);  // 播放到结束

TArray<UAvaSequencePlayer*> Players = PlaybackObject->PlaySequencesByLabel(FName("MySequenceLabel"), PlayParams);
```

**配置播放参数**

```cpp
// 设置播放速度和循环
FAvaSequencePlayParams PlayParams;
PlayParams.PlayMode = EAvaSequencePlayMode::Forward;
PlayParams.AdvancedSettings.LoopCount = -1;        // 无限循环
PlayParams.AdvancedSettings.PlaybackSpeed = 2.0f;  // 2倍速
PlayParams.AdvancedSettings.bRestoreState = true;   // 停止后恢复初始状态

// 使用时间约束
PlayParams.Start = FAvaSequenceTime(1.5);  // 从 1.5 秒处开始
PlayParams.End = FAvaSequenceTime(3.0);    // 到 3.0 秒处结束

// 也可以用帧或标记
PlayParams.Start = FAvaSequenceTime(FFrameTime(30));        // 从第 30 帧开始
PlayParams.End = FAvaSequenceTime(FString("LoopPoint"));    // 到 "LoopPoint" 标记处结束
```

**暂停和继续序列**

```cpp
// 通过标签暂停
PlaybackObject->PauseSequencesByLabel(FName("Background"));

// 通过 GameplayTag 暂停
FAvaTagHandle TagHandle;
// ... 设置 Tag
PlaybackObject->PauseSequencesByTag(TagHandle, false);

// 继续播放
PlaybackObject->ContinueSequencesByLabel(FName("Background"));
```

**查询活动播放器**

```cpp
TArray<UAvaSequencePlayer*> AllPlayers = PlaybackObject->GetAllSequencePlayers();
for (UAvaSequencePlayer* Player : AllPlayers)
{
    if (Player && Player->GetAvaSequence())
    {
        UE_LOG(LogTemp, Log, TEXT("Playing: %s"), *Player->GetAvaSequence()->GetLabel().ToString());
    }
}
```

### 进阶用法

**UAvaSequence 的标签与标记管理**

```cpp
// 获取序列对象
UAvaSequence* Sequence = /* ... */;

// 设置序列标签（用于批量查找）
Sequence->SetLabel(FName("UI_Animation"));

// 设置序列的 GameplayTag
FAvaTagHandle TagHandle;
Sequence->SetSequenceTag(TagHandle);

// 查询标记
const TSet<FAvaMark>& Marks = Sequence->GetMarks();
for (const FAvaMark& Mark : Marks)
{
    UE_LOG(LogTemp, Log, TEXT("Mark: %s, Role: %d, Direction: %d"),
        *FString(Mark.GetLabel()), (int32)Mark.Role, (int32)Mark.Direction);
}

// 获取预览标记（编辑器中用）
const FAvaMark* PreviewMark = Sequence->GetPreviewMark();
```

**StateTree 转场任务集成**

```cpp
// FAvaTransitionPlaySequenceTask 用于在 StateTree 状态切换时播放序列
// 在 StateTree 编辑器中配置:
// - QueryType: 通过 Name 或 Tag 查找序列
// - WaitType: NoWait（发后不管）或 WaitUntilStop（等待序列结束）
// - PlaySettings: 播放参数

// 也可以在 C++ 中自定义任务继承 FAvaTransitionSequenceTaskBase:
struct FAvaMyCustomSequenceTask : public FAvaTransitionSequenceTaskBase
{
    using FInstanceDataType = FAvaTransitionSequenceTaskBaseInstanceData;

    virtual TArray<UAvaSequencePlayer*> ExecuteSequenceTask(
        FStateTreeExecutionContext& InContext) const override
    {
        // 根据 QueryType 查找并播放序列
        const FInstanceDataType& InstanceData = InContext.GetInstanceData(*this);
        
        IAvaSequencePlaybackObject* PlaybackObject = GetPlaybackObject(InContext);
        if (!PlaybackObject) return {};

        if (InstanceData.QueryType == EAvaTransitionSequenceQueryType::Name)
        {
            return PlaybackObject->PlaySequencesByLabel(
                InstanceData.SequenceName, FAvaSequencePlayParams());
        }
        return PlaybackObject->PlaySequencesByTag(
            InstanceData.SequenceTag, InstanceData.bPerformExactMatch, FAvaSequencePlayParams());
    }
};
```

**自定义序列提供者（IAvaSequenceProvider）**

```cpp
// 实现 IAvaSequenceProvider 接口以提供自定义的序列管理
class UMySequenceProvider : public UObject, public IAvaSequenceProvider
{
    GENERATED_BODY()

public:
    virtual FName GetSequenceProviderDebugName() const override
    {
        return FName("MyProvider");
    }

    virtual UObject* ToUObject() override { return this; }
    virtual UWorld* GetContextWorld() const override { return GetWorld(); }

    virtual bool AddSequence(UAvaSequence* InSequence) override
    {
        if (InSequence && !Sequences.Contains(InSequence))
        {
            Sequences.Add(InSequence);
            return true;
        }
        return false;
    }

    virtual const TArray<TObjectPtr<UAvaSequence>>& GetSequences() const override
    {
        return Sequences;
    }

    // ... 其他接口方法实现

private:
    TArray<TObjectPtr<UAvaSequence>> Sequences;
};
```

**注册到序列子系统**

```cpp
// 在 Level 初始化时注册提供者
UAvaSequenceSubsystem* Subsystem = UAvaSequenceSubsystem::Get(GetWorld());
if (Subsystem)
{
    Subsystem->RegisterSequenceProvider(GetLevel(), MyProvider);
    
    // 查找或创建播放对象
    IAvaSequencePlaybackObject* PlaybackObject = 
        Subsystem->FindOrCreatePlaybackObject(GetLevel(), *MyProvider);
}
```

## Demo 示例

**自定义序列播放器组件**

```cpp
// MySequencePlayerComponent.h
#pragma once

#include "Components/ActorComponent.h"
#include "AvaSequenceShared.h"
#include "MySequencePlayerComponent.generated.h"

class IAvaSequencePlaybackObject;
class UAvaSequencePlayer;

UCLASS(ClassGroup=(MotionDesign), meta=(BlueprintSpawnableComponent))
class MYGAME_API UMySequencePlayerComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UMySequencePlayerComponent();

    /** 通过标签名播放序列 */
    UFUNCTION(BlueprintCallable, Category = "MySequence")
    void PlaySequenceByLabel(FName InLabel);

    /** 暂停所有匹配标签的序列 */
    UFUNCTION(BlueprintCallable, Category = "MySequence")
    void PauseSequencesByLabel(FName InLabel);

    /** 继续所有匹配标签的序列 */
    UFUNCTION(BlueprintCallable, Category = "MySequence")
    void ResumeSequencesByLabel(FName InLabel);

    /** 停止所有匹配标签的序列 */
    UFUNCTION(BlueprintCallable, Category = "MySequence")
    void StopSequencesByLabel(FName InLabel);

    /** 检查是否有活动序列 */
    UFUNCTION(BlueprintPure, Category = "MySequence")
    bool HasActiveSequences() const;

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    IAvaSequencePlaybackObject* GetPlaybackObject() const;
};
```

```cpp
// MySequencePlayerComponent.cpp
#include "MySequencePlayerComponent.h"
#include "AvaSequenceSubsystem.h"
#include "AvaSequencePlaybackObject.h"
#include "AvaSequencePlayer.h"

UMySequencePlayerComponent::UMySequencePlayerComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UMySequencePlayerComponent::BeginPlay()
{
    Super::BeginPlay();
}

void UMySequencePlayerComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    // 停止所有活动序列
    if (IAvaSequencePlaybackObject* PlaybackObject = GetPlaybackObject())
    {
        TArray<UAvaSequencePlayer*> Players = PlaybackObject->GetAllSequencePlayers();
        for (UAvaSequencePlayer* Player : Players)
        {
            if (Player && Player->GetAvaSequence())
            {
                PlaybackObject->StopSequence(Player->GetAvaSequence());
            }
        }
    }
    Super::EndPlay(EndPlayReason);
}

IAvaSequencePlaybackObject* UMySequencePlayerComponent::GetPlaybackObject() const
{
    UAvaSequenceSubsystem* Subsystem = UAvaSequenceSubsystem::Get(GetWorld());
    if (!Subsystem) return nullptr;
    return Subsystem->FindPlaybackObject(GetOwner()->GetLevel());
}

void UMySequencePlayerComponent::PlaySequenceByLabel(FName InLabel)
{
    IAvaSequencePlaybackObject* PlaybackObject = GetPlaybackObject();
    if (!PlaybackObject) return;

    FAvaSequencePlayParams PlayParams;
    PlayParams.PlayMode = EAvaSequencePlayMode::Forward;
    PlaybackObject->PlaySequencesByLabel(InLabel, PlayParams);
}

void UMySequencePlayerComponent::PauseSequencesByLabel(FName InLabel)
{
    if (IAvaSequencePlaybackObject* PlaybackObject = GetPlaybackObject())
    {
        PlaybackObject->PauseSequencesByLabel(InLabel);
    }
}

void UMySequencePlayerComponent::ResumeSequencesByLabel(FName InLabel)
{
    if (IAvaSequencePlaybackObject* PlaybackObject = GetPlaybackObject())
    {
        PlaybackObject->ContinueSequencesByLabel(InLabel);
    }
}

void UMySequencePlayerComponent::StopSequencesByLabel(FName InLabel)
{
    if (IAvaSequencePlaybackObject* PlaybackObject = GetPlaybackObject())
    {
        PlaybackObject->StopSequencesByLabel(InLabel);
    }
}

bool UMySequencePlayerComponent::HasActiveSequences() const
{
    if (IAvaSequencePlaybackObject* PlaybackObject = GetPlaybackObject())
    {
        return PlaybackObject->HasActiveSequencePlayers();
    }
    return false;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AvalancheTag` | 提供 FAvaTagHandle 标签系统，用于序列标签匹配 |
| `AvalancheCore` | Motion Design 核心框架 |
| `Sequencer` | StateTree 转场集成依赖（AvalanchePropertyAnimator 模块） |
| `LevelSequence` | UAvaSequence 基类 ULevelSequence 所在模块 |
| `MovieScene` | 序列播放器、帧时间、标记帧等基础 Sequencer 类型 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将动态设计的标签页从关卡编辑器分离到独立分组 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 添加 MRQ 分析功能，用于追踪节目单页面设置使用情况 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 为节目控制工具栏添加页面加载选项（全部/下一个/已选择） |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 添加项目设置，可强制禁用 Text3D 和形状的碰撞 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构视口客户端关联/解除关联的通知机制 |

### 维护评价

**活跃维护** 🟢

- **创建时间**：2025 年 5 月，约 1 年前从 Experimental 迁移到 VirtualProduction 目录
- **近期活跃度**：最近 1 周内有多次提交（2026-05-14 ~ 2026-05-20），处于高频开发阶段
- **开发性质**：Epic Games 官方维护，属于 Virtual Production 工作流核心组件
- **规模**：整个 Motion Design 插件包含 43 个模块、2060+ 源文件，是 Epic 目前在虚拟制片方向投入最大的工具集之一
- **依赖链**：依赖大量其他插件（Remote Control、Media Compositing、Text3D 等），说明其定位为核心枢纽

**推荐使用**：对于虚拟制片和动态图形场景，该插件是 Epic 官方推荐的工具链，处于积极开发中。但需注意：
- 该插件需要手动启用（EnabledByDefault=false）
- 依赖众多其他插件，需确保所有依赖项已启用
- 作为较新的插件，API 可能会有变动

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheSequence)
- [插件根目录](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/motion-design-in-unreal-engine)