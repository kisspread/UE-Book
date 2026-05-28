# Avid DNxHD® decoder for Electra

> Avid DNxHD® video decoder

| 属性 | 值 |
|---|---|
| 中文名 | DNxHD解码器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AvidDNxHDDecoderElectra` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2023-04-03 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AvidDNxHDDecoderElectra) | |

## 用途

此插件为 UE5 的 **Electra 媒体框架** 提供了 Avid DNxHD® 专业视频编解码器的解码能力。DNxHD 是专业影视后期制作和编辑领域广泛使用的中间编解码器。通过此插件，UE5 能够通过 Electra 媒体播放器解码并播放使用 DNxHD 编码的视频文件，服务于虚拟制片、离线预览、媒体资产处理等工作流。该插件默认禁用，需要手动启用。

## 使用场景

- 你正在开发一个面向影视后期或虚拟制片的项目，需要导入并播放 `.mxf` 等容器中采用 DNxHD 编码的专业视频素材。
- 你需要在 UE5 编辑器中预览或在运行时回放由专业剪辑软件（如 Avid Media Composer）输出的 DNxHD 视频。

## 蓝图用法

该插件作为 Electra 媒体框架的解码器后端，通常不直接暴露蓝图接口供用户在蓝图中显式调用。其功能由 Electra 媒体播放器在底层透明地调度使用。

### 核心节点

无直接面向用户的蓝图节点。解码器的加载和卸载由插件模块在引擎初始化阶段自动完成。

### 使用示例（蓝图描述）

用户无需在蓝图中直接操作此解码器插件。当插件启用后，在 Electra 媒体播放器的播放流程中遇到 DNxHD 编码的视频流时，会自动使用此解码器进行解码。

## C++ 用法

此插件主要作为底层解码器集成，不推荐用户在 C++ 中直接调用其内部类。其正确使用方式是通过标准的 `UMediaPlayer` 或 `UElectraMediaSource` 等 UE 媒体 API 进行媒体播放。

### 头文件引入

如果你需要访问插件的日志类别进行调试，可以引入：

```cpp
// Source/Private/AvidDNxHDDecoderElectraModule.h
#include "AvidDNxHDDecoderElectraModule.h"
```

### 基本用法

日志类别的使用示例。

```cpp
// 源文件：任何你想输出相关日志的代码中
#include "AvidDNxHDDecoderElectraModule.h"

void SomeFunction()
{
    UE_LOG(LogAvidDNxHDElectraDecoder, Log, TEXT("This is a log message related to Avid DNxHD decoding."));
}
```

*来源文件：`Source/Private/AvidDNxHDDecoderElectraModule.h`*

### 进阶用法

作为解码器插件，其核心逻辑封装在 `FElectraMediaAvidDNxHDDecoder` 中，并通过模块的 `Startup` 和 `Shutdown` 自动注册到 Electra 框架。用户通常无需直接调用这些方法。更高级的用法是参考此插件的实现，创建自定义的 Electra 解码器插件。

## Demo 示例

以下是一个最小的自定义 Electra 解码器插件的框架示例，演示了其基本结构（AvidDNxHDDecoderElectra 是同类插件的实现参考）：

**MyCustomDecoder.h**
```cpp
#pragma once
#include "CoreMinimal.h"

class FMyCustomElectraDecoder
{
public:
    static void Startup();
    static void Shutdown();
};
```

**MyCustomDecoder.cpp**
```cpp
#include "MyCustomDecoder.h"
// 需要包含 ElectraCodecs 和其他相关头文件

void FMyCustomElectraDecoder::Startup()
{
    // 在此处向 Electra 框架注册你的解码器
    // 例如：ElectraMedia::RegisterDecoder(...)
}

void FMyCustomElectraDecoder::Shutdown()
{
    // 在此处从 Electra 框架注销你的解码器
}
```

*此示例仅展示结构，实际注册/注销 API 需参考 `ElectraCodecs` 插件文档。*

## 模块依赖

| 模块 | 用途 |
|---|---|
| `DirectX` | 提供 Direct3D 相关的工具和头文件，用于可能的硬件加速解码路径。 |
| `ElectraCodecs` (插件依赖) | Electra 媒体框架的核心编解码器接口，本插件的解码器需要向此接口注册。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-20 | `3ed2062b` | ElectraDecoders: modernized the decoder factory to be more usable for other clients | 现代化解码器工厂接口，提升其他客户端的易用性。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏至新的 UE_LOGF 格式。 |
| 2026-01-21 | `7ea56be1` | CopyBuffer now always runs on the decoder thread and is no longer outsourced to a async task in orde | 将缓冲区拷贝操作固定为在解码器线程执行，不再外包给异步任务。 |
| 2025-11-19 | `514ccff4` | ElectraCodecs: Add information about the decoder implementation being used for decoding. | 添加关于解码器实现信息的日志。 |
| 2025-09-23 | `a0779f41` | ElectraDecoders: Added missing explicit ESPMode on shared pointers of D3D helper for consistency | 为 D3D 辅助对象的共享指针补充了显式的 ESPMode 参数以保持一致性。 |

### 维护评价

- **活跃维护**：该插件在最近 1 年内有多次实质性更新，包括 API 现代化、性能优化（线程模型调整）和兼容性修复。
- **状态**：作为专业媒体解码器插件，其更新与 Electra 框架的演进保持同步，目前处于**积极维护**状态。
- **推荐使用**：如果你的项目确实需要解码 Avid DNxHD 格式的视频，并且目标平台为 Windows (x64)，**可以使用**此插件。由于它默认禁用，请确保在启用后测试特定格式的兼容性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AvidDNxHDDecoderElectra)
- [依赖插件: ElectraCodecs](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraCodecs)