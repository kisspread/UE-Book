# OpenXR

> OpenXR is an open VR/AR standard

| 属性 | 值 |
|---|---|
| 中文名 | OpenXR接口 |
| 分类 | Virtual Reality |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（VR/AR标准资产） |
| 模块 | `OpenXRHMD` (Runtime), `OpenXRInput` (Runtime), `OpenXRAR` (Runtime), `OpenXREditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2019-04-16 |
| 年龄标签 | 🏛️ 文物（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/OpenXR) | |

## 用途

OpenXR 插件是 Unreal Engine 对 Khronos Group 制定的 OpenXR 开放标准的官方实现。它的核心目的是为开发者提供一个统一、跨平台的 API，用于开发虚拟现实（VR）和增强现实（AR）应用。通过这个标准接口，开发者无需为每个 XR 头显设备（如 Meta Quest、Valve Index、HTC Vive 等）或平台（如 PC、Android）编写特定的设备驱动代码。它解决了 XR 生态系统碎片化的问题，使得同一套代码能够在兼容 OpenXR 的所有设备上运行。

## 使用场景

-   你正在开发一款需要支持多个品牌 VR 头显的沉浸式游戏。
-   你的 AR 应用需要兼容不同厂商的 AR 眼镜和手机平台。
-   你想使用 Unreal Engine 内置的 VR 模板或 AR 功能，并希望确保最广泛的设备兼容性。
-   你需要集成第三方开发的 OpenXR 扩展（Extensions）来实现特殊功能。

## 蓝图用法

OpenXR 的核心功能通过蓝图类暴露，主要分布在 `OpenXRHMD` 和 `OpenXRInput` 模块中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get OpenXR System` | 获取当前的 OpenXR 系统实例。 | `UOpenXRHMDLibrary` |
| `Is OpenXR Enabled` | 检查当前会话是否使用了 OpenXR。 | `UOpenXRHMDLibrary` |
| `Get OpenXR Reference Spaces` | 获取设备支持的参考空间类型列表（如 Local, Stage）。 | `UOpenXRHMDLibrary` |
| `Create OpenXR Reference Space` | 创建一个 OpenXR 参考空间。 | `UOpenXRHMDLibrary` |
| `Get OpenXR Action Sets` | 获取当前激活的 Action Set 列表。 | `UOpenXRInputLibrary` |
| `Create OpenXR Action` | 创建一个输入动作（如按键、摇杆）。 | `UOpenXRInputLibrary` |

### 使用示例（蓝图描述）

一个典型的蓝图工作流是：
1.  游戏启动时，使用 `Get OpenXR System` 节点检查 OpenXR 系统是否成功初始化。
2.  使用 `Get OpenXR Reference Spaces` 检查设备支持的空间模式，并根据需要 `Create OpenXR Reference Space` 来定义追踪原点。
3.  在 `Project Settings` 或通过蓝图 `Create OpenXR Action` 和 `Create OpenXR Action Set` 来定义你的输入动作（如“开火”、“移动”），并将这些 Action 绑定到具体的硬件控制器输入源。
4.  在游戏逻辑中，通过 Enhanced Input 系统（OpenXR 与之深度集成）来查询这些 Action 的状态。

## C++ 用法

### 头文件引入

```cpp
#include "OpenXRCore.h"
#include "OpenXRHMD.h"
#include "OpenXRInput.h"
```

### 基本用法

从测试用例和模块核心代码中提取的用法示例。
```cpp
// 来源: Engine/Plugins/Runtime/OpenXR/Source/OpenXRHMD/Private/OpenXRHMD.cpp 及相关测试
// 检查当前的 HMD 插件是否是 OpenXR
if (GEngine && GEngine->XRSystem.IsValid())
{
    if (FHeadMountedDisplay* HMD = GEngine->XRSystem.Get())
    {
        if (HMD->GetSystemName() == TEXT("OpenXR"))
        {
            // 我们正在使用 OpenXR
            // 可以进一步获取 OpenXR 特定接口
            IOpenXRHMDPlugin* OpenXRHMDPlugin = &FOpenXRHMDPlugin::Get();
            // ... 获取设备信息，管理会话等
        }
    }
}

// 通过 OpenXR 核心模块获取运行时信息
XrInstance Instance = FOpenXRCoreModule::Get().GetInstance();
XrSystemId SystemId = FOpenXRCoreModule::Get().GetSystemId();
```

### 进阶用法

与 OpenXR 输入系统和增强输入系统交互。
```cpp
// 来源: Engine/Plugins/Runtime/OpenXR/Source/OpenXRInput/Private/OpenXRInput.cpp
// 直接操作 OpenXR Action
XrActionSet ActionSet = ...; // 已创建的 ActionSet
XrAction Action = ...; // 已创建的 Action

// 获取动作的当前状态
XrActionStateGetInfo GetInfo = { XR_TYPE_ACTION_STATE_GET_INFO };
GetInfo.action = Action;
GetInfo.subactionPath = XR_NULL_PATH; // 或指定子动作路径

XrActionStateFloat State = { XR_TYPE_ACTION_STATE_FLOAT };
if (XR_UNQUALIFIED_SUCCESS(xrGetActionStateFloat(Session, &GetInfo, &State)))
{
    if (State.isActive)
    {
        float TriggerValue = State.currentState;
        // 使用触发器数值...
    }
}
```

## Demo 示例

一个最小化的 C++ 示例，用于连接 OpenXR 系统并查询基础信息。
```cpp
// MyOpenXRDemo.h
#pragma once
#include "CoreMinimal.h"

class FMyOpenXRDemo
{
public:
    static void Initialize();
    static void PrintOpenXRSystemInfo();
};

// MyOpenXRDemo.cpp
#include "MyOpenXRDemo.h"
#include "OpenXRCore.h"
#include "IOpenXRHMDModule.h"

void FMyOpenXRDemo::Initialize()
{
    // OpenXR 系统通常在引擎启动早期由 HMD 模块自动初始化。
    // 此处可以放置需要在 OpenXR 就绪后运行的逻辑。
    PrintOpenXRSystemInfo();
}

void FMyOpenXRDemo::PrintOpenXRSystemInfo()
{
    // 确保 OpenXR 模块已加载
    if (!IOpenXRHMDModule::IsAvailable())
    {
        UE_LOG(LogTemp, Warning, TEXT("OpenXR HMD Module not available."));
        return;
    }

    IOpenXRHMDModule& OpenXRModule = IOpenXRHMDModule::Get();
    if (XrInstance Instance = OpenXRModule.GetInstance())
    {
        // 通过 Instance 可以查询 OpenXR 扩展、系统属性等
        UE_LOG(LogTemp, Log, TEXT("OpenXR Instance is valid."));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("OpenXR Instance is not valid. The runtime may not be installed."));
    }
}
```

## 模块依赖

你的项目模块如果依赖此插件，需要在 `Build.cs` 文件中添加以下模块：

| 模块 | 用途 |
|---|---|
| `XRBase` | UE XR 系统的基础抽象层，OpenXR 构建于其上。 |
| `EnhancedInput` | OpenXR 输入系统与增强输入系统深度集成，用于处理和映射控制器输入。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `0421053e` | [OpenXR][Vulkan] Request TRANSFER_DST_BIT for XR render target swapchains | 为 Vulkan 后端的 XR 渲染目标交换链添加了 TRANSFER_DST_BIT 使用标志。 |
| 2026-05-14 | `a57c6062` | Stereolayers with Supports Depth wobble: prevent dangling next-chain pointers in CompositionDepthTest | 修复了支持深度的立体层在深度测试组合时可能导致的悬空指针问题。 |
| 2026-04-30 | `da4fc827` | PR #14037: Fix no audio when xrGetAudioOutputDeviceGuidOculus returns failure | 修复了当 Oculus 的 xrGetAudioOutputDeviceGuidOculus 调用失败时可能导致的无音频问题。 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复了在格式化函数中使用作用域枚举可能导致输出垃圾字符的问题。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了格式化说明符与参数位宽不匹配（32位 vs 64位）可能导致的问题。 |

### 维护评价

OpenXR 插件作为 UE 官方对重要行业标准的实现，维护非常活跃。从提交历史看，最近一年内持续有功能优化、Bug 修复和平台兼容性更新，特别是针对 Vulkan 渲染后端、立体层渲染和 Oculus 等特定设备的音频集成。尽管该插件默认未启用（需要用户在插件列表中手动开启），但它已经从一个实验性插件成长为稳定、核心的 XR 支持组件。**推荐在所有涉及 VR/AR 开发的项目中使用此插件**，以获得最佳的跨平台兼容性和官方支持。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/OpenXR)
- [OpenXR 官方规范](https://www.khronos.org/openxr/) (Khronos Group)