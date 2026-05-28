# Game Input (Windows)

> GameInput is a next-generation input API that exposes input devices of all kinds through a single consistent interface.

| 属性 | 值 |
|---|---|
| 中文名 | GameInput Windows |
| 分类 | Input Devices |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GameInputWindows` (RuntimeNoCommandlet) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-11-11 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/GameInputWindows) | |

## 用途

`GameInputWindows` 是 `GameInput` 核心插件的 **Windows 平台实现模块**。它负责在 Windows 系统上，将微软的 GameInput API 集成到虚幻引擎的输入系统中。GameInput 是一个旨在统一处理手柄、方向盘、飞行摇杆等各类输入设备的现代化 API。该插件的主要作用是：当引擎运行在 Windows 平台时，通过 GameInput 协议来发现和管理游戏输入设备，从而为 Xbox 手柄等兼容设备提供原生、高性能且功能丰富的支持。

## 使用场景

-   你正在为 **Windows 平台**开发游戏，并需要支持 **Xbox 手柄**或其他兼容 GameInput 的游戏外设。
-   你的项目需要利用 GameInput API 提供的高级功能（例如更精细的触觉反馈、扳机振动等），而不仅仅是基础输入。
-   你希望在编辑器中也能使用这些设备进行测试和调试。

## 蓝图用法

此插件为运行时平台模块，不直接暴露蓝图节点。输入设备的连接、断开和读取将由引擎的输入系统自动管理，最终输入事件会通过标准的 Action/Axis 映射或 Enhanced Input 系统暴露给蓝图。

## C++ 用法

### 头文件引入

```cpp
#include "GameInputWindowsModule.h"
```

### 基本用法

该插件作为 `IInputDeviceModule` 的实现，通常由引擎输入系统在后台自动加载和使用。开发者可以直接查询其状态。

```cpp
// 检查 GameInput Windows 模块是否可用（已加载并成功初始化）
if (FGameInputWindowsModule::IsAvailable())
{
    // 模块可用，GameInput 设备将由引擎自动处理
    UE_LOG(LogTemp, Log, TEXT("GameInput Windows module is available."));
}

// 获取模块实例的引用（通常用于高级交互或调试）
FGameInputWindowsModule& GameInputModule = FGameInputWindowsModule::Get();
const TCHAR* APIStr = GameInputModule.GetPreferredDeviceAPIString();
UE_LOG(LogTemp, Log, TEXT("Preferred Device API: %s"), APIStr);
```

**来源**: `GameInputWindowsModule.h`

## Demo 示例

**GameInputWindowsDemo.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "GameInputWindowsDemo.generated.h"

UCLASS()
class AGameInputWindowsDemo : public AActor
{
    GENERATED_BODY()

public:
    void CheckGameInputStatus();
};
```

**GameInputWindowsDemo.cpp**
```cpp
#include "GameInputWindowsDemo.h"
#include "GameInputWindowsModule.h"

void AGameInputWindowsDemo::CheckGameInputStatus()
{
    // 检查 GameInput (Windows) 模块是否被加载并可用
    if (FGameInputWindowsModule::IsAvailable())
    {
        UE_LOG(LogTemp, Warning, TEXT("GameInputWindows is active and available on this Windows platform."));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("GameInputWindows module is not available. Check plugin enablement and platform."));
    }
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

**插件依赖**：该插件依赖于 `GameInput` 核心插件（已自动启用）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-02 | `a4559861` | UE_LOG -> UE_LOGF macro conversion for Game Input modules | 将日志宏从 UE_LOG 统一转换为 UE_LOGF |
| 2026-03-26 | `2cdca0c0` | [Input] FInputDeviceScope refactor and deprecation. | 重构并弃用了 FInputDeviceScope 输入设备作用域 |
| 2026-03-26 | `f6e9de5e` | [Game Input] Make the GameInput::HID device type a gamepad input device type by default. | 将 GameInput HID 设备默认识别为游戏手柄类型 |
| 2026-03-23 | `b22ef9f5` | [Input] Add a new FInputDeviceRegistry: | 输入系统新增 FInputDeviceRegistry 设备注册表 |
| 2026-03-20 | `7f95ae73` | [Game Input] Add default hardware device Id data for Windows targets | 为 Windows 平台添加默认的硬件设备 ID 数据 |

### 维护评价

`GameInputWindows` 是一个相对较新的插件（约1年历史），目前处于 **Beta** 实验性阶段。从提交历史看，维护**非常活跃**（最近一次更新在1个月内），并且改动多与核心输入系统重构和功能完善相关，表明它正处于积极开发和集成阶段。需要注意的是，它默认**未启用** (`EnabledByDefault: false`)，且明确为实验性功能，这意味着其 API 和行为可能在未来版本中发生变化。对于需要在 Windows 上使用最新 GameInput 特性的项目，可以谨慎评估使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/GameInputWindows)
- [官方文档](https://learn.microsoft.com/en-us/gaming/gdk/_content/gc/input/overviews/input-overview) （GameInput API 官方文档）