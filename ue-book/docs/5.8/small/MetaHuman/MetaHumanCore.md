# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | 元人类动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置、资产、蓝图） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-03-17 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是一个完整的端到端工具链，用于将真实世界的面部表演数据（通常来自 iPhone 的深度摄像头）转化为驱动 MetaHuman 角色动画的骨骼数据。它解决的核心问题是**高保真数字人动画的生成与编辑**。

这个插件不是单一的功能，而是一个庞大的生态系统，涵盖了从数据摄入（Ingestion）、面部特征点追踪（Contour Tracking）、面部网格匹配（Fitting）、动画求解（Animation Solving）到最终在 Sequencer 中编辑和导出动画的完整流程。它允许开发者创建逼真的 MetaHuman 角色面部动画，用于游戏过场动画、虚拟制片或实时应用。

## 使用场景

- **数字人动画制作**：你需要为 MetaHuman 角色创建逼真的面部动画，基于演员的真实表演。
- **虚拟制片**：在虚拟制片项目中，需要将实时或预先录制的面部表演数据快速应用到虚拟角色上。
- **游戏过场动画**：为游戏的过场动画或实时对话系统生成高质量的面部动画。
- **数据处理与批处理**：使用 `MetaHumanBatchProcessor` 模块，对大量的表演数据进行自动化处理。

## 蓝图用法

核心蓝图节点主要集中在视图控制、曲线编辑和数据管理方面，通过 `UMetaHumanViewportSettings` 和 `FMetaHumanCurveDataController` 类暴露。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetViewModeIndex` | 获取指定视图（A/B）的当前显示模式（如线框、光照等） | `UMetaHumanViewportSettings` |
| `SetViewModeIndex` | 设置指定视图的显示模式 | `UMetaHumanViewportSettings` |
| `ToggleShowCurves` | 切换在指定视图中显示/隐藏面部曲线 | `UMetaHumanViewportSettings` |
| `IsShowingCurves` | 检查指定视图中是否正在显示面部曲线 | `UMetaHumanViewportSettings` |
| `ToggleSkeletalMeshVisibility` | 切换在指定视图中显示/隐藏骨骼网格体 | `UMetaHumanViewportSettings` |
| `ToggleFootageVisibility` | 切换在指定视图中显示/隐藏原始素材画面 | `UMetaHumanViewportSettings` |
| `MoveSelectedPoint` | 将选中的控制点移动到新的图像空间坐标 | `FMetaHumanCurveDataController` |
| `OffsetSelectedPoints` | 按偏移量移动所有选中的控制点 | `FMetaHumanCurveDataController` |
| `AddRemoveKey` | 在指定曲线上添加或移除一个关键点 | `FMetaHumanCurveDataController` |

### 使用示例（蓝图描述）

1.  **控制视图显示**：获取当前编辑器的视图设置对象 (`UMetaHumanViewportSettings`)。使用 `IsFootageVisible` 节点检查视图A是否显示素材，如果不显示，则调用 `ToggleFootageVisibility` 节点（传入 `EABImageViewMode::A`）来显示它。
2.  **编辑面部曲线**：在动画编辑器中，通过某种方式获取到 `FMetaHumanCurveDataController` 的实例。当用户在视口点击某个曲线上的控制点时，获取该点的ID。然后，使用 `MoveSelectedPoint` 节点，传入该点ID和鼠标在图像空间的新坐标，实现对点的拖拽操作。

## C++ 用法

### 头文件引入

```cpp
// 核心视图与曲线控制
#include "MetaHumanCore/Public/MetaHumanViewportSettings.h"
#include "MetaHumanCore/Public/MetaHumanCurveDataController.h"
#include "MetaHumanCore/Public/MetaHumanContourData.h"

// 轮廓数据版本管理
#include "MetaHumanCore/Public/MetaHumanContourDataVersion.h"

// DNA工具
#include "MetaHumanCore/Public/DNAUtilities.h"
```

### 基本用法

以下示例展示了如何控制MetaHuman编辑器的视图状态，来源基于 `UMetaHumanViewportSettings` 的公共接口。

```cpp
// 假设我们已经获取到 UMetaHumanViewportSettings* ViewportSettings
if (ViewportSettings)
{
    // 1. 检查并切换视图A的骨骼网格体显示
    if (!ViewportSettings->IsSkeletalMeshVisible(EABImageViewMode::A))
    {
        ViewportSettings->ToggleSkeletalMeshVisibility(EABImageViewMode::A);
    }

    // 2. 设置视图B的显示模式为“线框”
    ViewportSettings->SetViewModeIndex(EABImageViewMode::B, VMI_Wireframe, true);

    // 3. 获取当前的相机状态
    const FMetaHumanViewportCameraState& CameraState = ViewportSettings->CameraState;
    UE_LOG(LogTemp, Log, TEXT("Camera Location: %s"), *CameraState.Location.ToString());
}
```

### 进阶用法

以下示例展示了如何使用 `FMetaHumanCurveDataController` 来程序化地操作面部曲线，来源基于其丰富的公共接口。

```cpp
// 假设我们已经有一个 FMetaHumanCurveDataController* CurveController 和 UMetaHumanContourData* ContourData
if (CurveController && ContourData)
{
    // 1. 从配置初始化曲线（通常在加载数据后调用）
    FFrameTrackingContourData DefaultContourData; // 从配置或默认值填充
    CurveController->InitializeContoursFromConfig(DefaultContourData, TEXT("1.0"));

    // 2. 在曲线上添加一个关键点
    FVector2D PointPosition(0.5f, 0.5f); // 图像空间坐标
    FString CurveName = TEXT("UpperLipTop");
    if (CurveController->AddRemoveKey(PointPosition, CurveName, true /* bInAdd */))
    {
        UE_LOG(LogTemp, Log, TEXT("Key added to curve %s"), *CurveName);
    }

    // 3. 选中一组点并移动它们
    TSet<int32> PointsToMove = { 101, 102, 103 }; // 假设的点ID
    FVector2D Offset(10.0f, -5.0f); // 像素偏移
    CurveController->OffsetSelectedPoints(PointsToMove, Offset);

    // 4. 获取曲线的控制点位置，用于自定义渲染
    TArray<FVector2D> ControlVertices = ContourData->GetControlVertexPositions(CurveName);
    for (const FVector2D& Vertex : ControlVertices)
    {
        // 绘制或记录这些控制点...
    }
}
```

## Demo 示例

这是一个最小化的 C++ 示例，展示如何实例化并配置视图设置对象。实际使用中，此类对象通常由 MetaHuman 编辑器工具管理。

```cpp
// MyMetaHumanController.h
#pragma once
#include "CoreMinimal.h"
#include "MetaHumanCore/Public/MetaHumanViewportSettings.h"
#include "MyMetaHumanController.generated.h"

UCLASS(BlueprintType)
class UMyMetaHumanController : public UObject
{
    GENERATED_BODY()

public:
    UMyMetaHumanController();

    UFUNCTION(BlueprintCallable, Category = "MyMetaHuman")
    void ResetViewportToDefault();

private:
    UPROPERTY()
    TObjectPtr<UMetaHumanViewportSettings> ViewportSettings;
};
```

```cpp
// MyMetaHumanController.cpp
#include "MyMetaHumanController.h"

UMyMetaHumanController::UMyMetaHumanController()
{
    ViewportSettings = NewObject<UMetaHumanViewportSettings>(this);
}

void UMyMetaHumanController::ResetViewportToDefault()
{
    if (ViewportSettings)
    {
        // 重置视图A为默认光照模式，并显示曲线
        ViewportSettings->SetViewModeIndex(EABImageViewMode::A, VMI_Lit, false);
        if (!ViewportSettings->IsShowingCurves(EABImageViewMode::A))
        {
            ViewportSettings->ToggleShowCurves(EABImageViewMode::A);
        }
        // 其他重置逻辑...
        ViewportSettings->NotifySettingsChanged();
    }
}
```

## 模块依赖

MetaHuman Animator 依赖众多专用模块来完成其复杂功能。要在你自己的模块中使用其功能，需要添加依赖。

| 模块 | 用途 |
|---|---|
| `MetaHumanCore` | 核心工具类、视图设置、曲线数据控制 |
| `MetaHumanIdentity` | MetaHuman 身份（面部拓扑、纹理）管理 |
| `MetaHumanPerformance` | 表演数据（捕捉的动画数据）管理 |
| `MetaHumanCaptureSource` | 捕捉数据源（如 Live Link Face）接口 |
| `MetaHumanFaceContourTracker` | 面部轮廓关键点追踪算法 |
| `MetaHumanFaceFittingSolver` | 将追踪的轮廓匹配到 MetaHuman 面部网格的求解器 |
| `MetaHumanFaceAnimationSolver` | 从匹配结果生成骨骼动画的求解器 |
| `MetaHumanPipeline` | 处理流程（Pipeline）的定义与管理 |
| `MetaHumanSequencer` | 与 Sequencer 集成，用于动画编辑和序列化 |
| `ControlRig` | 底层的动画蓝图控制系统 |
| `MeshTrackerInterface` | 网格追踪器接口，用于深度图处理 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用身体追踪时，禁用关卡序列导出功能 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复MetaHuman角色上的渲染瑕疵 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 在身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | [MHA] 为现有网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复Sequencer的缓存问题 |

### 维护评价

MetaHuman Animator 处于**积极维护**状态。它是 Epic Games 用于推动 MetaHuman 技术的核心工具之一。从近期的 git 历史看，更新非常频繁（几乎每日），内容集中在功能增强（如身体追踪集成）、渲染质量改进和关键 bug 修复上。

**优点**：
- 由 Epic 官方维护，长期支持有保障。
- 功能完整，涵盖从捕捉到最终输出的全流程。
- 与 UE5 编辑器深度集成，提供专业的 UI 工具。

**注意**：
- 这是一个极其复杂和庞大的插件，学习曲线较陡峭。
- 高度依赖特定的硬件（如 iPhone 的 TrueDepth 摄像头）和 Epic 的云服务（用于生成初始的 MetaHuman 资产）。
- 部分模块（如 `MetaHumanPipeline`）是 Runtime 类型，但其使用场景多为编辑器内处理。

**推荐使用**：如果你的项目需要制作高质量的数字人动画，且目标平台和硬件支持 MetaHuman 工作流，那么强烈推荐使用此插件。它是目前 UE 生态中功能最强大的官方数字人动画解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [MetaHuman 官方文档](https://docs.unrealengine.com/5.0/en-US/metahuman-unreal-engine-documentation/)