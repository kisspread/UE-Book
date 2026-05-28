# Multi-User Editing

> Allow collaborative multi-users sessions in the Editor

| 属性 | 值 |
|---|---|
| 中文名 | 多用户协作编辑 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MultiUserClient` (Runtime), `MultiUserClientLibrary` (Runtime), `MultiUserReplicationEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-03-28 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Concert/ConcertApp/MultiUserClient) | |

## 用途

Multi-User Editing 是 Unreal Engine 的多人协作编辑系统，允许多位开发者同时连接到同一个编辑器会话中，实时同步各自对关卡、资产和 Actor 的修改。它基于 Concert（Concert 通信框架）构建，是 UE5 协作工作流的核心客户端插件。

该插件解决的核心问题：**多人同时编辑同一个项目时的冲突与同步**——当一位美术调整了灯光位置，其他参与者能立刻在自己的编辑器中看到变化，无需手动导入导出或等待提交。

该插件默认关闭（`EnabledByDefault: false`），且仍处于 Beta 阶段，需要通过编辑器偏好设置或命令行手动启用。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| [`MultiUserClient`](MultiUserClient.md) | Runtime | 核心客户端模块，管理与 Concert 服务器的连接、会话生命周期及事务同步 |
| [`MultiUserClientLibrary`](MultiUserClientLibrary.md) | Runtime | 公共库模块，暴露供其他插件/模块调用的 BlueprintCallable API 和接口定义 |
| [`MultiUserReplicationEditor`](MultiUserReplicationEditor.md) | Runtime | 编辑器内属性复制 UI 模块，提供 Actor 属性同步的编辑器界面与配置工具 |

## 使用场景

- **多人关卡设计**：一个团队的关卡设计师和灯光师同时在同一关卡中工作，彼此的修改实时可见
- **远程协作审查**：远程团队成员连接到同一 Multi-User Session，审查并实时讨论场景变更
- **蓝图协作调试**：多人同时查看和编辑蓝图，避免文件冲突
- **大型项目资产同步**：配合属性复制系统，在不同编辑器实例间同步 Actor 变换、组件属性等

## 蓝图用法

详细的蓝图 API 请参阅各子模块文档，核心接口集中在 `MultiUserClientLibrary` 模块中。

## C++ 用法

详细的 C++ 用法请参阅各子模块文档。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Concert` | 底层多用户通信框架（消息传输、会话管理） |
| `ConcertClient` | Concert 客户端实现 |
| `ConcertTransport` | Concert 网络传输层 |
| `ReplicationGraph` | Actor 属性复制图（ReplicationEditor 使用） |
| `ToolWidgets` | 编辑器工具控件 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `39d8e540` | IsObjectHierarchyReplicated lambda dereferences Object->IsA<AActor>() without a null check. | 修复属性复制中空指针解引用导致的崩溃 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏至新 API，保持代码风格统一 |
| 2025-12-10 | `c4420deb` | Multi User: Fix crash in -game | 修复以 `-game` 模式启动时的崩溃问题 |
| 2025-12-10 | `fec01c4e` | Multi User: Register Multi User with the sandbox system. | 将多用户编辑注册到沙盒系统以支持文件隔离 |
| 2025-11-26 | `025cea32` | Concert: Convert ConcertClient to use new FileSandbox API for package sandbox. | 适配新的 FileSandbox API，改善包沙盒管理 |

### 维护评价

✅ **活跃维护中**。该插件在最近 6 个月内持续有功能性更新和 Bug 修复，团队显然在积极开发中。虽然仍标记为 Beta（`IsBetaVersion: true`），但代码质量和更新频率表明 Epic 在认真推进此功能。注意：该插件默认关闭且处于 Beta 状态，生产环境使用需谨慎评估稳定性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Concert/ConcertApp/MultiUserClient)
- [Concert 插件（通信框架）](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Concert)
- [MultiUserClient 模块文档](MultiUserClient.md)
- [MultiUserClientLibrary 模块文档](MultiUserClientLibrary.md)
- [MultiUserReplicationEditor 模块文档](MultiUserReplicationEditor.md)