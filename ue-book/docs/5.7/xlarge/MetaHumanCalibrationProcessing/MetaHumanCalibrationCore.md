# MetaHuman Animator Calibration Processing

> The official MetaHuman Calibration Processing Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（UI 图标、样式资源） |
| 模块 | `MetaHumanCalibrationCore` (Runtime), `MetaHumanCalibrationGenerator` (Runtime), `MetaHumanCalibrationLib` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-04-01 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanCalibrationProcessing) | |

## 用途

MetaHumanCalibrationProcessing 是 MetaHuman Animator 管线中的**相机标定处理工具**。它解决的核心问题是：在使用双目相机进行面部捕捉时，需要对每台相机进行精确标定（内参和外参），以确保面部追踪的精度。

该插件提供了完整的棋盘格标定工作流：

1. **帧解析**：从 `UFootageCaptureData` 中提取双相机的标定帧路径，按时间码对齐
2. **棋盘格角点检测与统计**：检测棋盘格角点并统计覆盖区域，帮助用户判断标定数据是否充分
3. **兴趣区域选择**：允许用户在图像上框选感兴趣区域，聚焦标定处理范围
4. **帧状态管理**：标记每帧为"良好/不良/中性"，排除质量差的帧
5. **图像查看与帧浏览**：提供带拖拽选择功能的图像查看器和帧时间轴

本质上，这是 MetaHuman Animator 从面部捕捉视频到可驱动 MetaHuman 角色之间的关键预处理步骤。

## 使用场景

- 你使用 MetaHuman Animator 进行面部捕捉 → 需要先用此插件标定双目相机
- 你有一组棋盘格标定图像 → 用此插件检测角点并评估覆盖质量
- 你需要排除标定序列中的坏帧 → 用帧状态管理标记并过滤
- 你需要在标定图像上选择特定区域 → 用区域选择工具框选兴趣区域

## 模块结构

该插件包含三个模块，按职责分层：

| 模块 | 类型 | 职责 |
|---|---|---|
| `MetaHumanCalibrationCore` | Runtime | 核心 UI 组件、工具类、帧解析、棋盘格统计 |
| `MetaHumanCalibrationGenerator` | Runtime | 标定数据生成逻辑 |
| `MetaHumanCalibrationLib` | Runtime | 底层标定算法库（依赖 UnrealEd） |

本文档主要覆盖 `MetaHumanCalibrationCore` 模块。

## 蓝图用法

### 核心结构体

#### FMetaHumanAreaOfInterest

定义标定图像上的兴趣区域，可在蓝图中编辑。

| 属性 | 类型 | 说明 |
|---|---|---|
| `TopLeft` | `FVector2D` | 区域左上角坐标 |
| `BottomRight` | `FVector2D` | 区域右下角坐标 |

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetSlateRect` | 将兴趣区域转换为 `FSlateRect` | `FMetaHumanAreaOfInterest` |
| `SetFromSlateRect` | 从 `FSlateRect` 设置兴趣区域 | `FMetaHumanAreaOfInterest` |
| `GetBox2D` | 将兴趣区域转换为 `FBox2D` | `FMetaHumanAreaOfInterest` |
| `SetFromBox2D` | 从 `FBox2D` 设置兴趣区域 | `FMetaHumanAreaOfInterest` |

### 使用示例（蓝图描述）

1. 创建一个 `FMetaHumanAreaOfInterest` 变量
2. 设置 `TopLeft` 和 `BottomRight` 定义标定图像上的关注区域
3. 调用 `GetBox2D()` 获取可用于点映射计算的边界框

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanCalibrationFrameResolver.h"
#include "MetaHumanChessboardPointCounter.h"
#include "MetaHumanCalibrationUtils.h"
#include "MetaHumanAreaOfInterest.h"
```

### 基本用法：帧解析

从 `UFootageCaptureData` 创建帧解析器，获取双相机的标定帧路径。

```cpp
// 从 CaptureData 创建帧解析器
// 来源: MetaHumanCalibrationFrameResolver.h
const UFootageCaptureData* CaptureData = /* ... */;

TOptional<FMetaHumanCalibrationFrameResolver> Resolver = 
    FMetaHumanCalibrationFrameResolver::CreateFromCaptureData(CaptureData);

if (Resolver.IsSet() && Resolver->HasFrames())
{
    // 获取所有标定帧路径（每帧包含第一相机和第二相机的路径）
    TArray<FMetaHumanCalibrationFramePaths> AllFrames = Resolver->GetCalibrationFramePaths();
    
    for (const FMetaHumanCalibrationFramePaths& Frame : AllFrames)
    {
        UE_LOG(LogTemp, Log, TEXT("Camera 1: %s"), *Frame.FirstCamera);
        UE_LOG(LogTemp, Log, TEXT("Camera 2: %s"), *Frame.SecondCamera);
    }
    
    // 按帧索引获取特定帧
    FMetaHumanCalibrationFramePaths SingleFrame;
    if (Resolver->GetCalibrationFramePathsForFrameIndex(0, SingleFrame))
    {
        // 处理第一帧
    }
    
    // 按相机索引获取所有帧路径
    TArray<FString> Camera0Frames;
    Resolver->GetFramePathsForCameraIndex(0, Camera0Frames);
}
```

### 基本用法：图像工具函数

```cpp
// 来源: MetaHumanCalibrationUtils.h
using namespace UE::MetaHuman;

// 获取灰度图像（用于棋盘格检测）
TOptional<FImage> GrayImage = Image::GetGrayscaleImage(TEXT("/path/to/calibration_image.png"));
if (GrayImage.IsSet())
{
    // 灰度图像可用于角点检测
}

// 过滤帧路径（例如只保留有效的标定帧）
const UFootageCaptureData* CaptureData = /* ... */;
auto [ValidPaths, InvalidPaths] = Image::FilterFramePaths(CaptureData, 
    [](int32 FrameIndex) -> bool
    {
        // 自定义过滤逻辑：例如跳过前10帧
        return FrameIndex >= 10;
    });
```

### 进阶用法：棋盘格角点统计

```cpp
// 来源: MetaHumanChessboardPointCounter.h
// 创建棋盘格点计数器，用于评估标定覆盖质量
FVector2D CoverageMapSize(1920.0, 1080.0);
TPair<FString, FString> CameraNames(TEXT("CameraLeft"), TEXT("CameraRight"));
TPair<FIntVector2, FIntVector2> ImageSizes(FIntVector2(1920, 1080), FIntVector2(1920, 1080));

FMetaHumanChessboardPointCounter PointCounter(CoverageMapSize, CameraNames, ImageSizes);

// 更新检测到的角点数据
FMetaHumanChessboardPointCounter::FFramePointsMap FramePointsMap;
FramePointsMap.Add(0, DetectedPoints);  // 帧0的角点
FramePointsMap.Add(1, DetectedPoints2); // 帧1的角点
PointCounter.Update(TEXT("CameraLeft"), FramePointsMap);

// 获取已占用的区块（覆盖阈值 > 0）
TArray<int32> OccupiedBlocks = PointCounter.GetOccupiedBlockIndices(TEXT("CameraLeft"), 1);

// 获取每个区块的占用计数
TMap<int32, int32> BlockCounts = PointCounter.GetOccupiedBlockIndicesAndCount(TEXT("CameraLeft"));

// 获取特定区块的角点数量
TOptional<int32> Count = PointCounter.GetCountForBlock(TEXT("CameraLeft"), 5);

// 获取区块尺寸
FVector2D BlockSize = PointCounter.GetBlockSize();

// 获取特定区块的边界
FBox2D Block = PointCounter.GetBlock(TEXT("CameraLeft"), 5);
```

### 进阶用法：坐标空间映射

```cpp
// 来源: MetaHumanCalibrationUtils.h - UE::MetaHuman::Points 命名空间
// 在纹理空间和控件空间之间映射点坐标

FVector2D TexturePoint(960.0, 540.0);
FVector2D TextureSize(1920.0, 1080.0);
FBox2D UV(FVector2D(0.0, 0.0), FVector2D(1.0, 1.0));
FVector2D WidgetSize(800.0, 600.0);

// 纹理坐标 → 控件坐标
FVector2D WidgetPoint = Points::MapTexturePointToLocalWidgetSpace(
    TexturePoint, TextureSize, UV, WidgetSize);

// 控件坐标 → 纹理坐标
FVector2D BackToTexture = Points::MapWidgetPointToTextureSpace(
    WidgetPoint, WidgetSize, UV, TextureSize);

// 缩放角点数组
TArray<FVector2D> PointsArray = /* detected chessboard corners */;
Points::ScalePointsInPlace(PointsArray, 0.5f);  // 缩小一半

// 检查点是否在控件边界外
bool bOutside = Points::IsOutsideWidgetBounds(WidgetPoint, WidgetSize);
```

## UI 组件

### SMetaHumanCalibrationSingleImageViewer

带区域选择功能的图像查看器，用于在标定图像上框选兴趣区域。

```cpp
// 创建图像查看器
TSharedRef<SMetaHumanCalibrationSingleImageViewer> Viewer = 
    SNew(SMetaHumanCalibrationSingleImageViewer)
    .Images(ImagePaths)
    .OnAddOverlays_Lambda([](FBox2d UV, const FGeometry& Geo, FSlateWindowElementList& Elems, int32& Layer)
    {
        // 自定义叠加绘制
    })
    .OnImageClick_Lambda([](FVector2D ClickPos, FBox2d UV, FVector2D WidgetSize)
    {
        // 处理图像点击
    });

// 启动区域选择模式
Viewer->StartSelecting(FMetaHumanCalibrationSingleImageViewer::FAreaSelectionEnded::CreateLambda(
    [](FSlateRect SelectedRect, FBox2d UV, FVector2D WidgetSize)
    {
        // 用户完成区域选择后的回调
    }));
```

### SMetaHumanImageViewerScrubber

帧时间轴控件，支持帧状态可视化（良好/不良/中性）。

```cpp
// 创建帧浏览控件
TSharedRef<SMetaHumanImageViewerScrubber> Scrubber = 
    SNew(SMetaHumanImageViewerScrubber)
    .NumberOfFrames(100)
    .FrameRate(30.0)
    .AllowVisualization(true)
    .OnValueChanged_Lambda([](float Value)
    {
        // 帧索引变化回调
    });

// 设置帧状态
Scrubber->SetFrameState(5, EFrameState::Type::Bad);   // 标记第5帧为不良
Scrubber->SetFrameState(10, EFrameState::Type::Ok);    // 标记第10帧为良好

// 批量设置
TMap<int32, EFrameState::Type> States;
States.Add(0, EFrameState::Type::Ok);
States.Add(1, EFrameState::Type::Bad);
States.Add(2, EFrameState::Type::Neutral);
Scrubber->SetFrameStates(States);
```

### FMetaHumanCalibrationNotificationManager

异步操作的通知管理器，支持线程安全。

```cpp
// 在工作线程中使用
TSharedRef<FMetaHumanCalibrationNotificationManager> NotifManager = 
    MakeShared<FMetaHumanCalibrationNotificationManager>();

// 开始处理时显示通知（线程安全，自动切换到游戏线程）
NotifManager->NotificationOnBegin(LOCTEXT("Calibrating", "正在标定相机..."));

// 处理完成
NotifManager->NotificationOnEnd(true, LOCTEXT("Success", "标定完成，检测到 240 个角点"));

// 处理失败
NotifManager->NotificationOnEnd(false, LOCTEXT("Failed", "未检测到足够的棋盘格角点"));
```

## Demo 示例

### 最小标定帧处理示例

```cpp
// MyCalibrationProcessor.h
#pragma once

#include "CoreMinimal.h"
#include "MetaHumanCalibrationFrameResolver.h"
#include "MetaHumanChessboardPointCounter.h"
#include "MetaHumanCalibrationUtils.h"

class FMyCalibrationProcessor
{
public:
    void ProcessCalibrationData(const UFootageCaptureData* InCaptureData);

private:
    TOptional<FMetaHumanCalibrationFrameResolver> FrameResolver;
    TSharedPtr<FMetaHumanChessboardPointCounter> PointCounter;
};
```

```cpp
// MyCalibrationProcessor.cpp
#include "MyCalibrationProcessor.h"

void FMyCalibrationProcessor::ProcessCalibrationData(const UFootageCaptureData* InCaptureData)
{
    using namespace UE::MetaHuman;

    // 1. 创建帧解析器
    FrameResolver = FMetaHumanCalibrationFrameResolver::CreateFromCaptureData(InCaptureData);
    if (!FrameResolver.IsSet() || !FrameResolver->HasFrames())
    {
        UE_LOG(LogTemp, Warning, TEXT("No calibration frames found"));
        return;
    }

    // 2. 获取所有帧
    TArray<FMetaHumanCalibrationFramePaths> AllFrames = FrameResolver->GetCalibrationFramePaths();
    UE_LOG(LogTemp, Log, TEXT("Found %d calibration frames"), AllFrames.Num());

    // 3. 过滤有效帧（例如只保留偶数帧）
    auto [ValidPaths, InvalidPaths] = Image::FilterFramePaths(InCaptureData,
        [](int32 FrameIndex) -> bool { return FrameIndex % 2 == 0; });

    // 4. 读取灰度图像用于角点检测
    for (const FString& Path : ValidPaths)
    {
        TOptional<FImage> GrayImage = Image::GetGrayscaleImage(Path);
        if (GrayImage.IsSet())
        {
            // 在此处进行棋盘格角点检测...
        }
    }

    // 5. 初始化棋盘格点计数器
    FVector2D CoverageSize(1920.0, 1080.0);
    TPair<FString, FString> Cameras(TEXT("Cam0"), TEXT("Cam1"));
    TPair<FIntVector2, FIntVector2> Sizes(FIntVector2(1920, 1080), FIntVector2(1920, 1080));
    PointCounter = MakeShared<FMetaHumanChessboardPointCounter>(CoverageSize, Cameras, Sizes);

    // 6. 更新检测到的角点并评估覆盖质量
    // PointCounter->Update(TEXT("Cam0"), DetectedCorners);
    // auto Occupied = PointCounter->GetOccupiedBlockIndices(TEXT("Cam0"), 1);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `CaptureData` | 提供 `UFootageCaptureData`、`UImgMediaSource` 等捕捉数据类型 |
| `ImageCore` | 提供 `FImage` 图像处理基础类型 |
| `ImgMedia` | 图像序列媒体源支持 |
| `PropertyEditor` | 细节面板编辑器（用于 `SMetaHumanCalibrationObjectWidget`） |

## 维护状态

### 近期更新

```
- fc3dc7573070 Updating scrubbing icons for Calibration Tool
- 973c68a98d7f Updating Calibration icons
- 5c0153a19c3d Resolving bughawk issues
```

### 维护评价

- **创建时间**：2025-04-01，非常新的插件
- **更新频率**：近期有活跃的 UI 图标更新和 bug 修复
- **维护状态**：🟢 活跃维护中 — 作为 MetaHuman Animator 官方工具链的一部分，由 Epic Games 持续维护
- **实验性**：否（`IsBetaVersion=false`，`IsExperimentalVersion=false`）
- **推荐使用**：✅ 如果你在使用 MetaHuman Animator 进行面部捕捉，这是必需的标定工具。作为官方工具链组件，质量和稳定性有保障。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanCalibrationProcessing)
- [MetaHuman 官方文档](https://docs.unrealengine.com/5.7/en-US/metahuman-in-unreal-engine/)