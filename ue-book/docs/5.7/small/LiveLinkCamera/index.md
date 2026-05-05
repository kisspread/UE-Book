# LiveLinkCamera

> Live Link plugin adding functionalities for camera handling

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | 否（IsBetaVersion = true） |
| 包含内容 | 是 |
| 模块 | LiveLinkCamera (Runtime), LiveLinkCameraEditor (Editor), LiveLinkCameraRecording (UncookedOnly) |
| 创建时间 | 2021-03-05 |
| 年龄标签 | 🆕（~5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/LiveLinkCamera) | |

## 用途

LiveLinkCamera 是 LiveLink 系统的相机专用控制器插件。它解决的核心问题是：**将外部设备（电影摄影机、追踪系统、虚拟摄像机等）通过 Live Link 协议实时传输的相机参数，自动应用到 UE5 的 CineCameraComponent 上**。

这个插件不仅仅传递 Transform（位置/旋转），还处理相机特有的专业参数：焦距（Focal Length）、光圈（Aperture）、对焦距离（Focus Distance）、Filmback（传感器尺寸）、FOV、宽高比、投影模式等。它与 CameraCalibrationCore 和 LensComponent 配合，支持通过 LensFile 进行编码器映射（Encoder Mapping），将物理镜头的编码器值转换为 UE5 可用的实际参数。

## 使用场景

- **虚拟制片（Virtual Production）**：在 LED Volume 拍摄中，将真实摄影机的运动和镜头参数（FIZ - Focus/Iris/Zoom）实时驱动场景中的虚拟相机
- **实时合成（Compositing）**：将追踪系统（如 Mo-Sys、Stype、NCAM）提供的相机数据映射到 UE5 场景中
- **镜头校准工作流**：配合 LensFile 资产，将物理镜头的编码器读数精确映射到焦距、光圈、对焦距离
- **Sequencer 录制**：通过 LiveLinkCameraRecording 模块，将 Live Link 相机数据录制到 Sequencer 轨道中，用于后期编辑
- **LiveLinkHub**：插件的 ProgramAllowlist 指定为 LiveLinkHub，说明它也是 LiveLinkHub 独立应用的核心组件之一

## 蓝图用法

LiveLinkCamera 本身不暴露 BlueprintCallable 函数——它的核心逻辑是通过 `ULiveLinkComponentController` 组件驱动的。你需要在 Actor 上添加 `ULiveLinkComponentController`，然后将控制器类设置为 `ULiveLinkCameraController`。

### 配置步骤

1. 在 Actor 上添加 **LiveLinkComponentController** 组件
2. 在组件的 Details 面板中，选择 Live Link Subject
3. 对于 Camera Role，控制器会自动使用 `ULiveLinkCameraController`

### 可配置属性（Details 面板）

| 属性 | 说明 |
|---|---|
| `bUseCameraRange` | 是否用 CineCamera 的 Min/Max 范围对归一化输入值做反归一化 |
| `LensFilePicker` | 选择 LensFile 资产，用于编码器映射（Encoder → 物理值） |
| `UpdateFlags.bApplyFieldOfView` | 是否应用 FOV |
| `UpdateFlags.bApplyAspectRatio` | 是否应用宽高比 |
| `UpdateFlags.bApplyFocalLength` | 是否应用焦距 |
| `UpdateFlags.bApplyProjectionMode` | 是否应用投影模式 |
| `UpdateFlags.bApplyFilmBack` | 是否应用 Filmback（传感器尺寸） |
| `UpdateFlags.bApplyAperture` | 是否应用光圈 |
| `UpdateFlags.bApplyFocusDistance` | 是否应用对焦距离 |

## C++ 用法

### 头文件引入

```cpp
#include "LiveLinkCameraController.h"
#include "Roles/LiveLinkCameraRole.h"
#include "Roles/LiveLinkCameraTypes.h"
```

### 基本用法

LiveLinkCameraController 继承自 `ULiveLinkControllerBase`，其核心接口在每帧 Tick 中被调用。以下是其工作流程的简化说明：

```cpp
// LiveLinkComponentController 会在每帧调用 Controller->Tick()
// LiveLinkCameraController::Tick() 的核心逻辑：

// 1. 从 LiveLink 帧数据中提取相机数据
const FLiveLinkCameraStaticData* StaticData = SubjectData.StaticData.Cast<FLiveLinkCameraStaticData>();
const FLiveLinkCameraFrameData* FrameData = SubjectData.FrameData.Cast<FLiveLinkCameraFrameData>();

// 2. 更新 LensFile 评估输入（Focus / Iris / Zoom）
LensFileEvalData.Input.Focus = FrameData->FocusDistance;
LensFileEvalData.Input.Iris = FrameData->Aperture;
LensFileEvalData.Input.Zoom = FrameData->FocalLength;

// 3. 应用到 CameraComponent
CameraComponent->SetFieldOfView(FrameData->FieldOfView);
CameraComponent->SetAspectRatio(FrameData->AspectRatio);

// 4. 对于 CineCameraComponent，还应用 Filmback 和 FIZ
CineCameraComponent->Filmback.SensorWidth = FrameData->FilmBackWidth;
CineCameraComponent->Filmback.SensorHeight = FrameData->FilmBackHeight;
```

来源：`Source/LiveLinkCamera/Private/LiveLinkCameraController.cpp`

### FIZ 应用逻辑

`ApplyFIZ()` 方法是镜头参数应用的核心，逻辑分两种情况：

**有 LensFile 时**：使用编码器映射
```cpp
// 如果有 Focus Encoder Mapping，将编码器值映射为实际对焦距离
if (LensFile->HasFocusEncoderMapping())
{
    CineCameraComponent->FocusSettings.ManualFocusDistance = 
        LensFile->EvaluateNormalizedFocus(LensFileEvalData.Input.Focus);
}
// 如果没有 Encoder Mapping 但有流式 Focus 数据，直接使用
else if (StaticData->bIsFocusDistanceSupported)
{
    CineCameraComponent->FocusSettings.ManualFocusDistance = LensFileEvalData.Input.Focus;
}
```

**无 LensFile 时**：分两种子情况
- `bUseCameraRange = true`：将 0-1 归一化值映射到 CineCamera 的 Min/Max 范围
- `bUseCameraRange = false`：直接使用流式传入的原始值（假设已经是物理单位）

来源：`Source/LiveLinkCamera/Private/LiveLinkCameraController.cpp`

### 检查角色支持

```cpp
// 控制器仅支持 Camera Role
bool ULiveLinkCameraController::IsRoleSupported(const TSubclassOf<ULiveLinkRole>& RoleToSupport)
{
    return RoleToSupport == ULiveLinkCameraRole::StaticClass();
}

// 期望附加到 CameraComponent
TSubclassOf<UActorComponent> ULiveLinkCameraController::GetDesiredComponentClass() const
{
    return UCameraComponent::StaticClass();
}
```

## Demo 示例

以下是一个最小化的 C++ 模块设置，用于通过 LiveLink 驱动相机：

**MyCamera.Build.cs**
```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Engine",
    "LiveLinkInterface",
    "LiveLink",
    "LiveLinkComponents",
    "LiveLinkCamera",       // 添加此依赖
    "CameraCalibrationCore",
    "CinematicCamera",
});
```

**MyCameraActor.h**
```cpp
#pragma once
#include "GameFramework/Actor.h"
#include "MyCameraActor.generated.h"

class UCineCameraComponent;
class ULiveLinkComponentController;

UCLASS()
class AMyCameraActor : public AActor
{
    GENERATED_BODY()
public:
    AMyCameraActor();

    UPROPERTY(VisibleAnywhere)
    UCineCameraComponent* CameraComponent;

    UPROPERTY(VisibleAnywhere)
    ULiveLinkComponentController* LiveLinkComponent;
};
```

**MyCameraActor.cpp**
```cpp
#include "MyCameraActor.h"
#include "CineCameraComponent.h"
#include "LiveLinkComponentController.h"

AMyCameraActor::AMyCameraActor()
{
    // 创建 CineCamera 组件
    CameraComponent = CreateDefaultSubobject<UCineCameraComponent>(TEXT("Camera"));
    RootComponent = CameraComponent;

    // 创建 LiveLink 组件控制器
    LiveLinkComponent = CreateDefaultSubobject<ULiveLinkComponentController>(TEXT("LiveLink"));
    
    // 在编辑器 Details 面板中配置：
    // - Subject: 选择你的 Live Link 相机源
    // - Camera Role 会自动使用 ULiveLinkCameraController
}
```

配置好 LiveLink Subject 后，运行时相机参数（焦距、光圈、FOV 等）会自动从外部设备更新到 CineCameraComponent。

## 模块依赖

### LiveLinkCamera（Runtime）

| 模块 | 用途 |
|---|---|
| `CameraCalibrationCore` | LensFile 资产和编码器映射 |
| `CinematicCamera` | UCineCameraComponent（电影级相机组件） |
| `Core` | UE 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `LiveLinkInterface` | LiveLink 数据接口定义（Role、FrameData 等） |
| `LiveLink` | LiveLink 运行时框架 |
| `LiveLinkComponents` | ULiveLinkComponentController 组件 |
| `LensComponent`（Private） | ULensComponent，处理畸变和 Nodal Offset |

### LiveLinkCameraEditor（Editor）

| 模块 | 用途 |
|---|---|
| `PropertyEditor` | Details 面板自定义 |
| `DetailCustomizations` | IDetailCustomization 基础设施 |
| `LiveLinkCamera` | 运行时模块 |
| `Slate` / `SlateCore` | UI 框架 |

### LiveLinkCameraRecording（UncookedOnly）

| 模块 | 用途 |
|---|---|
| `LiveLinkMovieScene` | LiveLink 与 Sequencer 的桥接 |
| `LiveLinkSequencer` | Sequencer 中的 LiveLink 集成 |
| `Sequencer` | Sequencer 编辑器 |
| `MovieScene` / `MovieSceneTracks` | Sequencer 轨道系统 |
| `TakeTrackRecorders` | Take Recorder 轨道录制器基础设施 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-04-22 | `91a4f38` | 更新 LiveLinkCameraController 支持从帧数据动态获取 Filmback 分辨率；更新 LiveLinkOpenTrackIOTypes 支持 Blueprint；添加自定义数据字段推送到 LiveLink 帧数据 |
| 2025-01-27 | `ef0d347` | Sequencer 轨道名称更新和轨道排序重组（UE-221625） |
| 2025-01-23 | `fa1c08d` | 回退上一次的 Sequencer 轨道重命名变更 |

### 维护评价

- **状态**：活跃维护中
- **创建时间**：2021-03-05（~5 年）
- **最近更新**：2025-04-22，有实质性功能更新（动态 Filmback 支持）
- **IsBetaVersion = true**：插件仍标记为 Beta 版
- **ProgramAllowlist = LiveLinkHub**：仅在 LiveLinkHub 中可用，标准 Editor 中不会自动加载
- **大量 DEPRECATED 标记**：5.1 版本中 Nodal Offset、畸变评估、裁剪 Filmback 等功能已迁移到 LensComponent，插件本身聚焦于 FIZ（Focus/Iris/Zoom）参数传递
- **推荐使用**：虚拟制片项目推荐使用，但需注意它仍在 Beta 阶段，API 可能变动

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/LiveLinkCamera)
- 官方文档：无（.uplugin 中 DocsURL 为空）
- 依赖插件：[LiveLink](../LiveLink/index.md)、CameraCalibrationCore、LensComponent
