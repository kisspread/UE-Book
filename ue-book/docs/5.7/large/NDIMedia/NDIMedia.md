# NDI Media

> Implements media source and media output using NDI protocol

| 属性 | 值 |
|---|---|
| 中文名 | NDI 媒体 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（资产资源） |
| 模块 | `NDIMedia` (Runtime), `NDIMediaEditor` (Editor), `NDIMediaRendering` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-10-07 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/NDIMedia) | |

## 用途

NDIMedia 插件基于 NDI® (Network Device Interface) 协议，让 Unreal Engine 能够作为 NDI 发送端（Output）将画面和音频实时推送到 NDI 网络，也能作为接收端（Source）从网络接收其他 NDI 源的视频、音频和元数据。

它解决了传统 SDI 布线的限制，允许通过标准 IP 网络（千兆/万兆）传输高质量、低延迟的视音频信号，常用于虚拟制片、现场直播、远程制作、多机位同步等场景。

## 使用场景

- **虚拟制片/实时合成**：将 UE 渲染的画面通过 NDI 输出至切换台或合成软件（如 vMix、OBS），同时接收现场摄像机信号作为画面源。
- **多引擎协作**：多台 UE 实例通过 NDI 互传摄像机视角、共享渲染结果。
- **远程协作**：团队成员可通过 NDI 传输实时预览，无需占用 SDI 视频矩阵。
- **时间码同步**：使用 NDI 时间码提供器实现多台设备帧精确同步。

## 蓝图用法

NDIMedia 在蓝图中主要通过两个 UCLASS 资产类型暴露功能：

- `UNDIMediaSource` – 定义接收 NDI 流的媒体源（Media Source）
- `UNDIMediaOutput` – 定义发送 NDI 流的媒体输出（Media Output）

此外，`FNDIMediaReceiverPerformanceData` 结构体可在蓝图中读取接收端的性能统计数据。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Media Source` / `Create Media Output` (右击选择 "NDI Media Source" / "NDI Media Output") | 创建 NDI 媒体源或输出资产 | 蓝图界面 |
| `Get Media Player` → `Open Source` | 打开一个 NDI 媒体源，播放 NDI 流 | `UMediaPlayer` |
| `Media Output` → `Start Capture (Scene Viewport / Render Target / Texture Resource)` | 启动对场景视口、渲染目标或 RHI 资源的 NDI 输出 | `UNDIMediaOutput` (继承 `UMediaOutput`) |
| `Get NDI Source Settings` (如有提供) | 读取当前 NDI 源的名称、带宽、音频/视频捕获开关等参数 | `FNDISourceSettings` |
| `Get Receiver Performance` (如有提供) | 获取接收端的视频/音频/元数据帧数及丢帧数 | `FNDIMediaReceiverPerformanceData` |

### 使用示例（蓝图描述）

**发送 NDI 流**：
1. 在内容浏览器中创建一个 `NDI Media Output` 资产（右键 → Media → NDI Media Output）。
2. 在关卡蓝图或 Actor 中，获取该资产并调用 `Media Output → Start Capture`，选择 `Scene Viewport` 将视口输出到 NDI 网络。
3. 可在 `Event Tick` 中读取 `Media Output` 的 `Capture State` 以监控状态。

**接收 NDI 流**：
1. 创建 `NDI Media Source` 资产（右键 → Media → NDI Media Source），在细节面板中配置 `Configuration`（选择 NDI 设备）和带宽模式。
2. 创建 `Media Player` 和一个 `Media Texture`，调用 `Open Source` 并连接刚才创建的 NDI Media Source。
3. 将 `Media Texture` 应用到材质或 UI 上显示画面。

**时间码提供器**：
1. 在项目设置或 GameInstance 中添加一个 `NDI Media Timecode Provider` 组件。
2. 配置 `Timecode Configuration` 为 NDI 源的时间码信息，即可同步引擎时间码。

## C++ 用法

### 头文件引入

```cpp
#include "NDIMediaModule.h"
#include "NDIMediaCapture.h"   // 若使用发送端
#include "NDIMediaSource.h"    // 若使用接收端
#include "NDIMediaOutput.h"
#include "Player/NDIStreamReceiver.h" // 直接操作接收器
```

### 基本用法

#### 发送 NDI 帧（运行时创建输出并捕获）

```cpp
// 创建一个 NDI 输出实例（通常在 Actor 或 GameInstance 中）
UNDIMediaOutput* MediaOutput = NewObject<UNDIMediaOutput>();
MediaOutput->SourceName = TEXT("My NDI Camera");
MediaOutput->FrameRate = FFrameRate(60, 1);
MediaOutput->bOverrideDesiredSize = true;
MediaOutput->DesiredSize = FIntPoint(1920, 1080);

// 启动捕获（例如从 RenderTarget 或 Viewport）
UMediaCapture* Capture = MediaOutput->CreateMediaCapture();
Capture->CaptureSceneViewport(SceneViewport, EMediaCaptureSceneViewportOptions::RenderAfterPresent);
```
*取自 Source/NDIMedia/Private/NDIMediaCapture.cpp 中的 OnFrameCaptured_RenderingThread 使用参考*

#### 接收 NDI 流（直接使用流接收器）

```cpp
#include "NDIMediaModule.h"
#include "Player/NDIStreamReceiver.h"

void MyReceiver::StartReceiving(const FString& SourceName)
{
    FNDIMediaModule* Module = FNDIMediaModule::Get();
    if (!Module) return;

    TSharedPtr<FNDIStreamReceiver> Receiver = MakeShared<FNDIStreamReceiver>(Module->GetNDIRuntimeLibrary());
    FNDISourceSettings Settings;
    Settings.SourceName = SourceName;
    Settings.bCaptureVideo = true;
    Settings.bCaptureAudio = false;
    Settings.Bandwidth = ENDIReceiverBandwidth::Highest;

    Receiver->Initialize(Settings, FNDIStreamReceiver::ECaptureMode::Manual);

    // 绑定帧接收回调
    Receiver->OnVideoFrameReceived().AddLambda([](FNDIStreamReceiver* Recv, const NDIlib_video_frame_v2_t& Frame, const FTimespan& Time)
    {
        // 处理视频帧
    });
}
```
*基于 Source/NDIMedia/Private/Player/NDIStreamReceiver.h 中的接口*

#### 使用 NDI 时间码提供器

```cpp
// 创建并提供给引擎
UNDIMediaTimecodeProvider* TimecodeProvider = NewObject<UNDIMediaTimecodeProvider>();
TimecodeProvider->TimecodeConfiguration.MediaConfiguration.MediaConnection.Device.DeviceName = TEXT("My NDI Source");
TimecodeProvider->TimecodeConfiguration.MediaConfiguration.MediaMode.FrameRate = FFrameRate(30, 1);

// 注册为引擎时间码提供器
GEngine->SetTimecodeProvider(TimecodeProvider);
```
*参考 Source/NDIMedia/Public/NDIMediaTimecodeProvider.h*

### 进阶用法

#### 通过 FNDIStreamReceiver 收发元数据

```cpp
// 向发送者发送元数据（XML 格式 或 元素/属性形式）
Receiver->SendMetadataFrame(TEXT("<info>Hello from UE</info>"));
Receiver->SendMetadataFrameAttr(TEXT("Frame"), TEXT("123"));
Receiver->SendMetadataFrameAttrs(TEXT("Camera"), {{ TEXT("ptz"), TEXT("pan=10 tilt=20") }});
```
*基于 Source/NDIMedia/Private/Player/NDIStreamReceiver.h 中的 SendMetadataFrame/Attr/Attrs 方法*

#### 管理共享接收器（FNDIStreamReceiverManager）

`FNDIStreamReceiverManager` 允许多个客户端（如播放器和时间码提供器）共享同一个 NDI 流接收器，避免重复连接。

```cpp
FNDIStreamReceiverManager& Manager = FNDIMediaModule::Get()->GetStreamReceiverManager();
if (auto Existing = Manager.FindReceiver(TEXT("StreamA")))
{
    // 重用现有接收器
}
else
{
    auto NewReceiver = MakeShared<FNDIStreamReceiver>(...);
    Manager.AddReceiver(NewReceiver);
}
```
*参考 Source/NDIMedia/Private/Player/NDIStreamReceiverManager.h*

## Demo 示例

以下是一个最小化的 C++ Actor，实现接收 NDI 流并在材质上显示（省略了材质动态实例化的细节）。

**MyNDIReceiver.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyNDIReceiver.generated.h"

UCLASS()
class AMyNDIReceiver : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "NDI")
    FString SourceName = TEXT("My NDI Source");

private:
    TSharedPtr<class FNDIStreamReceiver> Receiver;
    class UMediaTexture* MediaTexture = nullptr;
};
```

**MyNDIReceiver.cpp**
```cpp
#include "MyNDIReceiver.h"
#include "NDIMediaModule.h"
#include "Player/NDIStreamReceiver.h"
#include "MediaIOCorePlayerBase.h" // 用于 FMediaIOCoreTextureSampleBase
#include "MediaTexture.h"

void AMyNDIReceiver::BeginPlay()
{
    Super::BeginPlay();

    FNDIMediaModule* Module = FNDIMediaModule::Get();
    if (!Module) return;

    TSharedPtr<FNDIMediaRuntimeLibrary> Lib = Module->GetNDIRuntimeLibrary();
    if (!Lib) return;

    Receiver = MakeShared<FNDIStreamReceiver>(Lib);
    FNDISourceSettings Settings;
    Settings.SourceName = SourceName;
    Settings.bCaptureVideo = true;
    Settings.Bandwidth = ENDIReceiverBandwidth::Highest;

    if (Receiver->Initialize(Settings, FNDIStreamReceiver::ECaptureMode::Manual))
    {
        // 在每帧 Tick 中手动 FetchVideo 来获取新帧（实际生产代码应使用 Timer 或 Tick）
        GetWorldTimerManager().SetTimerForNextTick(this, [this]()
        {
            // 此处可绑定 OnVideoFrameReceived 回调来更新媒体纹理
        });
    }
}

void AMyNDIReceiver::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (Receiver.IsValid())
    {
        Receiver->Shutdown();
        Receiver.Reset();
    }
    Super::EndPlay(EndPlayReason);
}
```

> 注意：实际生产中建议使用 `UNDIMediaSource` + `UMediaPlayer` 的蓝图/标准路径；直接使用 FNDIStreamReceiver 适合对帧处理有更高控制需求的场景。

## 模块依赖

以下模块是使用 NDIMedia 时，你的项目模块需要依赖的**独特依赖**（标准 Core/Engine/Slate 等已省略）：

| 模块 | 用途 |
|---|---|
| `MediaIOFramework` | 提供媒体 IO 配置、设备提供者、通用媒体基础类 |
| `MediaIOCore` | 提供媒体 IO 核心类型（FMediaIOCoreTextureSampleBase 等） |
| `NDISDK` (第三方) | NDI® SDK 的 C API 和 C++ 封装，用于底层 NDI 操作 |

> 如果你的模块仅使用 `UNDIMediaSource` / `UNDIMediaOutput` 蓝图资产，则只需在 `.Build.cs` 中添加 `"NDIMedia"` 到 `PublicDependencyModuleNames`；若直接操作内部类（如 `FNDIStreamReceiver`），则还需添加 `"NDISDK"`。

## 维护状态

### 近期更新

```
- 2026-01-23 1fa4204 — [NDIMedia] Fix Just in Time Rendering (JITR) and timecode synchronization.
- 2026-01-23 d0f5497 — [NDIMedia] Fix Framerate property to be editable in media profile.
- 2025-12-18 c64f793 — [NDIMedia] Fixing low quality render when receiving an NDI stream with alpha channel.
- 2025-10-14 ad8c421 — [NDI Media] Crash fix for NDIMediaOutput on Mac Platform - SupportsAnyThreadCapture is not supported
- 2025-10-07 4137cc3 — Mac: Add NDI Support
```

### 维护评价

NDIMedia 插件创建于 2025 年 10 月，诞生不到半年，但已进行多次重要修复和功能改进（JITR、时间码同步、帧率编辑、Alpha 通道质量、Mac 崩溃修复）。近期更新活跃（2026 年 1 月仍有修复），表明该插件处于积极开发维护阶段。

- **状态**：活跃维护，持续修复问题并优化性能。
- **建议**：可以作为生产环境使用，但需注意其为实验性插件，API 可能仍在调整。
- **已知限制**：Mac 上 `SupportsAnyThreadCapture` 不支持（已修复为不使用）；10 位像素格式暂不支持（代码注释中提到）。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/NDIMedia)
- [官方文档](https://docs.unrealengine.com/)（搜索 "NDI Media" 获取最新说明）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/NDIMedia/Tests)（如存在）