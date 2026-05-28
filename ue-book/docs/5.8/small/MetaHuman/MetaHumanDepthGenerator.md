# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman套件 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容资产） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | unknown |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

该插件是 Epic Games 为 Unreal Engine 提供的 MetaHuman 官方工具集，专注于从各种输入数据（如 iPhone 捕获、面部追踪数据）创建、配置和驱动高保真数字人资产。其核心目标是打通从原始面部视频到可驱动 MetaHuman 角色的完整制作流程。`MetaHumanDepthGenerator` 模块在此流程中扮演关键角色，负责从 iPhone 的 LiDAR 深度传感器或其他来源提供的图像序列中，计算并生成可用于后续面部拟合和资产优化的深度数据。

## 使用场景

- 你正在使用 iPhone Pro 的 LiDAR 传感器为真人演员拍摄面部性能数据，并希望将这些数据转换为可用于驱动 MetaHuman 角色的高精度深度序列。
- 你的虚拟制作工作流需要精确的深度信息，用于增强面部重建的准确性或进行后期合成。
- 你需要一个集成的工具来管理从素材捕获、深度处理到最终资产生成的自动化管线。

## 蓝图用法

该模块提供了用于在蓝图中控制深度生成过程的核心类和选项。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Process` | 从镜头捕获数据生成深度序列。 | `UMetaHumanDepthGenerator` |
| `AssetName` / `PackagePath` 等属性 | 配置深度生成的目标资产名称、存储路径、是否压缩等参数。 | `UMetaHumanGenerateDepthWindowOptions` |

### 使用示例（蓝图描述）

1.  **创建深度生成器**：在蓝图中，通过 `Construct Object from Class` 节点创建一个 `UMetaHumanDepthGenerator` 的实例。
2.  **配置选项**：创建或设置 `UMetaHumanGenerateDepthWindowOptions` 对象。设置其 `AssetName`、`PackagePath`、`ImageSequenceRootPath` 等属性。可以调整 `MinDistance` 和 `MaxDistance` 来过滤深度噪声，选择 `DepthPrecision` 和 `DepthResolution` 平衡精度与存储空间。
3.  **处理数据**：将已有的 `UFootageCaptureData` 对象（包含需要处理的图像序列）和配置好的 `UMetaHumanGenerateDepthWindowOptions` 对象作为输入，调用 `MetaHumanDepthGenerator` 的 `Process` 节点。此节点返回一个布尔值指示处理是否成功。

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanDepthGenerator.h"
#include "Widgets/MetaHumanGenerateDepthWindowOptions.h"
```

### 基本用法

```cpp
// 来源：Private/MetaHumanDepthGenerator.h
// 创建深度生成器实例
UMetaHumanDepthGenerator* DepthGenerator = NewObject<UMetaHumanDepthGenerator>();

// 获取或创建一个镜头捕获数据对象 (假设已经存在)
UFootageCaptureData* FootageData = /* ... */;

// 使用默认选项进行处理
bool bSuccess = DepthGenerator->Process(FootageData);

if (bSuccess)
{
    UE_LOG(LogTemp, Log, TEXT("深度数据生成成功。"));
}
```

### 进阶用法

```cpp
// 来源：Private/MetaHumanDepthGenerator.h & Private/Widgets/MetaHumanGenerateDepthWindowOptions.h
UMetaHumanDepthGenerator* DepthGenerator = NewObject<UMetaHumanDepthGenerator>();
UFootageCaptureData* FootageData = /* ... */;

// 创建并自定义选项对象
UMetaHumanGenerateDepthWindowOptions* Options = NewObject<UMetaHumanGenerateDepthWindowOptions>();
Options->AssetName = TEXT("MyCharacter_Depth");
Options->PackagePath.Path = TEXT("/Game/MetaHuman/Assets");
Options->ImageSequenceRootPath.Path = TEXT("C:/MyCapture/Sequences");
Options->bShouldCompressDepthFiles = false; // 为了调试，不压缩
Options->MinDistance = 5.0f;  // 忽略5cm以内的噪声
Options->MaxDistance = 30.0f; // 忽略30cm以外的数据

// 使用自定义选项进行处理
bool bSuccess = DepthGenerator->Process(FootageData, Options);
```

## Demo 示例

以下示例展示了如何通过 C++ 在编辑器工具中调用深度生成功能。

```cpp
// MyDepthTool.h
#pragma once
#include "CoreMinimal.h"

class UFootageCaptureData;
class UMetaHumanGenerateDepthWindowOptions;

class FMyDepthTool
{
public:
    void GenerateDepthForCaptureData(UFootageCaptureData* InCaptureData);
};

// MyDepthTool.cpp
#include "MyDepthTool.h"
#include "MetaHumanDepthGenerator.h"
#include "Widgets/MetaHumanGenerateDepthWindowOptions.h"

void FMyDepthTool::GenerateDepthForCaptureData(UFootageCaptureData* InCaptureData)
{
    if (!InCaptureData)
    {
        UE_LOG(LogTemp, Error, TEXT("输入的 CaptureData 无效。"));
        return;
    }

    // 1. 创建深度生成器
    UMetaHumanDepthGenerator* Generator = NewObject<UMetaHumanDepthGenerator>();

    // 2. 准备选项 (此处简化，实际可从UI或配置加载)
    UMetaHumanGenerateDepthWindowOptions* Options = NewObject<UMetaHumanGenerateDepthWindowOptions>();
    Options->AssetName = TEXT("GeneratedDepth");
    // 可以在此处设置更多 Options 参数...

    // 3. 执行处理
    bool bSuccess = Generator->Process(InCaptureData, Options);

    // 4. 处理结果
    if (bSuccess)
    {
        UE_LOG(LogTemp, Display, TEXT("为 %s 生成深度数据成功。"), *InCaptureData->GetName());
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("深度数据生成失败。"));
    }
}
```

## 模块依赖

`MetaHumanDepthGenerator` 模块的 Build.cs 未在输入中提供，但根据其功能（处理深度、集成编辑器窗口）以及它所属的 `MetaHumanAnimator` 插件的通用依赖，它很可能依赖以下模块。

| 模块 | 用途 |
|---|---|
| `MetaHumanCore` | 提供 MetaHuman 相关的核心类型和工具函数 |
| `MetaHumanCaptureUtils` | 提供用于处理捕获数据的通用工具 |
| `UMG` | 用于创建 `SMetaHumanGenerateDepthWindow` 所使用的 Slate/UMG 控件 |
| `EditorStyle` | 用于编辑器窗口和控件的样式 |
| `ContentBrowser` | 可能用于处理资产路径和包保存 |

*注意：具体依赖需查阅实际的 `MetaHumanDepthGenerator.Build.cs` 文件。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用身体追踪时，禁用关卡序列导出功能 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 上的渲染伪影 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 当进行身体追踪时，过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | [MHA] 为已有的网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存问题 |

### 维护评价

**综合评价：积极维护中**
- **年龄**：该插件是较新的官方工具（创建时间未知，但近期有密集更新）。
- **近期活跃度**：从提交记录看，在 2026 年 5 月仍有多次功能性更新和 bug 修复，表明其处于**积极维护**状态。
- **官方支持**：作为 Epic Games 的官方插件，其长期维护和兼容性有保障。
- **已知问题/限制**：文档提到 `MetaHumanDepthGeneratorAutoReimport` 中的功能与 `MetaHumanCaptureSource` 模块重复，计划未来合并，表明存在已知的技术债务。
- **推荐使用**：**强烈推荐**在需要进行从 iPhone 等设备捕获深度数据并生成 MetaHuman 的项目中使用。它是官方流程的核心部分，功能稳定且持续更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanDepthGenerator)
- [官方文档]() (无链接)
- [测试用例]() (无链接)