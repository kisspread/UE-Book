# Camera Calibration Core

> Supports lens distortion and camera calibration.

| 属性 | 值 |
|---|---|
| 中文名 | 镜头标定核心 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（镜头模型资产、标定模板） |
| 模块 | `CameraCalibrationCore` (Runtime), `CameraCalibrationCoreEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-05-27 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CameraCalibrationCore) | |

## 用途

CameraCalibrationCore 是虚拟制片（Virtual Production）工作流中的核心镜头标定系统，用于解决**实拍镜头画面与 CG 画面精确合成**时的镜头畸变问题。

真实摄像机镜头不可避免地会引入径向畸变、切向畸变等光学失真。当需要将 CG 元素叠加到实拍画面上时（如 LED 虚拟墙、SimulCam），必须精确建模这些畸变特征，才能让虚拟物体看起来"贴合"在实拍画面中。

本插件提供：

- **镜头畸变模型系统**：支持多种数学畸变模型（球面模型、变形镜头模型、Brown-Conrady 多项式模型等）
- **镜头标定数据管理（LensFile）**：以 Focus/Zoom 为参数的多维查找表，存储校准后的畸变参数、焦距、图像中心、节点偏移等数据
- **位移贴图（Displacement Map）渲染**：通过场景视图扩展（Scene View Extension）在渲染管线中实时应用畸变校正
- **标定工具框架**：可扩展的标定算法接口，支持棋盘格/Charuco 标定板检测

插件默认隐藏（Hidden=true），主要面向专业虚拟制片团队，通常配合 LiveLinkHub 使用。

## 使用场景

- 你在做 **LED 虚拟墙（LED Volume）** 制作 → 需要将 CG 背景与实拍镜头完美匹配，使用本插件校准镜头畸变
- 你在做 **SimulCam**（实时合成预览） → 需要实时应用镜头畸变到虚拟摄像机输出，使用 LensFile + 场景视图扩展
- 你使用 **变形镜头（Anamorphic Lens）** 拍摄 → 插件内置 Anamorphic 变形镜头畸变模型
- 你需要 **校准实体摄像机的内部参数**（焦距、图像中心、节点偏移） → 使用内置标定工具框架和棋盘格/Charuco 检测算法
- 你想 **自定义畸变模型** → 继承 `ULensModel` 和 `ULensDistortionModelHandlerBase` 实现自己的模型

## 蓝图用法

### 核心节点 — LensFile 数据操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `EvaluateDistortionParameters` | 根据 Focus/Zoom 插值获取畸变参数 | `ULensFile` |
| `EvaluateFocalLength` | 根据 Focus/Zoom 插值获取焦距 | `ULensFile` |
| `EvaluateImageCenterParameters` | 根据 Focus/Zoom 插值获取图像中心 | `ULensFile` |
| `EvaluateNodalPointOffset` | 根据 Focus/Zoom 插值获取节点偏移 | `ULensFile` |
| `EvaluateDistortionData` | 根据 Focus/Zoom 计算畸变数据并应用到镜头处理器 | `ULensFile` |
| `AddDistortionPoint` | 添加畸变校准数据点 | `ULensFile` |
| `AddFocalLengthPoint` | 添加焦距校准数据点 | `ULensFile` |
| `AddImageCenterPoint` | 添加图像中心校准数据点 | `ULensFile` |
| `AddNodalOffsetPoint` | 添加节点偏移校准数据点 | `ULensFile` |
| `GetDistortionPoints` / `GetFocalLengthPoints` | 获取所有校准数据点 | `ULensFile` |

### 核心节点 — 子系统管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetDefaultLensFile` / `SetDefaultLensFile` | 获取/设置项目默认镜头文件 | `UCameraCalibrationSubsystem` |
| `GetLensFile` | 根据 Picker 获取镜头文件 | `UCameraCalibrationSubsystem` |
| `GetRegisteredLensModel` | 获取已注册的镜头畸变模型类 | `UCameraCalibrationSubsystem` |
| `GetOverlayMaterial` | 获取标定叠加材质 | `UCameraCalibrationSubsystem` |
| `GetCameraCalibrationSteps` | 获取可用的标定步骤 | `UCameraCalibrationSubsystem` |

### 核心节点 — 畸变处理器

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetDistortionState` | 更新畸变状态、重算 overscan 并设置材质参数 | `ULensDistortionModelHandlerBase` |
| `GetUndistortionDisplacementMap` | 获取去畸变位移贴图 | `ULensDistortionModelHandlerBase` |
| `GetDistortionDisplacementMap` | 获取畸变位移贴图 | `ULensDistortionModelHandlerBase` |
| `IsModelSupported` | 检查处理器是否支持指定镜头模型 | `ULensDistortionModelHandlerBase` |

### 使用示例

**添加镜头标定数据到 LensFile**：

1. 获取或创建 `ULensFile` 资产
2. 对于每个标定点（Focus/Zoom 组合），调用 `AddDistortionPoint` 传入畸变参数和焦距
3. 对于图像中心数据，调用 `AddImageCenterPoint`
4. 运行时通过 `EvaluateDistortionParameters(Focus, Zoom, OutInfo)` 获取插值结果

**设置默认镜头文件**：

1. 在项目设置的 Camera Calibration 分类中设置 `StartupLensFile`
2. 或在蓝图中调用 `Get Default Lens File` → `Set Default Lens File`

## C++ 用法

### 头文件引入

```cpp
#include "CameraCalibrationSubsystem.h"
#include "LensFile.h"
#include "LensData.h"
#include "LensDistortionModelHandlerBase.h"
```

### 基本用法 — 获取子系统并操作 LensFile

```cpp
// 获取 Camera Calibration 子系统
UCameraCalibrationSubsystem* Subsystem = GEngine->GetEngineSubsystem<UCameraCalibrationSubsystem>();

// 获取默认镜头文件
ULensFile* DefaultLensFile = Subsystem->GetDefaultLensFile();
if (DefaultLensFile)
{
    // 添加畸变校准点
    FDistortionInfo DistortionInfo;
    DistortionInfo.Parameters = {0.1f, -0.05f, 0.01f}; // K1, K2, K3 示例参数
    
    FFocalLengthInfo FocalLength;
    FocalLength.FxFy = FVector2D(1.0f, 16.0f/9.0f);
    
    DefaultLensFile->AddDistortionPoint(
        /*Focus=*/ 1500.0f,
        /*Zoom=*/ 1.0f,
        DistortionInfo,
        FocalLength
    );
    
    // 运行时插值查询
    FDistortionInfo EvaluatedDistortion;
    if (DefaultLensFile->EvaluateDistortionParameters(1500.0f, 1.0f, EvaluatedDistortion))
    {
        // 使用插值后的畸变参数
    }
    
    // 查询焦距
    FFocalLengthInfo EvaluatedFocalLength;
    if (DefaultLensFile->EvaluateFocalLength(1500.0f, 1.0f, EvaluatedFocalLength))
    {
        FVector2D FxFy = EvaluatedFocalLength.FxFy;
    }
}
```

> 来源：`Public/CameraCalibrationSubsystem.h`、`Public/LensFile.h`

### 基本用法 — 畸变处理器

```cpp
// 创建畸变处理器（通常通过 Lens Component 自动管理）
ULensDistortionModelHandlerBase* Handler = /* 从 Lens Component 获取 */;

// 设置畸变状态
FLensDistortionState NewState;
NewState.DistortionInfo.Parameters = {0.1f, -0.05f, 0.01f};
NewState.FocalLengthInfo.FxFy = FVector2D(1.0f, 16.0f/9.0f);
NewState.ImageCenter.PrincipalPoint = FVector2D(0.5f, 0.5f);

Handler->SetDistortionState(NewState);

// 获取位移贴图用于后处理
UTextureRenderTarget2D* UndistortionMap = Handler->GetUndistortionDisplacementMap();
UTextureRenderTarget2D* DistortionMap = Handler->GetDistortionDisplacementMap();

// 计算 overscan 因子
float Overscan = Handler->ComputeOverscanFactor();
Handler->SetOverscanFactor(Overscan);
```

> 来源：`Public/LensDistortionModelHandlerBase.h`

### 进阶用法 — 畸变混合（Focus/Zoom 双轴插值）

```cpp
// LensFile 支持多 Focus 点、每 Focus 点多个 Zoom 点的二维插值
ULensFile* LensFile = Subsystem->GetDefaultLensFile();

// 获取混合状态，用于场景视图扩展渲染
FDisplacementMapBlendingParams BlendState;
LensFile->GetBlendState(
    /*InFocus=*/ 1500.0f,
    /*InZoom=*/ 1.0f,
    /*InFilmback=*/ FVector2D(23.76f, 13.365f),
    BlendState
);

// 将混合状态传递给场景视图扩展
ACameraActor* CameraActor = /* 获取摄像机 */;
ULensDistortionModelHandlerBase* Handler = /* 获取处理器 */;
Subsystem->SetLensDistortionSVEState(
    CameraActor,
    BlendState,
    Handler,
    EDistortionRenderingMode::Preferred
);
```

> 来源：`Public/CameraCalibrationSubsystem.h`、`Public/LensFileRendering.h`

### 进阶用法 — 自定义镜头模型

```cpp
// 1. 定义畸变参数结构体
USTRUCT(BlueprintType)
struct FMyDistortionParameters
{
    GENERATED_BODY()
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Distortion")
    float Param1 = 0.0f;
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Distortion")
    float Param2 = 0.0f;
};

// 2. 实现镜头模型
UCLASS(BlueprintType, meta = (DisplayName = "My Custom Lens Model"))
class UMyLensModel : public ULensModel
{
    GENERATED_BODY()
public:
    virtual UScriptStruct* GetParameterStruct() const override { return FMyDistortionParameters::StaticStruct(); }
    virtual FName GetModelName() const override { return TEXT("MyCustomModel"); }
    virtual FName GetShortModelName() const override { return TEXT("MYCM"); }
};

// 3. 实现畸变处理器
UCLASS(BlueprintType)
class UMyDistortionHandler : public ULensDistortionModelHandlerBase
{
    GENERATED_BODY()
protected:
    virtual void InitializeHandler() override { LensModelClass = UMyLensModel::StaticClass(); }
    virtual FVector2D ComputeDistortedUV(const FVector2D& InScreenUV) const override { /* 畸变计算 */ return InScreenUV; }
    virtual FVector2D ComputeUndistortedUV(const FVector2D& InScreenUV) const override { /* 去畸变计算 */ return InScreenUV; }
    virtual void InitDistortionMaterials() override { /* 初始化材质 */ }
    virtual void UpdateMaterialParameters() override { /* 更新材质参数 */ }
    virtual void InterpretDistortionParameters() override { /* 解释畸变参数 */ }
};
```

> 来源：`Public/Models/SphericalLensModel.h`、`Public/Models/AnamorphicLensModel.h`

## Demo 示例

### 运行时查询镜头标定数据

```cpp
// LensFileQueryComponent.h
#pragma once
#include "Components/ActorComponent.h"
#include "LensFile.h"
#include "CameraCalibrationSubsystem.h"
#include "LensFileQueryComponent.generated.h"

UCLASS(ClassGroup=(CameraCalibration), meta=(BlueprintSpawnableComponent))
class ULensFileQueryComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, Category = "Lens")
    float CurrentFocus = 1000.0f;

    UPROPERTY(EditAnywhere, Category = "Lens")
    float CurrentZoom = 1.0f;

    UPROPERTY(BlueprintReadOnly, Category = "Lens|Result")
    FDistortionInfo LastDistortionResult;

    UPROPERTY(BlueprintReadOnly, Category = "Lens|Result")
    FFocalLengthInfo LastFocalLengthResult;

    UPROPERTY(BlueprintReadOnly, Category = "Lens|Result")
    FNodalPointOffset LastNodalOffsetResult;

    UFUNCTION(BlueprintCallable, Category = "Lens")
    bool QueryLensFile()
    {
        UCameraCalibrationSubsystem* Subsystem = GEngine->GetEngineSubsystem<UCameraCalibrationSubsystem>();
        if (!Subsystem) return false;

        ULensFile* LensFile = Subsystem->GetDefaultLensFile();
        if (!LensFile) return false;

        bool bSuccess = true;
        bSuccess &= LensFile->EvaluateDistortionParameters(CurrentFocus, CurrentZoom, LastDistortionResult);
        bSuccess &= LensFile->EvaluateFocalLength(CurrentFocus, CurrentZoom, LastFocalLengthResult);
        bSuccess &= LensFile->EvaluateNodalPointOffset(CurrentFocus, CurrentZoom, LastNodalOffsetResult);
        return bSuccess;
    }
};
```

## 模块依赖

从 Build.cs 和 .uplugin 的 Plugins 字段分析：

| 模块 | 用途 |
|---|---|
| `GameplayCameras` | 摄像机系统基础支持 |
| `ProceduralMeshComponent` | 标定板（Checkerboard/Charuco）的程序化网格生成 |
| `LiveLink` | 实时数据驱动 Focus/Zoom/Iris 输入 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `eb68c63d` | Fix crashes and data loss when opening upgraded MetaHuman identities from older UEFN versions | 修复从旧版 UEFN 升级 MetaHuman 时的崩溃和数据丢失 |
| 2026-05-13 | `057dbc69` | Fix crashes in PostEditChangeProperty overrides when MemberProperty is null, which occurs when Pytho | 修复 Python 调用时 PostEditChangeProperty 中 MemberProperty 为空导致的崩溃 |
| 2026-05-12 | `5e90bad9` | Composure: Warn when lens distortion rendering mode is not TSR | Composure 集成：镜头畸变渲染模式非 TSR 时发出警告 |
| 2026-04-15 | `2a295e97` | Removed BlockUntilGPUIdle and SubmitCommandsAndFlushGPU in place of SubmitAndBlockUntilGPUIdle | GPU 同步 API 更新：替换废弃的阻塞调用 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF | 日志宏迁移：从 UE_LOG 迁移到 UE_LOGF |

### 维护评价

- **状态**：活跃维护中 — 2026 年仍有实质性更新（API 重构、Bug 修复、渲染管线集成改进）
- **标记为实验性**：`IsBetaVersion=true`，说明 Epic 尚未将其视为稳定 API，接口可能随版本变化
- **隐藏状态**：`Hidden=true`，不在插件浏览器中显示，需要手动在 .uproject 中启用
- **程序白名单**：仅允许 LiveLinkHub 运行，说明主要面向专业虚拟制片管线
- **已知限制**：
  - 多个 API 在 5.1 中已标记 `UE_DEPRECATED`（如子系统直接管理畸变处理器的方式），迁移时需注意
  - 镜头模型处理器的管理方式从子系统级迁移到了 Lens Component 级
- **推荐度**：如果你做虚拟制片中的镜头校准工作，这是 **必用插件**。注意它仍在 beta 状态，API 可能变动。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CameraCalibrationCore)
- [官方文档]()（暂无）