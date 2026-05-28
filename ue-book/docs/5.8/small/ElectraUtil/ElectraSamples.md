# Electra Player Utilities

> Reusable Base Components for Electra Player Media Playback

| 属性 | 值 |
|---|---|
| 中文名 | Electra 媒体组件库 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ElectraBase` (RuntimeNoCommandlet), `ElectraSamples` (RuntimeNoCommandlet), `ElectraHTTPStream` (RuntimeNoCommandlet) |
| 实验性 | 否 |
| 创建时间 | 2021-01-06 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraUtil) | |

## 用途

ElectraUtil 是 Epic 专为 Electra 媒体播放器构建的**底层基础设施库**，封装了媒体播放流程中最复杂、最平台相关的部分：

1. **平台纹理采样抽象**：为 Windows（DX11/DX12）、Apple（Metal）、Android（OES/Vulkan）、Linux 提供统一的纹理样本接口，解码器只需关注解码逻辑，GPU 侧的资源创建与同步由本插件处理
2. **GPU 缓冲池管理**：DX12 侧实现了基于 Heap + Fence 的解码输出缓冲池（`FElectraMediaDecoderOutputBufferPool_DX12`），避免频繁的 GPU 资源分配/释放
3. **HDR 与色彩空间**：封装 MPEG 标准的色彩基原（Color Primaries）、传输特性（Transfer Characteristics）、矩阵系数（Matrix Coefficients）到 UE 内部色彩空间的映射，统一处理 SDR/HDR（HLG、PQ/ST2084）场景
4. **音频/字幕/元数据样本**：提供符合 UE Media Framework 接口规范的音频样本（`FElectraAudioSample`）、字幕样本（`FElectraSubtitleSample`）、二进制元数据样本（`IElectraBinarySample`）实现
5. **对象池机制**：所有样本类型都接入 `TMediaObjectPool`，通过池化复用降低 GC 压力和内存分配开销

本插件**不面向终端用户**，它是 Electra Player 媒体播放器（用于 MPEG-DASH、HLS 流媒体播放）的核心依赖库。游戏开发者通常不会直接使用此插件。

## 使用场景

- 你在开发自定义媒体解码器插件，需要平台无关的纹理样本 → 用 ElectraSamples 的 `IElectraTextureSampleBase` 继承体系
- 你在实现 DX12 视频解码器，需要管理解码输出缓冲区的 GPU 同步 → 用 `FElectraMediaDecoderOutputBufferPool_DX12`
- 你在处理 MPEG-DASH/HLS 流中的 timed metadata 事件 → 用 `IElectraBinarySample`
- 你需要将 MPEG 色彩描述（VUI 参数）转换为 UE 色彩空间 → 用 `ElectraColorimetryUtils`

## 蓝图用法

本插件为纯 C++ 运行时库，所有 API 均为 C++ 层接口，**不暴露任何蓝图节点**。以下 API 需在 C++ 中调用。

## C++ 用法

### 头文件引入

```cpp
// 纹理样本基础接口
#include "IElectraTextureSample.h"

// 音频样本
#include "IElectraAudioSample.h"

// 元数据样本
#include "IElectraMetadataSample.h"

// 字幕样本
#include "IElectraSubtitleSample.h"

// 色彩空间工具
#include "ElectraTextureSampleUtils.h"

// 平台纹理样本（Windows 为例）
#include "Windows/ElectraTextureSample.h"

// DX12 GPU 缓冲池
#include "Windows/WindowsElectraTextureSampleGPUBufferHelper.h"
```

### 基本用法 — 音频样本分配

```cpp
#include "IElectraAudioSample.h"

// 从对象池获取一个音频样本
FElectraAudioSamplePool AudioSamplePool;
FElectraAudioSample* Sample = AudioSamplePool.AcquireShared();

// 分配缓冲区（16-bit PCM, 立体声, 1024 帧）
Sample->AllocateFor(EMediaAudioSampleFormat::Int16, 2, 1024);

// 将解码后的音频数据拷入
void* WritableBuffer = Sample->GetWritableBuffer();
FMemory::Memcpy(WritableBuffer, DecodedAudioData, Sample->GetAllocatedSize());

// 设置时间戳信息
Sample->SetParameters(48000, FMediaTimeStamp(PresentationTime), Duration);
Sample->SetNumFrames(1024);
```

### 基本用法 — 色彩空间转换

```cpp
#include "ElectraTextureSampleUtils.h"

// 将 MPEG VUI 参数转换为 UE 内部色彩空间
uint8 MPEGColorPrimaries = 9;  // BT.2020
uint8 MPEGMatrixCoeffs = 9;    // BT.2020
uint8 MPEGTransferChar = 16;   // ST2084 (PQ)

UE::Color::EColorSpace ColorSpace = ElectraColorimetryUtils::TranslateMPEGColorPrimaries(MPEGColorPrimaries);
// → UE::Color::EColorSpace::Rec2020

UE::Color::EEncoding Encoding = ElectraColorimetryUtils::TranslateMPEGTransferCharacteristics(MPEGTransferChar);
// → UE::Color::EEncoding::ST2084
```

*来源: `Public/ElectraTextureSampleUtils.h`*

### 进阶用法 — DX12 解码输出缓冲池

```cpp
#include "Windows/WindowsElectraTextureSampleGPUBufferHelper.h"

// 创建一个用于上传数据的缓冲池（用于 CPU→GPU 数据传输）
TRefCountPtr<ID3D12Device> D3D12Device = /* 从 RHI 获取 */;
auto BufferPool = MakeShared<FElectraMediaDecoderOutputBufferPool_DX12, ESPMode::ThreadSafe>(
    D3D12Device,
    4,          // MaxNumBuffers
    1920,       // Width
    1080,       // Height
    4,          // BytesPerPixel (RGBA8)
    D3D12_HEAP_TYPE_UPLOAD
);

// 检查是否有可用缓冲区
if (BufferPool->BufferAvailable())
{
    FElectraMediaDecoderOutputBufferPool_DX12::FOutputData OutputData;
    HRESULT Result;
    FString Message;
    uint32 Pitch = 0;

    bool bSuccess = BufferPool->AllocateOutputDataAsBuffer(Result, Message, OutputData, Pitch);
    if (bSuccess)
    {
        // OutputData.Resource 是 ID3D12Resource，可直接 Map 写入解码数据
        // OutputData.Fence + OutputData.FenceValue 用于 GPU 同步
    }
}

// 创建用于 GPU 纹理的缓冲池
auto TexturePool = MakeShared<FElectraMediaDecoderOutputBufferPool_DX12, ESPMode::ThreadSafe>(
    D3D12Device,
    4, 1920, 1080,
    DXGI_FORMAT_NV12,  // NV12 视频格式
    D3D12_HEAP_TYPE_DEFAULT
);

FElectraMediaDecoderOutputBufferPool_DX12::FOutputData TextureData;
TexturePool->AllocateOutputDataAsTexture(Result, Message, TextureData, 1920, 1080, DXGI_FORMAT_NV12);
```

*来源: `Public/Windows/WindowsElectraTextureSampleGPUBufferHelper.h`*

### 进阶用法 — 元数据事件处理

```cpp
#include "IElectraMetadataSample.h"

// 接收到一个元数据样本后，检查其来源和内容
TSharedPtr<IElectraBinarySample, ESPMode::ThreadSafe> MetadataSample = /* 从播放器获取 */;

if (MetadataSample->GetOrigin() == IElectraBinarySample::EOrigin::InbandEventStream)
{
    // 处理 MPEG-DASH inband 事件
    const FString& SchemeId = MetadataSample->GetSchemeIdUri();
    const FString& Value = MetadataSample->GetValue();
    const void* Data = MetadataSample->GetData();
    uint32 DataSize = MetadataSample->GetSize();

    // 获取相对时间（如果有非零基准时间）
    TOptional<FMediaTimeStamp> BaseTime = MetadataSample->GetTrackBaseTime();
    FMediaTimeStamp EventTime = MetadataSample->GetTime();
}
```

*来源: `Public/IElectraMetadataSample.h`*

## Demo 示例

> ⚠️ 本插件为 Electra Player 的内部基础设施，不建议独立使用。以下示例展示如何继承 `IElectraTextureSampleBase` 创建自定义平台纹理样本。

```cpp
// MyCustomTextureSample.h
#pragma once

#include "IElectraTextureSampleSample.h"  // IElectraTextureSampleBase

class FMyCustomTextureSample final
    : public IElectraTextureSampleBase
    , public IMediaTextureSampleConverter
{
public:
    FMyCustomTextureSample() = default;
    virtual ~FMyCustomTextureSample() = default;

    // --- IMediaTextureSample 接口 ---
    const void* GetBuffer() override { return Buffer.IsValid() ? Buffer->GetData() : nullptr; }
    uint32 GetStride() const override { return Stride; }
    EMediaTextureSampleFormat GetFormat() const override { return SampleFormat; }

#if WITH_ENGINE
    FRHITexture* GetTexture() const override { return Texture.GetReference(); }
#endif

    IMediaTextureSampleConverter* GetMediaTextureSampleConverter() override { return this; }

    // --- IMediaTextureSampleConverter 接口 ---
    uint32 GetConverterInfoFlags() const override { return ConverterInfoFlags_PreprocessOnly; }
    bool Convert(FRHICommandListImmediate& RHICmdList, FTextureRHIRef& InDstTexture,
                 const FConversionHints& Hints) override
    {
        // 在此处实现平台特定的纹理数据上传
        // 例如：从 Buffer 拷贝到 InDstTexture
        return true;
    }

    // --- 池化接口 ---
    bool FinishInitialization() override
    {
        // 从 Electra::FParamDict 初始化采样参数
        return IElectraTextureSampleBase::FinishInitialization();
    }

#if !UE_SERVER
    void ShutdownPoolable() override
    {
        // 释放 GPU 资源
        Texture.SafeRelease();
        Buffer.Reset();
        IElectraTextureSampleBase::ShutdownPoolable();
    }
#endif

    // 自定义数据
    TSharedPtr<TArray64<uint8>, ESPMode::ThreadSafe> Buffer;
    EMediaTextureSampleFormat SampleFormat = EMediaTextureSampleFormat::Undefined;
    uint32 Stride = 0;

private:
    FTextureRHIRef Texture;
};

// 对象池
class FMyCustomTextureSamplePool
    : public TMediaObjectPool<FMyCustomTextureSample, FMyCustomTextureSamplePool>
{
    using TextureSample = FMyCustomTextureSample;
public:
    FMyCustomTextureSamplePool()
        : TMediaObjectPool<TextureSample, FMyCustomTextureSamplePool>(this)
    {}
    TextureSample* Alloc() const { return new TextureSample(); }
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `DirectX` | Windows DX11/DX12 纹理样本与 GPU 缓冲池管理 |

无其他特殊依赖（仅标准 Core/Engine 等）。

> 注意：ElectraBase 和 ElectraHTTPStream 模块的具体依赖未在 Build.cs 分析中完整展示，但作为运行时媒体组件，它们同样依赖 Core/Engine 基础模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `bc37b7ea` | ElectraUtil: added stub methods for server builds to prevent linker errors when this class is accide | 为服务器构建添加桩方法，防止链接错误 |
| 2026-04-23 | `efcad028` | HDR: Fix HDR normalization factor across media causing incorrect brightness levels going from/to the | 修复 HDR 归一化因子导致跨媒体亮度不正确的问题 |
| 2026-04-20 | `3ed2062b` | ElectraDecoders: modernized the decoder factory to be more usable for other clients | 现代化解码器工厂，提升其他客户端的可用性 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏从 UE_LOG 迁移到 UE_LOGF |
| 2026-03-25 | `2924c4cc` | [ElectraUtil] Fix timecode subframe precision loss in CreateTimecodeFromMPEGDefinition | 修复 MPEG 时间码子帧精度丢失问题 |

### 维护评价

**活跃维护中。** 该插件自 2021 年创建以来持续更新，最近 3 个月（2026 年 3-5 月）仍有功能性改进和 bug 修复，包括 HDR 亮度校正、时间码精度修复、服务器兼容性改善等。

- ✅ 仍在活跃维护，更新频率稳定
- ✅ 功能成熟，被 Electra Player（UE 默认的 MPEG-DASH/HLS 播放器）直接依赖
- ⚠️ `EnabledByDefault=false`，需要在项目设置中手动启用或被其他插件自动启用
- ⚠️ 不支持 Server 目标（`TargetDenyList: ["Server"]`）
- ✅ 支持所有主流客户端平台（Win64, Mac, iOS, tvOS, Android, Linux）

**推荐使用**：如果你正在开发或扩展 Electra 媒体播放器，此插件是必选依赖。对于一般的媒体播放需求，直接使用 Media Framework 或 Electra Player 插件即可，无需直接接触本库。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraUtil)
- [官方文档](https://docs.unrealengine.com/en-US/Engine/MediaFramework/Overview)
- [ElectraSamples 源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraUtil/Source/ElectraSamples)