# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 集群渲染 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器资产、着色器、配置模板） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是 UE5 中用于驱动**多机集群同步渲染**的完整解决方案。它解决的核心问题是：如何让多台 PC 各自渲染画面的不同部分（或同一场景的不同视角），并将它们精确拼合成一个无缝的大画面。

典型硬件拓扑包括：

- **LED 墙（LED Volume）**：虚拟制片中常见的 ICVFX（In-Camera VFX）场景，多块 LED 屏幕由不同渲染节点驱动，需要严格帧同步和几何校正
- **CAVE 系统**：沉浸式投影环境，多个投影仪从不同方向投射画面到房间墙壁上
- **穹顶/弧幕**：天文馆、飞行模拟器等超宽视角显示系统
- **多通道同步回放**：Movie Pipeline 集成，将 nDisplay 配置渲染为 EXR 序列文件

插件包含 29 个模块，涵盖：投影几何校正（Warp/Blend）、MPCDI 配置支持、色彩分级、媒体输入/输出、共享内存传输、多用户编辑同步、远程控制、舞台监控、消息总线拦截同步等完整功能栈。

> **注意**：此插件默认未启用（`EnabledByDefault: false`），需要在项目的 `.uproject` 或编辑器插件管理器中手动启用。

## 本文档聚焦模块：DisplayClusterMessageInterception

本模块负责在集群渲染的多台 PC 之间**拦截并同步 Unreal 消息总线（MessageBus）消息**。

在 nDisplay 集群中，每台渲染节点都是一个独立的 UE 实例。当某个节点收到消息（如 UI 交互事件、游戏逻辑事件、Multi-User 编辑操作等）时，如果其他节点没有同步收到相同消息，画面状态就会不一致。本模块通过拦截 MessageBus 消息，将其广播到集群所有节点，在确认所有节点都收到后再统一放行，从而保证集群状态同步。

### 核心机制

```
节点A 收到消息 → 拦截器截获 → 广播到集群
                                   ├── 节点A 确认收到 ✓
                                   ├── 节点B 确认收到 ✓
                                   └── 节点C 确认收到 ✓
                               → 全部确认 → 放行消息到各节点本地处理
```

如果超过配置的超时时间（默认 1.0 秒）仍有节点未确认，消息会被强制放行（Purge）以避免阻塞。

## 使用场景

- 你正在搭建虚拟制片 LED 墙 → 需要 nDisplay 集群渲染 + MessageInterception 保证 Multi-User 编辑同步
- 你在构建 CAVE 沉浸式投影系统 → 需要 nDisplay 的投影校正 + 消息同步
- 你用多个 PC 驱动环绕显示器 → 需要 nDisplay 的 Warp/Blend 和帧同步
- 你使用 Multi-User 编辑操作 nDisplay 集群 → MessageInterception 确保编辑操作在所有节点同步执行

## 蓝图用法

本模块的核心类 `FDisplayClusterMessageInterceptor` 是纯 C++ 类（非 UObject），不暴露蓝图节点。配置通过 `UDisplayClusterMessageInterceptionSettings` 在编辑器设置中管理。

### 设置面板

在 **编辑器 → 项目设置 → Display Cluster → Interception Settings** 中可配置：

| 设置项 | 说明 | 默认值 |
|---|---|---|
| `bIsEnabled` | 是否启用消息拦截 | `true` |
| `bInterceptMultiUserMessages` | 是否拦截 Multi-User 消息 | `true` |
| `TimeoutSeconds` | 等待集群同步的最大秒数 | `1.0` |

> 注意：主节点（Primary Node）的设置会自动同步到集群所有节点。

## C++ 用法

### 头文件引入

```cpp
#include "DisplayClusterMessageInterceptor.h"
#include "DisplayClusterMessageInterceptionSettings.h"
```

### 基本用法

创建拦截器并绑定到集群管理器和消息总线：

```cpp
// 基于 DisplayClusterMessageInterceptor.h 核心 API

// 1. 创建拦截器实例
TSharedRef<FDisplayClusterMessageInterceptor> Interceptor =
    MakeShared<FDisplayClusterMessageInterceptor>();

// 2. 获取集群管理器和拦截设置
IDisplayClusterClusterManager* ClusterManager = /* 从子系统获取 */;
FMessageInterceptionSettings Settings;
Settings.bIsEnabled = true;
Settings.bInterceptMultiUserMessages = true;
Settings.TimeoutSeconds = 1.0f;

// 3. 初始化：绑定集群管理器和设置
Interceptor->Setup(ClusterManager, Settings);

// 4. 启动：绑定到消息总线，开始拦截
TSharedPtr<IMessageBus, ESPMode::ThreadSafe> Bus = /* 获取消息总线 */;
Interceptor->Start(Bus);

// 5. 周期性同步（通常在 Tick 或集群同步回调中调用）
Interceptor->SyncMessages();

// 6. 停止拦截
Interceptor->Stop();
```

### 进阶用法

处理集群事件和节点故障：

```cpp
// 监听集群事件并转发给拦截器
void OnClusterEvent(const FDisplayClusterClusterEventJson& Event)
{
    // 拦截器内部会根据事件更新消息同步状态
    Interceptor->HandleClusterEvent(Event);
}

// 处理节点故障：当集群中某节点断开时
void OnNodeFailure(const FString& FailedNodeId)
{
    // 从所有待同步消息的确认集合中移除该节点
    // 避免因为离线节点导致所有消息超时
    Interceptor->HandleClusterNodeFailure(FailedNodeId);
}
```

自定义消息拦截描述：

```cpp
// FInterceptedMessageDescriptor 用于描述需要拦截的消息类型
TArray<FTopLevelAssetPath> MessageTypes;
MessageTypes.Add(FTopLevelAssetPath(TEXT("/Script/MyModule.MyMessage")));
FInterceptedMessageDescriptor Descriptor(MoveTemp(MessageTypes), FName("MySyncGroup"));
```

## Demo 示例

```cpp
// MyClusterSyncSubsystem.h
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "DisplayClusterMessageInterceptor.h"
#include "MyClusterSyncSubsystem.generated.h"

UCLASS()
class UMyClusterSyncSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

    /** 每帧调用以推进消息同步 */
    void TickMessages();

private:
    TSharedPtr<FDisplayClusterMessageInterceptor> MessageInterceptor;
};

// MyClusterSyncSubsystem.cpp
#include "MyClusterSyncSubsystem.h"
#include "DisplayClusterClusterManager.h"
#include "DisplayClusterMessageInterceptionSettings.h"
#include "IMessageBus.h"
#include "MessageEndpointBuilder.h"

void UMyClusterSyncSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);

    // 获取集群管理器（假设已由 nDisplay 核心模块初始化）
    IDisplayClusterClusterManager* ClusterMgr = nullptr;
    // 实际使用时通过 GEngine->GetEngineSubsystem 或类似途径获取

    // 从配置中读取拦截设置
    UDisplayClusterMessageInterceptionSettings* Settings =
        GetMutableDefault<UDisplayClusterMessageInterceptionSettings>();

    // 创建并初始化拦截器
    MessageInterceptor = MakeShared<FDisplayClusterMessageInterceptor>();
    MessageInterceptor->Setup(ClusterMgr, Settings->InterceptionSettings);

    // 获取消息总线并启动拦截
    // 实际使用时从 FMessageEndpoint::GetBus() 获取
    // MessageInterceptor->Start(Bus);
}

void UMyClusterSyncSubsystem::Deinitialize()
{
    if (MessageInterceptor.IsValid())
    {
        MessageInterceptor->Stop();
        MessageInterceptor.Reset();
    }
    Super::Deinitialize();
}

void UMyClusterSyncSubsystem::TickMessages()
{
    if (MessageInterceptor.IsValid())
    {
        // 推进消息同步，检查所有节点是否已确认
        MessageInterceptor->SyncMessages();
    }
}
```

## 模块依赖

本模块（DisplayClusterMessageInterception）依赖关系从源码引用推断：

| 模块 | 用途 |
|---|---|
| `DisplayCluster` | nDisplay 核心模块，提供 `IDisplayClusterClusterManager` 集群管理接口 |
| `Messaging` | Unreal 消息总线框架，提供 `IMessageBus`、`IMessageInterceptor`、`IMessageSender` 接口 |

> nDisplay 插件整体还依赖：`D3D12RHI`、`MediaUtils`、`MPCDI` 等，但这些是其他子模块的依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | MovieGraph 管线支持 EXR 多层渲染输出 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | MoviePipeline 中合并 WarpBlendAlpha 模式到 WarpBlend |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复 MRG 中拓扑感知相机命名及 MPCDI/ICVFX 着色器不透明度问题 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 输出帧编码回退时正确处理非默认 DisplayGamma |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复 GUI 纹理尺寸小于视口尺寸时的闪烁问题 |

### 维护评价

**🟢 活跃维护中**

- **创建时间**：2018 年（UE 4.20 时期），已有约 8 年历史
- **最近更新频率**：2026 年 5 月内有 5 次提交，更新非常频繁
- **维护内容**：持续的功能增强（EXR 多层、MovieGraph 集成）和 bug 修复，功能仍在积极扩展
- **代码规模**：1351 个源文件，29 个模块，是 UE5 中最大的官方插件之一
- **是否推荐使用**：✅ 是。这是 Epic 官方维护的虚拟制片/集群渲染核心插件，广泛应用于行业项目

> **特别说明**：虽然许多模块名中包含 "Editor"（如 `DisplayClusterEditor`、`DisplayClusterConfigurator`），但它们均标记为 Runtime 类型。这是因为 nDisplay 的编辑器工作流与运行时紧密耦合，需要在打包后的应用中也能访问部分编辑器功能。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/en-US/RenderingAndGraphics/nDisplay/)（UE 官方 nDisplay 文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests)