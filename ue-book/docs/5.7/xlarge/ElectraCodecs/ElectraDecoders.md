# Electra Codecs

> Codecs for use with Electra player.

| 属性 | 值 |
|---|---|
| 中文名 | Electra 解码模块 |
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

`ElectraDecoders` 是 **Electra 媒体播放器**（`ElectraPlayer`）的底层解码器模块，负责提供平台原生的音频和视频硬件解码能力。它不直接暴露给用户，而是被 `ElectraCodecFactory` 模块调用，通过工厂模式注册各类编解码器（如 AAC、H.264、H.265、VP9）到全局编解码器注册表（`IElectraCodecRegistry`）中。

**为什么要存在？**  
Electra 媒体框架需要跨平台的高性能多媒体解码能力，而不同操作系统（Windows、macOS、iOS、Android、Linux）拥有不同的原生解码 API（如 Windows 的 Media Foundation、Android 的 MediaCodec、Apple 的 VideoToolbox）。`ElectraDecoders` 将这些平台差异封装为统一的 `IElectraDecoder` 接口，使上层播放器无需关心具体平台实现，只需通过工厂方法获取解码器实例即可。

## 使用场景

- 你正在使用 **Electra 媒体播放器** 播放 HLS/DASH 流媒体，需要硬件加速解码 H.264/H.265 视频或 AAC 音频。
- 你需要为项目添加自定义媒体格式支持，希望复用 Electra 的解码器注册机制。
- 你的应用运行在 Android/iOS 设备上，需要利用硬件编解码器降低 CPU 占用。

## 蓝图用法

该模块为纯 C++ 实现，不暴露任何蓝图可调用函数或属性。所有解码器的创建、配置和管理均通过 C++ 接口进行。

## C++ 用法

### 头文件引入

```cpp
#include "ElectraDecodersModule.h"
#include "IElectraDecoder.h"
#include "IElectraCodecFactory.h"
#include "IElectraCodecRegistry.h"
```

### 基本用法

**1. 获取解码器工厂**（以 Android H.264 为例）  
```cpp
// 文件：ElectraCodecs/Source/ElectraDecoders/Private/Android/h264/H264_VideoDecoder_Android.h
TSharedPtr<IElectraCodecFactory, ESPMode::ThreadSafe> Factory = FH264VideoDecoderAndroid::CreateFactory();
```

**2. 通过工厂创建解码器**  
```cpp
TMap<FString, FVariant> Options;
Options.Add(TEXT("MaxWidth"), 1920);
Options.Add(TEXT("MaxHeight"), 1080);
// 具体选项参考各解码器的 GetConfigurationOptions()
TSharedPtr<IElectraDecoder, ESPMode::ThreadSafe> Decoder = Factory->CreateDecoder(Options);
```

**3. 注册解码器到编解码器注册表**  
通常在模块启动时调用，例如在 `FPlatformElectraDecodersAndroid::Startup()` 中：
```cpp
// 文件：ElectraCodecs/Source/ElectraDecoders/Private/Android/AndroidPlatformElectraDecoders.cpp
void FPlatformElectraDecodersAndroid::RegisterWithCodecFactory(IElectraCodecRegistry* Registry)
{
    Registry->RegisterCodecFactory(FAACAudioDecoderAndroid::CreateFactory());
    Registry->RegisterCodecFactory(FH264VideoDecoderAndroid::CreateFactory());
    Registry->RegisterCodecFactory(FH265VideoDecoderAndroid::CreateFactory());
    Registry->RegisterCodecFactory(FVPxVideoDecoderAndroid::CreateFactory());
}
```

**4. 使用解码器解码**（以 AAC 音频为例）  
```cpp
// 创建解码器
TSharedPtr<IElectraDecoder, ESPMode::ThreadSafe> AacDecoder = IElectraAudioDecoderAAC_Android::Create(Options);

// 提交输入数据（ES 帧）
IElectraDecoderInputRef Input = ...;
Decoder->SetInputData(Input);

// 获取解码输出
IElectraDecoderOutputRef Output = Decoder->GetOutput();
if (Output.IsValid())
{
    // 处理音频样本
    const TArray<uint8>& AudioData = Output->GetData();
    // ...
}
```

### 进阶用法

**跨平台解码器配置查询**  
每个解码器实现均提供 `GetConfigurationOptions()` 静态方法，用于返回支持的配置参数。例如在 Windows（DX）中查询 H.264 解码器配置：
```cpp
TMap<FString, FVariant> ConfigOptions;
IElectraVideoDecoderH264_DX::GetConfigurationOptions(ConfigOptions);
// 遍历 ConfigOptions 查看支持的参数名称和默认值
```

**获取平台支持的编解码能力**  
部分解码器（如 H.264/H.265 for Apple）提供 `PlatformGetSupportedConfigurations()` 来查询设备支持的分辨率、帧率等信息：
```cpp
TArray<IElectraVideoDecoderH264_Apple::FSupportedConfiguration> Supported;
IElectraVideoDecoderH264_Apple::PlatformGetSupportedConfigurations(Supported);
for (const auto& Config : Supported)
{
    UE_LOG(LogElectraDecoders, Log, TEXT("H.264: Profile=%d, Level=%d, %dx%d @ %d fps"),
        Config.Profile, Config.Level, Config.Width, Config.Height, Config.FramesPerSecond);
}
```

**Windows DX 解码器底层控制**  
`IElectraVideoDecoderH264_DX` 提供了 `PlatformCreateMFDecoderTransform` 方法来直接访问 Media Foundation 的 `IMFTransform`，用于高级定制：
```cpp
IElectraVideoDecoderH264_DX::IPlatformHandle* Handle = nullptr;
FError Error = IElectraVideoDecoderH264_DX::PlatformCreateMFDecoderTransform(&Handle, Options);
if (Handle)
{
    void* MFT = Handle->GetMFTransform();   // 获取 IMFTransform*
    // 使用 MFT 进行自定义配置
    IElectraVideoDecoderH264_DX::PlatformReleaseMFDecoderTransform(&Handle);
}
```

**MP3 解码器集成**  
`FElectraMediaMP3Decoder` 提供了独立的 MP3 解码工厂，可通过 `CreateFactory()` 获取并注册：
```cpp
TSharedPtr<IElectraCodecFactory, ESPMode::ThreadSafe> Mp3Factory = FElectraMediaMP3Decoder::CreateFactory();
Registry->RegisterCodecFactory(Mp3Factory);
```

## Demo 示例

下面是一个最小 C++ 示例，演示如何在 `PostEngineInit` 阶段注册 Android H.264 解码器（非完整运行代码，仅示意模式）：

**H264DecoderRegistrar.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FH264DecoderRegistrar : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

**H264DecoderRegistrar.cpp**
```cpp
#include "H264DecoderRegistrar.h"
#include "IElectraCodecRegistry.h"
#include "Android/h264/H264_VideoDecoder_Android.h"

IMPLEMENT_MODULE(FH264DecoderRegistrar, H264DecoderRegistrar);

void FH264DecoderRegistrar::StartupModule()
{
    // 获取 ElectraCodecFactory 模块（需在 Build.cs 中添加依赖）
    IElectraCodecRegistry* Registry = FModuleManager::GetModulePtr<IElectraCodecRegistry>("ElectraCodecFactory");
    if (Registry)
    {
        auto Factory = FH264VideoDecoderAndroid::CreateFactory();
        Registry->RegisterCodecFactory(Factory);
    }
}

void FH264DecoderRegistrar::ShutdownModule()
{
    // 可选清理
}
```

**Build.cs 依赖样例**
```csharp
PublicDependencyModuleNames.AddRange(
    new string[] {
        "ElectraCodecFactory",
        "ElectraDecoders"
    }
);
```

> 实际部署时，通常由 `FElectraDecodersModule` 模块自动完成平台解码器的注册，无需手动编写上述代码。本例仅展示如何自定义注册流程。

## 模块依赖

**省略常见依赖**：无特殊依赖（仅标准 Core/Engine/Slate 等）。

| 模块 | 用途 |
|---|---|
| `SignalProcessing` | 音频信号处理辅助（用于音频解码输出转换） |
| `DirectX` | Windows 平台 DX 解码器所需的 DirectX 基础设施 |

## 维护状态

### 近期更新

- 2025-09-24 `7d7c63bd` ElectraUtil: fixed DX12 GPU buffer helper heap issues  
- 2025-09-24 `f9460684` ElectraDecoders: Added missing explicit ESPMode on shared pointers of D3D helper for consistency  
- 2025-09-23 `569bf4e1` ElectraDecoders: Passing any low level D3D12 failures up for better error reporting  
- 2025-09-15 `4a054a4b` ElectraDecoders: Only register the MF codec factories when the required DLLs could be loaded  
- 2025-09-11 `6312e16d` Fix crash from pending JNI exception in non-Shipping builds  

### 维护评价

- **创建时间**: 2025 年 9 月，距今不到 1 个月，属于全新插件。  
- **更新频率**: 最近 2 周内有多次功能性提交（DX 错误处理、DLL 加载逻辑、JNI 稳定性），说明团队正在积极开发和打磨。  
- **活跃度**: 高。提交信息显示针对平台特定 bug 和接口完整性进行修复，没有停滞迹象。  
- **已知限制**: 作为新插件，部分特性可能仍在迭代中（如 VPx 在 Linux 上的支持、MP3 解码器的跨平台一致性）。  
- **推荐使用**: ✅ 强烈推荐。Electra 是 UE 5.x 中推荐的现代媒体框架，此模块是其核心依赖。若需要使用 ElectraPlayer 或自行集成底层解码器，应首选此插件。

> ⚠️ 注意：插件默认不启用，需在项目插件设置中手动勾选 “Electra Codecs”。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/ElectraCodecs)
- [官方文档](https://docs.unrealengine.com/en-US/Engine/MediaFramework/Overview)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/ElectraCodecs/Source/ElectraDecoders/Private/)（平台私有实现，无独立测试目录）