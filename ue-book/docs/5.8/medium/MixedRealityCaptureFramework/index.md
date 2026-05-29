# Mixed Reality Capture Framework

> A simple framework that provides users a way to integrate mixed reality capture into their VR projects.

| 属性 | 值 |
|---|---|
| 中文名 | 混合现实捕捉 |
| 分类 | Virtual Reality |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、校准配置） |
| 模块 | `MixedRealityCaptureFramework` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-05-10 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MixedRealityCaptureFramework) | |

## 用途

该插件并非一个“简单”的框架，而是一个完整的混合现实（MR）合成系统。它旨在解决在虚拟现实（VR）项目中实时合成来自物理世界摄像头（通常佩戴在 VR 头显上）画面与虚拟场景的问题。其核心是允许开发者将真实的玩家（通过绿幕等手段）与虚拟游戏世界无缝融合，常用于 MR 直播、MR 游戏演示或开发。

**它解决的具体问题包括**：
1.  **视频源集成**：连接并管理来自摄像头的视频流。
2.  **镜头畸变校正**：使用 OpenCV 库对摄像头原始画面进行畸变矫正。
3.  **合成与材质处理**：提供管线（包括绿幕抠像/色度键）来处理视频画面，并将其投影到一个跟随玩家的虚拟平面上。
4.  **空间对齐（校准）**：校准物理摄像头在虚拟世界中的位置、方向和视野（FOV），确保视频画面与虚拟场景精确对齐。
5.  **垃圾遮罩**：为视频流创建遮罩，以排除现实世界中不需要的物体（如摄像头支架）。
6.  **广播输出**：将最终合成的 MR 画面输出到旁观者屏幕或直播流。

## 使用场景

-   **你正在开发一个 VR 游戏或应用，并希望将真实玩家的形象混合进虚拟场景中进行直播或录制**。
-   **你需要校准一个固定在 VR 头显上的外部摄像头，以准确合成 MR 画面**。
-   **你的 MR 工作流需要复杂的视频处理，如色度键抠像、镜头畸变校正和垃圾遮罩**。
-   **你需要将 MR 合成结果发送到旁观者屏幕或外部软件（如 OBS）**。

## 蓝图用法

该插件的核心功能通过 `UMixedRealityCaptureComponent` 暴露给蓝图。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SaveConfiguration` / `LoadConfiguration` | 将校准数据（镜头、对齐、垃圾遮罩等）保存到存档或从存档加载。 | `UMixedRealityCaptureComponent` |
| `SaveAsDefaultConfiguration` / `LoadDefaultConfiguration` | 保存或加载项目默认的校准配置。 | `UMixedRealityCaptureComponent` |
| `SetCaptureDevice` | 设置视频捕捉源（通过 `FMrcVideoCaptureFeedIndex` 指定设备、流和格式）。 | `UMixedRealityCaptureComponent` |
| `SetLensDistortionParameters` | 设置 OpenCV 镜头畸变参数以校正画面。 | `UMixedRealityCaptureComponent` |
| `SetVideoProcessingMaterial` | 设置用于处理原始视频画面的材质（如实现色度键抠像）。 | `UMixedRealityCaptureComponent` |
| `SetVideoProcessingParams` | 设置视频处理材质的动态参数（标量、向量）。 | `UMixedRealityCaptureComponent` |
| `SetGarbageMatteActor` | 指定一个垃圾遮罩 Actor，用于遮盖视频源中不需要的物体。 | `UMixedRealityCaptureComponent` |
| `SetDeviceAttachment` / `DetachFromDevice` | 将捕捉组件附加到或分离自特定的运动控制器或追踪源。 | `UMixedRealityCaptureComponent` |
| `SetTrackingDelay` | 设置应用于运动控制器组件的延迟（毫秒），用于对齐延迟的摄像头画面。 | `UMixedRealityCaptureComponent` |
| `SetProjectionDepthOffset` | 设置视频投影平面相对于 HMD 的深度偏移。 | `UMixedRealityCaptureComponent` |
| `SetEnableProjectionDepthTracking` | 启用或禁用投影平面跟踪 HMD 移动以模拟玩家深度。 | `UMixedRealityCaptureComponent` |
| `ConstructCalibrationData` / `ApplyCalibrationData` | 构造或应用校准数据对象，可重写以自定义校准逻辑。 | `UMixedRealityCaptureComponent` |
| `OpenMrcVideoCaptureDevice` | 异步打开一个媒体捕捉设备。 | `UAsyncTask_OpenMrcVidCaptureDevice` |
| `IsMixedRealityCaptureBroadcasting` | 检查 MR 捕捉画面是否正在广播到旁观者屏幕。 | `UMrcUtilLibrary` |
| `SetMixedRealityCaptureBroadcasting` | 切换 MR 捕捉画面的广播状态。 | `UMrcUtilLibrary` |
| `GetMixedRealityCaptureTexture` | 获取最终的 MR 合成纹理。 | `UMrcUtilLibrary` |

### 使用示例（蓝图描述）

1.  **基础设置**：
    *   在你的 Actor 中添加一个 `MixedRealityCaptureComponent`。
    *   使用 `OpenMrcVideoCaptureDevice` 节点异步打开摄像头，并将成功的回调连接到 `SetCaptureDevice` 节点。
    *   在 `SetVideoProcessingMaterial` 中指定一个实现抠像（如色度键）的材质。
    *   使用 `SetLensDistortionParameters` 传入你校准好的镜头参数。
    *   调用 `LoadDefaultConfiguration` 或手动设置 `SetProjectionDepthOffset` 等属性来对齐视频画面。

2.  **校准流程**：
    *   使用 `SaveConfiguration` 将当前的镜头参数、跟踪附件、垃圾遮罩等所有设置保存到一个命名的存档槽中。
    *   在另一个会话或 Actor 中，使用 `LoadConfiguration` 并提供相同的槽名和用户索引来加载配置。

3.  **广播输出**：
    *   调用 `SetMixedRealityCaptureBroadcasting` 并将 `bEnable` 设为 `true`，即可将当前的 MR 合成画面输出到旁观者屏幕。

## C++ 用法

### 头文件引入

```cpp
#include "MixedRealityCaptureComponent.h"
#include "MrcVideoCaptureDevice.h"
#include "MrcCalibrationData.h"
#include "MrcUtilLibrary.h"
```

### 基本用法

创建并配置一个 MR 捕捉组件。
```cpp
// 假设在一个 Actor 的 BeginPlay 中
void AMyActor::BeginPlay()
{
    Super::BeginPlay();

    // 创建并添加组件
    UMixedRealityCaptureComponent* CaptureComp = NewObject<UMixedRealityCaptureComponent>(this);
    CaptureComp->RegisterComponent();
    CaptureComp->AttachToComponent(RootComponent, FAttachmentTransformRules::KeepRelativeTransform);

    // 异步打开视频源
    UMediaPlayer* MediaPlayer = ...; // 需要你自己的媒体播放器实例
    FMrcVideoCaptureFeedIndex DesiredFeed;
    DesiredFeed.DeviceURL = TEXT("YourCameraDeviceURL");

    auto* OpenTask = UAsyncTask_OpenMrcVidCaptureFeed::OpenMrcVideoCaptureFeed(DesiredFeed, MediaPlayer);
    if (OpenTask)
    {
        OpenTask->OnSuccess.AddDynamic(CaptureComp, &UMixedRealityCaptureComponent::SetCaptureDevice);
        OpenTask->Activate();
    }

    // 设置镜头畸变参数 (通常从校准中获得)
    FOpenCVLensDistortionParameters LensParams;
    // ... 填充 LensParams ...
    CaptureComp->SetLensDistortionParameters(LensParams);

    // 设置视频处理材质
    UMaterialInterface* ChromaKeyMaterial = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/Materials/M_ChromaKey"));
    if (ChromaKeyMaterial)
    {
        CaptureComp->SetVidProjectionMat(ChromaKeyMaterial);
    }
}
```

### 进阶用法

手动管理校准数据的保存与加载。
```cpp
// 保存校准数据到指定存档
bool AMixedRealityCaptureActor::SaveMyConfiguration(const FString& SlotName)
{
    if (CaptureComponent)
    {
        // 创建校准数据对象
        UMrcCalibrationData* CalData = CaptureComponent->ConstructCalibrationData();
        if (CalData)
        {
            // 将组件当前状态填充到校准数据中
            CaptureComponent->FillOutCalibrationData(CalData);
            // 保存到存档系统 (示例使用 SaveGameToSlot)
            return UGameplayStatics::SaveGameToSlot(CalData, SlotName, 0);
        }
    }
    return false;
}

// 从存档加载校准数据并应用
bool AMixedRealityCaptureActor::LoadMyConfiguration(const FString& SlotName)
{
    if (CaptureComponent)
    {
        // 从存档系统加载
        UMrcCalibrationData* LoadedData = Cast<UMrcCalibrationData>(UGameplayStatics::LoadGameFromSlot(SlotName, 0));
        if (LoadedData)
        {
            // 将加载的数据应用到组件
            CaptureComponent->ApplyCalibrationData(LoadedData);
            return true;
        }
    }
    return false;
}
```

## Demo 示例

以下是一个最小的、可编译的 C++ 示例，演示如何创建一个带有 MR 捕捉组件的 Actor。

**MixedRealityDemoActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MixedRealityDemoActor.generated.h"

class UMixedRealityCaptureComponent;
class UMediaPlayer;

UCLASS()
class AMixedRealityDemoActor : public AActor
{
    GENERATED_BODY()

public:
    AMixedRealityDemoActor();

protected:
    virtual void BeginPlay() override;

    // 捕捉组件
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MR Capture")
    TObjectPtr<UMixedRealityCaptureComponent> CaptureComponent;

    // 媒体播放器资产 (可在蓝图中设置)
    UPROPERTY(EditAnywhere, Category = "MR Capture")
    TObjectPtr<UMediaPlayer> MediaPlayerAsset;
};
```

**MixedRealityDemoActor.cpp**
```cpp
#include "MixedRealityDemoActor.h"
#include "MixedRealityCaptureComponent.h"
#include "MrcVideoCaptureDevice.h"
#include "MediaPlayer.h"

AMixedRealityDemoActor::AMixedRealityDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;

    // 创建并配置捕捉组件
    CaptureComponent = CreateDefaultSubobject<UMixedRealityCaptureComponent>(TEXT("MRCaptureComponent"));
    RootComponent = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
    CaptureComponent->SetupAttachment(RootComponent);
}

void AMixedRealityDemoActor::BeginPlay()
{
    Super::BeginPlay();

    if (MediaPlayerAsset)
    {
        // 尝试打开媒体播放器的第一个可用视频源
        TArray<FMrcVideoCaptureFeedIndex> Feeds = FMrcVideoCaptureUtils::EnumerateAvailableFeeds(MediaPlayerAsset);
        if (Feeds.Num() > 0)
        {
            // 异步打开第一个视频源
            auto* Task = UAsyncTask_OpenMrcVidCaptureFeed::OpenMrcVideoCaptureFeed(Feeds[0], MediaPlayerAsset);
            Task->OnSuccess.AddDynamic(CaptureComponent, &UMixedRealityCaptureComponent::SetCaptureDevice);
            Task->Activate();
        }
    }

    // 加载默认配置（如果存在）
    CaptureComponent->LoadDefaultConfiguration();
}
```

## 模块依赖

该插件的 Build.cs 显示它依赖于 `EditorFramework` 和 `UnrealEd`，但这通常是编辑器功能的内部依赖。对于用户项目来说，该插件的**运行时功能**没有特殊的、非常见的公共模块依赖。它主要依赖其声明的插件依赖项。

要使用此插件，你需要确保项目启用了以下插件：

| 插件 | 用途 |
|---|---|
| `OpenCVLensDistortion` | 为镜头畸变校正提供核心算法支持。 |
| `XRBase` | 提供基础的 VR/XR 系统抽象和跟踪支持。 |

你的项目 Build.cs 无需额外添加不常见的模块依赖，仅需标准 Core/Engine 等。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将插件内的日志宏迁移到新的 `UE_LOGF` 格式。 |
| 2025-10-07 | `96352708` | - Renaming Base<Plugin>.ini to Default<Plugin>.ini | 将插件默认配置文件从 `Base` 前缀重命名为 `Default` 前缀，以符合新的命名规范。 |
| 2024-11-25 | `f8c64277` | Converted renderer to use new SceneRenderBuilder interface. | 更新渲染器代码以使用新的 `SceneRenderBuilder` 接口，这是一次引擎渲染框架的适配。 |
| 2024-11-14 | `a74e120f` | Preventing IDelegateInstance::RemoveAll() and IDelegateInstance::IsCompacta... | 修复了与委托实例相关的一个潜在问题，可能影响组件的事件绑定。 |
| 2024-03-13 | `32e5d7e7` | Deprecates and removes MatchSubstring CoreRedirects from ini files in favour of `MatchWildcard=true,...` | 清理了配置文件中过时的重定向规则，使用新的通配符匹配方式。 |

### 维护评价

- **创建时间**：该插件始于 2018 年，已有较长历史。
- **活跃度**：**维护不活跃**。最近一次有意义的功能性更新（适配新渲染接口）发生在 2024 年 11 月。2025 和 2026 年的提交均为基础维护（日志、文件重命名）。
- **状态**：插件仍处于 **Beta 版本**（`IsBetaVersion=true`）且**默认禁用**，表明 Epic 官方认为其尚未达到生产就绪状态，或仅供特定用途。
- **已知问题/限制**：作为实验性功能，其 API 和行为在未来的引擎版本中可能发生不兼容的变更。文档和示例可能相对匮乏。
- **推荐**：**谨慎使用**。如果你的项目确实需要混合现实捕捉功能，这是一个可行的起点。但你需要做好自行调试、适配新版引擎以及寻找社区支持的准备。对于新的、非实验性的项目，建议评估其他更成熟或社区支持的 MR 方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MixedRealityCaptureFramework)
- [官方文档]()（无）
- [测试用例]()（插件目录内未发现标准测试文件）