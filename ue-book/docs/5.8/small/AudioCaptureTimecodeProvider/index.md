# Audio Capture Timecode Provider

> Decodes an LTC signal (linear timcode) from a live audio capture device (ie. the computer audio jack).（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 音频捕获时间码 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AudioCaptureTimecodeProvider` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-05-14 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AudioCaptureTimecodeProvider) | |

## 用途

此插件的核心功能是通过计算机音频接口（如麦克风或线路输入）捕获**线性时间码（LTC）** 信号，并将其解码为引擎可识别的时间码（`FTimecode`）和帧率（`FFrameRate`）信息。

LTC 是专业视频和音频制作中用于同步设备的行业标准时间码格式。该插件解决了**将外部专业设备（如摄像机、录音机、调音台）的时间码同步到虚幻引擎**的问题，这对于多机位拍摄、虚拟制作或任何需要精确帧同步的实时或后期工作流程至关重要。

## 使用场景

- 你正在使用多台摄像机拍摄虚拟制片的镜头，并希望所有摄像机与虚幻引擎的 Sequencer 时间轴精确同步。
- 你在进行现场直播，需要将来自调音台或导播台的 LTC 时间码实时注入引擎，以同步图形、音频和视频输出。
- 你在后期制作中，需要确保引擎渲染的序列与外部录音或视频文件的时间码对齐。

## 蓝图用法

该插件提供了一个可蓝图化的 `UAudioCaptureTimecodeProvider` 类，用于配置和控制音频捕获时间码。

### 核心节点

由于时间码提供者主要作为配置对象使用，其核心交互发生在编辑器属性面板中。以下是关键的可编辑属性：

| 属性 | 说明 | 所在类 |
|---|---|---|
| `bDetectFrameRate` | 是否从音频信号中自动检测帧率。可能需要一些时间才能正确识别。 | `UAudioCaptureTimecodeProvider` |
| `bAssumeDropFrameFormat` | 当自动检测帧率时，假设信号是丢帧（Drop Frame）格式。 | `UAudioCaptureTimecodeProvider` |
| `FrameRate` | 当不使用自动检测时，手动设置预期的音频源帧率。 | `UAudioCaptureTimecodeProvider` |
| `AudioChannel` | 用于捕获的音频通道索引（从1开始）。 | `UAudioCaptureTimecodeProvider` |

### 使用示例（蓝图描述）

1.  **在项目设置中启用**：在 `Plugins` 窗口中找到并启用 “Audio Capture Timecode Provider” 和 “Linear Timecode” 插件。
2.  **配置时间码源**：
    *   在 `World Settings` 或 `Project Settings` 的 `Timecode` 部分。
    *   在 `Timecode Provider` 下拉菜单中，选择 `Audio Capture Timecode Provider`。
    *   选中后，下方会出现该提供者的详细设置面板。
    *   根据你的音频源配置 `AudioChannel`、帧率检测选项（`bDetectFrameRate`, `bAssumeDropFrameFormat`）或手动帧率（`FrameRate`）。
3.  **运行时监控**：在运行时，可以通过 `Get Synchronization State` 节点（来自 `UTimecodeProvider` 基类）检查该提供者是否已成功同步（`Synchronized` 状态表示成功解码了 LTC 信号）。

## C++ 用法

### 头文件引入

```cpp
#include "AudioCaptureTimecodeProvider.h"
```

### 基本用法

```cpp
// 来源：AudioCaptureTimecodeProvider.h 及其使用模式
#include "AudioCaptureTimecodeProvider.h"
#include "Engine/Engine.h"

// 创建一个音频捕获时间码提供者的实例
UAudioCaptureTimecodeProvider* AudioTimecodeProvider = NewObject<UAudioCaptureTimecodeProvider>();

// 配置提供者（通常在编辑器属性中完成，也可在代码中设置）
AudioTimecodeProvider->bDetectFrameRate = false; // 不自动检测，手动设置
AudioTimecodeProvider->FrameRate = FFrameRate(30, 1); // 30fps 非丢帧
AudioTimecodeProvider->AudioChannel = 1; // 使用第一个音频通道

// 初始化提供者（通常由引擎在启用时调用）
// bool bInitialized = AudioTimecodeProvider->Initialize(GEngine);

// 在游戏循环或需要时获取时间码
FQualifiedFrameTime CurrentFrameTime;
if (AudioTimecodeProvider->FetchTimecode(CurrentFrameTime))
{
    UE_LOG(LogTemp, Log, TEXT("当前时间码: %s"), *CurrentFrameTime.AsString());
    // 使用 CurrentFrameTime.Timecode 和 CurrentFrameTime.Rate
}
```

### 进阶用法

```cpp
// 来源：AudioCaptureTimecodeProvider.h
#include "AudioCaptureTimecodeProvider.h"
#include "Engine/Engine.h"

// 监控同步状态变化（可能需要轮询或结合事件）
UAudioCaptureTimecodeProvider* Provider = ...; // 获取实例指针
ETimecodeProviderSynchronizationState State = Provider->GetSynchronizationState();

switch (State)
{
    case ETimecodeProviderSynchronizationState::Closed:
        UE_LOG(LogTemp, Log, TEXT("时间码提供者已关闭。"));
        break;
    case ETimecodeProviderSynchronizationState::Error:
        UE_LOG(LogTemp, Warning, TEXT("时间码提供者发生错误！请检查音频输入和 LTC 信号。"));
        break;
    case ETimecodeProviderSynchronizationState::Synchronizing:
        UE_LOG(LogTemp, Log, TEXT("正在尝试同步 LTC 信号..."));
        break;
    case ETimecodeProviderSynchronizationState::Synchronized:
        UE_LOG(LogTemp, Log, TEXT("时间码已同步！"));
        FQualifiedFrameTime Time;
        if (Provider->FetchTimecode(Time))
        {
            UE_LOG(LogTemp, Log, TEXT("同步的时间码: %s"), *Time.AsString());
        }
        break;
}

// 正确关闭
if (Provider)
{
    Provider->Shutdown(GEngine);
}
```

## Demo 示例

```cpp
// AudioTimecodeDemo.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "AudioTimecodeDemo.generated.h"

class UAudioCaptureTimecodeProvider;

UCLASS()
class AAudioTimecodeDemo : public AActor
{
    GENERATED_BODY()

public:
    AAudioTimecodeDemo();

    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
    virtual void Tick(float DeltaTime) override;

private:
    UPROPERTY()
    UAudioCaptureTimecodeProvider* TimecodeProvider;

    float LastDisplayTime = 0.f;
};
```

```cpp
// AudioTimecodeDemo.cpp
#include "AudioTimecodeDemo.h"
#include "AudioCaptureTimecodeProvider.h"

AAudioTimecodeDemo::AAudioTimecodeDemo()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AAudioTimecodeDemo::BeginPlay()
{
    Super::BeginPlay();

    // 创建时间码提供者实例
    TimecodeProvider = NewObject<UAudioCaptureTimecodeProvider>();
    if (TimecodeProvider)
    {
        // 配置 (也可以不配置，使用默认或编辑器设置的值)
        TimecodeProvider->bDetectFrameRate = true; // 让它自动检测
        TimecodeProvider->AudioChannel = 1;

        // 初始化
        bool bInitSuccess = TimecodeProvider->Initialize(GEngine);
        UE_LOG(LogTemp, Log, TEXT("时间码提供者初始化 %s"), bInitSuccess ? TEXT("成功") : TEXT("失败"));
    }
}

void AAudioTimecodeDemo::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (TimecodeProvider)
    {
        TimecodeProvider->Shutdown(GEngine);
        TimecodeProvider = nullptr;
    }
    Super::EndPlay(EndPlayReason);
}

void AAudioTimecodeDemo::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    // 每隔一段时间输出一次时间码状态
    LastDisplayTime += DeltaTime;
    if (LastDisplayTime > 1.0f && TimecodeProvider)
    {
        LastDisplayTime = 0.f;
        ETimecodeProviderSynchronizationState State = TimecodeProvider->GetSynchronizationState();
        if (State == ETimecodeProviderSynchronizationState::Synchronized)
        {
            FQualifiedFrameTime CurrentTime;
            if (TimecodeProvider->FetchTimecode(CurrentTime))
            {
                UE_LOG(LogTemp, Log, TEXT("Demo - 当前同步时间码: %s"), *CurrentTime.AsString());
            }
        }
        else
        {
            UE_LOG(LogTemp, Warning, TEXT("Demo - 时间码未同步，状态: %s"), *UEnum::GetValueAsString(State));
        }
    }
}
```

## 模块依赖

从插件的依赖插件列表 (`.uplugin`) 提取。

| 模块 | 用途 |
|---|---|
| `AudioCapture` | 提供跨平台的音频捕获设备访问接口。 |
| `LinearTimecode` | 提供 LTC 信号的解码功能。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF。 |
| 2024-10-09 | `c4ad1cc7` | Fix and silence new PVS 7.33 warnings | 修复并消除新的 PVS Studio 静态分析警告。 |
| 2023-03-22 | `a381e0b7` | [Audio Capture] WASAPI device support for audio capture. (3 of 3) | 【音频捕获】为音频捕获添加 WASAPI 设备支持。 |
| 2023-02-18 | `e599d19e` | Removing redundant Private includes. | 移除冗余的私有头文件包含。 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 更新内置插件的供应商链接以使用安全协议。 |

### 维护评价

该插件创建于 **2018 年**，至今已超过 7 年。从 git 历史看，它**仍在维护中**，最近的更新（2026 年）涉及底层日志系统的迁移，表明它仍然跟随引擎的代码规范演进。更重要的是，2023 年有针对 **WASAPI**（Windows Audio Session API）的重要功能更新，增强了其在现代 Windows 系统上的兼容性和性能。

然而，它**仍处于 Beta 版本**（`IsBetaVersion: true`）且**默认未启用**，这意味着 Epic 官方可能认为其稳定性或功能完整性尚未达到正式发布标准。对于需要 LTC 同步的专业工作流，这是一个可行的解决方案，但使用者应意识到其 Beta 状态，并可能需要在生产环境中进行充分的测试。

**结论**：这是一个有明确用途、仍在维护但功能成熟度标记为 Beta 的专业工具插件。推荐在需要 LTC 音频时间码同步的场景中使用，但需注意其 Beta 状态。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AudioCaptureTimecodeProvider)
- [官方文档]() (无)
- [测试用例]() (未提供)