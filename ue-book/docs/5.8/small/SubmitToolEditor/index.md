# Submit Tool Editor Override

> Sets up Submit Tool to be launched by the editor

| 属性 | 值 |
|---|---|
| 中文名 | 提交工具编辑器 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SubmitToolEditor` (Editor) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2025-01-24 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SubmitToolEditor) | |

## 用途
该插件用于覆盖 Unreal Engine 编辑器内置的源代码控制提交流程。当团队使用自定义的提交工具（例如具有额外检查、报告或 UI 的脚本或应用程序）时，此插件允许将该工具集成到编辑器的“提交”按钮操作中。它解决了在引擎内直接调用并管理外部提交工具生命周期的需求，使得团队能够强制执行特定的提交流程（如数据验证、自动添加标签等）。

## 使用场景
- 你的团队使用自定义的提交检查工具（例如 `p4 submit` 的包装脚本），希望直接从编辑器的“提交到源代码控制”对话框中触发它。
- 你需要在提交前强制执行数据验证（`bEnforceDataValidation`），并根据验证结果自动向变更列表描述中添加标签或调整提交工具的参数。
- 你希望用团队统一的、可能带有 UI 的提交工具，完全替代引擎默认的 Perforce/Git 提交界面。

## 蓝图用法
此插件主要作为编辑器模块运行，不提供公开的蓝图节点。其行为通过编辑器项目设置进行配置。

### 核心设置

| 设置 | 说明 |
|---|---|
| `SubmitToolPath` | 外部提交工具的可执行文件路径。 |
| `SubmitToolArguments` | 传递给提交工具的启动参数。 |
| `bSubmitToolEnabled` | 是否启用此提交工具覆盖。 |
| `bForceSubmitTool` | 是否强制使用此工具，即使默认提交流程可用。 |
| `bEnforceDataValidation` | 是否在提交前强制执行数据验证。 |

## C++ 用法
该插件通过设置 (`USubmitToolEditorSettings`) 和模块 (`FSubmitToolEditorModule`) 进行交互。通常不需要直接调用代码，但理解其内部机制有助于调试和自定义。

### 头文件引入
```cpp
#include "SubmitToolEditor.h"
```

### 基本用法 (配置与注册)
该插件的核心是注册委托以拦截提交流程。此过程在模块启动时自动完成，前提是设置中启用了功能。
```cpp
// 通常无需手动调用，插件内部会自动处理。
// 以下代码仅说明其工作原理：
// 1. 模块启动时，根据设置注册提交覆盖委托。
void FSubmitToolEditorModule::StartupModule()
{
    // ... 根据配置注册 OnCanSubmitToolOverrideCallback 和 OnSubmitToolOverrideCallback
}

// 2. 当编辑器尝试提交时，会调用注册的回调。
// OnCanSubmitToolOverrideCallback: 检查是否可以/应该覆盖提交。
// OnSubmitToolOverrideCallback: 实际执行提交覆盖，调用外部工具。
```

### 进阶用法 (自动验证与标签)
该插件可以根据数据验证的结果，动态地向提交参数和变更列表描述中添加内容。
```cpp
// 设置中定义触发规则：
// FSubmitToolArgumentTrigger: 根据验证消息的正则匹配，添加额外的命令行参数。
// FSubmitToolChangelistTagTrigger: 根据验证消息的正则匹配，在变更列表描述中添加标签。

// 插件内部会调用：
bool FSubmitToolEditorModule::GetChangelistValidationResult(...); // 获取验证消息
void FSubmitToolEditorModule::UpdateOptionalValidationArgs(...);  // 根据消息和规则更新参数
void FSubmitToolEditorModule::UpdateOptionalValidationTags(...);  // 根据消息和规则更新描述
```

## Demo 示例
由于此插件主要是配置驱动的，代码集成较少。以下是一个通过代码动态修改其设置的示例。

### MyGame.h
```cpp
#pragma once
#include "CoreMinimal.h"

class FSubmitToolEditorSettingsManager
{
public:
    static void ConfigureForPerforceSubmission();
};
```

### MyGame.cpp
```cpp
#include "MyGame.h"
#include "SubmitToolEditorSettings.h"
#include "ISourceControlModule.h"

void FSubmitToolEditorSettingsManager::ConfigureForPerforceSubmission()
{
    // 获取设置对象（通常通过编辑器UI修改，这里展示代码方式）
    USubmitToolEditorSettings* Settings = GetMutableDefault<USubmitToolEditorSettings>();
    if (Settings)
    {
        // 配置提交工具路径和参数
        Settings->SubmitToolPath = TEXT("C:/Tools/CustomSubmitTool.exe");
        Settings->SubmitToolArguments = TEXT("-workspace ${workspace} -changelist ${changelist}");
        Settings->bSubmitToolEnabled = true;
        Settings->bForceSubmitTool = true;
        Settings->bEnforceDataValidation = true;

        // 保存设置变更，插件会在下次提交时生效
        Settings->SaveConfig();
        
        // 通知模块重新加载设置（如果模块已运行）
        if (ISourceControlModule::Get().IsEnabled())
        {
            // 插件会自动监听设置变更并重新注册委托
        }
    }
}
```

## 模块依赖
该插件依赖于源代码控制模块以与版本控制系统交互。对于你的项目模块，如果需要使用其功能或类型，应添加依赖。

| 模块 | 用途 |
|---|---|
| `SourceControl` | 核心源代码控制接口，用于提供者、变更列表等操作。 |
| `SourceControlHelpers` | 源代码控制相关的辅助函数。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移至新的 `UE_LOGF` 宏。 |
| 2025-11-25 | `c0ee383c` | Fix new changelist created in editor not running data validation before invoking submit tool | 修复编辑器创建新变更列表时，未在调用提交工具前运行数据验证的问题。 |
| 2025-11-11 | `64968397` | Add validation message parsing to SubmitToolEditor. | 向提交工具编辑器添加验证消息解析功能。 |
| 2025-11-03 | `a757ea03` | Modify ISourceControlModule submit validation delegates. | 修改了 `ISourceControlModule` 的提交验证委托。 |
| 2025-07-10 | `9803c443` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applie | 为具有对应 .gen.cpp 文件的源文件添加了 `UE_INLINE_GENERATED_CPP_BY_NAME` 宏。 |

### 维护评价
该插件创建于2025年1月，是一个相对较新的实验性插件。从提交历史看，它仍在被**积极维护**，近期（2025年11月至2026年4月）有明确的功能增强（添加验证消息解析）和关键Bug修复（修复验证时序问题）。最新一次更新是为了遵循引擎日志宏的新规范。

**建议**：这是一个功能明确且维护活跃的插件。由于标记为实验性且默认禁用，适合有明确自定义提交工具集成需求的团队评估使用。在生产环境中启用前，建议在版本控制测试环境中进行充分验证。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SubmitToolEditor)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/Editor/SourceControl)