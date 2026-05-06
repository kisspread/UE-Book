# Electra Player Utilities

> Reusable Base Components for Electra Player Media Playback

| 属性 | 值 |
|---|---|
| 中文名 | Electra 播放器工具集 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ElectraBase` (Runtime), `ElectraSamples` (Runtime), `ElectraHTTPStream` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-09-24 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/ElectraUtil) | |

## 用途

ElectraUtil 提供了三个可复用的基础模块，用于支持 Electra 播放器的媒体播放流程：

- **ElectraBase**：核心基类与公用工具，如参数字典、线程同步、日志等。
- **ElectraSamples**：媒体样本（音视频帧）的缓冲、管理与 GPU 上传，支持 DirectX 12 等图形 API。
- **ElectraHTTPStream**：轻量级的 HTTP 流式请求/响应接口，支持分块下载、Range 请求、性能追踪等，是 Electra 网络播放的基础。

该插件不直接提供播放器 UI，而是为上层播放器（如 `MediaPlayer`）提供底层网络 I/O 和样本处理组件。

## 使用场景

- 你正在开发或扩展基于 Electra 的媒体播放功能，需要自定义 HTTP 请求的细节（如 Headers、进度回调、性能监控）。
- 你需要以低延迟、流式方式从网络拉取音视频数据，并对接收到的数据缓冲区进行精细控制（如并行下载分片）。
- 你需要在 C++ 层直接操作媒体样本的 GPU 纹理或 CPU 缓冲区，而不通过 UE 的 `MediaTextureResource` 管道。

## 蓝图用法

本模块的接口设计为纯 C++ 类（`IElectraHTTPStream`、`IElectraHTTPStreamRequest` 等），未暴露为蓝图节点。若需从蓝图触发网络请求，应使用上层 `MediaPlayer` 自带的加载逻辑，或通过自定义 C++ 函数包装后暴露。

## C++ 用法

### 头文件引入

```cpp
#include "ElectraHTTPStream.h"
#include "IElectraHTTPStreamModule.h"
#include "ElectraHTTPStreamBuffer.h"
#include "Utilities/HttpRangeHeader.h"
```

### 基本用法：发起 GET 请求

以下示例展示了如何通过 `IElectraHTTPStream` 发起一个简单的 HTTP GET 请求，并获取响应体。

```cpp
// 1. 创建 HTTP 流实例（通常来自 Module 单例）
IElectraHTTPStream* Stream = IElectraHTTPStream::Create();

// 2. 创建请求对象
TSharedPtr<IElectraHTTPStreamRequest, ESPMode::ThreadSafe> Request = Stream->CreateRequest();

// 3. 设置 URL
Request->SetURL(TEXT("https://example.com/video.mp4"));

// 4. 设置附加 Headers 和参数（可选）
Request->SetVerb(TEXT("GET"));

// 5. 注册回调
Request->SetNotificationDelegate(FElectraHTTPStreamNotificationDelegate::CreateLambda(
    [](IElectraHTTPStreamRequestPtr Req, EElectraHTTPStreamNotificationReason Reason, int64 Param)
    {
        if (Reason == EElectraHTTPStreamNotificationReason::Completed)
        {
            const IElectraHTTPStreamResponse& Resp = Req->GetResponse();
            // 读取响应数据
            const IElectraHTTPStreamBuffer& Buffer = Resp.GetResponseData();
            int64 Avail = Buffer.GetNumBytesAvailableForRead();
            const uint8* Data = nullptr;
            int64 OutBytes = 0;
            Buffer.LockBuffer(Data, OutBytes);
            // 处理数据...
            Buffer.UnlockBuffer(OutBytes);
        }
    }
));

// 6. 添加请求数据（仅 POST/PUT 时需要）
// Request->AddRequestData(...);

// 7. 发送请求
Request->Start();

// 8. 释放流（通常在模块关闭时）
// delete Stream;
```

### 进阶用法：使用 Range 请求

对于断点续传或流式分片下载，可利用 `FElectraHTTPStreamBuffer` 和 Range 头：

```cpp
// 构造 Range 头
ElectraHTTPStream::FHttpRange Range;
Range.SetStart(0);
Range.SetEndIncluding(1024 * 1024); // 前 1MB

// 设置到请求头
Request->SetHeader(TEXT("Range"), Range.GetString(true)); // "bytes=0-1048576"

// 请求后解析 Content-Range 以获取分片信息
// 通过 IElectraHTTPStreamResponse::GetContentRangeHeader() 获取
```

### 性能追踪

启用时序追踪以调试网络延迟：

```cpp
// 在创建请求后启用
Request->EnableTimingTraces();

// 请求结束后从 Response 获取时间线
TArray<IElectraHTTPStreamResponse::FTimingTrace> Traces;
double nameResolved = Response.GetTimeUntilNameResolved();
double firstByte    = Response.GetTimeUntilFirstByte();
double elapsed      = Response.GetTimeElapsed();
```

### 自定义缓冲区处理

`FElectraHTTPStreamBuffer` 提供了线程安全的数据追加与消费操作：

```cpp
FElectraHTTPStreamBuffer Buffer;
TArray<uint8> Chunk1 = {0x00, 0x01, 0x02};
Buffer.AddData(Chunk1);

int64 Avail = Buffer.GetNumBytesAvailableForRead(); // 3
const uint8* ReadPtr = nullptr;
int64 Num = 0;
Buffer.LockBuffer(ReadPtr, Num); // 返回 Buffer 内部指针
// 读取数据
Buffer.UnlockBuffer(Num); // 消费所有已读取数据
```

## Demo 示例

以下为一个完整的 C++ Minimal 示例（需在 `MediaPlayer` 或自定义 Actor 中使用）。

**DemoHTTPActor.h**

```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ElectraHTTPStream.h"
#include "DemoHTTPActor.generated.h"

UCLASS()
class ADemoHTTPActor : public AActor
{
    GENERATED_BODY()
public:
    ADemoHTTPActor();
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    IElectraHTTPStream* HTTPStream = nullptr;
    IElectraHTTPStreamRequestPtr Request;
    void OnRequestCompleted(IElectraHTTPStreamRequestPtr Req, EElectraHTTPStreamNotificationReason Reason, int64 Param);
};
```

**DemoHTTPActor.cpp**

```cpp
#include "DemoHTTPActor.h"
#include "IElectraHTTPStreamModule.h"

ADemoHTTPActor::ADemoHTTPActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void ADemoHTTPActor::BeginPlay()
{
    Super::BeginPlay();
    HTTPStream = IElectraHTTPStream::Create();
    if (!HTTPStream) return;

    Request = HTTPStream->CreateRequest();
    Request->SetURL(TEXT("https://httpbin.org/get"));
    Request->SetVerb(TEXT("GET"));
    Request->SetNotificationDelegate(FElectraHTTPStreamNotificationDelegate::CreateUObject(this, &ADemoHTTPActor::OnRequestCompleted));
    Request->Start();
}

void ADemoHTTPActor::OnRequestCompleted(IElectraHTTPStreamRequestPtr Req, EElectraHTTPStreamNotificationReason Reason, int64 Param)
{
    if (Reason == EElectraHTTPStreamNotificationReason::Completed)
    {
        const IElectraHTTPStreamResponse& Resp = Req->GetResponse();
        UE_LOG(LogTemp, Log, TEXT("HTTP Status: %d, Body size: %lld bytes"), Resp.GetHTTPResponseCode(), Resp.GetNumResponseBytesReceived());
    }
}

void ADemoHTTPActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    delete HTTPStream;
    HTTPStream = nullptr;
    Super::EndPlay(EndPlayReason);
}
```

## 模块依赖

仅列出该插件需告知用户引用的独特模块（省略标准引擎模块）：

| 模块 | 用途 |
|---|---|
| `ParameterDictionary` | 在 `ElectraHTTPStream::Create` 中用于传递平台级选项 |
| `DirectX` | 仅 `ElectraSamples` 模块使用，用于 GPU 纹理创建（Win64） |
| 无特殊依赖（ElectraBase/ElectraHTTPStream） | 仅依赖 CoreMinimal、HAL、Templates 等标准模块 |

使用本插件时，你需要在模块的 `Build.cs` 中增加 `"ElectraBase", "ElectraSamples", "ElectraHTTPStream"` 中的具体模块名。

## 维护状态

### 近期更新

- 2025-09-25 e6018661 — ElectraUtils: Fixed check to BufferAvailable() in the DX12 buffer helpers
- 2025-09-25 83ef846c — ElectraSamples: Fixed Linux server build linker error
- 2025-09-25 916bb820 — ElectraSamples: calling ShutdownPoolable() in the destructor to avoid potential resource leaks
- 2025-09-24 241a7987 — ElectraUtil: Removing hard limit of number of buffer slots in favor of dynamic resizes
- 2025-09-24 7d7c63bd — ElectraUtil: fixed DX12 GPU buffer helper heap issues

### 维护评价

ElectraUtil 是 UE 5.5 之后引入的新插件，代码量适中（~93 源文件），从创建（2025-09-24）至今几乎每天都有功能性和修复性提交，维护非常活跃。目前无明显已知缺陷，推荐在需要底层媒体流控制或自定义网络传输时使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/ElectraUtil)
- [官方文档](https://docs.unrealengine.com/en-US/Engine/MediaFramework/Overview)
- 测试用例路径：`Engine/Plugins/Media/ElectraUtil/Tests/` （未公开源码，实际位于内部仓库）