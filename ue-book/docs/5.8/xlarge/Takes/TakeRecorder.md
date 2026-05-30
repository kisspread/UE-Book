# Takes

> A suite of tools and interfaces designed for recording, reviewing and playing back takes in a virtual production environment.

| 属性 | 值 |
|---|---|
| 中文名 | 录制工具集 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、预设资产、UI 资源） |
| 模块 | `CacheTrackRecorder` (Runtime), `TakeMovieScene` (Runtime), `TakeRecorder` (Runtime), `TakeRecorderEditor` (Runtime), `TakeRecorderNamingTokens` (Runtime), `TakeRecorderSources` (Runtime), `TakeSequencer` (Runtime), `TakeTrackRecorders` (Runtime), `TakesCore` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-01-11 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Takes) | |

## 用途

Takes 是虚拟制片（Virtual Production）环境下的**录制、回放和管理 Take** 的完整工具套件。它解决的核心问题是：在实时渲染场景（如 LED Volume、动作捕捉舞台）中，需要像传统影视拍摄一样对每一"条"（Take）进行编号、录制、回放和对比。

具体来说，Takes 插件提供了以下能力：

1. **录制运行时数据到 Sequencer**：将 Actor 变换、动画、摄像机、音频等运行时数据录制为 Level Sequence 资产，支持 Possessable 和 Spawnable 两种绑定模式
2. **Slate/Take 编号管理**：模拟影视工业的 Slate（场记板）和 Take Number（第几条）工作流，自动递增编号
3. **多源录制架构**：通过 `UTakeRecorderSource` 插件化架构，支持同时录制多个不同类型的源（Actor、摄像机、音频、自定义属性等）
4. **预设系统**：通过 `UTakePreset` 保存和复用录制配置，确保多次录制的一致性
5. **防卡顿保护（Hitch Protection）**：在录制过程中，如果引擎出现帧卡顿，通过固定时间步长和线性回归算法补偿，确保录制数据的时间码均匀
6. **命名令牌（Naming Tokens）**：支持在文件路径和名称中使用动态令牌（如 `{slate}`、`{take}`、`{year}`），自动替换为实际值
7. **回放与审查**：录制完成后可立即回放和审查，支持标记关键帧（Mark Frame）

这个插件之所以存在，是因为虚拟制片需要在实时渲染和传统影视工作流之间架起桥梁。没有 Takes，用户就需要手动创建 Sequencer、手动设置动画录制、手动管理文件命名——Takes 将这些全部自动化。

## 使用场景

- 你在做虚拟制片（LED Volume 拍摄），需要录制演员在 Unreal 中的实时表演数据 → 用 Takes
- 你在做动作捕捉，需要将 Mocap 数据录制到 Sequencer 中并按 Slate/Take 管理 → 用 Takes
- 你需要录制摄像机动画、角色动画到 Sequencer 进行后期编辑 → 用 Takes
- 你需要对多次录制进行对比和审查（Review），选择最佳 Take → 用 Takes
- 你需要批量录制多个 Actor 的属性变化，并自动保存为 Level Sequence → 用 Takes
- 你在做实时预览录制（Previs），需要快速迭代多次录制 → 用 Takes

## 蓝图用法

### 核心节点（通过 Subsystem 访问）

Take Recorder 的主要蓝图 API 通过 `UTakeRecorderSubsystem` 引擎子系统访问。你需要先调用 `SetTargetSequence` 初始化，然后才能使用其他功能。

#### 录制控制

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Start Recording` | 开始录制，可选是否打开 Sequencer 和显示错误信息 | `UTakeRecorderSubsystem` |
| `Stop Recording` | 停止当前录制 | `UTakeRecorderSubsystem` |
| `Cancel Recording` | 取消进行中的录制（不保存数据） | `UTakeRecorderSubsystem` |
| `Is Recording` | 查询是否正在录制 | `UTakeRecorderSubsystem` |
| `Is Reviewing` | 查询是否正在回放审查 | `UTakeRecorderSubsystem` |
| `Can Review Last Recording` | 查询是否可以回放上一次录制 | `UTakeRecorderSubsystem` |
| `Review Last Recording` | 回放上一次录制的内容 | `UTakeRecorderSubsystem` |
| `Get State` | 获取当前录制状态（PreInitialization/CountingDown/Started/Stopped/Cancelled 等） | `UTakeRecorderSubsystem` |

#### 源（Source）管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Add Source` | 按类型添加录制源 | `UTakeRecorderSubsystem` |
| `Remove Source` | 移除指定录制源 | `UTakeRecorderSubsystem` |
| `Clear Sources` | 清除所有录制源 | `UTakeRecorderSubsystem` |
| `Get Sources` | 获取源管理器对象 | `UTakeRecorderSubsystem` |
| `Get All Sources (Copy)` | 获取所有源的副本（蓝图专用，不要修改） | `UTakeRecorderSubsystem` |
| `Get Source By Class` | 按类型查找第一个匹配的源 | `UTakeRecorderSubsystem` |
| `Add Source For Actor` | 为指定 Actor 添加录制源 | `UTakeRecorderSubsystem` |
| `Remove Actor From Sources` | 从源中移除指定 Actor | `UTakeRecorderSubsystem` |
| `Get Source Actor` | 获取源对应的 Actor | `UTakeRecorderSubsystem` |

#### Slate 和 Take 管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Slate Name` | 设置 Slate 名称（场记板名） | `UTakeRecorderSubsystem` |
| `Set Take Number` | 直接设置 Take 编号 | `UTakeRecorderSubsystem` |
| `Get Next Take Number` | 计算指定 Slate 的下一个 Take 编号 | `UTakeRecorderSubsystem` |
| `Get Number Of Takes` | 获取指定 Slate 的最大 Take 数和总数 | `UTakeRecorderSubsystem` |
| `Increment Take Number` | 自动递增 Take 编号 | `UTakeRecorderSubsystem` |
| `Get Slates` | 获取所有已有的 Slate 列表 | `UTakeRecorderSubsystem` |

#### 序列和帧率

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Target Sequence` | **必须首先调用**，设置目标序列并初始化子系统 | `UTakeRecorderSubsystem` |
| `Get Level Sequence` | 获取当前关联的 Level Sequence | `UTakeRecorderSubsystem` |
| `Get Last Recorded Level Sequence` | 获取最后一次录制生成的 Level Sequence | `UTakeRecorderSubsystem` |
| `Get Frame Rate` | 获取当前帧率 | `UTakeRecorderSubsystem` |
| `Set Frame Rate` | 设置录制帧率 | `UTakeRecorderSubsystem` |
| `Set Frame Rate From Timecode` | 从 Timecode 源设置帧率 | `UTakeRecorderSubsystem` |
| `Mark Frame` | 在当前帧添加标记 | `UTakeRecorderSubsystem` |

#### 设置和元数据

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Global Record Settings` | 获取全局录制参数 | `UTakeRecorderSubsystem` |
| `Set Global Record Settings` | 设置全局录制参数 | `UTakeRecorderSubsystem` |
| `Get Take Meta Data` | 获取 Take 元数据对象 | `UTakeRecorderSubsystem` |
| `Get Take Recorder Mode` | 获取录制模式（新建序列 / 录入已有序列） | `UTakeRecorderSubsystem` |
| `Get Source Record Settings` | 获取指定源的额外录制设置 | `UTakeRecorderSubsystem` |
| `Set Sequence Countdown` | 设置录制前的倒计时秒数 | `UTakeRecorderSubsystem` |
| `Try Get Sequence Countdown` | 获取当前倒计时剩余时间 | `UTakeRecorderSubsystem` |
| `Get Pending Take` | 获取待处理的 Take 预设 | `UTakeRecorderSubsystem` |
| `Reset To Pending Take` | 重置到待处理的 Take | `UTakeRecorderSubsystem` |
| `Clear Pending Take` | 清除待处理的 Take | `UTakeRecorderSubsystem` |

### 事件委托（Delegate）

`UTakeRecorderSubsystem` 暴露了丰富的蓝图可绑定事件：

| 委托 | 触发时机 |
|---|---|
| `TakeRecorderPreInitialize` | 录制按钮按下后、倒计时开始前 |
| `TakeRecorderInitialized` | 录制初始化完成 |
| `TakeRecorderStarted` | 录制正式开始 |
| `TakeRecorderStopped` | 录制停止 |
| `TakeRecorderFinished` | 录制完成（数据已保存） |
| `TakeRecorderCancelled` | 录制取消 |
| `TakeRecorderMarkedFrameAdded` | 添加了标记帧 |
| `TakeRecorderSlateChanged` | Slate 名称改变 |
| `TakeRecorderTakeNumberChanged` | Take 编号改变 |
| `TakeRecorderSourceAdded` | 添加了录制源 |
| `TakeRecorderSourceRemoved` | 移除了录制源 |
| `TakeRecorderSourceModified` | 录制源被修改 |
| `PendingTakeCleared` | 待处理的 Take 被清除 |

### 蓝图函数库快捷节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Is Take Recorder Enabled` | 检查 Take Recorder 是否在构建中启用 | `UTakeRecorderBlueprintLibrary` |
| `Start Recording` (Library) | 直接开始录制（指定序列、源、元数据、参数） | `UTakeRecorderBlueprintLibrary` |
| `Is Recording` (Library) | 检查是否有录制正在进行 | `UTakeRecorderBlueprintLibrary` |
| `Get Active Recorder` | 获取当前活跃的录制器实例 | `UTakeRecorderBlueprintLibrary` |
| `Open Take Recorder Panel` | 打开 Take Recorder 面板 | `UTakeRecorderBlueprintLibrary` |
| `Get Take Recorder Panel` | 获取已打开的面板对象 | `UTakeRecorderBlueprintLibrary` |
| `Get Default Parameters` | 获取默认录制参数 | `UTakeRecorderBlueprintLibrary` |

### 面板控制（UTakeRecorderPanel）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Mode` | 获取面板模式（NewRecording/RecordingInto/EditingPreset/ReviewingRecording） | `UTakeRecorderPanel` |
| `Setup For Recording (Take Preset)` | 使用预设配置面板以准备录制 | `UTakeRecorderPanel` |
| `Setup For Recording (Level Sequence)` | 使用 Level Sequence 配置面板以准备录制 | `UTakeRecorderPanel` |
| `Setup For Recording Into (Level Sequence)` | 配置面板以录制到已有序列中 | `UTakeRecorderPanel` |
| `Setup For Editing` | 配置面板为预设编辑模式 | `UTakeRecorderPanel` |
| `Setup For Viewing` | 配置面板为只读查看模式 | `UTakeRecorderPanel` |

### 使用示例（蓝图描述）

**示例 1：基本录制流程**

1. 获取 `TakeRecorderSubsystem`（通过 `Get Game Instance Subsystem` 节点选择 `TakeRecorderSubsystem`）
2. 调用 `Set Target Sequence` 初始化（参数可留空使用默认值）
3. 调用 `Set Slate Name` 设置场记板名称，如 "MyScene"
4. 调用 `Add Source For Actor` 添加要录制的 Actor
5. （可选）设置倒计时：`Set Sequence Countdown` → 3.0
6. 调用 `Start Recording` 开始录制
7. 等待 `TakeRecorderStopped` 或 `TakeRecorderFinished` 事件
8. 调用 `Get Last Recorded Level Sequence` 获取录制结果

**示例 2：批量录制多个 Actor**

1. 获取 `TakeRecorderSubsystem`
2. 调用 `Set Target Sequence` 初始化
3. 使用 `For Each Loop` 遍历 Actor 数组，对每个 Actor 调用 `Add Source For Actor`
4. 调用 `Start Recording`
5. 绑定 `TakeRecorderFinished` 事件，在回调中获取结果并设置下一次录制的 Slate/Take

**示例 3：录制到已有序列**

1. 获取 `TakeRecorderSubsystem`
2. 调用 `Set Target Sequence`，在参数中设置 `RecordIntoSequence` 为已有的 Level Sequence
3. 调用 `Start Recording`

## C++ 用法

### 头文件引入

```cpp
// 核心录制 API
#include "Recorder/TakeRecorderSubsystem.h"

// 录制器实例
#include "Recorder/TakeRecorder.h"

// 参数结构体
#include "Recorder/TakeRecorderParameters.h"

// 蓝图函数库
#include "Recorder/TakeRecorderBlueprintLibrary.h"

// 面板对象
#include "Recorder/TakeRecorderPanel.h"

// 设置
#include "TakeRecorderSettings.h"
```

### 基本用法

通过 Subsystem 启动录制（推荐方式）：

```cpp
// 来源: Public/Recorder/TakeRecorderSubsystem.h
#include "Recorder/TakeRecorderSubsystem.h"

void AMyActor::StartMyRecording()
{
    UTakeRecorderSubsystem* Subsystem = GEngine->GetEngineSubsystem<UTakeRecorderSubsystem>();
    if (!Subsystem)
    {
        return;
    }

    // 必须先调用 SetTargetSequence 初始化子系统
    FTakeRecorderSequenceParameters SequenceParams;
    // 可以留空使用默认配置，或指定基础预设/序列
    Subsystem->SetTargetSequence(SequenceParams);

    // 设置 Slate 和 Take
    Subsystem->SetSlateName(TEXT("TestScene"));
    Subsystem->SetTakeNumber(1);

    // 添加要录制的 Actor
    if (AActor* MyActor = GetWorld()->GetFirstPlayerController()->GetPawn())
    {
        Subsystem->AddSourceForActor(MyActor, true, true);
    }

    // 绑定完成回调
    Subsystem->TakeRecorderFinished.AddDynamic(this, &AMyActor::OnRecordingFinished);

    // 开始录制
    Subsystem->StartRecording(true, true);
}

void AMyActor::OnRecordingFinished()
{
    UTakeRecorderSubsystem* Subsystem = GEngine->GetEngineSubsystem<UTakeRecorderSubsystem>();
    ULevelSequence* RecordedSequence = Subsystem->GetLastRecordedLevelSequence();
    if (RecordedSequence)
    {
        UE_LOG(LogTemp, Log, TEXT("录制完成: %s"), *RecordedSequence->GetName());
    }
}
```

### 直接使用 UTakeRecorder API

```cpp
// 来源: Public/Recorder/TakeRecorder.h, Public/Recorder/TakeRecorderBlueprintLibrary.h
#include "Recorder/TakeRecorder.h"
#include "Recorder/TakeRecorderBlueprintLibrary.h"

void AMyActor::StartDirectRecording()
{
    // 检查是否已有录制在进行
    if (UTakeRecorderBlueprintLibrary::IsRecording())
    {
        UE_LOG(LogTemp, Warning, TEXT("已有录制正在进行"));
        return;
    }

    // 创建录制所需的对象
    ULevelSequence* BaseSequence = LoadObject<ULevelSequence>(nullptr, TEXT("/Game/MyBaseSequence"));
    UTakeRecorderSources* Sources = NewObject<UTakeRecorderSources>();
    UTakeMetaData* MetaData = NewObject<UTakeMetaData>();

    // 配置录制参数
    FTakeRecorderParameters Parameters = UTakeRecorderBlueprintLibrary::GetDefaultParameters();
    Parameters.User.CountdownSeconds = 3.0f;
    Parameters.User.bSaveRecordedAssets = true;
    Parameters.Project.bRecordToPossessable = true;

    // 通过蓝图函数库启动录制
    UTakeRecorder* Recorder = UTakeRecorderBlueprintLibrary::StartRecording(
        BaseSequence, Sources, MetaData, Parameters
    );

    if (Recorder)
    {
        // 绑定录制事件
        Recorder->OnRecordingStopped().AddUObject(this, &AMyActor::OnRecorderStopped);

        // 可以访问倒计时
        float Countdown = Recorder->GetCountdownSeconds();
        UE_LOG(LogTemp, Log, TEXT("倒计时: %.1f 秒"), Countdown);
    }
}
```

### 使用录制参数

```cpp
// 来源: Public/Recorder/TakeRecorderParameters.h
#include "Recorder/TakeRecorderParameters.h"

FTakeRecorderParameters BuildRecordingParameters()
{
    FTakeRecorderParameters Params;

    // 用户设置
    Params.User.bMaximizeViewport = true;        // 录制时最大化视口
    Params.User.CountdownSeconds = 3.0f;          // 3秒倒计时
    Params.User.EngineTimeDilation = 1.0f;         // 正常时间流速
    Params.User.bResetPlayhead = true;             // 开始时重置播放头
    Params.User.bStopAtPlaybackEnd = false;        // 不在播放范围结束时自动停止
    Params.User.bRemoveRedundantTracks = true;     // 移除冗余轨道
    Params.User.ReduceKeysTolerance = 0.01f;        // 关键帧简化容差
    Params.User.bSaveRecordedAssets = true;         // 保存录制资产
    Params.User.bAutoLock = true;                  // 录制完成后锁定序列
    Params.User.bAutoSerialize = true;             // 增量序列化

    // 项目设置
    Params.Project.RootTakeSaveDir.Path = TEXT("/Game/Takes");
    Params.Project.TakeSaveDir = TEXT("{slate}/{year}{month}{day}");
    Params.Project.DefaultSlate = TEXT("Default");
    Params.Project.bStartAtCurrentTimecode = true;
    Params.Project.bRecordTimecode = true;
    Params.Project.bRecordSourcesIntoSubSequences = true;
    Params.Project.bRecordToPossessable = true;
    Params.Project.bShowNotifications = true;

    // 卡顿保护
    Params.HitchProtection.bEnableHitchProtection = true;
    Params.HitchProtection.MaxCatchupSeconds = 8.0;

    // 录制模式
    Params.TakeRecorderMode = ETakeRecorderMode::RecordNewSequence;
    Params.StartFrame = 0;
    Params.bOpenSequencer = true;

    return Params;
}
```

### 进阶用法

**录制到已有序列（Record Into）**：

```cpp
// 来源: Public/Recorder/TakeRecorderSubsystem.h + ITakeRecorderSubsystemInterface.h
#include "Recorder/TakeRecorderSubsystem.h"

void AMyActor::RecordIntoExistingSequence()
{
    UTakeRecorderSubsystem* Subsystem = GEngine->GetEngineSubsystem<UTakeRecorderSubsystem>();

    ULevelSequence* ExistingSequence = LoadObject<ULevelSequence>(
        nullptr, TEXT("/Game/Sequences/MyExistingSequence")
    );

    // 方法1: 通过 SetRecordIntoLevelSequence
    Subsystem->SetTargetSequence(FTakeRecorderSequenceParameters());
    Subsystem->SetRecordIntoLevelSequence(ExistingSequence);

    // 方法2: 通过 SequenceParameters
    FTakeRecorderSequenceParameters Params;
    Params.RecordIntoSequence = ExistingSequence;
    Subsystem->SetTargetSequence(Params);

    Subsystem->StartRecording(true, true);
}
```

**监听录制生命周期事件**：

```cpp
// 来源: Public/Recorder/TakeRecorderSubsystem.h
void AMyActor::BindToRecordingEvents()
{
    UTakeRecorderSubsystem* Subsystem = GEngine->GetEngineSubsystem<UTakeRecorderSubsystem>();

    // 原生多播委托（用于 C++ 监听，顺序可靠）
    Subsystem->GetOnRecordingPreInitializedEvent().AddUObject(
        this, &AMyActor::OnPreInitialize
    );
    Subsystem->GetOnRecordingInitializedEvent().AddUObject(
        this, &AMyActor::OnInitialized
    );
    Subsystem->GetOnRecordingStartedEvent().AddUObject(
        this, &AMyActor::OnStarted
    );
    Subsystem->GetOnRecordingStoppedEvent().AddUObject(
        this, &AMyActor::OnStopped
    );
    Subsystem->GetOnRecordingFinishedEvent().AddUObject(
        this, &AMyActor::OnFinished
    );
    Subsystem->GetOnRecordingCancelledEvent().AddUObject(
        this, &AMyActor::OnCancelled
    );
    Subsystem->GetOnRecordingSourceAddedEvent().AddUObject(
        this, &AMyActor::OnSourceAdded
    );
    Subsystem->GetOnRecordingSourceRemovedEvent().AddUObject(
        this, &AMyActor::OnSourceRemoved
    );
    Subsystem->GetOnRecordingSourceModifiedEvent().AddUObject(
        this, &AMyActor::OnSourceModified
    );
}
```

**使用录制参数覆盖机制**：

```cpp
// 来源: Public/Recorder/TakeRecorder.h - FTakeRecorderParameterOverride
#include "Recorder/TakeRecorder.h"

void AMyActor::RegisterParameterOverride()
{
    // TakeInitializeParameterOverride 允许在录制初始化时动态修改参数
    FTakeRecorderParameterOverride& Override = UTakeRecorder::TakeInitializeParameterOverride();

    Override.RegisterHandler(
        FName("MyCustomOverride"),
        FTakeRecorderParameterDelegate::CreateLambda(
            [](const FTakeRecorderParameters& InParams) -> FTakeRecorderParameters
            {
                FTakeRecorderParameters Modified = InParams;
                Modified.User.bSaveRecordedAssets = false; // 不自动保存
                return Modified;
            }
        )
    );
}
```

**模块扩展注册（自定义 Source 菜单）**：

```cpp
// 来源: Public/ITakeRecorderModule.h
#include "ITakeRecorderModule.h"

void FMyModule::RegisterTakeRecorderExtensions()
{
    if (ITakeRecorderModule::IsAvailable())
    {
        ITakeRecorderModule& TakeModule = ITakeRecorderModule::Get();

        // 注册 Source 菜单扩展
        FOnExtendSourcesMenu MenuExtension;
        MenuExtension.BindLambda([](TSharedRef<FExtender> Extender, UTakeRecorderSources* Sources)
        {
            // 添加自定义菜单项
        });
        TakeModule.RegisterSourcesMenuExtension(MenuExtension);

        // 注册工具栏扩展
        TakeModule.GetToolbarExtensionGenerators().AddLambda(
            [](TArray<TSharedRef<SWidget>>& OutExtensions)
            {
                // 添加自定义工具栏按钮
            }
        );

        // 注册录制错误检查
        TakeModule.GetRecordErrorCheckGenerator().AddLambda(
            [](FText& OutError)
            {
                // 检查录制条件是否满足
                // 如果不满足，设置 OutError 为错误描述
                // 如果满足，确保 OutError 为空
            }
        );
    }
}
```

## Demo 示例

### 最小录制示例（.h）

```cpp
// MyRecordingActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyRecordingActor.generated.h"

class UTakeRecorderSubsystem;
class ULevelSequence;

UCLASS()
class MYPROJECT_API AMyRecordingActor : public AActor
{
    GENERATED_BODY()

public:
    AMyRecordingActor();

    /** 开始录制指定 Actor */
    UFUNCTION(BlueprintCallable, Category = "Demo")
    void StartRecordingActor(AActor* TargetActor, const FString& SlateName);

    /** 停止当前录制 */
    UFUNCTION(BlueprintCallable, Category = "Demo")
    void StopCurrentRecording();

    /** 获取最后一次录制的序列 */
    UFUNCTION(BlueprintCallable, Category = "Demo")
    ULevelSequence* GetLastRecordedSequence() const;

protected:
    virtual void BeginPlay() override;

private:
    UFUNCTION()
    void OnRecordingFinished();

    TWeakObjectPtr<UTakeRecorderSubsystem> SubsystemWeak;
    int32 CurrentTakeNumber = 1;
};
```

### 最小录制示例（.cpp）

```cpp
// MyRecordingActor.cpp
#include "MyRecordingActor.h"
#include "Recorder/TakeRecorderSubsystem.h"
#include "LevelSequence.h"

AMyRecordingActor::AMyRecordingActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyRecordingActor::BeginPlay()
{
    Super::BeginPlay();

    // 获取 Take Recorder 子系统
    UTakeRecorderSubsystem* Subsystem = GEngine->GetEngineSubsystem<UTakeRecorderSubsystem>();
    if (ensure(Subsystem))
    {
        SubsystemWeak = Subsystem;

        // 初始化子系统（必须在使用前调用）
        FTakeRecorderSequenceParameters SequenceParams;
        Subsystem->SetTargetSequence(SequenceParams);

        // 绑定完成回调
        Subsystem->TakeRecorderFinished.AddDynamic(this, &AMyRecordingActor::OnRecordingFinished);

        UE_LOG(LogTemp, Log, TEXT("Take Recorder 子系统已初始化"));
    }
}

void AMyRecordingActor::StartRecordingActor(AActor* TargetActor, const FString& SlateName)
{
    UTakeRecorderSubsystem* Subsystem = SubsystemWeak.Get();
    if (!Subsystem || !TargetActor)
    {
        UE_LOG(LogTemp, Error, TEXT("无法开始录制：子系统或目标 Actor 无效"));
        return;
    }

    if (Subsystem->IsRecording())
    {
        UE_LOG(LogTemp, Warning, TEXT("已有录制正在进行，请先停止"));
        return;
    }

    // 配置 Slate 和 Take
    Subsystem->SetSlateName(SlateName);
    Subsystem->SetTakeNumber(CurrentTakeNumber);

    // 清除旧的源并添加新的
    Subsystem->ClearSources();
    Subsystem->AddSourceForActor(TargetActor, true, true);

    // 设置倒计时
    Subsystem->SetSequenceCountdown(3.0f);

    // 开始录制
    bool bStarted = Subsystem->StartRecording(true, true);
    if (bStarted)
    {
        UE_LOG(LogTemp, Log, TEXT("开始录制 Slate=%s Take=%d"),
            *SlateName, CurrentTakeNumber);
    }
}

void AMyRecordingActor::StopCurrentRecording()
{
    UTakeRecorderSubsystem* Subsystem = SubsystemWeak.Get();
    if (Subsystem && Subsystem->IsRecording())
    {
        Subsystem->StopRecording();
    }
}

ULevelSequence* AMyRecordingActor::GetLastRecordedSequence() const
{
    UTakeRecorderSubsystem* Subsystem = SubsystemWeak.Get();
    return Subsystem ? Subsystem->GetLastRecordedLevelSequence() : nullptr;
}

void AMyRecordingActor::OnRecordingFinished()
{
    CurrentTakeNumber++;

    ULevelSequence* Recorded = GetLastRecordedSequence();
    if (Recorded)
    {
        UE_LOG(LogTemp, Log, TEXT("录制完成！资产: %s，下一条: %d"),
            *Recorded->GetName(), CurrentTakeNumber);
    }
}
```

## 模块依赖

从源码中使用的类型和头文件推断，以下是该插件独特的模块依赖（不列出标准 Core/Engine/Slate 等）：

| 模块 | 用途 |
|---|---|
| `LevelSequence` | Level Sequence 资产和操作（录制目标格式） |
| `MovieScene` | Movie Scene 底层框架（轨道、Section、时间码） |
| `SequencerCore` | Sequencer 核心功能（ISequencer 接口） |
| `TimeManagement` | 时间码提供器、自定义时间步长（卡顿保护） |
| `NamingTokens` | 命名令牌系统（动态文件路径命名） |
| `SerializedRecorderInterface` | 序列化录制器接口（增量录制） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `ee6722f8` | Take Recorder: Correcting regression where the Attach Track Recorder does not correctly record attac | 修复附件轨道录制器无法正确录制附件关系的回归问题 |
| 2026-05-14 | `d17111f0` | Take Recorder: Protecting against crashing on a null sub section sequence. | 修复子 Section 序列为空时导致崩溃的问题 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 到 float 截断的编译警告 |
| 2026-05-13 | `0c5ab24a` | Take Recorder: Adding missing WITH_EDITOR guard on log. | 补充缺失的 WITH_EDITOR 宏保护，防止非编辑器构建中日志编译错误 |
| 2026-05-13 | `6aee158b` | Take Recorder: Fixing possible crash where a weak pointer could trigger an assertion due to a CastCh | 修复弱指针在类型转换时可能触发断言导致的崩溃 |

### 维护评价

**综合评价：活跃维护，推荐使用**

- **创建时间**：2019 年 1 月，已持续维护约 7 年，是虚拟制片核心工具之一
- **近期活跃度**：非常活跃，最近的更新集中在 2026 年 5 月，且持续有实质性 bug 修复和稳定性改进
- **维护质量**：从 commit 历史看，Epic 团队在积极修复回归问题、崩溃和编译兼容性问题，说明该插件在持续被使用和测试
- **架构成熟度**：采用 Subsystem + 接口分离 + 模块化 Source 的架构，扩展性好；从 5.4 起部分旧 API 已标记为 Deprecated，表明 API 在有计划地演进
- **注意事项**：
  - 这是一个大型插件（9 个模块、219 个源文件），学习曲线较陡
  - `UTakeRecorderBlueprintLibrary` 中部分委托设置函数已在 5.4 标记废弃，应迁移到 `UTakeRecorderSubsystem` 的事件委托
  - 虚拟制片功能通常需要配合 nDisplay、Media Framework 等插件使用
- **推荐程度**：如果项目涉及虚拟制片、动作捕捉或需要运行时录制 Sequencer 数据，这是**官方唯一推荐的解决方案**，直接使用即可

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Takes)
- [官方文档](https://docs.unrealengine.com/en-US/AnimatingObjects/Sequencer/TakeRecorder/)（Take Recorder 官方文档）