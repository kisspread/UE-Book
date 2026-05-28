# Electra Player Subtitle Module

> Subtitle Decoder Module for Electra Player Media Playback

| 属性 | 值 |
|---|---|
| 中文名 | Electra字幕解码器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ElectraSubtitles` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-07-27 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraSubtitles) | |

## 用途

ElectraSubtitles 是 ElectraPlayer 媒体播放器的字幕解码模块。它通过模块化特性（Modular Feature）机制为 ElectraPlayer 提供多格式字幕解析能力，支持以下字幕格式：

- **WebVTT**（Web Video Text Tracks）：W3C 标准的网页字幕格式，广泛用于 HLS 流媒体
- **TX3G**（3GPP Timed Text）：用于 MP4 容器中的字幕，定义在 ETSI TS 126.245 中
- **TTML/IMSC1**（Timed Text Markup Language）：W3C 标准的 XML 字幕格式，支持 STPP（ISO/IEC 14496-30）和外挂 XML 文档两种模式

该插件的设计采用优先级竞争机制：当多个插件支持同一格式时，优先级最高的解码器会被选用。这允许第三方插件覆盖默认实现。

## 使用场景

- 你使用 ElectraPlayer 播放 HLS/DASH 流媒体，需要显示 WebVTT 或 TTML 字幕
- 你播放包含内嵌 TX3G 字幕的 MP4 文件
- 你需要外挂（sideload）TTML/XML 字幕文件
- 你需要自定义字幕解码器来替换默认实现（通过优先级机制）

## 蓝图用法

该插件没有暴露任何 BlueprintCallable 节点。字幕处理完全在底层通过 C++ 委托机制完成，最终通过 ElectraPlayer 内部管线传递。

## C++ 用法

### 头文件引入

```cpp
#include "IElectraSubtitleModule.h"
#include "IElectraSubtitleDecoder.h"
```

### 基本用法 — 查询支持的字幕格式

通过 Modular Feature 机制获取字幕模块，查询支持的格式：

```cpp
// 来源: IElectraSubtitleModule.h
#include "IElectraSubtitleModule.h"
#include "Features/IModularFeatures.h"

// 获取所有注册的字幕模块特性
TArray<IModularFeature*> Features = IModularFeatures::Get().GetModularFeatureImplementations(
    IElectraSubtitlesModule::GetModularFeatureName());

for (IModularFeature* Feature : Features)
{
    if (IElectraSubtitleModularFeature* SubtitleFeature = static_cast<IElectraSubtitleModularFeature*>(Feature))
    {
        // 查询支持的格式列表
        TArray<FString> SupportedFormats;
        SubtitleFeature->GetSupportedFormats(SupportedFormats);
        
        // 检查是否支持特定格式
        if (SubtitleFeature->SupportsFormat(TEXT("wvtt")))
        {
            // 创建该格式的解码器
            TSharedPtr<IElectraSubtitleDecoder> Decoder = 
                SubtitleFeature->CreateDecoderForFormat(TEXT("wvtt"));
        }
    }
}
```

### 基本用法 — 接收字幕数据

```cpp
// 来源: IElectraSubtitleDecoder.h
// 订阅字幕解析完成的委托
Decoder->GetParsedSubtitleReceiveDelegate().AddLambda(
    [](ISubtitleDecoderOutputPtr DecodedSubtitle)
    {
        // 处理解码后的字幕
    });

// 初始化解码器（传入 codec specific data）
TArray<uint8> CSD; // 从媒体流中获取
Electra::FParamDict AdditionalInfo;
Decoder->InitializeStreamWithCSD(CSD, AdditionalInfo);

// 启动解码器
Decoder->Start();
```

### 进阶用法 — 流式字幕数据处理

```cpp
// 来源: IElectraSubtitleDecoder.h
// 添加流式字幕数据
Decoder->AddStreamedSubtitleData(InData, InAbsoluteTimestamp, InDuration, AdditionalInfo);

// 更新播放位置以触发字幕显示
Decoder->UpdatePlaybackPosition(AbsolutePosition, LocalPosition);

// 获取提前投递的时间偏移量
Electra::FTimeValue DeliveryOffset = Decoder->GetStreamedDeliveryTimeOffset();

// 信号字幕流结束
Decoder->SignalStreamedSubtitleEOD();

// Flush 所有输入输出
Decoder->Flush();

// 停止解码器
Decoder->Stop();
```

## Demo 示例

一个自定义字幕解码器注册示例：

```cpp
// MySubtitleModule.h
#pragma once

#include "IElectraSubtitleModule.h"
#include "IElectraSubtitleDecoder.h"

class FMySubtitleModule : public IElectraSubtitleModularFeature
{
public:
    virtual ~FMySubtitleModule() = default;

    // IElectraSubtitleModularFeature 接口
    virtual bool SupportsFormat(const FString& SubtitleCodecName) const override
    {
        return SubtitleCodecName == TEXT("wvtt");
    }

    virtual void GetSupportedFormats(TArray<FString>& OutSupportedCodecNames) const override
    {
        OutSupportedCodecNames.Add(TEXT("wvtt"));
    }

    virtual int32 GetPriorityForFormat(const FString& SubtitleCodecName) const override
    {
        // 返回比默认实现更高的优先级以覆盖默认行为
        return 100;
    }

    virtual TSharedPtr<IElectraSubtitleDecoder, ESPMode::ThreadSafe> CreateDecoderForFormat(
        const FString& SubtitleCodecName) override
    {
        // 返回自定义解码器实例
        return nullptr; // 替换为实际实现
    }
};
```

```cpp
// MySubtitleModule.cpp
#include "MySubtitleModule.h"
#include "Features/IModularFeatures.h"

void FMySubtitleModule::StartupModule()
{
    IModularFeatures::Get().RegisterModularFeature(
        IElectraSubtitlesModule::GetModularFeatureName(), this);
}

void FMySubtitleModule::ShutdownModule()
{
    IModularFeatures::Get().UnregisterModularFeature(
        IElectraSubtitlesModule::GetModularFeatureName(), this);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ElectraUtil` | Electra 播放器公共工具库，提供时间值、参数字典等基础类型 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到新 API |
| 2026-01-12 | `58f81ed8` | [ElectraSubtitles] Include CoreMinimal.h from TTMLSubtitleHandler.h because UE Tests is having compi | 修复测试编译缺少头文件引用问题 |
| 2025-10-01 | `bea2a432` | ElectraSubtitles: Fixed an incorrectly released mutex | 修复互斥锁错误释放的线程安全问题 |
| 2025-04-08 | `275a8bf9` | ElectraPlayer: Fixing TTML subtitle timing in DASH period having a presentationTimeOffset; fixed ind | 修复 DASH 流中 TTML 字幕时间偏移计算 |
| 2025-04-04 | `cf834c18` | ElectraSubtitles: Fix for overlapping WebVTT subtitles | 修复 WebVTT 字幕重叠显示问题 |

### 维护评价

该插件创建于 2021 年 7 月，约 5 年历史。最近的更新集中在 2025-2026 年，包括日志 API 迁移、编译修复、线程安全修复和字幕时间计算修正，表明仍在**积极维护**中。作为 ElectraPlayer 的核心字幕模块，它随 ElectraPlayer 一起被维护。不过该插件默认未启用（`EnabledByDefault=false`），说明它需要用户主动启用才能使用。推荐在使用 ElectraPlayer 播放包含字幕的媒体内容时启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraSubtitles)
- [官方文档](https://docs.unrealengine.com/en-US/Engine/MediaFramework/Overview)