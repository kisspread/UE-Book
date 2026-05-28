# Game Input Base

> GameInput is a next-generation input API that exposes input devices of all kinds through a single consistent interface.

| 属性 | 值 |
|---|---|
| 中文名 | 游戏输入基础 |
| 分类 | Input Devices |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GameInputBase` (Runtime), `GameInputBaseEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2024-02-12 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GameInput) | |

## 用途

该插件是微软 **GameInput API** 的 Unreal Engine 集成封装。GameInput 是旨在取代传统 XInput 的下一代输入框架，它通过一个统一的接口暴露了游戏手柄、键盘、鼠标等各类输入设备。此插件的核心作用是为 UE 项目提供接入这一现代 Windows 输入系统的桥梁，解决了 XInput 在设备支持、功能扩展性（如高级触觉反馈、自适应扳机）方面的局限性。

## 使用场景

- 你在 Windows 平台上开发游戏，并希望使用超越 XInput 功能的**现代游戏手柄**（如 Xbox Wireless Controller with USB-C）的高级特性（如 HD 震动、自适应扳机）。
- 你需要一个**统一的输入接口**来处理来自不同种类设备的输入，而不是分别处理 XInput、DirectInput 等。
- 你希望获得更底层的设备信息或支持未来可能出现的新型输入设备。
- 你的目标平台是 **Win64**，并希望利用平台原生的下一代输入 API。

## 模块概览

| 模块 | 类型 | 说明 |
|---|---|---|
| **GameInputBase** | Runtime | 核心运行时模块，负责实现 `IInputDevice` 接口，封装与 GameInput API 的交互，处理设备枚举、输入轮询和数据转换。 |
| **GameInputBaseEditor** | Editor | 编辑器集成模块，提供编辑器相关的设置和状态查看功能。 |
| **GameInputWindowsLibrary** | External | 外部依赖库模块，包含微软提供的 GameInput 头文件和预编译的静态库文件，是链接 GameInput 功能的基础。 |

## 模块依赖

要使用此插件，你的模块需要依赖：

| 模块 | 用途 |
|---|---|
| `GameInputBase` | 提供核心的 `IInputDevice` 实现和输入设备管理器接口。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 移植函数类型转换警告，提升跨编译器（MSVC/Clang）兼容性。 |
| 2026-05-01 | `1fbba943` | [GameInput] Add haptic audio endpoint support via XAudio2. | 为 GameInput 添加通过 XAudio2 实现的触觉音频端点支持。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移至 UE_LOGF 宏。 |
| 2026-04-02 | `a4559861` | UE_LOG -> UE_LOGF macro conversion for Game Input modules | 为游戏输入模块进行 UE_LOG 到 UE_LOGF 的宏转换。 |
| 2026-04-01 | `1afb0871` | [Input] Add a thread affinity for input for IInputDevice so that we can specify which input modules | 为 IInputDevice 添加线程关联性，允许指定输入模块的运行线程。 |

### 维护评价

该插件创建于 2024 年初，相对年轻。从最近的 Git 提交记录来看（最新到 2026 年 5 月），**维护非常活跃**。近期的更新不仅包括了编译器兼容性修复、日志系统升级等常规维护，更重要的是持续添加了新功能（如触觉音频端点支持）和对底层架构的改进（输入线程关联性）。这表明该插件是 Epic 重点关注和支持的特性，旨在为 Windows 平台提供下一代输入能力。**强烈推荐**在 Windows 平台需要使用高级输入设备功能的项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GameInput)
- [GameInput 官方文档 (Microsoft)](https://learn.microsoft.com/en-us/gaming/gdk/_content/gc/input/overviews/input-overview)