# XR Base

> XR Base Feature Implementations.  (Generally this plugin will be automatically enabled by another plugin that requires it.)

| 属性 | 值 |
|---|---|
| 分类 | Virtual Reality |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `XRBase` (Runtime), `XRBaseEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2023-04-10 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/XRBase) | |

## 用途

XRBase 是 Unreal Engine XR（扩展现实）子系统的**基础实现层**。它不是一个独立使用的插件，而是为各种 XR 运行时插件（如 OpenXR、OculusHMD 等）提供共享的基类和工具函数库。

这个插件存在的原因是：不同 XR 设备的驱动实现有很多共同逻辑（如跟踪系统管理、运动控制器基类、立体渲染层管理、加载屏幕、观察者屏幕等），XRBase 将这些通用实现抽取为可复用的基类，避免每个 XR 插件重复造轮子。

**核心职责**：
- 为 `IXRTrackingSystem` 提供默认实现 (`FXRTrackingSystemBase`)
- 为 `IHeadMountedDisplay` 提供默认实现 (`FHeadMountedDisplayBase`)
- 为 `IMotionController` 提供默认实现 (`FXRMotionControllerBase`)
- 提供 HMD 蓝图函数库、运动追踪设备管理、XR 加载屏幕等蓝图可调用功能
- 提供立体层（Stereo Layer）管理、交换链（Swap Chain）、渲染桥接等底层渲染支持
- 提供设备可视化组件和 VR 通知组件

## 使用场景

- **你是 XR 设备驱动开发者**：继承 `FHeadMountedDisplayBase` 或 `FXRTrackingSystemBase` 来实现新的 XR 设备支持
- **你需要查询 HMD 状态**：通过 `UHeadMountedDisplayFunctionLibrary` 蓝图节点获取 HMD 方位、跟踪状态等
- **你需要管理运动控制器追踪**：通过 `UMotionTrackedDeviceFunctionLibrary` 控制哪些设备被追踪
- **你需要 VR 加载屏幕**：通过 `UXRLoadingScreenFunctionLibrary` 设置 VR 专用加载画面
- **你需要监听 VR 事件**：通过 `UVRNotificationsComponent` 响应 HMD 连接/断开、佩戴/摘下等事件
- **你需要显示 XR 设备模型**：通过 `UXRDeviceVisualizationComponent` 渲染控制器等设备的 3D 模型

## 蓝图用法

### HMD 状态查询节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IsHeadMountedDisplayEnabled` | 当前是否正在使用 HMD | `UHeadMountedDisplayFunctionLibrary` |
| `IsHeadMountedDisplayConnected` | HMD 硬件是否已连接 | `UHeadMountedDisplayFunctionLibrary` |
| `EnableHMD` | 启用/禁用 HMD 和立体渲染 | `UHeadMountedDisplayFunctionLibrary` |
| `GetHMDDeviceName` | 获取当前 HMD 设备名称 | `UHeadMountedDisplayFunctionLibrary` |
| `GetHMDWornState` | 获取佩戴状态（Unknown/Worn/NotWorn） | `UHeadMountedDisplayFunctionLibrary` |
| `GetOrientationAndPosition` | 获取 HMD 当前朝向和位置 | `UHeadMountedDisplayFunctionLibrary` |
| `HasValidTrackingPosition` | HMD 是否有有效位置跟踪 | `UHeadMountedDisplayFunctionLibrary` |

### 跟踪与坐标系节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetTrackingOrigin` | 设置跟踪原点类型（EyeLevel/Floor/Stage） | `UHeadMountedDisplayFunctionLibrary` |
| `GetTrackingOrigin` | 获取当前跟踪原点类型 | `UHeadMountedDisplayFunctionLibrary` |
| `GetTrackingToWorldTransform` | 获取跟踪空间到世界空间的变换 | `UHeadMountedDisplayFunctionLibrary` |
| `GetWorldToMetersScale` | 获取世界到米的缩放比例 | `UHeadMountedDisplayFunctionLibrary` |
| `SetWorldToMetersScale` | 设置世界到米的缩放比例 | `UHeadMountedDisplayFunctionLibrary` |
| `ResetOrientationAndPosition` | 重置朝向和位置 | `UHeadMountedDisplayFunctionLibrary` |
| `GetPlayAreaBounds` | 获取可玩区域边界 | `UHeadMountedDisplayFunctionLibrary` |
| `GetPlayAreaRect` | 获取可玩区域矩形 | `UHeadMountedDisplayFunctionLibrary` |

### XR 设备查询节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `EnumerateTrackedDevices` | 枚举所有被追踪的 XR 设备 | `UHeadMountedDisplayFunctionLibrary` |
| `GetDevicePose` | 获取指定设备的跟踪空间位姿 | `UHeadMountedDisplayFunctionLibrary` |
| `GetDeviceWorldPose` | 获取指定设备的世界空间位姿 | `UHeadMountedDisplayFunctionLibrary` |
| `IsDeviceTracking` | 检查设备是否正在被追踪 | `UHeadMountedDisplayFunctionLibrary` |
| `GetMotionControllerState` | 获取运动控制器状态 | `UHeadMountedDisplayFunctionLibrary` |
| `GetHandTrackingState` | 获取手部追踪状态 | `UHeadMountedDisplayFunctionLibrary` |
| `GetCurrentInteractionProfile` | 获取当前交互配置文件 | `UHeadMountedDisplayFunctionLibrary` |

### 运动追踪设备管理节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IsMotionTrackedDeviceCountManagementNecessary` | 是否需要管理追踪设备数量 | `UMotionTrackedDeviceFunctionLibrary` |
| `GetMaximumMotionTrackedControllerCount` | 最大可追踪控制器数 | `UMotionTrackedDeviceFunctionLibrary` |
| `EnableMotionTrackingOfSource` | 启用指定来源的追踪 | `UMotionTrackedDeviceFunctionLibrary` |
| `DisableMotionTrackingOfSource` | 禁用指定来源的追踪 | `UMotionTrackedDeviceFunctionLibrary` |
| `DisableMotionTrackingOfAllControllers` | 禁用所有控制器追踪 | `UMotionTrackedDeviceFunctionLibrary` |
| `EnumerateMotionSources` | 枚举所有可用运动源 | `UMotionTrackedDeviceFunctionLibrary` |
| `IsMotionSourceTracking` | 检查运动源是否正在被追踪 | `UMotionTrackedDeviceFunctionLibrary` |

### 加载屏幕节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetLoadingScreen` | 设置 VR 加载屏幕纹理 | `UXRLoadingScreenFunctionLibrary` |
| `AddLoadingScreenSplash` | 添加加载画面飞溅元素 | `UXRLoadingScreenFunctionLibrary` |
| `ShowLoadingScreen` | 显示加载屏幕 | `UXRLoadingScreenFunctionLibrary` |
| `HideLoadingScreen` | 隐藏加载屏幕 | `UXRLoadingScreenFunctionLibrary` |
| `ClearLoadingScreenSplashes` | 清除所有飞溅元素 | `UXRLoadingScreenFunctionLibrary` |

### 观察者屏幕节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IsSpectatorScreenModeControllable` | 观察者屏幕模式是否可控 | `UHeadMountedDisplayFunctionLibrary` |
| `SetSpectatorScreenMode` | 设置社交屏幕模式 | `UHeadMountedDisplayFunctionLibrary` |
| `SetSpectatorScreenTexture` | 设置社交屏幕纹理 | `UHeadMountedDisplayFunctionLibrary` |
| `SetSpectatorScreenModeTexturePlusEyeLayout` | 设置纹理+眼睛布局 | `UHeadMountedDisplayFunctionLibrary` |

### VR 通知组件

`UVRNotificationsComponent` 提供以下蓝图可绑定委托：

| 委托 | 说明 |
|---|---|
| `HMDTrackingInitializingAndNeedsHMDToBeTrackedDelegate` | HMD 正在初始化，需要被追踪 |
| `HMDTrackingInitializedDelegate` | HMD 初始化完成 |
| `HMDRecenteredDelegate` | HMD 已重新居中 |
| `HMDLostDelegate` | HMD 连接丢失 |
| `HMDReconnectedDelegate` | HMD 重新连接 |
| `HMDConnectCanceledDelegate` | 用户取消连接 |
| `HMDPutOnHeadDelegate` | 检测到佩戴 |
| `HMDRemovedFromHeadDelegate` | 检测到摘下 |
| `VRControllerRecenteredDelegate` | 控制器重新居中 |
| `XRTrackingOriginChangedDelegate` | 跟踪原点改变 |
| `XRPlayAreaChangedDelegate` | 游玩区域改变 |
| `XRInteractionProfileChangedDelegate` | 交互配置文件改变 |

### 使用示例（蓝图描述）

**获取 HMD 朝向和位置**：
1. 创建一个 `Get Orientation and Position` 节点
2. 将 `Device Rotation` 和 `Device Position` 输出连接到需要使用的变量或组件

**设置 VR 加载屏幕**：
1. 调用 `Set Loading Screen`，传入一个 `UTexture2D` 引用和缩放参数
2. 调用 `Show Loading Screen` 显示它
3. 加载完成后调用 `Hide Loading Screen`

**监听 HMD 事件**：
1. 在 Actor 上添加 `VR Notifications Component`
2. 在蓝图中绑定 `HMD Lost Delegate` 或 `HMD Reconnected Delegate` 等委托
3. 在委托回调中处理相应逻辑

## C++ 用法

### 头文件引入

```cpp
// HMD 功能函数库
#include "HeadMountedDisplayFunctionLibrary.h"

// 运动追踪设备函数库
#include "MotionTrackedDeviceFunctionLibrary.h"

// XR 加载屏幕函数库
#include "XRLoadingScreenFunctionLibrary.h"

// VR 通知组件
#include "VRNotificationsComponent.h"

// 设备可视化组件
#include "XRDeviceVisualizationComponent.h"

// 追踪系统基类（用于实现新的 XR 后端）
#include "XRTrackingSystemBase.h"

// HMD 基类（用于实现新的 XR 后端）
#include "HeadMountedDisplayBase.h"

// 运动控制器基类（用于实现新的 XR 后端）
#include "XRMotionControllerBase.h"
```

### 基本用法：查询 HMD 状态

```cpp
// 检查 HMD 是否启用
bool bEnabled = UHeadMountedDisplayFunctionLibrary::IsHeadMountedDisplayEnabled();

// 获取 HMD 方位和位置
FRotator DeviceRotation;
FVector DevicePosition;
UHeadMountedDisplayFunctionLibrary::GetOrientationAndPosition(DeviceRotation, DevicePosition);

// 获取跟踪原点类型
EHMDTrackingOrigin::Type Origin = UHeadMountedDisplayFunctionLibrary::GetTrackingOrigin();
```

### 进阶用法：实现新的 XR 跟踪系统

继承 `FXRTrackingSystemBase` 是实现新 XR 设备支持的标准方式：

```cpp
#include "HeadMountedDisplayBase.h"

class FMyXRSystem : public FHeadMountedDisplayBase
{
public:
    FMyXRSystem(IARSystemSupport* InAR)
        : FHeadMountedDisplayBase(InAR)
    {}

    // 实现 IXRTrackingSystem 接口
    virtual FName GetSystemName() const override
    {
        return FName(TEXT("MyXRSystem"));
    }

    virtual bool DoesSupportPositionalTracking() const override
    {
        return true; // 支持位置追踪
    }

    virtual bool GetCurrentPose(int32 DeviceId, FQuat& OutOrientation, FVector& OutPosition) override
    {
        // 从硬件获取当前位姿
        return true;
    }

    virtual uint32 CountTrackedDevices(EXRTrackedDeviceType Type) override
    {
        // 返回被追踪设备数量
        return 1;
    }

    // ... 其他必须实现的方法
};
```

### 进阶用法：继承运动控制器基类

```cpp
#include "XRMotionControllerBase.h"

class FMyMotionController : public FXRMotionControllerBase
{
public:
    // 必须实现的纯虚函数
    virtual bool GetControllerOrientationAndPosition(
        const int32 ControllerIndex,
        const FName MotionSource,
        FRotator& OutOrientation,
        FVector& OutPosition,
        float WorldToMetersScale) const override
    {
        // 从硬件获取控制器位姿
        return true;
    }

    virtual ETrackingStatus GetControllerTrackingStatus(
        const int32 ControllerIndex,
        const FName MotionSource) const override
    {
        return ETrackingStatus::Tracked;
    }
};
```

## Demo 示例

### 最小 HMD 状态查询示例

```cpp
// MyVRActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "MyVRActor.generated.h"

UCLASS()
class AMyVRActor : public AActor
{
    GENERATED_BODY()
public:
    virtual void Tick(float DeltaTime) override
    {
        Super::Tick(DeltaTime);

        if (UHeadMountedDisplayFunctionLibrary::IsHeadMountedDisplayEnabled())
        {
            FRotator Rotation;
            FVector Position;
            UHeadMountedDisplayFunctionLibrary::GetOrientationAndPosition(Rotation, Position);

            UE_LOG(LogTemp, Log, TEXT("HMD Pos: %s, Rot: %s"),
                *Position.ToString(), *Rotation.ToString());
        }
    }
};
```

**Build.cs 依赖**：
```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "HeadMountedDisplay",
    "XRBase",
    "Core",
    "CoreUObject",
    "Engine"
});
```

## 模块依赖

### XRBase (Runtime)

| 模块 | 用途 |
|---|---|
| `HeadMountedDisplay` | XR 核心接口定义（IXRTrackingSystem, IHeadMountedDisplay 等） |
| `AugmentedReality` | AR 系统支持接口 |
| `Core` | UE 核心库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `EngineSettings` | 引擎设置 |
| `Renderer` | 渲染器 |
| `RenderCore` | 渲染核心 |
| `RHI` | 渲染硬件接口 |
| `InputCore` | 输入核心 |
| `Slate` | UI 框架 |

### XRBaseEditor (Editor)

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心库 |
| `CoreUObject` | UObject 系统 |
| `PropertyEditor` | 属性编辑器面板定制 |
| `InputCore` | 输入核心 |
| `SlateCore` | Slate 核心 |
| `Slate` | UI 框架 |
| `HeadMountedDisplay` | XR 核心接口 |
| `XRBase` | XR 基础运行时模块 |

## 维护状态

### 近期更新

1. **2025-09-12** `8406696f` — Explicitly adding various missing headers to fix non-unity build errors after large CoreUObject change.
   - 编译修复：为非 unity build 配置显式添加缺失的头文件。

2. **2025-08-29** `1d7d2cdb` — Add missing include from some no-PCH configurations, including explicit include for GCObject.h
   - 编译修复：修复 no-PCH 配置下的缺失 include。

3. **2025-08-04** `0e172e41` — Move the change adding xr.MobilePrimaryScalingMode back in after it was backed out due to issues with cine cameras/viewrect quantization.
   - 功能更新：重新引入 `xr.MobilePrimaryScalingMode` CVar，控制移动端主缩放是否重定向到 HMD 运行时。修复了与 cine cameras 和 viewrect 量化相关的问题。

### 维护评价

- **创建时间**：2023-04-10，约 3 年前
- **最近更新**：2025-09-12，最近 1 个月内有更新
- **维护状态**：**活跃维护** — 作为 UE5 XR 子系统的基础层，随着引擎更新持续维护
- **注意事项**：
  - 该插件默认不启用（`EnabledByDefault: false`），通常由其他 XR 插件（如 OpenXR）自动启用
  - 多个 API 在 5.6 版本中标记为 `UE_DEPRECATED`，建议使用新的替代 API
  - `XRThreadUtils.h` 中的所有函数在 5.7 中标记为废弃，应使用 `ENQUEUE_RENDER_COMMAND` 替代
  - `TStereoLayerManager` 在 5.6 中标记为废弃，应使用 `FSimpleLayerManager`
- **推荐**：如果你在开发 XR 设备驱动或需要使用 UE5 的 XR 蓝图 API，这个插件是必选的依赖项。普通游戏开发者通常不需要直接引用此插件，而是通过 OpenXR 等上层插件间接使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/XRBase)
- [HeadMountedDisplay 模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Source/Runtime/HeadMountedDisplay)
- [OpenXR 插件源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/OpenXR)
