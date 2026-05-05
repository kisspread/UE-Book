# Rivermax Core

> Base plugin exposing rivermax to engine

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `RivermaxCore` (Runtime), `RivermaxEditor` (Editor), `RivermaxRendering` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-03-30 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Rivermax/RivermaxCore) | |

## 用途

RivermaxCore 是 UE5 对 [NVIDIA Rivermax](https://developer.nvidia.com/networking/rivermax) SDK 的引擎封装层。Rivermax 是一个高性能用户态网络 I/O 库，用于在支持 RDMA 的网卡（如 NVIDIA ConnectX / BlueField）上实现 **SMPTE ST 2110** 协议族的音视频数据传输——这是专业广播和虚拟制片 (Virtual Production) 领域的行业标准 IP 视频传输协议。

**解决的问题：** 传统视频 I/O 走 SDI 线缆，而 ST 2110 将视频、音频、辅助数据拆分为独立的 IP 流在以太网上传输。RivermaxCore 让 UE 引擎能够直接通过 25/100GbE 网络以纳秒级精度发送和接收广播级视频流，无需专用 SDI 采集卡。

**为什么存在：** Epic 在虚拟制片（如 LED Volume / nDisplay）场景中需要将引擎渲染画面实时推送到 LED 墙控制器，或将外部摄像机信号接入引擎。Rivermax 提供了比普通 socket 低得多的延迟和 CPU 开销，且支持 GPU Direct RDMA——数据可从 GPU 显存直接 DMA 到网卡，绕过 CPU 和系统内存。

## 核心架构

```
┌─────────────────────────────────────────────────────────┐
│                    UE5 Engine                            │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │ Media Output │  │ Media Input  │  │ nDisplay /    │  │
│  │ (nDisplay等) │  │ (MediaPlayer)│  │ Custom Code   │  │
│  └──────┬───────┘  └──────┬───────┘  └───────┬───────┘  │
│         │                 │                  │           │
│  ┌──────▼─────────────────▼──────────────────▼───────┐  │
│  │            IRivermaxCoreModule (入口)               │  │
│  │  CreateOutputStream() / CreateInputStream()        │  │
│  └────────────────────┬───────────────────────────────┘  │
│                       │                                  │
│  ┌────────────────────▼───────────────────────────────┐  │
│  │           IRivermaxManager (管理器)                  │  │
│  │  Library init / PTP clock / GPU Direct / Devices    │  │
│  └────────────────────┬───────────────────────────────┘  │
│                       │                                  │
│  ┌────────────────────▼───────────────────────────────┐  │
│  │  Streams: Video (ST2110-20) | Anc TC (ST2110-40)   │  │
│  │  FrameManager / FrameAllocator / BoundaryMonitor    │  │
│  └────────────────────┬───────────────────────────────┘  │
│                       │                                  │
│  ┌────────────────────▼───────────────────────────────┐  │
│  │         RivermaxWrapper (DLL 加载 + API 桥接)       │  │
│  └────────────────────┬───────────────────────────────┘  │
└───────────────────────┼──────────────────────────────────┘
                        │
                 ┌──────▼──────┐
                 │ Rivermax DLL │  (NVIDIA Rivermax SDK)
                 └──────┬──────┘
                        │
                 ┌──────▼──────┐
                 │ ConnectX NIC │  (RDMA / GPUDirect)
                 └─────────────┘
```

### 支持的 ST 2110 子协议

| 枚举值 | 协议 | 说明 | 实现状态 |
|---|---|---|---|
| `ST2110_20` | SMPTE ST 2110-20 | 未压缩视频流 | ✅ 完整实现（输入 + 输出） |
| `ST2110_30` | SMPTE ST 2110-30 | PCM 音频流 | ❌ 未实现（返回 nullptr） |
| `ST2110_40` | SMPTE ST 2110-40 | 通用辅助数据 | ✅ 输出 |
| `ST2110_40_TC` | SMPTE ST 2110-40 | 时间码辅助数据 | ✅ 输出 |

### 支持的像素格式

`ESamplingType` 枚举定义了所有支持的采样格式：

| 类别 | 格式 |
|---|---|
| YUV 4:2:2 | 8bit, 10bit, 12bit, 16bit, 16bit Float |
| YUV 4:4:4 | 8bit, 10bit, 12bit, 16bit, 16bit Float |
| RGB | 8bit, 10bit, 12bit, 16bit, 16bit Float |

每种格式的 pgroup 大小和位深由 `FStandardVideoFormat::GetVideoFormatInfo()` 查询。

## 使用场景

- **LED Volume 虚拟制片**：将 UE 实时渲染画面通过 ST 2110-20 推送到 LED 墙控制器（如 Brompton、Megapixel），替代传统 SDI → SDI-to-HDMI 转换链路
- **外部摄像机接入**：通过 ST 2110-20 接收来自广播级 IP 摄像机或编码器的视频流，在引擎内进行合成
- **时间码同步**：通过 ST 2110-40 TC 流发送/接收 SMPTE 时间码，保持多设备间帧精确同步
- **PTP 精确时钟**：利用 IEEE 1588 PTP 协议实现纳秒级时钟同步，确保帧边界对齐（ST 2059）
- **GPU Direct RDMA**：在支持 CUDA + RDMA 的平台上，视频数据直接从 GPU 显存传输到网卡，零拷贝、最低延迟

## 蓝图用法

此插件 **没有暴露任何蓝图节点**。所有 API 均为纯 C++ 接面，供 Media Framework 插件、nDisplay 或自定义 C++ 模块调用。

## C++ 用法

### 头文件引入

```cpp
#include "IRivermaxCoreModule.h"
#include "IRivermaxManager.h"
#include "IRivermaxOutputStream.h"
#include "IRivermaxInputStream.h"
#include "RivermaxTypes.h"
```

### 基本用法 — 创建输出流

```cpp
// 获取 Rivermax 模块
IRivermaxCoreModule& RivermaxModule = IRivermaxCoreModule::Get();

// 验证 Rivermax 库已加载
TSharedPtr<IRivermaxManager> Manager = RivermaxModule.GetRivermaxManager();
if (!Manager->ValidateLibraryIsLoaded())
{
    return; // Rivermax 库未就绪
}

// 配置视频输出选项
FRivermaxOutputOptions OutputOptions;
OutputOptions.NumberOfBuffers = 2;
OutputOptions.AlignmentMode = ERivermaxAlignmentMode::AlignmentPoint;
OutputOptions.FrameLockingMode = EFrameLockingMode::FreeRun;
OutputOptions.bDoContinuousOutput = true;
OutputOptions.bDoFrameCounterTimestamping = true;

// 配置 ST 2110-20 视频流选项
auto VideoOptions = MakeShared<FRivermaxVideoOutputOptions>();
VideoOptions->InterfaceAddress = TEXT("192.168.1.10");  // 本地网卡 IP
VideoOptions->StreamAddress = TEXT("239.1.1.1");        // 组播地址
VideoOptions->Port = 50000;
VideoOptions->Resolution = FIntPoint(1920, 1080);
VideoOptions->PixelFormat = ESamplingType::RGB_10bit;
VideoOptions->FrameRate = FFrameRate(60000, 1001);      // 59.94fps
VideoOptions->bUseGPUDirect = true;

OutputOptions.StreamOptions[ERivermaxStreamType::ST2110_20] = VideoOptions;

// 创建输出流（需要 SDP 描述，可为空）
TArray<char> SDPDescription;
TUniquePtr<IRivermaxOutputStream> OutputStream =
    RivermaxModule.CreateOutputStream(ERivermaxStreamType::ST2110_20, SDPDescription);

// 实现监听器接口
class FMyOutputStreamListener : public IRivermaxOutputStreamListener
{
public:
    virtual void OnInitializationCompleted(bool bHasSucceed) override
    {
        if (bHasSucceed) { /* 流已就绪 */ }
    }
    virtual void OnStreamError() override { /* 处理错误 */ }
    virtual void OnPreFrameEnqueue() override { /* 帧入队前回调 */ }
};

FMyOutputStreamListener Listener;
OutputStream->Initialize(OutputOptions, Listener);
```

来源：`Source/RivermaxCore/Public/IRivermaxCoreModule.h`, `IRivermaxOutputStream.h`, `RivermaxTypes.h`

### 基本用法 — 推送视频帧

```cpp
// 准备帧数据
FRivermaxOutputInfoVideo FrameInfo;
FrameInfo.FrameIdentifier = GFrameCounter;
FrameInfo.Width = 1920;
FrameInfo.Height = 1080;
FrameInfo.Stride = 1920 * 4; // RGBA
FrameInfo.CPUBuffer = MyPixelData;    // CPU 内存指针
// 或使用 GPU Direct:
// FrameInfo.GPUBuffer = MyRHIBuffer;

// 预留帧槽位（阻塞模式下会等待直到有空闲槽位）
OutputStream->ReserveFrame(GFrameCounter);

// 推送帧
OutputStream->PushFrame(MakeShared<FRivermaxOutputInfoVideo>(FrameInfo));
```

来源：`Source/RivermaxCore/Public/IRivermaxOutputStream.h`

### 基本用法 — 创建输入流

```cpp
// 配置输入流选项
FRivermaxInputStreamOptions InputOptions;
InputOptions.InterfaceAddress = TEXT("192.168.1.10");
InputOptions.StreamAddress = TEXT("239.1.1.1");
InputOptions.Port = 50000;
InputOptions.FrameRate = FFrameRate(60000, 1001);
InputOptions.PixelFormat = ESamplingType::RGB_10bit;
InputOptions.NumberOfBuffers = 3;
InputOptions.bUseGPUDirect = true;

// 创建输入流
TArray<char> SDPDescription;
TUniquePtr<IRivermaxInputStream> InputStream =
    RivermaxModule.CreateInputStream(ERivermaxStreamType::ST2110_20, SDPDescription);

// 实现监听器
class FMyInputStreamListener : public IRivermaxInputStreamListener
{
public:
    virtual void OnInitializationCompleted(const FRivermaxInputInitializationResult& Result) override
    {
        if (Result.bHasSucceed)
        {
            // 输入流就绪，GPU Direct 是否可用: Result.bIsGPUDirectSupported
        }
    }

    virtual TSharedPtr<IRivermaxVideoSample> OnVideoFrameRequested(
        const FRivermaxInputVideoFrameDescriptor& FrameInfo) override
    {
        // 流请求一个缓冲区来接收下一帧
        // 返回一个 IRivermaxVideoSample 实现，提供接收缓冲区
        return MakeShared<FMyVideoSample>(FrameInfo.Width, FrameInfo.Height);
    }

    virtual void OnVideoFrameReceived(TSharedPtr<IRivermaxVideoSample> InFrame) override
    {
        // 帧已接收完成，可用于渲染
    }

    virtual void OnStreamError() override { /* 错误处理 */ }

    virtual void OnVideoFormatChanged(
        const FRivermaxInputVideoFormatChangedInfo& NewFormat) override
    {
        // 输入格式变化（分辨率/像素格式变更）
    }
};

FMyInputStreamListener InputListener;
InputStream->Initialize(InputOptions, InputListener);
```

来源：`Source/RivermaxCore/Public/IRivermaxInputStream.h`, `RivermaxTypes.h`

### PTP 时间与帧对齐

```cpp
#include "RivermaxPTPUtils.h"

// 获取当前 PTP 时间（纳秒）
uint64 CurrentTimeNs = Manager->GetTime();

// 获取当前帧号（基于 PTP 时间和帧率）
FFrameRate Rate(60000, 1001); // 59.94fps
uint64 FrameNumber = UE::RivermaxCore::GetFrameNumber(CurrentTimeNs, Rate);

// 获取下一个帧边界对齐点（ST 2059 标准）
uint64 NextAlignment = UE::RivermaxCore::GetNextAlignmentPoint(CurrentTimeNs, Rate);

// 从帧号反算对齐点时间
uint64 AlignmentFromFrame = UE::RivermaxCore::GetAlignmentPointFromFrameNumber(FrameNumber, Rate);
```

来源：`Source/RivermaxCore/Public/RivermaxPTPUtils.h`, 测试用例 `Private/Tests/PTPTest.cpp`

### GPU Direct 状态查询

```cpp
// 检查 GPU Direct 支持状态
bool bGPUDirectSupported = Manager->IsGPUDirectSupported();
bool bInputSupported = Manager->IsGPUDirectInputSupported();
bool bOutputSupported = Manager->IsGPUDirectOutputSupported();

// 枚举可用网络设备
for (const FRivermaxDeviceInfo& Device : Manager->GetDevices())
{
    UE_LOG(LogTemp, Log, TEXT("Device: %s at %s"),
        *Device.Description, *Device.InterfaceAddress);
}

// 根据源 IP 查找匹配的设备接口
FString DeviceIP;
if (Manager->GetMatchingDevice(TEXT("192.168.1.100"), DeviceIP))
{
    UE_LOG(LogTemp, Log, TEXT("Matched device: %s"), *DeviceIP);
}
```

来源：`Source/RivermaxCore/Public/IRivermaxManager.h`

## 模块架构

### RivermaxCore（Runtime）

核心运行时模块，负责：
- Rivermax DLL 加载与 API 桥接（`RivermaxWrapper`）
- 流的创建、生命周期管理
- PTP 时钟初始化与管理
- 帧边界监控（ST 2059）
- 设备发现与 IP 解析
- GPU Direct (CUDA) 能力检测

### RivermaxRendering（Runtime）

GPU 计算着色器模块，提供 **像素格式转换** 的 compute shader：

| 着色器 | 方向 | 说明 |
|---|---|---|
| `FYUV8Bit422ToRGBACS` | 输入 | YUV422 8bit → RGBA |
| `FYUV10Bit422ToRGBACS` | 输入 | YUV422 10bit LE → RGBA |
| `FRGB8BitToRGBA8CS` | 输入 | RGB 8bit packed → RGBA |
| `FRGB10BitToRGBA10CS` | 输入 | RGB 10bit packed → RGBA |
| `FRGB12BitToRGBA12CS` | 输入 | RGB 12bit packed → RGBA |
| `FRGB16fBitToRGBA16fCS` | 输入 | RGB 16bit float → RGBA |
| `FRGBToYUV8Bit422CS` | 输出 | RGBA → YUV422 8bit |
| `FRGBToYUV10Bit422LittleEndianCS` | 输出 | RGBA → YUV422 10bit LE |
| `FRGBToRGB8BitCS` | 输出 | RGBA → RGB 8bit packed |
| `FRGBToRGB10BitCS` | 输出 | RGBA → RGB 10bit packed |
| `FRGBToRGB12BitCS` | 输出 | RGBA → RGB 12bit packed |
| `FRGBToRGB16fCS` | 输出 | RGBA → RGB 16bit float |

这些 shader 使用 RDG (Render Dependency Graph) 在 GPU 上完成格式转换，避免 CPU 端逐像素处理。

### RivermaxEditor（Editor）

编辑器扩展模块，提供：
- `URivermaxSettings` 的属性面板自定义（`RivermaxSettingsDetailsCustomization`）
- 网络接口选择下拉框（`SRivermaxInterfaceComboBox`）
- 设备选择自定义（`RivermaxDeviceSelectionCustomization`）

## 编辑器设置

通过 **Edit → Project Settings → Plugins → Rivermax** 访问：

| 设置项 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| Time Source | Enum | PTP | 时钟源：PTP / Engine / System |
| PTP Interface Address | String | `*.*.*.*` | PTP 使用的网络接口，`*` 为通配符 |

修改任一设置后需要 **重启编辑器** 生效（`ConfigRestartRequired = true`）。

## 控制台变量

| CVar | 默认值 | 说明 |
|---|---|---|
| `Rivermax.Monitor.Enable` | 1 | 启用/禁用帧边界监控线程 |

## 模块依赖

### RivermaxCore (Runtime)

| 模块 | 用途 |
|---|---|
| `Core` | 引擎核心基础 |
| `CoreUObject` | UObject 系统 |
| `DeveloperSettings` | 开发者设置基类 |
| `MediaAssets` | Media Framework 集成 |
| `RHI` | 渲染硬件接口（GPU Buffer） |
| `RivermaxLib` | Rivermax SDK 的 UE 封装（DLL 加载） |
| `TimeManagement` | 时间管理（PTP 等） |
| `D3D12RHI` (Private) | DirectX 12 支持（GPU Direct） |
| `Engine` (Private) | 引擎核心 |
| `Networking` (Private) | 网络功能 |
| `RenderCore` (Private) | 渲染核心 |
| `CUDA` (ThirdParty) | CUDA 支持（GPU Direct RDMA） |
| `DX12` (ThirdParty) | DirectX 12 第三方库 |

### RivermaxRendering (Runtime)

| 模块 | 用途 |
|---|---|
| `Core` | 引擎核心 |
| `Projects` | 项目配置 |
| `RenderCore` | 渲染核心（RDG） |
| `RHI` | 渲染硬件接口 |

### RivermaxEditor (Editor)

| 模块 | 用途 |
|---|---|
| `Core` | 引擎核心 |
| `PropertyEditor` | 属性面板自定义 |
| `RivermaxCore` | 核心运行时模块 |
| `Slate` / `SlateCore` | UI 框架 |
| `UnrealEd` | 编辑器功能 |

### 插件依赖

| 插件 | 用途 |
|---|---|
| `MediaIOFramework` | Media IO 框架集成 |

## 硬件与平台要求

- **平台**：仅 Win64
- **网卡**：NVIDIA ConnectX-5 或更高（支持 RDMA）
- **驱动**：Mellanox OFED / NVIDIA Rivermax SDK
- **GPU Direct**（可选）：NVIDIA GPU + CUDA + 支持 RDMA 的网卡
- **PTP**（推荐）：网络中需有 PTP Grandmaster 时钟源

## 维护状态

### 近期更新

| 日期 | Hash | 说明 |
|---|---|---|
| 2025-10-03 | `36009346` | 修复 16bit RGB 输入流裁剪问题（dispatch group count 超限），清理与小改进 |
| 2025-09-23 | `3f4735f5` | 修复 Debug 构建失败（缺少 include） |
| 2025-09-12 | `b9d90b69` | ANC Media Output UI 美化，修复 IP 值不保存的问题 |
| 2025-09-11 | `d8ea04d0` | 修复 ATC 时间码打包（ST 12-2 交错映射），Rivermax API 流销毁超时保护，DPU 队列满时让出线程 |
| 2025-09-08 | `a88db4c5` | 修复 Monolithic 构建问题 |

### 维护评价

- **创建时间**：2022-03-30，约 4 年前，与 UE5 虚拟制片功能同步推出
- **更新频率**：活跃维护中，最近更新在 2025 年 10 月，持续有功能修复和改进
- **维护状态**：🟢 **活跃维护** — 最近 1 个月内有多次实质性更新（bug 修复、ATC 时间码支持、16bit 格式修复等）
- **实验性标记**：`IsBetaVersion = true`，表明 API 仍可能发生变化
- **已知限制**：
  - 仅支持 Win64
  - ST 2110-30 (Audio) 未实现
  - 需要特定硬件（支持 RDMA 的 NVIDIA 网卡）
  - Hidden plugin，不在插件浏览器中默认显示
- **推荐使用**：如果你在做虚拟制片 / LED Volume / 广播级 IP 视频集成，这是官方推荐的路径。对于普通游戏开发则不需要。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Rivermax/RivermaxCore)
- [NVIDIA Rivermax SDK](https://developer.nvidia.com/networking/rivermax)
- [SMPTE ST 2110 标准](https://www.smpte.org/standards/st2110)
- [SMPTE ST 2059 (PTP 帧对齐)](https://www.smpte.org/standards/st2059)
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/VirtualProduction/Rivermax/RivermaxCore/Source/RivermaxCore/Private/Tests/PTPTest.cpp)
