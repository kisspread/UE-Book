# AMFCodecs

> Adds codecs from the AMD Advanced Media Framework SDK to AVCodecs（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | AMF 编解码器 |
| 分类 | Codecs |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AMFCodecs` (Runtime), `AMFCodecsRHI` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-01-25 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AVCodecs/AMFCodecs) | |

## 用途

该插件将 AMD Advanced Media Framework (AMF) SDK 集成到 UE5 的 `AVCodecs` 框架中，为引擎提供了基于 AMD GPU 的硬件加速视频编码能力（主要是 H.264/AVC 和 H.265/HEVC）。它解决了使用软件编码器（如 `VideoToolbox` 或 `x264`）带来的 CPU 占用高、功耗大和延迟高的问题，特别是在需要高质量、低延迟硬件编码的场景中。

## 使用场景

-   你需要进行游戏画面录制（Replay）或直播推流，并希望利用 AMD 显卡进行硬件编码，以降低 CPU 负载和功耗。
-   你正在开发云游戏或串流服务，对编码延迟和画质有极高要求。
-   你的项目中使用了 `MediaIOCore` 或自定义媒体管道，需要接入硬件编码能力。

## 蓝图用法

该插件主要在 C++ 层面工作，通过配置 `AVCodecs` 框架来启用。蓝图层面的直接节点较少，主要涉及创建和配置编码器实例。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `创建 AMF 编码器实例` | 根据 `AMFCodecs` 模块的注册信息，实例化一个 AMF 编码器 | `UAMFEncoder` (通过工厂) |
| `设置编码参数` | 配置编码器，如分辨率、比特率、Profile 等 | `UAMFEncoder` |

### 使用示例（蓝图描述）

1.  在项目设置中启用 `AMFCodecs` 插件。
2.  在需要编码的类（如 `UGameInstance`）中，通过 `GetSubsystem` 获取 `UAMFCodecsSubsystem`。
3.  调用子系统的工厂方法来创建一个 `UAMFEncoder` 对象。
4.  通过该对象的蓝图可调用函数（如 `SetConfiguration`）设置编码参数。
5.  使用 `SubmitFrame` 等函数输入原始帧数据，通过 `GetEncodedData` 获取压缩后的码流。

## C++ 用法

### 头文件引入

```cpp
#include "AMFCodecs/AMFCodecs.h"
```

### 基本用法

主要涉及初始化 AMF 环境和创建编码器。

```cpp
// 假设已获取有效的 FAMFCodecsModule 实例
FAMFCodecsModule* AMFModule = FModuleManager::GetModulePtr<FAMFCodecsModule>(TEXT("AMFCodecs"));
if (AMFModule && AMFModule->IsAvailable())
{
    // 初始化 AMF 运行时上下文（通常在模块启动时由子系统完成）
    // ...

    // 创建编码器配置
    FAMFEncoderConfig Config;
    Config.Width = 1920;
    Config.Height = 1080;
    Config.FrameRate = {60, 1};
    Config.Bitrate = 20'000'000; // 20 Mbps
    Config.Codec = EAMFVideoCodec::H265;

    // 通过 AMF 子系统创建编码器实例
    UAMFEncoder* Encoder = NewObject<UAMFEncoder>();
    if (Encoder->Initialize(Config))
    {
        // 编码器准备就绪
    }
}
```

### 进阶用法

结合 `MediaIOCore` 或 `AVRender` 管道进行实时编码，并处理异步操作。

```cpp
// 在 MediaOutput 或自定义渲染通道中使用
void EncodeVideoFrame(const FTexture2DRHIRef& Texture)
{
    if (Encoder && Encoder->IsReady())
    {
        // 将 RHI 纹理提交给编码器
        // AMF 编码器会通过 RHI（Vulkan/D3D12）直接访问 GPU 内存
        Encoder->SubmitFrameGPU(Texture);

        // 异步获取编码后的数据包
        Encoder->GetEncodedDataAsync([this](TArray<uint8> EncodedData, FTimespan Duration, bool bKeyFrame)
        {
            // 处理编码后的码流，例如写入文件、发送到网络
            ProcessEncodedPacket(EncodedData, bKeyFrame);
        });
    }
}
```

## Demo 示例

一个最小的控制台应用示例，演示如何编码一帧测试数据。

```cpp
// AMFCodecsDemo.h
#pragma once
#include "CoreMinimal.h"

class FAMFCodecsDemo
{
public:
    void RunDemo();
};

// AMFCodecsDemo.cpp
#include "AMFCodecsDemo.h"
#include "AMFCodecs/AMFCodecs.h"
#include "AMFCodecs/AMFEncoder.h"

void FAMFCodecsDemo::RunDemo()
{
    FAMFCodecsModule* AMFModule = FModuleManager::GetModulePtr<FAMFCodecsModule>(TEXT("AMFCodecs"));
    if (!AMFModule || !AMFModule->IsAvailable())
    {
        UE_LOG(LogTemp, Error, TEXT("AMFCodecs module not available."));
        return;
    }

    // 配置编码器
    FAMFEncoderConfig EncoderConfig;
    EncoderConfig.Width = 640;
    EncoderConfig.Height = 480;
    EncoderConfig.FrameRate = {30, 1};
    EncoderConfig.Bitrate = 5'000'000;
    EncoderConfig.Codec = EAMFVideoCodec::H264;

    // 创建并初始化编码器
    UAMFEncoder* Encoder = NewObject<UAMFEncoder>();
    if (!Encoder->Initialize(EncoderConfig))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to initialize AMF encoder."));
        return;
    }

    // 生成一帧测试数据 (NV12 格式)
    int32 FrameSize = EncoderConfig.Width * EncoderConfig.Height * 3 / 2; // NV12
    TArray<uint8> TestFrame;
    TestFrame.SetNumUninitialized(FrameSize);
    FMemory::Memset(TestFrame.GetData(), 128, FrameSize); // 灰色填充

    // 提交并编码
    Encoder->SubmitFrameCPU(TestFrame.GetData(), FrameSize);
    Encoder->Flush();

    // 获取编码结果
    TArray<uint8> EncodedData;
    if (Encoder->GetEncodedData(EncodedData) && EncodedData.Num() > 0)
    {
        UE_LOG(LogTemp, Log, TEXT("Encoded %d bytes of H.264 data."), EncodedData.Num());
        // 可将 EncodedData 保存为 .h264 文件
    }

    Encoder->Close();
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Vulkan` | AMF SDK 通过 Vulkan API 与 AMD GPU 硬件交互，获取硬件加速上下文和纹理资源。这是该插件最核心的依赖。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复了作用域枚举在格式化函数中可能导致输出乱码的问题 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复了前一次提交中错误的查找替换操作。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退了 CL51314860 的更改。 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 将委托获取方式从直接引用改为Get函数，修复了初始化顺序导致的注册缺失问题。 |
| 2026-01-22 | `ad8a0de1` | Update BuildVersionSettings that are out of date | 更新了过时的构建版本设置。 |

### 维护评价

该插件创建于 2023 年初，属于较新的实验性功能。从近期的提交记录（最新至 2026 年 4 月）来看，**维护活跃**，主要集中在修复 bug 和适配引擎底层 API 的变更（如委托系统）。

**注意事项**：
-   **实验性插件**：标记为 `IsExperimentalVersion: true` 且默认未启用 (`EnabledByDefault: false`)，表明其 API 和功能尚未完全稳定，可能在未来版本中发生重大变化。
-   **硬件依赖**：功能的实现强依赖于用户系统上安装了兼容的 AMD 显卡驱动和 AMF 运行时。
-   **推荐使用**：如果你的项目明确需要在 AMD 硬件上进行高性能视频编码，并且可以接受实验性插件的稳定性风险，那么推荐尝试使用。对于生产环境，建议进行充分测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AVCodecs/AMFCodecs)
- [AMD AMF SDK 官方文档](https://github.com/GPUOpen-LibrariesAndSDKs/AMF) (外部链接)