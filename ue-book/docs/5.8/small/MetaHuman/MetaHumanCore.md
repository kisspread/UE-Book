# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（运行时模块、编辑器工具、资产） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 🆕 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是一套完整的数字人创建、动画和编辑工具集。它旨在解决从面部捕捉数据生成高质量 MetaHuman 动画的端到端工作流问题。插件的核心功能包括：

1.  **面部捕捉与追踪**：处理来自 Live Link Face 等应用的原始面部捕捉数据，通过轮廓追踪（Contour Tracking）和深度生成（Depth Generation）来驱动面部网格。
2.  **身份与动画求解**：提供面部拟合求解器（Face Fitting Solver）和动画求解器（Animation Solver），将捕捉数据转换为适用于特定 MetaHuman 角色的动画控制数据。
3.  **性能与批量处理**：包含性能优化（Performance）和批量处理（Batch Processor）模块，以提高大型序列或多个资产的处理效率。
4.  **编辑器集成与工具**：提供丰富的编辑器工具（如 Identity 编辑器、Sequencer 集成、视口控制）来创建、预览和精调 MetaHuman 动画。
5.  **语音驱动动画**：集成 Speech2Face 技术，支持从音频直接生成面部动画。

**为什么存在？** 随着虚拟数字人在游戏、影视和实时应用中的需求激增，创建逼真且具有表现力的数字人成为了一项复杂的技术挑战。MetaHuman Animator 通过整合 Epic Games 在面部捕捉、机器学习和实时渲染方面的先进技术，为创作者提供了一个标准化的、高质量的工具链，极大地简化了从现实演员到虚拟角色的动画转换流程。

## 使用场景

-   **游戏开发**：为你的 MetaHuman 角色创建电影级的面部动画序列，用于过场动画或实时对话系统。
-   **虚拟制片**：在 LED 虚拟影棚中，利用实时面部捕捉驱动虚拟角色，实现即时预览和交互。
-   **实时互动应用**：在 VR/AR 或元宇宙应用中，驱动用户的虚拟化身进行实时表情互动。
-   **高质量内容创作**：为广告、宣传片或影视项目制作超写实的数字人动画。

## 蓝图用法

由于插件规模庞大且功能高度专业化，蓝图交互主要集中在几个核心的设置和控制类上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetViewModeIndex` | 获取指定视图模式（A视/B视）的视口渲染模式（如光照、线框等） | `UMetaHumanViewportSettings` |
| `SetViewModeIndex` | 设置指定视图模式的视口渲染模式 | `UMetaHumanViewportSettings` |
| `ToggleShowCurves` | 切换显示/隐藏指定视图中的面部控制曲线 | `UMetaHumanViewportSettings` |
| `IsShowingCurves` | 查询指定视图中是否正在显示曲线 | `UMetaHumanViewportSettings` |
| `ToggleSkeletalMeshVisibility` | 切换显示/隐藏指定视图中的骨骼网格体 | `UMetaHumanViewportSettings` |
| `IsSkeletalMeshVisible` | 查询指定视图中骨骼网格体是否可见 | `UMetaHumanViewportSettings` |
| `ToggleFootageVisibility` | 切换显示/隐藏指定视图中的原始捕捉画面 | `UMetaHumanViewportSettings` |
| `IsFootageVisible` | 查询指定视图中原始捕捉画面是否可见 | `UMetaHumanViewportSettings` |

### 使用示例（蓝图描述）

1.  **切换视口显示**：在 MetaHuman 编辑器工具界面中，你可能会有“A视”和“B视”两个视口。通过蓝图，你可以获取一个 `UMetaHumanViewportSettings` 对象的引用，然后调用 `ToggleFootageVisibility` 节点，传入 `EABImageViewMode::A`，即可控制A视中原始捕捉画面的显示/隐藏，用于对比原始数据和动画结果。
2.  **查询动画状态**：在动画精调过程中，你可能需要知道当前是否正在显示控制顶点以便进行编辑。可以调用 `IsShowingControlVertices` 节点，如果返回 `true`，则可能启用一个用于拖拽这些顶点的蓝图逻辑。

## C++ 用法

### 头文件引入

使用 MetaHuman Animator 的核心功能时，通常需要引入 `MetaHumanCore` 模块。

```cpp
#include "MetaHumanCore.h"
```

### 基本用法

从提供的 `MetaHumanViewportSettings.h` 头文件中，我们可以看到管理视口状态的核心类。

```cpp
// 获取或创建一个视口设置对象（通常在编辑器工具或自定义视口逻辑中）
UMetaHumanViewportSettings* ViewportSettings = GetMutableDefault<UMetaHumanViewportSettings>();

// 查询当前A视是否显示骨骼网格体
bool bIsMeshVisible = ViewportSettings->IsSkeletalMeshVisible(EABImageViewMode::A);

// 切换B视的曲线显示状态
ViewportSettings->ToggleShowCurves(EABImageViewMode::B);

// 设置A视的视口模式为线框模式
ViewportSettings->SetViewModeIndex(EABImageViewMode::A, VMI_Wireframe, true /* bNotify */);
```

**来源文件**: `Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanCore/Public/MetaHumanViewportSettings.h`

### 进阶用法

`FMetaHumanCurveDataController` 类管理面部控制曲线的显示和编辑逻辑，是进行精细动画调整的关键。

```cpp
// 假设你已经有一个 FMetaHumanCurveDataController 实例（通常在编辑器上下文中获取）
FMetaHumanCurveDataController CurveController(ContourData, ECurveDisplayMode::Editing);

// 初始化轮廓数据
CurveController.InitializeContoursFromConfig(TrackingContourData, ConfigVersion);

// 移动选中的控制点（例如在用户拖拽后）
TSet<int32> SelectedPointIds = { 1, 2, 3 };
FVector2D DragOffset(5.0f, -2.0f);
CurveController.OffsetSelectedPoints(SelectedPointIds, DragOffset);

// 添加或移除关键帧（控制点）
bool bSuccess = CurveController.AddRemoveKey(FVector2D(100.0f, 150.0f), TEXT("brow_inner_left"), true /* bAdd */);

// 监听曲线更新事件
CurveController.TriggerContourUpdate().AddLambda([]() {
    // 当曲线数据发生变化时，刷新视口或UI
    UE_LOG(LogMetaHumanCore, Log, TEXT("Contour data updated, refreshing view."));
});
```

**来源文件**: `Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanCore/Public/MetaHumanCurveDataController.h`

## Demo 示例

由于 MetaHuman Animator 是一个高度集成、界面驱动的工具集，其“最小示例”通常是在 Unreal Editor 中创建和使用一个 MetaHuman 角色并为其应用捕捉数据。以下代码片段展示了如何在 C++ 中编程访问和操作核心数据对象。

```cpp
// MetaHumanDemoActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MetaHumanContourData.h"
#include "MetaHumanViewportSettings.h"
#include "MetaHumanDemoActor.generated.h"

UCLASS()
class AMetaHumanDemoActor : public AActor
{
    GENERATED_BODY()

public:
    AMetaHumanDemoActor();

protected:
    virtual void BeginPlay() override;

public:
    UFUNCTION(BlueprintCallable, Category = "MetaHuman Demo")
    void SetViewportFootageVisible(bool bVisible);

private:
    UPROPERTY()
    TObjectPtr<UMetaHumanContourData> ContourData;

    UPROPERTY()
    TObjectPtr<UMetaHumanViewportSettings> ViewportSettings;
};

// MetaHumanDemoActor.cpp
#include "MetaHumanDemoActor.h"
#include "MetaHumanViewportSettings.h"

AMetaHumanDemoActor::AMetaHumanDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;
    ContourData = CreateDefaultSubobject<UMetaHumanContourData>(TEXT("ContourData"));
}

void AMetaHumanDemoActor::BeginPlay()
{
    Super::BeginPlay();

    // 获取全局视口设置（单例）
    ViewportSettings = GetMutableDefault<UMetaHumanViewportSettings>();
}

void AMetaHumanDemoActor::SetViewportFootageVisible(bool bVisible)
{
    if (ViewportSettings)
    {
        // 根据当前可见性状态进行切换，使其达到目标状态
        if (ViewportSettings->IsFootageVisible(EABImageViewMode::A) != bVisible)
        {
            ViewportSettings->ToggleFootageVisibility(EABImageViewMode::A);
        }
    }
}
```

## 模块依赖

MetaHuman Animator 由近 30 个模块组成，形成了一个复杂的依赖网络。以下是该插件**独特**的、不常见的核心依赖：

| 模块 | 用途 |
|---|---|
| `ControlRigDeveloper` | 为 MetaHuman 的面部骨骼提供 Control Rig 的开发支持。 |
| `SkeletalMeshUtilitiesCommon` | 提供骨骼网格体的通用工具函数，用于处理 MetaHuman 的身体和面部网格。 |
| `MetaHumanSDKEditor` | 提供与 MetaHuman 创作工具（如 MetaHuman Creator）交互的编辑器层接口。 |
| `MediaUtils`, `MediaAssets` | 处理视频媒体（如捕捉镜头）的加载和播放。 |
| `LiveLinkInterface` | 集成 Live Link 系统，用于接收实时的面部捕捉数据。 |

**说明**：除了上述模块，该插件还依赖所有常见的 UE 核心模块（Core, Engine, Slate, UMG 等）。由于模块众多，依赖关系复杂，在项目中启用此插件时，建议通过 Unreal Build Tool 自动处理依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 启用身体追踪时禁用关卡序列导出功能 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 上的渲染瑕疵 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | [MHA] 支持为现有网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存问题 |

### 维护评价

**活跃维护**。

-   **创建时间**：创建日期未知，但作为 MetaHuman 工具链的核心部分，其开发周期与 UE5 的 MetaHuman 功能紧密相关。
-   **更新频率**：从近期提交记录看，维护非常**活跃**（多个提交集中在几天内）。更新内容聚焦于功能修复、新特性（如导出支持）和性能优化（缓存问题），表明该插件是 Epic Games 持续投入的重点项目。
-   **已知限制**：作为一套庞大的工具集，它对硬件（特别是 GPU 计算和 RHI）有一定要求（参考 `FMetaHumanSupportedRHI`），并且工作流涉及多个步骤，学习曲线较陡。
-   **推荐使用**：**强烈推荐**用于任何涉及 MetaHuman 角色高质量面部动画的项目。它是实现该功能的官方且最完整的解决方案。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
-   [官方文档](https://docs.unrealengine.com/5.8/en-US/metahuman-animator-in-unreal-engine/)