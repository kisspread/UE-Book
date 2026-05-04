# Motion Design For nDisplay

> Motion Design Synchronization extensions for nDisplay clustering

| 属性 | 值 |
|---|---|
| 分类 | Experimental |
| 默认启用 | false |
| 包含内容 | true |
| 模块 | AvalancheDisplayCluster (Runtime) |
| 创建时间 | 2024-06-15 |
| 年龄标签 | 🆕 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/AvalancheDisplayCluster) | |

## 用途

AvalancheDisplayCluster 为 Motion Design（Avalanche Media）系统在 nDisplay 多机集群环境下提供**同步事件分发机制**。它解决的核心问题是：在 nDisplay 集群中，多个渲染节点（Node）需要在完全相同的时刻执行某个事件（如播放媒体、切换场景），但各节点的事件产生时机可能存在几帧的偏差。本 plugin 通过 nDisplay 的 Cluster Event 二进制通信机制，实现了一个"等所有节点都就绪后再统一执行"的同步协议。

简而言之：**让 Motion Design 的媒体播放在 nDisplay 多屏/多机集群上帧同步**。

## 使用场景

- 你使用 Motion Design（Avalanche Media）制作 LED 墙/投影映射内容，部署在 nDisplay 集群上 → 需要本 plugin 保证所有节点同时触发播放事件
- 你的 nDisplay 集群中有多台机器各自渲染部分内容，需要媒体内容（视频、动画）在所有节点上精确同步 → 本 plugin 提供底层同步保障
- 你在做虚拟制片（Virtual Production），使用 nDisplay 驱动多块 LED 屏幕，Motion Design 内容需要跨屏同步 → 启用本 plugin

**前提条件**：需要同时启用 **Avalanche** 和 **nDisplay** 两个 plugin。

## 蓝图用法

本 plugin 不暴露任何蓝图可调用接口。它是一个纯 Runtime 模块，通过 Modular Feature 模式自动注册到 Avalanche Media 的同步事件系统中，无需用户在蓝图中直接操作。

## C++ 用法

本 plugin 主要作为"即插即用"模块工作。启用后，Avalanche Media 系统会自动发现并使用 `IAvaMediaSynchronizedEventsFeature` 的 nDisplay 实现。

### 头文件引入

本 plugin 的所有类均为 `Private`，不对外暴露公共头文件。外部使用者不应直接引用本模块的头文件——它是 Avalanche Media 同步系统的内部实现。

### 架构概览

整个 plugin 由以下核心组件构成：

#### 1. 模块入口：`FAvaDisplayClusterModule`

启动时注册一个 `FAvaDisplayClusterSynchronizedEventsFeature` 作为 Modular Feature，使 Avalanche Media 系统可以发现并使用 nDisplay 同步实现。

#### 2. 同步事件特性：`FAvaDisplayClusterSynchronizedEventsFeature`

实现 `IAvaMediaSynchronizedEventsFeature` 接口，负责：
- 注册为 nDisplay 集群的二进制事件监听器
- 创建和管理 `FAvaDisplayClusterSynchronizedEventDispatcher` 实例
- 将接收到的集群事件路由到正确的 Dispatcher
- 处理 Dispatcher 尚未创建时的"追踪事件"（Tracking Events）

#### 3. 同步事件分发器：`FAvaDisplayClusterSynchronizedEventDispatcher`

核心同步逻辑所在，实现 `IAvaMediaSynchronizedEventDispatcher` 接口。工作流程：

1. **PushEvent** — 本地节点产生一个事件，通过 Cluster Event 广播给所有节点
2. **等待确认** — 每个收到事件的节点会广播自己的确认
3. **全部就绪** — 当所有节点都确认后，事件进入 Ready 状态
4. **Dispatch** — 在下一帧统一执行事件回调

对于特殊情况的处理：
- 如果某个节点的确认先于本地事件到达，会先记录到 `TrackedEvents` 中
- 如果等待超时（默认 5 秒），事件会被强制执行
- 如果 Cluster Event 丢失，会自动重发（默认每 200ms 重发一次）

#### 4. 时间戳工具：`FAvaDisplayClusterTimeStamp`

记录事件产生时的系统时间和帧号，用于超时计算和调试日志。

### 控制台变量

| CVar | 默认值 | 说明 |
|---|---|---|
| `AvaDisplayCluster.Sync.EarlyDispatch` | `false` | 设为 `true` 时，事件就绪后立即执行（可提前 1 帧）；`false` 时在下一 tick 批量执行 |
| `AvaDisplayCluster.Sync.DispatchTimeout` | `5000` ms | 等待所有节点确认的超时时间。超时后强制执行事件 |
| `AvaDisplayCluster.Sync.RepeatTimeout` | `200` ms | 重新广播 Cluster Event 的间隔。用于应对事件丢失的情况 |
| `AvaDisplayCluster.Sync.TrackingTimeout` | `5000` ms | 追踪事件的过期时间。超过此时间的追踪事件会被丢弃 |

### 日志

- `LogAvaDisplayCluster` — 模块级日志
- `LogAvaDisplayClusterSyncEvents` — 同步事件详细日志（设为 Verbose 可看到每个事件的广播/确认/执行过程）

## Demo 示例

本 plugin 无法独立使用，它是 Avalanche Media + nDisplay 集成的一部分。典型使用流程：

### 1. 启用 Plugin

在项目的 `.uproject` 文件或编辑器的 Plugins 面板中启用：
- `Avalanche`（Motion Design）
- `nDisplay`
- `AvalancheDisplayCluster`

### 2. 配置 nDisplay 集群

配置你的 nDisplay 集群拓扑（多个渲染节点），确保 Cluster Event 通信正常工作。

### 3. 使用 Motion Design

正常使用 Motion Design 系统创建媒体播放内容。当 nDisplay 集群模式激活时，本 plugin 会自动接管同步事件分发，确保所有节点上的媒体播放同步执行。

### 4. 调试

如果遇到同步问题，可以在控制台中调整参数：

```
// 查看详细同步日志
Log LogAvaDisplayClusterSyncEvents Verbose

// 缩短超时（适用于高帧率场景）
AvaDisplayCluster.Sync.DispatchTimeout 2000

// 启用即时分发（减少 1 帧延迟）
AvaDisplayCluster.Sync.EarlyDispatch true
```

## 模块依赖

### Plugin 依赖

| Plugin | 用途 |
|---|---|
| `Avalanche` | Motion Design 媒体播放系统（提供 `IAvaMediaSynchronizedEventsFeature` 接口） |
| `nDisplay` | 多屏/多机集群渲染（提供 Cluster Event 通信机制） |

### 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础引擎功能（Public） |
| `AvalancheMedia` | Motion Design 媒体播放和同步事件接口 |
| `DisplayCluster` | nDisplay 集群管理和 Cluster Event 系统 |
| `Engine` | 引擎核心功能 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2024-11-05 | `cb903fb` | Fix Installed Build generation failure caused by AvalancheDisplayCluster | 修复打包构建问题，属于构建系统兼容性修复 |
| 2024-06-15 | `3d84215` | Fix CIS 498201 - nDisplay not supported on Mac | 修复平台兼容性：Mac 不支持 nDisplay 的编译问题 |
| 2024-06-15 | `2f604ce` | Display Cluster synchronization support for Level Streaming Playable | 初始提交，实现了核心同步事件功能 |

### 维护评价

- **创建时间**：2024-06-15，约 1.9 年前
- **更新频率**：创建后仅 2 次后续修复（均为构建/平台兼容性修复），无功能性更新
- **维护状态**：**维护不活跃** — 自创建以来没有实质性功能迭代
- **稳定性**：代码结构清晰，但有多个 TODO 注释表明仍在开发中
- **推荐**：仅在明确需要 nDisplay + Motion Design 集成的场景下使用。作为 Experimental 插件，API 和行为可能随版本变化。生产环境使用需谨慎评估。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/AvalancheDisplayCluster)
- 官方文档：无（`.uplugin` 中 DocsURL 为空）
- [Avalanche (Motion Design) Plugin](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Avalanche)
- [nDisplay Plugin](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/DisplayCluster)
