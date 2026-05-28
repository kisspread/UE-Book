# Python Editor Script Plugin

> Python integration for the Unreal Editor.

| 属性 | 值 |
|---|---|
| 中文名 | Python编辑器脚本 |
| 分类 | Scripting |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（Python脚本资产、示例） |
| 模块 | `PythonScriptPluginPreload` (Runtime), `PythonScriptPlugin` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2017-12-08 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PythonScriptPlugin) | |

## 用途

该插件为 Unreal Editor 提供了完整的 **Python 脚本支持**。它允许开发者和技术美术使用 Python 语言来编写编辑器扩展、自动化批处理任务、操作资产、生成内容以及与蓝图系统交互。其核心价值在于利用 Python 语言的简洁、丰富的库生态和跨平台能力，大幅扩展编辑器的脚本化与自动化能力，解决原本需要使用 C++ 或复杂蓝图才能完成的编辑器工作流问题。

## 使用场景

*   **资产批处理与维护**：批量重命名、修改、迁移或清理大量资产。
*   **场景操作与生成**：程序化生成场景元素、调整Actor属性、执行大规模场景替换。
*   **编辑器扩展与工具开发**：快速创建自定义编辑器窗口、菜单项、工具栏按钮等，用于团队内部工具。
*   **自动化测试与CI/CD**：编写脚本自动化执行编辑器操作，用于回归测试或在持续集成流程中构建和验证项目。
*   **数据导入/导出**：与外部数据格式（如 JSON, CSV, Excel）进行交互，实现数据驱动的游戏内容。

## 模块列表

*   **`PythonScriptPluginPreload` (Runtime)**: 在引擎最早期加载的预加载模块。负责在编辑器启动时进行必要的早期Python环境初始化或钩子设置。
*   **`PythonScriptPlugin` (UncookedOnly)**: 核心模块。实现了与Python的绑定、脚本执行引擎、UE类型到Python的映射、编辑器API暴露等所有主要功能。仅在编辑器和未烘焙的开发版本中可用。

## 蓝图用法

此插件主要通过Python脚本调用，但其部分功能也暴露给蓝图，用于在蓝图图表中触发Python脚本。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Execute Python Command` | 执行一行Python命令字符串。 | `UPythonScriptLibrary` |
| `Execute Python Script` | 执行指定文件路径下的Python脚本。 | `UPythonScriptLibrary` |
| `Get Python Variable` | 从Python全局作用域获取一个变量，并将其值作为FProperty返回。 | `UPythonScriptLibrary` |
| `Set Python Variable` | 向Python全局作用域设置一个变量。 | `UPythonScriptLibrary` |

### 使用示例（蓝图描述）

在蓝图函数图表中，从一个按钮点击事件连接到 `Execute Python Command` 节点。在该节点的 `Command` 输入引脚中，输入Python代码字符串，例如 `"import unreal; unreal.EditorAssetLibrary.find_asset_data('/Game/MyAsset').get_asset()"`。执行时，该命令将调用Python解释器执行，并可在编辑器输出日志中查看结果。

## C++ 用法

### 头文件引入

```cpp
#include "PythonScriptPlugin.h"
#include "PythonScriptPluginSettings.h"
```

### 基本用法

```cpp
// 来源于 Engine/Tests/PythonScriptPlugin/PythonScriptPluginTests.cpp
// 获取Python脚本插件实例
if (FPythonScriptPlugin* PythonPlugin = FPythonScriptModule::Get())
{
    // 执行一段简单的Python代码
    PythonPlugin->Exec(nullptr, TEXT("print('Hello from UE5 C++')"), *GLog);
}
```

### 进阶用法

```cpp
// 来源于 Engine/Tests/PythonScriptPlugin/PythonScriptPluginTests.cpp
// 通过插件设置来配置启动脚本
UPythonScriptPluginSettings* Settings = GetMutableDefault<UPythonScriptPluginSettings>();
Settings->StartupScripts.Add(TEXT("/Game/Python/init_script.py"));
// 重新加载插件以应用设置
FPythonScriptModule::Get()->RestartPlugin();
```

## Demo 示例

以下是一个最小的编辑器工具示例，它创建一个菜单项，点击后会执行一个简单的Python脚本。

```cpp
// MyPythonTool.h
#pragma once
#include "CoreMinimal.h"

class FMyPythonTool
{
public:
    /** 模块启动时调用，注册菜单项 */
    static void StartupModule();
    /** 模块关闭时调用，注销菜单项 */
    static void ShutdownModule();
    /** 菜单项回调，执行Python脚本 */
    static void ExecutePythonAction();
};
```

```cpp
// MyPythonTool.cpp
#include "MyPythonTool.h"
#include "PythonScriptPlugin.h"
#include "Framework/Commands/UIAction.h"
#include "Framework/MultiBox/MultiBoxBuilder.h"
#include "ToolMenus.h"

#define LOCTEXT_NAMESPACE "FMyPythonToolModule"

void FMyPythonTool::StartupModule()
{
    UToolMenus::RegisterStartupCallback(FSimpleMulticastDelegate::FDelegate::CreateRaw(
        &FMyPythonTool::RegisterMenus));
}

void FMyPythonTool::ShutdownModule()
{
    UToolMenus::UnRegisterStartupCallback(this);
}

void FMyPythonTool::RegisterMenus()
{
    // 向“窗口”菜单添加一个新条目
    FToolMenuOwnerScoped OwnerScoped(this);
    UToolMenu* Menu = UToolMenus::Get()->ExtendMenu("LevelEditor.MainMenu.Window");
    FToolMenuSection& Section = Menu->AddSection("PythonToolsSection", LOCTEXT("PythonTools", "Python Tools"));
    Section.AddMenuEntry(
        "ExecuteMyPythonScript",
        LOCTEXT("ExecuteMyPythonScript_Label", "Execute My Python Script"),
        LOCTEXT("ExecuteMyPythonScript_ToolTip", "Runs a predefined Python script"),
        FSlateIcon(),
        FUIAction(FExecuteAction::CreateStatic(&FMyPythonTool::ExecutePythonAction))
    );
}

void FMyPythonTool::ExecutePythonAction()
{
    if (FPythonScriptPlugin* PythonPlugin = FPythonScriptModule::Get())
    {
        const FString Script = TEXT("import unreal; unreal.log('Hello from the custom menu item!')");
        PythonPlugin->Exec(nullptr, *Script, *GLog);
    }
}

#undef LOCTEXT_NAMESPACE
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Python3` | 提供Python语言运行时核心库 |
| `EditorScriptingUtilities` | 提供大量编辑器操作的蓝图/C++辅助函数 |
| `ContentBrowserFileDataSource` | 支持在内容浏览器中直接操作文件系统资产 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `2d500e32` | Python-defined function return value fixes | 修复了Python自定义函数返回值的处理问题 |
| 2026-04-14 | `a65e136c` | [UEFN] Add allow list for Python startup scripts UEFN | 为UEFN项目添加Python启动脚本的白名单功能 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从UE_LOG迁移至UE_LOGF |
| 2026-04-13 | `895825ca` | [Backout] - CL52634718 | 回滚了一次提交 |
| 2026-04-13 | `d6c3836d` | [UEFN] Add allow list for Python startup scripts. | 为UEFN项目添加Python启动脚本的白名单功能（初版） |

### 维护评价

该插件创建于 **2017 年**，历史较长。然而，从最近的提交记录看（截至 2026 年 4 月），它**仍在被积极维护和更新**，最近的改动涉及功能增强（如UEFN集成、函数返回值修复）和代码现代化。作为 Epic 官方提供的编辑器脚本核心工具，其重要性不言而喻，且已被集成到 **LiveLinkHub** 等专业工作流中。虽然 `.uplugin` 标记为 `IsBetaVersion=true` 且默认未启用，但这更多表明其API可能尚未完全稳定。对于需要编辑器自动化的项目，这是**强烈推荐使用**的插件，但需注意它目前仅在编辑器和未打包版本中可用 (`UncookedOnly`)。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PythonScriptPlugin)
- [官方文档](https://docs.unrealengine.com/en-US/Engine/Editor/ScriptingAndAutomation/Python/index.html)
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Tests/PythonScriptPlugin/)