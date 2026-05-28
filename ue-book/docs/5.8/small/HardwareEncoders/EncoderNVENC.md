# Hardware Encoders

> Adds support of hardware encoders to AVEncoder

| 属性 | 值 |
|---|---|
| 中文名 | 硬件编码器 |
| 分类 | Encoders |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `EncoderAMF` (Runtime), `EncoderNVENC` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-10-26 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/HardwareEncoders) | |

## 用途

该插件为虚幻引擎的 `AVEncoder`（音视频编码器）框架提供了硬件编码器的后端支持。它主要解决了两个核心问题：

1.  **高性能视频编码**：通过利用 NVIDIA (NVENC) 和 AMD (AMF) 显卡的专用硬件编码单元（GPU 上的固定功能电路），将视频编码（尤其是 H.264 等格式）从 CPU 卸载到 GPU。这能显著降低 CPU 使用率，并实现更低延迟的编码流程，对于实时应用至关重要。
2.  **为 Pixel Streaming 提供基础**：此插件是虚幻引擎 Pixel Streaming 功能的关键底层组件之一。Pixel Streaming 需要高效、低延迟地捕获游戏画面并编码为视频流，硬件编码器完美契合这一需求。

简单来说，`AVEncoder` 定义了一套抽象的视频编码接口，而 `HardwareEncoders` 插件为这些接口注入了由主流显卡厂商（NVIDIA, AMD）提供的、利用硬件加速的高性能实现。

## 使用场景

-   **部署 Pixel Streaming 服务**：当你的项目需要作为 Pixel Streaming 服务器运行时，需要利用 GPU 的硬件编码能力来高效处理多个并发用户的视频流。
-   **开发高性能录制/流式推流功能**：在游戏内开发自定义的视频录制或直播推流功能，需要低 CPU 开销和高编码效率。
-   **进行硬件编码性能基准测试或研究**：利用 `NVENCStats` 等工具监控和优化硬件编码器的延迟与吞吐量。

**重要提示**：此插件默认是 **禁用** 的（`EnabledByDefault: false`），并且标记为 **实验性**（`IsBetaVersion: true`）。你需要在项目的 `.uproject` 文件中或通过编辑器手动启用它，并且应准备好处理可能存在的兼容性或稳定性问题。

## 蓝图用法

此插件的设计目标是为 `AVEncoder` 框架提供底层后端，其核心类（如 `FVideoEncoderNVENC_H264`）通常不直接暴露给蓝图。蓝图层面的使用是通过更高层次的、依赖于此插件的系统（如 Pixel Streaming 插件）间接完成的。

### 核心节点

在当前的插件源码中，没有直接暴露 `BlueprintCallable` 或 `BlueprintReadWrite` 的蓝图接口。它的功能集成点位于 C++ 代码层面。

### 使用示例（蓝图描述）

对于此插件，没有直接的蓝图使用示例。典型的使用流程是：
1.  在 C++ 代码或插件配置中启用 `HardwareEncoders`。
2.  确保你的项目启用了 `PixelStreaming` 或其他依赖 `AVEncoder` 的插件。
3.  运行时，这些插件会自动调用 `HardwareEncoders` 注册的硬件编码器工厂来创建编码器实例。

## C++ 用法

### 头文件引入

要使用 NVENC 编码器，通常需要包含以下头文件：

```cpp
// 主要接口和工厂
#include "VideoEncoderFactory.h" // 来自 AVEncoder 模块
#include "VideoEncoder.h"

// 具体 NVENC 实现 (通常由系统内部使用，但了解有帮助)
#include "NVENC_EncoderH264.h"
```

### 基本用法：注册与查询硬件编码器

硬件编码器通过工厂模式集成到 `AVEncoder` 中。以下代码展示了如何查询 NVENC H264 编码器是否可用，并将其注册到编码器工厂中。

```cpp
// 1. 获取或创建视频编码器工厂实例
TSharedRef<FVideoEncoderFactory> EncoderFactory = MakeShared<FVideoEncoderFactory>();

// 2. 检查 NVENC H264 编码器在当前环境下是否可用
FVideoEncoderInfo EncoderInfo;
bool bIsAvailable = FVideoEncoderNVENC_H264::GetIsAvailable(*InputFrameFactory, EncoderInfo);

if (bIsAvailable)
{
    UE_LOG(LogTemp, Log, TEXT("NVENC H264 encoder is available. Caps: %s"), *EncoderInfo.Description);
}

// 3. 将 NVENC H264 编码器注册到工厂，之后系统可通过工厂请求该编码器
FVideoEncoderNVENC_H264::Register(*EncoderFactory);
```

*（逻辑参考自 `NVENC_EncoderH264.h` 中的 `GetIsAvailable` 和 `Register` 静态函数声明）*

### 进阶用法：编码帧数据（流程概述）

虽然具体调用由 `AVEncoder` 管理器完成，但理解其内部流程有助于调试和优化。以下是一个简化的编码调用流程：

```cpp
// 假设已通过工厂创建了编码器实例
TSharedPtr<FVideoEncoder> Encoder = EncoderFactory->CreateEncoder(“NVENC_H264”);

// 初始化编码器，传入帧输入接口和配置
FLayerConfig Config;
Config.Width = 1920;
Config.Height = 1080;
Config.MaxBitrate = 10000000; // 10 Mbps
// ... 其他配置
Encoder->Setup(InputFrameFactory, Config);

// 当收到需要编码的纹理帧时（例如，来自渲染线程的屏幕截图或游戏场景捕获）
TSharedPtr<FVideoEncoderInputFrame> Frame = InputFrameFactory->CreateFrame();
Frame->SetTexture2D(/* ... 你的D3D11/12纹理指针 ... */);

// 调用编码。这是一个异步操作，编码结果通过回调返回。
FEncodeOptions Options;
Options.bForceKeyFrame = false; // 是否强制关键帧
Encoder->Encode(Frame, Options);

// 编码完成后的回调通常由框架处理，例如将编码后的比特流打包并发送。
```

*（流程综合自 `FVideoEncoder` 基类接口和 `FVideoEncoderNVENC_H264` 的实现逻辑）*

## Demo 示例

此插件没有独立的可运行Demo项目。一个最小化的“Demo”就是**启用该插件后运行 Pixel Streaming 示例项目**。

1.  创建一个新的虚幻引擎项目。
2.  在 `.uproject` 文件中添加以下内容以启用插件：
    ```json
    "Plugins": [
        {
            "Name": "HardwareEncoders",
            "Enabled": true
        },
        {
            "Name": "PixelStreaming",
            "Enabled": true
        }
    ]
    ```
3.  打开 `Engine/Content/PixelStreaming` 目录下的 `PixelStreamingDemo.uproject` 示例。
4.  使用 `-PixelStreaming` 命令行参数打包并运行你的项目。引擎将自动使用 NVENC 或 AMF 进行硬件编码。

## 模块依赖

该插件本身没有独特的公共依赖。但它的子模块依赖于外部厂商 SDK：

| 模块 | 用途 |
|---|---|
| `NVENC` (NVIDIA Video Codec SDK) | EncoderNVENC 模块依赖此 SDK 来调用 NVENC API。SDK 通常需要单独安装或由引擎供应商提供。 |
| `AMF` (AMD Advanced Media Framework) | EncoderAMF 模块依赖此 SDK 来调用 AMD 的硬件编码能力。 |

**注意**：这些依赖是隐式的，包含在模块的 `Build.cs` 中。作为插件使用者，你通常只需确保目标机器上安装了相应的最新显卡驱动程序。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式的 `UE_LOG` 日志宏统一迁移到新的 `UE_LOGF` 宏，属于代码现代化和一致性修复。 |
| 2026-03-02 | `c3f81430` | VulkanRHI: Remove extensions that don't need to be manually loaded anymore from plugin startup: | 清理 Vulkan 相关插件的启动代码，移除了不再需要手动加载的扩展项，可能间接影响相关上下文。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复了上一次代码查找替换中的错误，并重新提交。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 撤回了之前的某次更改（CL51314860），可能引入了问题。 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist... | 修改了引擎核心委托的获取方式，以修复一个注册缺失的问题，属于底层框架调整。 |

### 维护评价

-   **状态**：**维护中**。最近一次更新在 2026 年 4 月，主要是针对代码规范和底层引擎接口变更的适配，表明插件仍在随引擎主线更新。
-   **活动水平**：更新频率较低，最近几次提交均为维护性质（修复编译错误、适配 API 变更、代码清理），没有重大新功能添加。
-   **稳定性与风险**：插件标记为 `IsBetaVersion: true` 且 `EnabledByDefault: false`，表明 Epic 将其视为实验性功能。这意味着 API 可能发生变化，且可能未在所有硬件/驱动组合上进行充分测试。
-   **推荐建议**：**有条件推荐**。如果你正在开发或部署 Pixel Streaming 服务，或明确需要 GPU 硬件编码以降低 CPU 负载和延迟，那么此插件是必要的。但对于一般性的项目开发，除非有上述特定需求，否则无需启用。使用时应密切关注引擎更新日志中关于此插件的变更说明，并做好处理潜在兼容性问题的准备。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/HardwareEncoders)
-   [官方文档 - Pixel Streaming](https://docs.unrealengine.com/5.8/en-US/pixel-streaming-in-unreal-engine/) （硬件编码器是其核心依赖之一）
-   [AVEncoder 模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Source/Runtime/AVEncoder) （插件为其提供后端实现）