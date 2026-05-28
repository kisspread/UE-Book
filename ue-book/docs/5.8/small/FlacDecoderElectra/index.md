# FLAC audio decoder for Electra

> Implements FLAC audio playback with the Electra media player

| 属性 | 值 |
|---|---|
| 中文名 | FLAC解码器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `FlacDecoderElectra` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-08-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/FlacDecoderElectra) | |

## 用途
该插件为 Unreal Engine 的 **Electra 媒体播放框架** 提供 **FLAC（Free Lossless Audio Codec）音频格式的解码能力**。FLAC 是一种广泛使用的无损音频压缩格式，能够完美还原原始音质且文件体积更小。通过集成此插件，游戏或应用程序可以使用 Electra 播放器播放 `.flac` 格式的音频文件，而无需依赖外部解码库或转换格式。

## 使用场景
- 你的游戏或应用需要播放高品质的无损背景音乐或音效。
- 你的音频资产以 FLAC 格式存储，并希望直接通过 Electra 媒体播放器进行播放，避免格式转换带来的质量损失或额外工作。
- 你正在 Windows 平台上开发，并且已经使用 Electra 作为主要的媒体播放解决方案。

## 蓝图用法
此插件主要通过 C++ 模块的自动注册机制为 Electra 播放器提供解码支持，**没有直接暴露给蓝图的函数节点**。

### 使用说明
启用插件后，其功能将自动集成到 Electra 媒体播放器中。在蓝图中，你只需使用标准的 `Media Player` 节点播放 `.flac` 文件即可，解码过程在底层由本插件处理。

**蓝图操作流程：**
1.  确保项目启用了 `FlacDecoderElectra` 插件。
2.  在蓝图中使用 `Open Source` 或 `Open URL` 节点，指定一个 `.flac` 文件路径或 URL 给 `Media Player` 对象。
3.  调用 `Play` 节点开始播放，Electra 播放器会自动调用本插件提供的解码器。

## C++ 用法

### 头文件引入
由于此插件主要提供内部服务，使用者通常不需要直接包含其头文件。集成工作由 Electra 播放器框架自动完成。

### 基本用法（插件工作原理）
插件的核心在于其**运行时模块**，它在启动时向 Electra 的解码器工厂系统注册一个能够创建 FLAC 解码器的工厂。播放器在遇到 FLAC 格式文件时，会请求工厂创建对应的解码器实例。

以下是插件模块注册逻辑的简化示意（非直接使用代码，而是解释其行为）：
```cpp
// 模块启动时自动调用，向 Electra 注册解码器工厂
void FFlacDecoderElectraModule::StartupModule()
{
    // ... 初始化日志等
    FElectraMediaFlacDecoder::Startup();
}

// 关闭时清理
void FFlacDecoderElectraModule::ShutdownModule()
{
    FElectraMediaFlacDecoder::Shutdown();
}
```

对于最终用户，**无需编写额外 C++ 代码**。只需：
1.  在项目的 `.Build.cs` 中添加对 `FlacDecoderElectra` 模块的运行时依赖。
2.  确保在 `DefaultEngine.ini` 或代码中启用了 Electra 媒体播放器。
3.  像使用其他媒体格式一样，通过 Electra 播放器加载和播放 `.flac` 文件。

### 进阶用法
如果你正在开发一个自定义的 Electra 解码器或需要了解插件如何与解码器工厂交互，可以查看 `FElectraMediaFlacDecoder` 类。它提供了静态方法 `CreateFactory()`，该方法返回一个 `IElectraCodecFactory` 的共享指针，这是 Electra 解码器系统识别和实例化解码器的关键接口。

## Demo 示例

### Minimal Example (Module Registration)
此示例展示了插件模块最核心的实现，即注册和注销解码器逻辑。
```cpp
// File: FlacDecoderElectraModule.h
#pragma once
#include "Modules/ModuleManager.h"

DECLARE_LOG_CATEGORY_EXTERN(LogFlacElectraDecoder, Log, All);

class FFlacDecoderElectraModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};

// File: FlacDecoderElectraModule.cpp
#include "FlacDecoderElectraModule.h"
#include "FlacDecoder/ElectraMediaFlacDecoder.h"

DEFINE_LOG_CATEGORY(LogFlacElectraDecoder);

void FFlacDecoderElectraModule::StartupModule()
{
    UE_LOG(LogFlacElectraDecoder, Log, TEXT("FlacDecoderElectra: Module Startup"));
    FElectraMediaFlacDecoder::Startup();
}

void FFlacDecoderElectraModule::ShutdownModule()
{
    UE_LOG(LogFlacElectraDecoder, Log, TEXT("FlacDecoderElectra: Module Shutdown"));
    FElectraMediaFlacDecoder::Shutdown();
}

IMPLEMENT_MODULE(FFlacDecoderElectraModule, FlacDecoderElectra);
```

## 模块依赖
要使你的模块能够使用此插件提供的功能（即通过 Electra 播放 FLAC 文件），需要在模块的 `Build.cs` 中进行依赖。

| 模块 | 用途 |
|---|---|
| `ElectraCodecs` | **关键依赖**。此插件是 `ElectraCodecs` 插件的一部分，提供了基础的解码器框架和接口。 |

*说明：除了对 `ElectraCodecs` 的特定依赖外，该插件只依赖常见的运行时模块（Core, CoreUObject, Engine等）。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-20 | `3ed2062b` | ElectraDecoders: modernized the decoder factory to be more usable for other clients | 现代化了解码器工厂，提升对其他客户端的可用性 |
| 2026-01-12 | `611dda1f` | Electra: Moved mp4 related utilities into dedicated plugin | 将MP4相关工具移至专用插件，可能涉及依赖调整 |
| 2025-11-19 | `514ccff4` | ElectraCodecs: Add information about the decoder implementation being used for decoding. | 为解码器添加实现信息，便于调试和状态监控 |
| 2025-08-06 | `831eeb24` | Reworked ElectraSamples, ElectraUtils and the decoder output of Electra Player | 重构了采样、工具和播放器解码输出，属于基础架构更新 |
| 2025-06-10 | `2d174355` | Electra: Removal of the platform resource delegate and the wrapping plugin | 移除了平台资源委托和包装插件，简化了架构 |

### 维护评价
**维护状态：活跃维护中。**
- **优点**：作为2024年新增的插件，代码库较新。从提交记录看，它随着 Electra 媒体框架的整体重构而持续更新（如解码器工厂现代化），表明它被纳入主流维护路径。
- **当前状态**：最近的提交（2026年4月）是对核心解码器工厂的改进，说明该插件在不断优化。
- **注意事项**：该插件默认未启用（`EnabledByDefault: false`），且仅支持 `Win64` 平台，这是一个主要限制。它明确排除了服务器（`Server`）目标。
- **推荐使用**：如果你的项目需要在 **Windows 平台**上使用 Electra 播放器播放 **FLAC 无损音频**，并且不介意手动启用插件，那么**推荐使用**此插件。它是实现该功能最直接和官方的途径。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/FlacDecoderElectra)
- [官方文档]() (无)
- [测试用例]() (无)