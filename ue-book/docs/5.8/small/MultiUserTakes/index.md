# Multi-User Takes

> Enables opt-in multi-user synchronization for Take Recorder.

| 属性 | 值 |
|---|---|
| 中文名 | 多用户Take同步 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `ConcertTakeRecorder` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/MultiUserTakes) | |

## 用途

该插件为 **Take Recorder** 添加了多用户同步功能，解决了在虚拟制片（Virtual Production）场景下，多个 Unreal Engine 客户端（如现场多台摄像机操作员的电脑）需要协同录制表演数据（如动作捕捉、面部捕捉）时的协调问题。它允许指定哪些客户端参与录制，并同步录制的开始、停止、取消以及录制预设参数的变更，确保所有参与者在正确的时间点录制相同的内容。

## 使用场景

- 你正在使用一个 Multi-User Editing 会话进行虚拟制片拍摄，现场有多个负责不同摄像机或传感器的操作员。
- 你需要确保所有客户端的 Take Recorder 同时开始和停止录制，以生成时间轴完全同步的多个 Take。
- 你需要从主控端远程控制或查看其他客户端是否开启了录制功能。

## 蓝图用法

该插件通过 `UMultiUserTakesFunctionLibrary` 暴露了一组静态蓝图函数，用于查询和控制多用户 Take 录制设置。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetRecordOnClientLocal` | 获取本地客户端的“录制此客户端”开关状态 | `UMultiUserTakesFunctionLibrary` |
| `SetRecordOnClientLocal` | 设置本地客户端的“录制此客户端”开关 | `UMultiUserTakesFunctionLibrary` |
| `GetRecordOnClient` | 通过 EndpointId 获取指定客户端的“录制此客户端”开关状态 | `UMultiTakesFunctionLibrary` |
| `SetRecordOnClient` | 通过 EndpointId 设置指定客户端的“录制此客户端”开关 | `UMultiTakesFunctionLibrary` |
| `GetSynchronizeTakeRecorderTransactionsLocal` | 获取本地客户端的“同步 Take 录制事务”设置状态 | `UMultiUserTakesFunctionLibrary` |
| `SetSynchronizeTakeRecorderTransactionsLocal` | 设置本地客户端的“同步 Take 录制事务”设置 | `UMultiUserTakesFunctionLibrary` |

### 使用示例（蓝图描述）

在蓝图中，你可以通过 `GetRecordOnClient` 节点查询所有连接的远程客户端（使用 `UMultiUserSubsystem::GetRemoteClientIds` 获取 ID 列表）的录制状态，从而在 UI 上显示哪些客户端将参与录制。在触发录制前，可以使用 `SetRecordOnClientLocal` 动态地启用或禁用本地客户端的录制功能。

## C++ 用法

核心逻辑在 `FConcertTakeRecorderManager` 类中，它监听 Take Recorder 和 Multi-User 会话的事件并进行同步。

### 头文件引入

```cpp
#include "ConcertTakeRecorderManager.h"
```

### 基本用法

管理器实例由 `FConcertTakeRecorderModule` 持有。要与 Multi-User 会话集成，需要将会话注册给管理器。

```cpp
// 来自 Source/ConcertTakeRecorder/Private/ConcertTakeRecorderManager.h
// 假设你已经通过 FConcertTakeRecorderModule::Get().GetTakeRecorderManager() 获取了管理器指针

// 当一个客户端会话连接或创建时，注册它
TSharedRef<IConcertClientSession> MySession = /* 你的会话引用 */;
TakeRecorderManager->Register(MySession);

// 当会话断开时，取消注册
TakeRecorderManager->Unregister(MySession);
```

### 进阶用法

管理器允许查询和修改会话中各客户端的录制设置。

```cpp
// 来自 Source/ConcertTakeRecorder/Private/ConcertTakeRecorderManager.h

// 查询某个远程客户端的录制设置
const FGuid RemoteClientEndpointId = /* 远程客户端ID */;
if (const FConcertClientRecordSetting* Setting = TakeRecorderManager->FindClientRecorderSetting(RemoteClientEndpointId))
{
    bool bShouldRecordOnClient = Setting->Settings.bRecordOnClient;
    // ...
}

// 修改远程客户端的录制设置（例如，主控端控制所有客户端开始录制）
TakeRecorderManager->EditClientSettings(RemoteClientEndpointId,
    [](FTakeRecordSettings& Settings)
    {
        Settings.bRecordOnClient = true;
    });
```

## Demo 示例

一个简化的示例，展示如何在自己的模块中获取并使用多用户 Take 录制管理器。

```cpp
// MyActor.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyActor.generated.h"

UCLASS()
class AMyActor : public AActor
{
    GENERATED_BODY()

public:
    void BeginPlay() override;

    /** 尝试同步开始所有客户端的录制 */
    UFUNCTION(BlueprintCallable)
    void StartSynchronizedRecordingOnAllClients();
};

// MyActor.cpp
#include "MyActor.h"
#include "ConcertTakeRecorderManager.h"
#include "ConcertTakeRecorderModule.h"
#include "IMultiUserSubsystem.h"

void AMyActor::BeginPlay()
{
    Super::BeginPlay();
}

void AMyActor::StartSynchronizedRecordingOnAllClients()
{
    // 1. 获取多用户子系统
    UMultiUserSubsystem* MultiUserSubsystem = GEngine->GetEngineSubsystem<UMultiUserSubsystem>();
    if (!MultiUserSubsystem) return;

    // 2. 获取 Take 录制管理器
    FConcertTakeRecorderManager* Manager = FConcertTakeRecorderModule::Get().GetTakeRecorderManager();
    if (!Manager) return;

    // 3. 设置所有连接的客户端（包括自己）为“应录制”
    TArray<FGuid> RemoteClientIds = MultiUserSubsystem->GetRemoteClientIds();
    FGuid LocalClientId = MultiUserSubsystem->GetLocalClientId();
    RemoteClientIds.Add(LocalClientId);

    for (const FGuid& EndpointId : RemoteClientIds)
    {
        Manager->EditClientSettings(EndpointId,
            [](FTakeRecordSettings& Settings)
            {
                Settings.bRecordOnClient = true;
            });
    }

    // 注意：实际触发录制可能需要与 Take Recorder 模块交互，此处仅为设置示例。
}
```

## 模块依赖

该插件本身依赖以下插件（在 `.uplugin` 中定义），你的项目需要启用它们：
- `ConcertSyncClient`
- `ConcertSyncCore`
- `ConcertMain`
- `Takes`

其模块 `ConcertTakeRecorder` 的具体模块依赖未提供，但根据功能推断，它必然依赖于 `ConcertSyncClient`、`ConcertSyncCore`、`TakeRecorder` 等模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧的 `UE_LOG` 日志宏迁移到新的 `UE_LOGF`。 |
| 2025-12-01 | `5e224f1c` | When recording to a plug-in path, it is possible that the _temp package generated for the user to ge | 修复了录制到插件路径时生成的临时包可能导致的问题。 |
| 2025-10-03 | `bba2cf0f` | horde issue #1080219 - add a null check prior before checking the sequence manager for remote open s | 为远程打开序列添加了空指针检查，修复了特定问题。 |
| 2025-10-03 | `e58da06f` | Warn users about having remote open enabled when recording on multiple clients. | 在多客户端录制时，如果启用了远程打开，现在会警告用户。 |
| 2025-10-03 | `b718d858` | Fix endless looping of take recorder when in Multi-user session. It requires you to start a take rec | 修复了在多用户会话中 Take Recorder 可能陷入无限循环的严重问题。 |

### 维护评价

- **创建时间**：插件于 2020 年 9 月创建，已有约 6 年历史。
- **近期活跃度**：**非常活跃**。在 2025 年 10 月和 2026 年 4 月都有实质性更新，修复了影响稳定性的严重 bug（如无限循环）并进行了代码现代化迁移。
- **维护状态**：**活跃维护中**。作为 Virtual Production 工作流的核心组件之一，由 Epic Games 持续维护和改进。
- **限制与已知问题**：插件依赖 Multi-User Editing (Concert) 框架，其稳定性与该框架绑定。
- **推荐使用**：**强烈推荐**在需要多用户协同录制的虚拟制片项目中使用。该插件经过长期实践检验，并且仍在积极修复问题和完善功能。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/MultiUserTakes)
- 官方文档（无公开链接）
- 测试用例（未在插件目录中发现标准测试文件）