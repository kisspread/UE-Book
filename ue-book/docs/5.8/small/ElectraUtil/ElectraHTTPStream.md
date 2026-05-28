# Electra Player Utilities

> Reusable Base Components for Electra Player Media Playback

| 属性 | 值 |
|---|---|
| 中文名 | Electra 媒体工具库 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ElectraBase` (Runtime), `ElectraSamples` (Runtime), `ElectraHTTPStream` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-01-06 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraUtil) | |

## 用途

ElectraUtil 是 UE5 Electra 媒体播放器系统的底层基础设施插件，提供三个核心可复用模块：

1. **ElectraBase** — Electra 播放器的基础类型定义（如 `FParamDict` 参数字典），是所有 Electra 组件的公共依赖。
2. **ElectraSamples** — 媒体样本（Sample）的处理工具，负责音视频帧数据的封装与传递。
3. **ElectraHTTPStream** — 专为媒体流设计的 HTTP 客户端，支持 HTTP Range 请求（用于 seek）、分块传输编码、线程安全的数据缓冲，以及精确到毫秒的传输计时。

该插件解决的核心问题是：标准 HTTP 客户端无法满足媒体流播放的特殊需求——需要 Range 请求实现随机跳转、需要后台线程异步下载、需要零拷贝的数据缓冲以减少延迟。ElectraHTTPStream 将这些能力封装为独立模块，供整个 Electra 播放管线复用。

> ⚠️ 该插件默认未启用（`EnabledByDefault=false`），需在 `.uproject` 或项目设置中手动启用。

## 使用场景

- 你需要从 HTTP/HTTPS URL 流式播放媒体内容 → 用 ElectraHTTPStream 发起异步 HTTP Range 请求
- 你在构建自定义媒体播放器，需要精确控制 HTTP 数据的下载与缓冲 → 用 `IElectraHTTPStreamBuffer` 的 Lock/Unlock 模式实现零拷贝读取
- 你需要监控媒体下载的各阶段耗时（DNS 解析、连接、首字节等）→ 用 `IElectraHTTPStreamResponse` 的 Timing API
- 你需要解析 HTTP `Content-Range` 响应头 → 用 `FHttpRange::ParseFromContentRangeResponse()`
- 你需要构建 Electra 媒体播放管线的底层组件 → 依赖 ElectraBase 和 ElectraSamples 模块

## 蓝图用法

该插件的三个模块均为纯 C++ 运行时模块，**不暴露任何蓝图节点**。所有 API 均通过 C++ 接口调用。如需在蓝图中使用媒体播放功能，应使用上层的 Electra Player 插件。

## C++ 用法

### 头文件引入

```cpp
// HTTP 流媒体客户端
#include "ElectraHTTPStream.h"

// HTTP 范围请求工具
#include "Utilities/HttpRangeHeader.h"

// 线程安全数据缓冲（如需直接使用具体实现）
#include "ElectraHTTPStreamBuffer.h"
```

### 基本用法：发起 HTTP 流式请求

以下代码演示如何创建 HTTP 流客户端、发起 GET 请求并接收数据：

```cpp
// 来源: Public/ElectraHTTPStream.h - IElectraHTTPStream 接口文档

#include "ElectraHTTPStream.h"
#include "Utilities/HttpRangeHeader.h"

// 1. 创建 HTTP 流客户端实例
Electra::FParamDict Options;
TSharedPtr<IElectraHTTPStream, ESPMode::ThreadSafe> HTTPStream = IElectraHTTPStream::Create(Options);

// 2. 创建请求
IElectraHTTPStreamRequestPtr Request = HTTPStream->CreateRequest();
Request->SetURL(TEXT("https://example.com/video.mp4"));
Request->SetVerb(TEXT("GET"));  // 可选，默认为 GET
Request->AllowCompression(true);

// 3. 设置 Range 请求（用于 seek 到指定字节位置）
ElectraHTTPStream::FHttpRange Range;
Range.SetStart(1024);           // 从第 1024 字节开始
Range.SetEndIncluding(8191);    // 到第 8191 字节
Request->SetRange(Range.GetString(true));  // 输出: "bytes=1024-8191"

// 4. 绑定通知回调
Request->NotificationDelegate().BindLambda(
    [](IElectraHTTPStreamRequestPtr InRequest,
       EElectraHTTPStreamNotificationReason Reason,
       int64 Param)
    {
        if (Reason == EElectraHTTPStreamNotificationReason::Completed)
        {
            if (Param == 0)
            {
                // 请求成功完成
                IElectraHTTPStreamResponsePtr Response = InRequest->GetResponse();
                int32 HTTPCode = Response->GetHTTPResponseCode();
                int64 BytesReceived = Response->GetNumResponseBytesReceived();
                UE_LOG(LogTemp, Log, TEXT("HTTP %d, received %lld bytes"), HTTPCode, BytesReceived);
            }
            else
            {
                // 请求失败
                UE_LOG(LogTemp, Error, TEXT("Request failed: %s"), *InRequest->GetErrorMessage());
            }
        }
        else if (Reason == EElectraHTTPStreamNotificationReason::ReadData)
        {
            // 新数据到达，Param 为新增字节数
        }
    });

// 5. 提交请求执行
HTTPStream->AddRequest(Request);
```

### 基本用法：读取响应数据（Lock/Unlock 模式）

```cpp
// 来源: Public/ElectraHTTPStream.h - IElectraHTTPStreamBuffer 接口

// 在通知回调或轮询中读取数据
IElectraHTTPStreamResponsePtr Response = Request->GetResponse();
IElectraHTTPStreamBuffer& Buffer = Response->GetResponseData();

// Lock 获取原始数据指针（零拷贝）
const uint8* ReadPtr = nullptr;
int64 BytesAvailable = 0;
Buffer.LockBuffer(ReadPtr, BytesAvailable);

if (BytesAvailable > 0)
{
    // 处理 ReadPtr 指向的 BytesAvailable 字节数据
    // 例如传递给解码器
    ProcessMediaData(ReadPtr, BytesAvailable);
}

// Unlock 并标记已消费的字节数
Buffer.UnlockBuffer(BytesAvailable);  // 消费全部
// 或 Buffer.UnlockBuffer(1024);     // 只消费部分
```

### 进阶用法：监控 HTTP 传输计时

```cpp
// 来源: Public/ElectraHTTPStream.h - IElectraHTTPStreamResponse 接口

// 创建请求时启用计时追踪
Request->EnableTimingTraces();

// ... 发起请求并等待数据 ...

IElectraHTTPStreamResponsePtr Response = Request->GetResponse();

// 获取各阶段耗时（秒）
double DNSTime     = Response->GetTimeUntilNameResolved();
double ConnectTime = Response->GetTimeUntilConnected();
double FirstByte   = Response->GetTimeUntilFirstByte();
double TotalTime   = Response->GetTimeElapsed();

UE_LOG(LogTemp, Log, TEXT("DNS: %.3fs, Connect: %.3fs, FirstByte: %.3fs, Total: %.3fs"),
    DNSTime, ConnectTime, FirstByte, TotalTime);

// 获取细粒度的采样追踪
TArray<IElectraHTTPStreamResponse::FTimingTrace> Traces;
Response->GetTimingTraces(&Traces, 0);  // 获取但不移除

for (const auto& Trace : Traces)
{
    UE_LOG(LogTemp, Verbose, TEXT("  t=%.3fs: +%lld bytes (total %lld)"),
        Trace.TimeSinceStart, Trace.NumBytesAdded, Trace.TotalBytesAdded);
}
```

### 进阶用法：解析 Content-Range 响应头

```cpp
// 来源: Public/Utilities/HttpRangeHeader.h

#include "Utilities/HttpRangeHeader.h"

// 解析服务器返回的 Content-Range 头
ElectraHTTPStream::FHttpRange ParsedRange;
FString ContentRangeHeader = TEXT("bytes 26151-157222/7594984");

if (ParsedRange.ParseFromContentRangeResponse(ContentRangeHeader))
{
    int64 Start     = ParsedRange.GetStart();           // 26151
    int64 End       = ParsedRange.GetEndIncluding();    // 157222
    int64 TotalSize = ParsedRange.GetDocumentSize();    // 7594984
    int64 Bytes     = ParsedRange.GetNumberOfBytes();   // 131072

    UE_LOG(LogTemp, Log, TEXT("Range %lld-%lld of %lld (%lld bytes)"),
        Start, End, TotalSize, Bytes);
}

// 构造 Range 请求头
ElectraHTTPStream::FHttpRange RequestRange;
RequestRange.SetStart(0);
RequestRange.SetEndIncluding(1023);
FString HeaderValue = RequestRange.GetString(true);  // "bytes=0-1023"
```

## Demo 示例

以下是一个完整的最小示例，演示如何使用 ElectraHTTPStream 下载文件数据：

```cpp
// MyHTTPStreamExample.h
#pragma once

#include "CoreMinimal.h"

class IElectraHTTPStream;
class IElectraHTTPStreamRequest;

class FMyHTTPStreamExample
{
public:
    void StartDownload(const FString& URL);
    void Tick();

private:
    TSharedPtr<IElectraHTTPStream, ESPMode::ThreadSafe> HTTPStream;
    TSharedPtr<IElectraHTTPStreamRequest, ESPMode::ThreadSafe> ActiveRequest;
    bool bDownloadComplete = false;
};
```

```cpp
// MyHTTPStreamExample.cpp
#include "MyHTTPStreamExample.h"
#include "ElectraHTTPStream.h"
#include "Utilities/HttpRangeHeader.h"

void FMyHTTPStreamExample::StartDownload(const FString& URL)
{
    // 创建 HTTP 流客户端
    Electra::FParamDict Options;
    HTTPStream = IElectraHTTPStream::Create(Options);
    if (!HTTPStream.IsValid())
    {
        return;
    }

    // 创建并配置请求
    ActiveRequest = HTTPStream->CreateRequest();
    ActiveRequest->SetURL(URL);
    ActiveRequest->AllowCompression(true);
    ActiveRequest->EnableTimingTraces();

    // 绑定回调
    ActiveRequest->NotificationDelegate().BindLambda(
        [this](IElectraHTTPStreamRequestPtr InRequest,
               EElectraHTTPStreamNotificationReason Reason,
               int64 Param)
        {
            if (Reason == EElectraHTTPStreamNotificationReason::Completed)
            {
                bDownloadComplete = true;

                if (Param != 0)
                {
                    UE_LOG(LogTemp, Error, TEXT("Download failed: %s"),
                        *InRequest->GetErrorMessage());
                    return;
                }

                auto Response = InRequest->GetResponse();
                UE_LOG(LogTemp, Log, TEXT("Download complete: HTTP %d, %lld bytes in %.2fs"),
                    Response->GetHTTPResponseCode(),
                    Response->GetNumResponseBytesReceived(),
                    Response->GetTimeUntilFirstByte());
            }
        });

    // 提交执行
    HTTPStream->AddRequest(ActiveRequest);
}

void FMyHTTPStreamExample::Tick()
{
    if (!ActiveRequest.IsValid() || bDownloadComplete)
    {
        return;
    }

    // 从缓冲区读取新到达的数据
    auto Response = ActiveRequest->GetResponse();
    if (Response.IsValid())
    {
        auto& Buffer = Response->GetResponseData();
        const uint8* DataPtr = nullptr;
        int64 NumBytes = 0;

        Buffer.LockBuffer(DataPtr, NumBytes);
        if (NumBytes > 0)
        {
            // 处理数据（例如写入文件或传递给解码器）
            // ...
            Buffer.UnlockBuffer(NumBytes);
        }
        else
        {
            Buffer.UnlockBuffer(0);
        }
    }

    if (bDownloadComplete && HTTPStream.IsValid())
    {
        HTTPStream->Close();
        HTTPStream.Reset();
        ActiveRequest.Reset();
    }
}
```

## 模块依赖

从 Build.cs 和源码推断的依赖关系：

| 模块 | 用途 |
|---|---|
| `ElectraBase` | 基础类型定义（`FParamDict` 等），ElectraHTTPStream 和 ElectraSamples 的公共依赖 |
| `HTTP` | 底层 HTTP 传输实现（ElectraHTTPStream 的实际网络请求依赖） |
| `DirectX` | 媒体样本处理的图形 API 支持（ElectraSamples 模块） |

> 常见的 Core、CoreUObject、Engine 等标准依赖已省略。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `bc37b7ea` | ElectraUtil: added stub methods for server builds to prevent linker errors when this class is accide | 为服务器构建添加桩方法，防止链接错误 |
| 2026-04-23 | `efcad028` | HDR: Fix HDR normalization factor across media causing incorrect brightness levels going from/to the | 修复 HDR 媒体归一化因子导致亮度不正确的问题 |
| 2026-04-20 | `3ed2062b` | ElectraDecoders: modernized the decoder factory to be more usable for other clients | 现代化解码器工厂，提升对其他客户端的可用性 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移到 UE_LOGF |
| 2026-03-25 | `2924c4cc` | [ElectraUtil] Fix timecode subframe precision loss in CreateTimecodeFromMPEGDefinition | 修复 MPEG 时间码子帧精度丢失问题 |

### 维护评价

- **活跃维护**：最近 6 个月内有多次功能性更新和 bug 修复（截至 2026-05）
- **持续演进**：从 NFL（内部）迁移至公开后持续更新，涵盖 HDR 修复、编解码器现代化、平台兼容性改进等
- **平台覆盖**：支持 Win64、Mac、iOS、tvOS、Android、Linux，排除服务器构建
- **风险提示**：`EnabledByDefault=false` 表明这是一个选择性启用的模块，通常由上层 Electra Player 插件自动依赖
- **推荐使用**：如果你在使用 Electra 媒体播放器，该插件是必需的底层依赖；如果是自定义媒体管线，ElectraHTTPStream 模块提供了生产级的 HTTP 流式传输能力

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraUtil)
- [官方文档](https://docs.unrealengine.com/en-US/Engine/MediaFramework/Overview)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraUtil/Tests)（如有）