# Game Input (Windows)

> GameInput is a next-generation input API that exposes input devices of all kinds through a single consistent interface.

| 属性 | 值 |
|---|---|
| 中文名 | 游戏输入（Windows） |
| 分类 | Input Devices |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GameInputWindows` (RuntimeNoCommandlet) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-02-04 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GameInputWindows) | |

## 用途

GameInput 是微软推出的新一代输入 API，旨在统一键盘、鼠标、手柄、触摸、六轴传感器等多种设备的输入处理。该插件将 GameInput 集成到 UE5 的输入设备框架中，作为 `IInputDevice` 的 Windows 平台实现，让开发者能够通过 GameInput 接口获取输入数据，并与其他输入系统（如增强输入、传统输入）协同工作。

该插件解决了以下核心问题：
- 在 Windows 平台上使用原生 GameInput API 获取更底层、更高效的输入数据。
- 支持 GameInput 特有的功能（如设备热插拔、精确时间戳、高轮询率等），弥补 UE5 默认输入系统的局限性。
- 作为 GameInput 基础插件的平台桥接层，将低层 GameInput 句柄转换为 UE 可用的设备对象。

## 使用场景

- 你正在开发需要低延迟、高精度输入响应的竞技游戏或模拟类游戏。
- 你的游戏需要原生支持 Xbox 无线控制器、DualShock/DualSense 手柄的特殊特性（如扳机震动、LED 灯带等）。
- 你需要统一的 API 处理 Windows 上的各种输入源，并希望利用 GameInput 的跨设备特性。
- 你已经在项目中使用 `GameInput` 基础插件，并需要为 Windows 平台启用实际输入设备访问。

## 蓝图用法

此插件不直接暴露任何蓝图节点。所有功能在 C++ 层通过 `IInputDeviceModule` 接口实现。如果你的项目通过 `IInputDeviceModule` 注册了该输入设备，则输入数据会自动流向 `FGenericApplicationMessageHandler`，可以通过标准输入绑定（如 `InputAction`、`Enhanced Input`）消费。

| 节点 | 说明 | 所在类 |
|---|---|---|
| 无 | 该插件仅提供 C++ 模块，无蓝图可调用接口 | - |

## C++ 用法

### 头文件引入

```cpp
#include "GameInputWindowsModule.h"
#include "IGameInputDeviceInterface.h"
#include "GameInputDeviceContainer.h" // 来自 GameInput 基础插件
```

### 基本用法

1. **在项目模块的 Build.cs 中添加依赖**（已隐式包含 `GameInputWindows` 和 `GameInput`）。

2. **获取模块并获取输入设备指针**（通常在 `Subsystem` 或 `PlayerController` 中）：

```cpp
// 获取 GameInputWindows 模块
FGameInputWindowsModule& GameInputWindowsModule = FModuleManager::LoadModuleChecked<FGameInputWindowsModule>("GameInputWindows");

// 通过模块创建输入设备（通常由引擎自动调用）
TSharedPtr<IInputDevice> Device = GameInputWindowsModule.CreateInputDevice(MessageHandler);
```

3. **在自定义 `IInputDevice` 子类中重写 `Tick` 处理 GameInput 数据**（注意：此插件创建的设备已实现 `IGameInputDeviceInterface`，内部自动处理）：

```cpp
// 框架层重写示例（在 GameInputBase 模块中实现）
void FGameInputWindowsInputDevice::Tick(float DeltaTime)
{
    // 基类会自动轮询 GameInput API 并更新设备状态
    // Windows 实现会在此处调用 GameInputGetCurrentReading 等 API
}
```

### 进阶用法

**自定义设备数据处理**（通过继承基类接口）：
```cpp
class FMyGameInputDevice : public FGameInputWindowsInputDevice
{
public:
    FMyGameInputDevice(const TSharedRef<FGenericApplicationMessageHandler>& InMessageHandler, IGameInput* InGameInput)
        : FGameInputWindowsInputDevice(InMessageHandler, InGameInput) {}

protected:
    virtual void HandleDeviceDisconnected(IGameInputDevice* Device, uint64 Timestamp) override
    {
        // 处理设备断开事件（例如弹出提示）
        UE_LOG(LogTemp, Warning, TEXT("Device disconnected: %p"), Device);
        BaseClass::HandleDeviceDisconnected(Device, Timestamp);
    }

    virtual FGameInputDeviceContainer* CreateDeviceData(IGameInputDevice* InDevice) override
    {
        // 创建自定义的设备容器，可存储额外的设备信息
        auto* Container = new FGameInputDeviceContainer(InDevice);
        Container->SetAdditionalData(...);
        return Container;
    }
};
```

**在多平台项目中使用宏控制**：
```cpp
#if PLATFORM_WINDOWS
#include "GameInputWindowsModule.h"
#endif

void InitGameInput()
{
#if PLATFORM_WINDOWS && GAME_INPUT_SUPPORT
    // 仅 Windows 且启用 GameInput 时加载
    FModuleManager::Get().LoadModuleChecked("GameInputWindows");
#endif
}
```

## Demo 示例

以下是一个简单的 C++ 类，演示如何在 GameInstance 中启用并监听 GameInput 设备连接事件。

**MyGameInstance.h**:
```cpp
#pragma once

#include "Engine/GameInstance.h"
#include "MyGameInstance.generated.h"

UCLASS()
class UMyGameInstance : public UGameInstance
{
    GENERATED_BODY()

public:
    virtual void OnStart() override;
    virtual void Shutdown() override;

private:
    TSharedPtr<class IInputDevice> GameInputDevice;
};
```

**MyGameInstance.cpp**:
```cpp
#include "MyGameInstance.h"
#include "GameInputWindowsModule.h"
#include "IInputDevice.h"
#include "Framework/Application/SlateApplication.h"

void UMyGameInstance::OnStart()
{
    Super::OnStart();

    // 确保 GameInputWindows 模块已加载
    FModuleManager::LoadModuleChecked<FGameInputWindowsModule>("GameInputWindows");

    // 获取消息处理器（通常来自 Slate 应用）
    TSharedRef<FGenericApplicationMessageHandler> MessageHandler =
        FSlateApplication::Get().GetPlatformApplication()->GetMessageHandler();

    // 通过模块创建设备（模块内部会调用 CreateInputDevice）
    FGameInputWindowsModule& InputModule = FModuleManager::Get().GetModuleChecked<FGameInputWindowsModule>("GameInputWindows");
    GameInputDevice = InputModule.CreateInputDevice(MessageHandler);
}

void UMyGameInstance::Shutdown()
{
    GameInputDevice.Reset();
    Super::Shutdown();
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GameInput` | 提供 GameInput API 的基础包装（设备容器、接口定义、跨平台抽象） |
| `ApplicationCore` | 提供 `FGenericApplicationMessageHandler` 等输入管道基础设施 |

> **注意**：`GameInputWindows` 是 Windows 平台专用模块，仅在 `Win64` 平台编译和加载。依赖于 `GameInput` 模块，该模块通常是跨平台的基础实现。

## 维护状态

### 近期更新

- 2025-10-21 `19293ef2` — Grab the FGameInputBaseModule module earlier in FGameInputWindowsModule to ensure that it Initialize
- 2025-06-26 `569255eb` — [Game Input] Refactor so that the base implementation allows for different versions of Game Input
- 2025-06-20 `a9973077` — [Gmae Input] Clean up some headers
- 2025-03-24 `78bea3a8` — Build Health: fix unreachable code warning affecting builds.
- 2025-02-04 `5e51c06f` — [Game Input] Make creation of the game input device async on module startup for GameInput on windows

### 维护评价

该插件创建于 2025 年 2 月，目前仍处于实验性阶段（IsBetaVersion=true），但代码持续活跃更新。最近的提交涉及模块初始化顺序修复、重构以支持不同版本的 GameInput API，以及清理警告。这表明插件正在积极开发完善中，尚未完全稳定。

**推荐使用**：如果你需要在 Windows 上使用 GameInput API，且能接受实验性插件可能的接口变动，可以启用。对于仅需基本手柄支持的项目，建议优先使用标准输入系统；当需要 GameInput 专有特性（如高级触觉反馈、多设备统一管理）时再考虑此插件。

**注意事项**：
- 必须同时启用 `GameInput` 基础插件（默认启用否，需手动开启）。
- 仅支持 Windows 64 位平台。
- 实验性插件在后续引擎版本中可能发生破坏性变更。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GameInputWindows)
- [官方文档（GameInput 概述）](https://learn.microsoft.com/en-us/gaming/gameinput/)
- [GameInput 基础插件源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GameInput)
- [测试用例（GameInput 基础模块）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GameInput/Source/GameInputBase/Private/Tests)