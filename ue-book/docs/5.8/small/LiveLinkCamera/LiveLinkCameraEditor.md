# LiveLinkCamera

> Live Link plugin adding functionalities for camera handling

| 属性 | 值 |
|---|---|
| 中文名 | 实时链接相机 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产） |
| 模块 | `LiveLinkCamera` (Runtime), `LiveLinkCameraEditor` (Runtime), `LiveLinkCameraRecording` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-03-05 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LiveLinkCamera) | |

## 用途

LiveLinkCamera 插件扩展了 Unreal Engine 的 **Live Link** 系统，专门用于处理来自外部设备（如虚拟摄影机、动作捕捉系统、其他数字内容创作软件）的**相机数据流**。它不仅仅是一个数据接收器，更重要的是提供了一套标准化的**相机数据角色（Role）**和**控制组件**，使得外部相机的位置、旋转、镜头参数（如焦距、光圈）等数据能够被引擎原生识别、解释并实时应用到场景中的虚拟相机上。这解决了在虚拟制片（Virtual Production）和实时渲染工作流中，如何将现实世界或数字世界的摄影机运动与参数无缝、精确地映射到UE场景中的核心问题。

## 使用场景

-   **虚拟制片（Virtual Production）**：在 LED 墙或绿幕前拍摄时，使用外部物理摄影机或虚拟摄影机系统（如 MotionBuilder、Maya）来控制 UE 中的虚拟摄影机，实现摄像机运动与实拍背景的实时同步。
-   **动画预演与动捕**：将动捕系统（如 Vicon、OptiTrack）中记录的摄影机动画数据，通过 Live Link 实时流送至 UE 进行预览或最终渲染。
-   **多软件协同**：在 DCC 软件（如 3ds Max, Blender）中调整虚拟摄影机，通过 Live Link 插件将变更实时反馈到 UE 中，方便美术迭代。
-   **远程协作与监控**：远程的摄影指导可以实时操控 UE 中的虚拟摄影机，用于远程审片或实时合成预览。

## 蓝图用法

插件通过 **Live Link 角色** 和 **控制器组件** 来工作。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Live Link Role` | 获取用于识别相机数据的 Live Link 角色（通常是 `ULiveLinkCameraRole`）。用于在蓝图中过滤或查找特定类型的 Live Link 主体。 | `ULiveLinkRole` (子类) |
| `Live Link Component Controller` | 场景中的核心组件，用于绑定一个 Live Link 主体（Subject），并将其数据应用到其关联的 Actor（如 CineCameraActor）上。 | `ULiveLinkComponentController` |
| `Get Camera Frame Data` | 从控制器获取当前帧的相机特定数据（如焦距、光圈）。 | `ULiveLinkCameraController` |
| `Set Live Link Subject` | 在运行时动态设置控制器组件要监听的 Live Link 主体名称。 | `ULiveLinkComponentController` |

### 使用示例

1.  **基本设置**：
    -   在场景中放置一个 `CineCameraActor`。
    -   给它添加一个 `Live Link Component Controller` 组件。
    -   在组件的细节面板中，设置 `Subject Representation`（主体表示）为你在外部设备（如 Live Link Hub）中广播的相机主体名称。
    -   将 `Controller` 设置为 `ULiveLinkCameraController`。此时，外部相机数据会驱动这个 CineCameraActor。
2.  **蓝图动态控制**：
    -   使用 `Get Live Link Subjects` 节点获取所有可用主体。
    -   通过筛选 `Role` 为 `ULiveLinkCameraRole` 来找到所有相机主体。
    -   使用 `Set Live Link Subject` 节点，将玩家控制或某个事件触发的相机切换到指定的外部相机数据源。

## C++ 用法

### 头文件引入

```cpp
#include "LiveLinkCameraRole.h" // 定义相机数据角色
#include "LiveLinkComponentController.h" // 核心控制器组件
```

### 基本用法

在 C++ 中，你通常需要创建或引用 `LiveLinkCameraRole` 来定义你的数据结构，并使用 `LiveLinkComponentController` 来应用数据。

```cpp
// (1) 获取一个 Live Link 主体的数据帧（如果已存在于 Live Link 系统中）
FLiveLinkSubjectKey SubjectKey = /* ... */;
TSubclassOf<ULiveLinkRole> CameraRole = ULiveLinkCameraRole::StaticClass();
if (GEngine->GetEngineSubsystem<ULiveLinkSubsystem>()->DoesSubjectSupportRole(SubjectKey, CameraRole))
{
    // 获取包含相机数据的帧数据
    FLiveLinkCameraFrameData CameraFrameData;
    // ... 通过 Live Link 子系统获取数据
    FVector CameraLocation = CameraFrameData.Transform.GetLocation();
    float FocalLength = CameraFrameData.FocalLength;
}

// (2) 编程方式控制一个已有的 Live Link 控制器组件
ULiveLinkComponentController* Controller = MyActor->FindComponentByClass<ULiveLinkComponentController>();
if (Controller)
{
    FLiveLinkSubjectKey NewSubject = /* ... */;
    Controller->SetSubjectRepresentation(FLiveLinkSubjectRepresentation(NewSubject, ULiveLinkCameraRole::StaticClass()));
    Controller->SetEnabled(true);
}
```

### 进阶用法：自定义相机数据处理

你可以继承 `ULiveLinkCameraRole` 或相关的类来实现自定义的相机数据处理逻辑，例如添加额外的镜头畸变参数。但这通常需要同时修改或扩展外部数据源（Live Link Hub 或自定义插件）来发送这些额外数据。

## Demo 示例

以下是一个最小化的自定义 `AActor`，它通过 Live Link 相机数据控制自身旋转的示例。

**MyLiveLinkCameraActor.h**
```cpp
#pragma once
#include "GameFramework/Actor.h"
#include "LiveLinkCameraRole.h"
#include "MyLiveLinkCameraActor.generated.h"

UCLASS()
class AMyLiveLinkCameraActor : public AActor
{
    GENERATED_BODY()

public:
    AMyLiveLinkCameraActor();

    virtual void Tick(float DeltaTime) override;

protected:
    // 要监听的 Live Link 主体名称
    UPROPERTY(EditAnywhere, Category = "Live Link")
    FName SubjectName = "MyVirtualCam";

private:
    // 缓存的 Live Link 角色类型
    TSubclassOf<ULiveLinkRole> CameraRoleClass;
};
```

**MyLiveLinkCameraActor.cpp**
```cpp
#include "MyLiveLinkCameraActor.h"
#include "LiveLinkSubsystem.h"
#include "LiveLinkController.h"
#include "Roles/LiveLinkCameraRole.h"

AMyLiveLinkCameraActor::AMyLiveLinkCameraActor()
{
    PrimaryActorTick.bCanEverTick = true;
    CameraRoleClass = ULiveLinkCameraRole::StaticClass();
}

void AMyLiveLinkCameraActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    ULiveLinkSubsystem* LiveLinkSubsystem = GEngine->GetEngineSubsystem<ULiveLinkSubsystem>();
    if (!LiveLinkSubsystem) return;

    // 构建要查询的主体键
    FLiveLinkSubjectKey TargetKey(FLiveLinkSourceGuid(), SubjectName);

    // 检查主体是否支持相机角色
    if (LiveLinkSubsystem->DoesSubjectSupportRole(TargetKey, CameraRoleClass))
    {
        // 获取一帧数据
        FLiveLinkStaticDataStruct StaticData;
        FLiveLinkFrameDataStruct FrameData;
        if (LiveLinkSubsystem->GetSubjectData(TargetKey, StaticData, FrameData))
        {
            // 将帧数据解释为相机数据
            if (FLiveLinkCameraFrameData* CameraFrameData = FrameData.Cast<FLiveLinkCameraFrameData>())
            {
                // 应用旋转（例如，只应用旋转）
                SetActorRotation(CameraFrameData.Transform.GetRotation());
            }
        }
    }
}
```

## 模块依赖

从 Build.cs 分析，该插件依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `LiveLinkInterface` | Live Link 系统的核心接口定义，包括角色、主体、帧数据等基础结构。 |
| `LiveLinkComponents` | 提供 `ULiveLinkComponentController` 等将 Live Link 数据应用到 Actor 的基础组件。 |

**使用者无需直接依赖** `LiveLinkCamera` 或 `LiveLinkCameraEditor` 模块，这些是插件内部模块。你只需确保你的项目启用了 `LiveLink` 和 `LiveLinkCamera` 插件即可。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-10-07 | `96352708` | - Renaming Base<Plugin>.ini to Default<Plugin>.ini | 适配引擎配置文件命名规范更改，将 `Base` 前缀改为 `Default`。 |
| 2025-04-22 | `92ef0a10` | - Update the LiveLinkCameraController to support dynamic filmback resolution from a frame data. | 增强控制器，支持从帧数据中动态获取摄影机胶片门分辨率。 |
| 2025-01-27 | `ef0d3477` | [Sequencer] Update Tracks Names and Reorganize Tracks Order | 更新序列器轨道名称并重组轨道顺序，属于编辑器UI/UX优化。 |
| 2025-01-23 | `fa1c08d3` | [Backout] - CL39424548 | 回滚了前一次提交（`c2e4648f`），属于问题修复。 |
| 2025-01-23 | `c2e4648f` | [Sequencer] Update Tracks Names and Reorganize Tracks Order | （被回滚）序列器轨道名称更新与顺序重组。 |

### 维护评价

-   **创建时间**：插件于 2021 年 3 月创建，已有约 5 年历史。
-   **更新频率**：从提交记录看，直到 2025 年初仍有功能性更新（动态 filmback 分辨率支持）和常规维护（适配引擎规范、UI 优化）。最后活动在 2025 年 10 月。
-   **维护状态**：**仍在活跃维护中**。作为虚拟制作管线的核心组件，Epic 持续进行改进和错误修复。
-   **已知限制**：作为实验性（Beta）插件，其 API 和行为在未来的版本中可能发生变化。功能深度依赖于外部 Live Link 数据源（如 LiveLinkHub）的实现。
-   **推荐**：**强烈推荐**在任何涉及外部相机数据集成的 UE 虚拟制作项目中使用。它是该领域的事实标准。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LiveLinkCamera)
-   [官方文档](https://docs.unrealengine.com) （搜索 “Live Link” 和 “Virtual Production Camera”）
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LiveLinkCamera/Tests) （如果存在）