# Capture Manager Ingest Blueprint

> The Capture Manager Editor plugin is used for importing the Capture archive data into UE/UEFN to create necessary assets

| 属性 | 值 |
|---|---|
| 中文名 | 捕获管理蓝图导入 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `CaptureManagerDeviceBlueprint` (Runtime), `CaptureManagerEditorSettings` (Runtime), `CaptureManagerIngestBlueprint` (Runtime), `DataIngestCoreEditor` (Runtime), `LiveLinkHubDiscoveryEditor` (Runtime), `LiveLinkHubExportServer` (Runtime), `LiveLinkHubWorkerManager` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-04 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerEditor) | |

## 用途

CaptureManagerIngestBlueprint 模块提供了一套完整的蓝图 API，用于将各种影视捕获数据导入到 Unreal Engine 中。它能处理多种捕获格式——包括单目/立体视频、LiveLink Face（iPhone 面部捕获）、Take Archive（.cptake 归档文件）以及独立的标定文件——并自动转换为 UE 内部的 `UFootageCaptureData` 资产。

核心价值在于：无论你的捕获设备和格式如何，都可以通过统一的蓝图接口完成导入，无需关心底层的视频解码、图像序列提取、音频分离和标定文件解析等细节。模块内置了一个异步调度器，支持队列化导入任务、并发控制和任务取消。

## 使用场景

- 你在使用 iPhone LiveLink Face App 捕获面部表演数据，需要导入到 UE 中制作 Metahuman 动画 → 使用 `IngestLiveLinkFace`
- 你有一段用专业摄影机拍摄的单目视频素材，需要作为场景参考导入 → 使用 `IngestMonoVideo`
- 你用立体摄影机（双目）拍摄了两个视角的视频，并带有标定文件 → 使用 `IngestStereoVideo`
- 你从 Capture Manager 或其他工具导出了 `.cptake` 归档包 → 使用 `IngestTakeArchive`
- 你有一个独立的相机标定 JSON 文件需要导入 → 使用 `IngestCalibration`
- 你需要批量扫描某个目录下所有可用的捕获素材 → 使用 `FindTakeDirectories`

## 蓝图用法

### 枚举类型

| 枚举 | 说明 |
|---|---|
| `ECaptureManagerIngestType` | 描述导入路径类型：MonoVideo、StereoVideo、LiveLinkFace、TakeArchive、Calibration |
| `ECaptureManagerImageFormat` | 图像输出格式：PNG、JPG |
| `ECaptureManagerAudioFormat` | 音频输出格式：WAV |

### 结构体

| 结构体 | 说明 |
|---|---|
| `FCaptureManagerConversionParams` | 导入转换参数：图像/音频格式、文件前缀、像素格式、旋转方式 |
| `FCaptureManagerTakeDirectoryInfo` | 目录扫描结果：路径、是否为 Take Archive、是否为 LiveLink Face、视频/图像序列/音频/标定文件列表 |

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IngestTakeArchive` | 异步导入 .cptake 归档包 | `UCaptureManagerIngestBlueprintLibrary` |
| `IngestTakeArchiveSync` | 同步导入 .cptake 归档包（阻塞） | `UCaptureManagerIngestBlueprintLibrary` |
| `IngestMonoVideo` | 异步导入单目视频文件 | `UCaptureManagerIngestBlueprintLibrary` |
| `IngestMonoVideoSync` | 同步导入单目视频文件（阻塞） | `UCaptureManagerIngestBlueprintLibrary` |
| `IngestStereoVideo` | 异步导入立体（双目）视频 | `UCaptureManagerIngestBlueprintLibrary` |
| `IngestStereoVideoSync` | 同步导入立体视频（阻塞） | `UCaptureManagerIngestBlueprintLibrary` |
| `IngestLiveLinkFace` | 异步导入 LiveLink Face 面部捕获数据 | `UCaptureManagerIngestBlueprintLibrary` |
| `IngestLiveLinkFaceSync` | 同步导入 LiveLink Face（阻塞） | `UCaptureManagerIngestBlueprintLibrary` |
| `IngestCalibration` | 异步导入独立标定文件 | `UCaptureManagerIngestBlueprintLibrary` |
| `IngestCalibrationSync` | 同步导入标定文件（阻塞） | `UCaptureManagerIngestBlueprintLibrary` |
| `CancelIngest` | 取消队列中或正在运行的导入任务 | `UCaptureManagerIngestBlueprintLibrary` |
| `FindTakeDirectories` | 扫描目录查找所有可用的捕获素材 | `UCaptureManagerIngestBlueprintLibrary` |

### 使用示例（蓝图描述）

**异步导入 LiveLink Face 捕获：**

1. 创建一个 `FCaptureManagerConversionParams` 结构体变量，设置图像格式为 PNG、像素格式等
2. 调用 `IngestLiveLinkFace`，传入 Take 目录路径和转换参数
3. 将 `OnSuccess` 委托连接到一个自定义事件，在事件中获取返回的 `UFootageCaptureData` 引用
4. 将 `OnFailure` 委托连接到另一个自定义事件，显示错误信息

**批量扫描目录并导入：**

1. 调用 `FindTakeDirectories`，传入根目录路径，设置 `bRecursive = true`
2. 遍历返回的 `TArray<FCaptureManagerTakeDirectoryInfo>` 数组
3. 对每个结果判断类型：`bIsTakeArchive` 为 true 则调用 `IngestTakeArchive`，`bIsLiveLinkFace` 为 true 则调用 `IngestLiveLinkFace`，否则根据 `VideoFiles` 判断调用 `IngestMonoVideo` 或 `IngestStereoVideo`

**取消进行中的导入：**

1. 保存异步导入节点返回的 `IngestId`（int32）
2. 需要取消时调用 `CancelIngest`，传入对应的 `IngestId`
3. 如果任务已启动，任务会在下一个检查点安全终止并清理临时文件

## C++ 用法

### 头文件引入

```cpp
#include "CaptureManagerIngestBlueprintLibrary.h"
```

### 基本用法

同步导入一个单目视频文件（来源：`Private/CaptureManagerIngestBlueprintLibrary.h`）：

```cpp
#include "CaptureManagerIngestBlueprintLibrary.h"

// 设置转换参数
FCaptureManagerConversionParams Params;
Params.ImageFormat = ECaptureManagerImageFormat::Png;
Params.AudioFormat = ECaptureManagerAudioFormat::Wav;
Params.PixelFormat = ECaptureManagerPixelFormat::U8_BGRA;
Params.Rotation = ECaptureManagerRotation::Auto;

// 同步导入单目视频
FText ErrorMessage;
UFootageCaptureData* CaptureData = UCaptureManagerIngestBlueprintLibrary::IngestMonoVideoSync(
    TEXT("/Path/To/video.mp4"),          // 视频路径
    TEXT(""),                             // 无独立音频文件
    TEXT("MySlate"),                      // Slate 名称
    1,                                    // Take 编号
    Params,
    ErrorMessage
);

if (CaptureData)
{
    // 导入成功，使用 CaptureData
    UE_LOG(LogTemp, Log, TEXT("导入成功，资产路径: %s"), *CaptureData->GetPathName());
}
else
{
    UE_LOG(LogTemp, Error, TEXT("导入失败: %s"), *ErrorMessage.ToString());
}
```

### 进阶用法

异步导入 + 取消（综合 `CaptureManagerIngestBlueprintLibrary.h` 和 `CaptureManagerIngestDispatcher.h`）：

```cpp
#include "CaptureManagerIngestBlueprintLibrary.h"

FCaptureManagerConversionParams Params;
Params.ImageFormat = ECaptureManagerImageFormat::Png;

// 异步导入 Take Archive
int32 IngestId = UCaptureManagerIngestBlueprintLibrary::IngestTakeArchive(
    TEXT("/Path/To/Take.cptake"),
    Params,
    // OnSuccess 回调
    FCaptureManagerIngestSuccess::CreateLambda(
        [](int32 Id, ECaptureManagerIngestType Type, UFootageCaptureData* Data)
        {
            UE_LOG(LogTemp, Log, TEXT("异步导入成功: ID=%d, 类型=%d"), Id, static_cast<int32>(Type));
        }
    ),
    // OnFailure 回调
    FCaptureManagerIngestFailed::CreateLambda(
        [](int32 Id, ECaptureManagerIngestType Type, FText Error)
        {
            UE_LOG(LogTemp, Error, TEXT("异步导入失败: ID=%d, 错误: %s"), Id, *Error.ToString());
        }
    )
);

// 稍后需要取消
bool bCancelled = UCaptureManagerIngestBlueprintLibrary::CancelIngest(IngestId);
UE_LOG(LogTemp, Log, TEXT("取消结果: %s"), bCancelled ? TEXT("成功") : TEXT("已不存在"));
```

扫描目录并遍历结果（来源：`Private/CaptureManagerFindTakes.h`、`Private/CaptureManagerIngestBlueprintLibrary.h`）：

```cpp
TArray<FCaptureManagerTakeDirectoryInfo> Results = 
    UCaptureManagerIngestBlueprintLibrary::FindTakeDirectories(
        TEXT("/Path/To/Captures"), true);

for (const FCaptureManagerTakeDirectoryInfo& Info : Results)
{
    UE_LOG(LogTemp, Log, TEXT("目录: %s"), *Info.Path);
    UE_LOG(LogTemp, Log, TEXT("  是否 Take Archive: %s"), Info.bIsTakeArchive ? TEXT("是") : TEXT("否"));
    UE_LOG(LogTemp, Log, TEXT("  是否 LiveLink Face: %s"), Info.bIsLiveLinkFace ? TEXT("是") : TEXT("否"));
    UE_LOG(LogTemp, Log, TEXT("  视频文件数: %d"), Info.VideoFiles.Num());
    UE_LOG(LogTemp, Log, TEXT("  图像序列目录数: %d"), Info.ImageSeqDirs.Num());
    UE_LOG(LogTemp, Log, TEXT("  音频文件数: %d"), Info.AudioFiles.Num());
    UE_LOG(LogTemp, Log, TEXT("  标定文件数: %d"), Info.CalibrationFiles.Num());
}
```

## Demo 示例

```cpp
// MyCaptureImporter.h
#pragma once

#include "CoreMinimal.h"
#include "CaptureManagerIngestBlueprintLibrary.h"
#include "MyCaptureImporter.generated.h"

UCLASS(BlueprintType)
class UMyCaptureImporter : public UObject
{
    GENERATED_BODY()

public:
    // 在蓝图或 C++ 中调用此函数导入捕获数据
    UFUNCTION(BlueprintCallable, Category = "MyTools")
    void ImportCaptureData(const FString& DirectoryPath);

    // 检查目录中有哪些可用的捕获素材
    UFUNCTION(BlueprintCallable, Category = "MyTools")
    TArray<FCaptureManagerTakeDirectoryInfo> ScanForCaptures(const FString& DirectoryPath);

private:
    FCaptureManagerConversionParams GetDefaultConversionParams();
};
```

```cpp
// MyCaptureImporter.cpp
#include "MyCaptureImporter.h"

void UMyCaptureImporter::ImportCaptureData(const FString& DirectoryPath)
{
    TArray<FCaptureManagerTakeDirectoryInfo> Takes = ScanForCaptures(DirectoryPath);
    
    FCaptureManagerConversionParams Params = GetDefaultConversionParams();
    
    for (const FCaptureManagerTakeDirectoryInfo& Take : Takes)
    {
        if (Take.bIsTakeArchive)
        {
            // .cptake 归档包直接整体导入
            UCaptureManagerIngestBlueprintLibrary::IngestTakeArchive(
                Take.Path, Params,
                FCaptureManagerIngestSuccess::CreateLambda([](int32, ECaptureManagerIngestType, UFootageCaptureData* Data)
                {
                    UE_LOG(LogTemp, Log, TEXT("Take Archive 导入成功: %s"), *Data->GetName());
                }),
                FCaptureManagerIngestFailed::CreateLambda([](int32, ECaptureManagerIngestType, FText Error)
                {
                    UE_LOG(LogTemp, Error, TEXT("Take Archive 导入失败: %s"), *Error.ToString());
                })
            );
        }
        else if (Take.bIsLiveLinkFace)
        {
            // LiveLink Face 面部捕获
            UCaptureManagerIngestBlueprintLibrary::IngestLiveLinkFace(
                Take.Path, Params,
                FCaptureManagerIngestSuccess::CreateLambda([](int32, ECaptureManagerIngestType, UFootageCaptureData* Data)
                {
                    UE_LOG(LogTemp, Log, TEXT("LiveLink Face 导入成功: %s"), *Data->GetName());
                }),
                FCaptureManagerIngestFailed::CreateLambda([](int32, ECaptureManagerIngestType, FText Error)
                {
                    UE_LOG(LogTemp, Error, TEXT("LiveLink Face 导入失败: %s"), *Error.ToString());
                })
            );
        }
        else if (Take.VideoFiles.Num() >= 2)
        {
            // 两个视频文件视为立体视频
            UCaptureManagerIngestBlueprintLibrary::IngestStereoVideo(
                Take.VideoFiles[0], Take.VideoFiles[1],
                Take.AudioFiles.Num() > 0 ? Take.AudioFiles[0] : TEXT(""),
                Take.CalibrationFiles.Num() > 0 ? Take.CalibrationFiles[0] : TEXT(""),
                TEXT(""), 1, Params,
                FCaptureManagerIngestSuccess::CreateLambda([](int32, ECaptureManagerIngestType, UFootageCaptureData* Data)
                {
                    UE_LOG(LogTemp, Log, TEXT("立体视频导入成功: %s"), *Data->GetName());
                }),
                FCaptureManagerIngestFailed::CreateLambda([](int32, ECaptureManagerIngestType, FText Error)
                {
                    UE_LOG(LogTemp, Error, TEXT("立体视频导入失败: %s"), *Error.ToString());
                })
            );
        }
        else if (Take.VideoFiles.Num() == 1)
        {
            // 单个视频文件
            UCaptureManagerIngestBlueprintLibrary::IngestMonoVideo(
                Take.VideoFiles[0],
                Take.AudioFiles.Num() > 0 ? Take.AudioFiles[0] : TEXT(""),
                TEXT(""), 1, Params,
                FCaptureManagerIngestSuccess::CreateLambda([](int32, ECaptureManagerIngestType, UFootageCaptureData* Data)
                {
                    UE_LOG(LogTemp, Log, TEXT("单目视频导入成功: %s"), *Data->GetName());
                }),
                FCaptureManagerIngestFailed::CreateLambda([](int32, ECaptureManagerIngestType, FText Error)
                {
                    UE_LOG(LogTemp, Error, TEXT("单目视频导入失败: %s"), *Error.ToString());
                })
            );
        }
        
        // 单独处理标定文件
        for (const FString& CalibFile : Take.CalibrationFiles)
        {
            FText Error;
            UFootageCaptureData* CalibData = UCaptureManagerIngestBlueprintLibrary::IngestCalibrationSync(
                CalibFile, FPaths::GetBaseFilename(CalibFile), Error);
            if (CalibData)
            {
                UE_LOG(LogTemp, Log, TEXT("标定导入成功: %s"), *CalibData->GetName());
            }
        }
    }
}

TArray<FCaptureManagerTakeDirectoryInfo> UMyCaptureImporter::ScanForCaptures(const FString& DirectoryPath)
{
    return UCaptureManagerIngestBlueprintLibrary::FindTakeDirectories(DirectoryPath, true);
}

FCaptureManagerConversionParams UMyCaptureImporter::GetDefaultConversionParams()
{
    FCaptureManagerConversionParams Params;
    Params.ImageFormat = ECaptureManagerImageFormat::Png;
    Params.AudioFormat = ECaptureManagerAudioFormat::Wav;
    Params.PixelFormat = ECaptureManagerPixelFormat::U8_BGRA;
    Params.Rotation = ECaptureManagerRotation::Auto;
    return Params;
}
```

## 模块依赖

从源码分析，CaptureManagerIngestBlueprint 模块依赖 `FootageCaptureData`、`FTakeMetadata`、`FStopToken` 等类型，这些来自同插件的其他模块。无特殊外部依赖（仅标准 Core/Engine/Slate 等）。

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine/Slate 等） | |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-30 | `175468f6` | [CaptureManager] Generalize device terminology in DeviceBlueprint | 泛化 DeviceBlueprint 模块中的设备术语 |
| 2026-04-30 | `63a844fc` | [CaptureManager] Move blocking ingest Blueprint APIs to a Blocking subcategory. | 将同步阻塞导入 API 移至蓝图子分类 |
| 2026-04-30 | `d6f72591` | [CaptureManager] Add CaptureManagerDeviceBlueprint module | 新增 CaptureManagerDeviceBlueprint 模块 |
| 2026-04-29 | `5a664506` | [Backout] - CL53274396 | 回退之前的提交 CL53274396 |
| 2026-04-29 | `1c481042` | [CaptureManager] Add CaptureManagerDeviceBlueprint module | 首次添加 CaptureManagerDeviceBlueprint 模块（后被回退后重新提交） |

### 维护评价

- **活跃维护**：插件创建于 2025 年 2 月，最近一次更新在 2026 年 4 月 30 日，近期有密集的功能迭代（新增 DeviceBlueprint 模块、调整 API 分类等）
- 插件仍在积极扩展中，当前提交集中在增加新模块和优化蓝图 API 组织结构
- 默认未启用（`EnabledByDefault=false`），属于可选的虚拟制片功能模块
- 无已知废弃标记，整体处于活跃开发阶段
- **推荐使用**：如果你在做虚拟制片或影视捕获相关的项目，这是一个功能完善且持续维护的导入工具

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerEditor)
- [官方文档]()（暂无）