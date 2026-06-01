# Motion Design

> Compositing, designer and broadcasting tool.
> Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 运动设计 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（完整的广播制作系统框架） |
| 模块 | `Avalanche` (Runtime), `AvalancheMedia` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Motion Design (Avalanche Media) 是一个**用于广播制作流程的完整远程控制与分布式渲染系统**。它不仅仅是简单的合成或设计工具，而是一个专为**电视、直播、大型活动**等场景构建的复杂后端框架。

**核心解决的问题：**
1.  **远程分布式渲染与控制**：允许一个主控端（Client）远程控制和同步多台渲染主机（Server）上的“可播放内容”（Playable Assets，如关卡、UI蓝图）的加载、播放和停止。
2.  **广播频道（Broadcast Channel）管理**：将渲染输出路由到不同的物理或虚拟的媒体输出设备（如SDI卡、NDI流、显示器），实现多路独立或协同的信号输出。
3.  **节目单（Rundown）系统**：管理一系列的“页面”（Pages），每个页面对应一个预制的可播放内容和其参数，支持播放、预览、过渡转场等操作，模拟传统广电的节目单流程。
4.  **资产同步与状态管理**：在分布式环境下，跟踪和同步客户端与服务器之间的资产版本和状态，确保播放内容的一致性。

简而言之，当你需要构建一个由多个UE5实例组成、通过网络协同工作、并向外部设备输出最终画面的**广播级实时图形系统**时，Motion Design 是你的基础设施。

## 使用场景

-   **电视演播室**：在控制中心操作一套节目单（Rundown），远程控制分布在不同机房的渲染主机，分别输出主播画面、虚拟场景、数据图表等多个通道。
-   **大型现场活动（如演唱会、电竞比赛）**：需要多个大屏幕显示不同的动态视觉内容，这些内容需要同步切换和过渡。
-   **多显示器展示系统**：如主题公园、博物馆，需要一组联网的UE5主机驱动多个相邻或独立的屏幕，播放协调一致的视觉内容。
-   **云渲染/像素流广播**：通过Playback Server架构，将渲染结果推送到远程的媒体输出或流服务。

## 蓝图用法

主要蓝图功能通过 `UAvaPlayableLibrary` 和 `UAvaBroadcastLibrary` 这两个蓝图函数库提供。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetPlayable` | 获取当前关卡所关联的“Playable”对象。 | `UAvaPlayableLibrary` |
| `UpdatePlayableRemoteControlValues` | 从当前过渡（Transition）中注入远程控制值到当前Playable。 | `UAvaPlayableLibrary` |
| `SetPlayableHidden` | 设置当前Playable的所有图元是否隐藏（不渲染）。 | `UAvaPlayableLibrary` |
| `PlayableSyncEventLatent` | 推送一个同步事件到集群，等待所有节点完成后继续（潜伏节点）。 | `UAvaPlayableLibrary` |
| `GetChannelViewportSize` | 获取当前Playable所在广播通道的视口尺寸。 | `UAvaBroadcastLibrary` |
| `GetChannelName` | 获取当前Playable所在的广播通道名称。 | `UAvaBroadcastLibrary` |
| `GetChannelStatus` | 获取指定通道的广播状态（离线、空闲、直播）。 | `UAvaBroadcastLibrary` |

### 使用示例（蓝图描述）

1.  **在Playable关卡中响应远程控制**：
    *   在Playable（关卡）的蓝图中，使用 `Event BeginPlay`。
    *   连接 `GetPlayable` 节点，获取Playable对象引用。
    *   使用 `OnPlayableRemoteControlValuesApplied` 事件（需要绑定）或 `UpdatePlayableRemoteControlValues` 节点来响应从Rundown页面或远程控制面板发送过来的值。
    *   根据更新的值，修改场景中的物体、材质、动画等。

2.  **查询当前通道信息**：
    *   在任何需要知道自身渲染环境的蓝图中，调用 `GetChannelViewportSize` 以获取正确的分辨率。
    *   调用 `GetChannelName` 用于日志或条件判断（例如，仅在特定通道显示调试信息）。

## C++ 用法

### 头文件引入

```cpp
#include "IAvaMediaModule.h"
// 包含具体使用的子系统头文件，例如：
#include "Playback/IAvaPlaybackClient.h"
#include "Broadcast/AvaBroadcast.h"
```

### 基本用法

1.  **获取模块接口与检查服务状态** (来自 `IAvaMediaModule`)
```cpp
// 检查模块是否已加载
if (IAvaMediaModule::IsModuleLoaded())
{
    IAvaMediaModule& AvaMediaModule = IAvaMediaModule::Get();

    // 检查播放客户端/服务器是否已启动
    bool bClientRunning = AvaMediaModule.IsPlaybackClientStarted();
    bool bServerRunning = AvaMediaModule.IsPlaybackServerStarted();

    // 启动本地播放服务器
    if (!bServerRunning)
    {
        AvaMediaModule.StartPlaybackServer(TEXT("MyRenderNode1"));
    }
}
```

2.  **控制广播输出** (来自 `UAvaBroadcast`)
```cpp
// 获取广播单例
UAvaBroadcast* Broadcast = UAvaBroadcast::GetBroadcast();
if (Broadcast)
{
    // 启动所有通道的广播
    Broadcast->StartBroadcast();

    // 或者仅启动特定通道
    Broadcast->ConditionalStartBroadcastChannel(FName("MyProgramChannel"));

    // 查询通道状态
    EAvaBroadcastChannelState ChannelState = Broadcast->GetChannelStatus(FName("MyProgramChannel"));
}
```

### 进阶用法

通过 **Playback Client** 请求远程服务器播放资产，并监听状态变化。

```cpp
// 获取播放客户端
IAvaPlaybackClient& PlaybackClient = IAvaMediaModule::Get().GetPlaybackClient();

// 定义资产路径和通道名
FSoftObjectPath AssetPath("/Game/MotionDesign/MyScene.MyScene");
FString ChannelName = "Program";

// 生成一个唯一的实例ID用于跟踪
FGuid InstanceId = FGuid::NewGuid();

// 请求服务器播放（加载并开始）
PlaybackClient.RequestPlayback(InstanceId, AssetPath, ChannelName, EAvaPlaybackAction::Play);

// 监听状态变化 (假设有一个回调函数 OnPlaybackStatusChanged)
// 实际状态需要通过轮询 PlaybackClient.GetRemotePlaybackStatus() 或处理服务器的响应消息来获取。
TOptional<EAvaPlaybackStatus> Status = PlaybackClient.GetRemotePlaybackStatus(InstanceId, AssetPath, ChannelName, TEXT("MyRenderNode1"));
if (Status.IsSet())
{
    UE_LOG(LogTemp, Log, TEXT("Remote playback status: %s"), *UEnum::GetValueAsString(Status.GetValue()));
}
```

## Demo 示例

以下是一个最小化的C++类，演示如何启动本地播放服务器和客户端，并监听状态。

**MyMotionDesignDemo.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "IAvaMediaModule.h"

class FMyMotionDesignDemo
{
public:
    void Initialize();
    void Shutdown();

private:
    // 用于存储订阅的委托句柄
    FDelegateHandle OnServerStartedHandle;
    FDelegateHandle OnServerStoppedHandle;

    void OnPlaybackServerStarted();
    void OnPlaybackServerStopped();
};
```

**MyMotionDesignDemo.cpp**
```cpp
#include "MyMotionDesignDemo.h"
#include "IAvaMediaModule.h"

void FMyMotionDesignDemo::Initialize()
{
    if (!IAvaMediaModule::IsModuleLoaded())
    {
        UE_LOG(LogTemp, Warning, TEXT("AvalancheMedia module is not loaded."));
        return;
    }

    IAvaMediaModule& AvaMediaModule = IAvaMediaModule::Get();

    // 绑定服务器启动/停止事件
    OnServerStartedHandle = AvaMediaModule.GetOnAvaPlaybackServerStarted().AddRaw(this, &FMyMotionDesignDemo::OnPlaybackServerStarted);
    OnServerStoppedHandle = AvaMediaModule.GetAvaPlaybackServerStopped().AddRaw(this, &FMyMotionDesignDemo::OnPlaybackServerStopped);

    // 如果服务器未启动，则启动它
    if (!AvaMediaModule.IsPlaybackServerStarted())
    {
        AvaMediaModule.StartPlaybackServer(TEXT("DemoServer"));
    }

    // 如果客户端未启动，则启动它
    if (!AvaMediaModule.IsPlaybackClientStarted())
    {
        AvaMediaModule.StartPlaybackClient();
    }
}

void FMyMotionDesignDemo::Shutdown()
{
    if (IAvaMediaModule::IsModuleLoaded())
    {
        IAvaMediaModule& AvaMediaModule = IAvaMediaModule::Get();
        
        // 取消事件订阅
        if (OnServerStartedHandle.IsValid())
        {
            AvaMediaModule.GetOnAvaPlaybackServerStarted().Remove(OnServerStartedHandle);
        }
        if (OnServerStoppedHandle.IsValid())
        {
            AvaMediaModule.GetAvaPlaybackServerStopped().Remove(OnServerStoppedHandle);
        }

        // 停止服务
        AvaMediaModule.StopPlaybackClient();
        AvaMediaModule.StopPlaybackServer();
    }
}

void FMyMotionDesignDemo::OnPlaybackServerStarted()
{
    UE_LOG(LogTemp, Log, TEXT("Motion Design Playback Server Started."));
}

void FMyMotionDesignDemo::OnPlaybackServerStopped()
{
    UE_LOG(LogTemp, Log, TEXT("Motion Design Playback Server Stopped."));
}
```

## 模块依赖

该插件依赖于多个不常见的特定功能模块。

| 模块 | 用途 |
|---|---|
| `MediaIOFramework` | 提供媒体IO设备抽象（如Blackmagic, AJA卡）的基础。 |
| `RemoteControl` | 实现远程控制属性和预设的核心功能。 |
| `AvalancheMedia` | 本插件的核心模块，包含播放、广播、可播放资产等所有运行时逻辑。 |
| `MediaCompositing` | 媒体合成相关功能。 |
| `GeometryCache` | 几何体缓存，用于高效存储和播放几何体动画。 |
| `GeometryScripting` | 提供脚本化几何体操作的能力。 |

**注意**：由于该插件模块众多（`AvalancheCore`, `AvalancheEditor`, `AvalancheSequence` 等），上述仅为几个关键依赖。实际使用时，根据所需功能（如需要修改器、效果器、序列器等）可能需要依赖更多插件内部模块。通常，在启用`Avalanche`和`AvalancheMedia`插件后，其依赖关系会由插件系统自动处理。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将运动设计的编辑器选项卡（场景设置、大纲视图）移至其独立分组，优化了UI布局。 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 在使用Rundown页面设置时添加了MRQ（Movie Render Queue）的分析统计功能。 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 为节目控制工具栏添加了页面加载选项（全部、下一个、已选），增强了Rundown的控制灵活性。 |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 添加了项目设置，可强制禁用Text3D和形状的碰撞，用于优化特定场景的性能或行为。 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口改进：通过通知客户端其与播放系统的关联/解除关联状态，重构了必要的关联代码。 |

### 维护评价

-   **活跃维护**：该插件在 **2026年5月** 有密集的功能更新和优化，表明正处于**非常活跃的开发期**。
-   **创建时间**：插件于2025年5月从Experimental目录迁移至正式的VirtualProduction目录，标志着其成熟度和稳定性得到了认可。
-   **近期更新频率**：非常高，几乎每天都有提交，且内容包含UI优化、新功能（MRQ分析、页面加载选项）、项目设置和代码重构，说明团队正在持续完善和扩展其功能。
-   **结论**：这是一个**正在积极维护和快速迭代**的大型插件。对于需要构建专业广播图形系统的项目，它是一个强大且可靠的基础设施。由于其功能复杂且仍在发展中，建议在使用时密切关注其更新日志和文档变化。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
-   官方文档：（目前未在.uplugin中找到链接，建议参考UE官方文档站的Virtual Production相关章节）
-   测试用例：（源码中包含 `AvalancheFunctionalTest` 模块，用于功能测试，但具体路径需在仓库内探索）