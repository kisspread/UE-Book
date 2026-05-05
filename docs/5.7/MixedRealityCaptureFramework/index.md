# Mixed Reality Capture Framework

> A simple framework that provides users a way to integrate mixed reality capture into their VR projects.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Reality |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质、纹理、网格体、配置重定向） |
| 模块 | `MixedRealityCaptureFramework` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-05-10 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MixedRealityCaptureFramework) | |

## 用途

Mixed Reality Capture Framework (MRC Framework) 是 UE5 中用于实现 **混合现实捕捉 (Mixed Reality Capture)** 的运行时框架。它解决的核心问题是：**如何将真实世界的摄像头画面与 VR 虚拟场景实时合成**，让观众通过旁观者屏幕 (Spectator Screen) 看到玩家"身处"虚拟世界的效果。

具体来说，这个框架提供了一套完整的管线：

1. **摄像头视频输入**：通过 Media Framework 接收外部摄像头（如 HDMI 采集卡）的实时画面
2. **镜头畸变校正**：使用 OpenCV 的镜头畸变参数对原始画面进行去畸变处理
3. **投影平面渲染**：将校正后的视频画面投影到 3D 空间中的平面上，与虚拟场景混合
4. **运动控制器追踪**：将摄像头绑定到 VR 追踪设备（如手柄），实时同步位置
5. **Garbage Matte 遮罩**：支持遮罩裁剪，只显示玩家身体部分而非背景
6. **追踪延迟补偿**：对追踪数据施加毫秒级延迟，补偿摄像头画面的固有延迟
7. **旁观者屏幕广播**：将合成结果自动输出到 VR 头显的旁观者屏幕

这是 VR 直播/演示场景的基础设施，常见于 VR 游戏直播、线下体验店、VR 活动展示等。

## 使用场景

- 你在做 VR 直播，想让观众看到玩家"走进"虚拟世界的效果 → 用 MRC Framework
- 你在搭建线下 VR 体验店，需要在大屏幕上显示合成画面 → 用 MRC Framework
- 你需要将外部摄像头画面与 VR 场景实时合成，并校正镜头畸变 → 用 MRC Framework
- 你需要精确对齐虚拟场景和真实摄像头的视角（标定/校准） → 用 MRC Framework
- 你只是做普通 3D 游戏，不需要摄像头合成 → **不需要这个插件**

## 蓝图用法

### 核心节点 — UMixedRealityCaptureComponent

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SaveAsDefaultConfiguration` | 将当前 MRC 配置（镜头参数、对齐、合成设置）保存为默认配置 | `UMixedRealityCaptureComponent` |
| `SaveConfiguration` | 保存配置到指定存档槽 | `UMixedRealityCaptureComponent` |
| `LoadDefaultConfiguration` | 加载默认 MRC 配置 | `UMixedRealityCaptureComponent` |
| `LoadConfiguration` | 从指定存档槽加载配置 | `UMixedRealityCaptureComponent` |
| `ConstructCalibrationData` | 构造当前配置的校准数据对象（BlueprintNativeEvent，可重写） | `UMixedRealityCaptureComponent` |
| `ApplyCalibrationData` | 应用校准数据到组件（BlueprintNativeEvent，可重写） | `UMixedRealityCaptureComponent` |
| `FillOutCalibrationData` | 将当前参数填充到校准数据对象 | `UMixedRealityCaptureComponent` |
| `SetDeviceAttachment` | 将 MRC 绑定到指定追踪源（如手柄） | `UMixedRealityCaptureComponent` |
| `DetatchFromDevice` | 解除追踪设备绑定 | `UMixedRealityCaptureComponent` |
| `IsTracked` | 查询是否已被追踪设备追踪 | `UMixedRealityCaptureComponent` |
| `SetGarbageMatteActor` | 设置外部 Garbage Matte Actor 用于实时预览遮罩 | `UMixedRealityCaptureComponent` |
| `GetProjectionActor` | 获取投影 Actor（蓝图用） | `UMixedRealityCaptureComponent` |

### 核心节点 — AMixedRealityCaptureActor

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetAutoBroadcast` | 设置是否自动将画面输出到旁观者屏幕 | `AMixedRealityCaptureActor` |
| `IsBroadcasting` | 查询是否正在广播到旁观者屏幕 | `AMixedRealityCaptureActor` |
| `GetCaptureTexture` | 获取当前合成的渲染目标纹理 | `AMixedRealityCaptureActor` |

### 核心节点 — UMrcUtilLibrary（静态工具函数）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IsMixedRealityCaptureBroadcasting` | 查询 MRC 是否正在广播 | `UMrcUtilLibrary` |
| `SetMixedRealityCaptureBroadcasting` | 开启/关闭 MRC 广播 | `UMrcUtilLibrary` |
| `GetMixedRealityCaptureTexture` | 获取 MRC 合成纹理 | `UMrcUtilLibrary` |

### 核心节点 — Garbage Matte

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ApplyCalibrationData` | 应用校准数据到 Garbage Matte 组件 | `UMrcGarbageMatteCaptureComponent` |
| `SetGarbageMatteActor` | 设置 Garbage Matte Actor | `UMrcGarbageMatteCaptureComponent` |
| `GetGarbageMatteData` | 获取 Garbage Matte 数据 | `UMrcGarbageMatteCaptureComponent` |
| `SetFocalDriver` | 设置焦距驱动接口 | `UMrcGarbageMatteCaptureComponent` |
| `AddNewGabageMatte` | 添加新的 Garbage Matte 图元 | `AMrcGarbageMatteActor` |
| `CreateGarbageMatte` | 创建 Garbage Matte（BlueprintNativeEvent） | `AMrcGarbageMatteActor` |

### 事件

| 事件 | 说明 | 所在类 |
|---|---|---|
| `OnCaptureSourceOpened` | 摄像头视频源打开成功时触发，携带 `FMrcVideoCaptureFeedIndex` | `UMixedRealityCaptureComponent` |

### 使用示例（蓝图描述）

**基础设置：**

1. 在场景中放置 `AMixedRealityCaptureActor`（或其子类）
2. 在 Details 面板中配置 `CaptureComponent` 的属性：
   - `MediaSource`：指定 Media Player 用于接收摄像头画面
   - `VideoProcessingMaterial`：指定用于色键 (chroma key) 处理的材质
   - `LensDistortionParameters`：设置 OpenCV 镜头畸变参数
   - `TrackingLatency`：设置追踪延迟补偿（毫秒）
3. 勾选 `bAutoAttachToVRPlayer` 使其自动附着到 VR 玩家
4. 勾选 `bAutoBroadcast` 自动将画面输出到旁观者屏幕

**运行时标定流程：**

1. 调用 `ApplyCalibrationData` 应用预标定的数据（FOV、畸变参数、摄像头偏移等）
2. 校准数据包含：`FMrcLensCalibrationData`（FOV + 畸变）、`FMrcAlignmentSaveData`（位置/旋转/追踪源）、`FMrcCompositingSaveData`（设备URL/深度偏移/延迟）
3. 调用 `SaveAsDefaultConfiguration` 持久化标定结果

## C++ 用法

### 头文件引入

```cpp
#include "MixedRealityCaptureComponent.h"
#include "MixedRealityCaptureActor.h"
#include "MrcCalibrationData.h"
#include "MrcVideoCaptureDevice.h"
#include "MrcUtilLibrary.h"
#include "MrcGarbageMatteCaptureComponent.h"
```

### 基本用法

从源码中提取的典型用法模式。`MixedRealityCaptureComponent` 继承自 `USceneCaptureComponent2D`，是整个框架的核心。

```cpp
// 获取 MRC Actor（通过模块接口）
IMrcFrameworkModule* MrcModule = FModuleManager::GetModulePtr<IMrcFrameworkModule>("MixedRealityCaptureFramework");
AMixedRealityCaptureActor* MrcActor = MrcModule ? MrcModule->GetMixedRealityCaptureActor() : nullptr;

// 检查是否正在广播
bool bBroadcasting = UMrcUtilLibrary::IsMixedRealityCaptureBroadcasting();

// 获取合成纹理
UTexture* CaptureTexture = UMrcUtilLibrary::GetMixedRealityCaptureTexture();
```

**来源**: `MrcUtilLibrary.h`, `IMrcFrameworkModule.h`

### 校准数据操作

```cpp
// 从组件构造校准数据
UMrcCalibrationData* CalData = CaptureComponent->ConstructCalibrationData();

// 手动填充校准数据
UMrcCalibrationData* CalData = NewObject<UMrcCalibrationData>(GetTransientPackage());
CaptureComponent->FillOutCalibrationData(CalData);

// 保存到存档系统
CaptureComponent->SaveAsDefaultConfiguration();
CaptureComponent->SaveConfiguration("MySlot", 0);

// 加载标定数据
CaptureComponent->LoadDefaultConfiguration();
CaptureComponent->LoadConfiguration("MySlot", 0);

// 应用校准数据
CaptureComponent->ApplyCalibrationData(CalData);
```

**来源**: `MixedRealityCaptureComponent.cpp` (SaveConfiguration/LoadConfiguration/ApplyCalibrationData 实现)

### 镜头畸变处理

```cpp
// 设置镜头畸变参数（自动触发去畸变位移图更新）
FOpenCVLensDistortionParameters DistortionParams;
// ... 从 OpenCV 标定结果填充参数
CaptureComponent->SetLensDistortionParameters(DistortionParams);
```

框架通过 CVar 控制畸变行为：
- `mrc.undistortion` (bool)：启用/禁用去畸变
- `mrc.undistortion.bUseFocalAspectRatio` (bool)：使用焦距比校正宽高比
- `mrc.undistortion.CroppingAmount` (float, 0~1)：去畸变裁剪量
- `mrc.undistortion.bUseUndistortedFOV` (bool)：使用去畸变后的估算 FOV
- `mrc.FovOverride` (float)：手动覆盖 FOV
- `mrc.TrackingLatencyOverride` (int)：覆盖追踪延迟

**来源**: `MixedRealityCaptureComponent.cpp` (MRCaptureComponent_Impl 命名空间)

### 追踪设备绑定

```cpp
// 绑定到指定追踪源（如手柄的 MotionSource）
CaptureComponent->SetDeviceAttachment(FName("Right"));

// 解除绑定
CaptureComponent->DetatchFromDevice();

// 查询追踪状态
bool bTracked = CaptureComponent->IsTracked();
```

**来源**: `MixedRealityCaptureComponent.cpp` (RefreshDevicePairing)

### 进阶用法 — Garbage Matte

```cpp
// 创建 Garbage Matte 组件
UMrcGarbageMatteCaptureComponent* GarbageMatteComp = 
    MRCaptureComponent_Impl::CreateGarbageMatteComponent(CaptureComponent, TrackingOrigin);

// 设置外部 Garbage Matte Actor（用于实时预览）
AMrcGarbageMatteActor* MatteActor = /* ... */;
CaptureComponent->SetGarbageMatteActor(MatteActor);

// 获取 Garbage Matte 数据
TArray<FMrcGarbageMatteSaveData> MatteData;
GarbageMatteComp->GetGarbageMatteData(MatteData);
```

**来源**: `MrcGarbageMatteCaptureComponent.h`, `MixedRealityCaptureComponent.cpp`

### 进阶用法 — 视频采集设备枚举

```cpp
// 枚举所有可用的视频采集设备
TArray<FMrcVideoCaptureFeedIndex> Feeds = FMrcVideoCaptureUtils::EnumerateAvailableFeeds(MediaPlayer);

// 排序选取最佳设备
FMrcVideoCaptureFeedIndex BestFeed;
// FeedSortPredicate 支持按宽高比、分辨率、格式优先级排序
```

**来源**: `MrcVideoCaptureDevice.h`

### 进阶用法 — FocalDriver 接口

```cpp
// 实现 IMrcFocalDriver 接口以提供自定义焦距信息
UCLASS()
class UMyFocalDriver : public UObject, public IMrcFocalDriver
{
    GENERATED_BODY()
public:
    virtual float GetHorizontalFieldOfView_Implementation() const override
    {
        return 90.0f; // 返回自定义 FOV
    }
};

// 设置到 Garbage Matte 组件
GarbageMatteComp->SetFocalDriver(MyFocalDriver);
```

**来源**: `IMrcFocalDriver.h`

## Demo 示例

以下是一个最小的 MRC 设置示例，展示如何在 C++ 中初始化和配置 MRC 捕获。

**MyMrcGameMode.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "MyMrcGameMode.generated.h"

class AMixedRealityCaptureActor;
class UMrcCalibrationData;

UCLASS()
class AMyMrcGameMode : public AGameModeBase
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;

    UPROPERTY(EditAnywhere, Category = "MRC")
    TSubclassOf<AMixedRealityCaptureActor> MrcActorClass;

    UPROPERTY(EditAnywhere, Category = "MRC")
    FString CalibrationSlotName = "DefaultMRC";

private:
    UPROPERTY()
    TObjectPtr<AMixedRealityCaptureActor> SpawnedMrcActor;
};
```

**MyMrcGameMode.cpp**
```cpp
#include "MyMrcGameMode.h"
#include "MixedRealityCaptureActor.h"
#include "MixedRealityCaptureComponent.h"
#include "MrcCalibrationData.h"
#include "MrcUtilLibrary.h"
#include "Kismet/GameplayStatics.h"

void AMyMrcGameMode::BeginPlay()
{
    Super::BeginPlay();

    // Spawn MRC Actor
    if (MrcActorClass)
    {
        FActorSpawnParameters SpawnParams;
        SpawnedMrcActor = GetWorld()->SpawnActor<AMixedRealityCaptureActor>(
            MrcActorClass, FTransform::Identity, SpawnParams);
    }

    if (!SpawnedMrcActor) return;

    UMixedRealityCaptureComponent* Capture = SpawnedMrcActor->CaptureComponent;
    if (!Capture) return;

    // 加载预标定的配置
    Capture->LoadConfiguration(CalibrationSlotName, 0);

    // 启用广播到旁观者屏幕
    SpawnedMrcActor->SetAutoBroadcast(true);
}
```

**Build.cs 依赖**
```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "MixedRealityCaptureFramework",
    "MediaAssets",  // MediaPlayer 支持
});
```

## 模块依赖

从 `MixedRealityCaptureFramework.Build.cs` 的 `PublicDependencyModuleNames` 和 `PrivateDependencyModuleNames` 提取：

| 模块 | 用途 |
|---|---|
| `MediaAssets` | 公开依赖，Media Player 和媒体资产支持 |
| `Core` | UE 核心库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心（Actor、Component、SaveGame 等） |
| `Media` | 底层媒体框架 |
| `HeadMountedDisplay` | HMD 接口、追踪系统、旁观者屏幕控制 |
| `InputCore` | 输入系统（EControllerHand 等） |
| `MediaUtils` | 媒体工具函数 |
| `RenderCore` | 渲染核心 |
| `OpenCVLensDistortion` | OpenCV 镜头畸变校正 |
| `OpenCVHelper` | OpenCV 辅助函数 |
| `XRBase` | XR 基础设施 |
| `EditorFramework` | 编辑器框架（仅编辑器构建） |
| `UnrealEd` | 编辑器功能（仅编辑器构建） |

插件级依赖：
- **OpenCVLensDistortion**：提供 `FOpenCVLensDistortionParameters` 和去畸变 UV 位移图生成
- **XRBase**：提供 XR 追踪系统基础接口

## CVar 控制台变量

| CVar | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `mrc.undistortion` | bool | `true` | 启用/禁用去畸变处理 |
| `mrc.undistortion.bUseFocalAspectRatio` | bool | `true` | 使用焦距比校正宽高比拉伸 |
| `mrc.undistortion.CroppingAmount` | float | `0.0` | 去畸变裁剪量 (0~1)，1 表示裁掉所有空白像素 |
| `mrc.undistortion.bUseUndistortedFOV` | bool | `true` | 使用 OpenCV 估算的去畸变 FOV |
| `mrc.FovOverride` | float | `0.0` | 手动覆盖 FOV（>0 时生效） |
| `mrc.TrackingLatencyOverride` | int | `0` | 覆盖追踪延迟（毫秒，>0 时生效） |

## 核心架构

### 类层次结构

```
USceneCaptureComponent2D
  └── UMixedRealityCaptureComponent    ← 核心组件，管理视频输入、畸变校正、投影、追踪
        ├── UChildActorComponent → AMrcProjectionActor  ← 投影平面
        ├── UMotionControllerComponent (PairedTracker)   ← 追踪设备绑定
        ├── USceneComponent (TrackingOriginOffset)       ← 追踪原点偏移补偿
        └── UMrcGarbageMatteCaptureComponent             ← Garbage Matte 渲染

AActor
  └── AMixedRealityCaptureActor         ← 顶层 Actor，封装 MRC 组件，管理自动附着和广播
        └── UMixedRealityCaptureComponent (CaptureComponent)

USaveGame
  └── UMrcCalibrationData               ← 校准数据（镜头、对齐、合成、Garbage Matte）
        └── UMrcCalibrationSaveGame     ← 存档元数据扩展
```

### 数据流

```
外部摄像头 → Media Player → VideoProcessingMaterial (色键处理)
                                    ↓
                          OpenCV 去畸变 (UV Displacement Map)
                                    ↓
                          SceneCaptureComponent2D 渲染
                                    ↓
                          MrcProjectionActor (投影平面, 跟踪 HMD 深度)
                                    ↓
                          TextureTarget → 旁观者屏幕 (Spectator Screen)
```

### 追踪延迟补偿

框架通过 `FMrcLatencyViewExtension`（一个 `FSceneViewExtension`）实现追踪延迟补偿。在渲染前将运动控制器组件的位置回退到 N 毫秒前的状态，渲染后再恢复。这通过 `FMotionDelayService` 注册延迟客户端来实现。

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2024-11-25 | `f8c6427` | 转换渲染器使用新的 SceneRenderBuilder 接口 — 适配 UE5 渲染管线重构 |
| 2024-11-14 | `a74e120` | 修复 IDelegateInstance::RemoveAll() 和 IsCompactable() 避免解析远程对象 |
| 2024-03-13 | `32e5d7e` | 废弃 ini 中的 MatchSubstring CoreRedirects，改用 `MatchWildcard=true` |

### 维护评价

- **年龄**：2018 年创建，约 8 年历史，从 UE 4.20 时代的 `MixedRealityFramework` 迁移重命名而来
- **更新频率**：最近一次功能更新在 2024 年 11 月（适配渲染接口变更），整体更新频率较低
- **维护状态**：**维护中但不活跃** — 仅有适配性更新（跟随引擎接口变更），无新功能开发
- **实验性标记**：`.uplugin` 中 `IsBetaVersion=true`，且 `EnabledByDefault=false`，表明 Epic 仍将其视为实验性功能
- **平台限制**：仅支持 Win64 和 Linux
- **已知限制**：
  - 作为 Beta 功能，API 可能在未来版本中变更
  - 依赖 OpenCV 镜头畸变插件
  - 旁观者屏幕模式管理有 TODO 注释，表明接口设计不够完善
- **推荐**：如果你需要 VR 混合现实捕捉功能，这是 UE5 唯一的官方方案，可以使用但需注意其 Beta 状态。对于生产环境，建议充分测试并做好 API 变更的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MixedRealityCaptureFramework)
- [官方文档](https://answers.unrealengine.com/)（无专属文档页，仅有支持论坛）
