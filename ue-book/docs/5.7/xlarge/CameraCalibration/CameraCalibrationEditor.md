# Camera Calibration

> Framework to support lens distortion and camera calibration in engine.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质、预设资产） |
| 模块 | `CameraCalibrationEditor` (Runtime), `TrackingAlignment` (Runtime), `TrackingAlignmentEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-04-29 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CameraCalibration) | |

## 用途

Camera Calibration 插件为虚幻引擎提供了一套完整的**镜头畸变校准与相机标定框架**，专为虚拟制片（Virtual Production）场景设计。

该插件解决的核心问题：

1. **镜头畸变建模**：真实摄像机镜头存在径向畸变（桶形/枕形畸变）和切向畸变，直接将 CG 内容叠加到实拍画面上会出现边缘不对齐。本插件通过 Nodal Offset、畸变网格等数学模型对镜头畸变进行精确建模。

2. **相机内参标定**：从真实摄像机的拍摄素材中提取焦距、主点偏移、畸变系数等内参（Intrinsic Parameters），使 CG 相机与实拍相机参数完全匹配。

3. **实时畸变校正/施加**：在运行时或编辑器中，将计算出的畸变参数应用到渲染管线，通过 Post Process Material 对画面进行畸变校正（去畸变）或畸变施加（使 CG 画面看起来像通过真实镜头拍摄）。

4. **跟踪对齐**：将外部动捕/跟踪系统的数据与引擎内摄像机数据对齐，确保虚拟摄像机运动与实拍摄像机运动一致。

**为什么存在**：在 LED Volume（LED 虚拟棚）拍摄和传统绿幕合成中，CG 画面必须与实拍画面在镜头畸变层面完全匹配，否则会出现明显的合成违和感。本插件将这一专业流程集成到引擎内，避免了依赖外部工具。

## 使用场景

- 你在做 **LED Volume 虚拟制片**，需要让 CG 背景与实拍画面的镜头畸变完全匹配
- 你有一段**实拍镜头素材**，需要从中提取镜头畸变参数（焦距、畸变系数等）
- 你需要在运行时对渲染画面**施加或去除镜头畸变**，用于实时合成
- 你使用**外部跟踪系统**（如 Mo-Sys、Stype 等），需要将跟踪数据与引擎摄像机对齐
- 你需要为不同镜头/焦距组合创建**畸变校准预设**，在拍摄现场快速切换

## 子模块文档

本插件包含 3 个模块，按功能拆分如下：

| 模块 | 类型 | 说明 | 文档链接 |
|---|---|---|---|
| CameraCalibrationEditor | Runtime | 核心校准框架：镜头模型、畸变参数、校准工具、渲染管线集成 | [CameraCalibrationEditor.md](CameraCalibrationEditor.md) |
| TrackingAlignment | Runtime | 跟踪数据对齐：将外部跟踪系统数据与引擎摄像机对齐 | [TrackingAlignment.md](TrackingAlignment.md) |
| TrackingAlignmentEditor | Runtime | 跟踪对齐编辑器工具：UI 面板、可视化调试 | [TrackingAlignmentEditor.md](TrackingAlignmentEditor.md) |

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetLensDistortionParameters` | 获取当前镜头的畸变参数（畸变系数 K1-K4、P1、P2） | `ULensDistortionModelHandlerBase` |
| `ApplyDistortionToSceneView` | 将畸变参数应用到场景渲染，通过 Post Process Material 施加畸变 | `UCameraCalibrationSubsystem` |
| `GetCalibratedLensFile` | 获取指定相机组件关联的校准镜头文件 | `UCameraCalibrationSubsystem` |
| `SetLensFile` | 为相机组件设置镜头校准文件 | `UCameraCalibrationSubsystem` |
| `EvaluateLensDistortion` | 在指定焦距处对镜头畸变模型求值，返回畸变参数 | `ULensFile` |
| `GetCroppedFilmback` | 获取畸变校正后的裁剪胶片背尺寸 | `ULensDistortionModelHandlerBase` |

### 使用示例（蓝图描述）

**场景：为 CineCamera 组件施加实时镜头畸变**

1. 在场景中放置一个 `CineCameraActor`
2. 通过 `UCameraCalibrationSubsystem`（GameInstance 子系统）调用 `SetLensFile`，将已校准的 `ULensFile` 资产关联到该相机
3. 在相机的 Post Process Settings 中，确保启用了插件提供的畸变 Post Process Material
4. 运行时，子系统会自动根据当前焦距从 LensFile 中插值畸变参数，并通过材质实例施加到渲染管线

**场景：从校准数据创建 LensFile 资产**

1. 在 Content Browser 中右键 → Miscellaneous → Lens File，创建 `ULensFile` 资产
2. 打开 Lens File 编辑器，导入或手动输入不同焦距下的畸变系数
3. 保存资产，后续可在运行时或编辑器中引用

## C++ 用法

### 头文件引入

```cpp
#include "CameraCalibrationSubsystem.h"
#include "LensFile.h"
#include "LensDistortionModelHandlerBase.h"
#include "CineCameraComponent.h"
```

### 基本用法

**获取相机校准子系统并关联镜头文件**

```cpp
// 来源: CameraCalibrationSubsystem.h
// 获取 CameraCalibration 子系统
UCameraCalibrationSubsystem* CalibSubsystem = GEngine->GetEngineSubsystem<UCameraCalibrationSubsystem>();

// 获取 CineCamera 组件
UCineCameraComponent* CineCamera = MyCineCameraActor->GetCineCameraComponent();

// 加载已校准的镜头文件资产
ULensFile* LensFile = LoadObject<ULensFile>(nullptr, TEXT("/Game/Calibration/MyLensFile"));

// 将镜头文件关联到相机
CalibSubsystem->SetLensFile(CineCamera, LensFile);
```

**查询畸变参数**

```cpp
// 来源: LensFile.h
// 在指定焦距处求值畸变参数
float CurrentFocalLength = CineCamera->CurrentFocalLength;
FLensDistortionParameters DistortionParams;

// 从 LensFile 中插值获取当前焦距对应的畸变参数
LensFile->EvaluateDistortionParameters(CurrentFocalLength, DistortionParams);

// DistortionParams 包含径向畸变系数 K1-K4、切向畸变系数 P1-P2 等
```

### 进阶用法

**自定义镜头畸变模型**

```cpp
// 来源: LensDistortionModelHandlerBase.h
// 插件支持可扩展的畸变模型架构
// 继承 ULensDistortionModelHandlerBase 实现自定义畸变模型

class UMyCustomDistortionHandler : public ULensDistortionModelHandlerBase
{
    GENERATED_BODY()

public:
    // 重写畸变计算逻辑
    virtual void InitializeLensDistortion(
        const ULensFile* InLensFile,
        float InFocalLength) override;

    // 重写畸变应用到渲染的逻辑
    virtual void ApplyDistortionToPostProcess(
        FPostProcessSettings& OutPostProcessSettings) override;
};
```

**跟踪对齐工作流**

```cpp
// 来源: TrackingAlignment 模块
// 将外部跟踪数据与引擎摄像机对齐
#include "TrackingAlignment.h"

// 获取跟踪对齐处理器
UTrackingAlignmentProcessor* AlignmentProcessor = 
    GetWorld()->GetSubsystem<UTrackingAlignmentSubsystem>()->GetProcessor();

// 设置外部跟踪数据源
FTransform ExternalTrackingTransform = /* 从外部跟踪系统获取 */;
AlignmentProcessor->SetExternalTrackingTransform(ExternalTrackingTransform);

// 计算对齐后的引擎摄像机变换
FTransform AlignedTransform;
AlignmentProcessor->ComputeAlignedTransform(AlignedTransform);
```

## Demo 示例

### 最小可编译示例：运行时镜头畸变施加

**MyCalibrationActor.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyCalibrationActor.generated.h"

class UCineCameraComponent;
class ULensFile;
class UCameraCalibrationSubsystem;

UCLASS()
class MYPROJECT_API AMyCalibrationActor : public AActor
{
    GENERATED_BODY()

public:
    AMyCalibrationActor();

    virtual void BeginPlay() override;

    UPROPERTY(EditAnywhere, Category = "Calibration")
    ULensFile* LensFile;

private:
    UPROPERTY(VisibleAnywhere)
    UCineCameraComponent* CineCamera;
};
```

**MyCalibrationActor.cpp**

```cpp
#include "MyCalibrationActor.h"
#include "CineCameraComponent.h"
#include "CameraCalibrationSubsystem.h"
#include "LensFile.h"
#include "Engine/Engine.h"

AMyCalibrationActor::AMyCalibrationActor()
{
    CineCamera = CreateDefaultSubobject<UCineCameraComponent>(TEXT("CineCamera"));
    RootComponent = CineCamera;
}

void AMyCalibrationActor::BeginPlay()
{
    Super::BeginPlay();

    if (LensFile)
    {
        UCameraCalibrationSubsystem* Subsystem = 
            GEngine->GetEngineSubsystem<UCameraCalibrationSubsystem>();
        
        if (Subsystem)
        {
            Subsystem->SetLensFile(CineCamera, LensFile);
        }
    }
}
```

**MyProject.Build.cs 依赖**

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Engine",
    "CameraCalibrationEditor",
    "CineCamera"
});
```

## 模块依赖

从各模块 Build.cs 提取的独特依赖（已省略标准 Core/Engine/Slate 等）：

| 模块 | 用途 |
|---|---|
| `CineCamera` | CineCamera 组件，插件的核心操作对象 |
| `MediaAssets` | 媒体纹理支持，用于将实拍视频作为校准参考 |
| `MediaUtils` | 媒体工具函数 |
| `ImageWriteQueue` | 校准结果图像导出 |
| `OpenCV` | OpenCV 计算机视觉库，用于镜头标定算法（畸变系数计算、棋盘格检测等） |
| `OpenCVHelper` | OpenCV 与 UE 类型之间的转换辅助 |
| `LevelSequence` | 级别序列支持，用于校准数据的时间线管理 |
| `MovieScene` | MovieScene 框架集成 |
| `Composure` | 合成框架（已在近期 commit 中移除依赖） |
| `RenderCore` | 底层渲染核心，用于自定义渲染通道 |
| `RHI` | 渲染硬件接口 |
| `Renderer` | 渲染器模块，用于 Post Process 集成 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2024 | `ce6ff392` | 修复 FTSTicker::RemoveTicker 的 nodiscard 警告 | 代码质量改进，适配引擎 API 变更 |
| 2024 | `3e286887` | 修复 PPM 畸变渲染模式下的裁剪错误 | Bug 修复，改善畸变渲染的视觉正确性 |
| 2024 | `7ee55960` | 移除对 Composure 的依赖，重写校准工具渲染逻辑 | 重大重构，降低了外部依赖，改用 Level Viewport Client 渲染 + Media Texture 叠加方案 |

### 维护评价

- **创建时间**：2021 年 4 月，约 4 年历史，属于较新的插件
- **实验性状态**：`IsBetaVersion=true`，API 可能在未来版本中发生变化
- **活跃度**：近期有实质性更新（重构渲染管线、移除外部依赖），表明仍在积极维护
- **已知限制**：
  - 仍标记为 Beta，生产环境使用需谨慎
  - 依赖 OpenCV 模块，可能增加包体大小
  - 畸变模型目前主要支持标准多项式模型，自定义模型需自行扩展
- **推荐程度**：⭐⭐⭐⭐ — 对于虚拟制片场景强烈推荐，是 Epic 官方维护的专业工具链。但需注意 Beta 状态，建议锁定引擎版本使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CameraCalibration)
- [官方文档]()（暂无）

---

# CameraCalibrationEditor 模块

> 核心校准框架模块：镜头畸变模型、校准参数管理、Post Process 畸变渲染管线集成

## 模块概述

CameraCalibrationEditor 是本插件的核心模块，提供：

1. **镜头文件（LensFile）资产系统**：存储和管理不同焦距下的畸变参数、投影参数、Nodal Offset 数据
2. **畸变模型处理器（Distortion Model Handler）**：可扩展的畸变计算架构，内置标准多项式模型
3. **相机校准子系统（CameraCalibrationSubsystem）**：引擎子系统，管理相机与镜头文件的关联关系
4. **Post Process 畸变渲染**：通过材质系统在渲染管线中施加/去除畸变
5. **校准工具 UI**：编辑器内的镜头校准工作流面板

## 核心类

### ULensFile

镜头文件资产，存储完整的镜头校准数据。

| 属性 | 类型 | 说明 |
|---|---|---|
| `DistortionMap` | `TMap<float, FLensDistortionPointFloatMap>` | 焦距 → 畸变参数映射表 |
| `FocalLengthRange` | `FVector2D` | 校准覆盖的焦距范围 |
| `DistortionModelType` | `ELensDistortionModel` | 使用的畸变模型类型 |

### UCameraCalibrationSubsystem

引擎子系统（`UEngineSubsystem`），管理全局相机校准状态。

| 方法 | 说明 |
|---|---|
| `SetLensFile(UCineCameraComponent*, ULensFile*)` | 为相机组件关联镜头文件 |
| `GetLensFile(UCineCameraComponent*)` | 获取相机关联的镜头文件 |
| `GetDistortionModelHandler(UCineCameraComponent*)` | 获取畸变模型处理器 |

### ULensDistortionModelHandlerBase

畸变模型处理器基类，负责实际的畸变计算和渲染集成。

| 方法 | 说明 |
|---|---|
| `InitializeLensDistortion()` | 初始化畸变参数 |
| `ApplyDistortionToPostProcess()` | 将畸变应用到 Post Process 设置 |
| `GetUndistortionDisplacementMap()` | 获取去畸变位移贴图 |
| `GetDistortionDisplacementMap()` | 获取施加畸变的位移贴图 |

## 蓝图 API

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetLensFile` | 关联镜头文件到相机 | `UCameraCalibrationSubsystem` |
| `GetLensFile` | 查询相机关联的镜头文件 | `UCameraCalibrationSubsystem` |
| `EvaluateDistortionParameters` | 在指定焦距处插值畸变参数 | `ULensFile` |
| `AddDistortionPoint` | 向镜头文件添加畸变数据点 | `ULensFile` |
| `ClearDistortionData` | 清除镜头文件中的畸变数据 | `ULensFile` |
| `GetLensDistortionHandler` | 获取畸变处理器实例 | `UCameraCalibrationSubsystem` |

## C++ 用法

### 基本用法

```cpp
// 来源: CameraCalibrationSubsystem.h
#include "CameraCalibrationSubsystem.h"
#include "LensFile.h"

// 获取子系统
UCameraCalibrationSubsystem* Subsystem = 
    GEngine->GetEngineSubsystem<UCameraCalibrationSubsystem>();

// 关联镜头文件
Subsystem->SetLensFile(MyCineCamera, MyLensFile);

// 查询畸变参数
float FocalLength = 50.0f;
FLensDistortionPointFloatMap DistortionData;
MyLensFile->GetDistortionPointAtFocalLength(FocalLength, DistortionData);
```

### 进阶用法：自定义畸变模型

```cpp
// 来源: LensDistortionModelHandlerBase.h
// 注册自定义畸变模型
UCameraCalibrationSubsystem* Subsystem = 
    GEngine->GetEngineSubsystem<UCameraCalibrationSubsystem>();

// 通过子系统注册自定义畸变模型处理器
Subsystem->RegisterDistortionModelHandler(
    UMyCustomDistortionHandler::StaticClass());
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `CineCamera` | CineCamera 组件支持 |
| `MediaAssets` | 媒体纹理，用于视频参考 |
| `OpenCV` | 镜头标定算法 |
| `OpenCVHelper` | OpenCV 类型转换 |
| `ImageWriteQueue` | 校准图像导出 |
| `RenderCore` | 渲染管线集成 |
| `RHI` | 硬件渲染接口 |

---

# TrackingAlignment 模块

> 跟踪数据对齐模块：将外部跟踪系统数据与引擎摄像机运动对齐

## 模块概述

TrackingAlignment 模块处理虚拟制片中常见的跟踪对齐问题：

1. **外部跟踪数据接收**：从 Mo-Sys、Stype、NCAM 等跟踪系统获取摄像机位姿数据
2. **坐标系转换**：将外部跟踪系统的坐标系转换为引擎坐标系
3. **对齐计算**：计算外部跟踪数据与引擎内虚拟摄像机之间的变换偏移
4. **实时对齐**：在运行时持续应用对齐变换，确保虚拟摄像机运动与实拍一致

## 核心类

### UTrackingAlignmentSubsystem

世界子系统，管理跟踪对齐的全局状态。

| 方法 | 说明 |
|---|---|
| `SetExternalTrackingTransform()` | 设置外部跟踪系统的摄像机变换 |
| `GetAlignedTransform()` | 获取对齐后的引擎摄像机变换 |
| `ComputeAlignmentOffset()` | 计算跟踪系统与引擎之间的偏移量 |
| `ResetAlignment()` | 重置对齐偏移 |

### FTrackingAlignmentData

跟踪对齐数据结构。

| 属性 | 类型 | 说明 |
|---|---|---|
| `ExternalTransform` | `FTransform` | 外部跟踪系统提供的摄像机变换 |
| `EngineTransform` | `FTransform` | 引擎内虚拟摄像机的变换 |
| `AlignmentOffset` | `FTransform` | 计算出的对齐偏移 |
| `bIsAligned` | `bool` | 是否已完成对齐 |

## 蓝图 API

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetExternalTransform` | 输入外部跟踪数据 | `UTrackingAlignmentSubsystem` |
| `GetAlignedTransform` | 获取对齐后的变换 | `UTrackingAlignmentSubsystem` |
| `ComputeAlignment` | 执行对齐计算 | `UTrackingAlignmentSubsystem` |
| `ResetAlignment` | 重置对齐 | `UTrackingAlignmentSubsystem` |
| `IsAligned` | 查询对齐状态 | `UTrackingAlignmentSubsystem` |

## C++ 用法

```cpp
// 来源: TrackingAlignment 模块
#include "TrackingAlignmentSubsystem.h"

// 获取跟踪对齐子系统
UTrackingAlignmentSubsystem* AlignmentSys = 
    GetWorld()->GetSubsystem<UTrackingAlignmentSubsystem>();

// 设置外部跟踪数据（通常每帧更新）
FTransform ExternalCamTransform = GetExternalTrackingData();
AlignmentSys->SetExternalTrackingTransform(ExternalCamTransform);

// 获取对齐后的变换应用到虚拟摄像机
FTransform AlignedTransform = AlignmentSys->GetAlignedTransform();
VirtualCamera->SetActorTransform(AlignedTransform);
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LiveLinkInterface` | Live Link 接口，用于接收外部跟踪数据流 |
| `CineCamera` | CineCamera 组件集成 |

---

# TrackingAlignmentEditor 模块

> 跟踪对齐编辑器工具：提供 UI 面板和可视化调试功能

## 模块概述

TrackingAlignmentEditor 为跟踪对齐功能提供编辑器端支持：

1. **对齐工具面板**：编辑器内的跟踪对齐配置 UI
2. **可视化调试**：在视口中显示跟踪数据、对齐偏移的可视化指示
3. **预设管理**：保存和加载跟踪对齐配置预设
4. **Live Link 集成**：编辑器内预览 Live Link 跟踪数据

## 核心功能

### 对齐工具面板

通过 Window → Virtual Production → Tracking Alignment 打开，提供：

- 外部跟踪数据源选择
- 实时对齐偏移显示
- 一键对齐/重置操作
- 对齐精度可视化

### 可视化调试

- 在视口中绘制跟踪点轨迹
- 显示外部跟踪坐标系与引擎坐标系的差异
- 对齐误差热力图

## 蓝图 API

本模块主要提供编辑器 UI，不暴露运行时蓝图 API。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `TrackingAlignment` | 运行时跟踪对齐核心逻辑 |
| `LiveLink` | Live Link 编辑器集成 |
| `LevelEditor` | 关卡编辑器集成 |