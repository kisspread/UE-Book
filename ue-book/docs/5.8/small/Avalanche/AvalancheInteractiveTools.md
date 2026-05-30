# Motion Design

> Compositing, designer and broadcasting tool.
>
> Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器工具、交互工具、材质系统、场景管理、媒体合成等） |
| 模块 | `Avalanche` (Runtime), `AvalancheAttribute` (Runtime), `AvalancheAttributeEditor` (Runtime), `AvalancheCamera` (Runtime), `AvalancheComponentVisualizers` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), `AvalancheEditorCore` (Runtime), `AvalancheEffectors` (Runtime), `AvalancheEffectorsEditor` (Runtime), `AvalancheFunctionalTest` (Runtime), `AvalancheInteractiveTools` (Runtime), `AvalancheInteractiveToolsRuntime` (Runtime), `AvalancheLevelViewport` (Runtime), `AvalancheMRQ` (Runtime), `AvalancheMRQEditor` (Runtime), `AvalancheMask` (Runtime), `AvalancheMaskEditor` (Runtime), `AvalancheMaterial` (Runtime), `AvalancheMedia` (Runtime), `AvalancheMediaEditor` (Runtime), `AvalancheModifiers` (Runtime), `AvalancheModifiersEditor` (Runtime), `AvalancheOutliner` (Runtime), `AvalanchePropertyAnimator` (Runtime), `AvalanchePropertyAnimatorEditor` (Runtime), `AvalancheRemoteControl` (Runtime), `AvalancheRemoteControlEditor` (Runtime), `AvalancheSVGEditor` (Runtime), `AvalancheSceneRig` (Runtime), `AvalancheSceneRigEditor` (Runtime), `AvalancheSceneTree` (Runtime), `AvalancheSequence` (Runtime), `AvalancheSequencer` (Runtime), `AvalancheShapes` (Runtime), `AvalancheShapesEditor` (Runtime), `AvalancheTag` (Runtime), `AvalancheTagEditor` (Runtime), `AvalancheText` (Runtime), `AvalancheTextEditor` (Runtime), `AvalancheTransition` (Runtime), `AvalancheTransitionEditor` (Runtime), `AvalancheViewport` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Motion Design 是 UE5 中面向虚拟制作的综合动态图形设计工具。它并非简单的某个功能插件，而是一个完整的**动态设计工作台**，整合了合成（Compositing）、设计师工具（Designer）和广播（Broadcasting）三大能力。

该插件从原来的 Experimental 目录迁移至 VirtualProduction，表明 Epic 认为它已达到生产可用级别。它基于 UE 的 InteractiveTools 框架构建了一套完整的交互式编辑模式（Editor Mode），允许用户在视口中直观地创建和操控 2D/3D 元素（文字、形状、克隆体、效果器等），同时集成了材质设计、场景管理、远程控制、媒体 I/O、MRQ 渲染队列、Sequencer 时间轴等功能。

**核心解决的问题**：为虚拟制作场景中的动态图形设计提供端到端的工作流，从设计、动画到播出。

## 使用场景

- 你在为虚拟制作场景设计 LED 墙上的动态图形 → 用 Motion Design
- 你需要在视口中交互式地创建 2D/3D 元素（文字、形状、SVG）并实时预览 → 用 Motion Design 的交互工具模式
- 你需要将克隆体（Cloner）和效果器（Effector）用于动态图形动画 → 用 Motion Design
- 你需要通过远程控制（Remote Control）实时调整场景参数 → 用 Motion Design
- 你需要将动态设计项目通过 MRQ 输出为视频 → 用 Motion Design

## 交互工具模式（AvalancheInteractiveTools 模块）

该模块为 Motion Design 提供了自定义编辑器模式（Editor Mode），是整个插件的交互入口。

### 模块架构

```
AvalancheInteractiveTools
├── Editor Mode (UAvaInteractiveToolsEdMode)
├── Tools
│   ├── UAvaInteractiveToolsToolBase          ← 所有工具基类
│   ├── UAvaInteractiveToolsActorToolBase     ← Actor 生成工具基类
│   ├── UAvaInteractiveToolsActorAreaToolBase ← 区域型 Actor 生成工具
│   ├── UAvaInteractiveToolsActorPointToolBase← 点击型 Actor 生成工具
│   ├── UAvaInteractiveToolsStaticMeshActorTool ← 静态网格生成工具
│   └── UAvaInteractiveToolsActorToolNull / Spline ← 内置具体工具
├── Builders
│   ├── UAvaInteractiveToolsToolBuilder
│   ├── UAvaInteractiveToolsActorToolBuilder
│   └── UAvaInteractiveToolsStaticMeshActorToolBuilder
├── Planners (视口交互规划器)
│   ├── UAvaInteractiveToolsToolViewportPlanner
│   ├── UAvaInteractiveToolsToolViewportPointPlanner
│   ├── UAvaInteractiveToolsToolViewportAreaPlanner
│   └── UAvaInteractiveToolsToolViewportPointListPlanner
├── Behaviors
│   └── UAvaSingleClickAndDragBehavior
└── Settings
    └── UAvaInteractiveToolsSettings
```

### 工具类别

模块预定义了五个工具类别：

| 类别 | 常量名 | 用途 |
|---|---|---|
| 2D 工具 | `CategoryName2D` | 2D 元素创建 |
| 3D 工具 | `CategoryName3D` | 3D 元素创建 |
| Actor 工具 | `CategoryNameActor` | Actor 放置 |
| 克隆体工具 | `CategoryNameCloner` | 克隆体效果 |
| 效果器工具 | `CategoryNameEffector` | 效果器效果 |

## 蓝图用法

该模块主要面向 C++ 扩展，Blueprint API 较少。以下是从源码中提取的关键蓝图可访问接口：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `UAvaInteractiveToolsToolViewportPlanner` | 可蓝图化的视口规划器基类 | `UAvaInteractiveToolsToolViewportPlanner` |
| `UAvaInteractiveToolsToolViewportPointPlanner` | 单点规划器（蓝图可继承） | `UAvaInteractiveToolsToolViewportPointPlanner` |
| `UAvaInteractiveToolsToolViewportAreaPlanner` | 区域规划器（蓝图可继承） | `UAvaInteractiveToolsToolViewportAreaPlanner` |
| `UAvaInteractiveToolsToolViewportPointListPlanner` | 多点规划器（蓝图可继承） | `UAvaInteractiveToolsToolViewportPointListPlanner` |

### 设置（蓝图/编辑器可配置）

通过 `Editor > Project Settings > Plugins > Interactive Tools` 访问：

| 设置 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `CameraDistance` | float | 500.0 | Actor 创建时与摄像机的距离 |
| `DefaultActionActorAlignment` | enum | Axis | 默认动作对齐方式（轴/摄像机） |
| `ViewportToolbarPosition` | enum | Bottom | 视口工具栏位置 |
| `bViewportToolbarLabelEnabled` | bool | false | 是否显示工具栏标签 |

## C++ 用法

### 头文件引入

```cpp
#include "IAvalancheInteractiveToolsModule.h"
#include "Tools/AvaInteractiveToolsToolBase.h"
#include "Builders/AvaInteractiveToolsActorToolBuilder.h"
#include "Planners/AvaInteractiveToolsToolViewportPlanner.h"
```

### 注册自定义工具类别

通过模块接口注册新的工具类别和工具：

```cpp
// 注册类别
IAvalancheInteractiveToolsModule& AITModule = IAvalancheInteractiveToolsModule::Get();
AITModule.RegisterCategory(
    FName("MyCustomCategory"),
    MyCategoryCommand,
    /* PlacementModeSortPriority */ 5
);

// 注册工具
FAvaInteractiveToolsToolParameters ToolParams;
ToolParams.UICommand = MyToolCommand;
ToolParams.ToolIdentifier = TEXT("MyTool_UniqueId");
ToolParams.Priority = 0;
ToolParams.CreateBuilder = [](UEdMode* InEdMode) -> UInteractiveToolBuilder*
{
    return UAvaInteractiveToolsActorToolBuilder::CreateActorToolBuilder(
        InEdMode,
        FName("MyCustomCategory"),
        MyToolCommand,
        TEXT("MyTool_UniqueId"),
        0,
        AMyActor::StaticClass()
    );
};
AITModule.RegisterTool(FName("MyCustomCategory"), MoveTemp(ToolParams));
```

### 创建自定义 Actor 生成工具

基于 `UAvaInteractiveToolsActorToolBase` 创建自定义工具：

```cpp
// MyTool.h
UCLASS()
class UMyCustomActorTool : public UAvaInteractiveToolsActorTool
{
    GENERATED_BODY()

public:
    virtual void OnRegisterTool(IAvalancheInteractiveToolsModule* InAITModule) override;

protected:
    virtual bool UseIdentityRotation() const override { return false; }
};

// MyTool.cpp
void UMyCustomActorTool::OnRegisterTool(IAvalancheInteractiveToolsModule* InAITModule)
{
    // 通过 Builder 注册
    FAvaInteractiveToolsToolParameters Params = 
        UAvaInteractiveToolsActorToolBuilder::CreateToolParameters<AMyActor>(
            IAvalancheInteractiveToolsModule::CategoryNameActor,
            MyCommand,
            TEXT("MyTool"),
            0
        );
    InAITModule->RegisterTool(IAvalancheInteractiveToolsModule::CategoryNameActor, MoveTemp(Params));
}
```

### 使用静态网格工具

通过 `UAvaInteractiveToolsStaticMeshActorToolBuilder` 创建基于静态网格的放置工具：

```cpp
auto* Builder = UAvaInteractiveToolsStaticMeshActorToolBuilder::CreateStaticMeshActorToolBuilder(
    InEdMode,
    IAvalancheInteractiveToolsModule::CategoryName3D,
    MyCommand,
    TEXT("MyMeshTool"),
    0,
    TEXT("/Game/Meshes/MyMesh")  // 静态网格路径
);
```

### 监听工具激活/停用事件

```cpp
IAvalancheInteractiveToolsModule& AITModule = IAvalancheInteractiveToolsModule::Get();

AITModule.OnToolActivation().AddLambda([](const FString& ToolIdentifier)
{
    UE_LOG(LogTemp, Log, TEXT("Tool activated: %s"), *ToolIdentifier);
});

AITModule.OnToolDeactivation().AddLambda([](const FString& ToolIdentifier)
{
    UE_LOG(LogTemp, Log, TEXT("Tool deactivated: %s"), *ToolIdentifier);
});
```

### 视口位置转世界坐标

工具基类提供了视口到世界的坐标转换：

```cpp
// 在自定义工具中
UWorld* World = nullptr;
FVector Position;
FRotator Rotation;

FVector2f ViewportPos(500.f, 300.f);
bool bSuccess = ViewportPositionToWorldPositionAndOrientation(
    EAvaViewportStatus::Focused,
    ViewportPos,
    1000.f,  // 距摄像机距离
    World,
    Position,
    Rotation
);
```

### 使用 Viewport Planner 进行交互式输入

Viewport Planner 封装了视口中的用户交互流程（点击、拖拽、区域选择）：

```cpp
// 在工具子类中使用 AreaPlanner
void UMyAreaTool::Setup()
{
    Super::Setup();
    ViewportPlannerClass = UAvaInteractiveToolsToolViewportAreaPlanner::StaticClass();
}

void UMyAreaTool::OnViewportPlannerComplete()
{
    auto* AreaPlanner = Cast<UAvaInteractiveToolsToolViewportAreaPlanner>(ViewportPlanner);
    if (AreaPlanner)
    {
        FVector WorldStart = AreaPlanner->GetStartPositionWorld();
        FVector WorldEnd = AreaPlanner->GetEndPositionWorld();
        FVector WorldSize = AreaPlanner->GetWorldSize();
        // 使用这些坐标创建或调整 Actor
    }
}
```

## Demo 示例

### 自定义工具完整示例

```cpp
// MyCustomAvaTool.h
#pragma once

#include "Tools/AvaInteractiveToolsActorToolBase.h"
#include "MyCustomAvaTool.generated.h"

UCLASS()
class MYMODULE_API UMyCustomAvaTool : public UAvaInteractiveToolsActorToolBase
{
    GENERATED_BODY()

public:
    UMyCustomAvaTool();

    virtual void OnRegisterTool(IAvalancheInteractiveToolsModule* InAITModule) override;

protected:
    virtual bool UseIdentityRotation() const override { return false; }
    virtual void OnActorSpawned(AActor* InActor) override;
    virtual void OnViewportPlannerComplete() override;
};
```

```cpp
// MyCustomAvaTool.cpp
#include "MyCustomAvaTool.h"
#include "IAvalancheInteractiveToolsModule.h"
#include "Builders/AvaInteractiveToolsActorToolBuilder.h"
#include "GameFramework/Actor.h"

UMyCustomAvaTool::UMyCustomAvaTool()
{
    ActorClass = AMyCustomActor::StaticClass();
}

void UMyCustomAvaTool::OnRegisterTool(IAvalancheInteractiveToolsModule* InAITModule)
{
    // 注册到 Actor 类别
    FAvaInteractiveToolsToolParameters Params = 
        UAvaInteractiveToolsActorToolBuilder::CreateToolParameters<AMyCustomActor>(
            IAvalancheInteractiveToolsModule::CategoryNameActor,
            nullptr,  // UICommand 可后续绑定
            TEXT("MyCustomAvaTool"),
            10
        );
    InAITModule->RegisterTool(
        IAvalancheInteractiveToolsModule::CategoryNameActor, 
        MoveTemp(Params)
    );
}

void UMyCustomAvaTool::OnActorSpawned(AActor* InActor)
{
    Super::OnActorSpawned(InActor);
    // Actor 生成后的自定义初始化逻辑
    if (InActor)
    {
        // 例如设置默认属性
    }
}

void UMyCustomAvaTool::OnViewportPlannerComplete()
{
    Super::OnViewportPlannerComplete();
    // 用户完成交互后的处理逻辑
    if (SpawnedActor)
    {
        // 根据视口规划器的位置调整 Actor
    }
}
```

## 模块依赖

`AvalancheInteractiveTools` 模块的 Build.cs 依赖关系：

| 模块 | 用途 |
|---|---|
| `InteractiveToolsFramework` | UE 交互工具框架基础 |
| `AvalancheCore` | Motion Design 核心功能 |
| `AvalancheEditorCore` | 编辑器核心支持 |

整体插件的特殊依赖（来自 .uplugin 描述）：

| 模块 | 用途 |
|---|---|
| `AdvancedRenamer` | 高级重命名功能 |
| `CustomDetailsView` | 自定义细节面板视图 |
| `DynamicMaterial` | 动态材质系统 |
| `GeometryCache` | 几何缓存 |
| `GeometryScripting` | 几何脚本 |
| `MediaCompositing` | 媒体合成 |
| `MediaIOFramework` | 媒体 I/O 框架 |
| `MeshModelingToolsetExp` | 网格建模工具集（实验性） |
| `RemoteControl` | 远程控制 |
| `SVGImporter` | SVG 导入器 |
| `Text3D` | 3D 文字 |
| `ActorModifierCore` | Actor 修改器核心 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将场景设置和大纲视图标签页移至独立分组 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 使用 Rundown 页面设置时新增 MRQ 分析统计 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 为节目控制工具栏添加页面加载选项（全部、下一个、选中） |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 新增项目设置以强制禁用 Text3D 和形状的碰撞 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构视口客户端关联/解除关联的通知机制 |

### 维护评价

**活跃维护** ⭐⭐⭐⭐⭐

- **创建时间**：2025-05-09，非常年轻的插件（不到 1 年）
- **更新频率**：最近一周内有 5 次提交，处于高频迭代期
- **代码规模**：2060 个源文件、42 个模块，是 UE5 中规模最大的插件之一
- **开发状态**：从 Experimental 迁移至 VirtualProduction，已正式进入生产状态
- **维护团队**：Epic Games 官方维护
- **近期改动方向**：UI 布局优化、MRQ 集成增强、节目控制功能完善、碰撞系统改进

这是一个处于**快速迭代**阶段的官方插件，功能持续增加中。推荐在虚拟制作项目中使用，但需注意 API 可能随版本更新而变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheFunctionalTest)