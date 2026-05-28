# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | 元人类动画师 |
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质、配置等） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 🆕（年龄未知） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方的元人类数字人工具包，核心功能是将真实演员的面部表演（通过 iPhone、专业头盔或其他设备捕获）转换为高保真数字人 MetaHuman 的面部动画。它不仅仅是一个简单的追踪工具，而是提供了一套完整的从数据捕获、处理、拟合、求解到最终动画输出的端到端工作流。该插件解决了将现实世界复杂面部肌肉运动精确映射到虚拟角色上的核心难题，是创建电影级实时数字人表演的关键。

当前聚焦的模块 `MetaHumanFaceContourTrackerEditor` 是工作流中的一个基础构建块，它主要负责在编辑器内提供面部轮廓追踪资产的管理界面和创建工厂，是艺术家和开发者定义和维护“如何追踪面部特征轮廓”这一规则的基石。

## 使用场景

- **影视/游戏过场动画制作**：你需要将专业演员的表演无缝转移到数字人角色上，以制作电影级的过场动画。
- **实时直播/虚拟偶像驱动**：你正在开发一个实时驱动的数字人直播应用，需要通过 iPhone 前置摄像头捕捉主播表情并实时渲染。
- **数字人资产创建流程**：你的团队需要一套标准化、可复用的工具来处理大量演员的面部数据，并生成高质量的动画资产。
- **自定义面部追踪规则**：你需要针对特定面部特征（如特殊妆容、纹身）或非标准人脸形状来调整和优化轮廓追踪的算法与规则，这便是 `MetaHumanFaceContourTrackerEditor` 模块的核心应用场景。

## 蓝图用法

`MetaHumanFaceContourTrackerEditor` 模块主要提供编辑器扩展功能（资产工厂和资产定义），并未直接暴露用于运行时逻辑的蓝图节点。其功能集成在 MetaHuman Animator 的编辑器 UI 工作流中。面部追踪过程的控制和配置主要通过 MetaHuman Animator 的专用编辑器资产（如 `UMetaHumanIdentity`）和面板进行，而非直接使用独立的蓝图节点。

## C++ 用法

此模块主要扩展了 Unreal Editor 的资产系统。开发者可以通过继承其提供的基类来创建或自定义面部轮廓追踪资产。

### 头文件引入

```cpp
#include “MetaHumanFaceContourTrackerAssetFactoryNew.h”
#include “AssetDefinition_MetaHumanFaceContourTracker.h”
```

### 基本用法

理解面部轮廓追踪资产在编辑器中的创建和呈现方式。

```cpp
// 示例：理解 MetaHumanFaceContourTrackerEditor 如何集成到编辑器
// 来源：MetaHumanFaceContourTrackerEditor 模块

// 1. 资产工厂 (AssetFactory)
// UMetaHumanFaceContourTrackerAssetFactoryNew 类继承自 UFactory，负责在编辑器中
// “新建资产”时创建 UMetaHumanFaceContourTrackerAsset 对象。
// 它是用户在内容浏览器中右键选择“MetaHuman > 面部轮廓追踪器”时触发创建的幕后类。
// 通常无需直接实例化，编辑器系统会自动调用。

// 2. 资产定义 (AssetDefinition)
// UAssetDefinition_MetaHumanFaceContourTracker 类继承自 UAssetDefinitionDefault，定义了
// 这种资产在内容浏览器中的显示名称、颜色、图标以及双击打开时的行为。
// 它负责将 UMetaHumanFaceContourTrackerAsset 类型的数据与编辑器UI关联起来。
```

### 进阶用法

如果你需要扩展或修改面部轮廓追踪资产的编辑器行为（例如，为其添加自定义的编辑器模式或面板），可以创建继承自 `UAssetDefinition_MetaHumanFaceContourTracker` 的子类，并覆盖 `OpenAssets` 方法来提供自定义的资产编辑器体验。

## Demo 示例

以下示例展示了如何创建一个自定义的资产定义类，该类可以关联到 `MetaHumanFaceContourTrackerEditor` 模块提供的基础资产。

```cpp
// MyCustomFaceContourTrackerEditor.h
#pragma once

#include “CoreMinimal.h”
#include “AssetDefinition_MetaHumanFaceContourTracker.h”
#include “MyCustomFaceContourTrackerEditor.generated.h”

UCLASS()
class UMyCustomFaceContourTrackerAssetDefinition : public UAssetDefinition_MetaHumanFaceContourTracker
{
	GENERATED_BODY()

public:
	// 覆盖资产显示名称
	virtual FText GetAssetDisplayName() const override;

	// 覆盖双击打开行为，指向自定义编辑器面板
	virtual EAssetCommandResult OpenAssets(const FAssetOpenArgs& InOpenArgs) const override;
};
```

```cpp
// MyCustomFaceContourTrackerEditor.cpp
#include “MyCustomFaceContourTrackerEditor.h”
#include “MetaHumanFaceContourTrackerAsset.h” // 假设的基础资产类头文件
#include “MyCustomFaceContourTrackerEditorStyle.h” // 你的自定义编辑器样式/面板

#define LOCTEXT_NAMESPACE “MyCustomFaceContourTrackerAssetDefinition”

FText UMyCustomFaceContourTrackerAssetDefinition::GetAssetDisplayName() const
{
	return LOCTEXT(“AssetDisplayName”, “Custom Face Contour Tracker”);
}

EAssetCommandResult UMyCustomFaceContourTrackerAssetDefinition::OpenAssets(const FAssetOpenArgs& InOpenArgs) const
{
	// 在这里创建并激活你的自定义编辑器面板，例如一个集成了自定义工具的 FaceContourTracker 编辑器。
	// for (UMetaHumanFaceContourTrackerAsset* Asset : InOpenArgs.LoadObjects<UMetaHumanFaceContourTrackerAsset>())
	// {
	// 	SMyCustomFaceContourTrackerEditor::Invoke(Asset);
	// }
	return EAssetCommandResult::Handled;
}

#undef LOCTEXT_NAMESPACE
```

## 模块依赖

`MetaHumanFaceContourTrackerEditor` 模块依赖于其运行时核心 `MetaHumanFaceContourTracker` 模块，并主要依赖于编辑器基础模块来实现资产系统的集成。

| 模块 | 用途 |
|---|---|
| `MetaHumanFaceContourTracker` | 提供面部轮廓追踪资产的运行时类 (`UMetaHumanFaceContourTrackerAsset`)。 |
| 无特殊依赖（仅标准 Slate/Editor 等模块） | 用于构建编辑器UI和资产系统集成。 |

## 维护状态

### 近期更新

最近的提交都围绕整个 MetaHuman Animator 插件进行改进，并未直接针对 `MetaHumanFaceContourTrackerEditor` 子模块。这表明该基础模块已处于稳定状态。

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用身体追踪时，禁用关卡序列导出功能。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复了在 MetaHuman 上的渲染瑕疵。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 启用身体追踪时，过滤掉可视化对象。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 为现有网格体导出动画序列。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复了 Sequencer 缓存问题。 |

### 维护评价

`MetaHumanFaceContourTrackerEditor` 作为 MetaHuman Animator 这一大型官方插件的组成部分，**处于活跃维护中**。从近期提交记录可见，其所属的整体插件正在被积极开发和修复问题（例如针对新特性、渲染问题和工作流优化）。该模块本身作为基础的资产类型集成代码，一旦稳定，更新频率会低于核心算法模块，但会随主插件一起接收必要的兼容性和维护性更新。**推荐使用**，它是官方工作流的一部分。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanFaceContourTrackerEditor)
- [官方文档](https://docs.unrealengine.com/en-US/Plugins/MetaHuman/) (待提供)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanFaceContourTrackerEditor/Tests) (路径可能包含测试文件)