# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 集群渲染同步 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产、着色器） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是 UE5 的**集群渲染同步系统**，用于将单个 UE5 应用程序的内容同步分发到多台 PC 和多个显示输出。核心用途包括：

- **LED 虚拟制片**：配合 LED 墙进行实时渲染，将画面同步输出到多块 LED 屏幕
- **CAVE 沉浸式环境**：在多面投影的 CAVE（Cave Automatic Virtual Environment）中实现立体渲染
- **多屏同步显示**：大型展览、主题公园、驾驶模拟器等需要多台机器同步渲染的场景
- **投影校正与变形**：支持 MPCDI、Mesh 等投影校正格式

该插件**默认不启用**，需要手动在项目设置中开启。

## 模块架构

```
nDisplay/
├── Core & Runtime
│   ├── DisplayCluster              ← 核心集群管理、通信、渲染管线
│   ├── DisplayClusterConfiguration ← 配置文件解析（.ndisplay）
│   └── DisplayClusterReplication   ← 状态同步复制
│
├── Rendering & Shaders
│   ├── DisplayClusterShaders       ← 集群渲染着色器
│   ├── DisplayClusterProjection    ← 投影映射（MPCDI、Mesh）
│   ├── DisplayClusterWarp          ← 变形校正
│   ├── DisplayClusterColorGrading  ← 颜色校准
│   └── DisplayClusterFillDerivedDataCache ← DDC 预填充
│
├── Media & Interchange
│   ├── DisplayClusterMedia         ← 媒体输入输出
│   ├── DisplayClusterMediaEditor   ← 媒体编辑器
│   └── SharedMemoryMedia           ← 共享内存传输
│
├── Synchronization
│   ├── DisplayClusterMessageInterception ← 消息总线拦截同步
│   ├── DisplayClusterMultiUser     ← 多用户同步
│   └── DisplayClusterRemoteControlInterceptor ← 远程控制拦截
│
├── Movie Pipeline
│   ├── DisplayClusterMoviePipeline      ← 录制支持
│   └── DisplayClusterMoviePipelineEditor ← 录制编辑器
│
├── Editor Tools
│   ├── DisplayClusterEditor        ← 编辑器集成
│   ├── DisplayClusterConfigurator  ← 配置编辑器
│   ├── DisplayClusterDetails       ← 属性面板
│   ├── DisplayClusterOperator      ← 操作器
│   ├── DisplayClusterLightCardEditor ← Light Card 编辑
│   └── DisplayClusterLightCardEditorShaders ← Light Card 着色器
│
├── Monitoring
│   ├── DisplayClusterMonitor       ← 集群监控
│   ├── DisplayClusterMonitorEditor ← 监控编辑器
│   └── DisplayClusterStageMonitoring ← 舞台监控
│
├── Scene
│   └── DisplayClusterScenePreview  ← 场景预览
│
└── External
    └── ScalableMPCDI               ← MPCDI 第三方库
```

## 子模块文档

本文档重点介绍 `DisplayClusterMessageInterception` 模块。

---

# DisplayClusterMessageInterception

> 消息总线拦截同步模块，用于在集群节点间同步 UE 消息总线事件

| 属性 | 值 |
|---|---|
| 中文名 | 消息拦截同步 |
| 分类 | Misc (nDisplay) |
| 默认启用 | ❌ 否（随 nDisplay 插件） |
| 包含内容 | ❌ 无 |
| 模块 | `DisplayClusterMessageInterception` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterMessageInterceptor) | |

## 用途

该模块解决的核心问题：在 nDisplay 集群环境中，当一个节点触发 UE 消息总线（MessageBus）消息时，需要确保**所有集群节点**都接收到并处理该消息，保持状态一致。

### 为什么需要消息拦截？

在集群渲染中，多台 PC 各自运行独立的 UE 实例。当某个节点（如主节点）发出消息（例如 UI 变更、物体状态变化），其他节点需要：
1. **接收**相同的消息
2. **同步**处理时机
3. **确认**所有节点都已处理

`FDisplayClusterMessageInterceptor` 实现了 `IMessageInterceptor` 接口，在消息总线上拦截特定消息，通过集群事件同步机制确保所有节点同步处理。

## 使用场景

- 你使用 nDisplay 进行 LED 虚拟制片，需要在所有节点上同步材质参数变更
- 你有多个渲染节点组成 CAVE 环境，需要同步触发某个蓝图事件
- 你在使用 nDisplay 的 Multi-User 编辑功能，需要确保操作同步

## 配置用法

### 项目设置

该模块通过 `UDisplayClusterMessageInterceptionSettings` 提供配置项：

| 设置项 | 默认值 | 说明 |
|---|---|---|
| `bIsEnabled` | `true` | 是否启用消息拦截 |
| `bInterceptMultiUserMessages` | `true` | 是否拦截多用户编辑消息 |
| `TimeoutSeconds` | `1.0f` | 消息同步最大等待时间（秒） |

### 配置路径

编辑器中：**Project Settings → Plugins → nDisplay → Message Interception**

## C++ 用法

### 头文件引入

```cpp
#include "DisplayClusterMessageInterceptor.h"
#include "DisplayClusterMessageInterceptionSettings.h"
```

### 基本用法

```cpp
// 创建消息拦截器
TSharedRef<FDisplayClusterMessageInterceptor> Interceptor = MakeShared<FDisplayClusterMessageInterceptor>();

// 初始化，关联集群管理器
FMessageInterceptionSettings Settings;
Settings.bIsEnabled = true;
Settings.bInterceptMultiUserMessages = true;
Settings.TimeoutSeconds = 1.5f;

Interceptor->Setup(ClusterManager, Settings);

// 启动拦截，关联消息总线
Interceptor->Start(MessageBus);

// 在每帧或定期调用同步
Interceptor->SyncMessages();

// 停止拦截
Interceptor->Stop();
```

### 进阶用法

处理集群节点故障：

```cpp
// 当某个集群节点掉线时，需要通知拦截器释放等待中的消息
Interceptor->HandleClusterNodeFailure(FailedNodeId);

// 手动触发清理，强制转发所有滞留消息（超时保护）
// 内部会调用 Purge() 方法
```

### 核心类说明

| 类 | 说明 |
|---|---|
| `FDisplayClusterMessageInterceptor` | 核心拦截器，实现 `IMessageInterceptor` 和 `IMessageSender` |
| `FMessageInterceptionSettings` | 拦截配置结构体 |
| `UDisplayClusterMessageInterceptionSettings` | UObject 包装，用于项目设置持久化 |

## 模块依赖

| 模块 | 用途 |
|---|---|
| `DisplayCluster` | 集群管理器接口 (`IDisplayClusterClusterManager`) |
| `MessageBus` | UE 消息总线系统（核心依赖） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support | 新增 EXR 多层渲染支持 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | MoviePipeline 简化 WarpBlend 模式 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复拓扑感知相机命名和着色器透明度问题 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 修复输出帧编码的 Gamma 处理 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复 GUI 纹理尺寸不足导致的闪烁 |

### 维护评价

**活跃维护** ✅

- nDisplay 是 Epic 官方支持的企业级插件，用于虚拟制片（Virtual Production）核心场景
- 最近更新频繁（2026 年 5 月），持续修复 bug 和添加功能
- 作为 UE5 虚拟制片工作流的支柱组件，获得持续投资
- 推荐用于 LED 虚拟制片、CAVE 沉浸式环境、多屏集群渲染场景

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/nDisplay-in-Unreal-Engine/)