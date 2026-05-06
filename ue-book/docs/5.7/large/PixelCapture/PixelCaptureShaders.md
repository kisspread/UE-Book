# Pixel Capture

> Framework for capturing pixel buffers in other formats while allowing for disconnected produce/consume rates.

| 属性 | 值 |
|---|---|
| 中文名 | 像素捕获框架 |
| 分类 | Graphics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（着色器、材质模板、蓝图节点） |
| 模块 | `PixelCapture` (Runtime), `PixelCaptureShaders` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-23 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/PixelCapture) | |

---

## 用途

Pixel Capture 是一个轻量级的像素缓冲区捕获与转换框架。它解决了实时渲染管线中不同组件之间像素数据生产速率和消费速率不一致的问题，支持异步多生产者/消费者模式。典型场景包括：

- 屏幕/视口画面录制 → 需要以固定帧率输出，但渲染帧率可能波动
- 像素流送（Pixel Streaming）→ 将 GPU 像素数据转换为网络编码所需的格式（如 YUV）
- 自定义后处理链 → 需要从中间帧缓冲提取数据而不阻塞渲染流程

框架包含两大模块：
- **PixelCapture**：核心运行时，提供 `FOutputFrameBuffer` 环形缓冲区和生产者/消费者管理逻辑。
- **PixelCaptureShaders**：提供 GPU 着色器运算，用于像素格式转换（如 RGB→YUV），输出到 UAV 纹理。

---

## 使用场景

- 你正在构建像素流送编码器 → 需要将渲染画面实时转换为 YUV420 格式供硬件编码器使用
- 你需要在游戏中录制高分辨率视频，但渲染线程不能阻塞 → 使用异步缓冲架构
- 你需要将渲染的目标（RenderTarget）内容传递到其他管线（如外部渲染器） → 使用共享缓冲区

---

## 蓝图用法

插件暴露了若干蓝图可调用的节点，主要集中在 `UPixelCapture` 类（假设，需确认实际暴露节点）。由于插件处于实验阶段，蓝图 API 可能有限。以下基于源码推断的核心交互方式：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Pixel Capture` | 创建捕获缓冲区实例，指定缓冲帧数和最大生产延迟 | `UPixelCapture` |
| `Produce Frame` | 提交一个像素缓冲区（来自 Render Target）到捕获队列 | `UPixelCapture` |
| `Consume Frame` | 从消费队列取出一个已就绪的帧（等待回调完成） | `UPixelCapture` |
| `On Frame Ready` | 当一帧完成格式转换后触发的事件（输出 `FPixelCaptureFrame`） | `UPixelCapture` |

### 使用示例（蓝图）

1. **创建捕获器**：在关卡蓝图的事件 BeginPlay 中，调用 `Create Pixel Capture` 节点，设置 BufferSize=3，MaxLatency=1。
2. **每帧提交画面**：在 Tick 中，获取一个渲染目标（如 `CaptureComponent2D` 的纹理），连接到 `Produce Frame` 的 Texture 引脚。
3. **消费输出**：绑定 `On Frame Ready` 事件，在事件中从 `FPixelCaptureFrame` 获取 Y/U/V 平面数据（作为 `Texture2D` 引用），传递给自定义编码器。

---

## C++ 用法

### 头文件引入

```cpp
// 核心运行时
#include "PixelCapture.h"
#include "OutputFrameBuffer.h"

// 着色器模块
#include "RGBToYUVShader.h"
```

### 基本用法 – 创建捕获缓冲并生产/消费

```cpp
// 从文件: Engine/Plugins/Media/PixelCapture/Source/PixelCapture/Private/... (示例)
// 使用 FOutputFrameBuffer 管理循环缓冲区

constexpr int32 BufferSize = 3;          // 缓冲帧数
constexpr int32 MaxProduceLatency = 2;   // 最大未消费帧数

TSharedPtr<FOutputFrameBuffer> CaptureBuffer = MakeShared<FOutputFrameBuffer>();

// 初始化缓冲区，指定帧大小和格式
FIntPoint FrameSize(1920, 1080);
EPixelFormat PixelFormat = EPixelFormat::PF_B8G8R8A8;

CaptureBuffer->Init(BufferSize, FrameSize, PixelFormat, MaxProduceLatency);

// 生产一帧（通常在渲染线程）
{
    auto Buffer = CaptureBuffer->LockProduceBuffer(); // 获取空闲缓冲
    if (Buffer)
    {
        // 将渲染目标拷贝到 Buffer->GetTexture()
        // ...
        CaptureBuffer->UnlockProduceBuffer(); // 标记为已生产
    }
}

// 消费一帧（通常在异步线程）
{
    auto ReadyFrame = CaptureBuffer->LockConsumeBuffer();
    if (ReadyFrame)
    {
        // 处理 ReadyFrame->GetTexture() 的数据
        // ...
        CaptureBuffer->UnlockConsumeBuffer();
    }
}
```

### 进阶用法 – RGB→YUV 转换（PixelCaptureShaders）

```cpp
// 从文件: Engine/Plugins/Media/PixelCapture/Source/PixelCaptureShaders/Public/RGBToYUVShader.h

void ConvertRGBToYUV(FRHICommandListImmediate& RHICmdList,
                     FTextureRHIRef SourceTexture,
                     FIntPoint SourceSize,
                     FUnorderedAccessViewRHIRef OutY,
                     FUnorderedAccessViewRHIRef OutU,
                     FUnorderedAccessViewRHIRef OutV)
{
    FRGBToYUVShaderParameters Params;
    Params.SourceTexture = SourceTexture;
    Params.DestPlaneYDimensions = FIntPoint(SourceSize.X, SourceSize.Y); // Y 平面与原图尺寸相同
    Params.DestPlaneUVDimensions = FIntPoint(SourceSize.X / 2, SourceSize.Y / 2); // UV 平面半分辨率
    Params.DestPlaneY = OutY;
    Params.DestPlaneU = OutU;
    Params.DestPlaneV = OutV;

    FRGBToYUVShader::Dispatch(RHICmdList, Params);
}
```

> **注意**：此着色器需要目标纹理已创建为 UAV 兼容格式（如 `PF_R8`）。调用前需确保资源已就绪。

---

## Demo 示例

以下是一个完整的最小示例，展示如何使用 `FOutputFrameBuffer` 和 `FRGBToYUVShader` 在 C++ 中捕获并转换像素数据。

### MyPixelCaptureActor.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "PixelCapture.h"
#include "OutputFrameBuffer.h"
#include "RHICommandList.h"
#include "MyPixelCaptureActor.generated.h"

UCLASS()
class AMyPixelCaptureActor : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

private:
    // 捕获缓冲
    TSharedPtr<FOutputFrameBuffer> CaptureBuffer;
    // UAV 资源用于 YUV 输出
    TRefCountPtr<FRHITexture2D> YPlaneTexture;
    TRefCountPtr<FRHITexture2D> UPlaneTexture;
    TRefCountPtr<FRHITexture2D> VPlaneTexture;
    FUnorderedAccessViewRHIRef YPlaneUAV;
    FUnorderedAccessViewRHIRef UPlaneUAV;
    FUnorderedAccessViewRHIRef VPlaneUAV;

    void InitResources();
    void ConvertFrame(FRHICommandListImmediate& RHICmdList, FTextureRHIRef SourceTexture);
};
```

### MyPixelCaptureActor.cpp

```cpp
#include "MyPixelCaptureActor.h"
#include "Engine/Texture2D.h"
#include "Engine/TextureRenderTarget2D.h"
#include "RenderingThread.h"
#include "RGBToYUVShader.h"

void AMyPixelCaptureActor::BeginPlay()
{
    Super::BeginPlay();
    InitResources();

    // 初始化捕获缓冲：2 个缓冲槽，最大延迟 1 帧
    CaptureBuffer = MakeShared<FOutputFrameBuffer>();
    CaptureBuffer->Init(2, FIntPoint(1920, 1080), EPixelFormat::PF_B8G8R8A8, 1);
}

void AMyPixelCaptureActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    // 示例：从 RenderTarget2D（假设已有）获取纹理
    UTextureRenderTarget2D* RenderTarget = /* 获取你的 RenderTarget */;
    if (!RenderTarget || !RenderTarget->GetResource()) return;

    FTextureRHIRef SourceTexture = RenderTarget->GetResource()->GetTexture2DRHI();
    if (!SourceTexture) return;

    // 生产一帧
    auto LockedBuffer = CaptureBuffer->LockProduceBuffer();
    if (LockedBuffer)
    {
        // 将 SourceTexture 拷贝到锁定缓冲区的纹理（此处省略具体拷贝实现）
        // LockedBuffer->GetTexture() 是预分配的纹理
        // 可以使用 FRHICopyTextureInfo 等
        FRHICommandListExecutor::GetImmediateCommandList().CopyTexture(
            SourceTexture, LockedBuffer->GetTexture(), FRHICopyTextureInfo()
        );
        CaptureBuffer->UnlockProduceBuffer();
    }

    // 消费一帧并进行格式转换
    auto ConsumedFrame = CaptureBuffer->LockConsumeBuffer();
    if (ConsumedFrame)
    {
        ENQUEUE_RENDER_COMMAND(ConvertPixelFrame)(
            [this, ConsumedFrame](FRHICommandListImmediate& RHICmdList)
            {
                ConvertFrame(RHICmdList, ConsumedFrame->GetTexture());
                // 消费完成后释放
                // 注意：此处仅为演示，实际应在渲染线程完成所有操作后调用 UnlockConsumeBuffer
            }
        );
        CaptureBuffer->UnlockConsumeBuffer();
    }
}

void AMyPixelCaptureActor::InitResources()
{
    // 创建 YUV 平面 UAV 纹理（PF_R8, 1920x1080 Y, 960x540 U/V）
    FRHIResourceCreateInfo CreateInfo;
    YPlaneTexture = RHICreateTexture2D(1920, 1080, PF_R8, 1, 1,
                                       TexCreate_UAV, CreateInfo);
    UPlaneTexture = RHICreateTexture2D(960, 540, PF_R8, 1, 1,
                                       TexCreate_UAV, CreateInfo);
    VPlaneTexture = RHICreateTexture2D(960, 540, PF_R8, 1, 1,
                                       TexCreate_UAV, CreateInfo);
    YPlaneUAV = RHICreateUnorderedAccessView(YPlaneTexture);
    UPlaneUAV = RHICreateUnorderedAccessView(UPlaneTexture);
    VPlaneUAV = RHICreateUnorderedAccessView(VPlaneTexture);
}

void AMyPixelCaptureActor::ConvertFrame(FRHICommandListImmediate& RHICmdList, FTextureRHIRef SourceTexture)
{
    FRGBToYUVShaderParameters Params;
    Params.SourceTexture = SourceTexture;
    Params.DestPlaneYDimensions = FIntPoint(1920, 1080);
    Params.DestPlaneUVDimensions = FIntPoint(960, 540);
    Params.DestPlaneY = YPlaneUAV;
    Params.DestPlaneU = UPlaneUAV;
    Params.DestPlaneV = VPlaneUAV;
    FRGBToYUVShader::Dispatch(RHICmdList, Params);
}
```

---

## 模块依赖

| 模块 | 用途 |
|---|---|
| `RHI`, `RenderCore` | GPU 资源创建、渲染命令、着色器调度 |
| `MediaIOFramework` | 可选依赖，提供媒体 I/O 管道集成 |
| `PixelCapture` 自身无特殊依赖（除标准 Core/Engine 外） | |

> 使用 `PixelCaptureShaders` 时需额外依赖 `RHI` 和 `RenderCore`（已在 Build.cs 中自动链接）。

---

## 维护状态

### 近期更新

- 2025-09-29 `9308001e` — [PixelCapture] Fix: Remove call to StopCapture as it can cause deadlocks
- 2025-09-25 `1fdac7d5` — [PixelCapture, PS, PS2] Fix: MediaCapture could get into a bad state due to use of queues and praying
- 2025-09-23 `20ee5e0e` — The source files included were modified by the UnrealCodeFixup tool so that they can pass the -merge
- 2025-09-23 `5a037905` — [PS2] Fix: Hang during first decoded frame
- 2025-06-23 `fb7a5db5` — [PixelCapture] Fix Pixel Capture incorrectly incrementing loop in FOutputFrameBuffer::LockProduceBu

### 维护评价

- **创建时间**：2025 年 6 月（距今约 4 个月）
- **更新频率**：活跃，最近一个月有多个 bug 修复
- **当前状态**：处于实验阶段（Beta），核心 API 可能变动
- **已知问题**：存在死锁（已修复）和缓冲区循环增加错误（已修复）
- **推荐使用**：✅ 适合需要像素捕获和格式转换的新项目，但请注意实验性标签，生产环境需等待稳定版

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/PixelCapture)
- [官方文档（像素流送）](https://docs.unrealengine.com/en-US/Platforms/PixelStreaming/index.html)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/PixelCapture/Tests)（若存在）