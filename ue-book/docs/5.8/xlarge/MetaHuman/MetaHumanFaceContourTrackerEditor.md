# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 元人类动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器资产） |
| 模块 | `MetaHumanFaceContourTrackerEditor` (Runtime), `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

`MetaHuman Face Contour Tracker Editor` 是 `MetaHuman Animator` 大型插件中的一个子模块，专门用于为 MetaHuman 面部轮廓追踪器资产（`UMetaHumanFaceContourTrackerAsset`）提供编辑器支持。它的主要功能是在虚幻编辑器中定义和管理用于面部特征点追踪的资产，这些资产是 MetaHuman 角色进行面部动画驱动（如通过视频捕捉）工作流中的关键数据结构。该模块解决了在编辑器环境中创建、配置和预览面部轮廓追踪配置的问题。

## 使用场景

- 你正在使用 MetaHuman 工作流，并希望通过视频或图像序列驱动 MetaHuman 角色的面部表情。
- 你需要自定义面部特征点的追踪方式，以优化特定面部动画捕捉（Performance Capture）的结果。
- 作为 MetaHuman Animator 工具链的一部分，你需要在编辑器中配置面部轮廓追踪器资产，以便后续用于面部动画求解。

## 蓝图用法

此模块主要提供编辑器集成（资产工厂、资产定义），没有直接暴露给蓝图的运行时节点。其功能主要通过编辑器内的资产创建和属性面板进行操作。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| 无直接蓝图节点 | 此模块不提供 `BlueprintCallable` 函数。其功能通过编辑器资产类型和工厂暴露。 | - |

### 使用示例（蓝图描述）

1.  在内容浏览器中右键点击。
2.  在 `Animation` 或 `MetaHuman` 类别下，选择 “MetaHuman Face Contour Tracker” 来创建一个新的资产。
3.  在资产编辑器中配置追踪参数（具体选项取决于 `MetaHumanFaceContourTracker` 模块提供的属性）。
4.  该资产可被 `MetaHumanPerformance` 等其他模块引用，用于驱动面部动画。

## C++ 用法

此模块的C++接口主要用于编辑器扩展和资产类型注册。开发者通常不直接与 `MetaHumanFaceContourTrackerEditor` 模块交互，而是使用其定义的资产类型 `UMetaHumanFaceContourTrackerAsset`（定义在 `MetaHumanFaceContourTracker` 运行时模块中）。

### 头文件引入

如需在编辑器工具或资产处理逻辑中访问该资产的定义，可能需要包含：

```cpp
// 访问资产类定义
#include "MetaHumanFaceContourTracker/Public/MetaHumanFaceContourTrackerAsset.h"
```

### 基本用法

该模块的核心是 `UMetaHumanFaceContourTrackerAssetFactoryNew` 类，它负责在编辑器中创建新的追踪器资产实例。

```cpp
// 通常不会直接实例化工厂，而是由编辑器自动使用
// UMetaHumanFaceContourTrackerAssetFactoryNew 工厂会在用户通过内容浏览器创建资产时被调用
// 其 `FactoryCreateNew` 方法实现了资产的创建逻辑
```

### 进阶用法

`UAssetDefinition_MetaHumanFaceContourTracker` 类定义了该资产在编辑器中的显示方式（名称、颜色、类别）以及双击打开时的行为。如果要扩展该资产的编辑器功能，可以参考或继承此类的模式。

## Demo 示例

由于此模块是纯编辑器支持模块，且其运行时资产类 (`UMetaHumanFaceContourTrackerAsset`) 的具体使用高度集成在 MetaHuman Animator 复杂的管线中，提供一个独立的可编译最小示例意义不大。建议参考 Epic Games 官方的 MetaHuman Animator 示例项目。

## 模块依赖

从 `MetaHumanFaceContourTrackerEditor.Build.cs` 文件分析：

| 模块 | 用途 |
|---|---|
| `MetaHumanImageViewerEditor` | 提供图像查看器编辑器支持，用于预览面部轮廓追踪结果 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用身体追踪时，禁用关卡序列导出功能 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复了 MetaHuman 上的渲染瑕疵 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 在身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | [MetaHuman Animator] 为现有网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复了 Sequencer 缓存问题 |

### 维护评价

基于提供的信息，`MetaHuman Animator` 插件处于 **积极维护** 状态。从近期提交记录（截至2026年5月）可以看出，团队正在持续修复问题、增加新功能（如针对身体追踪的优化）并优化性能。作为 Epic Games 官方的核心 MetaHuman 工具套件，它获得了很高的开发优先级。虽然 `MetaHumanFaceContourTrackerEditor` 本身是较小的编辑器模块，但其所属的整体插件是活跃且推荐的。目前没有观察到已知的重大限制或废弃标记。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- 官方文档: （.uplugin 中未提供 DocsURL，建议查阅 Epic Games 官方 MetaHuman 文档）