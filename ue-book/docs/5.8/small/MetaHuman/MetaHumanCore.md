# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 动画师 |
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（配置资产、蓝图资产） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-04-01 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方提供的 MetaHuman 角色动画制作工具套件。它解决的核心问题是：**将真实世界的面部捕捉数据转换为 MetaHuman 角色的高质量面部动画**。

具体来说，该插件提供了一整套从面部视频/深度数据采集、面部轮廓追踪、面部拟合求解到最终动画输出的完整管线。它支持：

- **面部捕捉数据导入**：从 Live Link Face 等应用获取面部视频和深度数据
- **面部轮廓追踪与编辑**：在视频帧上自动检测并手动调整面部特征轮廓线（contour curves），包括 Catmull-Rom 样条插值
- **面部动画求解**：将追踪数据转换为骨骼网格体的面部动画
- **面部拟合求解**：将通用 MetaHuman 模板拟合到特定人物的面部数据
- **音频驱动动画**：通过 Speech2Face 技术从音频生成面部动画
- **批量处理与管线管理**：自动化处理多个捕捉会话的数据

该插件存在是因为 MetaHuman 是 Epic 生态中数字人类创建的核心技术，而 Animator 模块是将真实演员表演映射到 MetaHuman 角色的关键桥梁。

## 使用场景

- 你拍摄了演员的面部表演视频 → 用 MetaHuman Capture Source 导入 → 用 Face Contour Tracker 追踪 → 用 Face Animation Solver 生成动画
- 你有 Live Link Face 应用的实时面部数据 → 通过 Capture Protocol Stack 接收 → 实时驱动 MetaHuman 角色
- 你需要从音频文件生成口型动画 → 用 Speech2Face 模块
- 你需要为大量捕捉数据批量生成动画 → 用 Batch Processor
- 你需要将 MetaHuman 模板适配到特定人物的面部照片 → 用 Identity + Face Fitting Solver
- 你需要在 Sequencer 中编辑和组合面部动画 → 用 MetaHuman Sequencer 模块

## 模块概览

本插件由 28 个模块组成，按功能可分为以下几大类：

### 数据采集与导入
| 模块 | 说明 |
|---|---|
| `MetaHumanCaptureSource` | 捕捉数据源管理 |
| `MetaHumanCaptureProtocolStack` | 捕捉协议栈（Live Link Face 等通信协议） |
| `MetaHumanCaptureUtils` | 捕捉工具函数库 |
| `MetaHumanCaptureDataEditor` | 捕捉数据编辑器 UI |
| `MetaHumanFootageIngest` | 视频素材摄入处理 |
| `MeshTrackerInterface` | 网格追踪器接口定义 |

### 面部追踪与求解
| 模块 | 说明 |
|---|---|
| `MetaHumanFaceContourTracker` | 面部轮廓追踪算法 |
| `MetaHumanFaceContourTrackerEditor` | 轮廓追踪编辑器 UI |
| `MetaHumanFaceAnimationSolver` | 面部动画求解器 |
| `MetaHumanFaceAnimationSolverEditor` | 动画求解器编辑器 UI |
| `MetaHumanFaceFittingSolver` | 面部拟合求解器 |
| `MetaHumanFaceFittingSolverEditor` | 拟合求解器编辑器 UI |
| `MetaHumanDepthGenerator` | 深度图生成 |

### 核心数据与配置
| 模块 | 说明 |
|---|---|
| `MetaHumanCore` | 核心数据类型、轮廓数据、视口设置、样式 |
| `MetaHumanCoreEditor` | 核心模块编辑器扩展 |
| `MetaHumanConfig` | 配置管理 |
| `MetaHumanConfigEditor` | 配置编辑器 |
| `MetaHumanIdentity` | MetaHuman 身份/角色定义与管理 |
| `MetaHumanIdentityEditor` | 身份管理编辑器 UI |
| `MetaHumanContourDataVersion` | 轮廓数据版本兼容性 |

### 动画输出与集成
| 模块 | 说明 |
|---|---|
| `MetaHumanPerformance` | 表演数据管理 |
| `MetaHumanSequencer` | Sequencer 集成（时间轴编辑） |
| `MetaHumanSpeech2Face` | 音频驱动面部动画 |
| `MetaHumanPipeline` | 处理管线框架 |

### 工具与批处理
| 模块 | 说明 |
|---|---|
| `MetaHumanToolkit` | 工具箱 UI 框架 |
| `MetaHumanBatchProcessor` | 批量数据处理 |
| `MetaHumanImageViewerEditor` | 图像查看器编辑器 |
| `MetaHumanPlatform` | 平台适配 |

## 蓝图用法

### 视口设置节点

来自 `UMetaHumanViewportSettings` 类：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetViewModeIndex` | 获取指定视图模式（A/B）的视口显示模式 | `UMetaHumanViewportSettings` |
| `SetViewModeIndex` | 设置指定视图模式的显示模式（Lit/Unlit 等） | `UMetaHumanViewportSettings` |
| `GetEV100` | 获取指定视图的曝光值 | `UMetaHumanViewportSettings` |
| `SetEV100` | 设置指定视图的曝光值 | `UMetaHumanViewportSettings` |
| `IsShowingSingleView` | 是否处于单视图模式 | `UMetaHumanViewportSettings` |
| `ToggleShowCurves` | 切换轮廓曲线显示/隐藏 | `UMetaHumanViewportSettings` |
| `IsShowingCurves` | 查询轮廓曲线是否可见 | `UMetaHumanViewportSettings` |
| `ToggleShowControlVertices` | 切换控制顶点显示/隐藏 | `UMetaHumanViewportSettings` |
| `IsShowingControlVertices` | 查询控制顶点是否可见 | `UMetaHumanViewportSettings` |
| `ToggleSkeletalMeshVisibility` | 切换骨骼网格体显示/隐藏 | `UMetaHumanViewportSettings` |
| `IsSkeletalMeshVisible` | 查询骨骼网格体是否可见 | `UMetaHumanViewportSettings` |
| `ToggleFootageVisibility` | 切换素材画面显示/隐藏 | `UMetaHumanViewportSettings` |
| `IsFootageVisible` | 查询素材画面是否可见 | `UMetaHumanViewportSettings` |
| `ToggleDepthMeshVisibility` | 切换深度网格显示/隐藏 | `UMetaHumanViewportSettings` |
| `IsDepthMeshVisible` | 查询深度网格是否可见 | `UMetaHumanViewportSettings` |
| `ToggleDistortion` | 切换畸变/去畸变显示 | `UMetaHumanViewportSettings` |
| `IsShowingUndistorted` | 查询是否显示去畸变画面 | `UMetaHumanViewportSettings` |

### 使用示例（蓝图描述）

在 MetaHuman Animator 工具的编辑器 UI 中，视口通常分为 A/B 两个视图模式：

1. 创建 `UMetaHumanViewportSettings` 对象
2. 调用 `SetViewModeIndex(EABImageViewMode::A, VMI_Lit, true)` 将 A 视图设为 Lit 模式
3. 调用 `ToggleSkeletalMeshVisibility(EABImageViewMode::A)` 在 A 视图显示骨骼网格体
4. 调用 `ToggleFootageVisibility(EABImageViewMode::B)` 在 B 视图显示原始素材
5. 通过 `SetEV100(EABImageViewMode::A, -2.0f, true)` 调整 A 视图的曝光

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanViewportSettings.h"
#include "MetaHumanContourData.h"
#include "MetaHumanCurveDataController.h"
#include "ShapeAnnotationWrapper.h"
#include "DNAUtilities.h"
```

### 基本用法：轮廓数据管理

来自 `MetaHumanContourData.h`，操作面部轮廓的控制顶点和曲线数据：

```cpp
// 获取轮廓数据对象
UMetaHumanContourData* ContourData = GetContourData();

// 获取某条轮廓曲线上的所有控制顶点（不包含端点）
TArray<FControlVertex> Vertices = ContourData->GetControlVerticesForCurve("nose_bridge");

// 获取控制顶点的位置
TArray<FVector2D> Positions = ContourData->GetControlVertexPositions("left_eyebrow");

// 获取所有选中的曲线名称
TSet<FString> SelectedCurves = ContourData->GetSelectedCurves();

// 检查某条曲线是否可见
bool bVisible = ContourData->ContourIsVisible("upper_lip");

// 获取曲线的起止点名称
TPair<FString, FString> StartEnd = ContourData->GetStartEndNamesForCurve("nose_bridge");
```

### 基本用法：曲线数据控制器

来自 `MetaHumanCurveDataController.h`，用于交互式编辑面部轮廓：

```cpp
// 创建曲线数据控制器（编辑模式）
FMetaHumanCurveDataController CurveController(ContourData, ECurveDisplayMode::Editing);

// 从配置初始化轮廓
FFrameTrackingContourData DefaultData;
CurveController.InitializeContoursFromConfig(DefaultData, TEXT("1.0"));

// 从追踪数据更新显示
FFrameTrackingContourData TrackingData = GetTrackingData();
CurveController.UpdateFromContourData(TrackingData, true);

// 移动选中的点
TSet<int32> SelectedPoints = {0, 1, 2};
FVector2D Offset(5.0f, -3.0f);
CurveController.OffsetSelectedPoints(SelectedPoints, Offset);

// 添加/移除关键点
bool bAdded = CurveController.AddRemoveKey(FVector2D(100.0f, 200.0f), "nose_bridge", true);

// 监听轮廓更新
CurveController.TriggerContourUpdate().AddLambda([]()
{
    UE_LOG(LogMetaHumanCore, Log, TEXT("Contour data updated"));
});
```

### 进阶用法：DNA 兼容性检查

来自 `DNAUtilities.h`，检查两个 MetaHuman 角色的 DNA 是否兼容：

```cpp
#include "DNAUtilities.h"

IDNAReader* DnaReaderA = GetDnaReaderA();
IDNAReader* DnaReaderB = GetDnaReaderB();

// 检查完整的 rig 兼容性（骨骼 + 网格 + LOD）
FString CompatibilityMsg;
bool bCompatible = FDNAUtilities::CheckCompatibility(
    DnaReaderA,
    DnaReaderB,
    EDNARigCompatiblityFlags::All,
    CompatibilityMsg
);

if (!bCompatible)
{
    UE_LOG(LogMetaHumanCore, Warning, TEXT("DNA incompatible: %s"), *CompatibilityMsg);
}

// 只检查骨骼兼容性
bool bJointCompatible = FDNAUtilities::CheckCompatibility(
    DnaReaderA,
    DnaReaderB,
    EDNARigCompatiblityFlags::Joint
);
```

### 进阶用法：ShapeAnnotation 样条生成

来自 `ShapeAnnotationWrapper.h`，从轮廓数据生成平滑的 Catmull-Rom 样条曲线：

```cpp
#include "ShapeAnnotationWrapper.h"

FShapeAnnotationWrapper ShapeAnnotation;

// 从轮廓数据生成绘制用的样条曲线
TMap<FString, TArray<FVector2D>> SplineData =
    ShapeAnnotation.GetDrawingSplinesFromContourData(ContourData);

// 获取特定曲线的控制顶点（用于编辑模式）
TArray<FVector2D> LandmarkData = GetLandmarkPositions();
TArray<FVector2D> ControlVerts = ShapeAnnotation.GetControlVerticesForCurve(
    LandmarkData,
    "left_eyebrow",
    ECurveDisplayMode::Editing
);
```

## Demo 示例

一个完整的、可编译的最小示例，展示如何使用 MetaHumanCore 模块的轮廓数据系统：

### MetaHumanDemoActor.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MetaHumanContourData.h"
#include "MetaHumanCurveDataController.h"
#include "MetaHumanViewportSettings.h"
#include "MetaHumanDemoActor.generated.h"

UCLASS()
class AMetaHumanDemoActor : public AActor
{
    GENERATED_BODY()

public:
    AMetaHumanDemoActor();

    virtual void BeginPlay() override;

    /** 初始化轮廓追踪数据 */
    UFUNCTION(BlueprintCallable, Category = "MetaHumanDemo")
    void InitializeContours();

    /** 模拟追踪数据更新 */
    UFUNCTION(BlueprintCallable, Category = "MetaHumanDemo")
    void SimulateTrackingUpdate();

    /** 获取可见曲线的绘制数据 */
    UFUNCTION(BlueprintCallable, Category = "MetaHumanDemo")
    TMap<FString, TArray<FVector2D>> GetVisibleCurveDrawData() const;

private:
    /** 轮廓数据对象 */
    UPROPERTY()
    TObjectPtr<UMetaHumanContourData> ContourData;

    /** 曲线数据控制器 */
    TUniquePtr<FMetaHumanCurveDataController> CurveController;

    /** 视口设置 */
    UPROPERTY()
    TObjectPtr<UMetaHumanViewportSettings> ViewportSettings;

    /** 轮廓更新回调 */
    void OnContourUpdated();
};
```

### MetaHumanDemoActor.cpp

```cpp
#include "MetaHumanDemoActor.h"
#include "MetaHumanCoreLog.h"

AMetaHumanDemoActor::AMetaHumanDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;

    // 创建轮廓数据
    ContourData = CreateDefaultSubobject<UMetaHumanContourData>(TEXT("ContourData"));

    // 创建视口设置
    ViewportSettings = CreateDefaultSubobject<UMetaHumanViewportSettings>(TEXT("ViewportSettings"));
}

void AMetaHumanDemoActor::BeginPlay()
{
    Super::BeginPlay();

    InitializeContours();

    // 配置视口：A 视图显示 Lit 模式 + 骨骼网格体
    ViewportSettings->SetViewModeIndex(EABImageViewMode::A, VMI_Lit, false);
    ViewportSettings->ToggleSkeletalMeshVisibility(EABImageViewMode::A);

    UE_LOG(LogMetaHumanCore, Log, TEXT("MetaHuman Demo Actor initialized"));
}

void AMetaHumanDemoActor::InitializeContours()
{
    // 创建曲线控制器（编辑模式）
    CurveController = MakeUnique<FMetaHumanCurveDataController>(
        ContourData,
        ECurveDisplayMode::Editing
    );

    // 注册轮廓更新回调
    CurveController->TriggerContourUpdate().AddUObject(
        this, &AMetaHumanDemoActor::OnContourUpdated
    );

    // 从默认配置初始化
    FFrameTrackingContourData DefaultContourData;
    CurveController->InitializeContoursFromConfig(DefaultContourData, TEXT("1.0"));

    UE_LOG(LogMetaHumanCore, Log, TEXT("Contours initialized from config"));
}

void AMetaHumanDemoActor::SimulateTrackingUpdate()
{
    if (!CurveController.IsValid())
    {
        return;
    }

    // 构造模拟的追踪数据
    FFrameTrackingContourData TrackingData;

    // 在实际使用中，这里会填入来自面部追踪器的真实数据
    // FTrackingContour& NoseContour = TrackingData.Add(TEXT("nose_bridge"));
    // NoseContour.DensePoints.Add(FVector2D(100.f, 200.f));
    // NoseContour.DensePoints.Add(FVector2D(105.f, 210.f));

    // 更新控制器
    CurveController->UpdateFromContourData(TrackingData, true);
}

TMap<FString, TArray<FVector2D>> AMetaHumanDemoActor::GetVisibleCurveDrawData() const
{
    if (!ContourData)
    {
        return {};
    }

    return ContourData->GetReducedDataForDrawing();
}

void AMetaHumanDemoActor::OnContourUpdated()
{
    UE_LOG(LogMetaHumanCore, Log, TEXT("Contour data updated successfully"));
}
```

## 模块依赖

以下列出各子模块的关键**非标准**依赖（Core/Engine/UMG/Slate 等常见模块已省略）：

| 模块 | 用途 |
|---|---|
| `UnrealEd` | 编辑器框架（MetaHumanCore, MetaHumanIdentity, MetaHumanPipeline 等依赖） |
| `MetaHumanCoreTechLib` | MetaHuman 核心算法库（MetaHumanConfig 依赖） |
| `SkeletalMeshUtilitiesCommon` | 骨骼网格体工具（MetaHumanIdentity 依赖） |
| `ControlRigDeveloper` | Control Rig 开发工具（MetaHumanIdentity 依赖） |
| `MetaHumanSDKEditor` | MetaHuman SDK 编辑器（MetaHumanIdentity 依赖） |
| `MetaHumanImageViewerEditor` | 图像查看器编辑器（MetaHumanCaptureDataEditor 依赖） |

**注意**：由于本插件包含 28 个模块，每个模块有各自的依赖链。使用特定子模块时，请查阅对应 Build.cs 文件获取完整依赖列表。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 启用身体追踪时禁用关卡序列导出 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 渲染瑕疵 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 为已有网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存问题 |

### 维护评价

MetaHuman Animator 是 Epic Games 官方维护的**核心数字人动画工具**，维护状态**非常活跃**：

- ✅ **持续更新**：最近一周内有 5 次提交，涵盖新功能（身体追踪集成）、Bug 修复（渲染瑕疵、缓存问题）和功能增强（动画序列导出）
- ✅ **模块化设计**：28 个模块分工明确，从数据采集到动画输出覆盖完整管线
- ✅ **跨平台支持**：支持 Win64、Linux、Mac
- ✅ **稳定版本**：`IsBetaVersion=false`，`IsExperimentalVersion=false`
- ⚠️ **复杂度高**：544 个源文件，是大型/超大型插件，学习曲线较陡
- ⚠️ **部分模块依赖外部库**：如 MetaHumanCoreTechLib，需要确认许可证和分发限制

**强烈推荐使用**：如果你的项目涉及数字人类动画制作，这是 Epic 官方支持的最佳方案，活跃维护且功能完善。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/metahuman-animator-in-unreal-engine/)（MetaHuman Animator 文档）
- [MetaHuman 官网](https://www.metahuman.unrealengine.com/)