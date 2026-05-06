# HAP Decoder for Electra

> Implements video playback of the HAP Codec. HAP is a high performance, high resolution codec that runs on the GPU.

| 属性 | 值 |
|---|---|
| 中文名 | HAP解码器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `HAPDecoderElectra` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-10-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/HAPDecoderElectra) | |

## 用途

该插件为 [Electra 媒体播放器框架](https://docs.unrealengine.com/5.7/en-US/electra-media-player-in-unreal-engine/) 提供 **HAP 编码格式**的视频解码能力。HAP 是一种专为实时回放设计的 GPU 加速编解码器，能够高效解码高分辨率（如 4K/8K）视频，同时保持低 CPU 占用。插件通过注册一个解码器工厂到 Electra 系统，使 Electra 播放器能够播放 .mov 等容器中的 HAP 视频流。

**为什么存在？**  
Electra 本身不内置 HAP 解码器，需要独立插件来支持该专业格式。该插件填补了这一空白，主要服务于需要实时播放高分辨率、低延迟视频内容的项目，例如虚拟制作、交互式安装、多媒体展览。

## 使用场景

- **虚拟制片**：实时播放 CG 背景视频或 LED 墙内容，HAP 可提供极低的解码延迟。
- **交互式体验**：在展会、博物馆中播放超高清视频，要求帧率稳定且不拖累主线程。
- **影视前期预览**：在 UE 中直接预览编辑好的 HAP 视频序列，无需转码。
- **媒体服务器集成**：搭配 Electra 播放器构建分发系统，支持 HAP 源。

## 蓝图用法

本插件是纯 C++ 运行时模块，**不暴露任何蓝图可调用函数或可编辑属性**。所有注册与解码流程由 Electra 系统在后台自动处理，无需用户编写蓝图逻辑。只需在项目设置中启用该插件，并确保视频文件为 HAP 编码即可。

## C++ 用法

安装插件后，C++ 代码中无需手动调用解码器相关 API。插件的模块启动时（`PostEngineInit`）会自动调用 `FElectraMediaHAPDecoder::Startup()` 向 Electra 注册解码器。当你使用 `IMediaPlayer` 或 `FMediaPlayer` 播放 .mov 文件时，Electra 会自动选择 HAP 解码器（如果视频流为 HAP 编码）。

### 头文件引入

```cpp
// 通常情况下不需要直接包含插件头文件
// 若需要手动管理生命周期，可包含：
#include "HAPDecoder/ElectraMediaHAPDecoder.h"
```

### 基本用法

```cpp
// 文件：Source/HAPDecoderElectra/Private/HAPDecoderElectraModule.cpp
// 模块启动时自动注册，如下代码由模块内部调用：
FElectraMediaHAPDecoder::Startup();
// 模块关闭时：
FElectraMediaHAPDecoder::Shutdown();
```

用户代码中仅需通过标准媒体播放流程加载 HAP 文件：

```cpp
// 示例：使用 Media Player 播放 HAP 视频
#include "MediaPlayer.h"
#include "MediaSource.h"

UMediaPlayer* MediaPlayer = CreateObject<UMediaPlayer>();
UMediaSource* MediaSource = CreateObject<UMediaSource>(); // 或从资产加载
MediaSource->FilePath = TEXT("/Game/Videos/Sample_HAP.mov");
MediaPlayer->OpenSource(MediaSource);
MediaPlayer->Play();
```

### 进阶用法

由于解码本身对用户透明，进阶用法主要集中在 **判断是否成功使用 HAP 解码器** 以及 **性能调优**。可通过 Electra 提供的日志类别 `LogHAPElectraDecoder` 查看解码信息：

```cpp
// 在任意位置输出 HAP 解码器状态
UE_LOG(LogHAPElectraDecoder, Log, TEXT("HAP decoder is %s"), 
       FElectraMediaHAPDecoder::IsRegistered() ? TEXT("registered") : TEXT("not registered"));
```

> 注意：`IsRegistered()` 非公开 API（由模块内部管理），实际应通过 Electra 的媒体播放器回调获取解码信息。

## Demo 示例

以下为一个最小的、可在 C++ 项目中使用的播放 HAP 视频的 GameInstance 子类示例。假设已完成插件启用并放置 HAP 视频文件。

**DemoHAPPlayer.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Engine/GameInstance.h"
#include "MediaPlayer.h"
#include "MediaSource.h"
#include "DemoHAPPlayer.generated.h"

UCLASS()
class UDemoHAPPlayer : public UGameInstance
{
    GENERATED_BODY()

public:
    virtual void Init() override;
    virtual void Shutdown() override;

    UFUNCTION(BlueprintCallable, Category = "HAP Demo")
    void PlayHAPVideo(const FString& FilePath);

private:
    UPROPERTY()
    UMediaPlayer* MediaPlayer;
};
```

**DemoHAPPlayer.cpp**
```cpp
#include "DemoHAPPlayer.h"
#include "MediaSource.h"
#include "FileMediaSource.h"

void UDemoHAPPlayer::Init()
{
    Super::Init();
    MediaPlayer = NewObject<UMediaPlayer>(this);
    // 可设置循环等属性
    MediaPlayer->SetLooping(true);
}

void UDemoHAPPlayer::Shutdown()
{
    if (MediaPlayer)
    {
        MediaPlayer->Close();
    }
    Super::Shutdown();
}

void UDemoHAPPlayer::PlayHAPVideo(const FString& FilePath)
{
    if (!MediaPlayer)
    {
        UE_LOG(LogTemp, Error, TEXT("MediaPlayer not initialized"));
        return;
    }

    // 创建文件媒体源
    UFileMediaSource* FileSource = NewObject<UFileMediaSource>();
    FileSource->SetFilePath(FilePath);
    FileSource->PrecacheFile = true; // 预缓存提高性能

    if (!MediaPlayer->OpenSource(FileSource))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to open media source: %s"), *FilePath);
    }
    else
    {
        MediaPlayer->Play();
    }
}
```

## 模块依赖

要使用此插件，你的模块的 `Build.cs` 需要包含以下依赖（标准依赖已省略）：

| 模块 | 用途 |
|---|---|
| `ElectraCodecs` | 提供 Electra 编解码器框架注册接口 |
| `DirectX` | 通过 DirectX 11/12 实现 GPU 端 HAP 解码（仅 Win64/Mac 平台） |

> **注意**：`DirectX` 通常由引擎自动链接，无需手动添加。`ElectraCodecs` 插件必须启用（.uplugin 中已声明依赖）。

## 维护状态

### 近期更新

```
- 2025-09-24 f946068 — ElectraDecoders: Added missing explicit ESPMode on shared pointers of D3D helper for consistency
- 2025-09-23 569bf4e — ElectraDecoders: Passing any low level D3D12 failures up for better error reporting
- 2025-08-06 831eeb2 — Reworked ElectraSamples, ElectraUtils and the decoder output of Electra Player
- 2025-06-10 2d17435 — Electra: Removal of the platform resource delegate and the wrapping plugin
- 2024-10-22 50c3f01 — ElectraDecoders: Added decoder specific bitstream processors
```

### 维护评价

- **创建时间**：2024-10-22（约 1 年）
- **活跃度**：2025 年有数次功能性更新（D3D 错误处理、采样输出重构等），属于活跃维护。
- **接口稳定性**：目前仅提供 `Startup/Shutdown`，且由模块自动管理，无需用户干预。
- **平台限制**：仅支持 Win64 和 Mac（不适用于 Linux/Android/iOS）。
- **推荐使用**：如果项目需要在 Electra 播放器中播放 HAP 视频，强烈推荐启用此插件。HAP 解码效率远高于 CPU 解码方案。

## 相关链接

- [源码（5.7 分支）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/HAPDecoderElectra)
- [官方 Electra 媒体播放器文档](https://docs.unrealengine.com/5.7/en-US/electra-media-player-in-unreal-engine/)
- [HAP 编解码器官方介绍](https://hap.video/)
- [测试用例（位于 ElectraDecoders 测试中）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/ElectraCodecs/Tests)