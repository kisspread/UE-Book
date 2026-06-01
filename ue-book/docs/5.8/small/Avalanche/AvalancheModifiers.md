# Motion Design

> Compositing, designer and broadcasting tool.
Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（大量Modifier组件、工具类、测试框架） |
| 模块 | `Avalanche` (Runtime), `AvalancheAttribute` (Runtime), `AvalancheAttributeEditor` (Runtime), `AvalancheCamera` (Runtime), `AvalancheComponentVisualizers` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), `AvalancheEditorCore` (Runtime), `AvalancheEffectors` (Runtime), `AvalancheEffectorsEditor` (Runtime), `AvalancheFunctionalTest` (Runtime), `AvalancheInteractiveTools` (Runtime), `AvalancheInteractiveToolsRuntime` (Runtime), `AvalancheLevelViewport` (Runtime), `AvalancheMRQ` (Runtime), `AvalancheMRQEditor` (Runtime), `AvalancheMask` (Runtime), `AvalancheMaskEditor` (Runtime), `AvalancheMaterial` (Runtime), `AvalancheMedia` (Runtime), `AvalancheMediaEditor` (Runtime), `AvalancheModifiers` (Runtime), `AvalancheModifiersEditor` (Runtime), `AvalancheOutliner` (Runtime), `AvalanchePropertyAnimator` (Runtime), `AvalanchePropertyAnimatorEditor` (Runtime), `AvalancheRemoteControl` (Runtime), `AvalancheRemoteControlEditor` (Runtime), `AvalancheSVGEditor` (Runtime), `AvalancheSceneRig` (Runtime), `AvalancheSceneRigEditor` (Runtime), `AvalancheSceneTree` (Runtime), `AvalancheSequence` (Runtime), `AvalancheSequencer` (Runtime), `AvalancheShapes` (Runtime), `AvalancheShapesEditor` (Runtime), `AvalancheTag` (Runtime), `AvalancheTagEditor` (Runtime), `AvalancheText` (Runtime), `AvalancheTextEditor` (Runtime), `AvalancheTransition` (Runtime), `AvalancheTransitionEditor` (Runtime), `AvalancheViewport` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Avalanche 插件（内部代号 Motion Design）是一个为虚拟制作和广播场景构建的强大、动态的设计师与合成工具集。它解决的核心问题是：在电视直播、体育赛事、演唱会等实时图形制作中，需要快速创建、编辑和动画化复杂的2D/3D画面元素，同时保持非破坏性工作流程和高实时性能。

插件提供了一个基于“Modifier（修改器）”栈的架构。用户可以将各种功能（如几何体修改、材质控制、阵列布局、可见性逻辑等）以堆栈形式应用到 Actor 上，程序化地改变其几何形状、材质、变换和渲染属性。这使得创建复杂的动态效果（如沿样条线扫描的几何体、参数化材质动画、自适应背景等）变得高效且可逆。

## 使用场景

- **电视与广播图形**：你需要为一场体育直播设计动态的比分板、选手介绍卡和广告板。使用 Motion Design 的 Modifier 栈，你可以快速创建形状、排列布局（Pattern）、添加材质效果，并轻松调整以适应不同画面。
- **虚拟演唱会与舞台设计**：你需要设计一个会随着音乐节奏变化的舞台背景。可以使用 `AvaPatternModifier`（阵列复制）创建粒子效果，用 `AvaSplineSweepModifier`（样条线扫描）制作流动的灯光轨迹。
- **产品可视化**：你需要展示一款产品，要求不同颜色和材质。使用 `AvaMaterialParameterModifier` 可以程序化地控制材质参数，实现一键换色。
- **动态UI与HUD**：你需要一个自适应的UI背景，当文本内容变化时能自动调整大小。`AvaAutoSizeModifier` 和 `AvaVisibilityModifier` 可以轻松实现这一需求。
- **程序化内容生成**：你需要创建大量有细微差别的物体。利用 `AvaPatternModifier` 的网格、圆形、直线布局工具，可以快速生成规则排列的物体阵列。

## 蓝图用法

Motion Design 的功能主要通过向 Actor 添加组件或修改器栈来使用。核心的 `BlueprintCallable` 函数分布在各个 `Modifier` 类中，用于动态控制修改器的行为。

### 核心节点

#### 几何体修改
| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetExtrudeMode` | 设置挤出模式（对称/前/后） | `UAvaExtrudeModifier` |
| `SetDepth` | 设置挤出深度 | `UAvaExtrudeModifier` |
| `SetBendPosition` | 设置弯曲位置 | `UAvaBendModifier` |
| `SetAngle` | 设置弯曲角度 | `UAvaBendModifier` |
| `SetMirrorFramePosition` | 设置镜像平面的位置 | `UAvaMirrorModifier` |
| `SetSourceActor` | 设置动态网格转换器的源Actor | `UAvaDynamicMeshConverterModifier` |

#### 材质与渲染
| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetMaterialParameters` | 设置材质参数映射（标量、向量、纹理） | `UAvaMaterialParameterModifier` |
| `SetGlobalOpacity` | 设置全局透明度（影响所有材质实例） | `UAvaGlobalOpacityModifier` |
| `SetMode` | 设置半透明排序优先级模式（手动/相机距离/大纲树） | `UAvaTranslucentPriorityModifier` |

#### 布局与排列
| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetLineCount` | 设置阵列复制的直线数量 | `UAvaPatternModifierLineTool` |
| `SetGridCountX` | 设置网格阵列的列数 | `UAvaPatternModifierGridTool` |
| `SetCircleRadius` | 设置圆形阵列的半径 | `UAvaPatternModifierCircleTool` |
| `SetFitMode` | 设置自适应大小模式（宽高/仅宽/仅高） | `UAvaAutoSizeModifier` |
| `SetReferenceActor` | 设置自适应大小的参考Actor | `UAvaAutoSizeModifier` |

#### 可见性与逻辑
| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetIndex` | 设置可见性控制的子物体索引 | `UAvaVisibilityModifier` |
| `SetTreatAsRange` | 将索引视为范围（显示0到Index） | `UAvaVisibilityModifier` |
| `SetContainerActor` | 设置空文本时隐藏的容器Actor | `UAvaHideEmptyModifier` |

### 使用示例（蓝图描述）

1.  **创建一个带挤出效果的3D文字**：
    - 在场景中放置一个 `Text3D` Actor。
    - 向其添加一个 `AvaExtrudeModifier` 组件。
    - 在 `AvaExtrudeModifier` 的细节面板中，设置 `Extrude Depth` 为 50，`Extrude Mode` 为 `Symmetrical`。文字将立即变为3D实体。

2.  **让一个形状自动适配另一个形状的大小**：
    - 放置两个 `AvaShape` Actor，一个作为目标，一个作为背景。
    - 在背景 Actor 上添加 `AvaAutoSizeModifier`。
    - 将 `Reference Actor` 属性设置为目标形状 Actor。
    - 设置 `Fit Mode` 为 `WidthAndHeight`。背景会自动调整大小以包裹目标，并可设置边距。

3.  **创建沿圆形排列的物体**：
    - 放置一个作为模板的 `AvaShape` Actor。
    - 向其添加 `AvaPatternModifier`。
    - 在 `Active Tool Class` 中选择 `AvaPatternModifierCircleTool`。
    - 在出现的圆形工具设置中，设置 `Circle Count` 为 8，`Circle Radius` 为 200。原物体将被复制并环绕中心点排列。

## C++ 用法

Motion Design 的 Modifier 系统基于 `UActorModifierCoreBase`。在 C++ 中，通常需要获取或创建 Actor 的 `UActorModifierCoreStack` 组件，然后向其中插入特定的 Modifier 实例。

### 头文件引入

```cpp
#include "Modifiers/AvaExtrudeModifier.h"
// 或其他具体 Modifier 的头文件，如 AvaBendModifier.h, AvaPatternModifier.h
#include "Components/ActorModifierCoreStack.h"
```

### 基本用法

向一个 Actor 添加挤出修改器并设置参数。

```cpp
// 假设你有一个 AActor* MyActor
UActorModifierCoreStack* ModifierStack = MyActor->FindComponentByClass<UActorModifierCoreStack>();
if (!ModifierStack)
{
    // 如果不存在，可能需要创建，具体取决于你的 Actor 类型和设置
    ModifierStack = NewObject<UActorModifierCoreStack>(MyActor);
    MyActor->AddInstanceComponent(ModifierStack);
    ModifierStack->RegisterComponent();
}

// 创建挤出修改器的插入操作
FActorModifierCoreStackInsertOp InsertOp;
InsertOp.SetModifierClass<UAvaExtrudeModifier>();
InsertOp.bEnableModifier = true;

// 插入修改器并获取其指针
UAvaExtrudeModifier* ExtrudeModifier = Cast<UAvaExtrudeModifier>(ModifierStack->InsertModifier(InsertOp));
if (ExtrudeModifier)
{
    // 设置挤出参数
    ExtrudeModifier->SetDepth(30.f);
    ExtrudeModifier->SetExtrudeMode(EAvaExtrudeMode::Symmetrical);
    ExtrudeModifier->SetCloseBack(true);
}
```

### 进阶用法

组合多个修改器，实现复杂效果：先挤出，再弯曲。

```cpp
// 接上面的代码，获取 ModifierStack

// 1. 添加挤出修改器
FActorModifierCoreStackInsertOp ExtrudeOp;
ExtrudeOp.SetModifierClass<UAvaExtrudeModifier>();
UAvaExtrudeModifier* ExtrudeMod = Cast<UAvaExtrudeModifier>(ModifierStack->InsertModifier(ExtrudeOp));
if (ExtrudeMod)
{
    ExtrudeMod->SetDepth(50.f);
}

// 2. 在挤出修改器之上添加弯曲修改器
FActorModifierCoreStackInsertOp BendOp;
BendOp.SetModifierClass<UAvaBendModifier>();
BendOp.bInsertBefore = false; // 插入到栈的当前末尾（挤出之后）
UAvaBendModifier* BendMod = Cast<UAvaBendModifier>(ModifierStack->InsertModifier(BendOp));
if (BendMod)
{
    BendMod->SetAngle(45.f);
    BendMod->SetExtent(0.8f); // 弯曲范围
}
```

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何创建一个自定义 Actor，该 Actor 在构建时自动添加挤出和弯曲修改器。

**MyMotionDesignActor.h**
```cpp
#pragma once
#include "GameFramework/Actor.h"
#include "MyMotionDesignActor.generated.h"

class UActorModifierCoreStack;

UCLASS()
class AMyMotionDesignActor : public AActor
{
    GENERATED_BODY()

public:
    AMyMotionDesignActor();

protected:
    virtual void BeginPlay() override;
    virtual void OnConstruction(const FTransform& Transform) override;

private:
    void SetupModifiers();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components", meta = (AllowPrivateAccess = "true"))
    UActorModifierCoreStack* ModifierStack;
};
```

**MyMotionDesignActor.cpp**
```cpp
#include "MyMotionDesignActor.h"
#include "Components/ActorModifierCoreStack.h"
#include "Modifiers/AvaExtrudeModifier.h"
#include "Modifiers/AvaBendModifier.h"

AMyMotionDesignActor::AMyMotionDesignActor()
{
    PrimaryActorTick.bCanEverTick = false;
    
    ModifierStack = CreateDefaultSubobject<UActorModifierCoreStack>(TEXT("ModifierStack"));
    RootComponent = ModifierStack; // 或者将其附加到根组件
}

void AMyMotionDesignActor::BeginPlay()
{
    Super::BeginPlay();
}

void AMyMotionDesignActor::OnConstruction(const FTransform& Transform)
{
    Super::OnConstruction(Transform);
    SetupModifiers();
}

void AMyMotionDesignActor::SetupModifiers()
{
    if (!ModifierStack) return;

    // 清除之前的修改器（如果需要）
    ModifierStack->ClearModifiers();

    // 添加挤出修改器
    FActorModifierCoreStackInsertOp ExtrudeOp;
    ExtrudeOp.SetModifierClass<UAvaExtrudeModifier>();
    UAvaExtrudeModifier* ExtrudeMod = Cast<UAvaExtrudeModifier>(ModifierStack->InsertModifier(ExtrudeOp));
    if (ExtrudeMod)
    {
        ExtrudeMod->SetDepth(40.f);
        ExtrudeMod->SetCloseBack(true);
    }

    // 添加弯曲修改器
    FActorModifierCoreStackInsertOp BendOp;
    BendOp.SetModifierClass<UAvaBendModifier>();
    UAvaBendModifier* BendMod = Cast<UAvaBendModifier>(ModifierStack->InsertModifier(BendOp));
    if (BendMod)
    {
        BendMod->SetAngle(30.f);
    }
}
```

## 模块依赖

使用 `AvalancheModifiers` 模块（及相关的 Modifier 功能），你的模块需要依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `GeometryCore` | 底层动态网格 (FDynamicMesh3) 数据结构 |
| `GeometryFramework` | 动态网格组件 (UDynamicMeshComponent) 和操作 |
| `ModelingComponents` | 几何处理工具库 (如布尔、细分、倒角等) |
| `DynamicMaterial` | 材质设计师 (Material Designer) 实例和参数管理 |
| `Text3D` | 3D文本组件，用于文字相关的Modifier |
| `ActorModifierCore` | 核心修改器栈框架，所有Modifier的基类 |
| `AvalancheCore` | Avalanche插件的核心功能和场景树 |
| `MeshModelingToolsetExp` | 实验性的网格建模工具集 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将场景设置和大纲视图等Motion Design选项卡移至编辑器独立组 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 添加了使用节目单页面设置时的MRQ分析数据记录功能 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 在节目控制工具栏增加了页面加载选项（全部/下一个/选中项） |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 添加了项目设置，可强制禁用3D文本和形状的碰撞检测 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构视口：在客户端关联/断开关联时进行通知，以清理冗余代码 |

### 维护评价

- **活跃维护**：插件于 2025 年 5 月创建，至 2026 年 5 月仍有持续的更新记录，最新更新集中在 2026 年 5 月，显示 Epic Games 正在积极开发和迭代此插件。
- **高频率更新**：近期内有多次提交，功能更新、性能优化、bug修复和工具链改进并行，表明项目处于活跃开发期。
- **无废弃迹象**：没有在提交信息中发现任何关于“deprecated”或“obsolete”的标记，反而看到从 `Experimental` 迁移到 `VirtualProduction` 目录的提交（首次提交），表明其已进入正式生产环境支持阶段。
- **推荐使用**：这是 Epic Games 官方维护的、用于虚拟制作核心流程的工具。对于从事广播图形、实时可视化、虚拟制片的项目，**强烈推荐**学习和使用。需要注意的是，它依赖众多其他插件，项目设置需完整。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/) （需在文档中搜索 “Motion Design”）