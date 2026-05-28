# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | 元人类动画师 |
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（资产、编辑器工具） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 🆕（年龄未知） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方的 MetaHuman 工具套件，旨在为 Unreal Engine 提供完整的 MetaHuman 数字人创建、驱动和动画工作流程。它解决了从原始视频或深度数据捕获，到面部追踪、模型拟合、动画生成以及资产管理的整套流程。其核心目标是让开发者和艺术家能够在虚幻引擎中高效、逼真地创建和驱动数字人角色。

## 使用场景

-   你需要为影视、游戏或虚拟制片创建逼真的数字人角色 → 使用 `MetaHumanIdentity` 和 `MetaHumanFaceFittingSolver`。
-   你有视频或深度相机捕捉的演员面部表演数据 → 使用 `MetaHumanCaptureSource` 和 `MetaHumanFaceContourTracker` 进行面部追踪与动画提取。
-   你需要将捕获的动画数据应用到 MetaHuman 角色上，并生成高质量的动画序列 → 使用 `MetaHumanFaceAnimationSolver` 和 `MetaHumanSequencer`。
-   你希望批量处理大量 MetaHuman 资产或动画数据 → 使用 `MetaHumanBatchProcessor`。
-   你需要管理多个 MetaHuman 角色的身份、配置和预设 → 使用 `MetaHumanConfig` 和 `MetaHumanIdentity`。
-   你希望通过音频直接生成面部动画 → 使用 `MetaHumanSpeech2Face`。

## 蓝图用法

**重要说明**：MetaHuman Animator 的大部分核心功能通过编辑器工具、专用资产和命令行操作实现。其运行时蓝图 API 相对有限，主要用于查询和操作配置与状态。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| (概念性) 获取/设置 MetaHuman 配置资产 | 在蓝图中查询或引用特定的 MetaHuman 配置资源。 | `UMetaHumanConfig` 等 |

**使用示例（蓝图描述）**
在蓝图中，你通常会通过资产引用来使用 MetaHuman 配置数据，例如，将一个 `UMetaHumanConfig` 资产拖拽到蓝图变量中。具体的动画驱动流程主要在 Sequencer、MetaHuman Toolkit 面板或通过命令行工具完成。

## C++ 用法

MetaHuman Animator 的主要 C++ 接口面向其内部工作流和编辑器扩展。

### 头文件引入

```cpp
// 根据使用的具体模块引入相应头文件
#include "MetaHumanConfig.h"
#include "MetaHumanIdentity.h"
// ... 其他模块头文件
```

### 基本用法

```cpp
// 假设需要程序化地引用一个 MetaHuman 配置资产
// 来自 MetaHumanConfig 模块
UMetaHumanConfig* Config = LoadObject<UMetaHumanConfig>(nullptr, TEXT("/Game/MetaHumans/MyConfig.MyConfig"));
if (Config)
{
    // 使用配置信息，例如获取预设的动画数据等
    // ... 具体接口需查阅源码 ...
}
```

### 进阶用法

```cpp
// 概念示例：使用 Pipeline 模块处理数据流
// 实际用法需要深入了解各模块的 Pipeline 定义
#include "MetaHumanPipeline.h"

// ... 设置一个处理管道，从捕获数据到最终动画
// 这涉及 MetaHumanCaptureSource, MetaHumanFaceContourTracker, MetaHumanFaceAnimationSolver 等模块的协同工作。
```

## Demo 示例

MetaHuman Animator 是一个复杂的工具套件，其“示例”通常体现为项目模板或工作流程文档。一个最小的可运行演示通常包含：
1.  一个 MetaHuman 角色资产（通过 MetaHuman Creator 创建）。
2.  一段视频或深度序列作为捕获数据。
3.  在 Unreal Editor 中，使用 MetaHuman Toolkit 面板导入数据、执行追踪和拟合。
4.  生成动画序列并应用到 MetaHuman 角色上。

## 模块依赖

以下是从 `Build.cs` 分析出的、该插件内部模块间和对外的独特依赖关系：

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | 提供底层的核心技术算法库（例如求解器）。 |
| `MetaHumanSDKEditor` | MetaHuman 的编辑器 SDK 集成。 |
| `SkeletalMeshUtilitiesCommon` | 用于骨骼网格体操作的通用工具。 |
| `ControlRigDeveloper` | 用于开发和处理 Control Rig（动画控制系统）。 |

*注意：该插件包含大量模块，模块间依赖复杂。上述列出的仅为从构建文件中识别出的、与 MetaHuman 功能直接相关的关键外部依赖模块。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 启用身体追踪时，禁用关卡序列导出功能。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 角色上的渲染瑕疵问题。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时，过滤可视化辅助对象。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | [MetaHuman Animator] 支持为现有网格体导出动画序列。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 中的缓存问题。 |

### 维护评价

**活跃维护**。MetaHuman Animator 是 Epic Games 的官方旗舰产品，受到持续、活跃的开发支持。从最近的 Git 记录（2026年5月）可以看出，插件仍在不断进行功能增强和 Bug 修复，例如新增身体追踪相关功能、优化导出流程和解决渲染问题。作为 MetaHuman 生态的核心组件，它预计将长期保持更新和维护。强烈推荐需要创建高质量数字人角色的团队使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/en-US/meta-humans-in-unreal-engine/) (MetaHuman 整体文档)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source) (测试代码通常内嵌在源码模块中，例如 `MetaHumanControlsConversionTest`)