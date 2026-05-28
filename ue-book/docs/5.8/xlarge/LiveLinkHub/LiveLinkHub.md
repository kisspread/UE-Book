# Live Link Hub

> LiveLink Hub allows streaming of animated data into Unreal Engine or UEFN

| 属性 | 值 |
|---|---|
| 中文名 | 实时链接中枢 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `LiveLinkHub` (Runtime), `LiveLinkHubEditor` (Runtime), `LiveLinkHubMessaging` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-02-02 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/LiveLinkHub) | |

## 用途

LiveLink Hub 是一个**独立的 Live Link 数据中枢（Hub）应用程序**，核心功能是汇聚来自各种外部数据源（如动作捕捉设备、虚拟摄像机等）的实时动画数据，并将其**选择性地转发**给网络上的多个 Unreal Engine / UEFN 客户端实例。

与直接在编辑器内使用 LiveLink 不同，LiveLink Hub 解决了以下问题：

1. **数据集中管理**：在 Hub 端统一配置所有 Live Link 源（Source）和主题（Subject），无需在每个 UE 客户端重复配置
2. **选择性转发**：可以按客户端、按主题粒度控制哪些数据发送给哪个 UE 实例
3. **会话持久化**：将源/主题/客户端配置保存为 Session 文件，支持快速切换不同拍摄配置
4. **录制与回放**：内置录制系统，可将实时动画数据录制为 UAsset 录像文件，并支持异步流式回放
5. **拓扑模式**：支持 Hub（一对多广播）和 Spoke（点对点连接）两种工作模式
6. **时间码同步**：可作为 Timecode 和 Genlock 源，向所有连接的客户端广播时间同步设置
7. **崩溃恢复**：内置自动保存和崩溃恢复系统，在异常退出后可恢复上次的会话配置

简而言之，LiveLink Hub 是面向**现场拍摄（Virtual Production）工作流**的专用工具，在动捕棚等场景中充当数据流的中心节点。

## 使用场景

- 你在进行虚拟拍摄/动作捕捉，需要将多个动捕源的数据集中转发给多个 UE 实例 → 使用 LiveLink Hub
- 你需要在不关闭 UE 编辑器的情况下切换不同的 LiveLink 配置（如换场景时切换动捕设置） → 使用 Session 功能
- 你需要录制实时动画数据以供后期回放和调试 → 使用录制功能
- 你需要在多个 UE 客户端之间统一 Timecode 和 Genlock 设置 → 使用 Timecode 广播功能
- 你需要 Hub 模式（一对多）或 Spoke 模式（一对一）的灵活拓扑 → 使用拓扑切换

## 架构概览

LiveLink Hub 采用模块化的控制器架构：

```
FLiveLinkHub (主控)
├── FLiveLinkHubClient         ← LiveLink 客户端（接收数据源）
├── FLiveLinkHubProvider       ← LiveLink 提供者（广播到 UE 客户端）
├── ILiveLinkHubSessionManager ← 会话管理（保存/加载/切换配置）
├── FLiveLinkHubRecordingController    ← 录制控制
├── FLiveLinkHubRecordingListController ← 录像列表管理
├── FLiveLinkHubPlaybackController     ← 回放控制
├── FLiveLinkHubClientsController      ← UE 客户端管理
├── FLiveLinkHubSubjectController      ← 主题管理
├── FLiveLinkHubWindowController       ← 窗口/布局管理
├── FLiveLinkHubAutosaveHandler        ← 自动保存
└── FLiveLinkHubCrashRecovery          ← 崩溃恢复
```

## 蓝图用法

LiveLink Hub 主要是一个 C++ 应用程序框架，**不提供标准蓝图节点**。其 UI 通过 Slate 控件实现，配置通过 Settings 对象管理。

### 设置访问

可通过 Project Settings 或代码访问以下设置类：

| 设置类 | 用途 |
|---|---|
| `ULiveLinkHubSettings` | 核心设置（回放缓冲、录制模板、自动保存等） |
| `ULiveLinkHubTimeAndSyncSettings` | 时间码和帧锁设置 |
| `ULiveLinkHubUserSettings` | 用户设置（最近配置、客户端过滤器等） |

### 可编辑的 UPROPERTY 属性（ULiveLinkHubSettings）

| 属性 | 类型 | 说明 |
|---|---|---|
| `StartupConfig` | `FFilePath` | 启动时加载的配置文件路径 |
| `PlaybackFrameBufferSizeMB` | `int32` | 回放帧缓冲区大小（MB） |
| `bAllowModifyingSourceSettingsInPlayback` | `bool` | 回放期间是否允许修改源设置 |
| `bRemoveInvalidSubjectsAfterLoadingSession` | `bool` | 加载会话后是否移除无效主题 |
| `bConfirmClose` | `bool` | 关闭时是否确认 |
| `bEnableCrashRecovery` | `bool` | 是否启用崩溃恢复 |
| `bTickOnGameThread` | `bool` | 是否在游戏线程上 Tick |
| `TargetFrameRate` | `float` | 目标帧率 |
| `bEnableAutosave` | `bool` | 是否启用自动保存 |
| `MinutesBetweenAutosave` | `uint32` | 自动保存间隔（分钟） |
| `FilenameTemplate` | `FString` | 录制文件名模板（如 `{session}_{slate}_tk{take}`） |

## C++ 用法

### 头文件引入

```cpp
#include "LiveLinkHub.h"
#include "ILiveLinkHubSessionManager.h"
#include "LiveLinkHubClient.h"
#include "LiveLinkHubProvider.h"
#include "ILiveLinkHubClientsModel.h"
```

### 获取 Hub 实例

```cpp
// 获取 LiveLinkHub 单例（可能在模块关闭时返回 nullptr）
TSharedPtr<FLiveLinkHub> Hub = FLiveLinkHub::Get();
if (!Hub.IsValid())
{
    return;
}

// 获取各种控制器
TSharedPtr<ILiveLinkHubSessionManager> SessionManager = Hub->GetSessionManager();
TSharedPtr<FLiveLinkHubProvider> Provider = Hub->GetLiveLinkProvider();
TSharedPtr<FLiveLinkHubRecordingController> RecController = Hub->GetRecordingController();
TSharedPtr<FLiveLinkHubPlaybackController> PbController = Hub->GetPlaybackController();
```
*（来源：Private/LiveLinkHub.h）*

### 会话管理（Session）

```cpp
// 获取会话管理器
TSharedPtr<ILiveLinkHubSessionManager> SessionManager = FLiveLinkHub::Get()->GetSessionManager();

// 创建新会话
SessionManager->NewSession();

// 保存当前会话（会提示用户选择文件路径）
SessionManager->SaveSessionAs();

// 保存到指定路径
SessionManager->SaveCurrentSession(TEXT("/path/to/session.livelinkhub"));

// 从文件恢复会话（弹出文件选择对话框）
SessionManager->RestoreSession();

// 从指定路径恢复
SessionManager->RestoreSession(TEXT("/path/to/session.livelinkhub"));

// 从内存中的数据恢复
ULiveLinkHubSessionData* SessionData = /* ... */;
SessionManager->RestoreSession(SessionData);

// 监听会话变化
SessionManager->OnActiveSessionChanged().AddLambda(
    [](const TSharedRef<ILiveLinkHubSession>& ActiveSession)
    {
        // 处理会话切换
    }
);

// 监听客户端添加/移除
SessionManager->OnClientAddedToSession().AddLambda(
    [](FLiveLinkHubClientId ClientId)
    {
        // 客户端已加入会话
    }
);
```
*（来源：Private/Session/LiveLinkHubSessionManager.h）*

### 客户端模型（Clients Model）

```cpp
// 通过 Modular Feature 获取客户端模型
ILiveLinkHubClientsModel& ClientsModel = ILiveLinkHubClientsModel::GetChecked();

// 获取会话中的客户端列表
TArray<FLiveLinkHubClientId> SessionClients = ClientsModel.GetSessionClients();

// 获取已发现的客户端
TArray<FLiveLinkHubClientId> DiscoveredClients = ClientsModel.GetDiscoveredClients();

// 获取客户端信息
TOptional<FLiveLinkHubUEClientInfo> ClientInfo = ClientsModel.GetClientInfo(ClientId);

// 连接到已发现的客户端
ClientsModel.ConnectTo(ClientId);

// 控制客户端启用/禁用
ClientsModel.SetClientEnabled(ClientId, true);
bool bEnabled = ClientsModel.IsClientEnabled(ClientId);

// 控制特定主题的启用/禁用
ClientsModel.SetSubjectEnabled(ClientId, FName("MySubject"), false);
bool bSubjectEnabled = ClientsModel.IsSubjectEnabled(ClientId, FName("MySubject"));

// 监听客户端事件
ClientsModel.OnClientEvent().AddLambda(
    [](FLiveLinkHubClientId ClientId, ILiveLinkHubClientsModel::EClientEventType EventType)
    {
        switch (EventType)
        {
        case ILiveLinkHubClientsModel::EClientEventType::Discovered:
            // 发现新客户端
            break;
        case ILiveLinkHubClientsModel::EClientEventType::Connected:
            // 客户端已连接
            break;
        case ILiveLinkHubClientsModel::EClientEventType::Disconnected:
            // 客户端断开
            break;
        }
    }
);
```
*（来源：Public/ILiveLinkHubClientsModel.h）*

### 录制操作

```cpp
TSharedPtr<FLiveLinkHub> Hub = FLiveLinkHub::Get();
TSharedPtr<FLiveLinkHubRecordingController> RecController = Hub->GetRecordingController();

// 检查是否正在录制
bool bRecording = Hub->IsRecording();

// 录制控制器的具体操作通常通过 UI 命令触发
// 核心录制逻辑在 FLiveLinkUAssetRecorder 中实现
```
*（来源：Private/Recording/Implementations/LiveLinkUAssetRecorder.h）*

### 回放控制

```cpp
TSharedPtr<FLiveLinkHubPlaybackController> PbController = FLiveLinkHub::Get()->GetPlaybackController();

// 准备回放
ULiveLinkRecording* Recording = /* ... */;
PbController->PreparePlayback(Recording);

// 开始回放
PbController->BeginPlayback(false);  // false = 正向播放

// 暂停/继续
PbController->PausePlayback();

// 停止并弹出
PbController->Eject();

// 跳转到指定时间
PbController->GoToTime(FQualifiedFrameTime(FrameTime, FrameRate));

// 设置循环
PbController->SetLooping(true);

// 设置播放速率
PbController->SetPlayRate(0.5f);  // 半速播放

// 监听回放事件
PbController->OnPlaybackReady().AddLambda([]()
{
    // 回放就绪
});

PbController->OnPlaybackFinished().AddLambda([]()
{
    // 回放结束
});
```
*（来源：Private/Recording/LiveLinkHubPlaybackController.h）*

### 拓扑模式

```cpp
TSharedPtr<FLiveLinkHub> Hub = FLiveLinkHub::Get();

// 获取当前拓扑模式
ELiveLinkTopologyMode Mode = Hub->GetTopologyMode();  // Hub 或 Spoke

// 切换拓扑模式
Hub->SetTopologyMode(ELiveLinkTopologyMode::Hub);

// 切换模式（在 Hub 和 Spoke 之间切换）
Hub->ToggleTopologyMode();

// 监听拓扑变化
Hub->OnTopologyModeChanged().AddLambda(
    [](ELiveLinkTopologyMode NewMode)
    {
        // 处理拓扑切换
    }
);
```
*（来源：Private/LiveLinkHub.h）*

## Demo 示例

以下是一个最小示例，演示如何通过 C++ 代码操作 LiveLink Hub 的会话和客户端。

### LiveLinkHubDemo.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "LiveLinkHub.h"
#include "ILiveLinkHubSessionManager.h"
#include "ILiveLinkHubClientsModel.h"

class FLiveLinkHubDemo
{
public:
    /** 打印当前 Hub 状态信息 */
    static void PrintHubStatus()
    {
        TSharedPtr<FLiveLinkHub> Hub = FLiveLinkHub::Get();
        if (!Hub.IsValid())
        {
            UE_LOG(LogTemp, Warning, TEXT("LiveLinkHub is not available"));
            return;
        }

        // 拓扑模式
        const TCHAR* ModeStr = (Hub->GetTopologyMode() == ELiveLinkTopologyMode::Hub)
            ? TEXT("Hub") : TEXT("Spoke");
        UE_LOG(LogTemp, Log, TEXT("Topology Mode: %s"), ModeStr);

        // 录制/回放状态
        UE_LOG(LogTemp, Log, TEXT("Recording: %s, In Playback: %s"),
            Hub->IsRecording() ? TEXT("Yes") : TEXT("No"),
            Hub->IsInPlayback() ? TEXT("Yes") : TEXT("No"));
    }

    /** 连接到所有已发现的 UE 客户端 */
    static void ConnectToAllClients()
    {
        ILiveLinkHubClientsModel* ClientsModel = ILiveLinkHubClientsModel::Get();
        if (!ClientsModel)
        {
            return;
        }

        TArray<FLiveLinkHubClientId> Discovered = ClientsModel->GetDiscoveredClients();
        for (const FLiveLinkHubClientId& ClientId : Discovered)
        {
            ClientsModel->ConnectTo(ClientId);
            UE_LOG(LogTemp, Log, TEXT("Connecting to client: %s"), *ClientId.ToString());
        }
    }

    /** 列出当前会话中的所有客户端 */
    static void ListSessionClients()
    {
        ILiveLinkHubClientsModel* ClientsModel = ILiveLinkHubClientsModel::Get();
        if (!ClientsModel)
        {
            return;
        }

        TArray<FLiveLinkHubClientId> Clients = ClientsModel->GetSessionClients();
        UE_LOG(LogTemp, Log, TEXT("Session clients: %d"), Clients.Num());

        for (const FLiveLinkHubClientId& ClientId : Clients)
        {
            FText DisplayName = ClientsModel->GetClientDisplayName(ClientId);
            TOptional<FLiveLinkHubUEClientInfo> Info = ClientsModel->GetClientInfo(ClientId);
            UE_LOG(LogTemp, Log, TEXT("  Client: %s (Host: %s, Project: %s)"),
                *DisplayName.ToString(),
                Info.IsSet() ? *Info->Hostname : TEXT("Unknown"),
                Info.IsSet() ? *Info->ProjectName : TEXT("Unknown"));
        }
    }
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LiveLink` | Live Link 核心功能（源、主题、角色、数据传输） |
| `MediaProfiles` | Timecode 和 Genlock 配置管理 |

无其他特殊依赖（仅标准 Core/Engine/Slate/UMG 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `54cbb9f8` | Ensure a transient MediaProfile always exists from startup | 确保启动时始终存在临时 MediaProfile |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的警告 |
| 2026-05-13 | `1e2d2efc` | Removed delegate pattern for transient profile creation (simplified to direct NewObject in MediaProf) | 简化临时配置文件创建流程，移除委托模式 |
| 2026-05-13 | `be3a46dd` | Fix use of recording directories nested inside the content folder. | 修复嵌套在 Content 文件夹内的录制目录使用问题 |
| 2026-05-12 | `ded7015a` | LiveLinkHub - Fix not being able to connect to a client if auto-connect is disabled | 修复禁用自动连接时无法手动连接客户端的问题 |

### 维护评价

- **活跃维护**：近期（2026年5月）有密集的功能更新和 Bug 修复，主要集中在 MediaProfile 管理、录制目录和客户端连接方面
- **仍在 Beta 阶段**：`.uplugin` 标记 `IsBetaVersion=true`，API 和功能可能会有变动
- **默认未启用**：`EnabledByDefault=false`，需要手动在插件管理器中启用
- **创建时间较短**：2024 年 2 月创建，约 2 年历史，属于较新的插件
- **活跃开发中**：从 Experimental 分支独立为正式插件后持续迭代
- **已知限制**：当前为 Beta 版本，部分功能（如 `bTickOnGameThread`）标记为实验性

**推荐使用**：如果你的项目涉及虚拟拍摄/动作捕捉的多客户端工作流，此插件是官方推荐的解决方案。但需注意其 Beta 状态，建议在生产环境中谨慎使用并关注版本更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/LiveLinkHub)