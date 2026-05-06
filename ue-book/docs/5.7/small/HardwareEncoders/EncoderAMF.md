# HardwareEncoders

> Adds support of hardware encoders to AVEncoder

| 属性 | 值 |
|---|---|
| 中文名 | 硬件编码器 |
| 分类 | Encoders |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `EncoderAMF` (Runtime), `EncoderNVENC` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-03-14 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/HardwareEncoders) | |

## 用途

提供 AMD AMF（Advanced Media Framework）和 NVIDIA NVENC 硬件编码器的集成，作为 AVEncoder 框架的底层实现。当系统检测到支持的硬件时，自动使用 GPU 加速编码，大幅降低 CPU 负载，适用于实时推流、本地录制等场景。

## 使用场景

- **直播推流**：利用 GPU 编码减少 CPU 占用，提高游戏和直播的流畅度。
- **本地高画质录制**：硬件编码可支持 4K/60fps 甚至更高规格，且不影响游戏帧率。
- **转码服务**：服务器端批量转码时使用硬件编码器提升吞吐量。
- **边缘计算**：在低功耗设备上实现硬件加速编码（如搭载 AMD/NVIDIA 显卡的设备）。

## 蓝图用法

此插件不直接暴露蓝图中可调用的节点或对象，所有功能通过 C++ 集成到 AVEncoder 框架中。若需在蓝图中使用硬件编码，可依赖 AVEncoder 模块提供的封装接口（如 `BeginVideoCapture` 等），底层会自动选择硬件编码器。

## C++ 用法

### 头文件引入

```cpp
#include "AVEncoder.h"
#include "EncoderAMF/Amf_Common.h"   // AMF 编码器，仅 Windows
#include "EncoderNVENC/NvEncoder.h" // NVENC 编码器，仅 Windows
```

### 基本用法

使用 `AVEncoder::FAmfCommon` 初始化和创建编码器：

```cpp
// 在启动时初始化 AMF 库（自动加载 Dll）
if (AVEncoder::FAmfCommon::Setup().GetIsAvailable())
{
    // 创建编码器实例（H.264 为例）
    AVEncoder::FVideoEncoderAmf_H264::Register(FVideoEncoderFactory::Get());

    // 获取编码器信息
    FVideoEncoderInfo EncoderInfo;
    // ... 填充输入帧参数
    if (AVEncoder::FVideoEncoderAmf_H264::GetIsAvailable(inputImpl, EncoderInfo))
    {
        // 配置编码层
        FLayerConfig Config;
        Config.Width = 1920;
        Config.Height = 1080;
        Config.Bitrate = 5000000;
        Config.Framerate = 30;
        auto Encoder = FVideoEncoder::Create(*AVEncoder::FVideoEncoderFactory::Get().GetEncoderFactoryByType(EVideoEncoderType::H264), Config);
        // 开始编码...
    }
}
```

### 进阶用法

直接操作 AMF 上下文和编码器：

```cpp
// 获取 AMF 工厂并创建编码器组件
auto& Amf = AVEncoder::FAmfCommon::Setup();
AMFContextPtr Ctx = Amf.GetContext();
AMFComponentPtr Encoder;
if (Amf.CreateEncoder(Encoder))
{
    // 配置编码参数
    Encoder->SetProperty(AMF_VIDEO_ENCODER_USAGE, AMF_VIDEO_ENCODER_USAGE_TRANSCONDING);
    // ... 提交帧
}
```

## Demo 示例

以下最小示例演示了在 Windows 上使用 NVENC 进行硬件编码（简化自测试代码）。

**HardwareEncoderDemo.h**

```cpp
#pragma once
#include "CoreMinimal.h"
#include "HAL/Runnable.h"

class FHardwareEncoderDemo : public FRunnable
{
public:
    static void RunDemo();
    virtual uint32 Run() override;
};
```

**HardwareEncoderDemo.cpp**

```cpp
#include "HardwareEncoderDemo.h"
#include "AVEncoder.h"
#include "EncoderNVENC/NvEncoder.h"
#include "Misc/ScopeLock.h"

void FHardwareEncoderDemo::RunDemo()
{
    // 初始化 NVENC 编码器（需系统支持）
    AVEncoder::FVideoEncoderNvEnc::Register(AVEncoder::FVideoEncoderFactory::Get());
    
    // 创建编码器输入
    TSharedRef<AVEncoder::FVideoEncoderInput> Input = AVEncoder::FVideoEncoderInput::CreateForD3D11(nullptr, 1920, 1080);
    
    // 创建 H.264 编码器
    auto Encoder = AVEncoder::FVideoEncoder::Create(*Factory, AVEncoder::FLayerConfig{1920, 1080, 5000000, 30});
    if (Encoder)
    {
        // 模拟编码几帧（实际应绑定 Render Target）
        for (int i = 0; i < 60; ++i)
        {
            TSharedPtr<AVEncoder::FVideoEncoderInputFrame> Frame = Input->GetAvailableFrame();
            if (Frame)
            {
                AVEncoder::FVideoEncoder::FEncodeOptions EncodeOpt;
                Encoder->Encode(Frame.ToSharedRef(), EncodeOpt);
            }
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AVEncoder` | 编码器抽象框架（必需） |
| `VideoEncoder` | 视频编码基础类型和接口 |
| `RHI` | 渲染硬件接口（用于获取 GPU 设备） |

**注意**：`AMF` 模块依赖 Windows SDK 和 AMD AMF 库，`NVENC` 依赖 NVIDIA 驱动接口。

## 维护状态

### 近期更新

- 2025-10-01 d7bd17d — Don't include windows things if not windows
- 2025-03-13 b059f7b — Fix trivial unreachable code warnings.
- 2024-10-09 c4ad1cc — Fix and silence new PVS 7.33 warnings
- 2024-03-15 ee20867 — QOL: Deprecate AVEncoder (for removal) and its dependencies (to be moved to plugins)
- 2024-03-14 0b34b68 — [Backout] - CL32235200 - CIS Compile Error

### 维护评价

插件作为 AVEncoder 的底层硬件编码器支持，目前仍处于 Beta 状态（`.uplugin` 中标记 `IsBetaVersion=true`）。最近一年内有积极维护（编译修复、警告修复），但核心功能无明显变更。存在已知迁移计划（AVEncoder 及其依赖将被移到插件外部），未来可能不再依赖此内联插件。**建议谨慎使用**，并关注后续源码迁移动态。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/HardwareEncoders)
- [AMD AMF SDK](https://github.com/GPUOpen-LibrariesAndSDKs/AMF)
- [NVIDIA NVENC API](https://developer.nvidia.com/video-encode-and-decode-gpu-support-matrix-new)