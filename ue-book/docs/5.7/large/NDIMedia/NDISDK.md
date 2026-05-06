# NDI Media

> Implements media source and media output using NDI protocol

| 属性 | 值 |
|---|---|
| 中文名 | NDI 媒体 SDK |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（第三方 NDI SDK 头文件和库） |
| 模块 | `NDIMedia` (Runtime), `NDIMediaEditor` (Editor), `NDIMediaRendering` (Runtime), `NDISDK` (External) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-10-07 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/NDIMedia) | |

## 用途

`NDISDK` 模块是 NDI®（Network Device Interface）协议的 UE 跨平台动态加载封装。它封装了 Vizrt NDI SDK 的 C API，在运行时加载系统原生 NDI 库（Windows: `Processing.NDI.Lib.x64.dll`，macOS: `libndi.dylib`，Linux: `libndi.so.6`），并通过函数指针结构体 `NDIlib_v5` 暴露所有 NDI 功能。

该模块解决的核心问题：**将 NDI 网络流媒体协议集成到 UE 媒体框架**，使 UE 能够：
- 发现局域网内所有 NDI 源（摄像头、软件输出等）
- 接收 NDI 视频/音频/元数据流
- 发送视频/音频/元数据到 NDI 网络
- 控制远程 NDI 设备的 PTZ（云台变焦）
- 使用帧同步器校正时钟偏差

## 使用场景

- **虚拟制片（Virtual Production）**：在 UE 中实时接收来自 LED 墙处理器或追踪摄像头的 NDI 流，作为背景或合成素材。
- **现场直播推流**：将 UE 渲染的画面（如虚拟演播室）通过 NDI 发送到导播台（如 OBS、Wirecast、vMix）。
- **远程摄像机控制**：通过 `NDIlib_recv_ptz_*` 函数远程控制支持 NDI PTZ 的摄像机。
- **多机位同步录制**：使用帧同步器（`NDIlib_framesync`）将多个 NDI 输入对齐到统一时钟。

## 蓝图用法

本模块（`NDISDK`）为底层 C 封装库，**不直接暴露蓝图可调用节点**。蓝图用户应通过插件中的 `NDIMedia` 运行时模块提供的 `MediaPlayer`、`MediaSource` 和 `MediaOutput` 资产进行操作。

### 相关资产（由 NDIMedia 模块提供）

| 资产类型 | 说明 |
|---|---|
| `NDIMediaSource` | 用于选择 NDI 网络源的媒体源资产 |
| `NDIMediaOutput` | 用于将 UE 输出到 NDI 网络的媒体输出资产 |

配置方式：在内容浏览器中创建媒体源/输出资产，设置 NDI 源名称或输出名称，然后挂载到 `MediaPlayer` / `MediaBundle` 使用。

## C++ 用法

### 头文件引入

```cpp
#include "NDISDK/Public/Processing.NDI.Lib.h"      // 核心 API 声明
#include "NDISDK/Public/Processing.NDI.DynamicLoad.h" // 动态加载处理（直接包含 Lib.h 即可）
```

### 基本用法

#### 1. 初始化与销毁 NDI 库

```cpp
// 初始化 NDI（调用一次即可）
bool bInitialized = NDIlib_initialize();
if (!bInitialized)
{
    UE_LOG(LogTemp, Error, TEXT("NDI initialization failed"));
    return;
}

// 程序退出时销毁
NDIlib_destroy();
```

#### 2. 查找网络上的 NDI 源

```cpp
// 创建查找实例（显示本地源，不限制组）
NDIlib_find_create_t findDesc;
findDesc.show_local_sources = true;
findDesc.p_groups = nullptr;
findDesc.p_extra_ips = nullptr;

NDIlib_find_instance_t pFind = NDIlib_find_create_v2(&findDesc);
if (!pFind) return;

// 等待并获取源列表
uint32_t srcCount = 0;
const NDIlib_source_t* pSources = NDIlib_find_get_current_sources(pFind, &srcCount);
for (uint32_t i = 0; i < srcCount; i++)
{
    UE_LOG(LogTemp, Log, TEXT("Found NDI source: %s"), UTF8_TO_TCHAR(pSources[i].p_ndi_name));
}

// 销毁查找实例
NDIlib_find_destroy(pFind);
```

#### 3. 创建接收器并捕获视频帧

```cpp
// 设置接收参数
NDIlib_recv_create_v3_t recvDesc;
recvDesc.source_to_connect_to = pSources[0];  // 使用第一个源
recvDesc.color_format = NDIlib_recv_color_format_BGRX_BGRA;
recvDesc.bandwidth = NDIlib_recv_bandwidth_highest;
recvDesc.allow_video_fields = true;

NDIlib_recv_instance_t pRecv = NDIlib_recv_create_v3(&recvDesc);

// 在主循环中捕获
NDIlib_video_frame_v2_t* pVideo = nullptr;
NDIlib_audio_frame_v2_t* pAudio = nullptr;
NDIlib_metadata_frame_t* pMeta = nullptr;

NDIlib_frame_type_e frameType = NDIlib_recv_capture_v2(pRecv, &pVideo, &pAudio, &pMeta, 1000);
if (frameType == NDIlib_frame_type_video)
{
    // 处理视频帧（pVideo->p_data 为 BGRX 数据）
    uint32_t width = pVideo->xres;
    uint32_t height = pVideo->yres;
    // 复制到 UE 纹理等...
    NDIlib_recv_free_video_v2(pRecv, pVideo);
}
else if (frameType == NDIlib_frame_type_audio)
{
    // 处理音频
    NDIlib_recv_free_audio_v2(pRecv, pAudio);
}
else if (frameType == NDIlib_frame_type_metadata)
{
    // 处理元数据
    NDIlib_recv_free_metadata(pRecv, pMeta);
}

// 销毁接收器
NDIlib_recv_destroy(pRecv);
```

#### 4. 发送视频帧

```cpp
// 创建发送实例
NDIlib_send_create_t sendDesc;
sendDesc.p_ndi_name = "My UE Sender";  // NDI 源名称
sendDesc.clock_video = true;
sendDesc.clock_audio = true;

NDIlib_send_instance_t pSend = NDIlib_send_create(&sendDesc);
if (!pSend) return;

// 准备视频帧（例如 1920x1080 BGRA）
TArray<uint8> FrameBuffer;
FrameBuffer.SetNum(1920 * 1080 * 4); // 填充像素数据

NDIlib_video_frame_v2_t videoFrame;
videoFrame.xres = 1920;
videoFrame.yres = 1080;
videoFrame.FourCC = NDIlib_FourCC_video_type_BGRA;
videoFrame.frame_rate_N = 30;
videoFrame.frame_rate_D = 1;
videoFrame.p_data = FrameBuffer.GetData();
videoFrame.line_stride_in_bytes = 1920 * 4;

NDIlib_send_send_video_v2(pSend, &videoFrame);

// 销毁发送器
NDIlib_send_destroy(pSend);
```

### 进阶用法

#### 使用帧同步器（Frame Sync）将接收流转换为拉模型

```cpp
NDIlib_framesync_instance_t pFS = NDIlib_framesync_create(pRecv);

// 在每帧调用（例如 GameThread 的 Tick）
NDIlib_video_frame_v2_t* pVideo = nullptr;
NDIlib_audio_frame_v2_t* pAudio = nullptr;
NDIlib_framesync_capture(pFS, &pVideo, &pAudio, 0);  // timeout=0 立即返回
if (pVideo)
{
    // 使用视频帧
    NDIlib_framesync_free_video(pFS, pVideo);
}
if (pAudio)
{
    NDIlib_framesync_free_audio(pFS, pAudio);
}

// 销毁帧同步器必须在销毁接收器之前
NDIlib_framesync_destroy(pFS);
```

## Demo 示例

以下是一个完整的 C++ 类，演示如何初始化 NDI、查找源、接收一帧视频并打印信息。

### NdiReceiverDemo.h

```cpp
#pragma once
#include "CoreMinimal.h"
#include "NDISDK/Public/Processing.NDI.Lib.h"

/**
 * 简单的 NDI 接收演示器
 */
class FNdiReceiverDemo
{
public:
    FNdiReceiverDemo();
    ~FNdiReceiverDemo();
    
    bool Initialize();
    void Shutdown();
    void Tick(float DeltaTime);
    
private:
    NDIlib_recv_instance_t NdiRecvInstance = nullptr;
    NDIlib_find_instance_t NdiFindInstance = nullptr;
    bool bInitialized = false;
};
```

### NdiReceiverDemo.cpp

```cpp
#include "NdiReceiverDemo.h"

FNdiReceiverDemo::FNdiReceiverDemo() {}
FNdiReceiverDemo::~FNdiReceiverDemo() { Shutdown(); }

bool FNdiReceiverDemo::Initialize()
{
    if (!NDIlib_initialize())
        return false;
    
    // 创建查找器，获取第一个源
    NDIlib_find_create_t findDesc;
    findDesc.show_local_sources = true;
    NdiFindInstance = NDIlib_find_create_v2(&findDesc);
    if (!NdiFindInstance) return false;
    
    // 等待片刻让源出现
    FPlatformProcess::Sleep(0.5f);
    
    uint32_t srcCount = 0;
    const NDIlib_source_t* pSources = NDIlib_find_get_current_sources(NdiFindInstance, &srcCount);
    if (srcCount == 0)
    {
        UE_LOG(LogTemp, Warning, TEXT("No NDI sources found"));
        return false;
    }
    
    // 连接到第一个源
    NDIlib_recv_create_v3_t recvDesc;
    recvDesc.source_to_connect_to = pSources[0];
    recvDesc.color_format = NDIlib_recv_color_format_BGRX_BGRA;
    recvDesc.bandwidth = NDIlib_recv_bandwidth_highest;
    recvDesc.allow_video_fields = true;
    
    NdiRecvInstance = NDIlib_recv_create_v3(&recvDesc);
    if (!NdiRecvInstance)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create NDI receiver"));
        return false;
    }
    
    bInitialized = true;
    return true;
}

void FNdiReceiverDemo::Shutdown()
{
    if (NdiRecvInstance)
    {
        NDIlib_recv_destroy(NdiRecvInstance);
        NdiRecvInstance = nullptr;
    }
    if (NdiFindInstance)
    {
        NDIlib_find_destroy(NdiFindInstance);
        NdiFindInstance = nullptr;
    }
    if (bInitialized)
    {
        NDIlib_destroy();
        bInitialized = false;
    }
}

void FNdiReceiverDemo::Tick(float DeltaTime)
{
    if (!NdiRecvInstance) return;
    
    NDIlib_video_frame_v2_t* pVideo = nullptr;
    NDIlib_audio_frame_v2_t* pAudio = nullptr;
    NDIlib_metadata_frame_t* pMeta = nullptr;
    
    NDIlib_frame_type_e frameType = NDIlib_recv_capture_v2(NdiRecvInstance, &pVideo, &pAudio, &pMeta, 100);
    
    if (frameType == NDIlib_frame_type_video)
    {
        UE_LOG(LogTemp, Log, TEXT("Received video: %dx%d, FourCC=0x%08x"),
               pVideo->xres, pVideo->yres, pVideo->FourCC);
        NDIlib_recv_free_video_v2(NdiRecvInstance, pVideo);
    }
    else if (frameType == NDIlib_frame_type_audio)
    {
        NDIlib_recv_free_audio_v2(NdiRecvInstance, pAudio);
    }
    else if (frameType == NDIlib_frame_type_metadata)
    {
        NDIlib_recv_free_metadata(NdiRecvInstance, pMeta);
    }
}
```

## 模块依赖

本模块（`NDISDK`）为外部第三方库封装，不依赖任何 UE 模块，编译时只需链接系统动态库。使用本模块的代码需在 `Build.cs` 中添加：

```csharp
PublicDependencyModuleNames.AddRange(new string[] { "NDISDK" });
```

**注意**：运行此插件需要用户安装 NDI Runtime（Windows/macOS/Linux），SDK 会自动从系统查找库文件。未安装时初始化会返回 false。

| 模块 | 用途 |
|---|---|
| `NDISDK` | 封装 NDI SDK 动态加载与函数指针，提供底层 C API |

## 维护状态

### 近期更新

- 2026-01-23 `1fa42043` [NDIMedia] Fix Just in Time Rendering (JITR) and timecode synchronization.
- 2026-01-23 `d0f5497d` [NDIMedia] Fix Framerate property to be editable in media profile.
- 2025-12-18 `c64f793f` [NDIMedia] Fixing low quality render when receiving an NDI stream with alpha channel.
- 2025-10-14 `ad8c4215` [NDI Media] Crash fix for NDIMediaOutput on Mac Platform - SupportsAnyThreadCapture is not supported
- 2025-10-07 `4137cc30` Mac: Add NDI Support

### 维护评价

该插件创建于 2025-10-07，目前不到一年，属于较新插件。最近更新频率高（平均每1-2个月有提交），内容涉及核心功能修复（JITR、时间同步、质量优化、平台兼容性），表明开发团队正在积极维护和改进。虽然标记为实验性（IsExperimentalVersion=true），但功能完整且持续迭代，推荐在 NDI 工作流中使用。注意：插件默认未启用，需在插件管理器中手动启用，且依赖用户安装 NDI Runtime。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/NDIMedia)
- [NDI SDK 官方下载](http://ndi.video/)
- [NDI 运行时安装指南](http://ndi.link/NDIRedistV6)