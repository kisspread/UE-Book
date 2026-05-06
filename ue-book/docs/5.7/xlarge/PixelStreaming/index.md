# Pixel Streaming

> Streaming of Unreal Engine audio and rendering to WebRTC-compatible media players such as a web browsers.

| 属性 | 值 |
|---|---|
| 中文名 | 像素流送 |
| 分类 | Graphics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图节点、流媒体服务器脚本） |
| 模块 | `PixelStreaming` (Runtime), `PixelStreamingBlueprint` (Runtime), `PixelStreamingBlueprintEditor` (Runtime), `PixelStreamingEditor` (Runtime), `PixelStreamingHMD` (Runtime), `PixelStreamingInput` (Runtime), `PixelStreamingServers` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-08-29 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/PixelStreaming) | |

## 总体用途

Pixel Streaming 插件将虚幻引擎的实时渲染画面和音频通过 WebRTC 协议流式传输到任何支持 WebRTC 的客户端（如网页浏览器、移动设备）。它支持双向交互：客户端可发送输入（鼠标、键盘、触控、游戏手柄）到引擎，引擎响应并更新画面。插件还集成了信令服务器和 Web 服务器的自动管理，支持 HMD 设备（VR/AR）的流送、自适应比特率编码、多个并行客户端以及编辑器内的预览和控制。适用于云端渲染、远程桌面、虚拟展览、汽车 HMI 演示等场景。

## 模块列表

| 模块 | 一句话总结 | 详细文档 |
|---|---|---|
| `PixelStreaming` | 核心运行时模块，管理编码器、渲染捕获、WebRTC 对等连接与整体生命周期 | [PixelStreaming.md](./PixelStreaming.md) |
| `PixelStreamingBlueprint` | 提供蓝图节点，用于在蓝图图表中控制流启动/停止、获取连接信息等 | [PixelStreamingBlueprint.md](./PixelStreamingBlueprint.md) |
| `PixelStreamingBlueprintEditor` | 编辑器扩展，用于配置蓝图节点的默认值或生成自定义事件 | [PixelStreamingBlueprintEditor.md](./PixelStreamingBlueprintEditor.md) |
| `PixelStreamingEditor` | 编辑器集成，允许在编辑器中直接启动/停止流媒体、调整设置并显示状态 | [PixelStreamingEditor.md](./PixelStreamingEditor.md) |
| `PixelStreamingHMD` | 支持 VR 头显（如 Oculus、Vive）的渲染流送，将 HMD 视图编码发送 | [PixelStreamingHMD.md](./PixelStreamingHMD.md) |
| `PixelStreamingInput` | 处理客户端输入（鼠标、键盘、触控、游戏手柄）并转化为引擎内部事件 | [PixelStreamingInput.md](./PixelStreamingInput.md) |
| `PixelStreamingServers` | 管理配套的 Web 服务器和信令服务器（Node.js 实现）的启动、停止与端口分配 | [PixelStreamingServers.md](./PixelStreamingServers.md) |

## 使用场景

- **云端游戏/应用**：在服务器上运行高画质虚幻应用，任何设备通过浏览器远程操控，无需下载客户端。
- **远程协作预可视化**：设计师在本地调整场景，实时推送给远端客户或评审人员。
- **VR 内容远程展示**：将 HMD 渲染的画面流送到大屏幕或远程观众设备，实现 VR 体验共享。
- **汽车/工业 HMI 演示**：在浏览器中运行交互式车辆座舱或机器控制界面，实时渲染复杂 3D 内容。
- **教学/培训**：多学员同时连接同一台服务器，观察并操作虚拟场景，降低硬件成本。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/PixelStreaming)
- [官方文档](https://docs.unrealengine.com/en-US/Platforms/PixelStreaming/index.html)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/PixelStreaming/Source/PixelStreaming/Tests)（部分模块）