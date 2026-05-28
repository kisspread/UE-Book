# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、配置资源） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-04-05（估算） |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic 官方的 MetaHuman 角色动画制作完整工具链。它解决的核心问题是：**如何将真实人类的面部表演高效、精准地转移到 MetaHuman 数字角色上**。

这个插件涵盖了一整套从拍摄到最终动画输出的流程：
- **面部捕获**：通过 iPhone TrueDepth 摄像头或专业摄像头采集面部表演数据
- **深度图生成**：从 2D 视频序列推算深度信息（`MetaHumanDepthGenerator`）
- **面部轮廓追踪**：自动检测和追踪面部特征点（`MetaHumanFaceContourTracker`）
- **面部拟合求解**：将追踪结果映射到 MetaHuman 面部网格（`MetaHumanFaceFittingSolver`）
- **动画求解**：将面部拟合结果转换为 Control Rig 可用的动画数据（`MetaHumanFaceAnimationSolver`）
- **身份管理**：管理 MetaHuman 角色身份资产（`MetaHumanIdentity`）
- **语音转面部**：从音频直接驱动面部动画（`MetaHumanSpeech2Face`）
- **性能捕获**：管理和播放捕获的表演数据（`MetaHumanPerformance`）
- **批处理**：批量处理多个捕获数据（`MetaHumanBatchProcessor`）

它不是单一功能的工具，而是一个**端到端的面部动画制作管线**。

## 使用场景

- 你用 iPhone LiDAR 捕获了演员的面部表演 → 用 MetaHuman Animator 导入并转换为动画
- 你有一段普通视频素材需要驱动数字人 → 用面部追踪 + 动画求解管线
- 你有音频素材需要生成口型动画 → 用 Speech2Face 模块
- 你需要批量处理大量捕获素材 → 用 MetaHumanBatchProcessor
- 你需要创建和管理 MetaHuman 角色身份 → 用 MetaHumanIdentity 资产
- 你需要从现有面部动画数据重新拟合到新角色 → 用 Performance + FittingSolver

## 蓝图用法

### 核心节点（MetaHumanDepthGenerator 模块）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Process` | 对 FootageCaptureData 生成深度图数据 | `UMetaHumanDepthGenerator` |

### 深度生成选项（可蓝图配置）

`UMetaHumanGenerateDepthWindowOptions` 提供了以下可配置属性：

| 属性 | 类型 | 说明 |
|---|---|---|
| `AssetName` | FString | 生成资产的名称 |
| `PackagePath` | FDirectoryPath | 资产保存路径 |
| `ImageSequenceRootPath` | FDirectoryPath | 图像序列根路径 |
| `bAutoSaveAssets` | bool | 是否自动保存生成的资产 |
| `bShouldExcludeDepthFilesFromImport` | bool | 是否从导入中排除深度文件 |
| `bShouldCompressDepthFiles` | bool | 是否压缩深度文件 |
| `ReferenceCameraCalibration` | UCameraCalibration* | 参考相机标定数据 |
| `MinDistance` | float | 有效深度的最小距离（cm），默认 10 |
| `MaxDistance` | float | 有效深度的最大距离（cm），默认 25 |
| `DepthPrecision` | EMetaHumanCaptureDepthPrecisionType | 深度精度（Full/Eighth 等） |
| `DepthResolution` | EMetaHumanCaptureDepthResolutionType | 深度分辨率（Full/降采样） |

### 使用示例（蓝图描述）

1. 创建一个 `UMetaHumanDepthGenerator` 实例
2. 创建 `UMetaHumanGenerateDepthWindowOptions` 实例，配置深度参数（最小/最大距离、精度、分辨率）
3. 设置 `ReferenceCameraCalibration` 为你拍摄时使用的相机标定数据
4. 调用 `Process(CaptureData, Options)` 生成深度数据
5. 生成的深度数据会自动关联到 FootageCaptureData 资产上

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanDepthGenerator.h"
#include "MetaHumanGenerateDepthWindowOptions.h"
```

### 基本用法

从 `UMetaHumanDepthGenerator::Process` 接口可直接在代码中驱动深度生成：

```cpp
// 来源: Private/MetaHumanDepthGenerator.h
// 获取或创建深度生成器实例
UMetaHumanDepthGenerator* DepthGenerator = NewObject<UMetaHumanDepthGenerator>();

// 方式一：使用默认选项生成深度
UFootageCaptureData* CaptureData = /* 你的捕获数据 */;
bool bSuccess = DepthGenerator->Process(CaptureData);

// 方式二：使用自定义选项生成深度
UMetaHumanGenerateDepthWindowOptions* Options = NewObject<UMetaHumanGenerateDepthWindowOptions>();
Options->MinDistance = 5.0f;   // 最小有效深度距离 5cm
Options->MaxDistance = 30.0f;  // 最大有效深度距离 30cm
Options->DepthPrecision = EMetaHumanCaptureDepthPrecisionType::Full;  // 全精度
Options->DepthResolution = EMetaHumanCaptureDepthResolutionType::Full; // 全分辨率
Options->bShouldCompressDepthFiles = true;
Options->bAutoSaveAssets = true;

bool bSuccess = DepthGenerator->Process(CaptureData, Options);
```

### 进阶用法

深度生成器还支持自动重新导入配置和帧偏移计算：

```cpp
// 来源: Private/MetaHumanDepthGeneratorAutoReimport.h
// 更新自动重新导入的排除目录配置
TArray<FAutoReimportDirectoryConfig> UpdatedConfigs = 
    UE::MetaHuman::DepthGeneratorUpdateAutoReimportExclusion(
        SourceDirectory,          // 源目录路径
        TEXT("*.exr"),            // 通配符模式
        ExistingConfigs           // 现有配置
    );

// 来源: Private/Utils/FrameOffsetCalculator.h
// 计算多相机之间的帧偏移
using namespace UE::MetaHuman::DepthGenerator;

TArray<FCameraTimecodeInfo> CameraInfos;
FCameraTimecodeInfo Info1;
Info1.Timecode = FTimecode(0, 0, 0, 0, false);
Info1.FrameRate = FFrameRate(30, 1);
CameraInfos.Add(Info1);

// 添加其他相机的时间码信息...

TArray<int32> FrameOffsets = CalculateFrameOffset(CameraInfos);
// FrameOffsets[i] 表示第 i 个相机相对于参考相机的帧偏移量
```

## Demo 示例

### 完整的深度生成器调用示例

```cpp
// MetaHumanDepthGeneratorExample.h
#pragma once

#include "CoreMinimal.h"
#include "MetaHumanDepthGenerator.h"
#include "MetaHumanGenerateDepthWindowOptions.h"
#include "FootageCaptureData.h"

class FMetaHumanDepthGenerationExample
{
public:
    /** 使用自定义参数从 FootageCaptureData 生成深度数据 */
    static bool GenerateDepthFromCapture(
        UFootageCaptureData* InCaptureData,
        float InMinDistance = 10.0f,
        float InMaxDistance = 25.0f,
        bool bCompressOutput = true
    );
};
```

```cpp
// MetaHumanDepthGeneratorExample.cpp
#include "MetaHumanDepthGeneratorExample.h"

bool FMetaHumanDepthGenerationExample::GenerateDepthFromCapture(
    UFootageCaptureData* InCaptureData,
    float InMinDistance,
    float InMaxDistance,
    bool bCompressOutput)
{
    if (!InCaptureData)
    {
        UE_LOG(LogTemp, Error, TEXT("CaptureData is null"));
        return false;
    }

    // 创建深度生成器实例
    UMetaHumanDepthGenerator* DepthGenerator = NewObject<UMetaHumanDepthGenerator>();

    // 配置生成选项
    UMetaHumanGenerateDepthWindowOptions* Options = NewObject<UMetaHumanGenerateDepthWindowOptions>();
    Options->MinDistance = InMinDistance;
    Options->MaxDistance = InMaxDistance;
    Options->bShouldCompressDepthFiles = bCompressOutput;
    Options->DepthPrecision = EMetaHumanCaptureDepthPrecisionType::Eightieth;
    Options->DepthResolution = EMetaHumanCaptureDepthResolutionType::Full;
    Options->bAutoSaveAssets = true;

    // 执行深度生成
    return DepthGenerator->Process(InCaptureData, Options);
}
```

## 模块依赖

MetaHumanAnimator 是一个大型插件，包含 28 个模块。以下是主要的模块依赖关系：

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | MetaHuman 核心技术库（底层算法） |
| `MetaHumanSDKEditor` | MetaHuman SDK 编辑器工具 |
| `ControlRigDeveloper` | Control Rig 开发者工具，用于动画驱动 |
| `SkeletalMeshUtilitiesCommon` | 骨骼网格工具，用于面部网格处理 |
| `MetaHumanCaptureDataEditor` | 捕获数据编辑器 |
| `MetaHumanImageViewerEditor` | 图像查看器编辑器 |

MetaHumanDepthGenerator 模块自身无特殊公开依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 启用身体追踪时禁用关卡序列导出 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 渲染伪影问题 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 支持对已有网格导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存问题 |

### 维护评价

**活跃维护**。MetaHuman Animator 作为 Epic 官方的核心 MetaHuman 工具链，持续获得功能性更新和 Bug 修复。近期更新集中在：
- 身体追踪功能的集成优化
- 渲染质量修复
- Sequencer 集成改进
- 动画导出功能增强

该插件拥有 28 个模块、544 个源文件的庞大代码库，是 MetaHuman 生态系统的核心组成部分。由于 Epic 持续投资 MetaHuman 技术（包括与 Meta 的合作），该插件预计将持续得到长期维护。

**注意事项**：
- 该插件默认未启用（`Installed: false`），需要手动在插件管理器中启用
- 依赖 MetaHuman 核心技术库（`MetaHumanCoreTechLib`），可能需要额外下载
- 仅支持 Win64、Linux、Mac 平台
- 某些功能（如语音转面部）可能需要额外的云服务或本地模型

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/en-US/metahuman-animator/)（MetaHuman Animator 官方文档页面）