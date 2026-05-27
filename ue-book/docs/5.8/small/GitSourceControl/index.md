# Git Source Control

> Git source control management（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | Git 源码管理 |
| 分类 | Source Control |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `GitSourceControl` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2015-01-19 |
| 年龄标签 | 🏛️ 文物（约 11 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/GitSourceControl) | |

## 用途

该插件将 Git 版本控制系统集成到 Unreal Editor 中，实现 `ISourceControlProvider` 接口。它允许开发者在编辑器内直接完成所有常见的 Git 操作——包括文件状态跟踪、提交、拉取、差异对比、回退和合并冲突解决——无需切换到终端或外部 Git 客户端。

插件的核心价值在于：
- 将 `git status`、`git commit`、`git log` 等命令封装为编辑器源码控制操作
- 自动检测 Git 二进制路径和仓库根目录
- 解析 Git 输出并转换为 UE 源码控制状态（修改/新增/删除/冲突等）
- 提供 Git LFS 大文件存储支持
- 提供编辑器内初始化 Git 仓库的 UI 流程（含自动创建 .gitignore）

尽管标记为 Beta，该插件默认启用且是 UE 中使用 Git 的标准方式。

## 使用场景

- 你的团队使用 Git 管理 UE 项目源码和资产 → 启用此插件，在编辑器中直接提交和查看状态
- 你需要在 Content Browser 中看到每个资产的版本控制状态图标（已修改/已添加/未跟踪等）→ 该插件提供这些状态图标
- 你需要对比 Blueprint 的不同版本 → 插件支持 Blueprint 可视化差异对比
- 你需要在编辑器内拉取远程更新 → 使用 Sync 操作执行 `git pull --rebase`
- 你的项目使用 Git LFS 管理大型资产文件 → 插件自动检测 LFS 能力
- 你需要将资产从一个项目迁移到另一个 Git 项目 → 支持跨项目资产迁移

## 蓝图用法

该插件**不暴露任何 BlueprintCallable 函数**。它作为编辑器源码控制提供者（`ISourceControlProvider`）运行，通过编辑器菜单和 Content Browser 集成使用。

所有操作通过编辑器 UI 触发：
1. **Connect**：编辑器启动时自动连接（或通过 Source Control 菜单）
2. **状态图标**：Content Browser 中自动显示文件状态
3. **右键菜单**：对资产执行 Commit、Revert、History 等操作

## C++ 用法

### 头文件引入

```cpp
#include "GitSourceControlProvider.h"
#include "GitSourceControlState.h"
#include "GitSourceControlUtils.h"
```

### 基本用法 — 通过源码控制 API 操作 Git

```cpp
// 通过 ISourceControlModule 获取 Git Provider
ISourceControlModule& SourceControlModule = ISourceControlModule::Get();
ISourceControlProvider* Provider = SourceControlModule.GetProvider();

if (Provider && Provider->GetName() == FName("Git"))
{
    // 获取文件状态
    TArray<FString> Files;
    Files.Add(TEXT("/Game/Maps/MyLevel.umap"));
    
    TArray<FSourceControlStateRef> OutStates;
    ECommandResult::Type Result = Provider->GetState(Files, OutStates, EStateCacheUsage::ForceUpdate);
    
    if (Result == ECommandResult::Succeeded && OutStates.Num() > 0)
    {
        FSourceControlStateRef State = OutStates[0];
        if (State->IsModified())
        {
            UE_LOG(LogTemp, Log, TEXT("文件已修改: %s"), *State->GetFilename());
        }
    }
}
```
*来源：`GitSourceControlProvider.h` 中 `GetState()` / `Execute()` 接口定义*

### 进阶用法 — 异步执行提交操作

```cpp
// 构造提交操作
FSourceControlOperationRef CheckInOperation = ISourceControlOperation::Create<FCheckIn>();

// 设置提交文件列表
TArray<FString> FilesToCommit;
FilesToCommit.Add(TEXT("/Game/Blueprints/MyActor.uasset"));

// 异步执行，通过回调接收结果
FSourceControlOperationComplete CompletionDelegate = FSourceControlOperationComplete::CreateLambda(
    [](const FSourceControlOperationRef& InOperation, ECommandResult::Type InResult)
    {
        if (InResult == ECommandResult::Succeeded)
        {
            UE_LOG(LogTemp, Log, TEXT("提交成功"));
        }
    }
);

Provider->Execute(CheckInOperation, nullptr, FilesToCommit, EConcurrency::Asynchronous, CompletionDelegate);
```
*来源：`GitSourceControlProvider.h` 中 `Execute()` 接口定义*

### 直接调用 Git 工具函数

```cpp
// 查找 Git 二进制路径
FString GitBinaryPath = GitSourceControlUtils::FindGitBinaryPath();

// 检查 Git 可用性
FGitVersion GitVersion;
bool bAvailable = GitSourceControlUtils::CheckGitAvailability(GitBinaryPath, &GitVersion);

// 查找仓库根目录
FString RepositoryRoot;
GitSourceControlUtils::FindRootDirectory(FPaths::ProjectDir(), RepositoryRoot);

// 获取当前分支名
FString BranchName;
GitSourceControlUtils::GetBranchName(GitBinaryPath, RepositoryRoot, BranchName);

// 获取用户配置
FString UserName, UserEmail;
GitSourceControlUtils::GetUserConfig(GitBinaryPath, RepositoryRoot, UserName, UserEmail);
```
*来源：`GitSourceControlUtils.h` 中的工具函数声明*

## Demo 示例

一个完整的示例：在编辑器工具中检测 Git 状态并获取当前分支名。

### MyGitStatusWidget.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Widgets/SCompoundWidget.h"

class SMyGitStatusWidget : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SMyGitStatusWidget) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs);

private:
    FText GetGitStatusText() const;
    FText GetBranchName() const;
    FReply OnRefreshClicked();
    void RefreshStatus();

    FText StatusText;
    FText BranchText;
};
```

### MyGitStatusWidget.cpp

```cpp
#include "MyGitStatusWidget.h"
#include "GitSourceControlProvider.h"
#include "GitSourceControlUtils.h"
#include "ISourceControlModule.h"
#include "Widgets/Text/STextBlock.h"
#include "Widgets/Input/SButton.h"
#include "Widgets/SBoxPanel.h"

void SMyGitStatusWidget::Construct(const FArguments& InArgs)
{
    ChildSlot
    [
        SNew(SVerticalBox)
        + SVerticalBox::Slot().AutoHeight().Padding(4)
        [
            SNew(STextBlock).Text_Lambda([this]() { return BranchText; })
        ]
        + SVerticalBox::Slot().AutoHeight().Padding(4)
        [
            SNew(STextBlock).Text_Lambda([this]() { return StatusText; })
        ]
        + SVerticalBox::Slot().AutoHeight().Padding(4)
        [
            SNew(SButton)
            .Text(FText::FromString(TEXT("刷新")))
            .OnClicked(this, &SMyGitStatusWidget::OnRefreshClicked)
        ]
    ];

    RefreshStatus();
}

FReply SMyGitStatusWidget::OnRefreshClicked()
{
    RefreshStatus();
    return FReply::Handled();
}

void SMyGitStatusWidget::RefreshStatus()
{
    ISourceControlModule& SCCModule = ISourceControlModule::Get();
    ISourceControlProvider* Provider = SCCModule.GetProvider();

    if (Provider && Provider->GetName() == FName("Git") && Provider->IsAvailable())
    {
        StatusText = FText::FromString(TEXT("Git 已连接"));

        // 获取分支名
        FString GitBinaryPath = GitSourceControlUtils::FindGitBinaryPath();
        FString RepoRoot = Provider->GetStatusText().ToString();
        FString Branch;
        if (GitSourceControlUtils::GetBranchName(GitBinaryPath, FPaths::ProjectDir(), Branch))
        {
            BranchText = FText::Format(FText::FromString(TEXT("当前分支: {0}")), FText::FromString(Branch));
        }
    }
    else
    {
        StatusText = FText::FromString(TEXT("Git 未连接"));
        BranchText = FText::GetEmpty();
    }
}
```

## 模块依赖

该插件是编辑器插件，通过 UE 内置的源码控制框架工作。使用者**无需在自己的 Build.cs 中依赖此插件模块**，只需在编辑器设置中选择 Git 作为源码控制提供者。

如需在自定义编辑器工具中编程访问 Git 状态，需依赖：

| 模块 | 用途 |
|---|---|
| `SourceControl` | UE 源码控制接口框架（ISourceControlModule / ISourceControlProvider） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-30 | `a7404169` | SourceControl: Add provider capability flag to use 'soft revert' when performing an FRevert prior to | 新增软回退能力标志，回退前不再删除文件 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移到 UE_LOGF 格式 |
| 2026-03-18 | `9271d5a5` | SourceControl: Deprecate IsAtLatestRevision() / GetNumLocalChanges() interfaces. | 废弃旧版版本检查和本地变更计数接口 |
| 2026-01-28 | `5f766aee` | Fixed modules that does not support portable toolchain | 修复可移植工具链编译兼容性 |
| 2026-01-24 | `e793e61e` | Fixed more compile errors when using portable toolchain | 修复更多可移植工具链编译错误 |

### 维护评价

该插件**仍在活跃维护中**。从 2026 年的提交记录看，更新频率稳定（约每 2-4 周一次），且包含功能性改进（软回退能力）和 API 规范化（废弃旧接口）。

**注意事项**：
- 插件自创建至今已约 11 年，标记仍为 Beta（`IsBetaVersion=true`），但默认启用
- 已知限制：编辑器内不显示删除/缺失文件状态、不支持 Tag 管理、不支持 Push/Pull 的编辑器内工作流
- 原子提交上限为 20 个文件（受 Git 单次 commit 限制）
- **推荐使用**：作为 UE 项目中使用 Git 的标准方式，该插件是唯一选择且持续维护

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/GitSourceControl)
- [官方文档]()（无）