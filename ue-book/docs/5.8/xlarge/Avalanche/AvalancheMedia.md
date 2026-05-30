# Motion Design

> Compositing, designer and broadcasting tool.

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、场景模板） |
| 模块 | `Avalanche` (Runtime), `AvalancheAttribute` (Runtime), `AvalancheAttributeEditor` (Runtime), `AvalancheCamera` (Runtime), `AvalancheComponentVisualizers` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), `AvalancheEditorCore` (Runtime), `AvalancheEffectors` (Runtime), `AvalancheEffectorsEditor` (Runtime), `AvalancheFunctionalTest` (Runtime), `AvalancheInteractiveTools` (Runtime), `AvalancheInteractiveToolsRuntime` (Runtime), `AvalancheLevelViewport` (Runtime), `AvalancheMRQ` (Runtime), `AvalancheMRQEditor` (Runtime), `AvalancheMask` (Runtime), `AvalancheMaskEditor` (Runtime), `AvalancheMaterial` (Runtime), `AvalancheMedia` (Runtime), `AvalancheMediaEditor` (Runtime), `AvalancheModifiers` (Runtime), `AvalancheModifiersEditor` (Runtime), `AvalancheOutliner` (Runtime), `AvalanchePropertyAnimator` (Runtime), `AvalanchePropertyAnimatorEditor` (Runtime), `AvalancheRemoteControl` (Runtime), `AvalancheRemoteControlEditor` (Runtime), `AvalancheSVGEditor` (Runtime), `AvalancheSceneRig` (Runtime), `AvalancheSceneRigEditor` (Runtime), `AvalancheSceneTree` (Runtime), `AvalancheSequence` (Runtime), `AvalancheSequencer` (Runtime), `AvalancheShapes` (Runtime), `AvalancheShapesEditor` (Runtime), `AvalancheTag` (Runtime), `AvalancheTagEditor` (Runtime), `AvalancheText` (Runtime), `AvalancheTextEditor` (Runtime), `AvalancheTransition` (Runtime), `AvalancheTransitionEditor` (Runtime), `AvalancheViewport` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Motion Design（内部代号 Avalanche）是 Unreal Engine 中面向**虚拟制作与广播**的全栈动态图形设计系统。它解决的核心问题是：如何在实时渲染环境中完成传统上由 After Effects、Vizrt 等专用工具承担的**合成、动态图形设计与播出控制**工作。

具体来说，这个插件提供：

- **Playback 框架**：通过 Playback Graph 和 Playable 抽象层，将 Motion Design 资产（关卡、蓝图、材质等）作为可独立控制的"图形元素"进行加载、播放、过渡和卸载。
- **广播通道系统**：管理多个 Broadcast Channel，每个通道可配置不同的 Media Output（本地或远程），支持实时推流到视频硬件或网络设备。
- **Rundown 节目单管理**：提供类似电视播出系统的 Rundown 资产，支持模板（Template）、实例页（Page）、组合模板（Combo Template）、页面视图（View）等层级结构，实现节目编排与播出控制。
- **分布式播放**：通过消息总线实现 Client/Server 架构，编辑器作为 Client 向远程 Server 发送播放命令，支持多机协同渲染和分布式广播。
- **过渡逻辑**：通过 Transition Layer 和 Transition Logic 实现页面间的平滑过渡效果。
- **远程控制集成**：与 Remote Control 系统深度集成，通过 RC Preset 控制播放中资产的属性。
- **资产同步**：通过 Modular Feature 插件化架构支持跨机器的资产同步（Push/Pull/Compare）。

## 使用场景

- 你需要在虚拟制作棚中实时播出动态图形内容（新闻字幕、体育比分、天气图表等）
- 你正在做多通道广播，需要在同一场景中同时渲染多个独立的图形到不同的输出设备
- 你需要一个"节目单"系统来管理图形的顺序播出和过渡
- 你需要在多台机器之间分布式渲染和同步 Motion Design 资产
- 你需要通过外部控制协议（HTTP/WebSocket）远程控制 UE 中的图形播出

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetBroadcast` | 获取全局广播管理对象 | `UAvaBroadcast` |
| `StartBroadcast` | 启动所有通道的广播 | `UAvaBroadcast` |
| `StopBroadcast` | 停止所有通道的广播 | `UAvaBroadcast` |
| `IsBroadcastingAnyChannel` | 检查是否有通道正在广播 | `UAvaBroadcast` |
| `GetChannelViewportSize` | 获取当前通道的视口尺寸 | `UAvaBroadcastLibrary` |
| `GetChannelName` | 获取当前通道名称 | `UAvaBroadcastLibrary` |
| `GetChannelStatus` | 获取通道状态（Offline/Idle/Live） | `UAvaBroadcastLibrary` |
| `GetChannelType` | 获取通道类型（Program/Preview） | `UAvaBroadcastLibrary` |
| `GetPlayable` | 获取当前关卡关联的 Playable | `UAvaPlayableLibrary` |
| `UpdatePlayableRemoteControlValues` | 从过渡中注入 RC 值到当前 Playable | `UAvaPlayableLibrary` |
| `IsPlayableHidden` | 获取 Playable 的隐藏状态 | `UAvaPlayableLibrary` |
| `SetPlayableHidden` | 设置 Playable 的隐藏状态 | `UAvaPlayableLibrary` |
| `PlayableSyncEventLatent` | 发送集群同步事件（延迟节点） | `UAvaPlayableLibrary` |

### 使用示例（蓝图描述）

**获取广播通道信息**：
1. 创建一个 `Get Broadcast` 节点获取 `UAvaBroadcast` 对象。
2. 使用 `Get Channel Status` 节点（输入通道名称）查询通道状态。
3. 分支判断：`Live` 时执行播出逻辑，`Idle` 时等待。

**控制 Playable 可见性**：
1. 在 Motion Design 资产关卡的蓝图中，调用 `Get Playable` 获取当前关卡关联的 Playable。
2. 使用 `Set Playable Hidden` 设置隐藏/显示。
3. 使用 `Playable Sync Event Latent` 实现跨集群的同步事件等待。

## C++ 用法

### 头文件引入

```cpp
#include "IAvaMediaModule.h"           // 播放/广播系统主模块接口
#include "AvaBroadcast.h"              // 广播通道管理
#include "AvaPlaybackGraph.h"          // 播放图
#include "AvaPlayable.h"               // Playable 抽象基类
#include "AvaPlayableGroup.h"          // Playable 分组管理
#include "AvaRundown.h"                // Rundown 节目单
#include "AvaPlaybackManager.h"        // 播放管理器
#include "AvaPlayableLibrary.h"        // 蓝图库函数
#include "AvaMediaSettings.h"          // 设置
#include "AvaMediaDefines.h"           // 枚举定义
```

### 基本用法

**启动和控制播放服务器/客户端**：

```cpp
// 来源: Public/IAvaMediaModule.h
// 获取模块接口
IAvaMediaModule& AvaModule = IAvaMediaModule::Get();

// 启动播放客户端（会停止本地服务器）
AvaModule.StartPlaybackClient();

// 启动播放服务器
AvaModule.StartPlaybackServer(TEXT("MyServer"));

// 查询状态
bool bClientRunning = AvaModule.IsPlaybackClientStarted();
bool bServerRunning = AvaModule.IsPlaybackServerStarted();

// 获取播放管理器（本地播放后端）
FAvaPlaybackManager& PlaybackManager = AvaModule.GetLocalPlaybackManager();
```

**管理广播通道**：

```cpp
// 来源: Public/Broadcast/AvaBroadcast.h
// 获取广播单例
UAvaBroadcast& Broadcast = UAvaBroadcast::Get();

// 启动/停止广播
Broadcast.StartBroadcast();
Broadcast.StopBroadcast();

// 查询通道状态
bool bIsLive = Broadcast.IsBroadcastingAnyChannel();

// 获取通道名称
FName ChannelName = Broadcast.GetChannelName(0);
```

### 进阶用法

**通过播放管理器加载和播放资产**：

```cpp
// 来源: Public/Playback/AvaPlaybackManager.h
FAvaPlaybackManager& Manager = IAvaMediaModule::Get().GetLocalPlaybackManager();

FSoftObjectPath AssetPath(TEXT("/Game/MotionDesign/MyGraphic"));
FString ChannelName = TEXT("Program");

// 加载或复用播放实例
TSharedPtr<FAvaPlaybackInstance> Instance = Manager.AcquireOrLoadPlaybackInstance(
    AssetPath, ChannelName);

// 注册监听实例状态变化
Manager.OnPlaybackInstanceStatusChanged.AddLambda(
    [](const FAvaPlaybackInstance& InInstance)
    {
        // 处理播放实例状态变化
    });
```

**通过播放图手动构建播放流程**：

```cpp
// 来源: Public/Playback/AvaPlaybackGraph.h
UAvaPlayableGroupManager* GroupManager = IAvaMediaModule::Get()
    .GetLocalPlaybackManager().GetPlayableGroupManager();

// 使用 Builder 模式构建播放图
FAvaPlaybackGraphBuilder Builder(GroupManager);

// 创建播放节点并连接到通道
UAvaPlaybackNode* PlayerNode = Builder.ConstructPlaybackNode<UAvaPlaybackNode>();
Builder.ConnectToRoot(TEXT("Program"), PlayerNode);

// 完成构建
UAvaPlaybackGraph* Graph = Builder.FinishBuilding();

// 加载和播放
Graph->LoadInstances();
Graph->Play();
```

**跨集群同步事件**：

```cpp
// 来源: Public/Playable/AvaPlayableGroup.h + AvaPlayableLibrary.h
// 在 Playable Group 上推送同步事件
PlayableGroup->PushSynchronizedEvent(
    TEXT("MySyncEvent"),
    [this]()
    {
        // 当集群所有节点都到达此事件点时执行
        DoSynchronizedAction();
    });
```

## Demo 示例

### 最小播放客户端示例

**MyMotionDesignController.h**：

```cpp
#pragma once

#include "CoreMinimal.h"
#include "IAvaMediaModule.h"
#include "AvaPlaybackManager.h"
#include "AvaMediaDefines.h"

class FMyMotionDesignController
{
public:
    void Initialize();
    void Shutdown();
    void PlayAsset(const FSoftObjectPath& InAssetPath, const FString& InChannelName);
    void StopAsset(const FSoftObjectPath& InAssetPath, const FString& InChannelName);
    bool IsAssetAvailable(const FSoftObjectPath& InAssetPath) const;
    
private:
    void OnPlaybackInstanceStatusChanged(const FAvaPlaybackInstance& InInstance);
    
    TSharedPtr<FAvaPlaybackManager> PlaybackManager;
    FDelegateHandle StatusChangedHandle;
};
```

**MyMotionDesignController.cpp**：

```cpp
#include "MyMotionDesignController.h"

void FMyMotionDesignController::Initialize()
{
    IAvaMediaModule& AvaModule = IAvaMediaModule::Get();
    
    // 启动本地播放服务器
    AvaModule.StartPlaybackServer(TEXT("DemoServer"));
    
    PlaybackManager = MakeShared<FAvaPlaybackManager>();
    
    StatusChangedHandle = PlaybackManager->OnPlaybackInstanceStatusChanged.AddRaw(
        this, &FMyMotionDesignController::OnPlaybackInstanceStatusChanged);
}

void FMyMotionDesignController::Shutdown()
{
    if (PlaybackManager.IsValid())
    {
        PlaybackManager->StopAllPlaybacks(true /* bUnload */);
        PlaybackManager->OnPlaybackInstanceStatusChanged.Remove(StatusChangedHandle);
        PlaybackManager.Reset();
    }
    
    IAvaMediaModule& AvaModule = IAvaMediaModule::Get();
    AvaModule.StopPlaybackServer();
}

void FMyMotionDesignController::PlayAsset(
    const FSoftObjectPath& InAssetPath, const FString& InChannelName)
{
    if (!PlaybackManager.IsValid())
    {
        return;
    }
    
    // 尝试复用已缓存的实例，若无则加载新的
    TSharedPtr<FAvaPlaybackInstance> Instance = 
        PlaybackManager->AcquireOrLoadPlaybackInstance(InAssetPath, InChannelName);
    
    if (Instance.IsValid())
    {
        UE_LOG(LogTemp, Log, TEXT("Started playback: %s on channel %s"),
            *InAssetPath.ToString(), *InChannelName);
    }
}

void FMyMotionDesignController::StopAsset(
    const FSoftObjectPath& InAssetPath, const FString& InChannelName)
{
    if (!PlaybackManager.IsValid())
    {
        return;
    }
    
    PlaybackManager->UnloadPlaybackInstances(InAssetPath, InChannelName);
}

bool FMyMotionDesignController::IsAssetAvailable(const FSoftObjectPath& InAssetPath) const
{
    if (!PlaybackManager.IsValid())
    {
        return false;
    }
    
    return PlaybackManager->IsLocalAssetAvailable(InAssetPath);
}

void FMyMotionDesignController::OnPlaybackInstanceStatusChanged(
    const FAvaPlaybackInstance& InInstance)
{
    UE_LOG(LogTemp, Log, TEXT("Playback instance status changed: %s"),
        *InInstance.GetSourceAssetPath().ToString());
}
```

## 模块依赖

由于插件本身包含 43 个模块，以下列出**插件级别**的独特依赖（来自 .uplugin Description 字段）：

| 模块 | 用途 |
|---|---|
| `MediaCompositing` | 媒体合成框架，广播通道底层实现 |
| `MediaIOFramework` | Media I/O 设备抽象层（输入/输出设备管理） |
| `RemoteControl` | 远程控制 Preset 系统，用于动态控制资产属性 |
| `GeometryCache` | 几何缓存，用于几何体动画 |
| `GeometryScripting` | 几何脚本工具 |
| `Text3D` | 3D 文本渲染 |
| `SVGImporter` | SVG 导入器，用于矢量图形导入 |
| `AdvancedRenamer` | 高级重命名工具 |
| `CustomDetailsView` | 自定义详情面板 |
| `DynamicMaterial` | 动态材质系统 |
| `ActorModifierCore` | Actor 修改器核心框架 |
| `ClonerEffector` | 克隆器与效果器（子插件） |
| `PropertyAnimator` | 属性动画器（子插件） |

**对于 AvalancheMedia 模块**的使用者，还需要关注：

| 模块 | 用途 |
|---|---|
| `Messaging` | UE 消息总线，Client/Server 通信基础 |
| `MediaUtils` | 媒体工具函数 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将 Motion Design 的场景设置和大纲面板从关卡编辑器移至独立分组 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 为 Rundown 页面设置添加了 Movie Render Queue 分析功能 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 在播出控制工具栏添加页面加载选项（全部/下一个/选中），并优化相关功能 |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 添加项目设置以强制禁用 Text3D 和形状的碰撞检测 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构视口客户端关联/解除关联的通知逻辑，减少重复代码 |

### 维护评价

**🟢 活跃维护中**

- **创建时间**：2025-05-09（从 Experimental 迁移到 VirtualProduction）
- **最近更新**：最近一次更新在 2026-05-20（约 1 年持续开发），更新频率稳定，几乎每周都有功能性更新
- **维护状态**：由 Epic Games 核心团队积极维护，是 UE5 Virtual Production 动态图形设计的核心工具
- **重要性**：作为 Motion Design 播出系统的基础架构，被多个上游插件依赖（ClonerEffector、PropertyAnimator、StormSync 等）
- **已知限制**：
  - EnabledByDefault=false，需要在项目设置中手动启用
  - 依赖大量上游插件（MediaIO、RemoteControl 等），配置较复杂
  - 分布式播放需要网络环境配置
- **推荐**：如果你的项目涉及虚拟制作中的动态图形设计和实时播出，强烈推荐使用。这是 Epic 官方推荐的 Motion Design 解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/virtual-production-and-broadcasting-tools-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheFunctionalTest)

---

# AvalancheMedia 模块

> Motion Design 播放与广播系统的核心运行时模块

AvalancheMedia 是 Motion Design 插件的**基础设施核心**，提供完整的播放（Playback）、广播（Broadcast）和节目单（Rundown）管理系统。它是连接 Motion Design 创作工具和实际播出输出之间的桥梁。

## 架构概览

```
┌─────────────────────────────────────────────────────────┐
│                    外部控制应用                            │
│              (HTTP / WebSocket / Web API)                │
└──────────────┬──────────────────────────────────┬───────┘
               │                                  │
┌──────────────▼──────────────┐  ┌───────────────▼───────┐
│   FAvaRundownServer         │  │  FAvaPlaybackHttpServer│
│   (Rundown 管理服务)         │  │  (HTTP API 服务)       │
└──────────────┬──────────────┘  └───────────────────────┘
               │
┌──────────────▼──────────────────────────────────────┐
│              FAvaPlaybackServer                      │
│   (播放/广播命令服务端)                                │
│   ├── FAvaPlaybackManager (播放管理)                  │
│   │   ├── UAvaPlaybackGraph (播放图)                  │
│   │   │   └── UAvaPlayable (Playable 抽象)            │
│   │   │       └── UAvaPlayableLevelStreaming         │
│   │   └── UAvaPlayableGroupManager (Playable 分组)    │
│   └── UAvaBroadcast (广播通道管理)                     │
│       └── FAvaBroadcastOutputChannel (输出通道)       │
└──────────────────────────────────────────────────────┘
               ▲ 消息总线
               │
┌──────────────┴──────────────┐
│   FAvaPlaybackClient        │
│   (播放客户端 / 编辑器端)    │
└─────────────────────────────┘
```

## 子模块文档

| 子模块 | 路径 | 说明 |
|---|---|---|
| [AvalancheMedia](./AvalancheMedia.md) | Source/AvalancheMedia | 播放、广播、Rundown 核心运行时 |

---

# AvalancheMedia

> 播放与广播系统的核心运行时模块

## 用途

AvalancheMedia 模块实现了 Motion Design 播出系统的完整后端，包括：

1. **Client/Server 通信**：通过 UE 消息总线实现编辑器（Client）和远程渲染机器（Server）之间的播放命令传输。
2. **Playback Manager**：管理播放实例的生命周期——加载、播放、停止、卸载，并实现实例池化复用。
3. **Playable 抽象**：将 Motion Design 资产（关卡、蓝图等）抽象为 Playable 对象，支持本地和远程代理两种模式。
4. **Playable Group**：将多个 Playable 分组到同一 GameInstance/World 中共享渲染上下文。
5. **Broadcast 通道**：管理广播输出通道，支持本地和远程 Media Output，实时推流到视频硬件。
6. **Rundown Server**：提供完整的节目单管理系统，支持模板、页面、组合模板、页面视图等。
7. **资产同步**：通过 Modular Feature 接口支持跨机器资产同步。
8. **HTTP API**：通过内置 HTTP 服务器暴露播放和广播控制接口。

## 核心组件

### IAvaMediaModule — 模块入口

```cpp
// 获取模块单例
IAvaMediaModule& Module = IAvaMediaModule::Get();

// 播放客户端控制
Module.StartPlaybackClient();
Module.StopPlaybackClient();

// 播放服务器控制
Module.StartPlaybackServer(TEXT("ServerName"));
Module.StopPlaybackServer();

// Rundown 服务器
Module.StartRundownServer(TEXT("RundownServer"));
Module.StopRundownServer();

// 启动独立进程的本地播放服务器
Module.LaunchGameModeLocalPlaybackServer();
```

### FAvaPlaybackManager — 播放管理器

播放管理器是本地播放的后端核心，管理播放实例的完整生命周期。

```cpp
FAvaPlaybackManager& Manager = IAvaMediaModule::Get().GetLocalPlaybackManager();

// 加载播放实例（优先复用缓存）
TSharedPtr<FAvaPlaybackInstance> Instance = 
    Manager.AcquireOrLoadPlaybackInstance(AssetPath, ChannelName);

// 查找已有实例
TSharedPtr<FAvaPlaybackInstance> Found = 
    Manager.FindPlaybackInstance(InstanceId, AssetPath, ChannelName);

// 卸载通道中某个资产的所有实例
Manager.UnloadPlaybackInstances(AssetPath, ChannelName);

// 停止所有播放（可选卸载）
TArray<FSoftObjectPath> StoppedAssets = Manager.StopAllPlaybacks(true);

// 推送动画命令
Manager.PushAnimationCommand(InstanceId, AssetPath, ChannelName,
    EAvaPlaybackAnimAction::Play, AnimSettings);

// 推送远程控制命令
Manager.PushRemoteControlCommand(InstanceId, AssetPath, ChannelName,
    RemoteControlValues, EAvaPlayableRCUpdateFlags::None);

// 查询本地资产可用性
bool bAvailable = Manager.IsLocalAssetAvailable(AssetPath);
```

### UAvaPlayable — Playable 抽象

Playable 是 Motion Design 可渲染元素的基础抽象，目前唯一具体实现是 `UAvaPlayableLevelStreaming`（基于关卡流送的 Playable）。

```cpp
// 创建 Playable（工厂方法）
UAvaPlayable::FPlayableCreationInfo Info;
Info.PlayableGroupManager = GroupManager;
Info.SourceAsset = SourceAssetPtr;
Info.ChannelName = FName("Program");
UAvaPlayable* Playable = UAvaPlayable::Create(Outer, Info);

// 加载资产
Playable->LoadAsset(SourceAsset, true /* bInitiallyVisible */);

// 开始播放
Playable->BeginPlay(WorldPlaySettings);

// 停止播放
Playable->EndPlay(EAvaPlayableEndPlayOptions::ConditionalEndPlayWorld);

// 更新远程控制值
Playable->UpdateRemoteControlCommand(RCValues, EAvaPlayableRCUpdateFlags::None);

// 设置可见性
Playable->SetShouldBeVisible(true);

// 获取 Playable 关联的 UWorld
UWorld* PlayWorld = Playable->GetPlayWorld();
```

### UAvaPlayableGroup — Playable 分组

PlayableGroup 将多个 Playable 分组到同一渲染上下文中（共享 GameInstance/World），通常对应一个广播通道。

```cpp
// 创建 PlayableGroup
UAvaPlayableGroup::FPlayableGroupCreationInfo GroupInfo;
GroupInfo.PlayableGroupManager = GroupManager;
GroupInfo.ChannelName = FName("Program");
GroupInfo.bIsSharedGroup = true;
UAvaPlayableGroup* Group = UAvaPlayableGroup::MakePlayableGroup(Outer, GroupInfo);

// 注册 Playable
Group->RegisterPlayable(Playable);

// 按来源资产查找 Playable
TArray<UAvaPlayable*> FoundPlayables;
Group->FindPlayablesBySourceAssetPath(AssetPath, FoundPlayables);

// 管理过渡
Group->RegisterPlayableTransition(Transition);
Group->TickTransitions(DeltaSeconds);

// 管理渲染目标
UTextureRenderTarget2D* RT = Group->GetRenderTarget();

// 同步事件（跨集群）
Group->PushSynchronizedEvent(TEXT("EventSignature"), [](){ /* sync action */ });
```

### UAvaBroadcast — 广播管理

```cpp
// 获取单例
UAvaBroadcast& Broadcast = UAvaBroadcast::Get();

// 启动/停止
Broadcast.StartBroadcast();
Broadcast.StopBroadcast();

// 通道管理
FName ChannelName = Broadcast.GetChannelName(0);
int32 ChannelIndex = Broadcast.GetChannelIndex(FName("Program"));
Broadcast.SetChannelType(ChannelName, EAvaBroadcastChannelType::Program);

// Profile 管理
FName ProfileName = Broadcast.CreateProfile(FName("Profile1"));
Broadcast.SetCurrentProfile(ProfileName);
Broadcast.DuplicateProfile(FName("Copy"), ProfileName);

// 监听变化
Broadcast.AddChangeListener(FOnAvaBroadcastChanged::FDelegate::CreateLambda(
    [](EAvaBroadcastChange InChange) { /* handle change */ }));
```

### FAvaPlaybackClient — 播放客户端

```cpp
// 通过模块接口获取
IAvaPlaybackClient& Client = IAvaMediaModule::Get().GetPlaybackClient();

// 发送播放请求
Client.RequestPlayback(InstanceId, AssetPath, ChannelName, 
    EAvaPlaybackAction::Play);

// 发送远程控制更新
Client.RequestRemoteControlUpdate(InstanceId, AssetPath, ChannelName,
    RCValues, EAvaPlayableRCUpdateFlags::None);

// 查询远程状态
TOptional<EAvaPlaybackStatus> Status = Client.GetRemotePlaybackStatus(
    InstanceId, AssetPath, ChannelName, ServerName);

// 获取已连接的服务器列表
TArray<FString> Servers = Client.GetServerNames();
```

### FAvaPlaybackServer — 播放服务器

```cpp
// 服务器由模块自动管理，通常不直接创建
IAvaPlaybackServer* Server = IAvaMediaModule::Get().GetPlaybackServer();

// 停止播放
Server->StopPlaybacks(ChannelName, AssetPath, true /* bUnload */);

// 查询通道信息
const IAvaBroadcastSettings* Settings = Server->GetBroadcastSettings();
const FAvaPlayableSettings* PlayableSettings = Server->GetPlayableSettings();
```

### FAvaRundownServer — Rundown 服务器

Rundown 服务器通过消息总线接收外部控制应用的命令，管理 Rundown 资产的加载、页面操作和播出控制。支持的完整 API 包括：

- Rundown 管理：创建、删除、导入、导出、保存
- 页面操作：创建、删除、修改、播放、停止
- 广播配置：Profile/Channel/Device 管理
- 通道预览：图像捕获、质量设置

## Playable Library（蓝图函数）

`UAvaPlayableLibrary` 提供从蓝图中访问当前 Playable 状态的便捷函数：

| 函数 | 说明 |
|---|---|
| `GetPlayable(Object)` | 获取当前 World 关联的 Playable |
| `GetPlayableTransition(Playable)` | 获取 Playable 参与的过渡 |
| `UpdatePlayableRemoteControlValues(Object)` | 从当前过渡注入 RC 值 |
| `IsPlayableHidden(Object)` | 查询 Playable 隐藏状态 |
| `SetPlayableHidden(Object, bHidden)` | 设置 Playable 隐藏状态 |
| `PlayableSyncEventLatent(Object, Signature)` | 跨集群同步事件（延迟） |

## Broadcast Library（蓝图函数）

`UAvaBroadcastLibrary` 提供广播通道相关查询：

| 函数 | 说明 |
|---|---|
| `GetChannelViewportSize(Object)` | 获取当前通道视口尺寸 |
| `GetChannelName(Object)` | 获取当前通道名称 |
| `GetChannelStatus(ChannelName)` | 获取通道状态 |
| `GetChannelType(ChannelName)` | 获取通道类型 |

## 设置

`UAvaMediaSettings`（显示名 "Playback & Broadcast"）提供以下配置类别：

- **Broadcast**：通道默认分辨率、像素格式、清屏颜色、溢出处理行为
- **Rundown**：预览分辨率、组合模板逻辑、控制器事件传播
- **Playback Client**：自动启动、Ping 间隔、超时设置
- **Playback Server**：自动启动、服务器名称、日志级别、本地服务器设置
- **Playback Manager**：实例缓存、实例设置、Playable 设置
- **Managed Instance Cache**：最大缓存大小
- **Web Server**：自动启动、HTTP 端口

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Messaging` | UE 消息总线，Client/Server 通信基础设施 |
| `MediaIOCore` | Media I/O 设备抽象（IMediaIOCoreDeviceProvider） |
| `MediaUtils` | 媒体工具函数 |
| `Json` / `JsonUtilities` | JSON 序列化/反序列化（Rundown 导入导出、HTTP API） |
| `HTTP` / `HTTPServer` | 内置 HTTP 服务器（Web API） |
| `StructUtils` | FInstancedStruct 支持（页面命令） |
| `ActorModifierCore` | Actor 修改器核心 |
| `RemoteControl` | 远程控制 Preset 系统 |
| `Text3D` | 3D 文本 |

无特殊依赖（仅标准 Core/Engine/Slate 等），上述为 AvalancheMedia **独特**依赖。