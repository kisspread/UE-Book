# Windows DualShock

> InputDevice plugin for the PS4 DualShock controller in Windows

| 属性 | 值 |
|---|---|
| 分类 | Input Devices |
| 默认启用 | ❌ `EnabledByDefault: false` |
| 包含内容 | ❌ `CanContainContent: false` |
| 模块 | WinDualShock (RuntimeNoCommandlet) |
| 创建时间 | 2020-06-23 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Windows/WinDualShock) | |

## 用途

WinDualShock 为 Windows 平台上的 PlayStation 手柄（DualShock 4 / DualSense）提供完整的输入和音频支持。它通过 Sony 官方的 `libScePad` 库与控制器通信，解决了以下问题：

1. **输入映射**：将 PS4/PS5 手柄的按键、摇杆、触摸板、陀螺仪等映射为 UE 输入事件
2. **力反馈（振动）**：将 UE 的 ForceFeedback 系统路由到手柄的振动马达
3. **手柄内置扬声器音频**：通过 XAudio2 将游戏音频输出到手柄内置喇叭
4. **振动马达音频**：DualSense 支持将音频数据直接发送到自适应扳机的振动线圈

该插件仅在 Windows 平台可用，且需要 Sony 的 `libScePad` 开发库（通常随 PlayStation SDK 提供）。由于 `DUALSHOCK4_SUPPORT` 编译宏的控制，如果构建环境中没有 `LibScePad`，插件会自动禁用自身功能。

## 使用场景

- 你在 Windows 上开发支持 PlayStation 手柄的游戏，需要读取 DualShock 4 / DualSense 的输入
- 你希望在手柄的内置扬声器播放音效（如无线电通话、环境音效等）
- 你需要使用 DualSense 的自适应扳机和触觉反馈功能
- 你正在开发一款跨平台游戏，需要在 PC 上也能测试 PlayStation 手柄的特殊功能

## 蓝图用法

该插件没有暴露 `BlueprintCallable` 函数或 `BlueprintReadWrite` 属性。它是一个**透明的输入设备层**——启用后，手柄自动作为标准输入设备被 UE 识别，通过增强输入系统（Enhanced Input）或传统输入映射直接使用。

### 在编辑器中启用插件

1. 打开 **Edit → Plugins**
2. 搜索 **"Windows DualShock"**
3. 勾选启用
4. 重启编辑器

### 配置选项（Engine.ini）

通过在 `Engine.ini` 的 `[SonyController]` 节配置以下选项：

| 配置项 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `bDSTouchEvents` | bool | false | 触摸板发送触摸事件 |
| `bDSTouchAxisButtons` | bool | false | 触摸板发送轴事件 |
| `bDSMouseEvents` | bool | false | 触摸板模拟鼠标事件 |
| `bDSMotionEvents` | bool | false | 启用陀螺仪/加速度计事件 |
| `DSPadSpeakerGain` | float | 1.0 | 手柄扬声器音量 (0.0–1.0) |
| `DSHeadphonesGain` | float | 1.0 | 耳机音量 (0.0–1.0) |
| `DSMicrophoneGain` | float | 1.0 | 麦克风音量 (0.0–1.0) |

### 音频端点设置

在 Audio Mixer 设置中，可配置以下音频端点类型将音频路由到手柄：

- **Pad Speaker Output** — 手柄内置扬声器
- **Vibration Output** — 振动马达（DualSense 专用，DualShock 4 忽略）

使用时在端点设置中指定 `ControllerIndex`（控制器索引，从 0 开始）。

## C++ 用法

### 头文件引入

```cpp
#include "WinDualShockSettings.h"        // UDualShockExternalEndpointSettings 等
#include "WinDualShockSettingsProxies.h"  // FDualShockExternalEndpointSettings 等
```

### 音频端点设置

通过 `UDualShockExternalEndpointSettings` 指定目标控制器：

```cpp
// 创建端点设置，将音频发送到控制器 0 的手柄扬声器
UDualShockExternalEndpointSettings* Settings = NewObject<UDualShockExternalEndpointSettings>();
Settings->ControllerIndex = 0;
```

### 空间化设置

`UDualShockSpatializationSettings` 提供手柄音频的空间化控制：

```cpp
UDualShockSpatializationSettings* SpatialSettings = NewObject<UDualShockSpatializationSettings>();
SpatialSettings->Spread = 1.0f;      // 扩散范围 (0 ~ 2π)
SpatialSettings->Priority = 0;       // 优先级 (0 ~ 1000)
SpatialSettings->Passthrough = false; // 是否直通
```

### 音频参数

插件内部使用以下固定参数（定义在 `EWinDualShockDefaults`）：

| 参数 | 值 |
|---|---|
| 采样率 | 48000 Hz |
| 帧大小 | 256 样本 |
| 手柄扬声器通道 | 2（立体声） |
| 振动通道 | 2 |
| 麦克风通道 | 2 |
| 队列深度 | 4 |

### 自定义模块依赖

如果你想在自己的模块中引用 WinDualShock 的设置类型，需要在 `Build.cs` 中添加依赖：

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "InputDevice",   // IInputDeviceModule 接口
    "AudioExtensions", // IAudioEndpoint / UAudioEndpointSettingsBase
    "Projects"         // IPluginManager
});
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础引擎功能 |
| `CoreUObject` | UObject 系统 |
| `ApplicationCore` | 平台应用抽象 |
| `Engine` | 引擎核心 |
| `Slate` | UI 框架 |
| `InputDevice` | 输入设备接口 (`IInputDeviceModule`) |
| `AudioMixerCore` | 音频混音器核心 |
| `AudioMixer` | 音频混音器 |
| `AudioExtensions` | 音频端点扩展 (`IAudioEndpoint`) |
| `Projects` | 插件管理 |

此外，构建时通过反射检查 `LibScePad` 模块是否存在，如果存在则额外依赖：
- `LibScePad` — Sony 官方手柄 SDK
- `DX11Audio` — DirectX 11 音频
- `XAudio2_9` — XAudio2 音频 API

## 维护状态

### 近期更新

| 日期 | Hash | 提交信息 | 解读 |
|---|---|---|---|
| 2025-07-18 | `892dcc40` | Fix DualSense controllers not functioning with Wasapi audio backend enabled | Bug 修复：修复了启用 WASAPI 音频后端时 DualSense 失灵的问题 |
| 2025-05-09 | `fcd37432` | WinDualShock disabled on arm64 in the build rules, not UEBuildWindows | 构建修复：在 Build.cs 中禁用 ARM64 支持（libScePad 不支持 ARM64） |
| 2025-04-22 | `08064e64` | Removed #pragma comment(lib, "xaudio2_9redist.lib") since we use an external module to pull in the lib/dll | 重构：移除硬编码的 lib 引用，改用模块化方式加载 XAudio2 |

### 维护评价

- **年龄**：创建于 2020 年，约 5 年历史
- **活跃度**：近期（2025 年 7 月）仍有功能性更新和 Bug 修复，属于**活跃维护**状态
- **平台限制**：仅 Windows 64 位，且需要 Sony SDK（`libScePad`），普通开发者无法直接使用
- **默认禁用**：`EnabledByDefault: false`，需手动启用
- **编译守卫**：代码通过 `DUALSHOCK4_SUPPORT` 宏控制，缺少 SDK 时自动编译为空模块

**建议**：如果你有 PlayStation 开发者授权和 Sony SDK，该插件是 UE5 中使用 PS 手柄的标准方式。对于一般 PC 游戏开发，UE5 内置的通用游戏手柄支持（通过 SDL/Windows.Gaming.Input）通常已经足够。该插件的价值在于访问 DualShock 4/DualSense 的**专有功能**（触摸板、陀螺仪、手柄扬声器、自适应扳机等）。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Windows/WinDualShock)
- [官方文档]()（无）
- [测试用例]()（插件目录内无测试文件）
