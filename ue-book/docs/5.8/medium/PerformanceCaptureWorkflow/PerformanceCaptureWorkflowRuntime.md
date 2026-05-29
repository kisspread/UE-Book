# Performance Capture Workflow

> Performance Capture In-Editor Workflow tools. Provides access to the Mocap Manager panel.

| 属性 | 值 |
|---|---|
| 中文名 | 表演捕捉工作流 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `PerformanceCaptureWorkflow` (Runtime), `PerformanceCaptureWorkflowRuntime` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-02 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/PerformanceCaptureWorkflow) | |

## 用途

Performance Capture Workflow 插件是 Epic Games 为**虚拟制作 (Virtual Production)** 流程设计的编辑器内工具集，其核心是**简化和增强表演捕捉（动捕）的工作流**。它解决的不是单一功能问题，而是一个**完整的工作流程集成问题**。

基于源码分析，该插件的核心功能包括：
1.  **道具驱动 (Prop Driving)**：通过 `UPCapPropComponent`，让用户的静态网格、骨骼网格或蓝图构成的道具，能够**接收来自 Live Link 的动捕数据（Transform 或 Animation 角色）并实时驱动其位置和姿态**。这对于同步演员手持道具与虚拟场景至关重要。
2.  **虚拟舞台管理 (Stage Management)**：通过 `APerformanceCaptureStageRoot` 提供一个抽象的舞台根节点，用于组织和管理虚拟动捕场景中的网格、俯视图捕捉和地面网格，为动捕排练提供一个可视化的场景基础。
3.  **动态约束计算**：`UPCapPropComponent` 提供了一套**动态约束**系统，可以根据特定角色（如演员）的骨骼位置来动态计算道具的偏移，解决道具与角色身体交互的物理问题（例如，让虚拟道具的尖端始终接触角色手掌）。
4.  **重定向器数据查询**：提供 `UPCapWorkflowRuntimeFunctionLibrary`，允许在运行时读取 IK Retargeter 的骨骼链等信息，主要用于支持动态约束的计算。

简而言之，该插件旨在成为连接动捕系统（Live Link）、资产管道（IK Retargeter）和虚拟场景搭建的**中枢工作流工具**。

## 使用场景

-   **在虚拟制片现场**：使用专业动捕设备捕捉演员表演时，需要将演员手中的虚拟道具（如武器、法杖、工具）与演员的手部骨骼实时同步，用于实时光预览或最终渲染。
-   **动捕排练与预览**：在正式拍摄前，在虚幻编辑器中快速搭建虚拟舞台（地面、标记物、角色模型），并让道具跟随动捕数据运动，用于检查走位、交互和镜头构图。
-   **自定义动态交互**：当简单的 Live Link 数据应用不能满足需求，需要道具根据角色特定部位（如手掌、头盔）的运动进行更复杂的动态位置计算时。
-   **需要查询和分析 IK 重定向器数据**：在蓝图或 C++ 中，需要根据动捕源角色的骨骼链来影响道具行为时。

## 蓝图用法

### 核心节点

**驱动道具 (UPCapPropComponent)**

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Live Link Subject` | 设置用于驱动此道具的 Live Link 主题名称 | `UPCapPropComponent` |
| `Set Evaluate Live Link Data` | 启用或禁用对 Live Link 数据的评估，即开始或暂停驱动 | `UPCapPropComponent` |
| `Set Offset Transform` | 设置应用到传入 Live Link 变换上的本地空间偏移 | `UPCapPropComponent` |
| `Set Global Scale` | 设置应用于传入 Live Link 位置（非缩放）的全局缩放因子 | `UPCapPropComponent` |
| `Set Controlled Component` | 指定受此组件驱动的场景组件（默认为 Actor 的根组件） | `UPCapPropComponent` |
| `Get Controlled Component` | 获取当前受驱动的场景组件 | `UPCapPropComponent` |

**查询重定向器 (UPCapWorkflowRuntimeFunctionLibrary)**

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Source Rig` | 从 IK Retargeter 资产获取源 IK Rig 定义 | `UPCapWorkflowRuntimeFunctionLibrary` |
| `Get Target Rig` | 从 IK Retargeter 资产获取目标 IK Rig 定义 | `UPCapWorkflowRuntimeFunctionLibrary` |
| `Get Retarget Chains` | 获取给定 IK Rig 中的所有骨骼链 | `UPCapWorkflowRuntimeFunctionLibrary` |
| `Get Chain Start Bone` | 获取指定骨骼链的起始骨骼名称 | `UPCapWorkflowRuntimeFunctionLibrary` |
| `Get Chain End Bone` | 获取指定骨骼链的结束骨骼名称 | `UPCapWorkflowRuntimeFunctionLibrary` |
| `Get Chain From Bone` | 获取指定骨骼所属的第一条骨骼链名称 | `UPCapWorkflowRuntimeFunctionLibrary` |

### 使用示例（蓝图描述）

**驱动一个虚拟道具**：
1.  在场景中放置一个 Actor（例如，一个带有静态网格的剑）。
2.  为该 Actor 添加 `PCap Prop Component`（搜索“Prop Component”）。
3.  在组件的详情面板中，将 `Subject Name` 设置为你的 Live Link 动捕数据流主题（例如 “PerformerHand”）。
4.  确保 `Evaluate Live Link Data` 勾选为 `true`。
5.  如果需要调整位置，编辑 `Offset Transform` 属性。
6.  运行时，该剑的 Actor 将跟随动捕数据移动和旋转。

**在运行时查询骨骼链信息**：
1.  创建一个引用了 `IK Retargeter` 资产的变量（例如 “RetargetAsset”）。
2.  从变量拖出引脚，调用 `Get Retarget Chains` 节点，获取所有链信息。
3.  或者，调用 `Get Chain From Bone` 节点，传入一个骨骼名（如 “hand_r”），查看它属于哪条链。

## C++ 用法

### 头文件引入

```cpp
#include "PCapPropComponent.h" // 如果使用 Prop Component
#include "PCapStageRoot.h" // 如果使用 Stage Root Actor
#include "PCapWorkflowRuntimeFunctionLibrary.h" // 如果使用重定向器查询函数库
```

### 基本用法 (驱动道具)

创建并配置一个 `PCapPropComponent` 来驱动一个 Actor 的根组件。
*来源: 基于 `Public/PCapPropComponent.h` 的类声明*

```cpp
// 假设我们有一个 AMyPropActor 类
void AMyPropActor::BeginPlay()
{
    Super::BeginPlay();

    // 创建 Prop 组件
    UPCapPropComponent* PropComponent = NewObject<UPCapPropComponent>(this, TEXT("MocapProp"));
    PropComponent->RegisterComponent();

    // 设置 Live Link 主题
    FLiveLinkSubjectName Subject;
    Subject.Name = TEXT("MotionCapture_Head");
    PropComponent->SetLiveLinkSubject(Subject);

    // 启用评估
    PropComponent->SetEvaluateLiveLinkData(true);

    // 可选：设置偏移和缩放
    FTransform LocalOffset(FRotator(0, 45, 0), FVector(0, 0, 10), FVector::OneVector);
    PropComponent->SetOffsetTransform(LocalOffset);
    PropComponent->SetGlobalScale(100.0f); // 假设动捕数据单位是米，场景单位是厘米

    // 默认情况下，它会驱动 Actor 的根组件。如果需要驱动其他组件：
    // USceneComponent* MyMesh = FindComponentByClass<UStaticMeshComponent>();
    // if (MyMesh)
    // {
    //     PropComponent->SetControlledComponent(MyMesh);
    // }
}
```

### 进阶用法 (使用动态约束和函数库)

使用函数库查询 Retargeter 信息，并结合 Prop 组件的动态约束功能。
*来源: 结合 `Public/PCapWorkflowRuntimeFunctionLibrary.h` 和 `Public/PCapPropComponent.h`*

```cpp
void AMyDynamicPropActor::UpdateDynamicConstraint()
{
    // 1. 获取 Retargeter 资产
    UIKRetargeter* RetargetAsset = LoadObject<UIKRetargeter>(nullptr, TEXT("/Game/Mocap/Retarget_Retargeter"));
    if (!RetargetAsset) return;

    // 2. 查询角色右手骨骼所在的链信息
    FName RightHandChain = UPCapWorkflowRuntimeFunctionLibrary::GetChainFromBone(
        RetargetAsset->GetIKRig(ERetargetSourceOrTarget::Target),
        TEXT("hand_r")
    );

    // 3. 在 Prop 组件中使用这些信息（这里仅为示例逻辑）
    if (PropComponent && !RightHandChain.IsNone())
    {
        // 假设我们有一个逻辑，当道具处于特定骨骼链时启用动态约束
        PropComponent->bUseDynamicConstraint = true;
        
        // 在蓝图或另一个类中，需要将具体的约束计算逻辑连接到
        // PropComponent->DynamicAttachmentCharacters 和
        // PropComponent->CalculateDynamicOffset() 委托上。
        
        // 强制更新组件以应用新的约束设置
        PropComponent->MarkRenderStateDirty();
    }
}
```

## Demo 示例

一个完整的、可编译的最小示例，展示如何创建一个使用 `PCapPropComponent` 驱动的 Actor。

### MyDrivenPropActor.h
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "PCapPropComponent.h"
#include "MyDrivenPropActor.generated.h"

UCLASS()
class AMyDrivenPropActor : public AActor
{
    GENERATED_BODY()

public:
    AMyDrivenPropActor();

    virtual void BeginPlay() override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Performance Capture")
    TObjectPtr<UStaticMeshComponent> PropMeshComponent;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Performance Capture")
    TObjectPtr<UPCapPropComponent> CapturePropComponent;
};
```

### MyDrivenPropActor.cpp
```cpp
#include "MyDrivenPropActor.h"
#include "Components/StaticMeshComponent.h"

AMyDrivenPropActor::AMyDrivenPropActor()
{
    PrimaryActorTick.bCanEverTick = false;

    PropMeshComponent = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("PropMesh"));
    SetRootComponent(PropMeshComponent);
    PropMeshComponent->SetCollisionProfileName(TEXT("NoCollision"));

    CapturePropComponent = CreateDefaultSubobject<UPCapPropComponent>(TEXT("CaptureProp"));
    // CapturePropComponent 默认会附加到根组件并驱动它
}

void AMyDrivenPropActor::BeginPlay()
{
    Super::BeginPlay();

    // 在蓝图或编辑器中设置 Subject Name，或在此处编程设置
    // FLiveLinkSubjectName Subject;
    // Subject.Name = TEXT("YourLiveLinkSubject");
    // CapturePropComponent->SetLiveLinkSubject(Subject);
    
    // 确保评估开始
    CapturePropComponent->SetEvaluateLiveLinkData(true);
}
```

## 模块依赖

从 Build.cs 的 `PublicDependencyModuleNames` 和 `PrivateDependencyModuleNames` 分析得出，该插件除了标准引擎模块外，独特地依赖于：

| 模块 | 用途 |
|---|---|
| `LiveLink` | 核心依赖，用于接收和处理来自外部动捕系统、摄像头等设备的实时数据流 |
| `LiveLinkInterface` | Live Link 接口定义，组件通过它访问 Live Link 客户端和数据 |
| `IKRig` | 用于访问和查询 IK Retargeter、IK Rig 定义等资产，支持运行时骨骼链分析 |
| `IKRigDeveloper` (Editor?) | 推测用于支持 IK Rig 资产的编辑器内功能（动态约束设置等） |
| `LevelSequence` / `LevelSequenceEditor` | 推测用于支持 Sequencer 对动捕道具的控制（通过 `bIsControlledBySequencer` 属性） |

**注意**：`PerformanceCaptureWorkflow` 模块（可能是编辑器或工具部分）的依赖未完全展示，但 `PerformanceCaptureWorkflowRuntime` 模块（运行时）的依赖如上所列。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `6738ae86` | [Performance Capture Workflow] - Add telemetry to the Mocap Manager panel invocation. | 为 Mocap Manager 面板的调用添加了遥测数据收集功能。 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | （虚拟制作相关）将虚拟制作资产归类并迁移，可能影响本插件资产的组织方式。 |
| 2026-05-12 | `cb548ae0` | [Performance Capture Workflow] - Add multicast BP delegates that fire on changes to the timecode and | 新增了蓝图多播委托，用于在时码和（其他属性）变化时广播事件，增强了蓝图可编程性。 |
| 2026-05-01 | `e5ecc8a9` | [PerformanceCaptureWorkflow] - Adds editor only BP function to update a specific row in a PCapDataTa | 添加了编辑器内专用的蓝图函数，用于更新 PCapDataTable 中的特定行，优化数据管理。 |
| 2026-04-20 | `12bc1b78` | [PerformanceCaptureWorkflow] | （提交信息不完整，但日期较近，表明近期有活动。） |

### 维护评价

-   **活跃维护**：插件创建于 2025 年 4 月，至今约 1 年。从近期 git 历史看，自 2026 年 4 月起有持续的提交，最近一次更新在 2026 年 5 月 12 日，且内容涉及功能添加（遥测、委托）和代码优化，表明**插件正在被积极开发和维护**。
-   **Beta 状态**：插件明确标记为 `IsBetaVersion: true`，这意味着其 API 和功能可能尚未完全稳定，在使用过程中可能会遇到变化或问题。
-   **功能聚焦**：插件专注于虚拟制作中的表演捕捉细分领域，功能明确，服务于一个特定的、高价值的用户群体。
-   **推荐程度**：**推荐用于虚拟制作流程的开发者和技术美术**。由于其 Beta 状态，建议在项目中谨慎集成，关注后续更新日志以应对接口变更。它提供了从动捕数据驱动道具到场景管理的完整工具链，能显著提升相关工作流效率。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/PerformanceCaptureWorkflow)
- [官方文档]() （.uplugin 中未提供 DocsURL）
- [测试用例]() （根据提供的文件信息，未在主要源码中发现明确的测试文件路径。测试可能位于 `Engine/Tests/` 目录下，或尚未公开。）