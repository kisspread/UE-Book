# AMFCodecs

> Adds codecs from the AMD Advanced Media Framework SDK to AVCodecs（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | AMF编解码器 |
| 分类 | Codecs |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AMFCodecs` (Runtime), `AMFCodecsRHI` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-01-25 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AVCodecs/AMFCodecs) | |

## 用途

AMFCodecs 插件是 Epic 的 AVCodecs 框架的一个具体实现，它将 AMD 的 Advanced Media Framework (AMF) SDK 集成到 UE5 中。其核心作用是为 UE5 的视频处理流水线提供基于 AMD GPU 的硬件加速编解码能力。

该插件的主要目的是解决以下问题：
1.  **利用 AMD GPU 硬件**：在支持的 AMD 显卡上，提供比纯 CPU 编解码（软件编解码）更高性能、更低功耗的 H.264/H.265 视频编码和解码。
2.  **统一接口**：通过 AVCodecs 框架提供标准化的 `TVideoEncoder` 和 `TVideoDecoder` 接口，使得上层代码（如视频录制、直播推流、视频回放）可以透明地使用硬件加速，而无需关心底层是哪个厂商的实现。
3.  **低延迟处理**：适用于需要实时或近实时视频处理的场景，如游戏内画面录制、视频会议、云渲染等。

## 使用场景

-   你的游戏或应用需要高质量、低性能损耗的**游戏画面录制或直播**，且目标用户主要使用 AMD 显卡。
-   你正在开发一个**视频处理或转码工具**，希望利用 AMD GPU 的硬件编解码单元来加速处理流程。
-   你在构建一个**云游戏或云渲染服务**，需要对来自 AMD GPU 的视频流进行高效的硬件编码。
-   你需要解码来自外部（如摄像头、网络流）的 H.264/H.265 视频流，并希望利用 AMD GPU 进行硬件解码以降低 CPU 负载。

## 蓝图用法

此插件主要提供 C++ 层面的 API 集成，未在提供的头文件中发现暴露给蓝图的 `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)`。使用此插件需要在 C++ 层面进行编程。

## C++ 用法

### 头文件引入

```cpp
#include "Video/Encoders/Configs/VideoEncoderConfigAMF.h"
#include "Video/Encoders/VideoEncoderAMF.h"
#include "Video/Decoders/Configs/VideoDecoderConfigAMF.h"
#include "Video/Decoders/VideoDecoderAMF.h"
#include "AMF.h"
```

### 基本用法：配置编码器

从 `Public/Video/Encoders/Configs/VideoEncoderConfigAMF.h` 提取。`FVideoEncoderConfigAMF` 是 AMF 编码器的核心配置类。

```cpp
// 来源: Engine/Plugins/Experimental/AVCodecs/AMFCodecs/Public/Video/Encoders/Configs/VideoEncoderConfigAMF.h

// 创建一个 H.264 编码器配置
FVideoEncoderConfigAMF EncoderConfig;
EncoderConfig.CodecType = FVideoEncoderConfigAMF::CodecTypeH264;
EncoderConfig.Width = 1920;
EncoderConfig.Height = 1080;

// 设置特定的 AMF 属性 (例如：设置目标码率)
// 假设我们要设置 “AMF_VIDEO_ENCODER_TARGET_BITRATE” 属性
int32 TargetBitrate = 5000000; // 5 Mbps
EncoderConfig.SetProperty(AMF_VIDEO_ENCODER_TARGET_BITRATE, TargetBitrate);

// 设置重复发送 SPS/PPS 头（对于某些流媒体场景是必要的）
EncoderConfig.RepeatSPSPPS = true;
```

### 进阶用法：创建和使用编码器实例

结合 `TVideoEncoderAMF` 模板类和 `FVideoEncoderConfigAMF` 使用。

```cpp
// 假设我们有一个用于渲染到纹理的 FVideoResourceVulkan 资源
TSharedPtr<FVideoResourceVulkan> MyVideoResource = ...;

// 1. 创建编码器实例（模板参数是资源类型）
TVideoEncoderAMF<FVideoResourceVulkan> MyEncoder;

// 2. 打开编码器，传入设备和实例（通常来自 AVCodecs 框架）
FAVResult OpenResult = MyEncoder.Open(MyAVDevice, MyAVInstance);
if (!OpenResult.HasValue()) {
    UE_LOG(LogTemp, Error, TEXT("Failed to open AMF encoder: %s"), *OpenResult.Message);
    return;
}

// 3. 应用我们之前配置的设置
MyEncoder.ApplyConfig(); // 内部会使用已设置的 FVideoEncoderConfigAMF

// 4. 发送一帧进行编码
FAVResult SendResult = MyEncoder.SendFrame(MyVideoResource, CurrentTimestamp);
if (!SendResult.HasValue()) {
    UE_LOG(LogTemp, Warning, TEXT("Error sending frame: %s"), *SendResult.Message);
}

// 5. 接收编码后的数据包（例如用于写入文件或发送网络流）
FVideoPacket OutPacket;
while (MyEncoder.ReceivePacket(OutPacket).HasValue())
{
    // 处理编码后的数据包 OutPacket
    // OutPacket.Data 包含压缩后的视频数据
    // OutPacket.Timestamp 为时间戳
}
```

## Demo 示例

以下是一个概念性的完整示例，展示了如何配置并使用 AMF H.264 编码器处理一帧。

**MyVideoEncoderComponent.h**
```cpp
// MyVideoEncoderComponent.h
#pragma once

#include "Components/ActorComponent.h"
#include "Video/Encoders/Configs/VideoEncoderConfigAMF.h"
#include "Video/Encoders/VideoEncoderAMF.h"
#include "AV/VideoResourceVulkan.h" // 假设使用 Vulkan 资源

class UMyVideoEncoderComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
    virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    // 编码器实例
    TVideoEncoderAMF<FVideoResourceVulkan> Encoder;
    // 编码器配置
    FVideoEncoderConfigAMF EncoderConfig;
    // 上下文和设备（简化示例，实际需从 AVCodecs 框架获取）
    TSharedPtr<FAVDevice> AVDevice;
    TSharedPtr<FAVInstance> AVInstance;

    bool bEncoderInitialized = false;
};
```

**MyVideoEncoderComponent.cpp**
```cpp
// MyVideoEncoderComponent.cpp
#include "MyVideoEncoderComponent.h"
#include "AV/AVContext.h" // 示例包含，实际依赖 AVCodecs 模块

void UMyVideoEncoderComponent::BeginPlay()
{
    Super::BeginPlay();

    // 初始化 AMF 上下文和设备 (这里仅为伪代码，实际需要创建或获取有效的上下文)
    AVDevice = MakeShared<FAVDevice>(); // 需要正确初始化
    AVInstance = MakeShared<FAVInstance>(); // 需要正确初始化

    // 配置编码器
    EncoderConfig.CodecType = FVideoEncoderConfigAMF::CodecTypeH264;
    EncoderConfig.Width = 1280;
    EncoderConfig.Height = 720;
    EncoderConfig.RepeatSPSPPS = true;
    // 设置其他 AMF 属性...
    // EncoderConfig.SetProperty(...);

    // 打开编码器
    FAVResult Result = Encoder.Open(AVDevice, AVInstance);
    if (Result.HasValue())
    {
        bEncoderInitialized = true;
        // 应用配置
        Encoder.ApplyConfig();
        UE_LOG(LogTemp, Log, TEXT("AMF H.264 Encoder Opened Successfully."));
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to open AMF Encoder: %s"), *Result.Message);
    }
}

void UMyVideoEncoderComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

    if (!bEncoderInitialized || !Encoder.IsOpen())
    {
        return;
    }

    // 1. 在你的渲染代码中，将场景渲染到一个 FVideoResourceVulkan 纹理
    // TSharedPtr<FVideoResourceVulkan> CurrentFrameResource = RenderSceneToVulkanTexture(...);
    // （此部分代码省略，取决于你的渲染管线）

    // 2. 假设我们获得了当前帧的资源
    // TSharedPtr<FVideoResourceVulkan> CurrentFrameResource = ...;

    // 3. 将帧发送给编码器
    /*
    if (CurrentFrameResource)
    {
        FAVResult SendResult = Encoder.SendFrame(CurrentFrameResource, GetWorld()->GetTimeSeconds());
        if (!SendResult.HasValue())
        {
            UE_LOG(LogTemp, Warning, TEXT("AMF Encoder SendFrame failed: %s"), *SendResult.Message);
        }

        // 4. 尝试接收编码结果
        FVideoPacket Packet;
        while (Encoder.ReceivePacket(Packet).HasValue())
        {
            // 这里可以将 Packet.Data 保存到文件，或通过网络发送
            // WriteToFile(Packet.Data, Packet.Timestamp);
        }
    }
    */
}

void UMyVideoEncoderComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    // 关闭编码器，释放资源
    if (Encoder.IsOpen())
    {
        Encoder.Close();
    }
    Super::EndPlay(EndPlayReason);
}
```

## 模块依赖

从模块 `AMFCodecs` 的 `Build.cs` 文件分析，它依赖于：

| 模块 | 用途 |
|---|---|
| `Vulkan` | 提供 Vulkan RHI 支持，用于在 AMD GPU 上创建和管理 AMF 上下文和表面资源。 |

**说明**：此插件还依赖于隐含的 `AVCodecs` 模块（父插件），该模块提供了基础的编解码器框架（如 `TVideoEncoder`， `FVideoPacket` 等）。你的模块若要使用此插件，通常也需要依赖 `AVCodecs` 和 `AMFCodecs`。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复了在格式化函数中使用作用域枚举可能导致输出错误的 bug |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修正了上一次错误查找替换后的第二次提交 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退了变更列表 CL51314860 的修改 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 将引擎初始化委托的调用方式改为函数获取，以修复注册缺失问题 |
| 2026-01-22 | `ad8a0de1` | Update BuildVersionSettings that are out of date | 更新了过时的构建版本设置 |

### 维护评价

**活跃维护**。虽然此插件标记为实验性（`IsExperimentalVersion: true`）且默认禁用，但从近期的 Git 历史看，它在过去两年内仍有持续的更新和维护（最近一次在2026年4月）。这些更新主要是编译修复和依赖项适配，表明它正在随着引擎核心的发展进行同步维护，以确保其作为实验性功能的基础可用性。

**结论**：此插件适用于需要利用 AMD 硬件编解码能力且不介意其“实验性”状态的 C++ 开发者。它提供了一个相对底层的接口，需要使用者熟悉 AVCodecs 框架。对于生产环境，需要充分测试其在不同 AMD GPU 上的稳定性和性能。由于其活跃的维护状态，可以期待其未来随着引擎版本更新而持续改进。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AVCodecs/AMFCodecs)
- 官方文档：无
- 测试用例：在提供的源码片段中未发现，可能位于 AVCodecs 父插件或引擎的测试目录中。