# Pixel Streaming 2

> Streaming of Unreal Engine audio and rendering to WebRTC-compatible media players such as a web browsers.

| 属性 | 值 |
|---|---|
| 中文名 | 像素流 2 |
| 分类 | Graphics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PixelStreaming2` (Runtime), `PixelStreaming2Core` (Runtime), `PixelStreaming2Editor` (Runtime), `PixelStreaming2HMD` (Runtime), `PixelStreaming2Input` (Runtime), `PixelStreaming2RTC` (Runtime), `PixelStreaming2Servers` (Runtime), `PixelStreaming2Settings` (Runtime), `EpicRtc` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-09-04 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming2) | |

## 用途

Pixel Streaming 2 是 Epic Games 为 UE5 打造的新一代像素流插件，用于将 Unreal Engine 的音频和视频渲染结果通过 WebRTC 协议实时传输到浏览器等兼容的 WebRTC 播放器。

与旧版 Pixel Streaming 插件相比，Pixel Streaming 2 进行了架构级重构：

- **内置 EpicRtc**：不再依赖外部 libwebrtc，而是集成了 Epic 自研的 `EpicRtc` WebRTC 抽象层，完全掌控 WebRTC 协议栈
- **模块化架构**：将功能拆分为 9 个独立模块（Core、RTC、Input、Servers、HMD、Settings、Editor 等），职责清晰
- **多房间模式支持**：支持 MediaServer（媒体服务器中转）、P2P（点对点）和 Mixed（混合）三种连接模式
- **自定义编解码器**：允许注入自定义的音频/视频编码器和解码器实现
- **完整的 SVC/Simulcast 支持**：支持 VP8/VP9/H264/AV1 编解码器，以及可伸缩视频编码（SVC）和 Simulcast
- **数据通道**：支持通过 WebRTC DataChannel 传输自定义数据

该插件解决的核心问题是：**让运行在高性能 GPU 服务器上的 UE5 应用，能够通过浏览器实时交互**，典型场景包括云游戏、远程渲染、Web 端数字孪生等。

## 使用场景

- **云游戏/云渲染**：在服务器上运行 UE5 游戏，玩家通过浏览器即可游玩，无需安装客户端
- **远程协作/远程桌面**：多人通过浏览器同时查看和操控同一个 UE5 应用
- **数字孪生/Web 可视化**：将 UE5 中构建的 3D 场景通过浏览器展示，支持实时交互
- **VR/XR 流式传输**：通过 `PixelStreaming2HMD` 模块支持 HMD 设备的流式传输
- **P2P 低延迟场景**：选择 P2P 模式时，参与者之间直接建立连接，无需中转服务器，延迟更低

## 蓝图用法

Pixel Streaming 2 主要是 C++ 层面的 API，其核心 EpicRtc 模块是纯 C++ 接口。不过上层 `PixelStreaming2` 和 `PixelStreaming2Core` 模块可能暴露部分蓝图节点。由于当前源码分析聚焦于 EpicRtc 底层模块，此处描述 C++ 层面的核心交互。

## C++ 用法

### 核心架构概述

EpicRtc 采用**引用计数接口**的设计模式，所有核心对象都继承自 `EpicRtcRefCountInterface`，通过 `AddRef()/Release()` 管理生命周期。辅助工具 `EpicRtc::RefCountPtr<T>` 提供了类似 `TComPtr`/`TSharedPtr` 的 RAII 封装。

对象层级关系：

```
EpicRtcPlatformInterface (平台入口)
  └── EpicRtcConferenceInterface (会议实例)
        └── EpicRtcSessionInterface (信令会话)
              └── EpicRtcRoomInterface (房间)
                    └── EpicRtcConnectionInterface (媒体连接)
                          ├── EpicRtcAudioTrackInterface (音频轨道)
                          ├── EpicRtcVideoTrackInterface (视频轨道)
                          └── EpicRtcDataTrackInterface (数据轨道)
```

### 头文件引入

```cpp
#include "epic_rtc/core/platform.h"
#include "epic_rtc/core/conference.h"
#include "epic_rtc/core/session.h"
#include "epic_rtc/core/room.h"
#include "epic_rtc/core/connection.h"
#include "epic_rtc/core/video/video_track.h"
#include "epic_rtc/core/audio/audio_track.h"
#include "epic_rtc/core/data_track.h"
#include "epic_rtc_helper/memory/ref_count_ptr.h"
```

### 基本用法

**1. 初始化平台和创建会议**

```cpp
#include "epic_rtc/core/platform.h"
#include "epic_rtc/core/conference.h"
#include "epic_rtc/core/conference_config.h"
#include "epic_rtc_helper/memory/ref_count_ptr.h"

// 配置平台
EpicRtcPlatformConfig platformConfig{};
platformConfig._memory = nullptr;    // 使用默认内存分配器
platformConfig._callstack = nullptr; // 使用默认调用栈追踪

// 获取平台实例
EpicRtc::RefCountPtr<EpicRtcPlatformInterface> platform;
EpicRtcErrorCode result = GetOrCreatePlatform(platformConfig, platform.GetInitReference());
if (result != EpicRtcErrorCode::Ok)
{
    UE_LOG(LogTemp, Error, TEXT("Failed to create EpicRtc platform"));
    return;
}

// 配置会议参数
EpicRtcConfig config{};
config._websocketFactory = myWebSocketFactory; // 需要实现 WebSocket 工厂
config._signallingType = EpicRtcSignallingType::Default;
config._signingPlugin = nullptr;
config._audioConfig._enableBuiltInAudioCodecs = true;
config._audioConfig._recordingSampleRate = 48000;
config._audioConfig._recordingChannels = 2;
config._videoConfig._enableBuiltInVideoCodecs = true;

// 创建会议实例
EpicRtc::RefCountPtr<EpicRtcConferenceInterface> conference;
result = platform->CreateConference(EpicRtcStringView{"MyConference", 13}, config, conference.GetInitReference());
```

**2. 创建会话并连接信令服务器**

```cpp
#include "epic_rtc/core/session.h"

// 配置会话（信令服务器 URL 等）
EpicRtcSessionConfig sessionConfig{};
// ... 设置信令服务器配置

EpicRtc::RefCountPtr<EpicRtcSessionInterface> session;
EpicRtcErrorCode result = conference->CreateSession(sessionConfig, session.GetInitReference());

// 连接到信令服务器
result = session->Connect();
```

**3. 创建房间并加入**

```cpp
#include "epic_rtc/core/room.h"
#include "epic_rtc/core/room_observer.h"
#include "epic_rtc/core/connection_config.h"

// 配置房间
EpicRtcRoomConfig roomConfig{};
roomConfig._roomId = EpicRtcStringView{"test-room", 9};
roomConfig._mode = EpicRtcRoomMode::MediaServer;

// 配置 ICE 服务器（STUN/TURN）
EpicRtcIceServer iceServer{};
// urls 设置等...

// 创建房间
EpicRtc::RefCountPtr<EpicRtcRoomInterface> room;
session->CreateRoom(roomConfig, room.GetInitReference());

// 注册房间观察者以接收事件回调
// room->SetObserver(myRoomObserver); // 需实现 EpicRtcRoomObserverInterface

// 加入房间
room->Join();
```

（来源：`Include/epic_rtc/core/room.h`, `Include/epic_rtc/core/session.h`, `Include/epic_rtc/core/conference.h`）

### 进阶用法

**4. 添加音视频轨道并推流**

```cpp
#include "epic_rtc/core/connection.h"
#include "epic_rtc/core/video/video_track.h"
#include "epic_rtc/core/audio/audio_track.h"

// 获取连接对象
EpicRtc::RefCountPtr<EpicRtcConnectionInterface> connection;
room->GetConnection(connection.GetInitReference());

// 添加视频源
EpicRtcVideoSource videoSource{};
// ... 配置视频源参数
connection->AddVideoSource(videoSource);

// 添加音频源
EpicRtcAudioSource audioSource{};
// ... 配置音频源参数
connection->AddAudioSource(audioSource);

// 开始协商
connection->StartNegotiation();
```

**5. 自定义视频编码器注入**

```cpp
#include "epic_rtc/core/video/video_encoder.h"
#include "epic_rtc/core/conference_config.h"

// 实现自定义编码器初始化器
class FMyVideoEncoderInitializer : public EpicRtcVideoEncoderInitializerInterface
{
public:
    void CreateEncoder(EpicRtcVideoCodecInfoInterface* codecInfo, EpicRtcVideoEncoderInterface** outEncoder) override
    {
        // 创建自定义编码器实例
        *outEncoder = new FMyVideoEncoder(codecInfo);
    }
    
    EpicRtcStringView GetName() override
    {
        return EpicRtcStringView{"MyCustomEncoder", 15};
    }
    
    EpicRtcVideoCodecInfoArrayInterface* GetSupportedCodecs() override
    {
        // 返回支持的编解码器列表
        return _supportedCodecs;
    }
    
    // 实现 AddRef/Release（使用 EPICRTC_REFCOUNT_INTERFACE_IN_PLACE 宏）
    EPICRTC_REFCOUNT_INTERFACE_IN_PLACE
};

// 在配置中注入
EpicRtcConfig config{};
FMyVideoEncoderInitializer* myInitializer = new FMyVideoEncoderInitializer();
EpicRtcVideoEncoderInitializerInterfaceSpan span{&myInitializer, 1};
config._videoConfig._videoEncoderInitializers = span;
```

（来源：`Include/epic_rtc/core/video/video_encoder.h`, `Include/epic_rtc/core/conference_config.h`）

**6. 统计数据收集**

```cpp
#include "epic_rtc/core/stats.h"

// 实现统计回调
class FMyStatsCallback : public EpicRtcStatsCollectorCallbackInterface
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
                // 处理连接统计数据...
            }
        }
    }
    
    EPICRTC_REFCOUNT_INTERFACE_IN_PLACE
};

// 在配置中启用统计
EpicRtcConfig config{};
FMyStatsCallback* statsCallback = new FMyStatsCallback();
config._stats._statsCollectorCallback = statsCallback;
config._stats._statsCollectorInterval = 1000; // 每 1000ms 收集一次
```

（来源：`Include/epic_rtc/core/stats.h`, `Include/epic_rtc/core/conference_config.h`）

## Demo 示例

**最小化 WebRTC 会议创建示例**

```cpp
// MyPixelStreamingDemo.h
#pragma once

#include "epic_rtc/core/platform.h"
#include "epic_rtc/core/conference.h"
#include "epic_rtc/core/session.h"
#include "epic_rtc/core/room.h"
#include "epic_rtc/core/room_observer.h"
#include "epic_rtc_helper/memory/ref_count_ptr.h"

class FMyPixelStreamingDemo
{
public:
    void Initialize();
    void Tick();
    void Shutdown();

private:
    EpicRtc::RefCountPtr<EpicRtcPlatformInterface> Platform;
    EpicRtc::RefCountPtr<EpicRtcConferenceInterface> Conference;
    EpicRtc::RefCountPtr<EpicRtcSessionInterface> Session;
    EpicRtc::RefCountPtr<EpicRtcRoomInterface> Room;
};
```

```cpp
// MyPixelStreamingDemo.cpp
#include "MyPixelStreamingDemo.h"

void FMyPixelStreamingDemo::Initialize()
{
    // 1. 创建平台
    EpicRtcPlatformConfig platformConfig{};
    platformConfig._memory = nullptr;
    platformConfig._callstack = nullptr;
    
    if (GetOrCreatePlatform(platformConfig, Platform.GetInitReference()) != EpicRtcErrorCode::Ok)
    {
        return;
    }
    
    // 2. 配置并创建会议
    EpicRtcConfig config{};
    config._websocketFactory = nullptr; // 需要实际实现
    config._signallingType = EpicRtcSignallingType::Default;
    config._signingPlugin = nullptr;
    config._audioConfig._enableBuiltInAudioCodecs = true;
    config._videoConfig._enableBuiltInVideoCodecs = true;
    config._stats._statsCollectorInterval = 0; // 禁用统计
    
    Conference.GetInitReference();
    if (Platform->CreateConference(
        EpicRtcStringView{"Demo", 4}, config, Conference.GetInitReference()) != EpicRtcErrorCode::Ok)
    {
        return;
    }
    
    // 3. 创建会话并连接
    EpicRtcSessionConfig sessionConfig{};
    Session.GetInitReference();
    if (Conference->CreateSession(sessionConfig, Session.GetInitReference()) != EpicRtcErrorCode::Ok)
    {
        return;
    }
    
    Session->Connect();
}

void FMyPixelStreamingDemo::Tick()
{
    if (Conference.IsValid())
    {
        // 处理 EpicRtc 事件队列
        while (Conference->NeedsTick())
        {
            Conference->Tick();
        }
    }
}

void FMyPixelStreamingDemo::Shutdown()
{
    // 逆序释放，RefCountPtr 析构时自动调用 Release
    Room.Reset();
    Session.Reset();
    Conference.Reset();
    Platform.Reset();
}
```

## 模块依赖

由于 EpicRtc 模块使用跨 DLL 边界的引用计数接口设计，其依赖关系较为独立。

| 模块 | 用途 |
|---|---|
| `VulkanRHI` | PixelStreaming2 主模块依赖，用于 GPU 帧捕获 |
| 无特殊依赖 | EpicRtc 模块为纯 C++ 第三方库，仅依赖标准 C++ 库 |

其他模块（PixelStreaming2Core、PixelStreaming2Input、PixelStreaming2Servers 等）的具体依赖需查看各自的 Build.cs 文件。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `c1dab3e1` | [PixelStreaming2] Fix: Input handler obtaining default target window from wrong method | 修复输入处理器从错误方法获取默认目标窗口的问题 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 产生的编译警告 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 虚拟制片资产分类调整和迁移 |
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构 JSON 对象以同时支持 FString 和 FSharedString |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复格式化函数中作用域枚举导致的垃圾输出问题 |

### 维护评价

**🟢 活跃维护**

Pixel Streaming 2 是 Epic Games 重点维护的插件，理由如下：

1. **创建时间较新**：2024 年 9 月随 UE5 新版本引入，是 Pixel Streaming 的下一代替代品
2. **持续更新**：最近数月内有多次实质性更新，涵盖输入处理、编译兼容性、JSON 重构等功能修复
3. **架构先进**：集成了 Epic 自研的 EpicRtc WebRTC 库，不再依赖外部 libwebrtc，表明 Epic 对该技术栈有长期投入
4. **注意**：默认未启用（`EnabledByDefault: false`），需要在项目设置中手动启用
5. **模块化设计**：9 个模块各自独立，便于单独理解和扩展

**推荐使用**：对于需要浏览器端实时交互 UE5 内容的项目，Pixel Streaming 2 是官方推荐的方案，建议优先于旧版 Pixel Streaming。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming2)
- [官方文档](https://docs.unrealengine.com/en-US/Platforms/PixelStreaming/index.html)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming2/Tests)