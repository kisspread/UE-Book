# Pixel Streaming 2

> Streaming of Unreal Engine audio and rendering to WebRTC-compatible media players such as a web browsers.

| 属性 | 值 |
|---|---|
| 中文名 | 像素流送2 |
| 分类 | Graphics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PixelStreaming2` (Runtime), `PixelStreaming2Core` (Runtime), `PixelStreaming2Editor` (Runtime), `PixelStreaming2HMD` (Runtime), `PixelStreaming2Input` (Runtime), `PixelStreaming2RTC` (Runtime), `PixelStreaming2Servers` (Runtime), `PixelStreaming2Settings` (Runtime), `EpicRtc` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-09-04 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming2) | |

## 用途

Pixel Streaming 2 是 UE5 的下一代像素流送插件，用于将 Unreal Engine 的渲染画面和音频通过 WebRTC 协议实时传输到兼容的媒体播放器（如 Web 浏览器）。这是对原版 Pixel Streaming（基于 libwebrtc）的完全重写版本。

该插件解决的核心问题：
- **远程渲染**：将 UE 应用的画面实时推送到浏览器端，客户端无需安装任何软件
- **低延迟交互**：通过 WebRTC 实现毫秒级延迟的双向通信
- **解耦的 RTC 层**：使用自研的 EpicRtc 抽象层替代直接依赖 libwebrtc，提供更清晰的架构和更好的可维护性
- **自定义编解码器**：支持插入自定义音视频编解码器
- **VR/HMD 支持**：专门的 HMD 模块处理 VR 场景下的像素流送
- **多参与者会议**：支持 MediaServer 模式和 P2P 模式

与原版 Pixel Streaming 的主要区别：
- 不依赖 libwebrtc，而是使用 EpicRtc 作为 WebRTC 抽象层
- 更模块化的架构（9 个独立模块）
- 支持 QUIC 协议（实验性）
- 更好的多人会议支持（Conference/Session/Room 层级）

## 使用场景

- 你需要将 UE 应用画面推送到浏览器供用户远程操作 → 使用 Pixel Streaming 2
- 你在做云游戏、云渲染服务 → 用 Pixel Streaming 2 替代传统串流方案
- 你需要构建多人实时协作的 Web 应用（如远程设计评审）→ 用 Pixel Streaming 2 的 P2P 或 MediaServer 模式
- 你需要在 VR 设备上进行远程渲染 → 使用 PixelStreaming2HMD 模块
- 你需要自定义视频编解码器（如使用硬件编码器）→ 通过 EpicRtc 的自定义编码器接口注入
- 你需要将原版 Pixel Streaming 迁移到更现代的架构 → 考虑迁移到 Pixel Streaming 2

## 模块架构

| 模块 | 类型 | 职责 |
|---|---|---|
| `PixelStreaming2` | Runtime | 主模块，依赖 VulkanRHI 处理图形渲染 |
| `PixelStreaming2Core` | Runtime | 核心流送逻辑和会话管理 |
| `PixelStreaming2Editor` | Runtime | 编辑器集成（注意：类型为 Runtime 而非 Editor） |
| `PixelStreaming2HMD` | Runtime | VR/HMD 设备的流送支持 |
| `PixelStreaming2Input` | Runtime | 输入处理（鼠标、键盘、触摸、手柄等远程输入） |
| `PixelStreaming2RTC` | Runtime | WebRTC 通信层，桥接 EpicRtc 和引擎 |
| `PixelStreaming2Servers` | Runtime | 信令服务器和媒体服务器管理 |
| `PixelStreaming2Settings` | Runtime | 插件设置和配置 |
| `EpicRtc` | Runtime | 第三方 WebRTC 抽象库（纯 C++，无 UE 依赖） |

## EpicRtc 架构概览

EpicRtc 是 Pixel Streaming 2 的底层 WebRTC 抽象层，采用纯 C++ 接口设计，支持跨 DLL 边界的 ABI 安全调用。其核心架构如下：

```
EpicRtcPlatformInterface          ← 顶层入口，管理所有 Conference
  └─ EpicRtcConferenceInterface   ← 会议实例，管理 Session
       └─ EpicRtcSessionInterface ← 会话，连接信令服务器，管理 Room
            └─ EpicRtcRoomInterface    ← 房间，管理参与者和媒体轨道
                 ├─ EpicRtcConnectionInterface  ← P2P/MediaServer 连接
                 ├─ EpicRtcAudioTrackInterface  ← 音频轨道
                 ├─ EpicRtcVideoTrackInterface  ← 视频轨道
                 └─ EpicRtcDataTrackInterface   ← 数据轨道
```

### 房间模式

| 模式 | 说明 |
|---|---|
| `MediaServer` | 所有媒体通过一个连接到媒体服务器，适合大规模分发 |
| `P2P` | 每个参与者独立连接，适合小规模低延迟场景 |
| `Mixed` | 混合模式，部分连接到服务器，部分 P2P |

## C++ 用法

> 注意：本插件未暴露任何 BlueprintCallable 函数，所有操作均需通过 C++ 进行。

### 头文件引入

```cpp
#include "EpicRtcPlatform.h"       // 平台初始化
#include "EpicRtcConference.h"     // 会议管理
#include "EpicRtcSession.h"        // 会话管理
#include "EpicRtcRoom.h"           // 房间管理
#include "EpicRtcConnection.h"     // 连接管理
#include "EpicRtcVideoTrack.h"     // 视频轨道
#include "EpicRtcAudioTrack.h"     // 音频轨道
#include "EpicRtcDataTrack.h"      // 数据轨道
```

### 基本用法：初始化平台并创建会议

从 `Include/epic_rtc/core/platform.h` 和 `Include/epic_rtc/core/conference.h` 提取的典型用法：

```cpp
#include "epic_rtc/core/platform.h"
#include "epic_rtc/core/conference.h"

// 1. 初始化平台
EpicRtcPlatformConfig platformConfig{};
platformConfig._memory = nullptr;    // 使用默认内存管理
platformConfig._callstack = nullptr; // 使用默认调用栈追踪

EpicRtcPlatformInterface* platform = nullptr;
EpicRtcErrorCode result = GetOrCreatePlatform(platformConfig, &platform);
if (result != EpicRtcErrorCode::Ok)
{
    UE_LOG(LogTemp, Error, TEXT("Failed to create EpicRtc platform"));
    return;
}

// 2. 配置会议参数
EpicRtcConfig config{};
config._websocketFactory = myWebSocketFactory;  // 需要实现 WebSocket 工厂
config._signallingType = EpicRtcSignallingType::Default;
config._signingPlugin = nullptr;                 // 可选：签名插件
config._migrationPlugin = nullptr;               // 可选：迁移插件
config._audioDevicePlugin = nullptr;             // 可选：音频设备插件

// 音频配置
config._audioConfig._tickAdm = false;
config._audioConfig._enableBuiltInAudioCodecs = true;
config._audioConfig._recordingSampleRate = 48000;
config._audioConfig._recordingChannels = 2;
config._audioConfig._playoutSampleRate = 48000;
config._audioConfig._playoutChannels = 2;

// 视频配置
config._videoConfig._enableBuiltInVideoCodecs = true;

// 日志配置
config._logging._level = EpicRtcLogLevel::Info;

// 统计配置
config._stats._statsCollectorCallback = myStatsCallback;
config._stats._statsCollectorInterval = 1000; // 1 秒

// 3. 创建会议
EpicRtcConferenceInterface* conference = nullptr;
result = platform->CreateConference(TEXT("MyConference"), config, &conference);
```

### 基本用法：创建会话和房间

从 `Include/epic_rtc/core/session.h` 和 `Include/epic_rtc/core/room.h` 提取：

```cpp
#include "epic_rtc/core/session.h"
#include "epic_rtc/core/room.h"

// 1. 创建会话
EpicRtcSessionConfig sessionConfig{};
// ... 配置信令服务器 URL 等

EpicRtcSessionInterface* session = nullptr;
conference->CreateSession(sessionConfig, &session);

// 2. 连接到信令服务器
session->Connect();

// 3. 创建房间
EpicRtcRoomConfig roomConfig{};
// ... 配置房间参数

EpicRtcRoomInterface* room = nullptr;
session->CreateRoom(roomConfig, &room);

// 4. 加入房间
room->Join();
```

### 进阶用法：添加媒体轨道

从 `Include/epic_rtc/core/connection.h`、`Include/epic_rtc/core/video/video_track.h`、`Include/epic_rtc/core/audio/audio_track.h` 提取：

```cpp
#include "epic_rtc/core/connection.h"
#include "epic_rtc/core/video/video_track.h"
#include "epic_rtc/core/audio/audio_track.h"

// 获取连接接口
EpicRtcConnectionInterface* connection = nullptr;
room->GetConnection(&connection);

// 添加视频源
EpicRtcVideoSource videoSource{};
// ... 配置视频源
connection->AddVideoSource(videoSource);

// 添加音频源
EpicRtcAudioSource audioSource{};
// ... 配置音频源
connection->AddAudioSource(audioSource);

// 添加数据通道
EpicRtcDataSource dataSource{};
// ... 配置数据源
connection->AddDataSource(localParticipantId, dataSource);

// 启动协商
connection->StartNegotiation();

// 推送视频帧（在观察者回调中获取到 track 后）
videoTrack->PushFrame(videoFrame);

// 推送音频帧
audioTrack->PushFrame(audioFrame);

// 推送数据帧
EpicRtcDataFrame dataFrame{};
dataFrame._data = myDataBuffer;
dataFrame._size = bufferSize;
dataFrame._binary = true;
dataTrack->PushFrame(dataFrame);
```

### 进阶用法：房间观察者（事件回调）

从 `Include/epic_rtc/core/room_observer.h` 提取：

```cpp
#include "epic_rtc/core/room_observer.h"

class MyRoomObserver : public EpicRtcRoomObserverInterface
{
public:
    void OnRoomStateUpdate(const EpicRtcRoomState inState) override
    {
        switch (inState)
        {
        case EpicRtcRoomState::Joined:
            UE_LOG(LogTemp, Log, TEXT("Successfully joined room"));
            break;
        case EpicRtcRoomState::Failed:
            UE_LOG(LogTemp, Error, TEXT("Room join failed"));
            break;
        case EpicRtcRoomState::Left:
            UE_LOG(LogTemp, Log, TEXT("Left room"));
            break;
        }
    }

    void OnRoomJoinedUpdate(EpicRtcParticipantInterface* inParticipant) override
    {
        // 新参与者加入
        UE_LOG(LogTemp, Log, TEXT("Participant joined: %s"),
            inParticipant->GetId()._ptr);
    }

    void OnRoomLeftUpdate(const EpicRtcStringView inParticipantId) override
    {
        // 参与者离开
        UE_LOG(LogTemp, Log, TEXT("Participant left"));
    }

    void OnAudioTrackUpdate(EpicRtcParticipantInterface* inParticipant,
                            EpicRtcAudioTrackInterface* inAudioTrack) override
    {
        // 音频轨道更新 - 可以在此处订阅远程音频
        inAudioTrack->Subscribe();
    }

    void OnVideoTrackUpdate(EpicRtcParticipantInterface* inParticipant,
                            EpicRtcVideoTrackInterface* inVideoTrack) override
    {
        // 视频轨道更新 - 可以在此处订阅远程视频
        inVideoTrack->Subscribe();
    }

    void OnDataTrackUpdate(EpicRtcParticipantInterface* inParticipant,
                           EpicRtcDataTrackInterface* inDataTrack) override
    {
        // 数据通道更新
    }

    EpicRtcSdpInterface* OnLocalSdpUpdate(EpicRtcParticipantInterface* inParticipant,
                                           EpicRtcSdpInterface* inOutSdp) override
    {
        // 可在此处修改本地 SDP
        return inOutSdp;
    }

    EpicRtcSdpInterface* OnRemoteSdpUpdate(EpicRtcParticipantInterface* inParticipant,
                                            EpicRtcSdpInterface* inOutSdp) override
    {
        // 可在此处修改远程 SDP
        return inOutSdp;
    }

    void OnRoomErrorUpdate(const EpicRtcErrorCode inError) override
    {
        UE_LOG(LogTemp, Error, TEXT("Room error: %d"), static_cast<uint32_t>(inError));
    }
};
```

### 进阶用法：自定义视频编解码器

从 `Include/epic_rtc/core/video/video_encoder.h` 和 `Include/epic_rtc/core/video/video_decoder.h` 提取：

```cpp
#include "epic_rtc/core/video/video_encoder.h"
#include "epic_rtc/core/video/video_decoder.h"

// 自定义视频编码器
class MyVideoEncoder : public EpicRtcVideoEncoderInterface
{
public:
    EpicRtcStringView GetName() const override { return {"MyEncoder", 10}; }

    EpicRtcVideoEncoderConfig GetConfig() const override { return _config; }

    EpicRtcMediaResult SetConfig(const EpicRtcVideoEncoderConfig& config) override
    {
        _config = config;
        // 应用编码器配置（分辨率、码率、编解码器类型等）
        return EpicRtcMediaResult::Ok;
    }

    EpicRtcVideoEncoderInfo GetInfo() override
    {
        EpicRtcVideoEncoderInfo info{};
        info._supportsNativeHandle = false;
        info._supportsSimulcast = true;
        info._isHardwareAccelerated = false;
        return info;
    }

    EpicRtcMediaResult Encode(const EpicRtcVideoFrame& videoFrame,
                              EpicRtcVideoFrameTypeArrayInterface* frameTypes) override
    {
        // 执行编码
        // 编码完成后通过 callback 通知
        return EpicRtcMediaResult::Ok;
    }

    void RegisterCallback(EpicRtcVideoEncoderCallbackInterface* callback) override
    {
        _callback = callback;
    }

    void Reset() override { /* 重置编码器状态 */ }

private:
    EpicRtcVideoEncoderConfig _config{};
    EpicRtcVideoEncoderCallbackInterface* _callback = nullptr;
};

// 自定义视频编码器初始化器
class MyVideoEncoderInitializer : public EpicRtcVideoEncoderInitializerInterface
{
public:
    void CreateEncoder(EpicRtcVideoCodecInfoInterface* codecInfo,
                       EpicRtcVideoEncoderInterface** outEncoder) override
    {
        *outEncoder = new MyVideoEncoder();
    }

    EpicRtcStringView GetName() override { return {"MyEncoder", 10}; }

    EpicRtcVideoCodecInfoArrayInterface* GetSupportedCodecs() override
    {
        return _supportedCodecs;
    }

private:
    EpicRtcVideoCodecInfoArrayInterface* _supportedCodecs = nullptr;
};

// 在配置中注入自定义编码器
EpicRtcConfig config{};
MyVideoEncoderInitializer* encoderInit = new MyVideoEncoderInitializer();
config._videoConfig._videoEncoderInitializers = {&encoderInit, 1};
config._videoConfig._enableBuiltInVideoCodecs = true; // 同时保留内置编码器
```

### 进阶用法：自定义音频编解码器

从 `Include/epic_rtc/core/audio/audio_encoder.h` 和 `Include/epic_rtc/core/audio/audio_decoder.h` 提取：

```cpp
#include "epic_rtc/core/audio/audio_encoder.h"
#include "epic_rtc/core/audio/audio_decoder.h"

// 自定义音频编码器
class MyAudioEncoder : public EpicRtcAudioEncoderInterface
{
public:
    EpicRtcStringView GetName() const override { return {"MyAudioEncoder", 15}; }

    const EpicRtcAudioEncoderConfig& GetAudioEncoderConfig() const override
    {
        return _config;
    }

    EpicRtcMediaResult SetAudioEncoderConfig(const EpicRtcAudioEncoderConfig& config) override
    {
        _config = config;
        return EpicRtcMediaResult::Ok;
    }

    EpicRtcEncodedAudioFrame Encode(EpicRtcAudioFrame& inAudioFrame) override
    {
        EpicRtcEncodedAudioFrame encodedFrame{};
        // 执行音频编码
        // encodedFrame._data = encodedBuffer;
        // encodedFrame._length = encodedSize;
        // encodedFrame._timestamp = inAudioFrame._timestamp;
        return encodedFrame;
    }

    void Reset() override { /* 重置 */ }

private:
    EpicRtcAudioEncoderConfig _config{};
};
```

### 进阶用法：视频编解码器类型

从 `Include/epic_rtc/core/video/video_common.h` 提取的编解码器支持：

| 编解码器 | 常量值 | 说明 |
|---|---|---|
| H264 | `'H','2','6','4'` | H.264/AVC，最广泛支持 |
| VP8 | `'V','P','8',0` | Google VP8 |
| VP9 | `'V','P','9',0` | Google VP9 |
| AV1 | `'A','V','1',0` | AV1，最新一代 |

### 进阶用法：连接配置

从 `Include/epic_rtc/core/connection_config.h` 提取：

```cpp
#include "epic_rtc/core/connection_config.h"

EpicRtcConnectionConfig connConfig{};

// 配置 ICE 服务器（STUN/TURN）
EpicRtcIceServer iceServer{};
iceServer._urls = {urls, urlCount}; // STUN/TURN 服务器 URL 列表
iceServer._username = {"myuser", 6};
iceServer._password = {"mypass", 6};

EpicRtcIceServer iceServers[] = {iceServer};
connConfig._iceServers = {iceServers, 1};

// ICE 策略
connConfig._iceConnectionPolicy = EpicRtcIcePolicy::All; // 或 Relay（仅中继）

// 码率配置
connConfig._bitrate._minBitrateBps = 100000;
connConfig._bitrate._hasMinBitrateBps = true;
connConfig._bitrate._maxBitrateBps = 5000000;
connConfig._bitrate._hasMaxBitrateBps = true;
connConfig._bitrate._startBitrateBps = 1000000;
connConfig._bitrate._hasStartBitrateBps = true;

// 端口分配器配置
connConfig._portAllocator._minPort = 49152;
connConfig._portAllocator._maxPort = 65535;
connConfig._portAllocator._portAllocation = EpicRtcPortAllocatorOptions::None;
```

### 进阶用法：统计信息收集

从 `Include/epic_rtc/core/stats.h` 提取的统计回调：

```cpp
#include "epic_rtc/core/stats.h"

class MyStatsCallback : public EpicRtcStatsCollectorCallbackInterface
{
public:
    void OnStatsDelivered(const EpicRtcStatsReport& report) override
    {
        // 遍历会话统计
        for (uint64_t i = 0; i < report._sessionStats._size; ++i)
        {
            const EpicRtcSessionStats& sessionStats = report._sessionStats._ptr[i];

            for (uint64_t j = 0; j < sessionStats._roomStats._size; ++j)
            {
                const EpicRtcRoomStats& roomStats = sessionStats._roomStats._ptr[j];

                for (uint64_t k = 0; k < roomStats._connectionStats._size; ++k)
                {
                    const EpicRtcConnectionStats& connStats = roomStats._connectionStats._ptr[k];

                    // 本地音频轨道统计
                    for (uint64_t a = 0; a < connStats._localAudioTracks._size; ++a)
                    {
                        const EpicRtcLocalAudioTrackStats& audioStats = connStats._localAudioTracks._ptr[a];
                        UE_LOG(LogTemp, Log, TEXT("Audio Track %s: bytes sent = %llu"),
                            audioStats._trackId._ptr,
                            audioStats._rtp._local._bytesSent);
                    }

                    // 本地视频轨道统计
                    for (uint64_t v = 0; v < connStats._localVideoTracks._size; ++v)
                    {
                        const EpicRtcLocalVideoTrackStats& videoStats = connStats._localVideoTracks._ptr[v];
                        UE_LOG(LogTemp, Log, TEXT("Video Track %s"), videoStats._trackId._ptr);
                    }

                    // 远程轨道统计
                    for (uint64_t r = 0; r < connStats._remoteVideoTracks._size; ++r)
                    {
                        const EpicRtcRemoteTrackStats& remoteStats = connStats._remoteVideoTracks._ptr[r];
                        UE_LOG(LogTemp, Log, TEXT("Remote Video: packets received = %llu, packets lost = %lld"),
                            remoteStats._rtp._local._packetsReceived,
                            remoteStats._rtp._local._packetsLost);
                    }

                    // 传输统计
                    for (uint64_t t = 0; t < connStats._transports._size; ++t)
                    {
                        const EpicRtcTransportStats& transportStats = connStats._transports._ptr[t];
                        UE_LOG(LogTemp, Log, TEXT("Transport: bytes sent = %llu, bytes received = %llu"),
                            transportStats._bytesSent,
                            transportStats._bytesReceived);
                    }
                }
            }
        }
    }
};
```

### 可用统计指标

| 结构体 | 关键字段 | 说明 |
|---|---|---|
| `EpicRtcInboundRtpStats` | `_packetsReceived`, `_packetsLost`, `_jitter`, `_framesDecoded` | 入站 RTP 统计 |
| `EpicRtcOutboundRtpStats` | `_packetsSent`, `_bytesSent`, `_framesEncoded`, `_qualityLimitationReason` | 出站 RTP 统计 |
| `EpicRtcRemoteInboundRtpStats` | `_roundTripTime`, `_fractionLost` | 远端入站统计（RTT） |
| `EpicRtcTransportStats` | `_bytesSent`, `_bytesReceived`, `_iceState`, `_dtlsState` | 传输层统计 |
| `EpicRtcIceCandidatePairStats` | `_state`, `_availableOutgoingBitrate`, `_currentRoundTripTime` | ICE 候选对统计 |
| `EpicRtcDataTrackStats` | `_messagesSent`, `_bytesSent`, `_messagesReceived` | 数据通道统计 |

## Demo 示例

以下是一个最小化的 Pixel Streaming 2 连接示例：

```cpp
// PixelStreamingDemo.h
#pragma once

#include "CoreMinimal.h"
#include "epic_rtc/core/platform.h"
#include "epic_rtc/core/conference.h"
#include "epic_rtc/core/session.h"
#include "epic_rtc/core/room.h"
#include "epic_rtc/core/room_observer.h"
#include "epic_rtc/core/connection.h"

class FPixelStreamingDemo : public EpicRtcRoomObserverInterface
{
public:
    void Initialize();
    void Shutdown();
    void Tick();

    // EpicRtcRoomObserverInterface
    void OnRoomStateUpdate(const EpicRtcRoomState inState) override;
    void OnRoomJoinedUpdate(EpicRtcParticipantInterface* inParticipant) override;
    void OnRoomLeftUpdate(const EpicRtcStringView inParticipantId) override;
    void OnAudioTrackUpdate(EpicRtcParticipantInterface* inParticipant, EpicRtcAudioTrackInterface* inAudioTrack) override;
    void OnVideoTrackUpdate(EpicRtcParticipantInterface* inParticipant, EpicRtcVideoTrackInterface* inVideoTrack) override;
    void OnDataTrackUpdate(EpicRtcParticipantInterface* inParticipant, EpicRtcDataTrackInterface* inDataTrack) override;
    EpicRtcSdpInterface* OnLocalSdpUpdate(EpicRtcParticipantInterface* inParticipant, EpicRtcSdpInterface* inOutSdp) override { return inOutSdp; }
    EpicRtcSdpInterface* OnRemoteSdpUpdate(EpicRtcParticipantInterface* inParticipant, EpicRtcSdpInterface* inOutSdp) override { return inOutSdp; }
    void OnRoomErrorUpdate(const EpicRtcErrorCode inError) override;

private:
    EpicRtcPlatformInterface* Platform = nullptr;
    EpicRtcConferenceInterface* Conference = nullptr;
    EpicRtcSessionInterface* Session = nullptr;
    EpicRtcRoomInterface* Room = nullptr;
    EpicRtcConnectionInterface* Connection = nullptr;
};
```

```cpp
// PixelStreamingDemo.cpp
#include "PixelStreamingDemo.h"

void FPixelStreamingDemo::Initialize()
{
    // 1. 创建平台
    EpicRtcPlatformConfig platformConfig{};
    GetOrCreatePlatform(platformConfig, &Platform);

    // 2. 创建会议
    EpicRtcConfig config{};
    config._websocketFactory = nullptr; // 需要实际的 WebSocket 工厂实现
    config._audioConfig._enableBuiltInAudioCodecs = true;
    config._videoConfig._enableBuiltInVideoCodecs = true;
    config._logging._level = EpicRtcLogLevel::Info;

    Platform->CreateConference(TEXT("Demo"), config, &Conference);

    // 3. 创建会话
    EpicRtcSessionConfig sessionConfig{};
    Conference->CreateSession(sessionConfig, &Session);
    Session->Connect();

    // 4. 创建房间
    EpicRtcRoomConfig roomConfig{};
    // 配置 ICE 服务器
    EpicRtcIceServer iceServer{};
    EpicRtcStringView stunUrl = {"stun:stun.l.google.com:19302", 27};
    iceServer._urls = {&stunUrl, 1};

    EpicRtcConnectionConfig connConfig{};
    iceServer._urls = {&stunUrl, 1};
    EpicRtcIceServer servers[] = {iceServer};
    connConfig._iceServers = {servers, 1};
    connConfig._iceConnectionPolicy = EpicRtcIcePolicy::All;

    Session->CreateRoom(roomConfig, &Room);

    // 5. 加入房间
    Room->Join();
}

void FPixelStreamingDemo::Tick()
{
    if (Conference)
    {
        while (Conference->NeedsTick())
        {
            Conference->Tick();
        }
    }
}

void FPixelStreamingDemo::Shutdown()
{
    if (Room) { Room->Leave(); Room->Release(); Room = nullptr; }
    if (Session) { Session->Disconnect({}); Session->Release(); Session = nullptr; }
    if (Conference) { Conference->Release(); Conference = nullptr; }
    if (Platform) { Platform->Release(); Platform = nullptr; }
}

void FPixelStreamingDemo::OnRoomStateUpdate(const EpicRtcRoomState inState)
{
    if (inState == EpicRtcRoomState::Joined)
    {
        Room->GetConnection(&Connection);
        // 可在此处添加音视频源并启动协商
    }
}

void FPixelStreamingDemo::OnRoomJoinedUpdate(EpicRtcParticipantInterface*) {}
void FPixelStreamingDemo::OnRoomLeftUpdate(const EpicRtcStringView) {}
void FPixelStreamingDemo::OnAudioTrackUpdate(EpicRtcParticipantInterface*, EpicRtcAudioTrackInterface* track)
{
    track->Subscribe();
}
void FPixelStreamingDemo::OnVideoTrackUpdate(EpicRtcParticipantInterface*, EpicRtcVideoTrackInterface* track)
{
    track->Subscribe();
}
void FPixelStreamingDemo::OnDataTrackUpdate(EpicRtcParticipantInterface*, EpicRtcDataTrackInterface*) {}
void FPixelStreamingDemo::OnRoomErrorUpdate(const EpicRtcErrorCode inError)
{
    UE_LOG(LogTemp, Error, TEXT("Room error: %d"), static_cast<uint32_t>(inError));
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `VulkanRhi` | Vulkan 渲染后端，用于 PixelStreaming2 主模块的图形处理 |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。EpicRtc 模块是纯 C++ 实现，不依赖任何 UE 模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `c1dab3e1` | [PixelStreaming2] Fix: Input handler obtaining default target window from wrong method | 修复输入处理器从错误方法获取默认目标窗口的问题 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点数的编译警告 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 虚拟制片资产分类调整（涉及 VP 相关内容） |
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构 JSON 对象以支持 FString 和 FSharedString |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复格式化函数中作用域枚举导致的乱码输出问题 |

### 维护评价

- **创建时间**：2024 年 9 月，是一个相对较新的插件
- **更新频率**：近期（2026 年 4-5 月）有多次实质性更新，说明仍在活跃维护
- **更新内容**：主要为 bug 修复和代码质量改进，功能趋于稳定
- **实验性标记**：`.uplugin` 中未标记为实验性，但 `EnabledByDefault=false` 说明 Epic 认为尚未准备好默认启用
- **架构成熟度**：9 个模块的清晰分离，自研 EpicRtc 抽象层，架构设计成熟

**推荐使用**：如果你需要 Pixel Streaming 功能，Pixel Streaming 2 是官方推荐的新一代实现。虽然默认未启用，但已在积极维护中。建议关注从原版 Pixel Streaming 迁移的时机。

**注意**：由于该插件默认未启用（`EnabledByDefault=false`），使用前需要在项目设置中手动启用，或在 `.uproject` 文件中添加插件声明。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming2)
- [官方文档](https://docs.unrealengine.com/en-US/Platforms/PixelStreaming/index.html)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming2/Tests)