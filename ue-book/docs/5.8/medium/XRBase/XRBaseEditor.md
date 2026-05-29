# XRBase

> XR Base Feature Implementations.  (Generally this plugin will be automatically enabled by another plugin that requires it.)

| 属性 | 值 |
|---|---|
| 中文名 | XR基础库 |
| 分类 | Virtual Reality |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `XRBase` (Runtime), `XRBaseEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2023-04-10 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/XRBase) | |

## 用途

**XRBase** 插件的核心目的是解决 UE5 引擎的模块化与按需加载问题。在 UE5 之前，所有与 VR/AR 相关的设备管理、输入处理、渲染支持等基础功能都紧密地集成在引擎的核心运行时模块（如 `HeadMountedDisplay`）中。这导致即使是最简单的非 XR 项目，也必须加载这些 XR 功能模块，增加了主程序的体积和内存开销。

此插件将这些 **XR 基础功能** 从引擎核心中剥离出来，封装成一个独立的运行时插件。它的存在是为了被其他更具体的 XR 插件（如 `OpenXR`）所依赖，从而实现 XR 功能的按需加载和更好的代码组织。它本身并不直接面向最终开发者，而是作为构建上层 XR 功能的基石。

## 使用场景

- **XR 插件开发者**：如果你正在开发一个新的 XR 平台插件（例如针对某个特定的 VR 头显），你的插件需要依赖 `XRBase` 来获取基础的设备抽象、事件系统和组件接口。
- **引擎定制与优化**：当构建一个不包含 VR 功能的轻量级版本时，可以安全地禁用或排除 `XRBase` 插件，从而进一步减小引擎体积。
- **需要深度定制 XR 交互或渲染管线的开发者**：在 `XRBase` 提供的基础框架上，你可以扩展或替换其默认行为。

## 蓝图用法

`XRBase` 插件主要作为底层库，其提供的蓝图可调用函数有限，更多是服务于上层插件（如 `OpenXR`）。核心节点可能包含一些全局的 XR 设备查询或事件绑定。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get XR System` | 获取当前 XR 子系统的实例（如 `IXRTrackingSystem`）。 | `UHeadMountedDisplayFunctionLibrary` (推断) |
| `Get HMD Device Name` | 获取当前连接的头戴设备名称。 | `UHeadMountedDisplayFunctionLibrary` (推断) |

*注：由于 `XRBase` 的公共头文件未在本次分析中提供，上表节点根据 XR 功能典型用法推断。*

### 使用示例（蓝图描述）

通常，你不需要在自己的蓝图中直接使用 `XRBase` 的节点。它们会被 `OpenXR` 等插件的节点在内部调用。例如，当你使用 `OpenXR` 插件的 “Start XR Session” 节点时，它底层会通过 `XRBase` 提供的接口来初始化 XR 系统。

## C++ 用法

`XRBase` 提供了 XR 系统的核心抽象接口和基础组件，是构建 XR 功能的起点。

### 头文件引入

```cpp
#include "XRBase.h" // 核心模块头文件
#include "HeadMountedDisplay.h" // 可能包含 HMD 相关的基础类型
```

### 基本用法

访问 XR 子系统并查询设备信息。

```cpp
// 来源：典型 XR 系统用法，基于 XRBase 提供的接口
#include "XRBase.h"
#include "HeadMountedDisplay.h"

void AXRActor::BeginPlay()
{
    Super::BeginPlay();

    // 获取 XR 追踪系统接口
    IXRTrackingSystem* XRSystem = GEngine->XRSystem.Get();
    if (XRSystem)
    {
        UE_LOG(LogTemp, Log, TEXT("XR System Found: %s"), *XRSystem->GetSystemName().ToString());

        // 查询头戴设备信息
        FString HMDDeviceName;
        if (GEngine->HMDDevice.IsValid())
        {
            HMDDeviceName = GEngine->HMDDevice->GetDeviceName();
            UE_LOG(LogTemp, Log, TEXT("HMD Device: %s"), *HMDDeviceName);
        }
    }
}
```

### 进阶用法

监听 XR 设备连接/断开事件。`XRBase` 模块可能定义了用于广播此类事件的委托。

```cpp
// 来源：基于事件驱动的 XR 设备管理
#include "XRBase.h"

DECLARE_DELEGATE_OneParam(FOnXRDeviceConnectionChanged, bool /*bIsConnected*/);

class FMyXRDeviceManager
{
public:
    FMyXRDeviceManager()
    {
        // 绑定到 XRBase 可能暴露的全局设备变更委托
        // FHeadMountedDisplayModule::Get().OnDeviceConnectionChanged.AddRaw(this, &FMyXRDeviceManager::HandleDeviceChanged);
    }

    void HandleDeviceChanged(bool bIsConnected)
    {
        UE_LOG(LogTemp, Warning, TEXT("XR Device %s."), bIsConnected ? TEXT("Connected") : TEXT("Disconnected"));
        // 执行自定义逻辑，如启用/禁用输入、更新UI等
    }
};
```

## Demo 示例

一个简单的 C++ Actor，用于监控 XR 设备状态并输出日志。

**XRDeviceMonitor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "XRDeviceMonitor.generated.h"

UCLASS()
class AXRDeviceMonitor : public AActor
{
    GENERATED_BODY()

public:
    AXRDeviceMonitor();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    // 处理设备连接状态变化的回调（示例签名）
    void OnDeviceStatusChanged(bool bIsConnected);

    // 存储绑定句柄，用于解绑
    FDelegateHandle DeviceChangedHandle;
};
```

**XRDeviceMonitor.cpp**
```cpp
#include "XRDeviceMonitor.h"
#include "XRBase.h" // 引入 XRBase 模块
#include "HeadMountedDisplay.h"

AXRDeviceMonitor::AXRDeviceMonitor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AXRDeviceMonitor::BeginPlay()
{
    Super::BeginPlay();

    // 订阅设备变更事件 (具体的委托名称和签名需参考 XRBase 源码)
    // 示例：假设存在一个全局委托 FHeadMountedDisplayModule::DeviceConnectionChanged
    // DeviceChangedHandle = FHeadMountedDisplayModule::Get().DeviceConnectionChanged.AddUObject(this, &AXRDeviceMonitor::OnDeviceStatusChanged);

    UE_LOG(LogTemp, Log, TEXT("XRDeviceMonitor: Actor started, listening for device changes."));
}

void AXRDeviceMonitor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    // 解绑事件
    if (DeviceChangedHandle.IsValid())
    {
        // FHeadMountedDisplayModule::Get().DeviceConnectionChanged.Remove(DeviceChangedHandle);
    }

    Super::EndPlay(EndPlayReason);
}

void AXRDeviceMonitor::OnDeviceStatusChanged(bool bIsConnected)
{
    if (bIsConnected)
    {
        UE_LOG(LogTemp, Log, TEXT("XR Device has been connected!"));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("XR Device has been disconnected!"));
    }
}
```

## 模块依赖

*由于未提供 `XRBase.Build.cs` 文件，以下为基于典型 XR 插件的推断依赖。*

| 模块 | 用途 |
|---|---|
| `OpenXR` 或其他XR运行时 | 可能作为其具体实现依赖（可选） |
| `RenderCore`, `RHI` | 用于 XR 渲染相关的底层支持 |
| `HeadMountedDisplay` (可能被合并) | 历史遗留或过渡期依赖，最终可能被本模块取代 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下双精度常量转换为浮点数产生警告的代码。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将UE_LOG宏迁移到UE_LOGF。 |
| 2026-04-08 | `01e78a0b` | Moving open xr shaders to XR base | 将OpenXR的着色器移动到XRBase插件中。 |
| 2026-04-03 | `22c896f3` | PR #13335: Add OpenXR XR_KHR_COMPOSITION_LAYER_CUBE_EXTENSION layer type | 新增对OpenXR立方体合成层扩展的支持。 |
| 2026-04-02 | `85acc4bf` | [Backout] - CL52371899 | 回滚了CL52371899的改动。 |

### 维护评价

**XRBase** 是一个相对年轻且非常活跃的基础插件。从 git 历史看，Epic 团队正在积极地将引擎核心的 XR 相关功能迁移到此插件中（如移动着色器），并在此基础上进行新功能的开发（如添加新的 OpenXR 图层类型）。近期更新集中在代码清理（迁移日志宏、修复编译警告）和功能扩展上，表明该插件处于**核心构建阶段**，并持续得到优化和增强。

它是未来 UE5 XR 功能模块化架构的关键组成部分，**强烈建议关注并学习其设计模式**。由于它主要作为依赖库被其他插件使用，直接使用它的场景不多，但其稳定性和演进方向对整个 XR 生态至关重要。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/XRBase)
- 官方文档：暂无（.uplugin `DocsURL` 为空）
- 测试用例：暂未在提供的路径中发现独立测试文件，可能集成在其他XR相关测试中或位于 `Engine/Tests/` 下。