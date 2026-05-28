# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产，内容资产） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 待定 |
| 年龄标签 | 待定 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 提供的官方 MetaHuman 工具包，旨在为虚幻引擎提供一整套用于创建、驱动和管理高保真数字人（MetaHuman）的完整流程。它不仅仅是一个资产集合，更是一个集成了从捕获数据处理、面部/身体追踪、动画求解到最终在引擎中驱动和控制数字人的端到端解决方案。

这个插件解决的核心问题是：**如何将现实世界中演员的表演（通常来自视频、深度相机或音频）高效、逼真地转化为可直接在引擎中使用的 MetaHuman 动画数据**。它填补了从原始捕获素材到可驱动数字人之间的技术鸿沟，让开发者能够专注于创意，而非底层复杂的图形学与动画处理。

## 使用场景

- 你正在制作一款叙事驱动的游戏，需要将真人演员的表演完整转移到游戏角色上，以实现电影级的过场动画。
- 你的项目需要从 iPhone 深度相机或专业动捕设备拍摄的视频中，快速生成角色的面部和身体动画。
- 你希望利用音频（语音）驱动数字人面部表情，实现对话系统的自动口型同步。
- 你需要一个统一的平台来管理多个数字人资产（Identity）、配置其控制绑定，并批量处理动画数据。
- 你正在开发一个包含大量数字人角色的虚拟制片或实时渲染项目，需要高效的资产管理和动画驱动工作流。

## 蓝图用法

基于提供的 `MetaHumanCaptureDataEditor` 模块头文件分析，该插件主要通过编辑器工具、资产处理器和自定义UI组件与用户交互，蓝图可直接调用的运行时节点相对较少。其核心蓝图用法通常体现在对 `UCaptureData`、`UMetaHumanIdentity`、`UPerformance` 等资产的操作，以及通过编辑器工具栏和自定义资产编辑器界面触发处理流程。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreatePreviewComponent` | 根据给定的捕获数据资产创建一个用于在编辑器中预览的场景组件。 | `MetaHumanCaptureDataUtils` |

### 使用示例（蓝图描述）

由于该插件的大部分功能封装在编辑器模式和资产处理管线中，典型的蓝图用法是间接的：
1.  **资产导入与处理**：通过“内容浏览器”的右键菜单或自定义资产编辑器（如 MetaHuman Identity Editor）导入原始捕获数据（视频、音频），并触发自动处理流程（面部追踪、动画求解等）。这些流程在后台运行，并生成可驱动 MetaHuman 的动画资产。
2.  **数据预览与验证**：在自定义的“图像查看器”或“捕获数据”资产编辑器中，使用 `SMetaHumanCameraCombo` 等自定义UI组件切换查看不同机位的捕获数据，并验证处理结果。
3.  **动画驱动**：将处理好的动画资产（如 `UPerformance`）或控制绑定（Control Rig）应用到场景中的 MetaHuman 角色上，通过 Sequencer 进行编排或实时驱动。

## C++ 用法

### 头文件引入

```cpp
#include "CaptureDataUtils.h"
```

### 基本用法

该插件提供的公开 C++ API 主要集中在编辑器扩展和数据处理工具类上。

```cpp
// 创建捕获数据的预览组件，用于在编辑器视口或资产编辑器中可视化显示。
// 来源: Source/MetaHumanCaptureDataEditor/Public/CaptureDataUtils.h
UCaptureData* MyCaptureData = /* 从项目中获取的捕获数据资产 */;
UObject* OuterObject = GetOuter(); // 通常为资产编辑器或上下文对象

if (MyCaptureData)
{
    USceneComponent* PreviewComp = MetaHumanCaptureDataUtils::CreatePreviewComponent(MyCaptureData, OuterObject);
    if (PreviewComp)
    {
        // 将预览组件附加到需要显示的Actor或直接管理
        PreviewComp->RegisterComponent();
    }
}
```

### 进阶用法

更复杂的用法涉及继承或使用插件内部的编辑器工具和管线。例如，自定义一个处理节点并将其集成到 MetaHuman 处理管线中，这通常需要深入理解 `MetaHumanPipeline` 模块的架构。由于插件规模庞大且复杂，详细的 C++ 集成需要参考引擎源码和 Epic 提供的开发指南。

## Demo 示例

由于该插件主要提供完整的编辑器工作流和资产处理管线，一个“可编译的最小示例”会过于简化且不具代表性。更实用的示例是学习如何通过其自定义的资产编辑器和处理流程来使用它。核心步骤如下：

1.  **启用插件**：在编辑器“插件”面板中搜索并启用 “MetaHuman Animator”。
2.  **获取资产**：从 Quixel Bridge 或 MetaHuman Creator 获取一个 MetaHuman 角色并导入项目。
3.  **创建身份资产**：在内容浏览器中右键 -> MetaHuman -> MetaHuman Identity，创建一个新的身份资产并将其与导入的 MetaHuman 关联。
4.  **捕获表演**：使用兼容的设备（如 iPhone）录制一段面部表演视频，或使用音频文件。
5.  **处理数据**：在身份资产编辑器中导入捕获的视频/音频，使用内置工具进行面部追踪、标记点和处理，最终生成可驱动该 MetaHuman 的动画资产。
6.  **驱动角色**：在场景中放置 MetaHuman 角色，将生成的动画资产或控制绑定应用给它。

## 模块依赖

该插件自成体系，拥有29个模块，各模块间相互依赖。使用者通常需要依赖以下特定模块来与 MetaHuman Animator 的核心数据和功能交互。

| 模块 | 用途 |
|---|---|
| `MetaHumanCore` | 包含核心数据类型（如 `UCaptureData`, `UMetaHumanIdentity`, `UPerformance`）和基础功能。 |
| `MetaHumanConfig` | 管理插件的全局配置和设置。 |
| `MetaHumanFaceAnimationSolver` | 包含面部动画求解算法，将追踪数据转换为动画曲线。 |
| `MetaHumanFaceFittingSolver` | 包含面部拟合求解器，用于将通用面部网格拟合到特定身份的拓扑结构。 |
| `MetaHumanPipeline` | 定义和驱动模块化数据处理管线，是自动化工作流的核心。 |
| `MetaHumanSequencer` | 提供与 Sequencer 的深度集成，用于编排和播放 MetaHuman 动画。 |
| `MetaHumanCaptureProtocolStack` | 实现与外部设备（如深度相机）的通信协议。 |
| `MetaHumanImageViewerEditor` | 提供用于查看和分析捕获图像序列的自定义编辑器窗口。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用身体追踪时，禁用关卡序列导出功能，可能为了解决冲突或简化流程。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 角色上的渲染瑕疵。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 在身体追踪模式下过滤掉特定的可视化对象，优化视图。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | [MetaHuman Animator] 支持为已有的网格体导出动画序列。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存相关的问题。 |

### 维护评价

MetaHuman Animator 是 Epic Games 官方维护的旗舰级插件，用于支持其 MetaHuman 技术栈。从近期（2026年5月）的提交记录可以看出，该插件正处于**非常活跃**的开发和维护阶段，近期更新频繁，涵盖了功能增强、Bug修复和工作流优化。作为官方支持的核心工具链，其稳定性和长期维护有较高保障。尽管文件数量庞大（544个），但其模块化设计清晰。

**推荐使用**：对于任何需要使用 MetaHuman 技术的虚幻引擎项目，此插件是必不可少的工具。它提供了目前最完整、最深入的数字人创建与驱动解决方案。由于其复杂性，建议从 Epic 官方文档和教程开始学习。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- 官方文档：暂无直接链接（.uplugin 中 DocsURL 为空），请参考 Epic Games 官网的 MetaHuman 文档中心。