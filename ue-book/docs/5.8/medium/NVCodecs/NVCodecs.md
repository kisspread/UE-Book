# NVCodecs

> Adds codecs from the NVIDIA Media Codec SDK to AVCodecs

| 属性 | 值 |
|---|---|
| 中文名 | NV 编解码器 |
| 分类 | Codecs |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NVCodecs` (Runtime), `NVCodecsRHI` (Runtime), `NVDEC` (Runtime), `NVENC` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-01-25 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AVCodecs/NVCodecs) | |

## 用途

NVCodecs 插件是 UE5 AVCodecs 多媒体处理框架的扩展，核心功能是将 NVIDIA 的 Media Codec SDK（特别是 NVENC 和 NVDEC）集成到引擎中。它解决的主要问题是利用 NVIDIA GPU 进行硬件加速的视频编解码。对于支持 NVIDIA GPU 的系统，该插件可以提供远高于 CPU 软编解码的性能，大幅降低游戏或应用在录制、串流、回放视频时的 CPU 负担。它是对 AVCodecs 软件编解码能力的有力补充，特别适用于对实时性、帧率和画质有较高要求的场景。

## 使用场景

- **高性能视频录制与串流**：当你需要在运行大型 3D 游戏或应用的同时，以高分辨率、高帧率录制视频或进行直播时，使用 NVENC 硬件编码可以避免游戏卡顿。
- **视频编辑与后期处理**：在应用内进行视频剪辑、预览或合成时，利用 NVDEC 硬件解码可以流畅地播放高码率、高分辨率的素材（如 4K、8K 视频）。
- **VR 应用与全景视频播放**：VR 应用对帧率和延迟极其敏感，使用 NVIDIA 硬件编解码可以保证稳定的性能，避免因软件编解码导致的性能瓶颈和晕动症。
- **云游戏与远程渲染**：在服务器端渲染并编码视频流，然后通过网络传输给客户端解码播放的场景中，NVENC 和 NVDEC 是关键组件。

## 蓝图用法

NVCodecs 插件主要提供底层的 CUDA 资源管理能力，其核心类（如 `FVideoContextCUDA`, `FVideoResourceCUDA`）主要在 C++ 层面使用。在蓝图层面，该插件通常不直接暴露节点，而是通过上层的 `AVCodecs` 或其他封装了硬件编解码功能的插件/模块来间接使用。以下列出与 CUDA 资源交互的核心类，这些是 C++ 使用的基石。

### 核心类

| 类/结构 | 说明 | 头文件 |
|---|---|---|
| `FCUDAContextScope` | RAII 风格的 CUDA 上下文管理，在构造时压入上下文，在析构时弹出。用于安全地操作 CUDA API。 | `VideoResourceCUDA.h` |
| `FVideoContextCUDA` | 表示一个 CUDA 上下文 (`CUcontext`) 的封装，继承自 `FAVContext`，是 CUDA 设备资源的“逻辑设备”代表。 | `VideoResourceCUDA.h` |
| `FVideoResourceCUDA` | 表示一个驻留在 CUDA 设备上的视频资源（如纹理、缓冲区）。提供创建、验证、读写和复制数据的功能。支持从 D3D11、D3D12、Vulkan 资源转换而来。 | `VideoResourceCUDA.h` |

## C++ 用法

本插件的核心是提供 CUDA 设备的视频资源抽象，用于与 NVENC/NVDEC 的输入输出对接。使用前，需要确保目标平台安装了合适的 NVIDIA 驱动。

### 头文件引入

```cpp
#include “VideoResourceCUDA.h”
// 来自 NVCodecs 模块
```

### 基本用法

**创建 CUDA 资源并操作**
以下示例展示了如何创建一个 `FVideoContextCUDA` 和 `FVideoResourceCUDA`，并进行基本的拷贝操作。
（来源：`Public/Video/Resources/VideoResourceCUDA.h` 及典型使用模式）

```cpp
// 假设已有一个有效的 CUDA 上下文 (例如从某个 CUDA 设备获取)
CUcontext MyCUDAContext = ...;

// 1. 使用 RAII 管理上下文
{
    FCUDAContextScope ContextScope(MyCUDAContext);
    // 在这个作用域内，所有 CUDA API 调用都会使用 MyCUDAContext

    // 2. 创建视频资源 (以从一个设备指针拷贝数据为例)
    //    需要先有设备引用、布局、描述符等信息
    TSharedRef<FAVDevice> Device = ...; // 获取或创建设备
    FAVLayout Layout = ...;             // 资源布局信息
    FVideoDescriptor Descriptor = ...; // 资源描述 (格式、尺寸)

    // 假设我们有一个指向源数据的 CUdeviceptr
    CUdeviceptr SourceDevicePtr = ...;
    uint32 SourcePitch = ...; // 源数据的行跨度 (字节)

    // 创建一个空的 CUDA 数组资源 (Raw 为 nullptr)
    TSharedPtr<FVideoResourceCUDA> CUDAResource = MakeShared<FVideoResourceCUDA>(Device, nullptr, Layout, Descriptor);

    // 3. 验证资源有效性
    FAVResult ValidateResult = CUDAResource->Validate();
    if (ValidateResult.IsNotSuccess())
    {
        // 处理错误
    }

    // 4. 从设备指针异步拷贝数据到 CUDA 资源
    FAVResult CopyResult = CUDAResource->CopyFromAsync(SourceDevicePtr, SourcePitch);
}
```

### 进阶用法

**管理外部资源与跨 API 转换**
NVCodecs 支持将其他图形 API（如 D3D12, Vulkan）的资源转换为 CUDA 资源，这对于实现零拷贝或低拷贝的编解码流水线至关重要。
（来源：`Public/Video/Resources/VideoResourceCUDA.h` 中的 `TransformResource` 模板特化）

```cpp
#if PLATFORM_WINDOWS
// 假设我们有一个 D3D12 的视频资源指针
TSharedPtr<FVideoResourceD3D12> D3D12Resource = ...; // 例如从纹理或缓冲区获取

// 创建用于接收转换结果的 CUDA 资源指针
TSharedPtr<FVideoResourceCUDA> CUDAResourceFromD3D12;

// 执行从 D3D12 到 CUDA 的资源转换
FAVResult TransformResult = FAVExtension::TransformResource<FVideoResourceCUDA, FVideoResourceD3D12>(
    CUDAResourceFromD3D12,
    D3D12Resource
);

if (TransformResult.IsSuccess())
{
    // 现在可以使用 CUDAResourceFromD3D12 进行 NVENC/NVDEC 操作
    // 该资源底层可能直接引用了 D3D12 的显存，实现了高效共享。
}
#endif

// 同样支持从 Vulkan 转换
TSharedPtr<FVideoResourceVulkan> VulkanResource = ...;
TSharedPtr<FVideoResourceCUDA> CUDAResourceFromVulkan;
TransformResult = FAVExtension::TransformResource<FVideoResourceCUDA, FVideoResourceVulkan>(
    CUDAResourceFromVulkan,
    VulkanResource
);
```

## Demo 示例

一个最小示例，展示如何创建一个用于编码的 CUDA 视频资源。
（注意：此示例省略了 CUDA 上下文、AVDevice 和描述符的创建，聚焦于 NVCodecs 资源层的使用。）

```cpp
// NVCodecsDemo.h
#pragma once
#include “VideoResourceCUDA.h”

class FNvCodecsDemo
{
public:
    // 演示创建一个 YUV420 格式的 CUDA 资源，用于后续编码
    static TSharedPtr<FVideoResourceCUDA> CreateEncodingResource(
        TSharedRef<FAVDevice> InDevice,
        uint32 Width, uint32 Height);
};

// NVCodecsDemo.cpp
#include “NVCodecsDemo.h”
#include “AVDevice.h” // 来自 AVCodecs 核心

TSharedPtr<FVideoResourceCUDA> FNvCodecsDemo::CreateEncodingResource(
    TSharedRef<FAVDevice> InDevice,
    uint32 Width, uint32 Height)
{
    // 1. 定义资源描述 (例如 NV12 格式，常用于视频编码)
    FVideoDescriptor Descriptor;
    Descriptor.Format = EVideoFormat::NV12;
    Descriptor.Width = Width;
    Descriptor.Height = Height;

    // 2. 定义布局 (简化，实际需计算偏移和步长)
    FAVLayout Layout;
    Layout.Stride = Width; // NV12 中 Y 平面行跨度通常等于宽度
    Layout.Size = Width * Height * 3 / 2; // NV12 总大小: Y + UV

    // 3. 创建 CUDA 资源 (初始时 Raw 数组为 nullptr，后续可通过其他方式初始化)
    TSharedPtr<FVideoResourceCUDA> Resource = MakeShared<FVideoResourceCUDA>(
        InDevice,
        nullptr, // Raw CUDA Array
        Layout,
        Descriptor
    );

    // 4. 验证
    if (Resource->Validate().IsNotSuccess())
    {
        return nullptr;
    }

    return Resource;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Vulkan` | 用于与 Vulkan 图形 API 进行资源互操作（TransformResource）。 |
| `AVCodecs` | 本插件的基础，提供 `FAVContext`, `TVideoResource`, `FAVExtension` 等核心基类和框架。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `408f8cf3` | [NvEnc] Add: Launch arg and config option to revert to legacy D3D12 -> CUDA -> NvEnc code path to wo | 为 NvEnc 添加了启动参数和配置选项，可回退到旧版 D3D12->CUDA->NvEnc 编码路径。 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复了作用域枚举在格式化函数中使用可能导致输出乱码的问题。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复了错误的查找替换后的第二次尝试。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回滚了提交 CL51314860 的更改。 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 将引擎初始化委托从静态变量访问改为函数访问，以修复可能的初始化时序问题。 |

### 维护评价

NVCodecs 是一个相对年轻的实验性插件（约 3 年）。最近的提交记录（截至 2026 年 5 月）显示它仍在进行**积极的维护和功能迭代**。近期工作主要集中在：
1.  **功能增强**：增加了对特定编码路径的回退控制，说明在解决特定硬件或驱动下的兼容性问题。
2.  **稳定性修复**：修复了枚举格式化和引擎初始化相关的 bug，提升了插件的稳定性。

由于它仍处于 **“Experimental”** 状态且默认禁用，意味着其 API 和行为在后续版本中可能会发生变化，不建议在追求稳定性的商业项目中未经充分测试就直接依赖。但对于研究硬件加速编解码、或在对性能有极致要求且能接受一定维护成本的项目（如自研串流解决方案、专业视频工具）中，它是一个重要且活跃的底层组件。推荐在可控环境下使用和贡献。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AVCodecs/NVCodecs)
- 官方文档 (无)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AVCodecs/NVCodecs/Tests) (如果存在)