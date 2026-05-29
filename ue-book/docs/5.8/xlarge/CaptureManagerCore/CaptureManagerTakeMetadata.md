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

`CaptureManagerCore` 是虚拟制作（Virtual Production）工作流中捕获管理工具链的**核心基础层**。它并非一个最终用户直接使用的独立工具，而是为上层的 `CaptureManagerApp`（可能用于外部应用或设备控制）和 `CaptureManagerEditor`（用于引擎内编辑）插件提供一系列**共享的功能模块**。

这些模块共同解决了以下核心问题：
1.  **数据格式标准化**：定义和处理捕获会话（Take）的元数据结构（如 `FTakeMetadata`），确保不同工具间对捕获数据（视频、音频、校准、设备信息等）的描述一致。
2.  **协议与通信**：提供与捕获设备（如 iPhone、专业相机）进行通信的协议栈实现（`CaptureProtocolStack`、`CaptureManagerCPSClient`），以及与 Live Link Hub 等消息系统集成的能力。
3.  **数据转换与处理**：包含将原始捕获数据（如视频文件、深度信息）转换为引擎可用格式的转换器（`CaptureDataConverter`、`CaptureManagerMediaRW`）。
4.  **工作流工具**：提供数据摄入（`DataIngestCore`）、元数据提取（`CaptureMetadataExtraction`）等实用工具，构成完整的数据处理管线（`CaptureManagerPipeline`）。
5.  **资源与风格**：可能包含编辑器内使用的 UI 风格资源（`CaptureManagerStyle`）和通用工具函数（`CaptureUtils`）。

简而言之，这个插件的存在是为了**集中和固化虚拟制片中捕获相关的核心逻辑与规范**，避免在 App 和 Editor 插件中重复开发，并确保整个捕获管理生态的技术基础统一。

## 使用场景

-   **开发或扩展捕获管理工具**：如果你正在开发一个自定义的虚拟制作捕获管理系统或插件，并且需要处理来自专业设备（如 iPhone + Live Link Face）的捕获数据，那么你需要依赖 `CaptureManagerCore` 来解析标准的 Take 元数据文件（`.take`）、与设备通信或转换媒体格式。
-   **构建自定义数据处理管线**：当标准管线无法满足需求时，你可以利用此插件提供的模块（如 `CaptureManagerPipeline`、`DataIngestCore`）来构建自己的数据预处理、校验或集成流程。
-   **集成虚拟制片设备**：在需要将新的捕获设备（如新型相机、音频录制设备）集成到 Unreal Engine 工作流时，你可能需要基于 `CaptureProtocolStack` 模块来实现或适配通信协议。

## 蓝图用法

`CaptureManagerCore` 主要是一个 **C++ 模块集合**，其核心数据结构和功能（如 `FTakeMetadata`, `FTakeMetadataParser`）主要为 C++ 设计。它通常不直接暴露大量的 `BlueprintCallable` 节点给蓝图。

其与蓝图的交互主要体现在：
1.  **数据驱动**：蓝图系统（如编辑器工具）可能会读取或创建 `FTakeMetadata` 对象所代表的数据结构，但这些数据通常通过 JSON 文件或 C++ 层处理的 `UObject`/`UStruct` 包装后传递给蓝图。
2.  **作为依赖**：蓝图相关的功能更可能存在于上层的 `CaptureManagerEditor` 插件中，而 `CaptureManagerCore` 是这些功能的底层支撑。

### 核心节点（C++ 数据结构）

由于缺乏蓝图暴露的接口，以下列出的是驱动蓝图数据流的核心 C++ 类：

| 类/结构体 | 说明 | 所在模块 |
|---|---|---|
| `FTakeMetadata` | **核心数据结构**。代表一次捕获会话（Take）的完整元数据，包括设备信息、视频/音频/深度列表、校准信息、时间码、缩略图等。 | `CaptureManagerTakeMetadata` |
| `FTakeThumbnailData` | 处理捕获会话的缩略图数据，支持从文件路径、压缩数据或原始图像数据构造。 | `CaptureManagerTakeMetadata` |
| `FTakeMetadataParser` | **解析器**。用于将 `.take` JSON 文件解析成 `FTakeMetadata` 对象。 | `CaptureManagerTakeMetadata` |

### 使用示例（数据流描述）

1.  **从文件加载 Take 元数据**（在 C++ 中）：
    ```cpp
    FTakeMetadataParser Parser;
    auto Result = Parser.Parse(TEXT("/path/to/my_take.take"));
    if (Result.HasValue())
    {
        FTakeMetadata TakeData = Result.GetValue();
        // TakeData.Video[0].Name, TakeData.Device.Name 等...
    }
    ```
    解析得到的 `FTakeMetadata` 对象可以序列化为 `FJsonObject`，再转换为 `UObject` 或结构体，以便蓝图系统可以读取其属性。

2.  **在蓝图编辑器工具中显示 Take 信息**（概念性描述）：
    - 一个编辑器蓝图工具的 C++ 部分调用 `FTakeMetadataParser`。
    - 将解析后的 `FTakeMetadata` 数据映射到一个 `UObject`（如 `UTakeMetadataObject`）上，并暴露给蓝图。
    - 蓝图图表可以读取这个 `UObject` 的属性（`TakeNumber`, `Slate`, `Device.Name`, `Video[0].FrameRate` 等），并显示在 UI 上。

## C++ 用法

以下用法基于 `CaptureManagerTakeMetadata` 模块的公共头文件 `CaptureManagerTakeMetadata.h`。

### 头文件引入

```cpp
#include "CaptureManagerTakeMetadata.h"
```

### 基本用法：解析 Take 元数据文件

这是最常见的用法：从磁盘读取一个 `.take` JSON 文件并解析成结构化的 C++ 对象。

```cpp
// 引入头文件
#include "CaptureManagerTakeMetadata.h"

// 解析 .take 文件
void ParseTakeFile(const FString& TakeFilePath)
{
    FTakeMetadataParser Parser;
    // TValueOrError 用于返回成功值或错误
    auto ParseResult = Parser.Parse(TakeFilePath);

    if (ParseResult.HasError())
    {
        // 错误处理：可以获取错误来源（Reader/Validator/Parser）和消息
        FTakeMetadataParserError Error = ParseResult.GetError();
        UE_LOG(LogTemp, Error, TEXT("解析 Take 文件失败 (%d): %s"), (int32)Error.Origin, *Error.Message.ToString());
        return;
    }

    // 成功获取 FTakeMetadata 对象
    FTakeMetadata TakeData = ParseResult.GetValue();

    // 访问数据示例
    UE_LOG(LogTemp, Log, TEXT("Take Number: %d, Slate: %s"), TakeData.TakeNumber, *TakeData.Slate);
    UE_LOG(LogTemp, Log, TEXT("设备: %s %s"), *TakeData.Device.Name, *TakeData.Device.Type);

    // 遍历视频列表
    for (const FTakeMetadata::FVideo& VideoInfo : TakeData.Video)
    {
        UE_LOG(LogTemp, Log, TEXT("视频: %s, 路径: %s, 帧率: %.2f"), *VideoInfo.Name, *VideoInfo.Path, VideoInfo.FrameRate);
    }
}
```

### 进阶用法：处理缩略图和路径工具

```cpp
#include "CaptureManagerTakeMetadata.h"

void ProcessTakeThumbnailAndPaths(const FTakeMetadata& TakeData)
{
    // 1. 处理缩略图
    const FTakeThumbnailData& ThumbnailData = TakeData.Thumbnail;
    // 尝试获取原始图像数据（如果缩略图是以原始数据存储的）
    TOptional<FTakeThumbnailData::FRawImage> RawImage = ThumbnailData.GetRawImage();
    if (RawImage.IsSet())
    {
        // 使用 RawImage->DecompressedImageData, RawImage->Width, RawImage->Height
        UE_LOG(LogTemp, Log, TEXT("缩略图尺寸: %d x %d"), RawImage->Width, RawImage->Height);
    }

    // 2. 使用路径工具类
    if (TakeData.Video.Num() > 0)
    {
        const FString& VideoPath = TakeData.Video[0].Path;
        // 检测路径是文件还是文件夹
        FTakeMetadata::FVideo::EPathType DetectedType = FTakeMetadataPathUtils::DetectPathType(VideoPath);
        // 验证 TakeData 中记录的路径类型是否与实际匹配
        if (TakeData.Video[0].PathType.IsSet())
        {
            bool bIsValid = FTakeMetadataPathUtils::ValidatePathType(VideoPath, TakeData.Video[0].PathType.GetValue());
            UE_LOG(LogTemp, Log, TEXT("视频路径类型验证: %s"), bIsValid ? TEXT("通过") : TEXT("失败"));
        }
    }
}
```

## Demo 示例

一个最小化的示例，展示如何使用 `CaptureManagerTakeMetadata` 模块解析文件并读取信息。

### MyTakeLoader.h
```cpp
// MyTakeLoader.h
#pragma once

#include "CoreMinimal.h"
#include "CaptureManagerTakeMetadata.h"

class FMyTakeLoader
{
public:
    /** 加载并打印Take文件信息 */
    static void LoadAndPrintTakeInfo(const FString& TakeFilePath);
};
```

### MyTakeLoader.cpp
```cpp
// MyTakeLoader.cpp
#include "MyTakeLoader.h"
#include "HAL/PlatformFilemanager.h"

void FMyTakeLoader::LoadAndPrintTakeInfo(const FString& TakeFilePath)
{
    // 1. 检查文件是否存在
    if (!FPlatformFileManager::Get().GetPlatformFile().FileExists(*TakeFilePath))
    {
        UE_LOG(LogTemp, Error, TEXT("文件不存在: %s"), *TakeFilePath);
        return;
    }

    // 2. 创建解析器并解析文件
    FTakeMetadataParser Parser;
    auto Result = Parser.Parse(TakeFilePath);

    if (!Result.HasValue())
    {
        UE_LOG(LogTemp, Error, TEXT("解析文件失败: %s"), *TakeFilePath);
        return;
    }

    // 3. 获取并使用元数据
    const FTakeMetadata& Metadata = Result.GetValue();

    UE_LOG(LogTemp, Display, TEXT("=== Take 信息 ==="));
    UE_LOG(LogTemp, Display, TEXT("Slate: %s"), *Metadata.Slate);
    UE_LOG(LogTemp, Display, TEXT("Take 号: %d"), Metadata.TakeNumber);
    UE_LOG(LogTemp, Display, TEXT("设备: %s (%s)"), *Metadata.Device.Name, *Metadata.Device.Type);

    // 打印视频信息
    for (int32 i = 0; i < Metadata.Video.Num(); ++i)
    {
        const FTakeMetadata::FVideo& Video = Metadata.Video[i];
        UE_LOG(LogTemp, Display, TEXT("视频 %d: %s, %s, %.2f fps"), i, *Video.Name, *Video.Path, Video.FrameRate);
    }

    // 打印音频信息
    for (int32 i = 0; i < Metadata.Audio.Num(); ++i)
    {
        const FTakeMetadata::FAudio& Audio = Metadata.Audio[i];
        UE_LOG(LogTemp, Display, TEXT("音频 %d: %s, 路径: %s"), i, *Audio.Name, *Audio.Path);
    }

    // 打印缩略图状态
    if (Metadata.Thumbnail.GetThumbnailPath().IsSet())
    {
        UE_LOG(LogTemp, Display, TEXT("缩略图路径: %s"), *Metadata.Thumbnail.GetThumbnailPath().GetValue());
    }
}
```

## 模块依赖

基于 `CaptureManagerTakeMetadata` 模块的 `Build.cs` 文件，该模块的主要外部依赖如下：

| 模块 | 用途 |
|---|---|
| `Json` | 用于解析 `.take` 文件中的 JSON 数据。 |
| `JsonUtilities` | 提供 JSON 对象与 `UObject`/`UStruct` 之间转换的实用工具。 |

**其他模块说明**：此插件的所有模块（如 `CaptureProtocolStack`, `CaptureUtils`）可能各自依赖不同的特定模块，但作为使用者，当你直接依赖 `CaptureManagerTakeMetadata` 时，只需确保上述 `Json` 和 `JsonUtilities` 模块在你的 `.Build.cs` 中被正确引用即可。其他依赖会由模块系统自动传递或需要根据你具体使用的模块进行添加。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `a2e4a9e3` | Forward the stop token to third-party encoder commands so audio and video conversion can be cancelle | 将停止令牌转发给第三方编码器命令，使得音频和视频转换过程可被取消。 |
| 2026-05-12 | `218704d7` | [CaptureManager] Added missing fix from 51621159 which was dropped during conversion module move. | 修复了在模块迁移过程中遗漏的一个已知问题修正。 |
| 2026-05-12 | `16e184f7` | [CaptureManager] Fix transaction ID data race causing transient download failures. | 修复了由事务ID数据竞争引起的偶发性下载失败问题。 |
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构了 FJsonObject 以支持 FString 和 UE::FSharedString 两种字符串类型。 |
| 2026-04-30 | `d6f72591` | [CaptureManager] Add CaptureManagerDeviceBlueprint module | 新增了 `CaptureManagerDeviceBlueprint` 模块（注：此模块可能属于同级其他插件或为新增）。 |

### 维护评价

-   **创建时间**：插件于 2025 年 2 月创建，非常年轻。
-   **维护状态**：**活跃维护**。最近一次更新（2026-05-13）是功能增强（支持可取消的媒体转换），且近期有多次重要的 Bug 修复（如数据竞争问题）。更新频率稳定，表明 Epic 正在积极发展虚拟制片工作流。
-   **已知问题/限制**：作为一个较新的插件，其 API 可能会随着虚拟制片管线的成熟而发生变化。`EnabledByDefault` 为 `false` 表明它目前可能处于集成测试或需要用户显式启用的阶段。
-   **推荐**：**推荐使用**。对于正在使用或计划使用 Unreal Engine 进行专业虚拟制片（尤其是涉及外部设备捕获）的项目，此插件是构建可靠、可扩展捕获管理系统的基石。它由 Epic 官方维护，质量有保障。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerCore)