# Audio Capture

> Plugin provides an interface for microphone input capture.

| 属性 | 值 |
|---|---|
| 中文名 | 音频捕获 |
| 分类 | Audio |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AudioCapture` (Runtime), `AudioCaptureEditor` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2017-10-26 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AudioCapture) | |

## 用途

此插件的核心目的是为 Unreal Engine 的程序（特别是 LiveLinkHub）提供一个统一的接口，用于从系统麦克风捕获音频输入。它封装了平台特定的底层音频捕获实现（如 Windows 的 WASAPI、RtAudio、macOS/iOS 的 AudioUnit 等），并通过 `UAudioCaptureComponent` 等组件或子系统提供易于在运行时使用的 API。这使得开发者能够快速实现实时音频输入功能，而无需关心跨平台底层差异。

## 使用场景

- 你需要在运行时从麦克风获取音频数据，用于游戏内语音聊天、语音指令或录音功能。
- 你正在使用 LiveLinkHub，并希望将麦克风音频作为实时数据源进行捕获和处理。
- 你的项目需要跨平台（Windows, Mac, Android 等）的麦克风捕获能力，并希望使用统一的 API。

## 蓝图用法

该插件的蓝图接口主要围绕 `UAudioCaptureSubsystem` 和 `UAudioCaptureComponent` 展开。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Start Capturing` | 开始从麦克风捕获音频。 | `UAudioCaptureSubsystem` |
| `Stop Capturing` | 停止捕获麦克风音频。 | `UAudioCaptureSubsystem` |
| `Get Audio Capture Component` | 获取或创建附加到指定Actor上的音频捕获组件。 | `UAudioCaptureSubsystem` |
| `Start` | 开始组件的音频捕获。 | `UAudioCaptureComponent` |
| `Stop` | 停止组件的音频捕获。 | `UAudioCaptureComponent` |

### 使用示例（蓝图描述）

1.  **通过子系统使用**：在任意蓝图（如你的 PlayerController）中，调用 `Get Audio Capture Subsystem` 节点获取 `UAudioCaptureSubsystem`。然后调用其 `Start Capturing` 节点。系统会自动管理一个全局的捕获实例。
2.  **通过组件使用**：将 `UAudioCaptureComponent` 添加到任何 Actor（如你的 Pawn）上。在该 Actor 的蓝图中，直接调用该组件的 `Start` 节点来开始捕获。捕获到的音频数据会通过组件的音频输出自动播放（可通过 `bAutoPlay` 属性控制）。

## C++ 用法

### 头文件引入

```cpp
#include "AudioCaptureComponent.h"
// 如需直接操作捕获器，可包含
#include "AudioCapture.h"
```

### 基本用法

使用 `UAudioCaptureComponent` 是最简单的集成方式。

```cpp
// 在 Actor 的头文件 (.h) 中
UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Audio")
UAudioCaptureComponent* AudioCaptureComp;

// 在 Actor 的构造函数或 BeginPlay 中 (.cpp)
AudioCaptureComp = CreateDefaultSubobject<UAudioCaptureComponent>(TEXT("AudioCaptureComp"));
AudioCaptureComp->SetupAttachment(RootComponent);
AudioCaptureComp->bAutoPlay = true; // 设为 true 可在开始时自动播放捕获的音频
```

### 进阶用法

直接使用 `FAudioCapture` 类以更低级别的方式捕获音频数据，适用于需要直接处理PCM数据的场景。

```cpp
#include "AudioCapture.h"

FAudioCapture AudioCapture;
// 获取默认设备信息
FAudioCaptureDeviceInputInfo Info;
if (AudioCapture.GetDefaultInputDeviceInfo(Info))
{
    UE_LOG(LogTemp, Log, TEXT("Default Device: %s"), *Info.DeviceName);
}

// 设置捕获回调，处理PCM数据
AudioCapture.CaptureAudio(FOnAudioCaptureFunction::CreateLambda(
    [](const float* InPCMData, int32 NumSamples, int32 InChannels, double InSampleRate)
    {
        // 在此处处理捕获到的音频数据
        // InPCMData: 原始浮点PCM数据
        // NumSamples: 采样点总数（单声道）
        // InChannels: 通道数
        // InSampleRate: 采样率
    }
));

// 开始捕获
AudioCapture.StartCapturing();

// ... 结束时停止
AudioCapture.StopCapturing();
```

## Demo 示例

一个最小化的 Actor，用于捕获麦克风音频并自动播放。

**AudioCaptureDemoActor.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "AudioCaptureDemoActor.generated.h"

class UAudioCaptureComponent;

UCLASS()
class AAudioCaptureDemoActor : public AActor
{
    GENERATED_BODY()
    
public:
    AAudioCaptureDemoActor();

protected:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
    UAudioCaptureComponent* CaptureComponent;
};
```

**AudioCaptureDemoActor.cpp**
```cpp
#include "AudioCaptureDemoActor.h"
#include "AudioCaptureComponent.h"

AAudioCaptureDemoActor::AAudioCaptureDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;

    CaptureComponent = CreateDefaultSubobject<UAudioCaptureComponent>(TEXT("CaptureComponent"));
    RootComponent = CaptureComponent;
    
    // 设置为自动播放捕获的音频
    CaptureComponent->bAutoPlay = true;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AudioCaptureWasapi` | 提供 Windows 平台的 WASAPI 音频捕获实现 |
| `AudioCaptureRtAudio` | 提供基于 RtAudio 库的跨平台音频捕获实现 |
| `AudioCaptureAudioUnit` | 提供 macOS/iOS 平台的 AudioUnit 音频捕获实现 |
| `AudioCaptureAndroid` | 提供 Android 平台的音频捕获实现 |
| `AudioMixer` | 作为底层音频渲染引擎，`AudioCaptureComponent` 依赖它来播放捕获到的音频 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏，属于引擎级代码风格统一更新。 |
| 2025-10-30 | `a0e12af6` | Ran UnrealCodeFixup on Engine to change all ~Type() {} to instead be ~Type() = default | 代码现代化，将析构函数改为 `= default`。 |
| 2025-08-18 | `c2b5d90f` | Allow take recorder microphone sources to work in -game. | **功能更新**：允许录制器中的麦克风源在 `-game` 模式下工作。 |
| 2025-06-26 | `ec900998` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. | 构建系统优化，减少生成的 cpp 文件。 |
| 2025-04-23 | `6ae57335` | Used UnrealGame build target to find and convert all files to have dllstorage on methods/staticvar | 导出符号相关调整。 |

### 维护评价

该插件**仍在活跃维护**。虽然其核心架构已存在多年，但近期（2025年8月）仍有针对特定场景（如游戏模式下的录制）的功能性更新，并且持续参与引擎级的代码现代化和构建优化。作为 `LiveLinkHub` 的一个依赖项，其运行时核心功能保持稳定。推荐在需要麦克风输入的项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AudioCapture)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/AudioCapture)