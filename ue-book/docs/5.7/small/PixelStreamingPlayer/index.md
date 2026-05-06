# Pixel Streaming Player

> Support for receiving a pixel streaming stream and displaying it in game.

| 属性 | 值 |
|---|---|
| 中文名 | 像素流接收器 |
| 分类 | Graphics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容资产） |
| 模块 | `PixelStreamingPlayer` (Runtime), `PixelStreamingPlayerEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-03-15 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PixelStreamingPlayer) | |

## 总体用途

Pixel Streaming Player 是一个实验性插件，用于在虚幻引擎应用中接收并显示像素流（Pixel Streaming）画面。它提供了一个流接收器（Streamer）组件，使得引擎实例可以作为像素流客户端运行，将远程渲染器的画面拉取并在本地渲染显示。

该插件解决了“在同一引擎实例中消费像素流”的需求，适用于需要将远程渲染画面作为材质、UI背景或场景元素嵌入本地世界的场景。作为实验性插件，它标志着像素流技术从“仅发送端”向“协议对称化”方向的演进，为更复杂的分布式渲染和虚拟制作工作流奠定基础。

> 详细模块文档请参考：
> - [PixelStreamingPlayer（运行时）](PixelStreamingPlayer.md)
> - [PixelStreamingPlayerEditor（编辑器）](PixelStreamingPlayerEditor.md)

## 使用场景

- **游戏内远程渲染**：在游戏世界中嵌入一个“显示器”，实时显示另一台服务器渲染的画面
- **多人协作 / 虚拟制作**：在一个 UE 会话中预览其他 UE 会话的输出
- **编辑器远程预览**：在编辑器编辑模式下嵌入像素流窗口，用于材质调试或场景对比
- **构建远程应用**：作为客户端组件集成到需要在本地渲染远程视频流的应用中

## 模块依赖

| 模块 | 用途 |
|---|---|
| `PixelStreaming` | 核心像素流协议层（信令、编解码、传输） |

> 注意：该插件的运行时模块依赖 `PixelStreaming` 模块，两者必须同时启用。

## 模块列表

| 模块名 | 类型 | 一句话总结 | 文档 |
|---|---|---|---|
| `PixelStreamingPlayer` | Runtime | 运行时核心，负责像素流接收、解码、渲染，提供流播放与状态管理组件 | [PixelStreamingPlayer.md](PixelStreamingPlayer.md) |
| `PixelStreamingPlayerEditor` | Editor | 编辑器扩展，提供流播放器 Actor 的定制面板、自定义细节与快捷创建入口 | [PixelStreamingPlayerEditor.md](PixelStreamingPlayerEditor.md) |

## 维护状态

### 近期更新

- 2025-08-26 — Deprecating the functions RHICreateTextureReference and RHIUpdateTextureReference to force callers to update
- 2025-04-10 — 更新渲染相关接口
- 2024-09-04 — [PixelStreaming] 修复：取消对 VCam 依赖的废弃 API 标记
- 2024-09-04 — 引入 PixelStreaming2（新版本概念）
- 2024-03-15 — 首次提交：移除 Media 模块中的 FRHICommandListExecutor 直接调用

### 维护评价

- **创建时间**：2024-03-15，约 1.6 年前
- **最近更新**：2025-08-26（2 个月前），维护活跃
- **关键信号**：
  - `IsBetaVersion=true`，标记为实验性
  - 2024-09-04 引入了 `PixelStreaming2` 概念，表明技术仍处于迭代期
  - 近期 commit 包含接口废弃与渲染层更新，说明正在跟随主流 RHI 重构
- **综合评价**：该插件是实验性、活跃开发的模块，适合用于预览、试验和下一代像素流方案探索。对于生产项目，建议密切关注 PixelStreaming2 的成熟度并做好迁移准备。总体而言**推荐尝试**，但需要接受 API 变更风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PixelStreamingPlayer)（GitHub，分支 5.7）
- [官方文档](https://docs.unrealengine.com/en-US/Platforms/PixelStreaming/index.html)（Pixel Streaming 总文档）
- [PixelStreamingPlayer.md](PixelStreamingPlayer.md) — 运行时模块详细文档
- [PixelStreamingPlayerEditor.md](PixelStreamingPlayerEditor.md) — 编辑器模块详细文档