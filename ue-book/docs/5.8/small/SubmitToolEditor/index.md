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

SubmitToolEditor 允许你将 UE5 编辑器中默认的源代码管理（Source Control）提交行为替换为调用外部提交工具（如自定义的 CLI 提交脚本、公司内部的代码审查提交工具等）。

**核心机制**：该插件通过注册源代码管理模块的提交覆盖委托（Submit Override Delegate），在用户触发提交时拦截流程，转而启动一个外部进程来处理提交。它还支持对 Perforce（P4）的参数透传（端口、用户、客户端、工作区路径），并能在提交前执行数据验证（Data Validation），根据验证结果决定是否允许提交或向外部工具传递额外参数。

**为什么存在**：在大型工作室和企业级项目中，通常有自己的提交工具或代码审查流程（如集成 Gerrit、自定义 Pre-commit 检查等），需要在提交代码时执行额外的验证、格式化或路由操作。此插件提供了一个标准化的桥接层，让团队无需修改引擎源码即可将自定义提交工具集成到 UE5 编辑器中。

## 使用场景

- 你的团队使用自定义的代码提交/审查工具（如内部 CLI 工具），需要在 UE5 编辑器的"提交"操作时自动调用它
- 你需要在提交前执行额外的数据验证（Data Validation），并根据验证结果自动向提交工具传递参数或打标签
- 你使用 Perforce 并需要将 changelist 描述、文件列表等信息透传给外部提交工具
- 你需要强制所有提交操作都通过外部工具完成，绕过编辑器默认的源码管理提交对话框

## 蓝图用法

该插件不暴露蓝图可调用函数。所有功能通过编辑器设置面板和 C++ 模块内部委托机制实现。

### 设置面板

在 **编辑 → 编辑器偏好设置（Editor Preferences）→ Submit Tool Settings** 中配置：

| 设置项 | 说明 |
|---|---|
| `SubmitToolPath` | 外部提交工具的可执行文件路径 |
| `SubmitToolArguments` | 传递给外部工具的命令行参数 |
| `bSubmitToolEnabled` | 是否启用外部提交工具 |
| `bForceSubmitTool` | 是否强制使用外部工具（跳过编辑器默认提交对话框），默认 `true` |
| `bEnforceDataValidation` | 是否在提交前执行数据验证 |
| `ChangelistTagTriggers` | 根据验证消息的正则匹配结果，自动在 changelist 描述中添加标签 |
| `OptionalArgumentTriggers` | 根据验证消息的正则匹配结果，自动向提交工具追加命令行参数 |

## C++ 用法

### 头文件引入

```cpp
#include "SubmitToolEditor.h"
```

### 基本用法

获取模块实例并注册/注销提交覆盖委托：

```cpp
#include "SubmitToolEditor.h"
#include "SubmitToolEditorSettings.h"

// 获取模块单例
FSubmitToolEditorModule& Module = FSubmitToolEditorModule::Get();

// 获取设置对象
const USubmitToolEditorSettings* Settings = GetDefault<USubmitToolEditorSettings>();

// 注册提交覆盖委托（通常在模块启动时自动完成）
Module.RegisterSubmitOverrideDelegate(Settings);

// 注销提交覆盖委托（通常在模块关闭时自动完成）
Module.UnregisterSubmitOverrideDelegate();
```

*（来源：Source/SubmitToolEditor/Private/SubmitToolEditor.h）*

### 进阶用法

该插件的内部工作流程如下：

1. **提交前检查**：`OnCanSubmitToolOverrideCallback` 判断是否可以覆盖提交（检查外部工具路径是否有效、是否启用了强制覆盖等）
2. **提交执行**：`OnSubmitToolOverrideCallback` 被调用，执行以下步骤：
   - 如果使用 Perforce，获取 Port/User/Client/WorkspacePath 参数
   - 如果启用了数据验证，执行 `GetChangelistValidationResult` 获取验证消息
   - 根据 `ChangelistTagTriggers` 和 `OptionalArgumentTriggers` 更新参数
   - 调用 `InvokeSubmitTool` 启动外部进程
3. **进程管理**：通过 `FProcHandle` 管理外部工具的生命周期，使用 `Tick` 检测进程状态

验证触发器的使用示例——根据正则匹配自动添加参数：

```cpp
// 设置中的 OptionalArgumentTriggers 示例
// RegExMessage: ".*Missing copyright.*"
// SubmitToolArgument: "--skip-copyright-check"
// → 当验证消息包含 "Missing copyright" 时，自动追加 --skip-copyright-check 参数
```

## Demo 示例

以下展示如何在自定义编辑器模块中利用 SubmitToolEditor 的设置对象：

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
#include "SubmitToolEditor.h"
#include "SubmitToolEditorSettings.h"

void FMyEditorModule::StartupModule()
{
    // 检查 SubmitToolEditor 模块是否加载
    if (FModuleManager::Get().IsModuleLoaded("SubmitToolEditor"))
    {
        FSubmitToolEditorModule& SubmitModule = FSubmitToolEditorModule::Get();
        const USubmitToolEditorSettings* Settings = GetDefault<USubmitToolEditorSettings>();

        if (Settings && Settings->bSubmitToolEnabled)
        {
            UE_LOG(LogTemp, Log, TEXT("Submit Tool 已启用，路径: %s"), *Settings->SubmitToolPath);
        }
    }
}

void FMyEditorModule::ShutdownModule()
{
}

IMPLEMENT_MODULE(FMyEditorModule, MyEditor)
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

该插件主要依赖 UE5 的源代码管理模块（SourceControl）内置的委托接口，无需额外引入非标准模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏从 UE_LOG 迁移至 UE_LOGF |
| 2025-11-25 | `c0ee383c` | Fix new changelist created in editor not running data validation before invoking submit tool | 修复编辑器新建 changelist 时未执行数据验证就调用提交工具的问题 |
| 2025-11-11 | `64968397` | Add validation message parsing to SubmitToolEditor. | 为提交工具编辑器添加验证消息解析功能 |
| 2025-11-03 | `a757ea03` | Modify ISourceControlModule submit validation delegates. | 修改源码管理模块的提交验证委托接口 |
| 2025-07-10 | `9803c443` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. | 为有对应 .gen.cpp 的源文件添加内联生成宏 |

### 维护评价

该插件于 **2025 年 1 月**创建，最近一次实质性功能更新在 **2025 年 11 月**（数据验证解析和 bug 修复），**2026 年 4 月**有日志宏迁移维护。

- **活跃度**：中等活跃。2025 年 11 月集中进行了功能增强（验证消息解析、Changelist 创建修复），之后主要是基础设施维护
- **状态**：实验性（`IsExperimentalVersion=true`），默认未启用（`EnabledByDefault=false`）
- **代码规模**：小型插件（约 4 个源文件），逻辑集中，维护成本低
- **推荐度**：如果你的团队需要在 UE5 编辑器中集成自定义提交工具，这是一个实用的基础插件。但由于其**实验性**状态且默认未启用，建议在生产环境中谨慎评估，并关注后续 API 变更

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SubmitToolEditor)