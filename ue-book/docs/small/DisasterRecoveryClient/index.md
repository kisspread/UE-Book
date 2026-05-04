# Recovery Hub (DisasterRecoveryClient)

> Track changes in the Editor to allow recovery in the event of a crash

| 属性 | 值 |
|---|---|
| 分类 | Developer |
| 默认启用 | ❌ 否 (`EnabledByDefault: false`) |
| 包含内容 | 否 |
| 模块 | DisasterRecoveryClient (EditorNoCommandlet) |
| 创建时间 | 2022-03-28 |
| 年龄标签 | 🆕 (~3 年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertApp/DisasterRecoveryClient) | |

## 用途

DisasterRecoveryClient（UI 名称 "Recovery Hub"）是 UE5 编辑器的**崩溃恢复系统**。它在编辑器运行期间持续追踪用户的操作（事务、资产修改等），将变更记录到本地的 Concert 恢复会话中。当编辑器意外崩溃后重启时，系统会自动检测到未正常结束的会话，弹出 Recovery Hub 窗口，让用户选择恢复到崩溃前的某个时间点。

核心机制：该插件内部启动一个 headless Concert 客户端（角色名为 `"DisasterRecovery"`），连接到本地的 `UnrealRecoverySvc` 服务进程，通过 Concert 的事务同步框架记录所有编辑器操作。恢复时，用户可以从活动流中选择恢复全部操作或恢复到某个特定操作为止。

**注意**：该插件标记为 `IsBetaVersion: true`，且默认不启用，属于实验性功能。

## 使用场景

- 你在编辑器中花了几个小时编辑关卡/蓝图，突然编辑器崩溃了 → 重启后 Recovery Hub 自动弹出，让你恢复未保存的工作
- 你想检查之前某次编辑会话的操作历史 → 打开 Recovery Hub 面板浏览最近的会话记录
- 你需要从崩溃报告文件中导入会话数据进行分析 → 使用 Recovery Hub 的 Import 功能
- 你同时使用 Multi-User Editing → Recovery Hub 会自动检测兼容性，在 MU 会话期间暂停恢复记录（MU 事务发生在临时沙箱中，不适合灾难恢复）

## 启用方式

该插件默认不启用。启用步骤：

1. 打开 **Edit → Plugins**
2. 搜索 "Recovery Hub" 或 "Disaster Recovery"
3. 勾选启用，重启编辑器
4. 启用后，在 **Project Settings → Plugins → Disaster Recovery** 中可以配置：
   - **Is Enabled**：是否实际创建恢复会话（禁用后仍可浏览/导入历史会话）
   - **Recovery Session Dir**：恢复会话存储目录（默认在项目的 Saved 目录下）
   - **Session History Size**：保留的历史会话数量（默认 4，最大 50）
   - **Imported Session History Size**：保留的导入会话数量（默认 4，最大 50）

## 蓝图用法

该插件**没有暴露任何 BlueprintCallable 函数**。它是一个纯编辑器内部模块，所有功能通过编辑器 UI 和 C++ API 提供。

### Recovery Hub 面板

启用插件后，可以通过以下方式打开 Recovery Hub 面板：

- **Window → Developer Tools → Recovery Hub**（菜单路径）

面板功能：

| 按钮 | 说明 |
|---|---|
| 📥 Import | 从崩溃报告中导入 SessionInfo.json 文件进行检查 |
| 🗑️ Delete | 删除选中的恢复会话 |
| ⚙️ Config | 打开 Disaster Recovery 设置页面 |
| Recover All | （崩溃恢复模式）恢复选中会话的全部操作 |
| Recover Through | （崩溃恢复模式）恢复到某个特定操作为止 |
| Discard | （崩溃恢复模式）放弃恢复，使用上次保存的状态 |

## C++ 用法

### 头文件引入

```cpp
#include "IDisasterRecoveryClientModule.h"
```

### 基本用法

该插件主要通过模块接口访问。C++ 侧的公开 API 仅有 `IDisasterRecoveryClientModule`：

```cpp
// 检查模块是否可用
if (IDisasterRecoveryClientModule::IsAvailable())
{
    // 获取模块实例
    IDisasterRecoveryClientModule& RecoveryModule = IDisasterRecoveryClientModule::Get();

    // 获取底层的 Concert 同步客户端
    TSharedPtr<IConcertSyncClient> Client = RecoveryModule.GetClient();

    // 通过客户端可以访问 workspace、会话等 Concert 基础设施
    if (Client.IsValid())
    {
        TSharedPtr<IConcertClientWorkspace> Workspace = Client->GetWorkspace();
        // ... 对 workspace 进行操作
    }
}
```

> 来源：`Source/DisasterRecoveryClient/Public/IDisasterRecoveryClientModule.h`

### 设置对象

```cpp
#include "DisasterRecoverySettings.h"

// 读取恢复设置
const UDisasterRecoverClientConfig* Config = GetDefault<UDisasterRecoverClientConfig>();
bool bEnabled = Config->bIsEnabled;                          // 是否启用恢复功能
FString RecoveryDir = Config->RecoverySessionDir.Path;       // 恢复会话存储目录
int32 MaxRecent = Config->RecentSessionMaxCount;             // 最大历史会话数
int32 MaxImported = Config->ImportedSessionMaxCount;         // 最大导入会话数
```

> 来源：`Source/DisasterRecoveryClient/Private/DisasterRecoverySettings.h`

### 会话信息结构

```cpp
#include "DisasterRecoverySessionInfo.h"

// FDisasterRecoverySession 包含单个恢复会话的信息
FDisasterRecoverySession Session;
FGuid RepoId = Session.RepositoryId;          // 服务端存储库 ID
FString Name = Session.SessionName;           // 会话名称
bool bLive = Session.IsLive();                // 是否正在进行
bool bCrash = Session.WasAbnormallyTerminated(); // 是否异常终止
bool bMounted = Session.IsMounted();          // 是否被某个进程挂载
```

> 来源：`Source/DisasterRecoveryClient/Private/DisasterRecoverySessionInfo.h`

## Demo 示例

该插件是编辑器内部工具，不建议在游戏代码中直接使用。典型的扩展方式是通过模块接口获取 Concert 客户端：

```cpp
// MyEditorModule.Build.cs
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Engine",
    "DisasterRecoveryClient",  // 需要依赖此模块
});
```

```cpp
// MyEditorUtility.h
#pragma once

#include "IDisasterRecoveryClientModule.h"

class FMyEditorUtility
{
public:
    /** 检查灾难恢复系统是否正在运行 */
    static bool IsDisasterRecoveryActive()
    {
        if (!IDisasterRecoveryClientModule::IsAvailable())
        {
            return false;
        }

        TSharedPtr<IConcertSyncClient> Client = IDisasterRecoveryClientModule::Get().GetClient();
        return Client.IsValid() && Client->GetWorkspace().IsValid();
    }
};
```

## 模块依赖

### Public 依赖（你的模块需要引用）

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |

### 插件依赖

| 插件 | 用途 |
|---|---|
| `ConcertSyncClient` | Concert 同步客户端框架，提供事务记录/回放能力 |
| `ConcertSharedSlate` | Concert 共享 UI 组件（会话恢复视图等） |

### 内部依赖（Private）

该插件内部依赖大量 Concert 子系统和编辑器模块：`Concert`、`ConcertClient`、`ConcertSyncCore`、`ConcertTransport`、`UnrealEd`、`Slate`、`SlateCore`、`Json`、`Serialization`、`DesktopPlatform`、`DirectoryWatcher` 等。

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-09-12 | `ce6ff392` | 修复 `FTSTicker::RemoveTicker` 的 nodiscard 警告 | 编译修复，非功能性改动 |
| 2024-06-21 | `4b1fd009` | 在会话列表视图中显示复制活动 | 功能增强，UI 层改进 |
| 2024-01-19 | `6d5b9748` | 修复 bool 参数的容器 resize 函数改为 EAllowShrinking | 代码质量重构 |

### 维护评价

- **创建时间**：2022 年 3 月，约 3 年历史
- **最近更新**：最后一次功能性更新在 2024 年 6 月，最近一次更新是 2025 年 9 月的编译修复
- **维护状态**：**维护中** — 仍有编译适配和小幅功能更新
- **实验性**：`IsBetaVersion: true` 且 `EnabledByDefault: false`，仍处于实验阶段
- **已知限制**：
  - Recovery Service 在 4.25.1 中曾因 CrashReporter 内托管时可疑崩溃而被禁用（`IsRecoveryServiceHostedInCrashReporter()` 始终返回 `false`）
  - 与 Multi-User Editing 会话不兼容（MU 事务在临时沙箱中执行，不可用于灾难恢复）
  - 无进程外 Crash Reporter 时需要 `UnrealRecoverySvc` 可执行文件（需单独编译）
- **推荐**：如果你在生产环境中需要崩溃恢复能力，可以启用此插件，但需注意其 Beta 状态。对于重要项目，建议同时配合 UE 的 Auto-Save 功能作为备份。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertApp/DisasterRecoveryClient)
- 官方文档：无（.uplugin 中 DocsURL 为空）
- 相关插件：ConcertSyncClient（事务同步核心）、Concert（多用户编辑框架）
