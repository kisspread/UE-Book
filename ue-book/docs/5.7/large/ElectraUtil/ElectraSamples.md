# Electra Player Utilities

> Reusable Base Components for Electra Player Media Playback

| 属性 | 值 |
|---|---|
| 中文名 | Electra 播放器实用工具 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ElectraBase` (RuntimeNoCommandlet), `ElectraSamples` (RuntimeNoCommandlet), `ElectraHTTPStream` (RuntimeNoCommandlet) |
| 实验性 | 否 |
| 创建时间 | 2025-09-24 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/ElectraUtil) | |

## 用途

`ElectraUtil` 是为 UE 的 Electra 媒体播放器提供通用可复用组件的底层插件集。它不直接提供播放器实现，而是封装了解码后音频、视频、字幕、元数据样本的标准化处理、内存管理、GPU 纹理转换、颜色空间处理等功能。该插件解决了不同平台（Win64、Mac、iOS、Android、Linux）下媒体样本的格式差异，使开发者能够基于 Electra 构建自定义媒体播放器，而无需重复实现跨平台的音视频样本包装和转换逻辑。

核心组件：
- **ElectraBase**：基础类型和共享基础设施（如参数字典、色彩空间转换工具）。
- **ElectraSamples**：音频、视频（纹理）、字幕、二进制样本的具体实现，包括平台特定的纹理转换（DirectX 11/12、Vulkan、Metal）和 GPU 缓冲区管理。
- **ElectraHTTPStream**：HTTP 流式传输支持（未在源码中详细展示，但声明为独立模块）。

## 使用场景

- **开发自定义媒体播放器**：当你需要基于 Electra 协议层实现播放器时，可使用本插件的样本池和格式转换功能简化音视频样本的接收与渲染。
- **实现视频纹理的跨平台转换**：直接使用 `FElectraTextureSample` 系列类可处理从解码器输出的 GPU/CPU 数据，自动转换为 UE 渲染可用的 `FRHITexture`。
- **处理音频渲染**：使用 `FElectraAudioSample` 管理 PCM 数据，支持浮点或整型格式，并可与 UE 的媒体音频管线集成。
- **处理字幕/元数据**：实现媒体播放器时，可通过 `IElectraSubtitleSample` / `IElectraBinarySample` 接收和处理事件流。

## 蓝图用法

此插件为纯 C++ 库，不提供蓝图可调用的函数或节点。媒体样本的分配、转换和生命周期管理均在 C++ 层完成。若需在蓝图中使用，需在 C++ 中编写桥接逻辑或利用媒体播放器框架（如 MediaPlayer / MediaTexture）的公有接口。

## C++ 用法

### 头文件引入

根据使用的模块引入对应头文件，例如：

```cpp
// 音频样本
#include "IElectraAudioSample.h"

// 纹理样本（Windows 平台）
#include "Windows/ElectraTextureSample.h"

// 颜色空间转换工具
#include "ElectraTextureSampleUtils.h"
```

### 基本用法

**1. 使用 `FElectraAudioSamplePool` 分配和管理音频样本**

```cpp
// 创建音频样本池
FElectraAudioSamplePool SamplePool;

// 分配一个样本
FElectraAudioSample* Sample = SamplePool.Alloc();

// 准备缓冲区（例如：Float 格式，2声道，48000 帧）
Sample->AllocateFor(EMediaAudioSampleFormat::Float, 2, 48000);

// 写入音频数据（假设已有 PCM 数据）
float* AudioData = static_cast<float*>(Sample->GetWritableBuffer());
// ... 填充数据 ...

// 设置时间戳和时长
FMediaTimeStamp Time(1.0, 0);
Sample->SetParameters(48000, Time, FTimespan::FromSeconds(0.1));

// 使用完释放
Sample->ShutdownPoolable();
```

**2. 使用 `FElectraTextureSample` 处理视频纹理（Windows 平台）**

```cpp
// 创建纹理样本（通常由解码器创建，此处仅为示例）
FElectraTextureSample TextureSample;

// 假设从解码器获取到 DX11 纹理
TextureSample.SourceType = FElectraTextureSample::ESourceType::SharedTextureDX11;
TextureSample.TextureDX11 = /* ID3D11Texture2D* */;
TextureSample.SampleFormat = EMediaTextureSampleFormat::CharNV12;
TextureSample.SetDim(FIntPoint(1920, 1080));

// 通过 IMediaTextureSampleConverter 执行转换
IMediaTextureSampleConverter* Converter = TextureSample.GetMediaTextureSampleConverter();
if (Converter)
{
    FRHICommandListImmediate& RHICmdList = FRHICommandListExecutor::GetImmediateCommandList();
    FTextureRHIRef DstTexture; // 目标 RHI 纹理
    Converter->Convert(RHICmdList, DstTexture, IMediaTextureSampleConverter::FConversionHints());
}
```

**3. 使用色彩空间转换工具**

```cpp
#include "ElectraTextureSampleUtils.h"

uint8 MPEGPrimaries = 1; // Rec.709
UE::Color::EColorSpace ColorSpace = ElectraColorimetryUtils::TranslateMPEGColorPrimaries(MPEGPrimaries);
// 得到 UE::Color::EColorSpace::sRGB
```

### 进阶用法

结合 `FElectraTextureSamplePool` 和自动重用机制：

```cpp
// 创建纹理样本池（线程安全，ESPMode::ThreadSafe）
TSharedPtr<FElectraTextureSamplePool> Pool = MakeShared<FElectraTextureSamplePool>();

// 从池中获取样本
FElectraTextureSample* Sample = Pool->Alloc();

// 初始化（设置维度、格式等）
Sample->SetDim(FIntPoint(1920, 1080));
Sample->FinishInitialization();

// 当样本使用完毕后，池会自动回收（池内实现了 ShutdownPoolable 回调）
// 或者手动调用：
Sample->ShutdownPoolable();
// 样本将回到池中供重新分配
```

对于 DX12 GPU 缓冲区管理，可使用 `FElectraMediaDecoderOutputBufferPool_DX12`：

```cpp
// 创建 DX12 输出缓冲区池（例如用于上传堆）
TRefCountPtr<ID3D12Device> Device = /* 获取 D3D12 设备 */;
uint32 MaxBuffers = 8;
uint32 Width = 1920;
uint32 Height = 1080;
uint32 BytesPerPixel = 2; // NV12 每像素 1.5 字节，此处仅为示例
D3D12_HEAP_TYPE HeapType = D3D12_HEAP_TYPE_UPLOAD;

TSharedRef<FElectraMediaDecoderOutputBufferPool_DX12> Pool =
    MakeShared<FElectraMediaDecoderOutputBufferPool_DX12>(
        Device, MaxBuffers, Width, Height, BytesPerPixel, HeapType);

// 检查兼容性
if (Pool->IsCompatibleAsBuffer(MaxBuffers, Width, Height, BytesPerPixel))
{
    // 分配资源
    HRESULT Result;
    FString ErrorMsg;
    uint32 Pitch;
    TRefCountPtr<ID3D12Resource> Resource = Pool->AllocateOutputDataAsBuffer(Result, ErrorMsg, Pool, Pitch);
}
```

## Demo 示例

以下是一个最小示例，展示如何在自定义媒体播放器中使用音频样本和纹理样本。

### ElectraSampleDemo.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "IElectraAudioSample.h"
#include "Windows/ElectraTextureSample.h"

class FElectraSampleDemo
{
public:
    void PlayAudioSample();
    void ProcessVideoSample(FElectraTextureSample& InSample);
};
```

### ElectraSampleDemo.cpp

```cpp
#include "ElectraSampleDemo.h"
#include "MediaObjectPool.h"

void FElectraSampleDemo::PlayAudioSample()
{
    // 创建音频样本池并分配样本
    FElectraAudioSamplePool Pool;
    FElectraAudioSample* Sample = Pool.Alloc();
    
    // 准备 48000 Hz 立体声浮点数据，100ms 长度
    const uint32 NumSamples = 4800; // 48000 * 0.1 * 2
    Sample->AllocateFor(EMediaAudioSampleFormat::Float, 2, NumSamples / 2);
    
    // 写入测试数据（正弦波）
    float* Buffer = static_cast<float*>(Sample->GetWritableBuffer());
    for (uint32 i = 0; i < NumSamples; ++i)
    {
        float t = static_cast<float>(i) / 48000.0f;
        Buffer[i] = FMath::Sin(2.0f * PI * 440.0f * t) * 0.5f;
    }
    
    // 设置时间信息
    Sample->SetParameters(48000, FMediaTimeStamp(0.0, 0), FTimespan::FromSeconds(0.1));
    
    // 假设将样本发送到音频渲染器...
    
    // 释放样本
    Sample->ShutdownPoolable();
}

void FElectraSampleDemo::ProcessVideoSample(FElectraTextureSample& InSample)
{
    // 假设已从解码器获取到 InSample，包含 DX11 纹理
    if (InSample.GetMediaTextureSampleConverter())
    {
        FRHICommandListImmediate& RHICmdList = FRHICommandListExecutor::GetImmediateCommandList();
        FTextureRHIRef DstTexture; // 需要提前准备
        InSample.Convert(RHICmdList, DstTexture, IMediaTextureSampleConverter::FConversionHints());
        // 此时 DstTexture 可用于渲染
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `DirectX` | `ElectraSamples` 模块依赖 DirectX 头文件和库，用于 Windows 平台的纹理转换（DX11/DX12 互操作）。 |

**ElectraBase** 和 **ElectraHTTPStream** 模块未提供详细的 Build.cs 信息，但推测它们仅依赖标准引擎模块（Core, CoreUObject 等）。总体而言，插件独特的依赖仅为 `DirectX`。

## 维护状态

### 近期更新

- 2025-09-25 e6018661 ElectraUtils: Fixed check to BufferAvailable() in the DX12 buffer helpers
- 2025-09-25 83ef846c ElectraSamples: Fixed Linux server build linker error
- 2025-09-25 916bb820 ElectraSamples: calling ShutdownPoolable() in the destructor to avoid potential resource leaks
- 2025-09-24 241a7987 ElectraUtil: Removing hard limit of number of buffer slots in favor of dynamic resizes
- 2025-09-24 7d7c63bd ElectraUtil: fixed DX12 GPU buffer helper heap issues

### 维护评价

该插件创建于 2025 年 9 月，极新，近期提交均为功能修复和稳定性改进（DX12 缓冲区助手、内存泄漏修复、服务器编译问题）。表明目前处于活跃开发阶段，修复迅速。由于插件包含多个平台（Win/Mac/iOS/Android/Linux）和多种 GPU API（DX11/12, Vulkan, Metal），维护工作持续进行。推荐用于基于 Electra 的媒体播放项目，但需注意其仍处于早期版本（Version 1.0），可能需要关注后续更新以获取稳定性和兼容性改进。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/ElectraUtil)
- [官方文档](https://docs.unrealengine.com/en-US/Engine/MediaFramework/Overview)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/ElectraUtil/Source/ElectraSamples/Private)（部分平台实现目录包含测试逻辑，但未发现独立测试文件）