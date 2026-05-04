# Git

> Git source control management

| 属性 | 值 |
|---|---|
| 分类 | Source Control |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 否 |
| 模块 | GitSourceControl (Editor) |
| 创建时间 | 2015-01-19 |
| 年龄标签 | 🏛️ 文物(>10年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/GitSourceControl) | |

## 用途

GitSourceControl 是 UE5 内置的 Git 版本控制提供者（Source Control Provider），让你可以在 Unreal Editor 内部直接执行 Git 操作，无需切换到命令行或外部 Git GUI 工具。

它解决了什么问题：UE 的源码管理（Source Control）系统是可插拔的，默认支持 Perforce（P4）。这个 plugin 把 Git 作为后端接入同一套 UI 和工作流，使得使用 Git 管理项目的团队也能获得编辑器内的版本控制集成——状态图标、提交、同步、差异对比等功能。

值得注意的是，虽然 `.uplugin` 标记了 `IsBetaVersion: true`，但该 plugin 从 2015 年至今一直在引擎中随附，功能基本稳定。

## 使用场景

- 你的团队使用 Git（GitHub / GitLab / Bitbucket 等）管理 UE 项目 → 在 Editor 的 Source Control 面板选择 "Git" 作为提供者
- 你想在 Content Browser 中看到文件的修改/新增/删除状态图标 → 启用此 plugin 后自动生效
- 你想在 Editor 内直接提交（Commit）蓝图、材质等资产的变更 → 右键资产 → Source Control → Check In
- 你想对比蓝图的当前版本和 depot 版本（Visual Diff）→ 右键资产 → Source Control → Diff Against Depot
- 你想在 Editor 内执行 Sync（Pull）操作 → Source Control 面板 → Sync

## 蓝图用法

此 plugin **不暴露任何蓝图节点**。所有功能通过 UE 的 Source Control UI 面板和右键菜单交互，不提供 `BlueprintCallable` / `BlueprintReadWrite` API。

Editor 内的操作入口：

| 操作 | 菜单路径 | 底层 Git 命令 |
|---|---|---|
| 连接 | Edit → Project Settings → Source Control → Git | 自动查找 `.git` 目录 |
| 提交 | 右键资产 → Source Control → Check In | `git commit` |
| 标记添加 | 右键资产 → Source Control → Mark for Add | `git add` |
| 删除 | 右键资产 → Source Control → Delete | `git rm` |
| 还原 | 右键资产 → Source Control → Revert | `git checkout` |
| 同步 | Source Control 面板 → Sync | `git pull --rebase` |
| 状态刷新 | Source Control 面板 → Update Status | `git status` |
| 移动/复制 | 右键资产 → Source Control → Copy/Move | `git mv` |
| 解决冲突 | 右键资产 → Source Control → Resolve | `git add`（标记冲突已解决） |
| 差异对比 | 右键资产 → Source Control → Diff Against Depot | `git diff` / `git show` |

## C++ 用法

此 plugin 的所有源文件位于 `Private/` 目录下，不暴露 Public API。它是一个纯 Editor 插件，通过 UE 的 `ISourceControlProvider` 接口注册到引擎的 Source Control 系统中，不供外部模块直接调用。

如果你需要在代码中与 Source Control 交互，应该使用引擎的通用接口 `ISourceControlModule` / `ISourceControlProvider`，而不是直接引用 GitSourceControl。

### 通过引擎接口间接使用

```cpp
#include "ISourceControlModule.h"
#include "ISourceControlProvider.h"

// 获取当前激活的 Source Control Provider
ISourceControlProvider& Provider = ISourceControlModule::Get().GetProvider();

// 查询文件状态
TArray<FString> Files;
Files.Add(TEXT("/Game/MyAsset"));
TArray<FSourceControlStateRef> States;
Provider.GetState(Files, States, EStateCacheUsage::ForceUpdate);
```

### 模块结构

| 文件 | 职责 |
|---|---|
| `FGitSourceControlModule` | 模块入口，注册 Provider，管理 Settings 生命周期 |
| `FGitSourceControlProvider` | 核心 Provider 实现，管理命令队列、状态缓存、Worker 分发 |
| `FGitSourceControlCommand` | 封装单次 Git 命令的执行（支持同步/异步），实现 `IQueuedWork` |
| `IGitSourceControlWorker` | Worker 接口，每种操作对应一个实现类 |
| `GitSourceControlOperations.h` | 9 个 Worker 实现：Connect / CheckIn / MarkForAdd / Delete / Revert / Sync / UpdateStatus / Copy / Resolve |
| `FGitSourceControlState` | 文件状态表示（Modified / Added / Deleted / Conflicted 等） |
| `FGitSourceControlRevision` | 文件修订版本信息（关联到 Git commit SHA1） |
| `GitSourceControlUtils` | Git 命令行调用工具函数（`RunCommand`、`RunCommit` 等） |
| `FGitSourceControlSettings` | 设置管理（Git 二进制路径），持久化到 ini |
| `SGitSourceControlSettings` | 设置 UI 面板（Slate Widget） |

## Demo 示例

由于此 plugin 不暴露 Public API，无法编写独立的 C++ Demo。使用方式是：

1. **启用 Plugin**：Edit → Plugins → 搜索 "Git Source Control" → 确认已启用（默认已启用）
2. **配置 Provider**：Edit → Project Settings → Source Control → 选择 "Git"
3. **首次连接**：如果项目目录已有 `.git`，会自动连接；如果没有，可在设置面板点击 "Initialize Git Repository"
4. **日常使用**：在 Content Browser 中右键资产即可看到 Source Control 操作菜单

### 初始化 Git 仓库

在 Editor 的 Source Control 设置面板中，可以：

- ✅ 创建 `.gitignore` 文件（自动生成 UE 专用规则）
- ✅ 创建 `README.md`
- ✅ 创建 `.gitattributes`（用于 Git LFS 配置）
- ✅ 自动执行初始提交（Initial Commit）
- ✅ 配置 Remote URL（如 GitHub 仓库地址）

## 模块依赖

从 `GitSourceControl.Build.cs` 的 `PrivateDependencyModuleNames` 提取。注意：此 plugin 不暴露 Public API，依赖均为私有。

| 模块 | 用途 |
|---|---|
| `Core` | 基础引擎功能 |
| `Slate` | UI 框架（设置面板） |
| `SlateCore` | Slate 核心 |
| `InputCore` | 输入处理 |
| `DesktopWidgets` | 桌面 UI 控件 |
| `SourceControl` | UE 源码管理抽象层（核心依赖） |
| `CoreUObject` | 仅编辑器构建 |
| `EditorFramework` | 仅编辑器构建 |
| `UnrealEd` | 仅编辑器构建 |

## 维护状态

### 近期更新

| 日期 | Hash | 提交信息 | 解读 |
|---|---|---|---|
| 2025-08-15 | `6678228e` | World Partition - HLOD: Added new option -ReuseParentBranchHLODs for HLOD builds | 非 GitSourceControl 核心改动，是在 HLOD 构建流程中增加了对 SCC（源码管理）的分支复用支持，间接涉及该 plugin 的 Provider 接口 |
| 2025-04-11 | `038fbb06` | Fix for `RunDumpToFile` to finish reading the pipe | Bug 修复：修复 `RunDumpToFile` 工具函数未正确完成管道读取的问题，影响文件 revision 的 dump 操作 |
| 2024-11-06 | `bc63a88d` | Redirect old cppcompilewarning properties to new *.CppCompileWarningSettings | 非功能性改动，是编译警告配置的迁移 |

### 维护评价

- **创建时间**：2015-01-19，已超过 11 年，属于引擎中最早的一批插件
- **标记状态**：`IsBetaVersion: true`，但已随引擎发布多年，实质上是稳定可用的
- **最近更新频率**：近 1 年有 3 次 commit，但大部分是非核心改动（编译配置迁移、HLOD 流程集成）
- **实质性修复**：2025-04 的 `RunDumpToFile` 管道读取修复是唯一与核心功能直接相关的更新
- **未实现的功能**（源码注释中标注）：
  - Git Tags 支持（`ISourceControlLabel` 未实现）
  - 分支管理不在 Editor 工作流中
  - Pull/Fetch/Push 不在 Editor 工作流中（仅 Sync = pull --rebase）
  - Amend commit 不在 Editor 工作流中
- **已知问题**（源码注释中标注）：
  - 编辑器不显示已删除文件
  - 不显示 `.uproject` 文件状态
  - 蓝图重命名后 Git 无法追踪历史
  - 文件历史中 Changelist 显示为有符号整数而非十六进制 SHA1
- **推荐程度**：✅ 推荐使用。虽然是 "Beta"，但已非常成熟，是使用 Git 管理 UE 项目的事实标准方案

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/GitSourceControl)
- [官方文档]() （.uplugin 中未提供 DocsURL）
- 测试用例：未找到（Engine/Tests 目录下无相关测试文件）
