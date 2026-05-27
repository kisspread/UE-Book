# Media Profile

> This plugin contains the Media Profile asset and related entities, which help manage media sources and outputs

| 属性 | 值 |
|---|---|
| 中文名 | 媒体配置文件 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（媒体配置资产） |
| 模块 | `MediaProfile` (Runtime), `MediaProfileEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-23 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaProfile) | |

## 用途

Media Profile 插件的核心功能是**将媒体源和输出的管理逻辑封装为一个独立的资产**。它从 OpenCVDistortion 等其他模块中解耦出来，提供一个标准化的方式来定义、存储和管理媒体管线的配置（如输入源、输出目标、播放状态等），而不是硬编码在各个不同的模块中。这样做的主要目的是：
1. **解耦依赖**：避免其他需要媒体功能的模块（如虚拟制片、Composure 合成等）必须依赖特定的媒体处理模块。
2. **配置化管理**：将媒体配置数据资产化，便于在不同场景（如不同拍摄场地、不同节目）间切换和复用。

## 使用场景

- 你需要在虚拟制片（Virtual Production）或实时合成（Compositing）项目中**统一管理视频输入源（如摄像头、SDI）和输出目标**。
- 你需要**为不同的拍摄场景或节目预设不同的媒体配置**（如分辨率、延迟设置），并快速切换。
- 你需要**避免在多个系统间重复和硬编码媒体连接逻辑**，希望将其模块化、资产化。

## 模块概述

| 模块 | 说明 |
|---|---|
| `MediaProfile` | 运行时核心模块，定义 `UMediaProfile` 等资产和管理逻辑。 |
| `MediaProfileEditor` | 编辑器模块，提供 `UMediaProfile` 资产的编辑器界面和操作支持。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-21 | `ff9996e8` | Media Profile: Fixed issue where ElectraProtron issue would not play a new video after it had alread | 修复 ElectraProtron 播放器在已播放视频后无法播放新视频的问题。 |
| 2026-05-20 | `54cbb9f8` | Ensure a transient MediaProfile always exists from startup | 确保从启动时起始终存在一个临时 MediaProfile 配置。 |
| 2026-05-20 | `de6434f1` | Composure: Add final new icons for composite actors, layers, and passes, and minor tweaks to menu co | 为 Composure 合成器的 Actor、图层和通道添加新图标，并微调菜单布局。 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构视口逻辑，通过通知客户端关联/解耦事件来避免重复代码。 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回退了一次提交（具体变更未在此说明）。 |

### 维护评价

- **创建时间**：2026年4月，是一个非常新的插件。
- **维护状态**：**活跃维护**。最近一次更新（修复问题）在2026年5月21日，距今不到一个月。
- **实验性标记**：插件目前标记为 `IsExperimentalVersion = true`，且默认未启用（`EnabledByDefault = false`）。
- **已知限制**：作为实验性功能，API 和功能在未来的引擎版本中可能发生变更或被移除。
- **推荐度**：**谨慎使用**。适合在虚拟制片等需要媒体配置管理的项目中进行探索和测试，但不建议用于需要长期稳定的核心生产流程，除非你准备好跟进 API 的变更。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaProfile)
- [官方文档]() (暂无)