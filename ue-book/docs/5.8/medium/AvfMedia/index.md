# AVF Media Player

> Implements a media player using Apple AV Foundation.

| 属性 | 值 |
|---|---|
| 中文名 | AVF媒体播放器 |
| 分类 | Media Players |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AvfMedia` (Runtime), `AvfMediaEditor` (Editor), `AvfMediaFactory` (Runtime, Editor), `AvfMediaCapture` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2014-09-16 |
| 年龄标签 | 🏛️ 文物（约 12 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AvfMedia) | |

## 用途

AvfMedia 是 Unreal Engine 媒体框架在 Apple 平台（iOS, macOS, tvOS）上的核心播放后端实现。它通过封装 Apple 的原生 AV Foundation 框架，为 UE 应用提供了高性能的媒体（视频/音频）解码、渲染和播放能力。该插件解决在 Apple 设备上播放本地或流媒体内容、捕获摄像头画面等媒体相关需求。

## 使用场景

*   你需要在 **iOS 或 macOS** 上的游戏或应用内播放过场动画、背景视频或用户生成内容。
*   你的跨平台项目需要一套统一的媒体播放接口，但在 Apple 设备上需要依赖原生框架以获得最佳性能和兼容性。
*   你需要在 **iOS 应用**中捕获摄像头视频流，并将其作为媒体源在引擎中处理或显示。

## 模块总览

该插件由四个模块组成，共同提供完整的媒体播放与捕获功能：

| 模块 | 类型 | 说明 |
|---|---|---|
| **AvfMedia** | Runtime | 核心运行时模块，封装 AV Foundation 的媒体播放器、音视频解码和渲染。 |
| **AvfMediaFactory** | Runtime/Editor | 工厂模块，负责向引擎注册 AVF 媒体播放器，使其可被 `UMediaPlayer` 等组件选用。 |
| **AvfMediaEditor** | Editor | 编辑器模块，提供在编辑器内预览 AVF 支持的媒体文件的功能。 |
| **AvfMediaCapture** | Runtime | 媒体捕获模块，用于在 iOS 和 macOS 上访问摄像头、麦克风等媒体采集设备。 |

## 相关链接

*   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AvfMedia)
*   [官方文档](https://forums.unrealengine.com/showthread.php?46879-Media-Framework-Documentation-for-4-5-Preview)

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `1951db93` | [AvfMedia] Default H.264 file playback to BGRA decode and provide CPU accessible buffer for media fi | H.264 文件默认使用 BGRA 解码并提供 CPU 可访问缓冲区，可能用于特定处理或与旧系统兼容。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志系统迁移，将旧的 `UE_LOG` 宏迁移到新的 `UE_LOGF` 格式。 |
| 2026-04-13 | `b905d146` | Fix/Silence unreachable code warnings | 修复或抑制“无法到达的代码”编译警告。 |
| 2026-04-01 | `39223292` | [AvfMedia] Provide CPU buffer alongside GPU texture when using FAvfMediaCapturePlayer | 媒体捕获播放器现在在提供 GPU 纹理的同时，也提供 CPU 可访问的缓冲区。 |
| 2026-02-05 | `d5be7e14` | Fixed printfs. | 修复了 `printf` 调试输出语句。 |

### 维护评价

**维护状态：活跃维护**

*   **年龄**：插件创建于 2014 年，历史悠久，是 UE 在 Apple 平台媒体支持的基石。
*   **近期活动**：近几个月内有多次提交，内容涵盖**功能改进**（如 CPU 缓冲区支持、解码默认设置调整）、**代码现代化**（日志宏迁移）和**编译修复**。
*   **活跃度**：近期更新表明 Epic Games 仍在积极维护此插件，确保其与新版 UE 和 Xcode 工具链兼容，并持续优化功能。
*   **推荐度**：**强烈推荐**。对于任何需要在 iOS、macOS 或 tvOS 上播放媒体或捕获媒体流的 UE 项目，此插件是**必备且唯一**的官方后端。它稳定、成熟且持续获得维护。