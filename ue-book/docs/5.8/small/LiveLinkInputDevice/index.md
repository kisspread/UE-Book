# LiveLinkInputDevice

> Live Link plugin for Unreal Engine Input Devices, i.e. Game Controllers. It uses the InputDevice system to query values and share state over LiveLink.

| 属性 | 值 |
|---|---|
| 中文名 | 输入设备LiveLink源 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（UI资产、Slate控件） |
| 模块 | `LiveLinkInputDevice` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-16 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LiveLinkInputDevice) | |

## 用途

本插件将游戏手柄（Gamepad）的输入状态通过 Live Link 协议广播出去，使得其他系统（如 Control Rig、动画蓝图、Live Link Hub）可以实时读取手柄的摇杆轴值和按钮状态。

**核心机制**：插件启动一个独立轮询线程，以 100Hz 频率读取 XInput 手柄的轴值和按键状态，封装为 LiveLink 帧数据后发送给 LiveLink Client。每个已连接的手柄被映射为一个 LiveLink Subject。

**为什么需要它**：标准的 UE 输入系统只能在游戏线程中处理输入，且需要经过 Input Mapping 的抽象层。本插件绕过这些限制，直接从底层 IInputDevice 接口读取原始数据，使外部程序（如 LiveLinkHub）无需运行完整游戏也能获取手柄输入，特别适合虚拟制片和动捕录制场景。

**当前限制**：仅支持 Win64 平台的 XInput 手柄（Xbox 手柄等），仅在 LiveLinkHub 程序中可用。

## 使用场景

- 你在做虚拟制片，需要用手柄实时驱动 Control Rig 中的虚拟摄像机或角色
- 你在使用 LiveLinkHub 录制动画，需要同步记录手柄输入作为参考数据
- 你需要从另一个应用程序（非游戏进程）获取手柄状态，用于外部控制或数据采集
- 你想把手柄输入作为 LiveLink Subject 发送给多个下游消费者

## 蓝图用法

本插件是纯 Runtime 的 LiveLink Source，不暴露任何 `BlueprintCallable` 函数或 `BlueprintReadWrite` 属性。所有交互通过 Live Link 面板完成。

### Live Link 面板操作

1. 打开 Live Link 面板（窗口 → Live Link）
2. 点击 **Add Source** → 选择 **Input Device**
3. 确认连接设置后，已连接的手柄会自动显示为 Subject
4. 每个 Subject 包含手柄的摇杆轴值和按钮状态

### 数据结构

每个手柄 Subject 发送 `FLiveLinkGamepadInputDeviceFrameData` 帧数据，包含：
- 左/右摇杆的 X、Y 轴值
- 左/右扳机的模拟值
- 所有按钮的按下/释放状态

## C++ 用法

### 头文件引入

```cpp
#include "LiveLinkInputDevice.h"
#include "LiveLinkInputDeviceSource.h"
#include "LiveLinkInputDeviceMessageHandler.h"
```

### 基本用法

通过代码手动创建 LiveLink Input Device Source：

```cpp
// 来源: LiveLinkInputDeviceSourceFactory.cpp
#include "LiveLinkInputDeviceSource.h"
#include "LiveLinkInputDeviceConnectionSettings.h"
#include "ILiveLinkClient.h"

// 创建连接设置
FLiveLinkInputDeviceConnectionSettings ConnectionSettings;

// 创建 Source 实例
TSharedPtr<FLiveLinkInputDeviceSource> Source = MakeShared<FLiveLinkInputDeviceSource>(ConnectionSettings);

// Source 内部会自动启动轮询线程
// 在 ReceiveClient 被调用后开始向 LiveLink Client 发送数据
```

### 进阶用法

自定义消息处理器获取手柄数据（无需 LiveLink）：

```cpp
// 来源: LiveLinkInputDeviceMessageHandler.h
#include "LiveLinkInputDeviceMessageHandler.h"

// 创建消息处理器来直接捕获手柄输入
FLiveLinkInputDeviceMessageHandler Handler;

// 模拟手柄输入回调（通常由 IInputDevice 内部调用）
Handler.OnControllerAnalog(FGamepadKeyNames::LeftStickX, PlatformUserId, InputDeviceId, 0.5f);
Handler.OnControllerButtonPressed(FGamepadKeyNames::FaceButtonBottom, PlatformUserId, InputDeviceId, false);

// 获取指定设备的最新帧数据
FLiveLinkGamepadInputDeviceFrameData FrameData = Handler.GetLatestValue(InputDeviceId);

// 获取所有已知设备 ID
TSet<FInputDeviceId> DeviceIds = Handler.GetDeviceIds();
```

## Demo 示例

一个通过代码创建 LiveLink Input Device Source 的最小示例：

```cpp
// MyLiveLinkInputDeviceManager.h
#pragma once

#include "CoreMinimal.h"

class ILiveLinkClient;
class FLiveLinkInputDeviceSource;

class FMyLiveLinkInputDeviceManager
{
public:
    void Initialize(ILiveLinkClient* InClient, const FGuid& InSourceGuid);
    void Shutdown();

private:
    TSharedPtr<FLiveLinkInputDeviceSource> InputDeviceSource;
};
```

```cpp
// MyLiveLinkInputDeviceManager.cpp
#include "MyLiveLinkInputDeviceManager.h"
#include "LiveLinkInputDeviceSource.h"
#include "LiveLinkInputDeviceConnectionSettings.h"
#include "ILiveLinkClient.h"

void FMyLiveLinkInputDeviceManager::Initialize(ILiveLinkClient* InClient, const FGuid& InSourceGuid)
{
    FLiveLinkInputDeviceConnectionSettings ConnectionSettings;
    
    InputDeviceSource = MakeShared<FLiveLinkInputDeviceSource>(ConnectionSettings);
    
    // 将 Source 注册到 LiveLink Client
    // Source 内部会启动轮询线程，以 100Hz 读取手柄数据
    // 每个检测到的手柄会自动注册为 LiveLink Subject
    InClient->ReceiveSource(InputDeviceSource, InSourceGuid);
}

void FMyLiveLinkInputDeviceManager::Shutdown()
{
    // 调用 RequestSourceShutdown 会通知线程停止
    if (InputDeviceSource.IsValid())
    {
        InputDeviceSource->RequestSourceShutdown();
        InputDeviceSource.Reset();
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LiveLink` (插件依赖) | 提供 ILiveLinkSource、ILiveLinkClient 等核心 LiveLink 接口 |

无特殊模块依赖（仅标准 Core/Engine/Slate 等）。主要依赖通过插件声明中的 LiveLink 插件依赖提供。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-02-03 | `88ba268b` | Fix unreachable code errors | 修复不可达代码编译错误 |
| 2025-05-30 | `d8d2374e` | LiveLink - Convert "Add Source" menu to pop up a modal window instead of a dropdown menu | LiveLink 添加源菜单改为弹窗模式 |
| 2024-06-18 | `06395cb7` | Add SceneTime to the frame data of LiveLinkInputDevice. This missing information was preventing input recording from being useful. | 帧数据中补充 SceneTime，修复录制数据缺失时间信息的问题 |
| 2024-06-04 | `a67aedfe` | Use IPlatformInputDeviceMapper::Get().GetOnInputDeviceConnectionChange() to detect game pad changes | 改用手柄连接变化的平台级回调检测设备插拔 |
| 2024-01-30 | `0c7f26bc` | Move input device type to accommodate accessing input device data from the Live Link Control Rig plugin | 调整输入设备类型定义以支持 Control Rig 插件读取数据 |

### 维护评价

- **创建时间**：2024 年 1 月，是一个较新的插件
- **更新频率**：约每 2-5 个月有一次更新，频率较低但持续维护中
- **状态**：仍在活跃维护，最近一次更新在 2026 年 2 月修复编译问题
- **限制**：Beta 状态，仅支持 Win64 平台的 XInput 手柄，仅限 LiveLinkHub 程序使用
- **推荐**：适合在虚拟制片/动捕场景中使用，但需注意其 Beta 状态和平台限制。如果你需要把手柄输入接入 LiveLink 生态系统，这是目前唯一的官方方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LiveLinkInputDevice)
- [Live Link 插件文档](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/LiveLink)