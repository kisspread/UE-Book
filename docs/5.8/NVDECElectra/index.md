# NVDEC hardware decoder support for Electra

> Adds codecs from the NVIDIA Media Codec SDK for use with Electra. Which codecs are supported depends on your GPU.
> Requires D3D12.

| 属性 | 值 |
|---|---|
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NVDECElectra` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-11-13 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/NVDECElectra) | |

## 用途

该插件为 Unreal Engine 的 Electra 媒体播放框架提供了基于 NVIDIA GPU 的硬件视频解码支持。它通过集成 NVIDIA Media Codec SDK (NVDEC)，将 H.264、HEVC 等视频编解码器的解码工作从 CPU 卸载到 NVIDIA GPU 上，从而显著降低 CPU 负载，提高高分辨率、高帧率视频的播放性能和能效。该插件是 Electra 框架的一个可选解码器后端。

## 使用场景

- 你需要在 Windows 平台上播放 4K、8K 或高帧率视频，并希望减轻 CPU 压力。
- 你的应用程序需要同时播放多个视频流（例如多路监控画面），使用 GPU 硬件解码可以避免 CPU 成为瓶颈。
- 你在开发对功耗敏感的应用（如笔记本电脑或移动设备上的应用），GPU 解码通常比 CPU 解码更节能。
- 你需要低延迟的视频解码，例如用于实时视频会议或云游戏串流。

## 蓝图用法

该插件作为 Electra 框架的底层解码器实现，**没有暴露任何蓝图可调用的节点或属性**。其功能通过 Electra 媒体播放器在内部自动调用。

## C++ 用法

该插件的核心功能通过 `FElectraMediaNVDECDecoder` 类提供，通常由 Electra 框架内部管理，开发者无需直接调用。但了解其接口有助于理解工作原理。

### 头文件引入

```cpp
#include "NVDEC/ElectraMediaNVDEC.h"
```

### 基本用法

该插件的生命周期由模块系统管理。以下是其核心接口的说明（通常由 Electra 内部使用）：

```cpp
// 在模块启动时（例如 FNVDECElectraModule::StartupModule），调用此静态方法注册 NVDEC 解码器工厂。
FElectraMediaNVDECDecoder::Startup();

// 在模块关闭时（例如 FNVDECElectraModule::ShutdownModule），调用此静态方法进行清理。
FElectraMediaNVDECDecoder::Shutdown();

// 创建一个 NVDEC 解码器工厂实例。Electra 框架会调用此方法来获取解码能力。
TSharedPtr<IElectraCodecFactory, ESPMode::ThreadSafe> Factory = FElectraMediaNVDECDecoder::CreateFactory();
```

### 进阶用法

作为运行时插件，其主要价值在于被 Electra 框架自动发现和使用。开发者需要做的是：
1.  确保项目启用了 `NVDECElectra` 插件。
2.  确保目标平台（Win64）安装了支持 NVDEC 的 NVIDIA 显卡驱动。
3.  使用标准的 Electra 媒体播放器 API（如 `UMediaPlayer`）播放视频。当播放 H.264 或 HEVC 内容时，Electra 会自动选择可用的 NVDEC 解码器。

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何在模块中集成 NVDEC 解码器的启动与关闭。请注意，实际项目中通常由插件模块自身完成此操作。

**NVDECIntegrationDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"

class FNVDECIntegrationDemo
{
public:
    static void Initialize();
    static void Deinitialize();
};
```

**NVDECIntegrationDemo.cpp**
```cpp
#include "NVDECIntegrationDemo.h"
#include "NVDEC/ElectraMediaNVDEC.h"

void FNVDECIntegrationDemo::Initialize()
{
    // 注册 NVDEC 解码器工厂到 Electra 系统
    FElectraMediaNVDECDecoder::Startup();
}

void FNVDECIntegrationDemo::Deinitialize()
{
    // 注销 NVDEC 解码器工厂
    FElectraMediaNVDECDecoder::Shutdown();
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `DirectX` | 提供 DirectX 基础头文件和库。 |
| `D3D12RHI` | 提供 Direct3D 12 渲染硬件接口，NVDEC 解码器需要通过 D3D12 进行 GPU 资源管理和命令提交。 |

## 维护状态

### 近期更新

- 2026-04-20 `3ed2062b` Electra解码器：对解码器工厂进行现代化改造，使其对其他客户端更易用。
- 2026-04-14 `35e60df1` 将UE_LOG迁移至UE_LOGF。
- 2026-02-04 `653786a3` Electra：移除了无用代码，并在视频解码器实现获取错误时添加了上游错误报告。
- 2025-11-19 `514ccff4` ElectraCodecs：添加了关于正在使用的解码器实现的信息。
- 2025-11-13 `956ea8af` ElectraCodecs：将constexpr改为宏，以解决Clang编译器报错值不恒定的问题。

### 维护评价

该插件的维护状态活跃且稳定。在约五个月的时间内有持续的提交，内容聚焦于代码质量提升、错误处理优化和编译器兼容性修复，表明其处于积极的维护和改进周期中。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/NVDECElectra)