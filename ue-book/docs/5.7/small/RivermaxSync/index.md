# RivermaxSync (NVIDIA Rivermax Media Synchronization)

> Adding NVIDIA Rivermax synchronization capabilities for nDisplay

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | 否 (IsBetaVersion=true) |
| 包含内容 | 否 |
| 模块 | RivermaxSync (Runtime), RivermaxSyncEditor (Editor) |
| 创建时间 | 2023-03-22 |
| 年龄标签 | 👴 老古董(>5年) |
| 平台 | Win64 only |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Rivermax/RivermaxSync) | |

## 用途

RivermaxSync 为 nDisplay 多节点集群提供基于 **PTP (Precision Time Protocol)** 的媒体输出同步策略。在虚拟制片 (Virtual Production) 场景中，nDisplay 需要多个渲染节点同时输出视频帧到 LED 墙。如果各节点的帧输出存在时间偏差，会导致 LED 墙上出现撕裂或画面不一致。

该 plugin 实现了一个同步策略类 `UMediaOutputSynchronizationPolicyRivermax`，利用 NVIDIA Rivermax SDK 的 PTP 时钟能力，通过 nDisplay 的 Generic Barrier 机制在集群节点间交换帧信息，检测帧级失同步并触发自动修复。

**核心解决的问题：** 多节点 nDisplay 集群中，通过 Rivermax 输出 ST 2110-20 视频流时，确保所有节点在相同的 PTP 帧边界上呈现相同的引擎帧。

## 使用场景

- 你在搭建 LED 虚拟制片 (VP) 摄影棚，使用 nDisplay 多节点渲染并通过 NVIDIA Rivermax 网卡输出 ST 2110-20 视频 → 使用 RivermaxSync 作为同步策略
- 你需要确保 LED 墙上所有区域的视频帧完全对齐，避免视觉撕裂 → 启用此 plugin 并配置 PTP 同步
- 你使用的是传统的 nDisplay 同步方案（如 Ethernet Barrier），但迁移到了 Rivermax 视频输出 → 将同步策略切换为 Rivermax (PTP)

**前置条件：**
- NVIDIA Rivermax SDK 及兼容网卡（Mellanox/NVIDIA ConnectX 系列）
- PTP 网络基础设施（PTP grandmaster clock）
- nDisplay 集群已配置 RivermaxMedia 作为媒体输出

## 蓝图用法

此 plugin 主要作为 nDisplay 的同步策略资产使用，不暴露太多蓝图节点。

### 核心资产类

| 资产类型 | 显示名称 | 说明 | 所在类 |
|---|---|---|---|
| Media Output Synchronization Policy | Rivermax (PTP) | Rivermax PTP 同步策略，可在编辑器中创建为资产 | `UMediaOutputSynchronizationPolicyRivermax` |

### 可配置属性

| 属性 | 类型 | 范围 | 说明 |
|---|---|---|---|
| `MarginMs` | float | 1–20 ms | 同步安全边距。距下一个对齐点不足此时间时，跳过该对齐点以避免不稳定输出 |

### 使用步骤

1. **启用 Plugin：** Edit → Plugins → 搜索 "RivermaxSync" → 启用（需同时启用 nDisplay、RivermaxCore、RivermaxMedia）
2. **创建同步策略资产：** Content Browser → 右键 → Miscellaneous → Media Output Synchronization Policy → 选择 "Rivermax (PTP)"
3. **配置 Margin：** 在资产编辑器中设置 Margin (ms)，默认 5ms，一般无需修改
4. **关联到 nDisplay：** 在 nDisplay 配置的媒体输出设置中，将同步策略指定为刚创建的 Rivermax (PTP) 资产

## C++ 用法

此 plugin 的核心逻辑通过 nDisplay 的同步策略接口工作，C++ 层面主要是内部实现，但可扩展。

### 头文件引入

```cpp
#include "MediaOutputSynchronizationPolicyRivermax.h"
```

### 内部同步机制

同步处理器 `FMediaOutputSynchronizationPolicyRivermaxHandler` 继承自 `FDisplayClusterMediaOutputSynchronizationPolicyEthernetBarrierBaseHandler`，核心同步流程如下：

```cpp
// 每帧调用的同步函数 (MediaOutputSynchronizationPolicyRivermax.cpp)
void FMediaOutputSynchronizationPolicyRivermaxHandler::Synchronize()
{
    // 1. 检查距下一个 PTP 对齐点的时间
    const double TimeLeftSeconds = GetTimeBeforeNextSyncPoint();
    const double MarginSeconds = double(MarginMs) / 1000;

    // 2. 如果距离太近（< Margin），跳过此对齐点
    if (TimeLeftSeconds < MarginSeconds)
    {
        // 睡眠到下一个对齐点之后
        const float SleepTime = TimeLeftSeconds + OffsetTimeSeconds;
        FPlatformProcess::SleepNoStats(SleepTime);
    }

    // 3. 获取最后呈现的帧信息并打包
    FPresentedFrameInfo FrameInfo;
    RmaxCapture->GetLastPresentedFrameInformation(FrameInfo);
    BarrierDataStruct.InsertFrameInfo(FrameInfo);

    // 4. 在 Barrier 上同步，与其他节点交换帧数据
    BarrierClient->Synchronize(GetBarrierId(), GetThreadMarker(), BarrierData, ResponseData);
}
```

### 失同步检测与自修复

Primary 节点在 Barrier 回调中比较所有节点的帧历史：

```cpp
// HandleBarrierSync - 在 Primary 节点上执行
// 比较各节点最近 2 帧的 RenderedFrameNumber 和 PresentedFrameBoundaryNumber
if (PtpBaseNodeData->HasConfirmedDesync(*NodeData, VsyncDelta))
{
    bSelfRepairRequired = true;
    // 记录警告日志
}

// 自修复：睡眠跳过下一个对齐点，让所有节点重新对齐
if (bSelfRepairRequired && bCanUseSelfRepair)
{
    const float SleepTime = TimeLeftSeconds + OffsetTimeSeconds;
    FPlatformProcess::SleepNoStats(SleepTime);
}
```

### 捕获类型验证

同步策略只在以下条件全部满足时生效：
- 使用 `URivermaxMediaCapture` 作为媒体捕获
- 时间源为 **PTP** 或 **System**
- 对齐模式为 **AlignmentPoint**（ST 2059 帧边界公式）

## 控制台变量 (CVars)

| CVar | 默认值 | 说明 |
|---|---|---|
| `Rivermax.Sync.WakeUpOffset` | 0.5 (ms) | 从对齐点到唤醒的偏移量，用于 Barrier 暂停集群后的恢复时机 |
| `Rivermax.Sync.EnableSelfRepair` | true | 是否在检测到失同步后自动执行自修复（跳过帧对齐点重新同步） |
| `Rivermax.Sync.Ptp.UnsyncFramesPerReport` | 120 | PTP 失同步 Stage Monitor 事件的报告频率（帧数间隔）。设为负数可禁用报告 |
| `Rivermax.Sync.ForceDesync` | false | 调试用 CVar，在 Barrier 同步后随机触发失同步以测试自修复 |

## Stage Monitor 事件

当集群中检测到 PTP 帧不匹配时，会通过 Stage Data Provider 发送 `FRivermaxClusterPtpUnsyncEvent` 事件：

| 字段 | 类型 | 说明 |
|---|---|---|
| `NodePtpFrameDeltas` | `TMap<FString, int64>` | 各节点与 PTP 基准节点的帧边界差值 |
| `PtpBaseNodeId` | `FString` | PTP 基准节点的 ID（默认为 Primary 节点） |

## 模块依赖

### RivermaxSync (Runtime 模块)

| 模块 | 用途 |
|---|---|
| `DisplayCluster` | nDisplay 核心框架，提供集群管理和 Barrier 机制 |
| `DisplayClusterMedia` | nDisplay 媒体输出同步策略基础类 |
| `RivermaxCore` | NVIDIA Rivermax SDK 封装，提供 PTP 时钟和流管理 |
| `StageDataCore` | Stage Monitor 数据接口，用于上报 PTP 失同步事件 |
| `RivermaxMedia` | (Private) Rivermax 媒体捕获实现，用于获取帧呈现信息 |

### RivermaxSyncEditor (Editor 模块)

| 模块 | 用途 |
|---|---|
| `RivermaxSync` | Runtime 模块引用 |
| `UnrealEd` | 编辑器工厂类支持 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-09-08 | `93ce6f365de4` | Rivermax: ANC Timecode, 自动字节序处理, UI 改进 | Rivermax 插件整体更新，涉及 ANC 时间码支持，RivermaxSync 作为子目录受影响 |
| 2025-04-06 | `8c1407abc931` | Rivermax Plugin Refactor: 拆分 Video stream, 添加 ANC 核心, 导出 SDP 选项 | 大规模重构，RivermaxSync 可能有间接影响 |
| 2025-03-12 | `c994df0ff34a` | nDisplay Base failover implementation (v1.5, P-node replacement) | nDisplay 故障转移实现，与同步机制相关 |

### 维护评价

- **实验性/Beta 状态**：`IsBetaVersion=true`，尚未标记为正式发布
- **活跃维护**：最近 6 个月内有相关更新（虽然主要是父级 Rivermax 插件的重构）
- **平台限制**：仅支持 Win64（依赖 NVIDIA Rivermax SDK）
- **代码量小**：核心代码集中在一个类（`UMediaOutputSynchronizationPolicyRivermax`），逻辑清晰，维护成本低
- **推荐程度**：如果你的 nDisplay 集群使用 Rivermax 网卡输出 ST 2110-20 视频，这是唯一的原生 PTP 同步方案，**必须使用**。但请注意其 Beta 状态，可能有边界情况未覆盖

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Rivermax/RivermaxSync)
- [父插件 Rivermax](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Rivermax)
- [RivermaxCore](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Rivermax/RivermaxCore) — Rivermax SDK 封装
- [RivermaxMedia](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Rivermax/RivermaxMedia) — Rivermax 媒体捕获/输出
- 官方文档：无（DocsURL 为空）
- 测试用例：无（未找到相关测试文件）
