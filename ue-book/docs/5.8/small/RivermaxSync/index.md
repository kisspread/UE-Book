# Rivermax Sync

> Adding NVIDIA Rivermax synchronization capabilities for nDisplay

| 属性 | 值 |
|---|---|
| 中文名 | Rivermax 同步 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `RivermaxSync` (Runtime), `RivermaxSyncEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-03-22 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Rivermax/RivermaxSync) | |

## 用途

为 nDisplay 虚拟制片系统添加 NVIDIA Rivermax 媒体同步能力。在 LED 虚拟制片场景中，多个渲染节点（nDisplay cluster）需要严格同步视频输出到 LED 墙，RivermaxSync 利用 NVIDIA Rivermax SDK 提供的低延迟 IP 视频 I/O 技术，实现渲染节点间的帧同步，确保所有显示输出保持一致，避免画面撕裂或时序错乱。

## 使用场景

- 你在使用 nDisplay 进行 LED 虚拟制片，需要多节点精确同步输出 → 用 RivermaxSync
- 你需要通过 NVIDIA Rivermax 硬件/网络进行低延迟视频采集和输出 → 用 RivermaxSync 配合 RivermaxCore/RivermaxMedia
- 你在 Linux 平台上进行虚拟制片渲染输出 → RivermaxSync 支持 Win64 和 Linux

## 模块说明

| 模块 | 类型 | 说明 |
|---|---|---|
| [RivermaxSync](RivermaxSync.md) | Runtime | 核心同步逻辑，提供 Rivermax 帧同步管理和 nDisplay 集成 |
| [RivermaxSyncEditor](RivermaxSyncEditor.md) | Editor | 编辑器支持，提供配置 UI 和设置面板 |

## 模块依赖

该插件本身依赖以下 **插件**（自动启用）：

| 插件 | 用途 |
|---|---|
| `nDisplay` | 虚拟制片多屏渲染系统，RivermaxSync 为其添加同步能力 |
| `RivermaxCore` | NVIDIA Rivermax SDK 核心封装 |
| `RivermaxMedia` | Rivermax 媒体 I/O 功能 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `c7e14abd` | Rivermax: Added linux support for rivermax output | 为 Rivermax 输出添加 Linux 平台支持 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移至 UE_LOGF |
| 2025-09-18 | `d4ef24be` | Rivermax: Fix a possible mod 0 depending on cvar value. | 修复 cvar 值可能导致模零的问题 |
| 2025-09-07 | `cd57697b` | Rivermax: | Rivermax 相关改动（commit 信息截断） |
| 2025-04-06 | `8c1407ab` | Rivermax Plugin Refactor: | Rivermax 插件整体重构 |

### 维护评价

- **状态**: 活跃维护中
- 插件标记为 **Beta（实验性）**，`IsBetaVersion=true`
- 2026 年 4 月仍在更新，最近新增了 Linux 输出支持
- 2025 年 4 月经历了整体重构，代码结构可能有较大变动
- 作为 NVIDIA Rivermax + nDisplay 生态的一部分，与 Epic 虚拟制片战略紧密相关
- **建议**: 适合虚拟制片项目使用，但注意 Beta 状态，API 可能变化

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Rivermax/RivermaxSync)
- [nDisplay 插件文档](https://docs.unrealengine.com/en-US/RenderingAndGraphics/nDisplay)
- [NVIDIA Rivermax 官网](https://developer.nvidia.com/networking/rivermax)