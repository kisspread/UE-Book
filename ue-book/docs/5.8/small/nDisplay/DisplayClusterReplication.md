# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 集群显示 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产、着色器、编辑器资源） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

> ⚠️ 本插件默认未启用（`EnabledByDefault: false`），需要在 Plugins 面板中手动启用。

## 用途

nDisplay 是 Unreal Engine 的**集群渲染（Clustered Rendering）**系统，允许使用多台 PC 协同渲染同一个场景，并将结果同步输出到多个物理显示器上。它解决的核心问题是：**单台机器的 GPU 算力不足以驱动大规模沉浸式显示环境时，如何让多台机器像一台机器一样无缝协作**。

典型应用场景包括：
- **LED 虚拟制片棚（Virtual Production Stage）**：多面 LED 屏幕组成的大型拍摄棚，每块屏幕由独立 PC 驱动
- **CAVE（Cave Automatic Virtual Environment）**：多面投影的沉浸式 VR 环境
- **多屏模拟器**：驾驶/飞行模拟器的环绕屏幕
- **穹顶/弧幕投影**：天文馆、展览馆的大型投影系统
- **汽车设计评审**：多台投影仪拼接的实车尺寸展示

nDisplay 通过自定义 NetDriver（`UDisplayClusterNetDriver`）实现集群节点间的**同步数据复制**，确保所有节点的渲染帧完全对齐，最终拼接出无缝画面。它还集成了 MPCDI（Multi-PC Display Configuration Interface）和 warp/blend 技术来处理投影几何校正。

## 使用场景

| 场景 | 推荐方案 |
|---|---|
| 你有一面 LED 墙需要用多台 PC 渲染 → | 用 nDisplay 配置集群拓扑，每台 PC 对应一个或多个 Viewport |
| 你需要构建 CAVE 或穹顶投影系统 → | 用 nDisplay + MPCDI 投影校正 |
| 你在做虚拟制片（Virtual Production）→ | nDisplay + 内置 ICVFX（In-Camera VFX）管线 |
| 你需要录制 nDisplay 画面到文件 → | 用 `DisplayClusterMoviePipeline` 模块集成 Movie Render Queue |
| 你需要多用户协同编辑 nDisplay 配置 → | 用 `DisplayClusterMultiUser` 模块 |
| 你只需要单机多屏输出 → | 可能不需要 nDisplay，标准 UE 多显示器方案即可 |

## 蓝图用法

> 由于文档提供的源码分析主要集中在 `DisplayClusterReplication` 模块（网络同步层），以下蓝图 API 基于该模块的公开接口。完整的 nDisplay 蓝图 API（如 Viewport 管理、投影配置等）分布在其他子模块中。

### 核心节点

nDisplay 的网络同步是自动化的，通常不需要直接操作蓝图节点。集群事件（Cluster Events）是与 nDisplay 集群交互的主要蓝图机制：

| 节点 | 说明 | 所在类 |
|---|---|---|
| Cluster Event 相关 | 发送/接收集群二进制事件，用于节点间自定义通信 | 通过 `FOnClusterClusterEventBinaryListener` 机制 |
| `HandleEvent` | 处理集群二进制事件（同步模式启动和数据包处理） | `UDisplayClusterNetDriver` |
| `AddNodeConnection` | 添加集群节点连接 | `UDisplayClusterNetDriver` |
| `RemoveNodeConnection` | 移除集群节点连接 | `UDisplayClusterNetDriver` |

### 使用示例（蓝图描述）

nDisplay 的主要配置和使用通过 **nDisplay 配置文件（.ndisplay）** 完成，而非蓝图节点。典型工作流程：

1. 在编辑器中通过 **nDisplay Configurator** 面板创建 `.ndisplay` 配置文件
2. 定义集群节点（Cluster Nodes）、视口（Viewports）、投影（Projections）
3. 在项目的 nDisplay 设置中加载配置文件
4. 启动时 nDisplay 自动建立集群网络连接、同步 Actor 复制
5. 如需自定义逻辑，通过 Cluster Events 在蓝图中发送/接收自定义二进制事件

## C++ 用法

### 头文件引入

```cpp
#include "DisplayClusterNetDriver.h"
#include "DisplayClusterNetConnection.h"
```

### 基本用法

`UDisplayClusterNetDriver` 继承自 `UIpNetDriver`，负责集群节点间的同步网络数据包分发。它重写了关键的网络调度方法以实现帧同步：

```cpp
// DisplayClusterNetDriver.h - 自动同步的 Tick 机制
// 网络数据包在 TickDispatch 和 TickFlush 中被同步处理
// 确保所有集群节点在同一帧处理相同的数据

// 集群同步的核心事件 ID
// NodeSyncEvent: 通知集群节点同步处理开始
// PacketSyncEvent: 标识同步数据包
inline static const int NodeSyncEvent = GetTypeHash(FStringView(TEXT("nDCRNodeSyncEvent")));
inline static const int PacketSyncEvent = GetTypeHash(FStringView(TEXT("nDCRPacketSyncEvent")));
```

### 进阶用法

自定义集群事件处理——通过二进制集群事件在节点间传递自定义数据：

```cpp
// 生成并发送集群同步事件
void GenerateClusterCommandsEvent(
    FDisplayClusterClusterEventBinary& NetworkDriverSyncEvent,
    int32 EventId,
    const TMap<uint32, int32>& Parameters
);

// 集群连接管理
UDisplayClusterNetConnection* Connection = /* ... */;
NetDriver->AddNodeConnection(Connection);    // 添加节点连接
NetDriver->RemoveNodeConnection(Connection); // 移除节点连接

// 集群连接按类型分类存储在 NetDriver 中：
// - NodeConnections: 所有 nDisplay 节点连接
// - PrimaryNodeConnections: 主节点连接
// - ClusterConnections: 按 ClusterId 分组的连接
// - SyncConnections: 参与同步复制的连接
```

`UDisplayClusterNetConnection` 包含每个节点的关键元数据：

```cpp
// DisplayClusterNetConnection.h - 节点连接属性
Connection->NodeName;          // 从 URL 解析的节点名称
Connection->ClientAddress;     // 节点 IP 地址
Connection->ClientId;          // 集群客户端唯一标识
Connection->ClusterId;         // 集群唯一标识（基于配置文件路径的哈希）
Connection->ClusterNodesNum;   // 集群节点总数
Connection->bNodeIsPrimary;    // 是否为主节点
Connection->bSynchronousMode;  // 是否在同步模式下工作

// 同步数据包处理：按 PacketId 顺序处理累积的数据包
Connection->ProcessPacket(PacketId);
```

## Demo 示例

以下展示如何自定义一个监听集群事件的 NetDriver Helper：

```cpp
// MyClusterEventHandler.h
#pragma once

#include "CoreMinimal.h"
#include "DisplayClusterNetDriver.h"

class FMyClusterEventHandler
{
public:
    void Initialize(UDisplayClusterNetDriver* InNetDriver)
    {
        if (!InNetDriver) return;

        // 注册二进制集群事件监听器
        // 当集群节点间有同步事件时自动回调
        InNetDriver->HandleEvent(/* FDisplayClusterClusterEventBinary */);
    }

    // 构建自定义同步事件数据
    void BuildSyncCommand(
        FDisplayClusterClusterEventBinary& OutEvent,
        int32 EventId,
        const TMap<uint32, int32>& Parameters)
    {
        // 将参数序列化为二进制事件数据
        // 每个节点收到相同的事件数据，确保同步一致性
        TArray<uint8> EventData;
        // ... 序列化逻辑
        OutEvent.EventData = MoveTemp(EventData);
    }
};
```

```cpp
// MyClusterEventHandler.cpp
#include "MyClusterEventHandler.h"
```

## 模块依赖

以下列出 nDisplay 插件的**独特**模块依赖（已省略通用 Core/Engine/Slate 等）：

| 模块 | 用途 |
|---|---|
| `EditorWidgets` | 编辑器自定义控件（nDisplay 配置面板 UI） |
| `LevelEditor` | 关卡编辑器集成（nDisplay 编辑器工具入口） |
| `D3D12RHI` | Direct3D 12 渲染硬件接口（共享内存媒体传输、GPU 资源共享） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | MovieGraph 框架下新增 EXR 多图层支持 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | MoviePipeline 中合并 WarpBlendAlpha 模式到 WarpBlend |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复 MRG 中拓扑感知的相机命名和 MPCDI/ICVFX 着色器不透明 Alpha 问题 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 输出帧编码回退时尊重非默认 DisplayGamma 设置 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复 GUI 纹理尺寸小于视口尺寸时的闪烁问题 |

### 维护评价

**状态：🟢 活跃维护中**

nDisplay 是 Epic Games 重点维护的企业级功能，与 **Virtual Production（虚拟制片）** 工作流深度绑定。最近的提交记录显示更新非常频繁（仅 2026 年 5 月就有 5 次以上更新），内容涵盖：

- **MoviePipeline 集成持续增强**（EXR 多图层、WarpBlend 改进）
- **着色器和渲染质量修复**（Alpha 通道、Gamma 处理）
- **稳定性修复**（UI 闪烁等边界情况）

该插件自 2018 年创建以来持续活跃，已有 8 年历史但仍在积极开发。它是 Unreal Engine **ICVFX（In-Camera Visual Effects）** 管线的核心基础设施，在影视行业有广泛采用。

**推荐使用**：如果你的工作涉及虚拟制片或多屏集群渲染，nDisplay 是官方推荐且唯一支持的方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/en-US/RenderingAndGraphics/nDisplay/)（Unreal Engine 官方 nDisplay 文档）