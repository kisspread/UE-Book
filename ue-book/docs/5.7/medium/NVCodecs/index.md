# NVCodecs

> Adds codecs from the NVIDIA Media Codec SDK to AVCodecs

| 属性 | 值 |
|---|---|
| 分类 | Codecs |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NVCodecs` (Runtime), `NVCodecsRHI` (Runtime), `NVDEC` (Runtime), `NVENC` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-01-25 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/AVCodecs/NVCodecs) | |

## 用途

NVCodecs 是 UE5 AVCodecs 框架的 NVIDIA 硬件编解码后端。它将 NVIDIA Media Codec SDK（NVENC/NVDEC）集成到引擎的统一视频编解码抽象层中，使得 UE 的视频编码器/解码器可以选择 NVIDIA GPU 硬件加速路径。

这个 plugin 解决的核心问题是：**利用 NVIDIA GPU 上专用的编解码硬件（NVENC 编码器、NVDEC 解码器）来实现高性能视频编解码**，而非通过 CPU 或通用 GPU 计算。这是 Pixel Streaming、视频录制、媒体播放等功能的底层加速基础。

Plugin 位于 `Experimental/AVCodecs/` 路径下，依赖同目录的 `AVCodecsCore` plugin 提供的统一抽象接口。

## 使用场景

- 你需要用 NVIDIA GPU 硬件编码视频流（H.264/H.265/AV1）→ 使用 NVENC 编码器
- 你需要用 NVIDIA GPU 硬件解码视频流（H.264/H.265/AV1）→ 使用 NVDEC 解码器
- 你在做 Pixel Streaming，需要低延迟硬件编码 → NVCodecs 提供 NVENC 后端
- 你需要在 D3D11/D3D12/Vulkan 渲染后端之间无缝切换编解码 → NVCodecs 自动适配

## 蓝图用法

NVCodecs 没有暴露任何 `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)`。它是一个纯 C++ 运行时模块，通过 AVCodecs 框架的注册机制自动被上层功能（如 Pixel Streaming）发现和使用。蓝图用户无法直接操作此 plugin。

## C++ 用法

### 头文件引入

```cpp
// 编码器
#include "Video/Encoders/VideoEncoderNVENC.h"
#include "Video/Encoders/Configs/VideoEncoderConfigNVENC.h"

// 解码器
#include "Video/Decoders/VideoDecoderNVDEC.h"
#include "Video/Decoders/Configs/VideoDecoderConfigNVDEC.h"

// CUDA 资源
#include "Video/Resources/VideoResourceCUDA.h"

// API 句柄
#include "NVENC.h"
#include "NVDEC.h"
```

### 基本用法 — NVENC 编码

NVCodecs 通过 AVCodecs 框架的 `FVideoEncoder::RegisterPermutationsOf` 机制注册编码器。启动时（`NVENCModule`）自动注册以下编码路径：

| 编解码器 | 资源类型 | 平台 |
|---|---|---|
| H.264 | CUDA + Vulkan | Win64, Linux |
| H.265 | CUDA + Vulkan | Win64, Linux |
| AV1 | CUDA + Vulkan | Win64, Linux |
| H.264 | D3D11 | Win64 |
| H.265 | D3D11 | Win64 |
| AV1 | D3D11 | Win64 |
| H.264 | D3D12 | Win64 |
| H.265 | D3D12 | Win64 |
| AV1 | D3D12 | Win64 |

使用者通常不直接实例化 `FVideoEncoderNVENC*`，而是通过 AVCodecs 框架请求编码器：

```cpp
// 通过 AVCodecs 框架获取编码器（伪代码，依赖具体上层 API）
// NVCodecs 注册后，框架会自动选择匹配的硬件编码器
FVideoEncoderConfigNVENC Config;
Config.presetGUID = NV_ENC_PRESET_P1_GUID;  // 低延迟预设
Config.frameRateNum = 60;
Config.frameRateDen = 1;

// 编码配置支持 H.264、H.265、AV1 三种编解码器
// 通过 FAVExtension::TransformConfig 从通用配置转换为 NVENC 专用配置
```

来源：`Source/NVENC/Public/Video/Encoders/Configs/VideoEncoderConfigNVENC.h`

### 基本用法 — NVDEC 解码

`NVDECModule` 在启动时自动注册 H.264、H.265、AV1 解码路径，支持的输出资源类型包括：

- `FVideoResourceCUDA`（跨平台）
- `FVideoResourceD3D11`（Win64）
- `FVideoResourceD3D12`（Win64）
- `FVideoResourceVulkan`（跨平台）

解码器使用 CUDA Video Parser 回调机制：

```cpp
// NVDEC 使用回调驱动的解码模型
class FVideoDecoderNVDEC : public TVideoDecoder<FVideoResourceCUDA, FVideoDecoderConfigNVDEC>
{
    // 回调函数由 CUDA Video Parser 调用
    int HandleVideoSequence(CUVIDEOFORMAT *VideoFormat);   // 流序列头解析
    int HandlePictureDecode(CUVIDPICPARAMS *PicParams);    // 帧解码
    int HandlePictureDisplay(CUVIDPARSERDISPINFO *DispInfo); // 帧显示
};
```

来源：`Source/NVDEC/Public/Video/Decoders/VideoDecoderNVDEC.h`

### 进阶用法 — CUDA 资源互操作

NVCodecs 核心模块提供 `FVideoResourceCUDA`，用于在不同图形 API 之间转换视频资源：

```cpp
// Win64: D3D11/D3D12 资源转 CUDA 资源
template <>
FAVResult FAVExtension::TransformResource(
    TSharedPtr<FVideoResourceCUDA>& OutResource,
    TSharedPtr<FVideoResourceD3D11> const& InResource);

template <>
FAVResult FAVExtension::TransformResource(
    TSharedPtr<FVideoResourceCUDA>& OutResource,
    TSharedPtr<FVideoResourceD3D12> const& InResource);

// 跨平台: Vulkan 资源转 CUDA 资源
template <>
FAVResult FAVExtension::TransformResource(
    TSharedPtr<FVideoResourceCUDA>& OutResource,
    TSharedPtr<FVideoResourceVulkan> const& InResource);
```

CUDA 资源支持异步拷贝：

```cpp
// 同步拷贝
FAVResult CopyFrom(CUdeviceptr Target, uint32 MapPitch);
FAVResult CopyTo(CUdeviceptr Source, uint32 MapPitch);

// 异步拷贝
FAVResult CopyFromAsync(CUdeviceptr Target, uint32 MapPitch);
FAVResult CopyToAsync(CUdeviceptr Source, uint32 MapPitch);
```

来源：`Source/NVCodecs/Public/Video/Resources/VideoResourceCUDA.h`

### 进阶用法 — CUDA 颜色空间转换 Kernel

NVCodecs 内置两个 CUDA kernel 用于硬件加速的颜色空间转换：

| Kernel | 功能 | 源码 |
|---|---|---|
| `nv12_to_bgra8` | NV12 → BGRA8 转换 | `Kernels/src/NV12_to_BGRA8.cu` |
| `p010_to_abgr10` | P010 → ABGR10 转换（HDR） | `Kernels/src/P010_to_ABGR10.cu` |

这些 kernel 以预编译的 `.fatbin` 文件分发，支持 SM 5.0 到 SM 7.5 架构。每个 kernel 提供两个变体：
- `*_device`：写入 `CUdeviceptr`（设备内存）
- 标准版本：写入 `cudaSurfaceObject_t`（CUDA Surface）

## Demo 示例

NVCodecs 是底层编解码模块，没有独立的可运行 demo。最简用法是通过 AVCodecs 框架间接使用：

```cpp
// MyModule.Build.cs
PublicDependencyModuleNames.AddRange(new string[] {
    "NVCodecs",
    "NVENC",       // 如果需要编码
    "NVDEC",       // 如果需要解码
    "AVCodecsCore"
});
```

```cpp
// 使用 AVCodecs 框架时，NVCodecs 会自动注册其编解码器
// 你只需要依赖正确的模块，框架会自动发现可用的硬件编解码器
// 具体调用方式取决于上层模块（如 PixelStreaming2）
```

**注意**：此 plugin 默认禁用（`EnabledByDefault: false`），需要在项目设置或 `.uproject` 中手动启用。

## 模块依赖

### NVCodecs 模块（核心/CUDA 资源）

| 模块 | 用途 |
|---|---|
| `RenderCore` | 渲染核心抽象 |
| `Core` | 引擎核心 |
| `Engine` | 引擎框架（私有） |
| `AVCodecsCore` | AV 编解码框架抽象（私有） |
| `CUDA` | CUDA 运行时支持（私有） |
| `Vulkan` | Vulkan 图形 API 支持 |
| `DX11` / `DX12` | DirectX 图形 API 支持（仅 Win64） |

### NVENC 模块（编码器）

| 模块 | 用途 |
|---|---|
| `nvEncode` | NVIDIA NVENC SDK 三方库 |
| `NVCodecs` | CUDA 资源和 kernel |
| `CUDA` | CUDA 运行时 |
| `RHI` | 渲染硬件接口 |
| `VulkanRHI` | Vulkan RHI（私有） |
| `DX11` | DirectX 11（仅 Win64，私有） |

### NVDEC 模块（解码器）

| 模块 | 用途 |
|---|---|
| `nvDecode` | NVIDIA NVDEC (cuviddec) SDK 三方库 |
| `NVCodecs` | CUDA 资源和 kernel |
| `CUDA` | CUDA 运行时 |
| `RHI` | 渲染硬件接口 |
| `VulkanRHI` | Vulkan RHI（私有） |
| `DX11` | DirectX 11（仅 Win64，私有） |

### NVCodecsRHI 模块（驱动检测）

| 模块 | 用途 |
|---|---|
| `NVDEC` | NVDEC 解码器 API |
| `NVENC` | NVENC 编码器 API |
| `AVCodecsCore` | AV 框架（私有） |
| `RHI` | 渲染硬件接口 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-11-18 | `d7a4d1607bdc` | [AVCodecs, PixelStreaming2] Fixes: 多个崩溃修复和警告降级 | NVCodecs 作为 AVCodecs 一部分随同修复 |
| 2025-10-01 | `d7bd17da4937` | Don't include windows things if not windows | 平台兼容性修复，避免非 Windows 平台引入 Windows 头文件 |
| 2025-09-23 | `20ee5e0e8b39` | UnrealCodeupFixup tool 修改，支持 -mergemodules 编译 | 代码现代化，为 PixelStreaming2 集成到 RemoteSession 做准备 |

### 维护评价

- **创建时间**：2023-01-25，约 3 年历史
- **维护状态**：**活跃维护** — 2025 年仍有实质性更新（崩溃修复、平台兼容性、代码现代化）
- **实验性标记**：`IsExperimentalVersion: true`，`EnabledByDefault: false`
- **平台支持**：Win64 + Linux，排除 Server 目标
- **驱动要求**：Windows 需要 NVIDIA 驱动 ≥ 531.61，Linux 需要 ≥ 530.41
- **注意事项**：
  - 此 plugin 是实验性的，API 可能发生变化
  - 需要 NVIDIA GPU 且驱动版本满足要求
  - D3D11 + CUDA 路径有特殊处理（注释指出 D3D11+CUDA 不能正确编码 UE 纹理，因此 D3D11 使用原始 D3D11 设备路径）
  - CUDA kernel 的 `.fatbin` 编译在 Build.cs 中被注释掉，目前以内置二进制分发
- **推荐**：如果你在使用 Pixel Streaming 或需要硬件视频编解码，这是必需的底层模块。虽然是实验性状态，但与 Pixel Streaming 一起被 Epic 积极维护。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/AVCodecs/NVCodecs)
- 依赖 plugin: [AVCodecsCore](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/AVCodecs/AVCodecsCore)
- NVIDIA NVENC SDK: https://developer.nvidia.com/video-codec-sdk
- NVIDIA NVDEC 文档: https://docs.nvidia.com/video-technologies/video-codec-sdk/developer-guide/
