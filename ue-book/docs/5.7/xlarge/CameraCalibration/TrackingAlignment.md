# Camera Calibration

> Framework to support lens distortion and camera calibration in engine.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `CameraCalibrationEditor` (Runtime), `TrackingAlignment` (Runtime), `TrackingAlignmentEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-04-29 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CameraCalibration) | |

## 用途

`CameraCalibration` 插件为 Unreal Engine 提供了一套完整的相机校准和镜头畸变处理框架。它主要用于虚拟制片（Virtual Production）工作流，解决以下核心问题：
1.  **镜头畸变校正**：真实相机镜头存在固有的光学畸变（如桶形畸变、枕形畸变）。该插件允许用户通过校准数据（如棋盘格图案）来测量并校正这些畸变，确保虚拟内容与实拍画面完美匹配。
2.  **相机参数解算**：从校准数据中解算出相机的内参（焦距、主点、畸变系数）和外参（位置、旋转），为精确的摄像机追踪和合成提供基础。
3.  **跟踪数据对齐**：特别是 `TrackingAlignment` 模块，专注于将来自外部跟踪系统（如 Mo-Sys、Stype 等）的相机运动数据与引擎内渲染的虚拟相机进行精确对齐和同步，这是实现高质量实时合成的关键。

## 使用场景

-   **虚拟制片（Virtual Production）**：在 LED 墙或绿幕前拍摄时，需要将实拍相机的运动与虚拟场景的渲染精确同步。使用此插件校准相机并持续对齐跟踪数据。
-   **视觉特效（VFX）**：在后期制作中，需要将 CG 元素无缝合成到实拍素材中。使用校准数据生成精确的镜头畸变图，应用于 CG 渲染。
-   **增强现实（AR）**：将虚拟物体精确地叠加到现实世界画面中，需要准确的相机参数和畸变校正。
-   **机器人与计算机视觉**：为需要精确视觉感知的机器人或计算机视觉应用提供相机标定工具。

## 蓝图用法

`TrackingAlignment` 模块主要提供运行时对齐功能，其蓝图接口通常通过 `CameraCalibrationSubsystem` 或相关的 Actor/Component 暴露。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Tracking Alignment` | 获取当前的跟踪对齐实例。 | `UCameraCalibrationSubsystem` |
| `Start Alignment` | 启动跟踪数据对齐流程。 | `UTrackingAlignment` |
| `Stop Alignment` | 停止跟踪数据对齐流程。 | `UTrackingAlignment` |
| `Set Alignment Transform` | 设置用于对齐的变换偏移。 | `UTrackingAlignment` |

### 使用示例（蓝图描述）

1.  在场景中放置一个 `CineCameraActor` 作为你的虚拟渲染相机。
2.  通过 `Get Tracking Alignment` 节点获取 `UTrackingAlignment` 对象。
3.  调用 `Start Alignment`，并传入你的 `CineCameraActor` 和外部跟踪数据源（通常通过接口或数据流）。
4.  在每一帧，`TrackingAlignment` 系统会自动将外部跟踪数据应用到你的虚拟相机上，并进行实时校正。
5.  当需要停止时，调用 `Stop Alignment`。

## C++ 用法

`TrackingAlignment` 模块的核心是 `UTrackingAlignment` 类，它管理对齐状态和逻辑。

### 头文件引入

```cpp
#include "TrackingAlignment.h"
```

### 基本用法

```cpp
// 假设你已经有了一个 UCameraCalibrationSubsystem 的引用
UCameraCalibrationSubsystem* CalibSubsystem = GEngine->GetEngineSubsystem<UCameraCalibrationSubsystem>();
if (CalibSubsystem)
{
    // 获取跟踪对齐对象
    UTrackingAlignment* TrackingAligner = CalibSubsystem->GetTrackingAlignment();
    if (TrackingAligner)
    {
        // 启动对齐，将外部跟踪数据应用到目标相机
        TrackingAligner->StartAlignment(TargetCameraComponent, ExternalTrackingDataSource);
        
        // 在 Tick 或合适的地方更新对齐状态
        // TrackingAligner->TickAlignment(DeltaTime);
        
        // 结束时停止对齐
        TrackingAligner->StopAlignment();
    }
}
```
*（注：以上为基于模块功能的示例代码结构，具体API需参考实际头文件）*

### 进阶用法

可以结合 `CameraCalibrationEditor` 模块提供的校准数据，在运行时动态加载镜头文件（`.lens`），并将其畸变参数应用到 `UTrackingAlignment` 的校正流程中，实现从校准到实时对齐的完整闭环。

## Demo 示例

一个最小的 C++ 示例，展示如何在 Actor 中集成跟踪对齐。

**MyTrackingActor.h**
```cpp
#pragma once
#include "GameFramework/Actor.h"
#include "MyTrackingActor.generated.h"

class UCameraComponent;
class UTrackingAlignment;

UCLASS()
class AMyTrackingActor : public AActor
{
    GENERATED_BODY()

public:
    AMyTrackingActor();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    UPROPERTY(VisibleAnywhere)
    UCameraComponent* VirtualCamera;

private:
    UPROPERTY()
    UTrackingAlignment* TrackingAligner;
};
```

**MyTrackingActor.cpp**
```cpp
#include "MyTrackingActor.h"
#include "Camera/CameraComponent.h"
#include "TrackingAlignment.h"
#include "CameraCalibrationSubsystem.h"

AMyTrackingActor::AMyTrackingActor()
{
    PrimaryActorTick.bCanEverTick = true;
    VirtualCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("VirtualCamera"));
    RootComponent = VirtualCamera;
}

void AMyTrackingActor::BeginPlay()
{
    Super::BeginPlay();

    // 获取子系统并创建对齐器
    UCameraCalibrationSubsystem* Subsystem = GEngine->GetEngineSubsystem<UCameraCalibrationSubsystem>();
    if (Subsystem)
    {
        TrackingAligner = Subsystem->CreateTrackingAlignment();
        if (TrackingAligner)
        {
            // 假设有一个外部数据源接口 IExternalTracker
            // TrackingAligner->StartAlignment(VirtualCamera, ExternalTracker);
        }
    }
}

void AMyTrackingActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (TrackingAligner)
    {
        TrackingAligner->StopAlignment();
        // 注意：对齐器的生命周期可能由子系统管理，此处仅停止。
    }
    Super::EndPlay(EndPlayReason);
}
```

**YourModule.Build.cs 依赖**
```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
    "Engine",
    "CameraCalibrationCore", // 假设的核心校准模块
    "TrackingAlignment"      // 本模块
});
```

## 模块依赖

从 `TrackingAlignment` 模块的功能推断，其依赖可能包括：

| 模块 | 用途 |
|---|---|
| `CameraCalibrationCore` | 提供基础的校准数据结构、镜头文件格式和核心校准算法。 |
| `MediaUtils` | 可能用于处理来自外部设备的媒体流或跟踪数据。 |
| `LiveLinkInterface` | 如果跟踪数据通过 Live Link 传输，则需要此依赖。 |

## 维护状态

### 近期更新

```
fcf82a98f07f TrackingAlignmentTool: Adding Tracking Alignment Tool into the Camera Calibration plugin.
```
- **日期**: 2024-05-14 (推测)
- **Commit**: `fcf82a98f07f`
- **说明**: 将 `TrackingAlignment` 工具正式添加到 `CameraCalibration` 插件中。
- **解读**: 这是该模块的初始提交，表明它是一个相对较新的功能模块，刚刚被集成到主插件中。这解释了为什么 git 历史只有一条记录。

### 维护评价

- **创建时间**：模块本身（`TrackingAlignment`）非常新，刚刚被添加。
- **最近更新频率**：目前只有一次提交，是功能的初始集成。
- **活跃维护**：作为 `CameraCalibration` 插件（创建于2021年，标记为实验性）的一部分，该插件整体处于**活跃开发**状态。`TrackingAlignment` 模块的加入正是其持续演进的证明。
- **已知问题或限制**：由于是新模块且插件整体标记为 `IsBetaVersion: true`，可能存在API不稳定、功能不完善或文档缺失的情况。
- **推荐使用**：**推荐在虚拟制片项目中试用**，但需注意其**实验性**状态。适合愿意跟进最新功能并能容忍潜在问题的团队。不建议用于对稳定性要求极高的生产环境，除非经过充分测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CameraCalibration)
- [官方文档]() (暂无)
- [测试用例]() (暂无，可能位于 `Engine/Tests/` 目录下)