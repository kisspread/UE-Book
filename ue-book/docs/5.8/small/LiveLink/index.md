# Live Link

> LiveLink allows streaming of animated data into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | 实时数据链接 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、图表节点） |
| 模块 | `LiveLink` (Runtime), `LiveLinkComponents` (Runtime), `LiveLinkEditor` (Runtime), `LiveLinkGraphNode` (Runtime), `LiveLinkMovieScene` (Runtime), `LiveLinkMultiUser` (Runtime), `LiveLinkSequencer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-02-27 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/LiveLink) | |

## 用途

Live Link 是 UE 的实时数据流框架，用于将外部设备或应用程序产生的动画数据（骨骼、变换、相机、灯光等）实时传输到引擎中。它是连接动作捕捉系统、虚拟摄像机、面部捕捉、Vicon/ OptiTrack 等专业硬件与 Unreal Engine 的核心桥梁。

该插件解决的核心问题：
- **外部数据标准化接入**：定义统一的 Live Link Subject 协议，任何数据源只需实现 Provider 即可向引擎推送数据
- **多源并发管理**：支持同时连接多个数据源（如身体动捕 + 面部捕捉 + 虚拟摄像机），各 Subject 独立运行
- **引擎各系统集成**：通过专门模块将实时数据接入动画蓝图、Sequencer、MovieScene、多用户协作等系统
- **编辑器调试**：提供 Live Link Client 面板用于监控数据源状态、预览 Subject 内容

**注意**：`EnabledByDefault=false`，需要在 Plugins 面板手动启用。

## 使用场景

- 你在做虚拟制片，需要将 Vicon/Mo-Sys 的动捕数据实时驱动虚拟角色 → 用 Live Link + LiveLinkComponents
- 你需要在 Sequencer 中录制并回放 Live Link 数据流 → 用 LiveLinkSequencer + LiveLinkMovieScene
- 你在多用户虚拟制片场景中需要同步 Live Link 数据 → 用 LiveLinkMultiUser
- 你需要通过蓝图创建自定义的 Live Link 数据源 → 用 LiveLinkGraphNode
- 你需要将 iPhone ARKit 面部追踪数据导入引擎驱动 MetaHuman → 用 Live Link 接收 ARKit Face Tracking Provider

## 模块总览

| 模块 | 说明 |
|---|---|
| **LiveLink** | 核心模块：定义 Live Link 协议、Subject、Source、Provider 基础架构，实现数据流的传输与管理 |
| **LiveLinkComponents** | 提供可附加到 Actor 的 Live Link 组件（变换组件、虚拟摄像机组件等），在运行时自动接收并应用 Subject 数据 |
| **LiveLinkEditor** | 编辑器模块：提供 Live Link Client 面板 UI，用于连接数据源、监控 Subject、预览数据 |
| **LiveLinkGraphNode** | 蓝图图表模块：提供自定义蓝图节点，支持在蓝图中创建和管理 Live Link Source/Subject |
| **LiveLinkMovieScene** | MovieScene 集成：将 Live Link 数据作为 Sequencer 轨道，支持录制、回放和关键帧编辑 |
| **LiveLinkMultiUser** | 多用户协作：在 Multi-User Editing 环境中同步 Live Link 数据，确保所有客户端接收相同的数据流 |
| **LiveLinkSequencer** | Sequencer 集成：提供 Sequencer 专用的 Live Link 数据录制、缓存和回放功能 |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/LiveLink)
- [Live Link 模块文档](LiveLink.md)
- [Live Link Components 模块文档](LiveLinkComponents.md)
- [Live Link Editor 模块文档](LiveLinkEditor.md)
- [Live Link GraphNode 模块文档](LiveLinkGraphNode.md)
- [Live Link MovieScene 模块文档](LiveLinkMovieScene.md)
- [Live Link MultiUser 模块文档](LiveLinkMultiUser.md)
- [Live Link Sequencer 模块文档](LiveLinkSequencer.md)

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cd46766d` | Fix crash in ULiveLinkBroadcastComponent::PostEditChangeProperty when the broadcast subsystem is una | 修复广播组件在广播子系统不可用时编辑属性导致的崩溃 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度截断为浮点的编译警告 |
| 2026-05-13 | `057dbc69` | Fix crashes in PostEditChangeProperty overrides when MemberProperty is null, which occurs when Pytho | 修复 Python 触发属性变更时 MemberProperty 为空导致的崩溃 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 虚拟制片资产分类调整与迁移 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复格式化函数中作用域枚举导致的乱码输出 |

### 维护评价

Live Link 作为 Epic 的**核心虚拟制片基础设施**，处于**活跃维护**状态。近期（2026年5月）仍有持续的功能修复和稳定性改进，涵盖崩溃修复、编译警告清理和格式化输出修正。该插件自 UE 4.19 起从实验性升级为正式功能，至今已有 8 年历史，架构成熟稳定。多个第三方动捕厂商（Vicon、OptiTrack、Xsens、Apple ARKit 等）均提供 Live Link Provider，生态系统完善。**推荐使用**，是连接外部动画数据源的标准方案。