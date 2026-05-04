# File Sandbox

> Core functionality for sandboxing files in the editor.

| 属性 | 值 |
|---|---|
| 分类 | Developer |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `FileSandboxCore` (UncookedOnly), `FileSandboxUI` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-16 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Sandbox/FileSandbox) | |

## 用途

File Sandbox 插件为 Unreal Editor 提供了一套**文件沙盒系统**。它通过拦截引擎底层的 `IPlatformFile` I/O 接口，将所有对挂载点（Mount Points，如 `/Game/`、`/Engine/`、`/MyPlugin/`）下文件的修改、新增、删除操作**重定向到一个独立的沙盒目录**中，而不触碰原始文件。

核心机制如下：

1. **I/O 重定向**：`FSandboxPlatformFile` 包装了真实的 `IPlatformFile`，所有文件写入/删除操作被拦截并重定向到沙盒目录（如 `Intermediate/Sandboxes/YourSandbox/Sandbox/Game/`）
2. **变更追踪**：通过 `Manifest.json` 文件记录所有被添加、修改、删除的文件清单及其时间戳
3. **源码控制集成**：`FSandboxedSourceControl` 拦截源码控制操作（checkout、delete、mark for add 等），在沙盒期间"吞掉"这些操作，持久化时再重新执行
4. **持久化/回滚**：用户可以随时将沙盒变更**持久化**（复制/移动到原始位置并注册源码控制变更）或**回滚**（丢弃所有变更恢复原始状态）
5. **目录监听**：`FWatchedSandboxRepository` 通过 `DirectoryWatcher` 实时监听沙盒目录变化，自动发现新增/删除的沙盒实例

**为什么存在**：在大型团队协作中，内容创作者需要一个安全的环境来实验性地修改资产，而不影响其他人或破坏已有文件。沙盒系统提供了一种"试用后再提交"的工作流，类似于 Git 的暂存区概念，但深度集成在引擎的 I/O 层。

## 使用场景

- **内容创作者实验性修改**：你在编辑器中修改了大量蓝图和材质，但还不确定是否要保留 → 用 File Sandbox 创建沙盒，所有修改被隔离，不满意直接回滚
- **代码审查前的变更整理**：你完成了一系列资产修改，需要在提交前审查所有变更 → 用 `GatherChangedFiles()` 列出所有变更，确认后再 `PersistAll()`
- **自动化测试中的文件隔离**：你在运行自动化测试，测试会修改项目文件 → 用 File Sandbox 确保测试结束后文件恢复原状
- **多用户编辑场景**：你在使用 Multi-User Editing / Concert，需要确保重命名操作创建 Redirector → 通过 `ESandboxInitFlags::ForceRedirectorsOnRenameInSourceControl` 标志强制创建
- **命令行启动沙盒**：通过命令行参数指定沙盒目录，编辑器启动时自动进入沙盒模式

## 蓝图用法

此插件的管理 API（`ISandboxManager`、`ISandboxInstance`）为纯 C++ 接口，**没有暴露 BlueprintCallable 函数**。这是因为沙盒操作发生在引擎 I/O 层，属于底层开发者工具，不适合通过蓝图节点直接调用。

不过，以下 `USTRUCT` 类型是蓝图兼容的，可以在自定义蓝图函数库中使用：

| 类型 | 说明 |
|---|---|
| `FFileSandboxCore_SandboxMetaData` | 沙盒元数据（名称、描述、标签、自定义数据） |
| `FFileSandboxCore_VersionInfo` | 版本信息（文件版本、引擎版本、自定义版本） |
| `FFileSandboxCore_InstancedStructMap` | 高级标签结构，支持按类型存储自定义数据 |

如需在蓝图中使用沙盒功能，建议通过 C++ 编写一个 `UBlueprintFunctionLibrary` 封装所需操作。

## C++ 用法

### 头文件引入

```cpp
// 最小化引入（推荐）
#include "FileSandboxCoreMinimal.h"

// 或按需引入
#include "IFileSandboxCoreModule.h"
#include "ISandboxManager.h"
#include "ISandboxInstance.h"
#include "ISandboxRepository.h"
```

### 基本用法：创建沙盒并工作

```cpp
#include "FileSandboxCoreMinimal.h"

using namespace UE::FileSandboxCore;

// 1. 获取沙盒管理器
IFileSandboxCoreModule& Module = IFileSandboxCoreModule::Get();
ISandboxManager& Manager = Module.GetSandboxManager();

// 2. 创建新沙盒
FNewSandboxArgs Args;
// Args 中设置沙盒名称、描述等元数据
FNewSandboxResult Result = Manager.CreateNewSandbox(Args);

if (ISandboxInstance* Instance = Result.GetInstance())
{
    // 此刻起，所有挂载点下的文件 I/O 被重定向到沙盒目录
    // 正常编辑资产即可，引擎会自动追踪变更
    
    // 3. 查看变更
    FGatheredFileChanges Changes = Instance->GatherChangedFiles();
    
    // 4a. 持久化所有变更（应用到真实文件）
    Instance->PersistAll();
    
    // 4b. 或者回滚所有变更
    // Instance->RevertAll();
}

// 5. 离开沙盒
Manager.LeaveSandbox();
```

*来源：基于 `Public/ISandboxManager.h` 和 `Public/ISandboxInstance.h` 的公开 API*

### 加载已有沙盒

```cpp
#include "FileSandboxCoreMinimal.h"

using namespace UE::FileSandboxCore;

IFileSandboxCoreModule& Module = IFileSandboxCoreModule::Get();
ISandboxManager& Manager = Module.GetSandboxManager();

// 按名称加载已有沙盒
FLoadSandboxByNameArgs LoadArgs;
LoadArgs.Name = TEXT("MyPreviousSandbox");

FLoadSandboxResult LoadResult = Manager.LoadNamedSandbox(LoadArgs);
if (ISandboxInstance* Instance = LoadResult.GetInstance())
{
    // 沙盒已加载，之前的变更状态被恢复
    // 已打开的资产会被热重载为沙盒版本
    
    UE_LOG(LogTemp, Log, TEXT("沙盒根目录: %s"), Instance->GetRootDirectory());
}
```

*来源：基于 `Public/ISandboxManager.h` 中 `LoadNamedSandbox` 的接口定义*

### 枚举文件变更

```cpp
using namespace UE::FileSandboxCore;

ISandboxInstance* Instance = Manager.GetActiveSandboxInstance();
if (Instance)
{
    // 方式一：收集所有变更
    FGatheredFileChanges AllChanges = Instance->GatherChangedFiles();
    
    // 方式二：逐个处理变更（更灵活，支持提前终止）
    Instance->EnumerateFileChanges(
        [](const FSandboxedFileChangeInfo& FileInfo) -> EBreakBehavior
        {
            UE_LOG(LogTemp, Log, TEXT("变更文件: %s"), *FileInfo.FilePath);
            return EBreakBehavior::Continue;
        },
        EFileEnumerationFlags::All
    );
    
    // 检查是否有任何变更
    if (Instance->HasFileChanges())
    {
        UE_LOG(LogTemp, Log, TEXT("有未保存的沙盒变更"));
    }
}
```

*来源：基于 `Public/ISandboxInstance.h` 中 `EnumerateFileChanges` 和 `GatherChangedFiles` 的接口定义*

### 高级持久化控制

```cpp
using namespace UE::FileSandboxCore;

ISandboxInstance* Instance = Manager.GetActiveSandboxInstance();
if (Instance)
{
    FPersistArgs PersistArgs;
    // 配置持久化参数...
    
    FPersistResult PersistResult = Instance->PersistSandbox(PersistArgs);
    // 检查 PersistResult 了解每个文件的持久化状态
}
```

*来源：基于 `Public/ISandboxInstance.h` 中 `PersistSandbox` 的接口定义*

### 使用沙盒仓库列出可用沙盒

```cpp
using namespace UE::FileSandboxCore;

IFileSandboxCoreModule& Module = IFileSandboxCoreModule::Get();
ISandboxRepository& Repository = Module.GetDefaultSandboxRepository();

// 列出所有已知沙盒
Repository.ForEachSandbox(
    [](const FString& RootPath, const FSandboxMetaInfo& MetaData) -> EBreakBehavior
    {
        UE_LOG(LogTemp, Log, TEXT("发现沙盒: %s (路径: %s)"), 
            *MetaData.GetName(), *RootPath);
        return EBreakBehavior::Continue;
    }
);

// 监听沙盒变化
Repository.OnSandboxesChanged().AddLambda(
    [](const FRepositoryChangedEvent& Event)
    {
        UE_LOG(LogTemp, Log, TEXT("沙盒列表发生变化"));
    }
);

// 监听元数据变化
Repository.OnSandboxMetaDataChanged().AddLambda(
    [](const FString& RootPath)
    {
        UE_LOG(LogTemp, Log, TEXT("沙盒元数据变化: %s"), *RootPath);
    }
);
```

*来源：基于 `Public/ISandboxRepository.h` 的公开接口*

### 监听沙盒生命周期事件

```cpp
using namespace UE::FileSandboxCore;

ISandboxManager& Manager = IFileSandboxCoreModule::Get().GetSandboxManager();

// 沙盒启动后
Manager.OnPostSandboxStartup().AddLambda(
    [](ISandboxInstance& Instance)
    {
        UE_LOG(LogTemp, Log, TEXT("沙盒已启动: %s"), Instance.GetRootDirectory());
    }
);

// 沙盒关闭前
Manager.OnPreSandboxShutdown().AddLambda(
    [](ISandboxInstance& Instance)
    {
        UE_LOG(LogTemp, Log, TEXT("沙盒即将关闭"));
    }
);

// 沙盒关闭后
Manager.OnPostSandboxShutdown().AddLambda(
    []()
    {
        UE_LOG(LogTemp, Log, TEXT("沙盒已关闭"));
    }
);
```

*来源：基于 `Public/ISandboxManager.h` 中事件委托的定义*

### 进阶用法：带源码控制的持久化与选择性回滚

```cpp
using namespace UE::FileSandboxCore;

ISandboxInstance* Instance = Manager.GetActiveSandboxInstance();
if (Instance)
{
    // 获取沙盒元数据
    const FFileSandboxCore_SandboxMetaData& Meta = Instance->GetInitialMetaData();
    UE_LOG(LogTemp, Log, TEXT("沙盒名称: %s"), *Meta.Name);
    
    // 获取特定文件的沙盒时间戳
    TOptional<FDateTime> Timestamp = Instance->GetSandboxedFileTimestamp(
        TEXT("/Game/Levels/MyLevel.umap")
    );
    if (Timestamp.IsSet())
    {
        UE_LOG(LogTemp, Log, TEXT("文件最后修改时间: %s"), 
            *Timestamp.GetValue().ToString());
    }
    
    // 检查被删除的包是否仍存在于非沙盒路径
    bool bExists = Instance->DeletedPackageExistsInNonSandbox(
        TEXT("/Game/Obsolete/OldAsset.uasset")
    );
    
    // 选择性回滚指定文件（实验性功能）
    TArray<FString> FilesToRevert = {
        TEXT("/Game/Levels/MyLevel.umap"),
        TEXT("/Game/Blueprints/MyBP.uasset")
    };
    FRevertResult RevertResult = Instance->RevertSpecified(FilesToRevert);
}
```

*来源：基于 `Public/ISandboxInstance.h` 中多个接口方法*

## Demo 示例

以下是一个完整的最小示例，展示如何在编辑器工具中使用 File Sandbox 系统：

### MySandboxTool.h

```cpp
// MySandboxTool.h
#pragma once

#include "CoreMinimal.h"

namespace UE::FileSandboxCore
{
    class ISandboxInstance;
    class ISandboxManager;
}

/**
 * 简单的沙盒工具，演示 File Sandbox 的基本工作流。
 * 在编辑器工具或命令中调用这些静态方法。
 */
class FMySandboxTool
{
public:
    /** 创建并进入一个名为 "MyTestSandbox" 的沙盒 */
    static bool EnterSandbox(const FString& SandboxName);
    
    /** 列出当前沙盒中的所有文件变更 */
    static void LogAllChanges();
    
    /** 持久化所有变更并离开沙盒 */
    static bool PersistAndLeave();
    
    /** 回滚所有变更并离开沙盒 */
    static bool RevertAndLeave();
    
    /** 当前是否在沙盒中 */
    static bool IsInSandbox();
};
```

### MySandboxTool.cpp

```cpp
// MySandboxTool.cpp
#include "MySandboxTool.h"
#include "FileSandboxCoreMinimal.h"

DEFINE_LOG_CATEGORY_STATIC(LogMySandboxTool, Log, All);

using namespace UE::FileSandboxCore;

bool FMySandboxTool::EnterSandbox(const FString& SandboxName)
{
    if (!IFileSandboxCoreModule::IsAvailable())
    {
        UE_LOG(LogMySandboxTool, Error, TEXT("FileSandboxCore 模块未加载"));
        return false;
    }
    
    ISandboxManager& Manager = IFileSandboxCoreModule::Get().GetSandboxManager();
    
    // 如果已在沙盒中，先离开
    if (Manager.GetActiveSandboxInstance())
    {
        UE_LOG(LogMySandboxTool, Warning, TEXT("已在沙盒中，先离开当前沙盒"));
        Manager.LeaveSandbox();
    }
    
    FNewSandboxArgs Args;
    // 设置沙盒元数据
    Args.MetaData = FFileSandboxCore_SandboxMetaData(
        SandboxName,
        TEXT("通过 FMySandboxTool 创建的测试沙盒")
    );
    
    FNewSandboxResult Result = Manager.CreateNewSandbox(Args);
    if (ISandboxInstance* Instance = Result.GetInstance())
    {
        UE_LOG(LogMySandboxTool, Log, 
            TEXT("成功进入沙盒 '%s'，根目录: %s"),
            *SandboxName, Instance->GetRootDirectory());
        return true;
    }
    
    UE_LOG(LogMySandboxTool, Error, TEXT("创建沙盒 '%s' 失败"), *SandboxName);
    return false;
}

void FMySandboxTool::LogAllChanges()
{
    ISandboxManager& Manager = IFileSandboxCoreModule::Get().GetSandboxManager();
    ISandboxInstance* Instance = Manager.GetActiveSandboxInstance();
    
    if (!Instance)
    {
        UE_LOG(LogMySandboxTool, Warning, TEXT("当前不在沙盒中"));
        return;
    }
    
    int32 ChangeCount = 0;
    Instance->EnumerateFileChanges(
        [&ChangeCount](const FSandboxedFileChangeInfo& FileInfo) -> EBreakBehavior
        {
            ChangeCount++;
            UE_LOG(LogMySandboxTool, Log, TEXT("  [%d] %s"),
                static_cast<int32>(FileInfo.Action), *FileInfo.FilePath);
            return EBreakBehavior::Continue;
        }
    );
    
    UE_LOG(LogMySandboxTool, Log, TEXT("共 %d 个文件变更"), ChangeCount);
}

bool FMySandboxTool::PersistAndLeave()
{
    ISandboxManager& Manager = IFileSandboxCoreModule::Get().GetSandboxManager();
    ISandboxInstance* Instance = Manager.GetActiveSandboxInstance();
    
    if (!Instance)
    {
        UE_LOG(LogMySandboxTool, Warning, TEXT("当前不在沙盒中"));
        return false;
    }
    
    // 持久化所有变更
    bool bPersisted = Instance->PersistAll();
    if (bPersisted)
    {
        UE_LOG(LogMySandboxTool, Log, TEXT("所有变更已持久化"));
    }
    else
    {
        UE_LOG(LogMySandboxTool, Warning, TEXT("部分文件持久化失败"));
    }
    
    // 离开沙盒
    FLeaveSandboxResult LeaveResult = Manager.LeaveSandbox();
    return bPersisted;
}

bool FMySandboxTool::RevertAndLeave()
{
    ISandboxManager& Manager = IFileSandboxCoreModule::Get().GetSandboxManager();
    ISandboxInstance* Instance = Manager.GetActiveSandboxInstance();
    
    if (!Instance)
    {
        UE_LOG(LogMySandboxTool, Warning, TEXT("当前不在沙盒中"));
        return false;
    }
    
    // 回滚所有变更
    FRevertResult RevertResult = Instance->RevertAll();
    UE_LOG(LogMySandboxTool, Log, TEXT("所有变更已回滚"));
    
    // 离开沙盒
    Manager.LeaveSandbox();
    return true;
}

bool FMySandboxTool::IsInSandbox()
{
    if (!IFileSandboxCoreModule::IsAvailable())
    {
        return false;
    }
    
    ISandboxManager& Manager = IFileSandboxCoreModule::Get().GetSandboxManager();
    return Manager.GetActiveSandboxInstance() != nullptr;
}
```

## 模块依赖

从 `FileSandboxCore.Build.cs` 提取的依赖关系：

| 模块 | 用途 |
|---|---|
| `DirectoryWatcher` | 监听沙盒目录的文件变化，实现 `FWatchedSandboxRepository` 的实时发现和元数据更新功能 |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

> **注意**：`FileSandboxUI` 模块的 Build.cs 未提供，其依赖关系未知。该模块为 Editor 类型，提供沙盒管理的编辑器 UI 界面。

## 维护状态

### 近期更新

> ⚠️ 无法获取 git log 数据（需要在主仓库 `/mnt/x/UnrealEngine` 执行 git 命令）。以下基于代码特征分析。

### 维护评价

**状态：早期开发中（Beta）**

综合评估如下：

| 指标 | 评估 |
|---|---|
| 版本号 | 0.1（极早期） |
| Beta 标记 | `IsBetaVersion=true` |
| 隐藏状态 | `Hidden=true`（不在插件浏览器中显示） |
| 默认启用 | `EnabledByDefault=false`（需手动启用） |
| 实验性功能 | `RevertSpecified` 标记为 `UE_EXPERIMENTAL(5.8)`，存在已知问题 UE-368478 |
| TODO 标记 | 代码中有 `TODO UE-350242`（版本兼容性检查） |
| 架构成熟度 | 架构设计完善（Manager/Instance/Repository 分层清晰，源码控制代理模式成熟） |

**综合评价**：

- 🟡 **不建议在生产环境使用**：当前为 Beta 版本，API 可能发生破坏性变更
- 🟢 **架构设计良好**：代码结构清晰，关注点分离合理（I/O 重定向、变更追踪、源码控制集成各自独立）
- 🟡 **部分功能实验性**：单文件回滚功能尚未完全实现
- 🟢 **适合内部开发/测试**：作为 Epic 内部开发工具，质量有保障，但公开 API 尚未稳定
- 📌 **建议关注**：如果需要文件沙盒功能，建议持续跟踪此插件的演进，待其脱离 Beta 后再正式采用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Sandbox/FileSandbox)
- 官方文档：无（`.uplugin` 中 `DocsURL` 为空）
- 测试用例：未在提供的源码中发现测试文件，可能位于 `Engine/Tests/` 目录下