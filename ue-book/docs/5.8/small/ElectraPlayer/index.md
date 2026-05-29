# Electra Player

> Cross platform media player for local files and internet streaming. Also provides optimized local mp4 file only player (Protron) for desktop machines.

| 属性 | 值 |
|---|---|
| 中文名 | Electra 播放器 |
| 分类 | Media Players |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ElectraPlayerFactory` (Runtime), `ElectraPlayerPlugin` (Runtime), `ElectraPlayerPluginHandler` (Runtime), `ElectraPlayerRuntime` (Runtime), `ElectraProtron` (Runtime), `ElectraProtronFactory` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-01-06 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraPlayer) | |

## 用途

ElectraPlayer 是 UE5 内置的**跨平台媒体播放框架**，用于播放本地文件和网络流媒体。它取代了旧的媒体播放器后端，提供统一的媒体解码管线。

插件包含两个独立的播放器引擎：
- **ElectraPlayer**：通用播放器，支持本地文件、HLS/DASH 网络流媒体、字幕、专辑元数据等完整功能。
- **Protron**：针对桌面平台的**高性能本地 MP4 播放器**，利用 D3D12 硬件加速实现零拷贝解码，适合对性能要求极高的场景（如过场视频、背景视频）。

两者通过工厂模式动态注册，框架根据平台能力和请求类型自动选择合适的播放器。

## 使用场景

- 你需要在游戏内播放过场动画视频 → 使用 Protron（桌面平台最优性能）
- 你需要从网络流式加载 HLS/DASH 视频 → 使用 ElectraPlayer
- 你需要播放本地 MP4/WebM 等格式的媒体文件 → 使用 ElectraPlayer
- 你需要为不同平台提供统一的媒体播放 API → 本插件即为该目的设计

## 模块一览

| 模块 | 类型 | 说明 |
|---|---|---|
| `ElectraPlayerPlugin` | Runtime | 与 UE Media Player 框架的集成层，注册媒体工厂并暴露蓝图/API 接口 |
| `ElectraPlayerRuntime` | Runtime | 核心媒体处理引擎：解封装、解码、同步、缓冲、渲染输出 |
| `ElectraPlayerPluginHandler` | Runtime | 插件加载与生命周期管理，协调 Runtime 与 Plugin 模块 |
| `ElectraPlayerFactory` | Runtime | 工厂模块，负责平台检测和创建 ElectraPlayer 实例 |
| `ElectraProtron` | Runtime | 桌面专用高性能 MP4 播放器，基于 D3D12 硬件加速 |
| `ElectraProtronFactory` | Runtime | Protron 工厂模块，检测平台能力并创建 Protron 实例 |

## 子模块文档

| 模块 | 文档 |
|---|---|
| ElectraPlayerFactory | [ElectraPlayerFactory.md](ElectraPlayerFactory.md) |
| ElectraPlayerPlugin | [ElectraPlayerPlugin.md](ElectraPlayerPlugin.md) |
| ElectraPlayerPluginHandler | [ElectraPlayerPluginHandler.md](ElectraPlayerPluginHandler.md) |
| ElectraPlayerRuntime | [ElectraPlayerRuntime.md](ElectraPlayerRuntime.md) |
| ElectraProtron | [ElectraProtron.md](ElectraProtron.md) |
| ElectraProtronFactory | [ElectraProtronFactory.md](ElectraProtronFactory.md) |

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ElectraBase` | Electra 基础库，提供公共类型和工具 |
| `DirectX` | DirectX 头文件与类型定义 |
| `D3D12RHI` | Direct3D 12 渲染硬件接口（Protron 零拷贝解码） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-21 | `ff9996e8` | Media Profile: Fixed issue where ElectraProtron issue would not play a new video after it had alread | 修复 Protron 播放完毕后无法播放新视频的问题 |
| 2026-05-14 | `d15b78b3` | ElectraPlayer: Fixed streamed album metadata | 修复流媒体专辑元数据解析问题 |
| 2026-05-13 | `4340cfa6` | ElectraPlayer: Added configuration and cvars to control if decoders need to be suspended during play | 新增配置项控制播放期间是否挂起解码器 |
| 2026-05-12 | `a6372743` | ElectraPlayer: changed an assertion to an if() condition to handle cases where .ts internal timestam | 修复 TS 流内部时间戳异常导致的断言崩溃 |
| 2026-05-12 | `e3746831` | ElectraPlayer: Checking for sequence index when prefetching subtitle media segments to reduce unnece | 优化字幕预取逻辑，减少不必要的网络请求 |

### 维护评价

**活跃维护** ✅

ElectraPlayer 是 Epic 自研的核心媒体播放框架，自 2021 年从内部项目（NFL 标注）迁移至公开仓库后持续活跃维护。最近一次更新在 2026 年 5 月，短期内连续修复多个播放问题并新增功能配置项，说明仍在积极迭代。作为 UE 内置的默认媒体播放后端，预计将持续随引擎版本更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraPlayer)
- [官方文档](https://docs.unrealengine.com/en-US/Engine/MediaFramework/Overview)