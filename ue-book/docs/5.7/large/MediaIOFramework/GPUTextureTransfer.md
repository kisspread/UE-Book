# Media IO Framework

> Media Framework classes to support Professional Media IO used by the Virtual Production industry.

| 属性 | 值 |
|---|---|
| 中文名 | 媒体 IO 框架 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MediaIOCore` (Runtime), `MediaIOEditor` (Editor), `GPUTextureTransfer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-10-03 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/MediaIOFramework) | |

## 用途

Media IO Framework 为虚幻引擎提供了与专业媒体硬件（如 AJA、Blackmagic DeckLink、NDI、Bluefish444 等）交互的底层框架。该插件封装了从视频采集卡获取视频帧、音频同步、时间码同步等功能，并支持将引擎渲染输出发送到外部设备。

核心模块 `MediaIOCore` 定义了平台无关的媒体 IO 接口和数据结构，`MediaIOEditor` 提供了编辑器中的媒体配置 UI，而 `GPUTextureTransfer` 模块则利用 NVIDIA 的 DVP（Direct Video Programming）技术实现 GPU 直接内存访问，**大幅降低视频帧在 CPU 和 GPU 之间传输的延迟和 CPU 占用**，这对于需要低延迟视频处理的虚拟制片工作流至关重要。

## 使用场景

- **虚拟制片（Virtual Production）**：在 LED 舞台或绿幕棚中，将实拍相机信号实时合成到虚拟场景中，需要极低延迟的视频回传。
- **广播级直播**：将 UE 渲染画面输出到 SDI 或 NDI 设备，用于演播室播出。
- **实时视频特效/处理**：对来自外部硬件的视频流进行实时调整（调色、遮罩等）后再输出。
- **多机位同步录制**：同时从多张采集卡获取视频流并同步时间码。

## 蓝图用法

该插件主要面向 C++ 开发，公共蓝图可调用接口**有限**。`MediaIOCore` 可能提供少数蓝图节点（如媒体源选择），但由于核心数据传输和初始化需通过 C++ 完成，故不建议仅靠蓝图实现完整的媒体 IO 功能。

> 注：`GPUTextureTransfer` 模块的所有接口均为纯 C++ 虚函数，未暴露至蓝图。

## C++ 用法

以下示例基于 `GPUTextureTransfer` 模块，展示如何初始化并使用 GPU 直接传输。

### 头文件引入

```cpp
#include "GPUTextureTransfer.h"
#include "GPUTextureTransferModule.h"
```

### 基本用法

#### 1. 初始化模块并获取传输对象

```cpp
// 获取模块实例
FGPUTextureTransferModule& Module = FGPUTextureTransferModule::Get();
Module.Initialize();  // 加载 DVP 库（阻塞，约 2 秒）

// 检查是否可用
if (Module.IsInitialized() && Module.IsEnabled())
{
    TSharedPtr<UE::GPUTextureTransfer::ITextureTransfer> Transfer = Module.GetTextureTransfer();
}
```

#### 2. 注册系统和 GPU 资源

```cpp
// 准备 DMA 参数
UE::GPUTextureTransfer::FInitializeDMAArgs InitArgs;
InitArgs.RHI = UE::GPUTextureTransfer::ERHI::Vulkan; // 根据实际 RHI 设置
// 填充 RHI 设备指针等（从 FRHICommandListImmediate 等获取）

Transfer->Initialize(InitArgs);

// 注册系统内存缓冲区（例如从采集卡拿到的一帧数据）
UE::GPUTextureTransfer::FRegisterDMABufferArgs BufferArgs;
BufferArgs.Buffer = SystemMemoryPointer;
BufferArgs.Width = 1920;
BufferArgs.Height = 1080;
BufferArgs.Stride = 1920 * 4; // 32bpp
BufferArgs.PixelFormat = UE::GPUTextureTransfer::EPixelFormat::PF_8Bit;
Transfer->RegisterBuffer(BufferArgs);

// 注册 GPU 纹理（FRHITexture*）
UE::GPUTextureTransfer::FRegisterDMATextureArgs TexArgs;
TexArgs.RHITexture = MyRHITexture;
TexArgs.Width = 1920;
TexArgs.Height = 1080;
TexArgs.Stride = 1920 * 4;
Transfer->RegisterTexture(TexArgs);
```

#### 3. 执行传输

```cpp
// 线程准备（必须在调用 TransferTexture 的线程上调用）
Transfer->ThreadPrep();

// 开始同步（等待缓冲区就绪）
Transfer->BeginSync(SystemBuffer, UE::GPUTextureTransfer::ETransferDirection::CPU_TO_GPU);

// 执行 DMA 传输：将系统内存中的帧数据传输到 GPU 纹理
Transfer->TransferTexture(SystemBuffer, MyRHITexture, UE::GPUTextureTransfer::ETransferDirection::CPU_TO_GPU);

// 结束同步
Transfer->EndSync(SystemBuffer);

// 可选：等待 GPU 完成（实验性）
Transfer->WaitForGPU(MyRHITexture);

// 线程清理
Transfer->ThreadCleanup();
```

#### 4. 释放资源

```cpp
Transfer->UnregisterBuffer(SystemBuffer);
Transfer->UnregisterTexture(MyRHITexture);
Transfer->Uninitialize();
```

**来源文件**：`Engine/Plugins/Media/MediaIOFramework/Source/GPUTextureTransfer/Public/GPUTextureTransfer.h`

### 进阶用法

- 多线程安全：`ThreadPrep()` 与 `ThreadCleanup()` 需在**同一线程**配对调用，该线程专用于传输操作。
- 锁定纹理：通过 `LockTexture` / `UnlockTexture` 阻止或允许 DVP 库访问纹理，避免与 RHI 渲染冲突。
- 不同 RHI 支持：目前支持 D3D11、D3D12 和 Vulkan，初始化时需正确设置 `ERHI` 和对应设备指针。

## Demo 示例

一个完整的最小示例，演示如何在游戏线程（或渲染线程）中利用 GPUTextureTransfer 从系统内存向 GPU 纹理传输一帧。

### MyMediaTransfer.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GPUTextureTransfer.h"
#include "GPUTextureTransferModule.h"

class FMyMediaTransfer
{
public:
    void Init();
    void TransferFrame(void* SystemBuffer, uint32 Width, uint32 Height, uint32 Stride);
    void Shutdown();

private:
    TSharedPtr<UE::GPUTextureTransfer::ITextureTransfer> Transfer;
    void* RegisteredBuffer = nullptr;
    FRHITexture* TargetTexture = nullptr;
};
```

### MyMediaTransfer.cpp

```cpp
#include "MyMediaTransfer.h"
#include "RenderingThread.h"

void FMyMediaTransfer::Init()
{
    FGPUTextureTransferModule& Module = FGPUTextureTransferModule::Get();
    Module.Initialize();
    if (!Module.IsInitialized() || !Module.IsEnabled())
    {
        UE_LOG(LogTemp, Error, TEXT("GPUTextureTransfer not available"));
        return;
    }
    Transfer = Module.GetTextureTransfer();

    // 初始化 DVP
    UE::GPUTextureTransfer::FInitializeDMAArgs Args;
    // 从引擎获取 RHI 信息（简化示例，实际需从 FGenericPlatformMisc 获取）
    Args.RHI = UE::GPUTextureTransfer::ERHI::Vulkan;
    // ... 填充 Args.RHIDevice, Args.VulkanInstance 等
    Transfer->Initialize(Args);

    // 创建目标纹理（假设已存在）
    // TargetTexture = ...;
}

void FMyMediaTransfer::TransferFrame(void* SystemBuffer, uint32 Width, uint32 Height, uint32 Stride)
{
    if (!Transfer) return;

    // 注册缓冲区（首次调用后注册）
    if (!RegisteredBuffer)
    {
        UE::GPUTextureTransfer::FRegisterDMABufferArgs BufArgs;
        BufArgs.Buffer = SystemBuffer;
        BufArgs.Width = Width;
        BufArgs.Height = Height;
        BufArgs.Stride = Stride;
        Transfer->RegisterBuffer(BufArgs);
        RegisteredBuffer = SystemBuffer;
    }
    // 注册纹理（首次调用）
    if (!TargetTexture)
    {
        UE::GPUTextureTransfer::FRegisterDMATextureArgs TexArgs;
        TexArgs.RHITexture = /* 已有纹理指针 */;
        TexArgs.Width = Width;
        TexArgs.Height = Height;
        TexArgs.Stride = Stride;
        Transfer->RegisterTexture(TexArgs);
        TargetTexture = TexArgs.RHITexture;
    }

    // 注意：ThreadPrep/ThreadCleanup 需在调用线程配对使用
    Transfer->ThreadPrep();
    Transfer->BeginSync(SystemBuffer, UE::GPUTextureTransfer::ETransferDirection::CPU_TO_GPU);
    bool bSuccess = Transfer->TransferTexture(SystemBuffer, TargetTexture, UE::GPUTextureTransfer::ETransferDirection::CPU_TO_GPU);
    Transfer->EndSync(SystemBuffer);
    Transfer->ThreadCleanup();
}

void FMyMediaTransfer::Shutdown()
{
    if (Transfer)
    {
        if (RegisteredBuffer) Transfer->UnregisterBuffer(RegisteredBuffer);
        if (TargetTexture) Transfer->UnregisterTexture(TargetTexture);
        Transfer->Uninitialize();
        Transfer.Reset();
    }
}
```

## 模块依赖

使用此插件时，你的模块需在 `Build.cs` 中添加以下依赖（除标准 Core/Engine/Slate 外）：

| 模块 | 用途 |
|---|---|
| `OpenColorIO` | 颜色管理支持（插件自身依赖，使用者通常无需额外添加） |

> **注意**：`GPUTextureTransfer` 内部依赖 `VulkanRHI` 等，但这些是插件内部依赖，使用者只需依赖 `MediaIOFramework` 即可。

如果你只使用 `MediaIOCore` 和 `MediaIOEditor`，一般无需额外依赖。若使用 `GPUTextureTransfer`，推荐在项目中启用 `MediaIOFramework` 插件（通过 `Edit > Plugins > Media > Media IO Framework`）。

## 维护状态

### 近期更新

- 2026-01-23 `4c7dda9d` Media IO - Fix Media Capture taking multiple frames to start outputting
- 2025-12-18 `38c0295d` Media IO - When using ResizeInRenderPass, fix output getting resized even if the input resolution matches
- 2025-10-17 `ab15e769` Media IO - Fix crash when refreshing media properties for Aja source
- 2025-10-06 `cefac266` Media I/O: Avoid raw this pointer capture in async task, which could cause crashes if the texture is deleted...
- 2025-10-03 `1b95a6c6` Media IO - Fix Media Source not being able to unset AutoDetect in Media Profile

### 维护评价

- 创建时间约 2025-10，属于较新的插件。
- 最近 3 个月内有多次 bug 修复和稳定性改进，维护**活跃**。
- 插件持续跟随 Unreal Engine 版本迭代，工程师团队正在积极修复崩溃和性能问题。
- 已知问题：`WaitForGPU` 标记为实验性；部分 RHI（如 D3D11）的 `MapBufferWaitAPI_Impl` 与 `MapBufferEndAPI_Impl` 未完全实现（返回 `DVP_STATUS_UNSUPPORTED`）。
- **推荐使用**：适合对低延迟、高效率视频传输有需求的虚拟制片和广播项目。由于默认未启用，需手动在 Project Settings 中开启 `Media IO Framework` 插件的 `Enable GPUDirect` 选项（`MediaIO.EnableGPUDirect` CVar）。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/MediaIOFramework)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/MediaIOFramework/Source/GPUTextureTransfer/Tests)（若有）
- 官方文档：暂无独立文档页，可参考 [Virtual Production 文档](https://docs.unrealengine.com/5.7/en-US/virtual-production-and-live-events-in-unreal-engine/) 中关于 Media Output 的章节。