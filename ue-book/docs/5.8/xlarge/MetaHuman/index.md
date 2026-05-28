# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 动画师 |
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、资产处理逻辑、深度学习模型资源等） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 🆕（近年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方的 MetaHuman 资产创建、编辑和动画工具包。它提供了一整套工作流，允许用户通过面部捕捉（如 iPhone 深度摄像头数据）、视频素材或直接参数控制，将真实世界的表演应用到 MetaHuman 数字人角色上，生成高质量的面部动画。该插件涵盖了从原始数据输入、面部特征追踪、网格拟合、动画解算、性能优化到最终资产导出的全流程。

## 使用场景

- **影视与游戏制作**：将演员的面部表演捕捉并转移到 MetaHuman 角色上，用于过场动画或实时演出。
- **虚拟主播/数字人直播**：使用 iPhone 等设备实时驱动 MetaHuman 面部表情，进行虚拟直播或互动。
- **快速原型制作**：无需复杂的面部绑定设置，快速为角色生成自然的口型同步动画（通过 Speech2Face 功能）。
- **资产优化**：批量处理和优化大量 MetaHuman 动画资产，提升项目性能。
- **自定义流程开发**：利用其提供的底层协议栈和接口，构建自定义的面部捕捉与数据处理管道。

## 模块列表

本插件由 28 个运行时模块组成，构成一个庞大的处理链：

| 模块 | 简述 |
|---|---|
| **MetaHumanCore** / **CoreEditor** | 核心逻辑与编辑器基础框架 |
| **MetaHumanIdentity** / **IdentityEditor** | 负责 MetaHuman 角色资产的创建、管理和编辑 |
| **MetaHumanToolkit** | 提供通用的工具和UI界面 |
| **MetaHumanCaptureProtocolStack** | 处理网络捕获协议（如 Live Link Face） |
| **MetaHumanCaptureSource** | 管理和驱动各种面部/身体捕捉数据源 |
| **MetaHumanCaptureUtils** | 捕捉数据的通用工具函数库 |
| **MetaHumanFootageIngest** | 导入和预处理视频素材 |
| **MetaHumanDepthGenerator** | 从深度图（如 iPhone）生成面部深度数据 |
| **MetaHumanFaceContourTracker** / **Editor** | 面部特征点（轮廓）的追踪与解算 |
| **MetaHumanFaceFittingSolver** / **Editor** | 将追踪数据拟合到 MetaHuman 面部网格 |
| **MetaHumanFaceAnimationSolver** / **Editor** | 根据拟合结果解算最终的面部动画 |
| **MetaHumanSpeech2Face** | 从音频自动生成对应的面部动画（口型同步） |
| **MetaHumanControlsConversionTest** | 控制器转换的测试模块 |
| **MetaHumanPerformance** | 动画性能优化与数据压缩 |
| **MetaHumanPipeline** | 处理流程编排与管理 |
| **MetaHumanBatchProcessor** | 批量处理资产与动画 |
| **MetaHumanCaptureDataEditor** | 捕捉数据的编辑器视图与工具 |
| **MetaHumanImageViewerEditor** | 图像数据的查看器编辑器 |
| **MetaHumanConfig** / **ConfigEditor** | 插件配置管理 |
| **MetaHumanPlatform** | 平台特定功能抽象 |
| **MetaHumanSequencer** | 与 UE Sequencer 的集成，用于动画序列编辑 |
| **MeshTrackerInterface** | 身体追踪（如手部、身体）的接口抽象 |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)