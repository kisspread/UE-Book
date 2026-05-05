# SoundFields

> Plugin featuring a variety of basic audio SoundFields solutions.

| 属性 | 值 |
|---|---|
| 分类 | Audio |
| 默认启用 | ✅ true |
| 包含内容 | false |
| 模块 | SoundFields (Runtime, PreDefault) |
| 创建时间 | 2020-02-09 |
| 年龄标签 | 👴 老古董(>5年) |
| Beta | ⚠️ IsBetaVersion = true |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/SoundFields) | |

## 用途

SoundFields 是 Unreal Audio Engine 的**默认 Ambisonics（高阶球谐函数空间音频）实现**。它提供了将多通道音频编码为 Ambisonics 格式、从 Ambisonics 解码回扬声器布局、以及在不同 Ambisonics 阶数之间转码的完整管线。

**为什么需要这个 plugin？** Ambisonics 是一种与扬声器布局无关的球形音频表示方法，广泛用于 VR/AR 空间音频、360° 视频和沉浸式音频制作。SoundFields plugin 让 UE5 的音频引擎能够原生支持 Ambisonics 编解码，无需第三方插件。

核心功能：
- **编码**：将任意多通道音频根据声源位置编码为 Ambisonics 格式
- **解码**：将 Ambisonics 音频解码到目标扬声器布局（支持虚拟 7.1 中间步骤）
- **转码**：在不同 Ambisonics 阶数之间转换（1–5 阶）
- **混音**：混合多个 Ambisonics 流，自动处理旋转到世界坐标

### 关键概念

Ambisonics 阶数与通道数的关系：**通道数 = (阶数 + 1)²**

| 阶数 | 通道数 | 典型用途 |
|---|---|---|
| 1 | 4 | 基础空间音频（FOA） |
| 2 | 9 | 中等精度 |
| 3 | 16 | 高精度空间音频 |
| 5 | 36 | 最高支持阶数 |

## 使用场景

- 你正在开发 **VR/AR 应用**，需要精确的头部追踪空间音频 → 启用 SoundFields 并在 Submix 上配置 Ambisonics 格式
- 你在制作 **360° 全景视频/音频**内容 → 使用 Ambisonics 编码捕获完整的声场
- 你需要 **与设备无关的空间音频**渲染 → Ambisonics 可以解码到任意扬声器布局
- 你使用了 Ambisonics 格式的录音素材（如 YouTube Spatial Audio） → 在 UE5 中解码播放

## 蓝图用法

SoundFields plugin 没有直接暴露给蓝图的 `BlueprintCallable` 函数或 `BlueprintReadWrite` 属性。它是通过 **引擎音频系统的 Submix 配置** 自动工作的。

### 配置方式（编辑器）

1. 在 **Sound Submix** 资产的 Details 面板中，设置 **Soundfield Effect** 使用 Ambisonics 格式
2. 在音频源的 **Attenuation** 设置中配置空间化选项
3. 通过 `UAmbisonicsEncodingSettings`（在编辑器中可配置）设置 Ambisonics 阶数

### UAmbisonicsEncodingSettings 属性

| 属性 | 类型 | 范围 | 说明 |
|---|---|---|---|
| `AmbisonicsOrder` | int32 | 1–5 | Ambisonics 阶数，通道数 = (N+1)² |

## C++ 用法

SoundFields 主要作为引擎内部的 Ambisonics 编解码器运行，但其核心类可以被 C++ 代码直接使用或扩展。

### 头文件引入

```cpp
#include "SoundFields.h"                    // UAmbisonicsEncodingSettings, FAmbisonicsSoundfieldFormat
#include "ISoundfieldFormat.h"              // ISoundfieldFactory, ISoundfieldEncoderStream, etc.
#include "SoundFieldRendering.h"            // FAmbisonicsSoundfieldBuffer, FSoundFieldDecoder
```

### 基本用法：获取默认 Ambisonics 格式

```cpp
// 获取已注册的 Ambisonics 格式工厂
ISoundfieldFactory* Factory = ISoundfieldFactory::Get(GetUnrealAmbisonicsFormatName());
if (Factory)
{
    // 获取默认编码设置
    const USoundfieldEncodingSettingsBase* DefaultSettings = Factory->GetDefaultEncodingSettings();
}
```

### 基本用法：创建编解码流

```cpp
// 创建编码流（多通道音频 → Ambisonics）
FAudioPluginInitializationParams InitInfo; /* 从引擎获取 */
ISoundfieldEncodingSettingsProxy& Settings = GetAmbisonicsSourceDefaultSettings();

TUniquePtr<ISoundfieldEncoderStream> Encoder = Factory->CreateEncoderStream(InitInfo, Settings);

// 创建解码流（Ambisonics → 扬声器输出）
TUniquePtr<ISoundfieldDecoderStream> Decoder = Factory->CreateDecoderStream(InitInfo, Settings);

// 创建混音流（混合多个 Ambisonics 流）
TUniquePtr<ISoundfieldMixerStream> Mixer = Factory->CreateMixerStream(Settings);
```

### 进阶用法：手动解码 Ambisonics 音频

```cpp
// 使用 FSoundFieldDecoder 直接解码
FSoundFieldDecoder Decoder;

FAmbisonicsSoundfieldBuffer AmbisonicsInput;
// ... 填充 Ambisonics 音频数据 ...

FSoundfieldSpeakerPositionalData OutputPositions;
// ... 设置输出扬声器位置 ...

Audio::FAlignedFloatBuffer OutputBuffer;

// 方式 1：先解码到虚拟 7.1 再混缩到设备（默认，音质更好）
Decoder.DecodeAudioToSevenOneAndDownmixToDevice(AmbisonicsInput, OutputPositions, OutputBuffer);

// 方式 2：直接解码到设备输出配置（性能更好）
Decoder.DecodeAudioDirectlyToDeviceOutputPositions(AmbisonicsInput, OutputPositions, OutputBuffer);
```

### 进阶用法：Ambisonics 阶数转换

```cpp
// 创建转码流（不同阶数的 Ambisonics 之间转换）
TUniquePtr<ISoundfieldTranscodeStream> Transcoder = Factory->CreateTranscoderStream(
    GetUnrealAmbisonicsFormatName(),  // 源格式
    SourceSettings,                     // 源阶数设置（如 1 阶）
    GetUnrealAmbisonicsFormatName(),  // 目标格式
    DestSettings,                       // 目标阶数设置（如 3 阶）
    InitInfo
);

// 转码：低阶→高阶用零填充额外通道，高阶→低阶截断多余通道
Transcoder->Transcode(InputPacket, SourceSettings, OutputPacket, DestSettings);
```

### 控制台变量

| CVar | 默认值 | 说明 |
|---|---|---|
| `au.Ambisonics.VirtualIntermediateChannels` | 1 | 设为 1 时先解码到虚拟 7.1 再混缩到设备；设为 0 时直接解码到设备输出配置 |

## Demo 示例

一个最小示例，展示如何在 C++ 中使用 Ambisonics 编解码系统：

### Build.cs

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "AudioExtensions",    // ISoundfieldFactory 等接口
    "SoundFieldRendering" // FAmbisonicsSoundfieldBuffer, FSoundFieldDecoder
});
```

### AmbisonicsDemo.h

```cpp
#pragma once

#include "CoreMinimal.h"

class FAmbisonicsDemo
{
public:
    /** 创建一个简单的 1 阶 Ambisonics 编码并解码的演示 */
    static void RunDemo();
};
```

### AmbisonicsDemo.cpp

```cpp
#include "AmbisonicsDemo.h"
#include "SoundFields.h"
#include "SoundFieldRendering.h"
#include "ISoundfieldFormat.h"

void FAmbisonicsDemo::RunDemo()
{
    // 1. 获取 Ambisonics 格式工厂
    ISoundfieldFactory* Factory = ISoundfieldFactory::Get(GetUnrealAmbisonicsFormatName());
    if (!Factory)
    {
        UE_LOG(LogTemp, Error, TEXT("Ambisonics format not registered!"));
        return;
    }

    // 2. 创建一个空的 Ambisonics 音频包
    TUniquePtr<ISoundfieldAudioPacket> Packet = Factory->CreateEmptyPacket();
    FAmbisonicsSoundfieldBuffer& AmbiBuffer = DowncastSoundfieldRef<FAmbisonicsSoundfieldBuffer>(*Packet);

    // 3. 填充 1 阶 Ambisonics 数据（4 通道）
    AmbiBuffer.NumChannels = 4;
    const int32 NumFrames = 1024;
    AmbiBuffer.AudioBuffer.AddZeroed(NumFrames * 4);

    // 通道 0 (W) 设为静音测试信号
    for (int32 i = 0; i < NumFrames; i++)
    {
        AmbiBuffer.AudioBuffer[i * 4 + 0] = FMath::Sin(2.0f * PI * 440.0f * i / 48000.0f) * 0.5f;
    }

    // 4. 使用 FSoundFieldDecoder 解码到立体声
    FSoundFieldDecoder Decoder;
    Audio::FAlignedFloatBuffer OutputBuffer;
    OutputBuffer.AddZeroed(NumFrames * 2);

    FSoundfieldSpeakerPositionalData OutputPositions;
    // 使用默认扬声器位置
    OutputPositions.NumChannels = 2;

    Decoder.DecodeAudioDirectlyToDeviceOutputPositions(AmbiBuffer, OutputPositions, OutputBuffer);

    UE_LOG(LogTemp, Log, TEXT("Decoded %d frames of 1st-order Ambisonics to %d channels"),
        NumFrames, OutputPositions.NumChannels);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础引擎模块 |
| `CoreUObject` | UObject 系统（UAmbisonicsEncodingSettings 等） |
| `Engine` | 引擎核心 |
| `SignalProcessing` | DSP 工具函数（数组混音等） |
| `SoundFieldRendering` | Ambisonics 缓冲区、解码器、球谐函数计算 |
| `AudioExtensions` | ISoundfieldFactory 等 Soundfield 接口定义 |

> **注意**：`Core` 是 PublicDependency，其余为 PrivateDependency。如果你只是通过引擎 Submix 系统使用 Ambisonics，无需直接依赖这些模块。只有在 C++ 中直接操作 Ambisonics 数据时才需要引入 `SoundFieldRendering` 和 `AudioExtensions`。

## 维护状态

### 近期更新

| 日期 | Hash | 提交信息 | 解读 |
|---|---|---|---|
| 2025-04-23 | `89df8c17` | Used UnrealGame build target to find and convert all files to have dllstorage on methods/staticvar instead of on types | DLL 导出符号规范统一，无功能变更 |
| 2024-11-09 | `66e9bb39` | Removed all #if UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes from the code base | 清理过时的 include 兼容代码 |
| 2023-01-13 | `3c9aacb1` | Updated public headers for ~170 engine plugins using iwyu to remove includes not needed | IWYU 头文件清理，批量更新 |

### 维护评价

- **创建时间**：2020-02-09（约 6 年前，UE5.0 时期引入）
- **Beta 状态**：`IsBetaVersion = true`，标记为实验性
- **活跃度**：最近 3 次提交均为全仓库级别的批量重构/清理，**无功能性更新**
- **最后实质性更新**：自 2020 年创建后，核心代码（编解码器、混音器、转码器）从未修改
- **评价**：这是一个**稳定的基础设施插件**，功能完整但处于维护模式。代码量极小（4 个源文件），接口简洁。虽然是 Beta 标记，但已默认启用且随引擎分发多年，实际使用无问题。
- **推荐**：✅ 推荐使用。作为 UE5 唯一内置的 Ambisonics 实现，它在 VR/AR 空间音频场景中是必要的。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/SoundFields)
- [ISoundfieldFormat 接口定义](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Source/Runtime/AudioExtensions/Public/ISoundfieldFormat.h)
- [SoundFieldRendering 模块](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Source/Runtime/SoundFieldRendering/Public/SoundFieldRendering.h)
- [官方文档]()（.uplugin 中未提供 DocsURL）
