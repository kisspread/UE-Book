# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 动画工具 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质、网格体等） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 🆕（< 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

**MetaHuman Animator** 是 Epic Games 官方推出的、用于在 Unreal Engine 内创建和驱动 MetaHuman 数字人的完整工具套件。它不仅仅是动画工具，而是一个涵盖了从**面部动作捕捉数据采集、处理、拟合、求解到动画制作和回放**全流程的综合性管线。

插件的核心流程通常为：
1.  **捕捉**: 使用 iPhone 的 Face ID 摄像头或其他兼容设备，通过 `MetaHumanCaptureSource` 模块录制面部表演视频。
2.  **深度生成**: 利用 `MetaHumanDepthGenerator` 模块，从单目 RGB 视频序列推算出深度信息，用于后续的三维重建。
3.  **面部拟合**: 使用 `MetaHumanFaceFittingSolver` 模块，将捕获的深度数据或视频数据“拟合”到 MetaHuman 标准面部拓扑结构上。
4.  **动画求解**: 通过 `MetaHumanFaceAnimationSolver` 模块，将拟合后的数据转换为 MetaHuman 面部骨骼的动画控制曲线。
5.  **驱动与编辑**: 在 `MetaHumanSequencer` 和 `MetaHumanPerformance` 模块中，将这些动画数据应用到 MetaHuman 角色上，并在 Sequencer 时间轴中进行精细编辑。

该插件解决了将现实世界中的人脸表演高保真地迁移到数字资产上的核心难题，是影视、游戏和虚拟制片领域制作高品质数字人动画的行业标准工具之一。

## 使用场景

- 你正在为一款游戏或一部影视作品创建逼真的数字人角色，并需要将其真实的演员表演迁移到数字模型上。
- 你需要一个集成在 UE 内部的、无需依赖外部复杂动捕软件的面部动画制作流程。
- 你已经有 MetaHuman 角色，希望快速为其添加高质量的面部动画，而不是手动制作或依赖通用的面部绑定。
- 你正在研究虚拟人、虚拟主播或数字孪生应用，需要实时或准实时地驱动虚拟角色面部。

## 蓝图用法

本插件的大部分核心操作通常通过编辑器 UI（如专用窗口和资产编辑器）进行，但部分底层功能也暴露给蓝图。以下基于 `MetaHumanDepthGenerator` 子模块的公开接口进行说明。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Process` | 使用指定选项处理镜头数据以生成深度信息 | `UMetaHumanDepthGenerator` |
| `AssetName` (属性) | 设置生成资产的名称 | `UMetaHumanGenerateDepthWindowOptions` |
| `PackagePath` (属性) | 设置生成资产的保存路径 | `UMetaHumanGenerateDepthWindowOptions` |
| `ImageSequenceRootPath` (属性) | 设置源图像序列的根目录 | `UMetaHumanGenerateDepthWindowOptions` |
| `MinDistance` / `MaxDistance` (属性) | 设置有效深度范围的最小和最大距离（厘米），用于过滤噪声 | `UMetaHumanGenerateDepthWindowOptions` |
| `DepthPrecision` (属性) | 设置深度数据的精度（如八分之一精度），影响精度和存储空间 | `UMetaHumanGenerateDepthWindowOptions` |
| `DepthResolution` (属性) | 设置深度数据的分辨率缩放，影响精度和存储空间 | `UMetaHumanGenerateDepthWindowOptions` |

### 使用示例（蓝图描述）

1.  **创建选项对象**：在蓝图中创建一个 `UMetaHumanGenerateDepthWindowOptions` 类型的变量。
2.  **配置选项**：设置该对象的各项属性，如 `AssetName`，`PackagePath` 指向项目内容目录，`ImageSequenceRootPath` 指向存放原始视频帧的文件夹。
3.  **执行生成**：获取或创建一个 `UMetaHumanDepthGenerator` 对象，调用其 `Process` 函数，并传入你准备好的镜头数据（`UFootageCaptureData`）和上一步配置好的选项对象。
4.  **检查结果**：`Process` 函数会返回一个布尔值指示成功与否。如果成功，生成的深度序列资产将保存在指定的 `PackagePath` 中。

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanDepthGenerator.h"
#include "Widgets/MetaHumanGenerateDepthWindowOptions.h"
#include "MetaHumanCapture/Public/FootageCaptureData.h" // 镜头数据来源
```

### 基本用法

以下示例展示了如何在代码中调用深度生成功能。

```cpp
// 假设你已经获得了镜头捕获数据的指针
UFootageCaptureData* MyCaptureData = ...;

// 创建并配置深度生成选项
UMetaHumanGenerateDepthWindowOptions* Options = NewObject<UMetaHumanGenerateDepthWindowOptions>();
Options->AssetName = TEXT("MyDepthSequence");
Options->PackagePath.Path = TEXT("/Game/MetaHuman/Generated");
Options->ImageSequenceRootPath.Path = TEXT("D:/MyCaptures/Subject01/Images");
Options->bAutoSaveAssets = true;
Options->MinDistance = 5.0f;
Options->MaxDistance = 30.0f;

// 创建深度生成器并执行处理
UMetaHumanDepthGenerator* DepthGenerator = NewObject<UMetaHumanDepthGenerator>();
bool bSuccess = DepthGenerator->Process(MyCaptureData, Options);

if (bSuccess)
{
    UE_LOG(LogTemp, Log, TEXT("深度数据生成成功！"));
}
else
{
    UE_LOG(LogTemp, Error, TEXT("深度数据生成失败。"));
}
```

*(注：此代码基于对 `MetaHumanDepthGenerator.h` 和 `MetaHumanGenerateDepthWindowOptions.h` 头文件的分析，展示了典型的类实例化和方法调用模式。)*

### 进阶用法

对于需要深度集成的工具或自动化流程，你可能需要：
1.  **批量处理**：遍历多个 `UFootageCaptureData` 对象，为每个创建独立的 `Options` 并调用 `Process`。
2.  **自定义流程**：深度生成通常是一个更大流程（如完整的面部动画流程）的一部分。你可以在 `MetaHumanPipeline` 模块中定义自定义流程，将深度生成作为其中一个节点。
3.  **访问底层数据**：生成的深度数据通常以纹理序列或体积纹理的形式存储。你可以通过 UE 的资产系统加载这些资产，并用于自定义的渲染或分析。

## Demo 示例

由于这是一个专注于特定生产管线的插件，没有简单的独立可编译示例。其使用通常通过编辑器内的“MetaHuman Animator”面板启动。

一个概念性的 C++ 使用示例如上“基本用法”章节所示，它演示了如何触发深度数据生成流程。

## 模块依赖

使用 `MetaHumanDepthGenerator` 模块，你的 `Build.cs` 文件需要添加以下依赖。这些是该模块**特有**的依赖：

| 模块 | 用途 |
|---|---|
| `MetaHumanCaptureData` | 提供镜头捕获数据 (`UFootageCaptureData`) 等基础数据类型 |
| `MetaHumanCore` | 提供 MetaHuman 共享的核心工具和数据类型 |
| `CameraCalibrationCore` | 用于处理摄像头校准数据 (`UCameraCalibration`) |
| `FootageIngest` | 用于管理和处理导入的影片素材 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 启用身体追踪时，禁用关卡序列导出功能 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复了在 MetaHuman 上出现的渲染瑕疵 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 当进行身体追踪时，过滤掉可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | [MetaHuman Animator] 支持为现有网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复了 Sequencer 的缓存问题 |

### 维护评价

该插件处于**积极维护**状态。从最近的提交历史看，Epic Games 团队仍在持续更新，主要集中在功能增强（如支持为现有网格体导出动画）、错误修复（渲染瑕疵、缓存问题）以及与新功能（如身体追踪）的集成适配。

- **活跃度**：非常高，每周都有多次提交。
- **稳定性**：核心功能稳定，但作为复杂管线的一部分，小版本迭代中可能会进行调整。
- **推荐度**：**强烈推荐**用于专业的数字人动画制作。它是 MetaHuman 生态系统的官方和核心组件，文档和社区支持也在不断完善。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/metahuman-animator-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanControlsConversionTest)