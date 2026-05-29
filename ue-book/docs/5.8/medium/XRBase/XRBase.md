# XRBase

> XR Base Feature Implementations.  (Generally this plugin will be automatically enabled by another plugin that requires it.)

| 属性 | 值 |
|---|---|
| 中文名 | XR基础插件 |
| 分类 | Virtual Reality |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `XRBase` (Runtime), `XRBaseEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2023-04-10 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/XRBase) | |

## 用途

XRBase 插件的**核心目的是将虚幻引擎核心的 HeadMountedDisplay (HMD) 相关运行时代码模块化为一个独立插件**。这主要基于两个原因：
1.  **减少主引擎开销**：将非核心的 XR 实现代码从主引擎模块中移出，可以减小最小化虚幻可执行文件的体积和内存占用。
2.  **优化项目组织**：将特定于 XR 的功能归集到一个插件中，使引擎核心更加精简，项目依赖关系更清晰。

该插件不包含任何特定的 XR 平台实现（如 OpenXR, Oculus, SteamVR）。它提供了**通用的接口、基类和蓝图函数库**，供其他具体的 XR 平台插件（如 OpenXR）继承和调用。简而言之，它是所有 XR 功能的“地基”。

## 使用场景

-   **你正在开发或使用一个具体的 XR 平台插件（如 OpenXR）**：该插件会自动依赖并启用 `XRBase`，为你提供 HMD 检测、跟踪原点设置、运动控制器查询等基础功能。
-   **你需要在蓝图中查询 HMD 状态或设备跟踪信息**：`HeadMountedDisplayFunctionLibrary` 和 `MotionTrackedDeviceFunctionLibrary` 提供了直接可用的蓝图节点。
-   **你正在为一个新的 XR 硬件平台开发引擎插件**：需要从 `FXRTrackingSystemBase`、`FHeadMountedDisplayBase` 或 `FXRMotionControllerBase` 继承，以快速获得符合引擎规范的基础实现。

## 蓝图用法

### 核心节点

以下节点来自 `UHeadMountedDisplayFunctionLibrary`，分类为 `Input|HeadMountedDisplay`。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IsHeadMountedDisplayEnabled` | 检查当前是否正在使用 HMD 进行立体渲染。 | `UHeadMountedDisplayFunctionLibrary` |
| `IsHeadMountedDisplayConnected` | 检查 HMD 硬件是否已连接并准备就绪。 | `UHeadMountedDisplayFunctionLibrary` |
| `EnableHMD` | 切换 HMD / 立体渲染的开关状态。 | `UHeadMountedDisplayFunctionLibrary` |
| `GetHMDDeviceName` | 获取当前活动的 HMD 设备名称（如 `OculusHMD`）。 | `UHeadMountedDisplayFunctionLibrary` |
| `GetOrientationAndPosition` | 获取 HMD 在追踪空间中的当前朝向和位置。 | `UHeadMountedDisplayFunctionLibrary` |
| `GetTrackingOrigin` | 获取当前的追踪原点类型（眼部高度或地面高度）。 | `UHeadMountedDisplayFunctionLibrary` |
| `SetTrackingOrigin` | 设置追踪原点类型。 | `UHeadMountedDisplayFunctionLibrary` |
| `GetWorldToMetersScale` | 获取世界到米的转换比例。 | `UHeadMountedDisplayFunctionLibrary` |
| `SetWorldToMetersScale` | 设置世界到米的转换比例（影响玩家对世界规模的感知）。 | `UHeadMountedDisplayFunctionLibrary` |
| `EnumerateTrackedDevices` | 枚举所有当前被追踪的 XR 设备（通用查询）。 | `UHeadMountedDisplayFunctionLibrary` |
| `GetDevicePose` | 查询指定设备的追踪状态、朝向和位置（在追踪空间）。 | `UHeadMountedDisplayFunctionLibrary` |
| `GetDeviceWorldPose` | 查询指定设备在世界空间中的朝向和位置。 | `UHeadMountedDisplayFunctionLibrary` |

以下节点来自 `UMotionTrackedDeviceFunctionLibrary`，分类为 `Input|MotionTracking`。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IsMotionTrackedDeviceCountManagementNecessary` | 检查是否需要手动管理同时追踪的运动控制器数量。 | `UMotionTrackedDeviceFunctionLibrary` |
| `EnableMotionTrackingOfSource` | 为指定玩家和运动源（名称）启用追踪。 | `UMotionTrackedDeviceFunctionLibrary` |
| `DisableMotionTrackingOfSource` | 为指定玩家和运动源（名称）禁用追踪。 | `UMotionTrackedDeviceFunctionLibrary` |
| `IsMotionTrackingEnabledForSource` | 查询指定玩家和运动源的追踪是否启用。 | `UMotionTrackedDeviceFunctionLibrary` |
| `EnumerateMotionSources` | 枚举当前所有可用的运动源名称。 | `UMotionTrackedDeviceFunctionLibrary` |
| `GetActiveTrackingSystemName` | 获取当前活动的 XR 追踪系统名称。 | `UMotionTrackedDeviceFunctionLibrary` |

### 使用示例（蓝图描述）

在蓝图中，你可以将 `GetOrientationAndPosition` 节点的输出连接到一个物体的 `SetWorldRotation` 和 `SetWorldLocation` 来实现一个跟随 HMD 视角的相机。或者，使用 `GetDeviceWorldPose` 直接获取运动控制器在世界坐标下的位置来驱动一个手部网格体。对于设备管理，先用 `IsMotionTrackedDeviceCountManagementNecessary` 判断，如果需要管理，则使用 `EnableMotionTrackingOfSource` 和 `DisableMotionTrackingOfSource` 来动态开关特定控制器的追踪。

## C++ 用法

### 头文件引入

```cpp
#include "HeadMountedDisplayFunctionLibrary.h"
#include "XRTrackingSystemBase.h"
#include "HeadMountedDisplayBase.h"
```

### 基本用法

`FXRTrackingSystemBase` 是实现 `IXRTrackingSystem` 接口的基类，为 XR 后端开发者提供了大量默认实现。

```cpp
// 示例：继承并实现一个自定义的 HMD 跟踪系统
// 来源：HeadMountedDisplayBase.h / XRTrackingSystemBase.h 的设计思路
class FMyCustomHMD : public FHeadMountedDisplayBase // FHeadMountedDisplayBase 继承自 FXRTrackingSystemBase
{
public:
    FMyCustomHMD(IARSystemSupport* InARImplementation)
        : FHeadMountedDisplayBase(InARImplementation)
    {
    }

    // 必须实现的核心虚函数
    virtual bool DoesSupportPositionalTracking() const override
    {
        return true; // 假设我们的设备支持位置追踪
    }

    virtual EHMDTrackingOrigin::Type GetTrackingOrigin() const override
    {
        // 根据设备状态返回，例如地面高度
        return EHMDTrackingOrigin::Stage;
    }

    // IXRTrackingSystem 接口
    virtual FName GetSystemName() const override
    {
        return TEXT("MyCustomHMD");
    }
    
    // IHeadMountedDisplay 接口 (通过 FHeadMountedDisplayBase)
    virtual bool IsHMDConnected() override
    {
        // 查询你的硬件连接状态
        return bIsHardwareConnected;
    }
    // ... 其他需要覆写的方法
};
```

### 进阶用法

`FHeadMountedDisplayBase` 整合了 `FXRTrackingSystemBase`、`IHeadMountedDisplay` 和 `IStereoRendering` 接口，并提供了默认的立体层 (`StereoLayer`) 和旁观者屏幕 (`SpectatorScreen`) 管理。你还可以使用 `FXRSwapChain` 来管理 XR 交换链资源。

```cpp
#include "XRSwapChain.h"
#include "XRRenderBridge.h"

// 创建一个自定义的 XR 交换链并获取其纹理引用
TArray<FTextureRHIRef> TextureChain;
// ... 填充交换链纹理
FTextureRHIRef AliasedTexture = TextureChain[0]; // 通常第一个纹理作为别名纹理

FXRSwapChainPtr MySwapChain = MakeShareable(new FXRSwapChain(MoveTemp(TextureChain), AliasedTexture));
FTextureRHIRef CurrentTexture = MySwapChain->GetTextureRef();

// 获取当前交换链索引（用于同步）
uint32 CurrentIndex = MySwapChain->GetSwapChainIndex_RHIThread();
```

## Demo 示例

一个最小的自定义 XR 系统实现框架。

**MyCustomXRSystem.h**
```cpp
#pragma once
#include "HeadMountedDisplayBase.h"

class FMyCustomXRSystem : public FHeadMountedDisplayBase
{
public:
    FMyCustomXRSystem(IARSystemSupport* InARImplementation);
    virtual ~FMyCustomXRSystem();

    // IXRSystemIdentifier
    virtual FName GetSystemName() const override;
    virtual int32 GetXRSystemFlags() const override;

    // IXRTrackingSystem
    virtual bool DoesSupportPositionalTracking() const override;
    virtual uint32 CountTrackedDevices(EXRTrackedDeviceType Type = EXRTrackedDeviceType::Any) override;
    virtual bool GetCurrentPose(int32 DeviceId, FQuat& OutOrientation, FVector& OutPosition) override;
    virtual void SetTrackingOrigin(EHMDTrackingOrigin::Type NewOrigin) override;
    virtual EHMDTrackingOrigin::Type GetTrackingOrigin() const override;

    // IHeadMountedDisplay
    virtual bool IsHMDConnected() override;
    virtual bool GetHMDDeviceName(FString& DeviceName) override;

private:
    bool bIsConnected;
    EHMDTrackingOrigin::Type CurrentTrackingOrigin;
};
```

**MyCustomXRSystem.cpp**
```cpp
#include "MyCustomXRSystem.h"

FMyCustomXRSystem::FMyCustomXRSystem(IARSystemSupport* InARImplementation)
    : FHeadMountedDisplayBase(InARImplementation)
    , bIsConnected(false)
    , CurrentTrackingOrigin(EHMDTrackingOrigin::Local)
{
}

FMyCustomXRSystem::~FMyCustomXRSystem() = default;

FName FMyCustomXRSystem::GetSystemName() const
{
    return TEXT("MyCustomXR");
}

int32 FMyCustomXRSystem::GetXRSystemFlags() const
{
    return EXRSystemFlags::IsHeadMounted;
}

bool FMyCustomXRSystem::DoesSupportPositionalTracking() const
{
    return true; // 假设支持6DOF
}

uint32 FMyCustomXRSystem::CountTrackedDevices(EXRTrackedDeviceType Type)
{
    // 假设只有1个HMD设备
    if (Type == EXRTrackedDeviceType::HeadMountedDisplay || Type == EXRTrackedDeviceType::Any)
    {
        return bIsConnected ? 1 : 0;
    }
    return 0;
}

bool FMyCustomXRSystem::GetCurrentPose(int32 DeviceId, FQuat& OutOrientation, FVector& OutPosition)
{
    if (DeviceId == HMDDeviceId && bIsConnected)
    {
        // 从你的硬件API获取位姿数据
        // OutOrientation = ...;
        // OutPosition = ...;
        return true;
    }
    return false;
}

void FMyCustomXRSystem::SetTrackingOrigin(EHMDTrackingOrigin::Type NewOrigin)
{
    CurrentTrackingOrigin = NewOrigin;
    // 通知系统追踪原点改变
    OnTrackingOriginChanged();
}

EHMDTrackingOrigin::Type FMyCustomXRSystem::GetTrackingOrigin() const
{
    return CurrentTrackingOrigin;
}

bool FMyCustomXRSystem::IsHMDConnected()
{
    // 查询硬件连接状态
    // bIsConnected = CheckHardwareConnection();
    return bIsConnected;
}

bool FMyCustomXRSystem::GetHMDDeviceName(FString& DeviceName)
{
    DeviceName = TEXT("My Custom HMD 1.0");
    return true;
}
```

## 模块依赖

从 `XRBase.Build.cs` 和 `XRBaseEditor.Build.cs` 分析，该插件依赖于引擎核心的 HeadMountedDisplay 和 AugmentedReality 模块。对于使用此插件（通常是通过依赖它的具体XR插件）的项目，你的模块通常无需直接声明对 `XRBase` 的依赖，因为它会被上游插件间接提供。

| 模块 | 用途 |
|---|---|
| `HeadMountedDisplay` | 提供 `IXRTrackingSystem`, `IHeadMountedDisplay` 等核心接口定义。XRBase 是这些接口的参考实现。 |
| `AugmentedReality` | 提供 `IARSystemSupport` 接口，`FXRTrackingSystemBase` 的构造函数需要它。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，双精度常量到单精度浮点数截断时产生的编译器警告。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧的 UE_LOG 日志宏迁移到新的 UE_LOGF 宏。 |
| 2026-04-08 | `01e78a0b` | Moving open xr shaders to XR base | 将 OpenXR 相关的着色器代码迁移到 XRBase 插件中，进一步集中 XR 渲染代码。 |
| 2026-04-03 | `22c896f3` | PR #13335: Add OpenXR XR_KHR_COMPOSITION_LAYER_CUBE_EXTENSION layer type | 合并社区PR，添加了对 OpenXR 扩展 `XR_KHR_COMPOSITION_LAYER_CUBE` 图层类型的支持。 |
| 2026-04-02 | `85acc4bf` | [Backout] - CL52371899 | 回退了某个变更（CL52371899），可能是为了解决引入的问题或不兼容。 |

### 维护评价

XRBase 插件是 **活跃维护** 的。虽然它本身只是一个“功能容器”插件，不常有功能性大改，但近期提交（2026年4-5月）表明 Epic 团队仍在持续对其进行：
1.  **代码质量改进**（修复警告、迁移日志宏）。
2.  **功能集中与优化**（将分散的XR着色器、OpenXR扩展支持合并至此）。
3.  **问题修复**（回退有问题的变更）。
4.  作为其他具体XR插件（特别是OpenXR）的**基础依赖**，其稳定性至关重要。
推荐作为开发其他XR后端或集成高级XR功能的**基础依赖库**使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/XRBase)
- [官方文档]() (无)
- [测试用例]() (插件目录内未发现专属测试)