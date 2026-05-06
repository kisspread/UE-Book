# WMFCodecs

> Adds codecs from the Windows Media Foundation to AVCodecs

| 属性 | 值 |
|---|---|
| 中文名 | WMF编解码器 |
| 分类 | Codecs |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `WMFCodecs` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-01-25 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AVCodecs/WMFCodecs) | |

## 用途

WMFCodecs 是 AVCodecs 框架的 Windows 平台扩展，它利用 Windows Media Foundation（WMF）API 提供音频编码能力。AVCodecs 是 UE5 中统一的音视频编解码抽象层，WMFCodecs 为其添加了 Windows 原生的硬件/软件音频编码器实现（如 AAC 等），使得在 Windows 64 位系统上能够通过系统内置的媒体基础组件完成音频编码任务，而不需要额外第三方库。

该插件解决了跨平台编解码框架无法直接使用 Windows 特定编码器的问题，为希望利用 Windows 原生编码性能或兼容性的项目提供了标准化接入点。

## 使用场景

- 你在开发一个需要录制或实时编码音频的 Windows 游戏（例如语音聊天、广播、回放录制），希望使用 Windows 系统自带的媒体基础编码器来减少包体和兼容性问题。
- 你的项目已使用 AVCodecs 框架处理视频/音频编解码，需要在 Windows 上扩展音频编码能力。
- 你需要一个统一的编码器接口来管理不同平台的音频编码，而 WMFCodecs 让 Windows 上的原生编码器可以与其他平台（如 macOS 的 AudioToolbox）无缝替换。

## 蓝图用法

此插件不提供任何蓝图节点。FAudioEncoderWMF 是纯 C++ 类，通过 AVCodecs 框架在 C++ 层控制，无法直接在蓝图调用。

## C++ 用法

### 头文件引入

```cpp
#include "Audio/Encoders/AudioEncoderWMF.h"
#include "Audio/Encoders/Configs/AudioEncoderConfigWMF.h"
```

### 基本用法

```cpp
// 创建 WMF 音频编码器实例
TSharedRef<FAudioEncoderWMF> Encoder = MakeShared<FAudioEncoderWMF>();

// 获取默认 AV 设备
TSharedRef<FAVDevice> Device = FAVDevice::GetDefault();
// 创建 AV 实例（通常全局共享）
TSharedRef<FAVInstance> Instance = FAVInstance::CreateShared();

// 打开编码器
FAVResult Result = Encoder->Open(Device, Instance);
if (Result.IsSuccess())
{
    // 配置编码器参数（例如 AAC 编码）
    FAudioEncoderConfigWMF Config;
    Config.CodecType = MFAudioFormat_AAC;  // 或使用 FAudioEncoderConfigAAC 转换
    Config.Preset = EAVPreset::HighQuality;
    Encoder->ApplyConfig(Config);

    // 发送音频数据（假设已有音频资源）
    TSharedPtr<FAudioResourceCPU> AudioResource = ...;
    uint32 Timestamp = 0;
    Encoder->SendFrame(AudioResource, Timestamp);

    // 接收编码后的包
    FAudioPacket OutPacket;
    while (Encoder->ReceivePacket(OutPacket))
    {
        // 处理编码后的音频数据包
    }
}
```

**来源文件**: `Engine/Plugins/Experimental/AVCodecs/WMFCodecs/Source/WMFCodecs/Public/Audio/Encoders/AudioEncoderWMF.h`

### 进阶用法

利用 `FAVExtension::TransformConfig` 将通用音频编码器配置（如 `FAudioEncoderConfigAAC`）转换为 `FAudioEncoderConfigWMF`，实现跨平台配置统一：

```cpp
#include "Audio/Encoders/Configs/AudioEncoderConfigAAC.h"

FAudioEncoderConfigAAC AACConfig;
AACConfig.BitRate = 128000;
AACConfig.SampleRate = 48000;

FAudioEncoderConfigWMF WMFConfig;
FAVExtension::TransformConfig(WMFConfig, AACConfig);
Encoder->ApplyConfig(WMFConfig);
```

## Demo 示例

以下是一个最小可编译的 C++ 示例，演示如何在 Windows 平台使用 WMFCodecs 编码音频数据为 AAC。

### EncoderDemo.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Audio/Encoders/AudioEncoderWMF.h"

class FWMFEncoderDemo
{
public:
    void Run();
private:
    TSharedPtr<FAudioEncoderWMF> Encoder;
};
```

### EncoderDemo.cpp

```cpp
#include "EncoderDemo.h"
#include "Audio/Encoders/Configs/AudioEncoderConfigWMF.h"
#include "Audio/AudioEncoder.h"
#include "Audio/Resources/AudioResourceCPU.h"
#include "AVResult.h"

void FWMFEncoderDemo::Run()
{
    Encoder = MakeShared<FAudioEncoderWMF>();
    TSharedRef<FAVDevice> Device = FAVDevice::GetDefault();
    TSharedRef<FAVInstance> Instance = FAVInstance::CreateShared();

    FAVResult Result = Encoder->Open(Device, Instance);
    if (!Result.IsSuccess())
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to open WMF Audio Encoder: %s"), *Result.ToString());
        return;
    }

    // 配置 AAC
    FAudioEncoderConfigWMF Config;
    Config.CodecType = MFAudioFormat_AAC;
    Config.Preset = EAVPreset::Default;
    Encoder->ApplyConfig(Config);

    // 模拟发送一个静音帧（假设 48000Hz 单声道，20ms 帧）
    constexpr int32 SampleRate = 48000;
    constexpr int32 NumChannels = 1;
    constexpr int32 NumSamples = SampleRate * 0.02f; // 960 samples
    TArray<int16> Silence;
    Silence.SetNumZeroed(NumSamples);

    auto Resource = MakeShared<FAudioResourceCPU>();
    Resource->Data = MakeShareable(new int16[Silence.Num()]);
    FMemory::Memcpy(Resource->Data.Get(), Silence.GetData(), Silence.Num() * sizeof(int16));
    Resource->NumSamples = Silence.Num();
    Resource->NumChannels = NumChannels;
    Resource->SampleRate = SampleRate;

    Encoder->SendFrame(Resource, 0);

    FAudioPacket Packet;
    while (Encoder->ReceivePacket(Packet))
    {
        // Packet.Data 包含编码后的 AAC 数据
        UE_LOG(LogTemp, Log, TEXT("Encoded packet: %d bytes"), Packet.Data.Num());
    }

    Encoder->Close();
}
```

## 模块依赖

要使用 WMFCodecs，你的模块需要在 `Build.cs` 中增加以下依赖：

| 模块 | 用途 |
|---|---|
| `AVCodecsCore` | 提供音视频编解码抽象设备、实例、资源和配置基础类型 |

**注意**：WMFCodecs 内部使用 Windows Media Foundation API，但在 `Build.cs` 中已自动处理链接，无需额外声明。

## 维护状态

### 近期更新

- 2026-01-22 `ad8a0de1` — Update BuildVersionSettings that are out of date
- 2025-03-13 `6aff9a26` — Do not mark non-installed plugins as installed
- 2024-05-28 `15afa78d` — Add test to make sure the module name in the IMPLEMENT_MODULE macros matches the name
- 2023-01-25 `32db50d3` — Disable AVCodecsCore for Apple platforms
- 2023-01-25 `5c48dbd6` — Added new experimental plugin AVCodecs which handles software/hardware encoding and decoding

### 维护评价

- **创建时间**: 2023-01-25（约 3 年）
- **近期更新**: 最近一次实质性代码变更是 2023-01-25 的初始提交，后续更新均为构建系统/版本标签修正，没有功能增强或 bug 修复。
- **活跃度**: 实验性插件，上游 AVCodecsCore 仍在活跃开发，但 WMFCodecs 本身自创建以来未增加新功能。
- **已知问题**: 依赖 `Windows Media Foundation`，仅支持 Win64 平台；参考 `.uplugin` 中 `IsExperimentalVersion=true`，可能会有 API 不稳定或缺少部分格式支持。
- **推荐度**: 可用于原型验证和 Windows 平台早期集成，但在生产项目中需注意实验性标记可能带来的破坏性变更风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AVCodecs/WMFCodecs)
- [AVCodecs Core 文档（暂缺）](https://docs.unrealengine.com/5.3/API/Plugins/AVCodecsCore/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AVCodecs/WMFCodecs/Source)（插件内无独立测试目录）