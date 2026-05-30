# PICO Controller

> This plugin provides support for XR_BD_controller_interaction and XR_BD_ultra_controller_interaction extensions.

| 属性 | 值 |
|---|---|
| 中文名 | PICO手柄交互 |
| 分类 | Virtual Reality |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PICOController` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2026-03-23 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/PICOController) | |

## 用途

这是一个为 PICO VR 头显的控制器（手柄）提供 OpenXR 底层支持的插件。它实现了 OpenXR 的 `XR_BD_controller_interaction` 和 `XR_BD_ultra_controller_interaction` 扩展，使得 Unreal Engine 能够正确识别和使用 PICO 手柄的按键布局、传感器和触觉反馈功能。简而言之，它解决的是在使用 OpenXR 标准时，PICO 特定手柄无法被引擎原生识别和配置的问题。

## 使用场景

-   当你为 **PICO VR 设备** 开发虚拟现实应用或游戏时，必须启用此插件以确保控制器功能（如按键映射、触觉反馈、追踪）正常工作。
-   当你需要创建一个支持多种 VR 头显（如 Meta Quest、Valve Index、PICO）的跨平台项目时，将此插件作为可选依赖，以便在 PICO 平台上启用其特定的控制器支持。
-   当你发现项目在 PICO 头显上运行时，手柄按键无响应或功能异常，应检查并启用此插件。

## 蓝图用法

此插件主要提供底层 OpenXR 扩展支持，不包含面向蓝图的公开节点（UFUNCTION）。其工作在引擎底层的输入系统中自动完成，为 PICO 控制器提供正确的交互配置文件（Interaction Profile），开发者无需在蓝图中直接操作。

## C++ 用法

### 头文件引入

```cpp
#include "PICOController.h"
```

### 基本用法

此插件主要通过实现 `IOpenXRExtensionPlugin` 接口来工作。对于大多数开发者而言，无需直接调用其 C++ API。以下是插件自身提供的接口函数，展示了它如何向 OpenXR 系统注册扩展：

**来源文件**: `Engine/Plugins/Runtime/PICOController/Source/PICOController/Private/PICOController.h`

```cpp
// 声明一个类继承自 IModuleInterface 和 IOpenXRExtensionPlugin
class FPICOControllerModule :
    public IModuleInterface,
    public IOpenXRExtensionPlugin
{
    // 向 OpenXR 实例声明必须启用的扩展
    virtual bool GetRequiredExtensions(TArray<const ANSICHAR*>& OutExtensions) override;

    // 向 OpenXR 实例声明可选启用的扩展
    virtual bool GetOptionalExtensions(TArray<const ANSICHAR*>& OutExtensions) override;

    // 向 OpenXR 子系统注册 PICO 控制器的交互配置文件
    virtual bool GetInteractionProfiles(XrInstance InInstance, TArray<FString>& OutKeyPrefixes, TArray<XrPath>& OutPaths, TArray<bool>& OutHasHaptics) override;
};
```

### 进阶用法

在开发需要与 OpenXR 扩展深度集成的自定义模块时，你可以依赖此插件，并在你的模块启动时检查其是否已加载。

## Demo 示例

以下示例展示了如何在你自己的运行时模块中，尝试获取 `PICOController` 模块的引用并查询其状态。

**头文件 (MyVRModule.h)**
```cpp
#pragma once

#include "Modules/ModuleManager.h"

class FMyVRModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

**源文件 (MyVRModule.cpp)**
```cpp
#include "MyVRModule.h"
#include "PICOController.h" // 包含 PICO 控制器插件头文件

#define LOCTEXT_NAMESPACE "FMyVRModule"

void FMyVRModule::StartupModule()
{
    // 尝试获取 PICO 控制器模块
    FPICOControllerModule* PICOControllerModule = FModuleManager::GetModulePtr<FPICOControllerModule>(TEXT("PICOController"));
    if (PICOControllerModule)
    {
        UE_LOG(LogTemp, Log, TEXT("PICO Controller 扩展已加载并可用。"));
        // 此处可以添加与 PICO 控制器交互的逻辑
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("PICO Controller 插件未启用，PICO 特定手柄功能将不可用。"));
    }
}

void FMyVRModule::ShutdownModule()
{
    // 清理工作
}

#undef LOCTEXT_NAMESPACE
```

## 模块依赖

要使你的项目或模块能够使用 PICO 控制器功能，你需要在 Build.cs 文件中依赖以下模块：

| 模块 | 用途 |
|---|---|
| `OpenXR` | 与 OpenXR 核心交互的基础，PICO 控制器插件作为其扩展 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-03-23 | `ea330405` | XR | Added PICO controller plugin which supports XR_BD_controller_interaction and XR_BD_ultra_controller_interaction extensions. Enabled the PICO Controller plugin and added PICO Controller Bindings to VR Template's Input Mapping Contexts. Removed Windows Mixed Reality Bindings. | 初始添加 PICO 控制器插件，支持其 OpenXR 扩展。默认在 VR 模板中启用并添加了输入绑定，同时移除了 WMR 的绑定。 |

### 维护评价

该插件**创建时间极新**（不足一年），目前仅有一次提交记录。它是由 PICO 官方创建并贡献给 Unreal Engine 的，作为其 VR 头显支持的一部分。由于是官方集成，且依赖于核心的 OpenXR 插件，其基础功能在引擎版本更新时通常会被同步维护。目前没有迹象表明它已被废弃。

**建议**：如果你的项目目标平台包含 PICO VR 设备，**建议启用此插件**。它提供了 PICO 控制器支持的标准官方实现，避免了自行集成 OpenXR 扩展的复杂性。由于其默认未启用（`EnabledByDefault=false`），你需要在项目的插件设置中手动启用它。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/PICOController)