# Disaster Recovery Client

> Track changes in the Editor to allow recovery in the event of a crash

| 属性 | 值 |
|---|---|
| 中文名 | 灾难恢复客户端 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DisasterRecoveryClient` (EditorNoCommandlet) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-03-28 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Concert/ConcertApp/DisasterRecoveryClient) | |

## 用途

这是一个基于 Unreal Insights / Concert 同步框架的**编辑器崩溃恢复系统**。它在后台持续记录编辑器操作事务（transactions），当编辑器崩溃后重新启动时，自动检测到之前未正常关闭的会话，并提供一个 Recovery Hub 界面让用户选择恢复到崩溃前的某个状态。

核心工作流程：
1. **持续记录**：编辑器运行时，创建一个灾备会话并通过 Concert 同步客户端将所有操作事务记录到本地仓库
2. **崩溃检测**：编辑器启动时检查是否有未正常终止的会话（通过进程 ID 判断）
3. **恢复选择**：如果发现可恢复的会话，展示 Recovery Hub UI，用户可以选择恢复全部事务或恢复到特定时间点
4. **会话轮转**：维护最近会话和导入会话的历史列表，自动清理过期会话

## 使用场景

- 你在使用 UE5 编辑器进行大量资产修改，担心编辑器突然崩溃丢失工作 → 启用此插件自动记录所有操作
- 编辑器崩溃后需要恢复到崩溃前的状态 → 重启编辑器后通过 Recovery Hub 选择恢复点
- 需要检查之前崩溃的会话记录 → 从崩溃报告目录导入会话进行检查
- 多个编辑器实例同时运行时，确保只有第一个崩溃的实例能触发恢复流程

## 蓝图用法

此插件主要作为底层服务运行，不暴露蓝图节点给用户直接调用。所有功能通过编辑器 UI（Recovery Hub 面板）和 C++ API 访问。

### 配置设置

设置项位于 **Project Settings → Plugins → Disaster Recovery**：

| 设置项 | 说明 | 默认值 |
|---|---|---|
| `bIsEnabled` | 是否启用 Recovery Hub | `true` |
| `RecoverySessionDir` | 恢复会话存储目录 | 项目 Saved 目录 |
| `RecentSessionMaxCount` | 最近会话历史大小（0-50） | `4` |
| `ImportedSessionMaxCount` | 导入会话历史大小（0-50） | `4` |

## C++ 用法

### 头文件引入

```cpp
#include "IDisasterRecoveryClientModule.h"
```

### 基本用法

获取模块实例并检查可用性（来源：`IDisasterRecoveryClientModule.h`）：

```cpp
// 检查模块是否已加载
if (IDisasterRecoveryClientModule::IsAvailable())
{
    // 获取模块接口
    IDisasterRecoveryClientModule& RecoveryModule = IDisasterRecoveryClientModule::Get();
    
    // 获取底层的 Concert 同步客户端
    TSharedPtr<IConcertSyncClient> SyncClient = RecoveryModule.GetClient();
    if (SyncClient.IsValid())
    {
        // 可以通过 SyncClient 进一步操作
    }
}
```

### 会话管理器用法

创建会话管理器并执行恢复操作（来源：`DisasterRecoverySessionManager.h`）：

```cpp
#include "DisasterRecoverySessionManager.h"

// 构造会话管理器（需要已配置并启动的 SyncClient）
FDisasterRecoverySessionManager SessionManager(
    TEXT("DisasterRecovery"),  // 角色标识
    SyncClient                  // Concert 同步客户端
);

// 检查是否有可恢复的候选项
TFuture<bool> FutureResult = SessionManager.HasRecoverableCandidates();
FutureResult.Next([](bool bHasCandidates)
{
    if (bHasCandidates)
    {
        // 显示 Recovery Hub UI
    }
});

// 获取当前所有会话列表
const TArray<TSharedRef<FDisasterRecoverySession>>& Sessions = SessionManager.GetSessions();
for (const TSharedRef<FDisasterRecoverySession>& Session : Sessions)
{
    UE_LOG(LogDisasterRecovery, Log, TEXT("Session: %s, Live: %d, Mounted: %d"),
        *Session->SessionName, Session->IsLive(), Session->IsMounted());
}
```

### 进阶用法

监听会话变更并执行恢复（来源：`DisasterRecoverySessionManager.h`）：

```cpp
// 监听会话添加事件
SessionManager.OnSessionAdded().AddLambda(
    [](TSharedRef<FDisasterRecoverySession> NewSession)
    {
        UE_LOG(LogDisasterRecovery, Log, TEXT("New session added: %s"), 
            *NewSession->SessionName);
    });

// 监听会话移除事件
SessionManager.OnSessionRemoved().AddLambda(
    [](const FGuid& RepositoryId)
    {
        UE_LOG(LogDisasterRecovery, Log, TEXT("Session removed: %s"), 
            *RepositoryId.ToString());
    });

// 从崩溃报告导入会话进行检查
FString SessionInfoPath = TEXT("/path/to/SessionInfo.json");
auto ImportResult = SessionManager.ImportSession(SessionInfoPath);
if (ImportResult.IsType<TSharedPtr<FDisasterRecoverySession>>())
{
    TSharedPtr<FDisasterRecoverySession> ImportedSession = ImportResult.Get<TSharedPtr<FDisasterRecoverySession>>();
    // 会话已导入，可以加载并查看
    
    // 加载会话活动流
    TFuture<TVariant<TSharedPtr<FConcertActivityStream>, FText>> LoadResult = 
        SessionManager.LoadSession(ImportedSession.ToSharedRef());
    LoadResult.Next([](TVariant<TSharedPtr<FConcertActivityStream>, FText> Result)
    {
        if (Result.IsType<TSharedPtr<FConcertActivityStream>>())
        {
            // 成功加载，可以检查活动记录
        }
    });
}

// 从归档会话恢复（恢复到特定时间点）
TFuture<TPair<bool, FText>> RestoreResult = 
    SessionManager.RestoreAndJoinSession(ArchivedSession, ThroughActivity);
RestoreResult.Next([](TPair<bool, FText> Result)
{
    if (Result.Key)
    {
        // 恢复成功
    }
    else
    {
        // 恢复失败，查看错误信息
        UE_LOG(LogDisasterRecovery, Error, TEXT("Restore failed: %s"), *Result.Value.ToString());
    }
});

// 离开当前会话
SessionManager.LeaveSession();

// 刷新会话信息（检测并发实例的状态变化）
SessionManager.Refresh();
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ConcertSyncCore` | Concert 同步核心框架，提供事务同步基础 |
| `ConcertSyncClient` | Concert 同步客户端，用于连接恢复服务器 |
| `Concert` | Concert 核心 API |

插件级依赖（`.uplugin` Plugins 字段）：

| 插件 | 用途 |
|---|---|
| `ConcertSyncClient` | Concert 同步客户端插件 |
| `ConcertSharedSlate` | Concert 共享 Slate UI 组件 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移到 UE_LOGF 宏 |
| 2025-09-12 | `fd5c41be` | Addressing instances "ignoring return value of function declared with 'nodiscard' attribute" issue f | 修复忽略 [[nodiscard]] 标记函数返回值的问题 |
| 2024-06-21 | `4b1fd009` | Display replication activities in session list view | 在会话列表视图中显示复制活动 |
| 2024-01-20 | `6d5b9748` | Fixed up a lot of bool-taking container resize functions to take EAllowShrinking instead. | 将容器 resize 函数的 bool 参数改为 EAllowShrinking 枚举 |

### 维护评价

**维护状态：活跃维护中** ✅

- 创建于 2022 年 3 月，作为 Concert 同步框架的一部分从 Multi-User 编辑功能中独立出来
- **仍在实验性阶段**（IsBetaVersion=true），默认未启用（EnabledByDefault=false）
- 最近的更新主要是编译器警告修复和宏迁移，属于维护性更新
- 最近的功能更新是 2024-06-21 添加了复制活动显示
- 该插件与 Concert 同步框架紧密集成，依赖于同一维护团队
- **推荐使用**：如果你需要在编辑器崩溃后恢复工作，这是一个有用的功能，但由于仍处于 Beta 状态，建议在非关键项目中使用并关注其稳定性

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Concert/ConcertApp/DisasterRecoveryClient)
- 官方文档（暂无）