# Electra Codecs

> Codecs for use with Electra player.

| 属性 | 值 |
|---|---|
| 中文名 | Electra解码器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ElectraCodecFactory` (Runtime), `ElectraDecoders` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2023-04-03 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraCodecs) | |

## 用途

ElectraCodecs 是一个为 Epic 的 Electra 媒体播放器提供解码器支持的插件框架。它的核心作用不是直接提供解码器实现，而是**定义了一个标准化的接口和注册机制**，允许各种平台原生的或第三方的音频、视频解码器能够以插件形式集成到 Electra 播放器中。这个插件解决了在跨平台媒体播放中，解码器能力的统一管理、发现和扩展问题，使得 Electra 播放器能够根据媒体格式和平台能力，动态选择最合适的解码器。

## 使用场景

- 你正在开发一个需要播放多种编码格式（如 H.264， H.265， VP9， AAC）视频或音频的功能。
- 你的应用需要支持自适应流媒体（如 HLS， DASH），并且希望根据不同平台（Windows， Android， iOS）的硬件能力，动态选择最高效的解码器。
- 你计划为一种新的媒体格式编写解码器，并希望它能无缝集成到 Unreal Engine 的 Electra 播放系统中。

## 蓝图用法

该插件主要提供 C++ 编程接口，未发现公开的 `BlueprintCallable` 函数。其功能主要用于底层媒体播放系统的扩展和集成，而非直接用于游戏逻辑蓝图。

## C++ 用法

该插件的核心是定义了媒体解码器工厂的接口标准。

### 头文件引入

```cpp
#include "IElectraCodecFactoryModule.h"
#include "IElectraCodecRegistry.h"
#include "IElectraCodecFactory.h"
```

### 基本用法

**1. 查询和获取解码器工厂**

通常，播放器内部会通过模块接口获取最匹配的工厂。
```cpp
// 假设通过模块系统获取 IElectraCodecFactoryModule 接口
FModuleManager::Get().LoadModule(TEXT(“ElectraCodecFactory”));
IElectraCodecFactoryModule* CodecFactoryModule = FModuleManager::Get().GetModulePtr<IElectraCodecFactoryModule>(TEXT(“ElectraCodecFactory”));

if (CodecFactoryModule)
{
    // 构建一个描述所需媒体格式的 FCodecTypeFormat 结构
    Electra::FCodecTypeFormat DesiredFormat;
    // ... 填充格式信息 (如 Type, FourCC, RFC6381 等)

    TMap<FString, FVariant> AdditionalOptions;
    // ... 可能添加如最大分辨率等额外选项

    TMap<FString, FVariant> OutFormatInfo;
    // 获取最适合此格式的解码器工厂
    TSharedPtr<IElectraCodecFactory, ESPMode::ThreadSafe> BestFactory = CodecFactoryModule->GetBestDecoderFactoryForFormat(OutFormatInfo, DesiredFormat, AdditionalOptions);

    if (BestFactory.IsValid())
    {
        // 使用工厂创建解码器实例
        TSharedPtr<IElectraDecoder, ESPMode::ThreadSafe> Decoder = BestFactory->CreateDecoder(DesiredFormat, AdditionalOptions);
        // ... 使用 Decoder 进行解码操作
    }
}
```

**2. 注册自定义解码器工厂**

要为 Electra 添加一个新的解码器，你需要实现 `IElectraCodecFactory` 接口，并将其注册。
```cpp
class FMyCustomAudioCodecFactory : public IElectraCodecFactory, public IElectraCodecFactory::IProviderInformation
{
public:
    // IElectraCodecFactory 接口实现
    virtual void GetConfigurationOptions(TMap<FString, FVariant>& OutOptions) const override
    {
        // 声明此解码器支持的配置选项
    }

    virtual int32 SupportsDecoding(TMap<FString, FVariant>& OutFormatInfo, const Electra::FCodecTypeFormat& InCodecFormat, const TMap<FString, FVariant>& InAdditionalOptions) const override
    {
        // 检查输入的格式是否被此工厂支持
        // 返回优先级数值 (越大越优先)，不支持则返回 0。
        if (/* 支持该格式 */)
        {
            return 100; // 返回一个优先级
        }
        return 0;
    }

    virtual TSharedPtr<IElectraDecoder, ESPMode::ThreadSafe> CreateDecoder(const Electra::FCodecTypeFormat& InCodecFormat, const TMap<FString, FVariant>& InAdditionalOptions) override
    {
        // 创建并返回具体的解码器实例
        return MakeShared<FMyCustomAudioDecoder>();
    }

    // IProviderInformation 接口实现
    virtual FString GetName() const override { return TEXT(“MyCustomAudio”); }
    virtual FString GetVersion() const override { return TEXT(“1.0”); }
    virtual FString GetImplementation() const override { return TEXT(“CPU”); }
    virtual FString GetVendor() const override { return TEXT(“MyCompany”); }

    virtual const IElectraCodecFactory::IProviderInformation& GetProviderInformation() const override
    {
        return *this;
    }
};

// 在模块启动时注册工厂
void FMyCustomCodecModule::StartupModule()
{
    IElectraCodecRegistry* Registry = FModuleManager::Get().LoadModulePtr<IElectraCodecFactoryModule>(TEXT(“ElectraCodecFactory”));
    if (Registry)
    {
        TSharedPtr<FMyCustomAudioCodecFactory> MyFactory = MakeShared<FMyCustomAudioCodecFactory>();
        Registry->AddCodecFactory(MyFactory);
    }
}
```

## Demo 示例

**自定义音频解码器工厂头文件 (MyAudioCodecFactory.h):**
```cpp
#pragma once

#include "IElectraCodecFactory.h"
#include "IElectraDecoder.h"

class FMyAudioDecoder : public IElectraDecoder
{
public:
    // IElectraDecoder 接口的具体实现省略，此处为示意
    virtual ~FMyAudioDecoder() = default;
    // ... Decode(), GetOutput() 等方法实现
};

class FMyAudioCodecFactory : public IElectraCodecFactory, public IElectraCodecFactory::IProviderInformation
{
public:
    virtual ~FMyAudioCodecFactory() = default;

    // IElectraCodecFactory Interface
    virtual void GetConfigurationOptions(TMap<FString, FVariant>& OutOptions) const override;
    virtual int32 SupportsDecoding(TMap<FString, FVariant>& OutFormatInfo, const Electra::FCodecTypeFormat& InCodecFormat, const TMap<FString, FVariant>& InAdditionalOptions) const override;
    virtual TSharedPtr<IElectraDecoder, ESPMode::ThreadSafe> CreateDecoder(const Electra::FCodecTypeFormat& InCodecFormat, const TMap<FString, FVariant>& InAdditionalOptions) override;
    virtual const IElectraCodecFactory::IProviderInformation& GetProviderInformation() const override;

    // IProviderInformation Interface
    virtual FString GetName() const override;
    virtual FString GetVersion() const override;
    virtual FString GetImplementation() const override;
    virtual FString GetVendor() const override;
};
```

**自定义音频解码器工厂实现文件 (MyAudioCodecFactory.cpp):**
```cpp
#include "MyAudioCodecFactory.h"

void FMyAudioCodecFactory::GetConfigurationOptions(TMap<FString, FVariant>& OutOptions) const
{
    // 可以声明如“最大采样率”等配置选项
}

int32 FMyAudioCodecFactory::SupportsDecoding(TMap<FString, FVariant>& OutFormatInfo, const Electra::FCodecTypeFormat& InCodecFormat, const TMap<FString, FVariant>& InAdditionalOptions) const
{
    // 简单示例：检查是否为音频类型且 FourCC 匹配 “MYAC”
    if (InCodecFormat.Type == Electra::FCodecTypeFormat::EType::Audio && InCodecFormat.FourCC == 0x4D594143) // ‘MYAC’
    {
        // 可以填充 OutFormatInfo 供调用者参考
        return 10;
    }
    return 0;
}

TSharedPtr<IElectraDecoder, ESPMode::ThreadSafe> FMyAudioCodecFactory::CreateDecoder(const Electra::FCodecTypeFormat& InCodecFormat, const TMap<FString, FVariant>& InAdditionalOptions)
{
    return MakeShared<FMyAudioDecoder>();
}

const IElectraCodecFactory::IProviderInformation& FMyAudioCodecFactory::GetProviderInformation() const
{
    return *this;
}

FString FMyAudioCodecFactory::GetName() const { return TEXT(“MyAudioCodec”); }
FString FMyAudioCodecFactory::GetVersion() const { return TEXT(“0.1”); }
FString FMyAudioCodecFactory::GetImplementation() const { return TEXT(“Custom”); }
FString FMyAudioCodecFactory::GetVendor() const { return TEXT(“ExampleCorp”); }
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `SignalProcessing` | 用于音频信号处理（ElectraDecoders 模块依赖） |
| `DirectX` | 用于访问 DirectX 相关的解码器或硬件加速功能（ElectraDecoders 模块依赖） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `e86f17b3` | Use ConvertToTimescale for overflow-safe milliFPS computation | 使用 ConvertToTimescale 进行防溢出的毫秒帧率计算 |
| 2026-05-13 | `4754a81b` | Fix Invalid Frame Rate for Android HEVC ingest without Third Party Encoder | 修复无第三方编码器时Android HEVC摄取的无效帧率问题 |
| 2026-05-12 | `3bbffee9` | ElectraCodecs: Fixed HEVC DCR array extraction. Should not append to a single array but retain indiv | 修复HEVC DCR数组提取，应保留单独数组而非合并 |
| 2026-04-27 | `53a5ec2a` | ElectraCodecs: Permitting short form codec RFC for VP8 and VP9 codec | 允许VP8和VP9编解码器使用简短的RFC格式 |
| 2026-04-23 | `0cd64869` | ElectraDecoders: Fixed an issue where mp4a audio is wrapped inside a wave box in a QuickTime file. T | 修复QuickTime文件中mp4a音频被包装在wave盒中的问题 |

### 维护评价

ElectraCodecs 是一个相对较新的插件（创建于2023年），但近期（2026年）有密集的维护活动。最近的提交记录表明该插件正在被积极维护和改进，主要集中在：
1.  **Bug修复**：解决了特定平台（Android）和编解码格式（HEVC, VP8/VP9, AAC）的具体问题。
2.  **格式兼容性增强**：增加了对更多编解码器RFC格式的支持。
3.  **稳定性改进**：修复了潜在的计算溢出和数据提取错误。

尽管最近一次提交记录在2026年5月，距今有一段时间，但考虑到这是底层媒体基础设施组件，更新周期可能较长。从提交历史看，**该插件仍处于活跃维护状态，没有废弃迹象**。对于需要稳定、跨平台媒体播放能力的项目，**推荐使用**，并确保启用此插件及其依赖的 `ElectraPlayer` 插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraCodecs)
- [官方文档](https://docs.unrealengine.com/en-US/Engine/MediaFramework/Overview)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraCodecs/Tests) （推测路径，需确认）