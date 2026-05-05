# Capture Manager Core

> The Capture Manager Core plugin contains utility modules that are shared between Capture Manager App plugin and Capture Manager Editor plugin.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（样式资产） |
| 模块 | `CaptureManagerStyle` (Runtime), `CaptureManagerTakeMetadata` (Runtime), `CaptureProtocolStack` (Runtime), `CaptureUtils` (Runtime), `DataIngestCore` (Runtime), `LiveLinkHubCaptureMessaging` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-04 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerCore) | |

## 用途

Capture Manager Core 是虚幻引擎虚拟制片（Virtual Production）工作流中 **Capture Manager** 系统的基础核心插件。它不直接面向最终用户，而是作为 Capture Manager App（移动端/桌面端采集应用）和 Capture Manager Editor（编辑器内管理工具）之间的**共享基础设施层**。

该插件解决的核心问题是：在多设备、多协议的动捕/影视采集场景中，需要一套统一的数据格式、协议栈、元数据管理和数据导入管线。Capture Manager Core 将这些通用能力抽取为独立模块，避免 App 和 Editor 插件之间的代码重复。

具体功能包括：
- **采集协议栈**（CaptureProtocolStack）：实现与采集设备通信的网络协议
- **Take 元数据管理**（CaptureManagerTakeMetadata）：标准化采集 Take 的元数据结构
- **数据导入管线**（DataIngestCore）：解析采集归档文件（视频、音频、标定数据）并导入 UE
- **Live Link Hub 消息传递**（LiveLinkHubCaptureMessaging）：与 Live Link Hub 进行实时通信
- **通用工具**（CaptureUtils）：跨模块共享的工具函数
- **UI 样式**（CaptureManagerStyle）：Capture Manager 相关编辑器 UI 的统一样式

## 使用场景

- 你正在开发与 **Capture Manager** 集成的自定义采集设备插件 → 依赖 CaptureProtocolStack 实现协议通信
- 你需要解析和导入 **采集归档文件**（.capture 格式，包含视频、音频、标定数据）→ 使用 DataIngestCore
- 你需要读取或修改 **Take 元数据**（Slate、Take Number、设备信息等）→ 使用 CaptureManagerTakeMetadata
- 你正在构建与 **Live Link Hub** 集成的采集工作流 → 使用 LiveLinkHubCaptureMessaging
- 你正在开发 Capture Manager 系列插件的扩展 → 依赖本插件作为基础层

## 模块概览

本插件包含 6 个 Runtime 模块，按功能域划分：

| 模块 | 职责 |
|---|---|
| **CaptureManagerStyle** | Capture Manager 编辑器 UI 的 Slate 样式定义 |
| **CaptureManagerTakeMetadata** | Take 元数据结构定义与序列化 |
| **CaptureProtocolStack** | 采集设备通信协议栈实现 |
| **CaptureUtils** | 跨模块共享的通用工具函数 |
| **DataIngestCore** | 采集数据解析与导入管线 |
| **LiveLinkHubCaptureMessaging** | Live Link Hub 采集消息传递 |

> 详细的子模块文档请参阅各模块独立页面。

## 蓝图用法

本插件主要面向 C++ 开发者，大部分模块为底层基础设施，不直接暴露蓝图接口。以下是从源码中提取的少量蓝图可用 API：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ParseTimecode` | 从字符串解析 Timecode | `UE::CaptureManager` (DataIngestCore) |
| `ParseFrameRate` | 从 double 解析帧率 | `UE::CaptureManager` (DataIngestCore) |

> 大部分核心功能通过 C++ API 提供，蓝图层面主要通过 Capture Manager Editor 插件间接使用。

## C++ 用法

### 头文件引入

```cpp
// DataIngestCore - 数据导入
#include "IngestCaptureData.h"
#include "Utils/ParseTakeUtils.h"
#include "Utils/UnrealCalibrationParser.h"

// CaptureManagerTakeMetadata - Take 元数据
#include "TakeMetadata.h"

// CaptureProtocolStack - 协议栈
#include "CaptureProtocol.h"
```

### 基本用法 - 解析采集归档文件

```cpp
#include "IngestCaptureData.h"

// 解析 .capture 归档文件
FString FilePath = TEXT("/path/to/take.capture");
auto ParseResult = UE::CaptureManager::IngestCaptureData::ParseFile(FilePath);

if (ParseResult.HasValue())
{
    const FIngestCaptureData& CaptureData = ParseResult.GetValue();
    
    // 访问视频信息
    for (const FIngestCaptureData::FVideo& Video : CaptureData.Video)
    {
        UE_LOG(LogTemp, Log, TEXT("Video: %s, Path: %s"), *Video.Name, *Video.Path);
        
        if (Video.FrameRate.IsSet())
        {
            UE_LOG(LogTemp, Log, TEXT("  Frame Rate: %f"), Video.FrameRate.GetValue());
        }
        
        if (Video.FrameWidth.IsSet() && Video.FrameHeight.IsSet())
        {
            UE_LOG(LogTemp, Log, TEXT("  Resolution: %dx%d"), 
                Video.FrameWidth.GetValue(), Video.FrameHeight.GetValue());
        }
    }
    
    // 访问音频信息
    for (const FIngestCaptureData::FAudio& Audio : CaptureData.Audio)
    {
        UE_LOG(LogTemp, Log, TEXT("Audio: %s, Path: %s"), *Audio.Name, *Audio.Path);
    }
    
    // 访问标定信息
    for (const FIngestCaptureData::FCalibration& Calib : CaptureData.Calibration)
    {
        UE_LOG(LogTemp, Log, TEXT("Calibration: %s, Path: %s"), *Calib.Name, *Calib.Path);
    }
    
    // 访问元数据
    UE_LOG(LogTemp, Log, TEXT("Device: %s, Slate: %s, Take: %d"),
        *CaptureData.DeviceModel, *CaptureData.Slate, CaptureData.TakeNumber);
}
else
{
    FText Error = ParseResult.GetError();
    UE_LOG(LogTemp, Error, TEXT("Failed to parse capture data: %s"), *Error.ToString());
}
```

### 基本用法 - 解析 Timecode 和帧率

```cpp
#include "Utils/ParseTakeUtils.h"

// 解析 Timecode 字符串
FString TimecodeStr = TEXT("01:23:45:12");
FTimecode Timecode = UE::CaptureManager::ParseTimecode(TimecodeStr);
UE_LOG(LogTemp, Log, TEXT("Parsed Timecode: %s"), *Timecode.ToString());

// 解析帧率
FFrameRate FrameRate = UE::CaptureManager::ParseFrameRate(29.97);
UE_LOG(LogTemp, Log, TEXT("Frame Rate: %f / %f"), 
    (float)FrameRate.Numerator, (float)FrameRate.Denominator);
```

### 进阶用法 - 序列化采集数据

```cpp
#include "IngestCaptureData.h"

// 构建采集数据对象
FIngestCaptureData CaptureData;
CaptureData.Version = 1;
CaptureData.DeviceModel = TEXT("iPhone 15 Pro");
CaptureData.Slate = TEXT("Shot_001");
CaptureData.TakeNumber = 3;

// 添加视频条目
FIngestCaptureData::FVideo VideoEntry;
VideoEntry.Name = TEXT("MainCamera");
VideoEntry.Path = TEXT("Videos/MainCamera.mp4");
VideoEntry.FrameRate = 30.0f;
VideoEntry.FrameWidth = 1920;
VideoEntry.FrameHeight = 1080;
VideoEntry.TimecodeStart = TEXT("01:00:00:00");
CaptureData.Video.Add(VideoEntry);

// 添加音频条目
FIngestCaptureData::FAudio AudioEntry;
AudioEntry.Name = TEXT("Microphone");
AudioEntry.Path = TEXT("Audio/Microphone.wav");
AudioEntry.TimecodeStart = TEXT("01:00:00:00");
AudioEntry.TimecodeRate = 48000.0f;
CaptureData.Audio.Add(AudioEntry);

// 添加标定条目
FIngestCaptureData::FCalibration CalibEntry;
CalibEntry.Name = TEXT("CameraCalibration");
CalibEntry.Path = TEXT("Calibration/camera.cal");
CaptureData.Calibration.Add(CalibEntry);

// 序列化到文件
TOptional<FText> SerializeResult = UE::CaptureManager::IngestCaptureData::Serialize(
    TEXT("/path/to/output/"),
    TEXT("take"),
    CaptureData
);

if (SerializeResult.IsSet())
{
    UE_LOG(LogTemp, Error, TEXT("Serialization failed: %s"), *SerializeResult.GetValue().ToString());
}
```

### 进阶用法 - 解析相机标定文件

```cpp
#include "Utils/UnrealCalibrationParser.h"

// 解析标定文件
FString CalibFilePath = TEXT("/path/to/camera.calibration");
auto Result = FUnrealCalibrationParser::Parse(CalibFilePath);

if (Result.HasValue())
{
    const TArray<FCameraCalibration>& Calibrations = Result.GetValue();
    
    for (const FCameraCalibration& Calib : Calibrations)
    {
        UE_LOG(LogTemp, Log, TEXT("Parsed calibration for camera"));
        // 使用标定数据...
    }
}
else
{
    FText Error = Result.GetError();
    UE_LOG(LogTemp, Error, TEXT("Calibration parse error: %s"), *Error.ToString());
}
```

## Demo 示例

以下是一个完整的最小示例，展示如何使用 DataIngestCore 模块解析和创建采集归档数据：

### CaptureDataDemo.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "CaptureDataDemo.generated.h"

UCLASS()
class UCaptureDataDemoSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    /** 演示解析采集归档文件 */
    UFUNCTION(BlueprintCallable, Category = "Capture Demo")
    void DemoParseCaptureFile(const FString& InFilePath);

    /** 演示创建并序列化采集数据 */
    UFUNCTION(BlueprintCallable, Category = "Capture Demo")
    void DemoCreateCaptureData(const FString& InOutputPath);
};
```

### CaptureDataDemo.cpp

```cpp
#include "CaptureDataDemo.h"
#include "IngestCaptureData.h"
#include "Utils/ParseTakeUtils.h"

void UCaptureDataDemoSubsystem::DemoParseCaptureFile(const FString& InFilePath)
{
    using namespace UE::CaptureManager;
    
    auto ParseResult = IngestCaptureData::ParseFile(InFilePath);
    
    if (!ParseResult.HasValue())
    {
        UE_LOG(LogTemp, Warning, TEXT("Parse failed: %s"), *ParseResult.GetError().ToString());
        return;
    }
    
    const FIngestCaptureData& Data = ParseResult.GetValue();
    UE_LOG(LogTemp, Log, TEXT("Device: %s, Slate: %s, Take: %u"),
        *Data.DeviceModel, *Data.Slate, Data.TakeNumber);
    UE_LOG(LogTemp, Log, TEXT("Videos: %d, Audios: %d, Calibrations: %d"),
        Data.Video.Num(), Data.Audio.Num(), Data.Calibration.Num());
}

void UCaptureDataDemoSubsystem::DemoCreateCaptureData(const FString& InOutputPath)
{
    using namespace UE::CaptureManager;
    
    FIngestCaptureData Data;
    Data.DeviceModel = TEXT("DemoDevice");
    Data.Slate = TEXT("Demo");
    Data.TakeNumber = 1;
    
    FIngestCaptureData::FVideo Video;
    Video.Name = TEXT("Camera");
    Video.Path = TEXT("camera.mp4");
    Video.FrameRate = 30.0f;
    Data.Video.Add(Video);
    
    auto Result = IngestCaptureData::Serialize(InOutputPath, TEXT("demo"), Data);
    if (Result.IsSet())
    {
        UE_LOG(LogTemp, Warning, TEXT("Serialize failed: %s"), *Result.GetValue().ToString());
    }
    else
    {
        UE_LOG(LogTemp, Log, TEXT("Capture data serialized to: %s"), *InOutputPath);
    }
}
```

## 模块依赖

本插件的模块间依赖关系：

| 模块 | 用途 |
|---|---|
| `CameraCalibration` | 相机标定数据结构（DataIngestCore 依赖） |
| `LiveLinkHubMessaging` | Live Link Hub 消息传递基础（LiveLinkHubCaptureMessaging 依赖） |
| `MediaUtils` | 媒体工具函数 |
| `MediaAssets` | 媒体资产类型 |

> 无特殊依赖（仅标准 Core/Engine/Slate 等 + 上述 Virtual Production 相关模块）

## 维护状态

### 近期更新

```
- 2739c3d30ebc Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types. Part 4/n
- bd59a22f1783 [CaptureManager] Replace UserId with Name in take metadata
- 404b5603644a [CaptureManager] Improve metadata key names
```

- `2739c3d30ebc`：代码质量修复，确保 DLL 导出标记（UE_API）正确放置在方法和静态变量上而非类型上。这是 Epic 全局代码修复的一部分。
- `bd59a22f1783`：Take 元数据中将 `UserId` 字段重命名为 `Name`，属于 API 改进。
- `404b5603644a`：改进元数据的键名命名，提升可读性和一致性。

### 维护评价

- **创建时间**：2025 年 2 月，非常新的插件
- **活跃度**：✅ 活跃维护中。近期有 API 改进和代码质量修复
- **成熟度**：作为 Capture Manager 系统的核心层，仍在快速迭代中（元数据 API 仍在调整）
- **注意事项**：
  - `EnabledByDefault: false`，需要手动启用
  - API 尚不稳定（近期有 UserId → Name 的破坏性变更）
  - 主要面向 Capture Manager 生态内部使用，不建议作为独立功能使用
- **推荐度**：⭐⭐⭐ 如果你在开发 Capture Manager 相关功能，这是必选依赖；如果是独立项目，不建议直接依赖

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerCore)
- [CaptureManagerStyle 模块文档](./CaptureManagerStyle.md)
- [CaptureManagerTakeMetadata 模块文档](./CaptureManagerTakeMetadata.md)
- [CaptureProtocolStack 模块文档](./CaptureProtocolStack.md)
- [CaptureUtils 模块文档](./CaptureUtils.md)
- [DataIngestCore 模块文档](./DataIngestCore.md)
- [LiveLinkHubCaptureMessaging 模块文档](./LiveLinkHubCaptureMessaging.md)

---

# DataIngestCore

> 采集数据解析与导入管线模块，负责将采集归档文件（视频、音频、标定数据）解析为 UE 可用的数据结构。

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否（随父插件 CaptureManagerCore） |
| 包含内容 | ❌ 无 |
| 模块 | `DataIngestCore` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-04 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerCore/Source/DataIngestCore) | |

## 用途

DataIngestCore 是 Capture Manager 数据导入管线的核心模块。它负责：

1. **解析采集归档文件**（`.capture` 格式）：将包含视频序列、音频轨道、相机标定数据的归档文件解析为结构化的 `FIngestCaptureData` 对象
2. **序列化采集数据**：将内存中的采集数据对象写回归档文件
3. **解析 Timecode 和帧率**：提供 Timecode 字符串和帧率数值的标准化解析
4. **解析相机标定文件**：将外部标定格式转换为 UE 的 `FCameraCalibration` 结构

该模块是数据从采集设备进入 UE 的第一道关口，确保所有采集数据在进入后续处理流程前被正确解析和标准化。

## 核心数据结构

### FIngestCaptureData

采集归档的顶层数据结构，包含：

| 字段 | 类型 | 说明 |
|---|---|---|
| `Version` | `uint32` | 归档格式版本号 |
| `DeviceModel` | `FString` | 采集设备型号 |
| `Slate` | `FString` | 场记板标识 |
| `TakeNumber` | `uint32` | Take 编号 |
| `Video` | `TArray<FVideo>` | 视频/图像序列列表 |
| `Depth` | `TArray<FVideo>` | 深度序列列表 |
| `Audio` | `TArray<FAudio>` | 音频轨道列表 |
| `Calibration` | `TArray<FCalibration>` | 标定数据列表 |

### FVideo

视频/图像序列信息：

| 字段 | 类型 | 说明 |
|---|---|---|
| `Name` | `FString` | 视频名称 |
| `Path` | `FString` | 文件路径 |
| `FrameRate` | `TOptional<float>` | 帧率 |
| `FrameWidth` | `TOptional<uint32>` | 帧宽度 |
| `FrameHeight` | `TOptional<uint32>` | 帧高度 |
| `DroppedFrames` | `TArray<uint32>` | 丢帧列表 |
| `TimecodeStart` | `TOptional<FString>` | 起始 Timecode |

### FAudio

音频信息：

| 字段 | 类型 | 说明 |
|---|---|---|
| `Name` | `FString` | 音频名称 |
| `Path` | `FString` | 文件路径 |
| `TimecodeStart` | `TOptional<FString>` | 起始 Timecode |
| `TimecodeRate` | `TOptional<float>` | Timecode 采样率 |

### FCalibration

标定数据信息：

| 字段 | 类型 | 说明 |
|---|---|---|
| `Name` | `FString` | 标定名称 |
| `Path` | `FString` | 标定文件路径 |

## C++ API

### 解析采集归档

```cpp
namespace UE::CaptureManager::IngestCaptureData
{
    using FParseResult = TValueOrError<FIngestCaptureData, FText>;
    DATAINGESTCORE_API FParseResult ParseFile(const FString& InFilePath);
}
```

### 序列化采集数据

```cpp
namespace UE::CaptureManager::IngestCaptureData
{
    DATAINGESTCORE_API TOptional<FText> Serialize(
        const FString& InFilePath,
        const FString& InFileName,
        const FIngestCaptureData& InIngestCaptureData
    );
}
```

### 解析 Timecode

```cpp
namespace UE::CaptureManager
{
    DATAINGESTCORE_API FTimecode ParseTimecode(const FString& InTimecodeString);
    DATAINGESTCORE_API FFrameRate ParseFrameRate(double InFrameRate);
}
```

### 解析相机标定

```cpp
class FUnrealCalibrationParser
{
public:
    using FParseResult = TValueOrError<TArray<FCameraCalibration>, FText>;
    static UE_API FParseResult Parse(const FString& InFile);
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `CameraCalibration` | 相机标定数据结构 `FCameraCalibration` |

---

# CaptureManagerTakeMetadata

> Take 元数据结构定义与序列化模块。

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否（随父插件） |
| 包含内容 | ❌ 无 |
| 模块 | `CaptureManagerTakeMetadata` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-04 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerCore/Source/CaptureManagerTakeMetadata) | |

## 用途

CaptureManagerTakeMetadata 定义了 Capture Manager 系统中 **Take 元数据** 的标准化结构。每个 Take（一次采集录制）都附带元数据，记录设备信息、时间码、场景信息等。

该模块确保 Capture Manager App 和 Editor 使用统一的元数据格式进行读写。

> **注意**：近期 API 变更 — `UserId` 字段已重命名为 `Name`，元数据键名也已改进。如果从旧版本迁移，需要更新相关代码。

---

# CaptureProtocolStack

> 采集设备通信协议栈实现模块。

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否（随父插件） |
| 包含内容 | ❌ 无 |
| 模块 | `CaptureProtocolStack` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-04 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerCore/Source/CaptureProtocolStack) | |

## 用途

CaptureProtocolStack 实现了 Capture Manager 系统与采集设备之间的**网络通信协议**。该模块处理：

- 与采集设备的连接建立和管理
- 命令的发送与响应解析
- 数据流的传输控制
- 协议版本协商

这是 Capture Manager App 能够远程控制采集设备（如 iPhone 上的 Live Link Face 应用）的底层通信基础。

---

# CaptureUtils

> 跨模块共享的通用工具函数模块。

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否（随父插件） |
| 包含内容 | ❌ 无 |
| 模块 | `CaptureUtils` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-04 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerCore/Source/CaptureUtils) | |

## 用途

CaptureUtils 提供 Capture Manager 系统中多个模块共用的**通用工具函数**。这些工具函数不属于任何特定功能域，但被多个模块共同依赖，因此抽取到独立模块中以避免循环依赖。

---

# CaptureManagerStyle

> Capture Manager 编辑器 UI 的 Slate 样式定义模块。

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否（随父插件） |
| 包含内容 | ✅ 有（Slate 样式资产） |
| 模块 | `CaptureManagerStyle` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-04 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerCore/Source/CaptureManagerStyle) | |

## 用途

CaptureManagerStyle 定义了 Capture Manager 系列插件在编辑器中使用的**统一样式**，包括图标、颜色、字体等 UI 资源。通过将样式集中管理，确保 Capture Manager App 和 Editor 插件的 UI 风格一致。

---

# LiveLinkHubCaptureMessaging

> Live Link Hub 采集消息传递模块。

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否（随父插件） |
| 包含内容 | ❌ 无 |
| 模块 | `LiveLinkHubCaptureMessaging` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-04 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerCore/Source/LiveLinkHubCaptureMessaging) | |

## 用途

LiveLinkHubCaptureMessaging 实现了 Capture Manager 与 **Live Link Hub** 之间的消息传递机制。Live Link Hub 是 UE 的集中式 Live Link 数据分发中心，该模块使 Capture Manager 能够：

- 通过 Live Link Hub 接收实时采集数据
- 向 Live Link Hub 发送采集控制命令
- 与 Live Link 生态系统的其他组件集成

| 模块 | 用途 |
|---|---|
| `LiveLinkHubMessaging` | Live Link Hub 基础消息传递框架 |