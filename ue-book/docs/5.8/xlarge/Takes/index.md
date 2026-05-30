# Take Recorder

> A suite of tools and interfaces designed for recording, reviewing and playing back takes in a virtual production environment.

| 属性 | 值 |
|---|---|
| 中文名 | 镜头录制器 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产，编辑器界面，示例数据） |
| 模块 | `CacheTrackRecorder` (Runtime), `TakeMovieScene` (Runtime), `TakeRecorder` (Runtime), `TakeRecorderEditor` (Runtime), `TakeRecorderNamingTokens` (Runtime), `TakeRecorderSources` (Runtime), `TakeSequencer` (Runtime), `TakeTrackRecorders` (Runtime), `TakesCore` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-01-11 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Takes) | |

## 用途

Takes 插件为 Unreal Engine 提供了专业的镜头（Take）录制与管理解决方案，主要服务于虚拟制作（Virtual Production）工作流。它不仅仅是简单的录制功能，而是一套完整的系统，用于在虚拟场景中同步捕获演员表演、摄像机运动、动画、音频以及场景状态等各类数据，并将它们打包成一个可管理、可审查、可回放的“镜头”单元。其核心价值在于将游戏引擎转变为一个专业的影视制作前端。

## 使用场景

- **影视虚拟制片**：在 LED Volume（如 The Volume）拍摄时，用于同步录制演员的表演数据、摄像机轨迹、灯光设置以及最终的渲染画面。
- **游戏过场动画制作**：为游戏中的复杂过场动画序列录制演员的面部和身体动画，并与预先设计的镜头动画同步。
- **多机位录制与审查**：同时管理多个“机位”（Take Recorder Sources）的录制，并在 Sequencer 中统一回放和对比不同的录制版本（Take）。

## 蓝图用法

蓝图功能主要通过 `UTakeRecorderSubsystem` 和 `UTakesCoreBlueprintLibrary` 暴露。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Take Recorder Subsystem` | 获取全局唯一的 Take Recorder 子系统实例，用于控制录制。 | `UTakeRecorderSubsystem` |
| `Start Recording` | 使用当前配置启动一次新的镜头录制。 | `UTakeRecorderSubsystem` |
| `Stop Recording` | 停止当前正在进行的录制。 | `UTakeRecorderSubsystem` |
| `Get Active Recorder` | 获取当前活动的录制器实例（如果正在录制）。 | `UTakeRecorderSubsystem` |
| `Create New Sequence` | 创建一个用于容纳录制数据的全新 Level Sequence 资产。 | `UTakesCoreBlueprintLibrary` |
| `Get Recorder Timecode` | 获取当前录制过程中的 Timecode。 | `UTakesCoreBlueprintLibrary` |

### 使用示例（蓝图描述）

1.  在蓝图中使用 `Get Take Recorder Subsystem` 获取子系统对象。
2.  将子系统对象的返回引脚连接到 `Start Recording` 节点的执行引脚，即可启动一次录制。
3.  可以先通过 `Create New Sequence` 创建一个新的序列资产，并将其连接到录制节点的输入参数，以指定录制数据的存储位置。
4.  当需要结束时，调用 `Stop Recording` 节点。

## C++ 用法

### 头文件引入

```cpp
#include "TakeRecorderSubsystem.h"
#include "TakesCoreBlueprintLibrary.h"
```

### 基本用法

通过获取全局子系统来控制录制流程。

```cpp
// 获取 Take Recorder 子系统
UTakeRecorderSubsystem* TakeRecorderSubsystem = GEngine->GetEngineSubsystem<UTakeRecorderSubsystem>();
if (TakeRecorderSubsystem)
{
    // 检查是否可以开始录制
    if (TakeRecorderSubsystem->CanStartRecording() == ETakeRecorderResponse::Accepted)
    {
        // 启动一次默认配置的录制
        UTakeRecorder* Recorder = TakeRecorderSubsystem->StartRecording();
        // Recorder 对象可用于进一步的配置或查询状态
    }
}
// 来源: Engine/Plugins/VirtualProduction/Takes/Source/TakeRecorder/Public/TakeRecorderSubsystem.h
```

### 进阶用法

```cpp
// 结合蓝图库函数创建新序列并指定录制
UTakeRecorderSubsystem* Subsystem = GEngine->GetEngineSubsystem<UTakeRecorderSubsystem>();

// 创建一个新的 Level Sequence 资产
ULevelSequence* NewSequence = UTakesCoreBlueprintLibrary::CreateNewSequence(TEXT("MyNewTake"));

// 配置录制设置
FTakeRecorderParameters Parameters;
Parameters.LevelSequence = NewSequence;

// 使用自定义参数启动录制
UTakeRecorder* CustomRecorder = Subsystem->StartRecording(Parameters);

// 在 Tick 或定时器中检查录制状态
if (CustomRecorder && CustomRecorder->GetStatus() == ETakeRecorderStatus::Stopped)
{
    // 录制已结束，处理结果
}
```

## Demo 示例

```cpp
// MyTakeRecorderActor.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyTakeRecorderActor.generated.h"

class UTakeRecorderSubsystem;
class UTakeRecorder;

UCLASS()
class MYPROJECT_API AMyTakeRecorderActor : public AActor
{
    GENERATED_BODY()
    
public:
    AMyTakeRecorderActor();

protected:
    virtual void BeginPlay() override;

public:
    virtual void Tick(float DeltaTime) override;

    // 蓝图可调用的函数，开始录制
    UFUNCTION(BlueprintCallable, Category = "Take Recorder")
    void StartMyRecording();

    // 蓝图可调用的函数，停止录制
    UFUNCTION(BlueprintCallable, Category = "Take Recorder")
    void StopMyRecording();

    // 蓝图可调用的函数，检查是否在录制
    UFUNCTION(BlueprintCallable, Category = "Take Recorder")
    bool IsCurrentlyRecording() const;

private:
    UPROPERTY()
    UTakeRecorderSubsystem* CachedSubsystem;

    UPROPERTY()
    TWeakObjectPtr<UTakeRecorder> CurrentRecorder;
};

// MyTakeRecorderActor.cpp
#include "MyTakeRecorderActor.h"
#include "TakeRecorderSubsystem.h"

AMyTakeRecorderActor::AMyTakeRecorderActor()
{
    PrimaryActorTick.bCanEverTick = true;
    CachedSubsystem = nullptr;
}

void AMyTakeRecorderActor::BeginPlay()
{
    Super::BeginPlay();
    CachedSubsystem = GEngine->GetEngineSubsystem<UTakeRecorderSubsystem>();
}

void AMyTakeRecorderActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    // 可以在这里监控录制进度或状态
    if (IsCurrentlyRecording())
    {
        UE_LOG(LogTemp, Log, TEXT("Recording in progress..."));
    }
}

void AMyTakeRecorderActor::StartMyRecording()
{
    if (CachedSubsystem && CachedSubsystem->CanStartRecording() == ETakeRecorderResponse::Accepted)
    {
        CurrentRecorder = CachedSubsystem->StartRecording();
        if (CurrentRecorder.IsValid())
        {
            UE_LOG(LogTemp, Warning, TEXT("Recording started."));
        }
    }
}

void AMyTakeRecorderActor::StopMyRecording()
{
    if (CachedSubsystem)
    {
        CachedSubsystem->StopRecording();
        CurrentRecorder.Reset();
        UE_LOG(LogTemp, Warning, TEXT("Recording stopped."));
    }
}

bool AMyTakeRecorderActor::IsCurrentlyRecording() const
{
    if (CurrentRecorder.IsValid())
    {
        return CurrentRecorder->GetStatus() == ETakeRecorderStatus::Recording;
    }
    return false;
}
```

## 模块依赖

此插件功能自包含，其模块依赖关系主要在内部。对于想要扩展录制功能（例如自定义录制源或轨道）的开发者，可能需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `TakeRecorderSources` | 如果要开发自定义的录制源（如新的数据捕获类型）。 |
| `TakeTrackRecorders` | 如果要开发自定义的轨道录制器（用于处理特定类型 Sequencer 轨道的录制）。 |
| `TakesCore` | 提供镜头（Take）管理、命名令牌等核心功能和数据结构。 |
| `SequencerCore` | 底层序列器核心，与数据结构和交互相关。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `ee6722f8` | Take Recorder: Correcting regression where the Attach Track Recorder does not correctly record attach. | 修复附着轨道录制器无法正确记录附着关系的回归问题。 |
| 2026-05-14 | `d17111f0` | Take Recorder: Protecting against crashing on a null sub section sequence. | 增加对空子序列段的防护，防止崩溃。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点数导致的编译器警告。 |
| 2026-05-13 | `0c5ab24a` | Take Recorder: Adding missing WITH_EDITOR guard on log. | 为日志输出添加缺失的编辑器环境宏保护。 |
| 2026-05-13 | `6aee158b` | Take Recorder: Fixing possible crash where a weak pointer could trigger an assertion due to a CastCh. | 修复一个可能导致弱指针因类型转换而触发断言并崩溃的问题。 |

### 维护评价

Takes 插件是 Epic Games 虚拟制作工具链的核心组件之一。从 Git 历史看，该插件**维护非常活跃**，最近的提交（截至 2026 年 5 月）集中于修复回归问题和提升稳定性，表明其仍在积极开发和优化中。虽然自 2019 年创建已约 7 年，但其持续的更新证明它在当前的生产流程中仍扮演着关键角色。该插件功能成熟，是虚拟制片和高质量过场动画制作的推荐工具。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Takes)
- [官方文档]() （暂无）
- [测试用例]() （插件目录内未发现标准测试文件，可能位于 Engine/Tests 或其它内部路径）