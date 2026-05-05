# Input Debugging

> Input debugging and visualization.

| 属性 | 值 |
|---|---|
| 分类 | Input |
| 默认启用 | true |
| 包含内容 | false |
| 模块 | InputDebugging (Runtime), InputDebuggingEditor (Editor) |
| 创建时间 | 2022-05-19 |
| 年龄标签 | 🆕 (约4年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/InputDebugging) | |

## 用途

InputDebugging plugin 提供运行时输入设备的调试可视化工具。它解决的核心问题是：在开发多平台、多设备的游戏时，开发者需要实时查看哪些输入设备已连接、它们被映射到哪个 Platform User、以及当前有哪些 Input Device Property 在生效。

这个 plugin 主要包含两个功能子系统：

1. **InputDeviceDebugTools** — 通过 HUD 调试绘制和控制台命令，展示输入设备的连接状态、硬件标识符、Platform User 映射，以及当前激活的 Input Device Properties（如触觉反馈等）。
2. **TouchInputVisualizer** — 在屏幕上可视化触摸输入点，包括触摸位置和压力值。

此外，Editor 模块会在编辑器中监听输入设备的连接/断开事件，弹出通知提醒开发者。

所有调试功能在 Shipping 构建中自动禁用（通过 `TargetConfigurationDenyList: ["Shipping"]` 和 `#if !UE_BUILD_SHIPPING` 预处理宏双重保障）。

## 使用场景

- 你在开发支持多控制器的本地多人游戏 → 用 InputDebugging 查看每个手柄映射到哪个 Platform User
- 你在调试输入设备的连接/断开流程 → 用控制台命令或 HUD 调试视图实时监控
- 你在开发触屏游戏，需要验证触摸点位置和压力 → 用 TouchInputVisualizer 在屏幕上直接看到触摸点
- 你在测试 Input Device Properties（如触发器阻力、灯光颜色等）→ 用 `showdebug DeviceProperty` 查看当前激活的属性

## 蓝图用法

此 plugin 没有暴露 BlueprintCallable 函数。它的功能主要通过控制台命令和 HUD 调试视图访问。

### 控制台命令

| 命令 | 说明 |
|---|---|
| `Input.ListAllHardwareDevices` | 将当前平台所有已知的 `FHardwareDeviceIdentifier` 输出到日志 |
| `Input.LogAllConnectedDevices` | 将所有已连接的输入设备及其元数据（设备ID、硬件信息、映射策略）输出到日志 |
| `Input.Debug.ShowTouches` | 设为 1 启用触摸输入可视化（在屏幕上绘制触摸点圆圈） |

### HUD 调试视图

使用 `showdebug` 控制台命令开启：

| 命令 | 说明 |
|---|---|
| `showdebug DeviceProperty` | 显示当前所有激活的 Input Device Properties，按 Platform User 分组，包含属性名、句柄、设备ID、标志位（循环/无视时间膨胀/暂停时播放/已应用）和评估时间 |
| `showdebug Devices` | 显示所有 Platform User 及其关联的输入设备，包含硬件标识符、Slate User Index、连接状态（彩色编码：绿=已连接、灰=已断开、红=无效、橙=未知） |

## C++ 用法

### 头文件引入

```cpp
// InputDeviceDebugTools.h 是 Private 的，不建议直接引用
// 通过 IInputDebuggingInterface 访问模块功能
#include "IInputDebuggingInterface.h"
```

### 基本用法：检查 InputDebugging 模块是否可用

```cpp
// IInputDebuggingInterface 定义在 InputCore 模块中
// 通过 Modular Feature 机制访问
if (IInputDebuggingInterface::IsAvailable())
{
    IInputDebuggingInterface& Debugging = IInputDebuggingInterface::Get();
    // 模块已加载，调试功能可用
}
```

> 来源：`Engine/Source/Runtime/InputCore/Public/IInputDebuggingInterface.h`

### 进阶用法：自定义编译宏控制调试功能

InputDebugging 使用两个编译宏控制调试功能的编译：

```cpp
// 在你的 Build.cs 中可以覆盖默认行为
// 默认值：非 Shipping 构建自动启用

// 控制 InputDeviceDebugTools（设备调试工具）
// 默认: #define SUPPORT_INPUT_DEVICE_DEBUGGING !UE_BUILD_SHIPPING

// 控制 TouchInputVisualizer（触摸可视化）
// 默认: #define SUPPORT_TOUCH_INPUT_DISPLAY !UE_BUILD_SHIPPING
```

如果你在 Build.cs 中设置了这些宏，可以精细控制哪些调试功能被编译进去：

```cpp
// 你的模块的 Build.cs
PublicDefinitions.Add("SUPPORT_INPUT_DEVICE_DEBUGGING=1");  // 强制启用设备调试
PublicDefinitions.Add("SUPPORT_TOUCH_INPUT_DISPLAY=0");      // 强制禁用触摸可视化
```

## Demo 示例

此 plugin 是纯调试工具，不需要在项目代码中直接集成。典型使用方式：

```
// 1. 确保 plugin 已启用（默认已启用）

// 2. 运行游戏，在控制台中输入：
Input.LogAllConnectedDevices

// 3. 输出示例（Log 窗口）：
// [LogInput] Total number of active users: 1
// [LogInput] Input Device Mapping Policy: PrimaryUserSharesKeyboardAndFirstGamepad
// [LogInput] Platform User: 0    2 devices
// [LogInput]     Input Device Id: 0    Hardware Info: GenericKeyboard::GenericKeyboard
// [LogInput]     Input Device Id: 1    Hardware Info: XInputController::XboxOneController

// 4. 查看 HUD 调试：
showdebug Devices
showdebug DeviceProperty

// 5. 触摸可视化（移动设备或模拟触摸）：
Input.Debug.ShowTouches 1
```

## 模块依赖

### InputDebugging（Runtime 模块）

| 模块 | 用途 |
|---|---|
| `ApplicationCore` | 平台输入设备映射器（IPlatformInputDeviceMapper） |
| `Core` | 基础类型和工具 |
| `CoreUObject` | UObject 系统 |
| `Engine` | Canvas、HUD、DebugDrawService、InputDeviceSubsystem |
| `InputCore` | IInputDebuggingInterface 接口定义 |
| `Slate` | FSlateApplication 输入预处理器（触摸可视化） |
| `SlateCore` | Slate 核心类型 |
| `UnrealEd` | 编辑器构建时才依赖，用于 LevelEditorPlaySettings |

### InputDebuggingEditor（Editor 模块）

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型 |
| `ApplicationCore` | 输入设备连接状态枚举 |
| `Slate` | 通知系统 |
| `SlateCore` | Slate 样式 |
| `MainFrame` | 主窗口框架 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-09-23 | `2e995baebf56` | Fix `suppress` misspellings in Engine/Plugins | 代码质量修复，将 `suppress` 拼写错误修正 |
| 2025-06-17 | `13ff9d053b79` | Add editor preference for "Simulated Device Mapping Policy" | **功能更新**：在编辑器 Play 设置中添加模拟设备映射策略，可在编辑器中测试不同设备映射场景 |
| 2025-05-16 | `bef838575068` | Add "Input.LogAllConnectedDevices" command | **功能更新**：新增控制台命令，可将所有连接设备及其元数据输出到日志 |

### 维护评价

- **创建时间**：2022-05-19，约 4 年历史
- **最近更新**：2025 年有两次实质性功能更新（新增控制台命令和编辑器模拟设备策略），说明仍在活跃开发
- **活跃度**：活跃维护中，近期有持续的功能增强
- **已知限制**：
  - Shipping 构建中完全禁用，无法在发布版本中使用
  - 没有公开的 Blueprint API，仅通过控制台命令和 HUD 调试访问
  - 没有自动化测试用例
- **推荐程度**：✅ 推荐在开发阶段使用。这是一个轻量级的调试辅助工具，默认启用无需额外配置，对多设备/多平台开发非常有帮助。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/InputDebugging)
- [IInputDebuggingInterface 接口](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Source/Runtime/InputCore/Public/IInputDebuggingInterface.h)
- 官方文档：无（.uplugin 中 DocsURL 为空）
