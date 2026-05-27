# RTSP Media

> Real-time media streaming via the RTSP protocol

| 属性 | 值 |
|---|---|
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `RTSPMedia` (Runtime), `RTSPMediaEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-03-20 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/RTSPMedia) | |

## 用途

RTSPMedia 插件为 Unreal Engine 提供了通过 RTSP（Real Time Streaming Protocol）协议接收实时视频流的能力。它解决的核心问题是：**将 IP 摄像头、流媒体服务器等 RTSP 源的 H.264 视频流接入 UE5 引擎**，用于监控画面叠加、远程视频渲染、安防可视化等场景。

该插件的实现架构包含以下关键组件：

- **RTSP 客户端**（`FRtspClient`）：在独立工作线程上处理 RTSP 协议握手（OPTIONS → DESCRIBE → SETUP → PLAY），支持 TCP 交织传输模式
- **RTP 抖动缓冲区**（`FRtpJitterBuffer` + `FRtpJitterEstimator`）：自动适应网络抖动，平滑 RTP 包的到达间隔，为解码器提供稳定的数据流
- **H.264 解包器**（`FRtpH264Depacketizer`）：处理 RFC 6184 定义的三种 H.264 RTP 包格式（单 NAL、STAP-A 聚合、FU-A 分片），重组完整的 NAL 单元
- **H.264 解码器**（`FRtpDecoder`）：基于 Electra 解码框架，在独立线程上执行硬件加速的 H.264 解码
- **自动重连机制**：连接失败后按指数退避策略自动重试，适用于不稳定的网络环境

与 UE5 内置的其他 Media Source（如 WmfMedia、AvfMedia）不同，RTSPMedia 专注于网络流媒体场景，不处理本地文件播放。

## 使用场景

- 你需要在 UE5 中显示 RTSP IP 摄像头的实时画面 → 用 RTSPMedia
- 你在做安防监控可视化项目，需要将多路摄像头流接入 3D 场景 → 用 RTSPMedia
- 你需要从流媒体服务器（如 GStreamer、FFmpeg 推流）接收 H.264 视频 → 用 RTSPMedia
- 你需要低延迟的远程视频渲染（如远程桌面、远程协作）→ 用 RTSPMedia，调整抖动缓冲区参数

## 蓝图用法

RTSPMedia 的蓝图接口主要通过 `URtspMediaSource` 资产暴露。该类继承自 `UBaseMediaSource`，可在编辑器中创建和配置，然后赋给 `MediaPlayer` 组件使用。

### 核心属性

| 属性 | 类型 | 说明 | 所在类 |
|---|---|---|---|
| `Host` | `FString` | RTSP 服务器主机名或 IP 地址 | `URtspMediaSource` |
| `Port` | `int32` | RTSP 服务器端口（默认 8554） | `URtspMediaSource` |
| `Path` | `FString` | 流路径（如 `/live/stream1`） | `URtspMediaSource` |
| `SocketBufferSizeKb` | `int32` | Socket 缓冲区大小（KB），高码率流建议增大 | `URtspMediaSource` |
| `RequestTimeoutSeconds` | `float` | RTSP 请求超时时间（秒） | `URtspMediaSource` |
| `bAutoReconnect` | `bool` | 是否启用自动重连 | `URtspMediaSource` |
| `MinReconnectDelaySeconds` | `float` | 最小重连延迟（秒） | `URtspMediaSource` |
| `MaxReconnectDelaySeconds` | `float` | 最大重连延迟（秒） | `URtspMediaSource` |
| `MaxReconnectAttempts` | `int32` | 最大重连次数（0 = 无限重试） | `URtspMediaSource` |
| `bJitterBufferAutoAdjust` | `bool` | 是否自动调整抖动缓冲区深度 | `URtspMediaSource` |
| `JitterBufferDepthMs` | `int32` | 静态抖动缓冲区深度（ms） | `URtspMediaSource` |
| `JitterBufferObservationWindowSeconds` | `float` | 抖动观测窗口时长（秒） | `URtspMediaSource` |
| `MaxFragmentBufferSizeMb` | `int32` | NAL 分片重组缓冲区上限（MB） | `URtspMediaSource` |
| `DecoderBufferSize` | `int32` | 解码器重排序缓冲区帧数 | `URtspMediaSource` |
| `DecoderPollIntervalMs` | `int32` | 解码器输出轮询间隔（ms） | `URtspMediaSource` |
| `bProvideCpuBuffer` | `bool` | 是否提供 CPU 端像素缓冲区 | `URtspMediaSource` |

### 使用示例（蓝图描述）

1. **创建 Media Source 资产**：在 Content Browser 中右键 → Media → RTSP Media Source
2. **配置连接参数**：设置 Host（如 `192.168.1.100`）、Port（如 `8554`）、Path（如 `/stream1`）
3. **创建 MediaPlayer 资产**：在 Content Browser 中右键 → Media → Media Player，勾选 "Video Output Media Texture"
4. **打开流**：在蓝图中调用 MediaPlayer 的 `Open Source` 节点，传入创建的 RTSP Media Source
5. **渲染画面**：将 Media Texture 赋给 Material，应用到 Static Mesh 或 Media Texture Widget 上

典型蓝图流程：
```
[BeginPlay] → [Create URtspMediaSource (或使用预创建的资产)]
            → [Set Host = "192.168.1.100"]
            → [Set Path = "/live/stream1"]
            → [MediaPlayer → Open Source (RtspMediaSource)]
            → [MediaTexture → 赋给材质/UMG]
```

## C++ 用法

### 头文件引入

```cpp
#include "RtspMediaSource.h"
```

### 基本用法

通过 C++ 创建和配置 RTSP Media Source，然后用 Media Framework API 打开流：

```cpp
#include "RtspMediaSource.h"
#include "MediaPlayer.h"
#include "MediaTexture.h"

// 创建 RTSP Media Source
URtspMediaSource* RtspSource = NewObject<URtspMediaSource>();
RtspSource->Host = TEXT("192.168.1.100");
RtspSource->Port = 8554;
RtspSource->Path = TEXT("/live/stream1");

// 配置自动重连
RtspSource->bAutoReconnect = true;
RtspSource->MinReconnectDelaySeconds = 2.0f;
RtspSource->MaxReconnectDelaySeconds = 30.0f;
RtspSource->MaxReconnectAttempts = 0; // 无限重试

// 打开流
UMediaPlayer* MediaPlayer = /* 获取或创建 MediaPlayer */;
MediaPlayer->OpenSource(RtspSource);
```

### 进阶用法

通过 URL 字符串直接打开，支持通过 Media Options 传递额外参数：

```cpp
#include "RtspMediaSource.h"
#include "MediaPlayer.h"

// 也可以通过 URL 直接打开
UMediaPlayer* MediaPlayer = /* 获取或创建 MediaPlayer */;

// 使用 OpenUrl 方式（需要 Media Source 已配置好）
URtspMediaSource* RtspSource = NewObject<URtspMediaSource>();
RtspSource->Host = TEXT("10.0.0.50");
RtspSource->Port = 554;
RtspSource->Path = TEXT("/h264/ch1/main/av_stream");

// 针对高码率 4K 流优化配置
RtspSource->SocketBufferSizeKb = 2048;
RtspSource->RequestTimeoutSeconds = 10.0f;
RtspSource->MaxFragmentBufferSizeMb = 32;
RtspSource->DecoderBufferSize = 1; // 最低延迟，无 B 帧

// 抖动缓冲区：手动配置低延迟模式
RtspSource->bJitterBufferAutoAdjust = false;
RtspSource->JitterBufferDepthMs = 100; // 100ms 缓冲

// CPU 缓冲区：用于像素级读取（如 OpenCV 处理）
RtspSource->bProvideCpuBuffer = true;

MediaPlayer->OpenSource(RtspSource);
```

## Demo 示例

以下是一个最小可编译示例，在 Actor 中打开 RTSP 流并监听状态变化：

### RtspStreamActor.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "RtspStreamActor.generated.h"

class UMediaPlayer;
class UMediaTexture;
class URtspMediaSource;

UCLASS()
class ARtspStreamActor : public AActor
{
    GENERATED_BODY()

public:
    ARtspStreamActor();

    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    /** RTSP 服务器地址 */
    UPROPERTY(EditAnywhere, Category = "RTSP")
    FString Host = TEXT("192.168.1.100");

    /** RTSP 端口 */
    UPROPERTY(EditAnywhere, Category = "RTSP")
    int32 Port = 8554;

    /** 流路径 */
    UPROPERTY(EditAnywhere, Category = "RTSP")
    FString Path = TEXT("/live/stream1");

    /** Media Player 组件 */
    UPROPERTY(VisibleAnywhere, Category = "RTSP")
    TObjectPtr<UMediaPlayer> MediaPlayer;

    /** Media Texture 组件 */
    UPROPERTY(VisibleAnywhere, Category = "RTSP")
    TObjectPtr<UMediaTexture> MediaTexture;

private:
    UFUNCTION()
    void OnMediaOpened(FString OpenedUrl);

    UFUNCTION()
    void OnMediaOpenFailed(FString FailedUrl);

    UPROPERTY()
    TObjectPtr<URtspMediaSource> RtspSource;
};
```

### RtspStreamActor.cpp

```cpp
#include "RtspStreamActor.h"
#include "RtspMediaSource.h"
#include "MediaPlayer.h"
#include "MediaTexture.h"

ARtspStreamActor::ARtspStreamActor()
{
    PrimaryActorTick.bCanEverTick = false;

    MediaPlayer = CreateDefaultSubobject<UMediaPlayer>(TEXT("MediaPlayer"));
    MediaTexture = CreateDefaultSubobject<UMediaTexture>(TEXT("MediaTexture"));
    MediaTexture->SetMediaPlayer(MediaPlayer);
}

void ARtspStreamActor::BeginPlay()
{
    Super::BeginPlay();

    // 创建 RTSP Media Source
    RtspSource = NewObject<URtspMediaSource>(this);
    RtspSource->Host = Host;
    RtspSource->Port = Port;
    RtspSource->Path = Path;
    RtspSource->bAutoReconnect = true;
    RtspSource->MaxReconnectAttempts = 0;

    // 绑定回调
    MediaPlayer->OnMediaOpened.AddDynamic(this, &ARtspStreamActor::OnMediaOpened);
    MediaPlayer->OnMediaOpenFailed.AddDynamic(this, &ARtspStreamActor::OnMediaOpenFailed);

    // 打开流
    if (!MediaPlayer->OpenSource(RtspSource))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to open RTSP source: %s:%d%s"), *Host, Port, *Path);
    }
}

void ARtspStreamActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (MediaPlayer)
    {
        MediaPlayer->Close();
    }
    Super::EndPlay(EndPlayReason);
}

void ARtspStreamActor::OnMediaOpened(FString OpenedUrl)
{
    UE_LOG(LogTemp, Log, TEXT("RTSP stream opened: %s"), *OpenedUrl);
}

void ARtspStreamActor::OnMediaOpenFailed(FString FailedUrl)
{
    UE_LOG(LogTemp, Warning, TEXT("RTSP stream failed to open: %s"), *FailedUrl);
}
```

## 模块依赖

从插件的 `.uplugin` 声明的插件依赖和源码头文件推断：

| 模块 | 用途 |
|---|---|
| `ElectraCodecs` | H.264 硬件解码器框架（`IElectraDecoder`、`IElectraCodecFactory`） |
| `MediaIOFramework` | 媒体 IO 基础设施 |
| `MediaPlayerEditor` | Media Player 编辑器集成（RTSPMediaEditor 模块依赖） |
| `MediaAssets` | `FMediaSamples`、`FElectraTextureSample` 等媒体资产类型 |

无特殊依赖（仅标准 Core/Engine/Slate 等 + 上述媒体框架模块）。

## 维护状态

### 近期更新

- 2026-04-20 `3ed2062b` ElectraDecoders: modernized the decoder factory to be more usable for other clients
- 2026-04-14 `35e60df1` Migrate UE_LOG to UE_LOGF.
- 2026-04-10 `e18acf19` More unreachable code warning fixes
- 2026-03-25 `160bc52a` [RTSPMedia] Enable bProvideCpuBuffer by default
- 2026-03-20 `1330a56b` [RTSPMedia] Add Provide CPU buffer option

### 维护评价

- **创建时间**：2026-03-20，全新插件
- **实验性标记**：`IsExperimentalVersion=true`，`EnabledByDefault=false`——需要在 Project Settings → Plugins 中手动启用
- **当前状态**：初始版本，API 可能发生破坏性变更
- **已知限制**：
  - 仅支持 **TCP 交织传输**模式（`ERtspMediaTransportProtocol::TCP`），不支持 UDP
  - 仅支持 **H.264 视频编解码器**，不支持 H.265/HEVC 或其他编码格式
  - `TransportProtocol` 属性在蓝图中标记为 `Hidden`，用户无法切换
  - 无音频轨道支持（SDP 解析器支持 AAC 参数解析，但解码管线仅实现 H.264）
- **推荐程度**：作为实验性插件，适合原型开发和内部测试。生产环境使用需关注后续版本的 API 稳定性。

⚠️ **注意**：该插件标记为实验性且默认禁用，Epic 可能在未来版本中修改或移除此功能。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/RTSPMedia)
- [官方文档](https://docs.unrealengine.com/en-US/InteractiveExperiences/AudioVideo/AssetsAndPlayers/)（Media Framework 通用文档）