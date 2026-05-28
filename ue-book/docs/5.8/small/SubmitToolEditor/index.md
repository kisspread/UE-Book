# Submit Tool Editor Override

> Sets up Submit Tool to be launched by the editor

| 属性 | 值 |
|---|---|
| 中文名 | 提交工具编辑器 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SubmitToolEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-01-24 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SubmitToolEditor) | |

## 用途

SubmitToolEditor 用于**覆盖编辑器内置的源代码控制提交行为**，将默认的源码管理提交操作替换为调用外部自定义提交工具（Submit Tool）。

默认情况下，UE 编辑器使用内置的源码管理集成（如 Perforce、Git 等）来提交变更。此插件允许你在提交流程中插入一个外部程序，实现自定义的提交校验、标签管理和工作流控制。具体功能包括：

- **拦截提交操作**：通过注册代理（Delegate）拦截编辑器的提交流程，替换为外部工具调用
- **Perforce 深度集成**：识别 Perforce 提供者，自动提取端口、用户、客户端及工作区路径作为外部工具参数
- **变更列表管理**：支持创建和编辑变更列表描述（Changelist Description）
- **数据验证集成**：在调用外部提交工具前执行数据验证，并将验证结果以参数或标签形式传递给外部工具
- **正则触发器**：基于验证消息的正则匹配，自动添加变更列表标签或附加命令行参数

## 使用场景

- 你的团队使用自定义提交工具（如内部代码审查系统）替代标准的源码管理提交 → 用 SubmitToolEditor 将编辑器提交按钮指向你的工具
- 你需要在每次提交前强制执行数据验证（如资产命名规范、蓝图校验）→ 启用 `bEnforceDataValidation` 配置
- 你想根据验证结果自动给变更列表添加标签（如 `#needs-review`、`#auto-validated`）→ 配置 `ChangelistTagTriggers`
- 你需要在不同验证场景下向外部工具传递不同参数 → 配置 `OptionalArgumentTriggers`

## 蓝图用法

此插件不暴露任何蓝图 API。所有功能通过 C++ 模块注册和编辑器设置面板（Project Settings → Submit Tool Settings）控制。

## C++ 用法

### 头文件引入

```cpp
#include "SubmitToolEditor/Private/SubmitToolEditor.h"
```

### 基本用法

获取模块实例并注册提交覆盖委托：

```cpp
// 获取模块实例
FSubmitToolEditorModule& SubmitToolModule = FSubmitToolEditorModule::Get();

// 从设置对象注册提交覆盖委托
const USubmitToolEditorSettings* Settings = GetDefault<USubmitToolEditorSettings>();
SubmitToolModule.RegisterSubmitOverrideDelegate(Settings);

// 取消注册
SubmitToolModule.UnregisterSubmitOverrideDelegate();
```

### 进阶用法

插件内部通过回调链实现提交覆盖。核心流程如下：

```cpp
// 1. 检查是否可以使用提交工具覆盖（由编辑器源码管理模块回调）
FSubmitOverrideReply FSubmitToolEditorModule::OnCanSubmitToolOverrideCallback(
    const SSubmitOverrideParameters& InParameters, FText* ErrorMessageOut);

// 2. 执行提交工具覆盖（由编辑器源码管理模块回调）
FSubmitOverrideReply FSubmitToolEditorModule::OnSubmitToolOverrideCallback(
    const SSubmitOverrideParameters& InParameters);

// 3. 实际调用外部提交工具（三个重载）
// 重载1: 带文件列表
FSubmitOverrideReply InvokeSubmitTool(
    ISourceControlProvider& InProvider,
    const FString& InPath,        // 外部工具路径
    const FString& InArgs,        // 命令行参数
    const FString& InDescription, // 变更列表描述
    const TArray<FString>& InFiles);

// 重载2: 带标识符（已存在的变更列表）
FSubmitOverrideReply InvokeSubmitTool(
    ISourceControlProvider& InProvider,
    const FString& InPath,
    const FString& InArgs,
    const FString& InDescription,
    const FString& InIdentifier);  // 变更列表标识符

// 重载3: 仅标识符
FSubmitOverrideReply InvokeSubmitTool(
    ISourceControlProvider& InProvider,
    const FString& InPath,
    const FString& InArgs,
    const FString& InIdentifier);
```

## 编辑器设置

插件通过 `USubmitToolEditorSettings`（`UDeveloperSettings` 子类）提供配置项，位于 **Project Settings → Submit Tool Settings**：

| 设置项 | 类型 | 说明 |
|---|---|---|
| `SubmitToolPath` | `FString` | 外部提交工具的可执行文件路径 |
| `SubmitToolArguments` | `FString` | 传递给外部工具的命令行参数模板 |
| `bSubmitToolEnabled` | `bool` | 是否启用提交工具覆盖 |
| `bForceSubmitTool` | `bool` | 是否强制使用提交工具（默认 true） |
| `bEnforceDataValidation` | `bool` | 是否在提交前执行数据验证 |
| `ChangelistTagTriggers` | `TArray<FSubmitToolChangelistTagTrigger>` | 基于验证消息正则匹配自动添加变更列表标签 |
| `OptionalArgumentTriggers` | `TArray<FSubmitToolArgumentTrigger>` | 基于验证消息正则匹配自动附加命令行参数 |

### 正则触发器结构

```cpp
// 变更列表标签触发器
struct FSubmitToolChangelistTagTrigger
{
    FString RegExMessage;   // 匹配验证消息的正则表达式
    FString SubmitToolTag;  // 匹配成功时添加的标签
};

// 参数触发器
struct FSubmitToolArgumentTrigger
{
    FString RegExMessage;       // 匹配验证消息的正则表达式
    FString SubmitToolArgument; // 匹配成功时附加的命令行参数
};
```

## Demo 示例

### 最小使用示例

以下展示如何在自定义编辑器模块中集成 SubmitToolEditor：

```cpp
// MyEditorModule.h
#pragma once

#include "Modules/ModuleManager.h"

class FMyEditorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

```cpp
// MyEditorModule.cpp
#include "MyEditorModule.h"
#include "SubmitToolEditor/Private/SubmitToolEditor.h"
#include "SubmitToolEditor/Private/SubmitToolEditorSettings.h"

void FMyEditorModule::StartupModule()
{
    // 确保 SubmitToolEditor 模块已加载
    if (FModuleManager::Get().IsModuleLoaded("SubmitToolEditor"))
    {
        FSubmitToolEditorModule& SubmitModule = FSubmitToolEditorModule::Get();
        const USubmitToolEditorSettings* Settings = GetDefault<USubmitToolEditorSettings>();

        if (Settings && Settings->bSubmitToolEnabled)
        {
            SubmitModule.RegisterSubmitOverrideDelegate(Settings);
        }
    }
}

void FMyEditorModule::ShutdownModule()
{
    if (FModuleManager::Get().IsModuleLoaded("SubmitToolEditor"))
    {
        FSubmitToolEditorModule::Get().UnregisterSubmitOverrideDelegate();
    }
}

IMPLEMENT_MODULE(FMyEditorModule, MyEditor)
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `SourceControl` | 源码管理接口，提供 `ISourceControlProvider` 等核心类型 |
| `DeveloperSettings` | 设置基类 `UDeveloperSettings`（常见依赖，略） |

无特殊依赖（仅标准 Core/Engine/Slate 等及 SourceControl 模块）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移到新格式 UE_LOGF |
| 2025-11-25 | `c0ee383c` | Fix new changelist created in editor not running data validation before invoking submit tool | 修复编辑器新建变更列表时未先执行数据验证的 bug |
| 2025-11-11 | `64968397` | Add validation message parsing to SubmitToolEditor. | 新增验证消息解析功能，支持正则触发器 |
| 2025-11-03 | `a757ea03` | Modify ISourceControlModule submit validation delegates. | 修改源码管理模块的提交验证代理接口 |
| 2025-07-10 | `9803c443` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. | 添加内联生成宏优化编译 |

### 维护评价

SubmitToolEditor 创建于 2025 年 1 月，是一个相对较新的实验性插件。从提交记录来看：

- **活跃维护**：最近 6 个月内有多次实质性功能更新（验证消息解析、数据验证修复、代理接口修改）
- **持续改进**：功能在逐步完善，从最初的简单提交覆盖扩展到支持验证集成和正则触发器
- **实验性标记**：`IsExperimentalVersion=true` 且 `EnabledByDefault=false`，表明 Epic 仍在评估此功能的稳定性
- **无已知废弃标记**：没有 deprecated 相关的提交记录

**推荐使用**：如果你的团队需要自定义提交工作流，可以尝试启用此插件。但需注意其**实验性状态**，API 和行为可能在未来版本中发生变化。建议在正式项目中使用前进行充分测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SubmitToolEditor)
- [设置文件](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Experimental/SubmitToolEditor/Source/SubmitToolEditor/Private/SubmitToolEditorSettings.h)
- [模块主文件](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Experimental/SubmitToolEditor/Source/SubmitToolEditor/Private/SubmitToolEditor.h)