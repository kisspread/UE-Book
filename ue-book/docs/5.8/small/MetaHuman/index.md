# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、配置资产） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 🆕（约 N 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是一个**用于将真实人类表演驱动数字 MetaHuman 角色**的完整工具包。它不仅仅是一个动画工具，更是一个集成的**面部动作捕捉、求解、拟合与动画制作流水线**。

该插件解决的核心问题是：如何将来自手机、专业相机或深度传感器的原始人脸视频数据，高效、准确地转换为适用于 MetaHuman 角色的面部动画数据。它集成了从数据导入、面部特征追踪、动画参数求解、到最终动画序列导出的全部流程，是 Epic 官方为 MetaHuman 生态系统提供的一站式动画解决方案。

## 使用场景

- **虚拟人表演捕捉**：你使用 iPhone 的深度摄像头（或兼容设备）拍摄了一段演员的面部表演，需要将这些数据转换为 MetaHuman 角色的动画。
- **批量处理表演数据**：你有一个包含大量视频素材的数据库，需要批量转换为动画数据。
- **面部动画制作**：你需要从零开始创建精确的面部动画，或对现有动画进行修正和优化。
- **实时驱动预览**：在编辑器或运行时，希望实时查看表演驱动 MetaHuman 的效果。
- **语音驱动面部动画**：你希望根据一段音频文件，自动生成对应的面部动画。

## 模块概览

本插件由 28 个模块组成，按功能可分为以下几类：

### 核心与平台
| 模块 | 简述 |
|---|---|
| `MetaHumanCore` | 提供核心功能、数据类型和运行时基础。 |
| `MetaHumanPlatform` | 处理与特定平台相关的功能。 |
| `MetaHumanConfig` | 管理插件的配置资产和设置。 |

### 捕获与输入
| 模块 | 简述 |
|---|---|
| `MetaHumanCaptureProtocolStack` | 实现与捕获设备（如手机 App）通信的协议栈。 |
| `MetaHumanCaptureSource` | 处理来自各种捕获设备的原始数据源。 |
| `MetaHumanCaptureUtils` | 提供捕获相关的通用工具函数。 |
| `MetaHumanFootageIngest` | 导入和预处理视频素材（Footage）。 |
| `MeshTrackerInterface` | 提供网格追踪的接口抽象。 |

### 追踪与求解
| 模块 | 简述 |
|---|---|
| `MetaHumanFaceContourTracker` | 从视频中追踪人脸关键点和轮廓。 |
| `MetaHumanFaceAnimationSolver` | 将追踪到的数据求解为 MetaHuman 的面部动画控制参数。 |
| `MetaHumanFaceFittingSolver` | 将追踪数据拟合到特定的 MetaHuman 面部模型上。 |
| `MetaHumanDepthGenerator` | 从视频或其他数据生成深度信息。 |
| `MetaHumanSpeech2Face` | 实现语音驱动面部动画的算法。 |

### 数据与流水线
| 模块 | 简述 |
|---|---|
| `MetaHumanPipeline` | 定义和管理数据处理流水线，串联各处理步骤。 |
| `MetaHumanIdentity` | 管理与 MetaHuman 角色身份（如面部网格）相关的数据。 |
| `MetaHumanPerformance` | 管理“表演”数据，即捕获的动画序列。 |
| `MetaHumanSequencer` | 与 UE 的 Sequencer 集成，用于回放和编辑动画序列。 |
| `MetaHumanBatchProcessor` | 提供批量处理多个资产或序列的功能。 |

### 编辑器与工具
| 模块 | 简述 |
|---|---|
| `MetaHumanToolkit` | 提供主编辑器工具集（Toolkit）的界面和逻辑。 |
| `MetaHumanCoreEditor` | 提供核心编辑器功能。 |
| `MetaHumanConfigEditor` | 提供配置资产的编辑器界面。 |
| `MetaHumanIdentityEditor` | 提供身份数据的编辑器工具。 |
| `MetaHumanPerformanceEditor` | 提供表演数据的编辑器工具。 |
| `MetaHumanCaptureDataEditor` | 提供捕获数据的编辑器查看和编辑工具。 |
| `MetaHumanImageViewerEditor` | 提供图像查看器的编辑器部件。 |
| `MetaHumanFaceContourTrackerEditor` | 提供轮廓追踪器的编辑器设置界面。 |
| `MetaHumanFaceAnimationSolverEditor` | 提供动画求解器的编辑器设置界面。 |
| `MetaHumanFaceFittingSolverEditor` | 提供拟合求解器的编辑器设置界面。 |
| `MetaHumanControlsConversionTest` | 包含用于测试控件转换的模块。 |

## 蓝图用法概述

该插件主要通过编辑器工具进行交互，但其核心模块也暴露了蓝图 API，主要用于在运行时或构建自定义流水线时使用。

### 核心节点（示例）

| 节点类别 | 说明 | 所在模块 |
|---|---|---|
| **捕获管理** | 开始、停止捕获会话，管理设备连接。 | `MetaHumanCaptureSource`, `MetaHumanCaptureProtocolStack` |
| **数据处理** | 触发面部追踪、动画求解、模型拟合等核心处理步骤。 | `MetaHumanPipeline`, `MetaHumanFaceContourTracker`, `MetaHumanFaceAnimationSolver` |
| **资产操作** | 创建、加载、保存 MetaHuman 表演（Performance）和身份（Identity）资产。 | `MetaHumanPerformance`, `MetaHumanIdentity` |
| **序列化导出** | 将处理后的动画数据导出为动画序列或应用到角色上。 | `MetaHumanSequencer`, `MetaHumanPerformance` |

> **注意**：由于此插件规模巨大，蓝图节点众多且复杂。具体节点的详细功能、参数和连接方式，请参考各子模块的独立文档。

## C++ 用法概述

在 C++ 中使用此插件通常是为了扩展流水线或创建更底层的自动化工具。

### 头文件引入
```cpp
// 核心功能
#include "MetaHumanCore/Public/MetaHumanCoreModule.h"
// 流水线定义
#include "MetaHumanPipeline/Public/Nodes/MetaHumanPipelineNode.h"
// 具体的求解器
#include "MetaHumanFaceAnimationSolver/Public/FaceAnimationSolver.h"
```

### 基本用法（概念示例）
```cpp
// 1. 获取流水线实例（通常从配置资产加载）
UMetaHumanPipeline* Pipeline = /* 从某个配置资产获取 */;

// 2. 创建或配置处理节点
UMetaHumanFaceContourTrackerNode* TrackerNode = NewObject<UMetaHumanFaceContourTrackerNode>();
Pipeline->AddNode(TrackerNode);

// 3. 设置输入数据（例如，一个视频帧序列）
FMetaHumanFrameData InputData;
TrackerNode->SetInputData(InputData);

// 4. 执行流水线
Pipeline->Process();

// 5. 获取输出结果
FMetaHumanAnimationData OutputAnimation = TrackerNode->GetOutputData();
```

> **注意**：以上为概念性代码。实际使用中，流水线的构建、节点的配置以及数据交换都非常复杂，需要深入研究各模块的 API。详细用法请参阅对应模块的文档。

## Demo 示例

本插件通常通过编辑器内的 **“MetaHuman Animator” 工具面板** 进行使用，这是一个基于 Slate 构建的复杂编辑器窗口，集成了从捕获设置、数据导入、处理、预览到导出的完整 UI。其核心逻辑分布在 `MetaHumanToolkit`、`MetaHumanCoreEditor` 等多个编辑器模块中。

一个最小的可运行 C++ 示例将涉及创建和驱动整个处理流水线，其复杂度远超普通插件。因此，**推荐用户直接使用编辑器工具**，并仅在需要深度定制时才通过 C++ 调用底层模块。

## 模块依赖

该插件的模块相互依赖紧密，且依赖 UE 的多个特定子系统。

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | MetaHuman 核心技术算法库（可能包含数学、几何处理等）。 |
| `MetaHumanSDKEditor` | MetaHuman SDK 的编辑器部分，提供与 MetaHuman 角色资产的交互。 |
| `ControlRigDeveloper` | 用于驱动 MetaHuman 角色的 Control Rig 开发相关模块。 |
| `SkeletalMeshUtilitiesCommon` | 提供骨骼网格体处理的通用工具。 |
| `LiveLinkInterface` | （隐式依赖）用于与 Live Link 系统集成，可能用于实时数据流。 |
| `MovieScene`, `LevelSequence` | 用于动画序列的录制和回放。 |
| `MediaUtils`, `MediaAssets` | 用于处理视频媒体文件。 |
| `ImageCore`, `ImageWrapper` | 用于图像数据的加载、处理和格式转换。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 启用身体追踪时禁用关卡序列导出，避免数据冲突。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 角色上的渲染瑕疵。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤掉不必要的可视化对象，提升性能。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 支持为已有的网格体导出动画序列。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 中的缓存问题。 |

### 维护评价
- **活跃维护**：从提交历史看，该插件正在被**积极开发和维护**，近期（2026年5月）有多次重要的功能更新和错误修复。
- **核心功能**：作为 MetaHuman 生态的核心动画工具，其重要性不言而喻，Epic 持续投入资源。
- **推荐使用**：如果你的工作流涉及 MetaHuman 角色的动画制作，**强烈推荐使用**此官方工具包。它功能强大且与 UE 集成度高。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/metahuman-animator-in-unreal-engine/) （Epic 官方 MetaHuman Animator 文档入口）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Tests) （模块内部的测试代码）