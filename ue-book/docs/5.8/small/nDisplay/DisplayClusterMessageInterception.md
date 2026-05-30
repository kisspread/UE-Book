# nDisplay — DisplayClusterMessageInterception

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 集群显示插件 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产、材质模板、编辑器工具、着色器） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 🏛️ 文物（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

> **注意**：nDisplay 是一个超大型插件（xlarge，1351+ 源文件，29 个模块）。本文档聚焦于 **DisplayClusterMessageInterception** 模块。其他子模块（投影、变形、媒体、调色等）需要各自独立文档。

---

## 用途

**nDisplay** 是 Unreal Engine 的集群渲染框架，允许多台 PC 协同同步渲染同一场景，用于大规模显示墙、LED Volume（虚拟制片）、CAVE 系统、穹顶投影等专业场景。

**DisplayClusterMessageInterception** 模块解决的核心问题是：**多机集群中的消息总线同步**。在集群模式下，所有节点运行相同的 UE 实例，但只有主节点（Primary Node）应处理某些消息（如 Multi-User 编辑事件）。此模块拦截消息总线（MessageBus）上的消息，在集群中同步分发，确保所有节点以一致的顺序和时机处理消息，避免状态不一致。

## 使用场景

- 你在构建 **LED Volume 虚拟制片**（如 ICVFX） → 使用 nDisplay 配合 DisplayClusterMessageInterception 确保多台渲染机器消息同步
- 你在搭建 **多通道投影 CAVE/穹顶系统** → nDisplay 管理多个视口和投影校正
- 你使用 **Multi-User Editing** 配合 nDisplay 集群 → MessageInterception 拦截并同步 Multi-User 消息，防止集群中只有部分节点收到编辑变更
- 你需要 **Movie Pipeline 录制** nDisplay 集群画面 → 配合 DisplayClusterMoviePipeline 模块

## 蓝图用法

DisplayClusterMessageInterception 主要是一个 **运行时底层同步系统**，没有暴露 BlueprintCallable 节点。其配置通过 `UDisplayClusterMessageInterceptionSettings` 的 `config=Engine` 属性暴露在项目设置中。

### 配置属性

| 属性 | 类型 | 说明 | 所在类 |
|---|---|---|---|
| `bIsEnabled` | bool | 是否启用消息拦截 | `UDisplayClusterMessageInterceptionSettings` |
| `bInterceptMultiUserMessages` | bool | 是否拦截 Multi-User 消息 | `UDisplayClusterMessageInterceptionSettings` |
| `TimeoutSeconds` | float | 消息等待集群同步的最大秒数 | `UDisplayClusterMessageInterceptionSettings` |

### 使用示例（配置方式）

在 **项目设置 → Engine → DisplayCluster Message Interception Settings** 中：

1. 勾选 **Is Enabled** → 启用消息拦截
2. 勾选 **Intercept Multi User Messages** → 让 Multi-User 编辑事件在集群中同步
3. 设置 **Timeout Seconds**（默认 1.0s）→ 控制消息等待超时，超时后强制转发

## C++ 用法

### 头文件引入

```cpp
#include "DisplayClusterMessageInterceptor.h"
#include "DisplayClusterMessageInterceptionSettings.h"
```

### 基本用法

核心类 `FDisplayClusterMessageInterceptor` 同时实现了 `IMessageInterceptor` 和 `IMessageSender` 接口，嵌入 MessageBus 管道中拦截并同步消息。

```cpp
// 来源: Private/DisplayClusterMessageInterceptor.h

// 创建拦截器实例
TSharedRef<FDisplayClusterMessageInterceptor> Interceptor = MakeShared<FDisplayClusterMessageInterceptor>();

// 初始化，绑定集群管理器和配置
FMessageInterceptionSettings Settings;
Settings.bIsEnabled = true;
Settings.bInterceptMultiUserMessages = true;
Settings.TimeoutSeconds = 1.0f;

Interceptor->Setup(ClusterManager, Settings);

// 启动拦截，绑定到消息总线
Interceptor->Start(MessageBus);
```

### 进阶用法

拦截器在集群事件驱动下工作：当集群节点确认收到消息后，主节点收集确认信息，所有节点到齐后才放行消息。

```cpp
// 来源: Private/DisplayClusterMessageInterceptor.h

// 在集群消息同步循环中调用（通常由集群管理器驱动）
Interceptor->SyncMessages();

// 处理来自集群节点的事件（节点确认收到消息）
FDisplayClusterClusterEventJson ClusterEvent;
Interceptor->HandleClusterEvent(ClusterEvent);

// 处理集群节点断连
Interceptor->HandleClusterNodeFailure(TEXT("Node-2"));

// 停止拦截
Interceptor->Stop();
```

消息拦截的内部流程：
1. `InterceptMessage()` 被 MessageBus 回调，将消息暂存到 `ContextMap`
2. 主节点通过集群事件将消息 ID 广播给所有节点
3. 各节点收到后回复确认
4. `SyncMessages()` 检查 `FContextSync::NodesReceived` 集合，当所有节点确认后调用 `Purge()` 放行消息
5. 超时（`TimeoutSeconds`）后也会强制放行，避免死锁

## Demo 示例

```cpp
// MyClusterApp.h
#pragma once

#include "CoreMinimal.h"

class FMyClusterMessageSync
{
public:
    void Initialize(class IDisplayClusterClusterManager* ClusterMgr, TSharedPtr<IMessageBus, ESPMode::ThreadSafe> Bus);
    void Shutdown();
    void Tick();

private:
    TSharedPtr<class FDisplayClusterMessageInterceptor, ESPMode::ThreadSafe> MessageInterceptor;
};
```

```cpp
// MyClusterApp.cpp
#include "MyClusterApp.h"
#include "DisplayClusterMessageInterceptor.h"
#include "DisplayClusterMessageInterceptionSettings.h"

void FMyClusterMessageSync::Initialize(
    IDisplayClusterClusterManager* ClusterMgr,
    TSharedPtr<IMessageBus, ESPMode::ThreadSafe> Bus)
{
    // 读取项目设置中的拦截配置
    const UDisplayClusterMessageInterceptionSettings* Settings =
        GetDefault<UDisplayClusterMessageInterceptionSettings>();

    if (Settings && Settings->InterceptionSettings.bIsEnabled)
    {
        MessageInterceptor = MakeShared<FDisplayClusterMessageInterceptor>();
        MessageInterceptor->Setup(ClusterMgr, Settings->InterceptionSettings);
        MessageInterceptor->Start(Bus);
    }
}

void FMyClusterMessageSync::Shutdown()
{
    if (MessageInterceptor.IsValid())
    {
        MessageInterceptor->Stop();
        MessageInterceptor.Reset();
    }
}

void FMyClusterMessageSync::Tick()
{
    if (MessageInterceptor.IsValid())
    {
        // 每帧检查集群中各节点的消息确认状态
        MessageInterceptor->SyncMessages();
    }
}
```

## 模块依赖

DisplayClusterMessageInterception 模块本身**无特殊依赖**（仅标准 Core/Engine/Slate 等）。

nDisplay 插件整体的独特依赖如下：

| 模块 | 用途 |
|---|---|
| `EditorWidgets` | 编辑器自定义控件（DisplayCluster 配置界面） |
| `LevelEditor` | 关卡编辑器集成（nDisplay 面板嵌入） |
| `D3D12RHI` | Direct3D 12 渲染硬件接口（SharedMemoryMedia 媒体共享） |

> ⚠️ 注意：nDisplay 的其他子模块可能依赖 `MPCDI`、`OpenCV`、`NDI` 等第三方库，此处仅列出 Build.cs 中明确声明的公共依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | MovieGraph 支持 EXR 多图层输出 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 合并 WarpBlendAlpha 模式到 WarpBlend |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复 MRG 相机命名和 MPCDI/ICVFX 着色器透明度 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 输出帧编码时正确处理非默认 DisplayGamma |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复 GUI 纹理小于视口时的闪烁问题 |

### 维护评价

nDisplay 是 **Epic Games 活跃维护的核心企业级插件**：

- ✅ **持续活跃**：2026 年 5 月有多次密集更新，聚焦于 MovieGraph、着色器修复、媒体管线改进
- ✅ **功能不断演进**：从 2018 年 UE 4.20 发布以来，持续增加 ICVFX（虚拟制片）、Movie Pipeline、Multi-User、Stage Monitoring 等功能
- ✅ **Epic 官方支持**：用于 Fortnite 的 LED Volume 虚拟制片等内部场景
- ⚠️ **复杂度极高**：29 个模块、1351+ 源文件，学习曲线陡峭
- ⚠️ **默认未启用**：`EnabledByDefault=false`，需要手动在插件列表中启用
- ⚠️ **DisplayClusterMessageInterception 模块**：作为底层同步机制，普通用户通常不需要直接接触，由 nDisplay 框架内部自动调用

**推荐使用**：如果你的项目涉及多机集群渲染、LED Volume 虚拟制片或多通道投影，nDisplay 是唯一选择且质量可靠。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/n-display-in-unreal-engine)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests)