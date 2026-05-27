# Submit Tool Editor Override

> Sets up Submit Tool to be launched by the editor

| 属性 | 值 |
|---|---|
| 中文名 | 提交工具覆盖 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SubmitToolEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-01-24 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SubmitToolEditor) | |

## 用途

此插件为 Unreal Engine 编辑器提供了一种覆盖默认源代码控制（Source Control）提交流程的机制。它的核心功能是拦截编辑器内置的“提交”（Submit）操作，并将其重定向到一个用户或团队自定义的外部“提交工具”（Submit Tool）程序。这解决了需要强制使用统一提交流程、集成外部提交管理系统，或在提交前执行自定义验证脚本的团队的需求。通过此插件，可以确保所有编辑器提交都经过标准化的工具处理。

## 使用场景

- 你的团队维护着一个自定义的提交工具，用于执行代码审查、关联任务追踪、或运行自动化检查。
- 你需要强制所有开发者在提交前运行一个特定的本地验证脚本。
- 你想将 UE 编辑器的提交功能与 Perforce 以外的版本控制系统或提交管理系统（如 Gerrit， GitLab MR）集成。
- 你希望在提交描述（Changelist Description）中自动添加或修改特定标签，以标记验证状态。

## 蓝图用法

此插件的功能主要通过编辑器设置（Project Settings）进行配置，而非通过蓝图节点直接调用。其主要可配置项如下：

### 核心设置（通过编辑器设置面板访问）

| 设置项 | 说明 | 类型 |
|---|---|---|
| `Submit Tool Path` | 指向外部提交工具可执行文件的完整路径。 | `FString` |
| `Submit Tool Arguments` | 调用提交工具时传递的命令行参数字符串。 | `FString` |
| `bSubmitToolEnabled` | 全局开关，是否启用外部提交工具覆盖。 | `bool` |
| `bForceSubmitTool` | 是否强制使用外部工具，即使用户可能想使用默认提交。 | `bool` |
| `bEnforceDataValidation` | 是否在调用提交工具前强制执行编辑器数据验证。 | `bool` |
| `Changelist Tag Triggers` | 数组，定义基于验证消息正则表达式向变更列表描述添加标签的规则。 | `TArray<FSubmitToolChangelistTagTrigger>` |
| `Optional Argument Triggers` | 数组，定义基于验证消息正则表达式向提交工具命令行追加参数的规则。 | `TArray<FSubmitToolArgumentTrigger>` |

**配置路径**：编辑器 -> 项目设置 -> 游戏 -> Submit Tool Settings

## C++ 用法

### 头文件引入

```cpp
#include "SubmitToolEditor.h"
#include "SubmitToolEditorSettings.h"
```

### 基本用法

1.  **获取设置实例**：要读取或修改提交工具的设置，需要获取 `USubmitToolEditorSettings` 的实例。
    ```cpp
    // 获取 Submit Tool 的设置对象
    const USubmitToolEditorSettings* Settings = GetDefault<USubmitToolEditorSettings>();
    if (Settings)
    {
        UE_LOG(LogSubmitToolEditor, Log, TEXT("Submit Tool Path: %s"), *Settings->SubmitToolPath);
        UE_LOG(LogSubmitToolEditor, Log, TEXT("Submit Tool Enabled: %s"), Settings->bSubmitToolEnabled ? TEXT("true") : TEXT("false"));
    }
    ```
    *来源: 推断自 `USubmitToolEditorSettings` 的定义。*

2.  **访问模块功能**：`FSubmitToolEditorModule` 提供了静态获取方法，但其主要公共接口是生命周期管理。
    ```cpp
    // 确保 SubmitToolEditor 模块已加载并获取其实例
    FSubmitToolEditorModule& SubmitToolModule = FSubmitToolEditorModule::Get();
    ```
    *来源: `FSubmitToolEditorModule::Get()` 方法。*

### 进阶用法

插件的核心逻辑在模块的私有方法中，如 `RegisterSubmitOverrideDelegate` 和 `InvokeSubmitTool`。这些方法在插件启动时自动注册到编辑器的源代码控制模块，拦截提交事件。开发者通常不需要直接调用这些方法，而是通过配置 `USubmitToolEditorSettings` 来控制其行为。`ChangelistTagTriggers` 和 `OptionalArgumentTriggers` 允许进行复杂的动态参数配置。

## Demo 示例

这是一个配置并获取提交工具设置的最小示例。

**MyClass.h**
```cpp
// MyClass.h
#pragma once
#include "CoreMinimal.h"

class FMySubmitToolConfig
{
public:
    void CheckAndPrintSubmitToolConfig();
};
```

**MyClass.cpp**
```cpp
// MyClass.cpp
#include "MyClass.h"
#include "SubmitToolEditorSettings.h"
#include "Modules/ModuleManager.h"

void FMySubmitToolConfig::CheckAndPrintSubmitToolConfig()
{
    // 确保模块被加载（虽然设置系统独立，但调用模块API前通常需要）
    FModuleManager::Get().LoadModuleChecked<FSubmitToolEditorModule>("SubmitToolEditor");

    // 获取设置默认对象
    const USubmitToolEditorSettings* Settings = GetDefault<USubmitToolEditorSettings>();
    if (Settings)
    {
        UE_LOG(LogTemp, Log, TEXT("--- Submit Tool Configuration ---"));
        UE_LOG(LogTemp, Log, TEXT("Enabled: %s"), Settings->bSubmitToolEnabled ? TEXT("Yes") : TEXT("No"));
        UE_LOG(LogTemp, Log, TEXT("Tool Path: %s"), *Settings->SubmitToolPath);
        UE_LOG(LogTemp, Log, TEXT("Force Submit: %s"), Settings->bForceSubmitTool ? TEXT("Yes") : TEXT("No"));
        UE_LOG(LogTemp, Log, TEXT("Enforce Validation: %s"), Settings->bEnforceDataValidation ? TEXT("Yes") : TEXT("No"));
        UE_LOG(LogTemp, Log, TEXT("Number of Tag Triggers: %d"), Settings->ChangelistTagTriggers.Num());
    }
}
```

## 模块依赖

根据插件类型（Editor）和功能（集成源代码控制、启动外部进程）推断，你的模块可能需要依赖：

| 模块 | 用途 |
|---|---|
| `SourceControl` | 与 Unreal 的源代码控制系统交互，注册提交覆盖代理 |
| `ToolMenus` | （推测）如果涉及菜单集成 |

*注意：由于未提供 `Build.cs` 文件内容，此列表为基于代码功能的推断。实际使用时，请以项目 `Build.cs` 中声明的依赖为准。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF，可能是为了支持更灵活的日志过滤。 |
| 2025-11-25 | `c0ee383c` | Fix new changelist created in editor not running data validation before invoking submit tool | 修复了在编辑器中创建新变更列表时，未在调用提交工具前运行数据验证的问题。 |
| 2025-11-11 | `64968397` | Add validation message parsing to SubmitToolEditor. | 为 SubmitToolEditor 添加了验证消息解析功能，用于驱动动态标签和参数。 |
| 2025-11-03 | `a757ea03` | Modify ISourceControlModule submit validation delegates. | 修改了源代码控制模块的提交验证委托，可能是为了适配新的覆盖机制。 |
| 2025-07-10 | `9803c443` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applie | 向具有对应 .gen.cpp 文件的源文件添加了 UE_INLINE_GENERATED_CPP_BY_NAME 宏。 |

### 维护评价

该插件创建于 **2025年初**，是一个相对较新的功能。从提交历史看，**直到2026年4月仍有维护性更新**，表明它处于**活跃维护**状态。插件标记为 `IsExperimentalVersion` 且 `EnabledByDefault=false`，说明 Epic 认为其仍处于实验阶段，不建议在核心生产流程中强制使用，但可供有能力的团队尝试和集成。

**结论**：这是一个**积极维护中**的实验性插件。适合有自定义提交流程集成需求的团队探索使用，但应注意其“实验性”标签可能意味着API或行为在未来版本中可能发生变化。由于功能相对聚焦（覆盖提交行为），没有已知的重大限制。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SubmitToolEditor)
- 官方文档：无
- 测试用例：在提供的插件目录中未发现明显的测试文件。