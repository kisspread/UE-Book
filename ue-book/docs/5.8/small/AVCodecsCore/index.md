# AVCodecs Core

> Core Plugin for various Audio/Video codecs

| 属性 | 值 |
|---|---|
| 中文名 | 音视频编解码核心 |
| 分类 | Codecs |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AVCodecsCore` (Runtime), `AVCodecsCoreRHI` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-01-25 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AVCodecs/AVCodecsCore) | |

## 用途

`AVCodecsCore` 是用于音频和视频编解码的基础核心插件。它本身不包含具体的编解码器实现（如 H.264 编码器或 AAC 解码器），而是提供了一套抽象层、接口定义和通用工具，用于统一管理、注册和使用不同平台及后端（软件/硬件）的音视频编解码器。它的存在是为了让上层应用（如媒体播放器、流媒体服务、录制功能）能够以一致的方式访问底层多样化的编解码能力。

## 使用场景

- 你需要为你的项目实现跨平台的视频录制或实时流媒体功能，且希望在不同设备上使用最优的硬件加速编解码器。
- 你正在开发一个媒体播放器插件，需要解码各种格式的视频文件。
- 你希望封装一个统一的音视频处理管线，并需要为不同的编码/解码任务动态选择合适的实现。

## 蓝图用法

蓝图 API 主要集中在 `AVCodecsCore` 模块中，用于创建和管理编解码器实例。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Video Encoder` | 根据类型（如 H264）和配置创建一个视频编码器实例 | `UAVCodecsBlueprintLibrary` |
| `Create Video Decoder` | 根据类型（如 H264）创建一个视频解码器实例 | `UAVCodecsBlueprintLibrary` |
| `Create Audio Encoder` | 根据类型（如 AAC）创建一个音频编码器实例 | `UAVCodecsBlueprintLibrary` |
| `Create Audio Decoder` | 根据类型（如 AAC）创建一个音频解码器实例 | `UAVCodecsBlueprintLibrary` |
| `Get Registered Video Encoders` | 获取当前所有已注册的视频编码器类型 | `UAVCodecsBlueprintLibrary` |
| `Get Registered Video Decoders` | 获取当前所有已注册的视频解码器类型 | `UAVCodecsBlueprintLibrary` |

### 使用示例（蓝图描述）

1.  创建一个 **Create Video Encoder** 节点，`Encoder Type` 设为 `EVideoCodec::H264`。
2.  连接一个包含编码参数（如分辨率、比特率）的 `FVideoEncoderConfig` 结构体到 `Config` 输入引脚。
3.  节点的输出引脚会返回一个 `UVideoEncoder*` 对象，你可以调用其上的 `Encode` 等函数进行编码。

## C++ 用法

### 头文件引入

```cpp
#include “AVCodecsCore.h“
#include “Video/VideoEncoder.h” // 示例：使用视频编码器
#include “Audio/AudioDecoder.h” // 示例：使用音频解码器
```

### 基本用法

在使用具体的编解码器前，需要确保对应的插件（如提供特定硬件编码器的插件）已加载，这些插件会在启动时向 `AVCodecsCore` 注册其提供的工厂。

```cpp
// 获取已注册的视频编码器工厂
TArray<TWeakObjectPtr<UVideoEncoderFactory>> RegisteredFactories;
UVideoEncoderRegistry::Get().GetRegisteredFactories(RegisteredFactories);

// 选择一个工厂并创建编码器实例
if (RegisteredFactories.Num() > 0)
{
    TWeakObjectPtr<UVideoEncoderFactory> Factory = RegisteredFactories[0];
    if (Factory.IsValid())
    {
        UVideoEncoder* Encoder = Factory->CreateEncoder();
        if (Encoder)
        {
            // 配置编码器
            FVideoEncoderConfig Config;
            Config.Width = 1920;
            Config.Height = 1080;
            Config.Bitrate = 5000000;
            Encoder->Configure(Config);

            // 开始编码过程（示例）
            // Encoder->Encode(FrameData);
        }
    }
}
```

## Demo 示例

以下示例展示了如何在模块启动时（`StartupModule`）查询可用的视频解码器，并在游戏逻辑中创建一个实例。

**MyPluginModule.h**
```cpp
#pragma once

#include “Modules/ModuleManager.h”

class FMyPluginModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    void ListAvailableVideoDecoders();
};
```

**MyPluginModule.cpp**
```cpp
#include “MyPluginModule.h“
#include “Video/VideoDecoderRegistry.h”

#define LOCTEXT_NAMESPACE “FMyPluginModule”

void FMyPluginModule::StartupModule()
{
    ListAvailableVideoDecoders();
}

void FMyPluginModule::ShutdownModule()
{
}

void FMyPluginModule::ListAvailableVideoDecoders()
{
    TArray<TWeakObjectPtr<UVideoDecoderFactory>> Factories;
    UVideoDecoderRegistry::Get().GetRegisteredFactories(Factories);

    UE_LOG(LogTemp, Log, TEXT(“Found %d registered video decoder factories.“), Factories.Num());
    for (const auto& Factory : Factories)
    {
        if (Factory.IsValid())
        {
            UE_LOG(LogTemp, Log, TEXT(“ - %s“), *Factory->GetFriendlyName());
        }
    }
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyPluginModule, MyPlugin)
```

## 模块依赖

使用此插件，你的模块需要添加对 `AVCodecsCore` 的依赖。如果你的代码需要直接与渲染硬件接口（RHI）交互处理纹理数据，则还需要依赖 `AVCodecsCoreRHI`。

| 模块 | 用途 |
|---|---|
| `AVCodecsCoreRHI` | 提供与 RHI 层交互的接口，用于处理 GPU 纹理数据的编解码。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的警告。 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 使函数类型转换警告在 MSVC 和 Clang 之间保持可移植性。 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复了在格式化函数中使用作用域枚举可能导致乱码输出的问题。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修正了格式说明符与64位参数不匹配的问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移至 UE_LOGF。 |

### 维护评价

- **状态**：**维护中**。最近一次更新在约 1 个月内，且过去几个月内有持续的提交。
- **更新内容**：近期的更新主要集中在**代码质量提升和编译器警告修复**（如浮点处理、类型转换、格式说明符），没有添加新功能。这表明该插件处于一个相对稳定的维护阶段，主要进行编译兼容性和代码健壮性的加固。
- **风险**：插件仍标记为**实验性**（`IsExperimentalVersion: true`），且**默认未启用**。这意味着其 API 和功能未来可能会发生 breaking changes。
- **建议**：如果你需要构建跨平台的音视频编解码功能，且愿意接受实验性 API 的潜在变动，可以基于此核心进行开发。但对于生产环境，需密切关注其更新日志，并做好应对 API 变更的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AVCodecs/AVCodecsCore)
- [子模块文档：AVCodecsCore](./AVCodecsCore.md)
- [子模块文档：AVCodecsCoreRHI](./AVCodecsCoreRHI.md)