# Git

> Git source control management（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | Git源代码控制 |
| 分类 | Source Control |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `GitSourceControl` (Editor) |
| 实验性 | ⚦ 是 |
| 创建时间 | 2015-01-19 |
| 年龄标签 | 🏛️ 文物（约 11 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/GitSourceControl) | |

## 用途

GitSourceControl 是 Unreal Engine 的官方 Git 版本控制插件。它将 Git 的核心功能（如提交、拉取、查看历史、解决冲突）直接集成到编辑器工作流中。该插件存在的核心目的是为了让使用 Git 进行版本控制的团队能够在编辑器内部无缝地管理资产和代码，而无需频繁切换到命令行或第三方 Git 客户端。它特别支持了 Git LFS（大文件存储），这对于管理游戏开发中的大型二进制资产（如纹理、模型、音频文件）至关重要。

## 使用场景

-   你的团队使用 Git（包括 GitHub, GitLab 或自托管服务器）作为项目的主版本控制系统。
-   你希望在编辑器中直接提交资产、查看文件状态（修改、新增、删除等图标）、查看历史记录并进行可视化差异对比（如 Blueprint 差异）。
-   你的项目包含大量二进制资产，并且使用了 Git LFS 进行管理。
-   你需要初始化一个新的 Git 仓库，并自动配置适合 Unreal 项目的 `.gitignore` 文件。

## 蓝图用法

此插件不提供任何 `BlueprintCallable` 或 `BlueprintReadWrite` 函数。它的所有功能都通过编辑器界面（如源代码控制菜单、状态图标、提交对话框）和 C++ 源代码控制 API 来提供。用户交互主要通过以下方式：
1.  **菜单操作**：在内容浏览器或文件上右键，选择“源代码控制”菜单中的操作（如“提交...”、“更新状态”、“历史记录”等）。
2.  **状态指示器**：文件图标上的状态标识（如绿色对勾、红色问号、蓝色加号等）反映其在 Git 中的状态。
3.  **设置面板**：通过“编辑 -> 项目设置 -> 源代码控制 -> Git”进行配置，如指定 Git 可执行文件路径。

## C++ 用法

此插件主要作为编辑器扩展，其功能由引擎内部的源代码控制接口（`ISourceControlProvider`, `ISourceControlOperation`）调用。开发者通常不直接调用此插件的 C++ 类，而是通过引擎提供的统一源代码控制接口（如 `ISourceControlModule::Get().GetProvider()`）来与之交互。

### 头文件引入

对于直接使用此插件源码进行修改或研究的情况，可以引入相关头文件。但在一般开发中，应使用引擎提供的公共头文件。

```cpp
// 引擎提供的源代码控制公共接口
#include "SourceControlOperations.h"
#include "ISourceControlProvider.h"

// 插件内部头文件（通常不推荐直接使用）
#include "GitSourceControlProvider.h"
#include "GitSourceControlUtils.h"
```

### 基本用法（引擎接口）

通过引擎的源代码控制接口执行操作，这些操作会被路由到当前的 Git 提供者。

```cpp
// 引用：Engine/Source/Editor/UnrealEd/Classes/Editor/EditorEngine.h
// 以及 Source/Developer/SourceControl/Public/ISourceControlModule.h

// 1. 获取源代码控制模块和当前提供者（即 GitSourceControlProvider）
ISourceControlModule& SourceControlModule = ISourceControlModule::Get();
if (SourceControlModule.IsEnabled())
{
    ISourceControlProvider& SourceControlProvider = SourceControlModule.GetProvider();

    // 2. 创建一个“更新状态”操作
    TSharedRef<FUpdateStatus, ESPMode::ThreadSafe> UpdateStatusOperation = ISourceControlOperation::Create<FUpdateStatus>();

    // 3. 指定要操作的文件
    TArray<FString> FilesToCheck;
    FilesToCheck.Add(TEXT("/Game/MyAsset.uasset"));
    FilesToCheck.Add(TEXT("/Game/Blueprints/BP_MyActor.uasset"));

    // 4. 通过提供者执行操作（这里为同步执行示例）
    ECommandResult::Type Result = SourceControlProvider.Execute(UpdateStatusOperation, FilesToCheck);
    if (Result == ECommandResult::Succeeded)
    {
        // 操作已提交给后台线程，状态稍后会通过代理更新
    }
}
```

## Demo 示例

以下是一个最简化的 C++ 代码片段，演示了如何在插件代码中查找 Git 二进制文件并检查其可用性。这通常发生在插件启动或连接时。

```cpp
// .h 文件
#pragma once
#include "CoreMinimal.h"

class FMyGitHelper
{
public:
    static bool CheckGitInstallation();
};

// .cpp 文件
#include "MyGitHelper.h"
#include "GitSourceControlUtils.h" // 来自插件
#include "GitSourceControlProvider.h" // 来自插件，用于 FGitVersion

bool FMyGitHelper::CheckGitInstallation()
{
    // 1. 查找 Git 可执行文件路径（搜索常见位置）
    FString GitPath = GitSourceControlUtils::FindGitBinaryPath();
    if (GitPath.IsEmpty())
    {
        UE_LOG(LogTemp, Error, TEXT("Git binary not found."));
        return false;
    }

    // 2. 检查 Git 可用性并获取版本信息
    FGitVersion GitVersion;
    bool bAvailable = GitSourceControlUtils::CheckGitAvailability(GitPath, &GitVersion);
    if (bAvailable)
    {
        UE_LOG(LogTemp, Log, TEXT("Git found at: %s, Version: %d.%d"), *GitPath, GitVersion.Major, GitVersion.Minor);
        // 3. 检查是否支持 Git LFS（对于大型资产管理很重要）
        GitSourceControlUtils::FindGitLfsCapabilities(GitPath, &GitVersion);
        if (GitVersion.bHasGitLfs)
        {
            UE_LOG(LogTemp, Log, TEXT("Git LFS is available."));
        }
    }
    return bAvailable;
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-30 | `a7404169` | SourceControl: Add provider capability flag to use 'soft revert' when performing an FRevert prior to | 为 Git 提供者添加了“软还原”功能标志，在执行 Revert 操作前使用。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将插件的日志宏从 UE_LOG 迁移至 UE_LOGF，提升日志处理能力。 |
| 2026-03-18 | `9271d5a5` | SourceControl: Deprecate IsAtLatestRevision() / GetNumLocalChanges() interfaces. | 弃用了 `IsAtLatestRevision()` 和 `GetNumLocalChanges()` 等旧版接口，推动使用新 API。 |
| 2026-01-28 | `5f766aee` | Fixed modules that does not support portable toolchain | 修复了对便携式工具链的兼容性问题。 |
| 2026-01-24 | `e793e61e` | Fixed more compile errors when using portable toolchain | 继续修复便携式工具链下的编译错误。 |

### 维护评价

**活跃维护**。虽然插件创建于 2015 年，但近期的提交记录（2026 年 1 月至 4 月）显示它仍在持续更新。最近的改动集中在功能增强（如“软还原”）、代码现代化（迁移日志宏）、API 清理（弃用旧接口）以及构建系统兼容性修复上。这表明该插件作为 Epic 官方支持的 Git 集成方案，仍在被积极维护和改进。考虑到其作为核心开发工具的地位，且最近有实质性更新，**推荐使用**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/GitSourceControl)
- [官方文档](无，.uplugin 中 DocsURL 为空)
- [测试用例](未在提供的信息中明确指定独立测试文件路径，通常包含在插件模块或引擎测试中)