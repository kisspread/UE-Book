# Plastic SCM

> Unity Version Control (formerly Plastic SCM)

| 属性 | 值 |
|---|---|
| 分类 | Source Control |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `PlasticSourceControl` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2019-10-01 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/PlasticSourceControl) | |

## 用途

PlasticSourceControl 是 Unreal Engine 内置的版本控制集成插件，将 **Unity Version Control**（原 Plastic SCM）的命令行工具 `cm` 深度嵌入编辑器工作流。它实现了 UE 的 `ISourceControlProvider` 接口，使得用户无需离开编辑器即可完成文件签出/签入、分支管理、变更列表（changelist）管理、文件锁定、changeset 浏览等全部版本控制操作。

该插件的核心设计思路是：

1. **后台 Shell 进程**：启动时启动 `cm shell` 后台进程（`PlasticSourceControlShell`），通过管道通信避免反复启动进程的开销
2. **Worker 模式**：每个 VCS 操作（签出、签入、同步等）都有对应的 Worker 类，支持同步/异步执行
3. **状态缓存**：通过 `StateCache` 缓存文件状态，避免重复查询
4. **Slate UI 集成**：提供 Branches、Changesets、Locks 三个可停靠窗口，以及工具栏状态栏 widget

**使用 Unity Version Control（而非 Perforce/Git）做版本控制的 UE5 项目会自动加载此插件。**

## 使用场景

- 你在使用 Unity Version Control（原 Plastic SCM）管理 UE5 项目 → 此插件自动生效，在编辑器中直接操作版本控制
- 你需要对大文件（如 `.uasset`）进行独占锁定（exclusive checkout），防止二进制冲突 → 使用 Locks 功能
- 你需要在编辑器内管理分支、查看 changeset 历史 → 使用 Branches/Changesets 窗口
- 你在使用 Gluon（部分工作区）模式 → 插件支持 partial workspace
- 你需要使用 changelist 组织待提交的变更 → 插件完整支持 changelist（含 shelving）

## 架构概览

```
FPlasticSourceControlModule (IModuleInterface)
├── FPlasticSourceControlProvider (ISourceControlProvider)
│   ├── WorkersMap          — 注册所有操作的 Worker 工厂
│   ├── StateCache          — 文件状态缓存
│   ├── ChangelistsStateCache — Changelist 状态缓存
│   ├── CommandQueue        — 主线程命令队列
│   └── FPlasticSourceControlConsole — 控制台命令
├── FPlasticSourceControlBranchesWindow   — 分支浏览窗口
├── FPlasticSourceControlChangesetsWindow — Changeset 浏览窗口
├── FPlasticSourceControlLocksWindow      — 锁管理窗口
└── FPlasticSourceControlWorkspaceCreation — 工作区创建逻辑
```

### 命令执行流程

```
编辑器 UI → ISourceControlProvider::Execute()
  → FPlasticSourceControlProvider::CreateWorker()  — 根据操作名创建 Worker
  → FPlasticSourceControlCommand::DoWork()          — 在线程池执行
    → IPlasticSourceControlWorker::Execute()
      → PlasticSourceControlUtils::RunCommand()
        → PlasticSourceControlShell::RunCommand()   — 通过 cm shell 管道
  → Worker::UpdateStates()                          — 回到主线程更新缓存
  → FPlasticSourceControlProvider::Tick()           — 通知 UI 刷新
```

## 支持的操作

### 标准 VCS 操作（继承自引擎）

| 操作 | Worker 类 | 说明 |
|---|---|---|
| Connect | `FPlasticConnectWorker` | 初始化连接，查找工作区根目录 |
| CheckOut | `FPlasticCheckOutWorker` | 签出文件（`cm checkout`） |
| CheckIn | `FPlasticCheckInWorker` | 签入文件（`cm checkin`） |
| MarkForAdd | `FPlasticMarkForAddWorker` | 添加新文件到版本控制 |
| Delete | `FPlasticDeleteWorker` | 删除文件并从版本控制移除 |
| Revert | `FPlasticRevertWorker` | 还原文件到 depot 状态 |
| UpdateStatus | `FPlasticUpdateStatusWorker` | 查询文件状态（`cm status`） |
| Sync | `FPlasticSyncWorker` | 同步工作区到最新（`cm update`） |
| Copy | `FPlasticCopyWorker` | 复制/移动文件 |
| Resolve | `FPlasticResolveWorker` | 标记冲突已解决 |
| GetPendingChangelists | `FPlasticGetPendingChangelistsWorker` | 获取 changelist 列表 |
| NewChangelist | `FPlasticNewChangelistWorker` | 创建新 changelist |
| DeleteChangelist | `FPlasticDeleteChangelistWorker` | 删除 changelist |
| EditChangelist | `FPlasticEditChangelistWorker` | 编辑 changelist 描述 |
| Reopen | `FPlasticReopenWorker` | 将文件移动到另一个 changelist |
| Shelve | `FPlasticShelveWorker` | 搁置 changelist 中的变更 |
| Unshelve | `FPlasticUnshelveWorker` | 取消搁置 |
| DeleteShelve | `FPlasticDeleteShelveWorker` | 删除搁置 |
| GetChangelistDetails | `FPlasticGetChangelistDetailsWorker` | 获取 changelist 详情 |
| GetFile | `FPlasticGetFileWorker` | 获取文件指定修订版 |
| GetHistory | `FPlasticGetHistoryWorker` | 获取文件历史 |

### Plastic 自定义操作

| 操作 | 类 | 说明 |
|---|---|---|
| RevertUnchanged | `FPlasticRevertUnchanged` | 仅还原未修改的签出文件（`cm unco --keepchanges`） |
| SyncAll | `FPlasticSyncAll` | 同步整个工作区，返回更新文件列表 |
| RevertAll | `FPlasticRevertAll` | 还原所有签出文件 |
| RevertToRevision | `FPlasticRevertToRevision` | 还原到指定 changeset |
| MakeWorkspace | `FPlasticMakeWorkspace` | 创建新工作区和仓库 |
| SwitchToPartialWorkspace | `FPlasticSwitchToPartialWorkspace` | 切换到 Gluon 部分工作区 |
| GetLocks | `FPlasticGetLocks` | 列出文件锁 |
| Unlock | `FPlasticUnlock` | 释放/移除文件锁 |
| GetBranches | `FPlasticGetBranches` | 列出分支 |
| Switch | `FPlasticSwitch` | 切换到分支/changeset |
| MergeBranch | `FPlasticMergeBranch` | 合并分支到当前分支 |
| CreateBranch | `FPlasticCreateBranch` | 创建分支 |
| RenameBranch | `FPlasticRenameBranch` | 重命名分支 |
| DeleteBranches | `FPlasticDeleteBranches` | 删除分支 |
| GetChangesets | `FPlasticGetChangesets` | 列出 changeset |
| GetChangesetFiles | `FPlasticGetChangesetFiles` | 列出 changeset 中的文件 |

## 文件状态模型

插件通过 `EWorkspaceState` 枚举跟踪文件状态：

| 状态 | 说明 | Content Browser 图标 |
|---|---|---|
| `Unknown` | 未知状态 | — |
| `Ignored` | 忽略的文件 | — |
| `Controlled` | 已版本控制，未修改 | ✅ 绿色 |
| `CheckedOutChanged` | 已签出且有修改 | 🔵 蓝色 |
| `CheckedOutUnchanged` | 已签出但无修改 | 🔵 蓝色 |
| `Added` | 新添加到版本控制 | ➕ |
| `Moved` | 已重命名/移动 | ↗️ |
| `Copied` | 已复制 | 📋 |
| `Replaced` | 已替换/合并 | 🔄 |
| `Deleted` | 已删除 | ❌ |
| `LocallyDeleted` | 本地文件缺失 | ⚠️ |
| `Changed` | 本地修改但未签出 | 🟡 |
| `Conflicted` | 有冲突 | 🔴 |
| `Private` | 未纳入版本控制 | ➖ |

`FPlasticSourceControlState` 还跟踪以下额外信息：
- `LockedBy` / `LockedWhere` / `LockedBranch` — 文件锁定信息
- `RetainedBy` — 在其他分支上的保留信息
- `MovedFrom` — 移动/重命名的原始路径
- `Changelist` — 所属的 changelist
- `DepotRevisionChangeset` / `LocalRevisionChangeset` — 版本号信息

## 工作区类型

| 类型 | 说明 | ChangesetNumber |
|---|---|---|
| 完整工作区 | 标准模式，同步到特定 changeset | 正数 |
| 部分工作区 (Gluon) | 只下载选择的文件 | -1 |

`FPlasticSourceControlProvider::IsPartialWorkspace()` 通过 `ChangesetNumber == -1` 判断。

## 编辑器 UI 集成

### 工具栏状态栏

`SPlasticSourceControlStatusBar` 在编辑器底部工具栏显示当前分支名，点击可打开 Branches 窗口。

### 右键菜单扩展

在 Content Browser 的资产右键菜单中添加了 Lock 管理选项（释放锁、移除锁）。

### 可停靠窗口

| 窗口 | 类 | 功能 |
|---|---|---|
| View Branches | `SPlasticSourceControlBranchesWidget` | 浏览、创建、重命名、删除、切换、合并分支 |
| View Changesets | `SPlasticSourceControlChangesetsWidget` | 浏览 changeset 列表、查看文件差异、切换到 changeset |
| View Locks | `SPlasticSourceControlLocksWidget` | 浏览文件锁、释放/移除锁 |

### 控制台命令

`FPlasticSourceControlConsole` 注册了 `cm` 控制台命令，允许在编辑器 Output Log 中直接运行 `cm` CLI 命令：

```
cm status
cm find branches
```

### 菜单操作

`FPlasticSourceControlMenu` 扩展了 Source Control 工具栏菜单：

| 菜单项 | 功能 |
|---|---|
| Sync Project | 同步整个项目到最新 |
| Revert Unchanged | 还原未修改的签出文件 |
| Revert All | 还原所有签出文件 |
| Switch to Partial Workspace | 切换到 Gluon 模式 |
| View Branches / Changesets / Locks | 打开对应窗口 |
| Open Desktop Application | 打开 Plastic SCM 桌面客户端 |
| Visit Docs / Support URL | 打开文档/支持页面 |

## 项目设置

通过 **Edit → Project Settings → Plugins → Source Control - Unity Version Control** 配置：

### 基础设置

| 设置 | 默认值 | 说明 |
|---|---|---|
| Binary Path | `cm` | `cm` 可执行文件路径 |
| Update Status At Startup | `false` | 启动时异步更新状态（大项目可能很慢） |
| Update Status Other Branches | `false` | 状态更新时检查其他分支的最近 changeset |
| View Local Changes | `true` | View Changes 窗口显示本地修改和未跟踪文件 |
| Enable Verbose Logs | `false` | 启用详细日志 |

### 用户名映射（`UPlasticSourceControlProjectSettings`）

| 设置 | 默认值 | 说明 |
|---|---|---|
| UserNameToDisplayName | `{}` | 将 VCS 用户名映射为短显示名 |
| HideEmailDomainInUsername | `true` | 隐藏邮箱域名后缀 |
| PromptForCheckoutOnChange | `true` | 文件修改时提示签出 |
| LimitNumberOfRevisionsInHistory | `50` | 历史窗口最大修订数 |

### 窗口列显示

可以控制 Branches、Changesets、Locks 三个窗口中各列的可见性，例如：

- `bShowBranchRepositoryColumn` — 显示分支所在仓库
- `bShowBranchCreatedByColumn` — 显示分支创建者
- `bShowLockDestinationBranchColumn` — 显示锁的目标分支
- `bShowChangesetBranchColumn` — 显示 changeset 所在分支

## C++ 用法

### 头文件引入

此插件的所有头文件都在 `Private` 目录下，**没有公共 API**。插件通过 UE 的 `ISourceControlProvider` 接口与引擎交互，不暴露自定义类型给外部模块。

如果需要以编程方式与版本控制交互，应使用引擎的通用 SourceControl API：

```cpp
#include "ISourceControlModule.h"
#include "ISourceControlProvider.h"
#include "SourceControlOperations.h"
```

### 基本用法（通用 SourceControl API）

```cpp
// 获取当前 source control provider
ISourceControlProvider& Provider = ISourceControlModule::Get().GetProvider();

// 查询文件状态
TArray<FString> Files;
Files.Add(TEXT("/Game/MyAsset.uasset"));

TArray<FSourceControlStateRef> States;
Provider.GetState(Files, States, EStateCacheUsage::ForceUpdate);

for (const FSourceControlStateRef& State : States)
{
    if (State->IsCheckedOut())
    {
        UE_LOG(LogTemp, Log, TEXT("File is checked out: %s"), *State->GetFilename());
    }
}

// 签出文件
FSourceControlOperationRef CheckOutOp = ISourceControlOperation::Create<FCheckOut>();
Provider.Execute(CheckOutOp, Files);

// 签入文件
FSourceControlOperationRef CheckInOp = ISourceControlOperation::Create<FCheckIn>();
CheckInOp->SetDescription(FText::FromString(TEXT("My check-in message")));
Provider.Execute(CheckInOp, Files);
```

### 获取 Plastic Provider 实例

```cpp
#include "PlasticSourceControlModule.h"

if (FPlasticSourceControlModule::IsLoaded())
{
    FPlasticSourceControlProvider& PlasticProvider = FPlasticSourceControlModule::Get().GetProvider();
    
    // 获取当前分支名
    FString BranchName = PlasticProvider.GetBranchName();
    
    // 获取工作区信息
    FString WorkspaceName = PlasticProvider.GetWorkspaceName();
    FString RepositoryName = PlasticProvider.GetRepositoryName();
    FString ServerUrl = PlasticProvider.GetServerUrl();
    int32 ChangesetNumber = PlasticProvider.GetChangesetNumber();
    
    // 检查是否为部分工作区
    bool bPartial = PlasticProvider.IsPartialWorkspace();
    
    // 获取软件版本
    const FSoftwareVersion& Version = PlasticProvider.GetPlasticScmVersion();
    FString PluginVersion = PlasticProvider.GetPluginVersion();
    
    // 获取云组织名（如使用 Unity Cloud）
    FString Organization = PlasticProvider.GetCloudOrganization();
}
```

### 直接运行 cm 命令

```cpp
#include "PlasticSourceControlUtils.h"

// 运行任意 cm 命令
TArray<FString> Results, Errors;
bool bSuccess = PlasticSourceControlUtils::RunCommand(
    TEXT("status"),
    { TEXT("--all"), TEXT("--ignored") },
    { TEXT("/path/to/file") },
    Results,
    Errors
);

// 或通过 Shell 管道（更高效）
#include "PlasticSourceControlShell.h"

FString Output, Error;
bool bOk = PlasticSourceControlShell::RunCommand(
    TEXT("log"),
    { TEXT("--last"), TEXT("5") },
    {},
    Output,
    Error
);
```

### 版本检查

```cpp
#include "PlasticSourceControlVersions.h"
#include "SoftwareVersion.h"

// 检查 cm 版本是否支持某功能
FSoftwareVersion CurrentVersion(TEXT("11.0.16.8133"));
if (CurrentVersion >= PlasticSourceControlVersions::SmartLocks)
{
    // 支持 Smart Locks
}
```

### 工作区创建

```cpp
#include "PlasticSourceControlModule.h"

FPlasticSourceControlWorkspaceCreation& WorkspaceCreation = 
    FPlasticSourceControlModule::Get().GetWorkspaceCreation();

FPlasticSourceControlWorkspaceCreation::FParameters Params;
Params.WorkspaceName = FText::FromString(TEXT("MyWorkspace"));
Params.RepositoryName = FText::FromString(TEXT("MyRepo"));
Params.ServerUrl = FText::FromString(TEXT("MyOrganization@cloud"));
Params.bCreatePartialWorkspace = false;
Params.bAutoInitialCommit = true;
Params.InitialCommitMessage = FText::FromString(TEXT("Initial commit"));

WorkspaceCreation.MakeWorkspace(Params);
```

## Demo 示例

> ⚠️ 注意：PlasticSourceControl 的所有头文件都在 `Private` 目录下，**不是公共 API**。以下示例仅展示如何使用引擎通用的 SourceControl 接口与 Plastic SCM 交互。

### Build.cs 依赖

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "SourceControl",
});
```

### 检查文件状态并签出

```cpp
// MySourceControlHelper.h
#pragma once
#include "CoreMinimal.h"

class FMySourceControlHelper
{
public:
    static bool CheckOutFile(const FString& InFilePath);
    static bool CheckInFiles(const TArray<FString>& InFiles, const FString& InMessage);
    static bool RevertUnchangedFiles();
};
```

```cpp
// MySourceControlHelper.cpp
#include "MySourceControlHelper.h"
#include "ISourceControlModule.h"
#include "ISourceControlProvider.h"
#include "SourceControlOperations.h"

bool FMySourceControlHelper::CheckOutFile(const FString& InFilePath)
{
    ISourceControlProvider& Provider = ISourceControlModule::Get().GetProvider();
    if (!Provider.IsEnabled() || !Provider.IsAvailable())
    {
        return false;
    }
    
    TArray<FString> Files;
    Files.Add(InFilePath);
    
    FSourceControlOperationRef Operation = ISourceControlOperation::Create<FCheckOut>();
    ECommandResult::Type Result = Provider.Execute(Operation, Files);
    
    return Result == ECommandResult::Succeeded;
}

bool FMySourceControlHelper::CheckInFiles(const TArray<FString>& InFiles, const FString& InMessage)
{
    ISourceControlProvider& Provider = ISourceControlModule::Get().GetProvider();
    if (!Provider.IsEnabled() || !Provider.IsAvailable())
    {
        return false;
    }
    
    FSourceControlOperationRef Operation = ISourceControlOperation::Create<FCheckIn>();
    Operation->SetDescription(FText::FromString(InMessage));
    ECommandResult::Type Result = Provider.Execute(Operation, InFiles);
    
    return Result == ECommandResult::Succeeded;
}

bool FMySourceControlHelper::RevertUnchangedFiles()
{
    ISourceControlProvider& Provider = ISourceControlModule::Get().GetProvider();
    if (!Provider.IsEnabled() || !Provider.IsAvailable())
    {
        return false;
    }
    
    // RevertUnchanged 是 Plastic 的自定义操作
    // 需要通过 provider 名字匹配来使用
    // 通用方式：签出后逐个检查是否修改
    TArray<FString> EmptyFiles;
    FSourceControlOperationRef Operation = ISourceControlOperation::Create<FRevertUnchanged>();
    ECommandResult::Type Result = Provider.Execute(Operation, EmptyFiles);
    
    return Result == ECommandResult::Succeeded;
}
```

## 模块依赖

从 `PlasticSourceControl.Build.cs` 的 `PrivateDependencyModuleNames` 提取：

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型、容器、字符串 |
| `CoreUObject` | UObject 系统、包管理 |
| `Engine` | 引擎核心、UPackage 保存事件 |
| `Slate` | UI 框架（窗口、Widget） |
| `SlateCore` | Slate 核心类型 |
| `InputCore` | 输入处理 |
| `UnrealEd` | 编辑器功能 |
| `LevelEditor` | 关卡编辑器集成 |
| `DesktopPlatform` | 桌面平台文件对话框 |
| `SourceControl` | UE 源码控制抽象接口 |
| `SourceControlWindows` | 源码控制通用窗口（History、Sync 等） |
| `XmlParser` | 解析 `cm` 的 XML 输出 |
| `Projects` | 插件管理器 |
| `AssetRegistry` | 资产注册表，资产路径转换 |
| `DeveloperSettings` | 项目设置框架 |
| `ToolMenus` | 工具栏/菜单扩展 |
| `ContentBrowser` | Content Browser 集成 |

> ⚠️ 此插件只有 `PrivateDependencyModuleNames`，没有公共依赖。这意味着**其他模块无法直接依赖此插件的类型**——只能通过引擎的 `SourceControl` 公共接口交互。

## cm 版本兼容性

插件对 `cm` CLI 版本有最低要求和渐进式功能支持：

| cm 版本 | 日期 | 新增功能 |
|---|---|---|
| `9.0.16.4839` | 2021/01/05 | 最低支持版本，changelist `--` 前缀 |
| `11.0.16.7248` | 2022/07/28 | `--descriptionfile` 多行描述 |
| `11.0.16.7504` | 2022/10/13 | `cm shelveset apply` 选择性 unshelve |
| `11.0.16.7608` | 2022/11/07 | `history --limit`，UE5 `UnrealEditor.exe` 支持 |
| `11.0.16.7665` | 2022/12/01 | `undocheckout --keepchanges` |
| `11.0.16.7709` | 2023/01/12 | `status --iscochanged` 区分签出有无修改 |
| `11.0.16.7726` | 2023/01/19 | `merge --xml` |
| `11.0.16.8133` | 2023/08/03 | Smart Locks，`--datetimeformat` |
| `11.0.16.8445` | 2024/02/22 | `lock list --workingbranch` |

## 平台支持

| 平台 | 支持 |
|---|---|
| Win64 | ✅ |
| Linux | ✅ |
| Mac | ❌ |

## 维护状态

### 近期更新

1. **`6678228e49ce`** (2025-08-15) — World Partition HLOD: 新增 `-ReuseParentBranchHLODs` 选项，支持在分支间复用 HLOD actor 文件以减少补丁大小。这是跨多个源码控制 provider 的通用改动，Plastic 作为 SCC 后端之一受益。

2. **`9ca4e8114df3`** (2025-01-27) — 修复 #39402991 引入的本地化问题。由原 PR 作者通过 GitHub 提供修复。

3. **`7afc4a5ea137`** (2025-01-23) — 修复 Plastic 通知中重复的本地化字符串 key。

4. **`4ae6b2333b0c`** (2025-01-23) — **重大更新**：将 Plastic SCM provider 从 1.9.0 升级到 1.11.0。这是长时间以来最大的功能更新。

5. **`dc4568d5401c`** (2025-01-08) — 回退了 changelist 窗口显示重定向器文件的修复（OFPE 相关）。

### 维护评价

**活跃维护** — 此插件由 Unity/Codice Software 的开发者 Sébastien Rombauts 长期维护，是 UE5 版本控制基础设施的核心组成部分。

- ✅ 2025 年 1 月有重大版本升级（1.9.0 → 1.11.0），包含多项新功能
- ✅ 2025 年 8 月有跨 SCC 的功能增强
- ✅ 持续的 bug 修复和本地化维护
- ✅ 支持 Smart Locks、Shelving、Gluon 部分工作区等现代 Plastic SCM 特性
- ⚠️ 所有头文件都在 Private 目录，没有公共 API——这意味着其他插件无法直接扩展
- ⚠️ 仅支持 Win64 和 Linux，不支持 Mac

**推荐使用**：如果你的团队使用 Unity Version Control（原 Plastic SCM），此插件是官方支持的 UE5 集成方案，维护活跃，功能完善。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/PlasticSourceControl)
- [官方文档](https://docs.unity.com/ugs/en-us/manual/devops/manual/vcs-plugins/unreal-plugin)
- [Unity Version Control 下载和发行说明](https://www.plasticscm.com/download/releasenotes)
