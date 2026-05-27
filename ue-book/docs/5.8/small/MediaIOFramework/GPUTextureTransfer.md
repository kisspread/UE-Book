# Media IO Framework

> Media Framework classes to support Professional Media IO used by the Virtual Production industry.

| 属性 | 值 |
|---|---|
| 中文名 | 媒体IO框架 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MediaIOCore` (Runtime), `MediaIOEditor` (Editor), `GPUTextureTransfer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-10-02 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaIOFramework) | |

## 用途

MediaIOFramework 是虚拟制作行业的核心媒体处理框架，主要解决**专业级视频设备与UE引擎之间的低延迟、高带宽数据传输问题**。

**核心解决的问题：**
1.  **专业视频设备集成**：为AJA、Blackmagic等专业采集卡提供统一的抽象层，隐藏不同硬件的底层差异。
2.  **高性能GPU数据传输**：通过 `GPUTextureTransfer` 模块利用NVIDIA GPUDirect技术，实现GPU显存与CPU系统内存之间的零拷贝或低延迟数据传输，避免通过CPU中转，极大提升实时性能。
3.  **色彩管理与配置**：与OpenColorIO插件集成，为虚拟制作流程提供准确的色彩转换和管理。
4.  **虚拟制作工作流支持**：提供包括采集、播放、配置、同步在内的全套媒体IO功能，是构建虚拟摄像机、LED墙渲染等高级虚拟制作功能的基石。

它存在于UE中，是为了将UE打造成一个可靠、高性能的虚拟制作引擎，满足电影、广告和广播行业对实时合成和回放的需求。

## 使用场景

- **LED墙虚拟制作**：需要将引擎渲染的实时画面以极低延迟发送到LED墙显示，同时可能需要从外部摄像机采集画面用于参考或合成。`GPUTextureTransfer` 模块在此场景下至关重要。
- **实时视频合成（Compositing）**：在引擎中渲染CG元素，并与外部摄像机采集的视频源实时合成。
- **多通道视频录制与回放**：将引擎渲染的多个视图（如主视图、HUD、特效层）分别录制为不同的视频流，或回放预先录制好的视频序列。
- **广播与实时图形**：在体育、新闻等直播场景中，使用UE生成实时图形，并无缝集成到传统视频制作流程中。

**你需要使用此插件，如果：**
- 你的项目需要连接AJA或Blackmagic等专业视频采集卡。
- 你需要实现超低延迟的视频输入/输出（例如用于虚拟制作）。
- 你正在构建虚拟摄像机系统或LED墙解决方案。

## 蓝图用法

MediaIOFramework主要提供底层的C++ API。其公开的蓝图功能通常通过更高级别的插件（如NDisplay、MediaFrameworkUtilities）或C++类暴露，核心的 `ITextureTransfer` 接口为纯C++设计。

### 核心概念

虽然没有直接的蓝图节点，但理解以下概念对配置至关重要：
1.  **媒体配置（Media Profile）**：在项目设置或编辑器中配置输入/输出设备、格式、分辨率等。
2.  **GPU直接传输（GPUDirect）**：通过 `MediaIO.EnableGPUDirect` 控制台变量启用，以利用GPU显存与CPU内存的零拷贝传输。
3.  **纹理传输对象**：通过 `FGPUTextureTransferModule` 获取，用于管理具体的传输任务。

## C++ 用法

### 头文件引入

使用 `GPUTextureTransfer` 模块：
```cpp
#include "GPUTextureTransfer.h"
#include "GPUTextureTransferModule.h"
```

### 基本用法

获取GPU纹理传输模块并检查是否可用。

```cpp
// 检查GPUDirect是否启用
static IAutoConsoleVariableRef CVarMediaIOEnableGPUDirect = IConsoleManager::Get().RegisterConsoleVariableRef(
    TEXT("MediaIO.EnableGPUDirect"),
    FIntRef(/* 默认值 */ 0),
    TEXT("Enable/Disable GPUDirect for Media IO. 1 to enable."),
    ECVF_ReadOnly);

// 获取模块并初始化
FGPUTextureTransferModule& GPUTextureTransferModule = FGPUTextureTransferModule::Get();

// 检查模块是否已初始化（DVP库是否加载）
if (!GPUTextureTransferModule.IsInitialized())
{
    // 手动初始化（阻塞调用，可能需要2秒）
    GPUTextureTransferModule.Initialize();
}

// 获取一个纹理传输对象
UE::GPUTextureTransfer::TextureTransferPtr TextureTransfer = GPUTextureTransferModule.GetTextureTransfer();
if (TextureTransfer.IsValid() && TextureTransfer->Initialize())
{
    // 使用纹理传输对象进行后续操作
}
```
*来源：基于 `Public/GPUTextureTransferModule.h` 和 `Public/GPUTextureTransfer.h` 推断的用法。*

### 进阶用法：执行纹理传输

以下是一个使用 `ITextureTransfer` 接口进行CPU到GPU传输的简化流程。

```cpp
// 1. 准备参数
UE::GPUTextureTransfer::FRegisterDMABufferArgs BufferArgs;
BufferArgs.Buffer = MyCPUMemoryBuffer; // 指向CPU内存中准备好的图像数据
BufferArgs.Width = 1920;
BufferArgs.Height = 1080;
BufferArgs.Stride = 1920 * 4; // 假设是BGRA格式，每像素4字节
BufferArgs.PixelFormat = UE::GPUTextureTransfer::EPixelFormat::PF_8Bit;

UE::GPUTextureTransfer::FRegisterDMATextureArgs TextureArgs;
TextureArgs.RHITexture = MyRHITexture.GetReference(); // 需要写入的GPU纹理
TextureArgs.Width = 1920;
TextureArgs.Height = 1080;
TextureArgs.PixelFormat = UE::GPUTextureTransfer::EPixelFormat::PF_8Bit;
TextureArgs.Stride = 1920 * 4;

// 2. 注册资源
TextureTransfer->RegisterBuffer(BufferArgs);
TextureTransfer->RegisterTexture(TextureArgs);

// 3. 执行传输
bool bSuccess = TextureTransfer->TransferTexture(
    BufferArgs.Buffer,
    TextureArgs.RHITexture,
    UE::GPUTextureTransfer::ETransferDirection::CPU_TO_GPU
);

if (bSuccess)
{
    // 4. 同步以确保GPU已使用完缓冲区
    TextureTransfer->BeginSync(BufferArgs.Buffer, UE::GPUTextureTransfer::ETransferDirection::CPU_TO_GPU);
    
    // ... 在此处可以安全地再次修改 MyCPUMemoryBuffer 的内容 ...
    
    TextureTransfer->EndSync(BufferArgs.Buffer);
}

// 5. 清理（在不再需要时）
TextureTransfer->UnregisterTexture(TextureArgs.RHITexture);
TextureTransfer->UnregisterBuffer(BufferArgs.Buffer);
TextureTransfer->Uninitialize();
```
*来源：基于 `Public/GPUTextureTransfer.h` 中 `ITextureTransfer` 接口的注释和方法签名推断。*

## Demo 示例

一个最小的、可运行的C++示例，演示如何初始化GPUDirect并执行一次CPU到GPU的纹理传输。

**示例头文件 (MyGPUDirectDemo.h):**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "GPUTextureTransfer.h"
#include "MyGPUDirectDemo.generated.h"

UCLASS()
class AMyGPUDirectDemo : public AActor
{
    GENERATED_BODY()

public:
    AMyGPUDirectDemo();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    void RunTransferDemo();

    // 存储传输对象
    UE::GPUTextureTransfer::TextureTransferPtr TextureTransfer;

    // 模拟的CPU内存缓冲区
    TArray<uint8> CPUBuffer;

    // 需要被写入的GPU纹理（需要在蓝图或构造函数中设置）
    UPROPERTY(EditAnywhere)
    UTexture2D* TargetTexture;
};
```

**示例源文件 (MyGPUDirectDemo.cpp):**
```cpp
#include "MyGPUDirectDemo.h"
#include "GPUTextureTransferModule.h"

AMyGPUDirectDemo::AMyGPUDirectDemo()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyGPUDirectDemo::BeginPlay()
{
    Super::BeginPlay();

    // 初始化传输模块（如果尚未初始化）
    FGPUTextureTransferModule::Get().Initialize();
    TextureTransfer = FGPUTextureTransferModule::Get().GetTextureTransfer();

    if (TextureTransfer.IsValid() && TextureTransfer->Initialize())
    {
        RunTransferDemo();
    }
}

void AMyGPUDirectDemo::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (TextureTransfer.IsValid())
    {
        TextureTransfer->Uninitialize();
        TextureTransfer.Reset();
    }
    Super::EndPlay(EndPlayReason);
}

void AMyGPUDirectDemo::RunTransferDemo()
{
    if (!TargetTexture || !TargetTexture->GetResource()) return;

    const uint32 Width = 256;
    const uint32 Height = 256;
    const uint32 Stride = Width * 4; // BGRA8

    // 1. 准备一些测试数据到CPU内存
    CPUBuffer.SetNumZeroed(Height * Stride);
    FMemory::Memset(CPUBuffer.GetData(), 0xFF, CPUBuffer.Num()); // 填充白色

    // 2. 获取纹理的RHI资源
    FTexture2DRHIRef TextureRHI = TargetTexture->GetResource()->GetTexture2DRHI();

    // 3. 配置注册参数
    UE::GPUTextureTransfer::FRegisterDMABufferArgs BufferArgs;
    BufferArgs.Buffer = CPUBuffer.GetData();
    BufferArgs.Width = Width;
    BufferArgs.Height = Height;
    BufferArgs.Stride = Stride;
    BufferArgs.PixelFormat = UE::GPUTextureTransfer::EPixelFormat::PF_8Bit;

    UE::GPUTextureTransfer::FRegisterDMATextureArgs TextureArgs;
    TextureArgs.RHITexture = TextureRHI;
    TextureArgs.Width = Width;
    TextureArgs.Height = Height;
    TextureArgs.Stride = Stride;
    TextureArgs.PixelFormat = UE::GPUTextureTransfer::EPixelFormat::PF_8Bit;

    // 4. 注册
    TextureTransfer->RegisterBuffer(BufferArgs);
    TextureTransfer->RegisterTexture(TextureArgs);

    // 5. 传输
    bool bTransferOK = TextureTransfer->TransferTexture(
        BufferArgs.Buffer,
        TextureArgs.RHITexture,
        UE::GPUTextureTransfer::ETransferDirection::CPU_TO_GPU
    );

    UE_LOG(LogTemp, Log, TEXT("GPU Texture Transfer %s."), bTransferOK ? TEXT("Succeeded") : TEXT("Failed"));

    // 6. 同步并清理
    if (bTransferOK)
    {
        TextureTransfer->BeginSync(BufferArgs.Buffer, UE::GPUTextureTransfer::ETransferDirection::CPU_TO_GPU);
        TextureTransfer->EndSync(BufferArgs.Buffer);
    }

    TextureTransfer->UnregisterTexture(TextureArgs.RHITexture);
    TextureTransfer->UnregisterBuffer(BufferArgs.Buffer);
}
```

## 模块依赖

要使用此插件中的功能，你的项目模块通常需要依赖一个更高级的包装插件（如 `MediaFrameworkUtilities`）。如果直接使用 `GPUTextureTransfer` 模块，请确保：

| 模块 | 用途 |
|---|---|
| `GPUTextureTransfer` | 提供GPUDirect纹理传输功能。 |
| `MediaIOCore` | 媒体IO框架的核心逻辑，通常通过 `MediaFrameworkUtilities` 插件间接使用。 |
| `OpenColorIO` | 插件显式依赖此插件，用于专业色彩管理。 |
| `VulkanRHI` | `GPUTextureTransfer` 模块在Vulkan RHI下的依赖。 |

**注意**：`MediaIOEditor` 模块仅在编辑器环境下可用，用于提供编辑器工具和UI。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `36c08694` | Media IO - Populate Media Configuration when using auto for Blackmagic and Aja cards | 优化了Blackmagic和Aja采集卡使用“自动”配置时的媒体配置填充逻辑。 |
| 2026-05-23 | `42746f7a` | Media IO: Added additional engine analytics information to various media players and capture and pro | 为多种媒体播放器、采集和处理模块添加了额外的引擎分析数据收集功能。 |
| 2026-05-14 | `a43a62b2` | Media Profile: Changed media texture capture behavior to always preserve aspect ratio of texture eve | 修改了媒体纹理捕获行为，使其始终保留纹理的宽高比。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下将双精度常量转换为浮点数会产生警告的代码。 |
| 2026-05-12 | `a879de69` | Fix clang warnings when compiling MediaIODeinterlacerTests | 修复了编译MediaIODeinterlacerTests时产生的clang警告。 |

### 维护评价

- **创建时间**：2018年创建，已有7年历史。
- **维护状态**：**活跃维护**。从近期提交记录看，直到2026年5月仍有持续的功能增强、bug修复和代码质量改进。
- **稳定性**：作为虚拟制作的核心组件，经过大量专业项目验证，相对稳定。
- **推荐程度**：**强烈推荐用于专业虚拟制作项目**。它是连接UE引擎与专业视频硬件的桥梁。对于非虚拟制作的常规游戏开发项目，通常不需要启用此插件。

**警告**：该插件默认禁用 (`EnabledByDefault: false`)，需要在项目设置中手动启用。它依赖于特定的硬件（专业采集卡）和驱动（NVIDIA GPUDirect）才能发挥全部功能。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaIOFramework)
- 官方文档链接未在 .uplugin 中提供，可参考 [UE官方文档中的虚拟制作部分](https://docs.unrealengine.com/5.0/en-US/virtual-production-in-unreal-engine/)。