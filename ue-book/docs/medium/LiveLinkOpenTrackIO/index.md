# Live Link Open Track IO

> Live Link plugin for supporting OpenTrackIO (https://opentrackio.org) devices in Unreal Engine or Live Link Hub.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试样本：JSON/CBOR 示例数据包） |
| 模块 | `LiveLinkOpenTrackIO` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-17 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/LiveLinkOpenTrackIO) | |

## 用途

OpenTrackIO（https://opentrackio.org）是一个开放的虚拟制作摄影机跟踪数据传输协议，定义了摄影机位姿、镜头参数（对焦/光圈/焦距）、畸变系数、时间码等数据的标准化格式。该 plugin 将 OpenTrackIO 的 UDP 数据流（支持 JSON 和 CBOR 两种编码）接入 UE 的 Live Link 系统，使用户可以在 Live Link Hub 或编辑器中接收来自外部跟踪设备（如 Mo-Sys、Stype、NCAM 等）的实时摄影机数据。

**注意**：该 plugin 仅限 `LiveLinkHub` 程序使用（`SupportedPrograms: ["LiveLinkHub"]`），无法在标准 UnrealEditor 中启用。需要在 Live Link Hub 中使用。

核心功能：
- 通过 UDP **Multicast**（默认 `239.135.1.1:55555`）或 **Unicast** 接收 OpenTrackIO 数据包
- 解析 16 字节 OpenTrackIO 协议头（含 Fletcher-16 校验和）和 JSON/CBOR payload
- 支持分段传输：大 payload 可拆分为多个 UDP 数据包，接收端自动重组
- 将 OpenTrackIO 数据映射到 Live Link 的 Lens 角色（`ULiveLinkOpenTrackIORole`，继承自 `ULiveLinkLensRole`）
- 坐标系自动转换：OpenTrackIO（Z-up、Y-forward、右手坐标系、米制）→ Unreal（Z-up、X-forward、左手坐标系、厘米）
- 镜头畸变系数转换：OpenTrackIO 的 Brown-Conrady 参数格式自动转换为 Unreal 的 OpenCV 格式
- 支持将 OpenTrackIO transform 链作为独立的 Live Link Transform Subject 输出
- 支持多路 sourceId/sourceNumber 并发流

## 使用场景

- 你在使用 LED Volume（如 Unreal Stage）进行虚拟制作，需要从外部跟踪系统（Mo-Sys StarTracker、Stype 等）接收实时摄影机位姿和镜头数据 → 使用此 plugin
- 你需要在 Live Link Hub 中聚合来自 OpenTrackIO 设备的摄影机跟踪数据 → 使用此 plugin
- 你有一个支持 OpenTrackIO 协议的跟踪设备，需要将数据传入 UE 的 CineCamera Actor → 使用此 plugin
- 你需要在蓝图中读取 OpenTrackIO 的完整数据（包括 lens 畸变、时间码、自定义 metadata 等）→ 使用此 plugin 的 Blueprint 数据结构

## 蓝图用法

该 plugin 暴露了大量 `BlueprintType` 结构体，可以在蓝图中读取 OpenTrackIO 数据。由于核心数据通过 Live Link 帧数据传递，蓝图通常通过 Live Link 蓝图接口获取数据。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetVersionString` | 从 Protocol 结构体返回版本字符串（如 "OpenTrackIO 1.0.0"） | `ULiveLinkOpenTrackIOLibrary` |

### 关键蓝图类型

| 类型 | 说明 |
|---|---|
| `FLiveLinkOpenTrackIOBlueprintData` | Live Link 蓝图数据载体，包含 StaticData 和 FrameData |
| `FLiveLinkOpenTrackIOFrameData` | 每帧数据，继承自 `FLiveLinkLensFrameData`，额外包含 `OpenTrackData` 属性 |
| `FLiveLinkOpenTrackIOData` | OpenTrackIO 完整数据结构，包含 Static、Tracker、Timing、Lens、Protocol、Transforms、Custom 等 |
| `FLiveLinkOpenTrackIOLens` | 镜头数据：FocusDistance、FStop、PinholeFocalLength、Distortion、Encoders 等 |
| `FLiveLinkOpenTrackIOTransform` | 变换数据：Translation（XYZ）、Rotation（Pan/Tilt/Roll）、Scale |
| `FLiveLinkOpenTrackIOTimecode` | SMPTE 时间码数据 |
| `FLiveLinkOpenTrackIOTiming` | 采样时间信息，含 SampleRate、SampleTimestamp、SequenceNumber、Synchronization |
| `FOpenTrackIOOptionalFloat` | 可选浮点值（蓝图可用），带 `bIsSet` 标记区分"未设置"和"值为 0" |
| `FLiveLinkOpenTrackIOStatics` | 静态数据：Camera（厂商/型号/传感器）、Lens（畸变/校准）、Tracker |

### 使用示例（蓝图描述）

1. **接收 OpenTrackIO 数据**：在 Live Link Hub 中，点击 Source 面板的 "+" → 选择 "Live Link OpenTrackIO Source" → 配置 Multicast/Unicast 端点 → 创建。Source 创建后自动监听 UDP 数据。

2. **在蓝图中读取镜头数据**：使用 Live Link 的蓝图接口（如 `GetLiveLinkSubjectFrameData`），将 Role 设为 "OpenTrackIO"，从返回的 `FLiveLinkOpenTrackIOBlueprintData` 中读取 `FrameData.OpenTrackData.Lens.FocusDistance`、`FStop`、`PinholeFocalLength` 等属性。注意这些值使用 `FOpenTrackIOOptionalFloat` 类型，需要先检查 `bIsSet` 再读取 `Value`。

3. **读取自定义 Metadata**：OpenTrackIO 数据的 `Custom.LiveLinkMetaData` 字段是一个键值对数组，会自动注入到 Live Link 帧数据的 `MetaData.StringMetaData` 中，可在蓝图中通过 key 读取。

## C++ 用法

### 头文件引入

```cpp
#include "LiveLinkOpenTrackIO.h"                    // 模块头文件
#include "LiveLinkOpenTrackIOTypes.h"               // 所有 OpenTrackIO 数据类型
#include "LiveLinkOpenTrackIOSourceSettings.h"      // Source 设置
#include "LiveLinkOpenTrackIOConnectionSettings.h"  // 连接设置
```

### 基本用法：解析 OpenTrackIO 数据

来自测试用例 `OpenTrackReaderTests.spec.cpp`：

```cpp
#include "LiveLinkOpenTrackIOParser.h"
#include "LiveLinkOpenTrackIOTypes.h"
#include "Misc/FileHelper.h"

// 解析 JSON payload
FString JsonBlob;
FFileHelper::LoadFileToString(JsonBlob, *JsonFilePath);
TOptional<FLiveLinkOpenTrackIOData> Data = UE::OpenTrackIO::Private::ParseJsonBlob(JsonBlob);
if (Data.IsSet())
{
    // 访问解析后的数据
    const FLiveLinkOpenTrackIOData& ParsedData = *Data;
    // ParsedData.Transforms  —— 变换链
    // ParsedData.Lens         —— 镜头参数
    // ParsedData.Timing       —— 时间信息
    // ParsedData.Static       —— 静态设备信息
}

// 解析 CBOR payload
TArray<uint8> BinaryBlob;
FFileHelper::LoadFileToArray(BinaryBlob, *CborFilePath);
TOptional<FLiveLinkOpenTrackIOData> CborData = UE::OpenTrackIO::Private::ParseCborBlob(BinaryBlob);
```

### 进阶用法：解析 UDP 数据包

来自测试用例 `OpenTrackReaderTests.spec.cpp`，演示如何从原始字节流中解析 OpenTrackIO 数据包：

```cpp
#include "LiveLinkOpenTrackIOParser.h"

// 假设 PacketsBlob 包含完整的 UDP 数据包字节流
TArrayView<uint8> AllPacketsView(PacketsBlob);
uint64 Index = 0;

while (Index < static_cast<uint64>(AllPacketsView.Num()))
{
    TArrayView<const uint8> PacketView = AllPacketsView.Slice(Index, AllPacketsView.Num() - Index);

    FOpenTrackIOHeaderWithPayload PayloadContainer;
    const bool bPayloadIsGood = UE::OpenTrackIO::Private::GetHeaderAndPayloadFromBytes(PacketView, PayloadContainer);

    if (!bPayloadIsGood) break;

    if (TOptional<FLiveLinkOpenTrackIOData> ParsedPayload = UE::OpenTrackIO::Private::ParsePayload(PayloadContainer))
    {
        const FLiveLinkOpenTrackIODatagramHeader& Header = PayloadContainer.GetHeader();
        const FLiveLinkOpenTrackIOData& Data = *ParsedPayload;

        // 使用 Data...
        // 推进索引：header 大小 + payload 大小
        Index += Header.GetPayloadSize() + sizeof(FLiveLinkOpenTrackIODatagramHeader);
    }
    else
    {
        break;
    }
}
```

### 进阶用法：坐标系转换

来自 `LiveLinkOpenTrackIOConversions.h`：

```cpp
#include "LiveLinkOpenTrackIOConversions.h"

// OpenTrackIO → Unreal 变换
FLiveLinkOpenTrackIOTransform OTTransform;  // 来自解析数据
FTransform UETransform = LiveLinkOpenTrackIOConversions::ToUnrealTransform(OTTransform);

// 单独转换各分量
FVector Translation = LiveLinkOpenTrackIOConversions::ToUnrealTranslation(OTTransform.Translation);
// 内部实现：FVector(Y, X, Z) * 100.0f  （交换 XY + 米→厘米）

FRotator Rotation = LiveLinkOpenTrackIOConversions::ToUnrealRotation(OTTransform.Rotation);
// 内部实现：FRotator(Tilt, -Pan, Roll)  （反转 Pan/Yaw 符号）
```

## Demo 示例

### 完整的 OpenTrackIO 数据解析示例

```cpp
// MyOpenTrackIOConsumer.h
#pragma once
#include "LiveLinkOpenTrackIOTypes.h"
#include "LiveLinkOpenTrackIOParser.h"

class FMyOpenTrackIOConsumer
{
public:
    // 从原始字节解析 OpenTrackIO 数据
    TOptional<FLiveLinkOpenTrackIOData> ParseFromBytes(TArrayView<const uint8> RawBytes)
    {
        FOpenTrackIOHeaderWithPayload PayloadContainer;
        if (!UE::OpenTrackIO::Private::GetHeaderAndPayloadFromBytes(RawBytes, PayloadContainer))
        {
            return {};
        }
        return UE::OpenTrackIO::Private::ParsePayload(PayloadContainer);
    }

    // 从 JSON 字符串解析
    TOptional<FLiveLinkOpenTrackIOData> ParseFromJson(const FString& JsonString)
    {
        return UE::OpenTrackIO::Private::ParseJsonBlob(JsonString);
    }

    // 提取镜头参数示例
    void ExtractLensParams(const FLiveLinkOpenTrackIOData& Data)
    {
        if (Data.Lens.FocusDistance.IsSet())
        {
            float FocusDistMeters = Data.Lens.FocusDistance.GetValue();
            // OpenTrackIO 单位是米，转换为 UE 的厘米
            float FocusDistCm = FocusDistMeters * 100.0f;
        }

        if (Data.Lens.FStop.IsSet())
        {
            float Aperture = Data.Lens.FStop.GetValue();
        }

        if (Data.Lens.PinholeFocalLength.IsSet())
        {
            float FocalLengthMm = Data.Lens.PinholeFocalLength.GetValue();
        }
    }
};
```

**Build.cs 依赖**：
```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "LiveLinkInterface",
    "LiveLinkOpenTrackIO"
});
```

## 模块依赖

从 `LiveLinkOpenTrackIO.Build.cs` 提取：

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `LiveLinkInterface` | Live Link 接口定义（ILiveLinkSource、ILiveLinkClient 等） |
| `Cbor` | CBOR 格式解析（私有依赖） |
| `Json` | JSON 格式解析（私有依赖） |
| `JsonUtilities` | JSON 工具函数（私有依赖） |
| `LiveLinkLens` | Live Link 镜头角色和数据类型（私有依赖） |
| `Networking` | UDP 网络通信（私有依赖） |
| `Sockets` | Socket API（私有依赖） |
| `Serialization` | 序列化支持（私有依赖） |
| `Slate` / `SlateCore` | UI 面板（Source 创建界面）（私有依赖） |
| `CoreUObject` | UObject 系统（私有依赖） |
| `Engine` | 引擎核心（私有依赖） |
| `ApplicationCore` | 应用核心（私有依赖） |
| `Projects` | 项目/插件系统（私有依赖） |

**插件依赖**（在 .uplugin 中声明）：

| 插件 | 用途 |
|---|---|
| `LiveLink` | Live Link 核心框架 |
| `LiveLinkCamera` | Live Link 摄影机角色 |
| `LiveLinkLens` | Live Link 镜头角色（本 plugin 的 OpenTrackIO Role 继承自此） |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-09-01 | `aefbf145cc7e` | OpenTrackIO: Support OpenLensIO lenses. | 新增对 OpenLensIO 镜头规范的支持 |
| 2025-06-27 | `2c8179fa6e16` | OpenTrackIO: Update to upcoming OTrIO version with a changed multicast address. | 更新至新版 OpenTrackIO 协议，调整默认多播地址 |
| 2025-05-13 | `23e096cc8280` | OpenTrackIO: Fix transform chain and entrance pupil offset order. | 修复变换链和入瞳偏移的计算顺序 |

### 维护评价

- **创建时间**：2025 年 4 月，是一个非常新的 plugin
- **更新频率**：3 次 commit 分布在 5 个月内，均为核心功能更新（协议支持、bug 修复），说明仍在活跃开发
- **Beta 状态**：`IsBetaVersion = true`，API 和功能可能随协议演进变化
- **平台限制**：仅限 Live Link Hub 使用（`ProgramAllowList: ["LiveLinkHub"]`），不适用于标准编辑器
- **协议兼容**：当前支持 OpenTrackIO 1.0.x 协议，代码中有版本校验（`IsSupported()` 检查 `Name == "OpenTrackIO"` 且 `Version[0] == 1, Version[1] == 0`）
- **推荐程度**：如果你在做 LED Volume / 虚拟制作且使用 Live Link Hub，这是接收 OpenTrackIO 数据的标准方式。但由于是 Beta 状态，生产环境使用需注意版本兼容性。

## 架构概览

```
UDP 数据包 (JSON/CBOR)
        │
        ▼
FLiveLinkOpenTrackIOSource (ILiveLinkSource)
    ├── HandleInboundData()     ← UDP 接收回调
    │       │
    │       ▼
    │   GetHeaderAndPayloadFromBytes()  ← 解析 16 字节协议头 + payload 重组
    │       │
    │       ▼
    │   ParsePayload()          ← JSON/CBOR 解码为 FLiveLinkOpenTrackIOData
    │       │
    │       ▼
    │   PushDataToLiveLink_AnyThread()
    │       ├── FLiveLinkOpenTrackIOCache::MakeStaticData()  ← 生成 Live Link 静态数据
    │       ├── FLiveLinkOpenTrackIOCache::MakeFrameData()   ← 生成 Live Link 帧数据
    │       │       └── LiveLinkOpenTrackIOConversions::ToUnrealLens()  ← 镜头参数 + 畸变转换
    │       │       └── LiveLinkOpenTrackIOConversions::ToUnrealTransform()  ← 坐标系转换
    │       └── ConditionallyPushLiveLinkTransformData()  ← 可选的 Transform Subject 输出
    │
    ▼
Live Link 系统 (ULiveLinkOpenTrackIORole)
    ├── FLiveLinkOpenTrackIOStaticData (继承 FLiveLinkLensStaticData)
    ├── FLiveLinkOpenTrackIOFrameData (继承 FLiveLinkLensFrameData)
    └── FLiveLinkOpenTrackIOBlueprintData (蓝图可用)
```

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/LiveLinkOpenTrackIO)
- [OpenTrackIO 规范](https://www.opentrackio.org/)
- [OpenTrackIO Schema](https://www.opentrackio.org/schema.json)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/LiveLinkOpenTrackIO/Source/LiveLinkOpenTrackIO/Private/Tests)
