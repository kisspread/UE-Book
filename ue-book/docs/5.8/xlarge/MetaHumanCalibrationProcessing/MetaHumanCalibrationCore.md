# MetaHuman Animator Calibration Processing

> The official MetaHuman Calibration Processing Unreal Engine toolkit（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 标定处理 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容资产） |
| 模块 | `MetaHumanCalibrationCore` (Runtime), `MetaHumanCalibrationGenerator` (Runtime), `MetaHumanCalibrationLib` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-04-01 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanCalibrationProcessing) | |

## 用途

该插件为 MetaHuman Animator 的**相机标定（Calibration）**流程提供完整的处理工具链。在 MetaHuman 面部动捕工作流中，需要使用棋盘格标定板对多台相机进行标定，以计算相机内参和外参，从而实现精确的立体视觉重建。

具体来说，该插件解决以下问题：

1. **标定选择与排序**：当拍摄了多组标定数据时，需要从中选择最优的标定结果。插件提供了抽象的 `UMetaHumanCalibrationSelector` 框架，支持基于 Timecode 等策略自动选取最佳标定。
2. **棋盘格检测与覆盖分析**：`FMetaHumanChessboardPointCounter` 负责追踪棋盘格角点在画面不同区域的分布密度（coverage map），帮助用户判断标定板是否覆盖了足够的画面区域。
3. **多相机帧同步**：`FMetaHumanCalibrationFrameResolver` 解决多相机拍摄时的帧对齐问题，基于 Timecode 将不同相机的帧进行一一匹配。
4. **标定过程的可视化与交互**：提供完整的 Slate UI 组件（图像查看器、帧拖拽条、区域选择等），让用户在编辑器中直观地审查和操作标定数据。

该插件是 MetaHuman Animator 全面部动捕方案的核心基础设施之一，不直接面向普通游戏开发，而是服务于影视级别的 MetaHuman 动画制作流水线。

## 使用场景

- 你在使用 **MetaHuman Animator** 进行全面部动捕，需要对相机进行标定校准 → 使用此插件
- 你有**多台相机**拍摄了棋盘格标定板的素材，需要自动匹配帧、分析角点覆盖 → 使用此插件
- 你需要**自定义标定选择策略**（例如基于 Timecode 选择最近的标定） → 继承 `UMetaHumanCalibrationSelector` 并在蓝图中实现
- 你需要在编辑器中**可视化标定帧**、审查棋盘格检测质量 → 使用插件提供的 Slate 控件
- 你需要对 `UFootageCaptureData` 和 `UCameraCalibration` 资产进行编程式操作 → 使用插件的工具类

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SelectCalibration` | 从多组标定中选择一个最优标定 | `UMetaHumanCalibrationSelector` |
| `OrderCalibrations` | 将标定数组按优先级排序 | `UMetaHumanCalibrationSelector` |
| `GetSettingsClass` | 获取该选择器对应的设置类 | `UMetaHumanCalibrationSelector` |
| `SetSettings` | 设置选择器的配置对象 | `UMetaHumanCalibrationSelector` |

### 自定义标定选择器（蓝图）

`UMetaHumanCalibrationSelector` 是一个 `Blueprintable` 抽象类，允许你在蓝图中创建自定义标定选择策略：

1. 在蓝图编辑器中创建 **Blueprint Class**，父类选择 `UMetaHumanCalibrationSelector`
2. 实现 `OrderCalibrations` 节点：接收 `UFootageCaptureData` 和一组 `UCameraCalibration*`，返回按优先级排序的数组
3. 实现 `GetSettingsClass` 节点：返回你的自定义设置类（继承自 `UMetaHumanCalibrationSelectorSettings`）
4. `SelectCalibration` 默认从 `OrderCalibrations` 返回的数组中取第一个元素，通常无需重写

插件内置了 `UMetaHumanTimecodeBasedSelector`，它根据 Timecode 将标定帧与素材帧进行匹配，选取时间上最接近的标定结果。

### FMetaHumanAreaOfInterest（蓝图结构体）

该结构体在蓝图中可用（`BlueprintType`），用于表示图像中的感兴趣区域（ROI）：

| 属性 | 类型 | 说明 |
|---|---|---|
| `TopLeft` | `FVector2D` | 区域左上角坐标 |
| `BottomRight` | `FVector2D` | 区域右下角坐标 |

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanCalibrationSelector.h"
#include "MetaHumanTimecodeBasedSelector.h"
#include "MetaHumanCalibrationUtils.h"
#include "MetaHumanCalibrationFrameResolver.h"
#include "MetaHumanChessboardPointCounter.h"
#include "MetaHumanAreaOfInterest.h"
```

### 基本用法 — 多相机帧解析

使用 `FMetaHumanCalibrationFrameResolver` 从拍摄数据中解析多相机的标定帧对齐关系。

```cpp
// 来源: Public/Utils/MetaHumanCalibrationFrameResolver.h

#include "MetaHumanCalibrationFrameResolver.h"
#include "FootageCaptureData.h"

// 从 FootageCaptureData 创建帧解析器
void ResolveCalibrationFrames(UFootageCaptureData* InCaptureData)
{
    TOptional<FMetaHumanCalibrationFrameResolver> Resolver =
        FMetaHumanCalibrationFrameResolver::CreateFromCaptureData(InCaptureData);

    if (!Resolver.IsSet() || !Resolver->HasFrames())
    {
        UE_LOG(LogTemp, Warning, TEXT("无法从拍摄数据创建帧解析器"));
        return;
    }

    // 获取所有帧的标定路径
    TArray<FMetaHumanCalibrationFramePaths> AllFrames = Resolver->GetCalibrationFramePaths();

    for (const FMetaHumanCalibrationFramePaths& Frame : AllFrames)
    {
        // 每帧包含两个相机的图像路径
        UE_LOG(LogTemp, Log, TEXT("相机1: %s, 相机2: %s"),
            *Frame.FirstCamera, *Frame.SecondCamera);
    }

    // 也可以按帧索引获取
    FMetaHumanCalibrationFramePaths SingleFrame;
    if (Resolver->GetCalibrationFramePathsForFrameIndex(0, SingleFrame))
    {
        UE_LOG(LogTemp, Log, TEXT("第0帧 - 相机1: %s, 相机2: %s"),
            *SingleFrame.FirstCamera, *SingleFrame.SecondCamera);
    }
}
```

### 基本用法 — 棋盘格覆盖分析

使用 `FMetaHumanChessboardPointCounter` 追踪棋盘格角点在画面中的分布情况。

```cpp
// 来源: Public/Utils/MetaHumanChessboardPointCounter.h

#include "MetaHumanChessboardPointCounter.h"

void AnalyzeChessboardCoverage()
{
    // 定义两个相机的名称和图像尺寸
    TPair<FString, FString> CameraNames("CameraLeft", "CameraRight");
    TPair<FIntVector2, FIntVector2> ImageSizes(
        FIntVector2(1920, 1080),
        FIntVector2(1920, 1080)
    );

    // 创建计数器，指定覆盖地图大小
    FMetaHumanChessboardPointCounter Counter(
        FVector2D(200, 150),  // CoverageMapSize
        CameraNames,
        ImageSizes
    );

    // 更新某帧的角点数据
    TArray<FVector2D> DetectedPoints;
    DetectedPoints.Add(FVector2D(500, 300));
    DetectedPoints.Add(FVector2D(520, 310));
    // ... 更多检测到的角点

    Counter.Update("CameraLeft", DetectedPoints);

    // 查询被占用的区块
    TArray<int32> OccupiedBlocks = Counter.GetOccupiedBlockIndices("CameraLeft");
    UE_LOG(LogTemp, Log, TEXT("CameraLeft 被占用区块数: %d"), OccupiedBlocks.Count);

    // 获取每个区块的点计数
    TMap<int32, int32> BlockCounts = Counter.GetOccupiedBlockIndicesAndCount("CameraLeft");
    for (const auto& [BlockIndex, Count] : BlockCounts)
    {
        UE_LOG(LogTemp, Log, TEXT("区块 %d: %d 个角点"), BlockIndex, Count);
    }

    // 可以重置后重新计算
    Counter.Invalidate();
}
```

### 基本用法 — 图像与点坐标工具

使用 `UE::MetaHuman::Image` 和 `UE::MetaHuman::Points` 命名空间中的工具函数。

```cpp
// 来源: Public/Utils/MetaHumanCalibrationUtils.h

#include "MetaHumanCalibrationUtils.h"

void ImageAndPointUtilities()
{
    using namespace UE::MetaHuman;

    // 1. 获取 ImgMediaSource 中的所有图像路径
    TArray<FString> Paths = Image::GetImagePaths(MyImgMediaSource);

    // 2. 加载灰度图像
    TOptional<FImage> GrayImage = Image::GetGrayscaleImage(Paths[0]);
    if (GrayImage.IsSet())
    {
        UE_LOG(LogTemp, Log, TEXT("灰度图尺寸: %dx%d"),
            GrayImage->GetWidth(), GrayImage->GetHeight());
    }

    // 3. 从 FootageCaptureData 过滤帧
    // 使用谓词函数过滤（例如只保留偶数帧）
    auto Filtered = Image::FilterFramePaths(
        MyCaptureData,
        [](int32 FrameIndex) -> bool
        {
            return FrameIndex % 2 == 0;
        }
    );
    // Filtered.Key() = 通过过滤的路径, Filtered.Value() = 被过滤掉的路径

    // 4. 纹理坐标与 Widget 坐标之间的映射
    FVector2D TexturePoint(960, 540);
    FVector2D TextureSize(1920, 1080);
    FBox2D UV(FVector2D(0, 0), FVector2D(1, 1));
    FVector2D WidgetSize(800, 600);

    // 纹理坐标 → Widget 坐标
    FVector2D WidgetPoint = Points::MapTexturePointToLocalWidgetSpace(
        TexturePoint, TextureSize, UV, WidgetSize
    );

    // Widget 坐标 → 纹理坐标
    FVector2D BackToTexture = Points::MapWidgetPointToTextureSpace(
        WidgetPoint, WidgetSize, UV, TextureSize
    );

    // 5. 检查点是否在 Widget 范围外
    bool bOutside = Points::IsOutsideWidgetBounds(WidgetPoint, WidgetSize);
}
```

### 进阶用法 — 创建自定义标定选择器（C++）

```cpp
// 来源: Public/Selectors/MetaHumanCalibrationSelector.h, MetaHumanTimecodeBasedSelector.h

#include "MetaHumanCalibrationSelector.h"

// 自定义选择器：选择检测到最多棋盘格角点的标定
UCLASS(BlueprintType, Blueprintable)
class UMetaHumanBestQualitySelector : public UMetaHumanCalibrationSelector
{
    GENERATED_BODY()

public:
    virtual TArray<UCameraCalibration*> OrderCalibrations_Implementation(
        UFootageCaptureData* InCaptureData,
        const TArray<UCameraCalibration*>& InCameraCalibrations) const override
    {
        // 复制数组后根据质量排序
        TArray<UCameraCalibration*> Sorted = InCameraCalibrations;
        Sorted.Sort([](const UCameraCalibration& A, const UCameraCalibration& B)
        {
            // 自定义排序逻辑
            return A.GetQualityScore() > B.GetQualityScore();
        });
        return Sorted;
    }

    virtual TSubclassOf<UMetaHumanCalibrationSelectorSettings> GetSettingsClass_Implementation() const override
    {
        return UMetaHumanBestQualitySelectorSettings::StaticClass();
    }
};
```

### 进阶用法 — 完整标定处理流程

```cpp
// 综合使用各工具类的完整流程

#include "MetaHumanCalibrationFrameResolver.h"
#include "MetaHumanChessboardPointCounter.h"
#include "MetaHumanCalibrationUtils.h"
#include "MetaHumanCalibrationSelector.h"

void FullCalibrationWorkflow(UFootageCaptureData* InCaptureData)
{
    using namespace UE::MetaHuman;

    // Step 1: 解析多相机帧对齐
    auto Resolver = FMetaHumanCalibrationFrameResolver::CreateFromCaptureData(InCaptureData);
    if (!Resolver.IsSet() || !Resolver->HasFrames())
    {
        return;
    }

    // Step 2: 获取所有帧路径
    TArray<FMetaHumanCalibrationFramePaths> AllFrames = Resolver->GetCalibrationFramePaths();

    // Step 3: 创建棋盘格覆盖分析器
    FMetaHumanChessboardPointCounter Counter(
        FVector2D(200, 150),
        TPair<FString, FString>("Left", "Right"),
        TPair<FIntVector2, FIntVector2>(FIntVector2(1920,1080), FIntVector2(1920,1080))
    );

    // Step 4: 使用图像工具加载和处理每一帧
    for (int32 i = 0; i < AllFrames.Num(); ++i)
    {
        TOptional<FImage> LeftImage = Image::GetGrayscaleImage(AllFrames[i].FirstCamera);
        TOptional<FImage> RightImage = Image::GetGrayscaleImage(AllFrames[i].SecondCamera);

        if (LeftImage.IsSet() && RightImage.IsSet())
        {
            // 执行棋盘格检测（需要 OpenCV，此处为示意）
            TArray<FVector2D> LeftPoints, RightPoints;
            // DetectChessboard(*LeftImage, LeftPoints);
            // DetectChessboard(*RightImage, RightPoints);

            // 更新覆盖计数器
            FMetaHumanChessboardPointCounter::FFramePerCameraPoints FramePoints;
            FramePoints.Add("Left", LeftPoints);
            FramePoints.Add("Right", RightPoints);
            Counter.Update(FramePoints);
        }
    }

    // Step 5: 评估标定质量
    auto LeftOccupied = Counter.GetOccupiedBlockIndicesAndCount("Left");
    auto RightOccupied = Counter.GetOccupiedBlockIndicesAndCount("Right");
    UE_LOG(LogTemp, Log, TEXT("Left覆盖区块: %d, Right覆盖区块: %d"),
        LeftOccupied.Num(), RightOccupied.Num());
}
```

## Demo 示例

### 自定义标定选择器

**MetaHumanCustomSelector.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Selectors/MetaHumanCalibrationSelector.h"
#include "MetaHumanCustomSelector.generated.h"

UCLASS(BlueprintType, Blueprintable)
class UMyCalibrationSelectorSettings : public UMetaHumanCalibrationSelectorSettings
{
    GENERATED_BODY()

public:
    // 最小覆盖阈值
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Settings")
    float MinCoverageThreshold = 0.7f;
};

UCLASS(BlueprintType, Blueprintable)
class MYPROJECT_API UMyCalibrationSelector : public UMetaHumanCalibrationSelector
{
    GENERATED_BODY()

public:
    virtual TArray<UCameraCalibration*> OrderCalibrations_Implementation(
        UFootageCaptureData* InCaptureData,
        const TArray<UCameraCalibration*>& InCameraCalibrations) const override;

    virtual TSubclassOf<UMetaHumanCalibrationSelectorSettings> GetSettingsClass_Implementation() const override;
};
```

**MetaHumanCustomSelector.cpp**

```cpp
#include "MetaHumanCustomSelector.h"

TArray<UCameraCalibration*> UMyCalibrationSelector::OrderCalibrations_Implementation(
    UFootageCaptureData* InCaptureData,
    const TArray<UCameraCalibration*>& InCameraCalibrations) const
{
    // 读取自定义设置
    const UMyCalibrationSelectorSettings* Settings = GetSettings<UMyCalibrationSelectorSettings>();

    TArray<UCameraCalibration*> Result = InCameraCalibrations;

    // 根据自定义逻辑排序
    if (Settings)
    {
        // 过滤掉覆盖度低于阈值的标定
        Result = Result.FilterByPredicate([Settings](const UCameraCalibration* Cal)
        {
            // 这里应根据实际的覆盖度计算逻辑来判断
            return true; // 示意
        });
    }

    return Result;
}

TSubclassOf<UMetaHumanCalibrationSelectorSettings> UMyCalibrationSelector::GetSettingsClass_Implementation() const
{
    return UMyCalibrationSelectorSettings::StaticClass();
}
```

### 标定图像查看器（Slate）

**SMetaHumanCalibrationViewer.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Widgets/SCompoundWidget.h"
#include "Widgets/SMetaHumanSingleImageViewer.h"
#include "Widgets/SMetaHumanImageViewerScrubber.h"

class SMyCalibrationViewer : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SMyCalibrationViewer) {}
        SLATE_ARGUMENT(TArray<FString>, ImagePaths)
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs);

private:
    void OnFrameChanged(float NewValue);
    void OnImageClicked(FVector2D ClickPos, FBox2d UV, FVector2D WidgetSize);

    TSharedPtr<SMetaHumanCalibrationSingleImageViewer> ImageViewer;
    TSharedPtr<SMetaHumanImageViewerScrubber> Scrubber;
    TArray<FString> CachedImagePaths;
};
```

**SMetaHumanCalibrationViewer.cpp**

```cpp
#include "SMetaHumanCalibrationViewer.h"

void SMyCalibrationViewer::Construct(const FArguments& InArgs)
{
    CachedImagePaths = InArgs._ImagePaths;

    ChildSlot
    [
        SNew(SVerticalBox)
        + SVerticalBox::Slot()
        .FillHeight(1.0f)
        [
            SAssignNew(ImageViewer, SMetaHumanCalibrationSingleImageViewer)
            .Images(CachedImagePaths)
            .OnImageClick(FOnImageClick::CreateSP(this, &SMyCalibrationViewer::OnImageClicked))
        ]
        + SVerticalBox::Slot()
        .AutoHeight()
        .Padding(4.0f)
        [
            SAssignNew(Scrubber, SMetaHumanImageViewerScrubber)
            .NumberOfFrames(CachedImagePaths.Num())
            .FrameRate(30.0)
            .AllowVisualization(true)
            .OnValueChanged(FOnFloatValueChanged::CreateSP(this, &SMyCalibrationViewer::OnFrameChanged))
        ]
    ];

    // 显示第一帧
    if (CachedImagePaths.Num() > 0)
    {
        ImageViewer->ShowImage(0);
    }
}

void SMyCalibrationViewer::OnFrameChanged(float NewValue)
{
    int32 FrameIndex = FMath::Clamp(
        FMath::RoundToInt(NewValue * (CachedImagePaths.Num() - 1)),
        0,
        CachedImagePaths.Num() - 1
    );
    ImageViewer->ShowImage(FrameIndex);
}

void SMyCalibrationViewer::OnImageClicked(FVector2D ClickPos, FBox2d UV, FVector2D WidgetSize)
{
    using namespace UE::MetaHuman::Points;
    // 将点击坐标从 Widget 空间映射回纹理空间
    FVector2D TextureSize(ImageViewer->GetImageSize().X, ImageViewer->GetImageSize().Y);
    FVector2D TexturePoint = MapWidgetPointToTextureSpace(ClickPos, WidgetSize, UV, TextureSize);
    UE_LOG(LogTemp, Log, TEXT("点击纹理坐标: %s"), *TexturePoint.ToString());
}
```

## 模块依赖

该插件包含三个运行时模块。`MetaHumanCalibrationLib` 虽然标记为 Runtime 类型，但实际依赖了 `UnrealEd`，这意味着它只能在编辑器环境中使用（非纯运行时模块）。

| 模块 | 用途 |
|---|---|
| `MetaHumanCore` | MetaHuman 核心框架，提供基础数据类型 |
| `ImgMedia` | 图像序列媒体源支持（`UImgMediaSource`） |
| `Media` | 媒体框架基础 |
| `CameraCalibrationCore` | 相机标定数据类型（`UCameraCalibration`） |
| `FootageCapture` | 拍摄素材数据（`UFootageCaptureData`） |
| `OpenCV` / `OpenCVHelper` | OpenCV 计算机视觉库封装（棋盘格检测等） |
| `ImageCore` | 图像数据处理（`FImage`） |

> **注意**：`MetaHumanCalibrationLib` 依赖 `UnrealEd`，因此该插件整体**仅限编辑器使用**，不能在打包后的游戏中运行。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `7f10fbf1` | [MetaHuman] Titan v9.0.8 | 更新至 Titan v9.0.8 版本 |
| 2026-05-26 | `cfa3dac6` | [MetaHuman] Titan v9.0.7 | 更新至 Titan v9.0.7 版本 |
| 2026-05-21 | `e936df4b` | [MetaHuman] Titan v9.0.6 | 更新至 Titan v9.0.6 版本 |
| 2026-05-14 | `52cbd20d` | [MetaHuman] titan v9.0.5 | 更新至 Titan v9.0.5 版本 |
| 2026-05-13 | `df646fb2` | Use infinity as limit for initial distance, to not overflow float in calculations | 修复浮点数溢出问题，改用无穷大作为初始距离限制 |

### 维护评价

- **活跃维护中**：该插件创建于 2025 年 4 月，至今（2026 年 5 月）仍在持续更新，最近一个月内有多次 Titan 版本升级和 bug 修复
- **更新频率高**：近 2 周内有 5 次提交，表明该插件与 MetaHuman Titan 引擎保持着紧密的同步更新节奏
- **更新内容**：主要是 Titan 版本迭代升级和关键数值计算修复，属于持续集成维护
- **依赖关系**：与 MetaHuman Titan 深度耦合，版本号与 Titan 一一对应（v9.0.x），升级时需同步更新
- **推荐使用**：作为 MetaHuman Animator 标准工作流的一部分，如果你使用 MetaHuman Animator 进行全面部动捕，该插件是必需的基础设施。但注意它不是通用工具库，只在 MetaHuman 动捕场景下有用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanCalibrationProcessing)
- [MetaHuman 官方文档](https://docs.unrealengine.com/en-US/metahuman/)
- [MetaHuman Animator 文档](https://docs.unrealengine.com/en-US/metahuman-animator/)