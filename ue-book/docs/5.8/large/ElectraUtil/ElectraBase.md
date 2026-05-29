# Electra Player Utilities

> Reusable Base Components for Electra Player Media Playback

| 属性 | 值 |
|---|---|
| 中文名 | Electra 播放器基础库 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ElectraBase` (Runtime), `ElectraSamples` (Runtime), `ElectraHTTPStream` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-01-06 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraUtil) | |

## 用途

ElectraUtil 是 Unreal Engine 媒体播放框架的**底层基础库**，为 Electra 媒体播放器及其相关插件（如 ElectraPlayer、ElectraDecoders 等）提供可复用的基础设施组件。

这个插件本身**不直接播放媒体**，而是提供构建媒体播放系统所需的核心构建块：

- **线程安全的数据结构**：消息队列（`TMediaMessageQueue`）、线程安全的参数字典（`FParamDictTS`）
- **时间值管理**：高精度时间表示（`FTimeValue`，基于百纳秒 HNS）、时间分数（`FTimeFraction`）
- **线程原语**：自定义线程封装（`FMediaThread`）、信号量（`FMediaSemaphore`）、事件信号（`FMediaEvent`）
- **二进制数据处理**：比特流读写器（`FBitstreamReader`/`FBitstreamWriter`）、字节序转换
- **URL 解析**：符合 RFC 3986 的 URL 解析器（`FURL_RFC3986`）
- **编解码器元数据**：编解码器格式描述（`FCodecTypeFormat`）、DRM 信息（`FDRMTypeFormat`）、解码器输出接口（视频/音频/字幕/元数据）
- **语言与国际化**：BCP47 语言标签解析、ISO 639 语言代码映射
- **MPEG 解析**：ES 描述符解析、ID3v2 元数据解析

**为什么存在**：Electra 媒体播放系统被设计为模块化架构，将底层工具函数和数据结构抽取到独立的基础库中，使得多个上层插件（播放器、解码器、HTTP 流等）可以共享同一套基础设施，避免代码重复。

**为什么默认不启用**：这是一个纯基础设施库，没有用户可见功能。它会被 ElectraPlayer 等上层插件自动依赖启用。

## 使用场景

- 你在实现自定义的媒体源或媒体播放器 → 用 ElectraBase 提供的时间值、消息队列和线程原语
- 你需要解析流媒体 URL（HLS/DASH manifest 中的链接）→ 用 `FURL_RFC3986`
- 你需要在多线程媒体管线中安全传递数据 → 用 `TMediaMessageQueue` 系列
- 你需要读取 MP4/媒体容器中的二进制数据 → 用 `FBitstreamReader`
- 你需要处理媒体时间码和帧率 → 用 `FTimeValue` 和 `FTimeFraction`
- 你在开发基于 Electra 的媒体扩展 → 这是必须依赖的基础模块

## 蓝图用法

本插件不包含任何 BlueprintCallable 函数。它是一个纯 C++ 基础设施库，所有 API 均为 C++ 层面使用。

## C++ 用法

### 头文件引入

```cpp
#include "TimeValue.h"                    // FTimeValue, FTimeFraction
#include "ParameterDictionary.h"          // FVariantValue, FParamDict, FParamDictTS
#include "MediaMessageQueue.h"            // TMediaMessageQueue 系列
#include "MediaQueue.h"                   // TMediaQueue 基础队列
#include "Utilities/ElectraBitstream.h"   // FBitstreamReader, FBitstreamWriter
#include "Utilities/URLParser.h"          // FURL_RFC3986
#include "MediaThreads.h"                 // FMediaThread, FMediaRunnable
#include "MediaSemaphore.h"               // FMediaSemaphore
#include "MediaEventSignal.h"             // FMediaEvent
#include "CodecTypeFormat.h"              // FCodecTypeFormat, FDRMTypeFormat
#include "MediaVideoDecoderOutput.h"      // IVideoDecoderHDRInformation 等
#include "Utilities/BCP47-Helpers.h"      // BCP47 语言标签
#include "Utilities/StringHelpers.h"      // 字符串工具
```

### 基本用法：时间值操作

`FTimeValue` 是 Electra 系统中最核心的时间表示类，内部以百纳秒（HNS）精度存储时间。

```cpp
// 来源: Public/PlayerTime.h

// 从秒创建时间值
Electra::FTimeValue Time(1.5);  // 1.5 秒

// 从毫秒创建
Electra::FTimeValue TimeMs;
TimeMs.SetFromMilliseconds(1500);

// 从 HNS（百纳秒）创建
Electra::FTimeValue TimeHNS;
TimeHNS.SetFromHNS(15000000);  // 1.5 秒

// 从 90kHz 时钟创建（MPEG 常用时钟频率）
Electra::FTimeValue Time90k;
Time90k.SetFrom90kHz(135000);  // 1.5 秒

// 从分数形式创建（如 30000/1001 = 29.97fps 对应的帧时间）
Electra::FTimeValue TimeND;
TimeND.SetFromND(30000, 1001);

// 转换为不同单位
double Seconds = Time.GetAsSeconds();
int64 Milliseconds = Time.GetAsMilliseconds();
int64 HNS = Time.GetAsHNS();
FTimespan Timespan = Time.GetAsTimespan();

// 特殊值
Electra::FTimeValue Invalid = Electra::FTimeValue::GetInvalid();
Electra::FTimeValue Zero = Electra::FTimeValue::GetZero();
Electra::FTimeValue PosInf = Electra::FTimeValue::GetPositiveInfinity();

// 运算
Electra::FTimeValue A(1.0);
Electra::FTimeValue B(0.5);
Electra::FTimeValue Sum = A + B;   // 1.5 秒
Electra::FTimeValue Diff = A - B;  // 0.5 秒
bool bLess = (B < A);              // true

// 检查有效性
if (Time.IsValid()) { /* 有效 */ }
if (Time.IsZero()) { /* 为零 */ }
if (Time.IsInfinity()) { /* 无穷大 */ }
```

### 基本用法：线程安全消息队列

```cpp
// 来源: Public/Core/MediaMessageQueue.h

// 固定容量、无超时版本
Electra::TMediaMessageQueueStaticNoTimeout<int32, 64> Queue;

// 发送消息（阻塞等待队列有空间）
Queue.SendMessage(42);

// 发送消息（队列满则立即返回 false）
bool bSent = Queue.SendMessage(42, false);

// 插入队列前端（高优先级消息）
Queue.JamMessage(99);

// 无阻塞接收（检查是否有待处理消息）
int32 Msg;
if (Queue.ReceiveMessage(Msg))
{
    // 处理消息
}

// 阻塞接收（等待直到有消息）
int32 BlockingMsg = Queue.ReceiveMessage();

// 带超时接收（仅 WithTimeout 版本支持）
Electra::TMediaMessageQueueStaticWithTimeout<int32, 64> TimeoutQueue;
int32 TimedMsg;
if (TimeoutQueue.ReceiveMessage(TimedMsg, 1000000))  // 等待最多 1 秒（微秒）
{
    // 在超时前收到消息
}

// 查询状态
bool bEmpty = Queue.HaveMessage() == false;
SIZE_T Count = Queue.NumWaitingMessages();
```

### 基本用法：参数字典

```cpp
// 来源: Public/ParameterDictionary.h

// 单线程版本
Electra::FParamDict Params;

// 设置各种类型的值
Params.Set(FName("Url"), Electra::FVariantValue(FString("https://example.com/video.mp4")));
Params.Set(FName("Bitrate"), Electra::FVariantValue((int64)5000000));
Params.Set(FName("Duration"), Electra::FVariantValue(120.5));
Params.Set(FName("IsLive"), Electra::FVariantValue(true));

// 读取值（类型必须匹配，否则返回空/零值）
FString Url = Params.GetValue(FName("Url")).GetFString();

// 安全读取（类型不匹配时返回默认值）
int64 Bitrate = Params.GetValue(FName("Bitrate")).SafeGetInt64(0);
double Duration = Params.GetValue(FName("Duration")).SafeGetDouble(0.0);

// 检查键是否存在
if (Params.HaveKey(FName("Url")))
{
    // ...
}

// 获取所有键
TArray<FName> Keys;
Params.GetKeys(Keys);

// 线程安全版本（用法完全相同）
Electra::FParamDictTS ThreadSafeParams;
ThreadSafeParams.Set(FName("Url"), Electra::FVariantValue(FString("...")));
FString SafeUrl = ThreadSafeParams.GetValue(FName("Url")).GetFString();
```

### 基本用法：比特流读取

```cpp
// 来源: Public/Utilities/ElectraBitstream.h

// 从内存缓冲区创建比特流读取器
const uint8* Data = /* ... */;
uint64 DataSize = /* ... */;
Electra::FBitstreamReader Reader(Data, DataSize);

// 读取指定比特数（最多 32 位）
uint32 NALUType = Reader.GetBits(5);
uint32 Profile = Reader.GetBits(8);
uint32 Flags = Reader.GetBits(16);

// 读取 64 位值
uint64 LargeValue = Reader.GetBits64(40);

// 预读（不移动读取位置）
uint32 Preview = Reader.PeekBits(8);

// 跳过比特/字节
Reader.SkipBits(3);
Reader.SkipBytes(10);

// 检查是否字节对齐
if (Reader.IsByteAligned())
{
    // 读取对齐的字节
    uint8 Buffer[16];
    Reader.GetAlignedBytes(Buffer, 16);
}

// 查询剩余数据
uint64 RemainingBits = Reader.GetRemainingBits();
uint64 RemainingBytes = Reader.GetRemainingByteLength();
```

### 进阶用法：URL 解析与解析

```cpp
// 来源: Public/Utilities/URLParser.h

Electra::FURL_RFC3986 URL;
URL.Parse("https://cdn.example.com:8080/path/to/segment.ts?token=abc&quality=high#fragment");

// 获取各部分
FString Scheme = URL.GetScheme();   // "https"
FString Host = URL.GetHost();       // "cdn.example.com"
FString Port = URL.GetPort();       // "8080"
FString Path = URL.GetPath();       // "/path/to/segment.ts"
FString Query = URL.GetQuery();     // "token=abc&quality=high"

// 解析查询参数
TArray<Electra::FURL_RFC3986::FQueryParam> QueryParams;
URL.GetQueryParams(QueryParams, true);  // true = 进行 URL 解码
// QueryParams[0] = { Name: "token", Value: "abc" }
// QueryParams[1] = { Name: "quality", Value: "high" }

// 相对 URL 解析（HLS/DASH 场景中常见）
Electra::FURL_RFC3986 BaseURL;
BaseURL.Parse("https://cdn.example.com/hls/master.m3u8");

Electra::FURL_RFC3986 SegmentURL;
SegmentURL.Parse("../segment/seg_001.ts");
SegmentURL.ResolveAgainst("https://cdn.example.com/hls/master.m3u8");
// 结果: https://cdn.example.com/segment/seg_001.ts

// 修改查询参数
TArray<Electra::FURL_RFC3986::FQueryParam> NewParams;
NewParams.Add({TEXT("token"), TEXT("new_token_value")});
URL.AddOrUpdateQueryParams(NewParams);

// 检查同源
bool bSameOrigin = URL.HasSameOriginAs(BaseURL);
```

### 进阶用法：编解码器格式信息

```cpp
// 来源: Public/CodecTypeFormat.h

Electra::FCodecTypeFormat CodecInfo;
CodecInfo.Type = Electra::FCodecTypeFormat::EType::Video;
CodecInfo.RFC6381 = TEXT("avc1.64001f");
CodecInfo.MimeType = TEXT("video/mp4");
CodecInfo.FourCC = Electra::Utils::Make4CC('a','v','c','1');
CodecInfo.Bitrate = 5000000;

// 设置视频属性
Electra::FCodecTypeFormat::FVideo VideoProps;
VideoProps.Width = 1920;
VideoProps.Height = 1080;
VideoProps.FrameRate = FFrameRate(30000, 1001);  // 29.97fps
VideoProps.BitDepth = 8;
VideoProps.AspectRatioW = 16;
VideoProps.AspectRatioH = 9;

// 设置 profile 信息
VideoProps.Profile.Tier = 0;
VideoProps.Profile.Profile = 100;  // High profile
VideoProps.Profile.Level = 31;     // Level 3.1
VideoProps.Profile.Constraints = 0;

// 设置颜色信息
Electra::FCodecTypeFormat::FVideo::FColorInfo ColorInfo;
ColorInfo.colourPrimaries = 1;      // BT.709
ColorInfo.transferCharacteristics = 1; // BT.709
ColorInfo.matrixCoefficients = 1;   // BT.709
ColorInfo.videoFullRangeFlag = 0;
VideoProps.OptColorInfo = ColorInfo;

CodecInfo.Properties.Set<Electra::FCodecTypeFormat::FVideo>(VideoProps);
```

### 进阶用法：线程封装

```cpp
// 来源: Public/Core/MediaThreads.h

// 方法一：使用 FMediaThread 作为成员变量
class FMyMediaProcessor
{
    Electra::FMediaThread WorkerThread;

    void StartProcessing()
    {
        WorkerThread.ThreadSetPriority(TPri_Normal);
        WorkerThread.ThreadSetCoreAffinity(2);  // 绑定到核心 2
        WorkerThread.ThreadWaitDoneOnDelete(true);  // 析构时自动等待
        WorkerThread.ThreadStart(Electra::FMediaRunnable::FStartDelegate::CreateRaw(
            this, &FMyMediaProcessor::WorkerLoop));
    }

    void WorkerLoop()
    {
        while (!bShouldStop)
        {
            // 处理媒体数据...
        }
    }

    void StopProcessing()
    {
        bShouldStop = true;
        WorkerThread.ThreadWaitDone();
    }

    bool bShouldStop = false;
};

// 方法二：使用 FMediaSemaphore 进行线程同步
Electra::FMediaSemaphore Semaphore(0);  // 初始计数为 0

// 生产者线程
Semaphore.Release();  // 信号 +1

// 消费者线程
if (Semaphore.Obtain(5000000))  // 等待最多 5 秒
{
    // 成功获取信号
}

// 非阻塞尝试
if (Semaphore.TryToObtain())
{
    // 立即获取成功
}
```

## Demo 示例

以下示例展示如何使用 ElectraBase 的核心工具类构建一个简单的媒体时间管理器：

**MediaTimeManager.h**

```cpp
#pragma once

#include "PlayerTime.h"
#include "ParameterDictionary.h"
#include "MediaMessageQueue.h"
#include "MediaThreads.h"

class FMediaTimeManager
{
public:
    FMediaTimeManager();
    ~FMediaTimeManager();

    // 设置媒体时长和帧率
    void Initialize(double DurationSeconds, FFrameRate FrameRate);

    // 设置当前播放时间（从播放线程调用）
    void SetCurrentTime(const Electra::FTimeValue& InTime);

    // 查询当前播放时间（从任意线程调用）
    Electra::FTimeValue GetCurrentTime() const;

    // 设置轨道元数据（线程安全）
    void SetTrackProperty(const FName& Key, const Electra::FVariantValue& Value);

    // 获取轨道元数据（线程安全）
    Electra::FVariantValue GetTrackProperty(const FName& Key) const;

private:
    void WorkerThread();

    Electra::FTimeValue MediaDuration;
    FFrameRate MediaFrameRate;
    Electra::FTimeValue CurrentTime;

    Electra::FParamDictTS TrackProperties;
    Electra::TMediaMessageQueueStaticNoTimeout<int32, 16> CommandQueue;
    Electra::FMediaThread UpdateThread;
    Electra::FMediaSemaphore StopSignal;

    std::atomic<bool> bRunning{false};
};
```

**MediaTimeManager.cpp**

```cpp
#include "MediaTimeManager.h"

FMediaTimeManager::FMediaTimeManager()
{
}

FMediaTimeManager::~FMediaTimeManager()
{
    if (bRunning.load())
    {
        bRunning.store(false);
        StopSignal.Release();
        UpdateThread.ThreadWaitDone();
    }
}

void FMediaTimeManager::Initialize(double DurationSeconds, FFrameRate InFrameRate)
{
    MediaDuration.SetFromSeconds(DurationSeconds);
    MediaFrameRate = InFrameRate;
    CurrentTime.SetToZero();

    // 设置帧率信息到轨道属性
    TrackProperties.Set(FName("FrameRate"),
        Electra::FVariantValue(MediaFrameRate));

    // 启动后台更新线程
    bRunning.store(true);
    UpdateThread.ThreadSetName("MediaTimeManager");
    UpdateThread.ThreadSetPriority(TPri_Normal);
    UpdateThread.ThreadWaitDoneOnDelete(true);
    UpdateThread.ThreadStart(
        Electra::FMediaRunnable::FStartDelegate::CreateRaw(
            this, &FMediaTimeManager::WorkerThread));
}

void FMediaTimeManager::SetCurrentTime(const Electra::FTimeValue& InTime)
{
    CurrentTime = InTime;
}

Electra::FTimeValue FMediaTimeManager::GetCurrentTime() const
{
    return CurrentTime;
}

void FMediaTimeManager::SetTrackProperty(const FName& Key,
    const Electra::FVariantValue& Value)
{
    TrackProperties.Set(Key, Value);
}

Electra::FVariantValue FMediaTimeManager::GetTrackProperty(const FName& Key) const
{
    return TrackProperties.GetValue(Key);
}

void FMediaTimeManager::WorkerThread()
{
    while (bRunning.load())
    {
        // 尝试接收命令（非阻塞）
        int32 Cmd;
        if (CommandQueue.ReceiveMessage(Cmd))
        {
            // 处理命令
        }

        // 用信号量等待一小段时间，避免忙等
        StopSignal.Obtain();
        if (bRunning.load())
        {
            // 被唤醒检查是否需要停止
            // 或者是由其他线程触发的信号
        }
    }
}
```

## 模块依赖

从源码分析和模块结构提取的依赖关系：

| 模块 | 用途 |
|---|---|
| `DirectX` | ElectraSamples 模块依赖，用于视频样本的 DirectX 纹理支持 |

无特殊依赖（仅标准 Core/Engine/Slate 等基础模块）。ElectraBase 模块本身仅依赖 UE 核心模块（Core、CoreUObject、Engine），所有线程原语和数据结构均基于 UE 平台抽象层实现。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `bc37b7ea` | ElectraUtil: added stub methods for server builds to prevent linker errors when this class is accide | 为服务器构建添加桩方法，防止意外链接时出现错误 |
| 2026-04-23 | `efcad028` | HDR: Fix HDR normalization factor across media causing incorrect brightness levels going from/to the | 修复跨媒体 HDR 归一化因子导致亮度异常的问题 |
| 2026-04-20 | `3ed2062b` | ElectraDecoders: modernized the decoder factory to be more usable for other clients | 现代化解码器工厂接口，便于其他客户端使用 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 宏 |
| 2026-03-25 | `2924c4cc` | [ElectraUtil] Fix timecode subframe precision loss in CreateTimecodeFromMPEGDefinition | 修复 MPEG 时间码子帧精度丢失问题 |

### 维护评价

- **活跃维护**：最近一次更新在 2026 年 5 月，近 3 个月内有多次功能性更新
- **核心基础设施**：作为 Electra 媒体播放系统的基础层，被多个上层插件依赖，不太可能被废弃
- **更新内容健康**：近期更新涵盖 bug 修复（HDR、时间码精度）、架构改进（解码器工厂现代化）和平台适配（服务器构建兼容性）
- **Epic 官方维护**：由 Epic Games 直接维护，跟随 UE 主版本持续迭代
- **推荐使用**：如果你在开发 Electra 相关的媒体功能扩展，这是必须依赖的基础库。对于独立的媒体功能，建议评估是否真的需要这些底层工具，还是 UE 内置的 `FMediaTimeStamp`、`FCriticalSection` 等标准类型已能满足需求

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraUtil)
- [官方文档](https://docs.unrealengine.com/en-US/Engine/MediaFramework/Overview)