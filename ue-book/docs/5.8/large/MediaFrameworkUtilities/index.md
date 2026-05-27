# Media Framework Utilities

> This plugin provides utility assets and actors designed to simplify the Media Framework setup. It includes access to the the Media Profile editor.

| 属性 | 值 |
|---|---|
| 中文名 | 媒体框架工具 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（媒体工具资产、编辑器扩展） |
| 模块 | `MediaFrameworkUtilities` (Runtime), `MediaFrameworkUtilitiesEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaFrameworkUtilities) | |

## 用途

Media Framework Utilities 是 Epic Games 为 UE 媒体框架（Media Framework）提供的**增强工具集**，核心解决两个问题：

1. **简化设置流程**：原生媒体框架配置复杂（需手动创建播放器、源、纹理等），此插件提供预配置的资产和Actor（如 MediaSource、MediaPlayer 包装器），减少样板代码。
2. **提供媒体配置管理**：包含 Media Profile 编辑器，允许项目创建和切换不同的媒体播放配置（分辨率、编解码器等），适用于需要运行时切换媒体配置的场景（如直播、多平台适配）。

## 使用场景

- 你需要在项目中播放视频流（网络/本地文件），但不想手动处理播放器生命周期 → 用此插件提供的 Actor 简化。
- 你的项目需要根据平台（PC/主机/移动端）或运行时条件（如网络带宽）动态切换视频质量/格式 → 使用 Media Profile 功能。
- 你在开发直播或视频点播应用，需要快速集成不同来源的媒体（摄像头、屏幕捕获、文件）→ 利用工具资产快速搭建。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| `MediaFrameworkUtilities` | Runtime | 核心运行时工具，提供简化的媒体播放器Actor和资产类 |
| `MediaFrameworkUtilitiesEditor` | Runtime | 编辑器扩展，包含 Media Profile 编辑器界面和资产创建向导 |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaFrameworkUtilities)
- [官方文档](https://docs.unrealengine.com/en-US/InteractiveExperiences/MediaFramework/)（媒体框架整体文档）
- 子模块文档：
  - [MediaFrameworkUtilities.md](MediaFrameworkUtilities.md)
  - [MediaFrameworkUtilitiesEditor.md](MediaFrameworkUtilitiesEditor.md)