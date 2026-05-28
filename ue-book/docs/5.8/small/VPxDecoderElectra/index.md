# VPx Decoder for Electra

> Implements VP8 and VP9 playback with the Electra media player on desktop machines

| 属性 | 值 |
|---|---|
| 中文名 | VP8/9解码器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `VPxDecoderElectra` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2023-05-30 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/VPxDecoderElectra) | |

## 用途

本插件是 Epic Games 自研的媒体播放框架 Electra 的一个**解码器插件**。它的核心作用是将开源的 VP8 和 VP9 视频编解码库 (libvpx) 集成到 Electra 媒体播放器中。

**解决的问题**：Electra 播放器本身不包含 VP8/VP9 解码器，无法直接播放使用这两种编码格式（常见于 WebM 容器）的视频。本插件填补了这一空白，使得 Electra 能够在 Windows、Mac、Linux 和 iOS 桌面平台上软件解码播放 VP8/VP9 视频。

**为什么存在**：为了提供对 Web 生态中常见的 WebM 视频格式的官方支持，并确保在所有主要桌面平台上拥有一致、可靠的软件解码能力。

## 使用场景

- 你需要在 UE 项目中播放 `.webm` 格式的视频文件。
- 你的应用需要播放来自互联网（如视频点播网站）的 VP8/VP9 编码视频流。
- 你需要在 iOS 移动设备上播放 VP8/VP9 编码的视频。
- 你的目标平台没有硬件 VP8/VP9 解码器，或你需要一个统一的软件解码方案。

## 蓝图用法

此插件是一个纯运行时 C++ 模块，不包含可直接在蓝图中使用的节点。其功能通过 Electra 媒体框架在后台自动调用。开发者只需通过标准的 Electra 媒体播放器 API 加载和播放支持的媒体源（如 `webm` 文件），解码工作将由本插件透明处理。

## C++ 用法

本插件的使用被 Electra 框架完全封装。开发者通常不需要直接调用本插件的类，而是通过 Electra 的媒体源和播放器接口间接使用。以下是相关的底层接口。

### 头文件引入

```cpp
// 包含 Electra 媒体播放器的核心接口
#include "ElectraMediaFactory.h" // 通过 ElectraCodecs 插件依赖

// 如果需要引用本插件内部的特定类（通常不需要）
#include "VPxDecoderElectraModule.h" // 仅用于日志
#include "ElectraMediaVPxDecoder.h"
```

### 基本用法

在后台，Electra 框架通过工厂模式获取解码器。以下是本插件如何向 Electra 注册自身的核心逻辑。

*(来源: `Source/VPxDecoderElectra/Private/VPxDecoder/ElectraMediaVPxDecoder.h`)*

```cpp
// 1. 在插件启动时，向 Electra 编解码器管理器注册本插件提供的解码器工厂
void FElectraMediaVPxDecoder::Startup()
{
    // 内部实现会创建一个工厂对象，并将其注册到全局的 ElectraCodecs 管理器中
    // 注册后，Electra 在遇到 VP8/VP9 编码的媒体时，会调用此工厂来创建解码器实例
}

// 2. 在插件关闭时，注销工厂
void FElectraMediaVPxDecoder::Shutdown()
{
    // 反注册，清理资源
}

// 3. 工厂方法：被 Electra 框架调用以创建实际的解码器实例
TSharedPtr<IElectraCodecFactory, ESPMode::ThreadSafe> FElectraMediaVPxDecoder::CreateFactory()
{
    // 返回一个实现了 IElectraCodecFactory 接口的智能指针
    // 这个工厂对象知道如何创建 VP8 和 VP9 的解码器
    // ...
    return MakeShared<FVPxCodecFactory, ESPMode::ThreadSafe>();
}
```

### 进阶用法

对于有高级需求的用户（如自定义解码流程），可以了解其依赖关系。本插件依赖于 `ElectraCodecs` 插件提供的核心接口 `IElectraCodecFactory` 和 `IElectraCodecDecoder`。

解码器工厂（如 `FVPxCodecFactory`）需要实现以下关键方法：
- `GetSupportedFormats()`: 返回支持的编码格式（如 `EVideoCodecFormat::VP8`, `EVideoCodecFormat::VP9`）。
- `CanCreateDecoderFor(...)`: 判断是否能为给定的媒体配置创建解码器。
- `CreateDecoder(...)`: 创建并返回一个 `IElectraCodecDecoder` 实例。

解码器实例（如 `FVPxDecoder`）需要实现：
- `GetConfigurationRequirements()`: 获取解码所需的输入输出格式配置。
- `Create(...)`: 初始化解码器（加载 libvpx 库）。
- `Decode(...)`: 接收压缩数据并输出解码后的视频帧。
- `Flush()`: 重置解码器状态。

## Demo 示例

本插件是框架的一部分，使用示例主要是通过标准 Electra 流程。以下是一个假设性的、简化的内部初始化示例，展示插件如何与 Electra 交互。

**Header (Demo.h):**
```cpp
// 这是一个概念性示例，实际代码在插件内部
#pragma once
#include "ElectraCodecFactory.h"

class FVPxCodecFactory : public IElectraCodecFactory
{
public:
    // IElectraCodecFactory 接口实现
    virtual bool GetSupportedFormats(TArray<FCodecInfo>& OutSupportedFormats) const override;
    virtual TSharedPtr<IElectraCodecDecoder, ESPMode::ThreadSafe> CreateDecoder(const FCodecInfo& InCodecInfo) override;
    // ... 其他工厂接口方法
};
```

**Source (Demo.cpp):**
```cpp
#include "Demo.h"
#include "libvpx/vpx_decoder.h" // 底层调用 libvpx 库

bool FVPxCodecFactory::GetSupportedFormats(TArray<FCodecInfo>& OutSupportedFormats) const
{
    // 声明支持 VP8 和 VP9
    OutSupportedFormats.Add({EVideoCodecFormat::VP8, TEXT("VP8")});
    OutSupportedFormats.Add({EVideoCodecFormat::VP9, TEXT("VP9")});
    return true;
}

TSharedPtr<IElectraCodecDecoder, ESPMode::ThreadSafe> FVPxCodecFactory::CreateDecoder(const FCodecInfo& InCodecInfo)
{
    // 根据请求的编码格式，创建对应的解码器实例
    if (InCodecInfo.Codec == EVideoCodecFormat::VP8 || InCodecInfo.Codec == EVideoCodecFormat::VP9)
    {
        return MakeShared<FVPxDecoder, ESPMode::ThreadSafe>(InCodecInfo);
    }
    return nullptr;
}
```
**使用方式**：开发者无需编写以上代码。只需确保插件启用，然后使用 Electra 媒体源加载一个 VP8/VP9 视频即可。

## 模块依赖

从 `VPxDecoderElectra.Build.cs` 分析得出：

| 模块 | 用途 |
|---|---|
| `DirectX` | 用于在 Windows 平台上支持硬件加速或特定的渲染交互（如纹理上传）。 |

## 维护状态

该插件维护状态非常活跃，更新频繁。

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-20 | `3ed2062b` | ElectraDecoders: modernized the decoder factory to be more usable for other clients | 现代化了解码器工厂接口，使其更易于其他客户端使用。 |
| 2026-02-11 | `2639e40b` | Updated libvpx to 1.15.1, did not copy the duplicated headers layout from 1.14.1 | 更新了底层 libvpx 库至 1.15.1 版本。 |
| 2025-11-19 | `514ccff4` | ElectraCodecs: Add information about the decoder implementation being used for decoding. | 为解码过程添加了关于所使用解码器实现的信息。 |
| 2025-11-13 | `f22a1f2b` | Electra: Some codec related utility work | 进行了一些与编解码器相关的工具性工作。 |
| 2025-09-23 | `a0779f41` | ElectraDecoders: Added missing explicit ESPMode on shared pointers of D3D helper for consistency | 修复了D3D辅助类中共享指针缺少显式ESPMode的问题，保证一致性。 |

### 维护评价

- **维护状态**：**活跃维护**。最近一次更新在2026年4月，主要进行了接口现代化改造，并且持续更新底层依赖库（libvpx）。
- **创建年龄**：插件于2023年创建，相对年轻。
- **功能状态**：非实验性，但默认未启用 (`EnabledByDefault=false`)，需要手动在项目中启用。
- **稳定性**：更新记录显示，近期工作多为改进、更新和一致性修复，表明插件已进入稳定迭代期。
- **推荐度**：**推荐使用**。对于需要在UE中播放WebM/VP8/VP9视频的项目，这是一个官方且维护良好的解决方案。由于默认未启用，使用时需在 `.uproject` 文件或编辑器中手动启用该插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/VPxDecoderElectra)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/VPxDecoderElectra/Tests) (如果存在)