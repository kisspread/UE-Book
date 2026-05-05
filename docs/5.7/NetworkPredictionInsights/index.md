# Network Prediction Insights

> Allows debugging of NetworkPrediction via Unreal Insights

| 属性 | 值 |
|---|---|
| 分类 | Insights |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NetworkPredictionInsights` (EditorAndProgram) |
| 实验性 | 否 |
| 创建时间 | 2020-03-16 |
| 年龄标签 | 🆕（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/NetworkPredictionInsights) | |

## 用途

NetworkPredictionInsights 是 Unreal Insights 的扩展模块，专门用于调试和可视化 [NetworkPrediction](../NetworkPrediction/) 系统的运行时数据。它解决的核心问题是：**在网络预测/回滚系统中，开发者很难直观地看到哪些模拟帧被确认、哪些被丢弃、哪些发生了回滚**。

这个 plugin 通过 Unreal Insights 的 Trace 系统采集 NetworkPrediction 的模拟数据（tick、网络接收、用户状态变更等），然后在 Insights 的专用标签页中以时间线的形式可视化展示。开发者可以：

- 查看每个 Actor 的模拟帧时间线，区分 Predicted / Confirmed / Trashed / Repredicted 等状态
- 检查网络接收事件（NetRecv）及其结果（Confirm / Rollback / Jump / Fault / Stale）
- 观察 Input、Sync、Aux、Physics 等用户状态的变化
- 追踪 Out-of-band 状态修改（游戏代码直接修改状态）
- 按 PIE Session 过滤数据

该 plugin 仅在 `UnrealInsights` 程序中加载（`ProgramAllowList: ["UnrealInsights"]`），不会在游戏运行时加载。

## 使用场景

- 你在使用 NetworkPrediction 系统做客户端预测 → 用此 plugin 可视化预测帧的确认/回滚过程
- 你在调试网络同步抖动 → 在时间线中查看哪些帧被 Trashed、哪些触发了 Rollback
- 你需要排查输入丢失或延迟 → 查看 BufferedInputCmds 计数和 InputFault 标记
- 你想验证网络 LOD 切换是否正确 → 在 Sparse 数据中查看 NetworkLOD 变化

## 蓝图用法

❌ 无。此 plugin 不暴露任何 BlueprintCallable 函数或 BlueprintReadWrite 属性。它是纯 Insights 分析工具，所有交互都在 Unreal Insights 的 UI 中完成。

## C++ 用法

此 plugin 是 Insights 分析模块，不需要在游戏代码中直接使用。它的 Trace 数据由 [NetworkPrediction](../NetworkPrediction/) 模块通过 `NetworkPredictionChannel` 自动产生。

### 启用 Trace 采集

要采集 NetworkPrediction 的 Trace 数据，需要在启动参数中指定 channel：

```bash
# 通过命令行参数启用
-trace=NetworkPrediction

# 或使用缩写
-trace=NP
```

### 在 Unreal Insights 中查看

1. 启动带有 `-trace=NP` 参数的应用程序
2. 打开 Unreal Insights (`UnrealInsights.exe`)
3. 连接到 trace 存储或打开 `.utrace` 文件
4. 如果在独立 UnrealInsights 中，检测到 NP 数据后会自动打开 "Network Prediction Insights" 标签页
5. 如果在编辑器中，手动在 Tools 菜单下找到 "Network Prediction Insights"

### 自动连接本地 Trace 服务器

在编辑器模式下，如果通过 `-trace=NP` 启动，模块会自动连接到本地 Trace 服务器（`127.0.0.1`）并启动分析：

```cpp
// NetworkPredictionInsightsModule.cpp 中的逻辑
// 编辑器模式下自动连接：
UnrealInsightsModule.ConnectToStore(TEXT("127.0.0.1"));
UnrealInsightsModule.CreateSessionViewer(false);
```

## UI 结构

Network Prediction Insights 窗口由三个主要面板组成：

### SNPWindow（主窗口）

顶层容器，管理过滤、PIE Session 选择、帧导航（前/后/首/末帧）和 AutoScroll。它持有 `FFilteredDataCollection`，将 Provider 的原始数据按帧范围过滤后传递给子面板。

### SNPSimFrameView（模拟帧时间线）

核心可视化面板，以时间线形式展示每个 Actor 的模拟帧。布局结构：

```
[ActorName, Role, NetGUID, Simulation Group]        } FSimulationActorGroup[0]
------------------------------------------------------------------------
  | Auto Proxy |  ****PP  !!!!!!                      } SubTrack[0..1]
------------------------------------------------------------------------
  | Authority  |  *****                               } SubTrack[0]
------------------------------------------------------------------------
  | Sim Proxy  |  *****                               } SubTrack[0]
```

每个模拟帧（Tick）根据状态着色：
- **Predicted** — 尚未确认的预测帧
- **Repredicted** — 回滚后重新预测的帧
- **Confirmed** — 已被权威状态确认的帧
- **Trashed** — 被丢弃的帧（被更新的预测覆盖）
- **Abandoned** — 跳帧导致被放弃的帧

网络接收事件（NetRecv）以竖线标记，根据结果着色（Confirm/Rollback/Jump/Fault/Stale）。

支持水平/垂直滚动、缩放、鼠标悬停工具提示、AutoScroll、用户状态文本搜索、Compact/Linear 视图切换。

### SNPSimFrameContents（帧内容详情）

点击时间线中的帧后，在此面板显示详细信息：
- 模拟信息（SimInfo）
- SimTick 详情
- InputCmd 状态
- SyncState 状态
- AuxState 状态
- 系统故障（SystemFaults）

## 数据流架构

```
[Runtime] NetworkPrediction 模块通过 UE_NP_TRACE 宏产生 trace 事件
     ↓
[TraceStream] 数据以二进制格式存储（.utrace 文件或 TCP 连接）
     ↓
[Analyzed] FNetworkPredictionAnalyzer 解析 trace 流，提取模拟事件
     ↓
[Provided] FNetworkPredictionProvider 存储所有分析后的数据
     ↓
[UI Widgets] SNPWindow 过滤 → SNPSimFrameView 可视化 → SNPSimFrameContents 详情
```

关键枚举类型（定义在 `INetworkPredictionProvider.h`）：

| 枚举 | 说明 |
|---|---|
| `ENP_NetRole` | 网络角色：None / SimulatedProxy / AutonomousProxy / Authority |
| `ENP_TickingPolicy` | Tick 策略：Independent / Fixed |
| `ENP_NetworkLOD` | 网络 LOD：Interpolated / SimExtrapolate / ForwardPredict |
| `ENP_UserState` | 用户状态类型：Input / Sync / Aux / Physics |
| `ENP_UserStateSource` | 状态来源：ProduceInput / SynthInput / SimTick / NetRecv / NetRecvCommit / OOB |
| `ENetSerializeRecvStatus` | 网络接收结果：Confirm / Rollback / Jump / Fault / Stale |

## 模块依赖

此 plugin 的所有依赖都是 PrivateDependencyModuleNames，不需要外部模块引用它。

| 模块 | 用途 |
|---|---|
| `Core` | 基础核心库 |
| `CoreUObject` | UObject 系统 |
| `InputCore` | 输入系统核心 |
| `SlateCore` | Slate UI 核心 |
| `Slate` | Slate UI 框架 |
| `TraceLog` | Trace 日志系统 |
| `TraceAnalysis` | Trace 分析框架 |
| `TraceServices` | Trace 服务（Provider/Analyzer 接口） |
| `TraceInsights` | Unreal Insights 集成 |
| `TraceInsightsCore` | Insights 核心模块 |
| `AssetRegistry` | 资产注册表 |
| `ApplicationCore` | 应用核心 |
| `Engine` | 引擎模块（条件编译：`bCompileAgainstEngine`） |
| `EditorFramework` | 编辑器框架（仅 Editor 目标） |
| `UnrealEd` | 编辑器工具（仅 Editor 目标） |
| `EditorWidgets` | 编辑器控件（仅 Editor 目标） |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-09-23 | `154d7077de01` | Removed deprecated code (toggled off by UE_DEPRECATED_PROFILER_ENABLED or by UE_STATS_MEMORY_PROFILER_ENABLED). Removed dependencies to deprecated Profiler* modules. | 清理废弃代码，移除对已删除 Profiler 模块的依赖。说明 Insights 基础架构在持续重构。 |
| 2025-09-12 | `ce6ff392ddca` | Addressing instances "ignoring return value of function declared with 'nodiscard' attribute" issue for FTSTicker::RemoveTicker usage. | 编译警告修复，适配 FTSTicker API 的 nodiscard 属性变更。 |
| 2025-04-08 | `855b561a75a6` | Fixed some wrongly-sized printf specifiers. | 格式化字符串修复，修正 printf 格式说明符大小不匹配的问题。 |

### 维护评价

- **创建时间**：2020 年 3 月，约 6 年历史
- **最近更新**：2025 年 9 月，最近 3 次 commit 都是基础设施维护（编译修复、废弃代码清理），无功能性更新
- **活跃程度**：**维护不活跃**。最近的实质性功能更新时间不明，近一年仅有编译/清理性质的变更
- **依赖关系**：与 NetworkPrediction 模块紧密耦合，依赖其 Trace 宏产出的数据格式
- **限制**：
  - 仅在 UnrealInsights 程序中加载，不能在游戏运行时使用
  - 不支持蓝图
  - 依赖 NetworkPrediction 模块产生特定格式的 trace 数据
- **推荐**：如果你正在使用 NetworkPrediction 系统做客户端预测，这是唯一官方的可视化调试工具，**强烈推荐使用**。虽然不常更新，但作为 Insights 扩展插件，功能相对稳定。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/NetworkPredictionInsights)
- [NetworkPrediction 插件](../NetworkPrediction/) — 产生此 plugin 可视化数据的网络预测框架
- [NetworkPredictionExtras 插件](../NetworkPredictionExtras/) — NetworkPrediction 的扩展组件
- 官方文档：无（.uplugin 中 DocsURL 为空）
