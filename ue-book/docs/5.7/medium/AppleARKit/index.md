# Apple ARKit

> Support for Apple's ARKit augmented reality system

| 属性 | 值 |
|---|---|
| 分类 | Augmented Reality |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质资产、着色器） |
| 模块 | `AppleARKit` (Runtime), `AppleARKitPoseTrackingLiveLink` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2017-07-17 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/AR/AppleAR/AppleARKit) | |

## 用途

Apple ARKit Plugin 是 UE5 对 Apple ARKit 增强现实框架的完整封装。它将 ARKit 的原生 AR 能力——平面检测、人脸追踪、身体姿态追踪、环境光估计、场景深度、地理追踪、网格重建等——桥接到 UE5 的 AR 抽象层（`AugmentedReality` 模块）和 XR 追踪系统中，让 iOS 设备可以作为 AR 平台使用。

核心价值：
- 在 iOS 设备上实现 AR 世界追踪、平面/图像/物体检测
- 支持人脸追踪（Face Tracking）和 LiveLink 面部 BlendShape 发布
- 支持身体姿态追踪（Pose Tracking）和 LiveLink 骨骼数据发布
- 摄像机透视叠加（Passthrough Overlay）与遮挡效果（深度遮挡、人物分割、场景深度）
- ARKit 1.0 到 4.0+ 的全版本支持检测
- 地理空间追踪（Geo Tracking，ARKit 4.0+）
- 场景网格重建与遮挡（Mesh Occlusion，ARKit 3.5+）

**注意**：此插件默认不启用（`EnabledByDefault: false`），需要在项目设置中手动启用，或通过 `SupportedPrograms: ["LiveLinkHub"]` 限定为 LiveLinkHub 程序使用。

## 使用场景

- 你需要在 iOS 设备上放置虚拟家具到真实桌面 → 使用 ARKit 的平面检测 + `UARSessionConfig::AddPlanesDetection`
- 你需要驱动虚拟角色的面部表情（Animoji 风格）→ 使用 ARKit 人脸追踪 + LiveLink 面部 BlendShape
- 你需要身体动作捕捉到骨骼动画 → 使用 ARKit Pose Tracking + `AppleARKitPoseTrackingLiveLink` 模块
- 你需要虚拟物体被真实世界遮挡 → 使用 ARKit 场景深度遮挡或人物分割遮挡
- 你需要基于 GPS 坐标在真实世界位置放置 AR 锚点 → 使用 ARKit 4.0+ Geo Tracking

## 蓝图用法

此插件主要通过 UE5 的 AR 抽象层（`UARBlueprintLibrary`）暴露给蓝图。插件本身不直接暴露 `BlueprintCallable` 函数，而是作为 AR 系统的后端实现。

### 核心配置（Project Settings → Apple ARKit）

`UAppleARKitSettings` 提供以下配置项：

| 设置 | 说明 |
|---|---|
| `bRequireARKitSupport` | 为 true 时，项目只能安装在支持 ARKit 的设备上 |
| `LivelinkTrackingTypes` | 启用哪些 LiveLink 追踪类型（FaceTracking / PoseTracking） |
| `bFaceTrackingLogData` | 是否启用面部追踪数据写入磁盘 |
| `bFaceTrackingWriteEachFrame` | 是否逐帧写入面部追踪数据 |
| `FaceTrackingFileWriterType` | 写入格式：None / CSV / JSON |
| `bShouldWriteCameraImagePerFrame` | 是否逐帧写入摄像机图像 |
| `WrittenCameraImageScale` | 写入图像的缩放比例 |
| `WrittenCameraImageQuality` | JPEG 质量（默认 85） |
| `LiveLinkPublishingPort` | LiveLink 发布端口（默认 11111） |
| `DefaultFaceTrackingLiveLinkSubjectName` | 面部追踪 LiveLink 主题名（默认 "iPhoneXFaceAR"） |
| `DefaultPoseTrackingLiveLinkSubjectName` | 姿态追踪 LiveLink 主题名（默认 "PoseTracking"） |
| `DefaultFaceTrackingDirection` | 面部追踪方向：FaceRelative / Mirrored |
| `bAdjustThreadPrioritiesDuringARSession` | AR 会话期间是否调整线程优先级 |
| `ARKitTimecodeProvider` | 自定义 Timecode Provider 路径 |

### 使用示例（蓝图描述）

**基本 AR 会话启动流程**：
1. 在 Actor 中添加 `UARSessionConfig` 资产并配置追踪类型
2. 使用 `UARBlueprintLibrary::StartARSession` 启动会话
3. 使用 `UARBlueprintLibrary::GetAllTrackedPlanes` 获取检测到的平面
4. 使用 `UARBlueprintLibrary::LineTraceTrackedObjects` 进行 AR 射线检测
5. 在检测到的位置放置虚拟物体

**面部追踪 LiveLink 流程**：
1. 在 Project Settings → Apple ARKit 中启用 `LivelinkTrackingTypes: [FaceTracking]`
2. 配置 `DefaultFaceTrackingLiveLinkSubjectName`
3. 启动 AR 会话后，面部 BlendShape 数据自动发布到 LiveLink
4. 在动画蓝图中通过 LiveLink 接收 BlendShape 数据驱动面部网格

## C++ 用法

### 头文件引入

```cpp
// AR 系统抽象层
#include "ARBlueprintLibrary.h"
#include "ARSessionConfig.h"
#include "ARPin.h"
#include "ARTraceResult.h"

// Apple ARKit 专有类型
#include "AppleARKitAvailability.h"
#include "AppleARKitConversion.h"
#include "AppleARKitSettings.h"
#include "AppleARKitTextures.h"
#include "AppleARKitFaceSupport.h"
#include "AppleARKitPoseTrackingLiveLink.h"
```

### 基本用法

**坐标系转换**（来源：`AppleARKitConversion.h`）：

```cpp
// ARKit 使用 Y-up 右手坐标系，UE 使用 Z-up 左手坐标系
// 自动处理坐标轴映射和 100x 缩放（米→厘米）

// ARKit matrix_float4x4 → UE FTransform
FTransform UeTransform = FAppleARKitConversion::ToFTransform(RawARKitMatrix);

// UE FTransform → ARKit matrix_float4x4
matrix_float4x4 ARKitMatrix = FAppleARKitConversion::ToARKitMatrix(UeTransform);

// ARKit vector → UE FVector（自动缩放 100x）
FVector UePos = FAppleARKitConversion::ToFVector(RawARKitVector);

// NSUUID → FGuid
FGuid AnchorGuid = FAppleARKitConversion::ToFGuid(nsUUID);
```

**ARKit 版本检测**（来源：`AppleARKitAvailability.h`）：

```cpp
// 运行时检测 ARKit 版本支持
if (FAppleARKitAvailability::SupportsARKit40())
{
    // ARKit 4.0+ 功能（Geo Tracking、场景深度等）
}
else if (FAppleARKitAvailability::SupportsARKit30())
{
    // ARKit 3.0+ 功能（身体追踪、人物分割等）
}
else if (FAppleARKitAvailability::SupportsARKit15())
{
    // ARKit 1.5+ 功能（图像检测等）
}
```

**获取 ARKit 系统实例**（来源：`AppleARKitModule.h`）：

```cpp
#include "AppleARKitModule.h"

// 获取 ARKit 系统实例
TSharedPtr<FAppleARKitSystem> ARKitSystem = FAppleARKitModule::GetARKitSystem();
if (ARKitSystem.IsValid())
{
    // 获取 ARKit 原生 ARSession 指针（仅 iOS）
    void* SessionPtr = ARKitSystem->GetARSessionRawPointer();
    
    // 获取当前帧的原生 ARFrame 指针
    void* FramePtr = ARKitSystem->GetGameThreadARFrameRawPointer();
}
```

### 进阶用法

**自定义 Face Tracking LiveLink Source**（来源：`AppleARKitPoseTrackingLiveLinkSourceFactory.h`）：

```cpp
#include "AppleARKitPoseTrackingLiveLinkSourceFactory.h"

// 创建 LiveLink 源
TSharedPtr<ILiveLinkSourceARPoseTracking> LiveLinkSource =
    FAppleARKitPoseTrackingLiveLinkSourceFactory::CreateLiveLinkSource();

// 该源会自动将 ARKit 追踪到的面部/身体数据发布到 LiveLink
```

**Mesh 遮挡数据处理**（来源：`AppleARKitMeshData.h`）：

```cpp
#include "AppleARKitMeshData.h"

// 通过 GUID 获取缓存的网格数据
FARKitMeshData::MeshDataPtr MeshData = FARKitMeshData::GetMeshData(AnchorGuid);

// 在世界空间某位置查询物体分类
uint8 Classification;
FVector ClassificationLocation;
bool bFound = MeshData->GetClassificationAtLocation(
    WorldLocation, LocalToWorldTransform,
    Classification, ClassificationLocation, MaxLocationDiff);

// 更新 MR Mesh 组件
FARKitMeshData::UpdateMRMesh(MeshTransform, MeshData, MRMeshComponent);
```

**Geo Tracking 支持**（来源：`ARKitGeoTrackingSupport.h`）：

```cpp
#include "ARKitGeoTrackingSupport.h"

UARKitGeoTrackingSupport* GeoSupport = GetMutableDefault<UARKitGeoTrackingSupport>();

// 检查地理追踪可用性
FString Error;
auto Task = GeoSupport->CheckGeoTrackingAvailability(Error);

// 在指定经纬度添加地理锚点
GeoSupport->AddGeoAnchorAtLocation(Longitude, Latitude, TEXT("MyAnchor"));
GeoSupport->AddGeoAnchorAtLocationWithAltitude(Longitude, Latitude, Altitude, TEXT("MyAnchorWithAlt"));
```

## Demo 示例

### 最小 AR 平面检测示例

```cpp
// MyARActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "ARActor.h"
#include "MyARActor.generated.h"

UCLASS()
class AMyARActor : public AActor
{
    GENERATED_BODY()
public:
    AMyARActor();

    UPROPERTY(EditAnywhere, Category = "AR")
    TObjectPtr<UARSessionConfig> ARConfig;

    UFUNCTION(BlueprintCallable)
    void StartARSession();

    UFUNCTION(BlueprintCallable)
    TArray<FARTraceResult> TraceARObjects(FVector2D ScreenPosition);

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
};
```

```cpp
// MyARActor.cpp
#include "MyARActor.h"
#include "ARBlueprintLibrary.h"
#include "ARSessionConfig.h"

AMyARActor::AMyARActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyARActor::BeginPlay()
{
    Super::BeginPlay();
    if (!ARConfig)
    {
        ARConfig = NewObject<UARSessionConfig>();
        ARConfig->AddPlanesDetection(EARPlaneDetectionCapability::Horizontal | EARPlaneDetectionCapability::Vertical);
        ARConfig->SetWorldAlignment(EARWorldAlignment::Gravity);
    }
}

void AMyARActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    UARBlueprintLibrary::StopARSession();
    Super::EndPlay(EndPlayReason);
}

void AMyARActor::StartARSession()
{
    if (ARConfig)
    {
        UARBlueprintLibrary::StartARSession(ARConfig);
    }
}

TArray<FARTraceResult> AMyARActor::TraceARObjects(FVector2D ScreenPosition)
{
    return UARBlueprintLibrary::LineTraceTrackedObjects(
        ScreenPosition, true, true, true, true);
}
```

**Build.cs 依赖**：

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "Engine",
    "AugmentedReality",
    "AppleARKit",
});
```

## Console Variables

此插件提供以下控制台变量：

| CVar | 默认值 | 说明 |
|---|---|---|
| `ar.ARKit.ReleaseSessionWhenStopped` | 0 | 停止时是否释放 ARKit session 对象 |
| `arkit.SceneDepthBufferSizeScale` | 1.0 | 场景深度缓冲区缩放（>1 时放大） |
| `arkit.SceneDepthBufferBlurAmount` | 0.0 | 场景深度缓冲区高斯模糊 sigma |

## 模块依赖

### AppleARKit 模块

| 模块 | 用途 |
|---|---|
| `Core` | 引擎核心 |
| `Engine` | 引擎框架 |
| `MRMesh` | Mixed Reality Mesh 组件（网格遮挡） |
| `EyeTracker` | 眼球追踪接口 |
| `CoreUObject` | UObject 系统 |
| `Slate` / `SlateCore` | UI 框架 |
| `RHI` / `Renderer` / `RenderCore` | 渲染硬件接口 |
| `HeadMountedDisplay` | HMD/XR 基础设施 |
| `XRBase` | XR 基础模块 |
| `AugmentedReality` | UE AR 抽象层（核心依赖） |
| `AppleImageUtils` | Apple 图像处理工具 |
| `Projects` | 项目信息 |
| `ARUtilities` | AR 工具函数 |
| `IOSRuntimeSettings` | iOS 运行时设置（仅 iOS） |
| `MetalRHI` | Metal 渲染后端（iOS/Mac） |

### AppleARKitPoseTrackingLiveLink 模块

| 模块 | 用途 |
|---|---|
| `Core` / `Engine` | 引擎核心 |
| `CoreUObject` | UObject 系统 |
| `HeadMountedDisplay` | HMD 基础设施 |
| `XRBase` | XR 基础模块 |
| `LiveLinkAnimationCore` | LiveLink 动画核心 |
| `LiveLinkInterface` | LiveLink 接口 |
| `AppleARKit` | Apple ARKit 核心模块 |
| `AppleImageUtils` | Apple 图像处理 |
| `ARUtilities` | AR 工具函数 |

### 原生框架依赖（iOS）

| Framework | 用途 |
|---|---|
| `ARKit` | Apple ARKit 原生框架 |
| `MetalPerformanceShaders` | Metal 性能着色器（图像处理） |
| `CoreLocation` | 地理位置服务 |
| `Metal` | Metal 图形 API（弱链接） |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-08-26 | `0a8b2cd9` | Deprecating RHICreateTextureReference/RHIUpdateTextureReference | RHI 层接口重构，要求调用者提供 command list，属于引擎级底层变更 |
| 2025-06-25 | `e5bc1298` | Fix CachedUniformExpressionShaderMap for AR template with Scene Depth occlusion | 修复 AR 模板中启用场景深度遮挡时的着色器缓存问题 |
| 2025-06-11 | `8406cd44` | Replace FORCEINLINE with inline in AR modules | 代码风格统一，性能无关 |
| 2025-06-02 | `f5bdc1ec` | Fix MetalRHI not included on Mac for ARKit | 修复 Mac 平台编译问题 |
| 2025-06-02 | `65244a08` | Removed MetalRHI from AppleARKit plugin | 平台依赖清理 |

### 维护评价

- **创建时间**：2017-07-17，与 ARKit 框架同步发布，历史长达约 9 年
- **最近更新**：2025 年 8 月有活跃更新，主要是引擎底层 RHI 重构适配和 bug 修复
- **维护状态**：**活跃维护**。作为 Apple AR 平台在 UE 中的核心实现，跟随引擎持续更新
- **已知限制**：
  - 仅在 iOS 设备上运行时提供完整 AR 功能，Win64/Mac/Linux/Android 平台仅提供编译支持（模块加载但不创建追踪系统）
  - 需要 Apple A9 及以上芯片的 iOS 设备（iPhone 6s+）
  - 人脸追踪需要 TrueDepth 摄像头（iPhone X+）
  - 身体追踪和人物分割需要 ARKit 3.0+（iPhone XR/XS+）
- **推荐**：如果你的项目面向 iOS AR，这是必需插件。活跃维护，无废弃风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/AR/AppleAR/AppleARKit)
- 官方文档：无（`.uplugin` 中 DocsURL 为空）
- [Apple ARKit 开发者文档](https://developer.apple.com/arkit/)
