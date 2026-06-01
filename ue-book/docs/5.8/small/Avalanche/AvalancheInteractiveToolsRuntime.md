# Motion Design

> Compositing, designer and broadcasting tool.

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、编辑器工具、示例） |
| 模块 | `Avalanche` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), `AvalancheMedia` (Runtime), `AvalancheOutliner` (Runtime), `AvalancheSequencer` (Runtime), `AvalancheText` (Runtime), `AvalancheShapes` (Runtime), `AvalancheMaterial` (Runtime), `AvalancheMask` (Runtime), `AvalancheEffectors` (Runtime), `AvalancheModifiers` (Runtime), `AvalanchePropertyAnimator` (Runtime), `AvalancheSceneTree` (Runtime), `AvalancheSequence` (Runtime), `AvalancheTransition` (Runtime), `AvalancheViewport` (Runtime), `AvalancheLevelViewport` (Runtime), `AvalancheInteractiveTools` (Runtime), `AvalancheInteractiveToolsRuntime` (Runtime), `AvalancheAttribute` (Runtime), `AvalancheCamera` (Runtime), `AvalancheComponentVisualizers` (Runtime), `AvalancheMRQ` (Runtime), `AvalancheRemoteControl` (Runtime), `AvalancheSceneRig` (Runtime), `AvalancheTag` (Runtime), `AvalancheFunctionalTest` (Runtime), `AvalancheEditorCore` (Runtime), `AvalancheAttributeEditor` (Runtime), `AvalancheEffectorsEditor` (Runtime), `AvalancheMRQEditor` (Runtime), `AvalancheMaskEditor` (Runtime), `AvalancheMediaEditor` (Runtime), `AvalancheModifiersEditor` (Runtime), `AvalanchePropertyAnimatorEditor` (Runtime), `AvalancheRemoteControlEditor` (Runtime), `AvalancheSVGEditor` (Runtime), `AvalancheSceneRigEditor` (Runtime), `AvalancheShapesEditor` (Runtime), `AvalancheTagEditor` (Runtime), `AvalancheTextEditor` (Runtime), `AvalancheTransitionEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Avalanche (Motion Design) 是一个功能完备的虚幻引擎原生虚拟制作（Virtual Production）工具链。它并非一个简单的单一工具，而是一套集成的编辑器扩展、运行时组件和自定义资产类型，旨在为电视广播、活动直播和虚拟摄影棚提供实时的动态图形设计、合成和播出控制能力。

核心解决的问题是：在虚幻引擎内，以非线性、可视化的方式，高效地创建、编辑和播放复杂的2D/3D动态图形序列（如节目包装、新闻图文、赛事计分板），并能与下游播出系统（如 CasparCG, Vizrt）集成。它填补了虚幻引擎在专业广播级动态图形制作领域的原生工具空白，让艺术家和设计师无需编写大量代码即可构建复杂的播出模板。

## 使用场景

- **电视图形包装 (TV Graphics Package)**：设计并制作新闻、体育、财经节目的动态字幕、Logo 演绎、数据可视化图表，并在直播中实时触发和播放。
- **虚拟摄影棚 (Virtual Studio)**：在虚拟场景中叠加交互式图文层，控制场景内物体的动画和过渡。
- **实时合成与合成**：将实拍画面与动态生成的图形元素进行实时合成。
- **直播图形控制 (Live Graphics Control)**：通过遥控（Remote Control）面板或集成系统，在播出时动态修改文本、图像、数据等内容。
- **动态数据驱动图形**：将实时数据（如比赛比分、股票行情）驱动图形动画。

## 蓝图用法

Motion Design 提供了大量蓝图可调用的接口和节点，用于控制图形序列的播放、修改属性等。以下为关键接口示例：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetModeDetailsObject` | 在交互式工具模式中，获取用于显示在“细节”面板中的自定义对象。允许工具模式提供专用的属性编辑界面。 | `IAvaInteractiveToolsModeDetailsObjectProvider` |

### 使用示例（蓝图描述）

1.  **创建一个自定义的交互式工具模式**：继承 `IAvaInteractiveToolsModeDetailsObjectProvider` 接口，并在 `GetModeDetailsObject` 函数的实现中，返回一个实现了 `IAvaInteractiveToolsModeDetailsObject` 接口的 UObject 实例。这个 UObject 上的 `UPROPERTY` 将自动显示在编辑器的细节面板中，当该工具模式激活时。
2.  **控制媒体播放**：使用 `AvalancheMedia` 模块提供的蓝图节点，加载、播放、暂停、停止图形序列（Sequence），并控制其中各个元素（Slot）的可见性、文本、材质等属性。
3.  **与 Remote Control 集成**：使用 `AvalancheRemoteControl` 模块提供的接口，将图形序列中的参数暴露到遥控面板，供直播操作员实时控制。

## C++ 用法

Motion Design 的架构深度集成到虚幻引擎中，扩展它通常需要继承其核心接口和类。

### 头文件引入

```cpp
#include "AvalancheInteractiveToolsRuntime/Public/IAvaInteractiveToolsModeDetailsObjectProvider.h"
#include "AvalancheInteractiveToolsRuntime/Public/IAvaInteractiveToolsModeDetailsObject.h"
```

### 基本用法

从 `AvalancheInteractiveToolsRuntime` 模块的公开接口看，其主要为编辑器交互工具提供扩展点。

**来源文件**: `Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheInteractiveToolsRuntime/Public/IAvaInteractiveToolsModeDetailsObjectProvider.h`

```cpp
// 实现一个提供详情对象的交互式工具模式
UCLASS()
class UMyCustomToolMode : public UInteractiveTool, public IAvaInteractiveToolsModeDetailsObjectProvider
{
    GENERATED_BODY()

public:
    // IAvaInteractiveToolsModeDetailsObjectProvider 接口实现
    virtual UObject* GetModeDetailsObject_Implementation() const override
    {
        // 返回一个包含此工具模式自定义属性的对象
        return MyDetailsObject;
    }

private:
    UPROPERTY()
    TObjectPtr<UMyToolModeDetails> MyDetailsObject;
};

// 定义详情对象类，实现标记接口
UCLASS()
class UMyToolModeDetails : public UObject, public IAvaInteractiveToolsModeDetailsObject
{
    GENERATED_BODY()

public:
    // 这个属性会显示在细节面板中
    UPROPERTY(EditAnywhere, Category = "My Tool")
    float SomeFloatParameter = 1.0f;

    UPROPERTY(EditAnywhere, Category = "My Tool")
    bool bSomeBoolFlag = false;
};
```

### 进阶用法

完整的 Motion Design 功能开发涉及对 `AvalancheCore`, `AvalancheMedia`, `AvalancheSequencer` 等多个模块的调用。通常，开发者会：
1.  **创建自定义资产类型**：如 `UAvaMediaAsset`，用于存储图形模板。
2.  **扩展编辑器界面**：通过继承 `AvalancheEditor` 模块中的类，为自定义资产添加专门的编辑器面板。
3.  **实现运行时逻辑**：在运行时组件中（如 `AAvaSequencePlayer`），驱动资产实例的播放和参数更新。

## Demo 示例

一个最小化的自定义交互式工具模式实现，展示如何提供详情对象。

```cpp
// MyCustomToolMode.h
#pragma once

#include "CoreMinimal.h"
#include "InteractiveTool.h"
#include "IAvaInteractiveToolsModeDetailsObjectProvider.h"
#include "MyCustomToolMode.generated.h"

UCLASS()
class UMyCustomToolModeDetails : public UObject, public IAvaInteractiveToolsModeDetailsObject
{
    GENERATED_BODY()
public:
    UPROPERTY(EditAnywhere, Category = "Demo")
    FVector Offset = FVector::ZeroVector;

    UPROPERTY(EditAnywhere, Category = "Demo")
    FColor TintColor = FColor::White;
};

UCLASS()
class UMyCustomToolMode : public UInteractiveTool, public IAvaInteractiveToolsModeDetailsObjectProvider
{
    GENERATED_BODY()

public:
    virtual void Setup() override;

    // 接口实现
    virtual UObject* GetModeDetailsObject_Implementation() const override;

private:
    UPROPERTY()
    TObjectPtr<UMyCustomToolModeDetails> Details;
};
```

```cpp
// MyCustomToolMode.cpp
#include "MyCustomToolMode.h"

void UMyCustomToolMode::Setup()
{
    UInteractiveTool::Setup();
    Details = NewObject<UMyCustomToolModeDetails>(this);
}

UObject* UMyCustomToolMode::GetModeDetailsObject_Implementation() const
{
    return Details;
}
```

## 模块依赖

使用 Motion Design 插件时，你的项目模块需要依赖以下核心模块（根据你要使用的功能）。

| 模块 | 用途 |
|---|---|
| `AvalancheCore` | Motion Design 的核心运行时逻辑、基础类型和组件。 |
| `AvalancheMedia` | 媒体资产（图形序列）的加载、播放和运行时控制。 |
| `AvalancheOutliner` | Motion Design 专用的大纲视图，用于组织场景中的图形元素。 |
| `AvalancheSequencer` | 与虚幻引擎序列器深度集成的通道和轨道，用于编辑图形动画。 |
| `AvalancheInteractiveTools` | 编辑器交互式工具框架，用于创建专用的图形设计工具（如笔刷、选框）。 |
| `AvalancheRemoteControl` | 提供将图形参数暴露到遥控面板的功能，用于实时播出控制。 |
| `AvalancheMRQ` | 与 Movie Render Queue 集成，用于高质量离线渲染动态图形。 |
| `Advanced Renamer` | 为资产和组件提供高级的批量重命名工具。 |
| `CustomDetailsView` | 支持创建自定义的细节面板视图，是许多 Motion Design 编辑器界面的基础。 |
| `Dynamic Material` | 动态材质实例管理工具，用于在编辑器中预览材质效果。 |
| `GeometryCache` | 几何体缓存资产的支持，用于导入和播放复杂的网格动画。 |
| `Geometry Scripting` | 几何体脚本操作支持。 |
| `Media Compositing` | 媒体合成相关功能。 |
| `Media IO Framework` | 媒体输入输出框架，与外部播出系统对接。 |
| `Mesh Modeling Toolset Exp` | 网格建模工具集，用于在 Motion Design 上下文中进行基础建模。 |
| `SVG Importer` | SVG 文件导入支持，用于导入矢量图形。 |
| `Text3D` | 3D 文本渲染组件支持。 |
| `ActorModifierCore` | Actor 修改器核心框架，是 Motion Design 中许多效果（克隆、变形）的基础。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将 Motion Design 的标签页（场景设置、大纲视图）移至编辑器自身的标签页组，优化布局。 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 为使用“节目单页面”设置时的 Movie Render Queue 增加了分析数据统计。 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 在节目控制工具栏中增加了页面加载选项（全部、下一个、已选），并增加了相关分析。 |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 增加项目设置，可强制禁用 Text3D 和形状组件的碰撞。 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构视口相关代码，在客户端关联/解除关联时发出通知，减少重复代码。 |

### 维护评价

- **创建时间**：2025年5月从 `Experimental` 迁移至 `VirtualProduction` 目录，标志着其从实验性项目晋级为官方支持的虚拟制作核心工具。
- **近期活跃度**：**非常活跃**。最近一次提交在2026年5月20日，近一周内有4次实质性功能更新和重构，表明 Epic 正在积极开发和迭代此功能。
- **维护状态**：**活跃维护**。这是一个 Epic Games 官方重点投资的虚拟制作管线核心组件，得到了持续的关注和资源投入。
- **已知限制**：作为一套庞大而复杂的工具链，学习曲线较陡峭。某些高级功能（如深度序列器集成、自定义播出协议）可能需要深入理解其内部架构。
- **推荐使用**：**强烈推荐**。对于从事电视广播、虚拟制作和实时图形包装的团队，这是虚幻引擎内最强大、最集成的原生解决方案。它处于积极开发中，功能不断完善。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/motion-design-in-unreal-engine) (Epic 官方 Motion Design 文档页面)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheFunctionalTest)