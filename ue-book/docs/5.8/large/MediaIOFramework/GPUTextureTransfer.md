# Media IO Framework

> Media Framework classes to support Professional Media IO used by the Virtual Production industry.

| 属性 | 值 |
|---|---|
| 中文名 | 专业媒体IO框架 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MediaIOCore` (Runtime), `MediaIOEditor` (Editor), `GPUTextureTransfer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-10-02 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaIOFramework) | |

## 用途

MediaIOFramework 是虚幻引擎中**专业级媒体输入/输出**的核心基础设施，专门为**虚拟制作（Virtual Production）**行业设计。它解决的核心问题是：如何在 GPU 与外部专业视频设备（如 AJA、Blackmagic 采集卡）之间实现**零拷贝、低延迟**的纹理数据传输。

该插件包含三个子模块，各司其职：

- **MediaIOCore**：运行时核心，提供媒体输入/输出的基础类和接口，供其他专业媒体插件（如 AJAMediaIO、BlackmagicMediaIO）继承和实现。它定义了媒体采集卡的通用抽象层，包括设备枚举、视频格式协商、时间码同步等。
- **MediaIOEditor**：编辑器扩展，为虚拟制作工作流提供编辑器内的媒体配置 UI、节点图（如 Composure 合成节点）中的媒体输入/输出节点。
- **GPUTextureTransfer**：基于 NVIDIA GPUDirect Video (DVP) 技术，实现 CPU 端 DMA 缓冲区与 GPU 纹理之间的**零拷贝传输**。这是 LED 虚拟墙（LED Volume）、实时合成、数字人等高帧率场景的关键性能保障。

插件的 `EnabledByDefault = false`，因为这是一个面向专业用户的高级功能，普通项目无需启用。使用时需要手动在插件设置中启用，且依赖 OpenColorIO 插件提供色彩管理支持。

## 使用场景

- 你在做**虚拟制作（LED Volume）** → 用 MediaIOCore + GPUTextureTransfer 驱动 LED 墙的实时画面输出
- 你需要从**专业采集卡（AJA/Blackmagic）**接收视频信号 → MediaIOCore 提供设备抽象层
- 你需要将游戏引擎的渲染画面以**超低延迟**发送给采集卡 → GPUTextureTransfer 实现 GPU→设备的零拷贝传输
- 你在做**实时合成（Composure）** → MediaIOEditor 提供编辑器内的媒体输入节点
- 你需要将外部摄像机画面**实时映射到虚拟场景** → 组合使用 MediaIOCore（采集）+ GPUTextureTransfer（传输）+ OpenColorIO（色彩管理）
- 你在开发**自定义媒体输入/输出设备插件** → 继承 MediaIOCore 的接口类

## 蓝图用法

本插件的核心功能主要通过 C++ 接口暴露。MediaIOCore 模块中定义了媒体配置相关的蓝图可读写属性，但 GPUTextureTransfer 模块是纯 C++ 接口，不直接暴露蓝图节点。

媒体设备的蓝图配置通常通过 MediaIOEditor 提供的编辑器 UI（如 Project Settings 中的 Media Configuration 面板）完成，而非蓝图节点。

## C++ 用法

### 头文件引入

```cpp
// GPUTextureTransfer 模块
#include "GPUTextureTransfer.h"

// MediaIOCore 模块（如有需要）
#include "MediaIOCoreModule.h"
```

### 基本用法：注册缓冲区与纹理传输

以下代码展示了使用 GPUTextureTransfer 进行零拷贝纹理传输的基本流程，来源于 `ITextureTransfer` 接口注释和 `FTextureTransferBase` 实现。

```cpp
#include "GPUTextureTransfer.h"

using namespace UE::GPUTextureTransfer;

// 1. 获取 TextureTransfer 模块实例
FGPUTextureTransferModule& Module = FGPUTextureTransferModule::Get();

// 2. 初始化（加载 DVP 库，耗时可达 2 秒）
Module.Initialize();

// 3. 获取纹理传输对象
TextureTransferPtr Transfer = Module.GetTextureTransfer();
if (!Transfer.IsValid())
{
    return;
}

// 4. 注册 CPU 端 DMA 缓冲区
FRegisterDMABufferArgs BufferArgs;
BufferArgs.Buffer    = MyCPUBuffer;       // 已分配的 CPU 内存
BufferArgs.Width     = 1920;
BufferArgs.Height    = 1080;
BufferArgs.Stride    = 1920 * 4;          // RGBA: 每像素 4 字节
BufferArgs.PixelFormat = EPixelFormat::PF_8Bit;
Transfer->RegisterBuffer(BufferArgs);

// 5. 注册 GPU 纹理
FRegisterDMATextureArgs TextureArgs;
TextureArgs.RHITexture       = MyRHITexture;
TextureArgs.RHIResourceMemory = nullptr;   // Vulkan 时需要填
TextureArgs.Width             = 1920;
TextureArgs.Height            = 1080;
TextureArgs.Stride            = 1920 * 4;
TextureArgs.PixelFormat       = EPixelFormat::PF_8Bit;
Transfer->RegisterTexture(TextureArgs);

// 6. 执行传输（GPU_TO_CPU：从 GPU 读回；CPU_TO_GPU：写入 GPU）
Transfer->TransferTexture(MyCPUBuffer, MyRHITexture, ETransferDirection::CPU_TO_GPU);

// 7. 同步（提交到渲染队列前）
Transfer->BeginSync(MyCPUBuffer, ETransferDirection::CPU_TO_GPU);

// ... 在此处调度渲染帧 ...

// 8. 同步完成
Transfer->EndSync(MyCPUBuffer);

// 9. 清理
Transfer->UnregisterBuffer(MyCPUBuffer);
Transfer->UnregisterTexture(MyRHITexture);
Transfer->Uninitialize();
```

### 进阶用法：多线程传输与纹理锁定

```cpp
#include "GPUTextureTransfer.h"

using namespace UE::GPUTextureTransfer;

// 场景：在采集线程中执行传输，同时确保渲染线程不会并发访问同一纹理

// 锁定纹理，阻止 DVP 库访问（在渲染线程中调用）
Transfer->LockTexture(MyRHITexture);

// 在采集线程中准备并执行传输
// （每个使用 TransferTexture 的线程必须先调用 ThreadPrep）
Transfer->ThreadPrep();

Transfer->TransferTexture(MyCPUBuffer, MyRHITexture, ETransferDirection::GPU_TO_CPU);
Transfer->BeginSync(MyCPUBuffer, ETransferDirection::GPU_TO_CPU);

// ... 处理采集到的帧数据 ...

Transfer->EndSync(MyCPUBuffer);
Transfer->ThreadCleanup();

// 解锁纹理，允许 DVP 库继续访问
Transfer->UnlockTexture(MyRHITexture);
```

### 进阶用法：查询对齐要求

```cpp
// 获取 CPU 缓冲区的推荐对齐（用于 posix_memalign 分配）
uint32 BufferAlignment = Transfer->GetBufferAlignment();

// 获取纹理的推荐 stride（字节对齐）
uint32 TextureStride = Transfer->GetTextureStride();

// 分配对齐的缓冲区
void* AlignedBuffer = nullptr;
posix_memalign(&AlignedBuffer, BufferAlignment, TextureStride * Height);
```

## Demo 示例

以下是一个完整的最小示例，展示如何初始化 GPUTextureTransfer 并执行一次 CPU→GPU 传输：

```cpp
// MyMediaTransfer.h
#pragma once

#include "CoreMinimal.h"
#include "GPUTextureTransfer.h"

class FMyMediaTransfer
{
public:
    void Initialize();
    void TransferFrame(void* CPUBuffer, uint32 Width, uint32 Height, FRHITexture* RHITexture);
    void Shutdown();

private:
    UE::GPUTextureTransfer::TextureTransferPtr Transfer;
};
```

```cpp
// MyMediaTransfer.cpp
#include "MyMediaTransfer.h"
#include "GPUTextureTransferModule.h"

void FMyMediaTransfer::Initialize()
{
    FGPUTextureTransferModule& Module = FGPUTextureTransferModule::Get();

    // 加载并初始化 DVP 库（阻塞调用，约 2 秒）
    Module.Initialize();

    Transfer = Module.GetTextureTransfer();
    if (Transfer.IsValid())
    {
        Transfer->Initialize();
    }
}

void FMyMediaTransfer::TransferFrame(void* CPUBuffer, uint32 Width, uint32 Height, FRHITexture* RHITexture)
{
    if (!Transfer.IsValid())
    {
        return;
    }

    // 注册缓冲区
    UE::GPUTextureTransfer::FRegisterDMABufferArgs BufferArgs;
    BufferArgs.Buffer      = CPUBuffer;
    BufferArgs.Width       = Width;
    BufferArgs.Height      = Height;
    BufferArgs.Stride      = Width * 4;
    BufferArgs.PixelFormat = UE::GPUTextureTransfer::EPixelFormat::PF_8Bit;
    Transfer->RegisterBuffer(BufferArgs);

    // 注册纹理
    UE::GPUTextureTransfer::FRegisterDMATextureArgs TextureArgs;
    TextureArgs.RHITexture = RHITexture;
    TextureArgs.Width      = Width;
    TextureArgs.Height     = Height;
    TextureArgs.Stride     = Width * 4;
    TextureArgs.PixelFormat = UE::GPUTextureTransfer::EPixelFormat::PF_8Bit;
    Transfer->RegisterTexture(TextureArgs);

    // 执行零拷贝传输
    Transfer->TransferTexture(CPUBuffer, RHITexture, UE::GPUTextureTransfer::ETransferDirection::CPU_TO_GPU);
    Transfer->BeginSync(CPUBuffer, UE::GPUTextureTransfer::ETransferDirection::CPU_TO_GPU);
    Transfer->EndSync(CPUBuffer);

    // 清理本次注册
    Transfer->UnregisterBuffer(CPUBuffer);
    Transfer->UnregisterTexture(RHITexture);
}

void FMyMediaTransfer::Shutdown()
{
    if (Transfer.IsValid())
    {
        Transfer->Uninitialize();
        Transfer.Reset();
    }

    FGPUTextureTransferModule::Get().ShutdownModule();
}
```

## 模块依赖

**重要**：此插件默认禁用（`EnabledByDefault = false`），需在项目设置中手动启用。还需启用 **OpenColorIO** 插件作为依赖。

| 模块 | 用途 |
|---|---|
| `VulkanRHI` | GPUTextureTransfer 模块的 Vulkan 图形 API 支持 |
| `LevelEditor` | MediaIOCore 模块的编辑器关卡扩展 |

> 无其他特殊依赖。EditorFramework、UnrealEd 等为编辑器插件通用依赖，已省略。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `36c08694` | Media IO - Populate Media Configuration when using auto for Blackmagic and Aja cards | 自动模式下为 Blackmagic 和 AJA 卡填充媒体配置 |
| 2026-05-23 | `42746f7a` | Media IO: Added additional engine analytics information to various media players and capture and pro | 为媒体播放器和采集卡添加引擎分析数据 |
| 2026-05-14 | `a43a62b2` | Media Profile: Changed media texture capture behavior to always preserve aspect ratio of texture eve | 媒体纹理采集始终保持宽高比不变 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 截断为 float 的编译警告 |
| 2026-05-12 | `a879de69` | Fix clang warnings when compiling MediaIODeinterlacerTests | 修复 MediaIO 去隔行测试的 clang 编译警告 |

### 维护评价

**🟢 活跃维护中。**

- 创建于 2018 年，是虚拟制作管线中成熟且持续维护的核心模块
- 2026 年 5 月仍有功能性更新（自动配置、分析数据、宽高比保持），表明处于**活跃开发**状态
- 作为 Unreal Engine 虚拟制作（Virtual Production）和 nDisplay 管线的关键基础设施，Epic 有持续投入的动力
- `EnabledByDefault = false` 表明这是一个面向专业用户的高级功能，普通项目无需关注
- **推荐使用**：如果你在做 LED 虚拟墙、专业采集卡集成或实时合成等虚拟制作工作流，这是必选基础设施

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaIOFramework)
- [GPUTextureTransfer 模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaIOFramework/Source/GPUTextureTransfer)