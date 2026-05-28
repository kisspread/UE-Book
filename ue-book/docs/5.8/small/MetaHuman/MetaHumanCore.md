# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 元人类动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、编辑器工具） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-05-02 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方提供的完整数字人类创建与动画工具包，其核心功能远超简单的“动画师”。它解决的问题是**从真实世界的表演捕捉数据（视频、深度图）驱动高保真 MetaHuman 角色的面部动画**。

该插件是一个庞大的系统，旨在实现“捕捉-追踪-求解-驱动”的完整流程：
1.  **捕捉与输入**：通过 `MetaHumanCaptureSource` 和 `MetaHumanCaptureProtocolStack` 导入来自 iPhone（Live Link Face）或其他设备的表演视频、深度数据和校准信息。
2.  **追踪与拟合**：使用 `MetaHumanFaceContourTracker` 追踪视频中的面部轮廓关键点，并利用 `MetaHumanFaceFittingSolver` 将这些 2D 追踪点拟合到 MetaHuman 的 3D 骨骼控制点上。
3.  **动画求解**：`MetaHumanFaceAnimationSolver` 负责将拟合后的数据转换为最终驱动 MetaHuman 骨骼和变形器的动画曲线。
4.  **身份管理**：`MetaHumanIdentity` 模块负责管理数字人类的“身份”，包括其基础网格、骨骼和 DNA 数据。
5.  **序列化与输出**：`MetaHumanSequencer` 模块确保生成的动画可以无缝集成到 Unreal Sequencer 中，用于最终合成或实时渲染。

## 使用场景

-   你需要为一部电影或电视剧创建数字替身，需要从演员的面部表演视频中提取高质量的动画数据。
-   你在开发一个需要实时数字人对话的虚拟人应用，希望通过面部捕捉驱动 MetaHuman 角色。
-   你已经使用 MetaHuman Creator 创建了角色模型，现在需要为其制作基于真实表演的动画序列。
-   你需要批处理大量捕捉数据，将它们转换为可用的动画。

## 蓝图用法

蓝图接口主要集中在视图控制和数据查询上。核心节点大多位于 `UMetaHumanViewportSettings` 类中，用于控制 MetaHuman Animator 编辑器视口的显示状态。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetViewModeIndex` | 获取指定视图（A/B/AB）的视图模式索引（如 Lit, Wireframe） | `UMetaHumanViewportSettings` |
| `SetViewModeIndex` | 设置指定视图的视图模式 | `UMetaHumanViewportSettings` |
| `ToggleShowCurves` | 切换指定视图中面部轮廓曲线的显示/隐藏 | `UMetaHumanViewportSettings` |
| `IsShowingCurves` | 查询指定视图中是否显示曲线 | `UMetaHumanViewportSettings` |
| `ToggleSkeletalMeshVisibility` | 切换指定视图中底层骨骼网格体的显示/隐藏 | `UMetaHumanViewportSettings` |
| `IsSkeletalMeshVisible` | 查询指定视图中骨骼网格体是否可见 | `UMetaHumanViewportSettings` |
| `ToggleFootageVisibility` | 切换指定视图中原始捕捉素材（视频/深度图）的显示/隐藏 | `UMetaHumanViewportSettings` |
| `IsFootageVisible` | 查询指定视图中素材是否可见 | `UMetaHumanViewportSettings` |
| `ToggleDistortion` | 切换指定视图中镜头畸变效果的显示/隐藏 | `UMetaHumanViewportSettings` |
| `IsShowingUndistorted` | 查询指定视图中是否显示未畸变的图像 | `UMetaHumanViewportSettings` |

### 使用示例（蓝图描述）

在一个编辑器工具蓝图（Editor Utility Widget）中，你可能需要创建一个界面来控制 MetaHuman Animator 的视口。
1.  获取 `MetaHumanViewportSettings` 对象的引用（通常在 Animator 面板活动时可用）。
2.  使用一个“Toggle Button”控件，将其 `On Clicked` 事件连接到一个自定义函数。
3.  在该函数中，调用 `ToggleSkeletalMeshVisibility` 节点，并将 `In View` 参数设置为 `EABImageViewMode::A` 或 `Current`。这会切换视图 A 中底层骨骼的显示，用于检查动画驱动是否正确。
4.  使用另一个按钮调用 `ToggleFootageVisibility`，以便在需要时将原始视频素材叠加显示，用于对比动画与原始表演。

## C++ 用法

C++ 层面提供了更底层的控制，用于处理曲线数据、形状注释和系统集成。

### 头文件引入

```cpp
#include "MetaHumanCurveDataController.h"
#include "ShapeAnnotationWrapper.h"
#include "DNAUtilities.h"
#include "MetaHumanContourData.h"
```

### 基本用法

使用 `FMetaHumanCurveDataController` 来操作和查询追踪到的面部轮廓数据。

```cpp
// 假设你有一个 UMetaHumanContourData* 对象 (ContourDataPtr)，它包含了一帧的轮廓数据
FMetaHumanCurveDataController CurveController(ContourDataPtr);

// 从配置文件和默认数据初始化轮廓
FFrameTrackingContourData DefaultData; // 通常从某个资产加载
CurveController.InitializeContoursFromConfig(DefaultData, TEXT("1.0"));

// 当收到新的追踪数据时更新
FFrameTrackingContourData NewTrackingData = ...; // 从追踪器获取
CurveController.UpdateFromContourData(NewTrackingData, true);

// 查询某条曲线（例如，左侧眉毛）是否被选中
TPair<bool, bool> Status = CurveController.GetCurveSelectedAndActiveStatus(TEXT("brow_left"));
if (Status.Key) // 是否被选中
{
    // 执行某些操作，如高亮显示
}

// 获取所有可见曲线的稠密点数据，用于绘制
TMap<FString, TArray<FVector2D>> VisibleDensePoints = CurveController.GetDensePointsForVisibleCurves();
```

**来源文件**: `Source/MetaHumanCore/Public/MetaHumanCurveDataController.h`

### 进阶用法

结合 `FDNAUtilities` 检查不同 MetaHuman 身份之间的 DNA 兼容性，这在准备批量处理或混合动画时很重要。

```cpp
#include "DNAUtilities.h"

// 假设你有两个 IDNAReader 指针，分别代表两个不同的 MetaHuman 角色
IDNAReader* ReaderA = ...;
IDNAReader* ReaderB = ...;

FString CompatibilityMessage;
bool bAreCompatible = FDNAUtilities::CheckCompatibility(
    ReaderA, 
    ReaderB, 
    EDNARigCompatiblityFlags::Joint | EDNARigCompatiblityFlags::Mesh, // 只检查骨骼和网格
    CompatibilityMessage
);

if (!bAreCompatible)
{
    UE_LOG(LogTemp, Warning, TEXT("DNA不兼容: %s"), *CompatibilityMessage);
    // 无法在它们之间安全地传递动画
}
```

**来源文件**: `Source/MetaHumanCore/Public/DNAUtilities.h`

## Demo 示例

以下是一个极简的 C++ 示例，展示如何初始化一个轮廓数据控制器并模拟一次更新。

```cpp
// MetaHumanDemoActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MetaHumanDemoActor.generated.h"

class UMetaHumanContourData;
class FMetaHumanCurveDataController;

UCLASS()
class MYPROJECT_API AMetaHumanDemoActor : public AActor
{
    GENERATED_BODY()

public:
    AMetaHumanDemoActor();

protected:
    virtual void BeginPlay() override;

private:
    // 轮廓数据资产，可在编辑器中分配
    UPROPERTY(EditAnywhere)
    TObjectPtr<UMetaHumanContourData> ContourDataAsset;

    // 控制器实例，用于管理轮廓数据
    TUniquePtr<FMetaHumanCurveDataController> CurveController;
};
```

```cpp
// MetaHumanDemoActor.cpp
#include "MetaHumanDemoActor.h"
#include "MetaHumanContourData.h"
#include "MetaHumanCurveDataController.h"

AMetaHumanDemoActor::AMetaHumanDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMetaHumanDemoActor::BeginPlay()
{
    Super::BeginPlay();

    if (ContourDataAsset)
    {
        // 初始化控制器
        CurveController = MakeUnique<FMetaHumanCurveDataController>(ContourDataAsset);
        
        // 模拟加载配置和默认数据
        FFrameTrackingContourData DefaultContourData;
        // ... 这里应该是从资产或配置文件加载 DefaultContourData 的代码 ...
        CurveController->InitializeContoursFromConfig(DefaultContourData, TEXT("5.0"));

        // 模拟一次追踪更新（实际数据应来自追踪管线）
        FFrameTrackingContourData SimulatedUpdate;
        // ... 填充 SimulatedUpdate 的代码 ...
        CurveController->UpdateFromContourData(SimulatedUpdate, true);

        UE_LOG(LogTemp, Log, TEXT("MetaHuman 轮廓控制器初始化完成"));
    }
}
```

## 模块依赖

由于插件内含众多模块，且它们相互依赖，作为使用者，你的项目通常只需依赖最外层的模块（如 `MetaHumanCore` 或 `MetaHumanIdentity`）。以下列出了一些关键且非通用的依赖模块。

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | 核心技术库，通常为底层算法提供支持 |
| `ControlRigDeveloper` | 用于创建和编辑 Control Rig，MetaHuman 的面部驱动基于 Control Rig |
| `SkeletalMeshUtilitiesCommon` | 骨骼网格体的通用工具函数 |
| `MetaHumanSDKEditor` | MetaHuman SDK 的编辑器部分，用于资产管理和编辑器集成 |
| `MetaHumanCaptureDataEditor` | 捕捉数据资产的编辑器自定义 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用身体追踪时，禁用关卡序列导出功能 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 上的渲染瑕疵 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 在身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | [MetaHuman Animator] 为现有网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存问题 |

### 维护评价

- **活跃维护**：从提交记录看，该插件在**近期（2026年5月）** 仍有密集的功能更新和 Bug 修复。
- **核心功能稳定**：作为 Epic 的官方工具，其用于核心的 MetaHuman 创建和动画工作流。
- **推荐使用**：如果你正在使用 MetaHuman 且需要进行基于表演的面部动画，这是**必须且推荐**的官方解决方案。它仍在持续开发中，以支持新的平台功能（如身体追踪）并修复问题。
- **注意**：该插件规模庞大，学习曲线较陡峭，建议结合 Epic 官方的 MetaHuman 文档和教程使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/MetaHuman-in-Unreal-Engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanControlsConversionTest)