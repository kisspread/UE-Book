# OpenCV Lens Distortion

> Plugin to handle camera calibration and lens distortion/undistortion displacement map generation using OpenCV.

| 属性 | 值 |
|---|---|
| 中文名 | OpenCV镜头畸变 |
| 分类 | Compositing |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `OpenCVLensCalibration` (Runtime), `OpenCVLensDistortion` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 🏛️ 文物（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Compositing/OpenCVLensDistortion) | |

## 用途

这个插件的核心功能是**解决真实摄像机镜头畸变的数字模拟与校正问题**。它利用 OpenCV 计算机视觉库，将真实摄像机拍摄画面中的镜头畸变（如桶形畸变、枕形畸变）以数学模型的形式进行描述和处理。

具体来说，它解决了以下两个关键问题：
1.  **镜头畸变建模**：通过输入真实摄像机的标定参数（焦距、主点、畸变系数等），精确建立镜头畸变的数学模型。
2.  **生成位移贴图**：基于该模型，计算出两张关键的 UV 位移贴图：
    *   **畸变到校正（Undistort）贴图**：用于将带有畸变的实时视频画面映射到校正后的画面。
    *   **校正到畸变（Distort）贴图**：用于将计算机生成的（CG）无畸变图像“扭曲”成带有真实镜头畸变效果的画面，以与真实视频无缝合成。

它的存在是为了在**虚拟制作、增强现实（AR）**等需要精确融合计算机图形与真实摄像机画面的场景中，提供开箱即用的、基于行业标准（OpenCV）的解决方案。

## 使用场景

-   你正在制作一部使用**虚拟制作**技术的电影，需要将 LED 屏幕上显示的 CG 背景与前景演员镜头完美匹配，包括模拟真实摄像机的镜头畸变。
-   你正在开发一个**增强现实（AR）**应用，需要将虚拟物体精确地“放置”在通过手机或头戴设备摄像头看到的真实世界中，并确保虚拟物体边缘与真实世界的畸变线条对齐。
-   你有一个已标定好参数的**工业或科研摄像机**，需要在引擎中实时处理或校正其拍摄的视频流。
-   你需要为后期合成或实时预览创建带有特定镜头“风格”（畸变）的虚拟摄像机画面。

## 蓝图用法

该插件主要提供了一个蓝图函数库 `UOpenCVLensDistortionBlueprintLibrary`，所有核心功能都通过静态函数实现。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateUndistortUVDisplacementMap` | 核心节点。根据镜头畸变参数和图像尺寸，计算并生成一张用于“校正畸变”的 UV 位移贴图。此操作可能耗时较长。 | `UOpenCVLensDistortionBlueprintLibrary` |
| `DrawDisplacementMapToRenderTarget` | 将预先计算好的位移贴图绘制到渲染目标（RenderTarget）上，以便在材质中采样使用。 | `UOpenCVLensDistortionBlueprintLibrary` |
| `Equal (LensDistortionParameters)` | 比较两个镜头畸变参数结构体是否相等。 | `UOpenCVLensDistortionBlueprintLibrary` |
| `NotEqual (LensDistortionParameters)` | 比较两个镜头畸变参数结构体是否不相等。 | `UOpenCVLensDistortionBlueprintLibrary` |

### 使用示例（蓝图描述）

**场景1：创建并应用镜头畸变效果**

1.  **获取参数**：首先，你需要一个 `FOpenCVLensDistortionParameters` 结构体变量，填入你摄像机的标定数据（如 `FocalLength`, `PrincipalPoint`, `DistortionCoefficients` 等）。这个数据可能来自外部标定软件，或通过 `OpenCVLensCalibration` 模块的 API 在引擎内计算。
2.  **生成位移贴图**：调用 `CreateUndistortUVDisplacementMap` 节点。将你的参数结构体、目标图像分辨率（如 `1920x1080`）以及一个裁剪因子（`CroppingFactor`，0.0到1.0之间）连接到输入。该节点会输出一个 `UTexture2D*` 类型的位移贴图，以及一个 `FOpenCVCameraViewInfo` 结构体，里面包含了校正后视图的FOV等信息，可用于调整场景捕获（SceneCapture）组件。
3.  **绘制到渲染目标**：由于后续材质处理可能更灵活，通常将生成的位移贴图绘制到一个 `UTextureRenderTarget2D*` 中。创建一个渲染目标资产，然后调用 `DrawDisplacementMapToRenderTarget` 节点，将生成的位移贴图作为输入。
4.  **在材质中使用**：在材质编辑器中，将上述渲染目标作为纹理采样。在最终输出颜色前，使用该纹理的 **RG通道** 作为 UV 坐标，去采样你的最终纹理。RG通道存储的就是畸变到校正的UV偏移，从而实现画面的“去畸变”效果。如果想模拟畸变，则使用 **BA通道**。

## C++ 用法

在 C++ 中使用此插件需要包含特定头文件，并理解其核心数据结构。

### 头文件引入

```cpp
// 使用镜头畸变参数和函数库
#include "OpenCVLensDistortionParameters.h"
#include "OpenCVLensDistortionBlueprintLibrary.h"

// 如果需要直接访问模块接口（通常不需要）
#include "IOpenCVLensDistortionModule.h"
```

### 基本用法

**创建并使用畸变参数结构体**

```cpp
// 来源: Public/OpenCVLensDistortionParameters.h
// FOpenCVLensDistortionParameters 是核心参数结构体
FOpenCVLensDistortionParameters LensParams;
LensParams.FocalLength = FVector2D(1000.0f, 1000.0f); // 示例焦距
LensParams.PrincipalPoint = FVector2D(960.0f, 540.0f); // 示例主点
LensParams.DistortionCoefficients = { -0.2f, 0.1f, 0.0f, 0.0f, 0.0f }; // 示例畸变系数

// 创建去畸变位移贴图
FIntPoint ImageSize(1920, 1080);
float CroppingFactor = 0.5f; // 裁剪50%
FOpenCVCameraViewInfo OutCameraInfo;

UTexture2D* DisplacementMap = LensParams.CreateUndistortUVDisplacementMap(
    ImageSize,
    CroppingFactor,
    OutCameraInfo
);

if (DisplacementMap)
{
    // 使用生成的位移贴图...
    UE_LOG(LogTemp, Log, TEXT("去畸变位移贴图已生成。校正后水平FOV: %f 度"), OutCameraInfo.HorizontalFOV);
}
```

### 进阶用法

**通过蓝图函数库与渲染目标交互**

```cpp
// 来源: Public/OpenCVLensDistortionBlueprintLibrary.h
// 需要一个 UWorld* 来获取渲染上下文
UWorld* World = GetWorld(); // 例如在 Actor 或 ActorComponent 中
UTextureRenderTarget2D* MyRenderTarget = /* 你的渲染目标资产 */;

if (World && MyRenderTarget && DisplacementMap) // DisplacementMap 来自上一节
{
    // 将位移贴图绘制到渲染目标
    UOpenCVLensDistortionBlueprintLibrary::DrawDisplacementMapToRenderTarget(
        World,
        MyRenderTarget,
        DisplacementMap
    );

    // 现在 MyRenderTarget 可以在材质中使用了
}
```

## Demo 示例

以下是一个最小化的 Actor 示例，它在开始游戏时生成位移贴图并应用到自身的动态材质实例上。

**LensDistortionDemoActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "LensDistortionDemoActor.generated.h"

class UTextureRenderTarget2D;
class UTexture2D;

UCLASS()
class ALensDistortionDemoActor : public AActor
{
    GENERATED_BODY()
    
public:    
    ALensDistortionDemoActor();

protected:
    virtual void BeginPlay() override;

    UPROPERTY(EditAnywhere, Category="Lens Distortion")
    FOpenCVLensDistortionParameters LensParameters;

    UPROPERTY(VisibleAnywhere, Category="Lens Distortion")
    UTextureRenderTarget2D* DistortionRenderTarget;

    UPROPERTY(VisibleAnywhere, Category="Lens Distortion")
    UStaticMeshComponent* MeshComponent;

private:
    UTexture2D* GeneratedDisplacementMap;
};
```

**LensDistortionDemoActor.cpp**
```cpp
#include "LensDistortionDemoActor.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/TextureRenderTarget2D.h"
#include "OpenCVLensDistortionParameters.h"
#include "OpenCVLensDistortionBlueprintLibrary.h"

ALensDistortionDemoActor::ALensDistortionDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;
    MeshComponent = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
    RootComponent = MeshComponent;
    // 创建一个渲染目标
    DistortionRenderTarget = CreateDefaultSubobject<UTextureRenderTarget2D>(TEXT("DistortionRT"));
}

void ALensDistortionDemoActor::BeginPlay()
{
    Super::BeginPlay();

    // 生成位移贴图
    FIntPoint ImageSize(1024, 1024);
    float CroppingFactor = 0.0f;
    FOpenCVCameraViewInfo CameraInfo;
    GeneratedDisplacementMap = LensParameters.CreateUndistortUVDisplacementMap(ImageSize, CroppingFactor, CameraInfo);

    if (GeneratedDisplacementMap && DistortionRenderTarget)
    {
        // 绘制到渲染目标
        UOpenCVLensDistortionBlueprintLibrary::DrawDisplacementMapToRenderTarget(
            GetWorld(),
            DistortionRenderTarget,
            GeneratedDisplacementMap
        );

        // 假设材质实例已经有一个名为 "DistortionMap" 的纹理参数
        UMaterialInstanceDynamic* DynMaterial = MeshComponent->CreateDynamicMaterialInstance(0);
        if (DynMaterial)
        {
            DynMaterial->SetTextureParameterValue("DistortionMap", DistortionRenderTarget);
        }
    }
}
```

## 模块依赖

此插件的核心依赖于 Unreal Engine 的 OpenCV 插件。要在你的模块中使用它，需要添加以下依赖：

| 模块 | 用途 |
|---|---|
| `OpenCVLensDistortion` | 提供核心的镜头畸变参数、计算和蓝图函数库。 |
| `OpenCV` | 底层 OpenCV 库的封装，此插件依赖其进行数学运算。 |

请确保在你的模块的 `.Build.cs` 文件中正确添加对这些模块的依赖。例如：

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
    "Engine",
    "OpenCVLensDistortion",
    "OpenCV" // 可能需要，取决于你使用的具体API
});
```

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志系统现代化，将旧版 UE_LOG 宏迁移至新版 UE_LOGF。 |
| 2025-10-07 | `96352708` | - Renaming Base<Plugin>.ini to Default<Plugin>.ini | 统一插件配置文件命名规范，将 BaseIni 改为 DefaultIni。 |
| 2024-01-29 | `10cdd4a1` | Merging //UE5/Dev-ParallelRendering/... | 合并并行渲染开发分支，更新相关底层代码。 |
| 2023-03-01 | `dd7c0212` | Changing a lot more code to use batched shader parameters. | 性能优化，大规模转向使用批处理着色器参数。 |
| 2023-01-17 | `44aeabe4` | [Engine/Plugins] | 例行插件维护与更新。 |

### 维护评价

该插件**处于“维护不活跃”状态**，但**未被废弃**。
- **创建时间**：约7年前，属于老插件。
- **更新频率**：最近的几次提交（2023， 2024， 2025， 2026）表明它仍在UE主版本升级中被顺带维护，但没有功能性的增强或重大修复。
- **状态**：标记为 `IsBetaVersion: true` 且 `EnabledByDefault: false`，表明它从未从实验性状态毕业，官方可能认为其API或功能尚未完全稳定。
- **已知限制**：主要限制是**平台支持**，仅限于 Win64, Linux, Mac，不支持主机或移动平台。此外，由于依赖OpenCV，会增加项目的最终包体大小。
- **推荐使用**：如果你在开发**PC平台的虚拟制作或AR原型**项目，并且接受其Beta状态和平台限制，它仍然是一个有价值且功能明确的工具。对于生产环境或需要广泛平台支持的项目，需谨慎评估。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Compositing/OpenCVLensDistortion)
- 官方文档链接（.uplugin 中 DocsURL 为空）
- 测试用例（未在提供信息中发现）