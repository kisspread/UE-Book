# Motion Design

> Compositing, designer and broadcasting tool.
> Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产，编辑器工具，运行时组件） |
| 模块 | `Avalanche` (Runtime), `AvalancheAttribute` (Runtime), `AvalancheAttributeEditor` (Runtime), `AvalancheCamera` (Runtime), `AvalancheComponentVisualizers` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), `AvalancheEditorCore` (Runtime), `AvalancheEffectors` (Runtime), `AvalancheEffectorsEditor` (Runtime), `AvalancheFunctionalTest` (Runtime), `AvalancheInteractiveTools` (Runtime), `AvalancheInteractiveToolsRuntime` (Runtime), `AvalancheLevelViewport` (Runtime), `AvalancheMRQ` (Runtime), `AvalancheMRQEditor` (Runtime), `AvalancheMask` (Runtime), `AvalancheMaskEditor` (Runtime), `AvalancheMaterial` (Runtime), `AvalancheMedia` (Runtime), `AvalancheMediaEditor` (Runtime), `AvalancheModifiers` (Runtime), `AvalancheModifiersEditor` (Runtime), `AvalancheOutliner` (Runtime), `AvalanchePropertyAnimator` (Runtime), `AvalanchePropertyAnimatorEditor` (Runtime), `AvalancheRemoteControl` (Runtime), `AvalancheRemoteControlEditor` (Runtime), `AvalancheSVGEditor` (Runtime), `AvalancheSceneRig` (Runtime), `AvalancheSceneRigEditor` (Runtime), `AvalancheSceneTree` (Runtime), `AvalancheSequence` (Runtime), `AvalancheSequencer` (Runtime), `AvalancheShapes` (Runtime), `AvalancheShapesEditor` (Runtime), `AvalancheTag` (Runtime), `AvalancheTagEditor` (Runtime), `AvalancheText` (Runtime), `AvalancheTextEditor` (Runtime), `AvalancheTransition` (Runtime), `AvalancheTransitionEditor` (Runtime), `AvalancheViewport` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-02-27 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Avalanche（Motion Design）插件是一个为虚拟制片（Virtual Production）和广播领域设计的综合性图形设计与合成工具链。它并非一个单一功能的插件，而是一个庞大的插件生态系统，旨在让UE5成为一个强大的实时运动图形（Motion Graphics）创作平台。其核心功能包括：
1.  **动态场景构建**：提供了“场景树（Scene Tree）”和“场景装置（Scene Rig）”等概念，用于组织和控制复杂的动态场景元素。
2.  **丰富的几何与材质工具**：包含矢量图形（SVG）、3D文字、基础形状、几何缓存（Geometry Cache）和动态材质（Dynamic Material）的创建与编辑工具。
3.  **动画与特效系统**：集成了克隆/效应器（Cloner/Effector）系统、属性动画器（Property Animator）和过渡逻辑（Transition Logic）系统，用于创建复杂的程序化动画和状态驱动动画。
4.  **媒体集成与输出**：支持媒体合成、媒体IO框架，以及与媒体渲染队列（MRQ）的集成，便于输出高质量的视频序列或进行实时广播。
5.  **编辑器扩展**：提供了高度定制化的编辑器视口、大纲视图、工具栏和自定义细节面板，为动态设计工作流打造专属的编辑环境。

简单来说，它解决的是“如何在UE中像在After Effects或C4D中一样高效地创作广播级动态图形”这一问题，将UE5强大的3D渲染引擎与专业的动态设计工作流相结合。

## 使用场景

-   **电视与广播图形**：为新闻、体育、天气等节目制作实时的动态标题、下三分之一、图表和虚拟场景。
-   **虚拟制片**：在LED墙或绿幕前，创建和控制需要实时变化的动态背景、信息图表或虚拟产品展示。
-   **现场活动与音乐会**：设计并驱动现场大屏幕上的动态视觉内容，如歌手名字、歌词特效、实时数据可视化。
-   **企业演示与发布会**：制作高品质的产品发布动画、技术演示图形和动态信息图。
-   **需要程序化动画的场景**：利用克隆/效应器系统制作大量物体的规律运动（如人群、矩阵特效），或使用过渡逻辑实现复杂的UI/UX状态机动画。

## 蓝图用法

由于Avalanche插件体系庞大，其蓝图API分散在众多子模块中。`AvalancheTransitionEditor` 模块主要提供编辑器侧的过渡树逻辑。更广泛和运行时的蓝图用法可通过其核心接口和资产进行访问。

### 核心接口

通过模块接口访问过渡树编辑功能。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get()` | 获取Avalanche过渡逻辑编辑器模块的单例引用。 | `IAvaTransitionEditorModule` |
| `GetOnBuildDefaultTransitionTree()` | 获取用于构建默认过渡树的委托，可用于自定义初始化行为。 | `IAvaTransitionEditorModule` |

### 使用示例（蓝图描述）

虽然过渡树的编辑主要在专用编辑器中进行，但通过蓝图可以触发其相关逻辑。例如，在蓝图中你可能需要：
1.  获取 `IAvaTransitionEditorModule` 接口。
2.  调用 `GetOnBuildDefaultTransitionTree()` 获取委托，并绑定一个自定义函数，当系统需要创建新的默认过渡树时，你的自定义逻辑会被调用，从而可以注入自己的状态或任务。

## C++ 用法

### 头文件引入

使用 `AvalancheTransitionEditor` 模块的功能需要引入其公共接口头文件。

```cpp
#include "IAvaTransitionEditorModule.h"
```

### 基本用法

访问过渡逻辑编辑器模块并查询其功能。
*(来源：Public/IAvaTransitionEditorModule.h)*

```cpp
// 检查模块是否已加载
if (IAvaTransitionEditorModule::IsLoaded())
{
    // 获取模块引用
    IAvaTransitionEditorModule& TransitionEditorModule = IAvaTransitionEditorModule::Get();

    // 绑定一个自定义函数来修改默认的过渡树构建过程
    TransitionEditorModule.GetOnBuildDefaultTransitionTree().BindLambda([](UAvaTransitionTreeEditorData& EditorData)
    {
        // 在此自定义默认过渡树的内容
        // 例如：添加自定义状态或修改初始状态
        UE_LOG(LogTemp, Log, TEXT("Customizing default transition tree..."));
    });
}
```

### 进阶用法

结合 `AvalancheTransition` 和 `AvalancheTransitionEditor` 模块，在C++中程序化地创建和编辑过渡树数据。
*(综合自 Public/AvaTransitionTreeEditorData.h 和 Private/Compiler/AvaTransitionCompiler.h)*

```cpp
// 1. 创建一个新的过渡树编辑器数据对象（通常作为资产存在）
UAvaTransitionTreeEditorData* EditorData = NewObject<UAvaTransitionTreeEditorData>();

// 2. 向编辑器数据中添加状态（UStateTreeState是底层状态树结构）
UStateTreeState& RootState = EditorData->CreateState(/* InSiblingState */, /* bInAfter */);
RootState.SetName(FText::FromString(TEXT("Root State")));

// 3. 使用编译器验证和编译树（编译器通常由编辑器内部管理）
// FAvaTransitionCompiler Compiler;
// Compiler.SetTransitionTree(TransitionTree);
// bool bSuccess = Compiler.Compile(EAvaTransitionEditorMode::Default);

// 4. 获取状态的元数据（如颜色等）
const FAvaTransitionStateMetadata* Metadata = EditorData->FindStateMetadata(RootState.GetID());
if (Metadata)
{
    FSlateColor StateColor = Metadata->Color;
}
```

## Demo 示例

一个最小的 C++ 示例，展示如何从模块接口开始，与过渡树系统交互。

**头文件 (MyTransitionHelper.h):**
```cpp
#pragma once

#include "CoreMinimal.h"

class UStateTreeState;
class UAvaTransitionTreeEditorData;

class FMyTransitionHelper
{
public:
    /** 尝试创建一个简单的过渡树编辑器数据 */
    static UAvaTransitionTreeEditorData* CreateSimpleTransitionTree();
};
```

**源文件 (MyTransitionHelper.cpp):**
```cpp
#include "MyTransitionHelper.h"
#include "IAvaTransitionEditorModule.h"
#include "AvaTransitionTreeEditorData.h"

UAvaTransitionTreeEditorData* FMyTransitionHelper::CreateSimpleTransitionTree()
{
    // 确保模块可用
    if (!IAvaTransitionEditorModule::IsLoaded())
    {
        return nullptr;
    }

    // 创建编辑器数据资产
    UAvaTransitionTreeEditorData* EditorData = NewObject<UAvaTransitionTreeEditorData>();
    if (EditorData)
    {
        // 创建第一个状态
        UStateTreeState& FirstState = EditorData->CreateState(*EditorData->GetRootState(), true);
        FirstState.SetName(FText::FromString(TEXT("Initial State")));
        FirstState.SetColor(FLinearColor::Green);

        // 此时，`EditorData` 已经是一个包含基本状态的过渡树数据。
        // 你可以将其保存为资产，或进一步添加任务（Tasks）和条件（Conditions）。
    }
    return EditorData;
}
```

## 模块依赖

要使用 `AvalancheTransitionEditor` 模块，你的模块需要在 `.Build.cs` 中添加对它的依赖。根据插件描述和代码结构，以下是关键且非通用的依赖模块。

| 模块 | 用途 |
|---|---|
| `AvalancheTransition` | 提供过渡逻辑的运行时数据和行为接口 (`IAvaTransitionBehavior`)。 |
| `AvalancheCore` | 提供Avalanche插件的核心类型、工具函数和接口（如`IAvaTypeCastable`）。 |
| `StateTree` | 底层状态树框架，是Avalanche过渡逻辑系统的基础。 |
| `StateTreeEditorModule` | 提供状态树编辑器的基础支持和数据结构 (`UStateTreeEditorData`)。 |
| `Sequencer` | 用于属性动画器 (`AvalanchePropertyAnimator`) 与Sequencer时间轴的集成。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own group | 将Motion Design的编辑器标签页（场景设置、大纲视图）归入独立分组，优化UI组织。 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 在使用“节目单页面”设置时增加了MRQ（媒体渲染队列）的分析功能。 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and added... | 在节目控制工具栏中增加了页面加载选项（全部、下一个、选中项），并添加了相关功能。 |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 新增项目设置，可以强制禁用3D文字和形状的碰撞。 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated with viewport. | 视口：通过在客户端关联或取消关联时发出通知，来规范必要的代码复制。 |

### 维护评价

Avalanche (Motion Design) 是一个 **活跃维护** 中的插件。
-   **活跃度**：从git日志看，直至2026年5月仍有频繁的功能性更新和优化，涉及编辑器UI、MRQ集成、新功能添加等。
-   **成熟度**：该插件从早期实验性插件（ActorModifier, ClonerEffector等）整合发展而来，现已迁移至 `VirtualProduction` 目录，表明其被视为生产就绪的核心虚拟制片工具。
-   **完整性**：插件体系庞大，模块化程度高，包含了从底层数据、运行时逻辑到高级编辑器的完整工具链。
-   **推荐度**：**强烈推荐**用于任何需要专业级实时运动图形和广播图形工作流的虚拟制片项目。由于其复杂性和庞大的依赖关系，建议通过官方学习资源和示例项目入手。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [官方文档](*请补充 Epic 官方文档链接，如果存在*)