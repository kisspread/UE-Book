# Electra Player Subtitle Module

> Subtitle Decoder Module for Electra Player Media Playback

| 属性 | 值 |
|---|---|
| 中文名 | 字幕解码模块 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ElectraSubtitles` (RuntimeNoCommandlet) |
| 实验性 | 否 |
| 创建时间 | 2025-03-19 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/ElectraSubtitles) | |

## 用途

ElectraSubtitles 是 Electra Player 多格式媒体播放器框架的 **字幕解码模块**，负责解析和输出各类字幕轨道数据。它通过可扩展的编解码器注册机制，将原始字幕数据（如 WebVTT、TTML/IMSC1、TX3G）转换为统一的 `ISubtitleDecoderOutput` 对象，供上层渲染系统使用。该模块作为 Electra 播放管道中的**可选后端**，由播放器根据媒体流格式自动加载，开发者无需直接操作。

## 使用场景

- 你正在使用 **Electra Player** 播放 HLS/MSS/DASH 流媒体，并且媒体流中包含字幕轨道 → ElectraSubtitles 将自动启用，无需额外配置。
- 你需要为 Electra Player **添加自定义字幕格式支持** → 通过 `IElectraSubtitleModularFeature` 接口注册自己的解码器实现。
- 你只在 **Win64/Mac/IOS/TVOS/Android/Linux** 平台上打包应用程序（服务端不提供字幕解码）。

## 蓝图用法

本插件为底层模块，**不暴露任何蓝图可调用节点**。字幕解析和渲染由 Electra Player 自动管理，不需要在蓝图中手动调用。如果你需要在蓝图中控制字幕的显示/隐藏，请使用 `MediaPlayer` 相关的蓝图节点（如 `SetSubtitlesEnabled`）。

## C++ 用法

### 头文件引入

```cpp
#include "IElectraSubtitleModule.h"
#include "IElectraSubtitleDecoder.h"
#include "ElectraSubtitleDecoderFactoryRegistry.h"  // 用于注册自定义解码器
```

### 基本用法

以下示例演示如何通过 `IElectraSubtitleModularFeature` 接口注册一个自定义字幕解码器。该功能通常用于扩展 Electra Player 的字幕格式支持。

```cpp
// 自定义解码器工厂，用于创建特定格式的解码器
class FMySubtitleDecoderFactory : public IElectraSubtitleDecoderFactory
{
public:
    virtual TSharedPtr<IElectraSubtitleDecoder, ESPMode::ThreadSafe> CreateDecoder(const FString& SubtitleCodecName) override
    {
        if (SubtitleCodecName == TEXT("my-custom-format"))
        {
            return MakeShared<FMySubtitleDecoder>();
        }
        return nullptr;
    }
};

// 在模块 Startup 期间注册
void FMyModule::StartupModule()
{
    // 获取模块中的解码器工厂注册表（由 ElectraSubtitles 提供）
    IElectraSubtitleDecoderFactoryRegistry& Registry = IElectraSubtitlesModule::Get();

    TArray<IElectraSubtitleDecoderFactoryRegistry::FCodecInfo> CodecInfo;
    IElectraSubtitleDecoderFactoryRegistry::FCodecInfo Info;
    Info.CodecName = TEXT("my-custom-format");
    Info.Priority = 0;  // 优先级，越大越优先
    CodecInfo.Add(Info);

    static FMySubtitleDecoderFactory Factory;
    Registry.AddDecoderFactory(CodecInfo, &Factory);
}
```

来源：该模式从 `IElectraSubtitleDecoderFactoryRegistry` 和内置解码器（如 TTML、WebVTT）的注册方式推导得出。

### 进阶用法

#### 直接使用解析后的字幕数据（仅限 C++）

如果你想在 Electra Player 输出字幕时进行拦截或二次处理，可以监听 `IElectraSubtitleDecoder::FOnSubtitleReceivedDelegate` 委托。该委托在解码器每次解析出一条完整字幕时触发。

```cpp
// 假设你已经获取到了一个 IElectraSubtitleDecoder 实例（例如通过播放器内部获取）
TSharedPtr<IElectraSubtitleDecoder> Decoder = ...;
Decoder->GetParsedSubtitleReceiveDelegate().AddLambda([](ISubtitleDecoderOutputPtr Output)
{
    // Output 包含字幕文本、时间戳、样式等
    const FString& Text = Output->GetText();
    const Electra::FTimeValue& StartTime = Output->GetStartTime();
    // ...
});
```

## Demo 示例

以下是一个**最小可用模块**，展示如何将自定义测试字幕解码器注册到 Electra Player 系统中（用于开发调试）。

**MySubtitleModule.h**
```cpp
#pragma once
#include "Modules/ModuleManager.h"

class FMySubtitleModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

**MySubtitleModule.cpp**
```cpp
#include "MySubtitleModule.h"
#include "IElectraSubtitleModule.h"
#include "IElectraSubtitleDecoder.h"
#include "ElectraSubtitleDecoderFactoryRegistry.h"

class FMyTestDecoder : public IElectraSubtitleDecoder
{
public:
    // 实现所有纯虚函数（此处省略具体逻辑，仅作演示）
    virtual bool InitializeStreamWithCSD(const TArray<uint8>& InCSD, const Electra::FParamDict& InAdditionalInfo) override { return true; }
    virtual FOnSubtitleReceivedDelegate& GetParsedSubtitleReceiveDelegate() override { return Delegate; }
    virtual Electra::FTimeValue GetStreamedDeliveryTimeOffset() override { return Electra::FTimeValue(); }
    virtual void AddStreamedSubtitleData(const TArray<uint8>& InData, Electra::FTimeValue InAbsoluteTimestamp, Electra::FTimeValue InDuration, const Electra::FParamDict& InAdditionalInfo) override {}
    virtual void SignalStreamedSubtitleEOD() override {}
    virtual void Flush() override {}
    virtual void Start() override {}
    virtual void Stop() override {}
    virtual void UpdatePlaybackPosition(Electra::FTimeValue InAbsolutePosition, Electra::FTimeValue InLocalPosition) override {}

private:
    FOnSubtitleReceivedDelegate Delegate;
};

class FMyTestDecoderFactory : public IElectraSubtitleDecoderFactory
{
public:
    virtual TSharedPtr<IElectraSubtitleDecoder, ESPMode::ThreadSafe> CreateDecoder(const FString& SubtitleCodecName) override
    {
        if (SubtitleCodecName == TEXT("test-format"))
        {
            return MakeShared<FMyTestDecoder>();
        }
        return nullptr;
    }
};

void FMySubtitleModule::StartupModule()
{
    IElectraSubtitleDecoderFactoryRegistry& Registry = IElectraSubtitlesModule::Get();
    static FMyTestDecoderFactory Factory;
    Registry.AddDecoderFactory({{ TEXT("test-format"), 0 }}, &Factory);
}

void FMySubtitleModule::ShutdownModule() {}

IMPLEMENT_MODULE(FMySubtitleModule, MySubtitleModule)
```

说明：该示例需要在插件 `ElectraSubtitles` 已启用的情况下编译运行，并且需要在模块 `Build.cs` 中添加对 `ElectraSubtitles` 和 `ElectraUtil` 的依赖。

## 模块依赖

要使用 `ElectraSubtitles`，你的模块需要在 `PublicDependencyModuleNames` 中包含以下模块：

| 模块 | 用途 |
|---|---|
| `ElectraUtil` | 提供核心时间戳、参数字典等基础工具类 |
| `XmlParser` | 解析 TTML/IMSC1 字幕的 XML 文档（解码器内部使用） |

> 注意：标准 `Core`、`CoreUObject`、`Engine` 等常见依赖未列出，因为它们几乎是所有模块的通用依赖。

## 维护状态

### 近期更新

- 2025-10-01 `9c2c28a2` — ElectraSubtitles: Fixed an incorrectly released mutex（修复一个错误释放的互斥锁）
- 2025-04-08 `275a8bf9` — ElectraPlayer: Fixing TTML subtitle timing in DASH period having a presentationTimeOffset; fixed ind（修复 DASH 周期中带 presentationTimeOffset 时的 TTML 字幕时序）
- 2025-04-04 `cf834c18` — ElectraSubtitles: Fix for overlapping WebVTT subtitles（修复重叠的 WebVTT 字幕）
- 2025-04-03 `8eff8c24` — Electra: Added webvtt subtitle parser; enabled subtitles with HLS; fixed issue with selecting initia（添加 WebVTT 字幕解析器，启用 HLS 字幕支持）
- 2025-03-19 `8845c6d6` — ElectraSubtitles: Setting the sequence index on the output（设置输出序列索引，初始功能提交）

### 维护评价

- **创建时间**：2025-03-19，距今约 7 个月。
- **更新频率**：2025 年 4 月集中添加了 WebVTT 解析器并修复多个问题，10 月修复了一个互斥锁问题。整体更新较为活跃，属于**积极维护**状态。
- **已知问题**：无特别报告，近期修复了时序和重叠问题。
- **推荐使用**：✅ 推荐。该插件是现代 UE Electra 播放系统的重要组成部分，功能稳定，社区支持良好。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/ElectraSubtitles)
- [官方文档](https://docs.unrealengine.com/en-US/Engine/MediaFramework/Overview)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/ElectraSubtitles/Source/ElectraSubtitles)（插件目录内无独立测试文件，相关测试可能在 Electra Player 单元测试目录下）