# Android Media Player

> Implements a media player using the Android Media library.

| 属性 | 值 |
|---|---|
| 中文名 | 安卓媒体播放器 |
| 分类 | Media Players |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AndroidMedia` (RuntimeNoCommandlet), `AndroidMediaEditor` (Editor), `AndroidMediaFactory` (RuntimeNoCommandlet) |
| 实验性 | 否 |
| 创建时间 | 2014-11-17 |
| 年龄标签 | 🏛️ 文物（约 11 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AndroidMedia) | |

## 用途

该插件为 Android 平台提供基于原生 Android Media 框架的媒体播放器实现。它解决了在 Android 设备上播放视频、音频等媒体内容的核心需求，特别是处理了与 Android 系统媒体库的集成、线程安全、纹理资源管理等平台特定问题。通过该插件，UE 项目可以在 Android 平台上无缝地播放本地或流媒体视频。

## 使用场景

- 你需要在 Android 设备上播放游戏内的过场动画或背景视频。
- 你正在开发一个 Android 应用，需要集成视频播放功能（如媒体墙、宣传片播放器）。
- 你的项目需要一个原生 Android 媒体播放方案，以获得最佳的兼容性和性能。

## 模块列表

- **`AndroidMedia`**: 核心运行时模块，封装 Android Media 库，提供 `UAndroidMediaMediaPlayer` 等媒体播放器实现。
- **`AndroidMediaEditor`**: 编辑器模块，提供 `UAndroidMediaSettings` 等用于配置和调试的编辑器专用功能。
- **`AndroidMediaFactory`**: 工厂模块，负责在编辑器和运行时创建具体的 `UAndroidMediaMediaPlayerFactory` 实例。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AndroidMedia)
- [官方文档](https://forums.unrealengine.com/showthread.php?46879-Media-Framework-Documentation-for-4-5-Preview)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AndroidMedia/Tests)

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移至新的 UE_LOGF 格式。 |
| 2026-02-05 | `d5be7e14` | Fixed printfs. | 修复打印语句（通常指日志或调试输出）。 |
| 2025-10-30 | `a0e12af6` | Ran UnrealCodeFixup on Engine to change all ~Type() {} to instead be ~Type() = default | 批量重构，将显式空析构函数改为编译器默认生成。 |
| 2025-08-29 | `32884de4` | Changing more uses of RHICreateTexture to RHICmdList.CreateTexture. | 持续将旧版 RHI 纹理创建 API 迁移至命令列表版本。 |
| 2025-06-18 | `79ad0f74` | Updated CameraPlayer14 to Camera2 API. | 将摄像机播放器从已弃用的 Camera1 API 迁移至 Camera2 API。 |

### 维护评价

该插件创建于 2014 年，历史非常悠久。从近期的更新记录看，其维护重点已从功能开发转向**底层兼容性维护和代码现代化**（如日志系统迁移、RHI API 更新、弃用 API 替换）。过去一年内的更新均为技术性维护，没有新增业务功能。考虑到其作为 Android 平台核心媒体组件的角色，这种维护模式是合理的，旨在确保其在现代引擎版本和新 Android 版本上的正常工作。**推荐继续使用**，但应预期不会有频繁的功能性更新。