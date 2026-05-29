# Subversion

> Subversion source control management

| 属性 | 值 |
|---|---|
| 中文名 | SVN 版本控制 |
| 分类 | Source Control |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `SubversionSourceControl` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2014-03-14 |
| 年龄标签 | 🏛️ 文物（约 12 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/SubversionSourceControl) | |

## 用途

该插件为 Unreal Editor 提供 Apache Subversion (SVN) 版本控制系统的集成支持。作为编辑器内置的源代码管理 Provider，它允许开发者在编辑器内直接执行 SVN 的标准版本控制操作（提交、检出、同步、回滚等），无需离开编辑器切换到外部 SVN 客户端。

插件通过封装 `svn` 命令行工具（支持 XML 输出解析），实现了与 SVN 服务器的交互。它将 SVN 的工作副本状态映射到 UE 统一的 `ISourceControlState` 接口，使得编辑器的源代码管理面板能够以统一的方式展示不同 VCS 后端的文件状态。

## 使用场景

- 你的团队使用 Apache Subversion 作为版本控制系统 → 启用此插件以在编辑器内管理文件
- 你需要在编辑器内直接执行 SVN 的提交、更新、回滚等操作 → 通过编辑器源代码管理面板操作
- 你的 SVN 仓库使用标准的 trunk/branches/tags 目录结构 → 插件通过 tags 目录模拟 Perforce 的 Label 功能

## 蓝图用法

该插件**不暴露任何蓝图 API**。作为 `UncookedOnly` 类型的编辑器集成插件，它完全通过 Unreal Editor 的源代码管理框架（Source Control Panel）进行交互，不提供可供蓝图调用的函数或属性。

所有操作通过编辑器菜单 **Source Control → Connect** 进行配置和连接。

## C++ 用法

该插件通常不需要直接的 C++ 交互。它的 API 通过 UE 的 `ISourceControlProvider` 接口进行抽象，开发者一般通过 `FSourceControlModule` 或 `ISourceControlModule` 的标准接口间接使用。

### 头文件引入

如需访问 SVN Provider 的高级功能：

```cpp
#include "SubversionSourceControlModule.h"
```

### 基本用法：通过 Provider 获取连接信息

```cpp
// 获取 SVN 模块和 Provider
FSubversionSourceControlModule& SVNModule = FModuleManager::LoadModuleChecked<FSubversionSourceControlModule>("SubversionSourceControl");
FSubversionSourceControlProvider& Provider = SVNModule.GetProvider();

// 查询连接状态
if (Provider.IsAvailable())
{
    FString RepoName = Provider.GetRepositoryName();
    FString UserName = Provider.GetUserName();
    FString WorkingCopy = Provider.GetWorkingCopyRoot();
    UE_LOG(LogTemp, Log, TEXT("Connected to SVN: %s as %s, working copy at %s"), 
        *RepoName, *UserName, *WorkingCopy);
}
```

### 基本用法：配置和保存设置

```cpp
// 修改 SVN 设置
FSubversionSourceControlSettings& Settings = SVNModule.AccessSettings();
Settings.SetRepository("https://svn.example.com/repo");
Settings.SetUserName("myusername");
Settings.SetLabelsRoot("tags/");
SVNModule.SaveSettings();
```

*来源：`Source/SubversionSourceControl/Private/SubversionSourceControlModule.h`*

### 进阶用法：使用通用源代码管理接口操作文件

```cpp
// 通过标准 UE 源代码管理接口执行操作
ISourceControlProvider& SCCProvider = ISourceControlModule::Get().GetProvider();

// 获取文件状态
TArray<FString> Files = { TEXT("/Game/Maps/MyLevel.umap") };
TArray<FSourceControlStateRef> States;
SCCProvider.GetState(Files, States, EStateCacheUsage::ForceUpdate);

// 执行 CheckOut 操作
TSharedRef<FCheckOut, ESPMode::ThreadSafe> CheckOutOp = ISourceControlOperation::Create<FCheckOut>();
SCCProvider.Execute(CheckOutOp, Files);

// 执行 CheckIn（提交）操作
TSharedRef<FCheckIn, ESPMode::ThreadSafe> CheckInOp = ISourceControlOperation::Create<FCheckIn>();
CheckInOp->SetDescription(FText::FromString(TEXT("提交说明")));
SCCProvider.Execute(CheckInOp, Files);
```

## Demo 示例

以下示例展示如何在编辑器工具中检测 SVN 连接状态并获取文件状态：

```cpp
// MySVNHelper.h
#pragma once

#include "CoreMinimal.h"

class FMySVNHelper
{
public:
    /** 检查 SVN 是否已连接并可用 */
    static bool IsSVNConnected();

    /** 获取指定文件的 SVN 状态描述 */
    static FText GetFileStatusText(const FString& InFilePath);
};
```

```cpp
// MySVNHelper.cpp
#include "MySVNHelper.h"
#include "SubversionSourceControlModule.h"
#include "SubversionSourceControlProvider.h"
#include "SubversionSourceControlState.h"
#include "ISourceControlModule.h"
#include "ISourceControlProvider.h"

bool FMySVNHelper::IsSVNConnected()
{
    if (!ISourceControlModule::Get().IsEnabled())
    {
        return false;
    }
    
    ISourceControlProvider& Provider = ISourceControlModule::Get().GetProvider();
    if (Provider.GetName() != "Subversion")
    {
        return false;
    }
    
    return Provider.IsAvailable();
}

FText FMySVNHelper::GetFileStatusText(const FString& InFilePath)
{
    ISourceControlProvider& Provider = ISourceControlModule::Get().GetProvider();
    
    TArray<FString> Files = { InFilePath };
    TArray<FSourceControlStateRef> States;
    ECommandResult::Type Result = Provider.GetState(Files, States, EStateCacheUsage::Use);
    
    if (Result == ECommandResult::Succeeded && States.Num() > 0)
    {
        return States[0]->GetDisplayTooltip();
    }
    
    return FText::FromString(TEXT("Unknown"));
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

该插件依赖 UE 内置的 `SourceControl` 模块提供 `ISourceControlProvider` 接口，以及 `XmlParser` 模块解析 SVN 命令的 XML 输出，这些都是引擎标准模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-30 | `a7404169` | SourceControl: Add provider capability flag to use 'soft revert' when performing an FRevert prior to | 为源代码管理框架添加软回滚能力标志，影响所有 Provider |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移至新的 UE_LOGF 格式 |
| 2026-03-18 | `9271d5a5` | SourceControl: Deprecate IsAtLatestRevision() / GetNumLocalChanges() interfaces. | 废弃两个源代码管理接口方法 |
| 2026-02-25 | `12a309dc` | Remove as many PVS suppressions as possible that are no longer needed | 清理不再需要的静态分析抑制标记 |
| 2025-08-15 | `6678228e` | World Partition - HLOD: Added new option -ReuseParentBranchHLODs for HLOD builds | 源代码管理接口变更，影响 HLOD 构建流程 |

### 维护评价

该插件自 **2014 年创建至今已超过 12 年**，是 UE 最早期的源代码管理集成之一。

**维护状态：被动维护**。近期的所有更新都是源代码管理框架层面的通用变更（接口废弃、日志迁移、代码清理），**没有针对 SVN 功能本身的实质性更新**。插件的 SVN 命令封装逻辑、状态解析、标签模拟等核心功能长期未发生变化。

**注意事项**：
- 作为 `UncookedOnly` 模块，仅在开发环境中可用，打包构建中不包含
- 核心功能依赖外部 `svn` 命令行工具，需要系统 PATH 中可找到或在设置中指定路径
- SVN 的 Label 功能是通过 tags 目录结构模拟的，与 Perforce 的 Label 语义不完全一致
- 不支持 SVN 锁定状态的高级分支操作（`IsCheckedOutInOtherBranch` 等始终返回 false）

**推荐使用**：如果你的团队确实使用 SVN 作为版本控制系统，该插件可以正常工作。但 SVN 本身在游戏开发中已不太常见，大多数团队已迁移到 Perforce 或 Git。该插件作为"功能完整但不活跃"的状态可以长期使用，但不要期待新功能的添加。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/SubversionSourceControl)
- 官方文档：无
- 测试用例：无独立测试文件