# Razer Chroma Devices

> Provides some functionality to set Razer Chroma effects at runtime.

| 属性 | 值 |
|---|---|
| 中文名 | 雷蛇幻彩设备 |
| 分类 | Peripherals |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容资产） |
| 模块 | `RazerChromaDevices` (ClientOnlyNoCommandlet), `RazerChromaEditor` (Editor), `RazerChromaSDK` (External) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-05-23 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/RazerChromaDevices) | |

## 用途

该插件封装了 **Razer Chroma SDK**，允许在游戏运行时（客户端）向雷蛇外设（键盘、鼠标、耳机、鼠标垫等）发送灯光效果指令。集成后可通过蓝图或 C++ 快速实现与游戏事件联动的动态 Chroma 灯光，增强沉浸式体验。同时提供编辑器模块，用于在开发阶段预览或管理 Chroma 效果资产。

## 模块列表

| 模块 | 类型 | 一句话说明 | 文档 |
|---|---|---|---|
| RazerChromaDevices | ClientOnlyNoCommandlet | 运行时核心模块，提供调用 Chroma SDK 的蓝图接口与 C++ API | [详细](RazerChromaDevices.md) |
| RazerChromaEditor | Editor | 编辑器模块，用于在项目设置/内容浏览器中对 Chroma 效果进行配置和预览 | [详细](RazerChromaEditor.md) |
| RazerChromaSDK | External | 外部 SDK 包装库，链接雷蛇官方的 Chroma SDK 动态库（Windows） | [详细](RazerChromaSDK.md) |

## 使用场景

- 制作一款支持雷蛇外设灯效的游戏，根据玩家血量、击杀、关卡切换等事件触发不同的键盘/鼠标灯光效果。
- 在编辑器中预先设计并测试多套 Chroma 灯光方案，运行时根据游戏状态切换。
- 利用 Chroma SDK 的 REST API（间接通过本插件）实现联动效果，扩大外设灯光生态的代入感。

## 相关链接

- [源码（5.7 分支）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/RazerChromaDevices)
- [Razer Chroma SDK 官方文档](https://developer.razer.com/chroma/)（外部）