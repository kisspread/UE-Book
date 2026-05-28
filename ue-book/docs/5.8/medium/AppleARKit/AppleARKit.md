# Apple ARKit

> Support for Apple's ARKit augmented reality system

| 属性 | 值 |
|---|---|
| 中文名 | 苹果ARKit |
| 分类 | Augmented Reality |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质） |
| 模块 | `AppleARKit` (Runtime), `AppleARKitPoseTrackingLiveLink` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AR/AppleAR/AppleARKit) | |

## 用途

AppleARKit 插件是 Unreal Engine 与苹果 ARKit 增强现实框架之间的桥梁。它的主要目的是将 ARKit 的原生功能（如平面检测、图像识别、环境光照估计、人脸追踪、物体追踪、场景重建等）封装成 UE5 的 AR 系统接口，使得开发者可以使用统一的 `UARSessionConfig`、`UARBlueprintLibrary` 等引擎 API 来调用 ARKit 的功能，而无需直接处理平台原生代码。该插件解决了在 iOS 设备上运行高质量、稳定 AR 体验的跨平台集成问题。

## 使用场景

- 你需要为 iOS 设备（iPhone/iPad）开发一个基于 ARKit 的增强现实应用。
- 你的 AR 项目需要使用 ARKit 特有的功能，如 `ARBodyTrackingConfiguration`（身体追踪）或 `ARGeoTrackingConfiguration`（地理空间追踪）。
- 你希望将 ARKit 的人脸追踪数据通过 Live Link 发送到虚幻引擎，用于驱动虚拟角色的面部动画。
- 你需要为 AR 体验配置特殊的线程优先级和性能设置。
- 你正在开发需要高精度环境遮挡（Depth Occlusion 或 Matte Occlusion）的 AR 应用。

## 蓝图用法

此插件主要通过引擎通用的 AR 蓝图库（`UARBlueprintLibrary`）和会话配置对象（`UARSessionConfig`）进行交互，自身不直接暴露大量独有的蓝图节点。其核心作用是为这些通用接口提供 ARKit 的后端实现。

### 核心配置节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Start AR Session` | 启动 AR 会话，使用指定的 `UARSessionConfig`。对于 ARKit，实际会话由 `FAppleARKitSystem` 管理。 | `UARBlueprintLibrary` |
| `Get AR Session Status` | 查询当前 AR 会话的状态（运行中/已暂停等）。 | `UARBlueprintLibrary` |
| `Get All Tracked Geometries` | 获取当前 AR 系统追踪到的所有几何体（如平面、图像）。 | `UARBlueprintLibrary` |
| `Line Trace Tracked Objects` | 执行射线检测，与 AR 追踪的几何体交互。 | `UARBlueprintLibrary` |
| `Pin Component to AR Pin` | 将一个场景组件“钉”在特定的 AR 追踪点（Pin）上，使其跟随 AR 空间移动。 | `UARBlueprintLibrary` |

### 使用示例（蓝图描述）

1.  **创建和配置 AR 会话**：
    - 在场景中创建一个 `ARSession Config` 对象资产。
    - 打开配置资产，根据需要启用功能，如 `Plane Detection`（平面检测）、`Image Tracking`（图像追踪）、`Face Tracking`（人脸追踪）。这些选项最终会传递给 `FAppleARKitSystem`，转换为对应的 `ARConfiguration`。
2.  **启动 AR 体验**：
    - 在某个 Actor（如 GameMode 或专用 Manager）的 `BeginPlay` 事件中，调用 `Start AR Session` 节点，并传入配置好的 `ARSession Config`。
3.  **处理 AR 数据**：
    - 使用 `Get All Tracked Geometries` 定期获取新检测到的平面或图像锚点，并为它们生成可视化 Actor。
    - 使用 `Pin Component to AR Pin` 将虚拟物体“放置”在真实的桌面或墙壁上。
    - 使用 `Line Trace Tracked Objects` 实现虚拟物体与真实环境的交互（如点击放置、射击等）。

## C++ 用法

虽然插件没有提供公开的测试用例，但可以从其公开接口和引擎通用的 AR 接口推断使用方式。

### 头文件引入

```cpp
#include "HeadMountedDisplayFunctionLibrary.h" // 用于 XR 相关通用功能
#include "ARBlueprintLibrary.h"                // 用于调用 AR 会话和查询
#include "ARSessionConfig.h"                   // 用于配置 AR 会话
#include "AppleARKitSystem.h"                  // （可选，用于底层访问）头文件位于 Private 目录，非公开 API，但有时可用于高级调试
```

### 基本用法：启动和管理 AR 会话

C++ 中的 AR 管理同样通过引擎提供的通用接口进行，AppleARKit 作为 `IXRTrackingSystem` 的一种实现被自动创建和使用。

```cpp
// MyARManager.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyARManager.generated.h"

UCLASS()
class AMyARManager : public AActor
{
    GENERATED_BODY()
public:
    AMyARManager();

    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    // 引用一个配置好的 ARSessionConfig 资产
    UPROPERTY(EditAnywhere, Category = "AR")
    TObjectPtr<UARSessionConfig> SessionConfig;

private:
    // 用于追踪的委托
    FDelegateHandle TrackedGeometryDelegateHandle;

    UFUNCTION()
    void OnTrackedGeometryAdded(UARTrackedGeometry* TrackedGeometry);
};
```

```cpp
// MyARManager.cpp
#include "MyARManager.h"
#include "ARBlueprintLibrary.h"
#include "Kismet/GameplayStatics.h"

AMyARManager::AMyARManager()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyARManager::BeginPlay()
{
    Super::BeginPlay();

    if (SessionConfig)
    {
        // 启动 AR 会话，这将触发引擎创建并使用 FAppleARKitSystem (在支持 ARKit 的 iOS 设备上)
        UARBlueprintLibrary::StartARSession(SessionConfig);

        // 订阅几何体追踪事件
        TrackedGeometryDelegateHandle = UARBlueprintLibrary::OnTrackableAddedDelegate.AddUObject(this, &AMyARManager::OnTrackedGeometryAdded);
        
        UE_LOG(LogTemp, Log, TEXT("AR Session Started with AppleARKit Backend."));
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("ARSessionConfig is null! Cannot start AR session."));
    }
}

void AMyARManager::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    UARBlueprintLibrary::OnTrackableAddedDelegate.Remove(TrackedGeometryDelegateHandle);
    
    // 停止 AR 会话
    UARBlueprintLibrary::StopARSession();
    
    Super::EndPlay(EndPlayReason);
}

void AMyARManager::OnTrackedGeometryAdded(UARTrackedGeometry* TrackedGeometry)
{
    if (TrackedGeometry && TrackedGeometry->IsA<UARTrackedPlane>())
    {
        UARTrackedPlane* Plane = Cast<UARTrackedPlane>(TrackedGeometry);
        UE_LOG(LogTemp, Log, TEXT("New AR Plane detected: %s, Size: %s"),
            *Plane->GetDebugName(),
            *Plane->GetExtent().ToString());
        // 在此生成平面的可视化 Actor...
    }
}
```

### 进阶用法：查询设备 ARKit 特性支持

在尝试启用高级功能前，检查设备是否支持。

```cpp
// 查询是否支持人脸追踪
bool bSupportsFaceTracking = UARBlueprintLibrary::IsSessionTrackingFeatureSupported(
    EARSessionType::Face,
    EARSessionTrackingFeature::FaceTracking
);

// 查询是否支持身体追踪
bool bSupportsBodyTracking = UARBlueprintLibrary::IsSessionTrackingFeatureSupported(
    EARSessionType::Body,
    EARSessionTrackingFeature::BodyTracking
);

// 查询是否支持场景深度
bool bSupportsSceneDepth = UARBlueprintLibrary::IsSceneReconstructionSupported(
    EARSessionType::World,
    EARSceneReconstruction::Mesh
);

if (bSupportsFaceTracking && bSupportsBodyTracking && bSupportsSceneDepth)
{
    // 配置启用这些高级功能
    SessionConfig->SetSessionTrackingFeatureEnabled(EARSessionTrackingFeature::FaceTracking, true);
    SessionConfig->SetSessionTrackingFeatureEnabled(EARSessionTrackingFeature::BodyTracking, true);
    SessionConfig->SetSceneReconstructionMethod(EARSceneReconstruction::Mesh);
    // ... 继续启动会话
}
```

## Demo 示例

一个最小的、可运行的 AR 平面检测示例。

```cpp
// MinimalARKitExample.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MinimalARKitExample.generated.h"

class UARSessionConfig;

UCLASS()
class AMinimalARKitExample : public AActor
{
    GENERATED_BODY()

public:
    AMinimalARKitExample();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    UPROPERTY(EditDefaultsOnly, Category = "AR")
    TSubclassOf<AActor> PlaneVisualizerClass;

    UPROPERTY()
    TObjectPtr<UARSessionConfig> ARConfig;

    UFUNCTION()
    void HandleARSessionStarted();

    UFUNCTION()
    void HandleTrackedGeometryAdded(UARTrackedGeometry* NewGeometry);
};
```

```cpp
// MinimalARKitExample.cpp
#include "MinimalARKitExample.h"
#include "ARBlueprintLibrary.h"
#include "ARSessionConfig.h"
#include "GameFramework/PlayerController.h"
#include "Engine/World.h"

AMinimalARKitExample::AMinimalARKitExample()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMinimalARKitExample::BeginPlay()
{
    Super::BeginPlay();

    // 1. 创建并配置 AR 会话配置对象
    ARConfig = NewObject<UARSessionConfig>();
    ARConfig->SetPlaneDetectionMode(EARPlaneDetectionMode::Horizontal); // 启用水平面检测

    // 2. 绑定事件
    UARBlueprintLibrary::OnARSessionStarted.AddDynamic(this, &AMinimalARKitExample::HandleARSessionStarted);
    UARBlueprintLibrary::OnTrackableAddedDelegate.AddDynamic(this, &AMinimalARKitExample::HandleTrackedGeometryAdded);

    // 3. 启动会话
    UARBlueprintLibrary::StartARSession(ARConfig);
}

void AMinimalARKitExample::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    UARBlueprintLibrary::StopARSession();
    UARBlueprintLibrary::OnARSessionStarted.RemoveDynamic(this, &AMinimalARKitExample::HandleARSessionStarted);
    UARBlueprintLibrary::OnTrackableAddedDelegate.RemoveDynamic(this, &AMinimalARKitExample::HandleTrackedGeometryAdded);
    Super::EndPlay(EndPlayReason);
}

void AMinimalARKitExample::HandleARSessionStarted()
{
    UE_LOG(LogTemp, Log, TEXT("MinimalARKitExample: AR Session has started!"));
}

void AMinimalARKitExample::HandleTrackedGeometryAdded(UARTrackedGeometry* NewGeometry)
{
    if (!NewGeometry || !PlaneVisualizerClass) return;

    if (UARTrackedPlane* TrackedPlane = Cast<UARTrackedPlane>(NewGeometry))
    {
        // 在检测到的平面上生成一个可视化 Actor
        FActorSpawnParameters SpawnParams;
        SpawnParams.Owner = this;
        SpawnParams.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;

        AActor* Visualizer = GetWorld()->SpawnActor<AActor>(PlaneVisualizerClass,
            TrackedPlane->GetLocalToWorldTransform().GetLocation(),
            FRotator::ZeroRotator,
            SpawnParams);

        if (Visualizer)
        {
            Visualizer->AttachToActor(this, FAttachmentTransformRules::KeepWorldTransform);
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `IOSRuntimeSettings` | 读取 iOS 平台特定的项目设置（如最低 iOS 版本），用于确定是否启用 ARKit 支持。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了 64 位平台上格式说明符不匹配的潜在问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 `UE_LOG` 迁移到 `UE_LOGF`，属于引擎全局重构。 |
| 2026-04-13 | `b905d146` | Fix/Silence unreachable code warnings | 修复或抑制了“不可达代码”的编译器警告。 |
| 2026-04-10 | `e18acf19` | More unreachable code warning fixes | 继续修复不可达代码警告。 |
| 2026-03-19 | `7662e97c` | Fix incorrect scene texture sampling uv in postprocess materials after TSR. This also caused incorre... | 修复了 TSR 技术后处理材质中场景纹理采样 UV 不正确的问题。 |

### 维护评价

AppleARKit 插件是 UE5 在 iOS 平台进行 AR 开发的基石，自 2020 年 9 月随 UE5 早期版本创建以来，一直是引擎的核心组成部分。从近期的 git 提交记录来看，**该插件处于持续维护状态**，但主要是应对引擎底层的代码质量改进、警告修复和系统级功能（如 TSR）的兼容性更新，而非添加新的 ARKit 特性。

**评价：**
- **成熟稳定**：作为运行时插件，其核心功能（会话管理、平面检测、图像追踪、光照估计）已经非常成熟和稳定。
- **维护模式**：最近的提交表明 Epic 仍在维护其与引擎的兼容性和代码健康度，但并非活跃开发新功能。新 ARKit 特性的集成通常发生在引擎主版本迭代中。
- **使用建议**：**强烈推荐使用**。这是在 UE5 中支持 iOS AR 功能的官方且唯一方案。开发者应依赖引擎通用的 AR API 进行开发，当需要访问最新的、尚未封装的 ARKit 特性时，才需要考虑扩展此插件或进行原生 iOS 开发。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AR/AppleAR/AppleARKit)
- 官方文档（未提供）
- [引擎 AR 测试用例（可能位于 Engine/Tests 目录）](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AR/AppleAR/AppleARKit)