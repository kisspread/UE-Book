# Apple ProRes Decoder for Electra

> Implements video playback of Apple ProRes encoded videos. Apple ProRes is a high quality, lossy video compression format.

| 属性 | 值 |
|---|---|
| 中文名 | ProRes 解码器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AppleProResDecoderElectra` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-08-06 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AppleProResDecoderElectra) | |

## 用途

该插件为 **Electra 媒体播放器**（`ElectraCodecs` 框架）添加了对 Apple ProRes 编码视频的硬件/软件解码能力。  
Apple ProRes 是一种高质量、有损的视频压缩格式，广泛应用于专业视频编辑和后期制作领域。  
此插件的存在使得基于 Electra 播放器的项目（如媒体播放器、过场动画播放、视频纹理等）能够原生播放 `.mov` 或 `.mxf` 等封装中的 ProRes 视频流，而无需依赖第三方解码库。

## 使用场景

- **专业视频制作工具**：在 Unreal Engine 中集成素材浏览或实时预览 ProRes 视频，例如用于虚拟制片、片场回放。
- **视频纹理/UI 播放**：在关卡或 UI 中播放 ProRes 格式的高质量视频（通过 `MediaPlayer` + `MediaTexture`）。
- **影视级过场动画**：需要以极高质量播放预渲染的 ProRes 过场，保持色彩深度和解码效率。
- **跨平台工具链**：在 Win64 和 Mac 上统一使用 ProRes 素材，Mac 平台可利用原生硬件加速。

> **注意**：该插件本身不提供独立的媒体播放器功能，必须结合 Electra 媒体播放器框架（`ElectraPlayer` 插件）及 `ElectraCodecs` 解码器库使用。

## 蓝图用法

该插件不公开任何蓝图可调用函数或属性。所有功能通过 Electra 媒体播放器的配置自动启用。  
在项目设置中启用插件后，当媒体源文件为 ProRes 编码时，Electra 播放器会自动使用此解码器。

### 播放启用流程（蓝图描述）

1. 在 **项目设置 > Plugins** 中勾选 `Apple ProRes Decoder for Electra`（需要同时启用 `ElectraCodecs` 和 `Electra Player` 等基础插件）。
2. 创建一个 `MediaPlayer` 资源和一个对应的 `FileMediaSource` 或 `URLMediaSource` 指向 ProRes 文件。
3. 将 `MediaPlayer` 分配给 `MediaTexture` 或 `MediaSoundComponent`。
4. 调用 `MediaPlayer->OpenSource` 节点，播放将自动选择 ProRes 解码器。

无需手动调用任何插件专属节点。

## C++ 用法

### 头文件引入

```cpp
#include "ElectraMediaProResDecoder.h"   // 位于 Public 目录（根据源码结构推测）
```

> 实际路径需参考插件公共头文件，当前只有私有的 `ProResDecoder/ElectraMediaProResDecoder.h`，但插件未暴露任何用户 API。  
> 通常你不需要直接引用此插件，只需通过 Electra 播放器 API 播放媒体即可。

### 基本用法（初始化/关闭）

```cpp
// 模块启动时由插件内部自动调用，无需手动调用
FElectraMediaProResDecoder::Startup();
// 模块关闭时自动调用
FElectraMediaProResDecoder::Shutdown();
```

### 进阶用法

当需要在项目中强制使用 ProRes 解码器或无头测试时，可手动控制生命周期：

```cpp
// 在自定义模块的 StartupModule 中确保解码器注册
void FMyModule::StartupModule()
{
    FElectraMediaProResDecoder::Startup();
}

void FMyModule::ShutdownModule()
{
    FElectraMediaProResDecoder::Shutdown();
}
```

> 插件源码位于 `Engine/Plugins/Media/AppleProResDecoderElectra/Source/AppleProResDecoderElectra/Private/ProResDecoder/ElectraMediaProResDecoder.h`

### 日志类别

```cpp
#include "AppleProResDecoderElectraModule.h"

UE_LOG(LogProResElectraDecoder, Log, TEXT("Decoding ProRes frame..."));
// 日志类别：LogProResElectraDecoder
```

## Demo 示例

由于插件提供的是内部解码器，不暴露独立 API，以下是一个基于 Electra 媒体播放器的最小 C++ 集成示例。

### MediaPlayerActor.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MediaPlayer.h"
#include "MediaTexture.h"
#include "MediaSoundComponent.h"
#include "MediaPlayerActor.generated.h"

UCLASS()
class AMediaPlayerActor : public AActor
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Media")
    UMediaPlayer* MediaPlayer;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Media")
    UMediaTexture* MediaTexture;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Media")
    UMediaSoundComponent* SoundComponent;

    UFUNCTION(BlueprintCallable, Category = "Media")
    void PlayProResFile(const FString& FilePath);

protected:
    virtual void BeginPlay() override;
};
```

### MediaPlayerActor.cpp

```cpp
#include "MediaPlayerActor.h"
#include "FileMediaSource.h"

void AMediaPlayerActor::BeginPlay()
{
    Super::BeginPlay();
    // 示例：播放在 Content/Media/ 目录下的 test_prores.mov
    PlayProResFile(TEXT("/Game/Media/test_prores.mov"));
}

void AMediaPlayerActor::PlayProResFile(const FString& FilePath)
{
    if (MediaPlayer && MediaTexture)
    {
        UFileMediaSource* Source = NewObject<UFileMediaSource>();
        Source->FilePath = FilePath;
        MediaPlayer->OpenSource(Source);
        MediaTexture->SetMediaPlayer(MediaPlayer);
        if (SoundComponent)
        {
            SoundComponent->SetMediaPlayer(MediaPlayer);
        }
        MediaPlayer->Play();
    }
}
```

> 此示例依赖 `ElectraPlayer` 插件（默认启用）和本插件（需手动启用）。

## 模块依赖

本插件的模块 `AppleProResDecoderElectra` 依赖于以下独特模块：

| 模块 | 用途 |
|---|---|
| `ElectraCodecs` | 必需，提供 Electra 解码器框架，ProRes 解码器注册其中 |
| `DirectX` (Windows) | 可选，用于 D3D12 缓冲区管理（仅在 Win64 上使用） |

**省略常见依赖**：无特殊依赖（仅标准 Core/Engine/Slate 等）。

> 注意：使用本插件的项目无需直接依赖 `AppleProResDecoderElectra`，只需依赖 `ElectraPlayer` 和 `ElectraCodecs` 即可。插件通过 `.uplugin` 的 `Plugins` 字段自动启用。

## 维护状态

### 近期更新

```
- 2025-09-24 f9460684 ElectraDecoders: Added missing explicit ESPMode on shared pointers of D3D helper for consistency
- 2025-09-23 569bf4e1 ElectraDecoders: Passing any low level D3D12 failures up for better error reporting
- 2025-08-07 2430e45d Enabling the ProRes decoder plugin for Electra on Mac
- 2025-08-06 9101d6c9 ElectraCodecs: better error handling in the ProRes decoder when DX12 buffers can't be allocated
- 2025-08-06 831eeb24 Reworked ElectraSamples, ElectraUtils and the decoder output of Electra Player
```

### 维护评价

该插件创建于 2025 年 8 月 6 日，至今不到 3 个月，属于全新插件。  
开发团队（Epic Games）持续对其进行修复和优化，包括跨平台支持（Mac 启用）、错误处理改进以及代码一致性维护。  
根据提交频率和内容，该插件目前处于 **活跃维护** 状态，推荐在需要 ProRes 播放的项目中使用。  
已知限制：不支持 Win64:arm64 架构（`PlatformArchitectureDenyList`），也不支持服务器目标平台。  

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AppleProResDecoderElectra)
- [Electra 媒体播放器文档](https://docs.unrealengine.com/5.7/en-US/electra-media-player-in-unreal-engine/)（官方文档）
- [ElectraCodecs 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/ElectraCodecs)