# LiveLinkFaceMetadata

> The Capture Manager allows control and monitoring of the capture device, obtains and transcodes the data from the devices and upload the data for import to the UE

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、配置资产） |
| 模块 | `CaptureDataConverter` (Runtime), `CaptureManagerEditor` (Runtime), `CaptureManagerMediaRW` (Runtime), `CaptureManagerPipeline` (Runtime), `CaptureManagerSettings` (Runtime), `CaptureManagerUnrealEndpoint` (Runtime), `ExampleLiveLinkDevices` (Runtime), `IngestLiveLinkDevice` (Runtime), `LiveLinkCapabilities` (Runtime), `LiveLinkFaceMetadata` (Runtime), `StereoCameraMetadata` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-04 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerApp) | |

## 用途

LiveLinkFaceMetadata 是 CaptureManagerApp 插件中的一个专用模块，负责解析旧版 LiveLink Face 应用程序生成的捕获元数据。该模块解决的核心问题是：在虚拟制片工作流中，需要将 LiveLink Face 应用（iOS 面部捕捉应用）录制的 JSON 元数据文件转换为 UE 内部统一的 `FTakeMetadata` 格式，以便后续的媒体转码、导入和处理流程能够正确理解视频帧的时间码、旋转信息等关键元数据。

该模块专门处理"旧版"格式的兼容性，确保从早期 LiveLink Face 版本录制的数据仍能被新的 CaptureManager 系统正确解析和使用。

## 使用场景

- 你使用 LiveLink Face iOS 应用录制了面部捕捉数据，需要将录制的 JSON 元数据导入 UE → 使用此模块解析元数据
- 你的虚拟制片管线需要处理不同帧率（非标准 30/60 FPS）的 LiveLink Face 视频 → 此模块支持任意帧率的时间码解析
- 你需要从旧版 LiveLink Face 格式迁移数据到新的 CaptureManager 系统 → 使用 `ParseOldLiveLinkTakeMetadata` 进行格式转换
- 你遇到 LiveLink Face 视频首帧为分数帧号导致时间码解析失败的问题 → 此模块已修复该边界情况

## 蓝图用法

本模块主要提供 C++ API，不直接暴露蓝图节点。元数据解析功能通过 `UE::CaptureManager::LiveLinkMetadata` 命名空间下的静态函数提供，供其他模块（如 CaptureDataConverter、CaptureManagerPipeline）在内部调用。

## C++ 用法

### 头文件引入

```cpp
#include "LiveLinkFaceMetadata.h"
```

### 基本用法

从 JSON 文件解析旧版 LiveLink Face 元数据：

```cpp
#include "LiveLinkFaceMetadata.h"

// 解析旧版 LiveLink Face 的 take 元数据
FString JsonFilePath = TEXT("/path/to/live_link_face_take.json");
TArray<FText> ValidationErrors;

TOptional<FTakeMetadata> TakeMetadata = 
    UE::CaptureManager::LiveLinkMetadata::ParseOldLiveLinkTakeMetadata(
        JsonFilePath, 
        ValidationErrors
    );

if (TakeMetadata.IsSet())
{
    // 解析成功，获取视频元数据
    const FTakeMetadata& Metadata = TakeMetadata.GetValue();
    
    // 访问视频信息（帧率、分辨率、时间码等）
    for (const FTakeMetadata::FVideo& Video : Metadata.Videos)
    {
        // Video 包含帧率、旋转、时间码偏移等信息
    }
}
else
{
    // 解析失败，检查验证错误
    for (const FText& Error : ValidationErrors)
    {
        UE_LOG(LogTemp, Warning, TEXT("Metadata validation error: %s"), *Error.ToString());
    }
}
```

### 进阶用法

从 JSON 字符串直接解析视频元数据（适用于已读取文件内容或从网络接收数据的场景）：

```cpp
#include "LiveLinkFaceMetadata.h"

// 假设已经从某处获取了 JSON 字符串
FString JsonString = TEXT(R"({"frames": [...], "frameRate": 24})");
TArray<FText> ValidationErrors;

TArray<FTakeMetadata::FVideo> VideoMetadata = 
    UE::CaptureManager::LiveLinkMetadata::ParseOldLiveLinkVideoMetadataFromString(
        JsonString, 
        ValidationErrors
    );

if (ValidationErrors.Num() == 0)
{
    // 成功解析所有视频元数据
    for (const FTakeMetadata::FVideo& Video : VideoMetadata)
    {
        // 处理每个视频流的元数据
        // 包含时间码信息，已修复首帧为分数帧号的情况
        // 支持任意帧率（不仅限于 30/60 FPS）
    }
}
```

## Demo 示例

### LiveLinkFaceMetadataParser.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "CaptureManagerTakeMetadata.h"

class FLiveLinkFaceMetadataParser
{
public:
    /**
     * 从文件路径解析 LiveLink Face 元数据
     * @param InJsonFilePath JSON 文件的完整路径
     * @param OutTakeMetadata 输出的 take 元数据
     * @return 解析是否成功
     */
    static bool ParseFromFile(const FString& InJsonFilePath, FTakeMetadata& OutTakeMetadata);

    /**
     * 从 JSON 字符串解析视频元数据
     * @param InJsonString JSON 字符串内容
     * @param OutVideoMetadata 输出的视频元数据数组
     * @return 解析是否成功
     */
    static bool ParseVideoFromString(const FString& InJsonString, TArray<FTakeMetadata::FVideo>& OutVideoMetadata);
};
```

### LiveLinkFaceMetadataParser.cpp

```cpp
#include "LiveLinkFaceMetadataParser.h"
#include "LiveLinkFaceMetadata.h"

bool FLiveLinkFaceMetadataParser::ParseFromFile(
    const FString& InJsonFilePath, 
    FTakeMetadata& OutTakeMetadata)
{
    TArray<FText> ValidationErrors;
    
    TOptional<FTakeMetadata> Result = 
        UE::CaptureManager::LiveLinkMetadata::ParseOldLiveLinkTakeMetadata(
            InJsonFilePath, 
            ValidationErrors
        );
    
    if (Result.IsSet())
    {
        OutTakeMetadata = Result.GetValue();
        return true;
    }
    
    // 输出所有验证错误以便调试
    for (const FText& Error : ValidationErrors)
    {
        UE_LOG(LogTemp, Error, TEXT("LiveLinkFaceMetadata: %s"), *Error.ToString());
    }
    
    return false;
}

bool FLiveLinkFaceMetadataParser::ParseVideoFromString(
    const FString& InJsonString, 
    TArray<FTakeMetadata::FVideo>& OutVideoMetadata)
{
    TArray<FText> ValidationErrors;
    
    OutVideoMetadata = 
        UE::CaptureManager::LiveLinkMetadata::ParseOldLiveLinkVideoMetadataFromString(
            InJsonString, 
            ValidationErrors
        );
    
    if (ValidationErrors.Num() > 0)
    {
        for (const FText& Error : ValidationErrors)
        {
            UE_LOG(LogTemp, Warning, TEXT("LiveLinkFaceMetadata validation: %s"), *Error.ToString());
        }
        return false;
    }
    
    return OutVideoMetadata.Num() > 0;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `CaptureManagerTakeMetadata` | 提供 `FTakeMetadata` 数据结构定义，是本模块输出的核心类型 |

## 维护状态

### 近期更新

```
- ba9b67eaf089 Update frame log based timecode parsing to accept video frame rates other than 30 and 60 FPS.
  → 扩展了时间码解析能力，支持任意帧率而非仅限于 30/60 FPS
- 9991761df98e CaptureManager: Fixed LLF video timecode when the first frame is fractional and rounded up to an invalid frame number.
  → 修复了首帧为分数帧号时四舍五入导致无效帧号的边界情况
- 7054c07db887 [CaptureManager] Fix for live link face metadata rotation parsing
  → 修复了旋转信息解析的问题
```

### 维护评价

- **创建时间**：2025-02-04，非常新的模块
- **更新频率**：近期有 3 次实质性更新，集中在时间码解析和元数据解析的 bug 修复
- **维护状态**：活跃维护中，作为 CaptureManagerApp 大型插件的一部分持续迭代
- **已知限制**：专门处理"旧版"LiveLink Face 格式，新版本可能使用不同的元数据格式
- **推荐使用**：✅ 推荐。如果你的虚拟制片管线需要处理 LiveLink Face 的历史数据，这是官方支持的解析方案。模块虽然小但功能专注，且有 Epic 持续维护。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerApp/Source/LiveLinkFaceMetadata)
- [CaptureManagerApp 插件根目录](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerApp)
- [CaptureManagerTakeMetadata 模块](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerApp/Source/CaptureManagerTakeMetadata)