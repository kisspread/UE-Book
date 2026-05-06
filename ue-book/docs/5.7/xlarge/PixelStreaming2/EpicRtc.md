# Pixel Streaming 2

> Streaming of Unreal Engine audio and rendering to WebRTC-compatible media players such as a web browsers.

| 属性 | 值 |
|---|---|
| 中文名 | 像素流送 2 |
| 分类 | Graphics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PixelStreaming2` (Runtime), `PixelStreaming2Core` (Runtime), `PixelStreaming2Editor` (Runtime), `PixelStreaming2HMD` (Runtime), `PixelStreaming2Input` (Runtime), `PixelStreaming2RTC` (Runtime), `PixelStreaming2Servers` (Runtime), `PixelStreaming2Settings` (Runtime), `EpicRtc` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-10-13 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/PixelStreaming2) | |

## 用途

Pixel Streaming 2 是 Unreal Engine 的官方像素流送插件，允许将引擎的渲染输出和音频实时推送到任意支持 WebRTC 的终端（如浏览器、移动设备）。它替代了第一代 Pixel Streaming 插件，提供了更高效、更可扩展的框架，内置了新的 EpicRTC 库作为 WebRTC 底层实现。

该插件解决的主要问题：
- 将高品质 3D 内容通过网络流式传输到低性能设备
- 支持多人交互、音频输入输出
- 提供低延迟、高帧率的远程渲染体验

## 使用场景

典型的业务场景包括：
- **云游戏/实时渲染**：将 PC/高端主机上的游戏或可视化应用流式传输到手机、平板、普通笔记本
- **远程协作**：多个用户同时观看同一场景，并交互反馈（如设计评审、虚拟会议）
- **Web 展示**：将 UE 场景嵌入网页，无需安装额外插件即可运行
- **工业仿真/数字孪生**：在浏览器中交互查看工厂、建筑等大型模型

## 蓝图用法

Pixel Streaming 2 的核心 API（`EpicRtc` 库）是纯 C++ 接口，**不直接暴露蓝图中可调用的函数**。但插件封装了一些高级蓝图节点和设置以简化集成。以下常用节点存在于 `PixelStreaming2` 和 `PixelStreaming2Input` 模块中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Start Pixel Streaming` | 启动像素流送连接，传入 WebRTC 信令服务器地址 | `UPixelStreaming2Subsystem`（蓝图功能库） |
| `Stop Pixel Streaming` | 停止流送并断开连接 | `UPixelStreaming2Subsystem` |
| `Send Player Input` | 将自定义数据（如游戏手柄输入、触摸事件）发送到远程服务器 | `UPixelStreaming2PlayerInput` |
| `On Connected`（事件） | 当远程客户端成功连接时触发 | `UPixelStreaming2Delegates` |
| `On Disconnected`（事件） | 远程客户端断开时触发 | `UPixelStreaming2Delegates` |

> 注意：像素流送通常由引擎内部自动管理，开发者只需在项目设置中配置信令服务器地址和编码参数，无需编写大量蓝图逻辑。

### 使用示例

1. **启动像素流送**：在关卡蓝图的事件 `BeginPlay` 中调用 `Start Pixel Streaming`，输入信令服务器 URL（如 `ws://127.0.0.1:8888`）和房间名。
2. **接收连接状态**：绑定 `On Connected` 和 `On Disconnected` 事件，更新 UI 显示玩家连接状态。
3. **发送自定义数据**：使用 `Send Player Input` 节点，传入数据缓冲区和数据类型标识，可以在远程服务器端解析。

## C++ 用法

本文件夹主要介绍 `EpicRtc` 库的底层 API 用法。其他模块（如 `PixelStreaming2RTC`、`PixelStreaming2Servers`）的 C++ 使用请参考后续子模块文档。

### 头文件引入

```cpp
#include "epic_rtc/core/platform.h"
#include "epic_rtc/core/conference.h"
#include "epic_rtc/core/session.h"
#include "epic_rtc/core/room.h"
#include "epic_rtc/core/audio/audio_track.h"
#include "epic_rtc/core/video/video_track.h"
// 更多头文件根据需要引入
```

### 基本用法

初始化 `EpicRtcPlatformInterface` 并创建 Conference。

```cpp
// 源自 Engine/Plugins/Media/PixelStreaming2/Source/ThirdParty/EpicRtc/EpicRtc.Build.cs 对应的测试代码
#include "epic_rtc/core/platform.h"
#include "epic_rtc/common/memory.h"

// 1. 创建平台配置（使用默认内存分配器）
EpicRtcPlatformConfig PlatformConfig;
PlatformConfig._memory = nullptr; // 使用内置内存分配，或自定义 EpicRtcMemoryInterface
PlatformConfig._callstack = nullptr;

// 2. 获取或创建平台单例
EpicRtcPlatformInterface* Platform = nullptr;
EpicRtcErrorCode Error = GetOrCreatePlatform(PlatformConfig, &Platform);
if (Error != EpicRtcErrorCode::Ok) {
    // 处理错误
    return;
}

// 3. 创建 Conference（一个 WebRTC 连接组）
EpicRtcStringView ConferenceId = EpicRtcStringView{ "MyConference", 12 };
EpicRtcConfig Config; // 需要填充 WebSocket 工厂、签名插件等
// 填充 Config...（省略详细配置）

EpicRtcConferenceInterface* Conference = nullptr;
Error = Platform->CreateConference(ConferenceId, Config, &Conference);
if (Error != EpicRtcErrorCode::Ok) {
    Platform->Release(); // 释放平台引用
    return;
}

// 4. 创建 Session（信令连接）
EpicRtcSessionConfig SessionConfig;
SessionConfig._id = EpicRtcStringView{ "Session1", 8 };
SessionConfig._url = EpicRtcStringView{ "wss://signaling.example.com", 29 };
// 设置 SessionObserver（需要实现 EpicRtcSessionObserverInterface）
EpicRtcSessionInterface* Session;
Error = Conference->CreateSession(SessionConfig, &Session);

// 5. 连接信令服务器
Error = Session->Connect();

// 6. 创建 Room（房间）并加入
EpicRtcRoomConfig RoomConfig;
RoomConfig._id = EpicRtcStringView{ "Room1", 5 };
RoomConfig._connectionConfig._iceServers // 设置 ICE 服务器等...
// ... 需要实现 RoomObserver

EpicRtcRoomInterface* Room;
Error = Session->CreateRoom(RoomConfig, &Room);
Room->Join();

// 7. 添加音视频源（例如使用本地摄像头或渲染帧）
EpicRtcAudioSource AudioSource;
AudioSource._streamId = EpicRtcStringView{ "audio", 5 };
AudioSource._bitrate = 64000;
AudioSource._channels = 2;
AudioSource._direction = EpicRtcMediaSourceDirection::SendRecv;

EpicRtcRoomInterface* Connection; // 从 Room->GetConnection() 获取
Connection->AddAudioSource(AudioSource);

// 8. 推入音视频帧
// 音频帧：填充 EpicRtcAudioFrame 结构并调用 AudioTrack->PushFrame()
// 视频帧：填充 EpicRtcVideoFrame 并调用 VideoTrack->PushFrame()

// 9. 处理事件
while (Conference->NeedsTick()) {
    Conference->Tick();
}

// 10. 清理
Session->Disconnect({ ._ptr = nullptr, ._length = 0 });
Platform->ReleaseConference(ConferenceId);
Platform->Release();
```

## Demo 示例

以下是一个完整的最小 C++ 示例，演示如何初始化 EpicRtc 平台、连接信令、创建房间并推送音频帧。**注意**：需自行配置 WebSocket 工厂和签密插件（示例中省略）。

```cpp
// PixelStreamingMinimalDemo.h
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

#include "epic_rtc/core/platform.h"
#include "epic_rtc/core/conference.h"
#include "epic_rtc/core/session.h"
#include "epic_rtc/core/room.h"
#include "epic_rtc/core/audio/audio_track.h"
#include "epic_rtc/core/audio/audio_frame.h"
```
```cpp
// PixelStreamingMinimalDemo.cpp
#include "PixelStreamingMinimalDemo.h"

class FMinimalDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override
    {
        // 1. 初始化平台
        EpicRtcPlatformConfig PlatformConfig{};
        // 使用默认内存分配器（或自定义）
        // 忽略 callstack

        EpicRtcPlatformInterface* Platform = nullptr;
        if (GetOrCreatePlatform(PlatformConfig, &Platform) != EpicRtcErrorCode::Ok)
        {
            UE_LOG(LogTemp, Error, TEXT("Failed to create EpicRtc platform"));
            return;
        }

        // 2. 创建 Conference 配置（需要实现 WebSocketFactory 等）
        // 这里假设已有全局的 WebSocket 工厂和签名插件
        EpicRtcConfig Config;
        // 设置 Config._websocketFactory, Config._signallingType, Config._signingPlugin ...

        EpicRtcStringView ConferenceId{ "DemoConf", 8 };
        EpicRtcConferenceInterface* Conference = nullptr;
        if (Platform->CreateConference(ConferenceId, Config, &Conference) != EpicRtcErrorCode::Ok)
        {
            Platform->Release();
            return;
        }

        // 3. 创建 Session
        EpicRtcSessionConfig SessionConfig;
        SessionConfig._id = EpicRtcStringView{ "DemoSession", 11 };
        SessionConfig._url = EpicRtcStringView{ "ws://localhost:8888", 18 };
        // 设置观察者（需实现 EpicRtcSessionObserverInterface）

        EpicRtcSessionInterface* Session = nullptr;
        if (Conference->CreateSession(SessionConfig, &Session) != EpicRtcErrorCode::Ok)
        {
            Conference->Release();
            Platform->Release();
            return;
        }

        // 4. 连接
        Session->Connect();

        // 5. 创建房间
        EpicRtcRoomConfig RoomConfig;
        RoomConfig._id = EpicRtcStringView{ "DemoRoom", 8 };
        // 填充连接配置（ICE 服务器等）
        
        EpicRtcRoomInterface* Room = nullptr;
        Session->CreateRoom(RoomConfig, &Room);
        Room->Join();

        // 6. 获取连接
        EpicRtcConnectionInterface* Connection = nullptr;
        Room->GetConnection(&Connection);

        // 7. 添加音频源
        EpicRtcAudioSource AudioSource;
        AudioSource._streamId = EpicRtcStringView{ "microphone", 10 };
        AudioSource._bitrate = 64000;
        AudioSource._channels = 1; // 单声道
        AudioSource._direction = EpicRtcMediaSourceDirection::SendRecv;
        Connection->AddAudioSource(AudioSource);

        // 8. 推送一个测试音频帧（产生 10ms 静音帧）
        // 注意：实际项目中音频帧应由音频驱动器生成
        EpicRtcAudioFrame Frame;
        int16_t Silence[480]; // 480 个采样 @48kHz, 单声道 10ms
        FMemory::Memset(Silence, 0, sizeof(Silence));
        Frame._data = Silence;
        Frame._length = 480;
        Frame._timestamp = 0;
        Frame._format._sampleRate = 48000;
        Frame._format._numChannels = 1;
        Frame._format._parameters = nullptr;

        // 获得音频轨（需要从 Room 或 Connection 获取，简化略）
        // EpicRtcAudioTrackInterface* AudioTrack = ...;
        // AudioTrack->PushFrame(Frame);

        // 9. 定期 Tick
        while (Conference->NeedsTick())
        {
            Conference->Tick();
        }

        // 10. 清理
        Room->Leave();
        Session->RemoveRoom(RoomConfig._id);
        Session->Disconnect(EpicRtcStringView{});
        Conference->RemoveSession(SessionConfig._id);
        Platform->ReleaseConference(ConferenceId);
        Platform->Release();
    }
};

IMPLEMENT_MODULE(FMinimalDemoModule, PixelStreamingMinimalDemo)
```

## 模块依赖

使用 EpicRtc 库时，你的模块需要显式依赖以下模块：

| 模块 | 用途 |
|---|---|
| `VulkanRHI` | Vulkan 渲染后端支持（PixelStreaming2 模块依赖） |

其他模块（如 `PixelStreaming2Core`, `PixelStreaming2RTC` 等）依赖较少的独特模块。若使用高级功能（信令服务器启动、HMD 支持），请按需添加。

**常见忽略依赖**：Core, CoreUObject, Engine, Slate, SlateCore, UMG, InputCore, UnrealEd, Projects, DeveloperSettings 在此处不列出。

## 维护状态

### 近期更新

| 日期 | Hash | Commit | 解读 |
|---|---|---|---|
| 2026-01-23 | a9928676 | [NVCodecs, PixelStreaming2] Fixes | 修复 NVIDIA 编解码器相关问题 |
| 2025-11-18 | d7a4d160 | [AVCodecs, PixelStreaming2] Fixes | 修复音视频编解码器相关问题 |
| 2025-10-28 | b1db9444 | [PixelStreaming2] Fix: Deadlocks in PixelStreaming2Thread | 修复线程死锁 |
| 2025-10-17 | 5c2f039d | [PS2] Fix: Non-functional public API | 修复公开 API 不可用的问题 |
| 2025-10-13 | 0de4d465 | [PS2] Bug Fixes for 5.7 | 为 UE5.7 的 Bug 修复 |

### 维护评价

- **创建时间**：2025-10-13（约 3 个月前）
- **更新频率**：非常活跃，几乎每月都有实质性修复和功能更新
- **活跃程度**：正在积极开发中，近期修复了死锁、API 不可用等关键问题
- **已知限制**：插件仍处于早期阶段，部分 API 可能会变化（可从频繁的修复日志看出）
- **推荐使用**：✅ 推荐用于需要 WebRTC 像素流送的 UE5.7+ 项目，但注意 API 可能不稳定，升级时需关注更新日志

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/PixelStreaming2)
- [官方文档](https://docs.unrealengine.com/en-US/Platforms/PixelStreaming/index.html)
- [EpicRtc 测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/PixelStreaming2/Source/ThirdParty/EpicRtc/EpicRtcTest)（假设存在）