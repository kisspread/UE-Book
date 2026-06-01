# RivermaxCore

> Base plugin exposing rivermax to engine

| 属性 | 值 |
|---|---|
| 中文名 | 河流最大核心 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `RivermaxCore` (Runtime), `RivermaxEditor` (Editor), `RivermaxRendering` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-03-30 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Rivermax/RivermaxCore) | |

## 用途

RivermaxCore 是 Unreal Engine 与 NVIDIA Rivermax SDK 之间的桥梁层，为虚拟制片提供符合 SMPTE ST 2110 标准的专业级 IP 视频传输能力。

该插件解决的核心问题是：**在专业广电和虚拟制片工作流中，通过 IP 网络以极低延迟收发无压缩视频帧**。具体包括：

1. **Rivermax SDK 动态加载**：运行时加载 Rivermax 动态库，管理所有 API 函数指针
2. **SMPTE ST 2110 视频流**（2110-20）：通过 RTP 协议按 RFC 4175 标准打包/解包视频帧，支持 RGB 和 YUV 多种采样格式
3. **SMPTE ST 2110 ANC 数据流**（2110-40）：发送/接收辅助数据包（如时间码），遵循 RFC 8331 标准
4. **GPU Direct 支持**：通过 CUDA 实现 GPU 到网卡的零拷贝传输，避免 CPU 中转
5. **PTP 时钟同步**：基于 ST-2059 标准的帧边界对齐和调度，确保帧发送/接收精确同步
6. **设备管理**：自动发现 Rivermax 可用网络接口，验证 GPU Direct 能力

隐藏插件且默认未启用，是 RivermaxMediaOutput 等上游插件的底层依赖。

## 使用场景

- 你需要在虚拟制片中将 UE5 渲染画面通过 IP 网络发送到 LED 墙控制器 → 使用 Rivermax 输出流
- 你需要从摄像机 IP 信号源接收无压缩视频帧到 UE5 → 使用 Rivermax 输入流
- 你需要发送或接收 SMPTE ST 2110-40 辅助数据（如时间码）→ 使用 ANC 流
- 你需要极致低延迟的 GPU 到网卡数据传输 → 启用 GPUDirect 模式
- 你在搭建基于 IP 的虚拟制片管线，需要 PTP 时钟同步 → 使用 Rivermax 的 PTP 时间源

## 蓝图用法

此插件主要面向 C++ 开发者，蓝图可访问的 API 较少。唯一暴露给蓝图的配置类是 `URivermaxSettings`，位于项目设置中。

### 项目设置

| 设置项 | 说明 | 所在类 |
|---|---|---|
| `TimeSource` | 时间源选择（PTP / Engine / System） | `URivermaxSettings` |
| `PTPInterfaceAddress` | PTP 网络接口地址，仅当 TimeSource=PTP 时生效 | `URivermaxSettings` |

> **注意**：所有流的创建、初始化和数据推送均需通过 C++ 接口完成。蓝图仅能修改全局时间源设置。

## C++ 用法

### 头文件引入

```cpp
// 核心模块接口
#include "IRivermaxCoreModule.h"

// 流类型定义和选项
#include "RivermaxTypes.h"

// 视频格式信息
#include "RivermaxFormats.h"

// 输出流接口（用于发送数据）
#include "IRivermaxOutputStream.h"

// 输入流接口（用于接收数据）
#include "IRivermaxInputStream.h"

// PTP 时间工具
#include "RivermaxPTPUtils.h"
```

### 基本用法 — 创建输出流并发送视频帧

```cpp
#include "IRivermaxCoreModule.h"
#include "RivermaxTypes.h"

// 1. 获取 Rivermax 模块
IRivermaxCoreModule& RivermaxModule = IRivermaxCoreModule::Get();

// 2. 准备 SDP 描述（通常从 MediaOutput 或配置中获取）
TArray<char> SDPDescription;
// ... 填充 SDP 字符串 ...

// 3. 创建输出流
TUniquePtr<IRivermaxOutputStream> OutputStream = 
    RivermaxModule.CreateOutputStream(ERivermaxStreamType::ST2110_20, SDPDescription);

// 4. 配置输出选项
FRivermaxOutputOptions OutputOptions;
OutputOptions.NumberOfBuffers = 2;
OutputOptions.AlignmentMode = ERivermaxAlignmentMode::AlignmentPoint;
OutputOptions.FrameLockingMode = EFrameLockingMode::FreeRun;

auto VideoOptions = MakeShared<FRivermaxVideoOutputOptions>();
VideoOptions->FrameRate = FFrameRate(60, 1);
VideoOptions->InterfaceAddress = TEXT("192.168.1.10");
VideoOptions->StreamAddress = TEXT("228.1.1.1");
VideoOptions->Port = 50000;
VideoOptions->Resolution = FIntPoint(1920, 1080);
VideoOptions->PixelFormat = ESamplingType::RGB_10bit;
VideoOptions->bUseGPUDirect = true;

OutputOptions.StreamOptions[ERivermaxStreamType::ST2110_20] = VideoOptions;

// 5. 实现监听器并初始化
class FMyOutputStreamListener : public IRivermaxOutputStreamListener
{
public:
    virtual void OnInitializationCompleted(bool bHasSucceed) override
    {
        if (bHasSucceed)
        {
            UE_LOG(LogTemp, Log, TEXT("Rivermax output stream initialized successfully"));
        }
    }
    virtual void OnStreamError() override { /* 处理流错误 */ }
    virtual void OnPreFrameEnqueue() override { /* 帧即将入队 */ }
};

FMyOutputStreamListener Listener;
OutputStream->Initialize(OutputOptions, Listener);

// 6. 推送视频帧
auto FrameInfo = MakeShared<FRivermaxOutputInfoVideo>();
FrameInfo->FrameIdentifier = GFrameCounter;
FrameInfo->Width = 1920;
FrameInfo->Height = 1080;
FrameInfo->CPUBuffer = MyVideoBuffer;  // 或使用 GPUBuffer
FrameInfo->Stride = 1920 * 4;

OutputStream->PushFrame(FrameInfo);
```

> 来源：`Public/IRivermaxCoreModule.h`、`Public/IRivermaxOutputStream.h`、`Public/RivermaxTypes.h`

### 基本用法 — 创建输入流接收视频帧

```cpp
#include "IRivermaxCoreModule.h"
#include "RivermaxTypes.h"

// 1. 配置输入流选项
FRivermaxInputStreamOptions InputOptions;
InputOptions.FrameRate = FFrameRate(60, 1);
InputOptions.InterfaceAddress = TEXT("192.168.1.10");
InputOptions.StreamAddress = TEXT("228.1.1.1");
InputOptions.Port = 50000;
InputOptions.PixelFormat = ESamplingType::RGB_10bit;
InputOptions.NumberOfBuffers = 3;
InputOptions.bUseGPUDirect = true;

// 2. 准备 SDP 描述
TArray<char> SDPDescription;
// ...

// 3. 创建输入流
TUniquePtr<IRivermaxInputStream> InputStream =
    RivermaxModule.CreateInputStream(ERivermaxStreamType::ST2110_20, SDPDescription);

// 4. 实现监听器
class FMyInputStreamListener : public IRivermaxInputStreamListener
{
public:
    virtual void OnInitializationCompleted(const FRivermaxInputInitializationResult& Result) override
    {
        if (Result.bHasSucceed)
        {
            UE_LOG(LogTemp, Log, TEXT("Input stream ready. GPUDirect: %s"),
                Result.bIsGPUDirectSupported ? TEXT("Yes") : TEXT("No"));
        }
    }

    // 当流准备好接收下一帧时调用，返回用于写入数据的 Sample
    virtual TSharedPtr<IRivermaxVideoSample> OnVideoFrameRequested(
        const FRivermaxInputVideoFrameDescriptor& FrameInfo) override
    {
        // 创建或返回一个可用于接收视频数据的 Sample
        return CreateVideoSample(FrameInfo.Width, FrameInfo.Height);
    }

    // 当一帧数据完整接收后调用
    virtual void OnVideoFrameReceived(TSharedPtr<IRivermaxVideoSample> ReceivedFrame) override
    {
        // 处理接收到的帧数据
        uint8* RawData = ReceivedFrame->GetVideoBufferRawPtr(FrameSize);
        // ... 渲染或处理 ...
    }

    virtual void OnStreamError() override { /* 处理流错误 */ }
    virtual void OnVideoFormatChanged(const FRivermaxInputVideoFormatChangedInfo& NewFormat) override
    {
        // 格式变化处理（如分辨率改变）
    }
};

FMyInputStreamListener Listener;
InputStream->Initialize(InputOptions, Listener);
```

> 来源：`Public/IRivermaxInputStream.h`、`Public/RivermaxTypes.h`

### 进阶用法 — 查询 Rivermax Manager

```cpp
#include "IRivermaxCoreModule.h"

IRivermaxCoreModule& Module = IRivermaxCoreModule::Get();
TSharedPtr<IRivermaxManager> Manager = Module.GetRivermaxManager();

// 检查库是否已初始化
if (Manager && Manager->ValidateLibraryIsLoaded())
{
    // 获取当前时间（PTP 或系统时间）
    uint64 CurrentTimeNs = Manager->GetTime();
    ERivermaxTimeSource TimeSrc = Manager->GetTimeSource();

    // 获取可用设备列表
    TConstArrayView<FRivermaxDeviceInfo> Devices = Manager->GetDevices();
    for (const FRivermaxDeviceInfo& Device : Devices)
    {
        UE_LOG(LogTemp, Log, TEXT("Device: %s, IP: %s"),
            *Device.Description, *Device.InterfaceAddress);
    }

    // 检查 GPUDirect 支持
    bool bGPUDirect = Manager->IsGPUDirectSupported();
    bool bInputGPD = Manager->IsGPUDirectInputSupported();
    bool bOutputGPD = Manager->IsGPUDirectOutputSupported();

    // 验证 IP 格式并查找匹配设备
    FString DeviceIP;
    if (Manager->GetMatchingDevice(TEXT("192.168.1.100"), DeviceIP))
    {
        UE_LOG(LogTemp, Log, TEXT("Matching device: %s"), *DeviceIP);
    }
}
```

> 来源：`Public/IRivermaxManager.h`

### 进阶用法 — ST 2110-40 ANC 数据发送

```cpp
#include "IRivermaxCoreModule.h"
#include "RivermaxTypes.h"
#include "RivermaxPTPUtils.h"
#include "RivermaxUtils.h"

// 1. 创建 ANC 输出选项（需要 DID 和 SDID）
auto AncOptions = MakeShared<FRivermaxAncOutputOptions>(0x60, 0x60);
AncOptions->FrameRate = FFrameRate(60, 1);
AncOptions->InterfaceAddress = TEXT("192.168.1.10");
AncOptions->StreamAddress = TEXT("228.1.1.2");
AncOptions->Port = 50001;

// 2. 创建输出流
TUniquePtr<IRivermaxOutputStream> AncStream =
    RivermaxModule.CreateOutputStream(ERivermaxStreamType::ST2110_40, SDPDescription);

// 3. 发送时间码 ANC 数据
FTimecode Timecode = FTimecode(1, 2, 30, 15);
TArray<uint16> TimecodeUDWs = UE::RivermaxCore::Private::Utils::TimecodeToAtcUDW10(
    Timecode, FFrameRate(60, 1));

auto AncFrame = MakeShared<FRivermaxOutputInfoAncTimecode>();
AncFrame->FrameIdentifier = GFrameCounter;
AncFrame->UDWs = TimecodeUDWs;
AncFrame->FrameRate = FFrameRate(60, 1);
AncFrame->Timecode = Timecode;

AncStream->PushFrame(AncFrame);
```

> 来源：`Public/RivermaxTypes.h`、`Private/RivermaxUtils.h`、`Private/Streams/RivermaxOutAncStream.h`

### 进阶用法 — 帧边界监控

```cpp
#include "IRivermaxCoreModule.h"

// 获取边界监控器
IRivermaxBoundaryMonitor& Monitor = RivermaxModule.GetRivermaxBoundaryMonitor();

// 全局启用监控
Monitor.EnableMonitoring(true);

// 开始监控特定帧率（返回 Guid 用于后续停止）
FGuid MonitorGuid = Monitor.StartMonitoring(FFrameRate(60, 1));

// Insights 跟踪中会自动在每个 ST-2059 帧边界处添加标记

// 停止监控
Monitor.StopMonitoring(MonitorGuid, FFrameRate(60, 1));
```

> 来源：`Public/IRivermaxBoundaryMonitor.h`

## Demo 示例

以下是一个最小可编译示例，演示如何查询 Rivermax Manager 状态：

### RivermaxDemoActor.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "IRivermaxCoreModule.h"
#include "RivermaxDemoActor.generated.h"

UCLASS()
class ARivermaxDemoActor : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;

    /** 打印 Rivermax 设备和状态信息 */
    UFUNCTION(BlueprintCallable, Category = "Rivermax")
    void PrintRivermaxStatus();

private:
    TSharedPtr<UE::RivermaxCore::IRivermaxManager> Manager;
};
```

### RivermaxDemoActor.cpp

```cpp
#include "RivermaxDemoActor.h"
#include "RivermaxTypes.h"

void ARivermaxDemoActor::BeginPlay()
{
    Super::BeginPlay();

    if (IRivermaxCoreModule::IsAvailable())
    {
        IRivermaxCoreModule& Module = IRivermaxCoreModule::Get();
        Manager = Module.GetRivermaxManager();

        if (Manager && Manager->IsLibraryInitialized())
        {
            UE_LOG(LogTemp, Log, TEXT("Rivermax library is ready"));
            PrintRivermaxStatus();
        }
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("RivermaxCore module not available"));
    }
}

void ARivermaxDemoActor::PrintRivermaxStatus()
{
    if (!Manager || !Manager->ValidateLibraryIsLoaded())
    {
        return;
    }

    // 时间源
    UE::RivermaxCore::ERivermaxTimeSource TimeSource = Manager->GetTimeSource();
    UE_LOG(LogTemp, Log, TEXT("Time source: %d"), static_cast<int32>(TimeSource));

    // 当前时间
    uint64 TimeNs = Manager->GetTime();
    UE_LOG(LogTemp, Log, TEXT("Current time: %llu ns"), TimeNs);

    // 设备列表
    TConstArrayView<UE::RivermaxCore::FRivermaxDeviceInfo> Devices = Manager->GetDevices();
    for (const auto& Device : Devices)
    {
        UE_LOG(LogTemp, Log, TEXT("  Device: %s (%s)"),
            *Device.Description, *Device.InterfaceAddress);
    }

    // GPU Direct 能力
    UE_LOG(LogTemp, Log, TEXT("GPUDirect supported: %s"),
        Manager->IsGPUDirectSupported() ? TEXT("Yes") : TEXT("No"));
    UE_LOG(LogTemp, Log, TEXT("GPUDirect input: %s"),
        Manager->IsGPUDirectInputSupported() ? TEXT("Yes") : TEXT("No"));
    UE_LOG(LogTemp, Log, TEXT("GPUDirect output: %s"),
        Manager->IsGPUDirectOutputSupported() ? TEXT("Yes") : TEXT("No"));
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MediaIOFramework` | 上游插件依赖，提供媒体 IO 框架基础 |
| `D3D12RHI` | RivermaxCore 模块依赖，用于 GPU Direct（CUDA）与 D3D12 缓冲区映射 |

**注意**：此插件在运行时动态加载 Rivermax SDK 动态库（DLL），无需在 Build.cs 中链接 Rivermax 静态库。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-04-29 | `bef86caa` | Whitespace: followup to migrate UE_LOG to UE_LOGF: Restore newlines in multi-line format strings tha | UE_LOG 迁移到 UE_LOGF 的后续：恢复多行格式字符串中的换行 |
| 2026-04-28 | `3348026a` | Rivermax: ANC timecode input, input stream base class refactor, and pixel format unification | 新增 ANC 时间码输入、重构输入流基类、统一像素格式枚举 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复格式化函数中 scoped enum 导致的乱码输出 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32 位/64 位格式说明符不匹配的问题 |

### 维护评价

**活跃维护中**。

- **创建于 2022 年 3 月**，约 4 年历史，属于较新的插件
- **近期更新频繁**：2026 年 4-5 月有多个功能性更新（ANC 时间码输入、输入流重构、像素格式统一）和代码质量修复
- **标记为 Beta**（`IsBetaVersion=true`），API 可能仍有变化
- **标记为 Hidden**，不直接面向终端用户，而是作为其他 Rivermax 插件的底层基础设施
- **限制**：仅支持 Win64 和 Linux 平台；需要系统安装支持 RDMA 的网卡和 CUDA 环境才能使用 GPUDirect
- **推荐使用**：如果你的虚拟制片管线需要 SMPTE 2110 IP 视频传输，此插件是引擎内置的唯一选择，Epic 持续维护中

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Rivermax/RivermaxCore)
- 官方文档：无（.uplugin 中 DocsURL 为空）
- [NVIDIA Rivermax SDK 文档](https://docs.nvidia.com/networking/category/rivermax)