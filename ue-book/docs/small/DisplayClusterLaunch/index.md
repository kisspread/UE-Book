# nDisplay Launch

> Launch local nDisplay nodes with ease.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | false |
| 包含内容 | true |
| 模块 | DisplayClusterLaunchEditor (Editor) |
| 创建时间 | 2022-04-07 |
| 年龄标签 | 🆕 (≈4年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.6/Engine/Plugins/Editor/DisplayClusterLaunch) | |

## 用途

DisplayClusterLaunch 是一个编辑器插件，为 nDisplay（UE5 的多屏幕/多节点渲染系统）提供**一键式本地启动**能力。

在没有这个插件的情况下，要在本地开发环境中启动 nDisplay 集群，你需要手动为每个节点构造冗长的命令行参数（包括 `.ndisplay` 配置路径、节点名、窗口位置、全屏参数、Multi-User 连接参数、控制台变量等），然后逐个通过终端启动 Unreal Editor 进程。这个过程繁琐且容易出错。

DisplayClusterLaunch 自动化了整个流程：
1. 从当前关卡中的 `ADisplayClusterRootActor` 读取 nDisplay 配置
2. 将配置导出为临时 `.ndisplay` 文件（非破坏性副本）
3. 为每个选中的集群节点自动生成完整的命令行参数
4. 启动对应的 Unreal Editor 进程（`-game` 模式）
5. 可选地自动启动 Multi-User (Concert) 服务器并连接会话

## 使用场景

- **虚拟制片开发**：你在本地工作站上开发 VP 项目，需要测试多屏幕 nDisplay 输出，但不想每次都手写命令行
- **多节点调试**：你的 nDisplay 配置有 3-4 个节点（如 LED 墙的不同区域），需要同时在窗口化模式下启动所有节点进行调试
- **Multi-User 协作测试**：你需要在启动 nDisplay 的同时自动连接到 Multi-User 编辑会话
- **性能分析**：需要在每个节点上自动启用 Unreal Insights 追踪来分析渲染性能

## 蓝图用法

此插件完全是**编辑器工具**，没有暴露蓝图可调用的节点（无 `UFUNCTION(BlueprintCallable)`）。所有功能通过编辑器 UI 交互。

## 编辑器 UI 用法

### 启用插件

由于 `EnabledByDefault: false` 且 `IsBetaVersion: true`，你需要手动启用：

1. 打开 **Edit → Plugins**
2. 搜索 "nDisplay Launch"
3. 勾选启用，重启编辑器

### 工具栏按钮

启用后，关卡编辑器工具栏的 **用户区域** 会出现两个按钮：

| 按钮 | 功能 |
|---|---|
| ▶ (Play) / ✕ (Stop) | 点击启动/终止 nDisplay 进程。图标根据是否有活跃进程自动切换 |
| ▼ 下拉菜单 | 展开完整的配置选项面板 |

### 下拉菜单结构

```
┌─────────────────────────────────────────┐
│ Launch nDisplay                         │
│  → Launch Last Node Configuration       │  ← 使用上次的节点配置快速启动
├─────────────────────────────────────────┤
│ Configuration                           │
│  ○ ConfigActor_1                        │  ← 选择 nDisplay Config Actor (单选)
│  ○ ConfigActor_2                        │
├─────────────────────────────────────────┤
│ Nodes                                   │
│  [NodeName Selected]                    │  ← 当前选中节点数量
│  → Select nDisplay Nodes                │  ← 子菜单：勾选节点 + 指定 Primary Node
├─────────────────────────────────────────┤
│ Additional Console Variables Asset      │
│  → None Selected / AssetName            │  ← 选择额外的 ConsoleVariablesAsset
├─────────────────────────────────────────┤
│ Options                                 │
│  ☐ Connect to Multi-User                │  ← 启动时自动连接 Multi-User
│  ☐ Enable Unreal Insights               │  ← 启用性能追踪
│  ☐ Close Editor on Launch               │  ← 启动后关闭编辑器（节省资源）
│  ⚙ Advanced Settings...                 │  ← 打开项目设置详细配置
└─────────────────────────────────────────┘
```

### 项目设置

通过 **Edit → Project Settings → Plugins → nDisplay Launch** 或下拉菜单中的 "Advanced Settings..." 访问：

| 设置 | 说明 |
|---|---|
| **Close Editor on Launch** | 启动节点进程时关闭编辑器，优化性能 |
| **Connect to Multi-User** | 自动连接或创建 Multi-User 会话 |
| **Explicit Session Name** | 指定 Multi-User 会话名称（留空则自动生成） |
| **Enable Unreal Insights** | 为启动的节点启用 `-trace` 参数 |
| **Enable Stat Named Events** | 配合 Insights 启用 `-statnamedevents` |
| **Explicit Trace File Save Directory** | 指定 Insights 追踪文件保存目录（留空则连接 localhost） |
| **Console Variables Preset** | 指定一个 `ConsoleVariablesAsset`，其保存的命令将在启动时执行 |
| **Additional Console Variables** | 额外的控制台变量（如 `r.ScreenPercentage 50`） |
| **Additional Console Commands** | 额外的控制台命令（如 `stat unit`） |
| **Command Line Arguments** | 额外的命令行参数（不带 `-` 前缀，如 `messaging`） |
| **Log FileName** | 日志文件名（留空则使用节点名） |
| **Logging** | 日志类别和详细级别配置数组 |

## C++ 用法

此插件主要是编辑器 UI 工具，通常不需要 C++ 代码调用。如果需要程序化控制，可以访问模块单例：

### 头文件引入

```cpp
#include "DisplayClusterLaunchEditorModule.h"
```

### 基本用法

```cpp
// 获取模块单例并启动 nDisplay 进程
FDisplayClusterLaunchEditorModule& LaunchModule = FDisplayClusterLaunchEditorModule::Get();

// 启动（会先检查世界中是否有 nDisplay 配置，然后根据设置处理 Multi-User 等）
LaunchModule.TryLaunchDisplayClusterProcess();

// 终止所有活跃的 nDisplay 节点进程
LaunchModule.TerminateActiveDisplayClusterProcesses();

// 打开项目设置面板
FDisplayClusterLaunchEditorModule::OpenProjectSettings();
```

### 源码路径

- 模块入口: `Source/DisplayClusterLaunchEditor/Private/DisplayClusterLaunchEditorModule.cpp`
- 项目设置: `Source/DisplayClusterLaunchEditor/Public/DisplayClusterLaunchEditorProjectSettings.h`

## Demo 示例

此插件无需编写代码，以下是一个完整的使用流程：

### 最小使用流程

1. **准备 nDisplay 配置**：确保关卡中至少放置了一个 `ADisplayClusterRootActor`（从 nDisplay 插件的 Placement Mode 中拖入）
2. **启用插件**：在 Plugins 面板中启用 "nDisplay Launch"
3. **启动**：点击工具栏的 ▶ 按钮，或展开下拉菜单选择具体配置和节点后启动

### 带 Multi-User 的完整流程

1. 在项目设置中启用 "Connect to Multi-User"
2. （可选）设置 "Explicit Session Name" 如 `MyVPSession`
3. 点击工具栏 ▶ 按钮
4. 插件会自动：启动 Concert Server → 创建/连接会话 → 启动所有节点进程

### 命令行参数说明

插件为每个节点自动生成的命令行大致如下：

```
UnrealEditor.exe "ProjectName.uproject" -game "MapName" Log=NodeName.log
  -fullscreen -dc_cfg="temp.ndisplay" -dc_node="NodeName"
  -CONCERTISHEADLESS -CONCERTRETRYAUTOCONNECTONERROR -CONCERTAUTOCONNECT
  -CONCERTSERVER="server_name" -CONCERTSESSION="session_name"
  -ini:Input:[/Script/Engine.InputSettings]:DefaultPlayerInputClass=/Script/DisplayCluster.DisplayClusterPlayerInput
  -UDPMESSAGING_TRANSPORT_UNICAST=... -UDPMESSAGING_TRANSPORT_MULTICAST=...
  -ExecCmds="console_commands" -DPCVars="console_variables" -LogCmds="log_categories"
```

关键参数：
- `-dc_cfg`：临时导出的 `.ndisplay` 配置文件路径
- `-dc_node`：当前进程对应的集群节点 ID
- 窗口参数根据节点配置自动设置（`-fullscreen` 或 `-windowed -forceres -WinX=... -ResX=...`）
- Headless 节点自动添加 `-RenderOffscreen`

## 模块依赖

### 插件依赖（.uplugin）

| 插件 | 用途 |
|---|---|
| `nDisplay` | 核心多节点渲染系统，提供 `ADisplayClusterRootActor` 等基础类型 |
| `ConsoleVariables` | 控制台变量管理 |
| `ConcertMain` | Multi-User Editing 基础框架 |
| `ConcertSyncClient` | Multi-User 客户端同步 |
| `MultiUserClient` | Multi-User 编辑客户端模块 |
| `UdpMessaging` | UDP 消息传输，节点间通信 |

### 模块依赖（Build.cs）

| 模块 | 用途 |
|---|---|
| `Core` | 核心基础库 |
| `OutputLog` | 输出日志面板 |
| `PlacementMode` | 编辑器放置模式，注册 nDisplay 资产到面板 |
| `DisplayCluster` | nDisplay 运行时模块 |
| `DisplayClusterConfiguration` | nDisplay 配置数据读写 |
| `Concert` / `ConcertClient` / `ConcertSyncClient` | Multi-User 会话管理 |
| `MultiUserClient` | Multi-User 编辑客户端 |
| `ConsoleVariablesEditor` / `ConsoleVariablesEditorRuntime` | 控制台变量资产读取 |
| `UdpMessaging` | UDP 消息设置读取与传递 |
| `Slate` / `SlateCore` / `ToolMenus` | UI 框架 |
| `UnrealEd` / `EditorStyle` / `EditorWidgets` | 编辑器集成 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-10-09 | `335895c2` | Specify SupportedPlatformTargets to prevent Mac builds | 平台适配修复：显式指定 Win64/Linux，避免在 Mac 上编译此编辑器插件 |
| 2025-09-03 | `49fd9ec3` | Added few more CVars to the launch command line | 功能增强：为启动命令行添加更多默认控制台变量 |
| 2025-07-23 | `b8c2660d` | Add nomcp option to default launch args | 添加 `-nomcp` 到默认启动参数，防止启动时连接 MCP |

### 维护评价

- **创建时间**：2022 年 4 月，约 4 年历史
- **最近更新**：2025 年 10 月有更新，属于**活跃维护**状态
- **Beta 状态**：`IsBetaVersion=true`，说明 Epic 仍视其为 Beta 产品
- **默认未启用**：`EnabledByDefault=false`，需要手动激活
- **平台限制**：仅支持 Win64 和 Linux（无 Mac/移动端）
- **推荐使用**：如果你在做 nDisplay 本地开发，这个插件能显著减少手动启动的痛苦。虽然是 Beta，但 Epic 在持续更新，建议使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.6/Engine/Plugins/Editor/DisplayClusterLaunch)
- 官方文档：无（.uplugin 中 DocsURL 为空）
- [nDisplay 文档](https://docs.unrealengine.com/5.6/en-US/n-display-in-unreal-engine/)
- [Multi-User Editing 文档](https://docs.unrealengine.com/5.6/en-US/multi-user-editing-in-unreal-engine/)
