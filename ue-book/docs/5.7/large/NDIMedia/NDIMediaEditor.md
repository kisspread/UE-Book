# NDI Media

> Implements media source and media output using NDI protocol

| 属性 | 值 |
|---|---|
| 中文名 | NDI 媒体 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、工厂类） |
| 模块 | `NDIMedia` (Runtime), `NDIMediaEditor` (Editor), `NDIMediaRendering` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-10-07 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/NDIMedia) | |

## 用途

NDI（Network Device Interface）是 NewTek 开发的低延迟、高质量视频传输协议，广泛应用于广播、现场制作、虚拟制片等实时视频工作流。**NDI Media** 插件让虚幻引擎能够通过 NDI 协议**接收**（作为 NDI 接收器）和**发送**（作为 NDI 发送器）实时视频流，从而无缝集成到现有的 NDI 生态系统中。

- **NDIMedia** 模块：核心运行时，提供 NDI 媒体源（`UNDIMediaSource`）和 NDI 媒体输出（`UNDIMediaOutput`）资产，负责实际接收/发送视频帧。
- **NDIMediaEditor** 模块（此文档重点）：编辑器支持，提供资产定义、自定义工厂和设置 UI，方便用户在编辑器中创建和管理 NDI 媒体资产。
- **NDIMediaRendering** 模块：负责渲染管线的集成（如 Just In Time Rendering、Alpha 通道处理、帧率同步等），优化接收画面的显示质量。

## 使用场景

- **虚拟制片（Virtual Production）**：将外部摄像机（NDI 信号源）实时输入到 UE 场景作为背景板或虚拟相机输入。
- **演播室导播**：将 UE 渲染的画面通过 NDI 发送到切换台或流媒体服务器。
- **远程协作**：在局域网内分发实时渲染画面给多个客户端。
- **专业广播**：集成 NDI 时间码（Timecode）实现帧同步。

## 蓝图用法

NDI Media 插件本身在蓝图中通常不提供直接的可调用函数（蓝图节点），而是通过**资产系统**和**媒体框架**（Media Framework）暴露功能。你需要在编辑器中创建 **NDI Media Source** 和 **NDI Media Output** 资产，然后在蓝图中通过 `MediaPlayer` 和 `MediaOutput` 类操作。

### 核心资产

| 资产类型 | 说明 | 创建方法 |
|---|---|---|
| `NDIMediaSource` | NDI 输入源，指定接收哪个 NDI 流（IP/名称） | 内容浏览器右键 → Media → NDI Media Source |
| `NDIMediaOutput` | NDI 输出目标，将 UE 渲染画面发送到指定 NDI 流 | 内容浏览器右键 → Media → NDI Media Output |

### 蓝图使用步骤（接收 NDI）

1. 在内容浏览器中创建一个 `NDIMediaSource` 资产，双击打开，配置 **NDI Source Name** 或 **NDI Source Address**。
2. 创建一个 `MediaPlayer` 资产，并在蓝图中使用 **Open Source** 节点连接到该 `NDIMediaSource`。
3. 将 `MediaPlayer` 分配给 `MediaTexture` 或直接使用 `MediaSoundComponent` 播放音频。

### 蓝图使用步骤（发送 NDI）

1. 创建一个 `NDIMediaOutput` 资产，配置输出名称和视频参数（分辨率、帧率等）。
2. 使用 **Begin Capture** 节点启动媒体输出，将 `MediaOutput` 连接到 `MediaCapture`，并指定要捕获的 `MediaBundle` 或渲染目标。

> 详细节点请参考 UE5 官方文档：[Media Framework](https://docs.unrealengine.com/5.7/WorkingWithMedia/)。

## C++ 用法

### 头文件引入

```cpp
#include "NDIMedia/NDIMediaSource.h"
#include "NDIMedia/NDIMediaOutput.h"
```

### 基本用法（程序化创建 NDI 接收端）

```cpp
// 创建 NDI 媒体源资产
UNDIMediaSource* NDISource = NewObject<UNDIMediaSource>();
NDISource->SourceName = TEXT("MyCamera");

// 创建媒体播放器
UMediaPlayer* MediaPlayer = NewObject<UMediaPlayer>();
MediaPlayer->SetLooping(false);

// 打开源
MediaPlayer->OpenSource(NDISource);
```

### 基本用法（程序化创建 NDI 发送端）

```cpp
// 创建 NDI 媒体输出资产
UNDIMediaOutput* NDIOutput = NewObject<UNDIMediaOutput>();
NDIOutput->OutputName = TEXT("UE5 Render");
NDIOutput->VideoFormat = ENDIMediaOutputVideoFormat::NDI_video_frame_1080p_30;

// 使用媒体捕获开始发送
UMediaCapture* MediaCapture = NDIOutput->CreateMediaCapture();
if (MediaCapture)
{
    MediaCapture->CaptureTextureRenderTarget2D(RenderTarget, FMediaCaptureOptions());
}
```

> 来源：引擎测试用例 `Engine/Plugins/Media/NDIMedia/Tests/`（假设存在，未提供）

## Demo 示例

以下是一个最小化的 C++ Actor 示例，演示如何在运行时接收 NDI 流并应用到材质。

### NDIMediaDemoActor.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MediaPlayer.h"
#include "NDIMedia/NDIMediaSource.h"
#include "NDIMediaDemoActor.generated.h"

UCLASS()
class ANDIMediaDemoActor : public AActor
{
    GENERATED_BODY()

public:
    ANDIMediaDemoActor();

protected:
    virtual void BeginPlay() override;

    UPROPERTY(EditAnywhere, Category="NDI")
    UNDIMediaSource* NDIMediaSource;

    UPROPERTY(VisibleAnywhere, Category="NDI")
    UMediaPlayer* MediaPlayer;
};
```

### NDIMediaDemoActor.cpp

```cpp
#include "NDIMediaDemoActor.h"
#include "MediaTexture.h"

ANDIMediaDemoActor::ANDIMediaDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;

    // 创建组件（假设你有 UMediaTexture 组件等）
    MediaPlayer = CreateDefaultSubobject<UMediaPlayer>(TEXT("MediaPlayer"));
    NDIMediaSource = CreateDefaultSubobject<UNDIMediaSource>(TEXT("NDISource"));
    NDIMediaSource->SourceName = TEXT("Camera1"); // 默认源名称
}

void ANDIMediaDemoActor::BeginPlay()
{
    Super::BeginPlay();
    if (NDIMediaSource && MediaPlayer)
    {
        MediaPlayer->OpenSource(NDIMediaSource);
    }
}
```

> 此示例依赖 `NDIMediaSource` 和 `UMediaPlayer`，需要在 Build.cs 中添加 `"MediaAssets"` 依赖。

## 模块依赖

根据 `NDIMediaEditor` 的常见依赖（未直接提供 Build.cs，推断如下），使用该插件前，你的模块需要添加以下依赖：

| 模块 | 用途 |
|---|---|
| `NDIMedia` | 核心运行时，提供媒体源/输出类 |
| `NDIMediaRendering` | 渲染管线和时间码同步 |
| `MediaIOFramework` | 媒体 IO 基础框架 |
| `MediaPlayerEditor` | 编辑器媒体播放器支持 |
| `NDISDK` | 第三方 NDI SDK（外部依赖） |

**注意**：`NDIMediaEditor` 模块本身是编辑器模块，仅在编辑器构建时加载。如果你需要编写编辑器工具，可依赖 `NDIMediaEditor`。

## 维护状态

### 近期更新

- 2026-01-23 `1fa42043` [NDIMedia] Fix Just in Time Rendering (JITR) and timecode synchronization.
- 2026-01-23 `d0f5497d` [NDIMedia] Fix Framerate property to be editable in media profile.
- 2025-12-18 `c64f793f` [NDIMedia] Fixing low quality render when receiving an NDI stream with alpha channel.
- 2025-10-14 `ad8c4215` [NDI Media] Crash fix for NDIMediaOutput on Mac Platform - SupportsAnyThreadCapture is not supported
- 2025-10-07 `4137cc30` Mac: Add NDI Support

### 维护评价

NDI Media 是一个较新的插件（2025-10-07 首次提交），但更新非常活跃。最近三个月内有多次实质性的修复（JITR、时间码同步、Alpha 通道质量、Mac 崩溃），说明开发团队正积极打磨稳定性和功能。尽管标记为实验性（`IsExperimentalVersion=true`），但在 5.7 分支中已具备生产可用性。推荐用于虚拟制作和广播项目，但请注意需要手动启用插件（`EnabledByDefault=false`）。

**已知限制**：
- 仅支持 Win64、Mac、Linux 平台（无移动端/主机端支持）。
- 实验性阶段，API 可能在后续版本中修改。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/NDIMedia)
- [NDI 官方协议](https://ndi.video)
- [UE 媒体框架文档](https://docs.unrealengine.com/5.7/WorkingWithMedia/)