# Live Link Over nDisplay

> LiveLink subjects synchronization for nDisplay setup

| 属性 | 值 |
|---|---|
| 分类 | Misc |
| 默认启用 | ❌ `EnabledByDefault: false` |
| 包含内容 | ❌ `CanContainContent: false` |
| 模块 | LiveLinkOverNDisplay (Runtime) |
| 创建时间 | 2019-11-20 |
| 年龄标签 | 👴 老古董（>5年） |
| 支持平台 | Win64, Linux |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/LiveLinkOverNDisplay) | |

## 用途

在 nDisplay 多机集群（Cluster）环境下，解决 **LiveLink 数据在各节点间的同步问题**。

nDisplay 允许将 Unreal Engine 渲染分布到多台机器上（例如 LED Volume、多投影幕等），每台机器（称为 Agent/Secondary 节点）需要显示完全一致的内容。LiveLink 是 UE 的实时数据传输框架（动捕、面部追踪、摄像机跟踪等），但默认情况下每台机器各自接收 LiveLink 数据，可能因网络延迟、数据源连接状态不同而导致各节点画面不一致。

本插件通过 nDisplay 的 **SyncObject 机制**，让 Controller（主控节点）在每帧将所有 LiveLink Subject 的帧数据序列化后广播给所有 Agent 节点。Agent 收到数据后创建对应的 **Virtual Subject**（虚拟主题）来替代原始数据源，确保集群中所有机器使用完全相同的 LiveLink 数据。

## 使用场景

- 你在使用 **nDisplay + LiveLink** 做虚拟制片（Virtual Production）→ 本插件保证动捕/面捕数据在所有渲染节点上同步
- 你有一个 **LED Volume 多机器集群**，需要所有机器的摄像机跟踪数据一致 → 启用本插件即可自动同步
- 你在做 **多投影融合**（CAVE），LiveLink 驱动的追踪数据需要在所有节点上同步 → 本插件解决这个问题
- 你需要在集群中 **Failover（故障切换）** 后保持 LiveLink 数据正常 → 本插件支持主节点切换后自动重新初始化

## 蓝图用法

本插件 **没有暴露任何蓝图节点**。它是一个纯运行时（Runtime）插件，通过 nDisplay 的 SyncObject 机制在后台自动工作。启用后无需手动配置蓝图。

配置唯一入口是 **Project Settings** 面板中的开关。

## 编辑器设置

在编辑器中可通过 **Project Settings → Plugins → LiveLink over nDisplay** 进行配置：

| 设置项 | 类型 | 说明 |
|---|---|---|
| `bIsEnabled` | `bool` | 是否启用 LiveLink over nDisplay 同步。默认 `true`（在插件启用的情况下） |

## C++ 用法

### 头文件引入

```cpp
#include "ILiveLinkOverNDisplayModule.h"
#include "NDisplayLiveLinkSubjectReplicator.h"
```

### 检查插件是否可用

```cpp
// 检查模块是否已加载
if (ILiveLinkOverNDisplayModule::IsAvailable())
{
    // 获取 Replicator 实例
    FNDisplayLiveLinkSubjectReplicator& Replicator = 
        ILiveLinkOverNDisplayModule::Get().GetSubjectReplicator();
    
    if (Replicator.IsActive())
    {
        // Replicator 正在运行，LiveLink 数据正在被同步
    }
}
```

> 来源: `ILiveLinkOverNDisplayModule.h` — `Get()` 和 `IsAvailable()` 静态方法

### 命令行覆盖

通过命令行参数可以覆盖项目设置中的启用状态：

```bash
# 启用
UnrealEditor.exe -EnableLiveLinkOverNDisplay=true

# 禁用
UnrealEditor.exe -EnableLiveLinkOverNDisplay=false
```

> 来源: `LiveLinkOverNDisplaySettings.cpp` — `ULiveLinkOverNDisplaySettings` 构造函数解析命令行

### 访问 Replicator

```cpp
// 通过模块接口获取 Replicator
ILiveLinkOverNDisplayModule& Module = ILiveLinkOverNDisplayModule::Get();
FNDisplayLiveLinkSubjectReplicator& Replicator = Module.GetSubjectReplicator();

// Replicator 实现了 IDisplayClusterClusterSyncObject 接口
// 它会自动注册到 nDisplay 的 SyncObject 系统中
// SyncId 为 "NDisplayLiveLinkSyncObject"
// 同步组为 EDisplayClusterSyncGroup::PreTick
```

> 来源: `NDisplayLiveLinkSubjectReplicator.cpp` — `Activate()` 和 `GetSyncId()`

## 架构概览

```
┌─────────────────────────────────────────────────────┐
│                    Controller 节点                    │
│                                                       │
│  LiveLink Sources ──► LiveLink Client ──┐             │
│  (动捕/面捕/跟踪)    (EvaluateFrame)    │             │
│                                          ▼             │
│                              OnLiveLinkTicked()       │
│                              序列化所有 Subject 帧数据  │
│                                          │             │
│                              SerializeToString()       │
└──────────────────────────────────────────┼─────────────┘
                                           │
                        nDisplay SyncObject (PreTick)
                                           │
┌──────────────────────────────────────────┼─────────────┐
│                    Agent 节点             ▼             │
│                                                       │
│  DeserializeFromString()                              │
│  反序列化帧数据                                         │
│         │                                             │
│         ▼                                             │
│  ProcessLiveLinkData_Agent()                          │
│  创建/更新 Virtual Subject                              │
│         │                                             │
│         ▼                                             │
│  UNDisplayAgentVirtualSubject                         │
│  (替代原始数据源，供 Actor 绑定)                        │
└───────────────────────────────────────────────────────┘
```

### 核心类

| 类名 | 文件 | 说明 |
|---|---|---|
| `FNDisplayLiveLinkSubjectReplicator` | `NDisplayLiveLinkSubjectReplicator.h/cpp` | 核心同步类。实现 `IDisplayClusterClusterSyncObject` 接口，负责将 Controller 的 LiveLink 数据序列化/反序列化并同步到集群 |
| `UNDisplayAgentVirtualSubject` | `NDisplayAgentVirtualSubject.h/cpp` | Agent 节点上的虚拟 LiveLink Subject。继承 `ULiveLinkVirtualSubject`，接收 Controller 传来的帧数据 |
| `ULiveLinkOverNDisplaySettings` | `LiveLinkOverNDisplaySettings.h/cpp` | 项目设置类。支持编辑器配置和命令行覆盖 |
| `FLiveLinkOverNDisplayModule` | `LiveLinkOverNDisplayModule.h/cpp` | 模块入口。注册 nDisplay 场景回调，管理 Replicator 生命周期 |

### 同步帧类型

Replicator 使用三种帧类型来优化带宽：

| 帧类型 | 说明 |
|---|---|
| `DataOnly` | 仅传输帧数据（最常见，Subject 的静态数据和 Role 未变化） |
| `NewSubject` | 新 Subject 首次出现，需要传输完整信息（静态数据 + Role + 帧数据） |
| `UpdatedSubject` | 已有 Subject 的静态数据或 Role 发生变化，需要重新传输静态数据 |

### 生命周期

1. **引擎初始化完成** → `OnEngineLoopInitComplete()` → 初始化 Replicator
2. **nDisplay 场景启动** → `OnDisplayClusterStartScene()` → 激活 Replicator（注册为 SyncObject）
3. **每帧**：
   - Controller: `OnLiveLinkTicked()` → 序列化所有 Subject 帧数据
   - nDisplay PreTick: SyncObject 跨集群同步
   - Agent: `OnEngineBeginFrame()` → 禁用非虚拟 Subject，仅保留复制的 Virtual Subject
4. **nDisplay 场景结束** → `OnDisplayClusterEndScene()` → 停用 Replicator
5. **故障切换** → `OnDisplayClusterPrimaryNodeChanged()` → Agent 升级为 Controller，重新初始化

## Demo 示例

本插件不需要编写代码。以下是一个完整的使用流程：

### 前提条件

1. 已配置 nDisplay 集群（至少 1 个 Controller + 1 个 Agent）
2. 已有 LiveLink 数据源（如动捕设备、面捕摄像头等）

### 步骤

1. **启用插件**：在编辑器中打开 `Edit → Plugins`，搜索 `Live Link Over nDisplay`，勾选启用
2. **重启编辑器**：插件需要重启才能生效
3. **配置设置**：进入 `Project Settings → Plugins → LiveLink over nDisplay`，确保 `bIsEnabled` 为 `true`
4. **正常运行 nDisplay 集群**：插件会自动在后台同步所有 LiveLink Subject

### 验证

在 Agent 节点上，打开 LiveLink 面板（`Window → Live Link`），应该能看到名为 `nDisplaySubjectReplicator` 的虚拟源，其中包含从 Controller 复制过来的所有 Subject。这些 Subject 的数据与 Controller 上的完全一致。

## 模块依赖

从 `LiveLinkOverNDisplay.Build.cs` 提取：

| 模块 | 类型 | 用途 |
|---|---|---|
| `Core` | Public | UE 核心库 |
| `CoreUObject` | Public | UObject 系统 |
| `DisplayCluster` | Private | nDisplay 集群管理（SyncObject、ClusterManager） |
| `Engine` | Private | 引擎核心功能 |
| `LiveLinkInterface` | Private | LiveLink 接口（ILiveLinkClient、Subject 管理） |
| `Settings` | Private (仅编辑器) | Project Settings 面板注册 |

### Plugin 依赖

| 插件 | 说明 |
|---|---|
| `nDisplay` | **必须**。本插件依赖 nDisplay 的集群同步机制 |

> **注意**：虽然 `LiveLinkInterface` 在 `PrivateDependencyModuleNames` 中，但本插件的设计意图是与完整的 LiveLink 插件一起使用。确保 LiveLink 插件也已启用。

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2026-04-13 | `35e60df1bc98` | Migrate UE_LOG to UE_LOGF | 全局日志宏迁移，无功能变化 |
| 2026-04-13 | `ab338b001f3a` | Migrate UE_LOG to UE_LOGF | 同上（可能在不同分支） |
| 2025-12-18 | `75d5bbaeeef9` | [nDisplay] Fixed LivelinkOverNDisplay replication logic in order to support new failover | 修复了 Failover（主节点故障切换）时的复制逻辑，支持 nDisplay 新的 Failover 机制 |

### 维护评价

- **创建时间**：2019 年 11 月（约 6.5 年前）
- **最近更新**：2026 年 4 月（最近一次功能性更新在 2025 年 12 月）
- **活跃度**：维护中。虽然更新不频繁，但 2025 年 12 月有实质性的 Failover 修复，说明仍在配合 nDisplay 的架构演进进行维护
- **已知限制**：
  - 仅支持 Win64 和 Linux 平台
  - 需要 nDisplay 以 Cluster 模式运行才生效
  - `EnabledByDefault: false`，需要手动启用
  - 使用字符串序列化传输数据（`SerializeToString`/`DeserializeFromString`），对于大量高频 Subject 可能有性能开销
- **推荐**：如果你在使用 nDisplay + LiveLink，这是 **必须启用** 的插件。没有它，LiveLink 数据在集群各节点上不会同步。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/LiveLinkOverNDisplay)
- 官方文档：暂无（`.uplugin` 中 `DocsURL` 为空）
- 测试用例：暂无
