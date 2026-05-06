# Pixel Streaming 2

> Streaming of Unreal Engine audio and rendering to WebRTC-compatible media players such as a web browsers.

| 属性 | 值 |
|---|---|
| 中文名 | 像素流送2 |
| 分类 | Graphics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PixelStreaming2` (Runtime), `PixelStreaming2Core` (Runtime), `PixelStreaming2Editor` (Runtime), `PixelStreaming2HMD` (Runtime), `PixelStreaming2Input` (Runtime), `PixelStreaming2RTC` (Runtime), `PixelStreaming2Servers` (Runtime), `PixelStreaming2Settings` (Runtime), `EpicRtc` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-10-13 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/PixelStreaming2) | |

---

## 总体用途

Pixel Streaming 2 是 UE5 的第二代像素流送插件。它通过 WebRTC 协议将虚幻引擎的视口渲染画面和音频实时流式传输到任意兼容 WebRTC 的浏览器或客户端。用户无需安装任何额外软件，即可通过网页远程交互、观看或操作 UE 应用程序。相比第一代，PixelStreaming2 重构了核心架构，使用自家 `EpicRtc` 替代旧方案，性能更高、延迟更低，并提供了更灵活的服务器部署与输入处理能力。

---

## 模块一览

每个模块的核心职责如下，详细 API 与用法请参考相应子文档。

| 模块 | 一句话总结 | 文档链接 |
|---|---|---|
| `PixelStreaming2` | 主模块：负责音视频编码、传输管线与整体流送生命周期管理。 | [PixelStreaming2.md](PixelStreaming2.md) |
| `PixelStreaming2Core` | 核心库：提供流送所需的数据结构、工具函数和日志系统。 | [PixelStreaming2Core.md](PixelStreaming2Core.md) |
| `PixelStreaming2Editor` | 编辑器集成：提供设置面板、启动按钮等编辑器内操作界面。 | [PixelStreaming2Editor.md](PixelStreaming2Editor.md) |
| `PixelStreaming2HMD` | 头显支持：处理 VR/XR 设备下的双视口流送与头部追踪数据回传。 | [PixelStreaming2HMD.md](PixelStreaming2HMD.md) |
| `PixelStreaming2Input` | 输入转发：接收浏览器的键盘、鼠标、触控、游戏手柄等输入事件，并注入引擎。 | [PixelStreaming2Input.md](PixelStreaming2Input.md) |
| `PixelStreaming2RTC` | WebRTC 连接管理：封装信令交互、PeerConnection 生命周期和媒体轨道控制。 | [PixelStreaming2RTC.md](PixelStreaming2RTC.md) |
| `PixelStreaming2Servers` | 服务器管理：集成信令服务器、SFU 等外部进程的启动、监控与停止。 | [PixelStreaming2Servers.md](PixelStreaming2Servers.md) |
| `PixelStreaming2Settings` | 设置系统：定义全局配置、编解码参数、网络策略等，支持控制台变量与项目设置。 | [PixelStreaming2Settings.md](PixelStreaming2Settings.md) |
| `EpicRtc` | 第三方 WebRTC 库封装：提供底层 RTC 接口实现，隐藏不同平台的编译与链接细节。 | [EpicRtc.md](EpicRtc.md) |

---

## 使用场景

- **远程协作审查**：建筑师、设计师或客户通过浏览器实时查看 3D 场景并进行交互，无需高性能硬件。
- **云游戏/交互式应用**：将 UE 游戏或模拟应用部署到云端，用户通过低延迟视频流在移动端或低配设备上操作。
- **数字孪生/可视化**：实时渲染智慧城市、工业仿真等大场景，多个观看者同时访问同一实例。
- **教育/培训**：将 VR/AR 内容流送到普通浏览器，降低硬件门槛，支持大规模在线教学。
- **远程演示与销售**：在线展示汽车配置、室内装修效果，用户通过网页自由切换视角与参数。

---

## 相关链接

- [官方文档](https://docs.unrealengine.com/en-US/Platforms/PixelStreaming/index.html)
- [源码（全部模块）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/PixelStreaming2)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/PixelStreaming2/Tests)（部分模块包含自动化测试）

---

## 维护状态

### 近期更新

| 日期 | 提交 | 解读 |
|---|---|---|
| 2026-01-23 | `a9928676` | [NVCodecs, PixelStreaming2] Fixes: 修复与编译、运行相关的多个问题。 |
| 2025-11-18 | `d7a4d160` | [AVCodecs, PixelStreaming2] Fixes: 修复编解码器兼容性和崩溃问题。 |
| 2025-10-28 | `b1db9444` | [PixelStreaming2] Fix: Deadlocks in PixelStreaming2Thread 修复线程死锁。 |
| 2025-10-17 | `5c2f039d` | [PS2] Fix: Non-functional public API 修复公共 API 不工作的缺陷。 |
| 2025-10-13 | `0de4d465` | [PS2] Bug Fixes for 5.7 针对 UE 5.7 的初始 bug 修复。 |

### 维护评价

- **创建时间**：2025-10-13（约 0.5 年）
- **更新频率**：前 3 个月密集修复，目前仍在活跃维护。
- **内容**：全为 bug 修复与稳定性改进，尚无重大功能新增，表明插件处于成熟稳定阶段。
- **推荐程度**：✅ **强烈推荐** – 作为官方第二代像素流送方案，架构合理、持续修复，适合生产环境使用。注意需要手动启用（`EnabledByDefault=false`），并在项目中配置 WebRTC 环境。