# Stylus & Tablet Plugin

> Support for advanced stylus and tablet inputs such as pressure, stylus and tablet buttons, and pen angles.

| 属性 | 值 |
|---|---|
| 中文名 | 手写板输入 |
| 分类 | Input Devices |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `StylusInput` (Editor), `StylusInputDebugWidget` (EditorNoCommandlet), `StylusInputMac` (EditorNoCommandlet), `StylusInputRealTimeStylus` (EditorNoCommandlet), `StylusInputWintab` (EditorNoCommandlet) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-06-04 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/StylusInput) | |

## 用途

为 UE5 编辑器提供数位板/手写板的高级输入支持。该插件抽象了不同平台的数位板驱动差异，提供统一的 API 来获取压感、笔倾斜角度、笔按键和数位板按键等输入数据。在编辑器中使用数位笔进行雕刻、绘制或精确操作时非常有用。

## 使用场景

- 你需要在编辑器中使用 Wacom 等数位板进行资产雕刻或绘制 → 用 StylusInput
- 你需要获取数位笔的压感和倾斜角度来控制笔刷效果 → 用 StylusInput
- 你在 macOS 上使用数位板进行开发 → 用 StylusInputMac
- 你在 Windows 上使用 RealTimeStylus API 的数位板 → 用 StylusInputRealTimeStylus
- 你在 Windows 上使用 Wintab 驱动的数位板（如旧版 Wacom）→ 用 StylusInputWintab

## 模块一览

| 模块 | 平台 | 说明 |
|---|---|---|
| `StylusInput` | 全平台 | 核心抽象层，定义数位板输入的公共接口和数据结构 |
| `StylusInputDebugWidget` | 全平台 | 调试用 UI 组件，可视化显示当前数位板输入状态 |
| `StylusInputMac` | macOS | macOS 平台数位板输入的实现（基于 NSEvent） |
| `StylusInputRealTimeStylus` | Win64 | Windows RealTimeStylus API 的实现 |
| `StylusInputWintab` | Win64 | Windows Wintab 驱动的实现 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-19 | `9693e160` | StylusInput: Fix NSEvent up/down | 修复 macOS 笔抬起/按下事件处理 |
| 2026-05-19 | `36a0dc9c` | StylusInput: Fix issue with multiple Wintab instances | 修复多个 Wintab 实例共存的问题 |
| 2026-05-13 | `041d4d75` | StylusInput: Fix coordinates issue with Wintab when main screen is not on left/top | 修复 Wintab 在非主显示器左上角时的坐标偏移 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移到新格式 |
| 2026-01-28 | `5f766aee` | Fixed modules that does not support portable toolchain | 修复不支持便携工具链的模块 |

### 维护评价

该插件创建于 2019 年（约 7 年前），但近期（2026 年）仍在持续修复平台相关的 bug，说明仍在活跃维护中。近期更新集中在 macOS 和 Windows 平台的输入正确性修复上。注意该插件仍标记为 **Beta 版本**且**默认未启用**，使用时需在插件设置中手动开启。对于需要在编辑器中使用数位板高级功能的用户，该插件是目前唯一的官方解决方案，可以放心使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/StylusInput)