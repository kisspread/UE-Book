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

AudioCapture 插件为虚幻引擎提供了核心的**音频输入捕获与管理**框架。它的核心作用是抽象并封装平台相关的麦克风（或其他音频输入设备）访问功能，使得上层应用（如 Sequencer 的 Take Recorder、游戏内的语音聊天、自定义录音工具）能够以统一的方式进行录音。它主要解决的问题是：

1.  **跨平台设备访问**：提供统一的接口（`IAudioCaptureEditor`）来查询和操作音频输入设备，隐藏了不同平台（Windows Wasapi, RtAudio, AudioUnit 等）的实现细节。
2.  **录制状态管理**：通过 `FAudioRecordingManager`（`AudioCaptureEditor` 模块）管理录音的完整生命周期（就绪、录制、停止），并处理原始音频数据的缓冲、采样率转换、声道分离等后处理工作。
3.  **资产生成**：能够将录制的原始 PCM 数据转换为虚幻引擎标准的 `USoundWave` 资产，方便后续使用。
4.  **高级录制支持**：通过 `AudioCaptureEditor` 模块与 **Sequencer 的 Take Recorder** 深度集成，支持带有时间码、视频帧率同步的专业级录制工作流。

## 使用场景

-   **虚拟制片 (Virtual Production)**：在使用 Take Recorder 录制演员表演时，同步录制其麦克风语音。
-   **游戏内录音**：开发需要玩家语音输入的社交或语音命令功能。
-   **音频工具开发**：制作自定义的音频录制、编辑或实时处理工具。
-   **测试与调试**：捕获环境声音或系统音频用于分析。

## 蓝图用法

该插件主要提供 C++ 接口。蓝图中的使用通常通过“音频捕获”模块暴露的子系统或函数库进行。由于提供的头文件中没有显式的 `UFUNCTION(BlueprintCallable)` 宏，蓝图访问可能通过上层封装（如 Take Recorder 的蓝图功能）或引擎编辑器模块间接实现。

### 核心节点（概念性）

此插件的核心功能偏向底层系统和编辑器工具，其典型的蓝图交互场景在于 **Take Recorder** 的音频源设置面板。

在 Take Recorder 的设置中，你可以：
1.  选择一个音频输入设备（基于 `GetCaptureDevicesAvailable` 返回的设备列表）。
2.  设置录制参数（缓冲区大小、时长等，对应 `FTakeRecorderAudioSettings`）。
3.  启动和停止带有音频源的录制（内部调用 `IAudioCaptureEditor` 的 `Start` 和 `Stop`）。

### 使用示例（蓝图描述）

在 Sequencer 中使用 Take Recorder 记录音频：
1.  打开 Sequencer，添加一个 `Take Recorder` 轨道。
2.  在 Take Recorder 的源列表中，点击添加 `+` 按钮，选择 `Microphone Audio`。
3.  在音频源的属性面板中，从 `Device` 下拉菜单选择你的麦克风设备。
4.  调整 `Gain (dB)`、`Buffer Size` 等设置。
5.  点击 Take Recorder 的录制按钮。录制的音频将与视频数据一起被保存和同步。

## C++ 用法

此插件提供了清晰的 C++ 接口用于底层音频捕获和集成。

### 头文件引入

要使用编辑器录制功能（与 Take Recorder 集成）：
```cpp
#include "IAudioCaptureEditorModule.h"
#include "IAudioCaptureEditor.h"
```
要使用底层的录制管理器（通常在 `AudioCaptureEditor` 模块内部使用）：
```cpp
#include "AudioRecordingManager.h"
```

### 基本用法

以下示例展示了如何通过模块接口创建和管理一个音频录制器实例。这是集成自定义录音逻辑的标准方式。
（来源：`Public/IAudioCaptureEditorModule.h`, `Public/IAudioCaptureEditor.h`）

```cpp
// 1. 获取音频捕获编辑器模块
IAudioCaptureEditorModule* AudioCaptureEditorModule = FModuleManager::GetModulePtr<IAudioCaptureEditorModule>(TEXT("AudioCaptureEditor"));

if (AudioCaptureEditorModule && AudioCaptureEditorModule->HasAudioRecorder())
{
    // 2. 创建一个音频录制器实例
    TUniquePtr<IAudioCaptureEditor> AudioRecorder = AudioCaptureEditorModule->CreateAudioRecorder();

    if (AudioRecorder)
    {
        // 3. 配置录制设置
        FTakeRecorderAudioSettings AudioSettings;
        AudioSettings.AudioCaptureDeviceId = TEXT(""); // 留空将使用默认设备，或填入具体设备ID
        AudioSettings.AudioInputBufferSize = 2048;

        // 4. 检查状态并开始录制
        if (AudioRecorder->IsReadyToRecord())
        {
            AudioRecorder->Start(AudioSettings);
            UE_LOG(LogTemp, Log, TEXT("Audio recording started."));

            // ... 经过一段时间或满足某些条件后 ...

            // 5. 停止录制
            AudioRecorder->Stop();
            UE_LOG(LogTemp, Log, TEXT("Audio recording stopped."));

            // 6. 获取录制结果
            FTakeRecorderAudioSourceSettings SourceSettings;
            SourceSettings.Directory.Path = TEXT("/Game/RecordedAudio");
            SourceSettings.AssetName = TEXT("MyRecording");
            SourceSettings.GainDb = 0.0f;

            TObjectPtr<USoundWave> RecordedSoundWave = AudioRecorder->GetRecordedSoundWave(SourceSettings);
            if (RecordedSoundWave)
            {
                UE_LOG(LogTemp, Log, TEXT("Successfully created USoundWave: %s"), *RecordedSoundWave->GetName());
            }
        }
    }
}
```

### 进阶用法

查询可用的音频捕获设备信息。
（来源：`Public/IAudioCaptureEditor.h`, `Public/AudioCaptureEditorTypes.h`）

```cpp
if (AudioRecorder)
{
    TArray<FTakeRecorderAudioDeviceInfo> AvailableDevices;
    if (AudioRecorder->GetCaptureDevicesAvailable(AvailableDevices))
    {
        for (const FTakeRecorderAudioDeviceInfo& DeviceInfo : AvailableDevices)
        {
            UE_LOG(LogTemp, Log, TEXT("Device: %s, ID: %s, Channels: %d, Sample Rate: %d"),
                *DeviceInfo.DeviceName,
                *DeviceInfo.DeviceId,
                *DeviceInfo.InputChannels,
                *DeviceInfo.PreferredSampleRate);
        }

        // 获取特定设备（例如索引0）的详细信息
        FTakeRecorderAudioDeviceInfo FirstDeviceInfo;
        if (AudioRecorder->GetCaptureDeviceInfo(FirstDeviceInfo, 0))
        {
            UE_LOG(LogTemp, Log, TEXT("First device preferred sample rate: %d"), FirstDeviceInfo.PreferredSampleRate);
        }
    }
}
```

## Demo 示例

一个简单的类，封装了使用 `IAudioCaptureEditor` 接口进行录制的基本流程。

**AudioCaptureDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "IAudioCaptureEditor.h"

class FAudioCaptureDemo
{
public:
    FAudioCaptureDemo();
    ~FAudioCaptureDemo();

    /** 开始一次简单的录音 */
    bool StartDemoRecording();

    /** 停止录音并保存为资产 */
    TObjectPtr<USoundWave> StopDemoRecordingAndSave();

    /** 查询当前录制状态 */
    bool IsCurrentlyRecording() const;

private:
    TUniquePtr<IAudioCaptureEditor> Recorder;
};
```

**AudioCaptureDemo.cpp**
```cpp
#include "AudioCaptureDemo.h"
#include "IAudioCaptureEditorModule.h"

FAudioCaptureDemo::FAudioCaptureDemo()
{
    // 初始化录制器
    IAudioCaptureEditorModule* Module = FModuleManager::GetModulePtr<IAudioCaptureEditorModule>(TEXT("AudioCaptureEditor"));
    if (Module && Module->HasAudioRecorder())
    {
        Recorder = Module->CreateAudioRecorder();
    }
}

FAudioCaptureDemo::~FAudioCaptureDemo()
{
    // 确保在销毁前停止录制
    if (Recorder && Recorder->IsRecording())
    {
        Recorder->Stop();
    }
}

bool FAudioCaptureDemo::StartDemoRecording()
{
    if (!Recorder || !Recorder->IsReadyToRecord())
    {
        return false;
    }

    FTakeRecorderAudioSettings Settings;
    Settings.AudioCaptureDeviceId = TEXT(""); // 使用默认设备
    Settings.AudioInputBufferSize = 1024;
    Settings.RecordingDuration = 5.0f; // 录制5秒

    Recorder->Start(Settings);
    return Recorder->IsRecording();
}

TObjectPtr<USoundWave> FAudioCaptureDemo::StopDemoRecordingAndSave()
{
    if (!Recorder || !Recorder->IsRecording())
    {
        return nullptr;
    }

    Recorder->Stop();

    if (Recorder->IsStopped())
    {
        FTakeRecorderAudioSourceSettings SaveSettings;
        SaveSettings.Directory.Path = TEXT("/Game/DemoRecordings");
        SaveSettings.AssetName = TEXT("DemoAudioClip");
        SaveSettings.GainDb = 3.0f; // 轻微增益

        return Recorder->GetRecordedSoundWave(SaveSettings);
    }
    return nullptr;
}

bool FAudioCaptureDemo::IsCurrentlyRecording() const
{
    return Recorder.IsValid() && Recorder->IsRecording();
}
```

## 模块依赖

从 `AudioCapture` 模块的 `Build.cs` 可以看到，它是一个聚合模块，其主要职责是依赖和组织平台特定的底层音频捕获实现。

| 模块 | 用途 |
|---|---|
| `AudioCaptureWasapi` | Windows 平台的音频捕获实现（基于 WASAPI） |
| `AudioCaptureRtAudio` | 跨平台音频捕获实现（基于 RtAudio 库） |
| `AudioCaptureAudioUnit` | macOS/iOS 平台的音频捕获实现（基于 AudioUnit） |
| `AudioCaptureAndroid` | Android 平台的音频捕获实现 |

**使用者（你的项目模块）只需要依赖 `AudioCapture` 模块即可**，它会为你链接正确的平台实现。`AudioCaptureEditor` 模块是用于编辑器环境的高级封装，主要为 Take Recorder 服务。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏统一迁移到新的 UE_LOGF 格式。 |
| 2025-10-30 | `a0e12af6` | Ran UnrealCodeFixup on Engine to change all ~Type() {} to instead be ~Type() = default | 批量优化代码，将显式定义的空析构函数改为使用编译器默认版本。 |
| 2025-08-18 | `c2b5d90f` | Allow take recorder microphone sources to work in -game. | 修复了一个问题，使 Take Recorder 的麦克风音频源在 `-game` 模式下也能正常工作。 |
| 2025-06-26 | `ec900998` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. | 为相关源文件添加宏以优化编译过程，减少构建时间。 |
| 2025-04-23 | `6ae57335` | Used UnrealGame build target to find and convert all files to have dllstorage on methods/staticvar i... | 对方法和静态变量进行导出标记，以支持模块化的动态链接。 |

### 维护评价

-   **活跃维护**：尽管该插件创建于 2017 年，但从 git 记录看，**直至 2026 年仍有持续的、实质性的代码维护和功能修复**（如 `-game` 模式支持、代码规范化）。
-   **稳定性**：最近的提交主要集中在**代码质量提升、跨平台兼容性修复和构建系统优化**，而非大规模功能改动，表明该模块已进入成熟稳定期。
-   **重要性**：作为 Sequencer Take Recorder 负责音频录制的核心底层模块，它在虚拟制片工作流中扮演关键角色，因此被 Epic 持续维护。
-   **推荐使用**：**推荐使用**。这是一个稳定、维护良好且对于需要音频输入功能的项目（尤其是涉及影视录制的）来说非常重要的插件。虽然其历史较长（年龄标签为“老古董”），但这恰恰证明了其可靠性和在引擎中的核心地位。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AudioCapture)