# Google ARCore

> Support for Google's Google AR platform.

| 属性 | 值 |
|---|---|
| 分类 | Augmented Reality |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GoogleARCoreBase` (Runtime), `GoogleARCoreRendering` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-01-28 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/AR/Google/GoogleARCore) | |

## 用途

GoogleARCore 是 Unreal Engine 内置的 Google ARCore 平台接入插件，为 Android 设备提供增强现实（AR）能力。它封装了 ARCore C API（`arcore_c_api.h`），通过 UE 的 `FARSystemSupportBase` 和 `IXRTrackingSystem` 接口，将 ARCore 的平面检测、图像追踪、人脸追踪、光照估计、深度感知等功能统一暴露给蓝图和 C++ 开发者。

该插件属于 **EnabledByDefault=false**，需要在项目设置中手动启用，且仅在 Android 平台上可用（实际功能代码通过 `#if PLATFORM_ANDROID` 保护）。编辑器和其他平台上的模块会以 stub 形式加载，不提供实际 AR 功能。

### 架构概览

```
┌─────────────────────────────────────────────────────┐
│  UE AR 系统 (FARSystemSupportBase / IXRTrackingSystem)│
├─────────────────────────────────────────────────────┤
│  FGoogleARCoreXRTrackingSystem  ← 跟踪系统入口      │
│       ↓                                              │
│  FGoogleARCoreDevice           ← 设备管理/生命周期   │
│       ↓                                              │
│  FGoogleARCoreSession          ← ARCore 会话封装     │
│       ↓                                              │
│  FGoogleARCoreFrame            ← 每帧数据处理        │
│       ↓                                              │
│  ARCore C API (arcore_c_api.h)                       │
└─────────────────────────────────────────────────────┘
```

## 使用场景

- 你在开发 Android AR 应用，需要在真实世界中放置虚拟物体 → 启用 GoogleARCore 插件，使用平面检测 + 锚点
- 你需要识别特定图片并触发 AR 内容 → 使用 Augmented Image 功能（`UGoogleARCoreAugmentedImage`）
- 你需要在用户脸上叠加 AR 效果 → 启用 Augmented Face 模式
- 你需要获取真实世界的光照信息来匹配虚拟物体 → 使用 Light Estimation
- 你需要将 AR 摄像头画面作为游戏背景渲染 → 使用 Passthrough Camera 渲染系统
- 你需要获取深度信息实现遮挡 → 使用深度传感器（Depth Sensor）

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddRuntimeCandidateImageFromRawbytes` | 运行时从灰度像素数据添加追踪图片，需重启会话生效 | `UGoogleARCoreSessionFunctionLibrary` |
| `GetAugmentedImageDatabase` | 获取当前配置的增强图片数据库 | `UGoogleARCoreSessionConfig` |
| `SetAugmentedImageDatabase` | 设置增强图片数据库 | `UGoogleARCoreSessionConfig` |
| `CreateARCoreSessionConfig` | 静态工厂方法，创建 ARCore 会话配置 | `UGoogleARCoreSessionConfig` |
| `IsUpdated` | 检查点云是否在本帧更新 | `UGoogleARCorePointCloud` |
| `GetPointNum` | 获取点云中的点数量 | `UGoogleARCorePointCloud` |
| `GetPoint` | 获取指定索引的点位置和置信度 | `UGoogleARCorePointCloud` |
| `GetPointId` | 获取指定索引的点 ID（跨帧持久） | `UGoogleARCorePointCloud` |
| `ReleasePointCloud` | 释放点云资源 | `UGoogleARCorePointCloud` |
| `GetFocalLength` | 获取相机焦距（像素） | `UGoogleARCoreCameraIntrinsics` |
| `GetPrincipalPoint` | 获取相机主点（像素） | `UGoogleARCoreCameraIntrinsics` |
| `GetImageDimensions` | 获取图像尺寸 | `UGoogleARCoreCameraIntrinsics` |
| `GetWidth` / `GetHeight` | 获取相机图像宽高 | `UGoogleARCoreCameraImage` |
| `GetPlaneCount` | 获取图像数据平面数 | `UGoogleARCoreCameraImage` |
| `Release` | 释放相机图像资源 | `UGoogleARCoreCameraImage` |
| `GetLocalToWorldTransformOfRegion` | 获取面部区域的世界变换 | `UGoogleARCoreAugmentedFace` |
| `GetLocalToTrackingTransformOfRegion` | 获取面部区域的追踪空间变换 | `UGoogleARCoreAugmentedFace` |

### 事件代理

| 代理 | 说明 | 类型 |
|---|---|---|
| `OnConfigCamera` | ARSession 启动前调用，返回支持的相机配置列表（VGA、720p、GPU纹理分辨率） | `UGoogleARCoreEventManager` (蓝图可绑定) |
| `FGoogleARCoreDelegates::OnCameraConfig` | 同上，C++ 多播委托 | 静态委托 |

### 使用示例（蓝图描述）

**基本 AR 会话启动：**
1. 创建 `UGoogleARCoreSessionConfig` 资产，配置平面检测、光照估计等选项
2. 使用 `Start AR Session` 节点（来自 AugmentedReality 模块）传入配置
3. 通过 `Get All Tracked Planes`、`Line Trace Tracked Objects` 等跨平台 AR 节点获取追踪数据

**运行时添加追踪图片：**
1. 将图片灰度数据转为 `TArray<uint8>`
2. 调用 `AddRuntimeCandidateImageFromRawbytes`，传入 SessionConfig、像素数据、宽高、名称、物理宽度
3. 使用返回的 `UARCandidateImage` 对象进行图片追踪

## C++ 用法

### 头文件引入

```cpp
#include "GoogleARCoreTypes.h"
#include "GoogleARCoreSessionConfig.h"
#include "GoogleARCoreFunctionLibrary.h"
#include "GoogleARCoreAugmentedImage.h"
#include "GoogleARCoreAugmentedFace.h"
#include "GoogleARCoreCameraImage.h"
#include "GoogleARCoreCameraIntrinsics.h"
```

### 基本用法 — 检查 ARCore 可用性并启动会话

```cpp
// 检查 ARCore 可用性（来源：GoogleARCoreDevice.h）
FGoogleARCoreDevice* Device = FGoogleARCoreDevice::GetInstance();
EGoogleARCoreAvailability Availability = Device->CheckARCoreAPKAvailability();

if (Availability == EGoogleARCoreAvailability::SupportedInstalled)
{
    // 安装并启动 AR 会话
    EGoogleARCoreInstallStatus InstallStatus;
    Device->RequestInstall(true, InstallStatus);

    // 创建 ARCore 会话配置
    UGoogleARCoreSessionConfig* Config = UGoogleARCoreSessionConfig::CreateARCoreSessionConfig(
        true,   // bHorizontalPlaneDetection
        true,   // bVerticalPlaneDetection
        EARLightEstimationMode::AmbientIntensityEstimate,
        EARFrameSyncMode::SyncImageAndCamera,
        true,   // bEnableAutoFocus
        true,   // bEnableAutomaticCameraOverlay
        true    // bEnableAutomaticCameraTracking
    );

    Device->StartARCoreSessionRequest(Config);
}
```

### 进阶用法 — 获取点云和相机图像

```cpp
// 获取最新点云（来源：GoogleARCoreAPI.h / GoogleARCoreDevice.h）
UGoogleARCorePointCloud* PointCloud = nullptr;
EGoogleARCoreFunctionStatus Status = Device->GetLatestPointCloud(PointCloud);
if (Status == EGoogleARCoreFunctionStatus::Success && PointCloud)
{
    int32 PointNum = PointCloud->GetPointNum();
    for (int32 i = 0; i < PointNum; i++)
    {
        FVector WorldPos;
        float Confidence;
        PointCloud->GetPoint(i, WorldPos, Confidence);
        // 使用 WorldPos 和 Confidence
    }
}

// 获取相机图像（CPU 访问）
UGoogleARCoreCameraImage* CameraImage = nullptr;
Status = Device->AcquireCameraImage(CameraImage);
if (Status == EGoogleARCoreFunctionStatus::Success && CameraImage)
{
    int32 Width = CameraImage->GetWidth();
    int32 Height = CameraImage->GetHeight();
    int32 PlaneCount = CameraImage->GetPlaneCount();

    for (int32 Plane = 0; Plane < PlaneCount; Plane++)
    {
        int32 PixelStride, RowStride, DataLength;
        const uint8* PlaneData = CameraImage->GetPlaneData(Plane, PixelStride, RowStride, DataLength);
        // 处理平面数据...
    }
    CameraImage->Release();  // 显式释放
}
```

### 进阶用法 — 相机配置

```cpp
// 自定义相机配置（来源：GoogleARCoreTypes.h）
FGoogleARCoreDelegates::OnCameraConfig.AddLambda(
    [](const TArray<FGoogleARCoreCameraConfig>& SupportedConfigs)
    {
        // SupportedConfigs 通常包含 3 个配置：
        // - VGA 分辨率 CPU 图像
        // - 720p 分辨率 CPU 图像
        // - 与 GPU 纹理匹配的 CPU 图像
        for (const auto& Config : SupportedConfigs)
        {
            UE_LOG(LogTemp, Log, TEXT("Camera: %s, CPU Image: %dx%d, GPU Texture: %dx%d"),
                *Config.CameraID,
                Config.CameraImageResolution.X, Config.CameraImageResolution.Y,
                Config.CameraTextureResolution.X, Config.CameraTextureResolution.Y);
        }
    });
```

### 进阶用法 — 增强面部追踪

```cpp
// 配置面部追踪（来源：GoogleARCoreAugmentedFace.h）
UGoogleARCoreSessionConfig* FaceConfig = NewObject<UGoogleARCoreSessionConfig>();
FaceConfig->AugmentedFaceMode = EGoogleARCoreAugmentedFaceMode::PoseAndMesh;

// 获取面部区域变换
TArray<UGoogleARCoreAugmentedFace*> Faces;
// 通过 AR 系统获取追踪到的面部...
for (auto* Face : Faces)
{
    FTransform NoseTransform = Face->GetLocalToWorldTransformOfRegion(
        EGoogleARCoreAugmentedFaceRegion::NoseTip);
    FTransform ForeheadLeft = Face->GetLocalToWorldTransformOfRegion(
        EGoogleARCoreAugmentedFaceRegion::ForeheadLeft);
    FTransform ForeheadRight = Face->GetLocalToWorldTransformOfRegion(
        EGoogleARCoreAugmentedFaceRegion::ForeheadRight);
    // 在这些位置放置 AR 内容...
}
```

## Demo 示例

### 最小可编译示例 — AR 平面检测与锚点放置

**Build.cs 依赖：**
```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "GoogleARCoreBase",
    "AugmentedReality",
    "HeadMountedDisplay"
});
```

**GoogleARCoreMinimalDemo.h：**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "GoogleARCoreTypes.h"
#include "GoogleARCoreSessionConfig.h"
#include "GoogleARCoreMinimalDemo.generated.h"

UCLASS()
class AGoogleARCoreMinimalDemo : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

    void StartARSession();
    void PerformLineTrace();

    UPROPERTY()
    TObjectPtr<UGoogleARCoreSessionConfig> ARConfig;
};
```

**GoogleARCoreMinimalDemo.cpp：**
```cpp
#include "GoogleARCoreMinimalDemo.h"
#include "GoogleARCoreDevice.h"
#include "GoogleARCoreFunctionLibrary.h"
#include "ARBlueprintLibrary.h"

void AGoogleARCoreMinimalDemo::BeginPlay()
{
    Super::BeginPlay();
    StartARSession();
}

void AGoogleARCoreMinimalDemo::StartARSession()
{
    // 创建配置：启用水平/垂直平面检测
    ARConfig = UGoogleARCoreSessionConfig::CreateARCoreSessionConfig(
        true, true,
        EARLightEstimationMode::AmbientIntensityEstimate,
        EARFrameSyncMode::SyncImageAndCamera,
        true, true, true
    );

    // 通过跨平台 API 启动会话
    UARBlueprintLibrary::StartARSession(ARConfig);
}

void AGoogleARCoreMinimalDemo::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    PerformLineTrace();
}

void AGoogleARCoreMinimalDemo::PerformLineTrace()
{
    // 屏幕中心射线检测
    TArray<FARTraceResult> HitResults = UARBlueprintLibrary::LineTraceTrackedObjects(
        FVector2D(0.5f, 0.5f),  // 屏幕中心（归一化坐标）
        false, true, true, true
    );

    for (const auto& HitResult : HitResults)
    {
        UARTrackedGeometry* Geometry = HitResult.GetTrackedGeometry();
        if (Geometry && Geometry->IsA<UARPlaneGeometry>())
        {
            // 在检测到的平面上放置锚点
            FTransform HitTransform = HitResult.GetLocalToWorldTransform();
            // ... 放置虚拟物体
        }
    }
}
```

## 模块依赖

从 `GoogleARCoreBase.Build.cs` 的 `PublicDependencyModuleNames` 提取：

| 模块 | 用途 |
|---|---|
| `HeadMountedDisplay` | XR 跟踪系统基础接口 |
| `AugmentedReality` | UE 跨平台 AR 抽象层（`UARSessionConfig`、`UARTrackedGeometry` 等） |

从 `PrivateDependencyModuleNames` 提取（间接依赖，不需要手动添加）：

| 模块 | 用途 |
|---|---|
| `Core` / `CoreUObject` / `Engine` | UE 核心框架 |
| `RHI` / `RenderCore` / `Renderer` | 渲染硬件接口 |
| `Slate` / `SlateCore` | UI 框架 |
| `OpenGL` / `OpenGLDrv` / `Vulkan` / `VulkanRHI` | 图形 API 支持（Android） |
| `AndroidPermission` | Android 运行时权限管理 |
| `GoogleARCoreRendering` | AR 摄像头画面渲染 |
| `GoogleARCoreSDK` | ARCore 原生 SDK 封装 |
| `ProceduralMeshComponent` | 程序化网格（用于面部网格等） |
| `MRMesh` | 混合现实网格支持 |
| `ARUtilities` | AR 工具函数和材质资源 |
| `UElibPNG` / `zlib` | 图像处理（增强图片数据库序列化） |

**使用者只需依赖：** `GoogleARCoreBase`（会自动拉取 `AugmentedReality` 和 `HeadMountedDisplay`）

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-08-26 | `0a8b2cd` | Deprecating RHICreateTextureReference and RHIUpdateTextureReference | RHI API 迁移，强制使用 CommandList 版本接口，非功能性更新 |
| 2025-06-02 | `c73322c` | Deprecate XRThreadUtils.h functions | RHI 命令列表 API 迁移，非功能性更新 |
| 2025-05-13 | `ffd3320` | RHIBindDebugLabelName Cleanup | 清理冗余的调试标签调用，非功能性更新 |

### 维护评价

- **创建时间：** 2019 年 1 月（约 7 年历史），随 UE4 的 AR 框架重构引入
- **最近更新：** 近 3 次提交均为 RHI/XR 基础设施的 API 迁移，不涉及 ARCore 功能性变更
- **维护状态：** 🔧 **维护中** — 代码持续跟随引擎 RHI API 变化更新，但 ARCore 特定功能近 1 年无实质性增强
- **已知限制：**
  - 仅支持 Android 平台
  - 需要设备安装 ARCore APK
  - `EnabledByDefault=false`，需手动启用
  - `GetCameraMetadata` 已在 UE 5.3 标记为废弃且无替代方案
  - `UGoogleARCoreAugmentedImageDatabase` 和 `FGoogleARCoreAugmentedImageDatabaseEntry` 已废弃，推荐使用跨平台的 `UARCandidateImage`
- **推荐：** ✅ 如果你需要在 UE5 中开发 Android AR 应用，这是官方唯一的 ARCore 接入方案，推荐使用。优先使用跨平台的 `AugmentedReality` 模块 API，仅在需要 ARCore 特有功能（如 Augmented Face、相机配置选择）时使用本插件的扩展 API。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/AR/Google/GoogleARCore)
- [官方文档](https://developers.google.com/ar/)（Google ARCore 开发者网站）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/AR/Google/GoogleARCore/Source/GoogleARCoreBase/Private/Tests)
- [相关插件：GoogleARCoreServices](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/AR/Google/GoogleARCoreServices)（Cloud Anchor 和持久化功能）
