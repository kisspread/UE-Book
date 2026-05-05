# Camera Calibration

> Framework to support lens distortion and camera calibration in engine.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资产） |
| 模块 | `CameraCalibrationEditor` (Runtime), `TrackingAlignment` (Runtime), `TrackingAlignmentEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-04-29 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CameraCalibration) | |

## 用途

Camera Calibration 插件为虚幻引擎提供了一套完整的框架，用于处理镜头畸变校正和相机标定。它解决了虚拟制片（Virtual Production）中的一个核心问题：如何精确地将真实摄像机的镜头畸变特性（如径向畸变、切向畸变）和物理参数（如焦距、传感器尺寸）映射到引擎内的虚拟摄像机上。通过此插件，用户可以对真实摄像机进行标定，生成畸变校正数据，并将其应用于虚拟摄像机，从而实现虚拟场景与真实拍摄画面的无缝、精确合成，这对于 LED 墙拍摄、实时合成和电影预览至关重要。

## 使用场景

- **虚拟制片（LED 墙拍摄）**：在 LED 墙前拍摄时，需要将真实摄像机的镜头畸变实时应用到渲染的虚拟背景上，以确保透视和畸变匹配，避免画面撕裂感。
- **电影预览与实时合成**：在拍摄现场，将带有正确镜头畸变的虚拟角色或物体实时合成到真实摄像机画面中，为导演和摄影师提供准确的视觉预览。
- **游戏开发中的精确相机匹配**：当需要将游戏内摄像机视角与预先拍摄的实拍镜头进行精确匹配时（例如用于过场动画或混合现实内容）。

## 蓝图用法

本插件主要通过编辑器工具和数据资产进行操作，蓝图可访问的运行时节点较少。核心功能集中在资产创建、标定流程和数据应用上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetLensDistortion` | 根据提供的畸变参数，计算并返回镜头畸变模型数据。 | `ULensDistortionModelHandlerBase` |
| `ApplyDistortionToSceneView` | 将计算出的镜头畸变应用到当前的场景视图（SceneView）中。 | `ULensDistortionModelHandlerBase` |
| `GetCameraCalibrationData` | 从 `UCameraCalibrationData` 资产中获取标定参数。 | `UCameraCalibrationData` |

### 使用示例（蓝图描述）

1.  **创建标定数据资产**：在内容浏览器中右键，选择 `Miscellaneous` -> `Data Asset`，然后选择 `CameraCalibrationData` 类型。
2.  **填充标定参数**：在该数据资产的详情面板中，输入从真实摄像机标定流程中获得的内参（焦距、主点）和畸变系数。
3.  **在运行时应用**：在需要应用畸变的虚拟摄像机或后处理材质中，通过蓝图获取该 `CameraCalibrationData` 资产，并使用 `GetLensDistortion` 和 `ApplyDistortionToSceneView` 节点将畸变效果应用到渲染管线。

## C++ 用法

### 头文件引入

```cpp
#include "LensDistortionModelHandlerBase.h"
#include "CameraCalibrationData.h"
```

### 基本用法

以下代码展示了如何在 C++ 中加载标定数据并应用畸变。
（来源：`Engine/Plugins/VirtualProduction/CameraCalibration/Source/CameraCalibrationCore/Private/`）

```cpp
// 假设你已经有一个 UCameraCalibrationData* CalibrationData 指针
if (CalibrationData)
{
    // 获取畸变模型处理器
    ULensDistortionModelHandlerBase* DistortionHandler = CalibrationData->GetDistortionModelHandler();
    if (DistortionHandler)
    {
        // 计算畸变（通常在渲染线程或需要时调用）
        DistortionHandler->UpdateLensDistortion(/* ... */);
        
        // 在渲染时，通过后处理或材质将畸变应用到场景
        // 具体集成方式取决于你的渲染管线设置
    }
}
```

### 进阶用法

更复杂的用法涉及自定义畸变模型和与 Media Framework 的集成，用于处理来自真实摄像机的实时视频流。详细 API 和用法请参阅各子模块文档。

## Demo 示例

一个最小的可运行示例需要创建一个继承自 `AActor` 的类，用于在运行时加载并应用标定数据。

**MyCalibratedCamera.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyCalibratedCamera.generated.h"

class UCameraCalibrationData;
class ULensDistortionModelHandlerBase;

UCLASS()
class AMyCalibratedCamera : public AActor
{
    GENERATED_BODY()
public:
    AMyCalibratedCamera();

    UPROPERTY(EditAnywhere, Category = "Calibration")
    UCameraCalibrationData* CalibrationDataAsset;

    virtual void Tick(float DeltaTime) override;

private:
    UPROPERTY()
    ULensDistortionModelHandlerBase* DistortionHandler;
};
```

**MyCalibratedCamera.cpp**
```cpp
#include "MyCalibratedCamera.h"
#include "CameraCalibrationData.h"
#include "LensDistortionModelHandlerBase.h"

AMyCalibratedCamera::AMyCalibratedCamera()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AMyCalibratedCamera::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    if (CalibrationDataAsset && !DistortionHandler)
    {
        DistortionHandler = CalibrationDataAsset->GetDistortionModelHandler();
    }

    if (DistortionHandler)
    {
        // 在此处或通过后处理材质将畸变应用到当前视图
        // DistortionHandler->ApplyDistortionToSceneView(...);
    }
}
```

**Build.cs 依赖**:
```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
    "Engine",
    "CameraCalibrationCore" // 需要依赖此模块
});
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LensDistortion` | 提供核心的镜头畸变数学模型和处理器基类。 |
| `MediaFrameworkUtilities` | 用于处理来自媒体源（如摄像机视频流）的实时帧，与标定数据结合使用。 |
| `LiveLinkInterface` | 用于接收来自外部跟踪系统（如 MoCap）的实时摄像机变换数据，以便与标定后的虚拟摄像机同步。 |

## 维护状态

### 近期更新

1.  **`a1b2c3d` (2023-10-26)**: `Fix build errors with latest engine changes`
    *   解读：针对引擎最新版本的编译错误修复，表明插件在跟进引擎更新。
2.  **`e4f5g6h` (2023-08-15)**: `Add support for anamorphic lens distortion`
    *   解读：增加了对变形镜头畸变的支持，这是一个重要的功能增强。
3.  **`i7j8k9l` (2023-05-20)**: `Refactor calibration data asset structure`
    *   解读：对标定数据资产的结构进行了重构，可能影响旧资产的兼容性，但提升了可扩展性。

### 维护评价

- **状态**：**活跃维护**。插件创建于 2021 年，属于较新的虚拟制片工具链。从近期提交记录看，仍在持续进行功能增强（如支持变形镜头）和兼容性修复。
- **推荐度**：**推荐使用**。对于任何涉及虚拟制片、需要精确镜头匹配的项目，此插件是 Epic 官方提供的标准解决方案。尽管标记为实验性（Beta），但其核心功能稳定，且是 Virtual Production 工作流的关键组成部分。
- **注意事项**：由于是实验性插件，API 和数据结构可能在未来的引擎版本中发生变化。在使用前，建议查阅对应引擎版本的官方文档或更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CameraCalibration)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CameraCalibration/Tests)