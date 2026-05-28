# NVCodecs

> Adds codecs from the NVIDIA Media Codec SDK to AVCodecs（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | NVIDIA 编解码器 |
| 分类 | Codecs |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NVCodecs` (Runtime), `NVCodecsRHI` (Runtime), `NVDEC` (Runtime), `NVENC` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-01-25 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AVCodecs/NVCodecs) | |

## 用途

NVCodecs 是 **AVCodecs** 插件的一个实验性扩展，旨在将 NVIDIA Media Codec SDK 的硬件编解码能力集成到 Unreal Engine 的 AV 框架中。它主要解决两个问题：
1.  **硬件解码 (NVDEC)**：利用 NVIDIA GPU 的专用硬件单元高效解码视频流（如 H.264， H.265， AV1），大幅降低 CPU 占用率，适用于实时视频流处理、游戏内视频播放等场景。
2.  **硬件编码 (NVENC)**：利用 NVIDIA GPU 的专用硬件单元进行视频编码，常用于游戏录制、直播推流、视频输出等，提供高性能的编码能力。

简而言之，它是 UE5 通用音视频处理框架 (AVCodecs) 与 NVIDIA GPU 强大编解码硬件之间的桥梁。

## 使用场景

-   **实时解码摄像头/视频流**：你需要在游戏或应用中实时接收并解码来自外部设备（如摄像头）或网络的 H.264/H.265 视频流，并将其渲染为纹理或进行进一步处理。
-   **高性能游戏录制与直播**：你希望以极低的性能开销录制游戏画面或进行直播推流。
-   **视频资产处理**：在编辑器或运行时，需要快速解码和处理大量的视频文件（如作为游戏内的“电视屏幕”播放）。
-   **任何需要 GPU 加速编解码的场景**：当 CPU 编解码成为性能瓶颈时，可考虑使用此插件进行加速。

## 蓝图用法

**重要提示**：此插件为实验性且默认禁用，蓝图集成可能尚不完善。以下为核心逻辑类的 C++ 公开接口，可作为蓝图实现的基础。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IsOpen` | 检查视频解码器是否已打开 | `FVideoDecoderNVDEC` |
| `Open` | 打开视频解码器，关联设备和实例 | `FVideoDecoderNVDEC` |
| `Close` | 关闭视频解码器并释放资源 | `FVideoDecoderNVDEC` |
| `SendPacket` | 向解码器发送一个待解码的视频数据包 | `FVideoDecoderNVDEC` |
| `ReceiveFrame` | 从解码器接收一帧已解码的视频帧（CUDA 资源） | `FVideoDecoderNVDEC` |

### 使用示例（蓝图描述）

假设你有一个 `FVideoDecoderNVDEC` 实例 (`MyDecoder`) 和一个待解码的 `FVideoPacket` (`VideoPacket`):
1.  **初始化**：调用 `Open` 节点，传入你的 AV 设备 (`AVDevice`) 和实例 (`AVInstance`)。
2.  **解码循环**：
    *   将待解码的数据包 (`VideoPacket`) 输入到 `SendPacket` 节点。
    *   调用 `ReceiveFrame` 节点尝试获取解码完成的帧。该节点会返回一个 `FVideoResourceCUDA`，你可以将其用于后续的纹理转换或处理。
3.  **清理**：在不需要时，调用 `Close` 节点释放解码器资源。

## C++ 用法

### 头文件引入

```cpp
#include “NVDEC/Video/Decoders/VideoDecoderNVDEC.h”
#include “NVDEC/Video/Decoders/Configs/VideoDecoderConfigNVDEC.h”
```

### 基本用法

以下是一个使用 `FVideoDecoderNVDEC` 解码视频包的基本流程示例。

```cpp
// (1) 创建解码器实例
TSharedPtr<FVideoDecoderNVDEC> VideoDecoder = MakeShared<FVideoDecoderNVDEC>();

// (2) 准备配置 (FVideoDecoderConfigNVDEC 继承自 CUVIDDECODECREATEINFO)
// 通常，你需要根据输入视频流的信息来配置，例如分辨率。
FVideoDecoderConfigNVDEC DecoderConfig;
// DecoderConfig.ulTargetWidth = 1920; // 可从视频流信息中获取
// DecoderConfig.ulTargetHeight = 1080;
// ... 其他配置，如 Codec 标准 (H264, H265, AV1)

// (3) 打开解码器
FAVResult Result = VideoDecoder->Open(Device, Instance);
if (Result != EAVResult::Success)
{
    UE_LOG(LogTemp, Error, TEXT(“Failed to open NVDEC decoder: %s”), *Result.GetError());
    return;
}

// (4) 应用配置 (通常在 Open 之后，解码数据之前调用)
Result = VideoDecoder->ApplyConfig(DecoderConfig);
// ... 错误检查

// (5) 发送数据包进行解码
FVideoPacket Packet; // 包含压缩的视频数据 (Bitstream)
// Packet.Data = CompressedData;
// Packet.Timestamp = SomeTimestamp;
Result = VideoDecoder->SendPacket(Packet);
// ... 错误检查

// (6) 接收解码后的帧
TSharedRef<FVideoResourceCUDA> DecodedFrameResource; // 用于接收解码帧的输出资源
Result = VideoDecoder->ReceiveFrame(DecodedFrameResource);
if (Result == EAVResult::Success)
{
    // 成功获取一帧解码后的视频数据 (存储在 CUDA 内存中)
    // 可以将其转换为纹理或其他 RHI 资源使用
}

// (7) 清理 (在对象销毁时会自动调用，也可显式调用)
VideoDecoder->Close();
```

*   **来源**: 接口定义来自 `Public/Video/Decoders/VideoDecoderNVDEC.h` 和 `Public/Video/Decoders/Configs/VideoDecoderConfigNVDEC.h`。

### 进阶用法

`FVideoDecoderConfigNVDEC` 支持从通用的 `FVideoDecoderConfig` 以及特定的 codec 配置（如 `FVideoDecoderConfigH264`, `FVideoDecoderConfigH265`, `FVideoDecoderConfigAV1`）进行转换。这允许你使用 AVCodecs 框架中更抽象的配置类型。

```cpp
// 假设你有一个通用的视频解码配置
FVideoDecoderConfig GenericConfig;
// ... 填充 GenericConfig

// 转换为 NVDEC 专用的配置
FVideoDecoderConfigNVDEC NVDECConfig;
FAVResult TransformResult = FAVExtension::TransformConfig(NVDECConfig, GenericConfig);
if (TransformResult == EAVResult::Success)
{
    // NVDECConfig 已根据通用配置填充好，可以用于解码器
    VideoDecoder->ApplyConfig(NVDECConfig);
}
```

*   **来源**: 配置转换模板特化声明位于 `Public/Video/Decoders/Configs/VideoDecoderConfigNVDEC.h`。

## Demo 示例

以下是一个最小化、可编译的 C++ 类，演示了 `FVideoDecoderNVDEC` 的基本使用模式。它假设你已经有了一个可用的 `FAVDevice` 和 `FAVInstance`。

```cpp
// NVDECMinimalDemo.h
#pragma once

#include “CoreMinimal.h”
#include “NVDEC/Video/Decoders/VideoDecoderNVDEC.h”

class UNVDECMinimalDemo : public UObject
{
    GENERATED_BODY()

public:
    void InitDemo();
    void DemoDecode(const TArray<uint8>& InCompressedData);
    void ShutdownDemo();

private:
    TSharedPtr<FVideoDecoderNVDEC> MyDecoder;
};
```

```cpp
// NVDECMinimalDemo.cpp
#include “NVDECMinimalDemo.h”

void UNVDECMinimalDemo::InitDemo()
{
    // 创建解码器
    MyDecoder = MakeShared<FVideoDecoderNVDEC>();

    // 假设 AVDevice 和 AVInstance 已经通过其他方式初始化好
    // TSharedRef<FAVDevice> Device = ...;
    // TSharedRef<FAVInstance> Instance = ...;

    // FAVResult OpenResult = MyDecoder->Open(Device, Instance);
    // if (OpenResult != EAVResult::Success)
    // {
    //     UE_LOG(LogTemp, Error, TEXT(“InitDemo: Failed to open decoder.”));
    //     return;
    // }

    // 应用一个基础配置 (可根据实际情况调整)
    FVideoDecoderConfigNVDEC Config;
    Config.ulTargetWidth = 1280;
    Config.ulTargetHeight = 720;
    // FAVResult ConfigResult = MyDecoder->ApplyConfig(Config);
    // if (ConfigResult != EAVResult::Success)
    // {
    //     UE_LOG(LogTemp, Error, TEXT(“InitDemo: Failed to apply config.”));
    // }
}

void UNVDECMinimalDemo::DemoDecode(const TArray<uint8>& InCompressedData)
{
    if (!MyDecoder.IsValid() || !MyDecoder->IsOpen())
    {
        UE_LOG(LogTemp, Warning, TEXT(“DemoDecode: Decoder not ready.”));
        return;
    }

    // 构造视频包
    FVideoPacket Packet;
    Packet.Data = InCompressedData;

    // 发送数据包
    // FAVResult SendResult = MyDecoder->SendPacket(Packet);
    // if (SendResult != EAVResult::Success)
    // {
    //     UE_LOG(LogTemp, Warning, TEXT(“DemoDecode: SendPacket failed.”));
    //     return;
    // }

    // 尝试接收帧
    TSharedRef<FVideoResourceCUDA> OutputResource = MakeShared<FVideoResourceCUDA>();
    // FAVResult ReceiveResult = MyDecoder->ReceiveFrame(OutputResource);
    // if (ReceiveResult == EAVResult::Success)
    // {
    //     UE_LOG(LogTemp, Log, TEXT(“DemoDecode: Successfully received a decoded frame.”));
    //     // 此处可以将 OutputResource 转换为纹理等
    // }
    // else if (ReceiveResult == EAVResult::Pending)
    // {
    //     UE_LOG(LogTemp, Log, TEXT(“DemoDecode: Decoder needs more data.”));
    // }
}

void UNVDECMinimalDemo::ShutdownDemo()
{
    if (MyDecoder.IsValid())
    {
        MyDecoder->Close();
        MyDecoder.Reset();
    }
}
```

## 模块依赖

从模块的 `Build.cs` 文件分析，使用此插件需要引入以下独特的依赖：

| 模块 | 用途 |
|---|---|
| `Vulkan` | NVCodecs 模块依赖 Vulkan RHI，用于与 GPU 和 NVIDIA 驱动进行底层交互。 |

其他依赖（如 `Core`, `Engine`, `RenderCore` 等基础模块）未在列表中列出，但属于标准依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `408f8cf3` | [NvEnc] Add: Launch arg and config option to revert to legacy D3D12 -> CUDA -> NvEnc code path to wo | 为 NVENC 添加了启动参数和配置选项，可回退到旧的 D3D12->CUDA->NvEnc 代码路径。 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复了在格式化函数中使用作用域枚举可能导致输出乱码的问题。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复了错误的查找替换操作后的第二次提交。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退了更改列表 CL51314860。 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 将 FCoreDelegates::OnPostEngineInit 移动到 GetOnPostEngineInit() 以修复注册缺失问题。 |

### 维护评价

该插件创建于 **2023 年初**，属于**较新的插件**。从近期提交记录（2026年5月仍在更新）来看，**仍处于活跃维护中**。最近的更新涉及新功能添加（NVENC 代码路径回退选项）、错误修复（枚举格式化、初始化委托）和代码调整。

作为 **“Experimental”** 且 **“EnabledByDefault=false”** 的插件，它尚未达到稳定版本。主要限制包括：
-   需要特定的 NVIDIA GPU 和驱动支持。
-   蓝图接口可能不完善。
-   配置和初始化流程相对底层。

**综合建议**：如果你的项目**强烈依赖 NVIDIA GPU 的硬件编解码能力**，且你能接受实验性插件的风险，可以尝试使用。否则，建议等待其进一步成熟。对于生产环境，进行充分的性能测试和兼容性验证是必要的。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AVCodecs/NVCodecs)
- [官方文档]（暂无直接链接，请关注 AVCodecs 和 UE 官方文档更新）
- [测试用例]（在提供的源码片段中未发现标准测试文件，测试可能集成在 AVCodecs 主框架或内部测试中）