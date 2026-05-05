# Camera Calibration Core

> Supports lens distortion and camera calibration.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质资产、Shader） |
| 模块 | `CameraCalibrationCore` (Runtime), `CameraCalibrationCoreEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-05-27 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CameraCalibrationCore) | |

## 用途

Camera Calibration Core 是 UE5 Virtual Production 工作流的核心插件，用于**镜头标定与畸变校正**。它解决的核心问题是：如何将真实摄像机镜头的光学畸变特性精确地应用到虚拟摄像机上，使得 CG 内容与实拍画面完美匹配。

这个插件存在是因为在 Virtual Production（LED Volume / In-Camera VFX）场景中，必须精确知道真实镜头的畸变参数，才能让 CG 图层与实拍画面在像素级别对齐。插件提供了一套完整的镜头标定数据管理系统（LensFile）、多种畸变数学模型（Brown-Conrady、Spherical、Anamorphic）、畸变渲染管线（位移贴图 + 后处理材质），以及可扩展的标定算法框架。

插件标记为 `IsBetaVersion=true` 且 `Hidden=true`，仅在 `LiveLinkHub` 程序中可用，说明它面向专业的 Virtual Production 工作流，不是通用运行时插件。

## 使用场景

- 你在做 LED Volume / In-Camera VFX 拍摄，需要将真实镜头畸变参数应用到虚拟摄像机 → 用 Camera Calibration Core 的 LensFile 存储和评估畸变数据
- 你需要对真实镜头进行标定，获取畸变参数（K1-K6、P1-P2 等） → 用插件的标定工具框架和 Checkerboard Actor
- 你有一个已知畸变模型的镜头（如 Cooke /i、ARRI LDS），需要在运行时校正 CG 画面 → 用 LensFile 的 EvaluateDistortionData + SVE 渲染管线
- 你需要对 Anamorphic（变形宽银幕）镜头进行标定 → 用 AnamorphicLensModel（3DE4 Standard Degree 4 模型）
- 你需要在蓝图中根据 Focus/Zoom 实时查询插值后的畸变参数 → 用 ULensFile 的 BlueprintPure 函数

## 蓝图用法

### 核心节点 — ULensFile

`ULensFile` 是核心数据资产，存储了镜头在不同 Focus/Zoom 下的标定数据，并支持实时插值查询。

#### 数据查询（BlueprintPure）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `EvaluateDistortionParameters` | 给定 Focus/Zoom，返回插值后的畸变参数 | `ULensFile` |
| `EvaluateFocalLength` | 给定 Focus/Zoom，返回插值后的焦距 | `ULensFile` |
| `EvaluateImageCenterParameters` | 给定 Focus/Zoom，返回插值后的图像中心 | `ULensFile` |
| `EvaluateDistortionData` | 给定 Focus/Zoom/Filmback，计算畸变位移贴图并更新 Handler | `ULensFile` |
| `EvaluateNodalPointOffset` | 给定 Focus/Zoom，返回插值后的节点偏移 | `ULensFile` |
| `EvaluateNormalizedFocus` | 将归一化编码器值转换为实际 Focus 值 | `ULensFile` |
| `EvaluateNormalizedIris` | 将归一化编码器值转换为实际 Iris 值 | `ULensFile` |

#### 数据管理（BlueprintCallable）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddDistortionPoint` | 添加畸变标定点（含焦距信息） | `ULensFile` |
| `AddFocalLengthPoint` | 添加焦距标定点 | `ULensFile` |
| `AddImageCenterPoint` | 添加图像中心标定点 | `ULensFile` |
| `AddNodalOffsetPoint` | 添加节点偏移标定点 | `ULensFile` |
| `AddSTMapPoint` | 添加 ST Map 标定点 | `ULensFile` |
| `RemoveFocusPoint` | 移除指定类别的 Focus 点 | `ULensFile` |
| `RemoveZoomPoint` | 移除指定 Focus 下的 Zoom 点 | `ULensFile` |
| `ClearAll` | 清除所有标定数据 | `ULensFile` |
| `ClearData` | 清除指定类别的标定数据 | `ULensFile` |

#### 数据查询 — 点列表

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetDistortionPoints` | 获取所有畸变标定点 | `ULensFile` |
| `GetFocalLengthPoints` | 获取所有焦距标定点 | `ULensFile` |
| `GetSTMapPoints` | 获取所有 ST Map 标定点 | `ULensFile` |
| `GetImageCenterPoints` | 获取所有图像中心标定点 | `ULensFile` |
| `GetNodalOffsetPoints` | 获取所有节点偏移标定点 | `ULensFile` |
| `HasSamples` | 检查指定类别是否有标定数据 | `ULensFile` |
| `GetTotalPointNum` | 获取指定类别的标定点总数 | `ULensFile` |

### 核心节点 — UCameraCalibrationSubsystem

`UCameraCalibrationSubsystem` 是引擎级子系统，管理全局镜头标定状态。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetDefaultLensFile` | 获取默认 LensFile 资产 | `UCameraCalibrationSubsystem` |
| `SetDefaultLensFile` | 设置默认 LensFile 资产 | `UCameraCalibrationSubsystem` |
| `GetLensFile` | 通过 FLensFilePicker 获取 LensFile | `UCameraCalibrationSubsystem` |
| `GetRegisteredLensModel` | 根据名称获取已注册的镜头模型类 | `UCameraCalibrationSubsystem` |
| `GetCameraNodalOffsetAlgo` | 获取节点偏移算法 | `UCameraCalibrationSubsystem` |
| `GetCameraImageCenterAlgo` | 获取图像中心算法 | `UCameraCalibrationSubsystem` |
| `GetOverlayMaterial` | 获取叠加层材质 | `UCameraCalibrationSubsystem` |
| `GetCameraCalibrationStep` | 获取标定步骤 | `UCameraCalibrationSubsystem` |

### 核心节点 — ULensDistortionModelHandlerBase

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetDistortionState` | 设置畸变状态，重算 overscan 并更新材质参数 | `ULensDistortionModelHandlerBase` |
| `GetUndistortionDisplacementMap` | 获取去畸变位移贴图 | `ULensDistortionModelHandlerBase` |
| `GetDistortionDisplacementMap` | 获取畸变位移贴图 | `ULensDistortionModelHandlerBase` |
| `IsModelSupported` | 检查是否支持指定镜头模型 | `ULensDistortionModelHandlerBase` |

### 核心节点 — ACameraCalibrationCheckerboard

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Rebuild` | 重建棋盘格标定板的实例化网格组件 | `ACameraCalibrationCheckerboard` |

### 核心节点 — UCalibrationPointComponent

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetWorldLocation` | 获取指定标定点的世界坐标 | `UCalibrationPointComponent` |
| `NamespacedSubpointName` | 获取子点的命名空间名称 | `UCalibrationPointComponent` |
| `GetNamespacedPointNames` | 获取所有命名空间化的点名 | `UCalibrationPointComponent` |
| `RebuildVertices` | 重建可视化网格 | `UCalibrationPointComponent` |

### 使用示例（蓝图描述）

**查询镜头畸变参数：**
1. 获取 `UCameraCalibrationSubsystem` → 调用 `GetDefaultLensFile` 获取默认 LensFile
2. 对 LensFile 调用 `EvaluateDistortionParameters`，输入当前 Focus 和 Zoom 值
3. 输出的 `FDistortionInfo.Parameters` 数组包含插值后的畸变系数

**添加标定数据：**
1. 创建 `ULensFile` 资产，设置 `LensInfo`（镜头型号、传感器尺寸等）
2. 选择 `DataMode`（Parameters 或 STMap）
3. 对每个标定点，调用 `AddDistortionPoint`（Focus, Zoom, DistortionInfo, FocalLengthInfo）

**运行时应用畸变：**
1. 在 `ACameraActor` 上设置 `LensFile` 引用
2. 系统自动通过 `LensCalibrationCameraNode` 或 Lens Component 调用 `EvaluateDistortionData`
3. 畸变通过 `FLensDistortionSceneViewExtension` 或后处理材质渲染到画面上

## C++ 用法

### 头文件引入

```cpp
#include "CameraCalibrationSubsystem.h"
#include "LensFile.h"
#include "LensDistortionModelHandlerBase.h"
#include "SphericalLensDistortionModelHandler.h"
#include "CameraCalibrationTypes.h"
#include "LensData.h"
```

### 基本用法 — 创建和查询 LensFile

来源: `Source/CameraCalibrationCore/Private/Tests/TestDistortionMapping.cpp`

```cpp
// 创建一个新的 LensFile 对象
ULensFile* LensFile = NewObject<ULensFile>();
LensFile->LensInfo.SensorDimensions = FVector2D(36.0f, 20.25f);

// 添加畸变标定点（Focus=0, Zoom=0）
FDistortionInfo DistortionInfo;
DistortionInfo.Parameters = { 0.1f, -0.05f, 0.0f }; // K1, K2, K3
FFocalLengthInfo FocalLengthInfo;
FocalLengthInfo.FxFy = FVector2D(1.0f, 1.0f);
LensFile->AddDistortionPoint(0.0f, 0.0f, DistortionInfo, FocalLengthInfo);

// 添加更多标定点
LensFile->AddDistortionPoint(0.0f, 0.5f, DistortionInfo, FocalLengthInfo);
LensFile->AddDistortionPoint(1.0f, 0.0f, DistortionInfo, FocalLengthInfo);
LensFile->AddDistortionPoint(1.0f, 0.5f, DistortionInfo, FocalLengthInfo);

// 查询插值后的畸变参数
FDistortionInfo EvaluatedDistortion;
bool bSuccess = LensFile->EvaluateDistortionParameters(0.5f, 0.25f, EvaluatedDistortion);
// EvaluatedDistortion.Parameters 包含在 Focus=0.5, Zoom=0.25 处的插值结果
```

### 基本用法 — 通过 Subsystem 访问

```cpp
// 获取子系统
UCameraCalibrationSubsystem* Subsystem = GEngine->GetEngineSubsystem<UCameraCalibrationSubsystem>();

// 获取默认 LensFile
ULensFile* DefaultLensFile = Subsystem->GetDefaultLensFile();

// 查询已注册的镜头模型
TSubclassOf<ULensModel> SphericalModel = Subsystem->GetRegisteredLensModel(FName("Spherical"));

// 获取标定步骤列表
TArray<FName> CalSteps = Subsystem->GetCameraCalibrationSteps();
```

### 进阶用法 — 自定义镜头模型

要注册自定义镜头模型，需要：

1. 定义参数结构体
2. 继承 `ULensModel` 并实现纯虚函数
3. 继承 `ULensDistortionModelHandlerBase` 并实现畸变计算

```cpp
// 1. 定义参数结构体
USTRUCT(BlueprintType)
struct FMyDistortionParameters
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    float Param1 = 0.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    float Param2 = 0.0f;
};

// 2. 镜头模型类
UCLASS(BlueprintType)
class UMyLensModel : public ULensModel
{
    GENERATED_BODY()
public:
    virtual UScriptStruct* GetParameterStruct() const override { return FMyDistortionParameters::StaticStruct(); }
    virtual FName GetModelName() const override { return FName("MyLensModel"); }
    virtual FName GetShortModelName() const override { return FName("MyLens"); }
};

// 3. 畸变处理器
UCLASS()
class UMyDistortionHandler : public ULensDistortionModelHandlerBase
{
    GENERATED_BODY()
protected:
    virtual void InitializeHandler() override { LensModelClass = UMyLensModel::StaticClass(); }
    virtual FVector2D ComputeDistortedUV(const FVector2D& InScreenUV) const override { /* 畸变计算 */ }
    virtual FVector2D ComputeUndistortedUV(const FVector2D& InScreenUV) const override { /* 去畸变计算 */ }
    virtual void InitDistortionMaterials() override { /* 创建材质 */ }
    virtual void UpdateMaterialParameters() override { /* 更新材质参数 */ }
    virtual void InterpretDistortionParameters() override { /* 解析参数 */ }
};
```

### 进阶用法 — 畸变渲染模式

```cpp
// 获取畸变渲染模式
EDistortionRenderingMode Mode = Handler->GetPreferredRenderingMode();

// Mode 可以是:
// - PostProcessMaterial: 使用后处理材质（反向畸变模型的默认偏好）
// - SceneViewExtension: 使用 Scene View Extension（正向畸变模型的默认偏好，配合 TSR）
// - Preferred: 使用镜头模型的默认偏好

// 通过 Console Variable 控制 SVE 模式下的畸变时机
// r.TSR.LensDistortion = 1 → 在 TSR 阶段应用畸变（默认）
// r.TSR.LensDistortion = 0 → 在 PrimaryUpscale 阶段应用畸变
```

### 进阶用法 — 位移贴图混合

来源: `Source/CameraCalibrationCore/Public/LensFileRendering.h`

```cpp
// 位移贴图混合支持 4 种模式：
// - OneFocusOneZoom: 无混合，直接使用
// - OneFocusTwoZoom: 在两个 Zoom 点之间 Bezier 插值
// - TwoFocusOneZoom: 在两个 Focus 点之间线性插值
// - TwoFocusTwoZoom: 双 Bezier + 线性插值（最复杂）

FDisplacementMapBlendingParams BlendParams;
BlendParams.BlendType = EDisplacementMapBlendType::TwoFocusTwoZoom;
BlendParams.EvalFocus = 0.5f;
BlendParams.EvalZoom = 0.25f;
// 设置四个角的畸变状态...

// 使用 LensFileRendering 命名空间绘制混合位移贴图
LensFileRendering::DrawBlendedDisplacementMap(OutRenderTarget, BlendParams, Tex1, Tex2, Tex3, Tex4);
```

## Demo 示例

### 最小示例 — 读取和评估镜头标定数据

**Build.cs 依赖:**
```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "CameraCalibrationCore",
    "Core",
    "CoreUObject",
    "Engine"
});
```

**MyLensCalibration.h:**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "MyLensCalibration.generated.h"

class ULensFile;
struct FDistortionInfo;

UCLASS(ClassGroup=(Calibration), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMyLensCalibration : public UActorComponent
{
    GENERATED_BODY()

public:
    /** LensFile 资产引用 */
    UPROPERTY(EditAnywhere, Category = "Calibration")
    TObjectPtr<ULensFile> LensFile;

    /** 当前 Focus 值 */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Calibration")
    float CurrentFocus = 0.0f;

    /** 当前 Zoom 值 */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Calibration")
    float CurrentZoom = 0.0f;

    /** 获取当前畸变参数 */
    UFUNCTION(BlueprintCallable, Category = "Calibration")
    bool GetCurrentDistortion(FDistortionInfo& OutDistortion);

    /** 获取当前焦距 */
    UFUNCTION(BlueprintCallable, Category = "Calibration")
    bool GetCurrentFocalLength(FFocalLengthInfo& OutFocalLength);
};
```

**MyLensCalibration.cpp:**
```cpp
#include "MyLensCalibration.h"
#include "LensFile.h"
#include "LensData.h"

bool UMyLensCalibration::GetCurrentDistortion(FDistortionInfo& OutDistortion)
{
    if (!LensFile)
    {
        return false;
    }
    return LensFile->EvaluateDistortionParameters(CurrentFocus, CurrentZoom, OutDistortion);
}

bool UMyLensCalibration::GetCurrentFocalLength(FFocalLengthInfo& OutFocalLength)
{
    if (!LensFile)
    {
        return false;
    }
    return LensFile->EvaluateFocalLength(CurrentFocus, CurrentZoom, OutFocalLength);
}
```

## 模块依赖

### CameraCalibrationCore (Runtime)

| 模块 | 用途 |
|---|---|
| `CinematicCamera` | CineCameraComponent 支持，电影摄像机功能 |
| `Core` | 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `DeveloperSettings` | 项目设置（UCameraCalibrationSettings） |
| `Engine` | 引擎核心 |
| `GameplayCameras` | 摄像机节点系统（LensCalibrationCameraNode） |
| `RenderCore` | 渲染核心（RDG、Shader） |
| `RHI` | 渲染硬件接口 |
| `Slate` | UI 框架 |
| `SlateCore` | UI 核心 |
| `ProceduralMeshComponent` | 程序化网格（棋盘格标定板可视化） |
| `Json` (Private) | JSON 序列化（标定数据导入导出） |
| `LiveLinkInterface` (Private) | Live Link 接口 |
| `Projects` (Private) | 项目管理 |
| `Renderer` (Private) | 渲染器（Scene View Extension） |

### CameraCalibrationCoreEditor (Editor)

| 模块 | 用途 |
|---|---|
| `CameraCalibrationCore` | 运行时模块 |
| `Core` | 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `PlacementMode` | 放置模式（Actor 拖放到场景） |
| `PropertyEditor` | 属性面板自定义 |
| `Slate` | UI 框架 |
| `SlateCore` | UI 核心 |
| `UnrealEd` | 编辑器功能 |

## 架构概览

### 镜头模型（Lens Models）

插件内置 4 种镜头畸变模型：

| 模型 | 类 | 参数 | 说明 |
|---|---|---|---|
| Spherical | `USphericalLensModel` | K1, K2, K3, P1, P2 | OpenCV 标准球面畸变模型 |
| Brown-Conrady U-D | `UBrownConradyUDLensModel` | K1-K6, P1, P2 | 多项式除法模型（Undistorted→Distorted） |
| Brown-Conrady D-U | `UBrownConradyDULensModel` | K1-K6, P1, P2 | 同上参数，反向（Distorted→Undistorted） |
| Anamorphic | `UAnamorphicLensModel` | 12 个参数 | 3DE4 Anamorphic Standard Degree 4 模型 |

### 标定数据表（Lens Tables）

LensFile 内部包含 6 个数据表，以 Focus/Zoom 为索引存储标定数据：

| 表 | 结构体 | 说明 |
|---|---|---|
| DistortionTable | `FDistortionTable` | 畸变参数 |
| FocalLengthTable | `FFocalLengthTable` | 焦距 |
| ImageCenterTable | `FImageCenterTable` | 图像中心（主点） |
| NodalOffsetTable | `FNodalOffsetTable` | 节点偏移（位置/旋转） |
| STMapTable | `FSTMapTable` | ST Map（预计算的 UV 位移贴图） |
| EncodersTable | `FEncodersTable` | 编码器映射（Focus/Iris 归一化映射） |

### 渲染管线

畸变渲染有两条路径：

1. **PostProcessMaterial**: 通过后处理材质直接在屏幕空间应用畸变（适合反向畸变模型）
2. **SceneViewExtension**: 通过 `FLensDistortionSceneViewExtension` 在 RDG 管线中渲染位移贴图（适合正向畸变模型，可配合 TSR 优化）

位移贴图分辨率可在项目设置中配置（默认 256x256），支持 4 种混合模式以实现 Focus/Zoom 之间的平滑过渡。

### 可扩展框架

插件通过抽象基类提供可扩展的标定算法框架：

| 基类 | 用途 | 注册位置 |
|---|---|---|
| `UCameraLensDistortionAlgo` | 镜头畸变标定算法 | Lens Distortion Tool |
| `UCameraNodalOffsetAlgo` | 节点偏移标定算法 | Nodal Offset Tool |
| `UCameraImageCenterAlgo` | 图像中心标定算法 | Image Center Tool |
| `UCameraCalibrationStep` | 标定步骤（自定义工具面板） | Camera Calibration Toolkit |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-09-29 | `30323f3d` | 修复打包游戏的支持 |
| 2025-09-01 | `a0f60cdb` | 添加默认畸变渲染模式选项 |
| 2025-09-01 | `8f557b73` | 添加 Brown-Conrady D-U 模型 |

### 维护评价

- **创建时间**: 2021-05-27（约 5 年）
- **最近更新**: 2025-09-29，约 8 个月前有功能性更新
- **维护状态**: ✅ **活跃维护** — 近期添加了新的镜头模型（Brown-Conrady D-U）和渲染模式配置功能，说明仍在积极开发
- **已知限制**: 标记为 Beta，仅在 LiveLinkHub 中可用；`Hidden=true` 不会出现在常规插件列表中
- **推荐使用**: ✅ **推荐**（对于 Virtual Production 场景）— 这是 Epic 官方 VP 工作流的核心组件，持续得到维护和增强

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CameraCalibrationCore)
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/VirtualProduction/CameraCalibrationCore/Source/CameraCalibrationCore/Private/Tests/TestDistortionMapping.cpp)
