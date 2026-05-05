# Take Recorder

> A suite of tools and interfaces designed for recording, reviewing and playing back takes in a virtual production environment.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（资产） |
| 模块 | `CacheTrackRecorder` (Runtime), `TakeMovieScene` (Runtime), `TakeRecorder` (Runtime), `TakeRecorderNamingTokens` (Runtime), `TakeRecorderSources` (Runtime), `TakesCore` (Runtime), `TakeSequencer` (Runtime), `TakeTrackRecorders` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-01-10 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Takes) | |

## 用途

Take Recorder 是 Unreal Engine 虚拟制作管线的核心录制工具。它解决的核心问题是：在虚拟制作（Virtual Production）环境中，如何**同步、精确地录制来自多个不同来源（如演员动作捕捉、虚拟摄像机、音频、灯光等）的数据**，并将其整合到一个统一的 Level Sequence 中，以便后续审查、编辑和回放。

它不仅仅是一个简单的录制器，而是一个完整的**录制管理系统**，提供了：
1.  **多源数据同步录制**：支持同时录制来自不同设备（如 Live Link、音频输入、蓝图属性）的数据。
2.  **Take 管理**：通过 Slate（场记板）和 Take Number 系统，像电影拍摄一样组织和管理多次录制尝试。
3.  **元数据记录**：自动记录每次录制的时间、日期、设置等元数据。
4.  **录制后审查**：提供即时回放和审查功能，无需离开编辑器。
5.  **预设系统**：可以将录制配置保存为预设（Take Preset），方便快速复用。
6.  **可扩展架构**：通过模块化接口（如 `ITakeRecorderDropHandler`、`ITakeRecorderSubsystemInterface`）允许开发者添加自定义数据源和功能。

其存在是为了将虚拟制作的实时录制流程标准化、自动化，并与 UE 的 Sequencer 系统深度集成，成为连接现场表演与后期制作的关键桥梁。

## 使用场景

-   **虚拟制片（Virtual Production）**：在 LED 墙或绿幕前拍摄时，同步录制演员的表演数据（通过 Live Link）、虚拟摄像机的运动、音频以及场景中其他元素的动画。
-   **动作捕捉（Motion Capture）**：录制来自光学或惯性动捕系统的数据，并将其直接应用到场景中的角色上。
-   **多机位录制**：同时控制和录制多个虚拟摄像机的视角，模拟多机位拍摄。
-   **自动化测试与数据采集**：需要精确记录游戏运行时特定对象状态变化的场景，用于后续分析或回放。
-   **快速原型迭代**：设计师或动画师希望快速录制一段角色动画或镜头运动，并立即在 Sequencer 中查看和调整。

## 蓝图用法

Take Recorder 提供了丰富的蓝图接口，主要通过 `UTakeRecorderSubsystem` 和 `UTakeRecorderBlueprintLibrary` 暴露。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Target Sequence` | 设置录制的目标序列（新建、录制到已有序列或使用预设）。**必须首先调用**。 | `UTakeRecorderSubsystem` |
| `Start Recording` | 开始录制。可选是否打开 Sequencer 窗口。 | `UTakeRecorderSubsystem` |
| `Stop Recording` | 停止当前录制。 | `UTakeRecorderSubsystem` |
| `Cancel Recording` | 取消当前录制，丢弃已录制的数据。 | `UTakeRecorderSubsystem` |
| `Add Source For Actor` | 为指定的 Actor 添加一个录制源。 | `UTakeRecorderSubsystem` |
| `Remove Actor From Sources` | 从录制源中移除指定的 Actor。 | `UTakeRecorderSubsystem` |
| `Get Active Recorder` | 获取当前活动的 `UTakeRecorder` 实例。 | `UTakeRecorderBlueprintLibrary` |
| `Is Recording` | 检查是否正在录制。 | `UTakeRecorderBlueprintLibrary` |
| `Get Take Recorder Panel` | 获取或打开 Take Recorder 的 UI 面板。 | `UTakeRecorderBlueprintLibrary` |

### 使用示例（蓝图描述）

1.  **基础录制流程**：
    *   从 `Get Game Instance` 节点获取实例，然后调用 `Get Subsystem` 并选择 `Take Recorder Subsystem`。
    *   调用 `Set Target Sequence`，在 `In Data` 参数中，可以设置 `New Sequence` 为 `true` 来创建新序列，或指定一个已有的 `Level Sequence`。
    *   调用 `Add Source For Actor`，传入你想要录制的 Actor 引用。
    *   调用 `Start Recording`。
    *   （录制中...）
    *   调用 `Stop Recording` 结束录制。

2.  **监听录制事件**：
    *   在 `Take Recorder Subsystem` 的实例上，可以绑定如 `On Take Recorder Started`、`On Take Recorder Finished` 等动态多播委托，以便在录制生命周期的关键节点执行自定义逻辑。

## C++ 用法

### 头文件引入

```cpp
#include "TakeRecorderSubsystem.h"
#include "TakeRecorderBlueprintLibrary.h"
#include "Recorder/TakeRecorderParameters.h"
```

### 基本用法

通过 `UTakeRecorderSubsystem` 控制录制流程。

```cpp
// 假设在某个 Actor 或 Subsystem 中
void AMyActor::StartMyRecording()
{
    // 1. 获取 Take Recorder 子系统
    UTakeRecorderSubsystem* TakeRecorderSubsystem = GEngine->GetEngineSubsystem<UTakeRecorderSubsystem>();
    if (!TakeRecorderSubsystem)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to get Take Recorder Subsystem."));
        return;
    }

    // 2. 设置目标序列（创建新序列）
    FTakeRecorderSequenceParameters SequenceParams;
    SequenceParams.bNewSequence = true;
    TakeRecorderSubsystem->SetTargetSequence(SequenceParams);

    // 3. 添加要录制的 Actor 作为源
    if (AActor* ActorToRecord = GetMyTargetActor())
    {
        TakeRecorderSubsystem->AddSourceForActor(ActorToRecord, true, true);
    }

    // 4. 开始录制
    bool bSuccess = TakeRecorderSubsystem->StartRecording(true, true);
    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("Recording started successfully."));
    }
}

void AMyActor::StopMyRecording()
{
    UTakeRecorderSubsystem* TakeRecorderSubsystem = GEngine->GetEngineSubsystem<UTakeRecorderSubsystem>();
    if (TakeRecorderSubsystem)
    {
        TakeRecorderSubsystem->StopRecording();
    }
}
```

### 进阶用法

监听录制事件并获取录制结果。

```cpp
// 在某个初始化函数中绑定委托
void AMyActor::BeginPlay()
{
    Super::BeginPlay();

    UTakeRecorderSubsystem* TakeRecorderSubsystem = GEngine->GetEngineSubsystem<UTakeRecorderSubsystem>();
    if (TakeRecorderSubsystem)
    {
        // 绑定录制完成事件
        TakeRecorderSubsystem->OnTakeRecorderFinished.AddDynamic(this, &AMyActor::OnRecordingFinished);
    }
}

// 事件回调函数
void AMyActor::OnRecordingFinished(ULevelSequence* RecordedSequence)
{
    if (RecordedSequence)
    {
        UE_LOG(LogTemp, Log, TEXT("Recording finished. Sequence asset: %s"), *RecordedSequence->GetName());
        // 在这里可以对录制完成的序列进行后续处理，例如打开它
    }
}
```

## Demo 示例

一个最小的 C++ 示例，展示如何通过子系统控制 Take Recorder。

**MyRecordingActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyRecordingActor.generated.h"

UCLASS()
class MYPROJECT_API AMyRecordingActor : public AActor
{
    GENERATED_BODY()

public:
    AMyRecordingActor();

protected:
    virtual void BeginPlay() override;

public:
    UFUNCTION(BlueprintCallable, Category = "Recording")
    void StartRecording();

    UFUNCTION(BlueprintCallable, Category = "Recording")
    void StopRecording();

private:
    UFUNCTION()
    void OnRecordingFinished(ULevelSequence* RecordedSequence);
};
```

**MyRecordingActor.cpp**
```cpp
#include "MyRecordingActor.h"
#include "TakeRecorderSubsystem.h"
#include "LevelSequence.h"

AMyRecordingActor::AMyRecordingActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyRecordingActor::BeginPlay()
{
    Super::BeginPlay();

    // 绑定录制完成事件
    UTakeRecorderSubsystem* Subsystem = GEngine->GetEngineSubsystem<UTakeRecorderSubsystem>();
    if (Subsystem)
    {
        Subsystem->OnTakeRecorderFinished.AddDynamic(this, &AMyRecordingActor::OnRecordingFinished);
    }
}

void AMyRecordingActor::StartRecording()
{
    UTakeRecorderSubsystem* Subsystem = GEngine->GetEngineSubsystem<UTakeRecorderSubsystem>();
    if (!Subsystem) return;

    // 设置为创建新序列
    FTakeRecorderSequenceParameters Params;
    Params.bNewSequence = true;
    Subsystem->SetTargetSequence(Params);

    // 将自身添加为录制源
    Subsystem->AddSourceForActor(this, true, true);

    // 开始录制
    Subsystem->StartRecording(true, true);
}

void AMyRecordingActor::StopRecording()
{
    UTakeRecorderSubsystem* Subsystem = GEngine->GetEngineSubsystem<UTakeRecorderSubsystem>();
    if (Subsystem)
    {
        Subsystem->StopRecording();
    }
}

void AMyRecordingActor::OnRecordingFinished(ULevelSequence* RecordedSequence)
{
    if (RecordedSequence)
    {
        UE_LOG(LogTemp, Warning, TEXT("Recording complete! Sequence: %s"), *RecordedSequence->GetPathName());
    }
}
```

## 模块依赖

从模块名称和头文件包含关系推断，使用 Take Recorder 功能通常需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `TakesCore` | 提供 Take 系统的核心数据结构和接口（如 `UTakeMetaData`, `UTakePreset`）。 |
| `TakeRecorderSources` | 定义和管理各种录制数据源（`UTakeRecorderSource`）。 |
| `TakeMovieScene` | 将录制的数据转换为 MovieScene 轨道和片段。 |
| `TakeSequencer` | 与 Sequencer 编辑器集成，提供录制时的 UI 和交互。 |
| `MovieScene` | UE 的序列器核心模块，处理时间轴、轨道和关键帧。 |
| `Sequencer` | Sequencer 编辑器模块，用于查看和编辑录制结果。 |
| `LiveLinkInterface` | （如果需要录制 Live Link 数据）Live Link 框架的核心接口。 |

## 维护状态

### 近期更新

```
- 8667f82a634e Take Recorder: Introduce bStopOnRollover setting, which causes recording to stop once timecode rolls over. This prevents the user from having a broken level sequence if timecode rolls over.
- dda1e95b930d [Backout] - CL46059773 [FYI] jason.walter #rnx Original CL Desc ----------------------------------------------------------------- Check for external references before save.
- c8ce00b861ef Take Recorder: Fix genlocked engine timestep being overriden by hitch protection.
```

*   `8667f82a634e` (2025-10-03): 新增了 `bStopOnRollover` 设置，当时间码发生翻转（如从 23:59:59 到 00:00:00）时自动停止录制，防止生成损坏的序列。这是一个重要的功能增强。
*   `dda1e95b930d` (2025-09-15): 回退了一个关于保存前检查外部引用的更改。这表明该功能可能引入了问题，团队选择了回退以保证稳定性。
*   `c8ce00b861ef` (2025-08-20): 修复了一个 Bug，该 Bug 导致 Genlock 引擎时间步长被卡顿保护（Hitch Protection）设置覆盖。这是一个针对虚拟制作中同步问题的关键修复。

### 维护评价

Take Recorder 是一个**活跃维护中**的核心虚拟制作工具。
- **年龄**：创建于 2019 年，已有约 6 年历史，属于成熟模块。
- **更新频率**：最近 3 个月（截至 2025 年 10 月）有 3 次提交，包含新功能和关键 Bug 修复，表明 Epic 仍在积极投入。
- **功能状态**：作为 Virtual Production 分类下的默认启用插件，它是 Epic 官方虚拟制作工作流的基石，不太可能被废弃。
- **已知限制**：从提交历史看，其与时间码、Genlock 和引擎时间步长的交互是复杂且容易出错的领域，使用时需要注意相关设置。
- **推荐使用**：**强烈推荐**。对于任何涉及虚拟制作、动作捕捉或多源数据同步录制的项目，Take Recorder 是官方且功能完备的解决方案。其子系统架构也便于在 C++ 和蓝图中进行深度集成和自动化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Takes)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/take-recorder-in-unreal-engine/) (UE5 官方文档链接)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Takes/Tests) (如果存在)