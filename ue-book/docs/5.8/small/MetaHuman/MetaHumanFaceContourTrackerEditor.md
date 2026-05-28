# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman动画师 |
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（面部动画资产、编辑器工具） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 🆕 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方推出的 MetaHuman 工具包，用于将真实人类的面部表演数据（如视频、深度信息）驱动到 MetaHuman 角色上。它提供了一套完整的流程：从原始素材导入（Ingest）、面部特征点追踪（Contour Tracking）、面部网格拟合（Fitting）、动画求解（Animation Solving）到最终的序列化输出。该插件解决的核心问题是**将现实世界的面部表演数据高精度地转化为可驱动 MetaHuman 角色的动画资产**，是影视、游戏和虚拟直播领域制作逼真数字人的关键工具。

## 使用场景

- **影视与游戏过场动画制作**：你有一段演员的正面表演视频，需要将其驱动到 MetaHuman 角色上生成口型同步和表情动画。
- **虚拟直播与实时驱动**：通过摄像头捕捉你的面部动作，实时驱动一个 MetaHuman 虚拟形象进行直播。
- **批量动画生产**：你有一批已录制的表演视频文件，需要批量处理并生成对应的动画资产。
- **自定义面部追踪与求解**：你需要调整面部特征点的追踪精度或使用自定义的动画求解器。
- **从音频生成面部动画**：使用音频文件（Speech2Face）直接生成对应的面部动画。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Ingest Footage` | 将外部素材（如视频文件）导入并转换为插件内部数据格式 | `UMetaHumanFootageIngest` |
| `Track Face Contours` | 对导入的素材执行面部特征点追踪 | `UMetaHumanFaceContourTracker` |
| `Solve Face Animation` | 根据追踪数据计算面部动画曲线 | `UMetaHumanFaceAnimationSolver` |
| `Export Animation Sequence` | 将求解后的动画数据导出为动画序列资产 | `UMetaHumanPipeline` |
| `Create MetaHuman Identity` | 从一组参考图像创建或更新 MetaHuman 身份资产 | `UMetaHumanIdentity` |
| `Batch Process` | 对指定目录下的多个素材文件进行批量处理 | `UMetaHumanBatchProcessor` |

### 使用示例（蓝图描述）

1.  **单素材处理流程**：
    - 使用 `Ingest Footage` 节点将一个视频文件转换为 `UCaptureData` 资产。
    - 将 `UCaptureData` 输入到 `Track Face Contours` 节点，生成 `UFaceContourTrackerResult`。
    - 将追踪结果输入到 `Solve Face Animation` 节点，得到动画曲线数据。
    - 最后使用 `Export Animation Sequence` 节点将数据保存为 `UAnimSequence` 资产。

2.  **身份资产驱动**：
    - 使用 `Create MetaHuman Identity` 节点，连接一张或多张人物正面/侧面照片，生成 `UMetaHumanIdentity` 资产。
    - 在动画处理流程中，将该身份资产连接到 `Solve Face Animation` 节点的 `Identity` 输入，以获得更贴合该特定人物的动画效果。

## C++ 用法

### 头文件引入

由于该插件模块众多，需根据具体功能引入对应的头文件。例如：
```cpp
#include "MetaHumanCaptureUtils/CaptureData.h"
#include "MetaHumanFaceContourTracker/FaceContourTracker.h"
```

### 基本用法

```cpp
// 示例：在C++中启动一个简单的面部追踪任务（伪代码）
#include "MetaHumanFaceContourTracker/FaceContourTracker.h"

void StartTracking(UCaptureData* InCaptureData)
{
    UFaceContourTracker* Tracker = NewObject<UFaceContourTracker>();
    Tracker->StartTracking(InCaptureData, FOnTrackingComplete::CreateLambda([](bool bSuccess, UFaceContourTrackerResult* Result)
    {
        if (bSuccess)
        {
            // 处理追踪结果
        }
    }));
}
```

### 进阶用法

```cpp
// 示例：自定义动画求解器配置（需要对插件架构有深入了解）
#include "MetaHumanFaceAnimationSolver/FaceAnimationSolver.h"
#include "MetaHumanConfig/ConfigData.h"

void SolveWithCustomConfig(UFaceContourTrackerResult* InTrackerResult, UMetaHumanIdentity* InIdentity)
{
    UFaceAnimationSolver* Solver = NewObject<UFaceAnimationSolver>();
    
    // 加载自定义配置
    UConfigData* CustomConfig = LoadObject<UConfigData>(nullptr, TEXT("/Game/MetaHuman/Configs/MyCustomConfig"));
    if (CustomConfig)
    {
        Solver->SetConfig(CustomConfig);
    }
    
    Solver->Solve(InTrackerResult, InIdentity, FOnSolveComplete::CreateLambda([](bool bSuccess, UAnimationResult* Result)
    {
        // 导出或使用结果
    }));
}
```

## Demo 示例

由于 MetaHuman 插件极其庞大且高度集成，提供一个完整可编译的最小示例不现实。建议参考 Epic Games 官方示例项目 **“MetaHuman Sample”**，其中包含完整的 C++ 和蓝图工作流演示。核心的使用模式是通过 `UMetaHumanPipeline` 类驱动整个处理流程。

## 模块依赖

该插件的模块众多，且许多模块相互依赖。以下是关键的、不常见的依赖模块（已省略 Core, Engine, Slate 等标准依赖）：

| 模块 | 用途 |
|---|---|
| `CoreTechLib` | Epic 内部几何处理库，用于网格拟合和变形 |
| `ControlRig` | 用于驱动 MetaHuman 骨骼的控制绑定系统 |
| `SkeletalMeshUtilitiesCommon` | 骨骼网格体相关的通用工具 |
| `MeshTrackerInterface` | 提供深度传感器接口（如 LiDAR） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用身体追踪时，禁用关卡序列导出功能。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 角色上的渲染瑕疵问题。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 在身体追踪时过滤可视化对象，避免干扰。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | [MetaHuman动画] 支持对已存在的网格体导出动画序列。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复与 Sequencer（序列器）相关的缓存问题。 |

### 维护评价

- **活跃维护**：从最近的 Git 记录看，该插件正在被积极维护和更新，最近一次提交在 2026 年 5 月，包含功能改进和 bug 修复。
- **核心工具**：作为 Epic Games 官方 MetaHuman 工作流的核心部分，它拥有长期维护的保障。
- **复杂性高**：插件结构复杂，模块众多，学习曲线较陡峭，且对硬件（如用于深度捕捉的传感器）可能有特定要求。
- **推荐使用**：对于任何需要创建高保真数字人面部动画的 UE5 项目，**强烈推荐使用**此插件。它是目前 UE5 生态中完成此任务的官方和最完整的解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/metahuman-animator-in-unreal-engine/) (通用文档，非 .uplugin 指定)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanControlsConversionTest) (插件内包含一个测试模块 `MetaHumanControlsConversionTest`)