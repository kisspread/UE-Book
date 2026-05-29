# Capture Data

> Classes releated to captured data

| 属性 | 值 |
|---|---|
| 中文名 | 捕获数据 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（捕获数据资产类定义） |
| 模块 | `CaptureDataCore` (Runtime), `CaptureDataEditor` (Editor), `CaptureDataUtils` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-09-04 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureData) | |

## 用途

CaptureData 插件是 MetaHuman 工作流中用于管理和处理**面部捕获数据**的核心基础设施。它提供了以下数据模型：

- **UCaptureData**：所有捕获数据的抽象基类，定义了初始化检查和变更通知接口
- **UMeshCaptureData**：存储代表面部表情（Pose）的网格数据，用于在 MetaHuman Identity 中生成骨骼网格体
- **UFootageCaptureData**：存储视频素材数据，包括 RGB 图像序列、深度序列、音频轨道和相机标定信息，是 MetaHuman Performance 从视频生成动画的关键输入
- **UCameraCalibration**：管理用于 MetaHuman 工作流的相机标定参数，支持镜头文件和立体对配置

此外还提供了坐标系转换（OpenCV ↔ Unreal）、图像序列工具、帧范围管理等实用工具。

简而言之：**这个插件定义了"怎么存储和验证面部捕获数据"，是整个 MetaHuman 捕获管线的数据层。**

## 使用场景

- 你在使用 iPhone 或头戴摄像机拍摄面部素材，需要将捕获数据导入 UE 进行 MetaHuman 创建 → 使用 `UFootageCaptureData`
- 你有一个已扫描的面部网格，需要用于 MetaHuman Identity 适配 → 使用 `UMeshCaptureData`
- 你需要管理多相机标定数据（含立体对）用于 3D 重建 → 使用 `UCameraCalibration`
- 你在处理图像序列时需要获取路径、文件列表、分辨率等信息 → 使用 `FImageSequenceUtils`
- 你需要在 OpenCV 坐标系和 Unreal 坐标系之间转换变换矩阵 → 使用 `FOpenCVHelperLocal`
- 你需要管理捕获数据中需要排除的帧区间 → 使用 `FFrameRange` 相关功能

## 蓝图用法

此插件隐藏（`Hidden: true`），主要面向编辑器工具和 C++ 代码，但核心数据结构暴露了部分蓝图属性。

### 核心资产属性

**UFootageCaptureData** 资产中可在编辑器中配置的蓝图属性：

| 属性 | 类型 | 说明 |
|---|---|---|
| `ImageSequences` | `TArray<UImgMediaSource*>` | RGB 图像序列列表 |
| `DepthSequences` | `TArray<UImgMediaSource*>` | 深度图像序列列表 |
| `AudioTracks` | `TArray<USoundWave*>` | 音频轨道列表 |
| `CameraCalibrations` | `TArray<UCameraCalibration*>` | 相机标定资产列表 |
| `Metadata` | `FFootageCaptureMetadata` | 素材元数据（设备类型、帧率等） |
| `CaptureExcludedFrames` | `TArray<FFrameRange>` | 需排除的帧区间 |

**UMeshCaptureData** 资产中可在编辑器中配置的蓝图属性：

| 属性 | 类型 | 说明 |
|---|---|---|
| `TargetMesh` | `UObject*` | 目标网格（StaticMesh 或 SkeletalMesh） |

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IsInitialized` | 检查捕获数据是否已完整初始化 | `UCaptureData` |
| `GetFootageColorResolution` | 获取素材的颜色通道分辨率 | `UFootageCaptureData` |
| `GetEffectiveImageTimecode` | 获取指定视角的有效图像时间码 | `UFootageCaptureData` |
| `GetEffectiveDepthTimecode` | 获取指定视角的有效深度时间码 | `UFootageCaptureData` |
| `GetEffectiveAudioTimecode` | 获取音频的有效时间码 | `UFootageCaptureData` |
| `VerifyData` | 验证捕获数据完整性，返回成功或错误信息 | `UFootageCaptureData` |
| `GetDataForConforming` | 获取用于面部适配 API 的顶点和三角形数据 | `UMeshCaptureData` |
| `SetDeviceClass` | 根据设备型号字符串设置设备类别 | `FFootageCaptureMetadata` |
| `PopulateCameraNames` | 填充素材中所有 RGB 相机名称列表 | `UFootageCaptureData` |

### 使用示例（蓝图描述）

**验证素材数据完整性：**

1. 获取 `UFootageCaptureData` 资产引用
2. 调用 `VerifyData` 节点，传入 `ECaptureDataInitializedCheck` 参数（Full 或 ImageSequencesOnly）
3. 结果为 `TValueOrError` 类型：成功则继续处理，失败则包含错误信息字符串
4. 可通过 `IsInitialized` 节点快速预检

**获取帧范围用于处理：**

1. 获取 `UFootageCaptureData` 引用
2. 调用 `GetFrameRanges`，传入目标帧率和时间码对齐方式
3. 输出包含：每个媒体的帧范围映射、处理帧范围、最大帧范围
4. 用于确定视频处理管线的实际处理区间

## C++ 用法

### 头文件引入

```cpp
// 核心数据类
#include "CaptureData.h"

// 相机标定
#include "CameraCalibration.h"

// 图像序列工具
#include "ImageSequenceUtils.h"

// OpenCV 坐标系转换
#include "OpenCVHelperLocal.h"

// 帧范围
#include "FrameRange.h"
```

### 基本用法

**创建和使用 FootageCaptureData 资产**（基于源码结构推断）：

```cpp
#include "CaptureData.h"

// 创建 FootageCaptureData 资产
UFootageCaptureData* CaptureData = NewObject<UFootageCaptureData>(GetTransientPackage(), TEXT("MyCapture"));

// 验证数据完整性
UCaptureData::FVerifyResult Result = CaptureData->VerifyData(ECaptureDataInitializedCheck::Full);
if (Result.HasError())
{
    UE_LOG(LogCaptureDataCore, Error, TEXT("Capture data validation failed: %s"), *Result.GetError());
}
```

**检查素材分辨率和时间码**：

```cpp
// 获取颜色通道分辨率
FIntPoint Resolution = CaptureData->GetFootageColorResolution();

// 获取有效时间码（某些轨道可能没有设置时间码，会从其他轨道推导）
FTimecode EffectiveTimecode = CaptureData->GetEffectiveImageTimecode(0);
FFrameRate EffectiveRate = CaptureData->GetEffectiveImageTimecodeRate(0);

// 获取帧范围
TMap<TWeakObjectPtr<UObject>, TRange<FFrameNumber>> MediaFrameRanges;
TRange<FFrameNumber> ProcessingRange;
TRange<FFrameNumber> MaxRange;
CaptureData->GetFrameRanges(
    FFrameRate(30, 1),
    ETimecodeAlignment::Absolute,
    true,  // 包含音频
    MediaFrameRanges,
    ProcessingRange,
    MaxRange
);
```

**使用 MeshCaptureData 获取网格数据**：

```cpp
#include "CaptureData.h"

UMeshCaptureData* MeshCapture = /* 获取资产引用 */;

// 获取用于面部适配的数据
TArray<float> Vertices;
TArray<int32> Triangles;
FTransform IdentityTransform = FTransform::Identity;
MeshCapture->GetDataForConforming(IdentityTransform, Vertices, Triangles);
```

### 进阶用法

**相机标定数据导入导出**（基于 `UCameraCalibration` 源码）：

```cpp
#include "CameraCalibration.h"

UCameraCalibration* Calibration = NewObject<UCameraCalibration>();

// 从 TrackerNode 格式转换相机标定
TArray<FCameraCalibration> InCalibrations;
// ... 填充标定数据 ...
bool bSuccess = Calibration->ConvertFromTrackerNodeCameraModels(InCalibrations, true);

// 导出为 TrackerNode 格式
TArray<FCameraCalibration> OutCalibrations;
TArray<TPair<FString, FString>> StereoPairs;
bSuccess = Calibration->ConvertToTrackerNodeCameraModels(OutCalibrations, StereoPairs);
```

**OpenCV ↔ Unreal 坐标系转换**：

```cpp
#include "OpenCVHelperLocal.h"

// 转换变换矩阵
FTransform MyTransform;
FOpenCVHelperLocal::ConvertOpenCVToUnreal(MyTransform);  // OpenCV → Unreal
FOpenCVHelperLocal::ConvertUnrealToOpenCV(MyTransform);  // Unreal → OpenCV

// 转换向量
FVector OpenCVPosition(1.0, 2.0, 3.0);
FVector UnrealPosition = FOpenCVHelperLocal::ConvertOpenCVToUnreal(OpenCVPosition);

// 自定义轴映射转换
FOpenCVHelperLocal::ConvertCoordinateSystem(
    MyTransform,
    FOpenCVHelperLocal::EAxis::X,   // 目标 X 轴 = 源 X 轴
    FOpenCVHelperLocal::EAxis::Zn,  // 目标 Y 轴 = 源 -Z 轴
    FOpenCVHelperLocal::EAxis::Yn   // 目标 Z 轴 = 源 -Y 轴
);
```

**图像序列路径检查**：

```cpp
#include "ImageSequenceUtils.h"
#include "ImageSequencePathChecker.h"

// 获取图像序列信息
UImgMediaSource* ImgSource = /* 获取引用 */;
FString FullPath;
TArray<FString> ImageFiles;
FImageSequenceUtils::GetImageSequencePathAndFilesFromAsset(ImgSource, FullPath, ImageFiles);

// 获取分辨率和帧数
FIntVector2 Dimensions;
int32 NumImages;
FImageSequenceUtils::GetImageSequenceInfoFromAsset(ImgSource, Dimensions, NumImages);

// 批量检查路径有效性
using namespace UE::CaptureData;
FImageSequencePathChecker PathChecker(FText::FromString(TEXT("My Capture")));
PathChecker.Check(*CaptureData);
if (PathChecker.HasError())
{
    PathChecker.DisplayDialog();
}
```

**帧范围管理**：

```cpp
#include "FrameRange.h"

// 检查帧是否在排除列表中
TArray<FFrameRange> ExcludedFrames;
FFrameRange Range;
Range.Name = TEXT("Bad Takes");
Range.StartFrame = 100;
Range.EndFrame = 150;
ExcludedFrames.Add(Range);

bool bIsExcluded = FFrameRange::ContainsFrame(120, ExcludedFrames);  // true

// 将连续帧号打包为帧范围
TArray<FFrameNumber> FrameNumbers;
FrameNumbers.Add(FFrameNumber(1));
FrameNumbers.Add(FFrameNumber(2));
FrameNumbers.Add(FFrameNumber(3));
FrameNumbers.Add(FFrameNumber(10));
FrameNumbers.Add(FFrameNumber(11));
TArray<FFrameNumber> PackedRanges = PackIntoFrameRanges(FrameNumbers);
// 结果: [1-3], [10-11]
```

## Demo 示例

以下展示如何创建一个工具类，读取和验证 FootageCaptureData 资产：

### CaptureDataValidator.h

```cpp
#pragma once

#include "CoreMinimal.h"

class UFootageCaptureData;
enum class ECaptureDataInitializedCheck : uint8;

/**
 * 简单的捕获数据验证工具
 * 演示如何使用 CaptureData 插件的核心功能
 */
class FCaptureDataValidator
{
public:
    /** 验证指定的 FootageCaptureData 资产 */
    static bool ValidateCaptureData(UFootageCaptureData* InCaptureData);

    /** 打印捕获数据摘要信息 */
    static void PrintCaptureDataSummary(UFootageCaptureData* InCaptureData);
};
```

### CaptureDataValidator.cpp

```cpp
#include "CaptureDataValidator.h"

#include "CaptureData.h"
#include "CameraCalibration.h"
#include "ImageSequenceUtils.h"
#include "CaptureDataLog.h"

bool FCaptureDataValidator::ValidateCaptureData(UFootageCaptureData* InCaptureData)
{
    if (!InCaptureData)
    {
        UE_LOG(LogCaptureDataCore, Error, TEXT("CaptureData is null"));
        return false;
    }

    // 检查初始化状态
    if (!InCaptureData->IsInitialized(ECaptureDataInitializedCheck::ImageSequencesOnly))
    {
        UE_LOG(LogCaptureDataCore, Warning, TEXT("CaptureData '%s' is not initialized (image sequences check)"),
            *InCaptureData->GetName());
    }

    // 执行完整验证
    UFootageCaptureData::FVerifyResult Result = InCaptureData->VerifyData(ECaptureDataInitializedCheck::Full);
    if (Result.HasError())
    {
        UE_LOG(LogCaptureDataCore, Error, TEXT("Validation failed for '%s': %s"),
            *InCaptureData->GetName(), *Result.GetError());
        return false;
    }

    // 检查图像序列路径
    TArray<UFootageCaptureData::FPathAssociation> InvalidPaths = InCaptureData->CheckImageSequencePaths();
    for (const auto& PathAssoc : InvalidPaths)
    {
        UE_LOG(LogCaptureDataCore, Warning, TEXT("Missing path for '%s': %s (Asset: %s)"),
            *InCaptureData->GetName(), *PathAssoc.PathOnDisk, *PathAssoc.AssetPath);
    }

    return InvalidPaths.Num() == 0;
}

void FCaptureDataValidator::PrintCaptureDataSummary(UFootageCaptureData* InCaptureData)
{
    if (!InCaptureData)
    {
        return;
    }

    FIntPoint Resolution = InCaptureData->GetFootageColorResolution();
    UE_LOG(LogCaptureDataCore, Log, TEXT("=== CaptureData Summary: %s ==="), *InCaptureData->GetName());
    UE_LOG(LogCaptureDataCore, Log, TEXT("  Color Resolution: %dx%d"), Resolution.X, Resolution.Y);
    UE_LOG(LogCaptureDataCore, Log, TEXT("  Image Sequences: %d"), InCaptureData->ImageSequences.Num());
    UE_LOG(LogCaptureDataCore, Log, TEXT("  Depth Sequences: %d"), InCaptureData->DepthSequences.Num());
    UE_LOG(LogCaptureDataCore, Log, TEXT("  Audio Tracks: %d"), InCaptureData->AudioTracks.Num());
    UE_LOG(LogCaptureDataCore, Log, TEXT("  Camera Calibrations: %d"), InCaptureData->CameraCalibrations.Num());
    UE_LOG(LogCaptureDataCore, Log, TEXT("  Device: %s"), *UEnum::GetValueAsString(InCaptureData->Metadata.DeviceClass));
    UE_LOG(LogCaptureDataCore, Log, TEXT("  Frame Rate: %.2f"), InCaptureData->Metadata.FrameRate);
    UE_LOG(LogCaptureDataCore, Log, TEXT("  Excluded Frames: %d ranges"), InCaptureData->CaptureExcludedFrames.Num());

    // 打印有效时间码
    if (InCaptureData->ImageSequences.Num() > 0)
    {
        FTimecode ImgTC = InCaptureData->GetEffectiveImageTimecode(0);
        FFrameRate ImgRate = InCaptureData->GetEffectiveImageTimecodeRate(0);
        UE_LOG(LogCaptureDataCore, Log, TEXT("  Effective Image Timecode: %s @ %.2fps"),
            *ImgTC.ToString(), ImgRate.AsDecimal());
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ImgMedia` | 图像序列媒体源（UImgMediaSource）支持 |
| `CameraCalibrationCore` | 镜头文件（ULensFile）和相机标定核心功能 |
| `MediaUtils` | 媒体工具（EMediaOrientation 等） |
| `AssetRegistry` | 资产注册标签（GetAssetRegistryTags） |

编辑器模块额外依赖：

| 模块 | 用途 |
|---|---|
| `EditorScriptingUtilities` | 编辑器脚本工具 |
| `ToolMenus` | 工具菜单扩展（ContentBrowser MetaHuman 菜单） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `d3aefcf1` | Improve timecode and frame rate resolution in capture data by independently validating each value | 改进时间码和帧率验证，改为逐个独立验证各值 |
| 2026-04-14 | `54e43b2d` | Added log messages to ImageSequenceUtils | 为图像序列工具添加日志输出 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF | 迁移日志宏到新的 UE_LOGF 格式 |
| 2026-04-06 | `65adeb26` | [ContentBrowser] New Add Menu MetaHuman Menu | 在内容浏览器新增 MetaHuman 菜单项 |
| 2026-03-31 | `99ca17a7` | [Capture Manager] Improved handling of non-integer frame rates | 改进非整数帧率的处理逻辑 |

### 维护评价

**活跃维护中** ✅

- **创建时间**：2024 年 9 月，是一个相对新的插件
- **更新频率**：近期（2026年3-5月）有持续的功能改进和代码维护，平均每 1-2 周有更新
- **更新内容**：涵盖功能改进（时间码验证、帧率处理）、代码质量提升（日志迁移）、UI 集成（ContentBrowser 菜单）
- **隐藏状态**：插件标记为 `Hidden: true`，说明它是 MetaHuman 工作流的内部基础设施，不直接面向终端用户
- **API 稳定性**：源码中可见多处 `DeprecatedProperty` 和版本迁移代码（如 `Views_DEPRECATED`、`Audio_DEPRECATED`），说明 API 在持续演进但保持了向后兼容

**推荐使用**：如果你在开发 MetaHuman 相关的自定义工具或管线，可以放心依赖此插件。但注意它是隐藏插件，API 可能会随 MetaHuman 工作流需求而变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureData)
- [官方文档]()（无）
- [MetaHuman 文档](https://docs.unrealengine.com/en-US/metahuman-in-unreal-engine/)