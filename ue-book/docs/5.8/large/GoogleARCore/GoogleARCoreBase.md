# Google ARCore

> Support for Google's AR platform.

| 属性 | 值 |
|---|---|
| 中文名 | 谷歌ARCore |
| 分类 | Augmented Reality |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、C++ 类） |
| 模块 | `GoogleARCoreBase` (Runtime), `GoogleARCoreRendering` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-01-28 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AR/Google/GoogleARCore) | |

## 用途

`GoogleARCore` 插件是 Unreal Engine 对 Google ARCore 增强现实平台的完整集成实现。它并非一个简单的功能模块，而是作为 UE 内置 AR 框架 (`UARSessionConfig`， `UARSystemSupport`) 的一个具体后端，将 ARCore 的 SDK 功能（如平面检测、图像追踪、面部追踪、光照估计、深度感知等）暴露给引擎和蓝图系统。

该插件解决了在 Android 设备上使用 UE 开发 AR 应用的核心问题：
1.  **平台集成**：封装了 ARCore 的 NDK 和 Java 层调用，处理了设备生命周期、权限申请、APK 安装检查等平台特定逻辑。
2.  **数据抽象**：将 ARCore 原生的 `ArSession`、`ArFrame`、`ArTrackable` 等句柄转换为 UE 友好的 `UObject`（如 `UGoogleARCoreAugmentedImage`， `UGoogleARCoreAugmentedFace`），并融入 UE 的反射和垃圾回收系统。
3.  **渲染支持**：提供了专用的相机纹理管理（包括 Vulkan 硬件缓冲区支持）和渲染管线集成（通过 `FGoogleARCoreXRCamera` 和视图扩展），实现“透过式”AR 相机效果。
4.  **跨平台兼容**：通过 UE 的 AR 系统接口，使得针对该插件编写的 AR 功能代码（如蓝图）在理念上可以更容易地迁移到其他 AR 平台（如 ARKit）。

## 使用场景

- 你在开发一个 **Android AR 游戏或应用**，需要识别现实世界的平面并放置虚拟物体。
- 你需要实现 **图像识别**，让应用识别特定的 2D 图片并触发 AR 内容。
- 你正在制作一个 **AR 试妆或 AR 面具** 应用，需要精确追踪用户的面部网格和特定区域（如鼻尖、额头）。
- 你需要利用设备摄像头获取 **CPU 可访问的原始图像数据** 进行计算机视觉处理。
- 你的 AR 应用需要感知 **环境光照**，并使虚拟物体的光照与真实环境匹配。
- 你希望为虚拟物体创建 **持久化的锚点**，使其在 AR 会话暂停或恢复后仍能固定在原地。

## 蓝图用法

本插件主要通过 UE 的通用 AR 蓝图接口（`Start ARSession`， `Get All Tracked Planes` 等）工作，但也提供了一些 ARCore 特有的扩展节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Add Runtime Candidate Image From Rawbytes` | 从原始灰度像素数据动态添加需要追踪的图像到会话配置中。 | `UGoogleARCoreSessionFunctionLibrary` |
| `Get Point` | 获取点云中指定索引的点的世界位置和置信度。 | `UGoogleARCorePointCloud` |
| `Get Local To World Transform Of Region` | 获取增强面部上指定区域（鼻尖、左/右额头）的局部到世界变换。 | `UGoogleARCoreAugmentedFace` |
| `Get Augmented Image Database` | 获取 `UGoogleARCoreSessionConfig` 中配置的增强图像数据库资产。 | `UGoogleARCoreSessionConfig` |

### 使用示例（蓝图描述）

**1. 启动 AR 会话并检测平面：**
1.  创建一个 `UGoogleARCoreSessionConfig` 资产，在其详细面板中启用“水平面检测”。
2.  使用 `Start ARSession` 节点，并传入上述配置对象。
3.  使用 `Get All Tracked Planes` 节点定期获取检测到的平面列表。
4.  对每个获取到的 `UARTrackedPlane`，使用 `Get Transform` 获取其变换，并在该位置生成一个虚拟网格体。

**2. 动态识别图像：**
1.  在某个事件（如按钮点击）中，获取一张图片的纹理资产或原始像素数据。
2.  调用 `Add Runtime Candidate Image From Rawbytes` 节点，传入像素数据、宽高和物理尺寸。
3.  重启 AR 会话（使用修改后的 `UARSessionConfig`）。
4.  当图像被识别时，`On Trackable Added` 事件将触发，传入的 `UARTrackedImage` 对象包含识别信息。

**3. 查询面部区域：**
1.  确保 `UGoogleARCoreSessionConfig` 中的“增强面部模式”设置为“姿态和网格”。
2.  使用 `Get All Tracked Faces` 节点获取追踪到的面部。
3.  对每个 `UGoogleARCoreAugmentedFace` 对象，调用 `Get Local To World Transform Of Region`，指定区域（如 `NoseTip`）。
4.  在返回的变换位置生成一个跟随鼻尖的虚拟物体（如墨镜）。

## C++ 用法

插件的核心逻辑在私有类中，C++ 开发者主要通过 `FGoogleARCoreDevice` 单例与引擎的 AR 系统交互。

### 头文件引入

```cpp
#include "GoogleARCoreBaseModule.h"
#include "GoogleARCoreDevice.h"
#include "GoogleARCoreSession.h"
```

### 基本用法

**1. 检查 ARCore 可用性并启动会话**

来源：基于 `FGoogleARCoreDevice` 公共接口推断。

```cpp
// 获取设备单例
FGoogleARCoreDevice* ARDevice = FGoogleARCoreDevice::GetInstance();
if (ARDevice)
{
    // 检查 ARCore APK 是否已安装且兼容
    EGoogleARCoreAvailability Availability = ARDevice->CheckARCoreAPKAvailability();
    if (Availability == EGoogleARCoreAvailability::SupportedApkInstalled)
    {
        // 配置 AR 会话
        UGoogleARCoreSessionConfig* Config = NewObject<UGoogleARCoreSessionConfig>();
        Config->bHorizontalPlaneDetection = true;
        Config->CameraFacing = EGoogleARCoreCameraFacing::Back;
        
        // 开始会话
        ARDevice->StartARCoreSessionRequest(Config);
    }
    else
    {
        // 处理需要安装或更新 ARCore 的情况
        EGoogleARCoreInstallStatus InstallStatus;
        ARDevice->RequestInstall(true, InstallStatus);
    }
}
```

**2. 在游戏循环中获取 AR 数据**

来源：基于 `FGoogleARCoreDevice` 的 `UpdateGameFrame` 和查询函数推断。

```cpp
void AMyARActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    
    FGoogleARCoreDevice* ARDevice = FGoogleARCoreDevice::GetInstance();
    if (ARDevice && ARDevice->GetIsARCoreSessionRunning())
    {
        // 更新设备数据，应每帧调用
        ARDevice->UpdateGameFrame(GetWorld());
        
        // 获取相机跟踪状态
        EGoogleARCoreTrackingState TrackingState = ARDevice->GetTrackingState();
        if (TrackingState == EGoogleARCoreTrackingState::Tracking)
        {
            // 获取最新的相机位姿
            FTransform CameraPose = ARDevice->GetLatestPose();
            
            // 执行射线检测
            TArray<FARTraceResult> HitResults;
            ARDevice->ARLineTrace(ScreenPosition, EGoogleARCoreLineTraceChannel::PlaneUsingExtent, HitResults);
            
            // 获取更新的追踪平面
            TArray<UARTrackedPlane*> UpdatedPlanes;
            ARDevice->GetUpdatedTrackables<UARTrackedPlane>(UpdatedPlanes);
        }
    }
}
```

### 进阶用法

**访问 ARCore 原生会话和帧（需要 Android 平台宏）**

对于需要极致性能或使用原生 NDK 特性（如自定义渲染）的场景，可以获取原生句柄。

```cpp
#if PLATFORM_ANDROID
    void* NativeSessionPtr = ARDevice->GetARSessionRawPointer();
    ArSession* NativeSession = static_cast<ArSession*>(NativeSessionPtr);
    
    void* NativeFramePtr = ARDevice->GetGameThreadARFrameRawPointer();
    ArFrame* NativeFrame = static_cast<ArFrame*>(NativeFramePtr);
    
    // 现在可以直接使用 ARCore NDK API 进行操作
    // 例如，获取 CPU 图像
    ArImage* arImage = nullptr;
    ArFrame_acquireCameraImage(NativeSession, NativeFrame, &arImage);
    // ... 处理图像数据 ...
    ArImage_release(arImage);
#endif
```

## Demo 示例

一个最小的 Actor 示例，用于检测水平面并在检测到的第一个平面上放置一个立方体。

```cpp
// MyARPlaneDetector.h
#pragma once
#include "GameFramework/Actor.h"
#include "GoogleARCoreTypes.h"
#include "MyARPlaneDetector.generated.h"

UCLASS()
class AMyARPlaneDetector : public AActor
{
    GENERATED_BODY()
    
public:
    AMyARPlaneDetector();

    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

private:
    void StartARSession();
    void UpdateARData();

    UPROPERTY()
    AActor* SpawnedCube;

    bool bPlanePlaced;
};
```

```cpp
// MyARPlaneDetector.cpp
#include "MyARPlaneDetector.h"
#include "GoogleARCoreDevice.h"
#include "GoogleARCoreSessionConfig.h"
#include "ARBlueprintLibrary.h"
#include "Engine/World.h"

AMyARPlaneDetector::AMyARPlaneDetector()
{
    PrimaryActorTick.bCanEverTick = true;
    bPlanePlaced = false;
    SpawnedCube = nullptr;
}

void AMyARPlaneDetector::BeginPlay()
{
    Super::BeginPlay();
    StartARSession();
}

void AMyARPlaneDetector::StartARSession()
{
    FGoogleARCoreDevice* ARDevice = FGoogleARCoreDevice::GetInstance();
    if (ARDevice && ARDevice->CheckARCoreAPKAvailability() == EGoogleARCoreAvailability::SupportedApkInstalled)
    {
        UGoogleARCoreSessionConfig* Config = NewObject<UGoogleARCoreSessionConfig>();
        Config->bHorizontalPlaneDetection = true;
        Config->LightEstimationMode = EARLightEstimationMode::AmbientIntensityEstimate;
        
        ARDevice->StartARCoreSessionRequest(Config);
    }
}

void AMyARPlaneDetector::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    if (!bPlanePlaced)
    {
        UpdateARData();
    }
}

void AMyARPlaneDetector::UpdateARData()
{
    FGoogleARCoreDevice* ARDevice = FGoogleARCoreDevice::GetInstance();
    if (!ARDevice || !ARDevice->GetIsARCoreSessionRunning())
    {
        return;
    }

    ARDevice->UpdateGameFrame(GetWorld());

    if (ARDevice->GetTrackingState() != EGoogleARCoreTrackingState::Tracking)
    {
        return;
    }

    TArray<UARTrackedPlane*> TrackedPlanes;
    ARDevice->GetUpdatedTrackables<UARTrackedPlane>(TrackedPlanes);

    for (UARTrackedPlane* Plane : TrackedPlanes)
    {
        if (Plane && Plane->GetTrackingState() == EARTrackingState::Tracking && Plane->GetSubsumedBy() == nullptr)
        {
            FTransform PlaneTransform = Plane->GetLocalToWorldTransform();
            
            if (SpawnedCube == nullptr)
            {
                // 在平面中心生成一个立方体
                FActorSpawnParameters SpawnParams;
                SpawnedCube = GetWorld()->SpawnActor<AActor>(AStaticMeshActor::StaticClass(), PlaneTransform, SpawnParams);
                // 假设已在编辑器中为立方体设置了网格体
            }
            else
            {
                // 更新立方体位置跟随平面
                SpawnedCube->SetActorTransform(PlaneTransform);
            }
            
            bPlanePlaced = true;
            break;
        }
    }
}
```

## 模块依赖

该插件的 `Build.cs` 文件未直接提供，但根据其功能可推断其依赖关系。使用 `GoogleARCoreBase` 模块时，你的项目模块需要依赖：

| 模块 | 用途 |
|---|---|
| `GoogleARCoreBase` | 插件的核心功能模块，包含设备管理、会话、数据类型等。 |
| `AugmentedReality` | UE 内置的跨平台 AR 框架模块，提供基础接口和类型。 |

（注：其他如 `Core`， `Engine`， `Slate` 等均为常见依赖，已省略。）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复了在格式化函数中使用枚举可能导致输出错误的问题 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了32位与64位格式说明符不匹配导致的潜在问题 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF |
| 2026-04-08 | `86879cf0` | Fix unreachable code warnings | 修复了不可达代码警告 |
| 2026-03-19 | `7662e97c` | Fix incorrect scene texture sampling uv in postprocess materials after TSR. This also caused incorre | 修复了TSR后后期处理材质中场景纹理采样UV不正确的问题 |

### 维护评价

`GoogleARCore` 插件自 **2019年1月** 起存在，是一个成熟的**老古董**级别的插件。

**维护评价：维护不活跃。**
-   **最近更新**：最近几次更新（2026年3月-4月）均为编译警告修复、日志宏迁移和特定渲染问题修复，属于**维护性提交**，没有新的 AR 功能特性加入。
-   **功能状态**：插件的功能集在几年前已基本稳定，覆盖了 ARCore 的主要能力。其核心架构（如 `FGoogleARCoreDevice`）未发生重大变化。
-   **平台限制**：此插件仅支持 **Android** 平台。
-   **依赖关系**：作为 UE AR 框架的一部分，其发展受 UE 版本和 Google ARCore SDK 版本共同影响。
-   **建议**：该插件**功能完善且稳定**，适用于已在生产中使用或计划仅针对 Android 发布 AR 应用的项目。但由于缺乏新的功能性更新，开发者应关注 ARCore SDK 的官方更新，并留意 UE 后续版本中可能对 AR 框架的改进。对于需要最新 ARCore 特性的新项目，建议评估此插件的现有功能是否满足需求。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AR/Google/GoogleARCore)
- [官方文档](https://developers.google.com/ar/)
- [UE AR 官方文档](https://docs.unrealengine.com/5.8/en-US/ar-overview-in-unreal-engine/)