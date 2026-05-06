# Metasounds Experimental

> Metasound developmental plugin, for new features before they are ready for prime time

| 属性 | 值 |
|---|---|
| 中文名 | Metasound 实验性功能 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、MetaSound 节点、编辑器工具） |
| 模块 | `AudioExperimentalRuntime` (Runtime), `MetasoundExperimentalRuntime` (Runtime), `MetasoundExperimentalEngineRuntime` (Runtime), `MetasoundExperimentalEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-05 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MetasoundExperimental) | |

## 用途

本插件为 MetaSound 系统的预发布特性提供实验性基础设施。核心关注点包括：

- **通道无关的音频处理**：通过 `FChannelAgnosticType` 提供与通道布局（离散、Ambisonics）无关的音频缓冲区，允许节点在不关心具体通道数的情况下处理音频数据。
- **类型家族系统**：定义 `FChannelTypeFamily` 层次结构及寄存器，支持运行时类型查询与安全的向下转型。
- **简化内存分配器**：提供 `FSimpleLinearAllocator` 和 `FSimpleHeapAllocator`，用于高频、短生命周期的音频内存分配，避免全局堆压力。
- **通道转码**：在离散通道与 Ambisonics 通道之间提供灵活的转码器生成机制，支持通道丢弃、混合/上混等策略。

此插件解决了 MetaSound 在发展中遇到的 **通道布局多样性** 和 **内存管理效率** 问题，为后续正式功能（如新的 MetaSound 节点、效果器）提供了底层基础。

## 使用场景

- 编写自定义 MetaSound 节点时，需要处理不同通道布局（2.0、5.1、Ambisonics 等），希望用同一份代码兼容多种格式。
- 开发需要频繁分配/释放临时音频缓冲区的 DSP 处理代码，使用 `FSimpleLinearAllocator` 减少 `new/delete` 开销。
- 需要在运行时判断两个音频缓冲区是否为同类通道类型，或获取其具体类型名。

## 蓝图用法

此插件为纯 C++ 运行时模块，**未暴露任何 BlueprintCallable 函数**。所有功能仅能通过 C++ 使用。

（插件包含的蓝图资产可能提供可直接使用的 MetaSound 节点，但不在本文档讨论范围内。）

## C++ 用法

### 头文件引入

```cpp
#include "ChannelAgnostic/ChannelAgnosticType.h"
#include "ChannelAgnostic/ChannelAgnosticTranscoding.h"
#include "SimpleAlloc/SimpleLinearAllocator.h"
#include "TypeFamily/ChannelTypeFamily.h"
```

### 基本用法

**1. 创建通道无关音频缓冲区**

```cpp
#include "ChannelAgnostic/ChannelAgnosticType.h"
#include "TypeFamily/ChannelTypeFamily.h"

using namespace Audio;

// 假设已有一个 FDiscreteChannelTypeFamily 实例（例如立体声）
FDiscreteChannelTypeFamily StereoType; // 简化示例，实际需从注册表获取

int32 NumFrames = 512;
FChannelAgnosticType AudioBuffer(StereoType, NumFrames);
AudioBuffer.Zero(); // 清零

// 访问单个声道
TArrayView<float> LeftChannel = AudioBuffer.GetChannel(0);
LeftChannel[0] = 0.5f; // 设置第一帧左声道值
```

*来源: `ChannelAgnosticType.h`*

**2. 使用线性分配器**

```cpp
#include "SimpleAlloc/SimpleLinearAllocator.h"

// 预分配一个 64KB 的堆内存页
FSimpleLinearAllocatorFromHeap Allocator(64 * 1024);

// 在 Allocator 上创建 ScratchBuffer（临时音频缓冲区）
TScratchBuffer<float> TempBuffer(256, &Allocator);
// ... 使用 TempBuffer 进行 DSP 处理
// 处理完成后，调用 Reset() 重用内存
Allocator.Reset();
```

*来源: `SimpleLinearAllocator.h`, `ScratchBuffer.h`*

**3. 获取离散通道与 Ambisonics 之间的转码器**

```cpp
#include "ChannelAgnostic/ChannelAgnosticTranscoding.h"

const FDiscreteChannelTypeFamily& FromType = ...;
const FAmbisonicsChannelTypeFamily& ToType = ...;

FChannelTypeFamily::FGetTranscoderParams Params;
Params.FromType = FromType;
Params.ToType   = ToType;

FChannelTypeFamily::FTranscoder Transcoder = GetTranscoder(FromType, ToType, Params);

// 应用转码器（具体调用方式取决于 Transcode 的实现）
Transcoder(/* 输入缓冲区, 输出缓冲区 */);
```

*来源: `ChannelAgnosticTranscoding.h`*

### 进阶用法

**组合使用：将通道无关缓冲区转换为交错格式**

```cpp
#include "ChannelAgnostic/ChannelAgnosticTypeUtils.h"

FChannelAgnosticType DeinterleavedBuffer(...);
TArray<float> InterleavedData(DeinterleavedBuffer.NumFrames() * DeinterleavedBuffer.NumChannels());
FCatUtils::Interleave(DeinterleavedBuffer, InterleavedData);
```

*来源: `ChannelAgnosticTypeUtils.h`*

## Demo 示例

以下是一个最小 C++ 示例，演示如何创建并填充一个立体声通道无关缓冲区：

**Demo.h**
```cpp
#pragma once
#include "CoreMinimal.h"

void RunAudioBufferDemo();
```

**Demo.cpp**
```cpp
#include "Demo.h"
#include "ChannelAgnostic/ChannelAgnosticType.h"
#include "TypeFamily/ChannelTypeFamily.h"

void RunAudioBufferDemo()
{
    using namespace Audio;

    // 简单示例：直接创建 FDiscreteChannelTypeFamily 的实例（实际应通过注册表获取）
    FDiscreteChannelTypeFamily Stereo(2, TEXT("Stereo"), TEXT("Stereo 2.0"), /*Parent*/ nullptr);
    FChannelAgnosticType Buffer(Stereo, 1024);
    Buffer.Zero();

    // 填充左声道为正弦波
    TArrayView<float> Left = Buffer.GetChannel(0);
    for (int32 i = 0; i < Left.Num(); ++i)
    {
        Left[i] = FMath::Sin(2.f * PI * i / 1024.f);
    }

    UE_LOG(LogTemp, Log, TEXT("Buffer type: %s, frames: %d, channels: %d"),
        *Buffer.GetTypeName().ToString(),
        Buffer.NumFrames(),
        Buffer.NumChannels());
}
```

编译要求：链接模块 `AudioExperimentalRuntime`。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Metasound` | MetaSound 核心框架，提供节点系统、类型注册表等 |
| `CoreUObject` | 基础 UObject 支持（模块自动引用） |

（其余如 Core、Engine 为标准依赖，此处省略。）

## 维护状态

### 近期更新

- 2025-09-30 `3a283b32` [MetaSound Experimental] Fade Node unit test fix
- 2025-08-21 `51079168` Improve metasound node registration association with modules
- 2025-08-15 `38229d1b` Metasound LOCTEXT fixups
- 2025-08-05 `da28318e` [Metasound Experimental] Addressed minor optimization feedback
- 2025-08-05 `4c1309f1` [Metasound Experimental] - Added Fade Node

### 维护评价

该插件创建于 2025 年 8 月，属于**全新实验性插件**。最新一次更新在 2025 年 9 月底，表明仍在积极开发中。提交内容包含功能新增（Fade Node）和优化修复，未见废弃标记。但由于处于实验阶段，**API 可能随时变更**，不建议在正式项目中使用。适合紧跟干线版本并愿意承担重构风险的开发者。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MetasoundExperimental)
- [官方文档]（暂无稳定文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MetasoundExperimental/Source/AudioExperimentalRuntime/Private/Tests)（假设存在，实际路径可能不同）