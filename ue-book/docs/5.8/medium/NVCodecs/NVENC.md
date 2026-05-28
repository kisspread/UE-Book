# NVCodecs

> Adds codecs from the NVIDIA Media Codec SDK to AVCodecs（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 英伟达编解码器 |
| 分类 | Codecs |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（NVIDIA硬件编解码器实现） |
| 模块 | `NVCodecs` (Runtime), `NVCodecsRHI` (Runtime), `NVDEC` (Runtime), `NVENC` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-01-25 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AVCodecs/NVCodecs) | |

## 用途

NVCodecs 插件是 Epic Games 为 UE5 开发的 **AVCodecs 框架**的 NVIDIA 硬件扩展。它的核心作用是将 NVIDIA 的 **Media Codec SDK**（包含 NVENC 和 NVDEC）集成到 UE 的统一 AVCodecs 编解码框架中。

**为什么存在：**
1.  **提供高性能硬件编解码能力**：UE 原生缺乏对 NVIDIA GPU 专用硬件编码器/解码器的直接支持。该插件填补了这一空白，允许开发者利用 NVIDIA GPU 上的专用编码单元（NVENC）和解码单元（NVDEC）进行视频处理，相比纯 CPU 或通用 GPU 计算，效率更高、功耗更低。
2.  **标准化接口**：它通过遵循 AVCodecs 框架的 `TVideoEncoder` 和 `TVideoDecoder` 模板接口，将 NVIDIA 的私有 SDK 逻辑封装成 UE 开发者熟悉的、跨平台（理论上）的统一 API。这使得在不同硬件后端（CUDA， D3D11， D3D12， Vulkan）之间切换编解码实现变得更加容易。
3.  **服务于高级视频处理场景**：为直播推流、视频录制、游戏内画面捕获、实时视频分析等需要高效视频编码的场景提供底层支持。

## 使用场景

-   **游戏直播/录制**：你需要以低性能开销将游戏画面实时编码成 H.264/H.265/AV1 流，用于推流或本地保存。`FVideoEncoderNVENC` 系列类正是为此设计。
-   **视频预览/画中画**：在游戏中需要解码来自网络摄像头或视频文件的实时视频流。这对应 `NVDEC` 模块的解码器。
-   **自定义视频处理管线**：你正在构建一个复杂的视频处理管线，需要将 NVENC 编码器作为管线中的一个标准化环节，与其他 UE 视频处理组件（如 AVCodecs 的捕获、转换节点）无缝集成。
-   **跨硬件后端支持**：你的项目需要同时支持 DirectX 11、DirectX 12 和 Vulkan 图形 API，并希望在每种情况下都尽可能利用 NVIDIA 的硬件编码器。该插件提供了针对 D3D11、D3D12 和 CUDA 资源的不同编码器实现。

## 蓝图用法

该插件主要为 **C++ Runtime 模块**，其核心 API 并未通过 `UFUNCTION(BlueprintCallable)` 暴露给蓝图可视化脚本。视频编解码操作通常属于底层、高性能的循环，更适合在 C++ 中控制。

**主要交互方式**：开发者通常会在 C++ 中创建编码器/解码器实例，处理视频帧数据，并通过 UE 的媒体框架或自定义逻辑与蓝图系统进行数据交换（例如，将编码后的视频包传回蓝图进行网络发送）。

## C++ 用法

### 头文件引入

使用 NVENC 编码器，通常需要包含以下头文件：

```cpp
// NVENC 核心 API 封装
#include "NVENC.h"

// NVENC 编码器实现
#include "Video/Encoders/VideoEncoderNVENC.h"

// NVENC 编码器配置（如果需要自定义）
#include "Video/Encoders/Configs/VideoEncoderConfigNVENC.h"
```

### 基本用法

以下示例展示了如何创建一个基于 CUDA 资源的 NVENC 编码器，并发送一帧进行编码。代码逻辑参考自插件结构及 NVENC SDK 通用用法。

```cpp
// 包含必要头文件（见上文）
#include "Video/Encoders/VideoEncoderNVENC.h"
#include "AVModule/Video/Resources/VideoResourceCUDA.h" // 假设使用 CUDA 资源

// 1. 创建编码器实例 (以 CUDA 为例)
TSharedPtr<FVideoEncoderNVENCCUDA> Encoder = MakeShared<FVideoEncoderNVENCCUDA>();

// 2. 获取或创建设备和实例 (示例逻辑，实际需根据上下文获取)
TSharedPtr<FAVDevice> Device = /* ... 从当前上下文获取或创建 AV 设备 ... */;
TSharedPtr<FAVInstance> Instance = /* ... 从当前上下文获取或创建 AV 实例 ... */;

// 3. 打开编码器会话
FAVResult Result = Encoder->Open(Device, Instance);
if (Result.IsNotSuccess())
{
    UE_LOG(LogTemp, Error, TEXT("Failed to open NVENC encoder: %s"), *Result.Message);
    return;
}

// 4. 应用配置 (使用默认或自定义配置)
// 可以直接使用 FVideoEncoderConfigNVENC 的默认值
FAVResult ApplyResult = Encoder->ApplyConfig();
if (ApplyResult.IsNotSuccess())
{
    UE_LOG(LogTemp, Error, TEXT("Failed to apply NVENC config: %s"), *ApplyResult.Message);
    return;
}

// 5. 准备并发送一帧视频数据
// 假设我们有一个有效的 CUDA 视频资源 (FVideoResourceCUDA)
TSharedPtr<FVideoResourceCUDA> VideoFrame = /* ... 捕获或创建一帧 CUDA 资源 ... */;
uint32 Timestamp = 1000; // 帧时间戳，单位根据配置
bool bForceKeyframe = false;

FAVResult SendResult = Encoder->SendFrame(VideoFrame, Timestamp, bForceKeyframe);
if (SendResult.IsNotSuccess())
{
    UE_LOG(LogTemp, Error, TEXT("Failed to send frame to NVENC: %s"), *SendResult.Message);
    // 处理错误，可能需要重新配置或关闭
}

// 6. 接收编码后的数据包
FVideoPacket EncodedPacket;
FAVResult ReceiveResult = Encoder->ReceivePacket(EncodedPacket);
if (ReceiveResult.IsSuccess())
{
    // 成功获取到编码后的数据包 (EncodedPacket)
    // EncodedPacket.Data 包含编码后的比特流 (H.264/H.265/AV1)
    // 可以将其发送到网络，或写入文件
    UE_LOG(LogTemp, Log, TEXT("Received encoded packet of size: %d bytes"), EncodedPacket.Data.Num());
}
```

### 进阶用法：自定义编码配置

可以通过修改 `FVideoEncoderConfigNVENC` 的成员来调整编码参数，例如码率、预设等。

```cpp
// 创建自定义配置
FVideoEncoderConfigNVENC CustomConfig;

// 修改预设 (例如，使用低延迟预设 P7)
CustomConfig.presetGUID = NV_ENC_PRESET_P7_GUID;

// 修改码率控制模式为 CBR (恒定码率)
NV_ENC_RC_PARAMS& RcParams = CustomConfig.encodeConfig->rcParams;
RcParams.rateControlMode = NV_ENC_PARAMS_RC_CBR;
RcParams.averageBitRate = 8000000; // 8 Mbps
RcParams.maxBitRate = 10000000;    // 10 Mbps

// 修改 GOP (图像组) 长度
CustomConfig.encodeConfig->gopLength = 30; // 每 30 帧一个关键帧

// 在打开编码器后，应用自定义配置
// 注意：通常需要在 Encoder->Open() 之后，但在发送帧之前调用 ApplyConfig
// 这里演示了如何将自定义配置传递给编码器 (具体API可能需要调整)
FAVResult ApplyCustomResult = Encoder->ApplyConfig(CustomConfig);
```

## Demo 示例

以下是一个最小化的示例，演示如何在 `UObject` 或 `Actor` 中初始化一个 NVENC CUDA 编码器。

```cpp
// MyVideoEncoder.h
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "Video/Encoders/VideoEncoderNVENC.h" // 核心头文件
#include "AVModule/Video/Resources/VideoResourceCUDA.h" // 资源头文件

class UMyVideoEncoder : public UObject
{
    GENERATED_BODY()

public:
    UMyVideoEncoder();
    ~UMyVideoEncoder();

    /** 初始化编码器 */
    bool InitializeEncoder();

    /** 编码一帧示例函数 (输入数据为示例) */
    bool EncodeOneFrame(const TArray<uint8>& RawPixelData, int32 Width, int32 Height);

private:
    TSharedPtr<FVideoEncoderNVENCCUDA> Encoder;
    TSharedPtr<FAVDevice> AVDevice;
    TSharedPtr<FAVInstance> AVInstance;
};
```

```cpp
// MyVideoEncoder.cpp
#include "MyVideoEncoder.h"
#include "AVModule/Core/AVResult.h"
#include "Modules/ModuleManager.h"

UMyVideoEncoder::UMyVideoEncoder()
{
}

UMyVideoEncoder::~UMyVideoEncoder()
{
    // 编码器会在智能指针释放时自动清理
    Encoder.Reset();
}

bool UMyVideoEncoder::InitializeEncoder()
{
    // 1. 创建编码器实例
    Encoder = MakeShared<FVideoEncoderNVENCCUDA>();

    // 2. 简化：获取设备和实例。在实际项目中，需要从图形设备或 AVCodecs 模块获取正确实例。
    // 这里仅为演示结构。
    AVDevice = MakeShared<FAVDevice>(EAVDeviceType::CUDA); // 假设存在此构造
    AVInstance = MakeShared<FAVInstance>();

    // 3. 打开编码器
    FAVResult OpenResult = Encoder->Open(AVDevice, AVInstance);
    if (OpenResult.IsNotSuccess())
    {
        UE_LOG(LogTemp, Error, TEXT("Encoder Open Failed: %s"), *OpenResult.Message);
        return false;
    }

    // 4. 应用默认配置
    FAVResult ConfigResult = Encoder->ApplyConfig();
    if (ConfigResult.IsNotSuccess())
    {
        UE_LOG(LogTemp, Error, TEXT("Apply Config Failed: %s"), *ConfigResult.Message);
        Encoder->Close();
        return false;
    }

    UE_LOG(LogTemp, Log, TEXT("NVENC CUDA Encoder initialized successfully."));
    return true;
}

bool UMyVideoEncoder::EncodeOneFrame(const TArray<uint8>& RawPixelData, int32 Width, int32 Height)
{
    if (!Encoder)
    {
        UE_LOG(LogTemp, Error, TEXT("Encoder is not initialized!"));
        return false;
    }

    // 注意：将原始像素数据 (RawPixelData) 包装成 FVideoResourceCUDA 是复杂步骤，
    // 涉及 CUDA 内存分配和数据传输，远超此示例范围。
    // 此处假设我们有一个从其他来源（如纹理读回）获得的 FVideoResourceCUDA。
    TSharedPtr<FVideoResourceCUDA> CudaResource = /* ... 实际创建过程 ... */;

    // 发送帧进行编码
    FAVResult SendResult = Encoder->SendFrame(CudaResource, FPlatformTime::Cycles());
    if (SendResult.IsNotSuccess())
    {
        UE_LOG(LogTemp, Error, TEXT("SendFrame Failed: %s"), *SendResult.Message);
        return false;
    }

    // 尝试接收编码结果
    FVideoPacket Packet;
    FAVResult RecvResult = Encoder->ReceivePacket(Packet);
    if (RecvResult.IsSuccess())
    {
        UE_LOG(LogTemp, Log, TEXT("Frame encoded. Packet size: %d"), Packet.Data.Num());
        return true;
    }

    // 发送和接收可能异步，未立即准备好不算严格错误
    return true;
}
```

## 模块依赖

要使用 `NVENC` 模块（或 `NVDEC`），你的项目模块的 `.Build.cs` 文件需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `AVCodecs` | AVCodecs 核心框架，提供编码器/解码器基类 (`TVideoEncoder`) 和通用类型定义。 |
| `Vulkan` | NVCodecs 构建时依赖 Vulkan 头文件，即使你的项目主要使用 DirectX。用于跨平台编译和 Vulkan 后端支持。 |

**示例 `.Build.cs` 依赖添加**：
```csharp
PublicDependencyModuleNames.AddRange(new string[] { "Core", "CoreUObject", "Engine", "AVCodecs" });
PrivateDependencyModuleNames.AddRange(new string[] { "NVENC", "Vulkan" }); // 或 "NVDEC"
```

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `408f8cf3` | [NvEnc] Add: Launch arg and config option to revert to legacy D3D12 -> CUDA -> NvEnc code path to wo | 添加命令行和配置选项，用于回退到旧的D3D12->CUDA->NvEnc编码路径。 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复了格式化函数中使用的作用域枚举可能导致乱码输出的问题。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 在修复了糟糕的查找替换操作后进行的第二次尝试。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退了提交 CL51314860 的更改。 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 将 FCoreDelegates::OnPostEngineInit 移至 FCoreDelegates::GetOnPostEngineInit()，以修复注册缺失问题。 |

### 维护评价

**综合评价：活跃维护的实验性模块。**

1.  **创建时间**：于 2023 年 1 月创建，相对较新。
2.  **近期活跃度**：**近期有实质性功能更新和问题修复**。最新一次提交（`408f8cf3`）增加了新的配置选项，表明功能仍在迭代。之前的提交也包含代码质量改进和缺陷修复。
3.  **维护状态**：鉴于其属于 **实验性** (`IsExperimentalVersion: true`) 且 **默认未启用** (`EnabledByDefault: false`)，其 API 和行为可能尚未完全稳定。但持续的更新（包括 2026 年的提交）表明该模块正在被内部项目使用和改进。
4.  **已知问题/限制**：
    *   **平台依赖性**：`FVideoEncoderNVENCD3D11` 和 `FVideoEncoderNVENCD3D12` 等类仅在 `PLATFORM_WINDOWS` 下编译。跨平台支持主要通过 CUDA 路径。
    *   **NVIDIA 驱动/硬件依赖**：需要目标机器安装有支持 NVIDIA NVENC/NVDEC 的驱动程序和显卡。
    *   **实验性警告**：作为实验性插件，其 API 可能在未来版本中发生变化。
5.  **推荐使用**：
    *   **推荐**用于需要高性能 NVIDIA 硬件编码/解码的 **实验性项目**或**内部工具开发**。
    *   在**正式生产项目**中使用需谨慎，务必做好回退方案，并密切关注未来版本可能的 breaking changes。
    *   对于必须使用 DirectX 11/12 路径的项目，注意该插件提供了相应的专用编码器实现。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AVCodecs/NVCodecs)
-   [官方文档](https://docs.nvidia.com/video-technologies/video-codec-sdk/) (NVIDIA Video Codec SDK 官方文档)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/Plugins/AVCodecs) (AVCodecs 框架的整体测试，可能包含 NVCodecs 相关测试)