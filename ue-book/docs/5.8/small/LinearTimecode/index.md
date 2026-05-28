# Linear Timecode

> Component to read a linear timecode from a media source. Does not use synchronization mechanism.

| 属性 | 值 |
|---|---|
| 中文名 | 线性时间码读取器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `LinearTimecode` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2017-12-11 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/LinearTimecode) | |

## 用途

该插件主要用于从**媒体播放器（MediaPlayer）** 的音频轨道中解码**线性时间码（LTC，Linear Timecode）**。线性时间码是影视行业中用于同步视频设备的标准时间码格式，通常以音频信号的形式嵌入在视频或音频流中。此插件通过处理媒体播放器的音频样本，提取并解码出对应的 LTC 时间码信息，并将其转换为 UE 可用的 `FDropTimecode` 结构。

**为什么存在？** 在虚拟制片、多机位拍摄、后期制作等场景中，常常需要将 Unreal Engine 场景中的时间与外部设备（如摄像机、录音机）的时间码进行同步。该插件提供了读取这些外部时间码的基础能力，使得引擎能够感知外部世界的时间信息。

## 使用场景

- **虚拟制片（Virtual Production）**：在 LED 墙拍摄时，需要将摄像机拍摄画面的 LTC 时间码与 UE 中 Sequencer 的时间轴同步，确保虚拟场景和实拍画面在后期制作中能够精确对齐。
- **多机位录制与回放**：使用 `Sequence Recorder` 录制多个带有 LTC 时间码的摄像机画面后，利用此插件在回放时精确同步各个视角。
- **广播电视与现场制作**：在现场导播或广播系统中，将外部播出设备的时间码输入到 UE，用于触发或同步引擎内的事件。

## 蓝图用法

该插件提供了一个主要的组件 `ULinearTimecodeComponent`，以及几个相关的工具函数和委托。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetDropFrameNumber` | 从组件当前解码的时间码中获取帧号 | `ULinearTimecodeComponent` |
| `GetDropTimeCodeFrameNumber` | **静态函数**。将 `FDropTimecode` 结构转换为总帧数 | `ULinearTimecodeComponent` |
| `SetDropTimecodeFrameNumber` | **静态函数**。根据总帧数设置 `FDropTimecode` 结构 | `ULinearTimecodeComponent` |
| `Conv_DropTimecodeToString` | **转换函数**。将 `FDropTimecode` 自动转换为可读字符串 (`HH:MM:SS:FF`) | `UDropTimecodeToStringConversion` |
| `OnTimecodeChange` | **事件**。当组件成功解码出一个新的 LTC 帧时触发，提供最新的 `FDropTimecode` | `ULinearTimecodeComponent` |

### 使用示例（蓝图描述）

1.  **读取时间码**：
    - 在你的 Actor 中添加 `ULinearTimecodeComponent` 组件。
    - 在组件的细节面板中，将 `MediaPlayer` 属性指向一个正在播放包含 LTC 音频信号的媒体文件的 `MediaPlayer` 资产。
    - 绑定 `OnTimecodeChange` 事件，在事件输出中获取最新的 `DropTimecode`。
    - 或者，在 Tick 中调用 `GetDropFrameNumber` 来持续获取当前帧。

2.  **时间码格式转换**：
    - 使用 `GetDropTimeCodeFrameNumber` 节点，输入一个 `DropTimecode` 变量，输出 `FrameNumber`（整数）。
    - 使用 `SetDropTimecodeFrameNumber` 节点，输入一个 `DropTimecode`（提供帧率和 Drop Frame 信息）和一个 `FrameNumber`，输出修改后的 `DropTimecode`。

## C++ 用法

### 头文件引入

```cpp
#include "LinearTimecodeComponent.h"
#include "DropTimecode.h"
```

### 基本用法

从源码头文件提取的用法，展示如何声明和使用组件。

```cpp
// 在你的 Actor 头文件中
UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Timecode")
ULinearTimecodeComponent* TimecodeReader;

// 在 Actor 的构造函数或 BeginPlay 中创建并初始化
TimecodeReader = CreateDefaultSubobject<ULinearTimecodeComponent>(TEXT("TimecodeReader"));
// 确保在构造函数中创建，以便在编辑器中可见和可配置

// 在 BeginPlay 中，你可能需要设置 MediaPlayer
void AMyActor::BeginPlay()
{
    Super::BeginPlay();
    if (TimecodeReader && MyMediaPlayerAsset)
    {
        TimecodeReader->MediaPlayer = MyMediaPlayerAsset;
        TimecodeReader->UpdatePlayer(); // 通知组件媒体播放器已更改
    }

    // 绑定委托
    TimecodeReader->OnTimecodeChange.AddDynamic(this, &AMyActor::HandleTimecodeChanged);
}

// 处理时间码变化的回调函数
void AMyActor::HandleTimecodeChanged(const FDropTimecode& NewTimecode)
{
    // 在此处理新时间码
    UE_LOG(LogTemp, Log, TEXT("New Timecode: %s"), *NewTimecode.Timecode.ToString());
    // NewTimecode.bNewFrame 为 true 表示这是一帧的开始
}
```

### 进阶用法

使用静态工具函数进行时间码与帧数的相互转换。

```cpp
#include "LinearTimecodeComponent.h"

// 假设我们有一个 FDropTimecode
FDropTimecode CurrentTimecode;
// ... 从组件获取或手动设置 CurrentTimecode ...

// 1. 将时间码转换为总帧数
int32 TotalFrames = 0;
ULinearTimecodeComponent::GetDropTimeCodeFrameNumber(CurrentTimecode, TotalFrames);
UE_LOG(LogTemp, Log, TEXT("Total frames: %d"), TotalFrames);

// 2. 从总帧数创建新的时间码（需要提供一个包含正确帧率和 Drop 标志的基础时间码）
FDropTimecode BaseTimecode;
BaseTimecode.FrameRate = 30; // 假设是 30fps
BaseTimecode.Timecode.bDropFrame = true; // 假设是 Drop Frame 格式

FDropTimecode NewTimecode;
int32 TargetFrame = 100; // 我们想要第 100 帧的时间码
ULinearTimecodeComponent::SetDropTimecodeFrameNumber(BaseTimecode, TargetFrame, NewTimecode);
UE_LOG(LogTemp, Log, TEXT("Timecode at frame 100: %s"), *NewTimecode.Timecode.ToString());
```

## Demo 示例

一个完整的、可编译的 Actor 示例，用于读取并打印 LTC 时间码。

```cpp
// LTCReaderActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "LinearTimecodeComponent.h"
#include "LTCReaderActor.generated.h"

UCLASS()
class ALTCReaderActor : public AActor
{
    GENERATED_BODY()

public:
    ALTCReaderActor();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
    ULinearTimecodeComponent* TimecodeComponent;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Timecode")
    UMediaPlayer* TargetMediaPlayer;

protected:
    virtual void BeginPlay() override;

    UFUNCTION()
    void OnTimecodeChanged(const FDropTimecode& NewTimecode);
};
```

```cpp
// LTCReaderActor.cpp
#include "LTCReaderActor.h"
#include "MediaMediaPlayer.h" // 根据实际包含路径可能需要调整

ALTCReaderActor::ALTCReaderActor()
{
    PrimaryActorTick.bCanEverTick = false;

    TimecodeComponent = CreateDefaultSubobject<ULinearTimecodeComponent>(TEXT("TimecodeComponent"));
    RootComponent = TimecodeComponent;
}

void ALTCReaderActor::BeginPlay()
{
    Super::BeginPlay();

    if (TargetMediaPlayer)
    {
        TimecodeComponent->MediaPlayer = TargetMediaPlayer;
        TimecodeComponent->UpdatePlayer();
    }

    TimecodeComponent->OnTimecodeChange.AddDynamic(this, &ALTCReaderActor::OnTimecodeChanged);
}

void ALTCReaderActor::OnTimecodeChanged(const FDropTimecode& NewTimecode)
{
    if (NewTimecode.bNewFrame)
    {
        FString TimecodeString;
        FDropTimecode TempTimecode = NewTimecode;
        UDropTimecodeToStringConversion::Conv_DropTimecodeToString(TempTimecode);
        UE_LOG(LogTemp, Display, TEXT("LTC Frame: %s | Rate: %d | Running Forward: %s"),
            *NewTimecode.Timecode.ToString(),
            NewTimecode.FrameRate,
            NewTimecode.bRunningForward ? TEXT("Yes") : TEXT("No"));
    }
}
```

## 模块依赖

基于代码分析，你的项目模块需要依赖以下模块才能使用此插件的功能：

| 模块 | 用途 |
|---|---|
| `MediaAssets` | 提供 `UMediaPlayer`、`UMediaSoundComponent` 等核心媒体类 |
| `MediaUtils` | 提供媒体工具类和样本格式定义（如 `IMediaAudioSample`） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2023-02-18 | `e599d19e` | Removing redundant Private includes. | 移除多余的 Private 目录头文件包含，代码清理。 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 大型提交，包含多个插件的更新，此插件无实质性功能改动。 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 更新插件元数据中的供应商链接以使用 HTTPS 协议。 |
| 2022-08-18 | `3f4252aa` | ObjectPtr upgrade for engine plugins... | 自动升级脚本将 `TObjectPtr` 应用于引擎插件。 |
| 2021-01-21 | `bc88b73a` | Merge Release-Engine-Staging to Main @ CL# 15151250 | 从发布分支合并到主线，无特定于此插件的改动。 |

### 维护评价

- **状态**：**维护不活跃**。该插件自2017年创建后，近两年没有功能性更新。最近的提交主要是全局性的代码清理、协议升级和自动化脚本改动，没有针对 LTC 解码或组件功能的增强或修复。
- **稳定性**：代码成熟且稳定，最后一次重大改动停留在2018年初（首次提交记录中）。作为“Legacy”（旧版）插件，它可能已被更新的解决方案（如 TimecodeSynchronizer 插件）部分取代。
- **推荐使用**：**仅推荐用于特定的遗留项目或明确需要简单 LTC 音频解码功能的场景**。对于新项目，特别是涉及复杂媒体同步的项目，建议评估引擎内更新的 `TimecodeSynchronizer` 或 Media Framework 是否提供更强大、维护更积极的功能。由于默认禁用，使用前需在插件管理器中手动启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/LinearTimecode)
- 官方文档：无
- 测试用例：无（未在提供的信息中找到）