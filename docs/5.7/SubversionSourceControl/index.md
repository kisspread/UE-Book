# Subversion

> Subversion source control management

| 属性 | 值 |
|---|---|
| 分类 | Source Control |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `SubversionSourceControl` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2014-03-14 |
| 年龄标签 | 🏛️ 文物（约 12 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/SubversionSourceControl) | |

## 用途

这是一个 Unreal Editor 源代码控制集成插件，将 [Apache Subversion (SVN)](https://subversion.apache.org/) 版本控制系统接入 UE5 编辑器的 Source Control 面板。插件通过调用外部 `svn` 命令行工具与 SVN 仓库交互，使开发者无需离开编辑器即可执行 checkout、checkin、update、revert、add、delete、resolve 等版本控制操作。

SVN 本身没有类似 Perforce 的 label/changelist 概念，此插件通过标准 SVN 仓库布局（`trunk/branches/tags`）中的 `tags/` 目录模拟 label 功能，将每个 tag 子目录视为一个版本标签。

## 使用场景

- 你的团队使用 SVN 管理 UE 项目资产和代码 → 启用此插件，在编辑器中直接操作版本控制
- 你需要在 Content Browser 中查看文件的版本状态（已修改、已签出、冲突等）→ 此插件提供状态图标和 tooltip
- 你需要查看文件历史、对比不同版本 → 通过 `UpdateStatus` 和 `Revision` 机制获取历史记录

## 蓝图用法

此插件不暴露任何 `UFUNCTION(BlueprintCallable)` 接口。所有功能通过 UE 编辑器的 Source Control 菜单和 Content Browser 右键菜单访问。

## C++ 用法

此插件作为编辑器内源代码控制 provider 运行，不直接对外暴露 C++ API。如需以编程方式与源代码控制交互，使用 `ISourceControlModule` 和 `ISourceControlProvider` 接口。

### 头文件引入

```cpp
#include "ISourceControlModule.h"
#include "ISourceControlProvider.h"
```

### 基本用法：获取当前 Provider

```cpp
// 获取源代码控制模块
ISourceControlModule& SCCModule = ISourceControlModule::Get();

// 检查是否已启用
if (SCCModule.IsEnabled())
{
    // 获取当前 provider（如果配置为 SVN，则返回 FSubversionSourceControlProvider）
    ISourceControlProvider& Provider = SCCModule.GetProvider();
    
    // 获取文件状态
    TArray<FString> Files = { TEXT("/Game/Maps/MyMap") };
    TArray<FSourceControlStateRef> States;
    Provider.GetState(Files, States, EStateCacheUsage::ForceUpdate);
    
    for (const auto& State : States)
    {
        UE_LOG(LogTemp, Log, TEXT("File: %s, CheckedOut: %d"), 
            *State->GetFilename(), State->IsCheckedOut());
    }
}
```

来源：`SubversionSourceControlProvider.cpp` 中的 `GetState()` 实现。

### 进阶用法：执行操作

```cpp
// 执行 checkout 操作
TSharedRef<FCheckOut, ESPMode::ThreadSafe> CheckOutOp = ISourceControlOperation::Create<FCheckOut>();
TArray<FString> Files = { TEXT("/Game/MyAsset.uasset") };

Provider.Execute(CheckOutOp, Files);
```

来源：`SubversionSourceControlProvider.cpp` 中的 `Execute()` 实现。

## Demo 示例

此插件是编辑器内部模块，无需用户代码集成。使用方式：

1. 打开 **Edit → Project Settings → Source Control**
2. 选择 **Subversion** 作为 Source Control Provider
3. 填写 Repository URL（如 `https://svn.example.com/repo/trunk`）
4. 填写用户名
5. 可选：填写 Labels Root（如 `tags/`），用于模拟 Perforce label
6. 点击 **Accept Settings**

## 模块依赖

从 `SubversionSourceControl.Build.cs` 的 `PrivateDependencyModuleNames` 提取：

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心库（字符串、容器、文件系统等） |
| `Slate` | UI 框架，用于设置面板 |
| `SlateCore` | Slate 核心类型 |
| `SourceControl` | UE 源代码控制抽象层（`ISourceControlProvider` 等接口） |
| `XmlParser` | 解析 SVN 命令的 XML 输出 |

此外，插件在 Win64 和 Mac 平台上依赖 `Engine/Binaries/ThirdParty/svn/` 目录下的 SVN 二进制文件。

## 架构概述

插件遵循 UE 源代码控制的标准 worker 模式：

```
FSubversionSourceControlModule (IModuleInterface)
  ├── FSubversionSourceControlProvider (ISourceControlProvider)
  │     ├── Worker 注册表 (WorkersMap)
  │     ├── 状态缓存 (StateCache)
  │     └── 命令队列 (CommandQueue)
  └── FSubversionSourceControlSettings
        ├── Repository URL
        ├── UserName
        ├── LabelsRoot
        └── ExecutableLocation
```

### Worker 列表

每个 Worker 实现 `ISubversionSourceControlWorker` 接口，封装一个 SVN 命令：

| Worker | 对应操作 | SVN 命令 |
|---|---|---|
| `FSubversionConnectWorker` | 连接仓库 | `svn info` |
| `FSubversionCheckOutWorker` | 签出文件 | `svn update` |
| `FSubversionCheckInWorker` | 提交变更 | `svn commit` |
| `FSubversionMarkForAddWorker` | 标记添加 | `svn add` |
| `FSubversionDeleteWorker` | 删除文件 | `svn delete` |
| `FSubversionRevertWorker` | 还原文件 | `svn revert` |
| `FSubversionSyncWorker` | 同步/更新 | `svn update` |
| `FSubversionUpdateStatusWorker` | 刷新状态 | `svn status` + `svn log` |
| `FSubversionCopyWorker` | 复制/分支 | `svn copy` |
| `FSubversionResolveWorker` | 解决冲突 | `svn resolve` |

### 文件状态模型

`FSubversionSourceControlState` 维护每个文件的状态：

- **WorkingCopyState**: `Unknown`, `Pristine`, `Added`, `Deleted`, `Modified`, `Replaced`, `Conflicted`, `External`, `Ignored`, `Incomplete`, `Merged`, `NotControlled`, `Obstructed`, `Missing`, `NotAWorkingCopy`
- **LockState**: `Unknown`, `NotLocked`, `Locked`, `LockedOther`
- 支持历史记录查询（通过 `svn log`）
- 支持文件修订版本追踪（`LocalRevNumber`）

### 命令执行模型

`FSubversionSourceControlCommand` 实现 `IQueuedWork` 接口，支持多线程执行。命令被放入队列，由 `FSubversionSourceControlProvider::Tick()` 在主线程上处理结果。

## 维护状态

### 近期更新

| 日期 | Hash | 说明 |
|---|---|---|
| 2025-08-15 | `6678228e49ce` | World Partition HLOD 新增 `-ReuseParentBranchHLODs` 选项，涉及 SCC 分支复用逻辑 |
| 2025-03-31 | `4479e8be794f` | 将 `GetRepoName` 调用移到循环外部（性能优化） |
| 2024-11-06 | `bc63a88d067f` | 将旧的 `CppCompileWarning` 属性重定向到新的 `CppCompileWarningSettings` |

### 维护评价

- **年龄**: 创建于 2014 年，是 UE4 早期就存在的插件（约 12 年）
- **更新频率**: 最近的更新多为编译兼容性修复和小优化，非功能性更新
- **活跃度**: 维护不活跃——SVN 在游戏行业的使用率已大幅下降，Epic 主推 Perforce (P4V) 和 Git
- **已知限制**: 依赖外部 `svn` 命令行工具；SVN 不原生支持 label/changelist，插件通过 `tags/` 目录模拟
- **推荐**: 如果团队仍在使用 SVN，此插件可用；新项目建议使用 Git 或 Perforce

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/SubversionSourceControl)
- 官方文档：无（`.uplugin` 中 DocsURL 为空）
