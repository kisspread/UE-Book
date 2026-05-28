# Opus audio decoder  for Electra

> Implements Opus audio playback with the Electra media player

| 属性 | 值 |
|---|---|
| 中文名 | Opus解码器(Electra) |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `OpusDecoderElectra` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2023-04-03 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/OpusDecoderElectra) | |

## 用途

本插件为 UE5 的 **Electra 媒体播放器框架** 提供了 **Opus 音频编解码器**的解码功能。Opus 是一种高效的音频压缩格式，特别适用于流媒体、实时通信和游戏中的音频流。该插件的主要作用是注册一个基于软件实现的 Opus 解码器工厂，使 Electra 播放器能够解码和播放 Opus 编码的音频流，从而扩展 Electra 播放器的格式兼容性。

## 使用场景

- 你的项目使用 **Electra 播放器** 来播放基于 HTTP 流媒体 (HLS/DASH) 的视频或音频。
- 你的媒体源包含使用 **Opus** 编码的音轨（例如，某些在线视频流或 WebRTC 通话）。
- 你需要在**不支持硬件解码 Opus** 的平台（或为了通用性）上，通过纯软件方式播放 Opus 音频。

## 蓝图用法

此插件是纯 C++ 的运行时解码器实现，主要集成在 Electra 媒体框架底层，**不直接暴露任何可供蓝图调用的节点**。用户通过 Electra 播放器的标准蓝图 API（如 `Open URL`， `Open Source`）打开媒体，解码过程是自动的。

## C++ 用法

此插件的核心是一个解码器工厂，由 Electra 框架在初始化时调用，无需用户手动实例化。但在需要手动管理或排查问题时，了解其接口是必要的。

### 头文件引入

```cpp
// 包含核心解码器声明头文件
#include "OpusDecoder/ElectraMediaOpusDecoder.h"
```

### 基本用法

解码器的生命周期由插件模块自动管理。典型的使用流程（概念上）如下：
```cpp
// 插件模块加载时会自动调用 Startup，向 Electra 框架注册解码器工厂
FElectraMediaOpusDecoder::Startup();

// 当需要创建解码器时，Electra 框架会通过工厂接口请求创建解码器实例
// TSharedPtr<IElectraCodecFactory> OpusFactory = FElectraMediaOpusDecoder::CreateFactory();
// 具体的解码器实例由工厂在内部创建和管理

// 插件模块卸载时会自动调用 Shutdown，进行清理
FElectraMediaOpusDecoder::Shutdown();
```
*来源：`Source/OpusDecoderElectra/Private/OpusDecoder/ElectraMediaOpusDecoder.h`*

### 进阶用法

在某些高级场景下，如果需要与 Electra 编解码器系统直接交互（例如，编写自己的媒体源或进行低层调试），你可以获取其工厂：
```cpp
#include "OpusDecoder/ElectraMediaOpusDecoder.h"
#include "ElectraDecoders/Public/IElectraCodecFactory.h"

// 获取 Opus 解码器工厂的共享指针
TSharedPtr<IElectraCodecFactory, ESPMode::ThreadSafe> Factory = FElectraMediaOpusDecoder::CreateFactory();

if (Factory.IsValid())
{
    // 工厂可以用来查询支持的编解码器信息，或在自定义流程中创建解码器
    // 具体的使用取决于 IElectraCodecFactory 接口的定义和你的自定义播放流程
}
```

## Demo 示例

这是一个最小的、演示如何集成和初始化解码器插件的 C++ 模块示例。通常，这些操作在插件加载/卸载时自动完成，无需用户代码。
```cpp
// MyGameModule.h
#pragma once

#include "Modules/ModuleManager.h"

class FMyGameModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};

// MyGameModule.cpp
#include "MyGameModule.h"

// 包含 Opus 解码器模块头文件（如果需要手动管理）
// #include "OpusDecoder/ElectraMediaOpusDecoder.h"

void FMyGameModule::StartupModule()
{
    // 此插件会自动通过 .uplugin 配置加载。
    // 这里展示的是如果你需要在自己的模块里确保其初始化，可以主动调用（但通常不需要）。
    // FElectraMediaOpusDecoder::Startup();
    UE_LOG(LogTemp, Log, TEXT("MyGameModule 启动，Opus 解码器插件应已准备就绪。"));
}

void FMyGameModule::ShutdownModule()
{
    // FElectraMediaOpusDecoder::Shutdown();
    UE_LOG(LogTemp, Log, TEXT("MyGameModule 关闭。"));
}

IMPLEMENT_PRIMARY_GAME_MODULE(FMyGameModule, MyGame, "MyGame");
```

## 模块依赖

此插件的核心依赖在 `.uplugin` 中声明。要使用它，你的模块或项目需要确保以下插件已启用：

| 模块 | 用途 |
|---|---|
| `ElectraCodecs` | 提供解码器工厂接口（`IElectraCodecFactory`）和 Electra 编解码器框架基础，是本插件运行的必需依赖。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-20 | `3ed2062b` | ElectraDecoders: modernized the decoder factory to be more usable for other clients | 现代化解码器工厂接口，提升对其他客户端的兼容性 |
| 2026-01-12 | `611dda1f` | Electra: Moved mp4 related utilities into dedicated plugin | 将MP4相关工具移至独立插件，本插件专注Opus解码 |
| 2025-11-19 | `514ccff4` | ElectraCodecs: Add information about the decoder implementation being used for decoding. | 为解码器添加实现信息，便于调试和识别 |
| 2025-08-06 | `831eeb24` | Reworked ElectraSamples, ElectraUtils and the decoder output of Electra Player | 重构 Electra 框架的基础模块和解码器输出，影响本插件的数据流 |
| 2025-06-10 | `2d174355` | Electra: Removal of the platform resource delegate and the wrapping plugin | 移除平台资源委托和包装插件，简化架构 |

### 维护评价

本插件作为 Electra 媒体框架的组成部分，**维护状态活跃**。
- **创建时间**：2023年4月，相对年轻。
- **更新频率**：最近一次更新在2026年4月，近一年内有多次功能性提交，表明其与 Electra 核心框架同步演进。
- **维护性质**：更新内容主要集中在适配 Electra 框架的内部重构、接口现代化和问题修复，而非新增功能，说明其已进入稳定期。
- **已知限制**：解码为纯软件实现，在高性能或低功耗场景下需评估CPU开销。需要`ElectraCodecs`插件支持。
- **推荐使用**：如果你的项目使用 Electra 播放器并需要播放 Opus 音频，**推荐启用此插件**。它是官方支持的、经过维护的 Opus 软件解码方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/OpusDecoderElectra)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/OpusDecoderElectra) (未在插件目录内发现独立测试文件，测试可能位于 Electra 集成测试中)