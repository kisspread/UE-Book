# Camera Calibration

> Framework to support lens distortion and camera calibration in engine.

| 属性 | 值 |
|---|---|
| 中文名 | 相机校准 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（镜头资产、校准数据） |
| 模块 | `CameraCalibrationEditor` (Runtime), `TrackingAlignment` (Runtime), `TrackingAlignmentEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-04-29 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CameraCalibration) | |

## 用途

Camera Calibration 插件旨在为虚幻引擎提供一套完整的镜头畸变和相机校准工作流。它解决的核心问题是：在虚拟制作（Virtual Production）中，特别是使用 LED 墙或进行精确合成时，如何将真实世界镜头的光学特性（如畸变、呼吸效应、对焦距离映射）精确地应用到虚拟摄像机上，以实现物理准确的渲染和合成。

该插件提供了一个框架，允许用户：
1.  **校准真实镜头**：使用校准图板拍摄图像，计算并存储镜头的畸变参数和非线性特性。
2.  **应用校正**：在引擎的运行时或渲染管线中，实时应用或反向应用这些畸变校正，使得虚拟渲染的画面能与真实摄像机拍摄的画面完美对齐。
3.  **管理数据**：统一管理不同镜头的校准数据文件，支持多种镜头文件格式。

## 使用场景

- **LED 虚拟制作**：在 LED 摄影棚中，需要将虚拟场景无缝投射到 LED 屏幕上，并确保通过真实摄像机看到的画面没有畸变或透视错误。此插件可校准并校正摄像机与屏幕之间的畸变。
- **影视后期合成**：在需要将 CG 元素与实拍素材进行合成时，精确匹配实拍镜头的畸变特性是保证真实感的关键。此插件生成的校正数据可用于后期软件或引擎内渲染。
- **高精度相机追踪**：用于需要极高视觉保真的 AR/VR 应用或模拟训练，确保虚拟物体在真实镜头视野中的位置和形状完全正确。

## 蓝图用法

插件的核心蓝图接口通过 `UCameraCalibrationSubsystem` 提供，该子系统管理所有校准数据和校正器。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Camera Calibration Subsystem` | 获取相机校准子系统的单例实例 | `UCameraCalibrationSubsystem` |
| `Get All Lens File` | 获取所有已加载的镜头文件资产列表 | `UCameraCalibrationSubsystem` |
| `Find Lens File` | 根据资产路径查找特定的镜头文件 | `UCameraCalibrationSubsystem` |
| `Import Lens File` | 从文件系统导入镜头数据文件（如 .lens） | `UCameraCalibrationSubsystem` |
| `Get All Distortion Overscan Multiplier` | 获取所有注册的畸变过扫描乘数校正器 | `UCameraCalibrationSubsystem` |
| `Get All Displacement Map` | 获取所有注册的位移贴图校正器 | `UCameraCalibrationSubsystem` |
| `Get All Focal Length Table` | 获取所有注册的焦距映射表校正器 | `UCameraCalibrationSubsystem` |

### 使用示例（蓝图描述）

1.  **加载镜头文件**：在 BeginPlay 中，使用 “Get Camera Calibration Subsystem” 节点获取子系统，然后调用 “Import Lens File” 并传入镜头文件路径，将其加载到内存中。
2.  **为组件应用校准**：找到场景中的 `UCameraComponent`，为其添加一个 `ULensComponent`。在 ULensComponent 的属性中，指定要使用的 `ULensFile` 资产。运行时，该组件会根据镜头文件中的数据自动驱动摄像机的畸变校正。
3.  **查询校正数据**：可以通过子系统的查询函数（如 `Find Lens File`）获取特定镜头的数据，然后调用如 `Evaluate Distortion` 之类的函数，在蓝图中计算特定焦距和对焦距离下的畸变参数。

## C++ 用法

### 头文件引入

```cpp
#include "CameraCalibrationSubsystem.h"
#include "LensFile.h"
#include "LensComponent.h"
```

### 基本用法

（示例来源：引擎测试代码 `Engine/Plugins/VirtualProduction/CameraCalibration/Tests/`）

```cpp
// 1. 获取相机校准子系统
UCameraCalibrationSubsystem* CalibrationSubsystem = GEngine->GetEngineSubsystem<UCameraCalibrationSubsystem>();

// 2. 加载一个镜头文件资产（通常在资产路径已知的情况下）
FString LensFilePath = TEXT("/Game/Calibration/MyLensFile");
TObjectPtr<ULensFile> LoadedLensFile = LoadObject<ULensFile>(nullptr, *LensFilePath);
if (LoadedLensFile)
{
    // 3. 将镜头文件注册到子系统（通常由ULensComponent自动完成，但也可手动）
    // CalibrationSubsystem->RegisterLensFile(LoadedLensFile);
}

// 4. 查询镜头文件中的数据
if (LoadedLensFile)
{
    float FocalLength = 50.0f;
    float FocusDistance = 1000.0f; // 10米
    FDistortionInfo DistortionInfo;
    // 评估在特定焦距和对焦距离下的畸变参数
    bool bSuccess = LoadedLensFile->EvaluateDistortion(FocalLength, FocusDistance, DistortionInfo);
}
```

### 进阶用法

自定义一个畸变校正器（Distortion Model），并将其注册到子系统。

```cpp
// MyCustomDistortionModel.h
#pragma once
#include "DistortionModel.h"
#include "MyCustomDistortionModel.generated.h"

UCLASS()
class UMyCustomDistortionModel : public UDistortionModel
{
    GENERATED_BODY()
public:
    // 实现畸变评估接口
    virtual FDistortionInfo Evaluate(const FCameraCalibrationParameters& Params, const FVector2D& InUV) const override;
    // ... 其他必要的虚函数实现
};
```

```cpp
// 在模块初始化时注册自定义模型
void FMyModule::StartupModule()
{
    UCameraCalibrationSubsystem* Subsystem = GEngine->GetEngineSubsystem<UCameraCalibrationSubsystem>();
    if (Subsystem)
    {
        // 创建并注册自定义模型
        UMyCustomDistortionModel* MyModel = NewObject<UMyCustomDistortionModel>(GetTransientPackage(), UMyCustomDistortionModel::StaticClass());
        Subsystem->RegisterDistortionModel(MyModel);
    }
}
```

## Demo 示例

下面是一个最小化的 C++ 示例，展示如何创建并注册一个简单的自定义镜头文件，并将其应用到场景中的摄像机上。

**MyCalibrationDemo.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyCalibrationDemo.generated.h"

class ULensFile;
class ULensComponent;

UCLASS()
class AMyCalibrationDemo : public AActor
{
    GENERATED_BODY()

public:
    AMyCalibrationDemo();

protected:
    virtual void BeginPlay() override;

private:
    // 一个用于演示的摄像机组件
    UPROPERTY(VisibleAnywhere)
    TObjectPtr<UCameraComponent> DemoCamera;

    // 附加到摄像机的镜头校准组件
    UPROPERTY(VisibleAnywhere)
    TObjectPtr<ULensComponent> DemoLensComponent;

    // 运行时创建的镜头文件资产
    UPROPERTY()
    TObjectPtr<ULensFile> RuntimeLensFile;
};
```

**MyCalibrationDemo.cpp**
```cpp
#include "MyCalibrationDemo.h"
#include "Camera/CameraComponent.h"
#include "LensComponent.h"
#include "LensFile.h"
#include "CameraCalibrationSubsystem.h"

AMyCalibrationDemo::AMyCalibrationDemo()
{
    // 创建根组件和摄像机组件
    RootComponent = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
    DemoCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("DemoCamera"));
    DemoCamera->SetupAttachment(RootComponent);

    // 创建并附加镜头组件
    DemoLensComponent = CreateDefaultSubobject<ULensComponent>(TEXT("DemoLens"));
    DemoLensComponent->SetupAttachment(DemoCamera);
}

void AMyCalibrationDemo::BeginPlay()
{
    Super::BeginPlay();

    // 创建一个临时的镜头文件对象用于演示
    RuntimeLensFile = NewObject<ULensFile>(GetTransientPackage(), TEXT("RuntimeLensFile"));

    // 为镜头文件设置一些示例数据 (通常从文件导入，这里简化)
    // 假设我们有一个标准的桶形畸变
    FDistortionInfo BarrelDistortion;
    BarrelDistortion.K1 = 0.3f;
    BarrelDistortion.K2 = 0.05f;
    // ... 设置其他参数
    RuntimeLensFile->SetDistortionInfo(BarrelDistortion);

    // 将镜头文件关联到镜头组件
    if (DemoLensComponent)
    {
        DemoLensComponent->SetLensFile(RuntimeLensFile);
    }
}
```

## 模块依赖

从各模块的 `Build.cs` 文件分析，插件除标准 Core/Engine 依赖外，还依赖以下独特模块：

| 模块 | 用途 |
|---|---|
| `LensComponent` | 提供用于驱动摄像机校准的核心组件。 |
| `ImageWriteQueue` | 用于在引擎内保存校准图表或渲染结果图像。 |
| `CinematicCamera` | 与电影摄像机功能集成。 |
| `LevelSequence` | 支持在序列器（Sequencer）中控制校准参数。 |
| `ImagePlate` | 集成图像板（Image Plate）功能，常用于合成。 |
| `OpenCV` | （可选）底层计算机视觉库，用于实际的校准计算。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构视口代码，优化客户端通知逻辑 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回退之前的提交 CL53913857 |
| 2026-05-14 | `9ede83f2` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 同 cfb610df，重构视口客户端通知 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下 double 转 float 的警告 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 调整虚拟制作资产的分类和目录结构 |

### 维护评价

- **活跃维护**：插件创建于2021年，截至2026年5月仍有**每周级别**的活跃更新，表明处于积极的开发和维护中。
- **实验性功能**：标记为 `IsBetaVersion = true`，说明 Epic 可能仍在对其 API 和功能进行迭代和优化，不建议在生产环境的关键路径上无条件依赖。
- **核心地位**：作为 Virtual Production 工作流中的关键一环，用于精确合成和 LED 墙拍摄，其重要性不言而喻。
- **推荐度**：**推荐使用**，特别是对于从事虚拟制作、需要精确镜头匹配的项目。但应注意其 Beta 状态，保持对后续版本变更的关注，并做好 API 可能调整的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CameraCalibration)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CameraCalibration/Tests)