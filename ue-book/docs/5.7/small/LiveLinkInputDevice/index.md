# LiveLinkInputDevice

> Live Link plugin for Unreal Engine Input Devices, i.e. Game Controllers. It uses the InputDevice system to query values and share state over LiveLink.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | false |
| 包含内容 | true |
| 模块 | LiveLinkInputDevice (Runtime) |
| 创建时间 | 2024-01-16 |
| 年龄标签 | 🆕 (≤5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/LiveLinkInputDevice) | |

## 用途

将 UE 的 InputDevice 系统（主要是游戏手柄/控制器）的输入数据通过 Live Link 协议广播出去。它在一个独立线程上以 100Hz 频率轮询所有已连接的手柄，将摇杆轴、扳机、按钮、方向键等输入值实时推送到 Live Link，供其他系统（如 Take Recorder 录制、动画驱动等）消费。

与直接在游戏中读取输入不同，这个 plugin 绕过了 Game Input Device Subsystem，可以在 **Live Link Hub** 中独立运行，用于录制和驱动目的。

## 重要限制

- **仅限 LiveLinkHub**：`SupportedPrograms` 和 `ProgramAllowList` 均为 `["LiveLinkHub"]`，不会在普通编辑器或游戏中加载
- **仅限 Win64**：`PlatformAllowList` 为 `["Win64"]`
- **Beta 状态**：`IsBetaVersion = true`，功能可能变化
- **需要手动启用**：`EnabledByDefault = false`

## 使用场景

- 你在用 **Live Link Hub** 录制手柄输入数据，用于后期驱动动画或回放
- 你需要将 Xbox/PS 手柄的实时输入通过 Live Link 转发给其他 UE 实例或外部工具
- 你需要在 Take Recorder 中录制手柄输入轨迹（plugin 带有 SceneTime 元数据支持）

## 使用方法

### 在 Live Link Hub 中添加源

1. 打开 **Live Link Hub**
2. 进入 Live Link 面板，点击 **Add Source**
3. 在弹出的模态窗口中选择 **LiveLinkInputDevice Source**
4. 点击 **Add** 确认（当前无额外配置选项）

### 连接手柄

- 连接 Xbox/PS 等游戏手柄后，源状态会自动从 "Waiting for a device." 变为 "Receiving"
- 每个手柄以 `Gamepad_0`、`Gamepad_1` 等名称作为独立的 Live Link Subject 出现
- 拔掉手柄后自动回到等待状态

### Live Link 数据结构

每个 Subject 使用 `ULiveLinkInputDeviceRole`，帧数据 (`FLiveLinkGamepadInputDeviceFrameData`) 包含以下字段：

| 类别 | 字段 |
|---|---|
| 左摇杆 | `LeftAnalogX`, `LeftAnalogY`, `LeftStickUp`, `LeftStickDown`, `LeftStickLeft`, `LeftStickRight` |
| 右摇杆 | `RightAnalogX`, `RightAnalogY`, `RightStickUp`, `RightStickDown`, `RightStickLeft`, `RightStickRight` |
| 扳机 | `LeftTriggerAnalog`, `LeftTriggerThreshold`, `RightTriggerAnalog`, `RightTriggerThreshold` |
| 肩键 | `LeftShoulder`, `RightShoulder` |
| 面板按钮 | `FaceButtonBottom`(A/×), `FaceButtonRight`(B/○), `FaceButtonLeft`(X/□), `FaceButtonTop`(Y/△) |
| 摇杆按下 | `LeftThumb`, `RightThumb` |
| 特殊键 | `SpecialLeft`(View/Share), `SpecialLeft_X`, `SpecialLeft_Y`, `SpecialRight`(Menu/Options) |
| 方向键 | `DPadUp`, `DPadDown`, `DPadLeft`, `DPadRight` |

按钮值为 0 或 1，摇杆/扳机值为 -1.0 ~ 1.0 或 0.0 ~ 1.0 的浮点数。

## C++ 用法

### 头文件引入

```cpp
#include "LiveLinkInputDevice.h"
#include "LiveLinkInputDeviceSource.h"
#include "LiveLinkInputDeviceConnectionSettings.h"
```

### 基本架构

Source 类 `FLiveLinkInputDeviceSource` 同时继承 `ILiveLinkSource` 和 `FRunnable`：

```cpp
// 创建 source（通常由 Factory 完成，不需要手动调用）
FLiveLinkInputDeviceConnectionSettings Settings;
TSharedPtr<FLiveLinkInputDeviceSource> Source = MakeShared<FLiveLinkInputDeviceSource>(Settings);
```

Source 在构造时注册两个回调：
- `FCoreDelegates::OnEndFrame` — 延迟启动轮询线程
- `IPlatformInputDeviceMapper::GetOnInputDeviceConnectionChange()` — 监听手柄热插拔

### MessageHandler

内部使用 `FLiveLinkInputDeviceMessageHandler`（继承 `FGenericApplicationMessageHandler`）拦截手柄事件：

```cpp
// 按钮按下 → 值设为 1
bool OnControllerButtonPressed(FGamepadKeyNames::Type KeyName, FPlatformUserId, FInputDeviceId, bool IsRepeat);

// 按钮释放 → 值设为 0
bool OnControllerButtonReleased(FGamepadKeyNames::Type KeyName, FPlatformUserId, FInputDeviceId, bool IsRepeat);

// 模拟轴 → 直接传递浮点值
bool OnControllerAnalog(FGamepadKeyNames::Type KeyName, FPlatformUserId, FInputDeviceId, float AnalogValue);
```

### Input Device 插件加载

Source 通过 `IModularFeatures` 发现所有 `IInputDeviceModule` 实现，调用 `CreateInputDevice` 创建输入设备实例（以非主设备身份）：

```cpp
TArray<IInputDeviceModule*> PluginImplementations = IModularFeatures::Get()
    .GetModularFeatureImplementations<IInputDeviceModule>(IInputDeviceModule::GetModularFeatureName());
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础模块 |
| `LiveLinkInterface` | Live Link 协议接口 |
| `ApplicationCore` | 平台输入设备映射 |
| `CoreUObject` | UObject 反射 |
| `Engine` | 引擎核心 |
| `InputDevice` | UE 输入设备系统 |
| `Slate` / `SlateCore` | 添加源的 UI 面板 |

Plugin 级别依赖：`LiveLink`

## 维护状态

### 近期更新

| 日期 | Hash | 说明 |
|---|---|---|
| 2025-05-30 | `d8d2374` | 将 "Add Source" 菜单从下拉改为模态弹窗 |
| 2024-06-18 | `06395cb` | 添加 SceneTime 到帧数据，使 Take Recorder 能录制 input device 轨道 |
| 2024-06-04 | `a67aedf` | 使用 IPlatformInputDeviceMapper 监听手柄连接变化（Live Link Hub 适配） |

### 维护评价

- **创建时间**：2024 年 1 月，约 2 年历史
- **活跃度**：最近一次更新在 2025 年 5 月，属于活跃维护
- **Beta 状态**：仍标记为 Beta，功能可能随版本变化
- **推荐度**：如果你的 Virtual Production 流程需要录制手柄输入，这是唯一官方方案。但注意它仅在 LiveLinkHub 中可用，且仅支持 Win64。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/LiveLinkInputDevice)
- [官方文档]()（无）
