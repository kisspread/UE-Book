# MetaHuman Core Tech

> The core technology behind the MetaHuman Creator and MetaHuman Animator plugins.

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 核心技术 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、数据资产） |
| 模块 | `MetaHumanBodyTrackerInterface` (Runtime), `MetaHumanCaptureData` (Runtime), `MetaHumanCoreTech` (Runtime), `MetaHumanCoreTechLib` (Runtime), `MetaHumanImageViewer` (Runtime), `MetaHumanPipelineCore` (Runtime) |
| 实验性 | 否 |
| 创建时间 | ~2021 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanCoreTechLib) | |

## 用途

MetaHumanCoreTech 是 MetaHuman Creator（云端高保真数字人创建工具）和 MetaHuman Animator（基于面部捕捉驱动数字人面部动画的工具）的底层核心库。它并非一个独立可用的功能插件，而是为上层 MetaHuman 插件提供共享基础设施的中间层。

该插件解决的核心问题包括：

- **面部/身体动画数据结构定义**：定义了 `FFrameAnimationData` 等核心数据结构，统一面部动画、身体动画（含 SMPLX 身体模型数据）、追踪轮廓、置信度等数据的序列化和传输格式
- **实时动画后处理**：提供 `FMetaHumanRealtimeSmoothing`（实时平滑，支持 RollingAverage 和 OneEuro 两种滤波算法）和 `FMetaHumanRealtimeCalibration`（实时校准，基于中性帧校正）等实时动画处理管线
- **数字人资产路径管理**：通过 `FMetaHumanCommonDataUtils` 集中管理 DNA 文件路径、骨骼网格体路径、ControlRig 路径、后处理动画蓝图路径等，解决 Creator 和 Animator 之间的资产路径耦合问题
- **头部坐标系转换**：`FMetaHumanHeadTransform` 提供 Mesh/Bone、Head/Root 坐标系之间的标准转换
- **图像处理工具**：提供将关键点和轮廓线绘制到图像上的工具函数（`BurnPointsIntoImage`、`BurnLineIntoImage`），用于面部追踪结果的可视化调试
- **OneEuro 滤波器**：完整实现 OneEuro 滤波算法（`FMetaHumanOneEuroFilter`），用于实时动画数据的自适应平滑

## 使用场景

- 你在开发 **MetaHuman Animator** 的自定义面部追踪管线 → 使用 `FFrameAnimationData`、`FTrackingContour` 等数据结构，以及 `FMetaHumanRealtimeSmoothing` 做后处理平滑
- 你需要对实时捕捉到的面部动画数据做 **降噪和平滑处理** → 使用 `FMetaHumanRealtimeSmoothing`（RollingAverage 或 OneEuro 算法）和 `FMetaHumanRealtimeCalibration`（中性帧校准）
- 你在编写需要 **读取 MetaHuman DNA 文件** 的工具 → 使用 `FMetaHumanCommonDataUtils::GetFaceDNAFilesystemPath()` 等静态方法获取标准路径
- 你需要将 **追踪结果可视化** 到调试图像上 → 使用 `epic::core::BurnPointsIntoImage` 和 `BurnLineIntoImage`
- 你在搭建自定义数字人渲染管线，需要做 **坐标系转换** → 使用 `FMetaHumanHeadTransform` 的 MeshToBone/BoneToMesh 等方法
- 你需要处理 **音频驱动动画** 的心情参数 → 使用 `SAudioDrivenAnimationMood` 编辑器控件

## 蓝图用法

本插件的核心功能主要面向 C++ 开发者，蓝图可直接使用的 API 较少。以下是从源码中提取的蓝图可用接口：

### 核心结构体

| 结构体 | 说明 |
|---|---|
| `FFrameAnimationData` | 单帧动画数据，包含面部动画数据（`AnimationData`）、身体动画数据（`BodyAnimationData`）、SMPLX 原始数据等 |
| `FTrackingContour` | 追踪轮廓，包含密集点集（`DensePoints`）、置信度、起止点名称、可见/激活状态 |
| `FFrameTrackingContourData` | 单帧追踪轮廓数据，按相机名称组织多个 `FTrackingContour` |
| `FMetaHumanRealtimeSmoothingParam` | 平滑参数，可选 RollingAverage（滑动平均帧数）或 OneEuro（斜率、最小截止频率） |
| `FMetaHumanMeshData` | 网格体顶点数据，分别存储面部、牙齿、左右眼的顶点数据 |

### 核心数据资产

| 资产类型 | 说明 | 所在类 |
|---|---|---|
| `UMetaHumanRealtimeSmoothingParams` | 实时平滑参数数据资产，可编辑每个属性名对应的平滑方法和参数 | `UMetaHumanRealtimeSmoothingParams` |

### 枚举类型

| 枚举 | 值 | 用途 |
|---|---|---|
| `EFrameAnimationQuality` | Undefined, Preview, Final, PostFiltered, Custom1, Custom2 | 动画质量等级 |
| `EAudioProcessingMode` | Undefined, FullFace, TongueTracking, MouthOnly | 音频处理模式 |
| `EFrameAnimationDataType` | Face, Body (位标志) | 动画数据类型标识 |
| `EMetaHumanImportDNAType` | Face, Body, Combined | DNA 导入类型 |
| `EMetaHumanRealtimeSmoothingParamMethod` | RollingAverage, OneEuro | 平滑算法选择 |

## C++ 用法

### 头文件引入

```cpp
// 核心数据结构
#include "FrameAnimationData.h"
#include "FrameTrackingContourData.h"
#include "MetaHumanMeshData.h"

// 实时处理
#include "MetaHumanRealtimeSmoothing.h"
#include "MetaHumanRealtimeCalibration.h"

// 工具类
#include "MetaHumanCommonDataUtils.h"
#include "CoreUtils.h"
#include "MetaHumanHeadTransform.h"
#include "MetaHumanOneEuroFilter.h"
```

### 基本用法 - OneEuro 滤波器

`FMetaHumanOneEuroFilter` 是一个独立的、自适应低通滤波器，速度越快时平滑越少，适合实时动画数据：

```cpp
#include "MetaHumanOneEuroFilter.h"

// 创建滤波器：(最小截止频率, 截止斜率, Delta截止频率)
FMetaHumanOneEuroFilter Filter(1.0, 0.007, 1.0);

// 逐帧过滤原始动画数据
double RawValue = GetRawAnimationValue();  // 原始数据
double DeltaTime = GetFrameDeltaTime();     // 帧间隔

double SmoothedValue = Filter.Filter(RawValue, DeltaTime);

// 动态调整参数
Filter.SetMinCutoff(0.5);    // 降低最小截止频率 → 更平滑
Filter.SetCutoffSlope(0.01); // 增大斜率 → 快速运动时更敏感
```

### 基本用法 - 实时平滑管线

`FMetaHumanRealtimeSmoothing` 对一组命名属性应用实时平滑，支持混合使用 RollingAverage 和 OneEuro：

```cpp
#include "MetaHumanRealtimeSmoothing.h"

// 从默认参数初始化（或从 UMetaHumanRealtimeSmoothingParams 数据资产加载）
TMap<FName, FMetaHumanRealtimeSmoothingParam> Params = 
    FMetaHumanRealtimeSmoothing::GetDefaultSmoothingParams();

// 自定义某个属性的平滑方法
FMetaHumanRealtimeSmoothingParam CustomParam;
CustomParam.Method = EMetaHumanRealtimeSmoothingParamMethod::OneEuro;
CustomParam.OneEuroSlope = 3000;
CustomParam.OneEuroMinCutoff = 3;
Params.Add(FName("jawOpen"), CustomParam);

// 创建平滑器实例
FMetaHumanRealtimeSmoothing Smoother(Params);

// 逐帧处理
TArray<FName> PropertyNames;
TArray<float> FrameData;
// ... 从追踪管线填充 PropertyNames 和 FrameData ...

double DeltaTime = GetFrameDeltaTime();
bool bSuccess = Smoother.ProcessFrame(PropertyNames, FrameData, DeltaTime);
```

### 基本用法 - 实时校准

`FMetaHumanRealtimeCalibration` 基于中性表情帧对后续动画数据做校正：

```cpp
#include "MetaHumanRealtimeCalibration.h"

// 获取默认校准属性列表
TArray<FName> Properties = FMetaHumanRealtimeCalibration::GetDefaultProperties();

// 记录中性表情帧
TArray<float> NeutralFrame = CaptureNeutralPose(Properties);

// 创建校准器：(属性列表, 中性帧, 混合系数)
FMetaHumanRealtimeCalibration Calibration(Properties, NeutralFrame, 0.8f);

// 对每帧动画数据应用校准
TArray<float> FrameData;
TArray<FName> FramePropertyNames;
// ... 填充数据 ...

Calibration.ProcessFrame(FramePropertyNames, FrameData);

// 动态更新参数
Calibration.SetAlpha(0.5f);                   // 调整校准强度
Calibration.SetNeutralFrame(NewNeutralFrame);  // 更新中性帧
```

### 基本用法 - 头部坐标系转换

```cpp
#include "MetaHumanHeadTransform.h"

// 骨骼空间 → 网格体空间
FTransform BoneTransform = GetBoneTransform();
FTransform MeshTransform = FMetaHumanHeadTransform::BoneToMesh(BoneTransform);

// 网格体空间 → 骨骼空间
FTransform BackToBone = FMetaHumanHeadTransform::MeshToBone(MeshTransform);

// 头部空间 → 根骨骼空间
FTransform HeadTransform = GetHeadPose();
FTransform RootTransform = FMetaHumanHeadTransform::HeadToRoot(HeadTransform);
```

### 基本用法 - 图像可视化调试

```cpp
#include "CoreUtils.h"

// 将追踪关键点绘制到调试图像
TArray<FVector2D> TrackedPoints;
// ... 从追踪器获取点 ...

int32 ImageWidth = 1920;
int32 ImageHeight = 1080;
TArray<uint8> ImageData;
ImageData.SetNum(ImageWidth * ImageHeight * 4);  // RGBA

// 用红色绘制关键点，点半径为 3 像素，开启抗锯齿
epic::core::BurnPointsIntoImage(
    TrackedPoints, ImageWidth, ImageHeight, ImageData,
    255, 0, 0, 3, true);

// 绘制轮廓线段
epic::core::BurnLineIntoImage(
    StartPoint, EndPoint, ImageWidth, ImageHeight, ImageData,
    0, 255, 0, 2, true);
```

### 进阶用法 - 完整的实时动画处理管线

将平滑、校准和坐标转换组合成完整的面部动画后处理管线：

```cpp
#include "MetaHumanRealtimeSmoothing.h"
#include "MetaHumanRealtimeCalibration.h"
#include "MetaHumanHeadTransform.h"
#include "FrameAnimationData.h"

class FFaceAnimationPipeline
{
public:
    void Initialize(const TArray<FName>& InProperties, const TArray<float>& InNeutralFrame)
    {
        // 初始化平滑器
        Smoother = MakeUnique<FMetaHumanRealtimeSmoothing>(
            FMetaHumanRealtimeSmoothing::GetDefaultSmoothingParams());
        
        // 初始化校准器
        Calibrator = MakeUnique<FMetaHumanRealtimeCalibration>(
            InProperties, InNeutralFrame, 1.0f);
        
        Properties = InProperties;
    }

    FFrameAnimationData ProcessFrame(
        const FFrameAnimationData& InRawFrame, 
        double InDeltaTime)
    {
        FFrameAnimationData Output = InRawFrame;
        
        // Step 1: 从原始数据提取浮点值
        TArray<float> Values;
        for (const FName& Prop : Properties)
        {
            if (float* Val = InRawFrame.RawAnimationData.Find(Prop.ToString()))
            {
                Values.Add(*Val);
            }
        }
        
        // Step 2: 校准（去除中性姿态偏移）
        Calibrator->ProcessFrame(Properties, Values);
        
        // Step 3: 实时平滑
        Smoother->ProcessFrame(Properties, Values, InDeltaTime);
        
        // Step 4: 写回动画数据
        for (int32 i = 0; i < Properties.Num(); ++i)
        {
            Output.AnimationData.Add(Properties[i].ToString(), Values[i]);
        }
        
        return Output;
    }

private:
    TUniquePtr<FMetaHumanRealtimeSmoothing> Smoother;
    TUniquePtr<FMetaHumanRealtimeCalibration> Calibrator;
    TArray<FName> Properties;
};
```

### 基本用法 - DNA 路径获取

```cpp
#include "MetaHumanCommonDataUtils.h"

// 获取面部 DNA 文件路径
FString FaceDNAPath = FMetaHumanCommonDataUtils::GetFaceDNAFilesystemPath();

// 获取身体 DNA 文件路径
FString BodyDNAPath = FMetaHumanCommonDataUtils::GetBodyDNAFilesystemPath();

// 根据导入类型获取 DNA 路径
FString Path = FMetaHumanCommonDataUtils::GetArchetypeDNAPath(
    EMetaHumanImportDNAType::Combined);

// 获取 Animator 插件中的面部骨骼路径（用于跨插件引用）
FStringView FaceSkelPath = FMetaHumanCommonDataUtils::GetAnimatorPluginFaceSkeletonPath();
FStringView FaceControlRigPath = FMetaHumanCommonDataUtils::GetAnimatorPluginFaceControlRigPath();

// 从资产注册表获取 ControlRig
TSoftObjectPtr<UObject> ControlRig = 
    FMetaHumanCommonDataUtils::GetDefaultControlRigFromRegistry(FaceControlRigPath);

// 设置后处理动画蓝图
USkeletalMesh* SkelMesh = GetSkeletalMesh();
FMetaHumanCommonDataUtils::SetPostProcessAnimBP(SkelMesh, ABPPackageName);
```

## Demo 示例

### 实时动画平滑器的完整使用示例

```cpp
// MetaHumanSmoothingDemo.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MetaHumanRealtimeSmoothing.h"
#include "MetaHumanRealtimeCalibration.h"
#include "FrameAnimationData.h"
#include "MetaHumanSmoothingDemo.generated.h"

UCLASS()
class AMetaHumanSmoothingDemo : public AActor
{
    GENERATED_BODY()

public:
    AMetaHumanSmoothingDemo();

    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

    /** 是否已完成中性帧校准 */
    UPROPERTY(BlueprintReadOnly, Category = "MetaHuman")
    bool bIsCalibrated = false;

    /** 当前处理后的动画数据 */
    UPROPERTY(BlueprintReadOnly, Category = "MetaHuman")
    TMap<FString, float> SmoothedAnimationData;

    /** 使用默认参数初始化并开始校准 */
    UFUNCTION(BlueprintCallable, Category = "MetaHuman")
    void InitializeWithDefaults();

    /** 使用中性帧数据完成校准 */
    UFUNCTION(BlueprintCallable, Category = "MetaHuman")
    void CalibrateWithNeutralFrame(const TMap<FString, float>& InNeutralPose);

    /** 提供一帧原始数据并获取平滑后的结果 */
    UFUNCTION(BlueprintCallable, Category = "MetaHuman")
    TMap<FString, float> ProcessRawFrame(
        const TMap<FString, float>& InRawFrame, 
        float InDeltaTime);

private:
    TUniquePtr<FMetaHumanRealtimeSmoothing> Smoother;
    TUniquePtr<FMetaHumanRealtimeCalibration> Calibrator;
    TArray<FName> PropertyNames;
    bool bInitialized = false;
};
```

```cpp
// MetaHumanSmoothingDemo.cpp
#include "MetaHumanSmoothingDemo.h"

AMetaHumanSmoothingDemo::AMetaHumanSmoothingDemo()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AMetaHumanSmoothingDemo::BeginPlay()
{
    Super::BeginPlay();
    InitializeWithDefaults();
}

void AMetaHumanSmoothingDemo::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    // Tick 中不自动处理，通过蓝图调用 ProcessRawFrame 按需处理
}

void AMetaHumanSmoothingDemo::InitializeWithDefaults()
{
    // 从默认参数构建平滑器
    TMap<FName, FMetaHumanRealtimeSmoothingParam> Params = 
        FMetaHumanRealtimeSmoothing::GetDefaultSmoothingParams();
    Smoother = MakeUnique<FMetaHumanRealtimeSmoothing>(Params);

    // 获取默认校准属性
    PropertyNames = FMetaHumanRealtimeCalibration::GetDefaultProperties();

    bInitialized = true;
    bIsCalibrated = false;
}

void AMetaHumanSmoothingDemo::CalibrateWithNeutralFrame(
    const TMap<FString, float>& InNeutralPose)
{
    if (!bInitialized) return;

    // 将中性帧 TMap 转为有序数组
    TArray<float> NeutralValues;
    NeutralValues.Reserve(PropertyNames.Num());
    for (const FName& Prop : PropertyNames)
    {
        const float* Val = InNeutralPose.Find(Prop.ToString());
        NeutralValues.Add(Val ? *Val : 0.0f);
    }

    // 创建校准器，Alpha=1.0 表示完全校准
    Calibrator = MakeUnique<FMetaHumanRealtimeCalibration>(
        PropertyNames, NeutralValues, 1.0f);

    bIsCalibrated = true;
}

TMap<FString, float> AMetaHumanSmoothingDemo::ProcessRawFrame(
    const TMap<FString, float>& InRawFrame, 
    float InDeltaTime)
{
    TMap<FString, float> Result;

    if (!bInitialized || !Smoother)
    {
        return InRawFrame;
    }

    // 提取有序数据
    TArray<float> FrameValues;
    FrameValues.Reserve(PropertyNames.Num());
    for (const FName& Prop : PropertyNames)
    {
        const float* Val = InRawFrame.Find(Prop.ToString());
        FrameValues.Add(Val ? *Val : 0.0f);
    }

    // Step 1: 校准（如果已完成校准）
    if (Calibrator)
    {
        Calibrator->ProcessFrame(PropertyNames, FrameValues);
    }

    // Step 2: 平滑
    Smoother->ProcessFrame(PropertyNames, FrameValues, (double)InDeltaTime);

    // 写回结果
    for (int32 i = 0; i < PropertyNames.Num(); ++i)
    {
        Result.Add(PropertyNames[i].ToString(), FrameValues[i]);
    }

    SmoothedAnimationData = Result;
    return Result;
}
```

## 模块依赖

从各模块的 Build.cs 提取的依赖关系：

| 模块 | 用途 |
|---|---|
| `MetaHumanImageViewer` | 面部图像查看器（MetaHumanCaptureData 依赖） |
| `DirectoryWatcher` | 文件目录监视，用于监控捕捉数据文件变化 |
| `OpenCVHelper` | OpenCV 辅助库，图像处理基础功能 |
| `OpenCV` | OpenCV 计算机视觉库，用于面部追踪和图像处理 |
| `OnlineSubsystem` | 在线子系统，可能用于 MetaHuman Creator 的云端通信 |

> 注意：`UnrealEd` 出现在 Runtime 模块（MetaHumanCoreTechLib、MetaHumanPipelineCore）的依赖中，通常通过 `#if WITH_EDITOR` 条件编译隔离编辑器功能。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `7f10fbf1` | [MetaHuman] Titan v9.0.8 | MetaHuman Titan 引擎升级至 v9.0.8 |
| 2026-05-26 | `cfa3dac6` | [MetaHuman] Titan v9.0.7 | MetaHuman Titan 引擎升级至 v9.0.7 |
| 2026-05-21 | `e936df4b` | [MetaHuman] Titan v9.0.6 | MetaHuman Titan 引擎升级至 v9.0.6 |
| 2026-05-20 | `c5214fb2` | [MetaHumanBodyTracker] allow foot-locking to be toggled on or off | 身体追踪器新增脚部锁定开关功能 |
| 2026-05-19 | `a29cddd9` | [MHA] Crash during MHC assembly with body performance | 修复 MetaHuman Creator 组装时身体性能相关的崩溃 |

### 维护评价

**活跃维护** — 该插件处于高度活跃的开发状态。

- **更新频率**：近一周内有多次 Titan 引擎版本迭代（v9.0.6→v9.0.8），说明底层渲染/处理引擎在持续升级
- **内容性质**：更新涵盖核心引擎升级、身体追踪功能增强（脚部锁定）、以及关键崩溃修复
- **重要性**：作为 MetaHuman Creator 和 Animator 两大产品的共享底层库，Epic 将持续投入维护
- **依赖风险**：依赖 OpenCV 等第三方库，以及 UnrealEd（Runtime 模块中），需要注意版本兼容性
- **使用建议**：该插件默认未启用（`EnabledByDefault=false`），且主要面向 MetaHuman 生态内部使用。普通开发者通常通过 MetaHuman Creator 或 MetaHuman Animator 插件间接使用此库，而非直接集成。如果你正在开发与 MetaHuman 兼容的自定义面部追踪或动画管线，可以直接引用此插件获取标准化的数据结构和后处理工具

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanCoreTechLib)
- [官方文档]()（未提供）