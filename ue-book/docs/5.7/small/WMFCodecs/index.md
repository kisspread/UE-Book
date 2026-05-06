# WMFCodecs

> Adds codecs from the Windows Media Foundation to AVCodecs

| 属性 | 值 |
|---|---|
| 中文名 | WMF 编解码器 |
| 分类 | Codecs |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `WMFCodecs` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-01-25 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/AVCodecs/WMFCodecs) | |

## 用途

WMFCodecs 是 AVCodecs 框架的一个后端实现，利用 Windows 内置的 Media Foundation 架构提供音频/视频编解码能力。目前公开的 API 包含一个音频编码器 `FAudioEncoderWMF`，用于将音频数据编码为 AAC 等标准格式。

该插件解决了在 Windows 平台上使用操作系统原生编解码硬件加速的问题，无需额外安装第三方编解码库，同时通过 AVCodecs 抽象层保持引擎一致的使用体验。

## 使用场景

- **实时音频编码**：在 Windows 客户端录制音频并编码为 AAC 流，用于网络传输或本地存储。
- **视频转码/推流**：配合其他 WMF 视频编码器（如 H.264/H.265）实现硬件加速编码（本插件也包含视频编解码器，但本文档仅覆盖音频部分）。
- **与 AVCodecs 管道集成**：在音频/视频处理管线中统一使用 AVCodecs 接口，通过切换后端实现跨平台兼容。

## 蓝图用法

本插件为底层编解码实现，不直接暴露蓝图可调用节点。所有 API 均通过 C++ 调用。

## C++ 用法

### 头文件引入

```cpp
#include "Audio/Encoders/AudioEncoderWMF.h"
#include "Audio/Encoders/Configs/AudioEncoderConfigWMF.h"
```

### 基本用法

以下示例演示使用 FAudioEncoderWMF 编码一段 PCM 音频为 AAC 数据。

```cpp
// 来源：Engine/Plugins/Experimental/AVCodecs/WMFCodecs/Source/WMFCodecs/Public/Audio/Encoders/AudioEncoderWMF.h

// 创建编码器实例
TSharedRef<FAudioEncoderWMF> Encoder = MakeShared<FAudioEncoderWMF>();

// 获取默认 AVDevice（选择系统首选设备）
TSharedRef<FAVDevice> Device = FAVDevice::GetDefault();

// 创建实例配置
TSharedRef<FAVInstance> Instance = MakeShared<FAVInstance>();

// 打开编码器并设置 AAC 编码配置
FAudioEncoderConfigWMF Config(EAVPreset::Default);
Config.CodecType = MFAudioFormat_AAC; // 需要 #include 相应的 WMF GUID

FAVResult Result = Encoder->Open(Device, Instance);
if (Result.IsSuccess())
{
    Encoder->SetConfig(Config);
    Encoder->ApplyConfig();
}

// 准备 PCM 资源（假设已填充 16 位单声道数据）
TSharedPtr<FAudioResourceCPU> Resource = MakeShared<FAudioResourceCPU>();
// 填充 Resource 数据...

// 发送帧进行编码
Encoder->SendFrame(Resource, 0);

// 接收编码后的数据包
FAudioPacket Packet;
while (Encoder->ReceivePacket(Packet) == EAVResult::Success)
{
    // 处理编码数据（Packet.Data, Packet.Timestamp 等）
}
```

### 进阶用法

结合 AVCodecsCore 的音频配置，可自定义采样率、比特率等参数。

```cpp
// 设置 AAC 编码配置
FAudioEncoderConfigAAC AACConfig;
AACConfig.BitRate = 128000;  // 128 kbps
AACConfig.SampleRate = 44100;
AACConfig.NumChannels = 2;

// 通过扩展转换到 WMF 配置
FAudioEncoderConfigWMF WMFConfig;
FAVExtension::TransformConfig(WMFConfig, AACConfig);

Encoder->SetConfig(WMFConfig);
Encoder->ApplyConfig();
```

## Demo 示例

一个完整的可编译最小示例（控制台应用或 GameInstance），展示音频编码流程。

```cpp
// WMFCodecsDemo.h
#pragma once

#include "CoreMinimal.h"
#include "Audio/Encoders/AudioEncoderWMF.h"
#include "Audio/Encoders/Configs/AudioEncoderConfigWMF.h"

class FWMFCodecsDemo
{
public:
    void Run();
};

// WMFCodecsDemo.cpp
#include "WMFCodecsDemo.h"
#include "HAL/PlatformProcess.h"

void FWMFCodecsDemo::Run()
{
    // 创建编码器
    TSharedRef<FAudioEncoderWMF> Encoder = MakeShared<FAudioEncoderWMF>();
    TSharedRef<FAVDevice> Device = FAVDevice::GetDefault();
    TSharedRef<FAVInstance> Instance = MakeShared<FAVInstance>();

    // 打开并配置 AAC 编码
    FAudioEncoderConfigWMF Config(EAVPreset::Default);
    Config.CodecType = MFAudioFormat_AAC;
    
    if (Encoder->Open(Device, Instance).IsSuccess())
    {
        Encoder->SetConfig(Config);
        Encoder->ApplyConfig();

        // 模拟发送一帧静音 PCM 数据（10ms 16位单声道）
        const int32 SamplesPerFrame = 441; // 44100Hz * 0.01s
        TArray<uint8> PCMData;
        PCMData.SetNumZeroed(SamplesPerFrame * sizeof(int16));
        
        TSharedPtr<FAudioResourceCPU> Resource = MakeShared<FAudioResourceCPU>();
        Resource->Data = PCMData;
        
        Encoder->SendFrame(Resource, 0);

        // 读取编码输出
        FAudioPacket Packet;
        while (Encoder->ReceivePacket(Packet) == EAVResult::Success)
        {
            UE_LOG(LogTemp, Log, TEXT("Encoded packet size: %d bytes"), Packet.Data.Num());
        }
    }

    Encoder->Close();
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AVCodecsCore` | 提供基础编解码框架、设备管理、配置结构体及编解码接口 |

## 维护状态

### 近期更新

- 2025-03-13 `6aff9a26` Do not mark non-installed plugins as installed（非功能更新，仅安装流程修复）
- 2024-05-28 `15afa78d` Add test to make sure the module name in the IMPLEMENT_MODULE macros matches the name declared in the uplugin（编译检查改进）
- 2023-01-25 `32db50d3` Disable AVCodecsCore for Apple platforms（平台限制更新）
- 2023-01-25 `5c48dbd6` Added new experimental plugin AVCodecs which handles software/hardware encoding and decoding of audio（原始提交，创建插件）

### 维护评价

- **创建时间**：2023-01-25（约 2 年）
- **最近功能更新**：创建提交后无实质性功能增删，近两年仅有编译兼容性和安装流程维护
- **活跃度**：功能开发停滞，实验性状态未改变
- **风险**：依赖的 WMF API 在 Windows 上稳定，但可能缺少新功能（如视频编解码器文档缺失、未暴露完整配置）
- **推荐度**：如果仅需 Windows 平台上的 AAC 音频编码，可谨慎使用；视频编解码能力未知，生产环境需自行评估

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/AVCodecs/WMFCodecs)
- [AVCodecsCore 文档](https://docs.unrealengine.com/5.3/en-US/avcodecs-in-unreal-engine/)（官方文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/AVCodecs/WMFCodecs/Source/WMFCodecs/Private/Tests)（如果存在）