# Motion Design

> Compositing, designer and broadcasting tool.
> Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 运动设计 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（几何修改器、材质参数工具、图案生成工具） |
| 模块 | `Avalanche` (Runtime), `AvalancheAttribute` (Runtime), `AvalancheCamera` (Runtime), `AvalancheComponentVisualizers` (Runtime), `AvalancheCore` (Runtime), `AvalancheEffectors` (Runtime), `AvalancheInteractiveTools` (Runtime), `AvalancheInteractiveToolsRuntime` (Runtime), `AvalancheLevelViewport` (Runtime), `AvalancheMRQ` (Runtime), `AvalancheMask` (Runtime), `AvalancheMaterial` (Runtime), `AvalancheMedia` (Runtime), `AvalancheModifiers` (Runtime), `AvalancheOutliner` (Runtime), `AvalanchePropertyAnimator` (Runtime), `AvalancheRemoteControl` (Runtime), `AvalancheSceneRig` (Runtime), `AvalancheSceneTree` (Runtime), `AvalancheSequence` (Runtime), `AvalancheSequencer` (Runtime), `AvalancheShapes` (Runtime), `AvalancheTag` (Runtime), `AvalancheText` (Runtime), `AvalancheTransition` (Runtime), `AvalancheViewport` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Motion Design（运动设计）插件是 UE5 为虚拟制作和广播设计场景提供的一套综合性工具集。它解决了在实时渲染环境中快速创建、编辑和控制动态图形元素的需求。

其核心模块 `AvalancheModifiers` 提供了一系列强大的非破坏性几何修改器（Modifier），允许设计师在编辑器或运行时对 3D 模型（如 Text3D 文本、形状、网格体）进行程序化变形和调整，而无需破坏原始资产。这些修改器可以堆叠、组合，形成强大的程序化建模和动画工作流，是创建虚拟演播室图形、数据可视化、动态标题等内容的理想选择。

## 使用场景

-   **虚拟演播室图形**：你需要快速设计并实时调整演播室中的 3D 标题、Logo、图表和背景元素。
-   **数据驱动可视化**：你需要将实时数据（如股市行情、体育比分）动态映射到 3D 模型的几何形状或材质参数上。
-   **动态重复图案**：你需要沿直线、网格或圆形快速生成一系列相同的几何体，并精确控制间距、旋转和缩放。
-   **复杂几何效果**：你需要为模型添加挤出、弯曲、锥化、倒角、布尔运算（挖洞、相交、合并）等效果。
-   **材质参数控制**：你需要动态控制一组模型上的材质参数（如颜色、不透明度），实现整体或局部的视觉变化。

## 蓝图用法

`AvalancheModifiers` 模块暴露了大量通过 `UFUNCTION(BlueprintCallable)` 标记的蓝图节点，这些节点主要分布在各个具体的修改器类中。以下按功能分组列出核心节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetExtrudeMode` | 设置挤出模式（对向、正面、对称） | `UAvaExtrudeModifier` |
| `SetDepth` | 设置挤出深度 | `UAvaExtrudeModifier` |
| `SetAngle` | 设置弯曲角度 | `UAvaBendModifier` |
| `SetAmount` | 设置锥化量 | `UAvaTaperModifier` |
| `SetMode` | 设置布尔模式（目标、减去、相交、合并） | `UAvaBooleanModifier` |
| `SetChannel` | 设置布尔运算通道 | `UAvaBooleanModifier` |
| `SetActiveToolClass` | 设置图案修改器使用的工具类（线、网格、圆） | `UAvaPatternModifier` |
| `SetGlobalOpacity` | 设置全局不透明度 | `UAvaGlobalOpacityModifier` |
| `SetMaterialParameters` | 设置材质参数映射 | `UAvaMaterialParameterModifier` |
| `SetSplineActor` | 设置样条线采样源 | `UAvaSplineSweepModifier` |
| `SetReferenceActor` | 设置自动缩放参考的 Actor | `UAvaAutoSizeModifier` |
| `SetMode` (TranslucentPriority) | 设置透明排序优先级模式（相机距离、大纲树顺序等） | `UAvaTranslucentPriorityModifier` |

### 使用示例（蓝图描述）

假设你有一个 `Text3D` 组件，并希望将其挤出 50 个单位，然后沿 Y 轴重复 4 次：
1.  获取文本 Actor 的 **Modifier Stack**（修改器栈）。
2.  使用 **Add Modifier** 节点，类选择 `UAvaExtrudeModifier`。
3.  调用新创建的修改器的 **Set Depth** 节点，将 `Depth` 设为 `50.0`。
4.  再次使用 **Add Modifier** 节点，添加一个 `UAvaPatternModifier`。
5.  调用 `UAvaPatternModifier` 的 **Set Active Tool Class** 节点，选择 `UAvaPatternModifierLineTool`。
6.  获取该工具并调用 **Set Line Axis** (设为 Y)，**Set Line Count** (设为 4)，**Set Line Spacing** (设为 `10.0`)。

## C++ 用法

### 头文件引入

```cpp
#include “Modifiers/AvaExtrudeModifier.h”
#include “Modifiers/AvaPatternModifier.h”
#include “Tools/AvaPatternModifierLineTool.h”
#include “AvalancheModifiersModule.h”
```

### 基本用法

以下示例展示了如何在 C++ 中为一个 Actor 添加并配置一个挤出修改器。

```cpp
// 假设我们有一个 AActor* MyActor
// 1. 获取或创建该 Actor 上的修改器栈
UActorModifierCoreStack* ModifierStack = UActorModifierCoreSubsystem::GetSubsystem()->GetOrCreateModifierStack(MyActor);

// 2. 构建添加操作，并指定要添加的修改器类
FActorModifierCoreStackInsertOp InsertOp;
InsertOp.ModifierClass = UAvaExtrudeModifier::StaticClass();

// 3. 添加修改器到栈中
UAvaExtrudeModifier* ExtrudeModifier = Cast<UAvaExtrudeModifier>(ModifierStack->AddModifier(InsertOp));
if (ExtrudeModifier)
{
    // 4. 配置修改器属性
    ExtrudeModifier->SetDepth(50.0f);
    ExtrudeModifier->SetExtrudeMode(EAvaExtrudeMode::Opposite);
    ExtrudeModifier->SetCloseBack(true);
    // 修改器栈会自动应用更改
}
```
*代码逻辑参考自 `FAvaModifierTestUtils` 中的测试工具函数。*

### 进阶用法

组合使用多个修改器，并设置一个图案修改器使用其线性工具。

```cpp
// 承接上文的 ExtrueModifier，再添加一个图案修改器
FActorModifierCoreStackInsertOp PatternInsertOp;
PatternInsertOp.ModifierClass = UAvaPatternModifier::StaticClass();
UAvaPatternModifier* PatternModifier = Cast<UAvaPatternModifier>(ModifierStack->AddModifier(PatternInsertOp));

if (PatternModifier)
{
    // 设置图案工具为线性
    TSubclassOf<UAvaPatternModifierLineTool> LineToolClass = UAvaPatternModifierLineTool::StaticClass();
    PatternModifier->SetActiveToolClass(LineToolClass);

    // 获取工具实例并进行配置
    if (UAvaPatternModifierLineTool* LineTool = Cast<UAvaPatternModifierLineTool>(
        PatternModifier->FindOrAddTool(LineToolClass)))
    {
        LineTool->SetLineAxis(EAvaPatternModifierAxis::X);
        LineTool->SetLineCount(5);
        LineTool->SetLineSpacing(20.0f);
        LineTool->SetLineAlignment(EAvaPatternModifierLineAlignment::Center);
    }
}
```

## Demo 示例

一个完整的、可编译的最小示例，展示如何在 C++ Actor 中创建并使用修改器栈。

**MyModifierActor.h**
```cpp
#pragma once

#include “CoreMinimal.h”
#include “GameFramework/Actor.h”
#include “MyModifierActor.generated.h”

class UActorModifierCoreStack;
class UAvaExtrudeModifier;

UCLASS()
class MYPROJECT_API AMyModifierActor : public AActor
{
    GENERATED_BODY()

public:
    AMyModifierActor();

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = “Modifier”, meta = (AllowPrivateAccess = “true”))
    UActorModifierCoreStack* ModifierStack;

    UPROPERTY()
    UAvaExtrudeModifier* ExtrudeModifier;
};
```

**MyModifierActor.cpp**
```cpp
#include “MyModifierActor.h”
#include “Components/StaticMeshComponent.h”
#include “Modifiers/AvaExtrudeModifier.h”
#include “ActorModifierCoreSubsystem.h”

AMyModifierActor::AMyModifierActor()
{
    PrimaryActorTick.bCanEverTick = false;

    UStaticMeshComponent* MeshComp = CreateDefaultSubobject<UStaticMeshComponent>(TEXT(“Mesh”));
    RootComponent = MeshComp;
    // 这里可以设置一个静态网格体
}

void AMyModifierActor::BeginPlay()
{
    Super::BeginPlay();

    // 1. 获取子系统
    UActorModifierCoreSubsystem* Subsystem = UActorModifierCoreSubsystem::GetSubsystem();

    // 2. 为当前 Actor 创建或获取修改器栈
    ModifierStack = Subsystem->GetOrCreateModifierStack(this);
    if (!ModifierStack)
    {
        UE_LOG(LogTemp, Error, TEXT(“Failed to get modifier stack for actor %s”), *GetName());
        return;
    }

    // 3. 定义添加挤出修改器的操作
    FActorModifierCoreStackInsertOp InsertOp;
    InsertOp.ModifierClass = UAvaExtrudeModifier::StaticClass();

    // 4. 添加修改器
    ExtrudeModifier = Cast<UAvaExtrudeModifier>(ModifierStack->AddModifier(InsertOp));

    // 5. 配置并应用
    if (ExtrudeModifier)
    {
        ExtrudeModifier->SetDepth(30.0f);
        ExtrudeModifier->SetExtrudeMode(EAvaExtrudeMode::Symmetrical);
        ExtrudeModifier->SetCloseBack(false);
        // 属性设置会自动触发 Apply
    }
}
```

## 模块依赖

要使用 `AvalancheModifiers` 模块，你的 `Build.cs` 文件需要依赖以下关键模块（除 Core/Engine 等常见模块外）：

| 模块 | 用途 |
|---|---|
| `ActorModifierCore` | 修改器系统的基础框架，提供修改器栈和核心基类。 |
| `GeometryScript` | 用于操作 `FDynamicMesh3`，执行实际的网格体修改（挤出、弯曲、布尔等）。 |
| `AvalancheCore` | Motion Design 插件的核心功能和类型定义。 |
| `MotionDesignToolset` | 提供与 Motion Design 工具集集成的工具类和接口。 |
| `MaterialDesigner` | 用于创建和操作 `UMaterialInstanceDynamic`，支持材质参数修改器。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将运动设计编辑器的选项卡（场景设置、大纲）独立分组，改善了编辑器布局。 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 在使用节目单页面设置时增加了 MRQ（Movie Render Queue）分析功能。 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 为节目控制工具栏添加了页面加载选项（全部、下一个、选定），并增加了新功能。 |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 增加了项目设置，可以强制禁用 Text3D 和形状的碰撞。 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口：通过在客户端关联或解除关联时进行通知，优化了代码结构。 |

### 维护评价

-   **活跃维护**：该插件是 Epic Games 官方维护的 Virtual Production 核心组件。从 Git 历史看，更新非常频繁（最近几次更新间隔仅数天），且每次提交都涉及实质性的功能增强、UI 改进或性能优化，而非简单的编译修复。
-   **稳定性**：插件从实验性目录 (`/Plugins/Experimental`) 正式迁移至生产目录 (`/Plugins/VirtualProduction`)，标志着其已达到生产就绪状态。源码中存在部分已废弃属性（如 `Resolution` 在 `AvaTaperModifier` 中），显示了代码的持续演进。
-   **推荐使用**：**强烈推荐**。该插件是 UE5 虚拟制作工作流中不可或缺的一部分，尤其适合广播设计和实时图形领域。其非破坏性的修改器架构功能强大且灵活，非常适合需要快速迭代和程序化控制的项目。文档和示例虽需自行探索源码，但其设计良好且测试齐全。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheModifiers/Internal/Tests)