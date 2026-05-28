# Electra Player Utilities

> Reusable Base Components for Electra Player Media Playback

| 属性 | 值 |
|---|---|
| 中文名 | Electra工具库 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ElectraBase` (Runtime), `ElectraSamples` (Runtime), `ElectraHTTPStream` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-01-06 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraUtil) | |

## 用途

ElectraUtil 并非一个功能完整的媒体播放器插件，而是为 Unreal Engine 的 “Electra” 媒体播放器系统提供底层的、可重用的基础组件。它包含了一系列用于媒体流处理的核心工具类，例如线程安全的消息队列、参数字典、高精度时间值、位流读写器、URL解析器以及各类解码器输出数据结构的定义。该插件解决了在实现高性能、多线程媒体播放器时所需的底层基础设施问题，是构建更高级 Electra 播放器模块（如解复用器、解码器、HTTP 流处理器）的基石。

## 使用场景

- 你需要**开发自定义的媒体播放器或流媒体协议支持**，需要底层的线程间通信、数据解析和状态管理工具时。
- 你的项目需要**集成或扩展 Electra 媒体播放框架**，利用其提供的标准化解码器输出接口、时间码处理或 HDR 元数据结构。
- 你在**处理媒体流数据**，需要用到符合 RFC 标准的 URL 解析（RFC 3986）、BCP47 语言标签解析（RFC 5646）或 MPEG ES 描述符解析等功能。

## 蓝图用法

该插件主要为 C++ 层设计，提供了底层的运行时组件和工具类，**没有暴露任何用于蓝图的 `UFUNCTION` 节点**。所有核心功能均需通过 C++ API 进行访问。

## C++ 用法

### 头文件引入

根据你使用的具体功能，引入相应的头文件。例如：

```cpp
// 使用媒体消息队列
#include "Core/MediaMessageQueue.h"
// 使用参数字典
#include "ParameterDictionary.h"
// 使用时间值类
#include "PlayerTime.h"
// 使用位流读取器
#include "Utilities/ElectraBitstream.h"
```

### 基本用法

以下示例展示了如何使用 `TMediaMessageQueueWithTimeout` 在多线程间安全地传递数据。

```cpp
// 来源：Source/ElectraBase/Public/Core/MediaMessageQueue.h

// 定义一个传递整数 ID 的消息队列，最大容量为 100
Electra::TMediaMessageQueueWithTimeout<int32> MessageQueue(100);

// --- 生产者线程 ---
// 发送一个消息，如果队列满则阻塞等待
int32 NewDataID = 42;
MessageQueue.SendMessage(NewDataID);

// --- 消费者线程 ---
// 等待最多 1000000 微秒（1秒）来接收消息
int32 ReceivedID = 0;
if (MessageQueue.ReceiveMessage(ReceivedID, 1000000))
{
    // 成功接收到消息
    UE_LOG(LogTemp, Log, TEXT("Received ID: %d"), ReceivedID);
}
```

### 进阶用法

以下示例结合使用 `FTimeValue` 进行高精度时间计算，以及 `FBitstreamReader` 解析一段二进制数据头。

```cpp
// 来源：Source/ElectraBase/Public/PlayerTime.h, Source/ElectraBase/Public/Utilities/ElectraBitstream.h

// 1. 时间计算
Electra::FTimeValue StartTime;
StartTime.SetFromSeconds(10.5); // 设置为 10.5 秒

Electra::FTimeValue Duration;
Duration.SetFromMilliseconds(2500); // 设置为 2500 毫秒

Electra::FTimeValue EndTime = StartTime + Duration; // 计算结束时间
double EndTimeInSeconds = EndTime.GetAsSeconds(); // 结果为 13.0 秒

// 2. 解析二进制数据头（例如，解析一个简单的 32 位长度头）
const uint8 RawData[] = { 0x00, 0x00, 0x01, 0x00 }; // 表示 256
Electra::FBitstreamReader BitReader(RawData, sizeof(RawData));

// 读取前 16 位（一个无符号短整型）
uint32 HeaderLength = BitReader.GetBits(16); // 结果为 0
// 再读取后 16 位
HeaderLength = (HeaderLength << 16) | BitReader.GetBits(16); // 结果为 256
```

## Demo 示例

下面是一个最小的控制台应用程序示例，演示了如何创建一个带超时的消息队列，并使用 `FTimeValue` 计算媒体片段的持续时间。

```cpp
// MediaUtilExample.h
#pragma once
#include "CoreMinimal.h"
#include "Core/MediaMessageQueue.h"
#include "PlayerTime.h"

namespace ElectraDemo
{
    void RunMessageQueueDemo();
    void RunTimeValueDemo();
}
```

```cpp
// MediaUtilExample.cpp
#include "MediaUtilExample.h"
#include "Misc/DateTime.h"

namespace ElectraDemo
{
    void RunMessageQueueDemo()
    {
        // 创建一个容量为 10，支持超时的字符串消息队列
        Electra::TMediaMessageQueueWithTimeout<FString> Queue(10);

        // 模拟生产者发送一条消息
        FString Greeting = TEXT("Hello, Electra!");
        Queue.SendMessage(Greeting);

        // 模拟消费者接收，设置 0.5 秒超时
        FString Received;
        if (Queue.ReceiveMessage(Received, 500000))
        {
            UE_LOG(LogTemp, Log, TEXT("Queue Demo - Received: %s"), *Received);
        }
        else
        {
            UE_LOG(LogTemp, Warning, TEXT("Queue Demo - Receive timed out."));
        }
    }

    void RunTimeValueDemo()
    {
        // 假设一个媒体片段的 PTS（显示时间戳）和持续时间
        Electra::FTimeValue SegmentPTS;
        SegmentPTS.SetFrom90kHz(81000); // 90kHz 时钟下的 81000 个时钟周期

        Electra::FTimeValue SegmentDuration;
        SegmentDuration.SetFromMilliseconds(3333); // 约 30fps 的帧时长

        Electra::FTimeValue SegmentEnd = SegmentPTS + SegmentDuration;

        UE_LOG(LogTemp, Log, TEXT("Time Demo - Segment starts at %.4f sec, ends at %.4f sec, duration is %.4f sec."),
            SegmentPTS.GetAsSeconds(),
            SegmentEnd.GetAsSeconds(),
            SegmentDuration.GetAsSeconds());
    }
}
```

## 模块依赖

该插件本身是媒体播放器的底层依赖。若要在你的模块中使用其提供的类，通常需要依赖 `ElectraBase` 模块。

| 模块 | 用途 |
|---|---|
| `Engine` | `ElectraSamples` 模块依赖，用于访问引擎核心功能 |
| `DirectX` | `ElectraSamples` 模块依赖，用于 DirectX 相关的媒体样本处理 |

对于 `ElectraBase` 和 `ElectraHTTPStream`，它们的依赖主要是 UE 核心模块，无需额外特殊依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `bc37b7ea` | ElectraUtil: added stub methods for server builds to prevent linker errors when this class is accide | 为服务端构建添加存根方法，防止意外链接时出错 |
| 2026-04-23 | `efcad028` | HDR: Fix HDR normalization factor across media causing incorrect brightness levels going from/to the | 修复跨媒体 HDR 归一化因子导致亮度不正确的问题 |
| 2026-04-20 | `3ed2062b` | ElectraDecoders: modernized the decoder factory to be more usable for other clients | 现代化解码器工厂，使其对其他客户端更易用 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移至 UE_LOGF |
| 2026-03-25 | `2924c4cc` | [ElectraUtil] Fix timecode subframe precision loss in CreateTimecodeFromMPEGDefinition | 修复 CreateTimecodeFromMPEGDefinition 中时间码子帧精度损失 |

### 维护评价

ElectraUtil 插件自 2021 年创建以来，持续获得更新，最近一次更新在 2026 年 5 月。从提交记录看，开发团队仍在积极维护和改进该插件，包括修复 HDR 显示问题、提升解码器工厂的易用性以及修复时间码精度等实质性功能更新。该插件作为 Electra 媒体框架的基石，具有较高的稳定性和持续维护保障，**推荐在需要底层媒体处理能力时使用**。不过需注意，其默认未启用，且主要为 C++ 开发者设计。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraUtil)
- [官方文档](https://docs.unrealengine.com/en-US/Engine/MediaFramework/Overview)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraUtil/Tests) (如果存在)