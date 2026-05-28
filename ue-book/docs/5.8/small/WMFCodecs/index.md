# WMFCodecs

> Adds codecs from the Windows Media Foundation to AVCodecs

| 属性 | 值 |
|---|---|
| 中文名 | 媒体基础编解码器 |
| 分类 | Codecs |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `WMFCodecs` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-01-25 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AVCodecs/WMFCodecs) | |

## 用途
WMFCodecs 是 UE5 音视频编解码框架 `AVCodecs` 的一个**实验性扩展插件**。它的核心功能是将 Windows 平台原生的 **Windows Media Foundation (WMF)** 编解码器能力集成到 `AVCodecs` 框架中。它主要解决在 Windows 平台上，通过 WMF 提供**硬件加速**或**系统原生**的音频（如 AAC）编码功能。开发者可以借助此插件，在不直接处理复杂的 COM 接口和 Windows API 的情况下，通过 `AVCodecs` 的统一接口使用 WMF 的编码能力。

## 使用场景
- 你正在为 Windows 平台开发需要**硬件加速音频编码**（如 AAC）的实时应用程序（例如视频会议、直播推流）。
- 你的项目已经使用了 `AVCodecs` 框架，希望利用 Windows 系统自带的编解码器，而无需引入第三方库。
- 你正在开发一个音视频处理管线，并希望对底层编解码器实现进行抽象，WMFCodecs 可以作为 `AVCodecs` 框架下的一个具体实现。

**重要提示**：此插件为实验性状态 (`IsExperimentalVersion: true`)，且默认禁用 (`EnabledByDefault: false`)，仅在 Windows x64 平台可用。使用前需要在项目设置中手动启用。

## 蓝图用法
根据提供的源码分析，此插件主要提供底层的 C++ 编解码器实现类 (`FAudioEncoderWMF`)，未发现可供蓝图直接调用的 `UFUNCTION(BlueprintCallable)` 或 `BlueprintReadWrite` 节点。其主要用途是供 C++ 代码在 `AVCodecs` 框架内调用。

## C++ 用法
### 头文件引入
使用此插件提供的编码器，需要引入相关头文件。
```cpp
// 主要的音频编码器类
#include "Audio/Encoders/AudioEncoderWMF.h"
// 编码器的配置结构体
#include "Audio/Encoders/Configs/AudioEncoderConfigWMF.h"
```

### 基本用法
此插件的核心类是 `FAudioEncoderWMF`，它继承自 `TAudioEncoder`，专门用于处理 CPU 上的音频资源 (`FAudioResourceCPU`)。以下是一个基本的使用流程示例，展示了如何实例化、配置并使用 WMF 音频编码器。

**文件来源**：基于 `Source/WMFCodecs/Public/Audio/Encoders/AudioEncoderWMF.h` 和 `Source/WMFCodecs/Public/Audio/Encoders/Configs/AudioEncoderConfigWMF.h` 中的定义。
```cpp
#include "Audio/Encoders/AudioEncoderWMF.h"
#include "Audio/Encoders/Configs/AudioEncoderConfigWMF.h"

void Example_UseWMFAudioEncoder()
{
    // 1. 创建编码器实例和配置对象
    TSharedRef<FAudioEncoderWMF> Encoder = MakeShared<FAudioEncoderWMF>();
    FAudioEncoderConfigWMF EncoderConfig;
    
    // （可选）根据需要配置 CodecType 等参数
    // EncoderConfig.CodecType = MFAudioFormat_AAC; // 示例：指定为 AAC 格式

    // 2. 打开编码器（需要提供 Device 和 Instance 上下文）
    TSharedRef<FAVDevice> Device = /* ... 获取或创建设备上下文 */;
    TSharedRef<FAVInstance> Instance = /* ... 获取或创建实例上下文 */;
    FAVResult OpenResult = Encoder->Open(Device, Instance);
    if (!OpenResult) 
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to open WMF Audio Encoder: %s"), *OpenResult.GetError());
        return;
    }

    // 3. 应用配置
    // Encoder->ApplyConfig(); // 通常配置在 Open 前后或通过专用函数应用

    // 4. 准备音频数据并编码
    // 假设你有一个 CPU 上的音频资源帧 AudioFrame
    TSharedPtr<FAudioResourceCPU> AudioFrame = /* ... */;
    uint32 Timestamp = /* ... */;
    FAVResult SendResult = Encoder->SendFrame(AudioFrame, Timestamp);
    if (!SendResult)
    {
        UE_LOG(LogTemp, Warning, TEXT("Failed to send audio frame to encoder."));
        return;
    }

    // 5. 接收编码后的数据包
    FAudioPacket EncodedPacket;
    FAVResult ReceiveResult = Encoder->ReceivePacket(EncodedPacket);
    if (ReceiveResult)
    {
        // 成功获取到编码后的音频包 EncodedPacket
        // ... 处理编码后的数据
    }

    // 6. 使用完毕后关闭编码器
    Encoder->Close();
}
```

### 进阶用法
更复杂的使用场景可能涉及自定义配置转换。头文件 `AudioEncoderConfigWMF.h` 中声明了一个 `TransformConfig` 模板特化函数，用于将通用的 AAC 配置 (`FAudioEncoderConfigAAC`) 转换为此插件特定的 `FAudioEncoderConfigWMF`。
```cpp
// 假设存在从通用配置转换的场景
FAudioEncoderConfigAAC GenericAACConfig;
GenericAACConfig.BitRate = 128000;

FAudioEncoderConfigWMF WMFConfig;
// 使用框架提供的转换函数
FAVResult TransformResult = FAVExtension::TransformConfig(WMFConfig, GenericAACConfig);
if (TransformResult)
{
    // WMFConfig 已根据 GenericAACConfig 被正确填充，现在可以用于编码器
}
```

## Demo 示例
一个完整的、可编译的最小音频编码示例。

**WMFDemoEncoder.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Audio/Encoders/AudioEncoderWMF.h"

class FWMFDemoEncoder
{
public:
    FWMFDemoEncoder();
    ~FWMFDemoEncoder();

    bool Initialize();
    void EncodeAudioData(const TArray<float>& PCMData, uint32 SampleRate, uint32 Channels);
    void Shutdown();

private:
    TSharedPtr<FAudioEncoderWMF> AudioEncoder;
    TSharedRef<FAVDevice> CreateDummyDevice() const;
    TSharedRef<FAVInstance> CreateDummyInstance() const;
};
```

**WMFDemoEncoder.cpp**
```cpp
#include "WMFDemoEncoder.h"
#include "Audio/Resources/AudioResourceCPU.h"

FWMFDemoEncoder::FWMFDemoEncoder()
    : AudioEncoder(MakeShared<FAudioEncoderWMF>())
{
}

FWMFDemoEncoder::~FWMFDemoEncoder()
{
    Shutdown();
}

bool FWMFDemoEncoder::Initialize()
{
    TSharedRef<FAVDevice> Device = CreateDummyDevice();
    TSharedRef<FAVInstance> Instance = CreateDummyInstance();
    return AudioEncoder->Open(Device, Instance);
}

void FWMFDemoEncoder::EncodeAudioData(const TArray<float>& PCMData, uint32 SampleRate, uint32 Channels)
{
    // 此示例仅为演示流程，实际需要构建完整的 FAudioResourceCPU
    // TSharedPtr<FAudioResourceCPU> Resource = ...;
    // AudioEncoder->SendFrame(Resource, 0);
    // FAudioPacket Packet;
    // AudioEncoder->ReceivePacket(Packet);
}

void FWMFDemoEncoder::Shutdown()
{
    if (AudioEncoder && AudioEncoder->IsOpen())
    {
        AudioEncoder->Close();
    }
}

// 以下为示意性函数，实际实现取决于你的应用上下文
TSharedRef<FAVDevice> FWMFDemoEncoder::CreateDummyDevice() const
{
    return MakeShared<FAVDevice>(TEXT("DummyWMFDevice"));
}

TSharedRef<FAVInstance> FWMFDemoEncoder::CreateDummyInstance() const
{
    return MakeShared<FAVInstance>(TEXT("DummyWMFInstance"));
}
```

## 模块依赖
此插件本身高度依赖 `AVCodecsCore` 提供的基础框架和接口。
| 模块 | 用途 |
|---|---|
| `AVCodecsCore` | 提供音频/视频编码器、资源、配置等基础抽象类和框架 |

## 维护状态
### 近期更新
| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-01-22 | `ad8a0de1` | Update BuildVersionSettings that are out of date | 更新过时的构建版本设置，属于项目配置维护 |
| 2025-03-13 | `6aff9a26` | Do not mark non-installed plugins as installed | 修正插件安装状态标记逻辑，影响插件管理 |
| 2024-05-28 | `15afa78d` | Add test to make sure the module name in the IMPLEMENT_MODULE macros matches the name declared in the .uplugin | 添加测试确保模块宏名称与.uplugin一致，增强模块健壮性 |
| 2023-01-25 | `32db50d3` | Disable AVCodecsCore for Apple platforms | 在 Apple 平台上禁用 AVCodecsCore，与本插件间接相关 |
| 2023-01-25 | `5c48dbd6` | Added new experimental plugin AVCodecs which handles software/hardware encoding and decoding of audio and video | 初始提交，包含本插件 |

### 维护评价
- **状态**：**维护不活跃**。
- **分析**：
    1.  **创建时间**：插件创建于 2023 年 1 月。
    2.  **更新频率**：最近一次功能性更新停留在 2024 年 5 月（模块名测试）。2025 和 2026 年的提交均为通用的构建或插件管理系统维护，未涉及 WMFCodecs 或 AVCodecs 的核心功能更新。
    3.  **实验性状态**：插件始终标记为实验性 (`IsExperimentalVersion: true`) 且默认禁用，表明 Epic 官方可能尚未将其视为稳定或最终确定的解决方案。
    4.  **平台限制**：仅支持 Win64，限制了其应用范围。
- **建议**：由于缺乏持续的功能更新和维护，且处于实验状态，**不建议在生产环境中深度依赖此插件**。它更适合作为学习 `AVCodecs` 框架或进行 Windows 平台特定编解码器研究的参考。在生产项目中，应评估其稳定性和长期维护计划。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AVCodecs/WMFCodecs)
- 测试用例：当前提供的源码信息中未包含明确的测试文件路径。相关的测试可能存在于 `AVCodecsCore` 或上层的测试框架中。