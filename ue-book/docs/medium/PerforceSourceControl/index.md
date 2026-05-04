# Perforce Source Control

> Perforce source control management

| 属性 | 值 |
|---|---|
| 分类 | Source Control |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `PerforceSourceControl` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2014-03-14 |
| 年龄标签 | 🏛️ 文物（约 12 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/PerforceSourceControl) | |

## 用途

这是 Unreal Engine 的 **Perforce (Helix Core) 源代码控制集成插件**，实现了 `ISourceControlProvider` 接口，将 Perforce 版本控制系统接入 UE 编辑器的 Source Control 面板。

它不是给游戏运行时使用的——它是一个 **编辑器开发工具**，让使用 Perforce 的团队能够在 UE 编辑器内直接执行 Check Out、Check In、Sync、Revert、Shelve 等版本控制操作，而无需切换到 P4V 等外部客户端。

插件底层通过 UE 内置的 Perforce C++ API（`ClientApi`）与 P4 服务器通信，支持持久化连接、自动检测 Workspace、多线程命令队列等机制。

## 使用场景

- 你的团队使用 Perforce 作为项目的版本控制系统 → 这个插件默认启用，编辑器会自动连接 P4 服务器
- 你需要在编辑器 Content Browser 中右键文件执行 Check Out / Revert / Submit → 由这个插件提供后端实现
- 你需要管理 Changelist、Shelve/Unshelve 文件、查看文件历史 → 全部通过此插件的 Worker 实现
- 你在使用 World Partition / OFPA 工作流，需要跨分支查询 HLOD 状态 → 依赖此插件的 `ChangeStatus` 操作
- 你需要通过命令行参数（`-P4Port`, `-P4User`, `-P4Client`）自动化连接 → 此插件支持命令行覆盖

## 蓝图用法

此插件 **没有暴露任何 `BlueprintCallable` 函数**。它完全通过 UE 的 Source Control 模块间接使用——编辑器 UI（Content Browser、Source Control 面板等）通过 `ISourceControlModule::Get().GetProvider()` 获取此 Provider 并调用标准接口。

## C++ 用法

这是一个内部实现模块，不提供面向游戏开发的公共 API。所有源文件都在 `Private/` 目录下（唯一一个 `Public/` 头文件是 `PerforceSourceControlChangeStatusOperation.h`，仅供需要直接调用 `p4 cstat` 的内部模块使用）。

如果你想在 C++ 中与 Perforce 交互，应通过 UE 的 `SourceControl` 模块的标准接口：

### 头文件引入

```cpp
#include "ISourceControlModule.h"
#include "ISourceControlProvider.h"
#include "SourceControlOperations.h"
```

### 基本用法

通过标准 Source Control API 执行操作（Provider 背后就是此插件）：

```cpp
// 获取当前 Provider（如果 PerforceSourceControl 已启用，返回的就是 FPerforceSourceControlProvider）
ISourceControlProvider& Provider = ISourceControlModule::Get().GetProvider();

// 查询文件状态
TArray<FString> Files;
Files.Add(TEXT("/Game/Maps/MyLevel.umap"));

TArray<FSourceControlStateRef> States;
Provider.GetState(Files, States, EStateCacheUsage::ForceUpdate);

if (States.Num() > 0 && States[0]->IsCheckedOut())
{
    UE_LOG(LogTemp, Log, TEXT("File is checked out"));
}

// Check Out 文件
FSourceControlOperationRef CheckOutOp = ISourceControlOperation::Create<FCheckOut>();
Provider.Execute(CheckOutOp, Files);

// Sync 文件到最新版本
FSourceControlOperationRef SyncOp = ISourceControlOperation::Create<FSync>();
Provider.Execute(SyncOp, Files);
```

*来源：标准 `ISourceControlProvider` 接口用法，参见 `SourceControl` 模块文档*

### 进阶用法

Perforce 专有操作 `ChangeStatus`（查询 changelist 同步状态）：

```cpp
#include "PerforceSourceControlChangeStatusOperation.h"

// 这是一个 Perforce 专有操作，包装了 p4 cstat 命令
// 返回指定路径下所有 changelist 的同步状态（Have/Need/Partial）
TSharedRef<FPerforceSourceControlChangeStatusOperation> Op =
    MakeShared<FPerforceSourceControlChangeStatusOperation>();

TArray<FString> Paths;
Paths.Add(TEXT("//depot/Project/..."));

Provider.Execute(Op, Paths);

for (const FChangelistStatusEntry& Entry : Op->OutResults)
{
    // Entry.ChangelistNumber - changelist 编号
    // Entry.Status - EChangelistStatus::Have / Need / Partial
}
```

*来源：`PerforceSourceControlChangeStatusOperation.h` (Public)*

## 架构概览

此插件采用 **Worker 模式**，每种源码控制操作对应一个 Worker 类：

### 核心类

| 类名 | 职责 |
|---|---|
| `FPerforceSourceControlProvider` | 主 Provider，实现 `ISourceControlProvider`，管理连接、状态缓存、命令队列 |
| `FPerforceConnection` | 封装 `ClientApi`（P4 C++ API），处理实际的服务器通信 |
| `FPerforceSourceControlCommand` | `IQueuedWork` 实现，支持多线程命令执行 |
| `FPerforceSourceControlState` | 文件状态（CheckedOut / ReadOnly / NotInDepot 等） |
| `FPerforceSourceControlChangelist` | Changelist 封装，支持 Default Changelist |
| `FPerforceSourceControlChangelistState` | Changelist 状态（包含文件列表、Shelved 文件） |
| `FPerforceSourceControlRevision` | 文件修订版本信息 |
| `FPerforceSourceControlLabel` | P4 Label 支持 |
| `FPerforceSourceControlSettings` | 连接设置管理（Port / User / Workspace 等） |
| `SPerforceSourceControlSettings` | Slate UI 设置面板（仅编辑器） |
| `FPerforceSourceControlModule` | 模块入口，注册 Provider 到 ModularFeatures |

### 注册的操作（Workers）

共 **30 种**操作：

| 操作名 | Worker 类 | 说明 |
|---|---|---|
| `Connect` | `FPerforceConnectWorker` | 建立连接 |
| `CheckOut` | `FPerforceCheckOutWorker` | Check Out 文件（p4 edit） |
| `CheckIn` | `FPerforceCheckInWorker` | Submit 文件（p4 submit） |
| `UpdateStatus` | `FPerforceUpdateStatusWorker` | 查询文件状态（p4 fstat） |
| `MarkForAdd` | `FPerforceMarkForAddWorker` | 标记新文件（p4 add） |
| `Delete` | `FPerforceDeleteWorker` | 标记删除（p4 delete） |
| `Revert` | `FPerforceRevertWorker` | Revert 修改（p4 revert） |
| `RevertUnchanged` | `FPerforceRevertUnchangedWorker` | Revert 未修改的文件（p4 revert -a） |
| `Sync` | `FPerforceSyncWorker` | 同步文件（p4 sync） |
| `Copy` | `FPerforceCopyWorker` | 复制/分支文件（p4 copy/branch） |
| `Resolve` | `FPerforceResolveWorker` | 解决冲突（p4 resolve） |
| `MoveToChangelist` | `FPerforceReopenWorker` | 移动文件到指定 Changelist（p4 reopen） |
| `Shelve` | `FPerforceShelveWorker` | Shelve 文件（p4 shelve） |
| `Unshelve` | `FPerforceUnshelveWorker` | Unshelve 文件（p4 unshelve） |
| `DeleteShelved` | `FPerforceDeleteShelveWorker` | 删除 Shelved 文件（p4 shelve -d） |
| `NewChangelist` | `FPerforceNewChangelistWorker` | 创建新 Changelist（p4 change） |
| `DeleteChangelist` | `FPerforceDeleteChangelistWorker` | 删除 Changelist（p4 change -d） |
| `EditChangelist` | `FPerforceEditChangelistWorker` | 编辑 Changelist 描述 |
| `UpdateChangelistsStatus` | `FPerforceGetPendingChangelistsWorker` | 更新 Pending Changelist 列表 |
| `GetChangelistDetails` | `FPerforceGetChangelistDetailsWorker` | 获取 Changelist 详情 |
| `GetWorkspaces` | `FPerforceGetWorkspacesWorker` | 获取所有 Workspace（p4 clients） |
| `GetProjectWorkspaces` | `FPerforceGetProjectWorkspacesWorker` | 获取当前项目的 Workspace |
| `CreateWorkspace` | `FPerforceCreateWorkspaceWorker` | 创建 Workspace（p4 client） |
| `DeleteWorkspace` | `FPerforceDeleteWorkspaceWorker` | 删除 Workspace |
| `DownloadFile` | `FPerforceDownloadFileWorker` | 下载文件 |
| `GetFileList` | `FPerforceGetFileListWorker` | 获取文件列表 |
| `GetFile` | `FPerforceGetFileWorker` | 获取单个文件 |
| `GetSourceControlRevisionInfo` | `FPerforceRevisionInfoWorker` | 获取修订版本信息 |
| `ChangeStatus` | `FPerforceChangeStatusWorker` | P4 专有：查询 Changelist 同步状态（p4 cstat） |
| `Where` | `FPerforceWhereWorker` | 查询文件在 Depot 中的路径（p4 where） |

### 文件状态枚举

`EPerforceState::Type` 定义了文件可能的状态：

| 枚举值 | 说明 |
|---|---|
| `DontCare` (0) | 未知/不关心 |
| `CheckedOut` (1) | 已被当前用户 Check Out |
| `ReadOnly` (2) | 受版本控制但未 Check Out |
| `NotInDepot` (4) | 新文件，未在 Depot 中 |
| `CheckedOutOther` (5) | 被其他用户 Check Out |
| `Ignore` (6) | 应被忽略的文件（MyLevel, Transient 等） |
| `OpenForAdd` (7) | 已标记添加 |
| `MarkedForDelete` (8) | 已标记删除 |
| `NotUnderClientRoot` (9) | 不在 Client Root 下 |
| `Branched` (10) | 已 Branch |

### 连接管理

- **持久连接**：Provider 维护一个 `FPerforceConnection` 持久连接，避免频繁建连开销
- **空闲断开**：连接空闲超过 1 小时（默认）自动断开，可通过 CVar `SourceControl.Perforce.IdleConnectionDisconnectSeconds` 调整
- **自动检测**：支持自动检测 Workspace、自动 Login
- **多线程安全**：同步操作使用持久连接，异步操作创建独立连接，通过 `FScopedPerforceConnection` 管理生命周期

### 设置来源

连接参数按优先级：
1. **命令行参数**：`-P4Port`, `-P4User`, `-P4Client`, `-P4Host`, `-P4Passwd`, `-P4Changelist`
2. **INI 配置**：保存在 EditorPerProjectUserSettings.ini 中
3. **P4 环境变量**：如果启用了 `UseP4Config`，从 `P4USER`, `P4PORT`, `P4CLIENT` 环境变量读取
4. **自动检测**：通过 `p4 clients` / `p4 where` 自动发现

## Demo 示例

此插件不提供独立的使用示例——它是 UE 编辑器 Source Control 框架的内部实现。以下是通过标准 API 间接使用的最小示例：

### Build.cs 依赖说明

```csharp
// 你的模块不需要直接依赖 PerforceSourceControl
// 只需依赖 SourceControl 模块即可使用标准 SCC API
PublicDependencyModuleNames.Add("SourceControl");
```

### 完整示例：查询文件 Check Out 状态

```cpp
// MySourceControlHelper.h
#pragma once
#include "CoreMinimal.h"

class FMySourceControlHelper
{
public:
    /** 查询文件是否已被 Check Out */
    static bool IsFileCheckedOut(const FString& AssetPath);

    /** 获取 P4 连接状态信息 */
    static FString GetConnectionStatusText();
};
```

```cpp
// MySourceControlHelper.cpp
#include "MySourceControlHelper.h"
#include "ISourceControlModule.h"
#include "ISourceControlProvider.h"
#include "SourceControlOperations.h"

bool FMySourceControlHelper::IsFileCheckedOut(const FString& AssetPath)
{
    ISourceControlProvider& Provider = ISourceControlModule::Get().GetProvider();

    if (!Provider.IsAvailable())
    {
        return false;
    }

    TArray<FString> Files;
    Files.Add(AssetPath);

    TArray<FSourceControlStateRef> States;
    Provider.GetState(Files, States, EStateCacheUsage::Use);

    return States.Num() > 0 && States[0]->IsCheckedOut();
}

FString FMySourceControlHelper::GetConnectionStatusText()
{
    ISourceControlProvider& Provider = ISourceControlModule::Get().GetProvider();
    return Provider.GetStatusText().ToString();
}
```

## 模块依赖

从 `PerforceSourceControl.Build.cs` 提取。此模块本身是 `PrivateDependencyModuleNames`，不对外暴露。以下是它依赖的模块：

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心库 |
| `CoreUObject` | UObject 系统 |
| `SourceControl` | 源码控制抽象层（`ISourceControlProvider` 接口定义） |
| `TypedElementFramework` | Typed Element 数据存储集成（用于 HLOD 分支查询等） |
| `InputCore` | 输入核心（条件依赖，仅当 `bUsesSlate` 时） |
| `Slate` | UI 框架（条件依赖，仅当 `bUsesSlate` 时） |
| `SlateCore` | Slate 核心（条件依赖，仅当 `bUsesSlate` 时） |
| `Perforce` (ThirdParty) | Perforce C++ API (`ClientApi`) |
| `OpenSSL` (ThirdParty) | SSL 加密（Win64/Mac，用于 P4 SSL 连接） |
| `zlib` (ThirdParty) | 压缩库（Win64/Mac） |

> **注意**：如果你只是通过 `SourceControl` 模块的标准 API 使用 Perforce，不需要直接依赖此插件。

## 维护状态

### 近期更新

1. **2025-08-15** `6678228` — World Partition HLOD: 添加 `-ReuseParentBranchHLODs` 选项
   - 新增功能：HLOD 构建时可复用父分支的 HLOD actor 文件，减少多分支构建对 patch size 的影响
   - 依赖 PerforceSourceControl 的 `ChangeStatus` 操作查询跨分支文件状态

2. **2025-07-31** `28d28e7` — 从 Pending Changelist 36726159 Unshelve
   - 内部开发流程操作，具体变更内容在 Unshelve 中

3. **2025-06-13** `af01ca2` — [Teds] 将 Elements/Common/TypedElement... 重命名为 DataStorage/...
   - 重构：对齐命名空间和类名，PerforceSourceControl 模块更新了 `TypedElementFramework` 相关引用

### 维护评价

- **活跃维护**：最近 3 个月内有实质性更新，持续适配 UE5 新功能（World Partition、TypedElement 等）
- **核心模块**：作为 UE 编辑器的默认源码控制 Provider，是 UE 开发工作流的基础设施，Epic 必然持续维护
- **成熟稳定**：创建于 2014 年，经过 12 年的迭代，代码非常成熟
- **依赖 Perforce API**：底层绑定 Perforce 官方 C++ API，兼容性有保障
- **推荐使用**：如果团队使用 Perforce，这是唯一的选择，且开箱即用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/PerforceSourceControl)
- [Source Control 模块](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Source/Developer/SourceControl) — 提供 `ISourceControlProvider` 抽象接口
- [Perforce 官方文档](https://www.perforce.com/manuals/p4api/Content/P4API/Home-p4api.html) — C++ API 参考
