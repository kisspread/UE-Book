# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | 元人类动画师 |
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（工具、资产） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-06-01 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是一个综合性的工具集，旨在将真实世界的视频素材（如智能手机录制的短视频）转化为驱动虚幻引擎中高保真MetaHuman角色面部动画的关键数据。其核心功能并非简单的“换脸”，而是通过复杂的计算机视觉和机器学习算法，从单目视频中提取面部运动信息，并将其精确地映射到MetaHuman的控制绑定（Control Rig）上，从而生成可直接在虚幻引擎中编辑和使用的动画数据。它解决了从表演捕捉到高质量数字人动画制作管线中的关键一环，大幅降低了创建逼真数字人角色的成本和难度。

## 使用场景

- **数字人内容创作**：使用智能手机为MetaHuman角色录制面部表演，并快速生成动画，用于虚拟主播、短视频或广告。
- **游戏开发**：为游戏中的过场动画或对话系统，批量生成高质量的面部动画序列。
- **影视虚拟制片**：将现场演员的表演实时或离线地应用到虚拟角色上，用于预演或最终渲染。
- **快速原型与迭代**：快速验证角色动画方案，无需昂贵的动作捕捉设备。
- **基于音频的动画生成**：结合`MetaHumanSpeech2Face`模块，可以从语音音频直接生成对应的面部动画。

## 模块列表

以下为插件包含的主要模块及其功能概述：

| 模块 | 说明 |
|---|---|
| **MetaHumanCore** | 核心功能模块，提供基础工具、类型定义和运行时支持。 |
| **MetaHumanPipeline** | 定义并处理捕捉到渲染的整个数据处理管线。 |
| **MetaHumanCaptureSource** | 集成各种视频/深度数据源，提供统一的输入接口。 |
| **MetaHumanCaptureProtocolStack** | 实现与外部设备（如iPhone LiDAR）进行数据通信的协议栈。 |
| **MetaHumanFaceContourTracker** | 核心算法模块，负责从视频帧中检测和追踪面部关键点轮廓。 |
| **MetaHumanFaceAnimationSolver** | 基于追踪数据，求解驱动MetaHuman面部的动画参数（Blendshapes）。 |
| **MetaHumanFaceFittingSolver** | 负责将MetaHuman的头部网格与追踪到的面部拓扑进行精确拟合对齐。 |
| **MetaHumanDepthGenerator** | 从单目RGB视频生成或估算深度信息，辅助3D重建。 |
| **MetaHumanIdentity** | 管理MetaHuman数字身份资产，包括头部拓扑、材质和绑定信息。 |
| **MetaHumanPerformance** | 存储和管理一次完整的捕捉会话（Performance）数据，包含原始和最终动画数据。 |
| **MetaHumanFootageIngest** | 处理和导入原始视频素材（Footage）数据。 |
| **MetaHumanSpeech2Face** | 利用语音音频生成对应面部动画的AI模型接口。 |
| **MetaHumanBatchProcessor** | 提供批量处理多个捕捉任务或动画的功能。 |
| **MetaHumanPlatform** | 处理平台相关的特定功能（如特定设备支持）。 |
| **MetaHumanConfig** | 管理插件的全局配置、参数和预设。 |
| **MetaHumanSequencer** | 集成虚幻引擎的定序器，支持在时间轴上编辑和预览捕捉的动画。 |
| **MeshTrackerInterface** | 定义网格追踪器的抽象接口，用于不同追踪后端的实现。 |
| **MetaHumanCaptureUtils** | 提供通用的捕捉和数据处理工具函数。 |
| **MetaHumanCoreEditor** | 编辑器专用核心功能，包含UI、资产编辑等。 |
| **MetaHumanConfigEditor** | 配置资产的编辑器界面和逻辑。 |
| **MetaHumanIdentityEditor** | MetaHuman Identity资产的编辑器工具和资产工厂。 |
| **MetaHumanPerformanceEditor** | Performance资产的编辑器工具，用于预览和微调动画。 |
| **MetaHumanFaceContourTrackerEditor** | 轮廓追踪器的编辑器设置和调试工具。 |
| **MetaHumanFaceFittingSolverEditor** | 面部拟合求解器的编辑器参数调整工具。 |
| **MetaHumanFaceAnimationSolverEditor** | 面部动画求解器的编辑器界面和调试可视化。 |
| **MetaHumanCaptureDataEditor** | 捕捉数据资产的编辑器查看器。 |
| **MetaHumanImageViewerEditor** | 提供图像序列查看器的编辑器窗口，用于调试追踪过程。 |
| **MetaHumanControlsConversionTest** | 控制参数转换功能的测试模块。 |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/en-US/AnimatingObjects/SkeletalMeshAnimation/Personas/Tools/MetaHumanAnimator/)
- [测试用例]() (路径待补充)