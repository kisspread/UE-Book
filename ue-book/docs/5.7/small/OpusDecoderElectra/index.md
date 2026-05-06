# Opus audio decoder for Electra

> Implements Opus audio playback with the Electra media player

| 属性 | 值 |
|---|---|
| 中文名 | Opus 音频解码器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `OpusDecoderElectra` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2023-08-04 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/OpusDecoderElectra) | |

## 用途

OpusDecoderElectra 插件为 **Electra 媒体框架** 提供了 Opus 音频格式的解码能力。Electra 是 UE5 中用于现代流媒体协议（如 HLS、DASH）的高性能播放器，而 Opus 是一种开源、低延迟的音频编解码器，广泛用于 WebRTC、直播等场景。

该插件包装了底层 Opus 解码库，将其适配为 `IElectraCodecFactory`，使得 Electra 播放器在解析媒体流时能够自动创建 Opus 解码器实例。**没有该插件，Electra 播放器将无法播放 Opus 编码的音频轨道**。

## 使用场景

- **流媒体直播**：你正在使用 Electra 播放器播放基于 DASH 或 HLS 协议的视频流，其中音频使用了 Opus 编码。
- **实时通信录制回放**：录制了 WebRTC 通信的音视频，在客户端回放时需要 Opus 解码。
- **自适应码率流**：音频通过 Opus 打包在不同分段中，需要按需解码。

简而言之：只要你的应用程序依赖 Electra 播放器，并且媒体源包含 Opus 音频轨道，就需要启用此插件。

## 蓝图用法

该插件是 **纯 C++ 后端**，不暴露任何蓝图可调用函数或蓝图资产。Electra 播放器蓝图节点（例如 `Open Source`、`Play` 等）会自动在内部调用该解码器，用户无需手动操作。

如果你需要在蓝图中使用 Electra 播放器播放包含 Opus 音频的媒体，请参考 Electra 媒体播放器的官方文档，插件本身对蓝图层透明。

## C++ 用法

### 头文件引入

```cpp
#include "OpusDecoderElectraModule.h"
#include "ElectraMediaOpusDecoder.h"
```

### 模块启动与工厂创建

插件在模块加载时（`PostEngineInit`）自动完成启动和注册。你可以通过工厂接口获取解码器创建器：

```cpp
// 启动解码器（通常由模块启动自动调用）
FElectraMediaOpusDecoder::Startup();

// 获取工厂实例
TSharedPtr<IElectraCodecFactory, ESPMode::ThreadSafe> OpusFactory = FElectraMediaOpusDecoder::CreateFactory();

// 使用工厂创建解码器实例（如果需要手动控制）
if (OpusFactory.IsValid())
{
    // 创建解码器，传入解码配置等...
    // IElectraCodecFactory::CreateDecoder(...)
}

// 关闭解码器
FElectraMediaOpusDecoder::Shutdown();
```

> 注：在 Electra 播放器的典型使用中，你不需要直接调用工厂；播放器会在内部根据媒体流编码信息自动选择并实例化合适的解码器。

### 日志类别

```cpp
UE_LOG(LogOpusElectraDecoder, Verbose, TEXT("Opus Decoder Initialized."));
```

## Demo 示例

以下是一个完整的 C++ 类，演示如何在 Electra 播放器中加载并播放带有 Opus 音频轨道的媒体流。该示例假定你已经配置好 Electra 媒体播放器并拥有有效的媒体源 URL。

### DemoMediaPlayer.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "MediaPlayer.h"
#include "MediaSource.h"

class FOpusDemoPlayer
{
public:
    void PlayOpusMedia(const FString& MediaUrl);
    void Stop();

private:
    UMediaPlayer* MediaPlayer = nullptr;
    UMediaSource* MediaSource = nullptr;
};
```

### DemoMediaPlayer.cpp

```cpp
#include "DemoMediaPlayer.h"
#include "MediaPlayer.h"
#include "MediaSource.h"
#include "OpusDecoderElectraModule.h"
#include "ElectraMediaOpusDecoder.h"

void FOpusDemoPlayer::PlayOpusMedia(const FString& MediaUrl)
{
    // 确保解码器已注册（模块自动在 PostEngineInit 时启动，但建议显式调用一次）
    FElectraMediaOpusDecoder::Startup();

    // 创建媒体播放器
    MediaPlayer = NewObject<UMediaPlayer>();
    MediaPlayer->SetLooping(false);

    // 创建媒体源（具体类型取决于协议，此处用 URL 自动推断）
    MediaSource = UMediaSource::CreateFromURL(MediaUrl);
    if (MediaSource)
    {
        MediaPlayer->OpenSource(MediaSource);
    }
}

void FOpusDemoPlayer::Stop()
{
    if (MediaPlayer)
    {
        MediaPlayer->Close();
        MediaPlayer = nullptr;
    }
    FElectraMediaOpusDecoder::Shutdown();
}
```

**注意**：实际项目中，你需要确保 `OpusDecoderElectra` 插件已启用（项目设置 → 插件），并正确链接依赖。演示仅展示通过 C++ 手动管理解码器生命周期的方法，通常情况下平台模块加载后自动处理启动和注册。

## 模块依赖

要使用此插件，你的模块需要在 `Build.cs` 中添加对以下依赖的引用（已在插件自身 `.uplugin` 中声明）：

| 模块 | 用途 |
|---|---|
| `ElectraCodecs` | 提供 `IElectraCodecFactory` 接口和编解码器管理框架 |

**无特殊依赖**（Core、Engine 等标准模块已省略）。

## 维护状态

### 近期更新

- 2025-08-06 `831eeb24` — Reworked ElectraSamples, ElectraUtils and the decoder output of Electra Player
- 2025-06-10 `2d174355` — Electra: Removal of the platform resource delegate and the wrapping plugin
- 2024-10-22 `50c3f01e` — ElectraDecoders: Added decoder specific bitstream processors
- 2024-09-26 `9dd9ac6f` — ElectraCodecs: Added dictionary parameter to receive decoder information upon instance creation.
- 2023-08-04 `85e7095f` — ElectraDecoder: Opus decoder needs to be configured with the next highest Opus-native sample rate if

### 维护评价

- **创建时间**：2023-08-04，约 2 年。
- **近期活跃度**：2025 年 8 月仍有实质性更新（重构输出处理），2025 年 6 月移除已废弃的包装插件，定期随整个 Electra 框架演进。
- **维护状态**：**活跃维护中**。插件作为 Electra 播放器的一部分，跟随主框架迭代，无废弃迹象。
- **已知限制**：仅支持特定平台（Win64、Mac、IOS、TVOS、Android、Linux），不支持服务器端。默认不启用，需手动勾选。

**推荐使用**：如果项目需要 Opus 音频支持并且依赖 Electra 播放器，强烈建议启用此插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/OpusDecoderElectra)
- [Electra 媒体播放器官方文档](https://docs.unrealengine.com/5.7/en-US/electra-media-player-for-unreal-engine/)
- [Opus 官方网站](https://opus-codec.org/)