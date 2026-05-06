# Submit Tool Editor Override

> Sets up Submit Tool to be launched by the editor

| 属性 | 值 |
|---|---|
| 中文名 | 提交工具编辑器集成 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SubmitToolEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-05-28 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/SubmitToolEditor) | |

## 用途

该插件用于在虚幻编辑器的版本控制提交流程中，将默认的提交对话框替换为外部可执行程序（Submit Tool）。它通过注册提交覆写委托，拦截“检查提交”（PromptForCheckin）和“可以提交”（CanSubmit）操作，并调用指定的外部工具完成提交。此机制允许团队统一使用内部开发的提交工具，并可以强制启用数据验证、路径约束等功能，从而规范提交流程。

## 使用场景

- **团队自定义提交流**：公司强制要求使用内部开发的 SubmitTool 客户端（如带有代码审查、测试检查等功能的独立程序），插件可以将其无缝集成到编辑器的版本控制操作中。
- **强制数据验证**：通过设置 `bEnforceDataValidation`，在提交前强制运行数据验证逻辑，只有通过验证的变更才能提交。
- **软/硬激活切换**：通过 `bForceSubmitTool` 控制是否强制使用 Submit Tool（默认强制），或允许用户降级为编辑器内置提交对话框（软激活），适用于逐步推广的场景。

## 蓝图用法

该插件不公开任何蓝图可调用函数或属性。所有配置和逻辑均通过 C++ 代码和编辑器设置完成。蓝图开发者无需直接使用此插件。

## C++ 用法

### 头文件引入

```cpp
#include "SubmitToolEditor.h"
#include "SubmitToolEditorSettings.h"
```

### 基本用法

以下示例展示如何在自定义模块中获取插件实例、读取并修改设置：

```cpp
// 获取 Submit Tool 编辑器模块实例（确保插件已启用）
FSubmitToolEditorModule& SubmitModule = FModuleManager::LoadModuleChecked<FSubmitToolEditorModule>("SubmitToolEditor");

// 修改默认设置（通常通过编辑器设置 UI 完成，此处展示代码方式）
if (USubmitToolEditorSettings* Settings = GetMutableDefault<USubmitToolEditorSettings>())
{
    Settings->SubmitToolPath = TEXT("C:/Tools/SubmitTool.exe");
    Settings->SubmitToolArguments = TEXT("--auto-submit");
    Settings->bSubmitToolEnabled = true;
    Settings->bForceSubmitTool = true;
    Settings->bEnforceDataValidation = true;
    Settings->SaveConfig();
}
```

### 进阶用法：注册/注销覆写委托

插件的核心功能在模块启动时自动注册覆写委托，但也可在运行时手动重新注册：

```cpp
// 重新注册（例如更改设置后）
if (USubmitToolEditorSettings* Settings = GetMutableDefault<USubmitToolEditorSettings>())
{
    FSubmitToolEditorModule::Get().RegisterSubmitOverrideDelegate(Settings);
}

// 注销覆写委托（恢复为编辑器默认提交对话框）
FSubmitToolEditorModule::Get().UnregisterSubmitOverrideDelegate();
```

## Demo 示例

以下是一个完整的代码示例，展示如何在新插件中使用 SubmitToolEditor 功能。该示例假定你的模块已经添加了对 `SubmitToolEditor` 和 `SourceControl` 的依赖。

### Header：MySubmitHelper.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FMySubmitHelperModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

### Source：MySubmitHelper.cpp

```cpp
#include "MySubmitHelper.h"
#include "SubmitToolEditorSettings.h"
#include "SubmitToolEditor.h"

IMPLEMENT_MODULE(FMySubmitHelperModule, MySubmitHelper)

void FMySubmitHelperModule::StartupModule()
{
    // 确保 SubmitToolEditor 模块已加载
    if (!FModuleManager::Get().IsModuleLoaded("SubmitToolEditor"))
    {
        FModuleManager::Get().LoadModule("SubmitToolEditor");
    }

    // 配置并启用提交工具（示例：从配置读取）
    USubmitToolEditorSettings* Settings = GetMutableDefault<USubmitToolEditorSettings>();
    if (Settings)
    {
        Settings->SubmitToolPath = TEXT("C:/MyTeam/SubmitTool/SubmitTool.exe");
        Settings->bSubmitToolEnabled = true;
        Settings->bForceSubmitTool = true;
        Settings->bEnforceDataValidation = false; // 根据团队需要
        Settings->SaveConfig();
    }

    // 注册覆写委托（插件启动时已自动注册，此处仅演示手动调用）
    FSubmitToolEditorModule::Get().RegisterSubmitOverrideDelegate(Settings);
}

void FMySubmitHelperModule::ShutdownModule()
{
    // 可选：注销覆写委托
    if (FModuleManager::Get().IsModuleLoaded("SubmitToolEditor"))
    {
        FSubmitToolEditorModule::Get().UnregisterSubmitOverrideDelegate();
    }
}
```

## 模块依赖

若要使用 SubmitToolEditor 插件，你的模块需要在 `Build.cs` 的 `PublicDependencyModuleNames` 中添加以下独特依赖：

| 模块 | 用途 |
|---|---|
| `SubmitToolEditor` | 核心模块，提供覆写注册和外部工具调用逻辑 |
| `SourceControl` | 提供版本控制提供者（如 Perforce）接口，供内部使用 |
| `DeveloperSettings` | 提供 `USubmitToolEditorSettings` 的设置系统支持 |

## 维护状态

### 近期更新

- 2025-07-10 9803c44 Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files.
- 2025-06-26 e84e10b [Revision Control] Allow submit override to manage whether submit option is available
- 2025-06-19 b8820c2 SourceControl: Add data validation for check-ins that go via FSourceControlWindows::PromptForCheckin
- 2025-05-29 1a83269 Move the StringOutputDevice into a separate header.
- 2025-05-28 353ef63 Added option for forcing submit tool enabled by default, setting this to false allows for a soft activation.

### 维护评价

这是一个全新的插件（2025年5月创建），至今仍在活跃开发中。最近的更新涉及代码重构（内联生成宏、头文件分离）和功能增强（提交选项控制、数据验证）。由于是实验性插件，API 可能会变化，但核心功能（外部提交工具集成）已经稳定。推荐在需要自定义提交流程的团队中使用，但注意启用插件需手动激活（`EnabledByDefault=false`）。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/SubmitToolEditor)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Source/Developer/SourceControl/Tests)（此插件无独立测试用例，相关测试位于 SourceControl 模块）