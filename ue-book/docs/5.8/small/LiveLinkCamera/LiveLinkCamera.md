# Live Link Camera

> Live Link plugin adding functionalities for camera handling

| 属性 | 值 |
|---|---|
| 中文名 | 实时链接相机 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、配置文件） |
| 模块 | `LiveLinkCamera` (Runtime), `LiveLinkCameraEditor` (Runtime), `LiveLinkCameraRecording` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-03-05 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LiveLinkCamera) | |

## 用途

Live Link Camera 是一个专注于实时相机控制的 Live Link 扩展插件。它解决了在虚拟制片和实时渲染中，如何将外部相机跟踪系统（如 Mo-cap 系统、专业摄像机）的实时数据精确映射到 UE5 内置相机上的问题。该插件负责将 Live Link 接收到的相机帧数据（如 FOV、焦距、光圈、失真等）应用到 CineCameraComponent，并与镜头文件（Lens File）系统集成，以实现从物理相机传感器到引擎相机属性的精确转换。

## 使用场景

- 你在进行虚拟制片，使用如 OptiTrack、Vicon 等动作捕捉系统跟踪真实摄影机，需要其运动数据实时驱动 UE5 内的虚拟相机。
- 你使用专业电影摄影机（如 ARRI, RED）并通过 Live Link 接口将其镜头数据（焦距、光圈、对焦距离）实时同步到引擎内，用于实时预览或最终合成。
- 你需要将相机跟踪系统的数据与引擎的镜头校准（Lens Calibration）工作流集成，以实现更精确的虚拟镜头模拟。

## 蓝图用法

该插件的主要蓝图节点通过 `LiveLinkCameraController` 类暴露，它继承自 `ULiveLinkControllerBase`，通常作为组件存在于 Actor 上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Apply FIZ` | 将 FIZ（焦点、光圈、变焦）数据应用到相机组件，可结合镜头文件 | `ULiveLinkCameraController` |
| `Get Lens File Eval Data Ref` | 获取用于评估镜头文件的输入数据的常量引用 | `ULiveLinkCameraController` |

### 核心属性（蓝图可读写）

| 属性 | 说明 | 所在类 |
|---|---|---|
| `Update Flags` | 一个结构体，控制是否应用 Live Link 帧数据中的各项属性（FOV、焦距、光圈等） | `ULiveLinkCameraController` |
| `b Use Camera Range` | 是否使用相机组件的范围将 Live Link 输入值重新映射（归一化到物理单位） | `ULiveLinkCameraController` |
| `Lens File Picker` | 选择用于 FIZ 数据映射的镜头文件资产 | `ULiveLinkCameraController` |

### 使用示例（蓝图描述）

1. 在场景中的 Actor（如 CineCameraActor）上添加 `LiveLinkController` 组件，并将其 `Controller Class` 设置为 `LiveLinkCameraController`。
2. 在该组件的细节面板中，配置 `Live Link Subject` 以选择你的相机数据源。
3. 通过 `Update Flags` 结构体勾选你希望由 Live Link 流控制的相机属性（例如，只更新 FOV 和焦距）。
4. 如果需要 FIZ 映射，将 `Lens File Picker` 指向你的镜头文件资产。
5. 运行时，该控制器会自动将 Live Link 帧数据应用到它所附加的相机组件上。

## C++ 用法

### 头文件引入

```cpp
#include "LiveLinkCameraController.h"
```

### 基本用法

该插件主要用于运行时控制。核心逻辑封装在 `ULiveLinkCameraController` 中，它实现了 `ULiveLinkControllerBase` 的接口。

**配置更新标志 (C++)**

在 C++ 中，你可以直接访问和修改控制器的更新标志来控制数据的应用。

```cpp
// 假设你已经有一个指向 ULiveLinkCameraController 实例的指针 LiveLinkCamController
ULiveLinkCameraController* LiveLinkCamController = ...; // 获取方式同任何 UObject

// 访问其更新标志
FLiveLinkCameraControllerUpdateFlags& Flags = LiveLinkCamController->UpdateFlags;

// 例如，只允许应用焦距和光圈，关闭 FOV 应用
Flags.bApplyFieldOfView = false;
Flags.bApplyFocalLength = true;
Flags.bApplyAperture = true;
```

### 进阶用法

你可以继承或实例化该控制器，并重写 `Tick` 函数来注入自定义逻辑，但更推荐使用它提供的 `ApplyFIZ` 方法，并结合 `FLensFileEvalData` 进行精细控制。

**从帧数据中提取 FIZ 信息 (C++)**

```cpp
// 在 Tick 或处理 Live Link 数据的回调中
void AMyCameraActor::HandleLiveLinkData(const FLiveLinkSubjectFrameData& SubjectData)
{
    // 假设 LiveLinkCamController 是你的控制器组件
    if (ULiveLinkCameraController* CamController = Cast<ULiveLinkCameraController>(LiveLinkCamController))
    {
        // 获取用于镜头文件评估的数据
        const FLensFileEvalData& EvalData = CamController->GetLensFileEvalDataRef();

        // 你可以使用 EvalData 来查询你的镜头文件，获取更高级的映射（如畸变校正参数）
        // 通常，FIZ 的直接应用由控制器在 Tick 中自动完成。
        // 此处可以进行其他基于 EvalData 的自定义逻辑。
    }
}
```

## Demo 示例

以下是一个最小示例，展示如何在 C++ Actor 中使用 LiveLinkCameraController。

**MyLiveLinkCameraActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "LiveLinkCameraController.h"
#include "MyLiveLinkCameraActor.generated.h"

UCLASS()
class AMyLiveLinkCameraActor : public AActor
{
    GENERATED_BODY()

public:
    AMyLiveLinkCameraActor();

protected:
    virtual void BeginPlay() override;

    // 用于控制相机的组件
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Live Link")
    TObjectPtr<ULiveLinkControllerBase> LiveLinkController;

    // 实际被控制的相机组件
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Camera")
    TObjectPtr<UCineCameraComponent> CineCamera;
};
```

**MyLiveLinkCameraActor.cpp**
```cpp
#include "MyLiveLinkCameraActor.h"
#include "LiveLinkCameraController.h"
#include "CineCameraComponent.h"

AMyLiveLinkCameraActor::AMyLiveLinkCameraActor()
{
    PrimaryActorTick.bCanEverTick = true;

    // 创建相机组件
    CineCamera = CreateDefaultSubobject<UCineCameraComponent>(TEXT("CineCamera"));
    RootComponent = CineCamera;

    // 创建 Live Link 控制器组件，并设置其控制器类为相机控制器
    LiveLinkController = CreateDefaultSubobject<ULiveLinkControllerBase>(TEXT("LiveLinkController"));
    // 注意：在编辑器细节面板中设置 ControllerClass 更为常见，此处仅为演示
}

void AMyLiveLinkCameraActor::BeginPlay()
{
    Super::BeginPlay();

    // 通常控制器的初始化由引擎在组件注册时处理。
    // 你需要在蓝图或编辑器中为 LiveLinkController 组件选择 Subject 和设置更新标志。
}
```

## 模块依赖

从模块类型推断，该插件需要以下模块，但具体依赖需查阅 `Build.cs`。以下是根据功能推断的可能依赖：

| 模块 | 用途 |
|---|---|
| `LiveLinkInterface` | Live Link 核心接口，用于接收和处理实时链接数据 |
| `LiveLinkComponents` | 提供 LiveLink 组件基类和基础功能 |
| `LiveLink` | Live Link 主要运行时模块 |
| `CineCamera` | 提供 CineCameraComponent，用于高级电影相机控制 |
| `CameraCalibrationCore` | 可能用于与镜头文件（Lens File）系统集成 |

**注意**：`LiveLinkCameraEditor` 和 `LiveLinkCameraRecording` 模块可能还依赖编辑器相关模块（如 `UnrealEd`）或 Sequencer 录制模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-10-07 | `96352708` | - Renaming Base<Plugin>.ini to Default<Plugin>.ini | 规范化配置文件命名，将插件配置文件从 Base<Plugin>.ini 重命名为 Default<Plugin>.ini |
| 2025-04-22 | `92ef0a10` | - Update the LiveLinkCameraController to support dynamic filmback resolution from a frame data. | 更新控制器以支持从帧数据中获取动态的胶片背面（Filmback）分辨率 |
| 2025-01-27 | `ef0d3477` | [Sequencer] Update Tracks Names and Reorganize Tracks Order | [序列器] 更新轨道名称并重新组织轨道顺序 |
| 2025-01-23 | `fa1c08d3` | [Backout] - CL39424548 | 回滚一个提交（CL39424548） |
| 2025-01-23 | `c2e4648f` | [Sequencer] Update Tracks Names and Reorganize Tracks Order | [序列器] 更新轨道名称并重新组织轨道顺序 |

### 维护评价

- **活跃维护**：插件在 2025 年有多次实质性更新，包括功能增强（动态 Filmback 支持）和代码规范清理，表明仍在积极维护。
- **实验性标记**：尽管插件仍在更新，但 `.uplugin` 中 `IsBetaVersion` 为 `true`，意味着其 API 或行为在未来版本中可能发生破坏性变更。
- **推荐使用**：推荐用于虚拟制片流程中的实时相机控制。但鉴于其“实验性”状态，在生产环境中使用时需关注后续版本更新说明，并准备好应对可能的 API 调整。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LiveLinkCamera)
- 官方文档：未在 `.uplugin` 中提供。可参考 UE 官方文档中关于 [Live Link](https://docs.unrealengine.com/5.0/en-US/live-link-in-unreal-engine/) 和 [Virtual Production](https://docs.unrealengine.com/5.0/en-US/virtual-production-in-unreal-engine/) 的章节。