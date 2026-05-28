# NDI Media

> Implements media source and media output using NDI protocol

| 属性 | 值 |
|---|---|
| 中文名 | NDI 媒体 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NDIMedia` (Runtime), `NDIMediaEditor` (Editor), `NDIMediaRendering` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-03-14 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/NDIMedia) | |

## 用途

NDI Media 插件集成了 NDI（Network Device Interface）SDK，使 Unreal Engine 5 项目能够通过局域网实时接收和发送高质量的视频、音频流。它主要解决了虚拟制作（Virtual Production）、现场直播、实时可视化等领域中，UE 项目与其他支持 NDI 的软件（如 vMix, OBS, Wirecast 等）或硬件设备之间进行低延迟、高画质媒体流交换的需求。插件封装了 NDI 协议的收发功能，并将其深度集成到 UE 的媒体框架（Media Framework）中，使得 NDI 源可以像其他媒体源（如视频文件、流媒体链接）一样被轻松使用。

## 使用场景

- **虚拟制作**：将 UE 中的实时渲染画面通过 NDI 推送给导播切换台（如 vMix），实现虚实结合的直播或多机位切换。
- **多软件协作**：将 UE 的渲染输出作为 NDI 源发送给其他软件（如 After Effects, TouchDesigner）进行后期合成或特效处理。
- **现场活动**：在大型活动、演出中，将 UE 生成的实时内容（如虚拟舞台、数据可视化）无缝集成到现场视频信号流中。
- **多机位预览**：在 UE 编辑器内通过 NDI 接收来自摄像机或其他视频源的信号，用于场景对位或实时预览。
- **媒体资产审查**：团队成员可以通过 NDI 客户端实时观看 UE 编辑器内的视口或渲染队列输出，方便进行远程审片。

## 蓝图用法

NDI Media 插件主要通过 UE 的媒体框架接口暴露功能。虽然具体的 `BlueprintCallable` 节点定义需要查阅生成的头文件，但核心使用模式是配置 `MediaSource` 和 `MediaOutput` 资产。

### 核心资产

| 资产类型 | 说明 |
|---|---|
| `UNDIMediaSource` | 用于从 NDI 网络接收媒体流。在蓝图中可以创建此资产，并设置要连接的 NDI 源名称。 |
| `UNDIMediaOutput` | 用于将 UE 中的媒体（如摄像机视图、合成输出）作为 NDI 流发送到网络。 |

### 使用示例（蓝图描述）

1.  **接收 NDI 流**：
    - 在内容浏览器中右键，选择 `Media` -> `NDI Media Source` 创建资产。
    - 在资产详情中，设置 `SourceName` 属性为你想要接收的 NDI 源名称（如 `“DESKTOP-ABC (My Camera)”`）。
    - 在场景中放置一个 `Media Player` 资产，并在蓝图中调用 `Open Source` 节点，传入上一步创建的 `UNDIMediaSource` 对象。
    - 将 `Media Player` 关联到一个 `Media Texture`，再将该纹理应用到 `Media Bundle` 或 `Image` 控件上即可显示画面。

2.  **发送 UE 画面**：
    - 在内容浏览器中右键，选择 `Media` -> `NDI Media Output` 创建资产。
    - 在资产详情中，设置 `OutputName` 属性为你希望在网络上显示的 NDI 源名称（如 `“My UE Stream”`）。
    - 在需要推流的摄像机或渲染目标（Render Target）的属性中，找到 `Media Output` 选项，选择上一步创建的 `UNDIMediaOutput` 资产。
    - 通过调用摄像机组件的 `Start Capture` 或相关函数开始推流。其他 NDI 客户端即可发现并接收该信号。

## C++ 用法

NDI 的核心功能通过 C++ API 实现，适用于需要更底层控制、高性能或多线程处理的场景。

### 头文件引入

```cpp
// 引入NDI SDK的核心头文件
#include "Processing.NDI.Lib.h"

// 引入UE封装的NDI媒体模块头文件（如果模块提供了封装类）
// #include "NDIMediaModule.h"
```

### 基本用法 (发送视频帧)

以下示例展示了如何直接使用 NDI SDK 创建一个发送端并发送一个简单的视频帧。来源：基于 NDI SDK 头文件 `Processing.NDI.Send.h` 和 `Processing.NDI.structs.h` 的典型用法。

```cpp
#include "Processing.NDI.Lib.h"

// 1. 初始化 NDI
if (!NDIlib_initialize()) {
    // 初始化失败处理
    return;
}

// 2. 创建发送端
NDIlib_send_create_t send_desc;
send_desc.p_ndi_name = "UE5_NDI_Out";
send_desc.p_groups = nullptr;
send_desc.clock_video = true;
send_desc.clock_audio = false;

NDIlib_send_instance_t pNDI_send = NDIlib_send_create(&send_desc);
if (!pNDI_send) {
    // 创建失败处理
    NDIlib_destroy();
    return;
}

// 3. 准备一个简单的测试视频帧 (例如 1920x1080 蓝色)
const int width = 1920;
const int height = 1080;
std::vector<uint8_t> frameBuffer(width * height * 4); // RGBA
for (int i = 0; i < width * height; i++) {
    frameBuffer[i * 4 + 0] = 0;   // R
    frameBuffer[i * 4 + 1] = 0;   // G
    frameBuffer[i * 4 + 2] = 255; // B
    frameBuffer[i * 4 + 3] = 255; // A
}

// 4. 配置视频帧结构体
NDIlib_video_frame_v2_t video_frame;
video_frame.xres = width;
video_frame.yres = height;
video_frame.FourCC = NDIlib_FourCC_video_type_BGRA;
video_frame.frame_rate_N = 30000;
video_frame.frame_rate_D = 1001;
video_frame.line_stride_in_bytes = width * 4;
video_frame.p_data = frameBuffer.data();
video_frame.timecode = NDIlib_send_timecode_synthesize;
video_frame.p_metadata = nullptr;

// 5. 发送视频帧 (异步方式)
NDIlib_send_send_video_async_v2(pNDI_send, &video_frame);

// 注意：异步发送后，frameBuffer 内存不能立即释放或修改，
// 需等待下一次调用 NDIlib_send_send_video 或销毁发送端。

// 6. 清理（在不再需要时）
// NDIlib_send_destroy(pNDI_send);
// NDIlib_destroy();
```

### 进阶用法 (接收与帧同步)

以下示例展示了如何创建一个接收端，并使用帧同步器（FrameSync）来平滑地获取视频帧，适用于需要稳定帧率输出的场景。来源：基于 `Processing.NDI.Recv.h` 和 `Processing.NDI.FrameSync.h`。

```cpp
#include "Processing.NDI.Lib.h"
#include <vector>

void ReceiveAndDisplayWithFrameSync() {
    NDIlib_initialize();

    // 1. 创建查找器以发现源
    NDIlib_find_instance_t pNDI_find = NDIlib_find_create_v2(nullptr);
    if (!pNDI_find) return;

    // 等待并获取源列表
    uint32_t no_sources = 0;
    const NDIlib_source_t* p_sources = nullptr;
    while (!p_sources) {
        NDIlib_find_wait_for_sources(pNDI_find, 1000); // 等待1秒
        p_sources = NDIlib_find_get_current_sources(pNDI_find, &no_sources);
    }

    // 假设使用第一个发现的源
    NDIlib_source_t source_to_connect = p_sources[0];
    NDIlib_find_destroy(pNDI_find); // 查找完成，销毁查找器

    // 2. 创建接收端
    NDIlib_recv_create_v3_t recv_desc;
    recv_desc.source_to_connect_to = source_to_connect;
    recv_desc.color_format = NDIlib_recv_color_format_BGRX_BGRA;
    recv_desc.bandwidth = NDIlib_recv_bandwidth_highest;
    recv_desc.allow_video_fields = false;
    recv_desc.p_ndi_recv_name = "UE5_FrameSync_Receiver";

    NDIlib_recv_instance_t pNDI_recv = NDIlib_recv_create_v3(&recv_desc);
    if (!pNDI_recv) {
        NDIlib_destroy();
        return;
    }

    // 3. 创建帧同步器
    NDIlib_framesync_instance_t pNDI_framesync = NDIlib_framesync_create(pNDI_recv);
    if (!pNDI_framesync) {
        NDIlib_recv_destroy(pNDI_recv);
        NDIlib_destroy();
        return;
    }

    // 4. 主循环，使用帧同步器获取视频
    bool running = true;
    while (running) {
        NDIlib_video_frame_v2_t video_frame;
        // 从帧同步器获取一帧（时间基校正，平滑）
        NDIlib_framesync_capture_video(pNDI_framesync, &video_frame, NDIlib_frame_format_type_progressive);

        if (video_frame.p_data) {
            // 在这里处理视频数据，例如上传到纹理
            // 注意：video_frame.p_data 的生命周期由帧同步器管理
            // ProcessVideoFrame(video_frame.p_data, video_frame.xres, video_frame.yres);
        }

        // 释放这一帧
        NDIlib_framesync_free_video(pNDI_framesync, &video_frame);

        // 可以在这里按固定帧率sleep，帧同步器会适配
        // FPlatformProcess::Sleep(1.0f / 30.0f); // 假设30fps

        // 检查退出条件
        // if (ShouldExit()) running = false;
    }

    // 5. 清理
    NDIlib_framesync_destroy(pNDI_framesync);
    NDIlib_recv_destroy(pNDI_recv);
    NDIlib_destroy();
}
```

## Demo 示例

一个最小化的、用于测试发送功能的 UE Actor 类。

**NDITestSender.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "NDITestSender.generated.h"

class USceneCaptureComponent2D;
class UTextureRenderTarget2D;

UCLASS()
class ANDITestSender : public AActor
{
    GENERATED_BODY()
    
public:
    ANDITestSender();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    // 定时发送帧
    void SendNextFrame();

    UPROPERTY(VisibleAnywhere)
    USceneCaptureComponent2D* SceneCapture;

    UPROPERTY(EditAnywhere)
    UTextureRenderTarget2D* RenderTarget;

    // NDI 相关的原始指针 (非UObject，需手动管理)
    void* NDI_SendInstance = nullptr;
    FTimerHandle SendTimerHandle;
};
```

**NDITestSender.cpp**
```cpp
#include "NDITestSender.h"
#include "Components/SceneCaptureComponent2D.h"
#include "Engine/TextureRenderTarget2D.h"
#include "Kismet/GameplayStatics.h"
#include "Processing.NDI.Lib.h" // 假设Build.cs中已正确配置NDI SDK路径

ANDITestSender::ANDITestSender()
{
    PrimaryActorTick.bCanEverTick = false;

    SceneCapture = CreateDefaultSubobject<USceneCaptureComponent2D>(TEXT("SceneCapture"));
    RootComponent = SceneCapture;
    SceneCapture->CaptureSource = ESceneCaptureSource::SCS_FinalColorLDR;
    SceneCapture->bCaptureEveryFrame = false;
    SceneCapture->bCaptureOnMovement = false;
}

void ANDITestSender::BeginPlay()
{
    Super::BeginPlay();

    // 初始化Render Target
    RenderTarget = NewObject<UTextureRenderTarget2D>();
    RenderTarget->InitAutoFormat(1920, 1080);
    SceneCapture->TextureTarget = RenderTarget;

    // 初始化NDI并创建发送端
    if (NDIlib_initialize())
    {
        NDIlib_send_create_t send_create;
        send_create.p_ndi_name = TCHAR_TO_UTF8(*GetName()); // 使用Actor名称作为NDI源名
        send_create.p_groups = nullptr;
        send_create.clock_video = true;
        send_create.clock_audio = false;

        NDI_SendInstance = NDIlib_send_create(&send_create);
        if (NDI_SendInstance)
        {
            // 启动定时发送，例如30fps
            GetWorldTimerManager().SetTimer(SendTimerHandle, this, &ANDITestSender::SendNextFrame, 1.0f / 30.0f, true);
        }
    }
}

void ANDITestSender::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    GetWorldTimerManager().ClearTimer(SendTimerHandle);
    if (NDI_SendInstance)
    {
        NDIlib_send_destroy((NDIlib_send_instance_t)NDI_SendInstance);
        NDI_SendInstance = nullptr;
    }
    NDIlib_destroy();
    Super::EndPlay(EndPlayReason);
}

void ANDITestSender::SendNextFrame()
{
    if (!RenderTarget || !NDI_SendInstance) return;

    // 捕获场景到Render Target
    SceneCapture->CaptureScene();

    // 读取Render Target像素 (简化示例，实际可能需要异步回读和缓冲区翻转)
    FRenderTarget* RT = RenderTarget->GameThread_GetRenderTargetResource();
    if (RT)
    {
        TArray<FColor> Bitmap;
        RT->ReadPixels(Bitmap);

        NDIlib_video_frame_v2_t video_frame;
        video_frame.xres = RenderTarget->SizeX;
        video_frame.yres = RenderTarget->SizeY;
        video_frame.FourCC = NDIlib_FourCC_video_type_BGRA;
        video_frame.frame_rate_N = 30000;
        video_frame.frame_rate_D = 1001;
        video_frame.line_stride_in_bytes = RenderTarget->SizeX * 4;
        video_frame.p_data = (uint8_t*)Bitmap.GetData();
        video_frame.timecode = NDIlib_send_timecode_synthesize;

        // 异步发送
        NDIlib_send_send_video_async_v2((NDIlib_send_instance_t)NDI_SendInstance, &video_frame);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MediaIOFramework` | UE 媒体 IO 框架，是 MediaSource 和 MediaOutput 的基类框架 |
| `MediaPlayerEditor` | 编辑器内媒体播放器的 UI 和资产编辑功能 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `96b8b04b` | Media IO: Fix to recent CL 54396736 for ImgMedia and NDI players emitting incorrect SourceOpened ana | 修复了 NDI 和 ImgMedia 播放器发送错误 `SourceOpened` 分析事件的问题 |
| 2026-05-23 | `42746f7a` | Media IO: Added additional engine analytics information to various media players and capture and pro | 为 NDI 等媒体播放器和捕获工具添加了额外的引擎分析信息 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the ... | 将虚拟制作相关资产（可能包括NDI相关资产）移至不同资产类别 |
| 2026-05-12 | `c657503b` | [Media] Add missing UAssetDefinition entries for concrete UMediaSource and UMediaOutput subclasses t | 为 `UNDIMediaSource` 等媒体源/输出子类添加了缺失的资产定义条目 |
| 2026-04-23 | `efcad028` | HDR: Fix HDR normalization factor across media causing incorrect brightness levels going from/to the | 修复了跨媒体（可能包括NDI流）的 HDR 归一化因子，解决了亮度不正确的问题 |

### 维护评价

- **活跃维护**：插件仍在持续维护中。最近的更新（截至2026年5月）表明 Epic Games 团队正在积极修复 bug、优化性能（如 HDR 修复）并增加分析功能，与 UE5 核心引擎的更新保持同步。
- **实验性状态**：`.uplugin` 中 `IsExperimentalVersion: true` 且 `EnabledByDefault: false`，表明该插件仍被视为实验性功能，API 和功能在未来版本中可能发生不兼容的变更。
- **使用建议**：对于虚拟制作、广播等专业且对新功能需求强烈的领域，该插件是可靠的选择，但应做好适应未来 API 变化的准备。对于生产环境，建议进行充分的测试，并关注 Epic 的更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/NDIMedia)
- [官方文档](https://docs.unrealengine.com/) (通用 UE 文档，无 NDI 插件专属页)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/NDIMedia/Tests) (如果存在)