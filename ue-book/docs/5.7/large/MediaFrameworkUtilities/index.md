# Media Framework Utilities

> Utility assets and actors to ease the use of the Media Framework.

| 属性 | 值 |
|---|---|
| 中文名 | 媒体框架工具集 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、配置文件） |
| 模块 | `MediaFrameworkUtilities` (Runtime), `MediaFrameworkUtilitiesEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-09-26 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/MediaFrameworkUtilities) | |

## 总体用途

Media Framework Utilities 提供了一系列实用资产和 Actor，用于简化媒体框架的使用。核心功能包括：

- **媒体配置文件（Media Profile）**：集中管理媒体源、输出和捕捉设置，支持运行时切换与保存。
- **媒体捕捉管理**：自动处理媒体源的生命周期（启动/停止），并修复 PIE 切换时的崩溃问题。
- **媒体 IO 工具**：扩展 AJA / SDI 等硬件媒体的参数刷新、属性保存等操作。

该插件旨在将原本分散的媒体设置整合为可复用、可保存的配置文件，降低手动配置的复杂度和出错率。

## 模块列表

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| [MediaFrameworkUtilities](MediaFrameworkUtilities.md) | Runtime | 核心运行时模块，提供媒体配置文件（MediaProfile）的播放管理与捕捉控制逻辑。 |
| [MediaFrameworkUtilitiesEditor](MediaFrameworkUtilitiesEditor.md) | Runtime | 编辑器模块，提供媒体配置文件的创建、编辑、保存功能，以及媒体 IO 设置的 UI 和属性处理。 |

## 使用场景

- 需要为直播、录播或多机位制作配置多个媒体源（如摄像头、视频采集卡），并希望保存/切换不同场景的媒体设置。
- 自动化媒体捕捉流程，避免手动启停媒体源。
- 使用 AJA / SDI 等硬件媒体时，需要简化和持久化设备的参数配置。

## 维护状态

### 近期更新

- 2026-01-23 b00fe8fa — Media Profile: Fix for crash caused by attempting to capture from camera spawned in by PIE after PIE
- 2026-01-23 b7b05be8 — Media Profile: Fixed issue where active media sources would get stopped whenever PIE was exited
- 2025-10-17 ab15e769 — Media IO - Fix crash when refreshing media properties for Aja source
- 2025-10-01 abe973bc — Media Profile: Created variant of media capture settings for media profile that can properly be saved
- 2025-09-26 0f143d8f — Media Profile: Moved media capture management from media profile editor into media profile playback

### 维护评价

该插件自 2025 年 9 月创建以来（约 4 个月），已有多次功能更新和关键 Bug 修复，最近一次 commit 为 2026 年 1 月 23 日，维护非常活跃。当前版本已能稳定处理媒体配置文件的保存与加载、PIE 时的媒体源生命周期管理，以及 AJA 源的属性刷新。无已知废弃或限制标记，推荐在新项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/MediaFrameworkUtilities)