# Audio Capture

> Plugin provides an interface for microphone input capture.

| 属性 | 值 |
|---|---|
| 分类 | Audio |
| 默认启用 | true |
| 包含内容 | false |
| 模块 | AudioCapture (Runtime), AudioCaptureEditor (UncookedOnly) |
| 支持程序 | LiveLinkHub |
| 创建时间 | 2017-10-26 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/AudioCapture) | |

## 用途

AudioCapture plugin 提供了 UE5 中麦克风音频输入捕获的统一接口。它封装了底层平台特定的音频捕获实现（Windows 的 WASAPI/RtAudio、macOS 的 RtAudio、iOS 的 AudioUnit、Android 的原生 API），并向上层暴露两种使用方式：

1. **UAudioCaptureComponent** — 继承自 `USynthComponent`，可直接作为 Actor 组件添加到场景中，将麦克风音频实时注入 UE 音频引擎的合成管线。适合需要将麦克风声音作为游戏内音频源播放的场景。
2. **UAudioCapture** — 继承自 `UAudioGenerator`，提供更底层的捕获控制，允许手动打开流、启停捕获、查询设备信息。适合需要直接获取音频数据进行处理的场景。

此外，plugin 还提供了 `UAudioCaptureBlueprintLibrary` 用于查询系统上所有可用的音频输入设备。

**注意**：此 plugin 当前配置为仅在 **LiveLinkHub** 程序中加载（`ProgramAllowList: ["LiveLinkHub"]`），不会在标准编辑器或游戏中自动启用。要在其他程序中使用，需要修改 `.uplugin` 或通过其他方式加载。

## 使用场景

- 你在做 LiveLink 相关的音频录制工作 → 用 AudioCapture 的 Take Recorder 集成
- 你需要在游戏/应用中实时播放麦克风输入 → 用 UAudioCaptureComponent 作为 Actor Component
- 你需要枚举系统上的麦克风设备让用户选择 → 用 UAudioCaptureBlueprintLibrary::GetAvailableAudioInputDevices
- 你需要获取原始麦克风音频数据进行自定义处理（如语音识别、音量检测） → 用 UAudioCapture

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Audio Capture` | 创建一个已打开默认音频流的 UAudioCapture 对象 | `UAudioCaptureFunctionLibrary` |
| `Get Audio Capture Device Info` | 获取当前捕获设备的名称、通道数、采样率 | `UAudioCapture` |
| `Start Capturing Audio` | 开始捕获麦克风音频 | `UAudioCapture` |
| `Stop Capturing Audio` | 停止捕获麦克风音频 | `UAudioCapture` |
| `Is Capturing Audio` | 查询当前是否正在捕获 | `UAudioCapture` |
| `Get Available Audio Input Devices` | 异步获取所有可用的音频输入设备列表 | `UAudioCaptureBlueprintLibrary` |
| `Audio Input Device Info To String` | 将设备信息转换为可读字符串（BlueprintPure） | `UAudioCaptureBlueprintLibrary` |

### 核心数据结构

| 结构体 | 说明 |
|---|---|
| `FAudioInputDeviceInfo` | 蓝图可用的音频输入设备信息：DeviceName、DeviceId、InputChannels、PreferredSampleRate、bSupportsHardwareAEC |
| `FAudioCaptureDeviceInfo` | 捕获设备信息：DeviceName、NumInputChannels、SampleRate |

### 使用示例（蓝图描述）

**获取设备列表并选择麦克风：**

1. 调用 `Get Available Audio Input Devices` 节点，绑定 `OnAudioInputDevicesObtained` 委托
2. 在回调中，从 `AvailableDevices` 数组获取 `FAudioInputDeviceInfo` 列表
3. 用设备信息展示给用户选择

**直接使用默认麦克风捕获并播放：**

1. 调用 `Create Audio Capture` 节点创建捕获对象
2. 对返回的对象调用 `Start Capturing Audio`
3. 捕获的声音会通过 UAudioGenerator 自动注入音频引擎

## C++ 用法

### 头文件引入

```cpp
// 使用 UAudioCaptureComponent
#include "AudioCaptureComponent.h"

// 使用 UAudioCapture 和工厂函数
#include "AudioCapture.h"

// 使用设备查询库
#include "AudioCaptureBlueprintLibrary.h"
```

### 基本用法：UAudioCaptureComponent

`UAudioCaptureComponent` 继承自 `USynthComponent`，可直接添加到 Actor 上。它自动打开默认麦克风设备，将捕获的音频送入合成管线播放。

```cpp
// 在 Actor 中添加麦克风捕获组件
// 来源: AudioCaptureComponent.h
UPROPERTY(VisibleAnywhere)
UAudioCaptureComponent* AudioCaptureComp;

// 创建组件
AudioCaptureComp = CreateDefaultSubobject<UAudioCaptureComponent>(TEXT("AudioCapture"));

// 调整延迟参数（默认值在 0-1024 之间）
// 增大此值可减少欠载但增加延迟
AudioCaptureComp->JitterLatencyFrames = 10;

// 组件激活后（Play 时）自动开始捕获
// 停用时自动停止
```

### 基本用法：UAudioCapture（工厂方式）

通过蓝图库中的工厂函数创建捕获对象，手动控制捕获流程。

```cpp
// 来源: AudioCapture.cpp - UAudioCaptureFunctionLibrary::CreateAudioCapture
UAudioCapture* Capture = UAudioCaptureFunctionLibrary::CreateAudioCapture();
if (Capture)
{
    // 获取设备信息
    FAudioCaptureDeviceInfo DeviceInfo;
    if (Capture->GetAudioCaptureDeviceInfo(DeviceInfo))
    {
        UE_LOG(LogTemp, Log, TEXT("Device: %s, Channels: %d, SampleRate: %d"),
            *DeviceInfo.DeviceName.ToString(),
            DeviceInfo.NumInputChannels,
            DeviceInfo.SampleRate);
    }
    
    // 开始捕获
    Capture->StartCapturingAudio();
    
    // 检查状态
    if (Capture->IsCapturingAudio())
    {
        UE_LOG(LogTemp, Log, TEXT("Capturing audio..."));
    }
    
    // 停止捕获
    Capture->StopCapturingAudio();
}
```

### 进阶用法：枚举系统音频输入设备

```cpp
// 来源: AudioCaptureBlueprintLibrary.cpp
// 必须在音频线程上执行，BlueprintLibrary 内部会自动切换到音频线程
UAudioCaptureBlueprintLibrary::GetAvailableAudioInputDevices(
    WorldContextObject,
    FOnAudioInputDevicesObtained::CreateLambda(
        [](const TArray<FAudioInputDeviceInfo>& AvailableDevices)
        {
            for (const FAudioInputDeviceInfo& Device : AvailableDevices)
            {
                UE_LOG(LogTemp, Log, TEXT("Device: %s, ID: %s, Channels: %d, SampleRate: %d, AEC: %s"),
                    *Device.DeviceName,
                    *Device.DeviceId,
                    Device.InputChannels,
                    Device.PreferredSampleRate,
                    Device.bSupportsHardwareAEC ? TEXT("Yes") : TEXT("No"));
            }
        }
    )
);
```

### 进阶用法：通过 UAudioGenerator 回调获取音频数据

`UAudioCapture` 继承自 `UAudioGenerator`，可以通过绑定 `OnAudioGenerated` 委托来接收原始音频数据：

```cpp
// UAudioCapture 内部通过 OpenDefaultAudioStream() 注册了音频回调
// 在 AudioCapture.cpp 中：
// OnCapture 回调将捕获的 PCM 数据传递给 OnGeneratedAudio()
// 你可以订阅此事件来获取原始浮点音频数据
```

## Demo 示例

完整的最小示例：在 Actor 中添加麦克风捕获并实时播放。

### MyAudioCaptureActor.h

```cpp
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

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    UAudioCaptureComponent* CaptureComponent;
};
```

### MyAudioCaptureActor.cpp

```cpp
#include "MyAudioCaptureActor.h"
#include "AudioCaptureComponent.h"

AMyAudioCaptureActor::AMyAudioCaptureActor()
{
    CaptureComponent = CreateDefaultSubobject<UAudioCaptureComponent>(TEXT("MicCapture"));
    RootComponent = CaptureComponent;
    
    // 设置抖动延迟帧数（平衡延迟与稳定性）
    CaptureComponent->JitterLatencyFrames = 10;
}
```

### MyProject.Build.cs 依赖

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Engine",
    "AudioCapture"
});
```

> **注意**：AudioCapture 模块会根据目标平台自动引入对应的底层实现模块（WASAPI、RtAudio、AudioUnit 等），无需手动添加。

## 模块依赖

### AudioCapture（Runtime）

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心功能 |
| `AudioMixer` | 音频混音器 |
| `AudioCaptureCore` | 音频捕获核心抽象层 |
| `AudioCaptureWasapi` | Windows 平台 WASAPI 捕获实现（Win64 私有依赖） |
| `AudioCaptureRtAudio` | 跨平台 RtAudio 捕获实现（Win64/Mac 私有依赖） |
| `AudioCaptureAudioUnit` | iOS 平台 AudioUnit 捕获实现（iOS 私有依赖） |
| `AudioCaptureAndroid` | Android 平台捕获实现（Android 私有依赖） |

### AudioCaptureEditor（UncookedOnly, Win64）

| 模块 | 用途 |
|---|---|
| `UnrealEd` | 编辑器框架 |
| `AudioEditor` | 音频编辑器工具 |
| `AudioCapture` | 本插件 Runtime 模块 |
| `AudioCaptureCore` | 音频捕获核心 |
| `AudioCaptureRtAudio` | RtAudio 捕获实现 |
| `AudioCaptureWasapi` | WASAPI 捕获实现（Win64） |
| `DirectSound` | RtAudio 的 Win64 依赖 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-08-18 | `c2b5d90f4bbf` | Allow take recorder microphone sources to work in -game | 功能性更新：修复了 Take Recorder 在 -game 模式下麦克风源不工作的问题，说明此 plugin 与 Take Recorder 深度集成 |
| 2025-06-26 | `ec9009980d52` | Added UE_INLINE_GENERATED_CPP_BY_NAME | 代码维护：添加内联生成代码宏，减少编译时间 |
| 2025-04-23 | `6ae573356bbf` | Used UnrealGame build target to convert files to dllstorage | 构建维护：DLL 导出标记规范化 |

### 维护评价

- **创建时间**：2017 年 10 月，已存在 8 年以上
- **最近更新**：2025 年 8 月有功能性更新，6 月和 4 月有代码维护更新
- **活跃程度**：活跃维护中 — 最近 6 个月内有实质性功能修复
- **限制**：
  - 当前配置为仅在 LiveLinkHub 中加载，标准编辑器/游戏中不会自动启用
  - AudioCaptureEditor 模块仅支持 Win64
  - 捕获使用默认设备，不支持指定特定输入设备（通过 UAudioCapture API）
- **推荐**：✅ 推荐使用。作为 Epic 官方的麦克风捕获接口，持续维护且与 Take Recorder 集成。但需注意 ProgramAllowList 限制，若要在游戏项目中使用需修改 .uplugin 配置。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/AudioCapture)
- 官方文档：无（.uplugin 中 DocsURL 为空）
- 底层实现模块：
  - [AudioCaptureCore](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Source/Runtime/AudioCaptureCore) — 平台无关的音频捕获抽象
  - [AudioCaptureRtAudio](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Source/Runtime/AudioCaptureRtAudio) — RtAudio 后端
  - [AudioCaptureWasapi](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Source/Runtime/AudioCaptureWasapi) — Windows WASAPI 后端
