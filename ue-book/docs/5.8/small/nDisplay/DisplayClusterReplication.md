# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 集群显示 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产、编辑器工具、着色器） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是 Unreal Engine 的**多机集群同步渲染**系统，用于将一个 UE 场景的画面拆分到多台 PC 上同步渲染，最终拼接成一个完整的超大分辨率或沉浸式画面。它是 Virtual Production（虚拟制片）和大型沉浸式体验（如 LED 墙、穹顶投影、CAVE 系统、环绕大屏）的核心基础设施。

**核心解决的问题：**

1. **同步渲染**：多台 PC 各自渲染场景的一部分（称为"节点"），nDisplay 确保所有节点的相机、Actor 状态、动画完全同步，实现无缝拼接。
2. **投影校正（Warp & Blend）**：支持复杂的几何校正和边缘融合，适用于曲面屏幕、投影仪阵列等非平面显示环境。支持 MPCDI 格式的校正数据。
3. **立体渲染**：支持单目（mono）和立体（stereo）渲染模式，适用于 VR 级别的沉浸式显示。
4. **集群事件与网络同步**：通过自定义 NetDriver 实现集群节点间的同步数据包处理，保证所有节点在同一帧看到相同的游戏状态。
5. **Virtual Camera / ICVFX**：在虚拟制片中与摄影机追踪系统集成，支持 In-Camera VFX 工作流。
6. **Light Card 编辑**：内置灯光卡编辑器，用于控制 LED 屏幕上的虚拟灯光反射。
7. **Media 集成**：支持共享内存媒体传输，以及与 Movie Pipeline 的集成用于离线渲染输出。

nDisplay 不需要默认启用，因为它只在特定的集群/多屏硬件环境下才有用。

## 使用场景

- 你在搭建 **LED Volume 虚拟制片舞台**（如 The Mandalorian 那种）→ 用 nDisplay 驱动 LED 墙的多台渲染 PC
- 你需要构建 **CAVE 沉浸式投影系统**（多面投影房间）→ 用 nDisplay 管理多投影仪同步
- 你要搭建 **环绕大屏展示厅**（如汽车发布会的 360° 屏幕）→ 用 nDisplay 拼接多台 PC 的输出
- 你做的是 **穹顶投影天文馆**→ 用 nDisplay 的投影校正和边缘融合
- 你需要 **多机同步离线渲染**超大分辨率序列帧 → 用 nDisplay + Movie Pipeline
- 你使用 **Remote Control** 从外部控制多节点集群 → 用 nDisplayRemoteControlInterceptor

## 蓝图用法

nDisplay 的蓝图 API 主要集中在集群配置、运行时控制和事件通信上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Cluster Node Id` | 获取当前集群节点 ID | `UDisplayClusterBlueprintAPI` |
| `Get Cluster Node Count` | 获取集群节点总数 | `UDisplayClusterBlueprintAPI` |
| `Is Primary Node` | 判断当前是否为主节点 | `UDisplayClusterBlueprintAPI` |
| `Get Cluster Event Listener` | 获取集群事件监听器，用于蓝图中收发集群事件 | `UDisplayClusterBlueprintAPI` |
| `Send Cluster Event Binary` | 向集群发送二进制事件 | `UDisplayClusterBlueprintAPI` |
| `Send Cluster Event Json` | 向集群发送 JSON 事件 | `UDisplayClusterBlueprintAPI` |
| `Get Viewport` | 获取指定 nDisplay 视口对象 | `UDisplayClusterBlueprintAPI` |
| `Get Viewport Ids` | 获取所有 nDisplay 视口 ID 列表 | `UDisplayClusterBlueprintAPI` |
| `Set Viewport Buffer Ratio` | 设置视口缓冲区比例（分辨率缩放） | `UDisplayClusterBlueprintAPI` |
| `Set Swap Sync Policy` | 设置帧同步策略 | `UDisplayClusterBlueprintAPI` |

### 使用示例（蓝图描述）

**场景：检测主节点并在主节点上执行特殊逻辑**

1. 使用 `Is Primary Node` 节点判断当前运行的 PC 是否为主节点（Primary）
2. 分支 True → 执行主节点专有逻辑（如 UI 显示、控制面板）
3. 分支 False → 执行渲染节点逻辑（如全屏渲染、去边框）

**场景：通过集群事件广播自定义数据**

1. 在主节点上，使用 `Send Cluster Event Json` 发送包含自定义参数的 JSON 事件
2. 在所有节点上，通过 `Get Cluster Event Listener` 绑定事件委托
3. 在事件回调中解析 JSON 数据，执行相应操作（如同步切换场景、调整参数）

## C++ 用法

### 头文件引入

```cpp
#include "DisplayClusterModule.h"
#include "DisplayClusterNetDriver.h"
#include "DisplayClusterNetConnection.h"
#include "DisplayClusterClusterEvent.h"
```

### 基本用法

**获取 nDisplay 模块并查询集群状态：**

```cpp
#include "DisplayClusterModule.h"

// 获取 nDisplay 模块
IDisplayClusterModule& DisplayClusterModule = FModuleManager::GetModuleChecked<IDisplayClusterModule>("DisplayCluster");

// 检查集群是否已启动
if (DisplayClusterModule.IsModuleInitialized())
{
    // 获取当前节点 ID
    FString NodeId = DisplayClusterModule.GetNodeId();
    
    // 检查是否为主节点
    bool bIsPrimary = DisplayClusterModule.IsPrimaryNode();
    
    UE_LOG(LogTemp, Log, TEXT("nDisplay Node: %s, Primary: %s"), 
        *NodeId, bIsPrimary ? TEXT("Yes") : TEXT("No"));
}
```

### 进阶用法

**自定义集群 NetDriver 实现同步复制：**

`UDisplayClusterNetDriver` 继承自 `UIpNetDriver`，负责集群节点间的同步网络包处理。它通过集群事件（Cluster Events）协调所有节点在同一帧同步处理网络数据包，确保 Actor 复制状态在所有渲染节点上完全一致。

```cpp
#include "DisplayClusterNetDriver.h"
#include "DisplayClusterClusterEvent.h"

// NetDriver 中的同步机制基于两个关键集群事件：
// - NodeSyncEvent: 通知集群节点准备开始同步包处理
// - PacketSyncEvent: 标识特定数据包的同步信息

// 在自定义逻辑中，你可以监听二进制集群事件
void HandleClusterEvent(const FDisplayClusterClusterEventBinary& Event)
{
    // 事件到达时，NetDriver 会在所有节点上同步处理
    // 这保证了所有渲染节点在同一帧看到相同的游戏状态
}
```

**注册集群二进制事件监听器：**

```cpp
#include "DisplayClusterNetDriver.h"

// DisplayClusterNetDriver 提供了 FOnClusterEventBinaryListener 用于监听同步事件
// HandleEvent 方法在客户端侧处理集群事件
// 包括同步模式启动和数据包处理

// NetDriver 内部维护了：
// - OutPacketsQueues: 每个连接的待处理包队列
// - SyncConnections: 参与同步复制的连接集合
// - ClusterReplicationState: 复制状态，用于均衡各节点的 Actor 数量
```

## Demo 示例

### 最小 nDisplay 集群事件收发示例

**MyClusterEventListener.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "DisplayClusterClusterEvent.h"
#include "MyClusterEventListener.generated.h"

UCLASS(ClassGroup=(nDisplay), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMyClusterEventListener : public UActorComponent
{
    GENERATED_BODY()

public:
    UMyClusterEventListener();

    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    /** 蓝图可调用：向集群发送一条文本消息 */
    UFUNCTION(BlueprintCallable, Category = "nDisplay")
    void SendClusterMessage(const FString& Message);

private:
    /** 处理接收到的集群事件 */
    void OnClusterEvent(const FDisplayClusterClusterEventBinary& Event);

    FDelegateHandle EventDelegateHandle;
};
```

**MyClusterEventListener.cpp**
```cpp
#include "MyClusterEventListener.h"
#include "DisplayClusterModule.h"
#include "DisplayClusterNetDriver.h"

UMyClusterEventListener::UMyClusterEventListener()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UMyClusterEventListener::BeginPlay()
{
    Super::BeginPlay();

    IDisplayClusterModule& DCModule = FModuleManager::GetModuleChecked<IDisplayClusterModule>("DisplayCluster");
    
    if (DCModule.IsModuleInitialized())
    {
        UE_LOG(LogTemp, Log, TEXT("nDisplay cluster active, node: %s"), *DCModule.GetNodeId());
    }
}

void UMyClusterEventListener::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    Super::EndPlay(EndPlayReason);
}

void UMyClusterEventListener::SendClusterMessage(const FString& Message)
{
    FDisplayClusterClusterEventBinary Event;
    Event.Name = TEXT("CustomMessage");
    Event.Category = TEXT("MyApp");
    
    // 将消息序列化为字节数组
    FTCHARToUTF8 Converter(*Message);
    Event.Data.Append((uint8*)Converter.Get(), Converter.Length());
    
    IDisplayClusterModule& DCModule = FModuleManager::GetModuleChecked<IDisplayClusterModule>("DisplayCluster");
    if (DCModule.IsModuleInitialized())
    {
        DCModule.EmitClusterEvent(Event);
    }
}

void UMyClusterEventListener::OnClusterEvent(const FDisplayClusterClusterEventBinary& Event)
{
    if (Event.Category == TEXT("MyApp") && Event.Name == TEXT("CustomMessage"))
    {
        FString ReceivedMessage = FString(UTF8_TO_TCHAR(Event.Data.GetData()));
        UE_LOG(LogTemp, Log, TEXT("Received cluster message: %s"), *ReceivedMessage);
    }
}
```

## 模块依赖

nDisplay 是一个超大型插件（29 个模块），以下是各模块的核心职责和关键依赖关系：

### 模块职责总览

| 模块 | 职责 |
|---|---|
| `DisplayCluster` | 核心运行时：集群管理、节点通信、视口管理 |
| `DisplayClusterConfiguration` | 配置数据模型：解析 .ndisplay 配置文件 |
| `DisplayClusterConfigurator` | 配置编辑器：可视化编辑集群拓扑 |
| `DisplayClusterProjection` | 投影系统：MPCDI、简单投影、Arena 投影 |
| `DisplayClusterWarp` | 几何校正与边缘融合 |
| `DisplayClusterShaders` | 着色器管理：WarpBlend、MPCDI、ICVFX 着色器 |
| `DisplayClusterReplication` | 网络同步：自定义 NetDriver 实现集群节点同步复制 |
| `DisplayClusterMedia` | 媒体传输：共享内存、视频输入输出 |
| `DisplayClusterColorGrading` | 颜色校正：集群统一的颜色分级 |
| `DisplayClusterLightCardEditor` | 灯光卡编辑：LED 墙上的虚拟灯光反射控制 |
| `DisplayClusterMoviePipeline` | 电影管线集成：多节点同步离线渲染 |
| `DisplayClusterMultiUser` | 多用户编辑：多人同时编辑 nDisplay 配置 |
| `DisplayClusterOperator` | 操作员面板：运行时监控和控制 |
| `DisplayClusterStageMonitoring` | 舞台监控：性能和状态监控 |
| `SharedMemoryMedia` | 共享内存传输：节点间的高效帧数据传输 |
| `ScalableMPCDI` | 第三方库：MPCDI 格式支持 |

### 关键依赖

| 模块 | 用途 |
|---|---|
| `D3D12RHI` | 共享内存媒体传输的 Direct3D 12 资源共享 |
| `UnrealEd` | 编辑器集成（配置编辑器、灯光卡编辑器等） |
| `EditorWidgets` | 自定义编辑器控件 |
| `LevelEditor` | 关卡编辑器集成（nDisplay 面板嵌入） |

> 注意：尽管多个模块标注为 Runtime 类型，但部分模块（如 DisplayCluster、DisplayClusterProjection）实际依赖 UnrealEd 等编辑器模块，这在打包时需要注意模块加载策略。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | MovieGraph 集成中增加 EXR 多图层输出支持 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | MoviePipeline 中将 WarpBlendAlpha 模式合并到 WarpBlend |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复 MRG 中拓扑感知摄影机命名及 MPCDI/ICVFX 着色器的不透明 alpha 问题 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 输出帧编码回退路径中正确处理非默认 DisplayGamma |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复 GUI 纹理尺寸小于视口尺寸时的闪烁问题 |

### 维护评价

**活跃维护** ✅

nDisplay 是 Epic Games 重点维护的核心 Virtual Production 基础设施。基于以下分析：

- **创建时间**：2018 年 6 月（UE 4.20 时期），已有约 8 年历史
- **更新频率**：非常活跃，仅 2026 年 5 月就有 5 次更新，涵盖功能增强（EXR 多图层、MoviePipeline 集成）、Bug 修复（着色器 alpha、闪烁、Gamma）和代码重构
- **代码规模**：1351 个源文件，29 个模块，是 UE 中最庞大的插件之一，持续有新模块和功能加入
- **官方支持**：由 Epic Games 直接开发和维护，是 Unreal Virtual Production 工作流的核心组件
- **局限性**：
  - 默认关闭（`EnabledByDefault: false`），需要手动启用
  - 需要专用的多机硬件环境才能有效使用
  - 配置复杂度高，学习曲线陡峭
  - 部分 Runtime 模块依赖编辑器模块，打包配置需额外注意
- **推荐使用**：如果你的项目涉及 LED Volume、沉浸式投影或多机渲染，nDisplay 是**唯一且必选**的官方方案，推荐使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/n-display-in-unreal-engine/)（Unreal Engine 官方 nDisplay 文档）