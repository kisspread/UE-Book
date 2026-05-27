# Pixel Streaming Player

> Support for receiving a pixel streaming stream and displaying it in game.

| 属性 | 值 |
|---|---|
| 中文名 | 像素流播放器 |
| 分类 | Graphics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质资产） |
| 模块 | `PixelStreamingPlayer` (Runtime), `PixelStreamingPlayerEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-01-25 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PixelStreamingPlayer) | |

## 用途

Pixel Streaming Player 插件用于在 UE5 应用中**接收并显示来自远端的像素流**。与标准 Pixel Streaming 插件不同（后者负责推流端），这个插件专注于**播放端**——将另一台设备通过 Pixel Streaming 技术推送的画面在本地游戏中实时渲染出来。

典型应用场景：你的 UE5 应用本身不是推流源，而是需要作为客户端接收并播放来自远程服务器或其他 UE5 实例的像素流画面。该插件依赖 Pixel Streaming 插件的编解码基础设施（AVCodecs），支持多种像素格式。

⚠️ 该插件当前为 Beta 实验性状态，且默认未启用，需要手动在插件设置中开启。

## 模块概览

| 模块 | 类型 | 说明 |
|---|---|---|
| `PixelStreamingPlayer` | Runtime | 核心运行时模块，负责接收像素流、解码并渲染到游戏画面中 |
| `PixelStreamingPlayerEditor` | Editor | 编辑器模块，提供编辑器内的材质资产支持和相关编辑器功能 |

## 使用场景

- 你需要在 UE5 应用中**播放来自远程服务器的像素流**画面
- 你在做多机协同演示，一台设备推流，另一台设备用本插件接收显示
- 你需要将 Pixel Streaming 画面作为游戏内纹理/材质显示（如虚拟摄像头、监控画面）
- 你使用 Virtual Camera (VCam) 等功能时，底层可能依赖本插件

## 模块依赖

| 模块 | 用途 |
|---|---|
| `PixelStreaming` | 像素流核心插件，提供编解码和 WebRTC 基础设施 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移至新格式 |
| 2026-03-15 | `2caebd20` | Add more missing includes and forward declarations for various rendering headers to files that have | 补充渲染头文件的缺失引用 |
| 2025-08-26 | `0a8b2cd9` | Deprecating the functions RHICreateTextureReference and RHIUpdateTextureReference to force callers t | 废弃 RHI 纹理引用相关函数 |
| 2025-04-10 | `ea97db60` | Movie Render Queue: High-res tiling support for paging scene view state persistent data to system m | 渲染队列高分辨率分页支持 |
| 2024-09-04 | `ffe80807` | [PixelStreaming] Fix: Undeprecate as VCam is still depending on it | 取消废弃：VCam 仍依赖此插件 |

### 维护评价

- **创建时间**：约 3 年（2023 年初）
- **更新频率**：近期有持续更新，但多为编译修复和头文件整理，非功能性更新
- **活跃程度**：被动维护中，无显著功能迭代
- **已知状态**：Beta 实验性插件，默认未启用；有 Virtual Camera 等系统依赖此插件
- **推荐使用**：⚠️ 谨慎使用。作为实验性 Beta 插件，API 可能变动。如果你的需求是接收像素流，这是官方唯一的解决方案，但建议关注后续正式版本。如果你只是做推流端，用标准 Pixel Streaming 插件即可。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PixelStreamingPlayer)
- [官方文档](https://docs.unrealengine.com/en-US/Platforms/PixelStreaming/index.html)