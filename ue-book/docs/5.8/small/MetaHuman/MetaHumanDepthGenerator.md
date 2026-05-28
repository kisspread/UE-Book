# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产、工具内容） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-04-01 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方的 MetaHuman 工具集，提供完整的数字人创建与动画工作流。该插件包含 28 个模块，涵盖从面部捕捉数据处理、深度图生成、面部轮廓追踪、动画解算到 Sequencer 集成的全链路能力。

本文档重点分析其中的 **MetaHumanDepthGenerator** 模块——该模块负责从视频素材（Footage）中计算深度信息，用于 MetaHuman 面部动画管线中的面部重建阶段。它解决了从 2D 视频提取 3D 深度数据的问题，支持多摄像头时间码对齐、深度精度/分辨率配置以及自动重导入工作流。

## 使用场景

- 你有多个摄像头拍摄的面部表演素材，需要生成深度图 → 用 MetaHumanDepthGenerator
- 你需要将演员的面部表演迁移到 MetaHuman 角色上 → 用完整的 MetaHuman Animator 工作流
- 你需要从语音音频驱动面部表情 → 用 MetaHumanSpeech2Face 模块
- 你需要批量处理多个 MetaHuman 素材 → 用 MetaHumanBatchProcessor 模块

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Process` | 对视频素材数据执行深度生成处理，支持自定义选项 | `UMetaHumanDepthGenerator` |

### 深度生成选项属性

`UMetaHumanGenerateDepthWindowOptions` 提供以下可配置属性：

| 属性 | 类型 | 说明 |
|---|---|---|
| `AssetName` | `FString` | 生成资产的名称 |
| `PackagePath` | `FDirectoryPath` | 资产保存路径 |
| `ImageSequenceRootPath` | `FDirectoryPath` | 图片序列根目录 |
| `bAutoSaveAssets` | `bool` | 是否自动保存生成的资产（默认 true） |
| `bShouldExcludeDepthFilesFromImport` | `bool` | 是否从导入中排除深度文件（默认 true） |
| `bShouldCompressDepthFiles` | `bool` | 是否压缩深度文件（默认 true） |
| `ReferenceCameraCalibration` | `UCameraCalibration*` | 参考相机标定数据 |
| `MinDistance` | `float` | 最小有效深度距离（厘米，默认 10.0） |
| `MaxDistance` | `float` | 最大有效深度距离（厘米，默认 25.0） |
| `DepthPrecision` | `EMetaHumanCaptureDepthPrecisionType` | 深度精度（默认 1/8 精度） |
| `DepthResolution` | `EMetaHumanCaptureDepthResolutionType` | 深度分辨率（默认全分辨率） |

### 使用示例（蓝图描述）

1. 创建 `UMetaHumanGenerateDepthWindowOptions` 对象
2. 设置 `ImageSequenceRootPath` 指向你的多摄像头素材目录
3. 根据场景调整 `MinDistance` / `MaxDistance` 过滤噪声
4. 设置 `ReferenceCameraCalibration` 为匹配的相机标定数据
5. 调用 `UMetaHumanDepthGenerator::Process(FootageCaptureData, Options)` 执行深度生成

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanDepthGenerator.h"
#include "MetaHumanGenerateDepthWindowOptions.h"
```

### 基本用法

```cpp
// 创建深度生成器
UMetaHumanDepthGenerator* DepthGenerator = NewObject<UMetaHumanDepthGenerator>();

// 使用默认选项处理 Footage 数据
bool bSuccess = DepthGenerator->Process(FootageCaptureData);
```

> 来源: `Private/MetaHumanDepthGenerator.h`

### 进阶用法

```cpp
// 创建并配置深度生成选项
UMetaHumanGenerateDepthWindowOptions* Options = NewObject<UMetaHumanGenerateDepthWindowOptions>();
Options->AssetName = TEXT("MyDepthAsset");
Options->PackagePath.Path = TEXT("/Game/MetaHuman/Depth");
Options->ImageSequenceRootPath.Path = TEXT("D:/Capture/Session01");
Options->bAutoSaveAssets = true;
Options->bShouldCompressDepthFiles = true;
Options->MinDistance = 8.0f;   // 厘米，过滤过近的噪声
Options->MaxDistance = 30.0f;  // 厘米，过滤过远的噪声
Options->DepthPrecision = EMetaHumanCaptureDepthPrecisionType::Eightieth;
Options->DepthResolution = EMetaHumanCaptureDepthResolutionType::Full;
Options->ReferenceCameraCalibration = MyCameraCalibration;

// 执行带自定义选项的深度生成
UMetaHumanDepthGenerator* DepthGenerator = NewObject<UMetaHumanDepthGenerator>();
bool bSuccess = DepthGenerator->Process(FootageCaptureData, Options);
```

> 来源: `Private/MetaHumanDepthGenerator.h`, `Private/Widgets/MetaHumanGenerateDepthWindowOptions.h`

### 帧偏移计算

```cpp
#include "Utils/FrameOffsetCalculator.h"

// 构造各摄像头的时间码信息
TArray<UE::MetaHuman::DepthGenerator::FCameraTimecodeInfo> CameraInfos;
for (const auto& Camera : Cameras)
{
    UE::MetaHuman::DepthGenerator::FCameraTimecodeInfo Info;
    Info.Timecode = Camera->GetTimecode();
    Info.FrameRate = Camera->GetFrameRate();
    CameraInfos.Add(Info);
}

// 计算各摄像头之间的帧偏移
TArray<int32> Offsets = UE::MetaHuman::DepthGenerator::CalculateFrameOffset(CameraInfos);
```

> 来源: `Private/Utils/FrameOffsetCalculator.h`

## Demo 示例

### MetaHumanDepthGenerator 最小示例

```cpp
// MetaHumanDepthExample.h
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "MetaHumanDepthExample.generated.h"

class UFootageCaptureData;

UCLASS()
class UMetaHumanDepthExampleSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    /** 对传入的 Footage 数据执行深度生成 */
    UFUNCTION(BlueprintCallable, Category = "MetaHuman Example")
    bool GenerateDepthFromFootage(UFootageCaptureData* InCaptureData, const FString& InOutputPath);
};
```

```cpp
// MetaHumanDepthExample.cpp
#include "MetaHumanDepthExample.h"
#include "MetaHumanDepthGenerator.h"
#include "MetaHumanGenerateDepthWindowOptions.h"

bool UMetaHumanDepthExampleSubsystem::GenerateDepthFromFootage(
    UFootageCaptureData* InCaptureData, const FString& InOutputPath)
{
    if (!InCaptureData)
    {
        UE_LOG(LogTemp, Error, TEXT("Invalid capture data"));
        return false;
    }

    // 配置深度生成选项
    UMetaHumanGenerateDepthWindowOptions* Options = NewObject<UMetaHumanGenerateDepthWindowOptions>();
    Options->PackagePath.Path = InOutputPath;
    Options->bAutoSaveAssets = true;
    Options->bShouldCompressDepthFiles = true;
    Options->MinDistance = 10.0f;
    Options->MaxDistance = 25.0f;

    // 执行深度生成
    UMetaHumanDepthGenerator* Generator = NewObject<UMetaHumanDepthGenerator>();
    return Generator->Process(InCaptureData, Options);
}
```

## 模块依赖

以下为 MetaHumanDepthGenerator 模块所需的依赖（该模块无额外的 Build.cs 依赖说明，仅需标准运行时依赖）：

| 模块 | 用途 |
|---|---|
| `MetaHumanCore` | MetaHuman 核心功能与公共类型 |
| `MetaHumanCaptureUtils` | 捕捉数据处理工具 |
| `MetaHumanConfig` | 配置与标定数据管理 |
| `MetaHumanCoreTechLib` | MetaHuman 底层技术库 |
| `MetaHumanImageViewerEditor` | 图像查看器编辑器支持 |

无特殊依赖（仅标准 Core/Engine/Slate 等）。整体 MetaHuman Animator 插件额外依赖 `ControlRigDeveloper`、`SkeletalMeshUtilitiesCommon`、`MetaHumanSDKEditor` 等模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 身体追踪启用时禁用关卡序列导出 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 渲染瑕疵 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 支持对已有网格导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存问题 |

### 维护评价

- **维护状态**：活跃维护中。最近的 commit 集中在 2026-05-20 至 2026-05-22，更新频率高且均为功能性改进和 Bug 修复
- **插件规模**：28 个模块、544 个源文件的大型插件，架构成熟
- **已知限制**：`MetaHumanDepthGeneratorAutoReimport.h` 中注释明确指出自动重导入逻辑在 `MetaHumanCaptureSource` 模块中有重复代码，计划未来合并
- **推荐度**：✅ 推荐使用。作为 Epic Games 官方维护的数字人工具集，该插件是 MetaHuman 工作流的核心组件，持续得到官方更新和支持

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/en-US/metahuman-animator/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanControlsConversionTest)