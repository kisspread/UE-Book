# Capture Manager Core

> The Capture Manager Core plugin contains utility modules that are shared between Capture Manager App plugin and Capture Manager Editor plugin.

| 属性 | 值 |
|---|---|
| 中文名 | 捕获管理器核心 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CaptureDataConverter` (Runtime), `CaptureManagerCPSClient` (Runtime), `CaptureManagerMediaRW` (Runtime), `CaptureManagerPipeline` (Runtime), `CaptureManagerStyle` (Runtime), `CaptureManagerTakeMetadata` (Runtime), `CaptureMetadataExtraction` (Runtime), `CaptureProtocolStack` (Runtime), `CaptureUtils` (Runtime), `DataIngestCore` (Runtime), `LiveLinkHubCaptureMessaging` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-04 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerCore) | |

## 用途

Capture Manager Core 是虚幻引擎虚拟制片流水线中**捕获管理系统的底层核心框架**。它不是面向最终用户的独立功能插件，而是作为 Capture Manager App（设备端应用）和 Capture Manager Editor（编辑器端插件）之间的**共享基础设施层**。

该插件解决的核心问题是：在动捕/面捕等性能捕获工作流中，设备端采集到的原始数据（视频、音频、深度、标定文件等）需要经过一套标准化的解析、传输、转换和入库流程，才能被引擎正确使用。Capture Manager Core 封装了这套流程的全部底层逻辑，包括：

- **捕获数据结构定义**：标准化的采集数据格式（`FIngestCaptureData`），涵盖视频、音频、深度和标定信息
- **协议通信栈**：设备与引擎之间的通信协议实现（`CaptureProtocolStack`、`CaptureManagerCPSClient`）
- **媒体读写**：音视频数据的读取与写入（`CaptureManagerMediaRW`）
- **数据转换管道**：将采集格式转换为引擎可用格式（`CaptureDataConverter`、`CaptureManagerPipeline`）
- **Take 元数据管理**：Take 编号、Slate 信息、时间码等元数据处理（`CaptureManagerTakeMetadata`、`CaptureMetadataExtraction`）
- **LiveLink 集成**：与 LiveLink Hub 的消息传递（`LiveLinkHubCaptureMessaging`）
- **标定解析**：相机标定数据的解析（`UnrealCalibrationParser`）

## 使用场景

- 你在搭建一个**动捕/面捕虚拟制片流水线** → 需要 CaptureManagerCore 作为基础设施
- 你在开发**自定义的捕获设备接入插件** → 使用 CaptureProtocolStack 实现通信协议
- 你需要将**外部采集的视频/音频数据**导入引擎 → 使用 DataIngestCore 解析采集存档
- 你在扩展 **Capture Manager** 的数据格式支持 → 使用 CaptureDataConverter 模块
- 你需要从采集数据中**提取时间码和帧率信息** → 使用 ParseTakeUtils 工具函数

> ⚠️ **注意**：此插件 `EnabledByDefault = false`，通常作为 CaptureManagerApp 或 CaptureManagerEditor 的依赖自动启用，不建议单独手动启用。

## 蓝图用法

该插件的所有模块均为 Runtime 类型，面向 C++ 开发者。从提供的公开 API 来看，核心数据结构 `FIngestCaptureData` 和解析工具均为 C++ 层接口，**没有直接暴露蓝图节点**。

如果需要在蓝图中使用捕获数据，通常通过 CaptureManagerEditor 插件提供的蓝图接口间接访问。

## C++ 用法

### 头文件引入

```cpp
// 捕获数据结构
#include "IngestCaptureData.h"

// 时间码/帧率解析工具
#include "Utils/ParseTakeUtils.h"

// 相机标定解析
#include "Utils/UnrealCalibrationParser.h"
```

### 基本用法 — 解析捕获存档文件

从采集设备导出的数据通常是一个 `.capture` 存档文件，使用 `ParseFile` 将其解析为结构化数据：

```cpp
#include "IngestCaptureData.h"

using namespace UE::CaptureManager::IngestCaptureData;

// 解析采集存档文件
FString ArchivePath = TEXT("/path/to/capture.archive");
FParseResult Result = ParseFile(ArchivePath);

if (Result.HasValue())
{
    const FIngestCaptureData& CaptureData = Result.GetValue();
    
    // 访问视频信息
    for (const FIngestCaptureData::FVideo& Video : CaptureData.Video)
    {
        UE_LOG(LogTemp, Log, TEXT("视频: %s, 路径: %s"), *Video.Name, *Video.Path);
        
        if (Video.FrameRate.IsSet())
        {
            UE_LOG(LogTemp, Log, TEXT("  帧率: %.2f"), Video.FrameRate.GetValue());
        }
        if (Video.FrameWidth.IsSet() && Video.FrameHeight.IsSet())
        {
            UE_LOG(LogTemp, Log, TEXT("  分辨率: %dx%d"), Video.FrameWidth.GetValue(), Video.FrameHeight.GetValue());
        }
    }
    
    // 访问音频信息
    for (const FIngestCaptureData::FAudio& Audio : CaptureData.Audio)
    {
        UE_LOG(LogTemp, Log, TEXT("音频: %s, 路径: %s"), *Audio.Name, *Audio.Path);
    }
}
else
{
    // 解析失败，获取错误信息
    FText Error = Result.GetError();
    UE_LOG(LogTemp, Error, TEXT("解析失败: %s"), *Error.ToString());
}
```

> 来源：`Public/IngestCaptureData.h`

### 基本用法 — 路径标准化

采集数据中的路径通常是相对路径，需要转换为绝对路径才能在引擎中正确引用：

```cpp
#include "IngestCaptureData.h"

FIngestCaptureData CaptureData;
// ... 从文件解析或手动构建

// 将所有相对路径转换为基于指定根目录的绝对路径
FString BasePath = TEXT("D:/Captures/Session001");
CaptureData.MakePathsAbsolute(BasePath);

// 现在所有 Video[i].Path, Audio[i].Path 等都是绝对路径
```

> 来源：`Public/IngestCaptureData.h`

### 进阶用法 — 时间码解析与帧率处理

在处理采集数据的同步信息时，需要将字符串格式的时间码和数值帧率转换为引擎原生类型：

```cpp
#include "Utils/ParseTakeUtils.h"
#include "IngestCaptureData.h"

using namespace UE::CaptureManager;

void ProcessTimecodes(const FIngestCaptureData& InCaptureData)
{
    for (const FIngestCaptureData::FVideo& Video : InCaptureData.Video)
    {
        if (Video.TimecodeStart.IsSet())
        {
            // 将字符串时间码解析为 FTimecode
            FTimecode Timecode = ParseTimecode(Video.TimecodeStart.GetValue());
            UE_LOG(LogTemp, Log, TEXT("视频 %s 起始时间码: %s"), 
                *Video.Name, *Timecode.ToString());
        }
        
        if (Video.FrameRate.IsSet())
        {
            // 将 double 帧率值解析为 FFrameRate（精确分数表示）
            FFrameRate FrameRate = ParseFrameRate(Video.FrameRate.GetValue());
            UE_LOG(LogTemp, Log, TEXT("视频 %s 帧率: %s (%.2f fps)"), 
                *Video.Name, *FrameRate.ToPrettyText().ToString(), 
                FrameRate.AsDecimal());
        }
    }
}
```

> 来源：`Public/Utils/ParseTakeUtils.h`

### 进阶用法 — 序列化捕获数据

将构建好的 `FIngestCaptureData` 保存到文件：

```cpp
#include "IngestCaptureData.h"

using namespace UE::CaptureManager::IngestCaptureData;

FIngestCaptureData NewCaptureData;
NewCaptureData.Version = 1;
NewCaptureData.DeviceModel = TEXT("MetaHuman Animator");
NewCaptureData.Slate = TEXT("SH010");
NewCaptureData.TakeNumber = 3;

// 添加视频信息
FIngestCaptureData::FVideo VideoInfo;
VideoInfo.Name = TEXT("front_camera");
VideoInfo.Path = TEXT("./video/front_camera.mp4");
VideoInfo.FrameRate = 30.0f;
VideoInfo.FrameWidth = 1920;
VideoInfo.FrameHeight = 1080;
NewCaptureData.Video.Add(MoveTemp(VideoInfo));

// 添加音频信息
FIngestCaptureData::FAudio AudioInfo;
AudioInfo.Name = TEXT("microphone");
AudioInfo.Path = TEXT("./audio/mic.wav");
AudioInfo.TimecodeStart = TEXT("01:00:00:00");
AudioInfo.TimecodeRate = 30.0f;
NewCaptureData.Audio.Add(MoveTemp(AudioInfo));

// 序列化到文件
FString OutputDir = TEXT("D:/Captures/Output");
FString FileName = TEXT("SH010_T003");
TOptional<FText> Error = Serialize(OutputDir, FileName, NewCaptureData);

if (Error.IsSet())
{
    UE_LOG(LogTemp, Error, TEXT("序列化失败: %s"), *Error.GetValue().ToString());
}
```

> 来源：`Public/IngestCaptureData.h`

### 进阶用法 — 相机标定数据解析

```cpp
#include "Utils/UnrealCalibrationParser.h"

using FCalibrationResult = FUnrealCalibrationParser::FParseResult;

FString CalibrationFile = TEXT("/path/to/calibration.json");
FCalibrationResult Result = FUnrealCalibrationParser::Parse(CalibrationFile);

if (Result.HasValue())
{
    const TArray<FCameraCalibration>& Calibrations = Result.GetValue();
    for (const FCameraCalibration& Cal : Calibrations)
    {
        UE_LOG(LogTemp, Log, TEXT("已加载相机标定数据"));
        // 使用 FCameraCalibration 中的内参/外参数据
    }
}
else
{
    UE_LOG(LogTemp, Error, TEXT("标定解析失败: %s"), *Result.GetError().ToString());
}
```

> 来源：`Public/Utils/UnrealCalibrationParser.h`

## Demo 示例

以下是一个完整的最小示例，演示如何解析采集存档并将路径标准化：

```cpp
// CaptureIngestDemo.h
#pragma once

#include "CoreMinimal.h"

class FCaptureIngestDemo
{
public:
    /** 解析采集存档并打印摘要信息 */
    static void RunDemo(const FString& InArchivePath, const FString& InBasePath);
};
```

```cpp
// CaptureIngestDemo.cpp
#include "CaptureIngestDemo.h"
#include "IngestCaptureData.h"
#include "Utils/ParseTakeUtils.h"

using namespace UE::CaptureManager;
using namespace UE::CaptureManager::IngestCaptureData;

void FCaptureIngestDemo::RunDemo(const FString& InArchivePath, const FString& InBasePath)
{
    // 1. 解析采集存档
    FParseResult Result = ParseFile(InArchivePath);
    if (!Result.HasValue())
    {
        UE_LOG(LogTemp, Error, TEXT("无法解析存档: %s"), *Result.GetError().ToString());
        return;
    }
    
    FIngestCaptureData CaptureData = Result.GetValue();
    
    // 2. 将相对路径标准化为绝对路径
    CaptureData.MakePathsAbsolute(InBasePath);
    
    // 3. 打印摘要
    UE_LOG(LogTemp, Log, TEXT("=== 采集数据摘要 ==="));
    UE_LOG(LogTemp, Log, TEXT("设备: %s | Slate: %s | Take: %u"),
        *CaptureData.DeviceModel, *CaptureData.Slate, CaptureData.TakeNumber);
    UE_LOG(LogTemp, Log, TEXT("视频: %d | 深度: %d | 音频: %d | 标定: %d"),
        CaptureData.Video.Num(), CaptureData.Depth.Num(),
        CaptureData.Audio.Num(), CaptureData.Calibration.Num());
    
    // 4. 解析时间码信息
    for (const auto& Video : CaptureData.Video)
    {
        if (Video.TimecodeStart.IsSet())
        {
            FTimecode Tc = ParseTimecode(Video.TimecodeStart.GetValue());
            UE_LOG(LogTemp, Log, TEXT("  [%s] 起始时间码: %s"), 
                *Video.Name, *Tc.ToString());
        }
    }
}
```

## 模块依赖

该插件包含 11 个 Runtime 模块，彼此之间存在依赖关系。以下列出使用者需要关注的**非通用**依赖：

| 模块 | 用途 |
|---|---|
| `LiveLink` | LiveLinkHubCaptureMessaging 模块用于与 LiveLink Hub 建立消息通道 |
| `Json` | CaptureProtocolStack 和 CaptureMetadataExtraction 用于解析 JSON 格式的元数据和协议消息 |
| `MediaUtils` | CaptureManagerMediaRW 用于音视频媒体的底层读写操作 |

> 实际 Build.cs 中可能包含更多依赖（如 MediaAssets、ImageWriteQueue 等），建议查阅具体模块的 Build.cs 文件确认完整依赖列表。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `a2e4a9e3` | Forward the stop token to third-party encoder commands so audio and video conversion can be cancelled | 支持向第三方编码器传递取消信号，使音视频转换可被中断 |
| 2026-05-12 | `218704d7` | [CaptureManager] Added missing fix from 51621159 which was dropped during conversion module move. | 补回模块迁移过程中丢失的修复代码 |
| 2026-05-12 | `16e184f7` | [CaptureManager] Fix transaction ID data race causing transient download failures. | 修复事务 ID 数据竞争导致的偶发下载失败 |
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构 JSON 对象以同时支持 FString 和 FSharedString |
| 2026-04-30 | `d6f72591` | [CaptureManager] Add CaptureManagerDeviceBlueprint module | 新增设备蓝图模块 |

### 维护评价

**活跃维护中** ✅

- **创建时间**：2025 年 2 月，作为 Capture Manager 从原有位置迁移到 Virtual Production 目录的一部分，是一个相对较新的基础设施插件
- **更新频率**：近期（2026 年 4-5 月）有多次实质性更新，包括功能增强（取消信号支持、新模块）、Bug 修复（数据竞争）和代码重构
- **维护状态**：由 Epic Games 官方团队积极维护，属于虚拟制片工作流的核心组件
- **注意事项**：
  - `EnabledByDefault = false`，表明它是被其他插件作为依赖引入的底层模块
  - 共 11 个模块、251 个源文件，架构规模较大，建议按模块分别理解
  - `.uplugin` 的 `IsBetaVersion` 字段被截断，但从 1.0.0 版本号和活跃维护来看，应已进入正式发布状态

**推荐使用**：如果你在开发与 Capture Manager 相关的虚拟制片工具，此插件是必需的基础设施。不建议直接使用，而是通过 CaptureManagerEditor 或 CaptureManagerApp 插件间接依赖。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerCore)
- [官方文档]()（暂无）
- [测试用例]()（待确认）