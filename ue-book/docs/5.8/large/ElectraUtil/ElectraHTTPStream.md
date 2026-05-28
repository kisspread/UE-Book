# Electra Player Utilities

> Reusable Base Components for Electra Player Media Playback（照抄，不翻译）

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

ElectraUtil 是 UE5 内置 Electra 媒体播放器系统的**基础设施层**，提供了媒体播放所需的核心可复用组件。它不是一个独立使用的插件，而是作为 Electra 媒体播放器生态系统的底层支撑。

该插件包含三个子模块，各自承担不同职责：

- **ElectraBase**：基础类型定义和通用工具
- **ElectraSamples**：媒体采样数据处理（处理解码后的音视频帧）
- **ElectraHTTPStream**：HTTP 流媒体传输层，处理基于 HTTP 的媒体数据获取

本插件存在的原因是：Electra 播放器需要支持 HLS、DASH 等基于 HTTP 的流媒体协议，而 HTTP 流式下载涉及分块传输、Range 请求、断点续传、数据缓冲等复杂逻辑。ElectraHTTPStream 将这些逻辑封装为独立的、线程安全的组件，供上层的 Electra 播放器和协议解析器使用。

**注意**：`EnabledByDefault = false`，需要手动在项目设置中启用，或由上层 Electra 播放器插件间接启用。

## 使用场景

- 你需要实现基于 HTTP 的流媒体播放（HLS/DASH）→ 使用 ElectraHTTPStream 进行分段数据下载
- 你需要对 HTTP 下载进行精细的进度跟踪和性能分析 → 使用响应对象的 Timing API
- 你需要实现 HTTP Range 请求以支持媒体 Seek → 使用 `FHttpRange` 工具类
- 你在开发自定义的 Electra 协议解析器 → 依赖 ElectraHTTPStream 作为数据获取层

## 蓝图用法

⚠️ **本插件不提供蓝图接口**。所有 API 均为纯 C++ 接口，面向开发者和协议实现者，不暴露给蓝图。

## C++ 用法

ElectraHTTPStream 提供了一套完整的异步 HTTP 流式下载 API，基于接口驱动设计（Interface-based），所有类型均为纯虚接口，平台特定实现由内部提供。

### 头文件引入

```cpp
#include "ElectraHTTPStream.h"
#include "ElectraHTTPStreamBuffer.h"
#include "Utilities/HttpRangeHeader.h"
```

### 基本用法

以下示例展示了如何创建 HTTP 流实例、发起请求并处理响应数据：

```cpp
#include "ElectraHTTPStream.h"

// 1. 创建 HTTP 流实例（线程安全）
Electra::FParamDict Options;
TSharedPtr<IElectraHTTPStream, ESPMode::ThreadSafe> HTTPStream = IElectraHTTPStream::Create(Options);

// 2. 创建请求
IElectraHTTPStreamRequestPtr Request = HTTPStream->CreateRequest();
Request->SetURL(TEXT("https://example.com/video_segment.ts"));
Request->SetVerb(TEXT("GET"));

// 3. 绑定进度通知回调
Request->NotificationDelegate().BindLambda(
    [](IElectraHTTPStreamRequestPtr InRequest, EElectraHTTPStreamNotificationReason Reason, int64 Param)
    {
        switch (Reason)
        {
            case EElectraHTTPStreamNotificationReason::ReceivedHeaders:
                // 头部已收到，可以开始读取元数据
                break;
            case EElectraHTTPStreamNotificationReason::ReadData:
                // 新数据到达，Param 为本批次字节数
                break;
            case EElectraHTTPStreamNotificationReason::Completed:
                // 请求完成（成功或失败）
                if (InRequest->HasFailed())
                {
                    UE_LOG(LogTemp, Error, TEXT("Request failed: %s"), *InRequest->GetErrorMessage());
                }
                break;
        }
    });

// 4. 提交请求执行
HTTPStream->AddRequest(Request);

// 5. 稍后从响应中读取数据
IElectraHTTPStreamResponsePtr Response = Request->GetResponse();
if (Response->GetStatus() == IElectraHTTPStreamResponse::EStatus::Completed)
{
    IElectraHTTPStreamBuffer& Buffer = Response->GetResponseData();
    const uint8* ReadPtr = nullptr;
    int64 BytesAvailable = 0;
    Buffer.LockBuffer(ReadPtr, BytesAvailable);
    
    // 处理 ReadPtr 指向的 BytesAvailable 字节数据...
    // 例如：将数据送入媒体解复用器
    
    Buffer.UnlockBuffer(BytesAvailable);  // 标记已消费的字节数
}
```

### 进阶用法

#### 使用 Range 请求实现媒体 Seek

```cpp
#include "Utilities/HttpRangeHeader.h"

// 构造 Range 请求头，实现部分内容下载（用于媒体 Seek）
Request->SetURL(TEXT("https://example.com/large_video.mp4"));

// 方式一：直接设置 Range 字符串
Request->SetRange(TEXT("bytes=1024-2047"));

// 方式二：使用 FHttpRange 工具类精确构造
ElectraHTTPStream::FHttpRange Range;
Range.SetStart(1024);
Range.SetEndIncluding(2047);
FString RangeStr = Range.GetString(true);  // "bytes=1024-2047"
Request->SetRange(RangeStr);
```

#### 解析 Content-Range 响应头

```cpp
// 从服务器响应中解析 Range 信息
ElectraHTTPStream::FHttpRange ParsedRange;
FString ContentRangeHeader = Response->GetContentRangeHeader();
// 例如: "bytes 26151-157222/7594984"

if (ParsedRange.ParseFromContentRangeResponse(ContentRangeHeader))
{
    int64 Start = ParsedRange.GetStart();           // 26151
    int64 End = ParsedRange.GetEndIncluding();       // 157222
    int64 DocumentSize = ParsedRange.GetDocumentSize(); // 7594984
    int64 ByteCount = ParsedRange.GetNumberOfBytes();   // 131072
}
```

#### 启用性能追踪

```cpp
// 启用详细的时间戳追踪，用于性能分析
Request->EnableTimingTraces();

// 请求完成后获取性能数据
IElectraHTTPStreamResponsePtr Response = Request->GetResponse();

// 获取各阶段耗时（秒）
double DNSResolveTime = Response->GetTimeUntilNameResolved();
double ConnectTime = Response->GetTimeUntilConnected();
double FirstByteTime = Response->GetTimeUntilFirstByte();
double TotalTime = Response->GetTimeUntilFinished();

// 获取详细的分块时间线
TArray<IElectraHTTPStreamResponse::FTimingTrace> Traces;
Response->GetTimingTraces(&Traces, 0);
for (const auto& Trace : Traces)
{
    UE_LOG(LogTemp, Log, TEXT("t=%.3fs: +%lld bytes (total: %lld)"),
        Trace.TimeSinceStart, Trace.NumBytesAdded, Trace.TotalBytesAdded);
}

// 读取后清除已消费的追踪数据
Response->GetTimingTraces(nullptr, Traces.Num());
```

#### 线程处理器委托

```cpp
// 为 HTTP 流添加自定义线程处理器，驱动外部控制逻辑
HTTPStream->AddThreadHandlerDelegate(
    IElectraHTTPStream::FElectraHTTPStreamThreadHandlerDelegate::CreateLambda([]()
    {
        // 在 HTTP 工作线程上周期性调用
        // 可以在这里驱动外部的状态机或请求调度器
    }));

// 手动触发工作信号，不等待超时
HTTPStream->TriggerWorkSignal();

// 清理时必须先关闭
HTTPStream->Close();
HTTPStream.Reset();
```

## Demo 示例

以下是一个完整的 HTTP 流式下载示例，展示了从请求创建到数据消费的完整流程：

```cpp
// ElectraHTTPStreamDemo.h
#pragma once

#include "CoreMinimal.h"
#include "ElectraHTTPStream.h"

class FElectraHTTPStreamDemo
{
public:
    void StartDownload(const FString& URL);
    bool IsComplete() const;
    void Cleanup();

private:
    TSharedPtr<IElectraHTTPStream, ESPMode::ThreadSafe> Stream;
    IElectraHTTPStreamRequestPtr ActiveRequest;
    std::atomic<bool> bComplete{false};
    TArray<uint8> AccumulatedData;
};
```

```cpp
// ElectraHTTPStreamDemo.cpp
#include "ElectraHTTPStreamDemo.h"
#include "ElectraHTTPStreamBuffer.h"

void FElectraHTTPStreamDemo::StartDownload(const FString& URL)
{
    // 创建 HTTP 流实例
    Stream = IElectraHTTPStream::Create(Electra::FParamDict());
    if (!Stream)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create Electra HTTP stream"));
        return;
    }

    // 配置请求
    ActiveRequest = Stream->CreateRequest();
    ActiveRequest->SetURL(URL);
    ActiveRequest->SetVerb(TEXT("GET"));
    ActiveRequest->AllowCompression(true);

    // 绑定通知回调
    ActiveRequest->NotificationDelegate().BindLambda(
        [this](IElectraHTTPStreamRequestPtr InRequest, EElectraHTTPStreamNotificationReason Reason, int64 Param)
        {
            if (Reason == EElectraHTTPStreamNotificationReason::ReadData)
            {
                // 从缓冲区读取新到达的数据
                IElectraHTTPStreamBuffer& Buffer = InRequest->GetResponse()->GetResponseData();
                const uint8* ReadPtr = nullptr;
                int64 BytesAvailable = 0;
                Buffer.LockBuffer(ReadPtr, BytesAvailable);
                
                if (BytesAvailable > 0)
                {
                    AccumulatedData.Append(ReadPtr, BytesAvailable);
                    Buffer.UnlockBuffer(BytesAvailable);
                }
                else
                {
                    Buffer.UnlockBuffer(0);
                }
            }
            else if (Reason == EElectraHTTPStreamNotificationReason::Completed)
            {
                bComplete.store(true);
                
                if (InRequest->HasFailed())
                {
                    UE_LOG(LogTemp, Error, TEXT("Download failed: %s"),
                        *InRequest->GetErrorMessage());
                }
                else
                {
                    auto Response = InRequest->GetResponse();
                    UE_LOG(LogTemp, Log, TEXT("Download complete: %lld bytes, HTTP %d"),
                        Response->GetNumResponseBytesReceived(),
                        Response->GetHTTPResponseCode());
                }
            }
        });

    // 提交执行
    Stream->AddRequest(ActiveRequest);
}

bool FElectraHTTPStreamDemo::IsComplete() const
{
    return bComplete.load();
}

void FElectraHTTPStreamDemo::Cleanup()
{
    if (ActiveRequest.IsValid())
    {
        ActiveRequest->Cancel();
        ActiveRequest.Reset();
    }
    if (Stream.IsValid())
    {
        Stream->Close();
        Stream.Reset();
    }
}
```

## 模块依赖

从 ElectraHTTPStream 的 Build.cs 分析，该模块依赖的标准模块较多，但多数为引擎基础模块。以下是**独特**的依赖：

| 模块 | 用途 |
|---|---|
| `ElectraBase` | Electra 基础类型定义（FParamDict 等） |

其余均为 Core、CoreUObject、Engine 等标准依赖。ElectraSamples 模块还额外依赖 `DirectX`（仅 Windows 平台）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `bc37b7ea` | ElectraUtil: added stub methods for server builds to prevent linker errors when this class is accide | 为服务器构建添加桩方法，修复链接错误 |
| 2026-04-23 | `efcad028` | HDR: Fix HDR normalization factor across media causing incorrect brightness levels going from/to the | 修复 HDR 归一化因子导致的亮度不正确问题 |
| 2026-04-20 | `3ed2062b` | ElectraDecoders: modernized the decoder factory to be more usable for other clients | 现代化解码器工厂，提高对其他客户端的可用性 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移到 UE_LOGF 宏 |
| 2026-03-25 | `2924c4cc` | [ElectraUtil] Fix timecode subframe precision loss in CreateTimecodeFromMPEGDefinition | 修复 MPEG 时间码子帧精度丢失问题 |

### 维护评价

**活跃维护**。

- 创建于 2021 年 1 月，是 Epic 从内部项目（NFL）迁移到公开引擎的组件
- 最近 3 个月内有多次实质性更新，涵盖 bug 修复、平台兼容性改进和代码现代化
- 作为 UE5 核心媒体播放器框架的基础设施，由 Epic 持续维护
- 最新提交（2026-05-26）表明仍在积极适配新的构建场景（如 Dedicated Server）
- **推荐使用**：如果你在开发基于 Electra 的媒体播放功能，这是必需的基础依赖
- **注意事项**：默认未启用（`EnabledByDefault = false`），需要手动启用或通过上层插件启用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraUtil)
- [官方文档](https://docs.unrealengine.com/en-US/Engine/MediaFramework/Overview)
- [ElectraHTTPStream 模块头文件](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Media/ElectraUtil/Source/ElectraHTTPStream/Public/ElectraHTTPStream.h)