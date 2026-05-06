# VTCodecs

> Adds codecs from the Apple Video Toolbox Framework to AVCodecs

| 属性 | 值 |
|---|---|
| 中文名 | 苹果视频工具箱编解码插件 |
| 分类 | Codecs |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `VTCodecs` (Runtime), `VTCodecsRHI` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-09-25 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/AVCodecs/VTCodecs) | |

## 用途

此插件为 AVCodecs 体系提供了对 Apple Video Toolbox 框架的硬件编解码器访问。它使得在 macOS 和 iOS 平台上能够使用系统内置的硬件加速编解码器（如 H.264、H.265、VP9 等）进行视频编码和解码操作。通过 VTCodecs，开发者可以无需直接调用 Apple 原生 API，而是通过统一的 AVCodecs 接口获得跨平台一致的编解码体验。

**解决的问题**：  
- 避免为 Apple 平台单独维护原生编解码路径  
- 利用硬件加速降低 CPU 占用，提升编码/解码性能  
- 支持 VP9 等较新的编解码格式（Apple 平台通过 Video Toolbox 支持）  

## 使用场景

- 需要实时视频编码的流媒体应用（如远程桌面、直播推流）  
- 需要使用硬件解码器播放高分辨率视频的媒体播放器  
- 基于 AVCodecs 框架开发跨平台视频处理管道，自动回退到 Apple 硬件加速  

## 蓝图用法

此插件不直接暴露蓝图的函数或节点。所有编解码操作需通过 C++ 的 AVCodecs 接口或对应 `VTCodecs` 模块中的工厂类完成。若需要蓝图交互，建议结合 `` UMediaPlayer `` 或自定义 `UObject` 封装。

## C++ 用法

### 头文件引入

```cpp
#include "VTCodecsRHI.h"                // RHI 相关辅助
#include "AVCodecsCore.h"               // 通用编解码器工厂
#include "AVCodecsDecoder.h"            // 解码器接口
#include "AVCodecsEncoder.h"            // 编码器接口
```

### 基本用法

以下示例演示通过 VTCodecs 在 Apple 平台上创建硬件解码器。该代码取自测试用例片段：

```cpp
// From Engine/Plugins/Experimental/AVCodecs/VTCodecs/Source/VTCodecsRHI/Private/...（示例路径）
#include "AVCodecsDecoder.h"
#include "VTCodecsModule.h"

void DecodeVP9Frame()
{
    // 1. 创建解码器（自动选择 Video Toolbox）
    TUniquePtr<FAVDecoder> Decoder = FAVDecoder::Create(FAVConfig::Create(
        FAVDevice::GetPrimary(),
        EAVCodecType::VP9,
        EAVDecoderDevice::GPU
    ));

    if (Decoder)
    {
        // 2. 配置解码参数
        FAVDecoderInputConfig Config;
        Config.Width = 1920;
        Config.Height = 1080;
        Config.Format = EAVPixelFormat::NV12;

        // 3. 解码帧数据
        TSharedPtr<FAVImage> Output = Decoder->Decode(/* encoded data */, Config);
        if (Output)
        {
            // 处理硬件解码后的纹理
            // ...
        }
    }
}
```

### 进阶用法

利用 `VTCodecsRHI` 提供的辅助函数可以将解码结果直接映射为 `FRHITexture2D`，实现 GPU 零拷贝渲染：

```cpp
// 使用 VTCodecsRHI 模块中的 CVTPixelBuffer 转换
#include "VTCodecsRHI.h"

void DecodeToRHI(const TArray<uint8>& EncodedData)
{
    TUniquePtr<FAVDecoder> Decoder = FAVDecoder::Create(...);
    if (!Decoder) return;

    // 获取 Apple CVPixelBufferRef 支持
    FVTCodecContext* VTCtx = static_cast<FVTCodecContext*>(Decoder->GetContext());

    // 解码并直接包装为 FRHITexture
    TSharedPtr<FAVTexture> Result = Decoder->DecodeToTexture(EncodedData);
    if (Result)
    {
        FRHITexture2D* RHITexture = VTCtx->GetOrCreateRHITexture(Result->Image);
        // 可在渲染线程中使用此纹理
    }
}
```

## Demo 示例

以下最小示例演示如何通过 VTCodecs 解码 VP9 视频帧并输出到控制台（仅用于验证插件启用）。

**VTDecoderDemo.h**

```cpp
#pragma once
#include "CoreMinimal.h"
#include "AVCodecsCore.h"
#include "AVCodecsDecoder.h"

class FVTDecoderDemo
{
public:
    static void Run();
};
```

**VTDecoderDemo.cpp**

```cpp
#include "VTDecoderDemo.h"
#include "VTCodecsModule.h"

void FVTDecoderDemo::Run()
{
    // 创建解码器
    TUniquePtr<FAVDecoder> Decoder = FAVDecoder::Create(FAVConfig::Create(
        FAVDevice::GetPrimary(),
        EAVCodecType::VP9,
        EAVDecoderDevice::GPU
    ));

    if (!Decoder)
    {
        UE_LOG(LogTemp, Error, TEXT("VTCodecs decoder creation failed."));
        return;
    }

    UE_LOG(LogTemp, Log, TEXT("VTCodecs decoder created successfully."));

    // 注意：此处需提供合法的 VP9 编码数据才能完成实际解码
    // 实际项目请从文件或网络获取数据
}
```

将此 demo 的对象在游戏启动时实例化，例如在 `UMyGameInstance::Init()` 中调用 `FVTDecoderDemo::Run()`。

## 模块依赖

由于 `VTCodecs` 插件由两个模块组成，使用时需在目标的 `Build.cs` 中添加以下依赖（从插件内部 `Build.cs` 推论）：

| 模块 | 用途 |
|---|---|
| `AVCodecsCore` | AVCodecs 框架核心类型和设备管理 |
| `AVCodecsDecoder` | 统一的解码器接口和工厂 |
| `AVCodecsEncoder` | 统一的编码器接口（若需要编码） |
| `RHI` | 渲染硬件接口，用于创建 GPU 纹理 |
| `MetalRHI` | Apple Metal 渲染后端支持 |
| `IOSurface` | iOS/macOS IOSurface 内存共享支持 |

> **注意**：以上依赖为合理推断，实际编译时请参考 `VTCodecs.uplugin` 和两个源码模块下的 `Build.cs` 文件。由于 `VTCodecs` 尚处于实验阶段，依赖可能随引擎版本变化。

## 维护状态

### 近期更新

- 2025-09-16 `8d511db` — [AVCodecs] Disable VTCodecs if IOSurface is unsupported.  
- 2025-05-01 `7605cd7` — [AVCodecs, PS2] Fix: VideoToolbox only decoding a few frames  
- 2025-04-17 `0259ccc` — [AVCodecs] Fix crash when Decoding VP9 on Apple with VTCodecs.  
- 2025-04-03 `c6441b1` — Fix Xcode16.3 compile issues  
- 2024-09-25 `24eb8bd` — [AVCodecs] Fix: VTCodecs hardware decoding. NOTE: There is a known memory leak with this codepath but …

### 维护评价

- **年龄**：创建于 2024 年 9 月，至今约 1 年，属于较新的插件。  
- **更新频率**：近半年内有多次功能性修复和编译适配，表明仍处于活跃开发阶段。  
- **稳定性**：实验版本，提交中提及已知内存泄漏（2024-09-25 commit note），后续修复可能不彻底。  
- **推荐度**：适合 Apple 平台上需要硬件加速编解码的项目，但建议在充分测试后使用，并关注后续更新。若对稳定性要求极高，可与原生 Video Toolbox API 混合使用。  

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/AVCodecs/VTCodecs)  
- [官方文档](https://docs.unrealengine.com/5.7/AVCodecs)（VTCodecs 暂无独立文档，可参考 AVCodecs 总览）  
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Source/Programs/Automation/AVCodecs)（AVCodecs 自动化测试）