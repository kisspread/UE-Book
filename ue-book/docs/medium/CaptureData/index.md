# Capture Data

> Classes releated to captured data

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产定义、编辑器自定义） |
| 模块 | `CaptureDataCore` (Runtime), `CaptureDataEditor` (Editor), `CaptureDataUtils` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-09-04 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureData) | |

## 用途

CaptureData 是 MetaHuman 工作流的核心数据层插件。它定义了两类捕获数据资产（Mesh Capture Data 和 Footage Capture Data）以及配套的相机标定资产，用于将真人面部捕获数据导入 UE5 并驱动 MetaHuman Identity 和 Performance 工作流。

具体来说，这个插件解决以下问题：

- **Mesh Capture Data**：存储面部表情的网格数据（Pose），用于 MetaHuman Identity 生成与真人相似的 Skeletal Mesh
- **Footage Capture Data**：存储面部捕获视频片段（图像序列 + 深度序列 + 音频），包含 timecode 同步、帧范围管理、设备元数据等
- **Camera Calibration**：存储相机内参和畸变参数（支持 OpenCV 模型），用于从捕获素材重建 3D 面部
- **Timecode 工具**：在 SoundWave 和 ImageSequence 上读写 timecode 信息，实现多轨素材同步

该插件是 Hidden 的（`.uplugin` 中 `Hidden: true`），不会出现在插件浏览器中，而是被其他 MetaHuman 相关插件（如 MetaHuman Identity、MetaHuman Performance）内部依赖。

## 使用场景

- 你在做 MetaHuman 面部捕获 → 用 Footage Capture Data 存储 iPhone/HMC 拍摄的面部视频
- 你有 3D 扫描的面部网格 → 用 Mesh Capture Data 存储 mesh pose 用于 Identity 匹配
- 你需要导入 `.mhaical` 相机标定文件 → 用 Camera Calibration 资产管理多相机标定参数
- 你需要同步多条视频/音频轨道的 timecode → 用 CaptureDataUtils 中的 timecode 工具
- 你需要排除捕获数据中的坏帧 → 用 FFrameRange 和 CaptureExcludedFrames 管理帧范围

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetCaptureMetadata` | 为任意 UObject 设置捕获元数据 | `UCaptureMetadata` |
| `GetCaptureMetadata` | 获取对象上的捕获元数据 | `UCaptureMetadata` |
| `ClearCaptureMetadata` | 清除对象上的捕获元数据 | `UCaptureMetadata` |
| `ShowCaptureMetadataObjects` | 弹出窗口显示多个对象的元数据 | `UCaptureMetadata` |
| `SetTimecodeInfo` (Audio) | 为 SoundWave 设置 timecode 和帧率 | `USoundWaveTimecodeUtils` |
| `GetTimecode` (Audio) | 获取 SoundWave 的 timecode | `USoundWaveTimecodeUtils` |
| `GetFrameRate` (Audio) | 获取 SoundWave 的帧率 | `USoundWaveTimecodeUtils` |
| `SetTimecodeInfo` (Image) | 为 ImgMediaSource 设置 timecode | `UImageSequenceTimecodeUtils` |
| `GetTimecode` (Image) | 获取图像序列的 timecode | `UImageSequenceTimecodeUtils` |
| `GetTimecodeString` | 获取图像序列 timecode 字符串 | `UImageSequenceTimecodeUtils` |
| `SetTimecodeInfoString` | 用字符串设置图像序列 timecode | `UImageSequenceTimecodeUtils` |

### 使用示例（蓝图描述）

**设置音频 timecode：**
1. 创建 `USoundWaveTimecodeUtils` 节点
2. 连接 `SetTimecodeInfo`，输入 FTimecode（如 01:00:00:00）、FFrameRate（如 30/1）和目标 SoundWave 资产引用
3. 输出即为已标注 timecode 的音频资产

**读取/写入捕获元数据：**
1. 拖入任意 UObject 引用
2. 调用 `SetCaptureMetadata` 传入 CameraId 等信息
3. 后续可通过 `GetCaptureMetadata` 检索

## C++ 用法

### 头文件引入

```cpp
#include "CaptureData.h"              // UCaptureData, UFootageCaptureData, UMeshCaptureData
#include "CameraCalibration.h"        // UCameraCalibration, FCameraCalibration
#include "FrameRange.h"               // FFrameRange, PackIntoFrameRanges
#include "ImageSequenceUtils.h"       // FImageSequenceUtils
#include "CaptureMetadata.h"          // UCaptureMetadata
#include "ParseTakeUtils.h"           // ParseTimecode, ConvertFrameRate
#include "ImageSequenceTimecodeUtils.h" // UImageSequenceTimecodeUtils
#include "SoundWaveTimecodeUtils.h"   // USoundWaveTimecodeUtils
```

### 基本用法

**创建 FootageCaptureData 并访问图像序列：**

```cpp
// 来源: CaptureData.h - UFootageCaptureData
UFootageCaptureData* FootageData = NewObject<UFootageCaptureData>();

// 添加图像序列
FootageData->ImageSequences.Add(MyImgMediaSource);

// 添加音频轨道
FootageData->AudioTracks.Add(MySoundWave);

// 添加相机标定
FootageData->CameraCalibrations.Add(MyCalibration);

// 检查是否完整初始化
bool bReady = FootageData->IsInitialized(UCaptureData::EInitializedCheck::Full);
```

**获取帧范围信息：**

```cpp
// 来源: CaptureData.h - GetFrameRanges
TMap<TWeakObjectPtr<UObject>, TRange<FFrameNumber>> MediaFrameRanges;
TRange<FFrameNumber> ProcessingFrameRange;
TRange<FFrameNumber> MaximumFrameRange;

FFrameRate TargetRate(30, 1);
FootageData->GetFrameRanges(
    TargetRate,
    ETimecodeAlignment::Absolute,
    true,  // include audio
    MediaFrameRanges,
    ProcessingFrameRange,
    MaximumFrameRange
);
```

**打包帧号为帧范围：**

```cpp
// 来源: TestPackIntoFrameRanges.cpp + FrameRange.h
TArray<FFrameNumber> FrameNumbers = { 1, 2, 3, 5, 6, 7 };
TArray<FFrameRange> FrameRanges = PackIntoFrameRanges(FrameNumbers);
// 结果: [{1,3}, {5,7}]

// 检查帧是否在范围内
bool bContained = FFrameRange::ContainsFrame(2, FrameRanges); // true
```

### 进阶用法

**获取图像序列信息：**

```cpp
// 来源: ImageSequenceUtils.h
FString FullPath;
TArray<FString> ImageFiles;
FImageSequenceUtils::GetImageSequencePathAndFilesFromAsset(MyImgMediaSource, FullPath, ImageFiles);

FIntVector2 Dimensions;
int32 NumImages;
FImageSequenceUtils::GetImageSequenceInfoFromAsset(MyImgMediaSource, Dimensions, NumImages);
```

**坐标系转换（Unreal ↔ OpenCV）：**

```cpp
// 来源: OpenCVHelperLocal.h
FTransform MyTransform = /* ... */;

// Unreal → OpenCV
FOpenCVHelperLocal::ConvertUnrealToOpenCV(MyTransform);

// OpenCV → Unreal
FOpenCVHelperLocal::ConvertOpenCVToUnreal(MyTransform);

// 也可以转换单个向量
FVector Pos = FOpenCVHelperLocal::ConvertUnrealToOpenCV(MyVector);
```

**相机标定数据转换：**

```cpp
// 来源: CameraCalibration.h
UCameraCalibration* Calibration = NewObject<UCameraCalibration>();

// 从 TrackerNode 格式导入
TArray<FCameraCalibration> Calibrations;
TMap<FString, FString> LensAssetNamesMap;
Calibration->ConvertFromTrackerNodeCameraModels(Calibrations, LensAssetNamesMap);

// 导出为 TrackerNode 格式
TArray<FCameraCalibration> OutCalibs;
TArray<TPair<FString, FString>> OutStereoPairs;
Calibration->ConvertToTrackerNodeCameraModels(OutCalibs, OutStereoPairs);
```

**验证 FootageCaptureData 完整性：**

```cpp
// 来源: CaptureData.h - VerifyData
auto Result = FootageData->VerifyData(UCaptureData::EInitializedCheck::Full);
if (Result.HasError())
{
    UE_LOG(LogCaptureDataCore, Error, TEXT("Validation failed: %s"), *Result.GetError());
}

// 检查图像序列路径是否有效
TArray<UFootageCaptureData::FPathAssociation> InvalidPaths = FootageData->CheckImageSequencePaths();
for (const auto& Path : InvalidPaths)
{
    UE_LOG(LogCaptureDataCore, Warning, TEXT("Missing path: %s"), *Path.PathOnDisk);
}
```

## Demo 示例

以下示例展示如何创建一个最小的 FootageCaptureData 处理管线：

```cpp
// MyCaptureProcessor.h
#pragma once
#include "CoreMinimal.h"
#include "CaptureData.h"
#include "ImageSequenceUtils.h"

class FMyCaptureProcessor
{
public:
    void ProcessCaptureData(UFootageCaptureData* InData)
    {
        // 1. 验证数据完整性
        auto VerifyResult = InData->VerifyData(UCaptureData::EInitializedCheck::Full);
        if (VerifyResult.HasError())
        {
            UE_LOG(LogTemp, Error, TEXT("Capture data invalid: %s"), *VerifyResult.GetError());
            return;
        }

        // 2. 获取有效 timecode
        FTimecode ImgTimecode = InData->GetEffectiveImageTimecode(0);
        FFrameRate ImgRate = InData->GetEffectiveImageTimecodeRate(0);

        // 3. 获取图像序列信息
        for (const auto& ImgSeq : InData->ImageSequences)
        {
            FIntVector2 Dims;
            int32 NumFrames;
            FImageSequenceUtils::GetImageSequenceInfoFromAsset(ImgSeq, Dims, NumFrames);
            UE_LOG(LogTemp, Log, TEXT("Sequence: %dx%d, %d frames"), Dims.X, Dims.Y, NumFrames);
        }

        // 4. 获取处理帧范围
        TMap<TWeakObjectPtr<UObject>, TRange<FFrameNumber>> MediaRanges;
        TRange<FFrameNumber> ProcessRange, MaxRange;
        InData->GetFrameRanges(ImgRate, ETimecodeAlignment::Relative, true,
            MediaRanges, ProcessRange, MaxRange);
    }
};
```

**Build.cs 依赖：**

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "CaptureDataCore",
    "CaptureDataUtils"
});
```

## 模块依赖

### CaptureDataCore (Runtime)

| 模块 | 用途 |
|---|---|
| `Media` | 媒体框架基础 |
| `Core` / `CoreUObject` / `Engine` | UE 核心 |
| `ImgMedia` | 图像序列媒体源 (`UImgMediaSource`) |
| `CameraCalibrationCore` | 镜头文件 (`ULensFile`) |
| `MeshDescription` / `StaticMeshDescription` | 网格数据处理 |
| `CaptureDataUtils` | Timecode 解析工具 |

### CaptureDataEditor (Editor)

| 模块 | 用途 |
|---|---|
| `Core` / `CoreUObject` / `Engine` | UE 核心 |
| `CaptureDataCore` | 核心数据类型 |
| `AssetDefinition` | 编辑器资产类型定义 |
| `UnrealEd` / `PropertyEditor` / `SlateCore` / `Slate` / `InputCore` | 编辑器 UI |
| `EditorScriptingUtilities` | 编辑器脚本工具 |

### CaptureDataUtils (Runtime)

| 模块 | 用途 |
|---|---|
| `Core` / `CoreUObject` / `Engine` | UE 核心 |
| `ImgMedia` | 图像序列媒体源 |
| `UnrealEd` / `EditorScriptingUtilities` | 仅编辑器构建时使用 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 |
|---|---|---|
| 2025-10-09 | `9650ae3` | [BugHawk] 添加 nullptr 安全检查 |
| 2025-10-03 | `a7fe5bc` | [CaptureManager] 在导入资产元数据中添加 camera id |
| 2025-10-02 | `409349d` | 添加 Capture Metadata 资产工具蓝图 |

**解读：** 最近三次提交集中在 2025 年 10 月，功能方向明确——增强捕获元数据能力（添加 camera id 到元数据、新增元数据蓝图工具）以及 BugHawk 驱动的稳定性修复。插件在 MetaHuman 工作流中持续获得维护投入。

### 维护评价

- **创建时间**：2024 年 9 月，相对较新的插件
- **最近更新**：2025 年 10 月，距今约 6 个月，有实质性功能更新
- **维护状态**：活跃维护中，与 MetaHuman Capture Manager 工作流紧密关联
- **已知限制**：`Hidden: true`，不能单独使用，必须被其他 MetaHuman 插件依赖
- **推荐程度**：如果你在做 MetaHuman 面部捕获相关开发，这是底层必需的数据层；对于一般项目不需要直接使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureData)
- [测试用例 - PackIntoFrameRanges](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/VirtualProduction/CaptureData/Source/CaptureDataCore/Private/Tests/TestPackIntoFrameRanges.cpp)
- [测试用例 - FootageCaptureMetadata](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/VirtualProduction/CaptureData/Source/CaptureDataCore/Private/Tests/FootageCaptureMetadata.spec.cpp)
