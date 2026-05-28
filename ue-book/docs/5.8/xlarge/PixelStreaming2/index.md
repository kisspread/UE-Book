# Pixel Streaming 2

> Streaming of Unreal Engine audio and rendering to WebRTC-compatible media players such as a web browsers.

| 属性 | 值 |
|---|---|
| 中文名 | 像素流送 2 |
| 分类 | Graphics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PixelStreaming2` (Runtime), `PixelStreaming2Core` (Runtime), `PixelStreaming2Editor` (Runtime), `PixelStreaming2HMD` (Runtime), `PixelStreaming2Input` (Runtime), `PixelStreaming2RTC` (Runtime), `PixelStreaming2Servers` (Runtime), `PixelStreaming2Settings` (Runtime), `EpicRtc` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-09-04 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming2) | |

## 用途

Pixel Streaming 2 是 UE5 新一代像素流送插件，将引擎的音视频渲染画面通过 WebRTC 协议实时编码并传输到浏览器等兼容播放端，实现无需安装客户端即可远程体验完整 3D 应用的能力。

相比旧版 PixelStreaming，Pixel Streaming 2 做了完整的架构重构：模块化拆分更清晰，使用 Epic 自研的 `EpicRtc` 替代第三方 WebRTC 库，新增 HMD 立体流送支持，并提供独立的信令/流媒体服务器进程，可部署为独立可执行文件。整个插件默认不启用，需手动在项目设置中开启。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| `PixelStreaming2` | Runtime | 主入口模块，提供流送会话管理、编码器选择、H.264/VP8 编码管线 |
| `PixelStreaming2Core` | Runtime | 核心工具库，定义基础类型、协议消息、线程安全工具 |
| `PixelStreaming2Editor` | Runtime | 编辑器集成，在编辑器内提供像素流送的预览与调试功能 |
| `PixelStreaming2HMD` | Runtime | HMD/VR 支持，将立体渲染画面编码为左右眼独立流 |
| `PixelStreaming2Input` | Runtime | 远程输入处理，接收并转发浏览器端的键鼠、触控、手柄输入 |
| `PixelStreaming2RTC` | Runtime | WebRTC 通信层，基于 EpicRtc 封装 PeerConnection、数据通道、音视频轨道 |
| `PixelStreaming2Servers` | Runtime | 信令服务器与 SFU 流媒体服务器，可编译为独立可执行进程 |
| `PixelStreaming2Settings` | Runtime | 插件设置，提供编辑器中的可配置参数面板 |
| `EpicRtc` | Runtime | 第三方 WebRTC 库，Epic 自研的跨平台 RTC 实现 |

## 使用场景

- **云渲染/云游戏**：在服务器端运行 UE 应用，将画面流送到用户的浏览器，适用于 Game-as-a-Service
- **建筑/汽车可视化**：客户无需安装客户端，打开网页链接即可交互浏览 3D 模型
- **VR 串流**：通过 HMD 模块将立体画面推送到头显浏览器，实现轻量化 VR 体验
- **远程协作评审**：多人通过浏览器共同查看同一 UE 场景，各自独立操控视角
- **数字孪生大屏**：在展厅大屏或移动设备上展示服务器端实时渲染的数字孪生应用
- **无需客户端分发**：任何需要避免客户端安装、快速分享 3D 内容的场景

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming2)
- [官方文档](https://docs.unrealengine.com/en-US/Platforms/PixelStreaming/index.html)
- [PixelStreaming2](PixelStreaming2.md) — 主模块文档
- [PixelStreaming2Core](PixelStreaming2Core.md) — 核心工具库文档
- [PixelStreaming2Editor](PixelStreaming2Editor.md) — 编辑器集成文档
- [PixelStreaming2HMD](PixelStreaming2HMD.md) — HMD 支持文档
- [PixelStreaming2Input](PixelStreaming2Input.md) — 远程输入文档
- [PixelStreaming2RTC](PixelStreaming2RTC.md) — WebRTC 通信层文档
- [PixelStreaming2Servers](PixelStreaming2Servers.md) — 服务器进程文档
- [PixelStreaming2Settings](PixelStreaming2Settings.md) — 设置面板文档
- [EpicRtc](EpicRtc.md) — 第三方 RTC 库文档

## 模块依赖

使用者需要依赖的核心模块：

| 模块 | 用途 |
|---|---|
| `PixelStreaming2` | 主流送功能，大部分使用者只需依赖此模块 |
| `PixelStreaming2Core` | 若需要访问核心类型定义或协议消息 |
| `PixelStreaming2Input` | 若需要自定义远程输入处理逻辑 |
| `PixelStreaming2RTC` | 若需要直接操作 WebRTC PeerConnection |
| `VulkanRHI` | PixelStreaming2 模块的额外依赖，用于 GPU 编码器采集 |

无特殊依赖（仅标准 Core/Engine/Slate 等 + `VulkanRHI`）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `c1dab3e1` | [PixelStreaming2] Fix: Input handler obtaining default target window from wrong method | 修复输入处理器获取默认目标窗口的方法错误 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 虚拟制作资产分类调整与迁移 |
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构 FJsonObject 以同时支持 FString 和 FSharedString |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复格式化函数中作用域枚举导致的输出乱码问题 |

### 维护评价

**活跃维护** ✅

Pixel Streaming 2 于 2024 年 9 月随 UE5 从 CL 迁入，是 Epic 官方重点推进的像素流送替代方案。从 git 历史看，2026 年 5 月仍有持续的功能修复和代码质量改进，维护非常活跃。

作为默认禁用的插件，建议在项目初期就决定是否采用——它需要额外的服务器部署架构（信令服务器、SFU）。适合对云渲染/远程访问有明确需求的项目，不建议作为"先开着再说"的插件。