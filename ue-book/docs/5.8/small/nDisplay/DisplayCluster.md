# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 多屏集群渲染 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产、材质模板、蓝图资产、编辑器工具） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 🏛️ 文物（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 文档目录

由于 nDisplay 是一个超大型插件（1351 源文件，29 个模块），本文档按子模块拆分：

| 文档 | 内容 |
|---|---|
| **[集群通信与故障转移](Cluster.md)** | 集群管理器、节点控制器、同步协议、故障恢复、通用屏障 |
| **[渲染系统与视口管理](Rendering.md)** | 渲染设备、视口管理器、投影策略、扭曲/混合、自动曝光、后处理 |
| **[组件与根Actor](Components.md)** | DisplayClusterRootActor、CameraComponent、ICVFXCameraComponent、LightCard、DisplayDevice、PreviewShare |
| **[蓝图与回调系统](Blueprints.md)** | 蓝图API、集群事件、自定义状态、回调接口 |
| **[媒体与编辑器工具](MediaAndEditor.md)** | 媒体输入/输出、MoviePipeline、LightCard编辑器、场景预览、多用户编辑 |
| **[通用工具与扩展](Utilities.md)** | 通用工具、数学工具、配置系统、Stage监控 |

## 用途

nDisplay 是 Unreal Engine 的**虚拟制作核心技术**，解决以下核心问题：

1. **多PC集群同步渲染**：允许多台计算机（节点）协同渲染同一场景的不同部分（视口），所有节点保持严格的帧同步和状态一致性
2. **LED墙虚拟制作（ICVFX）**：支持 In-Camera VFX 工作流，将渲染画面投射到 LED 墙上，通过摄像机内视锥实现虚实融合
3. **多视口投影与扭曲**：支持各种投影映射方式（MPCDI、Mesh、EasyBlend 等），将渲染内容正确映射到物理显示表面
4. **CAVE/穹顶/环绕显示**：支持任意数量和布局的显示面板，包括立体（stereo）渲染

**为什么存在**：标准 Unreal Engine 的单机渲染无法满足虚拟制作、主题公园、CAVE 系统等场景中多台显示器的精确同步需求。nDisplay 提供了一套完整的集群通信协议、故障转移机制、帧同步屏障和投影映射管线，使得多台 PC 能够像一台超级计算机一样协调工作。

## 使用场景

- **LED虚拟摄影棚**：你在用 LED 墙做 In-Camera VFX → 使用 nDisplay 配置 ICVFX Camera 和内/外视锥
- **多投影仪CAVE系统**：你有 6 个投影仪组成沉浸式空间 → 使用 nDisplay 配置 MPCDI/Mesh 投影策略
- **穹顶影院**：你需要将画面映射到球形穹顶 → 使用 nDisplay 配置自定义投影网格
- **多PC同步渲染**：你需要 4 台 PC 各驱动一块 LED 面板且保持帧同步 → 使用 nDisplay 的集群模式
- **MoviePipeline离线渲染**：你需要将 nDisplay 画面录制为视频 → 使用 DisplayClusterMoviePipeline 模块
- **虚拟制作调色**：你需要对 LED 墙进行实时色彩校准 → 使用 DisplayClusterColorGrading 和 OCIO 支持
- **多用户协作编辑**：多人同时编辑 nDisplay 配置 → 使用 DisplayClusterMultiUser 模块

## 核心架构

nDisplay 采用模块化架构，核心组件交互如下：

```
┌─────────────────────────────────────────────────────────┐
│                ADisplayClusterRootActor                  │
│  ┌──────────────┐  ┌──────────────────┐  ┌───────────┐  │
│  │ Camera Comp   │  │ ICVFX Camera Comp│  │ LightCard │  │
│  └──────┬───────┘  └────────┬─────────┘  └─────┬─────┘  │
│         │                   │                   │        │
│  ┌──────┴───────────────────┴───────────────────┴─────┐  │
│  │              DisplayClusterViewportManager          │  │
│  │  ┌──────────┐  ┌──────────────┐  ┌──────────────┐  │  │
│  │  │ Viewport  │  │ ViewportProxy│  │ RenderTarget │  │  │
│  │  │ (GameThread)│ │ (RenderThread)│ │  Manager     │  │  │
│  │  └──────────┘  └──────────────┘  └──────────────┘  │  │
│  └────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
           │                           │
    ┌──────┴──────┐            ┌───────┴───────┐
    │  Cluster     │            │   Render       │
    │  Manager     │            │   Manager      │
    │ ┌──────────┐ │            │ ┌────────────┐ │
    │ │Node Ctrl  │ │            │ │RenderDevice│ │
    │ │Failover   │ │            │ │SyncPolicy  │ │
    │ │NetApi     │ │            │ │Projection  │ │
    │ └──────────┘ │            │ └────────────┘ │
    └──────────────┘            └────────────────┘
           │                           │
    ┌──────┴───────────────────────────┴──────┐
    │         Network (TCP/SharedMemory)       │
    │  Primary Node  ◄──── Sync ────► Secondary│
    └─────────────────────────────────────────┘
```

## 蓝图用法

> **注意**：许多蓝图函数已从 `IDisplayClusterBlueprintAPI` 迁移到 `UDisplayClusterBlueprintLib`（5.4+），在蓝图编辑器中搜索 **"nDisplay"** 节点类即可找到。

### 集群节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IsPrimary` | 判断当前节点是否为 Primary 节点 | `UDisplayClusterBlueprintLib` |
| `IsSecondary` | 判断当前节点是否为 Secondary 节点 | `UDisplayClusterBlueprintLib` |
| `IsBackup` | 判断当前节点是否为 Backup 节点 | `UDisplayClusterBlueprintLib` |
| `GetClusterRole` | 获取当前节点的集群角色 | `UDisplayClusterBlueprintLib` |
| `GetNodeId` | 获取当前节点ID | `UDisplayClusterBlueprintLib` |
| `GetActiveNodeIds` | 获取所有活跃节点ID列表 | `UDisplayClusterBlueprintLib` |
| `GetActiveNodesAmount` | 获取活跃节点数量 | `UDisplayClusterBlueprintLib` |
| `GetOperationMode` | 获取当前操作模式（Cluster/Editor/Disabled） | `UDisplayClusterBlueprintLib` |
| `GetRootActor` | 获取 nDisplay Root Actor | `UDisplayClusterBlueprintLib` |

### 集群事件

| 节点 | 说明 | 所在类 |
|---|---|---|
| `EmitClusterEventJson` | 发送 JSON 格式的集群事件 | `UDisplayClusterBlueprintLib` |
| `EmitClusterEventBinary` | 发送二进制格式的集群事件 | `UDisplayClusterBlueprintLib` |
| `AddClusterEventListener` | 添加集群事件监听器 | `UDisplayClusterBlueprintLib` |
| `RemoveClusterEventListener` | 移除集群事件监听器 | `UDisplayClusterBlueprintLib` |
| `SendClusterEventJsonTo` | 向特定地址发送 JSON 集群事件（集群外） | `UDisplayClusterBlueprintLib` |

### Camera 组件

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetInterpupillaryDistance` | 获取瞳距（立体模式） | `UDisplayClusterCameraComponent` |
| `SetInterpupillaryDistance` | 设置瞳距 | `UDisplayClusterCameraComponent` |
| `GetSwapEyes` | 获取双眼交换状态 | `UDisplayClusterCameraComponent` |
| `SetSwapEyes` | 设置双眼交换 | `UDisplayClusterCameraComponent` |
| `ToggleSwapEyes` | 切换双眼交换 | `UDisplayClusterCameraComponent` |

### ICVFX Camera 组件

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IsICVFXEnabled` | 判断此摄像机在当前节点是否激活 | `UDisplayClusterICVFXCameraComponent` |
| `GetActualCineCameraComponent` | 获取实际的 CineCamera 组件 | `UDisplayClusterICVFXCameraComponent` |
| `SetDepthOfFieldParameters` | 设置景深参数并更新补偿LUT | `UDisplayClusterICVFXCameraComponent` |

### Root Actor

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetFlushPositionAndNormal` | 获取舞台几何体上贴合位置和法线 | `ADisplayClusterRootActor` |
| `MakeStageActorFlushToWall` | 使 Stage Actor 贴合墙壁 | `ADisplayClusterRootActor` |
| `GetDistanceToStageGeometry` | 获取到舞台几何体的距离 | `ADisplayClusterRootActor` |
| `SetReplaceTextureFlagForAllViewports` | 为所有视口设置纹理替换标志 | `ADisplayClusterRootActor` |
| `SetFreezeOuterViewports` | 冻结/解冻外视锥视口 | `ADisplayClusterRootActor` |
| `UpdateProceduralMeshComponentData` | 更新程序化网格组件数据 | `ADisplayClusterRootActor` |

### 使用示例（蓝图描述）

**集群事件收发示例**：
1. 创建一个 Blueprint，添加 `IDisplayClusterClusterEventListener` 接口
2. 在 Event Graph 中使用 `Add Cluster Event Listener` 节点注册监听（Self 作为 Listener）
3. 实现 `OnClusterEventJson` 事件处理接收到的 JSON 事件
4. 使用 `Emit Cluster Event Json` 节点发送事件，构造 `FDisplayClusterClusterEventJson` 结构体填入 Category 和 Type

**获取节点角色示例**：
1. 使用 `Get Cluster Role` 节点获取当前角色
2. 比较返回值：`Primary` / `Secondary` / `Backup` / `None`
3. 根据角色执行不同逻辑（例如只有 Primary 节点控制全局状态）

## C++ 用法

### 头文件引入

```cpp
#include "DisplayClusterRootActor.h"
#include "DisplayClusterCameraComponent.h"
#include "DisplayClusterICVFXCameraComponent.h"
#include "IDisplayCluster.h"
#include "IDisplayClusterClusterManager.h"
#include "IDisplayClusterRenderManager.h"
#include "IDisplayClusterCallbacks.h"
#include "IDisplayClusterViewportManager.h"
```

### 基本用法 — 访问 nDisplay 模块

```cpp
// 获取 nDisplay 模块单例
if (IDisplayCluster::IsAvailable())
{
    IDisplayCluster& DC = IDisplayCluster::Get();

    // 获取操作模式
    EDisplayClusterOperationMode Mode = DC.GetOperationMode();

    // 获取各管理器
    IDisplayClusterClusterManager* ClusterMgr = DC.GetClusterMgr();
    IDisplayClusterRenderManager*  RenderMgr  = DC.GetRenderMgr();

    // 判断当前节点角色
    if (ClusterMgr)
    {
        bool bPrimary = ClusterMgr->IsPrimary();
        FString NodeId = ClusterMgr->GetNodeId();
        uint32 NodeCount = ClusterMgr->GetNodesAmount();
    }
}
```

### 集群事件收发

```cpp
// 发送 JSON 集群事件
IDisplayClusterClusterManager* ClusterMgr = IDisplayCluster::Get().GetClusterMgr();
if (ClusterMgr)
{
    FDisplayClusterClusterEventJson Event;
    Event.Category = TEXT("MyCategory");
    Event.Type = TEXT("MyEventType");
    Event.Name = TEXT("MyEventName");
    Event.bIsSystemEvent = false;
    Event.Parameters.Add(TEXT("Key"), TEXT("Value"));

    // bPrimaryOnly=true 表示只有 Primary 节点会广播此事件
    ClusterMgr->EmitClusterEventJson(Event, true);
}

// 监听集群事件
FOnClusterEventJsonListener Listener;
Listener.BindLambda([](const FDisplayClusterClusterEventJson& Event)
{
    UE_LOG(LogTemp, Log, TEXT("Received event: %s/%s"), *Event.Category, *Event.Type);
});
ClusterMgr->AddClusterEventJsonListener(Listener);
```

### 自定义状态同步

```cpp
// 创建分布式自定义状态（集群范围自动同步）
#include "DisplayClusterCustomStateDistributed.h"

// 使用工厂方法创建状态（自动注册到集群管理器）
TSharedPtr<TDistributedCustomState<FMyStateData>> MyState =
    TDistributedCustomState<FMyStateData>::Create(FName("MyUniqueState"));

if (MyState)
{
    // 设置本地数据（下一帧生效）
    MyState->SetData(NewData);

    // 获取本地数据
    const FMyStateData& LocalData = MyState->GetData();

    // 获取其他节点的数据
    const FMyStateData& NodeData = MyState->GetData(FName("OtherNodeId"));

    // 获取所有可用节点
    TSet<FName> Nodes = MyState->GetAvailableNodes();
}
```

### 注册回调

```cpp
#include "IDisplayClusterCallbacks.h"

IDisplayClusterCallbacks& Callbacks = IDisplayCluster::Get().GetCallbacks();

// 会话开始回调
FDelegateHandle SessionStartHandle = Callbacks.OnDisplayClusterStartSession().AddLambda([]()
{
    UE_LOG(LogTemp, Log, TEXT("nDisplay session started"));
});

// 渲染线程 Warp 回调
FDelegateHandle WarpHandle = Callbacks.OnDisplayClusterPreWarp_RenderThread().AddLambda(
    [](FRHICommandListImmediate& RHICmdList, const IDisplayClusterViewportManagerProxy* Proxy)
    {
        // 在 Warp/Blend 之前执行自定义操作
    });

// 清理
Callbacks.OnDisplayClusterStartSession().Remove(SessionStartHandle);
Callbacks.OnDisplayClusterPreWarp_RenderThread().Remove(WarpHandle);
```

### 注册自定义投影策略

```cpp
#include "IDisplayClusterRenderManager.h"

IDisplayClusterRenderManager* RenderMgr = IDisplayCluster::Get().GetRenderMgr();
if (RenderMgr)
{
    // 注册自定义投影策略工厂
    TSharedPtr<IDisplayClusterProjectionPolicyFactory> MyFactory = MakeShared<FMyProjectionPolicyFactory>();
    RenderMgr->RegisterProjectionPolicyFactory(TEXT("MyProjection"), MyFactory);
}
```

## Demo 示例

以下是一个最小的自定义投影策略工厂和集群事件监听示例：

```cpp
// MyDisplayClusterModule.h
#pragma once

#include "IDisplayCluster.h"
#include "IDisplayClusterClusterManager.h"
#include "IDisplayClusterCallbacks.h"

class FMyDisplayClusterListener
{
public:
    void StartListening()
    {
        if (!IDisplayCluster::IsAvailable())
        {
            return;
        }

        IDisplayCluster& DC = IDisplayCluster::Get();
        IDisplayClusterClusterManager* ClusterMgr = DC.GetClusterMgr();
        IDisplayClusterCallbacks& Callbacks = DC.GetCallbacks();

        // 监听 JSON 集群事件
        if (ClusterMgr)
        {
            ClusterEventListener.BindRaw(this, &FMyDisplayClusterListener::OnClusterEvent);
            ClusterMgr->AddClusterEventJsonListener(ClusterEventListener);
        }

        // 监听会话生命周期
        SessionEndHandle = Callbacks.OnDisplayClusterEndSession().AddRaw(
            this, &FMyDisplayClusterListener::OnSessionEnd);
    }

    void StopListening()
    {
        if (!IDisplayCluster::IsAvailable())
        {
            return;
        }

        IDisplayCluster& DC = IDisplayCluster::Get();
        IDisplayClusterClusterManager* ClusterMgr = DC.GetClusterMgr();
        IDisplayClusterCallbacks& Callbacks = DC.GetCallbacks();

        if (ClusterMgr)
        {
            ClusterMgr->RemoveClusterEventJsonListener(ClusterEventListener);
        }
        Callbacks.OnDisplayClusterEndSession().Remove(SessionEndHandle);
    }

private:
    void OnClusterEvent(const FDisplayClusterClusterEventJson& Event)
    {
        UE_LOG(LogTemp, Log, TEXT("Received cluster event: Category=%s Type=%s Name=%s"),
            *Event.Category, *Event.Type, *Event.Name);

        // 处理特定事件
        if (Event.Type == TEXT("CustomCommand"))
        {
            const FString* ParamValue = Event.Parameters.Find(TEXT("Action"));
            if (ParamValue && *ParamValue == TEXT("ResetScene"))
            {
                // 执行自定义逻辑...
            }
        }
    }

    void OnSessionEnd()
    {
        UE_LOG(LogTemp, Log, TEXT("nDisplay session ended"));
    }

    FOnClusterEventJsonListener ClusterEventListener;
    FDelegateHandle SessionEndHandle;
};
```

## 模块依赖

nDisplay 的模块间依赖复杂且广泛。以下是**不常见**的、使用者需要特别注意的依赖：

| 模块 | 用途 |
|---|---|
| `DisplayClusterConfiguration` | nDisplay 配置数据模型（视口、投影、集群节点定义） |
| `DisplayClusterReplication` | 集群数据复制协议实现 |
| `DisplayClusterWarp` | Warp/Blend 扭曲混合渲染管线 |
| `DisplayClusterShaders` | nDisplay 自定义着色器（ICVFX、WarpBlend、LightCard 等） |
| `DisplayClusterProjection` | 投影策略实现（MPCDI、Mesh、EasyBlend 等） |
| `SharedMemoryMedia` | 共享内存媒体传输（GPU 间/节点间高效纹理传输） |
| `ScalableMPCDI` (External) | 第三方 MPCDI（Multi-Projector Common Data Interchange）库 |
| `D3D12RHI` | Direct3D 12 渲染硬件接口（用于共享内存媒体） |
| `MediaUtils` | 媒体框架工具（媒体输入/输出支持） |

**常见但需注意的依赖**：DisplayCluster 和 DisplayClusterMedia 依赖 `UnrealEd`、`LevelEditor`（编辑器集成）；DisplayClusterMonitor 依赖 `UnrealEd`。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | MovieGraph 管线新增 EXR 多层支持 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | MoviePipeline 中将 WarpBlendAlpha 模式合并到 WarpBlend |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复 MRG 中拓扑感知的摄像机命名及 MPCDI/ICVFX 着色器的不透明 Alpha 问题 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 在输出帧编码回退时正确处理非默认 DisplayGamma |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复 GUI 纹理尺寸小于视口尺寸时的闪烁问题 |

### 维护评价

- **创建时间**：2018 年 6 月（UE 4.20 时代），至今约 8 年
- **最近更新**：2026 年 5 月持续有功能性更新（MovieGraph、着色器修复、Gamma 处理等）
- **维护状态**：🟢 **活跃维护** — 由 Epic Games 核心团队持续维护，是虚拟制作管线的关键组件
- **已知限制**：
  - `EnabledByDefault=false`，需要在项目设置中手动启用
  - 仅支持 Win64 和 Linux 平台
  - 集群模式需要网络环境配置
  - 多个模块标记为 Runtime 但依赖 UnrealEd，表明存在编辑器/运行时混合逻辑
- **推荐程度**：⭐⭐⭐⭐⭐ — 如果你的项目涉及虚拟制作、LED 墙、CAVE 系统或多屏渲染，这是必须使用的核心插件

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- 官方文档：（.uplugin 中未提供 DocsURL）
- 测试用例：`Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests/`