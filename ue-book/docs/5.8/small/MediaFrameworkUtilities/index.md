# Media Framework Utilities

> This plugin provides utility assets and actors designed to simplify the Media Framework setup. It includes access to the the Media Profile editor.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 媒体框架工具集 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器资产、蓝图类） |
| 模块 | `MediaFrameworkUtilities` (Runtime), `MediaFrameworkUtilitiesEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaFrameworkUtilities) | |

## 用途

该插件是 UE 内置媒体播放框架（Media Framework）的**工具箱**，旨在解决媒体播放系统设置复杂、配置繁琐的问题。它将底层的媒体播放器、采样器等组件封装为更易用的编辑器资产（如 MediaProfile）和预设的蓝图演员，让开发者能快速搭建视频播放、实时视频输入等媒体功能，而无需手动配置每一个细节。

## 使用场景

-   **直播或实时视频输入**：你需要快速接入 Blackmagic 或 AJA 等专业视频采集卡 → 使用此插件的 MediaProfile 配置自动填充功能。
-   **展会/演示项目**：需要在多个场景或关卡中复用同一套媒体播放设置（分辨率、编码器等） → 创建并应用 MediaProfile 资产进行统一管理。
-   **简化媒体演员放置**：不想每次都在场景中手动拖拽和配置 MediaSource、MediaPlayer、MediaTexture 等一整套组件 → 使用插件提供的预设蓝图演员（如 `BP_MediaFrameworkUtilities_MediaActor`）。
-   **编辑器集成**：希望在编辑器窗口中有一个便捷的“媒体”菜单来快速访问媒体配置和播放工具。

## 模块列表

| 模块 | 说明 |
|---|---|
| `MediaFrameworkUtilities` | 提供核心运行时类，如 `MediaProfile` 资产和用于简化媒体播放的蓝图工具函数。 |
| `MediaFrameworkUtilitiesEditor` | 提供编辑器扩展，包括 Media Profile 编辑器、相关的资产创建工厂和编辑器内工具窗口。 |

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaFrameworkUtilities)
-   [官方文档](https://docs.unrealengine.com/en-US/WorkingWithMedia/MediaFramework/)（Media Framework 主页）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `36c08694` | Media IO - Populate Media Configuration when using auto for Blackmagic and Aja cards | 使用 Blackmagic/Aja 卡的自动模式时，自动填充媒体配置 |
| 2026-05-22 | `7d256b73` | [Media] Add shared Media category to the Level Editor Window menu | 在关卡编辑器窗口菜单中添加了共享的“媒体”类别 |
| 2026-05-21 | `ff9996e8` | Media Profile: Fixed issue where ElectraProtron issue would not play a new video after it had alread | 修复 Media Profile 中 Electra 播放器播放过视频后无法播放新视频的问题 |
| 2026-05-20 | `54cbb9f8` | Ensure a transient MediaProfile always exists from startup | 确保启动时始终存在一个临时 MediaProfile |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构视口代码，通过通知机制减少重复代码 |

### 维护评价

-   **活跃维护**：插件创建于约 7 年前，但近期（2026年5月）仍有**高频次的功能增强和 Bug 修复**，表明它仍在积极维护中，以适应新的媒体硬件（Blackmagic/Aja）和引擎功能。
-   **功能完善**：主要围绕 **MediaProfile** 资产和**编辑器集成**进行迭代，目标是进一步简化媒体工作流。
-   **无已知重大限制**：作为 Epic 官方维护的工具集，与引擎版本兼容性好。
-   **推荐使用**：对于任何需要进行专业视频播放、实时输入或复杂媒体设置的 UE 项目，**强烈推荐启用**此插件。它能显著减少初始设置时间并提高配置的一致性。