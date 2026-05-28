# Electra Codecs

> Codecs for use with Electra player.

| 属性 | 值 |
|---|---|
| 中文名 | Electra 解码器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ElectraCodecFactory` (Runtime), `ElectraDecoders` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2023-04-03 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraCodecs) | |

## 用途

ElectraCodecs 是 UE5 Electra 媒体播放器的底层解码器集合。它提供了一套统一的解码器接口（`IElectraDecoder`），并在各平台上实现了具体解码器：

- **视频解码器**：H.264 (AVC)、H.265 (HEVC)、VP8/VP9、AV1
- **音频解码器**：AAC

与传统的 UE 媒体框架不同，ElectraCodecs 采用了**每帧管线式**的解码模型：通过 `DecodeAccessUnit()` → `HaveOutput()` → `GetOutput()` 循环逐帧处理，并支持自适应流切换（分辨率/码率变化无需销毁重建解码器）。

该插件默认**未启用**，需要在项目中手动启用后才能被 Electra 播放器使用。它不包含任何资产内容，是纯代码模块。

## 使用场景

- 你在使用 Electra 媒体播放器播放流媒体或本地视频文件 → 需要启用此插件提供解码能力
- 你需要在 Android 上利用硬件 MediaCodec 解码 H.265/H.264 视频 → 此插件封装了 JNI 接口调用
- 你需要在 Windows 上使用 DirectX/DXGI + Media Foundation 进行硬件视频解码 → 此插件封装了 MF Transform 接口
- 你需要解码带 HDR 元数据（Mastering Display、Content Light Level）的视频流 → 此插件的 SEI 解析器可提取这些信息
- 你需要在自适应流媒体场景中无缝切换码率/分辨率 → 此插件的解码器支持 CSD 兼容性检测与动态切换

## 蓝图用法

该插件不暴露 `BlueprintCallable` 函数。它是纯 C++ 运行时模块，通过 Electra 播放器内部管线自动调用。普通蓝图用户无需直接接触此插件的 API。

## C++ 用法

### 头文件引入

```cpp
// 解码器核心接口
#include "IElectraDecoder.h"

// 解码器特性和选项常量
#include "IElectraDecoderFeaturesAndOptions.h"

// 视频输出接口
#include "IElectraDecoderOutputVideo.h"

// 音频输出接口
#include "IElectraDecoderOutputAudio.h"

// 解码器模块注册接口
#include "IElectraDecodersModule.h"

// 工具函数
#include "ElectraDecodersUtils.h"
```

### 基本用法：解码循环

以下展示了一个典型的解码器使用流程（源自 `IElectraDecoder` 接口设计）：

```cpp
#include "IElectraDecoder.h"
#include "IElectraDecoderOutputVideo.h"

void DecodeLoop(TSharedPtr<IElectraDecoder, ESPMode::ThreadSafe> InDecoder, const TArray<FElectraDecoderInputAccessUnit>& InAccessUnits)
{
    // 1. 验证解码器类型
    if (InDecoder->GetType() != IElectraDecoder::EType::Video)
    {
        return; // 类型不匹配
    }

    // 2. 逐帧送入数据
    for (const auto& AU : InAccessUnits)
    {
        IElectraDecoder::EDecoderError DecodeResult = InDecoder->DecodeAccessUnit(AU, {}/*additionalOptions*/);

        switch (DecodeResult)
        {
        case IElectraDecoder::EDecoderError::None:
            // 数据已接受，检查是否有输出
            break;
        case IElectraDecoder::EDecoderError::NoBuffer:
            // 输出缓冲区已满，先取出已有输出
            break;
        case IElectraDecoder::EDecoderError::Error:
            // 解码错误，获取错误信息并销毁解码器
            IElectraDecoder::FError Error = InDecoder->GetError();
            UE_LOG(LogElectraDecoders, Error, TEXT("Decode error: %s"), *Error.GetMessage());
            InDecoder->Close();
            return;
        default:
            break;
        }

        // 3. 取出可用的解码输出
        while (true)
        {
            IElectraDecoder::EOutputStatus Status = InDecoder->HaveOutput();

            if (Status == IElectraDecoder::EOutputStatus::Available)
            {
                TSharedPtr<IElectraDecoderOutput, ESPMode::ThreadSafe> Output = InDecoder->GetOutput();
                if (Output && Output->GetType() == IElectraDecoderOutput::EType::Video)
                {
                    TSharedPtr<IElectraDecoderVideoOutput, ESPMode::ThreadSafe> VideoOutput =
                        StaticCastSharedPtr<IElectraDecoderVideoOutput>(Output);

                    // 获取视频参数
                    int32 Width = VideoOutput->GetWidth();
                    int32 Height = VideoOutput->GetHeight();
                    FTimespan PTS = VideoOutput->GetPTS();

                    UE_LOG(LogElectraDecoders, Log, TEXT("Decoded frame: %dx%d, PTS=%lld"),
                        Width, Height, PTS.GetTicks());
                }
            }
            else if (Status == IElectraDecoder::EOutputStatus::NeedInput)
            {
                break; // 需要更多输入
            }
            else if (Status == IElectraDecoder::EOutputStatus::EndOfData)
            {
                break; // 所有输出已返回
            }
            else
            {
                break; // TryAgainLater 或 Error
            }
        }
    }

    // 4. 结束时关闭解码器
    InDecoder->Close();
}
```

### 进阶用法：检查解码器特性与自适应流处理

```cpp
#include "IElectraDecoder.h"
#include "IElectraDecoderFeaturesAndOptions.h"

// 检查解码器支持的特性
void QueryDecoderFeatures(TSharedPtr<IElectraDecoder, ESPMode::ThreadSafe> InDecoder)
{
    TMap<FString, FVariant> Features;
    InDecoder->GetFeatures(Features);

    // 检查是否支持自适应解码（分辨率/码率变化时不需重建）
    const FVariant* IsAdaptive = Features.Find(IElectraDecoderFeature::IsAdaptive);
    if (IsAdaptive && IsAdaptive->GetValue<bool>())
    {
        UE_LOG(LogElectraDecoders, Log, TEXT("Decoder supports adaptive decoding"));
    }

    // 检查是否支持丢弃输出帧（非参考帧优化）
    const FVariant* SupportsDropping = Features.Find(IElectraDecoderFeature::SupportsDroppingOutput);
    if (SupportsDropping && SupportsDropping->GetValue<bool>())
    {
        UE_LOG(LogElectraDecoders, Log, TEXT("Decoder supports dropping output frames"));
    }

    // 检查最小输出帧缓冲数量
    const FVariant* MinFrames = Features.Find(IElectraDecoderFeature::MinimumNumberOfOutputFrames);
    if (MinFrames)
    {
        int32 MinNum = MinFrames->GetValue<int32>();
        UE_LOG(LogElectraDecoders, Log, TEXT("Minimum output frames: %d"), MinNum);
    }
}

// 处理 CSD（Codec Specific Data）变化时的自适应切换
void HandleCSDChange(TSharedPtr<IElectraDecoder, ESPMode::ThreadSafe> InDecoder,
                     const TMap<FString, FVariant>& InNewCSDAndOptions)
{
    IElectraDecoder::ECSDCompatibility Compat = InDecoder->IsCompatibleWith(InNewCSDAndOptions);

    switch (Compat)
    {
    case IElectraDecoder::ECSDCompatibility::Compatible:
        // 可以直接继续解码，无需任何操作
        UE_LOG(LogElectraDecoders, Log, TEXT("CSD compatible, continuing"));
        break;

    case IElectraDecoder::ECSDCompatibility::Drain:
        // 需要先排空解码器缓冲，然后继续
        InDecoder->SendEndOfData();
        while (InDecoder->HaveOutput() == IElectraDecoder::EOutputStatus::Available)
        {
            InDecoder->GetOutput(); // 消费所有剩余输出
        }
        UE_LOG(LogElectraDecoders, Log, TEXT("CSD changed, decoder drained"));
        break;

    case IElectraDecoder::ECSDCompatibility::DrainAndReset:
        // 需要排空后重置解码器
        InDecoder->SendEndOfData();
        while (InDecoder->HaveOutput() == IElectraDecoder::EOutputStatus::Available)
        {
            InDecoder->GetOutput();
        }
        if (!InDecoder->ResetToCleanStart())
        {
            // 重置失败，需要重建解码器
            UE_LOG(LogElectraDecoders, Warning, TEXT("Reset failed, decoder must be recreated"));
        }
        break;
    }
}
```

### 进阶用法：位流处理器（Bitstream Processor）

```cpp
#include "IElectraDecoder.h"

void UseBitstreamProcessor(TSharedPtr<IElectraDecoder, ESPMode::ThreadSafe> InDecoder)
{
    // 创建位流预处理器（可选，用于提取 SEI 消息等 sideband 信息）
    TSharedPtr<IElectraDecoderBitstreamProcessor, ESPMode::ThreadSafe> BSP = InDecoder->CreateBitstreamProcessor();

    if (BSP.IsValid())
    {
        FElectraDecoderInputAccessUnit AU;
        // ... 填充 AU 数据 ...

        TSharedPtr<IElectraDecoderBitstreamInfo, ESPMode::ThreadSafe> BSI;
        auto ProcessResult = BSP->ProcessInputForDecoding(BSI, AU, {}/*sidebandData*/);

        if (ProcessResult == IElectraDecoderBitstreamProcessor::EProcessResult::Ok ||
            ProcessResult == IElectraDecoderBitstreamProcessor::EProcessResult::CSDChanged)
        {
            // AU 已处理，可以送入解码器
            InDecoder->DecodeAccessUnit(AU, {});

            // 将 sideband 属性传递给输出
            TMap<FString, FVariant> OutputProps;
            BSP->SetPropertiesOnOutput(OutputProps, BSI);
        }
    }
}
```

### 进阶用法：读取 AV1 Codec Configuration

```cpp
#include "Utils/AOMedia/ElectraUtilsAV1Video.h"

void ParseAV1CodecConfig(const TArray<uint8>& InDCRData)
{
    ElectraDecodersUtil::AV1Video::FAV1CodecConfigurationRecord AV1Config;
    if (AV1Config.Parse(InDCRData))
    {
        uint8 Profile = AV1Config.GetProfile();
        uint8 Level = AV1Config.GetLevel();
        uint8 BitDepth = AV1Config.GetBitDepth();

        // 获取 RFC 6381 格式的 codec 字符串（用于 MP4 容器）
        FString RFC6381 = AV1Config.GetCodecSpecifierRFC6381();
        UE_LOG(LogElectraDecoders, Log, TEXT("AV1 codec: %s"), *RFC6381);
        // 示例输出: "av01.0.04M.08.0.112.09.16.09.0"
    }
}
```

### 进阶用法：MPEG SEI 消息解析（HDR 元数据）

```cpp
#include "Utils/MPEG/ElectraUtilsMPEGVideo.h"
#include "Utils/VideoDecoderHelpers.h"

void ExtractHDRMetadata(const void* InBitstream, uint64 InBitstreamLength)
{
    using namespace ElectraDecodersUtil::MPEG;

    // 从 H.265 码流中提取 SEI 消息
    TArray<FSEIMessage> SEIMessages;
    ExtractSEIMessages(SEIMessages, InBitstream, InBitstreamLength, ESEIStreamType::H265, true);

    for (const auto& SEI : SEIMessages)
    {
        if (SEI.PayloadType == FSEIMessage::PT_mastering_display_colour_volume)
        {
            FSEImastering_display_colour_volume MDCV;
            if (ParseFromSEIMessage(MDCV, SEI))
            {
                UE_LOG(LogElectraDecoders, Log,
                    TEXT("Max Luminance: %u, Min Luminance: %u"),
                    MDCV.max_display_mastering_luminance,
                    MDCV.min_display_mastering_luminance);
            }
        }
        else if (SEI.PayloadType == FSEIMessage::PT_content_light_level_info)
        {
            FSEIcontent_light_level_info CLLI;
            if (ParseFromSEIMessage(CLLI, SEI))
            {
                UE_LOG(LogElectraDecoders, Log,
                    TEXT("Max Content Light Level: %u, Max Pic Average: %u"),
                    CLLI.max_content_light_level,
                    CLLI.max_pic_average_light_level);
            }
        }
    }

    // 使用 HDR Helper 整合所有 HDR 信息
    Electra::MPEG::FHDRHelper HDRHelper;
    Electra::MPEG::FColorimetryHelper ColorHelper;
    ColorHelper.Update(9/*BT2020*/, 16/*PQ*/, 9/*BT2020_NCL*/, 0, 5);
    HDRHelper.Update(10/*bit depth*/, ColorHelper, SEIMessages, {}, true);
}
```

## Demo 示例

以下是一个完整的解码器自定义实现骨架，展示如何实现 `IElectraDecoder` 接口：

```cpp
// MyCustomVideoDecoder.h
#pragma once

#include "IElectraDecoder.h"

class FMyCustomVideoDecoder : public IElectraDecoder
{
public:
    FMyCustomVideoDecoder(const Electra::FCodecTypeFormat& InCodecFormat, const TMap<FString, FVariant>& InOptions);
    virtual ~FMyCustomVideoDecoder();

    static TSharedPtr<IElectraDecoder, ESPMode::ThreadSafe> Create(
        const Electra::FCodecTypeFormat& InCodecFormat,
        const TMap<FString, FVariant>& InAdditionalOptions);

    // IElectraDecoder interface
    virtual EType GetType() const override { return EType::Video; }
    virtual void GetFeatures(TMap<FString, FVariant>& OutFeatures) const override;
    virtual FError GetError() const override;
    virtual void Close() override;

    virtual ECSDCompatibility IsCompatibleWith(const TMap<FString, FVariant>& CSDAndAdditionalOptions) override;
    virtual bool ResetToCleanStart() override;

    virtual EDecoderError DecodeAccessUnit(const FInputAccessUnit& InInputAccessUnit,
                                           const TMap<FString, FVariant>& InAdditionalOptions) override;
    virtual EDecoderError SendEndOfData() override;
    virtual EDecoderError Flush() override;

    virtual EOutputStatus HaveOutput() override;
    virtual TSharedPtr<IElectraDecoderOutput, ESPMode::ThreadSafe> GetOutput() override;

    virtual TSharedPtr<IElectraDecoderBitstreamProcessor, ESPMode::ThreadSafe> CreateBitstreamProcessor() override;

    virtual void Suspend() override;
    virtual void Resume() override;

private:
    FError LastError;
    bool bClosed = false;
    bool bEndOfDataSent = false;
    TArray<TSharedPtr<IElectraDecoderOutput, ESPMode::ThreadSafe>> PendingOutputs;
};

// MyCustomVideoDecoder.cpp
#include "MyCustomVideoDecoder.h"
#include "IElectraDecoderFeaturesAndOptions.h"

FMyCustomVideoDecoder::FMyCustomVideoDecoder(
    const Electra::FCodecTypeFormat& InCodecFormat,
    const TMap<FString, FVariant>& InOptions)
{
    // 初始化平台解码器资源
}

FMyCustomVideoDecoder::~FMyCustomVideoDecoder()
{
    Close();
}

TSharedPtr<IElectraDecoder, ESPMode::ThreadSafe> FMyCustomVideoDecoder::Create(
    const Electra::FCodecTypeFormat& InCodecFormat,
    const TMap<FString, FVariant>& InAdditionalOptions)
{
    return MakeShared<FMyCustomVideoDecoder>(InCodecFormat, InAdditionalOptions);
}

void FMyCustomVideoDecoder::GetFeatures(TMap<FString, FVariant>& OutFeatures) const
{
    OutFeatures.Add(IElectraDecoderFeature::IsAdaptive, FVariant(true));
    OutFeatures.Add(IElectraDecoderFeature::SupportsDroppingOutput, FVariant(false));
    OutFeatures.Add(IElectraDecoderFeature::MinimumNumberOfOutputFrames, FVariant(4));
}

IElectraDecoder::FError FMyCustomVideoDecoder::GetError() const
{
    return LastError;
}

void FMyCustomVideoDecoder::Close()
{
    if (!bClosed)
    {
        bClosed = true;
        // 释放平台解码器资源
        PendingOutputs.Empty();
    }
}

IElectraDecoder::ECSDCompatibility FMyCustomVideoDecoder::IsCompatibleWith(
    const TMap<FString, FVariant>& CSDAndAdditionalOptions)
{
    // 检查新的 codec specific data 是否与当前配置兼容
    return ECSDCompatibility::Compatible;
}

bool FMyCustomVideoDecoder::ResetToCleanStart()
{
    bEndOfDataSent = false;
    PendingOutputs.Empty();
    return true;
}

IElectraDecoder::EDecoderError FMyCustomVideoDecoder::DecodeAccessUnit(
    const FInputAccessUnit& InInputAccessUnit,
    const TMap<FString, FVariant>& InAdditionalOptions)
{
    if (bClosed) return EDecoderError::Error;
    // 将数据送入平台解码器并处理...
    return EDecoderError::None;
}

IElectraDecoder::EDecoderError FMyCustomVideoDecoder::SendEndOfData()
{
    if (bEndOfDataSent) return EDecoderError::EndOfData;
    bEndOfDataSent = true;
    return EDecoderError::None;
}

IElectraDecoder::EDecoderError FMyCustomVideoDecoder::Flush()
{
    PendingOutputs.Empty();
    bEndOfDataSent = false;
    return EDecoderError::None;
}

IElectraDecoder::EOutputStatus FMyCustomVideoDecoder::HaveOutput()
{
    if (PendingOutputs.Num() > 0) return EOutputStatus::Available;
    if (bEndOfDataSent) return EOutputStatus::EndOfData;
    return EOutputStatus::NeedInput;
}

TSharedPtr<IElectraDecoderOutput, ESPMode::ThreadSafe> FMyCustomVideoDecoder::GetOutput()
{
    if (PendingOutputs.Num() > 0)
    {
        return PendingOutputs.Pop();
    }
    return nullptr;
}

TSharedPtr<IElectraDecoderBitstreamProcessor, ESPMode::ThreadSafe> FMyCustomVideoDecoder::CreateBitstreamProcessor()
{
    return nullptr; // 可选实现
}

void FMyCustomVideoDecoder::Suspend()
{
    // 暂停解码器（应用进入后台时）
}

void FMyCustomVideoDecoder::Resume()
{
    // 恢复解码器
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `SignalProcessing` | 音频信号处理（用于 AAC 解码器的音频格式转换） |
| `DirectX` | Windows 平台 DirectX 硬件解码支持（D3D11/D3D12 + Media Foundation） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `e86f17b3` | Use ConvertToTimescale for overflow-safe milliFPS computation | 使用 ConvertToTimescale 实现溢出安全的毫秒帧率计算 |
| 2026-05-13 | `4754a81b` | Fix Invalid Frame Rate for Android HEVC ingest without Third Party Encoder | 修复 Android HEVC 无第三方编码器时帧率错误的问题 |
| 2026-05-12 | `3bbffee9` | ElectraCodecs: Fixed HEVC DCR array extraction. Should not append to a single array but retain individual | 修复 HEVC DCR 数组提取逻辑，不再合并到单个数组 |
| 2026-04-27 | `53a5ec2a` | ElectraCodecs: Permitting short form codec RFC for VP8 and VP9 codec | 允许 VP8 和 VP9 使用简短格式的 RFC codec 标识符 |
| 2026-04-23 | `0cd64869` | ElectraDecoders: Fixed an issue where mp4a audio is wrapped inside a wave box in a QuickTime file | 修复 mp4a 音频在 QuickTime 文件中被 wave box 包装的问题 |

### 维护评价

- **活跃维护**：该插件持续获得功能更新和 Bug 修复，最近一次提交在 2026-05-13
- 更新频率稳定，涵盖平台兼容性修复、HDR 处理改进、编解码格式支持完善
- 作为 Electra 播放器的核心组件，与 Epic 的媒体基础设施深度绑定，长期维护有保障
- 默认未启用（`EnabledByDefault=false`），属于可选组件
- **推荐使用**：如果你的项目使用 Electra 媒体播放器播放视频/音频内容，此插件是必需的解码器后端

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraCodecs)
- [官方文档](https://docs.unrealengine.com/en-US/Engine/MediaFramework/Overview)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraCodecs/Source/ElectraDecoders/Tests)