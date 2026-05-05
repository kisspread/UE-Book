# NVIDIA Rivermax Media Streaming

> Adding NVIDIA Rivermax capabilities for Media Captures and Media Players

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `RivermaxMedia` (Runtime), `RivermaxMediaEditor` (Editor), `RivermaxMediaFactory` (RuntimeNoCommandlet) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-03-30 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Rivermax/RivermaxMedia) | |

## 用途

RivermaxMedia 是 UE5 对 [NVIDIA Rivermax](https://developer.nvidia.com/rivermax) SDK 的 Media Framework 集成，基于 SMPTE ST 2110 标准实现 IP 视频的收发。

该 plugin 解决的核心问题：在虚拟制片（Virtual Production）场景中，需要通过标准 IP 网络（而非 SDI/HDMI）以超低延迟传输和接收高分辨率视频流。NVIDIA Rivermax 利用支持 RDMA 的网卡（如 NVIDIA ConnectX 系列）直接在 GPU 与 NIC 之间传输数据（GPUDirect），绕过系统内存，实现亚帧级延迟。

具体功能：
- **Media Source**（输入）：接收 ST 2110-20 视频流，支持 YUV422 / RGB 等多种像素格式，可选 GPUDirect 路径直接写入 GPU 内存
- **Media Output**（输出）：将 UE5 渲染内容编码为 ST 2110-20 视频流 + ST 2110-40 ANC 辅助数据流（如 Timecode）发送到网络
- **Genlock / CustomTimeStep**：通过 PTP（IEEE 1588）时钟实现引擎帧率与外部同步信号对齐（ST 2059 标准）
- **Timecode Provider**：从 PTP 时钟获取时间码，支持 TAI→UTC 转换和 LTC 时间码对齐

## 使用场景

- **LED Volume 摄影棚**：nDisplay 多机渲染集群通过 ST 2110 IP 网络同步分发视频帧，每个渲染节点通过 RivermaxMedia Source 接收帧并锁定
- **远程合成（Compositing）**：将 UE5 实时渲染画面通过 RivermaxMedia Output 推送到第三方合成软件（如 Nuke），替代 SDI 硬件链路
- **IP 基础设施替换 SDI**：已有 ST 2110 网络设施的演播室，用 Rivermax 替换 DeckLink/AJA 等采集卡方案
- **多引擎帧同步**：利用 PTP Genlock 确保多个 UE5 实例以完全相同的帧率和相位运行

## 蓝图用法

### Media Source（接收流）

在 Content Browser 中右键 → Media → **NVIDIA Rivermax Source** 创建资产，或在 Media Player 组件中选择 Source。

| 属性 | 说明 | 类型 |
|---|---|---|
| `Resolution` | 输入流分辨率（可选覆盖） | `FIntPoint` |
| `FrameRate` | 输入流帧率 | `FFrameRate` |
| `PixelFormat` | 像素格式：8bit/10bit YUV422、8bit/10bit/12bit RGB、16bit Float RGB | `ERivermaxMediaSourcePixelFormat` |
| `InterfaceAddress` | 网卡接口地址（支持通配符如 `192.168.0.*`） | `FString` |
| `StreamAddress` | 流地址（支持组播如 `228.1.1.1`） | `FString` |
| `Port` | 端口号（默认 50000） | `int32` |
| `bUseGPUDirect` | 启用 GPUDirect（NIC 直接到 GPU） | `bool` |

### Media Output（发送流）

在 Content Browser 中右键 → Media → **NVIDIA Rivermax Output** 创建资产。

| 属性 | 说明 | 类型 |
|---|---|---|
| `AlignmentMode` | 对齐模式：`AlignmentPoint`（ST 2059 时钟对齐）或 `FrameCreation`（帧创建对齐） | `ERivermaxMediaAlignmentMode` |
| `bDoContinuousOutput` | 无新帧时是否重复上一帧持续输出 | `bool` |
| `FrameLockingMode` | 帧锁定：`FreeRun`（丢帧继续）或 `BlockOnReservation`（阻塞等待） | `ERivermaxFrameLockingMode` |
| `PresentationQueueSize` | 输出队列大小（2-8） | `int32` |
| `VideoStream` | 视频流配置（分辨率/帧率/像素格式/网络地址/GPUDirect） | `FRivermaxVideoStream` |
| `AncStreams` | 辅助数据流列表（如 Timecode） | `TArray<FRivermaxAncStream>` |

### Media Capture

通过蓝图 `Create Media Capture` 节点，将 Media Output 绑定到 SceneViewport 或 RenderTarget 即可开始推流。

### CustomTimeStep（Genlock）

在 Project Settings → Engine → General Settings → Custom TimeStep 中设置为 `URivermaxCustomTimeStep`：

| 属性 | 说明 |
|---|---|
| `FrameRate` | Genlock 目标帧率 |
| `AlignmentPointDelayMS` | 对齐点后的延迟（毫秒） |
| `bEnableOverrunDetection` | 引擎跟不上时显示丢帧警告 |

### Timecode Provider

在 Project Settings → Engine → General Settings → Timecode 中设置为 `URivermaxTimecodeProvider`：

| 属性 | 说明 |
|---|---|
| `FrameRate` | 时间码帧率 |
| `PTPToLTCTimecodeFrameOffset` | PTP 与 LTC 时间码的帧偏移（默认 1） |
| `UTCSecondsOffset` | TAI→UTC 秒偏移（默认 37） |
| `DaylightSavingTimeHourOffset` | 夏令时小时偏移 |

## C++ 用法

### 头文件引入

```cpp
#include "RivermaxMediaSource.h"      // URivermaxMediaSource
#include "RivermaxMediaOutput.h"      // URivermaxMediaOutput, FRivermaxVideoStream
#include "RivermaxMediaCapture.h"     // URivermaxMediaCapture
#include "RivermaxCustomTimeStep.h"   // URivermaxCustomTimeStep
#include "RivermaxTimecodeProvider.h" // URivermaxTimecodeProvider
#include "IRivermaxMediaModule.h"     // IRivermaxMediaModule
```

### 基本用法：创建 Media Source 并打开播放

```cpp
// 创建 Rivermax Media Source
URivermaxMediaSource* Source = NewObject<URivermaxMediaSource>();
Source->Resolution = FIntPoint(1920, 1080);
Source->FrameRate = FFrameRate(24, 1);
Source->PixelFormat = ERivermaxMediaSourcePixelFormat::RGB_10bit;
Source->InterfaceAddress = TEXT("192.168.1.100");
Source->StreamAddress = TEXT("228.1.1.1");
Source->Port = 50000;
Source->bUseGPUDirect = true;

// 通过 Media Player 打开
UMediaPlayer* MediaPlayer = ...; // 获取或创建 Media Player
MediaPlayer->OpenSource(Source);
```

（来源：`Source/RivermaxMedia/Private/RivermaxMediaSource.cpp`）

### 基本用法：创建 Media Output 并推流

```cpp
// 创建 Rivermax Media Output
URivermaxMediaOutput* Output = NewObject<URivermaxMediaOutput>();
Output->VideoStream.Resolution = FIntPoint(1920, 1080);
Output->VideoStream.FrameRate = FFrameRate(24, 1);
Output->VideoStream.PixelFormat = ERivermaxMediaOutputPixelFormat::PF_10BIT_RGB;
Output->VideoStream.InterfaceAddress = TEXT("192.168.1.100");
Output->VideoStream.StreamAddress = TEXT("228.1.1.1");
Output->VideoStream.Port = 50000;
Output->VideoStream.bUseGPUDirect = true;
Output->AlignmentMode = ERivermaxMediaAlignmentMode::AlignmentPoint;
Output->bDoContinuousOutput = true;
Output->PresentationQueueSize = 2;

// 添加 ANC Timecode 流
FRivermaxAncStream AncStream;
AncStream.StreamType = ERivermaxAncStreamType::ST2110_40_TC;
AncStream.InterfaceAddress = TEXT("192.168.1.100");
AncStream.StreamAddress = TEXT("228.1.1.2");
AncStream.Port = 50001;
Output->AncStreams.Add(AncStream);

// 创建 Capture 并开始推流
UMediaCapture* Capture = Output->CreateMediaCapture();
Capture->CaptureSceneViewport(); // 或 CaptureRenderTarget(...)
```

（来源：`Source/RivermaxMedia/Private/RivermaxMediaOutput.cpp`）

### 进阶用法：获取输出帧信息

```cpp
URivermaxMediaCapture* RivermaxCapture = Cast<URivermaxMediaCapture>(Capture);
if (RivermaxCapture)
{
    UE::RivermaxCore::FPresentedFrameInfo FrameInfo;
    RivermaxCapture->GetLastPresentedFrameInformation(FrameInfo);
    // FrameInfo 包含最近一帧的呈现时间戳等信息
}
```

### 进阶用法：导出 SDP 文件

```cpp
// 将输出配置导出为 SDP 文件，供第三方播放器使用
Output->ExportSDP(TEXT("C:/output/stream.sdp"));
```

（来源：`Source/RivermaxMedia/Private/RivermaxMediaOutput.cpp`，`ExportSDP()` 方法）

## Demo 示例

### 最小推流示例

```cpp
// MyRivermaxStreamer.h
#pragma once
#include "GameFramework/Actor.h"
#include "MyRivermaxStreamer.generated.h"

UCLASS()
class AMyRivermaxStreamer : public AActor
{
    GENERATED_BODY()
public:
    void BeginPlay() override;

private:
    UPROPERTY()
    TObjectPtr<URivermaxMediaOutput> MediaOutput;

    UPROPERTY()
    TObjectPtr<UMediaCapture> MediaCapture;
};

// MyRivermaxStreamer.cpp
#include "MyRivermaxStreamer.h"
#include "RivermaxMediaOutput.h"

void AMyRivermaxStreamer::BeginPlay()
{
    Super::BeginPlay();

    MediaOutput = NewObject<URivermaxMediaOutput>();
    MediaOutput->VideoStream.FrameRate = FFrameRate(60, 1);
    MediaOutput->VideoStream.PixelFormat = ERivermaxMediaOutputPixelFormat::PF_10BIT_RGB;
    MediaOutput->VideoStream.StreamAddress = TEXT("228.1.1.1");
    MediaOutput->VideoStream.Port = 50000;
    MediaOutput->AlignmentMode = ERivermaxMediaAlignmentMode::AlignmentPoint;

    MediaCapture = MediaOutput->CreateMediaCapture();
    MediaCapture->CaptureSceneViewport();
}
```

**Build.cs 依赖**：
```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "RivermaxMedia",
    "MediaAssets",
    "MediaIOCore"
});
```

## 模块依赖

### RivermaxMedia（Runtime）

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `MediaAssets` | Media Framework 资产类型 |
| `MediaIOCore` | Media I/O 核心基类（`FMediaIOCorePlayerBase`、`UMediaCapture` 等） |
| `RivermaxCore` | NVIDIA Rivermax SDK 的 UE 封装（流管理、PTP 时钟、设备枚举） |
| `TimeManagement` | 时间码和 Genlock 基类（`UGenlockedCustomTimeStep`、`UGenlockedTimecodeProvider`） |
| `Engine` | 引擎核心（私有） |
| `OpenColorIO` | 色彩空间转换（私有） |
| `RenderCore` | 渲染核心（私有） |
| `RHI` | 渲染硬件接口（私有） |
| `RivermaxRendering` | Rivermax GPU 计算着色器（私有） |

### RivermaxMediaEditor（Editor）

| 模块 | 用途 |
|---|---|
| `MediaIOEditor` | Media I/O 编辑器集成 |
| `RivermaxEditor` | Rivermax 编辑器工具 |
| `DisplayClusterModularFeaturesEditor` | nDisplay 模块化特性集成 |
| `UnrealEd` | 编辑器框架 |
| `PropertyEditor` / `EditorStyle` | 属性面板自定义 |

### RivermaxMediaFactory（RuntimeNoCommandlet）

| 模块 | 用途 |
|---|---|
| `Media` | Media Player 工厂注册 |
| `MediaAssets` | 媒体资产管理 |
| `RivermaxMedia` | 运行时 Media Player 创建 |

## 维护状态

### 近期更新

1. **2025-10-06** `cefac2667e` — Media I/O: 修复异步任务中原始 this 指针捕获导致的潜在崩溃。解决纹理样本在任务执行前被销毁时的 use-after-free 问题。

2. **2025-10-03** `360093466e` — 修复 16bit RGB 流输入时因 dispatch group count 超出最大限制导致画面被裁剪的问题。代码清理和小幅改进。

3. **2025-09-12** `b9d90b691b` — ANC 输出 UI 美化，修复 IP 地址值未保存的问题。

### 维护评价

- **活跃维护** ✅：最近 6 个月内有多次实质性更新（bug 修复 + 功能改进）
- **持续演进**：UE 5.5 中废弃了旧的 PlayerMode/Framelock 接口，统一到 MediaIOCore 的 SampleEvaluationType 体系；UE 5.7 中进一步将 Output 的视频参数迁移到 FRivermaxVideoStream 结构体并引入 ANC 流支持
- **实验性标记**：`.uplugin` 中 `IsBetaVersion=true`，API 可能在未来版本中发生变化
- **平台限制**：仅支持 Win64，需要 NVIDIA ConnectX 系列网卡 + Rivermax SDK
- **推荐使用**：如果你的虚拟制片管线基于 ST 2110 IP 网络，这是 Epic 官方维护的首选方案，推荐在了解其 Beta 状态的前提下使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Rivermax/RivermaxMedia)
- [RivermaxCore 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Rivermax/RivermaxCore) — RivermaxMedia 的底层依赖
- [NVIDIA Rivermax SDK 文档](https://docs.nvidia.com/networking/display/RivermaxSDKv140) — 官方 SDK 文档
- 测试用例：未在 Engine/Tests 目录中发现针对 RivermaxMedia 的自动化测试
