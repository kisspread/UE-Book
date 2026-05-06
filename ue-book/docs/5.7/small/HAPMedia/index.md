# HAP Media

> Implements video playback of the HAP Codec. HAP is a high performance, high resolution codec that runs on the GPU.

| 属性 | 值 |
|---|---|
| 中文名 | HAP 视频播放 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `HAPMedia` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-11-18 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/HAPMedia) | |

## 用途

HAP Media 是 Unreal Engine 的一个媒体解码插件，为 **WMF Media Player** 提供 HAP 视频编解码器的解码能力。HAP 是一种基于 GPU 的高性能、高分辨率编解码器，特别适合实时渲染、虚拟制片、大屏播放等对帧率和画质要求极高的场景。

该插件本身不暴露任何独立的蓝图或 C++ API，而是作为 **WmfMedia** 插件的解码扩展，在播放 `.mov` 或 `.avi` 文件中的 HAP 编码视频时自动加载使用。只需确保项目中启用了此插件和 WmfMedia，并在媒体源中配置正确的格式即可。

## 使用场景

- **实时虚拟制片 / 舞台背景视频**：HAP 格式对 GPU 友好，解码速度快，适合拼接多路 4K / 8K 视频。
- **数字标牌 / 大屏播放**：需要高帧率、低延迟的长时间循环播放。
- **受限于 CPU 性能的设备**：HAP 将解码工作交给 GPU，减轻 CPU 负担，适合 CPU 密集型场景。

## 蓝图用法

由于 HAP Media 作为底层解码器工作，不提供任何可调用的蓝图函数。使用方式为：

1. 在 **Project Settings → Plugins** 中启用 `HAP Media` 和 `WmfMedia Player` 插件。
2. 创建 `Media Player` 资产，并在 `Media Source` 中指定一个 HAP 编码的视频文件（.mov）。
3. 将 `Media Player` 连接到 `Media Texture` 或 `File Media Source`，即可在 UI 或材质中播放。

无需额外的蓝图节点。

## C++ 用法

同样，此插件不提供公开的 C++ 接口。在 C++ 中使用 HAP 视频的方式与蓝图一致：通过 `UMediaPlayer` 播放 HAP 编码的媒体源，解码器会自动选择。

如果需要强制指定解码器或用代码加载插件，可以在模块的 `StartupModule` 中确保 `HAPMedia` 被加载：

```cpp
#include "HAPMediaModule.h"       // 仅包含日志声明，无实际接口

// 无需额外代码，HAPMedia 在 WmfMedia 需要时自动初始化
```

## Demo 示例

由于插件无可调用的 API，以下示例展示如何通过 C++ 播放 HAP 视频：

**HAPVideoPlayer.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MediaPlayer.h"
#include "MediaTexture.h"
#include "HAPVideoPlayer.generated.h"

UCLASS()
class AHAPVideoPlayer : public AActor
{
    GENERATED_BODY()

public:
    AHAPVideoPlayer();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Media")
    UMediaPlayer* MediaPlayer;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Media")
    UMediaTexture* MediaTexture;

    UFUNCTION(BlueprintCallable, Category = "Media")
    void PlayHAPVideo(const FString& FilePath);
};
```

**HAPVideoPlayer.cpp**
```cpp
#include "HAPVideoPlayer.h"
#include "FileMediaSource.h"

AHAPVideoPlayer::AHAPVideoPlayer()
{
    PrimaryActorTick.bCanEverTick = false;

    MediaPlayer = CreateDefaultSubobject<UMediaPlayer>(TEXT("MediaPlayer"));
    MediaTexture = CreateDefaultSubobject<UMediaTexture>(TEXT("MediaTexture"));
    MediaTexture->SetMediaPlayer(MediaPlayer);
}

void AHAPVideoPlayer::PlayHAPVideo(const FString& FilePath)
{
    UFileMediaSource* MediaSource = NewObject<UFileMediaSource>();
    MediaSource->FilePath = FilePath;

    if (!MediaPlayer->OpenSource(MediaSource))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to open HAP video: %s"), *FilePath);
    }
}
```

需要在 `.Build.cs` 中添加依赖：`MediaAssets`（用于 `UMediaTexture` 和 `UFileMediaSource`）、`Media`、`MediaUtils`（通常已隐含）。

## 模块依赖

除了常见的 Core、Engine、Media、MediaAssets 外，本插件独特依赖如下：

| 模块 | 用途 |
|---|---|
| `WmfMedia` | 提供 Windows Media Foundation 媒体框架，HAP 解码器作为其扩展注册 |

使用本插件时，你的模块不需要额外添加 `HAPMedia` 依赖（它是运行时自动加载的），但需要确保 `WmfMedia` 可用。

## 维护状态

### 近期更新

| 日期 | Hash | 说明 |
|---|---|---|
| 2023-04-03 | `ebabab67` | 从编解码器重构任务流合并代码 |
| 2022-10-21 | `610c4676` | 将内置插件的供应商链接更新为安全协议 |
| 2022-08-15 | `a2d38616` | 修复 DX12 下 WMF Media Player 的 HAP 播放 |
| 2021-11-29 | `9e51a331` | HAP 改用外部缓冲区 |
| 2021-11-18 | `0c3be2b6` | 初始提交（合并到发布分支） |

### 维护评价

- 创建至今约 4 年，只有一次实质性功能更新（2023-04-03 的重构合并），此后无任何代码变更。
- 最近一次 commit 距今已超过 2.5 年，无 bug 修复或新特性。
- 插件使用 C++ 原生编码，代码量极少（仅 4 个源文件），维护成本低。
- **警告**：由于长时间未更新，可能无法适配最新的 UE 引擎版本或修复潜在的兼容性问题。如果项目重度依赖 HAP 播放，建议自行进行测试并准备备选方案（如通过外部解码器插件）。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/HAPMedia)
- [WmfMedia 插件（HAP 依赖）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/WmfMedia)
- [HAP 编码标准 (Vidvox)](http://hap.video/)（第三方格式说明）