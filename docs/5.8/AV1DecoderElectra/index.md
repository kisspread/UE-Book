# AV1 software decoder for Electra

> Enables decoding of AV1 encoded videos with the Electra media player

| 属性 | 值 |
|---|---|
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AV1DecoderElectra` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-11-03 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AV1DecoderElectra) | |

## 用途

此插件为 Unreal Engine 的 Electra 媒体播放器框架提供了一个**软件实现的 AV1 视频解码器**。它的核心作用是作为 `ElectraCodecs` 插件的一个解码器工厂，在系统没有硬件 AV1 解码能力（或硬件解码器不可用/不兼容）时，提供纯 CPU 的软件解码方案，从而确保 AV1 编码的视频内容能够在支持的平台（Win64, Linux）上被播放。

## 使用场景

- 你需要在 Windows 或 Linux 平台上播放 AV1 编码的视频文件（例如 .mp4, .webm），但目标机器的显卡或驱动不支持硬件 AV1 解码。
- 你正在开发一个对视频格式兼容性要求较高的应用，需要确保 AV1 这种新兴高效编码格式的软件回退方案。
- 你正在使用 Electra 媒体播放器，并希望扩展其解码能力以支持 AV1。

## 蓝图用法

此插件是一个纯运行时模块，其主要功能通过 `ElectraCodecs` 框架进行注册和调用，**不直接暴露任何蓝图可调用的函数或属性**。AV1 解码器的启用和使用由 Electra 媒体播放器在内部根据视频流的编码格式自动处理。

## C++ 用法

此插件的 C++ 接口主要用于在 `ElectraCodecs` 框架内注册解码器工厂。对于插件使用者而言，通常无需直接调用其 API，解码过程由 Electra 播放器自动管理。以下是其内部接口的说明。

### 头文件引入

```cpp
// 通常不需要直接包含此插件的头文件，除非你需要手动管理其生命周期。
// 解码器工厂通过 ElectraCodecs 框架自动发现和使用。
#include "AV1DecoderElectraModule.h"
```

### 基本用法

插件模块在加载时会自动向 `ElectraCodecs` 注册其解码器工厂。以下代码展示了其内部的注册逻辑（摘自模块实现，非用户直接调用）。

```cpp
// 模块启动时注册解码器工厂
void FAV1DecoderElectraModule::StartupModule()
{
    FElectraMediaAV1Decoder::Startup();
}

// 模块关闭时注销
void FAV1DecoderElectraModule::ShutdownModule()
{
    FElectraMediaAV1Decoder::Shutdown();
}
```

### 进阶用法

解码器工厂的创建和使用由 `ElectraCodecs` 框架管理。当 Electra 播放器需要一个 AV1 解码器时，它会查询所有已注册的工厂。`FElectraMediaAV1Decoder::CreateFactory()` 静态方法负责返回一个实现了 `IElectraCodecFactory` 接口的工厂实例。

```cpp
// 由 ElectraCodecs 框架调用，获取 AV1 解码器工厂
TSharedPtr<IElectraCodecFactory, ESPMode::ThreadSafe> FElectraMediaAV1Decoder::CreateFactory()
{
    // 内部会创建并返回一个用于实例化软件 AV1 解码器的工厂
    // 具体实现依赖于底层的 libdav1d 或其他软件解码库
    return MakeShared<FElectraMediaAV1DecoderFactory, ESPMode::ThreadSafe>();
}
```

## Demo 示例

此插件作为 Electra 解码器框架的一部分，其使用是透明的。以下是一个最小化的示例，展示如何确保插件被正确加载和初始化（通常由引擎自动完成）。

```cpp
// MyMediaModule.h
#pragma once
#include "Modules/ModuleManager.h"

class FMyMediaModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

```cpp
// MyMediaModule.cpp
#include "MyMediaModule.h"
#include "AV1DecoderElectraModule.h" // 引入插件模块头文件以访问其日志类别等

#define LOCTEXT_NAMESPACE "FMyMediaModule"

void FMyMediaModule::StartupModule()
{
    // 此插件模块会自行启动，这里可以添加依赖于它的逻辑
    UE_LOG(LogAV1ElectraDecoder, Log, TEXT("AV1 Decoder for Electra is available."));
}

void FMyMediaModule::ShutdownModule()
{
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyMediaModule, MyMedia)
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `DirectX` | 提供底层图形和媒体相关的头文件与库，可能用于某些优化的解码路径或与硬件交互。 |

## 维护状态

### 近期更新

- 2026-04-20 `3ed2062b` ElectraDecoders: 对解码器工厂进行了现代化改造，使其对其他客户端更加易用。
- 2025-11-19 `514ccff4` ElectraCodecs: 添加了关于正在使用的解码器实现的信息。
- 2025-11-04 `4d60ad68` ElectraCodec: 重命名了 AV1 解码器工厂。
- 2025-11-04 `2d22420d` ElectraCodecs: 为 x86_64 Linux 平台添加了 AV1 软件解码支持。
- 2025-11-03 `ca937255` ElectraCodecs: 添加了软件 AV1 解码器插件。

### 维护评价

该插件近期处于**稳定活跃**的维护状态。从2025年11月集中添加核心功能（AV1软件解码）到2026年4月进行架构优化，更新持续且目的明确，表明开发团队在积极完善其功能和可用性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AV1DecoderElectra)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Tests/Media/Electra)