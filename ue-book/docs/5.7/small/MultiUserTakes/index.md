# Take Recorder Multi-User synchronization

> Enables opt-in multi-user synchronization for Take Recorder.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | true |
| 包含内容 | true |
| 模块 | ConcertTakeRecorder (UncookedOnly) |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/MultiUserTakes) | |

## 用途

MultiUserTakes 是 UE5 Multi-User Editing (Concert) 框架与 Take Recorder 之间的桥梁。它解决的核心问题是：**在虚拟制片多人协作场景下，如何让多台编辑器客户端同步执行 Take 录制操作。**

在影视虚拟制片工作流中，通常有一台 Operator（操作员）编辑器和多台 Client（客户端）编辑器同时连接到同一个 Multi-User Session。当 Operator 开始录制 Take 时，所有已标记为 "Record On Client" 的客户端都应自动开始/停止/取消录制，确保所有客户端的 Level Sequence、Take Metadata 和录制资产保持同步。

该 Plugin 通过 Concert 的自定义事件机制，在客户端之间传递录制状态变更（开始、完成、取消），同时提供 UI 扩展让 Operator 可以控制哪些客户端参与录制、是否同步事务。

## 使用场景

- **虚拟制片多机位录制**：你在操作一台主编辑器，需要多台工作站同步录制动画捕捉、摄像机追踪等 Take 数据 → 启用 MultiUserTakes 并在 Take Recorder 面板底部勾选各客户端的 "Record On Client"
- **多人协作录制**：多台编辑器连接到同一个 Multi-User Session，需要统一控制录制流程 → 使用该 Plugin 同步录制开始/停止/取消
- **蓝图自动化**：你希望通过编辑器脚本自动切换客户端录制状态 → 使用 `UMultiUserTakesFunctionLibrary` 提供的蓝图节点

## 蓝图用法

该 Plugin 提供 `UMultiUserTakesFunctionLibrary` 蓝图函数库，用于通过蓝图脚本控制多用户 Take 录制设置。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetRecordOnClientLocal` | 获取本地客户端是否勾选了 "Record On Client" | `UMultiUserTakesFunctionLibrary` |
| `SetRecordOnClientLocal` | 设置本地客户端的 "Record On Client" 勾选状态 | `UMultiUserTakesFunctionLibrary` |
| `GetRecordOnClient` | 获取指定 EndpointId 客户端的录制状态 | `UMultiUserTakesFunctionLibrary` |
| `SetRecordOnClient` | 设置指定 EndpointId 客户端的录制状态 | `UMultiUserTakesFunctionLibrary` |
| `GetSynchronizeTakeRecorderTransactionsLocal` | 获取本地的 "Synchronize Take Recorder Transactions" 状态 | `UMultiUserTakesFunctionLibrary` |
| `GetSynchronizeTakeRecorderTransactions` | 获取指定客户端的事务同步状态 | `UMultiUserTakesFunctionLibrary` |
| `SetSynchronizeTakeRecorderTransactionsLocal` | 设置本地的事务同步开关 | `UMultiUserTakesFunctionLibrary` |

### 使用示例（蓝图描述）

**自动启用所有远程客户端录制：**

1. 使用 `UMultiUserSubsystem::GetRemoteClientIds` 获取所有远程客户端 ID
2. 对每个 ID，调用 `SetRecordOnClient(ClientEndpointId, true)` 启用录制
3. 最后调用 `SetRecordOnClientLocal(true)` 启用本地录制

**查询并切换本地同步设置：**

1. 调用 `GetSynchronizeTakeRecorderTransactionsLocal` 获取当前状态
2. 根据返回值，调用 `SetSynchronizeTakeRecorderTransactionsLocal(!当前状态)` 进行切换

## C++ 用法

### 头文件引入

```cpp
#include "MultiUserTakesFunctionLibrary.h"
```

### 基本用法

通过 `UMultiUserTakesFunctionLibrary` 静态函数控制录制设置：

```cpp
// 启用本地客户端录制
UMultiUserTakesFunctionLibrary::SetRecordOnClientLocal(true);

// 查询本地录制状态
bool bLocalRecording = UMultiUserTakesFunctionLibrary::GetRecordOnClientLocal();

// 通过 EndpointId 设置远程客户端录制
FGuid RemoteEndpointId = /* 从 UMultiUserSubsystem 获取 */;
UMultiUserTakesFunctionLibrary::SetRecordOnClient(RemoteEndpointId, true);

// 启用事务同步
UMultiUserTakesFunctionLibrary::SetSynchronizeTakeRecorderTransactionsLocal(true);
```

### 进阶用法

通过模块直接访问 Manager，可用于更精细的控制：

```cpp
#include "ConcertTakeRecorderModule.h"

// 获取 Manager 实例
UE::ConcertTakeRecorder::FConcertTakeRecorderModule& Module = 
    UE::ConcertTakeRecorder::FConcertTakeRecorderModule::Get();
FConcertTakeRecorderManager* Manager = Module.GetTakeRecorderManager();

// 查询指定客户端的录制设置
if (const FConcertClientRecordSetting* Setting = Manager->FindClientRecorderSetting(EndpointId))
{
    bool bEnabled = Setting->Settings.bRecordOnClient;
    bool bSyncEnabled = Setting->bTakeSyncEnabled;
}

// 修改客户端设置并通知其他客户端
Manager->EditClientSettings(
    EndpointId,
    [](FTakeRecordSettings& Settings) { Settings.bRecordOnClient = true; },
    TOptional<TFunctionRef<bool(const FTakeRecordSettings&)>>(
        [](const FTakeRecordSettings& Settings) { return !Settings.bRecordOnClient; }
    )
);
```

### 控制台变量

| CVar | 默认值 | 说明 |
|---|---|---|
| `Concert.EnableTakeRecorderSync` | 1 | 全局启用/禁用 Take Recorder 同步 |
| `Concert.UseTakePresetPath` | 0 | 使用 Take Preset 路径进行录制同步 |
| `Concert.TakeRecorderSkipHotReloadHint` | 0 | 指示客户端可跳过 Take Recorder 生成资产的 Hot Reload |

## Demo 示例

### 最小集成示例

```cpp
// MyMultiUserTakeController.h
#pragma once
#include "CoreMinimal.h"

class FMyMultiUserTakeController
{
public:
    // 在多用户会话中自动启用所有客户端录制
    void EnableAllClientsForRecording();
};
```

```cpp
// MyMultiUserTakeController.cpp
#include "MyMultiUserTakeController.h"
#include "MultiUserTakesFunctionLibrary.h"
#include "MultiUserSubsystem.h"

void FMyMultiUserTakeController::EnableAllClientsForRecording()
{
    // 启用本地录制
    UMultiUserTakesFunctionLibrary::SetRecordOnClientLocal(true);
    
    // 启用事务同步
    UMultiUserTakesFunctionLibrary::SetSynchronizeTakeRecorderTransactionsLocal(true);
}
```

**Build.cs 依赖**（如需直接引用本模块的类）：

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
    "ConcertTakeRecorder"  // 蓝图函数库
});
```

## 模块依赖

本 Plugin 依赖以下 Plugin 和模块：

### Plugin 依赖

| Plugin | 用途 |
|---|---|
| `ConcertSyncClient` | Multi-User 客户端同步核心 |
| `ConcertSyncCore` | Multi-User 同步核心数据结构 |
| `ConcertMain` | Multi-User Editing 主功能 |
| `Takes` | Take 系统核心 |

### 模块依赖（Build.cs）

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心库 |
| `CoreUObject` | UObject 系统 |
| `Concert` | Concert 框架基础 |
| `ConcertSyncClient` | Concert 客户端同步 |
| `ConcertSyncCore` | Concert 同步核心 |
| `ConcertTransport` | Concert 传输层 |
| `TakeRecorder` | Take Recorder 录制系统 |
| `TakesCore` | Take 系统核心 |
| `LevelSequence` | Level Sequence 支持 |
| `UnrealEd` | 编辑器功能 |
| `Slate` / `SlateCore` | UI 扩展 |
| `EditorStyle` | 编辑器样式 |
| `Projects` | 项目设置 |
| `InputCore` | 输入核心 |
| `Engine` | 引擎核心 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-10-03 | `a69d185` | horde issue #1080219 - 在检查 Sequence Manager 远程打开状态前增加空指针检查 | Bug 修复：防止空指针崩溃 |
| 2025-10-03 | `302e17f` | 在多客户端录制时警告用户关于 Remote Open 启用状态 | 用户体验改进：增加警告提示避免多客户端冲突 |
| 2025-10-03 | `fc73444` | 修复 Multi-User 会话中 Take Recorder 无限循环问题 | 重要 Bug 修复：解决了当 Operator 发起录制、其他节点未在上次会话中录制时，状态跟踪变量不同步导致的无限循环 |

### 维护评价

- **创建时间**：2020 年 9 月，约 5.6 年历史
- **最近更新**：2025 年 10 月，3 次 commit 集中修复 Multi-User 录制的关键 Bug
- **维护状态**：**活跃维护** — 最近 6 个月内有实质性 Bug 修复
- **模块类型**：UncookedOnly（仅在编辑器/未打包版本中加载），符合其作为编辑器工具的定位
- **已知限制**：
  - 模块类型为 UncookedOnly，不可在运行时使用
  - 依赖 Multi-User Editing 框架，必须在 Concert Session 中才能工作
  - 多客户端同时录制时可能产生事务冲突
- **推荐程度**：✅ 推荐使用。对于虚拟制片多人协作场景，这是官方推荐的 Take 录制同步方案。近期活跃的 Bug 修复表明 Epic 仍在维护该功能。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/MultiUserTakes)
- [官方文档]()（无单独文档页面）
- [Multi-User Editing 文档](https://docs.unrealengine.com/5.7/en-US/multi-user-editing-in-unreal-engine/)
- [Take Recorder 文档](https://docs.unrealengine.com/5.7/en-US/take-recorder-in-unreal-engine/)
