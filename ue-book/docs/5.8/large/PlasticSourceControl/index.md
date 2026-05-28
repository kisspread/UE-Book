# Plastic SCM

> Unity Version Control (formerly Plastic SCM)

| 属性 | 值 |
|---|---|
| 中文名 | Unity 版本控制 |
| 分类 | Source Control |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `PlasticSourceControl` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2019-10-02 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/PlasticSourceControl) | |

## 用途

Plastic SCM 插件将 Unity Version Control（原 Plastic SCM）集成到 Unreal Engine 的源代码管理系统中，作为 `ISourceControlProvider` 的实现。它允许开发者在编辑器内部直接执行常见的版本控制操作，包括：

- **文件检入/检出/还原**：标准的 VCS 文件操作
- **分支管理**：创建、切换、合并、重命名、删除分支，以及专用的分支浏览器窗口
- **变更集管理**：浏览变更集列表、查看变更集内的文件差异，以及专用的变更集浏览器窗口
- **文件锁管理**：查看、释放、删除文件锁，支持 Smart Locks 功能，以及专用的锁浏览器窗口
- **工作区管理**：创建新工作区（包括 Partial/Gluon 工作区）、同步、切换到指定变更集或分支
- **搁置（Shelve）支持**：搁置和取消搁置变更
- **桌面应用集成**：一键打开 Unity Version Control 桌面应用进行可视化 Diff、Branch Explorer 等高级操作

该插件通过 `cm shell` 后台进程与 Plastic SCM CLI 通信，支持异步命令执行，避免阻塞编辑器主线程。

## 使用场景

- 你的团队使用 Unity Version Control（原 Plastic SCM）作为版本控制系统 → 安装此插件即可在 UE 编辑器内完成所有 VCS 操作
- 你需要在编辑器内管理文件锁以避免合并冲突 → 使用锁浏览器窗口
- 你需要可视化查看和切换分支 → 使用分支浏览器窗口
- 你需要审查其他开发者提交的变更集 → 使用变更集浏览器窗口
- 你使用 Partial/Gluon 工作区来管理大型资产库 → 支持 Partial 工作区切换

## 蓝图用法

此插件不提供 BlueprintCallable 函数。它作为 `ISourceControlProvider` 的注册实现，所有功能通过编辑器的源代码控制 UI（工具栏菜单、右键菜单、专用窗口）访问。

### 项目设置

插件在 **Project Settings → Source Control - Unity Version Control** 中提供以下可配置选项：

| 设置 | 说明 |
|---|---|
| `UserNameToDisplayName` | 将 Plastic 用户名（通常是邮箱）映射为简短显示名 |
| `bHideEmailDomainInUsername` | 隐藏用户名中的邮箱域名部分（默认开启） |
| `bPromptForCheckoutOnChange` | 文件变更时提示检出（默认开启） |
| `LimitNumberOfRevisionsInHistory` | 历史窗口中显示的最大修订数（默认 50） |
| 分支浏览器列显示 | 控制是否显示 Repository、CreatedBy、Date、Comment 列 |
| 锁浏览器列显示 | 控制是否显示 Id、Workspace、Date、DestinationBranch 列 |
| 变更集浏览器列显示 | 控制是否显示 CreatedBy、Date、Comment、Branch 列 |

### 编辑器设置

在 **Editor Preferences → Source Control** 中可配置：

| 设置 | 说明 |
|---|---|
| Binary Path | `cm` 可执行文件路径（默认 `"cm"`，依赖系统 PATH） |
| Update Status at Startup | 启动时异步更新状态（默认关闭，大型项目可能很慢） |
| Update Status Other Branches | 检查其他分支的最近变更集（可能较慢） |
| View Local Changes | 变更窗口中同时显示本地已修改和未跟踪文件 |
| Enable Verbose Logs | 启用详细日志 |

## C++ 用法

此插件的所有类均为 `Private` 头文件，不对外暴露公共 API。它是 UE 源代码控制系统的内部实现，不作为可编程接口使用。

### 如何通过源代码控制系统 API 交互

如果你需要在 C++ 中与源代码控制系统交互（不限于 Plastic），使用 UE 通用的 `ISourceControlProvider` 接口：

```cpp
#include "ISourceControlModule.h"
#include "ISourceControlProvider.h"

// 获取当前源代码控制提供者
ISourceControlProvider& Provider = ISourceControlModule::Get().GetProvider();

// 执行同步操作（例如 Checkout）
TArray<FString> Files;
Files.Add(TEXT("/Game/MyAsset.uasset"));

FSourceControlOperationRef Operation = ISourceControlOperation::Create<FCheckOut>();
ECommandResult::Type Result = Provider.Execute(Operation, Files);
```

**注意**：Plastic 插件的具体内部实现类（如 `FPlasticSourceControlProvider`、`FPlasticSourceControlState` 等）位于 `Private/` 目录下，不是公共 API 的一部分。直接使用这些类可能导致编译问题和版本兼容性问题。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `WorkspaceNotification` | 工作区通知和桌面通知支持 |
| `ToolWidgets` | 编辑器工具控件（搜索框等） |

此外，该插件在运行时依赖系统中安装的 Unity Version Control CLI 工具（`cm` 命令）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-30 | `a7404169` | SourceControl: Add provider capability flag to use 'soft revert' when performing an FRevert prior to | 添加软还原能力标志，优化 FRevert 操作 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式说明符不匹配问题 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移到 UE_LOGF 宏 |
| 2026-03-18 | `9271d5a5` | SourceControl: Deprecate IsAtLatestRevision() / GetNumLocalChanges() interfaces. | 废弃 IsAtLatestRevision/GetNumLocalChanges 接口 |
| 2026-02-03 | `a06af5c3` | Added a function to check if there are any dirty packages. | 添加脏包检测函数 |

### 维护评价

- **活跃维护**：最近 3 个月内持续有实质性更新（新功能、API 调整、Bug 修复），由 Codice Software/SRombauts 持续维护
- **成熟度高**：自 2019 年创建以来持续迭代，当前版本为 1.11.0，功能完整
- **CLI 版本兼容性**：支持最低 `cm` 版本 9.0.16.4839（2021 年），最新特性要求 11.0.16.8445（2024 年），需要定期更新 CLI 工具以获得完整功能
- **平台限制**：仅支持 Win64 和 Linux，不支持 macOS
- **推荐使用**：如果你的团队使用 Unity Version Control，此插件是官方支持的 UE 集成方案，推荐使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/PlasticSourceControl)
- [官方文档](https://docs.unity.com/ugs/en-us/manual/devops/manual/vcs-plugins/unreal-plugin)
- [支持页面](https://support.unity.com/hc/en-us/requests/new?ticket_form_id=360001051792)