# Mf Media

> Implements a media player using the Microsoft Media Foundation framework. Requires Xbox One or Windows 7 and higher.

| 属性 | 值 |
|---|---|
| 中文名 | MF媒体播放器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MfMedia` (RuntimeNoCommandlet), `MfMediaEditor` (Editor), `MfMediaFactory` (Editor), `MfMediaFactory` (RuntimeNoCommandlet) |
| 实验性 | 否 |
| 创建时间 | 2017-01-25 |
| 年龄标签 | 🏛️ 文物（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MfMedia) | |

## 用途

MfMedia 是一个基于 Microsoft Media Foundation (MFM) 框架的媒体播放器插件。它为 UE5 提供了在 Windows 和 Xbox One 平台上播放音视频媒体的能力。该插件封装了底层的 Media Foundation API，使其能够通过 UE 标准的 Media Player 接口进行媒体解码、播放和控制。

插件存在的主要原因是为 UE 提供一个原生的、高性能的 Windows 平台媒体播放方案。与其他跨平台媒体框架（如 FFmpeg）相比，Media Foundation 能更好地利用 Windows 系统的硬件加速和编解码器资源。

## 使用场景

- **游戏内过场动画播放**：在 Windows 或 Xbox One 平台的游戏中，使用 Media Player 蓝图播放预渲染的过场动画视频。
- **实时视频流显示**：将摄像头输入或屏幕捕捉的视频流，通过 Media Texture 显示在游戏世界的场景中。
- **UI 视频广告**：在 UI 界面中嵌入视频广告或宣传视频，并提供播放控制。
- **需要硬件解码的高性能视频**：对于 4K 或高帧率视频，利用系统 Media Foundation 的硬件解码能力以降低 CPU 占用。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| `MfMedia` | RuntimeNoCommandlet | 核心运行时模块，封装 Media Foundation 播放器、会话和拓扑管理。 |
| `MfMediaEditor` | Editor | 编辑器支持模块，提供媒体资产的预览和细节面板属性自定义。 |
| `MfMediaFactory` | Editor/ RuntimeNoCommandlet | 工厂模块，用于创建和注册 MfMedia 播放器实例，在编辑器和特定平台运行时加载。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF。 |
| 2025-10-30 | `a0e12af6` | Ran UnrealCodeFixup on Engine to change all ~Type() {} to instead be ~Type() = default | 批量将析构函数体改为 `= default`。 |
| 2025-09-25 | `94af5100` | Replaced PREPROCESSOR_TO_STRING with UE_STRINGIZE. | 使用 UE_STRINGIZE 替换旧的宏。 |
| 2025-06-20 | `642aa84c` | Fix PVS warnings | 修复了潜在视觉系统（PVS）的编译警告。 |
| 2025-02-18 | `0ecd6846` | Media: reworking the timestamp associated sequence index | 重新设计了媒体时间戳与序列索引的关联逻辑。 |

### 维护评价

该插件创建于 2017 年，属于 **文物级** 组件。从近期提交记录看，虽然仍有维护，但多为代码规范化和底层 API 更新（如日志宏迁移、析构函数写法统一），而非功能增强或新特性开发。最近一次功能性改动（`0ecd6846`）也距今超过一年。

**总体评价**：
- **维护不活跃**：核心功能稳定，长期无重大更新。
- **平台限制**：**默认禁用**，且仅支持 Windows 和 Xbox One，不具备跨平台能力。
- **使用建议**：如果你的项目**仅针对 Windows/Xbox One** 平台，且需要原生的 Media Foundation 支持（例如需要与特定 Windows 编解码器集成），可以使用。否则，更推荐使用跨平台的 `WmfMedia` (Windows) 或 `AvfMedia` (Apple) 插件，或者基于 FFmpeg 的 `FFMPEGMedia` 插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MfMedia)
- [官方文档](https://forums.unrealengine.com/showthread.php?46879-Media-Framework-Documentation-for-4-5-Preview)