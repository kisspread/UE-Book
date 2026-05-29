# OpenXR

> OpenXR is an open VR/AR standard（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 开放XR |
| 分类 | Virtual Reality |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（XR基础资产） |
| 模块 | `OpenXRHMD` (Runtime), `OpenXRInput` (Runtime), `OpenXRAR` (Runtime), `OpenXREditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2019-04-16 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/OpenXR) | |

## 用途
该插件为 Unreal Engine 提供了符合 OpenXR 标准的 XR（扩展现实）运行时支持。它解决了跨平台 VR/AR 开发的标准化问题，使开发者能够通过统一的 OpenXR API 来访问不同的 XR 硬件（如 Meta Quest、HTC Vive、Valve Index、Windows Mixed Reality 等），而无需为每个设备编写特定的代码。其核心是实现了一个 HMD（头戴式显示器）驱动，并集成了输入和 AR 子系统。

## 使用场景
- 你正在开发一个需要兼容多种 VR 头显的跨平台游戏或应用 → 使用 OpenXR 作为统一的 HMD 驱动。
- 你需要为 VR 体验集成 AR 功能（如透视、平面检测） → 使用 OpenXRAR 模块。
- 你希望使用现代的、标准化的输入系统来处理 XR 控制器输入 → 使用 OpenXRInput 模块，并与 EnhancedInput 插件集成。

## 蓝图用法
由于 OpenXR 主要通过引擎内部的 `IXRTrackingSystem` 接口工作，其直接暴露的蓝图节点相对较少，更多功能隐藏在引擎底层。以下是核心的、开发者可直接使用或影响的蓝图节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get HMD Device Name` | 获取当前连接的 HMD 设备名称 | `UOpenXRHMDFunctionLibrary` (或通用 `UHeadMountedDisplayFunctionLibrary`) |
| `Get XR Tracking Origin` | 获取当前的 XR 追踪原点类型 | `UOpenXRHMDFunctionLibrary` |
| `Set XR Tracking Origin` | 设置 XR 追踪原点类型 | `UOpenXRHMDFunctionLibrary` |
| `Get Motion Controller Data` | 获取特定控制器的追踪数据（位置、旋转） | 通用 `UHeadMountedDisplayFunctionLibrary` |

**说明**：OpenXR 的很多强大功能（如交换链管理、合成层、性能设置）主要通过 C++ API 和控制台命令暴露。蓝图中更常用的是引擎标准的 HMD 功能库函数，OpenXR 插件是这些函数的底层实现之一。

## C++ 用法

### 头文件引入
```cpp
#include "OpenXRHMD.h"
#include "IOpenXRARModule.h"
// 根据需要引入特定模块的头文件
```

### 基本用法
**场景**：在运行时检查当前是否使用 OpenXR 驱动，并获取一些基本信息。
```cpp
// (来自通用 XR 用法示例，适用于 OpenXR 实现)
#include "HeadMountedDisplayFunctionLibrary.h"
#include "IXRTrackingSystem.h"

// 检查 HMD 是否连接并正在使用
if (GEngine && GEngine->XRSystem.IsValid())
{
    // 获取设备名称，对于 OpenXR，这可能返回 “OpenXR”
    FString DeviceName = GEngine->XRSystem->GetSystemName();
    UE_LOG(LogTemp, Log, TEXT("XR System: %s"), *DeviceName);

    // 获取追踪原点
    ETrackingStatus TrackingStatus;
    FVector Position;
    FRotator Rotation;
    UHeadMountedDisplayFunctionLibrary::GetTrackingSensorParameters(Position, Rotation, 0, TrackingStatus);
}
```

### 进阶用法
**场景**：使用 OpenXRAR 模块访问 AR 特性（如透视）。
```cpp
#include "IOpenXRARModule.h"

// 确保 AR 模块已加载
IOpenXRARModule* OpenXRARModule = FModuleManager::GetModulePtr<IOpenXRARModule>("OpenXRAR");
if (OpenXRARModule)
{
    // 检查是否支持透视（Passthrough）功能
    bool bSupportsPassthrough = OpenXRARModule->IsPassthroughSupported();
    if (bSupportsPassthrough)
    {
        // 启用或禁用透视层
        OpenXRARModule->EnablePassthrough(true);
    }
}
```

## Demo 示例
一个最小的、展示如何在代码中感知 OpenXR 系统存在的示例。

**MyXRHelper.h**
```cpp
#pragma once

#include "CoreMinimal.h"

class FMyXRHelper
{
public:
    // 检查 OpenXR 是否为当前活跃的 XR 系统
    static bool IsActiveOpenXRSystem();
};
```

**MyXRHelper.cpp**
```cpp
#include "MyXRHelper.h"
#include "Engine/Engine.h"

bool FMyXRHelper::IsActiveOpenXRSystem()
{
    if (GEngine && GEngine->XRSystem.IsValid())
    {
        // GetSystemName 返回插件提供的系统名称，OpenXR HMD 模块通常返回 “OpenXR”
        return GEngine->XRSystem->GetSystemName() == TEXT("OpenXR");
    }
    return false;
}
```

## 模块依赖
使用此插件，你的模块可能需要以下依赖（根据具体功能）：

| 模块 | 用途 |
|---|---|
| `EnhancedInput` | 用于处理 OpenXR 控制器输入，将其映射到增强输入动作 |
| `HeadMountedDisplay` | XR 功能的核心接口模块 |
| `AugmentedReality` | 使用 OpenXRAR 模块提供的 AR 功能时需要 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `0421053e` | [OpenXR][Vulkan] Request TRANSFER_DST_BIT for XR render target swapchains | 修复 Vulkan 渲染后端下，XR 渲染目标交换链的格式兼容性问题 |
| 2026-05-14 | `a57c6062` | Stereolayers with Supports Depth wobble: prevent dangling next-chain pointers in CompositionDepthTes | 修复立体层深度测试中可能导致的指针悬挂（野指针）问题 |
| 2026-04-30 | `da4fc827` | PR #14037: Fix no audio when xrGetAudioOutputDeviceGuidOculus returns failure | 修复在 Oculus OpenXR 运行时音频设备枚举失败时，可能导致无声音输出的问题 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复在日志格式化输出中使用特定枚举类型可能导致的乱码问题 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复日志格式化中 32 位与 64 位格式说明符不匹配导致的打印错误 |

### 维护评价
- **活跃维护**：该插件自 2019 年创建以来一直持续更新，最近一次更新在 2026 年 5 月，更新频率非常高。
- **维护重点**：近期提交主要集中在修复各种平台（特别是 Vulkan）和硬件（如 Oculus）的兼容性问题、运行时稳定性问题（如野指针）以及日志/诊断改进。
- **状态**：作为 Epic Games 官方维护的 XR 核心插件之一，它是 UE5 XR 开发的基石，维护状态非常积极，推荐作为 VR/AR 项目的首选运行时。
- **注意**：插件默认未启用 (`EnabledByDefault: false`)，需要在项目设置中手动启用。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/OpenXR)
- [官方文档]()（.uplugin 中未提供，通常在 Epic 官方文档站有独立章节）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/Source/EngineTests/XR)（引擎级 XR 测试可能包含 OpenXR 相关）