# NVCodecs

> Adds codecs from the NVIDIA Media Codec SDK to AVCodecs

| 属性 | 值 |
|---|---|
| 中文名 | NVIDIA编解码器 |
| 分类 | Codecs |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NVCodecs` (Runtime), `NVCodecsRHI` (Runtime), `NVDEC` (Runtime), `NVENC` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-01-25 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AVCodecs/NVCodecs) | |

## 用途

NVCodecs 插件将 NVIDIA 的硬件编解码能力集成到 Unreal Engine 的 AVCodecs 框架中。它主要解决在虚幻引擎中利用 NVIDIA GPU 进行高性能、低延迟的视频编解码问题。具体来说：

1.  **硬件加速解码 (NVDEC)**：提供基于 NVIDIA GPU 的视频解码能力，可用于播放高分辨率视频或处理视频流。
2.  **硬件加速编码 (NVENC)**：提供基于 NVIDIA GPU 的视频编码能力，适用于实时视频录制、推流或视频导出。
3.  **图形API集成 (NVCodecsRHI)**：作为抽象层，确保编解码器能够与引擎底层的图形API（如 DirectX 12, Vulkan）无缝协作。

它存在的意义在于为需要实时视频处理的应用程序（如虚拟制片、广播、高质量录制）提供远超 CPU 编解码的性能。

## 使用场景

-   你需要将游戏画面实时录制为高质量的视频文件（如 MP4）。
-   你在开发一个视频播放器，需要流畅解码 4K/8K 的 H.264/H.265 视频。
-   你正在构建一个实时视频通信或直播推流功能，需要极低的编码延迟。
-   你的项目涉及视频合成或后处理，需要高效的视频帧读写。

## 蓝图用法

此插件为底层运行时模块，主要提供 C++ API。蓝图层面的交互通常通过上层的 `Media` 或 `AVCodecs` 框架进行封装，直接暴露的蓝图节点较少。核心功能更侧重于 C++ 实现。

## C++ 用法

### 头文件引入

使用 NVENC 编码器：
```cpp
#include "NVENC/NVEncoder.h"
```

使用 NVDEC 解码器：
```cpp
#include "NVDEC/NVDecoder.h"
```

### 基本用法

以下是一个使用 NVENC 进行视频编码的基本流程框架（概念性代码）。
```cpp
// 假设已获取到正确的图形API设备和上下文
// #include "NVENC/NVEncoder.h"

// 1. 初始化编码器
FNVEncoder Encoder;
FNVENC_InitializeParams InitParams;
InitParams.Width = 1920;
InitParams.Height = 1080;
InitParams.FrameRate = 60;
// 设置编码格式 (H.264/HEVC)， 码率， Profile 等参数
bool bSuccess = Encoder.Initialize(InitParams);

// 2. 获取一帧输入纹理 (例如，从渲染目标获取)
FTextureRHIRef InputTexture = GetMyRenderTargetResource()->GetRenderTargetTexture();

// 3. 编码帧
FNVENC_EncodeFrameParams EncodeParams;
EncodeParams.Texture = InputTexture;
FNVENC_EncodeOutput Output;
bSuccess = Encoder.Encode(EncodeParams, Output);

// 4. 处理编码输出 (Output 包含编码后的比特流数据)
if (bSuccess)
{
    // 可以将 Output.BitstreamData 写入文件或发送到网络
}

// 5. 清理
Encoder.Shutdown();
```
*（基于对 NVENC 模块的推断和 NVIDIA NVENC SDK 的通用用法）*

### 进阶用法

结合 `NVCodecsRHI` 模块处理不同的图形API上下文，并管理编码会话的生命周期。
```cpp
// 确保在正确的 RHI 上下文中操作
// #include "NVCodecsRHI.h"
// #include "NVENC/NVEncoder.h"

// 从 RHI 层获取适用于当前环境的设备指针
void* NativeDevice = NVCodecsRHI::GetDevice(); // 示例函数

FNVEncoder Encoder;
// 在初始化时可能需要传入特定的设备指针
Encoder.InitializeForDevice(NativeDevice, InitParams);

// 后续编码流程与基本用法类似...
// 在编码过程中，可实时调整码率、分辨率等参数 (如果编码器支持动态参数调整)
```
*（基于模块依赖和 NVIDIA 编码器架构的典型用法）*

## Demo 示例

一个最小化的 NVENC 编码器封装类头文件示例：
```cpp
// MySimpleNvencEncoder.h
#pragma once

#include "NVENC/NVEncoder.h"

class FMySimpleNvencEncoder
{
public:
    bool Init(uint32 Width, uint32 Height);
    bool EncodeFrame(FTextureRHIRef InputTexture, TArray<uint8>& OutEncodedData);
    void Shutdown();

private:
    TUniquePtr<FNVEncoder> Encoder;
};

// MySimpleNvencEncoder.cpp
#include "MySimpleNvencEncoder.h"

bool FMySimpleNvencEncoder::Init(uint32 Width, uint32 Height)
{
    Encoder = MakeUnique<FNVEncoder>();
    FNVENC_InitializeParams Params;
    Params.Width = Width;
    Params.Height = Height;
    Params.FrameRate = 30;
    // ... 设置其他必要的编码参数
    return Encoder->Initialize(Params);
}

bool FMySimpleNvencEncoder::EncodeFrame(FTextureRHIRef InputTexture, TArray<uint8>& OutEncodedData)
{
    if (!Encoder || !InputTexture) return false;

    FNVENC_EncodeFrameParams FrameParams;
    FrameParams.Texture = InputTexture;

    FNVENC_EncodeOutput Output;
    if (Encoder->Encode(FrameParams, Output))
    {
        OutEncodedData = MoveTemp(Output.BitstreamData);
        return true;
    }
    return false;
}

void FMySimpleNvencEncoder::Shutdown()
{
    if (Encoder)
    {
        Encoder->Shutdown();
        Encoder.Reset();
    }
}
```
*(这是一个简化的演示，实际使用需要处理同步、线程安全、错误检查以及更多参数配置)*

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Vulkan` | 为 VULKAN RHI 提供 NVIDIA 编解码器的底层支持。 |
| `CUDA` | NVIDIA 的并行计算平台，NVCodecs 内部用于与 GPU 交互。 |
| `NVAPI` | NVIDIA 提供的专用 API 库，用于获取 GPU 功能和进行底层控制。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `408f8cf3` | [NvEnc] Add: Launch arg and config option to revert to legacy D3D12 -> CUDA -> NvEnc code path to wo | 为 NVENC 添加命令行参数和配置项，可回退到传统的 D3D12->CUDA->NvEnc 代码路径。 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复了用于格式化函数的强类型枚举问题，该问题可能导致输出乱码。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复上次错误查找替换后的第二次提交。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退 CL 51314860 的更改。 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 修复委托注册问题，将 FCoreDelegates::OnPostEngineInit 迁移为函数调用形式。 |

### 维护评价

**活跃维护中**。尽管标记为实验性插件且默认未启用，但从近期的 Git 提交历史（最近一次更新在2026年5月）可以看出，该插件仍在持续进行开发和问题修复。更新内容包括新功能支持（如代码路径回退）、重要 Bug 修复（枚举格式化、委托注册）以及稳定性改进。鉴于其提供关键的硬件加速能力，且仍在积极维护，对于需要 NVIDIA 硬件编解码支持的项目来说是**推荐使用**的。但需注意其“实验性”标签，意味着 API 可能发生变化，且需要额外的环境配置（如 NVIDIA 驱动、CUDA 工具包）。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AVCodecs/NVCodecs)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AVCodecs/NVCodecs/Tests) (如果存在)