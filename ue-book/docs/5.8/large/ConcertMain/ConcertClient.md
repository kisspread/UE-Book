# Concert - Main

> Allow collaborative multi-users sessions in the Editor

| 属性 | 值 |
|---|---|
| 中文名 | 多用户协作 |
| 分类 | Networking |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `Concert` (UncookedOnly), `ConcertClient` (UncookedOnly), `ConcertServer` (UncookedOnly), `ConcertTransport` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-01-10 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Concert/ConcertMain) | |

## 用途

ConcertMain 是 UE5 **Multi-User Editing（多用户编辑）** 系统的核心客户端框架。它解决了多个编辑器实例如何连接到同一会话、实时同步编辑操作的问题。

具体来说，ConcertMain 提供：

1. **会话生命周期管理** — 创建、加入、归档、恢复、复制、重命名、删除会话
2. **服务器发现** — 自动发现局域网内的 Concert 服务器
3. **自动连接** — 编辑器启动时自动连接到默认服务器和会话
4. **连接前验证** — 通过可扩展的连接任务链（`IConcertClientConnectionTask`）执行源码控制验证、脏包检查等
5. **文件共享** — 通过共享文件夹在客户端之间传输大型资产
6. **会话仓库管理** — 挂载、查询、卸载会话持久化仓库
7. **角色与权限** — 支持只读（ReadOnly）、仅发送（SendOnly）、完全读写三种连接模式

该插件**不是给普通游戏项目用的**，它是 Editor 开发者工具。从 `.uplugin` 的 `ProgramAllowList` 可以看出，`Concert`/`ConcertServer`/`ConcertTransport` 仅在 `UnrealMultiUserServer`、`LiveLinkHub` 等专用程序中加载，而 `ConcertClient` 在普通编辑器中加载（通过 `ProgramDenyList` 排除服务器程序）。

## 使用场景

- 你的团队需要多人同时编辑同一个关卡 → 连接到 Concert 会话，所有编辑操作实时同步
- 你需要灾难恢复功能 → 利用会话归档/恢复机制回放编辑历史
- 你在搭建 Live Link Hub 等专用工具 → 使用 Concert 框架实现多实例协作
- 你需要在编辑器启动时自动连接到团队服务器 → 配置 `bAutoConnect` 和 `DefaultServerURL`
- 你需要限制某些角色只能观察不能编辑 → 使用 `ReadOnlyAssignment` 或 `SendOnlyAssignment`

## 蓝图用法

ConcertMain 主要是 C++ 框架层，不直接暴露蓝图节点。所有会话管理通过 `IConcertClient` 接口在 C++ 中完成。

但可通过 `UConcertClientConfig` 的 UPROPERTY 在编辑器设置面板中配置：

### 配置项（编辑器设置）

| 配置 | 说明 | 类型 |
|---|---|---|
| `DisplayName` | 在会话中显示的用户名，支持命令行 `-CONCERTDISPLAYNAME=` | `FString` |
| `AvatarColor` | 用户头像颜色 | `FLinearColor` |
| `bAutoConnect` | 启动时自动连接，支持 `-CONCERTAUTOCONNECT` | `bool` |
| `bInstallEditorToolbarButton` | 在关卡编辑器工具栏安装多用户按钮 | `bool` |
| `DefaultServerURL` | 默认服务器地址，支持 `-CONCERTSERVER=` | `FString` |
| `DefaultSessionName` | 默认会话名，支持 `-CONCERTSESSION=` | `FString` |
| `bEnableFileSharing` | 启用文件共享服务 | `bool` |
| `ValidationMode` | 源码控制验证模式（Hard/Soft/SoftAutoProceed） | `EConcertSourceValidationMode` |
| `ReadOnlyAssignment` | 只读角色列表 | `FGameplayTagContainer` |
| `SendOnlyAssignment` | 仅发送角色列表 | `FGameplayTagContainer` |

## C++ 用法

### 头文件引入

```cpp
#include "IConcertClientModule.h"
#include "IConcertClient.h"
```

### 基本用法 — 创建客户端并连接会话

```cpp
// 获取 ConcertClient 模块
IConcertClientModule& ConcertClientModule = IConcertClientModule::Get();

// 创建一个特定角色的客户端（如 "MultiUser"）
IConcertClientPtr Client = ConcertClientModule.CreateClient(TEXT("MultiUser"));

// 配置客户端
UConcertClientConfig* Config = NewObject<UConcertClientConfig>();
Config->ClientSettings.DisplayName = TEXT("艺术家A");
Config->ClientSettings.AvatarColor = FLinearColor::Red;
Config->bAutoConnect = false;
Client->Configure(Config);

// 启动客户端
Client->Startup();

// 启动服务器发现
Client->StartDiscovery();

// 监听服务器列表更新
Client->OnKnownServersUpdated().AddLambda([Client]()
{
    TArray<FConcertServerInfo> Servers = Client->GetKnownServers();
    for (const FConcertServerInfo& Server : Servers)
    {
        UE_LOG(LogTemp, Log, TEXT("发现服务器: %s"), *Server.AdminEndpointId.ToString());
    }
});
```

（来源：`IConcertClient.h` 接口定义）

### 进阶用法 — 创建会话并管理生命周期

```cpp
// 假设已获取服务器的 AdminEndpointId
FGuid ServerAdminEndpointId = /* 从 GetKnownServers() 获取 */;

// 创建新会话
FConcertCreateSessionArgs CreateArgs;
CreateArgs.SessionName = TEXT("关卡编辑会话");
Client->CreateSession(ServerAdminEndpointId, CreateArgs).Then([](TFuture<EConcertResponseCode> Future)
{
    EConcertResponseCode Result = Future.Get();
    if (Result == EConcertResponseCode::Success)
    {
        UE_LOG(LogTemp, Log, TEXT("会话创建成功"));
    }
});

// 加入已有会话
FGuid ExistingSessionId = /* 从 GetServerSessions() 获取 */;
Client->JoinSession(ServerAdminEndpointId, ExistingSessionId);

// 监听连接状态变化
Client->OnSessionConnectionChanged().AddLambda(
    [](IConcertClientSession& Session, EConcertConnectionStatus Status)
    {
        switch (Status)
        {
        case EConcertConnectionStatus::Connected:
            UE_LOG(LogTemp, Log, TEXT("已连接到会话"));
            break;
        case EConcertConnectionStatus::Disconnected:
            UE_LOG(LogTemp, Warning, TEXT("已断开连接"));
            break;
        }
    });

// 断开会话
Client->DisconnectSession();
```

（来源：`IConcertClient.h` 中的会话管理接口）

### 高级用法 — 自定义连接前任务

```cpp
// 注册自定义连接前任务（如检查工作区状态）
Client->OnGetPreConnectionTasks().AddLambda(
    [](const IConcertClient& InClient, TArray<TUniquePtr<IConcertClientConnectionTask>>& OutTasks)
    {
        // 可添加自定义的 IConcertClientConnectionTask 实现
        // 任务按顺序执行，支持取消和进度提示
        OutTasks.Add(MakeUnique<FMyCustomValidationTask>());
    });
```

（来源：`IConcertClient.h` 中的 `FOnConcertClientSessionGetPreConnectionTasks` 委托）

### 文件共享配置

```cpp
UConcertClientConfig* Config = NewObject<UConcertClientConfig>();
Config->ClientSettings.bEnableFileSharing = true;
Config->ClientSettings.bCleanSessionFilesOnDisconnect = true;
Config->ClientSettings.CloudFileSharingPath.Path = TEXT("//shared-drive/concert-files/");
Client->Configure(Config);
```

（来源：`Public/ConcertClientSettings.h` 中的 `FConcertClientSettings`）

## Demo 示例

```cpp
// MyConcertManager.h
#pragma once

#include "CoreMinimal.h"
#include "IConcertClient.h"

class FMyConcertManager
{
public:
    void Initialize();
    void ConnectToSession(const FString& ServerURL, const FString& SessionName);
    void Disconnect();

    bool IsConnected() const;

private:
    IConcertClientPtr ConcertClient;

    void OnConnectionChanged(IConcertClientSession& Session, EConcertConnectionStatus Status);
    void OnSessionClientChanged(IConcertClientSession& Session, EConcertClientSessionClientChangeType Type, const FConcertSessionClientInfo& ClientInfo);
};
```

```cpp
// MyConcertManager.cpp
#include "MyConcertManager.h"
#include "IConcertClientModule.h"
#include "ConcertClientSettings.h"

void FMyConcertManager::Initialize()
{
    IConcertClientModule& Module = IConcertClientModule::Get();
    ConcertClient = Module.CreateClient(TEXT("MultiUser"));

    // 配置
    UConcertClientConfig* Config = NewObject<UConcertClientConfig>();
    Config->ClientSettings.DisplayName = FPlatformProcess::UserName(false);
    Config->bAutoConnect = false;
    Config->ClientSettings.DiscoveryTimeoutSeconds = 5;
    ConcertClient->Configure(Config);

    // 绑定连接状态回调
    ConcertClient->OnSessionConnectionChanged().AddRaw(
        this, &FMyConcertManager::OnConnectionChanged);

    ConcertClient->Startup();
    ConcertClient->StartDiscovery();
}

void FMyConcertManager::ConnectToSession(const FString& ServerURL, const FString& SessionName)
{
    // 发现服务器后加入会话
    TArray<FConcertServerInfo> Servers = ConcertClient->GetKnownServers();
    if (Servers.Num() > 0)
    {
        // 查找目标会话
        ConcertClient->GetServerSessions(Servers[0].AdminEndpointId).Then(
            [this, &Servers](TFuture<FConcertAdmin_GetAllSessionsResponse> Future)
        {
            auto Response = Future.Get();
            for (const auto& SessionInfo : Response.LiveSessions)
            {
                if (SessionInfo.SessionName == TEXT("MySession"))
                {
                    ConcertClient->JoinSession(Servers[0].AdminEndpointId, SessionInfo.SessionId);
                    break;
                }
            }
        });
    }
}

void FMyConcertManager::Disconnect()
{
    ConcertClient->DisconnectSession();
}

bool FMyConcertManager::IsConnected() const
{
    return ConcertClient.IsValid() &&
        ConcertClient->GetSessionConnectionStatus() == EConcertConnectionStatus::Connected;
}

void FMyConcertManager::OnConnectionChanged(IConcertClientSession& Session, EConcertConnectionStatus Status)
{
    if (Status == EConcertConnectionStatus::Connected)
    {
        UE_LOG(LogTemp, Log, TEXT("Multi-User: 已连接到会话 '%s'"), *Session.GetName());
    }
}

void FMyConcertManager::OnSessionClientChanged(
    IConcertClientSession& Session,
    EConcertClientSessionClientChangeType Type,
    const FConcertSessionClientInfo& ClientInfo)
{
    // 处理其他用户的加入/离开
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Concert` | Concert 核心共享模块（会话接口、通用实现） |
| `ConcertTransport` | Concert 网络传输层 |
| `ConcertShared` | 共享数据类型和接口定义 |
| `ConcertSyncCore` | 同步核心逻辑（事务、包同步） |

无特殊依赖（仅标准 Core/Engine/Slate 等）。具体依赖请查阅各模块的 `.Build.cs` 文件。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移到 UE_LOGF 格式 |
| 2026-04-02 | `5cc4482f` | Add descriptions to trace channels and a few other places. | 为 trace 通道添加描述信息 |
| 2026-03-10 | `a69ab07d` | [IsSavingPackage] | 修复包保存状态相关逻辑 |
| 2025-12-10 | `11a770db` | Specify FConcertSessionChallengeData::ChallengeKey should be ignored when running member initializat | 指定会话挑战密钥在成员初始化时应被忽略 |
| 2025-12-08 | `ce8c0205` | Implements a file sharing system that can be used with Multi-user. FConcertCloudSharingService will | 实现多用户云文件共享服务 |

### 维护评价

**维护状态：活跃维护中**

- 创建于 2019 年，已持续维护约 7 年，是 Epic 官方 Multi-User Editing 功能的核心基础设施
- 2025-2026 年仍有功能性更新（文件共享系统、trace 改进等），更新频率稳定
- 仍标记为 `IsBetaVersion=true`，属于实验性功能，API 可能发生变化
- `EnabledByDefault=false` + `Hidden=true`，表明这不是面向最终用户的公开功能
- 仅在特定程序（`UnrealMultiUserServer`、`LiveLinkHub` 等）中加载，普通编辑器仅加载 `ConcertClient` 模块
- **推荐使用**：如果你需要在自定义工具中实现多用户协作功能，Concert 框架是官方首选方案；如果只是在编辑器中使用多用户编辑，无需直接接触此插件，通过编辑器内置的 Multi-User Session 面板即可操作

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Concert/ConcertMain)
- [ConcertClient 接口](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Developer/Concert/ConcertMain/Source/ConcertClient/Public/IConcertClient.h)
- [ConcertClient 设置](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Developer/Concert/ConcertMain/Source/ConcertClient/Public/ConcertClientSettings.h)
- [ConcertSyncClient 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Concert/ConcertSyncClient)（上层实现，处理实际的事务/包同步）