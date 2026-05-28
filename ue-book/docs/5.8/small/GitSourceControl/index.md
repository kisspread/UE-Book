# Git Source Control

> Git source control management

| 属性 | 值 |
|---|---|
| 中文名 | 源码管理 |
| 分类 | Source Control |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `GitSourceControl` (Editor) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2015-01-19 |
| 年龄标签 | 🏛️ 文物（约 10 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/GitSourceControl) | |

## 用途

该插件将 Git 版本控制系统深度集成到 Unreal Engine 编辑器中，允许开发者在编辑器内直接执行大部分常见的版本控制操作，而无需频繁切换到命令行或外部 Git 客户端。它解决了在游戏开发工作流中管理资产和代码版本的需求，将版本控制状态可视化（如文件状态图标），并提供了提交、更新、差异对比、历史查看等编辑器内功能，极大地提升了团队协作的效率。

## 使用场景

- 你在使用 Git 管理你的 Unreal Engine 项目，并希望直接在编辑器中查看文件的修改状态（如已修改、新增、冲突）并进行提交。
- 你需要在编辑器中快速比较蓝图资产与仓库中的版本，或在不同提交版本间进行视觉差异对比。
- 你希望执行 “Sync” 操作来拉取远程最新代码，但前提是没有未提交的本地修改。

## 蓝图用法

此插件主要作为编辑器内 UI 功能集成，公开的蓝图 API 相对有限，大部分操作通过编辑器的“源码管理”菜单触发。

### 核心设置节点

插件提供了一个设置界面 (`SGitSourceControlSettings`)，允许在编辑器中配置 Git 路径并初始化仓库。相关的底层函数主要通过 `FGitSourceControlModule` 和 `FGitSourceControlProvider` 类访问，这些并非设计为蓝图可调用的节点。

### 使用示例（蓝图描述）

由于此插件主要提供编辑器集成而非游戏运行时蓝图 API，其使用流程通常如下：
1.  在 `项目设置 > 插件 > 源码管理` 中选择 Git 作为提供者。
2.  在编辑器内右键点击内容浏览器中的资产，选择“源码管理”子菜单进行操作（如提交、更新、查看差异）。
3.  在“源码管理”面板中查看当前分支、用户信息以及操作队列。

## C++ 用法

开发者可以通过 C++ 代码与 Git 源码管理提供者交互，执行自动化脚本或集成版本控制逻辑到编辑器工具中。

### 头文件引入

```cpp
#include "GitSourceControlModule.h"
#include "GitSourceControlProvider.h"
#include "GitSourceControlUtils.h"
```

### 基本用法

以下代码展示了如何获取 Git 提供者并检查其可用性。
（参考 `GitSourceControlModule.h`, `GitSourceControlProvider.h`）

```cpp
// 获取 Git 源码管理模块
FGitSourceControlModule& GitModule = FModuleManager::LoadModuleChecked<FGitSourceControlModule>("GitSourceControl");

// 获取提供者实例
FGitSourceControlProvider& Provider = GitModule.GetProvider();

// 检查 Git 是否可用且仓库已找到
if (Provider.IsGitAvailable() && Provider.IsAvailable())
{
    // 获取当前分支名、用户信息等
    FString BranchName = Provider.GetStatusText().ToString();
    FString UserName = Provider.GetUserName();
    FString UserEmail = Provider.GetUserEmail();
    
    UE_LOG(LogTemp, Log, TEXT("Git Ready. Branch: %s, User: %s <%s>"), *BranchName, *UserName, *UserEmail);
}
else
{
    UE_LOG(LogTemp, Warning, TEXT("Git source control is not available. Check binary path and repository."));
}
```

### 进阶用法

利用 `GitSourceControlUtils` 中的静态函数，可以执行底层的 Git 命令。以下示例演示了如何运行一个自定义的 Git 状态命令。
（参考 `GitSourceControlUtils.h`）

```cpp
#include "GitSourceControlUtils.h"
#include "GitSourceControlProvider.h"

void CheckCustomGitStatus(const TArray<FString>& FilesToCheck)
{
    FGitSourceControlModule& GitModule = FModuleManager::LoadModuleChecked<FGitSourceControlModule>("GitSourceControl");
    FGitSourceControlProvider& Provider = GitModule.GetProvider();
    
    if (!Provider.IsGitAvailable()) return;

    const FString GitBinaryPath = Provider.AccessSettings().GetBinaryPath();
    const FString RepositoryRoot = Provider.GetPathToRepositoryRoot();
    
    TArray<FString> Parameters;
    Parameters.Add(TEXT("--short")); // 使用简短格式
    Parameters.Add(TEXT("--untracked-files=normal")); // 包含未跟踪文件
    
    TArray<FString> Results;
    TArray<FString> Errors;
    
    // 执行 `git status --short` 命令
    if (GitSourceControlUtils::RunCommand(TEXT("status"), GitBinaryPath, RepositoryRoot, Parameters, FilesToCheck, Results, Errors))
    {
        for (const FString& Line : Results)
        {
            UE_LOG(LogTemp, Log, TEXT("Git Status: %s"), *Line);
        }
    }
    else
    {
        for (const FString& Error : Errors)
        {
            UE_LOG(LogTemp, Error, TEXT("Git Status Error: %s"), *Error);
        }
    }
}
```

## Demo 示例

以下是一个简单的 Editor Utility Widget 蓝图类（或编辑器模块），用于显示当前 Git 仓库状态信息。

**GitStatusWidget.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Widgets/SCompoundWidget.h"

class SGitStatusWidget : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SGitStatusWidget) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs);

private:
    FText GetStatusText() const;
    FText GetBranchText() const;
    FText GetUserText() const;
    
    TSharedRef<SWidget> BuildInfoRow(const FText& Label, TAttribute<FText> Value) const;
    
    // 用于定时刷新状态的定时器
    FTimerHandle RefreshTimerHandle;
    void RefreshStatus();
    
    FText CurrentStatusText;
    FText CurrentBranchText;
    FText CurrentUserText;
};
```

**GitStatusWidget.cpp**
```cpp
#include "GitStatusWidget.h"
#include "GitSourceControlModule.h"
#include "GitSourceControlProvider.h"
#include "Widgets/Text/STextBlock.h"
#include "Widgets/Layout/SBox.h"
#include "TimerManager.h"
#include "Engine/World.h"

void SGitStatusWidget::Construct(const FArguments& InArgs)
{
    ChildSlot
    [
        SNew(SVerticalBox)
        + SVerticalBox::Slot().AutoHeight().Padding(4)
        [
            BuildInfoRow(NSLOCTEXT("GitWidget", "StatusLabel", "Status:"), TAttribute<FText>::Create(TAttribute<FText>::FGetter::CreateSP(this, &SGitStatusWidget::GetStatusText)))
        ]
        + SVerticalBox::Slot().AutoHeight().Padding(4)
        [
            BuildInfoRow(NSLOCTEXT("GitWidget", "BranchLabel", "Branch:"), TAttribute<FText>::Create(TAttribute<FText>::FGetter::CreateSP(this, &SGitStatusWidget::GetBranchText)))
        ]
        + SVerticalBox::Slot().AutoHeight().Padding(4)
        [
            BuildInfoRow(NSLOCTEXT("GitWidget", "UserLabel", "User:"), TAttribute<FText>::Create(TAttribute<FText>::FGetter::CreateSP(this, &SGitStatusWidget::GetUserText)))
        ]
        + SVerticalBox::Slot().AutoHeight().Padding(4)
        [
            SNew(SButton)
            .Text(NSLOCTEXT("GitWidget", "RefreshButton", "Refresh"))
            .OnClicked_Lambda([this]() -> FReply { RefreshStatus(); return FReply::Handled(); })
        ]
    ];
    
    // 启动一个5秒的定时器来刷新状态
    if (GEngine && GEngine->GetWorldContexts().Num() > 0)
    {
        GEngine->GetWorldContexts()[0].World()->GetTimerManager().SetTimer(RefreshTimerHandle, this, &SGitStatusWidget::RefreshStatus, 5.0f, true);
    }
    RefreshStatus();
}

FText SGitStatusWidget::GetStatusText() const
{
    return CurrentStatusText;
}

FText SGitStatusWidget::GetBranchText() const
{
    return CurrentBranchText;
}

FText SGitStatusWidget::GetUserText() const
{
    return CurrentUserText;
}

TSharedRef<SWidget> SGitStatusWidget::BuildInfoRow(const FText& Label, TAttribute<FText> Value) const
{
    return SNew(SHorizontalBox)
    + SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center)
    [
        SNew(STextBlock).Text(Label)
    ]
    + SHorizontalBox::Slot().FillWidth(1.0f).Padding(8, 0, 0, 0)
    [
        SNew(STextBlock).Text(Value)
    ];
}

void SGitStatusWidget::RefreshStatus()
{
    FGitSourceControlModule& GitModule = FModuleManager::LoadModuleChecked<FGitSourceControlModule>("GitSourceControl");
    FGitSourceControlProvider& Provider = GitModule.GetProvider();
    
    if (Provider.IsGitAvailable() && Provider.IsAvailable())
    {
        CurrentBranchText = FText::FromString(Provider.GetBranchName());
        CurrentUserText = FText::FromString(FString::Printf(TEXT("%s <%s>"), *Provider.GetUserName(), *Provider.GetUserEmail()));
        CurrentStatusText = FText::FromString(Provider.GetStatusText().ToString());
    }
    else
    {
        CurrentStatusText = NSLOCTEXT("GitWidget", "NotAvailable", "Git Not Available");
        CurrentBranchText = FText::GetEmpty();
        CurrentUserText = FText::GetEmpty();
    }
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。根据 `GitSourceControl.Build.cs`，其依赖模块 `EditorFramework` 和 `UnrealEd` 是编辑器插件的常见依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-30 | `a7404169` | SourceControl: Add provider capability flag to use 'soft revert' when performing an FRevert prior to | 为“软回退”操作添加了能力标志，改进了回退逻辑 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移到新的 UE_LOGF 格式 |
| 2026-03-18 | `9271d5a5` | SourceControl: Deprecate IsAtLatestRevision() / GetNumLocalChanges() interfaces. | 弃用两个旧的查询接口，可能影响部分自动化脚本 |
| 2026-01-28 | `5f766aee` | Fixed modules that does not support portable toolchain | 修复了对可移植工具链的支持问题 |
| 2026-01-24 | `e793e61e` | Fixed more compile errors when using portable toolchain | 修复了更多可移植工具链的编译错误 |

### 维护评价

该插件是一个历史悠久（约10年）的核心编辑器功能插件。虽然被标记为实验性（IsBetaVersion=true），但它已成为 Unreal Engine 的标准组成部分，并且被广泛使用。从近期的 git 历史（2026年）可以看出，它仍然在被积极维护，主要是进行接口更新、bug 修复和编译器兼容性改进。尽管有些功能（如标签、分支管理）仍未集成到编辑器工作流中，但其核心的 Git 操作功能稳定可靠。对于使用 Git 管理项目的团队，**推荐使用**此插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/GitSourceControl)
- [官方文档]() （无）
- [测试用例]() （该插件的测试用例可能位于 `Engine/Tests/` 目录下，而非插件目录内）