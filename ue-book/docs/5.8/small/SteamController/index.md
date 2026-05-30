# Steam Controller Plugin

> InputDevice plugin for Steam controller（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | Steam 手柄 |
| 分类 | Input Devices |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SteamController` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2015-01-23 |
| 年龄标签 | 🏛️ 文物（约 10 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Steam/SteamController) | |

## 用途

该插件是一个运行时输入设备模块，用于将 Steam 手柄（Valve 的 Steam Controller）集成到 Unreal Engine 的输入系统中。它实现了 `IInputDeviceModule` 接口，使得引擎能够识别、初始化和管理 Steam 手柄，并将该手柄的独特输入（如触控板、背部按键、陀螺仪等）映射为引擎可用的输入事件。该插件的存在是为了让基于 UE 开发的游戏能原生支持 Steam 手柄，提升在 Steam 平台上运行的游戏体验。

## 使用场景

- 你正在 Steam 平台上发布一款游戏，并希望提供对 Steam 手柄的原生支持。
- 你的游戏需要利用 Steam 手柄特有的功能，如两个触控板、背部拨片或陀螺仪控制。
- 你希望统一不同手柄（包括 Steam 手柄）的输入处理逻辑，通过引擎的输入设备接口进行管理。

## 蓝图用法

该插件主要通过 C++ 的模块接口进行访问，在当前的源码分析中未发现暴露的 `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)` 接口。因此，它主要通过 C++ 进行集成和使用。

## C++ 用法

### 头文件引入

```cpp
#include "ISteamControllerPlugin.h"
```

### 基本用法

该插件的核心是提供一个可访问的模块接口。典型用法是先检查模块是否可用，然后获取其引用。

```cpp
// 来源：Engine/Plugins/Runtime/Steam/SteamController/Source/SteamController/Public/ISteamControllerPlugin.h
// 检查 Steam 手柄插件模块是否已加载并可用
if (ISteamControllerPlugin::IsAvailable())
{
    // 获取 Steam 手柄插件模块的引用
    ISteamControllerPlugin& SteamControllerModule = ISteamControllerPlugin::Get();

    // 通常，游戏代码会通过标准的输入接口（如 FInputDevice）来接收输入，
    // 而此模块在后台处理与 Steam API 的通信。
    // 引擎的输入设备管理器 (IInputInterface) 会自动发现并注册此模块提供的输入设备。
}
```

### 进阶用法

在更底层的框架集成中，你可能需要在初始化时确保 SteamController 模块被正确加载。例如，在某个游戏模块的 `StartupModule` 中可以尝试加载它。但请注意，该插件默认不启用，需要在项目设置或命令行中显式启用。

## Demo 示例

这是一个检查并获取 SteamController 模块的最小示例。

**MyClass.h**
```cpp
#pragma once

#include "CoreMinimal.h"

class FMyInputHandler
{
public:
    void Initialize();
    bool bIsSteamControllerSupported;
};
```

**MyClass.cpp**
```cpp
#include "MyClass.h"
#include "ISteamControllerPlugin.h" // 引入插件模块接口头文件

void FMyInputHandler::Initialize()
{
    // 检查 Steam Controller 模块是否可用
    if (ISteamControllerPlugin::IsAvailable())
    {
        // 获取模块单例，通常这里不会直接调用模块的函数，
        // 更多是确认输入系统已经集成了该设备。
        // ISteamControllerPlugin& ControllerPlugin = ISteamControllerPlugin::Get();
        bIsSteamControllerSupported = true;
        UE_LOG(LogTemp, Log, TEXT("Steam Controller Plugin is available and loaded."));
    }
    else
    {
        bIsSteamControllerSupported = false;
        UE_LOG(LogTemp, Warning, TEXT("Steam Controller Plugin is not available."));
    }
}
```

## 模块依赖

从 .uplugin 的 `Plugins` 字段和模块定义推断，使用该插件需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `SteamShared` | 提供共享的 Steam SDK 引用和基础功能 |

无其他特殊依赖（仅标准 Core/Engine 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧版 UE_LOG 宏迁移至新版 UE_LOGF 宏。 |
| 2026-03-26 | `2cdca0c0` | [Input] FInputDeviceScope refactor and deprecation. | 对输入设备作用域（FInputDeviceScope）进行重构并标记为废弃。 |
| 2025-06-03 | `0a44e4b8` | Plugin modules can be included & excluded on a per-architecture basis. | 插件模块现在可以按 CPU 架构（如 arm64）进行包含或排除。 |
| 2025-05-22 | `97f9ce7f` | Fix a race condition crash on shutdown of the SteamController plugin. | 修复了 SteamController 插件在关闭时因竞争条件导致的崩溃问题。 |
| 2023-03-06 | `0ac2dd67` | Add a EHardwareDeviceSupportedFeatures and EHardwareDevicePrimaryType enums to hardware device ident | 在硬件设备标识中添加了 EHardwareDeviceSupportedFeatures 和 EHardwareDevicePrimaryType 枚举。 |

### 维护评价

该插件自 2015 年创建，历史悠久。从 git 历史看，尽管更新频率不高，但在近期（2025-2026年）仍有实质性的维护活动，包括修复关键的崩溃问题、适配引擎框架的重构以及针对新平台架构的支持。这表明 Epic 仍在维护此插件以确保其与新版引擎兼容。考虑到其默认禁用且功能专一，属于**维护中**状态，可以放心使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Steam/SteamController)
- 官方文档：无
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Steam/SteamController/Tests)（如果存在）