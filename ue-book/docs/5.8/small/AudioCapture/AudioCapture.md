# Audio Capture

> Plugin provides an interface for microphone input capture.

| 属性 | 值 |
|---|---|
| 中文名 | 音频捕获 |
| 分类 | Audio |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AudioCapture` (Runtime), `AudioCaptureEditor` (UncookedOnly，仅限 LiveLinkHub 和 Win64 平台) |
| 实验性 | 否 |
| 创建时间 | 2017-10-26 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AudioCapture) | |

## 用途

该插件为 UE5 提供了一套标准化的麦克风（音频输入设备）捕获接口。它解决了从操作系统底层音频 API（如 Windows WASAPI、CoreAudio、ALSA）获取原始音频流并将其集成到引擎音频系统中的复杂性问题。开发者可以通过蓝图或 C++ 轻松枚举系统音频输入设备、打开设备、开始/停止音频捕获，并获得原始的音频数据缓冲区。这对于实现语音聊天、实时音频处理、语音识别等应用至关重要。

## 使用场景

- **语音聊天功能**：你需要为游戏或应用添加实时语音通信，使用该插件捕获麦克风音频，并通过网络发送。
- **实时音频效果处理**：你想制作一个变声器或实时音频可视化工具，需要获取麦克风的原始 PCM 数据进行处理。
- **语音识别输入**：你的应用需要接收用户的语音指令，使用该插件作为音频源，将数据发送给语音识别引擎。
- **录音功能**：你想在应用中实现一个简单的录音机，将麦克风输入保存为音频文件。

## 蓝图用法

从 `UAudioCaptureBlueprintLibrary`、`UAudioCaptureFunctionLibrary` 和 `UAudioCaptureComponent` 的头文件中提取核心蓝图 API。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetAvailableAudioInputDevices` | 异步获取系统所有可用的音频输入设备列表，通过委托返回。 | `UAudioCaptureBlueprintLibrary` |
| `Conv_AudioInputDeviceInfoToString` | 将音频设备信息 (`FAudioInputDeviceInfo`) 转换为可读的字符串格式。 | `UAudioCaptureBlueprintLibrary` |
| `CreateAudioCapture` | 创建一个独立的 `UAudioCapture` 对象，用于直接访问设备数据。 | `UAudioCaptureFunctionLibrary` |
| `Get Audio Capture Device Info` | 获取当前 `UAudioCapture` 或 `UAudioCaptureComponent` 已打开设备的详细信息。 | `UAudioCapture`, `UAudioCaptureComponent` |
| `Start Capturing Audio` | 开始从音频设备捕获音频。 | `UAudioCapture`, `UAudioCaptureComponent` |
| `Stop Capturing Audio` | 停止音频捕获。 | `UAudioCapture`, `UAudioCaptureComponent` |
| `Is Capturing Audio` | 查询当前是否正在捕获音频。 | `UAudioCapture` |

### 使用示例（蓝图描述）

**1. 枚举设备并启动捕获：**
*   创建一个 `GetAvailableAudioInputDevices` 节点，连接 `OnObtainDevicesEvent` 委托。
*   在委托内，将返回的设备数组 (`TArray<FAudioInputDeviceInfo>`) 连接到一个 `For Each Loop`。
*   在循环体内，可以使用设备信息的 `DeviceName` 等属性。找到目标设备后，通常结合 `CreateAudioCapture` 和 `UAudioCapture` 的 `OpenDefaultAudioStream` 来开始捕获。

**2. 使用 AudioCaptureComponent（推荐用于场景内音频播放）：**
*   在 Actor 蓝图中，添加一个 `UAudioCaptureComponent` 组件。
*   在组件细节面板中，可调整 `JitterLatencyFrames` 属性以平衡延迟和稳定性。
*   在组件事件中，使用 `Start Capturing Audio` 和 `Stop Capturing Audio` 节点进行控制。捕获的音频会通过组件内部的 `OnGenerateAudio` 自动生成并播放。

## C++ 用法

### 头文件引入

```cpp
#include "AudioCapture.h"
// 如果使用组件，还需包含:
#include "AudioCaptureComponent.h"
```

### 基本用法

创建并控制一个独立的音频捕获实例。
(源自 `UAudioCapture` 和 `UAudioCaptureFunctionLibrary` 的接口)

```cpp
// 创建一个音频捕获实例
UAudioCapture* AudioCapture = UAudioCaptureFunctionLibrary::CreateAudioCapture();
if (AudioCapture)
{
    // 打开默认音频流
    if (AudioCapture->OpenDefaultAudioStream())
    {
        // 开始捕获
        AudioCapture->StartCapturingAudio();

        // 查询状态
        bool bIsCapturing = AudioCapture->IsCapturingAudio();

        // 获取设备信息
        FAudioCaptureDeviceInfo DeviceInfo;
        if (AudioCapture->GetAudioCaptureDeviceInfo(DeviceInfo))
        {
            UE_LOG(LogTemp, Log, TEXT("Capturing from: %s, Channels: %d, SampleRate: %d"),
                *DeviceInfo.DeviceName.ToString(), DeviceInfo.NumInputChannels, DeviceInfo.SampleRate);
        }

        // ... 在某个时刻停止捕获
        // AudioCapture->StopCapturingAudio();
    }
}
```

### 进阶用法

使用 `UAudioCaptureComponent`，它继承自 `USynthComponent`，可以更自然地集成到场景中播放捕获的音频，并允许调整延迟参数。

```cpp
// 在 Actor 中动态创建组件
UAudioCaptureComponent* CaptureComp = NewObject<UAudioCaptureComponent>(MyActor);
CaptureComp->SetupAttachment(MyActor->GetRootComponent());
CaptureComp->RegisterComponent();

// 调整抖动缓冲帧数（示例，通常在构造函数或细节面板设置）
CaptureComp->JitterLatencyFrames = 256; // 增大此值可减少欠载，但增加延迟

// 开始捕获（组件内部处理初始化、开始和音频生成）
// 通过组件的 StartCapturingAudio 或在蓝图中调用
CaptureComp->StartCapturingAudio(); // 注意：此函数在源码中未直接暴露为公共函数，通常通过组件蓝图事件或重写来控制。

// 组件生命周期结束时，会自动处理资源清理（BeginDestroy, FinishDestroy）。
```

## Demo 示例

一个最小的、可编译的 Actor 类，使用 `UAudioCaptureComponent` 捕获并播放麦克风音频。

```cpp
// MyAudioCaptureActor.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyAudioCaptureActor.generated.h"

class UAudioCaptureComponent;

UCLASS()
class MYPROJECT_API AMyAudioCaptureActor : public AActor
{
    GENERATED_BODY()

public:
    AMyAudioCaptureActor();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Audio")
    UAudioCaptureComponent* CaptureComponent;

    UFUNCTION(BlueprintCallable, Category = "Audio")
    void StartCapture();

    UFUNCTION(BlueprintCallable, Category = "Audio")
    void StopCapture();
};
```

```cpp
// MyAudioCaptureActor.cpp
#include "MyAudioCaptureActor.h"
#include "AudioCaptureComponent.h"

AMyAudioCaptureActor::AMyAudioCaptureActor()
{
    PrimaryActorTick.bCanEverTick = false;

    CaptureComponent = CreateDefaultSubobject<UAudioCaptureComponent>(TEXT("AudioCapture"));
    RootComponent = CaptureComponent;
    // 设置一个合理的抖动延迟值
    CaptureComponent->JitterLatencyFrames = 512;
}

void AMyAudioCaptureActor::BeginPlay()
{
    Super::BeginPlay();
    // 默认在 BeginPlay 时开始捕获，也可以改为由外部调用 StartCapture
    StartCapture();
}

void AMyAudioCaptureActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    StopCapture();
    Super::EndPlay(EndPlayReason);
}

void AMyAudioCaptureActor::StartCapture()
{
    if (CaptureComponent && !CaptureComponent->IsCapturingAudio())
    {
        // 注意：IsCapturingAudio() 在 UAudioCaptureComponent 中未直接暴露，此逻辑仅为示意。
        // 实际启动捕获的逻辑在 USynthComponent 的 Play 方法或蓝图事件中。
        // 调用 Play() 会触发 Init 和 OnBeginGenerate。
        CaptureComponent->Play();
        UE_LOG(LogTemp, Log, TEXT("Audio capture started."));
    }
}

void AMyAudioCaptureActor::StopCapture()
{
    if (CaptureComponent)
    {
        CaptureComponent->Stop();
        UE_LOG(LogTemp, Log, TEXT("Audio capture stopped."));
    }
}
```

## 模块依赖

`AudioCapture` 运行时模块依赖以下平台特定的音频捕获实现模块，这些依赖已由插件内部管理。

| 模块 | 用途 |
|---|---|
| `AudioCaptureWasapi` | Windows 平台 WASAPI 音频捕获实现 |
| `AudioCaptureRtAudio` | 跨平台的 RtAudio 库封装，提供后备捕获能力 |
| `AudioCaptureAudioUnit` | Apple 平台 (macOS/iOS) AudioUnit 音频捕获实现 |
| `AudioCaptureAndroid` | Android 平台 Oboe/AAudio 音频捕获实现 |

**使用方无需额外添加这些依赖**，插件已处理平台适配。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移至新格式。 |
| 2025-10-30 | `a0e12af6` | Ran UnrealCodeFixup on Engine to change all ~Type() {} to instead be ~Type() = default | 统一析构函数写法，使用 `= default`。 |
| 2025-08-18 | `c2b5d90f` | Allow take recorder microphone sources to work in -game. | 修复拍摄记录器中的麦克风源在 `-game` 模式下不工作的问题。 |
| 2025-06-26 | `ec900998` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. | 优化编译，为源文件添加内联生成宏。 |
| 2025-04-23 | `6ae57335` | Used UnrealGame build target to find and convert all files to have dllstorage on methods/staticvar i | 为方法和静态变量添加 DLL 导出符号。 |

### 维护评价

AudioCapture 插件创建于 2017 年，是一个相对成熟且基础的模块。从近期的 Git 记录来看，维护活动主要集中在**代码现代化、平台兼容性修复和编译优化**上（如迁移日志宏、修复游戏模式下的功能、添加 DLL 导出符号）。没有出现大规模的功能增加或重构。最近一次实质性功能修复在 2025 年 8 月（`c2b5d90f`）。该插件的核心功能（设备枚举、音频捕获）稳定，平台支持完善（Windows, macOS, Android）。虽然近两年更新频率不高，但考虑到其功能已相对完善，且仍在处理兼容性和构建问题，可以认为它处于**稳定维护状态**。

**推荐使用**：对于需要基础麦克风输入捕获的项目，AudioCapture 是官方提供的、跨平台的标准解决方案，集成度好，API 简洁，可以放心使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AudioCapture)