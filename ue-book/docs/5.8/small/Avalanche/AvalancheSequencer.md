# Motion Design

> Compositing, designer and broadcasting tool. Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质、工具、测试资源） |
| 模块 | `Avalanche` (Runtime), `AvalancheAttribute` (Runtime), `AvalancheAttributeEditor` (Runtime), `AvalancheCamera` (Runtime), `AvalancheComponentVisualizers` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), `AvalancheEditorCore` (Runtime), `AvalancheEffectors` (Runtime), `AvalancheEffectorsEditor` (Runtime), `AvalancheFunctionalTest` (Runtime), `AvalancheInteractiveTools` (Runtime), `AvalancheInteractiveToolsRuntime` (Runtime), `AvalancheLevelViewport` (Runtime), `AvalancheMRQ` (Runtime), `AvalancheMRQEditor` (Runtime), `AvalancheMask` (Runtime), `AvalancheMaskEditor` (Runtime), `AvalancheMaterial` (Runtime), `AvalancheMedia` (Runtime), `AvalancheMediaEditor` (Runtime), `AvalancheModifiers` (Runtime), `AvalancheModifiersEditor` (Runtime), `AvalancheOutliner` (Runtime), `AvalanchePropertyAnimator` (Runtime), `AvalanchePropertyAnimatorEditor` (Runtime), `AvalancheRemoteControl` (Runtime), `AvalancheRemoteControlEditor` (Runtime), `AvalancheSVGEditor` (Runtime), `AvalancheSceneRig` (Runtime), `AvalancheSceneRigEditor` (Runtime), `AvalancheSceneTree` (Runtime), `AvalancheSequence` (Runtime), `AvalancheSequencer` (Runtime), `AvalancheShapes` (Runtime), `AvalancheShapesEditor` (Runtime), `AvalancheTag` (Runtime), `AvalancheTagEditor` (Runtime), `AvalancheText` (Runtime), `AvalancheTextEditor` (Runtime), `AvalancheTransition` (Runtime), `AvalancheTransitionEditor` (Runtime), `AvalancheViewport` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Avalanche (Motion Design) 插件是一个面向**虚拟制作、广播和实时图形**的综合工具套件。它并非简单地将几个功能拼接在一起，而是构建了一套完整的**动态设计（Motion Design）工作流**，旨在解决以下核心问题：
1.  **序列管理与复用**：扩展标准的 Unreal Sequencer，引入 `UAvaSequence` 作为更灵活的序列单元，支持**预设（Presets）**、**预设组（Preset Groups）** 和**交错（Stagger）** 等高级编排功能，便于在直播或节目中快速创建和复用动画序列。
2.  **合成与效果集成**：集成了媒体合成、材质设计、几何缓存、文本3D、遮罩、克隆/效果器等功能，允许在 Sequencer 时间线内直接控制复杂的视觉效果和媒体播放，实现广播级的合成。
3.  **自定义与扩展性**：通过 `IAvaSequencerProvider` 等接口，允许深度定制 Sequencer 的行为、播放上下文和编辑体验，使其能适配特定的广播系统或演播室控制软件。
4.  **远程控制与播放**：内置远程控制支持，便于与外部系统（如 SDI 信号发生器、OBS 等）集成，实现自动化和远程触发序列。

简而言之，这个插件将 Unreal Engine 的 Sequencer 从一个主要面向关卡动画的工具，转变为一个专为**直播包装、虚拟演播室、实时图形驱动**而设计的强大动态设计引擎。

## 使用场景

-   你正在制作一个**电视直播节目**的虚拟演播室背景和图形 → 使用 Motion Design 的序列预设和远程控制功能，根据节目流程（如主持人出场、广告插播）精确触发不同的动画和媒体播放。
-   你需要为一个**大型活动（如颁奖礼、电竞比赛）** 设计实时生成的选手介绍图形、比分板和转场动画 → 利用 `AvalancheSequencer` 的交错工具和序列树管理大量、可动态替换的图形模板。
-   你想在 Unreal 中创建**复杂的广播级合成**，将摄像机视频源、3D 场景、文字和特效实时混合 → 结合 `AvalancheMedia`、`AvalancheMaterial`、`AvalancheText` 等模块，通过 Sequencer 统一控制。
-   你需要一个**标准化的动画制作流程**，让设计师可以快速创建符合品牌规范（时长、过渡、标签）的动画片段 → 使用 `UAvaSequencePreset` 和 `UAvaSequencerSettings` 来强制执行标准。

## 蓝图用法

AvalancheSequencer 模块主要提供底层 C++ 接口和编辑器功能，其核心的序列管理 API 通过 `IAvaSequencer` 接口暴露。以下是一些关键的公开接口：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Sequencer` | 获取或创建当前世界的 Motion Design Sequencer 实例 | `UAvaSequencerSubsystem` |
| `Get Viewed Sequence` | 获取 Sequencer 当前正在查看/编辑的 `UAvaSequence` | `IAvaSequencer` (通过子系统或 Provider 获取) |
| `Set Viewed Sequence` | 设置 Sequencer 要查看/编辑的序列 | `IAvaSequencer` |
| `Get Sequences For Object` | 查找所有包含指定对象（如 Actor）的序列 | `IAvaSequencer` |
| `Add Sequence` | 创建一个新的 `UAvaSequence`（可指定父序列） | `IAvaSequencer` |
| `Add Sequences From Presets` | 基于一个或多个预设快速创建序列 | `IAvaSequencer` |
| `Delete Sequences` | 删除指定的序列集合 | `IAvaSequencer` |
| `Play / Continue / Stop Sequences` | 控制选定序列的播放、继续和停止（通过命令） | `FAvaSequencer` (内部命令映射) |

### 使用示例（蓝图描述）

1.  **获取并播放一个预设序列**：
    -   从 `UAvaSequencerSubsystem` 调用 `Get Sequencer` 节点获取 `IAvaSequencer` 接口。
    -   调用 `Get Sequencer Settings` 节点获取 `UAvaSequencerSettings`。
    -   使用 `Find Preset` 节点（输入如 “IntroAnimation”）查找预设。
    -   将找到的预设作为参数，调用 `Add Sequences From Presets` 节点。
    -   （可选）使用返回的序列，通过 `Set Viewed Sequence` 在编辑器中查看它。

2.  **在 Gameplay 中触发序列播放**：
    -   确保在项目的 Motion Design Sequencer 设置中配置了远程控制。
    -   在游戏逻辑中（如某个 Actor 的事件），通过 `Remote Control` 模块暴露的属性或函数，向 Sequencer 发送播放命令（例如 “Play: SequenceName”）。

## C++ 用法

### 头文件引入

```cpp
#include "AvaSequencerSubsystem.h"
#include "IAvaSequencer.h"
#include "IAvaSequencerProvider.h"
#include "Settings/AvaSequencerSettings.h"
#include "Settings/AvaSequencePreset.h"
```

### 基本用法

```cpp
// 1. 获取 Sequencer 子系统
UAvaSequencerSubsystem* SequencerSubsystem = GetWorld()->GetSubsystem<UAvaSequencerSubsystem>();
if (SequencerSubsystem)
{
    // 2. 获取或创建 Sequencer 实例 (通常由 Provider 触发创建)
    // TSharedRef<IAvaSequencer> AvaSequencer = SequencerSubsystem->GetOrCreateSequencer(Provider, Args);
    
    // 3. 通过 Sequencer 创建一个新序列
    if (TSharedPtr<IAvaSequencer> AvaSequencerPtr = SequencerSubsystem->GetSequencer())
    {
        if (UAvaSequence* NewSequence = AvaSequencerPtr->AddSequence())
        {
            UE_LOG(LogTemp, Log, TEXT("Created new Ava Sequence: %s"), *NewSequence->GetName());
            
            // 设置序列参数 (可选，也可以使用预设)
            NewSequence->SetSequenceEnd(5.0f); // 设置5秒结束时间
        }
        
        // 4. 应用预设创建序列
        const UAvaSequencerSettings* Settings = GetDefault<UAvaSequencerSettings>();
        const FAvaSequencePreset* Preset = Settings->FindPreset(FName("MyPreset"));
        if (Preset)
        {
            TArray<const FAvaSequencePreset*> PresetsToApply = { Preset };
            uint32 CreatedCount = AvaSequencerPtr->AddSequenceFromPresets(PresetsToApply);
            UE_LOG(LogTemp, Log, TEXT("Created %u sequences from preset."), CreatedCount);
        }
    }
}
```
*（基于 `AvaSequencerSubsystem.h` 和 `IAvaSequencer.h` 的接口推断）*

### 进阶用法

实现 `IAvaSequencerProvider` 接口以深度集成到 Motion Design Sequencer。这通常用于创建自定义的编辑器模式或面板。

```cpp
// MyCustomSequencerProvider.h
#include "IAvaSequencerProvider.h"
#include "EditorModeTools.h"

class FMyCustomSequencerProvider : public IAvaSequencerProvider
{
public:
    FMyCustomSequencerProvider();
    virtual ~FMyCustomSequencerProvider() override;

    // IAvaSequencerProvider Interface
    virtual TSharedPtr<IAvaSequencer> GetAvaSequencer() const override;
    virtual IAvaSequenceProvider* GetSequenceProvider() const override;
    virtual FEditorModeTools* GetSequencerModeTools() const override;
    virtual IAvaSequencePlaybackObject* GetPlaybackObject() const override;
    virtual TSharedPtr<IToolkitHost> GetSequencerToolkitHost() const override;
    virtual UObject* GetPlaybackContext() const override;
    virtual bool CanEditOrPlaySequences() const override;
    // ... 其他接口实现
    virtual void OnViewedSequenceChanged(UAvaSequence* InOldSequence, UAvaSequence* InNewSequence) override;

private:
    TSharedPtr<IAvaSequencer> AvaSequencer;
    // ... 其他成员
};
```

```cpp
// MyCustomSequencerProvider.cpp
#include "MyCustomSequencerProvider.h"
#include "AvaSequencerSubsystem.h"

FMyCustomSequencerProvider::FMyCustomSequencerProvider()
{
    // 在构造时，通常通过子系统获取或初始化 Sequencer
    if (UWorld* World = GetWorld()) // 假设 GetWorld() 可用
    {
        UAvaSequencerSubsystem* Subsystem = World->GetSubsystem<UAvaSequencerSubsystem>();
        if (Subsystem)
        {
            FAvaSequencerArgs Args;
            Args.bUseCustomCleanPlaybackMode = true; // 启用自定义清洁播放模式
            AvaSequencer = Subsystem->GetOrCreateSequencer(*this, MoveTemp(Args));
        }
    }
}

void FMyCustomSequencerProvider::OnViewedSequenceChanged(UAvaSequence* InOldSequence, UAvaSequence* InNewSequence)
{
    // 当用户在 Sequencer 中切换序列时，在这里更新你的自定义 UI
    if (InNewSequence)
    {
        UE_LOG(LogTemp, Log, TEXT("Viewing new sequence: %s"), *InNewSequence->GetSequenceLabel().ToString());
    }
}

// ... 实现其他 IAvaSequencerProvider 方法
```
*（基于 `IAvaSequencerProvider.h` 的接口定义推断）*

## Demo 示例

一个最小化的示例，展示如何通过 C++ 代码触发 Motion Design Sequencer 创建序列。

```cpp
// MinSequenceCreator.h
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "MinSequenceCreator.generated.h"

UCLASS()
class UMinSequenceCreator : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "Motion Design Demo")
    void CreateDemoSequence();
};
```

```cpp
// MinSequenceCreator.cpp
#include "MinSequenceCreator.h"
#include "AvaSequencerSubsystem.h"
#include "IAvaSequencer.h"
#include "Engine/World.h"

void UMinSequenceCreator::CreateDemoSequence()
{
    UWorld* World = GetWorld();
    if (!World)
    {
        return;
    }

    // 1. 获取 Sequencer 子系统
    UAvaSequencerSubsystem* SequencerSubsystem = World->GetSubsystem<UAvaSequencerSubsystem>();
    if (!SequencerSubsystem)
    {
        UE_LOG(LogTemp, Error, TEXT("AvalancheSequencer Subsystem not found!"));
        return;
    }

    // 2. 尝试获取已有的 Sequencer 实例。
    // 注意：在独立游戏逻辑中，通常需要一个 Provider 来首次创建它。
    // 为简化，此处假设在编辑器或已有 Provider 的环境下。
    TSharedPtr<IAvaSequencer> AvaSequencer = SequencerSubsystem->GetSequencer();
    if (!AvaSequencer.IsValid())
    {
        UE_LOG(LogTemp, Warning, TEXT("No active AvaSequencer found. Creation might require an active editor/provider."));
        return;
    }

    // 3. 创建一个新的序列
    UAvaSequence* NewSequence = AvaSequencer->AddSequence();
    if (NewSequence)
    {
        // 4. (可选) 为序列设置一些初始属性
        NewSequence->SetSequenceLabel(FName("DemoSequence_CPP"));
        NewSequence->SetSequenceEnd(3.0f); // 持续时间 3 秒

        UE_LOG(LogTemp, Log, TEXT("Successfully created demo sequence: %s"), *NewSequence->GetSequenceLabel().ToString());
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create new AvaSequence."));
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Sequencer` | 核心依赖，AvalancheSequencer 扩展了 Unreal 的序列器功能。 |
| `UMG` | 用于创建 Sequencer 的自定义 UI（如序列树、交错工具窗口）。 |
| `PropertyEditor` | 用于实现序列属性、预设等的自定义细节面板。 |
| `NavigationTool` | （可选）用于集成到编辑器的导航工具中。 |
| `EditorInteractiveToolsFramework` | 用于支持在 Sequencer 中开发的交互式编辑工具。 |
| `AvalancheCore` | 本插件的核心运行时库，提供基础类型和接口。 |
| `AvalancheEditorCore` | 本插件的编辑器核心库，提供编辑器扩展基础设施。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将运动设计的“场景设置”和“大纲”选项卡移至编辑器中的独立分组，优化了编辑器布局。 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 添加了在使用“节目单页面”设置时对 MRQ（Movie Render Queue）的分析统计功能。 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 为节目控制工具栏添加了页面加载选项（全部、下一个、已选），并增加了相关设置。 |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 新增项目设置，可强制禁用 Text3D 和形状的碰撞，避免不必要的物理计算。 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口优化：重构代码，通过通知客户端其关联状态来减少冗余的复制粘贴代码。 |

### 维护评价

**活跃维护**。

-   **创建时间**：约 1 年前（2025年5月），属于较新的插件。
-   **更新频率**：近期（2026年5月）有密集的功能更新和优化，表明仍在积极开发。
-   **维护内容**：更新集中在功能增强（如 MRQ 分析、页面加载选项）、编辑器体验优化（UI 重构）和项目设置扩展上，而非单纯的编译修复，说明插件在持续演进。
-   **状态**：作为 Epic Games 开发的官方 Virtual Production 工具套件，预计会得到长期维护。
-   **推荐使用**：强烈推荐。如果你正在从事与虚拟制作、广播或实时图形相关的 Unreal Engine 项目，这个插件提供了强大且专业的解决方案。注意它默认是禁用的，需要手动启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- 官方文档：无（.uplugin 中未提供）
- 测试用例：无（.uplugin 中未提供路径）