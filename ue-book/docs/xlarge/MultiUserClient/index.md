# Multi-User Editing

> Allow collaborative multi-users sessions in the Editor

| 属性 | 值 |
|---|---|
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MultiUserClient` (Runtime), `MultiUserClientLibrary` (Runtime), `MultiUserReplicationEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-06-10 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertApp/MultiUserClient) | |

## 用途

Multi-User Editing 插件是 Unreal Engine 多人协作编辑功能的核心客户端实现。它解决了多个开发者同时在同一个关卡（Level）中进行编辑时，如何实时同步修改、避免冲突并保持编辑状态一致性的核心问题。该插件通过与 Concert 服务器通信，管理会话、同步资产和 Actor 的变更，是实现“多人同时编辑同一关卡”这一工作流的基础。

## 使用场景

- **团队协作开发**：美术、设计师和程序员可以同时连接到同一个编辑会话，实时看到彼此对关卡、蓝图或资产的修改。
- **实时同步修改**：当一位开发者移动一个 Actor 或修改材质参数时，其他会话参与者会立即看到变化，无需手动同步或合并文件。
- **解决编辑冲突**：插件内置机制处理多人同时修改同一对象时的冲突，例如通过锁定或最后修改者优先的策略。
- **大型项目集成**：适用于需要频繁进行关卡布局、灯光调试或蓝图逻辑联调的大型团队项目。

## 模块列表

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| `MultiUserClient` | Runtime | **核心客户端模块**，负责与 Concert 服务器的连接、会话管理、变更事务的发送与接收。 |
| `MultiUserClientLibrary` | Runtime | **客户端库模块**，提供供其他模块（如编辑器 UI）调用的公共 API 和接口，封装了复杂的客户端逻辑。 |
| `MultiUserReplicationEditor` | Runtime | **编辑器复制模块**，专门处理编辑器内 Actor 和资产属性的复制逻辑，是同步编辑状态的关键。 |

## 蓝图用法

本插件主要为编辑器扩展和底层 C++ 系统提供服务，其核心功能（如连接、同步）通常由编辑器 UI 或其他系统模块调用，而非直接暴露给游戏逻辑蓝图。详细 API 请参阅各子模块文档。

## C++ 用法

### 头文件引入

```cpp
// 引入客户端库以访问主要功能
#include "MultiUserClientLibrary.h"
// 引入复制编辑器模块以处理属性同步
#include "MultiUserReplicationEditor.h"
```

### 基本用法

通过 `MultiUserClientLibrary` 提供的接口来管理会话。详细 API 和用法请参阅 [MultiUserClientLibrary 模块文档](MultiUserClientLibrary.md)。

### 进阶用法

自定义资产或 Actor 的复制行为需要深入 `MultiUserReplicationEditor` 模块。详细 API 和用法请参阅 [MultiUserReplicationEditor 模块文档](MultiUserReplicationEditor.md)。

## Demo 示例

一个最小化的 C++ 示例，展示如何检查并尝试连接到一个已有的多用户会话。

```cpp
// MyMultiUserHelper.h
#pragma once
#include "CoreMinimal.h"

class FMyMultiUserHelper
{
public:
    static void TryJoinExistingSession();
};
```

```cpp
// MyMultiUserHelper.cpp
#include "MyMultiUserHelper.h"
#include "MultiUserClientLibrary.h" // 依赖 MultiUserClientLibrary 模块

void FMyMultiUserHelper::TryJoinExistingSession()
{
    // 获取多用户客户端库的实例
    IMultiUserClientModule& MultiUserClientModule = IMultiUserClientModule::Get();
    if (MultiUserClientModule.IsAvailable())
    {
        // 检查是否已有可用的会话
        TArray<FConcertSessionInfo> AvailableSessions = MultiUserClientModule.GetAvailableSessions();
        if (AvailableSessions.Num() > 0)
        {
            // 尝试加入第一个找到的会话
            FConcertSessionInfo& SessionToJoin = AvailableSessions[0];
            MultiUserClientModule.JoinSession(SessionToJoin.SessionId);
            UE_LOG(LogTemp, Log, TEXT("尝试加入会话: %s"), *SessionToJoin.SessionName);
        }
        else
        {
            UE_LOG(LogTemp, Warning, TEXT("未找到可用的多用户会话。"));
        }
    }
}
```

## 模块依赖

要使用此插件的功能，你的模块通常需要依赖 `MultiUserClientLibrary`。该模块封装了核心功能，是推荐的接入点。

| 模块 | 用途 |
|---|---|
| `Concert` | Concert 多用户协作框架的核心模块，提供会话、同步等基础协议和类型定义。 |
| `ConcertClient` | Concert 框架的客户端实现，`MultiUserClient` 模块在此基础上构建。 |
| `ConcertSyncClient` | 处理客户端与服务器间具体数据同步逻辑的模块。 |

## 维护状态

### 近期更新

（注：以下为基于插件性质和创建时间的推断，具体 commit 信息需查询仓库）
- 该插件作为 UE 编辑器核心协作功能的一部分，随引擎版本持续更新。
- 主要更新通常与引擎版本发布同步，包含功能增强、性能优化和 Bug 修复。
- 由于是实验性功能，更新可能包含 API 变动。

### 维护评价

- **创建时间**：2019年，已存在约6年，是相对成熟的功能。
- **实验性状态**：`.uplugin` 中 `IsBetaVersion=true`，表明 Epic 仍将其视为实验性功能，API 和行为可能发生变化。
- **维护活跃度**：作为引擎内置的协作编辑解决方案，它随引擎主版本积极维护，但可能不会频繁发布独立更新。
- **推荐使用**：**推荐在团队项目中使用**，以提升协作效率。但需注意其“实验性”标签，意味着在生产环境中应做好应对潜在问题或未来 API 变更的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertApp/MultiUserClient)
- [MultiUserClient 模块文档](MultiUserClient.md)
- [MultiUserClientLibrary 模块文档](MultiUserClientLibrary.md)
- [MultiUserReplicationEditor 模块文档](MultiUserReplicationEditor.md)