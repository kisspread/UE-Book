# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman动画器 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、工具配置） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 约 2023 年 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方的 MetaHuman 工具包，提供从真人面部捕捉数据生成高保真 MetaHuman 动画的完整管线。**MetaHumanDepthGenerator** 模块专注于从多机位拍摄的影像序列（Footage）生成深度图数据，是面部追踪和动画求解管线的前置步骤。

该模块解决的核心问题：单目/多目视频素材缺少深度信息，无法直接用于 3D 面部拟合。MetaHumanDepthGenerator 通过算法从 2D 影像推算每帧的深度图，并支持多机位时间码对齐、深度精度/分辨率配置、噪声过滤等功能，为后续的面部轮廓追踪（FaceContourTracker）和面部拟合求解（FaceFittingSolver）提供高质量的深度输入。

## 使用场景

- 你用 iPhone 或多机位设备拍摄了真人面部表演视频，需要生成深度图 → 用 MetaHumanDepthGenerator
- 你有一批 FootageCaptureData 资产需要批量处理深度信息 → 通过 MetaHumanBatchProcessor 调用深度生成
- 你需要调整深度图的精度和分辨率以平衡质量与磁盘空间 → 通过 UMetaHumanGenerateDepthWindowOptions 配置
- 你需要过滤掉过近或过远的噪声深度数据 → 通过 MinDistance/MaxDistance 参数控制

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Process` | 从 FootageCaptureData 生成深度图（使用弹窗交互式配置） | `UMetaHumanDepthGenerator` |
| `Process` (重载) | 从 FootageCaptureData 按指定选项生成深度图 | `UMetaHumanDepthGenerator` |

### 选项参数（UMetaHumanGenerateDepthWindowOptions）

| 属性 | 类型 | 说明 |
|---|---|---|
| `AssetName` | `FString` | 生成资产的名称 |
| `PackagePath` | `FDirectoryPath` | 资产保存路径（内容目录） |
| `ImageSequenceRootPath` | `FDirectoryPath` | 影像序列根目录 |
| `bAutoSaveAssets` | `bool` | 是否自动保存生成的资产，默认 `true` |
| `bShouldExcludeDepthFilesFromImport` | `bool` | 是否从导入中排除深度文件，默认 `true` |
| `bShouldCompressDepthFiles` | `bool` | 是否压缩深度文件，默认 `true` |
| `ReferenceCameraCalibration` | `UCameraCalibration*` | 参考相机标定数据 |
| `MinDistance` | `float` | 有效深度最小距离（厘米），默认 10.0，用于过滤噪声 |
| `MaxDistance` | `float` | 有效深度最大距离（厘米），默认 25.0，用于过滤噪声 |
| `DepthPrecision` | `EMetaHumanCaptureDepthPrecisionType` | 深度数据精度（完整精度更准确但占用更多磁盘空间） |
| `DepthResolution` | `EMetaHumanCaptureDepthResolutionType` | 深度数据分辨率缩放 |

### 使用示例（蓝图描述）

1. **交互式生成**：创建 `UMetaHumanDepthGenerator` 实例 → 调用 `Process(FootageCaptureData)`（单参数版本） → 系统弹出配置窗口（`SMetaHumanGenerateDepthWindow`），用户可调整深度范围、精度、分辨率等参数 → 确认后生成深度图资产。

2. **脚本式生成**：创建 `UMetaHumanGenerateDepthWindowOptions` 实例 → 设置 `AssetName`、`PackagePath`、`MinDistance`、`MaxDistance` 等参数 → 创建 `UMetaHumanDepthGenerator` 实例 → 调用 `Process(FootageCaptureData, Options)` → 直接按指定选项生成，无需用户交互。

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanDepthGenerator.h"
#include "Widgets/MetaHumanGenerateDepthWindowOptions.h"
```

### 基本用法

```cpp
// 从 FootageCaptureData 生成深度图（带选项）
// 来源：Private/MetaHumanDepthGenerator.h

UMetaHumanDepthGenerator* DepthGenerator = NewObject<UMetaHumanDepthGenerator>();
UMetaHumanGenerateDepthWindowOptions* Options = NewObject<UMetaHumanGenerateDepthWindowOptions>();

// 配置深度生成选项
Options->AssetName = TEXT("MyDepthData");
Options->PackagePath.Path = TEXT("/Game/MetaHuman/DepthData");
Options->MinDistance = 10.0f;  // 最小有效距离 10cm
Options->MaxDistance = 25.0f;  // 最大有效距离 25cm
Options->DepthPrecision = EMetaHumanCaptureDepthPrecisionType::Eightieth;
Options->DepthResolution = EMetaHumanCaptureDepthResolutionType::Full;
Options->bShouldCompressDepthFiles = true;

// 执行深度生成
UFootageCaptureData* CaptureData = /* 获取捕捉数据 */;
bool bSuccess = DepthGenerator->Process(CaptureData, Options);
```

### 进阶用法

```cpp
// 多机位时间码对齐计算
// 来源：Private/Utils/FrameOffsetCalculator.h

#include "Utils/FrameOffsetCalculator.h"

using namespace UE::MetaHuman::DepthGenerator;

// 准备各相机的时间码信息
TArray<FCameraTimecodeInfo> CameraInfos;
for (const auto& Camera : Cameras)
{
    FCameraTimecodeInfo Info;
    Info.Timecode = Camera->GetTimecode();
    Info.FrameRate = Camera->GetFrameRate();
    CameraInfos.Add(Info);
}

// 计算各相机之间的帧偏移量
TArray<int32> FrameOffsets = CalculateFrameOffset(CameraInfos);
// FrameOffsets[i] 表示第 i 个相机相对于参考相机的帧偏移
```

```cpp
// 自动重新导入配置管理
// 来源：Private/MetaHumanDepthGeneratorAutoReimport.h

#include "MetaHumanDepthGeneratorAutoReimport.h"

using namespace UE::MetaHuman;

// 更新自动重新导入排除列表（过滤深度文件目录）
TArray<FAutoReimportDirectoryConfig> UpdatedConfigs =
    DepthGeneratorUpdateAutoReimportExclusion(
        SourceDirectory,
        TEXT("*.exr"),  // 深度图通配符
        ExistingConfigs
    );

// 检查配置是否有变化
bool bChanged = DepthGeneratorDirectoryConfigsAreDifferent(
    ExistingConfigs, UpdatedConfigs
);
```

## Demo 示例

```cpp
// MetaHumanDepthGeneratorExample.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MetaHumanDepthGeneratorExample.generated.h"

class UMetaHumanDepthGenerator;
class UFootageCaptureData;
class UMetaHumanGenerateDepthWindowOptions;

UCLASS()
class AMyDepthGeneratorExample : public AActor
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, Category = "Depth")
    TObjectPtr<UFootageCaptureData> CaptureData;

    UPROPERTY(EditAnywhere, Category = "Depth")
    FString OutputAssetName = TEXT("GeneratedDepth");

    UPROPERTY(EditAnywhere, Category = "Depth", meta = (ContentDir))
    FDirectoryPath OutputPath;

    UPROPERTY(EditAnywhere, Category = "Depth Options",
              meta = (Units="Centimeters", ClampMin = "0.0", ClampMax = "200.0"))
    float MinDepthDistance = 10.0f;

    UPROPERTY(EditAnywhere, Category = "Depth Options",
              meta = (Units="Centimeters", ClampMin = "0.0", ClampMax = "200.0"))
    float MaxDepthDistance = 25.0f;

    UFUNCTION(BlueprintCallable, CallInEditor, Category = "Depth")
    void GenerateDepth();

private:
    UPROPERTY()
    TObjectPtr<UMetaHumanDepthGenerator> DepthGenerator;
};
```

```cpp
// MetaHumanDepthGeneratorExample.cpp
#include "MetaHumanDepthGeneratorExample.h"
#include "MetaHumanDepthGenerator.h"
#include "Widgets/MetaHumanGenerateDepthWindowOptions.h"

void AMyDepthGeneratorExample::GenerateDepth()
{
    if (!CaptureData)
    {
        UE_LOG(LogTemp, Warning, TEXT("CaptureData is null"));
        return;
    }

    // 创建深度生成器
    DepthGenerator = NewObject<UMetaHumanDepthGenerator>();

    // 配置选项
    UMetaHumanGenerateDepthWindowOptions* Options =
        NewObject<UMetaHumanGenerateDepthWindowOptions>();
    Options->AssetName = OutputAssetName;
    Options->PackagePath = OutputPath;
    Options->MinDistance = MinDepthDistance;
    Options->MaxDistance = MaxDepthDistance;
    Options->bAutoSaveAssets = true;
    Options->bShouldCompressDepthFiles = true;

    // 执行深度生成
    bool bSuccess = DepthGenerator->Process(CaptureData, Options);

    UE_LOG(LogTemp, Log, TEXT("Depth generation %s"),
           bSuccess ? TEXT("succeeded") : TEXT("failed"));
}
```

## 模块依赖

以下是 MetaHumanDepthGenerator 模块的依赖关系（基于其他模块的 Build.cs 信息推断）：

| 模块 | 用途 |
|---|---|
| `MetaHumanCore` | MetaHuman 核心类型和工具函数 |
| `MetaHumanCaptureUtils` | 捕捉数据工具类（深度精度/分辨率枚举等） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 启用身体追踪时禁用关卡序列导出 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 渲染瑕疵 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 支持对已有网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存问题 |

### 维护评价

**活跃维护中**。MetaHuman Animator 是 Epic Games 的旗舰产品级插件，近期（2026 年 5 月）仍有密集的功能更新和 Bug 修复。该插件作为 MetaHuman 数字人工作流的核心组件，与 MetaHuman Creator、Quixel Bridge 等工具深度集成，预计将持续得到长期支持和维护。

**注意事项**：
- 该插件默认未启用（`Installed: false`），需在项目设置中手动启用
- 插件包含大量模块（28+），完整功能需要多个模块协同工作
- MetaHumanDepthGenerator 模块的自动重新导入功能与 MetaHumanCaptureSource 模块存在代码重复，官方注释表示计划在未来合并
- 推荐在使用 MetaHuman 完整管线时配合使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档]()（暂无链接）
- [MetaHuman 官网](https://www.unrealengine.com/en-US/metahuman)