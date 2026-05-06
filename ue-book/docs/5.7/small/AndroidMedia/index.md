# Android Media Player

> Implements a media player using the Android Media library.

| 属性 | 值 |
|---|---|
| 中文名 | 安卓媒体播放器 |
| 分类 | Media Players |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AndroidMedia` (Runtime), `AndroidMediaEditor` (Editor), `AndroidMediaFactory` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-03-28 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AndroidMedia) | |

---

## 总体用途

Android Media Player 插件利用 Android 原生 Media API 实现媒体播放功能。它封装了 Android 平台上的媒体解码、渲染和控制逻辑，使 UE 项目能够在 Android 设备上无缝播放本地或网络音视频资源。该插件通过工厂模式提供跨模块的播放器实例创建，并通过编辑器模块暴露基本配置选项，开发者无需直接编写 JNI 代码即可集成安卓媒体播放。

---

## 模块列表

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| AndroidMedia | Runtime | 核心运行时模块，封装 Android 媒体播放器的创建、播放控制与渲染。 |
| AndroidMediaEditor | Editor | 编辑器模块，提供平台设置与播放器配置界面。 |
| AndroidMediaFactory | Runtime | 工厂模块，依据平台和设备能力自动选择并创建合适的媒体播放器实现。 |

每个模块的详细文档请参见：
- [AndroidMedia 模块](AndroidMedia.md)
- [AndroidMediaEditor 模块](AndroidMediaEditor.md)
- [AndroidMediaFactory 模块](AndroidMediaFactory.md)

---

## 使用场景

- 你正在开发一款 Android 平台游戏，需要嵌入过场动画、宣传视频或动态背景。
- 你的应用需要播放 Android 设备本地存储的视频文件，或通过 HTTP(s) 流式播放在线媒体。
- 你需要一个开箱即用的媒体播放器，无需额外配置第三方 SDK。
- 你在编辑器中预览媒体资源或调整播放参数。

---

## 维护状态

### 近期更新

| 日期 | Hash | 说明 |
|---|---|---|
| 2025-08-29 | `32884de4` | 将更多 RHICreateTexture 调用迁移至 RHICmdList.CreateTexture |
| 2025-06-18 | `79ad0f74` | 将 CameraPlayer14 更新为 Camera2 API |
| 2025-05-31 | `52e3acd1` | 使用 UnrealCodeFixup 更新头文件以确保 DLL storage 正确 |
| 2025-04-10 | `ea97db60` | Movie Render Queue 高分辨率平铺支持: 将场景视图状态持久数据分页到系统内存 |
| 2025-03-28 | `b892a182` | 为 MediaPlayer14 新增 BitmapRenderer |

### 维护评价

该插件创建于 2025 年 3 月，至今约半年，仍处于早期活跃阶段。最近的提交涉及 API 适配（Camera2）、性能优化（RHICmdList）和基础设施升级，表明开发团队正在积极维护并使其与引擎其他部分保持同步。插件功能核心稳定，暂无废弃标记或已知重大问题。由于推出时间较短，可能仍存在边缘 bug，但整体推荐在 Android 媒体播放需求中使用。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AndroidMedia)
- [官方论坛文档](https://forums.unrealengine.com/showthread.php?46879-Media-Framework-Documentation-for-4-5-Preview)（较旧，仅供参考）
- [模块源码 - AndroidMedia](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Media/AndroidMedia/Source/AndroidMedia)
- [模块源码 - AndroidMediaEditor](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Media/AndroidMedia/Source/AndroidMediaEditor)
- [模块源码 - AndroidMediaFactory](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Media/AndroidMedia/Source/AndroidMediaFactory)