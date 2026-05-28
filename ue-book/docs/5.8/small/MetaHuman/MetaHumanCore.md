# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | 超写实角色动画器 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（运行时模块、编辑器模块、测试资源） |
| 模块 | `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MeshTrackerInterface` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-04-07 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是一个完整的 MetaHuman 角色动画制作解决方案，旨在将真实的面部表演数据转化为高质量的数字角色动画。该插件提供从原始视频捕捉到最终动画输出的全流程工具链，解决了以下核心问题：

1. **面部追踪与轮廓提取**：通过 `MetaHumanFaceContourTracker` 从视频中提取面部特征点和轮廓
2. **动画求解**：使用 `MetaHumanFaceAnimationSolver` 将追踪数据转化为面部骨骼动画
3. **身份与拓扑适配**：通过 `MetaHumanIdentity` 将动画适配到不同的 MetaHuman 角色
4. **流程自动化**：`MetaHumanBatchProcessor` 支持批量处理多个动画序列
5. **实时预览与调试**：提供视口工具和双视图对比功能，方便动画师调整

该插件的核心价值在于提供了一个专业级的面部动画管线，使用户能够快速将真实表演转化为逼真的数字角色动画。

## 使用场景

- **影视动画制作**：将演员的面部表演直接驱动数字角色
- **游戏开发**：为游戏角色创建逼真的面部动画
- **虚拟主播/VTuber**：实时驱动虚拟角色面部表情
- **广告制作**：快速生成品牌代言人的数字分身动画
- **教育培训**：创建虚拟教师或讲解员的面部动画

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetViewModeIndex` | 获取指定视图的渲染模式索引 | `UMetaHumanViewportSettings` |
| `SetViewModeIndex` | 设置指定视图的渲染模式 | `UMetaHumanViewportSettings` |
| `ToggleShowCurves` | 切换曲线显示/隐藏状态 | `UMetaHumanViewportSettings` |
| `IsShowingCurves` | 查询曲线是否显示 | `UMetaHumanViewportSettings` |
| `ToggleSkeletalMeshVisibility` | 切换骨骼网格体可见性 | `UMetaHumanViewportSettings` |
| `IsSkeletalMeshVisible` | 查询骨骼网格体是否可见 | `UMetaHumanViewportSettings` |
| `ToggleFootageVisibility` | 切换原始素材可见性 | `UMetaHumanViewportSettings` |
| `ToggleDepthMeshVisibility` | 切换深度网格可见性 | `UMetaHumanViewportSettings` |
| `GetContourData` | 获取轮廓数据对象 | `FMetaHumanCurveDataController` |
| `SetCurveSelection` | 设置曲线选择状态 | `FMetaHumanCurveDataController` |
| `MoveSelectedPoint` | 移动选中的控制点 | `FMetaHumanCurveDataController` |

### 使用示例（蓝图描述）

在蓝图中创建一个 MetaHuman 动画工作流程：

1. **初始化阶段**：
   - 从 `UMetaHumanViewportSettings` 获取视口设置对象
   - 调用 `SetViewModeIndex` 设置视图模式为 `VMI_Lit`
   - 调用 `ToggleSkeletalMeshVisibility` 显示骨骼网格体

2. **数据处理阶段**：
   - 通过 `FMetaHumanCurveDataController` 加载轮廓数据
   - 调用 `InitializeContoursFromConfig` 从配置文件初始化曲线
   - 调用 `UpdateFromContourData` 更新追踪数据

3. **交互编辑阶段**：
   - 调用 `SetCurveSelection` 选择需要编辑的曲线
   - 调用 `MoveSelectedPoint` 根据用户输入移动控制点
   - 调用 `TriggerContourUpdate` 触发视图更新

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanViewportSettings.h"
#include "MetaHumanCurveDataController.h"
#include "MetaHumanContourData.h"
```

### 基本用法

从测试用例中提取的典型用法示例：

```cpp
// 1. 创建并配置视口设置
UMetaHumanViewportSettings* ViewportSettings = NewObject<UMetaHumanViewportSettings>();
ViewportSettings->SetViewModeIndex(EABImageViewMode::A, VMI_Lit, true);
ViewportSettings->ToggleShowCurves(EABImageViewMode::A);
ViewportSettings->SetEV100(EABImageViewMode::A, 1.5f, true);

// 2. 管理轮廓数据
UMetaHumanContourData* ContourData = NewObject<UMetaHumanContourData>();
ContourData->SetContourDataForDrawing(DrawDataMap);
ContourData->SetFullCurveContourDataForDrawing(FullDrawDataMap);

// 3. 使用曲线数据控制器
FMetaHumanCurveDataController CurveController(ContourData, ECurveDisplayMode::Editing);
CurveController.InitializeContoursFromConfig(DefaultContourData, "1.0.0");
CurveController.UpdateFromContourData(TrackingData, true);

// 4. 查询和修改控制点
TArray<FControlVertex> Vertices = ContourData->GetControlVerticesForCurve("FaceContour");
FControlVertex* Vertex = ContourData->GetControlVertexFromPointId(PointId);
if (Vertex && ContourData->ControlVertexIsVisible(*Vertex))
{
    // 移动控制点
    CurveController.MoveSelectedPoint(NewPosition, PointId);
}
```

### 进阶用法

结合多个模块的高级工作流：

```cpp
// 1. 加载和校准相机数据
UCameraCalibration* Calibration = LoadLiveLinkFaceCameraCalibration(
    UCameraCalibration::StaticClass(),
    GetTransientPackage(),
    "CameraCalibration",
    RF_NoFlags,
    "CalibrationData.json"
);

// 2. 初始化形状注释系统
FShapeAnnotationWrapper ShapeAnnotation;
TMap<FString, TArray<FVector2D>> SplineData = 
    ShapeAnnotation.GetDrawingSplinesFromContourData(ContourData);

// 3. 版本兼容性检查
FString Version = FMetaHumanContourDataVersion::GetContourDataVersionString();
ECompatibilityResult CompatResult;
TArray<FString> VersionList = {Version, "1.2.0"};
FMetaHumanContourDataVersion::CheckVersionCompatibility(VersionList, CompatResult);

// 4. DNA 兼容性验证
IDNAReader* ReaderA = /* 获取DNA读取器A */;
IDNAReader* ReaderB = /* 获取DNA读取器B */;
bool bCompatible = FDNAUtilities::CheckCompatibility(
    ReaderA, ReaderB, EDNARigCompatiblityFlags::All
);

// 5. RHI 兼容性检查
if (FMetaHumanSupportedRHI::IsSupported())
{
    FText SupportedNames = FMetaHumanSupportedRHI::GetSupportedRHINames();
    // 显示支持的 RHI 列表
}
```

## Demo 示例

以下是一个完整的 MetaHuman 动画工作流示例：

### MetaHumanAnimatorDemo.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "MetaHumanViewportSettings.h"
#include "MetaHumanCurveDataController.h"
#include "MetaHumanContourData.h"

class FMetaHumanAnimatorDemo
{
public:
    void InitializeDemo();
    void ProcessTrackingData(const FFrameTrackingContourData& TrackingData);
    void ToggleViewOptions();
    void ExportAnimationData();
    
private:
    UPROPERTY()
    TObjectPtr<UMetaHumanViewportSettings> ViewportSettings;
    
    UPROPERTY()
    TObjectPtr<UMetaHumanContourData> ContourData;
    
    TUniquePtr<FMetaHumanCurveDataController> CurveController;
    
    // 调试计数器
    int32 ProcessedFrames = 0;
};
```

### MetaHumanAnimatorDemo.cpp

```cpp
#include "MetaHumanAnimatorDemo.h"

void FMetaHumanAnimatorDemo::InitializeDemo()
{
    // 1. 初始化视口设置
    ViewportSettings = NewObject<UMetaHumanViewportSettings>();
    ViewportSettings->SetViewModeIndex(EABImageViewMode::ABSplit, VMI_Lit, false);
    ViewportSettings->ToggleShowCurves(EABImageViewMode::A);
    ViewportSettings->ToggleShowControlVertices(EABImageViewMode::B);
    
    // 2. 初始化轮廓数据
    ContourData = NewObject<UMetaHumanContourData>();
    
    // 3. 初始化曲线控制器
    CurveController = MakeUnique<FMetaHumanCurveDataController>(
        ContourData, 
        ECurveDisplayMode::Editing
    );
    
    // 4. 加载配置数据
    FFrameTrackingContourData DefaultData;
    // ... 填充默认数据 ...
    CurveController->InitializeContoursFromConfig(DefaultData, "1.0.0");
    
    UE_LOG(LogMetaHumanCore, Log, TEXT("MetaHuman Animator Demo 已初始化"));
}

void FMetaHumanAnimatorDemo::ProcessTrackingData(
    const FFrameTrackingContourData& TrackingData)
{
    // 更新追踪数据
    CurveController->UpdateFromContourData(TrackingData, true);
    
    // 自动选择所有曲线进行可视化
    TSet<FString> AllCurves;
    for (const auto& Pair : TrackingData.TrackingContours)
    {
        AllCurves.Add(Pair.Key);
    }
    CurveController->SetCurveSelection(AllCurves, true);
    
    // 统计处理帧数
    ProcessedFrames++;
    UE_LOG(LogMetaHumanCore, Log, 
        TEXT("已处理第 %d 帧，包含 %d 条曲线"), 
        ProcessedFrames, 
        TrackingData.TrackingContours.Num());
}

void FMetaHumanAnimatorDemo::ToggleViewOptions()
{
    // 切换 A/B 视图的不同显示选项
    ViewportSettings->ToggleSkeletalMeshVisibility(EABImageViewMode::A);
    ViewportSettings->ToggleFootageVisibility(EABImageViewMode::B);
    ViewportSettings->ToggleDepthMeshVisibility(EABImageViewMode::ABSplit);
    
    // 切换视图模式
    EViewModeIndex CurrentMode = ViewportSettings->GetViewModeIndex(EABImageViewMode::A);
    if (CurrentMode == VMI_Lit)
    {
        ViewportSettings->SetViewModeIndex(EABImageViewMode::A, VMI_Unlit, true);
    }
    else
    {
        ViewportSettings->SetViewModeIndex(EABImageViewMode::A, VMI_Lit, true);
    }
    
    UE_LOG(LogMetaHumanCore, Log, TEXT("视图选项已切换"));
}

void FMetaHumanAnimatorDemo::ExportAnimationData()
{
    // 获取最终动画数据
    TMap<FString, TArray<FVector2D>> FullData = 
        ContourData->GetTrackingContourDataForDrawing();
    
    // 获取选定曲线的简化数据
    TSet<FString> SelectedCurves = ContourData->GetSelectedCurves();
    for (const FString& CurveName : SelectedCurves)
    {
        TArray<FControlVertex> Vertices = 
            ContourData->GetControlVerticesForCurve(CurveName);
        
        UE_LOG(LogMetaHumanCore, Log, 
            TEXT("曲线 '%s' 包含 %d 个控制点"), 
            *CurveName, Vertices.Num());
    }
    
    UE_LOG(LogMetaHumanCore, Log, 
        TEXT("动画数据已导出，共 %d 条曲线"), 
        FullData.Num());
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | MetaHuman 核心技术库，提供基础算法和数据处理 |
| `SkeletalMeshUtilitiesCommon` | 骨骼网格体工具函数 |
| `ControlRigDeveloper` | 控制绑定开发工具 |
| `MetaHumanSDKEditor` | MetaHuman SDK 编辑器集成 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 禁用身体追踪时的关卡序列导出功能 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 渲染伪影问题 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | [MHA] 为现有网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复序列器缓存问题 |

### 维护评价

MetaHuman Animator 是一个**活跃维护**的插件，具有以下特点：

1. **近期活跃度**：最近一周内有5次提交，说明开发团队正在积极维护
2. **持续改进**：最新的提交集中在修复渲染问题、优化身体追踪和增强序列器功能
3. **功能增强**：正在添加新的导出功能（为现有网格体导出动画序列）
4. **稳定性优先**：多个提交专注于修复缓存和渲染问题

**推荐使用**：该插件适合需要高质量面部动画的专业项目，特别是影视和游戏开发领域。由于是官方维护，与 MetaHuman 生态系统深度集成，长期支持有保障。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/en-US/Plugins/MetaHuman/)（MetaHuman 整体文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Tests)