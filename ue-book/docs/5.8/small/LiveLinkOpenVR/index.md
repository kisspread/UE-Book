# LiveLinkOpenVR

> Live Link plugin for OpenVR (Not supported for native arm64.)

| 属性 | 值 |
|---|---|
| 中文名 | OpenVR实时链接 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `LiveLinkOpenVR` (Runtime), `OpenVR` (External) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-09-11 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/LiveLinkOpenVR) | |

## 用途

为 LiveLink 系统提供 OpenVR（SteamVR）跟踪数据源。该插件主要面向 **LiveLinkHub** 场景，解决 LiveLinkXR 插件在多进程工作流中暴露的问题——通过独立的 OpenVR 数据源，实现跨进程消费 SteamVR 的追踪数据。插件附带了一份 OpenVR SDK 的本地副本（原先存放在 `Engine/Source/ThirdParty` 下）。

简而言之：如果你想在 LiveLinkHub 中获取 SteamVR 头显/控制器的追踪数据，且 LiveLinkXR 无法满足需求，这就是替代方案。

**限制**：仅支持 Win64，不支持原生 arm64 架构。

## 使用场景

- 你在使用 **LiveLinkHub** 做虚拟制片，需要从 SteamVR 获取头显和控制器的 6DoF 追踪数据
- LiveLinkXR 插件在多进程架构下存在问题，你需要一个替代的 VR 追踪数据源
- 你需要将 SteamVR 手柄输入以 **LiveLink Gamepad Input Device** 角色传递给下游工程

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等，以及内置的 OpenVR SDK）。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| [`LiveLinkOpenVR`](LiveLinkOpenVR.md) | Runtime | LiveLink OpenVR 源主体，负责连接 SteamVR 并将跟踪/输入数据发布为 LiveLink 帧 |
| [`OpenVR`](OpenVR.md) | External | 第三方 OpenVR SDK 本地副本（Valve 提供） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到新 API |
| 2025-06-03 | `0a44e4b8` | Plugin modules can be included & excluded on a per-architecture basis. | 支持按架构启用/禁用模块 |
| 2025-05-23 | `f3063039` | LiveLinkOpenVR disabled for arm64 | 禁用 arm64 架构支持 |
| 2024-11-22 | `8ca76f71` | LiveLinkOpenVR: Improved default bindings. | 改进默认按键绑定映射 |
| 2024-09-27 | `9d145f1b` | LiveLinkOpenVR: Marshal SteamVR Input into LiveLinkGamepadInputDevice role. | 将 SteamVR 手柄输入映射为 LiveLink 手柄输入角色 |

### 维护评价

该插件于 2024 年 9 月创建，至今约 1 年，仍处于 **实验性** 阶段。最近一次更新（2026 年 4 月）为日志宏迁移，属维护性改动；实质性功能更新集中在 2024 年底至 2025 年初。作为实验性插件，它仍在维护中但功能边界相对稳定。**推荐在 LiveLinkHub 多进程 VR 追踪场景中使用**，但注意其实验性状态及 Win64-only 限制。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/LiveLinkOpenVR)
- [LiveLinkOpenVR 模块文档](LiveLinkOpenVR.md)
- [OpenVR 模块文档](OpenVR.md)