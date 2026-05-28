# Python Editor Script Plugin

> Python integration for the Unreal Editor.

| 属性 | 值 |
|---|---|
| 中文名 | Python 编辑器脚本插件 |
| 分类 | Scripting |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（示例脚本、启动脚本） |
| 模块 | `PythonScriptPluginPreload` (Runtime), `PythonScriptPlugin` (UncookedOnly) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2017-12-08 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PythonScriptPlugin) | |

## 用途

该插件将 CPython 解释器集成到虚幻编辑器中，使开发者和技术美术能够使用 Python 脚本语言来自动化编辑器任务、批量处理资产、扩展编辑器功能以及创建自定义工作流。它解决了通过编写 C++ 代码来扩展编辑器过于复杂、迭代周期长的问题，允许用户利用 Python 生态系统的强大功能和便捷性。

## 使用场景

- 你需要批量重命名、移动、处理数百个资产 → 用 Python 脚本自动化。
- 你希望为技术美术创建自定义的资产处理或关卡编辑工具 → 用 Python 编写编辑器工具。
- 你需要为导入/导出流程集成自定义逻辑 → 用 Python 脚本作为中间层。
- 你希望快速原型验证编辑器 API 的功能 → 用 Python 交互式执行。

## 蓝图用法

此插件的核心是 Python 脚本环境，大部分功能通过 Python 代码调用。但部分底层和管理功能通过蓝图暴露。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Execute Python Command` | 在 Python 解释器中执行一个命令字符串。 | `UPythonScriptLibrary` |
| `Execute Python Script` | 从文件路径或字符串执行一个完整的 Python 脚本。 | `UPythonScriptLibrary` |

### 使用示例（蓝图描述）

1.  **执行简单命令**：在蓝图中拖拽 `Execute Python Command` 节点。将 `Command` 输入连接到一个字符串变量，例如 `"print('Hello from Unreal!')"`。执行后，输出日志会显示 Python 的打印结果。
2.  **运行资产处理脚本**：使用 `Execute Python Script` 节点，将 `File` 输入连接到你编写好的 `.py` 脚本路径。这可以用于批量修改资产属性或生成报告。

## C++ 用法

在 C++ 模块中，你可以直接与 Python 插件交互，调用 Python 代码或扩展 Python 能力。

### 头文件引入

```cpp
#include "PythonScriptPlugin.h"
```

### 基本用法

以下代码演示了如何在 C++ 中调用 Python 执行简单代码并获取结果。
(来源：推断自插件核心接口和 `FPythonScriptPlugin` 类)

```cpp
// 获取 Python 插件实例
FPythonScriptPlugin* PythonPlugin = FPythonScriptPlugin::Get();
if (PythonPlugin && PythonPlugin->IsPythonAvailable())
{
    // 执行一段 Python 代码
    FString Command = TEXT("import unreal; print(f'Current Level: {unreal.EditorLevelLibrary.get_editor_world().get_name()}')");
    PythonPlugin->ExecutePythonCommand(*Command);
}
```

### 进阶用法

你可以将 UE 的对象或数据暴露给 Python，或者从 Python 调用自定义的 C++ 函数。
(思路源自插件将引擎 API 暴露给 Python 的机制)

```cpp
// 假设你有一个需要暴露给 Python 的自定义类
// 通常通过在 .Build.cs 中添加模块依赖，并使用 UNREAL_PYTHON_DEFINE_CLASS 宏（或类似机制）来注册。
// 更常见的是通过 Python 插件提供的元数据反射机制，你的 UObject 类和函数会自动对 Python 可见（需注意访问权限）。

// 在 C++ 中调用 Python 定义的函数（需要插件支持）
// 这通常涉及保存 Python 函数引用并回调，插件内部有相关机制。
```

## Demo 示例

一个最小化的 C++ 示例，展示如何在你的编辑器工具模块中初始化并调用 Python。
(此示例依赖 `PythonScriptPlugin` 模块)

```cpp
// MyEditorTool.h
#pragma once

#include "CoreMinimal.h"

class FMyEditorTool
{
public:
    static void RunSimplePythonCommand();
    static void RunPythonScriptFromFile(const FString& ScriptPath);
};
```

```cpp
// MyEditorTool.cpp
#include "MyEditorTool.h"
#include "PythonScriptPlugin.h" // 引入 Python 插件头文件

void FMyEditorTool::RunSimplePythonCommand()
{
    FPythonScriptPlugin* PythonPlugin = FPythonScriptPlugin::Get();
    if (PythonPlugin && PythonPlugin->IsPythonAvailable())
    {
        // 在编辑器的 Python 环境中执行命令
        FString PythonCode = TEXT("print('Hello from MyEditorTool!')");
        PythonPlugin->ExecutePythonCommand(*PythonCode);
        UE_LOG(LogTemp, Log, TEXT("Python command executed."));
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Python Script Plugin is not available."));
    }
}

void FMyEditorTool::RunPythonScriptFromFile(const FString& ScriptPath)
{
    FPythonScriptPlugin* PythonPlugin = FPythonScriptPlugin::Get();
    if (PythonPlugin && PythonPlugin->IsPythonAvailable())
    {
        // 执行一个 .py 脚本文件
        if (FPaths::FileExists(ScriptPath))
        {
            PythonPlugin->ExecutePythonScript(*ScriptPath);
            UE_LOG(LogTemp, Log, TEXT("Python script '%s' executed."), *ScriptPath);
        }
        else
        {
            UE_LOG(LogTemp, Error, TEXT("Python script file not found: %s"), *ScriptPath);
        }
    }
}
```

## 模块依赖

你的项目需要链接特定模块才能使用 Python 功能。

| 模块 | 用途 |
|---|---|
| `Python3` | 提供基础的 Python 解释器和库支持（必须依赖）。 |
| `PythonScriptPlugin` | 提供与 Unreal Editor 集成的 Python 脚本功能和 API。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `2d500e32` | Python-defined function return value fixes | 修复 Python 定义函数的返回值问题。 |
| 2026-04-14 | `a65e136c` | [UEFN] Add allow list for Python startup scripts UEFN | 为 UEFN 添加 Python 启动脚本的白名单功能。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移到新的 UE_LOGF 格式。 |
| 2026-04-13 | `895825ca` | [Backout] - CL52634718 | 回滚了编号为 52634718 的提交。 |
| 2026-04-13 | `d6c3836d` | [UEFN] Add allow list for Python startup scripts. | 为 UEFN 添加 Python 启动脚本白名单。 |

### 维护评价

- **创建时间**：8 年以上，属于成熟的“老古董”级别插件。
- **近期更新**：截至 2026 年 4 月仍有持续的功能更新和 bug 修复，特别是针对 UEFN（Unreal Editor for Fortnite）的适配，表明其仍在**活跃维护**。
- **实验性状态**：插件标记为 `IsBetaVersion = true` 且 `EnabledByDefault = false`，意味着它是一个**实验性功能**，API 和行为在未来版本中可能发生重大变化。
- **推荐使用**：**推荐**在编辑器工具开发和自动化流程中使用。它功能强大且维护活跃，但务必注意其实验性身份，避免在需要长期稳定性的运行时核心逻辑中使用。建议随时关注更新日志以应对可能的 API 变更。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PythonScriptPlugin)
- [官方文档](https://docs.unrealengine.com/en-US/Engine/Editor/ScriptingAndAutomation/Python/index.html)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PythonScriptPlugin/Content/Scripts) （插件内嵌的示例脚本）
- [论坛支持](https://forums.unrealengine.com/)