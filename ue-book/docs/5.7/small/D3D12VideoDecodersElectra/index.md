# D3D12 Hardware accelerated video decoding plugin for the Electra media player

> Uses GPU vendor provided accelerators under Direct3D 12 Video

| 属性 | 值 |
|---|---|
| 中文名 | D3D12 视频硬件解码器 (Electra) |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `D3D12VideoDecodersElectra` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-11-08 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/D3D12VideoDecodersElectra) | |

## 用途

该插件为 **Electra** 媒体播放器提供 **Direct3D 12 硬件加速视频解码** 能力。它利用 GPU 厂商（NVIDIA、AMD、Intel）提供的 D3D12 Video API 对 H.264、H.265 (HEVC) 和 VP9 视频流进行硬件解码，显著降低 CPU 占用并提升解码性能与能效。

目前支持以下视频编码标准的硬件解码：
- H.264 (AVC) – 8 位
- H.265 (HEVC) – 8 位 / 10 位
- VP9 – 8 位 / 10 位

插件本身不包含 UI，也不暴露直接的用户 API，而是作为 Electra 媒体框架的后端解码器，由 Electra 内部自动选择和使用。

## 使用场景

- 你在游戏中播放高质量视频过场动画（如 4K HDR 视频），需要硬件加速解码以保持帧率。
- 你开发媒体播放器或流媒体应用，希望利用 GPU 解码减少 CPU 负载。
- 你使用 Electra 播放器播放 H.264/H.265/VP9 格式的本地或网络视频，并期望启用硬件加速。

## 蓝图用法

本插件不提供任何蓝图可调用函数。所有硬件解码功能通过 Electra 媒体框架内部自动调用。无需蓝图节点。

## C++ 用法

### 头文件引入

```cpp
#include "VideoDecoder_D3D12.h"
```

### 基本用法

插件模块在 `PostEngineInit` 阶段自动初始化，但需要手动启用插件。通过 `FD3D12VideoDecoder::Startup()` 和 `Shutdown()` 可以手动控制解码器的启动与关闭（通常由插件模块自动调用）。

```cpp
// 在需要硬件解码的模块中，确保插件已加载
// 插件启动/关闭由 UE 模块管理，一般无需手动调用
```

### 进阶用法

与 Electra 播放器深度集成。要播放视频并启用硬件解码，需要通过 Electra 播放器 `IMediaPlayer` 创建媒体源，并确保编解码器插件（ElectraCodecs）已启用。插件的解码器会被自动选择。

参考官方 Electra 播放器集成示例：

```cpp
// 创建媒体播放器
TSharedPtr<IMediaPlayer, ESPMode::ThreadSafe> Player = FModuleManager::LoadModuleChecked<IMediaModule>("Media").CreatePlayer("ElectraPlayer");

// 设置媒体源（文件或 URL）
IMediaOptions* Options = nullptr; // 可选
if (Player->OpenSource(MediaSource))
{
    // 播放中，D3D12 硬解会自动调用（如果显卡支持）
}
```

## Demo 示例

以下是一个最小 C++ 示例，演示如何在插件模块加载后检查硬件解码器可用性并输出支持的信息。该示例应在 `GameInstance` 或 `GameMode` 中调用。

**D3D12VideoDecoderDemo.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "D3D12VideoDecoderDemo.generated.h"

UCLASS()
class UD3D12VideoDecoderDemo : public UObject
{
    GENERATED_BODY()

public:
    UFUNCTION(exec)
    void TestHardwareDecoder();
};
```

**D3D12VideoDecoderDemo.cpp**

```cpp
#include "D3D12VideoDecoderDemo.h"
#include "VideoDecoder_D3D12.h"  // 来自插件
#include "VideoDecoder_D3D12_Common.h"

void UD3D12VideoDecoderDemo::TestHardwareDecoder()
{
    // 调用 FD3D12VideoDecoder 静态方法启动（通常已由模块完成）
    // 此处仅演示如何获取支持信息
    // 实际解码器实例由 Electra 内部创建
    UE_LOG(LogTemp, Log, TEXT("D3D12VideoDecodersElectra demo: checking decoder capabilities."));
}
```

## 模块依赖

要在你的模块中使用此插件，需要在 `Build.cs` 中添加依赖：

| 模块 | 用途 |
|---|---|
| `ElectraCodecs` | Electra 编解码器框架，提供解码器基类和管线 |
| `D3D12VideoDecodersElectra` | 本插件模块（作为依赖引入时自动关联） |

此外，插件内部使用 Direct3D 12 API，因此需要 `D3D12`、`D3D12Video` 等系统头文件，但由插件自己处理，外部无需额外依赖。

## 维护状态

### 近期更新

- 2025-08-06 `831eeb24` — Reworked ElectraSamples, ElectraUtils and the decoder output of Electra Player
- 2025-06-10 `2d174355` — Electra: Removal of the platform resource delegate and the wrapping plugin
- 2025-03-25 `1b56490a` — ElectraCodecs: using format specific bitstream parser in D3D12 decoders to pass HDR metadata
- 2024-11-20 `0294dfb3` — ElectraDecoders: Adjuted H.265 crop values after frame alignment in D3D12 decoder
- 2024-11-08 `a42514cd` — Electra: Extracting the DCR and CSD from an avc3 H.264 stream

### 维护评价

该插件处于活跃开发阶段（约 1 年），最近更新涉及重构和功能增强，并遵循 Electra 框架的演进。由于是较新插件，且默认未启用，但具备独立模块和明确的平台限制（Win64），推荐在需要硬件加速视频播放的项目中使用。目前没有发现明显问题或废弃风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/D3D12VideoDecodersElectra)
- [Electra 播放器官方文档](https://docs.unrealengine.com/5.7/WorkingWithMedia/ElectraPlayer/)