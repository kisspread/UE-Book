# Electra Codecs

> Codecs for use with Electra player.

| 属性 | 值 |
|---|---|
| 中文名 | Electra 编解码器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ElectraDecoders` (Runtime), `ElectraCodecFactory` (Runtime), `ElectraCodecFactory` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-09-11 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/ElectraCodecs) | |

---

## 用途

Electra Codecs 插件为 Electra 多媒体播放框架提供编解码器支持。它通过统一的工厂模式注册平台特定的音视频解码器实现，使 Electra 播放器能够跨平台解码 H.264、H.265、AAC 等常见格式。

该插件解决了以下核心问题：
- 将编解码器实现与播放器框架解耦，便于扩展新格式或替换底层解码库。
- 提供平台适配层（例如 Windows 上使用 Media Foundation，Android 上使用 Java MediaCodec），无需播放器关心具体平台差异。
- 通过优先级机制自动选择最优解码器，支持本地硬件加速。

## 使用场景

- 你正在开发使用 Electra 播放器的功能（如媒体播放器控件、流媒体播放）。
- 需要为特定格式添加自定义硬件解码器或软件解码器。
- 希望编写跨平台的媒体应用，而不关心底层编解码器接口。

## 蓝图用法

> 本插件为纯 C++ 模块，不直接暴露任何蓝图可调用节点。所有功能需通过 C++ 接口使用。

## C++ 用法

### 头文件引入

```cpp
#include "IElectraCodecFactoryModule.h"
#include "IElectraCodecFactory.h"
#include "IElectraCodecRegistry.h"
```

### 基本用法

**获取最佳编解码器工厂**

在 Electra 播放器初始化过程中，通过模块接口查询支持特定格式的工厂：

```cpp
// 获取模块实例
IElectraCodecFactoryModule& CodecFactoryModule = FModuleManager::LoadModuleChecked<IElectraCodecFactoryModule>("ElectraCodecFactory");

// 准备格式查询参数
TMap<FString, FVariant> FormatInfo;
TMap<FString, FVariant> Options;
const FString CodecFormat = TEXT("avc1.4d002a"); // H.264 High Profile

// 查询最合适的解码器工厂
TSharedPtr<IElectraCodecFactory, ESPMode::ThreadSafe> Factory = CodecFactoryModule.GetBestFactoryForFormat(
    FormatInfo,
    CodecFormat,
    false, // 解码器
    Options
);

if (Factory.IsValid())
{
    // 创建解码器实例
    TSharedPtr<IElectraDecoder, ESPMode::ThreadSafe> Decoder = Factory->CreateDecoderForFormat(CodecFormat, Options);
}
```

**注册自定义编解码器工厂**

第三方模块可以实现 `IElectraCodecFactory` 并注册到系统中：

```cpp
class FMyCodecFactory : public IElectraCodecFactory
{
public:
    virtual int32 SupportsFormat(TMap<FString, FVariant>& OutFormatInfo, const FString& InCodecFormat, bool bInEncoder, const TMap<FString, FVariant>& InOptions) const override
    {
        if (InCodecFormat == TEXT("my.custom.codec"))
            return 100; // 优先级
        return 0;
    }

    virtual void GetConfigurationOptions(TMap<FString, FVariant>& OutOptions) const override
    {
        // 填充配置选项
    }

    virtual TSharedPtr<IElectraDecoder, ESPMode::ThreadSafe> CreateDecoderForFormat(const FString& InCodecFormat, const TMap<FString, FVariant>& InOptions) override
    {
        // 创建并返回解码器实例
        return MakeShared<FMyDecoder>();
    }
};

// 在模块启动时注册
void FMyModule::StartupModule()
{
    IElectraCodecFactoryModule& FactoryModule = FModuleManager::GetModuleChecked<IElectraCodecFactoryModule>("ElectraCodecFactory");
    TSharedPtr<IElectraCodecFactory, ESPMode::ThreadSafe> Factory = MakeShared<FMyCodecFactory>();
    // 通过注册器接口添加（需获取 IElectraCodecRegistry 实例）
    if (auto* Registry = IModularFeatures::Get().GetModularFeature<IElectraCodecModularFeature>(IElectraCodecFactoryModule::GetModularFeatureName()))
    {
        // 实际注册方式通过 TSharedPtr<IElectraCodecRegistry> 扩展可能来自其他模块
    }
}
```

### 进阶用法

**解码器配置选项**

创建解码器时可以传递额外的配置参数，如视频尺寸、比特率等：

```cpp
TMap<FString, FVariant> Options;
Options.Add(TEXT("width"), FVariant(1920u));
Options.Add(TEXT("height"), FVariant(1080u));
Options.Add(TEXT("fps"), FVariant(30.0));
Options.Add(TEXT("bps"), FVariant(5000000ll));

TSharedPtr<IElectraDecoder, ESPMode::ThreadSafe> Decoder = Factory->CreateDecoderForFormat(CodecFormat, Options);
```

**平台特定选项**

Windows 上可传递 D3D 设备句柄等低级资源；Android 上可传递 JNI 环境。

## Demo 示例

以下是一个最小 C++ 示例，展示如何查询并创建 H.264 解码器（假设已注册了 Windows Media Foundation 或 Android 解码器）：

```cpp
// MyCodecDemo.h
#pragma once
#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FMyCodecDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};

// MyCodecDemo.cpp
#include "MyCodecDemo.h"
#include "IElectraCodecFactoryModule.h"
#include "IElectraCodecFactory.h"

DEFINE_LOG_CATEGORY_STATIC(LogMyCodecDemo, Log, All);

void FMyCodecDemoModule::StartupModule()
{
    IElectraCodecFactoryModule& FactoryModule = FModuleManager::LoadModuleChecked<IElectraCodecFactoryModule>("ElectraCodecFactory");

    TMap<FString, FVariant> FormatInfo;
    TMap<FString, FVariant> Options;
    const FString CodecFormat = TEXT("avc1.4d002a");

    TSharedPtr<IElectraCodecFactory, ESPMode::ThreadSafe> Factory = FactoryModule.GetBestFactoryForFormat(
        FormatInfo, CodecFormat, false, Options);

    if (Factory.IsValid())
    {
        TSharedPtr<IElectraDecoder, ESPMode::ThreadSafe> Decoder = Factory->CreateDecoderForFormat(CodecFormat, Options);
        if (Decoder.IsValid())
        {
            UE_LOG(LogMyCodecDemo, Log, TEXT("Successfully created H.264 decoder."));
        }
    }
    else
    {
        UE_LOG(LogMyCodecDemo, Warning, TEXT("No H.264 decoder factory found."));
    }
}

void FMyCodecDemoModule::ShutdownModule()
{
}

IMPLEMENT_MODULE(FMyCodecDemoModule, MyCodecDemo);
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ElectraUtil` | 提供 Electra 基础工具类和数据结构（如派生缓冲区、时间标注） |
| `SignalProcessing` | 音频信号处理功能（ElectraDecoders 依赖） |
| `DirectX` | Windows 平台 D3D 设备资源（ElectraDecoders 依赖） |

**注意**：常见依赖（Core、CoreUObject、Engine 等）已省略。

## 维护状态

### 近期更新

| 日期 | 哈希 | 说明 |
|---|---|---|
| 2025-09-24 | `7d7c63bd` | ElectraUtil: fixed DX12 GPU buffer helper heap issues |
| 2025-09-24 | `f9460684` | ElectraDecoders: Added missing explicit ESPMode on shared pointers of D3D helper for consistency |
| 2025-09-23 | `569bf4e1` | ElectraDecoders: Passing any low level D3D12 failures up for better error reporting |
| 2025-09-15 | `4a054a4b` | ElectraDecoders: Only register the MF codec factories when the required DLLs could be loaded |
| 2025-09-11 | `6312e16d` | Fix crash from pending JNI exception in non-Shipping builds |

### 维护评价

该插件创建于 2025年9月，非常新但已有多次实质性更新，包括修复 D3D 错误、JNI 崩溃、注册逻辑优化。开发活跃，且是 Electra 播放框架的核心依赖。当前无已知废弃风险。**推荐使用**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/ElectraCodecs)
- [官方文档 - Media Framework Overview](https://docs.unrealengine.com/en-US/Engine/MediaFramework/Overview)
- [Electra Player 概述（非官方翻译）](https://docs.unrealengine.com/5.7/zh-CN/MediaFramework/MediaPlayer)