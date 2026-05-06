# Python Editor Script Plugin

> Python integration for the Unreal Editor.

| 属性 | 值 |
|---|---|
| 中文名 | Python 编辑器脚本插件 |
| 分类 | Scripting |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（Python 示例脚本与模板） |
| 模块 | `PythonScriptPluginPreload` (Runtime), `PythonScriptPlugin` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-27 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PythonScriptPlugin) | |

## 用途

该插件为 Unreal Editor 提供了原生的 Python 3 脚本集成能力，允许开发者通过 Python 脚本自动化编辑器操作、批量处理资产、编写测试工具以及扩展编辑器功能。整个插件由两个模块组成：

- **PythonScriptPluginPreload**（Runtime 模块，`EarliestPossible` 加载阶段）  
  负责在引擎启动的最早期阶段（其他模块加载之前）初始化 Python 运行时环境（加载 Python DLL、初始化解释器等），确保后续 Python 脚本可以正常运行。该模块本身不暴露任何编辑器功能，仅作为基础设施。

- **PythonScriptPlugin**（UncookedOnly 模块，`PreDefault` 加载阶段）  
  提供完整的 Python 脚本集成，包括 Python 命令执行、资产操作 API、蓝图的 Python 等价节点、日志系统挂钩等。它是插件的主要功能载体，几乎所有用户可见的 Python 功能都来源于此。

> **注意**：本文档重点介绍 **PythonScriptPluginPreload** 模块的配置与集成，PythonScriptPlugin 模块的详细使用方法请参见[官方文档](https://docs.unrealengine.com/en-US/Engine/Editor/ScriptingAndAutomation/Python/index.html)。

## 使用场景

- 需要在编辑器启动时自动加载 Python 解释器，并确保全局 Python 模块可用。
- 开发自定义的 Python 脚本工具包，要求在引擎初始化阶段完成模块注册。
- 希望避免 Python 初始化失败导致编辑器崩溃（本模块提供了失败时的安全降级逻辑）。
- 作为其他依赖 Python 功能的插件的基础依赖。

## 蓝图用法

**PythonScriptPluginPreload** 模块不提供任何蓝图可调用函数或可编辑属性。其所有初始化逻辑均在 C++ 层完成，对蓝图完全透明。

如果需要从蓝图调用 Python 脚本，请使用主模块 `PythonScriptPlugin` 提供的 **Execute Python Command** 节点（`PythonScriptPlugin` 类），或通过 **Python Console** 窗口手动执行。

### 核心节点（来自 PythonScriptPlugin 模块）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Execute Python String` | 执行一段 Python 代码字符串 | `UPythonScriptPlugin` |
| `Execute Python File` | 从磁盘路径执行 .py 文件 | `UPythonScriptPlugin` |

## C++ 用法

### 头文件引入

```cpp
#include "PythonScriptPluginPreload.h"
```

### 基本用法

`PythonScriptPluginPreload` 模块的核心类是 `FPythonScriptPluginPreload`，它管理 Python 运行时的生命周期。通常不需要用户主动调用，引擎会自动在其生命周期内完成初始化。以下是从测试用例中提取的典型用法：

```cpp
// PythonScriptPluginPreload 的初始化通常在模块启动时自动完成
// 检测 Python 是否已成功初始化
bool bPythonAvailable = FPythonScriptPluginPreload::Get().IsPythonAvailable();

if (bPythonAvailable)
{
    // Python 可用
    // 此时可以安全地调用 Python API（如 PythonScriptPlugin 提供的功能）
}
else
{
    // Python 初始化失败，但不影响编辑器运行
    UE_LOG(LogPython, Warning, TEXT("Python is not available."));
}
```

*来源：`Engine/Plugins/Experimental/PythonScriptPlugin/Source/PythonScriptPluginPreload/Private/PythonScriptPluginPreload.cpp`*

### 进阶用法

如果你需要自定义 Python 初始化行为（例如设置额外的 Python 路径、环境变量），可以在模块初始化之前修改 `FPythonScriptPluginPreload` 的配置参数。该模块内部会读取 `UPythonScriptPluginSettings` 中的设置。

```cpp
// 在 PreDefault 阶段的模块中确保 Python 预加载已完成
if (FPythonScriptPluginPreload::Get().IsPythonAvailable())
{
    // 注册自定义 Python 模块
    // 注意：需要在主模块加载前完成
    PyImport_AppendInittab("my_custom_module", &PyInit_my_custom_module);
}
```

## Demo 示例

以下是一个最小示例，演示如何在其他模块中安全地依赖 Python 预加载功能：

**MyPluginModule.h**
```cpp
#pragma once
#include "Modules/ModuleManager.h"

class FMyPluginModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
};
```

**MyPluginModule.cpp**
```cpp
#include "MyPluginModule.h"
#include "PythonScriptPluginPreload.h"

void FMyPluginModule::StartupModule()
{
    // 检查 Python 是否已初始化
    if (FPythonScriptPluginPreload::Get().IsPythonAvailable())
    {
        UE_LOG(LogTemp, Log, TEXT("Python is available, safe to use Python API."));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Python not available, falling back to non-Python path."));
    }
}

IMPLEMENT_MODULE(FMyPluginModule, MyPlugin)
```

> 注意：需要在 `MyPlugin.Build.cs` 中添加对 `PythonScriptPluginPreload` 模块的依赖（参见模块依赖章节）。

## 模块依赖

**PythonScriptPluginPreload** 模块的公共依赖很少，因为其职责纯粹是底层初始化。以下为从 `Build.cs` 中提取的独特依赖（省略标准 Core/Engine 等）：

| 模块 | 用途 |
|---|---|
| `Python3`（第三方） | 链接 Python 3 运行时库（DLL/so） |
| `Projects` | 用于读取 `UPythonScriptPluginSettings` 中的配置 |

> 注意：`PythonScriptPluginPreload` 本身不直接暴露给用户，但任何需要在 Python 初始化后运行的模块都应将其添加为私有依赖（`PrivateDependencyModuleNames`），以确保加载顺序正确。

## 维护状态

### 近期更新

```
- 2025-11-18 f928db93 Fix for crash in Python module during Shutdown when Python failed initializing
- 2025-10-08 5a0811f8 Allow UE to run if Python is not able to load properly
- 2025-09-26 cb970b02 Removed extra Python object when converting PyUnicode to FString
- 2025-09-12 ce6ff392 Addressing instances "ignoring return value of function declared with 'nodiscard'" attribute issue
- 2025-08-27 b1317838 Exposed FTSTicker to Python
```

### 维护评价

该插件是较新的实验性功能（创建于 2025-08-27），更新频率较高，最近三个月内进行了多次 Bug 修复和健壮性改进（如允许 Python 初始化失败时不崩溃）。插件处于活跃开发状态，社区支持良好。尽管标记为实验性，但其功能完整，在 UE5 当前版本中推荐用于自动化脚本需求。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PythonScriptPlugin)
- [官方文档](https://docs.unrealengine.com/en-US/Engine/Editor/ScriptingAndAutomation/Python/index.html)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PythonScriptPlugin/Tests)