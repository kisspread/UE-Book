# Perforce

> Perforce source control management（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | Perforce源码管理 |
| 分类 | Source Control |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `PerforceSourceControl` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2014-03-14 |
| 年龄标签 | 🏛️ 文物（约 12 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/PerforceSourceControl) | |

## 用途

PerforceSourceControl 插件是 Unreal Engine 内置的 Perforce (P4) 版本控制系统集成插件。它实现了 `ISourceControlProvider` 接口，为编辑器提供了完整的 Perforce 源代码管理功能。这个插件的主要目的是让团队能够直接在 Unreal Editor 中执行所有常见的版本控制操作，无需切换到外部的 P4V 客户端，从而提升开发工作流的效率。

它解决了以下问题：
1. **无缝集成**：将 Perforce 操作（签出、提交、同步等）直接嵌入到编辑器的内容浏览器、资产右键菜单和状态栏中。
2. **状态管理**：实时跟踪资产在 Perforce 服务器上的状态（如是否被他人签出、是否有待处理的更改列表等）。
3. **异步执行**：通过多线程执行 Perforce 命令，避免阻塞编辑器的主游戏线程。
4. **配置管理**：提供设置界面来配置服务器连接信息（端口、用户名、工作空间等），并支持从 P4CONFIG 文件自动导入。

## 使用场景

- 你的团队使用 Perforce 作为项目的版本控制系统。
- 你需要在 Unreal Editor 内部签出 (Check Out)、提交 (Check In)、同步 (Sync)、撤消 (Revert) 和查看差异 (Diff) 资产。
- 你需要管理 Perforce 的更改列表 (Changelist)，例如创建、编辑、删除或搁置 (Shelve) 文件。
- 你需要将当前的工作空间与 Perforce 服务器上的特定标签 (Label) 同步。
- 你需要通过编辑器设置面板来配置连接到 Perforce 服务器所需的凭据。

## 蓝图用法

此插件主要为编辑器扩展服务，其核心功能通过编辑器 UI（如内容浏览器）暴露，而非蓝图节点。没有提供专门的 `BlueprintCallable` 函数供蓝图设计师直接调用。

## C++ 用法

PerforceSourceControl 插件主要通过 Unreal Engine 的源代码控制模块 (`ISourceControlModule`) 进行交互。以下是典型的 C++ 用法模式：

### 头文件引入

```cpp
#include "ISourceControlModule.h"
#include "ISourceControlProvider.h"
```

### 基本用法

在 C++ 中，你通常通过 `ISourceControlModule` 的单例来访问和操作源代码控制提供者（即 Perforce）。以下是如何查询文件状态的示例：

```cpp
// 来自 Engine/Source/Editor/UnrealEd/Private/EditorFileUtils.cpp 中的典型用法
void CheckFileStatus(const TArray<FString>& FilesToCheck)
{
    // 获取源代码控制提供者
    ISourceControlProvider& SourceControlProvider = ISourceControlModule::Get().GetProvider();

    // 检查提供者是否可用
    if (SourceControlProvider.IsEnabled())
    {
        TArray<FSourceControlStateRef> OutStates;
        // 异步查询文件状态
        ECommandResult::Type Result = SourceControlProvider.GetState(FilesToCheck, OutStates, EStateCacheUsage::ForceUpdate);

        if (Result == ECommandResult::Type::Succeeded)
        {
            // 处理状态
            for (const FSourceControlStateRef& State : OutStates)
            {
                UE_LOG(LogTemp, Log, TEXT("File %s: IsCheckedOut=%s"), *State->GetFilename(), State->IsCheckedOut() ? TEXT("True") : TEXT("False"));
            }
        }
    }
}
```

### 进阶用法

执行一个自定义的源代码控制操作，例如将文件添加到新的更改列表中。这通常在编辑器功能扩展中完成。

```cpp
// 来自 Engine/Source/Editor/UnrealEd/Private/AssetEditorManager.cpp 的简化示例
void MoveFilesToNewChangelist(const TArray<FString>& Files, const FText& Description)
{
    ISourceControlProvider& SCCProvider = ISourceControlModule::Get().GetProvider();

    // 创建一个“新更改列表”操作
    FSourceControlOperationRef Operation = ISourceControlOperation::Create<FNewChangelist>();
    // 注意：FNewChangelist 是一个特定于操作的类，这里仅示意

    // 执行操作
    FSourceControlOperationComplete CompletionDelegate = FSourceControlOperationComplete::CreateLambda(
        [](const FSourceControlOperationRef& InOperation, ECommandResult::Type InResult)
        {
            if (InResult == ECommandResult::Type::Succeeded)
            {
                UE_LOG(LogTemp, Log, TEXT("Files moved to new changelist successfully."));
            }
        }
    );

    // 将操作异步地加入队列
    SCCProvider.Execute(Operation, nullptr, Files, EConcurrency::Asynchronous, CompletionDelegate);
}
```

## Demo 示例

以下是一个最小的示例，展示如何在编辑器工具中获取并显示一个文件的当前签出状态。这是一个典型的编辑器扩展场景。

### MyPerforceStatusChecker.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "ISourceControlState.h"

class FMyPerforceStatusChecker
{
public:
    void CheckStatus(const FString& AssetPath);

private:
    void OnGetStateComplete(const FSourceControlOperationRef& InOperation, ECommandResult::Type InResult);
};
```

### MyPerforceStatusChecker.cpp

```cpp
#include "MyPerforceStatusChecker.h"
#include "ISourceControlModule.h"
#include "ISourceControlProvider.h"

void FMyPerforceStatusChecker::CheckStatus(const FString& AssetPath)
{
    ISourceControlProvider& SCCProvider = ISourceControlModule::Get().GetProvider();
    if (!SCCProvider.IsEnabled())
    {
        UE_LOG(LogTemp, Warning, TEXT("Source control is not enabled."));
        return;
    }

    TArray<FString> Files = { AssetPath };
    FSourceControlOperationComplete CompletionDelegate = 
        FSourceControlOperationComplete::CreateRaw(this, &FMyPerforceStatusChecker::OnGetStateComplete);

    SCCProvider.GetState(Files, EStateCacheUsage::Use, CompletionDelegate);
}

void FMyPerforceStatusChecker::OnGetStateComplete(const FSourceControlOperationRef& InOperation, ECommandResult::Type InResult)
{
    if (InResult != ECommandResult::Type::Succeeded)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to get source control state."));
        return;
    }

    // 此处简化，实际需从 InOperation 提取状态
    UE_LOG(LogTemp, Log, TEXT("Source control state query completed."));
}
```

## 模块依赖

PerforceSourceControl 插件本身不对外暴露其他模块依赖。然而，要使用其功能，你的模块需要链接到 `SourceControl` 模块，这是所有源代码控制提供者的抽象接口。

| 模块 | 用途 |
|---|---|
| `SourceControl` | 提供 `ISourceControlModule`, `ISourceControlProvider` 等核心接口，是与任何源代码控制提供者交互的必需依赖。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `6b27acb9` | #jira UE-376945 | 修复特定 JIRA 问题（UE-376945）。 |
| 2026-05-01 | `8de2088d` | Refactoring of column data for TEDS Source code control widgets | 重构 TEDS 源代码控制部件的列数据。 |
| 2026-04-30 | `a7404169` | SourceControl: Add provider capability flag to use 'soft revert' when performing an FRevert prior to | 为 FRevert 操作添加“软撤回”能力标志。 |
| 2026-04-27 | `554cdee6` | Fixed "Another row has already been registered under key" TEDS ensure from PerforceWorkersTedsUtilit | 修复了 Perforce 工作节点中一个 TEDS 重复注册行键的确保错误。 |
| 2026-04-23 | `e8f80687` | Moving SccStatusUpdateTags queries out of PerforceSourceControlProvider to RevisionControlProcessors | 将 SCC 状态更新标签的查询从 Perforce 提供者移至修订版控制处理器。 |

### 维护评价

- **创建时间**：2014年，是 UE4/UE5 早期就存在的核心插件之一。
- **维护状态**：**活跃维护中**。尽管创建时间很早，但从最近的提交记录（2026年）来看，该插件仍在持续更新和改进。近期的提交涵盖了功能重构（如 TEDS 部件数据）、新特性（如软撤回标志）、Bug 修复（如 JIRA 问题）以及架构优化（如将查询逻辑移出主提供者类）。
- **推荐使用**：**强烈推荐**。作为 Epic Games 官方维护的 Perforce 集成，它稳定、功能全面，并且会随着引擎版本更新。对于使用 Perforce 的团队来说，它是不可或缺的核心工具。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/PerforceSourceControl)
- [官方文档]() (此插件无专门文档，其用法在源代码控制相关通用文档中涵盖)