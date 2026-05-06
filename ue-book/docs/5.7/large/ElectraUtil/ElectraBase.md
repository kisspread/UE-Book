# Electra Player Utilities

> Reusable Base Components for Electra Player Media Playback

| 属性 | 值 |
|---|---|
| 中文名 | Electra 播放器工具库 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ElectraBase` (RuntimeNoCommandlet), `ElectraSamples` (RuntimeNoCommandlet), `ElectraHTTPStream` (RuntimeNoCommandlet) |
| 实验性 | 否 |
| 创建时间 | 2025-09-24 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/ElectraUtil) | |

## 用途

`ElectraUtil` 插件为 Electra 媒体播放器提供了一组可复用的底层基础组件。它包含三个模块：

- **ElectraBase**：核心基础库，提供线程安全工具（事件、信号量、锁、队列、线程管理）、媒体时间处理（`FTimeValue`）、数据解析（MP4 box、Bitstream、URL、BCP47 语言标签、ISO 8601 时间）以及解码输出接口（视频/音频/字幕/元数据）。
- **ElectraSamples**：媒体样本解码输出缓冲区管理，支持 GPU 纹理处理。
- **ElectraHTTPStream**：用于媒体流式传输的 HTTP 流处理。

该插件本身不提供直接可用的播放器 UI 或蓝图节点，而是作为 Electra 播放器各模块的共享底层，降低代码冗余并保证跨模块一致性。

## 使用场景

- **自定义媒体播放器开发**：你需要基于 Electra 框架构建一个媒体播放器，可以用 `ElectraBase` 中的线程安全队列、事件、信号量来实现高效的多线程解码流水线。
- **MP4 文件解析**：需要解析 ISOBMFF (MP4) 文件结构时，可使用 `UtilitiesMP4` 命名空间下的 MP4 box 类。
- **时间值处理**：处理媒体时间戳（PTS/DTS）时，推荐使用 `Electra::FTimeValue` 而非原生 `FTimespan`，它支持不同时间精度的转换和正无穷/负无穷表示。
- **URL 操作**：流媒体 URL 的重定向、参数修改、相对 URL 解析等场景，可利用 `Electra::FURL_RFC3986`。

## 蓝图用法

ElectraBase 模块不提供任何蓝图可调用函数。所有 API 均为 C++ 级别。

| 节点 | 说明 | 所在类 |
|---|---|---|
| 无 | 该模块无蓝图暴露节点 | — |

## C++ 用法

### 头文件引入

ElectraBase 的核心工具分布在不同的头文件中：

```cpp
#include "Core/MediaEventSignal.h"      // FMediaEvent
#include "Core/MediaSemaphore.h"        // FMediaSemaphore
#include "Core/MediaLock.h"             // FMediaLockCriticalSection, FMediaLockNone
#include "Core/MediaQueue.h"            // TMediaQueue
#include "Core/MediaMessageQueue.h"     // TMediaMessageQueueNoTimeout
#include "Core/MediaThreads.h"          // FMediaRunnable
#include "Core/MediaTypes.h"            // UEMediaError, Electra::TSharedPtrTS
#include "PlayerTime.h"                 // Electra::FTimeValue
#include "Utilities/URLParser.h"        // Electra::FURL_RFC3986
#include "Utilities/MP4Boxes/MP4Boxes.h"// Electra::UtilitiesMP4::FMP4BoxBase
#include "Utilities/BCP47-Helpers.h"    // Electra::BCP47::FLanguageTag
#include "MediaVideoDecoderOutput.h"    // IVideoDecoderColorimetry, IVideoDecoderHDRInformation
```

### 基本用法

#### 事件信号 (FMediaEvent)

用于线程间的单次信号通知，类似于手动重置事件。

```cpp
#include "Core/MediaEventSignal.h"

FMediaEvent DoneEvent;

// 工作线程完成时触发
DoneEvent.Signal();

// 主线程等待完成（阻塞）
DoneEvent.Wait();

// 带超时的等待（微秒）
bool bSignaled = DoneEvent.WaitTimeout(5000000);  // 5秒

// 等待并自动重置
DoneEvent.WaitAndReset();
```

#### 信号量 (FMediaSemaphore)

用于限制资源访问容量。

```cpp
#include "Core/MediaSemaphore.h"

FMediaSemaphore Semaphore(3);  // 初始计数3

// 获取一个资源（阻塞）
Semaphore.Obtain();

// 尝试获取，超时5秒
bool bGot = Semaphore.Obtain(5000000);

// 尝试获取（不阻塞）
bool bTry = Semaphore.TryToObtain();

// 释放一个资源
Semaphore.Release();
```

#### 消息队列 (TMediaMessageQueueNoTimeout)

多生产者、单消费者模式的线程安全队列。

```cpp
#include "Core/MediaMessageQueue.h"

using MyQueue = TMediaMessageQueueNoTimeout<FString>;
MyQueue Queue(100);  // 最大100条消息

// 发送消息（若队列满则阻塞）
Queue.SendMessage(TEXT("Hello"));

// 接收消息（阻塞）
FString Msg = Queue.ReceiveMessage();

// 非阻塞接收
FString Out;
bool bReceived = Queue.ReceiveMessage(Out);
```

#### 线程管理 (FMediaRunnable)

轻量级线程封装，适合媒体解码等工作线程。

```cpp
#include "Core/MediaThreads.h"

// 创建工作线程（指定核心亲和性、优先级、栈大小、线程名）
FMediaRunnable* Runnable = FMediaRunnable::Create(
    -1,                           // 核心亲和性：-1表示不限制
    TPri_Normal,
    65536,
    TEXT("MediaDecoder")
);

// 设置入口委托
FMediaRunnable::FStartDelegate Entry;
Entry.BindLambda([]()
{
    // 线程执行体
    while (/* condition */) { }
});
Runnable->Start(Entry);

// 等待线程完成（可选）
FMediaEvent Done;
Runnable->SetDoneSignal(&Done);
// ... 在其他地方等待 Done

// 销毁
FMediaRunnable::Destroy(Runnable);
```

#### 时间值 (FTimeValue)

统一媒体时间表示，可转换为 HNS（百纳秒）、秒、分数等。

```cpp
#include "PlayerTime.h"

using namespace Electra;

// 从秒构造
FTimeValue Time1(30.5);  // 30.5秒

// 从分数构造（分子/分母）
FTimeValue Time2(300, 1); // 300秒

// 从 HNS 构造
FTimeValue Time3(FTimeValue::MillisecondsToHNS(1500)); // 1.5秒

// 正无穷/无效/零
FTimeValue Infinity = FTimeValue::GetPositiveInfinity();
FTimeValue Invalid = FTimeValue::GetInvalid();
FTimeValue Zero = FTimeValue::GetZero();

// 获取秒数
double Seconds = Time1.GetAsSeconds();  // 30.5

// 获取 HNS
int64 HNS = Time1.GetAsHNS();  // 305000000

// 比较
if (Time1 > Time2) { }
```

#### URL 解析 (FURL_RFC3986)

遵循 RFC 3986 的 URL 处理。

```cpp
#include "Utilities/URLParser.h"

Electra::FURL_RFC3986 Url;
if (Url.Parse(TEXT("http://example.com/path/to/file.m3u8?token=abc#frag")))
{
    FString Scheme = Url.GetScheme();      // "http"
    FString Host = Url.GetHost();          // "example.com"
    FString Path = Url.GetPath();          // "/path/to/file.m3u8"
    FString Query = Url.GetQuery();        // "token=abc"
    FString Frag = Url.GetFragment();      // "frag"
}

// 解析相对 URL
FURL_RFC3986 Base;
Base.Parse(TEXT("http://example.com/video/"));
Base.ResolveWith(TEXT("subdir/clip.mp4"));
// Base 变为 "http://example.com/video/subdir/clip.mp4"
```

### 进阶用法

#### MP4 文件解析

`UtilitiesMP4` 提供了一个完整的 ISOBMFF 解析器，可递归解析 box 结构。

```cpp
#include "Utilities/MP4Boxes/MP4Boxes.h"
#include "Utilities/MP4Boxes/MP4Track.h"

// 假设有一个 IBaseDataReader 对象指向 MP4 文件
TSharedPtr<Electra::UtilitiesMP4::FMP4BoxMOOV> MoovBox;

// 从文件中解析 moov box（具体解析逻辑需自行实现，参考 Electra 内部代码）
// ...

// 获取轨道列表
TArray<TSharedPtr<Electra::UtilitiesMP4::FMP4BoxTRAK>> Tracks;
MoovBox->GetAllBoxInstances(Tracks, Electra::UtilitiesMP4::MakeBoxAtom('t','r','a','k'));

// 创建轨道迭代器
for (auto& Trak : Tracks)
{
    auto Track = Electra::UtilitiesMP4::FMP4Track::Create(Trak);
    Track->Prepare(/* fullMovieDuration */, /* adjustedDuration */);

    auto& Iterator = Track->GetIterator();
    while (Iterator.IsValid())
    {
        uint32 SampleNum = Iterator.GetSampleNumber();
        int64 DTS = Iterator.GetDTS().GetAsHNS();
        int64 PTS = Iterator.GetEffectivePTS().GetAsHNS();
        int64 Size = Iterator.GetSampleSize();
        // ... 处理样本
        Iterator.Next();
    }
}
```

#### 字节能流位解析 (FBitstreamReader)

用于从 MPEG 比特流中读取不定长数据。

```cpp
#include "Utilities/ElectraBitstream.h"

TArray<uint8> Data = ...;
Electra::FBitstreamReader Reader(Data.GetData(), Data.Num());

// 读取 8 位
uint8 Byte = Reader.GetBits<uint8>(8);

// 读取 1 位
uint32 Bit = Reader.GetBits(1);

// 读取无符号指数哥伦布编码（如 H.264/H.265）
uint32 Ue = Reader.GetUE();

// 读取有符号指数哥伦布编码
int32 Se = Reader.GetSE();

// 字节对齐
Reader.SkipToNextByte();
```

## Demo 示例

以下是一个使用 `ElectraBase` 的简单工作线程示例，模拟解码循环。**注意：** 需要手动启用插件（`EnabledByDefault=false`）。

### MyMediaDecoder.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Core/MediaEventSignal.h"
#include "Core/MediaThreads.h"
#include "PlayerTime.h"

class FMyMediaDecoder : public TSharedFromThis<FMyMediaDecoder>
{
public:
    FMyMediaDecoder();
    ~FMyMediaDecoder();

    void StartDecoding(const FString& InURL);
    void StopDecoding();
    bool IsDecoding() const { return bDecoding; }

private:
    void DecodeLoop();

    FMediaRunnable* Runnable;
    FMediaEvent StopEvent;
    FString URL;
    std::atomic<bool> bDecoding{false};
};
```

### MyMediaDecoder.cpp

```cpp
#include "MyMediaDecoder.h"
#include "Core/MediaLock.h"
#include "HAL/PlatformProcess.h"

FMyMediaDecoder::FMyMediaDecoder()
    : Runnable(nullptr)
{
}

FMyMediaDecoder::~FMyMediaDecoder()
{
    StopDecoding();
}

void FMyMediaDecoder::StartDecoding(const FString& InURL)
{
    if (bDecoding) return;
    URL = InURL;
    bDecoding = true;

    Runnable = FMediaRunnable::Create(-1, TPri_Normal, 65536, TEXT("DemoDecoder"));
    FMediaRunnable::FStartDelegate Delegate;
    Delegate.BindRaw(this, &FMyMediaDecoder::DecodeLoop);
    Runnable->Start(Delegate);
}

void FMyMediaDecoder::StopDecoding()
{
    if (!bDecoding) return;
    bDecoding = false;
    StopEvent.Signal();
    if (Runnable)
    {
        // 等待线程结束（可选择超时）
        FMediaEvent Done;
        Runnable->SetDoneSignal(&Done);
        Done.WaitTimeout(5000000); // 5秒超时
        FMediaRunnable::Destroy(Runnable);
        Runnable = nullptr;
    }
}

void FMyMediaDecoder::DecodeLoop()
{
    // 模拟解码帧处理
    using namespace Electra;
    FTimeValue FrameTime = FTimeValue::GetZero();
    const FTimeValue FrameDuration(1, 30); // 假设 30fps

    while (bDecoding)
    {
        // 检查停止信号
        if (StopEvent.IsSignaled())
        {
            break;
        }

        // 模拟解码一帧
        UE_LOG(LogTemp, Log, TEXT("Decoding frame at %s"), *FrameTime.GetAsString());
        FrameTime += FrameDuration;

        // 模拟解码耗时
        FPlatformProcess::Sleep(0.033f);
    }
}
```

**注意：** 使用前需在项目 `.Build.cs` 中添加 `"ElectraBase"` 依赖，并在 `ProjectSetting -> Plugins` 中启用 `Electra Player Utilities`。

## 模块依赖

| 模块 | 用途 |
|---|---|
| 无特殊依赖 | 仅依赖 Core、CoreUObject、Engine 等标准模块 |

（ElectraBase 的 Build.cs 未展示，但从头文件使用来看仅依赖 Core 等常见模块。）

## 维护状态

### 近期更新

- 2025-09-25 e601866 — ElectraUtils: Fixed check to BufferAvailable() in the DX12 buffer helpers
- 2025-09-25 83ef846 — ElectraSamples: Fixed Linux server build linker error
- 2025-09-25 916bb82 — ElectraSamples: calling ShutdownPoolable() in the destructor to avoid potential resource leaks
- 2025-09-24 241a798 — ElectraUtil: Removing hard limit of number of buffer slots in favor of dynamic resizes
- 2025-09-24 7d7c63b — ElectraUtil: fixed DX12 GPU buffer helper heap issues

### 维护评价

该插件于 **2025-09-24** 创建，年龄不足1个月，属于全新插件。最近5天内有多次功能性修复和调整（DX12 缓冲区、动态插槽、资源泄漏修复），维护非常活跃。当前版本为 1.0，未标记实验性。推荐在需要自定义 Electra 播放器时使用，但注意插件默认未启用，需手动启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/ElectraUtil)
- [官方文档](https://docs.unrealengine.com/en-US/Engine/MediaFramework/Overview)
- [ElectraSamples 模块](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/ElectraUtil/Source/ElectraSamples)
- [ElectraHTTPStream 模块](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/ElectraUtil/Source/ElectraHTTPStream)